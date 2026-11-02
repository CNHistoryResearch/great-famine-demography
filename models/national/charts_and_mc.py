"""Charts + Monte Carlo uncertainty. Run after famine_model.py:  python3 -I charts_and_mc.py"""
import os, io, contextlib, runpy, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, 'results'); C = os.path.join(HERE, 'charts')
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(os.path.join(HERE, 'famine_model.py'))
run, project, init53, c64, MX, normal_mx, famine_shape, NA = g['run'], g['project'], g['init53'], g['c64'], g['MX'], g['normal_mx'], g['famine_shape'], g['NA']
off, w24, hill, central = g['off'], g['w24'], g['hill'], g['central']
COL = dict(blue='#2a78d6', orange='#eb6834', aqua='#1baf7a', yellow='#eda100', magenta='#e87ba4', green='#008300', violet='#6250d6', red='#e34948')
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'xtick.color': INK2, 'ytick.color': INK2,
                     'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6,
                     'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb', 'lines.linewidth': 2})

# ---- central calibrated mortality, annual population for model CDR
N = {s: normal_mx(MX[s]) for s in 'MF'}; F = {s: famine_shape(MX[s], N[s]) for s in 'MF'}
def Mk(ka, kc):
    o = {}
    for s in 'MF':
        kk = np.full((NA, 1), ka); kk[:11] = kc; o[s] = N[s] * (1 + kk * F[s])
    return o
res, rec, B, P64m, Pcf = run()
M = Mk(res['k_adult'], res['k_child'])
P = init53('V2'); pops = [sum(P[s].sum() for s in 'MF')]
Pn = init53('V2'); popn = [pops[0]]; dn = []
for t in range(1953, 1964):
    P, r = project(P, {t: B[t]}, M, t, t + 1); pops.append(sum(P[s].sum() for s in 'MF'))
    Pn, rn = project(Pn, {t: B[t]}, N, t, t + 1); popn.append(sum(Pn[s].sum() for s in 'MF')); dn.append(rn.deaths.iloc[0])
rec['pop_mid_fy'] = [(pops[i] + pops[i + 1]) / 2 for i in range(11)]
rec['cdr_model'] = 1000 * (rec.deaths_old + rec.deaths_new) / rec.pop_mid_fy
rec['cdr_normal_cf'] = [1000 * dn[i] / ((popn[i] + popn[i + 1]) / 2) for i in range(11)]
rec['cbr_model'] = 1000 * rec.births / rec.pop_mid_fy
rec.round(3).to_csv(f'{R}/10_model_annual_fy.csv', index=False)

# ---- chart 1: CDR
fig, ax = plt.subplots(figsize=(9, 5))
yrs = np.arange(1950, 1971)
ax.plot(yrs + 0.5, off.cdr.loc[1950:1970], color=COL['blue'], marker='o', ms=4, label='Official NBS (registered), calendar yr')
ax.plot(yrs + 0.5, w24.cdr.loc[1950:1970], color=COL['orange'], marker='s', ms=4, label='UN WPP2024, calendar yr')
ax.plot(hill.index + 1, hill.cdr, color=COL['violet'], marker='^', ms=5, label='Hill 1988 reconstruction, mid-yr to mid-yr')
ax.plot(rec.fy + 1, rec.cdr_model, color=COL['red'], marker='D', ms=5, label='This model (census-calibrated), mid-yr to mid-yr')
ax.plot(rec.fy + 1, rec.cdr_normal_cf, color=COL['aqua'], ls='--', label='This model: no-famine counterfactual')
ax.set_ylabel('Crude death rate (per 1,000)'); ax.set_xlabel('Year (points at mid-period)')
ax.set_title('China crude death rate 1950-1970: registered vs reconstructed', loc='left', color=INK)
ax.legend(frameon=False, fontsize=8.5, loc='upper right'); ax.set_xlim(1950, 1971.5)
fig.tight_layout(); fig.savefig(f'{C}/01_cdr_official_vs_modeled.png', dpi=150); plt.close(fig)

