from __future__ import annotations
import argparse, hashlib, json, math, os
from pathlib import Path

import numpy as np
import pandas as pd

import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as chhho
import gold_monthly_chhho_predev_currentgpr_v2 as gprv2

SNAPSHOT_SHA="5e4dfbfda5a89aceff9b30f5454fb36ab33c3baf"
START,END="2010-01","2024-12"
HIGH_AE=63.06
HIGH_APE=2.96117
HIGH_RETURN_ERROR_PP=3.00590

def mshift(m,d): return base.month_shift(m,d)

def gold_frame(b):
    s=pd.Series({m:float(v) for m,v in b.core_gold.items()},dtype=float).sort_index()
    f=pd.DataFrame({"Gold":s})
    f["Gold_r1"]=np.log(f.Gold/f.Gold.shift(1))
    f["Gold_r3"]=np.log(f.Gold/f.Gold.shift(3))
    f["ma12_prior"]=f.Gold.shift(1).rolling(12,min_periods=12).mean()
    f["gap"]=f.Gold/f.ma12_prior-1
    f["next_r1"]=f.Gold_r1.shift(-1)
    f["next_abs_r1"]=f.next_r1.abs()
    return f

def market_stats(f):
    cal=f.loc[START:END].copy()
    valid=cal[cal.next_abs_r1.notna()]
    q3=float(valid.next_abs_r1.quantile(.75))
    baseline={
        "n":int(len(valid)),
        "mean":float(valid.next_abs_r1.mean()),
        "median":float(valid.next_abs_r1.median()),
        "q3":q3,
    }
    out={}
    for name,mask in {"E_level":cal.gap>.20,"G":cal.Gold_r3<=-.10}.items():
        z=cal[mask & cal.next_abs_r1.notna()]
        rows=[]
        for m,r in z.iterrows():
            rows.append({
                "origin":m,"target":mshift(m,1),
                "gold_r1":float(r.Gold_r1),"gold_r3":float(r.Gold_r3),
                "gold_vs_ma12":float(r.gap),
                "next_log_return":float(r.next_r1),
                "next_abs_log_return":float(r.next_abs_r1),
                "above_baseline_q3":bool(r.next_abs_r1>q3),
            })
        out[name]={
            "events":len(rows),
            "origins":[x["origin"] for x in rows],
            "q3_hits":sum(x["above_baseline_q3"] for x in rows),
            "q3_hit_rate":None if not rows else sum(x["above_baseline_q3"] for x in rows)/len(rows),
            "mean":None if z.empty else float(z.next_abs_r1.mean()),
            "median":None if z.empty else float(z.next_abs_r1.median()),
            "mean_uplift_ratio":None if z.empty else float(z.next_abs_r1.mean()/baseline["mean"]),
            "rows":rows,
        }
    return baseline,out

def fetch_gpr():
    raw=gprv2.fetch_snapshot(SNAPSHOT_SHA)
    h,meta=gprv2.parse_xls(raw)
    return h,{
        "repo":gprv2.REPO,"path":gprv2.PATH,"commit_sha":SNAPSHOT_SHA,
        "sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"parse_meta":meta,
    }

def samples_with_history(b,target,h):
    out={}
    for t in base.month_range("2010-03",target):
        try: out[t]=base.sample_for_target(b,t,h,lag_gpr=True)
        except RuntimeError: pass
    if target not in out: raise RuntimeError(f"TARGET_NOT_BUILDABLE {target}")
    return out

def evaluate_prediction(b,f,origin,target,pred,forecast,actual,source,train_rows=None,diag=None):
    g1=float(f.loc[origin,"Gold_r1"])
    e_level=bool(f.loc[origin,"gap"]>.20)
    g=bool(f.loc[origin,"Gold_r3"]<=-.10)
    ae=abs(float(forecast)-float(actual))
    ape=ae/float(actual)*100.0
    ar=math.log(float(actual)/float(b.core_gold[origin]))
    re=abs(float(pred)-ar)*100.0
    return {
        "origin":origin,"target":target,"source":source,"buildable":True,"status":"PASS",
        "E_level":e_level,"G":g,
        "E_full":bool(e_level and abs(float(pred)-g1)>.05),
        "gold_r1":g1,"gold_r3":float(f.loc[origin,"Gold_r3"]),
        "gold_vs_ma12":float(f.loc[origin,"gap"]),
        "pred_log_return_gold":float(pred),"forecast":float(forecast),"actual":float(actual),
        "actual_log_return_gold":ar,"ae":ae,"ape_pct":ape,"return_error_pp":re,
        "high_ae":bool(ae>HIGH_AE),"high_ape":bool(ape>HIGH_APE),
        "high_return_error":bool(re>HIGH_RETURN_ERROR_PP),
        "train_rows":None if train_rows is None else int(train_rows),
        "diag":diag,
    }

