from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

import macro_event_successor_v3_pipeline as core
import macro_event_successor_v3_pipeline_dbcompat as compat
import macro_event_successor_v3_prospective_consensus_capture as capture_mod

OUT = Path("macro_event_successor_v3_live_result.json")
LOOKAHEAD_DAYS = 7
POST_RELEASE_MAX_HOURS = 12

FAMILY_RELEASE_SERIES = {
    "INFLATION": "CPIAUCSL",
    "EMPLOYMENT": "PAYEMS",
}

EMPLOYMENT_FRED = {
    "nfp_level": "PAYEMS",
    "unemp": "UNRATE",
    "ahe_level": "CES0500000003",
}


def release_id_for_series(series_id: str) -> tuple[int, str]:
    key = core.require_env("FRED_API_KEY")
    d = core.get(
        "https://api.stlouisfed.org/fred/series/release",
        params={"series_id": series_id, "api_key": key, "file_type": "json"},
    ).json()
    rows = d.get("releases") or []
    if len(rows) != 1:
        raise RuntimeError(f"RELEASE_ID_AMBIGUOUS:{series_id}:{len(rows)}")
    return int(rows[0]["id"]), str(rows[0]["name"])


def release_dates(release_id: int, start: datetime, end: datetime) -> list[str]:
    key = core.require_env("FRED_API_KEY")
    d = core.get(
        "https://api.stlouisfed.org/fred/release/dates",
        params={
            "release_id": release_id,
            "api_key": key,
            "file_type": "json",
            "realtime_start": start.date().isoformat(),
            "realtime_end": end.date().isoformat(),
            "include_release_dates_with_no_data": "true",
            "limit": 10000,
            "sort_order": "asc",
        },
    ).json()
    return [str(x["date"]) for x in d.get("release_dates") or []]


def governed_events(now: datetime) -> list[dict]:
    events: list[dict] = []
    start = now - timedelta(days=1)
    end = now + timedelta(days=LOOKAHEAD_DAYS)
    for family, sid in FAMILY_RELEASE_SERIES.items():
        rid, name = release_id_for_series(sid)
        for ds in release_dates(rid, start, end):
            d = datetime.strptime(ds, "%Y-%m-%d")
            release_local = datetime(d.year, d.month, d.day, 8, 30, tzinfo=core.ET)
            release_at = release_local.astimezone(core.UTC)
            events.append({
                "family": family,
                "release_id": rid,
                "release_name": name,
                "release_date": ds,
                "release_at": release_at,
                "reference_month": compat.previous_month_key(d),
                "authority": "FRED_SOURCE_PUBLISHED_RELEASE_DATE__BLS_0830_AMERICA_NEW_YORK",
            })
    events.sort(key=lambda x: (x["release_at"], x["family"]))
    return events


def employment_actuals(event: dict) -> tuple[dict[str, float], dict[str, str]]:
    ref = datetime.strptime(event["reference_month"] + "-01", "%Y-%m-%d").replace(tzinfo=core.UTC)
    prev = core.previous_month(ref)
    start, end = prev.date().isoformat(), ref.date().isoformat()
    vals: dict[str, float] = {}; hashes: dict[str, str] = {}
    for name, sid in EMPLOYMENT_FRED.items():
        d, h = core.fred_asof_level(sid, event["release_date"], start, end)
        if end not in d:
            raise RuntimeError(f"EMPLOYMENT_ACTUAL_NOT_YET_AVAILABLE:{sid}:{end}")
        if name != "unemp" and start not in d:
            raise RuntimeError(f"EMPLOYMENT_PRIOR_NOT_AVAILABLE:{sid}:{start}")
        if name == "nfp_level":
            vals["nfp"] = round(d[end] - d[start], 0)
        elif name == "unemp":
            vals["unemp"] = float(d[end])
        else:
            vals["ahe"] = round((d[end] / d[start] - 1.0) * 100.0, 1)
        hashes[name] = h
    return vals, hashes


def insert_run(conn, run_id: str, now: datetime) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """insert into retrieval_runs
            (run_id,started_at,git_sha,pipeline_version,trigger_type,status,observations_read,observations_written,notes,metadata)
            values(%s,%s,%s,%s,%s,'RUNNING',0,0,%s,%s::jsonb)""",
            (run_id, now, os.environ.get("GITHUB_SHA"), "MACRO_EVENT_SUCCESSOR_V3_LIVE_R1_2026-09-08",
             "macro_event_v3_prospective_shadow", "Prospective pre-release consensus and post-release first-observed actual; research only",
             json.dumps({"engine": core.ENGINE, "evidence_class": "PROSPECTIVE_SHADOW", "production_authority": False})),
        )


