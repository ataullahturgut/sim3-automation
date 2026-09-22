from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

from regime_v1_data import (
    load_external, load_governed, to_logit_days, to_ttsm_days, logit_mod, ttsm_mod
)
from regime_v1_router_sqrt import sqrt_rows

IDENTITY = "SQRT_PURE_UP_DETECTOR_CONDITIONAL_AUDIT_V1_RESEARCH"
OUT = Path("sqrt_pure_up_audit_out")
EXPECTED_ALARMS = {2020:212, 2021:28, 2022:11, 2023:2, 2024:17}
EXPECTED_CLASSES = {"HIT_DOWN":115, "HIT_UP":103, "MISS":52}


def rv_logit_map(days):
    dl = to_logit_days(days)
    out = {}
    for i in range(1, len(dl)-1):
        origin = dl[i]
        if not math.isfinite(origin.lag1_return):
            continue
        train_idx = list(range(1, i))
        if len(train_idx) < 250:
            continue
        y = np.array([
            1.0 if math.log(dl[j+1].close / dl[j].close) > 0 else 0.0
            for j in train_idx
        ], dtype=float)
        X = np.array([[float(dl[j].log_rv)] for j in train_idx], dtype=float)
        xn = np.array([float(origin.log_rv)], dtype=float)
        p, _ = logit_mod.fit_logit_predict(X, y, xn)
        ret = math.log(dl[i+1].close / origin.close)
        if ret == 0:
            continue
        out[dl[i+1].d.isoformat()] = {
            "origin_date": origin.d.isoformat(),
            "actual_up": int(ret > 0),
            "p_up": float(p),
            "up": int(p >= 0.5),
        }
    return out


def ttsm_s2_map(days):
    rows = ttsm_mod.build_signal_rows(to_ttsm_days(days))
    return {
        r["target_date"]: {
            "origin_date": r["origin_date"],
            "actual_up": int(r["actual_up"]),
            "up": int(r["ttsm_s2_signal"] == 1),
            "raw_signal": int(r["ttsm_s2_signal"]),
        }
        for r in rows
    }


