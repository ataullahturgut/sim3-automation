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
POP_SIZE=common.POP_SIZE
SELECT_GENS=common.SELECT_GENS
REFIT_GENS=common.REFIT_GENS
REPEATS=common.REPEATS
LOWER,UPPER=common.LOWER,common.UPPER
PARAM_DIM=common.PARAM_DIM

def levy(rng,shape,beta=1.5):
    sigma=(math.gamma(1+beta)*math.sin(math.pi*beta/2)/(math.gamma((1+beta)/2)*beta*2**((beta-1)/2)))**(1/beta)
    u=rng.normal(0,sigma,size=shape); v=rng.normal(0,1,size=shape)
    return u/(np.abs(v)**(1/beta)+1e-12)

def krill_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    N=np.zeros_like(x); Fd=np.zeros_like(x); dt=.5
    vbest,vfit=None,math.inf
    if Xv is not None: vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for t in range(generations):
        order=np.argsort(fit); best=x[order[0]].copy()
        new=np.empty_like(x)
        for i in range(POP_SIZE):
            d=np.linalg.norm(x-x[i],axis=1)
            neigh=np.argsort(d)[1:min(5,POP_SIZE)]
            local=np.mean(x[neigh],axis=0) if len(neigh) else best
            N[i]=.6*N[i]+.8*((local-x[i])+(best-x[i]))
            Fd[i]=.5*Fd[i]+.8*(best-x[i])*(1-t/max(1,generations-1))
            diffusion=.01*(1-t/max(1,generations))*rng.normal(0,1,PARAM_DIM)
            cand=x[i]+dt*(N[i]+Fd[i])+diffusion
            if rng.random()<.05: cand += rng.uniform(-1,1,PARAM_DIM)*.05*(UPPER-LOWER)
            new[i]=np.clip(cand,LOWER,UPPER)
        x=new; fit=np.array([common.weighted_mae(z,X,Y) for z in x])
        if Xv is not None: vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))

def crow_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    mem=x.copy()
    fit=np.array([common.weighted_mae(z,X,Y) for z in x]); mfit=fit.copy()
    fl,ap=2.0,.1
    vbest,vfit=None,math.inf
    if Xv is not None: vbest,vfit=common.validation_pick(mem,mfit,Xv,Yv,vbest,vfit)
    for _ in range(generations):
        for i in range(POP_SIZE):
            j=i
            while j==i: j=int(rng.integers(0,POP_SIZE))
            if rng.random()>ap:
                cand=x[i]+rng.random(PARAM_DIM)*fl*(mem[j]-x[i])
            else:
                cand=rng.uniform(LOWER,UPPER,PARAM_DIM)
            cand=np.clip(cand,LOWER,UPPER); cf=common.weighted_mae(cand,X,Y)
            x[i]=cand; fit[i]=cf
            if cf<mfit[i]: mem[i]=cand; mfit[i]=cf
        if Xv is not None: vbest,vfit=common.validation_pick(mem,mfit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(mfit))
    return (vbest if Xv is not None else mem[bi].copy()),(vfit if Xv is not None else float(mfit[bi]))

