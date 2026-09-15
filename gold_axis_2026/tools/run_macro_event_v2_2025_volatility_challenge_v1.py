from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_DIR = ROOT / "data_pipeline"
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

import macro_event_successor_v2_score_replay as v2  # noqa: E402

CHALLENGE_ID = "GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_V1"
REPLAY_ID = "MACRO_EVENT_SUCCESSOR_V2_2025_FULL_TIMELINE_REPLAY_V1"
NY = ZoneInfo("America/New_York")
SHOCK_STATES = {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}
EXPECTED_2025_RELEASE_REFS = (
    "2024-12",
    "2025-01",
    "2025-02",
    "2025-03",
    "2025-04",
    "2025-05",
    "2025-06",
    "2025-07",
    "2025-08",
    "2025-09",
    "2025-11",
)
EXPECTED_2025_RELEASE_COUNT = 11
EXPECTED_CANCELED_REF = "2025-10"

# Frozen independently before this V2 2025 replay. Never passed into the V2 scoring engine.
VOL_EVENTS: tuple[tuple[str, str, str], ...] = (
    ("2025-02-10", "UP", "MAJOR"),
    ("2025-02-14", "DOWN", "MAJOR"),
    ("2025-02-18", "UP", "MAJOR"),
    ("2025-03-13", "UP", "MAJOR"),
    ("2025-04-04", "DOWN", "EXTREME"),
    ("2025-04-09", "UP", "EXTREME"),
    ("2025-04-10", "UP", "MAJOR"),
    ("2025-07-21", "UP", "MAJOR"),
    ("2025-08-01", "UP", "MAJOR"),
    ("2025-09-02", "UP", "MAJOR"),
    ("2025-09-22", "UP", "MAJOR"),
    ("2025-09-29", "UP", "MAJOR"),
    ("2025-10-06", "UP", "MAJOR"),
    ("2025-10-13", "UP", "MAJOR"),
    ("2025-10-16", "UP", "MAJOR"),
    ("2025-10-17", "DOWN", "MAJOR"),
    ("2025-10-21", "DOWN", "EXTREME"),
    ("2025-12-22", "UP", "EXTREME"),
    ("2025-12-29", "DOWN", "EXTREME"),
)


def engine_direction(state: str) -> str | None:
    if state == "GOLD_ADVERSE_MACRO_SHOCK":
        return "DOWN"
    if state == "GOLD_SUPPORTIVE_MACRO_SHOCK":
        return "UP"
    return None


def reaction_pct(p0: float, p15: float) -> float:
    if not (math.isfinite(p0) and math.isfinite(p15) and p0 > 0.0 and p15 > 0.0):
        raise ValueError("INVALID_REACTION_PRICE")
    return 100.0 * (p15 / p0 - 1.0)


def signed_reaction(state: str, r15_pct: float) -> float | None:
    if state == "GOLD_ADVERSE_MACRO_SHOCK":
        return -r15_pct
    if state == "GOLD_SUPPORTIVE_MACRO_SHOCK":
        return r15_pct
    return None


def _validate_release_ts(ts: datetime, ref_month: str) -> str:
    local = ts.astimezone(NY)
    if (local.hour, local.minute, local.second) != (8, 30, 0):
        raise RuntimeError(f"RELEASE_TIME_NOT_0830_ET:{ref_month}:{local.isoformat()}")
    if local.year != 2025:
        raise RuntimeError(f"NOT_2025_RELEASE:{ref_month}:{local.isoformat()}")
    return local.date().isoformat()


