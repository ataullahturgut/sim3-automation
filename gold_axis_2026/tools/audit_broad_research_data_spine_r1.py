from __future__ import annotations

import argparse
import calendar
import hashlib
import io
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import requests

UTC = timezone.utc
NY = ZoneInfo("America/New_York")
PIPELINE_VERSION = "GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_PREFLIGHT_R1_2026-09-05"
STAK_REPO = "lbruton/StakTrakr"
STAK_COMMIT = "429d8e612d504a964846ff6438dbdb28ace630c3"
STAK_METALS = ("Gold", "Silver", "Platinum", "Palladium")
STAK_START_YEAR = 2010
STAK_END_YEAR = 2026
STAK_END_DATE = date(2026, 7, 31)
TWELVE_URL = "https://api.twelvedata.com/time_series"
TWELVE_START = "2022-03"
TWELVE_END = "2026-08"
TWELVE_MIN_DAYS = 15
GPR_SERIES = ("GPRT", "GPRA")
NEON_INVENTORY_SERIES = (
    "DJIA_FRED",
    "NASDAQ100_FRED",
    "SP500_FRED",
    "DGS10_ALFRED_PIT_ME",
    "DFF_ALFRED_PIT_ME",
    "DEXCHUS_ALFRED_PIT_ME",
    "NASDAQ100_ALFRED_PIT_ME",
    "BARRICK_B_TWELVEDATA",
    "NEM_TWELVEDATA",
    "DZZ_TWELVEDATA",
    "GLL_TWELVEDATA",
    "HL_PB_TWELVEDATA",
    "VIX_CBOE",
    "GVZ_CBOE",
)


def month_range(start: str, end: str) -> list[str]:
    return [str(p) for p in pd.period_range(start, end, freq="M")]


def previous_month(month: str) -> str:
    return str(pd.Period(month, freq="M") - 1)


def utc_now() -> datetime:
    return datetime.now(UTC)


def safe_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def _http_get_json(session: requests.Session, url: str, *, params: dict[str, Any] | None = None, timeout: int = 90) -> tuple[Any, bytes]:
    r = session.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    raw = r.content
    return r.json(), raw


def audit_staktrakr(session: requests.Session) -> dict[str, Any]:
    per_metal: dict[str, list[date]] = defaultdict(list)
    date_metals: dict[date, set[str]] = defaultdict(set)
    annual_files: list[dict[str, Any]] = []
    provider_labels: set[str] = set()

    for year in range(STAK_START_YEAR, STAK_END_YEAR + 1):
        url = f"https://raw.githubusercontent.com/{STAK_REPO}/{STAK_COMMIT}/data/spot-history-{year}.json"
        rows, raw = _http_get_json(session, url)
        if not isinstance(rows, list):
            raise RuntimeError(f"STAKTRAKR_SCHEMA_NOT_LIST:{year}")
        accepted = 0
        for row in rows:
            if not isinstance(row, dict):
                continue
            metal = str(row.get("metal") or "")
            if metal not in STAK_METALS:
                continue
            ts = pd.to_datetime(row.get("timestamp"), errors="coerce", utc=True)
            if pd.isna(ts):
                continue
            d = ts.date()
            if d > STAK_END_DATE:
                continue
            try:
                float(row.get("spot"))
            except (TypeError, ValueError):
                continue
            per_metal[metal].append(d)
            date_metals[d].add(metal)
            provider = str(row.get("provider") or "").strip()
            if provider:
                provider_labels.add(provider)
            accepted += 1
        annual_files.append({
            "year": year,
            "http_ok": True,
            "payload_sha256": hashlib.sha256(raw).hexdigest(),
            "accepted_four_metal_rows": accepted,
        })

    metal_summary: dict[str, Any] = {}
    for metal in STAK_METALS:
        ds = sorted(set(per_metal.get(metal, [])))
        metal_summary[metal] = {
            "unique_days": len(ds),
            "first_date": ds[0].isoformat() if ds else None,
            "last_date": ds[-1].isoformat() if ds else None,
        }

    common = sorted(d for d, metals in date_metals.items() if all(m in metals for m in STAK_METALS))
    all_files_ok = len(annual_files) == (STAK_END_YEAR - STAK_START_YEAR + 1) and all(x["http_ok"] for x in annual_files)
    all_metals_nonempty = all(metal_summary[m]["unique_days"] > 0 for m in STAK_METALS)
    historical_depth_ok = bool(common and common[0] <= date(2010, 12, 31))
    july_2026_ok = bool(common and common[-1] >= date(2026, 7, 30))
    pass_gate = all_files_ok and all_metals_nonempty and historical_depth_ok and july_2026_ok

    return {
        "status": "PASS" if pass_gate else "FAIL",
        "upstream_repo": STAK_REPO,
        "pinned_commit": STAK_COMMIT,
        "evidence_class": "HISTORICAL_RECONSTRUCTION_NO_ORIGIN_PIT_CLAIM",
        "annual_file_count": len(annual_files),
        "annual_files": annual_files,
        "metal_summary": metal_summary,
        "common_four_metal_unique_days": len(common),
        "common_first_date": common[0].isoformat() if common else None,
        "common_last_date": common[-1].isoformat() if common else None,
        "provider_label_count": len(provider_labels),
        "raw_market_values_logged": False,
        "gate_checks": {
            "all_2010_2026_files_retrieved": all_files_ok,
            "all_four_metals_nonempty": all_metals_nonempty,
            "historical_depth_reaches_2010": historical_depth_ok,
            "common_panel_reaches_july_2026": july_2026_ok,
        },
    }


