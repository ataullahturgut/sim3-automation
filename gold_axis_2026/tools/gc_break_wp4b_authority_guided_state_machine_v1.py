from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "gc_break_v0" / "gc_break_wp4b_authority_guided_state_machine_prereg_v1.json").exists():
            return parent
    raise RuntimeError("PROJECT_ROOT_NOT_FOUND")


def load_contract() -> dict:
    c = json.loads((project_root() / "gc_break_v0" / "gc_break_wp4b_authority_guided_state_machine_prereg_v1.json").read_text(encoding="utf-8"))
    if c.get("status") != "FROZEN_BEFORE_FORMATION_SCORING":
        raise RuntimeError("WP4B_CONTRACT_NOT_FROZEN")
    g = c["governance"]
    keys = ["no_random_split", "no_post_score_tuning", "no_threshold_search", "no_hyperparameter_search", "no_2025_challenge_access", "no_2026_stress_access", "no_database_writes"]
    if not all(g.get(k) is True for k in keys):
        raise RuntimeError("WP4B_GOVERNANCE_GUARD_FAIL")
    return c


def same(state: str, regime: str) -> bool:
    return (regime == "UP" and state == "ROBUST_UP") or (regime == "DOWN" and state == "ROBUST_DOWN")


def opposite(state: str, regime: str) -> bool:
    return (regime == "UP" and state == "ROBUST_DOWN") or (regime == "DOWN" and state == "ROBUST_UP")


def trajectory(panel: pd.DataFrame, use_cusum: bool, h: float, model_id: str) -> pd.DataFrame:
    p = panel.sort_values("date").reset_index(drop=True).copy()
    logp = np.log(p["close"].astype(float))
    ret = logp.diff()
    sigma = ret.shift(1).rolling(20, min_periods=20).std(ddof=1)
    if p["fast_state"].isna().any():
        raise RuntimeError("FAST_MISSING_IN_PRIMARY_FORMATION")
    regime = str(p.loc[0, "regime_pre"])
    if regime not in {"UP", "DOWN"}:
        raise RuntimeError("INITIAL_REGIME_NOT_AVAILABLE")
    state, g = "STABLE", 0.0
    rows = []
    for i, r in p.iterrows():
        sig = float(sigma.iloc[i]) if pd.notna(sigma.iloc[i]) else math.nan
        rr = float(ret.iloc[i]) if pd.notna(ret.iloc[i]) else math.nan
        z = rr / sig if math.isfinite(rr) and math.isfinite(sig) and sig > 0 else math.nan
        adverse_z = (-z if regime == "UP" else z) if math.isfinite(z) else math.nan
        if use_cusum and math.isfinite(adverse_z):
            g = max(0.0, g + adverse_z - 0.5)
        elif not use_cusum:
            g = 0.0

        fs = str(r["fast_state"])
        ss = str(r["slow_state"]) if pd.notna(r["slow_state"]) else "MISSING"
        f_same, f_opp = same(fs, regime), opposite(fs, regime)
        f_conflict = not f_same
        s_same = same(ss, regime)
        c_alert = bool(use_cusum and g >= h)
        weak = bool(f_conflict or c_alert)
        strong = bool(f_opp or (f_conflict and c_alert))
        before_state, before_regime = state, regime
        break_now = bool(r["wp2_break_flag"])
        reason = "HOLD"

        if break_now:
            state = "CONFIRMED_BREAK"
            regime = "DOWN" if regime == "UP" else "UP"
            g = 0.0
            reason = "FROZEN_CURRENT_ORIGIN_BREAK"
        elif state == "CONFIRMED_BREAK":
            if s_same:
                state, reason = "NEW_REGIME", "SLOW_CONFIRMS_NEW_REGIME"
            else:
                reason = "AWAIT_SLOW_CONFIRMATION"
        elif state == "NEW_REGIME":
            if s_same and f_same:
                state, reason = "STABLE", "FAST_AND_SLOW_SUPPORT_NEW_REGIME"
            else:
                reason = "NEW_REGIME_SETTLING"
        elif state == "STABLE":
            if weak:
                state, reason = "WEAKENING", "FAST_CONFLICT_OR_CUSUM_ALERT"
            else:
                reason = "STABLE_EVIDENCE"
        elif state == "WEAKENING":
            if strong:
                state, reason = "BREAK_ALERT", "FAST_OPPOSITE_OR_FAST_PLUS_CUSUM"
            elif not weak:
                state, reason = "STABLE", "RECOVERY_TO_STABLE"
            else:
                reason = "WEAKENING_PERSISTS"
        elif state == "BREAK_ALERT":
            if strong:
                reason = "BREAK_ALERT_PERSISTS"
            elif weak:
                state, reason = "WEAKENING", "DEESCALATE_TO_WEAKENING"
            else:
                state, reason = "STABLE", "RECOVERY_TO_STABLE"
        else:
            raise RuntimeError(f"UNKNOWN_STATE:{state}")

        rows.append({
            "model_id": model_id, "date": r["date"], "close": float(r["close"]), "wp2_break_flag": break_now,
            "event_id": r["event_id"], "regime_before_processing": before_regime, "regime_after_processing": regime,
            "state_before": before_state, "state_after": state, "transition_reason": reason, "fast_state": fs,
            "slow_state": ss, "fast_same": f_same, "fast_conflict": f_conflict, "fast_opposite": f_opp,
            "slow_same_current_regime_before_break": s_same, "log_return": rr, "lagged_sigma20": sig,
            "adverse_z": adverse_z, "cusum_g_after_update": g, "cusum_h": h if use_cusum else np.nan,
            "cusum_alert": c_alert,
        })
    return pd.DataFrame(rows)