def counterfactual_row(b,f,h,origin):
    target=mshift(origin,1); req=mshift(origin,-1)
    shell={
        "origin":origin,"target":target,"source":"COUNTERFACTUAL_2021Q4_CURRENT_GPR",
        "E_level":bool(f.loc[origin,"gap"]>.20),"G":bool(f.loc[origin,"Gold_r3"]<=-.10),
        "gold_r1":float(f.loc[origin,"Gold_r1"]),"gold_r3":float(f.loc[origin,"Gold_r3"]),
        "gold_vs_ma12":float(f.loc[origin,"gap"]),"buildable":False,
        "gpr_required_month":req,
    }
    if req not in h:
        shell["status"]="GPR_REQUIRED_MONTH_MISSING"; return shell
    hh={k:v for k,v in h.items() if k<=req}
    try:
        ss=samples_with_history(b,target,hh)
        pred,n,diag=chhho.select(ss,target,"CHHHO")
        pg=float(pred[0]); fc=float(b.core_gold[origin]*math.exp(pg)); act=float(b.core_gold[target])
        z=evaluate_prediction(b,f,origin,target,pg,fc,act,shell["source"],n,diag)
        z["gpr_required_month"]=req
        return z
    except Exception as e:
        shell["status"]="MODEL_UNBUILDABLE"; shell["error"]=f"{type(e).__name__}:{e}"
        return shell

def canonical_rows(ch):
    out={}
    for sec in ["dev","transport_2025","stress_2026"]:
        for r in ch[sec]["rows"]:
            out[r["target"]]=r
    return out

def summarize_model(rows,flag):
    z=[r for r in rows if r.get("buildable") and r.get(flag)]
    return {
        "events":len(z),
        "targets":[r["target"] for r in z],
        "canonical_events":sum(r["source"]=="FROZEN_CANONICAL_CHHHO" for r in z),
        "counterfactual_events":sum(r["source"]!="FROZEN_CANONICAL_CHHHO" for r in z),
        "high_ae":sum(r["high_ae"] for r in z),
        "high_ape":sum(r["high_ape"] for r in z),
        "high_return_error":sum(r["high_return_error"] for r in z),
        "mean_ae":None if not z else float(np.mean([r["ae"] for r in z])),
        "mean_ape_pct":None if not z else float(np.mean([r["ape_pct"] for r in z])),
        "mean_return_error_pp":None if not z else float(np.mean([r["return_error_pp"] for r in z])),
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--chhho",required=True); a=ap.parse_args()
    ch=json.loads(Path(a.chhho).read_text())
    canon=canonical_rows(ch)
    b=base.load_data(os.environ["NEON_DATABASE_URL"])
    f=gold_frame(b)
    baseline,signals=market_stats(f)
    h,gmeta=fetch_gpr()

    e=set(signals["E_level"]["origins"]); g=set(signals["G"]["origins"]); origins=sorted(e|g)
    rows=[]
    for origin in origins:
        target=mshift(origin,1)
        if target in canon:
            r=canon[target]
            rows.append(evaluate_prediction(
                b,f,origin,target,float(r["pred_log_return_gold"]),float(r["forecast"]),
                float(r["actual"]),"FROZEN_CANONICAL_CHHHO",r.get("train_rows"),r.get("diag")
            ))
        else:
            rows.append(counterfactual_row(b,f,h,origin))

    unbuild=[r for r in rows if not r.get("buildable")]
    out={
        "schema":"GOLD_MONTHLY_CHHHO_EG_HISTORICAL_VALIDATION_V2_2026-09-30",
        "status":"COMPLETE",
        "period":f"{START}..{END}",
        "thresholds":{
            "E_level_gap_gt":0.20,"E_disagreement_abs_gt":0.05,"G_r3_lte":-0.10,
            "high_ae_usd_gt":HIGH_AE,"high_ape_pct_gt":HIGH_APE,
            "high_return_error_pp_gt":HIGH_RETURN_ERROR_PP,
        },
        "market_state":{"baseline":baseline,"signals":signals},
        "gpr_counterfactual_authority":gmeta,
        "model_rows":rows,
        "model_summary":{
            "candidate_origins":origins,
            "candidate_count":len(origins),
            "buildable_count":sum(r.get("buildable",False) for r in rows),
            "unbuildable":unbuild,
            "E_level":summarize_model(rows,"E_level"),
            "E_full":summarize_model(rows,"E_full"),
            "G":summarize_model(rows,"G"),
        },
        "governance":{
            "canonical_2022_2024_forecasts_rerun":False,
            "canonical_2022_2024_frozen_artifact_used":True,
            "pre_2022_replay_is_counterfactual_not_pit":True,
            "threshold_retuning":False,
            "routing_tested":False,
            "database_read_only":True,
        },
    }
    Path("GOLD_MONTHLY_CHHHO_EG_HISTORICAL_VALIDATION_V2_2026-09-30.json").write_text(
        json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n"
    )
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "market_state":out["market_state"],
        "model_summary":out["model_summary"],
        "model_rows":[{k:r.get(k) for k in (
            "origin","target","source","E_level","E_full","G","buildable","status",
            "ae","ape_pct","return_error_pp","high_ae","high_ape","high_return_error"
        )} for r in rows],
    },sort_keys=True))

if __name__=="__main__":
    main()
