from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import os
import subprocess
import sys
import time
import uuid
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
import requests
from psycopg.rows import dict_row

UTC = timezone.utc
GOLD_ROOT = Path(__file__).resolve().parents[1]
CORE5_PATH = GOLD_ROOT / "core5_monthly.csv.gz.b64"

PIPELINE_VERSION = "GOLD_CONTROL_BROAD_RESEARCH_NEON_INGEST_R1_2026-09-05"
AUTH_TOKEN = "MANIFEST_V1_37_BROAD_RESEARCH_DATA_SPINE_R1"
REQUIRED_MANIFEST_VERSION = "1.37"
CANONICAL_BRANCH = "gold-r4-direction-engine"

PREFLIGHT_RUN_ID = 33989608218
PREFLIGHT_HEAD_SHA = "a0a06bbce8249f8e7ac4cc0f482f1f68c711657b"
PREFLIGHT_ARTIFACT_DIGEST = "sha256:ba4300d3501211ce7deaeea61627042f066ec45e679f672deb1741e26e102f1a"

STAK_REPO = "lbruton/StakTrakr"
STAK_COMMIT = "ed2e549f82ba0d1cd3ca32842b82d3888d301e01"
STAK_END_DATE = date(2026, 7, 31)
STAK_METAL_SERIES = {
    "Gold": "XAU_STAKTRAKR_RESEARCH_DAILY_R1",
    "Silver": "XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "Platinum": "XPT_STAKTRAKR_RESEARCH_DAILY_R1",
    "Palladium": "XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}

CORE5_SERIES = {
    "gold_monthly": ("CORE5_GOLD_USD_OZ_RESEARCH_R1", "GOLD_USD_OZ", "USD/oz"),
    "fedfunds": ("CORE5_FEDFUNDS_RESEARCH_R1", "FEDFUNDS", "percent"),
    "nasdaq": ("CORE5_NASDAQ_AVG_RESEARCH_R1", "NASDAQ_AVG", "index"),
    "usdcny": ("CORE5_USDCNY_AVG_RESEARCH_R1", "USDCNY_AVG", "CNY per USD"),
    "gpr": ("CORE5_GPR_ROUNDED_RESEARCH_R1", "GPR_CORE_ROUNDED", "index"),
}

TWELVE_SERIES = "XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1"
TWELVE_URL = "https://api.twelvedata.com/time_series"
TWELVE_START = "2022-03"
TWELVE_END = "2026-08"
TWELVE_MIN_DAYS = 15

GPR_COMPANIONS = {
    "GPRT": "GPRT_OFFICIAL_GIT_PIT",
    "GPRA": "GPRA_OFFICIAL_GIT_PIT",
}

DECISION_TABLES = (
    "monthly_forecast_contracts",
    "decision_signal_snapshots",
    "decision_runs",
    "decision_events",
)
ALLOWED_WRITE_TABLES = {
    "source_registry", "retrieval_runs", "observations", "source_vintages", "quality_events",
}


def utcnow() -> datetime:
    return datetime.now(UTC)


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    return value


def require_production_authority() -> None:
    if os.environ.get("BROAD_RESEARCH_PRODUCTION_WRITE_AUTHORIZED", "").strip() != AUTH_TOKEN:
        raise RuntimeError("BROAD_RESEARCH_PRODUCTION_WRITE_NOT_AUTHORIZED")
    if os.environ.get("GITHUB_REF_NAME", "").strip() != CANONICAL_BRANCH:
        raise RuntimeError("BROAD_RESEARCH_WRITE_REQUIRES_CANONICAL_BRANCH")
    if os.environ.get("GOLD_CONTROL_MANIFEST_VERSION", "").strip() != REQUIRED_MANIFEST_VERSION:
        raise RuntimeError("BROAD_RESEARCH_WRITE_REQUIRES_MANIFEST_1_37")
    if os.environ.get("BROAD_RESEARCH_PREFLIGHT_HEAD_SHA", "").strip() != PREFLIGHT_HEAD_SHA:
        raise RuntimeError("BROAD_RESEARCH_PREFLIGHT_HEAD_SHA_MISMATCH")
    if os.environ.get("BROAD_RESEARCH_PREFLIGHT_ARTIFACT_DIGEST", "").strip() != PREFLIGHT_ARTIFACT_DIGEST:
        raise RuntimeError("BROAD_RESEARCH_PREFLIGHT_ARTIFACT_DIGEST_MISMATCH")


def month_range(start: str, end: str) -> list[str]:
    return [str(x) for x in pd.period_range(start, end, freq="M")]


def previous_month(month: str) -> str:
    return str(pd.Period(month, freq="M") - 1)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def base_bundle(retrieved_at: datetime) -> dict[str, Any]:
    return {
        "run_id": str(uuid.uuid4()),
        "started_at": retrieved_at.isoformat(),
        "finished_at": retrieved_at.isoformat(),
        "pipeline_version": PIPELINE_VERSION,
        "mode": "historical_research_source_ingestion",
        "observations": [],
        "vintages": [],
        "quality_events": [],
        "metadata": {
            "evidence_scope": "RESEARCH_DATA_ONLY",
            "preflight_run_id": PREFLIGHT_RUN_ID,
            "preflight_head_sha": PREFLIGHT_HEAD_SHA,
            "preflight_artifact_digest": PREFLIGHT_ARTIFACT_DIGEST,
            "database_write": False,
            "model_scores": False,
            "forecast_write": False,
            "decision_write": False,
            "auto_selector": "OFF",
            "auto_ensemble": "OFF",
        },
    }


def append_observation(bundle: dict[str, Any], **row: Any) -> None:
    bundle["observations"].append(row)


def build_core5(bundle: dict[str, Any], retrieved_at: datetime) -> dict[str, Any]:
    encoded = CORE5_PATH.read_bytes().strip()
    compressed = base64.b64decode(encoded, validate=True)
    raw = gzip.decompress(compressed)
    df = pd.read_csv(io.BytesIO(raw))
    required_cols = ["date", *CORE5_SERIES.keys()]
    if list(df.columns) != required_cols:
        raise RuntimeError(f"CORE5_SCHEMA_MISMATCH:{list(df.columns)}")
    dates = pd.to_datetime(df["date"], errors="raise", utc=True)
    if len(df) != 390 or dates.iloc[0].date().isoformat() != "1994-02-01" or dates.iloc[-1].date().isoformat() != "2026-07-01":
        raise RuntimeError("CORE5_RANGE_OR_ROWCOUNT_MISMATCH")
    if dates.duplicated().any():
        raise RuntimeError("CORE5_DUPLICATE_DATES")
    for col in CORE5_SERIES:
        if pd.to_numeric(df[col], errors="coerce").isna().any():
            raise RuntimeError(f"CORE5_NULL_OR_NONNUMERIC:{col}")

    payload_hash = sha256(raw)
    lineage = f"CORE5_MONTHLY_LOCKED_RESEARCH_R1_{payload_hash[:12]}"
    for i, dt in enumerate(dates):
        for col, (series_id, source_symbol, unit) in CORE5_SERIES.items():
            append_observation(
                bundle,
                run_id=bundle["run_id"],
                series_id=series_id,
                observation_ts=dt.isoformat(),
                value=float(df.iloc[i][col]),
                source="Gold Control locked local CORE5 research snapshot",
                source_symbol=source_symbol,
                provider_as_of=None,
                available_as_of=retrieved_at.isoformat(),
                first_seen_at=retrieved_at.isoformat(),
                retrieved_at=retrieved_at.isoformat(),
                frequency="monthly",
                unit=unit,
                transform="LEVEL",
                quality_status="APPROVED_LOCKED_RESEARCH_SNAPSHOT_NOT_PIT",
                lineage_id=lineage,
                payload_hash=payload_hash,
                metadata={
                    "evidence_class": "LOCKED_LOCAL_RESEARCH_SNAPSHOT_NOT_HISTORICAL_PIT",
                    "historical_pit_claim": False,
                    "retrieval_time_not_backdated": True,
                    "locked_source_reference": "GOLD_H1_R1_CANONICAL_DATASET_V1.xlsx/Source_Lineage/CORE5_MONTHLY",
                    "preflight_head_sha": PREFLIGHT_HEAD_SHA,
                },
            )
    bundle["vintages"].append({
        "source_id": "CORE5_MONTHLY_LOCKED_RESEARCH_R1",
        "retrieved_at": retrieved_at.isoformat(),
        "provider_as_of": None,
        "content_sha256": payload_hash,
        "content_type": "text/csv",
        "byte_count": len(raw),
        "metadata": {
            "evidence_class": "LOCKED_LOCAL_RESEARCH_SNAPSHOT_NOT_HISTORICAL_PIT",
            "rows": 390,
            "first_month": "1994-02",
            "last_month": "2026-07",
            "historical_pit_claim": False,
        },
    })
    return {"rows": 390 * len(CORE5_SERIES), "months": 390, "payload_sha256": payload_hash}


def request_json(session: requests.Session, url: str, *, params: dict[str, Any] | None = None, timeout: int = 90) -> tuple[Any, bytes, str | None]:
    response = session.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json(), response.content, response.headers.get("content-type")


def build_staktrakr(bundle: dict[str, Any], retrieved_at: datetime, session: requests.Session) -> dict[str, Any]:
    counts = {series_id: 0 for series_id in STAK_METAL_SERIES.values()}
    seen: dict[tuple[str, str], float] = {}
    annual_hashes: dict[int, str] = {}
    for year in range(2010, 2027):
        url = f"https://raw.githubusercontent.com/{STAK_REPO}/{STAK_COMMIT}/data/spot-history-{year}.json"
        payload, raw, content_type = request_json(session, url)
        if not isinstance(payload, list):
            raise RuntimeError(f"STAKTRAKR_SCHEMA_NOT_LIST:{year}")
        payload_hash = sha256(raw)
        annual_hashes[year] = payload_hash
        bundle["vintages"].append({
            "source_id": f"STAKTRAKR_SPOT_HISTORY_{year}_{STAK_COMMIT[:12]}",
            "retrieved_at": retrieved_at.isoformat(),
            "provider_as_of": None,
            "content_sha256": payload_hash,
            "content_type": content_type or "application/json",
            "byte_count": len(raw),
            "metadata": {
                "upstream_repo": STAK_REPO,
                "pinned_commit": STAK_COMMIT,
                "year": year,
                "evidence_class": "HISTORICAL_RECONSTRUCTION_NO_ORIGIN_PIT_CLAIM",
            },
        })
        for row in payload:
            if not isinstance(row, dict):
                continue
            metal = str(row.get("metal") or "")
            if metal not in STAK_METAL_SERIES:
                continue
            ts = pd.to_datetime(row.get("timestamp"), errors="coerce", utc=True)
            if pd.isna(ts) or ts.date() > STAK_END_DATE:
                continue
            try:
                value = float(row.get("spot"))
            except (TypeError, ValueError):
                continue
            series_id = STAK_METAL_SERIES[metal]
            day = ts.date().isoformat()
            key = (series_id, day)
            if key in seen:
                if seen[key] != value:
                    raise RuntimeError(f"STAKTRAKR_CONFLICTING_DUPLICATE:{series_id}:{day}")
                continue
            seen[key] = value
            obs_ts = pd.Timestamp(day, tz="UTC").isoformat()
            provider_label = str(row.get("provider") or "").strip() or None
            lineage = f"STAKTRAKR_{year}_{STAK_COMMIT[:12]}_{payload_hash[:12]}"
            append_observation(
                bundle,
                run_id=bundle["run_id"],
                series_id=series_id,
                observation_ts=obs_ts,
                value=value,
                source=f"{STAK_REPO}@{STAK_COMMIT}",
                source_symbol=metal,
                provider_as_of=None,
                available_as_of=retrieved_at.isoformat(),
                first_seen_at=retrieved_at.isoformat(),
                retrieved_at=retrieved_at.isoformat(),
                frequency="daily",
                unit=None,
                transform="LEVEL",
                quality_status="APPROVED_HISTORICAL_RESEARCH_RECONSTRUCTION_NOT_PIT",
                lineage_id=lineage,
                payload_hash=payload_hash,
                metadata={
                    "metal": metal,
                    "original_timestamp": str(row.get("timestamp")),
                    "payload_provider_label": provider_label,
                    "payload_source_label": str(row.get("source") or "") or None,
                    "pinned_commit": STAK_COMMIT,
                    "historical_pit_claim": False,
                    "retrieval_time_not_backdated": True,
                    "unit_not_encoded_in_source_payload": True,
                    "evidence_class": "HISTORICAL_RECONSTRUCTION_NO_ORIGIN_PIT_CLAIM",
                },
            )
            counts[series_id] += 1
    if any(v <= 0 for v in counts.values()):
        raise RuntimeError(f"STAKTRAKR_EMPTY_SERIES:{counts}")
    return {"series_rows": counts, "annual_files": 17, "annual_payload_hashes": annual_hashes}


def month_bounds(month: str) -> tuple[str, str]:
    p = pd.Period(month, freq="M")
    return p.start_time.strftime("%Y-%m-%d 00:00:00"), p.end_time.strftime("%Y-%m-%d 23:59:59")


def fetch_twelve_month(session: requests.Session, api_key: str, month: str) -> tuple[dict[str, Any], bytes, str | None]:
    start, end = month_bounds(month)
    params = {
        "symbol": "XAU/USD",
        "interval": "1h",
        "start_date": start,
        "end_date": end,
        "timezone": "America/New_York",
        "outputsize": 1000,
        "format": "JSON",
        "apikey": api_key,
    }
    for attempt in range(1, 4):
        try:
            payload, raw, content_type = request_json(session, TWELVE_URL, params=params)
            if not isinstance(payload, dict):
                raise RuntimeError(f"TWELVE_SCHEMA_NOT_OBJECT:{month}")
            if payload.get("status") == "error":
                code = str(payload.get("code") or "")
                message = str(payload.get("message") or "TWELVE_ERROR")
                if attempt < 3 and (code in {"429", "4290"} or "credit" in message.lower() or "rate" in message.lower()):
                    time.sleep(61)
                    continue
                raise RuntimeError(f"TWELVE_PROVIDER_ERROR:{month}:code={code}:{message[:120]}")
            meta = payload.get("meta") or {}
            if meta.get("symbol") not in (None, "", "XAU/USD"):
                raise RuntimeError(f"TWELVE_SYMBOL_MISMATCH:{month}")
            if meta.get("interval") not in (None, "", "1h"):
                raise RuntimeError(f"TWELVE_INTERVAL_MISMATCH:{month}")
            if not isinstance(payload.get("values"), list):
                raise RuntimeError(f"TWELVE_VALUES_NOT_LIST:{month}")
            return payload, raw, content_type
        except requests.RequestException as exc:
            if attempt == 3:
                raise RuntimeError(f"TWELVE_REQUEST_FAILED:{month}:{type(exc).__name__}") from exc
            status = getattr(getattr(exc, "response", None), "status_code", None)
            time.sleep(61 if status == 429 else 5 * attempt)
    raise RuntimeError(f"TWELVE_REQUEST_FAILED:{month}")


def build_twelve(bundle: dict[str, Any], retrieved_at: datetime, session: requests.Session, api_key: str, pacing: float) -> dict[str, Any]:
    months = month_range(TWELVE_START, TWELVE_END)
    total_selected = 0
    month_counts: dict[str, int] = {}
    for idx, month in enumerate(months):
        payload, raw, content_type = fetch_twelve_month(session, api_key, month)
        payload_hash = sha256(raw)
        lineage = f"TWELVE_XAU_1H_RESEARCH_{month.replace('-', '')}_{payload_hash[:12]}"
        selected: dict[str, tuple[pd.Timestamp, float]] = {}
        for row in payload["values"]:
            if not isinstance(row, dict):
                continue
            dt = pd.to_datetime(row.get("datetime"), errors="coerce")
            if pd.isna(dt) or dt.strftime("%H:%M:%S") != "16:00:00":
                continue
            try:
                value = float(row.get("close"))
            except (TypeError, ValueError):
                continue
            local_dt = pd.Timestamp(dt).tz_localize("America/New_York")
            day = local_dt.date().isoformat()
            if day in selected and selected[day][1] != value:
                raise RuntimeError(f"TWELVE_CONFLICTING_16ET_DUPLICATE:{day}")
            selected[day] = (local_dt, value)
        if len(selected) < TWELVE_MIN_DAYS:
            raise RuntimeError(f"TWELVE_MONTH_COVERAGE_FAIL:{month}:{len(selected)}/{TWELVE_MIN_DAYS}")
        month_counts[month] = len(selected)
        total_selected += len(selected)
        for _, (local_dt, value) in sorted(selected.items()):
            append_observation(
                bundle,
                run_id=bundle["run_id"],
                series_id=TWELVE_SERIES,
                observation_ts=local_dt.tz_convert("UTC").isoformat(),
                value=value,
                source="Twelve Data",
                source_symbol="XAU/USD",
                provider_as_of=None,
                available_as_of=retrieved_at.isoformat(),
                first_seen_at=retrieved_at.isoformat(),
                retrieved_at=retrieved_at.isoformat(),
                frequency="daily_derived_from_1h",
                unit="USD/oz",
                transform="SELECT_16_00_AMERICA_NEW_YORK_HOURLY_CLOSE",
                quality_status="APPROVED_HISTORICAL_RESEARCH_RETRIEVAL_NOT_CANONICAL_NY17",
                lineage_id=lineage,
                payload_hash=payload_hash,
                metadata={
                    "provider_interval": "1h",
                    "provider_timezone": "America/New_York",
                    "selected_bar_open_time": "16:00:00",
                    "interpreted_bar_end_time": "17:00:00",
                    "historical_pit_claim": False,
                    "retrieval_time_not_backdated": True,
                    "not_equivalent_to": "XAU_EOD_TWELVE_NY17",
                    "evidence_class": "HISTORICAL_RESEARCH_RETRIEVAL_NOT_CANONICAL_NY17",
                },
            )
        bundle["vintages"].append({
            "source_id": f"TWELVE_XAU_HOURLY_RESEARCH_{month.replace('-', '')}",
            "retrieved_at": retrieved_at.isoformat(),
            "provider_as_of": None,
            "content_sha256": payload_hash,
            "content_type": content_type or "application/json",
            "byte_count": len(raw),
            "metadata": {
                "month": month,
                "symbol": "XAU/USD",
                "interval": "1h",
                "timezone": "America/New_York",
                "selected_days": len(selected),
                "evidence_class": "HISTORICAL_RESEARCH_RETRIEVAL_NOT_CANONICAL_NY17",
                "not_equivalent_to": "XAU_EOD_TWELVE_NY17",
            },
        })
        if idx < len(months) - 1 and pacing > 0:
            time.sleep(pacing)
    if len(month_counts) != 54:
        raise RuntimeError(f"TWELVE_REQUIRED_MONTHS_MISMATCH:{len(month_counts)}/54")
    return {"months": len(month_counts), "selected_daily_rows": total_selected, "min_days_per_month": min(month_counts.values())}


def git_text(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True, timeout=90)
    return proc.stdout.strip()


def git_bytes(repo: Path, sha: str, relpath: str) -> bytes:
    proc = subprocess.run(["git", "show", f"{sha}:{relpath}"], cwd=repo, check=True, capture_output=True, timeout=90)
    return proc.stdout


def earliest_add(repo: Path, relpath: str) -> tuple[str, datetime] | None:
    out = git_text(repo, "log", "--all", "--diff-filter=A", "--format=%H|%cI", "--", relpath)
    rows: list[tuple[str, datetime]] = []
    for line in out.splitlines():
        if "|" not in line:
            continue
        sha, stamp = line.split("|", 1)
        rows.append((sha, datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(UTC)))
    return sorted(rows, key=lambda x: x[1])[0] if rows else None


def workbook_series(raw: bytes, series: str) -> pd.DataFrame:
    sheets = pd.read_excel(io.BytesIO(raw), sheet_name=None, engine="xlrd")
    candidates: list[pd.DataFrame] = []
    for df in sheets.values():
        cols = {str(c).strip().upper(): c for c in df.columns}
        if series.upper() not in cols:
            continue
        date_col = cols.get("MONTH") or cols.get("DATE") or df.columns[0]
        q = df[[date_col, cols[series.upper()]]].copy()
        q.columns = ["date", "value"]
        q["date"] = pd.to_datetime(q["date"], errors="coerce")
        q["value"] = pd.to_numeric(q["value"], errors="coerce")
        q = q.dropna(subset=["date", "value"]).sort_values("date").drop_duplicates("date", keep="last")
        if not q.empty:
            candidates.append(q)
    if not candidates:
        raise RuntimeError(f"GPR_COMPANION_SCHEMA_NOT_FOUND:{series}")
    return max(candidates, key=len)


def load_gpr_coverage(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise RuntimeError("GPR_COVERAGE_ROWS_MISSING")
    wanted = month_range(TWELVE_START, TWELVE_END)
    by_origin = {str(r.get("origin_month")): r for r in rows}
    if set(wanted) - set(by_origin):
        raise RuntimeError("GPR_COVERAGE_ORIGINS_MISSING")
    if any(not bool(by_origin[m].get("repo_git_pit_proven")) for m in wanted):
        raise RuntimeError("GPR_BASE_PIT_NOT_PROVEN_FOR_ALL_ORIGINS")
    return {m: by_origin[m] for m in wanted}


def build_gpr_companions(bundle: dict[str, Any], retrieved_at: datetime, repo: Path, coverage_path: Path) -> dict[str, Any]:
    if not (repo / ".git").exists():
        raise RuntimeError("GPR_UPSTREAM_REPO_NOT_GIT_CLONE")
    coverage = load_gpr_coverage(coverage_path)
    origins_by_series = {series_id: 0 for series_id in GPR_COMPANIONS.values()}
    rows_by_series = {series_id: 0 for series_id in GPR_COMPANIONS.values()}
    vintage_count = 0
    for origin in month_range(TWELVE_START, TWELVE_END):
        compact = origin.replace("-", "")
        relpath = f"gpr_archive_files/data_gpr_export_{compact}.xls"
        add = earliest_add(repo, relpath)
        if add is None:
            raise RuntimeError(f"GPR_COMPANION_ADD_COMMIT_MISSING:{origin}")
        commit_sha, commit_at = add
        cutoff = pd.Timestamp(coverage[origin]["origin_cutoff_utc"]).to_pydatetime().astimezone(UTC)
        if commit_at > cutoff:
            raise RuntimeError(f"GPR_COMPANION_COMMIT_AFTER_ORIGIN:{origin}")
        raw = git_bytes(repo, commit_sha, relpath)
        payload_hash = sha256(raw)
        required_month = previous_month(origin)
        bundle["vintages"].append({
            "source_id": f"GPR_COMPANION_GIT_PIT_VINTAGE_{compact}",
            "retrieved_at": retrieved_at.isoformat(),
            "provider_as_of": commit_at.isoformat(),
            "content_sha256": payload_hash,
            "content_type": "application/vnd.ms-excel",
            "byte_count": len(raw),
            "metadata": {
                "origin_month": origin,
                "required_observation_month": required_month,
                "archive_path": relpath,
                "archive_commit_sha": commit_sha,
                "archive_commit_at": commit_at.isoformat(),
                "availability_policy": "EARLIEST_OFFICIAL_GIT_ARCHIVE_ADD_COMMIT_FLOOR",
                "series": list(GPR_COMPANIONS.values()),
            },
        })
        vintage_count += 1
        for column, series_id in GPR_COMPANIONS.items():
            df = workbook_series(raw, column)
            usable = df[df["date"].dt.to_period("M") <= pd.Period(required_month, freq="M")].copy()
            required = usable[usable["date"].dt.to_period("M") == pd.Period(required_month, freq="M")]
            if required.empty:
                raise RuntimeError(f"GPR_COMPANION_REQUIRED_P_MINUS_1_MISSING:{column}:{origin}:{required_month}")
            lineage = f"{series_id}_{compact}_{payload_hash[:12]}"
            for _, row in usable.iterrows():
                obs_month = pd.Timestamp(row["date"]).to_period("M").to_timestamp().tz_localize("UTC")
                append_observation(
                    bundle,
                    run_id=bundle["run_id"],
                    series_id=series_id,
                    observation_ts=obs_month.isoformat(),
                    value=float(row["value"]),
                    source="Caldara-Iacoviello official GitHub archive",
                    source_symbol=column,
                    provider_as_of=commit_at.isoformat(),
                    available_as_of=commit_at.isoformat(),
                    first_seen_at=retrieved_at.isoformat(),
                    retrieved_at=retrieved_at.isoformat(),
                    frequency="monthly_vintage",
                    unit="index",
                    transform="LEVEL_FROM_ORIGIN_VINTAGE",
                    quality_status="APPROVED_HISTORICAL_PIT_RECONSTRUCTION_RESEARCH",
                    lineage_id=lineage,
                    payload_hash=payload_hash,
                    metadata={
                        "origin_month": origin,
                        "required_observation_month": required_month,
                        "archive_path": relpath,
                        "archive_commit_sha": commit_sha,
                        "archive_commit_at": commit_at.isoformat(),
                        "availability_policy": "EARLIEST_OFFICIAL_GIT_ARCHIVE_ADD_COMMIT_FLOOR",
                        "historical_reconstruction_not_original_retrieval": True,
                        "retrieval_time_not_backdated": True,
                        "vintage_specific_lineage": True,
                        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                    },
                )
                rows_by_series[series_id] += 1
            origins_by_series[series_id] += 1
    if vintage_count != 54 or any(v != 54 for v in origins_by_series.values()):
        raise RuntimeError(f"GPR_COMPANION_COVERAGE_INCOMPLETE:{vintage_count}:{origins_by_series}")
    return {"vintages": vintage_count, "origins_by_series": origins_by_series, "rows_by_series": rows_by_series}


def registry_specs() -> dict[str, dict[str, Any]]:
    specs: dict[str, dict[str, Any]] = {}
    for _, (sid, symbol, unit) in CORE5_SERIES.items():
        specs[sid] = {
            "semantic_id": sid,
            "source_name": "Gold Control locked local CORE5 research snapshot",
            "source_symbol": symbol,
            "source_tier": "RESEARCH_TIER_A",
            "frequency": "monthly",
            "unit": unit,
            "model_role": "RESEARCH_INPUT_ONLY",
            "status": "APPROVED_RESEARCH_ONLY_NOT_PIT",
            "license_note": "Locked local research snapshot; no historical PIT claim.",
            "metadata": {"evidence_class": "LOCKED_LOCAL_RESEARCH_SNAPSHOT_NOT_HISTORICAL_PIT"},
        }
    for metal, sid in STAK_METAL_SERIES.items():
        specs[sid] = {
            "semantic_id": sid,
            "source_name": f"{STAK_REPO}@{STAK_COMMIT}",
            "source_symbol": metal,
            "source_tier": "RESEARCH_TIER_A",
            "frequency": "daily",
            "unit": None,
            "model_role": "RESEARCH_INPUT_ONLY",
            "status": "APPROVED_RESEARCH_ONLY_NOT_PIT",
            "license_note": "Pinned open-source research payload; unit not encoded in source payload.",
            "metadata": {"evidence_class": "HISTORICAL_RECONSTRUCTION_NO_ORIGIN_PIT_CLAIM", "pinned_commit": STAK_COMMIT},
        }
    specs[TWELVE_SERIES] = {
        "semantic_id": TWELVE_SERIES,
        "source_name": "Twelve Data",
        "source_symbol": "XAU/USD",
        "source_tier": "RESEARCH_TIER_A",
        "frequency": "daily_derived_from_1h",
        "unit": "USD/oz",
        "model_role": "RESEARCH_INPUT_ONLY",
        "status": "APPROVED_RESEARCH_ONLY_NOT_CANONICAL_NY17",
        "license_note": "Historical vendor retrieval for internal research; raw values are not emitted to CI evidence.",
        "metadata": {
            "evidence_class": "HISTORICAL_RESEARCH_RETRIEVAL_NOT_CANONICAL_NY17",
            "interval": "1h",
            "timezone": "America/New_York",
            "selected_bar_time": "16:00:00",
            "not_equivalent_to": "XAU_EOD_TWELVE_NY17",
        },
    }
    for column, sid in GPR_COMPANIONS.items():
        specs[sid] = {
            "semantic_id": sid,
            "source_name": "Caldara-Iacoviello official GitHub archive",
            "source_symbol": column,
            "source_tier": "RESEARCH_TIER_A",
            "frequency": "monthly_vintage",
            "unit": "index",
            "model_role": "RESEARCH_INPUT_ONLY",
            "status": "APPROVED_HISTORICAL_PIT_RECONSTRUCTION_RESEARCH",
            "license_note": "Official Git archive vintage reconstruction; archive-add commit floor is availability evidence.",
            "metadata": {"evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION"},
        }
    return specs


def decision_counts(conn: psycopg.Connection) -> dict[str, int]:
    out: dict[str, int] = {}
    with conn.cursor(row_factory=dict_row) as cur:
        for table in DECISION_TABLES:
            cur.execute(f"select count(*)::bigint as n from {table}")
            out[table] = int(cur.fetchone()["n"])
    return out


def current_runtime_counts(conn: psycopg.Connection) -> dict[str, int]:
    query = """
    with current_ids(engine_id) as (
      values
      ('MONTHLY_DIRECTION_3M'),('FAST'),('SLOW'),('GVZ_RISK'),
      ('BOCPD_RETURN_SUCCESSOR_V1'),('MACRO_EVENT_SUCCESSOR_V2'),
      ('CAUSAL_PATCH'),('MOMENTUM_3M'),('RANDOM_WALK'),
      ('EMERGENCY_LEVEL'),('EMERGENCY_REVERSAL'),('VW_MIDAS_MSVR')
    )
    select l.runtime_status, count(*)::bigint as n
    from current_ids c
    join lateral (
      select runtime_status
      from latest_engine_runtime_state x
      where x.engine_id=c.engine_id
      order by x.as_of desc
      limit 1
    ) l on true
    group by l.runtime_status
    order by l.runtime_status
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        return {str(r["runtime_status"]): int(r["n"]) for r in cur.fetchall()}


def verify_neon_read_only() -> dict[str, Any]:
    with psycopg.connect(db_url()) as conn:
        decisions = decision_counts(conn)
        runtime = current_runtime_counts(conn)
    return {"decision_counts": decisions, "runtime_counts": runtime}


def _existing_registry(cur, series_id: str) -> dict[str, Any] | None:
    cur.execute(
        """select series_id, semantic_id, source_name, source_symbol, source_tier, frequency,
                  unit, model_role, status, license_note, metadata
           from source_registry where series_id=%s""",
        (series_id,),
    )
    row = cur.fetchone()
    return dict(row) if row else None


def seed_registry_append_safe(cur, specs: dict[str, dict[str, Any]]) -> int:
    inserted = 0
    for sid, spec in specs.items():
        existing = _existing_registry(cur, sid)
        if existing is not None:
            identity_fields = ("semantic_id", "source_name", "source_symbol", "frequency")
            mismatches = [f for f in identity_fields if existing.get(f) != spec.get(f)]
            if mismatches:
                raise RuntimeError(f"SOURCE_REGISTRY_IDENTITY_CONFLICT:{sid}:{mismatches}")
            continue
        cur.execute(
            """insert into source_registry
               (series_id, semantic_id, source_name, source_symbol, source_tier, frequency,
                unit, model_role, status, license_note, metadata)
               values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
            (
                sid, spec["semantic_id"], spec["source_name"], spec.get("source_symbol"),
                spec["source_tier"], spec["frequency"], spec.get("unit"), spec.get("model_role"),
                spec["status"], spec.get("license_note"), json.dumps(spec.get("metadata") or {}),
            ),
        )
        inserted += 1
    return inserted


def latest_map(conn: psycopg.Connection, series_ids: list[str]) -> dict[tuple[str, str, str], dict[str, Any]]:
    if not series_ids:
        return {}
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """select series_id, observation_ts, lineage_id, value, quality_status, first_seen_at
               from canonical_latest where series_id=any(%s)""",
            (series_ids,),
        )
        out = {}
        for row in cur.fetchall():
            key = (row["series_id"], row["observation_ts"].isoformat(), row["lineage_id"])
            out[key] = dict(row)
        return out


