from __future__ import annotations
"""General target H=1 frozen top-two ANN? No: ChHHO-ANFIS & DE-ABC-RBFNN only.

Reuses the identical frozen optimizer modules and CURRENT8 8-feature formula.
Cannot run a forecast before its origin month completes. No retrospective models
are promoted, and the WorldBank origin publication is not fabricated.
"""
import argparse,hashlib,json,math
from datetime import datetime,timezone
from pathlib import Path
import numpy as np

import vw_midas_msvr_successor_v1 as base
import gold_monthly_public_forward_top2_v1 as runner
import gold_monthly_h1_origin_public_bundle_v1 as source

def load_authorized(path,target):
    raw=json.loads(Path(path).read_text())
    if raw.get("schema")!="GOLD_MONTHLY_H1_ORIGIN_PUBLIC_BUNDLE_V1" or raw.get("target")!=target:
        raise RuntimeError("SOURCE_BUNDLE_TARGET_OR_SCHEMA_MISMATCH")
    fingerprint=raw["payload_sha256"]
    q=dict(raw);q.pop("payload_sha256")
    actual=hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    if actual!=fingerprint:raise RuntimeError("SOURCE_BUNDLE_SHA256_CHANGED")
    origin,origin_last,cutoff=source.month_origin(target)
    if raw["origin"]!=origin:raise RuntimeError("ORIGIN_TARGET_MISMATCH")
    auth=raw["authority"]
    if not auth["source_cutoff_proven"] or not auth["origin_metal_month_complete"]:
        raise RuntimeError("ORIGIN_SOURCE_CUTOFF_NOT_PROVEN")
    if not auth["origin_reference_price_role"]=="STAKTRAKR_COMPLETED_ORIGIN_PROVISIONAL":
        raise RuntimeError("ORIGIN_PRICE_AUTHORITY_CHANGED")
    dates=[x["date"] for x in raw["daily_extension_rows"]]
    if max(dates)>origin_last.isoformat() or max(dates)<source.last_weekday_of_month(origin_last).isoformat():
        raise RuntimeError("ORIGIN_DAILY_ASOF_RANGE_INVALID")
    m=raw["gpr_meta"][origin]
    if m["lag_month"]!=base.month_shift(origin,-1):
        raise RuntimeError("OFFICIAL_GPR_LAG_MISMATCH")
    if datetime.fromisoformat(m["source_committed_at_utc"])>datetime.fromisoformat(raw["origin_cutoff_utc"]):
        raise RuntimeError("GPR_VINTAGE_AFTER_ORIGIN_CUTOFF")
    for k in ("stak","stak_api","gpr"):
        if datetime.fromisoformat(raw["source_commits"][k]["committedAtUtc"])>datetime.fromisoformat(raw["origin_cutoff_utc"]):
            raise RuntimeError(f"{k}_SOURCE_AFTER_ORIGIN_CUTOFF")
    if len({x["date"] for x in raw["daily_extension_rows"] if x["date"].startswith(origin)})<18:
        raise RuntimeError("INCOMPLETE_ORIGIN_MONTH")
    return raw,fingerprint

def forecast(dev_snapshot,current_bundle,target,model):
    raw,source_hash=load_authorized(current_bundle,target)
    origin=raw["origin"]
    bundle,cur,meta=runner.merge_bundle(dev_snapshot,current_bundle)
    if meta["payload_sha256"]!=raw["authority"]["dev_snapshot_payload_sha256"]:
        raise RuntimeError("DEV_SNAPSHOT_CHANGED")
    if target in bundle.core_gold or target in bundle.monthly_metal["Gold"]:
        raise RuntimeError("TARGET_MONTH_ACTUAL_LEAKAGE")
    gh=bundle.gpr_vintages[origin]
    x=runner.forward_x(bundle,target,gh)
    if len(x)!=8 or not np.all(np.isfinite(x)):
        raise RuntimeError("CURRENT8_VECTOR_INVALID")
    feature_json={
      "feature_order":["Au_MR","Au_GPR_VW","Ag_MR","Ag_GPR_VW",
                       "Pt_MR","Pt_GPR_VW","Pd_MR","Pd_GPR_VW"],
      "values":[float(t) for t in x],
      "gpr_lag_value":raw["gpr_meta"][origin]["lag_value"],
      "gpr_normalized":raw["gpr_meta"][origin]["gpr_z"],
      "gpr_origin":origin
    }
    vector_sha=hashlib.sha256(json.dumps(feature_json,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    samples=runner.forward_samples(bundle,target,origin)
    eligible=sorted(t for t in samples if t<target)
    if len(eligible)<24 or eligible[-1]!=origin:
        raise RuntimeError("ORIGIN_TRAINING_ROW_MISSING")
    pred,diag=runner.predict(model,samples,target)
    if not np.all(np.isfinite(pred)) or abs(float(pred[0]))>0.5:
        raise RuntimeError("MODEL_PREDICTION_NUMERIC_GUARD_FAIL")
    origin_mean=float(bundle.monthly_metal["Gold"][origin])
    if not np.isfinite(origin_mean) or origin_mean<=0:
        raise RuntimeError("GOLD_ORIGIN_PROXY_INVALID")
    value=float(origin_mean*math.exp(float(pred[0])))
    return {
      "schema":"GOLD_MONTHLY_H1_FROZEN_FORWARD_V1",
      "target":target,"origin":origin,"model":model,
      "produced_on_utc":datetime.now(timezone.utc).isoformat(),
      "evidence_class":"PROSPECTIVE_FORWARD",
      "research_status":"FROZEN_MODEL_STAKTRAKR_ORIGIN_LEVEL_PROVISIONAL",
      "forecast":value,"origin_reference":origin_mean,
      "reference_authority":"STAKTRAKR_PROVISIONAL",
      "target_actual":None,
      "pred_log_return_gold":float(pred[0]),
      "train_end":origin,
      "train_rows":int(diag.get("train_rows") or len(eligible)),
      "input_feature_vector":feature_json,"input_feature_sha256":vector_sha,
      "input_evidence_class":"FORWARD_ORIGIN_KNOWN_SOURCE_COMMIT",
      "source_bundle_sha256":source_hash,
      "dev_snapshot_sha256":meta["payload_sha256"],
      "official_gpr_xls_sha256":raw["gpr_meta"][origin]["source_xls_sha256"],
      "official_gpr_origin_commit":raw["gpr_meta"][origin]["source_commit_sha"],
      "source_commits":raw["source_commits"],
      "origin_cutoff_utc":raw["origin_cutoff_utc"],
      "source_data_first_provenance":{"neon_reads":0,"historical_training_pit_all_origins":False,
        "origin_daily_commit_by_cutoff":True,"official_gpr_vintage_by_cutoff":True,
        "world_bank_origin_reference_proven":False,
        "target_month_actual_used":False},
      "diagnostics":diag
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dev-snapshot",required=True)
    p.add_argument("--current-bundle",required=True)
    p.add_argument("--target",required=True)
    p.add_argument("--model",required=True,choices=("CHHHO","DE_ABC"))
    p.add_argument("--output",required=True)
    args=p.parse_args()
    out=forecast(args.dev_snapshot,args.current_bundle,args.target,args.model)
    Path(args.output).write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("GOLD_MONTHLY_H1_FROZEN_FORWARD_GATE=PASS",
      json.dumps({k:out[k] for k in ("target","model","forecast","origin_reference","train_end","input_feature_sha256")},sort_keys=True))

if __name__=="__main__":main()
