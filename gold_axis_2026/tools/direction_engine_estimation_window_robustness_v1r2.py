from __future__ import annotations
import argparse, csv, json, math, os
from datetime import date
from pathlib import Path
import numpy as np
import psycopg
from scipy.stats import rankdata

IDENTITY="DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1R2"
TABLE="public.xau_intraday_research_cache_5m"
TZ="America/New_York"
MIN_BARS=240
MIN_FORMATION=250
PRE_YEARS=(2022,2023,2024)
EPS=1e-14
GRID_STEP=25
BREAK_GRID_STEP=5
BREAK_MIN_SEG=125

def db_url():
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v: raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def nearest_rank(a,q):
    a=np.asarray(a,float)
    if len(a)==0: raise RuntimeError("EMPTY_QUANTILE")
    k=max(1,min(len(a),int(math.ceil(q*len(a)))))
    return float(np.sort(a)[k-1])

def load_external(path:Path):
    out=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d=date.fromisoformat(r["date"])
            if d.year>2021: continue
            c=float(r["close_mid"]); dr=float(r["dr_5m"])
            if not(math.isfinite(c) and c>0 and math.isfinite(dr) and dr>=0):
                raise RuntimeError(f"BAD_EXTERNAL:{d}")
            out.append((d,c,dr))
    return out