def persist_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    if bundle.get("quality_events"):
        raise RuntimeError("BROAD_RESEARCH_BUNDLE_HAS_QUALITY_EVENTS")
    observations = list(bundle["observations"])
    series_ids = sorted({str(o["series_id"]) for o in observations})
    specs = registry_specs()
    if set(series_ids) != set(specs):
        raise RuntimeError(f"BROAD_RESEARCH_SERIES_SET_MISMATCH:{sorted(set(series_ids)^set(specs))}")

    with psycopg.connect(db_url(), autocommit=False, row_factory=dict_row) as conn:
        before_decisions = decision_counts(conn)
        before_runtime = current_runtime_counts(conn)
        if any(before_decisions.values()):
            raise RuntimeError(f"DECISION_AUTHORITY_STORE_NOT_EMPTY_BEFORE_SOURCE_INGEST:{before_decisions}")
        if before_runtime != {"ACTIVE": 6, "BLOCKED": 1, "WAITING": 5}:
            raise RuntimeError(f"RUNTIME_INVARIANT_MISMATCH_BEFORE_SOURCE_INGEST:{before_runtime}")

        with conn.cursor(row_factory=dict_row) as cur:
            registry_inserted = seed_registry_append_safe(cur, specs)
            cur.execute(
                """insert into retrieval_runs
                   (run_id, started_at, finished_at, git_sha, pipeline_version, trigger_type,
                    status, observations_read, observations_written, notes, metadata)
                   values (%s,%s,%s,%s,%s,%s,%s,%s,0,%s,%s::jsonb)""",
                (
                    bundle["run_id"], bundle["started_at"], bundle["finished_at"],
                    os.environ.get("GOLD_CODE_SHA") or os.environ.get("GITHUB_SHA"),
                    bundle["pipeline_version"], "MANUAL_GOVERNED_PRODUCTION_SOURCE_INGEST",
                    "SUCCESS", len(observations), None,
                    json.dumps({
                        **bundle["metadata"],
                        "database_write": True,
                        "production_write_authority": AUTH_TOKEN,
                        "allowed_write_tables": sorted(ALLOWED_WRITE_TABLES),
                    }),
                ),
            )

        existing = latest_map(conn, series_ids)
        to_insert: list[dict[str, Any]] = []
        revised = 0
        for raw in observations:
            o = dict(raw)
            key = (o["series_id"], pd.Timestamp(o["observation_ts"]).isoformat(), o["lineage_id"])
            prev = existing.get(key)
            if prev is not None:
                same = float(prev["value"]) == float(o["value"]) and str(prev["quality_status"]) == str(o["quality_status"])
                if same:
                    continue
                revised += 1
                o["first_seen_at"] = prev["first_seen_at"].isoformat()
            to_insert.append(o)

        with conn.cursor() as cur:
            if to_insert:
                cur.executemany(
                    """insert into observations
                       (run_id, series_id, observation_ts, value, source, source_symbol,
                        provider_as_of, available_as_of, first_seen_at, retrieved_at,
                        frequency, unit, transform, quality_status, lineage_id, payload_hash, metadata)
                       values
                       (%(run_id)s, %(series_id)s, %(observation_ts)s, %(value)s, %(source)s, %(source_symbol)s,
                        %(provider_as_of)s, %(available_as_of)s, %(first_seen_at)s, %(retrieved_at)s,
                        %(frequency)s, %(unit)s, %(transform)s, %(quality_status)s, %(lineage_id)s,
                        %(payload_hash)s, %(metadata)s::jsonb)""",
                    [{**o, "metadata": json.dumps(o.get("metadata") or {})} for o in to_insert],
                )
            if bundle["vintages"]:
                cur.executemany(
                    """insert into source_vintages
                       (source_id, retrieved_at, provider_as_of, content_sha256, content_type, byte_count, metadata)
                       values (%s,%s,%s,%s,%s,%s,%s::jsonb)
                       on conflict (source_id, content_sha256) do nothing""",
                    [
                        (
                            v["source_id"], v["retrieved_at"], v.get("provider_as_of"), v["content_sha256"],
                            v.get("content_type"), v.get("byte_count"), json.dumps(v.get("metadata") or {}),
                        )
                        for v in bundle["vintages"]
                    ],
                )
            cur.execute(
                """update retrieval_runs set observations_written=%s, finished_at=%s, status='SUCCESS'
                   where run_id=%s""",
                (len(to_insert), utcnow().isoformat(), bundle["run_id"]),
            )

        after_decisions = decision_counts(conn)
        after_runtime = current_runtime_counts(conn)
        if after_decisions != before_decisions:
            raise RuntimeError(f"DECISION_AUTHORITY_STORE_CHANGED_DURING_SOURCE_INGEST:{before_decisions}->{after_decisions}")
        if after_runtime != before_runtime:
            raise RuntimeError(f"RUNTIME_STATE_CHANGED_DURING_SOURCE_INGEST:{before_runtime}->{after_runtime}")
        conn.commit()

    return {
        "status": "SUCCESS",
        "run_id": bundle["run_id"],
        "series_count": len(series_ids),
        "observations_read": len(observations),
        "observations_written": len(to_insert),
        "revised_observations": revised,
        "registry_rows_inserted": registry_inserted,
        "decision_counts_before": before_decisions,
        "decision_counts_after": after_decisions,
        "runtime_counts_before": before_runtime,
        "runtime_counts_after": after_runtime,
        "forecast_or_decision_write": False,
        "engine_runtime_write": False,
    }


