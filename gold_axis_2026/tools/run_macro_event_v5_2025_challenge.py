from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg
from psycopg.rows import dict_row

from macro_event_v5_core import RawEvent, predict_ols, score_family, severity

ENGINE_ID = "MACRO_EVENT_SUCCESSOR_V5_PRE2025"
START = datetime(2016, 1, 1, tzinfo=timezone.utc)
CHALLENGE_START = datetime(2025, 1, 1, tzinfo=timezone.utc)
CHALLENGE_END = datetime(2026, 1, 1, tzinfo=timezone.utc)
NY = ZoneInfo("America/New_York")

SOURCE_RUNS = {
    "EMPLOYMENT": "6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a",
    "INFLATION": "1e96b5ac-3d44-472b-b6fd-d5d6558181a6",
    "FOMC": "2f86f5d7-9800-4fe2-880c-48d6b84ff755",
}
EMP_SERIES = {
    "nfp_actual": "MACRO_NFP_ACTUAL_FIRST_PRINT",
    "nfp_consensus": "MACRO_NFP_CONSENSUS_PIT",
    "unemp_actual": "MACRO_UNEMP_ACTUAL_FIRST_PRINT",
    "unemp_consensus": "MACRO_UNEMP_CONSENSUS_PIT",
    "ahe_actual": "MACRO_AHE_ACTUAL_FIRST_PRINT",
    "ahe_consensus": "MACRO_AHE_CONSENSUS_PIT",
}
INF_SERIES = {
    "cpi_actual": "MACRO_CPI_ACTUAL_FIRST_PRINT",
    "cpi_consensus": "MACRO_CPI_CONSENSUS_PIT",
    "core_actual": "MACRO_CORE_CPI_ACTUAL_FIRST_PRINT",
    "core_consensus": "MACRO_CORE_CPI_CONSENSUS_PIT",
}
FOMC_SERIES = {
    "target": "MACRO_FOMC_GSS_TARGET_FROZEN2015",
    "path": "MACRO_FOMC_GSS_PATH_FROZEN2015",
}
EXPECTED_2025_COUNTS = {"EMPLOYMENT": 11, "INFLATION": 10, "FOMC": 8}

VOLATILITY_EVENTS = [
    ("2025-02-10", "UP", "MAJOR", 2.3407),
    ("2025-02-14", "DOWN", "MAJOR", -2.2468),
    ("2025-02-18", "UP", "MAJOR", 2.1885),
    ("2025-03-13", "UP", "MAJOR", 2.1237),
    ("2025-04-04", "DOWN", "EXTREME", -3.3930),
    ("2025-04-09", "UP", "EXTREME", 3.2185),
    ("2025-04-10", "UP", "MAJOR", 2.3440),
    ("2025-07-21", "UP", "MAJOR", 2.0611),
    ("2025-08-01", "UP", "MAJOR", 2.5481),
    ("2025-09-02", "UP", "MAJOR", 2.6673),
    ("2025-09-22", "UP", "MAJOR", 2.6254),
    ("2025-09-29", "UP", "MAJOR", 2.3040),
    ("2025-10-06", "UP", "MAJOR", 2.7911),
    ("2025-10-13", "UP", "MAJOR", 2.5043),
    ("2025-10-16", "UP", "MAJOR", 2.9074),
    ("2025-10-17", "DOWN", "MAJOR", -2.0589),
    ("2025-10-21", "DOWN", "EXTREME", -4.1054),
    ("2025-12-22", "UP", "EXTREME", 4.0174),
    ("2025-12-29", "DOWN", "EXTREME", -6.6415),
]


