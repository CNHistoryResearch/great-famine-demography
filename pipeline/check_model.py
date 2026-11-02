"""Re-run the national model and confirm it reproduces the published headline.

  python -m pipeline.check_model [--tolerance 0.1]

Fails if the central excess-death estimate differs from the latest EST-OURS-* entry in
data/registry/estimates.yaml by more than the tolerance (millions). A data change that moves the
headline must update the registry and the report in the same pull request.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

from pipeline.common import REGISTRY, ROOT, load_yaml


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tolerance", type=float, default=0.1)
    a = ap.parse_args(argv)
    d = ROOT / "models" / "national"
    subprocess.run([sys.executable, "-I", "famine_model.py"], cwd=d, check=True, stdout=subprocess.DEVNULL)
    got = json.loads((d / "results" / "summary.json").read_text())["central"]["excess_FY58_62"]
    ours = [e for e in load_yaml(REGISTRY / "estimates.yaml")["estimates"] if e["id"].startswith("EST-OURS")]
    want = ours[-1]["central"]
    print(f"model central excess deaths: {got:.2f}M; registry {ours[-1]['id']}: {want}M")
    if abs(got - want) > a.tolerance:
        print(f"ERROR: differs by {abs(got - want):.2f}M (> {a.tolerance}). Update estimates.yaml and the report together.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
