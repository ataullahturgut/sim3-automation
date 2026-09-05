from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

import psycopg
from psycopg.rows import dict_row
import requests

import macro_event_successor_v2_score_replay as v2

VALIDATION_ID = "MACRO_EVENT_SUCCESSOR_V2_EVENT_REACTION_VALIDATION_V1"
REACTION_PREREG_PATH = Path(__file__).resolve().parents[1] / "GOLD_CONTROL_MACRO_EVENT_SUCCESSOR_V2_EVENT_REACTION_PREREG_2026-09-05.md"
EXPECTED_EVENT_MONTHS = (
    "2021-02",
    "2021-04",
    "2021-07",
    "2022-01",
    "2022-07",
    "2023-01",
    "2023-04",
    "2024-01",
)
EXPECTED_EVENT_COUNT = 8
SHOCK_STATES = {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}
TIME_SERIES_URL = "https://api.twelvedata.com/time_series"
TZ = "America/New_York"
SYMBOL = "XAU/USD"
INTERVAL = "1min"
BAR_TIMES = ("08:29:00", "08:34:00", "08:44:00", "08:59:00")


@dataclass(frozen=True)
class ReactionRow:
    reference_month: str
    evidence_window: str
    macro_state: str
    release_date: str
    r5_pct: float
    r15_pct: float
    r30_pct: float
    signed_r15_pct: float
    directional_hit: bool
    response_sha256: str


def twelve_key() -> str:
    value = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not value:
        raise RuntimeError("TWELVE_DATA_API_KEY_NOT_SET")
    return value


def binom_one_sided_p(hits: int, n: int) -> float:
    if not (0 <= hits <= n):
        raise ValueError("INVALID_HITS")
    return sum(math.comb(n, k) for k in range(hits, n + 1)) / (2 ** n)


def reaction_pct(pre: float, post: float) -> float:
    if not (math.isfinite(pre) and math.isfinite(post) and pre > 0 and post > 0):
        raise ValueError("INVALID_PRICE")
    return 100.0 * (post / pre - 1.0)


def expected_signed_return(state: str, r15_pct: float) -> float:
    if state == "GOLD_ADVERSE_MACRO_SHOCK":
        return -r15_pct
    if state == "GOLD_SUPPORTIVE_MACRO_SHOCK":
        return r15_pct
    raise ValueError(f"NOT_A_SHOCK_STATE:{state}")


