from __future__ import annotations

import hashlib
import io
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import psycopg
import requests
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, log_loss, matthews_corrcoef
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from gold_axis_2026.v156_thesis import run_v156_realtime_quantile_selective as v156
from gold_axis_2026.v157_thesis import run_v157_breakaware_realized_moments as v157
from gold_axis_2026.v158_thesis import run_v158_trend_reversal_router as v158

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "v159_thesis/contracts/v159_driver_corrected_meta_trust_freeze_v1.json"
V157_CONTRACT_PATH = ROOT / "v157_thesis/contracts/v157_breakaware_realized_moments_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v159_thesis"
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv"


def load_contract() -> dict:
    c = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if c.get("status") != "FROZEN_BEFORE_V159_RETROSPECTIVE_SCORING":
        raise RuntimeError("V159_CONTRACT_NOT_FROZEN")
    g = c["governance"]
    if g.get("AUTO_SELECTOR") != "OFF" or g.get("AUTO_ENSEMBLE") != "OFF":
        raise RuntimeError("V159_GOVERNANCE_LOCK_FAIL")
    if g.get("production_authority") is not False or g.get("production_writes") != "NONE":
        raise RuntimeError("V159_PRODUCTION_AUTHORITY_FORBIDDEN")
    return c


def fetch_fred_series(series_id: str, start: str, end: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    response = requests.get(
        FRED_CSV,
        params={"id": series_id, "cosd": start, "coed": end},
        headers={"User-Agent": "Gold-Control-V159-Research/1.0"},
        timeout=(20, 120),
    )
    retrieved_at = datetime.now(timezone.utc).isoformat()
    payload_sha = hashlib.sha256(response.content).hexdigest()
    if response.status_code != 200:
        raise RuntimeError(f"V159_FRED_HTTP_{series_id}_{response.status_code}")
    try:
        d = pd.read_csv(io.BytesIO(response.content))
    except Exception as exc:
        raise RuntimeError(f"V159_FRED_PARSE_{series_id}") from exc
    if d.shape[1] < 2:
        raise RuntimeError(f"V159_FRED_SCHEMA_{series_id}")
    date_col = d.columns[0]
    value_col = series_id if series_id in d.columns else d.columns[1]
    d = d[[date_col, value_col]].rename(columns={date_col: "source_date", value_col: "value"})
    d["source_date"] = pd.to_datetime(d["source_date"], errors="coerce").dt.normalize()
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["source_date", "value"]).sort_values("source_date").drop_duplicates("source_date", keep="last")
    d = d[np.isfinite(d["value"])].copy()
    if d.empty:
        raise RuntimeError(f"V159_FRED_EMPTY_{series_id}")
    evidence = {
        "provider": "FRED",
        "series_id": series_id,
        "retrieved_at": retrieved_at,
        "payload_sha256": payload_sha,
        "rows": int(len(d)),
        "first_source_date": d["source_date"].min().date().isoformat(),
        "last_source_date": d["source_date"].max().date().isoformat(),
        "evidence_class": "HISTORICAL_ECONOMIC_DATE_RECONSTRUCTION_NOT_PROSPECTIVE_PIT",
        "same_date_join_forbidden": True,
    }
    return d.reset_index(drop=True), evidence


def build_driver_source(contract: dict) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    w = contract["windows"]
    # A full extra year is fetched only to form lagged source-date transformations before the 2023 panel begins.
    start = "2022-01-01"
    end = w["test_end"]
    frames: dict[str, pd.DataFrame] = {}
    evidence: dict[str, Any] = {}
    for sid in ["DTWEXBGS", "DFII10"]:
        d, e = fetch_fred_series(sid, start, end)
        frames[sid] = d
        evidence[sid] = e
    return frames, evidence


