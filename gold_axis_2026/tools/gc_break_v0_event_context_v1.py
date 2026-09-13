from __future__ import annotations

import importlib.util
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_event_context_contract_v1.json"
DIAG_DIR = ROOT / "data_pipeline" / "audits" / "gc_break_v0_diagnostic_v1"
OUT_DIR = ROOT / "data_pipeline" / "audits" / "gc_break_v0_event_context_v1"
SERIES = [
    "MACRO_EVENT_V3_EMPLOYMENT_SCORE",
    "MACRO_EVENT_V3_INFLATION_SCORE",
    "MACRO_EVENT_V3_FOMC_SCORE",
]
STRONG_STATES = {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}


def load_contract() -> dict:
    c = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if c.get("status") != "FROZEN_BEFORE_EVENT_CONTEXT_SCORING":
        raise RuntimeError("EVENT_CONTEXT_CONTRACT_NOT_FROZEN")
    if c.get("database_write_permitted") is not False:
        raise RuntimeError("DATABASE_WRITE_GUARD_FAIL")
    if c["market_shock"]["standalone_promotion"] is not False:
        raise RuntimeError("MARKET_SHOCK_PROMOTION_GUARD_FAIL")
    return c


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def fetch_df(conn, sql: str, params=()) -> pd.DataFrame:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [d.name for d in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)


def load_neon_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
        batch = fetch_df(
            conn,
            """
            SELECT batch_id, series_id, interval, first_ts, last_ts, retrieved_at,
                   provider, symbol, evidence_class, purpose, row_count, inserted_count,
                   payload_sha256, code_sha, status
            FROM xau_intraday_research_cache_batches
            WHERE interval='5min'
            ORDER BY batch_id DESC
            LIMIT 1
            """,
        )
        if len(batch) != 1:
            raise RuntimeError("XAU_5M_CACHE_BATCH_NOT_FOUND")
        raw = fetch_df(
            conn,
            """
            SELECT observation_ts AS ts, close
            FROM xau_intraday_research_cache_5m
            WHERE observation_ts >= '2020-04-06 00:00:00+00'
              AND observation_ts <  '2026-09-01 00:00:00+00'
            ORDER BY observation_ts
            """,
        )
        macro = fetch_df(
            conn,
            """
            SELECT series_id, observation_ts, value, available_as_of, first_seen_at,
                   retrieved_at, quality_status, metadata
            FROM observations
            WHERE series_id = ANY(%s)
              AND observation_ts >= '2025-01-01 00:00:00+00'
              AND observation_ts <  '2026-09-01 00:00:00+00'
            ORDER BY observation_ts, series_id
            """,
            (SERIES,),
        )
        # If any DML accidentally appeared above, PostgreSQL's READ ONLY transaction
        # would fail closed. No commit-side mutation is performed.

    if raw.empty or macro.empty:
        raise RuntimeError(f"REQUIRED_NEON_INPUT_EMPTY:{len(raw)}:{len(macro)}")
    raw["ts"] = pd.to_datetime(raw["ts"], utc=True)
    raw["close"] = pd.to_numeric(raw["close"], errors="raise")
    macro["observation_ts"] = pd.to_datetime(macro["observation_ts"], utc=True)
    macro["score"] = pd.to_numeric(macro["value"], errors="raise")
    macro["state"] = macro["metadata"].map(lambda x: (x or {}).get("state"))
    macro["family"] = macro["metadata"].map(lambda x: (x or {}).get("family"))
    lineage = batch.iloc[0].to_dict()
    lineage = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in lineage.items()}
    return raw, macro, lineage


