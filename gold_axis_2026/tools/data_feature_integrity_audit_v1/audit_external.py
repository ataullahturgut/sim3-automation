import os
import sys,json,importlib.util,math
from pathlib import Path
import numpy as np,pandas as pd
R=Path(os.environ.get("GOLD_AUDIT_WORKDIR", str(Path(__file__).parent)));O=R/'results'
sys.path[:0]=[str(R/'base/gold_axis_2026'),str(R/'base/gold_axis_2026/tools')]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def save(n,x):(O/n).write_text(json.dumps(x,indent=2,default=str))
base=load('base_ext',R/'base/gold_axis_2026/tools/down_verifier_candidate_audit_v1_run.py')
route=load('route_ext',R/'route/gold_axis_2026/tools/cbr_cascade_route_consistent_extension_v1_run.py')
up=load('up_ext',R/'up2/gold_axis_2026/tools/residual_one_sided_up2_logit_v1_run.py')
iw=load('iw_ext',R/'iw/gold_axis_2026/tools/up2_importance_weighted_source_adaptation_v1.py')
mech=load('mech_ext',R/'mechanism/gold_axis_2026/tools/direction_mechanism_gap_audit_v1.py')
sqrt=route.load_sqrt_mod(R/'external_sqrt.py');spine=route.load_external_spine(R/'external_daily.csv')
raw=route.build_external_5m(R/'mdl');save('external_reconstruction.json',route.external_reconstruction_audit(raw,spine));print('External raw reconstructed',flush=True)
sr,ss=route.external_sqrt_cases(sqrt,route.load_external_daily_for_sqrt(spine));rr,rs=route.external_router_rows(base,spine);res,rc=route.route_external_sqrt_cases(sr,rr)
save('external_routes.json',dict(sqrt=ss,router=rs,residual=rc))
sm={(r['origin_date'],r['target_date']):r for r in sr};rm={(r['origin_date'],r['target_date']):r for r in rr};lag=up.lag_map_from_spine(spine)
train=[]
for r in res:
 key=(r['origin_date'],r['target_date']);train.append(up.enrich_case(r,sm[key]['sqrt_normalized_risk_score'],rm[key],lag[r['origin_date']],raw[r['origin_date']]['rets'],'EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN'))
pd.DataFrame(train).to_csv(O/'external_training_features.csv',index=False)
ledger=pd.read_csv(next((R/'up2/gold_axis_2026').glob('*ONE_SIDED_UP2*LEDGER*.csv')))
verified=ledger.copy();D=pd.read_csv(O/'daily_recomputed.csv').set_index('date');P=pd.read_csv(O/'router_recomputed.csv').set_index(['origin_date','target_date']);F=pd.read_csv(O/'sqrt_recomputed.csv').set_index(['origin_date','target_date'])
for idx,row in verified.iterrows():
 key=(row.origin_date,row.target_date);day=D.loc[row.origin_date];rr0=P.loc[key];ff=F.loc[key]
 for f in ['lag1_close_return','downside_share','intraday_end_norm','close_location','trough_recovery_norm','last_quarter_return_norm']:verified.at[idx,f]=day[f]
 verified.at[idx,'sqrt_score']=ff.sqrt_normalized_risk_score
 verified.at[idx,'direct_up_fraction']=sum(rr0[k] for k in base.DIRECT_UP_EXPERTS)/5
 verified.at[idx,'legacy_up_fraction']=rr0.legacy_up_count/3
 verified.at[idx,'actual_up']=int(ff.target_close_return>0)
 assert rr0.router_up==0 and ff.sqrt_high_risk_alert==1
verified.to_csv(O/'up2_verified_model_inputs.csv',index=False)
pre=verified[verified.evaluation_year<2025].to_dict('records');hist=train+pre
sc=[];metrics={}
for y in [2022,2023,2024,2025]:
 tr=[r for r in hist if r['evaluation_year']<y];te=verified[verified.evaluation_year==y].to_dict('records');z,m=up.score_year(tr,te,y);sc+=z;metrics[str(y)]=m
S=pd.DataFrame(sc);S.to_csv(O/'up2_refit.csv',index=False);save('up2_refit_metrics.json',metrics)
diff=S.p_up.to_numpy()-ledger.p_up.to_numpy();save('up2_refit_comparison.json',dict(rows=len(S),p_max_abs=float(abs(diff).max()),p_mismatch=int((abs(diff)>1e-9).sum()),tau_max_abs=float(abs(S.tau-ledger.tau).max()),call_mismatch=int((S.up2_call!=ledger.up2_call).sum())))
source,_,_,_=iw.source_rows(route,sqrt,base,mech,spine,raw)
paths=dict(np.load(O/'retained_paths.npz'));target,errs=iw.target_call_rows(ledger.to_dict('records'),paths,mech);adapt=[r for r in target if r['evaluation_year']==2022]
weights=iw.fit_domain_weights(source,adapt);model,mu,sd=iw.fit_failure(source,weights['weights']);scored=iw.score(model,mu,sd,target)
pd.DataFrame(source).assign(weight=weights['weights'],raw_ratio=weights['raw_ratio']).to_csv(O/'iw_source_weights.csv',index=False);pd.DataFrame(scored).to_csv(O/'iw_recomputed.csv',index=False)
save('iw_reproduction.json',dict(source_n=len(source),source_up=sum(x['actual_up'] for x in source),target_n=len(adapt),ess=weights['ess'],weight_mean=float(weights['weights'].mean()),raw_max=float(weights['raw_ratio'].max()),errors=errs,locked2025=iw.summarize([r for r in scored if r['evaluation_year']==2025]),guard=iw.summarize([r for r in scored if r['evaluation_year'] in (2023,2024)])))
# Outcome invariance of unlabeled adaptation.
adapt_flip=[{**r,'actual_up':1-r['actual_up'],'failure':1-r['failure']} for r in adapt];wf=iw.fit_domain_weights(source,adapt_flip)
save('iw_label_invariance.json',dict(max_abs_weight_change=float(np.max(abs(weights['weights']-wf['weights'])))))
# Independent formulas for IW path features, every source and target row.
checks=[]
for group,cases,paths0 in [('source',source,{k:v['rets'] for k,v in raw.items()}),('target',target,paths)]:
 for row in cases:
  a=np.array(paths0[row['origin_date']]);q=math.ceil(len(a)/4);late=a[-q:];intensity=float((late[late<0]**2).sum()/(a*a).sum());p=np.r_[0,np.cumsum(a[-12:])];x=np.arange(len(p));xc=x-x.mean();pc=p-p.mean();sst=float(pc@pc);r2=float((xc@pc)**2/((xc@xc)*sst)) if sst>1e-15 else 0.
  checks.append(dict(group=group,origin_date=row['origin_date'],intensity_abs=abs(intensity-row['late_downside_intensity']),r2_abs=abs(r2-row['last_hour_trend_r2'])))
pd.DataFrame(checks).to_csv(O/'iw_independent_feature_comparison.csv',index=False)
print(json.dumps(dict(up2_p_max_abs=float(abs(diff).max()),iw_ess=weights['ess'],iw_2025=iw.summarize([r for r in scored if r['evaluation_year']==2025]))),flush=True)
