from __future__ import annotations

import argparse
import base64
import calendar
import gzip
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

import pandas as pd
import requests

UTC = timezone.utc
PIPELINE_VERSION = "GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_PREFLIGHT_R1_2026-09-05"
GOLD_ROOT = Path(__file__).resolve().parents[1]
CORE5_PATH = GOLD_ROOT / "core5_monthly.csv.gz.b64"
CORE5_REQUIRED = ("gold_monthly", "fedfunds", "nasdaq", "usdcny", "gpr")
STAK_REPO = "lbruton/StakTrakr"
STAK_COMMIT = "ed2e549f82ba0d1cd3ca32842b82d3888d301e01"
STAK_METALS = ("Gold", "Silver", "Platinum", "Palladium")
STAK_END_DATE = date(2026, 7, 31)
TWELVE_URL = "https://api.twelvedata.com/time_series"
TWELVE_START = "2022-03"
TWELVE_END = "2026-08"
TWELVE_MIN_DAYS = 15
GPR_SERIES = ("GPRT", "GPRA")
NEON_INVENTORY_SERIES = (
    "DJIA_FRED", "NASDAQ100_FRED", "SP500_FRED", "DGS10_ALFRED_PIT_ME",
    "DFF_ALFRED_PIT_ME", "DEXCHUS_ALFRED_PIT_ME", "NASDAQ100_ALFRED_PIT_ME",
    "BARRICK_B_TWELVEDATA", "NEM_TWELVEDATA", "DZZ_TWELVEDATA",
    "GLL_TWELVEDATA", "HL_PB_TWELVEDATA", "VIX_CBOE", "GVZ_CBOE",
)


def now_utc() -> datetime:
    return datetime.now(UTC)


def month_range(start: str, end: str) -> list[str]:
    return [str(x) for x in pd.period_range(start, end, freq="M")]


def previous_month(month: str) -> str:
    return str(pd.Period(month, freq="M") - 1)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def audit_core5() -> dict[str, Any]:
    if not CORE5_PATH.exists():
        raise RuntimeError("CORE5_LOCKED_ARTIFACT_MISSING")
    encoded = CORE5_PATH.read_bytes().strip()
    compressed = base64.b64decode(encoded, validate=True)
    raw = gzip.decompress(compressed)
    df = pd.read_csv(io.BytesIO(raw))
    if "date" not in df.columns:
        raise RuntimeError("CORE5_DATE_COLUMN_MISSING")
    missing = [c for c in CORE5_REQUIRED if c not in df.columns]
    dates = pd.to_datetime(df["date"], errors="coerce")
    valid_dates = dates.dropna().sort_values()
    row_count = int(len(df))
    first = valid_dates.iloc[0].date().isoformat() if not valid_dates.empty else None
    last = valid_dates.iloc[-1].date().isoformat() if not valid_dates.empty else None
    required_nonnull = {c: int(pd.to_numeric(df[c], errors="coerce").notna().sum()) for c in CORE5_REQUIRED if c in df.columns}
    pass_gate = (
        not missing
        and row_count == 390
        and first == "1994-02-01"
        and last == "2026-07-01"
        and all(required_nonnull.get(c, 0) > 0 for c in CORE5_REQUIRED)
    )
    return {
        "status": "PASS" if pass_gate else "FAIL",
        "source_id": "CORE5_MONTHLY_LOCKED_RESEARCH_R1",
        "source_path": str(CORE5_PATH.relative_to(GOLD_ROOT.parent)),
        "payload_sha256_csv": hashlib.sha256(raw).hexdigest(),
        "required_rows": 390,
        "observed_rows": row_count,
        "first_month": first,
        "last_month": last,
        "required_columns": list(CORE5_REQUIRED),
        "missing_columns": missing,
        "nonnull_counts": required_nonnull,
        "evidence_class": "LOCKED_LOCAL_RESEARCH_SNAPSHOT_NOT_HISTORICAL_PIT",
        "raw_market_values_logged": False,
    }


def get_json(session: requests.Session, url: str, params: dict[str, Any] | None = None, timeout: int = 90) -> tuple[Any, bytes]:
    resp = session.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json(), resp.content


