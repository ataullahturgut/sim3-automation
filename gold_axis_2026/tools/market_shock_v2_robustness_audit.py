from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

from gold_axis_2026.tools import market_shock_challenger_v2 as v2

EXPECTED_ROWS = 482_734
EXPECTED_FIRST_TS = pd.Timestamp("2020-04-06T00:00:00Z")
EXPECTED_LAST_TS = pd.Timestamp("2026-08-31T23:55:00Z")
YEARS = (2024, 2025, 2026)
SEEDS = tuple(2026090801 + i for i in range(20))
NOISE_SEEDS = tuple(2026090901 + i for i in range(5))
POWER_SIZES = (0.015, 0.020)
NOISE_BPS = (0.5, 1.0)


def _db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def load_raw() -> pd.DataFrame:
    with psycopg.connect(_db_url()) as conn, conn.cursor() as cur:
        cur.execute(
            """
            select observation_ts, close
            from xau_intraday_research_cache_5m
            order by observation_ts
            """
        )
        rows = cur.fetchall()
    out = pd.DataFrame({
        "ts": [pd.Timestamp(r[0]) for r in rows],
        "close": [float(r[1]) for r in rows],
    })
    if len(out) != EXPECTED_ROWS:
        raise RuntimeError(f"CACHE_ROW_COUNT_MISMATCH:{len(out)}:{EXPECTED_ROWS}")
    if out["ts"].min() != EXPECTED_FIRST_TS:
        raise RuntimeError(f"CACHE_FIRST_TS_MISMATCH:{out['ts'].min()}:{EXPECTED_FIRST_TS}")
    if out["ts"].max() != EXPECTED_LAST_TS:
        raise RuntimeError(f"CACHE_LAST_TS_MISMATCH:{out['ts'].max()}:{EXPECTED_LAST_TS}")
    if out["ts"].duplicated().any():
        raise RuntimeError("CACHE_DUPLICATE_TIMESTAMPS")
    if not out["close"].gt(0).all():
        raise RuntimeError("CACHE_NONPOSITIVE_CLOSE")
    return out


