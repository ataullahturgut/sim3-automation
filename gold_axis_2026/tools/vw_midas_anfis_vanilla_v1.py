from __future__ import annotations

import json, math, os
from pathlib import Path

import numpy as np
import psycopg
from sklearn.cluster import KMeans

import vw_midas_msvr_successor_v1 as base

DEV_START, DEV_END = "2022-04", "2024-12"
TR_START, TR_END = "2025-01", "2025-12"
ST_START, ST_END = "2026-01", "2026-07"

N_RULES = 5
KMEANS_N_INIT = 20
KMEANS_SEED = 1701
SPREAD_FLOOR = 0.20
SPREAD_CEIL = 5.0
EPOCHS = 50
LR_CENTER = 0.01
LR_LOGSPREAD = 0.005
GRAD_CLIP = 5.0
MIN_IMPROVEMENT = 1e-10


def arrays(samples, target):
    keys = sorted(k for k in samples if k < target)
    if len(keys) < 30:
        raise RuntimeError(f"TRAIN_TOO_SMALL {target} n={len(keys)}")
    X = np.stack([samples[k][0] for k in keys])
    Y = np.stack([samples[k][1] for k in keys])
    tx = samples[target][0][None, :]
    xm, xs = X.mean(0), X.std(0)
    ym, ys = Y.mean(0), Y.std(0)
    xs = np.where(xs < 1e-9, 1.0, xs)
    ys = np.where(ys < 1e-9, 1.0, ys)
    return keys, (X-xm)/xs, (Y-ym)/ys, (tx-xm)/xs, ym, ys


def init_premise(X):
    km=KMeans(n_clusters=N_RULES,n_init=KMEANS_N_INIT,random_state=KMEANS_SEED,algorithm="lloyd")
    labels=km.fit_predict(X)
    centers=np.asarray(km.cluster_centers_,float)
    gs=np.std(X,axis=0); gs=np.where(gs<1e-9,1.0,gs)
    spreads=np.empty_like(centers)
    for r in range(N_RULES):
        pts=X[labels==r]
        s=np.std(pts,axis=0) if len(pts)>=2 else gs.copy()
        spreads[r]=np.clip(s,SPREAD_FLOOR,SPREAD_CEIL)
    return centers, np.log(spreads), labels


def firing(X, centers, logspreads):
    spreads=np.exp(logspreads)
    z=(X[:,None,:]-centers[None,:,:])/spreads[None,:,:]
    # Canonical Gaussian: exp(-0.5 z^2), product AND in log space.
    logw=-0.5*np.sum(z*z,axis=2)
    logw-=np.max(logw,axis=1,keepdims=True)
    w=np.exp(logw)
    den=np.sum(w,axis=1,keepdims=True)
    den=np.where(den<1e-12,1.0,den)
    return w/den


def design(X, centers, logspreads):
    q=firing(X,centers,logspreads)
    basis=np.concatenate([np.ones((len(X),1)),X],axis=1)
    return (q[:,:,None]*basis[:,None,:]).reshape(len(X),-1)


def fit_consequents_lse(X,Y,centers,logspreads):
    H=design(X,centers,logspreads)
    beta, *_ = np.linalg.lstsq(H,Y,rcond=None)
    return beta


def consequent_values(X,beta):
    d=X.shape[1]
    b=beta.reshape(N_RULES,d+1,YDIM)
    basis=np.concatenate([np.ones((len(X),1)),X],axis=1)
    return np.einsum("nd,rdo->nro",basis,b)


def loss_and_grad(X,Y,centers,logspreads,beta):
    q=firing(X,centers,logspreads)
    fr=consequent_values(X,beta)
    yhat=np.sum(q[:,:,None]*fr,axis=1)
    err=yhat-Y
    loss=float(np.mean(err*err))

    # d yhat_o / d theta_rj = q_r (f_ro-yhat_o) d log(w_r)/d theta_rj
    delta=q[:,:,None]*(fr-yhat[:,None,:])
    # aggregate over outputs and observations
    influence=(2.0/(len(X)*Y.shape[1]))*np.einsum("no,nro->nr",err,delta)

    spreads=np.exp(logspreads)
    diff=X[:,None,:]-centers[None,:,:]
    dlogw_dc=diff/(spreads[None,:,:]**2)
    dlogw_dlogs=(diff*diff)/(spreads[None,:,:]**2)

    gc=np.einsum("nr,nrd->rd",influence,dlogw_dc)
    gs=np.einsum("nr,nrd->rd",influence,dlogw_dlogs)
    return loss,gc,gs,yhat


def clip_grad(g,limit):
    n=float(np.linalg.norm(g))
    return g if n<=limit or n<1e-15 else g*(limit/n)


