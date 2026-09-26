"""Frozen LMC candidate runner; production requires Stage3AB closure.
Formal candidate authority must be committed with activation before execution.
"""
import hashlib,json,math,os,time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
import gpr_experiment_v1 as e
import gpr_lmc_core_v1 as l

METHOD='LMC2_RBF_M32'

def tune(samples,target,method):
 keys,X,Y,split,sc=e.prepare(samples,target);seed=int(hashlib.sha256(target.encode()).hexdigest()[:8],16);records=[];best=None
 for rep in range(3):
  rng=np.random.default_rng((seed+7777*rep+1911)%(2**32));start=l.PRIOR.copy() if rep==0 else np.clip(l.PRIOR+rng.normal(0,.15,40),l.LOW,l.HIGH)
  calls=[0]
  def loss(theta):
   calls[0]+=1
   try:
    nll,grad=l.value_gradient(theta,X[:split],Y[:split]);return (nll+.5*np.sum((theta-l.PRIOR)**2))/(4*split),(grad+theta-l.PRIOR)/(4*split)
   except (e.gp.ScientificFailure,np.linalg.LinAlgError):return math.inf,np.zeros(40)
  fit=minimize(loss,start,method='L-BFGS-B',jac=True,bounds=list(zip(l.LOW,l.HIGH)),options={'maxiter':60,'maxfun':1600,'ftol':1e-7})
  f=l.fit(fit.x,X[:split],Y[:split]);p,_=l.predict(f,X[split:],False);score=e.r.common.weighted_mae_from_pred(p,Y[split:])
  records.append({'repeat':rep,'seed':(seed+7777*rep+1911)%(2**32),'validation_loss':float(score),'training_objective':float(fit.fun),'optimizer_success':bool(fit.success),'message':str(fit.message),'evaluations':calls[0]})
  if np.isfinite(score) and (best is None or score<best[0]):best=(score,fit.x.copy(),rep)
 if best is None:raise e.gp.ScientificFailure('NO_VALID_LMC_FIT')
 return best[1],sc,{'theta':best[1].tolist(),'kind':'LMC2_RBF_M32','single':False,'prior_strength':1.,'selected_repeat':best[2],'repeat_records':e.finite(records),
   'inner_train_last':keys[split-1],'validation_first':keys[split],'validation_last':keys[-1],'tuning_last':keys[-1]}

def forecast(samples,target,frozen):
 theta,sc,meta=frozen;keys=sorted(k for k in samples if k<target);xm,xs,ym,ys=sc
 X=(np.stack([samples[k][0] for k in keys])-xm)/xs;Y=(np.stack([samples[k][1] for k in keys])-ym)/ys
 f=l.fit(theta,X,Y);p,v=l.predict(f,(samples[target][0][None,:]-xm)/xs);mu=p[0]*ys+ym;var=v[0]*ys**2
 if not np.isfinite(mu).all() or max(abs(mu))>=1 or not np.isfinite(var).all() or var.min()<=0:raise e.gp.ScientificFailure('PATHOLOGICAL_LMC_PREDICTION')
 return mu,var,{**meta,'train_last':keys[-1],'train_rows':len(keys),'theta_sha256':hashlib.sha256(theta.tobytes()).hexdigest(),'observation_return_variance':var.tolist(),'condition_upper_bound':f['condition_upper_bound']}

def run():
 root=Path('gold_axis_2026');closure=root/'GOLD_MONTHLY_GPR_STAGE3AB_CLOSURE_2026-09-26.json';assert json.loads(closure.read_text())['status']=='COMPLETE'
 authority=root/'GOLD_MONTHLY_GPR_STAGE3C_AUTHORITY_2026-09-26.md';assert authority.exists()
 e.tune=tune;e.forecast=forecast;b=e.r.base.load_data(os.environ['NEON_DATABASE_URL']);start=time.time()
 d={'method':METHOD,'stage':'3C','model_id':'GPR_LMC2_V1','run_id':os.getenv('GITHUB_RUN_ID'),'commit':os.getenv('GITHUB_SHA'),
 'authority_document_sha256':hashlib.sha256(authority.read_bytes()).hexdigest(),'stage3ab_closure_sha256':hashlib.sha256(closure.read_bytes()).hexdigest(),
 'spec':{'outputs':4,'bounds':[l.LOW.tolist(),l.HIGH.tolist()],'posterior':'exact dense LMC sum of two separable kernels','kernels':['ARD_RBF','ARD_M32'],'task_covariances':'two learned full-rank PSD Cholesky factors','parameters':40,'optimizer':'L-BFGS-B with exact analytic NLL gradient','repeats':3,'maxiter':60,'maxfun':1600,'prior_strength':1.,'condition_upper_bound_limit':1e12,'jitter':e.gp.JITTER},
 'authority':{'selection':'DEV_ONLY','database':'READ_ONLY','2025':'REPORT_ONLY','2026':'REPORT_ONLY','random_split':False,'source_checks':b.source_checks,'invariants_before':b.invariants_before}}
 path=Path('gpr_lmc2_rbf_m32_result.json');d['dev']=e.evaluate(b,METHOD,'2022-04','2024-12');d['dev_decision_frozen_before_external']='ELIGIBLE' if d['dev']['scientific_gate']=='PASS' else 'REJECTED_SCIENTIFIC_FAILURE'
 d['dev_freeze_sha256']=hashlib.sha256(json.dumps(d['dev'],sort_keys=True).encode()).hexdigest();path.write_text(json.dumps(e.finite(d),indent=2,sort_keys=True)+'\n')
 frozen=tune(e.r.base.all_samples_at_origin(b,'2025-01',governed=True),'2025-01',METHOD)
 d['external_freeze']={'tuning_last':frozen[2]['tuning_last'],'theta_sha256':hashlib.sha256(frozen[0].tobytes()).hexdigest(),'scaler_sha256':hashlib.sha256(np.concatenate(frozen[1]).tobytes()).hexdigest()}
 d['transport_2025']=e.evaluate(b,METHOD,'2025-01','2025-12',frozen);d['stress_2026']=e.evaluate(b,METHOD,'2026-01','2026-07',frozen)
 d['authority']['invariants_after']=e.r.vanilla.read_invariants(os.environ['NEON_DATABASE_URL']);assert d['authority']['invariants_after']==b.invariants_before
 d['status']='COMPLETE';d['seconds']=time.time()-start;path.write_text(json.dumps(e.finite(d),indent=2,sort_keys=True,allow_nan=False)+'\n');print(json.dumps(d['dev']['metrics']),flush=True)
if __name__=='__main__':run()