def _merge_strict_previous_date(left: pd.DataFrame, right: pd.DataFrame, source_name: str) -> pd.DataFrame:
    l = left.copy().sort_values("date")
    r = right.copy().sort_values("source_date")
    out = pd.merge_asof(
        l,
        r,
        left_on="date",
        right_on="source_date",
        direction="backward",
        allow_exact_matches=False,
    )
    out = out.rename(columns={"source_date": f"{source_name}_source_date"})
    bad = out[f"{source_name}_source_date"].notna() & (out[f"{source_name}_source_date"] >= out["date"])
    if bad.any():
        raise RuntimeError(f"V159_SAME_OR_FUTURE_DATE_DRIVER_JOIN:{source_name}")
    return out


def add_corrected_drivers(panel: pd.DataFrame, frames: dict[str, pd.DataFrame], contract: dict) -> pd.DataFrame:
    usd = frames["DTWEXBGS"].copy()
    usd["broad_usd_level"] = usd["value"].astype(float)
    lp = np.log(usd["broad_usd_level"])
    usd["broad_usd_logdiff1"] = lp.diff(1)
    usd["broad_usd_logdiff5"] = lp.diff(5)
    usd = usd.drop(columns=["value"])

    real = frames["DFII10"].copy()
    real["real10_level"] = real["value"].astype(float)
    real["real10_delta1"] = real["real10_level"].diff(1)
    real["real10_delta5"] = real["real10_level"].diff(5)
    real = real.drop(columns=["value"])

    d = _merge_strict_previous_date(panel, usd, "broad_usd")
    d = _merge_strict_previous_date(d, real, "real10")
    required = list(contract["corrected_driver_features"])
    score_start = pd.Timestamp(contract["windows"]["formation_score_start"])
    scoring = d[d["date"] >= score_start]
    if scoring[required].isna().any().any():
        missing = {c: int(scoring[c].isna().sum()) for c in required if scoring[c].isna().any()}
        raise RuntimeError(f"V159_CORRECTED_DRIVER_COVERAGE_FAIL:{missing}")
    return d.sort_values("date").reset_index(drop=True)


def corrected_parent_features(base_features: list[str], contract: dict) -> list[str]:
    banned = {"fx_level", "fx_logdiff"}
    out = [x for x in base_features if x not in banned]
    out.extend(list(contract["corrected_driver_features"]))
    if any(x in out for x in banned):
        raise RuntimeError("V159_LEGACY_GENERIC_FX_NOT_REMOVED")
    return list(dict.fromkeys(out))


def corrected_rtq_parent(panel: pd.DataFrame, features: list[str], contract: dict) -> pd.DataFrame:
    h = int(contract["target"]["primary_horizon_sessions"])
    z = v156.add_target(panel, h)
    cfg = dict(contract["rtq_model"])
    f = v156.sequential_quantiles(
        z,
        features,
        "DRIVER_RTQ_R126",
        cfg,
        h,
        contract["windows"]["formation_score_start"],
    )
    if f.empty:
        raise RuntimeError("V159_DRIVER_RTQ_EMPTY")
    f["parent_signal"] = np.where(f["q25"] > 0, 1, np.where(f["q75"] < 0, -1, 0)).astype(int)
    return f


def legacy_rtq_parent(panel: pd.DataFrame, base_features: list[str]) -> pd.DataFrame:
    f = v158.build_rtq_baseline(panel, base_features).copy()
    f = f.rename(columns={"rtq_signal": "parent_signal"})
    f["parent_signal"] = f["parent_signal"].astype(int)
    return f


