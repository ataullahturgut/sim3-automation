from __future__ import annotations

import argparse, json, math, os
from pathlib import Path
import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import gold_monthly_external_driver_residual_v1 as core
import gold_monthly_f4_b1_transform_parity_v1 as b1

FEATURES=[
  "BRENT_MR1","BRENT_VW","BRENT_RVOL","BRENT_DOWNSIDE_VOL","BRENT_MAX_DD"
]
BLOCKS={
  "B1_MR1":["BRENT_MR1"],
  "B2_MR1_RVOL":["BRENT_MR1","BRENT_RVOL"],
  "B3_MR1_DOWNSIDE":["BRENT_MR1","BRENT_DOWNSIDE_VOL"],
  "B4_MR1_MAXDD":["BRENT_MR1","BRENT_MAX_DD"],
  "B5_MR1_RVOL_DOWNSIDE_MAXDD":["BRENT_MR1","BRENT_RVOL","BRENT_DOWNSIDE_VOL","BRENT_MAX_DD"],
  "B6_ALL5":["BRENT_MR1","BRENT_VW","BRENT_RVOL","BRENT_DOWNSIDE_VOL","BRENT_MAX_DD"],
}

def bias_prequential(rows):
    out=[]
    for i,r in enumerate(rows):
        z=dict(r); z["correction"]=0.0; z["corrected_forecast"]=float(r["forecast"]); z["eligible"]=False
        prior=rows[:i]
        if len(prior)>=core.MIN_HISTORY:
            y=np.asarray([q["actual"]-q["forecast"] for q in prior],float)
            pred=float(np.mean(y))
            cap=core.CAP_MULT*float(np.median(np.abs(y)))
            pred=float(np.clip(pred,-cap,cap))
            z["correction"]=pred
            z["corrected_forecast"]=float(r["forecast"]+pred)
            z["eligible"]=True
        out.append(z)
    return out

def incremental_gate(rows,bias_rows,cand_rows):
    b={r["target"]:r for r in bias_rows if r.get("eligible")}
    c={r["target"]:r for r in cand_rows if r.get("eligible")}
    common=[r["target"] for r in rows if r["target"] in b and r["target"] in c]
    if not common:
        return {"pass":False,"reason":"NO_COMMON_ELIGIBLE"}
    diffs=[]
    y24=[]
    for t in common:
        rb=b[t]; rc=c[t]
        actual=float(rc["actual"])
        imp=abs(float(rb["corrected_forecast"])-actual)-abs(float(rc["corrected_forecast"])-actual)
        diffs.append(imp)
        if t.startswith("2024"): y24.append(imp)
    diffs=np.asarray(diffs,float)
    total=float(diffs.sum())
    robust=float(total-diffs[int(np.argmax(diffs))]) if len(diffs)>1 else -1e9
    y24imp=float(np.sum(y24)) if y24 else 0.0
    return {
      "pass":bool(total>0 and robust>0 and y24imp>0),
      "n":len(common),
      "incremental_sum_ae_improvement_vs_bias":total,
      "incremental_improvement_excluding_single_best_month":robust,
      "incremental_2024_improvement_vs_bias":y24imp,
    }

