"""Pool freeze separated from evaluation; strict prequential simplex/shrinkage."""
import argparse,gzip,hashlib,json,os
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
import vw_midas_elmfis_baseline_v1 as metric

PERIODS=('dev','transport_2025','stress_2026');ALPHAS=(0.,.10,.25,.50,.75,1.)

from gpr_stage2_v1 import load

def metrics(rows):
    m=metric.active_metrics(rows);ae=np.array([abs(r['forecast']-r['actual']) for r in rows])
    m.update(worst_ae=float(ae.max()),worst_month=rows[int(ae.argmax())]['target'])
    return m

def freeze(root,path):
    assert json.loads((root/'GOLD_MONTHLY_GPR_STAGE3_CLOSURE_2026-09-26.json').read_text())['status']=='COMPLETE'
    all_models=load(root)
    models={n:d for n,d in all_models.items() if d['spec']['outputs']==4 and len(d['dev']['rows'])==33 and d['dev'].get('scientific_gate','PASS')=='PASS'}
    ms={n:metrics(d['dev']['rows']) for n,d in models.items()}
    roles={'architecture_anchor':'VANILLA_ICM_RBF','price_leader':min(ms,key=lambda n:ms[n]['sum_abs_error']),
      'direction_leader':min(ms,key=lambda n:(-ms[n]['direction_correct'],ms[n]['sum_abs_error'])),
      'stability_model':min(ms,key=lambda n:max(x['relative_mae_vs_rw'] for x in metric.yearly(models[n]['dev']['rows']).values()))}
    refined=[n for n in models if n.startswith('ADAPTIVE') or 'TUNED' in n or n=='PSO_TLBO' or n.startswith('MPA_')]
    if refined:roles['refinement_representative']=min(refined,key=lambda n:ms[n]['sum_abs_error'])
    full=list(dict.fromkeys(roles.values()));reduced=full.copy();removed={}
    protected={roles['architecture_anchor'],roles['price_leader'],roles['direction_leader']}
    errors={n:np.array([r['forecast']-r['actual'] for r in models[n]['dev']['rows']]) for n in full}
    for n in full:
        if n in protected:continue
        for o in reduced:
            if n==o:continue
            corr=float(np.corrcoef(errors[n],errors[o])[0,1])
            if corr>.95 and ms[o]['sum_abs_error']<=ms[n]['sum_abs_error'] and ms[o]['direction_correct']>=ms[n]['direction_correct']:
                reduced.remove(n);removed[n]={'dominator':o,'signed_error_correlation':corr};break
    out={'status':'FROZEN_BEFORE_ENSEMBLE_EVALUATION','roles':roles,'FULL':full,'REDUCED':reduced,'removed':removed,
      'selection':'DEV_ONLY','alphas':ALPHAS,'minimum_meta_history':6,'simplex_objective':'prior ΣAE',
      'external_weights':'frozen_at_end_of_DEV_no_external_loss_updates',
      'source_dev_hashes':{n:hashlib.sha256(json.dumps(models[n]['dev'],sort_keys=True).encode()).hexdigest() for n in full}}
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))

def simplex(P,y):
    n,k=P.shape;c=np.r_[np.zeros(k),np.ones(n)]
    A=np.r_[np.c_[P,-np.eye(n)],np.c_[-P,-np.eye(n)]];b=np.r_[y,-y]
    eq=np.r_[np.ones(k),np.zeros(n)][None,:]
    res=linprog(c,A_ub=A,b_ub=b,A_eq=eq,b_eq=[1.],bounds=[(0,1)]*k+[(0,None)]*n,method='highs')
    if not res.success:raise RuntimeError('SIMPLEX_LP_FAILURE '+res.message)
    w=np.maximum(res.x[:k],0);w/=w.sum();return w

def aligned(models,names,period):
    rows=sorted(models[names[0]][period]['rows'],key=lambda r:r['target'])
    P=[]
    for n in names:
        rr=sorted(models[n][period]['rows'],key=lambda r:r['target'])
        assert [(r['target'],r['actual'],r['rw']) for r in rr]==[(r['target'],r['actual'],r['rw']) for r in rows]
        P.append([r['forecast'] for r in rr])
    return np.array(P).T,rows

def pack(pred,rows):
    rr=[{'target':r['target'],'actual':r['actual'],'rw':r['rw'],'forecast':float(p)} for p,r in zip(pred,rows)]
    return {'rows':rr,'metrics':metrics(rr),'yearly':metric.yearly(rr)}

