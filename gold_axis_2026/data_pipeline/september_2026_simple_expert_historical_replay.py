from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import psycopg
import requests
from psycopg.rows import dict_row

from multi_expert_forecast import (
    ExpertForecastRecord,
    MOMENTUM_EXPERT,
    MOMENTUM_V2_VERSION,
    RW_EXPERT,
    RW_V2_VERSION,
    momentum_3m_r2_source_bound,
    rw_r2_source_bound,
)
from multi_expert_forecast_store import insert_expert_forecast


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "GOLD_CONTROL_SEPTEMBER_2026_REPLAY_AND_CURRENT_CONTEXT_CONTRACT_2026-09-03.md"
EVIDENCE_PATH = ROOT / "stage4b" / "september_2026_simple_expert_historical_replay_evidence.json"

CONTRACT_MARKER = "FROZEN_SEPTEMBER_2026_HISTORICAL_REPLAY_AND_CURRENT_CONTEXT_V1"
TRACK = "HISTORICAL_REPLAY"
EVIDENCE = "HISTORICAL_REPLAY"
TARGET_MONTH = "2026-09"
FORECAST_ORIGIN = datetime(2026, 8, 31, 21, 0, 0, tzinfo=timezone.utc)
SOURCE_ID = "SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2"
SOURCE_START_NY = pd.Timestamp("2026-05-01 00:00:00")
SOURCE_END_NY = pd.Timestamp("2026-08-31 23:59:59")
REQUIRED_MONTHS = tuple(pd.Timestamp(x) for x in ("2026-05-01", "2026-06-01", "2026-07-01", "2026-08-01"))
MIN_DAILY_PER_MONTH = 15
TWELVE_URL = "https://api.twelvedata.com/time_series"
PATCH_REPLAY_STATUS = "BLOCKED_REPLAY_INPUT_SET_NOT_REPRODUCIBLE_FOR_2026_08_31"
VW_REPLAY_STATUS = "BLOCKED_NOT_PROVEN_EXECUTABLE"
OFFICIAL_SEP_STATUS = "NOT_ISSUED_MISSED_2026_08_31_ORIGIN"


def _env(name: str) -> str:
    value = str(os.environ.get(name, "")).strip()
    if not value:
        raise RuntimeError(f"{name}_MISSING")
    return value


def _verify_contract() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    required = [
        CONTRACT_MARKER,
        TARGET_MONTH,
        "HISTORICAL_REPLAY",
        RW_V2_VERSION,
        MOMENTUM_V2_VERSION,
        PATCH_REPLAY_STATUS,
        VW_REPLAY_STATUS,
        "REPLAY · PROSPECTIVE DEĞİL",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"SEPTEMBER_REPLAY_CONTRACT_NOT_FROZEN:{missing}")


def _request_json(session: requests.Session, params: dict[str, Any], attempts: int = 6) -> dict[str, Any]:
    api_key = _env("TWELVE_DATA_API_KEY")
    last = "UNKNOWN"
    for attempt in range(attempts):
        try:
            response = session.get(
                TWELVE_URL,
                params=params,
                headers={
                    "Authorization": f"apikey {api_key}",
                    "User-Agent": "Gold-Control-September-2026-Historical-Replay/1.0",
                },
                timeout=(20, 180),
            )
            payload = response.json() if response.content else None
            code = payload.get("code") if isinstance(payload, dict) else None
            if response.status_code == 429 or code == 429:
                last = "RATE_LIMIT"
                time.sleep(65)
                continue
            response.raise_for_status()
            if not isinstance(payload, dict):
                raise RuntimeError("TWELVE_RESPONSE_NOT_DICT")
            if payload.get("status") == "error":
                raise RuntimeError(f"TWELVE_API_ERROR_{payload.get('code')}")
            return payload
        except Exception as exc:
            last = type(exc).__name__
            if attempt + 1 < attempts:
                time.sleep(min(20, 2**attempt))
    raise RuntimeError(f"TWELVE_RETRY_EXHAUSTED:{last}")


