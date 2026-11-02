"""One-off: seed data/registry/{sources,claims}.yaml from the v1.0 report and registries.
Kept for transparency; later changes go through submissions, not this script."""
import re, sys, yaml, hashlib, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
REG = ROOT / "data" / "registry"

sys.path.insert(0, str(ROOT))
from pipeline.common import grade_url as grade  # noqa: E402

links = {}
for lang in ("en", "zh"):
    md = (ROOT / "reports" / "v1.0" / f"report_{lang}.md").read_text()
    for text, url in re.findall(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", md):
        links.setdefault(url, set()).add(text.strip())
arch = yaml.safe_load((REG / "archive_snapshots.yaml").read_text())["snapshots"]
arch_by_url = {a["original_url"]: a["id"] for a in arch}
sources = []
for url in sorted(links):
    g, k = grade(url)
    sid = "SRC-" + hashlib.sha1(url.encode()).hexdigest()[:8].upper()
    sources.append({"id": sid, "title": sorted(links[url], key=len)[-1], "url": url, "kind": k, "grade": g,
                    "first_cited_in": "v1.0", **({"archive_record": arch_by_url[url]} if url in arch_by_url else {})})
(REG / "sources.yaml").write_text("# Auto-seeded from v1.0 report links (pipeline/tools/seed_registry_v1.py); grades are a first pass by domain\n"
    "# A=official/primary statistical or archival, B=peer-reviewed or research institution, C=secondary/repost/journalism, D=user-generated or unverified\n"
    + yaml.safe_dump({"schema_version": 1, "sources": sources}, allow_unicode=True, sort_keys=False, width=200))

claims, n = [], 0
def add(**kw):
    global n; n += 1; kw = {"id": f"CLM-{n:04d}", **kw}; kw.setdefault("status", "registered"); kw.setdefault("added_in", "v1.0"); claims.append(kw)
def years(p):
    ys = [int(y) for y in re.findall(r"(19\d\d)", p)]
    return (min(ys), max(ys)) if ys else (None, None)
for e in yaml.safe_load((REG / "estimates.yaml").read_text())["estimates"]:
    s, t = years(e["period"])
    add(measure=e["measure"], value=e["central"], unit="million", **({"low": e["low"]} if "low" in e else {}),
        **({"high": e["high"]} if "high" in e else {}), geography={"level": "national", "name": "China"},
        period={"start": s, "end": t, "label": e["period"]}, source=e["id"], method_class=e["method_class"])
md = (ROOT / "reports" / "v1.0" / "report_en.md").read_text()
rows = re.findall(r"^\|\s*(?:\*\*)?([A-Z][A-Za-z ]+?)(?: \(revised\))?(?:\*\*)?\s*\|\s*([\d.—–-]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*(?:\*\*)?([\d.]+)(?:\*\*)?(?: \(or [\d.]+\))?\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|", md, re.M)
for r in rows:
    prov = r[0].strip()
    for yr, v in zip(range(1958, 1963), r[2:7]):
        add(measure="cdr", value=float(v), unit="per_mille", geography={"level": "province", "name": prov},
            period={"start": yr, "end": yr, "label": str(yr)}, source="SRC-SSB-PROVINCIAL-CDR", method_class="registration")
    cao = r[9].strip().strip("*")
    if re.fullmatch(r"\d+", cao):
        add(measure="excess_deaths", value=int(cao) / 100, unit="million", geography={"level": "province", "name": prov},
            period={"start": 1959, "end": 1961, "label": "1959-61"}, source="EST-CAO-2005", method_class="local_records")
    add(measure="excess_deaths", value=int(r[7]) / 100, unit="million", geography={"level": "province", "name": prov},
        period={"start": 1958, "end": 1962, "label": "1958-62"}, source="EST-OFFICIAL-REG", method_class="registration",
        note="simple excess: (CDR - 1956-57 mean) x population, positive years")
import csv
for h in csv.DictReader(open(ROOT / "data" / "regional" / "hotspots.csv")):
    try: v = float(str(h["figure"]).replace(",", ""))
    except ValueError: continue
    t = h["type_of_figure"].lower()
    meas = ("cdr" if "‰" in t or "cdr" in t else "abnormal_deaths" if "abnormal" in t or "non-normal" in t
            else "starvation_deaths" if "starv" in t else "population_change" if "decline" in t or "population" in t else "total_deaths")
    add(measure=meas, value=v, unit="per_mille" if meas == "cdr" else "person",
        geography={"level": h["level"] or "county", "name": h["locality"], "province": h["province"]},
        period={"start": None, "end": None, "label": h["period"]}, source=h["secondary_source_used"],
        first_source=h["first_or_earliest_known_source"], method_class="archival")
(REG / "claims.yaml").write_text("# Numeric claims registry used by pipeline/reconcile.py. Seeded from v1.0 (pipeline/tools/seed_registry_v1.py).\n"
    + yaml.safe_dump({"schema_version": 1, "claims": claims}, allow_unicode=True, sort_keys=False, width=200))
print(len(sources), "sources;", len(claims), "claims;", len(rows), "province rows")
