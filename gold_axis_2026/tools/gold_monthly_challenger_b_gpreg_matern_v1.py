#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,math,os,platform
from collections import Counter
from pathlib import Path
import numpy as np, psycopg, sklearn
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel,Matern
from sklearn.preprocessing import StandardScaler
import vw_midas_msvr_successor_v1 as base

MODEL_ID="GOLD_MONTHLY_CHALLENGER_B_GPREG_MATERN_V1"
FREEZE_FILE="GOLD_MONTHLY_CHALLENGER_B_GPREG_MATERN_FREEZE_2026-09-28.md"
TRAIN_START="2010-05"; INNER_VAL_MONTHS=12; MIN_INNER_TRAIN=36
LENGTH_SCALES=(0.5,1.0,2.0,5.0); SIGNAL_SCALES=(1.0,); ALPHAS=(1e-3,1e-2,1e-1); NUS=(0.5,1.5,2.5)
DEV_START,DEV_END="2022-04","2024-12"; HOLDOUT_START,HOLDOUT_END="2025-01","2025-12"; STRESS_START,STRESS_END="2026-01","2026-07"
FRONTIER=[
{"model":"ChHHO-ANFIS","family":"ANFIS","sum_abs_error":1413.029779,"direction_correct":23,"approximate":False},
{"model":"RBFNN DE-ABC","family":"RBFNN","sum_abs_error":1415.8371,"direction_correct":25,"approximate":True},
{"model":"PLS1 V1","family":"Challenger-B","sum_abs_error":1420.0291314697745,"direction_correct":20,"approximate":False},
{"model":"GPR/MOGP LMC2_RBF_M32","family":"GPR/MOGP","sum_abs_error":1424.17,"direction_correct":19,"approximate":True},
{"model":"FULL7 Equal ANN Ensemble","family":"ANN","sum_abs_error":1428.86,"direction_correct":22,"approximate":False},
{"model":"REDUCED4 Equal ANN Ensemble","family":"ANN","sum_abs_error":1431.46,"direction_correct":24,"approximate":False},
{"model":"SVR frozen parent","family":"SVR","sum_abs_error":1449.187363,"direction_correct":19,"approximate":False},
{"model":"CatBoost PRICE","family":"Boosting","sum_abs_error":1460.433935309605,"direction_correct":20,"approximate":False},
{"model":"PLS2 V1","family":"Challenger-B","sum_abs_error":1489.3300296660234,"direction_correct":23,"approximate":False},
{"model":"Random Forest comparator","family":"RF","sum_abs_error":1491.550693715667,"direction_correct":20,"approximate":False},
{"model":"Ridge V1","family":"Challenger-B","sum_abs_error":1520.9926031249222,"direction_correct":21,"approximate":False},
{"model":"Huber V1","family":"Challenger-B","sum_abs_error":1530.1299616481554,"direction_correct":20,"approximate":False},
{"model":"Elastic Net V1","family":"Challenger-B","sum_abs_error":1590.3570524947138,"direction_correct":16,"approximate":False},
{"model":"GPReg-RBF V1","family":"Challenger-B","sum_abs_error":1696.3365035638303,"direction_correct":16,"approximate":False},
]
def read_invariants(dsn):
  with psycopg.connect(dsn,autocommit=True) as c:
    with c.cursor() as cur:
      cur.execute("SET default_transaction_read_only=on"); return base.authority_invariants(cur)
def xonly(bundle,target,gh):
  p=base.month_shift(target,-1); pp=base.month_shift(target,-2); z=base.gpr_norm(gh,pp); x=[]
  for m in base.METALS:
    M=bundle.monthly_metal[m]
    if p not in M or pp not in M: raise RuntimeError("FEATURE_MISSING")
    x.extend((math.log(float(M[p])/float(M[pp])),base.weighted_daily_return(bundle,m,p,z)))
  a=np.asarray(x,float)
  if a.shape!=(8,) or not np.isfinite(a).all(): raise RuntimeError("CURRENT8_FAIL")
  return a
def data(bundle,target):
  origin=base.month_shift(target,-1)
  if origin not in bundle.gpr_vintages: raise RuntimeError("GPR_VINTAGE_MISSING")
  gh=bundle.gpr_vintages[origin]; samples={}
  for t in base.month_range(TRAIN_START,origin):
    try:samples[t]=base.sample_for_target(bundle,t,gh,True)
    except RuntimeError:continue
  keys=sorted(k for k in samples if TRAIN_START<=k<=origin)
  if len(keys)<INNER_VAL_MONTHS+MIN_INNER_TRAIN:raise RuntimeError("TRAIN_TOO_SMALL")
  s=len(keys)-INNER_VAL_MONTHS; tr,va=keys[:s],keys[s:]
  Xtr=np.stack([samples[k][0] for k in tr]); ytr=np.asarray([samples[k][1][0] for k in tr],float)
  Xv=np.stack([samples[k][0] for k in va]); prev=np.asarray([bundle.core_gold[base.month_shift(k,-1)] for k in va],float); act=np.asarray([bundle.core_gold[k] for k in va],float)
  Xall=np.stack([samples[k][0] for k in keys]); yall=np.asarray([samples[k][1][0] for k in keys],float); xt=xonly(bundle,target,gh).reshape(1,-1)
  return {"origin":origin,"keys":keys,"tr":tr,"va":va,"Xtr":Xtr,"ytr":ytr,"Xv":Xv,"prev":prev,"act":act,"rw":float(np.abs(prev-act).sum()),"Xall":Xall,"yall":yall,"xt":xt,"anchor":float(bundle.core_gold[origin])}
