# Age and sex analysis (UN WPP)

`wpp_excess_by_age.py` and `checks.py` compute excess deaths by age and sex implied by the UN World Population
Prospects 2022 single-year series, and the arithmetic checks of the Zhihu answer's "7×" and "40+ gap" claims.

The WPP files are large and not stored here. Fetch them, then pass the folder as the first argument:

```bash
mkdir -p models/cohort/data
for f in mx1dt popAge1dt; do
  curl -L -o models/cohort/data/$f.rda https://github.com/PPgp/wpp2022/raw/master/data/$f.rda
done
python models/cohort/wpp_excess_by_age.py models/cohort/data
```

Note: the UN's age split of famine excess is a modelling assumption, not independent evidence.
