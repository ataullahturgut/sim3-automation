from __future__ import annotations

"""PIT-safe Patch V7 construction helpers for the manifest v1.22 Multi-Expert engine.

This module is intentionally NOT an issuer.  The legacy single-Patch canonical
writer was removed when Gold Control moved to the v1.22 build-first/select-later
architecture.  The governed Patch issuer may import the deterministic data/model
construction helpers below and persist the result only as a MONTH_END_EXPERT row
through ``stage4b_multi_expert_patch_v7_month_end_issuer.py``.

Direct execution and legacy canonical persistence are fail-closed by design.
"""

import base64
import hashlib
import io
import json
import math
import os
import subprocess
import sys
from calendar import monthrange
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import causal_patch_r1_repro_v6_monthly_level as v6  # noqa: E402
import causal_patch_r1_repro_v7_daily_feature_pit as v7  # noqa: E402

CONTRACT = ROOT / "GOLD_CONTROL_PATCH_V7_FIRST_PROSPECTIVE_SHADOW_ISSUER_CONTRACT_2026-09-02.md"
V7_EVIDENCE = ROOT / "patch_repro_v1" / "locked_replay_v7_daily_feature_pit_evidence.json"
SCHEMA_EVIDENCE = ROOT / "stage4b" / "forecast_writer_schema_evidence.json"
WRITER_EVIDENCE = ROOT / "stage4b" / "patch_v7_writer_rehearsal_evidence.json"

MODEL_NAME = "CAUSAL_PATCH_R1"
MODEL_VERSION = "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE"
MODEL_ROLE = "PRIMARY_EXECUTABLE"
EVIDENCE_CLASS = "PROSPECTIVE_SHADOW"
FIRST_ORIGIN_DATE = pd.Timestamp("2026-09-30")
FIRST_TARGET = pd.Timestamp("2026-10-01")
NY = ZoneInfo("America/New_York")
TWELVE_URL = "https://api.twelvedata.com/time_series"
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
GPR_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls"

ARCHITECTURE_CONTRACT = "MANIFEST_V1_22_MULTI_EXPERT_BUILD_FIRST_SELECT_LATER"
DIRECT_EXECUTION_STATUS = "BLOCKED_MANIFEST_V1_22_RUNNER_CORE_NOT_AN_ISSUER"
CANONICAL_PERSISTENCE_STATUS = "REMOVED_MANIFEST_V1_22_SINGLE_PATCH_CANONICAL_WRITER"
REPLACEMENT_ISSUER = "stage4b_multi_expert_patch_v7_month_end_issuer.py"


def env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name}_MISSING")
    return value


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT.parent, text=True).strip()
    except Exception as exc:
        raise RuntimeError("CANONICAL_GIT_SHA_NOT_RESOLVED") from exc


def static_gates() -> dict:
    text = CONTRACT.read_text(encoding="utf-8")
    if "FROZEN_BEFORE_FIRST_ELIGIBLE_FORWARD_ORIGIN" not in text or MODEL_VERSION not in text:
        raise RuntimeError("FIRST_SHADOW_CONTRACT_NOT_FROZEN")
    v7e = json.loads(V7_EVIDENCE.read_text(encoding="utf-8"))
    se = json.loads(SCHEMA_EVIDENCE.read_text(encoding="utf-8"))
    we = json.loads(WRITER_EVIDENCE.read_text(encoding="utf-8"))
    if v7e.get("decision") != "PATCH_R1_V7_COMPLETED_SESSION_DAILY_FEATURE_MODEL_IMPACT_PASS" or not v7e.get("model_impact_pass"):
        raise RuntimeError("V7_PARENT_NOT_PASS")
    if se.get("decision") != "FORECAST_WRITER_SCHEMA_AUDIT_PASS" or not se.get("schema_audit_pass"):
        raise RuntimeError("FORECAST_SCHEMA_NOT_PASS")
    if we.get("decision") != "PATCH_V7_FORECAST_WRITER_REHEARSAL_PASS" or not we.get("rehearsal_pass"):
        raise RuntimeError("FORECAST_WRITER_REHEARSAL_NOT_PASS")
    return {"v7": v7e["decision"], "schema": se["decision"], "writer": we["decision"]}


