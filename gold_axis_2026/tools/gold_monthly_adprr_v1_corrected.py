#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import warnings
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import vw_midas_msvr_successor_v1 as base
import gold_monthly_challenger_b_pls1_v1 as pls

MODEL_ID="GOLD_MONTHLY_ADPRR_V1_CORRECTED"
SEED=20261001
TRAIN_START="2010-05"
CAL_WINDOW=36
REL_A=3.0
REL_B=3.0
RECENT_N=60
ANALOG_K=15
ANALOG_PSEUDO=10.0
STRONG_RECALL_TOL=0.05
PRICE_AE_TOL=0.02
THRESHOLDS=(0.02,0.05,0.08,0.12,0.16,0.20,0.25)
DEV_START,DEV_END="2022-04","2024-12"
HOLD_START,HOLD_END="2025-01","2025-12"
STRESS_START,STRESS_END="2026-01","2026-07"

REFS={
 "ChHHO_ANFIS":{"dev_sumae":1413.0297794084559,"dev_direction_correct":23},
 "DE_ABC_RBFNN":{"dev_sumae":1415.8371290308862,"dev_direction_correct":25},
 "FULL7_ANN":{"dev_sumae":1428.8589858125417,"dev_direction_correct":22},
 "REDUCED4_ANN":{"dev_sumae":1431.4587,"dev_direction_correct":24},
}

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def long_en():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=.30,penalty="elasticnet",l1_ratio=.50,solver="saga",
            class_weight="balanced",max_iter=5000,tol=1e-4,random_state=SEED
        ))
    ])

def recent_l2():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=1.0,penalty="l2",solver="lbfgs",class_weight="balanced",
            max_iter=3000,random_state=SEED
        ))
    ])

def history_samples(bundle,target):
    origin=base.month_shift(target,-1)
    gh=bundle.gpr_vintages.get(origin)
    if gh is None:
        raise RuntimeError(f"GPR_ORIGIN_VINTAGE_MISSING {origin}")
    out={}
    for t in base.month_range(TRAIN_START,origin):
        try:
            out[t]=base.sample_for_target(bundle,t,gh,True)
        except RuntimeError:
            continue
    if len(out)<72:
        raise RuntimeError(f"HISTORY_TOO_SHORT target={target} n={len(out)}")
    xt=pls.current8_x_only(bundle,target,gh)
    return out,xt,gh

def xy(samples,keys):
    X=np.stack([samples[k][0] for k in keys])
    y=np.asarray([1 if float(samples[k][1][0])>0 else 0 for k in keys],int)
    return X,y

def analog_predict(samples,keys,x):
    X,y=xy(samples,keys)
    mu=X.mean(0); sd=X.std(0); sd=np.where(sd>1e-12,sd,1.0)
    Z=(X-mu)/sd; z=(x-mu)/sd
    d=np.sqrt(np.mean((Z-z)**2,axis=1))
    k=min(ANALOG_K,len(keys))
    idx=np.argpartition(d,k-1)[:k]
    dd=d[idx]
    pos=dd[dd>0]
    scale=float(np.median(pos)) if len(pos) else 1.0
    if not np.isfinite(scale) or scale<=1e-12: scale=1.0
    w=np.exp(-dd/scale)
    prior=float(y.mean())
    local=float(np.sum(w*y[idx])/np.sum(w)) if float(np.sum(w))>0 else prior
    eff=float(np.sum(w))
    return float((eff*local+ANALOG_PSEUDO*prior)/(eff+ANALOG_PSEUDO))

def expert_predict(samples,train_keys,x):
    if len(train_keys)<48:
        raise RuntimeError(f"EXPERT_TRAIN_TOO_SHORT n={len(train_keys)}")
    X,y=xy(samples,train_keys)
    if len(np.unique(y))<2:
        p=float(y.mean())
        return {"LONG_EN":p,"RECENT60_L2":p,"LOCAL_ANALOG":p}
    m1=long_en(); m1.fit(X,y); p1=float(m1.predict_proba(np.asarray(x).reshape(1,-1))[0,1])
    rk=train_keys[-RECENT_N:]
    Xr,yr=xy(samples,rk)
    if len(np.unique(yr))<2:
        p2=float(yr.mean())
    else:
        m2=recent_l2(); m2.fit(Xr,yr); p2=float(m2.predict_proba(np.asarray(x).reshape(1,-1))[0,1])
    p3=analog_predict(samples,train_keys,np.asarray(x,float))
    return {"LONG_EN":p1,"RECENT60_L2":p2,"LOCAL_ANALOG":p3}

