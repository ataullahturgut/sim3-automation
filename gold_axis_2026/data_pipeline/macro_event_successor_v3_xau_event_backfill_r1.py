from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import uuid
from datetime import datetime, timedelta, timezone

import psycopg
from psycopg.rows import dict_row
import requests

ENGINE = "MACRO_EVENT_SUCCESSOR_V3"
PIPELINE_VERSION = "MACRO_EVENT_SUCCESSOR_V3_XAU_EVENT_BACKFILL_R1_2026-09-08"
SERIES_ID = "XAU_USD_MACRO_EVENT_REACTION_1M"
SCORE_SERIES = {
    "EMPLOYMENT": "MACRO_EVENT_V3_EMPLOYMENT_SCORE",
    "INFLATION": "MACRO_EVENT_V3_INFLATION_SCORE",
    "FOMC": "MACRO_EVENT_V3_FOMC_SCORE",
}
STRONG = {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}
START = datetime(2021, 1, 1, tzinfo=timezone.utc)
END = datetime(2026, 1, 1, tzinfo=timezone.utc)
OFFSETS = (-1, 4, 14, 29)
API_URL = "https://api.twelvedata.com/time_series"


def env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise RuntimeError(f"{name}_NOT_SET")
    return v


def git_sha() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return os.environ.get("GITHUB_SHA")


def load_events(conn) -> list[dict]:
    ids = list(SCORE_SERIES.values())
    rev = {v: k for k, v in SCORE_SERIES.items()}
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""
            select distinct on (series_id, observation_ts)
                   series_id, observation_ts, value, metadata, retrieved_at
            from observations
            where series_id = any(%s)
              and observation_ts >= %s and observation_ts < %s
            order by series_id, observation_ts, retrieved_at desc, id desc
        """, (ids, START, END))
        rows = cur.fetchall()
    out = []
    for r in rows:
        meta = r["metadata"] or {}
        state = str(meta.get("state") or "")
        if state not in STRONG:
            continue
        out.append({
            "family": rev[r["series_id"]],
            "event_ts": r["observation_ts"],
            "state": state,
            "score": float(r["value"]),
        })
    out.sort(key=lambda x: (x["event_ts"], x["family"]))
    return out


def existing_times(conn, events: list[dict]) -> set[datetime]:
    needed = sorted({e["event_ts"] + timedelta(minutes=o) for e in events for o in OFFSETS})
    if not needed:
        return set()
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""
            select observation_ts from xau_intraday_research_cache_1m where observation_ts=any(%s)
            union
            select observation_ts from observations where series_id=%s and observation_ts=any(%s)
        """, (needed, SERIES_ID, needed))
        return {r["observation_ts"] for r in cur.fetchall()}


def request_event(session: requests.Session, event: dict) -> tuple[dict[datetime, float], str]:
    ts = event["event_ts"]
    start = ts - timedelta(minutes=5)
    end = ts + timedelta(minutes=35)
    params = {
        "symbol": "XAU/USD",
        "interval": "1min",
        "timezone": "UTC",
        "start_date": start.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end.strftime("%Y-%m-%d %H:%M:%S"),
        "format": "JSON",
        "outputsize": 100,
    }
    last_error = None
    for attempt in range(3):
        r = session.get(
            API_URL,
            params=params,
            headers={"Authorization": f"apikey {env('TWELVE_DATA_API_KEY')}", "User-Agent": "Gold-Control-Macro-Event-V3/1.0"},
            timeout=(10, 45),
        )
        payload_hash = hashlib.sha256(r.content).hexdigest()
        if r.status_code == 429:
            last_error = f"HTTP_429:{r.text[:300]}"
            time.sleep(30 * (attempt + 1))
            continue
        r.raise_for_status()
        payload = r.json()
        if payload.get("status") == "error":
            raise RuntimeError(f"TWELVE_API_ERROR:{payload.get('code')}:{payload.get('message')}")
        out = {}
        for item in payload.get("values") or []:
            raw = str(item.get("datetime") or "")
            if not raw:
                continue
            dt = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            close = float(item["close"])
            if close <= 0:
                raise RuntimeError(f"INVALID_CLOSE:{dt}:{close}")
            out[dt] = close
        return out, payload_hash
    raise RuntimeError(last_error or "TWELVE_RETRY_EXHAUSTED")


