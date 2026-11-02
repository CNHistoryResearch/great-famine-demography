"""Gates 0-4 for submissions. See docs/quality-gates.md for the rules in plain language.

Usage:
  python -m pipeline.quality_gate --changed --out gate_report.md --json gate_report.json
  python -m pipeline.quality_gate submissions/data/SUB-2026-0001
Exit code: 0 if every checked submission passes gates 0-3 (ready for maintainer review), 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

from pipeline.common import REGISTRY, changed_files, grade_url, iter_manifests, load_yaml
from pipeline.validate import validate_manifest

PII_PATTERNS = {
    "email address": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "phone number": re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)|(?<!\d)\d{3,4}-\d{7,8}(?!\d)"),
    "PRC ID number": re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)"),
}
PLAUSIBLE = {  # measure -> (min, max) in canonical units (millions for counts at national level)
    "cdr": (0, 1000), "cbr": (0, 80), "imr": (0, 1000), "life_expectancy": (5, 90),
}


def text_blobs(m: dict, folder: pathlib.Path) -> list[str]:
    out = [json.dumps(m, ensure_ascii=False)]
    for f in m.get("files") or []:
        p = folder / f["path"]
        if p.suffix.lower() in {".md", ".txt", ".csv", ".yaml", ".yml"} and p.exists():
            out.append(p.read_text(encoding="utf-8", errors="ignore"))
    return out


def gate(path: pathlib.Path, m: dict, known_urls: set, known_hashes: set, known_claims: set) -> dict:
    folder = path.parent
    res = {"id": m.get("id"), "type": m.get("type"), "title": m.get("title"), "gates": {}, "warnings": [], "grade": None}

    # G0 structure
    g0 = validate_manifest(path, m)
    res["gates"]["G0_structure"] = {"pass": not g0, "issues": g0}
    if g0:
        res["status"] = "needs-work"
        return res

    # G1 provenance
    g1 = []
    for i, p in enumerate(m["provenance"]):
        if p.get("url") and not p.get("archive_url"):
            res["warnings"].append(f"provenance[{i}] has no archive_url; the archive step will try to create one")
        if not p.get("url") and not p.get("page_ref") and m["type"] != "testimony":
            g1.append(f"provenance[{i}] is a citation without URL or page reference")
    if m["type"] == "material" and not any(p.get("original_publication") for p in m["provenance"]):
        res["warnings"].append("material: say where/when the item first appeared (original_publication) if known")
    if m.get("files") and m["license"] == "unknown":
        g1.append("files attached but license is 'unknown': we cannot redistribute them; link instead or state the license")
    grades = [grade_url(p["url"])[0] for p in m["provenance"] if p.get("url")]
    order = {"A": 0, "B": 1, "C": 2, "D": 3, "unrated": 4}
    res["grade"] = min(grades, key=lambda g: order[g]) if grades else ("T" if m["type"] == "testimony" else "unrated")
    res["gates"]["G1_provenance"] = {"pass": not g1, "issues": g1}

    # G2 verifiability (type-specific)
    g2 = []
    claims = m.get("claims") or []
    for i, c in enumerate(claims):
        if not (c.get("quote") or c.get("page_ref")):
            g2.append(f"claims[{i}]: give the verbatim quote or page reference that states the number")
        lo, hi = PLAUSIBLE.get(c["measure"], (0, float("inf")))
        if not lo <= c["value"] <= hi:
            g2.append(f"claims[{i}]: value {c['value']} outside plausible range for {c['measure']}")
        if c["measure"].endswith("deaths") and c["geography"]["level"] == "national" and c["unit"] == "million" and c["value"] > 100:
            g2.append(f"claims[{i}]: {c['value']} million national deaths is implausible; check the unit")
    t = m["type"]
    if t == "data" and not claims and not m.get("files"):
        g2.append("data submission needs claims or a data file")
    if t == "research":
        r = m["research"]
        if not r.get("method"):
            g2.append("research: describe the method")
        if not (r.get("code_url") or r.get("data_url") or r.get("doi")):
            g2.append("research: provide code, data, or a DOI so the result can be checked")
    if t == "testimony":
        tt = m["testimony"]
        for blob in text_blobs(m, folder):
            for label, rx in PII_PATTERNS.items():
                if rx.search(blob):
                    g2.append(f"testimony contains what looks like a {label}; remove personal identifiers")
        rel = tt["narrator"]["relation"]
        res["grade"] = "T1" if tt.get("corroborated_by") and rel != "secondhand" else ("T2" if rel != "secondhand" else "T3")
    if t == "correction" and not (m["correction"].get("target") and m["correction"].get("proposed_change")):
        g2.append("correction: name the target and the proposed change")
    res["gates"]["G2_verifiability"] = {"pass": not g2, "issues": sorted(set(g2))}

    # G3 novelty
    new_urls = [p["url"] for p in m["provenance"] if p.get("url") and p["url"] not in known_urls]
    new_files = [f for f in m.get("files") or [] if f["sha256"] not in known_hashes]
    new_claims = [c for c in claims if claim_key(c) not in known_claims]
    novel = bool(new_urls or new_files or new_claims or t in {"testimony", "research", "correction"})
    g3 = [] if novel else ["nothing new: every source, file and claim is already in the registry"]
    res["gates"]["G3_novelty"] = {"pass": not g3, "issues": g3,
                                  "new": {"urls": len(new_urls), "files": len(new_files), "claims": len(new_claims)}}

    # G4 human review is enforced by branch protection / CODEOWNERS
    res["gates"]["G4_review"] = {"pass": None, "issues": ["pending maintainer review (2 approvals if it changes a headline number)"]}
    res["status"] = "ready-for-review" if all(g["pass"] for k, g in res["gates"].items() if k != "G4_review") else "needs-work"
    return res


def claim_key(c: dict) -> tuple:
    g = c["geography"]
    return (c["measure"], g["level"], g["name"].lower(), c["period"].get("label", ""), round(float(c["value"]), 3), c["unit"])


def known_sets(exclude: set[str]):
    urls = {s["url"] for s in load_yaml(REGISTRY / "sources.yaml")["sources"]}
    urls |= {a["original_url"] for a in load_yaml(REGISTRY / "archive_snapshots.yaml")["snapshots"]}
    hashes, claims = set(), {claim_key(c) for c in load_yaml(REGISTRY / "claims.yaml")["claims"]}
    for path, m in iter_manifests():
        if m.get("id") in exclude:
            continue
        urls |= {p.get("url") for p in m.get("provenance") or [] if p.get("url")}
        hashes |= {f["sha256"] for f in m.get("files") or []}
        claims |= {claim_key(c) for c in m.get("claims") or []}
    return urls, hashes, claims


def render(results: list[dict]) -> str:
    icon = {True: "✅", False: "❌", None: "⏳"}
    lines = ["## Quality gate report", ""]
    if not results:
        return "\n".join(lines + ["No submissions changed."])
    for r in results:
        lines += [f"### {r['id']}: {r.get('title')}", f"Type **{r['type']}** · provisional grade **{r['grade']}** · status **{r['status']}**", "",
                  "| Gate | Result | Notes |", "|---|---|---|"]
        for k, g in r["gates"].items():
            lines.append(f"| {k} | {icon[g['pass']]} | {'<br>'.join(g['issues']) or '—'} |")
        if r["warnings"]:
            lines += ["", "Warnings:"] + [f"- {w}" for w in r["warnings"]]
        lines.append("")
    lines.append("Gates are explained in [docs/quality-gates.md](../blob/main/docs/quality-gates.md).")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", type=pathlib.Path)
    ap.add_argument("--changed", action="store_true")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--out")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    if a.changed:
        targets = list(iter_manifests(changed_files(a.base)))
    elif a.paths:
        targets = list(iter_manifests(a.paths))
    else:
        targets = list(iter_manifests())
    ids = {m.get("id") for _, m in targets}
    urls, hashes, claims = known_sets(ids)
    results = [gate(p, m, urls, hashes, claims) for p, m in targets]
    md = render(results)
    if a.out:
        pathlib.Path(a.out).write_text(md, encoding="utf-8")
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(md)
    return 0 if all(r["status"] == "ready-for-review" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
