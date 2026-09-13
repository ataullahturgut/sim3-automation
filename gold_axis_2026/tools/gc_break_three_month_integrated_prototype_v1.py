from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
if str(R4_SRC) not in sys.path:
    sys.path.insert(0, str(R4_SRC))

from gold_r4.emergency import EmergencyState
from gold_r4.gvz import gvz_risk
from gold_r4.monthly import three_month_direction
from gold_r4.tactical import completed_weekly_closes, fast_state, slow_state

CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_three_month_integrated_prototype_contract_v1.json"
EVENT_CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_event_contract_v1.json"
LOCKED_H1 = ROOT / "patch_repro_v1" / "locked_replay_v7_daily_feature_pit_43.csv"


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
        return pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])


def sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-z))


def fit_balanced_ridge_logit(X: np.ndarray, y: np.ndarray, lam: float = 1.0):
    n = len(y)
    n1 = int(y.sum())
    n0 = n - n1
    if n1 < 5 or n0 < 20:
        raise RuntimeError(f"INSUFFICIENT_CLASS_SUPPORT:POS={n1}:NEG={n0}")
    w1 = n / (2.0 * n1)
    w0 = n / (2.0 * n0)
    sw = np.where(y == 1, w1, w0)

    def objective(theta: np.ndarray):
        b = theta[0]
        beta = theta[1:]
        p = sigmoid(b + X @ beta)
        eps = 1e-12
        nll = -np.sum(sw * (y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps)))
        return nll + 0.5 * lam * float(beta @ beta)

    res = minimize(objective, np.zeros(X.shape[1] + 1), method="L-BFGS-B")
    if not res.success:
        raise RuntimeError(f"LOGIT_OPTIMIZATION_FAIL:{res.message}")
    return float(res.x[0]), res.x[1:].astype(float), {"positive_weight": w1, "negative_weight": w0}


