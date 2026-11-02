# Methodology (v1.0)

Full detail is in the report ([English](../reports/v1.0/report_en.md), sections "National estimate" and
"Three common objections") and the notes in `research/v1.0/notes/national_modeling.md`.

## Definitions

- **Excess deaths** (超额死亡, 非正常死亡 in demographic usage): deaths above what a no-famine counterfactual
  mortality schedule would have produced in the same population. Includes starvation, disease, child deaths, violence.
- **Starvation deaths** (饿死): a subset; no data source isolates it nationally.
- **Lost births**: births that did not happen because of the famine. Never counted as deaths.
- **Population deficit**: excess deaths + net lost births.

## Data

- 1953, 1964, 1982 census totals and single-year age distributions (`data/national/census_*`). The comparable
  1953 mainland base is 582.6 million, not the 594.35 million NBS lists (which includes overseas Chinese).
- Official registered births, deaths and year-end population, 1949–1982 (`official_nbs_vitals_*`), which come from
  Ministry of Public Security household registration before 1982.
- Hill (1988) survey-based births from the 1982 One-per-Thousand Fertility Survey.
- UN World Population Prospects 2022/2024 single-age mortality (normal-mortality schedule).

## Models (`models/national/famine_model.py`)

- **A. Crude-rate excess**: registered death rate minus a baseline, times population. A floor.
- **B. Intercensal balancing**: deaths = 1953 population + births − 1964 population, under several birth series.
- **C. Census-calibrated cohort-component (central)**: single-year, two-sex projection from the 1953 census with
  no-famine mortality interpolated 1957→1963; births back-projected from the 1982 census; famine mortality scaled
  so that the projection reproduces the 1964 census exactly. Child mortality calibrated separately against Hill's births.
- **D. UN WPP** series through the same baselines, for comparison.

## Main uncertainties

1. Relative completeness of the 1953 and 1964 censuses: each 1% moves the estimate about ±5.5 million.
2. The level of normal mortality: ±15% moves it about ±9 million.
3. Child famine mortality: halving or doubling moves it to 24.9–43.6 million.

A Monte Carlo over these gives a median of 32.1 million and an interquartile range of 26.3–38.1 million.

## Reproducing

```bash
pip install -r requirements.txt
python models/national/famine_model.py     # writes models/national/results/
python models/national/charts_and_mc.py    # charts and Monte Carlo
python -m pipeline.check_model             # compares with data/registry/estimates.yaml
```
