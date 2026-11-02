"""
National excess-death model for China's 1958-62 famine.
Run:  python3 -I famine_model.py      (reads ./data/*.csv, writes ./results/*.csv and ./charts/*.png)
Units: millions of persons unless noted. FY t = mid-year t to mid-year t+1 (census dates are mid-year).
"""
import os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, '..', '..', 'data', 'national')
R = os.path.join(HERE, 'results'); C = os.path.join(HERE, 'charts')
os.makedirs(R, exist_ok=True); os.makedirs(C, exist_ok=True)
out = {}

# ---------------------------------------------------------------- data
off = pd.read_csv(f'{D}/official_nbs_vitals_1949_1970.csv').set_index('year')
off2 = pd.read_csv(f'{D}/official_nbs_vitals_1971_1982.csv').set_index('year')
offall = pd.concat([off[['pop_end_10k', 'cbr', 'cdr']], off2[['pop_end_10k', 'cbr', 'cdr']]])
offall['P'] = offall.pop_end_10k / 100.0           # millions, year end
offall['mid'] = (offall.P + offall.P.shift(1)) / 2
w24 = pd.read_csv(f'{D}/wpp2024_china_annual_1950_1985.csv').set_index('year')
w22 = pd.read_csv(f'{D}/wpp2022_china_annual_1950_1985.csv').set_index('year')
hill = pd.read_csv(f'{D}/hill1988_reconstruction_fy1953_1964.csv').set_index('fy_start')
age = pd.read_csv(f'{D}/census_age_single_year_1953_1964_1982.csv')
mxd = pd.read_csv(f'{D}/wpp2024_china_mx_single_age_1950_1985.csv')
popw = pd.read_csv(f'{D}/wpp2024_china_pop_single_age_1949_1985.csv')

P53_MAIN, P53_DIRECT, P53_NBS, P53_AGE = 582.603417, 574.205940, 594.35, 567.446758
P64, P82, P82_AGE = 694.581759, 1008.175288, 1003.913927

# ---------------------------------------------------------------- 1. internal consistency of official series
cons = pd.DataFrame(index=range(1950, 1971))
cons['dP_reported'] = offall.P.diff()
cons['births'] = offall.cbr / 1000 * offall.mid
cons['deaths'] = offall.cdr / 1000 * offall.mid
cons['nat_incr'] = cons.births - cons.deaths
cons['residual_dP_minus_NI'] = cons.dP_reported - cons.nat_incr
cons = cons.round(3); cons.to_csv(f'{R}/01_official_consistency.csv')
out['consistency'] = {
    'resid_1958_1959': float(cons.loc[1958:1959].residual_dP_minus_NI.sum()),
    'resid_1960_1961': float(cons.loc[1960:1961].residual_dP_minus_NI.sum()),
    'resid_1958_1961': float(cons.loc[1958:1961].residual_dP_minus_NI.sum()),
    'resid_1962_1964': float(cons.loc[1962:1964].residual_dP_minus_NI.sum()),
    'resid_1954_1957': float(cons.loc[1954:1957].residual_dP_minus_NI.sum()),
    'resid_1965_1970': float(cons.loc[1965:1970].residual_dP_minus_NI.sum())}

# ---------------------------------------------------------------- 2. aggregate intercensal accounting (official rates)
def window_sum(series, y0, y1):
    """sum calendar-year flows from mid-y0 to mid-y1 (half weights at ends)"""
    s = series.loc[y0:y1].copy(); s.loc[y0] *= 0.5; s.loc[y1] *= 0.5; return float(s.sum())
b_all = offall.cbr / 1000 * offall.mid; d_all = offall.cdr / 1000 * offall.mid
acc = []
for (y0, y1, p0, p1, lab) in [(1953, 1964, P53_MAIN, P64, '1953-64 (mainland 582.6)'),
                              (1953, 1964, P53_NBS, P64, '1953-64 (NBS 594.35 incl. overseas Chinese)'),
                              (1964, 1982, P64, P82, '1964-82 control period')]:
    B, Dd = window_sum(b_all, y0, y1), window_sum(d_all, y0, y1)
    acc.append(dict(period=lab, P_start=p0, births_official=B, deaths_official=Dd,
                    P_end_predicted=p0 + B - Dd, P_end_census=p1, closure_error=p0 + B - Dd - p1,
                    closure_error_pct=100 * (p0 + B - Dd - p1) / p1,
                    implied_deaths_with_official_births=p0 + B - p1,
                    implied_over_registered=(p0 + B - p1) / Dd))
