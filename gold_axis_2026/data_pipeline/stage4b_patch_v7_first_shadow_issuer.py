from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import math
import os
import subprocess
import sys
from calendar import monthrange
from datetime import datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import psycopg
import requests
from psycopg.rows import dict_row

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
PREFLIGHT_OUT = ROOT / "stage4b" / "first_shadow_issuer_preflight_evidence.json"

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


def read_ledger_state(url: str) -> dict:
    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("select count(*) as n from forecast_input_snapshots")
            inputs = int(cur.fetchone()["n"])
            cur.execute("select count(*) as n from monthly_forecast_contracts")
            contracts = int(cur.fetchone()["n"])
            cur.execute(
                """
                select count(*) as n from monthly_forecast_contracts
                where target_month=%s and model_name=%s and model_version=%s and model_role=%s
                """,
                (FIRST_TARGET.date(), MODEL_NAME, MODEL_VERSION, MODEL_ROLE),
            )
            duplicate = int(cur.fetchone()["n"])
        conn.rollback()
    return {"forecast_input_rows": inputs, "forecast_contract_rows": contracts, "target_duplicate_rows": duplicate}


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


def persist_shadow(url: str, issued_at: datetime, result: dict, sha: str) -> dict:
    target_period = "2026-10"
    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """select count(*) as n from monthly_forecast_contracts
                       where target_month=%s and model_name=%s and model_version=%s and model_role=%s""",
                    (FIRST_TARGET.date(), MODEL_NAME, MODEL_VERSION, MODEL_ROLE),
                )
                if int(cur.fetchone()["n"]) != 0:
                    conn.rollback(); return {"duplicate": True}

                ids = []
                ids.append(insert_snapshot(
                    cur, issued_at=issued_at, target_period=target_period, sha=sha,
                    series_id="PATCH_V7_TRAINING_TENSOR", semantic_id="MODEL_TRAINING_TENSOR",
                    observation_ts=issued_at, value=len(result["training"]),
                    transform="NPZ_COMPRESSED_EXACT_TRAINING_TENSOR_V1", lineage=MODEL_VERSION,
                    metadata={"encoding":"npz_compressed_base64","payload_b64":result["training_payload"],"sha256":result["training_sha"],"training_sample_count":len(result["training"]),"train_valid_cut":result["training_cut"],"evidence_class":EVIDENCE_CLASS},
                ))
                ids.append(insert_snapshot(
                    cur, issued_at=issued_at, target_period=target_period, sha=sha,
                    series_id="PATCH_V7_TEST_X_TENSOR", semantic_id="MODEL_TEST_X_TENSOR",
                    observation_ts=issued_at, value=252,
                    transform="NPZ_COMPRESSED_EXACT_252X2_TEST_TENSOR_V1", lineage=MODEL_VERSION,
                    metadata={"encoding":"npz_compressed_base64","payload_b64":result["test_payload"],"sha256":result["test_sha"],"shape":[252,2],"daily_feature_max_date":result["daily_max_date"],"same_origin_date_use":False,"evidence_class":EVIDENCE_CLASS},
                ))
                macro_specs = [
                    ("DFF_FRED","FEDFUNDS",result["test_macro"][0],"MONTHLY_MEAN_DFF_ASOF_2026_09_30",result["source_meta"]["fedfunds"]),
                    ("NASDAQCOM_COMPLETED_MONTH_RETURN_MARKET_CLOSE_V3","NASDAQ_RETURN",result["test_macro"][1],"LOG_COMPLETED_MONTH_MEAN_RETURN_AUG_OVER_JUL_V3",{"months":["2026-08","2026-07"]}),
                    ("DEXCHUS_FRED","USDCNY_RETURN",result["test_macro"][2],"LOG_MONTHLY_MEAN_RETURN_SEP_OVER_AUG_OWN_MONTHEND_VINTAGES",{"sep":result["source_meta"]["fx_sep"],"aug":result["source_meta"]["fx_aug"]}),
                    ("GPR_OFFICIAL","GPR_LOG1P_LAG2",result["test_macro"][3],"LOG1P_GPR_2026_08_LAG2",result["source_meta"]["gpr"]),
                    ("GPR_OFFICIAL","GPR_MINMAX_Z_LAG2",result["test_macro"][4],"MINMAX_Z_GPR_2026_08_LAG2_FROZEN_CORE_PLUS_CURRENT",result["source_meta"]["gpr"]),
                ]
                for series_id, semantic_id, value, transform, meta in macro_specs:
                    ids.append(insert_snapshot(cur, issued_at=issued_at, target_period=target_period, sha=sha,
                        series_id=series_id, semantic_id=semantic_id, observation_ts=issued_at,
                        value=value, transform=transform, lineage=series_id,
                        metadata={"source_meta":meta,"evidence_class":EVIDENCE_CLASS}))
                ids.append(insert_snapshot(cur, issued_at=issued_at, target_period=target_period, sha=sha,
                    series_id="PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V6_ANCHOR",
                    semantic_id="MONTHLY_REFERENCE_ANCHOR", observation_ts=issued_at,
                    value=result["anchor"], transform="MONTHLY_MEAN_17ET_HOURLY_CLOSE_2026_09",
                    lineage="PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V6_ANCHOR",
                    metadata={"source_meta":result["source_meta"]["anchor"],"evidence_class":EVIDENCE_CLASS}))

                cur.execute(
                    """
                    insert into derived_feature_snapshots
                      (feature_name,feature_version,calculation_ts,input_cutoff,value_num,
                       git_commit,input_lineage,quality_status,metadata)
                    values (%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s::jsonb)
                    returning id
                    """,
                    ("PATCH_V7_PREDICTED_LOG_RETURN",MODEL_VERSION,issued_at,issued_at,
                     result["predicted_return"],sha,json.dumps({"forecast_input_snapshot_ids":ids,"input_fingerprint":result["input_fingerprint"]}),
                     EVIDENCE_CLASS,json.dumps({"target_month":"2026-10","prospective_claim":True,"auto_selector":"OFF","auto_ensemble":"OFF"})),
                )
                derived_id = int(cur.fetchone()["id"])

                provenance = {
                    "evidence_class": EVIDENCE_CLASS, "prospective_claim": True,
                    "forecast_input_snapshot_ids": ids, "derived_feature_snapshot_id": derived_id,
                    "input_fingerprint": result["input_fingerprint"], "model_impact_parent": "PATCH_R1_V7_COMPLETED_SESSION_DAILY_FEATURE_MODEL_IMPACT_PASS",
                    "writer_rehearsal_parent": "PATCH_V7_FORECAST_WRITER_REHEARSAL_PASS",
                    "auto_selector": "OFF", "auto_ensemble": "OFF", "decision_store_write": "NONE",
                }
                cur.execute(
                    """
                    insert into monthly_forecast_contracts
                      (target_month,forecast_origin,model_name,model_version,forecast_value,
                       unit,model_role,frozen_at,git_commit,provenance)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                    returning id
                    """,
                    (FIRST_TARGET.date(),issued_at,MODEL_NAME,MODEL_VERSION,result["forecast"],
                     "USD/oz",MODEL_ROLE,issued_at,sha,json.dumps(provenance)),
                )
                contract_id = int(cur.fetchone()["id"])
            conn.commit()
        except Exception:
            conn.rollback(); raise

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("select id,model_name,model_version,model_role,provenance from monthly_forecast_contracts where id=%s", (contract_id,))
            contract = cur.fetchone()
            cur.execute("select count(*) as n from forecast_input_snapshots where id=any(%s)", (ids,))
            snapshot_n = int(cur.fetchone()["n"])
        conn.rollback()
    if not contract or snapshot_n != len(ids) or contract["model_version"] != MODEL_VERSION or (contract["provenance"] or {}).get("evidence_class") != EVIDENCE_CLASS:
        raise RuntimeError("FIRST_SHADOW_POST_COMMIT_VERIFY_FAILED")
    return {"duplicate":False,"contract_id":contract_id,"snapshot_ids":ids,"derived_feature_id":derived_id,"snapshot_count":snapshot_n}


