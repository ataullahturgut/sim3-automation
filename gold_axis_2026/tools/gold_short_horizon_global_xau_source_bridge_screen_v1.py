from __future__ import annotations

import json
import math
import os
from datetime import date, datetime, timezone
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo

import numpy as np
import psycopg

HIST = "XAU_STAKTRAKR_RESEARCH_DAILY_R1"
CANDIDATES = ("XAU_EOD_TWELVE_NY17", "XAU_DAILY_XAUS")
ALL_SERIES = (HIST,) + CANDIDATES

OUT_JSON = Path("gold_axis_2026/results/GOLD_SHORT_HORIZON_GLOBAL_XAU_SOURCE_BRIDGE_SCREEN_2026-10-01.json")
OUT_MD = Path("gold_axis_2026/results/GOLD_SHORT_HORIZON_GLOBAL_XAU_SOURCE_BRIDGE_SCREEN_2026-10-01.md")

GATE = {
    "min_common_return_pairs": 60,
    "pearson_min": 0.90,
    "sign_agreement_pct_min": 80.0,
    "return_diff_sd_pct_max": 0.75,
}


def _date_key(ts, series_id: str) -> date:
    if isinstance(ts, date) and not isinstance(ts, datetime):
        return ts
    if not isinstance(ts, datetime):
        raise TypeError(f"unsupported observation_ts type: {type(ts)!r}")
    if series_id == HIST:
        # Frozen authority: StakTrakr 00:00 UTC is a DATE LABEL.
        # Never timezone-convert it to New York.
        if ts.tzinfo is None:
            return ts.date()
        return ts.astimezone(timezone.utc).date()
    if series_id == "XAU_EOD_TWELVE_NY17":
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(ZoneInfo("America/New_York")).date()
    if series_id == "XAU_DAILY_XAUS":
        # Frozen authority: use its observation_ts calendar date as stored by
        # the daily-history pipeline; no lag/date search.
        return ts.date()
    raise KeyError(series_id)


def _rank_average(a: np.ndarray) -> np.ndarray:
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)
    i = 0
    while i < len(a):
        j = i + 1
        while j < len(a) and a[order[j]] == a[order[i]]:
            j += 1
        avg = (i + 1 + j) / 2.0
        ranks[order[i:j]] = avg
        i = j
    return ranks


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or float(np.std(a)) == 0.0 or float(np.std(b)) == 0.0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _fetch_series(cur, series_id: str):
    cur.execute(
        """
        SELECT observation_ts, value
        FROM observations
        WHERE series_id=%s
          AND value IS NOT NULL
        ORDER BY observation_ts
        """,
        (series_id,),
    )
    raw = cur.fetchall()
    by_date = {}
    duplicates = 0
    for ts, value in raw:
        d = _date_key(ts, series_id)
        if d in by_date:
            duplicates += 1
        # Deterministic: later row in observation_ts order wins.
        by_date[d] = float(value)
    return raw, by_date, duplicates


def _inventory(raw, by_date, duplicates):
    if not raw:
        return {
            "raw_rows": 0,
            "source_dates": 0,
            "first_observation_ts": None,
            "last_observation_ts": None,
            "first_source_date": None,
            "last_source_date": None,
            "duplicate_source_dates": 0,
        }
    return {
        "raw_rows": len(raw),
        "source_dates": len(by_date),
        "first_observation_ts": raw[0][0].isoformat(),
        "last_observation_ts": raw[-1][0].isoformat(),
        "first_source_date": min(by_date).isoformat(),
        "last_source_date": max(by_date).isoformat(),
        "duplicate_source_dates": duplicates,
    }


def _bridge(hist: dict[date, float], cand: dict[date, float], candidate_id: str):
    common = sorted(set(hist).intersection(cand))
    if len(common) < 2:
        return {
            "candidate": candidate_id,
            "common_level_dates": len(common),
            "common_return_pairs": max(0, len(common) - 1),
            "gate_pass": False,
            "gate_fail_reasons": ["INSUFFICIENT_COMMON_DATES"],
        }

    h = np.asarray([hist[d] for d in common], dtype=float)
    c = np.asarray([cand[d] for d in common], dtype=float)

    valid_level = np.isfinite(h) & np.isfinite(c) & (h > 0) & (c > 0)
    common = [d for d, ok in zip(common, valid_level) if ok]
    h = h[valid_level]
    c = c[valid_level]

    if len(h) < 2:
        return {
            "candidate": candidate_id,
            "common_level_dates": len(h),
            "common_return_pairs": max(0, len(h) - 1),
            "gate_pass": False,
            "gate_fail_reasons": ["INSUFFICIENT_VALID_LEVELS"],
        }

    rh = np.diff(np.log(h))
    rc = np.diff(np.log(c))
    diff = rh - rc
    ratio = h / c

    pearson = _corr(rh, rc)
    spearman = _corr(_rank_average(rh), _rank_average(rc))
    sign = float(np.mean(np.sign(rh) == np.sign(rc)) * 100.0)
    mad = float(np.mean(np.abs(diff)) * 100.0)
    dsd = float(np.std(diff, ddof=0) * 100.0)
    med_ratio = float(np.median(ratio))
    ratio_cv = float(np.std(ratio, ddof=0) / np.mean(ratio) * 100.0)

    failures = []
    if len(rh) < GATE["min_common_return_pairs"]:
        failures.append(f"COMMON_RETURN_PAIRS<{GATE['min_common_return_pairs']}")
    if not np.isfinite(pearson) or pearson < GATE["pearson_min"]:
        failures.append(f"PEARSON<{GATE['pearson_min']}")
    if sign < GATE["sign_agreement_pct_min"]:
        failures.append(f"SIGN_AGREEMENT<{GATE['sign_agreement_pct_min']}%")
    if dsd > GATE["return_diff_sd_pct_max"]:
        failures.append(f"RETURN_DIFF_SD>{GATE['return_diff_sd_pct_max']}%")

    return {
        "candidate": candidate_id,
        "common_level_dates": len(h),
        "common_return_pairs": len(rh),
        "first_common_date": common[0].isoformat(),
        "last_common_date": common[-1].isoformat(),
        "pearson_log_return": pearson,
        "spearman_log_return": spearman,
        "sign_agreement_pct": sign,
        "mean_abs_return_difference_pct": mad,
        "return_difference_sd_pct": dsd,
        "median_level_ratio_hist_over_candidate": med_ratio,
        "level_ratio_cv_pct": ratio_cv,
        "gate_pass": not failures,
        "gate_fail_reasons": failures,
    }


