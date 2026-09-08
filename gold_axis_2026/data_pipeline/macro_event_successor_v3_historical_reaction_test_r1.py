from __future__ import annotations

import json
import math
import os
import statistics
import subprocess
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import psycopg
from psycopg.rows import dict_row

ENGINE = "MACRO_EVENT_SUCCESSOR_V3"
TEST_ID = "MACRO_EVENT_SUCCESSOR_V3_HISTORICAL_REACTION_TEST_R1_2026-09-08"
PIPELINE_VERSION = TEST_ID
START = datetime(2021, 1, 1, tzinfo=timezone.utc)
END = datetime(2026, 1, 1, tzinfo=timezone.utc)
SCORE_SERIES = {
    "EMPLOYMENT": "MACRO_EVENT_V3_EMPLOYMENT_SCORE",
    "INFLATION": "MACRO_EVENT_V3_INFLATION_SCORE",
    "FOMC": "MACRO_EVENT_V3_FOMC_SCORE",
}
STRONG = {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}
DECISION_TABLES = ("monthly_forecast_contracts", "decision_signal_snapshots", "decision_runs", "decision_events")


def db_url() -> str:
    v = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    return v


def git_sha() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return os.environ.get("GITHUB_SHA")


def decision_counts(conn) -> dict[str, int]:
    out = {}
    with conn.cursor(row_factory=dict_row) as cur:
        for t in DECISION_TABLES:
            cur.execute(f"select count(*)::bigint n from {t}")
            out[t] = int(cur.fetchone()["n"])
    return out


def load_strong_events(conn) -> list[dict]:
    ids = list(SCORE_SERIES.values())
    rev = {v: k for k, v in SCORE_SERIES.items()}
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""
            select distinct on (series_id,observation_ts)
                   series_id,observation_ts,value,metadata,retrieved_at
            from observations
            where series_id=any(%s) and observation_ts >= %s and observation_ts < %s
            order by series_id,observation_ts,retrieved_at desc,id desc
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
            "series_id": r["series_id"],
            "event_ts": r["observation_ts"],
            "score": float(r["value"]),
            "state": state,
        })
    out.sort(key=lambda x: (x["event_ts"], x["family"]))
    return out


def load_required_bars(conn, events: list[dict]) -> dict[datetime, float]:
    times = set()
    for e in events:
        ts = e["event_ts"]
        times.update([ts - timedelta(minutes=1), ts + timedelta(minutes=4), ts + timedelta(minutes=14), ts + timedelta(minutes=29)])
    if not times:
        return {}
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("select observation_ts,close from xau_intraday_research_cache_1m where observation_ts=any(%s)", (list(sorted(times)),))
        rows = cur.fetchall()
    return {r["observation_ts"]: float(r["close"]) for r in rows if r["close"] is not None}


def pct(pre: float, post: float) -> float:
    if not (pre > 0 and post > 0 and math.isfinite(pre) and math.isfinite(post)):
        raise ValueError("INVALID_PRICE")
    return 100.0 * (post / pre - 1.0)


def signed_return(state: str, r15: float) -> float:
    return -r15 if state == "GOLD_ADVERSE_MACRO_SHOCK" else r15


def exact_one_sided_sign_p(hits: int, n: int) -> float | None:
    if n <= 0:
        return None
    return sum(math.comb(n, k) for k in range(hits, n + 1)) / (2 ** n)


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    hits = sum(1 for r in rows if r["directional_hit"])
    signed = [r["signed_r15_pct"] for r in rows]
    return {
        "event_count": n,
        "directional_hits": hits,
        "directional_hit_rate": hits / n if n else None,
        "one_sided_exact_sign_test_p": exact_one_sided_sign_p(hits, n),
        "median_signed_r15_pct": statistics.median(signed) if signed else None,
        "median_abs_r15_pct": statistics.median(abs(r["r15_pct"]) for r in rows) if rows else None,
    }


