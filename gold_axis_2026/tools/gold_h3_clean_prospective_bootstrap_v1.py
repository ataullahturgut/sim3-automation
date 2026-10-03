from __future__ import annotations
# bootstrap rerun after pinned STAK source env fix
import json, math, os
from pathlib import Path

# The imported prospective harness resolves this at import time.
os.environ.setdefault("STAK_LIVE_REF", "54fdf1c8d39b7b6c7b874d0f30f784296e886044")
import numpy as np, pandas as pd

import gold_h3_aurora_prospective_v1 as base
import gold_h3_iris_v1 as iris
import gold_h3_rift_v1 as rift
import gold_h3_turn_v1 as turn
import gold_h3_vega_v1 as vega
import gold_h3_opal_v1 as opal

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("OUT_DIR","gold_h3_clean_prospective_bootstrap_out"))
OUT.mkdir(parents=True,exist_ok=True)

OLD_PRICE=ROOT/"gold_axis_2026"/"GOLD_H3_AURORA_V1_FROZEN_DAILY_PRICES.csv"
OLD_MATRIX=ROOT/"gold_axis_2026"/"GOLD_H3_AURORA_V1_FROZEN_EXPERT_TRAIN_MATRIX.csv"
CLEAN_A1=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_NOVA_A1_PREDICTIONS_2026-10-03.csv"
CLEAN_EXPERT=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_EXPERT_LEDGER_2026-10-03.csv"
CLEAN_AURORA=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_AURORA_PREDICTIONS_2026-10-03.csv"
CLEAN_RIFT=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv"
CLEAN_TURN=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_TURN_PREDICTIONS_2026-10-03.csv"
CLEAN_VEGA=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv"
CLEAN_OPAL=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_OPAL_PREDICTIONS_2026-10-03.csv"

PATCH_DATE=pd.Timestamp("2026-02-27")
PATCH={"gold":5183.80,"silver":88.14,"platinum":2369.25,"palladium":1789.96}

def compare(path_ref, pred, pcol):
    ref=pd.read_csv(path_ref)
    for c in ["forecast_issue_date"]:
        ref[c]=pd.to_datetime(ref[c]); pred[c]=pd.to_datetime(pred[c])
    z=ref[["forecast_issue_date",pcol,"override"]].merge(
        pred[["forecast_issue_date",pcol,"override"]],
        on="forecast_issue_date",how="inner",suffixes=("_ref","_new"),validate="one_to_one")
    if len(z)!=len(ref):
        raise RuntimeError(f"REPRO_MATCH_FAIL {path_ref.name} ref={len(ref)} got={len(z)}")
    maxdiff=float(np.max(np.abs(z[f"{pcol}_ref"].astype(float)-z[f"{pcol}_new"].astype(float))))
    same=bool((z.override_ref.astype(str).str.lower()==z.override_new.astype(str).str.lower()).all())
    return {"rows":int(len(z)),"max_abs_prob_diff":maxdiff,"override_equal":same,"pass":bool(maxdiff<=1e-10 and same)}

