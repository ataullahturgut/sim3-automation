from __future__ import annotations

import csv, hashlib, json, math, os
from datetime import date
from pathlib import Path

import numpy as np
import psycopg
from sklearn.linear_model import LogisticRegression
from scipy.stats import rankdata

IDENTITY="DOWNSIDE_META_FALSE_ALARM_VETO_V1_RESEARCH"
PARENT_CSV=Path("gold_axis_2026/GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_FORECASTS_2026-09-22.csv")
TABLE="public.xau_intraday_research_cache_5m"
TZ="America/New_York"
YEARS=(2024,2025,2026)
FEATURES=("log_risk_margin","representation_disagreement","origin_close_return","signed_semivariance_imbalance","risk_acceleration")
EPS=1e-12

def db_url():
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v: raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def load_parent():
    with PARENT_CSV.open(newline="") as f:
        rows=list(csv.DictReader(f))
    out=[]
    for r in rows:
        o=dict(r)
        for k in [
            "dr_d","dr_w","dr_m","sd_d","sd_w","sd_m","target_dr","target_sd","target_close_return",
            "formation_mean_dr","high_risk_threshold","extreme_return_threshold","raw_har_dr_forecast",
            "sqrt_har_sd_forecast","sqrt_har_dr_forecast","raw_normalized_risk_score","sqrt_normalized_risk_score"
        ]:
            o[k]=float(o[k])
        for k in ["evaluation_year","formation_n","actual_high_risk","raw_high_risk_alert","sqrt_high_risk_alert"]:
            o[k]=int(float(o[k]))
        out.append(o)
    return out

