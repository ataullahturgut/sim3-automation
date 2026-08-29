#!/usr/bin/env python3
import io, zipfile, urllib.request, re
from pathlib import Path
import numpy as np, pandas as pd
OUT=Path('projects/gold_h1_r1')
frames=[]
for y in range(2010,2027):
    url=f'https://www.cftc.gov/files/dea/history/fut_disagg_txt_{y}.zip'
    try:
        data=urllib.request.urlopen(url,timeout=90).read()
        z=zipfile.ZipFile(io.BytesIO(data)); name=z.namelist()[0]
        df=pd.read_csv(z.open(name),low_memory=False)
        frames.append(df)
    except Exception as e: print('YEAR_FAIL',y,e)
allc=pd.concat(frames,ignore_index=True)
# normalize cols
cols={c.strip():c for c in allc.columns}
def pick(patterns):
    for p in patterns:
        for c in allc.columns:
            if p.lower() in c.strip().lower(): return c
    raise KeyError(patterns)
market=pick(['Market_and_Exchange_Names','Market and Exchange Names'])
code=pick(['CFTC_Contract_Market_Code','CFTC Contract Market Code'])
datec=pick(['Report_Date_as_YYYY-MM-DD','As_of_Date_In_Form_YYMMDD','Report Date as YYYY-MM-DD'])
oi=pick(['Open_Interest_All','Open Interest (All)'])
ml=pick(['M_Money_Positions_Long_All','Managed Money Positions Long (All)'])
ms=pick(['M_Money_Positions_Short_All','Managed Money Positions Short (All)'])
# GOLD COMEX code 088691; string-clean to avoid int formatting issues
q=allc[allc[code].astype(str).str.replace('.0','',regex=False).str.strip().eq('088691')].copy()
if q.empty: q=allc[allc[market].astype(str).str.contains('GOLD - COMMODITY EXCHANGE',case=False,na=False)].copy()
q['date']=pd.to_datetime(q[datec],errors='coerce'); q=q.sort_values('date')
for c in [oi,ml,ms]: q[c]=pd.to_numeric(q[c],errors='coerce')
q['mm_net']=q[ml]-q[ms]; q['mm_net_oi']=q.mm_net/q[oi]
q['chg1']=q.mm_net_oi.diff(); q['chg4']=q.mm_net_oi-q.mm_net_oi.shift(4)
# causal rolling percentile rank based on prior 156 weeks only
def past_pct(s,win=156,minp=52):
    a=[]
    vals=s.to_numpy(float)
    for i,x in enumerate(vals):
        hist=vals[max(0,i-win):i]; hist=hist[np.isfinite(hist)]
        a.append(np.nan if len(hist)<minp or not np.isfinite(x) else float((hist<=x).mean()))
    return a
q['crowd_pct']=past_pct(q.mm_net_oi)
q['unwind4_pct']=past_pct(-q.chg4)
q[['date',market,code,oi,ml,ms,'mm_net','mm_net_oi','chg1','chg4','crowd_pct','unwind4_pct']].to_csv(OUT/'cot_gold_weekly_2010_2026.csv',index=False)
# monthly direction data, append locked 2024-26
m=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv'); m['target']=pd.to_datetime(m.target);m['origin']=pd.to_datetime(m.origin)
l=pd.read_csv(OUT/'direction_locked_replay.csv'); l=l[l.Target<='2026-07'].copy()
l2=pd.DataFrame({'target':pd.to_datetime(l.Target+'-01'),'origin':pd.to_datetime(l.Origin+'-01'),'actual_dir':l['Actual Dir'].astype(float),'dir3':l['MOM3 Dir'].astype(float),'flat':False})
m=pd.concat([m,l2],ignore_index=True).drop_duplicates('target',keep='last').sort_values('target')
# last COT report date <= origin month end (report date itself was known later that week, but by month-end all such reports are public)
rows=[]
for _,r in m.iterrows():
    end=r.origin+pd.offsets.MonthEnd(0); z=q[q.date<=end]
    if z.empty: continue
    z=z.iloc[-1]
    rows.append([r.target,r.origin,r.actual_dir,r.dir3,r.flat,z.date,z.mm_net_oi,z.chg4,z.crowd_pct,z.unwind4_pct])
