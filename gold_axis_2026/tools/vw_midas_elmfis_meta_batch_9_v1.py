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


def de_abc_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(x,X,Y)
    trials=np.zeros(POP_SIZE,dtype=int)
    F,CR,limit=.7,.9,10
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    for _ in range(generations):
        # DE phase
        for i in range(POP_SIZE):
            idx=[j for j in range(POP_SIZE) if j!=i]
            a,b,c=rng.choice(idx,3,replace=False)
            mutant=np.clip(x[a]+F*(x[b]-x[c]),LOWER,UPPER)
            mask=rng.random(PARAM_DIM)<CR
            mask[int(rng.integers(0,PARAM_DIM))]=True
            cand=np.where(mask,mutant,x[i])
            cf=common.training_loss(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i],trials[i]=cand,cf,0
            else:
                trials[i]+=1

        # ABC employed/onlooker phase
        q=1/(1+fit)
        probs=q/q.sum()
        for _b in range(POP_SIZE):
            i=int(rng.choice(POP_SIZE,p=probs))
            k=i
            while k==i:
                k=int(rng.integers(0,POP_SIZE))
            j=int(rng.integers(0,PARAM_DIM))
            phi=float(rng.uniform(-1,1))
            cand=x[i].copy()
            cand[j]=np.clip(x[i,j]+phi*(x[i,j]-x[k,j]),LOWER[j],UPPER[j])
            cf=common.training_loss(cand,X,Y)
            if cf<fit[i]:
                x[i],fit[i],trials[i]=cand,cf,0
            else:
                trials[i]+=1

        for i in range(POP_SIZE):
            if trials[i]>=limit:
                if refit:
                    cand=center+rng.normal(0,1,PARAM_DIM)*common.REFIT_SIGMA
                    x[i]=np.clip(cand,LOWER,UPPER)
                else:
                    x[i]=rng.uniform(LOWER,UPPER,size=PARAM_DIM)
                fit[i]=common.training_loss(x[i],X,Y)
                trials[i]=0

        if Xv is not None:
            vbest,vfit=common.validation_pick(x,fit,X,Y,Xv,Yv,vbest,vfit)

    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))


