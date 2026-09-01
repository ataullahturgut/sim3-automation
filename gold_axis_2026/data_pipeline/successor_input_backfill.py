from __future__ import annotations

import hashlib
import io
import json
import os
import re
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import psycopg
import requests
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parent
CONTRACT_PATH = ROOT / "source_contracts_successor.json"
WB_URL = "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
START_MONTH = pd.Timestamp("2016-01-01")
LAST_PIT_MONTH_END = pd.Timestamp("2026-08-31")
FRED_MAP = {
    "DGS10_ALFRED_PIT_ME": "DGS10",
    "DFF_ALFRED_PIT_ME": "DFF",
    "DEXCHUS_ALFRED_PIT_ME": "DEXCHUS",
    "NASDAQ100_ALFRED_PIT_ME": "NASDAQ100",
}
PIPELINE_VERSION = "GOLD_SUCCESSOR_INPUT_BACKFILL_R1_2026-09-01"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def db_url() -> str:
    v = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    return v


def fred_key() -> str:
    v = os.environ.get("FRED_API_KEY", "").strip()
    if not v:
        raise RuntimeError("FRED_API_KEY_NOT_SET")
    return v


def contracts() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def get_with_retry(url: str, *, params: dict | None = None, attempts: int = 5) -> requests.Response:
    last = None
    for i in range(attempts):
        try:
            r = requests.get(
                url,
                params=params,
                timeout=(15, 90),
                headers={"User-Agent": "Gold-Control-Successor-Input-Backfill/1.0"},
            )
            if r.status_code == 429:
                time.sleep(min(60, 8 * (i + 1)))
                last = RuntimeError("HTTP_429")
                continue
            r.raise_for_status()
            return r
        except Exception as exc:
            last = exc
            if i + 1 < attempts:
                time.sleep(min(20, 2 ** i))
    raise RuntimeError(f"HTTP_RETRY_EXHAUSTED:{type(last).__name__}")


def parse_worldbank_monthly(raw_bytes: bytes) -> list[tuple[pd.Timestamp, float]]:
    raw = pd.read_excel(io.BytesIO(raw_bytes), sheet_name="Monthly Prices", header=None)
    gold_col = None
    for rr in range(min(15, len(raw))):
        for cc in range(raw.shape[1]):
            v = str(raw.iat[rr, cc]).strip().lower()
            if v == "gold" or v.startswith("gold "):
                gold_col = cc
                break
        if gold_col is not None:
            break
    if gold_col is None:
        raise RuntimeError("WORLD_BANK_GOLD_COLUMN_NOT_FOUND")

    rows: list[tuple[pd.Timestamp, float]] = []
    for _, row in raw.iterrows():
        m = re.match(r"^(\d{4})M(\d{1,2})$", str(row.iloc[0]).strip(), re.I)
        if not m:
            continue
        month = pd.Timestamp(int(m.group(1)), int(m.group(2)), 1)
        val = pd.to_numeric(row.iloc[gold_col], errors="coerce")
        if month >= START_MONTH and pd.notna(val) and float(val) > 0:
            rows.append((month, float(val)))
    rows.sort(key=lambda x: x[0])
    if not rows or rows[0][0] != START_MONTH:
        raise RuntimeError("WORLD_BANK_2016_START_NOT_PRESENT")
    return rows


def month_ends(start: pd.Timestamp, end: pd.Timestamp) -> list[pd.Timestamp]:
    out = []
    cur = start
    while cur <= end:
        out.append(cur + pd.offsets.MonthEnd(0))
        cur = cur + pd.offsets.MonthBegin(1)
    return out


def fred_asof_snapshot(series_id: str, asof: pd.Timestamp, api_key: str) -> tuple[float, str, str]:
    start = (asof - pd.Timedelta(days=45)).date().isoformat()
    end = asof.date().isoformat()
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "realtime_start": end,
        "realtime_end": end,
        "observation_start": start,
        "observation_end": end,
        "sort_order": "desc",
        "limit": 100,
    }
    r = get_with_retry(FRED_URL, params=params)
    payload = r.json()
    obs = payload.get("observations", []) if isinstance(payload, dict) else []
    valid = []
    for z in obs:
        sv = str(z.get("value", "."))
        if sv in {".", "", "nan", "None"}:
            continue
        try:
            value = float(sv)
        except ValueError:
            continue
        d = pd.Timestamp(str(z.get("date")))
        valid.append((d, value))
    if not valid:
        raise RuntimeError(f"ALFRED_NO_VALID_VALUE:{series_id}:{end}")
    d, value = max(valid, key=lambda x: x[0])
    digest = hashlib.sha256(r.content).hexdigest()
    return value, d.date().isoformat(), digest


def source_registry_row(series_id: str, spec: dict) -> tuple:
    metadata = {k: v for k, v in spec.items() if k not in {
        "semantic", "source", "symbol", "tier", "frequency", "unit", "role", "status", "license_note"
    }}
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
        json.dumps(metadata),
    )


