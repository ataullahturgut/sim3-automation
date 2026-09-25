from __future__ import annotations

import csv, json, math, os
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

import vw_midas_msvr_successor_v1 as base
import vw_midas_estimator_headswap_v1 as hs
import vw_midas_fmrvr_v1 as fmr
import vw_midas_shallow_mlp_v1 as mlp

DEV_START, DEV_END = "2022-04", "2024-12"
TEST_START, TEST_END = "2025-01", "2026-07"

MODEL_ORDER = ("MSVR","FMRVR","PLS2","MLP")
SPECS = {
    "MSVR": ("MSVR", None, {"C":1.0,"epsilon":0.05,"gamma_scale":0.5}),
    "FMRVR": 2.5,
    "PLS2": ("PLS2", None, {"n_components":4}),
    "MLP": ((4,),1.0,"tanh"),
}

def actual_logret(b,t):
    p=base.month_shift(t,-1)
    return float(math.log(b.monthly_metal["Gold"][t]/b.monthly_metal["Gold"][p]))

def predict_all(b, samples, t):
    out={}
    pred,n=hs.predict_gold(samples,t,*SPECS["MSVR"])
    out["MSVR"]=(float(pred),n)
    pred,n,_,_=fmr.fit_predict(samples,t,SPECS["FMRVR"])
    out["FMRVR"]=(float(pred[0]),n)
    pred,n=hs.predict_gold(samples,t,*SPECS["PLS2"])
    out["PLS2"]=(float(pred),n)
    pred,n,_=mlp.fit_predict(samples,t,SPECS["MLP"])
    out["MLP"]=(float(pred[0]),n)
    return out

def meta_x(samples,t):
    # Only target-origin VW-MIDAS feature vector; target y is never used.
    x=np.asarray(samples[t][0],float)
    # Parsimonious summaries plus the 8 frozen features.
    mr=x[0::2]; vw=x[1::2]
    z=np.r_[x, np.mean(np.abs(x)), np.std(mr), np.std(vw), x[0]-x[1]]
    return z

def row_bundle(b, samples, t):
    preds=predict_all(b,samples,t)
    ar=actual_logret(b,t)
    p=base.month_shift(t,-1)
    anchor=float(b.core_gold[p]); actual=float(b.core_gold[t])
    row={"target":t,"origin":p,"actual_logret":ar,"anchor":anchor,"actual":actual,
         "meta_x":meta_x(samples,t).tolist()}
    for m,(rhat,n) in preds.items():
        fc=anchor*math.exp(rhat)
        row[m]={"pred_logret":rhat,"forecast":fc,"ape_pct":100*abs(fc-actual)/actual,
                "abs_logret_error":abs(rhat-ar),"train_rows":n}
    winner=min(MODEL_ORDER,key=lambda m:(row[m]["abs_logret_error"],MODEL_ORDER.index(m)))
    row["winner"]=winner
    row["winner_price_ape_model"]=min(MODEL_ORDER,key=lambda m:(row[m]["ape_pct"],MODEL_ORDER.index(m)))
    return row

def choose_alpha(dev_rows):
    alphas=(0.1,1.0,10.0,100.0)
    scores={a:[] for a in alphas}
    # Strict expanding meta-validation inside pre-2025 development.
    for i in range(12,len(dev_rows)):
        tr=dev_rows[:i]; va=dev_rows[i]
        X=np.array([r["meta_x"] for r in tr],float)
        y=np.array([r["FMRVR"]["abs_logret_error"]-r["PLS2"]["abs_logret_error"] for r in tr],float)
        xv=np.array(va["meta_x"],float)[None,:]
        sc=StandardScaler().fit(X); Xs=sc.transform(X); xvs=sc.transform(xv)
        truth=va["FMRVR"]["abs_logret_error"]-va["PLS2"]["abs_logret_error"]
        for a in alphas:
            model=Ridge(alpha=a).fit(Xs,y)
            pred=float(model.predict(xvs)[0])
            scores[a].append(abs(pred-truth))
    return min(alphas,key=lambda a:(float(np.mean(scores[a])),a)), {str(a):float(np.mean(scores[a])) for a in alphas}

def fit_gate(dev_rows,alpha):
    X=np.array([r["meta_x"] for r in dev_rows],float)
    y=np.array([r["FMRVR"]["abs_logret_error"]-r["PLS2"]["abs_logret_error"] for r in dev_rows],float)
    sc=StandardScaler().fit(X)
    model=Ridge(alpha=alpha).fit(sc.transform(X),y)
    return sc,model

