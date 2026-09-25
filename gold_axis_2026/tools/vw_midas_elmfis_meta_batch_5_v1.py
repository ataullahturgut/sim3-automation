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


def levy(rng,shape,beta=1.5):
    sigma=(math.gamma(1+beta)*math.sin(math.pi*beta/2)/(math.gamma((1+beta)/2)*beta*2**((beta-1)/2)))**(1/beta)
    u=rng.normal(0,sigma,shape); v=rng.normal(0,1,shape)
    return u/(np.abs(v)**(1/beta)+1e-12)


def cs_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    nests=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(nests,X,Y)
    pa=0.25
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(nests,fit,X,Y,Xv,Yv,vbest,vfit)
    for _ in range(generations):
        best=nests[int(np.argmin(fit))].copy()
        for i in range(POP_SIZE):
            cand=nests[i]+0.01*levy(rng,(PARAM_DIM,))*(nests[i]-best)
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.training_loss(cand,X,Y)
            j=int(rng.integers(0,POP_SIZE))
            if cf<fit[j]:
                nests[j],fit[j]=cand,cf

        abandon=rng.random(POP_SIZE)<pa
        for i in np.where(abandon)[0]:
            j,k=rng.choice(POP_SIZE,2,replace=False)
            cand=nests[i]+rng.random(PARAM_DIM)*(nests[j]-nests[k])
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.training_loss(cand,X,Y)
            if cf<fit[i]:
                nests[i],fit[i]=cand,cf

        if Xv is not None:
            vbest,vfit=common.validation_pick(nests,fit,X,Y,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else nests[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


def sca_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)
    for t in range(generations):
        best=x[int(np.argmin(fit))].copy()
        r1=2-2*t/max(1,generations-1)
        for i in range(POP_SIZE):
            r2=2*np.pi*rng.random(PARAM_DIM)
            r3=2*rng.random(PARAM_DIM)
            r4=rng.random(PARAM_DIM)
            trig=np.where(r4<0.5,np.sin(r2),np.cos(r2))
            cand=x[i]+r1*trig*np.abs(r3*best-x[i])
            cand=np.clip(cand,LOWER,UPPER)
            cf=common.training_loss(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i]=cand,cf
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


def salp_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)
    for t in range(generations):
        food=x[int(np.argmin(fit))].copy()
        c1=2*np.exp(-((4*t/max(1,generations))**2))
        new=x.copy()
        c2=rng.random(PARAM_DIM); c3=rng.random(PARAM_DIM)
        # Standard salp leader move, applied component-wise to heterogeneous
        # ELMFIS center/log-spread bounds.
        sampled_box=LOWER+SPAN*c2
        new[0]=food+np.where(c3<0.5,1.0,-1.0)*c1*sampled_box
        for i in range(1,POP_SIZE):
            new[i]=0.5*(x[i]+new[i-1])
        new=np.clip(new,LOWER,UPPER)
        nfit=common.population_fit(new,X,Y)
        improve=nfit<fit
        x[improve]=new[improve]; fit[improve]=nfit[improve]
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


def sma_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)
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
                if refit:
                    new[i]=np.clip(center+rng.normal(0,1,PARAM_DIM)*common.REFIT_SIGMA,LOWER,UPPER)
                else:
                    new[i]=rng.uniform(LOWER,UPPER,size=PARAM_DIM)
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
        fit=common.population_fit(x,X,Y)
        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


PHASE={"CS":cs_phase,"SCA":sca_phase,"SALP":salp_phase,"SMA":sma_phase}
SEED_BASE={"CS":178110,"SCA":188110,"SALP":198110,"SMA":208110}


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
        "CS":{"abandon_probability":0.25,"levy_scale":0.01},
        "SCA":{"r1_schedule":"2_to_0","trig":"sin_or_cos"},
        "SALP":{"c1_schedule":"2*exp(-(4t/T)^2)","leader_followers":True},
        "SMA":{"random_restart_prob":0.03,"adaptive_weights":True}
    }[method]
    out={
        "batch_id":"VW_MIDAS_ELMFIS_META_BATCH_5_V1",
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
    p=Path(f"vw_midas_elmfis_meta_batch_5_v1_{method.lower()}_result.json")
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"method":method,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--method",required=True,choices=sorted(PHASE))
    args=ap.parse_args()
    run_method(args.method)


if __name__=="__main__":
    main()
