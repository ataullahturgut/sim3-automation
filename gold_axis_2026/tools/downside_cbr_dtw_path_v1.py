from __future__ import annotations

import csv, json, math, os, hashlib
from datetime import date
from pathlib import Path

import numpy as np
import psycopg
from scipy.stats import rankdata

IDENTITY="DOWNSIDE_CBR_DTW_PATH_V1_RESEARCH"
PARENT=Path("gold_axis_2026/GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_FORECASTS_2026-09-22.csv")
TABLE="public.xau_intraday_research_cache_5m"
TZ="America/New_York"
YEARS=(2024,2025,2026)
NPTS=48
BAND=6
K=3
EPS=1e-8

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
        for k in ["target_close_return","sqrt_normalized_risk_score","sqrt_har_dr_forecast","raw_har_dr_forecast"]:
            o[k]=float(o[k])
        for k in ["evaluation_year","sqrt_high_risk_alert"]:
            o[k]=int(float(o[k]))
        o["meta_y"]=int(o["target_close_return"]<0)
        out.append(o)
    return out

def load_paths(parent_dates):
    mind=min(parent_dates); maxd=max(parent_dates)
    sql=f"""
    with b as (
      select
        (observation_ts at time zone '{TZ}')::date as d,
        observation_ts,
        close::double precision as close,
        lag(close::double precision) over(
          partition by (observation_ts at time zone '{TZ}')::date
          order by observation_ts
        ) as prev_close
      from {TABLE}
      where (observation_ts at time zone '{TZ}')::date between %s::date and %s::date
        and extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
    )
    select d::text,observation_ts,
           case when prev_close>0 then ln(close/prev_close) end as ret
    from b
    order by d,observation_ts
    """
    with psycopg.connect(db_url(),autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only=on")
            cur.execute(sql,(mind,maxd))
            raw=cur.fetchall()
    grouped={}
    for d,ts,r in raw:
        if r is None: continue
        grouped.setdefault(str(d),[]).append(float(r))
    return grouped

def path_repr(rets):
    r=np.asarray(rets,float)
    if len(r)<239: raise RuntimeError(f"TOO_FEW_RETURNS:{len(r)}")
    rv=float(np.sum(r*r))
    if not(rv>0): raise RuntimeError("ZERO_RV")
    cum=np.cumsum(r)/math.sqrt(rv)
    press=np.cumsum(np.where(r<0,r*r,-r*r))/rv
    xold=np.linspace(0.0,1.0,len(r))
    xnew=np.linspace(0.0,1.0,NPTS)
    p=np.interp(xnew,xold,cum)
    s=np.interp(xnew,xold,press)
    return np.column_stack([p,s])

def enrich(parent,rawpaths):
    out=[]
    for r in parent:
        d=r["origin_date"]
        if d not in rawpaths: raise RuntimeError(f"MISSING_PATH:{d}")
        x=dict(r)
        x["path"]=path_repr(rawpaths[d])
        out.append(x)
    return out

def panel_hash(rows):
    parts=[]
    for r in rows:
        a=r["path"]
        parts.append(f"{r['origin_date']}|{r['target_date']}|{r['meta_y']}|"+
                     ",".join(f"{v:.10g}" for v in a.ravel()))
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()

def dtw(a,b):
    n=len(a);m=len(b)
    inf=1e100
    D=np.full((n+1,m+1),inf,float);D[0,0]=0.0
    for i in range(1,n+1):
        j0=max(1,i-BAND);j1=min(m,i+BAND)
        for j in range(j0,j1+1):
            diff=a[i-1]-b[j-1]
            cost=float(np.dot(diff,diff))
            D[i,j]=cost+min(D[i-1,j],D[i,j-1],D[i-1,j-1])
    val=D[n,m]
    if not math.isfinite(val): raise RuntimeError("DTW_FAIL")
    return math.sqrt(val/(n+m))

def case_prob(train,target):
    if len(train)<K: return None,None
    ds=[]
    for r in train:
        d=dtw(r["path"],target["path"])
        ds.append((d,int(r["meta_y"])))
    ds.sort(key=lambda x:x[0])
    nn=ds[:K]
    exact=[y for d,y in nn if d<1e-12]
    if exact:
        p=float(np.mean(exact))
    else:
        w=np.array([1.0/(d+EPS) for d,y in nn],float)
        y=np.array([y for d,y in nn],float)
        p=float(np.sum(w*y)/np.sum(w))
    return p,float(np.mean([d for d,y in nn]))

def loo_probs(train):
    if len(train)<=K:return None
    y=np.array([int(r["meta_y"]) for r in train],int)
    if len(np.unique(y))<2:return None
    p=np.full(len(train),np.nan);dist=np.full(len(train),np.nan)
    for i,t in enumerate(train):
        others=[r for j,r in enumerate(train) if j!=i]
        pp,dd=case_prob(others,t)
        if pp is None:return None
        p[i]=pp;dist[i]=dd
    return p,dist

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

def select_recall75(train):
    z=loo_probs(train)
    if z is None:return None,{"status":"NOT_PROVEN"}
    p,dist=z
    y=np.array([int(r["meta_y"]) for r in train],int)
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
    return best[1],{"status":"OK","loo_metrics":best[2],"loo_auc":auc(y,p),
                    "loo_brier":float(np.mean((p-y)**2)),
                    "loo_mean_neighbor_distance":float(np.mean(dist))}

def evaluate(train,test,mode):
    if len(train)<K or len(set(int(r["meta_y"]) for r in train))<2:
        return {"status":"NOT_PROVEN"}
    probs=[];dists=[]
    for t in test:
        p,d=case_prob(train,t)
        probs.append(p);dists.append(d)
    probs=np.asarray(probs,float)
    y=np.asarray([int(r["meta_y"]) for r in test],int)
    if mode=="P050":
        thr=0.5;sel={"status":"FIXED"}
    elif mode=="RECALL75":
        thr,sel=select_recall75(train)
        if thr is None:return {"status":"NOT_PROVEN","threshold_selection":sel}
    else: raise ValueError(mode)
    c=confusion(y,probs>=thr)
    c.update({"status":"OK","threshold":float(thr),"auc":auc(y,probs),
              "brier":float(np.mean((probs-y)**2)),
              "mean_neighbor_distance":float(np.mean(dists)),
              "mean_p":float(np.mean(probs)),
              "threshold_selection":sel})
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
    strict=[r for r in hist if int(r["sqrt_high_risk_alert"])==1]
    context=[r for r in hist if float(r["sqrt_normalized_risk_score"])>=0.80]
    y=np.array([int(r["meta_y"]) for r in test],int)
    ref=confusion(y,np.ones(len(y),bool))
    out={"test_alarm_n":len(test),"test_actual_down":int(np.sum(y)),
         "strict_train_n":len(strict),"strict_train_down":int(sum(r["meta_y"] for r in strict)),
         "context_train_n":len(context),"context_train_down":int(sum(r["meta_y"] for r in context)),
         "reference_all_as_down":ref,"variants":{}}
    for pname,pool in [("STRICT",strict),("CONTEXT",context)]:
        for mode in ("P050","RECALL75"):
            name=f"{pname}_{mode}"
            try:m=evaluate(pool,test,mode)
            except Exception as e:m={"status":"FAILED","error":str(e)}
            out["variants"][name]=add_ref(m,ref)
    return out

def main():
    out=Path("cbr_dtw_out");out.mkdir(exist_ok=True)
    parent=load_parent()
    dates=[r["origin_date"] for r in parent]
    raw=load_paths(dates)
    rows=enrich(parent,raw)
    years={str(y):year_eval(rows,y) for y in YEARS}
    gate={}
    ref=years["2024"]["reference_all_as_down"]
    for name,m in years["2024"]["variants"].items():
        ok=bool(m.get("status")=="OK" and m["fp"]<ref["fp"] and
                m["recall"] is not None and m["recall"]>=0.70 and
                m["balanced_accuracy"] is not None and m["balanced_accuracy"]>0.55 and
                m["auc"] is not None and m["auc"]>0.55)
        gate[name]="PRE2025_PATH_MORPHOLOGY_SIGNAL" if ok else "PRE2025_PATH_MORPHOLOGY_NOT_SUPPORTED"
    result={"identity":IDENTITY,"manifest_modified":False,"production_write":"NONE",
            "evidence_classification":"2024_SMALL_SAMPLE_RETROSPECTIVE_FALSIFICATION_2025_2026_STRESS_ONLY",
            "representation":{"points":NPTS,"channels":["normalized_cumulative_return","cumulative_signed_variance_pressure"],
                              "dtw_band":BAND,"k":K},
            "panel_sha256":panel_hash(rows),"years":years,"pre2025_gate":gate}
    (out/"GOLD_CONTROL_DOWNSIDE_CBR_DTW_PATH_V1_RESULT_2026-09-22.json").write_text(json.dumps(result,indent=2))

    lines=["# GOLD CONTROL — CBR-DTW PATH MORPHOLOGY V1 RESULT","",
           "**Manifest modified:** NO  ","",
           "| Year | Variant | TP | FP | FN | TN | Precision | Recall | BA | AUC | FA reduction | DOWN retained |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    def fmt(v): return "-" if v is None else f"{v:.4f}"
    for y in YEARS:
        for name,m in years[str(y)]["variants"].items():
            if m.get("status")!="OK":
                lines.append(f"| {y} | {name} | - | - | - | - | - | - | - | - | - | - |")
                continue
            lines.append(f"| {y} | {name} | {m['tp']} | {m['fp']} | {m['fn']} | {m['tn']} | "
                         f"{fmt(m['precision'])} | {fmt(m['recall'])} | {fmt(m['balanced_accuracy'])} | "
                         f"{fmt(m['auc'])} | {fmt(m['false_alarm_reduction_rate'])} | {fmt(m['true_down_retention_rate'])} |")
    lines+=["","## 2024 pre-2025 gate",""]
    for name,status in gate.items(): lines.append(f"- {name}: `{status}`")
    (out/"GOLD_CONTROL_DOWNSIDE_CBR_DTW_PATH_V1_RESULT_2026-09-22.md").write_text("\n".join(lines)+"\n")
    print("CBR_DTW_SUCCESS")

if __name__=="__main__": main()
