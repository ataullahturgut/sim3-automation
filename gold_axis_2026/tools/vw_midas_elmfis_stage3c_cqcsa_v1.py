from __future__ import annotations

import json, math, os
from pathlib import Path
import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as elmfis
import vw_midas_elmfis_meta_batch_1_v1 as common

DEV_START,DEV_END=common.DEV_START,common.DEV_END
TR_START,TR_END=common.TR_START,common.TR_END
ST_START,ST_END=common.ST_START,common.ST_END

POP=common.POP_SIZE
GENS=common.SELECT_GENS
REFIT=common.REFIT_GENS
REPEATS=common.REPEATS
D=common.PARAM_DIM
LO,HI=common.LOWER,common.UPPER
SPAN=HI-LO
AP=0.10
FL=2.0
N_CLUSTERS=4

def quasi_opposite(x,rng):
    # Das et al. Eq. 15 adapted coordinate-wise to bounded ELMFIS antecedent space:
    # X_QO ~ U((a+b)/2, a+b-X), with interval endpoints ordered.
    midpoint=(LO+HI)/2.0
    opposite=LO+HI-x
    low=np.minimum(midpoint,opposite)
    high=np.maximum(midpoint,opposite)
    return rng.uniform(low,high)

def cluster_labels(x,fit):
    # Project adaptation of the paper's fitness-weighted cluster/leader idea.
    # Crows are ordered by fitness-derived weights and split into balanced groups;
    # the best member in each group is its leader.
    order=np.argsort(fit)
    groups=np.array_split(order,N_CLUSTERS)
    labels=np.empty(len(x),dtype=int)
    leaders=[]
    for k,g in enumerate(groups):
        labels[g]=k
        leaders.append(int(g[np.argmin(fit[g])]))
    return labels,np.array(leaders,dtype=int)

def cqcsa_phase(X,Y,seed,generations,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center,refit=refit)
    mem=x.copy()
    fit=common.population_fit(x,X,Y)
    mfit=fit.copy()
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(mem,mfit,X,Y,Xv,Yv,vbest,vfit)

    trace=[]
    for t in range(generations):
        labels,leaders=cluster_labels(mem,mfit)
        new=x.copy()
        n_quasi=int(round(rng.random() * max(0,generations-(t+1))))
        n_quasi=min(n_quasi,POP)

        for i in range(POP):
            leader=int(leaders[labels[i]])
            if leader==i and len(leaders)>1:
                leader=int(leaders[int(rng.integers(0,len(leaders)))])
            if rng.random()>=AP:
                # cluster leader-following exploitation (paper Phase 1)
                target=mem[leader]
                cand=x[i]+rng.random(D)*FL*(target-x[i])
            else:
                # paper Phase 2 replaces blind random move with quasi-opposition.
                cand=quasi_opposite(x[i],rng)
                if refit:
                    cand=0.70*cand+0.30*(center+rng.normal(0,1,D)*common.REFIT_SIGMA)
            new[i]=np.clip(cand,LO,HI)

        nfit=common.population_fit(new,X,Y)
        x,fit=new,nfit

        improve=fit<mfit
        mem[improve]=x[improve]
        mfit[improve]=fit[improve]

        # Iteration-dependent replacement of worst crows by quasi-opposite crows
        # following Das et al. Eq. 16 concept.
        if n_quasi>0:
            worst=np.argsort(mfit)[-n_quasi:]
            for i in worst:
                qo=np.clip(quasi_opposite(mem[i],rng),LO,HI)
                qf=common.training_loss(qo,X,Y)
                if qf<mfit[i]:
                    mem[i]=qo; mfit[i]=qf
                    x[i]=qo; fit[i]=qf

        if Xv is not None:
            vbest,vfit=common.validation_pick(mem,mfit,X,Y,Xv,Yv,vbest,vfit)
        trace.append({
            "generation":t+1,
            "quasi_replacements_requested":int(n_quasi),
            "best_train_fitness":float(np.min(mfit)),
        })

    bi=int(np.argmin(mfit))
    return (vbest if Xv is not None else mem[bi].copy()),(vfit if Xv is not None else float(mfit[bi])),trace

