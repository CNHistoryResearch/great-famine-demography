"""Shared helpers for the pipeline. Standard library + PyYAML + jsonschema only."""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import subprocess
from typing import Iterable

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "registry"
SUBMISSIONS = ROOT / "submissions"
QUESTIONS = ROOT / "questions" / "questions.yaml"
REPORTS = ROOT / "reports"
SCHEMAS = ROOT / "schemas"

SUBMISSION_TYPES = ("material", "data", "testimony", "research", "correction")


def load_yaml(path: pathlib.Path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(obj, path: pathlib.Path, header: str = "") -> None:
    text = yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=200)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + text, encoding="utf-8")


def yaml_header(path: pathlib.Path) -> str:
    """Leading comment lines of a YAML file, so rewrites keep them."""
    out = []
    for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
        if not line.startswith("#"):
            break
        out.append(line)
    return "".join(out)


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def schema_validator(name: str):
    """Return a jsonschema validator that resolves the local $refs between our schemas."""
    import jsonschema
    from referencing import Registry, Resource

    resources = []
    for p in SCHEMAS.glob("*.schema.json"):
        s = json.loads(p.read_text(encoding="utf-8"))
        resources.append((p.name, Resource.from_contents(s)))
    registry = Registry().with_resources(resources)
    schema = load_schema(name)
    cls = jsonschema.validators.validator_for(schema)
    return cls(schema, registry=registry, format_checker=cls.FORMAT_CHECKER)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_manifests(paths: Iterable[pathlib.Path] | None = None):
    """Yield (manifest_path, manifest) for every submission, or only those under the given paths."""
    if paths is not None:
        seen = set()
        for p in paths:
            p = p if p.is_absolute() else (ROOT / p)
            try:
                rel = p.resolve().relative_to(SUBMISSIONS)
            except ValueError:
                continue
            if len(rel.parts) < 2:
                continue
            cand = SUBMISSIONS / rel.parts[0] / rel.parts[1] / "manifest.yaml"
            if cand.exists() and cand not in seen:
                seen.add(cand)
                yield cand, load_yaml(cand)
        return
    for m in sorted(SUBMISSIONS.glob("*/*/manifest.yaml")):
        yield m, load_yaml(m)


def changed_files(base: str = "origin/main") -> list[pathlib.Path]:
    """Files changed relative to base (used in pull-request workflows)."""
    try:
        out = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return []
    return [pathlib.Path(line) for line in out.splitlines() if line.strip()]


def normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"https?://\S+", " ", s)
    return re.sub(r"[\s\W_]+", " ", s).strip()


def tokens(s: str) -> list[str]:
    """Word tokens for Latin text plus character bigrams for CJK, so Chinese questions dedupe too."""
    s = normalize_text(s)
    out = re.findall(r"[a-z0-9]+", s)
    cjk = re.findall(r"[一-鿿]", s)
    out += ["".join(cjk[i:i + 2]) for i in range(len(cjk) - 1)]
    return out


def cosine(a: list[str], b: list[str]) -> float:
    from collections import Counter
    import math
    ca, cb = Counter(a), Counter(b)
    num = sum(ca[t] * cb[t] for t in ca.keys() & cb.keys())
    den = math.sqrt(sum(v * v for v in ca.values())) * math.sqrt(sum(v * v for v in cb.values()))
    return num / den if den else 0.0


def to_millions(value: float, unit: str) -> float | None:
    if unit == "million":
        return value
    if unit == "person":
        return value / 1e6
    return None


def vkey(v: str) -> tuple:
    """Sort key for version strings like 'v1.10' (numeric, so v1.10 > v1.9)."""
    try:
        return tuple(int(x) for x in str(v).lstrip("v").split("."))
    except ValueError:
        return (-1,)


def parse_years(label: str) -> tuple[int | None, int | None]:
    """Year range from a period label: '1960', '1959-61', '1959–1961', '1959年至1961年', 'winter 1959 – spring 1960'."""
    if not label:
        return None, None
    text = str(label)
    years = []
    for m in re.finditer(r"(19\d\d)(?:\s*[-–—~至到]\s*(\d{2})(?!\d))?", text):
        years.append(int(m.group(1)))
        if m.group(2):
            years.append(int(m.group(1)[:2] + m.group(2)))
    return (min(years), max(years)) if years else (None, None)


def current_version() -> str:
    versions = sorted((p.name for p in REPORTS.glob("v*") if p.is_dir()), key=vkey)
    return versions[-1] if versions else "v0.0"


def next_version(kind: str = "minor") -> str:
    major, minor = (int(x) for x in current_version()[1:].split("."))
    return f"v{major + 1}.0" if kind == "major" else f"v{major}.{minor + 1}"


# Provisional source grade by domain (maintainers can override in sources.yaml)
GRADE_BY_DOMAIN = [  # (substring, grade, kind)
    ("stats.gov.cn", "A", "official_statistics"), ("worldbank.org", "B", "research_report"),
    ("github.com/PPgp", "B", "dataset"), ("cairn.info", "B", "peer_reviewed"), ("ucd.ie", "B", "working_paper"),
    ("rkyj.ruc.edu.cn", "B", "peer_reviewed"), ("iussp.org", "B", "conference_paper"), ("gwern.net", "B", "peer_reviewed_copy"),
    ("ageconsearch", "B", "working_paper"), ("kellogg", "B", "peer_reviewed_copy"), ("berkeley.edu", "B", "peer_reviewed_copy"),
    ("springer.com", "B", "book_chapter"), ("history.state.gov", "A", "government_archive"), ("wilsoncenter", "A", "archival_document"),
    ("aisixiang.com", "C", "repost"), ("chinadigitaltimes.net", "C", "journalism_or_repost"), ("nybooks.com", "C", "journalism"),
    ("chinafile.com", "C", "journalism"), ("saildart.org", "C", "wire_copy"), ("adst.org", "C", "oral_history"),
    ("globalvoices", "C", "journalism"), ("themoscowtimes", "C", "journalism"), ("chinanews.com.cn", "C", "state_media"),
    ("wikipedia.org", "D", "encyclopedia"), ("yhcw.net", "C", "mirror"), ("bannedbook.org", "C", "mirror"),
    ("gotohui.com", "C", "data_aggregator"), ("zhihu.com", "D", "user_post"), ("wyzxwk.com", "C", "opinion"),
    ("minjian-danganguan", "C", "archive_mirror"), ("ttcdw.com", "C", "repost"), ("web.archive.org", "C", "archive_snapshot"),
    ("marxistarkiv", "C", "document_copy"), ("china-embassy", "A", "official_document"), ("ennonline", "C", "journalism"),
    ("ihsn.org", "B", "catalog"), ("lists.osu.edu", "D", "mailing_list"), ("freeweibo", "D", "censorship_mirror"),
    ("nytimes.com", "C", "journalism"), ("ifeng.com", "C", "journalism"), ("cass.cn", "A", "official_journal_toc"),
    ("rpb115.nsysu", "B", "journal_article"),
]
def grade_url(url):
    for s, g, k in GRADE_BY_DOMAIN:
        if s in url: return g, k
    return "unrated", "unknown"

