from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from regime_v1_data import Daily, load_external, load_governed, rsk_value
from regime_v1_router_sqrt import nearest_rank

IDENTITY = "HIGH_RISK_HURDLE_RESOLUTION_V1_RESEARCH"
OUT = Path("high_risk_hurdle_out")
EPS = 1e-12
FEATURES = [
    "log_dr_d_q80",
    "log_dr_w_q80",
    "log_dr_m_q80",
    "log_rv_d_q80",
    "rsk_d",
    "origin_return_1d",
    "recent20_high_share",
]
CLASS_ORDER = ["HIT_DOWN", "HIT_UP", "MISS"]
EXPECTED_ALARMS = {2020: 212, 2021: 28, 2022: 11, 2023: 2, 2024: 17}
EXPECTED_CLASSES = {"HIT_DOWN": 115, "HIT_UP": 103, "MISS": 52}


def base_rows(days: list[Daily]) -> list[dict]:
    dr = np.array([x.dr for x in days], dtype=float)
    rv = np.array([x.rv for x in days], dtype=float)
    close = np.array([x.close for x in days], dtype=float)
    out = []
    for i in range(21, len(days) - 1):
        t = i + 1
        ret1 = math.log(close[i] / close[i - 1])
        target_ret = math.log(close[t] / close[i])
        out.append({
            "origin_index": i,
            "origin_date": days[i].d.isoformat(),
            "target_date": days[t].d.isoformat(),
            "dr_d": float(dr[i]),
            "dr_w": float(np.mean(dr[i - 4:i + 1])),
            "dr_m": float(np.mean(dr[i - 21:i + 1])),
            "rv_d": float(rv[i]),
            "rsk_d": float(rsk_value(days[i])),
            "origin_return_1d": float(ret1),
            "target_dr": float(dr[t]),
            "target_return": float(target_ret),
        })
    return out


def fit_parent_and_build(days: list[Daily], year: int) -> tuple[list[dict], list[dict], dict]:
    rows = base_rows(days)
    cutoff = date(year - 1, 12, 31)
    formation = [r for r in rows if date.fromisoformat(r["target_date"]) <= cutoff]
    test = [r for r in rows if date.fromisoformat(r["target_date"]).year == year]
    if len(formation) < 250:
        raise RuntimeError(f"FORMATION_TOO_SHORT:{year}:{len(formation)}")

    q80 = nearest_rank(np.array([r["target_dr"] for r in formation], dtype=float), 0.80)

    # Frozen parent fit, identical SQRT-HAR-DR annual semantics.
    # IMPORTANT: frozen parent uses mean(sqrt(DR)) for weekly/monthly
    # SQRT-HAR features, not sqrt(mean(DR)). Keep this numerically identical
    # to regime_v1_router_sqrt.sqrt_rows.
    dr_all = np.array([x.dr for x in days], dtype=float)
    sd_all = np.sqrt(dr_all)
    parent_feature_by_target = {}
    for i in range(21, len(days) - 1):
        td = days[i + 1].d.isoformat()
        parent_feature_by_target[td] = (
            float(sd_all[i]),
            float(np.mean(sd_all[i - 4:i + 1])),
            float(np.mean(sd_all[i - 21:i + 1])),
        )

    Xp = np.array([
        [1.0, *parent_feature_by_target[r["target_date"]]]
        for r in formation
    ], dtype=float)
    yp = np.array([math.sqrt(max(r["target_dr"], 0.0)) for r in formation], dtype=float)
    beta = np.linalg.lstsq(Xp, yp, rcond=None)[0]

    def enrich(r: dict, is_test: bool) -> dict:
        rr = dict(r)
        i = int(rr["origin_index"])
        hist = days[max(0, i - 19): i + 1]
        high_share = sum(int(x.dr >= q80) for x in hist) / len(hist)
        rr.update({
            "evaluation_year": year,
            "q80": float(q80),
            "log_dr_d_q80": float(math.log((rr["dr_d"] + EPS) / (q80 + EPS))),
            "log_dr_w_q80": float(math.log((rr["dr_w"] + EPS) / (q80 + EPS))),
            "log_dr_m_q80": float(math.log((rr["dr_m"] + EPS) / (q80 + EPS))),
            "log_rv_d_q80": float(math.log((rr["rv_d"] + EPS) / (q80 + EPS))),
            "recent20_high_share": float(high_share),
        })
        hit = int(rr["target_dr"] >= q80)
        if rr["target_return"] == 0:
            rr["outcome_class"] = "FLAT"
        elif hit and rr["target_return"] < 0:
            rr["outcome_class"] = "HIT_DOWN"
        elif hit and rr["target_return"] > 0:
            rr["outcome_class"] = "HIT_UP"
        else:
            rr["outcome_class"] = "MISS"
        rr["risk_hit"] = hit
        rr["down_given_hit"] = int(rr["target_return"] < 0) if hit else None

        if is_test:
            sd_d, sd_w, sd_m = parent_feature_by_target[rr["target_date"]]
            xn = np.array([1.0, sd_d, sd_w, sd_m], dtype=float)
            sp = float(xn @ beta)
            if not math.isfinite(sp) or sp <= 0:
                raise RuntimeError(f"PARENT_NONPOSITIVE:{year}:{rr['target_date']}:{sp}")
            fp = sp * sp
            rr["sqrt_forecast"] = fp
            rr["sqrt_normalized_risk_score"] = fp / q80
            rr["sqrt_alarm"] = int(fp >= q80)
        return rr

    form_e = [enrich(r, False) for r in formation]
    test_e = [enrich(r, True) for r in test]

    meta = {
        "formation_n": len(form_e),
        "test_n": len(test_e),
        "q80": float(q80),
        "formation_class_counts": dict(Counter(r["outcome_class"] for r in form_e)),
        "formation_risk_hit_n": sum(r["risk_hit"] for r in form_e),
    }
    return form_e, test_e, meta


