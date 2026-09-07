from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
import websocket
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
if str(R4_SRC) not in sys.path:
    sys.path.insert(0, str(R4_SRC))

from gold_r4.emergency import EmergencyState

CONTRACT = "GOLD_CONTROL_LIVE_XAU_EMERGENCY_V145"
WS_URL = "wss://ws.twelvedata.com/v1/quotes/price?apikey={apikey}"
SYMBOL = "XAU/USD"
LIVE_SERIES = "XAU_LIVE_TWELVE_WS_1M"
BOOTSTRAP_SERIES = "XAU_INTRADAY_TWELVE_REST_1M"
FEATURE_VERSION = "EMERGENCY_LIVE_PROVISIONAL_V145"
STALE_SECONDS = 120
RECONNECT_MAX_SECONDS = 30


def _db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def _api_key() -> str:
    value = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not value:
        raise RuntimeError("TWELVE_DATA_API_KEY is not set")
    return value


def _code_sha() -> str | None:
    override = os.environ.get("GOLD_CODE_SHA", "").strip().lower()
    if override:
        return override
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True, timeout=5)
        value = proc.stdout.strip().lower()
        return value if len(value) == 40 else None
    except Exception:
        return None


def _utc_iso(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts.isoformat()


def _fingerprint(kind: str, payload: Any) -> str:
    raw = json.dumps({"contract": CONTRACT, "kind": kind, "payload": payload}, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(raw).hexdigest()


@dataclass
class MinuteBar:
    minute_ts: datetime
    close: float
    provider_event_ts: datetime
    receive_ts: datetime
    event_count: int


class MinuteAggregator:
    def __init__(self) -> None:
        self._minute: datetime | None = None
        self._close: float | None = None
        self._provider_ts: datetime | None = None
        self._receive_ts: datetime | None = None
        self._count = 0

    @staticmethod
    def _floor_minute(ts: datetime) -> datetime:
        return ts.astimezone(timezone.utc).replace(second=0, microsecond=0)

    def add(self, provider_ts: datetime, price: float, receive_ts: datetime) -> MinuteBar | None:
        minute = self._floor_minute(provider_ts)
        completed: MinuteBar | None = None
        if self._minute is not None and minute > self._minute:
            assert self._close is not None and self._provider_ts is not None and self._receive_ts is not None
            completed = MinuteBar(self._minute, self._close, self._provider_ts, self._receive_ts, self._count)
            self._minute, self._close, self._provider_ts, self._receive_ts, self._count = minute, price, provider_ts, receive_ts, 1
        elif self._minute is None:
            self._minute, self._close, self._provider_ts, self._receive_ts, self._count = minute, price, provider_ts, receive_ts, 1
        elif minute == self._minute:
            if provider_ts >= (self._provider_ts or provider_ts):
                self._close, self._provider_ts, self._receive_ts = price, provider_ts, receive_ts
            self._count += 1
        return completed


def _target_and_reference(cur) -> tuple[str, float, str]:
    cur.execute("select distinct target_context from current_engine_runtime_state_v1")
    contexts = [str(r["target_context"] or "").strip() for r in cur.fetchall()]
    contexts = sorted({x for x in contexts if x})
    if len(contexts) != 1:
        raise RuntimeError(f"BLOCKED_CURRENT_TARGET_CONTEXT_NOT_UNIQUE:{contexts}")
    target = contexts[0]
    cur.execute("select metadata from current_engine_runtime_state_v1 where engine_id='CAUSAL_PATCH' and target_context=%s", (target,))
    row = cur.fetchone()
    if row is None:
        raise RuntimeError("BLOCKED_CAUSAL_REFERENCE_RUNTIME_MISSING")
    metadata = row["metadata"] if isinstance(row["metadata"], dict) else {}
    ref = metadata.get("current_month_reference") if isinstance(metadata.get("current_month_reference"), dict) else None
    if not ref:
        raise RuntimeError("BLOCKED_CAUSAL_CURRENT_MONTH_REFERENCE_MISSING")
    value = float(ref.get("forecast_value"))
    evidence = str(ref.get("evidence_class") or "").strip()
    if not math.isfinite(value) or value <= 0:
        raise RuntimeError("BLOCKED_CAUSAL_REFERENCE_INVALID")
    if evidence not in {"HISTORICAL_REPLAY", "PROSPECTIVE_SHADOW", "LIVE_PRODUCTION"}:
        raise RuntimeError(f"BLOCKED_CAUSAL_REFERENCE_EVIDENCE:{evidence or 'MISSING'}")
    return target, value, evidence


def _registry_ready(cur) -> None:
    cur.execute("select status from source_registry where series_id=%s", (LIVE_SERIES,))
    row = cur.fetchone()
    if row is None:
        raise RuntimeError("BLOCKED_LIVE_SOURCE_NOT_REGISTERED")
    status = str(row["status"] or "")
    if not status.startswith("APPROVED_LIVE_SHADOW"):
        raise RuntimeError(f"BLOCKED_LIVE_SOURCE_STATUS:{status}")


def _merged_month_history(cur, target_context: str, pending: MinuteBar | None = None) -> tuple[list[tuple[datetime, float, str]], bool]:
    start = pd.Timestamp(f"{target_context}-01", tz="UTC")
    cur.execute(
        """
        select distinct on (series_id,observation_ts) series_id,observation_ts,value,retrieved_at
        from observations
        where series_id=any(%s) and observation_ts >= %s
        order by series_id,observation_ts,retrieved_at desc,id desc
        """,
        ([BOOTSTRAP_SERIES, LIVE_SERIES], start.to_pydatetime()),
    )
    raw = [dict(r) for r in cur.fetchall()]
    by_ts: dict[datetime, tuple[float, str]] = {}
    for r in raw:
        ts = pd.Timestamp(r["observation_ts"]).tz_convert("UTC").to_pydatetime()
        value = float(r["value"])
        series = str(r["series_id"])
        old = by_ts.get(ts)
        if old is None or series == LIVE_SERIES:
            by_ts[ts] = (value, series)
    if pending is not None:
        by_ts[pending.minute_ts] = (pending.close, LIVE_SERIES)
    history = [(ts, by_ts[ts][0], by_ts[ts][1]) for ts in sorted(by_ts)]

    # Reversal requires historical intraday bootstrap. Level alert can operate
    # immediately, but reversal is not declared ready until REST bootstrap exists.
    bootstrap_complete = any(series == BOOTSTRAP_SERIES for _ts, _v, series in history)
    return history, bootstrap_complete


def _emergency_from_history(history: list[tuple[datetime, float, str]], reference: float) -> tuple[str, str]:
    state = EmergencyState()
    level = "NEUTRAL"
    reversal = "OFF"
    for ts, value, _series in history:
        level_obj, reversal_obj = state.update(pd.Timestamp(ts), float(value), reference)
        level, reversal = level_obj.value, reversal_obj.value
    return level, reversal


def _insert_retrieval_and_observation(cur, bar: MinuteBar, code_sha: str | None) -> tuple[int, str, str]:
    cur.execute("select id,lineage_id from observations where series_id=%s and observation_ts=%s order by retrieved_at desc,id desc limit 1", (LIVE_SERIES, bar.minute_ts))
    existing = cur.fetchone()
    if existing is not None:
        return int(existing["id"]), str(existing["lineage_id"]), "DUPLICATE_MINUTE_NO_WRITE"

    run_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    event_payload = {
        "series_id": LIVE_SERIES,
        "observation_ts": bar.minute_ts.isoformat(),
        "close": bar.close,
        "provider_event_ts": bar.provider_event_ts.isoformat(),
        "receive_ts": bar.receive_ts.isoformat(),
        "event_count": bar.event_count,
    }
    payload_hash = hashlib.sha256(json.dumps(event_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    lineage_id = f"{CONTRACT}:{bar.minute_ts.isoformat()}:{payload_hash[:16]}"
    cur.execute(
        """
        insert into retrieval_runs(run_id,started_at,finished_at,pipeline_version,git_sha,trigger_type,status,observations_read,observations_written,notes,metadata)
        values(%s,%s,%s,%s,%s,'LIVE_WEBSOCKET','SUCCESS',%s,1,'Twelve XAU/USD completed-minute shadow event',%s::jsonb)
        """,
        (run_id, bar.receive_ts, now, CONTRACT, code_sha, bar.event_count, json.dumps({"source": "Twelve Data WebSocket", "symbol": SYMBOL, "fallback_policy": "NONE"})),
    )
    cur.execute(
        """
        insert into observations(id,run_id,series_id,observation_ts,value,source,source_symbol,provider_as_of,available_as_of,first_seen_at,retrieved_at,frequency,unit,transform,quality_status,lineage_id,payload_hash,metadata)
        values(nextval('observations_id_seq'),%s,%s,%s,%s,'Twelve Data WebSocket',%s,%s,%s,%s,%s,'1min','USD/troy_oz','LEVEL','APPROVED_LIVE_SHADOW_WS_1M',%s,%s,%s::jsonb)
        returning id
        """,
        (
            run_id, LIVE_SERIES, bar.minute_ts, bar.close, SYMBOL, bar.provider_event_ts, bar.receive_ts,
            bar.receive_ts, now, lineage_id, payload_hash,
            json.dumps({
                "contract": CONTRACT,
                "aggregation": "last valid provider price event in completed UTC minute",
                "provider_event_timestamp": bar.provider_event_ts.isoformat(),
                "receive_timestamp": bar.receive_ts.isoformat(),
                "event_count": bar.event_count,
                "evidence_class": "LIVE_PROVISIONAL_SHADOW",
                "prospective_h1_claim": False,
                "canonical_forecast_authority": False,
                "fallback_policy": "NONE",
                "interpolation": "FORBIDDEN",
                "forward_fill": "FORBIDDEN",
            }),
        ),
    )
    return int(cur.fetchone()["id"]), lineage_id, "WRITTEN"


def _latest_feature_state(cur, name: str, target: str) -> tuple[str | None, str | None]:
    cur.execute(
        """
        select value_text,metadata->>'input_fingerprint' as fp
        from derived_feature_snapshots
        where feature_name=%s and metadata->>'target_context'=%s
        order by calculation_ts desc,id desc limit 1
        """,
        (name, target),
    )
    row = cur.fetchone()
    return (None, None) if row is None else (row["value_text"], row["fp"])


def _persist_alert_feature(cur, *, name: str, value: str, target: str, cutoff: datetime, reference: float, reference_evidence: str, history: list[tuple[datetime, float, str]], bootstrap_complete: bool, code_sha: str | None) -> bool:
    selected = [{"ts": ts.isoformat(), "value": value_, "series": series} for ts, value_, series in history[-2000:]]
    fp = _fingerprint(name, {"reference": reference, "reference_evidence": reference_evidence, "history": selected, "bootstrap_complete": bootstrap_complete})
    previous_value, previous_fp = _latest_feature_state(cur, name, target)
    if previous_fp == fp or previous_value == value:
        return False
    quality = "LIVE_PROVISIONAL_CURRENT_INPUT_HISTORICAL_REFERENCE_CONTEXT" if reference_evidence == "HISTORICAL_REPLAY" else "LIVE_PROVISIONAL_SHADOW_CONTEXT"
    cur.execute(
        """
        insert into derived_feature_snapshots(id,feature_name,feature_version,calculation_ts,input_cutoff,value_text,git_commit,input_lineage,quality_status,metadata)
        values(nextval('derived_feature_snapshots_id_seq'),%s,%s,now(),%s,%s,%s,%s::jsonb,%s,%s::jsonb)
        """,
        (
            name, FEATURE_VERSION, cutoff, value, code_sha,
            json.dumps({"series_ids": [BOOTSTRAP_SERIES, LIVE_SERIES], "selected_inputs": selected[-120:]}),
            quality,
            json.dumps({
                "contract": CONTRACT,
                "target_context": target,
                "input_fingerprint": fp,
                "monthly_reference": reference,
                "reference_expert_id": "CAUSAL_PATCH",
                "reference_evidence_class": reference_evidence,
                "live_provisional": True,
                "eod_confirmation_series": "XAU_EOD_TWELVE_NY17",
                "reversal_bootstrap_complete": bootstrap_complete,
                "prospective_h1_claim": False,
                "canonical_forecast_authority": False,
                "decision_store_write": "NONE",
                "auto_selector": "OFF",
                "auto_ensemble": "OFF",
            }),
        ),
    )
    return True


def _process_completed_bar(bar: MinuteBar, *, persist: bool) -> dict[str, Any]:
    code_sha = _code_sha()
    conn = psycopg.connect(_db_url(), autocommit=False, row_factory=dict_row)
    try:
        with conn.cursor() as cur:
            if not persist:
                cur.execute("set transaction read only")
            target, reference, ref_evidence = _target_and_reference(cur)
            if persist:
                _registry_ready(cur)
                observation_id, lineage_id, write_status = _insert_retrieval_and_observation(cur, bar, code_sha)
                history, bootstrap_complete = _merged_month_history(cur, target)
            else:
                observation_id, lineage_id, write_status = -1, "DRY_RUN", "DRY_RUN"
                history, bootstrap_complete = _merged_month_history(cur, target, pending=bar)

            level, reversal = _emergency_from_history(history, reference)
            if not bootstrap_complete:
                reversal = "NOT_READY_INTRAMONTH_BOOTSTRAP_REQUIRED"

            feature_writes: list[str] = []
            if persist:
                if _persist_alert_feature(cur, name="EMERGENCY_LIVE_LEVEL", value=level, target=target, cutoff=bar.receive_ts, reference=reference, reference_evidence=ref_evidence, history=history, bootstrap_complete=bootstrap_complete, code_sha=code_sha):
                    feature_writes.append("EMERGENCY_LIVE_LEVEL")
                if _persist_alert_feature(cur, name="EMERGENCY_LIVE_REVERSAL", value=reversal, target=target, cutoff=bar.receive_ts, reference=reference, reference_evidence=ref_evidence, history=history, bootstrap_complete=bootstrap_complete, code_sha=code_sha):
                    feature_writes.append("EMERGENCY_LIVE_REVERSAL")
                conn.commit()
            else:
                conn.rollback()
            return {
                "contract": CONTRACT,
                "target_context": target,
                "minute_ts": bar.minute_ts.isoformat(),
                "close": bar.close,
                "provider_event_ts": bar.provider_event_ts.isoformat(),
                "receive_ts": bar.receive_ts.isoformat(),
                "event_count": bar.event_count,
                "observation_id": observation_id,
                "lineage_id": lineage_id,
                "write_status": write_status,
                "emergency_live_level": level,
                "emergency_live_reversal": reversal,
                "reversal_bootstrap_complete": bootstrap_complete,
                "feature_writes": feature_writes,
                "reference_expert_id": "CAUSAL_PATCH",
                "reference_value": reference,
                "reference_evidence_class": ref_evidence,
                "decision_store_write": "NONE",
                "forecast_authority_write": "NONE",
            }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def run(*, duration_seconds: float, persist: bool, stale_seconds: int = STALE_SECONDS) -> dict[str, Any]:
    if duration_seconds < 10:
        raise ValueError("duration_seconds must be >= 10")
    aggregator = MinuteAggregator()
    start = time.monotonic()
    last_valid_receive = datetime.now(timezone.utc)
    processed: list[dict[str, Any]] = []
    reconnect_delay = 1.0
    while time.monotonic() - start < duration_seconds:
        ws = None
        try:
            ws = websocket.create_connection(WS_URL.format(apikey=_api_key()), timeout=10, origin="https://twelvedata.com")
            ws.send(json.dumps({"action": "subscribe", "params": {"symbols": SYMBOL}}))
            reconnect_delay = 1.0
            while time.monotonic() - start < duration_seconds:
                now = datetime.now(timezone.utc)
                if (now - last_valid_receive).total_seconds() > stale_seconds:
                    raise RuntimeError(f"BLOCKED_STALE_TWELVE_WS_FEED:{stale_seconds}s")
                try:
                    raw = ws.recv()
                except websocket.WebSocketTimeoutException:
                    continue
                if not raw:
                    continue
                event = json.loads(raw)
                event_type = str(event.get("event") or event.get("type") or "").lower()
                if event_type in {"error", "status", "subscribe-status"}:
                    text = json.dumps(event, default=str).lower()
                    if any(token in text for token in ("not authorized", "permission", "upgrade", "failed")):
                        raise RuntimeError(f"BLOCKED_TWELVE_WS_PROVIDER_STATUS:{event}")
                    continue
                if event_type not in {"price", "quote"} or str(event.get("symbol") or "") != SYMBOL:
                    continue
                try:
                    price = float(event.get("price"))
                    provider_ts = datetime.fromtimestamp(float(event.get("timestamp")), tz=timezone.utc)
                except Exception as exc:
                    raise RuntimeError(f"BLOCKED_INVALID_TWELVE_WS_EVENT:{event}") from exc
                receive_ts = datetime.now(timezone.utc)
                if not math.isfinite(price) or price <= 0:
                    raise RuntimeError(f"BLOCKED_INVALID_TWELVE_WS_PRICE:{price}")
                if provider_ts > receive_ts + pd.Timedelta(seconds=10):
                    raise RuntimeError("BLOCKED_PROVIDER_EVENT_FROM_FUTURE")
                last_valid_receive = receive_ts
                completed = aggregator.add(provider_ts, price, receive_ts)
                if completed is not None:
                    processed.append(_process_completed_bar(completed, persist=persist))
        except Exception:
            if ws is not None:
                try:
                    ws.close()
                except Exception:
                    pass
            if time.monotonic() - start >= duration_seconds:
                break
            time.sleep(min(reconnect_delay, RECONNECT_MAX_SECONDS))
            reconnect_delay = min(reconnect_delay * 2.0, RECONNECT_MAX_SECONDS)
            continue
        finally:
            if ws is not None:
                try:
                    ws.close()
                except Exception:
                    pass

    return {
        "contract": CONTRACT,
        "duration_seconds": duration_seconds,
        "persist": persist,
        "completed_minutes_processed": len(processed),
        "last_processed": None if not processed else processed[-1],
        "database_write_scope": "observations+derived_feature_snapshots+retrieval_runs only" if persist else "NONE",
        "decision_store_write": "NONE",
        "forecast_authority_write": "NONE",
    }


def _self_test() -> None:
    agg = MinuteAggregator()
    t0 = datetime(2026, 9, 7, 11, 49, 1, tzinfo=timezone.utc)
    assert agg.add(t0, 4400.0, t0) is None
    assert agg.add(t0.replace(second=55), 4401.0, t0.replace(second=55)) is None
    done = agg.add(datetime(2026, 9, 7, 11, 50, 2, tzinfo=timezone.utc), 4402.0, datetime(2026, 9, 7, 11, 50, 2, tzinfo=timezone.utc))
    assert done is not None
    assert done.minute_ts == datetime(2026, 9, 7, 11, 49, tzinfo=timezone.utc)
    assert done.close == 4401.0
    state = EmergencyState()
    level, reversal = state.update(pd.Timestamp("2026-09-07T11:49:00Z"), 4630.0, 4450.0)
    assert level.value == "UP"
    assert reversal.value == "OFF"
    print("LIVE_XAU_EMERGENCY_V145_SELF_TEST_PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-seconds", type=float, default=90.0)
    parser.add_argument("--persist", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        if not args.persist and args.duration_seconds <= 0:
            return 0
    result = run(duration_seconds=args.duration_seconds, persist=args.persist)
    print(json.dumps(result, indent=2, default=str))
    print("LIVE_XAU_EMERGENCY_V145_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
