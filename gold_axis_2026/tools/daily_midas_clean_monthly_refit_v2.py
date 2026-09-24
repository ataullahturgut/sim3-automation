from __future__ import annotations
import argparse, json, os
from pathlib import Path
import numpy as np
import pandas as pd
import daily_midas_clean_pilot_v2 as base

def walk_monthly(p,features,model_kind,target):
    rows=[]
    q=p[(p.origin_date>=base.START_SCORE)&(p.origin_date<base.END_SCORE)].copy()
    if q.empty:
        return pd.DataFrame()
    q["ym"]=q.origin_date.dt.strftime("%Y-%m")
    ycol="y_up" if target=="up" else "y_mat_down"
    for ym,g in q.groupby("ym",sort=True):
        first_origin=g.origin_date.min()
        hist=p[(p.target_date<first_origin)&(p.origin_date<first_origin)].copy()
        if target=="mat_down":
            hist=hist[np.isfinite(hist.tail_cutoff)].copy()
        if len(hist)<base.MIN_TRAIN:
            continue
        y=hist[ycol].to_numpy(int)
        if len(np.unique(y))<2:
            continue
        m=base.model_logit("L2")
        m.fit(hist[features],y)
        probs=m.predict_proba(g[features])[:,1]
        for (_,r),prob in zip(g.iterrows(),probs):
            rows.append({
              "origin_date":r.origin_date.strftime("%Y-%m-%d"),
              "target_date":r.target_date.strftime("%Y-%m-%d"),
              "actual":int(r[ycol]),"prob":float(prob),"pred":int(prob>=.5),
              "r_next":float(r.r_next),
              "tail_cutoff":None if not np.isfinite(r.tail_cutoff) else float(r.tail_cutoff)
            })
    return pd.DataFrame(rows)

def fit_block_monthly(p,features,name):
    up=walk_monthly(p,features,"L2","up")
    dn=walk_monthly(p,features,"L2","mat_down")
    return {"features":features,"models":{"L2_MONTHLY_REFIT":{
      "UP":base.periods(up),"MAT_DOWN":base.periods(dn),
      "prediction_counts":{"UP":len(up),"MAT_DOWN":len(dn)}
    }}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="GOLD_CONTROL_DAILY_MIDAS_CLEAN_MONTHLY_REFIT_V2_RESULT_2026-09-25.json")
    a=ap.parse_args()
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    old=base.fit_block
    base.fit_block=fit_block_monthly
    try:
        o=base.run(dsn)
    finally:
        base.fit_block=old
    o["identity"]="GOLD_CONTROL_DAILY_MIDAS_CLEAN_MONTHLY_REFIT_V2_RESEARCH"
    o["method"]["model_families"]=["L2 logistic; coefficients frozen within each calendar month"]
    o["method"]["refit_frequency"]="MONTHLY_AT_FIRST_SCORABLE_ORIGIN_USING_ONLY_TARGETS_MATURED_BEFORE_MONTH_FIRST_ORIGIN"
    Path(a.out).write_text(json.dumps(o,indent=2,default=str),encoding="utf-8")
    print(json.dumps({
      "identity":o["identity"],"status":o["status"],
      "calendar_audit":o["calendar_audit"],"results":o["results"],
      "invariants":o["authority_invariants_unchanged"]
    },indent=2,default=str))

if __name__=="__main__": main()
