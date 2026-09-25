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

POP=common.POP_SIZE
GENS=common.SELECT_GENS
REFIT=common.REFIT_GENS
REPEATS=common.REPEATS
LO,HI=common.LOWER,common.UPPER
D=common.PARAM_DIM

def levy(rng,shape,beta=1.5):
    sigma=(math.gamma(1+beta)*math.sin(math.pi*beta/2)/(math.gamma((1+beta)/2)*beta*2**((beta-1)/2)))**(1/beta)
    u=rng.normal(0,sigma,size=shape); v=rng.normal(0,1,size=shape)
    return u/(np.abs(v)**(1/beta)+1e-12)

def mpa_proposals(pop,fit,t,T,rng):
    elite=pop[int(np.argmin(fit))].copy()
    P=.5; FADs=.2
    cf=(1-(t+1)/T)**(2*(t+1)/T)
    cand=pop.copy()
    if (t+1)<=T/3:
        RB=rng.normal(0,1,size=pop.shape)
        for i in range(POP):
            step=RB[i]*(elite-RB[i]*pop[i])
            cand[i]=pop[i]+P*rng.random(D)*step
    elif (t+1)<=2*T/3:
        RL=.05*levy(rng,pop.shape); RB=rng.normal(0,1,size=pop.shape)
        half=POP//2
        for i in range(POP):
            if i<half:
                step=RL[i]*(elite-RL[i]*pop[i])
                cand[i]=pop[i]+P*rng.random(D)*step
            else:
                step=RB[i]*(RB[i]*elite-pop[i])
                cand[i]=elite+P*cf*step
    else:
        RL=.05*levy(rng,pop.shape)
        for i in range(POP):
            step=RL[i]*(RL[i]*elite-pop[i])
            cand[i]=elite+P*cf*step

    cand=np.clip(cand,LO,HI)
    if rng.random()<FADs:
        U=(rng.random(cand.shape)<FADs).astype(float)
        cand=cand+cf*(LO+rng.random(cand.shape)*(HI-LO))*U
    else:
        r=rng.random()
        i1,i2=rng.permutation(POP),rng.permutation(POP)
        cand=cand+(FADs*(1-r)+r)*(cand[i1]-cand[i2])
    return np.clip(cand,LO,HI)

def cpa_proposals(pop,fit,t,T,rng):
    # One CPA operator step per incumbent, matching the Stage-1 CPA
    # exploration/exploitation equations. Acceptance is delegated to the
    # common three-pool survivor competition, so CPA and MPA get equal proposal budgets.
    best=pop[int(np.argmin(fit))].copy()
    scale=1-t/max(1,T-1)
    out=np.empty_like(pop)
    for i in range(POP):
        j=int(rng.integers(0,POP))
        if rng.random()<.5:
            cand=pop[i]+rng.random(D)*(best-pop[i])+scale*rng.random(D)*(pop[j]-pop[i])
        else:
            cand=best+scale*rng.normal(0,1,D)*np.abs(best-pop[i])
        if rng.random()<.05:
            cand=rng.uniform(LO,HI,D)
        out[i]=np.clip(cand,LO,HI)
    return out

def hybrid_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    pop=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in pop])
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(pop,fit,Xv,Yv,vbest,vfit)

    totals={"INCUMBENT":0,"MPA":0,"CPA":0}
    trace=[]

    for t in range(generations):
        mpa=mpa_proposals(pop,fit,t,generations,rng)
        mfit=np.array([common.weighted_mae(z,X,Y) for z in mpa])

        cpa=cpa_proposals(pop,fit,t,generations,rng)
        cfit=np.array([common.weighted_mae(z,X,Y) for z in cpa])

        pool=np.vstack([pop,mpa,cpa])
        pfit=np.concatenate([fit,mfit,cfit])
        source=np.array(["INCUMBENT"]*POP+["MPA"]*POP+["CPA"]*POP,dtype=object)
        keep=np.argsort(pfit)[:POP]
        kept=source[keep]
        counts={k:int(np.sum(kept==k)) for k in totals}
        for k,v in counts.items():
            totals[k]+=v
        trace.append({"generation":t+1,**counts})

        pop=pool[keep].copy()
        fit=pfit[keep].copy()
        if Xv is not None:
            vbest,vfit=common.validation_pick(pop,fit,Xv,Yv,vbest,vfit)

    bi=int(np.argmin(fit))
    theta=vbest if Xv is not None else pop[bi].copy()
    score=vfit if Xv is not None else float(fit[bi])
    denom=max(1,generations*POP)
    shares={k:float(v/denom) for k,v in totals.items()}
    return theta,score,shares,trace

