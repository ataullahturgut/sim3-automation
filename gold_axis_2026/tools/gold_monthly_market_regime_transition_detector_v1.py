from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import logsumexp

import gold_monthly_market_regime_discovery_v1 as base
import gold_monthly_market_regime_prototype_alignment_v1 as palign

EVAL_START = "2015-07"
CORE_START = "2022-01"
TRANSPORT_START = "2025-01"
END = "2026-08"
CONFIDENCE = 0.60
FEATURES = list(base.FEATURES)
R_STATES = ["R0", "R1", "R2"]


def load_json(path: str):
    return json.loads(Path(path).read_text())


def next_month(month: str) -> str:
    return str(pd.Period(month, freq="M") + 1)


def month_diff(a: str, b: str) -> int:
    return int(pd.Period(b, freq="M").ordinal - pd.Period(a, freq="M").ordinal)


def empirical_percentile(pool: np.ndarray, value: float) -> float:
    if len(pool) == 0:
        return float("nan")
    return float(np.mean(pool <= value))


def training_predictive_scores(model, posts: np.ndarray, loge: np.ndarray) -> np.ndarray:
    vals = []
    trans = np.asarray(model.transmat_, float)
    for i in range(1, len(posts)):
        prior = posts[i - 1] @ trans
        vals.append(float(logsumexp(np.log(np.maximum(prior, 1e-300)) + loge[i])))
    return np.asarray(vals, float)


def score_sequence_with_transition(fit, train: pd.DataFrame, future: pd.DataFrame):
    scaler = fit["scaler"]
    pca = fit["pca"]
    model = fit["model"]

    z_train = scaler.transform(train[FEATURES].to_numpy(float))
    z_future = scaler.transform(future[FEATURES].to_numpy(float))
    x_train = fit["x_train"]
    x_future = pca.transform(z_future)
    x_all = np.vstack([x_train, x_future])
    z_all = np.vstack([z_train, z_future])

    posts, loge = base.forward_filter(model, x_all)
    ntrain = len(train)
    hard_train = posts[:ntrain].argmax(axis=1)
    train_pred_scores = training_predictive_scores(model, posts[:ntrain], loge[:ntrain])
    pred_q10 = float(np.quantile(train_pred_scores, 0.10))

    train_jump = np.sqrt(np.sum(np.diff(z_train, axis=0) ** 2, axis=1))
    jump_q90 = float(np.quantile(train_jump, 0.90))

    out = []
    trans = np.asarray(model.transmat_, float)

    for j, month in enumerate(future.index):
        i = ntrain + j
        prev_i = i - 1

        incumbent = int(np.argmax(posts[prev_i]))
        prev_inc_prob = float(posts[prev_i, incumbent])
        cur_inc_prob = float(posts[i, incumbent])
        posterior_drop = float(prev_inc_prob - cur_inc_prob)

        current_best = int(np.argmax(posts[i]))
        current_best_prob = float(posts[i, current_best])

        prior = posts[prev_i] @ trans
        current_pred_score = float(logsumexp(np.log(np.maximum(prior, 1e-300)) + loge[i]))

        inc_pool = loge[:ntrain, incumbent][hard_train == incumbent]
        if len(inc_pool) >= 8:
            inc_q10 = float(np.quantile(inc_pool, 0.10))
            inc_pct = empirical_percentile(inc_pool, float(loge[i, incumbent]))
            s2 = bool(float(loge[i, incumbent]) <= inc_q10)
            s2_available = True
        else:
            inc_q10 = None
            inc_pct = None
            s2 = False
            s2_available = False

        pred_pct = empirical_percentile(train_pred_scores, current_pred_score)
        cur_jump = float(np.sqrt(np.sum((z_all[i] - z_all[prev_i]) ** 2)))
        jump_pct = empirical_percentile(train_jump, cur_jump)

        s1 = bool(cur_inc_prob < 0.70 or posterior_drop >= 0.20)
        s3 = bool(current_pred_score <= pred_q10)
        s4 = bool(cur_jump >= jump_q90)
        s5 = bool(current_best != incumbent and current_best_prob >= CONFIDENCE)

        vote_count = int(s1) + int(s2) + int(s3) + int(s4)
        transition = bool(s5 or vote_count >= 2)

        proto_id = int(fit["prototype_mapping"][current_best])
        proto_state = f"R{proto_id}"
        semantic_label = proto_state if current_best_prob >= CONFIDENCE else "BELIRSIZ"

        active = []
        for name, flag in [("S1_POSTERIOR_EROSION", s1), ("S2_INCUMBENT_EMISSION_ANOMALY", s2),
                           ("S3_PREDICTIVE_SURPRISE", s3), ("S4_MARKET_STATE_JUMP", s4),
                           ("S5_CONFIDENT_LATENT_SWITCH", s5)]:
            if flag:
                active.append(name)

        out.append({
            "month": str(month),
            "semantic_state": proto_state,
            "semantic_label": semantic_label,
            "semantic_probability": current_best_prob,
            "transition_status": "TRANSITION" if transition else "STABLE",
            "transition_flag": transition,
            "active_signals": active,
            "vote_count_s1_s4": vote_count,
            "S1_posterior_erosion": s1,
            "S2_incumbent_emission_anomaly": s2,
            "S2_available": s2_available,
            "S3_predictive_surprise": s3,
            "S4_market_state_jump": s4,
            "S5_confident_latent_switch": s5,
            "incumbent_raw_state": incumbent,
            "current_best_raw_state": current_best,
            "incumbent_previous_probability": prev_inc_prob,
            "incumbent_current_probability": cur_inc_prob,
            "incumbent_posterior_drop": posterior_drop,
            "current_best_probability": current_best_prob,
            "incumbent_emission_logdensity": float(loge[i, incumbent]),
            "incumbent_emission_train_q10": inc_q10,
            "incumbent_emission_empirical_percentile": inc_pct,
            "predictive_log_score": current_pred_score,
            "predictive_log_score_train_q10": pred_q10,
            "predictive_log_score_empirical_percentile": pred_pct,
            "market_state_jump_norm": cur_jump,
            "market_state_jump_train_q90": jump_q90,
            "market_state_jump_empirical_percentile": jump_pct,
            "train_start": fit["train_start"],
            "train_end": fit["train_end"],
            "train_rows": fit["train_rows"],
            "hmm_seed": fit["seed"],
            "prototype_assignment": fit["prototype_detail"]["assignment"],
        })

    return out


