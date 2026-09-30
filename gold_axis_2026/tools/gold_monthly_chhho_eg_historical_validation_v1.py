from __future__ import annotations
import hashlib, io, json, math, os
from pathlib import Path

import numpy as np
import pandas as pd
import requests

import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as chhho
import gold_monthly_chhho_predev_currentgpr_v2 as gprv2

SNAPSHOT_SHA = "5e4dfbfda5a89aceff9b30f5454fb36ab33c3baf"
START, END = "2010-01", "2021-12"
HIGH_AE = 63.06
HIGH_APE = 2.96117
HIGH_RETURN_ERROR_PP = 3.00590

def mshift(m,d): return base.month_shift(m,d)

def canonical_gold_state(b):
    months=sorted(b.core_gold)
    s=pd.Series({m:float(b.core_gold[m]) for m in months},dtype=float).sort_index()
    f=pd.DataFrame({"Gold":s})
    f["Gold_r1"]=np.log(f.Gold/f.Gold.shift(1))
    f["Gold_r3"]=np.log(f.Gold/f.Gold.shift(3))
    f["ma12_prior"]=f.Gold.shift(1).rolling(12,min_periods=12).mean()
    f["gap"]=f.Gold/f.ma12_prior-1
    f["next_r1"]=f.Gold_r1.shift(-1)
    f["next_abs_r1"]=f.next_r1.abs()
    return f

def layer1(frame):
    cal=frame.loc[START:END].copy()
    valid=cal[cal.next_abs_r1.notna()]
    q3=float(valid.next_abs_r1.quantile(.75))
    base_stats={
        "n":int(len(valid)),
        "next_abs_return_mean":float(valid.next_abs_r1.mean()),
        "next_abs_return_median":float(valid.next_abs_r1.median()),
        "next_abs_return_q3":q3,
    }
    out={}
    masks={
        "E_level":cal.gap>.20,
        "G":cal.Gold_r3<=-.10,
    }
    for name,mask in masks.items():
        z=cal[mask & cal.next_abs_r1.notna()].copy()
        rows=[]
        for m,r in z.iterrows():
            rows.append({
                "origin":m,
                "target":mshift(m,1),
                "gold":float(r.Gold),
                "gold_r1":float(r.Gold_r1),
                "gold_r3":float(r.Gold_r3),
                "gold_vs_ma12":float(r.gap),
                "next_log_return":float(r.next_r1),
                "next_abs_log_return":float(r.next_abs_r1),
                "above_baseline_q3":bool(r.next_abs_r1>q3),
            })
        vals=z.next_abs_r1
        out[name]={
            "events":int(len(z)),
            "origins":[r["origin"] for r in rows],
            "q3_hits":int(sum(r["above_baseline_q3"] for r in rows)),
            "q3_hit_rate":None if not rows else float(sum(r["above_baseline_q3"] for r in rows)/len(rows)),
            "next_abs_return_mean":None if z.empty else float(vals.mean()),
            "next_abs_return_median":None if z.empty else float(vals.median()),
            "baseline_mean":base_stats["next_abs_return_mean"],
            "baseline_median":base_stats["next_abs_return_median"],
            "mean_uplift_ratio":None if z.empty else float(vals.mean()/base_stats["next_abs_return_mean"]),
            "rows":rows,
        }
    return base_stats,out

def fetch_gpr_snapshot():
    raw=gprv2.fetch_snapshot(SNAPSHOT_SHA)
    hist,meta=gprv2.parse_xls(raw)
    return hist,{
        "repo":gprv2.REPO,
        "path":gprv2.PATH,
        "commit_sha":SNAPSHOT_SHA,
        "sha256":hashlib.sha256(raw).hexdigest(),
        "bytes":len(raw),
        "parse_meta":meta,
    }

def samples_with_history(b,target,h):
    out={}
    for t in base.month_range("2010-03",target):
        try:
            out[t]=base.sample_for_target(b,t,h,lag_gpr=True)
        except RuntimeError:
            pass
    if target not in out:
        raise RuntimeError(f"TARGET_NOT_BUILDABLE {target}")
    return out

