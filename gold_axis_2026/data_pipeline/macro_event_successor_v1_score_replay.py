from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

SOURCE_RUN_ID = "6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a"
SOURCE_PIPELINE = "MACRO_EVENT_SUCCESSOR_V1_RESEARCH_DATA_PLANE_R1"
PREREG_PATH = Path(__file__).resolve().parents[1] / "GOLD_CONTROL_MACRO_EVENT_SUCCESSOR_V1_SCORE_PREREG_2026-09-05.md"
PREREG_BLOB_SHA = "ce4a6489667ba22ef7cc6aa5067c9f650952a135"
START_REFERENCE = "2016-01"
END_REFERENCE = "2026-08"
EXPECTED_COMPLETE_CASES = 126
EXPECTED_SOURCE_ROWS = 756
EXPECTED_EXCLUDED_MONTHS = ["2020-08", "2025-10"]
MIN_PRIOR = 24

SERIES = {
    "nfp_actual": "MACRO_NFP_ACTUAL_FIRST_PRINT",
    "nfp_consensus": "MACRO_NFP_CONSENSUS_PIT",
    "unemp_actual": "MACRO_UNEMP_ACTUAL_FIRST_PRINT",
    "unemp_consensus": "MACRO_UNEMP_CONSENSUS_PIT",
    "ahe_actual": "MACRO_AHE_ACTUAL_FIRST_PRINT",
    "ahe_consensus": "MACRO_AHE_CONSENSUS_PIT",
}
ALL_SERIES = tuple(SERIES.values())
DECISION_TABLES = (
    "monthly_forecast_contracts",
    "decision_signal_snapshots",
    "decision_runs",
    "decision_events",
)


@dataclass(frozen=True)
class EventRow:
    reference_month: str
    nfp_actual: float
    nfp_consensus: float
    unemp_actual: float
    unemp_consensus: float
    ahe_actual: float
    ahe_consensus: float

    def surprises(self) -> dict[str, float]:
        return {
            "nfp": self.nfp_actual - self.nfp_consensus,
            "unemp": self.unemp_actual - self.unemp_consensus,
            "ahe": self.ahe_actual - self.ahe_consensus,
        }


@dataclass(frozen=True)
class ScoreRow:
    reference_month: str
    evidence_window: str
    state: str
    score: float | None
    adverse_breadth: int | None
    supportive_breadth: int | None


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    return value


def month_range(start: str, end: str) -> list[str]:
    sy, sm = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    out: list[str] = []
    y, m = sy, sm
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y += 1
            m = 1
    return out


def evidence_window(month: str) -> str:
    if "2016-01" <= month <= "2020-12":
        return "DEV"
    if "2021-01" <= month <= "2023-12":
        return "VAL"
    if "2024-01" <= month <= "2026-08":
        return "LOCK"
    raise RuntimeError(f"REFERENCE_MONTH_OUTSIDE_FROZEN_WINDOWS:{month}")


def classify(score: float, adverse: int, supportive: int) -> str:
    if score <= -1.0 and adverse >= 2:
        return "GOLD_ADVERSE_MACRO_SHOCK"
    if score >= 1.0 and supportive >= 2:
        return "GOLD_SUPPORTIVE_MACRO_SHOCK"
    return "MACRO_MIXED_OR_SMALL"


def compute_scores(panel: list[EventRow]) -> list[ScoreRow]:
    prior: dict[str, list[float]] = {"nfp": [], "unemp": [], "ahe": []}
    out: list[ScoreRow] = []

    for row in panel:
        e = row.surprises()
        if min(len(prior[k]) for k in prior) < MIN_PRIOR:
            out.append(ScoreRow(row.reference_month, evidence_window(row.reference_month), "INSUFFICIENT_HISTORY", None, None, None))
        else:
            sigmas = {k: statistics.stdev(prior[k]) for k in prior}
            if any((not math.isfinite(v) or v <= 0.0) for v in sigmas.values()):
                out.append(ScoreRow(row.reference_month, evidence_window(row.reference_month), "INSUFFICIENT_HISTORY", None, None, None))
            else:
                z_nfp = e["nfp"] / sigmas["nfp"]
                z_unemp = e["unemp"] / sigmas["unemp"]
                z_ahe = e["ahe"] / sigmas["ahe"]
                g = (-z_nfp, z_unemp, -z_ahe)
                score = sum(g) / 3.0
                adverse = sum(1 for x in g if x < 0.0)
                supportive = sum(1 for x in g if x > 0.0)
                out.append(ScoreRow(row.reference_month, evidence_window(row.reference_month), classify(score, adverse, supportive), score, adverse, supportive))

        for k in prior:
            prior[k].append(e[k])

    return out


