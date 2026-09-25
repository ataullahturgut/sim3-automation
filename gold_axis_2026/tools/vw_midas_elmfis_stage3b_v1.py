from __future__ import annotations

import argparse, json, math, os
from pathlib import Path
import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_meta_batch_1_v1 as common

DEV_START,DEV_END=common.DEV_START,common.DEV_END
TR_START,TR_END=common.TR_START,common.TR_END
ST_START,ST_END=common.ST_START,common.ST_END

POP=common.POP_SIZE
GENS=common.SELECT_GENS
REFIT=common.REFIT_GENS
REPEATS=common.REPEATS
LO,HI=common.LOWER,common.UPPER
D=common.PARAM_DIM

def levy(rng,shape,beta=1.5):
    sigma=(math.gamma(1+beta)*math.sin(math.pi*beta/2)/(math.gamma((1+beta)/2)*beta*2**((beta-1)/2)))**(1/beta)
    u=rng.normal(0,sigma,size=shape); v=rng.normal(0,1,size=shape)
    return u/(np.abs(v)**(1/beta)+1e-12)

def mpa_proposals(pop,fit,t,T,rng):
    elite=pop[int(np.argmin(fit))].copy()
    P=.5; FADs=.2
    cf=(1-(t+1)/T)**(2*(t+1)/T)
    cand=pop.copy()
    if (t+1)<=T/3:
        RB=rng.normal(0,1,size=pop.shape)
        for i in range(POP):
            step=RB[i]*(elite-RB[i]*pop[i])
            cand[i]=pop[i]+P*rng.random(D)*step
    elif (t+1)<=2*T/3:
        RL=.05*levy(rng,pop.shape); RB=rng.normal(0,1,size=pop.shape)
        half=POP//2
        for i in range(POP):
            if i<half:
                step=RL[i]*(elite-RL[i]*pop[i])
                cand[i]=pop[i]+P*rng.random(D)*step
            else:
                step=RB[i]*(RB[i]*elite-pop[i])
                cand[i]=elite+P*cf*step
    else:
        RL=.05*levy(rng,pop.shape)
        for i in range(POP):
            step=RL[i]*(RL[i]*elite-pop[i])
            cand[i]=elite+P*cf*step
    cand=np.clip(cand,LO,HI)
    if rng.random()<FADs:
        U=(rng.random(cand.shape)<FADs).astype(float)
        cand=cand+cf*(LO+rng.random(cand.shape)*(HI-LO))*U
    else:
        r=rng.random(); i1,i2=rng.permutation(POP),rng.permutation(POP)
        cand=cand+(FADs*(1-r)+r)*(cand[i1]-cand[i2])
    return np.clip(cand,LO,HI)

def sca_proposals(pop,fit,t,T,rng):
    best=pop[int(np.argmin(fit))].copy()
    r1=2-2*t/max(1,T-1)
    out=np.empty_like(pop)
    for i in range(POP):
        r2=2*np.pi*rng.random(D); r3=2*rng.random(D); r4=rng.random(D)
        trig=np.where(r4<.5,np.sin(r2),np.cos(r2))
        out[i]=pop[i]+r1*trig*np.abs(r3*best-pop[i])
    return np.clip(out,LO,HI)

def tournament(rng,pop,fit,k=3):
    idx=rng.choice(len(pop),size=k,replace=False)
    return pop[idx[np.argmin(fit[idx])]].copy()

def ga_proposals(pop,fit,t,T,rng):
    elite=np.argsort(fit)[:2]
    new=[pop[i].copy() for i in elite]
    sigma=max(.04,.22*(1-t/max(1,T-1)))
    while len(new)<POP:
        p1=tournament(rng,pop,fit); p2=tournament(rng,pop,fit)
        if rng.random()<.85:
            a=rng.random(D); c1=a*p1+(1-a)*p2; c2=a*p2+(1-a)*p1
        else:
            c1,c2=p1.copy(),p2.copy()
        for c in (c1,c2):
            mask=rng.random(D)<.08
            if np.any(mask): c[mask]+=rng.normal(0,sigma,size=int(mask.sum()))
            new.append(np.clip(c,LO,HI))
            if len(new)>=POP: break
    return np.stack(new)

def cpa_proposals(pop,fit,t,T,rng):
    best=pop[int(np.argmin(fit))].copy()
    scale=1-t/max(1,T-1)
    out=np.empty_like(pop)
    for i in range(POP):
        j=int(rng.integers(0,POP))
        if rng.random()<.5:
            cand=pop[i]+rng.random(D)*(best-pop[i])+scale*rng.random(D)*(pop[j]-pop[i])
        else:
            cand=best+scale*rng.normal(0,1,D)*np.abs(best-pop[i])
        if rng.random()<.05:
            cand=rng.uniform(LO,HI,D)
        out[i]=np.clip(cand,LO,HI)
    return out

def second_proposals(kind,pop,fit,t,T,rng):
    if kind=="SCA": return sca_proposals(pop,fit,t,T,rng)
    if kind=="GA": return ga_proposals(pop,fit,t,T,rng)
    if kind=="CPA": return cpa_proposals(pop,fit,t,T,rng)
    raise ValueError(kind)