def episodes(tr: pd.DataFrame, states: set[str], label: str) -> pd.DataFrame:
    on = tr["state_after"].isin(states).to_numpy()
    out, start = [], None
    for i, flag in enumerate(on):
        if flag and start is None:
            start = i
        if start is None:
            continue
        next_break = i + 1 < len(tr) and bool(tr.loc[i + 1, "wp2_break_flag"])
        end_now = i == len(tr) - 1 or not flag or next_break or (flag and i + 1 < len(tr) and not on[i + 1])
        if not end_now:
            continue
        end = i if flag else i - 1
        if end >= start:
            converted = bool(end + 1 < len(tr) and tr.loc[end + 1, "wp2_break_flag"])
            bd = pd.Timestamp(tr.loc[end + 1, "date"]) if converted else pd.NaT
            out.append({
                "episode_type": label, "episode_id": len(out) + 1, "start_i": start, "end_i": end,
                "start_date": pd.Timestamp(tr.loc[start, "date"]), "end_date": pd.Timestamp(tr.loc[end, "date"]),
                "converted": converted, "break_date": bd,
                "lead_observations": end + 1 - start if converted else np.nan,
                "lead_calendar_days": (bd - pd.Timestamp(tr.loc[start, "date"])).days if converted else np.nan,
                "recovered_to_stable": bool((not converted) and end + 1 < len(tr) and tr.loc[end + 1, "state_after"] == "STABLE"),
            })
        start = None
    return pd.DataFrame(out)


def episode_metrics(ep: pd.DataFrame, n_events: int, n_origins: int) -> dict:
    if ep.empty:
        return {"episodes": 0, "converted_episodes": 0, "false_episodes": 0, "episode_conversion_rate": None,
                "prebreak_event_recall": 0.0, "false_episodes_per_100_origins": 0.0,
                "median_lead_observations": None, "median_lead_calendar_days": None,
                "recovery_episode_count": 0, "recovery_rate_before_break": None}
    conv, false = ep[ep["converted"]], ep[~ep["converted"]]
    leads_o, leads_c = conv["lead_observations"].dropna(), conv["lead_calendar_days"].dropna()
    recovered = false["recovered_to_stable"].fillna(False).astype(bool)
    return {
        "episodes": int(len(ep)), "converted_episodes": int(len(conv)), "false_episodes": int(len(false)),
        "episode_conversion_rate": float(len(conv) / len(ep)),
        "prebreak_event_recall": float(pd.to_datetime(conv["break_date"]).nunique() / n_events),
        "false_episodes_per_100_origins": float(len(false) * 100.0 / n_origins),
        "median_lead_observations": float(leads_o.median()) if len(leads_o) else None,
        "median_lead_calendar_days": float(leads_c.median()) if len(leads_c) else None,
        "recovery_episode_count": int(recovered.sum()),
        "recovery_rate_before_break": float(recovered.mean()) if len(false) else None,
    }


