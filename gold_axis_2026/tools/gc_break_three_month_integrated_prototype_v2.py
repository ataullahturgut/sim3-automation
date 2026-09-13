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
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_three_month_integrated_prototype_contract_v2.json"
EVENT_CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_event_contract_v1.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


BASE = load_module(ROOT / "tools" / "gc_break_three_month_integrated_prototype_v1.py", "gc_break_three_month_base_v1")
MACRO_V2 = load_module(ROOT / "data_pipeline" / "macro_event_successor_v2_score_replay.py", "gc_break_macro_event_v2_replay")


def fetch_df(conn, sql: str, params=()) -> pd.DataFrame:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])


def load_market_inputs(conn, start: str, end_exclusive: str):
    xau = fetch_df(conn, """
        SELECT DISTINCT ON (observation_ts::date)
               observation_ts::date AS date, value AS close, quality_status, retrieved_at, metadata
        FROM observations
        WHERE series_id='XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1'
          AND observation_ts >= %s AND observation_ts < %s
        ORDER BY observation_ts::date, retrieved_at DESC NULLS LAST, id DESC
    """, (start, end_exclusive))
    gvz = fetch_df(conn, """
        SELECT DISTINCT ON (observation_ts::date)
               observation_ts::date AS date, value AS gvz, quality_status, retrieved_at
        FROM observations
        WHERE series_id='GVZ_CBOE'
          AND observation_ts >= %s AND observation_ts < %s
        ORDER BY observation_ts::date, retrieved_at DESC NULLS LAST, id DESC
    """, (start, end_exclusive))
    vix = fetch_df(conn, """
        SELECT DISTINCT ON (observation_ts::date)
               observation_ts::date AS date, value AS vix, quality_status, retrieved_at
        FROM observations
        WHERE series_id='VIX_CBOE'
          AND observation_ts >= %s AND observation_ts < %s
        ORDER BY observation_ts::date, retrieved_at DESC NULLS LAST, id DESC
    """, (start, end_exclusive))
    cache5 = fetch_df(conn, """
        SELECT date_trunc('month', observation_ts)::date AS month,
               COUNT(*) AS rows, COUNT(DISTINCT observation_ts::date) AS distinct_dates,
               MIN(observation_ts) AS min_ts, MAX(observation_ts) AS max_ts
        FROM xau_intraday_research_cache_5m
        WHERE observation_ts >= %s AND observation_ts < %s
        GROUP BY 1 ORDER BY 1
    """, (start, end_exclusive))
    return xau, gvz, vix, cache5


def build_macro_v2_events(conn) -> tuple[pd.DataFrame, dict]:
    panel, source_run = MACRO_V2.load_frozen_panel(conn)
    scores = MACRO_V2.compute_scores(panel)
    score_rows = pd.DataFrame([
        {
            "reference_month": r.reference_month,
            "macro_v2_state": r.state,
            "macro_v2_score": r.score,
            "macro_v2_adverse_breadth": r.adverse_breadth,
            "macro_v2_supportive_breadth": r.supportive_breadth,
            "evidence_window": r.evidence_window,
        }
        for r in scores
    ])
    release = fetch_df(conn, """
        SELECT DISTINCT ON (metadata->>'reference_month')
               metadata->>'reference_month' AS reference_month,
               observation_ts AS release_ts,
               available_as_of,
               retrieved_at,
               quality_status,
               metadata
        FROM observations
        WHERE run_id=%s::uuid
          AND series_id='MACRO_NFP_ACTUAL_FIRST_PRINT'
        ORDER BY metadata->>'reference_month', observation_ts
    """, (MACRO_V2.SOURCE_RUN_ID,))
    if release.empty:
        raise RuntimeError("MACRO_V2_RELEASE_TIMESTAMPS_NOT_FOUND")
    release["release_ts"] = pd.to_datetime(release["release_ts"], utc=True)
    out = release.merge(score_rows, on="reference_month", how="inner", validate="one_to_one")
    if len(out) != len(score_rows):
        raise RuntimeError(f"MACRO_V2_SCORE_RELEASE_JOIN_FAIL:{len(out)}:{len(score_rows)}")
    out["release_date_ny"] = out["release_ts"].dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
    lineage = {
        "engine_id": "MACRO_EVENT_SUCCESSOR_V2",
        "source_run_id": MACRO_V2.SOURCE_RUN_ID,
        "source_pipeline": MACRO_V2.SOURCE_PIPELINE,
        "preregistration_blob_sha": MACRO_V2.PREREG_BLOB_SHA,
        "source_run": source_run,
        "score_replay_rows": int(len(score_rows)),
    }
    return out, lineage