def load_intraday_features():
    sql=f"""
    with b as (
      select
        (observation_ts at time zone '{TZ}')::date as d,
        observation_ts,
        close::double precision as close,
        lag(close::double precision) over (
          partition by (observation_ts at time zone '{TZ}')::date
          order by observation_ts
        ) as prev_close
      from {TABLE}
      where extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
    ),
    r as (
      select d,observation_ts,close,
             case when prev_close>0 then ln(close/prev_close) end as ret
      from b
    ),
    a as (
      select d,
             count(*)::int as bars,
             (array_agg(close order by observation_ts desc))[1]::double precision as day_close,
             sum(case when ret<0 then ret*ret else 0 end)::double precision as rsminus,
             sum(case when ret>0 then ret*ret else 0 end)::double precision as rsplus
      from r group by d
    ),
    e as (
      select d,bars,day_close,rsminus,rsplus,
             lag(day_close) over(order by d) as prev_day_close
      from a
      where bars>=240
    )
    select d::text,bars,day_close,prev_day_close,rsminus,rsplus
    from e
    order by d
    """
    with psycopg.connect(db_url(),autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only=on")
            cur.execute(sql)
            raw=cur.fetchall()
    out={}
    for d,bars,c,pc,rsm,rsp in raw:
        if pc is None: continue
        c=float(c);pc=float(pc);rsm=float(rsm);rsp=float(rsp)
        den=rsm+rsp
        if not(c>0 and pc>0 and den>0): continue
        out[str(d)]={
            "origin_close_return":math.log(c/pc),
            "signed_semivariance_imbalance":(rsm-rsp)/den,
            "bars":int(bars)
        }
    return out

def enrich(parent,intra):
    rows=[]
    for r in parent:
        d=r["origin_date"]
        if d not in intra: raise RuntimeError(f"MISSING_INTRADAY:{d}")
        risk=float(r["sqrt_normalized_risk_score"])
        rawf=float(r["raw_har_dr_forecast"]); sqrtf=float(r["sqrt_har_dr_forecast"])
        if not(risk>0 and rawf>0 and sqrtf>0 and r["sd_d"]>0 and r["sd_w"]>0):
            raise RuntimeError(f"BAD_FEATURE_DOMAIN:{d}")
        x=dict(r)
        x["log_risk_margin"]=math.log(risk)
        x["representation_disagreement"]=math.log(sqrtf/rawf)
        x["origin_close_return"]=intra[d]["origin_close_return"]
        x["signed_semivariance_imbalance"]=intra[d]["signed_semivariance_imbalance"]
        x["risk_acceleration"]=math.log(float(r["sd_d"])/float(r["sd_w"]))
        x["meta_y"]=int(float(r["target_close_return"])<0)
        rows.append(x)
    return rows

def panel_hash(rows):
    s="\n".join(
        f"{r['origin_date']}|{r['target_date']}|{r['sqrt_normalized_risk_score']:.12g}|"
        f"{r['raw_har_dr_forecast']:.12g}|{r['sqrt_har_dr_forecast']:.12g}|"
        f"{r['origin_close_return']:.12g}|{r['signed_semivariance_imbalance']:.12g}|"
        f"{r['risk_acceleration']:.12g}|{r['meta_y']}"
        for r in rows
    )
    return hashlib.sha256(s.encode()).hexdigest()

def Xy(rows):
    X=np.asarray([[float(r[k]) for k in FEATURES] for r in rows],float)
    y=np.asarray([int(r["meta_y"]) for r in rows],int)
    return X,y

def standardize_fit(X):
    mu=X.mean(axis=0); sd=X.std(axis=0,ddof=1)
    sd=np.where(sd>1e-12,sd,1.0)
    return mu,sd

def fit_logit(rows):
    X,y=Xy(rows)
    if len(np.unique(y))<2: raise RuntimeError("ONE_CLASS_META_TRAIN")
    mu,sd=standardize_fit(X)
    m=LogisticRegression(C=1.0,penalty="l2",solver="lbfgs",fit_intercept=True,class_weight=None,max_iter=5000)
    m.fit((X-mu)/sd,y)
    return m,mu,sd

def predict_prob(fit,rows):
    m,mu,sd=fit
    X,_=Xy(rows)
    return m.predict_proba((X-mu)/sd)[:,1]

def loo_probs(rows):
    X,y=Xy(rows)
    if len(rows)<4 or len(np.unique(y))<2: return None
    out=np.full(len(rows),np.nan)
    for i in range(len(rows)):
        keep=np.ones(len(rows),dtype=bool);keep[i]=False
        yt=y[keep]
        if len(np.unique(yt))<2: return None
        Xtr=X[keep];mu,sd=standardize_fit(Xtr)
        m=LogisticRegression(C=1.0,penalty="l2",solver="lbfgs",fit_intercept=True,class_weight=None,max_iter=5000)
        m.fit((Xtr-mu)/sd,yt)
        out[i]=m.predict_proba(((X[i:i+1]-mu)/sd))[:,1][0]
    return out

def auc(y,s):
    y=np.asarray(y,int);s=np.asarray(s,float)
    n1=int(np.sum(y==1));n0=int(np.sum(y==0))
    if n1==0 or n0==0:return None
    r=rankdata(s,method="average")
    return float((np.sum(r[y==1])-n1*(n1+1)/2)/(n1*n0))

def confusion(y,pred):
    y=np.asarray(y,int);pred=np.asarray(pred,bool)
    tp=int(np.sum(pred&(y==1)));fp=int(np.sum(pred&(y==0)))
    fn=int(np.sum((~pred)&(y==1)));tn=int(np.sum((~pred)&(y==0)))
    rec=tp/(tp+fn) if tp+fn else None
    spec=tn/(tn+fp) if tn+fp else None
    prec=tp/(tp+fp) if tp+fp else None
    ba=(rec+spec)/2 if rec is not None and spec is not None else None
    return {"n":len(y),"actual_down":int(np.sum(y)),"confirm_count":int(np.sum(pred)),
            "tp":tp,"fp":fp,"fn":fn,"tn":tn,"precision":prec,"recall":rec,
            "specificity":spec,"balanced_accuracy":ba}

def select_recall75(rows):
    y=np.asarray([int(r["meta_y"]) for r in rows],int)
    p=loo_probs(rows)
    if p is None:return None,{"status":"NOT_PROVEN"}
    candidates=np.unique(np.r_[0.0,p,1.0])
    best=None
    for t in candidates:
        c=confusion(y,p>=t)
        if c["recall"] is None or c["recall"]<0.75 or c["confirm_count"]==0: continue
        score=(c["precision"] if c["precision"] is not None else -1,
               c["balanced_accuracy"] if c["balanced_accuracy"] is not None else -1,
               float(t))
        if best is None or score>best[0]:
            best=(score,float(t),c)
    if best is None:return None,{"status":"NO_FEASIBLE_THRESHOLD"}
    return best[1],{"status":"OK","loo_threshold_metrics":best[2],"loo_auc":auc(y,p),
                    "loo_brier":float(np.mean((p-y)**2))}

def evaluate_variant(train,test,threshold_mode):
    fit=fit_logit(train)
    p=predict_prob(fit,test)
    y=np.asarray([int(r["meta_y"]) for r in test],int)
    if threshold_mode=="P050":
        t=0.5; sel={"status":"FIXED"}
    elif threshold_mode=="RECALL75":
        t,sel=select_recall75(train)
        if t is None:return {"status":"NOT_PROVEN","threshold_selection":sel}
    else: raise ValueError(threshold_mode)
    c=confusion(y,p>=t)
    c.update({
        "status":"OK","threshold":float(t),"meta_auc":auc(y,p),
        "meta_brier":float(np.mean((p-y)**2)),
        "mean_p":float(np.mean(p)),
        "threshold_selection":sel
    })
    return c

def add_reference_fields(m,ref):
    if m.get("status")!="OK": return m
    ref_fp=ref["fp"]; ref_tp=ref["tp"]
    m["false_alarm_reduction_count"]=ref_fp-m["fp"]
    m["false_alarm_reduction_rate"]=(ref_fp-m["fp"])/ref_fp if ref_fp else None
    m["true_down_retention_rate"]=m["tp"]/ref_tp if ref_tp else None
    return m

def year_eval(rows,year):
    cutoff=date(year-1,12,31)
    hist=[r for r in rows if date.fromisoformat(r["target_date"])<=cutoff]
    test=[r for r in rows if int(r["evaluation_year"])==year and int(r["sqrt_high_risk_alert"])==1]
    if not test: raise RuntimeError(f"NO_TEST_ALERTS:{year}")
    strict=[r for r in hist if int(r["sqrt_high_risk_alert"])==1]
    context=[r for r in hist if float(r["sqrt_normalized_risk_score"])>=0.80]
    y=np.asarray([int(r["meta_y"]) for r in test],int)
    ref=confusion(y,np.ones(len(y),dtype=bool))
    out={"test_alarm_n":len(test),"test_actual_down":int(np.sum(y)),
         "strict_train_n":len(strict),"strict_train_down":int(sum(r["meta_y"] for r in strict)),
         "context_train_n":len(context),"context_train_down":int(sum(r["meta_y"] for r in context)),
         "reference_all_as_down":ref,"variants":{}}
    for pool_name,pool in [("STRICT",strict),("CONTEXT",context)]:
        for mode in ("P050","RECALL75"):
            name=f"{pool_name}_{mode}"
            try:
                m=evaluate_variant(pool,test,mode)
            except Exception as e:
                m={"status":"FAILED","error":str(e)}
            out["variants"][name]=add_reference_fields(m,ref)
    return out

def main():
    out=Path("meta_veto_out");out.mkdir(exist_ok=True)
    parent=load_parent();intra=load_intraday_features();rows=enrich(parent,intra)
    years={str(y):year_eval(rows,y) for y in YEARS}

    # Pre-2025 gate is based only on 2024.
    gate={}
    y24=years["2024"]
    ref=y24["reference_all_as_down"]
    for name,m in y24["variants"].items():
        ok=bool(
            m.get("status")=="OK"
            and m["fp"]<ref["fp"]
            and m["recall"] is not None and m["recall"]>=0.70
            and m["balanced_accuracy"] is not None and m["balanced_accuracy"]>0.55
            and m["meta_auc"] is not None and m["meta_auc"]>0.55
        )
        gate[name]="PRE2025_META_VETO_SIGNAL" if ok else "PRE2025_META_VETO_NOT_SUPPORTED"

    result={
      "identity":IDENTITY,"manifest_modified":False,"production_write":"NONE",
      "evidence_classification":"2024_SMALL_SAMPLE_RETROSPECTIVE_FALSIFICATION_2025_2026_STRESS_ONLY",
      "feature_names":list(FEATURES),"context_boundary":0.80,
      "panel_sha256":panel_hash(rows),"years":years,"pre2025_gate":gate
    }
    (out/"GOLD_CONTROL_DOWNSIDE_META_FALSE_ALARM_VETO_V1_RESULT_2026-09-22.json").write_text(json.dumps(result,indent=2))

    lines=["# GOLD CONTROL — META FALSE-ALARM VETO V1 RESULT","",
           "**Manifest modified:** NO  ","",
           "| Year | Variant | TP | FP | FN | TN | Precision | Recall | BA | AUC | FA reduction | DOWN retained |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for y in YEARS:
        b=years[str(y)]
        for name,m in b["variants"].items():
            if m.get("status")!="OK":
                lines.append(f"| {y} | {name} | - | - | - | - | - | - | - | - | - | - |")
                continue
            def f(v):
                return "-" if v is None else f"{v:.4f}"
            lines.append(
                f"| {y} | {name} | {m['tp']} | {m['fp']} | {m['fn']} | {m['tn']} | "
                f"{f(m['precision'])} | {f(m['recall'])} | {f(m['balanced_accuracy'])} | "
                f"{f(m['meta_auc'])} | {f(m['false_alarm_reduction_rate'])} | {f(m['true_down_retention_rate'])} |"
            )
    lines+=["","## 2024 pre-2025 gate",""]
    for name,status in gate.items(): lines.append(f"- {name}: `{status}`")
    (out/"GOLD_CONTROL_DOWNSIDE_META_FALSE_ALARM_VETO_V1_RESULT_2026-09-22.md").write_text("\n".join(lines)+"\n")
    print("META_VETO_SUCCESS")

if __name__=="__main__": main()