def select_refit(X,Y,split,target):
    Xtr,Ytr,Xv,Yv=X[:split],Y[:split],X[split:],Y[split:]
    base_seed=437110
    best=None; reps=[]

    for rep in range(REPEATS):
        seed=base_seed+1009*rep+sum(map(ord,target))
        th,val,shares,trace=hybrid_phase(Xtr,Ytr,seed,GENS,Xv=Xv,Yv=Yv)
        reps.append({
            "repeat":rep,
            "seed":seed,
            "inner_validation_fitness":float(val),
            "survivor_shares":shares,
        })
        if best is None or val<best[0]:
            best=(float(val),th.copy(),rep,shares)

    val,th,rep,select_shares=best
    seed=base_seed+900001+1009*rep+sum(map(ord,target))
    final,full,refit_shares,trace=hybrid_phase(X,Y,seed,REFIT,center=th)
    return final,val,float(full),int(rep),reps,select_shares,refit_shares

def predict_target(samples,target):
    keys,X,Y,tx,ym,ys,split=common.arrays(samples,target)
    th,val,full,rep,reps,sel_shares,refit_shares=select_refit(X,Y,split,target)
    pred=common.ann_predict(th,tx)[0]*ys+ym
    return pred,len(keys),{
        "selected_repeat":rep,
        "inner_validation_fitness":val,
        "full_history_refit_fitness":full,
        "repeat_validation":reps,
        "selected_repeat_survivor_shares":sel_shares,
        "refit_survivor_shares":refit_shares,
    }

def evaluate(bundle,cache,start,end):
    rows=[]
    for target in base.month_range(start,end):
        pred,n,meta=predict_target(cache[target],target)
        origin=base.month_shift(target,-1)
        rows.append({
            "target":target,
            "origin":origin,
            "method":"MPA_CPA",
            "train_rows":n,
            **meta,
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

    dev=evaluate(bundle,cache,DEV_START,DEV_END)
    tr=evaluate(bundle,cache,TR_START,TR_END)
    st=evaluate(bundle,cache,ST_START,ST_END)

    after=read_invariants(dsn)
    if after!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    result={
        "dev":{"metrics":base.metrics(dev),"yearly":base.yearly(dev),"rows":dev},
        "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
        "stress_2026":{"metrics":base.metrics(st),"rows":st},
    }

    out={
        "batch_id":"VW_MIDAS_ANN_STAGE3_BATCH35_V1",
        "method":{
            "architecture":"frozen canonical Stage-1 ANN 8->4(tanh)->4 linear",
            "hybrid":"MPA + CPA competitive operator portfolio",
            "selection_rule":"incumbent + MPA proposal population + CPA proposal population; best 24 survive by inner-training weighted MAE",
            "operator_share":"implicit training-only survivor competition",
            "population":POP,
            "selection_generations":GENS,
            "refit_generations":REFIT,
            "repeats":REPEATS,
            "MPA":{"FADs":.2,"P":.5,"phases":"Brownian/transition/Levy"},
            "CPA":{"explore_exploit_mix":.5,"restart_prob":.05},
        },
        "authority":{
            "database_access":"READ_ONLY",
            "feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
            "random_validation":"NONE",
            "target_month_in_fitness":False,
            "selection_period":f"{DEV_START}..{DEV_END}",
            "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
            "authority_invariants_before":bundle.invariants_before,
            "authority_invariants_after":after,
        },
        "models":{"MPA_CPA":result},
    }

    Path("vw_midas_ann_stage3_batch35_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )

    print(json.dumps({
        "MPA_CPA":{
            "dev":result["dev"]["metrics"],
            "transport_2025":result["transport_2025"]["metrics"],
            "stress_2026":result["stress_2026"]["metrics"],
        }
    },sort_keys=True))

if __name__=="__main__":
    main()
