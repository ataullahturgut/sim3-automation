"""Multi-output orthogonal forward selection RBF, Chen/Grant/Cowan 1991.

Primary source: https://www.southampton.ac.uk/~sqc/listP/c-icann1991.pdf
Adaptations explicitly declared: standardized four outputs, intercept, compact
chronological width/center-count/ridge selection, rather than paper's tolerance.
"""
import hashlib,json,math,os
from pathlib import Path
import numpy as np
import vw_midas_rbfnn_stage1_v1 as r

COUNTS=(4,6,8,12)

def order_centers(X,Y,width,maximum=12):
    candidates=np.unique(X,axis=0)
    phi=r.vanilla.design(X,candidates,np.full(len(candidates),width))[:,1:]
    Q=np.ones((len(X),1))/np.sqrt(len(X));selected=[]
    for _ in range(min(maximum,len(candidates))):
        residual=phi-Q@(Q.T@phi)
        residual-=Q@(Q.T@residual) # reorthogonalization
        norm2=np.sum(residual**2,axis=0)
        gain=np.sum((residual.T@Y)**2,axis=1)/np.maximum(norm2,1e-300)
        gain[norm2<1e-10]=-np.inf
        gain[selected]=-np.inf
        j=int(np.argmax(gain))
        if not np.isfinite(gain[j]):break
        selected.append(j)
        Q=np.column_stack([Q,residual[:,j]/np.sqrt(norm2[j])])
    return candidates[selected]

def fit_geometry(samples,target):
    keys=sorted(k for k in samples if k<target)
    X0=np.stack([samples[k][0] for k in keys]);Y0=np.stack([samples[k][1] for k in keys])
    split=len(keys)-max(6,round(.2*len(keys)))
    if split<30:raise RuntimeError('INNER_TRAIN_TOO_SMALL')
    sc=r.vanilla.scale_fit(X0[:split],Y0[:split]);xm,xs,ym,ys=sc
    X=(X0-xm)/xs;Y=(Y0-ym)/ys
    distances=np.linalg.norm(X[:split,None]-X[None,:split],axis=2)
    width0=float(np.median(distances[distances>1e-9]));best=None
    for ws in r.WIDTH_GRID:
        width=width0*ws
        c=order_centers(X[:split],Y[:split],width)
        for count in COUNTS:
            if len(c)<count:continue
            centers=c[:count];widths=np.full(count,width)
            P=r.vanilla.design(X[:split],centers,widths);Pv=r.vanilla.design(X[split:],centers,widths)
            if np.linalg.cond(P)>r.COND_LIMIT:continue
            for ridge in r.RIDGE_GRID:
                beta=r.analytic(P,Y[:split],ridge)
                score=r.common.weighted_mae_from_pred(Pv@beta,Y[split:])
                if best is None or score<best[0]:best=(score,centers.copy(),widths.copy(),ridge)
    if best is None:raise r.ScientificFailure('NO_VALID_MOLS_GEOMETRY')
    v,c,w,ridge=best
    counts=np.bincount(np.argmin(np.linalg.norm(X[:split,None]-c[None,:],axis=2),axis=1),minlength=len(c))
    if min(counts)==0:raise r.ScientificFailure('EMPTY_SELECTED_CENTER')
    return c,w,ridge,sc,{'centers':len(c),'width':float(w[0]),'ridge':ridge,'inner_validation':v,
      'initial_cluster_counts':counts.tolist(),'width_min':float(w.min()),'width_max':float(w.max()),
      'inner_train_last':keys[split-1],'validation_first':keys[split],'validation_last':keys[-1],
      'tuning_last':keys[-1],'mechanism':'multi-output orthogonal forward explained-trace selection',
      'geometry_sha256':hashlib.sha256(c.tobytes()+w.tobytes()).hexdigest()}