def _month_bounds(month: str) -> tuple[str, str]:
    p = pd.Period(month, freq="M")
    start = p.start_time.strftime("%Y-%m-%d 00:00:00")
    end = p.end_time.strftime("%Y-%m-%d 23:59:59")
    return start, end


def _twelve_request_month(session: requests.Session, api_key: str, month: str) -> dict[str, Any]:
    start, end = _month_bounds(month)
    params = {
        "symbol": "XAU/USD",
        "interval": "1h",
        "start_date": start,
        "end_date": end,
        "timezone": "America/New_York",
        "outputsize": 1000,
        "apikey": api_key,
        "format": "JSON",
    }
    last_error: str | None = None
    for attempt in range(1, 4):
        try:
            payload, _ = _http_get_json(session, TWELVE_URL, params=params, timeout=90)
            if isinstance(payload, dict) and payload.get("status") == "error":
                code = payload.get("code")
                msg = str(payload.get("message") or "TWELVE_ERROR")
                last_error = f"code={code}:{msg[:180]}"
                if str(code) in {"429", "4290"} or "credit" in msg.lower() or "rate" in msg.lower():
                    if attempt < 3:
                        time.sleep(61)
                        continue
                raise RuntimeError(f"TWELVE_PROVIDER_ERROR:{month}:{last_error}")
            if not isinstance(payload, dict):
                raise RuntimeError(f"TWELVE_SCHEMA_NOT_OBJECT:{month}")
            meta = payload.get("meta") or {}
            symbol = str(meta.get("symbol") or "")
            interval = str(meta.get("interval") or "")
            values = payload.get("values")
            if symbol and symbol != "XAU/USD":
                raise RuntimeError(f"TWELVE_SYMBOL_MISMATCH:{month}:{symbol}")
            if interval and interval != "1h":
                raise RuntimeError(f"TWELVE_INTERVAL_MISMATCH:{month}:{interval}")
            if not isinstance(values, list):
                raise RuntimeError(f"TWELVE_VALUES_NOT_LIST:{month}")
            selected_dates: set[str] = set()
            parsed_rows = 0
            for row in values:
                if not isinstance(row, dict):
                    continue
                dt = pd.to_datetime(row.get("datetime"), errors="coerce")
                if pd.isna(dt):
                    continue
                try:
                    float(row.get("close"))
                except (TypeError, ValueError):
                    continue
                parsed_rows += 1
                if dt.strftime("%H:%M:%S") == "16:00:00":
                    selected_dates.add(dt.date().isoformat())
            return {
                "month": month,
                "parsed_hourly_rows": parsed_rows,
                "selected_16ET_unique_days": len(selected_dates),
                "min_required_days": TWELVE_MIN_DAYS,
                "pass": len(selected_dates) >= TWELVE_MIN_DAYS,
                "raw_market_values_logged": False,
            }
        except requests.RequestException as exc:
            last_error = f"{type(exc).__name__}:{getattr(getattr(exc, 'response', None), 'status_code', None)}"
            if attempt < 3:
                time.sleep(61 if getattr(getattr(exc, "response", None), "status_code", None) == 429 else 5 * attempt)
                continue
            raise RuntimeError(f"TWELVE_REQUEST_FAILED:{month}:{last_error}") from exc
    raise RuntimeError(f"TWELVE_REQUEST_FAILED:{month}:{last_error}")