def confirmation(tr: pd.DataFrame, events: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    pos = {pd.Timestamp(d): i for i, d in enumerate(pd.to_datetime(tr["date"]))}
    rows = []
    for j, ev in events.reset_index(drop=True).iterrows():
        b = pd.Timestamp(ev["break_date"]); bi = pos[b]
        next_i = pos[pd.Timestamp(events.iloc[j + 1]["break_date"])] if j + 1 < len(events) else len(tr)
        found = next((i for i in range(bi + 1, next_i) if tr.loc[i, "state_after"] == "NEW_REGIME"), None)
        rows.append({"event_id": str(ev["event_id"]), "break_date": b, "confirmed_before_next_break": found is not None,
                     "confirmation_date": pd.Timestamp(tr.loc[found, "date"]) if found is not None else pd.NaT,
                     "delay_observations": found - bi if found is not None else np.nan,
                     "delay_calendar_days": (pd.Timestamp(tr.loc[found, "date"]) - b).days if found is not None else np.nan})
    c = pd.DataFrame(rows); v = c[c["confirmed_before_next_break"]]
    m = {"events": int(len(c)), "confirmed_before_next_break": int(len(v)),
         "confirmation_rate_before_next_break": float(len(v) / len(c)),
         "median_confirmation_delay_observations": float(v["delay_observations"].median()) if len(v) else None,
         "median_confirmation_delay_calendar_days": float(v["delay_calendar_days"].median()) if len(v) else None}
    return m, c


def evaluate(tr: pd.DataFrame, events: pd.DataFrame) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    w = episodes(tr, {"WEAKENING", "BREAK_ALERT"}, "WEAKENING_OR_HIGHER")
    a = episodes(tr, {"BREAK_ALERT"}, "BREAK_ALERT")
    cm, c = confirmation(tr, events)
    wm, am = episode_metrics(w, len(events), len(tr)), episode_metrics(a, len(events), len(tr))
    false_w = w[~w["converted"]] if not w.empty else w
    flips = 0
    for _, ep in false_w.iterrows():
        seq = tr.loc[max(0, int(ep.start_i)-1):min(len(tr)-1, int(ep.end_i)+1), "state_after"].tolist()
        flips += sum(x != y for x, y in zip(seq, seq[1:]))
    d = {"time_fraction_in_warning_states": float(tr["state_after"].isin(["WEAKENING", "BREAK_ALERT"]).mean()),
         "spurious_state_flip_count_descriptive": int(flips), "state_counts": tr["state_after"].value_counts().to_dict(),
         "transition_reason_counts": tr["transition_reason"].value_counts().to_dict()}
    return {"model_id": tr["model_id"].iloc[0], "origins": int(len(tr)), "events": int(len(events)),
            "weakening": wm, "break_alert": am, "confirmation": cm, "descriptives": d}, w, a, c


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", type=Path, required=True); ap.add_argument("--events", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True)
    contract = load_contract()
    p = pd.read_csv(a.panel, parse_dates=["date"])
    e = pd.read_csv(a.events, parse_dates=["trade_date"]).rename(columns={"trade_date": "break_date"})
    if len(p) != 351 or len(e) != 21 or p["date"].duplicated().any():
        raise RuntimeError(f"FROZEN_SUPPORT_FAIL:{len(p)}:{len(e)}")
    if p["prospective_claim"].astype(bool).any():
        raise RuntimeError("PROSPECTIVE_CONTAMINATION")

    specs = [("WP4B_ROLE_FSM_NO_CUSUM", False, 5.0), ("WP4B_RP_CUSUM_FSM_H5", True, 5.0),
             ("WP4B_RP_CUSUM_FSM_H4_SENSITIVITY", True, 4.0)]
    summaries, trs, wes, aes, confs = {}, [], [], [], []
    for mid, use, h in specs:
        tr = trajectory(p, use, h, mid); s, we, ae, cf = evaluate(tr, e); summaries[mid] = s; trs.append(tr)
        if not we.empty: we = we.copy(); we["model_id"] = mid; wes.append(we)
        if not ae.empty: ae = ae.copy(); ae["model_id"] = mid; aes.append(ae)
        cf = cf.copy(); cf["model_id"] = mid; confs.append(cf)

    q = summaries["WP4B_RP_CUSUM_FSM_H5"]["weakening"]
    base_recall, base_lead, ceiling = 1.0/3.0, 0.0, 5.698005698005698
    positive = q["prebreak_event_recall"] >= base_recall and q["median_lead_observations"] is not None and q["median_lead_observations"] >= base_lead and q["false_episodes_per_100_origins"] <= ceiling and (q["prebreak_event_recall"] > base_recall or q["median_lead_observations"] > base_lead)
    stronger = q["prebreak_event_recall"] >= 0.50 and q["median_lead_observations"] is not None and q["median_lead_observations"] >= 1.0 and q["false_episodes_per_100_origins"] <= ceiling
    status = "FORMATION_STRONGER_SIGNAL" if stronger else ("FORMATION_POSITIVE_SIGNAL" if positive else "NO_INCREMENTAL_VALUE")
    out = {"audit_id": "GC_BREAK_WP4B_AUTHORITY_GUIDED_STATE_MACHINE_V1", "contract_id": contract["contract_id"],
           "contract_status": contract["status"], "status": status, "formation_origins": len(p), "formation_break_events": len(e),
           "models": summaries, "primary_decision": {"model_id": "WP4B_RP_CUSUM_FSM_H5", "positive_signal": bool(positive),
           "stronger_signal": bool(stronger), "reference_fast_conflict_prebreak_recall": base_recall,
           "reference_fast_conflict_median_lead_observations": base_lead, "false_warning_burden_ceiling_per_100": ceiling},
           "sensitivity_h4_can_rescue_primary": False, "challenge_2025_accessed": False, "stress_2026_accessed": False,
           "database_write": "NONE", "production_authority": False, "prospective_claim": False, "post_score_tuning_performed": False}
    pd.concat(trs, ignore_index=True).to_csv(a.output_dir / "gc_break_wp4b_state_trajectories_v1.csv", index=False)
    pd.concat(wes, ignore_index=True).to_csv(a.output_dir / "gc_break_wp4b_warning_episodes_v1.csv", index=False)
    pd.concat(aes, ignore_index=True).to_csv(a.output_dir / "gc_break_wp4b_break_alert_episodes_v1.csv", index=False)
    pd.concat(confs, ignore_index=True).to_csv(a.output_dir / "gc_break_wp4b_confirmation_delays_v1.csv", index=False)
    (a.output_dir / "gc_break_wp4b_authority_guided_state_machine_v1_summary.json").write_text(json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
