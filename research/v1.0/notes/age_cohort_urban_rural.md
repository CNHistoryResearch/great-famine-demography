# Who died and who was not born: age, sex, cohort and urban/rural distribution of China's 1958–62 famine losses

Scripts and data for my own calculations are in `models/cohort/` (scripts) and `data/` (inputs):
- `wpp_excess_by_age.py` computes excess deaths by age and sex from UN WPP 2022 single-year estimates (data pulled from github.com/PPgp/wpp2022, `mx1dt.rda` and `popAge1dt.rda`).
- `checks.py` covers the urban/rural split, the Zhihu-claim arithmetic, the Hill 1988 tables and the birth deficit.
- Run either as `python3 -I script.py <cohort/data dir>`.

Abbreviations: CDR = crude death rate; IMR = infant mortality rate; e0 = life expectancy at birth.

## Q1. Age-specific mortality in 1959–61 compared with the 1957 and 1963–64 baselines

### Takeaway
Every reconstruction shows mortality rising at all ages, and the peaks are very high in infancy and early childhood.
- Reconstructed IMR peaked at roughly 200–285 per 1,000.
- Ages 1–4 had the largest proportional rise.
- In absolute numbers, however, the best adult/child decomposition (Hill 1988, part of the Ashton et al. team) attributes about 70–78% of excess deaths to people aged 10+. His survival-ratio analysis also places the adult anomaly mainly at ages ~40+, especially among men.
- Children still died at catastrophic rates. Their absolute excess is held down because far fewer children were born in 1959–61.
- Reconstructed e0 fell to about 31–33 years for 1959–60/1960 in the sources I could verify.
- I could not verify the "~25 in 1960" figure (Ashton et al. 1984) from a primary source in this session.

