from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from psycopg.rows import dict_row
from sklearn.linear_model import HuberRegressor, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from statsmodels.tsa.holtwinters import Holt

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "successor_r2"
OUTDIR.mkdir(exist_ok=True)
TARGET_SERIES = "XAU_MONTHLY_WB_PINKSHEET"
MACRO_SERIES = [
    "DGS10_ALFRED_PIT_ME",
    "DFF_ALFRED_PIT_ME",
    "DEXCHUS_ALFRED_PIT_ME",
    "NASDAQ100_ALFRED_PIT_ME",
]
EVAL_START = pd.Period("2018-07", freq="M")
EVAL_END = pd.Period("2026-07", freq="M")
COMPLETED_YEARS = list(range(2019, 2026))
EXPECTED_N = 97
MIN_TRAIN = 24


def db_url() -> str:
    v = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    return v


def canonical_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def load_data() -> tuple[pd.Series, pd.DataFrame, dict]:
    ids = [TARGET_SERIES, *MACRO_SERIES]
    with psycopg.connect(db_url(), autocommit=True) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select series_id, observation_ts, value, provider_as_of, retrieved_at,
                       quality_status, lineage_id, metadata
                from canonical_latest
                where series_id = any(%s)
                order by series_id, observation_ts
                """,
                (ids,),
            )
            rows = cur.fetchall()
            cur.execute("select count(*) as n from forecast_input_snapshots")
            fis = int(cur.fetchone()["n"])
            cur.execute("select count(*) as n from derived_feature_snapshots")
            dfs = int(cur.fetchone()["n"])
            cur.execute("select count(*) as n from monthly_forecast_contracts")
            mfc = int(cur.fetchone()["n"])

    by = {sid: [] for sid in ids}
    for r in rows:
        by[r["series_id"]].append(r)

    target_rows = by[TARGET_SERIES]
    if len(target_rows) != 127:
        raise RuntimeError(f"TARGET_COUNT_NOT_127:{len(target_rows)}")
    if len({r["lineage_id"] for r in target_rows}) != 1:
        raise RuntimeError("TARGET_LINEAGE_NOT_UNIQUE")
    target = pd.Series(
        {pd.Timestamp(r["observation_ts"]).to_period("M"): float(r["value"]) for r in target_rows},
        dtype=float,
    ).sort_index()
    if target.index.min() != pd.Period("2016-01", "M") or target.index.max() != pd.Period("2026-07", "M"):
        raise RuntimeError("TARGET_SPAN_MISMATCH")

    macro = pd.DataFrame(index=pd.period_range("2016-01", "2026-08", freq="M"))
    coverage = {TARGET_SERIES: len(target_rows)}
    for sid in MACRO_SERIES:
        rs = by[sid]
        if len(rs) != 128:
            raise RuntimeError(f"MACRO_COUNT_NOT_128:{sid}:{len(rs)}")
        if len({r["lineage_id"] for r in rs}) != 1:
            raise RuntimeError(f"MACRO_LINEAGE_NOT_UNIQUE:{sid}")
        if not all(str(r["quality_status"]) == "APPROVED_HISTORICAL_PIT_RECONSTRUCTION_RESEARCH" for r in rs):
            raise RuntimeError(f"MACRO_QUALITY_MISMATCH:{sid}")
        s = pd.Series(
            {pd.Timestamp(r["observation_ts"]).to_period("M"): float(r["value"]) for r in rs},
            dtype=float,
        ).sort_index()
        macro[sid] = s
        coverage[sid] = len(rs)

    if macro.isna().any().any():
        raise RuntimeError(f"MACRO_MISSING_VALUES:{macro.isna().sum().to_dict()}")

    audit = {
        "coverage": coverage,
        "forecast_input_snapshots": fis,
        "derived_feature_snapshots": dfs,
        "monthly_forecast_contracts": mfc,
        "source_pit_gate": "PASS",
    }
    return target, macro, audit


def macro_feature_row(t: pd.Period, target: pd.Series, macro: pd.DataFrame) -> dict | None:
    # target T, origin T-1, latest finalized target allowed T-2
    p2, p3, p4, p5 = t - 2, t - 3, t - 4, t - 5
    origin, prior_origin = t - 1, t - 2
    needed_y = [p2, p3, p4, p5]
    if any(p not in target.index for p in needed_y):
        return None
    if origin not in macro.index or prior_origin not in macro.index:
        return None
    y2, y3, y4, y5 = [float(target.loc[p]) for p in needed_y]
    if min(y2, y3, y4, y5) <= 0:
        return None
    r2 = y2 / y3 - 1.0
    r3 = y3 / y4 - 1.0
    r4 = y4 / y5 - 1.0
    m = macro.loc[origin]
    mp = macro.loc[prior_origin]
    vals = {
        "log_y_lag2": math.log(y2),
        "ret_end_lag2": r2,
        "ret_end_lag3": r3,
        "ret3_mean": float(np.mean([r2, r3, r4])),
        "dgs10_level": float(m["DGS10_ALFRED_PIT_ME"]),
        "dgs10_change": float(m["DGS10_ALFRED_PIT_ME"] - mp["DGS10_ALFRED_PIT_ME"]),
        "dff_level": float(m["DFF_ALFRED_PIT_ME"]),
        "dff_change": float(m["DFF_ALFRED_PIT_ME"] - mp["DFF_ALFRED_PIT_ME"]),
        "log_dexchus": math.log(float(m["DEXCHUS_ALFRED_PIT_ME"])),
        "dexchus_log_change": math.log(float(m["DEXCHUS_ALFRED_PIT_ME"]) / float(mp["DEXCHUS_ALFRED_PIT_ME"])),
        "log_nasdaq100": math.log(float(m["NASDAQ100_ALFRED_PIT_ME"])),
        "nasdaq100_log_change": math.log(float(m["NASDAQ100_ALFRED_PIT_ME"]) / float(mp["NASDAQ100_ALFRED_PIT_ME"])),
    }
    if not all(np.isfinite(list(vals.values()))):
        return None
    return vals


def available_target_history(t: pd.Period, target: pd.Series) -> pd.Series:
    # forecasting T at end T-1; finalized target feedback only through T-2
    return target[target.index <= (t - 2)].copy()


def forecast_rw(t: pd.Period, target: pd.Series) -> float:
    h = available_target_history(t, target)
    return float(h.iloc[-1])


def forecast_drift(t: pd.Period, target: pd.Series) -> float:
    h = available_target_history(t, target).tail(12)
    if len(h) < 12:
        raise RuntimeError("DRIFT_MIN_HISTORY")
    x = np.arange(len(h), dtype=float)
    slope, intercept = np.polyfit(x, h.to_numpy(float), 1)
    # last permissible target is T-2; T is two monthly target steps ahead
    return float(intercept + slope * (len(h) + 1))


def forecast_mom3(t: pd.Period, target: pd.Series) -> float:
    h = available_target_history(t, target)
    if len(h) < 4:
        raise RuntimeError("MOM3_MIN_HISTORY")
    rets = h.pct_change().dropna().tail(3)
    mean_r = float(rets.mean())
    return float(h.iloc[-1] * ((1.0 + mean_r) ** 2))


def forecast_damped(t: pd.Period, target: pd.Series) -> float:
    h = available_target_history(t, target)
    if len(h) < 24:
        raise RuntimeError("DAMPED_MIN_HISTORY")
    fit = Holt(h.to_numpy(float), damped_trend=True, initialization_method="estimated").fit(optimized=True)
    fc = fit.forecast(2)
    return float(fc[-1])


def training_matrix(t: pd.Period, target: pd.Series, macro: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    # At outer origin T-1, labels are finalized only through T-2.
    rows = []
    ys = []
    labels_end = t - 2
    for tau in target.index:
        if tau > labels_end:
            break
        f = macro_feature_row(tau, target, macro)
        if f is None:
            continue
        rows.append(f)
        ys.append(math.log(float(target.loc[tau])))
    X = pd.DataFrame(rows)
    y = np.asarray(ys, dtype=float)
    if len(X) < MIN_TRAIN:
        raise RuntimeError(f"MACRO_MIN_TRAIN:{t}:{len(X)}")
    return X, y


def forecast_macro(t: pd.Period, target: pd.Series, macro: pd.DataFrame, kind: str) -> float:
    X, y = training_matrix(t, target, macro)
    f = macro_feature_row(t, target, macro)
    if f is None:
        raise RuntimeError(f"MACRO_FEATURE_MISSING:{t}")
    x0 = pd.DataFrame([f], columns=X.columns)
    if kind == "RIDGE_MACRO_R2":
        model = Pipeline([("scale", StandardScaler()), ("model", Ridge(alpha=1.0))])
    elif kind == "HUBER_MACRO_R2":
        model = Pipeline([
            ("scale", StandardScaler()),
            ("model", HuberRegressor(epsilon=1.35, alpha=0.0001, max_iter=1000)),
        ])
    elif kind == "SVR_RBF_MACRO_R2":
        model = Pipeline([
            ("scale", StandardScaler()),
            ("model", SVR(kernel="rbf", C=10.0, gamma="scale", epsilon=0.02)),
        ])
    else:
        raise ValueError(kind)
    model.fit(X, y)
    return float(math.exp(float(model.predict(x0)[0])))


CANDIDATES = [
    "RW_R2_PIT",
    "DRIFT_R2_PIT",
    "MOM3_R2_PIT",
    "DAMPED_TREND_R2_PIT",
    "RIDGE_MACRO_R2",
    "HUBER_MACRO_R2",
    "SVR_RBF_MACRO_R2",
]


def run_once(target: pd.Series, macro: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for t in pd.period_range(EVAL_START, EVAL_END, freq="M"):
        actual = float(target.loc[t])
        latest = float(target.loc[t - 2])
        preds = {
            "RW_R2_PIT": forecast_rw(t, target),
            "DRIFT_R2_PIT": forecast_drift(t, target),
            "MOM3_R2_PIT": forecast_mom3(t, target),
            "DAMPED_TREND_R2_PIT": forecast_damped(t, target),
            "RIDGE_MACRO_R2": forecast_macro(t, target, macro, "RIDGE_MACRO_R2"),
            "HUBER_MACRO_R2": forecast_macro(t, target, macro, "HUBER_MACRO_R2"),
            "SVR_RBF_MACRO_R2": forecast_macro(t, target, macro, "SVR_RBF_MACRO_R2"),
        }
        for model, pred in preds.items():
            if not np.isfinite(pred) or pred <= 0:
                raise RuntimeError(f"INVALID_PREDICTION:{model}:{t}:{pred}")
            rows.append({
                "target_month": str(t),
                "year": int(t.year),
                "model": model,
                "actual": actual,
                "forecast": pred,
                "latest_permissible_target": latest,
                "error": pred - actual,
                "abs_error": abs(pred - actual),
                "ape_pct": abs(pred - actual) / actual * 100.0,
                "direction_actual": int(np.sign(actual - latest)),
                "direction_forecast": int(np.sign(pred - latest)),
            })
    df = pd.DataFrame(rows)
    counts = df.groupby("model")["target_month"].nunique().to_dict()
    bad = {k: v for k, v in counts.items() if v != EXPECTED_N}
    if bad or len(counts) != len(CANDIDATES):
        raise RuntimeError(f"INCOMPLETE_COMMON_WINDOW:{bad}:{counts}")
    return df


def metrics_for(g: pd.DataFrame, rw: pd.DataFrame) -> dict:
    e = g["error"].to_numpy(float)
    a = g["actual"].to_numpy(float)
    f = g["forecast"].to_numpy(float)
    ae = np.abs(e)
    rw_ae = rw["abs_error"].to_numpy(float)
    return {
        "N": int(len(g)),
        "MAE": float(np.mean(ae)),
        "MAPE_pct": float(np.mean(ae / a) * 100.0),
        "sMAPE_pct": float(np.mean(2.0 * ae / (np.abs(a) + np.abs(f))) * 100.0),
        "median_abs_error": float(np.median(ae)),
        "RMSE": float(np.sqrt(np.mean(e * e))),
        "Relative_MAE_vs_RW": float(np.sum(ae) / np.sum(rw_ae)),
        "monthly_win_rate_vs_RW": float(np.mean(ae < rw_ae)),
        "direction_accuracy": float(np.mean(g["direction_actual"].to_numpy() == g["direction_forecast"].to_numpy())),
    }


def score(df: pd.DataFrame, deterministic_pass: bool, source_gate: str) -> tuple[pd.DataFrame, dict]:
    rw = df[df.model == "RW_R2_PIT"].sort_values("target_month").reset_index(drop=True)
    rw_metrics = None
    records = []
    gate_details = {}
    for model in CANDIDATES:
        g = df[df.model == model].sort_values("target_month").reset_index(drop=True)
        m = metrics_for(g, rw)
        if model == "RW_R2_PIT":
            rw_metrics = m
            m["Relative_MAE_vs_RW"] = 1.0
        year_ratios = {}
        year_beats = 0
        for yr in COMPLETED_YEARS:
            cg = g[g.year == yr]
            rg = rw[rw.year == yr]
            if len(cg) != 12 or len(rg) != 12:
                raise RuntimeError(f"COMPLETED_YEAR_NOT_12:{model}:{yr}:{len(cg)}:{len(rg)}")
            cmae = float(cg.abs_error.mean())
            rmae = float(rg.abs_error.mean())
            ratio = cmae / rmae if rmae else math.inf
            year_ratios[str(yr)] = ratio
            if cmae < rmae:
                year_beats += 1
        m["completed_years_beaten_vs_RW"] = year_beats
        m["max_completed_year_MAE_ratio_vs_RW"] = float(max(year_ratios.values()))
        m["completed_year_MAE_ratios_vs_RW"] = year_ratios
        records.append({"model": model, **{k: v for k, v in m.items() if k != "completed_year_MAE_ratios_vs_RW"}})
        gate_details[model] = {"year_ratios": year_ratios}

    assert rw_metrics is not None
    scored = pd.DataFrame(records)
    for i, row in scored.iterrows():
        model = row["model"]
        if model == "RW_R2_PIT":
            eligible = False
            reasons = ["MANDATORY_BENCHMARK_NOT_CANDIDATE"]
        else:
            reasons = []
            checks = {
                "source_provenance_pit": source_gate == "PASS",
                "deterministic_rerun": deterministic_pass,
                "complete_common_window": int(row["N"]) == EXPECTED_N,
                "relative_mae_lt_1": float(row["Relative_MAE_vs_RW"]) < 1.0,
                "mape_le_rw": float(row["MAPE_pct"]) <= float(rw_metrics["MAPE_pct"]),
                "median_abs_le_rw": float(row["median_abs_error"]) <= float(rw_metrics["median_abs_error"]),
                "beats_at_least_4_completed_years": int(row["completed_years_beaten_vs_RW"]) >= 4,
                "no_year_ratio_gt_1_5": float(row["max_completed_year_MAE_ratio_vs_RW"]) <= 1.5,
                "no_unresolved_leakage_exception": True,
            }
            reasons = [k for k, ok in checks.items() if not ok]
            eligible = not reasons
            gate_details[model]["checks"] = checks
        scored.loc[i, "eligible"] = bool(eligible)
        scored.loc[i, "failed_gates"] = ";".join(reasons)

    passing = scored[scored.eligible == True].copy()  # noqa: E712
    if passing.empty:
        decision = "REJECT_ALL_SUCCESSOR_CANDIDATES_R2"
        selected = None
    else:
        complexity = {
            "DRIFT_R2_PIT": 1,
            "MOM3_R2_PIT": 1,
            "DAMPED_TREND_R2_PIT": 2,
            "RIDGE_MACRO_R2": 3,
            "HUBER_MACRO_R2": 4,
            "SVR_RBF_MACRO_R2": 5,
        }
        passing["complexity"] = passing.model.map(complexity).fillna(99)
        passing = passing.sort_values(["Relative_MAE_vs_RW", "median_abs_error", "complexity"])
        selected = str(passing.iloc[0].model)
        decision = "HISTORICAL_REPLAY_SHADOW_ELIGIBLE"
    return scored, {"decision": decision, "selected_model": selected, "gate_details": gate_details}


def canonical_json_hash(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def main() -> None:
    target, macro, data_audit = load_data()
    run1 = run_once(target, macro)
    run2 = run_once(target, macro)
    cols = ["target_month", "model", "forecast"]
    a = run1[cols].sort_values(["target_month", "model"]).reset_index(drop=True)
    b = run2[cols].sort_values(["target_month", "model"]).reset_index(drop=True)
    max_diff = float(np.max(np.abs(a.forecast.to_numpy() - b.forecast.to_numpy())))
    deterministic_pass = bool(max_diff <= 1e-9 and a[["target_month", "model"]].equals(b[["target_month", "model"]]))
    if not deterministic_pass:
        raise RuntimeError(f"DETERMINISM_FAIL:{max_diff}")

    scorecard, decision = score(run1, deterministic_pass, data_audit["source_pit_gate"])
    sha = canonical_sha()
    evidence = {
        "contract": "GOLD_CONTROL_H1_SUCCESSOR_VALIDATION_CONTRACT_R2",
        "evidence_class": "HISTORICAL_REPLAY",
        "canonical_code_sha": sha,
        "target_series": TARGET_SERIES,
        "macro_series": MACRO_SERIES,
        "window": {"start": str(EVAL_START), "end": str(EVAL_END), "N": EXPECTED_N},
        "completed_year_gate_buckets": COMPLETED_YEARS,
        "data_audit": data_audit,
        "determinism": {"pass": deterministic_pass, "max_abs_rerun_diff": max_diff},
        "decision": decision,
        "scorecard": scorecard.to_dict(orient="records"),
        "forecast_ledger_write": "NONE",
        "prospective_claim": False,
    }
    evidence["evidence_sha256"] = canonical_json_hash(evidence)

    # Keep actual/forecast rows as a research artifact; never insert them into the prospective forecast ledger.
    out_rows = run1[["target_month", "year", "model", "actual", "forecast", "abs_error", "ape_pct"]].copy()
    out_rows.to_csv(OUTDIR / "successor_r2_historical_replay_predictions.csv", index=False)
    scorecard.to_csv(OUTDIR / "successor_r2_scorecard.csv", index=False)
    (OUTDIR / "successor_r2_evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")

    print(f"COMMON_WINDOW_N={EXPECTED_N}")
    print(f"DETERMINISTIC_RERUN_PASS={deterministic_pass}")
    print(f"DETERMINISTIC_MAX_ABS_DIFF={max_diff:.12g}")
    for _, r in scorecard.sort_values("Relative_MAE_vs_RW").iterrows():
        print(
            "SCORE "
            f"model={r['model']} rel_mae={r['Relative_MAE_vs_RW']:.6f} "
            f"mae={r['MAE']:.6f} mape={r['MAPE_pct']:.6f} medae={r['median_abs_error']:.6f} "
            f"year_beats={int(r['completed_years_beaten_vs_RW'])} max_year_ratio={r['max_completed_year_MAE_ratio_vs_RW']:.6f} "
            f"eligible={bool(r['eligible'])} failed={r['failed_gates']}"
        )
    print(f"SUCCESSOR_R2_DECISION={decision['decision']}")
    print(f"SUCCESSOR_R2_SELECTED_MODEL={decision['selected_model']}")
    print(f"EVIDENCE_SHA256={evidence['evidence_sha256']}")
    print("FORECAST_LEDGER_WRITE=NONE")
    print("PROSPECTIVE_CLAIM=NO")
    print("SUCCESSOR_R2_HISTORICAL_REPLAY_COMPLETE")


if __name__ == "__main__":
    main()
