from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pywt
from scipy.optimize import minimize
from scipy.special import expit
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
AURORAP=AX/"tools"/"gold_session_aurora_v1_20261007.py"
M05P=AX/"tools"/"gold_session_model05b_structural_iris_1h_feature_selection_20261007.py"
OUT=AX/"SESSION_PRISM_V1_OUT";OUT.mkdir(exist_ok=True)

LAMBDA_GRID=[1.0,10.0,50.0]
LATENT_COLS=[f"wv_{i:02d}" for i in range(16)]+["log_rv48","jump48"]
MIN_TRAIN=80

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

aur=loadmod("session_aurora",AURORAP)
m05=loadmod("m05",M05P)

def metric(y,p):
    y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "up_actual":int((y==1).sum()),
        "up_correct":int(((y==1)&(pred==1)).sum()),
        "down_actual":int((y==0).sum()),
        "down_correct":int(((y==0)&(pred==0)).sum()),
    }

def logit(p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    return np.log(p/(1-p))

def paa4(x):
    x=np.asarray(x,float)
    if len(x)!=48:raise ValueError(len(x))
    return x.reshape(4,12).mean(axis=1)

def wavelet_latent(rets):
    r=np.asarray(rets,float)
    if len(r)!=48 or not np.isfinite(r).all():raise ValueError("BAD_48_RETURNS")
    rv=float(np.sqrt(np.sum(r*r)))
    rn=r/(rv+1e-12)
    coeffs=pywt.swt(rn,"db2",level=3,trim_approx=False,norm=True)
    arrays=[coeffs[0][0]]+[pair[1] for pair in coeffs]
    latent=[]
    for arr in arrays:
        latent.extend(paa4(arr).tolist())
    jump=float(np.max(np.abs(r))/(rv+1e-12))
    latent.extend([math.log(rv+1e-12),jump])
    return np.asarray(latent,float)

def fresh_aurora():
    ledger=aur.sentry.load_ledger()
    rows=[]
    for (part,win),g in ledger.groupby(["partition","window"],sort=True):
        pred,_=aur.run_window(g[g.year.isin([2023,2024,2025])].copy())
        if not pred.empty:rows.append(pred)
    return pd.concat(rows,ignore_index=True).sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def attach_latent(panel):
    x15=m05.load_xau15_extended()
    h=m05.load_xau1h(x15).copy().sort_values("available_at_utc").reset_index(drop=True)
    h["logp"]=np.log(h.value.astype(float))
    av=h.available_at_utc.astype("int64").to_numpy()
    logp=h.logp.to_numpy(float)

    rows=[]
    missing=[]
    for r in panel.itertuples(index=False):
        t=pd.Timestamp(r.start_utc)
        # strict available_at < session start
        j=int(np.searchsorted(av,t.value,side="left")-1)
        if j<48:
            missing.append(str(t));continue
        vals=logp[j-48:j+1]
        if len(vals)!=49 or not np.isfinite(vals).all():
            missing.append(str(t));continue
        z=wavelet_latent(np.diff(vals))
        row={k:getattr(r,k) for k in panel.columns}
        row["hourly_anchor_available"]=h.iloc[j].available_at_utc
        for i,v in enumerate(z):row[LATENT_COLS[i]]=float(v)
        rows.append(row)
    q=pd.DataFrame(rows)
    if q.empty:raise RuntimeError("PRISM_NO_LATENT_ROWS")
    if not (q.hourly_anchor_available<q.start_utc).all():
        raise RuntimeError("PRISM_TIME_LEAK")
    return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True),missing

def build_panel():
    return attach_latent(fresh_aurora())

def standardize(tr,te):
    X=tr[LATENT_COLS].astype(float).to_numpy()
    T=te[LATENT_COLS].astype(float).to_numpy()
    mu=X.mean(axis=0);sd=X.std(axis=0,ddof=0);sd=np.where(sd>1e-8,sd,1.0)
    return (X-mu)/sd,(T-mu)/sd