def pseudo_pls(samples,bundle,u):
    allkeys=sorted(k for k in samples if k<u)
    if len(allkeys)<48:
        raise RuntimeError(f"PSEUDO_PLS_HISTORY_SHORT target={u} n={len(allkeys)}")
    tr=allkeys[:-12]; va=allkeys[-12:]
    Xtr=np.stack([samples[k][0] for k in tr])
    ytr=np.asarray([float(samples[k][1][0]) for k in tr],float)
    Xv=np.stack([samples[k][0] for k in va])
    prev=np.asarray([float(bundle.core_gold[base.month_shift(k,-1)]) for k in va])
    actual=np.asarray([float(bundle.core_gold[k]) for k in va])
    denom=max(float(np.abs(prev-actual).sum()),1e-12)
    scored=[]
    for nc in pls.COMPONENTS:
        pred,_,wc,_=pls.predict_return(Xtr,ytr,Xv,nc)
        fc=prev*np.exp(pred)
        sae=float(np.abs(fc-actual).sum())
        scored.append((sae/denom,int(nc),int(wc)))
    scored.sort(key=lambda x:(x[0],x[1]))
    nc=scored[0][1]
    Xa=np.stack([samples[k][0] for k in allkeys])
    ya=np.asarray([float(samples[k][1][0]) for k in allkeys],float)
    xu=np.asarray(samples[u][0],float).reshape(1,-1)
    pred,_,_,_=pls.predict_return(Xa,ya,xu,nc)
    return float(pred[0]),int(nc)

def calibration_ledger(bundle,target,samples):
    keys=sorted(samples)
    cal=keys[-CAL_WINDOW:]
    rows=[]
    for u in cal:
        train_keys=[k for k in keys if k<u]
        if len(train_keys)<48: continue
        r_pls,nc=pseudo_pls(samples,bundle,u)
        p=expert_predict(samples,train_keys,samples[u][0])
        y=1 if float(samples[u][1][0])>0 else 0
        rw=float(bundle.core_gold[base.month_shift(u,-1)])
        actual=float(bundle.core_gold[u])
        rows.append({
            "target":u,"y_up":y,"rw":rw,"actual":actual,"r_pls":r_pls,"ncomp":nc,
            **{f"p_{k}":v for k,v in p.items()}
        })
    q=pd.DataFrame(rows)
    if len(q)<30:
        raise RuntimeError(f"CAL_LEDGER_TOO_SHORT outer={target} n={len(q)}")
    return q

def side_rel(cal,pcol,side,exclude_idx=None):
    h=cal if exclude_idx is None else cal.drop(index=exclude_idx)
    pred=(h[pcol].to_numpy(float)>=.5).astype(int)
    y=h.y_up.to_numpy(int)
    mask=pred==side
    calls=int(mask.sum())
    correct=int(np.sum(pred[mask]==y[mask])) if calls else 0
    rel=float((correct+REL_A)/(calls+REL_A+REL_B))
    return rel,calls,correct

def rescue_score_for_probs(cal,probs):
    num=0.0; den=0.0; detail={}
    for name,p in probs.items():
        side=int(p>=.5)
        rel,calls,correct=side_rel(cal,f"p_{name}",side)
        edge=max(2*rel-1,0.0)
        conf=2*float(p)-1
        num+=edge*conf; den+=edge
        detail[name]={"rel":rel,"calls":calls,"correct":correct,"edge":edge}
    score=float(num/den) if den>1e-12 else 0.0
    return score,detail

