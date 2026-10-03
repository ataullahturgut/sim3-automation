from __future__ import annotations

import io
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "gold_axis_2026"

RIFT_PANEL = OUT / "GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
OPAL_PRED = OUT / "GOLD_H3_CLEAN_OPAL_PREDICTIONS_2026-10-03.csv"
V5_PRED = OUT / "GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

SOURCE_OUT = OUT / "GOLD_H3_OPTIONS_FLOW_V1_OCC_SOURCE_2026-10-03.csv"
PANEL_OUT = OUT / "GOLD_H3_OPTIONS_FLOW_V1_PANEL_2026-10-03.csv"
PRED_OUT = OUT / "GOLD_H3_OPTIONS_FLOW_V1_PREDICTIONS_2026-10-03.csv"
GRID_OUT = OUT / "GOLD_H3_OPTIONS_FLOW_V1_THRESHOLD_GRID_2026-10-03.csv"
SUMMARY_OUT = OUT / "GOLD_H3_OPTIONS_FLOW_V1_SUMMARY_2026-10-03.json"
RESULT_OUT = OUT / "GOLD_H3_OPTIONS_FLOW_V1_RESULT_2026-10-03.md"

BASE_URL = "https://marketdata.theocc.com/volume-query"
START_SOURCE = pd.Timestamp("2024-10-04")
END_SOURCE = pd.Timestamp("2026-09-30")
SEED = 20261003
THRESHOLDS = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]

FEATURES = [
    "mom_x_log_pcr_total",
    "mom_x_d_log_pcr_total",
    "mom_x_log_pcr_customer",
    "mom_x_d_log_pcr_customer",
    "reversal_imbalance_total",
    "reversal_imbalance_customer",
    "mom_x_log_pcr_z20",
    "volume_z20",
    "flow_pressure_x_volume",
    "customer_mm_divergence_mom",
]


def make_model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0,
            solver="lbfgs",
            max_iter=3000,
            class_weight="balanced",
            random_state=SEED,
        )),
    ])


def f2(precision: float, recall: float) -> float:
    if precision <= 0.0 or recall <= 0.0:
        return 0.0
    return 5.0 * precision * recall / (4.0 * precision + recall)


def candidate_metrics(y, cand):
    y = np.asarray(y, dtype=int)
    cand = np.asarray(cand, dtype=bool)
    tp = int(((y == 1) & cand).sum())
    fp = int(((y == 0) & cand).sum())
    fn = int(((y == 1) & (~cand)).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    rate = float(cand.mean()) if len(cand) else 0.0
    return {
        "eligible_n": int(len(y)),
        "candidate_n": int(cand.sum()),
        "true_reversal_n": int((y == 1).sum()),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "candidate_rate": rate,
        "f2": f2(precision, recall),
    }


def request_one(session: requests.Session, date: pd.Timestamp, porc: str):
    params = {
        "reportDate": date.strftime("%Y%m%d"),
        "format": "csv",
        "volumeQueryType": "O",
        "symbolType": "O",
        "symbol": "GLD",
        "reportType": "D",
        "accountType": "ALL",
        "productKind": "OSTK",
        "porc": porc,
    }
    last_error = None
    for attempt in range(3):
        try:
            r = session.get(
                BASE_URL,
                params=params,
                timeout=45,
                headers={
                    "User-Agent": "Mozilla/5.0 research",
                    "Accept": "text/csv,text/plain,application/octet-stream,*/*",
                },
            )
            if r.status_code != 200:
                last_error = f"HTTP_{r.status_code}"
                time.sleep(0.25 * (attempt + 1))
                continue
            text = r.content.decode("utf-8-sig", errors="replace").strip()
            if not text:
                return None, "EMPTY"
            low = text.lower()
            if "report date cannot be prior" in low:
                return None, "RETENTION_BLOCK"
            if "no data" in low or "not a valid" in low or "invalid date" in low:
                return None, "NO_DATA"
            try:
                df = pd.read_csv(io.StringIO(text))
            except Exception as e:
                return None, "PARSE_ERROR:" + repr(e)
            if not {"quantity", "symbol", "actype", "porc", "actdate"}.issubset(df.columns):
                return None, "SCHEMA_MISMATCH:" + "|".join(map(str, df.columns))
            df = df[df["symbol"].astype(str).str.upper().eq("GLD")].copy()
            if df.empty:
                return None, "NO_GLD"
            df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0.0)
            df["actype"] = df["actype"].astype(str).str.upper()
            df["porc"] = df["porc"].astype(str).str.upper()
            return df, "PASS"
        except Exception as e:
            last_error = repr(e)
            time.sleep(0.25 * (attempt + 1))
    return None, "REQUEST_ERROR:" + str(last_error)


