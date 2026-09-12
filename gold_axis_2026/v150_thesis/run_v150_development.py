from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import psycopg
from scipy.stats import binomtest
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v150_thesis/contracts/v150_role_hierarchy_development_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v150_thesis"
SEED = 20260912

PIT_SERIES = {
    "dgs10": "DGS10_ALFRED_PIT_ME",
    "dff": "DFF_ALFRED_PIT_ME",
    "fx": "DEXCHUS_ALFRED_PIT_ME",
}
EQUITY_SERIES = {
    "nasdaq": "NASDAQ100_FRED",
    "sp500": "SP500_FRED",
    "djia": "DJIA_FRED",
}
PRECIOUS_SERIES = {
    "xag": "XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "xpt": "XPT_STAKTRAKR_RESEARCH_DAILY_R1",
    "xpd": "XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}
MACRO_SERIES = [
    "MACRO_EVENT_V3_EMPLOYMENT_SCORE",
    "MACRO_EVENT_V3_INFLATION_SCORE",
    "MACRO_EVENT_V3_FOMC_SCORE",
]

G0 = [
    "gold_ret_lag1", "gold_ret_lag2", "gold_ret_lag3",
    "gold_mom3", "gold_mom5", "gold_mom10", "gold_mom20",
    "gold_rv5", "gold_rv10", "gold_rv20",
]
G1 = ["fast_role", "slow_role", "monthly_direction_3m"]
G2 = ["dgs10_level", "dgs10_delta", "dff_level", "dff_delta", "fx_level", "fx_logdiff"]
G3 = ["nasdaq_ret", "sp500_ret", "djia_ret"]
G4 = ["xag_ret", "xpt_ret", "xpd_ret"]
FEATURE_SETS = {
    "G0": G0,
    "G0_G1": G0 + G1,
    "G0_G1_G2": G0 + G1 + G2,
    "G0_G1_G3": G0 + G1 + G3,
    "G0_G1_G4": G0 + G1 + G4,
    "G0_G1_G2_G3_G4": G0 + G1 + G2 + G3 + G4,
}
MODELS = [
    ("LOGIT_C01", "logit", 0.1),
    ("LOGIT_C1", "logit", 1.0),
    ("HGB_D2", "hgb", 2),
]


def q(conn, sql: str, params=None) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)


def frame_hash(d: pd.DataFrame) -> str:
    return hashlib.sha256(
        d.to_csv(index=False, float_format="%.12g", lineterminator="\n").encode()
    ).hexdigest()


def load_ny17(conn) -> pd.DataFrame:
    d = q(conn, """
        SELECT observation_ts,
               (observation_ts AT TIME ZONE 'America/New_York')::date AS date,
               close
        FROM xau_intraday_research_cache_1m
        WHERE (observation_ts AT TIME ZONE 'America/New_York')::time = '16:59:00'
          AND (observation_ts AT TIME ZONE 'America/New_York')::date >= DATE '2023-01-01'
          AND (observation_ts AT TIME ZONE 'America/New_York')::date <= DATE '2024-12-31'
        ORDER BY observation_ts
    """)
    if d.empty:
        raise RuntimeError("BLOCKED_NY17_DEVELOPMENT_EMPTY")
    d["date"] = pd.to_datetime(d["date"])
    d["observation_ts"] = pd.to_datetime(d["observation_ts"], utc=True)
    if d["date"].duplicated().any():
        raise RuntimeError("DUPLICATE_EXACT_NY17_DATE")
    if d["date"].max() >= pd.Timestamp("2025-01-01"):
        raise RuntimeError("OUTER_LOCK_VIOLATION_NY17")
    return d.reset_index(drop=True)


