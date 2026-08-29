#!/usr/bin/env python3
import io, urllib.request
from pathlib import Path
import numpy as np, pandas as pd
PIN='f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0'
BASE=f'https://raw.githubusercontent.com/simom1/XAUUSD-history/{PIN}/Gold-Cash/XAUUSD'
OUT=Path('projects/gold_h1_r1')
def get(name):
    with urllib.request.urlopen(f'{BASE}/{name}',timeout=60) as r:return pd.read_csv(io.BytesIO(r.read()))
d1=get('XAUUSD_D1.csv'); d1.time=pd.to_datetime(d1.time)
# Rebuild weekly bars from D1 using proven source convention: Sunday through Friday.
weeks=[]
for sunday in pd.date_range('2009-01-04','2026-07-26',freq='W-SUN'):
    q=d1[(d1.time>=sunday)&(d1.time<=sunday+pd.Timedelta(days=5))]
    if len(q):
        weeks.append([sunday,sunday+pd.Timedelta(days=5),q.iloc[0].open,q.high.max(),q.low.min(),q.iloc[-1].close,q.tick_volume.sum()])
w=pd.DataFrame(weeks,columns=['week_label','week_end','open','high','low','close','volume']).sort_values('week_label').reset_index(drop=True)
w['sma4']=w.close.rolling(4).mean(); w['gap']=w.close/w.sma4-1; w['raw']=np.sign(w.gap).fillna(0).astype(int)
w['slow']=np.where((w.raw!=0)&(w.raw==w.raw.shift()),w.raw,0).astype(int)
w['ret1']=w.close.pct_change(); w['vol8']=w.ret1.rolling(8).std(); w['gprev']=w.gap.shift()
run=[];last=0;n=0
for x in w.raw:
    n=n+1 if x!=0 and x==last else (1 if x!=0 else 0);run.append(n);last=x
w['persist']=run
locked=pd.read_csv(OUT/'direction_locked_replay.csv')
locked=locked[(locked.Target>='2026-01')&(locked.Target<='2026-07')].copy()
rows=[]
for _,r in locked.iterrows():
    origin_end=pd.Period(r.Origin,freq='M').end_time.normalize()
    z=w[w.week_end<=origin_end].iloc[-1]
    prior=int(r['MOM3 Dir']); slow=int(z.slow)
    rows.append([r.Origin,r.Target,origin_end.date(),float(r['Origin Price']),float(r['Target Price']),int(r['Actual Dir']),prior,int(r['MOM1 Dir']),z.week_label.date(),z.week_end.date(),float(z.close),float(z.sma4),float(z.gap),int(z.raw),slow,int(z.persist),int(slow!=0 and slow==-prior),float(-prior*z.gap),float(-prior*(z.gap-z.gprev)),float(slow*z.ret1) if slow else np.nan,float(z.vol8),float((-prior*z.gap)/z.vol8) if z.vol8>0 else np.nan])
cols=['origin','target','origin_end','origin_price','target_price','actual_dir','mom3_dir','mom1_dir','week_label','week_end','weekly_close','sma4','gap_pct','raw_dir','slow_dir','raw_persistence','conflict','conflict_strength','gap_accel','oriented_weekly_ret','vol8','strength_z']
pd.DataFrame(rows,columns=cols).to_csv(OUT/'tactical_origin_2026_jan_jul.csv',index=False)
print(pd.DataFrame(rows,columns=cols).to_string(index=False))