def aggregate_day(df: pd.DataFrame, date: pd.Timestamp, transport_mode: str):
    row = {
        "source_date": date,
        "transport_mode": transport_mode,
    }
    for side, prefix in [("C", "call"), ("P", "put")]:
        s = df[df["porc"].eq(side)]
        for acct, suffix in [("C", "customer"), ("F", "firm"), ("M", "mm")]:
            row[f"{prefix}_{suffix}"] = float(s.loc[s["actype"].eq(acct), "quantity"].sum())
    for prefix in ["call", "put"]:
        row[f"{prefix}_total"] = (
            row[f"{prefix}_customer"]
            + row[f"{prefix}_firm"]
            + row[f"{prefix}_mm"]
        )
    row["option_volume_total"] = row["call_total"] + row["put_total"]
    return row


def download_source():
    session = requests.Session()
    rows = []
    audit = []
    dates = pd.bdate_range(START_SOURCE, END_SOURCE)

    for idx, d in enumerate(dates):
        both, status = request_one(session, d, "BOTH")
        transport = "BOTH"
        if both is None or not {"C", "P"}.issubset(set(both["porc"].astype(str).str.upper().unique())):
            c, sc = request_one(session, d, "C")
            p, sp = request_one(session, d, "P")
            if c is not None and p is not None:
                both = pd.concat([c, p], ignore_index=True)
                status = "PASS"
                transport = "C_PLUS_P"
            else:
                audit.append({
                    "source_date": d.strftime("%Y-%m-%d"),
                    "status": status,
                    "call_status": sc,
                    "put_status": sp,
                })
                continue

        rows.append(aggregate_day(both, d, transport))
        audit.append({
            "source_date": d.strftime("%Y-%m-%d"),
            "status": "PASS",
            "transport_mode": transport,
            "rows": int(len(both)),
        })
        if idx % 25 == 0:
            print(f"source progress {idx+1}/{len(dates)} accepted={len(rows)}")
        time.sleep(0.03)

    if not rows:
        raise RuntimeError("NO_OCC_SOURCE_ROWS")

    src = pd.DataFrame(rows).sort_values("source_date").reset_index(drop=True)
    src["source_date"] = pd.to_datetime(src["source_date"])

    eps = 1.0
    src["log_pcr_total"] = np.log((src["put_total"] + eps) / (src["call_total"] + eps))
    src["log_pcr_customer"] = np.log((src["put_customer"] + eps) / (src["call_customer"] + eps))
    src["log_pcr_mm"] = np.log((src["put_mm"] + eps) / (src["call_mm"] + eps))
    src["d_log_pcr_total_1"] = src["log_pcr_total"].diff()
    src["d_log_pcr_customer_1"] = src["log_pcr_customer"].diff()
    src["imbalance_total"] = (
        (src["call_total"] - src["put_total"])
        / (src["call_total"] + src["put_total"] + eps)
    )
    src["imbalance_customer"] = (
        (src["call_customer"] - src["put_customer"])
        / (src["call_customer"] + src["put_customer"] + eps)
    )

    logvol = np.log1p(src["option_volume_total"])
    hist_logvol = logvol.shift(1)
    mu_v = hist_logvol.rolling(20, min_periods=20).mean()
    sd_v = hist_logvol.rolling(20, min_periods=20).std(ddof=0)
    src["volume_z20"] = (logvol - mu_v) / (sd_v + 1e-8)

    hist_pcr = src["log_pcr_total"].shift(1)
    mu_p = hist_pcr.rolling(20, min_periods=20).mean()
    sd_p = hist_pcr.rolling(20, min_periods=20).std(ddof=0)
    src["log_pcr_total_z20"] = (src["log_pcr_total"] - mu_p) / (sd_p + 1e-8)

    src.to_csv(SOURCE_OUT, index=False)
    return src, audit


