#!/usr/bin/env python3
"""R77: strict time-matured binary first-passage shock risks, not daily sign labels.
Preregged in GOLD_R77_20261013_TWO_SIDED_SHOCK_HAZARD_PREREG.md.
Historical research ONLY. Not a bank tradable alert or user-specific recommendation.
"""
import csv, json, math
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score, average_precision_score, log_loss
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data_r76/GOLD_R76_20261013_09TR_SHOCK_FIRST_TOUCH_3D_ORIGINS.csv"
EVENTS=ROOT/"data_r77/GOLD_R77_20261013_VOL_SCALED_FIRST_TOUCH_EVENTS.csv"
OUT=ROOT/"GOLD_R77_20261013_"
ALPHA=5.
FEATURES=("r1","r5","r20","sd20","ret4","sqrt_rv4","asym4")
OUTCOMES=("DOWN","UP","ANY")
SCORED_YEARS=(2023,2024,2025,2026)
rng=np.random.default_rng(76013)

def load():
    rows=[]
    with SOURCE.open() as f:
        for r in csv.DictReader(f):
            if r["cls"]=="TIE":
                continue
            x={k:(float(r[k]) if r[k] else (0.0 if k in ("neg_rv4","pos_rv4") else float("nan"))) for k in ("p","r1","r5","r20","sd20","ret4","rv4","neg_rv4","pos_rv4","himax","lomin")}
            if not all(math.isfinite(z) for z in x.values()):
                raise ValueError("missing core numeric except empty semivariance")
            x["sqrt_rv4"]=math.sqrt(max(x["rv4"],0))
            x["asym4"]=(x["neg_rv4"]-x["pos_rv4"])/(x["rv4"]+1e-10)
            x.update(d=date.fromisoformat(r["d"]),year=int(r["d"][:4]),cls=r["cls"],cls1=r["cls1"],
                     up_t=r["up_t"],dn_t=r["dn_t"],src=r["src"])
            x["ANY"]=int(x["cls"]!="NONE")
            x["DOWN"]=int(x["cls"]=="DOWN")
            x["UP"]=int(x["cls"]=="UP")
            x["ANY1"]=int(x["cls1"]!="NONE")
            rows.append(x)
    with EVENTS.open() as fh:
        realized=list(csv.DictReader(fh))
    labelmap={date.fromisoformat(x["d"]):x for x in realized}
    if len(rows)!=len(realized) or len(labelmap)!=len(rows):
        raise AssertionError("R77 source/origin set differs from R76")
    for x in rows:
        e=labelmap.get(x["d"])
        if e is None or e["src"]!=x["src"]:
            raise AssertionError("source/date mismatch")
        if abs(float(e["p"])/x["p"]-1)>1e-12:
            raise AssertionError("issue price mismatch")
        x["thr"]=float(e["thr"])
        x["cls"]=e["cls"]
        x["up_t"]=e["up_t"]
        x["dn_t"]=e["dn_t"]
        x["himax"]=float(e["himax"])
        x["lomin"]=float(e["lomin"])
        x["ANY"]=int(x["cls"]!="NONE")
        x["DOWN"]=int(x["cls"]=="DOWN")
        x["UP"]=int(x["cls"]=="UP")
    rows.sort(key=lambda x:x["d"])
    if len({x["d"] for x in rows})!=len(rows):raise AssertionError("duplicate source issue dates")
    return rows

def mature_before(x,d):
    # Every 3d horizon <= +7 calendar days; 7d buffer safely preserves training-as-of.
    return x["d"]+timedelta(days=7) < d

