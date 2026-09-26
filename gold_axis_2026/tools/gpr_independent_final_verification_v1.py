"""Independent arithmetic, source-identity and frozen-weight artifact audit."""
import argparse,gzip,hashlib,json,math
from pathlib import Path
import numpy as np
from gpr_audit_v1 import audit
from gpr_stage2_v1 import load

def check_metrics(part):
 if part.get('scientific_gate','PASS')!='PASS':return
 rows=part['rows'];m=part['metrics'];ae=[abs(r['forecast']-r['actual']) for r in rows]
 assert abs(sum(ae)-m['sum_abs_error'])<1e-7
 assert abs(sum(ae)/len(rows)-m['mae'])<1e-8
 assert sum(np.sign(r['forecast']-r['rw'])==np.sign(r['actual']-r['rw']) for r in rows)==m['direction_correct']
 assert abs(math.sqrt(sum((r['forecast']-r['actual'])**2 for r in rows)/len(rows))-m['rmse'])<1e-8

def run(root,job,artifact):
 models=load(root);ref=json.loads(gzip.decompress((root/'evidence/rbfnn_stage1/strict_results.json.gz').read_bytes()))['DE_ABC'];numerical={};checks=0
 for name,d in models.items():
  audit(d);conditions=[];minvars=[];failures=[]
  for p in ['dev','transport_2025','stress_2026']:
   check_metrics(d[p]);truth={r['target']:(r['actual'],r['rw']) for r in ref[p]['rows']}
   failures.extend(d[p]['failures'])
   for r in d[p]['rows']:
    assert (r['actual'],r['rw'])==truth[r['target']]
    assert abs(r['forecast']-r['rw']*math.exp(r['pred_returns'][0]))<1e-8
    theta=np.array(r['diag']['theta']);assert np.all(theta>=np.array(d['spec']['bounds'][0])-1e-8) and np.all(theta<=np.array(d['spec']['bounds'][1])+1e-8)
    assert hashlib.sha256(theta.tobytes()).hexdigest()==r['diag']['theta_sha256']
    conditions.append(r['diag']['condition_upper_bound']);minvars+=r['diag']['observation_return_variance']
   checks+=1
  numerical[name]={'max_condition_upper_bound':max(conditions) if conditions else None,'min_observation_return_variance':min(minvars) if minvars else None,'scientific_failures':failures,'outputs':d['spec']['outputs']}
 pools=json.loads((root/'GOLD_MONTHLY_GPR_STAGE4_POOL_FREEZE_2026-09-26.json').read_text());ens=json.loads((root/'GOLD_MONTHLY_GPR_STAGE4_RESULT_2026-09-26.json').read_text());assert ens['pool_freeze_sha256']==hashlib.sha256((root/'GOLD_MONTHLY_GPR_STAGE4_POOL_FREEZE_2026-09-26.json').read_bytes()).hexdigest()
 count=0
 for pool,rec in ens['pools'].items():
  names=rec['components'];assert names==pools[pool]
  W=np.array(rec['prequential_optimized_weights']);V=np.array(rec['prequential_inverse_weights'])
  assert W.min()>=0 and np.allclose(W.sum(axis=1),1) and np.allclose(W[:6],1/len(names))
  for n in names:assert hashlib.sha256(json.dumps(models[n]['dev'],sort_keys=True).encode()).hexdigest()==pools['source_dev_hashes'][n]
  P=np.array([[r['forecast'] for r in models[n]['dev']['rows']] for n in names]).T;y=np.array([r['actual'] for r in models[names[0]]['dev']['rows']])
  for i in range(6,len(y)):
   inv=1/np.maximum(np.mean(abs(P[:i]-y[:i,None]),axis=0),1e-12);inv/=inv.sum();assert np.allclose(inv,V[i])
   assert np.sum(abs(P[:i]@W[i]-y[:i]))<=np.sum(abs(P[:i].mean(axis=1)-y[:i]))+1e-7
  for variant,d in rec['variants'].items():
   for p in ['dev','transport_2025','stress_2026']:
    check_metrics(d[p])
    if d[p].get('scientific_gate','PASS')!='PASS':continue
    X=np.array([[r['forecast'] for r in models[n][p]['rows']] for n in names]).T
    if variant=='MEDIAN':pred=np.median(X,axis=1)
    elif p!='dev':pred=X@np.array(d['frozen_external_weights'])
    elif variant=='SIMPLE_AVERAGE':pred=X.mean(axis=1)
    elif variant=='INVERSE_PRIOR_MAE':pred=np.sum(X*V,axis=1)
    else:
     a=float(variant.split('_')[1]);pred=np.sum(X*((1-a)/len(names)+a*W),axis=1)
    assert np.allclose(pred,[r['forecast'] for r in d[p]['rows']],rtol=0,atol=1e-8);count+=1
 out={'status':'PASS','model_specifications':len(models),'model_period_checks':checks,'ensemble_period_checks':count,'numerical_diagnostics':numerical,'run_id':ens['run_id'],'execution_commit':ens['commit'],'job_id':job,'artifact_id':artifact}
 (root/'GOLD_MONTHLY_GPR_FINAL_VERIFICATION_2026-09-26.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='numerical_diagnostics'}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--job',type=int,required=True);p.add_argument('--artifact',type=int,required=True);a=p.parse_args();run(Path('gold_axis_2026'),a.job,a.artifact)