def forecast(samples,target,geometry):
    c,w,ridge,sc,meta=geometry;xm,xs,ym,ys=sc
    keys=sorted(k for k in samples if k<target)
    X=(np.stack([samples[k][0] for k in keys])-xm)/xs;Y=(np.stack([samples[k][1] for k in keys])-ym)/ys
    P=r.vanilla.design(X,c,w);condition=float(np.linalg.cond(P))
    if not np.isfinite(condition) or condition>r.COND_LIMIT:raise r.ScientificFailure('ILL_CONDITIONED')
    beta=r.analytic(P,Y,ridge)
    p=(r.vanilla.design((samples[target][0][None,:]-xm)/xs,c,w)@beta)[0]*ys+ym
    if not np.isfinite(p).all() or max(abs(p))>=1:raise r.ScientificFailure('PATHOLOGICAL_RETURN')
    sep=np.linalg.norm(c[:,None]-c[None,:],axis=2)+np.eye(len(c))*1e9
    if sep.min()<1e-6 or min(w)<.025 or max(w)>40:raise r.ScientificFailure('COLLAPSED_GEOMETRY')
    return p,{**meta,'train_last':keys[-1],'train_rows':len(keys),'design_condition':condition}

def evaluate(bundle,a,z,frozen=None):
    rows=[];fails=[]
    for target in r.base.month_range(a,z):
        samples=r.base.all_samples_at_origin(bundle,target,governed=True)
        try:
            geometry=frozen if frozen is not None else fit_geometry(samples,target)
            p,d=forecast(samples,target,geometry);o=r.base.month_shift(target,-1)
            rows.append({'target':target,'origin':o,'forecast':float(bundle.core_gold[o]*math.exp(p[0])),
              'actual':float(bundle.core_gold[target]),'rw':float(bundle.core_gold[o]),'pred_returns':p.tolist(),'diag':d})
        except r.ScientificFailure as e:fails.append({'target':target,'reason':str(e)})
    return {'rows':rows,'failures':fails,'scientific_gate':'PASS' if not fails else 'FAIL',
      'metrics':r.metrics.active_metrics(rows) if not fails else None,'yearly':r.metrics.yearly(rows) if not fails else None}

def run():
    stage=Path('gold_axis_2026/GOLD_MONTHLY_RBFNN_STAGE3AB_CLOSURE_2026-09-26.json')
    assert json.loads(stage.read_text())['status']=='COMPLETE'
    dsn=os.environ['NEON_DATABASE_URL'];b=r.base.load_data(dsn)
    d={'method':'MOLS_RBFNN','model_id':'RBFNN_STAGE3C_MOLS_V1','run_id':os.getenv('GITHUB_RUN_ID'),'commit':os.getenv('GITHUB_SHA'),
      'source':'https://www.southampton.ac.uk/~sqc/listP/c-icann1991.pdf',
      'source_mechanism':'forward orthogonal basis selection maximizing explained covariance trace over four outputs',
      'adaptations':['Gaussian basis with intercept','center-count grid replaces paper tolerance stopping',
        'chronological width and ridge validation','standardized outputs; Gold-weighted validation MAE'],
      'spec':{'counts':COUNTS,'width_scale_grid':r.WIDTH_GRID,'ridge_grid':r.RIDGE_GRID,'condition_limit':r.COND_LIMIT,
        'metaheuristic':False,'output_fit':'analytic joint four-output ridge/OLS'},
      'authority':{'selection':'DEV_ONLY','database':'READ_ONLY','2025':'REPORTING_ONLY','2026':'REPORTING_ONLY','invariants_before':b.invariants_before}}
    d['dev']=evaluate(b,'2022-04','2024-12')
    d['dev_decision_frozen_before_external']='ELIGIBLE_FOR_STAGE4' if d['dev']['scientific_gate']=='PASS' else 'REJECTED_SCIENTIFIC_FAILURE'
    d['dev_freeze_sha256']=hashlib.sha256(json.dumps(d['dev'],sort_keys=True).encode()).hexdigest()
    path=Path('rbfnn_stage3c_mols_result.json');path.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    frozen=fit_geometry(r.base.all_samples_at_origin(b,'2025-01',governed=True),'2025-01')
    d['transport_2025']=evaluate(b,'2025-01','2025-12',frozen);d['stress_2026']=evaluate(b,'2026-01','2026-07',frozen)
    d['authority']['invariants_after']=r.vanilla.read_invariants(dsn)
    assert d['authority']['invariants_after']==b.invariants_before
    d['status']='COMPLETE';path.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(d['dev']['metrics']),flush=True)

if __name__=='__main__':run()
