from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

from gold_axis_2026.tools import market_shock_challenger_v2 as v2

EXPECTED_ROWS = 482_734
EXPECTED_FIRST_TS = "2020-04-06T00:00:00+00:00"
EXPECTED_LAST_TS = "2026-08-31T23:55:00+00:00"
RAW_MOVE_THRESHOLD = 0.005
CONTROL_WINDOWS_PER_EPISODE = 5
CONTROL_EXCLUSION_MINUTES = 60
CONTROL_SEED_BASE = 20260908
MIN_EPISODES = 30
MIN_PROXY_PRECISION = 0.80
MIN_WILSON_LOWER = 0.75
MIN_ENRICHMENT = 5.0
MIN_CONTROL_COMPLETION = 0.90


def _db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def load_cache() -> pd.DataFrame:
    with psycopg.connect(_db_url()) as conn, conn.cursor() as cur:
        cur.execute(
            """
            select observation_ts, close
            from xau_intraday_research_cache_5m
            order by observation_ts
            """
        )
        rows = cur.fetchall()
    frame = pd.DataFrame(
        {
            "ts": [pd.Timestamp(r[0]) for r in rows],
            "close": [float(r[1]) for r in rows],
        }
    )
    if len(frame) != EXPECTED_ROWS:
        raise RuntimeError(f"CACHE_ROW_COUNT_MISMATCH:{len(frame)}:{EXPECTED_ROWS}")
    first_ts = frame["ts"].min().isoformat()
    last_ts = frame["ts"].max().isoformat()
    if first_ts != EXPECTED_FIRST_TS:
        raise RuntimeError(f"CACHE_FIRST_TS_MISMATCH:{first_ts}:{EXPECTED_FIRST_TS}")
    if last_ts != EXPECTED_LAST_TS:
        raise RuntimeError(f"CACHE_LAST_TS_MISMATCH:{last_ts}:{EXPECTED_LAST_TS}")
    return frame


