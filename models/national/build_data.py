"""Assemble input data CSVs (each with a source column). Run: python3 -I build_data.py"""
import pandas as pd, numpy as np, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'national')

# 1. Official NBS series 1949-1970 (中国历年人口状况统计1949-2004, as reproduced in the 2012 chenqin Zhihu answer)
off = """year,pop_end_10k,male_10k,female_10k,urban_10k,rural_10k,cbr,cdr,nir
1949,54167,28145,26022,5765,48402,36,20,16
1950,55196,28669,26527,6169,49027,37,18,19
1951,56300,29231,27069,6632,49668,37.8,17.8,20
1952,57482,29833,27649,7163,50319,37,17,20
1953,58796,30468,28328,7826,50970,37,14,23
1954,60266,31242,29024,8249,52017,37.97,13.18,24.79
1955,61465,31809,29656,8285,53180,32.6,12.28,20.32
1956,62828,32536,30292,9185,53643,31.9,11.4,20.5
1957,64653,33469,31184,9949,54704,34.03,10.8,23.23
1958,65994,34195,31799,10721,55273,29.22,11.98,17.24
1959,67207,34890,32317,12371,54836,24.78,14.59,10.19
1960,66207,34283,31924,13073,53134,20.86,25.43,-4.57
1961,65859,33880,31979,12707,53152,18.02,14.24,3.78
1962,67295,34517,32778,11659,55636,37.01,10.02,26.99
1963,69172,35533,33639,11646,57526,43.37,10.04,33.33
1964,70499,36142,34357,12950,57549,39.14,11.5,27.64
1965,72538,37128,35410,13045,59493,37.88,9.5,28.38
1966,74542,38189,36353,13313,61229,35.05,8.83,26.22
1967,76368,39115,37253,13548,62820,33.96,8.43,25.53
1968,78534,40226,38308,13838,64696,35.59,8.21,27.38
1969,80671,41289,39382,14117,66554,34.11,8.03,26.08
1970,82992,42686,40306,14424,68568,33.43,7.6,25.83"""
from io import StringIO
o = pd.read_csv(StringIO(off))
o['source'] = ('NBS 中国历年人口状况统计(1949-2004) as reproduced in Zhihu screenshot (chenqin); totals/CBR/CDR cross-checked vs '
               'Statistical Yearbook of China 1983 as reproduced in Hill 1988 World Bank Discussion Paper 22 Table 1 and NBS 1999 yearbook Table 4-2')
# CDR as printed in the screenshot (read from a 2x zoom) differs in the 2nd decimal for several years from
# CBR-NIR and from NBS yearbooks; keep both. cdr_nbs = CBR - NIR (agrees with SYB1983 1-decimal values in Hill 1988 and NBS 1999 Table 4-2).
o['cdr_screenshot']=o['cdr']
o.loc[o.year==1956,'cdr_screenshot']=11.48; o.loc[o.year==1958,'cdr_screenshot']=11.9
o.loc[o.year==1959,'cdr_screenshot']=14.58; o.loc[o.year==1960,'cdr_screenshot']=25.49
o.loc[o.year==1961,'cdr_screenshot']=14.23; o.loc[o.year==1962,'cdr_screenshot']=10.04
o.loc[o.year==1963,'cdr_screenshot']=10.02; o.loc[o.year==1964,'cdr_screenshot']=11.54
o['cdr']=(o.cbr-o.nir).round(2)
o.to_csv(f'{D}/official_nbs_vitals_1949_1970.csv', index=False)

# 2. Census totals
c = pd.DataFrame([
 dict(census='1953', ref_date='1953-06-30 24:00', item='mainland total (direct+indirect)', persons=582603417, source='1953 census communique; = Hill 1988 Table1 582.6M; Wikipedia 1964 Chinese census page'),
 dict(census='1953', ref_date='1953-06-30 24:00', item='directly enumerated', persons=574205940, source='1953 census communique (standard figure; not re-fetched online in this session)'),
 dict(census='1953', ref_date='1953-06-30 24:00', item='indirectly estimated (remote areas e.g. Tibet)', persons=8397477, source='1953 census communique (582603417-574205940)'),
 dict(census='1953', ref_date='1953-06-30 24:00', item='NBS published total (excl. Taiwan, incl. overseas Chinese/students ~11.74M)', persons=594350000, source='NBS yearbook 2005 Table 4-4 (59435 x10k); = 601938035 - Taiwan 7591298'),
 dict(census='1953', ref_date='1953-06-30 24:00', item='age-classified population (single-year table)', persons=567446758, source='IDE-JETRO statistical compilation TSS009400_007 (ir.ide.go.jp/record/44763)'),
 dict(census='1964', ref_date='1964-06-30 24:00', item='mainland 28 prov. + military', persons=694581759, source='NBS 1964 census communique (stats.gov.cn t20230206_1901987)'),
 dict(census='1964', ref_date='1964-06-30 24:00', item='grand total incl. Taiwan/HK/Macau/overseas', persons=723070269, source='NBS 1964 census communique'),
 dict(census='1964', ref_date='1964-06-30 24:00', item='age-classified population', persons=694581759, source='IDE-JETRO TSS009400_007'),
 dict(census='1982', ref_date='1982-07-01 00:00', item='mainland 29 prov. + military', persons=1008175288, source='NBS yearbook 2005 Table 4-4 (100818 x10k); Hill 1988 (1,008,175 thousand)'),
 dict(census='1982', ref_date='1982-07-01 00:00', item='age-classified (civilian) population', persons=1003913927, source='IDE-JETRO TSS009400_007'),
])
c.to_csv(f'{D}/census_totals.csv', index=False)

# 3. Hill (1988) reconstruction FY (mid-year to mid-year) 1953-64 (millions)
h = pd.DataFrame({'fy_start':range(1953,1964),
 'pop_begin_m':[582.6,594.7,608.3,620.3,633.7,647.3,653.5,651.0,646.6,653.7,677.4],
 'births_m':[26.08,27.31,24.82,25.54,25.80,22.11,18.88,14.72,20.88,33.81,30.71],
 'deaths_m':[13.99,13.69,12.86,12.10,12.24,15.87,21.37,19.17,13.79,10.07,11.73],
 'cbr':[44.3,45.4,40.4,40.7,40.3,34.0,28.9,22.7,32.1,50.8,44.7],
 'cdr':[23.8,22.8,20.9,19.3,19.1,24.4,32.8,29.5,21.2,15.1,17.1],
 'imr':[186,177,167,156,144,236,205,132,236,88,96]})
h['source']='Hill 1988, Demographic Trends in China from 1950 to 1982, World Bank Discussion Paper 22, Table 2 (reconstruction underlying Ashton et al. 1984; births from 1982 1-per-1000 fertility survey adjusted)'
h.to_csv(f'{D}/hill1988_reconstruction_fy1953_1964.csv', index=False)
print('ok')
