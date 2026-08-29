#!/usr/bin/env python3
# Bidirectional emergency shock audit. Candidate rules selected only on 2010-2022; 2023 is untouched test.
import io, urllib.request, time
from pathlib import Path
import numpy as np, pandas as pd
OUT=Path('projects/gold_h1_r1'); PIN='f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0'
GOLD=f'https://raw.githubusercontent.com/simom1/XAUUSD-history/{PIN}/Gold-Cash/XAUUSD/XAUUSD_D1.csv'
def read_csv(url):
  err=None
  for i in range(5):
    try:
      req=urllib.request.Request(url,headers={'User-Agent':'gold-h1-r1-bidir-emergency/1.0'})
      with urllib.request.urlopen(req,timeout=180) as r:return pd.read_csv(io.BytesIO(r.read()))
    except Exception as e: err=e; time.sleep(3*(i+1))
  raise err
def fred(s):
  d=read_csv(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}&cosd=2009-01-01&coed=2023-12-31'); d.columns=['date',s]; d.date=pd.to_datetime(d.date); d[s]=pd.to_numeric(d[s],errors='coerce'); return d.dropna()
g=read_csv(GOLD); g['date']=pd.to_datetime(g.time); g=g[['date','close']].sort_values('date').drop_duplicates('date')
for s in ['VIXCLS','DTWEXBGS','DFII10']:
  g=pd.merge_asof(g,fred(s),on='date',direction='backward',tolerance=pd.Timedelta('7D'))
g['ret5']=g.close.pct_change(5); g['sma50']=g.close.rolling(50).mean(); g['month']=g.date.dt.to_period('M').astype(str)
g['mtd_peak']=g.groupby('month').close.cummax(); g['mtd_trough']=g.groupby('month').close.cummin(); g['mtd_dd']=g.close/g.mtd_peak-1; g['mtd_up']=g.close/g.mtd_trough-1
g['vix5']=g.VIXCLS/g.VIXCLS.shift(5)-1; g['usd5']=g.DTWEXBGS/g.DTWEXBGS.shift(5)-1; g['ry5']=g.DFII10-g.DFII10.shift(5)
m=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv'); m['target']=pd.to_datetime(m.target).dt.to_period('M').astype(str); m=m[~m.flat.astype(bool)].copy()
# downside eligible when prior is UP; upside eligible when prior is DOWN.
def signal(d,side,move,r5,stress):
  if side=='DOWN':
    base=(d.mtd_dd<=-move)&(d.ret5<=-r5)&(d.close<d.sma50)
    macro=(d.usd5>0)|(d.ry5>0)
  else:
    base=(d.mtd_up>=move)&(d.ret5>=r5)&(d.close>d.sma50)
    # supportive gold shock context: risk spike OR weaker USD OR lower real yield
    macro=(d.usd5<0)|(d.ry5<0)
  if stress=='NONE': return base
  if stress=='MACRO': return base&macro
  if stress=='VIX_OR_MACRO': return base&((d.vix5>=.10)|macro)
  return base
cands=[(mv,r5,st) for mv in [.03,.05,.07] for r5 in [.02,.04,.06] for st in ['NONE','MACRO','VIX_OR_MACRO']]
def evaluate(side,rule,a,b):
  prior=1 if side=='DOWN' else -1; actual=-1 if side=='DOWN' else 1
  x=m[(m.target>=a)&(m.target<=b)&(m.dir3==prior)].copy(); corr=dmg=trig=0
  for _,r in x.iterrows():
    d=g[g.month==r.target]; hit=bool(signal(d,side,*rule).any()); trig+=hit; corr+=int(hit and r.actual_dir==actual); dmg+=int(hit and r.actual_dir==prior)
  need=int((x.actual_dir==actual).sum()); return len(x),need,trig,corr,dmg,(corr/trig if trig else np.nan),(corr-dmg)
def choose(side):
  rows=[]
  for rule in cands:
    dev=evaluate(side,rule,'2010-01','2020-12'); val=evaluate(side,rule,'2021-01','2022-12'); rows.append((rule,dev,val))
  eligible=[]
  for rule,dev,val in rows:
    if dev[2] and dev[5]>=.5 and dev[6]>=0: eligible.append((val[6], val[5] if np.isfinite(val[5]) else -1, -val[4], dev[6], rule))
  if not eligible: raise RuntimeError(f'no eligible {side} rule')
  return max(eligible)[-1],rows
outs=[]; frozen={}
for side in ['DOWN','UP']:
  rule,rows=choose(side); frozen[side]=rule
  for rule0,dev,val in rows:
    if rule0==rule:
      for p,a,b in [('DEV','2010-01','2020-12'),('VAL','2021-01','2022-12'),('TEST2023','2023-01','2023-12')]: outs.append([side,*rule,p,*evaluate(side,rule,a,b)])
pd.DataFrame(outs,columns=['side','move','ret5','stress','period','eligible','needs','triggers','corrected','damaged','precision','utility']).to_csv(OUT/'bidirectional_emergency_rule_audit.csv',index=False)
# untouched 2023 event replay
rows=[]
for _,r in m[(m.target>='2023-01')&(m.target<='2023-12')].iterrows():
  side='DOWN' if r.dir3==1 else ('UP' if r.dir3==-1 else '')
  if not side: continue
  d=g[g.month==r.target].copy(); sig=signal(d,side,*frozen[side]); hit=bool(sig.any()); first=d.loc[sig,'date'].min() if hit else pd.NaT
  rows.append([r.target,int(r.actual_dir),int(r.dir3),side,hit,'' if not hit else first.date().isoformat()])
ev=pd.DataFrame(rows,columns=['target','actual_dir','prior_dir','eligible_shock_side','trigger','trigger_date']); ev.to_csv(OUT/'bidirectional_emergency_2023_replay.csv',index=False)
# report
lines=['# Bidirectional Emergency Shock Audit R1','','Selection uses DEV 2010-2020 + VAL 2021-2022 only. 2023 is untouched test.','',f"Frozen DOWN fracture rule: {frozen['DOWN']}",f"Frozen UP shock rule: {frozen['UP']}",'','## Audit']
for r in outs: lines.append(f'- {r}')
lines+=['','## 2023 events']
for _,r in ev.iterrows(): lines.append(f"- {r.target}: actual={r.actual_dir:+d}, prior={r.prior_dir:+d}, eligible={r.eligible_shock_side}, trigger={r.trigger}, date={r.trigger_date or '-'}")
(OUT/'BIDIRECTIONAL_EMERGENCY_AUDIT_R1.md').write_text('\n'.join(lines)+'\n',encoding='utf-8'); print('\n'.join(lines))