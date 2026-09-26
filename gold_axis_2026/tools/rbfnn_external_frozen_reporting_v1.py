"""Strict external exclusion: no 2025/26 observations enter parameter selection.

Reuses unchanged Stage-1 DEV evidence. Freeze optimizer/width/ridge/geometry at
2024-12; only analytic output coefficients expand on available past history.
"""
import argparse,hashlib,json,math,os
from pathlib import Path
import numpy as np
import vw_midas_rbfnn_stage1_v1 as r

def freeze(bundle,method):
    target='2025-01';samples=r.base.all_samples_at_origin(bundle,target,governed=True)
    keys=sorted(k for k in samples if k<target)
    assert max(keys)=='2024-12'
    X0=np.stack([samples[k][0] for k in keys]);Y0=np.stack([samples[k][1] for k in keys])
    split=len(keys)-max(6,round(.2*len(keys)))
    xm,xs,ym,ys=r.vanilla.scale_fit(X0[:split],Y0[:split]);X=(X0-xm)/xs;Y=(Y0-ym)/ys
    seed=int(hashlib.sha256(target.encode()).hexdigest()[:8],16)
    c,w,counts=r.vanilla.fit_centers_widths(X[:split],seed)
    if min(counts)<1:raise r.ScientificFailure('EMPTY_INITIAL_CLUSTER')
    best=None
    for width in r.WIDTH_GRID:
        for ridge in r.RIDGE_GRID:
            obj=r.Objective(c,w*width,ridge)
            loss=obj.validation(np.zeros(72),X[:split],Y[:split],X[split:],Y[split:])
            if best is None or loss<best[0]:best=(loss,width,ridge)
    _,width,ridge=best;obj=r.Objective(c,w*width,ridge);mod,fn=r.optimizer(method,obj)
    winner=None;reps=[]
    for rep in range(r.REPEATS):
        s=(seed+mod.SEED_BASE[method]+1009*rep)%(2**32)
        th,v=fn(X[:split],Y[:split],s,r.GENS,center=np.zeros(72),Xv=X[split:],Yv=Y[split:],refit=False)
        reps.append({'repeat':rep,'seed':s,'validation_loss':float(v) if math.isfinite(v) else None})
        if th is not None and math.isfinite(v) and (winner is None or v<winner[0]):winner=(v,th,rep)
    if winner is None:raise r.ScientificFailure('NO_VALID_FROZEN_EXTERNAL_GEOMETRY')
    return obj,winner[1],(xm,xs,ym,ys),{'tuning_last':'2024-12','geometry_origin':'2024-12',
      'selected_repeat':winner[2],'repeat_records':reps,'width_scale':width,'ridge':ridge,
      'frozen_geometry_sha256':hashlib.sha256(winner[1].tobytes()+c.tobytes()+w.tobytes()).hexdigest(),
      'external_policy':'no external observations in tuning; expanding analytic output refit only'}

def run(method,source):
    d=json.loads(source.read_text());assert d['method']==method and d['status']=='COMPLETE'
    dev_hash=hashlib.sha256(json.dumps(d['dev'],sort_keys=True).encode()).hexdigest()
    assert dev_hash==d['dev_freeze_sha256']
    b=r.base.load_data(os.environ['NEON_DATABASE_URL'])
    obj,theta,sc,meta=freeze(b,method);xm,xs,ym,ys=sc
    for period,a,z in [('transport_2025','2025-01','2025-12'),('stress_2026','2026-01','2026-07')]:
        rows=[];failures=[]
        for target in r.base.month_range(a,z):
            s=r.base.all_samples_at_origin(b,target,governed=True);keys=sorted(k for k in s if k<target)
            X=(np.stack([s[k][0] for k in keys])-xm)/xs;Y=(np.stack([s[k][1] for k in keys])-ym)/ys
            try:
                c,w,beta,condition=obj.fit(theta,X,Y)
                p=(r.vanilla.design((s[target][0][None,:]-xm)/xs,c,w)@beta)[0]*ys+ym
                if not np.isfinite(p).all() or max(abs(p))>=1:raise r.ScientificFailure('PATHOLOGICAL_FOUR_OUTPUT_RETURN')
                origin=r.base.month_shift(target,-1)
                rows.append({'target':target,'origin':origin,'method':method,'pred_returns':p.tolist(),
                  'pred_log_return_gold':float(p[0]),'forecast':float(b.core_gold[origin]*math.exp(p[0])),
                  'actual':float(b.core_gold[target]),'rw':float(b.core_gold[origin]),
                  'diag':{**meta,'train_last':keys[-1],'train_rows':len(keys),'design_condition':condition,
                    'width_min':float(w.min()),'width_max':float(w.max())}})
            except r.ScientificFailure as e:failures.append({'target':target,'reason':str(e)})
        d[period]={'rows':rows,'failures':failures,'scientific_gate':'PASS' if not failures else 'FAIL',
          'metrics':r.metrics.active_metrics(rows) if not failures else None,
          'yearly':r.metrics.yearly(rows) if not failures else None}
    after=r.vanilla.read_invariants(os.environ['NEON_DATABASE_URL'])
    assert after==b.invariants_before
    d['external_lineage']={'source_run_id':d['run_id'],'run_id':os.getenv('GITHUB_RUN_ID'),
      'commit':os.getenv('GITHUB_SHA'),'source_artifact_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'superseded':'original external rows used expanding inner tuning; not strict 2025/2026 exclusion',
      'dev_unchanged':True,'invariants_before':b.invariants_before,'invariants_after':after,**meta}
    assert hashlib.sha256(json.dumps(d['dev'],sort_keys=True).encode()).hexdigest()==dev_hash
    Path(f'rbfnn_stage1_{method.lower()}_result.json').write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('STRICT_EXTERNAL_EXCLUSION_PASS',method,flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--method',required=True);ap.add_argument('--source',type=Path,required=True)
    a=ap.parse_args();run(a.method,a.source)
