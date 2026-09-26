"""Mandatory parity refinements; executable only after a committed Stage-2 freeze."""
import argparse,hashlib,importlib,json,math,os,sys
from pathlib import Path
import numpy as np
import vw_midas_rbfnn_stage1_v1 as r
import rbfnn_external_frozen_reporting_v1 as external

METHODS=['ADAPTIVE_PSO','ADAPTIVE_TLBO','TLBO_TUNED_PSO','DE_TUNED_PSO','ADAPTIVE_CROW','PSO_TLBO']
SEED_BASE={m:400000+i*10000 for i,m in enumerate(METHODS)}
ORIGINAL_OPTIMIZER=r.optimizer
ORIGINAL_PREDICT=r.predict
CURRENT_META={}

def finite_json(x):
    if isinstance(x,dict):return {k:finite_json(v) for k,v in x.items()}
    if isinstance(x,list):return [finite_json(v) for v in x]
    if isinstance(x,float) and not math.isfinite(x):return None
    return x

def optimizer(method,obj):
    global CURRENT_META
    ORIGINAL_OPTIMIZER('PSO',obj)
    number=31 if method in METHODS[:2] else 32 if method in METHODS[2:4] else 33
    mod=importlib.import_module(f'vw_midas_elmfis_stage3_batch{number}_v1')
    mod.LO=r.LO;mod.HI=r.HI;mod.SPAN=r.HI-r.LO
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
            if not math.isfinite(score):raise r.ScientificFailure('NO_VALID_OUTER_TUNING')
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

def predict(samples,target,method):
    p,d=ORIGINAL_PREDICT(samples,target,method)
    d['refinement']=finite_json(CURRENT_META)
    return p,d

def run(method):
    freeze_path=Path('gold_axis_2026/GOLD_MONTHLY_RBFNN_STAGE2_FREEZE_2026-09-26.json')
    f=json.loads(freeze_path.read_text());assert f['status']=='FROZEN_BEFORE_STAGE3'
    assert f['external_metrics_used'] is False
    r.optimizer=optimizer;r.predict=predict
    b=r.base.load_data(os.environ['NEON_DATABASE_URL'])
    dev=r.evaluate(b,method,'2022-04','2024-12')
    after=r.vanilla.read_invariants(os.environ['NEON_DATABASE_URL']);assert after==b.invariants_before
    d={'status':'COMPLETE','model_id':'RBFNN_STAGE3A_V1_'+method,'method':method,
      'run_id':os.getenv('GITHUB_RUN_ID'),'commit':os.getenv('GITHUB_SHA'),
      'parent_freeze_sha256':hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
      'spec':{'condition_limit':r.COND_LIMIT,'inputs':8,'outputs':4,'centers':8,
        'population':24,'generations':45,'repeats':3,'parameter_bounds':[r.LO.tolist(),r.HI.tolist()],
        'refinement_spec':'per-origin diag.refinement contains exact outer parameters, trace and source hash',
        'analytic_output':'augmented least-squares ridge; full pre-target refit',
        'external_tuning_cutoff':'2024-12'},
      'authority':{'selection':'DEV_ONLY','2025':'REPORTING_ONLY','2026':'REPORTING_ONLY',
        'database':'READ_ONLY','random_split':False,'target_month_fitness':False,
        'invariants_before':b.invariants_before,'invariants_after':after},'dev':dev,
      'dev_decision_frozen_before_external':'ELIGIBLE_FOR_STAGE4' if dev['scientific_gate']=='PASS' else 'REJECTED_SCIENTIFIC_FAILURE'}
    d['dev_freeze_sha256']=hashlib.sha256(json.dumps(dev,sort_keys=True).encode()).hexdigest()
    source=Path('stage3_dev_frozen.json');source.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+'\n')
    external.run(method,source)
    Path(f'rbfnn_stage1_{method.lower()}_result.json').rename(f'rbfnn_stage3a_{method.lower()}_result.json')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--method',required=True,choices=METHODS)
    run(ap.parse_args().method)
