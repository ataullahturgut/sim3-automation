from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

SCORE_VERSION = "MACRO_EVENT_SUCCESSOR_V1_SCORE_R1"
MIN_PRIOR = 24
ACTUAL_IDS = {
    "nfp": "MACRO_NFP_ACTUAL_FIRST_PRINT",
    "unemployment": "MACRO_UNEMP_ACTUAL_FIRST_PRINT",
    "ahe_mom": "MACRO_AHE_ACTUAL_FIRST_PRINT",
}
CONSENSUS_IDS = {
    "nfp": "MACRO_NFP_CONSENSUS_PIT",
    "unemployment": "MACRO_UNEMP_CONSENSUS_PIT",
    "ahe_mom": "MACRO_AHE_CONSENSUS_PIT",
}
ALL_IDS = tuple(ACTUAL_IDS.values()) + tuple(CONSENSUS_IDS.values())
EXPECTED_MONTHS = 126
OUT = Path("macro_event_successor_v1_score_replay.json")


def db_url() -> str:
    v = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    return v


def evidence_window(reference_month: str) -> str:
    if "2016-01" <= reference_month <= "2020-12":
        return "DEV"
    if "2021-01" <= reference_month <= "2023-12":
        return "VAL"
    if "2024-01" <= reference_month <= "2026-08":
        return "LOCK"
    return "OUT_OF_FROZEN_WINDOW"


def context_month(release_ts: datetime) -> str:
    return f"{release_ts.year:04d}-{release_ts.month:02d}"


def load_panel() -> list[dict]:
    with psycopg.connect(db_url()) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select distinct on (series_id, metadata->>'reference_month')
                       series_id,
                       metadata->>'reference_month' as reference_month,
                       observation_ts,
                       value,
                       quality_status,
                       retrieved_at
                from observations
                where series_id = any(%s)
                  and metadata ? 'reference_month'
                order by series_id, metadata->>'reference_month', retrieved_at asc
                """,
                (list(ALL_IDS),),
            )
            rows = [dict(r) for r in cur.fetchall()]

    by_month: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        by_month[row["reference_month"]][row["series_id"]] = row

    panel = []
    for month in sorted(by_month):
        group = by_month[month]
        if set(group) != set(ALL_IDS):
            raise RuntimeError(f"MACRO_SCORE_INCOMPLETE_DB_INPUTS:{month}:{sorted(group)}")
        release_timestamps = {group[s]["observation_ts"] for s in ALL_IDS}
        if len(release_timestamps) != 1:
            raise RuntimeError(f"MACRO_SCORE_RELEASE_TS_MISMATCH:{month}")
        release_ts = next(iter(release_timestamps))
        panel.append({
            "reference_month": month,
            "release_ts": release_ts,
            "actual": {k: float(group[sid]["value"]) for k, sid in ACTUAL_IDS.items()},
            "consensus": {k: float(group[sid]["value"]) for k, sid in CONSENSUS_IDS.items()},
        })

    if len(panel) != EXPECTED_MONTHS:
        raise RuntimeError(f"MACRO_SCORE_PANEL_COUNT:{len(panel)}/{EXPECTED_MONTHS}")
    return panel


def sample_sigma(values: list[float]) -> float | None:
    if len(values) < MIN_PRIOR:
        return None
    sigma = statistics.stdev(values)
    if not math.isfinite(sigma) or sigma <= 0:
        return None
    return float(sigma)


def replay(panel: list[dict]) -> list[dict]:
    prior = {"nfp": [], "unemployment": [], "ahe_mom": []}
    results = []

    for row in panel:
        surprises = {k: row["actual"][k] - row["consensus"][k] for k in prior}
        sigmas = {k: sample_sigma(prior[k]) for k in prior}
        if any(v is None for v in sigmas.values()):
            result = {
                "reference_month": row["reference_month"],
                "release_ts": row["release_ts"].isoformat(),
                "context_month": context_month(row["release_ts"]),
                "window": evidence_window(row["reference_month"]),
                "state": "INSUFFICIENT_HISTORY",
                "macro_gold_score": None,
                "adverse_breadth": None,
                "supportive_breadth": None,
            }
        else:
            z_nfp = surprises["nfp"] / sigmas["nfp"]
            z_unemp = surprises["unemployment"] / sigmas["unemployment"]
            z_ahe = surprises["ahe_mom"] / sigmas["ahe_mom"]
            components = [-z_nfp, z_unemp, -z_ahe]
            score = sum(components) / 3.0
            adverse = sum(1 for x in components if x < 0)
            supportive = sum(1 for x in components if x > 0)
            if score <= -1.0 and adverse >= 2:
                state = "GOLD_ADVERSE_MACRO_SHOCK"
            elif score >= 1.0 and supportive >= 2:
                state = "GOLD_SUPPORTIVE_MACRO_SHOCK"
            else:
                state = "MACRO_MIXED_OR_SMALL"
            result = {
                "reference_month": row["reference_month"],
                "release_ts": row["release_ts"].isoformat(),
                "context_month": context_month(row["release_ts"]),
                "window": evidence_window(row["reference_month"]),
                "state": state,
                "macro_gold_score": round(float(score), 12),
                "adverse_breadth": adverse,
                "supportive_breadth": supportive,
            }
        results.append(result)
        for key in prior:
            prior[key].append(float(surprises[key]))

    return results


def summary_payload(results: list[dict]) -> dict:
    scored = [r for r in results if r["macro_gold_score"] is not None]
    counts = {}
    for window in ("DEV", "VAL", "LOCK"):
        counts[window] = dict(Counter(r["state"] for r in results if r["window"] == window))
    latest = results[-1]
    canonical_rows = [
        {
            "reference_month": r["reference_month"],
            "release_ts": r["release_ts"],
            "state": r["state"],
            "score": r["macro_gold_score"],
            "adverse_breadth": r["adverse_breadth"],
            "supportive_breadth": r["supportive_breadth"],
        }
        for r in results
    ]
    digest = hashlib.sha256(json.dumps(canonical_rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "engine_id": "MACRO_EVENT_SUCCESSOR_V1",
        "score_version": SCORE_VERSION,
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "formula_frozen_before_replay": True,
        "input_panel_rows": len(results),
        "scored_rows": len(scored),
        "insufficient_history_rows": sum(1 for r in results if r["state"] == "INSUFFICIENT_HISTORY"),
        "state_counts_by_window": counts,
        "latest": latest,
        "deterministic_score_replay_sha256": digest,
        "rows": results,
        "direction_vote": False,
        "runtime_promotion": False,
        "forecast_or_decision_write": False,
        "event_reaction_confirmation_proven": False,
    }


def main() -> int:
    panel = load_panel()
    results = replay(panel)
    payload = summary_payload(results)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "rows"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
