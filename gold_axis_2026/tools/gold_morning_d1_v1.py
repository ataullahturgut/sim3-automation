from __future__ import annotations
import json, math, time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, log_loss

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"MORNING_D1_V1_OUT"
OUT.mkdir(exist_ok=True)

AURORA=AX/"GOLD_H3_CLEAN_AURORA_PREDICTIONS_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
RIFT=AX/"GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv"
VEGA=AX/"GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv"
PRICE=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv"
CIG=AX/"GOLD_D1_CIG_V1_EXTENDED_JAN_SEP_REPLAY_2026-10-05.csv"

SYMS={"GC":"GC=F","SI":"SI=F","NQ":"NQ=F","ZN":"ZN=F","CL":"CL=F"}
START="2025-01-01"
END="2026-10-01"
CHECKPOINT_HOUR_UTC=6
SEED=20261005

M1=[
 "gc_anchor_to_cp","gc_ret_1h","gc_ret_3h","gc_ret_6h",
 "gc_rv_6h","gc_rv_12h","gc_upfrac_6h","gc_upfrac_12h",
 "gc_range_6h","gc_range_12h","gc_slope_6h","gc_slope_12h"
]
M2=M1+["si_anchor_to_cp","nq_anchor_to_cp","zn_anchor_to_cp","cl_anchor_to_cp"]
M3=M2+[
 "p_aurora","p_v5","p_rift","p_vega","p_opal_reversal",
 "opal_override","candidate_reversal","expert_std","gap_v5_rift","gap_v5_vega"
]
FAMILIES={"M1_GOLD_MICRO":M1,"M2_GOLD_PLUS_CROSS":M2,"M3_MICRO_PLUS_H3":M3}
MODELS=["LOGIT_L2","HGB_SMALL"]
THRESH=[.55,.60,.65,.70,.75]

def epoch(s):
    return int(pd.Timestamp(s,tz="UTC").timestamp())

