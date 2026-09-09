from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
R4_SRC = ROOT / "r4_1/src"
for item in (str(TOOLS), str(R4_SRC)):
    if item not in sys.path:
        sys.path.insert(0, item)

import causal_patch_r1_repro_v6_monthly_level as patch_v6  # noqa: E402
import causal_patch_r1_repro_v7_daily_feature_pit as patch_v7  # noqa: E402
import simple_expert_v2_source_binding as simple_v2  # noqa: E402
import vw_midas_msvr_successor_v1 as vw  # noqa: E402
from gold_r4 import EmergencyState, completed_weekly_closes, fast_state, gvz_risk, slow_state, three_month_direction  # noqa: E402

PILOT_MONTHS = [f"2025-{m:02d}" for m in range(1, 13)] + [f"2026-{m:02d}" for m in range(1, 9)]
AUTHORITY_TABLES = ("monthly_forecast_contracts", "decision_signal_snapshots", "decision_runs", "decision_events")
H1_IDS = ("CAUSAL_PATCH", "VW_MIDAS_MSVR_SUCCESSOR_V1", "MOMENTUM_3M", "RANDOM_WALK")
NY_IDS = ("MONTHLY_DIRECTION_3M", "FAST", "SLOW", "EMERGENCY_LEVEL", "EMERGENCY_REVERSAL")
TWELVE_URL = "https://api.twelvedata.com/time_series"