def build_observations(retrieved_at: datetime) -> tuple[list[dict], dict]:
    cfg = contracts()["series"]
    observations: list[dict] = []
    provenance: dict = {}

    wb_resp = get_with_retry(WB_URL)
    wb_hash = hashlib.sha256(wb_resp.content).hexdigest()
    wb_rows = parse_worldbank_monthly(wb_resp.content)
    for month, value in wb_rows:
        obs_ts = month.to_pydatetime().replace(tzinfo=timezone.utc)
        period_end = (month + pd.offsets.MonthEnd(0)).date().isoformat()
        observations.append({
            "series_id": "XAU_MONTHLY_WB_PINKSHEET",
            "observation_ts": obs_ts,
            "value": value,
            "source": "World Bank Pink Sheet",
            "source_symbol": "Gold",
            "provider_as_of": retrieved_at,
            "available_as_of": retrieved_at,
            "first_seen_at": retrieved_at,
            "retrieved_at": retrieved_at,
            "frequency": "monthly",
            "unit": "USD/troy_oz",
            "transform": "LEVEL",
            "quality_status": "APPROVED_HISTORICAL_TARGET_FINAL_VINTAGE_RESEARCH",
            "lineage_id": "WORLDBANK_PINKSHEET_GOLD_MONTHLY_R1",
            "payload_hash": wb_hash,
            "metadata": {
                "target_month": month.strftime("%Y-%m"),
                "period_end": period_end,
                "historical_final_vintage": True,
                "retrieval_time_truth": True,
                "replay_training_lag_months_min": 1,
                "availability_policy": "do_not_backdate_current_worldbank_workbook; historical replay target loader must enforce lag",
                "evidence_class": "HISTORICAL_REPLAY",
            },
        })
    provenance["worldbank"] = {
        "sha256": wb_hash,
        "rows": len(wb_rows),
        "first_month": wb_rows[0][0].strftime("%Y-%m"),
        "last_month": wb_rows[-1][0].strftime("%Y-%m"),
    }

    expected_mes = month_ends(pd.Timestamp("2016-01-31"), LAST_PIT_MONTH_END)
    key = fred_key()
    for out_sid, fred_sid in FRED_MAP.items():
        count_before = len(observations)
        for asof in expected_mes:
            value, source_date, payload_hash = fred_asof_snapshot(fred_sid, asof, key)
            asof_dt = asof.to_pydatetime().replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            observations.append({
                "series_id": out_sid,
                "observation_ts": asof_dt,
                "value": value,
                "source": "Federal Reserve Bank of St. Louis ALFRED",
                "source_symbol": fred_sid,
                "provider_as_of": asof_dt,
                "available_as_of": asof_dt,
                "first_seen_at": retrieved_at,
                "retrieved_at": retrieved_at,
                "frequency": "monthly_snapshot",
                "unit": cfg[out_sid].get("unit"),
                "transform": "LAST_AVAILABLE_ASOF_MONTH_END",
                "quality_status": "APPROVED_HISTORICAL_PIT_RECONSTRUCTION_RESEARCH",
                "lineage_id": f"ALFRED_{fred_sid}_MONTHEND_ASOF_R1",
                "payload_hash": payload_hash,
                "metadata": {
                    "historical_realtime_asof": asof.date().isoformat(),
                    "source_observation_date": source_date,
                    "reconstructed_at": retrieved_at.isoformat(),
                    "historical_reconstruction_not_original_retrieval": True,
                    "retrieval_time_not_backdated": True,
                    "replay_use_contract": "provider_as_of-authoritative historical reconstruction; not observations_as_of storage proof",
                    "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                },
            })
            time.sleep(0.12)
        n = len(observations) - count_before
        if n != len(expected_mes):
            raise RuntimeError(f"ALFRED_COVERAGE_INCOMPLETE:{out_sid}:{n}/{len(expected_mes)}")
        provenance[out_sid] = {
            "rows": n,
            "first_asof": expected_mes[0].date().isoformat(),
            "last_asof": expected_mes[-1].date().isoformat(),
        }

    return observations, provenance


def persist(observations: list[dict], provenance: dict, retrieved_at: datetime) -> dict:
    cfg = contracts()["series"]
    run_id = str(uuid.uuid4())
    git_sha = os.environ.get("GITHUB_SHA")

    with psycopg.connect(db_url(), autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
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
                """,
                [source_registry_row(sid, spec) for sid, spec in cfg.items()],
            )
            cur.execute(
                """
                insert into retrieval_runs
                (run_id, started_at, finished_at, git_sha, pipeline_version, trigger_type,
                 status, observations_read, observations_written, notes, metadata)
                values (%s,%s,%s,%s,%s,%s,%s,%s,0,%s,%s::jsonb)
                on conflict (run_id) do nothing
                """,
                (
                    run_id, retrieved_at, retrieved_at, git_sha, PIPELINE_VERSION,
                    "governed_historical_reconstruction", "SUCCESS", len(observations),
                    "World Bank target final-vintage + ALFRED historical PIT reconstruction; no forecast/model score issued",
                    json.dumps({"provenance": provenance, "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION"}),
                ),
            )

        series_ids = sorted({x["series_id"] for x in observations})
        latest = {}
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select series_id, observation_ts, lineage_id, value, quality_status, first_seen_at
                from canonical_latest
                where series_id = any(%s)
                """,
                (series_ids,),
            )
            for row in cur.fetchall():
                latest[(row["series_id"], row["observation_ts"], row["lineage_id"])] = row

        to_insert = []
        revised = 0
        for o in observations:
            prev = latest.get((o["series_id"], o["observation_ts"], o["lineage_id"]))
            if prev is not None:
                if float(prev["value"]) == float(o["value"]) and str(prev["quality_status"]) == str(o["quality_status"]):
                    continue
                revised += 1
                o = dict(o)
                o["first_seen_at"] = prev["first_seen_at"]
            to_insert.append(o)

        with conn.cursor() as cur:
            if to_insert:
                cur.executemany(
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
                    [
                        {**o, "run_id": run_id, "metadata": json.dumps(o.get("metadata") or {})}
                        for o in to_insert
                    ],
                )

            wb = provenance["worldbank"]
            cur.execute(
                """
                insert into source_vintages
                (source_id, retrieved_at, provider_as_of, content_sha256, content_type, byte_count, metadata)
                values (%s,%s,%s,%s,%s,%s,%s::jsonb)
                on conflict (source_id, content_sha256) do nothing
                """,
                (
                    "WORLD_BANK_PINKSHEET_MONTHLY_GOLD", retrieved_at, retrieved_at,
                    wb["sha256"], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    None, json.dumps({"rows": wb["rows"], "first_month": wb["first_month"], "last_month": wb["last_month"]}),
                ),
            )
            cur.execute(
                "update retrieval_runs set observations_written=%s, finished_at=%s where run_id=%s",
                (len(to_insert), utcnow(), run_id),
            )
        conn.commit()

        verification = {}
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select series_id, count(*) as n, min(observation_ts) as first_ts, max(observation_ts) as last_ts,
                       count(distinct lineage_id) as lineage_count, count(distinct quality_status) as quality_count
                from canonical_latest
                where series_id = any(%s)
                group by series_id
                order by series_id
                """,
                (series_ids,),
            )
            verification["series"] = [dict(r) for r in cur.fetchall()]
            cur.execute("select count(*) as n from forecast_input_snapshots")
            verification["forecast_input_snapshots"] = int(cur.fetchone()["n"])
            cur.execute("select count(*) as n from monthly_forecast_contracts")
            verification["monthly_forecast_contracts"] = int(cur.fetchone()["n"])
            cur.execute("select count(*) as n from derived_feature_snapshots")
            verification["derived_feature_snapshots"] = int(cur.fetchone()["n"])

    return {
        "run_id": run_id,
        "observations_read": len(observations),
        "observations_written": len(to_insert),
        "revised_observations": revised,
        "verification": verification,
    }


def main() -> None:
    retrieved_at = utcnow()
    observations, provenance = build_observations(retrieved_at)
    expected_pit = len(month_ends(pd.Timestamp("2016-01-31"), LAST_PIT_MONTH_END))
    wb_n = sum(1 for x in observations if x["series_id"] == "XAU_MONTHLY_WB_PINKSHEET")
    print(f"PREWRITE_WORLD_BANK_ROWS={wb_n}")
    print(f"PREWRITE_EXPECTED_PIT_ROWS_PER_SERIES={expected_pit}")
    print("PREWRITE_MODEL_SCORE_RUN=NONE")
    print("PREWRITE_FORECAST_ISSUANCE=NONE")
    print("RAW_MARKET_VALUES_LOGGED=NO")

    result = persist(observations, provenance, retrieved_at)
    print(f"RUN_ID={result['run_id']}")
    print(f"OBSERVATIONS_READ={result['observations_read']}")
    print(f"OBSERVATIONS_WRITTEN={result['observations_written']}")
    print(f"REVISED_OBSERVATIONS={result['revised_observations']}")
    for row in result["verification"]["series"]:
        print(
            "VERIFY_SERIES "
            f"series_id={row['series_id']} n={row['n']} first_ts={row['first_ts']} last_ts={row['last_ts']} "
            f"lineage_count={row['lineage_count']} quality_count={row['quality_count']}"
        )
    print(f"VERIFY_FORECAST_INPUT_SNAPSHOTS={result['verification']['forecast_input_snapshots']}")
    print(f"VERIFY_MONTHLY_FORECAST_CONTRACTS={result['verification']['monthly_forecast_contracts']}")
    print(f"VERIFY_DERIVED_FEATURE_SNAPSHOTS={result['verification']['derived_feature_snapshots']}")
    print("DATABASE_WRITE_CLASS=HISTORICAL_REPLAY_RECONSTRUCTION_ONLY")
    print("PROSPECTIVE_CLAIM=NO")
    print("MODEL_SCORE_RUN=NONE")
    print("SUCCESSOR_INPUT_BACKFILL_SUCCESS")


if __name__ == "__main__":
    main()
