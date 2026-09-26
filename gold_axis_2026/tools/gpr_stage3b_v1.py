"""Evidence-gated MPA proposal hybrids, exact repository parity mechanism."""
import argparse,hashlib,json
from pathlib import Path
import gpr_experiment_v1 as e
import vw_midas_elmfis_stage3b_v1 as h
ORIGINAL_ADAPTER=e.adapter;ORIGINAL_TUNE=e.tune;META={}

def adapter(method,obj):
 global META
 ORIGINAL_ADAPTER('MPA',obj);h.LO=e.gp.LOW;h.HI=e.gp.HIGH;h.D=22;h.POP=24
 META={'source':Path(h.__file__).name,'sha256':hashlib.sha256(Path(h.__file__).read_bytes()).hexdigest(),'second':method.split('_')[1],'population':24,'generations':45,'repeats':[]}
 current=META
 def phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
  th,score,shares,trace=h.hybrid_phase(X,Y,seed,generations,current['second'],center,Xv,Yv,False)
  current['repeats'].append({'seed':seed,'survivor_shares':shares,'trace':trace})
  return th,score
 return h,phase

def tune(samples,target,method):
 th,sc,meta=ORIGINAL_TUNE(samples,target,method);meta['hybrid']=e.finite(META);return th,sc,meta

def run(method):
 root=Path('gold_axis_2026');f=json.loads((root/'GOLD_MONTHLY_GPR_STAGE2_FREEZE_2026-09-26.json').read_text())
 assert json.loads((root/'GOLD_MONTHLY_GPR_STAGE3A_CLOSURE_2026-09-26.json').read_text())['status']=='COMPLETE'
 assert f['status']=='FROZEN_BEFORE_STAGE3' and f['external_metrics_used'] is False
 assert len(f['hybrid_opening'])==1 and '_'.join(f['hybrid_opening'][0]['pair'])==method
 e.adapter=adapter;e.tune=tune;e.run(method)
 p=Path(f'gpr_{method.lower()}_result.json');d=json.loads(p.read_text());d['stage']='3B';d['opening_evidence']=f['hybrid_opening'][0];p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--method',required=True,choices=['MPA_SCA','MPA_GA','MPA_CPA']);run(p.parse_args().method)