def load_release_lineage(conn) -> list[dict[str, Any]]:
    from psycopg.rows import dict_row

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            select metadata->>'reference_month' as reference_month,
                   observation_ts as release_ts,
                   metadata->>'release_date' as release_date,
                   metadata->>'evidence_class' as evidence_class
            from observations
            where run_id=%s::uuid
              and series_id='MACRO_NFP_ACTUAL_FIRST_PRINT'
              and observation_ts >= timestamptz '2025-01-01 00:00:00+00'
              and observation_ts <  timestamptz '2026-01-01 00:00:00+00'
            order by observation_ts
            """,
            (v2.SOURCE_RUN_ID,),
        )
        releases = [dict(r) for r in cur.fetchall()]

        cur.execute(
            """
            select metadata->>'reference_month' as reference_month,
                   count(*)::int as n,
                   count(distinct series_id)::int as series_n
            from observations
            where run_id=%s::uuid
              and series_id=any(%s)
              and metadata->>'reference_month'=any(%s)
            group by metadata->>'reference_month'
            order by metadata->>'reference_month'
            """,
            (v2.SOURCE_RUN_ID, list(v2.ALL_SERIES), list(EXPECTED_2025_RELEASE_REFS)),
        )
        coverage = {str(r["reference_month"]): (int(r["n"]), int(r["series_n"])) for r in cur.fetchall()}

        cur.execute(
            """
            select metadata->>'reference_month' as reference_month,
                   bool_and(coalesce(metadata->>'provider_exact_pre_release_update_timestamp_proven','false')='true') as all_pre_release_proven,
                   count(*)::int as n
            from observations
            where run_id=%s::uuid
              and series_id=any(%s)
              and metadata->>'reference_month'=any(%s)
            group by metadata->>'reference_month'
            order by metadata->>'reference_month'
            """,
            (
                v2.SOURCE_RUN_ID,
                [v2.SERIES["nfp_consensus"], v2.SERIES["unemp_consensus"], v2.SERIES["ahe_consensus"]],
                list(EXPECTED_2025_RELEASE_REFS),
            ),
        )
        consensus_flags = {
            str(r["reference_month"]): {
                "all_pre_release_update_timestamps_proven": bool(r["all_pre_release_proven"]),
                "consensus_rows": int(r["n"]),
            }
            for r in cur.fetchall()
        }

    refs = tuple(str(r["reference_month"]) for r in releases)
    if refs != EXPECTED_2025_RELEASE_REFS:
        raise RuntimeError(f"2025_RELEASE_REFERENCE_SET_DRIFT:{refs}")
    if len(releases) != EXPECTED_2025_RELEASE_COUNT:
        raise RuntimeError(f"2025_RELEASE_COUNT_DRIFT:{len(releases)}")

    for r in releases:
        ref = str(r["reference_month"])
        if coverage.get(ref) != (6, 6):
            raise RuntimeError(f"INCOMPLETE_V2_RELEASE_INPUT:{ref}:{coverage.get(ref)}")
        if consensus_flags.get(ref, {}).get("consensus_rows") != 3:
            raise RuntimeError(f"CONSENSUS_ROW_COUNT:{ref}:{consensus_flags.get(ref)}")
        derived_date = _validate_release_ts(r["release_ts"], ref)
        if str(r["release_date"]) != derived_date:
            raise RuntimeError(f"RELEASE_DATE_TIMESTAMP_MISMATCH:{ref}:{r['release_date']}:{derived_date}")
        r["consensus_exact_pre_release_timestamp_proven"] = consensus_flags[ref][
            "all_pre_release_update_timestamps_proven"
        ]
    return releases


def exact_close(conn, ts: datetime) -> float | None:
    from psycopg.rows import dict_row

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "select close from xau_intraday_research_cache_1m where observation_ts=%s",
            (ts,),
        )
        rows = cur.fetchall()
    if len(rows) > 1:
        raise RuntimeError(f"DUPLICATE_1M_BAR:{ts.isoformat()}")
    if not rows:
        return None
    x = float(rows[0]["close"])
    if not math.isfinite(x) or x <= 0.0:
        raise RuntimeError(f"INVALID_1M_CLOSE:{ts.isoformat()}:{x}")
    return x


def build_engine_timeline(conn) -> list[dict[str, Any]]:
    """Build all 2025 V2 outputs. Deliberately has no volatility-event argument."""
    panel, _run = v2.load_frozen_panel(conn)
    scores = v2.compute_scores(panel)
    v2.assert_prefix_invariance(panel, scores)

    scores2 = v2.compute_scores(panel)
    if [asdict(x) for x in scores] != [asdict(x) for x in scores2]:
        raise RuntimeError("V2_NONDETERMINISTIC_REPLAY")

    by_ref = {s.reference_month: s for s in scores}
    releases = load_release_lineage(conn)
    out: list[dict[str, Any]] = []

    for rel in releases:
        ref = str(rel["reference_month"])
        score = by_ref.get(ref)
        if score is None:
            raise RuntimeError(f"V2_SCORE_MISSING:{ref}")
        if score.score is None:
            raise RuntimeError(f"V2_2025_INSUFFICIENT_HISTORY_UNEXPECTED:{ref}")

        p0_ts = rel["release_ts"] - __import__("datetime").timedelta(minutes=1)
        p15_ts = rel["release_ts"] + __import__("datetime").timedelta(minutes=14)
        p0 = exact_close(conn, p0_ts)
        p15 = exact_close(conn, p15_ts)
        r15 = None if p0 is None or p15 is None else reaction_pct(p0, p15)
        sr15 = None if r15 is None else signed_reaction(score.state, r15)
        signal_dir = engine_direction(score.state)

        out.append(
            {
                "reference_month": ref,
                "release_date": str(rel["release_date"]),
                "release_ts_utc": rel["release_ts"].isoformat(),
                "release_ts_ny": rel["release_ts"].astimezone(NY).isoformat(),
                "state": score.state,
                "score": float(score.score),
                "adverse_breadth": int(score.adverse_breadth),
                "supportive_breadth": int(score.supportive_breadth),
                "signal_direction": signal_dir,
                "signal_status": "STRONG_EVENT_SIGNAL" if signal_dir else "NO_SIGNAL",
                "scale_nfp": float(score.scale_nfp),
                "scale_unemp": float(score.scale_unemp),
                "scale_ahe": float(score.scale_ahe),
                "method_nfp": score.method_nfp,
                "method_unemp": score.method_unemp,
                "method_ahe": score.method_ahe,
                "consensus_exact_pre_release_timestamp_proven": bool(
                    rel["consensus_exact_pre_release_timestamp_proven"]
                ),
                "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                "p0_0829_close": p0,
                "p15_0844_close": p15,
                "r15_pct": r15,
                "signed_r15_pct": sr15,
                "r15_direction_hit": (sr15 > 0.0) if sr15 is not None else None,
            }
        )

    if len(out) != EXPECTED_2025_RELEASE_COUNT:
        raise RuntimeError("ENGINE_TIMELINE_COUNT_MISMATCH")
    return out


def overlay_volatility(engine_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Second-stage overlay. Engine rows are already fixed before this function sees event dates."""
    events = {d: {"direction": direction, "tier": tier} for d, direction, tier in VOL_EVENTS}
    releases_by_date = {str(r["release_date"]): r for r in engine_rows}

    release_rows: list[dict[str, Any]] = []
    for row in engine_rows:
        x = dict(row)
        event = events.get(str(row["release_date"]))
        x["volatility_event_same_date"] = event is not None
        x["volatility_direction"] = event["direction"] if event else None
        x["volatility_tier"] = event["tier"] if event else None
        if event is None:
            x["challenge_status"] = (
                "FALSE_WARNING_FOR_DAILY_VOLATILITY_CHALLENGE"
                if row["signal_status"] == "STRONG_EVENT_SIGNAL"
                else "NO_SIGNAL_NON_VOLATILITY_RELEASE"
            )
        elif row["signal_status"] != "STRONG_EVENT_SIGNAL":
            x["challenge_status"] = "NO_SIGNAL"
        elif row["signal_direction"] == event["direction"]:
            x["challenge_status"] = "SAME_EVENT_SIGNAL_DIRECTION_ALIGNED"
        else:
            x["challenge_status"] = "SAME_EVENT_SIGNAL_DIRECTION_OPPOSED"
        release_rows.append(x)

    event_rows: list[dict[str, Any]] = []
    for date, direction, tier in VOL_EVENTS:
        macro = releases_by_date.get(date)
        if macro is None:
            event_rows.append(
                {
                    "event_date": date,
                    "event_direction": direction,
                    "tier": tier,
                    "macro_eligible_release": False,
                    "macro_state": None,
                    "macro_signal_direction": None,
                    "status": "NOT_APPLICABLE",
                }
            )
            continue
        if macro["signal_status"] != "STRONG_EVENT_SIGNAL":
            status = "NO_SIGNAL"
        elif macro["signal_direction"] == direction:
            status = "SAME_EVENT_SIGNAL_DIRECTION_ALIGNED"
        else:
            status = "SAME_EVENT_SIGNAL_DIRECTION_OPPOSED"
        event_rows.append(
            {
                "event_date": date,
                "event_direction": direction,
                "tier": tier,
                "macro_eligible_release": True,
                "macro_state": macro["state"],
                "macro_signal_direction": macro["signal_direction"],
                "status": status,
            }
        )
    return release_rows, event_rows


