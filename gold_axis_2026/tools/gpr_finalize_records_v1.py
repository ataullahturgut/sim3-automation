"""Write terminal ledger/checkpoint state only after independent final PASS."""
import hashlib,json,re
from pathlib import Path
from gpr_stage2_v1 import load

def run(root):
 final=json.loads((root/'GOLD_MONTHLY_GPR_FINAL_FREEZE_2026-09-26.json').read_text());verification=json.loads((root/'GOLD_MONTHLY_GPR_FINAL_VERIFICATION_2026-09-26.json').read_text())
 assert final['status']=='COMPLETE' and verification['status']=='PASS'
 assert json.loads((root/'GOLD_MONTHLY_GPR_STAGE3_CLOSURE_2026-09-26.json').read_text())['status']=='COMPLETE'
 models=load(root);assert len(models)==44 and verification['model_specifications']==44
 ensemble=json.loads((root/'GOLD_MONTHLY_GPR_STAGE4_RESULT_2026-09-26.json').read_text())
 candidates={**models,**{p+'_'+n:d for p,z in ensemble['pools'].items() for n,d in z['variants'].items()}}
 primary=final['primary'];m=candidates[primary]['dev']['metrics'];direction=final['direction_specialist'];dm=candidates[direction]['dev']['metrics']
 closure={'status':'COMPLETE_FROZEN','family':'GPR','stages_completed':['0','1','2','3A','3B','3C','4','5'],'specifications':44,'ensemble_variants':sum(len(v['variants']) for v in ensemble['pools'].values()),'primary':primary,'direction_specialist':direction,'selection':'DEV_ONLY','external_acceptance_authority':False,
 'final_run_id':verification['run_id'],'final_job_id':verification['job_id'],'final_artifact_id':verification['artifact_id'],'execution_commit':verification['execution_commit'],
 'verification_sha256':hashlib.sha256((root/'GOLD_MONTHLY_GPR_FINAL_VERIFICATION_2026-09-26.json').read_bytes()).hexdigest(),'next_family':'N3 Multi-task RFF-BLR','next_family_executed':False}
 (root/'GOLD_MONTHLY_GPR_ALL_STAGES_CLOSURE_2026-09-26.json').write_text(json.dumps(closure,indent=2,sort_keys=True)+'\n')
 p=root/'GOLD_MONTHLY_GPR_EXECUTION_CHECKPOINT_2026-09-26.json';c=json.loads(p.read_text());c['status']='COMPLETE_FROZEN';c['stage3']['status']='COMPLETE_AUDITED';c['stage3']['audited_methods']=[n for n,d in models.items() if d.get('stage') in ['3A','3B','3C']];c['stage3']['literature']='LMC2_RBF_M32 COMPLETE_AUDITED';c['stage4_5']={k:v for k,v in closure.items() if k.startswith('final_') or k in ['status','execution_commit','primary','direction_specialist']};c['next_action']='GPR complete and frozen. Consult final Turkish method/results dossier and final evidence. Next roadmap family N3 Multi-task RFF-BLR has not been executed.';c['prepared_local_only']=[];p.write_text(json.dumps(c,indent=2)+'\n')
 p=root/'GOLD_MONTHLY_ELM_METAHEURISTIC_LEDGER_ANN_PLAN_2026-09-25.md';s=p.read_text()
 top=f"> **Current checkpoint — 2026-09-26: N2 GPR Stage0–5 COMPLETE/FROZEN.** Joint primary {primary}: DEV ΣAE{m['sum_abs_error']:.4f}, direction{m['direction_correct']}/33. Direction specialist {direction}: {dm['sum_abs_error']:.4f}/{dm['direction_correct']}. All44 model specifications and18 ensemble variants archived; independent final verification PASS. RBFNN remains closed. [GPR method/results](GOLD_MONTHLY_GPR_YONTEM_VE_SONUCLAR_2026-09-26.md). Next N3 Multi-task RFF-BLR, not executed. Historical entries below remain chronological; this closure supersedes pending statuses."
 s=re.sub(r'^> \*\*Current checkpoint.*$',top,s,count=1,flags=re.M)
 title='### GPR Stage4–5 final closure — COMPLETE / INDEPENDENTLY VERIFIED'
 assert title not in s
 lines=['','',title,'',f"Final run{verification['run_id']}; job{verification['job_id']}; artifact{verification['artifact_id']}; execution commit`{verification['execution_commit']}`. Pool file committed before ensemble evaluation; exact hashes in Stage4 result and verification. All44 model specs, {verification['model_period_checks']} model-period and {verification['ensemble_period_checks']} ensemble-period arithmetic/source checks PASS.",'',f"Joint primary {primary}: DEV ΣAE{m['sum_abs_error']:.6f}, direction{m['direction_correct']}/33. Direction specialist {direction}: ΣAE{dm['sum_abs_error']:.6f}, direction{dm['direction_correct']}/33. Best single {final['single_leader']}; best hybrid {final['hybrid_leader']}; best Stage3 {final['stage3_leader']}; ensemble {final['ensemble_leader']}: {final['ensemble_decision']}. Balanced challenger {final['balanced_challenger']}. External results never selected models/pools/alpha.",'','Cross-family recomputed DEV:','','| Model | ΣAE | Direction |','|---|---:|---:|']
 for n,d in sorted(final['cross_family_metrics'].items(),key=lambda kv:kv[1]['dev']['sum_abs_error']):
  q=d['dev'];lines.append(f"| {n} | {q['sum_abs_error']:.6f} | {q['direction_correct']}/33 |")
 lines+=['','Point-estimate Pareto: '+', '.join(final['cross_family_frontier'])+'. Identical aliases recorded separately. No claim of statistical superiority. Conditional prequential pool selection, fixed-prediction leave-one-month sensitivity, interval limitations and independent-repeat NOT_PROVEN status remain explicit.','','Kontrol ve Uyum Özeti: DEV-only PASS; external hyperparameter and weight freeze PASS; chronological training/weight checks PASS; pool/alpha estimates conditional on DEV selection; DB READ_ONLY/invariants equal; scientific gates and failed-period exclusion enforced; same target/actual/RW reference values verified; full provenance archived.','','Turkish dossier `GOLD_MONTHLY_GPR_YONTEM_VE_SONUCLAR_2026-09-26.md` includes sources, equations, implementation bounds, all model/ensemble outcomes, compute counts and selected GPR plus RBFNN2026 actual/predicted tables. Final closure `GOLD_MONTHLY_GPR_ALL_STAGES_CLOSURE_2026-09-26.json`. Next N3 Multi-task RFF-BLR; not automatically started.','']
 p.write_text(s+'\n'.join(lines));print(json.dumps(closure))
if __name__=='__main__':run(Path('gold_axis_2026'))
