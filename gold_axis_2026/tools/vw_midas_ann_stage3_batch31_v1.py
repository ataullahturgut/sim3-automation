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

HIDDEN_GRID=[3,4,6]
WD_GRID=[0.0,1e-4,1e-3]
POP=24
SELECT_GENS=45
REFIT_GENS=15
REPEATS=3
LO,HI=-2.0,2.0
MIN_VAL=6

def dim(h): return 13*h+4

def decode(theta,h):
    i=0
    W1=theta[i:i+8*h].reshape(8,h); i+=8*h
    b1=theta[i:i+h]; i+=h
    W2=theta[i:i+h*4].reshape(h,4); i+=h*4
    b2=theta[i:i+4]
    return W1,b1,W2,b2

def predict_std(theta,X,h):
    W1,b1,W2,b2=decode(theta,h)
    return np.tanh(X@W1+b1)@W2+b2

def mae_loss(theta,X,Y,h):
    p=predict_std(theta,X,h)
    return float(.7*np.mean(np.abs(p[:,0]-Y[:,0]))+.3*np.mean(np.abs(p-Y)))

def train_obj(theta,X,Y,h,wd):
    return mae_loss(theta,X,Y,h)+float(wd)*float(np.mean(np.asarray(theta)**2))

def split_xy(X,Y):
    nv=max(MIN_VAL,int(round(.2*len(X))))
    s=len(X)-nv
    if s<24: raise RuntimeError(f"INNER_TRAIN_TOO_SMALL n={len(X)} split={s}")
    return X[:s],Y[:s],X[s:],Y[s:]

def init_pop(rng,h,center=None):
    d=dim(h)
    if center is None:
        return rng.uniform(LO,HI,(POP,d))
    p=np.clip(np.asarray(center)[None,:]+rng.normal(0,.18,(POP,d)),LO,HI)
    p[0]=np.asarray(center)
    return p

def adaptive_pso_run(X,Y,h,wd,seed,gens,center=None):
    rng=np.random.default_rng(seed)
    x=init_pop(rng,h,center); v=np.zeros_like(x)
    fit=np.array([train_obj(z,X,Y,h,wd) for z in x])
    pbest=x.copy(); pfit=fit.copy()
    gi=int(np.argmin(pfit)); gbest=pbest[gi].copy(); gfit=float(pfit[gi])
    vmax=.4*(HI-LO)
    for t in range(gens):
        tau=t/max(1,gens-1)
        w=.9-.5*tau
        c1=2.5-2.0*tau
        c2=.5+2.0*tau
        for i in range(POP):
            r1=rng.random(dim(h)); r2=rng.random(dim(h))
            v[i]=w*v[i]+c1*r1*(pbest[i]-x[i])+c2*r2*(gbest-x[i])
            v[i]=np.clip(v[i],-vmax,vmax)
            x[i]=np.clip(x[i]+v[i],LO,HI)
            cf=train_obj(x[i],X,Y,h,wd)
            if cf<pfit[i]:
                pbest[i]=x[i].copy(); pfit[i]=cf
                if cf<gfit:
                    gbest=x[i].copy(); gfit=float(cf)
    return gbest,gfit

def adaptive_pso_select(X,Y,target):
    Xtr,Ytr,Xv,Yv=split_xy(X,Y)
    best=None; rows=[]
    seed0=407110+sum(map(ord,target))
    for h in HIDDEN_GRID:
        for wd in WD_GRID:
            for rep in range(REPEATS):
                seed=seed0+10000*h+1000*WD_GRID.index(wd)+97*rep
                theta,trfit=adaptive_pso_run(Xtr,Ytr,h,wd,seed,SELECT_GENS)
                val=mae_loss(theta,Xv,Yv,h)
                row={"hidden":h,"weight_decay":wd,"repeat":rep,"seed":seed,
                     "inner_train_objective":float(trfit),"inner_validation_fitness":float(val)}
                rows.append(row)
                cand=(val,h,wd,theta,rep)
                if best is None or cand[0]<best[0]: best=cand
    val,h,wd,theta,rep=best
    seed=seed0+900001+10000*h+1000*WD_GRID.index(wd)+97*rep
    final,full=adaptive_pso_run(X,Y,h,wd,seed,REFIT_GENS,center=theta)
    return final,float(val),float(full),h,wd,int(rep),rows

