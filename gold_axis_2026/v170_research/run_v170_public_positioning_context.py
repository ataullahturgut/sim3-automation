from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, log_loss, matthews_corrcoef, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v170_research/contracts/v170_public_positioning_context_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v170_research"

SHUTDOWN_RELEASES = {
    "2025-09-30": "2025-11-19",
    "2025-10-07": "2025-11-21",
    "2025-10-14": "2025-11-25",
    "2025-10-21": "2025-12-02",
    "2025-10-28": "2025-12-05",
    "2025-11-04": "2025-12-09",
    "2025-11-10": "2025-12-12",
    "2025-11-18": "2025-12-16",
    "2025-11-25": "2025-12-19",
    "2025-12-02": "2025-12-23",
    "2025-12-09": "2025-12-30",
    "2025-12-16": "2026-01-06",
    "2025-12-23": "2026-01-09",
    "2025-12-30": "2026-01-13",
    "2026-01-06": "2026-01-16",
    "2026-01-13": "2026-01-20",
    "2026-01-20": "2026-01-23",
}


def load_contract() -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_ANY_V170_SCORING":
        raise RuntimeError("V170_CONTRACT_NOT_FROZEN")
    if c["governance"]["AUTO_SELECTOR"] != "OFF" or c["governance"]["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V170_GOVERNANCE_LOCK_FAIL")
    required = {"same_day_GVZ", "COT_report_date_as_if_publication_date", "post_score_feature_addition", "hyperparameter_search", "2025_2026_based_selection", "paid_data", "production_writes"}
    if not required.issubset(set(c["forbidden_in_v170"])):
        raise RuntimeError("V170_FORBIDDEN_LOCK_FAIL")
    return c


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def source_dirs() -> tuple[Path, Path]:
    a = Path(os.environ.get("V164_ARTIFACT_DIR", ""))
    s = Path(os.environ.get("V170_PUBLIC_SOURCE_DIR", ""))
    if not (a / "v164_panel.csv").exists():
        raise RuntimeError("V170_V164_PANEL_MISSING")
    if not (s / "cftc_gold_088691.csv").exists():
        raise RuntimeError("V170_CFTC_SOURCE_MISSING")
    if not (s / "GVZ_History.csv").exists():
        raise RuntimeError("V170_GVZ_SOURCE_MISSING")
    return a, s


def build_target_panel(panel: pd.DataFrame, horizon: int) -> pd.DataFrame:
    z = panel.copy().reset_index().rename(columns={"index": "origin_index"})
    z["origin_date"] = pd.to_datetime(z["date"])
    z["target_date"] = pd.to_datetime(z["date"].shift(-int(horizon)))
    c0 = pd.to_numeric(z["close"], errors="coerce")
    ch = pd.to_numeric(z["close"].shift(-int(horizon)), errors="coerce")
    z["continuous_return"] = np.log(ch / c0)
    z["y"] = (z["continuous_return"] > 0.0).astype(float)
    z = z[z["target_date"].notna() & np.isfinite(z["continuous_return"])].copy()
    z["y"] = z["y"].astype(int)
    z["horizon"] = int(horizon)
    return z


def normalize(s: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(s)).strip("_")


def resolve_col(df: pd.DataFrame, candidates: list[str]) -> str:
    m = {normalize(c): c for c in df.columns}
    for cand in candidates:
        if normalize(cand) in m:
            return m[normalize(cand)]
    raise RuntimeError(f"V170_COLUMN_NOT_FOUND:{candidates}")


def prepare_gvz(path: Path) -> pd.DataFrame:
    g = pd.read_csv(path)
    date_col = resolve_col(g, ["DATE", "Date"])
    close_col = resolve_col(g, ["CLOSE", "Close"])
    z = pd.DataFrame({"gvz_date": pd.to_datetime(g[date_col], errors="coerce"), "gvz_close": pd.to_numeric(g[close_col], errors="coerce")})
    z = z.dropna().sort_values("gvz_date").drop_duplicates("gvz_date", keep="last").reset_index(drop=True)
    z["pub_gvz_ret1_lag"] = np.log(z["gvz_close"] / z["gvz_close"].shift(1))
    z["pub_gvz_chg5_lag"] = np.log(z["gvz_close"] / z["gvz_close"].shift(5))
    mu = z["gvz_close"].rolling(20, min_periods=10).mean().shift(1)
    sd = z["gvz_close"].rolling(20, min_periods=10).std(ddof=0).shift(1)
    z["pub_gvz_z20_lag"] = (z["gvz_close"] - mu) / sd.replace(0.0, np.nan)
    z["pub_gvz_level_lag"] = z["gvz_close"]
    return z[["gvz_date", "pub_gvz_level_lag", "pub_gvz_ret1_lag", "pub_gvz_chg5_lag", "pub_gvz_z20_lag"]]


