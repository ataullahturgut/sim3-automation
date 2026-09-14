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
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
if str(R4_SRC) not in sys.path:
    sys.path.insert(0, str(R4_SRC))
from gold_r4 import completed_weekly_closes, fast_state, slow_state, three_month_direction  # noqa: E402

PROTOCOL_PATH = ROOT / "gc_break_v0" / "gc_break_wp4d_2025_challenge_protocol_v1.json"
START_PREHISTORY = pd.Timestamp("2021-09-01")
FORMATION_START = pd.Timestamp("2022-01-01")
CHALLENGE_START = pd.Timestamp("2025-01-01")
CHALLENGE_END = pd.Timestamp("2025-12-31")
SIGMA_WINDOW = 20
K = 3.0
FINAL_STATUSES = {"VALID_EXACT_BAR", "PROVIDER_NO_BAR"}
MACRO_SERIES = [
    "MACRO_EVENT_V3_EMPLOYMENT_SCORE",
    "MACRO_EVENT_V3_INFLATION_SCORE",
    "MACRO_EVENT_V3_FOMC_SCORE",
]
STRONG_MACRO_STATES = {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}
M1_FEATURES = ["log1p_regime_sojourn_age", "fast_opposite_at_episode_start"]
M2_FEATURES = [
    "log1p_regime_sojourn_age",
    "fast_opposite_at_episode_start",
    "monthly_direction_conflict_at_episode_start",
    "bocpd_downside_adverse_context_at_episode_start",
    "macro_break_pressure_at_episode_start",
]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_protocol_and_freeze(model_freeze: Path) -> tuple[dict, dict]:
    p = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    f = json.loads(model_freeze.read_text(encoding="utf-8"))
    if p.get("status") != "FROZEN_BEFORE_2025_CHALLENGE_SCORING":
        raise RuntimeError("WP4D_CHALLENGE_PROTOCOL_NOT_FROZEN")
    if f.get("status") != "FROZEN_BEFORE_2025_CHALLENGE_SCORING":
        raise RuntimeError("WP4D_MODEL_FREEZE_NOT_FROZEN")
    if f.get("challenge_protocol") != p.get("protocol_id"):
        raise RuntimeError("WP4D_MODEL_PROTOCOL_MISMATCH")
    if f.get("formation_only") is not True or f.get("challenge_data_accessed") is not False:
        raise RuntimeError("WP4D_MODEL_FREEZE_CONTAMINATION_FAIL")
    if f.get("fit_support") != {"terminal_core_eligible_episodes": 35, "break_conversions": 13, "recoveries": 22}:
        raise RuntimeError("WP4D_MODEL_FREEZE_SUPPORT_FAIL")
    if abs(float(f["M0_EPISODE_EMPIRICAL_PRIOR"]["probability"]) - 0.375) > 1e-12:
        raise RuntimeError("WP4D_M0_FREEZE_FAIL")
    return p, f