def finish_run(conn, run_id: str, status: str, written: int, result: dict) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "update retrieval_runs set finished_at=%s,status=%s,observations_written=%s,notes=%s,metadata=%s::jsonb where run_id=%s",
            (core.utcnow(), status, written, result.get("status"), json.dumps(result, default=str), run_id),
        )


def persist_consensus(conn, run_id: str, event: dict, cap: dict, now: datetime) -> int:
    obs = []
    for s in cap.get("snapshots") or []:
        captured_at = datetime.fromisoformat(str(s["captured_at"]).replace("Z", "+00:00"))
        release_at = event["release_at"]
        if not captured_at < release_at:
            raise RuntimeError("CONSENSUS_CAPTURE_NOT_PRE_RELEASE")
        metadata = {
            **s,
            "engine": core.ENGINE,
            "official_release_at": release_at.isoformat(),
            "release_id": event["release_id"],
            "release_name": event["release_name"],
            "reference_month": event["reference_month"],
            "authority": event["authority"],
            "evidence_class": "PROSPECTIVE_PRE_RELEASE_CAPTURE",
            "historical_backdating": False,
            "production_authority": False,
        }
        obs.append(core.obs_dict(
            s["series_id"], release_at, float(s["consensus_value"]), s["provider"],
            f"event_attr_id={s['event_attr_id']}", captured_at, captured_at,
            "percent" if s["unit"] == "percent" else s["unit"],
            "PROSPECTIVE_PRE_RELEASE_CAPTURE", f"MACRO_V3_{s['series_id']}_PROSPECTIVE_R1",
            s["payload_hash_sha256"], metadata,
        ))
    w, _ = core.persist_observations(conn, run_id, obs)
    return w


def persist_actuals(conn, run_id: str, event: dict, now: datetime) -> int:
    obs = []
    base = {
        "engine": core.ENGINE,
        "family": event["family"],
        "reference_month": event["reference_month"],
        "official_release_at": event["release_at"].isoformat(),
        "release_id": event["release_id"],
        "release_name": event["release_name"],
        "authority": event["authority"],
        "evidence_class": "PROSPECTIVE_FIRST_OBSERVED_POST_RELEASE",
        "retrieved_after_release": now >= event["release_at"],
        "production_authority": False,
    }
    if event["family"] == "INFLATION":
        vals, hashes = core.inflation_actuals(event)
        specs = [
            (core.INFLATION_IDS["cpi_actual"], vals["cpi"], "CPIAUCSL", hashes["cpi"]),
            (core.INFLATION_IDS["core_actual"], vals["core"], "CPILFESL", hashes["core"]),
        ]
    else:
        vals, hashes = employment_actuals(event)
        specs = [
            (core.EMPLOYMENT_IDS["nfp_actual"], vals["nfp"], "PAYEMS", hashes["nfp_level"]),
            (core.EMPLOYMENT_IDS["unemp_actual"], vals["unemp"], "UNRATE", hashes["unemp"]),
            (core.EMPLOYMENT_IDS["ahe_actual"], vals["ahe"], "CES0500000003", hashes["ahe_level"]),
        ]
    for sid, value, symbol, digest in specs:
        unit = "thousand" if sid == core.EMPLOYMENT_IDS["nfp_actual"] else "percent"
        obs.append(core.obs_dict(
            sid, event["release_at"], float(value), "Federal Reserve Bank of St. Louis ALFRED / BLS",
            symbol, now, now, unit, "PROSPECTIVE_FIRST_OBSERVED_POST_RELEASE",
            f"MACRO_V3_{sid}_PROSPECTIVE_R1", digest, base,
        ))
    w, _ = core.persist_observations(conn, run_id, obs)
    return w