def wilson_interval(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if n <= 0:
        return None, None
    p = successes / n
    den = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / den
    half = z * math.sqrt((p * (1.0 - p) / n) + (z * z / (4.0 * n * n))) / den
    return max(0.0, center - half), min(1.0, center + half)


def add_raw_moves(seg: pd.DataFrame) -> pd.DataFrame:
    out = seg.sort_values("ts").copy()
    prev_close = out["close"].shift(1)
    out["raw_simple_5m"] = out["close"] / prev_close - 1.0
    out.loc[out["ret"].isna(), "raw_simple_5m"] = np.nan

    prev6 = out["close"].shift(6)
    out["raw_simple_30m"] = out["close"] / prev6 - 1.0
    out.loc[out["move30"].isna(), "raw_simple_30m"] = np.nan
    out["month"] = out["ts"].dt.to_period("M").astype(str)
    return out.reset_index(drop=True)


def build_episodes(seg: pd.DataFrame) -> list[dict]:
    sig = seg["shock_sig"].fillna(False).to_numpy(bool)
    times = pd.to_datetime(seg["ts"], utc=True)
    episodes: list[list[int]] = []
    current: list[int] = []
    prev_i: int | None = None
    for i, on in enumerate(sig):
        if not on:
            continue
        new_episode = (
            prev_i is None
            or i != prev_i + 1
            or (times.iloc[i] - times.iloc[prev_i]).total_seconds() > 600
        )
        if new_episode:
            if current:
                episodes.append(current)
            current = [i]
        else:
            current.append(i)
        prev_i = i
    if current:
        episodes.append(current)

    rows: list[dict] = []
    for eid, idxs in enumerate(episodes, start=1):
        g = seg.iloc[idxs]
        has_lm = bool(g["lm_sig"].any())
        has_evt = bool(g["evt30_sig"].any())
        lm_support = bool(
            has_lm
            and g.loc[g["lm_sig"], "raw_simple_5m"].abs().ge(RAW_MOVE_THRESHOLD).any()
        )
        evt_support = bool(
            has_evt
            and g.loc[g["evt30_sig"], "raw_simple_30m"].abs().ge(RAW_MOVE_THRESHOLD).any()
        )
        supported = lm_support or evt_support
        dirs = g.loc[g["shock_sig"], "shock_direction"]
        direction = "UP" if float(dirs.median()) > 0 else "DOWN" if float(dirs.median()) < 0 else "MIXED"
        rows.append(
            {
                "episode_id": eid,
                "start_pos": int(idxs[0]),
                "end_pos": int(idxs[-1]),
                "bars": int(len(idxs)),
                "start_ts": pd.Timestamp(g["ts"].iloc[0]).isoformat(),
                "end_ts": pd.Timestamp(g["ts"].iloc[-1]).isoformat(),
                "month": str(g["month"].iloc[0]),
                "has_lm": has_lm,
                "has_evt": has_evt,
                "compound": has_lm and has_evt,
                "direction": direction,
                "lm_support": lm_support,
                "evt_support": evt_support,
                "proxy_supported": supported,
                "max_abs_raw_5m": float(g["raw_simple_5m"].abs().max(skipna=True)) if g["raw_simple_5m"].notna().any() else None,
                "max_abs_raw_30m": float(g["raw_simple_30m"].abs().max(skipna=True)) if g["raw_simple_30m"].notna().any() else None,
            }
        )
    return rows


def _window_valid_for_episode(seg: pd.DataFrame, start: int, length: int, ep: dict, signal_positions: np.ndarray) -> bool:
    end = start + length - 1
    if start < 0 or end >= len(seg):
        return False
    w = seg.iloc[start : end + 1]
    if len(w) != length or str(w["month"].iloc[0]) != ep["month"] or str(w["month"].iloc[-1]) != ep["month"]:
        return False
    if bool(w["shock_sig"].any()):
        return False
    if length > 1:
        gaps = w["ts"].diff().dt.total_seconds().iloc[1:]
        if not bool(gaps.between(240, 600, inclusive="both").all()):
            return False
    if ep["has_lm"] and not bool(w["raw_simple_5m"].notna().all()):
        return False
    if ep["has_evt"] and not bool(w["raw_simple_30m"].notna().all()):
        return False
    if signal_positions.size:
        nearest = np.min(np.abs(signal_positions[:, None] - np.arange(start, end + 1)[None, :]))
        if nearest <= (CONTROL_EXCLUSION_MINUTES // 5):
            return False
    return True


def _window_supported(seg: pd.DataFrame, start: int, length: int, ep: dict) -> bool:
    w = seg.iloc[start : start + length]
    lm_support = bool(ep["has_lm"] and w["raw_simple_5m"].abs().ge(RAW_MOVE_THRESHOLD).any())
    evt_support = bool(ep["has_evt"] and w["raw_simple_30m"].abs().ge(RAW_MOVE_THRESHOLD).any())
    return lm_support or evt_support


def matched_controls(seg: pd.DataFrame, episodes: list[dict], year: int) -> tuple[list[dict], int]:
    rng = np.random.default_rng(CONTROL_SEED_BASE + year)
    by_month: dict[str, np.ndarray] = {}
    for month, g in seg.groupby("month", sort=True):
        by_month[str(month)] = g.index.to_numpy(dtype=int)
    signal_positions = np.flatnonzero(seg["shock_sig"].fillna(False).to_numpy(bool))

    controls: list[dict] = []
    requested = len(episodes) * CONTROL_WINDOWS_PER_EPISODE
    for ep in episodes:
        starts = by_month.get(ep["month"], np.array([], dtype=int)).copy()
        if starts.size == 0:
            continue
        rng.shuffle(starts)
        made = 0
        for start in starts:
            if made >= CONTROL_WINDOWS_PER_EPISODE:
                break
            if not _window_valid_for_episode(seg, int(start), ep["bars"], ep, signal_positions):
                continue
            controls.append(
                {
                    "episode_id": ep["episode_id"],
                    "start_pos": int(start),
                    "start_ts": pd.Timestamp(seg["ts"].iloc[int(start)]).isoformat(),
                    "bars": ep["bars"],
                    "month": ep["month"],
                    "has_lm": ep["has_lm"],
                    "has_evt": ep["has_evt"],
                    "proxy_supported": _window_supported(seg, int(start), ep["bars"], ep),
                }
            )
            made += 1
    return controls, requested


def summarize_group(episodes: list[dict], key: str, value) -> dict:
    rows = [e for e in episodes if e[key] == value]
    n = len(rows)
    s = sum(bool(e["proxy_supported"]) for e in rows)
    return {"n": n, "supported": s, "precision": (s / n if n else None)}


def run_year(data: pd.DataFrame, year: int) -> dict:
    cutoff = pd.Timestamp(f"{year}-01-01", tz="UTC")
    train = data[data["ts"] < cutoff].copy()
    if len(train) < 100000:
        raise RuntimeError(f"TRAIN_TOO_SMALL:{year}:{len(train)}")

    periodicity = v2.fit_periodicity(train)
    train_scored = v2.add_scores(train, periodicity)
    evt30 = v2.fit_evt(train_scored["score30"])
    segment_report, seg, _ = v2.score_segment(data, year, periodicity, evt30)
    seg = add_raw_moves(seg)
    episodes = build_episodes(seg)
    controls, requested_controls = matched_controls(seg, episodes, year)

    n = len(episodes)
    supported = sum(bool(e["proxy_supported"]) for e in episodes)
    precision = supported / n if n else None
    wilson_low, wilson_high = wilson_interval(supported, n)
    control_n = len(controls)
    control_supported = sum(bool(c["proxy_supported"]) for c in controls)
    control_rate = control_supported / control_n if control_n else None
    enrichment = None
    if precision is not None and control_rate is not None:
        enrichment = float("inf") if control_rate == 0 else precision / control_rate
    completion = control_n / requested_controls if requested_controls else None

    checks = {
        "EPISODES_GTE_30": n >= MIN_EPISODES,
        "PROXY_PRECISION_GTE_080": precision is not None and precision >= MIN_PROXY_PRECISION,
        "WILSON_LOWER_GTE_075": wilson_low is not None and wilson_low >= MIN_WILSON_LOWER,
        "ENRICHMENT_GTE_5": enrichment is not None and enrichment >= MIN_ENRICHMENT,
        "CONTROL_COMPLETION_GTE_090": completion is not None and completion >= MIN_CONTROL_COMPLETION,
    }
    if n < MIN_EPISODES:
        status = "INSUFFICIENT_SAMPLE"
    elif all(checks.values()):
        status = "PASS_PROXY_VALIDATION"
    else:
        status = "FAIL_PROXY_VALIDATION"

    return {
        "contract": "GOLD_CONTROL_MARKET_SHOCK_V2_REALIZED_MOVE_PROXY_AUDIT",
        "year": year,
        "evidence_class": "HISTORICAL_REALIZED_MOVE_PROXY_VALIDATION",
        "prospective_claim": False,
        "authoritative_false_positive_claim": "NOT_PROVEN_NO_INDEPENDENT_EVENT_LABEL_SET",
        "proxy_definition": {
            "raw_move_threshold": RAW_MOVE_THRESHOLD,
            "lm_horizon": "5m_simple_return",
            "evt_horizon": "30m_simple_move",
            "episode_rule": "V2_CONSECUTIVE_SIGNAL_BARS_BREAK_ON_NONSIGNAL_OR_GT10MIN_GAP",
        },
        "training": {
            "train_end_exclusive": cutoff.isoformat(),
            "train_rows": int(len(train)),
            "periodicity_slots": int(len(periodicity)),
            "evt30": asdict(evt30),
        },
        "model_segment": segment_report,
        "episode_results": {
            "episodes": n,
            "supported": supported,
            "unsupported": n - supported,
            "proxy_precision": precision,
            "proxy_false_alarm_rate": (1.0 - precision if precision is not None else None),
            "wilson_95_low": wilson_low,
            "wilson_95_high": wilson_high,
            "lm_containing": summarize_group(episodes, "has_lm", True),
            "evt_containing": summarize_group(episodes, "has_evt", True),
            "compound": summarize_group(episodes, "compound", True),
            "up": summarize_group(episodes, "direction", "UP"),
            "down": summarize_group(episodes, "direction", "DOWN"),
        },
        "matched_controls": {
            "requested": requested_controls,
            "constructed": control_n,
            "completion_rate": completion,
            "supported": control_supported,
            "support_rate": control_rate,
            "enrichment_ratio": enrichment,
            "windows_per_episode": CONTROL_WINDOWS_PER_EPISODE,
            "signal_exclusion_minutes": CONTROL_EXCLUSION_MINUTES,
            "seed": CONTROL_SEED_BASE + year,
        },
        "gate": {
            "checks": checks,
            "status": status,
            "thresholds_frozen_before_run": {
                "min_episodes": MIN_EPISODES,
                "min_proxy_precision": MIN_PROXY_PRECISION,
                "min_wilson_lower": MIN_WILSON_LOWER,
                "min_enrichment": MIN_ENRICHMENT,
                "min_control_completion": MIN_CONTROL_COMPLETION,
            },
        },
        "top_unsupported_episodes": sorted(
            [e for e in episodes if not e["proxy_supported"]],
            key=lambda e: max(e["max_abs_raw_5m"] or 0.0, e["max_abs_raw_30m"] or 0.0),
            reverse=True,
        )[:25],
        "governance": {
            "production_promotion": "BLOCKED_RESEARCH_CHALLENGER_ONLY",
            "existing_lt_1pct_alarm_gate_changed": False,
            "model_parameters_changed": False,
            "database_write": "NONE",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True, choices=[2024, 2025, 2026])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    report: dict = {
        "contract": "GOLD_CONTROL_MARKET_SHOCK_V2_REALIZED_MOVE_PROXY_AUDIT",
        "year": args.year,
    }
    try:
        raw = load_cache()
        data = v2.build_returns(raw)
        report = run_year(data, args.year)
        report["input_source"] = "NEON_RESEARCH_CACHE"
        report["cache_scope"] = {
            "rows": int(len(raw)),
            "first_ts": raw["ts"].min().isoformat(),
            "last_ts": raw["ts"].max().isoformat(),
        }
        output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["gate"]["status"] == "PASS_PROXY_VALIDATION" else 2
    except Exception as exc:
        report["status"] = "BLOCKED_EXECUTION"
        report["error"] = f"{type(exc).__name__}:{exc}"
        report["production_promotion"] = "BLOCKED_RESEARCH_CHALLENGER_ONLY"
        output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
