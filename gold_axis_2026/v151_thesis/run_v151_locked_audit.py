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
CONTRACT = ROOT / "v151_thesis/contracts/v151_master_locked_audit_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v151_thesis"
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


def q(conn, sql: str, params=None) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)


def frame_hash(d: pd.DataFrame) -> str:
    return hashlib.sha256(d.to_csv(index=False, float_format="%.12g", lineterminator="\n").encode()).hexdigest()


def _clip_prob(p: np.ndarray | pd.Series | float):
    return np.clip(p, 1e-6, 1 - 1e-6)


def _logit(p: float) -> float:
    p = float(_clip_prob(p))
    return math.log(p / (1.0 - p))


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def load_ny17(conn, end_date: str) -> pd.DataFrame:
    hist = q(conn, """
        SELECT observation_ts,
               (observation_ts AT TIME ZONE 'America/New_York')::date AS date,
               close,
               'RESEARCH_CACHE_EXACT_1659'::text AS source_class,
               1 AS source_rank
        FROM xau_intraday_research_cache_1m
        WHERE (observation_ts AT TIME ZONE 'America/New_York')::time='16:59:00'
          AND (observation_ts AT TIME ZONE 'America/New_York')::date >= DATE '2023-01-01'
          AND (observation_ts AT TIME ZONE 'America/New_York')::date <= %s::date
        ORDER BY observation_ts
    """, (end_date,))
    current = q(conn, """
        SELECT observation_ts,
               (observation_ts AT TIME ZONE 'America/New_York')::date AS date,
               value AS close,
               'CANONICAL_XAU_EOD_TWELVE_NY17'::text AS source_class,
               2 AS source_rank
        FROM observations
        WHERE series_id='XAU_EOD_TWELVE_NY17'
          AND observation_ts >= '2023-01-01 00:00:00+00'
          AND (observation_ts AT TIME ZONE 'America/New_York')::date <= %s::date
        ORDER BY observation_ts
    """, (end_date,))
    d = pd.concat([hist, current], ignore_index=True)
    if d.empty:
        raise RuntimeError("BLOCKED_NY17_EMPTY")
    d["observation_ts"] = pd.to_datetime(d["observation_ts"], utc=True)
    d["date"] = pd.to_datetime(d["date"])
    d["close"] = pd.to_numeric(d["close"], errors="coerce")
    d = d[d["close"].gt(0)].sort_values(["date", "source_rank", "observation_ts"])
    d = d.drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)
    if d["date"].duplicated().any():
        raise RuntimeError("DUPLICATE_NY17_DATE")
    return d


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
    return float(np.sign(float(mr.iloc[-3:].mean())))


