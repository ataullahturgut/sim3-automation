from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

from gold_axis_2026.tools import market_shock_v2_2026_multifrequency_lm_audit as mf

CONTROLS_PER_EPISODE = 5
CONTROL_EXCLUSION_MINUTES = 60
TIME_OF_DAY_TOLERANCE_MINUTES = 60
SEED_BASE = 20260908


def wilson(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if n <= 0:
        return None, None
    p = successes / n
    den = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / den
    half = z * math.sqrt((p * (1.0 - p) / n) + (z * z / (4.0 * n * n))) / den
    return max(0.0, center - half), min(1.0, center + half)


def _signal_caches(scored: dict[str, pd.DataFrame]) -> dict[str, np.ndarray]:
    return {label: np.sort(mf._signal_times(frame, 0.001)) for label, frame in scored.items()}


def _classify_control_times(base_times: pd.DatetimeIndex, caches: dict[str, np.ndarray]) -> str:
    confirms = {}
    for label, spec in mf.FREQ_SPECS.items():
        confirms[label] = mf._confirms(base_times, caches[label], int(spec["tolerance_minutes"]))
    p1, p3, p10 = confirms["1m"], confirms["3m"], confirms["10m"]
    count = int(p1) + int(p3) + int(p10)
    if count >= 2 and (p3 or p10):
        return "FREQ_STRONG"
    if p3 or p10:
        return "FREQ_CONFIRMED"
    if p1:
        return "MICRO_ONLY"
    return "FREQ_ISOLATED"


def _minute_of_day(ts: pd.Timestamp) -> int:
    return int(ts.hour * 60 + ts.minute)


def _circular_tod_distance(a: int, b: int) -> int:
    d = abs(a - b)
    return min(d, 1440 - d)


def _control_valid(seg5: pd.DataFrame, start: int, length: int, ep: dict, shock_positions: np.ndarray) -> bool:
    end = start + length - 1
    if start < 0 or end >= len(seg5):
        return False
    w = seg5.iloc[start : end + 1]
    if len(w) != length:
        return False
    start_ts = pd.Timestamp(w["ts"].iloc[0])
    end_ts = pd.Timestamp(w["ts"].iloc[-1])
    ep_start = pd.Timestamp(ep["start_ts"])
    if start_ts.strftime("%Y-%m") != ep_start.strftime("%Y-%m"):
        return False
    if start_ts.weekday() != ep_start.weekday():
        return False
    if _circular_tod_distance(_minute_of_day(start_ts), _minute_of_day(ep_start)) > TIME_OF_DAY_TOLERANCE_MINUTES:
        return False
    if bool(w["shock_sig"].any()):
        return False
    if length > 1:
        gaps = w["ts"].diff().dt.total_seconds().iloc[1:]
        if not bool(gaps.between(299, 301, inclusive="both").all()):
            return False
    if shock_positions.size:
        positions = np.arange(start, end + 1)
        nearest_bars = int(np.min(np.abs(shock_positions[:, None] - positions[None, :])))
        if nearest_bars <= CONTROL_EXCLUSION_MINUTES // 5:
            return False
    if (end_ts - start_ts).total_seconds() > max((length - 1) * 301, 1):
        return False
    return True


def build_controls(seg5: pd.DataFrame, episodes: list[dict], caches: dict[str, np.ndarray]) -> tuple[list[dict], int]:
    shock_positions = np.flatnonzero(seg5["shock_sig"].fillna(False).to_numpy(bool))
    controls: list[dict] = []
    requested = len(episodes) * CONTROLS_PER_EPISODE
    for ep in episodes:
        ep_start = pd.Timestamp(ep["start_ts"])
        month_mask = seg5["ts"].dt.strftime("%Y-%m").eq(ep_start.strftime("%Y-%m"))
        weekday_mask = seg5["ts"].dt.weekday.eq(ep_start.weekday())
        candidate_starts = np.flatnonzero((month_mask & weekday_mask).to_numpy(bool))
        rng = np.random.default_rng(SEED_BASE + int(ep["episode_id"]))
        rng.shuffle(candidate_starts)
        made = 0
        used: set[int] = set()
        for start in candidate_starts:
            start = int(start)
            if made >= CONTROLS_PER_EPISODE:
                break
            if start in used:
                continue
            if not _control_valid(seg5, start, int(ep["bars"]), ep, shock_positions):
                continue
            w = seg5.iloc[start : start + int(ep["bars"])]
            base_times = pd.DatetimeIndex(pd.to_datetime(w["ts"], utc=True))
            controls.append({
                "episode_id": int(ep["episode_id"]),
                "control_start_ts": pd.Timestamp(w["ts"].iloc[0]).isoformat(),
                "bars": int(ep["bars"]),
                "frequency_class": _classify_control_times(base_times, caches),
            })
            used.add(start)
            made += 1
    return controls, requested


def run() -> dict:
    raw1 = mf.load_one_minute_common_support()
    scored = {}
    freq_meta = {}
    for label, spec in mf.FREQ_SPECS.items():
        frame, meta = mf.score_frequency(raw1, label, spec)
        scored[label] = frame
        freq_meta[label] = meta
    seg5, prior_rows, base_meta = mf.authoritative_jan_may()
    observed_rows = mf.classify_multifrequency(seg5, prior_rows, scored)
    caches = _signal_caches(scored)
    controls, requested = build_controls(seg5, observed_rows, caches)

    obs_n = len(observed_rows)
    obs_strong = sum(r["frequency_class"] == "FREQ_STRONG" for r in observed_rows)
    ctl_n = len(controls)
    ctl_strong = sum(r["frequency_class"] == "FREQ_STRONG" for r in controls)
    obs_rate = obs_strong / obs_n if obs_n else None
    ctl_rate = ctl_strong / ctl_n if ctl_n else None
    obs_ci = wilson(obs_strong, obs_n)
    ctl_ci = wilson(ctl_strong, ctl_n)
    table = [[obs_strong, obs_n - obs_strong], [ctl_strong, ctl_n - ctl_strong]]
    _, pvalue = fisher_exact(table, alternative="two-sided") if obs_n and ctl_n else (None, None)
    completion = ctl_n / requested if requested else None
    nonoverlap = bool(obs_ci[0] is not None and ctl_ci[1] is not None and obs_ci[0] > ctl_ci[1])
    checks = {
        "CONTROL_COMPLETION_GTE_090": completion is not None and completion >= 0.90,
        "WILSON_95_NONOVERLAP": nonoverlap,
        "FISHER_TWO_SIDED_P_LT_0001": pvalue is not None and pvalue < 0.001,
    }
    status = "DISCRIMINATIVE_SANITY_PASS" if all(checks.values()) else "DISCRIMINATIVE_SANITY_FAIL"
    risk_ratio = None
    if obs_rate is not None and ctl_rate is not None:
        risk_ratio = float("inf") if ctl_rate == 0 else obs_rate / ctl_rate

    classes = ["FREQ_STRONG", "FREQ_CONFIRMED", "MICRO_ONLY", "FREQ_ISOLATED"]
    return {
        "contract": "GOLD_CONTROL_MARKET_SHOCK_V2_2026_MULTIFREQUENCY_NULL_AUDIT",
        "status": status,
        "evidence_class": "HISTORICAL_MATCHED_NEGATIVE_CONTROL_SANITY",
        "prospective_claim": False,
        "observed": {
            "episodes": obs_n,
            "freq_strong": obs_strong,
            "freq_strong_rate": obs_rate,
            "wilson_95": {"low": obs_ci[0], "high": obs_ci[1]},
        },
        "controls": {
            "requested": requested,
            "constructed": ctl_n,
            "completion_rate": completion,
            "classes": {c: sum(r["frequency_class"] == c for r in controls) for c in classes},
            "freq_strong_rate": ctl_rate,
            "wilson_95": {"low": ctl_ci[0], "high": ctl_ci[1]},
            "controls_per_episode": CONTROLS_PER_EPISODE,
            "shock_exclusion_minutes": CONTROL_EXCLUSION_MINUTES,
            "time_of_day_tolerance_minutes": TIME_OF_DAY_TOLERANCE_MINUTES,
        },
        "comparison": {
            "freq_strong_risk_ratio_observed_vs_control": risk_ratio,
            "fisher_exact_two_sided_p": pvalue,
            "fisher_role": "SIMPLE_DIAGNOSTIC_CONTROLS_CLUSTERED_BY_EPISODE",
            "checks": checks,
        },
        "frequency_models_reference": freq_meta,
        "authoritative_5m_reference": base_meta,
        "governance": {
            "authoritative_false_positive_rate": "NOT_PROVEN",
            "model_changed": False,
            "v3_created": False,
            "run_2025_authorized": False,
            "production_promotion": "BLOCKED_RESEARCH_ONLY",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="market_shock_v2_2026_multifrequency_null_audit.json")
    args = parser.parse_args()
    out = Path(args.output)
    try:
        report = run()
        out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({
            "status": report["status"],
            "observed": report["observed"],
            "controls": report["controls"],
            "comparison": report["comparison"],
        }, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        report = {
            "contract": "GOLD_CONTROL_MARKET_SHOCK_V2_2026_MULTIFREQUENCY_NULL_AUDIT",
            "status": "BLOCKED_EXECUTION",
            "error": f"{type(exc).__name__}:{exc}",
            "production_promotion": "BLOCKED_RESEARCH_ONLY",
        }
        out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
