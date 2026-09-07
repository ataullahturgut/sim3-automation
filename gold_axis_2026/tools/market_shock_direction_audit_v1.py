from __future__ import annotations

import argparse
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from gold_axis_2026.tools import market_shock_challenger_v1 as v1
from gold_axis_2026.tools.market_shock_challenger_v1_lm_sn_fix import lm_critical as corrected_lm_critical

# Research-only, pre-specified before observing this audit's outputs.
YEARS = (2024, 2025, 2026)
FORWARD_HORIZONS_MIN = (15, 30, 60)
ABS_MOVE_THRESHOLDS_PCT = (0.5, 1.0, 1.5, 2.0)


def _sgn(x: float) -> int:
    if not math.isfinite(x) or x == 0:
        return 0
    return 1 if x > 0 else -1


def _episode_starts(seg: pd.DataFrame) -> pd.DataFrame:
    x = seg[seg["consensus_sig"].fillna(False)].copy()
    if x.empty:
        return x
    x = x.sort_values("ts")
    prev_ts = x["ts"].shift(1)
    prev_idx = x.index.to_series().shift(1)
    new_episode = prev_ts.isna() | ((x["ts"] - prev_ts).dt.total_seconds() > 600) | ((x.index.to_series() - prev_idx) != 1)
    return x[new_episode].copy()


def _forward_outcomes(episodes: pd.DataFrame, close_map: dict[pd.Timestamp, float]) -> dict:
    out: dict[str, dict] = {}
    for h in FORWARD_HORIZONS_MIN:
        rows = []
        for _, r in episodes.iterrows():
            ts = pd.Timestamp(r["ts"])
            p0 = float(r["close"])
            p1 = close_map.get(ts + pd.Timedelta(minutes=h))
            if p1 is None or p0 <= 0 or p1 <= 0:
                continue
            fwd = math.log(float(p1) / p0)
            sig_dir = int(np.sign(r["consensus_dir"]))
            if sig_dir == 0:
                continue
            rows.append((sig_dir, fwd))
        n = len(rows)
        continuation = sum(_sgn(fwd) == sig_dir for sig_dir, fwd in rows)
        reversal = sum(_sgn(fwd) == -sig_dir for sig_dir, fwd in rows)
        zero = sum(_sgn(fwd) == 0 for _, fwd in rows)
        out[str(h)] = {
            "eligible_signal_episodes": n,
            "continuation_hits": continuation,
            "continuation_hit_rate": continuation / n if n else None,
            "reversal_hits": reversal,
            "reversal_rate": reversal / n if n else None,
            "zero_forward_return": zero,
            "median_signed_forward_return_pct": float(np.median([sig_dir * fwd * 100 for sig_dir, fwd in rows])) if rows else None,
            "note": "POST_SIGNAL_OUTCOME_NOT_THE_LM_JUMP_DIRECTION_DEFINITION",
        }
    return out


def _coverage(seg: pd.DataFrame, move_col: str) -> dict:
    result: dict[str, dict] = {}
    vals = pd.to_numeric(seg[move_col], errors="coerce")
    for threshold_pct in ABS_MOVE_THRESHOLDS_PCT:
        threshold = threshold_pct / 100.0
        event = vals.abs() >= threshold
        eligible = int(event.sum())
        detected = event & seg["consensus_sig"].fillna(False)
        detected_n = int(detected.sum())
        label_dir = np.sign(vals[detected].to_numpy(float))
        signal_dir = np.sign(seg.loc[detected, "consensus_dir"].to_numpy(float))
        direction_matches = int((label_dir == signal_dir).sum()) if detected_n else 0
        result[str(threshold_pct)] = {
            "eligible_large_move_bars": eligible,
            "detected_bars": detected_n,
            "coverage_recall": detected_n / eligible if eligible else None,
            "detected_direction_matches": direction_matches,
            "direction_match_rate_given_detected": direction_matches / detected_n if detected_n else None,
            "label": f"ABS_{move_col.upper()}_GTE_{threshold_pct}PCT_REALIZED_MOVE_PROXY",
        }
    return result


