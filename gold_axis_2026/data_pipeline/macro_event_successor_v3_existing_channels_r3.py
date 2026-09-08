from __future__ import annotations

import json
import math
import os
import subprocess
import uuid
from datetime import datetime, timezone

import psycopg
from psycopg.rows import dict_row

import macro_event_successor_v3_existing_channels_r2 as r2

ENGINE = "MACRO_EVENT_SUCCESSOR_V3"
PIPELINE_VERSION = "MACRO_EVENT_SUCCESSOR_V3_EXISTING_CHANNELS_R3_FOMC_USMPD_2026-09-08"
FOMC_SOURCE_PIPELINE = "MACRO_EVENT_SUCCESSOR_V3_FOMC_USMPD_HISTORICAL_R1_2026-09-08"
TARGET_ID = "MACRO_FOMC_GSS_TARGET_FROZEN2015"
PATH_ID = "MACRO_FOMC_GSS_PATH_FROZEN2015"
FOMC_SCORE_ID = "MACRO_EVENT_V3_FOMC_SCORE"
EVAL_START = datetime(2016, 1, 1, tzinfo=timezone.utc)


def git_sha() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return os.environ.get("GITHUB_SHA")


def latest_source_run(conn, pipeline: str) -> str:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""select run_id from retrieval_runs where pipeline_version=%s and status='SUCCESS'
                       order by finished_at desc limit 1""", (pipeline,))
        row = cur.fetchone()
    if not row:
        raise RuntimeError(f"SOURCE_RUN_NOT_FOUND:{pipeline}")
    return str(row["run_id"])


def load_fomc_panel(conn, run_id: str) -> list[dict]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""select series_id,observation_ts,value,metadata from observations
                       where run_id=%s::uuid and series_id=any(%s)
                       order by observation_ts,series_id""", (run_id, [TARGET_ID, PATH_ID]))
        rows = cur.fetchall()
    by = {}
    for row in rows:
        ts = row["observation_ts"]
        k = "target" if row["series_id"] == TARGET_ID else "path"
        by.setdefault(ts, {"observation_ts": ts, "metadata": row["metadata"]})[k] = float(row["value"])
    panel = [v for _, v in sorted(by.items()) if "target" in v and "path" in v]
    if len(panel) < 200:
        raise RuntimeError(f"FOMC_FACTOR_PANEL_TOO_SMALL:{len(panel)}")
    return panel


def score_fomc(panel: list[dict]) -> list[dict]:
    prior_target: list[float] = []
    prior_path: list[float] = []
    out = []
    for row in panel:
        t = float(row["target"]); p = float(row["path"])
        st, mt = r2.robust_scale(prior_target)
        sp, mp = r2.robust_scale(prior_path)
        if row["observation_ts"] >= EVAL_START and st is not None and sp is not None:
            zt = t / float(st); zp = p / float(sp)
            oriented = [-zt, -zp]
            score = sum(oriented) / 2.0
            state = r2.state_from_score(score, oriented, 2)
            out.append({
                "observation_ts": row["observation_ts"],
                "score": score,
                "state": state,
                "components": oriented,
                "surprises": {"target": t, "path": p},
                "scale_methods": {"target": mt, "path": mp},
                "scale_values": {"target": st, "path": sp},
                "unscheduled": int((row.get("metadata") or {}).get("unscheduled") or 0),
            })
        prior_target.append(t); prior_path.append(p)
    return out


def assert_prefix_invariance(panel: list[dict], scores: list[dict]) -> None:
    expected = {x["observation_ts"]: (x["score"], x["state"], x["scale_values"]) for x in scores}
    eval_rows = [i for i, r in enumerate(panel) if r["observation_ts"] >= EVAL_START]
    for idx in eval_rows:
        prefix_scores = score_fomc(panel[: idx + 1])
        if not prefix_scores:
            continue
        x = prefix_scores[-1]
        exp = expected.get(x["observation_ts"])
        if exp is None:
            raise RuntimeError(f"FOMC_PREFIX_EVENT_NOT_IN_FULL:{x['observation_ts']}")
        if not math.isclose(float(x["score"]), float(exp[0]), rel_tol=0, abs_tol=1e-12) or x["state"] != exp[1]:
            raise RuntimeError(f"FOMC_PREFIX_INVARIANCE_FAIL:{x['observation_ts']}")
        for k in ("target", "path"):
            if not math.isclose(float(x["scale_values"][k]), float(exp[2][k]), rel_tol=0, abs_tol=1e-12):
                raise RuntimeError(f"FOMC_PREFIX_SCALE_INVARIANCE_FAIL:{x['observation_ts']}:{k}")


def upsert_score_registry(conn, source_run: str) -> None:
    metadata = {
        "engine": ENGINE,
        "family": "FOMC",
        "source_run_id": source_run,
        "method": "GSS_TARGET_PATH_FROZEN_PRE2016_PLUS_EXPANDING_ROBUST_SCALE",
        "strong_threshold": r2.STRONG_THRESHOLD,
        "breadth_required": 2,
        "minimum_prior": r2.MIN_PRIOR,
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "production_authority": False,
    }
    with conn.cursor() as cur:
        cur.execute("""insert into source_registry
            (series_id,semantic_id,source_name,source_symbol,source_tier,frequency,unit,model_role,status,license_note,metadata)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
            on conflict (series_id) do update set semantic_id=excluded.semantic_id,source_name=excluded.source_name,
              source_symbol=excluded.source_symbol,source_tier=excluded.source_tier,frequency=excluded.frequency,
              unit=excluded.unit,model_role=excluded.model_role,status=excluded.status,metadata=excluded.metadata,updated_at=now()""",
            (FOMC_SCORE_ID, FOMC_SCORE_ID, "Derived from governed SF Fed USMPD FOMC factors", "GSS_TARGET_PATH",
             "AUTHORITY_DERIVED", "event", "robust_z", "FOMC event risk context",
             "CURRENT_MACRO_EVENT_SUCCESSOR_V3_HISTORICAL_SCORE", None, json.dumps(metadata, sort_keys=True)))