def fit_hurdle(formation: list[dict]) -> dict:
    X = np.array([[float(r[f]) for f in FEATURES] for r in formation], dtype=float)
    if not np.all(np.isfinite(X)):
        raise RuntimeError("NONFINITE_FORMATION_FEATURE")

    mu = X.mean(axis=0)
    sd = X.std(axis=0, ddof=0)
    sd = np.where(sd <= 1e-12, 1.0, sd)
    Z = (X - mu) / sd

    y_hit = np.array([int(r["risk_hit"]) for r in formation], dtype=int)
    if len(np.unique(y_hit)) < 2:
        raise RuntimeError("DEGENERATE_STAGE_A")

    stage_a = LogisticRegression(
        penalty="l2",
        C=1.0,
        solver="lbfgs",
        max_iter=2000,
        class_weight=None,
        random_state=None,
    )
    stage_a.fit(Z, y_hit)

    idx_hit = np.where(y_hit == 1)[0]
    y_down = np.array([
        int(formation[j]["down_given_hit"])
        for j in idx_hit
    ], dtype=int)
    if len(np.unique(y_down)) < 2:
        raise RuntimeError("DEGENERATE_STAGE_B")

    stage_b = LogisticRegression(
        penalty="l2",
        C=1.0,
        solver="lbfgs",
        max_iter=2000,
        class_weight=None,
        random_state=None,
    )
    stage_b.fit(Z[idx_hit], y_down)

    return {
        "mu": mu,
        "sd": sd,
        "stage_a": stage_a,
        "stage_b": stage_b,
        "stage_a_n": len(y_hit),
        "stage_a_positive": int(y_hit.sum()),
        "stage_b_n": len(y_down),
        "stage_b_down": int(y_down.sum()),
    }


