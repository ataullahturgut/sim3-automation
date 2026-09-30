from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

import numpy as np

DEV_START, DEV_END = "2022-04", "2024-12"
TRANSPORT_START, TRANSPORT_END = "2025-01", "2026-07"

BOOST_MODELS = ("CATBOOST_ORDERED", "RANDOM_FOREST_ANCHOR")
SVR_REPS = ("CURRENT8", "DAILY_SUMMARY12", "MIXED20")


def load_json(path: str):
    return json.loads(Path(path).read_text())


def month_range(start: str, end: str):
    y, m = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    while (y, m) <= (ey, em):
        yield f"{y:04d}-{m:02d}"
        m += 1
        if m == 13:
            y += 1
            m = 1


def metrics(rows):
    a=np.asarray([float(r["actual"]) for r in rows],float)
    f=np.asarray([float(r["forecast"]) for r in rows],float)
    rw=np.asarray([float(r["rw"]) for r in rows],float)
    ae=np.abs(f-a)
    d=[bool(r["direction_correct"]) for r in rows]
    return {
        "n":len(rows),
        "sum_abs_error":float(ae.sum()),
        "mae":float(ae.mean()),
        "rmse":float(np.sqrt(np.mean((f-a)**2))),
        "mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100),
        "relative_mae_vs_rw":float(ae.sum()/np.maximum(np.abs(rw-a).sum(),1e-12)),
        "direction_correct":int(sum(d)),
    }


def compare_boost_or_svr(new_rows, old_rows, family: str):
    om={r["target"]:r for r in old_rows}
    diffs=[]
    for r in new_rows:
        o=om[r["target"]]
        dlog=abs(float(r["pred_log_return_gold"])-float(o["pred_log_return_gold"]))
        df=abs(float(r["forecast"])-float(o["forecast"]))
        tr_key="train_rows"
        same_train=int(r[tr_key])==int(o[tr_key])
        diffs.append({
            "target":r["target"],
            "pred_log_return_abs_diff":dlog,
            "forecast_abs_diff":df,
            "train_rows_match":same_train,
        })
    max_log=max(x["pred_log_return_abs_diff"] for x in diffs)
    max_fc=max(x["forecast_abs_diff"] for x in diffs)
    gate=bool(
        len(new_rows)==33
        and max_log <= 1e-10
        and max_fc <= 1e-7
        and all(x["train_rows_match"] for x in diffs)
    )
    return {
        "family":family,
        "status":"PASS" if gate else "FAIL",
        "max_pred_log_return_abs_diff":max_log,
        "max_forecast_abs_diff":max_fc,
        "all_train_rows_match":all(x["train_rows_match"] for x in diffs),
        "tolerance_pred_log_return":1e-10,
        "tolerance_forecast_usd":1e-7,
        "row_diffs":diffs,
    }


def compare_seq(new_rows, old_rows):
    om={r["target"]:r for r in old_rows}
    diffs=[]
    for r in new_rows:
        o=om[r["target"]]
        dlog=abs(float(r["pred_log_return_gold"])-float(o["pred_log_return_gold"]))
        df=abs(float(r["forecast"])-float(o["forecast"]))
        diffs.append({
            "target":r["target"],
            "pred_log_return_abs_diff":dlog,
            "forecast_abs_diff":df,
            "selected_seed_match":int(r["selected_seed"])==int(o["selected_seed"]),
            "selected_best_epoch_match":int(r["selected_best_epoch"])==int(o["selected_best_epoch"]),
            "train_sequence_rows_match":int(r["train_sequence_rows"])==int(o["train_sequence_rows"]),
        })
    newm=metrics(new_rows)
    oldm=metrics(old_rows)
    sae_diff=abs(newm["sum_abs_error"]-oldm["sum_abs_error"])
    gate=bool(
        len(new_rows)==33
        and max(x["pred_log_return_abs_diff"] for x in diffs) <= 5e-5
        and max(x["forecast_abs_diff"] for x in diffs) <= 0.10
        and all(x["selected_seed_match"] for x in diffs)
        and all(x["selected_best_epoch_match"] for x in diffs)
        and all(x["train_sequence_rows_match"] for x in diffs)
        and sae_diff <= 1.0
        and newm["direction_correct"]==oldm["direction_correct"]
    )
    return {
        "family":"SEQ_STAGE1A",
        "status":"PASS" if gate else "FAIL",
        "max_pred_log_return_abs_diff":max(x["pred_log_return_abs_diff"] for x in diffs),
        "max_forecast_abs_diff":max(x["forecast_abs_diff"] for x in diffs),
        "dev_sum_abs_error_abs_diff":sae_diff,
        "new_dev_direction_correct":newm["direction_correct"],
        "old_dev_direction_correct":oldm["direction_correct"],
        "all_selected_seed_match":all(x["selected_seed_match"] for x in diffs),
        "all_selected_best_epoch_match":all(x["selected_best_epoch_match"] for x in diffs),
        "all_train_sequence_rows_match":all(x["train_sequence_rows_match"] for x in diffs),
        "tolerance_pred_log_return":5e-5,
        "tolerance_forecast_usd":0.10,
        "tolerance_dev_sum_abs_error_usd":1.0,
        "row_diffs":diffs,
    }


