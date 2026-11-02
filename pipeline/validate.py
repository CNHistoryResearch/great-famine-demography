"""Gate 0: structural validation of registries and submissions.

Usage:
  python -m pipeline.validate               # everything
  python -m pipeline.validate --changed     # only submissions touched relative to origin/main
Exit code 1 if any error.
"""
from __future__ import annotations

import argparse
import csv
import sys

from pipeline.common import (QUESTIONS, REGISTRY, ROOT, SUBMISSIONS, changed_files, iter_manifests,
                             load_yaml, schema_validator, sha256_file)


def validate_registries() -> list[str]:
    errs: list[str] = []
    claim_v = schema_validator("claim.schema.json")
    q_v = schema_validator("question.schema.json")

    ids: dict[str, str] = {}

    def seen(i: str, where: str):
        if i in ids:
            errs.append(f"duplicate id {i} in {where} (also in {ids[i]})")
        ids[i] = where

    claims = load_yaml(REGISTRY / "claims.yaml")["claims"]
    for c in claims:
        seen(c["id"], "claims.yaml")
        for e in claim_v.iter_errors(c):
            errs.append(f"claims.yaml {c.get('id')}: {e.message}")
        if "low" in c and "high" in c and c["low"] > c["high"]:
            errs.append(f"claims.yaml {c['id']}: low > high")
    for e in load_yaml(REGISTRY / "estimates.yaml")["estimates"]:
        seen(e["id"], "estimates.yaml")
    for s in load_yaml(REGISTRY / "sources.yaml")["sources"]:
        seen(s["id"], "sources.yaml")
        if s.get("grade") not in {"A", "B", "C", "D"}:
            errs.append(f"sources.yaml {s['id']}: grade must be A-D, got {s.get('grade')}")
    for a in load_yaml(REGISTRY / "archive_snapshots.yaml")["snapshots"]:
        seen(a["id"], "archive_snapshots.yaml")
    for q in load_yaml(QUESTIONS)["questions"]:
        seen(q["id"], "questions.yaml")
        for e in q_v.iter_errors(q):
            errs.append(f"questions.yaml {q.get('id')}: {e.message}")
        if q["status"] == "answered" and not q.get("answered_in"):
            errs.append(f"questions.yaml {q['id']}: answered but no answered_in")
        if q["status"] == "duplicate" and not q.get("duplicate_of"):
            errs.append(f"questions.yaml {q['id']}: duplicate but no duplicate_of")
    return errs


def validate_csvs() -> list[str]:
    errs = []
    for p in sorted((ROOT / "data").rglob("*.csv")):
        with open(p, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
        if not rows:
            errs.append(f"{p.relative_to(ROOT)}: empty")
            continue
        header = rows[0]
        if any(not h.strip() for h in header):
            errs.append(f"{p.relative_to(ROOT)}: blank column name")
        for i, r in enumerate(rows[1:], start=2):
            if len(r) != len(header):
                errs.append(f"{p.relative_to(ROOT)}:{i}: {len(r)} fields, header has {len(header)}")
                break
    return errs


def validate_manifest(path, m) -> list[str]:
    errs = []
    v = schema_validator("submission.schema.json")
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    for e in v.iter_errors(m):
        loc = "/".join(str(x) for x in e.absolute_path)
        errs.append(f"{rel}: {loc or '(root)'}: {e.message}")
    if isinstance(m, dict):
        if path.parent.name != m.get("id"):
            errs.append(f"{rel}: folder name must equal id ({m.get('id')})")
        if path.parent.parent.name != m.get("type"):
            errs.append(f"{rel}: must live under submissions/{m.get('type')}/")
        for f in m.get("files") or []:
            fp = path.parent / f["path"]
            if not fp.exists():
                errs.append(f"{rel}: file {f['path']} missing")
            elif sha256_file(fp) != f["sha256"]:
                errs.append(f"{rel}: sha256 mismatch for {f['path']}")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--changed", action="store_true", help="only submissions changed vs origin/main")
    ap.add_argument("--base", default="origin/main")
    a = ap.parse_args(argv)
    errs = validate_registries() + validate_csvs()
    manifests = iter_manifests(changed_files(a.base)) if a.changed else iter_manifests()
    seen_ids: dict[str, str] = {}
    for path, m in iter_manifests():
        sid = (m or {}).get("id")
        if sid in seen_ids:
            errs.append(f"duplicate submission id {sid}: {seen_ids[sid]} and {path.relative_to(ROOT)}")
        seen_ids[sid] = str(path.relative_to(ROOT))
    n = 0
    for path, m in manifests:
        n += 1
        errs += validate_manifest(path, m)
    for d in SUBMISSIONS.glob("*/*"):
        if d.is_dir() and not (d / "manifest.yaml").exists():
            errs.append(f"{d.relative_to(ROOT)}: folder without manifest.yaml")
    for e in errs:
        print(f"ERROR {e}")
    print(f"validate: {n} submission(s) checked, {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