def load_governed():
    sql=f"""
    with b as (
      select (observation_ts at time zone '{TZ}')::date as d,
             observation_ts, close::double precision as close,
             lag(close::double precision) over (
               partition by (observation_ts at time zone '{TZ}')::date
               order by observation_ts
             ) as prev_close
      from {TABLE}
      where observation_ts >= '2020-01-01'::timestamptz
        and observation_ts < '2025-01-01'::timestamptz
        and extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
    ),
    intr as (
      select d,observation_ts,close,
             case when prev_close is not null and prev_close>0 then ln(close/prev_close) end as r
      from b
    )
    select d,count(*)::int as n_bars,
           (array_agg(close order by observation_ts desc))[1]::double precision as close,
           coalesce(sum(case when r<=0 then r*r else 0 end),0)::double precision as dr
    from intr group by d having count(*) >= {MIN_BARS} order by d
    """
    with psycopg.connect(db_url(),autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only=on")
            cur.execute(sql); raw=cur.fetchall()
    out=[]
    for d,n,c,x in raw:
        c=float(c); x=float(x)
        if not(math.isfinite(c) and c>0 and math.isfinite(x) and x>=0):
            raise RuntimeError(f"BAD_GOV:{d}")
        out.append((d,c,x))
    return out

def overlap_audit(ext,gov):
    em={d:(c,x) for d,c,x in ext if d.year in (2020,2021)}
    gm={d:(c,x) for d,c,x in gov if d.year in (2020,2021)}
    common=sorted(set(em)&set(gm))
    if not common: return {"passed":False,"n":0}
    ec=np.array([em[d][0] for d in common]); gc=np.array([gm[d][0] for d in common])
    ed=np.array([em[d][1] for d in common]); gd=np.array([gm[d][1] for d in common])
    cc=float(np.corrcoef(ec,gc)[0,1]) if np.std(ec)>0 and np.std(gc)>0 else None
    cd=float(np.corrcoef(ed,gd)[0,1]) if np.std(ed)>0 and np.std(gd)>0 else None
    rel_close=float(np.median(np.abs(ec-gc)/np.maximum(np.abs(gc),1e-12)))
    ratio_dr=float(np.median(np.maximum(ed,EPS)/np.maximum(gd,EPS)))
    passed=bool(len(common)>=300 and cc is not None and cc>=0.999 and cd is not None and cd>=0.90)
    return {"passed":passed,"n":len(common),"close_corr":cc,"dr_corr":cd,
            "median_abs_relative_close_diff":rel_close,"median_dr_ratio_ext_to_gov":ratio_dr}

def combine(ext,gov):
    # Binding splice: external through 2021, governed from 2022. Never mix same date.
    rows=[x for x in ext if x[0].year<=2021] + [x for x in gov if 2022<=x[0].year<=2024]
    rows=sorted(rows,key=lambda z:z[0])
    ds=[x[0] for x in rows]
    if len(ds)!=len(set(ds)): raise RuntimeError("DUPLICATE_DATES_AFTER_SPLICE")
    if ds[-1]>=date(2025,1,1): raise RuntimeError("LOCKED_PERIOD_LEAK")
    return ds,np.array([x[1] for x in rows],float),np.array([x[2] for x in rows],float)

def build_rows(ds,close,dr):
    sd=np.sqrt(dr)
    rets=np.full(len(ds),np.nan); rets[1:]=np.log(close[1:]/close[:-1])
    out=[]
    for i in range(21,len(ds)-1):
        t=i+1
        out.append({"origin_date":ds[i],"target_date":ds[t],
          "sd_d":float(sd[i]),"sd_w":float(np.mean(sd[i-4:i+1])),
          "sd_m":float(np.mean(sd[i-21:i+1])),
          "target_sd":float(sd[t]),"target_dr":float(dr[t]),
          "target_close_return":float(rets[t])})
    return out

def Xy(rows):
    X=np.array([[1.,r["sd_d"],r["sd_w"],r["sd_m"]] for r in rows],float)
    y=np.array([r["target_sd"] for r in rows],float)
    return X,y

def fit(rows):
    X,y=Xy(rows)
    return np.linalg.lstsq(X,y,rcond=None)[0]

def roc_auc(y,s):
    y=np.asarray(y,int); s=np.asarray(s,float)
    n1=int(np.sum(y==1)); n0=int(np.sum(y==0))
    if not n1 or not n0: return None
    r=rankdata(s,method="average")
    return float((np.sum(r[y==1])-n1*(n1+1)/2)/(n1*n0))

def qloss(y,f):
    yy=max(float(y),EPS); ff=max(float(f),EPS); z=yy/ff
    return z-math.log(z)-1

def score(train,test):
    b=fit(train); Xt,_=Xy(test); sd=Xt@b
    if np.any(~np.isfinite(sd)) or np.any(sd<=0): return None
    pred=sd*sd; y=np.array([r["target_dr"] for r in test],float)
    hi=nearest_rank([r["target_dr"] for r in train],.80)
    actual=(y>=hi).astype(int); alert=(pred>=hi)
    tp=int(np.sum(alert&(actual==1))); fp=int(np.sum(alert&(actual==0)))
    fn=int(np.sum((~alert)&(actual==1)))
    return {
      "mse":float(np.mean((pred-y)**2)),
      "qlike":float(np.mean([qloss(a,b) for a,b in zip(y,pred)])),
      "auc":roc_auc(actual,pred),
      "coverage":float(np.mean(alert)),
      "precision":tp/(tp+fp) if tp+fp else None,
      "recall":tp/(tp+fn) if tp+fn else None,
      "alerts":int(np.sum(alert)),"n":len(test)}

def window_grid(n):
    vals=list(range(MIN_FORMATION,n+1,GRID_STEP))
    if vals[-1]!=n: vals.append(n)
    return sorted(set(vals))

def seg_prefix(rows):
    X,y=Xy(rows); n=len(y); p=X.shape[1]
    Pxx=np.zeros((n+1,p,p)); Pxy=np.zeros((n+1,p)); Pyy=np.zeros(n+1)
    for i in range(n):
        Pxx[i+1]=Pxx[i]+np.outer(X[i],X[i])
        Pxy[i+1]=Pxy[i]+X[i]*y[i]
        Pyy[i+1]=Pyy[i]+y[i]*y[i]
    return X,y,Pxx,Pxy,Pyy

def seg_sse(Pxx,Pxy,Pyy,a,b):
    # [a,b)
    xx=Pxx[b]-Pxx[a]; xy=Pxy[b]-Pxy[a]; yy=Pyy[b]-Pyy[a]
    beta=np.linalg.lstsq(xx,xy,rcond=None)[0]
    val=float(yy-2*beta@xy+beta@xx@beta)
    return max(val,1e-30)

def segmented_last_break(rows,max_breaks=3):
    n=len(rows); p=4
    if n<2*BREAK_MIN_SEG: return None,{"n":n,"selected_breaks":0,"reason":"TOO_SHORT"}
    X,y,Pxx,Pxy,Pyy=seg_prefix(rows)
    pts=sorted(set([0,n]+list(range(BREAK_MIN_SEG,n-BREAK_MIN_SEG+1,BREAK_GRID_STEP))))
    # DP over candidate endpoints. state[(segments,end)] = (sse, breaks)
    dp={}
    for end in pts:
        if end>=BREAK_MIN_SEG:
            dp[(1,end)]=(seg_sse(Pxx,Pxy,Pyy,0,end),[])
    cands=[]
    for segs in range(1,max_breaks+2):
        if segs>1:
            for end in pts:
                if end<segs*BREAK_MIN_SEG: continue
                opts=[]
                for k in pts:
                    if k< (segs-1)*BREAK_MIN_SEG or end-k<BREAK_MIN_SEG: continue
                    prev=dp.get((segs-1,k))
                    if prev is None: continue
                    opts.append((prev[0]+seg_sse(Pxx,Pxy,Pyy,k,end),prev[1]+[k]))
                if opts: dp[(segs,end)]=min(opts,key=lambda z:z[0])
        key=(segs,n)
        if key in dp:
            ss,br=dp[key]; kpar=segs*p+(segs-1)
            bic=n*math.log(max(ss/n,1e-30))+kpar*math.log(n)
            cands.append((bic,segs,br,ss))
    if not cands: return None,{"n":n,"selected_breaks":0,"reason":"NO_DP_SOLUTION"}
    bic,segs,br,ss=min(cands,key=lambda z:z[0])
    dates=[rows[k]["target_date"].isoformat() for k in br]
    return (br[-1] if br else None),{"n":n,"selected_breaks":len(br),"break_indices":br,
      "break_dates":dates,"bic":bic,"sse":ss,"grid_step":BREAK_GRID_STEP,"min_segment":BREAK_MIN_SEG}

def evaluate(rows):
    policy_rows=[]; meta={}
    expanding={}
    for year in PRE_YEARS:
        cutoff=date(year-1,12,31)
        train=[r for r in rows if r["target_date"]<=cutoff]
        test=[r for r in rows if r["target_date"].year==year]
        if len(train)<MIN_FORMATION or not test:
            meta[str(year)]={"status":"UNAVAILABLE","train_n":len(train),"test_n":len(test)}
            continue
        em=score(train,test); expanding[year]=em
        policy_rows.append({"year":year,"policy":"EXPANDING","window":len(train),**em})
        for w in window_grid(len(train)):
            mm=score(train[-w:],test)
            if mm is not None: policy_rows.append({"year":year,"policy":"ROLLING","window":w,**mm})
        idx,bi=segmented_last_break(train)
        bc=train[idx:] if idx is not None else train
        bm=score(bc,test)
        policy_rows.append({"year":year,"policy":"BREAK_CONDITIONED","window":len(bc),**bm,
          "break_date":bi.get("break_dates",[""])[-1] if bi.get("break_dates") else "",
          "break_count":bi.get("selected_breaks",0)})
        meta[str(year)]={"status":"OK","train_n":len(train),"test_n":len(test),"break":bi}
    return policy_rows,meta,expanding

def rolling_summary(policy_rows,expanding):
    by_w={}
    for r in policy_rows:
        if r["policy"]=="ROLLING": by_w.setdefault(r["window"],[]).append(r)
    out=[]
    for w,v in sorted(by_w.items()):
        yrs={r["year"]:r for r in v}
        comparisons=[]
        for y,r in yrs.items():
            e=expanding[y]
            comparisons.append({
              "year":y,
              "mse_ratio":r["mse"]/e["mse"],
              "qlike_ratio":r["qlike"]/e["qlike"],
              "auc_delta":None if r["auc"] is None or e["auc"] is None else r["auc"]-e["auc"],
              "coverage_delta":r["coverage"]-e["coverage"]})
        guard=[c for c in comparisons if c["mse_ratio"]<=1.02 and c["qlike_ratio"]<=1.02
               and (c["auc_delta"] is None or c["auc_delta"]>=-0.02)
               and abs(c["coverage_delta"])<=0.10]
        strict=[c for c in comparisons if c["mse_ratio"]<1 and c["qlike_ratio"]<1]
        out.append({"window":w,"years_tested":len(comparisons),"guard_years":len(guard),
          "strict_loss_improve_years":len(strict),"comparisons":comparisons})
    # Require all three pre-years and >=2 strict improvements, with guard in all years.
    eligible=[x for x in out if x["years_tested"]==3 and x["guard_years"]==3 and x["strict_loss_improve_years"]>=2]
    ws=sorted(x["window"] for x in eligible)
    bands=[]
    cur=[]
    for w in ws:
        if not cur or w-cur[-1] in (GRID_STEP,): cur.append(w)
        else:
            bands.append(cur); cur=[w]
    if cur: bands.append(cur)
    bands=[b for b in bands if len(b)>=3]
    return out,bands

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--external-spine",type=Path,required=True)
    args=ap.parse_args()
    out=Path("history_robustness_out"); out.mkdir(exist_ok=True)
    ext=load_external(args.external_spine); gov=load_governed(); audit=overlap_audit(ext,gov)
    if not audit["passed"]: raise RuntimeError(f"EXTERNAL_GOVERNED_HARMONIZATION_FAIL:{audit}")
    ds,close,dr=combine(ext,gov); rows=build_rows(ds,close,dr)
    policy_rows,meta,expanding=evaluate(rows)
    surface,bands=rolling_summary(policy_rows,expanding)
    break_counts=[meta[str(y)]["break"]["selected_breaks"] for y in PRE_YEARS]
    if bands:
        decision="ROBUST_ROLLING_CANDIDATE_BAND_FOUND"
    else:
        decision="NO_ROBUST_ROLLING_ADVANTAGE_PRE2025"
    break_decision="NO_ORIGIN_SAFE_BREAK_SELECTED" if all(x==0 for x in break_counts) else "BREAK_CONDITIONED_CANDIDATE_EXISTS"
    result={"identity":IDENTITY,"status":"PRE2025_FULL_HISTORY_COMPLETE",
      "source_policy":"external corrected daily spine through 2021; governed read-only Neon from 2022 through 2024",
      "source_overlap_audit":audit,"panel_first_day":ds[0].isoformat(),"panel_last_day":ds[-1].isoformat(),
      "locked_2025_used":False,"y2026_used":False,"formula_changed":False,
      "yearly_meta":meta,"rolling_surface":surface,"robust_bands":bands,
      "rolling_decision":decision,"break_decision":break_decision,
      "structural_break_method":"origin-safe segmented OLS dynamic programming on 5-row candidate grid; 0..3 breaks; min segment 125; BIC selection; Bai-Perron-style approximation",
      "policy_rows":policy_rows,
      "governance":{"random_split":False,"production_writes":False,"runtime_promotion":False}}
    (out/"GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1R2_RESULT_2026-09-24.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    fields=sorted({k for r in policy_rows for k in r})
    with (out/"GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1R2_SURFACE_2026-09-24.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(policy_rows)
    print(json.dumps({"status":result["status"],"rolling_decision":decision,
      "robust_bands":bands,"break_decision":break_decision,"yearly_meta":meta,
      "source_overlap_audit":audit},indent=2))
if __name__=="__main__": main()
