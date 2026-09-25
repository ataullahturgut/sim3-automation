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
POP=24
SELECT_ITERS=35
REFIT_ITERS=15
REPEATS=3
MIN_VAL=6

CROW_LO=np.array([0.02,0.05,0.0,0.2],float)
CROW_HI=np.array([0.8,3.0,1.0,3.0],float)
HYB_LO=np.array([0.2,0.2,0.2,0.05,0.0,0.0],float)
HYB_HI=np.array([0.95,3.0,3.0,0.8,1.0,2.0],float)

def split_xy(X,Y):
    nv=max(MIN_VAL,int(round(.2*len(X))))
    s=len(X)-nv
    if s<24: raise RuntimeError(f"INNER_TRAIN_TOO_SMALL n={len(X)} split={s}")
    return X[:s],Y[:s],X[s:],Y[s:]

def train_obj(theta,X,Y):
    return common.training_loss(theta,X,Y)

def val_obj(theta,Xtr,Ytr,Xv,Yv):
    return common.validation_loss(theta,Xtr,Ytr,Xv,Yv)

def init_pop(rng,center,refit=False):
    return common.init_population(rng,center,refit=refit)

def run_crow(X,Y,q,seed,iters,center,refit=False):
    ap0,fl0,aps,fld=np.clip(np.asarray(q,float),CROW_LO,CROW_HI)
    rng=np.random.default_rng(seed)
    P=init_pop(rng,center,refit); M=P.copy()
    F=np.array([train_obj(z,X,Y) for z in P]); MF=F.copy()
    for t in range(iters):
        tau=t/max(1,iters-1)
        ap=np.clip(float(ap0)+float(aps)*tau,0.01,0.95)
        fl=max(0.02,float(fl0)*(1-tau)**(1/max(float(fld),1e-8)))
        NP=P.copy()
        for i in range(POP):
            j=i
            while j==i: j=int(rng.integers(0,POP))
            if rng.random()>=ap:
                cand=P[i]+fl*rng.random(common.PARAM_DIM)*(M[j]-P[i])
            else:
                cand=rng.uniform(LO,HI,common.PARAM_DIM)
            NP[i]=np.clip(cand,LO,HI)
        NF=np.array([train_obj(z,X,Y) for z in NP])
        improve=NF<F
        P[improve]=NP[improve]; F[improve]=NF[improve]
        mem=F<MF
        M[mem]=P[mem]; MF[mem]=F[mem]
    i=int(np.argmin(MF))
    return M[i].copy(),float(MF[i])

def crow_outer_score(q,Xtr,Ytr,Xv,Yv,seed,anchor):
    vals=[]
    for rep in range(2):
        th,_=run_crow(Xtr,Ytr,q,seed+97*rep,20,anchor,False)
        vals.append(val_obj(th,Xtr,Ytr,Xv,Yv))
    return float(np.mean(vals))

def tune_crow(Xtr,Ytr,Xv,Yv,seed,anchor):
    rng=np.random.default_rng(seed)
    cand=[]
    for _ in range(6):
        q=rng.uniform(CROW_LO,CROW_HI)
        cand.append((crow_outer_score(q,Xtr,Ytr,Xv,Yv,seed+1000+len(cand),anchor),q.copy()))
    cand.sort(key=lambda z:z[0])
    bestf,best=float(cand[0][0]),cand[0][1].copy()
    trace=[{"stage":"random","score":float(f)} for f,_ in cand]
    for it in range(2):
        for k in range(4):
            q=np.clip(best+rng.normal(0,1,4)*(CROW_HI-CROW_LO)*(.18/(it+1)),CROW_LO,CROW_HI)
            f=crow_outer_score(q,Xtr,Ytr,Xv,Yv,seed+10000+it*100+k,anchor)
            trace.append({"stage":f"local_{it}","score":float(f)})
            if f<bestf: bestf,best=float(f),q.copy()
    return best,bestf,trace

def run_hybrid(X,Y,q,seed,iters,center,refit=False):
    w,c1,c2,vf,mix,tg=np.clip(np.asarray(q,float),HYB_LO,HYB_HI)
    rng=np.random.default_rng(seed)
    P=init_pop(rng,center,refit); V=np.zeros_like(P)
    F=np.array([train_obj(z,X,Y) for z in P])
    PB=P.copy(); PF=F.copy()
    gi=int(np.argmin(PF)); GB=PB[gi].copy(); GF=float(PF[gi])
    vmax=float(vf)*SPAN
    for t in range(iters):
        tau=t/max(1,iters-1)
        teacher=P[int(np.argmin(F))].copy(); mean=P.mean(0)
        tf=1 if tau<.5 else 2
        for i in range(POP):
            r1=rng.random(common.PARAM_DIM); r2=rng.random(common.PARAM_DIM)
            V[i]=np.clip(float(w)*V[i]+float(c1)*r1*(PB[i]-P[i])+float(c2)*r2*(GB-P[i]),-vmax,vmax)
            pso=np.clip(P[i]+V[i],LO,HI)
            tlbo=np.clip(P[i]+float(tg)*rng.random(common.PARAM_DIM)*(teacher-tf*mean),LO,HI)
            cand=np.clip((1-float(mix))*pso+float(mix)*tlbo,LO,HI)
            cf=train_obj(cand,X,Y)
            if cf<F[i]: P[i]=cand; F[i]=cf
            if F[i]<PF[i]:
                PB[i]=P[i].copy(); PF[i]=F[i]
                if F[i]<GF: GB=P[i].copy(); GF=float(F[i])
        for i in range(POP):
            j=i
            while j==i: j=int(rng.integers(0,POP))
            direction=P[i]-P[j] if F[i]<F[j] else P[j]-P[i]
            cand=np.clip(P[i]+float(mix)*float(tg)*rng.random(common.PARAM_DIM)*direction,LO,HI)
            cf=train_obj(cand,X,Y)
            if cf<F[i]:
                P[i]=cand; F[i]=cf
                if cf<PF[i]:
                    PB[i]=cand.copy(); PF[i]=cf
                    if cf<GF: GB=cand.copy(); GF=float(cf)
    return GB,GF