def prepare_parent_frame(parent: pd.DataFrame, routed_panel: pd.DataFrame, contract: dict) -> pd.DataFrame:
    base_meta = list(contract["meta_features"]["BASE"])
    driver_meta = list(contract["corrected_driver_features"])
    panel_cols = [
        "origin_index", "future_direction", "target_return",
        *[c for c in base_meta if not c.startswith("rtq_")],
        *driver_meta,
    ]
    panel_cols = list(dict.fromkeys(panel_cols))
    missing = [c for c in panel_cols if c not in routed_panel.columns]
    if missing:
        raise RuntimeError(f"V159_META_PANEL_FEATURES_MISSING:{missing}")
    d = parent.merge(routed_panel[panel_cols], on="origin_index", how="left", validate="one_to_one", suffixes=("", "_panel"))
    if d["future_direction"].isna().any():
        raise RuntimeError("V159_PARENT_ACTUAL_ALIGNMENT_FAIL")
    d["rtq_q25"] = d["q25"].astype(float)
    d["rtq_q50"] = d["q50"].astype(float)
    d["rtq_q75"] = d["q75"].astype(float)
    d["rtq_iqr_width"] = d["rtq_q75"] - d["rtq_q25"]
    d["rtq_direction"] = d["parent_signal"].astype(float)
    d["rtq_zero_distance"] = np.where(
        d["parent_signal"].eq(1),
        d["rtq_q25"],
        np.where(d["parent_signal"].eq(-1), -d["rtq_q75"], 0.0),
    )
    d["parent_correct"] = np.where(
        d["parent_signal"].ne(0),
        (d["parent_signal"].astype(int) == d["future_direction"].astype(int)).astype(float),
        np.nan,
    )
    return d.sort_values("origin_index").reset_index(drop=True)


def make_meta_model(spec: dict):
    if spec["model"] == "LOGIT":
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            StandardScaler(),
            LogisticRegression(
                C=float(spec["C"]),
                class_weight=str(spec["class_weight"]),
                max_iter=int(spec["max_iter"]),
                random_state=int(spec["random_state"]),
            ),
        )
    if spec["model"] == "HGB":
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            HistGradientBoostingClassifier(
                max_depth=int(spec["max_depth"]),
                max_iter=int(spec["max_iter"]),
                learning_rate=float(spec["learning_rate"]),
                l2_regularization=float(spec["l2_regularization"]),
                random_state=int(spec["random_state"]),
            ),
        )
    raise KeyError(spec["model"])


def mature_meta_training_indices(d: pd.DataFrame, row_pos: int, h: int, spec: dict) -> list[int]:
    current_origin = int(d.loc[row_pos, "origin_index"])
    idx = [
        j for j in range(row_pos)
        if int(d.loc[j, "parent_signal"]) != 0
        and pd.notna(d.loc[j, "parent_correct"])
        and int(d.loc[j, "origin_index"]) + h <= current_origin
    ]
    cap = int(spec["rolling_window"])
    return idx[-cap:]


def sequential_meta_trust(parent_frame: pd.DataFrame, candidate_id: str, contract: dict) -> pd.DataFrame:
    spec = contract["meta_candidates"][candidate_id]
    h = int(contract["target"]["primary_horizon_sessions"])
    base = list(contract["meta_features"]["BASE"])
    features = base if spec["feature_set"] == "BASE" else base + list(contract["corrected_driver_features"])
    threshold = float(contract["routing"]["trust_probability_min"])
    rows: list[dict[str, Any]] = []
    for i in range(len(parent_frame)):
        row = parent_frame.loc[i]
        signal = int(row["parent_signal"])
        p_correct = np.nan
        prior = np.nan
        train_n = 0
        if signal != 0:
            train = mature_meta_training_indices(parent_frame, i, h, spec)
            train_n = len(train)
            if train_n >= int(spec["minimum_mature_parent_signals"]):
                y = parent_frame.loc[train, "parent_correct"].astype(int)
                prior = float(y.mean())
                if y.nunique() >= 2:
                    model = make_meta_model(spec)
                    model.fit(parent_frame.loc[train, features], y)
                    p_correct = float(model.predict_proba(parent_frame.loc[[i], features])[0, 1])
                    if not math.isfinite(p_correct) or not (0.0 <= p_correct <= 1.0):
                        raise RuntimeError("V159_META_PROBABILITY_INVALID")
        final_dir = signal if signal != 0 and math.isfinite(p_correct) and p_correct >= threshold else 0
        rows.append({
            "origin_index": int(row["origin_index"]),
            "origin_date": row["origin_date"],
            "target_date": row["target_date"],
            "future_direction": int(row["future_direction"]),
            "target_return": float(row["target_return"]),
            "parent_signal": signal,
            "parent_correct": None if pd.isna(row["parent_correct"]) else int(row["parent_correct"]),
            "candidate_id": candidate_id,
            "p_parent_correct": None if not math.isfinite(p_correct) else p_correct,
            "prior_correct_frequency": None if not math.isfinite(prior) else prior,
            "train_n": int(train_n),
            "final_direction": int(final_dir),
        })
    return pd.DataFrame(rows)