def tune_q(q):
    q=np.clip(q,[.3,.2,0,.5,0,0],[1.8,1.8,1,3,2,2])
    tg=float(q[0]); lg=float(q[1]); tfp=float(q[2]); decay=float(q[3])
    h=HIDDEN_GRID[int(round(q[4]))]
    wd=WD_GRID[int(round(q[5]))]
    return tg,lg,tfp,decay,h,wd

def itlbo_run(X,Y,q,seed,gens,center=None):
    tg,lg,tfp,decay,h,wd=tune_q(q)
    rng=np.random.default_rng(seed)
    P=init_pop(rng,h,center)
    F=np.array([train_obj(z,X,Y,h,wd) for z in P])
    for t in range(gens):
        tau=t/max(1,gens-1)
        local_tg=tg*(1-tau)**(1/decay)+.1
        local_lg=lg*(.5+.5*(1-tau))
        teacher=P[int(np.argmin(F))].copy(); mean=P.mean(0)
        tf=2 if rng.random()<tfp else 1
        for i in range(POP):
            cand=P[i]+local_tg*rng.random(dim(h))*(teacher-tf*mean)
            cand=np.clip(cand,LO,HI); cf=train_obj(cand,X,Y,h,wd)
            if cf<F[i]: P[i]=cand; F[i]=cf
        for i in range(POP):
            j=i
            while j==i: j=int(rng.integers(0,POP))
            direction=(P[i]-P[j]) if F[i]<F[j] else (P[j]-P[i])
            cand=P[i]+local_lg*rng.random(dim(h))*direction
            cand=np.clip(cand,LO,HI); cf=train_obj(cand,X,Y,h,wd)
            if cf<F[i]: P[i]=cand; F[i]=cf
        if (t+1)%10==0:
            best=P[int(np.argmin(F))].copy()
            for _ in range(2):
                wi=int(np.argmax(F))
                cand=np.clip(best+rng.normal(0,.05,dim(h)),LO,HI)
                cf=train_obj(cand,X,Y,h,wd)
                if cf<F[wi]: P[wi]=cand; F[wi]=cf
    i=int(np.argmin(F))
    return P[i].copy(),float(F[i]),h,wd,(tg,lg,tfp,decay)

def q_outer_score(q,Xtr,Ytr,Xv,Yv,seed):
    vals=[]
    for rep in range(2):
        theta,_,h,wd,_=itlbo_run(Xtr,Ytr,q,seed+97*rep,35)
        vals.append(mae_loss(theta,Xv,Yv,h))
    return float(np.mean(vals))

def tune_outer(Xtr,Ytr,Xv,Yv,seed):
    rng=np.random.default_rng(seed)
    lo=np.array([.3,.2,0,.5,0,0],float)
    hi=np.array([1.8,1.8,1,3,2,2],float)
    trials=[]
    for _ in range(6):
        q=rng.uniform(lo,hi)
        f=q_outer_score(q,Xtr,Ytr,Xv,Yv,seed+1000+len(trials))
        trials.append((f,q.copy()))
    trials.sort(key=lambda z:z[0])
    bestf,best=trials[0][0],trials[0][1].copy()
    for it in range(2):
        for k in range(4):
            scale=(hi-lo)*(.18/(it+1))
            q=np.clip(best+rng.normal(0,1,6)*scale,lo,hi)
            f=q_outer_score(q,Xtr,Ytr,Xv,Yv,seed+10000+it*100+k)
            trials.append((f,q.copy()))
            if f<bestf: bestf,best=float(f),q.copy()
    return best,float(bestf),[{"score":float(f),"q":[float(v) for v in q]} for f,q in trials]

