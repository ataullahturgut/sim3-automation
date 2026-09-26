"""Governed RBFNN screen. Reuses exact repository optimizer update equations.

Only the objective/bounds interface is adapted; no ELMFIS fitting is called.
Each process runs one method. Do not run methods in threads: optimizer modules
have module-local configuration. Output coefficients are analytic ridge/OLS.
"""
from __future__ import annotations
import argparse, hashlib, importlib, inspect, json, math, os
from pathlib import Path
import numpy as np
import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as metrics
import vw_midas_elmfis_meta_batch_1_v1 as common
import vw_midas_rbfnn_vanilla_v1 as vanilla

BATCHES = [['PSO','GA','DE'],['MPA','ABC','SSA','GWO'],
 ['WOA','HHO','ACO','BAT'],['FA','MFO','FPA','FA_FPA'],
 ['CS','SCA','SALP','SMA'],['GOA','ALO','TLBO','JAYA'],
 ['HGS','CHOA','HGSO','AOA'],['CPA','KRILL','CROW'],['DE_ABC','MULTISWARM']]
K, D, POP, GENS, REPEATS = 8, 8, 24, 45, 3
WIDTH_GRID = (.5,1.,1.5,2.)
RIDGE_GRID = (0.,1e-4,1e-3,1e-2,.1)
LO = np.r_[np.full(K*D,-1.),np.full(K,math.log(.5))]
HI = -LO
COND_LIMIT, MIN_SEPARATION = 1e10, 1e-6

class ScientificFailure(RuntimeError): pass

def analytic(P,Y,ridge):
    # Augmented least squares avoids squaring the condition number.
    if ridge:
        penalty = np.sqrt(ridge)*np.diag([0.]+[1.]*(P.shape[1]-1))
        return np.linalg.lstsq(np.vstack([P,penalty]),
                             np.vstack([Y,np.zeros((len(penalty),4))]),rcond=None)[0]
    return np.linalg.lstsq(P,Y,rcond=None)[0]

class Objective:
    def __init__(self,c,w,ridge):
        self.c,self.w,self.ridge=c,w,ridge
        self.train_calls=self.validation_calls=self.invalid_candidates=0
    def decode(self,theta):
        return self.c+theta[:K*D].reshape(K,D), self.w*np.exp(theta[K*D:])
    def fit(self,theta,X,Y):
        c,w=self.decode(theta)
        if not np.isfinite(c).all() or not np.isfinite(w).all() or w.min()<.025-1e-12 or w.max()>40+1e-12:
            raise ScientificFailure('NONFINITE_OR_WIDTH_COLLAPSE')
        sep=np.linalg.norm(c[:,None]-c[None,:],axis=2)+np.eye(K)*1e9
        if sep.min()<MIN_SEPARATION: raise ScientificFailure('CENTER_COLLAPSE')
        P=vanilla.design(X,c,w)
        condition=float(np.linalg.cond(P))
        if not np.isfinite(condition) or condition>COND_LIMIT: raise ScientificFailure('ILL_CONDITIONED_DESIGN')
        b=analytic(P,Y,self.ridge)
        if not np.isfinite(b).all(): raise ScientificFailure('NONFINITE_BETA')
        return c,w,b,condition
    def loss(self,theta,X,Y,Xe,Ye):
        try:
            c,w,b,_=self.fit(theta,X,Y)
            p=vanilla.design(Xe,c,w)@b
            return common.weighted_mae_from_pred(p,Ye) if np.isfinite(p).all() else math.inf
        except (ScientificFailure,np.linalg.LinAlgError):
            self.invalid_candidates+=1
            return math.inf
    def training(self,theta,X,Y):
        self.train_calls+=1
        return self.loss(theta,X,Y,X,Y)
    def validation(self,theta,X,Y,Xv,Yv):
        self.validation_calls+=1
        return self.loss(theta,X,Y,Xv,Yv)