def gate_pick(sc,model,row):
    # Predicted error differential >0 => FMRVR expected worse => choose PLS2.
    d=float(model.predict(sc.transform(np.array(row["meta_x"],float)[None,:]))[0])
    return ("PLS2" if d>0 else "FMRVR"), d

def metrics(rows, selector):
    rr=[]
    for r in rows:
        m=selector(r)
        rr.append({"target":r["target"],"forecast":r[m]["forecast"],"actual":r["actual"],"rw":r["anchor"]})
    return base.metrics(rr)

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    all_targets=list(base.month_range(DEV_START,TEST_END))
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in all_targets}

    rows=[row_bundle(b,cache[t],t) for t in all_targets]
    dev=[r for r in rows if DEV_START<=r["target"]<=DEV_END]
    test=[r for r in rows if TEST_START<=r["target"]<=TEST_END]
    y2025=[r for r in rows if r["target"].startswith("2025-")]
    y2026=[r for r in rows if r["target"].startswith("2026-")]

    alpha,cv=choose_alpha(dev)
    sc,gate=fit_gate(dev,alpha)
    for r in rows:
        pick,d=gate_pick(sc,gate,r)
        r["gate_pick"]=pick; r["gate_score_pred_fmrvr_minus_pls2_error"]=d

    def fixed(m): return lambda r:m
    def gated(r): return r["gate_pick"]
    def oracle2(r): return min(("FMRVR","PLS2"),key=lambda m:r[m]["abs_logret_error"])

    summary={}
    for label,subset in [("DEV",dev),("2025",y2025),("2026",y2026),("2025_2026",test)]:
        summary[label]={
            "MSVR":metrics(subset,fixed("MSVR")),
            "FMRVR":metrics(subset,fixed("FMRVR")),
            "PLS2":metrics(subset,fixed("PLS2")),
            "MLP":metrics(subset,fixed("MLP")),
            "GATE_FMRVR_PLS2":metrics(subset,gated),
            "ORACLE_FMRVR_PLS2_DIAGNOSTIC_ONLY":metrics(subset,oracle2),
            "winner_counts":dict(Counter(r["winner"] for r in subset)),
            "gate_pick_counts":dict(Counter(r["gate_pick"] for r in subset)),
        }

    # Anatomy: where FMRVR vs PLS2 diverge materially.
    anatomy=[]
    for r in rows:
        diff=r["FMRVR"]["ape_pct"]-r["PLS2"]["ape_pct"]
        anatomy.append({
            "target":r["target"],"actual":r["actual"],
            "msvr_forecast":r["MSVR"]["forecast"],"msvr_ape":r["MSVR"]["ape_pct"],
            "fmrvr_forecast":r["FMRVR"]["forecast"],"fmrvr_ape":r["FMRVR"]["ape_pct"],
            "pls2_forecast":r["PLS2"]["forecast"],"pls2_ape":r["PLS2"]["ape_pct"],
            "mlp_forecast":r["MLP"]["forecast"],"mlp_ape":r["MLP"]["ape_pct"],
            "winner":r["winner"],"gate_pick":r["gate_pick"],
            "fmrvr_minus_pls2_ape":diff,
        })
    largest=sorted(anatomy,key=lambda x:abs(x["fmrvr_minus_pls2_ape"]),reverse=True)[:15]

    result={
        "model_id":"VW_MIDAS_ESTIMATOR_REGIME_GATE_DIAGNOSTIC_V1",
        "authority":{
            "database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
            "gate_training_period":f"{DEV_START}..{DEV_END}",
            "gate_inputs":"ORIGIN_SAFE_VW_MIDAS_X_ONLY",
            "gate_target":"FMRVR_abs_logret_error_minus_PLS2_abs_logret_error",
            "2025_role":"LOCKED_TRANSPORT_NOT_GATE_TUNING",
            "2026_role":"RETROSPECTIVE_STRESS_NOT_GATE_TUNING",
        },
        "gate":{"family":"Ridge","selected_alpha":alpha,"inner_expanding_cv_mae":cv,
                "interpretation":"predicted differential >0 => choose PLS2; else FMRVR"},
        "summary":summary,
        "largest_fmrvr_pls2_disagreements":largest,
        "rows":rows,
    }
    Path("vw_midas_estimator_regime_gate_v1_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    with open("vw_midas_estimator_regime_gate_v1_monthly.csv","w",newline="",encoding="utf-8") as f:
        fields=list(anatomy[0].keys())
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(anatomy)

    print(json.dumps({"gate":result["gate"],"summary":summary},sort_keys=True))

if __name__=="__main__": main()
