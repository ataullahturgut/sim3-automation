import os
import json,math
from pathlib import Path
from statistics import NormalDist
import pandas as pd,numpy as np
R=Path(os.environ.get("GOLD_AUDIT_WORKDIR", str(Path(__file__).parent)));O=R/'results'
P=pd.read_csv(O/'router_recomputed.csv').fillna(''); experts=['TTSM_S2','TTSM_S1','BONATO_AR1_RM_QBOOST_H1','AR1_RM_LOGIT','RM_LOGIT'];z=NormalDist().inv_cdf(.9)
hist=P[P.target_date.str.startswith('2023')].to_dict('records');checked=[];maturity=[]
for r in P[P.target_date.str[:4].isin(['2024','2025'])].to_dict('records'):
 assert all(h['target_date']<=r['origin_date'] for h in hist)
 bucket=[h for h in hist if sum(h[k] for k in ['FAST_UP','SLOW_UP','MONTHLY_UP'])>=2] if r['legacy_bucket']=='CONSENSUS_UP' else [h for h in hist if sum(h[k] for k in ['FAST_UP','SLOW_UP','MONTHLY_UP'])<2]
 candidates=[]
 for i,e in enumerate(experts):
  if not r[e]:continue
  pop=bucket if sum(h[e] for h in bucket)>=30 else hist;calls=[h for h in pop if h[e]];n=len(calls)
  if n<30:continue
  tp=sum(h['actual_up'] for h in calls);p=tp/n;nd=sum(1-h['actual_up'] for h in pop);f=(n-tp)/nd if nd else 1
  if p<=.5 or f>=.5:continue
  l=(p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)
  candidates.append((-l,f,-p,i,e))
 winner=min(candidates)[-1] if candidates else '';checked.append(dict(origin_date=r['origin_date'],target_date=r['target_date'],expected=winner,stored=r['selected_expert'],match=winner==r['selected_expert']))
 maturity.append(dict(origin_date=r['origin_date'],latest_matured_target=max(h['target_date'] for h in hist),history_n=len(hist)))
 hist.append(r)
pd.DataFrame(checked).to_csv(O/'router_independent_selection.csv',index=False)
(O/'chronology.json').write_text(json.dumps(dict(router_checked=len(checked),selection_mismatches=sum(not x['match'] for x in checked),maturity_violations=sum(x['latest_matured_target']>x['origin_date'] for x in maturity),latest_history_rule='target_date <= completed origin date',zero_target_returns=int((pd.read_csv(O/'sqrt_recomputed.csv').target_close_return==0).sum())),indent=2))
# Representative raw-to-feature trace, chosen by coverage and declared state only.
D=pd.read_csv(O/'daily_recomputed.csv');F=pd.read_csv(O/'sqrt_recomputed.csv');U=pd.read_csv(O/'up2_refit.csv');C=pd.read_csv(O/'calendar_integrity.csv');dates={}
for label,sub in [('normal',F[F.sqrt_high_risk_alert==0]),('high_risk',F[F.sqrt_high_risk_alert==1]),('primary_up',P[P.router_up==1]),('primary_abstain',P[P.router_up==0]),('up2_true',U[(U.up2_call==1)&(U.actual_up==1)]),('up2_false',U[(U.up2_call==1)&(U.actual_up==0)])]:
 for d in sub.origin_date.head(2):dates.setdefault(d,[]).append(label)
for d in ['2023-03-22','2023-08-08','2025-10-10','2026-01-31']:
 dates.setdefault(d,[]).append('source_edge')
trace=[]
for d,labels in dates.items():
 dr=D[D.date==d];cr=C[C.date==d];fr=F[F.origin_date==d];ur=U[U.origin_date==d];pr=P[P.origin_date==d]
 trace.append(dict(date=d,categories=labels,calendar=cr.to_dict('records'),derived=dr.to_dict('records'),sqrt=fr.to_dict('records'),router=pr.to_dict('records'),up2=ur.to_dict('records')))
(O/'spot_checks.json').write_text(json.dumps(trace,indent=2,default=str))
print('Independent router selection:',len(checked),'mismatches:',sum(not x['match'] for x in checked))
