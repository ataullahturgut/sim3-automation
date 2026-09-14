from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = ["ret_1", "ret_2", "ret_3", "mom_3", "mom_5", "mom_10", "rv_5", "rv_10", "rv_20"]
FINAL_STATUSES = {"VALID_EXACT_BAR", "PROVIDER_NO_BAR"}
TRAIN_START = pd.Timestamp("2022-01-01")
TRAIN_END = pd.Timestamp("2024-12-31")
CHALLENGE_START = pd.Timestamp("2025-01-01")
CHALLENGE_END = pd.Timestamp("2025-12-31")


def load_contract(path: Path) -> dict:
    c = json.loads(path.read_text(encoding="utf-8"))
    assert c["contract_id"] == "GOLD_RIDGE_RECONSTRUCTION_V1_2025"
    assert c["status"] == "FROZEN_BEFORE_2025_REPLAY"
    assert c["split"]["challenge_refit"] is False
    assert c["split"]["challenge_hyperparameter_search"] is False
    assert c["features"] == FEATURES
    return c


def load_exact(path: Path, require_challenge_lineage: bool) -> pd.DataFrame:
    d = pd.read_csv(path, dtype=str, keep_default_na=False)
    required = {"trade_date", "acquisition_status"}
    if not required <= set(d.columns):
        raise RuntimeError(f"EXACT_SCHEMA_FAIL:{path}")
    bad = sorted(set(d["acquisition_status"]) - FINAL_STATUSES)
    if bad:
        raise RuntimeError(f"UNRESOLVED_EXACT_STATUS:{path}:{bad[:5]}")
    valid = d[d["acquisition_status"].eq("VALID_EXACT_BAR")].copy()
    if valid.empty:
        raise RuntimeError(f"NO_VALID_EXACT_ROWS:{path}")
    if require_challenge_lineage:
        expected = {
            "provider": "Twelve Data",
            "symbol": "XAU/USD",
            "interval": "1min",
            "timezone": "America/New_York",
            "accepted_source_time": "16:59:00",
            "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
            "prospective_claim": "False",
        }
        for field, value in expected.items():
            if field not in valid.columns:
                raise RuntimeError(f"CHALLENGE_LINEAGE_COLUMN_MISSING:{field}")
            vals = set(valid[field])
            if vals != {value}:
                raise RuntimeError(f"CHALLENGE_LINEAGE_FAIL:{field}:{sorted(vals)}")
    valid["date"] = pd.to_datetime(valid["trade_date"], errors="raise").dt.normalize()
    valid["close"] = pd.to_numeric(valid["close"], errors="raise")
    if valid["date"].duplicated().any():
        raise RuntimeError(f"DUPLICATE_VALID_DATE:{path}")
    if (valid["close"] <= 0).any() or not np.isfinite(valid["close"].to_numpy(float)).all():
        raise RuntimeError(f"INVALID_CLOSE:{path}")
    return valid[["date", "close"]].sort_values("date").reset_index(drop=True)


def build_features(d: pd.DataFrame) -> pd.DataFrame:
    q = d.copy().sort_values("date").reset_index(drop=True)
    r = np.log(q["close"]).diff()
    q["ret_1"] = r
    q["ret_2"] = r.shift(1)
    q["ret_3"] = r.shift(2)
    for k in (3, 5, 10):
        q[f"mom_{k}"] = np.log(q["close"] / q["close"].shift(k))
    for k in (5, 10, 20):
        q[f"rv_{k}"] = r.rolling(k, min_periods=k).std(ddof=0)
    q["next_date"] = q["date"].shift(-1)
    q["next_return"] = np.log(q["close"].shift(-1) / q["close"])
    q["y_up_next"] = (q["next_return"] > 0).astype(float)
    q.loc[q["next_return"].isna(), "y_up_next"] = np.nan
    return q


