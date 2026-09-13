from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_event_contract_v1.json"
NY17_PATH = ROOT / "data_pipeline" / "audits" / "component_role_replays_v145" / "ny17_context_role_replay_v145.csv"
GVZ_PATH = ROOT / "data_pipeline" / "audits" / "component_role_replays_v145" / "gvz_role_replay_v145.csv"
OUT_DIR = ROOT / "data_pipeline" / "audits" / "gc_break_v0_diagnostic_v1"


def load_contract() -> dict:
    c = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if c.get("status") != "FROZEN_BEFORE_GC_BREAK_V0_DIAGNOSTIC_SCORING":
        raise RuntimeError("EVENT_CONTRACT_NOT_FROZEN")
    if c["primary_event_rule"]["engine_inputs_forbidden"] == []:
        raise RuntimeError("ENGINE_INDEPENDENCE_GUARD_MISSING")
    if c["governance"]["no_database_writes"] is not True:
        raise RuntimeError("NO_WRITE_GUARD_MISSING")
    return c


def load_ny17() -> pd.DataFrame:
    d = pd.read_csv(NY17_PATH)
    d["date"] = pd.to_datetime(d["date"]).dt.normalize()
    d["close"] = pd.to_numeric(d["close"], errors="raise")
    if d["date"].duplicated().any():
        raise RuntimeError("DUPLICATE_NY17_DATES")
    if (d["close"] <= 0).any() or not np.isfinite(d["close"]).all():
        raise RuntimeError("INVALID_NY17_CLOSE")
    return d.sort_values("date").reset_index(drop=True)


def load_gvz() -> pd.DataFrame:
    g = pd.read_csv(GVZ_PATH)
    g["observation_date"] = pd.to_datetime(g["observation_date"]).dt.normalize()
    g["value"] = pd.to_numeric(g["value"], errors="coerce")
    g["panic"] = g["panic"].astype(str).str.lower().eq("true")
    return g.sort_values("observation_date").reset_index(drop=True)


