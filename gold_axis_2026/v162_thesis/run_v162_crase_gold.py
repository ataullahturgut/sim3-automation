from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.metrics import accuracy_score, balanced_accuracy_score, matthews_corrcoef

from gold_axis_2026.v157_thesis import run_v157_breakaware_realized_moments as v157
from gold_axis_2026.v161_thesis import run_v161_short_horizon_price_discovery as v161

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "v162_thesis/contracts/v162_crase_gold_freeze_v1.json"
V157_CONTRACT_PATH = ROOT / "v157_thesis/contracts/v157_breakaware_realized_moments_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v162_thesis"


def load_contract() -> dict:
    c = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_V162_RETROSPECTIVE_SCORING":
        raise RuntimeError("V162_CONTRACT_NOT_FROZEN")
    g = c["governance"]
    if g["AUTO_SELECTOR"] != "OFF" or g["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V162_GOVERNANCE_LOCK_FAIL")
    if g["production_authority"] is not False or g["production_writes"] != "NONE":
        raise RuntimeError("V162_PRODUCTION_AUTHORITY_FORBIDDEN")
    return c


def build_research_surface(database_url: str, contract: dict) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    v157_contract = json.loads(V157_CONTRACT_PATH.read_text(encoding="utf-8"))
    v161_contract = v161.load_contract()
    with psycopg.connect(database_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
        panel, _, _, _ = v157.build_panel(conn, v157_contract)

    panel, fed_evidence = v161.add_corrected_macro(panel, v161_contract)
    gc, gc_evidence = v161.fetch_yahoo_daily("GC=F", "2022-01-01", contract["windows"]["test_end"])
    gld, gld_evidence = v161.fetch_yahoo_daily("GLD", "2022-01-01", contract["windows"]["test_end"])
    panel = v161.add_price_discovery(panel, gc, gld)

    fs = v161.feature_sets(v161_contract)
    base = v161.sequential(panel, 5, "H5_BASE_QB", fs["BASE"], False, False, v161_contract)
    pd_rm = v161.sequential(panel, 5, "H5_PD_RM_QB", fs["BASE_PLUS_RM_PLUS_PD"], True, True, v161_contract)
    pred = pd.concat([base, pd_rm], ignore_index=True)
    evidence = {
        "fed": fed_evidence,
        "GC=F": gc_evidence,
        "GLD": gld_evidence,
        "inherits_v161_same_day_daily_bar_ban": True,
        "researcher_visible_2025_2026": True,
    }
    return panel.sort_values("date").reset_index(drop=True), pred, evidence


def prepare_experts(panel: pd.DataFrame, predictions: pd.DataFrame, h: int = 5) -> pd.DataFrame:
    p = panel.copy().sort_values("date").reset_index(drop=True)
    p["target_close"] = p["close"].shift(-h)
    p["target_date"] = p["date"].shift(-h)
    p["target_return"] = np.log(p["target_close"] / p["close"])
    p["future_direction"] = np.where(
        p["target_return"].notna(), np.where(p["target_return"] > 0, 1, -1), np.nan
    )
    p["origin_index"] = np.arange(len(p), dtype=int)
    for cid in ["H5_BASE_QB", "H5_PD_RM_QB"]:
        x = predictions[predictions["candidate"].eq(cid)].set_index("origin_index")["signal"]
        p[cid] = p["origin_index"].map(x).fillna(0).astype(int)
    p["TREND20"] = np.sign(pd.to_numeric(p["mom20"], errors="coerce")).fillna(0).astype(int)
    p["GC_TREND3"] = np.sign(pd.to_numeric(p["gc_ret3"], errors="coerce")).fillna(0).astype(int)
    return p


def robust_center_scale(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    med = np.nanmedian(x, axis=0)
    q25 = np.nanpercentile(x, 25, axis=0)
    q75 = np.nanpercentile(x, 75, axis=0)
    iqr = q75 - q25
    iqr = np.where(np.isfinite(iqr) & (iqr >= 1e-8), iqr, np.nan)
    return med, iqr


def effective_sample_size(w: np.ndarray) -> float:
    sw = float(np.sum(w))
    sw2 = float(np.sum(w * w))
    if sw <= 0 or sw2 <= 0:
        return 0.0
    return sw * sw / sw2


def local_reliability(
    t: int,
    expert_signal: np.ndarray,
    actual: np.ndarray,
    target_dates: np.ndarray,
    dates: np.ndarray,
    regime_x: np.ndarray,
    med: np.ndarray,
    iqr: np.ndarray,
    cfg: dict,
) -> dict | None:
    hist_cap = int(cfg["similarity"]["history_cap"])
    k = int(cfg["similarity"]["nearest_mature_neighbors"])
    min_shared = int(cfg["similarity"]["minimum_shared_features"])
    half = float(cfg["similarity"]["recency_half_life_trading_rows"])
    min_ess = float(cfg["maturity"]["minimum_effective_support"])
    full_ess = float(cfg["maturity"]["support_full_strength_ess"])

    js = np.arange(max(0, t - hist_cap), t)
    mature = (
        (~pd.isna(target_dates[js]))
        & (target_dates[js] <= dates[t])
        & (expert_signal[js] != 0)
        & np.isfinite(actual[js])
    )
    js = js[mature]
    if len(js) < 10:
        return None

    zt = regime_x[t]
    distances: list[tuple[int, float]] = []
    for j in js:
        shared = np.isfinite(zt) & np.isfinite(regime_x[j]) & np.isfinite(iqr)
        if int(shared.sum()) < min_shared:
            continue
        d = float(np.sqrt(np.mean(((zt[shared] - regime_x[j, shared]) / iqr[shared]) ** 2)))
        if np.isfinite(d):
            distances.append((int(j), d))
    if len(distances) < 10:
        return None

    distances.sort(key=lambda z: z[1])
    distances = distances[:k]
    idx = np.asarray([j for j, _ in distances], dtype=int)
    dist = np.asarray([d for _, d in distances], dtype=float)
    ages = (t - idx).astype(float)
    w = np.exp(-0.5 * dist * dist) * np.exp(-math.log(2.0) * ages / half)
    ess = effective_sample_size(w)
    if ess < min_ess:
        return None

    y = actual[idx].astype(int)
    s = expert_signal[idx].astype(int)
    wp = float(w[y == 1].sum())
    wn = float(w[y == -1].sum())
    if wp <= 0 or wn <= 0:
        return None

    hit_up = float(w[(y == 1) & (s == 1)].sum() / wp)
    hit_down = float(w[(y == -1) & (s == -1)].sum() / wn)
    balanced = 0.5 * (hit_up + hit_down)
    sw = float(w.sum())
    pred_up = float(w[s == 1].sum() / sw)
    pred_down = float(w[s == -1].sum() / sw)
    degeneracy = 2.0 * min(pred_up, pred_down)
    support = min(1.0, ess / full_ess)
    score = max(0.0, 2.0 * balanced - 1.0) * degeneracy * support
    return {
        "score": float(score),
        "balanced_accuracy": float(balanced),
        "degeneracy_penalty": float(degeneracy),
        "effective_n": float(ess),
        "neighbors": int(len(idx)),
    }


def run_crase(panel: pd.DataFrame, contract: dict) -> pd.DataFrame:
    h = int(contract["horizon"])
    p = panel.copy().sort_values("date").reset_index(drop=True)
    experts = list(contract["experts"])
    regime = list(contract["regime_features"])
    for col in regime + experts:
        if col not in p.columns:
            raise RuntimeError(f"V162_REQUIRED_COLUMN_MISSING:{col}")

    x = p[regime].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    actual = p["future_direction"].to_numpy(float)
    target_dates = p["target_date"].to_numpy(dtype="datetime64[ns]")
    dates = p["date"].to_numpy(dtype="datetime64[ns]")
    emat = {e: p[e].to_numpy(int) for e in experts}
    hist_cap = int(contract["similarity"]["history_cap"])
    min_rel = float(contract["aggregation"]["minimum_total_reliability"])
    min_abs = float(contract["aggregation"]["minimum_absolute_direction_score"])
    start = pd.Timestamp(contract["windows"]["formation_start"])

    rows: list[dict] = []
    for t in range(len(p) - h):
        if pd.Timestamp(p.loc[t, "date"]) < start:
            continue
        hist = x[max(0, t - hist_cap):t]
        med, iqr = robust_center_scale(hist)
        num = 0.0
        den = 0.0
        diag: dict[str, dict | None] = {}
        for e in experts:
            cur = int(emat[e][t])
            if cur == 0:
                diag[e] = None
                continue
            r = local_reliability(t, emat[e], actual, target_dates, dates, x, med, iqr, contract)
            diag[e] = r
            if r is not None and r["score"] > 0:
                num += float(r["score"]) * cur
                den += float(r["score"])
        direction_score = num / den if den > 0 else 0.0
        signal = 0
        if den >= min_rel and abs(direction_score) >= min_abs:
            signal = 1 if direction_score > 0 else -1
        row = {
            "origin_index": int(t),
            "origin_date": p.loc[t, "date"],
            "target_date": p.loc[t, "target_date"],
            "target_return": float(p.loc[t, "target_return"]),
            "future_direction": int(p.loc[t, "future_direction"]),
            "signal": int(signal),
            "direction_score": float(direction_score),
            "total_reliability": float(den),
        }
        for e in experts:
            row[f"{e}_current"] = int(emat[e][t])
            row[f"{e}_reliability"] = None if diag[e] is None else float(diag[e]["score"])
            row[f"{e}_local_balanced_accuracy"] = None if diag[e] is None else float(diag[e]["balanced_accuracy"])
            row[f"{e}_effective_n"] = None if diag[e] is None else float(diag[e]["effective_n"])
        rows.append(row)
    return pd.DataFrame(rows)


def period_slice(d: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return d[(d["origin_date"] >= a) & (d["origin_date"] <= b) & (d["target_date"] <= b)].copy()


def metrics(d: pd.DataFrame) -> dict:
    if d.empty:
        return {"n": 0, "selective_n": 0, "coverage": 0.0, "status": "BLOCKED_EMPTY"}
    take = d["signal"].astype(int).ne(0)
    g = d[take].copy()
    out = {"n": int(len(d)), "selective_n": int(len(g)), "coverage": float(take.mean())}
    if g.empty:
        out.update({"status": "NO_SIGNAL", "accuracy": None, "balanced_accuracy": None, "mcc": None, "up_signals": 0, "down_signals": 0, "median_signed_return": None})
        return out
    y = (g["future_direction"].astype(int) > 0).astype(int)
    s = (g["signal"].astype(int) > 0).astype(int)
    out.update({
        "status": "OK",
        "accuracy": float(accuracy_score(y, s)),
        "balanced_accuracy": float(balanced_accuracy_score(y, s)),
        "mcc": float(matthews_corrcoef(y, s)),
        "up_signals": int((g["signal"] > 0).sum()),
        "down_signals": int((g["signal"] < 0).sum()),
        "realized_up": int((g["future_direction"] > 0).sum()),
        "realized_down": int((g["future_direction"] < 0).sum()),
        "median_signed_return": float(np.median(g["target_return"].to_numpy(float) * g["signal"].to_numpy(int))),
    })
    return out


def score_periods(d: pd.DataFrame, contract: dict) -> dict:
    w = contract["windows"]
    return {
        "FORMATION_2024": metrics(period_slice(d, w["formation_start"], w["formation_end"])),
        "VALIDATION_2025": metrics(period_slice(d, w["validation_start"], w["validation_end"])),
        "TEST_2026_AVAILABLE": metrics(period_slice(d, w["test_start"], w["test_end"])),
    }


def gate(scored: dict, contract: dict) -> dict:
    c = contract["evaluation"]["support_gate"]
    v = scored["VALIDATION_2025"]
    t = scored["TEST_2026_AVAILABLE"]
    checks = {
        "validation_coverage": v.get("coverage", 0.0) >= float(c["validation_coverage_min"]),
        "validation_balanced": (v.get("balanced_accuracy") or 0.0) >= float(c["validation_balanced_accuracy_min"]),
        "validation_mcc": (v.get("mcc") or 0.0) > float(c["validation_mcc_strictly_above"]),
        "validation_both_directions": v.get("up_signals", 0) > 0 and v.get("down_signals", 0) > 0,
        "test_coverage": t.get("coverage", 0.0) >= float(c["test_coverage_min"]),
        "test_balanced": (t.get("balanced_accuracy") or 0.0) >= float(c["test_balanced_accuracy_min"]),
        "test_mcc": (t.get("mcc") or 0.0) > float(c["test_mcc_strictly_above"]),
        "test_both_directions": t.get("up_signals", 0) > 0 and t.get("down_signals", 0) > 0,
    }
    return {"pass": bool(all(checks.values())), "checks": checks}


def main() -> int:
    contract = load_contract()
    database_url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not database_url:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")

    raw_panel, parent_predictions, evidence = build_research_surface(database_url, contract)
    panel = prepare_experts(raw_panel, parent_predictions, h=int(contract["horizon"]))
    pred = run_crase(panel, contract)
    scored = score_periods(pred, contract)
    support = gate(scored, contract)

    result = {
        "contract_id": contract["contract_id"],
        "method_name": contract["method_name"],
        "status": "RETROSPECTIVE_METHOD_DEVELOPMENT_DIAGNOSTIC_COMPLETE",
        "evidence_class": contract["evidence_class"],
        "production_authority": False,
        "novelty_status": contract["novelty_status"],
        "results": scored,
        "support_gate": support,
        "source_evidence": evidence,
        "interpretation_lock": {
            "not_claimed_novel_yet": True,
            "2025_2026_researcher_visible": True,
            "post_score_repair_inside_v162_forbidden": True,
            "future_prospective_shadow_required_even_if_gate_passes": True,
            "no_production_authority": True,
        },
    }

    OUT.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT / "v162_panel_with_experts.csv", index=False)
    pred.to_csv(OUT / "v162_crase_predictions.csv", index=False)
    parent_predictions.to_csv(OUT / "v162_parent_predictions.csv", index=False)
    (OUT / "v162_results.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
