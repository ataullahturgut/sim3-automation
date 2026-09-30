from __future__ import annotations
import argparse, io, json, math
from pathlib import Path

import numpy as np
import pandas as pd

import gold_monthly_chhho_etf_anomaly_screen_v1 as v1
import gold_monthly_chhho_etf_dynamic_regime_v2 as v2

CAL_START,CAL_END="2010-01","2020-12"
LATER1_START,LATER1_END="2021-01","2024-12"
LATER2_START,LATER2_END="2025-01","2026-08"
SEED=20260930

FROZEN_FLOW_DELTA_Q10=-0.04281621590920031
FROZEN_BREADTH_STREAK=2

def parse_gld_full(raw: bytes) -> pd.DataFrame:
    df=pd.read_excel(io.BytesIO(raw),sheet_name="US GLD Historical Archive",engine="openpyxl")
    df=df.rename(columns={
        "Date":"date",
        "Closing Price":"close",
        "Tonnes of Gold":"tonnes",
        "Daily Share Volume":"volume",
    })
    df["date"]=pd.to_datetime(df["date"],format="%d-%b-%Y",errors="coerce")
    for c in ["close","tonnes","volume"]:
        df[c]=pd.to_numeric(df[c],errors="coerce")
    df=df.dropna(subset=["date","close","tonnes"]).sort_values("date").drop_duplicates("date",keep="last")
    return df[["date","close","tonnes","volume"]]

def fisher_greater(a,b,c,d):
    # 2x2: [[event_move,event_no],[non_move,non_no]], one-sided enrichment.
    n1=a+b; n2=c+d; k=a+c; n=n1+n2
    lo=max(0,n1-(n-k)); hi=min(n1,k)
    den=math.comb(n,n1)
    p=0.0
    for x in range(a,hi+1):
        p += math.comb(k,x)*math.comb(n-k,n1-x)/den
    return min(1.0,float(p))

def monthly_panel(gld,iau):
    # ETF features from frozen V2 construction.
    gbasic=gld[["date","tonnes","volume"]].copy()
    base=v1.monthly_features(gbasic,iau)
    z=v2.dynamic_features(base)

    gc=gld.copy()
    gc["month"]=gc.date.dt.strftime("%Y-%m")
    gme=gc.groupby("month").tail(1).set_index("month")
    z["gld_close_end"]=gme.close.reindex(z.index)
    z["gld_logret"]=np.log(z.gld_close_end/z.gld_close_end.shift(1))
    z["gld_simple_ret"]=z.gld_close_end/z.gld_close_end.shift(1)-1.0
    z["next_gld_logret"]=z.gld_logret.shift(-1)
    z["next_gld_simple_ret"]=z.gld_simple_ret.shift(-1)
    z["next_abs_logret_pp"]=z.next_gld_logret.abs()*100.0
    z["next_abs_simple_pct"]=z.next_gld_simple_ret.abs()*100.0
    z["move3"]=z.next_abs_logret_pp>=3.0
    z["move5"]=z.next_abs_logret_pp>=5.0
    z["move8"]=z.next_abs_logret_pp>=8.0
    z["next_up"]=z.next_gld_logret>0
    z["next_down"]=z.next_gld_logret<0
    z["sign_reversal"]=(np.sign(z.gld_logret)*np.sign(z.next_gld_logret))<0
    z["I1"]=z.flow_delta1<=FROZEN_FLOW_DELTA_Q10
    z["I2"]=z.breadth2_streak>=FROZEN_BREADTH_STREAK
    return z

def period_rows(z,start,end):
    x=z.loc[start:end].copy()
    x=x[pd.notna(x.next_gld_logret)]
    return x