def map_macro_v2(origins: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    out = origins[["date"]].copy().sort_values("date").reset_index(drop=True)
    out["macro_v2_event_count"] = 0
    out["macro_v2_strong_adverse_count"] = 0
    out["macro_v2_strong_supportive_count"] = 0
    out["macro_v2_max_abs_score"] = 0.0
    origin_dates = out["date"].to_numpy(dtype="datetime64[ns]")
    for _, ev in events.iterrows():
        event_date = pd.Timestamp(ev["release_date_ny"]).normalize()
        pos = int(np.searchsorted(origin_dates, np.datetime64(event_date), side="left"))
        if pos >= len(out):
            continue
        state = str(ev["macro_v2_state"])
        score = ev["macro_v2_score"]
        out.loc[pos, "macro_v2_event_count"] += 1
        out.loc[pos, "macro_v2_strong_adverse_count"] += int(state == "GOLD_ADVERSE_MACRO_SHOCK")
        out.loc[pos, "macro_v2_strong_supportive_count"] += int(state == "GOLD_SUPPORTIVE_MACRO_SHOCK")
        if score is not None and pd.notna(score):
            out.loc[pos, "macro_v2_max_abs_score"] = max(float(out.loc[pos, "macro_v2_max_abs_score"]), abs(float(score)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("status") != "RESEARCH_ONLY_IDENTITY_CORRECTED_FROZEN_BEFORE_ACCEPTED_SCORING":
        raise RuntimeError("V2_CONTRACT_NOT_FROZEN")
    if contract["governance"]["no_database_writes"] is not True:
        raise RuntimeError("NO_WRITE_GUARD_FAIL")
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")

    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
        xau, gvz, vix, cache5 = load_market_inputs(conn, "2025-01-01", "2026-07-01")
        macro_v2_all, macro_v2_lineage = build_macro_v2_events(conn)

    for d in (xau, gvz, vix):
        d["date"] = pd.to_datetime(d["date"]).dt.normalize()
    xau["close"] = pd.to_numeric(xau["close"], errors="raise")
    gvz["gvz"] = pd.to_numeric(gvz["gvz"], errors="raise")
    vix["vix"] = pd.to_numeric(vix["vix"], errors="raise")

    daily = xau[xau["date"].dt.dayofweek < 5][["date", "close"]].drop_duplicates("date").sort_values("date").reset_index(drop=True)
    if daily.empty or (daily["close"] <= 0).any():
        raise RuntimeError("XAU_RESEARCH_DAILY_INVALID")

    h1 = BASE.prepare_h1()
    bocpd = BASE.build_bocpd_lookup()
    panel = BASE.build_role_panel(daily, h1, bocpd)

    diag = load_module(ROOT / "tools" / "gc_break_v0_governed_diagnostic_v1.py", "gc_break_three_month_diag_v2")
    event_contract = json.loads(EVENT_CONTRACT_PATH.read_text(encoding="utf-8"))
    events, origins = diag.build_break_inventory(panel[["date", "close"]], event_contract)
    p = panel.merge(origins, on="date", how="left", validate="one_to_one")

    valid_regime = p["regime_pre"].isin(["UP", "DOWN"])
    p["adverse_fraction_clipped_0_1"] = p["adverse_fraction"].clip(0, 1).fillna(0.0)
    p["fast_conflict"] = valid_regime & ~pd.Series([BASE.same_robust(s, r) for s, r in zip(p["fast_state"], p["regime_pre"])])
    p["fast_opposite"] = pd.Series([BASE.opposite_robust(s, r) for s, r in zip(p["fast_state"], p["regime_pre"])])
    p["slow_opposite"] = pd.Series([BASE.opposite_robust(s, r) for s, r in zip(p["slow_state"], p["regime_pre"])])
    p["emergency_reversal_opposite"] = (
        ((p["regime_pre"] == "UP") & (p["emergency_reversal"] == "DOWN_ALERT")) |
        ((p["regime_pre"] == "DOWN") & (p["emergency_reversal"] == "UP_ALERT"))
    )
    p["is_break"] = p["event_id"].notna()
    p["next_date"] = p["date"].shift(-1)
    all_break_dates = set(pd.to_datetime(events["break_date"])) if len(events) else set()
    p["y_next_break"] = p["next_date"].isin(all_break_dates).astype(int)

    model = p[~p["is_break"]].copy()
    train = model[(model["date"] >= "2025-01-02") & (model["next_date"] <= "2026-03-31")].copy()
    train["fast_conflict"] = train["fast_conflict"].astype(int)
    features = ["adverse_fraction_clipped_0_1", "fast_conflict"]
    Xtr = train[features].to_numpy(float)
    ytr = train["y_next_break"].to_numpy(int)
    intercept, beta, class_weights = BASE.fit_balanced_ridge_logit(Xtr, ytr, lam=1.0)
    ptr = BASE.sigmoid(intercept + Xtr @ beta)
    threshold = float(np.quantile(ptr, 0.75))

    risk = gvz.merge(vix, on="date", how="inner", validate="one_to_one")
    risk = risk[(risk["date"] >= "2026-04-01") & (risk["date"] <= "2026-06-30")].copy()
    full = p[(p["date"] >= "2026-04-01") & (p["date"] <= "2026-06-30")].merge(
        risk[["date", "gvz", "vix"]], on="date", how="inner", validate="one_to_one"
    ).sort_values("date").reset_index(drop=True)
    if len(full) < int(contract["selection_rule"]["minimum_common_xau_gvz_vix_origins"]):
        raise RuntimeError(f"COMMON_ORIGIN_COVERAGE_FAIL:{len(full)}")

    macro_v2_test = macro_v2_all[
        (macro_v2_all["release_date_ny"] >= pd.Timestamp("2026-04-01")) &
        (macro_v2_all["release_date_ny"] <= pd.Timestamp("2026-06-30"))
    ].copy()
    if macro_v2_test.empty:
        raise RuntimeError("MACRO_EVENT_SUCCESSOR_V2_NO_TEST_EVENTS")
    full = full.merge(map_macro_v2(full, macro_v2_test), on="date", how="left", validate="one_to_one")

    gvz_states = [BASE.gvz_risk(float(v)) for v in full["gvz"]]
    full["gvz_cap"] = [float(s.cap) for s in gvz_states]
    full["gvz_panic"] = [bool(s.panic) for s in gvz_states]
    full["macro_event_v2_opposite"] = (
        ((full["regime_pre"] == "UP") & (full["macro_v2_strong_adverse_count"] > 0)) |
        ((full["regime_pre"] == "DOWN") & (full["macro_v2_strong_supportive_count"] > 0))
    )
    full["strong_modifier"] = full["fast_opposite"] | full["emergency_reversal_opposite"] | full["macro_event_v2_opposite"]
    full["strategic_prior_conflict"] = (
        ((full["regime_pre"] == "UP") & (full["monthly_direction_3m"] == "DOWN")) |
        ((full["regime_pre"] == "DOWN") & (full["monthly_direction_3m"] == "UP"))
    )
    full["h1_consensus_context"] = np.where(full["h1_price_gap_to_consensus"] >= 0, "PRICE_ABOVE_H1_CONSENSUS", "PRICE_BELOW_H1_CONSENSUS")
    full["risk_context"] = np.where(full["gvz_panic"], "PANIC", np.where(full["gvz_cap"] < 1.0, "ELEVATED", "NORMAL"))
    full["reliability_status"] = np.where(
        full[["bocpd_state", "h1_consensus_median", "gvz"]].notna().all(axis=1),
        "SUPPORTED_RESEARCH_REPLAY", "NO_SIGNAL_MISSING_CONTEXT"
    )

    score = full[~full["is_break"]].copy().reset_index(drop=True)
    Xte = score[features].assign(fast_conflict=score["fast_conflict"].astype(int)).to_numpy(float)
    yte = score["y_next_break"].to_numpy(int)
    score["hazard_next_observation"] = BASE.sigmoid(intercept + Xte @ beta)
    score["weakening"] = score["hazard_next_observation"] >= threshold
    states = []
    consecutive = 0
    for _, r in score.iterrows():
        if bool(r["weakening"]):
            consecutive += 1
            states.append("BREAK_ALERT" if consecutive >= 2 or bool(r["strong_modifier"]) else "WEAKENING")
        else:
            consecutive = 0
            states.append("STABLE")
    score["sequential_state"] = states
    score["break_alert"] = score["sequential_state"].eq("BREAK_ALERT")
    full = full.merge(score[["date", "hazard_next_observation", "weakening", "sequential_state", "break_alert"]], on="date", how="left", validate="one_to_one")
    full.loc[full["is_break"], ["weakening", "break_alert"]] = False
    full.loc[full["is_break"], "sequential_state"] = "GROUND_TRUTH_BREAK_NOT_SCORED"

    weakening_metrics = BASE.episode_metrics(full, "weakening")
    alert_metrics = BASE.episode_metrics(full, "break_alert")

    event_meta = events[["break_date", "new_regime"]].copy()
    event_meta["break_date"] = pd.to_datetime(event_meta["break_date"]).dt.normalize()
    if event_meta["break_date"].duplicated().any():
        raise RuntimeError("DUPLICATE_BREAK_DATE_IN_EVENT_META")
    break_rows = full[full["is_break"]].copy().merge(
        event_meta, left_on="date", right_on="break_date", how="left", validate="one_to_one"
    )
    if break_rows["new_regime"].isna().any():
        raise RuntimeError("BREAK_EVENT_REGIME_JOIN_FAIL")
    slow_confirmation = []
    for _, ev in break_rows.iterrows():
        bd = pd.Timestamp(ev["date"])
        new_regime = str(ev["new_regime"])
        next_break = break_rows.loc[break_rows["date"] > bd, "date"].min()
        after = full[full["date"] >= bd].copy()
        if pd.notna(next_break):
            after = after[after["date"] < next_break]
        target = "ROBUST_UP" if new_regime == "UP" else "ROBUST_DOWN"
        hit = after[after["slow_state"].eq(target)]
        confirm = None if hit.empty else pd.Timestamp(hit.iloc[0]["date"])
        delay = None if confirm is None else int(after.reset_index(drop=True).index[after["date"].reset_index(drop=True).eq(confirm)][0])
        slow_confirmation.append({
            "break_date": bd.date().isoformat(),
            "new_regime": new_regime,
            "confirmation_date": confirm.date().isoformat() if confirm is not None else None,
            "delay_origins": delay,
        })

    represented = {
        "CAUSAL_PATCH": bool(full["h1_causal_patch"].notna().all()),
        "VW_MIDAS_MSVR_SUCCESSOR_V1": bool(full["h1_vw_midas"].notna().all()),
        "MOMENTUM_3M": bool(full["h1_momentum_3m"].notna().all()),
        "RANDOM_WALK": bool(full["h1_random_walk"].notna().all()),
        "MONTHLY_DIRECTION_3M": bool(full["monthly_direction_3m"].notna().all()),
        "FAST": bool(full["fast_state"].notna().all()),
        "SLOW": bool(full["slow_state"].notna().all()),
        "MACRO_EVENT_SUCCESSOR_V2": bool(len(macro_v2_test) > 0 and macro_v2_lineage["engine_id"] == "MACRO_EVENT_SUCCESSOR_V2"),
        "BOCPD_RETURN_SUCCESSOR_V1": bool(full["bocpd_state"].notna().all()),
        "EMERGENCY_LEVEL": bool(full["emergency_level"].notna().all()),
        "EMERGENCY_REVERSAL": bool(full["emergency_reversal"].notna().all()),
        "GVZ_RISK": bool(full["gvz"].notna().all()),
    }
    if not all(represented.values()):
        raise RuntimeError(f"RUNTIME_IDENTITY_INTEGRATION_FAIL:{represented}")

    cache5["month"] = pd.to_datetime(cache5["month"]).dt.strftime("%Y-%m")
    cache_sel = cache5[cache5["month"].isin(["2026-04", "2026-05", "2026-06"])].copy()
    break_dates = [pd.Timestamp(d).date().isoformat() for d in full.loc[full["is_break"], "date"]]
    macro_event_rows = [
        {
            "reference_month": str(r.reference_month),
            "release_date_ny": pd.Timestamp(r.release_date_ny).date().isoformat(),
            "state": str(r.macro_v2_state),
            "score": None if pd.isna(r.macro_v2_score) else float(r.macro_v2_score),
        }
        for r in macro_v2_test.itertuples(index=False)
    ]

    summary = {
        "audit_id": "GC_BREAK_THREE_MONTH_INTEGRATED_PROTOTYPE_V2",
        "contract_status": contract["status"],
        "supersedes_invalid_v1": True,
        "v1_invalidation_reason": contract["supersession_reason"],
        "evidence_class": "HISTORICAL_RESEARCH_REPLAY_NOT_CANONICAL_NY17",
        "official_wp4_completion": False,
        "coverage_selection_consumed_outcomes": False,
        "coverage": {
            "selected_window": ["2026-04-01", "2026-06-30"],
            "common_xau_gvz_vix_origins": int(len(full)),
            "scored_non_break_origins": int(len(score)),
            "origins_by_month": {k: int(v) for k, v in full.groupby(full["date"].dt.strftime("%Y-%m")).size().to_dict().items()},
            "macro_event_v2_events": int(len(macro_v2_test)),
            "cache5": cache_sel.to_dict(orient="records"),
            "missing_required_context_rows": int((full["reliability_status"] != "SUPPORTED_RESEARCH_REPLAY").sum()),
        },
        "runtime_identity_representation": represented,
        "macro_event_v2_lineage": macro_v2_lineage,
        "macro_event_v2_test_events": macro_event_rows,
        "learned_core": {
            "training_start": "2025-01-02",
            "training_end": "2026-03-31",
            "train_origins": int(len(train)),
            "train_break_targets": int(ytr.sum()),
            "features": features,
            "intercept": intercept,
            "coefficients": {k: float(v) for k, v in zip(features, beta)},
            "class_weights": class_weights,
            "weakening_threshold_training_q75": threshold,
            "train_auc": BASE.auc_rank(ytr, ptr),
        },
        "test": {
            "coverage_origins": int(len(full)),
            "scored_origins": int(len(score)),
            "next_break_targets": int(yte.sum()),
            "break_dates": break_dates,
            "test_auc": BASE.auc_rank(yte, score["hazard_next_observation"].to_numpy(float)),
            "weakening": weakening_metrics,
            "break_alert": alert_metrics,
            "slow_confirmation": slow_confirmation,
        },
        "channel_activity": {
            "fast_conflict_origins": int(full["fast_conflict"].sum()),
            "fast_opposite_origins": int(full["fast_opposite"].sum()),
            "emergency_level_non_neutral": int((full["emergency_level"] != "NEUTRAL").sum()),
            "emergency_reversal_origins": int((full["emergency_reversal"] != "OFF").sum()),
            "macro_event_v2_strong_event_origins": int(((full["macro_v2_strong_adverse_count"] + full["macro_v2_strong_supportive_count"]) > 0).sum()),
            "gvz_panic_origins": int(full["gvz_panic"].sum()),
            "gvz_elevated_or_panic_origins": int((full["gvz_cap"] < 1.0).sum()),
            "strategic_prior_conflict_origins": int(full["strategic_prior_conflict"].sum()),
            "bocpd_state_counts": {str(k): int(v) for k, v in full["bocpd_state"].value_counts(dropna=False).to_dict().items()},
        },
        "governance": {
            "database_write": "NONE",
            "prospective_claim": False,
            "canonical_exact_ny17": False,
            "post_test_threshold_tuning": False,
            "flat_equal_vote": False,
            "buy_sell_mapping": False,
            "macro_event_identity": "EXACT_MACRO_EVENT_SUCCESSOR_V2_REPLAY",
            "interpretation": "Research-only three-month integration prototype. All 12 governed runtime identities are represented under their manifest identities and role locks. This does not complete manifest WP4 and requires canonical/full-formation validation."
        }
    }

    full.to_csv(args.output_dir / "gc_break_three_month_integrated_panel_v2.csv", index=False)
    macro_v2_test.to_csv(args.output_dir / "gc_break_three_month_macro_event_v2_events.csv", index=False)
    pd.DataFrame(slow_confirmation).to_csv(args.output_dir / "gc_break_three_month_slow_confirmation_v2.csv", index=False)
    (args.output_dir / "gc_break_three_month_integrated_summary_v2.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
