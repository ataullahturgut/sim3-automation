from __future__ import annotations

import json
import math
import os
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.metrics import (
    balanced_accuracy_score,
    brier_score_loss,
    log_loss,
    matthews_corrcoef,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v165diag_research/contracts/v165diag_failure_attribution_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v165diag_research"

PARENTS = [
    "GOLD_RIDGE",
    "SESSION_RM_RIDGE",
    "PRICE_DISCOVERY_HGB",
    "MACRO_CROSS_RIDGE",
    "FULL_HGB",
]

GOLD = [
    "gold_ret_lag1", "gold_ret_lag2", "gold_ret_lag3", "gold_mom3", "gold_mom5",
    "gold_mom10", "gold_mom20", "gold_rv5", "gold_rv10", "gold_rv20",
]
SESSION_RM = [
    "europe_session_ret", "us_morning_ret", "post_0829_ret",
    "rm_vol", "rm_rsv_neg", "rm_rsv_pos", "rm_downside_share",
    "rm_skew", "rm_kurt", "rm_jump_fraction", "rm_max_abs",
]
PRICE_DISCOVERY = [
    "gc_ret1", "gc_ret3", "gc_ret5", "gc_range1", "gc_oc1", "gc_vol5", "gc_vol20", "gc_volume_z20", "gc_basis_prev",
    "gld_ret1", "gld_ret3", "gld_ret5", "gld_range1", "gld_oc1", "gld_vol5", "gld_vol20", "gld_volume_z20",
]
MACRO_CROSS = [
    "nasdaq_ret", "sp500_ret", "xag_ret", "xpt_ret", "xpd_ret",
    "broad_usd_level", "broad_usd_logdiff1", "broad_usd_logdiff5",
    "real10_level", "real10_delta1", "real10_delta5",
]
ROLE_CONTEXT = ["fast_state_encoded", "slow_state_encoded", "monthly_direction_3m_encoded"]
FEATURES = {
    "GOLD_RIDGE": GOLD,
    "SESSION_RM_RIDGE": SESSION_RM,
    "PRICE_DISCOVERY_HGB": PRICE_DISCOVERY,
    "MACRO_CROSS_RIDGE": MACRO_CROSS,
    "FULL_HGB": GOLD + SESSION_RM + PRICE_DISCOVERY + MACRO_CROSS + ROLE_CONTEXT,
}


def load_contract() -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_ANY_V165DIAG_SCORING":
        raise RuntimeError("V165DIAG_CONTRACT_NOT_FROZEN")
    e = c["evaluation_lock"]
    forbidden = [
        "model_refitting_in_v165diag", "recalibration_in_v165diag", "drift_detector_scoring_in_v165diag",
        "triggered_adaptation_in_v165diag", "selector_scoring_in_v165diag", "abstention_tuning_in_v165diag",
        "post_score_threshold_or_feature_search",
    ]
    if any(e[k] != "FORBIDDEN" for k in forbidden):
        raise RuntimeError("V165DIAG_EVALUATION_LOCK_FAIL")
    g = c["governance"]
    if g["AUTO_SELECTOR"] != "OFF" or g["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V165DIAG_GOVERNANCE_LOCK_FAIL")
    return c


def artifact_dir(contract: dict) -> Path:
    raw = os.environ.get("V164_ARTIFACT_DIR", "").strip()
    if not raw:
        raise SystemExit("BLOCKED_DATA:V164_ARTIFACT_DIR_REQUIRED")
    p = Path(raw)
    missing = [name for name in contract["source_artifact"]["required_files"] if not (p / name).exists()]
    if missing:
        raise RuntimeError(f"V165DIAG_SOURCE_ARTIFACT_FILES_MISSING:{missing}")
    return p


def prediction_path(art: Path, horizon: int, parent: str) -> Path:
    return art / f"v164_{horizon}d_{parent.lower()}_predictions.csv"


def period_slice(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    od = pd.to_datetime(df["origin_date"])
    td = pd.to_datetime(df["target_date"])
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return df[(od >= a) & (od <= b) & (td <= b)].copy()


def brier_decomposition(y: np.ndarray, p: np.ndarray, bins: int) -> dict:
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1], right=False), 0, bins - 1)
    ybar = float(np.mean(y))
    n = len(y)
    reliability = 0.0
    resolution = 0.0
    ece = 0.0
    used = 0
    for k in range(bins):
        mask = idx == k
        nk = int(mask.sum())
        if nk == 0:
            continue
        pk = float(np.mean(p[mask]))
        yk = float(np.mean(y[mask]))
        w = nk / n
        reliability += w * (pk - yk) ** 2
        resolution += w * (yk - ybar) ** 2
        ece += w * abs(pk - yk)
        used += 1
    return {
        "ece": float(ece),
        "murphy_reliability": float(reliability),
        "murphy_resolution": float(resolution),
        "murphy_uncertainty": float(ybar * (1.0 - ybar)),
        "bins_used": int(used),
    }