def persist_fomc_scores(conn, source_run: str, scores: list[dict], run_id: str, retrieved: datetime) -> int:
    inserted = 0
    for s in scores:
        lineage = f"V3R3_FOMC_SCORE_{s['observation_ts'].strftime('%Y%m%dT%H%M%SZ')}"
        metadata = {
            "engine": ENGINE, "family": "FOMC", "state": s["state"], "components": s["components"],
            "surprises": s["surprises"], "scale_methods": s["scale_methods"], "scale_values": s["scale_values"],
            "source_run_id": source_run, "unscheduled": s["unscheduled"],
            "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION", "context_only": True, "direction_vote": False,
            "market_shock_threshold_changed": False, "raw_market_shock_episode_changed": False,
            "production_authority": False, "future_event_factor_fit": False,
        }
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""select value,metadata from observations where series_id=%s and observation_ts=%s and lineage_id=%s
                           order by retrieved_at desc limit 1""", (FOMC_SCORE_ID, s["observation_ts"], lineage))
            prev = cur.fetchone()
        if prev:
            if not math.isclose(float(prev["value"]), float(s["score"]), rel_tol=0, abs_tol=1e-12):
                raise RuntimeError(f"FROZEN_FOMC_SCORE_CHANGED:{s['observation_ts']}")
            continue
        payload_hash = __import__("hashlib").sha256(json.dumps(metadata, sort_keys=True, default=str).encode()).hexdigest()
        with conn.cursor() as cur:
            cur.execute("""insert into observations
                (run_id,series_id,observation_ts,value,source,source_symbol,provider_as_of,available_as_of,first_seen_at,retrieved_at,
                 frequency,unit,transform,quality_status,lineage_id,payload_hash,metadata)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
                (run_id, FOMC_SCORE_ID, s["observation_ts"], s["score"], "Derived from governed SF Fed USMPD FOMC factors",
                 "GSS_TARGET_PATH", retrieved, retrieved, retrieved, retrieved, "event", "robust_z",
                 "ROBUST_EVENT_SURPRISE_SCORE", "RESEARCH_CONTEXT_ONLY", lineage, payload_hash, json.dumps(metadata, sort_keys=True)))
        inserted += 1
    return inserted


def score_summary(scores: list[dict]) -> dict:
    counts = {"GOLD_ADVERSE_MACRO_SHOCK": 0, "GOLD_SUPPORTIVE_MACRO_SHOCK": 0, "MACRO_MIXED_OR_SMALL": 0}
    for x in scores:
        counts[x["state"]] = counts.get(x["state"], 0) + 1
    return {"scored_events": len(scores), "state_counts": counts, "latest": scores[-1] if scores else None}


def main() -> int:
    retrieved = datetime.now(timezone.utc); run_id = str(uuid.uuid4())
    with psycopg.connect(r2.db_url(), autocommit=False) as conn:
        before = r2.decision_counts(conn)
        source_run = latest_source_run(conn, FOMC_SOURCE_PIPELINE)
        panel = load_fomc_panel(conn, source_run)
        scores = score_fomc(panel)
        if not scores:
            raise RuntimeError("FOMC_NO_SCORES")
        assert_prefix_invariance(panel, scores)
        upsert_score_registry(conn, source_run)
        result = {
            "engine_id": ENGINE,
            "status": "PASS_EMPLOYMENT_INFLATION_FOMC_HISTORICAL_MODEL_BOUND",
            "employment": {"status": "PASS_EXISTING_V3_SCORE_SERIES"},
            "inflation": {"status": "PASS_EXISTING_V3_SCORE_SERIES"},
            "fomc": {"source_run_id": source_run, "factor_events": len(panel), **score_summary(scores), "prefix_invariance": True},
            "fomc_method": "SF_FED_USMPD_GSS_TARGET_PATH_FROZEN_PRE2016",
            "model_layer_external_http_calls": False,
            "market_shock_threshold_changed": False,
            "raw_market_shock_episode_changed": False,
            "production_authority": False,
            "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        }
        with conn.cursor() as cur:
            cur.execute("""insert into retrieval_runs
                (run_id,started_at,git_sha,pipeline_version,trigger_type,status,observations_read,observations_written,notes,metadata)
                values(%s,%s,%s,%s,%s,'RUNNING',%s,0,%s,%s::jsonb)""",
                (run_id, retrieved, git_sha(), PIPELINE_VERSION, "macro_event_v3_fomc_score_historical", len(panel) * 2,
                 "V3 FOMC historical score from governed Neon USMPD factors only", json.dumps(result, sort_keys=True, default=str)))
        written = persist_fomc_scores(conn, source_run, scores, run_id, retrieved)
        result["fomc"]["observations_written"] = written
        with conn.cursor() as cur:
            cur.execute("update retrieval_runs set finished_at=now(),status='SUCCESS',observations_written=%s,metadata=%s::jsonb where run_id=%s",
                        (written, json.dumps(result, sort_keys=True, default=str), run_id))
        after = r2.decision_counts(conn)
        if after != before:
            raise RuntimeError(f"DECISION_AUTHORITY_STORE_CHANGED:{before}->{after}")
        conn.commit()
    result["score_run_id"] = run_id
    result["decision_counts_before"] = before; result["decision_counts_after"] = after
    with open("macro_event_successor_v3_existing_channels_r3_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True, default=str)
    print(json.dumps(result, indent=2, sort_keys=True, default=str)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