def derive_frozen_events(conn) -> list[tuple[v2.ScoreRow, str]]:
    panel, _ = v2.load_frozen_panel(conn)
    scores = v2.compute_scores(panel)
    v2.assert_prefix_invariance(panel, scores)
    shocks = [s for s in scores if s.evidence_window in {"VAL", "LOCK"} and s.state in SHOCK_STATES]
    months = tuple(s.reference_month for s in shocks)
    if len(shocks) != EXPECTED_EVENT_COUNT or months != EXPECTED_EVENT_MONTHS:
        raise RuntimeError(f"V2_EVENT_SET_DRIFT:{months}")

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            select metadata->>'reference_month' as reference_month,
                   metadata->>'release_date' as release_date,
                   observation_ts,
                   available_as_of,
                   provider_as_of
            from observations
            where run_id=%s::uuid
              and series_id='MACRO_NFP_ACTUAL_FIRST_PRINT'
              and metadata->>'reference_month'=any(%s)
            order by metadata->>'reference_month'
            """,
            (v2.SOURCE_RUN_ID, list(EXPECTED_EVENT_MONTHS)),
        )
        rows = cur.fetchall()
    if len(rows) != EXPECTED_EVENT_COUNT:
        raise RuntimeError(f"RELEASE_DATE_ROW_COUNT:{len(rows)}")
    release_by_month = {}
    for r in rows:
        m = str(r["reference_month"])
        d = str(r["release_date"])
        if not d:
            raise RuntimeError(f"MISSING_RELEASE_DATE:{m}")
        # Governed source contract fixes Employment Situation at 08:30 America/New_York.
        release_by_month[m] = d
    return [(s, release_by_month[s.reference_month]) for s in shocks]


def _request_day(session: requests.Session, release_date: str) -> tuple[dict[str, float], str, dict]:
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "timezone": TZ,
        "start_date": f"{release_date} 08:20:00",
        "end_date": f"{release_date} 09:05:00",
        "format": "JSON",
    }
    response = session.get(
        TIME_SERIES_URL,
        params=params,
        headers={"Authorization": f"apikey {twelve_key()}", "User-Agent": "GoldControl-MacroEventV2/1.0"},
        timeout=(8, 40),
    )
    response.raise_for_status()
    payload_hash = hashlib.sha256(response.content).hexdigest()
    payload = response.json()
    if payload.get("status") == "error":
        raise RuntimeError(f"TWELVE_API_ERROR:{payload.get('code')}:{payload.get('message')}")
    values = payload.get("values") or []
    if not values:
        raise RuntimeError("TWELVE_NO_VALUES")

    bars: dict[str, float] = {}
    for item in values:
        dt = str(item.get("datetime") or "")
        if not dt.startswith(release_date):
            continue
        time_part = dt.split(" ", 1)[1] if " " in dt else ""
        if time_part not in BAR_TIMES:
            continue
        close = float(item["close"])
        if not math.isfinite(close) or close <= 0:
            raise RuntimeError(f"INVALID_BAR_CLOSE:{release_date}:{time_part}")
        if time_part in bars:
            raise RuntimeError(f"DUPLICATE_BAR:{release_date}:{time_part}")
        bars[time_part] = close

    missing = [t for t in BAR_TIMES if t not in bars]
    if missing:
        raise RuntimeError(f"MISSING_REQUIRED_BARS:{release_date}:{missing}")
    return bars, payload_hash, payload.get("meta") or {}


def fetch_reactions(events: list[tuple[v2.ScoreRow, str]]) -> list[ReactionRow]:
    session = requests.Session()
    out: list[ReactionRow] = []
    for score, release_date in events:
        bars, payload_hash, _meta = _request_day(session, release_date)
        p0 = bars["08:29:00"]
        r5 = reaction_pct(p0, bars["08:34:00"])
        r15 = reaction_pct(p0, bars["08:44:00"])
        r30 = reaction_pct(p0, bars["08:59:00"])
        signed = expected_signed_return(score.state, r15)
        out.append(ReactionRow(
            reference_month=score.reference_month,
            evidence_window=score.evidence_window,
            macro_state=score.state,
            release_date=release_date,
            r5_pct=r5,
            r15_pct=r15,
            r30_pct=r30,
            signed_r15_pct=signed,
            directional_hit=signed > 0.0,
            response_sha256=payload_hash,
        ))
    return out


def summarize(reactions: list[ReactionRow], before: dict[str, int], after: dict[str, int]) -> dict:
    if len(reactions) != EXPECTED_EVENT_COUNT:
        raise RuntimeError("REACTION_COUNT_MISMATCH")
    hits = sum(1 for r in reactions if r.directional_hit)
    p_value = binom_one_sided_p(hits, len(reactions))
    median_signed = statistics.median(r.signed_r15_pct for r in reactions)
    reaction_pass = p_value <= 0.10 and median_signed > 0.0
    status = "PASS_EVENT_REACTION_EVIDENCE" if reaction_pass else "FAIL_EVENT_REACTION_EVIDENCE"
    return {
        "status": status,
        "validation_id": VALIDATION_ID,
        "engine_id": "MACRO_EVENT_SUCCESSOR_V2",
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "source_run_id": v2.SOURCE_RUN_ID,
        "gold_source": "Twelve Data XAU/USD Commodity Aggregate",
        "interval": INTERVAL,
        "timezone": TZ,
        "primary_window": "08:29_bar_close_to_08:44_bar_close",
        "event_count": len(reactions),
        "directional_hits": hits,
        "directional_hit_rate": hits / len(reactions),
        "one_sided_exact_sign_test_p": p_value,
        "median_signed_r15_pct": median_signed,
        "acceptance_gate_sign_test_p_lte": 0.10,
        "acceptance_gate_median_signed_r15_gt": 0.0,
        "reaction_gate_pass": reaction_pass,
        "events": [
            {
                "reference_month": r.reference_month,
                "evidence_window": r.evidence_window,
                "macro_state": r.macro_state,
                "release_date": r.release_date,
                "r5_pct": round(r.r5_pct, 6),
                "r15_pct": round(r.r15_pct, 6),
                "r30_pct": round(r.r30_pct, 6),
                "signed_r15_pct": round(r.signed_r15_pct, 6),
                "directional_hit": r.directional_hit,
                "response_sha256": r.response_sha256,
            }
            for r in reactions
        ],
        "production_db_write": False,
        "model_result_persisted_to_neon": False,
        "direction_vote": False,
        "forecast_or_decision_write": False,
        "decision_counts_before": before,
        "decision_counts_after": after,
        "promotion_status": "ELIGIBLE_FOR_PROMOTION_CHANGE_CONTROL" if reaction_pass else "NOT_APPROVED_REACTION_GATE_FAILED",
    }


def main() -> int:
    if not REACTION_PREREG_PATH.exists():
        raise RuntimeError("REACTION_PREREGISTRATION_FILE_MISSING")
    with psycopg.connect(v2.db_url()) as conn:
        before = v2.decision_counts(conn)
        events = derive_frozen_events(conn)

    try:
        reactions = fetch_reactions(events)
    except Exception as exc:
        blocked = {
            "status": "BLOCKED_TWELVE_HISTORICAL_INTRADAY_ACCESS",
            "validation_id": VALIDATION_ID,
            "engine_id": "MACRO_EVENT_SUCCESSOR_V2",
            "event_count_expected": EXPECTED_EVENT_COUNT,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "production_db_write": False,
            "model_result_persisted_to_neon": False,
            "direction_vote": False,
            "forecast_or_decision_write": False,
            "promotion_status": "NOT_APPROVED_SOURCE_BLOCKED",
        }
        print(json.dumps(blocked, indent=2, sort_keys=True))
        return 0

    with psycopg.connect(v2.db_url()) as conn:
        after = v2.decision_counts(conn)
    if after != before:
        raise RuntimeError(f"DECISION_AUTHORITY_STORE_CHANGED:{before}->{after}")

    result = summarize(reactions, before, after)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