def _preferred(results):
    eligible = [r for r in results if r.get("common_return_pairs", 0) >= GATE["min_common_return_pairs"]]
    if not eligible:
        return None
    eligible = sorted(eligible, key=lambda r: r.get("pearson_log_return", float("-inf")), reverse=True)
    best = eligible[0]
    if len(eligible) >= 2:
        second = eligible[1]
        p1 = best.get("pearson_log_return", float("-inf"))
        p2 = second.get("pearson_log_return", float("-inf"))
        if np.isfinite(p1) and np.isfinite(p2) and abs(p1 - p2) <= 0.01:
            if second.get("sign_agreement_pct", float("-inf")) > best.get("sign_agreement_pct", float("-inf")):
                best = second
    return best["candidate"]


def main():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    with psycopg.connect(dsn, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                """
                SELECT series_id, count(*), min(observation_ts), max(observation_ts)
                FROM observations
                WHERE series_id = ANY(%s)
                GROUP BY series_id
                ORDER BY series_id
                """,
                (list(ALL_SERIES),),
            )
            table_inventory = {
                sid: {
                    "rows": int(n),
                    "min_observation_ts": lo.isoformat() if lo else None,
                    "max_observation_ts": hi.isoformat() if hi else None,
                }
                for sid, n, lo, hi in cur.fetchall()
            }

            series = {}
            inventory = {}
            for sid in ALL_SERIES:
                raw, by_date, dup = _fetch_series(cur, sid)
                series[sid] = by_date
                inventory[sid] = _inventory(raw, by_date, dup)
            conn.rollback()

    results = [_bridge(series[HIST], series[c], c) for c in CANDIDATES]
    preferred = _preferred(results)
    passing = [r["candidate"] for r in results if r.get("gate_pass")]
    live_status = "RESOLVED" if passing else "UNRESOLVED_NO_CANDIDATE_PASSES_REFERENCE_GATE"

    out = {
        "project": "GOLD_SHORT_HORIZON_GLOBAL_XAU",
        "run_type": "EXISTING_SOURCE_BRIDGE_SCREEN",
        "authority_date": "2026-10-01",
        "database_access": "READ_ONLY",
        "historical_anchor": HIST,
        "candidates": list(CANDIDATES),
        "date_semantics": {
            HIST: "observation_ts UTC calendar date label; NO America/New_York conversion",
            "XAU_EOD_TWELVE_NY17": "true timestamp -> America/New_York trade date",
            "XAU_DAILY_XAUS": "observation_ts calendar date as stored by daily-history pipeline",
            "lag_search": "FORBIDDEN",
        },
        "reference_gate": GATE,
        "neon_inventory_query": table_inventory,
        "source_date_inventory": inventory,
        "bridge_results": results,
        "preferred_existing_candidate_by_frozen_rule": preferred,
        "candidates_passing_reference_gate": passing,
        "prospective_live_extension_status": live_status,
        "target_authority_freeze_allowed": bool(passing),
        "selection_note": (
            "Preferred candidate is descriptive under the frozen ranking rule. "
            "Target authority may be frozen for live extension only if at least one candidate passes every reference gate."
        ),
        "frozen_2025_selection_policy": "CLOSED",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# GOLD SHORT-HORIZON GLOBAL XAU — Source Bridge Screen Result",
        "",
        "**Authority:** 2026-10-01 frozen pre-run specification",
        "",
        f"- Historical anchor: `{HIST}`",
        f"- Preferred existing candidate (frozen ranking rule): `{preferred}`",
        f"- Prospective live extension status: **{live_status}**",
        f"- Target authority freeze allowed: **{bool(passing)}**",
        "",
        "| Candidate | N return | Pearson | Spearman | Sign % | Mean abs diff % | Diff SD % | Median ratio | Ratio CV % | Gate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in results:
        lines.append(
            "| {candidate} | {common_return_pairs} | {pearson_log_return:.6f} | {spearman_log_return:.6f} | "
            "{sign_agreement_pct:.2f} | {mean_abs_return_difference_pct:.3f} | {return_difference_sd_pct:.3f} | "
            "{median_level_ratio_hist_over_candidate:.6f} | {level_ratio_cv_pct:.3f} | {gate} |".format(
                gate="PASS" if r.get("gate_pass") else "FAIL",
                **r,
            )
        )
    lines += [
        "",
        "## Reference gate",
        "",
        f"- Common return pairs >= {GATE['min_common_return_pairs']}",
        f"- Pearson >= {GATE['pearson_min']}",
        f"- Sign agreement >= {GATE['sign_agreement_pct_min']}%",
        f"- Return-difference SD <= {GATE['return_diff_sd_pct_max']}%",
        "",
        "No lag search was performed. 2025 remained closed for model/horizon/threshold selection.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("SOURCE_BRIDGE_SCREEN_RESULT=" + json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
