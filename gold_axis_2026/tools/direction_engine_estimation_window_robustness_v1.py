from __future__ import annotations
import csv, json, math, os
from datetime import date
from pathlib import Path
import numpy as np
import psycopg
from scipy.stats import rankdata

IDENTITY="DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1"
TABLE="public.xau_intraday_research_cache_5m"
TZ="America/New_York"
MIN_BARS=240
MIN_FORMATION=250
PRE_YEARS=(2022,2023,2024)
EPS=1e-14

def db_url():
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v: raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def nearest_rank(a,q):
    a=np.asarray(a,float)
    k=max(1,min(len(a),int(math.ceil(q*len(a)))))
    return float(np.sort(a)[k-1])

def load_days():
    sql=f"""
    with b as (
      select (observation_ts at time zone '{TZ}')::date as d,
             observation_ts, close::double precision as close,
             lag(close::double precision) over (
               partition by (observation_ts at time zone '{TZ}')::date
               order by observation_ts
             ) as prev_close
      from {TABLE}
      where observation_ts < '2025-01-01'::timestamptz
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
            cur.execute(sql)
            raw=cur.fetchall()
    ds=[]; close=[]; dr=[]
    for d,n,c,x in raw:
        c=float(c); x=float(x)
        if not(math.isfinite(c) and c>0 and math.isfinite(x) and x>=0):
            raise RuntimeError(f"BAD_ROW:{d}")
        ds.append(d); close.append(c); dr.append(x)
    if not ds or ds[-1] >= date(2025,1,1):
        raise RuntimeError("LOCKED_PERIOD_LEAK")
    return ds,np.asarray(close,float),np.asarray(dr,float)

def build_rows(ds,close,dr):
    sd=np.sqrt(dr)
    rets=np.full(len(ds),np.nan); rets[1:]=np.log(close[1:]/close[:-1])
    out=[]
    for i in range(21,len(ds)-1):
        t=i+1
        out.append({
          "origin_date":ds[i],"target_date":ds[t],
          "sd_d":float(sd[i]),"sd_w":float(np.mean(sd[i-4:i+1])),
          "sd_m":float(np.mean(sd[i-21:i+1])),
          "target_sd":float(sd[t]),"target_dr":float(dr[t]),
          "target_close_return":float(rets[t]),
        })
    return out

def Xy(rows):
    X=np.array([[1.,r["sd_d"],r["sd_w"],r["sd_m"]] for r in rows],float)
    y=np.array([r["target_sd"] for r in rows],float)
    return X,y

def fit(rows):
    X,y=Xy(rows)
    b=np.linalg.lstsq(X,y,rcond=None)[0]
    return b

def roc_auc(y,s):
    y=np.asarray(y,int); s=np.asarray(s,float)
    n1=int(np.sum(y==1)); n0=int(np.sum(y==0))
    if not n1 or not n0: return None
    r=rankdata(s,method="average")
    return float((np.sum(r[y==1])-n1*(n1+1)/2)/(n1*n0))

def qloss(y,f):
    yy=max(float(y),EPS); ff=max(float(f),EPS)
    z=yy/ff
    return z-math.log(z)-1

def score(train,test):
    b=fit(train)
    Xt,_=Xy(test)
    sd= Xt@b
    if np.any(~np.isfinite(sd)) or np.any(sd<=0): return None
    pred=sd*sd
    y=np.array([r["target_dr"] for r in test],float)
    mse=float(np.mean((pred-y)**2))
    q=float(np.mean([qloss(a,b) for a,b in zip(y,pred)]))
    train_dr=np.array([r["target_dr"] for r in train],float)
    hi=nearest_rank(train_dr,.80)
    actual=(y>=hi).astype(int); alert=(pred>=hi).astype(int)
    auc=roc_auc(actual,pred)
    cov=float(np.mean(alert))
    prec=float(np.sum(alert&(actual==1))/np.sum(alert)) if np.sum(alert) else None
    rec=float(np.sum(alert&(actual==1))/np.sum(actual==1)) if np.sum(actual==1) else None
    return {"mse":mse,"qlike":q,"auc":auc,"coverage":cov,"precision":prec,"recall":rec,
            "alerts":int(np.sum(alert)),"n":len(test)}

def grid_for(n):
    vals=list(range(MIN_FORMATION,n+1,25))
    if n>=MIN_FORMATION and (not vals or vals[-1]!=n): vals.append(n)
    return sorted(set(vals))

def segmented_last_break(rows,max_breaks=3,min_seg=125):
    X,y=Xy(rows); n=len(y); p=X.shape[1]
    if n<2*min_seg: return None,{"n":n,"selected_breaks":0,"bic":None}
    sse=np.full((n,n),np.inf)
    for i in range(0,n-min_seg+1):
        for j in range(i+min_seg,n+1):
            xx=X[i:j]; yy=y[i:j]
            b=np.linalg.lstsq(xx,yy,rcond=None)[0]
            e=yy-xx@b
            sse[i,j-1]=float(e@e)
    best={}
    # segments = 1..max_breaks+1
    dp={(1,j):(sse[0,j],[]) for j in range(min_seg-1,n)}
    candidates=[]
    for segs in range(1,max_breaks+2):
        if segs>1:
            for j in range(segs*min_seg-1,n):
                opts=[]
                for k in range((segs-1)*min_seg-1,j-min_seg+1):
                    prev=dp.get((segs-1,k))
                    if prev is None or not np.isfinite(sse[k+1,j]): continue
                    opts.append((prev[0]+sse[k+1,j],prev[1]+[k]))
                if opts: dp[(segs,j)]=min(opts,key=lambda z:z[0])
        key=(segs,n-1)
        if key in dp:
            ss,br=dp[key]
            kpar=segs*p + (segs-1)
            bic=n*math.log(max(ss/n,1e-30))+kpar*math.log(n)
            candidates.append((bic,segs,br,ss))
    if not candidates: return None,{"n":n,"selected_breaks":0,"bic":None}
    bic,segs,br,ss=min(candidates,key=lambda z:z[0])
    if not br: return None,{"n":n,"selected_breaks":0,"bic":bic,"sse":ss}
    idx=br[-1]+1
    return idx,{"n":n,"selected_breaks":len(br),"break_indices":[x+1 for x in br],
                "break_dates":[rows[x+1]["target_date"].isoformat() for x in br],"bic":bic,"sse":ss}

def main():
    out=Path("history_robustness_out"); out.mkdir(exist_ok=True)
    ds,close,dr=load_days(); rows=build_rows(ds,close,dr)
    if min(r["target_date"] for r in rows).year>2020:
        raise RuntimeError("HISTORY_TOO_SHORT")
    allres=[]; yearly_meta={}
    for year in PRE_YEARS:
        cutoff=date(year-1,12,31)
        train=[r for r in rows if r["target_date"]<=cutoff]
        test=[r for r in rows if r["target_date"].year==year]
        if len(train)<MIN_FORMATION or not test:
            yearly_meta[str(year)]={"status":"UNAVAILABLE","train_n":len(train),"test_n":len(test)}
            continue
        # Expanding
        m=score(train,test)
        allres.append({"year":year,"policy":"EXPANDING","window":len(train),**m})
        # Rolling surface
        for w in grid_for(len(train)):
            mm=score(train[-w:],test)
            if mm is not None:
                allres.append({"year":year,"policy":"ROLLING","window":w,**mm})
        # Origin-safe segmented regression/BIC break-conditioned
        idx,bi=segmented_last_break(train)
        bc=train[idx:] if idx is not None else train
        bm=score(bc,test)
        allres.append({"year":year,"policy":"BREAK_CONDITIONED","window":len(bc),**bm,
                       "break_date":bi.get("break_dates",[""])[-1] if bi.get("break_dates") else "",
                       "break_count":bi.get("selected_breaks",0)})
        yearly_meta[str(year)]={"status":"OK","train_n":len(train),"test_n":len(test),"break":bi}

    # Common rolling windows across all available pre-years
    by_w={}
    for r in allres:
        if r["policy"]=="ROLLING":
            by_w.setdefault(r["window"],[]).append(r)
    common={w:v for w,v in by_w.items() if len(v)==len(PRE_YEARS)}
    surface=[]
    for w,v in sorted(common.items()):
        surface.append({
          "window":w,
          "years":len(v),
          "mean_mse":float(np.mean([x["mse"] for x in v])),
          "mean_qlike":float(np.mean([x["qlike"] for x in v])),
          "mean_auc":float(np.mean([x["auc"] for x in v if x["auc"] is not None])),
          "coverage_sd":float(np.std([x["coverage"] for x in v])),
          "min_precision":min([x["precision"] for x in v if x["precision"] is not None],default=None)
        })
    # Normalize ranks: lower MSE/QLIKE/coverage instability better, higher AUC better.
    def ranks(vals,reverse=False):
        order=np.argsort([-x if reverse else x for x in vals])
        rr=np.empty(len(vals),int)
        for i,j in enumerate(order): rr[j]=i+1
        return rr
    robust=[]
    if surface:
        rm=ranks([x["mean_mse"] for x in surface])
        rq=ranks([x["mean_qlike"] for x in surface])
        ra=ranks([x["mean_auc"] for x in surface],reverse=True)
        rs=ranks([x["coverage_sd"] for x in surface])
        for i,x in enumerate(surface):
            z=dict(x); z["rank_score"]=float((rm[i]+rq[i]+ra[i]+rs[i])/4); robust.append(z)
        robust.sort(key=lambda x:(x["rank_score"],x["window"]))
    top=robust[:max(1,min(10,len(robust)))]
    if top:
        ws=sorted(x["window"] for x in top)
        robust_band={"top_n":len(top),"min_window":ws[0],"max_window":ws[-1],
                     "median_window":float(np.median(ws)),"members":ws}
    else:
        robust_band=None

    result={
      "identity":IDENTITY,
      "status":"PRE2025_ONLY_COMPLETE",
      "source_table":TABLE,
      "panel_first_day":ds[0].isoformat(),"panel_last_day":ds[-1].isoformat(),
      "locked_2025_used":False,"y2026_used":False,
      "formula_changed":False,
      "yearly_meta":yearly_meta,
      "rolling_surface":robust,
      "robust_band":robust_band,
      "policy_rows":allres,
      "structural_break_method":"origin-safe segmented OLS dynamic programming, 0..3 breaks, min segment 125, BIC selection; Bai-Perron-style approximation",
      "governance":{"random_split":False,"production_writes":False,"runtime_promotion":False}
    }
    (out/"GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_RESULT_2026-09-24.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    fields=sorted({k for r in allres for k in r})
    with (out/"GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_SURFACE_2026-09-24.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(allres)
    print(json.dumps({"status":result["status"],"robust_band":robust_band,"yearly_meta":yearly_meta},indent=2))
if __name__=="__main__": main()
