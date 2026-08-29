#!/usr/bin/env python3
import io, urllib.request
from pathlib import Path
import numpy as np, pandas as pd
PIN='f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0'
BASE=f'https://raw.githubusercontent.com/simom1/XAUUSD-history/{PIN}/Gold-Cash/XAUUSD'
OUT=Path('projects/gold_h1_r1')
def get(name):
    with urllib.request.urlopen(f'{BASE}/{name}',timeout=60) as r:return pd.read_csv(io.BytesIO(r.read()))
d1=get('XAUUSD_D1.csv'); w1=get('XAUUSD_W1.csv'); d1.time=pd.to_datetime(d1.time); w1.time=pd.to_datetime(w1.time)
rows=[]
for _,r in w1[(w1.time>='2010-01-01')&(w1.time<='2022-12-31')].iterrows():
    schemes={
      'MON_FRI':(r.time+pd.Timedelta(days=1),r.time+pd.Timedelta(days=5)),
      'SUN_FRI':(r.time,r.time+pd.Timedelta(days=5)),
      'SUN_SAT':(r.time,r.time+pd.Timedelta(days=6)),
    }
    out={}
    for name,(a,b) in schemes.items():
        q=d1[(d1.time>=a)&(d1.time<=b)]
        if q.empty:
            out[name]=(0,np.nan,np.nan,np.nan,np.nan,np.nan,False)
        else:
            vals=np.array([q.iloc[0].open,q.high.max(),q.low.min(),q.iloc[-1].close,q.tick_volume.sum()],float)
            ref=np.array([r.open,r.high,r.low,r.close,r.tick_volume],float)
            diff=vals-ref
            out[name]=(len(q),*diff,bool(np.all(np.abs(diff)<1e-8)))
    best='SUN_FRI' if out['SUN_FRI'][-1] else ('MON_FRI' if out['MON_FRI'][-1] else ('SUN_SAT' if out['SUN_SAT'][-1] else 'NONE'))
    sun=d1[d1.time==r.time]
    sunday_present=not sun.empty
    sunday_vol=float(sun.tick_volume.sum()) if sunday_present else 0.0
    sunday_open=float(sun.iloc[0].open) if sunday_present else np.nan
    rows.append([r.time,best,sunday_present,sunday_open,sunday_vol,*out['MON_FRI'],*out['SUN_FRI'],*out['SUN_SAT']])
cols=['week','best_scheme','sunday_present','sunday_open','sunday_volume']
for s in ['monfri','sunfri','sunsat']:
    cols += [f'{s}_n',f'{s}_open_diff',f'{s}_high_diff',f'{s}_low_diff',f'{s}_close_diff',f'{s}_vol_diff',f'{s}_exact']
a=pd.DataFrame(rows,columns=cols)
a.to_csv(OUT/'weekly_mismatch_autopsy_2010_2022.csv',index=False)
summary={
 'weeks':len(a),
 'monfri_exact':int(a.monfri_exact.sum()),
 'sunfri_exact':int(a.sunfri_exact.sum()),
 'sunsat_exact':int(a.sunsat_exact.sum()),
 'sunday_present':int(a.sunday_present.sum()),
 'resolved_by_adding_sunday':int(((~a.monfri_exact)&a.sunfri_exact).sum()),
 'unresolved_after_sunfri':int((~a.sunfri_exact).sum()),
}
# assess decision relevance: close-only and SMA4 state equality under reconstructed SUN_FRI vs published W1
rec=[]
for _,r in w1.sort_values('time').reset_index(drop=True).iterrows():
    q=d1[(d1.time>=r.time)&(d1.time<=r.time+pd.Timedelta(days=5))]
    rec.append(float(q.iloc[-1].close) if len(q) else np.nan)
w=w1.sort_values('time').reset_index(drop=True).copy(); w['rec_close']=rec
w['w_sma4']=w.close.rolling(4).mean(); w['r_sma4']=w.rec_close.rolling(4).mean()
w['w_raw']=np.sign(w.close/w.w_sma4-1).fillna(0).astype(int); w['r_raw']=np.sign(w.rec_close/w.r_sma4-1).fillna(0).astype(int)
w['w_slow']=np.where((w.w_raw!=0)&(w.w_raw==w.w_raw.shift()),w.w_raw,0).astype(int); w['r_slow']=np.where((w.r_raw!=0)&(w.r_raw==w.r_raw.shift()),w.r_raw,0).astype(int)
z=w[(w.time>='2010-01-01')&(w.time<='2022-12-31')]
summary['weekly_close_mismatch_count']=int((np.abs(z.close-z.rec_close)>1e-8).sum())
summary['raw_state_mismatch_count']=int((z.w_raw!=z.r_raw).sum())
summary['slow_state_mismatch_count']=int((z.w_slow!=z.r_slow).sum())
# Write report
lines=['# GOLD H1 R1 — Weekly Mismatch Autopsy R1','']
for k,v in summary.items(): lines.append(f'- {k}: **{v}**')
lines += ['','Interpretation rules:','- If SUN_FRI exact materially exceeds MON_FRI, prior failures were mainly calendar-boundary aggregation artifacts (Sunday ticks), not corrupted weekly close history.','- Tactical Slow uses weekly close vs SMA4 and persistence; therefore close/state mismatch counts are the decision-relevant integrity checks.','- If slow_state_mismatch_count is zero or negligible, open/volume aggregation differences do not invalidate the Tactical close-based signal.']
(OUT/'WEEKLY_MISMATCH_AUTOPSY_R1.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
