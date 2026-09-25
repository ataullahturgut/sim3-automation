from __future__ import annotations

import json, math, os
from pathlib import Path
import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import vw_midas_ann_meta_batch_1_v1 as common

DEV_START,DEV_END=common.DEV_START,common.DEV_END
TR_START,TR_END=common.TR_START,common.TR_END
ST_START,ST_END=common.ST_START,common.ST_END

HIDDEN_GRID=[3,4,6]
WD_GRID=[0.0,1e-4,1e-3]
LO,HI=-2.0,2.0

# Outer tuner follows the original ELM meta-on-meta budget class.
OUTER_PSO_POP=12
OUTER_PSO_ITERS=20
TLBO_POP=6
TLBO_ITERS=5
DE_POP=8
DE_ITERS=6

# Final selected PSO is re-evaluated more robustly.
FINAL_POP=24
FINAL_ITERS=45
REFIT_ITERS=15
REPEATS=3
MIN_VAL=6

QLO=np.array([.2,.2,.2,.05,0,0],float)
QHI=np.array([.95,3.0,3.0,.8,2,2],float)

def dim(h): return 13*h+4

def decode(theta,h):
    i=0
    W1=theta[i:i+8*h].reshape(8,h); i+=8*h
    b1=theta[i:i+h]; i+=h
    W2=theta[i:i+4*h].reshape(h,4); i+=4*h
    b2=theta[i:i+4]
    return W1,b1,W2,b2

def predict_std(theta,X,h):
    W1,b1,W2,b2=decode(theta,h)
    return np.tanh(X@W1+b1)@W2+b2

def mae_loss(theta,X,Y,h):
    p=predict_std(theta,X,h)
    return float(.7*np.mean(np.abs(p[:,0]-Y[:,0]))+.3*np.mean(np.abs(p-Y)))

def train_obj(theta,X,Y,h,wd):
    return mae_loss(theta,X,Y,h)+float(wd)*float(np.mean(np.asarray(theta)**2))

def split_xy(X,Y):
    nv=max(MIN_VAL,int(round(.2*len(X))))
    s=len(X)-nv
    if s<24: raise RuntimeError(f"INNER_TRAIN_TOO_SMALL n={len(X)} split={s}")
    return X[:s],Y[:s],X[s:],Y[s:]

def parse_q(q):
    q=np.clip(np.asarray(q,float),QLO,QHI)
    w,c1,c2,vf=[float(x) for x in q[:4]]
    h=HIDDEN_GRID[int(round(float(q[4])))]
    wd=WD_GRID[int(round(float(q[5])))]
    return (w,c1,c2,vf),h,wd

def init_pop(rng,h,pop,center=None):
    d=dim(h)
    if center is None:
        return rng.uniform(LO,HI,(pop,d))
    X=np.clip(np.asarray(center)[None,:]+rng.normal(0,.18,(pop,d)),LO,HI)
    X[0]=np.asarray(center)
    return X

def pso_train(X,Y,q,seed,pop,iters,center=None):
    (w,c1,c2,vf),h,wd=parse_q(q)
    rng=np.random.default_rng(seed)
    x=init_pop(rng,h,pop,center)
    v=np.zeros_like(x)
    fit=np.array([train_obj(z,X,Y,h,wd) for z in x])
    pb=x.copy(); pf=fit.copy()
    gi=int(np.argmin(pf)); gb=pb[gi].copy(); gf=float(pf[gi])
    vmax=vf*(HI-LO)
    for _ in range(iters):
        for i in range(pop):
            r1=rng.random(dim(h)); r2=rng.random(dim(h))
            v[i]=np.clip(w*v[i]+c1*r1*(pb[i]-x[i])+c2*r2*(gb-x[i]),-vmax,vmax)
            x[i]=np.clip(x[i]+v[i],LO,HI)
            cf=train_obj(x[i],X,Y,h,wd)
            if cf<pf[i]:
                pb[i]=x[i].copy(); pf[i]=cf
                if cf<gf:
                    gb=x[i].copy(); gf=float(cf)
    return gb,gf,h,wd,(w,c1,c2,vf)

