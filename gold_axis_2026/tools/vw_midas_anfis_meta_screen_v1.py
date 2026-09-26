from __future__ import annotations
import argparse,importlib,json,math,os
from pathlib import Path
import numpy as np, psycopg
import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as eb
import vw_midas_elmfis_meta_batch_1_v1 as common
import vw_midas_anfis_vanilla_v2 as acore

DEV_START,DEV_END="2022-04","2024-12"; TR_START,TR_END="2025-01","2025-12"; ST_START,ST_END="2026-01","2026-07"
VAL_FRAC=.20; MIN_VAL=12; LOCAL_MAX_EPOCHS=100

BATCH={
 "PSO":1,"GA":1,"DE":1,
 "MPA":2,"ABC":2,"SSA":2,"GWO":2,
 "WOA":3,"HHO":3,"ACO":3,"BAT":3,
 "FA":4,"MFO":4,"FPA":4,"FA_FPA":4,
 "CS":5,"SCA":5,"SALP":5,"SMA":5,
 "GOA":6,"ALO":6,"TLBO":6,"JAYA":6,
 "HGS":7,"CHOA":7,"HGSO":7,"AOA":7,
 "CPA":8,"KRILL":8,"CROW":8,
 "DE_ABC":9,"MULTISWARM":9}

def ols_predict(theta,Xfit,Yfit,Xeval):
    c,s=common.decode(theta); l=np.log(s); b=acore.lse(Xfit,Yfit,c,l)
    return acore.design(Xeval,c,l)@b

def weighted_mae(pred,Y):
    return float(.7*np.mean(np.abs(pred[:,0]-Y[:,0]))+.3*np.mean(np.abs(pred-Y)))

def train_loss(theta,X,Y): return weighted_mae(ols_predict(theta,X,Y,X),Y)
def val_loss(theta,X,Y,Xv,Yv): return weighted_mae(ols_predict(theta,X,Y,Xv),Yv)
def pop_fit(pop,X,Y): return np.array([train_loss(z,X,Y) for z in pop],float)

