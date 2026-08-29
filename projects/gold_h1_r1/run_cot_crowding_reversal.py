#!/usr/bin/env python3
import io, zipfile, urllib.request
from pathlib import Path
import numpy as np, pandas as pd
OUT=Path('projects/gold_h1_r1')
frames=[]
for y in range(2010,2027):
    url=f'https://www.cftc.gov/files/dea/history/fut_disagg_txt_{y}.zip'
    try:
        data=urllib.request.urlopen(url,timeout=90).read(); z=zipfile.ZipFile(io.BytesIO(data)); df=pd.read_csv(z.open(z.namelist()[0]),low_memory=False); frames.append(df)
    except Exception as e: print('YEAR_FAIL',y,e)
allc=pd.concat(frames,ignore_index=True)
def pick(ps):
    for p in ps:
      for c in allc.columns:
        if p.lower() in c.strip().lower(): return c
    raise KeyError(ps)
market=pick(['Market_and_Exchange_Names','Market and Exchange Names']); code=pick(['CFTC_Contract_Market_Code','CFTC Contract Market Code']); datec=pick(['Report_Date_as_YYYY-MM-DD','Report Date as YYYY-MM-DD']); oi=pick(['Open_Interest_All','Open Interest (All)']); ml=pick(['M_Money_Positions_Long_All','Managed Money Positions Long (All)']); ms=pick(['M_Money_Positions_Short_All','Managed Money Positions Short (All)'])
q=allc[allc[code].astype(str).str.replace('.0','',regex=False).str.strip().eq('088691')].copy()
if q.empty:q=allc[allc[market].astype(str).str.contains('GOLD - COMMODITY EXCHANGE',case=False,na=False)].copy()
q['date']=pd.to_datetime(q[datec],errors='coerce');q=q.sort_values('date')
for c in [oi,ml,ms]:q[c]=pd.to_numeric(q[c],errors='coerce')
q['mm_net']=q[ml]-q[ms];q['mm_net_oi']=q.mm_net/q[oi];q['chg4']=q.mm_net_oi-q.mm_net_oi.shift(4)
def pp(s,win=156,minp=52):
 a=[];v=s.to_numpy(float)
 for i,x in enumerate(v):
  h=v[max(0,i-win):i];h=h[np.isfinite(h)];a.append(np.nan if len(h)<minp or not np.isfinite(x) else float((h<=x).mean()))
 return a
q['crowd_pct']=pp(q.mm_net_oi);q['unwind4_pct']=pp(-q.chg4);q[['date',market,code,oi,ml,ms,'mm_net','mm_net_oi','chg4','crowd_pct','unwind4_pct']].to_csv(OUT/'cot_gold_weekly_2010_2026.csv',index=False)
m=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv');m['target']=pd.to_datetime(m.target);m['origin']=pd.to_datetime(m.origin)
l=pd.read_csv(OUT/'direction_locked_replay.csv');l=l[l.Target<='2026-07'];l2=pd.DataFrame({'target':pd.to_datetime(l.Target+'-01'),'origin':pd.to_datetime(l.Origin+'-01'),'actual_dir':l['Actual Dir'].astype(float),'dir3':l['MOM3 Dir'].astype(float),'flat':False});m=pd.concat([m,l2]).drop_duplicates('target',keep='last').sort_values('target')
rows=[]
for _,r in m.iterrows():
 z=q[q.date<=r.origin+pd.offsets.MonthEnd(0)]
 if len(z):
  z=z.iloc[-1];rows.append([r.target,r.origin,r.actual_dir,r.dir3,r.flat,z.date,z.mm_net_oi,z.chg4,z.crowd_pct,z.unwind4_pct])
