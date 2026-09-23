import os
import json, math, sys, csv, hashlib, importlib.util
from pathlib import Path
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
from collections import Counter
import numpy as np
import pandas as pd

ROOT=Path(os.environ.get("GOLD_AUDIT_WORKDIR", str(Path(__file__).parent)))
OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
def load(group,name):
 p=ROOT/group/'gold_axis_2026/tools'/name
 spec=importlib.util.spec_from_file_location(group+'_'+p.stem,p);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
def save(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2,default=str))
def compare(a,b,fields,label):
 out=[]
 for f in fields:
  aa=np.asarray(a[f],float);bb=np.asarray(b[f],float);dif=np.abs(aa-bb);good=np.isclose(aa,bb,atol=1e-12,rtol=1e-9)
  out.append(dict(component=label,field=f,total=len(aa),exact=int(np.sum(aa==bb)),matched=int(good.sum()),mismatched=int((~good).sum()),max_abs=float(dif.max()),max_rel=float(np.max(dif/np.maximum(np.abs(bb),1e-30))),tolerance='atol=1e-12,rtol=1e-9',first_mismatch_dates=list(a.loc[~good,'origin_date'].head(5)) if 'origin_date' in a else []))
 return out
raw=[]
for y in range(2020,2027):raw+=json.loads((ROOT/f'raw_{y}.json').read_text())[0]['bars']
df=pd.DataFrame(raw,columns=['ts','close']);df['dt']=pd.to_datetime(df.ts,unit='s',utc=True).dt.tz_convert('America/New_York');df['date']=df.dt.dt.date
daily=[]; paths={};stats=[]
for d,g in df.groupby('date',sort=True):
 p=g.close.to_numpy(float);r=np.log(p[1:]/p[:-1]);n=len(p);gap=np.diff(g.ts.to_numpy());weekday=d.weekday()<5
 stats.append(dict(date=str(d),n=n,weekday=weekday,retained=weekday and n>=240,missing_grid_inside=int(np.sum(np.maximum(gap/300-1,0))),first=str(g.dt.iloc[0]),last=str(g.dt.iloc[-1]),zero_returns=int(np.sum(r==0)),max_abs_return=float(np.max(np.abs(r))) if len(r) else 0))
 if not weekday or n<240:continue
 paths[str(d)]=r;rv=float(r@r);dr=float(r[r<0]@r[r<0]);cum=np.cumsum(r);lo=float(cum.min());hi=float(cum.max());end=float(cum[-1]);scale=math.sqrt(rv);qn=math.ceil(len(r)/4)
 daily.append(dict(date=str(d),close=p[-1],n_bars=n,m_returns=len(r),rv=rv,r3=float(np.sum(r**3)),rs_plus=float(r[r>0]@r[r>0]),rs_minus=dr,dr=dr,sd=math.sqrt(dr),downside_share=dr/rv,intraday_end_norm=end/scale,close_location=(end-lo)/(hi-lo) if hi-lo>1e-15 else .5,trough_recovery_norm=(end-lo)/scale,last_quarter_return_norm=float(r[-qn:].sum())/scale))
D=pd.DataFrame(daily);D['lag1_close_return']=np.log(D.close/D.close.shift(1));D.to_csv(OUT/'daily_recomputed.csv',index=False);pd.DataFrame(stats).to_csv(OUT/'calendar_integrity.csv',index=False)
save('raw_summary.json',dict(rows=len(df),duplicates=int(df.ts.duplicated().sum()),retained_days=len(D),date_from=D.date.iloc[0],date_to=D.date.iloc[-1],by_year={str(y):dict(raw=int((df.dt.dt.year==y).sum()),retained=int(D.date.str.startswith(str(y)).sum())) for y in range(2020,2027)},extreme_return_dates=[x for x in stats if x['max_abs_return']>.05],weekend_bars=int((df.dt.dt.dayofweek>=5).sum())))
rows=[]
for i in range(21,len(D)-1):
 a=D.iloc[i];b=D.iloc[i+1]
 rows.append(dict(origin_date=a.date,target_date=b.date,dr_d=a.dr,dr_w=D.dr.iloc[i-4:i+1].mean(),dr_m=D.dr.iloc[i-21:i+1].mean(),sd_d=a.sd,sd_w=D.sd.iloc[i-4:i+1].mean(),sd_m=D.sd.iloc[i-21:i+1].mean(),target_dr=b.dr,target_sd=b.sd,target_close_return=math.log(b.close/a.close)))
R=pd.DataFrame(rows);forecasts=[];formation=[]
for y in range(2022,2027):
 tr=R[R.target_date<str(y)];te=R[R.target_date.str.startswith(str(y))].copy();assert len(tr)>=250
 X=np.column_stack([np.ones(len(tr)),tr[['sd_d','sd_w','sd_m']]]);beta=np.linalg.lstsq(X,tr.target_sd,rcond=None)[0]
 sd=np.column_stack([np.ones(len(te)),te[['sd_d','sd_w','sd_m']]])@beta;assert (sd>0).all()
 q=np.sort(tr.target_dr)[math.ceil(.8*len(tr))-1]
 te['sqrt_har_sd_forecast']=sd;te['sqrt_har_dr_forecast']=sd**2;te['high_risk_threshold']=q;te['sqrt_normalized_risk_score']=sd**2/q;te['sqrt_high_risk_alert']=(sd**2>=q).astype(int);te['formation_n']=len(tr);forecasts.append(te)
 formation.append(dict(year=y,n=len(tr),q80=q,beta=beta.tolist(),alarm_count=int(te.sqrt_high_risk_alert.sum())))