def attach_loo_scores(cal):
    scores=[]
    for idx,row in cal.iterrows():
        num=0.0; den=0.0
        for name in ("LONG_EN","RECENT60_L2","LOCAL_ANALOG"):
            p=float(row[f"p_{name}"])
            side=int(p>=.5)
            rel,_,_=side_rel(cal,f"p_{name}",side,exclude_idx=idx)
            edge=max(2*rel-1,0.0)
            num+=edge*(2*p-1); den+=edge
        scores.append(float(num/den) if den>1e-12 else 0.0)
    q=cal.copy(); q["rescue_score"]=scores
    return q

def recall_side(y,pred,side):
    m=y==side
    return float(np.mean(pred[m]==side)) if np.any(m) else 0.0

def eval_threshold(cal,th):
    y=cal.y_up.to_numpy(int)
    anchor=(cal.r_pls.to_numpy(float)>=0).astype(int)
    score=cal.rescue_score.to_numpy(float)
    rescue=(score>=0).astype(int)
    pred=anchor.copy()
    over=(np.abs(score)>=th)&(rescue!=anchor)
    pred[over]=rescue[over]
    r=cal.r_pls.to_numpy(float)
    rf=np.where(pred==anchor,r,np.where(pred==1,np.abs(r),-np.abs(r)))
    rw=cal.rw.to_numpy(float); actual=cal.actual.to_numpy(float)
    fc=rw*np.exp(rf); ae=np.abs(fc-actual)
    return {
        "sum_abs_error":float(ae.sum()),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "up_recall":recall_side(y,pred,1),
        "down_recall":recall_side(y,pred,0),
        "override_count":int(over.sum()),
        "pred":pred,
    }

def choose_threshold(cal):
    y=cal.y_up.to_numpy(int)
    anchor=(cal.r_pls.to_numpy(float)>=0).astype(int)
    base_r=cal.r_pls.to_numpy(float)
    rw=cal.rw.to_numpy(float); actual=cal.actual.to_numpy(float)
    base_fc=rw*np.exp(base_r)
    base_sae=float(np.abs(base_fc-actual).sum())
    up=recall_side(y,anchor,1); down=recall_side(y,anchor,0)
    strong=1 if up>=down else 0; weak=1-strong
    base_strong=up if strong else down
    scored=[]
    for th in THRESHOLDS:
        m=eval_threshold(cal,th)
        sr=m["up_recall"] if strong else m["down_recall"]
        wr=m["down_recall"] if strong else m["up_recall"]
        eligible=(sr>=base_strong-STRONG_RECALL_TOL-1e-12 and m["sum_abs_error"]<=base_sae*(1+PRICE_AE_TOL)+1e-9)
        scored.append({
            "threshold":float(th),"eligible":bool(eligible),
            "strong_side":"UP" if strong else "DOWN",
            "weak_side":"DOWN" if strong else "UP",
            "strong_recall":float(sr),"weak_recall":float(wr),
            "balanced_accuracy":float(m["balanced_accuracy"]),
            "accuracy":float(m["accuracy"]),
            "sum_abs_error":float(m["sum_abs_error"]),
            "override_count":int(m["override_count"]),
        })
    elig=[x for x in scored if x["eligible"]]
    if not elig:
        return None,{"reason":"KEEP_ANCHOR_NO_ELIGIBLE","candidates":scored,"strong_side":"UP" if strong else "DOWN","weak_side":"DOWN" if strong else "UP"}
    elig.sort(key=lambda z:(-z["weak_recall"],-z["balanced_accuracy"],z["sum_abs_error"],-z["threshold"]))
    return float(elig[0]["threshold"]),{"reason":"SELECTED","selected":elig[0],"candidates":scored,"strong_side":elig[0]["strong_side"],"weak_side":elig[0]["weak_side"]}