def eligibility(now_utc: datetime) -> tuple[bool, str]:
    local = now_utc.astimezone(NY)
    d = pd.Timestamp(local.date())
    if d < FIRST_ORIGIN_DATE:
        return False, "SKIP_NOT_ELIGIBLE_ORIGIN"
    if d > FIRST_ORIGIN_DATE:
        return False, "SKIP_FIRST_ORIGIN_WINDOW_CLOSED_NO_BACKFILL"
    if local.day != monthrange(local.year, local.month)[1]:
        return False, "SKIP_NOT_MONTH_END"
    if local.timetz().replace(tzinfo=None) < time(17, 20):
        return False, "SKIP_BEFORE_17_20_ET"
    return True, "ELIGIBLE_FIRST_PROSPECTIVE_SHADOW_ORIGIN"


def request_json(session: requests.Session, url: str, params: dict, headers: dict | None = None) -> dict:
    return v6.request_json(session, url, params=params, headers=headers)


def fetch_xau_daily(session: requests.Session, origin_date: pd.Timestamp) -> pd.DataFrame:
    payload = request_json(
        session,
        TWELVE_URL,
        {
            "symbol": "XAU/USD", "interval": "1day", "start_date": "2010-01-01",
            "end_date": origin_date.strftime("%Y-%m-%d"), "outputsize": 5000,
            "order": "ASC", "format": "JSON",
        },
        {"Authorization": f"apikey {env('TWELVE_DATA_API_KEY')}", "User-Agent": "Gold-Control-First-Shadow/1.0"},
    )
    meta = payload.get("meta") or {}
    if str(meta.get("symbol")) != "XAU/USD" or str(meta.get("interval")) != "1day":
        raise RuntimeError("FIRST_SHADOW_DAILY_META_MISMATCH")
    rows = []
    for z in payload.get("values") or []:
        try:
            d = pd.Timestamp(str(z.get("datetime"))).normalize(); value = float(z.get("close"))
        except Exception:
            continue
        if np.isfinite(value) and value > 0:
            rows.append((d, value))
    frame = pd.DataFrame(rows, columns=["date", "Gold"]).sort_values("date")
    if frame.empty or frame.duplicated("date").any():
        raise RuntimeError("FIRST_SHADOW_DAILY_HISTORY_INVALID")
    return frame.set_index("date")


def fetch_hourly_anchor(session: requests.Session, origin_date: pd.Timestamp) -> tuple[float, dict]:
    start = origin_date.replace(day=1)
    payload = request_json(
        session,
        TWELVE_URL,
        {
            "symbol": "XAU/USD", "interval": "1h",
            "start_date": start.strftime("%Y-%m-%d 00:00:00"),
            "end_date": origin_date.strftime("%Y-%m-%d 23:59:59"),
            "timezone": "America/New_York", "outputsize": 5000,
            "order": "ASC", "format": "JSON",
        },
        {"Authorization": f"apikey {env('TWELVE_DATA_API_KEY')}", "User-Agent": "Gold-Control-First-Shadow-Anchor/1.0"},
    )
    meta = payload.get("meta") or {}
    if str(meta.get("symbol")) != "XAU/USD" or str(meta.get("interval")) != "1h":
        raise RuntimeError("FIRST_SHADOW_HOURLY_META_MISMATCH")
    rows = []
    seen = set()
    for z in payload.get("values") or []:
        text = str(z.get("datetime", ""))
        if not text.endswith("16:00:00"):
            continue
        try:
            ts = pd.Timestamp(text); value = float(z.get("close"))
        except Exception:
            continue
        d = ts.normalize()
        if d in seen:
            raise RuntimeError("FIRST_SHADOW_HOURLY_DUPLICATE_DATE")
        if np.isfinite(value) and value > 0:
            seen.add(d); rows.append((d, value))
    if len(rows) < 15:
        raise RuntimeError(f"FIRST_SHADOW_HOURLY_ANCHOR_TOO_SPARSE:{len(rows)}")
    values = np.array([x[1] for x in rows], float)
    return float(values.mean()), {
        "provider": "Twelve Data", "symbol": "XAU/USD", "interval": "1h",
        "timezone": "America/New_York", "bar_open": "16:00:00", "bar_end": "17:00_ET",
        "observation_count": len(rows), "first_date": rows[0][0].date().isoformat(),
        "last_date": rows[-1][0].date().isoformat(),
    }


