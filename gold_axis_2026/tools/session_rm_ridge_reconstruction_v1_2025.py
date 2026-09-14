from __future__ import annotations

import argparse
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

NY = ZoneInfo("America/New_York")
FINAL_STATUSES = {"VALID_EXACT_BAR", "PROVIDER_NO_BAR"}
TRAIN_START = pd.Timestamp("2022-01-01")
TRAIN_END = pd.Timestamp("2024-12-31")
CHALLENGE_START = pd.Timestamp("2025-01-01")
CHALLENGE_END = pd.Timestamp("2025-12-31")
SESSIONS = ["PRE_ASIA", "ASIA_AM", "ASIA_PM", "EUROPE", "NYLON", "US_PRE_NY17"]
FEATURES = [x for s in SESSIONS for x in (f"{s.lower()}_ret", f"{s.lower()}_rv")]


def load_contract(path: Path) -> dict:
    c = json.loads(path.read_text(encoding="utf-8"))
    assert c["contract_id"] == "SESSION_RM_RIDGE_RECONSTRUCTION_V1_2025"
    assert c["status"] == "FROZEN_BEFORE_2025_REPLAY"
    assert c["split"]["challenge_refit"] is False
    assert c["split"]["challenge_hyperparameter_search"] is False
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
            "provider": "Twelve Data",
            "symbol": "XAU/USD",
            "interval": "1min",
            "timezone": "America/New_York",
            "accepted_source_time": "16:59:00",
            "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
            "prospective_claim": "False",
        }
        for k, val in expected.items():
            if k not in v or set(v[k]) != {val}:
                raise RuntimeError(f"CHALLENGE_LINEAGE_FAIL:{k}")
    v["date"] = pd.to_datetime(v["trade_date"], errors="raise").dt.normalize()
    v["close"] = pd.to_numeric(v["close"], errors="raise")
    if v["date"].duplicated().any() or (v["close"] <= 0).any():
        raise RuntimeError("INVALID_EXACT_ROWS")
    return v[["date", "close"]].sort_values("date").reset_index(drop=True)


def load_intraday(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path)
    if not {"observation_ts", "close"} <= set(d.columns):
        raise RuntimeError("INTRADAY_SCHEMA_FAIL")
    d["observation_ts"] = pd.to_datetime(d["observation_ts"], utc=True, errors="raise")
    d["close"] = pd.to_numeric(d["close"], errors="raise")
    d = d.drop_duplicates("observation_ts", keep="last").sort_values("observation_ts")
    if d.empty or (d["close"] <= 0).any() or not np.isfinite(d["close"].to_numpy(float)).all():
        raise RuntimeError("INVALID_INTRADAY_ROWS")
    d["ts_ny"] = d["observation_ts"].dt.tz_convert(NY)
    return d.reset_index(drop=True)


def nyts(day: pd.Timestamp, clock: str) -> pd.Timestamp:
    return pd.Timestamp(f"{day.strftime('%Y-%m-%d')} {clock}", tz=NY)


def session_bounds(day: pd.Timestamp) -> dict[str, tuple[pd.Timestamp, pd.Timestamp]]:
    prev = day - pd.Timedelta(days=1)
    return {
        "PRE_ASIA": (nyts(prev, "17:00"), nyts(prev, "21:00")),
        "ASIA_AM": (nyts(prev, "21:00"), nyts(prev, "23:30")),
        "ASIA_PM": (nyts(day, "01:30"), nyts(day, "03:30")),
        "EUROPE": (nyts(day, "03:30"), nyts(day, "08:00")),
        "NYLON": (nyts(day, "08:00"), nyts(day, "14:30")),
        "US_PRE_NY17": (nyts(day, "14:30"), nyts(day, "17:00")),
    }


def make_session_panel(origins: pd.DataFrame, intraday: pd.DataFrame, min_bars: int) -> pd.DataFrame:
    t = intraday["ts_ny"]
    close = intraday["close"]
    rows = []
    for r in origins.itertuples(index=False):
        day = pd.Timestamp(r.date)
        out = {"date": day, "close": float(r.close)}
        for name, (start, end) in session_bounds(day).items():
            mask = (t >= start) & (t < end)
            x = close.loc[mask].to_numpy(float)
            key = name.lower()
            out[f"{key}_bars"] = int(len(x))
            if len(x) < min_bars:
                out[f"{key}_ret"] = np.nan
                out[f"{key}_rv"] = np.nan
            else:
                lr = np.diff(np.log(x))
                out[f"{key}_ret"] = float(np.log(x[-1] / x[0]))
                out[f"{key}_rv"] = float(np.std(lr, ddof=0)) if len(lr) else 0.0
        rows.append(out)
    return pd.DataFrame(rows)


