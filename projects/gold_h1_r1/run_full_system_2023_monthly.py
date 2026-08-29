#!/usr/bin/env python3
import io, urllib.request, time
from pathlib import Path
import numpy as np, pandas as pd
OUT=Path('projects/gold_h1_r1')
PIN='f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0'
GOLD=f'https://raw.githubusercontent.com/simom1/XAUUSD-history/{PIN}/Gold-Cash/XAUUSD/XAUUSD_D1.csv'
def read_csv(url):
    err=None
    for k in range(5):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 gold-h1-r1/1.0'})
            with urllib.request.urlopen(req,timeout=180) as r:return pd.read_csv(io.BytesIO(r.read()))
        except Exception as e: err=e; time.sleep(2*(k+1))
    raise err
A=pd.read_csv(OUT/'autopsy_2023_direction.csv'); A['month']=A['month'].astype(str)
g=read_csv(GOLD); g['date']=pd.to_datetime(g['time']); g=g[['date','close']].sort_values('date').drop_duplicates('date')
g['month']=g.date.dt.to_period('M').astype(str); g['ret5']=g.close.pct_change(5); g['sma20']=g.close.rolling(20).mean(); g['sma50']=g.close.rolling(50).mean(); g['above20']=g.close>g.sma20; g['above50']=g.close>g.sma50; g['below20']=g.close<g.sma20; g['below50']=g.close<g.sma50
g['mtd_peak']=g.groupby('month').close.cummax(); g['mtd_trough']=g.groupby('month').close.cummin(); g['mtd_dd']=g.close/g.mtd_peak-1; g['mtd_rally']=g.close/g.mtd_trough-1
M=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv'); M['target']=pd.to_datetime(M.target).dt.to_period('M').astype(str); M=M[~M.flat.astype(bool)].copy()
down_rule=(-.03,-.04,50)
up_cands=[(r5,rally,sma) for r5 in [.02,.03,.04,.05,.06] for rally in [.03,.05,.07,.09] for sma in [20,50]]
def hit_down(month):
    d=g[g.month==month]; s=(d.mtd_dd<=down_rule[0])&(d.ret5<=down_rule[1])&(d[f'below{down_rule[2]}']); return bool(s.any()), d.loc[s,'date'].min() if s.any() else pd.NaT
def hit_up(month,rule):
    r5,rally,sma=rule; d=g[g.month==month]; s=(d.mtd_rally>=rally)&(d.ret5>=r5)&(d[f'above{sma}']); return bool(s.any()), d.loc[s,'date'].min() if s.any() else pd.NaT
def eval_up(rule,a,b):
    x=M[(M.target>=a)&(M.target<=b)&(M.dir3==-1)]; corr=dmg=tr=0
    for _,r in x.iterrows():
        h,_=hit_up(r.target,rule); tr+=h; corr+=int(h and r.actual_dir==1); dmg+=int(h and r.actual_dir==-1)
    return corr,dmg,tr,corr-dmg
choices=[]
for rule in up_cands:
    dc,dd,dt,du=eval_up(rule,'2010-01','2020-12'); vc,vd,vt,vu=eval_up(rule,'2021-01','2022-12')
    if du>=0 and dc>=dd and (dt==0 or dc/max(dt,1)>=.5): choices.append((vu,-vd,vc,du,rule))
