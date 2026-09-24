from __future__ import annotations
import argparse, csv, json, math, os
from datetime import date
from pathlib import Path
import numpy as np
import psycopg
from scipy.stats import rankdata

IDENTITY="GOLD_CONTROL_SQRT_MEMORY_POLICY_2025_TRANSPORT_2026_STRESS_V1"
TABLE="public.xau_intraday_research_cache_5m"
TZ="America/New_York"
MIN_BARS=240
EPS=1e-14
PRIMARY_W=500
BAND=(475,500,525,550)
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
    cc=float(np.corrcoef(ec,gc)[0,1]); cd=float(np.corrcoef(ed,gd)[0,1])
    return {"passed":bool(len(common)>=300 and cc>=0.999 and cd>=0.90),
            "n":len(common),"close_corr":cc,"dr_corr":cd,
            "median_abs_relative_close_diff":float(np.median(np.abs(ec-gc)/np.maximum(np.abs(gc),1e-12))),
            "median_dr_ratio_ext_to_gov":float(np.median(np.maximum(ed,EPS)/np.maximum(gd,EPS)))}

def combine(ext,gov):
    rows=[x for x in ext if x[0].year<=2021] + [x for x in gov if x[0].year>=2022]
    rows=sorted(rows,key=lambda z:z[0]); ds=[x[0] for x in rows]
    if len(ds)!=len(set(ds)): raise RuntimeError("DUPLICATE_DATES_AFTER_SPLICE")
    return ds,np.array([x[1] for x in rows],float),np.array([x[2] for x in rows],float)

def build_rows(ds,close,dr):
    sd=np.sqrt(dr); rets=np.full(len(ds),np.nan); rets[1:]=np.log(close[1:]/close[:-1])
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
    X,y=Xy(train); b=np.linalg.lstsq(X,y,rcond=None)[0]
    Xt,_=Xy(test); sd=Xt@b
    if np.any(~np.isfinite(sd)) or np.any(sd<=0): raise RuntimeError("NONPOSITIVE_SD")
    pred=sd*sd; actual_dr=np.array([r["target_dr"] for r in test],float)
    hi=nearest_rank([r["target_dr"] for r in train],.80)
    actual=(actual_dr>=hi).astype(int); alert=(pred>=hi)
    tp=int(np.sum(alert&(actual==1))); fp=int(np.sum(alert&(actual==0))); fn=int(np.sum((~alert)&(actual==1)))
    return {
      "formation_n":len(train),"test_n":len(test),"high_risk_threshold":hi,
      "mse":float(np.mean((pred-actual_dr)**2)),
      "qlike":float(np.mean([qloss(a,b) for a,b in zip(actual_dr,pred)])),
      "auc":roc_auc(actual,pred),
      "coverage":float(np.mean(alert)),
      "precision":tp/(tp+fp) if tp+fp else None,
      "recall":tp/(tp+fn) if tp+fn else None,
      "alerts":int(np.sum(alert)),"tp":tp,"fp":fp,"fn":fn
    }

def seg_prefix(rows):
    X,y=Xy(rows); n=len(y); p=X.shape[1]
    Pxx=np.zeros((n+1,p,p)); Pxy=np.zeros((n+1,p)); Pyy=np.zeros(n+1)
    for i in range(n):
        Pxx[i+1]=Pxx[i]+np.outer(X[i],X[i]); Pxy[i+1]=Pxy[i]+X[i]*y[i]; Pyy[i+1]=Pyy[i]+y[i]*y[i]
    return Pxx,Pxy,Pyy

def seg_sse(Pxx,Pxy,Pyy,a,b):
    xx=Pxx[b]-Pxx[a]; xy=Pxy[b]-Pxy[a]; yy=Pyy[b]-Pyy[a]
    beta=np.linalg.lstsq(xx,xy,rcond=None)[0]
    return max(float(yy-2*beta@xy+beta@xx@beta),1e-30)

def segmented_last_break(rows,max_breaks=3):
    n=len(rows); p=4
    Pxx,Pxy,Pyy=seg_prefix(rows)
    pts=sorted(set([0,n]+list(range(BREAK_MIN_SEG,n-BREAK_MIN_SEG+1,BREAK_GRID_STEP))))
    dp={(1,e):(seg_sse(Pxx,Pxy,Pyy,0,e),[]) for e in pts if e>=BREAK_MIN_SEG}
    cands=[]
    for segs in range(1,max_breaks+2):
        if segs>1:
            for end in pts:
                if end<segs*BREAK_MIN_SEG: continue
                opts=[]
                for k in pts:
                    if k<(segs-1)*BREAK_MIN_SEG or end-k<BREAK_MIN_SEG: continue
                    prev=dp.get((segs-1,k))
                    if prev is not None: opts.append((prev[0]+seg_sse(Pxx,Pxy,Pyy,k,end),prev[1]+[k]))
                if opts: dp[(segs,end)]=min(opts,key=lambda z:z[0])
        if (segs,n) in dp:
            ss,br=dp[(segs,n)]; kpar=segs*p+(segs-1)
            cands.append((n*math.log(max(ss/n,1e-30))+kpar*math.log(n),br,ss))
    bic,br,ss=min(cands,key=lambda z:z[0])
    return (br[-1] if br else None),{"selected_breaks":len(br),"break_dates":[rows[k]["target_date"].isoformat() for k in br],"bic":bic}

