from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import requests
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
R4_SRC = ROOT / "r4_1" / "src"
for path in (TOOLS, R4_SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import bocpd_return_successor_v1 as bocpd  # noqa: E402
import causal_patch_r1_repro_v6_monthly_level as v6  # noqa: E402
import causal_patch_r1_repro_v7_daily_feature_pit as v7  # noqa: E402
import stage4b_patch_v7_runner_core as patch_core  # noqa: E402

CONTRACT = ROOT / "GOLD_CONTROL_AUG31_REPLAY_EXPANSION_V2_CHANGE_CONTROL_2026-09-04.md"
CONTRACT_MARKER = "FROZEN_BEFORE_AUG31_EXPANSION_RESULT"
V6_EVIDENCE = ROOT / "patch_repro_v1" / "locked_replay_v6_monthly_level_evidence.json"
ORIGIN_TS = datetime(2026, 8, 31, 21, 0, tzinfo=timezone.utc)
ORIGIN_DATE = pd.Timestamp("2026-08-31")
TARGET = pd.Timestamp("2026-09-01")
TARGET_CONTEXT = "2026-09"
PATCH_ID = "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE"
BOCPD_CONTEXT_ID = "BOCPD_RETURN_SUCCESSOR_V1_AUG31_CONTEXT_BRIDGE_V1"
EVIDENCE_CLASS = "HISTORICAL_REPLAY"
BOCPD_EVIDENCE = "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT"


def git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def canonical_hash(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def authority_counts(cur) -> dict[str, int]:
    out = {}
    for table in ("monthly_forecast_contracts", "decision_signal_snapshots", "decision_runs", "decision_events"):
        cur.execute(f"select count(*) as n from {table}")
        out[table] = int(cur.fetchone()["n"])
    return out


def operational_state(cur) -> dict:
    cur.execute("select runtime_status,count(*) as n from latest_engine_runtime_state group by runtime_status")
    counts = {str(r["runtime_status"]): int(r["n"]) for r in cur.fetchall()}
    cur.execute("select count(*) as n from latest_engine_runtime_state where direction_vote_permitted")
    votes = int(cur.fetchone()["n"])
    return {"counts": counts, "direction_votes": votes}


def fetch_nasdaq_asof(session: requests.Session) -> pd.Series:
    payload = patch_core.request_json(
        session,
        patch_core.FRED_URL,
        {
            "series_id": "NASDAQCOM",
            "api_key": patch_core.env("FRED_API_KEY"),
            "file_type": "json",
            "realtime_start": ORIGIN_DATE.date().isoformat(),
            "realtime_end": ORIGIN_DATE.date().isoformat(),
            "observation_start": "2010-01-01",
            "observation_end": ORIGIN_DATE.date().isoformat(),
            "sort_order": "asc",
            "limit": 100000,
        },
        {"User-Agent": "Gold-Control-Aug31-Replay-V2/1.0"},
    )
    rows = []
    for z in payload.get("observations") or []:
        raw = str(z.get("value", "."))
        if raw in {".", "", "nan", "None"}:
            continue
        try:
            d = pd.Timestamp(str(z.get("date"))).normalize()
            value = float(raw)
        except Exception:
            continue
        if d <= ORIGIN_DATE and np.isfinite(value) and value > 0:
            rows.append((d, value))
    frame = pd.DataFrame(rows, columns=["date", "value"]).sort_values("date")
    if frame.empty or frame.duplicated("date").any():
        raise RuntimeError("AUG31_REPLAY_NASDAQ_ASOF_INVALID")
    monthly = frame.set_index("date")["value"].resample("MS").mean().dropna()
    for required in (pd.Timestamp("2026-06-01"), pd.Timestamp("2026-07-01")):
        if required not in monthly.index:
            raise RuntimeError(f"AUG31_REPLAY_NASDAQ_REQUIRED_MONTH_MISSING:{required.date()}")
    return monthly


def training_samples_through_july(xau_daily: pd.DataFrame, daily_level: pd.Series, core: pd.DataFrame, nasdaq: pd.Series) -> list[tuple]:
    samples = []
    for target in pd.date_range("2011-03-01", "2026-07-01", freq="MS"):
        p = target - pd.offsets.MonthBegin(1)
        if target not in daily_level.index or p not in daily_level.index:
            continue
        try:
            _, x, macro = v7.feature_sample_v7(target, xau_daily, core, nasdaq)
        except RuntimeError:
            continue
        y = float(np.log(float(daily_level.loc[target]) / float(daily_level.loc[p])))
        samples.append((target, x, macro, y))
    if not samples or samples[-1][0] != pd.Timestamp("2026-07-01"):
        raise RuntimeError("AUG31_REPLAY_TRAINING_DOES_NOT_REACH_2026_07")
    return samples


def patch_replay_once(source_bundle: dict | None = None) -> dict:
    core = v6.load_core()
    session = requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-Aug31-Replay-V2/1.0"})

    if source_bundle is None:
        xau_daily = patch_core.fetch_xau_daily(session, ORIGIN_DATE)
        nasdaq = fetch_nasdaq_asof(session)
        fed_aug, fed_meta = patch_core.fred_month_mean_asof(session, "DFF", pd.Timestamp("2026-08-01"))
        fx_aug, fx_aug_meta = patch_core.fred_month_mean_asof(session, "DEXCHUS", pd.Timestamp("2026-08-01"))
        anchor, anchor_meta = patch_core.fetch_hourly_anchor(session, ORIGIN_DATE)
        source_bundle = {
            "xau_daily": xau_daily,
            "nasdaq": nasdaq,
            "fed_aug": fed_aug,
            "fed_meta": fed_meta,
            "fx_aug": fx_aug,
            "fx_aug_meta": fx_aug_meta,
            "anchor": anchor,
            "anchor_meta": anchor_meta,
        }
    else:
        xau_daily = source_bundle["xau_daily"]
        nasdaq = source_bundle["nasdaq"]
        fed_aug = source_bundle["fed_aug"]
        fed_meta = source_bundle["fed_meta"]
        fx_aug = source_bundle["fx_aug"]
        fx_aug_meta = source_bundle["fx_aug_meta"]
        anchor = source_bundle["anchor"]
        anchor_meta = source_bundle["anchor_meta"]

    daily_level, daily_count = v6.daily_monthly_levels(xau_daily)
    august = pd.Timestamp("2026-08-01")
    if august not in daily_level.index or int(daily_count.loc[august]) < 15:
        raise RuntimeError("AUG31_REPLAY_AUGUST_DAILY_LEVEL_NOT_COMPLETE")

    core_ext = core.copy()
    if august not in core_ext.index:
        core_ext.loc[august] = np.nan
    core_ext.loc[august, "fedfunds"] = fed_aug
    core_ext.loc[august, "usdcny"] = fx_aug
    core_ext = core_ext.sort_index()

    training = training_samples_through_july(xau_daily, daily_level, core, nasdaq)
    _, test_x, test_macro = v7.feature_sample_v7(TARGET, xau_daily, core_ext, nasdaq)

    daily_returns = np.log(xau_daily[["Gold"]]).diff().dropna()
    selected = daily_returns.loc[daily_returns.index < ORIGIN_DATE].iloc[-252:]
    if len(selected) != 252 or not bool(selected.index.max() < ORIGIN_DATE):
        raise RuntimeError("AUG31_REPLAY_PATCH_DAILY_PIT_FAIL")

    cut = max(48, int(len(training) * 0.85))
    cut = min(cut, len(training) - 12)
    train, valid = training[:cut], training[cut:]
    if len(train) < 48 or len(valid) < 12:
        raise RuntimeError("AUG31_REPLAY_PATCH_TRAIN_VALID_INVALID")

    reps = []
    for offset in (0, 101, 202):
        model, scale = v6.fit_patch(train, valid, v6.SEED + offset + int(TARGET.strftime("%Y%m")), 140)
        reps.append(v6.predict(model, scale, test_x, test_macro))
    predicted_return = float(np.median(reps))
    forecast = float(anchor * math.exp(predicted_return))
    if not np.isfinite(forecast) or forecast <= 0:
        raise RuntimeError("AUG31_REPLAY_PATCH_FORECAST_INVALID")

    fingerprint_payload = {
        "model": PATCH_ID,
        "origin": ORIGIN_TS.isoformat(),
        "target": TARGET_CONTEXT,
        "training_n": len(training),
        "cut": cut,
        "test_x_sha": hashlib.sha256(np.asarray(test_x, np.float32).tobytes()).hexdigest(),
        "test_macro": [float(v) for v in test_macro],
        "anchor": float(anchor),
        "daily_max_date": selected.index.max().date().isoformat(),
    }
    return {
        "forecast": forecast,
        "predicted_return": predicted_return,
        "training_n": len(training),
        "training_cut": cut,
        "daily_max_date": selected.index.max().date().isoformat(),
        "test_macro": [float(v) for v in test_macro],
        "anchor": float(anchor),
        "input_fingerprint": canonical_hash(fingerprint_payload),
        "august_daily_level": float(daily_level.loc[august]),
        "august_daily_count": int(daily_count.loc[august]),
        "source_meta": {
            "fed_aug": fed_meta,
            "fx_aug": fx_aug_meta,
            "anchor": anchor_meta,
            "retrieved_post_origin": True,
            "nasdaq_realtime_asof": ORIGIN_DATE.date().isoformat(),
        },
        "source_bundle": source_bundle,
    }


def build_bocpd_context(patch: dict) -> dict:
    contract = bocpd.load_contract()
    core = bocpd.load_core_monthly()
    price = core["gold_monthly"].astype(float).copy()
    august = pd.Timestamp("2026-08-01")
    bridge_used = False

    if august not in price.index:
        v6e = json.loads(V6_EVIDENCE.read_text(encoding="utf-8"))
        if v6e.get("source_gate") != "PATCH_MONTHLY_LEVEL_BRIDGE_V6_SOURCE_PASS" or not v6e.get("model_impact_pass"):
            raise RuntimeError("AUG31_REPLAY_BOCPD_CONTEXT_BRIDGE_PARENT_NOT_PASS")
        if int(patch["august_daily_count"]) < 15:
            raise RuntimeError("AUG31_REPLAY_BOCPD_CONTEXT_BRIDGE_AUGUST_COUNT_FAIL")
        price.loc[august] = float(patch["august_daily_level"])
        bridge_used = True
    elif not np.isfinite(float(price.loc[august])) or float(price.loc[august]) <= 0:
        raise RuntimeError("AUG31_REPLAY_BOCPD_AUGUST_CORE5_INVALID")

    price = price.sort_index().loc[:august]
    returns = np.log(price / price.shift(1)).dropna()
    prior = bocpd.fit_development_prior(returns, contract)
    expected_run_length = int(contract["hazard"]["expected_run_length_months"])
    rows = bocpd.run_bocpd(returns.loc[pd.Timestamp(contract["windows"]["development_start"]):august], prior, expected_run_length, contract)
    if august not in rows.index:
        raise RuntimeError("AUG31_REPLAY_BOCPD_AUGUST_STATE_MISSING")
    row = rows.loc[august]

    # deterministic repeat with identical frozen inputs
    rows2 = bocpd.run_bocpd(returns.loc[pd.Timestamp(contract["windows"]["development_start"]):august], prior, expected_run_length, contract)
    cols = ["log_return", "previous_map_run", "expected_uninterrupted_run", "map_run", "map_reset", "reset_fraction", "state"]
    for col in cols:
        a, b = rows.loc[august, col], rows2.loc[august, col]
        if isinstance(a, (float, np.floating)):
            if abs(float(a) - float(b)) > 1e-12:
                raise RuntimeError(f"AUG31_REPLAY_BOCPD_NONDETERMINISTIC:{col}")
        elif str(a) != str(b):
            raise RuntimeError(f"AUG31_REPLAY_BOCPD_NONDETERMINISTIC:{col}")

    return {
        "successor_id": bocpd.SUCCESSOR_ID,
        "context_identity": BOCPD_CONTEXT_ID if bridge_used else "BOCPD_RETURN_SUCCESSOR_V1_CORE5_AUG31_CONTEXT",
        "archived_identity": "BOCPD",
        "archived_identity_status": contract["archived_status"],
        "state": str(row["state"]),
        "log_return": float(row["log_return"]),
        "previous_map_run": int(row["previous_map_run"]),
        "expected_uninterrupted_run": int(row["expected_uninterrupted_run"]),
        "map_run": int(row["map_run"]),
        "map_reset": bool(row["map_reset"]),
        "reset_fraction": float(row["reset_fraction"]),
        "prior": asdict(prior),
        "expected_run_length": expected_run_length,
        "source_bridge_used": bridge_used,
        "source_series": "PATCH_XAU_TWELVE_DAILY_MONTHLY_MEAN_V6_TRAIN" if bridge_used else "CORE5_GOLD_MONTHLY",
        "retrieved_post_origin": bool(bridge_used),
        "evidence_class": BOCPD_EVIDENCE,
        "direction_vote_permitted": False,
        "validation_claim": False,
        "production_claim": False,
    }


def build_summary(url: str) -> dict:
    if CONTRACT_MARKER not in CONTRACT.read_text(encoding="utf-8"):
        raise RuntimeError("AUG31_REPLAY_EXPANSION_V2_CONTRACT_NOT_FROZEN")
    if (v6.L, v6.P, v6.D) != (252, 21, 32):
        raise RuntimeError("AUG31_REPLAY_PATCH_GEOMETRY_CHANGED")

    first = patch_replay_once()
    second = patch_replay_once(first["source_bundle"])
    if abs(first["forecast"] - second["forecast"]) > 1e-8 or abs(first["predicted_return"] - second["predicted_return"]) > 1e-12:
        raise RuntimeError("AUG31_REPLAY_PATCH_NONDETERMINISTIC")

    bocpd_context = build_bocpd_context(first)
    emergency = {
        "level": "NEUTRAL",
        "reversal": "OFF",
        "reason": "MONTH_OPEN_INITIALIZED_NO_SEPTEMBER_EOD_OBSERVATION",
        "monthly_reference": float(first["forecast"]),
        "reference_identity": PATCH_ID,
        "reference_evidence": EVIDENCE_CLASS,
        "direction_vote_permitted": False,
    }

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            before = authority_counts(cur)
            runtime = operational_state(cur)
        conn.rollback()
    if before != {"monthly_forecast_contracts": 0, "decision_signal_snapshots": 0, "decision_runs": 0, "decision_events": 0}:
        raise RuntimeError(f"AUG31_REPLAY_AUTHORITY_PRECONDITION_CHANGED:{before}")
    if runtime != {"counts": {"ACTIVE": 4, "WAITING": 5, "BLOCKED": 3}, "direction_votes": 3}:
        raise RuntimeError(f"AUG31_REPLAY_RUNTIME_PRECONDITION_CHANGED:{runtime}")

    return {
        "contract": CONTRACT.name,
        "git_commit": git_sha(),
        "target_context": TARGET_CONTEXT,
        "information_cutoff": ORIGIN_TS.isoformat(),
        "replay_executed_at": datetime.now(timezone.utc).isoformat(),
        "evidence_class": EVIDENCE_CLASS,
        "historical_replay": True,
        "prospective_claim": False,
        "current_runtime_authority": False,
        "canonical_authority": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "position_mapping": "NOT_PROVEN_POSITION_MAPPING",
        "patch": {k: v for k, v in first.items() if k != "source_bundle"},
        "emergency": emergency,
        "bocpd_successor": bocpd_context,
        "archived_bocpd": {
            "status": "BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED",
            "unchanged": True,
        },
        "production_runtime_before": runtime,
        "authority_counts_before": before,
        "database_writes": "NONE",
        "canonical_forecast_write": "NONE",
        "decision_store_write": "NONE",
        "dry_run_pass": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    summary = build_summary(url)
    raw = json.dumps(summary, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(raw, encoding="utf-8")
    # Derived outputs are intentionally visible; raw vendor source values are not logged.
    print(f"AUG31_REPLAY_EXPANSION_V2_DRY_RUN_PASS={str(summary['dry_run_pass']).lower()}")
    print(f"PATCH_SEPTEMBER_FORECAST={summary['patch']['forecast']:.12f}")
    print(f"PATCH_DAILY_FEATURE_MAX_DATE={summary['patch']['daily_max_date']}")
    print(f"EMERGENCY_LEVEL={summary['emergency']['level']}")
    print(f"EMERGENCY_REVERSAL={summary['emergency']['reversal']}")
    print(f"BOCPD_SUCCESSOR_STATE={summary['bocpd_successor']['state']}")
    print(f"BOCPD_SOURCE_BRIDGE_USED={str(summary['bocpd_successor']['source_bridge_used']).lower()}")
    print("PROSPECTIVE_CLAIM=false")
    print("CURRENT_RUNTIME_AUTHORITY=false")
    print("CANONICAL_FORECAST_WRITE=NONE")
    print("DECISION_STORE_WRITE=NONE")
    print("DATABASE_WRITES=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