def stable_input_fingerprint(panel: list[EventRow]) -> str:
    payload = [
        [
            r.reference_month,
            r.nfp_actual,
            r.nfp_consensus,
            r.unemp_actual,
            r.unemp_consensus,
            r.ahe_actual,
            r.ahe_consensus,
        ]
        for r in panel
    ]
    raw = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def decision_counts(conn) -> dict[str, int]:
    out: dict[str, int] = {}
    with conn.cursor(row_factory=dict_row) as cur:
        for table in DECISION_TABLES:
            cur.execute(f"select count(*)::bigint as n from {table}")
            out[table] = int(cur.fetchone()["n"])
    return out


def load_frozen_panel(conn) -> tuple[list[EventRow], dict]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            select run_id, pipeline_version, status, observations_read, observations_written
            from retrieval_runs where run_id=%s::uuid
            """,
            (SOURCE_RUN_ID,),
        )
        run = cur.fetchone()
        if not run:
            raise RuntimeError("FROZEN_SOURCE_RETRIEVAL_RUN_NOT_FOUND")
        if run["status"] != "SUCCESS" or run["pipeline_version"] != SOURCE_PIPELINE:
            raise RuntimeError(f"FROZEN_SOURCE_RETRIEVAL_RUN_INVALID:{dict(run)}")
        if int(run["observations_read"]) != EXPECTED_SOURCE_ROWS or int(run["observations_written"]) != EXPECTED_SOURCE_ROWS:
            raise RuntimeError("FROZEN_SOURCE_RETRIEVAL_COUNTS_INVALID")

        cur.execute(
            """
            select metadata->>'reference_month' as reference_month, series_id, value
            from observations
            where run_id=%s::uuid and series_id=any(%s)
            order by metadata->>'reference_month', series_id
            """,
            (SOURCE_RUN_ID, list(ALL_SERIES)),
        )
        rows = cur.fetchall()

    if len(rows) != EXPECTED_SOURCE_ROWS:
        raise RuntimeError(f"FROZEN_SOURCE_ROW_COUNT:{len(rows)}/{EXPECTED_SOURCE_ROWS}")

    by_month: dict[str, dict[str, float]] = defaultdict(dict)
    for row in rows:
        month = str(row["reference_month"])
        sid = str(row["series_id"])
        if sid in by_month[month]:
            raise RuntimeError(f"DUPLICATE_SERIES_MONTH:{month}:{sid}")
        by_month[month][sid] = float(row["value"])

    expected_all = month_range(START_REFERENCE, END_REFERENCE)
    excluded = sorted(set(expected_all) - set(by_month))
    if excluded != EXPECTED_EXCLUDED_MONTHS:
        raise RuntimeError(f"FROZEN_EXCLUSION_DRIFT:{excluded}")
    if len(by_month) != EXPECTED_COMPLETE_CASES:
        raise RuntimeError(f"FROZEN_COMPLETE_CASE_COUNT:{len(by_month)}/{EXPECTED_COMPLETE_CASES}")

    panel: list[EventRow] = []
    for month in sorted(by_month):
        m = by_month[month]
        if set(m) != set(ALL_SERIES):
            raise RuntimeError(f"INCOMPLETE_FROZEN_MONTH:{month}:{sorted(m)}")
        panel.append(EventRow(
            reference_month=month,
            nfp_actual=m[SERIES["nfp_actual"]],
            nfp_consensus=m[SERIES["nfp_consensus"]],
            unemp_actual=m[SERIES["unemp_actual"]],
            unemp_consensus=m[SERIES["unemp_consensus"]],
            ahe_actual=m[SERIES["ahe_actual"]],
            ahe_consensus=m[SERIES["ahe_consensus"]],
        ))
    return panel, dict(run)


def assert_prefix_invariance(panel: list[EventRow], full_scores: list[ScoreRow]) -> None:
    for i in range(len(panel)):
        prefix_scores = compute_scores(panel[: i + 1])
        a = full_scores[i]
        b = prefix_scores[-1]
        if a.state != b.state or a.adverse_breadth != b.adverse_breadth or a.supportive_breadth != b.supportive_breadth:
            raise RuntimeError(f"PREFIX_STATE_INVARIANCE_FAIL:{a.reference_month}")
        if a.score is None or b.score is None:
            if a.score is not None or b.score is not None:
                raise RuntimeError(f"PREFIX_SCORE_NULL_INVARIANCE_FAIL:{a.reference_month}")
        elif not math.isclose(a.score, b.score, rel_tol=0.0, abs_tol=1e-12):
            raise RuntimeError(f"PREFIX_SCORE_INVARIANCE_FAIL:{a.reference_month}:{a.score}:{b.score}")


def summarize(panel: list[EventRow], scores: list[ScoreRow], before: dict[str, int], after: dict[str, int], run: dict) -> dict:
    counts = Counter((r.evidence_window, r.state) for r in scores)
    shock_events = [
        {
            "reference_month": r.reference_month,
            "evidence_window": r.evidence_window,
            "score": round(float(r.score), 6),
            "adverse_breadth": r.adverse_breadth,
            "supportive_breadth": r.supportive_breadth,
            "state": r.state,
        }
        for r in scores
        if r.state in {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}
    ]
    latest = scores[-1]
    scored = [r for r in scores if r.score is not None]
    val_lock_shocks = [r for r in scores if r.evidence_window in {"VAL", "LOCK"} and "SHOCK" in r.state]

    return {
        "status": "PASS_PREREG_REPLAY_REPRODUCIBLE",
        "engine_id": "MACRO_EVENT_SUCCESSOR_V1",
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "source_run_id": SOURCE_RUN_ID,
        "source_pipeline": SOURCE_PIPELINE,
        "source_input_fingerprint_sha256": stable_input_fingerprint(panel),
        "preregistration_blob_sha": PREREG_BLOB_SHA,
        "complete_case_months": len(panel),
        "source_observations": EXPECTED_SOURCE_ROWS,
        "excluded_months": EXPECTED_EXCLUDED_MONTHS,
        "minimum_prior_events": MIN_PRIOR,
        "scored_events": len(scored),
        "insufficient_history_events": sum(1 for r in scores if r.state == "INSUFFICIENT_HISTORY"),
        "state_counts": [
            {"evidence_window": w, "state": s, "count": n}
            for (w, s), n in sorted(counts.items())
        ],
        "shock_events": shock_events,
        "out_of_sample_shock_events_val_lock": len(val_lock_shocks),
        "latest": {
            "reference_month": latest.reference_month,
            "evidence_window": latest.evidence_window,
            "score": None if latest.score is None else round(float(latest.score), 12),
            "adverse_breadth": latest.adverse_breadth,
            "supportive_breadth": latest.supportive_breadth,
            "state": latest.state,
        },
        "prefix_invariance": True,
        "production_db_write": False,
        "model_result_persisted_to_neon": False,
        "direction_vote": False,
        "forecast_or_decision_write": False,
        "decision_counts_before": before,
        "decision_counts_after": after,
        "promotion_status": "NOT_APPROVED_EVENT_REACTION_VALIDATION_REQUIRED",
        "promotion_note": "Engineering replay alone cannot promote V1. The preregistration requires a separately frozen point-in-time gold event-reaction source/window and validation contract.",
        "source_run_status": run["status"],
    }


def main() -> int:
    if not PREREG_PATH.exists():
        raise RuntimeError("PREREGISTRATION_FILE_MISSING")

    with psycopg.connect(db_url()) as conn:
        before = decision_counts(conn)
        panel, run = load_frozen_panel(conn)

    scores = compute_scores(panel)
    if len(scores) != EXPECTED_COMPLETE_CASES:
        raise RuntimeError("SCORE_ROW_COUNT_MISMATCH")
    assert_prefix_invariance(panel, scores)

    with psycopg.connect(db_url()) as conn:
        after = decision_counts(conn)
    if after != before:
        raise RuntimeError(f"DECISION_AUTHORITY_STORE_CHANGED:{before}->{after}")

    result = summarize(panel, scores, before, after, run)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
