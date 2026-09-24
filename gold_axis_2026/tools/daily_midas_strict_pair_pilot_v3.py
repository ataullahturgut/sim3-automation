from __future__ import annotations
import argparse, json, math, os
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import psycopg
import daily_midas_clean_pilot_v2 as base

IDENTITY="GOLD_CONTROL_DAILY_MIDAS_STRICT_PAIR_PILOT_V3_RESEARCH"
FAST_LAGS=60
SLOW_LAGS=12
MIN_TRAIN=252
TAIL_Q=.67
START_SCORE=pd.Timestamp("2022-01-01")
END_SCORE=pd.Timestamp("2026-09-01")

def business_source(d,label):
    z=d.sort_values("date").drop_duplicates("date",keep="last").copy()
    raw_n=len(z);weekend=int((z.date.dt.weekday>=5).sum())
    z=z[z.date.dt.weekday<5].copy().reset_index(drop=True)
    z["ret"]=np.log(z.value/z.value.shift(1))
    z["target_date"]=z.date.shift(-1);z["target_value"]=z.value.shift(-1)
    z["gap_days"]=(z.target_date-z.date).dt.days
    z["pair_ok"]=z.gap_days.between(1,4)
    z["r_next"]=np.log(z.target_value/z.value)
    audit={"label":label,"raw_rows":raw_n,"weekend_rows_removed":weekend,"business_rows":len(z),
           "pair_ok":int(z.pair_ok.sum()),"gap_gt4":int((z.gap_days>4).fillna(False).sum()),
           "max_gap":int(z.gap_days.dropna().max()) if z.gap_days.notna().any() else None,
           "first":z.date.min().strftime("%Y-%m-%d"),"last":z.date.max().strftime("%Y-%m-%d")}
    return z,audit

def gpr_cutoff(origin_date,clock):
    d=pd.Timestamp(origin_date).date()
    if clock=="NY17_RESEARCH":
        local=pd.Timestamp(d).tz_localize(ZoneInfo("America/New_York"))+pd.Timedelta(hours=17)
        return local.tz_convert("UTC")
    # Proxy clock has no proven close time. Conservative: only vintages available by end of previous UTC day.
    return pd.Timestamp(d,tz="UTC")-pd.Timedelta(seconds=1)

def gpr_features(gpr,origin_date,clock):
    cutoff=gpr_cutoff(origin_date,clock)
    h=gpr[gpr.available_as_of<=cutoff].copy()
    if h.empty:return None
    h["obs_month"]=h.obs_ts.dt.strftime("%Y-%m")
    h=h.sort_values(["obs_month","available_as_of"]).groupby("obs_month",as_index=False).tail(1)
    vals={r.obs_month:float(r.value) for r in h.itertuples()}
    cur=base.month_shift(base.month_key(origin_date),-1);seq=[]
    for _ in range(SLOW_LAGS):
        if cur not in vals:return None
        seq.append(vals[cur]);cur=base.month_shift(cur,-1)
    return base.almon2(seq)+base.exp_basis(seq)

def add_basis(row,prefix,seq):
    for j,v in enumerate(base.almon2(seq)):row[f"{prefix}_A{j}"]=v
    for j,v in enumerate(base.exp_basis(seq)):row[f"{prefix}_E{j}"]=v

