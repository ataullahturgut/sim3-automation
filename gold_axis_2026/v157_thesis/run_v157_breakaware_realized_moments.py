from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from scipy.stats import norm
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import accuracy_score, balanced_accuracy_score, matthews_corrcoef, mean_pinball_loss

from gold_axis_2026.tools import bocpd_return_successor_v1 as bocpd
from gold_axis_2026.v155_thesis import run_v155_dynamic_crossmarket_direction as v155

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v157_thesis/contracts/v157_breakaware_realized_moments_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v157_thesis"


def q(conn, sql: str, params=None) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)


def add_target(d: pd.DataFrame, h: int) -> pd.DataFrame:
    z = d.copy().sort_values("date").reset_index(drop=True)
    z["target_close"] = z["close"].shift(-h)
    z["target_date"] = z["date"].shift(-h)
    z["target_return"] = np.log(z["target_close"] / z["close"])
    z["y"] = np.where(z["target_return"].notna(), (z["target_return"] > 0).astype(int), np.nan)
    z["origin_index"] = np.arange(len(z), dtype=int)
    return z


def load_realized_moments(conn, contract: dict) -> pd.DataFrame:
    w = contract["windows"]
    s = contract["source"]["realized_moment_session"]
    d = q(
        conn,
        """
        WITH session_bars AS (
          SELECT observation_ts,
                 close::double precision AS close,
                 (observation_ts AT TIME ZONE 'America/New_York')::date AS date,
                 (observation_ts AT TIME ZONE 'America/New_York')::time AS ny_time
          FROM xau_intraday_research_cache_1m
          WHERE observation_ts >= %s::timestamptz
            AND observation_ts < (%s::date + interval '1 day')
            AND close > 0
            AND (observation_ts AT TIME ZONE 'America/New_York')::time >= %s::time
            AND (observation_ts AT TIME ZONE 'America/New_York')::time <= %s::time
        ), lagged AS (
          SELECT *,
                 lag(close) OVER (PARTITION BY date ORDER BY observation_ts) AS prev_close,
                 lag(observation_ts) OVER (PARTITION BY date ORDER BY observation_ts) AS prev_ts
          FROM session_bars
        ), returns AS (
          SELECT date, observation_ts,
                 CASE
                   WHEN prev_close > 0
                    AND extract(epoch FROM (observation_ts-prev_ts)) > 0
                    AND extract(epoch FROM (observation_ts-prev_ts)) <= %s
                   THEN ln(close/prev_close)
                 END AS r
          FROM lagged
        ), valid AS (
          SELECT date, observation_ts, r,
                 lag(r) OVER (PARTITION BY date ORDER BY observation_ts) AS prev_r
          FROM returns
          WHERE r IS NOT NULL
        )
        SELECT date,
               count(*)::integer AS rm_n,
               sum(r*r)::double precision AS rm_rv,
               sum(CASE WHEN r < 0 THEN r*r ELSE 0 END)::double precision AS rm_rsv_neg,
               sum(CASE WHEN r >= 0 THEN r*r ELSE 0 END)::double precision AS rm_rsv_pos,
               sum(r*r*r)::double precision AS rm_m3,
               sum(r*r*r*r)::double precision AS rm_m4,
               (pi()/2.0 * sum(abs(r)*abs(prev_r)) FILTER (WHERE prev_r IS NOT NULL))::double precision AS rm_bpv,
               max(abs(r))::double precision AS rm_max_abs,
               max(observation_ts) AS rm_last_ts
        FROM valid
        GROUP BY date
        ORDER BY date
        """,
        (w["data_start"], w["test_end"], s["start"], s["end"], int(s["maximum_gap_seconds"])),
    )
    if d.empty:
        raise RuntimeError("BLOCKED_REALIZED_MOMENTS_EMPTY")
    d["date"] = pd.to_datetime(d["date"])
    d["rm_last_ts"] = pd.to_datetime(d["rm_last_ts"], utc=True)
    for c in ["rm_n", "rm_rv", "rm_rsv_neg", "rm_rsv_pos", "rm_m3", "rm_m4", "rm_bpv", "rm_max_abs"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    n = d["rm_n"].astype(float)
    rv = d["rm_rv"].astype(float)
    d["rm_vol"] = np.sqrt(rv.clip(lower=0.0))
    d["rm_downside_share"] = d["rm_rsv_neg"] / rv.replace(0, np.nan)
    d["rm_skew"] = np.sqrt(n) * d["rm_m3"] / np.power(rv.replace(0, np.nan), 1.5)
    d["rm_kurt"] = n * d["rm_m4"] / np.power(rv.replace(0, np.nan), 2.0)
    d["rm_jump_fraction"] = np.maximum(0.0, 1.0 - d["rm_bpv"] / rv.replace(0, np.nan))
    min_n = int(s["minimum_valid_returns"])
    moment_cols = contract["realized_moment_features"]
    finite = np.isfinite(d[moment_cols].to_numpy(dtype=float)).all(axis=1)
    d["rm_valid"] = d["rm_n"].ge(min_n) & finite
    # Invalid moment rows carry no modeled values; no silent imputation of the realized-moment channel.
    d.loc[~d["rm_valid"], moment_cols] = np.nan
    return d


def build_bocpd_daily_context(panel: pd.DataFrame) -> pd.DataFrame:
    contract = bocpd.load_contract()
    core = bocpd.load_core_monthly()
    returns = bocpd.monthly_log_returns(core)
    prior = bocpd.fit_development_prior(returns, contract)
    w = contract["windows"]
    replay_returns = returns.loc[pd.Timestamp(w["development_start"]): pd.Timestamp(w["locked_end"])]
    rows = bocpd.run_bocpd(replay_returns, prior, int(contract["hazard"]["expected_run_length_months"]), contract).reset_index()
    rows = rows.rename(columns={"month": "bocpd_month"})
    rows["bocpd_month"] = pd.to_datetime(rows["bocpd_month"])
    rows["bocpd_available_date"] = rows["bocpd_month"].dt.to_period("M").dt.end_time.dt.normalize() + pd.Timedelta(days=1)
    rows["bocpd_map_reset"] = rows["map_reset"].astype(float)
    rows["bocpd_reset_fraction"] = rows["reset_fraction"].astype(float)
    rows["bocpd_map_run"] = rows["map_run"].astype(float)
    rows["bocpd_segment_mean"] = rows["map_segment_mean"].astype(float)
    rows["bocpd_entropy"] = rows["run_length_entropy"].astype(float)
    rows["bocpd_p_run0"] = rows["p_run0"].astype(float)
    rows["bocpd_last_break_available"] = rows["bocpd_available_date"].where(rows["map_reset"].astype(bool)).ffill()
    keep = [
        "bocpd_available_date", "bocpd_month", "bocpd_map_reset", "bocpd_reset_fraction", "bocpd_map_run",
        "bocpd_segment_mean", "bocpd_entropy", "bocpd_p_run0", "bocpd_last_break_available",
    ]
    left = panel.copy().sort_values("date")
    right = rows[keep].sort_values("bocpd_available_date")
    out = pd.merge_asof(left, right, left_on="date", right_on="bocpd_available_date", direction="backward", allow_exact_matches=True)
    bad = out["bocpd_month"].notna() & (out["bocpd_month"].dt.to_period("M") >= out["date"].dt.to_period("M"))
    if bad.any():
        raise RuntimeError("BOCPD_CURRENT_OR_FUTURE_MONTH_LEAK")
    return out.sort_values("date").reset_index(drop=True)


def build_panel(conn, contract: dict) -> tuple[pd.DataFrame, list[str], list[str], list[str]]:
    base, _, full_cols = v155.build_panel(conn, contract)
    moments = load_realized_moments(conn, contract)
    d = base.merge(moments, on="date", how="left", validate="one_to_one")
    d = build_bocpd_daily_context(d)
    moment_cols = list(contract["realized_moment_features"])
    bocpd_cols = list(contract["bocpd_context_features"])
    d["rm_valid"] = d["rm_valid"].fillna(False).astype(bool)
    for c in bocpd_cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    full_plus = list(full_cols) + moment_cols + bocpd_cols
    return d, list(full_cols), full_plus, moment_cols


def regressor(contract: dict, quantile: float) -> HistGradientBoostingRegressor:
    c = contract["model"]
    return HistGradientBoostingRegressor(
        loss="quantile",
        quantile=float(quantile),
        max_depth=int(c["max_depth"]),
        max_iter=int(c["max_iter"]),
        learning_rate=float(c["learning_rate"]),
        l2_regularization=float(c["l2_regularization"]),
        random_state=int(c["random_state"]),
    )


def mature_indices(z: pd.DataFrame, t: int, h: int, require_moments: bool) -> list[int]:
    out = [j for j in range(t) if j + h <= t and pd.notna(z.loc[j, "target_return"])]
    if require_moments:
        out = [j for j in out if bool(z.loc[j, "rm_valid"])]
    return out


def training_indices(z: pd.DataFrame, t: int, h: int, training: str, require_moments: bool, contract: dict) -> tuple[list[int], str, str | None]:
    cfg = contract["break_aware_training"]
    mature = mature_indices(z, t, h, require_moments)
    if len(mature) < int(cfg["minimum_mature_targets"]):
        return [], "INSUFFICIENT_MATURE", None
    cap = int(cfg["rolling_cap"])
    if training == "ROLLING126":
        return mature[-cap:], "ROLLING126", None
    if training != "BREAK_AWARE":
        raise KeyError(training)
    raw_break = z.loc[t, "bocpd_last_break_available"]
    if pd.notna(raw_break):
        b = pd.Timestamp(raw_break)
        post = [j for j in mature if pd.Timestamp(z.loc[j, "date"]) >= b]
        if len(post) >= int(cfg["minimum_post_break_mature_targets"]):
            return post[-cap:], "POST_BREAK", b.date().isoformat()
    return mature[-cap:], "ROLLING126_FALLBACK", None


def sequential_quantiles(z: pd.DataFrame, features: list[str], candidate: str, training: str, require_moments: bool, h: int, contract: dict) -> pd.DataFrame:
    qs = [float(x) for x in contract["model"]["quantiles"]]
    start = pd.Timestamp(contract["windows"]["formation_score_start"])
    rows: list[dict] = []
    for t in range(len(z) - h):
        if pd.Timestamp(z.loc[t, "date"]) < start:
            continue
        if require_moments and not bool(z.loc[t, "rm_valid"]):
            continue
        train, train_mode, break_date = training_indices(z, t, h, training, require_moments, contract)
        if not train:
            continue
        ytrain = z.loc[train, "target_return"].astype(float)
        if not np.isfinite(ytrain.to_numpy()).all():
            raise RuntimeError("NONFINITE_TRAINING_TARGET")
        preds = []
        for qq in qs:
            m = regressor(contract, qq)
            m.fit(z.loc[train, features], ytrain)
            preds.append(float(m.predict(z.loc[[t], features])[0]))
        q25, q50, q75 = sorted(preds)
        rows.append({
            "origin_index": int(t),
            "origin_date": z.loc[t, "date"],
            "target_date": z.loc[t, "target_date"],
            "target_return": float(z.loc[t, "target_return"]),
            "y": int(z.loc[t, "y"]),
            "candidate": candidate,
            "q25": q25,
            "q50": q50,
            "q75": q75,
            "train_n": int(len(train)),
            "training_mode_realized": train_mode,
            "break_date_used": break_date,
        })
    return pd.DataFrame(rows)


def period_slice(f: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    if f.empty:
        return f.copy()
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return f[(f["origin_date"] >= a) & (f["origin_date"] <= b) & (f["target_date"] <= b)].copy()


def pinball_row(f: pd.DataFrame) -> np.ndarray:
    y = f["target_return"].to_numpy(float)
    losses = []
    for qv, col in [(0.25, "q25"), (0.50, "q50"), (0.75, "q75")]:
        pred = f[col].to_numpy(float)
        e = y - pred
        losses.append(np.maximum(qv * e, (qv - 1.0) * e))
    return np.mean(np.vstack(losses), axis=0)


def pt_test(actual: np.ndarray, predicted: np.ndarray) -> dict:
    y = np.asarray(actual, dtype=int)
    x = np.asarray(predicted, dtype=int)
    n = len(y)
    if n < 5 or np.unique(y).size < 2 or np.unique(x).size < 2:
        return {"statistic": None, "pvalue_one_sided": None, "status": "UNDEFINED_DEGENERATE_MARGIN"}
    py = float(np.mean(y))
    px = float(np.mean(x))
    phat = float(np.mean(y == x))
    pstar = px * py + (1.0 - px) * (1.0 - py)
    var_p = pstar * (1.0 - pstar) / n
    var_star = (
        ((2.0 * py - 1.0) ** 2) * px * (1.0 - px) / n
        + ((2.0 * px - 1.0) ** 2) * py * (1.0 - py) / n
        + 4.0 * px * py * (1.0 - px) * (1.0 - py) / (n * n)
    )
    den2 = var_p - var_star
    if not math.isfinite(den2) or den2 <= 0:
        return {"statistic": None, "pvalue_one_sided": None, "status": "UNDEFINED_NONPOSITIVE_VARIANCE"}
    stat = (phat - pstar) / math.sqrt(den2)
    return {"statistic": float(stat), "pvalue_one_sided": float(norm.sf(stat)), "status": "OK"}


def metrics(f: pd.DataFrame) -> dict:
    if f.empty:
        return {"n": 0, "status": "BLOCKED_EMPTY"}
    y = f["y"].astype(int).to_numpy()
    med = (f["q50"].to_numpy(float) > 0).astype(int)
    qloss = {
        "q25_pinball": float(mean_pinball_loss(f["target_return"], f["q25"], alpha=0.25)),
        "q50_pinball": float(mean_pinball_loss(f["target_return"], f["q50"], alpha=0.50)),
        "q75_pinball": float(mean_pinball_loss(f["target_return"], f["q75"], alpha=0.75)),
    }
    qloss["mean_pinball"] = float(np.mean(list(qloss.values())))
    q25 = f["q25"].to_numpy(float)
    q75 = f["q75"].to_numpy(float)
    sig = np.where(q25 > 0, 1, np.where(q75 < 0, 0, -1))
    mask = sig >= 0
    z_y, z_p = y[mask], sig[mask].astype(int)
    selective = {
        "selective_n": int(mask.sum()),
        "coverage": float(mask.mean()),
        "up_signals": int(np.sum(z_p == 1)),
        "down_signals": int(np.sum(z_p == 0)),
        "actual_up_rate_on_signals": float(np.mean(z_y)) if len(z_y) else None,
    }
    if len(z_y):
        selective.update({
            "selective_accuracy": float(accuracy_score(z_y, z_p)),
            "selective_balanced_accuracy": float(balanced_accuracy_score(z_y, z_p)),
            "mcc": float(matthews_corrcoef(z_y, z_p)),
            "median_signed_realized_return": float(np.median(np.where(z_p == 1, 1.0, -1.0) * f.loc[mask, "target_return"].to_numpy(float))),
            "pesaran_timmermann": pt_test(z_y, z_p),
        })
    else:
        selective.update({"selective_accuracy": None, "selective_balanced_accuracy": None, "mcc": None, "median_signed_realized_return": None, "pesaran_timmermann": {"status": "NO_SIGNAL"}})
    return {
        "n": int(len(f)),
        "actual_up_rate": float(np.mean(y)),
        "median_accuracy": float(accuracy_score(y, med)),
        "median_balanced_accuracy": float(balanced_accuracy_score(y, med)),
        "median_mcc": float(matthews_corrcoef(y, med)),
        "median_predicted_up_rate": float(np.mean(med)),
        **qloss,
        **selective,
    }


def hac_dm_hln(base: pd.DataFrame, challenger: pd.DataFrame, h: int) -> dict:
    a = base[["origin_index", "target_return", "q25", "q50", "q75"]].copy()
    b = challenger[["origin_index", "q25", "q50", "q75"]].copy()
    b = b.rename(columns={"q25": "cq25", "q50": "cq50", "q75": "cq75"})
    m = a.merge(b, on="origin_index", how="inner")
    if len(m) < max(20, h + 5):
        return {"n": int(len(m)), "status": "INSUFFICIENT_ALIGNED"}
    base_like = m.rename(columns={"cq25": "_cq25", "cq50": "_cq50", "cq75": "_cq75"})
    lb = pinball_row(base_like[["target_return", "q25", "q50", "q75"]])
    lc_frame = pd.DataFrame({"target_return": m["target_return"], "q25": m["_cq25"], "q50": m["_cq50"], "q75": m["_cq75"]})
    lc = pinball_row(lc_frame)
    d = lb - lc  # positive means challenger has lower loss
    n = len(d)
    mu = float(np.mean(d))
    u = d - mu
    lag = min(h - 1, n - 2)
    lrv = float(np.mean(u * u))
    for k in range(1, lag + 1):
        gamma = float(np.mean(u[k:] * u[:-k]))
        weight = 1.0 - k / (lag + 1.0)
        lrv += 2.0 * weight * gamma
    if not math.isfinite(lrv) or lrv <= 0:
        return {"n": n, "mean_loss_gain": mu, "status": "NONPOSITIVE_HAC_VARIANCE"}
    dm = mu / math.sqrt(lrv / n)
    factor2 = (n + 1.0 - 2.0 * h + h * (h - 1.0) / n) / n
    hln = dm * math.sqrt(max(factor2, 0.0))
    return {
        "n": n,
        "mean_loss_gain": mu,
        "base_mean_pinball_aligned": float(np.mean(lb)),
        "challenger_mean_pinball_aligned": float(np.mean(lc)),
        "hac_lag": lag,
        "dm_stat": float(dm),
        "hln_dm_stat": float(hln),
        "pvalue_one_sided_challenger_better": float(norm.sf(hln)),
        "status": "OK",
    }


def white_reality_check(period_frames: dict[str, pd.DataFrame], baseline_id: str, challenger_ids: list[str], h: int, contract: dict) -> dict:
    base = period_frames.get(baseline_id, pd.DataFrame())
    if base.empty:
        return {"status": "BLOCKED_BASELINE_EMPTY"}
    merged = base[["origin_index", "target_return", "q25", "q50", "q75"]].copy()
    merged = merged.rename(columns={"q25": "bq25", "q50": "bq50", "q75": "bq75"})
    for cid in challenger_ids:
        f = period_frames.get(cid, pd.DataFrame())
        if f.empty:
            return {"status": f"BLOCKED_EMPTY_{cid}"}
        z = f[["origin_index", "q25", "q50", "q75"]].rename(columns={"q25": f"{cid}_q25", "q50": f"{cid}_q50", "q75": f"{cid}_q75"})
        merged = merged.merge(z, on="origin_index", how="inner")
    if len(merged) < 30:
        return {"n": int(len(merged)), "status": "INSUFFICIENT_COMMON_ORIGINS"}
    base_loss = pinball_row(pd.DataFrame({"target_return": merged["target_return"], "q25": merged["bq25"], "q50": merged["bq50"], "q75": merged["bq75"]}))
    ds = []
    means = {}
    for cid in challenger_ids:
        cl = pinball_row(pd.DataFrame({"target_return": merged["target_return"], "q25": merged[f"{cid}_q25"], "q50": merged[f"{cid}_q50"], "q75": merged[f"{cid}_q75"]}))
        d = base_loss - cl
        ds.append(d)
        means[cid] = float(np.mean(d))
    D = np.column_stack(ds)
    n = len(D)
    obs = math.sqrt(n) * max(float(np.mean(D[:, j])) for j in range(D.shape[1]))
    centered = D - D.mean(axis=0, keepdims=True)
    cfg = contract["evaluation"]["multiple_search_diagnostic"]
    B = int(cfg["bootstrap_replications"])
    block = min(int(cfg["block_length"]), n)
    rng = np.random.default_rng(int(cfg["random_seed"]))
    boot_stats = np.empty(B, dtype=float)
    starts_max = n
    blocks_needed = int(math.ceil(n / block))
    for b in range(B):
        idx = []
        for _ in range(blocks_needed):
            s = int(rng.integers(0, starts_max))
            idx.extend((s + np.arange(block)) % n)
        sample = centered[np.asarray(idx[:n], dtype=int), :]
        boot_stats[b] = math.sqrt(n) * float(np.max(sample.mean(axis=0)))
    p = (1.0 + float(np.sum(boot_stats >= obs))) / (B + 1.0)
    return {
        "status": "OK",
        "n": int(n),
        "block_length": int(block),
        "bootstrap_replications": B,
        "mean_loss_gains": means,
        "observed_max_stat": float(obs),
        "pvalue": float(p),
        "interpretation": "diagnostic for the frozen V1.57 H10 challenger family only; not a correction for the full V1.51-V1.57 search history",
    }


def primary_support(candidate_metrics: dict, dm: dict, contract: dict) -> dict:
    rule = contract["evaluation"]["primary_support_rule"]
    checks = {
        "coverage": candidate_metrics.get("coverage", 0.0) >= float(rule["coverage_each_period_min"]),
        "balanced_above_chance": (candidate_metrics.get("selective_balanced_accuracy") is not None and candidate_metrics["selective_balanced_accuracy"] > float(rule["selective_balanced_accuracy_each_period_strictly_above"])),
        "mcc_positive": (candidate_metrics.get("mcc") is not None and candidate_metrics["mcc"] > float(rule["mcc_each_period_strictly_above"])),
        "both_directions": candidate_metrics.get("up_signals", 0) > 0 and candidate_metrics.get("down_signals", 0) > 0,
        "pinball_better_aligned": dm.get("mean_loss_gain", -np.inf) > 0.0,
    }
    return {"pass": bool(all(checks.values())), "checks": checks}


def run_lane(panel: pd.DataFrame, base_features: list[str], full_plus_features: list[str], lane: str, h: int, contract: dict) -> tuple[dict, pd.DataFrame]:
    z = add_target(panel, h)
    frames: dict[str, pd.DataFrame] = {}
    for spec in contract["candidate_universe"][lane]:
        cid = spec["candidate"]
        use_mom = spec["feature_set"] == "FULL_PLUS_MOMENTS_BOCPD"
        feats = full_plus_features if use_mom else base_features
        frames[cid] = sequential_quantiles(z, feats, cid, spec["training"], use_mom, h, contract)
    w = contract["windows"]
    periods = {
        "FORMATION_2024": (w["formation_score_start"], w["formation_score_end"]),
        "VALIDATION_2025": (w["validation_start"], w["validation_end"]),
        "TEST_2026_AVAILABLE": (w["test_start"], w["test_end"]),
    }
    out = {"horizon": h, "models": {}, "comparisons": {}}
    pred_rows = []
    period_frames: dict[str, dict[str, pd.DataFrame]] = {p: {} for p in periods}
    for cid, f in frames.items():
        block = {}
        for plabel, (a, b) in periods.items():
            g = period_slice(f, a, b)
            period_frames[plabel][cid] = g
            block[plabel] = metrics(g)
            if not g.empty:
                gg = g.copy()
                gg["period"] = plabel
                gg["lane"] = lane
                pred_rows.append(gg)
        out["models"][cid] = block
    if lane == "PRIMARY_H10":
        baseline_id = "H10_BASE_RTQ_R126"
        challengers = ["H10_MOM_R126", "H10_MOM_BREAK"]
        for cid in challengers:
            out["comparisons"][cid] = {}
            for plabel in periods:
                dm = hac_dm_hln(period_frames[plabel][baseline_id], period_frames[plabel][cid], h)
                support = primary_support(out["models"][cid][plabel], dm, contract) if plabel in {"VALIDATION_2025", "TEST_2026_AVAILABLE"} else None
                out["comparisons"][cid][plabel] = {"dm_hln": dm, "support": support}
            vpass = out["comparisons"][cid]["VALIDATION_2025"]["support"]["pass"]
            tpass = out["comparisons"][cid]["TEST_2026_AVAILABLE"]["support"]["pass"]
            out["comparisons"][cid]["two_period_multi_criteria_support"] = bool(vpass and tpass)
        out["white_reality_check"] = {}
        for plabel in periods:
            out["white_reality_check"][plabel] = white_reality_check(period_frames[plabel], baseline_id, challengers, h, contract)
    preds = pd.concat(pred_rows, ignore_index=True) if pred_rows else pd.DataFrame()
    return out, preds


def main() -> None:
    contract = json.loads(CONTRACT.read_text())
    if contract["status"] != "FROZEN_BEFORE_V157_2025_2026_SCORING":
        raise RuntimeError("CONTRACT_NOT_FROZEN")
    if contract["governance"]["production_authority"] or contract["governance"]["production_writes"] != "NONE":
        raise RuntimeError("RESEARCH_ONLY_GOVERNANCE_VIOLATION")
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    with psycopg.connect(db) as conn:
        panel, base_features, full_plus_features, moment_cols = build_panel(conn, contract)
    results = {}
    pred_all = []
    for lane, h in contract["horizons"].items():
        block, preds = run_lane(panel, base_features, full_plus_features, lane, int(h), contract)
        results[lane] = block
        if not preds.empty:
            pred_all.append(preds)
    report = {
        "contract_id": contract["contract_id"],
        "evidence_class": contract["evidence_class"],
        "panel_n": int(len(panel)),
        "panel_first": panel["date"].min().date().isoformat(),
        "panel_last": panel["date"].max().date().isoformat(),
        "moment_valid_n": int(panel["rm_valid"].sum()),
        "moment_valid_rate": float(panel["rm_valid"].mean()),
        "base_feature_count": int(len(base_features)),
        "v157_feature_count": int(len(full_plus_features)),
        "realized_moment_features": moment_cols,
        "bocpd_role": "REGIME_BREAK_CONTEXT_ONLY_NO_DIRECTION_VOTE",
        "results": results,
        "governance": contract["governance"],
        "notes": [
            "V1.57 was frozen before its 2025/2026 scoring run.",
            "All model fits use only targets mature at each origin; moment-dependent models require a valid same-day realized-moment session.",
            "BOCPD uses only completed-month state and never contributes a direction vote.",
            "2025 and 2026 are retrospective successor diagnostics because earlier V1.51-V1.56 research already exposed these outcomes.",
            "The V1.57 White Reality Check covers only the two frozen H10 challengers and cannot erase broader specification-search exposure.",
            "No result-dependent candidate, threshold, horizon or action change is permitted inside V1.57."
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT / "v157_breakaware_realized_moments_panel.csv", index=False)
    if pred_all:
        pd.concat(pred_all, ignore_index=True).to_csv(OUT / "v157_breakaware_realized_moments_predictions.csv", index=False)
    (OUT / "v157_breakaware_realized_moments_results.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
