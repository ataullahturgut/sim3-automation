#!/usr/bin/env python3
import pandas as pd, numpy as np
from pathlib import Path
OUT=Path('projects/gold_h1_r1')
def fred(series):
 u=f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}'
 x=pd.read_csv(u); x.columns=['date',series]; x['date']=pd.to_datetime(x.date); x[series]=pd.to_numeric(x[series],errors='coerce'); return x.dropna()
ry=fred('DFII10'); usd=fred('DTWEXBGS')
def month_last(x,col): return x.set_index('date')[col].resample('ME').last().dropna()
r=month_last(ry,'DFII10'); d=month_last(usd,'DTWEXBGS')
f=pd.concat([r,d],axis=1).dropna(); f['ry_chg1']=f.DFII10.diff(); f['ry_chg3']=f.DFII10.diff(3); f['usd_ret1']=f.DTWEXBGS.pct_change(); f['usd_ret3']=f.DTWEXBGS.pct_change(3)
m=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv');m['target']=pd.to_datetime(m.target);m['origin']=pd.to_datetime(m.origin)
l=pd.read_csv(OUT/'direction_locked_replay.csv');l=l[l.Target<='2026-07'];l2=pd.DataFrame({'target':pd.to_datetime(l.Target+'-01'),'origin':pd.to_datetime(l.Origin+'-01'),'actual_dir':l['Actual Dir'].astype(float),'dir3':l['MOM3 Dir'].astype(float),'flat':False});m=pd.concat([m,l2]).drop_duplicates('target',keep='last').sort_values('target')
rows=[]
for _,z in m.iterrows():
 e=z.origin+pd.offsets.MonthEnd(0); h=f[f.index<=e]
 if len(h):
  v=h.iloc[-1]; rows.append([z.target,z.origin,z.actual_dir,z.dir3,z.flat,v.DFII10,v.DTWEXBGS,v.ry_chg1,v.ry_chg3,v.usd_ret1,v.usd_ret3])
p=pd.DataFrame(rows,columns=['target','origin','actual_dir','dir3','flat','real10','usd','ry1','ry3','usd1','usd3'])
# simple economically signed family, thresholds fixed grid selected pre-2023 only
sc=[]
for ry_thr in [0.0,.10,.20,.30]:
 for usd_thr in [0.0,.01,.02,.03]:
  for mode in ['AND','OR','RY_ONLY','USD_ONLY']:
   a=p.ry1>=ry_thr; b=p.usd1>=usd_thr
   risk={'AND':a&b,'OR':a|b,'RY_ONLY':a,'USD_ONLY':b}[mode]
   alarm=(p.dir3==1)&risk; pred=np.where(alarm,-1,p.dir3)
   for name,x,y in [('DEV','2010-01','2020-12'),('VAL','2021-01','2022-12'),('TEST2023','2023-01','2023-12'),('LOCK','2024-01','2026-07')]:
    mask=(p.target>=x)&(p.target<=y)&(~p.flat.astype(bool));base=(p.loc[mask,'dir3']==p.loc[mask,'actual_dir']).mean();acc=(pred[mask.to_numpy()]==p.loc[mask,'actual_dir'].to_numpy()).mean();corr=int(((p.loc[mask,'dir3']!=p.loc[mask,'actual_dir'])&(pred[mask.to_numpy()]==p.loc[mask,'actual_dir'])).sum());dmg=int(((p.loc[mask,'dir3']==p.loc[mask,'actual_dir'])&(pred[mask.to_numpy()]!=p.loc[mask,'actual_dir'])).sum());sc.append([ry_thr,usd_thr,mode,name,int(mask.sum()),base,acc,corr,dmg,int(alarm[mask].sum())])
s=pd.DataFrame(sc,columns=['ry_thr','usd_thr','mode','period','n','base_acc','rule_acc','corrected','damaged','alarms']);s.to_csv(OUT/'macro_reversal_rule_audit.csv',index=False)
c=[]
for key,g in s.groupby(['ry_thr','usd_thr','mode']):
 d0=g.set_index('period');dg=d0.loc['DEV','rule_acc']-d0.loc['DEV','base_acc'];vg=d0.loc['VAL','rule_acc']-d0.loc['VAL','base_acc']
 if dg>=0:c.append((vg,dg,-d0.loc['VAL','damaged'],-d0.loc['VAL','alarms'],key))
ry_thr,usd_thr,mode=max(c)[-1];a=p.ry1>=ry_thr;b=p.usd1>=usd_thr;risk={'AND':a&b,'OR':a|b,'RY_ONLY':a,'USD_ONLY':b}[mode];p['alarm_frozen']=(p.dir3==1)&risk;p['pred_frozen']=np.where(p.alarm_frozen,-1,p.dir3);p.to_csv(OUT/'macro_reversal_frozen_replay.csv',index=False)
def met(a,b):
 x=p[(p.target>=a)&(p.target<=b)&(~p.flat.astype(bool))];return len(x),(x.dir3==x.actual_dir).mean(),(x.pred_frozen==x.actual_dir).mean(),int(((x.dir3!=x.actual_dir)&(x.pred_frozen==x.actual_dir)).sum()),int(((x.dir3==x.actual_dir)&(x.pred_frozen!=x.actual_dir)).sum()),int(x.alarm_frozen.sum())
lines=['# Macro Reversal Audit R1','',f'Frozen pre-2023 rule: mode={mode}, real-yield 1M change >= {ry_thr}, USD 1M return >= {usd_thr:.1%}.','']
for n,a,b in [('DEV','2010-01','2020-12'),('VAL','2021-01','2022-12'),('TEST2023','2023-01','2023-12'),('LOCK','2024-01','2026-07')]:lines.append(f'- {n}: {met(a,b)}')
lines+=['','## 2026 Jan-Jul']
for _,r in p[(p.target>='2026-01')&(p.target<='2026-07')].iterrows():lines.append(f"- {r.target:%Y-%m}: actual={int(r.actual_dir):+d} 3M={int(r.dir3):+d} ry1={r.ry1:+.3f} usd1={r.usd1:+.3%} alarm={bool(r.alarm_frozen)} pred={int(r.pred_frozen):+d}")
(OUT/'MACRO_REVERSAL_AUDIT_R1.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
