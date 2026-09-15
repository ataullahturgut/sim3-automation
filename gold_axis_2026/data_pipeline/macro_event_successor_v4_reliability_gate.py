from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

ENGINE_ID = "MACRO_EVENT_SUCCESSOR_V4_RELIABILITY_GATE"
STRONG_STATES = {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}
ROLE_BY_FAMILY = {
    "EMPLOYMENT": "DIRECTIONAL",
    "FOMC": "DIRECTIONAL",
    "INFLATION": "CONTEXT_ONLY",
}
SERIES_TO_FAMILY = {
    "MACRO_EVENT_V3_EMPLOYMENT_SCORE": "EMPLOYMENT",
    "MACRO_EVENT_V3_FOMC_SCORE": "FOMC",
    "MACRO_EVENT_V3_INFLATION_SCORE": "INFLATION",
}


@dataclass(frozen=True)
class V4Event:
    family: str
    observation_ts: datetime
    parent_state: str
    parent_score: float
    parent_evidence_class: str | None
    role: str
    signal: str


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    return value


def normalize_family(value: str) -> str:
    family = value.strip().upper()
    if family not in ROLE_BY_FAMILY:
        raise ValueError(f"UNKNOWN_FAMILY:{value}")
    return family


def classify_role(family: str, parent_state: str) -> tuple[str, str]:
    family = normalize_family(family)
    if parent_state not in STRONG_STATES:
        return ROLE_BY_FAMILY[family], "NO_SIGNAL"
    role = ROLE_BY_FAMILY[family]
    if role == "CONTEXT_ONLY":
        return role, "ABSTAIN_CONTEXT_ONLY"
    if parent_state == "GOLD_ADVERSE_MACRO_SHOCK":
        return role, "GOLD_ADVERSE"
    return role, "GOLD_SUPPORTIVE"


def reaction_pct(p0: float, p15: float) -> float:
    if not (math.isfinite(p0) and math.isfinite(p15) and p0 > 0.0 and p15 > 0.0):
        raise ValueError("INVALID_PRICE")
    return 100.0 * (p15 / p0 - 1.0)


def signed_reaction(parent_state: str, r15_pct: float) -> float:
    if parent_state == "GOLD_ADVERSE_MACRO_SHOCK":
        return -r15_pct
    if parent_state == "GOLD_SUPPORTIVE_MACRO_SHOCK":
        return r15_pct
    raise ValueError(f"NOT_STRONG_STATE:{parent_state}")


def binom_one_sided_p(hits: int, n: int) -> float:
    if not (0 <= hits <= n):
        raise ValueError("INVALID_HITS")
    return sum(math.comb(n, k) for k in range(hits, n + 1)) / (2**n)


def load_parent_events(conn, start_utc: datetime, end_utc: datetime) -> list[V4Event]:
    from psycopg.rows import dict_row

    series_ids = list(SERIES_TO_FAMILY)
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            select series_id, observation_ts, value,
                   metadata->>'state' as parent_state,
                   metadata->>'evidence_class' as evidence_class
            from observations
            where series_id = any(%s)
              and observation_ts >= %s
              and observation_ts < %s
            order by observation_ts, series_id
            """,
            (series_ids, start_utc, end_utc),
        )
        rows = cur.fetchall()

    out: list[V4Event] = []
    for row in rows:
        family = SERIES_TO_FAMILY[str(row["series_id"])]
        state = str(row["parent_state"] or "")
        role, signal = classify_role(family, state)
        out.append(
            V4Event(
                family=family,
                observation_ts=row["observation_ts"],
                parent_state=state,
                parent_score=float(row["value"]),
                parent_evidence_class=row["evidence_class"],
                role=role,
                signal=signal,
            )
        )
    return out


def exact_close(conn, ts: datetime) -> float | None:
    from psycopg.rows import dict_row

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            select close
            from xau_intraday_research_cache_1m
            where observation_ts = %s
            """,
            (ts,),
        )
        rows = cur.fetchall()
    if len(rows) > 1:
        raise RuntimeError(f"DUPLICATE_1M_BAR:{ts.isoformat()}")
    if not rows:
        return None
    value = float(rows[0]["close"])
    if not math.isfinite(value) or value <= 0:
        raise RuntimeError(f"INVALID_1M_CLOSE:{ts.isoformat()}:{value}")
    return value