def optimizer(method,obj):
    common.PARAM_DIM=K*D+K; common.LOWER=LO; common.UPPER=HI
    common.POP_SIZE=POP
    common.LOCAL_SIGMA=np.r_[np.full(K*D,.25),np.full(K,.2)]
    common.REFIT_SIGMA=np.r_[np.full(K*D,.1),np.full(K,.1)]
    common.training_loss=obj.training; common.validation_loss=obj.validation
    batch=next(i+1 for i,x in enumerate(BATCHES) if method in x)
    mod=importlib.import_module(f'vw_midas_elmfis_meta_batch_{batch}_v1')
    mod.PARAM_DIM=K*D+K; mod.LOWER=LO; mod.UPPER=HI; mod.SPAN=HI-LO; mod.POP_SIZE=POP
    return mod,mod.PHASE[method]

def predict(samples,target,method):
    keys=sorted(k for k in samples if k<target)
    X0=np.stack([samples[k][0] for k in keys]);Y0=np.stack([samples[k][1] for k in keys])
    tx0=samples[target][0][None,:]
    split=len(keys)-max(6,round(.2*len(keys)))
    if split<30: raise RuntimeError('INNER_TRAIN_TOO_SMALL')
    xm,xs,ym,ys=vanilla.scale_fit(X0[:split],Y0[:split])
    X=(X0-xm)/xs;Y=(Y0-ym)/ys;tx=(tx0-xm)/xs
    seed=int(hashlib.sha256(target.encode()).hexdigest()[:8],16)
    c,w,counts=vanilla.fit_centers_widths(X[:split],seed)
    if min(counts)<1: raise ScientificFailure('EMPTY_INITIAL_CLUSTER')
    # Compact structural reference chosen on chronological past-only validation.
    best=None
    for width in WIDTH_GRID:
        for ridge in RIDGE_GRID:
            ob=Objective(c,w*width,ridge)
            loss=ob.validation(np.zeros(K*D+K),X[:split],Y[:split],X[split:],Y[split:])
            if best is None or loss<best[0]:best=(loss,width,ridge)
    if not math.isfinite(best[0]):raise ScientificFailure('NO_VALID_STRUCTURAL_REFERENCE')
    _,width,ridge=best;obj=Objective(c,w*width,ridge);mod,fn=optimizer(method,obj)
    reps=[];winner=None
    for rep in range(REPEATS):
        repeat_seed=(seed+mod.SEED_BASE[method]+1009*rep)%(2**32)
        th,loss=fn(X[:split],Y[:split],repeat_seed,GENS,center=np.zeros(K*D+K),Xv=X[split:],Yv=Y[split:],refit=False)
        reps.append({'repeat':rep,'seed':repeat_seed,'validation_loss':float(loss) if math.isfinite(loss) else None})
        if th is not None and math.isfinite(loss) and (winner is None or loss<winner[0]):winner=(loss,th,rep)
    if winner is None:raise ScientificFailure('NO_VALID_OPTIMIZER_CANDIDATE')
    # Preserve selected geometry AND scaling. Re-estimating k-means would permute
    # center identities and invalidate learned per-center perturbations.
    c,w,b,condition=obj.fit(winner[1],X,Y)
    pred=(vanilla.design(tx,c,w)@b)[0]*ys+ym
    if not np.isfinite(pred).all() or np.max(np.abs(pred))>=1:
        raise ScientificFailure('PATHOLOGICAL_OR_NONFINITE_FOUR_OUTPUT_RETURN')
    nearest=np.argmin(np.linalg.norm(X[:,None]-c[None,:],axis=2),axis=1)
    occupied=np.bincount(nearest,minlength=K).tolist()
    # Evolved RBF bases need not partition training observations. Empty nearest
    # regions are diagnostic, while coincident centers/design collapse are gates.
    return pred,{'train_rows':len(keys),'train_last':keys[-1],'inner_train_last':keys[split-1],
      'validation_first':keys[split],'validation_last':keys[-1], 'initial_cluster_counts':counts,
      'evolved_nearest_center_counts':occupied,'width_min':float(w.min()),'width_max':float(w.max()),
      'design_condition':condition,'width_scale':width,'ridge':ridge,'repeat_records':reps,
      'selected_repeat':winner[2],'selected_validation_loss':winner[0],
      'training_fitness_calls':obj.train_calls,'validation_calls':obj.validation_calls,
      'invalid_candidate_evaluations':obj.invalid_candidates,
      'refit':'analytic_output_on_all_history; frozen_inner_geometry_and_scaler',
      'theta_sha256':hashlib.sha256(winner[1].tobytes()).hexdigest()}

