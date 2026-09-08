from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from scipy.special import gamma
from scipy.stats import norm

from gold_axis_2026.tools import market_shock_challenger_v2 as v2
from gold_axis_2026.tools import market_shock_v2_realized_move_proxy_audit as proxy

EXPECTED_ROWS = 482_734
EXPECTED_FIRST_TS = "2020-04-06T00:00:00+00:00"
EXPECTED_LAST_TS = "2026-08-31T23:55:00+00:00"
YEAR = 2026
ABD_SESSION_ALPHA = 0.001
K10 = 135
N10 = 144
LM10_ALPHA = 0.001
LM10_CONFIRM_MINUTES = 10


def _db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def load_cache() -> pd.DataFrame:
    with psycopg.connect(_db_url()) as conn, conn.cursor() as cur:
        cur.execute(
            "select observation_ts, close from xau_intraday_research_cache_5m order by observation_ts"
        )
        rows = cur.fetchall()
    frame = pd.DataFrame({
        "ts": [pd.Timestamp(r[0]) for r in rows],
        "close": [float(r[1]) for r in rows],
    })
    if len(frame) != EXPECTED_ROWS:
        raise RuntimeError(f"CACHE_ROW_COUNT_MISMATCH:{len(frame)}:{EXPECTED_ROWS}")
    if frame["ts"].min().isoformat() != EXPECTED_FIRST_TS:
        raise RuntimeError("CACHE_FIRST_TS_MISMATCH")
    if frame["ts"].max().isoformat() != EXPECTED_LAST_TS:
        raise RuntimeError("CACHE_LAST_TS_MISMATCH")
    return frame