def moving_block_mean_ci(x: np.ndarray, block_length: int, replicates: int, seed: int) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n == 0:
        raise ValueError("EMPTY_BOOTSTRAP_INPUT")
    if n == 1:
        return float(x[0]), float(x[0])
    b = min(int(block_length), n)
    max_start = n - b
    rng = np.random.default_rng(int(seed))
    means = np.empty(int(replicates), dtype=float)
    for r in range(int(replicates)):
        chunks: list[np.ndarray] = []
        total = 0
        while total < n:
            start = int(rng.integers(0, max_start + 1)) if max_start > 0 else 0
            chunk = x[start:start + b]
            chunks.append(chunk)
            total += len(chunk)
        means[r] = float(np.mean(np.concatenate(chunks)[:n]))
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def performance_metrics(df: pd.DataFrame, horizon: int, key: str, contract: dict) -> dict:
    y = df["y"].to_numpy(dtype=int)
    p = np.clip(df["STATIC"].to_numpy(dtype=float), 1e-9, 1 - 1e-9)
    fq = np.clip(df["FREQ"].to_numpy(dtype=float), 1e-9, 1 - 1e-9)
    pred = (p >= 0.5).astype(int)
    model_brier = float(brier_score_loss(y, p))
    frequency_brier = float(brier_score_loss(y, fq))
    excess = np.square(y - p) - np.square(y - fq)

    cfg = contract["audit_modules"]["performance_and_uncertainty"]
    seed = int(cfg["bootstrap_seed"]) + zlib.crc32(key.encode("utf-8")) % 1_000_000
    ci_lo, ci_hi = moving_block_mean_ci(
        excess,
        block_length=max(5, int(horizon)),
        replicates=int(cfg["block_bootstrap_replicates"]),
        seed=seed,
    )
    auc = float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None
    ba = float(balanced_accuracy_score(y, pred)) if len(np.unique(y)) == 2 else None
    mcc = float(matthews_corrcoef(y, pred)) if len(np.unique(y)) == 2 and len(np.unique(pred)) == 2 else 0.0
    out = {
        "n": int(len(df)),
        "brier": model_brier,
        "frequency_brier": frequency_brier,
        "p50_brier": float(np.mean(np.square(y - 0.5))),
        "brier_skill_vs_frequency": float(1.0 - model_brier / frequency_brier) if frequency_brier > 0 else None,
        "mean_excess_brier": float(np.mean(excess)),
        "excess_brier_ci95": [ci_lo, ci_hi],
        "robust_benchmark_skill": bool(float(np.mean(excess)) < 0.0 and ci_hi < 0.0),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "balanced_accuracy": ba,
        "mcc": mcc,
        "roc_auc": auc,
        "up_predictions": int(pred.sum()),
        "down_predictions": int((1 - pred).sum()),
        "actual_up": int(y.sum()),
        "actual_down": int((1 - y).sum()),
    }
    bins = int(contract["audit_modules"]["calibration_discrimination"]["fixed_probability_bins"])
    out.update(brier_decomposition(y, p, bins))

    cal = contract["audit_modules"]["calibration_discrimination"]
    auc_min = float(cal["discrimination_signal_auc_min"])
    ece_min = float(cal["material_ece_min"])
    bss = out["brier_skill_vs_frequency"]
    out["calibration_problem_plausible"] = bool(
        auc is not None and auc >= auc_min and bss is not None and bss <= 0.0 and out["ece"] >= ece_min
    )
    out["discrimination_problem_plausible"] = bool(
        auc is not None and auc < auc_min and bss is not None and bss <= 0.0
    )
    out["estimation_uncertainty_material"] = bool(ci_lo <= 0.0 <= ci_hi)
    return out