def prequential_weights(P,y,minimum_history=6):
    u=np.ones(P.shape[1])/P.shape[1];W=[];V=[]
    for i in range(len(y)):
        if i<minimum_history:w=v=u.copy()
        else:
            w=simplex(P[:i],y[:i]);v=1/np.maximum(np.mean(abs(P[:i]-y[:i,None]),axis=0),1e-12);v/=v.sum()
        W.append(w);V.append(v)
    return np.array(W),np.array(V)

def evaluate(root,pool_path,out_path):
    pools=json.loads(pool_path.read_text());assert pools['status']=='FROZEN_BEFORE_ENSEMBLE_EVALUATION'
    models=load(root)
    for n,h in pools['source_dev_hashes'].items():assert hashlib.sha256(json.dumps(models[n]['dev'],sort_keys=True).encode()).hexdigest()==h
    out={'pool_freeze_sha256':hashlib.sha256(pool_path.read_bytes()).hexdigest(),'authority':'DEV_ONLY','pools':{},
      'run_id':os.getenv('GITHUB_RUN_ID'),'commit':os.getenv('GITHUB_SHA'),
      'external_policy':'ensemble weights frozen after DEV; all component GP hyperparameters/kernel/scalers frozen 2024-12; exact posterior conditions on expanding past observations',
      'limitation':'prequential weights conditional on a DEV-selected frozen component pool; not an independent holdout estimate'}
    for pool_name in ['FULL','REDUCED']:
        names=pools[pool_name];P,rows=aligned(models,names,'dev');y=np.array([r['actual'] for r in rows]);k=len(names);u=np.ones(k)/k
        W,V=prequential_weights(P,y,pools['minimum_meta_history']);final=simplex(P,y)
        vf=1/np.maximum(np.mean(abs(P-y[:,None]),axis=0),1e-12);vf/=vf.sum()
        variants={'SIMPLE_AVERAGE':(P@u,u),'MEDIAN':(np.median(P,axis=1),None),'INVERSE_PRIOR_MAE':(np.sum(P*V,axis=1),vf)}
        for a in ALPHAS:variants[f'SHRINK_{a:.2f}']=(np.sum(P*((1-a)*u+a*W),axis=1),(1-a)*u+a*final)
        rec={'components':names,'diagnostic_full_DEV_simplex':pack(P@final,rows),'diagnostic_weights':final.tolist(),
          'prequential_optimized_weights':W.tolist(),'prequential_inverse_weights':V.tolist(),'variants':{}}
        for name,(pred,w) in variants.items():
            v={'dev':pack(pred,rows),'frozen_external_weights':w.tolist() if w is not None else 'MEDIAN'}
            for period in PERIODS[1:]:
                expected={'transport_2025':12,'stress_2026':7}[period]
                if any(len(models[n][period]['rows'])!=expected or models[n][period].get('scientific_gate','PASS')!='PASS' for n in names):
                    v[period]={'rows':[],'scientific_gate':'FAIL','metrics':None,'yearly':None,'reason':'INCOMPLETE_COMPONENT_EXTERNAL_REPORT; frozen DEV pool unchanged'}
                    continue
                X,rr=aligned(models,names,period)
                v[period]=pack(np.median(X,axis=1) if w is None else X@w,rr)
            rec['variants'][name]=v
        rec['selected_alpha']=min(ALPHAS,key=lambda a:(rec['variants'][f'SHRINK_{a:.2f}']['dev']['metrics']['sum_abs_error'],-rec['variants'][f'SHRINK_{a:.2f}']['dev']['metrics']['direction_correct']))
        rec['leave_one_component_out_diagnostic']={}
        for n in names:
            if len(names)>1:
                ix=[i for i,m in enumerate(names) if m!=n]
                rec['leave_one_component_out_diagnostic'][n]=pack(np.mean(P[:,ix],axis=1),rows)['metrics']
        out['pools'][pool_name]=rec
    out['status']='COMPLETE';out_path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({n:{'alpha':d['selected_alpha'],'best':min(d['variants'],key=lambda v:d['variants'][v]['dev']['metrics']['sum_abs_error'])} for n,d in out['pools'].items()}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['freeze','evaluate']);ap.add_argument('root',type=Path);ap.add_argument('pool',type=Path);ap.add_argument('--out',type=Path)
    a=ap.parse_args();freeze(a.root,a.pool) if a.mode=='freeze' else evaluate(a.root,a.pool,a.out)