def prepare_cot(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path)
    code_col = resolve_col(d, ["cftc_contract_market_code", "CFTC_Contract_Market_Code"])
    d[code_col] = d[code_col].astype(str).str.strip()
    d = d[d[code_col].str.replace(".0", "", regex=False) == "088691"].copy()
    if d.empty:
        raise RuntimeError("V170_NO_GOLD_COT_ROWS")
    report_col = resolve_col(d, ["report_date_as_yyyy_mm_dd", "Report_Date_as_YYYY_MM_DD"])
    oi_col = resolve_col(d, ["open_interest_all", "Open_Interest_All"])
    pm_l = resolve_col(d, ["prod_merc_positions_long", "prod_merc_positions_long_all", "Prod_Merc_Positions_Long_All"])
    pm_s = resolve_col(d, ["prod_merc_positions_short", "prod_merc_positions_short_all", "Prod_Merc_Positions_Short_All"])
    sw_l = resolve_col(d, ["swap_positions_long_all", "Swap_Positions_Long_All"])
    sw_s = resolve_col(d, ["swap__positions_short_all", "swap_positions_short_all", "Swap__Positions_Short_All"])
    mm_l = resolve_col(d, ["m_money_positions_long_all", "M_Money_Positions_Long_All"])
    mm_s = resolve_col(d, ["m_money_positions_short_all", "M_Money_Positions_Short_All"])
    z = pd.DataFrame({
        "report_date": pd.to_datetime(d[report_col], errors="coerce"),
        "oi": pd.to_numeric(d[oi_col], errors="coerce"),
        "pm_long": pd.to_numeric(d[pm_l], errors="coerce"), "pm_short": pd.to_numeric(d[pm_s], errors="coerce"),
        "sw_long": pd.to_numeric(d[sw_l], errors="coerce"), "sw_short": pd.to_numeric(d[sw_s], errors="coerce"),
        "mm_long": pd.to_numeric(d[mm_l], errors="coerce"), "mm_short": pd.to_numeric(d[mm_s], errors="coerce"),
    }).dropna(subset=["report_date", "oi"])
    z = z[z["oi"] > 0].sort_values("report_date").drop_duplicates("report_date", keep="last").reset_index(drop=True)
    z["pub_cot_mm_net_oi"] = (z["mm_long"] - z["mm_short"]) / z["oi"]
    z["pub_cot_prod_net_oi"] = (z["pm_long"] - z["pm_short"]) / z["oi"]
    z["pub_cot_swap_net_oi"] = (z["sw_long"] - z["sw_short"]) / z["oi"]
    z["pub_cot_mm_net_change_1w_oi"] = z["pub_cot_mm_net_oi"].diff(1)
    z["pub_cot_oi_change_1w"] = z["oi"].pct_change(1)
    z["available_date"] = z["report_date"] + pd.to_timedelta(7, unit="D")
    for rd, ad in SHUTDOWN_RELEASES.items():
        z.loc[z["report_date"] == pd.Timestamp(rd), "available_date"] = pd.Timestamp(ad)
    return z[["report_date", "available_date", "pub_cot_mm_net_oi", "pub_cot_prod_net_oi", "pub_cot_swap_net_oi", "pub_cot_mm_net_change_1w_oi", "pub_cot_oi_change_1w"]]


def attach_public(panel: pd.DataFrame, gvz: pd.DataFrame, cot: pd.DataFrame) -> pd.DataFrame:
    z = panel.copy().sort_values("origin_date").reset_index(drop=True)
    # Strict previous-date GVZ: shift join key by one nanosecond so same-day rows cannot match.
    left = z[["origin_date"]].copy()
    left["gvz_key"] = left["origin_date"] - pd.Timedelta(nanoseconds=1)
    z = pd.concat([z, pd.merge_asof(left.sort_values("gvz_key"), gvz.sort_values("gvz_date"), left_on="gvz_key", right_on="gvz_date", direction="backward").drop(columns=["origin_date", "gvz_key"])], axis=1)
    left2 = z[["origin_date"]].copy()
    left2["cot_key"] = left2["origin_date"] - pd.Timedelta(nanoseconds=1)
    c = pd.merge_asof(left2.sort_values("cot_key"), cot.sort_values("available_date"), left_on="cot_key", right_on="available_date", direction="backward")
    z = pd.concat([z, c.drop(columns=["origin_date", "cot_key"])], axis=1)
    z["pub_cot_age_days"] = (pd.to_datetime(z["origin_date"]) - pd.to_datetime(z["available_date"])).dt.days.astype(float)
    if ((pd.to_datetime(z["gvz_date"]) >= pd.to_datetime(z["origin_date"])) & z["gvz_date"].notna()).any():
        raise RuntimeError("V170_SAME_DAY_GVZ_LEAK")
    if ((pd.to_datetime(z["available_date"]) >= pd.to_datetime(z["origin_date"])) & z["available_date"].notna()).any():
        raise RuntimeError("V170_COT_AVAILABILITY_LEAK")
    return z