def build_break_inventory(d: pd.DataFrame, contract: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    r = contract["primary_event_rule"]
    window = int(r["sigma_window_observations"])
    k = float(r["k_sigma"])
    logp = np.log(d["close"].to_numpy(float))
    ret = pd.Series(logp).diff()
    sigma = ret.shift(int(r["sigma_lag"])).rolling(window, min_periods=window).std(ddof=int(r["sigma_ddof"]))

    trend: int | None = None
    extreme = math.nan
    extreme_i: int | None = None
    events: list[dict] = []
    rows: list[dict] = []

    for i, row in d.iterrows():
        px = float(row["close"])
        sig = float(sigma.iloc[i]) if pd.notna(sigma.iloc[i]) else math.nan

        if trend is None and i >= window and math.isfinite(sig) and sig > 0:
            mom = logp[i] - logp[i - window]
            if mom > 0:
                trend = 1
                extreme = px
                extreme_i = i
            elif mom < 0:
                trend = -1
                extreme = px
                extreme_i = i

        regime_pre = trend
        event_id = None
        adverse_move = math.nan
        adverse_fraction = math.nan
        threshold = k * sig if math.isfinite(sig) and sig > 0 else math.nan
        pre_extreme = extreme
        pre_extreme_i = extreme_i

        if trend is not None:
            if trend == 1:
                if px > extreme:
                    extreme = px
                    extreme_i = i
                adverse_move = max(0.0, math.log(extreme / px))
            else:
                if px < extreme:
                    extreme = px
                    extreme_i = i
                adverse_move = max(0.0, math.log(px / extreme))
            if math.isfinite(threshold) and threshold > 0:
                adverse_fraction = adverse_move / threshold

            if math.isfinite(threshold) and threshold > 0 and adverse_move >= threshold:
                old = trend
                new = -trend
                event_id = len(events) + 1
                events.append(
                    {
                        "event_id": event_id,
                        "break_date": row["date"],
                        "old_regime": "UP" if old == 1 else "DOWN",
                        "new_regime": "UP" if new == 1 else "DOWN",
                        "close": px,
                        "lagged_sigma20": sig,
                        "threshold_log_move": threshold,
                        "adverse_log_move": adverse_move,
                        "adverse_fraction": adverse_fraction,
                        "extreme_date": d.iloc[int(extreme_i)]["date"] if extreme_i is not None else pd.NaT,
                        "extreme_close": extreme,
                        "event_contract_id": contract["contract_id"],
                    }
                )
                trend = new
                extreme = px
                extreme_i = i

        rows.append(
            {
                "date": row["date"],
                "regime_pre": None if regime_pre is None else ("UP" if regime_pre == 1 else "DOWN"),
                "regime_post": None if trend is None else ("UP" if trend == 1 else "DOWN"),
                "lagged_sigma20": sig,
                "threshold_log_move": threshold,
                "adverse_log_move": adverse_move,
                "adverse_fraction": adverse_fraction,
                "event_id": event_id,
                "event_contract_id": contract["contract_id"],
                "pre_extreme_close": pre_extreme,
                "pre_extreme_index": pre_extreme_i,
            }
        )

    return pd.DataFrame(events), pd.DataFrame(rows)


def add_bocpd(panel: pd.DataFrame) -> pd.DataFrame:
    # Import the already-frozen monthly BOCPD successor; do not mutate its identity.
    import importlib.util
    import sys

    p = ROOT / "tools" / "bocpd_return_successor_v1.py"
    spec = importlib.util.spec_from_file_location("gc_break_bocpd_frozen", p)
    if not spec or not spec.loader:
        raise RuntimeError("BOCPD_IMPORT_FAIL")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    replay = mod.build_replay().rows.reset_index()
    replay["month"] = pd.to_datetime(replay["month"]).dt.to_period("M")
    state_map = replay.set_index("month")["state"].to_dict()

    current = panel["date"].dt.to_period("M")
    previous = current - 1
    panel["bocpd_prior_completed_month_state"] = previous.map(state_map)
    panel["bocpd_adverse_candidate"] = panel["bocpd_prior_completed_month_state"].eq("ADVERSE_BREAK_CANDIDATE")
    panel["bocpd_direction_vote_permitted"] = False
    return panel


def same_robust(state: pd.Series, regime: pd.Series) -> pd.Series:
    return ((regime == "UP") & (state == "ROBUST_UP")) | ((regime == "DOWN") & (state == "ROBUST_DOWN"))


def opposite_robust(state: pd.Series, regime: pd.Series) -> pd.Series:
    return ((regime == "UP") & (state == "ROBUST_DOWN")) | ((regime == "DOWN") & (state == "ROBUST_UP"))


def add_signals(panel: pd.DataFrame) -> pd.DataFrame:
    valid_regime = panel["regime_pre"].isin(["UP", "DOWN"])
    panel["path_half"] = valid_regime & panel["adverse_fraction"].ge(0.50)
    panel["fast_same"] = same_robust(panel["fast_state"], panel["regime_pre"])
    panel["fast_conflict"] = valid_regime & ~panel["fast_same"]
    panel["fast_opposite"] = valid_regime & opposite_robust(panel["fast_state"], panel["regime_pre"])
    panel["slow_same"] = same_robust(panel["slow_state"], panel["regime_pre"])
    panel["slow_conflict"] = valid_regime & ~panel["slow_same"]
    panel["slow_opposite"] = valid_regime & opposite_robust(panel["slow_state"], panel["regime_pre"])
    panel["emergency_level_opposite"] = (
        ((panel["regime_pre"] == "UP") & (panel["emergency_level"] == "DOWN"))
        | ((panel["regime_pre"] == "DOWN") & (panel["emergency_level"] == "UP"))
    )
    panel["emergency_reversal_opposite"] = (
        ((panel["regime_pre"] == "UP") & (panel["emergency_reversal"] == "DOWN_ALERT"))
        | ((panel["regime_pre"] == "DOWN") & (panel["emergency_reversal"] == "UP_ALERT"))
    )
    panel["emergency_any_opposite"] = panel["emergency_level_opposite"] | panel["emergency_reversal_opposite"]
    panel["monthly_direction_conflict"] = (
        ((panel["regime_pre"] == "UP") & (panel["monthly_direction_3m"] == "DOWN"))
        | ((panel["regime_pre"] == "DOWN") & (panel["monthly_direction_3m"] == "UP"))
    )

    # Role-preserving research states frozen in code before this diagnostic run.
    panel["core_weakening"] = panel["fast_conflict"] | panel["emergency_reversal_opposite"]
    panel["core_break_alert"] = (
        (panel["fast_opposite"] & (panel["emergency_any_opposite"] | panel["slow_conflict"]))
        | (panel["emergency_reversal_opposite"] & panel["slow_conflict"])
        | ((panel["regime_pre"] == "UP") & panel["bocpd_adverse_candidate"] & panel["fast_conflict"])
    )
    panel["core_confirm"] = panel["slow_opposite"]
    panel["path_half_and_fast"] = panel["path_half"] & panel["fast_conflict"]
    panel["fast_and_emergency"] = panel["fast_conflict"] & panel["emergency_any_opposite"]
    panel["fast_and_slow"] = panel["fast_conflict"] & panel["slow_conflict"]
    return panel


def add_gvz_sensitivity(panel: pd.DataFrame, gvz: pd.DataFrame) -> pd.DataFrame:
    # Historical daily join only. Exact release clock was not proven in V1.49,
    # so GVZ is explicitly excluded from primary PIT signal definitions.
    g = gvz[["observation_date", "value", "panic"]].copy().sort_values("observation_date")
    p = panel.sort_values("date").copy()
    p = pd.merge_asof(p, g, left_on="date", right_on="observation_date", direction="backward")
    p = p.rename(columns={"value": "gvz_value", "panic": "gvz_panic"})
    p["gvz_pit_status"] = "RETROSPECTIVE_SENSITIVITY_ONLY_EXACT_RELEASE_CLOCK_NOT_PROVEN"
    p["core_break_alert_gvz_sensitivity"] = p["core_break_alert"] & p["gvz_panic"].fillna(False)
    return p


def signal_episodes(panel: pd.DataFrame, signal: str) -> pd.DataFrame:
    x = panel[["date", signal, "event_id"]].copy().reset_index(drop=True)
    on = x[signal].fillna(False).astype(bool).to_numpy()
    episodes = []
    start = None
    for i, flag in enumerate(on):
        if flag and start is None:
            start = i
        if start is not None and (not flag or i == len(on) - 1):
            end = i - 1 if not flag else i
            evs = x.loc[start:end, "event_id"].dropna().astype(int).tolist()
            episodes.append(
                {
                    "signal": signal,
                    "episode_id": len(episodes) + 1,
                    "start_i": start,
                    "end_i": end,
                    "start_date": x.loc[start, "date"],
                    "end_date": x.loc[end, "date"],
                    "converted_event_id": evs[0] if evs else None,
                }
            )
            start = None
    return pd.DataFrame(episodes)


def evaluate_signal(panel: pd.DataFrame, events: pd.DataFrame, signal: str) -> tuple[dict, pd.DataFrame]:
    eps = signal_episodes(panel, signal)
    if eps.empty:
        return {
            "signal": signal,
            "origins": int(len(panel)),
            "events": int(len(events)),
            "episodes": 0,
            "converted_episodes": 0,
            "false_episodes": 0,
            "episode_conversion_rate": None,
            "prebreak_event_recall": 0.0 if len(events) else None,
            "at_or_before_event_recall": 0.0 if len(events) else None,
            "false_episodes_per_100_origins": 0.0,
            "median_lead_observations": None,
            "median_lead_calendar_days": None,
            "mean_lead_observations": None,
            "mean_lead_calendar_days": None,
        }, eps

    converted = eps[eps["converted_event_id"].notna()].copy()
    false = eps[eps["converted_event_id"].isna()].copy()
    event_lookup = events.set_index("event_id")["break_date"].to_dict() if len(events) else {}
    panel_pos = {d: i for i, d in enumerate(panel["date"])}
    leads_obs = []
    leads_cal = []
    prebreak_events = set()
    detected_events = set()
    for _, ep in converted.iterrows():
        eid = int(ep["converted_event_id"])
        b = pd.Timestamp(event_lookup[eid])
        s = pd.Timestamp(ep["start_date"])
        lead_obs = panel_pos[b] - int(ep["start_i"])
        lead_cal = (b - s).days
        leads_obs.append(lead_obs)
        leads_cal.append(lead_cal)
        detected_events.add(eid)
        if lead_obs > 0:
            prebreak_events.add(eid)

    n_events = int(len(events))
    n_ep = int(len(eps))
    n_conv = int(len(converted))
    metric = {
        "signal": signal,
        "origins": int(len(panel)),
        "events": n_events,
        "episodes": n_ep,
        "converted_episodes": n_conv,
        "false_episodes": int(len(false)),
        "episode_conversion_rate": float(n_conv / n_ep) if n_ep else None,
        "prebreak_event_recall": float(len(prebreak_events) / n_events) if n_events else None,
        "at_or_before_event_recall": float(len(detected_events) / n_events) if n_events else None,
        "false_episodes_per_100_origins": float(len(false) * 100.0 / len(panel)) if len(panel) else None,
        "median_lead_observations": float(np.median(leads_obs)) if leads_obs else None,
        "median_lead_calendar_days": float(np.median(leads_cal)) if leads_cal else None,
        "mean_lead_observations": float(np.mean(leads_obs)) if leads_obs else None,
        "mean_lead_calendar_days": float(np.mean(leads_cal)) if leads_cal else None,
    }
    return metric, eps


def confirmation_delays(panel: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for j, ev in events.iterrows():
        b = pd.Timestamp(ev["break_date"])
        new_regime = ev["new_regime"]
        start_i = int(panel.index[panel["date"].eq(b)][0])
        next_i = len(panel) - 1
        if j + 1 < len(events):
            nb = pd.Timestamp(events.iloc[j + 1]["break_date"])
            next_i = int(panel.index[panel["date"].eq(nb)][0]) - 1
        target_state = "ROBUST_UP" if new_regime == "UP" else "ROBUST_DOWN"
        seg = panel.loc[start_i:next_i]
        hit = seg[seg["slow_state"].eq(target_state)]
        if hit.empty:
            hit_i = None
            hit_date = pd.NaT
            obs_delay = None
            cal_delay = None
        else:
            hit_i = int(hit.index[0])
            hit_date = pd.Timestamp(hit.iloc[0]["date"])
            obs_delay = hit_i - start_i
            cal_delay = (hit_date - b).days
        rows.append(
            {
                "event_id": int(ev["event_id"]),
                "break_date": b,
                "new_regime": new_regime,
                "slow_confirmation_date": hit_date,
                "delay_observations": obs_delay,
                "delay_calendar_days": cal_delay,
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    contract = load_contract()
    ny = load_ny17()
    gvz = load_gvz()
    events, anatomy = build_break_inventory(ny, contract)

    panel = ny.merge(anatomy, on="date", how="left", validate="one_to_one")
    panel = add_bocpd(panel)
    panel = add_signals(panel)
    panel = add_gvz_sensitivity(panel, gvz)

    signals = [
        "path_half",
        "fast_conflict",
        "fast_opposite",
        "path_half_and_fast",
        "fast_and_emergency",
        "fast_and_slow",
        "core_weakening",
        "core_break_alert",
        "core_break_alert_gvz_sensitivity",
    ]
    metrics = []
    episode_frames = []
    for signal in signals:
        m, e = evaluate_signal(panel, events, signal)
        metrics.append(m)
        if not e.empty:
            episode_frames.append(e)
    metrics_df = pd.DataFrame(metrics)
    episodes_df = pd.concat(episode_frames, ignore_index=True) if episode_frames else pd.DataFrame()
    conf = confirmation_delays(panel, events)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT_DIR / "gc_break_v0_origin_panel.csv", index=False)
    events.to_csv(OUT_DIR / "gc_break_v0_break_events.csv", index=False)
    metrics_df.to_csv(OUT_DIR / "gc_break_v0_warning_metrics.csv", index=False)
    episodes_df.to_csv(OUT_DIR / "gc_break_v0_warning_episodes.csv", index=False)
    conf.to_csv(OUT_DIR / "gc_break_v0_confirmation_delays.csv", index=False)

    conf_valid = conf.dropna(subset=["delay_observations"])
    summary = {
        "audit_id": "GC_BREAK_V0_GOVERNED_DIAGNOSTIC_V1",
        "event_contract_id": contract["contract_id"],
        "event_contract_status": contract["status"],
        "evidence_class": "RETROSPECTIVE_HISTORICAL_RECONSTRUCTION_NOT_PROSPECTIVE",
        "production_authority": False,
        "production_database_write": "NONE",
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "rows": int(len(panel)),
        "start_date": panel["date"].min().strftime("%Y-%m-%d"),
        "end_date": panel["date"].max().strftime("%Y-%m-%d"),
        "primary_break_events": int(len(events)),
        "break_direction_counts": events["new_regime"].value_counts().to_dict() if len(events) else {},
        "warning_metrics": metrics_df.set_index("signal").replace({np.nan: None}).to_dict(orient="index"),
        "slow_confirmation": {
            "events": int(len(conf)),
            "confirmed_before_next_break": int(len(conf_valid)),
            "rate": float(len(conf_valid) / len(conf)) if len(conf) else None,
            "median_delay_observations": float(conf_valid["delay_observations"].median()) if len(conf_valid) else None,
            "median_delay_calendar_days": float(conf_valid["delay_calendar_days"].median()) if len(conf_valid) else None,
        },
        "role_locks": {
            "BOCPD": "NATIVE_COMPLETED_MONTH_CONTEXT_ONLY_DIRECTION_VOTE_FALSE",
            "GVZ": "RETROSPECTIVE_SENSITIVITY_ONLY_EXACT_RELEASE_CLOCK_NOT_PROVEN",
            "MONTHLY_DIRECTION_3M": "STRATEGIC_CONTEXT_NOT_STANDALONE_BREAK_VOTE",
            "FAST": "TACTICAL_WEAKENING_CONTEXT",
            "SLOW": "CONFIRMATION_CONTEXT",
            "EMERGENCY": "ABNORMALITY_REVERSAL_CONTEXT",
        },
        "interpretation_lock": "RETROSPECTIVE_DIAGNOSTIC_ONLY; NO MODEL OR THRESHOLD MAY BE PROMOTED FROM THIS RESULT; FORMATION BACKFILL AND PROSPECTIVE SHADOW REMAIN REQUIRED",
    }
    (OUT_DIR / "gc_break_v0_governed_diagnostic_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
