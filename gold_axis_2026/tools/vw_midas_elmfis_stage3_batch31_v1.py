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

POP=common.POP_SIZE
SELECT_GENS=45
REFIT_GENS=15
REPEATS=3
MIN_VAL=6
LO,HI=common.LOWER,common.UPPER
SPAN=HI-LO

def split_xy(X,Y):
    nv=max(MIN_VAL,int(round(.2*len(X))))
    s=len(X)-nv
    if s<24:
        raise RuntimeError(f"INNER_TRAIN_TOO_SMALL n={len(X)} split={s}")
    return X[:s],Y[:s],X[s:],Y[s:]

def init_pop(rng,center=None,refit=False):
    if center is None:
        center=common.initial_theta(np.zeros((30,common.INPUTS)))
    return common.init_population(rng,center,refit=refit)

def train_obj(theta,X,Y):
    return common.training_loss(theta,X,Y)

def val_obj(theta,Xtr,Ytr,Xv,Yv):
    return common.validation_loss(theta,Xtr,Ytr,Xv,Yv)

def adaptive_pso_run(X,Y,seed,gens,center,refit=False):
    rng=np.random.default_rng(seed)
    P=common.init_population(rng,center,refit=refit)
    V=np.zeros_like(P)
    F=np.array([train_obj(z,X,Y) for z in P])
    PB=P.copy(); PF=F.copy()
    gi=int(np.argmin(PF)); GB=PB[gi].copy(); GF=float(PF[gi])
    vmax=.18*SPAN
    for t in range(gens):
        tau=t/max(1,gens-1)
        w=.90-.50*tau
        c1=2.50-2.00*tau
        c2=.50+2.00*tau
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

def adaptive_pso_select(X,Y,target):
    Xtr,Ytr,Xv,Yv=split_xy(X,Y)
    anchor=common.initial_theta(Xtr)
    seed0=407110+sum(map(ord,target))
    rows=[]; best=None
    for rep in range(REPEATS):
        seed=seed0+97*rep
        th,trfit=adaptive_pso_run(Xtr,Ytr,seed,SELECT_GENS,anchor,False)
        val=val_obj(th,Xtr,Ytr,Xv,Yv)
        rows.append({"repeat":rep,"seed":seed,"inner_train_objective":float(trfit),"inner_validation_fitness":float(val)})
        cand=(val,th,trfit,rep)
        if best is None or val<best[0]: best=cand
    val,th,trfit,rep=best
    final,full=adaptive_pso_run(X,Y,seed0+900001+97*rep,REFIT_GENS,th,True)
    return final,{
        "selected_repeat":int(rep),
        "inner_validation_fitness":float(val),
        "full_history_refit_objective":float(full),
        "repeat_validation":rows,
        "schedule":{"w":"0.90_to_0.40","c1":"2.50_to_0.50","c2":"0.50_to_2.50","vmax_frac":0.18},
    }

QLO=np.array([.3,.2,0,.5],float)
QHI=np.array([1.8,1.8,1,3],float)

def itlbo_run(X,Y,q,seed,gens,center,refit=False):
    tg,lg,tfp,decay=np.clip(np.asarray(q,float),QLO,QHI)
    rng=np.random.default_rng(seed)
    P=common.init_population(rng,center,refit=refit)
    F=np.array([train_obj(z,X,Y) for z in P])
    for t in range(gens):
        tau=t/max(1,gens-1)
        local_tg=float(tg)*(1-tau)**(1/max(float(decay),1e-8))+.1
        local_lg=float(lg)*(.5+.5*(1-tau))
        teacher=P[int(np.argmin(F))].copy(); mean=P.mean(0)
        tf=2 if rng.random()<float(tfp) else 1
        for i in range(POP):
            cand=np.clip(P[i]+local_tg*rng.random(common.PARAM_DIM)*(teacher-tf*mean),LO,HI)
            cf=train_obj(cand,X,Y)
            if cf<F[i]: P[i]=cand; F[i]=cf
        for i in range(POP):
            j=i
            while j==i: j=int(rng.integers(0,POP))
            direction=P[i]-P[j] if F[i]<F[j] else P[j]-P[i]
            cand=np.clip(P[i]+local_lg*rng.random(common.PARAM_DIM)*direction,LO,HI)
            cf=train_obj(cand,X,Y)
            if cf<F[i]: P[i]=cand; F[i]=cf
        if (t+1)%10==0:
            best=P[int(np.argmin(F))].copy()
            for _ in range(2):
                wi=int(np.argmax(F))
                cand=np.clip(best+rng.normal(0,.04,common.PARAM_DIM)*SPAN,LO,HI)
                cf=train_obj(cand,X,Y)
                if cf<F[wi]: P[wi]=cand; F[wi]=cf
    i=int(np.argmin(F))
    return P[i].copy(),float(F[i])