def load_exact(path: Path, challenge: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    req = {"trade_date", "acquisition_status"}
    if not req <= set(raw.columns):
        raise RuntimeError(f"EXACT_SCHEMA_FAIL:{path}")
    bad = sorted(set(raw["acquisition_status"]) - FINAL_STATUSES)
    if bad:
        raise RuntimeError(f"UNRESOLVED_EXACT_STATUS:{path}:{bad[:5]}")
    if challenge:
        lineage = {
            "provider": "Twelve Data",
            "symbol": "XAU/USD",
            "interval": "1min",
            "timezone": "America/New_York",
            "accepted_source_time": "16:59:00",
            "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
            "prospective_claim": "False",
        }
        valid_rows = raw[raw["acquisition_status"].eq("VALID_EXACT_BAR")]
        for k, v in lineage.items():
            vals = set(valid_rows[k]) if k in raw.columns else set()
            if vals != {v}:
                raise RuntimeError(f"CHALLENGE_LINEAGE_FAIL:{k}:{vals}")
    valid = raw[raw["acquisition_status"].eq("VALID_EXACT_BAR")].copy()
    valid["date"] = pd.to_datetime(valid["trade_date"]).dt.normalize()
    valid["close"] = pd.to_numeric(valid["close"], errors="raise")
    if valid["date"].duplicated().any() or (valid["close"] <= 0).any() or not np.isfinite(valid["close"].to_numpy()).all():
        raise RuntimeError(f"INVALID_EXACT_ROWS:{path}")
    return valid[["date", "close"]].sort_values("date").reset_index(drop=True), raw


def label_history(d: pd.DataFrame) -> pd.DataFrame:
    x = d.sort_values("date").reset_index(drop=True).copy()
    x["log_ret"] = np.log(x["close"] / x["close"].shift(1))
    x["close_lag20"] = x["close"].shift(20)
    x["sigma20_lag1"] = x["log_ret"].shift(1).rolling(SIGMA_WINDOW, min_periods=SIGMA_WINDOW).std(ddof=1)
    regime = None
    extreme = None
    rows = []
    event_seq = 0
    for r in x.itertuples(index=False):
        before = regime
        is_break = False
        adverse = np.nan
        threshold = np.nan
        if regime is None:
            if pd.notna(r.close_lag20):
                mom = float(np.log(float(r.close) / float(r.close_lag20)))
                if mom > 0:
                    regime = "UP"
                elif mom < 0:
                    regime = "DOWN"
                if regime is not None:
                    extreme = float(r.close)
        else:
            sigma = float(r.sigma20_lag1) if pd.notna(r.sigma20_lag1) else np.nan
            adverse = float(np.log(float(extreme) / float(r.close))) if regime == "UP" else float(np.log(float(r.close) / float(extreme)))
            threshold = float(K * sigma) if np.isfinite(sigma) else np.nan
            if np.isfinite(threshold) and adverse >= threshold:
                is_break = True
                event_seq += 1
                regime = "DOWN" if regime == "UP" else "UP"
                extreme = float(r.close)
            elif regime == "UP":
                extreme = max(float(extreme), float(r.close))
            else:
                extreme = min(float(extreme), float(r.close))
        frac = adverse / threshold if np.isfinite(adverse) and np.isfinite(threshold) and threshold > 0 else np.nan
        rows.append({
            "date": pd.Timestamp(r.date), "close": float(r.close), "log_ret": r.log_ret,
            "sigma20_lag1": r.sigma20_lag1, "regime_pre": before, "regime_post": regime,
            "adverse_move": adverse, "threshold": threshold, "adverse_fraction": frac,
            "wp2_break_flag": bool(is_break), "event_seq_all": event_seq if is_break else np.nan,
        })
    return pd.DataFrame(rows)


def add_r4_roles(lab: pd.DataFrame) -> pd.DataFrame:
    month_levels = lab.set_index("date")["close"].resample("MS").last().dropna()
    rows = []
    for i, r in lab.iterrows():
        hist = lab.loc[:i, ["date", "close"]]
        day = pd.Timestamp(r["date"])
        target_start = day.to_period("M").start_time
        prior_levels = month_levels.loc[month_levels.index < target_start]
        completed_returns = prior_levels.pct_change().dropna().tolist()
        rows.append({
            "fast_state": fast_state(hist["close"].tolist()).value,
            "slow_state": slow_state(completed_weekly_closes(hist, day)).value,
            "monthly_direction_3m": three_month_direction(completed_returns).value,
        })
    out = lab.copy()
    role = pd.DataFrame(rows, index=out.index)
    for c in role.columns:
        out[c] = role[c]
    return out


def add_bocpd_context(p: pd.DataFrame) -> pd.DataFrame:
    bocpd = load_module(ROOT / "tools" / "bocpd_return_successor_v1.py", "gc_break_wp4d_bocpd")
    replay = bocpd.build_replay().rows.reset_index()
    replay["month"] = pd.to_datetime(replay["month"]).dt.to_period("M")
    lookup = replay.set_index("month")["state"].to_dict()
    current_month = p["date"].dt.to_period("M")
    prior_month = current_month - 1
    q = p.copy()
    q["bocpd_source_month"] = prior_month.astype(str)
    q["bocpd_state"] = prior_month.map(lookup)
    if q.loc[q["date"].between(CHALLENGE_START, CHALLENGE_END), "bocpd_state"].isna().any():
        missing = q.loc[q["date"].between(CHALLENGE_START, CHALLENGE_END) & q["bocpd_state"].isna(), "date"].dt.strftime("%Y-%m-%d").tolist()
        raise RuntimeError(f"WP4D_CHALLENGE_BOCPD_MISSING:{missing[:10]}")
    return q


def fetch_2025_macro_events() -> pd.DataFrame:
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    sql = """
        SELECT series_id, observation_ts, value, available_as_of, first_seen_at,
               retrieved_at, quality_status, metadata
        FROM observations
        WHERE series_id = ANY(%s)
          AND observation_ts >= '2025-01-01 00:00:00+00'
          AND observation_ts <  '2026-01-01 00:00:00+00'
        ORDER BY observation_ts, series_id
    """
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(sql, (MACRO_SERIES,))
            d = pd.DataFrame(cur.fetchall(), columns=[x.name for x in cur.description])
    if d.empty:
        raise RuntimeError("WP4D_2025_MACRO_EVENT_CONTEXT_MISSING")
    d["observation_ts"] = pd.to_datetime(d["observation_ts"], utc=True)
    d["score"] = pd.to_numeric(d["value"], errors="raise")
    d["state"] = d["metadata"].map(lambda x: (x or {}).get("state"))
    d["family"] = d["metadata"].map(lambda x: (x or {}).get("family"))
    strong = d[d["state"].isin(STRONG_MACRO_STATES)].copy()
    strong["release_date_ny"] = strong["observation_ts"].dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
    return strong.reset_index(drop=True)


def map_macro_to_challenge(p: pd.DataFrame, strong: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    q = p.copy()
    q["macro_strong_event_count"] = 0
    q["macro_adverse_event_count"] = 0
    challenge_idx = q.index[q["date"].between(CHALLENGE_START, CHALLENGE_END)].tolist()
    if not challenge_idx:
        raise RuntimeError("WP4D_NO_CHALLENGE_ORIGINS")
    challenge_dates = q.loc[challenge_idx, "date"].to_numpy(dtype="datetime64[ns]")
    mapped = []
    for _, ev in strong.iterrows():
        rd = pd.Timestamp(ev["release_date_ny"]).normalize()
        pos = int(np.searchsorted(challenge_dates, np.datetime64(rd), side="left"))
        if pos >= len(challenge_idx):
            continue
        idx = challenge_idx[pos]
        q.loc[idx, "macro_strong_event_count"] += 1
        q.loc[idx, "macro_adverse_event_count"] += int(ev["state"] == "GOLD_ADVERSE_MACRO_SHOCK")
        row = ev.to_dict()
        row["mapped_origin_date"] = pd.Timestamp(q.loc[idx, "date"])
        mapped.append(row)
    return q, pd.DataFrame(mapped)


def same(v: str, regime: str | None) -> bool:
    return (regime == "UP" and v == "ROBUST_UP") or (regime == "DOWN" and v == "ROBUST_DOWN")


def opposite(v: str, regime: str | None) -> bool:
    return (regime == "UP" and v == "ROBUST_DOWN") or (regime == "DOWN" and v == "ROBUST_UP")


def add_wp4d_features(p: pd.DataFrame) -> pd.DataFrame:
    q = p.copy().sort_values("date").reset_index(drop=True)
    valid = q["regime_pre"].isin(["UP", "DOWN"])
    q["fast_same"] = [same(str(v), r) for v, r in zip(q["fast_state"], q["regime_pre"])]
    q["fast_conflict"] = valid & ~q["fast_same"]
    q["fast_opposite"] = [opposite(str(v), r) for v, r in zip(q["fast_state"], q["regime_pre"])]
    q["path_half"] = valid & q["adverse_fraction"].ge(0.50)
    q["wp4d_episode_opener"] = q["path_half"] | q["fast_conflict"]

    ages = []
    age = 0
    prev_break = False
    for cur_break in q["wp2_break_flag"].astype(bool).tolist():
        age = 1 if prev_break or age == 0 else age + 1
        ages.append(age)
        prev_break = bool(cur_break)
    q["regime_sojourn_age"] = ages
    q["log1p_regime_sojourn_age"] = np.log1p(q["regime_sojourn_age"].astype(float))

    q["monthly_direction_conflict_wp4d"] = np.where(
        valid,
        ((q["regime_pre"] == "UP") & (q["monthly_direction_3m"] == "DOWN"))
        | ((q["regime_pre"] == "DOWN") & (q["monthly_direction_3m"] == "UP")),
        np.nan,
    )
    q["bocpd_downside_adverse_context_wp4d"] = np.where(
        q["bocpd_state"].notna(),
        ((q["regime_pre"] == "UP") & (q["bocpd_state"] == "ADVERSE_BREAK_CANDIDATE")).astype(float),
        np.nan,
    )
    strong = pd.to_numeric(q["macro_strong_event_count"], errors="coerce")
    adverse = pd.to_numeric(q["macro_adverse_event_count"], errors="coerce")
    supportive = strong - adverse
    q["macro_break_pressure_wp4d"] = np.where(
        q["regime_pre"] == "UP", (adverse > 0).astype(float),
        np.where(q["regime_pre"] == "DOWN", (supportive > 0).astype(float), np.nan),
    )
    return q


def episode_snapshot(q: pd.DataFrame, start_i: int, terminal_i: int, outcome: int, episode_id: int) -> dict:
    r = q.iloc[start_i]
    return {
        "episode_id": episode_id,
        "start_i": int(start_i), "terminal_i": int(terminal_i),
        "start_date": pd.Timestamp(r["date"]), "terminal_date": pd.Timestamp(q.iloc[terminal_i]["date"]),
        "outcome_break": int(outcome), "terminal_type": "BREAK" if outcome else "RECOVERY",
        "lead_observations_if_break": int(terminal_i - start_i) if outcome else np.nan,
        "lead_calendar_days_if_break": int((pd.Timestamp(q.iloc[terminal_i]["date"]) - pd.Timestamp(r["date"])).days) if outcome else np.nan,
        "regime_pre": r["regime_pre"],
        "log1p_regime_sojourn_age": float(r["log1p_regime_sojourn_age"]),
        "fast_opposite_at_episode_start": float(bool(r["fast_opposite"])),
        "monthly_direction_conflict_at_episode_start": float(r["monthly_direction_conflict_wp4d"]),
        "bocpd_downside_adverse_context_at_episode_start": float(r["bocpd_downside_adverse_context_wp4d"]),
        "macro_break_pressure_at_episode_start": float(r["macro_break_pressure_wp4d"]),
    }


def build_challenge_predictive_episodes(full: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    start_candidates = full.index[full["date"].between(CHALLENGE_START, CHALLENGE_END)].tolist()
    if not start_candidates:
        raise RuntimeError("WP4D_NO_2025_GOVERNED_ORIGIN")
    first = start_candidates[0]
    last = start_candidates[-1]
    carry_in = bool(first > 0 and full.loc[first - 1, "wp4d_episode_opener"])
    blocked_for_carry = carry_in
    active_start = None
    rows = []
    same_origin = 0
    right_censored = 0
    eid = 0

    for i in range(first, last + 1):
        r = full.loc[i]
        opener = bool(r["wp4d_episode_opener"])
        is_break = bool(r["wp2_break_flag"])
        if blocked_for_carry:
            if not opener:
                blocked_for_carry = False
            continue
        if active_start is None:
            if opener and is_break:
                same_origin += 1
                continue
            if opener:
                active_start = i
            continue
        if is_break:
            eid += 1
            rows.append(episode_snapshot(full, active_start, i, 1, eid))
            active_start = None
            continue
        if not opener:
            eid += 1
            rows.append(episode_snapshot(full, active_start, i, 0, eid))
            active_start = None
    if active_start is not None:
        right_censored = 1
    out = pd.DataFrame(rows)
    audit = {
        "left_censored_carry_in_excluded": int(carry_in),
        "same_origin_break_openers_excluded": int(same_origin),
        "right_censored_open_episode": int(right_censored),
        "terminal_predictive_episodes": int(len(out)),
        "break_conversions": int(out["outcome_break"].sum()) if len(out) else 0,
        "recoveries": int((1 - out["outcome_break"]).sum()) if len(out) else 0,
    }
    return out, audit


def frozen_probability(row: pd.Series, spec: dict) -> float:
    features = list(spec["features"])
    x = np.array([float(row[f]) for f in features], dtype=float)
    mean = np.array(spec["standardizer_mean"], dtype=float)
    scale = np.array(spec["standardizer_scale"], dtype=float)
    coef = np.array(spec["coef_standardized"], dtype=float)
    if not (len(x) == len(mean) == len(scale) == len(coef)) or np.any(scale <= 0):
        raise RuntimeError("WP4D_FROZEN_PARAMETER_SHAPE_FAIL")
    z = float(spec["intercept"]) + float(np.dot((x - mean) / scale, coef))
    if z >= 0:
        p = 1.0 / (1.0 + math.exp(-z))
    else:
        ez = math.exp(z)
        p = ez / (1.0 + ez)
    return float(np.clip(p, 1e-6, 1 - 1e-6))


def score_probability(episodes: pd.DataFrame, probs: np.ndarray) -> dict:
    if episodes.empty:
        return {"n": 0, "breaks": 0, "recoveries": 0, "brier_score": None, "log_loss": None,
                "average_precision_descriptive": None, "roc_auc_descriptive": None}
    y = episodes["outcome_break"].astype(int).to_numpy()
    p = np.clip(np.asarray(probs, dtype=float), 1e-6, 1 - 1e-6)
    both = len(set(y.tolist())) == 2
    return {
        "n": int(len(y)), "breaks": int(y.sum()), "recoveries": int(len(y) - y.sum()),
        "brier_score": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "average_precision_descriptive": float(average_precision_score(y, p)) if both else None,
        "roc_auc_descriptive": float(roc_auc_score(y, p)) if both else None,
    }


def signal_episodes(full: pd.DataFrame, signal_col: str) -> tuple[pd.DataFrame, dict]:
    idxs = full.index[full["date"].between(CHALLENGE_START, CHALLENGE_END)].tolist()
    first, last = idxs[0], idxs[-1]
    carry_in = bool(first > 0 and bool(full.loc[first - 1, signal_col]))
    blocked = carry_in
    active = None
    rows = []
    eid = 0
    for i in range(first, last + 1):
        flag = bool(full.loc[i, signal_col])
        br = bool(full.loc[i, "wp2_break_flag"])
        if blocked:
            if not flag:
                blocked = False
            continue
        if active is None:
            if flag:
                if br:
                    # contemporaneous opening is not a pre-break warning episode
                    continue
                active = i
            continue
        if br:
            eid += 1
            rows.append({
                "episode_id": eid, "start_date": full.loc[active, "date"], "end_date": full.loc[i, "date"],
                "converted": True, "break_date": full.loc[i, "date"],
                "lead_observations": int(i - active),
                "lead_calendar_days": int((pd.Timestamp(full.loc[i, "date"]) - pd.Timestamp(full.loc[active, "date"])).days),
            })
            active = None
            continue
        if not flag:
            eid += 1
            rows.append({
                "episode_id": eid, "start_date": full.loc[active, "date"], "end_date": full.loc[i, "date"],
                "converted": False, "break_date": pd.NaT, "lead_observations": np.nan, "lead_calendar_days": np.nan,
            })
            active = None
    right_censored = int(active is not None)
    return pd.DataFrame(rows), {"left_censored_carry_in_excluded": int(carry_in), "right_censored": right_censored}


def monitoring_metrics(ep: pd.DataFrame, challenge_break_dates: set[pd.Timestamp], n_origins: int) -> dict:
    n_events = len(challenge_break_dates)
    if ep.empty:
        return {
            "episodes": 0, "converted_episodes": 0, "false_episodes": 0,
            "prebreak_event_recall": 0.0 if n_events else None,
            "false_episodes_per_100_origins": 0.0,
            "median_lead_observations": None, "median_lead_calendar_days": None,
        }
    c = ep[ep["converted"].astype(bool)].copy()
    detected = set(pd.to_datetime(c["break_date"]).dropna())
    leads = c["lead_observations"].dropna()
    return {
        "episodes": int(len(ep)), "converted_episodes": int(len(c)), "false_episodes": int((~ep["converted"].astype(bool)).sum()),
        "prebreak_event_recall": float(len(detected) / n_events) if n_events else None,
        "false_episodes_per_100_origins": float((~ep["converted"].astype(bool)).sum() * 100.0 / n_origins),
        "median_lead_observations": float(leads.median()) if len(leads) else None,
        "median_lead_calendar_days": float(c["lead_calendar_days"].dropna().median()) if len(c) else None,
    }


def slow_confirmation_summary(full: pd.DataFrame) -> dict:
    qidx = full.index[full["date"].between(CHALLENGE_START, CHALLENGE_END)].tolist()
    breaks = [i for i in qidx if bool(full.loc[i, "wp2_break_flag"])]
    confirmed, obs_delays, cal_delays = 0, [], []
    for k, i in enumerate(breaks):
        new_regime = full.loc[i, "regime_post"]
        target = "ROBUST_UP" if new_regime == "UP" else "ROBUST_DOWN"
        stop = breaks[k + 1] if k + 1 < len(breaks) else qidx[-1] + 1
        found = None
        for j in range(i, stop):
            if str(full.loc[j, "slow_state"]) == target:
                found = j
                break
        if found is not None:
            confirmed += 1
            obs_delays.append(found - i)
            cal_delays.append((pd.Timestamp(full.loc[found, "date"]) - pd.Timestamp(full.loc[i, "date"])).days)
    return {
        "challenge_break_events": int(len(breaks)),
        "confirmed_before_next_break": int(confirmed),
        "confirmation_rate_before_next_break": float(confirmed / len(breaks)) if breaks else None,
        "median_delay_observations": float(np.median(obs_delays)) if obs_delays else None,
        "median_delay_calendar_days": float(np.median(cal_delays)) if cal_delays else None,
        "role": "POST_BREAK_CONFIRMATION_NEW_REGIME_ONLY",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--historical-exact", type=Path, required=True)
    ap.add_argument("--challenge-exact", type=Path, required=True)
    ap.add_argument("--model-freeze", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    protocol, freeze = load_protocol_and_freeze(args.model_freeze)
    hist, _ = load_exact(args.historical_exact, challenge=False)
    challenge, challenge_raw = load_exact(args.challenge_exact, challenge=True)
    if challenge.empty or challenge["date"].min() < CHALLENGE_START or challenge["date"].max() > CHALLENGE_END:
        raise RuntimeError("WP4D_CHALLENGE_DATE_RANGE_FAIL")
    if int((challenge_raw["acquisition_status"] == "VALID_EXACT_BAR").sum()) != 204:
        raise RuntimeError("WP4D_CHALLENGE_VALID_EXACT_COUNT_FAIL")
    if int((challenge_raw["acquisition_status"] == "PROVIDER_NO_BAR").sum()) != 161:
        raise RuntimeError("WP4D_CHALLENGE_NO_BAR_COUNT_FAIL")

    allx = pd.concat([hist[hist["date"] < CHALLENGE_START], challenge], ignore_index=True)
    allx = allx.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    allx = allx[allx["date"] >= START_PREHISTORY].reset_index(drop=True)
    panel = add_r4_roles(label_history(allx))
    panel = add_bocpd_context(panel)
    strong_macro = fetch_2025_macro_events()
    panel, mapped_macro = map_macro_to_challenge(panel, strong_macro)
    panel = add_wp4d_features(panel)

    # The formation episode-age convention begins at formation start and carries continuously through challenge.
    panel = panel[panel["date"] >= FORMATION_START].reset_index(drop=True)
    # Recompute sojourn age after the prehistory trim to exactly match formation convention.
    ages, age, prev_break = [], 0, False
    for cur_break in panel["wp2_break_flag"].astype(bool).tolist():
        age = 1 if prev_break or age == 0 else age + 1
        ages.append(age)
        prev_break = bool(cur_break)
    panel["regime_sojourn_age"] = ages
    panel["log1p_regime_sojourn_age"] = np.log1p(panel["regime_sojourn_age"].astype(float))

    episodes, ep_audit = build_challenge_predictive_episodes(panel)
    if not episodes.empty and episodes[M2_FEATURES].isna().any().any():
        raise RuntimeError("WP4D_CHALLENGE_CORE_FEATURE_MISSING")

    m0_p = float(freeze["M0_EPISODE_EMPIRICAL_PRIOR"]["probability"])
    if len(episodes):
        episodes["p_M0"] = m0_p
        episodes["p_M1"] = [frozen_probability(r, freeze["M1_TACTICAL_DURATION_RIDGE"]) for _, r in episodes.iterrows()]
        episodes["p_M2"] = [frozen_probability(r, freeze["M2_INTEGRATED_ROLE_CORE_RIDGE"]) for _, r in episodes.iterrows()]
    else:
        episodes["p_M0"] = []
        episodes["p_M1"] = []
        episodes["p_M2"] = []

    prob_metrics = {
        "M0_EPISODE_EMPIRICAL_PRIOR": score_probability(episodes, episodes["p_M0"].to_numpy() if len(episodes) else np.array([])),
        "M1_TACTICAL_DURATION_RIDGE": score_probability(episodes, episodes["p_M1"].to_numpy() if len(episodes) else np.array([])),
        "M2_INTEGRATED_ROLE_CORE_RIDGE": score_probability(episodes, episodes["p_M2"].to_numpy() if len(episodes) else np.array([])),
    }

    q = panel[panel["date"].between(CHALLENGE_START, CHALLENGE_END)].copy().reset_index(drop=True)
    # Monitoring episodes use the same challenge-only censoring philosophy, implemented against full history.
    fast_ep, fast_boundary = signal_episodes(panel, "fast_conflict")
    dual_ep, dual_boundary = signal_episodes(panel, "wp4d_episode_opener")
    break_dates = set(pd.to_datetime(q.loc[q["wp2_break_flag"].astype(bool), "date"]))
    fast_m = monitoring_metrics(fast_ep, break_dates, len(q))
    dual_m = monitoring_metrics(dual_ep, break_dates, len(q))
    slow_m = slow_confirmation_summary(panel)

    support_cfg = protocol["challenge_support_gate"]
    support_pass = (
        int(ep_audit["terminal_predictive_episodes"]) >= int(support_cfg["minimum_terminal_predictive_episodes"])
        and int(ep_audit["break_conversions"]) >= int(support_cfg["minimum_break_conversions"])
        and int(ep_audit["recoveries"]) >= int(support_cfg["minimum_recoveries"])
    )

    if support_pass:
        m0 = prob_metrics["M0_EPISODE_EMPIRICAL_PRIOR"]
        m1 = prob_metrics["M1_TACTICAL_DURATION_RIDGE"]
        m2 = prob_metrics["M2_INTEGRATED_ROLE_CORE_RIDGE"]
        tol = 1e-12
        vs_null = bool(m2["brier_score"] < m0["brier_score"] - tol and m2["log_loss"] < m0["log_loss"] - tol)
        no_worse_m1 = bool(m2["brier_score"] <= m1["brier_score"] + tol and m2["log_loss"] <= m1["log_loss"] + tol)
        strict_m1 = bool(m2["brier_score"] < m1["brier_score"] - tol or m2["log_loss"] < m1["log_loss"] - tol)
        vs_m1 = bool(no_worse_m1 and strict_m1)
        probability_pass = bool(vs_null and vs_m1)
    else:
        vs_null = vs_m1 = probability_pass = False

    ceiling = float(protocol["monitoring_gate"]["false_warning_episodes_per_100_max"])
    fast_lead = fast_m["median_lead_observations"] if fast_m["median_lead_observations"] is not None else -1.0
    dual_lead = dual_m["median_lead_observations"] if dual_m["median_lead_observations"] is not None else -1.0
    monitoring_parts = {
        "dual_recall_at_least_fast": bool(dual_m["prebreak_event_recall"] >= fast_m["prebreak_event_recall"]),
        "dual_lead_strictly_greater_fast": bool(dual_lead > fast_lead),
        "dual_false_burden_within_ceiling": bool(dual_m["false_episodes_per_100_origins"] <= ceiling),
    }
    monitoring_pass = bool(all(monitoring_parts.values()))

    if not support_pass:
        status = protocol["final_decision_rule"]["insufficient_status"]
    elif probability_pass and monitoring_pass:
        status = protocol["final_decision_rule"]["accept_status"]
    else:
        status = protocol["final_decision_rule"]["reject_status"]

    ledger = [
        {"engine": "CAUSAL_PATCH", "challenge_role": "STRATEGIC_CONTEXT_ONLY_EXCLUDED_FROM_M2_AFTER_E1_FORMATION_FAIL"},
        {"engine": "VW_MIDAS_MSVR_SUCCESSOR_V1", "challenge_role": "STRATEGIC_CONTEXT_ONLY_EXCLUDED_FROM_M2_AFTER_E1_FORMATION_FAIL"},
        {"engine": "MOMENTUM_3M", "challenge_role": "STRATEGIC_CONTEXT_ONLY_EXCLUDED_FROM_M2_AFTER_E1_FORMATION_FAIL"},
        {"engine": "RANDOM_WALK", "challenge_role": "STRATEGIC_BENCHMARK_ONLY_EXCLUDED_FROM_M2_AFTER_E1_FORMATION_FAIL"},
        {"engine": "MONTHLY_DIRECTION_3M", "challenge_role": "M2_STRATEGIC_PRIOR_CONFLICT_FEATURE"},
        {"engine": "FAST", "challenge_role": "TACTICAL_OPENER_AND_M2_FAST_OPPOSITE_FEATURE"},
        {"engine": "SLOW", "challenge_role": "POST_BREAK_CONFIRMATION_NEW_REGIME_ONLY"},
        {"engine": "MACRO_EVENT_SUCCESSOR_V2", "challenge_role": "M2_EVENT_CLOCK_BREAK_PRESSURE_FEATURE"},
        {"engine": "BOCPD_RETURN_SUCCESSOR_V1", "challenge_role": "M2_NATIVE_MONTHLY_REGIME_CONTEXT_FEATURE"},
        {"engine": "EMERGENCY_LEVEL", "challenge_role": "CONTEXT_ONLY_EXCLUDED_FROM_M2_AFTER_E2_FORMATION_FAIL"},
        {"engine": "EMERGENCY_REVERSAL", "challenge_role": "CONFIRMATION_CONTEXT_ONLY_EXCLUDED_FROM_M2_AFTER_E2_FORMATION_FAIL"},
        {"engine": "GVZ_RISK", "challenge_role": "NOT_TESTABLE_FORMATION_PIT_NOT_PROVEN"},
    ]

    summary = {
        "audit_id": "GC_BREAK_WP4D_2025_CHALLENGE_V1",
        "status": status,
        "challenge_protocol": protocol["protocol_id"],
        "model_freeze_id": freeze["freeze_id"],
        "challenge_origins": int(len(q)),
        "challenge_origin_min": q["date"].min().date().isoformat(),
        "challenge_origin_max": q["date"].max().date().isoformat(),
        "challenge_primary_break_events": int(len(break_dates)),
        "predictive_episode_audit": ep_audit,
        "support_gate_pass": bool(support_pass),
        "probability_metrics": prob_metrics,
        "probability_gate": {
            "passed": bool(probability_pass),
            "M2_strictly_improves_M0_brier_and_logloss": bool(vs_null),
            "M2_no_worse_M1_both_and_strictly_improves_at_least_one": bool(vs_m1),
        },
        "monitoring": {
            "FAST_CONFLICT": fast_m,
            "INTEGRATED_DUAL_LANE_PATH_HALF_OR_FAST_CONFLICT": dual_m,
            "fast_boundary_audit": fast_boundary,
            "dual_boundary_audit": dual_boundary,
            "false_warning_ceiling": ceiling,
            "gate": {"passed": bool(monitoring_pass), **monitoring_parts},
            "claim_separation": "PATH_HALF is structural health/anatomy monitoring, not an independent probability predictor.",
        },
        "slow_confirmation_lane": slow_m,
        "macro_context": {
            "strong_2025_macro_events": int(len(strong_macro)),
            "mapped_strong_events": int(len(mapped_macro)),
            "source_series": MACRO_SERIES,
            "database_access": "READ_ONLY_TRANSACTION",
        },
        "governed_identity_ledger": ledger,
        "all_12_governed_identities_accounted_for": len(ledger) == 12,
        "H1_probability_modifier_used": False,
        "emergency_probability_modifier_used": False,
        "GVZ_probability_modifier_used": False,
        "path_half_or_adverse_fraction_probability_feature": False,
        "challenge_refit": False,
        "hyperparameter_search": False,
        "threshold_search": False,
        "post_challenge_tuning": False,
        "stress_2026_accessed": False,
        "database_write": "NONE",
        "production_authority": False,
        "prospective_claim": False,
        "decision_interpretation": protocol["final_decision_rule"],
    }

    q.to_csv(args.output_dir / "gc_break_wp4d_2025_challenge_panel_v1.csv", index=False)
    episodes.to_csv(args.output_dir / "gc_break_wp4d_2025_predictive_episodes_v1.csv", index=False)
    fast_ep.to_csv(args.output_dir / "gc_break_wp4d_2025_fast_conflict_monitoring_episodes_v1.csv", index=False)
    dual_ep.to_csv(args.output_dir / "gc_break_wp4d_2025_dual_lane_monitoring_episodes_v1.csv", index=False)
    mapped_macro.to_csv(args.output_dir / "gc_break_wp4d_2025_mapped_strong_macro_events_v1.csv", index=False)
    (args.output_dir / "gc_break_wp4d_2025_engine_role_ledger_v1.json").write_text(json.dumps(ledger, indent=2, default=str) + "\n", encoding="utf-8")
    (args.output_dir / "gc_break_wp4d_2025_challenge_summary_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
