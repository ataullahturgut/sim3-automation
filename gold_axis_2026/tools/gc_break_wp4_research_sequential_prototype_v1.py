from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
if str(R4_SRC) not in sys.path:
    sys.path.insert(0, str(R4_SRC))

from gold_r4.emergency import EmergencyState  # noqa: E402
from gold_r4.tactical import completed_weekly_closes, fast_state, slow_state  # noqa: E402

CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_wp4_research_sequential_prototype_contract_v1.json"
EVENT_CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_event_contract_v1.json"

# Frozen research-only monthly references already used in the 2024 replay family.
# They are NOT canonical historical NY17 inputs and must not be promoted to production authority.
MONTHLY_REF = {
    "2024-01": 2022.6484770325865,
    "2024-02": 2092.2926047779174,
    "2024-03": 1997.7506094668854,
    "2024-04": 2143.5740800480094,
    "2024-05": 2371.114230713846,
    "2024-06": 2390.5707089022567,
    "2024-07": 2335.9130338349873,
    "2024-08": 2461.1324656594306,
}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-z))


def fit_balanced_ridge_logit(X: np.ndarray, y: np.ndarray, lam: float = 1.0):
    n = len(y)
    n1 = int(y.sum())
    n0 = n - n1
    if n1 < 5 or n0 < 5:
        raise RuntimeError(f"INSUFFICIENT_CLASS_SUPPORT:POS={n1}:NEG={n0}")
    w1 = n / (2.0 * n1)
    w0 = n / (2.0 * n0)
    sw = np.where(y == 1, w1, w0)

    def objective(theta: np.ndarray):
        b = theta[0]
        beta = theta[1:]
        p = sigmoid(b + X @ beta)
        eps = 1e-12
        nll = -np.sum(sw * (y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps)))
        penalty = 0.5 * lam * float(beta @ beta)
        return nll + penalty

    res = minimize(objective, np.zeros(X.shape[1] + 1), method="L-BFGS-B")
    if not res.success:
        raise RuntimeError(f"LOGIT_OPTIMIZATION_FAIL:{res.message}")
    return float(res.x[0]), res.x[1:].astype(float), {"positive_weight": w1, "negative_weight": w0}


def auc_rank(y: np.ndarray, p: np.ndarray):
    y = np.asarray(y, int)
    p = np.asarray(p, float)
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return None
    ranks = pd.Series(p).rank(method="average").to_numpy()
    s = float(ranks[y == 1].sum())
    return (s - n1 * (n1 + 1) / 2.0) / (n1 * n0)


def average_precision(y: np.ndarray, p: np.ndarray):
    order = np.argsort(-p)
    yy = y[order]
    total = int(yy.sum())
    if total == 0:
        return None
    hits = 0
    vals = []
    for i, v in enumerate(yy, start=1):
        if v == 1:
            hits += 1
            vals.append(hits / i)
    return float(np.mean(vals))


def same_robust(state: str, regime: str | None) -> bool:
    return (regime == "UP" and state == "ROBUST_UP") or (regime == "DOWN" and state == "ROBUST_DOWN")


def opposite_robust(state: str, regime: str | None) -> bool:
    return (regime == "UP" and state == "ROBUST_DOWN") or (regime == "DOWN" and state == "ROBUST_UP")


def build_role_panel(daily: pd.DataFrame) -> pd.DataFrame:
    em = EmergencyState()
    rows = []
    for i, row in daily.iterrows():
        d = pd.Timestamp(row["date"])
        c = float(row["close"])
        fs = fast_state(daily.loc[:i, "close"].tolist()).value
        wc = completed_weekly_closes(daily.loc[:i, ["date", "close"]], d)
        ss = slow_state(wc).value
        mk = d.strftime("%Y-%m")
        if mk in MONTHLY_REF:
            el, er = em.update(d, c, MONTHLY_REF[mk])
            elv = el.value
            erv = er.value
        else:
            elv = "NOT_AVAILABLE"
            erv = "OFF"
        rows.append({"date": d, "close": c, "fast_state": fs, "slow_state": ss,
                     "emergency_level": elv, "emergency_reversal": erv})
    return pd.DataFrame(rows)