def build_panel(src: pd.DataFrame):
    p = pd.read_csv(RIFT_PANEL)
    for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
        p[c] = pd.to_datetime(p[c], errors="raise")
    p = p.sort_values("feature_cutoff_date").reset_index(drop=True)

    source_cols = [
        "source_date",
        "call_customer", "call_firm", "call_mm",
        "put_customer", "put_firm", "put_mm",
        "call_total", "put_total", "option_volume_total",
        "log_pcr_total", "log_pcr_customer", "log_pcr_mm",
        "d_log_pcr_total_1", "d_log_pcr_customer_1",
        "imbalance_total", "imbalance_customer",
        "volume_z20", "log_pcr_total_z20",
    ]
    s = src[source_cols].sort_values("source_date").copy()

    m = pd.merge_asof(
        p.sort_values("feature_cutoff_date"),
        s,
        left_on="feature_cutoff_date",
        right_on="source_date",
        direction="backward",
        allow_exact_matches=False,
    )
    m["source_staleness_days"] = (m["feature_cutoff_date"] - m["source_date"]).dt.days
    m = m[m["source_staleness_days"].between(1, 5, inclusive="both")].copy()

    momentum_sign = np.where(m["momentum_up"].astype(bool), 1.0, -1.0)
    m["mom_x_log_pcr_total"] = momentum_sign * m["log_pcr_total"]
    m["mom_x_d_log_pcr_total"] = momentum_sign * m["d_log_pcr_total_1"]
    m["mom_x_log_pcr_customer"] = momentum_sign * m["log_pcr_customer"]
    m["mom_x_d_log_pcr_customer"] = momentum_sign * m["d_log_pcr_customer_1"]
    m["reversal_imbalance_total"] = -momentum_sign * m["imbalance_total"]
    m["reversal_imbalance_customer"] = -momentum_sign * m["imbalance_customer"]
    m["mom_x_log_pcr_z20"] = momentum_sign * m["log_pcr_total_z20"]
    m["flow_pressure_x_volume"] = m["reversal_imbalance_total"] * m["volume_z20"]
    m["customer_mm_divergence_mom"] = momentum_sign * (
        m["log_pcr_customer"] - m["log_pcr_mm"]
    )

    m = m.dropna(subset=FEATURES + ["reversal_target"]).copy()
    m["month_key"] = m["forecast_issue_date"].dt.to_period("M").astype(str)
    return m.sort_values("forecast_issue_date").reset_index(drop=True)


def expanding_predictions(panel: pd.DataFrame):
    eval_start = pd.Timestamp("2025-01-01")
    test = panel[panel["forecast_issue_date"] >= eval_start].copy()
    out = []

    for mo in sorted(test["month_key"].unique()):
        te = test[test["month_key"].eq(mo)].copy()
        cutoff = te["feature_cutoff_date"].min()
        tr = panel[
            (panel["target_end_date_h3"] <= cutoff)
            & (panel["aurora_follows_momentum"].astype(bool))
        ].copy()
        if len(tr) < 40 or tr["reversal_target"].nunique() < 2:
            continue
        model = make_model()
        model.fit(tr[FEATURES].to_numpy(float), tr["reversal_target"].astype(int).to_numpy())
        pr = model.predict_proba(te[FEATURES].to_numpy(float))[:, 1]

        keep = [
            "feature_cutoff_date", "forecast_issue_date", "target_end_date_h3",
            "year", "month", "y_up", "target_r3", "p_aurora",
            "h_ret_12", "momentum_up", "reversal_target",
            "aurora_pred", "aurora_follows_momentum",
            "source_date", "source_staleness_days",
        ]
        q = te[keep].copy()
        q["p_options_flow_reversal"] = pr
        q["train_n"] = len(tr)
        out.append(q)

    if not out:
        raise RuntimeError("NO_EXPANDING_PREDICTIONS")
    return pd.concat(out, ignore_index=True).sort_values("forecast_issue_date").reset_index(drop=True)


def load_opal():
    o = pd.read_csv(OPAL_PRED)
    o["forecast_issue_date"] = pd.to_datetime(o["forecast_issue_date"])
    o["opal_candidate"] = o["override"].astype(str).str.lower().eq("true")
    return o[["forecast_issue_date", "opal_candidate"]]


def threshold_grid(pred: pd.DataFrame):
    d = pred[
        (pred["forecast_issue_date"] >= pd.Timestamp("2025-01-01"))
        & (pred["forecast_issue_date"] <= pd.Timestamp("2025-06-30"))
        & (pred["aurora_follows_momentum"].astype(bool))
    ].copy()
    rows = []
    for th in THRESHOLDS:
        met = candidate_metrics(d["reversal_target"], d["p_options_flow_reversal"] >= th)
        eligible = bool(met["precision"] >= 0.45 and met["candidate_rate"] <= 0.40)
        rows.append({"threshold": th, **met, "eligible": eligible})
    tab = pd.DataFrame(rows)
    elig = tab[tab["eligible"]].copy()
    if elig.empty:
        return tab, None
    elig = elig.sort_values(
        ["f2", "recall", "precision", "candidate_rate", "threshold"],
        ascending=[False, False, False, True, False],
    )
    return tab, float(elig.iloc[0]["threshold"])