def select_refit(X,Y,split,target):
    Xtr,Ytr,Xv,Yv=X[:split],Y[:split],X[split:],Y[split:]
    anchor=common.initial_theta(Xtr)
    target_seed=sum(map(ord,target))
    best=None; reps=[]
    for rep in range(REPEATS):
        seed=987110+1009*rep+target_seed
        th,val,trace=cqcsa_phase(Xtr,Ytr,seed,GENS,anchor,Xv,Yv,False)
        reps.append({"repeat":rep,"seed":seed,"inner_validation_fitness":float(val),
                     "final_generation_best_train":trace[-1]["best_train_fitness"]})
        if best is None or val<best[0]:
            best=(float(val),th.copy(),rep)
    val,th,rep=best
    seed=987110+900001+1009*rep+target_seed
    final,full,trace=cqcsa_phase(X,Y,seed,REFIT,th,None,None,True)
    return final,val,float(full),int(rep),reps,trace

def predict_target(samples,target):
    keys,X,Y,tx,ym,ys,split=common.arrays(samples,target)
    th,val,full,rep,reps,trace=select_refit(X,Y,split,target)
    pred_std=common.predict_with_fit(th,X,Y,tx)[0]
    pred=pred_std*ys+ym
    centers,spreads=common.decode(th)
    return pred,len(keys),{
        "selected_repeat":rep,
        "inner_validation_fitness":val,
        "full_history_refit_fitness":full,
        "repeat_validation":reps,
        "refit_trace":trace,
        "antecedent_min_spread":float(np.min(spreads)),
        "antecedent_max_spread":float(np.max(spreads)),
        "antecedent_max_abs_center":float(np.max(np.abs(centers))),
    }

def evaluate(bundle,cache,start,end):
    rows=[]
    for target in base.month_range(start,end):
        pred,n,meta=predict_target(cache[target],target)
        origin=base.month_shift(target,-1)
        rows.append({"target":target,"origin":origin,"method":"CQCSA","train_rows":n,**meta,
                     "pred_log_return_gold":float(pred[0]),
                     "forecast":float(bundle.core_gold[origin]*math.exp(float(pred[0]))),
                     "actual":float(bundle.core_gold[target]),"rw":float(bundle.core_gold[origin])})
    return rows

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    dev=evaluate(b,cache,DEV_START,DEV_END)
    tr=evaluate(b,cache,TR_START,TR_END)
    st=evaluate(b,cache,ST_START,ST_END)
    after=read_invariants(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={
      "batch_id":"VW_MIDAS_ELMFIS_STAGE3C_CQCSA_V1",
      "model_id":"VW_MIDAS_CQCSA_ELMFIS_V1",
      "method":"CQCSA",
      "authority_note":"Project adaptation of Das, Sahu & Janghel (Resources Policy 79, 2022, 103109); not claimed as exact source-code reproduction.",
      "literature_reference":{"doi":"10.1016/j.resourpol.2022.103109","title":"Oil and gold price prediction using optimized fuzzy inference system based extreme learning machine"},
      "cqcsa_contract":{
        "population":POP,"selection_generations":GENS,"refit_generations":REFIT,"repeats":REPEATS,
        "awareness_probability":AP,"flight_length":FL,"clusters":N_CLUSTERS,
        "cluster_rule":"fitness-ordered balanced clusters; best member is leader",
        "quasi_opposition":"uniform between search midpoint and opposite point coordinate-wise",
        "worst_replacement_count":"round(U[0,1]*(itermax-it)), clipped to population",
        "scope":"ELMFIS antecedent centers + log-spreads only"
      },
      "canonical_elmfis":{"inputs":common.INPUTS,"outputs":common.OUTPUTS,"rules":common.RULES,
                          "consequent_fit":"analytic_ridge_per_candidate","ridge_alpha":elmfis.RIDGE_ALPHA},
      "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
                   "random_validation":"NONE","target_month_in_fitness":False,
                   "selection_period":f"{DEV_START}..{DEV_END}",
                   "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
                   "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
                   "authority_invariants_before":b.invariants_before,"authority_invariants_after":after},
      "dev":{"metrics":elmfis.active_metrics(dev),"yearly":elmfis.yearly(dev),"rows":dev},
      "transport_2025":{"metrics":elmfis.active_metrics(tr),"rows":tr},
      "stress_2026":{"metrics":elmfis.active_metrics(st),"rows":st}
    }
    Path("vw_midas_elmfis_stage3c_cqcsa_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"method":"CQCSA","dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))

if __name__=="__main__": main()