def hybrid_phase(X,Y,seed,generations,second,center,Xv=None,Yv=None,refit=False):
    rng=np.random.default_rng(seed)
    pop=common.init_population(rng,center,refit=refit)
    fit=common.population_fit(pop,X,Y)
    vbest,vfit=None,math.inf
    if Xv is not None:
        vbest,vfit=common.validation_pick(pop,fit,X,Y,Xv,Yv,vbest,vfit)

    totals={"INCUMBENT":0,"MPA":0,second:0}
    trace=[]

    for t in range(generations):
        mpa=mpa_proposals(pop,fit,t,generations,rng)
        mfit=common.population_fit(mpa,X,Y)

        sec=second_proposals(second,pop,fit,t,generations,rng)
        sfit=common.population_fit(sec,X,Y)

        pool=np.vstack([pop,mpa,sec])
        pfit=np.concatenate([fit,mfit,sfit])
        src=np.array(["INCUMBENT"]*POP+["MPA"]*POP+[second]*POP,dtype=object)
        keep=np.argsort(pfit)[:POP]
        kept=src[keep]
        counts={k:int(np.sum(kept==k)) for k in totals}
        for k,v in counts.items(): totals[k]+=v
        trace.append({"generation":t+1,**counts})

        pop=pool[keep].copy(); fit=pfit[keep].copy()
        if Xv is not None:
            vbest,vfit=common.validation_pick(pop,fit,X,Y,Xv,Yv,vbest,vfit)

    bi=int(np.argmin(fit))
    theta=vbest if Xv is not None else pop[bi].copy()
    score=vfit if Xv is not None else float(fit[bi])
    denom=max(1,generations*POP)
    shares={k:float(v/denom) for k,v in totals.items()}
    return theta,score,shares,trace

def select_refit(X,Y,split,target,method):
    Xtr,Ytr,Xv,Yv=X[:split],Y[:split],X[split:],Y[split:]
    second={"MPA_SCA":"SCA","MPA_GA":"GA","MPA_CPA":"CPA"}[method]
    base_seed={"MPA_SCA":417110,"MPA_GA":427110,"MPA_CPA":437110}[method]
    anchor=common.initial_theta(Xtr)

    best=None; reps=[]
    for rep in range(REPEATS):
        seed=base_seed+1009*rep+sum(map(ord,target))
        th,val,shares,_=hybrid_phase(Xtr,Ytr,seed,GENS,second,anchor,Xv,Yv,False)
        reps.append({"repeat":rep,"seed":seed,"inner_validation_fitness":float(val),"survivor_shares":shares})
        if best is None or val<best[0]:
            best=(float(val),th.copy(),rep,shares)

    val,th,rep,select_shares=best
    seed=base_seed+900001+1009*rep+sum(map(ord,target))
    final,full,refit_shares,_=hybrid_phase(X,Y,seed,REFIT,second,th,None,None,True)
    return final,val,float(full),int(rep),reps,select_shares,refit_shares

def predict_target(samples,target,method):
    keys,X,Y,tx,ym,ys,split=common.arrays(samples,target)
    th,val,full,rep,reps,sel_shares,refit_shares=select_refit(X,Y,split,target,method)
    pred_std=common.predict_with_fit(th,X,Y,tx)[0]
    pred=pred_std*ys+ym
    return pred,len(keys),{
        "selected_repeat":rep,
        "inner_validation_fitness":val,
        "full_history_refit_fitness":full,
        "repeat_validation":reps,
        "selected_repeat_survivor_shares":sel_shares,
        "refit_survivor_shares":refit_shares,
    }

def evaluate(bundle,cache,method,start,end):
    rows=[]
    for target in base.month_range(start,end):
        pred,n,meta=predict_target(cache[target],target,method)
        origin=base.month_shift(target,-1)
        rows.append({"target":target,"origin":origin,"method":method,"train_rows":n,**meta,
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
    ap=argparse.ArgumentParser()
    ap.add_argument("--method",required=True,choices=["MPA_SCA","MPA_GA","MPA_CPA"])
    args=ap.parse_args()

    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")

    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}

    dev=evaluate(b,cache,args.method,DEV_START,DEV_END)
    tr=evaluate(b,cache,args.method,TR_START,TR_END)
    st=evaluate(b,cache,args.method,ST_START,ST_END)

    after=read_invariants(dsn)
    if after!=b.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out={
      "batch_id":"VW_MIDAS_ELMFIS_STAGE3B_V1",
      "method":args.method,
      "hybrid_contract":{
        "type":"competitive operator portfolio on one shared population",
        "selection_rule":"incumbent + MPA proposal population + second-optimizer proposal population; keep best 24 by inner-training weighted MAE",
        "operator_share":"implicit training-only survivor competition",
        "population":POP,"selection_generations":GENS,"refit_generations":REFIT,"repeats":REPEATS,
        "MPA":{"FADs":0.2,"P":0.5,"phases":"Brownian/transition/Levy"}
      },
      "authority":{
        "database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
        "random_validation":"NONE","target_month_in_fitness":False,
        "selection_period":f"{DEV_START}..{DEV_END}",
        "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
        "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
        "authority_invariants_before":b.invariants_before,"authority_invariants_after":after},
      "dev":{"metrics":common.elmfis.active_metrics(dev),"yearly":common.elmfis.yearly(dev),"rows":dev},
      "transport_2025":{"metrics":common.elmfis.active_metrics(tr),"rows":tr},
      "stress_2026":{"metrics":common.elmfis.active_metrics(st),"rows":st}
    }

    p=Path(f"vw_midas_elmfis_stage3b_v1_{args.method.lower()}_result.json")
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"method":args.method,"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))

if __name__=="__main__":
    main()