def predictive_episode_metrics(pred: pd.DataFrame, daily_dates: list[pd.Timestamp], break_dates: set[pd.Timestamp], signal_col: str):
    positions = {d: i for i, d in enumerate(daily_dates)}
    x = pred[["date", signal_col]].copy().reset_index(drop=True)
    flags = x[signal_col].astype(bool).to_numpy()
    episodes = []
    start = None
    for i, flag in enumerate(flags):
        if flag and start is None:
            start = i
        if start is not None and ((not flag) or i == len(flags) - 1):
            end = i - 1 if not flag else i
            sd = pd.Timestamp(x.loc[start, "date"])
            ed = pd.Timestamp(x.loc[end, "date"])
            pidx = positions[ed]
            nxt = daily_dates[pidx + 1] if pidx + 1 < len(daily_dates) else pd.NaT
            converted = nxt in break_dates
            episodes.append({
                "start_date": sd,
                "end_date": ed,
                "converted": converted,
                "break_date": nxt if converted else None,
                "lead_observations": (positions[nxt] - positions[sd]) if converted else None,
            })
            start = None
    conv = [e for e in episodes if e["converted"]]
    false = [e for e in episodes if not e["converted"]]
    detected = {e["break_date"] for e in conv}
    leads = [e["lead_observations"] for e in conv]
    return {
        "episodes": len(episodes),
        "converted_episodes": len(conv),
        "false_episodes": len(false),
        "episode_conversion_rate": len(conv) / len(episodes) if episodes else None,
        "event_recall": len(detected) / len(break_dates) if break_dates else None,
        "false_episodes_per_100_origins": len(false) * 100.0 / len(pred) if len(pred) else None,
        "median_lead_observations": float(np.median(leads)) if leads else None,
        "mean_lead_observations": float(np.mean(leads)) if leads else None,
        "episodes_detail": episodes,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--daily-csv", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("status") != "RESEARCH_ONLY_EXPLORATORY_NOT_CANONICAL":
        raise RuntimeError("RESEARCH_PROTOTYPE_CONTRACT_STATUS_CHANGED")
    if contract["governance"]["no_database_writes"] is not True:
        raise RuntimeError("NO_DATABASE_WRITE_GUARD_FAIL")

    daily = pd.read_csv(args.daily_csv)
    daily["date"] = pd.to_datetime(daily["date"]).dt.normalize()
    daily["close"] = pd.to_numeric(daily["close"], errors="raise")
    daily = daily.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    if (daily["close"] <= 0).any():
        raise RuntimeError("INVALID_CLOSE")

    panel = build_role_panel(daily)
    diag = load_module(ROOT / "tools" / "gc_break_v0_governed_diagnostic_v1.py", "gc_break_wp4_research_diag")
    event_contract = json.loads(EVENT_CONTRACT_PATH.read_text(encoding="utf-8"))
    events, origins = diag.build_break_inventory(panel[["date", "close"]], event_contract)
    p = panel.merge(origins, on="date", how="left", validate="one_to_one")

    valid = p["regime_pre"].isin(["UP", "DOWN"])
    p["adverse_fraction_clipped_0_1"] = p["adverse_fraction"].clip(0, 1).fillna(0.0)
    p["fast_conflict"] = valid & ~pd.Series([same_robust(s, r) for s, r in zip(p["fast_state"], p["regime_pre"])])
    p["slow_conflict"] = valid & ~pd.Series([same_robust(s, r) for s, r in zip(p["slow_state"], p["regime_pre"])])
    p["emergency_reversal_opposite"] = (
        ((p["regime_pre"] == "UP") & (p["emergency_reversal"] == "DOWN_ALERT")) |
        ((p["regime_pre"] == "DOWN") & (p["emergency_reversal"] == "UP_ALERT"))
    )
    p["is_break"] = p["event_id"].notna()
    p["next_date"] = p["date"].shift(-1)
    break_dates_all = set(pd.to_datetime(events["break_date"])) if len(events) else set()
    p["y_next_break"] = p["next_date"].isin(break_dates_all).astype(int)

    model = p[~p["is_break"]].copy()
    feats = ["adverse_fraction_clipped_0_1", "fast_conflict", "slow_conflict", "emergency_reversal_opposite"]
    for c in feats[1:]:
        model[c] = model[c].astype(int)

    train = model[(model["date"] >= "2024-01-02") & (model["next_date"] <= "2024-05-31")].copy()
    test = model[(model["date"] >= "2024-06-03") & (model["next_date"] <= "2024-08-30")].copy()
    Xtr = train[feats].to_numpy(float)
    ytr = train["y_next_break"].to_numpy(int)
    Xte = test[feats].to_numpy(float)
    yte = test["y_next_break"].to_numpy(int)

    intercept, beta, class_weights = fit_balanced_ridge_logit(Xtr, ytr, lam=1.0)
    ptr = sigmoid(intercept + Xtr @ beta)
    pte = sigmoid(intercept + Xte @ beta)
    threshold = float(np.quantile(ptr, 0.75))

    test["hazard_next_observation"] = pte
    test["weakening"] = test["hazard_next_observation"] >= threshold
    states = []
    consecutive = 0
    for flag in test["weakening"].astype(bool):
        if flag:
            consecutive += 1
            states.append("BREAK_ALERT" if consecutive >= 2 else "WEAKENING")
        else:
            consecutive = 0
            states.append("STABLE")
    test["sequential_state"] = states
    test["break_alert"] = test["sequential_state"].eq("BREAK_ALERT")

    test_break_dates = set(pd.to_datetime(events.loc[(events["break_date"] >= "2024-06-01") & (events["break_date"] <= "2024-08-31"), "break_date"]))
    daily_dates = list(panel["date"])
    weakening_metrics = predictive_episode_metrics(test, daily_dates, test_break_dates, "weakening")
    alert_metrics = predictive_episode_metrics(test, daily_dates, test_break_dates, "break_alert")

    summary = {
        "audit_id": "GC_BREAK_WP4_RESEARCH_SEQUENTIAL_PROTOTYPE_V1",
        "contract_status": contract["status"],
        "source_evidence_class": contract["source"]["evidence_class"],
        "canonical_validation_required": True,
        "train_origins": int(len(train)),
        "train_break_targets": int(ytr.sum()),
        "test_origins": int(len(test)),
        "test_break_targets": int(yte.sum()),
        "test_break_dates": [d.date().isoformat() for d in sorted(test_break_dates)],
        "features": feats,
        "feature_nonzero_support_train": {c: int(train[c].astype(bool).sum()) for c in feats[1:]},
        "model": {
            "intercept": intercept,
            "coefficients": {c: float(v) for c, v in zip(feats, beta)},
            "class_weights": class_weights,
            "weakening_threshold_training_q75": threshold,
        },
        "proper_and_ranking_scores": {
            "train_auc": auc_rank(ytr, ptr),
            "train_average_precision": average_precision(ytr, ptr),
            "train_brier": float(np.mean((ptr - ytr) ** 2)),
            "test_auc": auc_rank(yte, pte),
            "test_average_precision": average_precision(yte, pte),
            "test_brier": float(np.mean((pte - yte) ** 2)),
        },
        "sequential_metrics": {
            "WEAKENING_OR_HIGHER": weakening_metrics,
            "BREAK_ALERT": alert_metrics,
        },
        "governance": {
            "production_authority": False,
            "prospective_claim": False,
            "database_write": "NONE",
            "post_test_threshold_tuning": False,
            "interpretation": "EXPLORATORY RESEARCH ONLY. Small-sample result; must be re-frozen and rerun on canonical exact-NY17 before scientific promotion."
        },
    }

    test.to_csv(args.output_dir / "gc_break_wp4_research_sequential_predictions_v1.csv", index=False)
    (args.output_dir / "gc_break_wp4_research_sequential_summary_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