def _periodicity_hash(periodicity: dict[int, float]) -> str:
    payload = json.dumps(
        [[int(k), float(periodicity[k])] for k in sorted(periodicity)],
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def fit_year(data: pd.DataFrame, year: int) -> dict:
    cutoff = pd.Timestamp(f"{year}-01-01", tz="UTC")
    train = data[data["ts"] < cutoff].copy()
    periodicity = v2.fit_periodicity(train)
    train_scored = v2.add_scores(train, periodicity)
    evt30 = v2.fit_evt(train_scored["score30"])
    report, seg, bns = v2.score_segment(data, year, periodicity, evt30)
    return {
        "year": year,
        "periodicity": periodicity,
        "periodicity_hash": _periodicity_hash(periodicity),
        "evt30": evt30,
        "report": report,
        "seg": seg,
        "bns": bns,
        "train_rows": int(len(train)),
    }


def base_pass(data: pd.DataFrame) -> dict[int, dict]:
    return {year: fit_year(data, year) for year in YEARS}


def _signature(fit: dict) -> str:
    payload = {
        "year": fit["year"],
        "train_rows": fit["train_rows"],
        "periodicity_hash": fit["periodicity_hash"],
        "evt30": asdict(fit["evt30"]),
        "report": fit["report"],
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def _same_float(a, b, tol=1e-12) -> bool:
    if a is None or b is None:
        return a is b
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tol)


def deterministic_rerun(first: dict[int, dict], second: dict[int, dict]) -> dict:
    rows = []
    for year in YEARS:
        s1 = _signature(first[year])
        s2 = _signature(second[year])
        rows.append({"year": year, "signature_1": s1, "signature_2": s2, "exact": s1 == s2})
    return {"rows": rows, "pass": all(r["exact"] for r in rows)}


def prefix_invariance(raw: pd.DataFrame, full: dict[int, dict]) -> dict:
    rows = []
    for year in (2024, 2025):
        end = pd.Timestamp(f"{year}-12-31T23:59:59Z")
        prefix_data = v2.build_returns(raw[raw["ts"] <= end].copy())
        pf = fit_year(prefix_data, year)
        ff = full[year]
        checks = {
            "periodicity_hash": pf["periodicity_hash"] == ff["periodicity_hash"],
            "evt_critical": _same_float(pf["evt30"].critical_score, ff["evt30"].critical_score),
            "lm": pf["report"]["lm"] == ff["report"]["lm"],
            "evt30": pf["report"]["evt30"] == ff["report"]["evt30"],
            "market_shock_v2": pf["report"]["market_shock_v2"] == ff["report"]["market_shock_v2"],
        }
        rows.append({"year": year, "checks": checks, "pass": all(checks.values())})
    return {"rows": rows, "pass": all(r["pass"] for r in rows)}


def _eligible_arrays(seg: pd.DataFrame):
    eligible = (
        seg["ret"].notna()
        & seg["move30"].notna()
        & seg["local_sigma"].gt(0)
        & seg["period_factor"].gt(0)
    )
    x = seg.loc[eligible].copy()
    denom = x["local_sigma"].to_numpy(float) * x["period_factor"].to_numpy(float)
    return x, denom


def _power_for_rows(x: pd.DataFrame, denom: np.ndarray, evt30, size: float) -> tuple[float, float]:
    base_r = x["ret"].to_numpy(float)
    base_m30 = x["move30"].to_numpy(float)
    lmcrit = v2.lm_critical(v2.LM_MAIN_ALPHA)
    out = []
    for sign in (-1, 1):
        jump = math.log(1.0 + size) if sign > 0 else math.log(1.0 - size)
        rj = base_r + jump
        m30j = base_m30 + jump
        lm = np.abs(rj) / denom > lmcrit
        e30 = np.abs(m30j) / (math.sqrt(6.0) * denom) >= evt30.critical_score
        out.append(float(np.mean(lm | e30)))
    return out[0], out[1]  # DOWN, UP


def seed_stability(fits: dict[int, dict]) -> dict:
    rows = []
    for year in YEARS:
        fit = fits[year]
        x, denom = _eligible_arrays(fit["seg"])
        if len(x) < 300:
            raise RuntimeError(f"SEED_ELIGIBLE_TOO_SMALL:{year}:{len(x)}")
        idx = np.arange(len(x))
        for seed in SEEDS:
            rng = np.random.default_rng(seed + year)
            take = rng.choice(idx, size=300, replace=False)
            xs = x.iloc[take]
            ds = denom[take]
            for size in POWER_SIZES:
                down, up = _power_for_rows(xs, ds, fit["evt30"], size)
                rows.append({
                    "year": year,
                    "seed": seed,
                    "jump_abs_pct": size * 100.0,
                    "down_power": down,
                    "up_power": up,
                    "mean_power": (down + up) / 2.0,
                })
    p15 = [r["mean_power"] for r in rows if math.isclose(r["jump_abs_pct"], 1.5)]
    p20 = [r["mean_power"] for r in rows if math.isclose(r["jump_abs_pct"], 2.0)]
    checks = {
        "min_1p5_gte_080": min(p15) >= 0.80,
        "min_2p0_gte_095": min(p20) >= 0.95,
    }
    return {
        "seeds": list(SEEDS),
        "sample_n_per_seed": 300,
        "min_1p5_power": float(min(p15)),
        "min_2p0_power": float(min(p20)),
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def volatility_regime_robustness(fits: dict[int, dict]) -> dict:
    rows = []
    for year in YEARS:
        fit = fits[year]
        x, denom = _eligible_arrays(fit["seg"])
        if len(x) < 100:
            raise RuntimeError(f"REGIME_ELIGIBLE_TOO_SMALL:{year}:{len(x)}")
        q = pd.qcut(pd.Series(denom), 4, labels=False, duplicates="drop")
        if q.nunique() != 4:
            raise RuntimeError(f"REGIME_QUARTILES_NOT_FOUR:{year}:{q.nunique()}")
        for quartile in range(4):
            mask = q.to_numpy() == quartile
            xs = x.iloc[np.flatnonzero(mask)]
            ds = denom[mask]
            for size in POWER_SIZES:
                down, up = _power_for_rows(xs, ds, fit["evt30"], size)
                rows.append({
                    "year": year,
                    "volatility_quartile": quartile + 1,
                    "n": int(mask.sum()),
                    "jump_abs_pct": size * 100.0,
                    "down_power": down,
                    "up_power": up,
                    "mean_power": (down + up) / 2.0,
                })
    p15 = [r["mean_power"] for r in rows if math.isclose(r["jump_abs_pct"], 1.5)]
    p20 = [r["mean_power"] for r in rows if math.isclose(r["jump_abs_pct"], 2.0)]
    checks = {
        "every_regime_1p5_gte_080": min(p15) >= 0.80,
        "every_regime_2p0_gte_095": min(p20) >= 0.95,
    }
    return {
        "min_regime_1p5_power": float(min(p15)),
        "min_regime_2p0_power": float(min(p20)),
        "rows": rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def direction_symmetry(fits: dict[int, dict]) -> dict:
    rows = []
    for year in YEARS:
        fit = fits[year]
        x, denom = _eligible_arrays(fit["seg"])
        for size in POWER_SIZES:
            down, up = _power_for_rows(x, denom, fit["evt30"], size)
            rows.append({
                "year": year,
                "jump_abs_pct": size * 100.0,
                "down_power": down,
                "up_power": up,
                "abs_difference": abs(up - down),
            })
    max_diff = max(r["abs_difference"] for r in rows)
    return {"rows": rows, "max_abs_difference": float(max_diff), "pass": max_diff <= 0.05}


def gap_safety() -> dict:
    ts = list(pd.date_range("2025-01-02T00:00:00Z", periods=12, freq="5min"))
    ts[6:] = [x + pd.Timedelta(minutes=20) for x in ts[6:]]
    close = np.exp(math.log(2000.0) + np.arange(12) * 0.0001)
    out = v2.build_returns(pd.DataFrame({"ts": ts, "close": close}))
    return_gap_blocked = bool(pd.isna(out.loc[6, "ret"]))
    move30_blocked = all(bool(pd.isna(out.loc[idx, "move30"])) for idx in range(6, 12))
    return {
        "return_across_gap_blocked": return_gap_blocked,
        "cross_gap_30m_move_blocked": move30_blocked,
        "pass": return_gap_blocked and move30_blocked,
    }


def noise_stress(fits: dict[int, dict]) -> dict:
    rows = []
    for year in YEARS:
        fit = fits[year]
        seg = fit["seg"].copy().reset_index(drop=True)
        denom = seg["local_sigma"].to_numpy(float) * seg["period_factor"].to_numpy(float)
        base_eligible = seg["shock_eligible"].fillna(False).to_numpy(bool) & np.isfinite(denom) & (denom > 0)
        base_rate = float(seg.loc[base_eligible, "shock_sig"].mean()) if base_eligible.any() else None
        r = seg["ret"].to_numpy(float)
        m30 = seg["move30"].to_numpy(float)
        lmcrit = v2.lm_critical(v2.LM_MAIN_ALPHA)
        for bps in NOISE_BPS:
            sigma = bps * 1e-4
            for seed in NOISE_SEEDS:
                rng = np.random.default_rng(seed + year)
                eps = rng.normal(0.0, sigma, len(seg))
                eps1 = np.r_[np.nan, eps[:-1]]
                eps6 = np.r_[np.full(6, np.nan), eps[:-6]]
                rn = r + eps - eps1
                m30n = m30 + eps - eps6
                lm = np.isfinite(rn) & np.isfinite(denom) & (denom > 0) & (np.abs(rn) / denom > lmcrit)
                e30 = np.isfinite(m30n) & np.isfinite(denom) & (denom > 0) & (
                    np.abs(m30n) / (math.sqrt(6.0) * denom) >= fit["evt30"].critical_score
                )
                shock = (lm | e30) & base_eligible
                rate = float(shock.sum() / base_eligible.sum()) if base_eligible.any() else None
                rows.append({
                    "year": year,
                    "noise_bps": bps,
                    "seed": seed,
                    "base_signal_rate": base_rate,
                    "noise_stress_signal_rate": rate,
                    "inflation_multiple": (rate / base_rate) if base_rate and rate is not None else None,
                })
    return {
        "role": "DIAGNOSTIC_ONLY_MICROSTRUCTURE_NOISE_DISTRIBUTION_NOT_IDENTIFIED",
        "noise_bps": list(NOISE_BPS),
        "seeds": list(NOISE_SEEDS),
        "rows": rows,
        "max_noise_signal_rate": max(r["noise_stress_signal_rate"] for r in rows if r["noise_stress_signal_rate"] is not None),
        "max_inflation_multiple": max(r["inflation_multiple"] for r in rows if r["inflation_multiple"] is not None),
        "formal_false_positive_claim": "NOT_PROVEN",
    }


def base_research_gates(fits: dict[int, dict]) -> dict:
    segments = [fits[y]["report"] for y in YEARS]
    synths = [v2.synthetic_injection(fits[y]["seg"], fits[y]["evt30"], y) for y in YEARS]
    return {
        "gates": v2._gate_status(segments, synths),
        "synthetic": synths,
    }


def main() -> int:
    output = Path(os.environ.get("ROBUSTNESS_OUTPUT", "market_shock_v2_robustness_report.json"))
    report = {
        "contract": "GOLD_CONTROL_MARKET_SHOCK_V2_ROBUSTNESS_AUDIT_2026_09_08",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "code_sha": os.environ.get("GOLD_CODE_SHA", "NOT_PROVIDED"),
        "evidence_class": "HISTORICAL_REPLAY_ROBUSTNESS",
        "prospective_claim": False,
        "production_promotion": "BLOCKED_RESEARCH_ONLY",
        "provider_requests": 0,
    }
    try:
        raw = load_raw()
        data = v2.build_returns(raw)
        first = base_pass(data)
        second = base_pass(data)

        r1 = deterministic_rerun(first, second)
        r2 = prefix_invariance(raw, first)
        r3 = seed_stability(first)
        r4 = volatility_regime_robustness(first)
        r5 = direction_symmetry(first)
        r6 = gap_safety()
        r7 = noise_stress(first)
        base = base_research_gates(first)

        checks = {
            "R1_DETERMINISTIC_RERUN": r1["pass"],
            "R2_PREFIX_INVARIANCE": r2["pass"],
            "R3_SYNTHETIC_SEED_STABILITY": r3["pass"],
            "R4_VOLATILITY_REGIME_ROBUSTNESS": r4["pass"],
            "R5_DIRECTION_SYMMETRY": r5["pass"],
            "R6_GAP_SAFETY": r6["pass"],
        }
        cleanup_ready = all(checks.values())
        report.update({
            "data": {
                "rows": int(len(raw)),
                "first_ts": raw["ts"].min().isoformat(),
                "last_ts": raw["ts"].max().isoformat(),
            },
            "frozen_parameters": {
                "K_LM": v2.K_LM,
                "LM_MAIN_ALPHA": v2.LM_MAIN_ALPHA,
                "N_INTRADAY": v2.N_INTRADAY,
                "POT_Q": v2.POT_Q,
                "TAIL_P": v2.TAIL_P,
                "BNS_ALPHA": v2.BNS_ALPHA,
                "BNS_MIN_RETURNS": v2.BNS_MIN_RETURNS,
            },
            "R1_deterministic_rerun": r1,
            "R2_prefix_invariance": r2,
            "R3_seed_stability": r3,
            "R4_volatility_regime": r4,
            "R5_direction_symmetry": r5,
            "R6_gap_safety": r6,
            "R7_microstructure_noise_stress": r7,
            "base_v2_research_gate_recheck": base,
            "robustness_checks": checks,
            "robustness_gate": "PASS" if cleanup_ready else "FAIL",
            "repository_cleanup_readiness": (
                "SOLE_CURRENT_MARKET_SHOCK_RESEARCH_IMPLEMENTATION_READY"
                if cleanup_ready
                else "NOT_READY_KEEP_V1_TREE_UNCHANGED"
            ),
            "production_status": "BLOCKED_UNCHANGED",
            "false_positive_rate_real_history": "NOT_PROVEN_NO_AUTHORITATIVE_EVENT_LABEL_SET",
        })
        output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({
            "robustness_gate": report["robustness_gate"],
            "repository_cleanup_readiness": report["repository_cleanup_readiness"],
            "checks": checks,
            "seed_min_1p5": r3["min_1p5_power"],
            "seed_min_2p0": r3["min_2p0_power"],
            "regime_min_1p5": r4["min_regime_1p5_power"],
            "regime_min_2p0": r4["min_regime_2p0_power"],
            "direction_max_diff": r5["max_abs_difference"],
            "noise_max_rate": r7["max_noise_signal_rate"],
            "noise_max_inflation": r7["max_inflation_multiple"],
            "base_research_numeric_gates": base["gates"]["research_numeric_gates"],
        }, indent=2, sort_keys=True))
        return 0 if cleanup_ready else 2
    except Exception as exc:
        report["status"] = "BLOCKED_EXECUTION"
        report["error"] = f"{type(exc).__name__}:{exc}"
        output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