def bootstrap_uplift(event_vals,non_vals,nboot=20000):
    ev=np.asarray(event_vals,dtype=float); nv=np.asarray(non_vals,dtype=float)
    if len(ev)==0 or len(nv)==0:
        return {"mean_diff_pp":None,"ci95":[None,None],"mean_ratio":None}
    rng=np.random.default_rng(SEED)
    diffs=np.empty(nboot)
    ratios=np.empty(nboot)
    for i in range(nboot):
        es=rng.choice(ev,size=len(ev),replace=True)
        ns=rng.choice(nv,size=len(nv),replace=True)
        em=float(es.mean()); nm=float(ns.mean())
        diffs[i]=em-nm
        ratios[i]=em/nm if nm!=0 else np.nan
    return {
        "mean_diff_pp":float(ev.mean()-nv.mean()),
        "ci95":[float(np.nanquantile(diffs,.025)),float(np.nanquantile(diffs,.975))],
        "mean_ratio":float(ev.mean()/nv.mean()) if nv.mean()!=0 else None,
        "ratio_ci95":[float(np.nanquantile(ratios,.025)),float(np.nanquantile(ratios,.975))],
    }

def summarize(z,flag):
    ev=z[z[flag]]
    ne=z[~z[flag]]
    allx=z
    def rate(df,col):
        return None if len(df)==0 else float(df[col].mean())
    out={
        "flag":flag,
        "n_origins":int(len(z)),
        "events":int(len(ev)),
        "event_origins":ev.index.tolist(),
        "non_events":int(len(ne)),
        "event_mean_abs_next_logret_pp":None if len(ev)==0 else float(ev.next_abs_logret_pp.mean()),
        "event_median_abs_next_logret_pp":None if len(ev)==0 else float(ev.next_abs_logret_pp.median()),
        "baseline_all_mean_abs_next_logret_pp":float(allx.next_abs_logret_pp.mean()),
        "baseline_non_event_mean_abs_next_logret_pp":None if len(ne)==0 else float(ne.next_abs_logret_pp.mean()),
        "baseline_all_median_abs_next_logret_pp":float(allx.next_abs_logret_pp.median()),
        "move3_event_rate":rate(ev,"move3"),
        "move3_all_rate":rate(allx,"move3"),
        "move3_non_event_rate":rate(ne,"move3"),
        "move5_event_rate":rate(ev,"move5"),
        "move5_all_rate":rate(allx,"move5"),
        "move5_non_event_rate":rate(ne,"move5"),
        "move8_event_rate":rate(ev,"move8"),
        "move8_all_rate":rate(allx,"move8"),
        "move8_non_event_rate":rate(ne,"move8"),
        "up_rate":rate(ev,"next_up"),
        "down_rate":rate(ev,"next_down"),
        "sign_reversal_rate":rate(ev,"sign_reversal"),
        "baseline_sign_reversal_rate":rate(allx,"sign_reversal"),
    }
    if len(ev)>0 and len(ne)>0:
        for k in [3,5,8]:
            er=out[f"move{k}_event_rate"]; nr=out[f"move{k}_non_event_rate"]
            out[f"move{k}_relative_risk_vs_non_event"]=None if nr in (None,0) else float(er/nr)
            a=int(ev[f"move{k}"].sum()); b=len(ev)-a
            c=int(ne[f"move{k}"].sum()); d=len(ne)-c
            out[f"move{k}_fisher_greater_p"]=fisher_greater(a,b,c,d)
        out["bootstrap_abs_return_uplift"]=bootstrap_uplift(ev.next_abs_logret_pp.values,ne.next_abs_logret_pp.values)
    else:
        out["bootstrap_abs_return_uplift"]=bootstrap_uplift([],[])
    out["event_detail"]=[
        {
            "origin":idx,
            "origin_gld_logret_pp":float(r.gld_logret*100.0),
            "next_gld_logret_pp":float(r.next_gld_logret*100.0),
            "next_abs_logret_pp":float(r.next_abs_logret_pp),
            "move3":bool(r.move3),"move5":bool(r.move5),"move8":bool(r.move8),
            "flow_delta1_pp":float(r.flow_delta1*100.0),
            "combined_flow_pct":float(r.combined_flow*100.0),
            "flow_sum3_pct":None if pd.isna(r.flow_sum3) else float(r.flow_sum3*100.0),
            "flow_sum6_pct":None if pd.isna(r.flow_sum6) else float(r.flow_sum6*100.0),
            "breadth2_streak":int(r.breadth2_streak),
            "outflow_streak":int(r.outflow_streak),
        } for idx,r in ev.iterrows()
    ]
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    gld_raw=v1.fetch(v1.GLD_URL)
    iau_raw=v1.fetch(v1.IAU_URL)
    gld=parse_gld_full(gld_raw)
    iau=v1.parse_iau(iau_raw)
    z=monthly_panel(gld,iau)

    # Guard frozen thresholds against current-source drift.
    th=v2.calibrate(v2.dynamic_features(v1.monthly_features(gld[["date","tonnes","volume"]],iau)))
    if abs(th["flow_delta1_q10"]-FROZEN_FLOW_DELTA_Q10)>1e-12:
        raise RuntimeError(("I1_THRESHOLD_DRIFT",th["flow_delta1_q10"],FROZEN_FLOW_DELTA_Q10))
    if max(2,th["breadth2_streak_q90"])!=FROZEN_BREADTH_STREAK:
        raise RuntimeError(("I2_THRESHOLD_DRIFT",th["breadth2_streak_q90"],FROZEN_BREADTH_STREAK))

    periods={
        "HISTORICAL_2010_2020":(CAL_START,CAL_END),
        "LATER_2021_2024":(LATER1_START,LATER1_END),
        "LATER_2025_2026_AUG":(LATER2_START,LATER2_END),
    }
    stats={}
    for p,(s,e) in periods.items():
        pp=period_rows(z,s,e)
        stats[p]={f:summarize(pp,f) for f in ["I1","I2"]}

    # Detailed core origins from the later alarm study.
    core_origins=["2022-04","2022-06","2022-08","2024-02"]
    core=[]
    for o in core_origins:
        r=z.loc[o]
        core.append({
            "origin":o,"I1":bool(r.I1),"I2":bool(r.I2),
            "origin_gld_logret_pp":float(r.gld_logret*100.0),
            "next_gld_logret_pp":float(r.next_gld_logret*100.0),
            "next_abs_logret_pp":float(r.next_abs_logret_pp),
            "move3":bool(r.move3),"move5":bool(r.move5),"move8":bool(r.move8),
            "flow_delta1_pp":float(r.flow_delta1*100.0),
            "combined_flow_pct":float(r.combined_flow*100.0),
            "flow_sum3_pct":float(r.flow_sum3*100.0),
            "flow_sum6_pct":float(r.flow_sum6*100.0),
            "breadth2_streak":int(r.breadth2_streak),
            "outflow_streak":int(r.outflow_streak),
        })

    out={
        "schema":"GOLD_MONTHLY_ETF_I1_I2_HISTORICAL_RECURRENCE_V1_2026-09-30",
        "status":"COMPLETE",
        "frozen_mechanisms":{
            "I1":{"flow_delta1_q10":FROZEN_FLOW_DELTA_Q10},
            "I2":{"breadth2_streak_months":FROZEN_BREADTH_STREAK},
        },
        "outcomes":{
            "MOVE_3":"abs(next month GLD log return) >= 3pp",
            "MOVE_5":"abs(next month GLD log return) >= 5pp",
            "MOVE_8":"abs(next month GLD log return) >= 8pp",
        },
        "stats":stats,
        "core_origins":core,
        "sources":{
            "GLD":{"url":v1.GLD_URL,"first":str(gld.date.min().date()),"last":str(gld.date.max().date()),"rows":len(gld)},
            "IAU":{"url":v1.IAU_URL,"first":str(iau.date.min().date()),"last":str(iau.date.max().date()),"rows":len(iau)},
        },
        "governance":{
            "model_free":True,
            "target_month_etf_used_in_signal":False,
            "mechanism_thresholds_retuned":False,
            "outcome_thresholds_fixed_pre_result":True,
            "routing_tested":False,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "historical":stats["HISTORICAL_2010_2020"],
        "later_2021_2024":stats["LATER_2021_2024"],
        "core":core,
    },sort_keys=True))

if __name__=="__main__": main()