def fit_offset(X,y,offset,lam):
    X=np.asarray(X,float);y=np.asarray(y,float);offset=np.asarray(offset,float)
    def fg(beta):
        eta=offset+X@beta
        loss=np.sum(np.logaddexp(0.0,eta)-y*eta)+0.5*lam*np.dot(beta,beta)
        pr=expit(eta)
        grad=X.T@(pr-y)+lam*beta
        return float(loss),grad
    init=np.zeros(X.shape[1],float)
    res=minimize(lambda b:fg(b)[0],init,jac=lambda b:fg(b)[1],
                 method="L-BFGS-B",options={"maxiter":1000,"ftol":1e-12})
    if not res.success:raise RuntimeError(f"PRISM_OPT_FAIL {res.message}")
    return res.x

def walk_forward(g,lam,years):
    g=g.sort_values("start_utc").reset_index(drop=True)
    test=g[g.year.isin(years)].copy()
    test["month_key"]=test.start_utc.dt.to_period("M").astype(str)
    rows=[]
    for mo in sorted(test.month_key.unique()):
        te=test[test.month_key.eq(mo)].copy()
        if te.empty:continue
        cutoff=te.start_utc.min()
        tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)].copy()
        if len(tr)<MIN_TRAIN or tr.y_up.nunique()<2:continue
        X,T=standardize(tr,te)
        beta=fit_offset(X,tr.y_up.to_numpy(int),logit(tr.p_aurora),lam)
        pp=expit(logit(te.p_aurora)+T@beta)
        for r,p in zip(te.itertuples(index=False),pp):
            rows.append({
                "partition":r.partition,"window":r.window,"label_date":r.label_date,
                "start_utc":r.start_utc,"end_utc":r.end_utc,"year":int(r.year),
                "y_up":int(r.y_up),"p_aurora":float(r.p_aurora),
                "p_prism":float(p),"lambda":float(lam),"train_n":int(len(tr))
            })
    return pd.DataFrame(rows)

def paired(g):
    ma=metric(g.y_up,g.p_aurora);mp=metric(g.y_up,g.p_prism)
    ad=(g.p_aurora>=.5).astype(int);pd_=(g.p_prism>=.5).astype(int);y=g.y_up.astype(int)
    ch=ad.ne(pd_)
    rescue=int((ch&ad.ne(y)&pd_.eq(y)).sum())
    broken=int((ch&ad.eq(y)&pd_.ne(y)).sum())
    return ma,mp,{
        "changed_calls":int(ch.sum()),"rescued":rescue,"broken":broken,"net_rescue":rescue-broken
    }

def select_lambda(g):
    rows=[];preds={}
    for lam in LAMBDA_GRID:
        z=walk_forward(g,lam,[2023,2024])
        if z.empty:
            rows.append({"lambda":lam,"eligible":False,"reason":"NO_DEV_PREDICTIONS"})
            continue
        preds[lam]=z
        ma,mp,x=paired(z)
        eligible=(
            x["changed_calls"]>0 and x["net_rescue"]>0 and
            mp["balanced_accuracy"]+1e-12>=ma["balanced_accuracy"] and
            mp["brier"]<=ma["brier"]+.003+1e-12
        )
        reason="PASS" if eligible else "DEV_GATE"
        rows.append({
            "lambda":lam,"eligible":eligible,"reason":reason,
            "n":len(z),"aurora_accuracy":ma["accuracy"],"prism_accuracy":mp["accuracy"],
            "aurora_ba":ma["balanced_accuracy"],"prism_ba":mp["balanced_accuracy"],
            "aurora_brier":ma["brier"],"prism_brier":mp["brier"],
            "prism_up_recall":mp["up_recall"],"prism_down_recall":mp["down_recall"],**x
        })
    tab=pd.DataFrame(rows)
    elig=tab[tab.eligible.eq(True)].copy() if "eligible" in tab.columns else pd.DataFrame()
    if elig.empty:return tab,None,preds
    elig=elig.sort_values(
        ["prism_ba","prism_accuracy","prism_brier","lambda"],
        ascending=[False,False,True,True]
    )
    return tab,float(elig.iloc[0].lambda),preds

def summarize(g,period):
    rows=[]
    for (part,win),z in g.groupby(["partition","window"],sort=True):
        ma,mp,x=paired(z)
        rows.append({
            "period":period,"partition":part,"window":win,
            "lambda":float(z["lambda"].iloc[0]),**x,
            **{f"aurora_{k}":v for k,v in ma.items()},
            **{f"prism_{k}":v for k,v in mp.items()}
        })
    return pd.DataFrame(rows)