def audit_staktrakr(session: requests.Session) -> dict[str, Any]:
    per_metal: dict[str, set[date]] = {m: set() for m in STAK_METALS}
    date_metals: dict[date, set[str]] = defaultdict(set)
    annual_files: list[dict[str, Any]] = []
    providers: set[str] = set()

    for year in range(2010, 2027):
        url = f"https://raw.githubusercontent.com/{STAK_REPO}/{STAK_COMMIT}/data/spot-history-{year}.json"
        rows, raw = get_json(session, url)
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
            per_metal[metal].add(d)
            date_metals[d].add(metal)
            p = str(row.get("provider") or "").strip()
            if p:
                providers.add(p)
            accepted += 1
        annual_files.append({
            "year": year,
            "payload_sha256": hashlib.sha256(raw).hexdigest(),
            "accepted_four_metal_rows": accepted,
        })

    summary: dict[str, Any] = {}
    for metal in STAK_METALS:
        ds = sorted(per_metal[metal])
        summary[metal] = {
            "unique_days": len(ds),
            "first_date": ds[0].isoformat() if ds else None,
            "last_date": ds[-1].isoformat() if ds else None,
        }
    common = sorted(d for d, ms in date_metals.items() if all(m in ms for m in STAK_METALS))
    ok = (
        len(annual_files) == 17
        and all(summary[m]["unique_days"] > 0 for m in STAK_METALS)
        and bool(common)
        and common[0] <= date(2010, 12, 31)
        and common[-1] >= date(2026, 7, 30)
    )
    return {
        "status": "PASS" if ok else "FAIL",
        "upstream_repo": STAK_REPO,
        "pinned_commit": STAK_COMMIT,
        "pin_authority": "GOLD_H1_R1_CANONICAL_DATASET_V1.xlsx/Source_Lineage/PRECIOUS_METALS_DAILY_PINNED",
        "evidence_class": "HISTORICAL_RECONSTRUCTION_NO_ORIGIN_PIT_CLAIM",
        "annual_file_count": len(annual_files),
        "annual_files": annual_files,
        "metal_summary": summary,
        "common_four_metal_unique_days": len(common),
        "common_first_date": common[0].isoformat() if common else None,
        "common_last_date": common[-1].isoformat() if common else None,
        "provider_label_count": len(providers),
        "raw_market_values_logged": False,
    }


def month_bounds(month: str) -> tuple[str, str]:
    p = pd.Period(month, freq="M")
    return p.start_time.strftime("%Y-%m-%d 00:00:00"), p.end_time.strftime("%Y-%m-%d 23:59:59")


def twelve_month(session: requests.Session, api_key: str, month: str) -> dict[str, Any]:
    start, end = month_bounds(month)
    params = {
        "symbol": "XAU/USD", "interval": "1h", "start_date": start, "end_date": end,
        "timezone": "America/New_York", "outputsize": 1000, "format": "JSON", "apikey": api_key,
    }
    for attempt in range(1, 4):
        try:
            payload, _ = get_json(session, TWELVE_URL, params=params)
            if not isinstance(payload, dict):
                raise RuntimeError(f"TWELVE_SCHEMA_NOT_OBJECT:{month}")
            if payload.get("status") == "error":
                code = payload.get("code")
                msg = str(payload.get("message") or "TWELVE_ERROR")
                if attempt < 3 and (str(code) in {"429", "4290"} or "credit" in msg.lower() or "rate" in msg.lower()):
                    time.sleep(61)
                    continue
                raise RuntimeError(f"TWELVE_PROVIDER_ERROR:{month}:code={code}:{msg[:160]}")
            meta = payload.get("meta") or {}
            if meta.get("symbol") not in (None, "", "XAU/USD"):
                raise RuntimeError(f"TWELVE_SYMBOL_MISMATCH:{month}:{meta.get('symbol')}")
            if meta.get("interval") not in (None, "", "1h"):
                raise RuntimeError(f"TWELVE_INTERVAL_MISMATCH:{month}:{meta.get('interval')}")
            values = payload.get("values")
            if not isinstance(values, list):
                raise RuntimeError(f"TWELVE_VALUES_NOT_LIST:{month}")
            selected: set[str] = set()
            parsed = 0
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
                parsed += 1
                if dt.strftime("%H:%M:%S") == "16:00:00":
                    selected.add(dt.date().isoformat())
            return {
                "month": month,
                "parsed_hourly_rows": parsed,
                "selected_16ET_unique_days": len(selected),
                "min_required_days": TWELVE_MIN_DAYS,
                "pass": len(selected) >= TWELVE_MIN_DAYS,
                "raw_market_values_logged": False,
            }
        except requests.RequestException as exc:
            if attempt == 3:
                raise RuntimeError(f"TWELVE_REQUEST_FAILED:{month}:{type(exc).__name__}") from exc
            status = getattr(getattr(exc, "response", None), "status_code", None)
            time.sleep(61 if status == 429 else 5 * attempt)
    raise RuntimeError(f"TWELVE_REQUEST_FAILED:{month}")