def compare_period(pred: pd.DataFrame, th: float, start: str, end: str):
    d = pred[
        (pred["forecast_issue_date"] >= pd.Timestamp(start))
        & (pred["forecast_issue_date"] <= pd.Timestamp(end))
        & (pred["aurora_follows_momentum"].astype(bool))
    ].copy()
    d = d.merge(load_opal(), on="forecast_issue_date", how="left", validate="one_to_one")
    d["opal_candidate"] = d["opal_candidate"].fillna(False).astype(bool)
    d["flow_candidate"] = d["p_options_flow_reversal"] >= th

    flow = candidate_metrics(d["reversal_target"], d["flow_candidate"])
    opal = candidate_metrics(d["reversal_target"], d["opal_candidate"])
    union = candidate_metrics(d["reversal_target"], d["flow_candidate"] | d["opal_candidate"])
    flow_only_true = int(
        (
            (d["reversal_target"] == 1)
            & d["flow_candidate"]
            & (~d["opal_candidate"])
        ).sum()
    )
    brier = float(brier_score_loss(d["reversal_target"].astype(int), d["p_options_flow_reversal"]))
    ll = float(log_loss(d["reversal_target"].astype(int), d["p_options_flow_reversal"], labels=[0, 1]))
    return d, {
        "options_flow": flow,
        "opal": opal,
        "union": union,
        "options_flow_only_true": flow_only_true,
        "brier": brier,
        "logloss": ll,
    }


def confirmation_2025_h2(pred: pd.DataFrame, th: float):
    _, r = compare_period(pred, th, "2025-07-01", "2025-12-31")
    passed = bool(
        r["options_flow"]["recall"] > r["opal"]["recall"]
        and r["options_flow_only_true"] >= 1
        and r["options_flow"]["precision"] >= 0.40
        and r["union"]["recall"] > r["opal"]["recall"]
    )
    r["pass_gate"] = passed
    return r


def holdout_2026(pred: pd.DataFrame, th: float):
    d, r = compare_period(pred, th, "2026-01-01", "2026-12-31")

    v = pd.read_csv(V5_PRED)
    v["forecast_issue_date"] = pd.to_datetime(v["forecast_issue_date"])
    v["v5_pred"] = (pd.to_numeric(v["p_helios_v5_dce"]) >= 0.5).astype(int)
    d = d.merge(
        v[["forecast_issue_date", "v5_pred"]],
        on="forecast_issue_date",
        how="left",
        validate="one_to_one",
    )
    d = d.dropna(subset=["v5_pred"]).copy()
    d["v5_pred"] = d["v5_pred"].astype(int)

    forced = np.where(
        d["flow_candidate"],
        1 - d["momentum_up"].astype(int),
        d["v5_pred"],
    )
    rescued = int(((d["v5_pred"] != d["y_up"]) & (forced == d["y_up"])).sum())
    broken = int(((d["v5_pred"] == d["y_up"]) & (forced != d["y_up"])).sum())

    missed_opal = (
        (d["v5_pred"] != d["y_up"])
        & (d["reversal_target"] == 1)
        & (~d["opal_candidate"])
    )
    r["v5_missed_opal_no_candidate_n"] = int(missed_opal.sum())
    r["v5_missed_opal_no_candidate_nominated"] = int(
        (missed_opal & d["flow_candidate"]).sum()
    )
    r["diagnostic_forced_flip_rescued"] = rescued
    r["diagnostic_forced_flip_broken"] = broken
    r["diagnostic_forced_flip_net"] = rescued - broken
    return r


