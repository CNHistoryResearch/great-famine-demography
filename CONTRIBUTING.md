# Contributing / 参与贡献

Thank you for helping document this history. You do not need to know Git: everything starts with an issue form.
感谢参与。不需要会用 Git，一切从填写议题表单开始（中文说明见下文）。

## What you can submit

| Type | Use it for | Form |
|---|---|---|
| Material | A document or publication containing evidence: gazetteer page, internal report, article, archived web page | Submit material |
| Data | Numbers: death rates, population counts, registration figures, survey tables | Submit data |
| Testimony | A first-hand or family account (read [the testimony policy](docs/testimony-policy.md) first) | Submit testimony |
| Research | A paper, estimate, reanalysis or critique | Submit research |
| Correction | Something in the report, data or registry is wrong | Report an error |
| Question | Something you want the next report to answer | Ask a question |

Open one at **Issues → New issue**. Issues are public: never include your real name, contact details, or anything
that identifies living private persons.

## What happens next

1. **Intake.** A bot reads your issue and comments with an automatic check of gates G0–G3
   ([docs/quality-gates.md](docs/quality-gates.md)). If something fails, the comment says what to fix; edit the issue
   and it runs again.
2. **Pull request.** The bot turns the issue into a pull request containing `submissions/<type>/<id>/manifest.yaml`
   (and attached files, if the license allows redistribution; testimony attachments are never copied). For a first
   contribution, a maintainer looks at the issue first and opens the PR by adding `submission:triage-ok`.
3. **Gate G4: review.** A maintainer checks the evidence. Merging the pull request accepts the submission and
   closes your issue.
4. **Reconciliation** places your numbers next to everything already known and flags disagreements.
5. **Research cycle.** Accepted material and questions are investigated and folded into the next report version.
   Question issues are closed with a link to the report that answers them.

## Writing claims (numbers)

One number per line, in this order:

```
measure | value | unit | level | place | province | period | quote or page
starvation_deaths | 37000 | person | county | Gaoyou | Jiangsu | 1959-61 | p. 85
cdr | 68.58 | per_mille | province | Anhui | | 1960 | Table 1
```

- **measure**: `excess_deaths` (deaths above normal), `abnormal_deaths` (a document's 非正常死亡), `starvation_deaths` (饿死),
  `total_deaths` (all deaths, including normal ones), `population_change`, `lost_births`, `births`, `cdr`, `cbr`, `imr`, `life_expectancy`, `population`.
  Pick the one the source actually states. Do not convert total deaths into excess deaths yourself.
- **unit**: `person`, `million`, `per_mille` (‰), `years`, `percent`.
- **level**: `national`, `province`, `prefecture`, `county`, `commune`, `city`, `camp`.
- Always give the verbatim quote (short) or the page/table reference.

## Contributing through Git directly

Fork, add `submissions/<type>/SUB-<year>-<nnnn>/manifest.yaml` following
[`schemas/submission.schema.json`](schemas/submission.schema.json), run `python -m pipeline.validate` and
`python -m pipeline.quality_gate <folder>`, and open a pull request. Changes to models, pipeline or docs are welcome
too; run `python -m pytest -q` and `python -m pipeline.check_model` before opening the PR.

---

## 中文说明

**可以提交什么：** 资料（地方志页面、内部报告、文章、网页存档）、数据（死亡率、人口数、户籍数字、调查表）、
口述证言（请先阅读[口述证言政策](docs/testimony-policy.md)）、研究（论文、估计、再分析、批评）、更正，以及问题。

**怎么提交：** 在 Issues → New issue 中选择对应表单。议题公开可见，请勿填写真实姓名、联系方式或可识别在世私人的信息。

**之后会发生什么：** 机器人先在议题下自动检查 G0–G3 关卡，不通过时会说明原因，修改议题后会重新检查。随后机器人
把议题转成拉取请求（首次贡献者需维护者加上 `submission:triage-ok` 标签后才会创建；证言附件不会被复制进仓库）。
维护者审核（G4）后合并即视为采纳，你的议题随之关闭。之后系统会把你的数字与已有资料对照核算，并在下一个研究周期中
纳入报告；问题类议题会在报告发布后关闭并附上链接。

**数字的写法：** 每行一个数字，依次为“口径 | 数值 | 单位 | 层级 | 地点 | 省 | 时期 | 原文引语或页码”，例如：
`starvation_deaths | 37000 | person | county | 高邮 | 江苏 | 1959-61 | 第85页`。口径请按来源原文选择：
饿死填 `starvation_deaths`，文件中的“非正常死亡”填 `abnormal_deaths`，全部死亡填 `total_deaths`，不要自行换算。