def multiswarm_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    swarms=3
    per=POP_SIZE//swarms
    xs=[]
    sigma=common.REFIT_SIGMA if refit else 0.18*SPAN

    for s in range(swarms):
        sw=np.empty((per,PARAM_DIM),float)
        if refit:
            sw[:]=np.clip(np.asarray(center)[None,:]+rng.normal(0,1,(per,PARAM_DIM))*sigma,LOWER,UPPER)
            if s==0:
                sw[0]=np.asarray(center)
        else:
            n_local=max(1,per//2)
            sw[:n_local]=np.clip(np.asarray(center)[None,:]+rng.normal(0,1,(n_local,PARAM_DIM))*(0.18*SPAN),LOWER,UPPER)
            sw[n_local:]=rng.uniform(LOWER,UPPER,size=(per-n_local,PARAM_DIM))
            if s==0:
                sw[0]=np.asarray(center)
        xs.append(sw)

    fits=[common.population_fit(sw,X,Y) for sw in xs]
    vel=[np.zeros_like(sw) for sw in xs]
    pbest=[sw.copy() for sw in xs]
    pfit=[f.copy() for f in fits]

    vbest,vfit=None,math.inf
    if Xv is not None:
        pool=np.vstack(pbest); pf=np.concatenate(pfit)
        vbest,vfit=common.validation_pick(pool,pf,X,Y,Xv,Yv,vbest,vfit)

    for t in range(generations):
        gbests=[]; gfits=[]
        for s in range(swarms):
            i=int(np.argmin(pfit[s]))
            gbests.append(pbest[s][i].copy())
            gfits.append(float(pfit[s][i]))
        global_best=gbests[int(np.argmin(gfits))].copy()
        w=.9-.5*t/max(1,generations-1)

        for s in range(swarms):
            for i in range(per):
                r1=rng.random(PARAM_DIM); r2=rng.random(PARAM_DIM); r3=rng.random(PARAM_DIM)
                vel[s][i]=(
                    w*vel[s][i]
                    +1.4*r1*(pbest[s][i]-xs[s][i])
                    +1.2*r2*(gbests[s]-xs[s][i])
                    +.4*r3*(global_best-xs[s][i])
                )
                xs[s][i]=np.clip(xs[s][i]+vel[s][i],LOWER,UPPER)
                cf=common.training_loss(xs[s][i],X,Y)
                if cf<pfit[s][i]:
                    pbest[s][i]=xs[s][i].copy()
                    pfit[s][i]=cf

        if (t+1)%10==0:
            order=np.argsort(gfits)
            src=gbests[order[0]].copy()
            for s in order[1:]:
                wi=int(np.argmax(pfit[s]))
                perturb=common.REFIT_SIGMA if refit else 0.05*SPAN
                xs[s][wi]=np.clip(src+rng.normal(0,1,PARAM_DIM)*perturb,LOWER,UPPER)
                pbest[s][wi]=xs[s][wi].copy()
                pfit[s][wi]=common.training_loss(xs[s][wi],X,Y)

        if Xv is not None:
            pool=np.vstack(pbest); pf=np.concatenate(pfit)
            vbest,vfit=common.validation_pick(pool,pf,X,Y,Xv,Yv,vbest,vfit)

    allb=[]; allf=[]
    for s in range(swarms):
        i=int(np.argmin(pfit[s]))
        allb.append(pbest[s][i]); allf.append(float(pfit[s][i]))
    j=int(np.argmin(allf))
    return (vbest if Xv is not None else allb[j].copy()),(vfit if Xv is not None else allf[j])


PHASE={"DE_ABC":de_abc_phase,"MULTISWARM":multiswarm_phase}
SEED_BASE={"DE_ABC":328110,"MULTISWARM":338110}


def select_and_refit(method,X,Y,split,target):
    fn=PHASE[method]
    Xtr,Ytr,Xv,Yv=X[:split],Y[:split],X[split:],Y[split:]
    base_theta=common.initial_theta(Xtr)
    best_theta,best_val,best_rep=None,math.inf,None
    reps=[]
    target_seed=sum(map(ord,target))

    for rep in range(REPEATS):
        seed=SEED_BASE[method]+1009*rep+target_seed
        theta,vfit=fn(Xtr,Ytr,seed,SELECT_GENS,base_theta,Xv,Yv,False)
        reps.append({"repeat":rep,"seed":seed,"inner_validation_fitness":float(vfit)})
        if vfit<best_val:
            best_theta,best_val,best_rep=theta.copy(),float(vfit),rep

    refit_seed=SEED_BASE[method]+900001+1009*int(best_rep)+target_seed
    final_theta,full_fit=fn(X,Y,refit_seed,REFIT_GENS,best_theta,None,None,True)
    return final_theta,best_val,float(full_fit),int(best_rep),reps


def predict_target(samples,target,method):
    keys,X,Y,tx,ym,ys,split=common.arrays(samples,target)
    theta,valfit,fullfit,rep,reps=select_and_refit(method,X,Y,split,target)
    pred_std=common.predict_with_fit(theta,X,Y,tx)[0]
    pred=pred_std*ys+ym
    centers,spreads=common.decode(theta)
    return pred,len(keys),valfit,fullfit,rep,reps,float(np.min(spreads)),float(np.max(spreads)),float(np.max(np.abs(centers)))


def evaluate(bundle,cache,method,start,end):
    rows=[]
    for target in base.month_range(start,end):
        pred,n,valfit,fullfit,rep,reps,min_spread,max_spread,max_abs_center=predict_target(cache[target],target,method)
        origin=base.month_shift(target,-1)
        rows.append({
            "target":target,"origin":origin,"method":method,"train_rows":n,
            "selected_repeat":rep,"inner_validation_fitness":valfit,
            "full_history_refit_fitness":fullfit,"repeat_validation":reps,
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
        "DE_ABC":{"F":0.7,"CR":0.9,"scout_limit":10},
        "MULTISWARM":{"swarms":3,"per_swarm":8,"elite_exchange_every":10}
    }[method]

    out={
        "batch_id":"VW_MIDAS_ELMFIS_META_BATCH_9_V1",
        "model_id":f"VW_MIDAS_{method}_ELMFIS_V1",
        "method":method,
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
    p=Path(f"vw_midas_elmfis_meta_batch_9_v1_{method.lower()}_result.json")
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"method":method,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--method",required=True,choices=sorted(PHASE))
    args=ap.parse_args()
    run_method(args.method)


if __name__=="__main__":
    main()