def period_name(date: pd.Timestamp, target_date: pd.Timestamp, contract: dict) -> str:
    w = contract["windows"]
    periods = [
        ("FORMATION_2024", w["formation_score_start"], w["formation_score_end"]),
        ("VALIDATION_2025", w["validation_start"], w["validation_end"]),
        ("TEST_2026_AVAILABLE", w["test_start"], w["test_end"]),
    ]
    for label, a, b in periods:
        if pd.Timestamp(a) <= date <= pd.Timestamp(b) and target_date <= pd.Timestamp(b):
            return label
    return "OUTSIDE"


def direction_metrics(f: pd.DataFrame, signal_col: str) -> dict[str, Any]:
    if f.empty:
        return {"n": 0, "selective_n": 0, "coverage": 0.0, "status": "BLOCKED_EMPTY"}
    sig = f[signal_col].fillna(0).astype(int)
    take = sig.ne(0)
    g = f.loc[take]
    if g.empty:
        return {"n": int(len(f)), "selective_n": 0, "coverage": 0.0, "status": "NO_SIGNAL"}
    pred = (g[signal_col].astype(int) > 0).astype(int)
    y = (g["future_direction"].astype(int) > 0).astype(int)
    return {
        "n": int(len(f)),
        "selective_n": int(len(g)),
        "coverage": float(len(g) / len(f)),
        "selective_accuracy": float(accuracy_score(y, pred)),
        "selective_balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "mcc": float(matthews_corrcoef(y, pred)),
        "up_signals": int((g[signal_col] > 0).sum()),
        "down_signals": int((g[signal_col] < 0).sum()),
        "actual_up_rate_on_signals": float(y.mean()),
        "median_signed_realized_return": float(np.median(np.where(g[signal_col].astype(int) > 0, 1.0, -1.0) * g["target_return"].astype(float))),
    }


def trust_metrics(f: pd.DataFrame) -> dict[str, Any]:
    z = f[f["p_parent_correct"].notna() & f["prior_correct_frequency"].notna() & f["parent_correct"].notna()].copy()
    if z.empty:
        return {"n": 0, "status": "BLOCKED_EMPTY"}
    y = z["parent_correct"].astype(int).to_numpy()
    p = z["p_parent_correct"].astype(float).clip(1e-6, 1 - 1e-6).to_numpy()
    prior = z["prior_correct_frequency"].astype(float).clip(1e-6, 1 - 1e-6).to_numpy()
    pred = (p >= 0.5).astype(int)
    return {
        "n": int(len(z)),
        "correct_rate": float(np.mean(y)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, np.column_stack([1 - p, p]), labels=[0, 1])),
        "prior_frequency_brier": float(brier_score_loss(y, prior)),
        "prior_frequency_log_loss": float(log_loss(y, np.column_stack([1 - prior, prior]), labels=[0, 1])),
        "balanced_accuracy_at_0_5": float(balanced_accuracy_score(y, pred)),
        "mcc_at_0_5": float(matthews_corrcoef(y, pred)),
    }


def proper_nonworse_with_one_strict(m: dict[str, Any]) -> bool:
    if not m or m.get("n", 0) == 0:
        return False
    nonworse = m["brier"] <= m["prior_frequency_brier"] and m["log_loss"] <= m["prior_frequency_log_loss"]
    strict = m["brier"] < m["prior_frequency_brier"] or m["log_loss"] < m["prior_frequency_log_loss"]
    return bool(nonworse and strict)