def add_role_context(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["fast_role"] = role_fast(d)
    d["slow_role"] = [_slow_at(d, i) for i in range(len(d))]
    d["monthly_direction_3m"] = [_monthly_direction_at(d, i) for i in range(len(d))]
    d["role_score"] = d[G1].mean(axis=1, skipna=True)
    return d


def load_series(conn, ids: Iterable[str], end_date: str) -> pd.DataFrame:
    d = q(conn, """
        SELECT series_id, observation_ts, value, available_as_of, retrieved_at
        FROM observations
        WHERE series_id = ANY(%s)
          AND observation_ts < (%s::date + interval '2 day')
        ORDER BY series_id, observation_ts, retrieved_at
    """, (list(ids), end_date))
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


def build_panel(conn, end_date: str) -> pd.DataFrame:
    d = add_role_context(add_gold_features(load_ny17(conn, end_date)))
    pit = load_series(conn, PIT_SERIES.values(), end_date)
    d = merge_pit_monthly(d, pit)
    daily = load_series(conn, list(EQUITY_SERIES.values()) + list(PRECIOUS_SERIES.values()), end_date)
    d = merge_lagged_daily(d, daily, EQUITY_SERIES)
    d = merge_lagged_daily(d, daily, PRECIOUS_SERIES)
    return d.sort_values("date").reset_index(drop=True)


def estimator(kind: str, p: float):
    if kind == "logit":
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            StandardScaler(),
            LogisticRegression(C=float(p), max_iter=2000, random_state=SEED),
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


def sequential_predictions(d: pd.DataFrame, h: int, cols: list[str], model_id: str, kind: str, param: float, fit_mode: str, min_train: int, rolling_window: int) -> pd.DataFrame:
    y, ret = targets(d, h)
    rows = []
    for t in range(min_train, len(d) - h):
        mature = [j for j in range(t) if j + h <= t and pd.notna(y.iloc[j])]
        if fit_mode == "rolling":
            mature = mature[-rolling_window:]
        if len(mature) < min_train:
            continue
        yy = y.iloc[mature].astype(int)
        if yy.nunique() < 2:
            continue
        m = estimator(kind, param)
        m.fit(d.loc[mature, cols], yy)
        p = float(m.predict_proba(d.loc[[t], cols])[0, 1])
        all_mature = [j for j in range(t) if j + h <= t and pd.notna(y.iloc[j])]
        freq = (float(y.iloc[all_mature].sum()) + 0.5) / (len(all_mature) + 1.0)
        rows.append({
            "origin_index": t,
            "origin_date": d.loc[t, "date"],
            "target_date": d.loc[t + h, "date"],
            "horizon": h,
            "candidate": model_id,
            "y": int(y.iloc[t]),
            "return": float(ret.iloc[t]),
            "p": p,
            "p50": 0.5,
            "pfreq": freq,
            "role_score": float(d.loc[t, "role_score"]) if pd.notna(d.loc[t, "role_score"]) else 0.0,
            "train_n": len(mature),
        })
    return pd.DataFrame(rows)


def metrics(f: pd.DataFrame, pcol: str = "p") -> dict:
    if f.empty:
        return {"n": 0, "status": "BLOCKED_EMPTY"}
    y = f["y"].astype(int).to_numpy()
    p = _clip_prob(f[pcol].astype(float).to_numpy())
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


def _join_member_rows(frames: dict[str, pd.DataFrame], members: list[str]) -> pd.DataFrame:
    base = None
    for k in members:
        f = frames[k][["origin_index", "origin_date", "target_date", "horizon", "y", "return", "p", "p50", "pfreq", "role_score"]].copy()
        f = f.rename(columns={"p": f"p__{k}"})
        keycols = ["origin_index", "origin_date", "target_date", "horizon", "y", "return", "p50", "pfreq", "role_score"]
        if base is None:
            base = f
        else:
            base = base.merge(f[["origin_index", f"p__{k}"]], on="origin_index", how="inner")
    return pd.DataFrame() if base is None else base


def fixed_average(frames: dict[str, pd.DataFrame], members: list[str], candidate_id: str) -> pd.DataFrame:
    z = _join_member_rows(frames, members)
    if z.empty:
        return z
    z["p"] = z[[f"p__{m}" for m in members]].mean(axis=1)
    z["candidate"] = candidate_id
    return z[["origin_index", "origin_date", "target_date", "horizon", "candidate", "y", "return", "p", "p50", "pfreq", "role_score"]]


def mature_error_weighted(frames: dict[str, pd.DataFrame], members: list[str], candidate_id: str, h: int, lookback: int, eta: float, min_mature: int) -> pd.DataFrame:
    z = _join_member_rows(frames, members)
    if z.empty:
        return z
    history = {m: frames[m].set_index("origin_index") for m in members}
    rows = []
    for r in z.itertuples(index=False):
        t = int(r.origin_index)
        ws = []
        ps = []
        valid = True
        for m in members:
            hm = history[m]
            prior = hm[(hm.index + h <= t)].tail(lookback)
            if len(prior) < min_mature:
                valid = False
                break
            pp = _clip_prob(prior["p"].to_numpy(float))
            yy = prior["y"].to_numpy(int)
            ll = float(np.mean(-(yy * np.log(pp) + (1 - yy) * np.log(1 - pp))))
            ws.append(math.exp(-eta * ll))
            ps.append(float(getattr(r, f"p__{m}")))
        if not valid or sum(ws) <= 0:
            continue
        p = float(np.dot(np.asarray(ws), np.asarray(ps)) / sum(ws))
        rows.append({
            "origin_index": t, "origin_date": r.origin_date, "target_date": r.target_date,
            "horizon": h, "candidate": candidate_id, "y": int(r.y), "return": float(r.return_),
            "p": p, "p50": float(r.p50), "pfreq": float(r.pfreq), "role_score": float(r.role_score)
        })
    return pd.DataFrame(rows)


def dma_style(frames: dict[str, pd.DataFrame], members: list[str], candidate_id: str, h: int, forgetting: float) -> pd.DataFrame:
    z = _join_member_rows(frames, members)
    if z.empty:
        return z
    by_member = {m: frames[m].set_index("origin_index") for m in members}
    logw = {m: 0.0 for m in members}
    rows = []
    for r in z.sort_values("origin_index").itertuples(index=False):
        t = int(r.origin_index)
        # Update only with outcomes whose horizon has matured by this origin.
        matured_index = t - h
        for m in members:
            hm = by_member[m]
            if matured_index in hm.index:
                rr = hm.loc[matured_index]
                p0 = float(_clip_prob(rr["p"]))
                y0 = int(rr["y"])
                loglik = math.log(p0 if y0 == 1 else 1.0 - p0)
                logw[m] = forgetting * logw[m] + loglik
            else:
                logw[m] = forgetting * logw[m]
        mx = max(logw.values())
        w = {m: math.exp(logw[m] - mx) for m in members}
        den = sum(w.values())
        p = sum(w[m] * float(getattr(r, f"p__{m}")) for m in members) / den
        rows.append({
            "origin_index": t, "origin_date": r.origin_date, "target_date": r.target_date,
            "horizon": h, "candidate": candidate_id, "y": int(r.y), "return": float(r.return_),
            "p": float(p), "p50": float(r.p50), "pfreq": float(r.pfreq), "role_score": float(r.role_score)
        })
    return pd.DataFrame(rows)


def role_tilt(base: pd.DataFrame, candidate_id: str, beta: float) -> pd.DataFrame:
    z = base.copy()
    z["p"] = [_sigmoid(_logit(p) + beta * float(s)) for p, s in zip(z["p"], z["role_score"])]
    z["candidate"] = candidate_id
    return z


def build_candidates(d: pd.DataFrame, contract: dict, h: int) -> tuple[dict[str, pd.DataFrame], set[str], set[str]]:
    gd = contract["general_direction"]
    frames: dict[str, pd.DataFrame] = {}
    strict = set(gd["strict_primary_feature_sets"])
    sensitivity = set(gd["research_sensitivity_feature_sets"])
    primary_ids: set[str] = set()
    sensitivity_ids: set[str] = set()
    for fs, cols in FEATURE_SETS.items():
        for spec in gd["base_candidates"]:
            cid = f"{fs}::{spec['id']}"
            f = sequential_predictions(
                d, h, cols, cid, spec["kind"], float(spec["param"]), spec["fit"],
                int(gd["minimum_training_origins"]), int(gd["rolling_window"])
            )
            if not f.empty:
                frames[cid] = f
                if fs in strict:
                    primary_ids.add(cid)
                elif fs in sensitivity:
                    sensitivity_ids.add(cid)
    ac = gd["adaptive_candidates"]
    avg = ac["fixed_pair_average"]
    if all(m in frames for m in avg["members"]):
        frames[avg["id"]] = fixed_average(frames, avg["members"], avg["id"])
        primary_ids.add(avg["id"])
    ew = ac["mature_error_weighted"]
    if all(m in frames for m in ew["members"]):
        frames[ew["id"]] = mature_error_weighted(frames, ew["members"], ew["id"], h, int(ew["lookback_mature_predictions"]), float(ew["eta"]), int(ew["minimum_mature_per_member"]))
        primary_ids.add(ew["id"])
        for ds in ac["dma_style"]:
            frames[ds["id"]] = dma_style(frames, ew["members"], ds["id"], h, float(ds["forgetting_factor"]))
            primary_ids.add(ds["id"])
    for rs in ac["role_logit_tilt"]:
        if rs["base"] in frames:
            frames[rs["id"]] = role_tilt(frames[rs["base"]], rs["id"], float(rs["beta"]))
            primary_ids.add(rs["id"])
    return frames, primary_ids, sensitivity_ids


def _period(f: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    return f[(f["origin_date"] >= s) & (f["origin_date"] <= e)].copy()


def select_threshold(f: pd.DataFrame, thresholds: list[float]) -> dict:
    best = None
    for th in thresholds:
        g = f[(f["p"] - 0.5).abs() >= float(th)]
        if len(g) < 30 or len(g) / max(len(f), 1) < 0.30:
            continue
        acc = float(np.mean((g["p"] >= 0.5).astype(int).to_numpy() == g["y"].astype(int).to_numpy()))
        coverage = float(len(g) / len(f))
        key = (acc, coverage, -float(th))
        if best is None or key > best[0]:
            best = (key, {"threshold": float(th), "validation_accuracy": acc, "validation_coverage": coverage, "validation_accepted_n": int(len(g))})
    return {"threshold": 0.0, "status": "FALLBACK_ZERO"} if best is None else {**best[1], "status": "SELECTED_ON_2025_VALIDATION"}


def selective_metrics(f: pd.DataFrame, th: float) -> dict:
    if f.empty:
        return {"accepted_n": 0, "coverage": 0.0, "accuracy": None, "balanced_accuracy": None}
    g = f[(f["p"] - 0.5).abs() >= th]
    if g.empty:
        return {"accepted_n": 0, "coverage": 0.0, "accuracy": None, "balanced_accuracy": None}
    pred = (g["p"] >= 0.5).astype(int)
    return {
        "accepted_n": int(len(g)),
        "coverage": float(len(g) / len(f)),
        "accuracy": float(np.mean(pred.to_numpy() == g["y"].astype(int).to_numpy())),
        "balanced_accuracy": float(balanced_accuracy_score(g["y"].astype(int), pred)),
    }


def run_general(d: pd.DataFrame, contract: dict) -> tuple[dict, pd.DataFrame]:
    w = contract["windows"]
    gd = contract["general_direction"]
    all_frames = []
    out = {}
    for h in gd["horizons"]:
        frames, primary_ids, sensitivity_ids = build_candidates(d, contract, int(h))
        rows = []
        for cid, f in frames.items():
            if f.empty:
                continue
            all_frames.append(f)
            rows.append({
                "candidate": cid,
                "universe": "THESIS_PRIMARY_STRICT" if cid in primary_ids else "RESEARCH_SENSITIVITY",
                "development": metrics(_period(f, w["development_start"], w["development_end"])),
                "validation_2025": metrics(_period(f, w["validation_start"], w["validation_end"])),
                "test_2026": metrics(_period(f, w["test_start"], w["test_end"])),
            })
        eligible = [r for r in rows if r["candidate"] in primary_ids and r["validation_2025"].get("n", 0) > 0]
        if not eligible:
            out[f"NEXT_NY17_{h}D"] = {"status": "BLOCKED_NO_PRIMARY_CANDIDATE"}
            continue
        eligible.sort(key=lambda r: (r["validation_2025"]["brier"], r["validation_2025"]["log_loss"], r["candidate"]))
        winner_id = eligible[0]["candidate"]
        wf = frames[winner_id]
        val = _period(wf, w["validation_start"], w["validation_end"])
        test = _period(wf, w["test_start"], w["test_end"])
        th = select_threshold(val, [float(x) for x in gd["selective_thresholds_abs_p_minus_half"]])
        val_model = metrics(val)
        val_p50 = metrics(val, "p50")
        val_freq = metrics(val, "pfreq")
        test_model = metrics(test)
        test_p50 = metrics(test, "p50")
        test_freq = metrics(test, "pfreq")
        out[f"NEXT_NY17_{h}D"] = {
            "selection_rule": gd["validation_selection_rule"],
            "winner_frozen_from_2025": winner_id,
            "frozen_selective_threshold": th,
            "validation_2025": {
                "model": val_model, "p50": val_p50, "expanding_frequency": val_freq,
                "selective": selective_metrics(val, float(th["threshold"])),
                "brier_gain_vs_p50": None if val_model.get("n", 0) == 0 else float(val_p50["brier"] - val_model["brier"]),
                "brier_gain_vs_frequency": None if val_model.get("n", 0) == 0 else float(val_freq["brier"] - val_model["brier"]),
            },
            "test_2026_locked_once": {
                "model": test_model, "p50": test_p50, "expanding_frequency": test_freq,
                "selective": selective_metrics(test, float(th["threshold"])),
                "brier_gain_vs_p50": None if test_model.get("n", 0) == 0 else float(test_p50["brier"] - test_model["brier"]),
                "brier_gain_vs_frequency": None if test_model.get("n", 0) == 0 else float(test_freq["brier"] - test_model["brier"]),
            },
            "candidate_scorecard": sorted(rows, key=lambda r: (r["validation_2025"].get("brier", 99), r["validation_2025"].get("log_loss", 99), r["candidate"])),
            "sensitivity_ids_not_eligible_to_win": sorted(sensitivity_ids),
        }
    pred = pd.concat(all_frames, ignore_index=True) if all_frames else pd.DataFrame()
    return out, pred


def load_event_rows(conn, start: str, end: str) -> pd.DataFrame:
    sql = """
    WITH ev AS (
      SELECT series_id,
             CASE WHEN series_id LIKE '%%EMPLOYMENT%%' THEN 'EMPLOYMENT'
                  WHEN series_id LIKE '%%INFLATION%%' THEN 'INFLATION'
                  WHEN series_id LIKE '%%FOMC%%' THEN 'FOMC' END AS family,
             observation_ts AS event_ts,
             value AS score,
             metadata
      FROM observations
      WHERE series_id = ANY(%s)
        AND observation_ts >= %s::timestamptz
        AND observation_ts < (%s::date + interval '1 day')
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
    d = q(conn, sql, (MACRO_SERIES, start, end))
    if d.empty:
        return d
    d["event_ts"] = pd.to_datetime(d["event_ts"], utc=True)
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
    return {
        "n": n,
        "hits": hits,
        "hit_rate": float(hits / n),
        "median_signed_log_return": float(np.median(signed)),
        "exact_binomial_one_sided_p": float(binomtest(hits, n, p=0.5, alternative="greater").pvalue),
    }


def run_event(d: pd.DataFrame, contract: dict) -> dict:
    if d.empty:
        return {"status": "BLOCKED_EVENT_EMPTY"}
    horizons = contract["event_direction"]["horizons"]
    strong = set(contract["event_direction"]["strong_states"])
    d = d.copy()
    d["year"] = d["event_ts"].dt.year
    out = {"by_period": {}, "by_family": {}, "coverage": {}}
    for label, years in {"DEVELOPMENT_2023_2024": [2023, 2024], "VALIDATION_2025": [2025], "TEST_2026": [2026]}.items():
        g = d[d["year"].isin(years)]
        out["by_period"][label] = {
            "all_nonzero_score": {h: event_metric(g, h) for h in horizons},
            "strong_state": {h: event_metric(g[g["state"].isin(strong)], h) for h in horizons},
        }
        out["coverage"][label] = {
            "event_rows": int(len(g)),
            "r15_observed_rows": int(g["R15"].notna().sum()),
            "last_event_ts": None if g.empty else g["event_ts"].max().isoformat(),
        }
    for fam, g in d.groupby("family"):
        out["by_family"][str(fam)] = {}
        for year in [2023, 2024, 2025, 2026]:
            gy = g[g["year"] == year]
            out["by_family"][str(fam)][str(year)] = {h: event_metric(gy, h) for h in horizons}
    return out


def load_current_master_state(conn) -> dict:
    engines = q(conn, """
      SELECT engine_id,engine_role,as_of,evidence_class,runtime_status,status_code,direction_vote_permitted,git_commit,input_fingerprint,metadata
      FROM current_engine_runtime_state_v1
      ORDER BY engine_id
    """)
    features = q(conn, """
      SELECT feature_name,calculation_ts,input_cutoff,value_num,value_text,quality_status,metadata
      FROM current_context_feature_state_v1
      ORDER BY feature_name
    """)
    erows = {}
    for r in engines.to_dict("records"):
        meta = r.get("metadata") if isinstance(r.get("metadata"), dict) else {}
        active = str(r.get("runtime_status")) == "ACTIVE"
        erows[str(r["engine_id"])] = {
            "engine_role": r.get("engine_role"),
            "as_of": None if pd.isna(r.get("as_of")) else pd.Timestamp(r["as_of"]).isoformat(),
            "evidence_class": r.get("evidence_class"),
            "runtime_status": r.get("runtime_status"),
            "status_code": r.get("status_code"),
            "eligible": bool(active),
            "state": meta.get("current_state"),
            "metadata_reference": meta.get("current_month_reference"),
            "direction_vote_permitted": bool(r.get("direction_vote_permitted")),
            "input_fingerprint": r.get("input_fingerprint"),
            "block_reason": None if active else r.get("status_code"),
        }
    frows = {str(r["feature_name"]): {
        "calculation_ts": None if pd.isna(r.get("calculation_ts")) else pd.Timestamp(r["calculation_ts"]).isoformat(),
        "input_cutoff": None if pd.isna(r.get("input_cutoff")) else pd.Timestamp(r["input_cutoff"]).isoformat(),
        "value_num": r.get("value_num"), "value_text": r.get("value_text"), "quality_status": r.get("quality_status")
    } for r in features.to_dict("records")}
    monthly = {}
    for eid in ["VW_MIDAS_MSVR_SUCCESSOR_V1", "CAUSAL_PATCH", "MOMENTUM_3M", "RANDOM_WALK"]:
        row = erows.get(eid, {})
        ref = row.get("metadata_reference") if isinstance(row.get("metadata_reference"), dict) else {}
        monthly[eid] = {
            "eligible": row.get("eligible", False),
            "forecast_value": ref.get("forecast_value"),
            "target_month": ref.get("target_month"),
            "reference_evidence_class": ref.get("evidence_class"),
            "block_reason": row.get("block_reason"),
        }
    strategic = frows.get("MONTHLY_DIRECTION_3M", {})
    return {
        "master_id": "MASTER_ORCHESTRATOR_BASELINE_V1",
        "monthly_price_layer": monthly,
        "strategic_direction": strategic,
        "tactical_layer": {"FAST": erows.get("FAST"), "SLOW": erows.get("SLOW")},
        "event_layer": {"MACRO_EVENT_SUCCESSOR_V2": erows.get("MACRO_EVENT_SUCCESSOR_V2"), "MARKET_SHOCK_CHALLENGER_V3": {"eligible": False, "runtime_status": "RESEARCH_ONLY_NOT_GOVERNED_RUNTIME", "role": "POST_RELEASE_CONFIRMATION_ONLY"}},
        "regime_layer": {"BOCPD_RETURN_SUCCESSOR_V1": erows.get("BOCPD_RETURN_SUCCESSOR_V1")},
        "emergency_layer": {"EMERGENCY_LEVEL": erows.get("EMERGENCY_LEVEL"), "EMERGENCY_REVERSAL": erows.get("EMERGENCY_REVERSAL")},
        "risk_layer": {"GVZ_RISK": erows.get("GVZ_RISK")},
        "feature_surface": frows,
        "policy": "ROLE_HIERARCHICAL_NO_EQUAL_VOTE_MISSING_NOT_NEUTRAL",
        "production_authority": False,
    }


def main() -> None:
    contract = json.loads(CONTRACT.read_text())
    if contract["status"] != "FROZEN_BEFORE_V151_2025_VALIDATION_AND_2026_TEST_RUN":
        raise RuntimeError("CONTRACT_NOT_FROZEN")
    if contract["governance"]["production_authority"]:
        raise RuntimeError("PRODUCTION_AUTHORITY_MUST_BE_FALSE")
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    OUT.mkdir(parents=True, exist_ok=True)
    end_date = contract["windows"]["test_end"]
    with psycopg.connect(db) as conn:
        panel = build_panel(conn, end_date)
        events = load_event_rows(conn, contract["windows"]["development_start"], end_date)
        current_master = load_current_master_state(conn)
    general, preds = run_general(panel, contract)
    event = run_event(events, contract)
    coverage = {k: int(panel[v].notna().all(axis=1).sum()) for k, v in FEATURE_SETS.items()}
    report = {
        "contract_id": contract["contract_id"],
        "evidence_class": contract["evidence_class"],
        "panel_first": panel["date"].min().date().isoformat(),
        "panel_last": panel["date"].max().date().isoformat(),
        "panel_n": int(len(panel)),
        "panel_year_counts": {str(k): int(v) for k, v in panel["date"].dt.year.value_counts().sort_index().items()},
        "feature_set_complete_case_counts_diagnostic": coverage,
        "general_direction": general,
        "event_direction": event,
        "current_master_orchestrator_state": current_master,
        "panel_hash": frame_hash(panel),
        "event_hash": None if events.empty else frame_hash(events.drop(columns=["metadata"])),
        "AUTO_SELECTOR": "OFF",
        "AUTO_ENSEMBLE": "OFF",
        "production_authority": False,
        "production_writes": "NONE",
        "test_tuning_after_read": False,
    }
    panel.to_csv(OUT / "v151_locked_panel.csv", index=False)
    preds.to_csv(OUT / "v151_general_predictions.csv", index=False)
    if not events.empty:
        events.drop(columns=["metadata"]).to_csv(OUT / "v151_event_rows.csv", index=False)
    (OUT / "v151_locked_audit_results.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
