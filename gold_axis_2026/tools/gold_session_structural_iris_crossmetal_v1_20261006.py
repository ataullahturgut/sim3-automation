from __future__ import annotations

import gzip
import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
A0_PATH = AX / "tools" / "gold_session_nova_a0_core3_raw_replay_v1_20261006.py"
SI_ARCHIVE = AX / "GOLD_DATABENTO_GLBX_OHLCV1H_N_RAW_2022_2024.csv.gz"
OUT = AX / "SESSION_STRUCTURAL_IRIS_CROSSMETAL_V1_OUT"
OUT.mkdir(exist_ok=True)

XAU_SERIES_ID = "XAU_USD_TWELVE_1H_RESEARCH_V1"
DATABENTO_DATASET = "GLBX.MDP3"
DATABENTO_SCHEMA = "ohlcv-1h"
DATABENTO_PL_SYMBOL = "PL.n.0"
START = "2022-01-01"
END = "2025-01-01"
PL_COST_CAP_USD = 1.00

SEED = 20261006
BLOCK = 5
A1_RECENT_N = 252
STRUCTURAL_MIN_TRAIN = 180

PATH_BASE = [
    "ret_1", "ret_3", "ret_6", "ret_12", "ret_24", "ret_48",
    "lag2", "session_ret",
]

spec = importlib.util.spec_from_file_location("nova_a0_raw", A0_PATH)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)
CORE3 = list(base.CORE3)


def make_model(*, balanced: bool = False):
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0,
            solver="lbfgs",
            max_iter=3000,
            class_weight="balanced" if balanced else None,
            random_state=SEED,
        )),
    ])


def metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(np.mean((p - y) ** 2)),
        "logloss": float(log_loss(y, p, labels=[0, 1])),
        "up_recall": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "down_recall": float(recall_score(y, pred, pos_label=0, zero_division=0)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def load_daily_session_panel():
    metals, annual_hashes = base.load_raw_metals()
    targets = base.verify_v5_targets()
    targets = targets[pd.to_datetime(targets["label_date"]).dt.year.isin([2023, 2024])].copy()
    panel = base.align_daily_features(targets, metals)
    panel = panel.dropna(subset=CORE3 + ["direction", "obs_date"]).copy()
    panel["start_utc"] = pd.to_datetime(panel["start_utc"], utc=True)
    panel["end_utc"] = pd.to_datetime(panel["end_utc"], utc=True)
    return panel, annual_hashes


def generate_fresh_a1(panel):
    out = []
    for (part, win), g0 in panel.groupby(["partition", "window"], sort=True):
        g = g0.sort_values("start_utc").reset_index(drop=True)
        for bs in range(0, len(g), BLOCK):
            te = g.iloc[bs:bs + BLOCK].copy()
            if te.empty:
                continue
            cutoff = te["start_utc"].min()
            tr = g[(g["end_utc"] <= cutoff) & (g["start_utc"] < cutoff)].copy()
            if len(tr) < A1_RECENT_N:
                continue
            yg = tr["y_up"].to_numpy(int)
            mg = make_model(balanced=False)
            mg.fit(tr[CORE3].astype(float), yg)
            p0 = mg.predict_proba(te[CORE3].astype(float))[:, 1]

            rr = tr.tail(A1_RECENT_N).copy()
            mr = make_model(balanced=True)
            mr.fit(rr[CORE3].astype(float), rr["y_up"].to_numpy(int))
            pr = mr.predict_proba(te[CORE3].astype(float))[:, 1]
            p1 = 0.75 * p0 + 0.25 * pr

            for idx, pp in zip(te.index, p1):
                r = te.loc[idx]
                out.append({
                    "label_date": r["label_date"],
                    "partition": part,
                    "window": win,
                    "start_utc": r["start_utc"],
                    "end_utc": r["end_utc"],
                    "direction": r["direction"],
                    "y_up": int(r["y_up"]),
                    "feature_obs_date": pd.Timestamp(r["obs_date"]).date().isoformat(),
                    "daily_age_days": int(r["daily_age_days"]),
                    "p_A1_arcr": float(pp),
                    "a1_train_n": int(len(tr)),
                })
    q = pd.DataFrame(out)
    if q.empty:
        raise RuntimeError("NO_FRESH_A1_ROWS")
    p = np.clip(q["p_A1_arcr"].to_numpy(float), 1e-5, 1 - 1e-5)
    q["base_logit"] = np.log(p / (1.0 - p))
    return q.sort_values(["partition", "window", "start_utc"]).reset_index(drop=True)


def load_xau_hourly():
    dsn = os.environ["NEON_DATABASE_URL"]
    with psycopg.connect(dsn, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                """
                SELECT observation_ts, value, retrieved_at
                FROM observations
                WHERE series_id=%s
                  AND observation_ts >= %s
                  AND observation_ts < %s
                ORDER BY observation_ts, retrieved_at
                """,
                (XAU_SERIES_ID, START, END),
            )
            rows = cur.fetchall()
        conn.rollback()
    if not rows:
        raise RuntimeError("NO_XAU_HOURLY_ROWS")
    x = pd.DataFrame(rows, columns=["ts", "value", "retrieved_at"])
    x["ts"] = pd.to_datetime(x["ts"], utc=True)
    x["value"] = pd.to_numeric(x["value"], errors="coerce")
    x = x.dropna(subset=["ts", "value"])
    x = x[x["value"] > 0].copy()
    x = x.sort_values(["ts", "retrieved_at"]).drop_duplicates("ts", keep="last")
    x["available_at_utc"] = x["ts"] + pd.Timedelta(hours=1)
    return x[["ts", "available_at_utc", "value"]].sort_values("ts").reset_index(drop=True)


def load_si_hourly():
    if not SI_ARCHIVE.exists():
        raise RuntimeError(f"SI_ARCHIVE_MISSING:{SI_ARCHIVE.name}")
    with gzip.open(SI_ARCHIVE, "rt", encoding="utf-8") as f:
        q = pd.read_csv(f)
    q = q[q["symbol"].astype(str).eq("SI.n.0")].copy()
    q["ts"] = pd.to_datetime(q["ts_event"], utc=True, errors="raise")
    q["value"] = pd.to_numeric(q["close"], errors="coerce")
    q = q.dropna(subset=["ts", "value"])
    q = q[q["value"] > 0].sort_values("ts").drop_duplicates("ts", keep="last")
    q["available_at_utc"] = q["ts"] + pd.Timedelta(hours=1)
    return q[["ts", "available_at_utc", "value"]].reset_index(drop=True)


def fetch_pl_hourly():
    key = os.environ.get("DATABENTO_API_KEY", "").strip()
    if not key:
        return None, {"status": "BLOCKED_DATABENTO_API_KEY_MISSING"}
    import databento as db

    client = db.Historical(key)
    req = dict(
        dataset=DATABENTO_DATASET,
        schema=DATABENTO_SCHEMA,
        symbols=[DATABENTO_PL_SYMBOL],
        stype_in="continuous",
        start=START,
        end=END,
    )
    try:
        est = float(client.metadata.get_cost(**req))
    except Exception as exc:
        return None, {"status": "BLOCKED_COST_PROBE_FAILED", "error": f"{type(exc).__name__}:{exc}"}
    if est > PL_COST_CAP_USD:
        return None, {
            "status": "BLOCKED_COST_CAP",
            "estimated_cost_usd": est,
            "cost_cap_usd": PL_COST_CAP_USD,
        }
    try:
        store = client.timeseries.get_range(**req)
        q = store.to_df().reset_index()
    except Exception as exc:
        return None, {
            "status": "BLOCKED_FETCH_FAILED",
            "estimated_cost_usd": est,
            "error": f"{type(exc).__name__}:{exc}",
        }
    if "ts_event" not in q.columns and "index" in q.columns:
        q = q.rename(columns={"index": "ts_event"})
    required = {"ts_event", "symbol", "close"}
    if not required.issubset(q.columns):
        return None, {
            "status": "BLOCKED_SCHEMA",
            "estimated_cost_usd": est,
            "columns": list(q.columns),
        }
    q = q[q["symbol"].astype(str).eq(DATABENTO_PL_SYMBOL)].copy()
    q["ts"] = pd.to_datetime(q["ts_event"], utc=True, errors="coerce")
    q["value"] = pd.to_numeric(q["close"], errors="coerce")
    q = q.dropna(subset=["ts", "value"])
    q = q[q["value"] > 0].sort_values("ts").drop_duplicates("ts", keep="last")
    if q.empty:
        return None, {"status": "BLOCKED_NO_ROWS", "estimated_cost_usd": est}
    q["available_at_utc"] = q["ts"] + pd.Timedelta(hours=1)
    years = {
        str(int(y)): int(len(g))
        for y, g in q.groupby(q["ts"].dt.year)
        if int(y) in (2022, 2023, 2024)
    }
    meta = {
        "status": "PASS",
        "estimated_cost_usd": est,
        "rows": int(len(q)),
        "first": q["ts"].min().isoformat(),
        "last": q["ts"].max().isoformat(),
        "rows_by_year": years,
        "symbol": DATABENTO_PL_SYMBOL,
        "schema": DATABENTO_SCHEMA,
    }
    return q[["ts", "available_at_utc", "value"]].reset_index(drop=True), meta


def build_path(raw, prefix):
    q = raw.copy().sort_values("ts").reset_index(drop=True)
    q["ts_ny"] = q["ts"].dt.tz_convert("America/New_York")
    q["local_date"] = q["ts_ny"].dt.date
    q["logp"] = np.log(q["value"].astype(float))
    q["hr"] = q["logp"].diff()
    for h in [1, 3, 6, 12, 24, 48]:
        q[f"{prefix}_ret_{h}"] = q["logp"] - q["logp"].shift(h)
    q[f"{prefix}_lag2"] = q["hr"].shift(2)
    first_log = q.groupby("local_date")["logp"].transform("first")
    q[f"{prefix}_session_ret"] = q["logp"] - first_log
    feats = [f"{prefix}_{x}" for x in PATH_BASE]
    q = q.dropna(subset=feats).copy()
    return q[["ts", "available_at_utc"] + feats].sort_values("available_at_utc").reset_index(drop=True), feats


def align_one(panel, hf, feats, tag):
    left = panel.sort_values("start_utc").copy()
    right = hf.sort_values("available_at_utc").copy()
    right = right.rename(columns={
        "ts": f"{tag}_bar_open_utc",
        "available_at_utc": f"{tag}_available_utc",
    })
    out = pd.merge_asof(
        left,
        right,
        left_on="start_utc",
        right_on=f"{tag}_available_utc",
        direction="backward",
    )
    out[f"{tag}_lag_minutes"] = (
        out["start_utc"] - out[f"{tag}_available_utc"]
    ).dt.total_seconds() / 60.0
    if (out[f"{tag}_available_utc"] > out["start_utc"]).fillna(False).any():
        raise RuntimeError(f"{tag}_FEATURE_LEAK")
    return out


def causal_replay(panel, model_name, features):
    rows = []
    for (part, win), g0 in panel.groupby(["partition", "window"], sort=True):
        g = g0.sort_values("start_utc").reset_index(drop=True)
        for bs in range(0, len(g), BLOCK):
            te = g.iloc[bs:bs + BLOCK].copy()
            if te.empty:
                continue
            cutoff = te["start_utc"].min()
            tr = g[(g["end_utc"] <= cutoff) & (g["start_utc"] < cutoff)].copy()
            if len(tr) < STRUCTURAL_MIN_TRAIN:
                continue
            m = make_model(balanced=False)
            m.fit(tr[features].astype(float), tr["y_up"].to_numpy(int))
            p = m.predict_proba(te[features].astype(float))[:, 1]
            for r, pp in zip(te.itertuples(index=False), p):
                rows.append({
                    "model": model_name,
                    "label_date": r.label_date,
                    "partition": part,
                    "window": win,
                    "start_utc": r.start_utc.isoformat(),
                    "end_utc": r.end_utc.isoformat(),
                    "year": int(r.start_utc.year),
                    "y_up": int(r.y_up),
                    "direction": r.direction,
                    "p_up": float(pp),
                    "pred": "UP" if pp >= 0.5 else "DOWN",
                    "train_n": int(len(tr)),
                })
    return pd.DataFrame(rows)


def source_stats(name, raw):
    if raw is None or raw.empty:
        return {"source": name, "rows": 0}
    q = raw.copy()
    return {
        "source": name,
        "rows": int(len(q)),
        "first": q["ts"].min().isoformat(),
        "last": q["ts"].max().isoformat(),
        "rows_2022": int((q["ts"].dt.year == 2022).sum()),
        "rows_2023": int((q["ts"].dt.year == 2023).sum()),
        "rows_2024": int((q["ts"].dt.year == 2024).sum()),
    }


def summarize_metrics(pred):
    rows = []
    if pred.empty:
        return pd.DataFrame()
    for (model, part, win, yr), g in pred.groupby(["model", "partition", "window", "year"], sort=True):
        rows.append({
            "model": model, "partition": part, "window": win, "period": str(yr),
            **metrics(g["y_up"], g["p_up"]),
        })
    for (model, part, win), g in pred.groupby(["model", "partition", "window"], sort=True):
        rows.append({
            "model": model, "partition": part, "window": win, "period": "2023-2024_SCORED",
            **metrics(g["y_up"], g["p_up"]),
        })
    return pd.DataFrame(rows)


def main():
    daily, daily_hashes = load_daily_session_panel()
    a1 = generate_fresh_a1(daily)

    xau_raw = load_xau_hourly()
    si_raw = load_si_hourly()
    pl_raw, pl_meta = fetch_pl_hourly()

    xau_h, xau_feats = build_path(xau_raw, "g")
    si_h, si_feats = build_path(si_raw, "si")

    panel = align_one(a1, xau_h, xau_feats, "g")
    panel = align_one(panel, si_h, si_feats, "si")

    source_rows = [
        source_stats("XAU_USD_TWELVE_1H_RESEARCH_V1", xau_raw),
        source_stats("SI.n.0 Databento", si_raw),
    ]
    variants = {
        "A1_XAU_PATH": ["base_logit"] + xau_feats,
        "A1_XAU_SI_PATH": ["base_logit"] + xau_feats + si_feats,
    }

    if pl_raw is not None:
        pl_h, pl_feats = build_path(pl_raw, "pl")
        panel = align_one(panel, pl_h, pl_feats, "pl")
        source_rows.append(source_stats("PL.n.0 Databento", pl_raw))
        variants["A1_XAU_SI_PL_PATH"] = ["base_logit"] + xau_feats + si_feats + pl_feats

    required = sorted(set(sum(variants.values(), [])))
    panel = panel.dropna(subset=required + ["direction", "start_utc", "end_utc"]).copy()

    # Source-quality guardrail, fixed before outcomes are scored.
    for tag in ["g", "si"] + (["pl"] if pl_raw is not None else []):
        panel = panel[panel[f"{tag}_lag_minutes"].between(0, 120, inclusive="both")].copy()

    preds = []
    for name, feats in variants.items():
        z = causal_replay(panel, name, feats)
        if not z.empty:
            preds.append(z)
    pred = pd.concat(preds, ignore_index=True) if preds else pd.DataFrame()
    mdf = summarize_metrics(pred)

    coverage = []
    for (part, win), g in panel.groupby(["partition", "window"], sort=True):
        coverage.append({
            "partition": part,
            "window": win,
            "common_feature_rows": int(len(g)),
            "first_start": g["start_utc"].min().isoformat(),
            "last_start": g["start_utc"].max().isoformat(),
            "median_xau_lag_minutes": float(g["g_lag_minutes"].median()),
            "median_si_lag_minutes": float(g["si_lag_minutes"].median()),
            "median_pl_lag_minutes": None if pl_raw is None else float(g["pl_lag_minutes"].median()),
        })
    cdf = pd.DataFrame(coverage)

    pred.to_csv(OUT / "crossmetal_predictions_2023_2024.csv", index=False)
    mdf.to_csv(OUT / "crossmetal_metrics_2023_2024.csv", index=False)
    cdf.to_csv(OUT / "crossmetal_common_coverage_2023_2024.csv", index=False)

    summary = {
        "status": "STRUCTURAL_IRIS_CROSSMETAL_V1_COMPLETE" if not pred.empty else "NO_SCORED_ROWS",
        "development_scope": "2023-2024 only; 2025/2026 unopened",
        "purpose": "Matched-sample causal ablation of intraday Silver/Platinum PATH added to fresh session A1 + XAU PATH.",
        "daily_a1": {
            "rows": int(len(a1)),
            "source_ready_rule": "strictly earlier America/New_York calendar-date Stak Gold/Silver/Platinum only",
            "stak_ref": base.STAK_REF,
            "annual_payload_sha256": daily_hashes,
        },
        "sources": source_rows,
        "pl_gate": pl_meta,
        "features": variants,
        "common_panel_rows": int(len(panel)),
        "metrics": mdf.to_dict("records"),
        "guardrails": [
            "Fresh A1 regenerated from raw daily Gold/Silver/Platinum; no archived NOVA/A1 predictions consumed.",
            "XAU hourly loaded from raw Neon/Twelve observations; close usable only at bar-open + 1h.",
            "SI/PL are Databento GLBX.MDP3 continuous futures exogenous PATH features, not spot-metal replacements.",
            "Primary SI/PL roll identity is n.0 fixed ex ante for this source experiment; no roll selected by outcome performance.",
            "All variants use the identical common feature panel when PL passes; otherwise A1_XAU_PATH vs A1_XAU_SI_PATH use an identical XAU+SI panel.",
            "Only matured same-window outcomes enter training.",
            "No 2025 or 2026 outcomes used.",
            "120-minute maximum feature staleness is fixed as a source-quality guardrail and is not performance-tuned.",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

    lines = [
        "# STRUCTURAL IRIS — CROSS-METAL INTRADAY PATH V1",
        "",
        f"**Status:** {summary['status']}",
        "",
        "- Development only: 2023–2024; 2025/2026 unopened.",
        "- Baseline: fresh A1 + XAU hourly PATH.",
        "- Challenger 1: baseline + SI hourly PATH.",
        "- Challenger 2: baseline + SI + PL hourly PATH when Platinum source gate passes.",
        f"- Platinum gate: **{pl_meta.get('status')}**",
        "",
        "## Matched metrics",
        "",
        "| Model | Partition | Window | Period | N | Accuracy | Balanced | UP recall | DOWN recall | Brier |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in mdf.itertuples(index=False):
        lines.append(
            f"| {r.model} | {r.partition} | {r.window} | {r.period} | {int(r.n)} | "
            f"{100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} |"
        )
    (OUT / "result.md").write_text("\n".join(lines) + "\n")

    print(json.dumps({
        "status": summary["status"],
        "pl_gate": pl_meta,
        "common_panel_rows": int(len(panel)),
        "metric_rows": int(len(mdf)),
        "models": list(variants),
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
