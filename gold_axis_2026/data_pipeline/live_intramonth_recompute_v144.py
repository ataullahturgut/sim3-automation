from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
if str(R4_SRC) not in sys.path:
    sys.path.insert(0, str(R4_SRC))

from gold_r4.emergency import EmergencyState
from gold_r4.gvz import gvz_risk
from gold_r4.tactical import completed_weekly_closes, fast_state, slow_state

CONTRACT = "GOLD_CONTROL_LIVE_INTRAMONTH_RECOMPUTE_V144"
XAU_SERIES = "XAU_EOD_TWELVE_NY17"
XAU_CROSSCHECK_SERIES = "XAU_DAILY_XAUS"
GVZ_SERIES = "GVZ_CBOE"
XAU_QUALITY = "APPROVED_CANONICAL_TWELVE_NY17"
FEATURE_VERSION = "R4_1_INTRAMONTH_APPEND_ONLY_V144"
CURRENT_FEATURES = ("FAST_STATE", "SLOW_STATE", "GVZ_VALUE", "GVZ_CAP", "GVZ_PANIC", "GVZ_REGIME")
RUNTIME_ENGINES = ("FAST", "SLOW", "GVZ_RISK", "EMERGENCY_LEVEL", "EMERGENCY_REVERSAL")


def _db_url() -> str:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return url


def _code_sha() -> str | None:
    override = os.environ.get("GOLD_CODE_SHA", "").strip().lower()
    if override:
        return override
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        value = proc.stdout.strip().lower()
        return value if len(value) == 40 else None
    except Exception:
        return None