# ---- chart 2: intercensal accounting
Bm = pd.read_csv(f'{R}/08_modelB_intercensal_balancing.csv'); Bm = Bm[Bm.P1953.str.startswith('582')]
fig, ax = plt.subplots(figsize=(9, 4.5))
lab = ['Official registered\nbirths', 'Hill 1988\n(1982 fert. survey)', 'Own: 1982 census\nback-projection', 'Own: 1964 census\nback-projection']
x = np.arange(len(Bm))
ax.bar(x - 0.2, Bm.registered_deaths, 0.38, color=COL['blue'], label='Registered deaths (official CDR), mid-1953 to mid-1964')
ax.bar(x + 0.2, Bm.normal_deaths_expected, 0.38, color=COL['aqua'], label='Normal (no-famine) deaths, model')
ax.bar(x + 0.2, Bm.excess_implied_minus_normal.clip(lower=0), 0.38, bottom=Bm.normal_deaths_expected, color=COL['red'], label='Excess = implied - normal')
for i, (imp, ex) in enumerate(zip(Bm.implied_deaths, Bm.excess_implied_minus_normal)):
    ax.text(i + 0.2, max(imp, Bm.normal_deaths_expected.iloc[i]) + 2, f'implied {imp:.0f}M\nexcess {ex:+.0f}M', ha='center', fontsize=8.5, color=INK)
ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=8.5); ax.set_ylabel('Deaths, millions (1953.5-1964.5)')
ax.set_title('Intercensal balancing: deaths implied by P1953 + births - P1964, by birth series', loc='left', color=INK, fontsize=10.5)
ax.set_ylim(0, 200); ax.legend(frameon=False, fontsize=8, loc='upper left')
fig.tight_layout(); fig.savefig(f'{C}/02_intercensal_accounting.png', dpi=150); plt.close(fig)

# ---- chart 3: tornado
S = pd.read_csv(f'{R}/09_sensitivity.csv'); base = S.excess_FY58_62.iloc[0]; get = lambda n: float(S[S.scenario == n].excess_FY58_62.iloc[0])
pairs = [('1953 census coverage +/-1%', '1953 census true pop = census x 0.99', '1953 census true pop = census x 1.01'),
         ('1964 census coverage +/-1%', '1964 census true pop = census x 1.01', '1964 census true pop = census x 0.99'),
         ('Normal mortality level x1.15 / x0.85', 'normal mortality x1.15', 'normal mortality x0.85'),
         ('Child famine mortality k=0.5 / k=2 (WPP shape)', 'child famine mortality k=0.5 x WPP shape', 'child famine mortality k=2 x WPP shape'),
         ('1953 start: age-classified only / NBS 594.35', '1953 init V3 (age-classified 567.4 only)', '1953 init V4 (NBS 594.35 incl. overseas Chinese)'),
         ('Births: Hill 1988 / own 1964 back-proj.', 'births: own 1964 back-projection', 'births: Hill 1988'),
         ('Old-age overstatement 0 / 1 yr', 'central (V2, own1982 births, WPP-normal 1957/63, no coverage adj)', 'ages 50+ overstated by 1 yr in both censuses'),
         ('Normal-mortality anchors 1957/63 vs 1957/65', 'central (V2, own1982 births, WPP-normal 1957/63, no coverage adj)', 'normal anchors 1957/1965')]
rows = sorted([(n, get(a), get(b)) for n, a, b in pairs], key=lambda r: abs(r[2] - r[1]))
fig, ax = plt.subplots(figsize=(9, 4.8))
for i, (n, lo, hi) in enumerate(rows):
    ax.barh(i, lo - base, left=base, color=COL['blue'], height=0.55); ax.barh(i, hi - base, left=base, color=COL['orange'], height=0.55)
    ax.text(min(lo, hi) - 0.4, i, f'{min(lo, hi):.1f}', va='center', ha='right', fontsize=8, color=INK2)
    ax.text(max(lo, hi) + 0.4, i, f'{max(lo, hi):.1f}', va='center', ha='left', fontsize=8, color=INK2)
ax.axvline(base, color=INK, lw=1); ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
ax.set_xlabel('Excess deaths mid-1958 to mid-1963 (millions)'); ax.set_xlim(8, 56)
ax.set_title(f'Sensitivity of excess deaths (central {base:.1f}M); blue = first option, orange = second', loc='left', color=INK, fontsize=10)
fig.tight_layout(); fig.savefig(f'{C}/03_sensitivity_tornado.png', dpi=150); plt.close(fig)

