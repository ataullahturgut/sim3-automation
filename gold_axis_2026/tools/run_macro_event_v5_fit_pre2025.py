from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from macro_event_v5_core import (
    RawEvent,
    fit_ols,
    linear_quantile,
    loo_sign_accuracy,
    predict_ols,
    score_family,
    severity,
    severity_thresholds,
    stable_float,
)

ENGINE_ID = "MACRO_EVENT_SUCCESSOR_V5_PRE2025"
FORMATION_START = datetime(2016, 1, 1, tzinfo=timezone.utc)
CUTOFF = datetime(2025, 1, 1, tzinfo=timezone.utc)
REACTION_START = datetime(2023, 1, 1, tzinfo=timezone.utc)
PREREG_BLOB_SHA = "58f3ef649a44c964a41bfa0261f5410322fb8651"

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

EXPECTED_EVENT_COUNTS = {"EMPLOYMENT": 106, "INFLATION": 107, "FOMC": 71}
EXPECTED_REACTION_SUPPORT = {"EMPLOYMENT": 23, "INFLATION": 24, "FOMC": 16}


def canonical_hash(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_rows(conn, run_id: str, series_ids: list[str], scheduled_fomc: bool = False):
    extra = "and coalesce(metadata->>'unscheduled','0')='0'" if scheduled_fomc else ""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            f"""
            select series_id, observation_ts, value
            from observations
            where run_id=%s::uuid
              and series_id=any(%s)
              and observation_ts >= %s
              and observation_ts < %s
              {extra}
            order by observation_ts, series_id
            """,
            (run_id, series_ids, FORMATION_START, CUTOFF),
        )
        rows = cur.fetchall()
    if any(r["observation_ts"] >= CUTOFF for r in rows):
        raise RuntimeError("POST_2024_ROW_ENTERED_V5_FIT")
    return rows


def group_complete(rows, required_series: list[str]) -> dict[datetime, dict[str, float]]:
    out: dict[datetime, dict[str, float]] = {}
    for row in rows:
        ts = row["observation_ts"]
        sid = str(row["series_id"])
        bucket = out.setdefault(ts, {})
        if sid in bucket:
            raise RuntimeError(f"DUPLICATE_SOURCE_ROW:{ts.isoformat()}:{sid}")
        bucket[sid] = float(row["value"])
    required = set(required_series)
    incomplete = {ts: sorted(required - set(vals)) for ts, vals in out.items() if set(vals) != required}
    if incomplete:
        raise RuntimeError(f"INCOMPLETE_SOURCE_EVENTS:{incomplete}")
    return out


def load_events(conn) -> dict[str, list[RawEvent]]:
    emp_rows = load_rows(conn, SOURCE_RUNS["EMPLOYMENT"], list(EMP_SERIES.values()))
    emp = group_complete(emp_rows, list(EMP_SERIES.values()))
    emp_events = []
    for ts, m in sorted(emp.items()):
        emp_events.append(RawEvent("EMPLOYMENT", ts, {
            "nfp": m[EMP_SERIES["nfp_actual"]] - m[EMP_SERIES["nfp_consensus"]],
            "unemp": m[EMP_SERIES["unemp_actual"]] - m[EMP_SERIES["unemp_consensus"]],
            "ahe": m[EMP_SERIES["ahe_actual"]] - m[EMP_SERIES["ahe_consensus"]],
        }))

    inf_rows = load_rows(conn, SOURCE_RUNS["INFLATION"], list(INF_SERIES.values()))
    inf = group_complete(inf_rows, list(INF_SERIES.values()))
    inf_events = []
    for ts, m in sorted(inf.items()):
        inf_events.append(RawEvent("INFLATION", ts, {
            "cpi": m[INF_SERIES["cpi_actual"]] - m[INF_SERIES["cpi_consensus"]],
            "core": m[INF_SERIES["core_actual"]] - m[INF_SERIES["core_consensus"]],
        }))

    fomc_rows = load_rows(conn, SOURCE_RUNS["FOMC"], list(FOMC_SERIES.values()), scheduled_fomc=True)
    fomc = group_complete(fomc_rows, list(FOMC_SERIES.values()))
    fomc_events = []
    for ts, m in sorted(fomc.items()):
        fomc_events.append(RawEvent("FOMC", ts, {
            "target": m[FOMC_SERIES["target"]],
            "path": m[FOMC_SERIES["path"]],
        }))

    result = {"EMPLOYMENT": emp_events, "INFLATION": inf_events, "FOMC": fomc_events}
    counts = {k: len(v) for k, v in result.items()}
    if counts != EXPECTED_EVENT_COUNTS:
        raise RuntimeError(f"PRE2025_EVENT_COUNT_DRIFT:{counts}")
    return result


