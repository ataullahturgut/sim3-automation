from __future__ import annotations

import json
import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parent
CONTRACTS_PATH = ROOT / "source_contracts.json"


def _db_url() -> str:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return url


def _load_contracts() -> dict:
    return json.loads(CONTRACTS_PATH.read_text(encoding="utf-8"))


def _source_row(series_id: str, spec: dict) -> tuple:
    return (
        series_id,
        spec.get("semantic") or series_id,
        spec.get("source") or "UNRESOLVED",
        spec.get("symbol"),
        spec.get("tier") or "UNRESOLVED",
        spec.get("frequency") or "UNRESOLVED",
        spec.get("unit"),
        spec.get("role"),
        spec.get("status") or "UNRESOLVED",
        spec.get("license_note"),
        json.dumps({k: v for k, v in spec.items() if k not in {
            "semantic", "source", "symbol", "tier", "frequency", "unit", "role", "status", "license_note"
        }}),
    )


def seed_source_registry(conn) -> None:
    contracts = _load_contracts().get("series", {})
    rows = [_source_row(sid, spec) for sid, spec in contracts.items() if spec.get("source")]
    sql = """
        insert into source_registry
        (series_id, semantic_id, source_name, source_symbol, source_tier, frequency,
         unit, model_role, status, license_note, metadata)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
        on conflict (series_id) do update set
          semantic_id=excluded.semantic_id,
          source_name=excluded.source_name,
          source_symbol=excluded.source_symbol,
          source_tier=excluded.source_tier,
          frequency=excluded.frequency,
          unit=excluded.unit,
          model_role=excluded.model_role,
          status=excluded.status,
          license_note=excluded.license_note,
          metadata=excluded.metadata,
          updated_at=now()
    """
    with conn.cursor() as cur:
        cur.executemany(sql, rows)


def _latest_map(conn, series_ids: list[str]) -> dict:
    if not series_ids:
        return {}
    sql = """
        select series_id, observation_ts, lineage_id, value, quality_status, payload_hash
        from canonical_latest
        where series_id = any(%s)
    """
    out = {}
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql, (series_ids,))
        for row in cur.fetchall():
            key = (row["series_id"], row["observation_ts"].isoformat(), row["lineage_id"])
            out[key] = row
    return out


def _insert_observation(cur, o: dict) -> None:
    cur.execute(
        """
        insert into observations
        (run_id, series_id, observation_ts, value, source, source_symbol,
         provider_as_of, available_as_of, first_seen_at, retrieved_at,
         frequency, unit, transform, quality_status, lineage_id, payload_hash, metadata)
        values
        (%(run_id)s, %(series_id)s, %(observation_ts)s, %(value)s, %(source)s, %(source_symbol)s,
         %(provider_as_of)s, %(available_as_of)s, %(first_seen_at)s, %(retrieved_at)s,
         %(frequency)s, %(unit)s, %(transform)s, %(quality_status)s, %(lineage_id)s,
         %(payload_hash)s, %(metadata)s::jsonb)
        """,
        {**o, "metadata": json.dumps(o.get("metadata") or {})},
    )


def persist_bundle(bundle: dict) -> dict:
    observations = bundle.get("observations", [])
    series_ids = sorted({o["series_id"] for o in observations})
    errors = [x for x in bundle.get("quality_events", []) if x.get("severity") == "ERROR"]
    run_status = "PARTIAL" if errors else "SUCCESS"

    with psycopg.connect(_db_url(), autocommit=False) as conn:
        seed_source_registry(conn)

        with conn.cursor() as cur:
            cur.execute(
                """
                insert into retrieval_runs
                (run_id, started_at, finished_at, git_sha, pipeline_version, trigger_type,
                 status, observations_read, observations_written, notes, metadata)
                values (%s,%s,%s,%s,%s,%s,%s,%s,0,%s,%s::jsonb)
                on conflict (run_id) do nothing
                """,
                (
                    bundle["run_id"], bundle["started_at"], bundle["finished_at"],
                    os.environ.get("GITHUB_SHA"), bundle["pipeline_version"], bundle.get("mode"),
                    run_status, len(observations),
                    "Collector completed with source errors" if errors else None,
                    json.dumps({"mode": bundle.get("mode")}),
                ),
            )

        latest = _latest_map(conn, series_ids)
        written = 0
        revised = 0

        with conn.cursor() as cur:
            for o in observations:
                key = (o["series_id"], o["observation_ts"], o["lineage_id"])
                prev = latest.get(key)
                same = False
                if prev is not None:
                    same = (
                        float(prev["value"]) == float(o["value"])
                        and str(prev["quality_status"]) == str(o["quality_status"])
                        and (prev["payload_hash"] or None) == (o.get("payload_hash") or None)
                    )
                if same:
                    continue
                if prev is not None:
                    revised += 1
                    # Preserve first-seen time across revisions.
                    with conn.cursor(row_factory=dict_row) as qcur:
                        qcur.execute(
                            """
                            select first_seen_at from canonical_latest
                            where series_id=%s and observation_ts=%s and lineage_id=%s
                            """,
                            (o["series_id"], o["observation_ts"], o["lineage_id"]),
                        )
                        row = qcur.fetchone()
                        if row:
                            o = dict(o)
                            o["first_seen_at"] = row["first_seen_at"].isoformat()
                _insert_observation(cur, o)
                written += 1

            for v in bundle.get("vintages", []):
                cur.execute(
                    """
                    insert into source_vintages
                    (source_id, retrieved_at, provider_as_of, content_sha256, content_type, byte_count, metadata)
                    values (%s,%s,%s,%s,%s,%s,%s::jsonb)
                    on conflict (source_id, content_sha256) do nothing
                    """,
                    (
                        v["source_id"], v["retrieved_at"], v.get("provider_as_of"),
                        v["content_sha256"], v.get("content_type"), v.get("byte_count"),
                        json.dumps(v.get("metadata") or {}),
                    ),
                )

            for q in bundle.get("quality_events", []):
                cur.execute(
                    """
                    insert into quality_events
                    (run_id, series_id, event_ts, severity, code, message, metadata)
                    values (%s,%s,%s,%s,%s,%s,%s::jsonb)
                    """,
                    (
                        q.get("run_id"), q.get("series_id"), q["event_ts"], q["severity"],
                        q["code"], q["message"], json.dumps(q.get("metadata") or {}),
                    ),
                )

            cur.execute(
                """
                update retrieval_runs
                set observations_written=%s, finished_at=%s, status=%s
                where run_id=%s
                """,
                (written, bundle["finished_at"], run_status, bundle["run_id"]),
            )

        conn.commit()

    return {
        "run_id": bundle["run_id"],
        "status": run_status,
        "observations_read": len(observations),
        "observations_written": written,
        "revised_observations": revised,
        "quality_errors": len(errors),
    }