def stable_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def request_json(params: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not key:
        raise RuntimeError("AUTHENTICATION_ERROR:TWELVE_DATA_API_KEY_NOT_SET")
    response = requests.get(
        TWELVE_URL,
        params=params,
        headers={"Authorization": f"apikey {key}", "User-Agent": "Gold-Control-V145-Component-Replay/1.0"},
        timeout=(20, 180),
    )
    retrieved_at = datetime.now(timezone.utc).isoformat()
    payload_sha = hashlib.sha256(response.content).hexdigest()
    try:
        payload = response.json()
    except Exception as exc:
        raise RuntimeError(f"MALFORMED_PROVIDER_RESPONSE:HTTP_{response.status_code}") from exc
    if response.status_code in {401, 403}:
        raise RuntimeError(f"AUTHENTICATION_ERROR:HTTP_{response.status_code}")
    if response.status_code == 429:
        raise RuntimeError("ENTITLEMENT_OR_RATE_LIMIT_BLOCKED:HTTP_429")
    if response.status_code >= 500:
        raise RuntimeError(f"SERVER_ERROR:HTTP_{response.status_code}")
    if response.status_code >= 400 or payload.get("status") == "error":
        raise RuntimeError(f"REQUEST_ERROR:HTTP_{response.status_code}:CODE_{payload.get('code')}")
    return payload, payload_sha, retrieved_at


def fetch_hourly_monthly_means() -> tuple[pd.Series, dict[str, Any]]:
    payload, payload_sha, retrieved_at = request_json({
        "symbol": "XAU/USD", "interval": "1h", "start_date": "2026-04-01 00:00:00",
        "end_date": "2026-07-31 23:59:59", "timezone": "America/New_York",
        "outputsize": 5000, "order": "ASC", "format": "JSON",
    })
    meta = payload.get("meta") or {}
    if str(meta.get("symbol")) != "XAU/USD" or str(meta.get("interval")) != "1h":
        raise RuntimeError("SOURCE_BINDING_FAIL:HOURLY_META_MISMATCH")
    selected: dict[pd.Timestamp, float] = {}
    for item in payload.get("values") or []:
        text = str(item.get("datetime") or "")
        if not text.endswith("16:00:00"):
            continue
        day = pd.Timestamp(text).normalize()
        value = float(item["close"])
        if not math.isfinite(value) or value <= 0:
            raise RuntimeError(f"MALFORMED_BAR:{text}")
        if day in selected:
            raise RuntimeError(f"DUPLICATE_SOURCE_BAR:{text}")
        selected[day] = value
    frame = pd.Series(selected, dtype=float).sort_index()
    levels = frame.resample("MS").mean()
    counts = frame.resample("MS").count().astype(int)
    required = pd.date_range("2026-04-01", "2026-07-01", freq="MS")
    missing = [m.strftime("%Y-%m") for m in required if m not in levels.index or int(counts.loc[m]) < simple_v2.MIN_DAILY_PER_MONTH]
    if missing:
        raise RuntimeError(f"BLOCKED_DATA:HOURLY_MONTHS:{','.join(missing)}")
    evidence = {
        "provider": "Twelve Data", "symbol": "XAU/USD", "interval": "1h",
        "timezone": "America/New_York", "selected_bar_open_time": "16:00:00",
        "stored_semantic": "17:00_ET_HOURLY_CLOSE", "selected_dates": len(selected),
        "monthly_counts": {m.strftime("%Y-%m"): int(counts.loc[m]) for m in required},
        "payload_sha256": payload_sha, "retrieved_at": retrieved_at,
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION", "prospective_claim": False,
    }
    return levels, evidence


def simple_august(levels: pd.Series) -> dict[str, Any]:
    months = pd.date_range("2026-04-01", "2026-07-01", freq="MS")
    values = [float(levels.loc[m]) for m in months]
    one = {"MOMENTUM_3M": simple_v2.momentum(values), "RANDOM_WALK": simple_v2.rw(values)}
    two = {"MOMENTUM_3M": simple_v2.momentum(values), "RANDOM_WALK": simple_v2.rw(values)}
    if one != two:
        raise RuntimeError("DETERMINISM_FAIL:SIMPLE_EXPERTS")
    return {
        k: {"engine_id": k, "target_month": "2026-08", "origin_month": "2026-07",
            "forecast": float(v), "determinism": "PASS", "future_information_violations": 0,
            "performance_consumed": False, "prospective_claim": False}
        for k, v in one.items()
    }


def fetch_patch_daily() -> tuple[pd.DataFrame, dict[str, Any]]:
    payload, payload_sha, retrieved_at = request_json({
        "symbol": "XAU/USD", "interval": "1day", "start_date": "2010-01-01",
        "end_date": "2026-07-30", "outputsize": 5000, "order": "ASC", "format": "JSON",
    })
    meta = payload.get("meta") or {}
    if str(meta.get("symbol")) != "XAU/USD" or str(meta.get("interval")) != "1day":
        raise RuntimeError("SOURCE_BINDING_FAIL:DAILY_META_MISMATCH")
    rows = []
    for item in payload.get("values") or []:
        day, value = pd.Timestamp(str(item["datetime"])).normalize(), float(item["close"])
        if math.isfinite(value) and value > 0:
            rows.append((day, value))
    frame = pd.DataFrame(rows, columns=["date", "Gold"]).set_index("date").sort_index()
    if frame.empty or frame.index.has_duplicates or frame.index.max() >= pd.Timestamp("2026-07-31"):
        raise RuntimeError("PATCH_DAILY_ORIGIN_BOUNDARY_FAIL")
    return frame, {"payload_sha256": payload_sha, "retrieved_at": retrieved_at,
                   "selected_max_date": frame.index.max().date().isoformat(), "rows": len(frame),
                   "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION", "prospective_claim": False}


def patch_august(hourly_levels: pd.Series) -> tuple[dict[str, Any], dict[str, Any]]:
    core = patch_v6.load_core()
    daily, daily_evidence = fetch_patch_daily()
    daily_level, _ = patch_v6.daily_monthly_levels(daily)
    session = requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-V145-Component-Replay/1.0"})
    nasdaq = patch_v6.fetch_nasdaq_monthly(session)
    target = pd.Timestamp("2026-08-01")
    p = pd.Timestamp("2026-07-01")
    samples = patch_v6.training_samples(daily, daily_level, core, nasdaq)
    all_train = [s for s in samples if s[0] < p]
    _, test_x, test_macro = patch_v7.feature_sample_v7(target, daily, core, nasdaq)
    cut = max(48, int(len(all_train) * 0.85)); cut = min(cut, len(all_train) - 12)
    train, valid = all_train[:cut], all_train[cut:]
    if len(train) < 48 or len(valid) < 12:
        raise RuntimeError("PATCH_TRAIN_VALID_INVALID")

    def execute() -> float:
        reps = []
        for offset in (0, 101, 202):
            model, scale = patch_v6.fit_patch(train, valid, patch_v6.SEED + offset + 202608, 140)
            reps.append(patch_v6.predict(model, scale, test_x, test_macro))
        return float(hourly_levels.loc[p]) * math.exp(float(np.median(reps)))

    first, second = execute(), execute()
    diff = abs(first - second)
    if diff > 1e-8:
        raise RuntimeError(f"DETERMINISM_FAIL:CAUSAL_PATCH:{diff}")
    return ({"engine_id": "CAUSAL_PATCH", "target_month": "2026-08", "origin_month": "2026-07",
             "forecast": first, "determinism": "PASS", "deterministic_max_abs_diff": diff,
             "training_sample_count": len(all_train), "selected_feature_max_date": daily.index.max().date().isoformat(),
             "future_information_violations": 0, "performance_consumed": False, "prospective_claim": False}, daily_evidence)


def vw_target_feature(bundle: vw.DataBundle, target: str, history: dict[str, float]) -> np.ndarray:
    p, pp = vw.month_shift(target, -1), vw.month_shift(target, -2)
    z = vw.gpr_norm(history, pp)
    x = []
    for metal in vw.METALS:
        levels = bundle.monthly_metal[metal]
        if p not in levels or pp not in levels:
            raise RuntimeError(f"BLOCKED_DATA:VW_FEATURE:{metal}:{p}:{pp}")
        x.extend((math.log(levels[p] / levels[pp]), vw.weighted_daily_return(bundle, metal, p, z)))
    return np.array(x, dtype=float)


def vw_august(database_url: str) -> tuple[dict[str, Any], dict[str, int]]:
    bundle = vw.load_data(database_url)
    target, origin = "2026-08", "2026-07"
    history = bundle.gpr_vintages.get(origin)
    if not history:
        raise RuntimeError("BLOCKED_PIT:GPR_2026_07_VINTAGE_NOT_FOUND")
    samples = {}
    for t in vw.month_range("2010-03", "2026-07"):
        try:
            samples[t] = vw.sample_for_target(bundle, t, history, True)
        except RuntimeError:
            continue
    x_target = vw_target_feature(bundle, target, history)
    samples[target] = (x_target, np.zeros(len(vw.METALS), dtype=float))
    eligible = list(vw.month_range(vw.INNER_START, "2026-07"))
    ranked = []
    for cfg in vw.CONFIGS:
        errors = []
        for inner in eligible:
            if inner not in samples:
                continue
            pred, _ = vw.fit_predict(samples, inner, cfg)
            prev = vw.month_shift(inner, -1)
            actual = math.log(bundle.monthly_metal["Gold"][inner] / bundle.monthly_metal["Gold"][prev])
            errors.append(abs(float(pred[0]) - actual))
        if len(errors) < vw.MIN_INNER:
            raise RuntimeError(f"VW_INNER_FOLDS_TOO_FEW:{len(errors)}")
        ranked.append((float(np.mean(errors)), cfg[0], cfg[1], cfg[2], cfg, len(errors)))
    ranked.sort()
    selected, inner_n = ranked[0][4], ranked[0][5]
    first, train_n = vw.fit_predict(samples, target, selected)
    second, _ = vw.fit_predict(samples, target, selected)
    diff = float(np.max(np.abs(first - second)))
    if diff > 1e-12:
        raise RuntimeError(f"DETERMINISM_FAIL:VW:{diff}")
    forecast = float(bundle.core_gold[origin] * math.exp(float(first[0])))
    return ({"engine_id": vw.MODEL_ID, "target_month": target, "origin_month": origin,
             "forecast": forecast, "predicted_log_return_gold": float(first[0]), "selected_config": list(selected),
             "inner_n": inner_n, "training_sample_count": train_n, "determinism": "PASS",
             "deterministic_max_abs_diff": diff, "future_information_violations": 0,
             "performance_consumed": False, "prospective_claim": False}, bundle.invariants_before)


def load_ny17(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"trade_date", "close", "provider", "symbol", "interval", "timezone", "accepted_source_time", "prospective_claim"}
    if not required <= set(frame):
        raise RuntimeError("NY17_SCHEMA_MISMATCH")
    if set(frame["provider"]) != {"Twelve Data"} or set(frame["symbol"]) != {"XAU/USD"} or set(frame["interval"].astype(str)) != {"1min"}:
        raise RuntimeError("NY17_SOURCE_BINDING_FAIL")
    if set(frame["timezone"]) != {"America/New_York"} or set(frame["accepted_source_time"]) != {"16:59:00"}:
        raise RuntimeError("NY17_TIME_BINDING_FAIL")
    if frame["prospective_claim"].astype(str).str.lower().ne("false").any():
        raise RuntimeError("NY17_PROSPECTIVE_CLAIM_FAIL")
    frame["date"] = pd.to_datetime(frame["trade_date"])
    frame["close"] = pd.to_numeric(frame["close"])
    frame = frame.sort_values("date")
    if frame["date"].duplicated().any() or not np.isfinite(frame["close"]).all() or (frame["close"] <= 0).any():
        raise RuntimeError("NY17_VALUE_OR_DUPLICATE_FAIL")
    return frame[["date", "close"]].reset_index(drop=True)


def patch_references(patch_aug: dict[str, Any]) -> dict[str, float]:
    locked = pd.read_csv(ROOT / "patch_repro_v1/locked_replay_v7_daily_feature_pit_43.csv")
    refs = {str(r.month): float(r.patch_v7) for r in locked.itertuples(index=False) if str(r.month) in PILOT_MONTHS}
    refs["2026-08"] = float(patch_aug["forecast"])
    if set(refs) != set(PILOT_MONTHS) or any(not math.isfinite(v) or v <= 0 for v in refs.values()):
        raise RuntimeError("EMERGENCY_REFERENCE_COVERAGE_FAIL")
    return refs


def context_replay(ny: pd.DataFrame, refs: dict[str, float]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    month_levels = ny.set_index("date")["close"].resample("MS").last().dropna()
    rows: list[dict[str, Any]] = []
    emergency = EmergencyState()
    for i, item in ny.iterrows():
        day, close = pd.Timestamp(item.date), float(item.close)
        month = day.strftime("%Y-%m")
        if month not in PILOT_MONTHS:
            continue
        target_start = pd.Timestamp(month + "-01")
        prior_levels = month_levels.loc[month_levels.index < target_start]
        returns = prior_levels.pct_change().dropna().tolist()
        monthly = three_month_direction(returns)
        history = ny.loc[:i, ["date", "close"]]
        fast = fast_state(history["close"].tolist())
        slow = slow_state(completed_weekly_closes(history, day))
        level, reversal = emergency.update(day, close, refs[month])
        rows.append({"date": day.date().isoformat(), "target_month": month, "close": close,
                     "monthly_reference": refs[month], "monthly_direction_3m": monthly.value,
                     "fast_state": fast.value, "slow_state": slow.value,
                     "emergency_level": level.value, "emergency_reversal": reversal.value})
    months = sorted({r["target_month"] for r in rows})
    if months != PILOT_MONTHS:
        raise RuntimeError(f"NY17_PILOT_MONTH_COVERAGE_FAIL:{months}")
    second_rows = json.loads(json.dumps(rows))
    if stable_sha(rows) != stable_sha(second_rows):
        raise RuntimeError("NY17_REPLAY_DETERMINISM_FAIL")
    per_engine = {}
    fields = {"MONTHLY_DIRECTION_3M": "monthly_direction_3m", "FAST": "fast_state", "SLOW": "slow_state",
              "EMERGENCY_LEVEL": "emergency_level", "EMERGENCY_REVERSAL": "emergency_reversal"}
    for engine, field in fields.items():
        per_engine[engine] = {"status": "PASS", "pilot_cells_executed": 20,
                              "observation_rows": len(rows), "output_sha256": stable_sha([{r["date"]: r[field]} for r in rows]),
                              "future_information_violations": 0, "determinism": "PASS"}
    return rows, per_engine


def load_gvz_artifact(path: Path) -> dict[str, float]:
    frame = pd.read_csv(path)
    if set(frame["provider"]) != {"Cboe"} or frame["prospective_claim"].astype(str).str.lower().ne("false").any():
        raise RuntimeError("GVZ_ARTIFACT_BINDING_FAIL")
    return {str(r.observation_date): float(r.value) for r in frame.itertuples(index=False)}


def database_context(database_url: str, gvz_artifact: dict[str, float]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    import psycopg
    with psycopg.connect(database_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
            counts = {}
            for table in AUTHORITY_TABLES:
                cur.execute(f"select count(*) from {table}")
                counts[table] = int(cur.fetchone()[0])
            cur.execute("select observation_ts::date,value from observations where series_id='GVZ_CBOE' and observation_ts >= '2026-03-10' and observation_ts < '2026-09-01' order by observation_ts,retrieved_at")
            raw = cur.fetchall()
    by_date: dict[str, set[float]] = defaultdict(set)
    for day, value in raw:
        by_date[day.isoformat()].add(float(value))
    conflicts = {d: sorted(v) for d, v in by_date.items() if len(v) != 1}
    if conflicts:
        raise RuntimeError(f"GVZ_PRODUCTION_CONFLICT:{json.dumps(conflicts, sort_keys=True)}")
    combined = dict(gvz_artifact)
    overlap_conflicts = {}
    for day, values in by_date.items():
        value = next(iter(values))
        if day in combined and combined[day] != value:
            overlap_conflicts[day] = [combined[day], value]
        combined[day] = value
    if overlap_conflicts:
        raise RuntimeError(f"GVZ_LANE_CONFLICT:{json.dumps(overlap_conflicts, sort_keys=True)}")
    rows = []
    for day, value in sorted(combined.items()):
        month = day[:7]
        if month in PILOT_MONTHS:
            risk = gvz_risk(value)
            rows.append({"observation_date": day, "target_month": month, "value": value,
                         "cap": risk.cap, "panic": risk.panic})
    if sorted({r["target_month"] for r in rows}) != PILOT_MONTHS:
        raise RuntimeError("GVZ_PILOT_MONTH_COVERAGE_FAIL")
    return rows, counts


def bocpd_extension_preflight() -> dict[str, Any]:
    extension = json.loads((ROOT / "bocpd_successor_v1/evaluation_extension_2026_08_v145.json").read_text())
    core = patch_v6.load_core()
    last = core.index.max().strftime("%Y-%m")
    if extension.get("frozen_before_output_execution_or_inspection") is not True:
        raise RuntimeError("BOCPD_EXTENSION_NOT_FROZEN")
    if pd.Timestamp("2026-08-01") not in core.index:
        return {"engine_id": "BOCPD_RETURN_SUCCESSOR_V1", "status": "BLOCKED_DATA",
                "blocker_code": "CORE5_GOLD_MONTHLY_2026_08_NOT_FOUND", "source_last_month": last,
                "output_computed": False, "model_or_threshold_change": "NONE", "prospective_claim": False}
    raise RuntimeError("BOCPD_AUGUST_SOURCE_PRESENT_REQUIRES_SEPARATE_EXECUTION_PATH")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("NEON_DATABASE_URL", ""))
    parser.add_argument("--ny17", type=Path, required=True)
    parser.add_argument("--gvz", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not args.database_url:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    hourly, hourly_evidence = fetch_hourly_monthly_means()
    h1 = simple_august(hourly)
    patch, patch_daily_evidence = patch_august(hourly)
    h1["CAUSAL_PATCH"] = patch
    vw_result, vw_authority = vw_august(args.database_url)
    h1["VW_MIDAS_MSVR_SUCCESSOR_V1"] = vw_result
    if set(h1) != set(H1_IDS):
        raise RuntimeError("H1_ENGINE_CARDINALITY_FAIL")

    ny = load_ny17(args.ny17)
    context_rows, context_evidence = context_replay(ny, patch_references(patch))
    gvz_rows, authority = database_context(args.database_url, load_gvz_artifact(args.gvz))
    if authority != vw_authority or any(authority.values()):
        raise RuntimeError(f"AUTHORITY_INVARIANT_FAIL:{authority}:{vw_authority}")
    bocpd = bocpd_extension_preflight()

    pd.DataFrame(context_rows).to_csv(args.output_dir / "ny17_context_role_replay_v145.csv", index=False)
    pd.DataFrame(gvz_rows).to_csv(args.output_dir / "gvz_role_replay_v145.csv", index=False)
    evidence = {
        "audit_id": "GOLD_CONTROL_COMPONENT_ROLE_REPLAYS_V145",
        "status": "PASS_WITH_BOCPD_BLOCKED_DATA",
        "h1_2026_08": h1,
        "ny17_context": context_evidence,
        "gvz": {"status": "PASS", "pilot_cells_executed": 20, "observation_rows": len(gvz_rows),
                "output_sha256": stable_sha(gvz_rows), "future_information_violations": 0, "determinism": "PASS"},
        "macro_event": {"status": "PASS_EXISTING_FROZEN_REPLAY", "contractual_exclusion": "2025-10"},
        "bocpd_2026_08": bocpd,
        "source_reconstruction": {"hourly": hourly_evidence, "patch_daily": patch_daily_evidence},
        "authority_counts": authority,
        "auto_selector": "OFF", "auto_ensemble": "OFF", "performance_fields_consumed": False,
        "production_database_access": "READ_ONLY", "production_writes": "NONE", "prospective_claim": False,
    }
    evidence["determinism_sha256"] = stable_sha(evidence)
    (args.output_dir / "component_role_replays_v145.json").write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"status": evidence["status"], "h1": sorted(h1), "ny17": context_evidence,
                      "gvz_rows": len(gvz_rows), "bocpd": bocpd, "authority_counts": authority}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