def outer_score(q,Xtr,Ytr,Xv,Yv,seed):
    vals=[]
    for rep in range(2):
        theta,_,h,_,_=pso_train(Xtr,Ytr,q,seed+97*rep,OUTER_PSO_POP,OUTER_PSO_ITERS)
        vals.append(mae_loss(theta,Xv,Yv,h))
    return float(np.mean(vals))

def tlbo_tune(Xtr,Ytr,Xv,Yv,seed):
    rng=np.random.default_rng(seed)
    P=rng.uniform(QLO,QHI,(TLBO_POP,6))
    F=np.array([outer_score(q,Xtr,Ytr,Xv,Yv,seed+1000+i) for i,q in enumerate(P)])
    trace=[]
    for g in range(TLBO_ITERS):
        teacher=P[int(np.argmin(F))].copy(); mean=P.mean(0)
        tf=int(rng.integers(1,3))
        for i in range(TLBO_POP):
            q=np.clip(P[i]+rng.random(6)*(teacher-tf*mean),QLO,QHI)
            f=outer_score(q,Xtr,Ytr,Xv,Yv,seed+10000+g*100+i)
            if f<F[i]: P[i]=q; F[i]=f
        for i in range(TLBO_POP):
            j=i
            while j==i: j=int(rng.integers(0,TLBO_POP))
            direction=P[i]-P[j] if F[i]<F[j] else P[j]-P[i]
            q=np.clip(P[i]+rng.random(6)*direction,QLO,QHI)
            f=outer_score(q,Xtr,Ytr,Xv,Yv,seed+20000+g*100+i)
            if f<F[i]: P[i]=q; F[i]=f
        trace.append({"iteration":g,"best_outer_validation":float(np.min(F))})
    i=int(np.argmin(F))
    return P[i].copy(),float(F[i]),trace

def de_tune(Xtr,Ytr,Xv,Yv,seed):
    rng=np.random.default_rng(seed)
    P=rng.uniform(QLO,QHI,(DE_POP,6))
    F=np.array([outer_score(q,Xtr,Ytr,Xv,Yv,seed+1000+i) for i,q in enumerate(P)])
    trace=[]
    for g in range(DE_ITERS):
        for i in range(DE_POP):
            pool=[j for j in range(DE_POP) if j!=i]
            a,b,c=rng.choice(pool,3,replace=False)
            mutant=np.clip(P[a]+.7*(P[b]-P[c]),QLO,QHI)
            mask=rng.random(6)<.9
            mask[rng.integers(0,6)]=True
            q=np.where(mask,mutant,P[i])
            f=outer_score(q,Xtr,Ytr,Xv,Yv,seed+10000+g*100+i)
            if f<F[i]: P[i]=q; F[i]=f
        trace.append({"iteration":g,"best_outer_validation":float(np.min(F))})
    i=int(np.argmin(F))
    return P[i].copy(),float(F[i]),trace

