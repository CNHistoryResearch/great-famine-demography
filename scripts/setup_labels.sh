#!/usr/bin/env bash
# Create the labels the workflows use. Requires: gh auth login (repo scope). Usage: bash scripts/setup_labels.sh [owner/repo]
set -euo pipefail
repo=${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}
mk() { gh label create "$1" --repo "$repo" --color "$2" --description "$3" --force; }
mk "submission:material"   "1d76db" "Document or publication as evidence"
mk "submission:data"       "0e8a16" "Numerical data"
mk "submission:testimony"  "5319e7" "Oral history or family account"
mk "submission:research"   "006b75" "Paper, estimate or reanalysis"
mk "submission:correction" "b60205" "Error in report, data or registry"
mk "submission:rejected"   "cccccc" "Declined by maintainers"
mk "submission:triage-ok"  "0e8a16" "Maintainer: open the PR for a first-time contributor's submission"
mk "submission:locked"     "5319e7" "Maintainer edited the PR by hand; issue edits no longer regenerate it"
mk "submission"            "c5def5" "Submission pull request"
mk "gate:passed"           "0e8a16" "Quality gates G0-G3 passed"
mk "gate:needs-work"       "fbca04" "A quality gate failed"
mk "question"              "d4c5f9" "Reader question"
mk "question:candidate"    "d4c5f9" "Triage: ready for maintainer decision"
mk "question:accepted"     "5319e7" "Will be answered in the next report"
mk "question:declined"     "cccccc" "Maintainer decided not to take this question"
mk "question:duplicate"    "cccccc" "Already asked"
mk "question:needs-clarification" "fbca04" "Please rephrase"
mk "question:out-of-scope" "cccccc" "Outside the project's scope"
mk "reconciliation"        "f9d0c4" "Reconciliation tracking"
mk "report:draft"          "fef2c0" "Draft report from a research cycle"
