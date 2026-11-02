# Reconciliation

`pipeline/reconcile.py` compares numbers so that disagreements are found by machine and explained by people.

## Normalization

Every claim is reduced to: measure, value (counts converted to millions), geography (province names matched
across English and Chinese, e.g. 四川省 = Sichuan), and period (start/end years). Claims come from
`data/registry/claims.yaml` and from every accepted submission.

## Classification of each new claim

| Status | Rule | What happens |
|---|---|---|
| consistent | Same measure, place and overlapping period; inside the registered range ± tolerance (15%) | Nothing; the claim strengthens the registry |
| definitional | Different measure in the death family, in the expected order (starvation ≤ excess ≈ abnormal ≤ total) | Noted; often explains apparent conflicts (e.g. a gazetteer's total deaths vs an excess estimate) |
| conflict | Same measure, place and period, outside the range; or a different measure in the wrong order | Research-queue item |
| new_coverage | Nothing comparable registered (new county, year or measure) | Research-queue item, so the next cycle can place it |

## Coherence checks across levels

- **Provincial sums vs national**: when one source gives ten or more provinces, their sum is compared with the
  same source's national figure (ratio 0.85–1.15 expected) and with the current model band.
- **Sub-provincial vs provincial**: county and prefecture deaths in a province should not exceed the highest
  provincial estimate; if they do, localities may overlap or be double counted.
- **Rate plausibility**: death rates outside level-specific bounds are flagged as likely typos or unit errors.
- **National vs model band**: national excess-death claims outside the current range are listed by method class.

Findings that involve only reviewed registry claims are marked `known`; findings that touch a new submission are
marked `check` and enter the research queue.

## The research queue

`research/queue.yaml` holds open items. A research cycle must resolve each one or explain in `CHANGES.md` why it
could not. Maintainers may close an item by hand with a `resolution` note.

## Limits

Reconciliation is arithmetic, not judgment. It cannot tell a faithful repost from a garbled one, or whether a
"non-normal death" count includes normal deaths. That is the research cycle's and reviewers' job.
