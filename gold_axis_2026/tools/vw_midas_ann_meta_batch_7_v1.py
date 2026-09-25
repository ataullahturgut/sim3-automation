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


def choa_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for t in range(generations):
        order=np.argsort(fit)
        leaders=[x[order[k]].copy() for k in range(4)]
        f=2.5-2.0*t/max(1,generations-1)
        new=np.empty_like(x)
        for i in range(POP_SIZE):
            cand=np.zeros(PARAM_DIM)
            for leader in leaders:
                r1=rng.random(PARAM_DIM); r2=rng.random(PARAM_DIM)
                a=2*f*r1-f; c=2*r2
                d=np.abs(c*leader-x[i])
                cand += leader-a*d
            cand/=4.0
            if rng.random()<0.1:
                cand += 0.05*rng.normal(0,1,PARAM_DIM)
            new[i]=np.clip(cand,LOWER,UPPER)
        x=new
        fit=np.array([common.weighted_mae(z,X,Y) for z in x])
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


def hgso_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    H=rng.uniform(0.1,1.0,POP_SIZE)
    C=rng.uniform(0.1,1.0,POP_SIZE)
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for t in range(generations):
        best=x[int(np.argmin(fit))].copy()
        T=np.exp(-t/max(1,generations))
        fmin=float(fit.min()); fmax=float(fit.max())
        for i in range(POP_SIZE):
            H[i]=H[i]*np.exp(-C[i]*(1/T-1))
            gamma=np.exp(-(fit[i]-fmin)/(abs(fmax-fmin)+1e-12))
            direction=best-x[i]
            cand=x[i]+rng.uniform(-1,1,PARAM_DIM)*H[i]*direction + gamma*rng.normal(0,0.05,PARAM_DIM)
            if rng.random()<0.1:
                cand += rng.uniform(-1,1,PARAM_DIM)*(UPPER-LOWER)*0.02
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.weighted_mae(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


def aoa_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    alpha=5.0; mu=0.5
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for t in range(generations):
        best=x[int(np.argmin(fit))].copy()
        moa=0.2+(1.0-0.2)*(t/max(1,generations-1))
        mop=1-(t/max(1,generations))**(1/alpha)
        for i in range(POP_SIZE):
            r1,r2,r3=rng.random(),rng.random(),rng.random()
            if r1>moa:
                if r2<0.5:
                    cand=best/(mop+1e-12)*(mu*(UPPER-LOWER)+LOWER)
                else:
                    cand=best*mop*(mu*(UPPER-LOWER)+LOWER)
            else:
                if r3<0.5:
                    cand=best-mop*(mu*(UPPER-LOWER)+LOWER)
                else:
                    cand=best+mop*(mu*(UPPER-LOWER)+LOWER)
            cand=np.asarray(cand)
            if cand.ndim==0:
                cand=np.full(PARAM_DIM,float(cand))
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.weighted_mae(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


def cpa_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for t in range(generations):
        best=x[int(np.argmin(fit))].copy()
        scale=1-t/max(1,generations-1)
        for i in range(POP_SIZE):
            j=int(rng.integers(0,POP_SIZE))
            if rng.random()<0.5:
                cand=x[i]+rng.random(PARAM_DIM)*(best-x[i])+scale*rng.random(PARAM_DIM)*(x[j]-x[i])
            else:
                cand=best+scale*rng.normal(0,1,PARAM_DIM)*np.abs(best-x[i])
            if rng.random()<0.05:
                cand=rng.uniform(LOWER,UPPER,PARAM_DIM)
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.weighted_mae(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


PHASE={"CHOA":choa_phase,"HGSO":hgso_phase,"AOA":aoa_phase,"CPA":cpa_phase}
SEED_BASE={"CHOA":267110,"HGSO":277110,"AOA":287110,"CPA":297110}


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
    for method in ("CHOA","HGSO","AOA","CPA"):
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
        "batch_id":"VW_MIDAS_ANN_META_BATCH_7_V1",
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
            "CHOA":{"leaders":4,"f_schedule":"2.5_to_0.5","mutation_prob":0.1},
            "HGSO":{"henry_range":[0.1,1.0],"solubility_range":[0.1,1.0],"noise_sd":0.05},
            "AOA":{"alpha":5.0,"mu":0.5,"moa_schedule":"0.2_to_1.0"},
            "CPA":{"explore_exploit_mix":0.5,"restart_prob":0.05}
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
    Path("vw_midas_ann_meta_batch_7_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        method:{
            "dev":results[method]["dev"]["metrics"],
            "transport_2025":results[method]["transport_2025"]["metrics"],
            "stress_2026":results[method]["stress_2026"]["metrics"]
        } for method in results
    },sort_keys=True))


if __name__=="__main__":
    main()
