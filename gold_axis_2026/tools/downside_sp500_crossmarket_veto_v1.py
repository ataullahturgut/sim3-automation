from __future__ import annotations

import csv, json, math, os, hashlib
from datetime import date
from pathlib import Path

import numpy as np
import psycopg
from sklearn.linear_model import LogisticRegression
from scipy.stats import rankdata

IDENTITY="DOWNSIDE_SP500_CROSSMARKET_VETO_V1_RESEARCH"
PARENT=Path("gold_axis_2026/GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_FORECASTS_2026-09-22.csv")
SPID="SP500_FRED"
YEARS=(2024,2025,2026)
EPS=1e-12

def db_url():
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v: raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def load_parent():
    with PARENT.open(newline="") as f:
        rows=list(csv.DictReader(f))
    out=[]
    for r in rows:
        o=dict(r)
        for k in ["target_close_return","sqrt_normalized_risk_score"]:
            o[k]=float(o[k])
        for k in ["evaluation_year","sqrt_high_risk_alert"]:
            o[k]=int(float(o[k]))
        o["meta_y"]=int(o["target_close_return"]<0)
        out.append(o)
    return out

def load_sp500():
    sql="""
    with d as (
      select distinct on (observation_ts::date)
             observation_ts::date d,
             value::double precision value,
             retrieved_at
      from public.observations
      where series_id=%s
        and value is not null
      order by observation_ts::date, retrieved_at desc nulls last, id desc
    )
    select d::text,value from d order by d
    """
    with psycopg.connect(db_url(),autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only=on")
            cur.execute(sql,(SPID,))
            raw=cur.fetchall()
    ds=[date.fromisoformat(str(d)) for d,v in raw]
    vals=np.array([float(v) for d,v in raw],float)
    if len(vals)<1000: raise RuntimeError(f"SP500_TOO_SHORT:{len(vals)}")
    if np.any(vals<=0): raise RuntimeError("SP500_NONPOSITIVE")
    ret=np.full(len(vals),np.nan);ret[1:]=np.log(vals[1:]/vals[:-1])
    ret5=np.full(len(vals),np.nan)
    for i in range(5,len(vals)): ret5[i]=math.log(vals[i]/vals[i-5])
    vol20=np.full(len(vals),np.nan)
    for i in range(20,len(vals)):
        vol20[i]=float(np.std(ret[i-19:i+1],ddof=1))
    return ds,vals,ret,ret5,vol20

def align(parent,sp):
    ds,vals,ret,ret5,vol20=sp
    ords=np.array([d.toordinal() for d in ds])
    out=[];stale=0
    for r in parent:
        od=date.fromisoformat(r["origin_date"])
        i=int(np.searchsorted(ords,od.toordinal(),side="right")-1)
        if i<20: continue
        age=(od-ds[i]).days
        if age>4:
            stale+=1
            continue
        if not(math.isfinite(ret[i]) and math.isfinite(ret5[i]) and math.isfinite(vol20[i]) and vol20[i]>0):
            continue
        x=dict(r)
        x["sp_date"]=ds[i].isoformat()
        x["sp_age_days"]=age
        x["sp_ret1"]=float(ret[i])
        x["sp_ret5"]=float(ret5[i])
        x["sp_vol20"]=float(vol20[i])
        x["sp_z1"]=float(ret[i]/vol20[i])
        x["gold_risk_margin"]=float(math.log(r["sqrt_normalized_risk_score"]))
        out.append(x)
    return out,stale

def panel_hash(rows):
    s="\n".join(f"{r['origin_date']}|{r['target_date']}|{r['sp_date']}|{r['sp_ret1']:.12g}|{r['sp_ret5']:.12g}|{r['sp_z1']:.12g}|{r['gold_risk_margin']:.12g}|{r['meta_y']}" for r in rows)
    return hashlib.sha256(s.encode()).hexdigest()

def nearest_rank(a,q):
    a=np.asarray(a,float)
    k=max(1,min(len(a),int(math.ceil(q*len(a)))))
    return float(np.sort(a)[k-1])

def auc(y,s):
    y=np.asarray(y,int);s=np.asarray(s,float)
    n1=int(np.sum(y==1));n0=int(np.sum(y==0))
    if not n1 or not n0:return None
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

FEATURES=("sp_ret1","sp_ret5","sp_z1","gold_risk_margin")

def Xy(rows):
    X=np.asarray([[float(r[k]) for k in FEATURES] for r in rows],float)
    y=np.asarray([int(r["meta_y"]) for r in rows],int)
    return X,y

def fit_logit(rows):
    X,y=Xy(rows)
    if len(np.unique(y))<2: raise RuntimeError("ONE_CLASS")
    mu=X.mean(0);sd=X.std(0,ddof=1);sd=np.where(sd>1e-12,sd,1.0)
    m=LogisticRegression(C=1.0,penalty="l2",solver="lbfgs",fit_intercept=True,max_iter=5000)
    m.fit((X-mu)/sd,y)
    return m,mu,sd

def probs(fit,rows):
    m,mu,sd=fit;X,_=Xy(rows)
    return m.predict_proba((X-mu)/sd)[:,1]

def loo_probs(rows):
    X,y=Xy(rows)
    if len(rows)<5 or len(np.unique(y))<2:return None
    out=np.full(len(rows),np.nan)
    for i in range(len(rows)):
        keep=np.ones(len(rows),bool);keep[i]=False
        yt=y[keep]
        if len(np.unique(yt))<2:return None
        Xt=X[keep];mu=Xt.mean(0);sd=Xt.std(0,ddof=1);sd=np.where(sd>1e-12,sd,1.0)
        m=LogisticRegression(C=1.0,penalty="l2",solver="lbfgs",fit_intercept=True,max_iter=5000)
        m.fit((Xt-mu)/sd,yt)
        out[i]=m.predict_proba(((X[i:i+1]-mu)/sd))[:,1][0]
    return out

def select_recall75(train):
    p=loo_probs(train)
    if p is None:return None,{"status":"NOT_PROVEN"}
    y=np.asarray([int(r["meta_y"]) for r in train],int)
    best=None
    for t in np.unique(np.r_[0.0,p,1.0]):
        c=confusion(y,p>=t)
        if c["recall"] is None or c["recall"]<0.75 or c["confirm_count"]==0:continue
        score=(c["precision"] if c["precision"] is not None else -1,
               c["balanced_accuracy"] if c["balanced_accuracy"] is not None else -1,
               float(t))
        if best is None or score>best[0]:best=(score,float(t),c)
    if best is None:return None,{"status":"NO_FEASIBLE_THRESHOLD"}
    return best[1],{"status":"OK","loo_metrics":best[2],"loo_auc":auc(y,p),
                    "loo_brier":float(np.mean((p-y)**2))}

def eval_logit(train,test,mode):
    fit=fit_logit(train);p=probs(fit,test);y=np.asarray([r["meta_y"] for r in test],int)
    if mode=="P050":
        t=0.5;sel={"status":"FIXED"}
    else:
        t,sel=select_recall75(train)
        if t is None:return {"status":"NOT_PROVEN","threshold_selection":sel}
    c=confusion(y,p>=t)
    c.update({"status":"OK","threshold":float(t),"auc":auc(y,p),
              "brier":float(np.mean((p-y)**2)),"threshold_selection":sel})
    return c

def add_ref(m,ref):
    if m.get("status")!="OK":return m
    m["false_alarm_reduction_count"]=ref["fp"]-m["fp"]
    m["false_alarm_reduction_rate"]=(ref["fp"]-m["fp"])/ref["fp"] if ref["fp"] else None
    m["true_down_retention_rate"]=m["tp"]/ref["tp"] if ref["tp"] else None
    return m

def year_eval(rows,year):
    cutoff=date(year-1,12,31)
    hist=[r for r in rows if date.fromisoformat(r["target_date"])<=cutoff]
    test=[r for r in rows if int(r["evaluation_year"])==year and int(r["sqrt_high_risk_alert"])==1]
    if not test: raise RuntimeError(f"NO_ALERTS:{year}")
    y=np.asarray([r["meta_y"] for r in test],int)
    ref=confusion(y,np.ones(len(y),bool))

    # Mechanism-first Q10 rule
    q10=nearest_rank(np.asarray([r["sp_ret1"] for r in hist]),.10)
    veto=np.asarray([r["sp_ret1"]<=q10 for r in test],bool)
    q10m=confusion(y,~veto)
    q10m.update({"status":"OK","formation_sp_ret1_q10":q10,
                 "veto_count":int(np.sum(veto)),
                 "veto_down_rate":float(np.mean(y[veto])) if np.sum(veto) else None,
                 "nonveto_down_rate":float(np.mean(y[~veto])) if np.sum(~veto) else None})
    q10m=add_ref(q10m,ref)

    train=[r for r in hist if float(r["sqrt_normalized_risk_score"])>=0.80]
    out={"test_alarm_n":len(test),"test_actual_down":int(np.sum(y)),
         "context_train_n":len(train),"context_train_down":int(sum(r["meta_y"] for r in train)),
         "reference_all_as_down":ref,"Q10_RULE":q10m,"LOGIT_P050":None,"LOGIT_RECALL75":None}
    for mode,key in [("P050","LOGIT_P050"),("RECALL75","LOGIT_RECALL75")]:
        try:m=eval_logit(train,test,mode)
        except Exception as e:m={"status":"FAILED","error":str(e)}
        out[key]=add_ref(m,ref)
    return out

def main():
    out=Path("sp500_veto_out");out.mkdir(exist_ok=True)
    parent=load_parent();sp=load_sp500();rows,stale=align(parent,sp)
    years={str(y):year_eval(rows,y) for y in YEARS}
    gates={}
    y24=years["2024"];ref=y24["reference_all_as_down"]
    q=y24["Q10_RULE"]
    qok=bool(q["fp"]<ref["fp"] and q["recall"]>=0.70 and q["balanced_accuracy"]>0.55 and
             q["veto_down_rate"] is not None and q["nonveto_down_rate"] is not None and q["veto_down_rate"]<q["nonveto_down_rate"])
    gates["Q10_RULE"]="PRE2025_CROSSMARKET_VETO_SIGNAL" if qok else "PRE2025_CROSSMARKET_VETO_NOT_SUPPORTED"
    for key in ("LOGIT_P050","LOGIT_RECALL75"):
        m=y24[key]
        ok=bool(m.get("status")=="OK" and m["fp"]<ref["fp"] and m["recall"]>=0.70 and m["balanced_accuracy"]>0.55 and m["auc"]>0.55)
        gates[key]="PRE2025_CROSSMARKET_VETO_SIGNAL" if ok else "PRE2025_CROSSMARKET_VETO_NOT_SUPPORTED"

    result={"identity":IDENTITY,"manifest_modified":False,"production_write":"NONE",
            "sp500_series_id":SPID,"historical_sp500_n":len(sp[0]),
            "aligned_parent_rows":len(rows),"stale_exclusions":stale,
            "panel_sha256":panel_hash(rows),"years":years,"pre2025_gate":gates}
    (out/"GOLD_CONTROL_DOWNSIDE_SP500_CROSSMARKET_VETO_V1_RESULT_2026-09-22.json").write_text(json.dumps(result,indent=2))

    lines=["# GOLD CONTROL — SP500 CROSS-MARKET VETO V1 RESULT","",
           "**Manifest modified:** NO  ","",
           "| Year | Variant | TP | FP | FN | TN | Precision | Recall | BA | AUC | FA reduction | DOWN retained |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    def fmt(v): return "-" if v is None else f"{v:.4f}"
    for y in YEARS:
        b=years[str(y)]
        for name in ("Q10_RULE","LOGIT_P050","LOGIT_RECALL75"):
            m=b[name]
            if m.get("status")!="OK":
                lines.append(f"| {y} | {name} | - | - | - | - | - | - | - | - | - | - |")
                continue
            lines.append(f"| {y} | {name} | {m['tp']} | {m['fp']} | {m['fn']} | {m['tn']} | "
                         f"{fmt(m['precision'])} | {fmt(m['recall'])} | {fmt(m['balanced_accuracy'])} | "
                         f"{fmt(m.get('auc'))} | {fmt(m['false_alarm_reduction_rate'])} | {fmt(m['true_down_retention_rate'])} |")
    lines+=["","## 2024 pre-2025 gate",""]
    for k,v in gates.items():lines.append(f"- {k}: `{v}`")
    (out/"GOLD_CONTROL_DOWNSIDE_SP500_CROSSMARKET_VETO_V1_RESULT_2026-09-22.md").write_text("\n".join(lines)+"\n")
    print("SP500_VETO_SUCCESS")

if __name__=="__main__": main()
