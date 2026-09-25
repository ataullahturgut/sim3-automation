from __future__ import annotations

import json, math, os
from pathlib import Path

import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import vw_midas_ann_meta_batch_1_v1 as common

DEV_START, DEV_END = common.DEV_START, common.DEV_END
TR_START, TR_END = common.TR_START, common.TR_END
ST_START, ST_END = common.ST_START, common.ST_END

POP_SIZE = common.POP_SIZE
SELECT_GENS = common.SELECT_GENS
REFIT_GENS = common.REFIT_GENS
REPEATS = common.REPEATS
LOWER, UPPER = common.LOWER, common.UPPER
PARAM_DIM = common.PARAM_DIM


def sca_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for t in range(generations):
        best=x[int(np.argmin(fit))].copy()
        r1=2-2*t/max(1,generations-1)
        for i in range(POP_SIZE):
            r2=2*np.pi*rng.random(PARAM_DIM)
            r3=2*rng.random(PARAM_DIM)
            r4=rng.random(PARAM_DIM)
            trig=np.where(r4<.5,np.sin(r2),np.cos(r2))
            cand=x[i]+r1*trig*np.abs(r3*best-x[i])
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.weighted_mae(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


def salp_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for t in range(generations):
        food=x[int(np.argmin(fit))].copy()
        c1=2*np.exp(-((4*t/max(1,generations))**2))
        new=x.copy()
        c2=rng.random(PARAM_DIM); c3=rng.random(PARAM_DIM)
        step=((UPPER-LOWER)*c2+LOWER)
        new[0]=food+np.where(c3<.5,1,-1)*c1*step
        for i in range(1,POP_SIZE):
            new[i]=0.5*(x[i]+new[i-1])
        new=np.clip(new,LOWER,UPPER)
        nfit=np.array([common.weighted_mae(z,X,Y) for z in new])
        improve=nfit<fit
        x[improve]=new[improve]; fit[improve]=nfit[improve]
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


def sma_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for t in range(generations):
        order=np.argsort(fit)
        best=x[order[0]].copy()
        fbest,fworst=fit[order[0]],fit[order[-1]]
        W=np.ones((POP_SIZE,PARAM_DIM))
        for rank,idx in enumerate(order):
            ratio=(fbest-fit[idx])/(fbest-fworst+1e-12)
            r=rng.random(PARAM_DIM)
            if rank<POP_SIZE/2:
                W[idx]=1+r*np.log10(abs(ratio)+1)
            else:
                W[idx]=1-r*np.log10(abs(ratio)+1)
        a=np.arctanh(max(1e-6,1-(t+1)/generations))
        b=1-(t+1)/generations
        new=np.empty_like(x)
        for i in range(POP_SIZE):
            if rng.random()<0.03:
                new[i]=rng.uniform(LOWER,UPPER,PARAM_DIM)
            else:
                p=np.tanh(abs(fit[i]-fbest))
                vb=rng.uniform(-a,a,PARAM_DIM)
                vc=rng.uniform(-b,b,PARAM_DIM)
                A,B=rng.choice(POP_SIZE,2,replace=False)
                if rng.random()<p:
                    new[i]=best+vb*(W[i]*x[A]-x[B])
                else:
                    new[i]=vc*x[i]
        x=np.clip(new,LOWER,UPPER)
        fit=np.array([common.weighted_mae(z,X,Y) for z in x])
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


def goa_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    cmax,cmin=1.0,0.00004
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for t in range(generations):
        best=x[int(np.argmin(fit))].copy()
        c=cmax-(cmax-cmin)*t/max(1,generations-1)
        new=np.empty_like(x)
        for i in range(POP_SIZE):
            ssum=np.zeros(PARAM_DIM)
            for j in range(POP_SIZE):
                if i==j:
                    continue
                dist=np.linalg.norm(x[j]-x[i])+1e-12
                dij=2+np.mod(dist,2)
                s=0.5*np.exp(-dij/1.5)-np.exp(-dij)
                ssum += ((x[j]-x[i])/dist)*s
            new[i]=c*ssum+best
        x=np.clip(new,LOWER,UPPER)
        fit=np.array([common.weighted_mae(z,X,Y) for z in x])
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


PHASE={"SCA":sca_phase,"SALP":salp_phase,"SMA":sma_phase,"GOA":goa_phase}
SEED_BASE={"SCA":187110,"SALP":197110,"SMA":207110,"GOA":217110}


def select_and_refit(method,X,Y,split,target):
    fn=PHASE[method]
    Xtr,Ytr,Xv,Yv=X[:split],Y[:split],X[split:],Y[split:]
    repeat_rows=[]
    best_theta,best_val,best_rep=None,math.inf,None
    target_seed=sum(map(ord,target))
    for rep in range(REPEATS):
        seed=SEED_BASE[method]+1009*rep+target_seed
        theta,vfit=fn(Xtr,Ytr,seed,SELECT_GENS,center=None,Xv=Xv,Yv=Yv)
        repeat_rows.append({"repeat":rep,"seed":seed,"inner_validation_fitness":float(vfit)})
        if vfit<best_val:
            best_theta,best_val,best_rep=theta.copy(),float(vfit),rep
    refit_seed=SEED_BASE[method]+900001+1009*int(best_rep)+target_seed
    final_theta,full_fit=fn(X,Y,refit_seed,REFIT_GENS,center=best_theta,Xv=None,Yv=None)
    return final_theta,best_val,float(full_fit),int(best_rep),repeat_rows


def predict_target(samples,target,method):
    keys,X,Y,tx,ym,ys,split=common.arrays(samples,target)
    theta,valfit,fullfit,rep,repeats=select_and_refit(method,X,Y,split,target)
    pred=common.ann_predict(theta,tx)[0]*ys+ym
    return pred,len(keys),valfit,fullfit,rep,repeats


def evaluate(bundle,cache,method,start,end):
    rows=[]
    for target in base.month_range(start,end):
        pred,n,valfit,fullfit,rep,repeats=predict_target(cache[target],target,method)
        origin=base.month_shift(target,-1)
        rows.append({
            "target":target,"origin":origin,"method":method,"train_rows":n,
            "selected_repeat":rep,"inner_validation_fitness":valfit,
            "full_history_refit_fitness":fullfit,"repeat_validation":repeats,
            "pred_log_return_gold":float(pred[0]),
            "forecast":float(bundle.core_gold[origin]*math.exp(float(pred[0]))),
            "actual":float(bundle.core_gold[target]),"rw":float(bundle.core_gold[origin])
        })
    return rows


def read_authority_invariants(dsn):
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
    for method in ("SCA","SALP","SMA","GOA"):
        dev=evaluate(bundle,cache,method,DEV_START,DEV_END)
        tr=evaluate(bundle,cache,method,TR_START,TR_END)
        st=evaluate(bundle,cache,method,ST_START,ST_END)
        results[method]={
            "model_id":f"VW_MIDAS_{method}_ANN_V1",
            "dev":{"metrics":base.metrics(dev),"yearly":base.yearly(dev),"rows":dev},
            "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
            "stress_2026":{"metrics":base.metrics(st),"rows":st}
        }
    after=read_authority_invariants(dsn)
    if after!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={
        "batch_id":"VW_MIDAS_ANN_META_BATCH_5_V1",
        "canonical_ann":{
            "input_units":common.INPUTS,"hidden_layers":[common.HIDDEN],
            "hidden_activation":common.ACTIVATION,"output_units":common.OUTPUTS,
            "output_activation":"linear","optimized_parameters":common.PARAM_DIM
        },
        "optimization_contract":{
            "scope":"all_ann_weights_and_biases","bounds":[LOWER,UPPER],"population":POP_SIZE,
            "selection_generations":SELECT_GENS,"full_history_refit_generations":REFIT_GENS,
            "deterministic_repeats_per_target":REPEATS,
            "inner_split":"chronological_last_20pct_training_history_min_6",
            "population_evolution_objective":"0.7*Gold_standardized_MAE + 0.3*all_output_standardized_MAE on inner-training",
            "selection_fitness":"same weighted MAE on chronological validation tail; top-quartile train candidates only",
            "refit":"warm-start from validation-selected theta; optimize on all pre-target history",
            "target_month_in_fitness":False
        },
        "method_parameters":{
            "SCA":{"r1_schedule":"2_to_0","trig":"sin_or_cos"},
            "SALP":{"c1_schedule":"2*exp(-(4t/T)^2)","leader_followers":True},
            "SMA":{"random_restart_prob":0.03,"adaptive_weights":True},
            "GOA":{"cmax":1.0,"cmin":0.00004,"pairwise_social_force":True}
        },
        "authority":{
            "database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
            "random_validation":"NONE","selection_period":f"{DEV_START}..{DEV_END}",
            "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
            "source_checks":bundle.source_checks,
            "authority_invariants_before":bundle.invariants_before,
            "authority_invariants_after":after
        },
        "models":results
    }
    Path("vw_midas_ann_meta_batch_5_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        method:{
            "dev":results[method]["dev"]["metrics"],
            "transport_2025":results[method]["transport_2025"]["metrics"],
            "stress_2026":results[method]["stress_2026"]["metrics"]
        } for method in results
    },sort_keys=True))


if __name__=="__main__":
    main()