def main() -> int:
    run_id = str(uuid.uuid4())
    retrieved = datetime.now(timezone.utc)
    session = requests.Session()
    with psycopg.connect(env("NEON_DATABASE_URL"), autocommit=False) as conn:
        events = load_events(conn)
        have = existing_times(conn, events)
        targets = []
        for e in events:
            req = [e["event_ts"] + timedelta(minutes=o) for o in OFFSETS]
            if any(t not in have for t in req):
                targets.append(e)

        inserted = 0
        supported_after = 0
        blocked = []
        rows_to_write = []
        for i, e in enumerate(targets):
            try:
                bars, payload_hash = request_event(session, e)
                missing = []
                for offset in OFFSETS:
                    t = e["event_ts"] + timedelta(minutes=offset)
                    if t in have:
                        continue
                    if t not in bars:
                        missing.append(t.isoformat())
                        continue
                    meta = {
                        "engine": ENGINE,
                        "family": e["family"],
                        "event_ts": e["event_ts"].isoformat(),
                        "event_state": e["state"],
                        "event_score": e["score"],
                        "offset_minutes": offset,
                        "symbol": "XAU/USD",
                        "interval": "1min",
                        "timezone": "UTC",
                        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                        "historical_retrieval_not_original_pit_capture": True,
                        "production_authority": False,
                    }
                    rows_to_write.append((
                        run_id, SERIES_ID, t, bars[t], "Twelve Data XAU/USD Commodity Aggregate", "XAU/USD",
                        retrieved, retrieved, retrieved, retrieved, "1min", "USD/oz", "LEVEL",
                        "APPROVED_HISTORICAL_REACTION_RECONSTRUCTION", f"{SERIES_ID}:{t.isoformat()}", payload_hash,
                        json.dumps(meta, sort_keys=True),
                    ))
                    have.add(t)
                if missing:
                    blocked.append({"family": e["family"], "event_ts": e["event_ts"].isoformat(), "missing": missing, "reason": "MISSING_REQUIRED_BARS_IN_PROVIDER_RESPONSE"})
                else:
                    supported_after += 1
            except Exception as exc:
                blocked.append({"family": e["family"], "event_ts": e["event_ts"].isoformat(), "reason": f"{type(exc).__name__}:{exc}"})
            if i + 1 < len(targets):
                time.sleep(8)

        with conn.cursor() as cur:
            cur.execute("""insert into retrieval_runs
                (run_id,started_at,finished_at,git_sha,pipeline_version,trigger_type,status,observations_read,observations_written,notes,metadata)
                values(%s,%s,now(),%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
                (run_id, retrieved, git_sha(), PIPELINE_VERSION, "macro_event_v3_xau_event_backfill",
                 "SUCCESS" if not blocked else "PARTIAL", len(targets), len(rows_to_write),
                 "Targeted event-window XAU 1m historical reconstruction", json.dumps({"blocked": blocked}, sort_keys=True)))
            for row in rows_to_write:
                cur.execute("""insert into observations
                    (run_id,series_id,observation_ts,value,source,source_symbol,provider_as_of,available_as_of,first_seen_at,retrieved_at,frequency,unit,transform,quality_status,lineage_id,payload_hash,metadata)
                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""", row)
                inserted += 1
        conn.commit()

    result = {
        "status": "PASS_XAU_EVENT_BACKFILL_COMPLETE" if not blocked else "PARTIAL_XAU_EVENT_BACKFILL",
        "run_id": run_id,
        "strong_events_total": len(events),
        "events_needing_provider_backfill": len(targets),
        "events_completed_from_provider": supported_after,
        "observations_written": inserted,
        "blocked": blocked,
        "series_id": SERIES_ID,
        "production_authority": False,
        "market_shock_threshold_changed": False,
    }
    with open("macro_event_successor_v3_xau_event_backfill_r1_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