def build_all(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    retrieved_at = utcnow()
    bundle = base_bundle(retrieved_at)
    session = requests.Session()
    session.headers.update({"User-Agent": "GoldControlBroadResearchIngestR1/1.0"})
    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("TWELVE_DATA_API_KEY_NOT_SET")

    summaries = {
        "core5": build_core5(bundle, retrieved_at),
        "staktrakr": build_staktrakr(bundle, retrieved_at, session),
        "twelve_xau_hourly": build_twelve(bundle, retrieved_at, session, api_key, args.twelve_pacing),
        "gpr_companions": build_gpr_companions(bundle, retrieved_at, args.gpr_upstream_repo, args.gpr_coverage_json),
    }
    bundle["finished_at"] = utcnow().isoformat()
    series_counts: dict[str, int] = defaultdict(int)
    for o in bundle["observations"]:
        series_counts[str(o["series_id"])] += 1
    summary = {
        "pipeline_version": PIPELINE_VERSION,
        "status": "PASS",
        "preflight_evidence": {
            "run_id": PREFLIGHT_RUN_ID,
            "head_sha": PREFLIGHT_HEAD_SHA,
            "artifact_digest": PREFLIGHT_ARTIFACT_DIGEST,
        },
        "sources": summaries,
        "series_count": len(series_counts),
        "series_row_counts": dict(sorted(series_counts.items())),
        "total_observation_rows_built": len(bundle["observations"]),
        "source_vintage_rows_built": len(bundle["vintages"]),
        "quality_events": len(bundle["quality_events"]),
        "database_writes": "NONE",
        "model_scores": "NONE",
        "forecast_writes": "NONE",
        "decision_writes": "NONE",
        "engine_runtime_writes": "NONE",
        "raw_market_values_logged": False,
        "production_write_authority_required": AUTH_TOKEN,
        "production_write_authority_active": False,
    }
    if summary["series_count"] != 12:
        raise RuntimeError(f"BROAD_RESEARCH_EXPECTED_12_SERIES:{summary['series_count']}")
    return bundle, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpr-upstream-repo", type=Path, required=True)
    parser.add_argument("--gpr-coverage-json", type=Path, required=True)
    parser.add_argument("--twelve-pacing", type=float, default=0.0)
    parser.add_argument("--summary-out", type=Path, default=Path("broad_research_ingestion_r1_summary.json"))
    parser.add_argument("--persist", action="store_true")
    parser.add_argument("--verify-neon-invariants", action="store_true")
    args = parser.parse_args()

    if args.persist:
        require_production_authority()

    bundle, summary = build_all(args)

    if args.verify_neon_invariants:
        neon_state = verify_neon_read_only()
        summary["neon_prewrite_invariants"] = neon_state
        if any(neon_state["decision_counts"].values()):
            raise RuntimeError(f"DECISION_AUTHORITY_STORE_NOT_EMPTY:{neon_state['decision_counts']}")
        if neon_state["runtime_counts"] != {"ACTIVE": 6, "BLOCKED": 1, "WAITING": 5}:
            raise RuntimeError(f"RUNTIME_INVARIANT_MISMATCH:{neon_state['runtime_counts']}")

    if args.persist:
        result = persist_bundle(bundle)
        summary["production_persist_result"] = result
        summary["database_writes"] = "SOURCE_DATA_AUDIT_ONLY"
        summary["production_write_authority_active"] = True

    args.summary_out.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
