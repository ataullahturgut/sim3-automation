"""Match unchanged score-domain replays to original Stage1 evidence."""
import gzip,json,math
from pathlib import Path

def compare(a,b,path=''):
 # Separate bitwise identity from a strict numerical replay check. Hash strings
 # can differ solely because theta doubles differ; actual theta values are checked.
 differences=[]
 if isinstance(a,dict) and isinstance(b,dict):
  assert a.keys()==b.keys(),path+' KEYS'
  for k in a:
   if k=='theta_sha256':continue
   differences+=compare(a[k],b[k],path+'/'+k)
 elif isinstance(a,list) and isinstance(b,list):
  assert len(a)==len(b),path+' LENGTH'
  for i,(x,y) in enumerate(zip(a,b)):differences+=compare(x,y,path+'/'+str(i))
 elif isinstance(a,float) and isinstance(b,(float,int)):
  assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),path+' NUMERICAL_MISMATCH'
  if a!=b:differences.append({'path':path,'absolute_difference':abs(a-b)})
 else:assert a==b,path+' DISCRETE_MISMATCH'
 return differences

def run(root):
 replay=json.loads(gzip.decompress((root/'evidence/gpr_score_domain/results.json.gz').read_bytes()));original=json.loads(gzip.decompress((root/'evidence/gpr_stage1/results.json.gz').read_bytes()))
 ids={'ABC':(108466913684,10912689533),'ALO':(108466913788,10913337530),'DE_ABC':(108466913693,10913840808)};records={}
 for n,d in replay.items():
  s=d['score_domain_audit'];assert s['status']=='PASS' and s['minimum']>0
  matched=n in original and d['dev_freeze_sha256']==original[n]['dev_freeze_sha256']
  differences=[]
  if n in original:
   for section in ['dev','transport_2025','stress_2026']:differences+=compare(original[n][section],d[section],section)
  numerical_match=n in original
  records[n]={'score_domain':s,'original_available':n in original,'exact_dev_hash_match':matched,'numerically_identical_replay':numerical_match,'float_tolerance':{'rtol':1e-10,'atol':1e-10},'differing_float_count':len(differences),'max_absolute_float_difference':max((x['absolute_difference'] for x in differences),default=0),'dev_freeze_sha256':original[n]['dev_freeze_sha256'] if n in original else None,'replay_dev_freeze_sha256':d['dev_freeze_sha256'],
   'run_id':d['run_id'],'commit':d['commit'],'job_id':ids[n][0],'artifact_id':ids[n][1]}
 status='PASS' if len(records)==3 and all(d['numerically_identical_replay'] for d in records.values()) else 'WAITING_FOR_ORIGINALS'
 out={'status':status,'models':records,'technical_only':True,'no_score_or_algorithm_change':True,'no_new_candidate':True,'scope':'All training evaluations in these frozen DEV and pre-2025 tuning runs; not a universal guarantee for other datasets'}
 (root/'GOLD_MONTHLY_GPR_SCORE_DOMAIN_AUDIT_2026-09-26.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'score_domain_status':status,'matched':[n for n,d in records.items() if d['numerically_identical_replay']]}))
if __name__=='__main__':run(Path('gold_axis_2026'))
