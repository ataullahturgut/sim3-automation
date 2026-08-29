#!/usr/bin/env python3
import io, urllib.request
from pathlib import Path
import numpy as np, pandas as pd
OUT=Path('projects/gold_h1_r1')
PIN='f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0'
GOLD=f'https://raw.githubusercontent.com/simom1/XAUUSD-history/{PIN}/Gold-Cash/XAUUSD/XAUUSD_D1.csv'
def read_csv(url):
    req=urllib.request.Request(url,headers={'User-Agent':'gold-h1-r1-audit/1.0'})
    with urllib.request.urlopen(req,timeout=90) as r:return pd.read_csv(io.BytesIO(r.read()))
def fred(s):
    d=read_csv(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}')
    d.columns=['date',s]; d.date=pd.to_datetime(d.date); d[s]=pd.to_numeric(d[s],errors='coerce');return d.dropna()
g=read_csv(GOLD); g['date']=pd.to_datetime(g['time']); g=g[['date','open','high','low','close']].sort_values('date').drop_duplicates('date')
# Market-observable daily stress proxies. VIX and broad USD are same/next-day market data; real yield used only as context.
for s in ['VIXCLS','DTWEXBGS','DFII10']:
    f=fred(s); g=pd.merge_asof(g.sort_values('date'),f.sort_values('date'),on='date',direction='backward',tolerance=pd.Timedelta('7D'))
g['ret1']=g.close.pct_change(); g['ret3']=g.close.pct_change(3); g['ret5']=g.close.pct_change(5)
g['sma20']=g.close.rolling(20).mean(); g['sma50']=g.close.rolling(50).mean(); g['below20']=g.close<g.sma20; g['below50']=g.close<g.sma50
g['vix5']=g.VIXCLS/g.VIXCLS.shift(5)-1; g['usd5']=g.DTWEXBGS/g.DTWEXBGS.shift(5)-1; g['ry5']=g.DFII10-g.DFII10.shift(5)
# trailing VIX percentile, causal
v=g.VIXCLS.to_numpy(float); pct=[]
for i,x in enumerate(v):
    h=v[max(0,i-252):i]; h=h[np.isfinite(h)]; pct.append(np.nan if len(h)<126 or not np.isfinite(x) else float((h<=x).mean()))
g['vix_pct']=pct
g['month']=g.date.dt.to_period('M').astype(str); g['mtd_peak']=g.groupby('month').close.cummax(); g['mtd_dd']=g.close/g.mtd_peak-1
# monthly direction contract
m=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv');m['target']=pd.to_datetime(m.target).dt.to_period('M').astype(str)
l=pd.read_csv(OUT/'direction_locked_replay.csv');l=l[l.Target<='2026-07'];l2=pd.DataFrame({'target':l.Target,'actual_dir':l['Actual Dir'].astype(float),'dir3':l['MOM3 Dir'].astype(float),'flat':False})
m=pd.concat([m[['target','actual_dir','dir3','flat']],l2],ignore_index=True).drop_duplicates('target',keep='last')
# Only UP priors are eligible for emergency downside override.
mm=m[(m.dir3==1)&(~m.flat.astype(bool))].copy(); mm['need_override']=(mm.actual_dir==-1).astype(int)
# candidate families: price fracture alone; price fracture + stress confirmation. No 2023+ tuning.
cands=[]
for dd in [-.03,-.05,-.07]:
  for r5 in [-.02,-.04,-.06]:
    for sma in [20,50]:
      for stress in ['NONE','VIX','USD_OR_RY','VIX_OR_MACRO']:
        for stress_thr in [0.10,0.20]:
          cands.append((dd,r5,sma,stress,stress_thr))
def day_signal(df,rule):
    dd,r5,sma,stress,thr=rule
    base=(df.mtd_dd<=dd)&(df.ret5<=r5)&(df[f'below{sma}'])
    if stress=='NONE': return base
    if stress=='VIX': return base&((df.vix5>=thr)|(df.vix_pct>=.85))
    macro=(df.usd5>0)|(df.ry5>0)
    if stress=='USD_OR_RY': return base&macro
    return base&(((df.vix5>=thr)|(df.vix_pct>=.85))|macro)