def prob_for_rows(model: dict, rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    X = np.array([[float(r[f]) for f in FEATURES] for r in rows], dtype=float)
    Z = (X - model["mu"]) / model["sd"]

    p_hit = model["stage_a"].predict_proba(Z)[:, list(model["stage_a"].classes_).index(1)]
    p_down = model["stage_b"].predict_proba(Z)[:, list(model["stage_b"].classes_).index(1)]

    out = []
    for r, ph, pd in zip(rows, p_hit, p_down):
        probs = {
            "HIT_DOWN": float(ph * pd),
            "HIT_UP": float(ph * (1.0 - pd)),
            "MISS": float(1.0 - ph),
        }
        s = sum(probs.values())
        if abs(s - 1.0) > 1e-10:
            raise RuntimeError(f"PROB_SUM:{r['target_date']}:{s}")
        argmax = max(CLASS_ORDER, key=lambda k: probs[k])
        pmax = probs[argmax]
        emitted = argmax if pmax > 0.50 else "UNCERTAIN"

        rr = dict(r)
        rr.update({
            "p_hit": float(ph),
            "p_down_given_hit": float(pd),
            "p_HIT_DOWN": probs["HIT_DOWN"],
            "p_HIT_UP": probs["HIT_UP"],
            "p_MISS": probs["MISS"],
            "argmax_class": argmax,
            "max_joint_probability": float(pmax),
            "emitted_class": emitted,
        })
        out.append(rr)
    return out


def multiclass_metrics(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        return {"n": 0}

    observed = Counter(r["outcome_class"] for r in rows)
    emitted = Counter(r["emitted_class"] for r in rows)
    accepted = [r for r in rows if r["emitted_class"] != "UNCERTAIN"]
    acc_sel = (
        sum(r["emitted_class"] == r["outcome_class"] for r in accepted) / len(accepted)
        if accepted else None
    )
    acc_argmax = sum(r["argmax_class"] == r["outcome_class"] for r in rows) / n

    per_class = {}
    for cls in CLASS_ORDER:
        pred_n = sum(r["emitted_class"] == cls for r in rows)
        true_n = sum(r["outcome_class"] == cls for r in rows)
        tp = sum(
            r["emitted_class"] == cls and r["outcome_class"] == cls
            for r in rows
        )
        per_class[cls] = {
            "precision": tp / pred_n if pred_n else None,
            "recall": tp / true_n if true_n else None,
            "predicted_n": pred_n,
            "true_n": true_n,
            "tp": tp,
        }

    conf = {
        true_cls: {
            pred_cls: sum(
                r["outcome_class"] == true_cls and r["emitted_class"] == pred_cls
                for r in rows
            )
            for pred_cls in CLASS_ORDER + ["UNCERTAIN"]
        }
        for true_cls in CLASS_ORDER
    }

    brier_terms = []
    log_terms = []
    calibration = {}
    for r in rows:
        p = np.array([r[f"p_{c}"] for c in CLASS_ORDER], dtype=float)
        y = np.array([1.0 if r["outcome_class"] == c else 0.0 for c in CLASS_ORDER])
        brier_terms.append(float(np.sum((p - y) ** 2)))
        true_p = r[f"p_{r['outcome_class']}"]
        log_terms.append(-math.log(max(min(true_p, 1.0 - 1e-15), 1e-15)))

    for true_cls in CLASS_ORDER:
        sub = [r for r in rows if r["outcome_class"] == true_cls]
        calibration[true_cls] = {
            "n": len(sub),
            "mean_p_HIT_DOWN": (
                float(np.mean([r["p_HIT_DOWN"] for r in sub])) if sub else None
            ),
            "mean_p_HIT_UP": (
                float(np.mean([r["p_HIT_UP"] for r in sub])) if sub else None
            ),
            "mean_p_MISS": (
                float(np.mean([r["p_MISS"] for r in sub])) if sub else None
            ),
        }

    hit_rows = [r for r in rows if r["outcome_class"] in ("HIT_DOWN", "HIT_UP")]
    if hit_rows:
        ydir = np.array([int(r["outcome_class"] == "HIT_DOWN") for r in hit_rows])
        pdir = np.array([r["p_down_given_hit"] for r in hit_rows], dtype=float)
        dir_acc = float(np.mean((pdir >= 0.5) == ydir))
        dir_auc = (
            float(roc_auc_score(ydir, pdir))
            if len(np.unique(ydir)) == 2 else None
        )
    else:
        dir_acc = None
        dir_auc = None

    return {
        "n": n,
        "observed_counts": {c: observed[c] for c in CLASS_ORDER},
        "emitted_counts": {c: emitted[c] for c in CLASS_ORDER + ["UNCERTAIN"]},
        "coverage": len(accepted) / n,
        "selective_accuracy": acc_sel,
        "nonselective_argmax_accuracy": acc_argmax,
        "largest_observed_class_share": max(observed.values()) / n,
        "per_class": per_class,
        "confusion_with_abstain": conf,
        "multiclass_brier": float(np.mean(brier_terms)),
        "multiclass_log_loss": float(np.mean(log_terms)),
        "mean_max_joint_probability": float(np.mean([r["max_joint_probability"] for r in rows])),
        "calibration_by_observed_class": calibration,
        "direction_on_realized_hit": {
            "n": len(hit_rows),
            "auc_p_down_given_hit": dir_auc,
            "accuracy_at_0_5": dir_acc,
        },
    }


def write_ledger(path: Path, rows: list[dict]) -> None:
    fields = [
        "source_class", "evaluation_year", "origin_date", "target_date",
        "q80", "sqrt_forecast", "sqrt_normalized_risk_score",
        "target_dr", "target_return", "outcome_class",
        *FEATURES,
        "p_hit", "p_down_given_hit", "p_HIT_DOWN", "p_HIT_UP", "p_MISS",
        "argmax_class", "max_joint_probability", "emitted_class",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ext = load_external()
    gov = load_governed()

    all_scored = []
    by_year = {}
    fit_meta = {}
    integrity_errors = []

    for year in (2020, 2021, 2022, 2023, 2024):
        days = ext if year <= 2021 else gov
        source_class = "EXTERNAL_RESEARCH_V2" if year <= 2021 else "GOVERNED"
        formation, test, meta = fit_parent_and_build(days, year)

        if any(r["outcome_class"] == "FLAT" for r in formation):
            formation = [r for r in formation if r["outcome_class"] != "FLAT"]
        model = fit_hurdle(formation)

        alarms = [r for r in test if r["sqrt_alarm"]]
        if any(r["outcome_class"] == "FLAT" for r in alarms):
            integrity_errors.append(f"FLAT_ALARM_{year}")

        scored = prob_for_rows(model, alarms)
        for r in scored:
            r["source_class"] = source_class

        if len(scored) != EXPECTED_ALARMS[year]:
            integrity_errors.append(
                f"ALARM_COUNT_{year}:{len(scored)}!={EXPECTED_ALARMS[year]}"
            )

        fit_meta[str(year)] = {
            **meta,
            "stage_a_n": model["stage_a_n"],
            "stage_a_risk_hit_n": model["stage_a_positive"],
            "stage_b_n": model["stage_b_n"],
            "stage_b_down_n": model["stage_b_down"],
            "feature_mean": {
                f: float(v) for f, v in zip(FEATURES, model["mu"])
            },
            "feature_std": {
                f: float(v) for f, v in zip(FEATURES, model["sd"])
            },
        }
        by_year[str(year)] = multiclass_metrics(scored)
        all_scored.extend(scored)

    pooled_counts = Counter(r["outcome_class"] for r in all_scored)
    for cls, expected in EXPECTED_CLASSES.items():
        if pooled_counts[cls] != expected:
            integrity_errors.append(
                f"CLASS_{cls}:{pooled_counts[cls]}!={expected}"
            )
    if len(all_scored) != 270:
        integrity_errors.append(f"POOLED_N:{len(all_scored)}!=270")

    pooled = multiclass_metrics(all_scored)
    if integrity_errors:
        status = "BLOCKED_INTEGRITY_MISMATCH"
    elif pooled["coverage"] <= 0:
        status = "NO_SELECTIVE_SIGNAL"
    elif (
        pooled["selective_accuracy"] is None
        or pooled["selective_accuracy"] <= pooled["largest_observed_class_share"]
    ):
        status = "NO_SELECTIVE_SIGNAL"
    else:
        status = "SELECTIVE_SIGNAL_PRESENT_NOT_CERTIFIED"

    result = {
        "identity": IDENTITY,
        "date": "2026-09-22",
        "architecture": {
            "stage_a": "L2 logistic: realized high-risk hit vs miss",
            "stage_b": "L2 logistic: DOWN vs UP conditional on realized high-risk",
            "joint_classes": CLASS_ORDER,
            "selective_rule": "emit argmax only if max joint probability > 0.50, else UNCERTAIN",
            "features": FEATURES,
            "router_used": False,
        },
        "governance": {
            "random_split": False,
            "2025_used": False,
            "2026_used": False,
            "production_writes": False,
            "runtime_promotion": False,
            "external_2020_2021_authority": "RESEARCH_ONLY_SESSIONMASK_V2",
        },
        "integrity_errors": integrity_errors,
        "fit_meta": fit_meta,
        "by_year": by_year,
        "pooled_2020_2024": pooled,
        "status": status,
        "interpretation_limit": (
            "Architecture probe only. Historical retrospective evidence; no "
            "runtime or prospective certification."
        ),
    }

    write_ledger(
        OUT / "GOLD_CONTROL_HIGH_RISK_HURDLE_RESOLUTION_V1_LEDGER_2026-09-22.csv",
        all_scored,
    )
    with (
        OUT / "GOLD_CONTROL_HIGH_RISK_HURDLE_RESOLUTION_V1_RESULT_2026-09-22.json"
    ).open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    lines = [
        "# GOLD CONTROL — HIGH-RISK HURDLE RESOLUTION V1 RESULT",
        "",
        f"Status: {status}",
        "",
        f"Integrity errors: {integrity_errors if integrity_errors else 'none'}",
        "",
        "## Year-by-year",
        "",
        "| Year | n | HIT_DOWN | HIT_UP | MISS | coverage | selective acc | argmax acc | dir AUC on risk hits |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for year in (2020, 2021, 2022, 2023, 2024):
        m = by_year[str(year)]
        lines.append(
            f"| {year} | {m['n']} | {m['observed_counts']['HIT_DOWN']} | "
            f"{m['observed_counts']['HIT_UP']} | {m['observed_counts']['MISS']} | "
            f"{m['coverage']} | {m['selective_accuracy']} | "
            f"{m['nonselective_argmax_accuracy']} | "
            f"{m['direction_on_realized_hit']['auc_p_down_given_hit']} |"
        )

    lines += [
        "",
        "## Pooled 2020–2024",
        "",
        f"- N: {pooled['n']}",
        f"- Observed: {pooled['observed_counts']}",
        f"- Emitted: {pooled['emitted_counts']}",
        f"- Coverage: {pooled['coverage']}",
        f"- Selective accuracy: {pooled['selective_accuracy']}",
        f"- Non-selective argmax accuracy: {pooled['nonselective_argmax_accuracy']}",
        f"- Largest observed class share: {pooled['largest_observed_class_share']}",
        f"- Multiclass Brier: {pooled['multiclass_brier']}",
        f"- Multiclass log loss: {pooled['multiclass_log_loss']}",
        f"- Direction AUC on realized-risk-hit alarms: {pooled['direction_on_realized_hit']['auc_p_down_given_hit']}",
        f"- Direction accuracy @0.5 on realized-risk-hit alarms: {pooled['direction_on_realized_hit']['accuracy_at_0_5']}",
        "",
        "Router/context features are intentionally excluded from V1.",
    ]
    (
        OUT / "GOLD_CONTROL_HIGH_RISK_HURDLE_RESOLUTION_V1_RESULT_2026-09-22.md"
    ).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(status)
    print(json.dumps({
        "integrity_errors": integrity_errors,
        "pooled": pooled,
        "by_year": by_year,
    }, indent=2))


if __name__ == "__main__":
    main()