def evaluate(bundle,method,start,end):
    rows=[];failures=[]
    for target in base.month_range(start,end):
        try:
            samples=base.all_samples_at_origin(bundle,target,governed=True)
            pred,diag=predict(samples,target,method);origin=base.month_shift(target,-1)
            rows.append({'target':target,'origin':origin,'method':method,'diag':diag,
              'pred_returns':pred.tolist(),'pred_log_return_gold':float(pred[0]),
              'forecast':float(bundle.core_gold[origin]*math.exp(pred[0])),
              'actual':float(bundle.core_gold[target]),'rw':float(bundle.core_gold[origin])})
        except ScientificFailure as e:failures.append({'target':target,'reason':str(e)})
        print(method,target,'DONE' if not failures or failures[-1]['target']!=target else 'SCIENTIFIC_FAILURE',flush=True)
    return {'rows':rows,'failures':failures,'scientific_gate':'PASS' if not failures else 'FAIL',
      'metrics':metrics.active_metrics(rows) if not failures else None,
      'yearly':metrics.yearly(rows) if not failures else None}

def run(method):
    dsn=os.environ['NEON_DATABASE_URL'];bundle=base.load_data(dsn)
    mod,fn=optimizer(method,Objective(np.zeros((K,D)),np.ones(K),.001))
    source=Path(inspect.getfile(mod))
    out={'model_id':f'RBFNN_STAGE1_V1_{method}','method':method,
      'commit':os.getenv('GITHUB_SHA'),'run_id':os.getenv('GITHUB_RUN_ID'),
      'spec':{'inputs':8,'outputs':4,'centers':K,'basis':'isotropic_Gaussian',
        'optimizer_source':str(source.relative_to(Path.cwd())) if source.is_relative_to(Path.cwd()) else source.name,
        'optimizer_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'optimizer_function':fn.__name__,'population':POP,'generations':GENS,'repeats':REPEATS,
        'center_delta_bounds':[-1,1],'log_width_multiplier_bounds':[float(LO[-1]),float(HI[-1])],
        'width_scale_grid':WIDTH_GRID,'ridge_grid':RIDGE_GRID,'objective':'.7 Gold + .3 four-output standardized MAE',
        'validation':'last20pct_min6; inner-training-only_scaler; top_quartile_training_candidates',
        'refit':'analytic output only on full pre-target history; selected geometry/scaler frozen',
        'condition_limit':COND_LIMIT,'minimum_center_separation':MIN_SEPARATION},
      'authority':{'selection':'2022-04..2024-12','2025':'REPORTING_ONLY','2026':'REPORTING_ONLY',
        'database':'READ_ONLY','random_split':False,'target_month_fitness':False,
        'source_checks':bundle.source_checks,'invariants_before':bundle.invariants_before}}
    path=Path(f'rbfnn_stage1_{method.lower()}_result.json')
    out['dev']=evaluate(bundle,method,'2022-04','2024-12')
    out['dev_decision_frozen_before_external']='ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED' if out['dev']['scientific_gate']=='PASS' else 'REJECTED_SCIENTIFIC_FAILURE'
    out['dev_freeze_sha256']=hashlib.sha256(json.dumps(out['dev'],sort_keys=True).encode()).hexdigest()
    path.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    for name,a,z in [('transport_2025','2025-01','2025-12'),('stress_2026','2026-01','2026-07')]:
        out[name]=evaluate(bundle,method,a,z)
        path.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    after=vanilla.read_invariants(dsn)
    if after!=bundle.invariants_before:raise RuntimeError('AUTHORITY_INVARIANTS_CHANGED')
    out['authority']['invariants_after']=after
    out['status']='COMPLETE'
    path.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'method':method,'dev':out['dev']['metrics'],'decision':out['dev_decision_frozen_before_external']}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--method',required=True,choices=sum(BATCHES,[]))
    run(parser.parse_args().method)
