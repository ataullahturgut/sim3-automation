#!/usr/bin/env python3
"""R78 PIT-clock-safe CME NQ/ZN/CL + known FOMC schedule, conditional standardized XAU first-touch shocks.
For research only; federal meeting dates retrospectively reconstructed, FIRSTPRINT unverified.
Pre-scoring prereg: GOLD_R78_20261013_MACRO_FED_SHOCK_ABLATION_PREREG.md.
"""
from pathlib import Path
from datetime import date, datetime, timedelta, timezone
from collections import Counter
import csv, json, math, random
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss, average_precision_score

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data_r76/GOLD_R76_20261013_09TR_SHOCK_FIRST_TOUCH_3D_ORIGINS.csv"
EVT=ROOT/"data_r77/GOLD_R77_20261013_VOL_SCALED_FIRST_TOUCH_EVENTS.csv"
MAC=ROOT/"data_r78/GOLD_R78_20261013_CME_NQ_ZN_CL_01_04UTC_AVAILABLE.csv"
OUT=ROOT/"GOLD_R78_20261013_"
PFEATURES=("r1","r5","r20","sd20","ret4","sqrt_rv4","asym4")
MFEATURES=("nq4","zn4","cl4")
FFEATURES=("fomc_window","fomc_prior_trading_day")
SPECS={"PRICE7":PFEATURES,"PRICE7_MACRO3":PFEATURES+MFEATURES,
       "PRICE7_MACRO3_FEDCAL":PFEATURES+MFEATURES+FFEATURES}
LABELS=("DOWN","UP","ANY")
FOMC_STATEMENT_DATES={
"2023-02-01","2023-03-22","2023-05-03","2023-06-14","2023-07-26","2023-09-20","2023-11-01","2023-12-13",
"2024-01-31","2024-03-20","2024-05-01","2024-06-12","2024-07-31","2024-09-18","2024-11-07","2024-12-18",
"2025-01-29","2025-03-19","2025-05-07","2025-06-18","2025-07-30","2025-09-17","2025-10-29","2025-12-10",
"2026-01-28","2026-03-18","2026-04-29","2026-06-17","2026-07-29","2026-09-16","2026-10-28","2026-12-09",
}
FOMC={date.fromisoformat(z) for z in FOMC_STATEMENT_DATES}
assert len(FOMC)==32
def read(path):
    with path.open(newline="") as f:return list(csv.DictReader(f))
def weekdays_after(d,n):
    z=[];t=d
    while len(z)<n:
        t+=timedelta(days=1)
        if t.weekday()<5:z.append(t)
    return z
def last_weekday(d):
    t=d-timedelta(days=1)
    while t.weekday()>=5:t-=timedelta(days=1)
    return t
def auroc(yy,pp):
    return float(roc_auc_score(yy,pp)) if len(set(yy))>1 else None
def score(rs,pkey,label):
    y=np.array([r[label] for r in rs])
    p=np.array([r[pkey] for r in rs])
    if len(y)==0:return {"n":0}
    ix=np.argsort(p)[-max(1,math.ceil(.2*len(rs))):]
    return {"n":len(rs),"events":int(y.sum()),"base_frequency":float(y.mean()),
            "brier":float(brier_score_loss(y,p)), "auc":auroc(y,p),
            "avg_precision":float(average_precision_score(y,p)) if y.sum()>0 else None,
            "top20_n":len(ix),"top20_events":int(y[ix].sum()),
            "top20_precision":float(y[ix].mean())}
def ci_brier_diff(rs,label,a,b,nboot=2400):
    # positive if model b is better than model a; matched 5-issue block.
    e=np.array([(r[a]-r[label])**2-(r[b]-r[label])**2 for r in rs])
    if len(e)<25:return None
    rand=random.Random(78013);out=[]
    for _ in range(nboot):
        sample=[]
        while len(sample)<len(e):
            k=rand.randrange(len(e)-4)
            sample.extend(e[k:k+5])
        out.append(sum(sample[:len(e)])/len(e))
    return [float(np.quantile(out,.025)),float(np.quantile(out,.975))]

def load():
    gold={r["d"]:r for r in read(DATA)}
    evs={r["d"]:r for r in read(EVT)}
    assert len(gold)==len(evs)==1540
    macro=read(MAC)
    assert len(macro)==778 and len(set(x["d"] for x in macro))==len(macro)
    assert all(x["lastbar_start"].startswith(x["d"]+"T04:00:00") for x in macro)
    data=[]
    for m in macro:
        if m["d"] not in gold:continue
        g,e=gold[m["d"]],evs[m["d"]]
        d=date.fromisoformat(g["d"])
        assert g["d"]==e["d"] and g["src"]==e["src"]
        assert abs(float(g["p"])-float(e["p"]))<1e-9
        if e["cls"]=="TIE":continue
        t={k:float(g[k]) if g[k] else 0.0 for k in ("p","r1","r5","r20","sd20","ret4","rv4","neg_rv4","pos_rv4")}
        t["sqrt_rv4"]=math.sqrt(max(0,t["rv4"]))
        t["asym4"]=(t["neg_rv4"]-t["pos_rv4"])/(t["rv4"]+1.e-10)
        t.update({k:float(m[k]) for k in MFEATURES})
        t["fomc_window"]=int(any(x in FOMC for x in [d]+weekdays_after(d,3)))
        t["fomc_prior_trading_day"]=int(last_weekday(d) in FOMC)
        t["d"]=d;t["year"]=d.year;t["src"]=g["src"];t["cls"]=e["cls"]
        t["DOWN"]=int(e["cls"]=="DOWN");t["UP"]=int(e["cls"]=="UP")
        t["ANY"]=int(e["cls"]!="NONE");t["thr"]=float(e["thr"])
        assert all(math.isfinite(t[f]) for f in PFEATURES+MFEATURES+FFEATURES)
        data.append(t)
    data.sort(key=lambda r:r["d"])
    assert len(set(x["d"] for x in data))==len(data)
    return data