### Cited Findings
**Hill 1988 (Kenneth Hill, World Bank Discussion Paper 22, Ashton et al. co-author; fiscal years July–June).** Source: [Hill 1988](https://documents1.worldbank.org/curated/en/492811468771874832/pdf/Demographic-Trends-in-China-from-1950-to-1982.pdf)
- Reconstructed indicators by fiscal year. Values are deaths in millions, CDR ‰ and IMR ‰.

| Fiscal year | Deaths (M) | CDR | IMR |
|---|---|---|---|
| 1957–58 | 12.24 | 19.1 | 144 |
| 1958–59 | 15.87 | 24.4 | 236 |
| 1959–60 | 21.37 | 32.8 | 205 |
| 1960–61 | 19.17 | 29.5 | 132 |
| 1961–62 | 13.79 | 21.2 | 236 |
| 1962–63 | 10.07 | 15.1 | 88 |
| 1963–64 | 11.73 | 17.1 | 96 |

  The IMR series is cohort-survival based and erratic. Hill himself flags 1962–63 as implausibly high and 1958–59 and 1961–62 as depressed.
- Deaths under 10 vs. 10+, thousands:

| Fiscal year | Under 10 | 10+ |
|---|---|---|
| 1957–58 | 5,193 | 7,045 |
| 1958–59 | 8,691 | 7,182 |
| 1959–60 | 6,491 | 14,877 |
| 1960–61 | 3,263 | 15,903 |
| 1961–62 | 7,062 | 6,727 |
| 1963–64 | 3,825 | 7,908 |

- Death rate at ages 10+, males: 16.5 (1957–58), 34.1 (1959–60), 36.4 (1960–61), 15.2 (1961–62). Females: 14.4, 29.5, 31.4, 13.1. That is roughly a doubling.
- e0 for males: 45.4 (1957–58), 37.7 (1958–59), 30.7 (1959–60), 35.1 (1960–61), 39.5 (1961–62), 51.5 (1962–63). Female e0 was 47.9 in 1957–58 and 37.0 in 1960–61; the 1959–60 female value is garbled in the scan (~32.3).
- From the 1953–64 intercensal survival ratios, Hill finds a sharp break in survivorship for people aged 35+ in 1953. He attributes it to excess deaths at ages 40+, especially for males, in 1958–62. He suggests rationing that favoured those under ~40 as an explanation.
- Hill's estimate is ~30M excess deaths and ~33M lost or postponed births.
- Registration completeness 1953–64 was ~30% for child deaths and ~80.5% for adult deaths.

**Zhao & Reimondos 2012 (Population 67(2)).** Based on the 1982 and 1988 fertility surveys, six worst-hit provinces (Anhui, Gansu, Guizhou, Henan, Qinghai, Sichuan). Source: [Zhao & Reimondos 2012 (Cairn abstract page)](https://shs.cairn.info/article/E_POPU_1202_0329?lang=en)
- IMR ≈ 120 (1957), ≈160 (1958), >218 (1959), 228 (1960), 156 (1961).
- Probability of dying at ages 1–4 ≈ 110 (1957), rising to ≥176 in 1959–60.
- Survival to age 10 (period): 76% (1957), 67% (1958), 59% (1959), 60% (1960), 73% (1961).
- Conditional e0 for 1960 ≈ 32.5.
- The surveys likely underestimate mortality, because women who died are not interviewed.

**Song 2008 (CCPR working paper).** Source: [Song 2008](https://ccpr.ucla.edu/wp-content/uploads/2024/04/Mortality-Consequences-of-the-1959-1961-Great-Leap-Forward-Famine-in-China_-Debilitation_-Selection_-and-Mortality-Crossovers.pdf)
- In survey cohort data, about 64% of the famine cohort's survival decline happened between ages 0 and 1.
- Famine-cohort mortality exceeded post-famine cohort mortality until ages 11–12.

**Coale's CDR estimates vs. official CDR** (‰). Source: [劉兆崑 2008, 二十一世紀](https://www.cuhk.edu.hk/ics/21c/media/online/0805050.pdf)

| Year | Coale | Official |
|---|---|---|
| 1958 | 20.4 | 11.98 |
| 1959 | 23.3 | 14.59 |
| 1960 | 38.8 | 25.43 |
| 1961 | 20.5 | 14.24 |
| 1962 | 13.7 | 10.02 |
| 1963 | 13.0 | 10.04 |

- Coale estimates that ≥38% of 1953–64 deaths went unregistered.

**My calculation from UN WPP 2022** (model estimates, not independent data). Source: [WPP2022 R data package](https://github.com/PPgp/wpp2022); script `cohort/wpp_excess_by_age.py`
- Death rates per 1,000, both sexes:

| Age group | 1957 | 1960 | 1963 |
|---|---|---|---|
| Age 0 | 121.7 | 229.3 | 105.0 |
| 1–4 | 17.5 | 45.7 | 14.6 |
| 5–14 | 5.8 | 13.1 | 4.5 |
| 15–39 | 5.5 | 9.0 | 4.6 |
| 40–59 | 17.4 | 26.2 | 15.6 |
| 60+ | 83.0 | 109.5 | 75.7 |

- e0 (both sexes): 48.2 (1957), 39.5 (1959), 33.0 (1960), 40.3 (1961), 51.3 (1963).
- Total excess 1958–62 ≈ 18.8M against a log-linear 1957→1964 baseline.
  - By age: under 5 = 48% (age 0: 4.0M; 1–4: 5.0M), 5–14 = 15%, 15–39 = 11%, 40–59 = 12%, 60+ = 15%.
  - Ages 40+ = 27% of the total.

**Hill 1988 Table 8 re-analysed** (my calculation, `checks.py` section E). Source: [Hill 1988](https://documents1.worldbank.org/curated/en/492811468771874832/pdf/Demographic-Trends-in-China-from-1950-to-1982.pdf)
- Fiscal years 1958/59–1961/62 against a flat 1957–58 baseline: excess ≈ 4.7M under 10 and 16.5M at 10+, for a total of 21.2M. Under-10s are 22% of the total.
- Against a linear 1957–58→1963–64 baseline: 7.0M under 10 and 15.1M at 10+, for a total of 22.1M. Under-10s are 32%.

### Inferences
- The age distribution of excess deaths depends heavily on the method.
  - WPP's pattern (about half under 5) looks like a model multiplier applied to all ages. Male mx at age 1 rose 3.3× and age 0 1.9×, compared with 1.6× at age 40 and 1.35× at age 70. It should not be read as evidence about the age pattern.
  - Hill's census-based decomposition shows adults (10+) dominating absolute excess deaths.
- The famine was therefore most lethal *per capita* for infants and young children. In *absolute counts*, adults and the elderly contributed a large share, probably the majority.
- The birth collapse mechanically reduced the number of infants at risk. Hill's under-10 deaths in 1960–61 (3.26M) are actually *below* 1957–58 (5.19M), even though rates were far higher.

### Gaps
- I could not open Ashton et al. 1984 itself, so the frequently quoted e0 of ~24.6 for 1960 and IMR ~284 remain unverified here. Hill 1988 (same team, fiscal years) gives e0 30.7 for males in 1959–60, and Zhao & Reimondos give 32.5 for 1960. Treat "~25" as unconfirmed; it may be a calendar-year figure, as opposed to fiscal-year.
- No age-specific tables found for Coale 1984, Banister 1987, 蒋正华's life tables or the 1957/1963 official life tables.

## Q2. Were males or females more affected?

### Takeaway
Males had higher excess mortality in essentially every reconstruction.
- Excess death rates were about 13–18‰ for males vs. 8.5–13‰ for females across five estimates, so males were about 55–60% of excess deaths.
- The male excess was concentrated among adults 40+.
- Among infants and children aged 1–4, girls in some provinces fared relatively worse, consistent with son preference.
- Famine birth cohorts show depressed sex ratios: the rural 1961 cohort was 100.3 males per 100 females in the 2000 census, against 109.6 for 1958.

### Cited Findings
**Mu & Zhang (IFPRI DP 760).** Source: [Mu & Zhang, IFPRI DP760](https://ageconsearch.umn.edu/record/42331/files/ifpridp00760.pdf)
- Excess mortality of famine vs. normal years, men vs. women (‰):

| Source | Men | Women |
|---|---|---|
| NBS 1994 | 17.38 | 12.47 |
| Coale 1984 | 13.77 | 9.04 |
| Banister 1984 | 13.18 | 8.49 |
| Calot 1985 | 13.95 | 9.22 |
| Jiang 1986 | 18.11 | 13.25 |

- Their conclusion: "during the famine period, women have lower age-specific mortality rates than do men".
- Rural sex ratios by birth year in the 2000 census: 1957: 108.78; 1958: 109.59; 1959: 108.48; 1960: 105.35; 1961: 100.30; 1962: 103.88; 1963: 104.44.
- Provinces with higher excess mortality had larger sex-ratio drops (coefficient −0.0138, t = −2.13, 28 provinces).
- They attribute about 68–71% of the gender gap in long-run famine effects to mortality selection.

**Hill 1988.** Source: [Hill 1988](https://documents1.worldbank.org/curated/en/492811468771874832/pdf/Demographic-Trends-in-China-from-1950-to-1982.pdf)
- The 10+ death rate rose from 16.5 to 36.4 for males and from 14.4 to 31.4 for females.
- The 1953–64 survival-ratio break at ages 35+ is "especially for males".

**Zhao & Reimondos 2012.** Source: [Zhao & Reimondos 2012](https://shs.cairn.info/article/E_POPU_1202_0329?lang=en)
- The male/female infant mortality ratio fell to near 1 in 1958 and below 1 in 1960–61.
- Girls aged 1–4 had higher mortality than boys in most years; the authors attribute this to son preference.

**My calculation from WPP 2022** (model-based). Source: [WPP2022](https://github.com/PPgp/wpp2022)
- Males account for 52% of excess deaths in 1958–62 (9.8M M vs. 9.0M F).

### Inferences
- Using the Mu & Zhang table, the male share of excess deaths is ≈ 58–61% for Coale, Banister and Calot, and ≈ 57–58% for NBS and Jiang. This assumes near-equal population sizes by sex; it is my arithmetic.
- This matches the general famine-demography finding that males are more vulnerable. Mu & Zhang cite Sen on Bengal 1943: 56% male, 44% female.

### Gaps
- I did not obtain 1964 or 1982 census sex ratios by age, which would show the adult-male deficit directly. The sex ratio for the 1964 cohorts aged 40–60 should be checked in 中国1964年人口普查资料 or 中国人口统计年鉴.

## Q3. Cohort evidence: lost births, the 1962–63 rebound, and famine-cohort research

### Takeaway
The birth deficit was large and comparable in size to the excess deaths.
- Hill/Ashton reconstruct births falling from 25.8M (FY1957–58) to 14.7M (FY1960–61), a TFR of 6.07→3.39. Births then rebounded to 33.8M in FY1962–63 (TFR 7.55).
- My arithmetic gives about 22–28M births lost in FY1958/59–1961/62, of which about 11–14M were "recovered" in the 1962–64 rebound. Hill's own figure is ~33M lost or postponed.
- In the 1990 census, rural (agricultural-hukou) county cohorts born in 1959–61 are only ~72% the size of the 1954–57 cohorts, compared with ~85% for non-agricultural cohorts.

### Cited Findings
**Hill 1988 Table 2.** Source: [Hill 1988](https://documents1.worldbank.org/curated/en/492811468771874832/pdf/Demographic-Trends-in-China-from-1950-to-1982.pdf)

| Fiscal year | Births (M) | CBR (‰) | TFR |
|---|---|---|---|
| 1957–58 | 25.80 | 40.3 | 6.07 |
| 1958–59 | 22.11 | 34.0 | 5.17 |
| 1959–60 | 18.88 | 28.9 | 4.38 |
| 1960–61 | 14.72 | 22.7 | 3.39 |
| 1961–62 | 20.88 | 32.1 | 4.71 |
| 1962–63 | 33.81 | 50.8 | 7.55 |
| 1963–64 | 30.71 | 44.7 | 6.82 |

- Birth registration was only about 80–87% complete.

**Official registered birth rates** (‰): 34.0 (1957), 29.2 (1958), 24.8 (1959), 20.9 (1960), 18.0 (1961), 37.0 (1962), 43.4 (1963), 39.1 (1964). Source: [Hill 1988 Table 1](https://documents1.worldbank.org/curated/en/492811468771874832/pdf/Demographic-Trends-in-China-from-1950-to-1982.pdf); [Ashton et al. appendix via Manning](https://scottmanning.com/content/visualizing-the-great-leap-forward/)

**Other birth-deficit estimates:**
- Coale: 30.68M fewer births. Banister: 31.2M. Hill: 33M. Source: [IUSSP paper on population change during the famine](https://iussp.org/sites/default/files/event_call_for_papers/A%20study%20of%20population%20change%20led%20by%20China%E2%80%99s%20great%20famine_.pdf)
- Yang Jisheng recomputes ~32–40M lost births alongside ~36M deaths. Source: [Yang Jisheng, Tombstone ch.23](https://books.xijinping.one/tombstone/ch23)
- Zhao & Reimondos cite a range of 15–30M and find fertility and marriage fell everywhere. Source: [Zhao & Reimondos 2012](https://shs.cairn.info/article/E_POPU_1202_0329?lang=en)

**Meng, Qian & Yared** (1990 census, county level, cohort size as famine-severity proxy). Source: [Meng, Qian & Yared](https://eml.berkeley.edu/~webfac/bardhan/qian.pdf)
- Agricultural-hukou famine cohort (born 1959–61) averages ~3,301 per county, vs. ~4,968 for 1954–57 cohorts, a ratio of ≈0.72. The ratio is ≈0.85 for non-agricultural cohorts.
- The 1960 agricultural cohort is on average 34% smaller than earlier cohorts.
- Beijing, Shanghai and Tianjin show no mortality change.

**Shanghai** births fell from 45.6‰ (1957) to 22.4‰ (1961) with almost no rise in deaths (6.0→7.7‰). That is about 140,000 "missing" births, with few starvation deaths. Source: [Yang Jisheng, Tombstone ch.23](https://books.xijinping.one/tombstone/ch23)

**My calculation.** Sources: [Hill 1988](https://documents1.worldbank.org/curated/en/492811468771874832/pdf/Demographic-Trends-in-China-from-1950-to-1982.pdf); [WPP2022](https://github.com/PPgp/wpp2022)
- Using Hill births with a baseline CBR of 40.3‰: lost births in FY58/59–61/62 = 28.1M, rebound surplus FY62/63–63/64 = 10.9M, net 17.2M.
- With a baseline CBR of 38‰: 22.1M lost, 13.9M rebound, net 8.2M.
- WPP age-0 population (millions): 24.9 (1957), 18.2 (1959), 16.8 (1960), 15.3 (1961), 25.1 (1962), 31.3 (1963). That implies a 1959–61 shortfall of ≈24.4M relative to the 1957 level.

### Inferences
- The holes in the age pyramids at ages ~20–23 in 1982 and ~2–5 in 1964 are mainly births that never happened, plus deaths of infants born in the famine.
- Cohort-size studies such as Meng-Qian-Yared and Chen & Zhou necessarily mix lost births with infant and child deaths. They should not be read as excess-death counts.
- The 1962–63 rebound recovered perhaps a third to a half of the lost births.

### Gaps
- I could not retrieve the province-level cohort-shortfall figures in Chen & Zhou 2007 (J. Health Econ.) or Almond et al.
- I did not obtain exact 1964/1982/1990/2000 census counts by single year of birth.

## Q4. Urban vs. rural (市 vs 县; non-agricultural vs agricultural hukou)

### Takeaway
Official statistics show a rural death-rate spike far larger than the urban one.
- In 1960, rural (县) CDR was 28.58‰ vs. 13.77‰ in cities (市). That is 2.58× the 1957 level for rural areas vs. 1.63× for cities.
- On official data, about 91% of 1958–61 excess deaths were rural; I computed this myself.
- Grain rations protected hukou-holding urban residents. The 1961–63 downsizing then moved ~26M urban residents (including over 18M laid-off workers) back to villages, mostly after the 1960 mortality peak.

### Cited Findings
**Official city/county death rates** (‰; SSB Statistical Yearbook 1991, pp.79–80). Source: [Lin & Yang 2000, Economic Journal](https://gwern.net/doc/sociology/2000-lin.pdf)

| Year | National | City (市) | Rural (县) | City share of population |
|---|---|---|---|---|
| 1957 | 10.80 | 8.47 | 11.07 | 15.4% |
| 1958 | 11.98 | 9.22 | 12.50 | 16.2% |
| 1959 | 14.59 | 10.92 | 14.61 | 18.4% |
| 1960 | 25.43 | 13.77 | 28.58 | 19.7% |
| 1961 | 14.24 | 11.39 | 14.58 | 19.3% |
| 1962 | 10.02 | 8.28 | 10.32 | 17.3% |
| 1963 | 10.04 | 7.13 | 10.49 | 16.8% |

**Urban grain entitlements:**
- 1956 urban monthly grain rations: 25 kg for very heavy labourers, 14 kg for white-collar workers.
- Lin & Yang argue urban residents had legal entitlements while peasants got the residual after procurement. They find the rural population share raised provincial death rates.
- Source: [Lin & Yang 2000](https://gwern.net/doc/sociology/2000-lin.pdf)

**Urban downsizing, 1961–63:** over 18M workers cut and over 26M urban residents returned to villages. Urban population fell by 13M in 1961 and nearly 12M in 1962; the May 1962 target was a 20M reduction. Source: [aisixiang 82837](https://www.aisixiang.com/data/82837.html)

**Anhui (Cao Shuji's gazetteer data):** urban death rate rose 260%, rural death rate almost eightfold. Source: [Ó Gráda, UCD WP11/03](https://www.ucd.ie/economics/t4media/WP11_03.pdf)

**Children:** rural children had ~1.9× the odds of dying at ages 0–2 compared with urban children, and urban child mortality was roughly stable. Source: [Zhao & Reimondos 2012](https://shs.cairn.info/article/E_POPU_1202_0329?lang=en)

**Jin Hui (金辉):** argues the national totals mask rural deaths and estimates rural abnormal deaths up to ~34.7M. Source: [Yang Jisheng, Tombstone ch.23](https://books.xijinping.one/tombstone/ch23)

**My calculation** (`checks.py` section A). Source: [Lin & Yang 2000](https://gwern.net/doc/sociology/2000-lin.pdf)
- Inputs: official population × city share, with baseline = mean of 1957 and 1962 rates.
- Official-data excess deaths 1958–61: 1.49M urban vs. 14.72M rural, so the rural share is 90.8%.
- In 1960, rural areas accounted for 89% of all deaths.

### Inferences
- The 市/县 split understates the rural share of hukou-based exposure: 县 includes county towns, and 市 includes suburban agricultural populations.
- The official totals undercount deaths by perhaps 40–50%, and the undercount was likely concentrated in rural areas.
- Taken together, the rural/agricultural-hukou share of excess deaths was probably ≥90%.
- The 1961–63 transfer of ~26M people to villages came after peak mortality, so it mainly shifted the burden of food deficits back onto rural areas.

### Gaps
- The 1983 Statistical Yearbook printing of this series was not directly verified; Lin & Yang cite the 1991 yearbook.
- I found no hukou-specific excess-death estimate in an academic source; the ~91% figure is my own derivation.

## Q5. Evaluating the Zhihu post's claims

### Takeaway
- **Claim 1** (29.57M "gap" at ages 40+ in the 1964 census, little child excess, negligible "少生"): partly right in direction, wrong in magnitude and interpretation.
- **Claim 2** ("7× mortality at 40+"): an arithmetic artefact.
- **Claim 3** (the specific life-table q40 values): unverifiable; the 1957 value is about half the UN WPP 2022 estimate for 40-year-old men in 1957.

### Cited Findings and my checks
**Claim 1, adult concentration.** There is genuine support that adults, especially men 40+, bore large excess mortality.
- Hill 1988 finds a survivorship break at ages 35+ in 1953, implying excess deaths at 40+ in 1958–62, especially males, and attributes about 70–78% of excess deaths to ages 10+. [Hill 1988](https://documents1.worldbank.org/curated/en/492811468771874832/pdf/Demographic-Trends-in-China-from-1950-to-1982.pdf)

**Claim 1, the 29.57M gap is inflated by death under-registration.** The counterfactual applies registered life tables to the 1953 census, but adult death registration was only ~80% complete [Hill 1988](https://documents1.worldbank.org/curated/en/492811468771874832/pdf/Demographic-Trends-in-China-from-1950-to-1982.pdf), and Coale estimates ≥38% of all deaths unregistered [劉兆崑 2008](https://www.cuhk.edu.hk/ics/21c/media/online/0805050.pdf).
- My calculation (`checks.py` section D): the cohorts aged 40+ in 1964 would suffer ~64M normal deaths in 1953–64 at WPP non-famine rates.
- 20% under-registration alone would inflate the "gap" by ~12.5M; 30% would inflate it by ~19M.
- So perhaps 40–80% of the 29.57M could be artefact. The 1953 census also had known age-exaggeration problems at older ages.

**Claim 1, "少生" negligible.** This is contradicted by every source.
- Registered CBR fell from 34‰ to 18‰.
- Reconstructed births fell by ~11M a year at the trough.
- The 1990-census agricultural famine cohorts are 28% smaller than earlier cohorts [Meng-Qian-Yared](https://eml.berkeley.edu/~webfac/bardhan/qian.pdf).
- Shanghai lost ~140k births with almost no excess deaths [Tombstone ch.23](https://books.xijinping.one/tombstone/ch23).
- The post's own 1982 chart shows the hole at ages 20–22.
- The post's finding that the 1964 under-10 population *exceeds* its counterfactual is itself evidence that registered births were incomplete (Hill: ~80–87% complete). Infants who were born and died unregistered cannot appear in that comparison at all, so the method is blind to child excess deaths by construction.

**Claim 2, "7×".** WPP 2022 puts the 1960 population aged 40+ at 153.9M, 23.5% of the total.
- If all 30M excess deaths over 3 years fell on the 40+ group, that is +10M a year.
- Against the WPP 1957 age-specific baseline (40+ death rate 36.0‰, ≈5.5M deaths a year), the multiplier is **2.8×**, not 7×.
- Even using the post's own 7M normal deaths a year, with the 45% share of deaths at 40+ implied by WPP, gives **4.2×**.
- The 7× figure is reproduced *exactly* by applying the flat national CDR of ~10.8‰ to the 40+ population: 7M × 0.235 = 1.65M, and (1.65 + 10)/1.65 = 7.1. This mistakes the population share for the death share; deaths are concentrated at old ages.
- If 7× were actually applied to every 40+ age-specific rate for 3 years (WPP 1957 base), the implied excess at 40+ alone would be ~58M, with 45% of 70-year-olds dying each year. That is inconsistent with any total estimate.
- The "4 → 30 per 1,000 forty-year-olds" framing uses a single age (age 40), while most deaths at 40+ occur at much older ages.
- Source for all of the above: [WPP2022](https://github.com/PPgp/wpp2022); my calculation in `checks.py` section B.

**Claim 3, life-table values.** The post gives male q40 of 5.47‰ (1957), 3.42‰ (1963) and 2.53‰ (1981).
- WPP 2022 male one-year q40 is 10.3‰ (1957), 8.7‰ (1963) and 4.3‰ (1981) [WPP2022](https://github.com/PPgp/wpp2022).
- The post's values are 40–60% lower, consistent with registration-based official tables understating adult mortality.
- I could not locate the original 1957/1963 official life tables to confirm the post's numbers.

### Inferences
- **Defensible version of the post's thesis:** a large share, probably the majority, of excess *deaths* were adolescents and adults, with a male, middle-aged and elderly tilt. This is Hill's finding.
- **Not defensible:**
  - that "少生" was negligible: it was comparable in size to the excess deaths, ~22–33M gross;
  - that a 1964-census gap at 40+ measures excess deaths directly;
  - that the 30M total is an *under*estimate on these grounds;
  - the 7× arithmetic.

### Gaps
- The post's underlying single-year 1953 and 1964 census tabulations and its life tables were not obtained, so I could not replicate the 29.57M figure directly.
- The WPP-based age shares are model-driven and should not be cited as empirical evidence on the age pattern.