def score_stats(rows, label, modelkey, basekey, raw=False):
    n=len(rows)
    if n<10: return {"n":n}
    y=np.array([r[label] for r in rows],dtype=float)
    p=np.array([r[modelkey] for r in rows],dtype=float)
    b=np.array([r[basekey] for r in rows],dtype=float)
    positive=int(y.sum())
    result={"n":n, "events":positive,"event_rate":float(y.mean()),
            "brier_model":float(brier_score_loss(y,p)),
            "brier_rolling60":float(brier_score_loss(y,b)),
            "brier_delta_baseline_minus_model":float(brier_score_loss(y,b)-brier_score_loss(y,p)),
            "logloss_model":float(log_loss(y,np.clip(p,1e-8,1-1e-8),labels=[0,1])),
            "auc":float(roc_auc_score(y,p)) if 0<positive<n else None,
            "avg_precision":float(average_precision_score(y,p)) if 0<positive<n else None}
    q=np.quantile(p,.8)
    top=(p>=q)
    result["top20_n"]=int(top.sum())
    result["top20_events"]=int(y[top].sum())
    result["top20_precision"]=float(y[top].mean())
    result["top20_lift_vs_overall"]=float(y[top].mean()-y.mean())
    result["top20_lift_vs_rolling60_exp"]=float(y[top].mean()-b[top].mean())
    return result

def paired_blocks(rows,label,block=5,bn=1500):
    # Each year separate blocks to avoid falsely assuming same shock months independent.
    per=[]
    for y in (2023,2024):
        r=[x for x in rows if x["year"]==y]
        if len(r)>=block:
            e=np.array([(x["roll60_"+label]-x[label])**2-(x["model_"+label]-x[label])**2 for x in r])
            per.append(e)
    if len(per)!=2:return [None,None]
    v=[]
    for _ in range(bn):
        samples=[]
        for d in per:
            idx=[]
            while len(idx)<len(d):
                st=rng.integers(0,len(d)-block+1)
                idx.extend(range(st,st+block))
            samples.extend(d[np.asarray(idx[:len(d)])])
        v.append(np.mean(samples))
    return list(map(float,np.quantile(v,[.025,.975])))