def q_outer_score(q,Xtr,Ytr,Xv,Yv,seed,anchor):
    vals=[]
    for rep in range(2):
        th,_=itlbo_run(Xtr,Ytr,q,seed+97*rep,20,anchor,False)
        vals.append(val_obj(th,Xtr,Ytr,Xv,Yv))
    return float(np.mean(vals))

def tune_outer(Xtr,Ytr,Xv,Yv,seed,anchor):
    rng=np.random.default_rng(seed)
    trials=[]
    for _ in range(6):
        q=rng.uniform(QLO,QHI)
        f=q_outer_score(q,Xtr,Ytr,Xv,Yv,seed+1000+len(trials),anchor)
        trials.append((f,q.copy()))
    trials.sort(key=lambda z:z[0])
    bestf,best=float(trials[0][0]),trials[0][1].copy()
    for it in range(2):
        for k in range(4):
            q=np.clip(best+rng.normal(0,1,4)*(QHI-QLO)*(.18/(it+1)),QLO,QHI)
            f=q_outer_score(q,Xtr,Ytr,Xv,Yv,seed+10000+it*100+k,anchor)
            trials.append((f,q.copy()))
            if f<bestf: bestf,best=float(f),q.copy()
    return best,bestf,[{"score":float(f),"q":[float(v) for v in q]} for f,q in trials]

def adaptive_tlbo_select(X,Y,target):
    Xtr,Ytr,Xv,Yv=split_xy(X,Y)
    anchor=common.initial_theta(Xtr)
    seed0=707110+sum(map(ord,target))
    q,outer,trials=tune_outer(Xtr,Ytr,Xv,Yv,seed0,anchor)
    reps=[]; best=None
    for rep in range(REPEATS):
        th,trfit=itlbo_run(Xtr,Ytr,q,seed0+500000+97*rep,SELECT_GENS,anchor,False)
        val=val_obj(th,Xtr,Ytr,Xv,Yv)
        row=(val,th,trfit,rep)
        reps.append(row)
        if best is None or val<best[0]: best=row
    val,th,trfit,rep=best
    final,full=itlbo_run(X,Y,q,seed0+900001+97*rep,REFIT_GENS,th,True)
    return final,{
        "selected_repeat":int(rep),
        "outer_validation_score":float(outer),
        "selected_q":{"teacher_gain":float(q[0]),"learner_gain":float(q[1]),"tf2_probability":float(q[2]),"decay":float(q[3])},
        "outer_trials":trials,
        "inner_validation_fitness":float(val),
        "full_history_refit_objective":float(full),
        "repeat_validation":[{"repeat":int(z[3]),"inner_validation_fitness":float(z[0]),"inner_train_objective":float(z[2])} for z in reps],
    }

def predict_target(samples,target,method):
    keys,X,Y,tx,ym,ys,split=common.arrays(samples,target)
    if method=="ADAPTIVE_PSO":
        th,meta=adaptive_pso_select(X,Y,target)
    else:
        th,meta=adaptive_tlbo_select(X,Y,target)
    pred_std=common.predict_with_fit(th,X,Y,tx)[0]
    pred=pred_std*ys+ym
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
    parser=argparse.ArgumentParser()
    parser.add_argument("--method",required=True,choices=["ADAPTIVE_PSO","ADAPTIVE_TLBO"])
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
        "batch_id":"VW_MIDAS_ELMFIS_STAGE3_BATCH31_V1",
        "method":args.method,
        "canonical_elmfis":{"rules":common.RULES,"inputs":common.INPUTS,"outputs":common.OUTPUTS,"optimized_parameters":common.PARAM_DIM,"consequent_fit":"analytic_ridge_per_candidate"},
        "authority":{
            "database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE","random_validation":"NONE",
            "target_month_in_fitness":False,"selection_period":f"{DEV_START}..{DEV_END}",
            "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
            "authority_invariants_before":bundle.invariants_before,"authority_invariants_after":after,
        },
        "dev":{"metrics":common.elmfis.active_metrics(dev),"yearly":common.elmfis.yearly(dev),"rows":dev},
        "transport_2025":{"metrics":common.elmfis.active_metrics(tr),"rows":tr},
        "stress_2026":{"metrics":common.elmfis.active_metrics(st),"rows":st},
    }
    p=Path(f"vw_midas_elmfis_stage3_batch31_v1_{args.method.lower()}_result.json")
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"method":args.method,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))

if __name__=="__main__":
    main()