acc = pd.DataFrame(acc); acc.to_csv(f'{R}/02_intercensal_accounting_official.csv', index=False)
# official year-end series vs census (interpolated to mid-year)
out['official_vs_census'] = {
    'official_mid1953': float((offall.P[1952] + offall.P[1953]) / 2), 'census1953': P53_MAIN,
    'official_mid1964': float((offall.P[1963] + offall.P[1964]) / 2), 'census1964': P64,
    'official_mid1982': float((offall.P[1981] + offall.P[1982]) / 2), 'census1982': P82}

# ---------------------------------------------------------------- 3. Model A: crude-rate excess
def crude_excess(cdr, pop, baseline, years):
    return float(sum((cdr[y] - baseline[y]) / 1000 * pop[y] for y in years))
def lin(y, ya, va, yb, vb): return va + (vb - va) * (y - ya) / (yb - ya)
yrs = range(1955, 1966)
nonfam = [1954, 1955, 1956, 1957, 1963, 1964, 1965]
rowsA = []
series = {'Official NBS (registered)': (off.cdr, offall.mid),
          'UN WPP2024': (w24.cdr, w24.deaths / w24.cdr),  # pop = deaths/cdr (millions since deaths in thousands)
          'UN WPP2022': (w22.cdr, w22.deaths / w22.cdr)}
for name, (cdr, pop) in series.items():
    fit = np.polyfit(nonfam, [cdr[y] for y in nonfam], 1)
    bases = {'B1 flat 1957': {y: cdr[1957] for y in yrs},
             'B2 mean 1956-57': {y: (cdr[1956] + cdr[1957]) / 2 for y in yrs},
             'B3 linear 1957->1963': {y: lin(y, 1957, cdr[1957], 1963, cdr[1963]) for y in yrs},
             'B4 OLS trend 1954-57 & 1963-65': {y: np.polyval(fit, y) for y in yrs},
             'B5 mean 1957 & 1963-64': {y: (cdr[1957] + cdr[1963] + cdr[1964]) / 3 for y in yrs}}
    for bn, b in bases.items():
        rowsA.append(dict(series=name, baseline=bn,
                          excess_1958_61=crude_excess(cdr, pop, b, range(1958, 1962)),
                          excess_1959_61=crude_excess(cdr, pop, b, range(1959, 1962)),
                          excess_1958_62=crude_excess(cdr, pop, b, range(1958, 1963))))
# Hill FY series (FY1958..FY1961 = mid-1958..mid-1962)
hp = hill.pop_begin_m + (hill.births_m - hill.deaths_m) / 2
hc = hill.cdr
for bn, b in {'B1 flat FY1957': {y: hc[1957] for y in range(1953, 1964)},
              'B3 linear FY1957->FY1962': {y: lin(y, 1957, hc[1957], 1962, hc[1962]) for y in range(1953, 1964)},
              'B4 OLS trend FY1953-57 & 62-63': {y: np.polyval(np.polyfit([1953, 1954, 1955, 1956, 1957, 1962, 1963], [hc[y] for y in [1953, 1954, 1955, 1956, 1957, 1962, 1963]], 1), y) for y in range(1953, 1964)}}.items():
    rowsA.append(dict(series='Hill 1988 reconstruction (FY)', baseline=bn,
                      excess_1958_61=crude_excess(hc, hp, b, range(1958, 1962)),
                      excess_1959_61=crude_excess(hc, hp, b, range(1959, 1962)),
                      excess_1958_62=crude_excess(hc, hp, b, range(1958, 1963))))
A = pd.DataFrame(rowsA).round(2); A.to_csv(f'{R}/03_modelA_crude_rate_excess.csv', index=False)