def evaluate_events(conn, events: Iterable[V4Event], prospective_only: bool) -> dict:
    output = []
    directional_signed = []
    all_strong = 0
    context_only = 0
    blocked_or_pending = 0

    for event in events:
        if event.parent_state not in STRONG_STATES:
            continue
        all_strong += 1

        if event.role == "CONTEXT_ONLY":
            context_only += 1

        source_ok = True
        if prospective_only and event.parent_evidence_class != "PROSPECTIVE_SHADOW":
            source_ok = False

        p0_ts = event.observation_ts - timedelta(minutes=1)
        p15_ts = event.observation_ts + timedelta(minutes=14)
        p0 = exact_close(conn, p0_ts)
        p15 = exact_close(conn, p15_ts)

        status = "OK"
        r15 = None
        signed = None
        hit = None

        if not source_ok:
            status = "BLOCKED_NOT_PROSPECTIVE_PARENT"
            blocked_or_pending += 1
        elif p0 is None or p15 is None:
            status = "PENDING_REACTION_OR_MISSING_BARS"
            blocked_or_pending += 1
        else:
            r15 = reaction_pct(p0, p15)
            if event.role == "DIRECTIONAL":
                signed = signed_reaction(event.parent_state, r15)
                hit = signed > 0.0
                directional_signed.append(signed)
            else:
                status = "CONTEXT_ONLY"

        output.append(
            {
                "family": event.family,
                "event_ts": event.observation_ts.isoformat(),
                "parent_state": event.parent_state,
                "parent_score": event.parent_score,
                "parent_evidence_class": event.parent_evidence_class,
                "v4_role": event.role,
                "v4_signal": event.signal,
                "status": status,
                "r15_pct": r15,
                "signed_r15_pct": signed,
                "directional_hit": hit,
            }
        )

    n = len(directional_signed)
    hits = sum(1 for x in directional_signed if x > 0.0)
    med = None
    if directional_signed:
        xs = sorted(directional_signed)
        mid = len(xs) // 2
        med = xs[mid] if len(xs) % 2 else (xs[mid - 1] + xs[mid]) / 2.0

    return {
        "engine_id": ENGINE_ID,
        "prospective_only": prospective_only,
        "all_parent_strong_events": all_strong,
        "directional_eligible_with_reaction": n,
        "directional_hits": hits,
        "directional_hit_rate": (hits / n) if n else None,
        "median_signed_r15_pct": med,
        "one_sided_exact_sign_test_p": binom_one_sided_p(hits, n) if n else None,
        "context_only_strong_events": context_only,
        "blocked_or_pending_events": blocked_or_pending,
        "promotion_gate_sample_ready": n >= 8,
        "promotion_gate_reaction_pass": (
            n >= 8
            and binom_one_sided_p(hits, n) <= 0.10
            and med is not None
            and med > 0.0
        ),
        "production_authority": False,
        "forecast_or_decision_write": False,
        "events": output,
    }


def parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def main() -> int:
    import psycopg

    parser = argparse.ArgumentParser()
    parser.add_argument("--start-utc", required=True)
    parser.add_argument("--end-utc", required=True)
    parser.add_argument(
        "--mode",
        choices=("historical-audit", "prospective-shadow"),
        default="prospective-shadow",
    )
    args = parser.parse_args()

    start_utc = parse_utc(args.start_utc)
    end_utc = parse_utc(args.end_utc)
    if end_utc <= start_utc:
        raise SystemExit("END_MUST_BE_AFTER_START")

    with psycopg.connect(db_url()) as conn:
        events = load_parent_events(conn, start_utc, end_utc)
        result = evaluate_events(
            conn,
            events,
            prospective_only=(args.mode == "prospective-shadow"),
        )

    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
