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


def hgs_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    for t in range(generations):
        order=np.argsort(fit)
        best=x[order[0]].copy()
        bestf=float(fit[order[0]])
        worst=float(fit[order[-1]])
        den=max(1e-12,worst-bestf)
        hunger=np.array([((fit[i]-bestf)/den)+rng.random()*0.1 for i in range(POP_SIZE)])
        hnorm=hunger/(hunger.max()+1e-12)
        shrink=1-t/max(1,generations-1)

        for i in range(POP_SIZE):
            r1=rng.random(PARAM_DIM); r2=rng.random(PARAM_DIM)
            W1=2*r1*shrink-1
            W2=2*r2*(1-hnorm[i])
            cand=x[i]*(1-rng.random()) + W1*np.abs(best-x[i]) + W2*best
            if rng.random()<0.03:
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


def choa_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

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
                sigma=common.REFIT_SIGMA if refit else 0.05*SPAN
                cand += rng.normal(0,1,PARAM_DIM)*sigma
            new[i]=np.clip(cand,LOWER,UPPER)
        x=new
        fit=common.population_fit(x,X,Y)

        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


def hgso_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    H=rng.uniform(0.1,1.0,POP_SIZE)
    C=rng.uniform(0.1,1.0,POP_SIZE)
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    for t in range(generations):
        best=x[int(np.argmin(fit))].copy()
        T=np.exp(-t/max(1,generations))
        fmin=float(fit.min()); fmax=float(fit.max())
        for i in range(POP_SIZE):
            H[i]=H[i]*np.exp(-C[i]*(1/T-1))
            gamma=np.exp(-(fit[i]-fmin)/(abs(fmax-fmin)+1e-12))
            direction=best-x[i]
            local_sigma=common.REFIT_SIGMA if refit else 0.05*SPAN
            cand=x[i]+rng.uniform(-1,1,PARAM_DIM)*H[i]*direction + gamma*rng.normal(0,1,PARAM_DIM)*local_sigma
            if rng.random()<0.1:
                cand += rng.uniform(-1,1,PARAM_DIM)*SPAN*0.02
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.training_loss(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf

        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


def aoa_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    alpha=5.0; mu=0.5
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    # Apply AOA in normalized [0,1] parameter space so heterogeneous
    # center/log-spread bounds do not distort the arithmetic operators.
    for t in range(generations):
        bi=int(np.argmin(fit))
        best=x[bi].copy()
        bestz=(best-LOWER)/(SPAN+1e-12)
        moa=0.2+(1.0-0.2)*(t/max(1,generations-1))
        mop=1-(t/max(1,generations))**(1/alpha)

        for i in range(POP_SIZE):
            zi=(x[i]-LOWER)/(SPAN+1e-12)
            r1,r2,r3=rng.random(),rng.random(),rng.random()
            scale=mu+0.5*rng.random(PARAM_DIM)
            if r1>moa:
                if r2<0.5:
                    candz=bestz/(mop+1e-12)*scale
                else:
                    candz=bestz*mop*scale
            else:
                if r3<0.5:
                    candz=bestz-mop*scale
                else:
                    candz=bestz+mop*scale
            # retain a weak memory term to avoid normalized arithmetic
            # collapsing all dimensions to identical bound behavior
            candz=0.9*candz+0.1*zi
            cand=LOWER+np.clip(candz,0.0,1.0)*SPAN
            cf=common.training_loss(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf

        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


PHASE={"HGS":hgs_phase,"CHOA":choa_phase,"HGSO":hgso_phase,"AOA":aoa_phase}
SEED_BASE={"HGS":258110,"CHOA":268110,"HGSO":278110,"AOA":288110}


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
        "HGS":{"hunger_normalization":True,"restart_prob":0.03},
        "CHOA":{"leaders":4,"f_schedule":"2.5_to_0.5","perturb_prob":0.1},
        "HGSO":{"H_init":[0.1,1.0],"C_init":[0.1,1.0],"perturb_prob":0.1},
        "AOA":{"alpha":5.0,"mu":0.5,"moa_schedule":"0.2_to_1.0","parameter_space":"span_normalized"}
    }[method]

    out={
        "batch_id":"VW_MIDAS_ELMFIS_META_BATCH_7_V1",
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

    p=Path(f"vw_midas_elmfis_meta_batch_7_v1_{method.lower()}_result.json")
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"method":method,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--method",required=True,choices=sorted(PHASE))
    args=ap.parse_args()
    run_method(args.method)


if __name__=="__main__":
    main()