def audit_twelve(session: requests.Session, api_key: str, pacing_seconds: float) -> dict[str, Any]:
    months = month_range(TWELVE_START, TWELVE_END)
    rows: list[dict[str, Any]] = []
    for idx, month in enumerate(months):
        row = _twelve_request_month(session, api_key, month)
        rows.append(row)
        if idx < len(months) - 1 and pacing_seconds > 0:
            time.sleep(pacing_seconds)
    failed = [r["month"] for r in rows if not r["pass"]]
    pass_gate = len(rows) == 54 and not failed
    return {
        "status": "PASS" if pass_gate else "FAIL",
        "series_id": "XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1",
        "provider": "Twelve Data",
        "symbol": "XAU/USD",
        "interval": "1h",
        "timezone": "America/New_York",
        "selected_bar_time": "16:00:00",
        "origin_month_count": len(rows),
        "required_origin_month_count": 54,
        "failed_months": failed,
        "months": rows,
        "evidence_class": "HISTORICAL_RESEARCH_RETRIEVAL_NOT_CANONICAL_NY17",
        "not_equivalent_to": "XAU_EOD_TWELVE_NY17",
        "raw_market_values_logged": False,
    }


def git_text(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True, timeout=90)
    return p.stdout.strip()


def earliest_add_commit(repo: Path, relpath: str) -> tuple[str, datetime] | None:
    out = git_text(repo, "log", "--all", "--diff-filter=A", "--format=%H|%cI", "--", relpath)
    candidates: list[tuple[str, datetime]] = []
    for line in out.splitlines():
        if "|" not in line:
            continue
        sha, stamp = line.split("|", 1)
        dt = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(UTC)
        candidates.append((sha, dt))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[1])
    return candidates[0]


def git_bytes(repo: Path, commit: str, relpath: str) -> bytes:
    p = subprocess.run(["git", "show", f"{commit}:{relpath}"], cwd=repo, check=True, capture_output=True, timeout=90)
    return p.stdout


def _extract_series_from_workbook(raw: bytes, series: str) -> pd.DataFrame:
    sheets = pd.read_excel(io.BytesIO(raw), sheet_name=None, engine="xlrd")
    candidates: list[pd.DataFrame] = []
    for _, df in sheets.items():
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


