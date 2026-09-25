from __future__ import annotations
import json,math,os
from pathlib import Path
import numpy as np, psycopg
import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as eb

DEV_START,DEV_END="2022-04","2024-12"
TR_START,TR_END="2025-01","2025-12"
ST_START,ST_END="2026-01","2026-07"
R=5; EPOCHS=100; K0=.01; KINC=1.1; KDEC=.9
SFLOOR=.20; SCEIL=5.0; YDIM=4

def fire(X,c,l):
    s=np.exp(l); z=(X[:,None,:]-c[None,:,:])/s[None,:,:]
    a=-.5*np.sum(z*z,2); a-=a.max(1,keepdims=True)
    w=np.exp(a); return w/np.maximum(w.sum(1,keepdims=True),1e-12)

def design(X,c,l):
    q=fire(X,c,l); b=np.c_[np.ones(len(X)),X]
    return (q[:,:,None]*b[:,None,:]).reshape(len(X),-1)

def lse(X,Y,c,l):
    return np.linalg.lstsq(design(X,c,l),Y,rcond=None)[0]

def rule_outputs(X,beta):
    b=beta.reshape(R,X.shape[1]+1,YDIM); a=np.c_[np.ones(len(X)),X]
    return np.einsum("nd,rdo->nro",a,b)

def loss_grad(X,Y,c,l,beta):
    q=fire(X,c,l); fr=rule_outputs(X,beta); yh=(q[:,:,None]*fr).sum(1)
    e=yh-Y; loss=float(np.mean(e*e))
    infl=(2/(len(X)*Y.shape[1]))*np.einsum("no,nro->nr",e,q[:,:,None]*(fr-yh[:,None,:]))
    s=np.exp(l); d=X[:,None,:]-c[None,:,:]
    gc=np.einsum("nr,nrd->rd",infl,d/(s[None,:,:]**2))
    gl=np.einsum("nr,nrd->rd",infl,(d*d)/(s[None,:,:]**2))
    return loss,gc,gl

def train(X,Y):
    global YDIM; YDIM=Y.shape[1]
    c,s,labels=eb.fit_antecedents(X); l=np.log(np.clip(s,SFLOOR,SCEIL))
    best=(float("inf"),c.copy(),l.copy(),0); hist=[]; k=K0; ks=[]
    for ep in range(EPOCHS):
        beta=lse(X,Y,c,l); loss,gc,gl=loss_grad(X,Y,c,l,beta)
        hist.append(loss); ks.append(k)
        if loss<best[0]-1e-12: best=(loss,c.copy(),l.copy(),ep)
        g=np.r_[gc.ravel(),gl.ravel()]; gn=float(np.linalg.norm(g))
        if np.isfinite(gn) and gn>1e-15:
            eta=k/gn; c-=eta*gc; l-=eta*gl
            l=np.clip(l,math.log(SFLOOR),math.log(SCEIL))
        if len(hist)>=5:
            dif=np.diff(hist[-5:]); sig=np.sign(dif)
            if np.all(dif<0): k*=KINC
            elif np.all(sig[:-1]*sig[1:]<0): k*=KDEC
    loss,c,l,ep=best; beta=lse(X,Y,c,l)
    return c,l,beta,labels,{"best_epoch":ep,"first_train_mse":hist[0],
        "best_train_mse":loss,"last_train_mse":hist[-1],
        "initial_step_size":K0,"final_step_size":ks[-1],"min_step_size":min(ks),"max_step_size":max(ks)}

def predict(samples,target):
    keys,X,Y,tx,ym,ys=eb.arrays(samples,target)
    c,l,b,labels,d=train(X,Y)
    p=(design(tx,c,l)@b)[0]*ys+ym
    return p,len(keys),[int((labels==r).sum()) for r in range(R)],d

def eval_period(bundle,cache,start,end):
    rows=[]
    for t in base.month_range(start,end):
        p,n,counts,d=predict(cache[t],t); o=base.month_shift(t,-1)
        rows.append({"target":t,"origin":o,"train_rows":n,"rule_counts":counts,"anfis_diag":d,
          "pred_log_return_gold":float(p[0]),"forecast":float(bundle.core_gold[o]*math.exp(float(p[0]))),
          "actual":float(bundle.core_gold[t]),"rw":float(bundle.core_gold[o])})
    return rows

def invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on"); return base.authority_invariants(cur)

def main():
    dsn=os.environ["NEON_DATABASE_URL"]; bundle=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in base.month_range(DEV_START,ST_END)}
    dev=eval_period(bundle,cache,DEV_START,DEV_END); tr=eval_period(bundle,cache,TR_START,TR_END); st=eval_period(bundle,cache,ST_START,ST_END)
    after=invariants(dsn)
    if after!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    out={"model_id":"VW_MIDAS_ANFIS_VANILLA_V2",
      "canonical_anfis":{"type":"first_order_Sugeno_ANFIS_project_multioutput_adaptation","inputs":8,"outputs":4,"rules":R,
       "membership":"Gaussian","consequent_learning":"LSE_each_forward_pass",
       "premise_learning":"Jang1993_normalized_gradient_backward_pass","epochs":EPOCHS,
       "initial_step_size":K0,"step_increase":KINC,"step_decrease":KDEC,
       "step_rule":"4_downs_x1.1; two alternating up/down combinations_x0.9",
       "initialization":"training_only_deterministic_kmeans","metaheuristic":"NONE"},
      "authority":{"database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
       "random_split":"NONE","selection_period":f"{DEV_START}..{DEV_END}",
       "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
       "target_month_in_training":False,"invariants_before":bundle.invariants_before,"invariants_after":after},
      "dev":{"metrics":eb.active_metrics(dev),"yearly":eb.yearly(dev),"rows":dev},
      "transport_2025":{"metrics":eb.active_metrics(tr),"rows":tr},
      "stress_2026":{"metrics":eb.active_metrics(st),"rows":st}}
    Path("vw_midas_anfis_vanilla_v2_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("OUTPUT_GATE=PASS"); print(json.dumps({"dev":out["dev"]["metrics"],"transport_2025":out["transport_2025"]["metrics"],"stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))
if __name__=="__main__": main()
