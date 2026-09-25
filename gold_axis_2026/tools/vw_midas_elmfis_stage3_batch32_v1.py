from __future__ import annotations

import argparse, json, math, os
from pathlib import Path
import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_meta_batch_1_v1 as common

DEV_START,DEV_END=common.DEV_START,common.DEV_END
TR_START,TR_END=common.TR_START,common.TR_END
ST_START,ST_END=common.ST_START,common.ST_END
LO,HI=common.LOWER,common.UPPER
SPAN=HI-LO

OUTER_PSO_POP=12
OUTER_PSO_ITERS=20
TLBO_POP=6
TLBO_ITERS=5
DE_POP=8
DE_ITERS=6
FINAL_POP=24
FINAL_ITERS=45
REFIT_ITERS=15
REPEATS=3
MIN_VAL=6

QLO=np.array([.2,.2,.2,.05],float)
QHI=np.array([.95,3.0,3.0,.8],float)

def split_xy(X,Y):
    nv=max(MIN_VAL,int(round(.2*len(X))))
    s=len(X)-nv
    if s<24: raise RuntimeError(f"INNER_TRAIN_TOO_SMALL n={len(X)} split={s}")
    return X[:s],Y[:s],X[s:],Y[s:]

def parse_q(q):
    q=np.clip(np.asarray(q,float),QLO,QHI)
    return tuple(float(x) for x in q)