def run_boost(original_path: str):
    import vw_midas_msvr_successor_v1 as base
    import gold_monthly_boosting_stage1_canonical_v1 as mod

    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    old=load_json(original_path)
    b=base.load_data(dsn)

    dev={}
    transport={}
    reproduction={}
    for name in BOOST_MODELS:
        dev_cache={t:base.all_samples_at_origin(b,t,governed=True) for t in month_range(DEV_START,DEV_END)}
        dev_rows=[mod.predict_one(b,dev_cache[t],t,name) for t in month_range(DEV_START,DEV_END)]
        reproduction[name]=compare_boost_or_svr(dev_rows,old["models"][name]["rows"],"BOOST_STAGE1")
        if reproduction[name]["status"]!="PASS":
            raise RuntimeError(("DEV_REPRO_FAIL",name,reproduction[name]))
        dev[name]=dev_rows

        tr_rows=[]
        for t in month_range(TRANSPORT_START,TRANSPORT_END):
            samples=base.all_samples_at_origin(b,t,governed=True)
            tr_rows.append(mod.predict_one(b,samples,t,name))
        transport[name]=tr_rows

    return {
        "schema":"GOLD_MONTHLY_MISSING9_FROZEN_TRANSPORT_BOOST_V1_2026-09-30",
        "status":"COMPLETE",
        "family":"BOOST_STAGE1",
        "models":list(BOOST_MODELS),
        "transport_period":[TRANSPORT_START,TRANSPORT_END],
        "reproduction":reproduction,
        "dev_reproduced":dev,
        "transport":transport,
        "governance":{
            "frozen_contract_changed":False,
            "hyperparameters_changed":False,
            "2025_2026_used_for_selection":False,
            "database":"READ_ONLY",
        },
    }


def run_svr(original_path: str):
    import vw_midas_msvr_successor_v1 as base
    import gold_monthly_svr_dwt_stage2b_representation_v1 as mod

    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    old=load_json(original_path)
    b=base.load_data(dsn)

    dev={}
    transport={}
    reproduction={}
    for rep in SVR_REPS:
        dev_rows=[mod.predict_one(b,t,rep) for t in month_range(DEV_START,DEV_END)]
        reproduction[rep]=compare_boost_or_svr(dev_rows,old["results"][rep]["rows"],"SVR_STAGE2B")
        if reproduction[rep]["status"]!="PASS":
            raise RuntimeError(("DEV_REPRO_FAIL",rep,reproduction[rep]))
        dev[rep]=dev_rows

        tr_rows=[mod.predict_one(b,t,rep) for t in month_range(TRANSPORT_START,TRANSPORT_END)]
        transport[rep]=tr_rows

    return {
        "schema":"GOLD_MONTHLY_MISSING9_FROZEN_TRANSPORT_SVR_V1_2026-09-30",
        "status":"COMPLETE",
        "family":"SVR_STAGE2B",
        "representations":list(SVR_REPS),
        "transport_period":[TRANSPORT_START,TRANSPORT_END],
        "reproduction":reproduction,
        "dev_reproduced":dev,
        "transport":transport,
        "governance":{
            "frozen_contract_changed":False,
            "representation_changed":False,
            "kernel_changed":False,
            "2025_2026_used_for_selection":False,
            "database":"READ_ONLY",
        },
    }


def run_seq(original_path: str, model: str, lookback: int):
    import vw_midas_msvr_successor_v1 as base
    import gold_monthly_cnn_lstm_stage1a_v1 as mod

    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    old=load_json(original_path)
    expected_id=f"GOLD_MONTHLY_CNN_LSTM_STAGE1A_{model}_LB{lookback}_V1"
    if old["model_id"]!=expected_id:
        raise RuntimeError(("ORIGINAL_MODEL_ID_MISMATCH",old["model_id"],expected_id))

    mod.LOOKBACK=int(lookback)
    mod.configure_tf()

    # Exact original DEV data scope for the reproduction gate.
    bdev=mod.load_dev_data(dsn)
    dev_rows=[]
    for t in month_range(DEV_START,DEV_END):
        samples=base.all_samples_at_origin(bdev,t,governed=True)
        dev_rows.append(mod.evaluate_origin(bdev,samples,t,model))

    reproduction=compare_seq(dev_rows,old["dev"]["rows"])
    if reproduction["status"]!="PASS":
        raise RuntimeError(("DEV_REPRO_FAIL",expected_id,reproduction))

    # Full origin-safe bundle only after frozen DEV reproduction passes.
    b=base.load_data(dsn)
    tr_rows=[]
    for t in month_range(TRANSPORT_START,TRANSPORT_END):
        samples=base.all_samples_at_origin(b,t,governed=True)
        tr_rows.append(mod.evaluate_origin(b,samples,t,model))

    return {
        "schema":"GOLD_MONTHLY_MISSING9_FROZEN_TRANSPORT_SEQ_V1_2026-09-30",
        "status":"COMPLETE",
        "family":"SEQ_STAGE1A",
        "model_id":expected_id,
        "model":model,
        "lookback":int(lookback),
        "transport_period":[TRANSPORT_START,TRANSPORT_END],
        "reproduction":reproduction,
        "dev_reproduced":dev_rows,
        "transport":tr_rows,
        "governance":{
            "frozen_contract_changed":False,
            "architecture_changed":False,
            "seed_grid_changed":False,
            "inner_validation_changed":False,
            "2025_2026_used_for_selection":False,
            "database":"READ_ONLY",
        },
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--family",required=True,choices=("BOOST","SVR","SEQ"))
    ap.add_argument("--original-json",required=True)
    ap.add_argument("--model",choices=("LSTM","CNN_LSTM"))
    ap.add_argument("--lookback",type=int,choices=(3,6))
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    if args.family=="BOOST":
        out=run_boost(args.original_json)
    elif args.family=="SVR":
        out=run_svr(args.original_json)
    else:
        if not args.model or not args.lookback:
            raise SystemExit("--model and --lookback required for SEQ")
        out=run_seq(args.original_json,args.model,args.lookback)

    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "family":out["family"],
        "status":out["status"],
        "transport_period":out["transport_period"],
        "reproduction":out["reproduction"],
    },sort_keys=True))


if __name__=="__main__":
    main()
