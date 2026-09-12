from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import psycopg
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, balanced_accuracy_score, matthews_corrcoef, mean_pinball_loss
from sklearn.pipeline import make_pipeline

from gold_axis_2026.v157_thesis import run_v157_breakaware_realized_moments as v157
from gold_axis_2026.v159_thesis import run_v159_driver_corrected_meta_trust as v159
from gold_axis_2026.v159_thesis import run_v159r1_entry as v159r1

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "v161_thesis/contracts/v161_literature_short_horizon_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v161_thesis"


def load_contract() -> dict[str, Any]:
    c = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if c.get("status") != "FROZEN_BEFORE_V161_RETROSPECTIVE_SCORING":
        raise RuntimeError("V161_CONTRACT_NOT_FROZEN")
    if c.get("relationship_to_v160", "").split(";")[0] != "SEPARATE_SHORT_HORIZON_RESEARCH_LINE":
        raise RuntimeError("V161_MUST_NOT_REOPEN_V160")
    g = c["governance"]
    if g.get("AUTO_SELECTOR") != "OFF" or g.get("AUTO_ENSEMBLE") != "OFF":
        raise RuntimeError("V161_GOVERNANCE_LOCK_FAIL")
    if g.get("production_authority") is not False or g.get("production_writes") != "NONE":
        raise RuntimeError("V161_PRODUCTION_AUTHORITY_FORBIDDEN")
    return c


