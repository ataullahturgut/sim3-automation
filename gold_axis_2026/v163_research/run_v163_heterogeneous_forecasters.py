from __future__ import annotations

import json
import math
import os
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, log_loss, matthews_corrcoef
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from gold_axis_2026.v149_thesis.run_rich_short_horizon import B0, load_panel
from gold_axis_2026.v157_thesis import run_v157_breakaware_realized_moments as v157
from gold_axis_2026.v161_thesis import run_v161_short_horizon_price_discovery as v161

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v163_research/contracts/v163_heterogeneous_forecasters_freeze_v1.json"
V157_CONTRACT = ROOT / "v157_thesis/contracts/v157_breakaware_realized_moments_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v163_research"
SEED = 20260913

GOLD = list(B0)
SESSION_RM = [
    "europe_session_ret", "us_morning_ret", "post_0829_ret",
    "rm_vol", "rm_rsv_neg", "rm_rsv_pos", "rm_downside_share",
    "rm_skew", "rm_kurt", "rm_jump_fraction", "rm_max_abs",
]
PRICE_DISCOVERY = [
    "gc_ret1", "gc_ret3", "gc_ret5", "gc_range1", "gc_oc1", "gc_vol5", "gc_vol20", "gc_volume_z20", "gc_basis_prev",
    "gld_ret1", "gld_ret3", "gld_ret5", "gld_range1", "gld_oc1", "gld_vol5", "gld_vol20", "gld_volume_z20",
]
MACRO_CROSS = [
    "nasdaq_ret", "sp500_ret", "xag_ret", "xpt_ret", "xpd_ret",
    "broad_usd_level", "broad_usd_logdiff1", "broad_usd_logdiff5",
    "real10_level", "real10_delta1", "real10_delta5",
]
ROLE_CONTEXT = ["fast_state_encoded", "slow_state_encoded", "monthly_direction_3m_encoded"]
FULL = GOLD + SESSION_RM + PRICE_DISCOVERY + MACRO_CROSS + ROLE_CONTEXT

EXPERTS = {
    "GOLD_RIDGE": ("ridge", GOLD),
    "SESSION_RM_RIDGE": ("ridge", SESSION_RM),
    "PRICE_DISCOVERY_HGB": ("hgb", PRICE_DISCOVERY),
    "MACRO_CROSS_RIDGE": ("ridge", MACRO_CROSS),
    "FULL_HGB": ("hgb", FULL),
}

ROLE_MAP = {
    "fast_state": {"ROBUST_UP": 1.0, "ROBUST_DOWN": -1.0, "MIXED": 0.0, "NOT_YET_ROBUST": 0.0},
    "slow_state": {"ROBUST_UP": 1.0, "ROBUST_DOWN": -1.0, "MIXED": 0.0, "NOT_YET_ROBUST": 0.0},
    "monthly_direction_3m": {"UP": 1.0, "DOWN": -1.0, "NEUTRAL": 0.0},
}


def load_contract() -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_ANY_V163_SCORING":
        raise RuntimeError("V163_CONTRACT_NOT_FROZEN")
    g = c["governance"]
    if g["AUTO_SELECTOR"] != "OFF" or g["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V163_GOVERNANCE_LOCK_FAIL")
    if c["evaluation"]["meta_selector_scoring_in_v163"] != "FORBIDDEN":
        raise RuntimeError("V163_SELECTOR_MUST_REMAIN_FORBIDDEN")
    return c


def _encode_roles(d: pd.DataFrame) -> pd.DataFrame:
    z = d.copy()
    for col, mapping in ROLE_MAP.items():
        z[f"{col}_encoded"] = z[col].map(mapping).fillna(0.0).astype(float) if col in z.columns else 0.0
    return z


