# Governance

## Roles

| Role | Who | Can |
|---|---|---|
| Contributor | Anyone with a GitHub account (anonymous accounts welcome) | Submit through issue forms or pull requests; comment |
| Reviewer | Contributors invited after sustained, careful work | Review submissions; approve pull requests (counts toward G4) |
| Maintainer | Listed in `.github/CODEOWNERS` | Merge; accept or decline questions; start research cycles; edit registries; release reports |
| Research agent | The `research-cycle` workflow (Claude) | Draft research notes and report versions **as pull requests only**; never merges, never pushes to `main` |

## Decisions

- **Accepting a submission** = merging its pull request after gates G0–G3 pass and one approving review (G4).
  A submission that would change a headline number needs **two** approvals.
- **Accepting a question** = a maintainer applies `question:accepted`. Declined questions get a one-line reason.
- **Publishing a report version** = merging the report pull request. Requires two approvals (enforced by the
  `Report approvals` check), at least one from a maintainer who did not start the research cycle. The `CHANGES.md`
  must account for every packet item.
- **Changing the headline** requires: the model change or new data in the same pull request, the
  `EST-OURS-*` registry entry updated, and an explanation of which assumption moved and by how much.
- **Disputes** about evidence are settled by evidence. If reviewers still disagree after discussion, the report states
  both readings and what would decide between them; a maintainer vote (simple majority) decides only wording.

## Standards for reviewers

- Check numbers against their original (page, table), not against a repost, whenever the original is reachable.
- Grade sources A–D and testimony T1–T3 per [docs/quality-gates.md](docs/quality-gates.md).
- Apply the same scrutiny to low and high estimates. Do not reject material for its conclusion.
- Never ask a contributor to identify themselves. Remove personal data you find, even in your own reviews.

## Conflicts of interest

Reviewers and maintainers do not approve their own submissions or research they authored, and disclose any
affiliation relevant to a submission (employer, funder, co-authorship) in the review.

## Safety of contributors

The subject is politically sensitive. The project never requires real names, never publishes contact details,
removes identifying details from testimony, and keeps no logs beyond what GitHub itself records. Maintainers
should read [docs/testimony-policy.md](docs/testimony-policy.md) and point contributors to it.

## Changing these rules

Amendments to this file, the quality gates or the testimony policy need two maintainer approvals and a 7-day
open comment period on the pull request.