def expanding_rows(panel: pd.DataFrame, months: list[str], proto):
    rows = []
    for month in months:
        train = panel.loc[panel.index < month].copy()
        cur = panel.loc[[month]].copy()
        fit = palign.fit_frozen(train, proto)
        row = score_sequence_with_transition(fit, train, cur)[0]
        row["detector"] = "EXPANDING_REFIT"
        rows.append(row)
    return rows


def annual_rows(panel: pd.DataFrame, months: list[str], proto):
    by_year = {}
    for m in months:
        by_year.setdefault(int(m[:4]), []).append(m)

    rows = []
    for year in sorted(by_year):
        if year == 2015:
            anchor_end = "2015-06"
            future_start = "2015-07"
        else:
            anchor_end = f"{year-1}-12"
            future_start = f"{year}-01"

        train = panel.loc[panel.index <= anchor_end].copy()
        year_months = [m for m in panel.index if future_start <= m <= min(f"{year}-12", END)]
        future = panel.loc[year_months].copy()
        fit = palign.fit_frozen(train, proto)
        scored = score_sequence_with_transition(fit, train, future)
        wanted = set(by_year[year])
        for row in scored:
            if row["month"] in wanted:
                row["detector"] = "ANNUAL_ANCHORED"
                row["anchor_end"] = anchor_end
                rows.append(row)

    rows.sort(key=lambda r: r["month"])
    return rows


def attach_reference(rows, ref):
    out = []
    for r in rows:
        rr = ref.loc[r["month"]]
        ref_prob = float(rr["state_probability"])
        ref_state = str(rr["state"])
        ref_label = ref_state if ref_prob >= CONFIDENCE else "BELIRSIZ"
        z = dict(r)
        z.update({
            "reference_state": ref_state,
            "reference_probability": ref_prob,
            "reference_label": ref_label,
            "reference_ood": bool(rr["ood_below_train_p05"]),
        })
        out.append(z)
    return out


def build_reference_events(ref_monthly: pd.DataFrame):
    rows = []
    for _, rr in ref_monthly.iterrows():
        prob = float(rr["state_probability"])
        label = str(rr["state"]) if prob >= CONFIDENCE else "BELIRSIZ"
        rows.append({"month": str(rr["month"]), "label": label})

    events = []
    last_conf_state = None
    last_conf_month = None
    for r in rows:
        if r["label"] not in R_STATES:
            continue
        if last_conf_state is None:
            last_conf_state = r["label"]
            last_conf_month = r["month"]
            continue
        if r["label"] != last_conf_state:
            zone_start = next_month(last_conf_month)
            confirmation = r["month"]
            zone_months = [str(p) for p in pd.period_range(zone_start, confirmation, freq="M")]
            events.append({
                "old_state": last_conf_state,
                "new_state": r["label"],
                "last_confident_old_month": last_conf_month,
                "zone_start": zone_start,
                "confirmation_month": confirmation,
                "zone_months": zone_months,
            })
            last_conf_state = r["label"]
        last_conf_month = r["month"]

    return events