def _signal_magnitude(seg: pd.DataFrame) -> dict:
    x = seg[seg["consensus_sig"].fillna(False)].copy()
    if x.empty:
        return {"signal_bars": 0}
    a5 = x["ret"].abs().dropna() * 100.0
    a30 = x["move30"].abs().dropna() * 100.0
    return {
        "signal_bars": int(len(x)),
        "abs_5m_return_pct": {
            "p10": float(a5.quantile(0.10)) if len(a5) else None,
            "median": float(a5.median()) if len(a5) else None,
            "p90": float(a5.quantile(0.90)) if len(a5) else None,
        },
        "abs_30m_move_pct": {
            "p10": float(a30.quantile(0.10)) if len(a30) else None,
            "median": float(a30.median()) if len(a30) else None,
            "p90": float(a30.quantile(0.90)) if len(a30) else None,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2020-04-06 00:00:00")
    parser.add_argument("--end", default="2026-08-31 23:59:59")
    parser.add_argument("--output", default="market_shock_direction_audit_v1.json")
    args = parser.parse_args()

    # Isolated methodology correction only: preserve all V1 detection logic.
    v1.lm_critical = corrected_lm_critical

    report: dict = {
        "contract": "GOLD_CONTROL_MARKET_SHOCK_DIRECTION_AUDIT_V1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "code_sha": os.environ.get("GOLD_CODE_SHA", "NOT_PROVIDED"),
        "evidence_class": "HISTORICAL_RESEARCH_RETRIEVAL",
        "prospective_claim": False,
        "production_promotion": "BLOCKED_RESEARCH_AUDIT_ONLY",
        "detector": "V1_WITH_ISOLATED_LEE_MYKLKAND_EQ13_SN_CORRECTION",
        "forward_horizons_minutes_frozen_before_run": list(FORWARD_HORIZONS_MIN),
        "large_move_proxy_thresholds_pct_frozen_before_run": list(ABS_MOVE_THRESHOLDS_PCT),
        "interpretation_contract": {
            "jump_direction": "SIGN_OF_REALIZED_DETECTED_JUMP; CONTEMPORANEOUS, NOT A FUTURE FORECAST",
            "post_signal_direction": "INDEPENDENT REALIZED FORWARD RETURN AT FIXED HORIZONS",
            "false_positive_rate": "NOT_PROVEN_NO_AUTHORITATIVE_EVENT_LABEL_SET",
            "large_move_coverage": "RESEARCH_PROXY_NOT_AUTHORITATIVE_JUMP_LABEL",
        },
    }

    try:
        client = v1.TwelveClient()
        start = pd.Timestamp(args.start, tz="UTC")
        end = pd.Timestamp(args.end, tz="UTC")
        raw = client.history(start, end)
        data = v1.build_returns(raw)
        close_map = {pd.Timestamp(ts): float(close) for ts, close in zip(data["ts"], data["close"])}
        report["history"] = {
            "rows": int(len(data)),
            "valid_5m_returns": int(data["ret"].notna().sum()),
            "gaps_gt_10min": int(data["gap_s"].gt(600).sum()),
            "first_ts": data["ts"].min().isoformat(),
            "last_ts": data["ts"].max().isoformat(),
        }

        years = []
        for year in YEARS:
            train = data[data["ts"] < pd.Timestamp(f"{year}-01-01", tz="UTC")].copy()
            periodicity = v1.fit_periodicity(train)
            train_scored = v1.add_scores(train, periodicity)
            evt5 = v1.fit_evt(train_scored["score5"])
            evt30 = v1.fit_evt(train_scored["score30"])
            scored_all = v1.add_scores(data, periodicity)
            seg_report, seg = v1.summarize_segment(scored_all, year, evt5, evt30)
            episodes = _episode_starts(seg)
            year_report = {
                "year": year,
                "consensus_signal_bars": int(seg_report["consensus"]["signal_bars"]),
                "consensus_episodes": int(seg_report["consensus"]["episodes"]),
                "consensus_signal_rate": float(seg_report["consensus"]["signal_rate"]),
                "episode_starts_count": int(len(episodes)),
                "large_realized_move_coverage_5m": _coverage(seg, "ret"),
                "large_realized_move_coverage_30m": _coverage(seg, "move30"),
                "post_signal_forward_direction": _forward_outcomes(episodes, close_map),
                "signal_magnitude_distribution": _signal_magnitude(seg),
            }
            years.append(year_report)
            print(json.dumps({
                "year": year,
                "episodes": year_report["consensus_episodes"],
                "recall_5m_1pct": year_report["large_realized_move_coverage_5m"]["1.0"]["coverage_recall"],
                "dir_match_5m_1pct": year_report["large_realized_move_coverage_5m"]["1.0"]["direction_match_rate_given_detected"],
                "fwd30_continuation": year_report["post_signal_forward_direction"]["30"]["continuation_hit_rate"],
            }, sort_keys=True), flush=True)

        report["years"] = years
        report["status"] = "RESEARCH_AUDIT_COMPLETE_NOT_PRODUCTION_GATE"
        Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        report["status"] = "BLOCKED"
        report["error"] = f"{type(exc).__name__}:{exc}"
        Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