def preflight(now_utc: datetime) -> int:
    parents = static_gates(); url = env("NEON_DATABASE_URL"); ledger = read_ledger_state(url); eligible, reason = eligibility(now_utc)
    passed = bool(ledger["forecast_input_rows"] == 0 and ledger["forecast_contract_rows"] == 0 and ledger["target_duplicate_rows"] == 0)
    evidence = {
        "generated_at": now_utc.isoformat(), "candidate_id": MODEL_VERSION,
        "parents": parents, "ledger": ledger, "current_origin_eligible": eligible,
        "eligibility_state": reason, "earliest_eligible_origin": "2026-09-30 after 17:20 America/New_York",
        "first_target": "2026-10", "september_backfill_allowed": False,
        "persistent_database_writes": "NONE", "raw_market_values_logged": False,
        "preflight_pass": passed,
        "decision": "FIRST_SHADOW_ISSUER_PREFLIGHT_PASS_WAITING_FOR_ELIGIBLE_ORIGIN" if passed else "BLOCKED_FIRST_SHADOW_ISSUER_PREFLIGHT",
    }
    PREFLIGHT_OUT.parent.mkdir(parents=True, exist_ok=True); PREFLIGHT_OUT.write_text(json.dumps(evidence,indent=2,sort_keys=True),encoding="utf-8")
    print(f"FIRST_SHADOW_ISSUER_PREFLIGHT_PASS={str(passed).lower()}")
    print(f"ELIGIBILITY_STATE={reason}")
    print("SEPTEMBER_BACKFILL_ALLOWED=NO")
    print("PERSISTENT_DATABASE_WRITES=NONE")
    print("RAW_MARKET_VALUES_LOGGED=NO")
    return 0 if passed else 3


