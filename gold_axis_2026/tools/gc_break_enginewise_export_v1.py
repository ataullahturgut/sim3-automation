from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
if str(R4_SRC) not in sys.path:
    sys.path.insert(0, str(R4_SRC))

from gold_r4 import EmergencyState, completed_weekly_closes, fast_state, gvz_risk, slow_state, three_month_direction  # noqa: E402

START_PREHISTORY = pd.Timestamp("2021-09-01")
EXPORT_START = pd.Timestamp("2022-01-01")
EXPORT_END = pd.Timestamp("2026-08-31")
FINAL_STATUSES = {"VALID_EXACT_BAR", "PROVIDER_NO_BAR"}
H1_LOCKED = ROOT / "patch_repro_v1" / "locked_replay_v7_daily_feature_pit_43.csv"
MACRO_SERIES = [
    "MACRO_EVENT_V3_EMPLOYMENT_SCORE",
    "MACRO_EVENT_V3_INFLATION_SCORE",
    "MACRO_EVENT_V3_FOMC_SCORE",
]
STRONG_MACRO_STATES = {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def split_for_date(day: pd.Timestamp) -> str:
    if day <= pd.Timestamp("2024-12-31"):
        return "FORMATION_2022_2024"
    if day <= pd.Timestamp("2025-12-31"):
        return "RETROSPECTIVE_CHALLENGE_2025"
    return "RETROSPECTIVE_STRESS_2026_JAN_AUG"


def load_exact_csv(path: Path, require_challenge_lineage: bool = False) -> pd.DataFrame:
    d = pd.read_csv(path, dtype=str, keep_default_na=False)
    required = {"trade_date", "acquisition_status"}
    if not required <= set(d.columns):
        raise RuntimeError(f"EXACT_SCHEMA_FAIL:{path}")
    bad = sorted(set(d["acquisition_status"]) - FINAL_STATUSES)
    if bad:
        raise RuntimeError(f"UNRESOLVED_EXACT_STATUS:{path}:{bad[:5]}")
    if require_challenge_lineage:
        lineage = {
            "provider": "Twelve Data",
            "symbol": "XAU/USD",
            "interval": "1min",
            "timezone": "America/New_York",
            "accepted_source_time": "16:59:00",
        }
        for k, v in lineage.items():
            vals = set(d.loc[d["acquisition_status"].eq("VALID_EXACT_BAR"), k]) if k in d.columns else set()
            if vals != {v}:
                raise RuntimeError(f"CHALLENGE_LINEAGE_FAIL:{k}:{vals}")
    d = d[d["acquisition_status"].eq("VALID_EXACT_BAR")].copy()
    d["date"] = pd.to_datetime(d["trade_date"]).dt.normalize()
    d["close"] = pd.to_numeric(d["close"], errors="raise")
    if d["date"].duplicated().any() or (d["close"] <= 0).any() or not np.isfinite(d["close"].to_numpy()).all():
        raise RuntimeError(f"INVALID_EXACT_ROWS:{path}")
    keep = ["date", "close"]
    for c in ["source_bar_datetime", "retrieved_at", "payload_sha256", "evidence_class", "provider", "symbol", "interval", "timezone", "accepted_source_time"]:
        if c in d.columns:
            keep.append(c)
    return d[keep].sort_values("date").reset_index(drop=True)


def fetch_neon_2026_and_context() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                """
                SELECT series_id, observation_ts, value, available_as_of, first_seen_at,
                       retrieved_at, quality_status, metadata
                FROM observations
                WHERE series_id = 'XAU_EOD_TWELVE_NY17'
                  AND observation_ts >= '2026-01-01 00:00:00+00'
                  AND observation_ts <  '2026-09-01 00:00:00+00'
                ORDER BY observation_ts
                """
            )
            xau_rows = cur.fetchall(); xau_cols = [d.name for d in cur.description]
            cur.execute(
                """
                SELECT series_id, observation_ts, value, available_as_of, first_seen_at,
                       retrieved_at, quality_status, metadata
                FROM observations
                WHERE series_id = ANY(%s)
                  AND observation_ts >= '2022-01-01 00:00:00+00'
                  AND observation_ts <  '2026-09-01 00:00:00+00'
                ORDER BY observation_ts, series_id
                """,
                (MACRO_SERIES,),
            )
            macro_rows = cur.fetchall(); macro_cols = [d.name for d in cur.description]
            cur.execute(
                """
                SELECT series_id, observation_ts, value, available_as_of, first_seen_at,
                       retrieved_at, quality_status, metadata
                FROM observations
                WHERE series_id ILIKE '%GVZ%'
                  AND observation_ts >= '2022-01-01 00:00:00+00'
                  AND observation_ts <  '2026-09-01 00:00:00+00'
                ORDER BY series_id, observation_ts
                """
            )
            gvz_rows = cur.fetchall(); gvz_cols = [d.name for d in cur.description]
    xau = pd.DataFrame(xau_rows, columns=xau_cols)
    macro = pd.DataFrame(macro_rows, columns=macro_cols)
    gvz = pd.DataFrame(gvz_rows, columns=gvz_cols)
    if xau.empty:
        raise RuntimeError("NO_2026_XAU_EOD_TWELVE_NY17_ROWS")
    xau["observation_ts"] = pd.to_datetime(xau["observation_ts"], utc=True)
    xau["date"] = xau["observation_ts"].dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
    xau["close"] = pd.to_numeric(xau["value"], errors="raise")
    if xau["date"].duplicated().any() or (xau["close"] <= 0).any():
        raise RuntimeError("INVALID_2026_NEON_XAU")
    xau_out = xau[["date", "close", "observation_ts", "available_as_of", "first_seen_at", "retrieved_at", "quality_status", "metadata"]].copy()
    lineage = {
        "2026_xau_series": "XAU_EOD_TWELVE_NY17",
        "2026_rows": int(len(xau_out)),
        "database_access": "READ_ONLY_TRANSACTION",
        "database_write": "NONE",
    }
    return xau_out, macro, gvz, lineage


