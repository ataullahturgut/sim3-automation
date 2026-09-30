from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd

import gold_monthly_chhho_etf_anomaly_screen_v1 as v1

CAL_START,CAL_END="2010-01","2020-12"
CORE_TARGETS=["2022-05","2022-07","2022-09","2024-03"]

def q(s,p): return float(pd.to_numeric(s,errors="coerce").dropna().quantile(p))

def streak(vals):
    out=[]; n=0
    for x in vals:
        if bool(x): n+=1
        else: n=0
        out.append(n)
    return out

def dynamic_features(m):
    z=m.copy()
    z["flow_delta1"]=z.combined_flow.diff()
    z["flow_sum3"]=z.combined_flow.rolling(3,min_periods=3).sum()
    z["flow_sum6"]=z.combined_flow.rolling(6,min_periods=6).sum()
    z["combined_outflow"]=z.combined_flow<0
    z["breadth2_outflow"]=(z.gld_tonnes_pct1<0)&(z.iau_shares_pct1<0)
    z["outflow_streak"]=streak(z.combined_outflow.fillna(False).tolist())
    z["breadth2_streak"]=streak(z.breadth2_outflow.fillna(False).tolist())
    z["gld_level_med12_prior"]=z.gld_tonnes_end.shift(1).rolling(12,min_periods=6).median()
    z["iau_level_med12_prior"]=z.iau_shares_end.shift(1).rolling(12,min_periods=6).median()
    z["gld_level_ratio12"]=z.gld_tonnes_end/z.gld_level_med12_prior
    z["iau_level_ratio12"]=z.iau_shares_end/z.iau_level_med12_prior
    return z

def calibrate(z):
    c=z.loc[CAL_START:CAL_END]
    return {
        "flow_delta1_q10":q(c.flow_delta1,.10),
        "flow_sum3_q10":q(c.flow_sum3,.10),
        "flow_sum6_q10":q(c.flow_sum6,.10),
        "outflow_streak_q90":q(c.outflow_streak,.90),
        "breadth2_streak_q90":q(c.breadth2_streak,.90),
        "gld_level_ratio12_q90":q(c.gld_level_ratio12,.90),
        "iau_level_ratio12_q90":q(c.iau_level_ratio12,.90),
    }

def flags(r,th):
    return {
      "ETF_FLOW_DETERIORATION_Q10":bool(r.flow_delta1<=th["flow_delta1_q10"]),
      "ETF_FLOW_SUM3_Q10":bool(r.flow_sum3<=th["flow_sum3_q10"]),
      "ETF_FLOW_SUM6_Q10":bool(r.flow_sum6<=th["flow_sum6_q10"]),
      "ETF_OUTFLOW_STREAK_Q90":bool(r.outflow_streak>=max(2,th["outflow_streak_q90"])),
      "ETF_BREADTH2_STREAK_Q90":bool(r.breadth2_streak>=max(2,th["breadth2_streak_q90"])),
      "ETF_GLD_LEVEL_HIGH_Q90":bool(r.gld_level_ratio12>=th["gld_level_ratio12_q90"]),
      "ETF_IAU_LEVEL_HIGH_Q90":bool(r.iau_level_ratio12>=th["iau_level_ratio12_q90"]),
    }

def score(rows,flag):
    ev=[r for r in rows if r[flag]]
    hi=[r for r in rows if r["ape_severity"]=="HIGH"]
    hits=[r for r in ev if r["ape_severity"]=="HIGH"]
    return {
      "events":len(ev),"hits":len(hits),"false_alarms":len(ev)-len(hits),
      "precision":None if not ev else len(hits)/len(ev),
      "recall":None if not hi else len(hits)/len(hi),
      "alarm_targets":[r["target"] for r in ev],
      "hit_targets":[r["target"] for r in hits],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--severity",required=True); ap.add_argument("--output",required=True)
    a=ap.parse_args()
    sev=json.loads(Path(a.severity).read_text())
    gld=v1.parse_gld(v1.fetch(v1.GLD_URL)); iau=v1.parse_iau(v1.fetch(v1.IAU_URL))
    m=dynamic_features(v1.monthly_features(gld,iau)); th=calibrate(m)

    rows=[]
    names=["flow_delta1","flow_sum3","flow_sum6","outflow_streak","breadth2_streak","gld_level_ratio12","iau_level_ratio12"]
    for sr in sev["rows"]:
        o=sr["origin"]
        if o not in m.index: continue
        r=m.loc[o]
        z={"target":sr["target"],"origin":o,"ape_pct":float(sr["ape_pct"]),"ape_severity":sr["ape_severity"]}
        for n in names:
            v=r[n]; z[n]=None if pd.isna(v) else float(v)
        z.update(flags(r,th)); rows.append(z)

    fnames=["ETF_FLOW_DETERIORATION_Q10","ETF_FLOW_SUM3_Q10","ETF_FLOW_SUM6_Q10",
            "ETF_OUTFLOW_STREAK_Q90","ETF_BREADTH2_STREAK_Q90","ETF_GLD_LEVEL_HIGH_Q90","ETF_IAU_LEVEL_HIGH_Q90"]
    scores={f:score(rows,f) for f in fnames}
    core=[r for r in rows if r["target"] in CORE_TARGETS]
    out={
      "schema":"GOLD_MONTHLY_CHHHO_ETF_DYNAMIC_REGIME_V2_2026-09-30",
      "status":"COMPLETE","calibration_period":f"{CAL_START}..{CAL_END}",
      "thresholds":th,"core_rows":core,"rows":rows,"scores":scores,
      "governance":{"target_month_etf_data_used":False,"threshold_retuning":False,"routing_tested":False}
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"thresholds":th,"core_rows":core,"scores":scores},sort_keys=True))
if __name__=="__main__": main()
