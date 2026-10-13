#!/usr/bin/env python3
"""R79: STRICT post-onset M15 decision and future residual XAU 16:30 continuation/reversal risk.
All threshold and model choices registered before 2026 results in R79 prereg.
No bank real quotes, no claim a tradable alpha.
"""
import csv, math, json, random
from pathlib import Path
from datetime import date
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import brier_score_loss, roc_auc_score, average_precision_score

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"data_r79/GOLD_R79_20261013_GOLD_75BP_FIRST_STARTED_MOVEMENT_OBSERVED_TR.csv"
OUT=ROOT/"GOLD_R79_20261013_"
FEATURES=["sign","abs_move","hours_remaining","aligned_4bar_ret","sqrt_rv4","aligned_pre_ret","sqrt_pre_rv"]
TARGETS=["CONT","REV50","CONT50"]
def read():
    data=[]
    with SRC.open() as f:
        for s in csv.DictReader(f):
            d=date.fromisoformat(s["d"])
            a=float(s["aligned_future"]);sign=1 if s["onset_sign"]=="UP" else -1
            x={k:float(s[k]) for k in ("move","past4_lr","past4_rv","pre_lr","pre_rv","hours_remaining","p09","p_issue","p1630")}
            x.update({"d":d,"year":d.year,"src":s["src"],"onset":s["onset_bar_start"],
                      "onset_sign":s["onset_sign"],"sign":sign,"aligned_future":a,
                      "abs_move":abs(x["move"]),
                      "aligned_4bar_ret":sign*x["past4_lr"],
                      "sqrt_rv4":math.sqrt(x["past4_rv"]),
                      "aligned_pre_ret":sign*x["pre_lr"],
                      "sqrt_pre_rv":math.sqrt(x["pre_rv"]),
                      "CONT":int(a>0),"REV50":int(a<=-.005),"CONT50":int(a>=.005)})
            if not all(math.isfinite(x[v]) for v in FEATURES):
                raise ValueError("invalid input "+str(d))
            data.append(x)
    data.sort(key=lambda a:a["d"])
    assert len(data)==359 and len({r["d"] for r in data})==359
    return data

def metrics(rows,target,predkey,basekey):
    if not rows:return {}
    y=np.array([r[target] for r in rows]);p=np.array([r[predkey] for r in rows])
    b=np.array([r[basekey] for r in rows]);j=np.argsort(p)[-max(1,math.ceil(.2*len(rows))):]
    return dict(n=len(rows),events=int(y.sum()),prevalence=float(y.mean()),
        brier_model=float(brier_score_loss(y,p)),brier_rolling=float(brier_score_loss(y,b)),
        brier_gain=float(brier_score_loss(y,b)-brier_score_loss(y,p)),
        auc=float(roc_auc_score(y,p)) if len(set(y))==2 else None,
        top20_n=len(j),top20_events=int(y[j].sum()),
        top20_event_precision=float(y[j].mean()),
        recall_threshold_half=float(((p>=.5)&(y==1)).sum()/sum(y)) if sum(y)>0 else None,
        signals_half=int((p>=.5).sum()),
        exact_class_correct=int(( (p>=.5)==y ).sum()),
        always_persist_correct=int((y==1).sum()) if target=="CONT" else None)

def paired_bootstrap(rows,target,block=5,n=3000):
    group=[ [r for r in rows if r["year"]==yr] for yr in (2023,2024)]
    if any(len(a)<10 for a in group):return [None,None]
    rand=random.Random(79013);vals=[]
    for _ in range(n):
        ds=[]
        for rg in group:
            a=np.array([(r[f"p_rolling_{target}"]-r[target])**2 -
                   (r[f"p_logit_{target}"]-r[target])**2 for r in rg])
            selected=[]
            while len(selected)<len(a):
                k=rand.randrange(len(a)-block+1)
                selected.extend(a[k:k+block])
            ds.extend(selected[:len(a)])
        vals.append(np.mean(ds))
    return [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]

def main():
    data=read()
    output={"source":str(SRC.relative_to(ROOT)),"n_qualified_events":len(data),
       "meaning":"threshold crossed using completed 15m bar only, future begins after it",
       "targets":{"CONT":"signed last confirmed signal close to FUTURE 16:30 positive",
                  "REV50":"signed residual move <= -50bp",
                  "CONT50":"signed residual move >= +50bp"},
       "model":"7 fixed origin-known features, L2 C0.2, prior-year refit; 2025/26 frozen 2020-24",
       "yearly":{},"gate":{},"counts":{}}
    for yr in (2023,2024,2025,2026):
        end=date(yr-1 if yr<2025 else 2024,12,24)
        train=[r for r in data if r["d"]<=end];te=[r for r in data if r["year"]==yr]
        assert len(train)>120 and len(te)>20,(yr,len(train),len(te))
        x=np.array([[r[k] for k in FEATURES] for r in train])
        z=np.array([[r[k] for k in FEATURES] for r in te])
        scaler=StandardScaler().fit(x)
        for target in TARGETS:
            y=np.array([r[target] for r in train])
            assert len(set(y))==2
            model=LogisticRegression(C=.2,solver="lbfgs",max_iter=3000).fit(scaler.transform(x),y)
            p=model.predict_proba(scaler.transform(z))[:,1]
            for r,pr in zip(te,p):
                prior=[x for x in data if x["d"]<r["d"] and x["year"]<=r["year"]]
                hist=prior[-60:]
                r[f"p_logit_{target}"]=float(pr)
                r[f"p_rolling_{target}"]=(1+sum(x[target] for x in hist))/(2+len(hist))
        output["yearly"][str(yr)]={"train_n":len(train),"test_n":len(te),
         "by_sign":{},"all":{}}
        for sign in ("UP","DOWN"):
            z=[r for r in te if r["onset_sign"]==sign]
            output["yearly"][str(yr)]["by_sign"][sign]={
                "n":len(z),"continued":sum(r["CONT"] for r in z),
                "reversed":sum(1-r["CONT"] for r in z),
                "reversal_ge50bp":sum(r["REV50"] for r in z),
                "continuation_ge50bp":sum(r["CONT50"] for r in z),
                "median_signed_residual_bp":float(10000*np.median([r["aligned_future"] for r in z])) if z else None}
        for target in TARGETS:
            output["yearly"][str(yr)]["all"][target]=metrics(te,target,f"p_logit_{target}",f"p_rolling_{target}")

    for target in TARGETS:
        groups=[r for r in data if r["year"] in (2023,2024)]
        ci=paired_bootstrap(groups,target)
        improve_all=all(output["yearly"][str(y)]["all"][target]["brier_gain"]>0 for y in (2023,2024,2025,2026))
        output["gate"][target]={"all_years_gain":improve_all,"dev_paired_block5_CI":ci,
             "SUPPORTED":bool(improve_all and ci[0]>0)}
    fields=["d","src","onset","onset_sign","p09","p_issue","p1630","move",
       "hours_remaining","aligned_future"]+FEATURES+TARGETS+[
         f"p_{prefix}_{target}" for target in TARGETS for prefix in ("logit","rolling")]
    with (Path(str(OUT)+"ROWS.csv")).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in data:
            if r["year"]>=2023:w.writerow({key:r.get(key) for key in fields})
    with (Path(str(OUT)+"SUMMARY.json")).open("w") as f:json.dump(output,f,indent=2,ensure_ascii=False,default=str)
    print(json.dumps({"n":len(data),"yearly":output["yearly"],"gate":output["gate"]},indent=2,default=float))

if __name__=="__main__":main()
