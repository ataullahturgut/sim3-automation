"""Close ordered stages only after required audited production artifacts exist."""
import argparse,gzip,hashlib,json
from pathlib import Path
from gpr_audit_v1 import audit
A=['ADAPTIVE_PSO','ADAPTIVE_TLBO','TLBO_TUNED_PSO','DE_TUNED_PSO','ADAPTIVE_CROW','PSO_TLBO']

def run(root,stage):
 models=json.loads(gzip.decompress((root/'evidence/gpr_stage3/results.json.gz').read_bytes()))
 freeze=root/'GOLD_MONTHLY_GPR_STAGE2_FREEZE_2026-09-26.json';parent=json.loads(freeze.read_text());opening=parent['hybrid_opening'];hybrid=['_'.join(x['pair']) for x in opening]
 names=A if stage=='3A' else A+hybrid if stage=='3AB' else A+hybrid+['LMC2_RBF_M32']
 for n in names:assert n in models,n+' MISSING';audit(models[n])
 for n in A:assert models[n]['parent_freeze_sha256']==hashlib.sha256(freeze.read_bytes()).hexdigest()
 if stage!='3A':assert json.loads((root/'GOLD_MONTHLY_GPR_STAGE3A_CLOSURE_2026-09-26.json').read_text())['status']=='COMPLETE'
 if stage=='3':assert json.loads((root/'GOLD_MONTHLY_GPR_STAGE3AB_CLOSURE_2026-09-26.json').read_text())['status']=='COMPLETE'
 out={'status':'COMPLETE','stage':stage,'models':names,'selection':'DEV_ONLY','external_metrics_used':False,'hybrid_status':'EXECUTED' if hybrid and stage!='3A' else 'ELIGIBLE_PENDING' if hybrid else 'CLOSED_NOT_OPENED',
 'models_audited':{n:{'run_id':models[n]['run_id'],'commit':models[n]['commit'],'dev_hash':models[n]['dev_freeze_sha256'],'dev_gate':models[n]['dev']['scientific_gate']} for n in names},'parent_freeze_sha256':hashlib.sha256(freeze.read_bytes()).hexdigest()}
 (root/f'GOLD_MONTHLY_GPR_STAGE{stage}_CLOSURE_2026-09-26.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['3A','3AB','3']);a=p.parse_args();run(Path('gold_axis_2026'),a.stage)
