from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, log_loss, matthews_corrcoef, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v166_research/contracts/v166_3d_mechanism_isolation_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v166_research"


def load_contract() -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_ANY_V166_SCORING":
        raise RuntimeError("V166_CONTRACT_NOT_FROZEN")
    d = c["decision_lock"]
    forbidden = [
        "gated_residual_correction_in_v166",
        "drift_detector_in_v166",
        "selector_scoring_in_v166",
        "abstention_tuning_in_v166",
    ]
    if any(d[k] != "FORBIDDEN" for k in forbidden):
        raise RuntimeError("V166_MECHANISM_ISOLATION_LOCK_FAIL")
    if not c["evaluation"]["no_post_score_parameter_search"]:
        raise RuntimeError("V166_POST_SCORE_SEARCH_MUST_BE_FORBIDDEN")
    g = c["governance"]
    if g["AUTO_SELECTOR"] != "OFF" or g["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V166_GOVERNANCE_LOCK_FAIL")
    if c["horizon"] != 3:
        raise RuntimeError("V166_HORIZON_MUST_BE_3D")
    return c


def artifact_dir() -> Path:
    raw = os.environ.get("V164_ARTIFACT_DIR", "").strip()
    if not raw:
        raise SystemExit("BLOCKED_DATA:V164_ARTIFACT_DIR_REQUIRED")
    p = Path(raw)
    if not p.exists():
        raise RuntimeError("V166_ARTIFACT_DIR_NOT_FOUND")
    return p


def prediction_path(art: Path, parent: str) -> Path:
    return art / f"v164_3d_{parent.lower()}_predictions.csv"


def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(np.asarray(p, dtype=float), 1e-9, 1 - 1e-9)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    z = np.asarray(x, dtype=float)
    z = np.clip(z, -35.0, 35.0)
    out = 1.0 / (1.0 + np.exp(-z))
    return float(out) if out.ndim == 0 else out


def fit_constrained_recalibration(p: np.ndarray, y: np.ndarray, lam: float) -> tuple[float, float, bool]:
    p = np.asarray(p, dtype=float)
    y = np.asarray(y, dtype=float)
    x = logit(p)
    if len(y) == 0 or len(np.unique(y.astype(int))) < 2:
        return 0.0, 1.0, False

    def objective(v: np.ndarray) -> float:
        a = float(v[0])
        theta = float(v[1])
        b = math.exp(float(np.clip(theta, -4.0, 4.0)))
        q = np.clip(sigmoid(a + b * x), 1e-9, 1 - 1e-9)
        nll = -float(np.sum(y * np.log(q) + (1.0 - y) * np.log(1.0 - q)))
        penalty = float(lam) * (a * a + theta * theta)
        return nll + penalty

    res = minimize(objective, x0=np.asarray([0.0, 0.0]), method="L-BFGS-B", bounds=[(-5.0, 5.0), (-4.0, 4.0)])
    if not res.success or not np.all(np.isfinite(res.x)):
        return 0.0, 1.0, False
    a = float(res.x[0])
    b = math.exp(float(res.x[1]))
    return a, b, True


def causal_recalibrate(df: pd.DataFrame, contract: dict) -> pd.DataFrame:
    cfg = contract["recalibration"]
    h = int(contract["horizon"])
    min_n = int(cfg["minimum_mature_forecasts"])
    cap = int(cfg["maximum_mature_forecasts"])
    lam = float(cfg["identity_shrink_lambda"])
    lo, hi = [float(x) for x in cfg["probability_clip"]]

    z = df.sort_values("origin_index").reset_index(drop=True).copy()
    recal = []
    a_values = []
    b_values = []
    support = []
    fitted = []

    for i, row in z.iterrows():
        t = int(row["origin_index"])
        hist = z.iloc[:i]
        hist = hist[(hist["origin_index"].astype(int) + h) <= t]
        if len(hist) > cap:
            hist = hist.iloc[-cap:]
        n = int(len(hist))
        p0 = float(np.clip(row["STATIC"], lo, hi))
        if n < min_n or hist["y"].nunique() < 2:
            recal.append(p0)
            a_values.append(0.0)
            b_values.append(1.0)
            support.append(n)
            fitted.append(False)
            continue
        a, b, ok = fit_constrained_recalibration(hist["STATIC"].to_numpy(float), hist["y"].to_numpy(int), lam)
        p = float(np.clip(sigmoid(a + b * float(logit(np.asarray([p0]))[0])), lo, hi)) if ok else p0
        recal.append(p)
        a_values.append(a if ok else 0.0)
        b_values.append(b if ok else 1.0)
        support.append(n)
        fitted.append(bool(ok))

    z["RECAL_ONLY"] = recal
    z["recal_intercept"] = a_values
    z["recal_slope"] = b_values
    z["recal_support_n"] = support
    z["recal_fitted"] = fitted
    z["FORGET_ONLY"] = z["FORGET"].astype(float)
    return z