# ---------------------------------------------------------------- 4. cohort-component machinery (single year, by sex)
NA = 86  # ages 0..84, 85 = 85+
years = range(1950, 1986)
def mx_matrix(col):
    m = mxd.pivot(index='age', columns='year', values=col)
    p = popw.pivot(index='age', columns='year', values='popM' if col == 'mxM' else 'popF')
    M = np.zeros((NA, len(years)))
    for j, y in enumerate(years):
        M[:85, j] = m.loc[0:84, y].values
        pp = p.loc[85:, y] if y in p.columns else p.loc[85:, 1985]
        mm = m.loc[85:, y].reindex(pp.index).fillna(m.loc[100, y])
        M[85, j] = float((mm * pp).sum() / pp.sum())
    return M
MX = {'M': mx_matrix('mxM'), 'F': mx_matrix('mxF')}
yi = {y: j for j, y in enumerate(years)}

def normal_mx(MXs, a0=1957, a1=1963, scale=1.0):
    """no-famine counterfactual: log-linear interpolation between anchor years; scale applies to all years"""
    N = MXs.copy()
    for y in range(a0 + 1, a1):
        f = (y - a0) / (a1 - a0)
        N[:, yi[y]] = np.exp((1 - f) * np.log(MXs[:, yi[a0]]) + f * np.log(MXs[:, yi[a1]]))
    return N * scale

def famine_shape(MXs, N):
    return np.clip(MXs / N - 1, 0, None)  # proportional famine excess in WPP (zero outside famine years)

def step_mort(M, t):
    """effective m for cohort aged x at mid t -> x+1 at mid t+1"""
    m0, m1 = M[:, yi[t]], M[:, yi[t + 1]]
    a = 0.5 * (m0 + m1)
    eff = np.empty(NA); eff[:84] = 0.5 * (a[:84] + a[1:85]); eff[84] = 0.5 * (a[84] + a[85]); eff[85] = a[85]
    q0 = a[0] / (1 + 0.7 * a[0]); sB = 1 - 0.7 * q0
    return eff, sB

def project(P0, births, Mdict, t0, t1, Mexp=None):
    """P0: dict sex->array(NA) at mid t0. births: dict FY->total births (M). Returns P at mid t1, deaths & expected deaths per FY"""
    P = {s: P0[s].copy() for s in 'MF'}; rec = []
    for t in range(t0, t1):
        tot_d = tot_e = 0.0
        newP = {}
        for s, shr in (('M', 0.515), ('F', 0.485)):
            eff, sB = step_mort(Mdict[s], t)
            surv = np.exp(-eff); B = births.get(t, 0.0) * shr
            n = np.zeros(NA); n[1:85] = P[s][:84] * surv[:84]; n[85] = P[s][84] * surv[84] + P[s][85] * surv[85]; n[0] = B * sB
            tot_d += P[s].sum() + B - n.sum()
            if Mexp is not None:
                effE, sBE = step_mort(Mexp[s], t)
                tot_e += float((P[s] * (1 - np.exp(-effE))).sum() + B * (1 - sBE))
            newP[s] = n
        P = newP; rec.append(dict(fy=t, deaths=tot_d, expected=tot_e, births=births.get(t, 0.0)))
    return P, pd.DataFrame(rec)

def census_vec(yr, total=None, extra_males=0.0, male_ages=(18, 35), age_shift=0):
    a = age[age.census == yr].sort_values('age')
    v = {'M': a.male.values / 1e6, 'F': a.female.values / 1e6}
    if age_shift:   # ages >=50 overstated by age_shift years -> move counts younger
        for s in 'MF':
            x = v[s].copy(); y = x.copy(); y[50:85] = 0
            y[50 - age_shift:85 - age_shift] += x[50:85]; v[s] = y
    if extra_males:
        lo, hi = male_ages; w = v['M'][lo:hi + 1]; v['M'][lo:hi + 1] += extra_males * w / w.sum()
    if total is not None:
        f = total / (v['M'].sum() + v['F'].sum()); v = {s: v[s] * f for s in 'MF'}
    return v

def init53(variant='V2', cov=0.0, age_shift=0):
    if variant == 'V1':   # proportional scaling of age-classified pop to mainland total
        v = census_vec(1953, P53_MAIN, age_shift=age_shift)
    elif variant == 'V2':  # unclassified 6.76M directly-enumerated -> males 18-35 (army etc.); 8.40M indirect -> proportional
        v = census_vec(1953, None, extra_males=P53_DIRECT - P53_AGE, age_shift=age_shift)
        f = P53_MAIN / (v['M'].sum() + v['F'].sum()); v = {s: v[s] * f for s in 'MF'}
    elif variant == 'V3':
        v = census_vec(1953, None, age_shift=age_shift)
    elif variant == 'V4':
        v = census_vec(1953, P53_NBS, age_shift=age_shift)
    return {s: v[s] * (1 + cov) for s in 'MF'}