def binary_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    eps = 1e-12
    pp = np.clip(p.astype(float), eps, 1 - eps)
    yy = y.astype(int)
    pred = (pp >= 0.5).astype(int)
    pos = yy == 1
    neg = yy == 0
    tpr = float(np.mean(pred[pos] == 1)) if pos.any() else None
    tnr = float(np.mean(pred[neg] == 0)) if neg.any() else None
    bal = float((tpr + tnr) / 2.0) if tpr is not None and tnr is not None else None
    return {
        "n": int(len(yy)),
        "up_rate": float(np.mean(yy)),
        "mean_p_up": float(np.mean(pp)),
        "accuracy": float(np.mean(pred == yy)),
        "balanced_accuracy": bal,
        "brier": float(np.mean((pp - yy) ** 2)),
        "log_loss": float(-np.mean(yy * np.log(pp) + (1 - yy) * np.log(1 - pp))),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--historical-exact", type=Path, required=True)
    ap.add_argument("--challenge-exact", type=Path, required=True)
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    contract = load_contract(args.contract)
    hist = load_exact(args.historical_exact, require_challenge_lineage=False)
    ch = load_exact(args.challenge_exact, require_challenge_lineage=True)

    if hist["date"].max() > TRAIN_END:
        hist = hist[hist["date"] <= TRAIN_END].copy()
    if ch["date"].min() < CHALLENGE_START or ch["date"].max() > CHALLENGE_END:
        raise RuntimeError(f"CHALLENGE_DATE_RANGE_FAIL:{ch['date'].min()}:{ch['date'].max()}")
    if hist["date"].max() >= ch["date"].min():
        raise RuntimeError("HISTORICAL_CHALLENGE_OVERLAP")

    combined = pd.concat([hist, ch], ignore_index=True).sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    feat = build_features(combined)

    train_mask = (
        feat["date"].between(TRAIN_START, TRAIN_END)
        & feat["next_date"].le(TRAIN_END)
        & feat[FEATURES].notna().all(axis=1)
        & feat["y_up_next"].notna()
    )
    train = feat.loc[train_mask].copy()
    if len(train) < 200:
        raise RuntimeError(f"INSUFFICIENT_TRAIN_ROWS:{len(train)}")
    if train["y_up_next"].nunique() < 2:
        raise RuntimeError("DEGENERATE_TRAIN_TARGET")

    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=1.0, solver="lbfgs", max_iter=500, random_state=20260911),
    )
    model.fit(train[FEATURES], train["y_up_next"].astype(int))

    score_mask = feat["date"].between(CHALLENGE_START, CHALLENGE_END) & feat[FEATURES].notna().all(axis=1)
    scored = feat.loc[score_mask, ["date", "close", "next_date", "next_return", "y_up_next", *FEATURES]].copy()
    if len(scored) < 180:
        raise RuntimeError(f"INSUFFICIENT_CHALLENGE_SCORE_ROWS:{len(scored)}")
    scored["p_up_next_governed_origin"] = model.predict_proba(scored[FEATURES])[:, 1]
    scored["edge_up_minus_down"] = 2.0 * scored["p_up_next_governed_origin"] - 1.0
    scored["implied_direction"] = np.where(scored["p_up_next_governed_origin"] >= 0.5, "UP", "DOWN")
    scored["research_identity"] = contract["research_identity"]
    scored["evidence_class"] = "HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PROSPECTIVE"
    scored["production_authority"] = False
    scored["challenge_refit"] = False
    scored["hyperparameter_search"] = False
    scored["threshold_search"] = False

    eval_rows = scored[scored["next_date"].le(CHALLENGE_END) & scored["y_up_next"].notna()].copy()
    metrics = binary_metrics(
        eval_rows["y_up_next"].astype(int).to_numpy(),
        eval_rows["p_up_next_governed_origin"].to_numpy(float),
    )

    scaler = model.named_steps["standardscaler"]
    clf = model.named_steps["logisticregression"]
    coef = pd.DataFrame({
        "feature": FEATURES,
        "coefficient_standardized": clf.coef_[0],
        "training_mean": scaler.mean_,
        "training_scale": scaler.scale_,
    })

    summary = {
        "audit_id": "GOLD_RIDGE_RECONSTRUCTION_V1_2025_REPLAY",
        "status": "PASS",
        "research_identity": contract["research_identity"],
        "manifest_channel_being_reconstructed": contract["manifest_channel_being_reconstructed"],
        "original_identity_recovered": False,
        "identity_claim": "SEPARATELY_NAMED_PROJECT_NATIVE_RECONSTRUCTION",
        "source_semantic": "Twelve Data XAU/USD 1min exact 16:59 America/New_York -> governed NY17 boundary",
        "train_start": TRAIN_START.date().isoformat(),
        "train_end": TRAIN_END.date().isoformat(),
        "train_rows": int(len(train)),
        "train_target_up_rate": float(train["y_up_next"].mean()),
        "challenge_start": CHALLENGE_START.date().isoformat(),
        "challenge_end": CHALLENGE_END.date().isoformat(),
        "challenge_input_valid_exact_rows": int(len(ch)),
        "challenge_scored_rows": int(len(scored)),
        "challenge_scored_min_date": scored["date"].min().date().isoformat(),
        "challenge_scored_max_date": scored["date"].max().date().isoformat(),
        "challenge_auxiliary_metrics": metrics,
        "probability_min": float(scored["p_up_next_governed_origin"].min()),
        "probability_max": float(scored["p_up_next_governed_origin"].max()),
        "probability_mean": float(scored["p_up_next_governed_origin"].mean()),
        "implied_direction_counts": {str(k): int(v) for k, v in scored["implied_direction"].value_counts().items()},
        "features": FEATURES,
        "model": "StandardScaler+LogisticRegression(C=1.0,solver=lbfgs,max_iter=500,random_state=20260911)",
        "challenge_refit": False,
        "hyperparameter_search": False,
        "threshold_search": False,
        "post_challenge_tuning": False,
        "current_gc_break_primary_target": False,
        "auxiliary_target_only": True,
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PROSPECTIVE",
        "production_database_write": "NONE",
        "production_authority": False,
    }

    scored.to_csv(args.output_dir / "gold_ridge_reconstruction_v1_2025_daily.csv", index=False)
    coef.to_csv(args.output_dir / "gold_ridge_reconstruction_v1_coefficients.csv", index=False)
    (args.output_dir / "gold_ridge_reconstruction_v1_2025_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