def hybrid_outer_score(q,Xtr,Ytr,Xv,Yv,seed,anchor):
    vals=[]
    for rep in range(2):
        th,_=run_hybrid(Xtr,Ytr,q,seed+97*rep,20,anchor,False)
        vals.append(val_obj(th,Xtr,Ytr,Xv,Yv))
    return float(np.mean(vals))

def tune_hybrid(Xtr,Ytr,Xv,Yv,seed,anchor):
    rng=np.random.default_rng(seed)
    cand=[]
    for _ in range(4):
        q=rng.uniform(HYB_LO,HYB_HI)
        cand.append((hybrid_outer_score(q,Xtr,Ytr,Xv,Yv,seed+1000+len(cand),anchor),q.copy()))
    cand.sort(key=lambda z:z[0])
    bestf,best=float(cand[0][0]),cand[0][1].copy()
    trace=[{"stage":"random","score":float(f)} for f,_ in cand]
    for k in range(4):
        q=np.clip(best+rng.normal(0,1,6)*(HYB_HI-HYB_LO)*.16,HYB_LO,HYB_HI)
        f=hybrid_outer_score(q,Xtr,Ytr,Xv,Yv,seed+10000+k,anchor)
        trace.append({"stage":"local","score":float(f)})
        if f<bestf: bestf,best=float(f),q.copy()
    return best,bestf,trace

def select_and_refit(X,Y,target,method):
    Xtr,Ytr,Xv,Yv=split_xy(X,Y)
    anchor=common.initial_theta(Xtr)
    seed0=(807110 if method=="ADAPTIVE_CROW" else 907110)+sum(map(ord,target))
    if method=="ADAPTIVE_CROW":
        q,outer,trace=tune_crow(Xtr,Ytr,Xv,Yv,seed0,anchor)
        runner=run_crow
    else:
        q,outer,trace=tune_hybrid(Xtr,Ytr,Xv,Yv,seed0,anchor)
        runner=run_hybrid
    reps=[]; best=None
    for rep in range(REPEATS):
        th,trfit=runner(Xtr,Ytr,q,seed0+500000+97*rep,SELECT_ITERS,anchor,False)
        val=val_obj(th,Xtr,Ytr,Xv,Yv)
        row=(val,th,trfit,rep)
        reps.append(row)
        if best is None or val<best[0]: best=row
    val,th,trfit,rep=best
    final,full=runner(X,Y,q,seed0+900001+97*rep,REFIT_ITERS,th,True)
    meta={
        "outer_validation_score":float(outer),
        "outer_trace":trace,
        "selected_repeat":int(rep),
        "inner_validation_fitness":float(val),
        "full_history_refit_objective":float(full),
        "repeat_validation":[{"repeat":int(z[3]),"inner_validation_fitness":float(z[0]),"inner_train_objective":float(z[2])} for z in reps],
    }
    if method=="ADAPTIVE_CROW":
        meta["selected_crow"]={"ap0":float(q[0]),"flight0":float(q[1]),"ap_slope":float(q[2]),"flight_decay":float(q[3])}
    else:
        meta["selected_hybrid"]={"w":float(q[0]),"c1":float(q[1]),"c2":float(q[2]),"vmax_frac":float(q[3]),"mix":float(q[4]),"tlbo_gain":float(q[5])}
    return final,meta

def predict_target(samples,target,method):
    keys,X,Y,tx,ym,ys,split=common.arrays(samples,target)
    th,meta=select_and_refit(X,Y,target,method)
    pred_std=common.predict_with_fit(th,X,Y,tx)[0]
    return pred_std*ys+ym,len(keys),meta

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
    parser=argparse.ArgumentParser()
    parser.add_argument("--method",required=True,choices=["ADAPTIVE_CROW","PSO_TLBO_HYBRID"])
    args=parser.parse_args()
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    dev=evaluate(bundle,cache,args.method,DEV_START,DEV_END)
    tr=evaluate(bundle,cache,args.method,TR_START,TR_END)
    st=evaluate(bundle,cache,args.method,ST_START,ST_END)
    after=read_invariants(dsn)
    if after!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={
        "batch_id":"VW_MIDAS_ELMFIS_STAGE3_BATCH33_V1","method":args.method,
        "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE","random_validation":"NONE","target_month_in_fitness":False,"selection_period":f"{DEV_START}..{DEV_END}","2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION","authority_invariants_before":bundle.invariants_before,"authority_invariants_after":after},
        "dev":{"metrics":common.elmfis.active_metrics(dev),"yearly":common.elmfis.yearly(dev),"rows":dev},
        "transport_2025":{"metrics":common.elmfis.active_metrics(tr),"rows":tr},
        "stress_2026":{"metrics":common.elmfis.active_metrics(st),"rows":st},
    }
    p=Path(f"vw_midas_elmfis_stage3_batch33_v1_{args.method.lower()}_result.json")
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"method":args.method,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))

if __name__=="__main__":
    main()