def build_panel(conn, contract: dict) -> tuple[pd.DataFrame, dict]:
    ny17 = _encode_roles(load_panel(conn))
    ny17["date"] = pd.to_datetime(ny17["date"]).dt.tz_localize(None).dt.normalize()

    v157_contract = json.loads(V157_CONTRACT.read_text(encoding="utf-8"))
    rich, _, _, _ = v157.build_panel(conn, v157_contract)
    rich, fed_evidence = v161.add_corrected_macro(rich, contract)
    gc, gc_evidence = v161.fetch_yahoo_daily("GC=F", "2022-01-01", contract["windows"]["test_end"])
    gld, gld_evidence = v161.fetch_yahoo_daily("GLD", "2022-01-01", contract["windows"]["test_end"])
    rich = v161.add_price_discovery(rich, gc, gld)
    rich["date"] = pd.to_datetime(rich["date"]).dt.tz_localize(None).dt.normalize()

    needed = sorted(set(SESSION_RM + PRICE_DISCOVERY + MACRO_CROSS))
    missing = [c for c in needed if c not in rich.columns]
    if missing:
        raise RuntimeError(f"V163_RICH_FEATURES_MISSING:{missing}")
    r = rich[["date"] + needed].drop_duplicates("date", keep="last")

    # Some V1.49 NY17 research columns use the same names as the richer V1.61
    # reconstruction. The frozen V1.63 contract requires the V1.61 versions, so
    # remove only those colliding feature columns before the identical-date merge.
    overlap = [c for c in needed if c in ny17.columns]
    ny17 = ny17.drop(columns=overlap)
    z = ny17.merge(r, on="date", how="left", validate="one_to_one")
    evidence = {
        "GC=F": gc_evidence,
        "GLD": gld_evidence,
        "fed": fed_evidence,
        "rich_rows": int(len(rich)),
        "ny17_rows": int(len(ny17)),
        "merged_rows": int(len(z)),
        "replaced_ny17_name_collisions_with_v161_rich_features": overlap,
    }
    return z.sort_values("date").reset_index(drop=True), evidence


def make_model(kind: str):
    if kind == "ridge":
        return make_pipeline(
            SimpleImputer(strategy="median", keep_empty_features=True),
            StandardScaler(),
            LogisticRegression(C=1.0, max_iter=2000, random_state=SEED),
        )
    if kind == "hgb":
        return make_pipeline(
            SimpleImputer(strategy="median", keep_empty_features=True),
            HistGradientBoostingClassifier(
                max_depth=2, max_iter=100, learning_rate=0.05,
                l2_regularization=1.0, random_state=SEED,
            ),
        )
    raise ValueError(kind)


def target_series(d: pd.DataFrame, h: int) -> tuple[pd.Series, pd.Series, pd.Series]:
    ret = np.log(d["close"].shift(-h) / d["close"])
    y = (ret > 0).astype(float)
    y.iloc[-h:] = np.nan
    target_date = d["date"].shift(-h)
    return y, ret, target_date


def matured_indices(y: pd.Series, t: int, h: int, cap: int) -> list[int]:
    idx = [j for j in range(t) if j + h <= t and pd.notna(y.iloc[j])]
    return idx[-cap:]


def sequential_expert(d: pd.DataFrame, h: int, expert: str, kind: str, features: list[str], contract: dict) -> pd.DataFrame:
    y, ret, target_date = target_series(d, h)
    missing = [c for c in features if c not in d.columns]
    if missing:
        raise RuntimeError(f"V163_EXPERT_FEATURES_MISSING:{expert}:{missing}")
    cap = int(contract["training"]["rolling_window"])
    min_n = int(contract["training"]["minimum_mature_targets"])
    start = pd.Timestamp(contract["windows"]["formation_start"])
    rows = []
    for t in range(len(d) - h):
        if d.loc[t, "date"] < start:
            continue
        idx = matured_indices(y, t, h, cap)
        if len(idx) < min_n:
            continue
        yy = y.iloc[idx].astype(int)
        if yy.nunique() < 2:
            continue
        m = make_model(kind)
        m.fit(d.loc[idx, features], yy)
        p = float(m.predict_proba(d.loc[[t], features])[0, 1])
        p = float(np.clip(p, 1e-6, 1 - 1e-6))
        freq_idx = [j for j in range(t) if j + h <= t and pd.notna(y.iloc[j])]
        freq = float((y.iloc[freq_idx].sum() + 0.5) / (len(freq_idx) + 1.0))
        rows.append({
            "expert": expert,
            "origin_index": int(t),
            "origin_date": d.loc[t, "date"],
            "target_date": target_date.iloc[t],
            "horizon": int(h),
            "y": int(y.iloc[t]),
            "return": float(ret.iloc[t]),
            "p": p,
            "p50": 0.5,
            "pfreq": freq,
            "train_n": int(len(idx)),
            "feature_missing_fraction": float(d.loc[t, features].isna().mean()),
        })
    return pd.DataFrame(rows)


