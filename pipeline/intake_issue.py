"""Turn a submission issue (GitHub issue form) into submissions/<type>/<id>/manifest.yaml.

Called by .github/workflows/submission-intake.yml. Can also be run by hand:
  python -m pipeline.intake_issue --event $GITHUB_EVENT_PATH [--download]
  python -m pipeline.intake_issue --body body.md --type data --number 12 --title "..." --author someone

The issue body produced by GitHub issue forms is a series of "### <label>" sections. Labels are matched
by slug, so wording in the form can change as long as the key words below stay.
Claims are entered one per line:  measure | value | unit | level | place | province | period | quote or page
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.request

import yaml

from pipeline.common import SUBMISSIONS, dump_yaml, iter_manifests, parse_years

TYPE_BY_LABEL = {"submission:material": "material", "submission:data": "data", "submission:testimony": "testimony",
                 "submission:research": "research", "submission:correction": "correction"}
REDISTRIBUTABLE = {"CC-BY-4.0", "CC0-1.0", "public-domain", "permission-granted"}
MAX_ATTACHMENT_BYTES = 25 * 1024 * 1024
ATTACHMENT_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/gif", "image/webp", "text/csv", "text/plain",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
LICENSES = {"cc-by-4.0": "CC-BY-4.0", "cc0-1.0": "CC0-1.0", "public domain": "public-domain",
            "quotation only": "quotation-only", "permission granted": "permission-granted"}


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def parse_sections(body: str) -> dict[str, str]:
    out, key, buf = {}, None, []
    for line in body.splitlines():
        m = re.match(r"^###\s+(.*)$", line)
        if m:
            if key:
                out[key] = "\n".join(buf).strip()
            key, buf = slug(m.group(1)), []
        else:
            buf.append(line)
    if key:
        out[key] = "\n".join(buf).strip()
    return {k: ("" if v in ("_No response_", "None") else v) for k, v in out.items()}


def field(sec: dict, *keys: str) -> str:
    """First section whose slug equals, starts with, or contains one of the keys (in that order of preference)."""
    for test in (lambda n, k: n == k, lambda n, k: n.startswith(k), lambda n, k: k in n):
        for k in keys:
            for name, v in sec.items():
                if test(name, k):
                    return v
    return ""


def checked(text: str, needle: str) -> bool:
    return bool(re.search(r"- \[[xX]\][^\n]*" + re.escape(needle), text))


def parse_provenance(text: str, accessed: str | None = None) -> list[dict]:
    out = []
    for line in text.splitlines():
        line = line.strip(" -*\t")
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        url = next((p for p in parts if re.match(r"https?://", p)), "")
        rest = [p for p in parts if p and p != url]
        item = {}
        if rest:
            item["citation"] = rest[0]
        if url:
            item["url"] = url
            item["accessed"] = accessed or dt.date.today().isoformat()
        if len(rest) > 1:
            item["page_ref"] = rest[1]
        if item:
            out.append(item)
    return out


def parse_claims(text: str) -> list[dict]:
    out = []
    for line in text.splitlines():
        parts = [p.strip() for p in line.strip(" -*\t").split("|")]
        if len(parts) < 7:
            continue
        measure, value, unit, level, place, province, period = parts[:7]
        quote = parts[7] if len(parts) > 7 else ""
        try:
            val = float(value.replace(",", ""))
        except ValueError:
            continue
        start, end = parse_years(period)
        c = {"measure": measure, "value": val, "unit": unit, "geography": {"level": level, "name": place},
             "period": {"start": start, "end": end, "label": period}}
        if province:
            c["geography"]["province"] = province
        if quote:
            c["page_ref" if re.match(r"^(p\.|pp\.|page|第)", quote) else "quote"] = quote
        out.append(c)
    return out


def relation(text: str) -> str:
    t = text.strip().lower()
    if t.startswith("first") or "亲历" in t:
        return "firsthand"
    if t.startswith("family") or "家人" in t:
        return "family_firsthand"
    return "secondhand"


def attachment_urls(text: str) -> list[str]:
    return re.findall(r"https://github\.com/user-attachments/(?:files|assets)/[^\s)\]]+", text)


def yaml_load(p: pathlib.Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def existing_for_issue(number: int):
    """Manifest already on this branch (i.e. accepted on main) for this issue, if any."""
    for path, m in iter_manifests():
        if m.get("issue") == number:
            return path
    return None


def build(body: str, typ: str, number: int, title: str, author: str, download: bool = False,
          created: str | None = None) -> pathlib.Path:
    sec = parse_sections(body)
    created = (created or dt.date.today().isoformat())[:10]
    sid = f"SUB-{created[:4]}-{number:04d}"
    folder = SUBMISSIONS / typ / sid
    for other in SUBMISSIONS.glob(f"*/{sid}/manifest.yaml"):
        prev = yaml_load(other)
        if prev.get("issue") not in (None, number) or other.parent.parent.name != typ:
            raise SystemExit(f"{sid} already exists for a different submission ({other}); refusing to overwrite")
    folder.mkdir(parents=True, exist_ok=True)
    lic_text = field(sec, "license", "licence").lower()
    lic = next((v for k, v in LICENSES.items() if k in lic_text), "unknown")
    anonymous = checked(field(sec, "attribution", "credit"), "anonymous")
    m: dict = {
        "id": sid, "type": typ, "title": re.sub(r"^\[[^\]]+\]\s*", "", title).strip(), "issue": number,
        "submitted_by": "anonymous" if anonymous else author,
        "submitted_at": created,
        "language": field(sec, "language") or "unspecified",
        "summary": field(sec, "summary", "what_is_it", "description", "why"),
        "license": lic,
        "provenance": parse_provenance(field(sec, "sources", "provenance", "where"), created),
    }
    orig = field(sec, "original_publication", "first_appeared")
    if orig and m["provenance"]:
        m["provenance"][0]["original_publication"] = orig
    claims = parse_claims(field(sec, "claims", "numbers"))
    if claims:
        m["claims"] = claims
    if typ == "research":
        m["research"] = {"method": field(sec, "method"), "code_url": field(sec, "code"), "data_url": field(sec, "data"),
                         "doi": field(sec, "doi"), "reproducible": checked(field(sec, "reproducib"), "reproduc"),
                         "peer_reviewed": checked(field(sec, "reproducib", "peer"), "eer-review")}
        m["research"] = {k: v for k, v in m["research"].items() if v not in ("", None)}
    if typ == "testimony":
        consent = field(sec, "consent")
        m["testimony"] = {
            "consent": {"publish": checked(consent, "publish"), "anonymized": checked(consent, "identif")},
            "narrator": {"relation": relation(field(sec, "relation", "who_experienced")),
                         "birth_decade": field(sec, "birth_decade", "decade_of_birth")},
            "events": {"province": field(sec, "province"), "county": field(sec, "county"), "period": field(sec, "period", "when")},
        }
        corr = field(sec, "corroborat")
        if corr:
            m["testimony"]["corroborated_by"] = [c.strip(" -") for c in corr.splitlines() if c.strip()]
        text = field(sec, "testimony", "account")
        if not m["summary"]:
            ev = m["testimony"]["events"]
            m["summary"] = (f"Testimony ({m['testimony']['narrator']['relation']}), {ev['province']}, {ev['period']}: "
                            + re.sub(r"\s+", " ", text)[:160]).strip()
        if text:
            (folder / "testimony.md").write_text(text + "\n", encoding="utf-8")
            m["files"] = [{"path": "testimony.md", "sha256": hashlib.sha256((text + "\n").encode()).hexdigest(),
                           "description": "testimony text as submitted (anonymized)"}]
        if not m["provenance"]:
            m["provenance"] = [{"citation": f"Testimony submitted via issue #{number}"}]
    if typ == "correction":
        m["correction"] = {"target": field(sec, "target", "what_should_change"), "proposed_change": field(sec, "proposed", "correction")}
    if not m["title"]:
        m["title"] = (m["summary"][:80].rstrip() or f"Untitled {typ} submission") + f" (#{number})"
    urls = attachment_urls(body)
    if urls and (typ == "testimony" or m["license"] not in REDISTRIBUTABLE):
        m["attachments_not_copied"] = urls
        print("attachments listed but not copied (testimony, or license does not allow redistribution)", file=sys.stderr)
    elif download and urls:
        files = m.setdefault("files", [])
        for i, url in enumerate(urls[:10], start=1):
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
                    data = r.read(MAX_ATTACHMENT_BYTES + 1)
            except Exception as e:  # noqa: BLE001 - attachment download is best-effort
                print(f"could not download {url}: {e}", file=sys.stderr)
                continue
            if len(data) > MAX_ATTACHMENT_BYTES or ctype not in ATTACHMENT_TYPES:
                print(f"skipped {url}: {ctype}, {len(data)} bytes", file=sys.stderr)
                m.setdefault("attachments_not_copied", []).append(url)
                continue
            ext = {"application/pdf": ".pdf", "image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif", "image/webp": ".webp",
                   "text/csv": ".csv", "text/plain": ".txt"}.get(ctype, pathlib.Path(url).suffix)
            name = f"attachment_{i}{ext}"
            (folder / name).write_bytes(data)
            files.append({"path": name, "sha256": hashlib.sha256(data).hexdigest(), "description": f"uploaded with issue #{number}"})
        if not files:
            m.pop("files")
    dump_yaml(m, folder / "manifest.yaml", f"# Created from issue #{number} by pipeline/intake_issue.py. Edit freely in the PR.\n")
    return folder


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--event")
    ap.add_argument("--body")
    ap.add_argument("--type", choices=sorted(set(TYPE_BY_LABEL.values())))
    ap.add_argument("--number", type=int)
    ap.add_argument("--title", default="")
    ap.add_argument("--author", default="anonymous")
    ap.add_argument("--download", action="store_true")
    a = ap.parse_args(argv)
    if a.event:
        ev = json.loads(pathlib.Path(a.event).read_text(encoding="utf-8"))
        iss = ev["issue"]
        labels = [l["name"] for l in iss.get("labels", [])]
        typ = next((TYPE_BY_LABEL[l] for l in labels if l in TYPE_BY_LABEL), None)
        if not typ:
            print("no submission:* label; nothing to do")
            return 0
        if iss.get("state") != "open":
            print("issue is closed; nothing to do")
            return 0
        if existing_for_issue(iss["number"]):
            print(f"issue #{iss['number']} already has an accepted submission on this branch; not regenerating")
            return 0
        folder = build(iss.get("body") or "", typ, iss["number"], iss["title"], iss["user"]["login"], a.download,
                       iss.get("created_at"))
    else:
        folder = build(pathlib.Path(a.body).read_text(encoding="utf-8"), a.type, a.number, a.title, a.author, a.download)
    rel = folder.relative_to(SUBMISSIONS.parent)
    print(rel)
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"path={rel}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