def build_history(hist: pd.DataFrame, ch: pd.DataFrame, x26: pd.DataFrame) -> pd.DataFrame:
    a = hist[["date", "close"]].copy(); a["source_period"] = "WP1_EXACT_HISTORY"
    b = ch[["date", "close"]].copy(); b["source_period"] = "2025_EXACT_CHALLENGE"
    c = x26[["date", "close"]].copy(); c["source_period"] = "2026_NEON_CANONICAL"
    x = pd.concat([a, b, c], ignore_index=True).sort_values("date")
    if x["date"].duplicated().any():
        dup = x.loc[x["date"].duplicated(False), "date"].dt.strftime("%Y-%m-%d").tolist()
        raise RuntimeError(f"DUPLICATE_GOVERNED_DATES:{dup[:10]}")
    x = x[x["date"].between(START_PREHISTORY, EXPORT_END)].reset_index(drop=True)
    x["split"] = x["date"].map(split_for_date)
    return x


def state_age(values: pd.Series) -> pd.Series:
    out, prev, age = [], object(), 0
    for v in values.astype(object):
        if pd.isna(v):
            prev, age = object(), 0; out.append(np.nan); continue
        if v == prev: age += 1
        else: prev, age = v, 1
        out.append(age)
    return pd.Series(out, index=values.index, dtype="float64")


def base_export(panel: pd.DataFrame, engine: str, native_clock: str, role: str) -> pd.DataFrame:
    q = panel[panel["date"].between(EXPORT_START, EXPORT_END)][["date", "split", "close"]].copy()
    q.insert(3, "engine_id", engine)
    q["native_clock"] = native_clock
    q["role"] = role
    return q


def engine_fast(history: pd.DataFrame) -> pd.DataFrame:
    vals = []
    for i, r in history.iterrows():
        vals.append(fast_state(history.loc[:i, "close"].tolist()).value)
    tmp = history.copy(); tmp["output_state"] = vals; tmp["state_age"] = state_age(tmp["output_state"])
    q = base_export(tmp, "FAST", "DAILY_GOVERNED_ORIGIN", "TACTICAL_TREND_WEAKENING")
    q["output_state"] = tmp.loc[tmp["date"].between(EXPORT_START, EXPORT_END), "output_state"].to_numpy()
    q["state_age"] = tmp.loc[tmp["date"].between(EXPORT_START, EXPORT_END), "state_age"].to_numpy()
    q["availability_status"] = np.where(q["output_state"].eq("INSUFFICIENT_DATA"), "NOT_TESTABLE_INSUFFICIENT_PREHISTORY", "AVAILABLE")
    q["missing_reason"] = np.where(q["availability_status"].eq("AVAILABLE"), None, "INSUFFICIENT_EXACT_NY17_PREHISTORY")
    return q