def c64(cov=0.0, age_shift=0):
    v = census_vec(1964, None, age_shift=age_shift); return {s: v[s] * (1 + cov) for s in 'MF'}
def c82(military=True):
    v = census_vec(1982, None, extra_males=(P82 - P82_AGE) if military else 0.0, male_ages=(18, 30)); return v

def backproject_births(cens, census_year, Mdict, fys):
    """births in FY t = N(census, age census_year-1-t)/survival(birth->census) under Mdict"""
    tot = cens['M'] + cens['F']; res = {}
    for t in fys:
        a = census_year - 1 - t
        s_m = s_f = None
        for s in 'MF':
            eff, sB = step_mort(Mdict[s], t); sv = sB
            for k in range(t + 1, census_year):
                e, _ = step_mort(Mdict[s], k); sv *= np.exp(-e[k - t - 1])
            if s == 'M': s_m = sv
            else: s_f = sv
        res[t] = cens['M'][a] / (0.515 * s_m) * 0.5 + cens['F'][a] / (0.485 * s_f) * 0.5
    return res

FY = range(1953, 1964)
def run(init='V2', cov53=0.0, cov64=0.0, births='own1982', anchors=(1957, 1963), nscale=1.0,
        age_shift=0, mil82=True, fixed_k=None, k_child=None):
    """Calibrated cohort-component reconstruction 1953->1964.
    Actual mortality m = m_normal * (1 + k * f), f = WPP2024 proportional famine excess (age/year shape),
    k_adult calibrated so cohorts alive in 1953 reproduce the 1964 census at ages 11+.
    k_child: calibrated to 1964 ages 0-10 when births are independent (Hill / official); otherwise fixed (default 1 = WPP shape)."""
    N = {s: normal_mx(MX[s], *anchors, scale=nscale) for s in 'MF'}
    Nw = {s: normal_mx(MX[s], *anchors) for s in 'MF'}
    F = {s: famine_shape(MX[s], Nw[s]) for s in 'MF'}
    def Mk(k_ad, k_ch):
        o = {}
        for s in 'MF':
            kk = np.full((NA, 1), k_ad); kk[:11] = k_ch
            o[s] = N[s] * (1 + kk * F[s])
        return o
    P0 = init53(init, cov53, age_shift); T64 = c64(cov64, age_shift)
    tgt_ad = sum(T64[s][11:].sum() for s in 'MF'); tgt_ch = sum(T64[s][:11].sum() for s in 'MF')
    Z0 = {s: np.zeros(NA) for s in 'MF'}
    def births_for(M):
        if births == 'hill': return {t: hill.births_m[t] for t in FY}
        if births == 'official': return {t: 0.5 * (b_all[t] + b_all[t + 1]) for t in FY}
        if births == 'own1982':
            M2 = {s: np.concatenate([M[s][:, :yi[1965]], MX[s][:, yi[1965]:]], axis=1) for s in 'MF'}
            return backproject_births(c82(mil82), 1982, M2, FY)
        if births == 'own1964': return backproject_births(T64, 1964, M, FY)
    def bisect(fun, target, lo=-0.95, hi=10.0):
        for _ in range(45):
            mid = (lo + hi) / 2
            if fun(mid) > target: lo = mid
            else: hi = mid
        return (lo + hi) / 2
    if fixed_k is not None: k_ad, k_ch = fixed_k
    else:
        k_ad = bisect(lambda k: sum(project(P0, {}, Mk(k, 1.0), 1953, 1964)[0][s][11:].sum() for s in 'MF'), tgt_ad)
        if k_child == -99: k_ch = k_ad
        elif k_child is not None: k_ch = k_child
        elif births in ('hill', 'official'):
            B_ = births_for(None)
            k_ch = bisect(lambda k: sum(project(Z0, B_, Mk(k_ad, k), 1953, 1964)[0][s].sum() for s in 'MF'), tgt_ch, hi=30.0)
        else: k_ch = 1.0
    M = Mk(k_ad, k_ch); B = births_for(M)
    Pold, rold = project(P0, {}, M, 1953, 1964, Mexp=N)
    Pnew, rnew = project(Z0, B, M, 1953, 1964, Mexp=N)
    rec = rold[['fy']].copy()
    rec['deaths_old'] = rold.deaths; rec['exp_old'] = rold.expected
    rec['deaths_new'] = rnew.deaths; rec['exp_new'] = rnew.expected; rec['births'] = rnew.births
    rec['excess_old'] = rec.deaths_old - rec.exp_old; rec['excess_new'] = rec.deaths_new - rec.exp_new
    rec['excess'] = rec.excess_old + rec.excess_new
    P = {s: Pold[s] + Pnew[s] for s in 'MF'}
    Pcf = {s: project(P0, B, N, 1953, 1964)[0][s] for s in 'MF'}
    f58 = rec.fy.between(1958, 1962); f61 = rec.fy.between(1958, 1961)
    res = dict(k_adult=k_ad, k_child=k_ch, births_FY53_63=sum(B.values()),
               deaths_FY53_63=float(rec.deaths_old.sum() + rec.deaths_new.sum()),
               implied_deaths_P53_plus_B_minus_P64=sum(P0[s].sum() for s in 'MF') + sum(B.values()) - sum(T64[s].sum() for s in 'MF'),
               expected_FY53_63=float(rec.exp_old.sum() + rec.exp_new.sum()),
               excess_FY58_62=float(rec[f58].excess.sum()), excess_FY58_61=float(rec[f61].excess.sum()),
               excess_old_FY58_62=float(rec[f58].excess_old.sum()), excess_new_FY58_62=float(rec[f58].excess_new.sum()),
               cf_pop_gap_1964=sum(Pcf[s].sum() for s in 'MF') - sum(T64[s].sum() for s in 'MF'),
               fit_adult=sum(P[s][11:].sum() for s in 'MF') - tgt_ad, fit_child=sum(P[s][:11].sum() for s in 'MF') - tgt_ch)
    return res, rec, B, P, Pcf