def score_market_shock(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    ms = load_module(ROOT / "tools" / "market_shock_challenger_v3.py", "gc_break_market_shock_v3")
    data = ms.build_returns(raw)
    segments = []
    reports = []
    for year in (2025, 2026):
        cutoff = pd.Timestamp(f"{year}-01-01", tz="UTC")
        train = data[data["ts"] < cutoff].copy()
        if len(train) < 100000:
            raise RuntimeError(f"MARKET_SHOCK_TRAIN_TOO_SMALL:{year}:{len(train)}")
        periodicity = ms.fit_periodicity(train)
        train_scored = ms.add_scores(train, periodicity)
        evt30 = ms.fit_evt(train_scored["score30"])
        rep, seg, _ = ms.score_segment(data, year, periodicity, evt30)
        reports.append(rep)
        segments.append(seg)
    return pd.concat(segments, ignore_index=True).sort_values("ts").reset_index(drop=True), reports


def first_shock(seg: pd.DataFrame, t: pd.Timestamp, minutes: int) -> pd.Series | None:
    w = seg[
        (seg["ts"] >= t)
        & (seg["ts"] <= t + pd.Timedelta(minutes=minutes))
        & seg["shock_sig"].fillna(False)
    ]
    if w.empty:
        return None
    return w.sort_values("ts").iloc[0]


def build_event_rows(macro: pd.DataFrame, shock: pd.DataFrame, contract: dict) -> pd.DataFrame:
    strong = macro[macro["state"].isin(STRONG_STATES)].copy()
    strong["macro_direction"] = np.sign(strong["score"]).astype(int)
    strong = strong[strong["macro_direction"].ne(0)].copy()
    minutes = int(contract["market_shock"]["event_overlap_window_minutes"])
    rows = []
    for _, ev in strong.iterrows():
        t = pd.Timestamp(ev["observation_ts"])
        match = first_shock(shock, t, minutes)
        shock_present = match is not None
        shock_direction = None
        shock_state = None
        shock_ts = pd.NaT
        concordant = False
        if match is not None:
            shock_direction = int(np.sign(float(match["shock_direction"])))
            shock_state = str(match["shock_state"])
            shock_ts = pd.Timestamp(match["ts"])
            concordant = shock_direction != 0 and shock_direction == int(ev["macro_direction"])
        local = t.tz_convert("America/New_York")
        rows.append(
            {
                "series_id": ev["series_id"],
                "family": ev["family"],
                "release_ts": t,
                "release_date_ny": pd.Timestamp(local.date()),
                "macro_score": float(ev["score"]),
                "macro_state": ev["state"],
                "macro_direction": int(ev["macro_direction"]),
                "market_shock_present_0_10m": shock_present,
                "market_shock_ts": shock_ts,
                "market_shock_state": shock_state,
                "market_shock_direction": shock_direction,
                "direction_concordant": concordant,
                "quality_status": ev["quality_status"],
                "available_as_of": ev["available_as_of"],
                "first_seen_at": ev["first_seen_at"],
                "retrieved_at": ev["retrieved_at"],
            }
        )
    return pd.DataFrame(rows)


def map_events_to_panel(panel: pd.DataFrame, events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    p = panel.sort_values("date").copy().reset_index(drop=True)
    p["date"] = pd.to_datetime(p["date"]).dt.normalize()
    p["macro_strong_event_count"] = 0
    p["macro_opposite_event_count"] = 0
    p["macro_strong_opposite"] = False
    p["event_concordant_opposite"] = False
    p["macro_strong_same_regime"] = False

    mapped = []
    dates = p["date"].to_numpy(dtype="datetime64[ns]")
    for _, ev in events.iterrows():
        release_date = pd.Timestamp(ev["release_date_ny"]).normalize()
        pos = int(np.searchsorted(dates, np.datetime64(release_date), side="left"))
        if pos >= len(p):
            continue
        mapped_date = pd.Timestamp(p.loc[pos, "date"])
        regime = p.loc[pos, "regime_pre"]
        macro_dir = int(ev["macro_direction"])
        opposite = (regime == "UP" and macro_dir < 0) or (regime == "DOWN" and macro_dir > 0)
        same = (regime == "UP" and macro_dir > 0) or (regime == "DOWN" and macro_dir < 0)
        concordant_opposite = bool(opposite and ev["direction_concordant"])
        p.loc[pos, "macro_strong_event_count"] += 1
        p.loc[pos, "macro_opposite_event_count"] += int(opposite)
        p.loc[pos, "macro_strong_opposite"] = bool(p.loc[pos, "macro_strong_opposite"] or opposite)
        p.loc[pos, "event_concordant_opposite"] = bool(p.loc[pos, "event_concordant_opposite"] or concordant_opposite)
        p.loc[pos, "macro_strong_same_regime"] = bool(p.loc[pos, "macro_strong_same_regime"] or same)
        r = ev.to_dict()
        r.update(
            {
                "mapped_origin_date": mapped_date,
                "mapped_regime_pre": regime,
                "opposite_current_regime": bool(opposite),
                "same_current_regime": bool(same),
                "concordant_opposite_regime": concordant_opposite,
            }
        )
        mapped.append(r)
    return p, pd.DataFrame(mapped)


def main() -> int:
    contract = load_contract()
    diag = load_module(ROOT / "tools" / "gc_break_v0_governed_diagnostic_v1.py", "gc_break_diag_module")
    panel_path = DIAG_DIR / "gc_break_v0_origin_panel.csv"
    events_path = DIAG_DIR / "gc_break_v0_break_events.csv"
    if not panel_path.exists() or not events_path.exists():
        raise RuntimeError("RUN_GOVERNED_DIAGNOSTIC_FIRST")
    panel = pd.read_csv(panel_path, parse_dates=["date"])
    breaks = pd.read_csv(events_path, parse_dates=["break_date"])

    raw, macro, lineage = load_neon_inputs()
    shock, shock_reports = score_market_shock(raw)
    event_rows = build_event_rows(macro, shock, contract)
    panel, mapped_events = map_events_to_panel(panel, event_rows)

    panel["core_weakening_event"] = panel["core_weakening"].fillna(False) | panel["macro_strong_opposite"]
    panel["core_break_alert_event"] = (
        panel["core_break_alert"].fillna(False)
        | (panel["core_weakening"].fillna(False) & panel["macro_strong_opposite"])
        | panel["event_concordant_opposite"]
    )

    metrics = []
    episode_frames = []
    for signal in ["core_weakening", "core_weakening_event", "core_break_alert", "core_break_alert_event"]:
        m, e = diag.evaluate_signal(panel, breaks, signal)
        metrics.append(m)
        if not e.empty:
            episode_frames.append(e)
    metrics_df = pd.DataFrame(metrics)
    episodes = pd.concat(episode_frames, ignore_index=True) if episode_frames else pd.DataFrame()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    event_rows.to_csv(OUT_DIR / "gc_break_event_context_strong_macro_events.csv", index=False)
    mapped_events.to_csv(OUT_DIR / "gc_break_event_context_mapped_events.csv", index=False)
    panel.to_csv(OUT_DIR / "gc_break_event_context_augmented_panel.csv", index=False)
    metrics_df.to_csv(OUT_DIR / "gc_break_event_context_warning_metrics.csv", index=False)
    episodes.to_csv(OUT_DIR / "gc_break_event_context_warning_episodes.csv", index=False)

    strong_n = int(len(event_rows))
    shock_n = int(event_rows["market_shock_present_0_10m"].sum()) if strong_n else 0
    concordant_n = int(event_rows["direction_concordant"].sum()) if strong_n else 0
    opposite_n = int(mapped_events["opposite_current_regime"].sum()) if len(mapped_events) else 0
    conc_opp_n = int(mapped_events["concordant_opposite_regime"].sum()) if len(mapped_events) else 0
    summary = {
        "audit_id": "GC_BREAK_V0_EVENT_CONTEXT_V1",
        "event_context_contract_id": contract["contract_id"],
        "event_context_contract_status": contract["status"],
        "evidence_class": "RETROSPECTIVE_HISTORICAL_RESEARCH_NOT_PROSPECTIVE",
        "production_authority": False,
        "neon_access": "READ_ONLY_TRANSACTION",
        "neon_write": False,
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "xau_5m_rows": int(len(raw)),
        "macro_all_rows": int(len(macro)),
        "strong_macro_events": strong_n,
        "strong_event_market_shock_overlap": shock_n,
        "strong_event_direction_concordant": concordant_n,
        "mapped_strong_events": int(len(mapped_events)),
        "mapped_opposite_regime_events": opposite_n,
        "mapped_concordant_opposite_events": conc_opp_n,
        "warning_metrics": metrics_df.set_index("signal").replace({np.nan: None}).to_dict(orient="index"),
        "market_shock_segment_reports": shock_reports,
        "cache_lineage": lineage,
        "role_lock": "Macro Event is event hazard context; Market Shock V3 is confirmation/intensity context and remains not promoted standalone.",
        "interpretation_lock": "RETROSPECTIVE_DIAGNOSTIC_ONLY; event integration rule was frozen before this scoring; no threshold reselection from result.",
    }
    (OUT_DIR / "gc_break_v0_event_context_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