def engine_slow(history: pd.DataFrame) -> pd.DataFrame:
    vals = []
    for i, r in history.iterrows():
        h = history.loc[:i, ["date", "close"]]
        vals.append(slow_state(completed_weekly_closes(h, pd.Timestamp(r["date"]))).value)
    tmp = history.copy(); tmp["output_state"] = vals; tmp["state_age"] = state_age(tmp["output_state"])
    m = tmp["date"].between(EXPORT_START, EXPORT_END)
    q = base_export(tmp, "SLOW", "COMPLETED_W_FRI_WEEK", "CONFIRMATION_NEW_REGIME")
    q["output_state"] = tmp.loc[m, "output_state"].to_numpy(); q["state_age"] = tmp.loc[m, "state_age"].to_numpy()
    q["availability_status"] = np.where(q["output_state"].eq("INSUFFICIENT_DATA"), "NOT_TESTABLE_INSUFFICIENT_PREHISTORY", "AVAILABLE")
    q["missing_reason"] = np.where(q["availability_status"].eq("AVAILABLE"), None, "INSUFFICIENT_COMPLETED_WEEK_PREHISTORY")
    return q


def engine_monthly_direction(history: pd.DataFrame) -> pd.DataFrame:
    levels = history.set_index("date")["close"].resample("MS").last().dropna()
    vals = []
    for _, r in history.iterrows():
        day = pd.Timestamp(r["date"]); start = day.to_period("M").to_timestamp()
        prior = levels.loc[levels.index < start]
        vals.append(three_month_direction(prior.pct_change().dropna().tolist()).value)
    tmp = history.copy(); tmp["output_state"] = vals
    m = tmp["date"].between(EXPORT_START, EXPORT_END)
    q = base_export(tmp, "MONTHLY_DIRECTION_3M", "PRIOR_COMPLETED_MONTHS", "STRATEGIC_MONTHLY_PRIOR")
    q["output_state"] = tmp.loc[m, "output_state"].to_numpy()
    q["native_period"] = tmp.loc[m, "date"].dt.strftime("%Y-%m").to_numpy()
    q["availability_status"] = "AVAILABLE"
    q["missing_reason"] = None
    return q


def load_h1_locked() -> pd.DataFrame:
    d = pd.read_csv(H1_LOCKED)
    req = {"month", "rw", "mom", "vw", "patch_v7"}
    if not req <= set(d.columns): raise RuntimeError("H1_LOCKED_REPLAY_SCHEMA_FAIL")
    d = d[["month", "rw", "mom", "vw", "patch_v7"]].copy(); d["month"] = d["month"].astype(str)
    for c in ["rw", "mom", "vw", "patch_v7"]:
        d[c] = pd.to_numeric(d[c], errors="raise")
    return d


def engine_h1(history: pd.DataFrame, locked: pd.DataFrame, engine: str, source_col: str) -> pd.DataFrame:
    q = base_export(history, engine, "MONTHLY_H1_TARGET_MONTH", "INDEPENDENT_MONTHLY_H1_FORECAST_STRATEGIC_CONTEXT")
    month = q["date"].dt.strftime("%Y-%m"); lookup = locked.set_index("month")[source_col].to_dict()
    q["native_period"] = month
    q["forecast_value_usd_oz"] = month.map(lookup)
    q["price_gap_to_forecast"] = q["close"] / q["forecast_value_usd_oz"] - 1.0
    q["availability_status"] = np.where(q["forecast_value_usd_oz"].notna(), "AVAILABLE_FROZEN_HISTORICAL_REPLAY", "NOT_TESTABLE_HISTORICAL_H1_REPLAY_NOT_AVAILABLE")
    q["missing_reason"] = np.where(q["forecast_value_usd_oz"].notna(), None, "NO_FROZEN_H1_REPLAY_FOR_TARGET_MONTH")
    return q