def load_reaction_prices(conn, scored_by_family):
    needed = set()
    for scored in scored_by_family.values():
        for e in scored:
            if e.status == "SCORED" and REACTION_START <= e.release_ts < CUTOFF:
                needed.add(e.release_ts - timedelta(minutes=1))
                needed.add(e.release_ts + timedelta(minutes=14))
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            select observation_ts, close
            from xau_intraday_research_cache_1m
            where observation_ts=any(%s)
            order by observation_ts
            """,
            (list(sorted(needed)),),
        )
        rows = cur.fetchall()
    prices = {r["observation_ts"]: float(r["close"]) for r in rows}
    return prices


def reaction_dataset(scored, prices):
    xs, ys, timestamps = [], [], []
    component_order = sorted(next(e.z for e in scored if e.z is not None))
    for e in scored:
        if e.z is None or not (REACTION_START <= e.release_ts < CUTOFF):
            continue
        pre = prices.get(e.release_ts - timedelta(minutes=1))
        post = prices.get(e.release_ts + timedelta(minutes=14))
        if pre is None or post is None:
            continue
        if pre <= 0.0 or post <= 0.0:
            raise RuntimeError(f"NONPOSITIVE_XAU_REACTION_PRICE:{e.release_ts.isoformat()}")
        r15 = 100.0 * math.log(post / pre)
        xs.append([float(e.z[k]) for k in component_order])
        ys.append(float(r15))
        timestamps.append(e.release_ts)
    return component_order, xs, ys, timestamps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--database-url", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    with psycopg.connect(args.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read read only")
        raw_by_family = load_events(conn)
        scored_by_family = {family: score_family(events) for family, events in raw_by_family.items()}
        prices = load_reaction_prices(conn, scored_by_family)

        families = {}
        timeline_rows = []
        for family in ("EMPLOYMENT", "INFLATION", "FOMC"):
            scored = scored_by_family[family]
            thresholds = severity_thresholds(scored)
            component_order, xs, ys, reaction_ts = reaction_dataset(scored, prices)
            if len(xs) != EXPECTED_REACTION_SUPPORT[family]:
                raise RuntimeError(f"REACTION_SUPPORT_DRIFT:{family}:{len(xs)}/{EXPECTED_REACTION_SUPPORT[family]}")
            direction = fit_ols(xs, ys)
            direction["loo_sign_accuracy"] = loo_sign_accuracy(xs, ys)
            direction["support_n"] = len(xs)
            direction["reaction_start"] = min(reaction_ts).isoformat()
            direction["reaction_end"] = max(reaction_ts).isoformat()
            direction["component_order"] = component_order
            direction["actual_r15_abs_q75"] = linear_quantile([abs(y) for y in ys], 0.75)
            direction["actual_r15_abs_q90"] = linear_quantile([abs(y) for y in ys], 0.90)

            scored_count = sum(e.status == "SCORED" for e in scored)
            families[family] = {
                "source_run_id": SOURCE_RUNS[family],
                "event_count": len(scored),
                "scored_event_count": scored_count,
                "component_order": component_order,
                "intensity_thresholds": {k: stable_float(v) for k, v in thresholds.items()},
                "direction_fit": {
                    "intercept": stable_float(direction["intercept"]),
                    "coefficients": [stable_float(v) for v in direction["coefficients"]],
                    "rmse": stable_float(direction["rmse"]),
                    "loo_sign_accuracy": stable_float(direction["loo_sign_accuracy"]),
                    "support_n": direction["support_n"],
                    "reaction_start": direction["reaction_start"],
                    "reaction_end": direction["reaction_end"],
                    "actual_r15_abs_q75": stable_float(direction["actual_r15_abs_q75"]),
                    "actual_r15_abs_q90": stable_float(direction["actual_r15_abs_q90"]),
                },
            }

            for e in scored:
                pred = None
                pred_direction = None
                if e.z is not None:
                    pred = predict_ols(direction, [float(e.z[k]) for k in component_order])
                    pred_direction = "UP" if pred > 0.0 else "DOWN" if pred < 0.0 else "FLAT"
                timeline_rows.append({
                    "family": family,
                    "release_ts": e.release_ts.isoformat(),
                    "status": e.status,
                    "raw_components_json": json.dumps(e.raw_components, sort_keys=True),
                    "z_json": json.dumps(e.z, sort_keys=True) if e.z is not None else "",
                    "shock_intensity": "" if e.shock_intensity is None else f"{e.shock_intensity:.12g}",
                    "severity": severity(e.shock_intensity, thresholds),
                    "predicted_r15": "" if pred is None else f"{pred:.12g}",
                    "predicted_direction": pred_direction or "",
                })

        fingerprint_payload = {
            family: [
                [e.release_ts.isoformat(), {k: stable_float(v) for k, v in sorted(e.components.items())}]
                for e in raw_by_family[family]
            ]
            for family in sorted(raw_by_family)
        }
        model = {
            "engine_id": ENGINE_ID,
            "status": "FROZEN_PRE2025_MODEL_PARAMETERS",
            "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
            "production_write": "NONE",
            "formation_start": FORMATION_START.isoformat(),
            "cutoff_exclusive": CUTOFF.isoformat(),
            "reaction_fit_window": [REACTION_START.isoformat(), CUTOFF.isoformat()],
            "preregistration_blob_sha": PREREG_BLOB_SHA,
            "source_input_fingerprint_sha256": canonical_hash(fingerprint_payload),
            "method": {
                "standardization": "EXPANDING_PRIOR_MAD_1P4826_WITH_IQR_NORMAL_FALLBACK",
                "shock_intensity": "MEAN_ABS_STANDARDIZED_SURPRISE",
                "severity": "FAMILY_PRE2025_Q75_Q90",
                "direction": "FAMILY_OLS_R15_ON_STANDARDIZED_SURPRISES",
                "r15": "100*LN(XAU_RELEASE_PLUS_14M/XAU_RELEASE_MINUS_1M)",
                "fomc": "SCHEDULED_ONLY_GSS_TARGET_PATH",
            },
            "families": families,
        }
        model["model_payload_sha256"] = canonical_hash(model)

        max_ts = max(e.release_ts for events in raw_by_family.values() for e in events)
        if max_ts >= CUTOFF:
            raise RuntimeError("V5_FIT_CUTOFF_VIOLATION")
        model["max_training_release_ts"] = max_ts.isoformat()

        model_path = outdir / "macro_event_v5_pre2025_model.json"
        model_path.write_text(json.dumps(model, indent=2, sort_keys=True), encoding="utf-8")

        timeline_path = outdir / "macro_event_v5_pre2025_timeline.csv"
        with timeline_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(timeline_rows[0]))
            writer.writeheader()
            writer.writerows(sorted(timeline_rows, key=lambda r: (r["release_ts"], r["family"])))

        summary = {
            "status": "PASS_PRE2025_ONLY",
            "engine_id": ENGINE_ID,
            "model_file": model_path.name,
            "model_payload_sha256": model["model_payload_sha256"],
            "max_training_release_ts": model["max_training_release_ts"],
            "family_event_counts": {k: v["event_count"] for k, v in families.items()},
            "family_scored_counts": {k: v["scored_event_count"] for k, v in families.items()},
            "reaction_support": {k: v["direction_fit"]["support_n"] for k, v in families.items()},
            "production_write": "NONE",
        }
        (outdir / "macro_event_v5_pre2025_fit_summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        conn.rollback()


if __name__ == "__main__":
    main()
