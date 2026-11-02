# Excess deaths by age/sex in China 1958-1962 implied by UN WPP 2022 single-year estimates
# Data: github.com/PPgp/wpp2022 (mx1dt.rda, popAge1dt.rda). Baseline: log-linear interpolation of mx between 1957 and 1964 (alt: 1957 & 1963).
import sys, pyreadr, numpy as np, pandas as pd
d = sys.argv[1]
mx = pyreadr.read_r(d+'/mx1dt.rda')['mx1dt']; pop = pyreadr.read_r(d+'/popAge1dt.rda')['popAge1dt']
mx = mx[mx.country_code==156]; pop = pop[pop.country_code==156]
mx = mx[(mx.year>=1950)&(mx.year<=1970)]; pop = pop[(pop.year>=1950)&(pop.year<=1971)]
# WPP pop is at 1 July (popAge1dt year t) ; mid-year pop * mx = deaths
m = mx.merge(pop, on=['country_code','year','age'])
m['DM']=m.mxM*m.popM; m['DF']=m.mxF*m.popF
def grp(a):
    return '0' if a==0 else '1-4' if a<5 else '5-14' if a<15 else '15-39' if a<40 else '40-59' if a<60 else '60+'
m['g']=m.age.apply(grp)
order=['0','1-4','5-14','15-39','40-59','60+']
for base in [(1957,1964),(1957,1963)]:
    b0,b1=base
    out=[]
    for y in range(1958,1963):
        w=(y-b0)/(b1-b0)
        sub=m[m.year==y].set_index('age')
        lo=m[m.year==b0].set_index('age'); hi=m[m.year==b1].set_index('age')
        for s in 'MF':
            bm=np.exp((1-w)*np.log(lo['mx'+s])+w*np.log(hi['mx'+s]))
            exc=(sub['mx'+s]-bm)*sub['pop'+s]
            df=pd.DataFrame({'exc':exc,'g':sub.g,'obs':sub['D'+s],'pop':sub['pop'+s]})
            for g,r in df.groupby('g'): out.append((y,s,g,r.exc.sum(),r.obs.sum(),r['pop'].sum()))
    o=pd.DataFrame(out,columns=['year','sex','grp','excess','deaths','pop'])
    print(f'\n=== baseline log-linear {b0}->{b1}; units thousands ===')
    t=o.pivot_table(index='grp',columns='year',values='excess',aggfunc='sum').reindex(order)
    t['1958-62']=t.sum(axis=1); t['share%']=100*t['1958-62']/t['1958-62'].sum()
    print(t.round(0)); print('total excess', round(t['1958-62'].sum()))
    s=o.groupby('sex').excess.sum(); print('by sex',s.round(0).to_dict(), 'male share %.1f'%(100*s.M/s.sum()))
    # 40+ share
    print('40+ share %.1f%%'%(100*o[o.grp.isin(['40-59','60+'])].excess.sum()/o.excess.sum()), ' under5 share %.1f%%'%(100*o[o.grp.isin(['0','1-4'])].excess.sum()/o.excess.sum()))
# rate ratios by age group 1960 vs 1957
print('\n=== death rates per 1000 by group, both sexes ===')
r=m.groupby(['year','g'])[['DM','DF','popM','popF']].sum()
r['rate']=1000*(r.DM+r.DF)/(r.popM+r.popF)
print(r.rate.unstack().reindex(columns=order).loc[1955:1966].round(1))
print('\n=== single-age mx (per 1000), males, ages 0,1,40,60,70 ===')
print((1000*m[m.age.isin([0,1,2,40,60,70])].pivot(index='year',columns='age',values='mxM')).loc[1955:1966].round(2))
# CDR, total deaths, births proxy
tot=m.groupby('year')[['DM','DF','popM','popF']].sum(); tot['CDR']=1000*(tot.DM+tot.DF)/(tot.popM+tot.popF); tot['D']=(tot.DM+tot.DF)/1000
print(tot[['CDR','D']].loc[1955:1966].round(2))
# population 40+ in 1960 and avg mortality
p=m[m.year==1960]; a=p[p.age>=40]; print('pop40+ 1960 (M):',round((a.popM.sum()+a.popF.sum())/1000,1),'share',round((a.popM.sum()+a.popF.sum())/(p.popM.sum()+p.popF.sum()),3))
for y in [1957,1960,1964]:
    a=m[(m.year==y)&(m.age>=40)]; print(y,'40+ crude death rate per 1000', round(1000*(a.DM.sum()+a.DF.sum())/(a.popM.sum()+a.popF.sum()),1))
# cohort sizes age0 by year (births proxy)
print('\nage0 pop (thous) 1955-1966:', m[m.age==0].set_index('year').eval('popM+popF').loc[1955:1966].round(0).to_dict())