central, rec_c, B_c, P_c, Pcf_c = run()
out['central'] = central
rec_c.to_csv(f'{R}/04_central_cc_by_fy.csv', index=False)

# WPP actual mortality, unadjusted (k=1): how well does UN mortality reproduce 1964 census?
wppchk, rec_w, _, P_w, _ = run(fixed_k=(1.0, 1.0))
out['wpp_k1'] = wppchk

# ---------------------------------------------------------------- 5. Zhihu check: 40+ gap in 1964
def gap40(init='V1', nscale=1.0, anchors=(1957, 1963), age_shift=0, mx_override=None):
    N = mx_override or {s: normal_mx(MX[s], *anchors, scale=nscale) for s in 'MF'}
    P0 = init53(init, 0.0, age_shift); P, _ = project(P0, {}, N, 1953, 1964)
    T = c64(0.0, age_shift)
    return sum(P[s][40:].sum() - T[s][40:].sum() for s in 'MF'), sum(P[s][40:].sum() for s in 'MF'), sum(T[s][40:].sum() for s in 'MF')
# e0 helper
def e0(m):
    l = 1.0; e = 0.0
    for x in range(85):
        q = m[x] / (1 + 0.5 * m[x]) if x else m[0] / (1 + 0.7 * m[0])
        Lx = l * (1 - (0.5 if x else 0.7) * q); e += Lx; l *= (1 - q)
    return e + l / m[85]
zrows = []
for nm, kw in [('V1 scaled to 582.6, WPP normal mx', dict(init='V1')),
               ('V2 (missing males 18-35), WPP normal', dict(init='V2')),
               ('V3 unscaled 567.4, WPP normal', dict(init='V3')),
               ('V4 scaled to NBS 594.35, WPP normal', dict(init='V4')),
               ('V1, normal mx x0.85', dict(init='V1', nscale=0.85)),
               ('V1, normal mx x0.70', dict(init='V1', nscale=0.70)),
               ('V1, normal mx x0.55 (~registration-level, e0~?)', dict(init='V1', nscale=0.55)),
               ('V4, normal mx x0.55', dict(init='V4', nscale=0.55)),
               ('V1, ages50+ overstated 1yr', dict(init='V1', age_shift=1)),
               ('V1, WPP2024 actual mx (with famine)', dict(init='V1', mx_override=MX))]:
    g, p, t = gap40(**kw)
    sc = kw.get('nscale', 1.0)
    zrows.append(dict(variant=nm, projected_40plus_1964=p, census_40plus_1964=t, gap=g,
                      e0_female_1957_normal=e0(MX['F'][:, yi[1957]] * sc), e0_female_1963_normal=e0(MX['F'][:, yi[1963]] * sc)))