def summarize(engine_rows: list[dict[str, Any]], release_overlay: list[dict[str, Any]], event_overlay: list[dict[str, Any]]) -> dict[str, Any]:
    strong = [r for r in engine_rows if r["signal_status"] == "STRONG_EVENT_SIGNAL"]
    same_date_events = [r for r in event_overlay if r["macro_eligible_release"]]
    strong_same_date = [r for r in event_overlay if r["status"].startswith("SAME_EVENT_SIGNAL")]
    return {
        "replay_id": REPLAY_ID,
        "challenge_id": CHALLENGE_ID,
        "engine_id": "MACRO_EVENT_SUCCESSOR_V2",
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "calendar_2025_eligible_release_origins": len(engine_rows),
        "strong_signal_origins": len(strong),
        "no_signal_origins": len(engine_rows) - len(strong),
        "consensus_exact_pre_release_timestamp_proven_origins": sum(
            bool(r["consensus_exact_pre_release_timestamp_proven"]) for r in engine_rows
        ),
        "r15_complete_origins": sum(r["r15_pct"] is not None for r in engine_rows),
        "strong_r15_direction_hits": sum(bool(r["r15_direction_hit"]) for r in strong),
        "strong_r15_direction_testable": sum(r["r15_direction_hit"] is not None for r in strong),
        "volatility_event_days": len(VOL_EVENTS),
        "volatility_days_with_macro_release": len(same_date_events),
        "volatility_days_without_macro_release_not_applicable": len(VOL_EVENTS) - len(same_date_events),
        "same_event_strong_signals": len(strong_same_date),
        "same_event_direction_aligned": sum(
            r["status"] == "SAME_EVENT_SIGNAL_DIRECTION_ALIGNED" for r in event_overlay
        ),
        "same_event_direction_opposed": sum(
            r["status"] == "SAME_EVENT_SIGNAL_DIRECTION_OPPOSED" for r in event_overlay
        ),
        "eligible_volatility_release_days_no_signal": sum(r["status"] == "NO_SIGNAL" for r in event_overlay),
        "strong_signals_on_non_volatility_release_days": sum(
            r["challenge_status"] == "FALSE_WARNING_FOR_DAILY_VOLATILITY_CHALLENGE"
            for r in release_overlay
        ),
        "production_write": "NONE",
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    import psycopg

    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("NEON_DATABASE_URL", ""))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not args.database_url:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with psycopg.connect(args.database_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
        engine_rows = build_engine_timeline(conn)
        # Only after the complete motor timeline exists do we expose the frozen volatility dates.
        release_overlay, event_overlay = overlay_volatility(engine_rows)
        summary = summarize(engine_rows, release_overlay, event_overlay)
        conn.rollback()

    payload = {
        "summary": summary,
        "engine_timeline": engine_rows,
        "release_overlay": release_overlay,
        "event_overlay": event_overlay,
    }
    (args.output_dir / "macro_event_v2_2025_summary_v1.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    write_csv(args.output_dir / "macro_event_v2_2025_full_release_timeline_v1.csv", engine_rows)
    write_csv(args.output_dir / "macro_event_v2_2025_release_volatility_overlay_v1.csv", release_overlay)
    write_csv(args.output_dir / "macro_event_v2_2025_volatility_event_overlay_v1.csv", event_overlay)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