def audit_twelve(session: requests.Session, api_key: str, pacing: float) -> dict[str, Any]:
    months = month_range(TWELVE_START, TWELVE_END)
    rows: list[dict[str, Any]] = []
    for i, month in enumerate(months):
        rows.append(twelve_month(session, api_key, month))
        if i < len(months) - 1 and pacing > 0:
            time.sleep(pacing)
    failed = [r["month"] for r in rows if not r["pass"]]
    ok = len(rows) == 54 and not failed
    return {
        "status": "PASS" if ok else "FAIL",
        "series_id": "XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1",
        "provider": "Twelve Data", "symbol": "XAU/USD", "interval": "1h",
        "timezone": "America/New_York", "selected_bar_time": "16:00:00",
        "origin_month_count": len(rows), "required_origin_month_count": 54,
        "failed_months": failed, "months": rows,
        "evidence_class": "HISTORICAL_RESEARCH_RETRIEVAL_NOT_CANONICAL_NY17",
        "not_equivalent_to": "XAU_EOD_TWELVE_NY17",
        "raw_market_values_logged": False,
    }


def git_text(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True, timeout=90)
    return p.stdout.strip()


def earliest_add(repo: Path, relpath: str) -> tuple[str, datetime] | None:
    out = git_text(repo, "log", "--all", "--diff-filter=A", "--format=%H|%cI", "--", relpath)
    vals: list[tuple[str, datetime]] = []
    for line in out.splitlines():
        if "|" not in line:
            continue
        sha, stamp = line.split("|", 1)
        vals.append((sha, datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(UTC)))
    return sorted(vals, key=lambda x: x[1])[0] if vals else None


def git_bytes(repo: Path, sha: str, relpath: str) -> bytes:
    p = subprocess.run(["git", "show", f"{sha}:{relpath}"], cwd=repo, check=True, capture_output=True, timeout=90)
    return p.stdout


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


def audit_gpr_companions(repo: Path, coverage_json: Path) -> dict[str, Any]:
    c = json.loads(coverage_json.read_text(encoding="utf-8"))
    rows = c.get("rows")
    if not isinstance(rows, list):
        raise RuntimeError("GPR_COVERAGE_ROWS_MISSING")
    wanted = month_range(TWELVE_START, TWELVE_END)
    by_origin = {str(r.get("origin_month")): r for r in rows}
    missing = [m for m in wanted if m not in by_origin]
    if missing:
        raise RuntimeError("GPR_COVERAGE_ORIGINS_MISSING:" + ",".join(missing))

    result: dict[str, list[dict[str, Any]]] = {s: [] for s in GPR_SERIES}
    for origin in wanted:
        base = by_origin[origin]
        compact = origin.replace("-", "")
        rel = f"gpr_archive_files/data_gpr_export_{compact}.xls"
        if not bool(base.get("repo_git_pit_proven")):
            for s in GPR_SERIES:
                result[s].append({"origin_month": origin, "pass": False, "reason": "BASE_GPR_NOT_PIT_PROVEN"})
            continue
        add = earliest_add(repo, rel)
        if add is None:
            for s in GPR_SERIES:
                result[s].append({"origin_month": origin, "pass": False, "reason": "ARCHIVE_ADD_NOT_FOUND"})
            continue
        sha, added = add
        cutoff = pd.Timestamp(base["origin_cutoff_utc"]).to_pydatetime().astimezone(UTC)
        if added > cutoff:
            for s in GPR_SERIES:
                result[s].append({"origin_month": origin, "pass": False, "reason": "ARCHIVE_ADD_AFTER_ORIGIN"})
            continue
        raw = git_bytes(repo, sha, rel)
        digest = hashlib.sha256(raw).hexdigest()
        req = pd.Period(previous_month(origin), freq="M")
        for s in GPR_SERIES:
            try:
                q = workbook_series(raw, s)
                ok = not q[q["date"].dt.to_period("M") == req].empty
                result[s].append({
                    "origin_month": origin, "required_observation_month": str(req),
                    "archive_commit_sha": sha, "archive_commit_at": added.isoformat(),
                    "payload_sha256": digest, "pass": ok,
                    "reason": "OK" if ok else "P_MINUS_1_MISSING",
                })
            except Exception as exc:
                result[s].append({
                    "origin_month": origin, "required_observation_month": str(req),
                    "archive_commit_sha": sha, "archive_commit_at": added.isoformat(),
                    "payload_sha256": digest, "pass": False, "reason": type(exc).__name__,
                })

    summary: dict[str, Any] = {}
    overall = True
    for s in GPR_SERIES:
        good = sum(1 for x in result[s] if x["pass"])
        failed = [x["origin_month"] for x in result[s] if not x["pass"]]
        ok = len(result[s]) == 54 and good == 54
        overall = overall and ok
        summary[s] = {
            "reserved_series_id": f"{s}_OFFICIAL_GIT_PIT",
            "required_origins": 54, "passed_origins": good,
            "failed_origins": failed, "status": "PASS" if ok else "FAIL",
        }
    return {
        "status": "PASS" if overall else "FAIL",
        "availability_policy": "EARLIEST_OFFICIAL_GIT_ARCHIVE_ADD_COMMIT_FLOOR",
        "base_authority_series": "GPR_OFFICIAL_GIT_PIT",
        "summary": summary, "origins": result, "raw_values_logged": False,
    }


