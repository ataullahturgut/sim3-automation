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


def goa_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    cmax,cmin=1.0,0.00004
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    for t in range(generations):
        best=x[int(np.argmin(fit))].copy()
        c=cmax-(cmax-cmin)*t/max(1,generations-1)
        new=np.empty_like(x)
        # Normalize pairwise distances by parameter spans so centers and
        # log-spreads contribute comparably.
        z=(x-LOWER)/(SPAN+1e-12)
        for i in range(POP_SIZE):
            ssum=np.zeros(PARAM_DIM)
            for j in range(POP_SIZE):
                if i==j:
                    continue
                dz=z[j]-z[i]
                dist=np.linalg.norm(dz)+1e-12
                dij=2+np.mod(dist,2)
                social=0.5*np.exp(-dij/1.5)-np.exp(-dij)
                ssum += (dz/dist)*social
            new[i]=best+c*ssum*SPAN
        x=np.clip(new,LOWER,UPPER)
        fit=common.population_fit(x,X,Y)
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


def alo_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    ants=common.init_population(rng,center,refit=refit)
    antlions=common.init_population(rng,center,refit=refit)
    afit=common.population_fit(ants,X,Y)
    lfit=common.population_fit(antlions,X,Y)
    elite=antlions[int(np.argmin(lfit))].copy()
    elite_fit=float(np.min(lfit))
    vbest,vfit=None,math.inf
    if Xv is not None:
        pool=np.vstack([ants,antlions]); pfit=np.concatenate([afit,lfit])
        vbest,vfit=common.validation_pick(pool,pfit,X,Y,Xv,Yv,vbest,vfit)

    for t in range(generations):
        quality=1.0/(1.0+lfit)
        probs=quality/quality.sum()
        shrink=1.0+10.0*(t/max(1,generations-1))
        radius=SPAN/shrink
        for i in range(POP_SIZE):
            sel=int(rng.choice(POP_SIZE,p=probs))
            centerp=(antlions[sel]+elite)/2.0
            ants[i]=np.clip(centerp+rng.uniform(-1,1,PARAM_DIM)*radius,LOWER,UPPER)
        afit=common.population_fit(ants,X,Y)
        combined=np.vstack([antlions,ants]); cfit=np.concatenate([lfit,afit])
        keep=np.argsort(cfit)[:POP_SIZE]
        antlions,lfit=combined[keep],cfit[keep]
        if float(lfit[0])<elite_fit:
            elite_fit=float(lfit[0]); elite=antlions[0].copy()
        if Xv is not None:
            vbest,vfit=common.validation_pick(antlions,lfit,X,Y,Xv,Yv,vbest,vfit)

    return (vbest if Xv is not None else elite),(vfit if Xv is not None else elite_fit)


def tlbo_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    for _ in range(generations):
        teacher=x[int(np.argmin(fit))].copy()
        mean=x.mean(axis=0)
        TF=int(rng.integers(1,3))

        for i in range(POP_SIZE):
            cand=x[i]+rng.random(PARAM_DIM)*(teacher-TF*mean)
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.training_loss(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf

        for i in range(POP_SIZE):
            j=i
            while j==i:
                j=int(rng.integers(0,POP_SIZE))
            direction=(x[i]-x[j]) if fit[i]<fit[j] else (x[j]-x[i])
            cand=x[i]+rng.random(PARAM_DIM)*direction
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.training_loss(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf

        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


def jaya_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    for _ in range(generations):
        best=x[int(np.argmin(fit))].copy()
        worst=x[int(np.argmax(fit))].copy()
        for i in range(POP_SIZE):
            r1=rng.random(PARAM_DIM); r2=rng.random(PARAM_DIM)
            cand=x[i]+r1*(best-np.abs(x[i]))-r2*(worst-np.abs(x[i]))
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.training_loss(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


PHASE={"GOA":goa_phase,"ALO":alo_phase,"TLBO":tlbo_phase,"JAYA":jaya_phase}
SEED_BASE={"GOA":218110,"ALO":228110,"TLBO":238110,"JAYA":248110}


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
        "GOA":{"cmax":1.0,"cmin":0.00004,"pairwise_social_force":True,"distance_space":"span_normalized"},
        "ALO":{"dual_populations":True,"shrink_schedule":"1_to_11","roulette_quality":"1/(1+loss)"},
        "TLBO":{"teacher_factor":"random_1_or_2","teacher_and_learner_phases":True},
        "JAYA":{"best_attraction":True,"worst_repulsion":True}
    }[method]

    out={
        "batch_id":"VW_MIDAS_ELMFIS_META_BATCH_6_V1",
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
    p=Path(f"vw_midas_elmfis_meta_batch_6_v1_{method.lower()}_result.json")
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"method":method,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--method",required=True,choices=sorted(PHASE))
    args=ap.parse_args()
    run_method(args.method)


if __name__=="__main__":
    main()