def support_gate(final_by_period: dict[str, dict], legacy_by_period: dict[str, dict], trust_by_period: dict[str, dict], contract: dict) -> dict:
    r = contract["evaluation"]["support_rule_primary"]
    v = final_by_period["VALIDATION_2025"]
    t = final_by_period["TEST_2026_AVAILABLE"]
    lv = legacy_by_period["VALIDATION_2025"]
    lt = legacy_by_period["TEST_2026_AVAILABLE"]
    checks = {
        "validation_balanced_beats_legacy": v.get("selective_balanced_accuracy", -1) > lv.get("selective_balanced_accuracy", 2),
        "validation_mcc_positive": v.get("mcc", 0) > 0,
        "validation_both_directions": v.get("up_signals", 0) > 0 and v.get("down_signals", 0) > 0,
        "validation_coverage": v.get("coverage", 0) >= float(r["coverage_each_2025_2026_min"]),
        "validation_meta_proper": proper_nonworse_with_one_strict(trust_by_period["VALIDATION_2025"]),
        "test_balanced_min": t.get("selective_balanced_accuracy", 0) >= float(r["test_2026_balanced_min"]),
        "test_not_more_than_003_below_legacy": t.get("selective_balanced_accuracy", -1) >= lt.get("selective_balanced_accuracy", 2) - 0.03,
        "test_mcc_positive": t.get("mcc", 0) > 0,
        "test_both_directions": t.get("up_signals", 0) > 0 and t.get("down_signals", 0) > 0,
        "test_coverage": t.get("coverage", 0) >= float(r["coverage_each_2025_2026_min"]),
        "test_meta_proper": proper_nonworse_with_one_strict(trust_by_period["TEST_2026_AVAILABLE"]),
    }
    return {"pass": bool(all(checks.values())), "checks": checks}


def score_parent(parent_frame: pd.DataFrame, contract: dict) -> dict[str, dict]:
    d = parent_frame.copy()
    d["period"] = [period_name(pd.Timestamp(a), pd.Timestamp(b), contract) for a, b in zip(d["origin_date"], d["target_date"])]
    return {
        period: direction_metrics(d[d["period"].eq(period)], "parent_signal")
        for period in ["FORMATION_2024", "VALIDATION_2025", "TEST_2026_AVAILABLE"]
    }


def score_meta(meta: pd.DataFrame, contract: dict) -> tuple[dict[str, dict], dict[str, dict]]:
    d = meta.copy()
    d["period"] = [period_name(pd.Timestamp(a), pd.Timestamp(b), contract) for a, b in zip(d["origin_date"], d["target_date"])]
    direction = {}
    trust = {}
    for period in ["FORMATION_2024", "VALIDATION_2025", "TEST_2026_AVAILABLE"]:
        g = d[d["period"].eq(period)]
        direction[period] = direction_metrics(g, "final_direction")
        trust[period] = trust_metrics(g)
    return direction, trust


def ontology_ablation(results: dict[str, Any]) -> dict[str, Any]:
    base = results["meta_candidates"].get("META_BASE_LOGIT", {})
    driver = results["meta_candidates"].get("META_DRIVER_LOGIT", {})
    out: dict[str, Any] = {}
    for p in ["VALIDATION_2025", "TEST_2026_AVAILABLE"]:
        try:
            bd = base["direction"][p]
            dd = driver["direction"][p]
            bt = base["trust"][p]
            dt = driver["trust"][p]
            out[p] = {
                "balanced_accuracy_delta_driver_minus_base": dd.get("selective_balanced_accuracy", np.nan) - bd.get("selective_balanced_accuracy", np.nan),
                "coverage_delta_driver_minus_base": dd.get("coverage", np.nan) - bd.get("coverage", np.nan),
                "trust_brier_gain_base_minus_driver": bt.get("brier", np.nan) - dt.get("brier", np.nan),
                "trust_logloss_gain_base_minus_driver": bt.get("log_loss", np.nan) - dt.get("log_loss", np.nan),
            }
        except KeyError:
            out[p] = {"status": "BLOCKED_MISSING"}
    return out