def build_panel(target,metals,sp500,gpr,clock):
    # target is full weekday business source, not a pre-filtered pair table.
    other={}
    for name,z in metals.items():
        q=z.copy();other[name]=q.set_index("date")["ret"]
    sp=sp500.set_index("date")["ret"]
    rows=[]
    for i,r in target.iterrows():
        if i<FAST_LAGS-1 or not bool(r.pair_ok) or not np.isfinite(r.r_next):continue
        od=pd.Timestamp(r.date)
        row={"origin_date":od,"target_date":pd.Timestamp(r.target_date),"r_next":float(r.r_next),
             "gap_days":int(r.gap_days)}
        # Current target-clock return is known at the forecast origin.
        for name,series in [("Gold",target.ret),("GoldAbs",target.ret.abs()),("GoldNeg",np.minimum(target.ret,0.0))]:
            seq=series.iloc[i-FAST_LAGS+1:i+1].to_numpy(float)[::-1];add_basis(row,f"G_{name}",seq)
        # Cross-source daily values are lagged strictly before origin date because exact same-day release/close clock is not proven.
        mok=True
        for name,ser in other.items():
            hist=ser.loc[ser.index<od].dropna().tail(FAST_LAGS)
            if len(hist)<FAST_LAGS:mok=False;break
            add_basis(row,f"M_{name}",hist.to_numpy(float)[::-1])
        row["metals_ok"]=mok
        sph=sp.loc[sp.index<od].dropna().tail(FAST_LAGS);row["sp500_ok"]=len(sph)>=FAST_LAGS
        if row["sp500_ok"]:add_basis(row,"X_SP500",sph.to_numpy(float)[::-1])
        gf=gpr_features(gpr,od,clock);row["gpr_ok"]=gf is not None
        if gf is not None:
            for j,v in enumerate(gf):row[f"S_GPR_{j}"]=v
        rows.append(row)
    p=pd.DataFrame(rows).sort_values("origin_date").reset_index(drop=True)
    if p.empty:return p
    # Equal-support panel for ALL ablations.
    p=p[p.metals_ok&p.sp500_ok&p.gpr_ok].copy().reset_index(drop=True)
    p["y_up"]=(p.r_next>0).astype(int)
    cuts=[]
    for i,r in p.iterrows():
        h=p.iloc[:i];h=h[h.target_date<r.origin_date]
        vals=h.r_next.abs().dropna().to_numpy(float)
        cuts.append(float(np.quantile(vals,TAIL_Q)) if len(vals)>=MIN_TRAIN else np.nan)
    p["tail_cutoff"]=cuts
    p["y_mat_down"]=(p.r_next < -p.tail_cutoff).astype(int)
    return p

def blocks(p):
    gold=[c for c in p if c.startswith("G_")]
    metals=[c for c in p if c.startswith("M_")]
    cross=[c for c in p if c.startswith("X_")]
    slow=[c for c in p if c.startswith("S_")]
    return {
      "GOLD_ONLY":gold,
      "GOLD_PLUS_METALS":gold+metals,
      "GOLD_PLUS_CROSS":gold+cross,
      "GOLD_PLUS_SLOW_MIDAS":gold+slow,
      "GOLD_METALS_CROSS":gold+metals+cross,
      "FULL_MIXED_FREQ_MIDAS":gold+metals+cross+slow,
    }

def walk_monthly(p,features,target):
    rows=[]
    q=p[(p.origin_date>=START_SCORE)&(p.origin_date<END_SCORE)].copy()
    if q.empty:return pd.DataFrame()
    q["ym"]=q.origin_date.dt.strftime("%Y-%m")
    ycol="y_up" if target=="UP" else "y_mat_down"
    for ym,g in q.groupby("ym",sort=True):
        first=g.origin_date.min()
        h=p[(p.target_date<first)&(p.origin_date<first)].copy()
        if target=="MAT_DOWN":h=h[np.isfinite(h.tail_cutoff)].copy()
        if len(h)<MIN_TRAIN:continue
        y=h[ycol].to_numpy(int)
        if len(np.unique(y))<2:continue
        m=base.model_logit("L2");m.fit(h[features],y)
        pr=m.predict_proba(g[features])[:,1]
        for (_,r),prob in zip(g.iterrows(),pr):
            rows.append({"origin_date":r.origin_date.strftime("%Y-%m-%d"),"target_date":r.target_date.strftime("%Y-%m-%d"),
                         "actual":int(r[ycol]),"prob":float(prob),"pred":int(prob>=.5),"r_next":float(r.r_next)})
    return pd.DataFrame(rows)