def period_metrics(rows, events, start, end=END):
    rr = [r for r in rows if start <= r["month"] <= end]
    months = {r["month"] for r in rr}

    period_events = [
        e for e in events
        if start <= e["confirmation_month"] <= end
    ]
    zone = set()
    for e in period_events:
        zone.update(m for m in e["zone_months"] if m in months)

    flags = [r for r in rr if r["transition_flag"]]
    zone_rows = [r for r in rr if r["month"] in zone]
    stable_rows = [r for r in rr if r["month"] not in zone]

    tp = sum(r["transition_flag"] for r in zone_rows)
    fp = sum(r["transition_flag"] for r in stable_rows)

    event_details = []
    hits = 0
    for e in period_events:
        in_zone = [r for r in rr if r["month"] in set(e["zone_months"])]
        flagged = [r for r in in_zone if r["transition_flag"]]
        first = flagged[0]["month"] if flagged else None
        if first is not None:
            hits += 1
        event_details.append({
            **e,
            "first_detector_flag_in_zone": first,
            "first_flag_relative_to_confirmation_months": None if first is None else month_diff(e["confirmation_month"], first),
            "hit": bool(first is not None),
        })

    return {
        "n_months": len(rr),
        "transition_flags": len(flags),
        "flag_rate": None if not rr else float(len(flags) / len(rr)),
        "transition_zone_months": len(zone_rows),
        "transition_zone_hits": int(tp),
        "transition_zone_recall": None if not zone_rows else float(tp / len(zone_rows)),
        "non_zone_months": len(stable_rows),
        "false_transition_count": int(fp),
        "false_transition_rate_non_zone": None if not stable_rows else float(fp / len(stable_rows)),
        "precision": None if not flags else float(tp / len(flags)),
        "reference_transition_events": len(period_events),
        "event_hits": int(hits),
        "event_misses": int(len(period_events) - hits),
        "event_hit_rate": None if not period_events else float(hits / len(period_events)),
        "event_details": event_details,
    }


def verify_against_prior(rows, prior_rows, detector):
    prior = {r["month"]: r for r in prior_rows}
    problems = []
    max_prob = 0.0
    max_score = 0.0

    for r in rows:
        p = prior.get(r["month"])
        if p is None:
            problems.append({"month": r["month"], "issue": "missing_prior"})
            continue
        dp = abs(float(r["semantic_probability"]) - float(p["probability"]))
        ds = abs(float(r["predictive_log_score"]) - float(p["predictive_log_score"]))
        max_prob = max(max_prob, dp)
        max_score = max(max_score, ds)
        if dp > 1e-6 or ds > 1e-6 or r["semantic_state"] != p["prototype_state"] or r["semantic_label"] != p["prototype_label"]:
            problems.append({
                "month": r["month"],
                "probability_abs_diff": dp,
                "predictive_log_score_abs_diff": ds,
                "new_state": r["semantic_state"],
                "prior_state": p["prototype_state"],
                "new_label": r["semantic_label"],
                "prior_label": p["prototype_label"],
            })

    return {
        "detector": detector,
        "pass": len(problems) == 0,
        "n_months": len(rows),
        "max_probability_abs_diff": max_prob,
        "max_predictive_log_score_abs_diff": max_score,
        "problems": problems,
    }