def period_slice(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    od = pd.to_datetime(df["origin_date"])
    td = pd.to_datetime(df["target_date"])
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return df[(od >= a) & (od <= b) & (td <= b)].copy()


def metrics(df: pd.DataFrame, col: str) -> dict:
    z = df[["y", col]].dropna()
    if z.empty:
        return {"n": 0, "status": "EMPTY"}
    y = z["y"].to_numpy(dtype=int)
    p = np.clip(z[col].to_numpy(dtype=float), 1e-9, 1 - 1e-9)
    pred = (p >= 0.5).astype(int)
    auc = float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None
    ba = float(balanced_accuracy_score(y, pred)) if len(np.unique(y)) == 2 else None
    mcc = float(matthews_corrcoef(y, pred)) if len(np.unique(y)) == 2 and len(np.unique(pred)) == 2 else 0.0
    return {
        "n": int(len(z)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "roc_auc": auc,
        "balanced_accuracy": ba,
        "mcc": mcc,
        "up_predictions": int(pred.sum()),
        "down_predictions": int((1 - pred).sum()),
        "actual_up": int(y.sum()),
        "actual_down": int((1 - y).sum()),
    }


def evaluate_periods(df: pd.DataFrame, contract: dict) -> dict:
    periods = {
        "VALIDATION_2025": contract["periods"]["validation_2025"],
        "TEST_2026_AVAILABLE": contract["periods"]["test_2026_available"],
    }
    out = {}
    for name, (start, end) in periods.items():
        g = period_slice(df, start, end)
        out[name] = {
            "FREQ": metrics(g, "FREQ"),
            "STATIC": metrics(g, "STATIC"),
            "RECAL_ONLY": metrics(g, "RECAL_ONLY"),
            "FORGET_ONLY": metrics(g, "FORGET_ONLY"),
            "recalibration_diagnostics": {
                "rows": int(len(g)),
                "fitted_share": float(g["recal_fitted"].mean()) if len(g) else None,
                "median_support_n": float(g["recal_support_n"].median()) if len(g) else None,
                "median_intercept": float(g.loc[g["recal_fitted"], "recal_intercept"].median()) if g["recal_fitted"].any() else None,
                "median_slope": float(g.loc[g["recal_fitted"], "recal_slope"].median()) if g["recal_fitted"].any() else None,
            },
        }
    return out


def gate_variant(periods: dict, variant: str, contract: dict) -> dict:
    v = periods["VALIDATION_2025"][variant]
    t = periods["TEST_2026_AVAILABLE"][variant]
    sv = periods["VALIDATION_2025"]["STATIC"]
    st = periods["TEST_2026_AVAILABLE"]["STATIC"]
    fv = periods["VALIDATION_2025"]["FREQ"]
    ft = periods["TEST_2026_AVAILABLE"]["FREQ"]
    cfg = contract["evaluation"]["mechanism_success_gate_per_parent"]
    checks = {
        "validation_brier_not_worse_than_static": v["brier"] <= sv["brier"],
        "test_brier_not_worse_than_static": t["brier"] <= st["brier"],
        "validation_log_loss_not_worse_than_static": v["log_loss"] <= sv["log_loss"],
        "test_log_loss_not_worse_than_static": t["log_loss"] <= st["log_loss"],
        "test_brier_improvement_vs_static_min": (st["brier"] - t["brier"]) >= float(cfg["test_brier_improvement_vs_static_min"]),
        "validation_brier_not_worse_than_frequency": v["brier"] <= fv["brier"],
        "test_brier_not_worse_than_frequency": t["brier"] <= ft["brier"],
        "test_roc_auc_min": (t.get("roc_auc") or 0.0) >= float(cfg["test_roc_auc_min"]),
        "both_predicted_directions_in_test": t.get("up_predictions", 0) > 0 and t.get("down_predictions", 0) > 0,
    }
    return {
        "checks": checks,
        "test_brier_improvement_vs_static": float(st["brier"] - t["brier"]),
        "pass": bool(all(checks.values())),
    }


def main() -> int:
    contract = load_contract()
    art = artifact_dir()
    OUT.mkdir(parents=True, exist_ok=True)
    required = set(contract["source_artifact"]["required_prediction_columns"])

    result = {
        "contract_id": contract["contract_id"],
        "evidence_class": contract["evidence_class"],
        "horizon": 3,
        "parents": {},
        "mechanism_family_pass": {"RECAL_ONLY": False, "FORGET_ONLY": False},
        "governance": {"AUTO_SELECTOR": "OFF", "AUTO_ENSEMBLE": "OFF", "production_authority": False, "production_writes": "NONE"},
    }

    for parent in contract["parents"]:
        path = prediction_path(art, parent)
        if not path.exists():
            raise RuntimeError(f"V166_SOURCE_PREDICTION_MISSING:{path.name}")
        raw = pd.read_csv(path)
        missing = sorted(required - set(raw.columns))
        if missing:
            raise RuntimeError(f"V166_SOURCE_COLUMNS_MISSING:{parent}:{missing}")
        if raw["horizon"].nunique() != 1 or int(raw["horizon"].iloc[0]) != 3:
            raise RuntimeError(f"V166_NON_3D_SOURCE:{parent}")
        z = causal_recalibrate(raw, contract)
        z.to_csv(OUT / f"v166_3d_{parent.lower()}_predictions.csv", index=False)
        periods = evaluate_periods(z, contract)
        gates = {
            "RECAL_ONLY": gate_variant(periods, "RECAL_ONLY", contract),
            "FORGET_ONLY": gate_variant(periods, "FORGET_ONLY", contract),
        }
        for mechanism, gate in gates.items():
            result["mechanism_family_pass"][mechanism] = bool(result["mechanism_family_pass"][mechanism] or gate["pass"])
        result["parents"][parent] = {"rows": int(len(z)), "period_metrics": periods, "success_gate": gates}

    if result["mechanism_family_pass"]["RECAL_ONLY"] and result["mechanism_family_pass"]["FORGET_ONLY"]:
        decision = "BOTH_MECHANISMS_HAVE_AT_LEAST_ONE_PASS_OPEN_NEW_FROZEN_COMPARISON"
    elif result["mechanism_family_pass"]["RECAL_ONLY"]:
        decision = "RECALIBRATION_PROMISING_OPEN_SEPARATE_GATED_CALIBRATION_STUDY"
    elif result["mechanism_family_pass"]["FORGET_ONLY"]:
        decision = "RECENCY_FORGETTING_PROMISING_OPEN_SEPARATE_ROBUSTNESS_STUDY"
    else:
        decision = "NEITHER_MECHANISM_PASSES_STOP_ADAPTATION_ESCALATION_RETURN_TO_SIGNAL_OR_NEW_HYPOTHESIS"
    result["frozen_decision"] = decision
    result["scientific_interpretation_lock"] = {
        "gated_residual_correction_performed": False,
        "drift_detector_scored": False,
        "selector_scored": False,
        "abstention_tuned": False,
        "post_score_parameter_search_performed": False,
        "2025_2026_are_researcher_visible": True,
        "prospective_claim": False,
    }

    (OUT / "v166_3d_mechanism_isolation_results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