def fit(X,y,ls,ss,alpha,nu):
  sc=StandardScaler(); Xs=sc.fit_transform(X)
  k=ConstantKernel(ss,constant_value_bounds="fixed")*Matern(ls,length_scale_bounds="fixed",nu=nu)
  m=GaussianProcessRegressor(kernel=k,alpha=alpha,normalize_y=True,optimizer=None,random_state=42)
  m.fit(Xs,y); return sc,m
def pred(X,y,Xt,ls,ss,a,nu,std=False):
  sc,m=fit(X,y,ls,ss,a,nu)
  if std:
    p,s=m.predict(sc.transform(Xt),return_std=True); return np.asarray(p,float),np.asarray(s,float),m
  return np.asarray(m.predict(sc.transform(Xt)),float),None,m
def choose(d):
  den=max(d["rw"],1e-12); scored=[]
  for ls in LENGTH_SCALES:
    for ss in SIGNAL_SCALES:
      for a in ALPHAS:
        for nu in NUS:
          p,_,_=pred(d["Xtr"],d["ytr"],d["Xv"],ls,ss,a,nu)
        fc=d["prev"]*np.exp(p); sae=float(np.abs(fc-d["act"]).sum())
        scored.append({"length_scale":ls,"signal_scale":ss,"alpha":a,"nu":nu,"inner_sum_abs_error":sae,"inner_relative_sum_abs_error_vs_rw":sae/den})
  scored.sort(key=lambda r:(r["inner_relative_sum_abs_error_vs_rw"],r["length_scale"],r["alpha"],r["nu"]))
  b=scored[0]; return b["length_scale"],b["signal_scale"],b["alpha"],b["nu"],scored
def one(bundle,target):
  d=data(bundle,target); ls,ss,a,nu,scores=choose(d); p,s,m=pred(d["Xall"],d["yall"],d["xt"],ls,ss,a,nu,True)
  r=float(p[0]); sd=float(s[0])
  if not math.isfinite(r) or abs(r)>=1: raise RuntimeError("PRED_FAIL")
  fc=d["anchor"]*math.exp(r); actual=float(bundle.core_gold[target]); rw=d["anchor"]
  return {"target":target,"origin":d["origin"],"train_rows":len(d["keys"]),"train_first":d["keys"][0],"train_last":d["keys"][-1],
          "inner_val_first":d["va"][0],"inner_val_last":d["va"][-1],"selected_length_scale":ls,"selected_signal_scale":ss,"selected_alpha":a,"selected_nu":nu,
          "candidate_scores":scores,"pred_log_return_gold":r,"predictive_std_log_return":sd,"forecast":fc,"actual":actual,"rw":rw,
          "absolute_error":abs(fc-actual),"rw_absolute_error":abs(rw-actual),
          "direction_correct":bool(int(np.sign(fc-rw))==int(np.sign(actual-rw)))}