def build_panel(contract: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    parent = v159r1.merged_contract()
    start = "2022-01-01"
    end = contract["windows"]["test_end"]
    frames: dict[str, pd.DataFrame] = {}
    source_evidence: dict[str, Any] = {}
    for sid in ["DTWEXBGS", "DFII10"]:
        d, evidence = v159r1.fedboard_fetch(sid, start, end)
        frames[sid] = d
        source_evidence[sid] = evidence

    database_url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not database_url:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")
    v157_contract = json.loads(v159.V157_CONTRACT_PATH.read_text(encoding="utf-8"))
    with psycopg.connect(database_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
        panel, _, _, _ = v157.build_panel(conn, v157_contract)
    panel = v159.add_corrected_drivers(panel, frames, parent)
    panel["date"] = pd.to_datetime(panel["date"], errors="raise").dt.normalize()
    return panel.sort_values("date").reset_index(drop=True), source_evidence


def feature_list(contract: dict[str, Any], candidate_id: str) -> list[str]:
    spec = contract["candidates"][candidate_id]
    base = list(contract["features"]["BASE"])
    if spec["feature_set"] == "BASE":
        return base
    if spec["feature_set"] == "BASE_PLUS_REALIZED":
        return base + list(contract["features"]["REALIZED"])
    raise KeyError(spec["feature_set"])


def prepare_horizon(panel: pd.DataFrame, h: int) -> pd.DataFrame:
    d = panel.copy()
    d["close"] = pd.to_numeric(d["close"], errors="coerce")
    d = d[(d["date"].dt.weekday < 5) & np.isfinite(d["close"])].copy()
    d = d.sort_values("date").reset_index(drop=True)
    d["eligible_index"] = np.arange(len(d), dtype=int)
    d["target_date"] = d["date"].shift(-h)
    d["target_close"] = d["close"].shift(-h)
    d["target_return"] = np.log(d["target_close"].astype(float) / d["close"].astype(float))
    d["future_direction"] = np.sign(d["target_return"]).fillna(0).astype(int)
    d["target_eligible_index"] = d["eligible_index"] + int(h)
    return d


def make_quantile_model(contract: dict[str, Any], q: float):
    m = contract["model"]
    return make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
        GradientBoostingRegressor(
            loss="quantile",
            alpha=float(q),
            n_estimators=int(m["n_estimators"]),
            learning_rate=float(m["learning_rate"]),
            max_depth=int(m["max_depth"]),
            min_samples_leaf=int(m["min_samples_leaf"]),
            subsample=float(m["subsample"]),
            random_state=int(m["random_state"]),
        ),
    )


def sequential_monthly_quantile_forecast(
    panel: pd.DataFrame,
    h: int,
    features: list[str],
    candidate_id: str,
    contract: dict[str, Any],
) -> pd.DataFrame:
    d = prepare_horizon(panel, h)
    missing = [c for c in features if c not in d.columns]
    if missing:
        raise RuntimeError(f"V161_FEATURES_MISSING:{candidate_id}:{missing}")
    start = pd.Timestamp(contract["windows"]["formation_start"])
    scoring = d[d["date"] >= start].copy()
    mcfg = contract["model"]
    cap = int(mcfg["training_window_mature_rows"])
    minimum = int(mcfg["minimum_mature_rows"])
    quantiles = [float(x) for x in mcfg["quantiles"]]
    rows: list[dict[str, Any]] = []

    for _, month_block in scoring.groupby(scoring["date"].dt.to_period("M"), sort=True):
        first_pos = int(month_block["eligible_index"].min())
        train = d[
            (d["target_eligible_index"] <= first_pos)
            & d["target_return"].notna()
            & np.isfinite(d["target_return"])
        ].copy()
        train = train.tail(cap)
        models = None
        if len(train) >= minimum:
            models = []
            for q in quantiles:
                model = make_quantile_model(contract, q)
                model.fit(train[features], train["target_return"].astype(float))
                models.append(model)

        for _, row in month_block.iterrows():
            pred = [np.nan, np.nan, np.nan]
            signal = 0
            if models is not None:
                x = row[features].to_frame().T
                pred = sorted(float(model.predict(x)[0]) for model in models)
                signal = 1 if pred[0] > 0 else (-1 if pred[2] < 0 else 0)
            rows.append({
                "candidate_id": candidate_id,
                "horizon": int(h),
                "eligible_index": int(row["eligible_index"]),
                "origin_date": row["date"],
                "target_date": row["target_date"],
                "target_return": None if pd.isna(row["target_return"]) else float(row["target_return"]),
                "future_direction": int(row["future_direction"]),
                "train_n": int(len(train)),
                "q25": None if not math.isfinite(pred[0]) else pred[0],
                "q50": None if not math.isfinite(pred[1]) else pred[1],
                "q75": None if not math.isfinite(pred[2]) else pred[2],
                "signal": int(signal),
            })
    return pd.DataFrame(rows)


def period_for(origin: pd.Timestamp, target: pd.Timestamp, contract: dict[str, Any]) -> str:
    periods = [
        ("FORMATION_2024", contract["windows"]["formation_start"], contract["windows"]["formation_end"]),
        ("VALIDATION_2025", contract["windows"]["validation_start"], contract["windows"]["validation_end"]),
        ("TEST_2026_AVAILABLE", contract["windows"]["test_start"], contract["windows"]["test_end"]),
    ]
    for name, a, b in periods:
        aa, bb = pd.Timestamp(a), pd.Timestamp(b)
        if aa <= origin <= bb and pd.notna(target) and target <= bb:
            return name
    return "OUTSIDE"


def _safe_number(x: float | int | np.number | None) -> float | int | None:
    if x is None:
        return None
    y = float(x)
    return y if math.isfinite(y) else None


def direction_metrics(g: pd.DataFrame, signal_col: str = "signal") -> dict[str, Any]:
    z = g[g["target_return"].notna() & g["future_direction"].ne(0)].copy()
    n = int(len(z))
    if n == 0:
        return {"n": 0, "selective_n": 0, "coverage": 0.0, "status": "BLOCKED_EMPTY"}
    sig = z[signal_col].fillna(0).astype(int)
    take = sig.ne(0)
    s = z.loc[take].copy()
    if s.empty:
        return {
            "n": n,
            "selective_n": 0,
            "coverage": 0.0,
            "selective_accuracy": None,
            "selective_balanced_accuracy": None,
            "mcc": None,
            "up_signals": 0,
            "down_signals": 0,
            "median_signed_return": None,
            "status": "NO_SIGNAL",
        }
    y = (s["future_direction"].astype(int) > 0).astype(int)
    pred = (s[signal_col].astype(int) > 0).astype(int)
    signed = s["target_return"].astype(float) * s[signal_col].astype(int)
    return {
        "n": n,
        "selective_n": int(len(s)),
        "coverage": float(len(s) / n),
        "selective_accuracy": float(accuracy_score(y, pred)),
        "selective_balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "mcc": float(matthews_corrcoef(y, pred)),
        "up_signals": int((s[signal_col].astype(int) == 1).sum()),
        "down_signals": int((s[signal_col].astype(int) == -1).sum()),
        "median_signed_return": float(np.median(signed)),
        "actual_up_rate": float(y.mean()),
        "status": "SCORED",
    }


def pinball_metrics(g: pd.DataFrame) -> dict[str, Any]:
    z = g[g["target_return"].notna() & g[["q25", "q50", "q75"]].notna().all(axis=1)].copy()
    if z.empty:
        return {"n": 0, "mean_pinball_loss": None}
    y = z["target_return"].astype(float).to_numpy()
    vals = []
    for q, col in [(0.25, "q25"), (0.50, "q50"), (0.75, "q75")]:
        vals.append(float(mean_pinball_loss(y, z[col].astype(float).to_numpy(), alpha=q)))
    return {
        "n": int(len(z)),
        "q25_pinball": vals[0],
        "q50_pinball": vals[1],
        "q75_pinball": vals[2],
        "mean_pinball_loss": float(np.mean(vals)),
    }


def nonoverlap_metrics(g: pd.DataFrame, h: int) -> dict[str, Any]:
    z = g.sort_values("eligible_index").reset_index(drop=True)
    if z.empty:
        return {"n": 0, "status": "BLOCKED_EMPTY"}
    z = z.iloc[:: int(h)].copy()
    return direction_metrics(z)


def momentum_benchmark(panel: pd.DataFrame, h: int, contract: dict[str, Any]) -> pd.DataFrame:
    d = prepare_horizon(panel, h)
    col = f"mom{h}"
    if col not in d.columns:
        raise RuntimeError(f"V161_MOMENTUM_COLUMN_MISSING:{col}")
    d["signal"] = np.sign(pd.to_numeric(d[col], errors="coerce")).fillna(0).astype(int)
    d["origin_date"] = d["date"]
    return d[["eligible_index", "origin_date", "target_date", "target_return", "future_direction", "signal"]]


def score_forecasts(forecasts: pd.DataFrame, contract: dict[str, Any]) -> dict[str, Any]:
    d = forecasts.copy()
    d["origin_date"] = pd.to_datetime(d["origin_date"])
    d["target_date"] = pd.to_datetime(d["target_date"])
    d["period"] = [period_for(a, b, contract) for a, b in zip(d["origin_date"], d["target_date"])]
    out: dict[str, Any] = {}
    for period in ["FORMATION_2024", "VALIDATION_2025", "TEST_2026_AVAILABLE"]:
        g = d[d["period"].eq(period)]
        direction = direction_metrics(g)
        direction["pinball"] = pinball_metrics(g)
        direction["nonoverlap_offset0"] = nonoverlap_metrics(g, int(d["horizon"].iloc[0])) if not d.empty else {"n": 0}
        out[period] = direction
    return out


def score_benchmark(bench: pd.DataFrame, h: int, contract: dict[str, Any]) -> dict[str, Any]:
    d = bench.copy()
    d["origin_date"] = pd.to_datetime(d["origin_date"])
    d["target_date"] = pd.to_datetime(d["target_date"])
    d["period"] = [period_for(a, b, contract) for a, b in zip(d["origin_date"], d["target_date"])]
    return {
        p: direction_metrics(d[d["period"].eq(p)])
        for p in ["FORMATION_2024", "VALIDATION_2025", "TEST_2026_AVAILABLE"]
    }


def support_gate(metrics: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    r = contract["evaluation"]["support_gate_primary"]
    v = metrics["VALIDATION_2025"]
    t = metrics["TEST_2026_AVAILABLE"]
    checks = {
        "validation_coverage": v.get("coverage", 0.0) >= float(r["validation_2025_coverage_min"]),
        "validation_balanced": (v.get("selective_balanced_accuracy") or 0.0) >= float(r["validation_2025_balanced_min"]),
        "validation_mcc": (v.get("mcc") or 0.0) >= float(r["validation_2025_mcc_min"]),
        "validation_both_directions": v.get("up_signals", 0) > 0 and v.get("down_signals", 0) > 0,
        "test_coverage": t.get("coverage", 0.0) >= float(r["test_2026_coverage_min"]),
        "test_balanced": (t.get("selective_balanced_accuracy") or 0.0) >= float(r["test_2026_balanced_min"]),
        "test_mcc": (t.get("mcc") or 0.0) >= float(r["test_2026_mcc_min"]),
        "test_both_directions": t.get("up_signals", 0) > 0 and t.get("down_signals", 0) > 0,
    }
    return {"pass": bool(all(checks.values())), "checks": checks}


def main() -> int:
    contract = load_contract()
    panel, source_evidence = build_panel(contract)
    candidate_frames: list[pd.DataFrame] = []
    results: dict[str, Any] = {
        "contract_id": contract["contract_id"],
        "status": "RETROSPECTIVE_SHORT_HORIZON_LITERATURE_DIAGNOSTIC_COMPLETE",
        "evidence_class": contract["evidence_class"],
        "production_authority": False,
        "source_evidence": source_evidence,
        "data_audit": {
            "panel_rows": int(len(panel)),
            "first_date": panel["date"].min().date().isoformat(),
            "last_date": panel["date"].max().date().isoformat(),
            "comex_gc_futures": contract["data"]["comex_gc_futures"],
            "futures_claim": contract["data"]["futures_claim"],
        },
        "candidates": {},
        "benchmarks": {},
    }

    horizons = [int(contract["targets"]["secondary_horizon_sessions"]), int(contract["targets"]["primary_horizon_sessions"])]
    for h in horizons:
        hkey = f"H{h}"
        results["candidates"][hkey] = {}
        for cid in contract["candidates"]:
            features = feature_list(contract, cid)
            f = sequential_monthly_quantile_forecast(panel, h, features, cid, contract)
            candidate_frames.append(f)
            results["candidates"][hkey][cid] = {
                "feature_count": int(len(features)),
                "metrics": score_forecasts(f, contract),
            }
        bench = momentum_benchmark(panel, h, contract)
        results["benchmarks"][hkey] = {"MOMENTUM_SAME_HORIZON": score_benchmark(bench, h, contract)}

    primary_h = int(contract["evaluation"]["primary_horizon"])
    primary_id = str(contract["evaluation"]["primary_candidate"])
    primary_metrics = results["candidates"][f"H{primary_h}"][primary_id]["metrics"]
    results["support_gate_primary"] = support_gate(primary_metrics, contract)
    results["interpretation_lock"] = {
        "primary_candidate": primary_id,
        "primary_horizon": primary_h,
        "v160_sequence_not_reopened": True,
        "comex_futures_not_used": True,
        "not_exact_replication_of_published_quantile_boosting": True,
        "2025_2026_are_researcher_visible": True,
        "future_prospective_shadow_required": True,
        "post_score_changes_forbidden_inside_v161": True,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT / "v161_driver_panel.csv", index=False)
    pd.concat(candidate_frames, ignore_index=True).to_csv(OUT / "v161_quantile_boosting_predictions.csv", index=False)
    (OUT / "v161_results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
