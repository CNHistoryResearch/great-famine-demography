# Arithmetic checks for the age/cohort/urban-rural note. Inputs cited inline.
import sys, pyreadr, numpy as np, pandas as pd
d=sys.argv[1]
mx=pyreadr.read_r(d+'/mx1dt.rda')['mx1dt']; pop=pyreadr.read_r(d+'/popAge1dt.rda')['popAge1dt']
mx=mx[mx.country_code==156]; pop=pop[pop.country_code==156]
m=mx.merge(pop,on=['country_code','year','age'])
def M(y,s='B'): return m[m.year==y].set_index('age')['mx'+s]
def P(y,s=''): t=m[m.year==y].set_index('age'); return t.popM+t.popF if s=='' else t['pop'+s]
print('--- (A) urban/rural split, official CDR by city/county (Lin & Yang 2000 Table 2 from SSB Yearbook 1991) ---')
cdr={1957:(10.80,8.47,11.07,15.4),1958:(11.98,9.22,12.50,16.2),1959:(14.59,10.92,14.61,18.4),1960:(25.43,13.77,28.58,19.7),1961:(14.24,11.39,14.58,19.3),1962:(10.02,8.28,10.32,17.3),1963:(10.04,7.13,10.49,16.8)}
popn={1957:646.5,1958:659.9,1959:672.1,1960:662.1,1961:658.6,1962:672.9,1963:691.7}  # official year-end pop (Ashton et al. appendix / Hill 1988 Table 1)
ex_c=ex_r=0
for y in [1958,1959,1960,1961]:
    nat,c,r,sh=cdr[y]; pc=popn[y]*sh/100; pr=popn[y]-pc
    bc=(cdr[1957][1]+cdr[1962][1])/2; br=(cdr[1957][2]+cdr[1962][2])/2   # baseline = mean of 1957 & 1962
    ec=(c-bc)*pc/1000; er=(r-br)*pr/1000; ex_c+=ec; ex_r+=er
    print(y,f'city deaths {c*pc/1000:.2f}M rural deaths {r*pr/1000:.2f}M rural share of all deaths {r*pr/(r*pr+c*pc):.1%}; excess city {ec:.2f}M rural {er:.2f}M')
print(f'official-data excess 1958-61: city {ex_c:.2f}M rural {ex_r:.2f}M rural share {ex_r/(ex_r+ex_c):.1%}; ratio 1960/1957 city {13.77/8.47:.2f}x rural {28.58/11.07:.2f}x')
print('\n--- (B) Zhihu claim 2: "40+ mortality must rise ~7x" ---')
p60=P(1960); a40=p60[p60.index>=40].sum()/1000; tot=p60.sum()/1000
print(f'WPP2022 pop 1960 total {tot:.0f}M, 40+ {a40:.1f}M ({a40/tot:.1%})')
for lbl,base in [('WPP 1957 age-specific rates',(M(1957)*P(1957))[P(1957).index>=40].sum()/P(1957)[P(1957).index>=40].sum()),('official CDR 10.8 applied flat',0.0108)]:
    b=base*a40; print(f' {lbl}: baseline 40+ deaths/yr {b:.2f}M (rate {1000*base:.1f}/1000); +10M/yr excess => ratio {(b+10)/b:.1f}x')
# share of normal deaths at 40+ under WPP 1957 rates
D=M(1957)*P(1957); print(f' WPP 1957: share of all deaths at 40+ = {D[D.index>=40].sum()/D.sum():.1%}; if total normal deaths 7M (poster), 40+ normal deaths={7*D[D.index>=40].sum()/D.sum():.2f}M -> ratio {(7*D[D.index>=40].sum()/D.sum()+10)/(7*D[D.index>=40].sum()/D.sum()):.1f}x')
print(f' poster implicit: 7M * 40+ pop share {a40/tot:.3f} = {7*a40/tot:.2f}M -> ratio {(7*a40/tot+10)/(7*a40/tot):.1f}x')
# simulate 7x on all 40+ age-specific rates for 1959-61 with depletion, WPP 1957 rates
for mult in [7,3]:
    for s in 'MF':
        pass
    popv=P(1959).copy().astype(float); base=M(1957).copy(); exc=0; 
    for y in range(3):
        mm=base.copy(); mm[mm.index>=40]*=mult
        q=1-np.exp(-mm); dd=popv*q; db=popv*(1-np.exp(-base)); exc+=(dd-db)[dd.index>=40].sum()
        popv=(popv-dd).shift(1).fillna(0)
    print(f' if ALL 40+ age-specific rates x{mult} for 3 yrs (WPP 1957 base): excess 40+ deaths ~{exc/1000:.0f}M; annual death prob at age 70 -> {1-np.exp(-mult*base[70]):.0%}')
