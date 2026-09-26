"""Replay only score-sensitive optimizers; no score transform or new candidate.

ABC/ALO/DE-ABC use 1/(1+loss). NLL is not universally nonnegative.
Track EVERY training score and require positivity on this actual experiment;
compare exact DEV prediction/hash to the primary artifacts before Stage2.
"""
import argparse,json,math
from pathlib import Path
import gpr_experiment_v1 as e
ORIGINAL=e.Objective
STATS={'minimum':math.inf,'maximum':-math.inf,'finite_calls':0,'nonfinite_calls':0}
class Tracked(ORIGINAL):
 def training(self,theta,X,Y):
  v=super().training(theta,X,Y)
  if math.isfinite(v):
   STATS['minimum']=min(STATS['minimum'],v);STATS['maximum']=max(STATS['maximum'],v);STATS['finite_calls']+=1
  else:STATS['nonfinite_calls']+=1
  return v

def run(method):
 e.Objective=Tracked;e.run(method)
 p=Path(f'gpr_{method.lower()}_result.json');d=json.loads(p.read_text());d['score_domain_audit']={**STATS,'status':'PASS' if STATS['minimum']>0 else 'BLOCKED_REQUIRES_SCORE_DOMAIN_FIX','purpose':'Technical replay, not an additional selection candidate; no score transform'}
 p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps(d['score_domain_audit']),flush=True)
 if STATS['minimum']<=0:raise RuntimeError('SCORE_DOMAIN_REQUIRES_REVIEW_BEFORE_STAGE2')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--method',required=True,choices=['ABC','ALO','DE_ABC']);run(p.parse_args().method)