def make_model(c: dict) -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("scale", StandardScaler()),
        ("model", LogisticRegression(C=float(c["model_lock"]["C"]), solver=c["model_lock"]["solver"], max_iter=5000, random_state=0)),
    ])


def clean_numeric(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    return df[features].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)


def forecast_origin(panel: pd.DataFrame, row_idx: int, features: list[str], c: dict) -> dict:
    current = panel.loc[[row_idx]]
    origin = pd.Timestamp(current.iloc[0]["origin_date"])
    hist = panel[pd.to_datetime(panel["target_date"]) < origin].sort_values("origin_date")
    freq = float(hist["y"].mean()) if len(hist) >= 20 else 0.5
    if len(hist) < 30 or hist["y"].nunique() < 2:
        return {"probability": freq, "frequency_probability": freq, "training_n": int(len(hist)), "fallback": True}
    m = make_model(c)
    m.fit(clean_numeric(hist, features), hist["y"].to_numpy(dtype=int))
    p = float(m.predict_proba(clean_numeric(current, features))[:, 1][0])
    return {"probability": p, "frequency_probability": freq, "training_n": int(len(hist)), "fallback": False}


def period_indices(panel: pd.DataFrame, start: str, end: str) -> list[int]:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    od, td = pd.to_datetime(panel["origin_date"]), pd.to_datetime(panel["target_date"])
    return panel.index[(od >= a) & (od <= b) & (td <= b)].tolist()


def predictions(panel: pd.DataFrame, idx: list[int], features: list[str], c: dict, period: str, candidate: str) -> pd.DataFrame:
    rows = []
    for i in idx:
        fc = forecast_origin(panel, i, features, c)
        r = panel.loc[i]
        rows.append({"period": period, "candidate": candidate, "horizon": int(r["horizon"]), "origin_date": str(pd.Timestamp(r["origin_date"]).date()), "target_date": str(pd.Timestamp(r["target_date"]).date()), "y": int(r["y"]), **fc})
    return pd.DataFrame(rows)


