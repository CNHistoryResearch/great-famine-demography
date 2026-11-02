# Supplement: official provincial crude death and birth rates, 1956–1963, and provincial excess-death sums

Companion data file: `regional/provincial_cdr_1956_1963.csv`. It has 232 rows covering 29 units (28 plus Tibet as an empty placeholder) for 1956–63. Columns are province, year, cdr, cbr, source_url and notes. Every cross-check and discrepancy is recorded in the notes column.

This supplements `regional.md` §1–3. That file had verified 1960 CDRs for only 8 provinces, plus Sichuan.

## 1. Full provincial CDR series, 1956–1963

### Takeaway
- **Coverage:** A complete 1956–63 CDR series is now in hand for 27 of 28 units. The only gaps are Ningxia 1956–57, where only the two-year average of 10.9‰ is known, and Tibet, for which no data exist.
- **Sources:** There are two independent carriers of the State Statistical Bureau (SSB) data:
  - **(a)** an English table, "Death Rates of the Chinese Provinces, 1954-66", covering 24 provinces. It cites SSB 《人口统计资料汇编 1949–1985》 (1988).
  - **(b)** NBS provincial series as served by gotohui.com. I used these for Beijing, Tianjin, Shanghai, Xinjiang, Inner Mongolia, Liaoning and Jiangsu.
- **Agreement:** Where (a) and (b) overlap (Liaoning, Inner Mongolia, Jiangsu 1959–63), the values are identical. Both are also consistent with the 1956–57 baselines in a third table, the 大饥荒档案 excess-death table built from 《全国各省、自治区、直辖市历史统计资料汇编 1949–1989》.
- **Big caveat, Sichuan:** The 1988 compendium carries an older and lower series: 1958 17.37, 1959 19.22, 1960 47.78, 1961 28.01. The revised official series is 25.17 / 46.9 / 53.97 / 29.42 / 14.82.
- **Unresolved conflict, Guizhou 1960:** 52.33 per table (a) and Yang Jisheng, versus 45.4 per Zhao & Reimondos.