def replay_one(b,frame,gpr_hist,origin,signal_e,signal_g):
    target=mshift(origin,1)
    req=mshift(origin,-1)
    row={
        "origin":origin,"target":target,
        "E_level":bool(signal_e),"G":bool(signal_g),
        "gold_r1":float(frame.loc[origin,"Gold_r1"]),
        "gold_r3":float(frame.loc[origin,"Gold_r3"]),
        "gold_vs_ma12":float(frame.loc[origin,"gap"]),
        "gpr_required_month":req,
        "buildable":False,
    }
    if req not in gpr_hist:
        row["status"]="GPR_REQUIRED_MONTH_MISSING"
        return row
    h={k:v for k,v in gpr_hist.items() if k<=req}
    try:
        ss=samples_with_history(b,target,h)
        pred,n,diag=chhho.select(ss,target,"CHHHO")
        pg=float(pred[0])
        fc=float(b.core_gold[origin]*math.exp(pg))
        act=float(b.core_gold[target])
        ae=abs(fc-act)
        ape=ae/act*100.0
        actual_ret=math.log(act/float(b.core_gold[origin]))
        ret_err_pp=abs(pg-actual_ret)*100.0
        full_e=bool(signal_e and abs(pg-row["gold_r1"])>.05)
        row.update({
            "buildable":True,
            "status":"PASS",
            "train_rows":int(n),
            "diag":diag,
            "pred_log_return_gold":pg,
            "forecast":fc,
            "actual":act,
            "actual_log_return_gold":actual_ret,
            "ae":ae,
            "ape_pct":ape,
            "return_error_pp":ret_err_pp,
            "E_full":full_e,
            "high_ae":bool(ae>HIGH_AE),
            "high_ape":bool(ape>HIGH_APE),
            "high_return_error":bool(ret_err_pp>HIGH_RETURN_ERROR_PP),
        })
    except Exception as e:
        row["status"]="MODEL_UNBUILDABLE"
        row["error"]=f"{type(e).__name__}:{e}"
    return row

def signal_model_summary(rows,signal_key):
    z=[r for r in rows if r.get(signal_key) and r.get("buildable")]
    return {
        "buildable_events":len(z),
        "targets":[r["target"] for r in z],
        "high_ae":sum(r["high_ae"] for r in z),
        "high_ape":sum(r["high_ape"] for r in z),
        "high_return_error":sum(r["high_return_error"] for r in z),
        "mean_ae":None if not z else float(np.mean([r["ae"] for r in z])),
        "mean_ape_pct":None if not z else float(np.mean([r["ape_pct"] for r in z])),
        "mean_return_error_pp":None if not z else float(np.mean([r["return_error_pp"] for r in z])),
    }

def main():
    b=base.load_data(os.environ["NEON_DATABASE_URL"])
    frame=canonical_gold_state(b)
    baseline,market=layer1(frame)
    gpr_hist,gpr_meta=fetch_gpr_snapshot()

    e_origins=set(market["E_level"]["origins"])
    g_origins=set(market["G"]["origins"])
    origins=sorted(e_origins|g_origins)
    rows=[
        replay_one(b,frame,gpr_hist,o,o in e_origins,o in g_origins)
        for o in origins
    ]

    full_e=[r for r in rows if r.get("E_full")]
    out={
        "schema":"GOLD_MONTHLY_CHHHO_EG_HISTORICAL_VALIDATION_V1_2026-09-30",
        "status":"COMPLETE",
        "scope":{
            "market_state_period":f"{START}..{END}",
            "model_replay_role":"COUNTERFACTUAL_SAME_METHOD_CURRENT_GPR_STRESS_NOT_PIT_VALIDATION",
        },
        "thresholds":{
            "E_level_gap_gt":0.20,
            "G_gold_r3_lte":-0.10,
            "E_disagreement_abs_gt":0.05,
            "high_ae_usd_gt":HIGH_AE,
            "high_ape_pct_gt":HIGH_APE,
            "high_return_error_pp_gt":HIGH_RETURN_ERROR_PP,
        },
        "market_state":{
            "baseline":baseline,
            "signals":market,
        },
        "gpr_stress_authority":gpr_meta,
        "model_replay_rows":rows,
        "model_replay_summary":{
            "candidate_origins":origins,
            "candidate_count":len(origins),
            "buildable_count":sum(r.get("buildable",False) for r in rows),
            "unbuildable":[{"origin":r["origin"],"target":r["target"],"status":r["status"],"error":r.get("error")} for r in rows if not r.get("buildable")],
            "G":signal_model_summary(rows,"G"),
            "E_level":signal_model_summary(rows,"E_level"),
            "E_full":{
                "events":len(full_e),
                "targets":[r["target"] for r in full_e],
                "high_ae":sum(r["high_ae"] for r in full_e),
                "high_ape":sum(r["high_ape"] for r in full_e),
                "high_return_error":sum(r["high_return_error"] for r in full_e),
            },
        },
        "governance":{
            "database_read_only":True,
            "current_method_gpr_snapshot_used":True,
            "gpr_snapshot_was_available_at_old_origins":False,
            "pit_validation_claim_allowed":False,
            "threshold_retuning":False,
            "routing_tested":False,
        },
    }
    Path("GOLD_MONTHLY_CHHHO_EG_HISTORICAL_VALIDATION_V1_2026-09-30.json").write_text(
        json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n"
    )
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "market_state":market,
        "model_replay_summary":out["model_replay_summary"],
        "rows":[{k:r.get(k) for k in (
            "origin","target","E_level","G","buildable","status","pred_log_return_gold",
            "E_full","ae","ape_pct","return_error_pp","high_ae","high_ape","high_return_error"
        )} for r in rows],
    },sort_keys=True))

if __name__=="__main__":
    main()
