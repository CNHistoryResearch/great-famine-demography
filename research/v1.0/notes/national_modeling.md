# National excess-death modeling: China's Great Leap Forward famine (三年困难时期), 1958–62

All paths in these notes are under `models/national/` (scripts, results) and `data/national/` (inputs).
- Scripts: `build_data.py` (makes the input CSVs), `famine_model.py` (Models A–D, sensitivity), `charts_and_mc.py` (charts and Monte Carlo). Run with `python3 -I <script>`. Each run takes about 15 s.
- Data (each CSV has a `source` column): `data/official_nbs_vitals_1949_1970.csv`, `data/official_nbs_vitals_1971_1982.csv`, `data/official_urban_rural_cdr.csv`, `data/census_totals.csv`, `data/census_age_single_year_1953_1964_1982.csv`, `data/hill1988_reconstruction_fy1953_1964.csv`, `data/wpp2024_china_annual_1950_1985.csv`, `data/wpp2022_china_annual_1950_1985.csv`, `data/wpp2024_china_mx_single_age_1950_1985.csv`, `data/wpp2024_china_pop_single_age_1949_1985.csv`, `data/literature_estimates.csv`
- Results: `results/01_official_consistency.csv` … `results/11_monte_carlo_summary.json`, plus `results/summary.json`
- Charts: `charts/01_cdr_official_vs_modeled.png`, `charts/02_intercensal_accounting.png`, `charts/03_sensitivity_tornado.png`, `charts/04_age_structure_1964.png`, `charts/05_births.png`

**Headline result.** Our central estimate is **≈31 million excess deaths** between mid-1958 and mid-1962/63. That number comes from a census-calibrated cohort-component reconstruction from 1953 to 1964. It splits into 20.2M deaths among people already alive at the 1953 census and 10.7M among children born after it.
- **Range.** A defensible range is **≈22–40M**: the 25–75% Monte Carlo interval is 26–38M, the 5–95% interval is 15–47M, and the median is 32M.
- **Lost or postponed births.** ≈36M gross for mid-1958 to mid-1962. After the 1962–63 rebound the net figure is ≈28M.
- **What drives the range.** Four things: (1) how complete the 1953 census was relative to the 1964 census; (2) the level of "normal" (no-famine) mortality; (3) how far child mortality rose during the famine; (4) which 1953 total is used. Registered (official) deaths alone give only 14–16M excess. That figure is a floor, because registered deaths cover only about 60% of the deaths implied by the censuses.

---

## Q1. Input data, sources, and verification of the Zhihu official table

### Takeaway
The year-end totals, CBR and natural-increase figures in the Zhihu table match the official series in the *Statistical Yearbook of China 1983*, as reproduced by Hill (1988). The NBS 1999 yearbook also agrees for 1957, 1962 and 1965. Several printed CDRs in the screenshot are off by 0.02–0.08‰, and the 1962 and 1963 CDRs are swapped. We use CDR = CBR − NIR, which agrees with the yearbook values. Single-year census age distributions for 1953, 1964 and 1982 were obtained, cleaned and saved.