def adaptive_tlbo_select(X,Y,target):
    Xtr,Ytr,Xv,Yv=split_xy(X,Y)
    seed0=707110+sum(map(ord,target))
    q,outer,trials=tune_outer(Xtr,Ytr,Xv,Yv,seed0)
    # after q is selected on chronological validation, choose one of three independent inner-train fits by validation
    candidates=[]
    for rep in range(REPEATS):
        theta,trfit,h,wd,p=itlbo_run(Xtr,Ytr,q,seed0+500000+97*rep,SELECT_GENS)
        val=mae_loss(theta,Xv,Yv,h)
        candidates.append((val,theta,trfit,h,wd,p,rep))
    candidates.sort(key=lambda z:z[0])
    val,theta,trfit,h,wd,p,rep=candidates[0]
    final,full,h2,wd2,p2=itlbo_run(X,Y,q,seed0+900001+97*rep,REFIT_GENS,center=theta)
    return final,float(val),float(full),h2,wd2,p2,int(rep),outer,trials,[
        {"repeat":int(z[6]),"inner_validation_fitness":float(z[0]),"inner_train_objective":float(z[2])}
        for z in candidates
    ]

def arrays(samples,target):
    return common.arrays(samples,target)

def predict_target(samples,target,method):
    keys,X,Y,tx,ym,ys,split=arrays(samples,target)
    if method=="ADAPTIVE_PSO":
        th,val,full,h,wd,rep,detail=adaptive_pso_select(X,Y,target)
        p=predict_std(th,tx,h)[0]*ys+ym
        meta={"selected_hidden":h,"selected_weight_decay":wd,"selected_repeat":rep,
              "inner_validation_fitness":val,"full_history_refit_objective":full,
              "selection_detail":detail}
    else:
        th,val,full,h,wd,params,rep,outer,trials,reps=adaptive_tlbo_select(X,Y,target)
        p=predict_std(th,tx,h)[0]*ys+ym
        meta={"selected_hidden":h,"selected_weight_decay":wd,"selected_repeat":rep,
              "selected_itlbo":{"teach_gain":params[0],"learn_gain":params[1],"tf2_probability":params[2],"decay":params[3]},
              "outer_validation_score":outer,"inner_validation_fitness":val,
              "full_history_refit_objective":full,"outer_trials":trials,"repeat_validation":reps}
    return p,len(keys),meta

def evaluate(bundle,cache,method,start,end):
    rows=[]
    for target in base.month_range(start,end):
        p,n,meta=predict_target(cache[target],target,method); origin=base.month_shift(target,-1)
        rows.append({"target":target,"origin":origin,"method":method,"train_rows":n,**meta,
                     "pred_log_return_gold":float(p[0]),
                     "forecast":float(bundle.core_gold[origin]*math.exp(float(p[0]))),
                     "actual":float(bundle.core_gold[target]),"rw":float(bundle.core_gold[origin])})
    return rows

def invariants(dsn):
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
    for method in ("ADAPTIVE_PSO","ADAPTIVE_TLBO"):
        dev=evaluate(bundle,cache,method,DEV_START,DEV_END)
        tr=evaluate(bundle,cache,method,TR_START,TR_END)
        st=evaluate(bundle,cache,method,ST_START,ST_END)
        results[method]={
            "dev":{"metrics":base.metrics(dev),"yearly":base.yearly(dev),"rows":dev},
            "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
            "stress_2026":{"metrics":base.metrics(st),"rows":st}}
    after=invariants(dsn)
    if after!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={
      "batch_id":"VW_MIDAS_ANN_STAGE3_BATCH31_V1",
      "method":{
        "ann":"direct all-weight optimization, tanh hidden, linear 4-output",
        "hidden_grid":HIDDEN_GRID,"weight_decay_grid":WD_GRID,
        "adaptive_pso":{"w":"0.9->0.4","c1":"2.5->0.5","c2":"0.5->2.5","vmax":1.6},
        "adaptive_tlbo":{"outer_tuned":["teach_gain","learn_gain","tf2_probability","decay","hidden","weight_decay"]},
        "population":POP,"selection_generations":SELECT_GENS,"refit_generations":REFIT_GENS,"repeats":REPEATS},
      "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
        "random_validation":"NONE","target_month_in_fitness":False,
        "inner_validation":"chronological final 20pct pre-target history",
        "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
        "authority_invariants_before":bundle.invariants_before,"authority_invariants_after":after},
      "models":results}
    Path("vw_midas_ann_stage3_batch31_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({m:{"dev":results[m]["dev"]["metrics"],"transport_2025":results[m]["transport_2025"]["metrics"],"stress_2026":results[m]["stress_2026"]["metrics"]} for m in results},sort_keys=True))

if __name__=="__main__": main()