def fetch_one(label,sym):
    params={
      "period1":epoch(START),"period2":epoch(END),
      "interval":"1h","events":"history","includeAdjustedClose":"true"
    }
    last=None
    for host in ["query1.finance.yahoo.com","query2.finance.yahoo.com"]:
        url=f"https://{host}/v8/finance/chart/{requests.utils.quote(sym,safe='')}"
        try:
            r=requests.get(url,params=params,headers={"User-Agent":"Mozilla/5.0 academic research"},timeout=60)
            if r.status_code!=200:
                last=f"HTTP_{r.status_code}:{r.text[:300]}"
                continue
            payload=r.json().get("chart",{})
            if payload.get("error") or not payload.get("result"):
                last=str(payload.get("error"))
                continue
            z=payload["result"][0]
            ts=z.get("timestamp") or []
            close=((z.get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
            q=pd.DataFrame({"ts":pd.to_datetime(ts,unit="s",utc=True),"close":close})
            q["close"]=pd.to_numeric(q.close,errors="coerce")
            q=q.dropna(subset=["close"])
            q=q[q.close>0].sort_values("ts").drop_duplicates("ts",keep="last").reset_index(drop=True)
            if len(q)<1000:
                last=f"TOO_FEW_{len(q)}"
                continue
            return q,{"symbol":sym,"rows":int(len(q)),"first":str(q.ts.min()),"last":str(q.ts.max()),"status":"OK"}
        except Exception as e:
            last=f"{type(e).__name__}:{e}"
    return None,{"symbol":sym,"status":"FAIL","error":last}

def slope(a):
    a=np.asarray(a,float)
    if len(a)<2:return np.nan
    x=np.arange(len(a),dtype=float)
    return float(np.polyfit(x,a,1)[0])

def feature_for_series(q, cutoff_date, issue_date, prefix):
    if q is None:return {}
    # Existing H3 cutoff uses prior trading date; use last completed 16:00 NY hourly bar.
    cd=pd.Timestamp(cutoff_date).date()
    cp=pd.Timestamp(issue_date,tz="UTC")+pd.Timedelta(hours=CHECKPOINT_HOUR_UTC)
    ny=q.ts.dt.tz_convert("America/New_York")
    anchor_mask=(ny.dt.date==cd)&(ny.dt.hour<=16)
    aq=q[anchor_mask]
    if aq.empty:return {}
    anchor=aq.iloc[-1]
    hist=q[q.ts<=cp].copy()
    if hist.empty or hist.iloc[-1].ts<=anchor.ts:return {}
    idx=hist.index[-1]
    cur=float(hist.loc[idx,"close"]); anc=float(anchor.close)
    lp=np.log(hist.close.astype(float)).to_numpy()
    out={f"{prefix}_anchor_to_cp":float(math.log(cur/anc))}
    for h in [1,3,6]:
        out[f"{prefix}_ret_{h}h"]=float(lp[-1]-lp[-1-h]) if len(lp)>h else np.nan
    rr=np.diff(lp)
    for h in [6,12]:
        if len(rr)>=h:
            x=rr[-h:]
            out[f"{prefix}_rv_{h}h"]=float(np.std(x,ddof=0))
            out[f"{prefix}_upfrac_{h}h"]=float(np.mean(x>0))
            w=lp[-(h+1):]
            out[f"{prefix}_range_{h}h"]=float(np.max(w)-np.min(w))
            out[f"{prefix}_slope_{h}h"]=slope(w)
        else:
            out[f"{prefix}_rv_{h}h"]=np.nan
            out[f"{prefix}_upfrac_{h}h"]=np.nan
            out[f"{prefix}_range_{h}h"]=np.nan
            out[f"{prefix}_slope_{h}h"]=np.nan
    return out

def build_panel(series):
    a=pd.read_csv(AURORA); v=pd.read_csv(V5); r=pd.read_csv(RIFT); g=pd.read_csv(VEGA)
    for z in [a,v,r,g]:
        z["feature_cutoff_date"]=pd.to_datetime(z.feature_cutoff_date).dt.normalize()
    a["forecast_issue_date"]=pd.to_datetime(a.forecast_issue_date).dt.normalize()
    ma=a.set_index("feature_cutoff_date"); mv=v.set_index("feature_cutoff_date"); mr=r.set_index("feature_cutoff_date"); mg=g.set_index("feature_cutoff_date")
    px=pd.read_csv(PRICE); px["date"]=pd.to_datetime(px.date).dt.normalize(); pmap=dict(zip(px.date,px.gold.astype(float)))
    rows=[]
    for x in a.itertuples(index=False):
        d=pd.Timestamp(x.feature_cutoff_date); issue=pd.Timestamp(x.forecast_issue_date)
        if issue<pd.Timestamp(START) or issue>pd.Timestamp("2026-09-25"):continue
        if d not in mv.index or d not in mr.index or d not in mg.index or d not in pmap or issue not in pmap:continue
        V=mv.loc[d]; R=mr.loc[d]; G=mg.loc[d]
        if isinstance(V,pd.DataFrame):V=V.iloc[0]
        if isinstance(R,pd.DataFrame):R=R.iloc[0]
        if isinstance(G,pd.DataFrame):G=G.iloc[0]
        row={
          "feature_cutoff_date":d,"forecast_issue_date":issue,
          "d1_up":int(pmap[issue]>pmap[d]),
          "p_aurora":float(x.p_aurora),"p_v5":float(V.p_helios_v5_dce),
          "p_rift":float(R.p_rift),"p_vega":float(G.p_vega),
          "p_opal_reversal":float(V.p_opal_reversal),
          "opal_override":int(str(V.opal_override).lower()=="true"),
          "candidate_reversal":int(str(V.candidate_reversal).lower()=="true"),
        }
        probs=np.array([row["p_aurora"],row["p_v5"],row["p_rift"],row["p_vega"]])
        row["expert_std"]=float(np.std(probs,ddof=0))
        row["gap_v5_rift"]=abs(row["p_v5"]-row["p_rift"])
        row["gap_v5_vega"]=abs(row["p_v5"]-row["p_vega"])
        gc=feature_for_series(series.get("GC"),d,issue,"gc")
        row.update(gc)
        for lab,prefix in [("SI","si"),("NQ","nq"),("ZN","zn"),("CL","cl")]:
            q=feature_for_series(series.get(lab),d,issue,prefix)
            row[f"{prefix}_anchor_to_cp"]=q.get(f"{prefix}_anchor_to_cp",np.nan)
        row["year"]=issue.year; row["quarter"]=f"{issue.year}-Q{((issue.month-1)//3)+1}"
        rows.append(row)
    z=pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)
    # primary GC availability is mandatory.
    z=z.dropna(subset=["gc_anchor_to_cp","gc_ret_1h","gc_ret_3h","gc_ret_6h"]).copy()
    return z

def make_model(name):
    if name=="LOGIT_L2":
        return Pipeline([
          ("imp",SimpleImputer(strategy="median")),
          ("scale",StandardScaler()),
          ("model",LogisticRegression(C=.5,solver="lbfgs",max_iter=3000,random_state=SEED))
        ])
    return Pipeline([
      ("imp",SimpleImputer(strategy="median")),
      ("model",HistGradientBoostingClassifier(max_depth=2,learning_rate=.05,max_iter=150,min_samples_leaf=20,l2_regularization=1.0,random_state=SEED))
    ])

def metrics(y,p):
    y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-6,1-1e-6);pred=(p>=.5).astype(int)
    return {"n":len(y),"accuracy":float(accuracy_score(y,pred)),"balanced_accuracy":float(balanced_accuracy_score(y,pred)),"brier":float(brier_score_loss(y,p)),"logloss":float(log_loss(y,p,labels=[0,1]))}