def _utc_iso(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts.isoformat()


def _ny_trade_date(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("America/New_York").date().isoformat()


def _fingerprint(kind: str, payload: Any) -> str:
    body = json.dumps(
        {"contract": CONTRACT, "kind": kind, "payload": payload},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def _target_context(cur) -> str:
    cur.execute("select distinct target_context from current_engine_runtime_state_v1")
    values = [str(r["target_context"] or "").strip() for r in cur.fetchall()]
    values = [v for v in values if v]
    if len(values) != 1:
        raise RuntimeError(f"BLOCKED_CURRENT_TARGET_CONTEXT_NOT_UNIQUE:{values}")
    return values[0]


def _xau_rows(cur) -> list[dict[str, Any]]:
    cur.execute(
        """
        select distinct on (observation_ts)
               id,observation_ts,value,available_as_of,retrieved_at,quality_status,lineage_id,source,source_symbol
        from observations
        where series_id=%s and quality_status=%s
        order by observation_ts,retrieved_at desc,id desc
        """,
        (XAU_SERIES, XAU_QUALITY),
    )
    rows = [dict(r) for r in cur.fetchall()]
    rows.sort(key=lambda r: r["observation_ts"])
    if len(rows) < 21:
        raise RuntimeError(f"BLOCKED_FAST_MIN_HISTORY:{len(rows)}")
    return rows


def _latest_crosscheck_date(cur) -> str | None:
    cur.execute(
        "select observation_ts from canonical_latest where series_id=%s order by observation_ts desc limit 1",
        (XAU_CROSSCHECK_SERIES,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return pd.Timestamp(row["observation_ts"]).date().isoformat()


def _gvz_row(cur) -> dict[str, Any]:
    cur.execute(
        """
        select distinct on (observation_ts)
               id,observation_ts,value,available_as_of,retrieved_at,quality_status,lineage_id,source,source_symbol
        from observations
        where series_id=%s and quality_status like 'APPROVED%%'
        order by observation_ts desc,retrieved_at desc,id desc
        limit 1
        """,
        (GVZ_SERIES,),
    )
    row = cur.fetchone()
    if row is None:
        raise RuntimeError("BLOCKED_GVZ_SOURCE_MISSING")
    return dict(row)


def _runtime_rows(cur, target_context: str) -> dict[str, dict[str, Any]]:
    cur.execute(
        """
        select engine_id,engine_version,engine_role,direction_vote_permitted,metadata,input_fingerprint
        from current_engine_runtime_state_v1
        where target_context=%s and engine_id=any(%s)
        """,
        (target_context, list(set(RUNTIME_ENGINES) | {"CAUSAL_PATCH"})),
    )
    return {str(r["engine_id"]): dict(r) for r in cur.fetchall()}


def _causal_reference(runtime: dict[str, dict[str, Any]], target_context: str) -> dict[str, Any]:
    row = runtime.get("CAUSAL_PATCH")
    if not row:
        raise RuntimeError("BLOCKED_EMERGENCY_REFERENCE_RUNTIME_MISSING")
    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    ref = metadata.get("current_month_reference") if isinstance(metadata.get("current_month_reference"), dict) else None
    if not ref:
        raise RuntimeError("BLOCKED_EMERGENCY_MONTHLY_REFERENCE_MISSING")
    value = ref.get("forecast_value")
    if value is None or float(value) <= 0:
        raise RuntimeError("BLOCKED_EMERGENCY_REFERENCE_VALUE_INVALID")
    ref_target = str(ref.get("target_month") or target_context)[:7]
    if ref_target != target_context:
        raise RuntimeError(f"BLOCKED_EMERGENCY_REFERENCE_TARGET_MISMATCH:{ref_target}:{target_context}")
    evidence = str(ref.get("evidence_class") or "").strip()
    if evidence not in {"HISTORICAL_REPLAY", "PROSPECTIVE_SHADOW", "LIVE_PRODUCTION"}:
        raise RuntimeError(f"BLOCKED_EMERGENCY_REFERENCE_EVIDENCE:{evidence or 'MISSING'}")
    if ref.get("canonical_authority") is True or ref.get("canonical_forecast_authority") is True:
        raise RuntimeError("BLOCKED_EMERGENCY_REFERENCE_CANONICAL_AUTHORITY_UNEXPECTED")
    return {**ref, "forecast_value": float(value), "evidence_class": evidence, "target_month": ref_target}


def _daily_frame(xau: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for r in xau:
        ts = pd.Timestamp(r["observation_ts"])
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        date = ts.tz_convert("America/New_York").tz_localize(None).normalize()
        rows.append(
            {
                "date": date,
                "close": float(r["value"]),
                "id": int(r["id"]),
                "observation_ts": _utc_iso(r["observation_ts"]),
                "available_as_of": _utc_iso(r["available_as_of"]),
                "lineage_id": str(r["lineage_id"]),
            }
        )
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def _weekly_payload(daily: pd.DataFrame, asof: pd.Timestamp) -> list[dict[str, Any]]:
    x = daily.loc[daily["date"] <= asof].copy().sort_values("date").set_index("date")
    closes = x["close"].resample("W-FRI").last().dropna()
    ids = x["id"].resample("W-FRI").last().reindex(closes.index)
    observation_ts = x["observation_ts"].resample("W-FRI").last().reindex(closes.index)
    available_as_of = x["available_as_of"].resample("W-FRI").last().reindex(closes.index)
    lineage_id = x["lineage_id"].resample("W-FRI").last().reindex(closes.index)
    if asof.weekday() < 4:
        current_week_end = asof.to_period("W-FRI").end_time.normalize()
        keep = closes.index < current_week_end
        closes = closes.loc[keep]
        ids = ids.loc[keep]
        observation_ts = observation_ts.loc[keep]
        available_as_of = available_as_of.loc[keep]
        lineage_id = lineage_id.loc[keep]
    return [
        {
            "week_end": pd.Timestamp(idx).date().isoformat(),
            "close": float(closes.loc[idx]),
            "source_observation_id": int(ids.loc[idx]),
            "source_observation_ts": str(observation_ts.loc[idx]),
            "source_available_as_of": str(available_as_of.loc[idx]),
            "lineage_id": str(lineage_id.loc[idx]),
        }
        for idx in closes.index
    ]


def _compute(xau: list[dict[str, Any]], gvz: dict[str, Any], target_context: str, reference: dict[str, Any]) -> dict[str, Any]:
    daily = _daily_frame(xau)
    latest_date = pd.Timestamp(daily.iloc[-1]["date"])

    fast = fast_state(daily["close"].tolist()).value
    weekly_closes = completed_weekly_closes(daily[["date", "close"]], latest_date)
    slow = slow_state(weekly_closes).value
    weekly_lineage = _weekly_payload(daily, latest_date)
    if len(weekly_lineage) < 5:
        raise RuntimeError(f"BLOCKED_SLOW_MIN_COMPLETED_WEEKS:{len(weekly_lineage)}")

    target_daily = daily[daily["date"].dt.strftime("%Y-%m") == target_context]
    if target_daily.empty:
        raise RuntimeError("BLOCKED_EMERGENCY_TARGET_MONTH_XAU_MISSING")
    emergency = EmergencyState()
    level = None
    reversal = None
    for row in target_daily.itertuples(index=False):
        level, reversal = emergency.update(pd.Timestamp(row.date), float(row.close), float(reference["forecast_value"]))
    assert level is not None and reversal is not None

    risk = gvz_risk(float(gvz["value"]))
    regime = "NORMAL" if risk.cap == 1.0 else ("ELEVATED" if risk.cap == 0.5 else "PANIC")

    xau_recent = daily.tail(60)[["id", "observation_ts", "close", "available_as_of", "lineage_id"]].rename(columns={"close": "value"}).to_dict("records")
    fast_lineage = xau_recent[-21:]
    slow_lineage = weekly_lineage[-5:]
    emergency_lineage = target_daily[["id", "observation_ts", "close", "available_as_of", "lineage_id"]].rename(columns={"close": "value"}).to_dict("records")
    gvz_payload = {
        "id": int(gvz["id"]),
        "observation_ts": _utc_iso(gvz["observation_ts"]),
        "value": float(gvz["value"]),
        "available_as_of": _utc_iso(gvz["available_as_of"]),
        "lineage_id": str(gvz["lineage_id"]),
    }

    return {
        "fast": fast,
        "slow": slow,
        "emergency_level": level.value,
        "emergency_reversal": reversal.value,
        "gvz_value": float(risk.value),
        "gvz_cap": float(risk.cap),
        "gvz_panic": bool(risk.panic),
        "gvz_regime": regime,
        "xau_latest_observation_ts": _utc_iso(xau[-1]["observation_ts"]),
        "xau_latest_available_as_of": _utc_iso(xau[-1]["available_as_of"]),
        "xau_latest_trade_date": _ny_trade_date(xau[-1]["observation_ts"]),
        "gvz_latest_observation_ts": gvz_payload["observation_ts"],
        "gvz_latest_available_as_of": gvz_payload["available_as_of"],
        "fast_fingerprint": _fingerprint("FAST", fast_lineage),
        "slow_fingerprint": _fingerprint("SLOW", slow_lineage),
        "emergency_fingerprint": _fingerprint("EMERGENCY", {"xau": emergency_lineage, "reference": reference}),
        "gvz_fingerprint": _fingerprint("GVZ", gvz_payload),
        "fast_lineage": fast_lineage,
        "slow_lineage": slow_lineage,
        "emergency_lineage": emergency_lineage,
        "gvz_lineage": gvz_payload,
    }


def _latest_feature_fingerprint(cur, name: str, target_context: str) -> str | None:
    cur.execute(
        """
        select metadata->>'input_fingerprint' as fp
        from derived_feature_snapshots
        where feature_name=%s and metadata->>'target_context'=%s
        order by calculation_ts desc,id desc limit 1
        """,
        (name, target_context),
    )
    row = cur.fetchone()
    return None if row is None else row["fp"]


def _insert_feature(
    cur,
    *,
    name: str,
    value_num: float | None,
    value_text: str | None,
    input_cutoff: str,
    fingerprint: str,
    lineage: dict[str, Any] | list[dict[str, Any]],
    target_context: str,
    code_sha: str | None,
    evidence_mode: str,
    calculation_ts: datetime,
) -> bool:
    if _latest_feature_fingerprint(cur, name, target_context) == fingerprint:
        return False
    quality = "PROSPECTIVE_SHADOW_INTRAMONTH_CONTEXT" if evidence_mode == "prospective-shadow" else "HISTORICAL_REPLAY_INTRAMONTH_CONTEXT"
    series_id = XAU_SERIES if name in {"FAST_STATE", "SLOW_STATE"} else GVZ_SERIES
    cur.execute(
        """
        insert into derived_feature_snapshots
        (id,feature_name,feature_version,calculation_ts,input_cutoff,value_num,value_text,git_commit,input_lineage,quality_status,metadata)
        values (nextval('derived_feature_snapshots_id_seq'),%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s::jsonb)
        """,
        (
            name, FEATURE_VERSION, calculation_ts, input_cutoff, value_num, value_text, code_sha,
            json.dumps({"source": "Twelve Data" if series_id == XAU_SERIES else "Cboe", "series_id": series_id, "selected_inputs": lineage}),
            quality,
            json.dumps({
                "contract": CONTRACT,
                "target_context": target_context,
                "evidence_mode": evidence_mode,
                "prospective_h1_claim": False,
                "canonical_forecast_authority": False,
                "decision_store_write": "NONE",
                "auto_selector": "OFF",
                "auto_ensemble": "OFF",
                "input_fingerprint": fingerprint,
            }),
        ),
    )
    return True


def _latest_runtime_fingerprint(cur, engine_id: str, target_context: str) -> str | None:
    cur.execute(
        """
        select input_fingerprint from engine_execution_runs
        where engine_id=%s and target_context=%s
        order by as_of desc,created_at desc limit 1
        """,
        (engine_id, target_context),
    )
    row = cur.fetchone()
    return None if row is None else row["input_fingerprint"]


def _insert_runtime(
    cur,
    *,
    base: dict[str, Any],
    engine_id: str,
    state: str,
    fingerprint: str,
    target_context: str,
    information_cutoff: str,
    source_observation_ts: str,
    source_series_id: str,
    code_sha: str | None,
    evidence_mode: str,
    calculation_ts: datetime,
    reference: dict[str, Any] | None = None,
) -> bool:
    if _latest_runtime_fingerprint(cur, engine_id, target_context) == fingerprint:
        return False

    detail = "PROSPECTIVE_SHADOW_INTRAMONTH_CONTEXT" if evidence_mode == "prospective-shadow" else "HISTORICAL_REPLAY_INTRAMONTH_CONTEXT"
    status_code = "ACTIVE_INTRAMONTH_PROSPECTIVE_SHADOW_CONTEXT_REFRESHED" if evidence_mode == "prospective-shadow" else "ACTIVE_INTRAMONTH_CATCHUP_CONTEXT_REFRESHED"
    if reference is not None and reference.get("evidence_class") == "HISTORICAL_REPLAY":
        detail = "CURRENT_INPUT_HISTORICAL_REFERENCE_CONTEXT"
        status_code = "ACTIVE_INTRAMONTH_CURRENT_INPUT_HISTORICAL_REFERENCE_CONTEXT"

    metadata = {
        "current_surface_contract": "GOLD_CONTROL_CURRENT_SURFACE_V144",
        "current_registry": True,
        "current_state": state,
        "current_state_evidence_class": detail,
        "current_state_as_of": calculation_ts.isoformat(),
        "information_cutoff": information_cutoff,
        "source_observation_ts": source_observation_ts,
        "source_series_id": source_series_id,
        "input_fingerprint": fingerprint,
        "operational_refresh_contract": CONTRACT,
        "context_issuance_mode": evidence_mode,
        "prospective_claim": False,
        "prospective_h1_claim": False,
        "canonical_forecast_authority": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "decision_store_write": "NONE",
    }
    if reference is not None:
        metadata.update({
            "reference_expert_id": "CAUSAL_PATCH",
            "monthly_reference_value": reference["forecast_value"],
            "reference_evidence_class": reference["evidence_class"],
            "reference_forecast_origin": reference.get("forecast_origin"),
            "reference_prospective_claim": bool(reference.get("prospective_claim", False)),
            "current_month_reference": {
                "reference_kind": "CURRENT_INTRAMONTH_RECOMPUTED_STATE",
                "state_value": state,
                "target_month": target_context,
                "monthly_reference": reference["forecast_value"],
                "reference_expert_id": "CAUSAL_PATCH",
                "reference_evidence_class": reference["evidence_class"],
                "forecast_origin": reference.get("forecast_origin"),
                "information_cutoff": information_cutoff,
                "source_observation_ts": source_observation_ts,
                "prospective_claim": False,
                "canonical_authority": False,
            },
        })

    cur.execute(
        """
        insert into engine_execution_runs
        (run_id,engine_id,engine_version,engine_role,as_of,target_context,evidence_class,runtime_status,status_code,
         direction_vote_permitted,git_commit,input_fingerprint,metadata,created_at)
        values (%s,%s,%s,%s,%s,%s,'RUNTIME_GOVERNANCE_AUDIT','ACTIVE',%s,%s,%s,%s,%s::jsonb,%s)
        """,
        (
            str(uuid.uuid4()), engine_id, base["engine_version"], base["engine_role"], calculation_ts,
            target_context, status_code, bool(base.get("direction_vote_permitted")), code_sha,
            fingerprint, json.dumps(metadata), calculation_ts,
        ),
    )
    return True


def run(*, persist: bool, evidence_mode: str) -> dict[str, Any]:
    if evidence_mode not in {"catchup", "prospective-shadow"}:
        raise ValueError("evidence_mode must be catchup or prospective-shadow")
    calculation_ts = datetime.now(timezone.utc)
    code_sha = _code_sha()
    conn = psycopg.connect(_db_url(), autocommit=False, row_factory=dict_row)
    try:
        with conn.cursor() as cur:
            if not persist:
                cur.execute("SET TRANSACTION READ ONLY")
            target_context = _target_context(cur)
            xau = _xau_rows(cur)
            canonical_date = _ny_trade_date(xau[-1]["observation_ts"])
            crosscheck_date = _latest_crosscheck_date(cur)
            if crosscheck_date and crosscheck_date > canonical_date:
                raise RuntimeError(f"BLOCKED_CANONICAL_XAU_BEHIND_CROSSCHECK:{canonical_date}:{crosscheck_date}")
            gvz = _gvz_row(cur)
            runtime = _runtime_rows(cur, target_context)
            missing = sorted((set(RUNTIME_ENGINES) | {"CAUSAL_PATCH"}) - set(runtime))
            if missing:
                raise RuntimeError(f"BLOCKED_RUNTIME_BASE_MISSING:{missing}")
            reference = _causal_reference(runtime, target_context)
            state = _compute(xau, gvz, target_context, reference)

            written_features: list[str] = []
            written_runtime: list[str] = []
            if persist:
                xau_cutoff = state["xau_latest_available_as_of"]
                gvz_cutoff = state["gvz_latest_available_as_of"]
                specs = [
                    ("FAST_STATE", None, state["fast"], xau_cutoff, state["fast_fingerprint"], state["fast_lineage"]),
                    ("SLOW_STATE", None, state["slow"], xau_cutoff, state["slow_fingerprint"], state["slow_lineage"]),
                    ("GVZ_VALUE", state["gvz_value"], None, gvz_cutoff, state["gvz_fingerprint"], state["gvz_lineage"]),
                    ("GVZ_CAP", state["gvz_cap"], None, gvz_cutoff, state["gvz_fingerprint"], state["gvz_lineage"]),
                    ("GVZ_PANIC", None, str(state["gvz_panic"]).lower(), gvz_cutoff, state["gvz_fingerprint"], state["gvz_lineage"]),
                    ("GVZ_REGIME", None, state["gvz_regime"], gvz_cutoff, state["gvz_fingerprint"], state["gvz_lineage"]),
                ]
                for name, value_num, value_text, cutoff, fp, lineage in specs:
                    if _insert_feature(
                        cur,
                        name=name,
                        value_num=value_num,
                        value_text=value_text,
                        input_cutoff=cutoff,
                        fingerprint=fp,
                        lineage=lineage,
                        target_context=target_context,
                        code_sha=code_sha,
                        evidence_mode=evidence_mode,
                        calculation_ts=calculation_ts,
                    ):
                        written_features.append(name)

                runtime_specs = [
                    ("FAST", state["fast"], state["fast_fingerprint"], xau_cutoff, state["xau_latest_observation_ts"], XAU_SERIES, None),
                    ("SLOW", state["slow"], state["slow_fingerprint"], xau_cutoff, state["xau_latest_observation_ts"], XAU_SERIES, None),
                    ("GVZ_RISK", f"GVZ={state['gvz_value']} · REGIME={state['gvz_regime']} · CAP={state['gvz_cap']} · PANIC={str(state['gvz_panic']).lower()}", state["gvz_fingerprint"], gvz_cutoff, state["gvz_latest_observation_ts"], GVZ_SERIES, None),
                    ("EMERGENCY_LEVEL", state["emergency_level"], state["emergency_fingerprint"], xau_cutoff, state["xau_latest_observation_ts"], XAU_SERIES, reference),
                    ("EMERGENCY_REVERSAL", state["emergency_reversal"], state["emergency_fingerprint"], xau_cutoff, state["xau_latest_observation_ts"], XAU_SERIES, reference),
                ]
                for engine_id, value, fp, cutoff, obs_ts, series_id, ref in runtime_specs:
                    if _insert_runtime(
                        cur,
                        base=runtime[engine_id],
                        engine_id=engine_id,
                        state=value,
                        fingerprint=fp,
                        target_context=target_context,
                        information_cutoff=cutoff,
                        source_observation_ts=obs_ts,
                        source_series_id=series_id,
                        code_sha=code_sha,
                        evidence_mode=evidence_mode,
                        calculation_ts=calculation_ts,
                        reference=ref,
                    ):
                        written_runtime.append(engine_id)
                conn.commit()
            else:
                conn.rollback()

            return {
                "contract": CONTRACT,
                "target_context": target_context,
                "persist": persist,
                "evidence_mode": evidence_mode,
                "canonical_xau_trade_date": canonical_date,
                "crosscheck_xau_trade_date": crosscheck_date,
                "state": state,
                "written_features": written_features,
                "written_runtime": written_runtime,
                "decision_store_write": "NONE",
                "forecast_authority_write": "NONE",
                "auto_selector": "OFF",
                "auto_ensemble": "OFF",
            }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persist", action="store_true")
    parser.add_argument("--evidence-mode", choices=["catchup", "prospective-shadow"], default="prospective-shadow")
    args = parser.parse_args()
    result = run(persist=args.persist, evidence_mode=args.evidence_mode)
    print(json.dumps(result, indent=2, default=str))
    print("LIVE_INTRAMONTH_RECOMPUTE_V144_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