F=pd.concat(forecasts,ignore_index=True);F.to_csv(OUT/'sqrt_recomputed.csv',index=False);save('formation.json',formation)
frozen=pd.read_csv(next((ROOT/'sqrt/gold_axis_2026').glob('*RAW_VS_SQRT*FORECASTS*.csv')))
J=F.merge(frozen,on=['origin_date','target_date'],suffixes=('_new','_old'),validate='one_to_one');fields=[f for f in F.columns if f not in ['origin_date','target_date'] and f in frozen]
aa=pd.DataFrame({f:J[f+'_new'] for f in fields});bb=pd.DataFrame({f:J[f+'_old'] for f in fields});aa['origin_date']=J.origin_date
comparisons=compare(aa,bb,fields,'SQRT');save('sqrt_comparison.json',dict(recomputed=len(F),frozen=len(frozen),joined=len(J),fields=comparisons))
up=pd.read_csv(next((ROOT/'up2/gold_axis_2026').glob('*ONE_SIDED_UP2*LEDGER*.csv')))
features=['lag1_close_return','downside_share','intraday_end_norm','close_location','trough_recovery_norm','last_quarter_return_norm']
U=up.merge(D,left_on='origin_date',right_on='date',suffixes=('_old','_new'),validate='many_to_one')
aa=pd.DataFrame({f:U[f+'_new'] for f in features});bb=pd.DataFrame({f:U[f+'_old'] for f in features});aa['origin_date']=U.origin_date
save('up2_raw_comparison.json',compare(aa,bb,features,'UP2'))
uf=up.merge(F,on=['origin_date','target_date'],suffixes=('_old','_new'),validate='one_to_one')
save('up2_route_label.json',dict(rows=len(up),joined=len(uf),not_high_risk=int((uf.sqrt_high_risk_alert!=1).sum()),sqrt_score_mismatch=int((~np.isclose(uf.sqrt_score,uf.sqrt_normalized_risk_score,rtol=1e-9,atol=1e-12)).sum()),label_mismatch=int((uf.actual_up!=(uf.target_close_return>0)).sum()),threshold_predicate_mismatch=int((up.up2_call!=(up.p_up>up.tau)).sum()),counts={str(y):dict(n=len(z),up=int(z.actual_up.sum()),calls=int(z.up2_call.sum()),true=int(((z.actual_up==1)&(z.up2_call==1)).sum()),false=int(((z.actual_up==0)&(z.up2_call==1)).sum())) for y,z in up.groupby('evaluation_year')}))
np.savez_compressed(OUT/'retained_paths.npz',**paths)
print(json.dumps(dict(raw=len(df),days=len(D),sqrt_rows=len(J),sqrt_mismatch_fields=[x for x in comparisons if x['mismatched']],up2_rows=len(up)),default=str),flush=True)

# Execute frozen expert construction against independently computed live-source moments.
sys.path[:0]=[str(ROOT/'base/gold_axis_2026'),str(ROOT/'base/gold_axis_2026/tools')]
base=load('base','down_verifier_candidate_audit_v1_run.py');bd=[base.BaseDay(date.fromisoformat(r.date),r.close,int(r.n_bars),int(r.m_returns),r.rv,r.r3,r.rs_plus,r.rs_minus) for r in D.itertuples() if r.date<'2026-01-02']
t,b,l,dd=base.transformed(bd); print('Reproducing direct experts',flush=True)
tm=base.ttsm_mod.build_signal_rows(t);bm=base.bonato_maps(b);lm=base.logit_maps(l);ctx=base.legacy_context(dd);router=base.build_router_rows(tm,bm,lm,ctx)
P=pd.DataFrame(router);P.to_csv(OUT/'router_recomputed.csv',index=False)
save('router_counts.json',{str(y):dict(n=len(z),calls=int(z.router_up.sum()),true=int(((z.router_up==1)&(z.actual_up==1)).sum()),false=int(((z.router_up==1)&(z.actual_up==0)).sum())) for y,z in P.groupby(P.target_date.str[:4])})
ur=up.merge(P,on=['origin_date','target_date'],suffixes=('_old','_new'),validate='one_to_one')
save('up2_router_comparison.json',dict(rows=len(ur),not_abstain=int(ur.router_up.sum()),direct_mismatch=int((~np.isclose(ur.direct_up_fraction,ur[base.DIRECT_UP_EXPERTS].sum(axis=1)/5)).sum()),legacy_mismatch=int((~np.isclose(ur.legacy_up_fraction,ur.legacy_up_count/3)).sum()),label_mismatch=int((ur.actual_up_old!=ur.actual_up_new).sum())))
print('Router reproduction complete',flush=True)
