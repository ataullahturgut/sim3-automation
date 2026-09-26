"""Match unchanged score-domain replays to original Stage1 evidence."""
import gzip,json
from pathlib import Path

def run(root):
 replay=json.loads(gzip.decompress((root/'evidence/gpr_score_domain/results.json.gz').read_bytes()));original=json.loads(gzip.decompress((root/'evidence/gpr_stage1/results.json.gz').read_bytes()))
 ids={'ABC':(108466913684,10912689533),'ALO':(108466913788,10913337530),'DE_ABC':(108466913693,10913840808)};records={}
 for n,d in replay.items():
  s=d['score_domain_audit'];assert s['status']=='PASS' and s['minimum']>0
  matched=n in original and d['dev_freeze_sha256']==original[n]['dev_freeze_sha256']
  if n in original:assert matched,'REPLAY_MISMATCH '+n
  records[n]={'score_domain':s,'original_available':n in original,'exact_dev_hash_match':matched,'dev_freeze_sha256':d['dev_freeze_sha256'],
   'run_id':d['run_id'],'commit':d['commit'],'job_id':ids[n][0],'artifact_id':ids[n][1]}
 status='PASS' if len(records)==3 and all(d['exact_dev_hash_match'] for d in records.values()) else 'WAITING_FOR_ORIGINALS'
 out={'status':status,'models':records,'technical_only':True,'no_score_or_algorithm_change':True,'no_new_candidate':True,'scope':'All training evaluations in these frozen DEV and pre-2025 tuning runs; not a universal guarantee for other datasets'}
 (root/'GOLD_MONTHLY_GPR_SCORE_DOMAIN_AUDIT_2026-09-26.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'score_domain_status':status,'matched':[n for n,d in records.items() if d['exact_dev_hash_match']]}))
if __name__=='__main__':run(Path('gold_axis_2026'))
