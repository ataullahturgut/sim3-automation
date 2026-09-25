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
POP=24
SELECT_ITERS=35
REFIT_ITERS=15
REPEATS=3
MIN_VAL=6

CROW_LO=np.array([0.02,0.05,0.0,0.2,0,0],float)
CROW_HI=np.array([0.8,3.0,1.0,3.0,2,2],float)
HYB_LO=np.array([0.2,0.2,0.2,0.05,0.0,0.0,0,0],float)
HYB_HI=np.array([0.95,3.0,3.0,0.8,1.0,2.0,2,2],float)

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
    if s<24:
        raise RuntimeError(f"INNER_TRAIN_TOO_SMALL n={len(X)} split={s}")
    return X[:s],Y[:s],X[s:],Y[s:]

def init_pop(rng,h,center=None):
    d=dim(h)
    if center is None:
        return rng.uniform(LO,HI,(POP,d))
    P=np.clip(np.asarray(center)[None,:]+rng.normal(0,.18,(POP,d)),LO,HI)
    P[0]=np.asarray(center)
    return P

def unpack_crow(q):
    q=np.clip(np.asarray(q,float),CROW_LO,CROW_HI)
    ap0=float(q[0]); fl0=float(q[1]); aps=float(q[2]); fld=float(q[3])
    h=HIDDEN_GRID[int(round(float(q[4])))]
    wd=WD_GRID[int(round(float(q[5])))]
    return ap0,fl0,aps,fld,h,wd

def run_crow(X,Y,q,seed,iters,center=None):
    ap0,fl0,aps,fld,h,wd=unpack_crow(q)
    rng=np.random.default_rng(seed)
    P=init_pop(rng,h,center); M=P.copy()
    F=np.array([train_obj(z,X,Y,h,wd) for z in P]); MF=F.copy()
    for t in range(iters):
        tau=t/max(1,iters-1)
        ap=np.clip(ap0+aps*tau,0.01,0.95)
        fl=max(0.02,fl0*(1-tau)**(1/max(fld,1e-8)))
        NP=P.copy()
        for i in range(POP):
            j=i
            while j==i:
                j=int(rng.integers(0,POP))
            if rng.random()>=ap:
                cand=P[i]+fl*rng.random(dim(h))*(M[j]-P[i])
            else:
                cand=rng.uniform(LO,HI,dim(h))
            NP[i]=np.clip(cand,LO,HI)
        NF=np.array([train_obj(z,X,Y,h,wd) for z in NP])
        improve=NF<F
        P[improve]=NP[improve]; F[improve]=NF[improve]
        mem=F<MF
        M[mem]=P[mem]; MF[mem]=F[mem]
    i=int(np.argmin(MF))
    return M[i].copy(),float(MF[i]),h,wd,(ap0,fl0,aps,fld)

def crow_outer_score(q,Xtr,Ytr,Xv,Yv,seed):
    vals=[]
    for rep in range(2):
        th,_,h,_,_=run_crow(Xtr,Ytr,q,seed+97*rep,SELECT_ITERS)
        vals.append(mae_loss(th,Xv,Yv,h))
    return float(np.mean(vals))

def tune_crow(Xtr,Ytr,Xv,Yv,seed):
    rng=np.random.default_rng(seed)
    cand=[]
    for _ in range(6):
        q=rng.uniform(CROW_LO,CROW_HI)
        cand.append((crow_outer_score(q,Xtr,Ytr,Xv,Yv,seed+1000+len(cand)),q))
    cand.sort(key=lambda z:z[0])
    bestf,best=float(cand[0][0]),cand[0][1].copy()
    trace=[{"stage":"random","score":float(f)} for f,_ in cand]
    for it in range(2):
        for k in range(4):
            scale=(CROW_HI-CROW_LO)*(.18/(it+1))
            q=np.clip(best+rng.normal(0,1,6)*scale,CROW_LO,CROW_HI)
            f=crow_outer_score(q,Xtr,Ytr,Xv,Yv,seed+10000+it*100+k)
            trace.append({"stage":f"local_{it}","score":float(f)})
            if f<bestf:
                bestf,best=float(f),q.copy()
    return best,bestf,trace

