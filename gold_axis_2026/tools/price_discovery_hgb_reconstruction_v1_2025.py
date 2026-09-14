from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

FINAL_STATUSES = {"VALID_EXACT_BAR", "PROVIDER_NO_BAR"}
TRAIN_START = pd.Timestamp("2022-01-01")
TRAIN_END = pd.Timestamp("2024-12-31")
CHALLENGE_START = pd.Timestamp("2025-01-01")
CHALLENGE_END = pd.Timestamp("2025-12-31")
GOLD_FEATURES = [
    "gold_ret_lag1", "gold_ret_lag2", "gold_ret_lag3",
    "gold_mom3", "gold_mom5", "gold_mom10", "gold_mom20",
    "gold_rv5", "gold_rv10", "gold_rv20",
]
CROSS_FEATURES = ["xag_ret", "xpt_ret", "xpd_ret"]
FEATURES = GOLD_FEATURES + CROSS_FEATURES
SERIES_MAP = {
    "xag": "XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "xpt": "XPT_STAKTRAKR_RESEARCH_DAILY_R1",
    "xpd": "XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}


def load_contract(path: Path) -> dict:
    c = json.loads(path.read_text(encoding="utf-8"))
    assert c["contract_id"] == "PRICE_DISCOVERY_HGB_RECONSTRUCTION_V1_2025"
    assert c["status"] == "FROZEN_BEFORE_2025_REPLAY"
    assert c["split"]["challenge_refit"] is False
    assert c["split"]["challenge_hyperparameter_search"] is False
    assert c["features"] == FEATURES
    return c


def load_exact(path: Path, challenge: bool) -> pd.DataFrame:
    d = pd.read_csv(path, dtype=str, keep_default_na=False)
    if not {"trade_date", "acquisition_status"} <= set(d.columns):
        raise RuntimeError(f"EXACT_SCHEMA_FAIL:{path}")
    bad = sorted(set(d["acquisition_status"]) - FINAL_STATUSES)
    if bad:
        raise RuntimeError(f"UNRESOLVED_EXACT_STATUS:{bad[:5]}")
    v = d[d["acquisition_status"].eq("VALID_EXACT_BAR")].copy()
    if challenge:
        expected = {
            "provider": "Twelve Data", "symbol": "XAU/USD", "interval": "1min",
            "timezone": "America/New_York", "accepted_source_time": "16:59:00",
            "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION", "prospective_claim": "False",
        }
        for k, val in expected.items():
            if k not in v.columns or set(v[k]) != {val}:
                raise RuntimeError(f"CHALLENGE_LINEAGE_FAIL:{k}")
    v["date"] = pd.to_datetime(v["trade_date"], errors="raise").dt.normalize()
    v["close"] = pd.to_numeric(v["close"], errors="raise")
    if v["date"].duplicated().any() or (v["close"] <= 0).any():
        raise RuntimeError("INVALID_EXACT_ROWS")
    return v[["date", "close"]].sort_values("date").reset_index(drop=True)


def build_gold_features(d: pd.DataFrame) -> pd.DataFrame:
    q = d.copy().sort_values("date").reset_index(drop=True)
    logc = np.log(q["close"])
    r = logc.diff()
    q["gold_ret_lag1"] = r
    q["gold_ret_lag2"] = r.shift(1)
    q["gold_ret_lag3"] = r.shift(2)
    for k in (3, 5, 10, 20):
        q[f"gold_mom{k}"] = np.log(q["close"] / q["close"].shift(k))
    for k in (5, 10, 20):
        q[f"gold_rv{k}"] = r.rolling(k, min_periods=k).std(ddof=0)
    return q


def attach_cross(d: pd.DataFrame, path: Path) -> pd.DataFrame:
    obs = pd.read_csv(path)
    required = {"series_id", "observation_ts", "value"}
    if not required <= set(obs.columns):
        raise RuntimeError("CROSS_SCHEMA_FAIL")
    obs["source_date"] = pd.to_datetime(obs["observation_ts"], utc=True, errors="raise").dt.tz_localize(None).dt.normalize()
    obs["value"] = pd.to_numeric(obs["value"], errors="coerce")
    obs = obs.dropna(subset=["value"])
    out = d.sort_values("date").copy()
    for name, sid in SERIES_MAP.items():
        z = obs[obs["series_id"].eq(sid)][["source_date", "value"]].copy()
        z = z.drop_duplicates("source_date", keep="last").sort_values("source_date")
        z[f"{name}_ret"] = np.log(z["value"]).diff()
        z = z.rename(columns={"source_date": f"{name}_source_date"})
        out = pd.merge_asof(
            out.sort_values("date"), z.sort_values(f"{name}_source_date"),
            left_on="date", right_on=f"{name}_source_date",
            direction="backward", allow_exact_matches=False,
        )
        bad = out[f"{name}_source_date"].notna() & (out[f"{name}_source_date"] >= out["date"])
        if bad.any():
            raise RuntimeError(f"FUTURE_OR_SAMEDAY_CROSS_SOURCE:{name}")
        out = out.drop(columns=["value"])
    return out


def binary_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    eps = 1e-12
    pp = np.clip(p.astype(float), eps, 1 - eps)
    yy = y.astype(int)
    pred = (pp >= 0.5).astype(int)
    pos, neg = yy == 1, yy == 0
    tpr = float(np.mean(pred[pos] == 1)) if pos.any() else None
    tnr = float(np.mean(pred[neg] == 0)) if neg.any() else None
    return {
        "n": int(len(yy)), "up_rate": float(np.mean(yy)), "mean_p_up": float(np.mean(pp)),
        "accuracy": float(np.mean(pred == yy)),
        "balanced_accuracy": float((tpr + tnr) / 2) if tpr is not None and tnr is not None else None,
        "brier": float(np.mean((pp - yy) ** 2)),
        "log_loss": float(-np.mean(yy * np.log(pp) + (1 - yy) * np.log(1 - pp))),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--historical-exact", type=Path, required=True)
    ap.add_argument("--challenge-exact", type=Path, required=True)
    ap.add_argument("--cross-csv", type=Path, required=True)
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    c = load_contract(args.contract)

    hist = load_exact(args.historical_exact, False)
    hist = hist[hist["date"] <= TRAIN_END].copy()
    ch = load_exact(args.challenge_exact, True)
    origins = pd.concat([hist, ch], ignore_index=True).sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    panel = attach_cross(build_gold_features(origins), args.cross_csv)
    panel["next_date"] = panel["date"].shift(-1)
    panel["next_return"] = np.log(panel["close"].shift(-1) / panel["close"])
    panel["y_up_next"] = (panel["next_return"] > 0).astype(float)
    panel.loc[panel["next_return"].isna(), "y_up_next"] = np.nan

    train_mask = (
        panel["date"].between(TRAIN_START, TRAIN_END)
        & panel["next_date"].le(TRAIN_END)
        & panel[FEATURES].notna().all(axis=1)
        & panel["y_up_next"].notna()
    )
    train = panel.loc[train_mask].copy()
    if len(train) < 250 or train["y_up_next"].nunique() < 2:
        raise RuntimeError(f"INSUFFICIENT_TRAIN_SUPPORT:{len(train)}")

    model = HistGradientBoostingClassifier(
        max_depth=2, max_iter=80, learning_rate=0.05,
        l2_regularization=1.0, random_state=20260911,
    )
    model.fit(train[FEATURES], train["y_up_next"].astype(int))

    score_mask = panel["date"].between(CHALLENGE_START, CHALLENGE_END) & panel[FEATURES].notna().all(axis=1)
    extra = [f"{n}_source_date" for n in SERIES_MAP]
    scored = panel.loc[score_mask, ["date", "close", "next_date", "next_return", "y_up_next", *FEATURES, *extra]].copy()
    if len(scored) < 180:
        raise RuntimeError(f"INSUFFICIENT_CHALLENGE_COVERAGE:{len(scored)}")
    scored["p_up_next_governed_origin"] = model.predict_proba(scored[FEATURES])[:, 1]
    scored["edge_up_minus_down"] = 2 * scored["p_up_next_governed_origin"] - 1
    scored["implied_direction"] = np.where(scored["p_up_next_governed_origin"] >= 0.5, "UP", "DOWN")
    scored["research_identity"] = c["research_identity"]
    scored["evidence_class"] = "HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PROSPECTIVE"
    scored["challenge_refit"] = False

    eval_rows = scored[scored["next_date"].le(CHALLENGE_END) & scored["y_up_next"].notna()].copy()
    metrics = binary_metrics(eval_rows["y_up_next"].astype(int).to_numpy(), eval_rows["p_up_next_governed_origin"].to_numpy(float))
    all_ch = panel[panel["date"].between(CHALLENGE_START, CHALLENGE_END)]
    summary = {
        "audit_id": "PRICE_DISCOVERY_HGB_RECONSTRUCTION_V1_2025_REPLAY",
        "status": "PASS", "research_identity": c["research_identity"],
        "manifest_channel_being_reconstructed": c["manifest_channel_being_reconstructed"],
        "original_identity_recovered": False,
        "identity_claim": "SEPARATELY_NAMED_PROJECT_NATIVE_LITERATURE_INFORMED_RECONSTRUCTION",
        "train_rows": int(len(train)), "train_target_up_rate": float(train["y_up_next"].mean()),
        "challenge_exact_rows": int(len(ch)), "challenge_feature_complete_rows": int(len(scored)),
        "challenge_feature_coverage": float(len(scored) / len(all_ch)) if len(all_ch) else 0.0,
        "challenge_auxiliary_metrics": metrics,
        "probability_min": float(scored["p_up_next_governed_origin"].min()),
        "probability_max": float(scored["p_up_next_governed_origin"].max()),
        "probability_mean": float(scored["p_up_next_governed_origin"].mean()),
        "implied_direction_counts": {str(k): int(v) for k, v in scored["implied_direction"].value_counts().items()},
        "features": FEATURES,
        "model": "HistGradientBoostingClassifier(max_depth=2,max_iter=80,learning_rate=0.05,l2_regularization=1,random_state=20260911)",
        "challenge_refit": False, "hyperparameter_search": False, "threshold_search": False,
        "post_challenge_tuning": False, "current_gc_break_primary_target": False, "auxiliary_target_only": True,
        "cross_metal_evidence_class": c["cross_metal_sources"]["evidence_class"],
        "production_database_write": "NONE", "production_authority": False,
    }
    scored.to_csv(args.output_dir / "price_discovery_hgb_reconstruction_v1_2025_daily.csv", index=False)
    (args.output_dir / "price_discovery_hgb_reconstruction_v1_2025_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