p=pd.DataFrame(rows,columns=['target','origin','actual_dir','dir3','flat','cot_date','mm_net_oi','chg4','crowd_pct','unwind4_pct']);p.to_csv(OUT/'cot_monthly_origin_panel_2010_2026.csv',index=False)
sc=[]
for cp in [.7,.8,.9]:
 for up in [.5,.7,.8]:
  for nu in [False,True]:
   alarm=(p.dir3==1)&(p.crowd_pct>=cp)&((p.unwind4_pct>=up) if nu else True);pred=np.where(alarm,-1,p.dir3)
   for name,a,b in [('DEV','2010-01','2020-12'),('VAL','2021-01','2022-12'),('TEST2023','2023-01','2023-12'),('LOCK','2024-01','2026-07')]:
    mask=(p.target>=a)&(p.target<=b)&(~p.flat.astype(bool)); base=(p.loc[mask,'dir3']==p.loc[mask,'actual_dir']).mean();acc=(pred[mask.to_numpy()]==p.loc[mask,'actual_dir'].to_numpy()).mean();corr=int(((p.loc[mask,'dir3']!=p.loc[mask,'actual_dir'])&(pred[mask.to_numpy()]==p.loc[mask,'actual_dir'])).sum());dmg=int(((p.loc[mask,'dir3']==p.loc[mask,'actual_dir'])&(pred[mask.to_numpy()]!=p.loc[mask,'actual_dir'])).sum());sc.append([cp,up,nu,name,int(mask.sum()),base,acc,corr,dmg,int(alarm[mask].sum())])
s=pd.DataFrame(sc,columns=['crowd_thr','unwind_thr','need_unwind','period','n','base_acc','rule_acc','corrected','damaged','alarms']);s.to_csv(OUT/'cot_crowding_rule_audit.csv',index=False)
# explicit selection from pre-2023 only
cands=[]
for key,g in s.groupby(['crowd_thr','unwind_thr','need_unwind']):
 d=g.set_index('period');dg=d.loc['DEV','rule_acc']-d.loc['DEV','base_acc'];vg=d.loc['VAL','rule_acc']-d.loc['VAL','base_acc']
 if dg>=0:cands.append((vg,dg,-d.loc['VAL','damaged'],-d.loc['VAL','alarms'],key))
cp,up,nu=max(cands)[-1]
p['alarm_frozen']=(p.dir3==1)&(p.crowd_pct>=cp)&((p.unwind4_pct>=up) if nu else True);p['pred_frozen']=np.where(p.alarm_frozen,-1,p.dir3);p.to_csv(OUT/'cot_crowding_frozen_replay.csv',index=False)
def met(a,b):
 x=p[(p.target>=a)&(p.target<=b)&(~p.flat.astype(bool))];return len(x),(x.dir3==x.actual_dir).mean(),(x.pred_frozen==x.actual_dir).mean(),int(((x.dir3!=x.actual_dir)&(x.pred_frozen==x.actual_dir)).sum()),int(((x.dir3==x.actual_dir)&(x.pred_frozen!=x.actual_dir)).sum()),int(x.alarm_frozen.sum())
lines=['# COT Crowding Reversal Audit R1','',f'Frozen pre-2023 rule: crowd_pct >= {cp:.2f}; unwind_required={nu}; unwind_pct >= {up:.2f}.','']
for n,a,b in [('DEV','2010-01','2020-12'),('VAL','2021-01','2022-12'),('TEST2023','2023-01','2023-12'),('LOCK','2024-01','2026-07')]:lines.append(f'- {n}: n/base/rule/corrected/damaged/alarms = {met(a,b)}')
lines+=['','## 2026 Jan-Jul']
for _,r in p[(p.target>='2026-01')&(p.target<='2026-07')].iterrows():lines.append(f"- {r.target:%Y-%m}: actual={int(r.actual_dir):+d} 3M={int(r.dir3):+d} crowd={r.crowd_pct:.3f} unwind={r.unwind4_pct:.3f} alarm={bool(r.alarm_frozen)} pred={int(r.pred_frozen):+d}")
(OUT/'COT_CROWDING_REVERSAL_AUDIT_R1.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