# gap by 1964 age band under central normal mortality (V2)
Nn = {s: normal_mx(MX[s]) for s in 'MF'}
Pn, _ = project(init53('V2'), {}, Nn, 1953, 1964); T = c64()
for lo, hi in [(11, 19), (20, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 85)]:
    zrows.append(dict(variant=f'V2 WPP-normal, 1964 ages {lo}-{hi}', projected_40plus_1964=sum(Pn[s][lo:hi+1].sum() for s in 'MF'),
                      census_40plus_1964=sum(T[s][lo:hi+1].sum() for s in 'MF'),
                      gap=sum(Pn[s][lo:hi+1].sum() - T[s][lo:hi+1].sum() for s in 'MF')))
Z = pd.DataFrame(zrows).round(2); Z.to_csv(f'{R}/05_zhihu_40plus_gap.csv', index=False)

# ---------------------------------------------------------------- 6. births: back-projection & lost births
Mc = None
Ncent = {s: normal_mx(MX[s]) for s in 'MF'}
Fc = {s: famine_shape(MX[s], Ncent[s]) for s in 'MF'}
def Mk_c(k_ad, k_ch):
    o = {}
    for s in 'MF':
        kk = np.full((NA, 1), k_ad); kk[:11] = k_ch; o[s] = Ncent[s] * (1 + kk * Fc[s])
    return o
Mcal = Mk_c(central['k_adult'], central['k_child'])
Mcal82 = {s: np.concatenate([Mcal[s][:, :yi[1965]], MX[s][:, yi[1965]:]], axis=1) for s in 'MF'}
FYB = range(1950, 1967)
b82 = backproject_births(c82(True), 1982, Mcal82, FYB)
b64 = backproject_births(c64(), 1964, Mcal, range(1953, 1964))
bw = backproject_births(c82(True), 1982, {s: MX[s] for s in 'MF'}, FYB)
bt = pd.DataFrame({'fy': list(FYB)})
bt['births_own_1982census_calibrated_mx'] = bt.fy.map(b82)
bt['births_own_1982census_WPPmx'] = bt.fy.map(bw)
bt['births_own_1964census_calibrated_mx'] = bt.fy.map(b64)
bt['births_hill1988'] = bt.fy.map(hill.births_m)
bt['births_official_FY'] = bt.fy.map(lambda t: 0.5 * (b_all.get(t, np.nan) + b_all.get(t + 1, np.nan)))
bt['births_wpp2024_FY'] = bt.fy.map(lambda t: 0.5 * (w24.births.get(t, np.nan) + w24.births.get(t + 1, np.nan)) / 1000)
# mid-FY population (official interpolation: year-end t)
bt['pop_midFY_official'] = bt.fy.map(lambda t: offall.P.get(t, np.nan))
bt['cbr_own'] = 1000 * bt.births_own_1982census_calibrated_mx / bt.pop_midFY_official
bt.round(3).to_csv(f'{R}/06_births_by_fy.csv', index=False)
pre = bt[bt.fy.between(1954, 1957)].cbr_own.mean()
post = bt[bt.fy.between(1964, 1965)].cbr_own.mean()
lb = []
for nm, base in [('flat pre-famine CBR (FY1954-57 mean)', lambda t: pre),
                 ('linear FY1957 -> FY1964-65 mean', lambda t: lin(t, 1957, pre, 1964.5, post))]:
    cf = bt.fy.map(base) * bt.pop_midFY_official / 1000
    d = cf - bt.births_own_1982census_calibrated_mx
    lb.append(dict(baseline=nm, gross_deficit_FY1958_61=float(d[bt.fy.between(1958, 1961)].sum()),
                   net_FY1958_64=float(d[bt.fy.between(1958, 1963)].sum())))
LB = pd.DataFrame(lb).round(2); LB.to_csv(f'{R}/07_lost_births.csv', index=False)

