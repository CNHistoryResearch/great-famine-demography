"""Triage reader questions and add accepted ones to questions/questions.yaml.

  python -m pipeline.triage_questions triage --event $GITHUB_EVENT_PATH --out comment.md --labels labels.txt
  python -m pipeline.triage_questions accept --event $GITHUB_EVENT_PATH      # when a maintainer labels question:accepted
  python -m pipeline.triage_questions triage --text "为什么1962年人口大增？"

Automatic triage never accepts a question by itself. It suggests one of:
  question:duplicate (similarity >= 0.6 to an existing question), question:needs-clarification (too short / not a question),
  question:out-of-scope (no in-scope keywords), question:candidate (ready for a maintainer decision).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

import yaml

from pipeline.common import QUESTIONS, cosine, load_yaml, tokens
from pipeline.intake_issue import field, parse_sections

SCOPE = [
    "famine", "death", "died", "mortality", "starv", "census", "population", "birth", "fertility", "hukou", "register", "province",
    "county", "rural", "urban", "age", "cohort", "estimate", "toll", "great leap", "commune", "grain", "procurement", "archive",
    "testimony", "1958", "1959", "1960", "1961", "1962",
    "饥荒", "死亡", "饿死", "人口", "普查", "出生", "生育", "户籍", "户口", "省", "县", "农村", "城市", "年龄", "大跃进", "公社",
    "粮食", "征购", "档案", "口述", "三年", "困难时期", "自然灾害",
]
DUP, RELATED = 0.6, 0.35


def all_texts(q: dict) -> list[str]:
    return [t for t in (q.get("text_en"), q.get("text_zh")) if t]


def triage(text: str, issue: int | None = None) -> dict:
    qs = [q for q in load_yaml(QUESTIONS)["questions"] if issue is None or q.get("issue") != issue]
    tk = tokens(text)
    scored = sorted(((max(cosine(tk, tokens(t)) for t in all_texts(q)), q) for q in qs), key=lambda x: -x[0])
    low = text.lower()
    in_scope = any(k in low for k in SCOPE)
    is_question = bool(re.search(r"[?？]|^(how|why|what|which|who|when|where|is|are|was|were|did|does|can)\b|吗|么|为什么|怎么|多少|哪", low.strip()))
    if scored and scored[0][0] >= DUP:
        label, note = "question:duplicate", f"Looks like a duplicate of **{scored[0][1]['id']}** (similarity {scored[0][0]:.2f})."
    elif len(text.strip()) < 12 or not is_question:
        label, note = "question:needs-clarification", "Please phrase this as a specific question we could answer with evidence."
    elif not in_scope:
        label, note = "question:out-of-scope", "This does not seem to be about the 1958–62 famine's demography, sources or record."
    else:
        label, note = "question:candidate", "Ready for a maintainer decision (accept, defer, or reject)."
    related = [(s, q) for s, q in scored[:5] if s >= RELATED]
    return {"label": label, "note": note, "related": [{"id": q["id"], "score": round(s, 2), "status": q["status"],
                                                       "text": q.get("text_en") or q.get("text_zh")} for s, q in related]}


def comment(res: dict) -> str:
    lines = ["**Automatic question triage**", "", f"Suggested: `{res['label']}`. {res['note']}"]
    if res["related"]:
        lines += ["", "Related questions already in the registry:", ""] + [
            f"- {r['id']} ({r['status']}, similarity {r['score']}): {r['text']}" for r in res["related"]]
    lines += ["", "A maintainer decides. Accepted questions are answered in the next report version and listed in `questions/questions.yaml`."]
    return "\n".join(lines)


def accept(text_en: str, text_zh: str, issue: int | None, priority: str = "medium") -> str:
    """Append an accepted question. Questions from issues get the deterministic id Q-1<issue, 4 digits>
    (issue #7 -> Q-10007) so parallel acceptance PRs never collide; the file is appended to, not rewritten."""
    data = load_yaml(QUESTIONS)
    if issue and any(q.get("issue") == issue for q in data["questions"]):
        return next(q["id"] for q in data["questions"] if q.get("issue") == issue)
    qid = f"Q-1{issue:04d}" if issue else f"Q-{max(int(q['id'][2:]) for q in data['questions'] if int(q['id'][2:]) < 10000) + 1:04d}"
    q = {"id": qid, **({"issue": issue} if issue else {}), "status": "accepted", "priority": priority}
    if text_en:
        q["text_en"] = text_en
    if text_zh:
        q["text_zh"] = text_zh
    block = yaml.safe_dump([q], allow_unicode=True, sort_keys=False, width=200)
    text = QUESTIONS.read_text(encoding="utf-8").rstrip("\n") + "\n" + "".join("  " + ln + "\n" for ln in block.splitlines())
    QUESTIONS.write_text(text, encoding="utf-8")
    return qid


def question_from_issue(ev: dict) -> tuple[str, int, str]:
    iss = ev["issue"]
    sec = parse_sections(iss.get("body") or "")
    text = field(sec, "your_question", "question", "问题") or re.sub(r"^\[[^\]]+\]\s*", "", iss["title"])
    ctx = field(sec, "context", "background")
    return text.strip(), iss["number"], ctx


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["triage", "accept"])
    ap.add_argument("--event")
    ap.add_argument("--text")
    ap.add_argument("--out")
    ap.add_argument("--labels")
    ap.add_argument("--priority", default="medium")
    a = ap.parse_args(argv)
    if a.event:
        text, number, _ = question_from_issue(json.loads(pathlib.Path(a.event).read_text(encoding="utf-8")))
    else:
        text, number = a.text or "", None
    if a.cmd == "triage":
        res = triage(text, number)
        md = comment(res)
        if a.out:
            pathlib.Path(a.out).write_text(md, encoding="utf-8")
        if a.labels:
            pathlib.Path(a.labels).write_text(res["label"] + "\n", encoding="utf-8")
        print(md)
    else:
        cjk = bool(re.search(r"[一-鿿]", text))
        qid = accept("" if cjk else text, text if cjk else "", number, a.priority)
        print(qid)
    return 0


if __name__ == "__main__":
    sys.exit(main())