def main():
    panel,missing=build_panel()
    selections=[];dev_parts=[];selected={}
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        tab,lam,preds=select_lambda(g)
        for r in tab.to_dict("records"):
            selections.append({"partition":part,"window":win,**r})
        if lam is not None:
            selected[(part,win)]=lam
            dev_parts.append(preds[lam])
    sel=pd.DataFrame(selections)
    dev=pd.concat(dev_parts,ignore_index=True) if dev_parts else pd.DataFrame()

    tr_parts=[]
    for (part,win),lam in selected.items():
        g=panel[(panel.partition==part)&(panel.window==win)].copy()
        z=walk_forward(g,lam,[2025])
        if not z.empty:tr_parts.append(z)
    tr=pd.concat(tr_parts,ignore_index=True) if tr_parts else pd.DataFrame(columns=dev.columns)

    panel.to_csv(OUT/"latent_panel.csv",index=False)
    sel.to_csv(OUT/"selection_grid.csv",index=False)
    dev.to_csv(OUT/"dev_predictions.csv",index=False)
    if not dev.empty:summarize(dev,"DEV_2023_2024").to_csv(OUT/"dev_metrics.csv",index=False)
    else:pd.DataFrame().to_csv(OUT/"dev_metrics.csv",index=False)
    tr.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    if not tr.empty:summarize(tr,"FROZEN_2025").to_csv(OUT/"transport_2025_metrics.csv",index=False)
    else:pd.DataFrame().to_csv(OUT/"transport_2025_metrics.csv",index=False)

    summary={
        "status":"SESSION_PRISM_V1_COMPLETE",
        "architecture":{"wavelet":"db2","level":3,"latent_dim":18,"returns":48,
                        "lambda_grid":LAMBDA_GRID,"min_train":MIN_TRAIN},
        "selected_heads":[{"partition":p,"window":w,"lambda":lam} for (p,w),lam in sorted(selected.items())],
        "selection_grid":sel.to_dict("records"),
        "transport_2025_metrics":summarize(tr,"FROZEN_2025").to_dict("records") if not tr.empty else [],
        "latent_missing_rows":len(missing),
        "guardrails":[
            "Fresh session AURORA only.",
            "48 active completed hourly returns strictly before session start.",
            "Lambda selected only from 2023-2024 development.",
            "No 2025 retuning.",
            "No 2026 outcome opened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION PRISM V1 — RESULT","",
           "## Development lambda selection","",
           "| Partition | Window | Lambda | N | AURORA BA | PRISM BA | PRISM UP | PRISM DOWN | Changed | Rescue | Break | Net | Eligible |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in sel.itertuples(index=False):
        if not hasattr(r,"n") or pd.isna(getattr(r,"n",np.nan)):
            continue
        lines.append(
            f"| {r.partition} | {r.window} | {r.lambda_ if hasattr(r,'lambda_') else getattr(r,'_2',r[2])} | "
            f"{int(r.n)} | {100*r.aurora_ba:.2f}% | {100*r.prism_ba:.2f}% | "
            f"{100*r.prism_up_recall:.2f}% | {100*r.prism_down_recall:.2f}% | "
            f"{int(r.changed_calls)} | {int(r.rescued)} | {int(r.broken)} | {int(r.net_rescue):+d} | {r.eligible} |"
        )
    lines+=["","## Frozen 2025 transport",""]
    if tr.empty:
        lines.append("No PRISM session head passed development; 2025 remained closed.")
    else:
        tm=summarize(tr,"FROZEN_2025")
        lines+=["| Partition | Window | Lambda | N | AURORA BA | PRISM BA | PRISM UP | PRISM DOWN | AURORA Brier | PRISM Brier | Changed | Net rescue |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for r in tm.itertuples(index=False):
            lines.append(
                f"| {r.partition} | {r.window} | {r.lambda_ if hasattr(r,'lambda_') else getattr(r,'_3',r[3])} | "
                f"{int(r.prism_n)} | {100*r.aurora_balanced_accuracy:.2f}% | "
                f"{100*r.prism_balanced_accuracy:.2f}% | {100*r.prism_up_recall:.2f}% | "
                f"{100*r.prism_down_recall:.2f}% | {r.aurora_brier:.4f} | {r.prism_brier:.4f} | "
                f"{int(r.changed_calls)} | {int(r.net_rescue):+d} |"
            )
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print((OUT/"result.md").read_text())

if __name__=="__main__":
    main()