def init_pop(rng,pop,center,refit=False):
    center=np.clip(np.asarray(center,float),LO,HI)
    P=np.empty((pop,common.PARAM_DIM),float)
    P[0]=center
    sigma=(common.REFIT_SIGMA if refit else common.LOCAL_SIGMA)
    nlocal=min(pop-1,max(1,(pop-1)//2))
    if nlocal>0:
        P[1:1+nlocal]=np.clip(center[None,:]+rng.normal(0,1,(nlocal,common.PARAM_DIM))*sigma,LO,HI)
    start=1+nlocal
    if start<pop:
        P[start:]=rng.uniform(LO,HI,(pop-start,common.PARAM_DIM))
    return P

def train_obj(theta,X,Y):
    return common.training_loss(theta,X,Y)

def val_obj(theta,Xtr,Ytr,Xv,Yv):
    return common.validation_loss(theta,Xtr,Ytr,Xv,Yv)

def pso_train(X,Y,q,seed,pop,iters,center,refit=False):
    w,c1,c2,vf=parse_q(q)
    rng=np.random.default_rng(seed)
    P=init_pop(rng,pop,center,refit)
    V=np.zeros_like(P)
    F=np.array([train_obj(z,X,Y) for z in P])
    PB=P.copy(); PF=F.copy()
    gi=int(np.argmin(PF)); GB=PB[gi].copy(); GF=float(PF[gi])
    vmax=vf*SPAN
    for _ in range(iters):
        r1=rng.random(P.shape); r2=rng.random(P.shape)
        V=np.clip(w*V+c1*r1*(PB-P)+c2*r2*(GB-P),-vmax,vmax)
        P=np.clip(P+V,LO,HI)
        F=np.array([train_obj(z,X,Y) for z in P])
        imp=F<PF
        PB[imp]=P[imp]; PF[imp]=F[imp]
        gi=int(np.argmin(PF))
        if float(PF[gi])<GF:
            GB=PB[gi].copy(); GF=float(PF[gi])
    return GB,GF

def outer_score(q,Xtr,Ytr,Xv,Yv,seed,anchor):
    vals=[]
    for rep in range(2):
        th,_=pso_train(Xtr,Ytr,q,seed+97*rep,OUTER_PSO_POP,OUTER_PSO_ITERS,anchor,False)
        vals.append(val_obj(th,Xtr,Ytr,Xv,Yv))
    return float(np.mean(vals))

def tlbo_tune(Xtr,Ytr,Xv,Yv,seed,anchor):
    rng=np.random.default_rng(seed)
    P=rng.uniform(QLO,QHI,(TLBO_POP,4))
    F=np.array([outer_score(q,Xtr,Ytr,Xv,Yv,seed+1000+i,anchor) for i,q in enumerate(P)])
    trace=[]
    for g in range(TLBO_ITERS):
        teacher=P[int(np.argmin(F))].copy(); mean=P.mean(0)
        tf=int(rng.integers(1,3))
        for i in range(TLBO_POP):
            q=np.clip(P[i]+rng.random(4)*(teacher-tf*mean),QLO,QHI)
            f=outer_score(q,Xtr,Ytr,Xv,Yv,seed+10000+g*100+i,anchor)
            if f<F[i]: P[i]=q; F[i]=f
        for i in range(TLBO_POP):
            j=i
            while j==i: j=int(rng.integers(0,TLBO_POP))
            direction=P[i]-P[j] if F[i]<F[j] else P[j]-P[i]
            q=np.clip(P[i]+rng.random(4)*direction,QLO,QHI)
            f=outer_score(q,Xtr,Ytr,Xv,Yv,seed+20000+g*100+i,anchor)
            if f<F[i]: P[i]=q; F[i]=f
        trace.append({"iteration":g,"best_outer_validation":float(np.min(F))})
    i=int(np.argmin(F))
    return P[i].copy(),float(F[i]),trace

def de_tune(Xtr,Ytr,Xv,Yv,seed,anchor):
    rng=np.random.default_rng(seed)
    P=rng.uniform(QLO,QHI,(DE_POP,4))
    F=np.array([outer_score(q,Xtr,Ytr,Xv,Yv,seed+1000+i,anchor) for i,q in enumerate(P)])
    trace=[]
    for g in range(DE_ITERS):
        for i in range(DE_POP):
            pool=[j for j in range(DE_POP) if j!=i]
            a,b,c=rng.choice(pool,3,replace=False)
            mutant=np.clip(P[a]+.7*(P[b]-P[c]),QLO,QHI)
            mask=rng.random(4)<.9
            mask[rng.integers(0,4)]=True
            q=np.where(mask,mutant,P[i])
            f=outer_score(q,Xtr,Ytr,Xv,Yv,seed+10000+g*100+i,anchor)
            if f<F[i]: P[i]=q; F[i]=f
        trace.append({"iteration":g,"best_outer_validation":float(np.min(F))})
    i=int(np.argmin(F))
    return P[i].copy(),float(F[i]),trace

def select_and_refit(X,Y,target,outer):
    Xtr,Ytr,Xv,Yv=split_xy(X,Y)
    anchor=common.initial_theta(Xtr)
    seed0=(507110 if outer=="TLBO" else 607110)+sum(map(ord,target))
    if outer=="TLBO":
        q,outer_val,trace=tlbo_tune(Xtr,Ytr,Xv,Yv,seed0,anchor)
    else:
        q,outer_val,trace=de_tune(Xtr,Ytr,Xv,Yv,seed0,anchor)

    reps=[]; best=None
    for rep in range(REPEATS):
        th,trfit=pso_train(Xtr,Ytr,q,seed0+500000+97*rep,FINAL_POP,FINAL_ITERS,anchor,False)
        val=val_obj(th,Xtr,Ytr,Xv,Yv)
        row=(val,th,trfit,rep)
        reps.append(row)
        if best is None or val<best[0]: best=row

    val,th,trfit,rep=best
    final,full=pso_train(X,Y,q,seed0+900001+97*rep,FINAL_POP,REFIT_ITERS,th,True)
    return final,{
        "outer_optimizer":outer,
        "outer_validation_score":float(outer_val),
        "outer_trace":trace,
        "selected_repeat":int(rep),
        "selected_pso":{"w":float(q[0]),"c1":float(q[1]),"c2":float(q[2]),"vmax_frac":float(q[3])},
        "inner_validation_fitness":float(val),
        "full_history_refit_objective":float(full),
        "repeat_validation":[{"repeat":int(z[3]),"inner_validation_fitness":float(z[0]),"inner_train_objective":float(z[2])} for z in reps],
    }

def predict_target(samples,target,outer):
    keys,X,Y,tx,ym,ys,split=common.arrays(samples,target)
    th,meta=select_and_refit(X,Y,target,outer)
    pred_std=common.predict_with_fit(th,X,Y,tx)[0]
    return pred_std*ys+ym,len(keys),meta

def evaluate(bundle,cache,outer,start,end):
    rows=[]
    for target in base.month_range(start,end):
        pred,n,meta=predict_target(cache[target],target,outer)
        origin=base.month_shift(target,-1)
        rows.append({
            "target":target,"origin":origin,"method":f"{outer}_TUNED_PSO","train_rows":n,**meta,
            "pred_log_return_gold":float(pred[0]),
            "forecast":float(bundle.core_gold[origin]*math.exp(float(pred[0]))),
            "actual":float(bundle.core_gold[target]),
            "rw":float(bundle.core_gold[origin]),
        })
    return rows

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--outer",required=True,choices=["TLBO","DE"])
    args=parser.parse_args()
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    dev=evaluate(bundle,cache,args.outer,DEV_START,DEV_END)
    tr=evaluate(bundle,cache,args.outer,TR_START,TR_END)
    st=evaluate(bundle,cache,args.outer,ST_START,ST_END)
    after=read_invariants(dsn)
    if after!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    key=f"{args.outer}_TUNED_PSO"
    out={
        "batch_id":"VW_MIDAS_ELMFIS_STAGE3_BATCH32_V1","method":key,
        "outer_tuning_contract":{"outer_tuned":["w","c1","c2","vmax_frac"],"outer_pso_population":OUTER_PSO_POP,"outer_pso_iterations":OUTER_PSO_ITERS,"tlbo_population":TLBO_POP,"tlbo_iterations":TLBO_ITERS,"de_population":DE_POP,"de_iterations":DE_ITERS,"final_population":FINAL_POP,"final_iterations":FINAL_ITERS,"refit_iterations":REFIT_ITERS,"repeats":REPEATS},
        "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE","random_validation":"NONE","target_month_in_fitness":False,"selection_period":f"{DEV_START}..{DEV_END}","2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION","authority_invariants_before":bundle.invariants_before,"authority_invariants_after":after},
        "dev":{"metrics":common.elmfis.active_metrics(dev),"yearly":common.elmfis.yearly(dev),"rows":dev},
        "transport_2025":{"metrics":common.elmfis.active_metrics(tr),"rows":tr},
        "stress_2026":{"metrics":common.elmfis.active_metrics(st),"rows":st},
    }
    p=Path(f"vw_midas_elmfis_stage3_batch32_v1_{args.outer.lower()}_tuned_pso_result.json")
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"method":key,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))

if __name__=="__main__":
    main()