def engine_emergency(history: pd.DataFrame, locked: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    refs = locked.set_index("month")["patch_v7"].to_dict(); state = EmergencyState(); levels=[]; reversals=[]; refs_out=[]; status=[]
    for _, r in history.iterrows():
        month = pd.Timestamp(r["date"]).strftime("%Y-%m"); ref = refs.get(month)
        if ref is None or not np.isfinite(ref):
            levels.append(None); reversals.append(None); refs_out.append(np.nan); status.append("NOT_TESTABLE_REFERENCE_NOT_FOUND")
        else:
            lev, rev = state.update(pd.Timestamp(r["date"]), float(r["close"]), float(ref))
            levels.append(lev.value); reversals.append(rev.value); refs_out.append(float(ref)); status.append("AVAILABLE_FROZEN_REFERENCE")
    tmp = history.copy(); tmp["emergency_level"] = levels; tmp["emergency_reversal"] = reversals; tmp["reference"] = refs_out; tmp["status"] = status
    m = tmp["date"].between(EXPORT_START, EXPORT_END)
    base = tmp.loc[m].reset_index(drop=True)
    q1 = base_export(tmp, "EMERGENCY_LEVEL", "DAILY_ORIGIN_WITH_MONTHLY_CAUSAL_PATCH_REFERENCE", "ABNORMAL_DISPLACEMENT_CONTEXT")
    q1["output_state"] = base["emergency_level"]; q1["monthly_reference"] = base["reference"]; q1["availability_status"] = base["status"]
    q1["missing_reason"] = np.where(q1["availability_status"].eq("AVAILABLE_FROZEN_REFERENCE"), None, "FROZEN_MONTHLY_REFERENCE_NOT_FOUND")
    q2 = base_export(tmp, "EMERGENCY_REVERSAL", "DAILY_ORIGIN_WITH_MONTHLY_CAUSAL_PATCH_REFERENCE", "SELECTIVE_REVERSAL_CONFIRMATION_CONTEXT")
    q2["output_state"] = base["emergency_reversal"]; q2["monthly_reference"] = base["reference"]; q2["availability_status"] = base["status"]
    q2["missing_reason"] = np.where(q2["availability_status"].eq("AVAILABLE_FROZEN_REFERENCE"), None, "FROZEN_MONTHLY_REFERENCE_NOT_FOUND")
    return q1, q2


def engine_bocpd(history: pd.DataFrame) -> pd.DataFrame:
    mod = load_module(ROOT / "tools" / "bocpd_return_successor_v1.py", "enginewise_bocpd")
    replay = mod.build_replay().rows.reset_index(); replay["month"] = pd.to_datetime(replay["month"]).dt.to_period("M")
    lookup = replay.set_index("month")
    q = base_export(history, "BOCPD_RETURN_SUCCESSOR_V1", "PRIOR_COMPLETED_MONTH", "REGIME_BREAK_CONTEXT_NO_DIRECTION_VOTE")
    current = q["date"].dt.to_period("M"); prior = current - 1
    q["native_period"] = prior.astype(str)
    for src, dst in [("state", "output_state"), ("reset_fraction", "reset_fraction"), ("p_run0", "p_run0"), ("run_length_entropy", "run_length_entropy")]:
        q[dst] = prior.map(lookup[src].to_dict())
    q["availability_status"] = np.where(q["output_state"].notna(), "AVAILABLE_NATIVE_MONTHLY_CONTEXT", "NOT_TESTABLE_NATIVE_REPLAY_MONTH_NOT_AVAILABLE")
    q["missing_reason"] = np.where(q["output_state"].notna(), None, "NATIVE_REPLAY_MONTH_NOT_AVAILABLE")
    return q


def engine_macro(history: pd.DataFrame, macro: pd.DataFrame) -> pd.DataFrame:
    q = base_export(history, "MACRO_EVENT_SUCCESSOR_V2", "EVENT_TRIGGERED_RELEASE_CLOCK", "EVENT_SURPRISE_CONTEXT")
    q["strong_event_count"] = 0; q["adverse_event_count"] = 0; q["supportive_event_count"] = 0; q["score_sum"] = 0.0; q["event_families"] = ""
    if macro.empty:
        q["availability_status"] = "NOT_TESTABLE_NO_MACRO_SERIES_ROWS"; q["missing_reason"] = "NO_MACRO_EVENT_SCORE_ROWS"; return q
    m = macro.copy(); m["observation_ts"] = pd.to_datetime(m["observation_ts"], utc=True); m["score"] = pd.to_numeric(m["value"], errors="coerce")
    m["state"] = m["metadata"].map(lambda x: (x or {}).get("state") if isinstance(x, dict) else None)
    m["family"] = m["metadata"].map(lambda x: (x or {}).get("family") if isinstance(x, dict) else None)
    m = m[m["state"].isin(STRONG_MACRO_STATES) & m["score"].notna()].copy()
    dates = q["date"].to_numpy(dtype="datetime64[ns]")
    fams = {i: [] for i in q.index}
    for _, ev in m.iterrows():
        release_date = pd.Timestamp(ev["observation_ts"]).tz_convert("America/New_York").tz_localize(None).normalize()
        pos = int(np.searchsorted(dates, np.datetime64(release_date), side="left"))
        if pos >= len(q): continue
        q.loc[pos, "strong_event_count"] += 1
        q.loc[pos, "adverse_event_count"] += int(ev["state"] == "GOLD_ADVERSE_MACRO_SHOCK")
        q.loc[pos, "supportive_event_count"] += int(ev["state"] == "GOLD_SUPPORTIVE_MACRO_SHOCK")
        q.loc[pos, "score_sum"] += float(ev["score"])
        fams[pos].append(str(ev["family"] or ev["series_id"]))
    q["event_families"] = [";".join(fams[i]) for i in q.index]
    q["availability_status"] = "AVAILABLE_EVENT_SERIES_CONTEXT"
    q["missing_reason"] = None
    return q


def engine_gvz(history: pd.DataFrame, gvz: pd.DataFrame) -> pd.DataFrame:
    q = base_export(history, "GVZ_RISK", "DAILY_RISK_SERIES", "RISK_SEVERITY_UNCERTAINTY_VETO_CONTEXT")
    q["gvz_value"] = np.nan; q["risk_cap"] = np.nan; q["panic"] = np.nan; q["gvz_series_id"] = None
    if gvz.empty:
        q["availability_status"] = "NOT_TESTABLE_PIT_NOT_FOUND"; q["missing_reason"] = "NO_GVZ_SERIES_ROWS_2022_2026"; return q
    g = gvz.copy(); g["observation_ts"] = pd.to_datetime(g["observation_ts"], utc=True); g["date"] = g["observation_ts"].dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize(); g["value_num"] = pd.to_numeric(g["value"], errors="coerce")
    g = g[g["value_num"].notna()].copy()
    # Prefer the canonical-looking series id if present, otherwise use the first available id deterministically.
    ids = list(dict.fromkeys(g["series_id"].astype(str).tolist()))
    preferred = "GVZ_CBOE" if "GVZ_CBOE" in ids else (ids[0] if ids else None)
    if preferred is None:
        q["availability_status"] = "NOT_TESTABLE_PIT_NOT_FOUND"; q["missing_reason"] = "NO_NUMERIC_GVZ_ROWS"; return q
    g = g[g["series_id"].astype(str).eq(preferred)].sort_values("observation_ts").drop_duplicates("date", keep="last")
    lookup = g.set_index("date")["value_num"].to_dict()
    vals = q["date"].map(lookup); q["gvz_value"] = vals; q["gvz_series_id"] = preferred
    caps=[]; pan=[]
    for v in vals:
        if pd.isna(v): caps.append(np.nan); pan.append(np.nan)
        else:
            r = gvz_risk(float(v)); caps.append(float(r.cap)); pan.append(bool(r.panic))
    q["risk_cap"] = caps; q["panic"] = pan
    q["availability_status"] = np.where(q["gvz_value"].notna(), "AVAILABLE_SAME_DAY_PIT_VALUE", "NOT_TESTABLE_NO_SAME_DAY_PIT_VALUE")
    q["missing_reason"] = np.where(q["gvz_value"].notna(), None, "NO_SAME_DAY_GVZ_PIT_VALUE_NO_FILL")
    return q


def write_engine(df: pd.DataFrame, outdir: Path, name: str) -> dict:
    out = outdir / f"{name}.csv"; df.to_csv(out, index=False)
    return {
        "engine_id": name,
        "rows": int(len(df)),
        "origin_min": df["date"].min().date().isoformat() if len(df) else None,
        "origin_max": df["date"].max().date().isoformat() if len(df) else None,
        "available_rows": int(df["availability_status"].astype(str).str.startswith("AVAILABLE").sum()) if "availability_status" in df else None,
        "not_testable_rows": int((~df["availability_status"].astype(str).str.startswith("AVAILABLE")).sum()) if "availability_status" in df else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--historical-exact", type=Path, required=True)
    ap.add_argument("--challenge-exact", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)

    hist = load_exact_csv(args.historical_exact, False)
    ch = load_exact_csv(args.challenge_exact, True)
    x26, macro, gvz, neon_lineage = fetch_neon_2026_and_context()
    history = build_history(hist, ch, x26)
    if history["date"].min() > START_PREHISTORY or history["date"].max() < pd.Timestamp("2026-01-01"):
        raise RuntimeError("ENGINEWISE_HISTORY_COVERAGE_FAIL")

    locked = load_h1_locked()
    outputs: dict[str, pd.DataFrame] = {}
    outputs["CAUSAL_PATCH"] = engine_h1(history, locked, "CAUSAL_PATCH", "patch_v7")
    outputs["VW_MIDAS_MSVR_SUCCESSOR_V1"] = engine_h1(history, locked, "VW_MIDAS_MSVR_SUCCESSOR_V1", "vw")
    outputs["MOMENTUM_3M"] = engine_h1(history, locked, "MOMENTUM_3M", "mom")
    outputs["RANDOM_WALK"] = engine_h1(history, locked, "RANDOM_WALK", "rw")
    outputs["MONTHLY_DIRECTION_3M"] = engine_monthly_direction(history)
    outputs["FAST"] = engine_fast(history)
    outputs["SLOW"] = engine_slow(history)
    outputs["MACRO_EVENT_SUCCESSOR_V2"] = engine_macro(history, macro)
    outputs["BOCPD_RETURN_SUCCESSOR_V1"] = engine_bocpd(history)
    em_level, em_rev = engine_emergency(history, locked)
    outputs["EMERGENCY_LEVEL"] = em_level
    outputs["EMERGENCY_REVERSAL"] = em_rev
    outputs["GVZ_RISK"] = engine_gvz(history, gvz)

    if set(outputs) != {
        "CAUSAL_PATCH", "VW_MIDAS_MSVR_SUCCESSOR_V1", "MOMENTUM_3M", "RANDOM_WALK",
        "MONTHLY_DIRECTION_3M", "FAST", "SLOW", "MACRO_EVENT_SUCCESSOR_V2",
        "BOCPD_RETURN_SUCCESSOR_V1", "EMERGENCY_LEVEL", "EMERGENCY_REVERSAL", "GVZ_RISK"
    }:
        raise RuntimeError("TWELVE_ENGINE_IDENTITY_SET_FAIL")

    summaries=[]
    for name, df in outputs.items(): summaries.append(write_engine(df, args.output_dir, name))
    summary = {
        "audit_id": "GC_BREAK_ENGINEWISE_EXPORT_V1",
        "status": "PASS_ENGINEWISE_EXPORT",
        "requested_export_window": [EXPORT_START.date().isoformat(), EXPORT_END.date().isoformat()],
        "prehistory_start": START_PREHISTORY.date().isoformat(),
        "governed_origins_total_export_window": int(history["date"].between(EXPORT_START, EXPORT_END).sum()),
        "split_counts": history.loc[history["date"].between(EXPORT_START, EXPORT_END), "split"].value_counts().to_dict(),
        "engine_count": len(outputs),
        "engines": summaries,
        "neon_lineage": neon_lineage,
        "governance": {
            "each_engine_exported_separately": True,
            "no_flat_vote": True,
            "no_main_model_fit": True,
            "no_random_split": True,
            "no_interpolation": True,
            "no_forward_fill": True,
            "no_silent_source_substitution": True,
            "database_write": "NONE",
            "2026_role": "RETROSPECTIVE_STRESS_NOT_FRESH_BLIND_OOS",
        },
    }
    (args.output_dir / "ENGINEWISE_EXPORT_SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n", encoding="utf-8")
    history.loc[history["date"].between(EXPORT_START, EXPORT_END)].to_csv(args.output_dir / "GOVERNED_ORIGIN_INDEX_2022_2026.csv", index=False)
    print(json.dumps(summary, indent=2, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