def metrics(rows, model):
    avail = [r for r in rows if r[f"{model}_available"]]
    if not avail:
        return {"n_total":len(rows),"n_available":0,"coverage":0.0}
    y = np.array([int(r["actual_up"]) for r in avail], dtype=int)
    pred = np.array([int(r[f"{model}_up"]) for r in avail], dtype=int)
    tp = int(np.sum((y==1)&(pred==1)))
    fp = int(np.sum((y==0)&(pred==1)))
    tn = int(np.sum((y==0)&(pred==0)))
    fn = int(np.sum((y==1)&(pred==0)))
    actual_up = tp+fn
    actual_down = tn+fp
    pred_up = tp+fp
    pred_down = tn+fn
    up_precision = tp/pred_up if pred_up else None
    up_recall = tp/actual_up if actual_up else None
    fpr = fp/actual_down if actual_down else None
    down_precision = tn/pred_down if pred_down else None
    down_recall = tn/actual_down if actual_down else None
    acc = (tp+tn)/len(avail)
    ba = ((up_recall or 0)+(down_recall or 0))/2 if actual_up and actual_down else None
    return {
        "n_total": len(rows),
        "n_available": len(avail),
        "coverage": len(avail)/len(rows) if rows else None,
        "actual_up": actual_up,
        "actual_down": actual_down,
        "pred_up": pred_up,
        "pred_down": pred_down,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "up_precision": up_precision,
        "up_recall": up_recall,
        "false_up_fpr": fpr,
        "down_precision": down_precision,
        "down_recall": down_recall,
        "accuracy": acc,
        "balanced_accuracy": ba,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ext = load_external()
    gov = load_governed()

    all_rows = []
    integrity = []

    for year in (2020,2021,2022,2023,2024):
        days = ext if year <= 2021 else gov
        rvmap = rv_logit_map(days)
        tmap = ttsm_s2_map(days)
        parents = sqrt_rows(days, year)
        alarms = [r for r in parents if r["sqrt_alarm"]]
        if len(alarms) != EXPECTED_ALARMS[year]:
            integrity.append(f"ALARM_{year}:{len(alarms)}!={EXPECTED_ALARMS[year]}")
        for s in alarms:
            td = s["target_date"]
            actual_up = int(float(s["target_return"]) > 0)
            hit = int(float(s["target_dr"]) >= float(s["q80"]))
            cls = "HIT_UP" if hit and actual_up else ("HIT_DOWN" if hit else "MISS")
            rr = {
                "year": year,
                "origin_date": s["origin_date"],
                "target_date": td,
                "q80": float(s["q80"]),
                "sqrt_forecast": float(s["sqrt_forecast"]),
                "target_dr": float(s["target_dr"]),
                "target_return": float(s["target_return"]),
                "risk_hit": hit,
                "actual_up": actual_up,
                "outcome_class": cls,
            }
            rv = rvmap.get(td)
            tt = tmap.get(td)
            rr["RV_LOGIT_available"] = int(rv is not None)
            rr["RV_LOGIT_up"] = int(rv["up"]) if rv else ""
            rr["RV_LOGIT_p_up"] = float(rv["p_up"]) if rv else ""
            rr["TTSM_S2_available"] = int(tt is not None)
            rr["TTSM_S2_up"] = int(tt["up"]) if tt else ""
            rr["TTSM_S2_signal"] = int(tt["raw_signal"]) if tt else ""
            if rv and int(rv["actual_up"]) != actual_up:
                integrity.append(f"RV_ACTUAL_MISMATCH:{td}")
            if tt and int(tt["actual_up"]) != actual_up:
                integrity.append(f"TTSM_ACTUAL_MISMATCH:{td}")
            all_rows.append(rr)

    counts = Counter(r["outcome_class"] for r in all_rows)
    if len(all_rows) != 270:
        integrity.append(f"POOLED_N:{len(all_rows)}!=270")
    for k,v in EXPECTED_CLASSES.items():
        if counts[k] != v:
            integrity.append(f"CLASS_{k}:{counts[k]}!={v}")

    by_year = {}
    for y in (2020,2021,2022,2023,2024):
        yr=[r for r in all_rows if r["year"]==y]
        hit=[r for r in yr if r["risk_hit"]]
        by_year[str(y)] = {
            "all_sqrt_alarms": {
                "RV_LOGIT": metrics(yr,"RV_LOGIT"),
                "TTSM_S2": metrics(yr,"TTSM_S2"),
            },
            "realized_high_risk_only": {
                "RV_LOGIT": metrics(hit,"RV_LOGIT"),
                "TTSM_S2": metrics(hit,"TTSM_S2"),
            },
        }

    hit_all=[r for r in all_rows if r["risk_hit"]]
    pooled = {
        "all_sqrt_alarms": {
            "RV_LOGIT": metrics(all_rows,"RV_LOGIT"),
            "TTSM_S2": metrics(all_rows,"TTSM_S2"),
        },
        "realized_high_risk_only": {
            "RV_LOGIT": metrics(hit_all,"RV_LOGIT"),
            "TTSM_S2": metrics(hit_all,"TTSM_S2"),
        },
    }

    result = {
        "identity": IDENTITY,
        "integrity_errors": integrity,
        "primary_manifest_leader": "RV_LOGIT",
        "secondary_transport_comparator": "TTSM_S2",
        "router_used": False,
        "rule": "UP signal => UP; otherwise => DOWN",
        "observed_counts": dict(counts),
        "by_year": by_year,
        "pooled_2020_2024": pooled,
        "interpretation_limit": (
            "Descriptive retrospective anatomy. RV_LOGIT was selected as the pre-2025 "
            "pure-UP leader using pooled 2023-2024 evidence; earlier-year performance is "
            "not prospective model-selection evidence."
        ),
    }
    (OUT/"GOLD_CONTROL_SQRT_PURE_UP_DETECTOR_CONDITIONAL_AUDIT_V1_RESULT_2026-09-22.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )

    fields=list(all_rows[0].keys())
    with (OUT/"GOLD_CONTROL_SQRT_PURE_UP_DETECTOR_CONDITIONAL_AUDIT_V1_LEDGER_2026-09-22.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(all_rows)

    print(json.dumps({
        "integrity_errors": integrity,
        "pooled": pooled,
    }, indent=2))


if __name__=="__main__":
    main()