def unpack_hybrid(q):
    q=np.clip(np.asarray(q,float),HYB_LO,HYB_HI)
    w,c1,c2,vf,mix,tg=[float(x) for x in q[:6]]
    h=HIDDEN_GRID[int(round(float(q[6])))]
    wd=WD_GRID[int(round(float(q[7])))]
    return w,c1,c2,vf,mix,tg,h,wd

def run_hybrid(X,Y,q,seed,iters,center=None):
    w,c1,c2,vf,mix,tg,h,wd=unpack_hybrid(q)
    rng=np.random.default_rng(seed)
    P=init_pop(rng,h,center); V=np.zeros_like(P)
    F=np.array([train_obj(z,X,Y,h,wd) for z in P])
    PB=P.copy(); PF=F.copy()
    gi=int(np.argmin(PF)); GB=PB[gi].copy(); GF=float(PF[gi])
    vmax=vf*(HI-LO)
    for t in range(iters):
        tau=t/max(1,iters-1)
        teacher=P[int(np.argmin(F))].copy(); mean=P.mean(0)
        tf=1 if tau<.5 else 2
        for i in range(POP):
            r1=rng.random(dim(h)); r2=rng.random(dim(h))
            V[i]=np.clip(w*V[i]+c1*r1*(PB[i]-P[i])+c2*r2*(GB-P[i]),-vmax,vmax)
            pso=np.clip(P[i]+V[i],LO,HI)
            tlbo=np.clip(P[i]+tg*rng.random(dim(h))*(teacher-tf*mean),LO,HI)
            cand=np.clip((1-mix)*pso+mix*tlbo,LO,HI)
            cf=train_obj(cand,X,Y,h,wd)
            if cf<F[i]:
                P[i]=cand; F[i]=cf
            if F[i]<PF[i]:
                PB[i]=P[i].copy(); PF[i]=F[i]
                if F[i]<GF:
                    GB=P[i].copy(); GF=float(F[i])
        for i in range(POP):
            j=i
            while j==i:
                j=int(rng.integers(0,POP))
            direction=P[i]-P[j] if F[i]<F[j] else P[j]-P[i]
            cand=np.clip(P[i]+mix*tg*rng.random(dim(h))*direction,LO,HI)
            cf=train_obj(cand,X,Y,h,wd)
            if cf<F[i]:
                P[i]=cand; F[i]=cf
                if cf<PF[i]:
                    PB[i]=cand.copy(); PF[i]=cf
                    if cf<GF:
                        GB=cand.copy(); GF=float(cf)
    return GB,GF,h,wd,(w,c1,c2,vf,mix,tg)

def hybrid_outer_score(q,Xtr,Ytr,Xv,Yv,seed):
    vals=[]
    for rep in range(2):
        th,_,h,_,_=run_hybrid(Xtr,Ytr,q,seed+97*rep,SELECT_ITERS)
        vals.append(mae_loss(th,Xv,Yv,h))
    return float(np.mean(vals))

def tune_hybrid(Xtr,Ytr,Xv,Yv,seed):
    rng=np.random.default_rng(seed)
    cand=[]
    for _ in range(4):
        q=rng.uniform(HYB_LO,HYB_HI)
        cand.append((hybrid_outer_score(q,Xtr,Ytr,Xv,Yv,seed+1000+len(cand)),q))
    cand.sort(key=lambda z:z[0])
    bestf,best=float(cand[0][0]),cand[0][1].copy()
    trace=[{"stage":"random","score":float(f)} for f,_ in cand]
    for k in range(3):
        scale=(HYB_HI-HYB_LO)*.16
        q=np.clip(best+rng.normal(0,1,8)*scale,HYB_LO,HYB_HI)
        f=hybrid_outer_score(q,Xtr,Ytr,Xv,Yv,seed+10000+k)
        trace.append({"stage":"local","score":float(f)})
        if f<bestf:
            bestf,best=float(f),q.copy()
    return best,bestf,trace