def standardized_mean_difference(a: pd.Series, b: pd.Series) -> float | None:
    aa = pd.to_numeric(a, errors="coerce").to_numpy(dtype=float)
    bb = pd.to_numeric(b, errors="coerce").to_numpy(dtype=float)
    aa = aa[np.isfinite(aa)]
    bb = bb[np.isfinite(bb)]
    if len(aa) < 2 or len(bb) < 2:
        return None
    denom = math.sqrt((float(np.var(aa, ddof=1)) + float(np.var(bb, ddof=1))) / 2.0)
    diff = float(np.mean(bb) - np.mean(aa))
    if denom < 1e-12:
        if abs(diff) < 1e-12:
            return 0.0
        return 10.0 if diff > 0 else -10.0
    return float(diff / denom)


def covariate_shift(panel: pd.DataFrame, pred: pd.DataFrame, features: list[str], contract: dict) -> tuple[dict, list[dict]]:
    indexed = panel.reset_index().rename(columns={"index": "origin_index"})
    origins = pred[["origin_index", "origin_date"]].drop_duplicates("origin_index")
    z = origins.merge(indexed[["origin_index"] + features], on="origin_index", how="left", validate="one_to_one")
    od = pd.to_datetime(z["origin_date"])
    d25 = z[(od >= pd.Timestamp("2025-01-01")) & (od <= pd.Timestamp("2025-12-31"))]
    d26 = z[(od >= pd.Timestamp("2026-01-01")) & (od <= pd.Timestamp("2026-06-30"))]

    rows: list[dict] = []
    for feature in features:
        a = pd.to_numeric(d25[feature], errors="coerce")
        b = pd.to_numeric(d26[feature], errors="coerce")
        af = a[np.isfinite(a)]
        bf = b[np.isfinite(b)]
        ks_stat = None
        ks_pvalue = None
        if len(af) >= 2 and len(bf) >= 2:
            ks = ks_2samp(af, bf, method="auto")
            ks_stat = float(ks.statistic)
            ks_pvalue = float(ks.pvalue)
        smd = standardized_mean_difference(af, bf)
        rows.append({
            "feature": feature,
            "n_2025": int(len(af)),
            "n_2026": int(len(bf)),
            "mean_2025": float(af.mean()) if len(af) else None,
            "mean_2026": float(bf.mean()) if len(bf) else None,
            "smd_2026_minus_2025": smd,
            "abs_smd": abs(smd) if smd is not None else None,
            "ks_statistic": ks_stat,
            "ks_pvalue": ks_pvalue,
            "missing_rate_2025": float(a.isna().mean()),
            "missing_rate_2026": float(b.isna().mean()),
            "missing_rate_difference": float(b.isna().mean() - a.isna().mean()),
        })

    valid = [r["abs_smd"] for r in rows if r["abs_smd"] is not None]
    cfg = contract["audit_modules"]["covariate_and_target_shift"]
    agg = {
        "feature_count": int(len(rows)),
        "median_abs_smd": float(np.median(valid)) if valid else None,
        "max_abs_smd": float(np.max(valid)) if valid else None,
        "share_abs_smd_ge_0_5": float(np.mean(np.asarray(valid) >= float(cfg["moderate_abs_smd"]))) if valid else None,
        "share_abs_smd_ge_1_0": float(np.mean(np.asarray(valid) >= float(cfg["large_abs_smd"]))) if valid else None,
    }
    agg["covariate_shift_material"] = bool(
        (agg["median_abs_smd"] is not None and agg["median_abs_smd"] >= float(cfg["material_median_abs_smd"]))
        or (
            agg["share_abs_smd_ge_0_5"] is not None
            and agg["share_abs_smd_ge_0_5"] >= float(cfg["material_feature_share_abs_smd_ge_0_5"])
        )
    )
    return agg, rows


