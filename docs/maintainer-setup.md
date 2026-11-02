# Maintainer setup

One-time configuration after creating the repository.

## 1. Secrets and variables (Settings → Secrets and variables → Actions)

| Name | Kind | Purpose |
|---|---|---|
| `BOT_TOKEN` | Secret (strongly recommended) | Fine-grained personal access token or GitHub App token for this repository with **Contents, Pull requests, Issues: read and write**. Bot-opened pull requests (submissions, questions, reconciliation, reports) only trigger CI and the quality gate when created with this token; with the default `GITHUB_TOKEN` they do not, and a maintainer has to close and reopen each one to start the checks. |
| `ANTHROPIC_API_KEY` | Secret | Used only by `research-cycle.yml` to run Claude. Without it, everything else still works. The workflow passes the repository token to the action, so the Claude GitHub App is not required. |
| `RESEARCH_CYCLE_SCHEDULE` | Variable | Set to `enabled` to let the monthly schedule start research cycles. Until then cycles run only when started by hand (Actions → Research cycle → Run workflow), so nothing is spent without a decision. |
| `CLAUDE_MODEL` | Variable (optional) | Model for research cycles; default `claude-opus-5-5`. |
| `CLAUDE_MAX_TURNS` | Variable (optional) | Turn cap per cycle (cost control); default 400. |

## 2. Actions permissions (Settings → Actions → General)

- Workflow permissions: **Read and write**.
- Check **Allow GitHub Actions to create and approve pull requests** (intake, question acceptance and research
  cycles open PRs).
- For pull requests from forks, keep the default approval requirement for first-time contributors.

## 3. Branch protection for `main` (Settings → Branches)

- Require a pull request before merging, **1 approval**, and review from Code Owners.
- Require status checks: `CI / checks`, `Quality gate / gate` (passes instantly on PRs without submissions) and
  `Report approvals / count` (requires 2 approvals when a report version or the headline estimate changes).
- Do not allow bypassing the above. No workflow pushes to `main` directly; automation always opens pull requests.

## 4. Code owners

Edit `.github/CODEOWNERS` and replace the placeholder with your GitHub handle (and co-maintainers).
Replace `OWNER/REPO` in `.github/ISSUE_TEMPLATE/config.yml` with the repository path.

## 5. Labels

```bash
bash scripts/setup_labels.sh          # needs the gh CLI, logged in with repo access
```

## 6. Day-to-day

- **First-time contributors** get an automatic gate preview on their issue; add `submission:triage-ok` to open the PR.
- If you edit a submission PR by hand, add `submission:locked` to its issue so later issue edits don't overwrite it.
- Decide questions with `question:accepted` or `question:declined`.
- Merge the weekly `bot/reconciliation` PR to update the research queue.

## 7. Optional

- GitHub Pages from `reports/` for a browsable site.
- A private contact channel for sensitive testimony (see docs/testimony-policy.md). Publish only an address you
  are comfortable being public.