def write_result(summary):
    grid = pd.DataFrame(summary["threshold_grid"])
    lines = [
        "# OPTIONS-FLOW-H3 V1 — RESULT",
        "",
        f"**Status:** **{summary['status']}**  ",
        f"**Evidence class:** **SHORT_HISTORY_OFFICIAL_OCC_AUTHORITY**  ",
        f"**Selected threshold:** **{summary['selected_threshold'] if summary['selected_threshold'] is not None else 'NONE'}**",
        "",
        "## OCC source audit",
        "",
        f"- accepted source dates: **{summary['source']['accepted_dates']}**",
        f"- first accepted date: **{summary['source']['min_date']}**",
        f"- last accepted date: **{summary['source']['max_date']}**",
        f"- BOTH transport dates: **{summary['source']['both_transport_dates']}**",
        f"- C+P fallback dates: **{summary['source']['split_transport_dates']}**",
        "",
        "## 2025 H1 DEV threshold grid",
        "",
        "| Th | Cand | Precision | Recall | Rate | F2 | Eligible |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in grid.itertuples():
        lines.append(
            f"| {r.threshold:.2f} | {int(r.candidate_n)} | "
            f"{100*r.precision:.2f}% | {100*r.recall:.2f}% | "
            f"{100*r.candidate_rate:.2f}% | {r.f2:.4f} | {r.eligible} |"
        )

    c = summary.get("confirmation_2025_h2")
    if c is not None:
        lines += [
            "",
            "## 2025 H2 confirmation",
            "",
            f"- OPTIONS-FLOW precision: **{100*c['options_flow']['precision']:.2f}%**",
            f"- OPTIONS-FLOW reversal recall: **{100*c['options_flow']['recall']:.2f}%**",
            f"- OPAL reversal recall: **{100*c['opal']['recall']:.2f}%**",
            f"- union reversal recall: **{100*c['union']['recall']:.2f}%**",
            f"- OPTIONS-FLOW-only true reversals: **{c['options_flow_only_true']}**",
            f"- Brier: **{c['brier']:.4f}**",
            f"- logloss: **{c['logloss']:.4f}**",
            f"- confirmation PASS: **{c['pass_gate']}**",
        ]

    h = summary.get("holdout_2026")
    if h is not None:
        lines += [
            "",
            "## 2026 frozen holdout",
            "",
            f"- OPTIONS-FLOW precision: **{100*h['options_flow']['precision']:.2f}%**",
            f"- OPTIONS-FLOW reversal recall: **{100*h['options_flow']['recall']:.2f}%**",
            f"- OPAL reversal recall: **{100*h['opal']['recall']:.2f}%**",
            f"- union reversal recall: **{100*h['union']['recall']:.2f}%**",
            f"- OPTIONS-FLOW-only true reversals: **{h['options_flow_only_true']}**",
            f"- V5-missed / OPAL-no-candidate reversals in scored universe: **{h['v5_missed_opal_no_candidate_n']}**",
            f"- nominated by OPTIONS-FLOW: **{h['v5_missed_opal_no_candidate_nominated']}**",
            f"- forced-flip rescue / broken / net: **{h['diagnostic_forced_flip_rescued']} / {h['diagnostic_forced_flip_broken']} / {h['diagnostic_forced_flip_net']}**",
            f"- Brier: **{h['brier']:.4f}**",
            f"- logloss: **{h['logloss']:.4f}**",
        ]

    lines += [
        "",
        "## Governance",
        "",
        "Source, periods, lag, feature family, model, threshold grid and gates were frozen before the full OCC history pull/model fit. "
        "Formal 2026 evaluation is opened only after 2025 H2 confirmation PASS.",
    ]
    RESULT_OUT.write_text("\n".join(lines) + "\n")


def main():
    src, audit = download_source()
    panel = build_panel(src)
    pred = expanding_predictions(panel)

    grid, th = threshold_grid(pred)
    grid.to_csv(GRID_OUT, index=False)
    panel.to_csv(PANEL_OUT, index=False)
    pred.to_csv(PRED_OUT, index=False)

    source_summary = {
        "accepted_dates": int(len(src)),
        "min_date": src["source_date"].min().strftime("%Y-%m-%d"),
        "max_date": src["source_date"].max().strftime("%Y-%m-%d"),
        "both_transport_dates": int((src["transport_mode"] == "BOTH").sum()),
        "split_transport_dates": int((src["transport_mode"] == "C_PLUS_P").sum()),
        "audit_status_counts": pd.Series([x["status"] for x in audit]).value_counts().to_dict(),
    }

    summary = {
        "schema": "OPTIONS_FLOW_H3_V1",
        "evidence_class": "SHORT_HISTORY_OFFICIAL_OCC_AUTHORITY",
        "features": FEATURES,
        "source": source_summary,
        "selected_threshold": th,
        "threshold_grid": grid.to_dict(orient="records"),
        "confirmation_2025_h2": None,
        "holdout_2026": None,
    }

    status = "NO_ELIGIBLE_OPTIONS_FLOW_THRESHOLD"
    if th is not None:
        conf = confirmation_2025_h2(pred, th)
        summary["confirmation_2025_h2"] = conf
        if conf["pass_gate"]:
            summary["holdout_2026"] = holdout_2026(pred, th)
            status = "CONFIRMATION_PASS_HOLDOUT_OPENED"
        else:
            status = "CONFIRMATION_2025_H2_FAIL"

    summary["status"] = status
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, default=str) + "\n")
    write_result(summary)
    print(RESULT_OUT.read_text())


if __name__ == "__main__":
    main()