def metrics(df: pd.DataFrame) -> dict:
    y = df["y"].to_numpy(dtype=int)
    p = np.clip(df["probability"].to_numpy(dtype=float), 1e-6, 1 - 1e-6)
    fq = np.clip(df["frequency_probability"].to_numpy(dtype=float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    brier = float(brier_score_loss(y, p)); fb = float(brier_score_loss(y, fq))
    ll = float(log_loss(y, p, labels=[0, 1])); fll = float(log_loss(y, fq, labels=[0, 1]))
    return {
        "n": int(len(df)), "brier": brier, "frequency_brier": fb, "brier_skill_vs_frequency": float(1 - brier / fb) if fb > 0 else None,
        "log_loss": ll, "frequency_log_loss": fll, "log_loss_improvement_vs_frequency": float(fll - ll),
        "roc_auc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)) if len(np.unique(y)) == 2 else None,
        "mcc": float(matthews_corrcoef(y, pred)) if len(np.unique(y)) == 2 and len(np.unique(pred)) == 2 else 0.0,
        "up_predictions": int(pred.sum()), "down_predictions": int((1 - pred).sum()), "both_predicted_directions": bool(len(np.unique(pred)) == 2),
    }


def evaluate_candidate(panel: pd.DataFrame, features: list[str], c: dict, candidate: str) -> tuple[dict, pd.DataFrame]:
    allp = []
    out = {}
    periods = {**c["temporal_design"]["formation"], "BRIDGE_2024Q4": c["temporal_design"]["bridge_2024Q4"], **c["temporal_design"]["visible_diagnostics"]}
    for name, (start, end) in periods.items():
        idx = period_indices(panel, start, end)
        p = predictions(panel, idx, features, c, name, candidate)
        allp.append(p)
        out[name] = metrics(p)
    return out, pd.concat(allp, ignore_index=True)


def decision_for_horizon(results: dict, c: dict) -> dict:
    envs = list(c["temporal_design"]["formation"].keys())
    base = results["BASE_CORE"]; aug = results["BASE_PLUS_PUBLIC"]
    diffs = [base[e]["brier"] - aug[e]["brier"] for e in envs]
    aucs = [aug[e]["roc_auc"] for e in envs]
    f = c["formation_gate"]
    formation_pass = bool(
        sum(d > 0 for d in diffs) >= int(f["augmented_brier_better_than_base_environments_min"])
        and float(np.median(diffs)) >= float(f["median_brier_improvement_vs_base_min"])
        and sum(aug[e]["brier_skill_vs_frequency"] is not None and aug[e]["brier_skill_vs_frequency"] > 0 for e in envs) >= int(f["augmented_positive_brier_skill_vs_frequency_environments_min"])
        and all(a is not None for a in aucs)
        and float(np.median(aucs)) >= float(f["augmented_median_auc_min"])
        and float(np.min(aucs)) >= float(f["augmented_minimum_auc_min"])
    )
    b = c["bridge_gate"]; bm = base["BRIDGE_2024Q4"]; am = aug["BRIDGE_2024Q4"]
    bridge_pass = bool(
        formation_pass
        and (bm["brier"] - am["brier"]) >= float(b["augmented_brier_improvement_vs_base_min"])
        and am["brier"] <= am["frequency_brier"] + 1e-12
        and am["log_loss"] <= bm["log_loss"] + 1e-12
        and am["log_loss"] <= am["frequency_log_loss"] + 1e-12
        and am["roc_auc"] is not None and bm["roc_auc"] is not None and am["roc_auc"] >= bm["roc_auc"] - 1e-12
        and am["roc_auc"] >= float(b["augmented_auc_min"])
        and am["both_predicted_directions"]
    )
    return {"formation_pass": formation_pass, "bridge_pass": bridge_pass, "formation_brier_improvements_vs_base": diffs, "bridge_brier_improvement_vs_base": float(bm["brier"] - am["brier"])}


def main() -> None:
    c = load_contract(); adir, sdir = source_dirs(); OUT.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(adir / "v164_panel.csv")
    gvz = prepare_gvz(sdir / "GVZ_History.csv")
    cot = prepare_cot(sdir / "cftc_gold_088691.csv")
    candidates = {
        "BASE_CORE": c["base_features"],
        "PUBLIC_ONLY": c["public_features"],
        "BASE_PLUS_PUBLIC": c["base_features"] + c["public_features"],
    }
    final = {"contract_id": c["contract_id"], "source_hashes": {"v164_panel": sha256(adir / "v164_panel.csv"), "cftc": sha256(sdir / "cftc_gold_088691.csv"), "gvz": sha256(sdir / "GVZ_History.csv")}, "source_coverage": {"cftc_report_min": str(cot["report_date"].min().date()), "cftc_report_max": str(cot["report_date"].max().date()), "gvz_min": str(gvz["gvz_date"].min().date()), "gvz_max": str(gvz["gvz_date"].max().date())}, "horizons": {}}
    pred_all = []
    for h in c["horizons"]:
        panel = attach_public(build_target_panel(raw, h), gvz, cot)
        hres = {}
        for name, feats in candidates.items():
            res, pred = evaluate_candidate(panel, feats, c, name)
            hres[name] = res; pred_all.append(pred)
        dec = decision_for_horizon(hres, c)
        final["horizons"][str(h)] = {"candidates": hres, "decision": dec}
    final["overall_decision"] = "PRE2025_INCREMENTAL_PUBLIC_SIGNAL_FOUND" if any(v["decision"]["bridge_pass"] for v in final["horizons"].values()) else "NO_PRE2025_INCREMENTAL_PUBLIC_SIGNAL__FREE_CONTEXT_HYPOTHESIS_FAIL"
    (OUT / "v170_public_positioning_context_results.json").write_text(json.dumps(final, indent=2, allow_nan=False), encoding="utf-8")
    pd.concat(pred_all, ignore_index=True).to_csv(OUT / "v170_public_positioning_context_predictions.csv", index=False)
    cot.to_csv(OUT / "v170_cot_prepared_audit.csv", index=False)
    print(json.dumps({"overall_decision": final["overall_decision"], "horizon_decisions": {h: v["decision"] for h, v in final["horizons"].items()}, "coverage": final["source_coverage"]}, indent=2))


if __name__ == "__main__":
    main()