### Cited Findings
- Hill (1988), World Bank Discussion Paper 22, Table 1 reproduces the official series from the *State Statistical Yearbook 1983*. Population (M): 1958 659.9, 1959 672.1, 1960 662.1, 1961 658.6. CBR/CDR 1959 24.8/14.6, 1960 20.9/25.4 (NIR −4.6), 1961 18.0/14.2, 1962 37.0/10.0, 1963 43.4/10.0, 1964 39.1/11.5. Census totals: 582.6M (1953), 694.6M (1964), 1008.2M (1982). — [Hill 1988, World Bank](https://documents1.worldbank.org/curated/en/492811468771874832/pdf/Demographic-Trends-in-China-from-1950-to-1982.pdf)
- NBS yearbook Table 4-2 (urban 市 / county 县 split): 1957 CBR 34.03, CDR 10.80 (市 8.47, 县 11.07); 1962 CBR 37.01, CDR 10.02 (市 8.28, 县 10.32); 1965 CDR 9.50 (市 5.69, 县 10.06). The page does not show the famine years 1958–61. — [NBS 1999 yearbook](https://www.stats.gov.cn/yearbook/1999/d02c.htm)
- **Discrepancies in the screenshot**, checked against a 2× zoom of the image and against CBR − NIR:
  - CDR 1956 printed 11.48; CBR − NIR gives 11.40.
  - 1958 printed 11.9; should be 11.98.
  - 1959 printed 14.58; should be 14.59.
  - 1960 printed 25.49; should be 25.43.
  - 1961 printed 14.23; should be 14.24.
  - 1962 printed 10.04 and 1963 printed 10.02; these are swapped (NBS 1999 gives 10.02 for 1962).
  - 1964 printed 11.54; should be 11.50.
  - Year-end totals, CBR and NIR agree with Hill's SYB1983 table to rounding.
  - Source files: the table reproduced in the chenqin Zhihu answer (archived: see data/registry/archive_snapshots.yaml, ARC-ZHIHU-CHENQIN) and `data/official_nbs_vitals_1949_1970.csv` (both CDR columns kept).
- 1964 census (reference time 30 June 1964, 24:00): 28 provinces plus military = 694,581,759 (male 356,517,011, female 338,064,748). Grand total including Taiwan, Hong Kong/Macau and overseas Chinese = 723,070,269. — [NBS 1964 census communiqué](https://www.stats.gov.cn/sj/tjgb/rkpcgb/qgrkpcgb/202302/t20230206_1901987.html)
- NBS's census summary table gives 59,435万 for 1953, 69,458万 for 1964 and 100,818万 for 1982. Its note says the 1953 total includes the indirectly surveyed population, and that census totals include military personnel. — [NBS yearbook 2005 Table 4-4](https://www.stats.gov.cn/sj/ndsj/2005/html/D0404e.htm)
- The 1953 mainland total of 582,603,417 is given in [Wikipedia: 1964 Chinese census](https://en.wikipedia.org/wiki/1964_Chinese_census) and matches Hill's 582.6M.
  - Our inference: NBS's 594.35M equals 601.94M (grand total) minus 7.59M (Taiwan). It therefore still includes about 11.74M overseas Chinese and students. The split 574.2M direct + 8.4M indirect + 7.59M Taiwan + 11.74M overseas is the standard communiqué breakdown, but we did not re-fetch it in this session.
- Single-year age distributions (percent of the age-classified total) come from an IDE-JETRO compilation. The age-classified totals are 1953: 567,446,758; 1964: 694,581,759; 1982: 1,003,913,927. — [IDE-JETRO TSS009400_007](https://ir.ide.go.jp/record/44763/files/TSS009400_007.pdf)
  - **Data fix.** In the 1953 table, the male share at age 36 is printed as 1.471511%. With that value the male column sums to 52.25%, against a published male share of 51.45%. We replaced it with 0.678511%, which makes the sums consistent. The fix is flagged in the CSV.
- Hill also notes that the 1953 census total includes persons not classified by age, which he assumes are the missing young adult males. He reports that the 1982 age distribution excludes the institutional (military) population. — [Hill 1988](https://documents1.worldbank.org/curated/en/492811468771874832/pdf/Demographic-Trends-in-China-from-1950-to-1982.pdf)
- **Retrospective births.** We could not obtain Coale & Chen (1987). As a substitute we use Hill's (1988) Table 2 births for mid-year 1953–64, which are built from the 1982 One-per-Thousand fertility survey adjusted for lunar-calendar misreporting.
  - Births (M) for 1953-54 … 1963-64: 26.08, 27.31, 24.82, 25.54, 25.80, 22.11, 18.88, 14.72, 20.88, 33.81, 30.71. Total 270.66M.
  - Hill's implied intercensal deaths are 156.875M. — [Hill 1988](https://documents1.worldbank.org/curated/en/492811468771874832/pdf/Demographic-Trends-in-China-from-1950-to-1982.pdf)
- UN WPP2024 and WPP2022 annual births, deaths, CBR, CDR, single-age mx and population for China were read from the R data packages. — [github.com/PPgp/wpp2024](https://github.com/PPgp/wpp2024), [github.com/PPgp/wpp2022](https://github.com/PPgp/wpp2022)

### Inferences
- The official series is internally consistent in its *rates* (CBR − CDR = NIR). The errors in the screenshot are transcription or web-copy typos, not evidence of manipulation.
- For any accounting, the correct 1953 base is 582.6M (mainland, direct + indirect). Using NBS's 594.35M silently adds about 11.7M overseas Chinese and inflates the excess by about 11M (see Q3).

### Gaps
- Coale & Chen (1987) provincial birth tables: not obtained.
- Coale (1984) appendix tables: the NAP online reader failed to load.
- Official 1957 and 1963 life tables: not found online.
- Official 市/县 CDR for 1958–61: not verified. The commonly quoted 1960 values (市 ≈13.8, 县 ≈28.6) could not be confirmed this session.
- Whether the 1953 figure of 582.6M includes the military: not verified. It makes ≤1% difference in the base (see Q4).

---

## Q2. Internal consistency of the official data (the 10M drop in 1960; intercensal closure)

### Takeaway
The year-end totals do not follow from the stated natural increase. The 1960 total fell by 10.00M, but registered natural increase explains only −3.05M, leaving a −6.95M residual; 1961 adds another −5.98M. Over 1953–64 the registered births minus deaths overshoot the 1964 census by 17.2M. With survey-corrected births the shortfall in registered deaths becomes about 64–68M.

Hukou double registration can shift population *between years*, but it cannot produce a net loss over a full cycle. It also does not touch census-to-census estimates. The residual is therefore best explained mainly by unregistered deaths.

### Cited Findings (computed here from the official series in Q1 — `results/01_official_consistency.csv`, `results/02_intercensal_accounting_official.csv`)

**Residual = ΔP(year-end) − (CBR−CDR) × mid-year population**

| Period | Residual (M) |
|---|---|
| 1954–57 | +3.90 |
| 1958 | +2.15 |
| 1959 | +5.34 |
| 1960 | **−6.95** (ΔP −10.00 vs natural increase −3.05) |
| 1961 | **−5.98** (ΔP −3.48 vs natural increase +2.50) |
| 1962–64 | −13.61 |
| 1965–70 | +2.98 |
| **Net 1954–64** | **−15.15** |

**Official series vs censuses**
- Mid-1953 interpolated: 581.4 (census 582.6).
- Mid-1964 interpolated: 698.4 (census 694.6; hukou series 3.8M or 0.5% *above* the census).
- Mid-1982 interpolated: 1008.05 (census 1008.18).

**Intercensal closure, mid-1953 → mid-1964** (official births 224.0M, registered deaths 94.8M)
- Predicted 1964 population: 711.8M against the census 694.6M, an error of +17.2M (+2.5%).
- Deaths implied with official births: 112.0M, i.e. 1.18 × registered deaths.
- With Hill's survey births (270.7M), implied deaths are 158.7M, so registered deaths are only about 60% complete.

**Control period, mid-1964 → mid-1982** (official rates)
- Predicted 1982 population: 992.7M against the census 1008.2M (−15.4M, −1.5%). This points to under-registered births, or under-counting in the 1964 census, rather than missing deaths.

**Competing explanation (孙经先)**
- Sun Jingxian (2016) attributes the "anomalous" change in hukou totals to duplicate migration registrations, cancelled duplicates, unrecorded migrations and retroactive registrations. He argues that unreported deaths do not affect these figures. — [Sun 2016, CCPS 2(1)](https://rpb115.nsysu.edu.tw/var/file/131/1131/img/2375/CCPS2(1)-Sun.pdf)
- The text we retrieved was corrupted, so his numerical estimates could not be read.
- Cao Shuji notes that official population totals run 400–700万 above the totals implied by growth rates, and that NBS death rates yield only about 15M excess deaths. — [Cao Shuji 2005 via CDT](https://chinadigitaltimes.net/chinese/?p=98017)

### Inferences
- **What double registration can and cannot explain.**
  - The pattern fits double registration in part: a positive residual in 1958–59 (+7.5M, during the urban hiring boom, when the official urban population rose 24.2M between end-1957 and end-1959 and 31.2M by end-1960), followed by negative residuals in 1960–64.
  - But pure double counting nets to zero once it is cancelled. The net residual over 1954–64 is −15.2M, so at least that much must be unrecorded loss: deaths, or births that were registered and never existed, which is implausible.
  - Survey and census evidence shows births were *under*-registered by about 46–51M over 1953–64. The missing registered deaths are therefore far larger than 15M.
  - The census-based estimates below never use the year-end hukou series. Duplicates that survived into the 1964 census would *inflate* the 1964 count and so bias our estimate *down*, not up.
- **Where the 10M drop comes from.** The 1960 fall of exactly 1,000万 is real arithmetic: 67,207 − 66,207. It mixes a registered natural decrease of about 3M with about 7M of register adjustments or unregistered losses. Citing it as "10M deaths" is wrong. So is dismissing the famine because of it.
- **Births under-registration.** Registered births sit 2–9‰ of CBR (roughly 2–7M births per year) below survey or census-based births in every FY from 1953 to 1963 (chart `05_births.png`). The Zhihu post's claim that "births did not really fall" confuses birth under-registration with the absence of a birth decline. Survey births (Hill) and our 1982 back-projection both show births falling from about 27M to about 15M in mid-1960 to mid-1961.

### Gaps
- Sun's numerical decomposition: PDF text corrupted. Yearly hukou migration and cancellation counts were not obtained.

---

## Q3. Model results (A crude-rate, B intercensal balancing, C cohort-component and back-projection, D UN WPP)

### Takeaway
- **Model A (registered deaths):** 14–16M (1958–61). This is a floor.
- **Model B (intercensal balancing):** 31–35M with survey or census-based births. With official births it gives a nonsensical −8M, which proves official births are too low.
- **Model C (census-calibrated cohort-component):** **30.9M** (mid-1958 to mid-1963), of which 20.2M were among cohorts alive in 1953.
- **Model D (UN WPP2024):** 15.7–18M. That figure results from WPP implicitly treating the 1964 census as about 2.7% under-counted relative to 1953. Our model reproduces it (15.8M) when given the same assumption.

### Methods (short)
- **Time unit.** All models run mid-year to mid-year ("FY t" = 1 July t to 30 June t+1), because the censuses are mid-year (1953-06-30 24:00, 1964-06-30 24:00, 1982-07-01).
- **Model A.** Excess = Σ(CDR_t − baseline_t) × mid-year population. Applied to NBS, WPP2024, WPP2022 and Hill's FY series. Baselines:
  - B1: 1957 level, held flat.
  - B2: mean of 1956–57.
  - B3: linear from 1957 to 1963.
  - B4: OLS trend fitted on 1954–57 and 1963–65.
  - B5: mean of 1957 and 1963–64.
- **Model C (central).**
  - *Projection.* Single-year, two-sex cohort-component projection from the 1953 census to the 1964 census.
  - *Starting population.* Variant "V2": the 1953 age-classified 567.4M, plus 6.76M unclassified directly enumerated persons assigned to males aged 18–35 (army and missing young men, following Hill), then scaled up by the indirect 8.40M to reach 582.6M.
  - *Normal (no-famine) mortality m\*.* UN WPP2024 single-age mx, log-linearly interpolated between the 1957 and 1963 anchors (female e0 50.4 → 53.9).
  - *Actual mortality.* m = m\*·(1 + k·f), where f is WPP2024's own proportional famine excess by age and year (the timing and age shape), and k is a scalar.
    - k_adult is solved by bisection so that cohorts alive in 1953 reproduce the 1964 census population at ages 11+ exactly. Result: k_adult = 2.58. WPP's own famine excess (k = 1) leaves 10.1M too many survivors.
    - k_child is set to 1 (the WPP shape). With Hill's independent survey births, calibrating k_child to the 1964 census ages 0–10 gives k_child = 1.05. That independently supports the WPP child-mortality shape.
  - *Births.* Own back-projection of the 1982 census, ages 18–28, with the 4.26M military allocated to males aged 18–30, survived backward under the calibrated mortality.
  - *Excess.* Actual deaths minus deaths expected for the actual population under m\*, summed for FY1958–62.
- **Lost births.** Counterfactual CBR equal to the FY1954–57 mean (alternative: a linear path to FY1964–65) minus own births.
- **Model D.** WPP2024 and WPP2022 deaths run through the Model A baselines.

### Results tables

**Model A — crude-rate excess (millions).** Source: `results/03_modelA_crude_rate_excess.csv`

| CDR series | B1 1957 flat | B2 1956–57 | B3 lin 57→63 | B4 OLS trend | B5 57&63–64 |
|---|---|---|---|---|---|
| Official NBS, 1958–61 | 15.33 | 14.53 | 16.17 | 14.35 | 15.38 |
| Official NBS, 1959–61 | 14.55 | 13.96 | 15.31 | 14.03 | 14.59 |
| UN WPP2024, 1958–61 | 12.51 | 11.97 | 15.74 | 15.73 | 18.15 |
| UN WPP2022, 1958–61 | 12.63 | 12.09 | 15.73 | 15.81 | 18.10 |
| Hill 1988 FY, FY1958–61 | 20.50 | – | 25.70 (lin FY57→FY62) | 23.34 | – |

**Model B — intercensal balancing, mid-1953 → mid-1964 (millions; P1953 = 582.6, P1964 = 694.58).** Source: `results/08_modelB_intercensal_balancing.csv`. The last column uses the NBS 1953 total of 594.35 instead.

| Birth series | Births | Implied deaths | Registered deaths | Normal deaths (model) | Excess = implied − normal | Excess if P1953 = 594.35 |
|---|---|---|---|---|---|---|
| Official registered | 224.0 | 112.0 | 94.8 | 120.3 | −8.3 (impossible) | 2.6 |
| Hill 1988 (1982 fertility survey) | 270.7 | 158.7 | 94.8 | 127.5 | **31.2** | 42.1 |
| Own: 1982 census back-projection | 275.1 | 163.1 | 94.8 | 128.3 | **34.9*** | 45.8 |
| Own: 1964 census back-projection | 270.1 | 158.1 | 94.8 | 127.4 | **30.7** | 41.5 |

\*The 1982-based births leave 3.9M more children in 1964 than the 1964 census counted. Almost all of this comes from allocating the 1982 military to these cohorts; without that allocation the residual is 0.09M. The cohort-component estimate on the same births is 30.9M.

**Model C — central census-calibrated reconstruction, by FY (millions).** Sources: `results/04_central_cc_by_fy.csv`, `results/10_model_annual_fy.csv`

| FY | Births | Deaths | Expected (normal) | Excess | of which, alive in 1953 | of which, born after | Model CDR ‰ | Normal CDR ‰ | Model CBR ‰ |
|---|---|---|---|---|---|---|---|---|---|
| 1957-58 | 27.74 | 12.56 | 12.50 | 0.06 | 0.06 | 0.00 | 19.5 | 19.4 | 43.0 |
| 1958-59 | 21.16 | 16.07 | 11.97 | 4.10 | 2.64 | 1.46 | 24.5 | 18.2 | 32.3 |
| 1959-60 | 21.17 | 22.78 | 11.32 | **11.45** | 7.37 | 4.08 | 34.7 | 17.2 | 32.3 |
| 1960-61 | 14.81 | 21.46 | 10.30 | **11.16** | 7.38 | 3.78 | 32.9 | 16.1 | 22.7 |
| 1961-62 | 20.16 | 13.96 | 9.86 | 4.09 | 2.74 | 1.35 | 21.4 | 15.7 | 30.9 |
| 1962-63 | 34.31 | 10.96 | 10.84 | 0.12 | 0.11 | 0.01 | 16.4 | 16.8 | 51.5 |
| **Total FY58–62** | | | | **30.93** | **20.24** | **10.68** | | | |

- Mid-1958 to mid-1962: 30.81M.
- Rough calendar-year split, assuming deaths are spread evenly within each FY: 1958 ≈ 2.1M, 1959 ≈ 7.8M, 1960 ≈ 11.3M, 1961 ≈ 7.6M, 1962 ≈ 2.1M. This timing is inherited from WPP's age and year shape, so treat it as indicative only.
- Total deaths mid-1953 to mid-1964: 159.3M, against 94.8M registered (registration completeness about 60%).

**Lost births.** Source: `results/07_lost_births.csv`

| Counterfactual | Gross deficit FY1958–61 | Net deficit FY1958–63 (after the 1962–63 rebound) |
|---|---|---|
| Flat pre-famine CBR (FY1954–57 mean ≈ 43.1‰) | 35.8M | 28.4M |
| Linear FY1957 → FY1964–65 | 35.4M | 27.6M |

- Population deficit = excess deaths + lost births: about **67M gross**, or about 59M net of the rebound.

**Model C — Zhihu test: the "40+ gap in 1964".** The 1953 population is projected forward with no births and compared with the 1964 census at ages 40+, which is 158.94M. Source: `results/05_zhihu_40plus_gap.csv`

| 1953 base / normal mortality | Female e0 under normal mortality, 1957 → 1963 | Projected 40+ | Gap |
|---|---|---|---|
| 582.6, proportional (V1), WPP normal | 50.4 → 53.9 | 171.9 | **13.0** |
| V2 (missing males), WPP normal | 50.4 → 53.9 | 172.0 | 13.1 |
| 567.4 age-classified only (V3) | 50.4 → 53.9 | 167.4 | 8.5 |
| 594.35 NBS (V4) | 50.4 → 53.9 | 175.4 | 16.4 |
| V1, normal mx × 0.85 | 53.9 → 57.1 | 178.7 | 19.8 |
| V1, normal mx × 0.70 | 57.9 → 60.9 | 186.2 | 27.3 |
| V1, normal mx × 0.55 | 62.7 → 65.4 | 194.5 | 35.5 |
| V1, WPP2024 *actual* mx (incl. famine) | – | 167.5 | 8.6 |

- Gap by 1964 age band (V2, WPP normal mortality), in millions: 11–19: 1.4; 20–29: 1.4; 30–39: 1.9; 40–49: 4.9; 50–59: 3.1; 60–69: 2.7; 70+: 2.4.

**Model D — UN WPP**
- WPP2024 deaths: 1959 15.90M, 1960 19.51M, 1961 14.70M; CDR 24.4 / 29.8 / 22.4‰. Normal years: 1957 11.92M (CDR 18.9), 1962 10.35M (CDR 15.6). WPP2022 is nearly identical (1960: 19.61M, CDR 29.99). — [wpp2024 data](https://github.com/PPgp/wpp2024), [wpp2022 data](https://github.com/PPgp/wpp2022)
- WPP2024's mid-year population is 583.5M in 1953 (census 582.6) and 713.8M in 1964 (census 694.6). WPP therefore embeds about 2.6–2.8% more 1953→64 growth than the two censuses show. That is equivalent to assuming the 1964 census under-counted by about 19M relative to 1953.

### Cited Findings
- Hill (1988) states that the crisis "cost some 30 million premature deaths and some 33 million lost or postponed births". He estimates adult death registration at about 80.5% complete and child-death registration at about 30%. — [Hill 1988](https://documents1.worldbank.org/curated/en/492811468771874832/pdf/Demographic-Trends-in-China-from-1950-to-1982.pdf)
- Hill's FY reconstruction: CDR 19.1 (1957-58), 24.4, 32.8, 29.5, 21.2, 15.1 (1962-63). Infant mortality 236 (1958-59). — same source

### Inferences
- **Registered deaths are a floor.** Official CDRs capture only about half of the famine excess: 15M against 31M. This matches Cao Shuji's remark that NBS rates give about 15M.
- **Model convergence.** The independent routes agree closely once the same 1953/1964 census totals are used: Hill's survey births, our 1982 and 1964 census back-projections, and calibrated cohort survival all give 30.7–34.9M.
- **Our replication of Hill's table gives less than "almost 30M".** Using Hill's own published FY CDRs with simple baselines gives 20.5–25.7M. That is below Ashton/Hill's "almost 30M". The likely reason is a lower or declining baseline in their computation (a normal CDR falling toward about 15‰), or a different period definition. Our counterfactual falls from 19.4 to 15.7‰ by FY1961, which yields 30.9M.
- **The Zhihu post's 29.57M "40+ gap" is reproducible only under low "normal" mortality.**
  - It needs normal mortality about 0.65–0.70 × WPP's, i.e. female e0 around 58–61 in 1957–63. That is roughly what an official, registration-based 1957 life table implies. The post said it used the 1957 and 1963 life tables, which we did not obtain.
  - With mortality consistent with the reconstructed age structure (WPP/Hill level, e0 about 47–50 in 1957), the 40+ gap is about 13M. Total excess among all pre-1953 cohorts is about 20M.
  - So the post's headline is roughly 2× too high for the 40+ group, because it counts 11 years of under-stated normal mortality as famine deaths.
  - Its conclusion that "almost all the shortfall is deaths, not lost births" is contradicted by survey and census births. The birth deficit (≈36M gross) is about as large as the excess deaths.
  - Its overall order of magnitude ("≈30M non-normal deaths") is nonetheless consistent with our central figure. It just arrives there for partly wrong reasons.
- **Control period 1964→1982.** Projecting the 1964 census forward with WPP mortality reproduces the 1982 census within about 1% at ages 18–45 (201.8 vs 202.0 civilians at ages 18–28; 200.5 vs 202.7 at ages 29–45). At ages 46+ it falls 8M short (181.1 vs 189.2). WPP's 1964–82 old-age mortality may be too high, or 1982 elderly ages exaggerated. Notably, WPP's 1981 e0 (62.6 male / 67.1 female) is below the NBS 1981 life table (66.28 / 69.27, [NBS 2005 T4-4](https://www.stats.gov.cn/sj/ndsj/2005/html/D0404e.htm)). If WPP also overstates 1950s normal mortality, our excess is biased low: normal mortality × 0.85 gives 40M.

### Gaps
- Exact Ashton et al. (1984) and Coale (1984) annual series: not obtained. We have only Coale's 1960 CDR of about 39 and Banister's of 44.6, from a secondary source.
- The "57 / 63 life tables" used by the Zhihu post: not identified.

---

## Q4. Sensitivity analysis, central estimate and defensible range

### Takeaway
- **Central:** 30.9M excess deaths (mid-1958 to mid-1963).
- **Defensible range:** about 22–40M (Monte Carlo 25–75%: 26.3–38.1M; 5–95%: 14.7–46.9M; median 32.1M).
- The range is driven, in order of importance, by four things. (1) How complete the 1953 census was relative to the 1964 census: each ±1% moves the total by ±5.5M. (2) The level of normal mortality: ±15% moves it by −9 / +9M. (3) Child famine mortality, which survey births pin near the WPP shape. (4) The choice of 1953 base: using NBS's 594.35M adds about 11M.

### Results (excess, mid-1958 to mid-1963, millions). Source: `results/09_sensitivity.csv`; chart: `charts/03_sensitivity_tornado.png`

| Scenario | Excess | Alive in 1953 | Born after |
|---|---|---|---|
| **Central** | **30.9** | 20.2 | 10.7 |
| 1953 true pop = census × 0.98 / 0.99 / 1.01 / 1.02 | 19.5 / 25.2 / 36.6 / 42.3 | 8.9 / 14.6 / 25.9 / 31.6 | 10.7 |
| 1964 true pop = census × 0.98 / 0.99 / 1.01 / 1.02 | 41.9 / 36.4 / 25.4 / 19.9 | | |
| 1964 true pop = census × 1.0275 (WPP-implied) | **15.8** (≈ WPP) | 5.1 | 10.7 |
| Both censuses +1% (equal undercount) | 31.1 | | |
| 1953 base V1 proportional / V3 567.4 only / V4 NBS 594.35 | 30.4 / 15.5 / 41.8 | | |
| Births: Hill 1988 / official / own 1964 / 1982 without military | 31.2 / 9.3 (invalid) / 30.7 / 30.7 | | |
| Normal mortality × 0.85 / × 1.15 | 40.3 / 22.0 | | |
| Normal anchors 1956/64; 1957/65 | 31.1; 31.2 | | |
| Child famine mortality k = 0.5 / 2 / = adult k | 24.9 / 43.6 / 51.4 | | 5.2 / 22.3 / 29.5 |
| Ages 50+ overstated 1 yr in both censuses | 33.2 | | |

**Monte Carlo** (300 draws; `results/11_monte_carlo_draws.csv`, `results/11_monte_carlo_summary.json`)
- Inputs drawn:
  - 1953 coverage and 1964 coverage: each N(0, 1%), independent.
  - Normal-mortality scale: lognormal(0, 0.08).
  - k_child: lognormal(0, 0.35).
  - 1953 base: V1 or V2.
  - Age overstatement: 0 or 1 year.
  - Births: own back-projection from 1982 or from 1964.
- Correlation with the result: 1953 coverage +0.56, normal mortality scale −0.49, k_child +0.48, 1964 coverage −0.43.

### Inferences
- **Choosing the central value.** WPP's assumption (a 1964 census under-count of about 2.7% relative to 1953) is the single assumption that separates "≈16M" from "≈31M".
  - We found no published evidence in this session for a 1964 under-count of that size relative to 1953.
  - Arguments in the other direction:
    - The 1953 census is generally thought *less* complete than 1964.
    - Duplicate hukou registration would inflate, not deflate, the 1964 count.
    - The 1964 census agrees with the 1982 census within about 1% for the cohorts aged 0–45 in 1964.
  - We therefore keep equal relative coverage as the central assumption, and treat WPP's figure as a low-end scenario rather than the central value.
- **Army, Taiwan and overseas inclusion.** These matter only through the 1953 base.
  - Using 594.35M (which includes about 11.7M overseas Chinese) is an error that adds about 11M.
  - The army or "unclassified" allocation changes the result by less than 1M (V1 vs V2).
  - If the 1953 figure of 582.6M excluded about 4M military, the excess would rise by about 3–4M. Not verified.
- **Age misreporting.** Old-age exaggeration in both censuses raises the estimate slightly (+2M), because true mortality at the reported ages would be lower.

### Gaps
- No independent post-enumeration evidence on 1953 versus 1964 census completeness was obtained.
- The famine age-shape f(x,t) is borrowed from WPP2024. Annual timing is an assumption, though the total is largely insensitive to it.

---

## Q5. Comparison with published estimates

### Takeaway
Our central 31M (range 22–40M) is close to Ashton/Hill (≈30M), Banister (29.9M) and Coale (26.8M for 1958–63). It is above Peng (≈23M), Li Chengrui (≈22M) and Jiang Zhenghua (≈17M), and well above UN WPP2024 (≈16–18M, computed here). The differences can be traced mainly to (a) the assumed relative completeness of the 1953 and 1964 censuses and (b) the normal-mortality baseline.

### Cited Findings and comparison

| Study | Period | Excess deaths | Lost births | Method | Our replication / comment |
|---|---|---|---|---|---|
| Ashton, Hill, Piazza, Zeitz 1984 ([IHSN abstract](https://catalog.ihsn.org/citations/46705)) | 1958–61 | "almost 30M" | 33M (Hill 1988) | Census survival + 1982 fertility-survey births | Same births and censuses give 31.2M (Model B/C). Hill's FY CDRs with flat or linear baselines give 20.5–25.7M, so their 30M implies a lower normal baseline. |
| Coale 1984 ([IUSSP paper](https://iussp.org/sites/default/files/event_call_for_papers/A%20study%20of%20population%20change%20led%20by%20China’s%20great%20famine_.pdf)) | 1958–63; 1959–61 | 26.8M; 24.81M | 30.68M (1959–61) | Three censuses + fertility survey, trend comparison | Within our range. Reproduced with normal mortality about 1.07 × WPP, or a 1953 base about 0.7% lower. |
| Banister 1987 (IUSSP paper; CDR 44.6 in 1960 per [Patnaik 2004](https://www.marxists.org/makedonski/tematska/mitovi-antikomunizam/2004/ideoloski-statistiki.htm)) | 1958–61 | 29.87M | – | Reconstruction | Agrees with our central figure. Her 1960 CDR (44.6) is above ours (about 33–35 at peak), because our FY smoothing spreads the peak. |
| Calot 1985 (IUSSP paper) | 1958–62 | 28.5M | ≈33.2M | Census-based | Agrees. |
| Jiang Zhenghua 1986/88 ([Cao 2005](https://chinadigitaltimes.net/chinese/?p=98017); IUSSP) | 1958–63 | 17M (16.5–17.9) | – | Dynamic-parameter model with life tables | Requires normal mortality about 1.25 × WPP, or a 1953 base about 2.5% lower relative to 1964 (true 1953 pop = census × 0.98 → 19.5M). |
| Peng Xizhe 1987 | 1958–62 | ≈23M (**not verified this session**) | – | Provincial registered CDR, adjusted | Corresponds to roughly our 25th percentile (26M) or below; similar to normal mortality × 1.15 (22M). |
| Li Chengrui 1997 (Cao 2005; IUSSP gives 21.58M) | famine period | ≈22M | – | Amended Coale | Similar to normal mortality × 1.15 or 1953 coverage −1%. |
| Luo Sheng 1988 (IUSSP) | 1959–63 | 28.89M | – | Brass-logit | Agrees. |
| Cao Shuji 2005 ([CDT](https://chinadigitaltimes.net/chinese/?p=98017)) | 1959–61 | 32.46M | – | Prefecture-level gazetteers | Agrees. |
| UN WPP2024 (computed here) | 1958–61 | 15.7M (B3/B4; 12.0–18.2 across baselines) | – | UN reconstruction | Reproduced (15.8M) only by assuming a 2.75% 1964 under-count relative to 1953. |
| Official registered CDR (computed here) | 1958–61 | 14.4–16.2M | – | Registration | A floor; registration is about 60% complete. |
| Zhihu "chenqin" | 1959–61 | ≈30M; "40+ gap 29.57M" | "no large birth decline" | Census projection with 1957/63 life tables | Total order of magnitude agrees. The 40+ gap is reproduced only with low, registration-level normal mortality; ours is about 13M. The birth claim is refuted. |

### Inferences
- Lower estimates (Jiang, Li, WPP) are mostly not about different data. They assume either higher normal mortality or a relatively more complete 1964 census, i.e. less 1953→64 attrition to be explained.
- Higher estimates (Cao, Banister) are consistent with equal census coverage and WPP-level or lower normal mortality.
- On the national data alone, a toll below about 15M requires both an under-counted 1964 census and high normal mortality. A toll above about 45M requires an under-counted 1953 census and low normal mortality, or very high child famine mortality.
- **Definitions used throughout.**
  - *Excess deaths:* all-cause deaths above the no-famine counterfactual. This includes disease, child deaths and any violence or camp deaths. It is **not** "starvation deaths", which are a subset not identifiable from these data.
  - *Lost births:* not deaths.
  - *Population deficit (≈59–67M):* excess deaths plus lost births.

### Gaps
- Peng Xizhe's 23M and his method were not verified.
- Banister's and Coale's full annual series were not retrieved.
- Coale & Chen (1987) were not retrieved.
- Li Chengrui's original article was not read; his figure is known only via Cao and the IUSSP paper.
- Some secondary-source numbers (IUSSP paper) may carry transcription errors.