up_rule=max(choices)[-1] if choices else (0.04,0.05,50)
rows=[]
for _,r in A.iterrows():
    m=r.month; actual=int(r.actual_dir); prior=int(r.mom3_dir); start_hit=int(prior==actual); disagree=[]
    if int(r.mom1_dir)!=0 and int(r.mom1_dir)!=prior: disagree.append('MOM1')
    if int(r.vw_dir)!=prior: disagree.append('VW')
    if int(r.patch_dir)!=prior: disagree.append('PATCH')
    if int(r.idma_dir)!=prior: disagree.append('IDMA')
    if str(r.tactical_relation)=='CONFLICT': disagree.append('TACTICAL')
    if prior==1: eh,ed=hit_down(m); etype='DOWN_FRACTURE' if eh else ''
    elif prior==-1: eh,ed=hit_up(m,up_rule); etype='UP_SHOCK' if eh else ''
    else: eh,ed=False,pd.NaT; etype=''
    final_dir=-prior if eh and prior!=0 else prior; final_hit=int(final_dir==actual) if actual!=0 else 0
    action='INTRAMONTH_EMERGENCY_FLIP' if eh else ('LOW_CONFIDENCE_KEEP_PRIOR' if disagree else 'KEEP_PRIOR')
    rows.append(dict(month=m,origin_gold=r.origin_gold,actual_gold=r.actual_gold,actual_move_pct=r.actual_move_pct,actual_dir=actual,mom3_dir=prior,mom1_dir=int(r.mom1_dir),vw_dir=int(r.vw_dir),patch_dir=int(r.patch_dir),idma_dir=int(r.idma_dir),tactical_relation=r.tactical_relation,disagreement='+'.join(disagree) if disagree else '',start_dir_hit=start_hit,emergency_type=etype,emergency_date='' if pd.isna(ed) else ed.date().isoformat(),intramonth_final_dir=final_dir,intramonth_hit=final_hit,action=action,vw_ape=abs(r.vw_forecast-r.actual_gold)/r.actual_gold*100,patch_ape=abs(r.patch_forecast-r.actual_gold)/r.actual_gold*100,idma_ape=abs(r.idma_forecast-r.actual_gold)/r.actual_gold*100,mom3_ape=abs(r.mom3_forecast-r.actual_gold)/r.actual_gold*100))
R=pd.DataFrame(rows); R.to_csv(OUT/'FULL_SYSTEM_2023_MONTHLY_REPLAY.csv',index=False); nonflat=R[R.actual_dir!=0]
strict=R.start_dir_hit.mean(); econ=nonflat.start_dir_hit.mean(); final=nonflat.intramonth_hit.mean()
lines=['# GOLD H1 R1 — 2023 Monthly Full-System Replay','',f'Frozen upside emergency rule selected on 2010-2022 only: 5D return >= {up_rule[0]:.1%}, MTD rally >= {up_rule[1]:.1%}, above SMA{up_rule[2]}.',f'Existing downside Emergency R1 preserved: MTD drawdown <= {down_rule[0]:.1%}, 5D return <= {down_rule[1]:.1%}, below SMA{down_rule[2]}.','',f'- Start-of-month 3M strict accuracy: {strict:.4%}',f'- Start-of-month economic accuracy excluding exact-flat October: {econ:.4%}',f'- Intramonth emergency-adjusted accuracy excluding flat: {final:.4%}',f'- VW MAPE: {R.vw_ape.mean():.4f}%',f'- Patch MAPE: {R.patch_ape.mean():.4f}%',f'- IDMA MAPE: {R.idma_ape.mean():.4f}%',f'- 3M level MAPE: {R.mom3_ape.mean():.4f}%','','|Month|Actual|3M|MOM1|VW|Tactical|Emergency|Date|Final|Action|','|---|---:|---:|---:|---:|---|---|---|---:|---|']
for _,r in R.iterrows(): lines.append(f"|{r.month}|{int(r.actual_dir):+d}|{int(r.mom3_dir):+d}|{int(r.mom1_dir):+d}|{int(r.vw_dir):+d}|{r.tactical_relation}|{r.emergency_type or '-'}|{r.emergency_date or '-'}|{int(r.intramonth_final_dir):+d}|{r.action}|")
lines+=['','## Contract','- Each month is evaluated separately at its own origin.','- 2023 outcomes do not select the upside emergency rule; selection uses only 2010-2022.','- Tactical disagreement does not automatically flip direction.','- Emergency signals are intramonth; they are reported separately from start-of-month forecast.','- Exact-flat October is shown separately rather than treated as an economic reversal.']
(OUT/'FULL_SYSTEM_2023_MONTHLY_REPORT.md').write_text('\n'.join(lines)+'\n'); print('\n'.join(lines))
