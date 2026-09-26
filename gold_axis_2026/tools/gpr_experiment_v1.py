"""Governed GP experiments: origin-safe exact posterior, DEV-only selection."""
import argparse,hashlib,importlib,inspect,json,math,os,time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
import gpr_core_v1 as gp
import vw_midas_rbfnn_stage1_v1 as r

BASELINES=['SO_RBF','VANILLA_ICM_RBF','ICM_M32','REGULARIZED_ICM_RBF']
REPEATS,POP,GENS=3,24,45

def finite(x):
 if isinstance(x,dict):return {k:finite(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [finite(v) for v in x]
 if isinstance(x,np.ndarray):return finite(x.tolist())
 if isinstance(x,(float,np.floating)):return float(x) if math.isfinite(x) else None
 if isinstance(x,np.integer):return int(x)
 return x

class Objective:
 def __init__(self,kind='RBF',strength=1.,single=False):self.kind=kind;self.strength=strength;self.single=single;self.train_calls=0;self.validation_calls=0;self.invalid=0
 def training(self,theta,X,Y):
  self.train_calls+=1
  try:
   f=gp.fit(theta,X,Y,self.kind,self.single);prior=.5*self.strength*np.sum((theta-gp.PRIOR)**2)
   return (f['nll']+prior)/(len(X)*(1 if self.single else 4))
  except (gp.ScientificFailure,np.linalg.LinAlgError):self.invalid+=1;return math.inf
 def validation(self,theta,X,Y,Xv,Yv):
  self.validation_calls+=1
  try:
   f=gp.fit(theta,X,Y,self.kind,self.single);p,_=gp.predict(f,Xv,False)
   return float(np.mean(abs(p[:,0]-Yv[:,0]))) if self.single else r.common.weighted_mae_from_pred(p,Yv)
  except (gp.ScientificFailure,np.linalg.LinAlgError):self.invalid+=1;return math.inf

def adapter(method,obj):
 c=r.common;c.PARAM_DIM=22;c.LOWER=gp.LOW;c.UPPER=gp.HIGH;c.POP_SIZE=POP
 c.LOCAL_SIGMA=.1*(gp.HIGH-gp.LOW);c.REFIT_SIGMA=.04*(gp.HIGH-gp.LOW)
 c.training_loss=obj.training;c.validation_loss=obj.validation
 batch=next(i+1 for i,v in enumerate(r.BATCHES) if method in v)
 mod=importlib.import_module(f'vw_midas_elmfis_meta_batch_{batch}_v1')
 mod.PARAM_DIM=22;mod.LOWER=gp.LOW;mod.UPPER=gp.HIGH;mod.SPAN=gp.HIGH-gp.LOW;mod.POP_SIZE=POP
 return mod,mod.PHASE[method]

def prepare(samples,target):
 keys=sorted(k for k in samples if k<target);X0=np.stack([samples[k][0] for k in keys]);Y0=np.stack([samples[k][1] for k in keys])
 split=len(keys)-max(6,round(.2*len(keys)));assert split>=30
 sc=r.vanilla.scale_fit(X0[:split],Y0[:split]);xm,xs,ym,ys=sc
 return keys,(X0-xm)/xs,(Y0-ym)/ys,split,sc

def tune(samples,target,method):
 keys,X,Y,split,sc=prepare(samples,target);kind='M32' if method=='ICM_M32' else 'RBF';single=method=='SO_RBF'
 strength=0. if method in ['SO_RBF','VANILLA_ICM_RBF','ICM_M32'] else 1.
 obj=Objective(kind,strength,single);seed=int(hashlib.sha256(target.encode()).hexdigest()[:8],16);center=gp.PRIOR.copy()
 cov=np.cov(Y[:split].T);L=np.linalg.cholesky(.8*np.eye(4)+.2*cov);center[8:12]=np.log(np.diag(L));center[12:18]=L[gp.OFF]
 records=[];best=None
 if method not in BASELINES:mod,fn=adapter(method,obj)
 for rep in range(REPEATS):
  rs=(seed+1009*rep+1729)%(2**32);rng=np.random.default_rng(rs)
  if method in BASELINES:
   active=np.r_[np.arange(9),18] if single else np.arange(22)
   start=center.copy() if rep==0 else np.clip(center+rng.normal(0,.2,22),gp.LOW,gp.HIGH)
   def loss(z):
    t=start.copy();t[active]=z;return obj.training(t,X[:split],Y[:split])
   opt=minimize(loss,start[active],method='L-BFGS-B',bounds=list(zip(gp.LOW[active],gp.HIGH[active])),options={'maxiter':60,'maxfun':1600,'ftol':1e-7})
   th=start.copy();th[active]=opt.x;score=obj.validation(th,X[:split],Y[:split],X[split:],Y[split:])
   rec={'optimizer_success':bool(opt.success),'message':str(opt.message),'iterations':int(opt.nit),'evaluations':int(opt.nfev),'training_objective':float(opt.fun)}
  else:
   th,score=fn(X[:split],Y[:split],rs,GENS,center=center,Xv=X[split:],Yv=Y[split:],refit=False)
   rec={'source':Path(inspect.getfile(mod)).name,'source_sha256':hashlib.sha256(Path(inspect.getfile(mod)).read_bytes()).hexdigest(),'function':fn.__name__}
  rec.update(repeat=rep,seed=rs,validation_loss=float(score));records.append(rec)
  if th is not None and np.isfinite(score) and (best is None or score<best[0]):best=(score,th.copy(),rep)
 if best is None:raise gp.ScientificFailure('NO_VALID_FIT')
 meta={'inner_train_last':keys[split-1],'validation_first':keys[split],'validation_last':keys[-1], 'tuning_last':keys[-1],
       'theta':best[1].tolist(),'kind':kind,'single':single,'prior_strength':strength,'selected_repeat':best[2],
       'repeat_records':finite(records),'training_calls':obj.train_calls,'validation_calls':obj.validation_calls,'invalid_candidates':obj.invalid}
 return best[1],sc,meta

def forecast(samples,target,frozen):
 th,sc,meta=frozen;keys=sorted(k for k in samples if k<target);xm,xs,ym,ys=sc
 X=(np.stack([samples[k][0] for k in keys])-xm)/xs;Y=(np.stack([samples[k][1] for k in keys])-ym)/ys
 f=gp.fit(th,X,Y,meta['kind'],meta['single']);p,v=gp.predict(f,(samples[target][0][None,:]-xm)/xs)
 q=p.shape[1];mu=p[0]*ys[:q]+ym[:q];var=v[0]*ys[:q]**2
 if not np.isfinite(mu).all() or max(abs(mu))>=1 or not np.isfinite(var).all() or var.min()<=0:raise gp.ScientificFailure('PATHOLOGICAL_RETURN_OR_VARIANCE')
 dg={**meta,'train_last':keys[-1],'train_rows':len(keys),'condition_upper_bound':gp.condition(f),
     'theta_sha256':hashlib.sha256(th.tobytes()).hexdigest(),'observation_return_variance':var.tolist(),'noise_variances':f['noise'].tolist()}
 return mu,var,dg

def evaluate(b,method,a,z,frozen=None):
 rows=[];fail=[]
 for t in r.base.month_range(a,z):
  samples=r.base.all_samples_at_origin(b,t,governed=True)
  try:
   theta=frozen if frozen is not None else tune(samples,t,method);mu,var,diag=forecast(samples,t,theta);o=r.base.month_shift(t,-1);rw=float(b.core_gold[o]);actual=float(b.core_gold[t]);sd=np.sqrt(var[0]);real=np.log(actual/rw)
   rows.append({'target':t,'origin':o,'actual':actual,'rw':rw,'forecast':float(rw*np.exp(mu[0])),
    'pred_returns':mu.tolist(),'gold_interval95':[float(rw*np.exp(mu[0]-1.95996398454*sd)),float(rw*np.exp(mu[0]+1.95996398454*sd))],
    'gold_return_nlpd':float(.5*(np.log(2*np.pi*var[0])+(real-mu[0])**2/var[0])),'diag':diag})
  except gp.ScientificFailure as e:fail.append({'target':t,'reason':str(e)})
  print(method,t,'DONE' if not fail or fail[-1]['target']!=t else 'SCIENTIFIC_FAIL',flush=True)
 out={'rows':rows,'failures':fail,'scientific_gate':'PASS' if not fail else 'FAIL','metrics':r.metrics.active_metrics(rows) if not fail else None,'yearly':r.metrics.yearly(rows) if not fail else None}
 if not fail:out['uncertainty']={'coverage95':sum(z['gold_interval95'][0]<=z['actual']<=z['gold_interval95'][1] for z in rows)/len(rows),'mean_interval_width':float(np.mean([z['gold_interval95'][1]-z['gold_interval95'][0] for z in rows])),'mean_gold_return_nlpd':float(np.mean([z['gold_return_nlpd'] for z in rows]))}
 return out

def run(method):
 b=r.base.load_data(os.environ['NEON_DATABASE_URL']);start=time.time()
 d={'method':method,'model_id':'GPR_V1_'+method,'run_id':os.getenv('GITHUB_RUN_ID'),'commit':os.getenv('GITHUB_SHA'),
 'spec':{'outputs':1 if method=='SO_RBF' else 4,'single_output_exception':'benchmark only; not main joint-learning family' if method=='SO_RBF' else None,'bounds':[gp.LOW.tolist(),gp.HIGH.tolist()],'repeats':REPEATS,'population':POP,'generations':GENS,'posterior':'exact ICM via noise whitening; checked against dense covariance','fitness':'joint normalized negative log marginal likelihood plus stated prior penalty','point_prediction':'lognormal median appropriate to price absolute-error objective','jitter':gp.JITTER,'condition_upper_bound_limit':1e12,'external':'theta/kernel/scaler frozen at 2024-12, posterior conditioned on expanding available history'},
 'authority':{'selection':'DEV_ONLY','database':'READ_ONLY','2025':'REPORT_ONLY','2026':'REPORT_ONLY','random_split':False,'source_checks':b.source_checks,'invariants_before':b.invariants_before}}
 path=Path(f'gpr_{method.lower()}_result.json');d['dev']=evaluate(b,method,'2022-04','2024-12');d['dev_decision_frozen_before_external']='BENCHMARK_ONLY' if method=='SO_RBF' else ('ELIGIBLE' if d['dev']['scientific_gate']=='PASS' else 'REJECTED_SCIENTIFIC_FAILURE')
 d['dev_freeze_sha256']=hashlib.sha256(json.dumps(d['dev'],sort_keys=True).encode()).hexdigest();path.write_text(json.dumps(finite(d),indent=2,sort_keys=True,allow_nan=False)+'\n')
 frozen=tune(r.base.all_samples_at_origin(b,'2025-01',governed=True),'2025-01',method)
 d['external_freeze']={'tuning_last':frozen[2]['tuning_last'],'theta_sha256':hashlib.sha256(frozen[0].tobytes()).hexdigest(),'scaler_sha256':hashlib.sha256(np.concatenate(frozen[1]).tobytes()).hexdigest()}
 d['transport_2025']=evaluate(b,method,'2025-01','2025-12',frozen);d['stress_2026']=evaluate(b,method,'2026-01','2026-07',frozen)
 d['authority']['invariants_after']=r.vanilla.read_invariants(os.environ['NEON_DATABASE_URL']);assert d['authority']['invariants_after']==b.invariants_before
 d['status']='COMPLETE';d['seconds']=time.time()-start;path.write_text(json.dumps(finite(d),indent=2,sort_keys=True,allow_nan=False)+'\n');print(json.dumps({'method':method,'dev':d['dev']['metrics'],'seconds':d['seconds']}),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--method',required=True,choices=BASELINES+sum(r.BATCHES,[]));run(ap.parse_args().method)
