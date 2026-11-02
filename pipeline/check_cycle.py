"""Gate for an automated research cycle's output (runs in the research-cycle workflow and on report PRs).

  python -m pipeline.check_cycle v1.1

Checks that the new report version is complete and that every packet item was handled:
  - reports/<v>/{report_en.md, report_zh.md, CHANGES.md, meta.yaml} exist and are non-trivial
  - every accepted question in the packet is answered (with a matching section) or deferred with a note
  - every research-queue item in the packet is resolved or still open with an explanation in CHANGES.md
  - every image referenced by the reports exists
  - no email addresses, phone numbers or ID numbers in the reports
  - the English and Chinese reports have the same number of tables and figures (translation completeness)
Exit 1 on any failure.
"""
from __future__ import annotations

import json
import re
import sys

from pipeline.common import QUESTIONS, REPORTS, ROOT, load_yaml
from pipeline.quality_gate import PII_PATTERNS


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: python -m pipeline.check_cycle <version>")
        return 2
    v = argv[0]
    d = REPORTS / v
    errs: list[str] = []
    for f, min_len in (("report_en.md", 3000), ("report_zh.md", 2000), ("CHANGES.md", 200), ("meta.yaml", 50)):
        p = d / f
        if not p.exists():
            errs.append(f"missing reports/{v}/{f}")
        elif len(p.read_text(encoding="utf-8")) < min_len:
            errs.append(f"reports/{v}/{f} looks truncated")
    if errs:
        print("\n".join("ERROR " + e for e in errs))
        return 1
    en = (d / "report_en.md").read_text(encoding="utf-8")
    zh = (d / "report_zh.md").read_text(encoding="utf-8")
    changes = (d / "CHANGES.md").read_text(encoding="utf-8")
    meta = load_yaml(d / "meta.yaml")
    for key in ("version", "published", "headline", "files"):
        if key not in meta:
            errs.append(f"meta.yaml missing '{key}'")

    packet_path = ROOT / "research" / v / "packet.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8")) if packet_path.exists() else {"questions": [], "queue": []}
    qs = {q["id"]: q for q in load_yaml(QUESTIONS)["questions"]}
    for q in packet["questions"]:
        cur = qs.get(q["id"], {})
        if cur.get("status") == "answered":
            if cur.get("answered_in") != v:
                errs.append(f"{q['id']}: answered_in should be {v}")
            if q["id"] not in en:
                errs.append(f"{q['id']}: marked answered but no section mentions it in report_en.md")
        elif cur.get("status") == "deferred":
            if not cur.get("note"):
                errs.append(f"{q['id']}: deferred without a note")
        else:
            errs.append(f"{q['id']}: still '{cur.get('status')}' — answer it or defer it with a note")
    qpath = ROOT / "research" / "queue.yaml"
    queue = {i["id"]: i for i in (load_yaml(qpath)["items"] if qpath.exists() else [])}
    for item in packet["queue"]:
        cur = queue.get(item["id"], {})
        if cur.get("status") != "resolved" and item["id"] not in changes:
            errs.append(f"{item['id']}: neither resolved nor explained in CHANGES.md")

    for name, text in (("report_en.md", en), ("report_zh.md", zh)):
        for img in re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", text):
            if not img.startswith("http") and not (d / img).exists():
                errs.append(f"{name}: image {img} not found")
        for label, rx in PII_PATTERNS.items():
            if rx.search(re.sub(r"https?://\S+", "", text)):
                errs.append(f"{name}: contains what looks like a {label}")
    count = lambda t, rx: len(re.findall(rx, t, re.M))
    if count(en, r"^\|[-| :]+\|$") != count(zh, r"^\|[-| :]+\|$"):
        errs.append("English and Chinese reports have different numbers of tables")
    if count(en, r"!\[") != count(zh, r"!\["):
        errs.append("English and Chinese reports have different numbers of figures")
    for e in errs:
        print("ERROR " + e)
    print(f"check_cycle {v}: {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