def build_features(external_v2, rows, dsn):
    doc=json.loads(Path(external_v2).read_text())
    brent=b1.flat_daily(doc,"brent_daily")
    bundle=base.load_data(dsn)
    out={}; meta={}
    for r in rows:
        origin=r["origin"]; prev=b1.mshift(origin,-1)
        vp,last_p,np_=b1.eligible_month_values(brent,origin,b1.LAGS["BRENT"])
        vq,last_q,nq=b1.eligible_month_values(brent,prev,b1.LAGS["BRENT"])
        if np.any(vp<=0) or np.any(vq<=0):
            raise RuntimeError(f"NONPOSITIVE_BRENT {origin}")
        mr1=float(math.log(float(np.mean(vp))/float(np.mean(vq))))
        lr=np.diff(np.log(vp))
        rvol=float(math.sqrt(float(np.sum(lr*lr)))) if len(lr) else 0.0
        neg=np.minimum(lr,0.0)
        downside=float(math.sqrt(float(np.sum(neg*neg)))) if len(neg) else 0.0
        running=np.maximum.accumulate(vp)
        dd=1.0-vp/running
        maxdd=float(np.max(dd)) if len(dd) else 0.0

        if origin not in bundle.gpr_vintages:
            raise RuntimeError(f"GPR_VINTAGE_MISSING {origin}")
        gh=bundle.gpr_vintages[origin]
        z=base.gpr_norm(gh,prev)
        vw=float(b1.generic_weighted_increment(vp,z,log_mode=True))

        out[origin]={
          "BRENT_MR1":mr1,
          "BRENT_VW":vw,
          "BRENT_RVOL":rvol,
          "BRENT_DOWNSIDE_VOL":downside,
          "BRENT_MAX_DD":maxdd,
        }
        meta[origin]={
          "origin_n":int(np_),"previous_n":int(nq),
          "origin_last":last_p,"previous_last":last_q,
          "gpr_z":float(z),
        }
    return doc,out,meta,bundle

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--chhho",required=True)
    ap.add_argument("--external-v2",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")

    m=core.load_model(a.chhho,"ChHHO-ANFIS")
    doc,ext,feature_meta,bundle=build_features(a.external_v2,m["dev"],dsn)
    bias=bias_prequential(m["dev"])
    bias_full=core.metrics(bias,"corrected_forecast")
    bias_gate=core.stability_gate(m["dev"],bias)

    result={
      "schema":"GOLD_MONTHLY_CHHHO_BRENT_EXPANDED_RESIDUAL_SCREEN_V1_2026-09-29",
      "authority":{
        "base_model_frozen":True,
        "base_artifact_id":10989389723,
        "external_authority_v2_artifact_id":11028494060,
        "selection":"DEV_2022-04..2024-12_ONLY",
        "2025_used_for_selection":False,
        "2026_used_for_selection":False,
        "database_access":"READ_ONLY",
        "random_split":False,
        "residual_target":"actual price - frozen ChHHO BASE price forecast",
        "learner":"Ridge",
        "ridge_alpha":core.RIDGE_ALPHA,
        "min_prior_residuals":core.MIN_HISTORY,
        "cap_multiple":core.CAP_MULT,
        "chronology":"prequential; prior DEV residuals only",
        "brent_release_lag_calendar_days":b1.LAGS["BRENT"],
        "bias_only_incremental_gate_required":True,
        "feature_definitions":{
          "BRENT_MR1":"log(mean eligible origin-month Brent / mean eligible previous-month Brent)",
          "BRENT_VW":"GPR-weighted daily Brent log-return summary using CURRENT8 weighting",
          "BRENT_RVOL":"sqrt(sum(daily Brent log-return^2)) in eligible origin month",
          "BRENT_DOWNSIDE_VOL":"sqrt(sum(min(daily Brent log-return,0)^2)) in eligible origin month",
          "BRENT_MAX_DD":"maximum peak-to-trough fractional drawdown within eligible origin month",
        },
        "blocks_frozen_before_outcomes":BLOCKS,
      },
      "external_authority_v2_payload_sha256":doc.get("payload_sha256"),
      "base_metrics":core.metrics(m["dev"]),
      "bias_only":{
        "full_metrics":bias_full,
        "gate":bias_gate,
        "rows":bias,
      },
      "feature_meta":feature_meta,
      "blocks":{},
    }

    promotable=[]
    for name,cols in BLOCKS.items():
        corr=core.prequential(m["dev"],ext,cols)
        base_gate=core.stability_gate(m["dev"],corr)
        inc=incremental_gate(m["dev"],bias,corr)
        fm=core.metrics(corr,"corrected_forecast")
        result["blocks"][name]={
          "columns":cols,
          "full_metrics":fm,
          "base_gate":base_gate,
          "incremental_vs_bias_gate":inc,
          "diagnostics":core.diagnostic(m["dev"],ext,cols),
          "rows":corr,
        }
        if base_gate.get("pass") and inc.get("pass"):
            promotable.append((fm["sum_ae"],name))

    promotable.sort()
    result["selected_on_dev"]=promotable[0][1] if promotable else "BIAS_ONLY"
    result["external_driver_promoted"]=bool(promotable)

    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            inv=base.authority_invariants(cur)
    if inv!=bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    result["authority_invariants_before"]=bundle.invariants_before
    result["authority_invariants_after"]=inv

    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_BRENT_EXPANDED_RESIDUAL_SCREEN_GATE=PASS")
    print(json.dumps({
      "base":result["base_metrics"],
      "bias_only":bias_full,
      "selected_on_dev":result["selected_on_dev"],
      "external_driver_promoted":result["external_driver_promoted"],
      "blocks":{
        k:{
          "full_sum_ae":v["full_metrics"]["sum_ae"],
          "full_direction":v["full_metrics"]["direction_correct"],
          "base_gate_pass":v["base_gate"].get("pass"),
          "incremental_vs_bias":v["incremental_vs_bias_gate"],
        } for k,v in result["blocks"].items()
      }
    },sort_keys=True))

if __name__=="__main__":
    main()