def forecast_outer(bundle,target):
    samples,xt,_=history_samples(bundle,target)
    cal=attach_loo_scores(calibration_ledger(bundle,target,samples))
    th,sel=choose_threshold(cal)
    anchor=pls.forecast_one(bundle,target)
    train_keys=sorted(samples)
    probs=expert_predict(samples,train_keys,xt)
    score,rel_detail=rescue_score_for_probs(cal,probs)

    r=float(anchor["pred_log_return_gold"])
    anchor_dir=1 if r>=0 else 0
    rescue_dir=1 if score>=0 else 0
    override=(th is not None and abs(score)>=th and rescue_dir!=anchor_dir)
    final_dir=rescue_dir if override else anchor_dir
    rf=r if not override else (abs(r) if final_dir==1 else -abs(r))
    rw=float(anchor["rw"]); actual=float(anchor["actual"])
    fc=float(rw*math.exp(rf))
    return {
        "target":target,"origin":anchor["origin"],
        "actual":actual,"rw":rw,
        "pls_forecast":float(anchor["forecast"]),"adprr_forecast":fc,
        "pls_ae":float(abs(float(anchor["forecast"])-actual)),"adprr_ae":float(abs(fc-actual)),
        "pls_direction":"UP" if anchor_dir else "DOWN",
        "adprr_direction":"UP" if final_dir else "DOWN",
        "actual_direction":"UP" if actual>rw else "DOWN",
        "pls_direction_correct":bool(anchor_dir==(1 if actual>rw else 0)),
        "adprr_direction_correct":bool(final_dir==(1 if actual>rw else 0)),
        "override":bool(override),
        "override_beneficial_direction":bool(override and anchor_dir!=(1 if actual>rw else 0) and final_dir==(1 if actual>rw else 0)),
        "override_harmful_direction":bool(override and anchor_dir==(1 if actual>rw else 0) and final_dir!=(1 if actual>rw else 0)),
        "override_beneficial_ae":bool(override and abs(fc-actual)<abs(float(anchor["forecast"])-actual)-1e-9),
        "override_harmful_ae":bool(override and abs(fc-actual)>abs(float(anchor["forecast"])-actual)+1e-9),
        "selected_threshold":th,
        "selection_reason":sel["reason"],
        "strong_side_calibration":sel.get("strong_side"),
        "weak_side_calibration":sel.get("weak_side"),
        "rescue_score":float(score),
        "p_LONG_EN":float(probs["LONG_EN"]),
        "p_RECENT60_L2":float(probs["RECENT60_L2"]),
        "p_LOCAL_ANALOG":float(probs["LOCAL_ANALOG"]),
        "rel_LONG_EN":rel_detail["LONG_EN"]["rel"],
        "rel_RECENT60_L2":rel_detail["RECENT60_L2"]["rel"],
        "rel_LOCAL_ANALOG":rel_detail["LOCAL_ANALOG"]["rel"],
        "anchor_n_components":int(anchor["selected_n_components"]),
        "calibration_n":int(len(cal)),
    }

def metric_rows(rows,prefix):
    fkey="adprr_forecast" if prefix=="adprr" else "pls_forecast"
    a=np.asarray([r["actual"] for r in rows],float)
    f=np.asarray([r[fkey] for r in rows],float)
    rw=np.asarray([r["rw"] for r in rows],float)
    y=(a>rw).astype(int); pred=(f>=rw).astype(int)
    ae=np.abs(f-a); rwae=np.abs(rw-a)
    wi=int(np.argmax(ae))
    up=recall_side(y,pred,1); down=recall_side(y,pred,0)
    return {
        "n":len(rows),"sum_abs_error":float(ae.sum()),"mae":float(ae.mean()),
        "rmse":float(np.sqrt(np.mean((f-a)**2))),
        "mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100),
        "wape_pct":float(ae.sum()/np.maximum(np.abs(a).sum(),1e-12)*100),
        "worst_ae":float(ae[wi]),"worst_month":rows[wi]["target"],
        "relative_mae_vs_rw":float(ae.sum()/max(float(rwae.sum()),1e-12)),
        "direction_correct":int(np.sum(pred==y)),
        "direction_accuracy_pct":float(np.mean(pred==y)*100),
        "balanced_accuracy_pct":float(balanced_accuracy_score(y,pred)*100),
        "up_recall_pct":float(up*100),"down_recall_pct":float(down*100),
        "min_side_recall_pct":float(min(up,down)*100),
        "override_count":int(sum(r["override"] for r in rows)) if prefix=="adprr" else 0,
        "direction_rescues":int(sum(r["override_beneficial_direction"] for r in rows)) if prefix=="adprr" else 0,
        "direction_damages":int(sum(r["override_harmful_direction"] for r in rows)) if prefix=="adprr" else 0,
        "ae_beneficial_overrides":int(sum(r["override_beneficial_ae"] for r in rows)) if prefix=="adprr" else 0,
        "ae_harmful_overrides":int(sum(r["override_harmful_ae"] for r in rows)) if prefix=="adprr" else 0,
    }

