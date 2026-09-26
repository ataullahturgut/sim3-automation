"""Artifact-level checks independent of selection and ensemble implementation."""
import hashlib,json,copy
from pathlib import Path
import numpy as np
import rbfnn_stage4_v1 as s4
from rbfnn_stage1_audit_report import audit

def run(root):
 models=s4.load(root);pool=json.loads((root/'GOLD_MONTHLY_RBFNN_STAGE4_POOL_FREEZE_2026-09-26.json').read_text());ens=json.loads((root/'GOLD_MONTHLY_RBFNN_STAGE4_RESULT_2026-09-26.json').read_text())
 assert ens['pool_freeze_sha256']==hashlib.sha256((root/'GOLD_MONTHLY_RBFNN_STAGE4_POOL_FREEZE_2026-09-26.json').read_bytes()).hexdigest()
 numerical={}
 for n,d in models.items():
  if n not in ['VANILLA','REGULARIZED']:audit(copy.deepcopy(d))
  diags=[r.get('diag',r.get('rbfnn_diag',{})) for r in d['dev']['rows']]
  cond=[x.get('design_condition',x.get('design_condition_number')) for x in diags];cond=[v for v in cond if v is not None]
  widths=[v for x in diags for v in [x.get('width_min'),x.get('width_max')] if v is not None]
  counts=[x.get('initial_cluster_counts',x.get('cluster_counts')) for x in diags]
  numerical[n]={'dev_condition_max':max(cond) if cond else 'NOT_PROVEN','dev_width_min':min(widths) if widths else 'NOT_PROVEN','dev_width_max':max(widths) if widths else 'NOT_PROVEN','initial_occupancy':'PASS' if all(x is not None and min(x)>0 for x in counts) else 'NOT_PROVEN','dev_scientific_gate':d['dev'].get('scientific_gate','HISTORICAL_GATE_SEE_STAGE0')}
  if n not in ['VANILLA','REGULARIZED']:assert max(cond)<=1e10
 checks=0
 for name,rec in ens['pools'].items():
  names=pool[name];assert names==rec['components']
  for n in names:assert hashlib.sha256(json.dumps(models[n]['dev'],sort_keys=True).encode()).hexdigest()==pool['source_dev_hashes'][n]
  W=np.array(rec['prequential_optimized_weights']);V=np.array(rec['prequential_inverse_weights']);assert np.allclose(W.sum(axis=1),1) and W.min()>=0 and np.allclose(W[:6],1/len(names));assert np.allclose(V.sum(axis=1),1)
  P=np.array([[r['forecast'] for r in models[n]['dev']['rows']] for n in names]).T;y=np.array([r['actual'] for r in models[names[0]]['dev']['rows']])
  for i in range(6,33):
   prior=np.mean(abs(P[:i]-y[:i,None]),axis=0);expected=1/np.maximum(prior,1e-12);expected/=expected.sum();assert np.allclose(V[i],expected)
   assert np.sum(abs(P[:i]@W[i]-y[:i]))<=np.sum(abs(P[:i].mean(axis=1)-y[:i]))+1e-7
  for variant,d in rec['variants'].items():
   for p,expected in [('dev',33),('transport_2025',12),('stress_2026',7)]:
    rr=d[p]['rows'];assert len(rr)==expected;ae=[abs(r['forecast']-r['actual']) for r in rr];direction=sum(np.sign(r['forecast']-r['rw'])==np.sign(r['actual']-r['rw']) for r in rr)
    assert abs(sum(ae)-d[p]['metrics']['sum_abs_error'])<1e-7 and direction==d[p]['metrics']['direction_correct'];assert np.isfinite([r['forecast'] for r in rr]).all()
    X=np.array([[r['forecast'] for r in models[n][p]['rows']] for n in names]).T
    if variant=='MEDIAN':pred=np.median(X,axis=1)
    elif p!='dev':pred=X@np.array(d['frozen_external_weights'])
    elif variant=='INVERSE_PRIOR_MAE':pred=np.sum(X*V,axis=1)
    elif variant=='SIMPLE_AVERAGE':pred=X.mean(axis=1)
    else:
     a=float(variant.split('_')[1]);pred=np.sum(X*((1-a)/len(names)+a*W),axis=1)
    assert np.allclose(pred,[r['forecast'] for r in rr],rtol=0,atol=1e-8);checks+=1
 out={'status':'PASS','models_audited':len(models),'new_model_artifacts_fully_audited':len(models)-2,'ensemble_period_metric_prediction_checks':checks,'numerical_diagnostics':numerical,'run_id':ens['run_id'],'job_id':108453610546,'artifact_id':10911484644,'execution_commit':ens['commit'],'notes':['DE_ABC and BEST_HYBRID_DE_ABC are the same model under two reporting roles; distinct global frontier has two models','Regularized baseline full occupancy evidence NOT_PROVEN; no unnecessary baseline rerun','41 specifications include two historical baseline audits, not two new baseline runs']}
 (root/'GOLD_MONTHLY_RBFNN_FINAL_VERIFICATION_2026-09-26.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='numerical_diagnostics'}));print('selected condition maxima',{n:numerical[n]['dev_condition_max'] for n in pool['FULL']})

if __name__=='__main__':run(Path('gold_axis_2026'))