def eval_year(rows,year):
    cutoff=date(year-1,12,31)
    train=[r for r in rows if r["target_date"]<=cutoff]
    test=[r for r in rows if r["target_date"].year==year]
    if len(train)<550 or not test: raise RuntimeError(f"INSUFFICIENT_YEAR:{year}:{len(train)}:{len(test)}")
    res={"EXPANDING":score(train,test)}
    for w in BAND: res[f"W{w}"]=score(train[-w:],test)
    idx,bi=segmented_last_break(train); bc=train[idx:] if idx is not None else train
    res["BREAK_CONDITIONED"]={**score(bc,test),"break":bi,"effective_window":len(bc)}
    return {"year":year,"formation_cutoff":cutoff.isoformat(),"last_target_date":test[-1]["target_date"].isoformat(),"policies":res}

def supportive(primary,expanding):
    return bool(primary["mse"]<=expanding["mse"] and primary["qlike"]<=expanding["qlike"]
                and primary["auc"] is not None and expanding["auc"] is not None
                and primary["auc"]>=expanding["auc"]-0.02 and primary["alerts"]>=1)

def transport_label(primary,expanding):
    if supportive(primary,expanding): return "SUPPORTIVE"
    if primary["mse"]>expanding["mse"] and primary["qlike"]>expanding["qlike"]: return "NOT_SUPPORTIVE"
    if primary["alerts"]==0: return "NOT_SUPPORTIVE"
    return "MIXED"

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--external-spine",type=Path,required=True)
    args=ap.parse_args(); out=Path("memory_transport_out"); out.mkdir(exist_ok=True)
    ext=load_external(args.external_spine); gov=load_governed(); audit=overlap_audit(ext,gov)
    if not audit["passed"]: raise RuntimeError(f"SOURCE_HARMONIZATION_FAIL:{audit}")
    ds,close,dr=combine(ext,gov); rows=build_rows(ds,close,dr)

    y25=eval_year(rows,2025)
    e25=y25["policies"]["EXPANDING"]; p25=y25["policies"]["W500"]
    primary_label=transport_label(p25,e25)
    band_flags={w:supportive(y25["policies"][f"W{w}"],e25) for w in BAND}
    n_support=sum(band_flags.values())
    band_label="SUPPORTIVE" if n_support>=3 else ("MIXED" if n_support==2 else "NOT_SUPPORTIVE")

    # 2026 is descriptive stress only; no selection label is allowed.
    y26=eval_year(rows,2026)

    result={
      "identity":IDENTITY,"date":"2026-09-24",
      "frozen_policy":{"primary_window":500,"robustness_envelope":list(BAND)},
      "source_overlap_audit":audit,
      "panel_first_day":ds[0].isoformat(),"panel_last_day":ds[-1].isoformat(),
      "stage5_locked_2025":{
        **y25,
        "primary_transport_label":primary_label,
        "band_supportive_flags":{str(k):v for k,v in band_flags.items()},
        "band_supportive_count":n_support,
        "band_transport_label":band_label,
        "policy_changed_after_open":False
      },
      "stage6_2026_stress":{
        **y26,
        "selection_or_tuning_allowed":False,
        "stress_only":True,
        "interpretation_status":"DESCRIPTIVE_ONLY_NO_MODEL_SELECTION"
      },
      "governance":{
        "2025_used_for_prior_selection":False,
        "2025_used_only_after_freeze":True,
        "2026_used_for_selection":False,
        "random_split":False,"production_writes":False,"runtime_promotion":False
      }
    }
    (out/"GOLD_CONTROL_SQRT_MEMORY_POLICY_2025_TRANSPORT_2026_STRESS_V1_RESULT_2026-09-24.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({
      "stage5_primary_label":primary_label,
      "stage5_band_label":band_label,
      "stage5_band_flags":band_flags,
      "stage5":y25,
      "stage6":y26,
      "panel_last_day":ds[-1].isoformat()
    },indent=2))

if __name__=="__main__": main()