def preferred_panel(conn, family: str) -> list[dict]:
    mapping = core.EMPLOYMENT_IDS if family == "EMPLOYMENT" else core.INFLATION_IDS
    series_ids = list(mapping.values())
    reverse = {v: k for k, v in mapping.items()}
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            select series_id,observation_ts,value,quality_status,retrieved_at,metadata
            from observations where series_id=any(%s)
            order by observation_ts,series_id,
              case when quality_status like 'PROSPECTIVE%%' then 2 else 1 end desc,
              retrieved_at desc,id desc
            """, (series_ids,)
        )
        rows = cur.fetchall()
    chosen: dict[tuple, dict] = {}
    for r in rows:
        key = (r["observation_ts"], r["series_id"])
        if key not in chosen:
            chosen[key] = dict(r)
    by: dict[datetime, dict] = {}
    for (ts, sid), r in chosen.items():
        k = reverse[sid]; by.setdefault(ts, {})[k] = float(r["value"])
    need = set(mapping)
    return [{"observation_ts": ts, **vals} for ts, vals in sorted(by.items()) if set(vals) >= need]


def persist_latest_score(conn, run_id: str, event: dict, now: datetime) -> int:
    panel = preferred_panel(conn, event["family"])
    scores = core.score_employment(panel) if event["family"] == "EMPLOYMENT" else core.score_inflation(panel)
    match = next((x for x in scores if x["observation_ts"] == event["release_at"]), None)
    if match is None:
        return 0
    sid = core.SCORE_IDS[event["family"]]
    metadata = {
        "engine": core.ENGINE, "family": event["family"], "state": match["state"],
        "components": match["components"], "surprises": match["surprises"],
        "scale_values": match["scale_values"], "scale_methods": match["scale_methods"],
        "evidence_class": "PROSPECTIVE_SHADOW", "macro_confirmed_authority": False,
        "production_authority": False, "official_release_at": event["release_at"].isoformat(),
    }
    obs = [core.obs_dict(
        sid, event["release_at"], match["score"], "Derived Macro Event V3",
        event["family"], now, now, "robust_z", "PROSPECTIVE_SHADOW",
        f"MACRO_V3_{event['family']}_SCORE_PROSPECTIVE_R1",
        core.canonical_json_hash({"event": event["release_at"].isoformat(), "score": match["score"], "state": match["state"]}),
        metadata,
    )]
    w, _ = core.persist_observations(conn, run_id, obs)
    return w


def main() -> int:
    now = core.utcnow(); run_id = str(uuid.uuid4())
    result = {"engine_id": core.ENGINE, "generated_at": now.isoformat(), "status": "RUNNING", "events": [],
              "production_authority": False, "market_shock_threshold_changed": False, "raw_market_shock_episode_changed": False}
    conn = psycopg.connect(core.require_env("NEON_DATABASE_URL"), autocommit=False)
    written = 0
    try:
        core.upsert_registry(conn); insert_run(conn, run_id, now)
        events = governed_events(now)
        for event in events:
            delta = event["release_at"] - now
            row = {**event, "release_at": event["release_at"].isoformat(), "action": "NOOP"}
            if timedelta(0) < delta <= timedelta(days=LOOKAHEAD_DAYS):
                cap = capture_mod.capture(event["family"], event["release_date"], event["release_at"], captured_at=now)
                row["capture_status"] = cap["status"]
                if cap["status"] == "PASS_PROSPECTIVE_PRE_RELEASE_CAPTURE":
                    w = persist_consensus(conn, run_id, event, cap, now); written += w; row["action"] = "PRE_RELEASE_CONSENSUS_CAPTURED"; row["written"] = w
            elif timedelta(0) <= -delta <= timedelta(hours=POST_RELEASE_MAX_HOURS):
                w = persist_actuals(conn, run_id, event, now); written += w
                sw = persist_latest_score(conn, run_id, event, now); written += sw
                row["action"] = "POST_RELEASE_ACTUAL_AND_SCORE_PROCESSED"; row["written"] = w + sw
            result["events"].append(row)
        result["fomc"] = {"status": "BLOCKED_CME_FEDWATCH_API_NOT_CONFIGURED" if not all(os.environ.get(x) for x in ("CME_FEDWATCH_API_URL","CME_FEDWATCH_API_KEY","CME_FEDWATCH_SCHEMA_VERSION")) else "SOURCE_CONFIGURED_NOT_YET_INGESTED", "proxy_substitution": False}
        result["written"] = written; result["run_id"] = run_id; result["status"] = "SUCCESS_PROSPECTIVE_SHADOW_LANE"
        finish_run(conn, run_id, "SUCCESS", written, result); conn.commit()
        OUT.write_text(json.dumps(result, indent=2, sort_keys=True, default=str), encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True, default=str)); return 0
    except Exception as exc:
        conn.rollback(); result["status"] = "FAIL_LIVE_PIPELINE"; result["error"] = f"{type(exc).__name__}:{exc}"
        OUT.write_text(json.dumps(result, indent=2, sort_keys=True, default=str), encoding="utf-8"); print(json.dumps(result, indent=2, sort_keys=True, default=str)); return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