def fit(train,test,features,name):
    m=make_model(name);m.fit(train[features],train.d1_up.astype(int));p=m.predict_proba(test[features])[:,1]
    return m,p,metrics(test.d1_up,p)

def sel(y,p,t):
    y=np.asarray(y,int);p=np.asarray(p,float);mask=(p>=t)|(p<=1-t);pred=(p>=.5).astype(int)
    return {"threshold":t,"n":len(y),"actions":int(mask.sum()),"coverage":float(mask.mean()) if len(y) else None,"correct":int((pred[mask]==y[mask]).sum()) if mask.any() else 0,"accuracy":float((pred[mask]==y[mask]).mean()) if mask.any() else None}

def cstat(q,col):
    a=q[q[col]!="UNCERTAIN"]
    return {"n":len(q),"actions":len(a),"coverage":len(a)/len(q) if len(q) else None,"correct":int((a[col]==a.actual).sum()),"accuracy":float((a[col]==a.actual).mean()) if len(a) else None}

def main():
    series={}; source={}
    for lab,sym in SYMS.items():
        q,meta=fetch_one(lab,sym);series[lab]=q;source[lab]=meta;time.sleep(.5)
    if series["GC"] is None:
        raise RuntimeError("GC_HOURLY_UNAVAILABLE:"+json.dumps(source))
    z=build_panel(series)
    h1=z[(z.forecast_issue_date>=pd.Timestamp("2025-01-01"))&(z.forecast_issue_date<pd.Timestamp("2025-07-01"))]
    q3=z[(z.forecast_issue_date>=pd.Timestamp("2025-07-01"))&(z.forecast_issue_date<pd.Timestamp("2025-10-01"))]
    q4=z[(z.forecast_issue_date>=pd.Timestamp("2025-10-01"))&(z.forecast_issue_date<pd.Timestamp("2026-01-01"))]
    y26=z[z.year==2026]
    if min(len(h1),len(q3),len(q4),len(y26))<40:
        raise RuntimeError(f"INSUFFICIENT_PANEL h1={len(h1)} q3={len(q3)} q4={len(q4)} y26={len(y26)}")

    rows=[]
    for fam,features in FAMILIES.items():
        # Require each family feature to have at least 80% nonmissing in H1+Q3.
        ref=pd.concat([h1,q3])
        cov=float(ref[features].notna().mean().min())
        if cov<.80:
            rows.append({"family":fam,"model":"INELIGIBLE","feature_min_coverage":cov})
            continue
        for name in MODELS:
            _,p,m=fit(h1,q3,features,name)
            rows.append({"family":fam,"model":name,"feature_min_coverage":cov,**m})
    ss=pd.DataFrame(rows)
    cand=ss[ss.model!="INELIGIBLE"].copy()
    if cand.empty:raise RuntimeError("NO_ELIGIBLE_MODEL")
    fo={k:i for i,k in enumerate(FAMILIES)};mo={k:i for i,k in enumerate(MODELS)}
    cand["_fo"]=cand.family.map(fo);cand["_mo"]=cand.model.map(mo)
    cand=cand.sort_values(["brier","balanced_accuracy","accuracy","_fo","_mo"],ascending=[True,False,False,True,True])
    chosen=cand.iloc[0];family=str(chosen.family);name=str(chosen.model);features=FAMILIES[family]

    train_q4=pd.concat([h1,q3])
    _,p4,_=fit(train_q4,q4,features,name)
    th=pd.DataFrame([sel(q4.d1_up,p4,t) for t in THRESH])
    elig=th[th.coverage>=.50].sort_values(["accuracy","coverage","threshold"],ascending=[False,False,False])
    threshold=float(elig.iloc[0].threshold)

    train25=z[z.year==2025]
    model,p26,m26=fit(train25,y26,features,name)
    s26=sel(y26.d1_up,p26,threshold)
    # Simple operational benchmark: predict the final D1 sign from the observed
    # GC move between the prior 16:00 NY anchor and the 06:00 UTC checkpoint.
    naive_p=np.where(y26.gc_anchor_to_cp.astype(float)>=0,1.0,0.0)
    naive26=metrics(y26.d1_up,naive_p)
    naive_aug_mask=y26.forecast_issue_date.dt.strftime("%Y-%m").eq("2026-08")
    naive_aug=metrics(y26.loc[naive_aug_mask,"d1_up"],naive_p[naive_aug_mask.to_numpy()]) if naive_aug_mask.any() else None
    pred=y26[["feature_cutoff_date","forecast_issue_date","d1_up"]].copy()
    pred["p_up"]=p26
    pred["morning_action"]=np.where(p26>=threshold,"UP",np.where(p26<=1-threshold,"DOWN","UNCERTAIN"))

    cig=pd.read_csv(CIG);cig["feature_cutoff_date"]=pd.to_datetime(cig.feature_cutoff_date).dt.normalize();cig["forecast_issue_date"]=pd.to_datetime(cig.forecast_issue_date).dt.normalize()
    q=cig.merge(pred[["feature_cutoff_date","p_up","morning_action"]],on="feature_cutoff_date",how="left")
    q["actual"]=q.d1_actual
    ro=[];vr=[]
    for r in q.itertuples(index=False):
        meta=r.morning_action if isinstance(r.morning_action,str) else "UNCERTAIN"
        a=r.consensus;b=r.consensus
        if r.consensus=="UNCERTAIN" and meta!="UNCERTAIN":
            a=meta;b=meta
        elif r.consensus!="UNCERTAIN" and meta!="UNCERTAIN" and meta!=r.consensus:
            b="UNCERTAIN"
        ro.append(a);vr.append(b)
    q["resolve_only"]=ro;q["veto_resolve"]=vr
    overall={x:cstat(q,x) for x in ["consensus","resolve_only","veto_resolve"]}
    aug=q[q.forecast_issue_date.dt.strftime("%Y-%m")=="2026-08"]
    augstat={x:cstat(aug,x) for x in ["consensus","resolve_only","veto_resolve"]}
    promote={}
    for pol in ["resolve_only","veto_resolve"]:
        promote[pol]=bool(s26["accuracy"]>=.72 and s26["coverage"]>=.50 and overall[pol]["accuracy"]>=overall["consensus"]["accuracy"] and augstat[pol]["accuracy"]>=.75 and augstat[pol]["coverage"]>augstat["consensus"]["coverage"])

    result={
      "identity":"MORNING_D1_V1","checkpoint":"06:00 UTC / 09:00 Europe-Istanbul",
      "source_meta":source,"panel_n":len(z),
      "splits":{"2025H1":len(h1),"2025Q3":len(q3),"2025Q4":len(q4),"2026":len(y26)},
      "selected":{"family":family,"model":name,"threshold":threshold,"features":features},
      "selection_2025Q3":ss.to_dict("records"),"threshold_2025Q4":th.to_dict("records"),
      "test_2026":{"full":m26,"selective":s26,"naive_overnight_sign":naive26,"naive_august":naive_aug},
      "cig_2026":overall,"august_2026":augstat,"promotion":promote
    }
    (OUT/"MORNING_D1_V1_RESULT.json").write_text(json.dumps(result,indent=2,default=str)+"\n")
    ss.to_csv(OUT/"MORNING_D1_V1_SELECTION.csv",index=False);th.to_csv(OUT/"MORNING_D1_V1_THRESHOLDS.csv",index=False)
    pred.to_csv(OUT/"MORNING_D1_V1_2026_PREDICTIONS.csv",index=False);q.to_csv(OUT/"MORNING_D1_V1_CIG_INTEGRATION.csv",index=False)
    if name=="LOGIT_L2":
        coef=model.named_steps["model"].coef_[0]
        pd.DataFrame({"feature":features,"std_coefficient":coef,"abs_std_coefficient":np.abs(coef)}).sort_values("abs_std_coefficient",ascending=False).to_csv(OUT/"MORNING_D1_V1_LOGIT_COEFFICIENTS.csv",index=False)

    def pc(x):return "—" if x is None else f"{100*x:.2f}%"
    lines=[
      "# MORNING-D1 V1 — 09:00 TR MICROSTATE NOWCAST RESULT","",
      f"**Selected:** {family} / {name} / threshold {threshold:.2f}","",
      "## Source availability","",
      "| Channel | Status | Rows | First | Last |","|---|---|---:|---|---|"
    ]
    for k,m in source.items(): lines.append(f"| {k} | {m.get('status')} | {m.get('rows','')} | {m.get('first','')} | {m.get('last','')} |")
    lines += ["","## 2025-Q3 selection","",
      "| Family | Model | Feature min coverage | Acc | BA | Brier |","|---|---|---:|---:|---:|---:|"]
    for r in ss.itertuples(index=False):
        if r.model=="INELIGIBLE":lines.append(f"| {r.family} | INELIGIBLE | {pc(r.feature_min_coverage)} | — | — | — |")
        else: lines.append(f"| {r.family} | {r.model} | {pc(r.feature_min_coverage)} | {pc(r.accuracy)} | {pc(r.balanced_accuracy)} | {r.brier:.4f} |")
    lines += ["","## 2025-Q4 frozen threshold","",
      "| t | Actions | Coverage | Correct | Accuracy |","|---:|---:|---:|---:|---:|"]
    for r in th.itertuples(index=False):lines.append(f"| {r.threshold:.2f} | {r.actions} | {pc(r.coverage)} | {r.correct} | {pc(r.accuracy)} |")
    lines += ["","## 2026 untouched test","",
      f"- full accuracy: **{pc(m26['accuracy'])}**; BA **{pc(m26['balanced_accuracy'])}**; Brier **{m26['brier']:.4f}**",
      f"- selective: **{s26['correct']}/{s26['actions']} = {pc(s26['accuracy'])}**, coverage **{pc(s26['coverage'])}**",
      f"- naive observed overnight GC sign: **{pc(naive26['accuracy'])}** (August **{pc(naive_aug['accuracy']) if naive_aug else '—'}**)","",
      "## CIG integration","",
      "| Policy | 2026 actions | Acc | Coverage | Aug actions | Aug acc | Aug coverage |","|---|---:|---:|---:|---:|---:|---:|"]
    for pol in ["consensus","resolve_only","veto_resolve"]:
        a=overall[pol];b=augstat[pol];lines.append(f"| {pol} | {a['actions']} | {pc(a['accuracy'])} | {pc(a['coverage'])} | {b['actions']} | {pc(b['accuracy'])} | {pc(b['coverage'])} |")
    lines += ["","## Promotion",f"- RESOLVE_ONLY: **{'PASS' if promote['resolve_only'] else 'FAIL'}**",f"- VETO_RESOLVE: **{'PASS' if promote['veto_resolve'] else 'FAIL'}**","",
      "This is a later-information nowcast and must not be represented as a prior-close forecast. Raw hourly vendor values are not persisted in repository outputs."
    ]
    (OUT/"MORNING_D1_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"MORNING_D1_V1_RESULT.md").read_text())
    print(json.dumps(result,indent=2,default=str))

if __name__=="__main__":
    main()
