"""Automated reconciliation ("arbitrage") of numeric claims.

Every claim in data/registry/claims.yaml plus every claim in accepted submissions is normalized
(units, geography names, periods, measure families) and checked against the others:

  consistent      within the registered range for the same measure, place and overlapping period
  definitional    differs, but the measures differ (e.g. total vs excess deaths) in the expected direction
  conflict        same measure, place and period, outside the registered range by more than the tolerance
  new_coverage    nothing comparable registered yet (a new place, period or measure)

Coherence checks across levels:
  - provincial sums vs the same source's national figure, and vs the current model band
  - county/prefecture totals vs the highest provincial estimate for that province
  - plausibility of rates (CDR) by geographic level
  - national excess-death claims outside the current model band, grouped by method class

Outputs: reports/reconciliation/latest.md, reports/reconciliation/latest.json, research/queue.yaml
Usage: python -m pipeline.reconcile [--since v1.0] [--tolerance 0.15]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import defaultdict

from pipeline.common import REGISTRY, REPORTS, ROOT, current_version, dump_yaml, iter_manifests, load_yaml, to_millions, vkey

PROVINCES = {
    "Anhui": "安徽", "Beijing": "北京", "Fujian": "福建", "Gansu": "甘肃", "Guangdong": "广东", "Guangxi": "广西",
    "Guizhou": "贵州", "Hebei": "河北", "Heilongjiang": "黑龙江", "Henan": "河南", "Hubei": "湖北", "Hunan": "湖南",
    "Inner Mongolia": "内蒙古", "Jiangsu": "江苏", "Jiangxi": "江西", "Jilin": "吉林", "Liaoning": "辽宁", "Ningxia": "宁夏",
    "Qinghai": "青海", "Shaanxi": "陕西", "Shandong": "山东", "Shanghai": "上海", "Shanxi": "山西", "Sichuan": "四川",
    "Tianjin": "天津", "Tibet": "西藏", "Xinjiang": "新疆", "Yunnan": "云南", "Zhejiang": "浙江",
}
ZH_TO_EN = {v: k for k, v in PROVINCES.items()}
DEATH_FAMILY = {"excess_deaths", "abnormal_deaths", "starvation_deaths", "total_deaths"}
# expected ordering when measures differ: starvation <= excess ~ abnormal <= total
RANK = {"starvation_deaths": 0, "excess_deaths": 1, "abnormal_deaths": 1, "total_deaths": 2}
CDR_BOUNDS = {"national": (5, 60), "province": (3, 120), "prefecture": (3, 400), "county": (3, 600), "commune": (3, 800)}


NATIONAL_NAMES = {"china", "prc", "mainland china", "national", "全国", "中国", "中国大陆", "全國"}
MODEL_BAND: tuple[float, float] | None = None  # set in main(); national excess deaths are judged against it


def canon_place(g: dict) -> tuple[str, str]:
    name = g["name"].strip()
    if g["level"] == "national" or name.lower() in NATIONAL_NAMES:
        return "national", "china"
    name = ZH_TO_EN.get(name.rstrip("省市自治区"), name)
    return g["level"], name.lower()


def years(c):
    p = c.get("period") or {}
    return p.get("start"), p.get("end")


def overlap(a, b) -> bool:
    (s1, e1), (s2, e2) = years(a), years(b)
    if None in (s1, e1, s2, e2):
        return (a.get("period") or {}).get("label") == (b.get("period") or {}).get("label")
    return s1 <= e2 and s2 <= e1


def value_m(c):
    v = to_millions(c["value"], c["unit"])
    return v if v is not None else c["value"]


def bounds(c):
    lo = c.get("low", c["value"])
    hi = c.get("high", c["value"])
    f = (lambda x: to_millions(x, c["unit"]) if to_millions(x, c["unit"]) is not None else x)
    return f(lo), f(hi)


def load_claims(since: str | None):
    reg = [dict(c, origin="registry") for c in load_yaml(REGISTRY / "claims.yaml")["claims"] if c.get("status", "registered") == "registered"]
    new = []
    for path, m in iter_manifests():
        for i, c in enumerate(m.get("claims") or []):
            c = dict(c, id=c.get("id") or f"{m['id']}#{i + 1}", origin=m["id"], source=c.get("source") or m["id"])
            new.append(c)
    if since:
        reg_new = [c for c in reg if c.get("added_in") and vkey(c["added_in"]) > vkey(since)]
        new += reg_new
    return reg, new


def classify(c, pool, tol):
    same = [r for r in pool if r is not c and r["measure"] == c["measure"] and canon_place(r["geography"]) == canon_place(c["geography"])
            and r["unit"] in (c["unit"], "million", "person") and overlap(r, c)]
    fam = [r for r in pool if r is not c and r["measure"] != c["measure"] and r["measure"] in DEATH_FAMILY and c["measure"] in DEATH_FAMILY
           and canon_place(r["geography"]) == canon_place(c["geography"]) and overlap(r, c)]
    v = value_m(c)
    if c["measure"] == "excess_deaths" and canon_place(c["geography"])[0] == "national" and MODEL_BAND:
        lo, hi = MODEL_BAND
        if lo * (1 - tol) <= v <= hi * (1 + tol):
            return "consistent", f"within the current model band {lo:g}–{hi:g}M", same
        return "conflict", f"{v:g}M outside the current model band {lo:g}–{hi:g}M", same
    if same:
        if len(same) >= 3:
            vals = sorted(value_m(r) for r in same)
            q = lambda f: vals[min(len(vals) - 1, max(0, round(f * (len(vals) - 1))))]
            lo, hi, kind = q(0.25), q(0.75), "interquartile range"
        else:
            lo, hi, kind = min(bounds(r)[0] for r in same), max(bounds(r)[1] for r in same), "range"
        if lo * (1 - tol) <= v <= hi * (1 + tol):
            return "consistent", f"within registered {kind} {lo:g}–{hi:g} ({len(same)} comparable)", same
        return "conflict", f"{v:g} outside registered {kind} {lo:g}–{hi:g} by more than {tol:.0%}", same
    if fam:
        notes = []
        ok = True
        for r in fam:
            rv = value_m(r)
            expect_le = RANK[c["measure"]] <= RANK[r["measure"]]
            if (expect_le and v > rv * (1 + tol)) or (not expect_le and v < rv * (1 - tol)):
                ok = False
            notes.append(f"{r['measure']}={rv:g} ({r.get('source')})")
        return ("definitional" if ok else "conflict"), "different measure: " + "; ".join(notes[:4]), fam
    return "new_coverage", "no comparable registered claim", []


def coherence(pool, band):
    """Return coherence findings. Findings that involve only registry claims are 'known' (already reviewed);
    those touching a new (submitted) claim are 'check'."""
    out = []
    is_new = lambda c: c.get("origin") != "registry"
    # 1. provincial sums by source vs national
    by_src = defaultdict(list)
    for c in pool:
        if c["measure"] == "excess_deaths" and c["geography"]["level"] == "province":
            by_src[(c.get("source"), (c.get("period") or {}).get("label"))].append(c)
    nat = {c.get("source"): c for c in pool if c["measure"] == "excess_deaths" and c["geography"]["level"] == "national"}
    for (src, per), rows in sorted(by_src.items(), key=lambda kv: str(kv[0])):
        if len(rows) < 10:
            continue
        s = sum(value_m(c) for c in rows)
        n = nat.get(src)
        msg = f"{len(rows)} provinces from {src} ({per}) sum to {s:.1f}M"
        if n:
            ratio = s / value_m(n)
            msg += f"; same source's national figure {value_m(n):g}M (ratio {ratio:.2f})"
            status = "ok" if 0.85 <= ratio <= 1.15 else "check"
        else:
            status = "ok"
        if not band[0] <= s <= band[1]:
            msg += f"; outside model band {band[0]:g}–{band[1]:g}M"
            status = "check"
        if status == "check" and not any(is_new(c) for c in rows + ([n] if n else [])):
            status = "known"
        out.append({"check": "provincial_sum", "status": status, "detail": msg})
    # 2. sub-provincial totals vs provincial maxima
    prov_max = defaultdict(float)
    for c in pool:
        if c["measure"] in {"excess_deaths", "abnormal_deaths", "total_deaths"} and c["geography"]["level"] == "province":
            prov_max[canon_place(c["geography"])[1]] = max(prov_max[canon_place(c["geography"])[1]], value_m(c))
    sub = defaultdict(float)
    sub_new = defaultdict(bool)
    for c in pool:
        g = c["geography"]
        if c["measure"] in {"excess_deaths", "abnormal_deaths", "starvation_deaths"} and g["level"] in {"county", "prefecture"} and g.get("province"):
            k = ZH_TO_EN.get(g["province"], g["province"]).lower()
            sub[k] += value_m(c) or 0
            sub_new[k] |= is_new(c)
    for p, s in sorted(sub.items()):
        mx = prov_max.get(p)
        if mx and s > mx * 1.05:
            out.append({"check": "subprovincial_vs_province", "status": "check" if sub_new[p] else "known",
                        "detail": f"{p}: registered county/prefecture deaths sum to {s:.2f}M, above the highest provincial estimate {mx:.2f}M (possible double counting or overlapping localities)"})
    # 3. rate plausibility
    for c in pool:
        if c["measure"] == "cdr":
            lo, hi = CDR_BOUNDS.get(c["geography"]["level"], (0, 1000))
            if not lo <= c["value"] <= hi:
                out.append({"check": "cdr_plausibility", "status": "check" if is_new(c) else "known",
                            "detail": f"{c['id']}: CDR {c['value']}‰ for {c['geography']['name']} ({c['geography']['level']}) outside {lo}–{hi}"})
    # 4. national claims vs band
    for c in pool:
        if c["measure"] == "excess_deaths" and c["geography"]["level"] == "national":
            v = value_m(c)
            if not band[0] <= v <= band[1]:
                out.append({"check": "national_vs_model_band", "status": "known" if c.get("origin") == "registry" else "check",
                            "detail": f"{c.get('source')}: {v:g}M ({c.get('method_class')}) outside model band {band[0]:g}–{band[1]:g}M"})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="treat registry claims added after this version as new")
    ap.add_argument("--tolerance", type=float,
                    default=load_yaml(ROOT / "pipeline" / "config.yaml")["reconciliation"]["tolerance"])
    ap.add_argument("--all", action="store_true", help="classify every claim, not only new ones")
    a = ap.parse_args(argv)
    ours = next(e for e in load_yaml(REGISTRY / "estimates.yaml")["estimates"] if e["id"].startswith("EST-OURS"))
    band = (ours["low"], ours["high"])
    global MODEL_BAND
    MODEL_BAND = band
    reg, new = load_claims(a.since)
    pool = reg + [c for c in new if c not in reg]
    targets = pool if a.all else new
    results = []
    for c in targets:
        status, why, comps = classify(c, [r for r in pool if r.get("origin") == "registry" or r is c] if not a.all else pool, a.tolerance)
        results.append({"claim": c["id"], "origin": c.get("origin"), "measure": c["measure"], "place": c["geography"]["name"],
                        "level": c["geography"]["level"], "period": (c.get("period") or {}).get("label"), "value": c["value"],
                        "unit": c["unit"], "status": status, "why": why, "compared_with": [r["id"] for r in comps][:8]})
    coh = coherence(pool, band)
    counts = defaultdict(int)
    for r in results:
        counts[r["status"]] += 1
    out_dir = REPORTS / "reconciliation"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.date.today().isoformat()
    payload = {"date": stamp, "report_version": current_version(), "model_band_million": band, "tolerance": a.tolerance,
               "counts": dict(counts), "claims": results, "coherence": coh}
    stem = "all_claims" if a.all else "latest"  # --all is diagnostic; never overwrite the published report
    (out_dir / f"{stem}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    md = [f"# Reconciliation report ({stamp})", "",
          f"Against report {current_version()}; model band {band[0]:g}–{band[1]:g} million excess deaths; tolerance ±{a.tolerance:.0%}.", "",
          "| Status | Claims |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(counts.items())] + [""]
    if not targets:
        md.append("No new claims since the last report. Coherence checks still ran on the full registry.\n")
    for st in ("conflict", "new_coverage", "definitional", "consistent"):
        rows = [r for r in results if r["status"] == st]
        if rows:
            md += [f"## {st} ({len(rows)})", "", "| Claim | From | Measure | Place | Period | Value | Why |", "|---|---|---|---|---|---|---|"]
            md += [f"| {r['claim']} | {r['origin']} | {r['measure']} | {r['place']} | {r['period']} | {r['value']} {r['unit']} | {r['why']} |" for r in rows[:200]]
            md.append("")
    md += ["## Coherence checks", "", "| Check | Status | Detail |", "|---|---|---|"]
    md += [f"| {c['check']} | {c['status']} | {c['detail']} |" for c in coh] or ["| — | ok | nothing flagged |"]
    (out_dir / f"{stem}.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    if a.all:
        print("\n".join(md[:12]))
        print("diagnostic run (--all): research queue not modified")
        return 0
    queue_path = ROOT / "research" / "queue.yaml"
    queue = load_yaml(queue_path) if queue_path.exists() else {"schema_version": 1, "items": []}
    have = {(i["kind"], i["ref"]) for i in queue["items"]}
    nxt = len(queue["items"]) + 1
    for r in results:
        if r["status"] in ("conflict", "new_coverage") and ("claim", r["claim"]) not in have:
            queue["items"].append({"id": f"R-{nxt:04d}", "kind": "claim", "ref": r["claim"], "status": "open",
                                   "reason": f"{r['status']}: {r['why']}", "opened": stamp})
            nxt += 1
    for c in coh:
        key = ("coherence", c["detail"][:120])
        if c["status"] == "check" and key not in have:
            queue["items"].append({"id": f"R-{nxt:04d}", "kind": "coherence", "ref": c["detail"][:120], "status": "open",
                                   "reason": c["check"], "opened": stamp})
            nxt += 1
    dump_yaml(queue, queue_path, "# Research queue: items the next research cycle must resolve. Written by pipeline/reconcile.py; maintainers may close items with a note.\n")
    print("\n".join(md[:12]))
    print(f"queue: {sum(1 for i in queue['items'] if i['status'] == 'open')} open item(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