def audit_gpr_companions(repo: Path, coverage_json: Path) -> dict[str, Any]:
    coverage = json.loads(coverage_json.read_text(encoding="utf-8"))
    rows = coverage.get("rows")
    if not isinstance(rows, list):
        raise RuntimeError("GPR_COVERAGE_ROWS_MISSING")
    wanted = month_range(TWELVE_START, TWELVE_END)
    by_origin = {str(r.get("origin_month")): r for r in rows}
    missing_coverage = [m for m in wanted if m not in by_origin]
    if missing_coverage:
        raise RuntimeError("GPR_COVERAGE_ORIGINS_MISSING:" + ",".join(missing_coverage))

    results: dict[str, list[dict[str, Any]]] = {s: [] for s in GPR_SERIES}
    for origin in wanted:
        c = by_origin[origin]
        if not bool(c.get("repo_git_pit_proven")):
            for s in GPR_SERIES:
                results[s].append({"origin_month": origin, "pass": False, "reason": "BASE_GPR_ORIGIN_NOT_PIT_PROVEN"})
            continue
        compact = origin.replace("-", "")
        relpath = f"gpr_archive_files/data_gpr_export_{compact}.xls"
        add = earliest_add_commit(repo, relpath)
        if add is None:
            for s in GPR_SERIES:
                results[s].append({"origin_month": origin, "pass": False, "reason": "ARCHIVE_ADD_COMMIT_NOT_FOUND"})
            continue
        commit_sha, commit_at = add
        cutoff = pd.Timestamp(c["origin_cutoff_utc"]).to_pydatetime().astimezone(UTC)
        if commit_at > cutoff:
            for s in GPR_SERIES:
                results[s].append({"origin_month": origin, "pass": False, "reason": "ARCHIVE_ADD_AFTER_ORIGIN"})
            continue
        raw = git_bytes(repo, commit_sha, relpath)
        payload_sha = hashlib.sha256(raw).hexdigest()
        req = pd.Period(previous_month(origin), freq="M")
        for s in GPR_SERIES:
            try:
                q = _extract_series_from_workbook(raw, s)
                exact = q[q["date"].dt.to_period("M") == req]
                ok = not exact.empty
                results[s].append({
                    "origin_month": origin,
                    "required_observation_month": str(req),
                    "archive_commit_sha": commit_sha,
                    "archive_commit_at": commit_at.isoformat(),
                    "payload_sha256": payload_sha,
                    "pass": ok,
                    "reason": "OK" if ok else "P_MINUS_1_MISSING",
                })
            except Exception as exc:
                results[s].append({
                    "origin_month": origin,
                    "required_observation_month": str(req),
                    "archive_commit_sha": commit_sha,
                    "archive_commit_at": commit_at.isoformat(),
                    "payload_sha256": payload_sha,
                    "pass": False,
                    "reason": type(exc).__name__,
                })

    summary: dict[str, Any] = {}
    overall = True
    for s in GPR_SERIES:
        good = sum(1 for r in results[s] if r["pass"])
        failed = [r["origin_month"] for r in results[s] if not r["pass"]]
        ok = good == 54 and len(results[s]) == 54
        overall = overall and ok
        summary[s] = {
            "reserved_series_id": f"{s}_OFFICIAL_GIT_PIT",
            "required_origins": 54,
            "passed_origins": good,
            "failed_origins": failed,
            "status": "PASS" if ok else "FAIL",
        }
    return {
        "status": "PASS" if overall else "FAIL",
        "availability_policy": "EARLIEST_OFFICIAL_GIT_ARCHIVE_ADD_COMMIT_FLOOR",
        "base_authority_series": "GPR_OFFICIAL_GIT_PIT",
        "summary": summary,
        "origins": results,
        "raw_values_logged": False,
    }


