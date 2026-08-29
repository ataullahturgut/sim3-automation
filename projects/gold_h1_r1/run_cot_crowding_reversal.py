#!/usr/bin/env python3
import json, urllib.parse, urllib.request
from pathlib import Path
import numpy as np, pandas as pd
OUT=Path('projects/gold_h1_r1')
params={
 '$select':'report_date_as_yyyy_mm_dd,market_and_exchange_names,cftc_contract_market_code,open_interest_all,m_money_positions_long_all,m_money_positions_short_all',
 '$where':"cftc_contract_market_code='088691'",
 '$order':'report_date_as_yyyy_mm_dd',
 '$limit':'5000'}
url='https://publicreporting.cftc.gov/resource/72hh-3qpy.json?'+urllib.parse.urlencode(params)
req=urllib.request.Request(url,headers={'User-Agent':'gold-h1-r1-audit/1.0','Accept':'application/json'})
with urllib.request.urlopen(req,timeout=90) as r: rows=json.loads(r.read().decode())
if not rows: raise RuntimeError('CFTC Socrata returned zero GOLD rows')
q=pd.DataFrame(rows)
q['date']=pd.to_datetime(q.report_date_as_yyyy_mm_dd,errors='coerce')
for c in ['open_interest_all','m_money_positions_long_all','m_money_positions_short_all']: q[c]=pd.to_numeric(q[c],errors='coerce')
q=q.sort_values('date').dropna(subset=['date','open_interest_all'])
q['mm_net']=q.m_money_positions_long_all-q.m_money_positions_short_all
q['mm_net_oi']=q.mm_net/q.open_interest_all
q['chg4']=q.mm_net_oi-q.mm_net_oi.shift(4)
def pp(s,win=156,minp=52):
 a=[]; v=s.to_numpy(float)
 for i,x in enumerate(v):
  h=v[max(0,i-win):i]; h=h[np.isfinite(h)]
  a.append(np.nan if len(h)<minp or not np.isfinite(x) else float((h<=x).mean()))
 return a
q['crowd_pct']=pp(q.mm_net_oi); q['unwind4_pct']=pp(-q.chg4)
q.to_csv(OUT/'cot_gold_weekly_2010_2026.csv',index=False)
m=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv'); m['target']=pd.to_datetime(m.target); m['origin']=pd.to_datetime(m.origin)
l=pd.read_csv(OUT/'direction_locked_replay.csv'); l=l[l.Target<='2026-07']
l2=pd.DataFrame({'target':pd.to_datetime(l.Target+'-01'),'origin':pd.to_datetime(l.Origin+'-01'),'actual_dir':l['Actual Dir'].astype(float),'dir3':l['MOM3 Dir'].astype(float),'flat':False})
m=pd.concat([m,l2],ignore_index=True).drop_duplicates('target',keep='last').sort_values('target')
rows=[]
for _,r in m.iterrows():
 z=q[q.date<=r.origin+pd.offsets.MonthEnd(0)]
 if len(z):
  z=z.iloc[-1]; rows.append([r.target,r.origin,r.actual_dir,r.dir3,r.flat,z.date,z.mm_net_oi,z.chg4,z.crowd_pct,z.unwind4_pct])
p=pd.DataFrame(rows,columns=['target','origin','actual_dir','dir3','flat','cot_date','mm_net_oi','chg4','crowd_pct','unwind4_pct'])
p.to_csv(OUT/'cot_monthly_origin_panel_2010_2026.csv',index=False)
sc=[]
for cp in [.70,.80,.90]:
 for up in [.50,.70,.80]:
  for nu in [False,True]:
   alarm=(p.dir3==1)&(p.crowd_pct>=cp)&((p.unwind4_pct>=up) if nu else True); pred=np.where(alarm,-1,p.dir3)
   for name,a,b in [('DEV','2010-01','2020-12'),('VAL','2021-01','2022-12'),('TEST2023','2023-01','2023-12'),('LOCK','2024-01','2026-07')]:
    mask=(p.target>=a)&(p.target<=b)&(~p.flat.astype(bool))
    base=(p.loc[mask,'dir3']==p.loc[mask,'actual_dir']).mean(); acc=(pred[mask.to_numpy()]==p.loc[mask,'actual_dir'].to_numpy()).mean()
    corr=int(((p.loc[mask,'dir3']!=p.loc[mask,'actual_dir'])&(pred[mask.to_numpy()]==p.loc[mask,'actual_dir'])).sum()); dmg=int(((p.loc[mask,'dir3']==p.loc[mask,'actual_dir'])&(pred[mask.to_numpy()]!=p.loc[mask,'actual_dir'])).sum())
    sc.append([cp,up,nu,name,int(mask.sum()),base,acc,corr,dmg,int(alarm[mask].sum())])
s=pd.DataFrame(sc,columns=['crowd_thr','unwind_thr','need_unwind','period','n','base_acc','rule_acc','corrected','damaged','alarms']); s.to_csv(OUT/'cot_crowding_rule_audit.csv',index=False)
cands=[]
for key,g in s.groupby(['crowd_thr','unwind_thr','need_unwind']):
 d=g.set_index('period'); dg=d.loc['DEV','rule_acc']-d.loc['DEV','base_acc']; vg=d.loc['VAL','rule_acc']-d.loc['VAL','base_acc']
 if dg>=0: cands.append((vg,dg,-d.loc['VAL','damaged'],-d.loc['VAL','alarms'],key))
if not cands: raise RuntimeError('No pre-2023 COT candidate preserves DEV')
cp,up,nu=max(cands)[-1]
p['alarm_frozen']=(p.dir3==1)&(p.crowd_pct>=cp)&((p.unwind4_pct>=up) if nu else True); p['pred_frozen']=np.where(p.alarm_frozen,-1,p.dir3)
p.to_csv(OUT/'cot_crowding_frozen_replay.csv',index=False)
def met(a,b):
 x=p[(p.target>=a)&(p.target<=b)&(~p.flat.astype(bool))]
 return len(x),(x.dir3==x.actual_dir).mean(),(x.pred_frozen==x.actual_dir).mean(),int(((x.dir3!=x.actual_dir)&(x.pred_frozen==x.actual_dir)).sum()),int(((x.dir3==x.actual_dir)&(x.pred_frozen!=x.actual_dir)).sum()),int(x.alarm_frozen.sum())
lines=['# COT Crowding Reversal Audit R1','',f'Frozen pre-2023 rule: crowd_pct >= {cp:.2f}; unwind_required={nu}; unwind_pct >= {up:.2f}.','',f'CFTC rows: {len(q)}; span {q.date.min().date()} to {q.date.max().date()}.']
for n,a,b in [('DEV','2010-01','2020-12'),('VAL','2021-01','2022-12'),('TEST2023','2023-01','2023-12'),('LOCK','2024-01','2026-07')]: lines.append(f'- {n}: n/base/rule/corrected/damaged/alarms = {met(a,b)}')
lines+=['','## 2026 Jan-Jul']
for _,r in p[(p.target>='2026-01')&(p.target<='2026-07')].iterrows(): lines.append(f"- {r.target:%Y-%m}: actual={int(r.actual_dir):+d} 3M={int(r.dir3):+d} crowd={r.crowd_pct:.3f} unwind={r.unwind4_pct:.3f} alarm={bool(r.alarm_frozen)} pred={int(r.pred_frozen):+d}")
(OUT/'COT_CROWDING_REVERSAL_AUDIT_R1.md').write_text('\n'.join(lines)+'\n'); print('\n'.join(lines))