def metrics(rows):
  a=np.array([r["actual"] for r in rows]); f=np.array([r["forecast"] for r in rows]); rw=np.array([r["rw"] for r in rows]); ae=np.abs(f-a); rwae=np.abs(rw-a); dc=np.array([r["direction_correct"] for r in rows]); wi=int(np.argmax(ae))
  return {"n":len(rows),"sum_abs_error":float(ae.sum()),"mae":float(ae.mean()),"rmse":float(np.sqrt(np.mean((f-a)**2))),"mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100),"wape_pct":float(ae.sum()/np.abs(a).sum()*100),"median_ae":float(np.median(ae)),"worst_ae":float(ae[wi]),"worst_month":rows[wi]["target"],"relative_mae_vs_rw":float(ae.sum()/max(rwae.sum(),1e-12)),"rw_sum_abs_error":float(rwae.sum()),"direction_correct":int(dc.sum()),"direction_accuracy_pct":float(dc.mean()*100),"mean_predictive_std_log_return":float(np.mean([r["predictive_std_log_return"] for r in rows]))}
def run(bundle,start,end,label):
  rows=[]; ts=list(base.month_range(start,end))
  for i,t in enumerate(ts,1):
    r=one(bundle,t);rows.append(r);print(f"PROGRESS {label} {i}/{len(ts)} {t} ls={r['selected_length_scale']} ss={r['selected_signal_scale']} a={r['selected_alpha']} nu={r['selected_nu']} AE={r['absolute_error']:.6f} dir={int(r['direction_correct'])}",flush=True)
  return {"role":label,"metrics":metrics(rows),"selected_length_scale_counts":dict(Counter(str(r["selected_length_scale"]) for r in rows)),"selected_signal_scale_counts":dict(Counter(str(r["selected_signal_scale"]) for r in rows)),"selected_alpha_counts":dict(Counter(str(r["selected_alpha"]) for r in rows)),"selected_nu_counts":dict(Counter(str(r["selected_nu"]) for r in rows)),"rows":rows}
def compare(dm):
  me={"model":"GPReg-Matérn V1","family":"Challenger-B","sum_abs_error":dm["sum_abs_error"],"direction_correct":dm["direction_correct"],"approximate":False}; allr=[dict(x) for x in FRONTIER]+[me]; ranked=sorted(allr,key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["model"]))
  for i,r in enumerate(ranked,1):r["price_error_rank"]=i
  rank=next(r["price_error_rank"] for r in ranked if r["model"]=="GPReg-Matérn V1")
  dom=[r["model"] for r in allr if r["model"]!="GPReg-Matérn V1" and r["sum_abs_error"]<=me["sum_abs_error"] and r["direction_correct"]>=me["direction_correct"] and (r["sum_abs_error"]<me["sum_abs_error"] or r["direction_correct"]>me["direction_correct"])]
  return {"ranking_by_primary_sumae":ranked,"gpreg_matern_price_error_rank":rank,"comparison_pool_n":len(ranked),"pareto_dominated_by":dom,"pareto_nondominated_within_pool":not dom}
def main():
  dsn=os.environ["NEON_DATABASE_URL"]; bundle=base.load_data(dsn)
  b0={"source_checks":bundle.source_checks,"gate_pass":not bundle.source_checks["missing_required_gpr_origins"] and not bundle.source_checks["late_required_gpr_origins"] and not bundle.source_checks["missing_required_gpr_lag_month"]}
  if not b0["gate_pass"]:raise RuntimeError("B0_FAIL")
  dev=run(bundle,DEV_START,DEV_END,"DEV_SELECTION_AUTHORITY"); hold=run(bundle,HOLDOUT_START,HOLDOUT_END,"LOCKED_REPORT_ONLY"); stress=run(bundle,STRESS_START,STRESS_END,"QUARANTINED_REPORT_ONLY")
  after=read_invariants(dsn); same=after==bundle.invariants_before
  if not same:raise RuntimeError("AUTHORITY_CHANGED")
  comp=compare(dev["metrics"]); digest=hashlib.sha256(json.dumps({"dev":dev["rows"],"hold":hold["rows"],"stress":stress["rows"]},sort_keys=True,separators=(",",":")).encode()).hexdigest()
  out={"model_id":MODEL_ID,"freeze_file":FREEZE_FILE,"scientific_gate":"PASS","contract":{"target":"H=1 next-calendar-month average XAU/USD","training_target":"Gold next-month log return","representation":"CURRENT8","training_start":TRAIN_START,"length_scale_grid":list(LENGTH_SCALES),"signal_scale_grid":list(SIGNAL_SCALES),"alpha_grid":list(ALPHAS),"nu_grid":list(NUS),"kernel":"ConstantKernel(fixed)*Matern(fixed length_scale, nu)","normalize_y":True,"optimizer":None,"random_state":42,"scaling":"StandardScaler X only; training-fold fit","random_split":"NONE","database":"READ_ONLY","2025_role":"LOCKED_REPORT_ONLY","2026_role":"QUARANTINED_REPORT_ONLY"},"b0_audit":b0,"authority_invariants_before":bundle.invariants_before,"authority_invariants_after":after,"authority_invariants_unchanged":same,"software":{"python":platform.python_version(),"numpy":np.__version__,"scikit_learn":sklearn.__version__},"dev":dev,"holdout_2025":hold,"stress_2026":stress,"challenger_a_comparison":comp,"result_payload_sha256":digest}
  Path("gold_monthly_challenger_b_gpreg_matern_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
  print("GPREG_MATERN_CHALLENGER_OUTPUT_GATE=PASS",flush=True); print(json.dumps({"dev_metrics":dev["metrics"],"rank":comp["gpreg_matern_price_error_rank"],"dominated_by":comp["pareto_dominated_by"],"holdout_2025_metrics":hold["metrics"],"stress_2026_metrics":stress["metrics"],"authority_invariants_unchanged":same,"sha256":digest},sort_keys=True),flush=True)
if __name__=="__main__":main()