def main():
    data=load()
    thresholds={}
    allpred=[]
    for yr in SCORED_YEARS:
        train_end=date(2024 if yr>=2025 else yr-1,12,24)
        train=[r for r in data if r["d"]<=train_end]
        test=[r for r in data if r["year"]==yr]
        features=np.array([[x[k] for k in FEATURES] for x in train])
        T=np.array([[x[k] for k in FEATURES] for x in test])
        ss=StandardScaler().fit(features)
        for label in OUTCOMES:
            y=np.array([r[label] for r in train])
            if len(set(y))<2:raise ValueError("untrainable outcome "+label)
            model=LogisticRegression(C=1/ALPHA,max_iter=2000,tol=1e-10,solver="lbfgs")
            model.fit(ss.transform(features),y)
            out=model.predict_proba(ss.transform(T))[:,1]
            for r,p in zip(test,out):
                r["model_"+label]=float(p)
        for r in test:
            # Previous matured outcomes ONLY; previous 60 dated source-qualified origins.
            past=[x for x in data if x["d"]<r["d"] and mature_before(x,r["d"])]
            past=past[-60:]
            for label in OUTCOMES:
                r["roll60_"+label]=(sum(x[label] for x in past)+1)/(len(past)+2)
            r["train_n"]=len(train)
            r["train_asof"]=train_end.isoformat()
            allpred.append(r)

    results={"source":str(SOURCE.relative_to(ROOT)),"label":"first of exante max(1.5pct,1.5*sqrt(3)*past20 return sigma) UP/DOWN log barriers within3 days",
             "model":"sklearn logistic L2 C0.2, zscale TRAIN only, fixed yearly train asof","features":FEATURES,
             "years":{},"development":{},"opened_transport":{}}
    for yr in SCORED_YEARS:
        rr=[x for x in allpred if x["year"]==yr]
        results["years"][str(yr)]={"source":rr[0]["src"],"n":len(rr), "median_barrier_pct":float(np.median([x["thr"] for x in rr])*100),
                   "train_n":rr[0]["train_n"],"train_asof":rr[0]["train_asof"],
                   "risk":{label:score_stats(rr,label,"model_"+label,"roll60_"+label) for label in OUTCOMES},
                   "secondary_one_session_ge1pct":{"any_shock_n":sum(x["ANY1"] for x in rr),
                       "any_shock_rate":sum(x["ANY1"] for x in rr)/len(rr)}}
    for label in OUTCOMES:
        dev=[x for x in allpred if x["year"]<=2024]
        results["development"][label]=score_stats(dev,label,"model_"+label,"roll60_"+label)
        results["development"][label]["paired5d_brier_gain_ci95"]=paired_blocks(dev,label)
        results["opened_transport"][label]=score_stats([x for x in allpred if x["year"]>=2025],
                                                        label,"model_"+label,"roll60_"+label)

    # Freeze a single prospective alarm threshold from DEV MODEL predicted probability, never year2025/26 outcomes.
    for label in ("DOWN","UP"):
        dev=[r for r in allpred if r["year"]<=2024]
        threshold=float(np.quantile([r["model_"+label] for r in dev],.8))
        thresholds[label]=threshold
        for yr in SCORED_YEARS:
            rr=[r for r in allpred if r["year"]==yr and r["model_"+label]>=threshold]
            results["years"][str(yr)]["risk"][label]["frozen_dev_alert_threshold"]=threshold
            results["years"][str(yr)]["risk"][label]["frozen_dev_alert_n"]=len(rr)
            results["years"][str(yr)]["risk"][label]["frozen_dev_alert_correct"]=sum(r[label] for r in rr)
            results["years"][str(yr)]["risk"][label]["frozen_dev_alert_precision"]=sum(r[label] for r in rr)/len(rr) if rr else None
    results["frozen_dev_thresholds"]=thresholds

    results["predeclared_support_gate"]={}
    for label in OUTCOMES:
        devs=[results["years"][str(y)]["risk"][label] for y in (2023,2024)]
        opened=[results["years"][str(y)]["risk"][label] for y in (2025,2026)]
        dev_ok=all(s["brier_delta_baseline_minus_model"]>0 and (s["auc"] or 0)>.5 for s in devs)
        open_ok=all(s["top20_lift_vs_rolling60_exp"]>=0 for s in opened)
        ci=results["development"][label]["paired5d_brier_gain_ci95"]
        results["predeclared_support_gate"][label]={"dev_ok":dev_ok,"opened_lift_ok":open_ok,
              "bootstrap_ci":ci,"SUPPORTED":bool(dev_ok and open_ok and ci[0]>0)}
    with (Path(str(OUT)+"RESULT.json")).open("w") as f:json.dump(results,f,indent=2,ensure_ascii=False)
    fields=["d","year","src","p","r1","r5","r20","sd20","ret4","sqrt_rv4","asym4",
            "cls","ANY","DOWN","UP","ANY1","thr","himax","lomin","up_t","dn_t","train_n","train_asof",
            "model_DOWN","roll60_DOWN","model_UP","roll60_UP","model_ANY","roll60_ANY"]
    with (Path(str(OUT)+"ROW_FORECASTS.csv")).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for x in allpred:
            w.writerow({k:x.get(k) for k in fields})
    print(json.dumps({"n":len(data),"counts_by_year":{y:{k:results["years"][str(y)]["risk"][k]["events"] for k in OUTCOMES} for y in SCORED_YEARS},
         "brier_deltas":{y:{k:round(results["years"][str(y)]["risk"][k]["brier_delta_baseline_minus_model"],5) for k in OUTCOMES} for y in SCORED_YEARS},
         "auc":{y:{k:results["years"][str(y)]["risk"][k]["auc"] for k in OUTCOMES} for y in SCORED_YEARS},
         "gate":results["predeclared_support_gate"]},indent=2,default=float))

if __name__=="__main__":main()