def common_matrix(predictions: dict[str, pd.DataFrame]) -> pd.DataFrame:
    out = None
    keys = ["origin_index", "origin_date", "target_date", "horizon", "y", "return", "p50", "pfreq"]
    for expert, f in predictions.items():
        x = f[keys + ["p", "train_n", "feature_missing_fraction"]].rename(columns={
            "p": f"p_{expert}", "train_n": f"train_n_{expert}", "feature_missing_fraction": f"missing_{expert}",
        })
        if out is None:
            out = x
        else:
            out = out.merge(x, on=keys, how="inner", validate="one_to_one")
    return out if out is not None else pd.DataFrame()


def metric_block(f: pd.DataFrame, col: str) -> dict:
    z = f[["y", col]].dropna()
    if z.empty:
        return {"n": 0, "status": "EMPTY"}
    y = z["y"].to_numpy(int)
    p = np.clip(z[col].to_numpy(float), 1e-9, 1 - 1e-9)
    pred = (p >= 0.5).astype(int)
    return {
        "n": int(len(z)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)) if len(np.unique(y)) == 2 else None,
        "mcc": float(matthews_corrcoef(y, pred)) if len(np.unique(y)) == 2 and len(np.unique(pred)) == 2 else 0.0,
        "up_predictions": int(pred.sum()),
        "down_predictions": int((1 - pred).sum()),
        "actual_up": int(y.sum()),
        "actual_down": int((1 - y).sum()),
    }