def fred_month_mean_asof(session: requests.Session, series: str, month: pd.Timestamp) -> tuple[float, dict]:
    end = month + pd.offsets.MonthEnd(0)
    payload = request_json(
        session,
        FRED_URL,
        {
            "series_id": series, "api_key": env("FRED_API_KEY"), "file_type": "json",
            "realtime_start": end.date().isoformat(), "realtime_end": end.date().isoformat(),
            "observation_start": month.date().isoformat(), "observation_end": end.date().isoformat(),
            "sort_order": "asc", "limit": 200,
        },
        {"User-Agent": "Gold-Control-First-Shadow/1.0"},
    )
    values = []
    dates = []
    for z in payload.get("observations") or []:
        raw = str(z.get("value", "."))
        if raw in {".", "", "nan", "None"}:
            continue
        try:
            d = pd.Timestamp(str(z.get("date"))).normalize(); value = float(raw)
        except Exception:
            continue
        if d > end:
            raise RuntimeError(f"FRED_FUTURE_DATE:{series}")
        if np.isfinite(value):
            values.append(value); dates.append(d)
    if not values:
        raise RuntimeError(f"FRED_MONTH_EMPTY:{series}:{month.strftime('%Y-%m')}")
    return float(np.mean(values)), {
        "series": series, "provider_realtime_asof": end.date().isoformat(),
        "observation_count": len(values), "max_source_date": max(dates).date().isoformat(),
    }


def fetch_nasdaq_monthly(session: requests.Session, origin_date: pd.Timestamp) -> pd.Series:
    payload = request_json(
        session,
        FRED_URL,
        {
            "series_id": "NASDAQCOM", "api_key": env("FRED_API_KEY"), "file_type": "json",
            "observation_start": "2010-01-01", "observation_end": origin_date.date().isoformat(),
            "sort_order": "asc", "limit": 100000,
        },
        {"User-Agent": "Gold-Control-First-Shadow/1.0"},
    )
    rows = []
    for z in payload.get("observations") or []:
        raw = str(z.get("value", "."))
        if raw in {".", "", "nan", "None"}:
            continue
        try:
            d = pd.Timestamp(str(z.get("date"))).normalize(); value = float(raw)
        except Exception:
            continue
        if np.isfinite(value) and value > 0:
            rows.append((d, value))
    frame = pd.DataFrame(rows, columns=["date", "value"]).sort_values("date")
    if frame.empty or frame.duplicated("date").any():
        raise RuntimeError("FIRST_SHADOW_NASDAQ_INVALID")
    return frame.set_index("date")["value"].resample("MS").mean().dropna()


def fetch_gpr_august(session: requests.Session) -> tuple[float, dict]:
    response = session.get(GPR_URL, timeout=(20, 120), headers={"User-Agent": "Gold-Control-First-Shadow/1.0"})
    response.raise_for_status()
    digest = hashlib.sha256(response.content).hexdigest()
    sheets = pd.read_excel(io.BytesIO(response.content), sheet_name=None, engine="xlrd")
    target = pd.Timestamp("2026-08-01")
    for sheet, frame in sheets.items():
        cols = {str(c).strip().upper(): c for c in frame.columns}
        if "GPR" not in cols:
            continue
        date_col = cols.get("MONTH") or cols.get("DATE") or frame.columns[0]
        q = frame[[date_col, cols["GPR"]]].copy(); q.columns = ["date", "gpr"]
        q["date"] = pd.to_datetime(q["date"], errors="coerce").dt.to_period("M").dt.to_timestamp()
        hit = q[q["date"] == target]
        if hit.empty:
            continue
        value = float(pd.to_numeric(hit.iloc[-1]["gpr"], errors="raise"))
        if not np.isfinite(value) or value < 0:
            raise RuntimeError("FIRST_SHADOW_GPR_INVALID")
        return value, {"source": "Caldara-Iacoviello official workbook", "series": "GPR", "target_month": "2026-08", "sheet": str(sheet), "payload_sha256": digest}
    raise RuntimeError("FIRST_SHADOW_GPR_2026_08_NOT_AVAILABLE")


