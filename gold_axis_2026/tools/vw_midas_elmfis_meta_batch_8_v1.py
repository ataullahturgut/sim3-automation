from __future__ import annotations

import argparse, json, math, os
from pathlib import Path

import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as elmfis
import vw_midas_elmfis_meta_batch_1_v1 as common

DEV_START, DEV_END = common.DEV_START, common.DEV_END
TR_START, TR_END = common.TR_START, common.TR_END
ST_START, ST_END = common.ST_START, common.ST_END

POP_SIZE=common.POP_SIZE
SELECT_GENS=common.SELECT_GENS
REFIT_GENS=common.REFIT_GENS
REPEATS=common.REPEATS
PARAM_DIM=common.PARAM_DIM
LOWER,UPPER=common.LOWER,common.UPPER
SPAN=UPPER-LOWER


def cpa_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

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
                if refit:
                    cand=center+rng.normal(0,1,PARAM_DIM)*common.REFIT_SIGMA
                else:
                    cand=rng.uniform(LOWER,UPPER,size=PARAM_DIM)
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.training_loss(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf

        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


def krill_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    N=np.zeros_like(x)
    Fd=np.zeros_like(x)
    dt=0.5
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    for t in range(generations):
        order=np.argsort(fit)
        best=x[order[0]].copy()
        z=(x-LOWER)/(SPAN+1e-12)
        bestz=(best-LOWER)/(SPAN+1e-12)
        new=np.empty_like(x)

        for i in range(POP_SIZE):
            d=np.linalg.norm(z-z[i],axis=1)
            neigh=np.argsort(d)[1:min(5,POP_SIZE)]
            localz=np.mean(z[neigh],axis=0) if len(neigh) else bestz
            N[i]=0.6*N[i]+0.8*((localz-z[i])+(bestz-z[i]))
            Fd[i]=0.5*Fd[i]+0.8*(bestz-z[i])*(1-t/max(1,generations-1))
            diffusion=0.01*(1-t/max(1,generations))*rng.normal(0,1,PARAM_DIM)
            candz=z[i]+dt*(N[i]+Fd[i])+diffusion
            if rng.random()<0.05:
                candz += rng.uniform(-1,1,PARAM_DIM)*0.05
            new[i]=LOWER+np.clip(candz,0.0,1.0)*SPAN

        x=new
        fit=common.population_fit(x,X,Y)
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


def crow_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    mem=x.copy()
    fit=common.population_fit(x,X,Y)
    mfit=fit.copy()
    fl,ap=2.0,0.1
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(mem,mfit,X,Y,Xv,Yv,vbest,vfit)

    for _ in range(generations):
        for i in range(POP_SIZE):
            j=i
            while j==i:
                j=int(rng.integers(0,POP_SIZE))

            if rng.random()>ap:
                cand=x[i]+rng.random(PARAM_DIM)*fl*(mem[j]-x[i])
            else:
                if refit:
                    cand=center+rng.normal(0,1,PARAM_DIM)*common.REFIT_SIGMA
                else:
                    cand=rng.uniform(LOWER,UPPER,size=PARAM_DIM)

            cand=np.clip(cand,LOWER,UPPER)
            cf=common.training_loss(cand,X,Y)
            x[i],fit[i]=cand,cf
            if cf<mfit[i]:
                mem[i],mfit[i]=cand,cf

        if Xv is not None:
            vbest,vfit=common.validation_pick(mem,mfit,X,Y,Xv,Yv,vbest,vfit)

    bi=int(np.argmin(mfit))
    return (vbest if Xv is not None else mem[bi].copy()),(vfit if Xv is not None else float(mfit[bi]))


PHASE={"CPA":cpa_phase,"KRILL":krill_phase,"CROW":crow_phase}
SEED_BASE={"CPA":298110,"KRILL":308110,"CROW":318110}


def select_and_refit(method,X,Y,split,target):
    fn=PHASE[method]
    Xtr,Ytr,Xv,Yv=X[:split],Y[:split],X[split:],Y[split:]
    base_theta=common.initial_theta(Xtr)
    repeat_rows=[]; best_theta,best_val,best_rep=None,math.inf,None
    target_seed=sum(map(ord,target))

    for rep in range(REPEATS):
        seed=SEED_BASE[method]+1009*rep+target_seed
        theta,vfit=fn(Xtr,Ytr,seed,SELECT_GENS,base_theta,Xv,Yv,False)
        repeat_rows.append({"repeat":rep,"seed":seed,"inner_validation_fitness":float(vfit)})
        if vfit<best_val:
            best_theta,best_val,best_rep=theta.copy(),float(vfit),rep

    refit_seed=SEED_BASE[method]+900001+1009*int(best_rep)+target_seed
    final_theta,full_fit=fn(X,Y,refit_seed,REFIT_GENS,best_theta,None,None,True)
    return final_theta,best_val,float(full_fit),int(best_rep),repeat_rows


def predict_target(samples,target,method):
    keys,X,Y,tx,ym,ys,split=common.arrays(samples,target)
    theta,valfit,fullfit,rep,repeats=select_and_refit(method,X,Y,split,target)
    pred_std=common.predict_with_fit(theta,X,Y,tx)[0]
    pred=pred_std*ys+ym
    centers,spreads=common.decode(theta)
    return pred,len(keys),valfit,fullfit,rep,repeats,float(np.min(spreads)),float(np.max(spreads)),float(np.max(np.abs(centers)))


def evaluate(bundle,cache,method,start,end):
    rows=[]
    for target in base.month_range(start,end):
        pred,n,valfit,fullfit,rep,repeats,min_spread,max_spread,max_abs_center=predict_target(cache[target],target,method)
        origin=base.month_shift(target,-1)
        rows.append({
            "target":target,"origin":origin,"method":method,"train_rows":n,
            "selected_repeat":rep,"inner_validation_fitness":valfit,
            "full_history_refit_fitness":fullfit,"repeat_validation":repeats,
            "antecedent_min_spread":min_spread,"antecedent_max_spread":max_spread,
            "antecedent_max_abs_center":max_abs_center,
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


def run_method(method):
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    dev=evaluate(bundle,cache,method,DEV_START,DEV_END)
    tr=evaluate(bundle,cache,method,TR_START,TR_END)
    st=evaluate(bundle,cache,method,ST_START,ST_END)

    after=read_authority_invariants(dsn)
    if after!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    params={
        "CPA":{"explore_exploit_mix":0.5,"restart_prob":0.05},
        "KRILL":{"dt":0.5,"neighbor_count":4,"induced_motion_memory":0.6,"foraging_memory":0.5,"space":"span_normalized"},
        "CROW":{"flight_length":2.0,"awareness_probability":0.1,"memory":True}
    }[method]

    out={
        "batch_id":"VW_MIDAS_ELMFIS_META_BATCH_8_V1",
        "model_id":f"VW_MIDAS_{method}_ELMFIS_V1","method":method,
        "canonical_elmfis":{
            "inputs":common.INPUTS,"outputs":common.OUTPUTS,"rules":common.RULES,
            "membership":"bell_gaussian_exp_minus_squared_distance",
            "and_operator":"product_logspace","rule_normalization":True,
            "consequent":"first_order_TSK_linear","consequent_fit":"analytic_ridge_per_candidate",
            "ridge_alpha":elmfis.RIDGE_ALPHA
        },
        "optimization_contract":{
            "scope":"antecedent_centers_and_log_spreads_only","optimized_parameters":PARAM_DIM,
            "center_bounds_standardized":[common.CENTER_LOW,common.CENTER_HIGH],
            "spread_bounds_standardized":[common.SPREAD_LOW,common.SPREAD_HIGH],
            "population_reference":POP_SIZE,"selection_generations":SELECT_GENS,
            "full_history_refit_generations":REFIT_GENS,"deterministic_repeats_per_target":REPEATS,
            "initialization":"training_only_kmeans_anchor_plus_local_and_uniform_exploration",
            "inner_split":"chronological_last_20pct_training_history_min_6",
            "population_evolution_objective":"0.7*Gold_standardized_MAE + 0.3*all_output_standardized_MAE on inner-training with analytic ridge consequent",
            "selection_fitness":"same weighted MAE on chronological validation tail; top-quartile train candidates only; consequents fit on inner-training",
            "refit":"warm-start antecedents from validation-selected theta; optimize on all pre-target history; consequents solved analytically",
            "target_month_in_fitness":False
        },
        "method_parameters":params,
        "authority":{
            "database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
            "target":"NEXT_MONTH_AVERAGE_PRICE_VIA_4_RETURN_OUTPUTS","random_validation":"NONE",
            "selection_period":f"{DEV_START}..{DEV_END}","2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
            "primary_metrics":["sum_abs_error","direction_accuracy_pct"],
            "source_checks":bundle.source_checks,
            "authority_invariants_before":bundle.invariants_before,
            "authority_invariants_after":after
        },
        "dev":{"metrics":elmfis.active_metrics(dev),"yearly":elmfis.yearly(dev),"rows":dev},
        "transport_2025":{"metrics":elmfis.active_metrics(tr),"rows":tr},
        "stress_2026":{"metrics":elmfis.active_metrics(st),"rows":st}
    }

    p=Path(f"vw_midas_elmfis_meta_batch_8_v1_{method.lower()}_result.json")
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"method":method,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--method",required=True,choices=sorted(PHASE))
    args=ap.parse_args()
    run_method(args.method)


if __name__=="__main__":
    main()