def main():
    # 1) Clean frozen price snapshot.
    px=pd.read_csv(OLD_PRICE)
    px["date"]=pd.to_datetime(px.date)
    if PATCH_DATE not in set(px.date): raise RuntimeError("PATCH_DATE_MISSING")
    old=px.loc[px.date==PATCH_DATE,["gold","silver","platinum","palladium"]].iloc[0].to_dict()
    for k,v in PATCH.items(): px.loc[px.date==PATCH_DATE,k]=float(v)
    px.to_csv(OUT/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv",index=False)

    # 2) Clean frozen AURORA expert training matrix.
    m=pd.read_csv(OLD_MATRIX)
    a=pd.read_csv(CLEAN_A1)
    for df in [m,a]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in df.columns: df[c]=pd.to_datetime(df[c],errors="raise")
    aa=a[["feature_cutoff_date","forecast_issue_date","target_end_date_h3","target_r3","y_up","p_A1_arcr"]].copy()
    x=m.drop(columns=["target_end_date_h3","target_r3","y_up","p_A1_arcr","base_logit"]).merge(
        aa,on=["feature_cutoff_date","forecast_issue_date"],how="inner",validate="one_to_one")
    if len(x)!=len(m): raise RuntimeError(f"CLEAN_MATRIX_MATCH_FAIL {len(x)} {len(m)}")
    p=np.clip(x.p_A1_arcr.astype(float).to_numpy(),1e-6,1-1e-6)
    x["base_logit"]=np.log(p/(1-p))
    cols=["feature_cutoff_date","forecast_issue_date","target_end_date_h3","target_r3","y_up","p_A1_arcr","base_logit"]+list(base.PATH)
    x=x[cols].sort_values("forecast_issue_date").reset_index(drop=True)
    x.to_csv(OUT/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_EXPERT_TRAIN_MATRIX.csv",index=False)

    # AURORA reproduction against clean expert ledger.
    old_sentry=base.SENTRY_FILE
    base.SENTRY_FILE=CLEAN_EXPERT
    audit=base.reproduction_audit(x)
    base.SENTRY_FILE=old_sentry
    if not audit["pass"]: raise RuntimeError(f"CLEAN_AURORA_REPRO_FAIL {audit}")

    # 3) Freeze exact clean historical reversal training panels.
    # Cache the same hourly extension once so every expert sees identical bytes.
    hist=iris.load_neon_hourly()
    succ,api_calls=iris.fetch_extension()
    _,bridge=iris.bridge_metrics(hist,succ)
    if not bridge["pass"]:
        raise RuntimeError(f"CLEAN_BOOTSTRAP_HOURLY_BRIDGE_FAIL {bridge}")
    iris.load_neon_hourly=lambda: hist.copy()
    iris.fetch_extension=lambda: (succ.copy(), api_calls)

    rift.AURORA=CLEAN_AURORA
    rp,_,_=rift.load_panel(); rp.to_csv(OUT/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv",index=False)
    rpred=rift.run_rift(rp); rr=compare(CLEAN_RIFT,rpred,"p_rift")

    turn.AURORA=CLEAN_AURORA
    tpred,_,_=turn.apply_turn(); tr=compare(CLEAN_TURN,tpred,"p_turn")

    vega.AURORA=CLEAN_AURORA
    vp,_,_,_=vega.load_panel(); vp.to_csv(OUT/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_VEGA_PANEL.csv",index=False)
    vpred=vega.run_vega(vp); vr=compare(CLEAN_VEGA,vpred,"p_vega")

    opal.AURORA=CLEAN_AURORA
    op,_,_,_,_=opal.load_panel(); op.to_csv(OUT/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_OPAL_PANEL.csv",index=False)
    opred=opal.run_opal(op); orr=compare(CLEAN_OPAL,opred,"p_opal")

    checks={"aurora_reproduction":audit,"rift":rr,"turn":tr,"vega":vr,"opal":orr}
    passed=bool(audit["pass"] and rr["pass"] and tr["pass"] and vr["pass"] and orr["pass"])
    if not passed: raise RuntimeError(f"CLEAN_PROSPECTIVE_BOOTSTRAP_FAIL {checks}")

    summary={
      "schema":"CLEAN_H3_PROSPECTIVE_V1_BOOTSTRAP",
      "status":"PASS",
      "first_eligible_feature_cutoff":"2026-10-05",
      "price_patch":{"date":"2026-02-27","old":old,"clean":PATCH},
      "checks":checks,
    }
    (OUT/"bootstrap_summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    lines=["# CLEAN H3 PROSPECTIVE V1 — BOOTSTRAP RESULT","",
      "**Status:** PASS","",
      "- first eligible feature cutoff: **2026-10-05**",
      "- clean 2026-02-27 four-metal overlay frozen",
      "- clean AURORA expert matrix reproduces the clean retrospective September ledger",
      "- RIFT/TURN/VEGA/OPAL historical predictions reproduce the recorded clean chain","",
      "## Reproduction checks",""]
    for k,v in checks.items(): lines.append(f"- {k}: `{json.dumps(v,sort_keys=True,default=str)}`")
    (OUT/"BOOTSTRAP_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"BOOTSTRAP_RESULT.md").read_text())

if __name__=="__main__": main()