def issue_if_eligible(now_utc: datetime) -> int:
    static_gates(); url = env("NEON_DATABASE_URL"); eligible, reason = eligibility(now_utc)
    if not eligible:
        print(f"FIRST_SHADOW_ISSUER_STATE={reason}")
        print("DATABASE_WRITES=NONE")
        print("RAW_MARKET_VALUES_LOGGED=NO")
        return 0
    ledger = read_ledger_state(url)
    if ledger["target_duplicate_rows"] > 0:
        print("FIRST_SHADOW_ISSUER_STATE=SKIP_ALREADY_ISSUED")
        print("DATABASE_WRITES=NONE")
        return 0
    if ledger["forecast_input_rows"] != 0 or ledger["forecast_contract_rows"] != 0:
        raise RuntimeError(f"PRE_ISSUANCE_LEDGER_NOT_EMPTY:{ledger}")
    result = build_forecast(now_utc); sha = git_sha(); persisted = persist_shadow(url, now_utc, result, sha)
    if persisted.get("duplicate"):
        print("FIRST_SHADOW_ISSUER_STATE=SKIP_ALREADY_ISSUED_RACE")
        return 0
    print("FIRST_SHADOW_ISSUER_STATE=PROSPECTIVE_SHADOW_ISSUED_VERIFIED")
    print(f"TARGET_MONTH=2026-10")
    print(f"MODEL_VERSION={MODEL_VERSION}")
    print(f"EVIDENCE_CLASS={EVIDENCE_CLASS}")
    print(f"FORECAST_CONTRACT_ID={persisted['contract_id']}")
    print(f"FORECAST_INPUT_SNAPSHOT_COUNT={persisted['snapshot_count']}")
    print(f"DERIVED_FEATURE_SNAPSHOT_ID={persisted['derived_feature_id']}")
    print("FORECAST_VALUE_LOGGED=NO")
    print("RAW_MARKET_VALUES_LOGGED=NO")
    print("DECISION_STORE_WRITE=NONE")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--mode", choices=["preflight","issue-if-eligible"], required=True); args = parser.parse_args()
    now_utc = datetime.now(timezone.utc)
    return preflight(now_utc) if args.mode == "preflight" else issue_if_eligible(now_utc)


if __name__ == "__main__":
    raise SystemExit(main())
