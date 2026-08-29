#!/usr/bin/env python3
import io, urllib.request
from pathlib import Path
import numpy as np, pandas as pd
OUT=Path('projects/gold_h1_r1')
PIN='f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0'
BASE=f'https://raw.githubusercontent.com/simom1/XAUUSD-history/{PIN}/Gold-Cash/XAUUSD'
def get(name):
    req=urllib.request.Request(f'{BASE}/{name}',headers={'User-Agent':'gold-h1-r1-full-2025/1.0'})
    with urllib.request.urlopen(req,timeout=180) as r:return pd.read_csv(io.BytesIO(r.read()))
# Core archived/persistent project files
locked=pd.read_csv(OUT/'direction_locked_replay.csv')
gate=pd.read_csv(OUT/'model_selector_gate_2024_2026.csv')
em=pd.read_csv(OUT/'emergency_shock_frozen_replay.csv')
# Exact pinned D1 -> Sunday-Friday completed W1 -> Tactical Slow R1
try:
    d1=get('XAUUSD_D1.csv')
except Exception:
    d1=get('XAUUSD_D1.csv')
d1['time']=pd.to_datetime(d1['time'])
weeks=[]
for sunday in pd.date_range('2009-01-04','2025-12-28',freq='W-SUN'):
    q=d1[(d1.time>=sunday)&(d1.time<=sunday+pd.Timedelta(days=5))]
    if len(q): weeks.append([sunday,sunday+pd.Timedelta(days=5),q.iloc[-1].close])
w=pd.DataFrame(weeks,columns=['week_label','week_end','close']).sort_values('week_label').reset_index(drop=True)
w['sma4']=w.close.rolling(4).mean(); w['raw']=np.sign(w.close-w.sma4).fillna(0).astype(int)
w['slow']=np.where((w.raw!=0)&(w.raw==w.raw.shift()),w.raw,0).astype(int)
# 2025 monthly core table
x=locked[(locked.Target>='2025-01')&(locked.Target<='2025-12')].copy()
x['month']=pd.to_datetime(x.Target+'-01')
g25=gate[(gate.month>='2025-01-01')&(gate.month<='2025-12-01')].copy(); g25['month']=pd.to_datetime(g25.month)
x=x.merge(g25,on='month',how='left')
# Tactical state at previous completed month-end
slow=[]; tstate=[]
for _,r in x.iterrows():
    origin_end=pd.Period(r.Origin,freq='M').end_time.normalize()
    z=w[w.week_end<=origin_end].iloc[-1]
    s=int(z.slow); p=int(r['MOM3 Dir']); slow.append(s)
    tstate.append('NEUTRAL' if s==0 else ('CONFIRM' if s==p else 'CONFLICT'))