def select_and_refit(X,Y,target,method):
    Xtr,Ytr,Xv,Yv=split_xy(X,Y)
    seed0=(807110 if method=="ADAPTIVE_CROW" else 907110)+sum(map(ord,target))
    if method=="ADAPTIVE_CROW":
        q,outer,trace=tune_crow(Xtr,Ytr,Xv,Yv,seed0)
        runner=run_crow
    else:
        q,outer,trace=tune_hybrid(Xtr,Ytr,Xv,Yv,seed0)
        runner=run_hybrid

    reps=[]; best=None
    for rep in range(REPEATS):
        th,trfit,h,wd,p=runner(Xtr,Ytr,q,seed0+500000+97*rep,SELECT_ITERS)
        val=mae_loss(th,Xv,Yv,h)
        row=(val,th,trfit,h,wd,p,rep)
        reps.append(row)
        if best is None or val<best[0]:
            best=row
    val,th,trfit,h,wd,p,rep=best
    final,full,h2,wd2,p2=runner(X,Y,q,seed0+900001+97*rep,REFIT_ITERS,center=th)

    meta={
        "outer_validation_score":float(outer),
        "outer_trace":trace,
        "selected_hidden":int(h2),
        "selected_weight_decay":float(wd2),
        "selected_repeat":int(rep),
        "inner_validation_fitness":float(val),
        "full_history_refit_objective":float(full),
        "repeat_validation":[
            {"repeat":int(z[6]),"inner_validation_fitness":float(z[0]),"inner_train_objective":float(z[2])}
            for z in reps
        ],
    }
    if method=="ADAPTIVE_CROW":
        meta["selected_crow"]={"ap0":float(p2[0]),"flight0":float(p2[1]),"ap_slope":float(p2[2]),"flight_decay":float(p2[3])}
    else:
        meta["selected_hybrid"]={"w":float(p2[0]),"c1":float(p2[1]),"c2":float(p2[2]),"vmax_frac":float(p2[3]),"mix":float(p2[4]),"tlbo_gain":float(p2[5])}
    return final,meta,h2

def predict_target(samples,target,method):
    keys,X,Y,tx,ym,ys,split=common.arrays(samples,target)
    th,meta,h=select_and_refit(X,Y,target,method)
    pred=predict_std(th,tx,h)[0]*ys+ym
    return pred,len(keys),meta

def evaluate(bundle,cache,method,start,end):
    rows=[]
    for target in base.month_range(start,end):
        pred,n,meta=predict_target(cache[target],target,method)
        origin=base.month_shift(target,-1)
        rows.append({
            "target":target,"origin":origin,"method":method,"train_rows":n,**meta,
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
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    results={}
    for method in ("ADAPTIVE_CROW","PSO_TLBO_HYBRID"):
        dev=evaluate(bundle,cache,method,DEV_START,DEV_END)
        tr=evaluate(bundle,cache,method,TR_START,TR_END)
        st=evaluate(bundle,cache,method,ST_START,ST_END)
        results[method]={
            "dev":{"metrics":base.metrics(dev),"yearly":base.yearly(dev),"rows":dev},
            "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
            "stress_2026":{"metrics":base.metrics(st),"rows":st},
        }

    after=read_invariants(dsn)
    if after!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out={
        "batch_id":"VW_MIDAS_ANN_STAGE3_BATCH33_V1",
        "method":{
            "ann":"direct all-weight optimization, tanh hidden, linear 4-output",
            "hidden_grid":HIDDEN_GRID,
            "weight_decay_grid":WD_GRID,
            "population":POP,
            "selection_iterations":SELECT_ITERS,
            "refit_iterations":REFIT_ITERS,
            "repeats":REPEATS,
            "adaptive_crow_tuned":["ap0","flight0","ap_slope","flight_decay","hidden","weight_decay"],
            "pso_tlbo_tuned":["w","c1","c2","vmax_frac","mix","tlbo_gain","hidden","weight_decay"],
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
    Path("vw_midas_ann_stage3_batch33_v1_result.json").write_text(
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