# ---------------------------------------------------------------- 7. intercensal balancing (model B) across birth series
rowsB = []
Dreg = window_sum(d_all, 1953, 1964)
for bname, bkey in [('official registered', 'official'), ('Hill 1988 (1982 fertility survey)', 'hill'),
                    ('own: 1982 census back-projection', 'own1982'), ('own: 1964 census back-projection', 'own1964')]:
    for p53n, ini in [('582.6 mainland (V2)', 'V2'), ('594.35 NBS incl. overseas (V4)', 'V4')]:
        r = run(init=ini, births=bkey)[0]
        rowsB.append(dict(births_series=bname, P1953=p53n, births_53_64=r['births_FY53_63'],
                          implied_deaths=r['implied_deaths_P53_plus_B_minus_P64'], registered_deaths=Dreg,
                          implied_minus_registered=r['implied_deaths_P53_plus_B_minus_P64'] - Dreg,
                          normal_deaths_expected=r['expected_FY53_63'],
                          excess_implied_minus_normal=r['implied_deaths_P53_plus_B_minus_P64'] - r['expected_FY53_63'],
                          excess_cc_FY58_62=r['excess_FY58_62'], k_adult=r['k_adult'], k_child=r['k_child'],
                          child_fit_residual=r['fit_child']))
B_ = pd.DataFrame(rowsB); B_.round(2).to_csv(f'{R}/08_modelB_intercensal_balancing.csv', index=False)

# ---------------------------------------------------------------- 8. sensitivity
sens = []
def add(name, **kw):
    r = run(**kw)[0]; sens.append(dict(scenario=name, **{k: r[k] for k in ['excess_FY58_62', 'excess_FY58_61', 'excess_old_FY58_62', 'excess_new_FY58_62', 'cf_pop_gap_1964', 'births_FY53_63', 'k_adult', 'k_child', 'fit_child']}))
add('central (V2, own1982 births, WPP-normal 1957/63, no coverage adj)')
for c in (-0.02, -0.01, 0.01, 0.02): add(f'1953 census true pop = census x {1+c:.2f}', cov53=c)
for c in (-0.02, -0.01, 0.01, 0.02, 0.0275): add(f'1964 census true pop = census x {1+c:.4g}', cov64=c)
add('1953 & 1964 both +1% (equal undercount)', cov53=0.01, cov64=0.01)
add('1953 init V1 (proportional to 582.6)', init='V1')
add('1953 init V3 (age-classified 567.4 only)', init='V3')
add('1953 init V4 (NBS 594.35 incl. overseas Chinese)', init='V4')
add('births: Hill 1988', births='hill')
add('births: official registered', births='official')
add('births: own 1964 back-projection', births='own1964')
add('births: 1982 without military allocation', mil82=False)
add('normal mortality x0.85', nscale=0.85)
add('normal mortality x1.15', nscale=1.15)
add('normal anchors 1956/1964', anchors=(1956, 1964))
add('normal anchors 1957/1965', anchors=(1957, 1965))
add('child famine mortality k=0.5 x WPP shape', k_child=0.5)
add('child famine mortality k=2 x WPP shape', k_child=2.0)
add('child k = calibrated adult k', k_child=-99)
add('ages 50+ overstated by 1 yr in both censuses', age_shift=1)
S = pd.DataFrame(sens).round(2); S.to_csv(f'{R}/09_sensitivity.csv', index=False)

# ---------------------------------------------------------------- 9. control period 1964->1982 cohort check (ages 18+ in 1982)
P0 = c64(); Pp, _ = project(P0, {}, {s: MX[s] for s in 'MF'}, 1964, 1982)
T82 = c82(True)
ctrl = dict(projected_18plus_1982=sum(Pp[s][18:].sum() for s in 'MF'), census_18plus_1982=sum(T82[s][18:].sum() for s in 'MF'))
ctrl['gap'] = ctrl['projected_18plus_1982'] - ctrl['census_18plus_1982']
out['control_1964_82'] = ctrl
json.dump(out, open(f'{R}/summary.json', 'w'), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
print(A.to_string()); print(Z.to_string()); print(bt.round(2).to_string()); print(LB.to_string()); print(B_.round(2).to_string()); print(S.to_string())
print(rec_c.round(3).to_string())
