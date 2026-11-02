"""Decide whether a research cycle is due and assemble the packet the research agent works from.

  python -m pipeline.research_packet --check          # prints due=true/false (for GitHub Actions output)
  python -m pipeline.research_packet --write          # writes research/<next>/packet.md and packet.json
  python -m pipeline.research_packet --write --force  # ignore thresholds

The packet lists, in priority order: open research-queue items (reconciliation conflicts and coherence
problems), accepted questions, and new accepted submissions since the last report. The research agent
must address every item or explain why it could not.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

from pipeline.common import QUESTIONS, REPORTS, ROOT, current_version, iter_manifests, load_yaml, next_version


def gather():
    cfg = load_yaml(ROOT / "pipeline" / "config.yaml")["research_cycle"]
    cur = current_version()
    meta = load_yaml(REPORTS / cur / "meta.yaml")
    published = str(meta["published"])
    subs = [(p, m) for p, m in iter_manifests() if str(m.get("submitted_at", "")) > published]
    qpath = ROOT / "research" / "queue.yaml"
    queue = [i for i in (load_yaml(qpath)["items"] if qpath.exists() else []) if i["status"] == "open"]
    questions = [q for q in load_yaml(QUESTIONS)["questions"] if q["status"] == "accepted"]
    prio = {"high": 0, "medium": 1, "low": 2}
    questions.sort(key=lambda q: prio.get(q.get("priority", "medium"), 1))
    reasons = []
    if len(subs) >= cfg["min_new_submissions"]:
        reasons.append(f"{len(subs)} new submissions")
    if len(queue) >= cfg["min_open_queue_items"]:
        reasons.append(f"{len(queue)} open queue items")
    if len(questions) >= cfg["min_accepted_questions"]:
        reasons.append(f"{len(questions)} accepted questions")
    return cfg, cur, meta, subs, queue, questions, reasons


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--bump", choices=["minor", "major"], default="minor")
    a = ap.parse_args(argv)
    cfg, cur, meta, subs, queue, questions, reasons = gather()
    due = bool(reasons) or a.force
    nxt = next_version(a.bump)
    if a.check or not a.write:
        print(f"due={'true' if due else 'false'}")
        print(f"next={nxt}")
        print(f"reasons={'; '.join(reasons) or ('forced' if a.force else 'none')}")
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
                f.write(f"due={'true' if due else 'false'}\nnext={nxt}\n")
        if not a.write:
            return 0
    if not due:
        print("not due; nothing written")
        return 0
    cap = cfg["max_items_per_cycle"]
    out_dir = ROOT / "research" / nxt
    out_dir.mkdir(parents=True, exist_ok=True)
    rec_path = REPORTS / "reconciliation" / "latest.md"
    packet = {
        "created": dt.date.today().isoformat(), "current_version": cur, "next_version": nxt,
        "headline": meta["headline"], "reasons": reasons or ["forced"],
        "queue": queue[:cap], "questions": questions[:cap],
        "submissions": [{"id": m["id"], "type": m["type"], "title": m["title"], "path": str(p.parent.relative_to(ROOT)),
                         "claims": len(m.get("claims") or []), "review": (m.get("review") or {}).get("status")} for p, m in subs[:cap]],
        "deferred": {"queue": max(0, len(queue) - cap), "questions": max(0, len(questions) - cap), "submissions": max(0, len(subs) - cap)},
    }
    (out_dir / "packet.json").write_text(json.dumps(packet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    md = [f"# Research packet for {nxt}", "", f"Created {packet['created']} from report {cur}. Why now: {'; '.join(packet['reasons'])}.", "",
          f"Current headline: {meta['headline']['excess_deaths_million']['central']} million excess deaths "
          f"(range {meta['headline']['excess_deaths_million']['low']}–{meta['headline']['excess_deaths_million']['high']}).", "",
          "## 1. Research queue (from reconciliation)", ""]
    md += [f"- **{i['id']}** [{i['kind']}] {i['ref']} — {i['reason']}" for i in packet["queue"]] or ["- none"]
    md += ["", "## 2. Accepted questions to answer", ""]
    md += [f"- **{q['id']}** ({q.get('priority', 'medium')}) {q.get('text_en') or ''} {q.get('text_zh') or ''}".rstrip() for q in packet["questions"]] or ["- none"]
    md += ["", "## 3. New accepted submissions", ""]
    md += [f"- **{s['id']}** [{s['type']}] {s['title']} — `{s['path']}` ({s['claims']} claims)" for s in packet["submissions"]] or ["- none"]
    md += ["", "## 4. Latest reconciliation report", "", f"See `{rec_path.relative_to(ROOT)}`." if rec_path.exists() else "Not yet generated.", ""]
    if any(packet["deferred"].values()):
        md += [f"Deferred to a later cycle (over the cap of {cap}): {packet['deferred']}", ""]
    (out_dir / "packet.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote research/{nxt}/packet.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