def main():
    data=load()
    out={"study":"R78 matched as-of morning CME+Fed scheduled dates; NOT observed policy or surprises",
         "n_joined":len(data),"all_years_counts":dict(Counter(x["year"] for x in data)),
         "fomc_source":"https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
         "train_scheme":"2024 train 2023 matured; 2025 and 2026 train frozen 2023+2024 matured to Dec24",
         "spec_features":SPECS,"risk":{},"promotion":{}}
    for year in (2024,2025,2026):
        train_end=date(2023 if year==2024 else 2024,12,24)
        train=[r for r in data if r["d"]<=train_end and r["d"].year>=2023]
        test=[r for r in data if r["year"]==year]
        if len(train)<160:raise AssertionError(f"train only {len(train)} for {year}")
        for spec,features in SPECS.items():
            x=np.array([[r[k] for k in features] for r in train])
            t=np.array([[r[k] for k in features] for r in test])
            ss=StandardScaler().fit(x)
            for label in LABELS:
                y=np.array([r[label] for r in train])
                assert len(set(y))==2, (year,label)
                clf=LogisticRegression(C=.2,solver="lbfgs",max_iter=2000,tol=1e-10).fit(ss.transform(x),y)
                pred=clf.predict_proba(ss.transform(t))[:,1]
                for i,r in enumerate(test):r[f"p_{spec}_{label}"]=float(pred[i])
                out["risk"].setdefault(str(year),{}).setdefault(label,{})[spec] =score(test,f"p_{spec}_{label}",label)
        for label in LABELS:
            for r in test:
                eligible=[v for v in data if v["d"]<r["d"]-timedelta(days=7) and v["year"]>=2023]
                z=eligible[-60:]
                r["p_FREQ60_"+label]=(sum(v[label] for v in z)+1)/(len(z)+2)
            out["risk"][str(year)][label]["FREQ60"]=score(test,"p_FREQ60_"+label,label)
        out["risk"][str(year)]["time_window_count"]=sum(r["fomc_window"] for r in test)
        out["risk"][str(year)]["train_n"]=len(train)

    # Freeze alarm threshold on DEV 2024 top fifth; keep it unchanged on 2025/26.
    dev=[r for r in data if r["year"]==2024]
    for spec in SPECS:
        for label in LABELS:
            threshold=float(np.quantile([r[f"p_{spec}_{label}"] for r in dev],.8))
            for year in (2024,2025,2026):
                xs=[r for r in data if r["year"]==year]
                selected=[r for r in xs if r[f"p_{spec}_{label}"]>=threshold]
                res=out["risk"][str(year)][label][spec]
                res.update({"dev2024_threshold":threshold,"alerts":len(selected),
                            "true_alerts":sum(r[label] for r in selected),
                            "alert_recall":sum(r[label] for r in selected)/sum(r[label] for r in xs) if sum(r[label] for r in xs) else None,
                            "alert_precision":sum(r[label] for r in selected)/len(selected) if selected else None})
    for label in LABELS:
        dev0=dev
        comp={}
        for left,right in (("PRICE7","PRICE7_MACRO3"),("PRICE7_MACRO3","PRICE7_MACRO3_FEDCAL")):
            a="p_"+left+"_"+label;b="p_"+right+"_"+label
            point={str(y):out["risk"][str(y)][label][left]["brier"]-
                             out["risk"][str(y)][label][right]["brier"]
                    for y in (2024,2025,2026)}
            ci=ci_brier_diff(dev0,label,a,b)
            passgate=all(v>0 for v in point.values()) and ci[0]>0
            comp[right+"_vs_"+left]={"paired_brier_benchmark_minus_enriched_by_year":point,
                                   "DEV2024_CI95":ci,"strict_gate_pass":bool(passgate)}
        out["promotion"][label]=comp
    fields=["d","year","src","cls","DOWN","UP","ANY","thr"]+list(PFEATURES+MFEATURES+FFEATURES)
    for label in LABELS:
        for spec in list(SPECS)+["FREQ60"]:fields.append(f"p_{spec}_{label}")
    with (Path(str(OUT)+"MATCHED_ROW_SCORES.csv")).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in data:
            if r["year"]>=2024:w.writerow({k:r.get(k) for k in fields})
    with (Path(str(OUT)+"SUMMARY.json")).open("w") as f:
        json.dump(out,f,indent=2,default=str)
    print(json.dumps({"matched":len(data),"by_year":out["all_years_counts"],
         "brier_delta":{y:{l:{
            "add_NQ_ZN_CL":round(out["risk"][y][l]["PRICE7"]["brier"]-out["risk"][y][l]["PRICE7_MACRO3"]["brier"],5),
            "add_FOMC_calendar":round(out["risk"][y][l]["PRICE7_MACRO3"]["brier"]-out["risk"][y][l]["PRICE7_MACRO3_FEDCAL"]["brier"],5)}
            for l in LABELS} for y in ("2024","2025","2026")},
         "auc":{y:{l:{s:round(out["risk"][y][l][s]["auc"],3) for s in SPECS}
            for l in LABELS} for y in ("2024","2025","2026")},
         "promote":out["promotion"]},indent=2))

if __name__=="__main__":main()