def period_slice(f: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    od = pd.to_datetime(f["origin_date"])
    td = pd.to_datetime(f["target_date"])
    return f[(od >= a) & (od <= b) & (td <= b)].copy()


def period_metrics(f: pd.DataFrame, contract: dict) -> dict:
    w = contract["windows"]
    periods = {
        "FORMATION_2024": period_slice(f, w["formation_start"], w["formation_end"]),
        "VALIDATION_2025": period_slice(f, w["validation_start"], w["validation_end"]),
        "TEST_2026_AVAILABLE": period_slice(f, w["test_start"], w["test_end"]),
    }
    out = {}
    for name, g in periods.items():
        row = {"P50": metric_block(g, "p50"), "FREQ": metric_block(g, "pfreq")}
        for e in EXPERTS:
            row[e] = metric_block(g, f"p_{e}")
        out[name] = row
    return out


def skill_gate(periods: dict, contract: dict) -> dict:
    gate = contract["evaluation"]["expert_skill_gate_each_of_validation_and_test"]
    out = {}
    for e in EXPERTS:
        checks = {}
        for period in ["VALIDATION_2025", "TEST_2026_AVAILABLE"]:
            m = periods[period][e]
            a = periods[period]["FREQ"]
            checks[period] = {
                "brier_improvement": float(a["brier"] - m["brier"]),
                "brier_pass": (a["brier"] - m["brier"]) >= float(gate["brier_improvement_vs_frequency_min"]),
                "log_loss_pass": m["log_loss"] <= a["log_loss"],
                "balanced_pass": (m.get("balanced_accuracy") or 0.0) >= float(gate["balanced_accuracy_min"]),
                "mcc_pass": (m.get("mcc") or 0.0) > 0.0,
                "both_directions_pass": m.get("up_predictions", 0) > 0 and m.get("down_predictions", 0) > 0,
            }
            checks[period]["pass"] = bool(all(v for k, v in checks[period].items() if k.endswith("_pass")))
        out[e] = {"periods": checks, "pass": bool(all(checks[p]["pass"] for p in checks))}
    return out


def diversity_audit(f: pd.DataFrame, skill: dict, contract: dict) -> dict:
    w = contract["windows"]
    z = pd.concat([
        period_slice(f, w["validation_start"], w["validation_end"]),
        period_slice(f, w["test_start"], w["test_end"]),
    ], ignore_index=True)
    skilled = [e for e, x in skill.items() if x["pass"]]
    g = contract["evaluation"]["diversity_gate"]
    pairs = {}
    eligible_pairs = []
    for a, b in combinations(skilled, 2):
        pa = z[f"p_{a}"].to_numpy(float)
        pb = z[f"p_{b}"].to_numpy(float)
        y = z["y"].to_numpy(float)
        la = np.square(pa - y)
        lb = np.square(pb - y)
        pcorr = float(np.corrcoef(pa, pb)[0, 1]) if len(z) > 2 else math.nan
        lcorr = float(np.corrcoef(la, lb)[0, 1]) if len(z) > 2 else math.nan
        a_win = float(np.mean(la < lb))
        b_win = float(np.mean(lb < la))
        checks = {
            "probability_corr_pass": bool(np.isfinite(pcorr) and pcorr <= float(g["pair_probability_correlation_max"])),
            "brier_residual_corr_pass": bool(np.isfinite(lcorr) and lcorr <= float(g["pair_brier_residual_correlation_max"])),
            "a_unique_win_pass": a_win >= float(g["minimum_each_expert_unique_win_share"]),
            "b_unique_win_pass": b_win >= float(g["minimum_each_expert_unique_win_share"]),
        }
        passed = bool(all(checks.values()))
        key = f"{a}__{b}"
        pairs[key] = {
            "n": int(len(z)), "probability_correlation": pcorr, "brier_residual_correlation": lcorr,
            "a_unique_win_share": a_win, "b_unique_win_share": b_win, "checks": checks, "pass": passed,
        }
        if passed:
            eligible_pairs.append([a, b])
    selector_eligible = len(skilled) >= int(g["minimum_skill_passing_experts"]) and bool(eligible_pairs)
    return {
        "skill_passing_experts": skilled,
        "pairwise": pairs,
        "eligible_pairs": eligible_pairs,
        "selector_eligible_for_future_version": bool(selector_eligible),
        "selector_scored_in_v163": False,
    }


def main() -> int:
    contract = load_contract()
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")
    OUT.mkdir(parents=True, exist_ok=True)
    with psycopg.connect(db, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
        panel, source_evidence = build_panel(conn, contract)

    result = {
        "contract_id": contract["contract_id"],
        "status": "RETROSPECTIVE_HETEROGENEOUS_FORECASTER_AUDIT_COMPLETE",
        "evidence_class": contract["evidence_class"],
        "source_evidence": source_evidence,
        "origin_rows": int(len(panel)),
        "experts": {e: {"model": k, "features": f} for e, (k, f) in EXPERTS.items()},
        "horizons": {},
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "production_authority": False,
        "production_writes": "NONE",
    }

    for h in [1, 3]:
        preds = {}
        for e, (kind, features) in EXPERTS.items():
            p = sequential_expert(panel, h, e, kind, features, contract)
            if p.empty:
                raise RuntimeError(f"V163_EMPTY_EXPERT:{h}:{e}")
            preds[e] = p
        common = common_matrix(preds)
        if common.empty:
            raise RuntimeError(f"V163_EMPTY_COMMON_MATRIX:{h}")
        common.to_csv(OUT / f"v163_{h}d_common_predictions.csv", index=False)
        for e, p in preds.items():
            p.to_csv(OUT / f"v163_{h}d_{e.lower()}_predictions.csv", index=False)
        pm = period_metrics(common, contract)
        sg = skill_gate(pm, contract)
        da = diversity_audit(common, sg, contract)
        result["horizons"][f"{h}D"] = {
            "common_rows": int(len(common)),
            "period_metrics": pm,
            "skill_gate": sg,
            "diversity_audit": da,
        }

    (OUT / "v163_heterogeneous_forecasters_results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