def _month_period_end_utc(month: pd.Timestamp) -> datetime:
    # May-August 2026 are EDT (UTC-4). The frozen 17:00 ET month-boundary
    # semantics therefore map to 21:00Z on the calendar month end.
    end_day = month + pd.offsets.MonthEnd(0)
    return datetime(end_day.year, end_day.month, end_day.day, 21, 0, 0, tzinfo=timezone.utc)


def fetch_frozen_source() -> tuple[dict[pd.Timestamp, float], dict[pd.Timestamp, int], dict[str, Any]]:
    session = requests.Session()
    payload = _request_json(
        session,
        {
            "symbol": "XAU/USD",
            "interval": "1h",
            "start_date": SOURCE_START_NY.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": SOURCE_END_NY.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": "America/New_York",
            "outputsize": 5000,
            "order": "ASC",
            "format": "JSON",
        },
    )
    meta = payload.get("meta") or {}
    if str(meta.get("symbol")) != "XAU/USD" or str(meta.get("interval")) != "1h":
        raise RuntimeError("SEPTEMBER_REPLAY_HOURLY_META_MISMATCH")

    selected: dict[pd.Timestamp, float] = {}
    duplicate_dates = 0
    for item in payload.get("values") or []:
        text = str(item.get("datetime") or "")
        if not text.endswith("16:00:00"):
            continue
        ts = pd.Timestamp(text)
        if ts > SOURCE_END_NY:
            raise RuntimeError("SEPTEMBER_REPLAY_FUTURE_SOURCE_OBSERVATION")
        try:
            value = float(item.get("close"))
        except Exception:
            continue
        if not (np.isfinite(value) and value > 0):
            continue
        day = ts.normalize()
        if day in selected:
            duplicate_dates += 1
            continue
        selected[day] = value

    if duplicate_dates:
        raise RuntimeError(f"SEPTEMBER_REPLAY_DUPLICATE_SELECTED_DATES:{duplicate_dates}")
    if not selected:
        raise RuntimeError("SEPTEMBER_REPLAY_SOURCE_EMPTY")

    daily = pd.Series(selected, dtype=float).sort_index()
    if daily.index.max() >= pd.Timestamp("2026-09-01"):
        raise RuntimeError("SEPTEMBER_REPLAY_SEPTEMBER_INPUT_FORBIDDEN")
    monthly = daily.resample("MS").mean().dropna()
    counts = daily.resample("MS").count().astype(int)

    levels: dict[pd.Timestamp, float] = {}
    month_counts: dict[pd.Timestamp, int] = {}
    for month in REQUIRED_MONTHS:
        if month not in monthly.index or month not in counts.index:
            raise RuntimeError(f"SEPTEMBER_REPLAY_REQUIRED_MONTH_MISSING:{month:%Y-%m}")
        n = int(counts.loc[month])
        if n < MIN_DAILY_PER_MONTH:
            raise RuntimeError(f"SEPTEMBER_REPLAY_REQUIRED_MONTH_LOW_COUNT:{month:%Y-%m}:{n}")
        value = float(monthly.loc[month])
        if not (np.isfinite(value) and value > 0):
            raise RuntimeError(f"SEPTEMBER_REPLAY_REQUIRED_MONTH_INVALID:{month:%Y-%m}")
        levels[month] = value
        month_counts[month] = n

    source_hash = hashlib.sha256(
        json.dumps(
            {
                "source_id": SOURCE_ID,
                "months": [m.strftime("%Y-%m") for m in REQUIRED_MONTHS],
                "values": [levels[m] for m in REQUIRED_MONTHS],
                "counts": [month_counts[m] for m in REQUIRED_MONTHS],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return levels, month_counts, {
        "provider": "Twelve Data",
        "source_id": SOURCE_ID,
        "symbol": "XAU/USD",
        "interval": "1h",
        "requested_timezone": "America/New_York",
        "selected_bar_open_time": "16:00:00",
        "selected_bar_end_semantic": "17:00_ET_HOURLY_CLOSE",
        "first_selected_date": daily.index.min().date().isoformat(),
        "last_selected_date": daily.index.max().date().isoformat(),
        "selected_daily_observation_count": int(len(daily)),
        "duplicate_selected_dates": duplicate_dates,
        "source_hash": source_hash,
    }


def _fingerprint(expert_id: str, model_version: str, months: list[pd.Timestamp], levels: dict[pd.Timestamp, float], counts: dict[pd.Timestamp, int]) -> str:
    payload = {
        "contract": CONTRACT_MARKER,
        "forecast_track": TRACK,
        "evidence_class": EVIDENCE,
        "expert_id": expert_id,
        "model_version": model_version,
        "target_month": TARGET_MONTH,
        "forecast_origin": FORECAST_ORIGIN.isoformat(),
        "source_id": SOURCE_ID,
        "months": [m.strftime("%Y-%m") for m in months],
        "levels": [levels[m] for m in months],
        "counts": [counts[m] for m in months],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def build_replay() -> dict[str, Any]:
    _verify_contract()
    levels, counts, source_meta = fetch_frozen_source()
    ordered = [levels[m] for m in REQUIRED_MONTHS]
    rw_value = rw_r2_source_bound([levels[REQUIRED_MONTHS[-1]]])
    momentum_value = momentum_3m_r2_source_bound(ordered)
    aug_anchor = levels[REQUIRED_MONTHS[-1]]

    def marker(value: float) -> str:
        if value > aug_anchor:
            return "ABOVE_AUG_ANCHOR"
        if value < aug_anchor:
            return "BELOW_AUG_ANCHOR"
        return "EQUAL_AUG_ANCHOR"

    rw_months = [REQUIRED_MONTHS[-1]]
    mom_months = list(REQUIRED_MONTHS)
    return {
        "source": source_meta,
        "counts": {m.strftime("%Y-%m"): counts[m] for m in REQUIRED_MONTHS},
        "experts": {
            RW_EXPERT: {
                "model_name": "RANDOM_WALK",
                "model_version": RW_V2_VERSION,
                "expert_role": "BENCHMARK",
                "months": rw_months,
                "forecast_value": rw_value,
                "input_fingerprint": _fingerprint(RW_EXPERT, RW_V2_VERSION, rw_months, levels, counts),
                "display_marker": marker(rw_value),
            },
            MOMENTUM_EXPERT: {
                "model_name": "MOMENTUM_3M",
                "model_version": MOMENTUM_V2_VERSION,
                "expert_role": "EXPERT",
                "months": mom_months,
                "forecast_value": momentum_value,
                "input_fingerprint": _fingerprint(MOMENTUM_EXPERT, MOMENTUM_V2_VERSION, mom_months, levels, counts),
                "display_marker": marker(momentum_value),
            },
        },
        "levels": levels,
    }


def _dry_run_evidence(built: dict[str, Any]) -> dict[str, Any]:
    expert_hashes = {
        expert_id: {
            "input_fingerprint": row["input_fingerprint"],
            "forecast_value_sha256": hashlib.sha256(format(float(row["forecast_value"]), ".17g").encode("ascii")).hexdigest(),
            "display_marker": row["display_marker"],
        }
        for expert_id, row in built["experts"].items()
    }
    return {
        "contract": CONTRACT_MARKER,
        "status": "SEPTEMBER_2026_SIMPLE_EXPERT_HISTORICAL_REPLAY_DRY_RUN_PASS",
        "target_month": TARGET_MONTH,
        "forecast_origin": FORECAST_ORIGIN.isoformat(),
        "official_prospective_status": OFFICIAL_SEP_STATUS,
        "forecast_track": TRACK,
        "evidence_class": EVIDENCE,
        "prospective_claim": False,
        "source": built["source"],
        "monthly_counts": built["counts"],
        "experts": expert_hashes,
        "causal_patch_replay_status": PATCH_REPLAY_STATUS,
        "vw_replay_status": VW_REPLAY_STATUS,
        "database_writes": "NONE",
        "raw_market_values_logged": False,
        "forecast_values_logged": False,
    }


def _insert_month_snapshot(cur, *, expert: dict[str, Any], expert_id: str, month: pd.Timestamp, value: float, count: int, replay_as_of: datetime, git_commit: str | None) -> int:
    period_end = _month_period_end_utc(month)
    if period_end > FORECAST_ORIGIN:
        raise RuntimeError("SEPTEMBER_REPLAY_SOURCE_PERIOD_AFTER_ORIGIN")
    metadata = {
        "contract": CONTRACT_MARKER,
        "historical_replay": True,
        "prospective_claim": False,
        "retrieved_post_origin": replay_as_of > FORECAST_ORIGIN,
        "source_id": SOURCE_ID,
        "source_period_start": datetime(month.year, month.month, 1, 0, 0, 0, tzinfo=timezone.utc).isoformat(),
        "source_period_end": period_end.isoformat(),
        "observation_count": int(count),
        "provider": "Twelve Data",
        "symbol": "XAU/USD",
        "interval": "1h",
        "requested_timezone": "America/New_York",
        "selected_bar_open_time": "16:00:00",
        "selected_bar_end_semantic": "17:00_ET_HOURLY_CLOSE",
    }
    cur.execute(
        """
        insert into forecast_input_snapshots
          (forecast_origin,target_period,model_name,model_version,git_commit,
           series_id,semantic_id,observation_ts,value_used,available_as_of,
           retrieved_at,transform,lineage_id,metadata)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
        returning id
        """,
        (
            FORECAST_ORIGIN,
            TARGET_MONTH,
            expert["model_name"],
            expert["model_version"],
            git_commit,
            SOURCE_ID,
            f"{SOURCE_ID}:{month:%Y-%m}",
            period_end,
            float(value),
            period_end,
            replay_as_of,
            "MONTHLY_MEAN_OF_NY_16_00_HOURLY_BARS_HISTORICAL_REPLAY",
            f"{CONTRACT_MARKER}:{expert_id}:{month:%Y-%m}",
            json.dumps(metadata, sort_keys=True),
        ),
    )
    return int(cur.fetchone()["id"])


def issue_replay(database_url: str, built: dict[str, Any], *, git_commit: str | None) -> dict[str, Any]:
    replay_as_of = datetime.now(timezone.utc).replace(microsecond=0)
    if replay_as_of <= FORECAST_ORIGIN:
        raise RuntimeError("SEPTEMBER_REPLAY_EXECUTION_TIME_INVALID")

    with psycopg.connect(database_url, autocommit=False, row_factory=dict_row) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select expert_id,count(*)::int as n
                    from monthly_expert_forecasts
                    where target_month='2026-09-01' and forecast_track='HISTORICAL_REPLAY'
                      and expert_id=any(%s)
                    group by expert_id order by expert_id
                    """,
                    ([RW_EXPERT, MOMENTUM_EXPERT],),
                )
                existing = {row["expert_id"]: int(row["n"]) for row in cur.fetchall()}
                if existing:
                    if existing == {MOMENTUM_EXPERT: 1, RW_EXPERT: 1}:
                        conn.rollback()
                        return {"duplicate": True, "status": "SEPTEMBER_REPLAY_ALREADY_ISSUED"}
                    raise RuntimeError(f"SEPTEMBER_REPLAY_PARTIAL_EXISTING_STATE:{existing}")

                results: dict[str, Any] = {}
                for expert_id in (RW_EXPERT, MOMENTUM_EXPERT):
                    expert = built["experts"][expert_id]
                    snapshot_ids: list[int] = []
                    for month in expert["months"]:
                        snapshot_ids.append(
                            _insert_month_snapshot(
                                cur,
                                expert=expert,
                                expert_id=expert_id,
                                month=month,
                                value=built["levels"][month],
                                count=int(built["counts"][month.strftime("%Y-%m")]),
                                replay_as_of=replay_as_of,
                                git_commit=git_commit,
                            )
                        )
                    provenance = {
                        "contract": CONTRACT_MARKER,
                        "historical_replay": True,
                        "prospective_claim": False,
                        "information_cutoff": FORECAST_ORIGIN.isoformat(),
                        "replay_executed_at": replay_as_of.isoformat(),
                        "official_prospective_status": OFFICIAL_SEP_STATUS,
                        "source_id": SOURCE_ID,
                        "retrieved_post_origin": True,
                        "display_marker": expert["display_marker"],
                        "direction_vote_permitted": False,
                        "canonical_authority": False,
                        "selector_status": "NOT_PROVEN_EXPERT_SELECTION_RULE",
                        "auto_selector": "OFF",
                        "auto_ensemble": "OFF",
                    }
                    record = ExpertForecastRecord(
                        target_month=TARGET_MONTH,
                        forecast_origin=FORECAST_ORIGIN,
                        as_of=replay_as_of,
                        forecast_track=TRACK,
                        expert_id=expert_id,
                        model_name=expert["model_name"],
                        model_version=expert["model_version"],
                        expert_role=expert["expert_role"],
                        forecast_value=float(expert["forecast_value"]),
                        unit="USD/oz",
                        evidence_class=EVIDENCE,
                        git_commit=git_commit,
                        input_snapshot_ids=tuple(snapshot_ids),
                        input_fingerprint=expert["input_fingerprint"],
                        provenance=provenance,
                    )
                    results[expert_id] = insert_expert_forecast(cur, record, verify_snapshots=True)

                cur.execute("select count(*)::int as n from monthly_forecast_contracts")
                canonical_before_commit = int(cur.fetchone()["n"])
                cur.execute("select count(*)::int as n from decision_signal_snapshots")
                decisions_before_commit = int(cur.fetchone()["n"])
                if canonical_before_commit != 0 or decisions_before_commit != 0:
                    raise RuntimeError("SEPTEMBER_REPLAY_CANONICAL_OR_DECISION_STORE_NOT_EMPTY")
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    return {
        "duplicate": False,
        "status": "SEPTEMBER_2026_SIMPLE_EXPERT_HISTORICAL_REPLAY_ISSUED",
        "replay_as_of": replay_as_of.isoformat(),
        "expert_rows": {key: {k: v for k, v in row.items() if k in {"id", "input_set_id", "engine_execution_run_id"}} for key, row in results.items()},
    }


def _write_evidence(evidence: dict[str, Any]) -> None:
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(json.dumps(evidence, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("dry-run", "issue"), default="dry-run")
    parser.add_argument("--database-url", default=os.environ.get("NEON_DATABASE_URL", ""))
    parser.add_argument("--git-commit", default=os.environ.get("GITHUB_SHA"))
    args = parser.parse_args()

    built = build_replay()
    dry = _dry_run_evidence(built)
    if args.mode == "dry-run":
        _write_evidence(dry)
        print(
            "SEPTEMBER_REPLAY_DRY_RUN_PASS "
            f"months={len(REQUIRED_MONTHS)}/4 min_count={min(dry['monthly_counts'].values())} "
            f"duplicate_dates={dry['source']['duplicate_selected_dates']} "
            f"source_hash={dry['source']['source_hash']} writes=NONE values_logged=NO"
        )
        for expert_id in (RW_EXPERT, MOMENTUM_EXPERT):
            print(
                f"{expert_id}_REPLAY_READY input_fingerprint={dry['experts'][expert_id]['input_fingerprint']} "
                f"forecast_sha256={dry['experts'][expert_id]['forecast_value_sha256']} "
                f"marker={dry['experts'][expert_id]['display_marker']}"
            )
        return 0

    database_url = str(args.database_url or "").strip()
    if not database_url:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")
    result = issue_replay(database_url, built, git_commit=args.git_commit)
    evidence = {
        **dry,
        "status": result["status"],
        "database_writes": "APPEND_ONLY_HISTORICAL_REPLAY_ONLY" if not result.get("duplicate") else "NONE_DUPLICATE",
        "replay_as_of": result.get("replay_as_of"),
        "expert_rows": result.get("expert_rows", {}),
    }
    _write_evidence(evidence)
    print(
        f"{result['status']} duplicate={bool(result.get('duplicate'))} "
        "canonical_writes=NONE decision_writes=NONE values_logged=NO"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