def add_gold_features(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    logp = np.log(d["close"].astype(float))
    r = logp.diff()
    d["gold_ret_lag1"] = r
    d["gold_ret_lag2"] = r.shift(1)
    d["gold_ret_lag3"] = r.shift(2)
    for k in [3, 5, 10, 20]:
        d[f"gold_mom{k}"] = logp - logp.shift(k)
    for k in [5, 10, 20]:
        d[f"gold_rv{k}"] = r.rolling(k, min_periods=k).std(ddof=0)
    return d


def role_fast(d: pd.DataFrame) -> pd.Series:
    s = d["close"].astype(float)
    ma = s.rolling(20, min_periods=20).mean()
    raw = np.sign(s - ma)
    out = pd.Series(0.0, index=d.index)
    out[(raw == 1) & (raw.shift(1) == 1)] = 1.0
    out[(raw == -1) & (raw.shift(1) == -1)] = -1.0
    out[ma.isna() | ma.shift(1).isna()] = np.nan
    return out


def _slow_at(d: pd.DataFrame, i: int) -> float:
    x = d.loc[:i, ["date", "close"]].copy().sort_values("date").set_index("date")
    asof = pd.Timestamp(d.loc[i, "date"])
    weekly = x["close"].resample("W-FRI").last().dropna()
    if asof.weekday() < 4:
        current_week_end = asof.to_period("W-FRI").end_time.normalize()
        weekly = weekly.loc[weekly.index < current_week_end]
    if len(weekly) < 5:
        return np.nan
    ma = weekly.rolling(4, min_periods=4).mean()
    cur = np.sign(float(weekly.iloc[-1]) - float(ma.iloc[-1]))
    prev = np.sign(float(weekly.iloc[-2]) - float(ma.iloc[-2]))
    if cur == prev == 1:
        return 1.0
    if cur == prev == -1:
        return -1.0
    return 0.0


def _monthly_direction_at(d: pd.DataFrame, i: int) -> float:
    asof = pd.Timestamp(d.loc[i, "date"])
    x = d.loc[:i, ["date", "close"]].copy().sort_values("date").set_index("date")
    completed = x.loc[x.index.to_period("M") < asof.to_period("M"), "close"]
    if completed.empty:
        return np.nan
    monthly = completed.resample("ME").last().dropna()
    mr = np.log(monthly).diff().dropna()
    if len(mr) < 3:
        return np.nan
    m3 = float(mr.iloc[-3:].mean())
    return float(np.sign(m3))


def add_role_context(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["fast_role"] = role_fast(d)
    d["slow_role"] = [_slow_at(d, i) for i in range(len(d))]
    d["monthly_direction_3m"] = [_monthly_direction_at(d, i) for i in range(len(d))]
    return d


def load_series(conn, ids: Iterable[str]) -> pd.DataFrame:
    ids = list(ids)
    d = q(conn, """
        SELECT series_id, observation_ts, value, available_as_of, retrieved_at
        FROM observations
        WHERE series_id = ANY(%s)
          AND observation_ts < '2025-01-01 00:00:00+00'
        ORDER BY series_id, observation_ts, retrieved_at
    """, (ids,))
    if d.empty:
        return d
    d["observation_ts"] = pd.to_datetime(d["observation_ts"], utc=True)
    d["available_as_of"] = pd.to_datetime(d["available_as_of"], utc=True)
    d["retrieved_at"] = pd.to_datetime(d["retrieved_at"], utc=True)
    return d


def merge_pit_monthly(d: pd.DataFrame, obs: pd.DataFrame) -> pd.DataFrame:
    d = d.copy().sort_values("observation_ts")
    for name, sid in PIT_SERIES.items():
        z = obs[obs["series_id"] == sid].copy()
        if z.empty:
            d[f"{name}_level"] = np.nan
            d[f"{name}_delta" if name != "fx" else f"{name}_logdiff"] = np.nan
            continue
        z = z.sort_values(["available_as_of", "retrieved_at"]).drop_duplicates("available_as_of", keep="last")
        z = z[["available_as_of", "value"]].rename(columns={"available_as_of": "avail", "value": f"{name}_level"})
        if name == "fx":
            z[f"{name}_logdiff"] = np.log(z[f"{name}_level"].astype(float)).diff()
        else:
            z[f"{name}_delta"] = z[f"{name}_level"].astype(float).diff()
        d = pd.merge_asof(d.sort_values("observation_ts"), z.sort_values("avail"), left_on="observation_ts", right_on="avail", direction="backward", allow_exact_matches=True)
        if (d["avail"].notna() & (d["avail"] > d["observation_ts"])).any():
            raise RuntimeError(f"PIT_FUTURE_JOIN_{name}")
        d = d.drop(columns=["avail"])
    return d


def merge_lagged_daily(d: pd.DataFrame, obs: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    d = d.copy().sort_values("date")
    for name, sid in mapping.items():
        z = obs[obs["series_id"] == sid].copy()
        if z.empty:
            d[f"{name}_ret"] = np.nan
            continue
        z["source_date"] = z["observation_ts"].dt.tz_convert("UTC").dt.tz_localize(None).dt.normalize()
        z = z.sort_values(["source_date", "retrieved_at"]).drop_duplicates("source_date", keep="last")
        z = z[["source_date", "value"]].sort_values("source_date")
        z[f"{name}_ret"] = np.log(z["value"].astype(float)).diff()
        z = z[["source_date", f"{name}_ret"]]
        d = pd.merge_asof(d.sort_values("date"), z.sort_values("source_date"), left_on="date", right_on="source_date", direction="backward", allow_exact_matches=False)
        if (d["source_date"].notna() & (d["source_date"] >= d["date"])).any():
            raise RuntimeError(f"LAG_VIOLATION_{name}")
        d = d.drop(columns=["source_date"])
    return d


def build_panel(conn) -> pd.DataFrame:
    d = add_role_context(add_gold_features(load_ny17(conn)))
    pit = load_series(conn, PIT_SERIES.values())
    d = merge_pit_monthly(d, pit)
    daily = load_series(conn, list(EQUITY_SERIES.values()) + list(PRECIOUS_SERIES.values()))
    d = merge_lagged_daily(d, daily, EQUITY_SERIES)
    d = merge_lagged_daily(d, daily, PRECIOUS_SERIES)
    if d["date"].max() >= pd.Timestamp("2025-01-01"):
        raise RuntimeError("OUTER_LOCK_VIOLATION_PANEL")
    return d.reset_index(drop=True)


def estimator(kind: str, p: float):
    if kind == "logit":
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            StandardScaler(),
            LogisticRegression(C=p, max_iter=2000, random_state=SEED),
        )
    return make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
        HistGradientBoostingClassifier(max_depth=int(p), max_iter=100, learning_rate=0.05, l2_regularization=1.0, random_state=SEED),
    )


def targets(d: pd.DataFrame, h: int):
    ret = np.log(d["close"].shift(-h) / d["close"])
    y = (ret > 0).astype(float)
    y.iloc[-h:] = np.nan
    return y, ret


def sequential_predictions(d: pd.DataFrame, h: int, cols: list[str], model_id: str, kind: str, p: float, min_train: int) -> pd.DataFrame:
    y, ret = targets(d, h)
    rows = []
    for t in range(min_train, len(d) - h):
        train = [j for j in range(t) if j + h <= t and pd.notna(y.iloc[j])]
        if len(train) < min_train:
            continue
        yy = y.iloc[train].astype(int)
        if yy.nunique() < 2:
            continue
        m = estimator(kind, p)
        m.fit(d.loc[train, cols], yy)
        prob = float(m.predict_proba(d.loc[[t], cols])[0, 1])
        matured = [j for j in range(t) if j + h <= t and pd.notna(y.iloc[j])]
        freq = (float(y.iloc[matured].sum()) + 0.5) / (len(matured) + 1.0)
        rows.append({
            "origin_index": t,
            "origin_date": d.loc[t, "date"],
            "target_date": d.loc[t + h, "date"],
            "horizon": h,
            "feature_set": None,
            "model": model_id,
            "y": int(y.iloc[t]),
            "return": float(ret.iloc[t]),
            "p": prob,
            "p50": 0.5,
            "pfreq": freq,
            "train_n": len(train),
        })
    return pd.DataFrame(rows)


def metrics(f: pd.DataFrame, pcol: str = "p") -> dict:
    if f.empty:
        return {"n": 0, "status": "BLOCKED_EMPTY"}
    y = f["y"].astype(int).to_numpy()
    p = np.clip(f[pcol].astype(float).to_numpy(), 1e-8, 1 - 1e-8)
    pred = p >= 0.5
    return {
        "n": int(len(f)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "up_rate": float(np.mean(y)),
        "mean_p": float(np.mean(p)),
    }


def select_threshold(f: pd.DataFrame, thresholds: list[float]) -> dict:
    best = None
    for th in thresholds:
        keep = (f["p"] - 0.5).abs() >= th
        g = f.loc[keep]
        n = len(g)
        coverage = n / len(f) if len(f) else 0.0
        if n < 20 or coverage < 0.35:
            continue
        acc = float(np.mean((g["p"] >= 0.5).astype(int).to_numpy() == g["y"].astype(int).to_numpy()))
        cand = (acc, coverage, -th, th, n)
        if best is None or cand[:3] > best[:3]:
            best = cand
    if best is None:
        return {"threshold": 0.0, "selection_status": "FALLBACK_ZERO"}
    return {"threshold": float(best[3]), "selection_status": "SELECTED_ON_PRELOCK", "selection_accuracy": float(best[0]), "selection_coverage": float(best[1]), "selection_n": int(best[4])}


def selective_metrics(f: pd.DataFrame, threshold: float) -> dict:
    if f.empty:
        return {"accepted_n": 0, "coverage": 0.0, "accuracy": None}
    keep = (f["p"] - 0.5).abs() >= threshold
    g = f.loc[keep]
    if g.empty:
        return {"accepted_n": 0, "coverage": 0.0, "accuracy": None}
    hit = (g["p"] >= 0.5).astype(int).to_numpy() == g["y"].astype(int).to_numpy()
    return {"accepted_n": int(len(g)), "coverage": float(len(g) / len(f)), "accuracy": float(np.mean(hit))}


def run_general(d: pd.DataFrame, contract: dict) -> tuple[dict, pd.DataFrame]:
    selection_end = pd.Timestamp(contract["general_direction"]["selection_window_end"])
    lock_start = pd.Timestamp(contract["general_direction"]["development_lock_window"][0])
    lock_end = pd.Timestamp(contract["general_direction"]["development_lock_window"][1])
    min_train = int(contract["general_direction"]["minimum_training_origins"])
    thresholds = list(contract["general_direction"]["selective_prediction"]["threshold_candidates_abs_p_minus_half"])
    all_preds = []
    summary = {}
    for h in [1, 3]:
        candidates = []
        for fs, cols in FEATURE_SETS.items():
            for mid, kind, p in MODELS:
                f = sequential_predictions(d, h, cols, mid, kind, p, min_train)
                if f.empty:
                    continue
                f["feature_set"] = fs
                all_preds.append(f)
                sel = f[f["origin_date"] <= selection_end]
                if len(sel) < 20:
                    continue
                candidates.append({"feature_set": fs, "model": mid, "selection": metrics(sel), "selection_n": int(len(sel))})
        if not candidates:
            summary[f"NEXT_NY17_{h}D"] = {"status": "BLOCKED_NO_CANDIDATE"}
            continue
        candidates = sorted(candidates, key=lambda r: (r["selection"]["brier"], r["selection"]["log_loss"], r["feature_set"], r["model"]))
        winner = candidates[0]
        wf = pd.concat([x for x in all_preds if (not x.empty and int(x["horizon"].iloc[0]) == h and x["feature_set"].iloc[0] == winner["feature_set"] and x["model"].iloc[0] == winner["model"])], ignore_index=True)
        sel = wf[wf["origin_date"] <= selection_end].copy()
        lock = wf[(wf["origin_date"] >= lock_start) & (wf["origin_date"] <= lock_end)].copy()
        th = select_threshold(sel, thresholds)
        lock_p = metrics(lock, "p")
        lock_50 = metrics(lock, "p50")
        lock_freq = metrics(lock, "pfreq")
        lock_sel = selective_metrics(lock, th["threshold"])
        gates = contract["general_direction"]["development_lock_gates_for_prospective_shadow_eligibility"]
        eligible = bool(
            lock_p.get("n", 0) > 0
            and lock_50.get("n", 0) > 0
            and (lock_50["brier"] - lock_p["brier"]) >= float(gates["brier_gain_vs_p50_min"])
            and lock_p["log_loss"] <= lock_50["log_loss"]
            and lock_sel.get("accepted_n", 0) >= int(gates["selective_accepted_n_min"])
            and lock_sel.get("coverage", 0.0) >= float(gates["selective_coverage_min"])
            and (lock_sel.get("accuracy") is not None and lock_sel["accuracy"] >= float(gates["selective_accuracy_min"]))
        )
        leaderboard = []
        for cand in candidates:
            f = pd.concat([x for x in all_preds if (not x.empty and int(x["horizon"].iloc[0]) == h and x["feature_set"].iloc[0] == cand["feature_set"] and x["model"].iloc[0] == cand["model"])], ignore_index=True)
            lk = f[(f["origin_date"] >= lock_start) & (f["origin_date"] <= lock_end)]
            leaderboard.append({
                "feature_set": cand["feature_set"],
                "model": cand["model"],
                "selection": cand["selection"],
                "lock": metrics(lk),
            })
        leaderboard = sorted(leaderboard, key=lambda r: (r["lock"].get("brier", 99), r["lock"].get("log_loss", 99)))
        summary[f"NEXT_NY17_{h}D"] = {
            "winner_selected_prelock": {"feature_set": winner["feature_set"], "model": winner["model"], "selection_metrics": winner["selection"]},
            "frozen_selective_threshold": th,
            "development_lock": {"model": lock_p, "p50": lock_50, "expanding_frequency": lock_freq, "selective": lock_sel},
            "prospective_shadow_eligible": eligible,
            "interpretation": "DEVELOPMENT_LOCK_ONLY_NOT_PROSPECTIVE_NOT_PROMOTION",
            "leaderboard": leaderboard,
        }
    pred = pd.concat(all_preds, ignore_index=True) if all_preds else pd.DataFrame()
    return summary, pred


def load_event_rows(conn) -> pd.DataFrame:
    sql = """
    WITH ev AS (
      SELECT series_id,
             CASE WHEN series_id LIKE '%EMPLOYMENT%' THEN 'EMPLOYMENT'
                  WHEN series_id LIKE '%INFLATION%' THEN 'INFLATION'
                  WHEN series_id LIKE '%FOMC%' THEN 'FOMC' END AS family,
             observation_ts AS event_ts,
             value AS score,
             metadata
      FROM observations
      WHERE series_id = ANY(%s)
        AND observation_ts >= '2023-01-01 00:00:00+00'
        AND observation_ts <  '2025-01-01 00:00:00+00'
    )
    SELECT e.*,
      p0.close AS p0, p5.close AS p5, p15.close AS p15, p30.close AS p30,
      ny1.close AS ny17_next
    FROM ev e
    LEFT JOIN LATERAL (SELECT close FROM xau_intraday_research_cache_1m WHERE observation_ts=e.event_ts-interval '1 minute' LIMIT 1) p0 ON true
    LEFT JOIN LATERAL (SELECT close FROM xau_intraday_research_cache_1m WHERE observation_ts=e.event_ts+interval '4 minute' LIMIT 1) p5 ON true
    LEFT JOIN LATERAL (SELECT close FROM xau_intraday_research_cache_1m WHERE observation_ts=e.event_ts+interval '14 minute' LIMIT 1) p15 ON true
    LEFT JOIN LATERAL (SELECT close FROM xau_intraday_research_cache_1m WHERE observation_ts=e.event_ts+interval '29 minute' LIMIT 1) p30 ON true
    LEFT JOIN LATERAL (
      SELECT close FROM xau_intraday_research_cache_1m x
      WHERE (x.observation_ts AT TIME ZONE 'America/New_York')::date > (e.event_ts AT TIME ZONE 'America/New_York')::date
        AND (x.observation_ts AT TIME ZONE 'America/New_York')::time='16:59:00'
      ORDER BY x.observation_ts LIMIT 1
    ) ny1 ON true
    ORDER BY e.event_ts, e.series_id
    """
    d = q(conn, sql, (MACRO_SERIES,))
    if d.empty:
        raise RuntimeError("BLOCKED_EVENT_DEVELOPMENT_EMPTY")
    d["event_ts"] = pd.to_datetime(d["event_ts"], utc=True)
    if (d["event_ts"] >= pd.Timestamp("2025-01-01", tz="UTC")).any():
        raise RuntimeError("OUTER_LOCK_VIOLATION_EVENT")
    d["state"] = d["metadata"].map(lambda x: (x or {}).get("state"))
    for label, col in [("R5", "p5"), ("R15", "p15"), ("R30", "p30"), ("EVENT_TO_NEXT_NY17", "ny17_next")]:
        d[label] = np.where((d["p0"] > 0) & (d[col] > 0), np.log(d[col] / d["p0"]), np.nan)
    return d


def event_metric(g: pd.DataFrame, horizon: str) -> dict:
    z = g[g[horizon].notna() & g["score"].notna() & (g["score"] != 0)].copy()
    if z.empty:
        return {"n": 0, "status": "BLOCKED_EMPTY"}
    signed = np.sign(z["score"].astype(float)) * z[horizon].astype(float)
    hits = int((signed > 0).sum())
    n = int(len(z))
    p = float(binomtest(hits, n, p=0.5, alternative="greater").pvalue)
    return {
        "n": n,
        "hits": hits,
        "hit_rate": float(hits / n),
        "median_signed_log_return": float(np.median(signed)),
        "exact_binomial_one_sided_p": p,
    }


def run_event(d: pd.DataFrame) -> dict:
    horizons = ["R5", "R15", "R30", "EVENT_TO_NEXT_NY17"]
    strong_states = {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}
    out = {
        "all_events": {h: event_metric(d, h) for h in horizons},
        "strong_state_only": {h: event_metric(d[d["state"].isin(strong_states)], h) for h in horizons},
        "by_family": {},
        "by_year": {},
        "interpretation": "DEVELOPMENT_ONLY. Initial reaction and continuation are distinct targets; no production authority."
    }
    for fam, g in d.groupby("family"):
        out["by_family"][str(fam)] = {h: event_metric(g, h) for h in horizons}
    d = d.copy()
    d["year"] = d["event_ts"].dt.year
    for year, g in d.groupby("year"):
        out["by_year"][str(int(year))] = {h: event_metric(g, h) for h in horizons}
    return out


def main() -> None:
    freeze = json.loads(CONTRACT.read_text())
    if freeze["status"] != "FROZEN_BEFORE_V150_DEVELOPMENT_RUN":
        raise RuntimeError("CONTRACT_NOT_FROZEN")
    if freeze["governance"]["production_authority"]:
        raise RuntimeError("PRODUCTION_AUTHORITY_MUST_BE_FALSE")
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    OUT.mkdir(parents=True, exist_ok=True)
    with psycopg.connect(db) as conn:
        panel = build_panel(conn)
        event_rows = load_event_rows(conn)
    general, preds = run_general(panel, freeze)
    event = run_event(event_rows)
    coverage = {k: int(panel[v].notna().all(axis=1).sum()) for k, v in FEATURE_SETS.items()}
    report = {
        "contract_id": freeze["contract_id"],
        "evidence_class": freeze["evidence_class"],
        "development_origin_first": panel["date"].min().date().isoformat(),
        "development_origin_last": panel["date"].max().date().isoformat(),
        "development_origin_n": int(len(panel)),
        "feature_set_complete_case_counts_for_diagnostic_only": coverage,
        "general_direction": general,
        "event_direction": event,
        "panel_hash": frame_hash(panel),
        "event_rows_hash": frame_hash(event_rows.drop(columns=["metadata"])),
        "AUTO_SELECTOR": "OFF",
        "AUTO_ENSEMBLE": "OFF",
        "production_authority": False,
        "production_writes": "NONE",
        "outer_2025_2026_read": False,
    }
    panel.to_csv(OUT / "v150_development_panel.csv", index=False)
    preds.to_csv(OUT / "v150_general_sequential_predictions.csv", index=False)
    event_rows.drop(columns=["metadata"]).to_csv(OUT / "v150_event_rows.csv", index=False)
    (OUT / "v150_development_results.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