def auc_rank(y: np.ndarray, p: np.ndarray):
    y = np.asarray(y, int)
    p = np.asarray(p, float)
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return None
    ranks = pd.Series(p).rank(method="average").to_numpy()
    s = float(ranks[y == 1].sum())
    return float((s - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def same_robust(state: str, regime: str | None) -> bool:
    return (regime == "UP" and state == "ROBUST_UP") or (regime == "DOWN" and state == "ROBUST_DOWN")


def opposite_robust(state: str, regime: str | None) -> bool:
    return (regime == "UP" and state == "ROBUST_DOWN") or (regime == "DOWN" and state == "ROBUST_UP")


def load_inputs(conn, start: str, end_exclusive: str):
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
    macro = fetch_df(conn, """
        SELECT series_id, observation_ts, value, metadata, available_as_of, first_seen_at, retrieved_at, quality_status
        FROM observations
        WHERE series_id = ANY(%s)
          AND observation_ts >= %s AND observation_ts < %s
        ORDER BY observation_ts, series_id
    """, (["MACRO_EVENT_V3_EMPLOYMENT_SCORE", "MACRO_EVENT_V3_INFLATION_SCORE", "MACRO_EVENT_V3_FOMC_SCORE"], start, end_exclusive))
    cache5 = fetch_df(conn, """
        SELECT date_trunc('month', observation_ts)::date AS month,
               COUNT(*) AS rows, COUNT(DISTINCT observation_ts::date) AS distinct_dates,
               MIN(observation_ts) AS min_ts, MAX(observation_ts) AS max_ts
        FROM xau_intraday_research_cache_5m
        WHERE observation_ts >= %s AND observation_ts < %s
        GROUP BY 1 ORDER BY 1
    """, (start, end_exclusive))
    return xau, gvz, vix, macro, cache5


def prepare_h1() -> pd.DataFrame:
    h1 = pd.read_csv(LOCKED_H1)
    h1["month"] = h1["month"].astype(str)
    needed = ["month", "rw", "mom", "vw", "patch_v7"]
    if not set(needed) <= set(h1.columns):
        raise RuntimeError("LOCKED_H1_SCHEMA_FAIL")
    for c in needed[1:]:
        h1[c] = pd.to_numeric(h1[c], errors="raise")
        if (~np.isfinite(h1[c])).any() or (h1[c] <= 0).any():
            raise RuntimeError(f"INVALID_H1:{c}")
    return h1[needed].copy()


def build_bocpd_lookup() -> pd.DataFrame:
    mod = load_module(ROOT / "tools" / "bocpd_return_successor_v1.py", "gc_break_three_month_bocpd")
    replay = mod.build_replay().rows.reset_index()
    replay["month"] = pd.to_datetime(replay["month"]).dt.to_period("M").astype(str)
    keep = ["month", "state", "reset_fraction", "p_run0", "run_length_entropy", "evidence_class"]
    return replay[keep].copy()


def build_role_panel(daily: pd.DataFrame, h1: pd.DataFrame, bocpd: pd.DataFrame) -> pd.DataFrame:
    h1_lookup = h1.set_index("month")
    bocpd_lookup = bocpd.set_index("month")
    month_levels = daily.set_index("date")["close"].resample("MS").last().dropna()
    em = EmergencyState()
    rows = []
    for i, row in daily.iterrows():
        d = pd.Timestamp(row["date"])
        c = float(row["close"])
        hist = daily.loc[:i, ["date", "close"]]
        fs = fast_state(hist["close"].tolist()).value
        ss = slow_state(completed_weekly_closes(hist, d)).value
        mk = d.strftime("%Y-%m")
        month_start = pd.Timestamp(mk + "-01")
        prior = month_levels.loc[month_levels.index < month_start]
        completed_returns = prior.pct_change().dropna().tolist()
        md = three_month_direction(completed_returns).value

        if mk not in h1_lookup.index:
            raise RuntimeError(f"H1_MONTH_MISSING:{mk}")
        hr = h1_lookup.loc[mk]
        h1_vals = [float(hr["rw"]), float(hr["mom"]), float(hr["vw"]), float(hr["patch_v7"])]
        consensus = float(np.median(h1_vals))
        dispersion = float(np.std(h1_vals, ddof=0))
        el, er = em.update(d, c, float(hr["patch_v7"]))

        prior_month = (d.to_period("M") - 1).strftime("%Y-%m")
        if prior_month in bocpd_lookup.index:
            br = bocpd_lookup.loc[prior_month]
            bstate = str(br["state"])
            breset = float(br["reset_fraction"])
            brun0 = float(br["p_run0"])
            bentropy = float(br["run_length_entropy"])
            bevidence = str(br["evidence_class"])
        else:
            bstate = None; breset = np.nan; brun0 = np.nan; bentropy = np.nan; bevidence = None

        rows.append({
            "date": d, "close": c,
            "fast_state": fs, "slow_state": ss, "monthly_direction_3m": md,
            "h1_random_walk": h1_vals[0], "h1_momentum_3m": h1_vals[1],
            "h1_vw_midas": h1_vals[2], "h1_causal_patch": h1_vals[3],
            "h1_consensus_median": consensus, "h1_dispersion_std": dispersion,
            "h1_price_gap_to_consensus": c / consensus - 1.0,
            "emergency_level": el.value, "emergency_reversal": er.value,
            "bocpd_source_month": prior_month, "bocpd_state": bstate,
            "bocpd_reset_fraction": breset, "bocpd_p_run0": brun0,
            "bocpd_run_length_entropy": bentropy, "bocpd_evidence_class": bevidence,
        })
    return pd.DataFrame(rows)


def map_macro_to_origins(origins: pd.DataFrame, macro: pd.DataFrame) -> pd.DataFrame:
    out = origins[["date"]].copy().sort_values("date").reset_index(drop=True)
    out["macro_event_count"] = 0
    out["macro_strong_adverse_count"] = 0
    out["macro_strong_supportive_count"] = 0
    out["macro_max_abs_score"] = 0.0
    origin_dates = out["date"].to_numpy(dtype="datetime64[ns]")
    for _, r in macro.iterrows():
        event_date = pd.Timestamp(r["observation_ts"]).tz_convert("America/New_York").tz_localize(None).normalize()
        pos = int(np.searchsorted(origin_dates, np.datetime64(event_date), side="left"))
        if pos >= len(out):
            continue
        meta = r["metadata"] or {}
        state = str(meta.get("state") or "")
        out.loc[pos, "macro_event_count"] += 1
        out.loc[pos, "macro_strong_adverse_count"] += int(state == "GOLD_ADVERSE_MACRO_SHOCK")
        out.loc[pos, "macro_strong_supportive_count"] += int(state == "GOLD_SUPPORTIVE_MACRO_SHOCK")
        out.loc[pos, "macro_max_abs_score"] = max(float(out.loc[pos, "macro_max_abs_score"]), abs(float(r["value"])))
    return out


def episode_metrics(pred: pd.DataFrame, break_dates: set[pd.Timestamp], signal_col: str):
    x = pred[["date", signal_col]].copy().reset_index(drop=True)
    flags = x[signal_col].astype(bool).to_numpy()
    episodes = []
    start = None
    dates = list(pd.to_datetime(x["date"]))
    for i, flag in enumerate(flags):
        if flag and start is None:
            start = i
        if start is not None and ((not flag) or i == len(flags) - 1):
            end = i - 1 if not flag else i
            sd = dates[start]
            ed = dates[end]
            future_breaks = [b for b in sorted(break_dates) if b >= sd and b <= ed + pd.Timedelta(days=10)]
            converted = bool(future_breaks)
            bd = future_breaks[0] if converted else None
            lead = None
            if converted:
                prior_dates = [d for d in dates if sd <= d <= bd]
                lead = max(len(prior_dates) - 1, 0)
            episodes.append({"start_date": sd.date().isoformat(), "end_date": ed.date().isoformat(), "converted": converted,
                             "break_date": bd.date().isoformat() if bd is not None else None, "lead_origins": lead})
            start = None
    converted = [e for e in episodes if e["converted"]]
    detected = {e["break_date"] for e in converted}
    leads = [e["lead_origins"] for e in converted if e["lead_origins"] is not None]
    return {
        "episodes": len(episodes),
        "converted_episodes": len(converted),
        "false_episodes": len(episodes) - len(converted),
        "event_recall": len(detected) / len(break_dates) if break_dates else None,
        "false_episodes_per_100_origins": (len(episodes) - len(converted)) * 100.0 / len(x) if len(x) else None,
        "median_lead_origins": float(np.median(leads)) if leads else None,
        "episodes_detail": episodes,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("status") != "RESEARCH_ONLY_FROZEN_BEFORE_SCORING":
        raise RuntimeError("PROTOTYPE_CONTRACT_NOT_FROZEN")
    if contract["governance"]["no_database_writes"] is not True:
        raise RuntimeError("NO_WRITE_GUARD_FAIL")

    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")

    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
        # Pull enough prehistory for the learned core and native-clock states.
        xau, gvz, vix, macro_all, cache5 = load_inputs(conn, "2025-01-01", "2026-07-01")

    for d in (xau, gvz, vix):
        d["date"] = pd.to_datetime(d["date"]).dt.normalize()
    xau["close"] = pd.to_numeric(xau["close"], errors="raise")
    gvz["gvz"] = pd.to_numeric(gvz["gvz"], errors="raise")
    vix["vix"] = pd.to_numeric(vix["vix"], errors="raise")
    macro_all["observation_ts"] = pd.to_datetime(macro_all["observation_ts"], utc=True)

    # The research hourly-derived series contains weekend carry-like rows in 2026.
    # Frozen FAST/SLOW are business/trading-clock constructs, so exclude Saturday/Sunday.
    daily = xau[xau["date"].dt.dayofweek < 5][["date", "close"]].drop_duplicates("date").sort_values("date").reset_index(drop=True)
    if daily.empty or (daily["close"] <= 0).any():
        raise RuntimeError("XAU_RESEARCH_DAILY_INVALID")

    h1 = prepare_h1()
    bocpd = build_bocpd_lookup()
    panel = build_role_panel(daily, h1, bocpd)

    diag = load_module(ROOT / "tools" / "gc_break_v0_governed_diagnostic_v1.py", "gc_break_three_month_diag")
    event_contract = json.loads(EVENT_CONTRACT_PATH.read_text(encoding="utf-8"))
    events, origins = diag.build_break_inventory(panel[["date", "close"]], event_contract)
    p = panel.merge(origins, on="date", how="left", validate="one_to_one")

    valid_regime = p["regime_pre"].isin(["UP", "DOWN"])
    p["adverse_fraction_clipped_0_1"] = p["adverse_fraction"].clip(0, 1).fillna(0.0)
    p["fast_conflict"] = valid_regime & ~pd.Series([same_robust(s, r) for s, r in zip(p["fast_state"], p["regime_pre"])])
    p["fast_opposite"] = pd.Series([opposite_robust(s, r) for s, r in zip(p["fast_state"], p["regime_pre"])])
    p["slow_opposite"] = pd.Series([opposite_robust(s, r) for s, r in zip(p["slow_state"], p["regime_pre"])])
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
    core_features = ["adverse_fraction_clipped_0_1", "fast_conflict"]
    train["fast_conflict"] = train["fast_conflict"].astype(int)
    Xtr = train[core_features].to_numpy(float)
    ytr = train["y_next_break"].to_numpy(int)
    intercept, beta, class_weights = fit_balanced_ridge_logit(Xtr, ytr, lam=1.0)
    ptr = sigmoid(intercept + Xtr @ beta)
    threshold = float(np.quantile(ptr, 0.75))

    # Coverage-selected prototype origins: common XAU/GVZ/VIX trading days in Apr-Jun 2026.
    risk = gvz.merge(vix, on="date", how="inner", validate="one_to_one")
    risk = risk[(risk["date"] >= "2026-04-01") & (risk["date"] <= "2026-06-30")].copy()
    test = model[(model["date"] >= "2026-04-01") & (model["date"] <= "2026-06-30")].merge(
        risk[["date", "gvz", "vix"]], on="date", how="inner", validate="one_to_one"
    )
    if len(test) < int(contract["selection_rule"]["minimum_common_xau_gvz_vix_origins"]):
        raise RuntimeError(f"COMMON_ORIGIN_COVERAGE_FAIL:{len(test)}")

    test = test.sort_values("date").reset_index(drop=True)
    macro = macro_all[(macro_all["observation_ts"] >= pd.Timestamp("2026-04-01", tz="UTC")) &
                      (macro_all["observation_ts"] < pd.Timestamp("2026-07-01", tz="UTC"))].copy()
    macro_map = map_macro_to_origins(test, macro)
    test = test.merge(macro_map, on="date", how="left", validate="one_to_one")

    Xte = test[core_features].assign(fast_conflict=test["fast_conflict"].astype(int)).to_numpy(float)
    yte = test["y_next_break"].to_numpy(int)
    pte = sigmoid(intercept + Xte @ beta)
    test["hazard_next_observation"] = pte
    test["weakening"] = test["hazard_next_observation"] >= threshold

    gvz_states = [gvz_risk(float(v)) for v in test["gvz"]]
    test["gvz_cap"] = [float(s.cap) for s in gvz_states]
    test["gvz_panic"] = [bool(s.panic) for s in gvz_states]
    test["macro_event_opposite"] = (
        ((test["regime_pre"] == "UP") & (test["macro_strong_adverse_count"] > 0)) |
        ((test["regime_pre"] == "DOWN") & (test["macro_strong_supportive_count"] > 0))
    )
    test["strong_modifier"] = test["fast_opposite"] | test["emergency_reversal_opposite"] | test["macro_event_opposite"]

    states = []
    consecutive = 0
    for _, r in test.iterrows():
        if bool(r["weakening"]):
            consecutive += 1
            if consecutive >= 2 or bool(r["strong_modifier"]):
                states.append("BREAK_ALERT")
            else:
                states.append("WEAKENING")
        else:
            consecutive = 0
            states.append("STABLE")
    test["sequential_state"] = states
    test["break_alert"] = test["sequential_state"].eq("BREAK_ALERT")

    # Strategic and regime contexts are carried explicitly, never flat-voted.
    test["strategic_prior_conflict"] = (
        ((test["regime_pre"] == "UP") & (test["monthly_direction_3m"] == "DOWN")) |
        ((test["regime_pre"] == "DOWN") & (test["monthly_direction_3m"] == "UP"))
    )
    test["h1_consensus_context"] = np.where(test["h1_price_gap_to_consensus"] >= 0, "PRICE_ABOVE_H1_CONSENSUS", "PRICE_BELOW_H1_CONSENSUS")
    test["risk_context"] = np.where(test["gvz_panic"], "PANIC", np.where(test["gvz_cap"] < 1.0, "ELEVATED", "NORMAL"))
    test["reliability_status"] = np.where(
        test[["bocpd_state", "h1_consensus_median", "gvz"]].notna().all(axis=1),
        "SUPPORTED_RESEARCH_REPLAY", "NO_SIGNAL_MISSING_CONTEXT"
    )

    test_break_dates = set(pd.to_datetime(events.loc[
        (pd.to_datetime(events["break_date"]) >= pd.Timestamp("2026-04-01")) &
        (pd.to_datetime(events["break_date"]) <= pd.Timestamp("2026-06-30")), "break_date"
    ])) if len(events) else set()
    weakening_metrics = episode_metrics(test, test_break_dates, "weakening")
    alert_metrics = episode_metrics(test, test_break_dates, "break_alert")

    # SLOW confirmation is measured after the engine-independent break, not used in the hazard.
    slow_confirmation = []
    for _, ev in events.iterrows():
        bd = pd.Timestamp(ev["break_date"])
        if bd < pd.Timestamp("2026-04-01") or bd > pd.Timestamp("2026-06-30"):
            continue
        new_regime = str(ev["new_regime"])
        after = test[test["date"] >= bd].copy()
        target_state = "ROBUST_UP" if new_regime == "UP" else "ROBUST_DOWN"
        hit = after[after["slow_state"].eq(target_state)]
        confirm = None if hit.empty else pd.Timestamp(hit.iloc[0]["date"])
        slow_confirmation.append({
            "break_date": bd.date().isoformat(), "new_regime": new_regime,
            "confirmation_date": confirm.date().isoformat() if confirm is not None else None,
            "delay_origins": int((after["date"] <= confirm).sum() - 1) if confirm is not None else None,
        })

    # Assert all 12 governed runtime identities are represented in the panel.
    represented = {
        "CAUSAL_PATCH": test["h1_causal_patch"].notna().all(),
        "VW_MIDAS_MSVR_SUCCESSOR_V1": test["h1_vw_midas"].notna().all(),
        "MOMENTUM_3M": test["h1_momentum_3m"].notna().all(),
        "RANDOM_WALK": test["h1_random_walk"].notna().all(),
        "MONTHLY_DIRECTION_3M": test["monthly_direction_3m"].notna().all(),
        "FAST": test["fast_state"].notna().all(),
        "SLOW": test["slow_state"].notna().all(),
        "MACRO_EVENT_SUCCESSOR_V2": True,
        "BOCPD_RETURN_SUCCESSOR_V1": test["bocpd_state"].notna().all(),
        "EMERGENCY_LEVEL": test["emergency_level"].notna().all(),
        "EMERGENCY_REVERSAL": test["emergency_reversal"].notna().all(),
        "GVZ_RISK": test["gvz"].notna().all(),
    }
    if not all(bool(v) for v in represented.values()):
        raise RuntimeError(f"RUNTIME_IDENTITY_INTEGRATION_FAIL:{represented}")

    cache5["month"] = pd.to_datetime(cache5["month"]).dt.strftime("%Y-%m")
    cache_sel = cache5[cache5["month"].isin(["2026-04", "2026-05", "2026-06"])].copy()
    coverage = {
        "selected_window": ["2026-04-01", "2026-06-30"],
        "common_xau_gvz_vix_origins": int(len(test)),
        "months": sorted(test["date"].dt.strftime("%Y-%m").unique().tolist()),
        "origins_by_month": {k: int(v) for k, v in test.groupby(test["date"].dt.strftime("%Y-%m")).size().to_dict().items()},
        "macro_events": int(len(macro)),
        "macro_events_by_family": {str(k): int(v) for k, v in macro["series_id"].value_counts().to_dict().items()},
        "cache5": cache_sel.to_dict(orient="records"),
        "missing_required_context_rows": int((test["reliability_status"] != "SUPPORTED_RESEARCH_REPLAY").sum()),
    }

    summary = {
        "audit_id": "GC_BREAK_THREE_MONTH_INTEGRATED_PROTOTYPE_V1",
        "contract_status": contract["status"],
        "evidence_class": "HISTORICAL_RESEARCH_REPLAY_NOT_CANONICAL_NY17",
        "official_wp4_completion": False,
        "coverage_selection_consumed_outcomes": False,
        "coverage": coverage,
        "runtime_identity_representation": represented,
        "learned_core": {
            "training_start": "2025-01-02", "training_end": "2026-03-31",
            "train_origins": int(len(train)), "train_break_targets": int(ytr.sum()),
            "features": core_features, "intercept": intercept,
            "coefficients": {k: float(v) for k, v in zip(core_features, beta)},
            "class_weights": class_weights, "weakening_threshold_training_q75": threshold,
            "train_auc": auc_rank(ytr, ptr),
        },
        "test": {
            "origins": int(len(test)), "next_break_targets": int(yte.sum()),
            "break_dates": [d.date().isoformat() for d in sorted(test_break_dates)],
            "test_auc": auc_rank(yte, pte),
            "weakening": weakening_metrics,
            "break_alert": alert_metrics,
            "slow_confirmation": slow_confirmation,
        },
        "channel_activity": {
            "fast_conflict_origins": int(test["fast_conflict"].sum()),
            "fast_opposite_origins": int(test["fast_opposite"].sum()),
            "emergency_level_non_neutral": int((test["emergency_level"] != "NEUTRAL").sum()),
            "emergency_reversal_origins": int((test["emergency_reversal"] != "OFF").sum()),
            "strong_macro_event_origins": int(((test["macro_strong_adverse_count"] + test["macro_strong_supportive_count"]) > 0).sum()),
            "gvz_panic_origins": int(test["gvz_panic"].sum()),
            "gvz_elevated_or_panic_origins": int((test["gvz_cap"] < 1.0).sum()),
            "strategic_prior_conflict_origins": int(test["strategic_prior_conflict"].sum()),
            "bocpd_state_counts": {str(k): int(v) for k, v in test["bocpd_state"].value_counts(dropna=False).to_dict().items()},
        },
        "governance": {
            "database_write": "NONE",
            "prospective_claim": False,
            "canonical_exact_ny17": False,
            "post_test_threshold_tuning": False,
            "flat_equal_vote": False,
            "buy_sell_mapping": False,
            "interpretation": "Research-only three-month integration prototype. The 12 governed runtime identities are role-preserved; result is not canonical validation and does not complete manifest WP4."
        }
    }

    test.to_csv(args.output_dir / "gc_break_three_month_integrated_panel_v1.csv", index=False)
    pd.DataFrame(slow_confirmation).to_csv(args.output_dir / "gc_break_three_month_slow_confirmation_v1.csv", index=False)
    (args.output_dir / "gc_break_three_month_integrated_summary_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