def main() -> int:
    contract = load_contract()
    database_url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not database_url:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")

    driver_frames, driver_evidence = build_driver_source(contract)
    v157_contract = json.loads(V157_CONTRACT_PATH.read_text(encoding="utf-8"))
    with psycopg.connect(database_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
        panel, base_features, _, _ = v157.build_panel(conn, v157_contract)

    panel = add_corrected_drivers(panel, driver_frames, contract)
    panel = v158.emergency_research_context(panel, v158.load_patch_references(), v158.load_contract())
    h = int(contract["target"]["primary_horizon_sessions"])
    routed = v158.add_router_target(panel, h)

    legacy_raw = legacy_rtq_parent(panel, base_features)
    corrected_features = corrected_parent_features(base_features, contract)
    driver_raw = corrected_rtq_parent(panel, corrected_features, contract)
    legacy = prepare_parent_frame(legacy_raw, routed, contract)
    driver = prepare_parent_frame(driver_raw, routed, contract)

    results: dict[str, Any] = {
        "contract_id": contract["contract_id"],
        "status": "RETROSPECTIVE_SUCCESSOR_DIAGNOSTIC_COMPLETE",
        "evidence_class": contract["evidence_class"],
        "production_authority": False,
        "driver_source_evidence": driver_evidence,
        "parent_feature_audit": {
            "legacy_feature_count": int(len(base_features)),
            "driver_corrected_feature_count": int(len(corrected_features)),
            "legacy_generic_fx_columns_removed_from_corrected_parent": ["fx_level", "fx_logdiff"],
            "corrected_driver_features_added": list(contract["corrected_driver_features"]),
        },
        "parent_experts": {
            "LEGACY_RTQ_R126": score_parent(legacy, contract),
            "DRIVER_RTQ_R126": score_parent(driver, contract),
        },
        "meta_candidates": {},
    }

    prediction_blocks = []
    legacy_period = results["parent_experts"]["LEGACY_RTQ_R126"]
    for cid in contract["meta_candidates"]:
        meta = sequential_meta_trust(driver, cid, contract)
        direction, trust = score_meta(meta, contract)
        block = {"direction": direction, "trust": trust}
        if cid == "META_DRIVER_LOGIT":
            block["support_gate_primary"] = support_gate(direction, legacy_period, trust, contract)
        results["meta_candidates"][cid] = block
        x = meta.copy()
        x["meta_candidate"] = cid
        prediction_blocks.append(x)

    results["ontology_ablation"] = ontology_ablation(results)
    results["interpretation_lock"] = {
        "h20_is_primary": True,
        "legacy_DEXCHUS_is_not_a_broad_USD_factor": True,
        "meta_layer_can_veto_but_never_flip": True,
        "NO_SIGNAL_is_not_NEUTRAL": True,
        "2025_2026_are_researcher_visible": True,
        "future_prospective_shadow_required": True,
        "post_score_changes_forbidden_inside_V159": True,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT / "v159_driver_corrected_panel.csv", index=False)
    pd.concat([
        legacy.assign(parent_id="LEGACY_RTQ_R126"),
        driver.assign(parent_id="DRIVER_RTQ_R126"),
    ], ignore_index=True).to_csv(OUT / "v159_parent_predictions.csv", index=False)
    if prediction_blocks:
        pd.concat(prediction_blocks, ignore_index=True).to_csv(OUT / "v159_meta_predictions.csv", index=False)
    source_rows = []
    for sid, frame in driver_frames.items():
        z = frame.copy()
        z["series_id"] = sid
        source_rows.append(z)
    pd.concat(source_rows, ignore_index=True).to_csv(OUT / "v159_fred_driver_reconstruction.csv", index=False)
    (OUT / "v159_results.json").write_text(json.dumps(results, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(results, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
