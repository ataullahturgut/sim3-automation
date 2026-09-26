"""GP mandatory parity refinements; no Stage3 execution before parent freeze."""
import argparse,hashlib,importlib,json,math,sys
from pathlib import Path
import numpy as np
import gpr_experiment_v1 as e
METHODS=['ADAPTIVE_PSO','ADAPTIVE_TLBO','TLBO_TUNED_PSO','DE_TUNED_PSO','ADAPTIVE_CROW','PSO_TLBO']
CURRENT_META={}
ORIGINAL_ADAPTER=e.adapter
ORIGINAL_TUNE=e.tune

def optimizer(method,obj):
    global CURRENT_META
    ORIGINAL_ADAPTER('PSO',obj)
    number=31 if method in METHODS[:2] else 32 if method in METHODS[2:4] else 33
    mod=importlib.import_module(f'vw_midas_elmfis_stage3_batch{number}_v1')
    mod.LO=e.gp.LOW;mod.HI=e.gp.HIGH;mod.SPAN=e.gp.HIGH-e.gp.LOW
    CURRENT_META={'implementation':Path(mod.__file__).name,
      'source_sha256':hashlib.sha256(Path(mod.__file__).read_bytes()).hexdigest(),
      'parameter_tuning':'chronological pre-target inner validation only',
      'final_population':24,'final_generations':45,'nonlinear_refit':False}
    meta=CURRENT_META
    def phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
        if 'q' not in meta and method!='ADAPTIVE_PSO':
            if method=='ADAPTIVE_TLBO':
                q,score,trace=mod.tune_outer(X,Y,Xv,Yv,seed,center)
                bounds=[mod.QLO.tolist(),mod.QHI.tolist()]
            elif method in ['TLBO_TUNED_PSO','DE_TUNED_PSO']:
                tuner=mod.tlbo_tune if method.startswith('TLBO') else mod.de_tune
                q,score,trace=tuner(X,Y,Xv,Yv,seed,center)
                bounds=[mod.QLO.tolist(),mod.QHI.tolist()]
                meta['outer_population']=mod.TLBO_POP if method.startswith('TLBO') else mod.DE_POP
                meta['outer_generations']=mod.TLBO_ITERS if method.startswith('TLBO') else mod.DE_ITERS
                meta['nested_pso_population']=mod.OUTER_PSO_POP;meta['nested_pso_generations']=mod.OUTER_PSO_ITERS
            elif method=='ADAPTIVE_CROW':
                q,score,trace=mod.tune_crow(X,Y,Xv,Yv,seed,center)
                bounds=[mod.CROW_LO.tolist(),mod.CROW_HI.tolist()]
            else:
                q,score,trace=mod.tune_hybrid(X,Y,Xv,Yv,seed,center)
                bounds=[mod.HYB_LO.tolist(),mod.HYB_HI.tolist()]
            if not math.isfinite(score):raise e.gp.ScientificFailure('NO_VALID_OUTER_TUNING')
            meta.update(q=q.tolist(),outer_score=float(score),outer_trace=trace,parameter_bounds=bounds)
        if method=='ADAPTIVE_PSO':
            th,_=mod.adaptive_pso_run(X,Y,seed,generations,center,False)
            meta['schedule']={'w':[.9,.4],'c1':[2.5,.5],'c2':[.5,2.5],'vmax_fraction':.18}
        elif method=='ADAPTIVE_TLBO':th,_=mod.itlbo_run(X,Y,np.array(meta['q']),seed,generations,center,False)
        elif method in ['TLBO_TUNED_PSO','DE_TUNED_PSO']:
            th,_=mod.pso_train(X,Y,np.array(meta['q']),seed,24,generations,center,False)
        elif method=='ADAPTIVE_CROW':th,_=mod.run_crow(X,Y,np.array(meta['q']),seed,generations,center,False)
        else:th,_=mod.run_hybrid(X,Y,np.array(meta['q']),seed,generations,center,False)
        # Every final candidate is the training winner; validation chooses repeat.
        return th,obj.validation(th,X,Y,Xv,Yv)
    return sys.modules[__name__],phase

def tune(samples,target,method):
    th,sc,meta=ORIGINAL_TUNE(samples,target,method)
    meta['refinement']=e.finite(CURRENT_META)
    return th,sc,meta

def run(method):
    freeze=Path('gold_axis_2026/GOLD_MONTHLY_GPR_STAGE2_FREEZE_2026-09-26.json')
    d=json.loads(freeze.read_text());assert d['status']=='FROZEN_BEFORE_STAGE3' and d['external_metrics_used'] is False
    e.adapter=optimizer;e.tune=tune;e.run(method)
    p=Path(f'gpr_{method.lower()}_result.json');r=json.loads(p.read_text());r['parent_freeze_sha256']=hashlib.sha256(freeze.read_bytes()).hexdigest();r['stage']='3A'
    p.write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+'\n')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--method',choices=METHODS,required=True);run(ap.parse_args().method)