def build_returns_10m(raw5: pd.DataFrame) -> pd.DataFrame:
    x = raw5.set_index("ts")[["close"]].resample("10min", label="right", closed="right").last().dropna().reset_index()
    x["logp"] = np.log(x["close"].astype(float))
    x["gap_s"] = x["ts"].diff().dt.total_seconds()
    x["ret"] = x["logp"].diff()
    valid_gap = x["gap_s"].between(540, 900, inclusive="both")
    x.loc[~valid_gap, "ret"] = np.nan
    x["slot"] = x["ts"].dt.weekday * N10 + x["ts"].dt.hour * 6 + (x["ts"].dt.minute // 10)
    x["utc_date"] = x["ts"].dt.floor("D")
    pair = x["ret"].abs() * x["ret"].shift(1).abs()
    x["local_var"] = pair.rolling(K10 - 2, min_periods=K10 - 2).mean().shift(1)
    x["local_sigma"] = np.sqrt(x["local_var"])
    return x


def score_lm10(raw5: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    data10 = build_returns_10m(raw5)
    cutoff = pd.Timestamp("2026-01-01", tz="UTC")
    train10 = data10[data10["ts"] < cutoff].copy()
    periodicity10 = v2.fit_periodicity(train10)
    seg10 = data10[(data10["ts"] >= cutoff) & (data10["ts"] < pd.Timestamp("2026-09-01", tz="UTC"))].copy()
    seg10["period_factor"] = seg10["slot"].map(periodicity10)
    denom = seg10["local_sigma"] * seg10["period_factor"]
    seg10["lm10_score"] = seg10["ret"].abs() / denom
    crit = v2.lm_critical(LM10_ALPHA, n=N10)
    seg10["lm10_eligible"] = seg10["lm10_score"].replace([np.inf, -np.inf], np.nan).notna()
    seg10["lm10_sig"] = seg10["lm10_eligible"] & (seg10["lm10_score"] > crit)
    meta = {
        "K10": K10,
        "N10": N10,
        "alpha": LM10_ALPHA,
        "critical": crit,
        "train_rows": int(len(train10)),
        "periodicity_slots": int(len(periodicity10)),
        "eligible": int(seg10["lm10_eligible"].sum()),
        "signal_bars": int(seg10["lm10_sig"].sum()),
    }
    return seg10, meta


def add_abd_wsd(seg: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    out = seg.copy()
    out["abd_score"] = np.nan
    out["abd_critical"] = np.nan
    out["abd_sig"] = False
    mu23 = (2.0 ** (1.0 / 3.0)) * float(gamma(5.0 / 6.0)) / math.sqrt(math.pi)
    sessions = 0
    valid_sessions = 0
    for bucket, g in out.groupby("ny17_bucket", sort=True):
        sessions += 1
        idx = g.index
        r = g["ret"].astype(float)
        valid = r.notna()
        n = int(valid.sum())
        if n < 200:
            continue
        a = r.abs() ** (2.0 / 3.0)
        triple = a * a.shift(1) * a.shift(2)
        tpv = (mu23 ** -3) * (n / max(n - 2, 1)) * float(triple.sum(skipna=True))
        if not (math.isfinite(tpv) and tpv > 0):
            continue
        beta = 1.0 - (1.0 - ABD_SESSION_ALPHA) ** (1.0 / n)
        critical = float(norm.ppf(1.0 - beta / 2.0))
        pf = g["period_factor"].astype(float)
        sigma_bar = math.sqrt(tpv / n) * pf
        score = g["ret"].abs() / sigma_bar
        sig = valid & pf.notna() & pf.gt(0) & score.gt(critical)
        out.loc[idx, "abd_score"] = score.to_numpy()
        out.loc[idx, "abd_critical"] = critical
        out.loc[idx, "abd_sig"] = sig.to_numpy(bool)
        valid_sessions += 1
    return out, {
        "method": "ABD_STYLE_WSD_TPV_EXPOST",
        "session_alpha": ABD_SESSION_ALPHA,
        "sessions": sessions,
        "valid_sessions": valid_sessions,
        "signal_bars": int(out["abd_sig"].sum()),
        "role": "EX_POST_ROBUSTNESS_ONLY_NOT_LIVE_VOTE",
    }


def _lm10_confirms(ep: dict, seg5: pd.DataFrame, lm10_times: pd.DatetimeIndex) -> bool:
    g = seg5.iloc[ep["start_pos"] : ep["end_pos"] + 1]
    lm5_times = pd.DatetimeIndex(pd.to_datetime(g.loc[g["lm_sig"], "ts"], utc=True))
    if len(lm5_times) == 0 or len(lm10_times) == 0:
        return False
    tol = pd.Timedelta(minutes=LM10_CONFIRM_MINUTES)
    for t5 in lm5_times:
        if bool(((lm10_times - t5).to_series(index=lm10_times).abs() <= tol).any()):
            return True
    return False


def classify_episodes(seg: pd.DataFrame, lm10: pd.DataFrame) -> list[dict]:
    episodes = proxy.build_episodes(seg)
    lm10_times = pd.DatetimeIndex(pd.to_datetime(lm10.loc[lm10["lm10_sig"], "ts"], utc=True))
    rows: list[dict] = []
    for ep in episodes:
        if not ep["has_lm"]:
            continue
        lo = max(0, ep["start_pos"] - 1)
        hi = min(len(seg) - 1, ep["end_pos"] + 1)
        near = seg.iloc[lo : hi + 1]
        abd = bool(near["abd_sig"].any())
        lm10_ok = _lm10_confirms(ep, seg, lm10_times)
        evt = bool(ep["has_evt"])
        primary_count = int(abd) + int(lm10_ok) + int(evt)
        g = seg.iloc[ep["start_pos"] : ep["end_pos"] + 1]
        bns = bool(g["bns_day_sig_expost"].any())
        if primary_count >= 2:
            tier = "MULTI_METHOD_STRONG"
        elif primary_count >= 1:
            tier = "CORROBORATED"
        else:
            tier = "LM_ONLY_UNCORROBORATED"
        row = dict(ep)
        row.update({
            "abd5_confirm": abd,
            "lm10_confirm": lm10_ok,
            "evt30_confirm": evt,
            "bns_day_support": bns,
            "primary_corroboration_count": primary_count,
            "tier": tier,
        })
        rows.append(row)
    return rows


def _tier_summary(rows: list[dict], tier: str) -> dict:
    x = [r for r in rows if r["tier"] == tier]
    vals = np.array([r["max_abs_raw_5m"] for r in x if r["max_abs_raw_5m"] is not None], dtype=float)
    return {
        "episodes": len(x),
        "rate_of_lm_episodes": len(x) / len(rows) if rows else None,
        "raw_0p5_proxy_supported": sum(bool(r["proxy_supported"]) for r in x),
        "raw_0p5_proxy_precision": (sum(bool(r["proxy_supported"]) for r in x) / len(x) if x else None),
        "median_abs_raw_5m": (float(np.median(vals)) if len(vals) else None),
        "p75_abs_raw_5m": (float(np.quantile(vals, 0.75)) if len(vals) else None),
        "p90_abs_raw_5m": (float(np.quantile(vals, 0.90)) if len(vals) else None),
    }


def candidate_diagnostic(seg: pd.DataFrame, lm_rows: list[dict]) -> dict:
    confirmed_positions: set[int] = set()
    for r in lm_rows:
        if r["abd5_confirm"] or r["lm10_confirm"]:
            confirmed_positions.update(range(r["start_pos"], r["end_pos"] + 1))
    conf_mask = pd.Series(False, index=seg.index)
    if confirmed_positions:
        conf_mask.iloc[list(sorted(confirmed_positions))] = True
    candidate = seg["evt30_sig"].fillna(False) | (seg["lm_sig"].fillna(False) & conf_mask)
    tmp = seg.copy()
    tmp["shock_sig"] = candidate
    cand_eps = proxy.build_episodes(tmp)
    n = len(cand_eps)
    supported = sum(bool(e["proxy_supported"]) for e in cand_eps)
    eligible = int(seg["shock_eligible"].sum())
    return {
        "definition": "EVT30_OR_LM5_AND_ABD5_OR_LM10",
        "research_candidate_only": True,
        "signal_bars": int(candidate.sum()),
        "signal_rate": float(candidate.sum() / eligible) if eligible else None,
        "episodes": n,
        "raw_0p5_proxy_supported": supported,
        "raw_0p5_proxy_precision": (supported / n if n else None),
        "baseline_v2_signal_bars": int(seg["shock_sig"].sum()),
        "baseline_v2_signal_rate": float(seg["shock_sig"].sum() / eligible) if eligible else None,
    }


def run() -> dict:
    raw = load_cache()
    data5 = v2.build_returns(raw)
    cutoff = pd.Timestamp("2026-01-01", tz="UTC")
    train5 = data5[data5["ts"] < cutoff].copy()
    periodicity5 = v2.fit_periodicity(train5)
    train5s = v2.add_scores(train5, periodicity5)
    evt30 = v2.fit_evt(train5s["score30"])
    segment_report, seg, bns = v2.score_segment(data5, YEAR, periodicity5, evt30)
    seg = proxy.add_raw_moves(seg)
    seg, abd_meta = add_abd_wsd(seg)
    lm10, lm10_meta = score_lm10(raw)
    rows = classify_episodes(seg, lm10)

    total = len(rows)
    corroborated = sum(r["tier"] != "LM_ONLY_UNCORROBORATED" for r in rows)
    strong = sum(r["tier"] == "MULTI_METHOD_STRONG" for r in rows)
    result = {
        "contract": "GOLD_CONTROL_MARKET_SHOCK_V2_LM_CORROBORATION_AUDIT_2026",
        "year": YEAR,
        "evidence_class": "HISTORICAL_MULTI_METHOD_CORROBORATION",
        "prospective_claim": False,
        "input_source": "NEON_RESEARCH_CACHE",
        "cache": {
            "rows": int(len(raw)),
            "first_ts": raw["ts"].min().isoformat(),
            "last_ts": raw["ts"].max().isoformat(),
        },
        "baseline_v2": segment_report,
        "abd5": abd_meta,
        "lm10": lm10_meta,
        "bns": {
            "eligible_buckets": int(len(bns)),
            "significant_buckets_999": int(bns["bns_sig_999"].sum()) if not bns.empty else 0,
            "role": "SECONDARY_EXPOST_ONLY",
        },
        "lm_episode_corroboration": {
            "lm_containing_episodes": total,
            "abd5_confirmed": sum(bool(r["abd5_confirm"]) for r in rows),
            "lm10_confirmed": sum(bool(r["lm10_confirm"]) for r in rows),
            "evt30_confirmed": sum(bool(r["evt30_confirm"]) for r in rows),
            "bns_day_supported": sum(bool(r["bns_day_support"]) for r in rows),
            "corroborated_any_primary": corroborated,
            "corroborated_any_primary_rate": corroborated / total if total else None,
            "multi_method_strong": strong,
            "multi_method_strong_rate": strong / total if total else None,
            "lm_only_uncorroborated": total - corroborated,
            "lm_only_uncorroborated_rate": (total - corroborated) / total if total else None,
            "up": {
                "n": sum(r["direction"] == "UP" for r in rows),
                "corroborated": sum(r["direction"] == "UP" and r["tier"] != "LM_ONLY_UNCORROBORATED" for r in rows),
            },
            "down": {
                "n": sum(r["direction"] == "DOWN" for r in rows),
                "corroborated": sum(r["direction"] == "DOWN" and r["tier"] != "LM_ONLY_UNCORROBORATED" for r in rows),
            },
        },
        "tiers": {
            "MULTI_METHOD_STRONG": _tier_summary(rows, "MULTI_METHOD_STRONG"),
            "CORROBORATED": _tier_summary(rows, "CORROBORATED"),
            "LM_ONLY_UNCORROBORATED": _tier_summary(rows, "LM_ONLY_UNCORROBORATED"),
        },
        "candidate_diagnostic": candidate_diagnostic(seg, rows),
        "interpretation_contract": {
            "fixed_0p5_proxy_is_primary_ground_truth": False,
            "old_proxy_fail_rewritten": False,
            "uncorroborated_equals_false_positive": False,
            "authoritative_false_positive_rate": "NOT_PROVEN_NO_INDEPENDENT_EVENT_LABEL_SET",
            "production_promotion": "BLOCKED_RESEARCH_ONLY",
            "model_parameters_changed": False,
            "canonical_merge": "NOT_AUTHORIZED",
        },
        "top_uncorroborated": sorted(
            [r for r in rows if r["tier"] == "LM_ONLY_UNCORROBORATED"],
            key=lambda r: r["max_abs_raw_5m"] or 0.0,
            reverse=True,
        )[:25],
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="market_shock_v2_lm_corroboration_2026.json")
    args = parser.parse_args()
    out = Path(args.output)
    try:
        report = run()
        report["status"] = "AUDIT_EXECUTION_PASS_RESEARCH_ONLY"
        out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({
            "status": report["status"],
            "lm_episode_corroboration": report["lm_episode_corroboration"],
            "tiers": report["tiers"],
            "candidate_diagnostic": report["candidate_diagnostic"],
        }, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        report = {
            "contract": "GOLD_CONTROL_MARKET_SHOCK_V2_LM_CORROBORATION_AUDIT_2026",
            "status": "BLOCKED_EXECUTION",
            "error": f"{type(exc).__name__}:{exc}",
            "production_promotion": "BLOCKED_RESEARCH_ONLY",
        }
        out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