print('\n--- (C) WPP2022 life expectancy & m(40) ---')
def e0(r):
    r=r.values; q=1-np.exp(-r); l=np.concatenate([[1],np.cumprod(1-q)[:-1]]); L=l*(1-q/2); return L.sum()
for y in [1957,1958,1959,1960,1961,1962,1963,1964,1981]:
    print(y, 'e0 M %.1f F %.1f B %.1f'%(e0(M(y,'M')),e0(M(y,'F')),e0(M(y,'B'))), ' male m40 %.2f/1000'%(1000*M(y,'M')[40]), ' male 1-yr q40 %.2f/1000'%(1000*(1-np.exp(-M(y,'M')[40]))))
print('\n--- (D) spurious 40+ gap from death under-registration (claim 1) ---')
# deaths 1953-1963 among cohorts aged 29+ in 1953 (40+ in 1964) under NON-famine WPP mortality (1957 rates for 1958-63 to strip famine)
tot_d=0
for y in range(1953,1964):
    yy=y if y<1958 else 1957
    r=M(yy); p=P(y); ages=p.index>=(29+(y-1953)); tot_d+=(r*p)[ages].sum()
print(f' non-famine deaths 1953-64 in cohorts that are 40+ in 1964: {tot_d/1000:.1f}M')
for comp in [0.805,0.7,0.62]:
    print(f'  if registration completeness {comp:.0%} => registered-life-table counterfactual overstates survivors by ~{tot_d/1000*(1-comp):.1f}M')
print('\n--- (E) Hill 1988 Table 8 (deaths under 10 / 10+, thousands, fiscal years) ---')
u10=[5193,8691,6491,3263,7062,3197,3825]; o10=[7045,7182,14877,15903,6727,6875,7908]
for name,base in [('1957-58 flat',lambda s,i: s[0]),('linear 1957-58->1963-64',lambda s,i: s[0]+(s[6]-s[0])*i/6)]:
    eu=sum(u10[i]-base(u10,i) for i in range(1,5)); eo=sum(o10[i]-base(o10,i) for i in range(1,5))
    print(f' baseline {name}: excess FY58/59-61/62 under10 {eu/1000:.1f}M, 10+ {eo/1000:.1f}M, total {(eu+eo)/1000:.1f}M, under10 share {eu/(eu+eo):.0%}')
print('\n--- (F) births: Hill 1988 Table 2 reconstructed births (M), fiscal years ---')
P0=[633.7,647.3,653.5,651.0,646.6,653.7,677.4]; B=[25.80,22.11,18.88,14.72,20.88,33.81,30.71]
for lbl,br in [('CBR 40.3 (FY57/58)',0.0403),('CBR 38',0.038)]:
    lost=sum(br*P0[i]*1.0-B[i] for i in range(1,5)); reb=sum(B[i]-br*P0[i] for i in (5,6))
    print(f' baseline {lbl}: lost births FY58/59-61/62 {lost:.1f}M; rebound surplus FY62/63-63/64 {reb:.1f}M; net {lost-reb:.1f}M')
w=m[m.age==0].set_index('year'); w=(w.popM+w.popF)/1000
print(' WPP age-0 pop (M):',w.loc[1956:1964].round(1).to_dict())
print(f' WPP: shortfall 1959-61 vs 1957 level: {3*w[1957]-w[1959]-w[1960]-w[1961]:.1f}M')