def select_and_refit(X,Y,target,outer):
    Xtr,Ytr,Xv,Yv=split_xy(X,Y)
    seed0=(507110 if outer=="TLBO" else 607110)+sum(map(ord,target))
    if outer=="TLBO":
        q,outer_val,trace=tlbo_tune(Xtr,Ytr,Xv,Yv,seed0)
    else:
        q,outer_val,trace=de_tune(Xtr,Ytr,Xv,Yv,seed0)

    reps=[]
    best=None
    for rep in range(REPEATS):
        theta,trfit,h,wd,p=pso_train(
            Xtr,Ytr,q,seed0+500000+97*rep,FINAL_POP,FINAL_ITERS
        )
        val=mae_loss(theta,Xv,Yv,h)
        row=(val,theta,trfit,h,wd,p,rep)
        reps.append(row)
        if best is None or val<best[0]: best=row

    val,theta,trfit,h,wd,p,rep=best
    final,full,h2,wd2,p2=pso_train(
        X,Y,q,seed0+900001+97*rep,FINAL_POP,REFIT_ITERS,center=theta
    )
    return final,{
        "outer_optimizer":outer,
        "outer_validation_score":float(outer_val),
        "outer_trace":trace,
        "selected_hidden":int(h2),
        "selected_weight_decay":float(wd2),
        "selected_repeat":int(rep),
        "selected_pso":{"w":float(p2[0]),"c1":float(p2[1]),"c2":float(p2[2]),"vmax_frac":float(p2[3])},
        "inner_validation_fitness":float(val),
        "full_history_refit_objective":float(full),
        "repeat_validation":[
            {"repeat":int(z[6]),"inner_validation_fitness":float(z[0]),"inner_train_objective":float(z[2])}
            for z in reps
        ],
    },h2

def predict_target(samples,target,outer):
    keys,X,Y,tx,ym,ys,split=common.arrays(samples,target)
    theta,meta,h=select_and_refit(X,Y,target,outer)
    pred=predict_std(theta,tx,h)[0]*ys+ym
    return pred,len(keys),meta

def evaluate(bundle,cache,outer,start,end):
    rows=[]
    for target in base.month_range(start,end):
        pred,n,meta=predict_target(cache[target],target,outer)
        origin=base.month_shift(target,-1)
        rows.append({
            "target":target,"origin":origin,"method":f"{outer}_TUNED_PSO",
            "train_rows":n,**meta,
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
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in base.month_range(DEV_START,ST_END)}

    results={}
    for outer in ("TLBO","DE"):
        dev=evaluate(bundle,cache,outer,DEV_START,DEV_END)
        tr=evaluate(bundle,cache,outer,TR_START,TR_END)
        st=evaluate(bundle,cache,outer,ST_START,ST_END)
        key=f"{outer}_TUNED_PSO"
        results[key]={
            "dev":{"metrics":base.metrics(dev),"yearly":base.yearly(dev),"rows":dev},
            "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
            "stress_2026":{"metrics":base.metrics(st),"rows":st},
        }

    after=read_invariants(dsn)
    if after!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out={
        "batch_id":"VW_MIDAS_ANN_STAGE3_BATCH32_V1",
        "method":{
            "ann":"direct all-weight optimization, tanh hidden, linear 4-output",
            "outer_tuned":["w","c1","c2","vmax_frac","hidden","weight_decay"],
            "hidden_grid":HIDDEN_GRID,
            "weight_decay_grid":WD_GRID,
            "outer_pso_population":OUTER_PSO_POP,
            "outer_pso_iterations":OUTER_PSO_ITERS,
            "tlbo_population":TLBO_POP,
            "tlbo_iterations":TLBO_ITERS,
            "de_population":DE_POP,
            "de_iterations":DE_ITERS,
            "final_pso_population":FINAL_POP,
            "final_pso_iterations":FINAL_ITERS,
            "refit_iterations":REFIT_ITERS,
            "final_repeats":REPEATS,
        },
        "authority":{
            "database_access":"READ_ONLY",
            "feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
            "random_validation":"NONE",
            "target_month_in_fitness":False,
            "outer_tuning":"chronological final 20pct of pre-target training only",
            "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
            "authority_invariants_before":bundle.invariants_before,
            "authority_invariants_after":after,
        },
        "models":results,
    }
    Path("vw_midas_ann_stage3_batch32_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps({
        k:{
            "dev":v["dev"]["metrics"],
            "transport_2025":v["transport_2025"]["metrics"],
            "stress_2026":v["stress_2026"]["metrics"],
        } for k,v in results.items()
    },sort_keys=True))

if __name__=="__main__":
    main()