### Cited Findings
- **Table (a): 1960 CDRs (‰)** from "Table 1 Death Rates of the Chinese Provinces, 1954-66" (source line: State Statistical Bureau, *Renkou Tongji Ziliao Huibian 1949-1985*, Zhongguo Caizheng Jingji Chubanshe, 1988). Values in descending order:

  | Province | 1960 CDR (‰) | | Province | 1960 CDR (‰) |
  |---|---|---|---|---|
  | Anhui | 68.58 | | Fujian | 15.61 |
  | Guizhou | 52.33 | | Guangdong | 15.09 |
  | Sichuan (old series) | 47.78 | | Shanxi | 14.21 |
  | Gansu | 41.32 | | Ningxia | 13.88 |
  | Qinghai | 40.73 | | Shaanxi | 12.27 |
  | Henan | 39.65 | | Hebei | 12.19 |
  | Guangxi | 29.20 | | Zhejiang | 11.88 |
  | Hunan | 29.26 | | Liaoning | 11.50 |
  | Yunnan | 26.26 | | Heilongjiang | 10.52 |
  | Shandong | 23.51 | | Jilin | 10.13 |
  | Hubei | 21.22 | | Inner Mongolia | 9.40 |
  | Jiangsu | 18.41 | | | |
  | Jiangxi | 16.06 | | | |

  The full 1955–64 rows are in the CSV. The same page also carries a province mess-hall participation table and a party-membership table, which suggests it is the data appendix of a provincial regression paper in the Yang Dali / Kung–Lin tradition; the paper is not named on the page. — [fmtab123 mirror, yhcw.net](http://www.yhcw.net/famine/Research/fmtab123.htm) (original at [bannedbook.org](https://www.bannedbook.org/books/famine/Research/fmtab123.htm), which this environment could not reach)
- **Typos in table (a):** Gansu 1956 is printed "1078" and Hunan 1962 is printed "1023". These are decimal-point slips for 10.78 and 10.23. Gansu's 10.78 is confirmed by the 11.0 baseline in the 大饥荒档案 table. — [fmtab123](http://www.yhcw.net/famine/Research/fmtab123.htm)
- **NBS series via gotohui, CDR (‰) 1956→1963, in year order 1956, 57, 58, 59, 60, 61, 62, 63:**

  | Unit | 1956 | 1957 | 1958 | 1959 | 1960 | 1961 | 1962 | 1963 |
  |---|---|---|---|---|---|---|---|---|
  | [Beijing](https://population.gotohui.com/show-84823) | 7.73 | 8.19 | 8.08 | 9.66 | 9.14 | **10.80** | 8.77 | 8.11 |
  | [Tianjin](https://population.gotohui.com/show-84822) | 8.79 | 9.35 | 8.66 | 9.88 | **10.34** | 9.89 | 7.36 | 7.30 |
  | [Shanghai](https://population.gotohui.com/show-84821) | 6.60 | 6.10 | 6.20 | **7.80** | 6.90 | 7.70 | 7.20 | 7.00 |
  | [Xinjiang](https://population.gotohui.com/show-84739) | 14.20 | 14.00 | 13.00 | **18.84** | 15.67 | 11.71 | 9.71 | 9.43 |
  | [Inner Mongolia](https://population.gotohui.com/show-84762) | 7.9 | 10.5 | 7.9 | 11.0 | 9.4 | 8.8 | 9.0 | 8.5 |
  | [Liaoning](https://population.gotohui.com/show-84761) | 6.6 | 9.4 | 8.8 | 11.8 | 11.5 | **17.5** | 8.5 | 7.9 |
  | [Jiangsu](https://population.gotohui.com/show-84758) | 13.02 | 10.26 | 9.40 | 14.55 | **18.41** | 13.35 | 10.36 | 9.04 |

- **Zhao & Reimondos (2012), Table 1, CDR (‰) 1957–62** (citing Fan 1995 and Yao & Yin 1994):

  | Province | 1957 | 1958 | 1959 | 1960 | 1961 | 1962 |
  |---|---|---|---|---|---|---|
  | Anhui | 9.1 | 12.3 | 16.7 | 68.6 | 8.1 | 8.2 |
  | Gansu | 11.3 | 21.1 | 17.4 | 41.3 | 11.5 | 8.3 |
  | **Guizhou** | 8.8 | 13.7 | 16.2 | **45.4** | 17.7 | 10.4 |
  | Henan | 11.8 | 12.7 | 14.1 | 39.6 | 10.2 | 8.0 |
  | Qinghai | 10.4 | 13.0 | 16.6 | 40.7 | 11.7 | 5.4 |
  | Sichuan | 12.1 | 25.2 | 47.0 | 54.0 | 29.4 | 14.6 |
  | National | 10.8 | 12.0 | 14.6 | 25.4 | 14.2 | 10.0 |

  — [Zhao & Reimondos, Population 67(2) 2012](https://shs.cairn.info/article/E_POPU_1202_0329?lang=en)
- **Cross-check with the 大饥荒档案 1956–57 baselines.** That table was built from the 1990 《汇编 1949–1989》. Its baselines agree with the 1956–57 average from the series above to within 0.1‰ in 24 of 28 units (examples: Beijing 8.0, Tianjin 9.1, Shanghai 6.4, Xinjiang 14.1, Anhui 11.7, Gansu 11.0, Henan 12.9). The exceptions are:

  | Unit | 1956–57 average from the series above | 大饥荒档案 baseline |
  |---|---|---|
  | Fujian | 8.72 | 8.2 |
  | Hebei | 11.43 | 11.3 |
  | Jiangsu (table (a)) | 11.4 | 11.7 (gotohui gives 11.64) |
  | Sichuan | older 1956–57 values average 11.8 | 11.2 |

  — [大饥荒档案编辑部, 大跃进期间各省非正常死亡人口情况表 (2000)](http://www.yhcw.net/famine/Data/ExDeath01.html)
- **Second-hand table of mixed reliability (arXiv):** An arXiv paper citing "Ren kou (1988)" gives these 1960 values:

  | Province | 1960 CDR (‰) | Agreement with table (a) |
  |---|---|---|
  | Jilin | 10.1 | agrees |
  | Heilongjiang | 10.5 | agrees |
  | Sichuan | 47.8 | agrees with the old series |
  | Anhui | 50.2 | conflicts with 68.58 |

  I treat the Anhui 50.2 as unreliable. — [arXiv 1807.05100](https://arxiv.org/pdf/1807.05100)
- **Yang Jisheng's 1960 values against table (a):**

  | Province | Yang | Table (a) |
  |---|---|---|
  | Hunan | 29.42 | 29.26 |
  | Henan | 39.60 | 39.65 |
  | Shandong | 23.60 | 23.51 |
  | Gansu | 41.30 | 41.32 |
  | Guizhou | 52.33 | 52.33 |
  | Anhui | 68.58 | 68.58 |
  | Qinghai | 40.73 | 40.73 |

  These are small revisions except Hunan, where 29.42 duplicates Sichuan's 1961 figure. That looks like a transcription slip; 29.26 is preferred. — [Yang lecture](https://chinadigitaltimes.net/chinese/?p=103671)

### Inferences
- **Sichuan 1958:** The 大饥荒档案 average for Sichuan 1958–62 is 34.2‰. That is reproducible only with 1958 = 25.17 (mean 34.06), not 15.17 (mean 32.1). So the "15.17" in Yang's lecture text is a typo for 25.17.
- **Peak years outside the heartland:** Several northern and northeastern units peaked in 1961, not 1960:
  - Liaoning 17.5
  - Beijing 10.8
  - Hebei 13.34
  - Jilin and Heilongjiang 11.12

  Xinjiang peaked in 1959 at 18.84. Shanghai, the lowest-mortality unit, peaked in 1959 at 7.8, and its CDR never exceeded 7.8‰.
- **Missing excess deaths, Inner Mongolia and Heilongjiang:** These show essentially no 1960 excess, with CDR at or below baseline. Part of the reason is in-migration of young famine refugees. This is an inference, not verified here.
- **The two Sichuan series:** The 1988 compendium's older Sichuan series removes about 2 million excess deaths relative to the revised series. Any regression dataset built on the 1988 table understates Sichuan, and possibly Guizhou depending on version.

### Gaps
- **Birth rates (CBR):** Found only for Beijing, Xinjiang and Ningxia (NBS via gotohui), Shanghai (registered-population basis only) and Inner Mongolia (derived as natural growth plus CDR). All are in the CSV.

  | Unit | 1957 CBR (‰) | Famine low (‰) | 1963 CBR (‰) |
  |---|---|---|---|
  | Beijing | 42.10 | 25.70 (1961) | 43.41 |
  | Ningxia | 43.24 | 13.03 (1961) | 50.52 |

  Other provinces' CBR series exist on gotohui at show-847xx IDs (birth ID = death ID + 26 for the series checked: Jiangsu 84758/84784, Inner Mongolia 84762/84788, Xinjiang 84739/84765). They were not fetched because of the call budget.
- **Ningxia 1956–57:** CDRs were not retrieved individually.
- **Tibet:** No 1956–63 vital rates in any source found.
- **Guizhou 1960:** The 52.33 versus 45.4 conflict is unresolved. The original 《中国人口·贵州分册》 or 《汇编 1949–1989》 page would settle it.

## 2. Peng Xizhe (1987) provincial excess deaths

### Takeaway
Peng's provincial table was not retrievable. JSTOR is unreachable, and no text reproduction of his provincial rows was found. His national total is cited secondhand as about 23 million. The 大饥荒档案 table explicitly says it uses "a method similar to Peng Xizhe 1987", so it is the closest available proxy, not Peng's own numbers.

### Cited Findings
- **Peng's national figure:** Chen Shuo (2011) cites Peng (1987, PDR 13:639–670, "Demographic Consequences of the Great Leap Forward in China's Provinces") for about 2,300万 national excess deaths. He does not reproduce provincial values. — [Chen Shuo, 世界经济 2011(4), Fudan PDF](https://econ.fudan.edu.cn/__local/9/E1/47/52D80A1D70B1C5EDD15CC5FDA3E_4929A117_AA9BD.pdf?e=.pdf)
- **The proxy table's method:** The 大饥荒档案 table takes the 1956–57 average CDR as baseline. Famine years are each province's 1958–62 years above that baseline. Average population comes from 汇编 year-end figures. The editors describe the method as similar to Peng (1987). The total across 28 units is just over 18 million (my sum of their column: 1,856.4万). They note that applying Jiang Zhenghua's minimum 18% under-registration gives at least 22 million. — [大饥荒档案 table](http://www.yhcw.net/famine/Data/ExDeath01.html)

### Gaps
- Peng's own provincial numbers, his choice of years, and his under-registration adjustment remain unverified. Do not attribute the 大饥荒档案 figures to Peng.

## 3. Other provincial breakdowns, and a computed simple estimate

### Takeaway
I recomputed excess deaths per province as (CDR − 1956–57 mean) × average famine-period population, using the CDRs above and the 大饥荒档案 population figures. The provincial sums are:

| Version | Total |
|---|---|
| 1958–62, positive years only | 1,901万 |
| 1958–62, net (negative years subtracted) | 1,739万 |
| 1959–61 only | 1,733万 |
| 大饥荒档案 published figure | 1,856万 |

All of these lie between the NBS national-derived ≈1,620万 and Yang's sum of provincial 《中国人口》 data, 2,098万. They are well below Cao Shuji's gazetteer reconstruction, 3,246万.

### Cited Findings
- **大饥荒档案 excess deaths (万), 1956–57 baseline**, with excess as ‰ of average population:

  | Province | Excess deaths (万) | ‰ of avg. pop | | Province | Excess deaths (万) | ‰ of avg. pop |
  |---|---|---|---|---|---|---|
  | Sichuan | 777.8 | 114.9 | | Guangdong | 27.1 | |
  | Anhui | 203.3 | 60.9 | | Fujian | 17.1 | |
  | Henan | 133.8 | | | Jilin | 16.7 | |
  | Shandong | 127.9 | | | Zhejiang | 11.2 | |
  | Hunan | 97.6 | | | Shaanxi | 10.7 | |
  | Guangxi | 63.9 | | | Qinghai | 10.5 | 44.7 |
  | Gansu | 62.7 | 49.7 | | Jiangxi | 10.1 | |
  | Guizhou | 51.9 | | | Heilongjiang | 6.1 | |
  | Jiangsu | 48.8 | | | Shanxi | 4.5 | |
  | Hubei | 48.1 | | | Xinjiang | 4.0 | |
  | Liaoning | 42.4 | | | Beijing | 4.0 | |
  | Yunnan | 38.4 | | | Ningxia | 2.4 | |
  | Hebei | 29.5 | | | Shanghai | 2.2 | |
  | | | | | Inner Mongolia | 2.1 | |
  | | | | | Tianjin | 1.6 | |

  — [大饥荒档案 table](http://www.yhcw.net/famine/Data/ExDeath01.html)
- **Lin & Yang (2000) excess death rate:** It is used as a provincial variable for 27 provinces: mean 6.4, SD 6.9, min 0.1, max 28.6 (units of 0.1%, i.e. ‰). The provincial rows are not shown in this source. — [Social Science & Medicine 148 (2015), PMC table](https://pmc.ncbi.nlm.nih.gov/articles/PMC4698174/table/T2)
- **Other datasets not obtained:** I could not obtain Houser/Sands/Xiao 2009, Kung & Lin 2003, or the Meng/Qian/Yared 2015 replication data. GitHub search API calls failed: the API returned 403 ("no linked GitHub account"). No web copy of their provincial rows was found.

### Computed simple estimate (this session; script logic described in Inferences)

Units are 万 (10,000 people). The baseline is the 1956–57 mean of the CSV CDRs; for Sichuan it is the 大饥荒档案 11.2, because revised 1956 is unavailable. Population is the 大饥荒档案 average famine-period population, held constant across years.

| Province | Baseline ‰ | Pop (万) | Excess 1958–62, positive years | Net 1958–62 | Excess 1959–61 | 大饥荒档案 | Cao 2005 |
|---|---|---|---|---|---|---|---|
| Sichuan | 11.2 | 6768 | 773.4 | 773.4 | 654.4 | 777.8 | 940 |
| Anhui | 11.68 | 3337 | 209.0 | 186.6 | 206.7 | 203.3 | 633 |
| Henan | 12.9 | 4930 | 137.8 | 99.5 | 137.8 | 133.8 | 294 |
| Shandong | 12.11 | 5302 | 131.1 | 131.1 | 126.3 | 127.9 | 181 |
| Guizhou | 12.68 | 1687 | 101.9 | 100.2 | 97.6 | **51.9** | 175 |
| Hunan | 10.93 | 3617 | 99.6 | 97.1 | 97.2 | 97.6 | 249 |
| Guangxi | 12.45 | 2183 | 64.5 | 58.5 | 64.5 | 63.9 | 93 |
| Gansu | 11.05 | 1263 | 59.4 | 55.9 | 46.7 | 62.7 | 102 |
| Jiangsu | 11.64 | 4262 | 48.5 | 33.5 | 48.5 | 48.8 | 153 |
| Hubei | 10.21 | 3161 | 48.3 | 38.3 | 48.3 | 48.1 | 68 |
| Liaoning | 8.0 | 2514 | 45.5 | 45.5 | 42.2 | 42.4 | <50 |
| Yunnan | 15.75 | 1907 | 35.5 | 18.7 | 24.3 | 38.4 | 80 |
| Guangdong | 9.8 | 3445 | 27.9 | 24.0 | 27.9 | 27.1 | 66 |
| Jilin | 8.29 | 1376 | 16.9 | 16.9 | 13.5 | 16.7 | <50 |
| Fujian | 8.72 | 1572 | 16.3 | 12.4 | 16.3 | 17.1 | <50 |
| Hebei | 11.43 | 3778 | 13.5 | 2.3 | 13.5 | **29.5** | 61 |
| Zhejiang | 9.39 | 2606 | 11.4 | 8.7 | 11.4 | 11.2 | <50 |
| Shaanxi | 10.08 | 1862 | 10.9 | 7.0 | 9.1 | 10.7 | <50 |
| Jiangxi | 11.98 | 1969 | 10.1 | 6.0 | 10.1 | 10.1 | <50 |
| Qinghai | 9.87 | 236 | 9.9 | 8.8 | 9.2 | 10.5 | <50 |
| Heilongjiang | 10.27 | 1740 | 6.3 | 1.5 | 6.3 | 6.1 | <50 |
| Shanxi | 12.14 | 1664 | 4.7 | 2.7 | 4.7 | 4.5 | <50 |
| Beijing | 7.96 | 698 | 4.6 | 4.6 | 4.0 | 4.0 | <50 |
| Shanghai | 6.35 | 997 | 4.2 | 4.0 | 3.3 | 2.2 | <50 |
| Xinjiang | 14.1 | 642 | 4.1 | −1.0 | 4.1 | 4.0 | <50 |
| Ningxia | 10.9 | 200 | 2.2 | 1.7 | 1.6 | 2.4 | <50 |
| Inner Mongolia | 9.2 | 1076 | 2.2 | 0.1 | 2.2 | 2.1 | <50 |
| Tianjin | 9.07 | 573 | 1.7 | 0.4 | 1.7 | 1.6 | <50 |
| **Total (28)** | | | **1,901.4** | **1,738.6** | **1,733.3** | **1,856.4** | 3,245.8 |

### Inferences
- **Reproducibility:** My recomputation reproduces the 大饥荒档案 figures within about ±5万 for 25 of 28 units. That confirms the CDR series in the CSV are essentially the 汇编 numbers. The three exceptions:
  - **Guizhou:** mine 101.9 against their 51.9. Their 1958–61 average CDR is 20.4‰, which is inconsistent both with 52.33 for 1960 (average 27.8) and with Zhao & Reimondos's 45.4 (average 23.3). Either their Guizhou input or the Guizhou series differs, and this is unresolved.
  - **Hebei:** mine 13.5 against their 29.5. Their 1959–61 average is 13.9‰ against 12.6‰ in table (a), so their Hebei series is higher. One possibility is that it includes Tianjin, which was administered by Hebei for most of 1958–66 (from memory, not verified here). Their separate Tianjin row would then double-count.
  - **Shanghai:** mine 4.2 against their 2.2, a small difference.
- **Comparison with the ~16M national official figure:**
  - Summing the provinces gives 1,730–1,900万. That is 7–17% above the ≈1,620万 implied by NBS national series.
  - Two reasons: provincial sums count only positive deviations in each province's own famine years, so there is no offsetting; and provincial baselines (1956–57) are not identical to the national baseline.
  - The Sichuan series version alone swings the total by about 200万.
  - Yang's 2,098万 "provincial official sum" is higher still. It uses the 《中国人口》 provincial volumes and a different baseline and years, which could not be reproduced here.
- **Concentration:** Sichuan alone is about 41% of the provincial sum. Sichuan, Anhui, Henan, Shandong, Guizhou and Hunan are about 77%. Cao's gazetteer figures are 1.2–3× higher in nearly every province, most of all in Anhui (3.1×), Jiangsu (3.2×) and Hebei (2–4.5×). That fits the claim that provincial vital registration missed many famine deaths, unevenly across provinces.
- **Method caveat:** These simple estimates use constant average population and no correction for under-registration. Jiang Zhenghua's ≥18% correction would raise the 28-unit sum to about 2,050–2,250万.