def period_metrics(df):
    if df.empty:return {}
    out={}
    for name,ys in {"2022":["2022"],"2023":["2023"],"2024":["2024"],"PRE2025":["2022","2023","2024"],"2025":["2025"],"2026":["2026"]}.items():
        g=df[df.target_date.str[:4].isin(ys)]
        if not g.empty:out[name]=base.score(g.actual,g.prob,g.pred)
    return out

def eval_clock(p):
    out={"panel":{"n":len(p),"first":p.origin_date.min().strftime("%Y-%m-%d") if len(p) else None,
                  "last":p.origin_date.max().strftime("%Y-%m-%d") if len(p) else None,
                  "gap_gt4_after_pair_build":int((p.gap_days>4).sum()) if len(p) else None,
                  "tail_ready":int(np.isfinite(p.tail_cutoff).sum()) if len(p) else 0},"blocks":{}}
    for name,fs in blocks(p).items():
        up=walk_monthly(p,fs,"UP");dn=walk_monthly(p,fs,"MAT_DOWN")
        out["blocks"][name]={"features":fs,"UP":period_metrics(up),"MAT_DOWN":period_metrics(dn),
                             "prediction_counts":{"UP":len(up),"MAT_DOWN":len(dn)}}
    return out

def run(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
      with conn.cursor() as cur:
        cur.execute("SET default_transaction_read_only=on");before=base.authority(cur)
        raw={k:base.load_scalar(cur,v) for k,v in base.SERIES.items() if k!="GPR"}
        gpr=base.load_gpr(cur)
    dm={k:base.daily_map(v) for k,v in raw.items()}
    gold_proxy,pa=business_source(dm["Gold"],"STAKTRAKR_PROXY_BUSINESS_SOURCE")
    ny17,na=business_source(dm["NY17H"],"NY17_HOURLY_DERIVED_BUSINESS_SOURCE")
    metals={}
    ma={}
    for k in ("Silver","Platinum","Palladium"):
        metals[k],ma[k]=business_source(dm[k],k+"_BUSINESS_SOURCE")
    sp,sa=business_source(dm["SP500"],"SP500_BUSINESS_SOURCE")
    pp=build_panel(gold_proxy,metals,sp,gpr,"PROXY")
    npanel=build_panel(ny17,metals,sp,gpr,"NY17_RESEARCH")
    with psycopg.connect(dsn,autocommit=True) as conn:
      with conn.cursor() as cur:cur.execute("SET default_transaction_read_only=on");after=base.authority(cur)
    return {"identity":IDENTITY,"status":"RESEARCH_ONLY_NO_PROMOTION",
      "calendar_audit":{"PROXY":pa,"NY17_RESEARCH":na,"METALS":ma,"SP500":sa},
      "method":{"target_pair":"weekday source series next row, gap 1..4 days; target not recomputed after filtering",
                "feature_returns":"computed on full weekday business source before target-pair selection",
                "cross_source_timing":"strictly date < origin",
                "gpr_pit":"row-level available_as_of; PROXY cutoff prior UTC day; NY17 cutoff 17:00 America/New_York with DST",
                "comparison_support":"same equal-support panel/history for all ablations within clock",
                "refit":"monthly frozen coefficients","random_split":False,"2025_tuning":False,"2026_tuning":False,
                "hyperparameter_search":"NONE","model":"L2 logistic C=1"},
      "results":{"PROXY":eval_clock(pp),"NY17_RESEARCH":eval_clock(npanel)},
      "authority_invariants_before":before,"authority_invariants_after":after,"authority_invariants_unchanged":before==after,
      "governance":{"database_writes":"NONE","canonical_modified":False,"runtime_promotion":"NONE"}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",default="GOLD_CONTROL_DAILY_MIDAS_STRICT_PAIR_PILOT_V3_RESULT_2026-09-25.json");a=ap.parse_args()
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:raise SystemExit("NEON_DATABASE_URL required")
    o=run(dsn);Path(a.out).write_text(json.dumps(o,indent=2,default=str),encoding="utf-8")
    print(json.dumps(o,indent=2,default=str))
if __name__=="__main__":main()
