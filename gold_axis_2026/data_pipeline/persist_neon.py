from __future__ import annotations

import json
import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parent
CONTRACTS_PATH = ROOT / "source_contracts.json"
DIRECT_CONTRACTS_PATH = ROOT / "source_contracts_direct.json"
TWELVE_VALIDATED_CONTRACTS_PATH = ROOT / "source_contracts_twelve_validated.json"


def _db_url() -> str:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return url


def _load_contracts() -> dict:
    """Merge frozen base contracts, direct-authority contracts, and validated vendor overrides.

    Direct-authority records must use new series IDs. Twelve Data validation records are
    intentionally field-level overrides for already-declared Twelve Data series IDs only;
    they may update a symbol/status after live vendor identity validation but may not
    change semantic identity or provider.
    """
    base = json.loads(CONTRACTS_PATH.read_text(encoding="utf-8"))
    merged = dict(base)
    series = dict(base.get("series", {}))

    if DIRECT_CONTRACTS_PATH.exists():
        direct = json.loads(DIRECT_CONTRACTS_PATH.read_text(encoding="utf-8"))
        overlap = sorted(set(series).intersection(direct.get("series", {})))
        if overlap:
            raise RuntimeError(f"DIRECT_CONTRACT_SERIES_ID_COLLISION:{overlap}")
        series.update(direct.get("series", {}))
        merged["direct_contract_version"] = direct.get("version")

    if TWELVE_VALIDATED_CONTRACTS_PATH.exists():
        validated = json.loads(TWELVE_VALIDATED_CONTRACTS_PATH.read_text(encoding="utf-8"))
        for sid, patch in validated.get("series", {}).items():
            if sid not in series:
                raise RuntimeError(f"TWELVE_VALIDATION_UNKNOWN_SERIES:{sid}")
            current = dict(series[sid])
            if current.get("source") != "Twelve Data":
                raise RuntimeError(f"TWELVE_VALIDATION_PROVIDER_MISMATCH:{sid}:{current.get('source')}")
            forbidden = {"semantic", "source", "tier", "role"}.intersection(patch)
            if forbidden:
                raise RuntimeError(f"TWELVE_VALIDATION_FORBIDDEN_FIELDS:{sid}:{sorted(forbidden)}")
            current.update(patch)
            series[sid] = current
        merged["twelve_validated_contract_version"] = validated.get("version")

    merged["series"] = series
    return merged


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
        select series_id, observation_ts, lineage_id, value, quality_status, first_seen_at
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


def _prepare_observation(o: dict) -> dict:
    return {**o, "metadata": json.dumps(o.get("metadata") or {})}


def _insert_observations(cur, rows: list[dict]) -> None:
    if not rows:
        return
    sql = """
        insert into observations
        (run_id, series_id, observation_ts, value, source, source_symbol,
         provider_as_of, available_as_of, first_seen_at, retrieved_at,
         frequency, unit, transform, quality_status, lineage_id, payload_hash, metadata)
        values
        (%(run_id)s, %(series_id)s, %(observation_ts)s, %(value)s, %(source)s, %(source_symbol)s,
         %(provider_as_of)s, %(available_as_of)s, %(first_seen_at)s, %(retrieved_at)s,
         %(frequency)s, %(unit)s, %(transform)s, %(quality_status)s, %(lineage_id)s,
         %(payload_hash)s, %(metadata)s::jsonb)
    """
    cur.executemany(sql, [_prepare_observation(o) for o in rows])


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
        revised = 0
        to_insert: list[dict] = []

        for raw in observations:
            o = dict(raw)
            key = (o["series_id"], o["observation_ts"], o["lineage_id"])
            prev = latest.get(key)

            # A new source-file hash alone is NOT a data revision. Revision means the
            # actual observation value or its quality classification changed.
            if prev is not None:
                same = (
                    float(prev["value"]) == float(o["value"])
                    and str(prev["quality_status"]) == str(o["quality_status"])
                )
                if same:
                    continue
                revised += 1
                o["first_seen_at"] = prev["first_seen_at"].isoformat()

            to_insert.append(o)

        written = len(to_insert)

        with conn.cursor() as cur:
            _insert_observations(cur, to_insert)

            vintages = bundle.get("vintages", [])
            if vintages:
                cur.executemany(
                    """
                    insert into source_vintages
                    (source_id, retrieved_at, provider_as_of, content_sha256, content_type, byte_count, metadata)
                    values (%s,%s,%s,%s,%s,%s,%s::jsonb)
                    on conflict (source_id, content_sha256) do nothing
                    """,
                    [
                        (
                            v["source_id"], v["retrieved_at"], v.get("provider_as_of"),
                            v["content_sha256"], v.get("content_type"), v.get("byte_count"),
                            json.dumps(v.get("metadata") or {}),
                        )
                        for v in vintages
                    ],
                )

            quality_events = bundle.get("quality_events", [])
            if quality_events:
                cur.executemany(
                    """
                    insert into quality_events
                    (run_id, series_id, event_ts, severity, code, message, metadata)
                    values (%s,%s,%s,%s,%s,%s,%s::jsonb)
                    """,
                    [
                        (
                            q.get("run_id"), q.get("series_id"), q["event_ts"], q["severity"],
                            q["code"], q["message"], json.dumps(q.get("metadata") or {}),
                        )
                        for q in quality_events
                    ],
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
