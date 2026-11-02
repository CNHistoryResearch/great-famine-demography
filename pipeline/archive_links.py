"""Make sure every cited URL has an archived copy (Gate 1 support).

For each provenance URL without `archive_url` in the given submissions:
  1. ask the Wayback Machine availability API for the closest existing snapshot;
  2. if none, request a new capture through Save Page Now (anonymous, rate-limited);
  3. write the snapshot URL back into the manifest.
Network failures never fail the build; the URL is simply left for a maintainer.

  python -m pipeline.archive_links --changed
  python -m pipeline.archive_links submissions/material/SUB-2026-0007
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

from pipeline.common import changed_files, dump_yaml, iter_manifests, yaml_header

UA = {"User-Agent": "great-famine-demography-archiver/1.0 (+https://github.com)"}


def closest(url: str) -> str | None:
    api = "https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe="")
    try:
        with urllib.request.urlopen(urllib.request.Request(api, headers=UA), timeout=30) as r:
            snap = json.load(r).get("archived_snapshots", {}).get("closest")
        return snap["url"] if snap and snap.get("available") else None
    except Exception as e:  # noqa: BLE001
        print(f"  availability check failed for {url}: {e}")
        return None


def save(url: str) -> str | None:
    try:
        req = urllib.request.Request("https://web.archive.org/save/" + url, headers=UA)
        with urllib.request.urlopen(req, timeout=120) as r:
            loc = r.headers.get("Content-Location") or r.geturl()
        return loc if loc.startswith("http") else "https://web.archive.org" + loc
    except Exception as e:  # noqa: BLE001
        print(f"  save failed for {url}: {e}")
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", type=pathlib.Path)
    ap.add_argument("--changed", action="store_true")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--no-save", action="store_true", help="only look up existing snapshots")
    a = ap.parse_args(argv)
    targets = iter_manifests(changed_files(a.base)) if a.changed else iter_manifests(a.paths or None)
    for path, m in targets:
        dirty = False
        for p in m.get("provenance") or []:
            if p.get("url") and not p.get("archive_url") and "web.archive.org" not in p["url"]:
                snap = closest(p["url"]) or (None if a.no_save else save(p["url"]))
                if snap:
                    p["archive_url"] = snap
                    dirty = True
                    print(f"{m['id']}: {p['url']} -> {snap}")
                time.sleep(5)  # be polite to the Wayback Machine
        if dirty:
            dump_yaml(m, path, yaml_header(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