def train_anfis(X,Y):
    global YDIM
    YDIM=Y.shape[1]
    centers,logs,labels=init_premise(X)
    best=(float("inf"),centers.copy(),logs.copy(),None,0)
    history=[]

    for epoch in range(EPOCHS):
        beta=fit_consequents_lse(X,Y,centers,logs)
        loss,gc,gs,_=loss_and_grad(X,Y,centers,logs,beta)
        history.append(loss)
        if loss+MIN_IMPROVEMENT < best[0]:
            best=(loss,centers.copy(),logs.copy(),beta.copy(),epoch)

        gc=clip_grad(gc,GRAD_CLIP); gs=clip_grad(gs,GRAD_CLIP)
        centers=centers-LR_CENTER*gc
        logs=logs-LR_LOGSPREAD*gs
        logs=np.clip(logs,math.log(SPREAD_FLOOR),math.log(SPREAD_CEIL))

    # Consequents must correspond exactly to the retained premise parameters.
    loss,bc,bl,_,be=best
    bb=fit_consequents_lse(X,Y,bc,bl)
    return bc,bl,bb,labels,{"best_epoch":int(be),"best_train_mse":float(loss),
                            "first_train_mse":float(history[0]),"last_train_mse":float(history[-1])}


def predict_target(samples,target):
    keys,X,Y,tx,ym,ys=arrays(samples,target)
    c,l,b,labels,diag=train_anfis(X,Y)
    pred_std=design(tx,c,l)@b
    pred=pred_std[0]*ys+ym
    counts=[int(np.sum(labels==r)) for r in range(N_RULES)]
    return pred,len(keys),counts,diag


def active_metrics(rows):
    m=dict(base.metrics(rows))
    actual=np.array([r["actual"] for r in rows],float)
    forecast=np.array([r["forecast"] for r in rows],float)
    ae=np.abs(forecast-actual)
    m["sum_abs_error"]=float(np.sum(ae))
    m["wape_pct"]=float(np.sum(ae)/np.sum(np.abs(actual))*100.0)
    m["direction_correct"]=int(sum(np.sign(r["forecast"]-r["rw"])==np.sign(r["actual"]-r["rw"]) for r in rows))
    return m


def yearly(rows):
    return {y:active_metrics([r for r in rows if r["target"].startswith(y)])
            for y in sorted({r["target"][:4] for r in rows})}


def evaluate(bundle,cache,start,end):
    rows=[]
    for target in base.month_range(start,end):
        pred,n,counts,diag=predict_target(cache[target],target)
        origin=base.month_shift(target,-1)
        rows.append({"target":target,"origin":origin,"train_rows":n,"rule_counts":counts,
                     "anfis_diag":diag,"pred_log_return_gold":float(pred[0]),
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
    cache={t:base.all_samples_at_origin(bundle,t,governed=True)
           for t in base.month_range(DEV_START,ST_END)}

    dev=evaluate(bundle,cache,DEV_START,DEV_END)
    tr=evaluate(bundle,cache,TR_START,TR_END)
    st=evaluate(bundle,cache,ST_START,ST_END)

    after=read_authority_invariants(dsn)
    if after!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out={
      "model_id":"VW_MIDAS_ANFIS_VANILLA_V1",
      "canonical_anfis":{
        "type":"first_order_Sugeno_ANFIS",
        "inputs":8,"outputs":4,"rules":N_RULES,
        "membership":"Gaussian_exp_minus_half_squared",
        "and_operator":"product_logspace","rule_normalization":True,
        "consequent":"first_order_TSK_linear",
        "consequent_learning":"ordinary_least_squares_each_forward_pass",
        "premise_learning":"analytic_gradient_descent_each_backward_pass",
        "epochs":EPOCHS,"lr_center":LR_CENTER,"lr_logspread":LR_LOGSPREAD,
        "gradient_clip":GRAD_CLIP,
        "initialization":"training_only_deterministic_kmeans_compact_rule_base",
        "spread_initialization":"within_rule_std_with_floor",
        "spread_floor":SPREAD_FLOOR,"spread_ceil":SPREAD_CEIL,
        "metaheuristic":"NONE"
      },
      "authority":{
        "database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
        "target":"NEXT_MONTH_AVERAGE_PRICE_VIA_4_RETURN_OUTPUTS",
        "random_split":"NONE","selection_period":f"{DEV_START}..{DEV_END}",
        "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
        "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
        "primary_metrics":["sum_abs_error","direction_accuracy_pct"],
        "target_month_in_training":False,
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after
      },
      "dev":{"metrics":active_metrics(dev),"yearly":yearly(dev),"rows":dev},
      "transport_2025":{"metrics":active_metrics(tr),"rows":tr},
      "stress_2026":{"metrics":active_metrics(st),"rows":st}
    }
    Path("vw_midas_anfis_vanilla_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"model_id":out["model_id"],"dev":out["dev"]["metrics"],
                      "transport_2025":out["transport_2025"]["metrics"],
                      "stress_2026":out["stress_2026"]["metrics"]},sort_keys=True))

if __name__=="__main__": main()
