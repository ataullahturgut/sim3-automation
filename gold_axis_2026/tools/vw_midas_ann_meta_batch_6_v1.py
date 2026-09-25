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


def alo_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    ants=common.init_population(rng,center)
    antlions=common.init_population(rng,center)
    afit=np.array([common.weighted_mae(z,X,Y) for z in ants])
    lfit=np.array([common.weighted_mae(z,X,Y) for z in antlions])
    elite=antlions[int(np.argmin(lfit))].copy()
    elite_fit=float(np.min(lfit))
    vbest,vfit=None,math.inf
    if Xv is not None:
        pool=np.vstack([ants,antlions]); pfit=np.concatenate([afit,lfit])
        vbest,vfit=common.validation_pick(pool,pfit,Xv,Yv,vbest,vfit)
    for t in range(generations):
        quality=1/(1+lfit); probs=quality/quality.sum()
        shrink=1+10*(t/max(1,generations-1))
        for i in range(POP_SIZE):
            sel=int(rng.choice(POP_SIZE,p=probs))
            centerp=(antlions[sel]+elite)/2
            radius=(UPPER-LOWER)/shrink
            ants[i]=np.clip(centerp+rng.uniform(-1,1,PARAM_DIM)*radius,LOWER,UPPER)
        afit=np.array([common.weighted_mae(z,X,Y) for z in ants])
        combined=np.vstack([antlions,ants]); cfit=np.concatenate([lfit,afit])
        keep=np.argsort(cfit)[:POP_SIZE]
        antlions=combined[keep]; lfit=cfit[keep]
        if float(lfit[0])<elite_fit:
            elite_fit=float(lfit[0]); elite=antlions[0].copy()
        if Xv is not None:
            vbest,vfit=common.validation_pick(antlions,lfit,Xv,Yv,vbest,vfit)
    return (vbest if Xv is not None else elite), (vfit if Xv is not None else elite_fit)


def tlbo_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for _ in range(generations):
        teacher=x[int(np.argmin(fit))].copy(); mean=x.mean(0); TF=int(rng.integers(1,3))
        for i in range(POP_SIZE):
            cand=x[i]+rng.random(PARAM_DIM)*(teacher-TF*mean)
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.weighted_mae(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf
        for i in range(POP_SIZE):
            j=i
            while j==i:
                j=int(rng.integers(0,POP_SIZE))
            direction=(x[i]-x[j]) if fit[i]<fit[j] else (x[j]-x[i])
            cand=x[i]+rng.random(PARAM_DIM)*direction
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.weighted_mae(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


def jaya_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for _ in range(generations):
        best=x[int(np.argmin(fit))].copy(); worst=x[int(np.argmax(fit))].copy()
        for i in range(POP_SIZE):
            r1=rng.random(PARAM_DIM); r2=rng.random(PARAM_DIM)
            cand=x[i]+r1*(best-np.abs(x[i]))-r2*(worst-np.abs(x[i]))
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.weighted_mae(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


def hgs_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for t in range(generations):
        order=np.argsort(fit); best=x[order[0]].copy()
        worst=float(fit[order[-1]]); bestf=float(fit[order[0]])
        hunger=np.zeros(POP_SIZE)
        span=max(1e-12,worst-bestf)
        for i in range(POP_SIZE):
            hunger[i]=((fit[i]-bestf)/span)+rng.random()*0.1
        hnorm=hunger/(hunger.max()+1e-12)
        shrink=1-t/max(1,generations-1)
        for i in range(POP_SIZE):
            r1=rng.random(PARAM_DIM); r2=rng.random(PARAM_DIM)
            W1=2*r1*shrink-1
            W2=2*r2*(1-hnorm[i])
            cand=x[i]*(1-rng.random()) + W1*np.abs(best-x[i]) + W2*best
            if rng.random()<0.03:
                cand=rng.uniform(LOWER,UPPER,PARAM_DIM)
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.weighted_mae(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


PHASE={"ALO":alo_phase,"TLBO":tlbo_phase,"JAYA":jaya_phase,"HGS":hgs_phase}
SEED_BASE={"ALO":227110,"TLBO":237110,"JAYA":247110,"HGS":257110}


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
    for method in ("ALO","TLBO","JAYA","HGS"):
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
        "batch_id":"VW_MIDAS_ANN_META_BATCH_6_V1",
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
            "ALO":{"roulette_quality":"1/(1+loss)","shrink":"1_to_11"},
            "TLBO":{"teacher_factor":"random_1_or_2","teacher_and_learner_phases":True},
            "JAYA":{"best_worst_update":True},
            "HGS":{"hunger_normalization":True,"restart_prob":0.03}
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
    Path("vw_midas_ann_meta_batch_6_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        method:{
            "dev":results[method]["dev"]["metrics"],
            "transport_2025":results[method]["transport_2025"]["metrics"],
            "stress_2026":results[method]["stress_2026"]["metrics"]
        } for method in results
    },sort_keys=True))


if __name__=="__main__":
    main()