p=pd.DataFrame(rows,columns=['target','origin','actual_dir','dir3','flat','cot_date','mm_net_oi','chg4','crowd_pct','unwind4_pct'])
p.to_csv(OUT/'cot_monthly_origin_panel_2010_2026.csv',index=False)
# Fixed small candidate family selected only DEV 2010-20, validated 2021-22. Alarm means override UP prior to DOWN only.
sc=[]
for cp in [0.70,0.80,0.90]:
  for up in [0.50,0.70,0.80]:
    for need_unwind in [False,True]:
      alarm=(p.dir3==1)&(p.crowd_pct>=cp)&((p.unwind4_pct>=up) if need_unwind else True)
      pred=np.where(alarm,-1,p.dir3)
      for name,a,b in [('DEV','2010-01','2020-12'),('VAL','2021-01','2022-12'),('TEST2023','2023-01','2023-12'),('LOCK','2024-01','2026-07')]:
        mask=(p.target>=a)&(p.target<=b)&(~p.flat.astype(bool))
        base=(p.loc[mask,'dir3']==p.loc[mask,'actual_dir']).mean(); acc=(pred[mask.to_numpy()]==p.loc[mask,'actual_dir'].to_numpy()).mean()
        corr=int(((p.loc[mask,'dir3']!=p.loc[mask,'actual_dir'])&(pred[mask.to_numpy()]==p.loc[mask,'actual_dir'])).sum())
        dmg=int(((p.loc[mask,'dir3']==p.loc[mask,'actual_dir'])&(pred[mask.to_numpy()]!=p.loc[mask,'actual_dir'])).sum())
        sc.append([cp,up,need_unwind,name,int(mask.sum()),base,acc,corr,dmg,int(alarm[mask].sum())])
s=pd.DataFrame(sc,columns=['crowd_thr','unwind_thr','need_unwind','period','n','base_acc','rule_acc','corrected','damaged','alarms'])
# choose by VAL gain first, DEV nonnegative gain and fewer alarms/damage as tie-breaker
wide=s.pivot_table(index=['crowd_thr','unwind_thr','need_unwind'],columns='period',values=['base_acc','rule_acc','corrected','damaged','alarms']).reset_index()
valid=[]
for idx,row in wide.iterrows():
    dg=row[('rule_acc','DEV')]-row[('base_acc','DEV')]; vg=row[('rule_acc','VAL')]-row[('base_acc','VAL')]
    if dg>=0: valid.append((vg,dg,-row[('damaged','VAL')],-row[('alarms','VAL')],idx))
best=max(valid)[-1] if valid else wide.index[0]
br=wide.loc[best]; key=(float(br[('crowd_thr','')]),float(br[('unwind_thr','')]),bool(br[('need_unwind','')]))
cp,up,nu=key
p['alarm_frozen']=(p.dir3==1)&(p.crowd_pct>=cp)&((p.unwind4_pct>=up) if nu else True)
p['pred_frozen']=np.where(p.alarm_frozen,-1,p.dir3)
p.to_csv(OUT/'cot_crowding_frozen_replay.csv',index=False)
s.to_csv(OUT/'cot_crowding_rule_audit.csv',index=False)
# report 2026 and key scores
def met(a,b):
    x=p[(p.target>=a)&(p.target<=b)&(~p.flat.astype(bool))];return len(x),(x.dir3==x.actual_dir).mean(),(x.pred_frozen==x.actual_dir).mean(),int(((x.dir3!=x.actual_dir)&(x.pred_frozen==x.actual_dir)).sum()),int(((x.dir3==x.actual_dir)&(x.pred_frozen!=x.actual_dir)).sum()),int(x.alarm_frozen.sum())
lines=['# COT Crowding Reversal Audit R1','',f'Frozen rule from pre-2023 only: crowd_pct >= {cp:.2f}; unwind required={nu}; unwind_pct >= {up:.2f}.','']
for name,a,b in [('DEV','2010-01','2020-12'),('VAL','2021-01','2022-12'),('TEST2023','2023-01','2023-12'),('LOCK','2024-01','2026-07')]: lines.append(f'- {name}: n/base/rule/corrected/damaged/alarms = {met(a,b)}')
lines+=['','## 2026 Jan-Jul']
for _,r in p[(p.target>='2026-01')&(p.target<='2026-07')].iterrows():lines.append(f"- {r.target:%Y-%m}: actual={int(r.actual_dir):+d} 3M={int(r.dir3):+d} crowd_pct={r.crowd_pct:.3f} unwind4_pct={r.unwind4_pct:.3f} alarm={bool(r.alarm_frozen)} pred={int(r.pred_frozen):+d}")
(OUT/'COT_CROWDING_REVERSAL_AUDIT_R1.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