def main() -> int:
    run_id = str(uuid.uuid4()); started = datetime.now(timezone.utc)
    with psycopg.connect(db_url(), autocommit=False) as conn:
        before = decision_counts(conn)
        events = load_strong_events(conn)
        if not events:
            raise RuntimeError("NO_STRONG_V3_EVENTS_IN_FROZEN_TEST_WINDOW")
        bars = load_required_bars(conn, events)
        supported = []; unsupported = []
        for e in events:
            ts = e["event_ts"]
            req = {
                "pre": ts - timedelta(minutes=1),
                "r5": ts + timedelta(minutes=4),
                "r15": ts + timedelta(minutes=14),
                "r30": ts + timedelta(minutes=29),
            }
            missing = [k for k, t in req.items() if t not in bars]
            if missing:
                unsupported.append({**e, "missing_bars": missing})
                continue
            p0 = bars[req["pre"]]
            r5 = pct(p0, bars[req["r5"]]); r15 = pct(p0, bars[req["r15"]]); r30 = pct(p0, bars[req["r30"]])
            sr = signed_return(e["state"], r15)
            supported.append({
                **e, "pre_ts": req["pre"], "r5_pct": r5, "r15_pct": r15, "r30_pct": r30,
                "signed_r15_pct": sr, "directional_hit": sr > 0.0,
            })

        overall = summarize(supported)
        family = {}
        for fam in SCORE_SERIES:
            family[fam] = summarize([r for r in supported if r["family"] == fam])
        gate = bool(overall["event_count"] and overall["one_sided_exact_sign_test_p"] is not None and
                    overall["one_sided_exact_sign_test_p"] <= 0.10 and overall["median_signed_r15_pct"] is not None and
                    overall["median_signed_r15_pct"] > 0.0)
        result = {
            "status": "PASS_EVENT_REACTION_EVIDENCE" if gate else "FAIL_EVENT_REACTION_EVIDENCE",
            "test_id": TEST_ID,
            "engine_id": ENGINE,
            "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
            "frozen_test_window": {"start": START.isoformat(), "end_exclusive": END.isoformat()},
            "xau_source": "Neon xau_intraday_research_cache_1m",
            "primary_window": "event_minus_1m_close_to_event_plus_14m_close",
            "diagnostic_windows": ["R5", "R30"],
            "strong_events_total": len(events),
            "supported_events": len(supported),
            "unsupported_events": len(unsupported),
            "overall": overall,
            "family": family,
            "acceptance_gate": {"one_sided_sign_p_lte": 0.10, "median_signed_r15_gt": 0.0, "pass": gate},
            "events": [{
                "family": r["family"], "event_ts": r["event_ts"].isoformat(), "score": r["score"], "state": r["state"],
                "r5_pct": round(r["r5_pct"], 6), "r15_pct": round(r["r15_pct"], 6), "r30_pct": round(r["r30_pct"], 6),
                "signed_r15_pct": round(r["signed_r15_pct"], 6), "directional_hit": r["directional_hit"],
            } for r in supported],
            "unsupported": [{
                "family": r["family"], "event_ts": r["event_ts"].isoformat(), "score": r["score"], "state": r["state"],
                "missing_bars": r["missing_bars"],
            } for r in unsupported],
            "production_authority": False,
            "promotion_status": "NOT_EVALUATED_FOR_PRODUCTION",
            "market_shock_threshold_changed": False,
            "raw_market_shock_episode_changed": False,
        }
        with conn.cursor() as cur:
            cur.execute("""insert into retrieval_runs
                (run_id,started_at,finished_at,git_sha,pipeline_version,trigger_type,status,observations_read,observations_written,notes,metadata)
                values(%s,%s,now(),%s,%s,%s,'SUCCESS',%s,0,%s,%s::jsonb)""",
                (run_id, started, git_sha(), PIPELINE_VERSION, "macro_event_v3_historical_reaction_test",
                 len(events), result["status"], json.dumps(result, sort_keys=True, default=str)))
        after = decision_counts(conn)
        if after != before:
            raise RuntimeError(f"DECISION_AUTHORITY_STORE_CHANGED:{before}->{after}")
        conn.commit()
    result["test_run_id"] = run_id; result["decision_counts_before"] = before; result["decision_counts_after"] = after
    with open("macro_event_successor_v3_historical_reaction_test_r1_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True, default=str)
    print(json.dumps(result, indent=2, sort_keys=True, default=str)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