def canonical_hash(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_model(model: dict, expected_sha: str | None):
    if model.get("engine_id") != ENGINE_ID:
        raise RuntimeError("MODEL_ENGINE_ID_MISMATCH")
    if model.get("status") != "FROZEN_PRE2025_MODEL_PARAMETERS":
        raise RuntimeError("MODEL_NOT_FROZEN_PRE2025")
    if model.get("cutoff_exclusive") != "2025-01-01T00:00:00+00:00":
        raise RuntimeError("MODEL_CUTOFF_DRIFT")
    if model.get("max_training_release_ts", "9999") >= "2025-01-01T00:00:00+00:00":
        raise RuntimeError("MODEL_CONTAINS_2025_TRAINING")
    claimed = model.get("model_payload_sha256")
    payload = dict(model)
    payload.pop("model_payload_sha256", None)
    actual = canonical_hash(payload)
    if actual != claimed:
        raise RuntimeError(f"MODEL_HASH_SELF_CHECK_FAIL:{actual}:{claimed}")
    if expected_sha and claimed != expected_sha:
        raise RuntimeError(f"MODEL_HASH_NOT_EXPECTED:{claimed}:{expected_sha}")


def load_rows(conn, run_id, series_ids, end, scheduled_fomc=False):
    extra = "and coalesce(metadata->>'unscheduled','0')='0'" if scheduled_fomc else ""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            f"""
            select series_id, observation_ts, value
            from observations
            where run_id=%s::uuid and series_id=any(%s)
              and observation_ts >= %s and observation_ts < %s
              {extra}
            order by observation_ts, series_id
            """,
            (run_id, series_ids, START, end),
        )
        return cur.fetchall()


def group_complete(rows, required_series):
    by_ts = {}
    for r in rows:
        ts = r["observation_ts"]
        sid = str(r["series_id"])
        bucket = by_ts.setdefault(ts, {})
        if sid in bucket:
            raise RuntimeError(f"DUPLICATE_SOURCE_ROW:{ts.isoformat()}:{sid}")
        bucket[sid] = float(r["value"])
    req = set(required_series)
    incomplete = {ts: sorted(req - set(v)) for ts, v in by_ts.items() if set(v) != req}
    if incomplete:
        raise RuntimeError(f"INCOMPLETE_SOURCE_EVENTS:{incomplete}")
    return by_ts