def target_shift(pred: pd.DataFrame, contract: dict) -> dict:
    periods = contract["periods"]
    d25 = period_slice(pred, *periods["VALIDATION_2025"])
    d26 = period_slice(pred, *periods["TEST_2026_AVAILABLE"])
    up25 = float(d25["y"].mean())
    up26 = float(d26["y"].mean())
    diff = float(up26 - up25)
    threshold = float(contract["audit_modules"]["covariate_and_target_shift"]["material_target_up_rate_difference"])
    return {
        "n_2025": int(len(d25)),
        "n_2026": int(len(d26)),
        "up_rate_2025": up25,
        "up_rate_2026": up26,
        "difference_2026_minus_2025": diff,
        "target_base_rate_shift_material": bool(abs(diff) >= threshold),
    }


def build_state_labels(panel: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    p = panel.copy()
    dates = pd.to_datetime(p["date"])
    formation = p[(dates >= pd.Timestamp("2024-01-01")) & (dates <= pd.Timestamp("2024-12-31"))]
    q = pd.to_numeric(formation["gold_rv20"], errors="coerce").dropna().quantile([1 / 3, 2 / 3]).to_numpy(dtype=float)
    if len(q) != 2 or not np.all(np.isfinite(q)):
        raise RuntimeError("V165DIAG_STATE_THRESHOLD_SUPPORT_FAIL")
    lo, hi = float(q[0]), float(q[1])
    out = pd.DataFrame(index=p.index)
    out["gold_rv20_state"] = pd.cut(
        pd.to_numeric(p["gold_rv20"], errors="coerce"),
        [-np.inf, lo, hi, np.inf],
        labels=["LOW", "MID", "HIGH"],
        include_lowest=True,
    ).astype(object)
    out["gold_mom20_state"] = np.where(pd.to_numeric(p["gold_mom20"], errors="coerce") < 0, "DOWN", "UP")
    out["broad_usd_logdiff5_state"] = np.where(pd.to_numeric(p["broad_usd_logdiff5"], errors="coerce") < 0, "DOWN", "UP")
    out["real10_delta5_state"] = np.where(pd.to_numeric(p["real10_delta5"], errors="coerce") < 0, "DOWN", "UP")
    role_map = {-1.0: "DOWN", 0.0: "NEUTRAL", 1.0: "UP"}
    for col in ["fast_state_encoded", "slow_state_encoded", "monthly_direction_3m_encoded"]:
        out[f"{col}_state"] = pd.to_numeric(p[col], errors="coerce").map(role_map).fillna("MISSING")
    return out, {"gold_rv20_q33_2024": lo, "gold_rv20_q67_2024": hi}


def state_skill_audit(panel: pd.DataFrame, pred: pd.DataFrame, contract: dict) -> tuple[dict, list[dict]]:
    states, thresholds = build_state_labels(panel)
    joined = pred.merge(
        states.reset_index().rename(columns={"index": "origin_index"}),
        on="origin_index",
        how="left",
        validate="many_to_one",
    )
    cfg = contract["audit_modules"]["state_dependent_skill"]
    min_n = int(cfg["minimum_state_support_each_period"])
    detail: list[dict] = []
    for state_feature in states.columns:
        values = sorted(joined.loc[joined[state_feature].notna(), state_feature].astype(str).unique())
        for state in values:
            row = {"state_feature": state_feature, "state": state, "periods": {}}
            comparable = True
            for period_name, (start, end) in contract["periods"].items():
                g = period_slice(joined[joined[state_feature].astype(str) == state], start, end)
                if len(g) < min_n:
                    comparable = False
                    row["periods"][period_name] = {"n": int(len(g)), "brier_skill_vs_frequency": None}
                    continue
                y = g["y"].to_numpy(dtype=float)
                p = g["STATIC"].to_numpy(dtype=float)
                fq = g["FREQ"].to_numpy(dtype=float)
                brier = float(np.mean(np.square(y - p)))
                fb = float(np.mean(np.square(y - fq)))
                row["periods"][period_name] = {
                    "n": int(len(g)),
                    "brier_skill_vs_frequency": float(1.0 - brier / fb) if fb > 0 else None,
                }
            row["comparable"] = bool(comparable)
            if comparable:
                a = row["periods"]["VALIDATION_2025"]["brier_skill_vs_frequency"]
                b = row["periods"]["TEST_2026_AVAILABLE"]["brier_skill_vs_frequency"]
                row["skill_sign_flip"] = bool(a is not None and b is not None and a * b < 0.0)
                row["abs_skill_change"] = abs(float(b - a)) if a is not None and b is not None else None
            else:
                row["skill_sign_flip"] = False
                row["abs_skill_change"] = None
            detail.append(row)

    comparable_rows = [r for r in detail if r["comparable"]]
    flips = int(sum(bool(r["skill_sign_flip"]) for r in comparable_rows))
    share = float(flips / len(comparable_rows)) if comparable_rows else 0.0
    return {
        "state_thresholds": thresholds,
        "comparable_states": int(len(comparable_rows)),
        "skill_sign_flips": flips,
        "sign_flip_share": share,
        "state_dependent_instability": bool(
            len(comparable_rows) > 0 and share >= float(cfg["material_sign_flip_share"])
        ),
        "mean_abs_skill_change": float(np.mean([r["abs_skill_change"] for r in comparable_rows])) if comparable_rows else None,
    }, detail


def oracle_headroom(predictions: dict[str, pd.DataFrame], contract: dict) -> dict:
    out: dict = {}
    threshold = float(contract["audit_modules"]["oracle_headroom"]["material_oracle_headroom_brier"])
    for period_name, (start, end) in contract["periods"].items():
        frames: list[pd.DataFrame] = []
        for parent in PARENTS:
            g = period_slice(predictions[parent], start, end)[["origin_index", "y", "FREQ", "STATIC"]].copy()
            g = g.rename(columns={"STATIC": parent})
            frames.append(g)
        merged = frames[0]
        for frame in frames[1:]:
            merged = merged.merge(frame[["origin_index", frame.columns[-1]]], on="origin_index", how="inner", validate="one_to_one")
        y = merged["y"].to_numpy(dtype=float)
        fq = merged["FREQ"].to_numpy(dtype=float)
        probs = merged[PARENTS].to_numpy(dtype=float)
        single = {parent: float(np.mean(np.square(y - merged[parent].to_numpy(dtype=float)))) for parent in PARENTS}
        best_parent = min(single, key=single.get)
        frequency_brier = float(np.mean(np.square(y - fq)))
        equal_brier = float(np.mean(np.square(y - np.mean(probs, axis=1))))
        oracle_brier = float(np.mean(np.min(np.square(y[:, None] - probs), axis=1)))
        corr = np.corrcoef(probs, rowvar=False)
        offdiag = corr[np.triu_indices_from(corr, k=1)]
        offdiag = offdiag[np.isfinite(offdiag)]
        headroom = float(frequency_brier - oracle_brier)
        out[period_name] = {
            "n": int(len(merged)),
            "frequency_brier": frequency_brier,
            "best_single_parent": best_parent,
            "best_single_brier": float(single[best_parent]),
            "equal_average_brier": equal_brier,
            "oracle_brier": oracle_brier,
            "oracle_headroom_vs_frequency": headroom,
            "oracle_headroom_material": bool(headroom >= threshold),
            "mean_pairwise_probability_correlation": float(np.mean(offdiag)) if len(offdiag) else None,
            "mean_cross_parent_probability_sd": float(np.mean(np.std(probs, axis=1))),
            "interpretation_lock": "RETROSPECTIVE_UNATTAINABLE_UPPER_BOUND_NOT_A_SELECTOR",
        }
    return out


def flatten_outputs(results: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    perf_rows: list[dict] = []
    cov_rows: list[dict] = []
    state_rows: list[dict] = []
    oracle_rows: list[dict] = []
    for horizon_name, hres in results["horizons"].items():
        for parent, pres in hres["parents"].items():
            for period, metrics in pres["periods"].items():
                perf_rows.append({"horizon": horizon_name, "parent": parent, "period": period, **metrics})
            for row in pres["covariate_shift_detail"]:
                cov_rows.append({"horizon": horizon_name, "parent": parent, **row})
            for row in pres["state_dependent_skill_detail"]:
                r = {"horizon": horizon_name, "parent": parent, "state_feature": row["state_feature"], "state": row["state"], "comparable": row["comparable"], "skill_sign_flip": row["skill_sign_flip"], "abs_skill_change": row["abs_skill_change"]}
                for period, values in row["periods"].items():
                    r[f"{period}_n"] = values["n"]
                    r[f"{period}_brier_skill"] = values["brier_skill_vs_frequency"]
                state_rows.append(r)
        for period, values in hres["oracle_headroom"].items():
            oracle_rows.append({"horizon": horizon_name, "period": period, **values})
    return pd.DataFrame(perf_rows), pd.DataFrame(cov_rows), pd.DataFrame(state_rows), pd.DataFrame(oracle_rows)


def main() -> int:
    contract = load_contract()
    art = artifact_dir(contract)
    panel = pd.read_csv(art / "v164_panel.csv")
    panel["date"] = pd.to_datetime(panel["date"])

    results = {
        "contract_id": contract["contract_id"],
        "evidence_class": contract["evidence_class"],
        "source_artifact": contract["source_artifact"],
        "horizons": {},
        "governance": {
            "model_refitting_performed": False,
            "recalibration_performed": False,
            "drift_detector_scoring_performed": False,
            "triggered_adaptation_performed": False,
            "selector_scoring_performed": False,
            "abstention_tuning_performed": False,
            "production_writes": "NONE",
            "prospective_claim": False,
        },
    }

    for horizon in [int(x) for x in contract["horizons"]]:
        predictions = {parent: pd.read_csv(prediction_path(art, horizon, parent)) for parent in PARENTS}
        hres = {
            "target_shift": target_shift(predictions[PARENTS[0]], contract),
            "oracle_headroom": oracle_headroom(predictions, contract),
            "parents": {},
            "horizon_labels": [],
        }
        if hres["target_shift"]["target_base_rate_shift_material"]:
            hres["horizon_labels"].append("TARGET_BASE_RATE_SHIFT_MATERIAL")

        for parent in PARENTS:
            pred = predictions[parent]
            pres = {"periods": {}, "supported_labels": []}
            for period_name, (start, end) in contract["periods"].items():
                g = period_slice(pred, start, end)
                if g.empty:
                    raise RuntimeError(f"V165DIAG_EMPTY_PERIOD:{horizon}:{parent}:{period_name}")
                pres["periods"][period_name] = performance_metrics(
                    g, horizon, f"{horizon}:{parent}:{period_name}", contract
                )

            cov_agg, cov_detail = covariate_shift(panel, pred, FEATURES[parent], contract)
            state_agg, state_detail = state_skill_audit(panel, pred, contract)
            pres["covariate_shift_2025_to_2026"] = cov_agg
            pres["covariate_shift_detail"] = cov_detail
            pres["state_dependent_skill"] = state_agg
            pres["state_dependent_skill_detail"] = state_detail

            if all(pres["periods"][p]["robust_benchmark_skill"] for p in contract["periods"]):
                pres["supported_labels"].append("ROBUST_BENCHMARK_SKILL_BOTH_PERIODS")
            if any(pres["periods"][p]["calibration_problem_plausible"] for p in contract["periods"]):
                pres["supported_labels"].append("CALIBRATION_PROBLEM_PLAUSIBLE")
            if any(pres["periods"][p]["discrimination_problem_plausible"] for p in contract["periods"]):
                pres["supported_labels"].append("DISCRIMINATION_PROBLEM_PLAUSIBLE")
            if cov_agg["covariate_shift_material"]:
                pres["supported_labels"].append("COVARIATE_SHIFT_MATERIAL")
            if state_agg["state_dependent_instability"]:
                pres["supported_labels"].append("STATE_DEPENDENT_INSTABILITY")
            if any(pres["periods"][p]["estimation_uncertainty_material"] for p in contract["periods"]):
                pres["supported_labels"].append("ESTIMATION_UNCERTAINTY_MATERIAL")
            hres["parents"][parent] = pres

        robust = [p for p, x in hres["parents"].items() if "ROBUST_BENCHMARK_SKILL_BOTH_PERIODS" in x["supported_labels"]]
        calibration = [p for p, x in hres["parents"].items() if "CALIBRATION_PROBLEM_PLAUSIBLE" in x["supported_labels"]]
        covariate = [p for p, x in hres["parents"].items() if "COVARIATE_SHIFT_MATERIAL" in x["supported_labels"]]
        state = [p for p, x in hres["parents"].items() if "STATE_DEPENDENT_INSTABILITY" in x["supported_labels"]]
        uncertainty = [p for p, x in hres["parents"].items() if "ESTIMATION_UNCERTAINTY_MATERIAL" in x["supported_labels"]]
        oracle_2026 = bool(hres["oracle_headroom"]["TEST_2026_AVAILABLE"]["oracle_headroom_material"])

        next_hypotheses: list[str] = []
        if not robust and not oracle_2026:
            next_hypotheses.append("SIGNAL_DISCOVERY_OR_HORIZON_REDESIGN_PRIORITY")
        if calibration:
            next_hypotheses.append("RECALIBRATION_RESEARCH_ELIGIBLE")
        if covariate and state:
            next_hypotheses.append("DRIFT_ADAPTATION_RESEARCH_ELIGIBLE")
        if oracle_2026 and state:
            next_hypotheses.append("STATE_DEPENDENT_SELECTION_OR_GATING_RESEARCH_ELIGIBLE")
        if len(uncertainty) >= 3:
            next_hypotheses.append("MORE_DATA_REQUIRED_FOR_STRONG_CAUSAL_ATTRIBUTION")

        hres["attribution_summary"] = {
            "robust_both_period_parents": robust,
            "calibration_problem_parents": calibration,
            "covariate_shift_parents": covariate,
            "state_instability_parents": state,
            "uncertainty_parents": uncertainty,
            "recommended_next_hypotheses": next_hypotheses,
            "no_single_forced_cause": True,
        }
        results["horizons"][f"{horizon}D"] = hres

    OUT.mkdir(parents=True, exist_ok=True)
    perf, cov, state, oracle = flatten_outputs(results)
    perf.to_csv(OUT / "v165diag_performance_calibration.csv", index=False)
    cov.to_csv(OUT / "v165diag_covariate_shift.csv", index=False)
    state.to_csv(OUT / "v165diag_state_dependent_skill.csv", index=False)
    oracle.to_csv(OUT / "v165diag_oracle_headroom.csv", index=False)
    (OUT / "v165diag_failure_attribution_results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
