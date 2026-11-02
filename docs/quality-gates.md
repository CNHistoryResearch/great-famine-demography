# Quality gates

Every submission passes five gates. G0–G3 are automatic (`pipeline/quality_gate.py`, run on every pull request,
using the gate code from the base branch so a pull request cannot change the rules it is judged by); G4 is human
review. A submission is accepted when its pull request is merged.

| Gate | Checks | Automated by | Fails when |
|---|---|---|---|
| **G0 Structure** | Manifest matches `schemas/submission.schema.json`; folder name equals id; files exist and their SHA-256 matches | `pipeline/validate.py` | Required field missing, wrong type, file missing or altered |
| **G1 Provenance** | Every source has a URL or a citation with page reference; URLs get an archived copy; license allows redistribution of attached files | `pipeline/quality_gate.py`, `pipeline/archive_links.py` | Citation without URL or page; files attached with unknown license |
| **G2 Verifiability** | Every number has a verbatim quote or page/table reference; values plausible for their measure and unit; research gives method + code/data/DOI; testimony has consent and no personal identifiers | `pipeline/quality_gate.py` | Unsourced number; impossible value; research without method; personal data in testimony |
| **G3 Novelty** | At least one new source, file or claim compared with the registry and other submissions (testimony, research and corrections always count as new) | `pipeline/quality_gate.py` | Everything already registered |
| **G4 Review** | A reviewer checks the evidence itself, grades it, and decides | Humans (CODEOWNERS, branch protection) | Evidence does not support what the submission says |

Warnings (missing archive link, unknown original publication) do not block, but reviewers should resolve them.

## Source grades (A–D)

| Grade | Meaning | Examples |
|---|---|---|
| A | Primary official statistics or archival documents, checkable at the original | NBS yearbooks, census communiqués, archival reports, official journals |
| B | Peer-reviewed research or research-institution reports; faithful copies of A-grade material | Population and Development Review, World Bank papers, UN WPP, mirrored SSB tables |
| C | Secondary: journalism, reposts, mirrors, oral-history collections, state media commentary | China Digital Times reposts, aisixiang, newspaper reports |
| D | User-generated or unverifiable: social media, forums, encyclopedias, anonymous claims | Weibo, Zhihu, Wikipedia |

`pipeline/common.py:grade_url` assigns a provisional grade by domain; reviewers override it in `data/registry/sources.yaml`.
A number from a C or D source should be traced to an A or B original before it moves a headline figure.

## Testimony grades (T1–T3)

| Grade | Meaning |
|---|---|
| T1 | First-hand (narrator or immediate family) **and** corroborated by a document or independent account |
| T2 | First-hand, internally consistent, not yet corroborated |
| T3 | Second-hand |

Testimony informs the report as evidence of experience and of local conditions. A T1 account may support a local
figure; testimony never sets a national or provincial number by itself.

## Claims

Numbers are recorded as claims (`schemas/claim.schema.json`) with a measure, unit, geography and period, so that
reconciliation compares like with like. The measure must be what the source states:

- `excess_deaths`: deaths above a no-famine counterfactual (the report's headline concept)
- `abnormal_deaths`: what a document calls 非正常死亡, definition unstated
- `starvation_deaths`: explicitly 饿死
- `total_deaths`: all deaths in the period, normal ones included
- `lost_births`, `population_change`, `cdr`, `cbr`, `imr`, `life_expectancy`, `population`