def fa_fpa_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    beta0=1.0; gamma=1.0/PARAM_DIM; alpha=.2
    vbest,vfit=None,math.inf
    if Xv is not None: vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for _ in range(generations):
        order=np.argsort(fit); best=x[order[0]].copy()
        for i in range(1,POP_SIZE):
            j=int(order[rng.integers(0,max(1,POP_SIZE//3))])
            r2=np.mean((x[i]-x[j])**2); beta=beta0*np.exp(-gamma*r2)
            cand=x[i]+beta*(x[j]-x[i])+alpha*rng.normal(0,1,PARAM_DIM)
            cand=np.clip(cand,LOWER,UPPER); cf=common.weighted_mae(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
        for i in range(POP_SIZE):
            if rng.random()<.75:
                cand=x[i]+.01*levy(rng,(PARAM_DIM,))*(best-x[i])
            else:
                j,k=rng.choice(POP_SIZE,2,replace=False)
                cand=x[i]+rng.random()*(x[j]-x[k])
            cand=np.clip(cand,LOWER,UPPER); cf=common.weighted_mae(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf
        alpha*=.97
        if Xv is not None: vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))

def de_abc_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    x=common.init_population(rng,center)
    fit=np.array([common.weighted_mae(z,X,Y) for z in x])
    trials=np.zeros(POP_SIZE,dtype=int); F=.7; CR=.9; limit=10
    vbest,vfit=None,math.inf
    if Xv is not None: vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    for _ in range(generations):
        for i in range(POP_SIZE):
            idx=[j for j in range(POP_SIZE) if j!=i]
            a,b,c=rng.choice(idx,3,replace=False)
            mutant=np.clip(x[a]+F*(x[b]-x[c]),LOWER,UPPER)
            mask=rng.random(PARAM_DIM)<CR; mask[rng.integers(0,PARAM_DIM)]=True
            cand=np.where(mask,mutant,x[i]); cf=common.weighted_mae(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf; trials[i]=0
            else: trials[i]+=1
        q=1/(1+fit); probs=q/q.sum()
        for _b in range(POP_SIZE):
            i=int(rng.choice(POP_SIZE,p=probs)); k=i
            while k==i: k=int(rng.integers(0,POP_SIZE))
            j=int(rng.integers(0,PARAM_DIM)); phi=rng.uniform(-1,1)
            cand=x[i].copy(); cand[j]=x[i,j]+phi*(x[i,j]-x[k,j])
            cand=np.clip(cand,LOWER,UPPER); cf=common.weighted_mae(cand,X,Y)
            if cf<fit[i]: x[i]=cand; fit[i]=cf; trials[i]=0
            else: trials[i]+=1
        for i in range(POP_SIZE):
            if trials[i]>=limit:
                x[i]=rng.uniform(LOWER,UPPER,PARAM_DIM); fit[i]=common.weighted_mae(x[i],X,Y); trials[i]=0
        if Xv is not None: vbest,vfit=common.validation_pick(x,fit,Xv,Yv,vbest,vfit)
    bi=int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()),(vfit if Xv is not None else float(fit[bi]))

def multiswarm_phase(X,Y,seed,generations,center=None,Xv=None,Yv=None):
    rng=np.random.default_rng(seed)
    swarms=3; per=POP_SIZE//swarms
    xs=[]
    for s in range(swarms):
        if center is None:
            sw=rng.uniform(LOWER,UPPER,(per,PARAM_DIM))
        else:
            sw=np.clip(np.asarray(center)[None,:]+rng.normal(0,.18,(per,PARAM_DIM)),LOWER,UPPER)
            if s==0: sw[0]=np.asarray(center)
        xs.append(sw)
    fits=[np.array([common.weighted_mae(z,X,Y) for z in sw]) for sw in xs]
    vel=[np.zeros_like(sw) for sw in xs]
    pbest=[sw.copy() for sw in xs]; pfit=[f.copy() for f in fits]
    vbest,vfit=None,math.inf
    if Xv is not None:
        pool=np.vstack(pbest); pf=np.concatenate(pfit)
        vbest,vfit=common.validation_pick(pool,pf,Xv,Yv,vbest,vfit)
    for t in range(generations):
        gbests=[]; gfits=[]
        for s in range(swarms):
            i=int(np.argmin(pfit[s])); gbests.append(pbest[s][i].copy()); gfits.append(float(pfit[s][i]))
        global_best=gbests[int(np.argmin(gfits))].copy()
        w=.9-.5*t/max(1,generations-1)
        for s in range(swarms):
            for i in range(per):
                r1=rng.random(PARAM_DIM); r2=rng.random(PARAM_DIM); r3=rng.random(PARAM_DIM)
                vel[s][i]=w*vel[s][i]+1.4*r1*(pbest[s][i]-xs[s][i])+1.2*r2*(gbests[s]-xs[s][i])+.4*r3*(global_best-xs[s][i])
                xs[s][i]=np.clip(xs[s][i]+vel[s][i],LOWER,UPPER)
                cf=common.weighted_mae(xs[s][i],X,Y)
                if cf<pfit[s][i]: pbest[s][i]=xs[s][i].copy(); pfit[s][i]=cf
        if (t+1)%10==0:
            order=np.argsort(gfits); src=gbests[order[0]].copy()
            for s in order[1:]:
                wi=int(np.argmax(pfit[s]))
                xs[s][wi]=np.clip(src+rng.normal(0,.05,PARAM_DIM),LOWER,UPPER)
                pbest[s][wi]=xs[s][wi].copy(); pfit[s][wi]=common.weighted_mae(xs[s][wi],X,Y)
        if Xv is not None:
            pool=np.vstack(pbest); pf=np.concatenate(pfit)
            vbest,vfit=common.validation_pick(pool,pf,Xv,Yv,vbest,vfit)
    allb=[]; allf=[]
    for s in range(swarms):
        i=int(np.argmin(pfit[s])); allb.append(pbest[s][i]); allf.append(float(pfit[s][i]))
    j=int(np.argmin(allf))
    return (vbest if Xv is not None else allb[j].copy()),(vfit if Xv is not None else allf[j])

PHASE={"KRILL":krill_phase,"CROW":crow_phase,"FA_FPA":fa_fpa_phase,"DE_ABC":de_abc_phase,"MULTISWARM":multiswarm_phase}
SEED_BASE={"KRILL":307110,"CROW":317110,"FA_FPA":327110,"DE_ABC":337110,"MULTISWARM":347110}

def select_and_refit(method,X,Y,split,target):
    fn=PHASE[method]
    Xtr,Ytr,Xv,Yv=X[:split],Y[:split],X[split:],Y[split:]
    best_theta,best_val,best_rep=None,math.inf,None; reps=[]
    target_seed=sum(map(ord,target))
    for rep in range(REPEATS):
        seed=SEED_BASE[method]+1009*rep+target_seed
        theta,vfit=fn(Xtr,Ytr,seed,SELECT_GENS,center=None,Xv=Xv,Yv=Yv)
        reps.append({"repeat":rep,"seed":seed,"inner_validation_fitness":float(vfit)})
        if vfit<best_val: best_theta,best_val,best_rep=theta.copy(),float(vfit),rep
    refit_seed=SEED_BASE[method]+900001+1009*int(best_rep)+target_seed
    final_theta,full_fit=fn(X,Y,refit_seed,REFIT_GENS,center=best_theta,Xv=None,Yv=None)
    return final_theta,best_val,float(full_fit),int(best_rep),reps

def predict_target(samples,target,method):
    keys,X,Y,tx,ym,ys,split=common.arrays(samples,target)
    theta,valfit,fullfit,rep,reps=select_and_refit(method,X,Y,split,target)
    pred=common.ann_predict(theta,tx)[0]*ys+ym
    return pred,len(keys),valfit,fullfit,rep,reps

def evaluate(bundle,cache,method,start,end):
    rows=[]
    for target in base.month_range(start,end):
        pred,n,valfit,fullfit,rep,reps=predict_target(cache[target],target,method)
        origin=base.month_shift(target,-1)
        rows.append({"target":target,"origin":origin,"method":method,"train_rows":n,
                     "selected_repeat":rep,"inner_validation_fitness":valfit,
                     "full_history_refit_fitness":fullfit,"repeat_validation":reps,
                     "pred_log_return_gold":float(pred[0]),
                     "forecast":float(bundle.core_gold[origin]*math.exp(float(pred[0]))),
                     "actual":float(bundle.core_gold[target]),"rw":float(bundle.core_gold[origin])})
    return rows

def read_authority_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    results={}
    for method in ("KRILL","CROW","FA_FPA","DE_ABC","MULTISWARM"):
        dev=evaluate(bundle,cache,method,DEV_START,DEV_END)
        tr=evaluate(bundle,cache,method,TR_START,TR_END)
        st=evaluate(bundle,cache,method,ST_START,ST_END)
        results[method]={
            "model_id":f"VW_MIDAS_{method}_ANN_V1",
            "dev":{"metrics":base.metrics(dev),"yearly":base.yearly(dev),"rows":dev},
            "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
            "stress_2026":{"metrics":base.metrics(st),"rows":st}}
    after=read_authority_invariants(dsn)
    if after!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={
        "batch_id":"VW_MIDAS_ANN_META_BATCH_8_V1",
        "canonical_ann":{"input_units":common.INPUTS,"hidden_layers":[common.HIDDEN],"hidden_activation":common.ACTIVATION,
                         "output_units":common.OUTPUTS,"output_activation":"linear","optimized_parameters":common.PARAM_DIM},
        "optimization_contract":{"scope":"all_ann_weights_and_biases","bounds":[LOWER,UPPER],"population_reference":POP_SIZE,
          "selection_generations":SELECT_GENS,"full_history_refit_generations":REFIT_GENS,
          "deterministic_repeats_per_target":REPEATS,"inner_split":"chronological_last_20pct_training_history_min_6",
          "population_evolution_objective":"0.7*Gold_standardized_MAE + 0.3*all_output_standardized_MAE on inner-training",
          "selection_fitness":"same weighted MAE on chronological validation tail; top-quartile train candidates only",
          "refit":"warm-start from validation-selected theta; optimize on all pre-target history","target_month_in_fitness":False},
        "method_parameters":{
          "KRILL":{"dt":0.5,"neighbor_count":4,"restart_prob":0.05},
          "CROW":{"flight_length":2.0,"awareness_probability":0.1},
          "FA_FPA":{"firefly_alpha0":0.2,"alpha_decay":0.97,"fpa_global_prob":0.75},
          "DE_ABC":{"F":0.7,"CR":0.9,"scout_limit":10},
          "MULTISWARM":{"swarms":3,"per_swarm":8,"elite_exchange_every":10}},
        "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
          "random_validation":"NONE","selection_period":f"{DEV_START}..{DEV_END}",
          "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
          "source_checks":bundle.source_checks,"authority_invariants_before":bundle.invariants_before,"authority_invariants_after":after},
        "models":results}
    Path("vw_midas_ann_meta_batch_8_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({m:{"dev":results[m]["dev"]["metrics"],"transport_2025":results[m]["transport_2025"]["metrics"],"stress_2026":results[m]["stress_2026"]["metrics"]} for m in results},sort_keys=True))

if __name__=="__main__": main()