# ---- chart 4: 1964 age structure
T = c64(); Pnorm, _ = project(init53('V2'), B, N, 1953, 1964); Pw, _ = project(init53('V2'), B, {s: MX[s] for s in 'MF'}, 1953, 1964)
ages = np.arange(86); tot = lambda P: P['M'] + P['F']
fig, axs = plt.subplots(2, 1, figsize=(9, 7), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
axs[0].plot(ages[:85], tot(T)[:85], color=COL['blue'], label='1964 census')
axs[0].plot(ages[:85], tot(Pnorm)[:85], color=COL['aqua'], ls='--', label='1953 census projected with no-famine mortality (own births)')
axs[0].plot(ages[:85], tot(Pw)[:85], color=COL['orange'], label='1953 census projected with UN WPP2024 mortality (incl. famine)')
axs[0].set_ylabel('Persons (millions) by single age'); axs[0].legend(frameon=False, fontsize=8.5)
axs[0].set_title('1964 age structure: census vs projections from the 1953 census (ages 0-84)', loc='left', color=INK, fontsize=10.5)
axs[1].bar(ages[:85], (tot(Pnorm) - tot(T))[:85], color=COL['red'], width=0.8)
axs[1].axhline(0, color=INK, lw=0.8); axs[1].set_ylabel('No-famine projection\nminus census (M)'); axs[1].set_xlabel('Age in 1964')
fig.tight_layout(); fig.savefig(f'{C}/04_age_structure_1964.png', dpi=150); plt.close(fig)

# ---- chart 5: births
bt = pd.read_csv(f'{R}/06_births_by_fy.csv')
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(bt.fy + 1, bt.births_official_FY, color=COL['blue'], marker='o', ms=4, label='Official registered (CBR x pop)')
ax.plot(bt.fy + 1, bt.births_hill1988, color=COL['violet'], marker='^', ms=5, label='Hill 1988 (1982 1-per-1000 fertility survey)')
ax.plot(bt.fy + 1, bt.births_own_1982census_calibrated_mx, color=COL['red'], marker='D', ms=4, label='Own: 1982 census back-projection')
ax.plot(bt.fy + 1, bt.births_wpp2024_FY, color=COL['orange'], marker='s', ms=4, label='UN WPP2024')
ax.set_ylabel('Births per year (millions)'); ax.set_xlabel('Year (end of mid-yr to mid-yr period)')
ax.set_title('Births 1950-1966: registered vs reconstructed', loc='left', color=INK); ax.legend(frameon=False, fontsize=8.5)
fig.tight_layout(); fig.savefig(f'{C}/05_births.png', dpi=150); plt.close(fig)

# ---- Monte Carlo
rng = np.random.default_rng(20261101); draws = []
NDR = int(os.environ.get('NDRAWS', 300))
for i in range(NDR):
    kw = dict(cov53=float(rng.normal(0, 0.01)), cov64=float(rng.normal(0, 0.01)), nscale=float(np.exp(rng.normal(0, 0.08))),
              k_child=float(np.exp(rng.normal(0, 0.35))), init=str(rng.choice(['V1', 'V2'])), age_shift=int(rng.choice([0, 1])),
              births=str(rng.choice(['own1982', 'own1964'])))
    r = run(**kw)[0]; draws.append(dict(**kw, **{k: r[k] for k in ['excess_FY58_62', 'excess_FY58_61', 'excess_old_FY58_62', 'excess_new_FY58_62']}))
MCd = pd.DataFrame(draws); MCd.to_csv(f'{R}/11_monte_carlo_draws.csv', index=False)
q = MCd.excess_FY58_62.quantile([0.05, 0.25, 0.5, 0.75, 0.95])
summ = {'median': q[0.5], 'p05': q[0.05], 'p25': q[0.25], 'p75': q[0.75], 'p95': q[0.95], 'mean': MCd.excess_FY58_62.mean(),
        'corr_with_excess': MCd[['cov53', 'cov64', 'nscale', 'k_child', 'age_shift', 'excess_FY58_62']].corr()['excess_FY58_62'].round(2).to_dict()}
json.dump(summ, open(f'{R}/11_monte_carlo_summary.json', 'w'), indent=1, default=float)
print(json.dumps(summ, indent=1, default=float)); print(rec.round(2).to_string())