def binary_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    eps = 1e-12
    pp = np.clip(p.astype(float), eps, 1 - eps)
    yy = y.astype(int)
    pred = (pp >= 0.5).astype(int)
    pos, neg = yy == 1, yy == 0
    tpr = float(np.mean(pred[pos] == 1)) if pos.any() else None
    tnr = float(np.mean(pred[neg] == 0)) if neg.any() else None
    return {
        "n": int(len(yy)),
        "up_rate": float(np.mean(yy)),
        "accuracy": float(np.mean(pred == yy)),
        "balanced_accuracy": float((tpr + tnr) / 2) if tpr is not None and tnr is not None else None,
        "brier": float(np.mean((pp - yy) ** 2)),
        "log_loss": float(-np.mean(yy * np.log(pp) + (1 - yy) * np.log(1 - pp))),
        "mean_p_up": float(np.mean(pp)),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--historical-exact", type=Path, required=True)
    ap.add_argument("--challenge-exact", type=Path, required=True)
    ap.add_argument("--intraday-csv", type=Path, required=True)
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    c = load_contract(args.contract)
    min_bars = int(c["minimum_bars_per_session"])

    hist = load_exact(args.historical_exact, False)
    hist = hist[hist["date"] <= TRAIN_END].copy()
    ch = load_exact(args.challenge_exact, True)
    intraday = load_intraday(args.intraday_csv)
    origins = pd.concat([hist, ch], ignore_index=True).sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    panel = make_session_panel(origins, intraday, min_bars)
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
    if len(train) < 200 or train["y_up_next"].nunique() < 2:
        raise RuntimeError(f"INSUFFICIENT_TRAIN_SUPPORT:{len(train)}")

    model = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, solver="lbfgs", max_iter=500, random_state=20260911))
    model.fit(train[FEATURES], train["y_up_next"].astype(int))

    score_mask = panel["date"].between(CHALLENGE_START, CHALLENGE_END) & panel[FEATURES].notna().all(axis=1)
    scored = panel.loc[score_mask, ["date", "close", "next_date", "next_return", "y_up_next", *FEATURES] + [f"{s.lower()}_bars" for s in SESSIONS]].copy()
    if len(scored) < 180:
        raise RuntimeError(f"INSUFFICIENT_CHALLENGE_FEATURE_COVERAGE:{len(scored)}")
    scored["p_up_next_governed_origin"] = model.predict_proba(scored[FEATURES])[:, 1]
    scored["edge_up_minus_down"] = 2 * scored["p_up_next_governed_origin"] - 1
    scored["implied_direction"] = np.where(scored["p_up_next_governed_origin"] >= 0.5, "UP", "DOWN")
    scored["research_identity"] = c["research_identity"]
    scored["evidence_class"] = "HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PROSPECTIVE"
    scored["challenge_refit"] = False

    eval_rows = scored[scored["next_date"].le(CHALLENGE_END) & scored["y_up_next"].notna()].copy()
    metrics = binary_metrics(eval_rows["y_up_next"].astype(int).to_numpy(), eval_rows["p_up_next_governed_origin"].to_numpy(float))

    scaler = model.named_steps["standardscaler"]
    clf = model.named_steps["logisticregression"]
    coef = pd.DataFrame({"feature": FEATURES, "coefficient_standardized": clf.coef_[0], "training_mean": scaler.mean_, "training_scale": scaler.scale_})

    all_challenge = panel[panel["date"].between(CHALLENGE_START, CHALLENGE_END)]
    summary = {
        "audit_id": "SESSION_RM_RIDGE_RECONSTRUCTION_V1_2025_REPLAY",
        "status": "PASS",
        "research_identity": c["research_identity"],
        "manifest_channel_being_reconstructed": c["manifest_channel_being_reconstructed"],
        "original_identity_recovered": False,
        "identity_claim": "SEPARATELY_NAMED_LITERATURE_INFORMED_RECONSTRUCTION",
        "train_rows": int(len(train)),
        "train_target_up_rate": float(train["y_up_next"].mean()),
        "challenge_exact_rows": int(len(ch)),
        "challenge_feature_complete_rows": int(len(scored)),
        "challenge_feature_coverage": float(len(scored) / len(all_challenge)) if len(all_challenge) else 0.0,
        "challenge_auxiliary_metrics": metrics,
        "probability_min": float(scored["p_up_next_governed_origin"].min()),
        "probability_max": float(scored["p_up_next_governed_origin"].max()),
        "probability_mean": float(scored["p_up_next_governed_origin"].mean()),
        "implied_direction_counts": {str(k): int(v) for k, v in scored["implied_direction"].value_counts().items()},
        "features": FEATURES,
        "session_windows": c["session_windows_america_new_york"],
        "model": "StandardScaler+LogisticRegression(C=1.0)",
        "challenge_refit": False,
        "hyperparameter_search": False,
        "threshold_search": False,
        "post_challenge_tuning": False,
        "current_gc_break_primary_target": False,
        "auxiliary_target_only": True,
        "intraday_evidence_class": c["intraday_feature_source"]["evidence_class"],
        "production_database_write": "NONE",
        "production_authority": False
    }
    scored.to_csv(args.output_dir / "session_rm_ridge_reconstruction_v1_2025_daily.csv", index=False)
    coef.to_csv(args.output_dir / "session_rm_ridge_reconstruction_v1_coefficients.csv", index=False)
    (args.output_dir / "session_rm_ridge_reconstruction_v1_2025_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