def val_pick(pop,fit,X,Y,Xv,Yv,inc=None,incv=math.inf):
    k=max(3,len(pop)//4)
    for i in np.argsort(fit)[:k]:
        v=val_loss(pop[i],X,Y,Xv,Yv)
        if v<incv: inc,incv=pop[i].copy(),float(v)
    return inc,incv

# Patch shared optimizer objective from ridge-ELMFIS to ANFIS forward-pass OLS.
common.predict_with_fit=ols_predict; common.training_loss=train_loss; common.validation_loss=val_loss
common.population_fit=pop_fit; common.validation_pick=val_pick

def arrays(samples,target):
    keys=sorted(k for k in samples if k<target)
    X=np.stack([samples[k][0] for k in keys]); Y=np.stack([samples[k][1] for k in keys]); tx=samples[target][0][None,:]
    xm,xs=X.mean(0),X.std(0); ym,ys=Y.mean(0),Y.std(0)
    xs=np.where(xs<1e-9,1,xs); ys=np.where(ys<1e-9,1,ys)
    X=(X-xm)/xs; Y=(Y-ym)/ys; tx=(tx-xm)/xs
    nv=max(MIN_VAL,int(round(VAL_FRAC*len(X)))); split=len(X)-nv
    if split<30: raise RuntimeError(f"INNER_TRAIN_TOO_SMALL {target} split={split}")
    return keys,X,Y,tx,ym,ys,split

def local_step(c,l,X,Y,k,hist):
    b=acore.lse(X,Y,c,l); loss,gc,gl=acore.loss_grad(X,Y,c,l,b)
    g=np.r_[gc.ravel(),gl.ravel()]; gn=float(np.linalg.norm(g))
    if np.isfinite(gn) and gn>1e-15:
        eta=k/gn; c=c-eta*gc; l=l-eta*gl
        l=np.clip(l,math.log(acore.SFLOOR),math.log(acore.SCEIL))
    hist.append(loss)
    if len(hist)>=5:
        d=np.diff(hist[-5:]); sg=np.sign(d)
        if np.all(d<0): k*=acore.KINC
        elif np.all(sg[:-1]*sg[1:]<0): k*=acore.KDEC
    return c,l,k,loss

def choose_local_epochs(theta,X,Y,Xv,Yv):
    c,s=common.decode(theta); l=np.log(s); k=acore.K0; hist=[]; best=(math.inf,1)
    for ep in range(LOCAL_MAX_EPOCHS):
        b=acore.lse(X,Y,c,l); pred=acore.design(Xv,c,l)@b
        chk=float(np.mean((pred-Yv)**2))
        if chk<best[0]-1e-12: best=(chk,ep+1)
        c,l,k,_=local_step(c,l,X,Y,k,hist)
    return int(best[1]),float(best[0])

def local_refit(theta,X,Y,epochs):
    c,s=common.decode(theta); l=np.log(s); k=acore.K0; hist=[]
    for _ in range(epochs): c,l,k,_=local_step(c,l,X,Y,k,hist)
    return c,l,acore.lse(X,Y,c,l),{"epochs":epochs,"first_mse":hist[0],"last_mse":hist[-1]}

def module_for(method):
    n=BATCH[method]
    return importlib.import_module(f"vw_midas_elmfis_meta_batch_{n}_v1")

def select_hybrid(method,X,Y,split,target):
    mod=module_for(method); fn=mod.PHASE[method]
    Xtr,Ytr,Xv,Yv=X[:split],Y[:split],X[split:],Y[split:]
    anchor=common.initial_theta(Xtr); best=None; bestv=math.inf; bestrep=None; reps=[]
    sb=mod.SEED_BASE[method]; tseed=sum(map(ord,target))
    for rep in range(common.REPEATS):
        seed=sb+1009*rep+tseed
        th,v=fn(Xtr,Ytr,seed,common.SELECT_GENS,center=anchor,Xv=Xv,Yv=Yv,refit=False)
        reps.append({"repeat":rep,"seed":seed,"inner_validation_fitness":float(v)})
        if v<bestv: best,bestv,bestrep=th.copy(),float(v),rep
    local_epochs,local_check=choose_local_epochs(best,Xtr,Ytr,Xv,Yv)
    refseed=sb+900001+1009*int(bestrep)+tseed
    final_theta,fullfit=fn(X,Y,refseed,common.REFIT_GENS,center=best,Xv=None,Yv=None,refit=True)
    c,l,b,ld=local_refit(final_theta,X,Y,local_epochs)
    return c,l,b,{"selected_repeat":bestrep,"meta_check_fitness":bestv,"local_check_mse":local_check,
      "selected_local_epochs":local_epochs,"full_meta_refit_fitness":float(fullfit),"repeats":reps,**ld}

def predict(samples,target,method):
    keys,X,Y,tx,ym,ys,split=arrays(samples,target)
    c,l,b,d=select_hybrid(method,X,Y,split,target)
    p=(acore.design(tx,c,l)@b)[0]*ys+ym
    return p,len(keys),d

def evaluate(bundle,cache,method,a,b):
    rows=[]
    for t in base.month_range(a,b):
        p,n,d=predict(cache[t],t,method); o=base.month_shift(t,-1)
        rows.append({"target":t,"origin":o,"method":method,"train_rows":n,"hybrid_diag":d,
          "pred_log_return_gold":float(p[0]),"forecast":float(bundle.core_gold[o]*math.exp(float(p[0]))),
          "actual":float(bundle.core_gold[t]),"rw":float(bundle.core_gold[o])})
    return rows

def inv(dsn):
    with psycopg.connect(dsn,autocommit=True) as cn:
      with cn.cursor() as cur: cur.execute("SET default_transaction_read_only=on"); return base.authority_invariants(cur)

def run(method):
    dsn=os.environ["NEON_DATABASE_URL"]; bundle=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    dev=evaluate(bundle,cache,method,DEV_START,DEV_END); tr=evaluate(bundle,cache,method,TR_START,TR_END); st=evaluate(bundle,cache,method,ST_START,ST_END)
    after=inv(dsn)
    if after!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={"model_id":f"VW_MIDAS_{method}_ANFIS_HYBRID_V1","method":method,
      "hybrid_contract":{"metaheuristic":method,"meta_scope":"premise_centers_and_log_spreads","candidate_consequents":"OLS",
       "post_meta_local_learning":"Jang1993_normalized_gradient_plus_LSE","local_epoch_selection":"chronological_inner_check_only",
       "inner_check":"last_20pct_min12_pre_target","meta_repeats":common.REPEATS,"meta_select_gens":common.SELECT_GENS,
       "meta_full_refit_gens":common.REFIT_GENS,"max_local_epochs":LOCAL_MAX_EPOCHS},
      "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE","random_split":"NONE",
       "target_month_in_training":False,"selection_period":f"{DEV_START}..{DEV_END}",
       "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"},
      "dev":{"metrics":eb.active_metrics(dev),"yearly":eb.yearly(dev),"rows":dev},
      "transport_2025":{"metrics":eb.active_metrics(tr),"rows":tr},"stress_2026":{"metrics":eb.active_metrics(st),"rows":st}}
    Path(f"anfis_hybrid_{method.lower()}_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("OUTPUT_GATE=PASS"); print(json.dumps({"method":method,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--method",required=True,choices=sorted(BATCH)); run(ap.parse_args().method)