def checkpoint_table(expanding, annual):
    months = [
        "2024-03", "2024-04", "2024-05", "2024-06",
        "2026-04", "2026-05", "2026-06", "2026-07", "2026-08",
    ]
    out = []
    for m in months:
        row = {"month": m}
        for name, rows in [("EXPANDING_REFIT", expanding), ("ANNUAL_ANCHORED", annual)]:
            r = next((x for x in rows if x["month"] == m), None)
            if r is None:
                continue
            row[name] = {
                "semantic_label": r["semantic_label"],
                "semantic_state": r["semantic_state"],
                "semantic_probability": r["semantic_probability"],
                "transition_status": r["transition_status"],
                "active_signals": r["active_signals"],
                "vote_count_s1_s4": r["vote_count_s1_s4"],
                "incumbent_previous_probability": r["incumbent_previous_probability"],
                "incumbent_current_probability": r["incumbent_current_probability"],
                "incumbent_posterior_drop": r["incumbent_posterior_drop"],
                "incumbent_emission_percentile": r["incumbent_emission_empirical_percentile"],
                "predictive_score_percentile": r["predictive_log_score_empirical_percentile"],
                "market_state_jump_percentile": r["market_state_jump_empirical_percentile"],
                "latent_switch": r["S5_confident_latent_switch"],
            }
            row["reference"] = {
                "state": r["reference_state"],
                "label": r["reference_label"],
                "probability": r["reference_probability"],
            }
        out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regime-discovery-json", required=True)
    ap.add_argument("--prototype-alignment-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src = load_json(args.regime_discovery_json)
    prior = load_json(args.prototype_alignment_json)

    if src.get("status") != "COMPLETE" or src.get("evidence", {}).get("selected_hmm_k") != 3:
        raise RuntimeError("INVALID_DISCOVERY_REFERENCE")
    if prior.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_PROTOTYPE_ALIGNMENT_REFERENCE")

    raw = pd.DataFrame(src["monthly_regimes"]).sort_values("month").reset_index(drop=True)
    missing = [c for c in FEATURES if c not in raw.columns]
    if missing:
        raise RuntimeError(("MISSING_FEATURES", missing))

    proto = palign.build_frozen_prototypes(raw)
    panel = raw[["month"] + FEATURES].copy().set_index("month")
    ref = raw[["month", "state", "state_probability", "ood_below_train_p05"]].copy().set_index("month")
    eval_months = [m for m in panel.index if EVAL_START <= m <= END]

    expanding = attach_reference(expanding_rows(panel, eval_months, proto), ref)
    annual = attach_reference(annual_rows(panel, eval_months, proto), ref)

    verify_exp = verify_against_prior(expanding, prior["rows"]["EXPANDING_REFIT"], "EXPANDING_REFIT")
    verify_ann = verify_against_prior(annual, prior["rows"]["ANNUAL_ANCHORED"], "ANNUAL_ANCHORED")
    if not verify_exp["pass"] or not verify_ann["pass"]:
        raise RuntimeError(("UNDERLYING_REGIME_REPRODUCTION_FAILED", verify_exp, verify_ann))

    events = build_reference_events(raw[["month", "state", "state_probability"]])

    periods = {
        "full_replay_2015_07_2026_08": EVAL_START,
        "core_2022_01_2026_08": CORE_START,
        "transport_2025_01_2026_08": TRANSPORT_START,
    }
    metrics = {}
    for pname, start in periods.items():
        metrics[pname] = {
            "EXPANDING_REFIT": period_metrics(expanding, events, start),
            "ANNUAL_ANCHORED": period_metrics(annual, events, start),
        }

    result = {
        "schema": "GOLD_MONTHLY_MARKET_REGIME_TRANSITION_DETECTOR_V1_2026-09-30",
        "status": "COMPLETE",
        "scientific_gate": "PASS",
        "rule": {
            "S1": "incumbent posterior <0.70 OR posterior drop >=0.20",
            "S2": "incumbent emission logdensity <= training incumbent-state q10; minimum pool 8",
            "S3": "one-step predictive log score <= training sequential predictive-score q10",
            "S4": "13D standardized month-to-month jump >= training q90",
            "S5": "best raw latent state switched AND best posterior >=0.60",
            "transition": "S5 OR at least 2 of S1..S4",
        },
        "reference_event_definition": {
            "confidence_threshold": CONFIDENCE,
            "belirsiz_bridge": True,
            "zone_start": "month immediately after last confident old-state month",
            "zone_end": "first confident new-state month inclusive",
        },
        "underlying_regime_reproduction": {
            "EXPANDING_REFIT": verify_exp,
            "ANNUAL_ANCHORED": verify_ann,
        },
        "metrics": metrics,
        "reference_events": events,
        "key_checkpoints": checkpoint_table(expanding, annual),
        "rows": {
            "EXPANDING_REFIT": expanding,
            "ANNUAL_ANCHORED": annual,
        },
        "governance": {
            "market_state_features_only": True,
            "forecast_error_used": False,
            "forecast_used": False,
            "alarm_labels_used": False,
            "high_medium_normal_used": False,
            "future_target_information_used": False,
            "reference_labels_used_in_detector": False,
            "reference_labels_used_evaluation_only": True,
            "alarm_selection_tested": False,
            "alarm_weighting_tested": False,
            "forecast_correction_tested": False,
            "routing_tested": False,
            "thresholds_tuned_after_result": False,
            "2025_2026_claimed_untouched": False,
        },
    }

    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")

    def compact(m):
        return {k: {kk: vv for kk, vv in v.items() if kk != "event_details"} for k, v in m.items()}

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "underlying_regime_reproduction": result["underlying_regime_reproduction"],
        "full": compact(metrics["full_replay_2015_07_2026_08"]),
        "core": compact(metrics["core_2022_01_2026_08"]),
        "transport": compact(metrics["transport_2025_01_2026_08"]),
        "core_event_details": {
            k: v["event_details"] for k, v in metrics["core_2022_01_2026_08"].items()
        },
        "transport_event_details": {
            k: v["event_details"] for k, v in metrics["transport_2025_01_2026_08"].items()
        },
        "key_checkpoints": result["key_checkpoints"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