def audit_neon_inventory(database_url: str) -> dict[str, Any]:
    import psycopg
    from psycopg.rows import dict_row

    found: list[dict[str, Any]] = []
    with psycopg.connect(database_url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            for series_id in NEON_INVENTORY_SERIES:
                cur.execute(
                    """
                    select count(*)::bigint as row_count,
                           min(observation_ts)::text as first_ts,
                           max(observation_ts)::text as last_ts,
                           count(distinct lineage_id)::bigint as lineage_count,
                           count(*) filter (where value is null)::bigint as null_values,
                           count(*) filter (where available_as_of is null)::bigint as missing_available_as_of,
                           count(*) filter (where provider_as_of is null)::bigint as missing_provider_as_of
                    from observations where series_id=%s
                    """,
                    (series_id,),
                )
                row = dict(cur.fetchone())
                row["series_id"] = series_id
                found.append(row)
        conn.rollback()
    return {
        "status": "INVENTORY_ONLY_NONBLOCKING",
        "series_count": len(found),
        "series": found,
        "raw_market_values_logged": False,
        "database_writes": "NONE",
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["sources"]
    lines = [
        "# Broad Research Data Spine R1 — Preflight Evidence",
        "",
        f"- Final gate: **{payload['final_gate']}**",
        f"- Database writes: **{payload['database_writes']}**",
        f"- Model scores: **{payload['model_scores']}**",
        f"- Forecast writes: **{payload['forecast_writes']}**",
        f"- Decision writes: **{payload['decision_writes']}**",
        "",
        "| Gate | Status |",
        "|---|---|",
        f"| StakTrakr four-metal reconstruction | {s['staktrakr']['status']} |",
        f"| Twelve XAU hourly-derived daily research line | {s['twelve_xau_hourly']['status']} |",
        f"| GPRT + GPRA exact-vintage companions | {s['gpr_companions']['status']} |",
        f"| Neon broad-market inventory | {s['neon_inventory']['status']} |",
        "",
        "## StakTrakr",
        "",
        f"- Pinned commit: `{s['staktrakr']['pinned_commit']}`",
        f"- Common four-metal days: **{s['staktrakr']['common_four_metal_unique_days']}**",
        f"- Common date range: **{s['staktrakr']['common_first_date']} .. {s['staktrakr']['common_last_date']}**",
        "- Evidence class: historical reconstruction; no historical-origin PIT claim.",
        "",
        "## Twelve XAU research line",
        "",
        f"- Months checked: **{s['twelve_xau_hourly']['origin_month_count']}/54**",
        f"- Failed months: **{len(s['twelve_xau_hourly']['failed_months'])}**",
        "- Uses XAU/USD 1h America/New_York, 16:00 bar; this is not canonical exact-minute NY17.",
        "",
        "## GPR companions",
        "",
    ]
    for name, x in s["gpr_companions"]["summary"].items():
        lines.append(f"- {name}: **{x['passed_origins']}/{x['required_origins']} — {x['status']}**")
    lines += [
        "",
        "## Neon inventory",
        "",
        f"- Series inventoried: **{s['neon_inventory']['series_count']}**",
        "- Inventory records counts/date ranges/lineage completeness only; no market values are emitted.",
        "",
        "No model was scored and no production database row was written by this preflight.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--gpr-upstream-repo", type=Path, required=True)
    p.add_argument("--gpr-coverage-json", type=Path, required=True)
    p.add_argument("--json-out", type=Path, default=Path("broad_research_data_spine_r1_preflight.json"))
    p.add_argument("--md-out", type=Path, default=Path("broad_research_data_spine_r1_preflight.md"))
    p.add_argument("--twelve-pacing-seconds", type=float, default=8.2)
    args = p.parse_args()

    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    db_url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not api_key:
        raise SystemExit("TWELVE_DATA_API_KEY_MISSING")
    if not db_url:
        raise SystemExit("NEON_DATABASE_URL_MISSING")
    if not (args.gpr_upstream_repo / ".git").exists():
        raise SystemExit("GPR_UPSTREAM_REPO_NOT_GIT_CLONE")

    started = utc_now()
    session = requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-Broad-Research-Data-Spine-R1/1.0"})

    sources: dict[str, Any] = {}
    sources["staktrakr"] = audit_staktrakr(session)
    sources["twelve_xau_hourly"] = audit_twelve(session, api_key, args.twelve_pacing_seconds)
    sources["gpr_companions"] = audit_gpr_companions(args.gpr_upstream_repo, args.gpr_coverage_json)
    sources["neon_inventory"] = audit_neon_inventory(db_url)

    final_ok = all(sources[k]["status"] == "PASS" for k in ("staktrakr", "twelve_xau_hourly", "gpr_companions"))
    payload = {
        "pipeline_version": PIPELINE_VERSION,
        "started_at": started.isoformat(),
        "finished_at": utc_now().isoformat(),
        "final_gate": "PASS" if final_ok else "FAIL",
        "database_writes": "NONE",
        "model_scores": "NONE",
        "forecast_writes": "NONE",
        "decision_writes": "NONE",
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "raw_market_values_logged": False,
        "sources": sources,
    }
    safe_json(args.json_out, payload)
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({
        "pipeline_version": PIPELINE_VERSION,
        "final_gate": payload["final_gate"],
        "staktrakr": sources["staktrakr"]["status"],
        "twelve_xau_hourly": sources["twelve_xau_hourly"]["status"],
        "gpr_companions": sources["gpr_companions"]["status"],
        "neon_inventory": sources["neon_inventory"]["status"],
        "database_writes": "NONE",
        "model_scores": "NONE",
        "raw_market_values_logged": False,
    }, indent=2))
    return 0 if final_ok else 2


if __name__ == "__main__":
    sys.exit(main())
