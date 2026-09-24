from __future__ import annotations
import argparse, json, os
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg
import daily_midas_clean_pilot_v2 as base
import daily_midas_strict_pair_pilot_v3 as strict

IDENTITY="GOLD_CONTROL_DAILY_MIDAS_STRICT_PAIR_VARIANTS_V3_RESEARCH"

def make_model(kind):
    if kind in ("L2","L1"): return base.model_logit(kind)
    if kind=="HGB": return base.model_hgb()
    raise ValueError(kind)

def walk_monthly(p,features,target,kind):
    rows=[]
    q=p[(p.origin_date>=strict.START_SCORE)&(p.origin_date<strict.END_SCORE)].copy()
    if q.empty:return pd.DataFrame()
    q["ym"]=q.origin_date.dt.strftime("%Y-%m")
    ycol="y_up" if target=="UP" else "y_mat_down"
    for ym,g in q.groupby("ym",sort=True):
        first=g.origin_date.min()
        h=p[(p.target_date<first)&(p.origin_date<first)].copy()
        if target=="MAT_DOWN":h=h[np.isfinite(h.tail_cutoff)].copy()
        if len(h)<strict.MIN_TRAIN:continue
        y=h[ycol].to_numpy(int)
        if len(np.unique(y))<2:continue
        m=make_model(kind);m.fit(h[features],y)
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
                  "tail_ready":int(np.isfinite(p.tail_cutoff).sum()) if len(p) else 0},"blocks":{}}
    for name,fs in strict.blocks(p).items():
        out["blocks"][name]={"features":fs,"models":{}}
        for kind in ("L2","L1","HGB"):
            up=walk_monthly(p,fs,"UP",kind);dn=walk_monthly(p,fs,"MAT_DOWN",kind)
            out["blocks"][name]["models"][kind]={"UP":period_metrics(up),"MAT_DOWN":period_metrics(dn),
                                                  "prediction_counts":{"UP":len(up),"MAT_DOWN":len(dn)}}
    return out

def run(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
      with conn.cursor() as cur:
        cur.execute("SET default_transaction_read_only=on");before=base.authority(cur)
        raw={k:base.load_scalar(cur,v) for k,v in base.SERIES.items() if k!="GPR"}
        gpr=base.load_gpr(cur)
    dm={k:base.daily_map(v) for k,v in raw.items()}
    gold_proxy,pa=strict.business_source(dm["Gold"],"STAKTRAKR_PROXY_BUSINESS_SOURCE")
    ny17,na=strict.business_source(dm["NY17H"],"NY17_HOURLY_DERIVED_BUSINESS_SOURCE")
    metals={};ma={}
    for k in ("Silver","Platinum","Palladium"):
        metals[k],ma[k]=strict.business_source(dm[k],k+"_BUSINESS_SOURCE")
    sp,sa=strict.business_source(dm["SP500"],"SP500_BUSINESS_SOURCE")
    pp=strict.build_panel(gold_proxy,metals,sp,gpr,"PROXY")
    npanel=strict.build_panel(ny17,metals,sp,gpr,"NY17_RESEARCH")
    with psycopg.connect(dsn,autocommit=True) as conn:
      with conn.cursor() as cur:cur.execute("SET default_transaction_read_only=on");after=base.authority(cur)
    return {"identity":IDENTITY,"status":"RESEARCH_ONLY_NO_PROMOTION",
      "calendar_audit":{"PROXY":pa,"NY17_RESEARCH":na,"METALS":ma,"SP500":sa},
      "method":{"inherits_strict_pair_v3":True,"refit":"monthly frozen coefficients",
                "model_families":["L2 fixed C=1","L1 fixed C=.25","small fixed HGB"],
                "hyperparameter_search":"NONE","random_split":False,"2025_tuning":False,"2026_tuning":False},
      "results":{"PROXY":eval_clock(pp),"NY17_RESEARCH":eval_clock(npanel)},
      "authority_invariants_unchanged":before==after,
      "governance":{"database_writes":"NONE","canonical_modified":False,"runtime_promotion":"NONE"}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",default="GOLD_CONTROL_DAILY_MIDAS_STRICT_PAIR_VARIANTS_V3_RESULT_2026-09-25.json");a=ap.parse_args()
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:raise SystemExit("NEON_DATABASE_URL required")
    o=run(dsn);Path(a.out).write_text(json.dumps(o,indent=2,default=str),encoding="utf-8")
    print(json.dumps(o,indent=2,default=str))
if __name__=="__main__":main()