def load_all_events(conn):
    emp = group_complete(
        load_rows(conn, SOURCE_RUNS["EMPLOYMENT"], list(EMP_SERIES.values()), CHALLENGE_END),
        list(EMP_SERIES.values()),
    )
    inf = group_complete(
        load_rows(conn, SOURCE_RUNS["INFLATION"], list(INF_SERIES.values()), CHALLENGE_END),
        list(INF_SERIES.values()),
    )
    fomc = group_complete(
        load_rows(conn, SOURCE_RUNS["FOMC"], list(FOMC_SERIES.values()), CHALLENGE_END, scheduled_fomc=True),
        list(FOMC_SERIES.values()),
    )
    out = {"EMPLOYMENT": [], "INFLATION": [], "FOMC": []}
    for ts, m in sorted(emp.items()):
        out["EMPLOYMENT"].append(RawEvent("EMPLOYMENT", ts, {
            "nfp": m[EMP_SERIES["nfp_actual"]] - m[EMP_SERIES["nfp_consensus"]],
            "unemp": m[EMP_SERIES["unemp_actual"]] - m[EMP_SERIES["unemp_consensus"]],
            "ahe": m[EMP_SERIES["ahe_actual"]] - m[EMP_SERIES["ahe_consensus"]],
        }))
    for ts, m in sorted(inf.items()):
        out["INFLATION"].append(RawEvent("INFLATION", ts, {
            "cpi": m[INF_SERIES["cpi_actual"]] - m[INF_SERIES["cpi_consensus"]],
            "core": m[INF_SERIES["core_actual"]] - m[INF_SERIES["core_consensus"]],
        }))
    for ts, m in sorted(fomc.items()):
        out["FOMC"].append(RawEvent("FOMC", ts, {
            "target": m[FOMC_SERIES["target"]],
            "path": m[FOMC_SERIES["path"]],
        }))
    counts = {
        family: sum(CHALLENGE_START <= e.release_ts < CHALLENGE_END for e in events)
        for family, events in out.items()
    }
    if counts != EXPECTED_2025_COUNTS:
        raise RuntimeError(f"CHALLENGE_EVENT_COUNT_DRIFT:{counts}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--database-url", required=True)
    ap.add_argument("--model-json", required=True)
    ap.add_argument("--expected-model-sha")
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    model = json.loads(Path(args.model_json).read_text(encoding="utf-8"))
    validate_model(model, args.expected_model_sha)

    with psycopg.connect(args.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read read only")
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select count(*)::int as n
                from observations
                where observation_ts >= %s and observation_ts < %s
                  and series_id like 'MACRO_EVENT_%%'
                """,
                (CHALLENGE_START, CHALLENGE_END),
            )
            if int(cur.fetchone()["n"]) != 0:
                raise RuntimeError("PREEXISTING_2025_DERIVED_MACRO_EVENT_ROWS_PRESENT")

        raw_by_family = load_all_events(conn)
        timeline = []
        for family in ("EMPLOYMENT", "INFLATION", "FOMC"):
            scored = score_family(raw_by_family[family])
            family_model = model["families"][family]
            thresholds = family_model["intensity_thresholds"]
            feature_order = family_model["component_order"]
            direction_model = family_model["direction_fit"]
            for e in scored:
                if not (CHALLENGE_START <= e.release_ts < CHALLENGE_END):
                    continue
                if e.z is None:
                    raise RuntimeError(f"2025_EVENT_UNSCORABLE:{family}:{e.release_ts.isoformat()}")
                pred = predict_ols(direction_model, [float(e.z[k]) for k in feature_order])
                direction = "UP" if pred > 0.0 else "DOWN" if pred < 0.0 else "FLAT"
                event_date_ny = e.release_ts.astimezone(NY).date().isoformat()
                timeline.append({
                    "family": family,
                    "release_ts": e.release_ts.isoformat(),
                    "event_date_ny": event_date_ny,
                    "raw_components_json": json.dumps(e.raw_components, sort_keys=True),
                    "z_json": json.dumps(e.z, sort_keys=True),
                    "shock_intensity": float(e.shock_intensity),
                    "severity": severity(e.shock_intensity, thresholds),
                    "predicted_r15": float(pred),
                    "predicted_direction": direction,
                    "direction_fit_support_n": int(direction_model["support_n"]),
                    "direction_loo_sign_accuracy": float(direction_model["loo_sign_accuracy"]),
                })

        timeline = sorted(timeline, key=lambda r: (r["release_ts"], r["family"]))
        if len(timeline) != sum(EXPECTED_2025_COUNTS.values()):
            raise RuntimeError(f"TIMELINE_COUNT_DRIFT:{len(timeline)}")

        # Freeze the engine-first timeline before the independent event overlay.
        timeline_payload_sha = canonical_hash(timeline)
        timeline_path = outdir / "macro_event_v5_2025_full_event_timeline.csv"
        with timeline_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(timeline[0]))
            writer.writeheader()
            writer.writerows(timeline)

        vol_by_date = {d: {"direction": direction, "tier": tier, "z": z} for d, direction, tier, z in VOLATILITY_EVENTS}
        macro_by_date = {}
        for row in timeline:
            macro_by_date.setdefault(row["event_date_ny"], []).append(row)

        event_overlay = []
        for d, direction, tier, z in VOLATILITY_EVENTS:
            macros = macro_by_date.get(d, [])
            if not macros:
                event_overlay.append({
                    "volatility_date": d,
                    "volatility_direction": direction,
                    "volatility_tier": tier,
                    "volatility_z": z,
                    "macro_families": "",
                    "macro_severities": "",
                    "macro_predicted_directions": "",
                    "primary_result": "NOT_APPLICABLE",
                })
                continue
            highs = [m for m in macros if m["severity"] == "HIGH"]
            elevated = [m for m in macros if m["severity"] == "ELEVATED"]
            if highs:
                primary = "SAME_EVENT_HIGH_DIRECTION_MATCH" if any(m["predicted_direction"] == direction for m in highs) else "SAME_EVENT_HIGH_DIRECTION_MISMATCH"
            elif elevated:
                primary = "NO_PRIMARY_SIGNAL_ELEVATED_ONLY"
            else:
                primary = "NO_SIGNAL"
            event_overlay.append({
                "volatility_date": d,
                "volatility_direction": direction,
                "volatility_tier": tier,
                "volatility_z": z,
                "macro_families": ";".join(m["family"] for m in macros),
                "macro_severities": ";".join(m["severity"] for m in macros),
                "macro_predicted_directions": ";".join(m["predicted_direction"] for m in macros),
                "primary_result": primary,
            })

        engine_overlay = []
        for m in timeline:
            v = vol_by_date.get(m["event_date_ny"])
            if v is None:
                result = "FALSE_WARNING_HIGH" if m["severity"] == "HIGH" else "NONVOLATILITY_EVENT"
            elif m["severity"] == "HIGH":
                result = "VOLATILITY_SAME_DAY_DIRECTION_MATCH" if m["predicted_direction"] == v["direction"] else "VOLATILITY_SAME_DAY_DIRECTION_MISMATCH"
            elif m["severity"] == "ELEVATED":
                result = "VOLATILITY_SAME_DAY_ELEVATED"
            else:
                result = "VOLATILITY_SAME_DAY_NO_PRIMARY_SIGNAL"
            engine_overlay.append({**m, "volatility_direction": "" if v is None else v["direction"], "volatility_tier": "" if v is None else v["tier"], "overlay_result": result})

        event_overlay_path = outdir / "macro_event_v5_2025_volatility_event_overlay.csv"
        with event_overlay_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(event_overlay[0]))
            writer.writeheader()
            writer.writerows(event_overlay)

        engine_overlay_path = outdir / "macro_event_v5_2025_engine_to_volatility_overlay.csv"
        with engine_overlay_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(engine_overlay[0]))
            writer.writeheader()
            writer.writerows(engine_overlay)

        summary = {
            "status": "PASS_V5_2025_ENGINE_FIRST_REPLAY",
            "engine_id": ENGINE_ID,
            "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
            "model_payload_sha256": model["model_payload_sha256"],
            "engine_timeline_sha256": timeline_payload_sha,
            "eligible_macro_events_2025": len(timeline),
            "family_counts": EXPECTED_2025_COUNTS,
            "severity_counts": {tier: sum(r["severity"] == tier for r in timeline) for tier in ("NORMAL", "ELEVATED", "HIGH")},
            "high_warning_dates": sorted({r["event_date_ny"] for r in timeline if r["severity"] == "HIGH"}),
            "high_false_warning_events": sum(r["overlay_result"] == "FALSE_WARNING_HIGH" for r in engine_overlay),
            "volatility_event_days": len(VOLATILITY_EVENTS),
            "volatility_days_macro_applicable": sum(r["primary_result"] != "NOT_APPLICABLE" for r in event_overlay),
            "volatility_days_not_applicable": sum(r["primary_result"] == "NOT_APPLICABLE" for r in event_overlay),
            "volatility_days_high_signal": sum(r["primary_result"].startswith("SAME_EVENT_HIGH") for r in event_overlay),
            "volatility_days_high_direction_match": sum(r["primary_result"] == "SAME_EVENT_HIGH_DIRECTION_MATCH" for r in event_overlay),
            "volatility_days_elevated_only": sum(r["primary_result"] == "NO_PRIMARY_SIGNAL_ELEVATED_ONLY" for r in event_overlay),
            "volatility_days_no_signal": sum(r["primary_result"] == "NO_SIGNAL" for r in event_overlay),
            "production_write": "NONE",
        }
        (outdir / "macro_event_v5_2025_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        conn.rollback()


if __name__ == "__main__":
    main()
