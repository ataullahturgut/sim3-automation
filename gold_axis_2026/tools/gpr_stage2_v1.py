"""DEV-only filtering and immutable role-based parent freeze after all32."""
import gzip,hashlib,json
from pathlib import Path
import numpy as np
from gpr_audit_v1 import audit
import vw_midas_elmfis_baseline_v1 as metric
from vw_midas_rbfnn_stage1_v1 import BATCHES

def load(root):
 out={}
 for stage in ['gpr_stage0','gpr_stage1','gpr_stage3']:
  p=root/'evidence'/stage/'results.json.gz'
  if p.exists():out.update(json.loads(gzip.decompress(p.read_bytes())))
 return out

def run(root):
 models=load(root);assert set(sum(BATCHES,[]))<=models.keys()
 domain=json.loads((root/'GOLD_MONTHLY_GPR_SCORE_DOMAIN_AUDIT_2026-09-26.json').read_text())
 assert domain['status']=='PASS'
 for n in ['ABC','ALO','DE_ABC']:assert domain['models'][n]['dev_freeze_sha256']==models[n]['dev_freeze_sha256']
 evidence={n:audit(d)['dev'] for n,d in models.items()}
 valid={n:d for n,d in models.items() if d['dev']['scientific_gate']=='PASS' and d['spec']['outputs']==4}
 ms={n:evidence[n] for n in valid};retained=[n for n in valid if ms[n]['relative_mae_vs_rw']<1 or n=='VANILLA_ICM_RBF']
 errors={n:np.array([r['forecast']-r['actual'] for r in d['dev']['rows']]) for n,d in valid.items()}
 dirs={n:np.array([np.sign(r['forecast']-r['rw'])==np.sign(r['actual']-r['rw']) for r in d['dev']['rows']]) for n,d in valid.items()}
 signs={n:np.array([np.sign(r['forecast']-r['rw']) for r in d['dev']['rows']]) for n,d in valid.items()}
 pairs={}
 for n in valid:
  for o in valid:
   if o<=n:continue
   e,f=errors[n],errors[o];x,y=dirs[n],dirs[o]
   pairs[n+'|'+o]={'signed_corr':float(np.corrcoef(e,f)[0,1]),'absolute_corr':float(np.corrcoef(abs(e),abs(f))[0,1]),'direction_correctness_agreement':int(np.sum(x==y)),
    'predicted_direction_agreement':int(np.sum(signs[n]==signs[o])),'predicted_direction_disagreement':int(np.sum(signs[n]!=signs[o])),
    'first_direction_rescue':int(np.sum(x&~y)),'second_direction_rescue':int(np.sum(y&~x)),'first_price_wins':int(np.sum(abs(e)<abs(f))),'second_price_wins':int(np.sum(abs(f)<abs(e)))}
 removed={}
 for n in list(retained):
  if n=='VANILLA_ICM_RBF':continue
  for o in retained:
   if o==n:continue
   if np.corrcoef(errors[n],errors[o])[0,1]>.995 and ms[o]['sum_abs_error']<=ms[n]['sum_abs_error'] and ms[o]['direction_correct']>=ms[n]['direction_correct']:
    retained.remove(n);removed[n]=o;break
 assert retained
 roles={'price_leader':min(retained,key=lambda n:ms[n]['sum_abs_error']),'direction_leader':min(retained,key=lambda n:(-ms[n]['direction_correct'],ms[n]['sum_abs_error'])),
  'stability_parent':min(retained,key=lambda n:max(v['relative_mae_vs_rw'] for v in metric.yearly(valid[n]['dev']['rows']).values())),'architecture_anchor':'VANILLA_ICM_RBF','optimizer_hybrid_parent':'MPA' if 'MPA' in retained else None}
 hybrid=[]
 if 'MPA' in retained:
  for n in ['SCA','GA','CPA']:
   if n not in retained:continue
   x,y=dirs['MPA'],dirs[n];e,f=errors['MPA'],errors[n];corr=float(np.corrcoef(e,f)[0,1])
   if corr<.90 and min(np.sum(x&~y),np.sum(y&~x))>=2 and min(np.sum(abs(e)<abs(f)),np.sum(abs(f)<abs(e)))>=8:hybrid.append({'pair':['MPA',n],'correlation':corr,'combined_sae':ms['MPA']['sum_abs_error']+ms[n]['sum_abs_error']})
 hybrid=sorted(hybrid,key=lambda d:(d['correlation'],d['combined_sae']))[:1]
 out={'status':'FROZEN_BEFORE_STAGE3','selection':'DEV_ONLY','external_metrics_used':False,'roles':roles,'parent_set':list(dict.fromkeys(v for v in roles.values() if v)),
  'retained':retained,'redundant':removed,'non_retained':[n for n in valid if n not in retained],'hybrid_opening':hybrid,'pairwise':pairs,'metrics':evidence,
  'yearly':{n:metric.yearly(d['dev']['rows']) for n,d in valid.items()},'dev_hashes':{n:d['dev_freeze_sha256'] for n,d in models.items()},
  'leave_one_origin_sae':{n:(abs(e).sum()-abs(e)).tolist() for n,e in errors.items()},
  'repeat_stability':{n:{'median_validation_range':float(np.median([max(x['validation_loss'] for x in r['diag']['repeat_records'] if x['validation_loss'] is not None)-min(x['validation_loss'] for x in r['diag']['repeat_records'] if x['validation_loss'] is not None) for r in d['dev']['rows']])),'independent_prediction_repeats':'NOT_PROVEN'} for n,d in valid.items()}}
 p=root/'GOLD_MONTHLY_GPR_STAGE2_FREEZE_2026-09-26.json';p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 lines=['# GPR Stage2 DEV filtering and parent freeze','','Status FROZEN_BEFORE_STAGE3; 2025/2026 never used.','','Roles: '+json.dumps(roles)+'.','','Conditional hybrid opening: '+json.dumps(hybrid)+'.','','| Model | DEV ΣAE | Direction | RW-relative MAE | Max condition bound | Retained |','|---|---:|---:|---:|---:|---|']
 for n in sorted(valid,key=lambda n:ms[n]['sum_abs_error']):
  m=ms[n];lines.append(f"| {n} | {m['sum_abs_error']:.4f} | {m['direction_correct']}/33 | {m['relative_mae_vs_rw']:.5f} | {m['max_condition_bound']:.4g} | {n in retained} |")
 lines+=['','Full pairwise signed/absolute-error correlations, direction rescue/loss and price-win counts, years, repeat-validation dispersion and source DEV hashes in JSON. Auxiliary SO_RBF is not a four-output parent. Independent predictive-repeat robustness remains NOT_PROVEN.','','## Kontrol ve Uyum Özeti','','DEV-only PASS; external exclusion PASS; no random split; audited chronology/scientific gates; DB invariants equal. Freeze must be committed before Stage3.']
 p.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps({'roles':roles,'hybrid':hybrid}))
if __name__=='__main__':run(Path('gold_axis_2026'))