def training_samples_forward(xau_daily: pd.DataFrame, daily_level: pd.Series, core: pd.DataFrame, nas_monthly: pd.Series) -> list[tuple]:
    samples = []
    final_target = pd.Timestamp("2026-08-01")
    for target in pd.date_range("2011-03-01", final_target, freq="MS"):
        p = target - pd.offsets.MonthBegin(1)
        if target not in daily_level.index or p not in daily_level.index:
            continue
        try:
            _, x, macro = v7.feature_sample_v7(target, xau_daily, core, nas_monthly)
        except RuntimeError:
            continue
        y = float(np.log(float(daily_level.loc[target]) / float(daily_level.loc[p])))
        samples.append((target, x, macro, y))
    if not samples or samples[-1][0] != final_target:
        raise RuntimeError(f"FIRST_SHADOW_TRAINING_SET_DOES_NOT_REACH_2026_08:{samples[-1][0] if samples else 'EMPTY'}")
    return samples


def pack_npz(**arrays) -> tuple[str, str]:
    buf = io.BytesIO(); np.savez_compressed(buf, **arrays); raw = buf.getvalue()
    return base64.b64encode(raw).decode("ascii"), hashlib.sha256(raw).hexdigest()


def build_forecast(now_utc: datetime) -> dict:
    del now_utc  # origin is frozen by the governed V7 contract
    origin_date = FIRST_ORIGIN_DATE
    core = v6.load_core()
    session = requests.Session(); session.headers.update({"User-Agent": "Gold-Control-First-Shadow/1.0"})
    xau_daily = fetch_xau_daily(session, origin_date)
    daily_level, daily_count = v6.daily_monthly_levels(xau_daily)
    if pd.Timestamp("2026-08-01") not in daily_level.index or int(daily_count.loc[pd.Timestamp("2026-08-01")]) < 15:
        raise RuntimeError("FIRST_SHADOW_AUGUST_DAILY_LEVEL_NOT_READY")
    nas_monthly = fetch_nasdaq_monthly(session, origin_date)
    training = training_samples_forward(xau_daily, daily_level, core, nas_monthly)

    fed_sep, fed_meta = fred_month_mean_asof(session, "DFF", pd.Timestamp("2026-09-01"))
    fx_sep, fx_sep_meta = fred_month_mean_asof(session, "DEXCHUS", pd.Timestamp("2026-09-01"))
    fx_aug, fx_aug_meta = fred_month_mean_asof(session, "DEXCHUS", pd.Timestamp("2026-08-01"))
    gpr_aug, gpr_meta = fetch_gpr_august(session)

    core_ext = core.copy()
    for m in [pd.Timestamp("2026-08-01"), pd.Timestamp("2026-09-01")]:
        if m not in core_ext.index:
            core_ext.loc[m] = np.nan
    core_ext.loc[pd.Timestamp("2026-09-01"), "fedfunds"] = fed_sep
    core_ext.loc[pd.Timestamp("2026-09-01"), "usdcny"] = fx_sep
    core_ext.loc[pd.Timestamp("2026-08-01"), "usdcny"] = fx_aug
    core_ext.loc[pd.Timestamp("2026-08-01"), "gpr"] = gpr_aug
    core_ext = core_ext.sort_index()

    _, test_x, test_macro = v7.feature_sample_v7(FIRST_TARGET, xau_daily, core_ext, nas_monthly)
    daily_returns = np.log(xau_daily[["Gold"]]).diff().dropna()
    selected_returns = daily_returns.loc[daily_returns.index < origin_date].iloc[-252:]
    if len(selected_returns) != 252 or selected_returns.index.max() >= origin_date:
        raise RuntimeError("FIRST_SHADOW_V7_DAILY_PIT_GATE_FAIL")

    anchor, anchor_meta = fetch_hourly_anchor(session, origin_date)
    p = pd.Timestamp("2026-09-01")
    all_train = [s for s in training if s[0] < p]
    cut = max(48, int(len(all_train) * 0.85)); cut = min(cut, len(all_train) - 12)
    train, valid = all_train[:cut], all_train[cut:]
    if len(train) < 48 or len(valid) < 12:
        raise RuntimeError("FIRST_SHADOW_TRAIN_VALID_INVALID")
    reps = []
    for offset in [0, 101, 202]:
        model, scale = v6.fit_patch(train, valid, v6.SEED + offset + int(FIRST_TARGET.strftime("%Y%m")), 140)
        reps.append(v6.predict(model, scale, test_x, test_macro))
    predicted_return = float(np.median(reps))
    forecast = float(anchor * math.exp(predicted_return))
    if not np.isfinite(forecast) or forecast <= 0:
        raise RuntimeError("FIRST_SHADOW_FORECAST_INVALID")

    train_payload, train_sha = pack_npz(
        x=np.stack([s[1] for s in all_train]).astype(np.float32),
        macro=np.stack([s[2] for s in all_train]).astype(np.float32),
        y=np.array([s[3] for s in all_train], np.float32),
        target_month=np.array([s[0].strftime("%Y-%m") for s in all_train]),
    )
    test_payload, test_sha = pack_npz(x=test_x.astype(np.float32))
    input_fingerprint = hashlib.sha256(json.dumps({
        "candidate": MODEL_VERSION, "train_sha": train_sha, "test_sha": test_sha,
        "test_macro": [float(x) for x in test_macro], "anchor": anchor,
        "training_n": len(all_train), "cut": cut,
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    return {
        "forecast": forecast, "predicted_return": predicted_return, "training": all_train,
        "training_cut": cut, "training_payload": train_payload, "training_sha": train_sha,
        "test_x": test_x, "test_payload": test_payload, "test_sha": test_sha,
        "test_macro": [float(x) for x in test_macro], "anchor": anchor,
        "input_fingerprint": input_fingerprint, "daily_max_date": selected_returns.index.max().date().isoformat(),
        "source_meta": {"fedfunds": fed_meta, "fx_sep": fx_sep_meta, "fx_aug": fx_aug_meta, "gpr": gpr_meta, "anchor": anchor_meta},
    }


def insert_snapshot(cur, *, issued_at, target_period, sha, series_id, semantic_id, observation_ts, value, transform, lineage, metadata) -> int:
    """Persist one immutable input snapshot through a caller-owned transaction."""
    cur.execute(
        """
        insert into forecast_input_snapshots
          (forecast_origin,target_period,model_name,model_version,git_commit,
           series_id,semantic_id,observation_ts,value_used,available_as_of,
           retrieved_at,transform,lineage_id,metadata)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
        returning id
        """,
        (issued_at, target_period, MODEL_NAME, MODEL_VERSION, sha, series_id, semantic_id,
         observation_ts, float(value), issued_at, issued_at, transform, lineage, json.dumps(metadata)),
    )
    return int(cur.fetchone()["id"])


def persist_shadow(*_args, **_kwargs):
    """Retired compatibility trap: single-Patch canonical persistence is forbidden."""
    raise RuntimeError(CANONICAL_PERSISTENCE_STATUS)


def main() -> int:
    print(f"RUNNER_CORE_STATUS={DIRECT_EXECUTION_STATUS}")
    print(f"ARCHITECTURE_CONTRACT={ARCHITECTURE_CONTRACT}")
    print(f"CANONICAL_PERSISTENCE_STATUS={CANONICAL_PERSISTENCE_STATUS}")
    print(f"REPLACEMENT_ISSUER={REPLACEMENT_ISSUER}")
    print("DATABASE_WRITES=NONE")
    print("FORECAST_VALUE_LOGGED=NO")
    print("RAW_MARKET_VALUES_LOGGED=NO")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