def eval_rule(rule,a,b):
    x=mm[(mm.target>=a)&(mm.target<=b)].copy(); corr=dmg=trig=0; dates=[]
    for _,r in x.iterrows():
        d=g[g.month==r.target].copy(); sig=day_signal(d,rule)
        hit=bool(sig.any()); first=d.loc[sig,'date'].min() if hit else pd.NaT
        if hit: trig+=1
        if hit and r.need_override: corr+=1
        if hit and not r.need_override: dmg+=1
        dates.append(first)
    n=len(x); needs=int(x.need_override.sum()); good=n-needs
    precision=corr/trig if trig else np.nan; recall=corr/needs if needs else np.nan; false_rate=dmg/good if good else np.nan
    utility=corr-dmg
    return dict(n=n,needs=needs,triggers=trig,corrected=corr,damaged=dmg,precision=precision,recall=recall,false_rate=false_rate,utility=utility)
rows=[]
for rule in cands:
    for name,a,b in [('DEV','2010-01','2020-12'),('VAL','2021-01','2022-12'),('TEST2023','2023-01','2023-12'),('LOCK','2024-01','2026-07')]:
        z=eval_rule(rule,a,b); rows.append([*rule,name,*z.values()])
audit=pd.DataFrame(rows,columns=['dd','r5','sma','stress','stress_thr','period','n','needs','triggers','corrected','damaged','precision','recall','false_rate','utility'])
audit.to_csv(OUT/'emergency_shock_rule_audit.csv',index=False)
# Select only from DEV+VAL: non-negative DEV utility, then VAL utility, VAL precision, lower damage, earlier/simpler stress preference.
choices=[]
for key,h in audit.groupby(['dd','r5','sma','stress','stress_thr']):
    z=h.set_index('period'); dev=z.loc['DEV']; val=z.loc['VAL']
    if dev.utility>=0 and dev.precision>=0.5:
        choices.append((val.utility, val.precision if np.isfinite(val.precision) else -1, -val.damaged, dev.utility, key))
if not choices: raise RuntimeError('No eligible pre-2023 shock rule')
rule=max(choices)[-1]
# full event replay
events=[]
for _,r in mm.iterrows():
    d=g[g.month==r.target].copy(); sig=day_signal(d,rule); hit=bool(sig.any()); first=d.loc[sig,'date'].min() if hit else pd.NaT
    fr=d[d.date==first].iloc[0] if hit else None
    events.append([r.target,int(r.actual_dir),int(r.need_override),hit,first.date().isoformat() if hit else '',float(fr.mtd_dd) if hit else np.nan,float(fr.ret5) if hit else np.nan,float(fr.VIXCLS) if hit else np.nan,float(fr.vix5) if hit else np.nan,float(fr.vix_pct) if hit else np.nan,float(fr.usd5) if hit else np.nan,float(fr.ry5) if hit else np.nan])
ev=pd.DataFrame(events,columns=['target','actual_dir','need_override','trigger','trigger_date','mtd_dd','ret5','vix','vix5','vix_pct','usd5','ry5']);ev.to_csv(OUT/'emergency_shock_frozen_replay.csv',index=False)
# 2026 compact table and report
def met(a,b):
    x=ev[(ev.target>=a)&(ev.target<=b)]; corr=int((x.trigger&(x.need_override==1)).sum());dmg=int((x.trigger&(x.need_override==0)).sum());tr=int(x.trigger.sum());need=int(x.need_override.sum());return len(x),need,tr,corr,dmg,(corr/tr if tr else np.nan),(corr/need if need else np.nan)
lines=['# Emergency Shock Override R1','',f'Frozen pre-2023 rule: MTD drawdown <= {rule[0]:.1%}, 5D return <= {rule[1]:.1%}, below SMA{rule[2]}, stress={rule[3]}, stress_thr={rule[4]:.0%}.','', 'Role: intramonth emergency downside override only when monthly 3M prior is UP. It does not alter the start-of-month forecast.','']
for n,a,b in [('DEV','2010-01','2020-12'),('VAL','2021-01','2022-12'),('TEST2023','2023-01','2023-12'),('LOCK','2024-01','2026-07')]: lines.append(f'- {n}: eligible/needs/triggers/corrected/damaged/precision/recall = {met(a,b)}')
lines+=['','## 2026 Jan-Jul UP-prior months']
for _,r in ev[(ev.target>='2026-01')&(ev.target<='2026-07')].iterrows():lines.append(f"- {r.target}: actual={int(r.actual_dir):+d} need_override={int(r.need_override)} trigger={bool(r.trigger)} date={r.trigger_date or '-'} dd={r.mtd_dd:.2%} ret5={r.ret5:.2%} VIX5={r.vix5:.2%} USD5={r.usd5:.2%} RY5={r.ry5:+.3f}")
(OUT/'EMERGENCY_SHOCK_OVERRIDE_R1.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