def run_period(bundle,start,end,label):
    rows=[]
    targets=list(base.month_range(start,end))
    for i,t in enumerate(targets,1):
        r=forecast_outer(bundle,t); r["role"]=label; rows.append(r)
        print(f"ADPRR_PROGRESS {label} {i}/{len(targets)} target={t} override={int(r['override'])} plsAE={r['pls_ae']:.3f} adprrAE={r['adprr_ae']:.3f} plsdir={int(r['pls_direction_correct'])} adprrdir={int(r['adprr_direction_correct'])}",flush=True)
    return {
        "role":label,"rows":rows,
        "metrics":metric_rows(rows,"adprr"),
        "anchor_metrics":metric_rows(rows,"pls"),
        "threshold_counts":dict(sorted(Counter("KEEP" if r["selected_threshold"] is None else f"{r['selected_threshold']:.2f}" for r in rows).items()))
    }

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    before=bundle.invariants_before
    dev=run_period(bundle,DEV_START,DEV_END,"DEV_SELECTION_AUTHORITY")
    hold=run_period(bundle,HOLD_START,HOLD_END,"LOCKED_REPORT_ONLY")
    stress=run_period(bundle,STRESS_START,STRESS_END,"QUARANTINED_REPORT_ONLY")
    after=read_invariants(dsn)
    if before!=after: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    comparison=[
        {"model":"ADPRR_V1","sum_abs_error":dev["metrics"]["sum_abs_error"],"direction_correct":dev["metrics"]["direction_correct"]},
        {"model":"PLS1_ANCHOR_REPLAY","sum_abs_error":dev["anchor_metrics"]["sum_abs_error"],"direction_correct":dev["anchor_metrics"]["direction_correct"]},
    ]+[
        {"model":k,"sum_abs_error":float(v["dev_sumae"]),"direction_correct":int(v["dev_direction_correct"])}
        for k,v in REFS.items()
    ]
    comparison=sorted(comparison,key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["model"]))
    payload={"dev":dev["rows"],"holdout_2025":hold["rows"],"stress_2026":stress["rows"]}
    digest=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

    out={
        "model_id":MODEL_ID,"scientific_gate":"PASS",
        "technical_correction":"GOLD_MONTHLY_ADPRR_V1_TECHNICAL_CORRECTION_2026-10-02.md",
        "contract":{
            "target":"H=1 next-calendar-month average XAU/USD",
            "representation":"CURRENT8",
            "base_anchor":"PLS1 V1",
            "calibration":"outer-origin nested historical 36-month ledger",
            "direction_experts":["LONG_EN","RECENT60_L2","LOCAL_ANALOG"],
            "beta_prior":[REL_A,REL_B],
            "threshold_grid":list(THRESHOLDS),
            "strong_side_recall_tolerance":STRONG_RECALL_TOL,
            "price_sumae_tolerance":PRICE_AE_TOL,
            "magnitude_policy":"ABS_PLS1_LOG_RETURN_PRESERVED",
            "random_split":"NONE","database":"READ_ONLY",
            "2025_role":"LOCKED_REPORT_ONLY","2026_role":"QUARANTINED_REPORT_ONLY",
        },
        "dev":dev,"holdout_2025":hold,"stress_2026":stress,
        "frozen_reference_comparison":comparison,
        "authority_invariants_unchanged":True,
        "software":{"python":platform.python_version(),"numpy":np.__version__,"scikit_learn":sklearn.__version__},
        "result_payload_sha256":digest,
    }
    Path("GOLD_MONTHLY_ADPRR_V1_RESULT_2026-10-02.json").write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")

    def line(name,m):
        return f"| {name} | {m['sum_abs_error']:.2f} | {m['direction_correct']}/{m['n']} ({m['direction_accuracy_pct']:.2f}%) | {m['balanced_accuracy_pct']:.2f}% | {m['up_recall_pct']:.2f}% | {m['down_recall_pct']:.2f}% | {m['min_side_recall_pct']:.2f}% | {m['override_count']} |"
    lines=[
        "# GOLD MONTHLY — ADPRR-v1 RESULT","",
        "Asymmetric Direction-Preserving Reliability Router. Technical source-contract correction applied before any scientific result existed.","",
        "## DEV 2022-04..2024-12","",
        "| Model | ΣAE USD | Direction | Balanced acc | UP recall | DOWN recall | Min-side recall | Overrides |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        line("PLS1 anchor replay",dev["anchor_metrics"]),
        line("ADPRR-v1",dev["metrics"]),"",
        f"Direction rescues / damages: **{dev['metrics']['direction_rescues']} / {dev['metrics']['direction_damages']}**.",
        f"AE-beneficial / AE-harmful overrides: **{dev['metrics']['ae_beneficial_overrides']} / {dev['metrics']['ae_harmful_overrides']}**.",
        f"Threshold counts: \`{json.dumps(dev['threshold_counts'],sort_keys=True)}\`.","",
        "## Reporting only","",
        "| Period | Model | ΣAE USD | Direction | Balanced acc | UP recall | DOWN recall | Overrides |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
        f"| 2025 | PLS1 | {hold['anchor_metrics']['sum_abs_error']:.2f} | {hold['anchor_metrics']['direction_correct']}/12 | {hold['anchor_metrics']['balanced_accuracy_pct']:.2f}% | {hold['anchor_metrics']['up_recall_pct']:.2f}% | {hold['anchor_metrics']['down_recall_pct']:.2f}% | 0 |",
        f"| 2025 | ADPRR-v1 | {hold['metrics']['sum_abs_error']:.2f} | {hold['metrics']['direction_correct']}/12 | {hold['metrics']['balanced_accuracy_pct']:.2f}% | {hold['metrics']['up_recall_pct']:.2f}% | {hold['metrics']['down_recall_pct']:.2f}% | {hold['metrics']['override_count']} |",
        f"| 2026 Jan-Jul | PLS1 | {stress['anchor_metrics']['sum_abs_error']:.2f} | {stress['anchor_metrics']['direction_correct']}/7 | {stress['anchor_metrics']['balanced_accuracy_pct']:.2f}% | {stress['anchor_metrics']['up_recall_pct']:.2f}% | {stress['anchor_metrics']['down_recall_pct']:.2f}% | 0 |",
        f"| 2026 Jan-Jul | ADPRR-v1 | {stress['metrics']['sum_abs_error']:.2f} | {stress['metrics']['direction_correct']}/7 | {stress['metrics']['balanced_accuracy_pct']:.2f}% | {stress['metrics']['up_recall_pct']:.2f}% | {stress['metrics']['down_recall_pct']:.2f}% | {stress['metrics']['override_count']} |",
        "","## Frozen reference frontier","",
        "| Model | DEV ΣAE | Direction |","|---|---:|---:|"
    ]
    for r in comparison: lines.append(f"| {r['model']} | {r['sum_abs_error']:.2f} | {r['direction_correct']}/33 |")
    lines+=["","2025/2026 were report-only and did not alter ADPRR-v1."]
    Path("GOLD_MONTHLY_ADPRR_V1_RESULT_2026-10-02.md").write_text("\n".join(lines)+"\n")
    pd.DataFrame(dev["rows"]+hold["rows"]+stress["rows"]).to_csv("GOLD_MONTHLY_ADPRR_V1_PREDICTIONS_2026-10-02.csv",index=False)
    print("ADPRR_V1_OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({"dev":dev["metrics"],"anchor":dev["anchor_metrics"],"holdout":hold["metrics"],"stress":stress["metrics"],"comparison":comparison,"sha":digest},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