def audit_neon(database_url: str) -> dict[str, Any]:
    import psycopg
    from psycopg.rows import dict_row

    out: list[dict[str, Any]] = []
    with psycopg.connect(database_url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            for sid in NEON_INVENTORY_SERIES:
                cur.execute(
                    """
                    select count(*)::bigint row_count, min(observation_ts)::text first_ts,
                           max(observation_ts)::text last_ts, count(distinct lineage_id)::bigint lineage_count,
                           count(*) filter(where value is null)::bigint null_values,
                           count(*) filter(where available_as_of is null)::bigint missing_available_as_of,
                           count(*) filter(where provider_as_of is null)::bigint missing_provider_as_of
                    from observations where series_id=%s
                    """,
                    (sid,),
                )
                r = dict(cur.fetchone())
                r["series_id"] = sid
                out.append(r)
        conn.rollback()
    return {
        "status": "INVENTORY_ONLY_NONBLOCKING", "series_count": len(out), "series": out,
        "database_writes": "NONE", "raw_market_values_logged": False,
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["sources"]
    lines = [
        "# Broad Research Data Spine R1 — Preflight Evidence", "",
        f"- Final gate: **{payload['final_gate']}**",
        f"- Database writes: **{payload['database_writes']}**",
        f"- Model scores: **{payload['model_scores']}**", "",
        "| Gate | Status |", "|---|---|",
        f"| Locked CORE5 monthly research block | {s['core5_locked_monthly']['status']} |",
        f"| Exact pinned four-metal daily panel | {s['staktrakr']['status']} |",
        f"| Twelve XAU hourly-derived daily line | {s['twelve_xau_hourly']['status']} |",
        f"| GPRT + GPRA exact-vintage companions | {s['gpr_companions']['status']} |",
        f"| Neon broad-market inventory | {s['neon_inventory']['status']} |", "",
        "## Authority facts", "",
        f"- CORE5: {s['core5_locked_monthly']['observed_rows']} rows, {s['core5_locked_monthly']['first_month']} .. {s['core5_locked_monthly']['last_month']}.",
        f"- StakTrakr pin: `{s['staktrakr']['pinned_commit']}`; common four-metal days: {s['staktrakr']['common_four_metal_unique_days']}.",
        f"- Twelve months: {s['twelve_xau_hourly']['origin_month_count']}/54; failed months: {len(s['twelve_xau_hourly']['failed_months'])}.",
    ]
    for name, x in s["gpr_companions"]["summary"].items():
        lines.append(f"- {name}: {x['passed_origins']}/{x['required_origins']} — {x['status']}.")
    lines += ["", "No model was scored and no production database row was written by this preflight."]
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

    started = now_utc()
    session = requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-Broad-Research-Data-Spine-R1/1.1"})
    sources = {
        "core5_locked_monthly": audit_core5(),
        "staktrakr": audit_staktrakr(session),
        "twelve_xau_hourly": audit_twelve(session, api_key, args.twelve_pacing_seconds),
        "gpr_companions": audit_gpr_companions(args.gpr_upstream_repo, args.gpr_coverage_json),
        "neon_inventory": audit_neon(db_url),
    }
    blocking = ("core5_locked_monthly", "staktrakr", "twelve_xau_hourly", "gpr_companions")
    ok = all(sources[k]["status"] == "PASS" for k in blocking)
    payload = {
        "pipeline_version": PIPELINE_VERSION, "started_at": started.isoformat(),
        "finished_at": now_utc().isoformat(), "final_gate": "PASS" if ok else "FAIL",
        "database_writes": "NONE", "model_scores": "NONE", "forecast_writes": "NONE",
        "decision_writes": "NONE", "auto_selector": "OFF", "auto_ensemble": "OFF",
        "raw_market_values_logged": False, "sources": sources,
    }
    write_json(args.json_out, payload)
    args.md_out.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps({
        "pipeline_version": PIPELINE_VERSION, "final_gate": payload["final_gate"],
        "core5": sources["core5_locked_monthly"]["status"],
        "staktrakr": sources["staktrakr"]["status"],
        "twelve_xau_hourly": sources["twelve_xau_hourly"]["status"],
        "gpr_companions": sources["gpr_companions"]["status"],
        "neon_inventory": sources["neon_inventory"]["status"],
        "database_writes": "NONE", "model_scores": "NONE", "raw_market_values_logged": False,
    }, indent=2))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