x['tactical_slow_dir']=slow; x['tactical_state']=tstate
# Emergency frozen replay only applies to UP priors. 2025 preserved file already frozen pre-2023.
em25=em[(em.target>='2025-01')&(em.target<='2025-12')][['target','trigger','trigger_date']].copy(); em25['month']=pd.to_datetime(em25.target+'-01')
x=x.merge(em25[['month','trigger','trigger_date']],on='month',how='left'); x['trigger']=x['trigger'].fillna(False).astype(bool)
# BOCPD-return frozen final audit has no 2025 locked alarms; alarms in locked window begin only in 2026.
x['bocpd_return_alarm']=False
# Price-level diagnostics. VW = archived audited reference path available in selector file.
x['vw_forecast']=x['past_mape_forecast']; x['vw_ape']=x['always_vw_ape']; x['selector_forecast']=x['gate_forecast']; x['selector_ape']=x['gate_ape']
x['equal_forecast']=x['equal_ensemble']; x['equal_ape']=x['equal_ensemble_ape']
# Direction diagnostics
x['vw_dir']=np.sign(x.vw_forecast-x['Origin Price']).astype(int)
x['selector_dir']=np.sign(x.selector_forecast-x['Origin Price']).astype(int)
x['mom3_hit']=(x['MOM3 Dir']==x['Actual Dir'])
x['mom1_hit']=(x['MOM1 Dir']==x['Actual Dir'])
x['vw_dir_hit']=(x.vw_dir==x['Actual Dir'])
x['selector_dir_hit']=(x.selector_dir==x['Actual Dir'])
# Approved conservative architecture does not auto-flip Tactical/BOCPD. Emergency is provisional risk override only.
x['start_direction']=x['MOM3 Dir']
x['operational_action']=np.where(x.trigger,'RISK_OFF_INTRAMONTH',np.where(x.tactical_state=='CONFLICT','LOW_CONFIDENCE_KEEP_PRIOR','KEEP_PRIOR'))
# A diagnostic reversal evidence label: only flag conflict, never silently claim production flip.
x['diagnostic_reversal_warning']=((x['MOM1 Dir']==-x['MOM3 Dir']) | (x.tactical_state=='CONFLICT') | (x.vw_dir==-x['MOM3 Dir']))
# Compact persisted table
cols=['Origin','Target','Origin Price','Target Price','Actual Return','Actual Dir','MOM1 Dir','MOM3 Dir','mom1_hit','mom3_hit','vw_forecast','vw_ape','vw_dir','vw_dir_hit','gate_pick','selector_forecast','selector_ape','selector_dir','selector_dir_hit','equal_forecast','equal_ape','tactical_slow_dir','tactical_state','bocpd_return_alarm','trigger','trigger_date','diagnostic_reversal_warning','operational_action','oracle_pick','oracle_ape','gate_hit']
out=x[cols].copy(); out.to_csv(OUT/'FULL_SYSTEM_2025_REPLAY.csv',index=False)
# Summary metrics
summary={
 'MOM3_direction_accuracy':float(x.mom3_hit.mean()),
 'MOM1_direction_accuracy':float(x.mom1_hit.mean()),
 'VW_direction_accuracy':float(x.vw_dir_hit.mean()),
 'selector_implied_direction_accuracy':float(x.selector_dir_hit.mean()),
 'VW_MAPE':float(x.vw_ape.mean()),
 'selector_MAPE':float(x.selector_ape.mean()),
 'equal_ensemble_MAPE':float(x.equal_ape.mean()),
 'selector_oracle_pick_rate':float(x.gate_hit.mean()),
 'tactical_confirm_months':int((x.tactical_state=='CONFIRM').sum()),
 'tactical_conflict_months':int((x.tactical_state=='CONFLICT').sum()),
 'tactical_neutral_months':int((x.tactical_state=='NEUTRAL').sum()),
 'bocpd_alarm_months':int(x.bocpd_return_alarm.sum()),
 'emergency_trigger_months':int(x.trigger.sum()),
 'reversal_warning_months':int(x.diagnostic_reversal_warning.sum()),
}
# Build report
s=['# GOLD H1 R1 — Full System 2025 Replay','',
   'Role separation is preserved: level forecast, model selection, monthly direction, Tactical confirmation/conflict, BOCPD regime risk, and Emergency intramonth override are reported separately. No 2025 outcome is used for tuning.','',
   '## Headline metrics','']
for k,v in summary.items(): s.append(f'- {k}: {v:.6f}' if isinstance(v,float) else f'- {k}: {v}')
s+=['','## Monthly replay','', '|Target|Actual|MOM3|MOM1|VW dir|Tactical|Selector|VW APE|Selector APE|BOCPD|Emergency|Action|','|---|---:|---:|---:|---:|---|---|---:|---:|---|---|---|']
for _,r in x.iterrows():
    s.append(f"|{r.Target}|{int(r['Actual Dir']):+d}|{int(r['MOM3 Dir']):+d}|{int(r['MOM1 Dir']):+d}|{int(r.vw_dir):+d}|{r.tactical_state}|{r.gate_pick}|{r.vw_ape:.3f}%|{r.selector_ape:.3f}%|{'ALARM' if r.bocpd_return_alarm else '-'}|{r.trigger_date if r.trigger else '-'}|{r.operational_action}|")
s+=['','## Decision','',
    '- The archived VW path is the stronger 2025 price-level reference than the exploratory selector if its mean MAPE is lower.',
    '- The selector remains diagnostic/challenger; gate_hit is ex-post oracle-model selection agreement, not direction accuracy.',
    '- Tactical conflict is a confidence warning, not an approved automatic flip.',
    '- BOCPD-return is structural risk context only.',
    '- Emergency Shock Override is intramonth risk-off only and does not rewrite the start-of-month forecast.',
    '- Any oracle_pick/oracle_ape column is diagnostic hindsight only.']
(OUT/'FULL_SYSTEM_2025_REPORT.md').write_text('\n'.join(s)+'\n',encoding='utf-8')
print('\n'.join(s))
