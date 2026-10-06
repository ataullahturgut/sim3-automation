from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
A0_PATH = AX / "tools" / "gold_session_nova_a0_core3_raw_replay_v1_20261006.py"
V1_PATH = AX / "tools" / "gold_session_structural_iris_crossmetal_v1_20261006.py"
OUT = AX / "SESSION_STRUCTURAL_IRIS_CROSSMETAL_V2_CLOCKSAFE_OUT"
OUT.mkdir(exist_ok=True)

def loadmod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

base = loadmod("nova_a0_raw", A0_PATH)
v1 = loadmod("crossmetal_v1", V1_PATH)

CORE3 = list(base.CORE3)
HORIZONS = [1, 3, 6, 12, 24, 48]
SEED = 20261006
BLOCK = 5
MIN_TRAIN = 120
MAX_SOURCE_LAG_MIN = 120.0

EXPECTED_CLOCKS = {
    ("SOBTI_5_ET", "ASIA_MORNING_LIT"): ("21:00", "23:30"),
    ("SOBTI_5_ET", "ASIA_AFTERNOON_LIT"): ("01:30", "03:30"),
    ("SOBTI_5_ET", "EUROPE_LIT"): ("03:30", "08:00"),
    ("SOBTI_5_ET", "NY_LONDON_LIT"): ("08:00", "14:30"),
    ("SOBTI_5_ET", "US_LATE_LIT"): ("14:30", "21:00"),
    ("WGC_2026_NY3", "ASIA"): ("18:00", "03:00"),
    ("WGC_2026_NY3", "EUROPE"): ("03:00", "08:00"),
    ("WGC_2026_NY3", "US"): ("08:00", "17:00"),
}

def make_model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(C=1.0, solver="lbfgs", max_iter=3000, random_state=SEED)),
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

def load_panel():
    metals, hashes = base.load_raw_metals()
    targets = base.verify_v5_targets()
    targets = targets[pd.to_datetime(targets["label_date"]).dt.year.isin([2023, 2024])].copy()
    panel = base.align_daily_features(targets, metals)
    panel = panel.dropna(subset=CORE3 + ["direction", "obs_date"]).copy()
    panel["start_utc"] = pd.to_datetime(panel["start_utc"], utc=True)
    panel["end_utc"] = pd.to_datetime(panel["end_utc"], utc=True)
    panel["y_up"] = (panel["direction"] == "UP").astype(int)
    return panel, hashes

def audit_target_clocks(panel):
    q = panel[["label_date", "partition", "window", "start_utc", "end_utc"]].copy()
    q["start_ny"] = q["start_utc"].dt.tz_convert("America/New_York")
    q["end_ny"] = q["end_utc"].dt.tz_convert("America/New_York")
    q["start_hm"] = q["start_ny"].dt.strftime("%H:%M")
    q["end_hm"] = q["end_ny"].dt.strftime("%H:%M")
    bad = []
    for r in q.itertuples(index=False):
        exp = EXPECTED_CLOCKS.get((r.partition, r.window))
        if exp is None:
            bad.append((r.label_date, r.partition, r.window, "UNKNOWN_WINDOW"))
            continue
        if (r.start_hm, r.end_hm) != exp:
            bad.append((r.label_date, r.partition, r.window, r.start_hm, r.end_hm, exp))
    if bad:
        raise RuntimeError(f"TARGET_CLOCK_AUDIT_FAIL n={len(bad)} sample={bad[:20]}")
    return q

def build_bar_features(raw, prefix):
    q = raw.copy().sort_values("ts").reset_index(drop=True)
    q["logp"] = np.log(pd.to_numeric(q["value"], errors="raise").astype(float))
    feats = []
    for h in HORIZONS:
        c = f"{prefix}_ret_{h}b"
        q[c] = q["logp"] - q["logp"].shift(h)
        feats.append(c)
    q = q.dropna(subset=feats).copy()
    return q[["ts", "available_at_utc"] + feats].sort_values("available_at_utc"), feats

def strict_align(panel, hf, feats, tag):
    right = hf.rename(columns={
        "ts": f"{tag}_bar_open_utc",
        "available_at_utc": f"{tag}_available_utc",
    }).sort_values(f"{tag}_available_utc")
    out = pd.merge_asof(
        panel.sort_values("start_utc"),
        right,
        left_on="start_utc",
        right_on=f"{tag}_available_utc",
        direction="backward",
        allow_exact_matches=False,
    )
    out[f"{tag}_lag_minutes"] = (
        out["start_utc"] - out[f"{tag}_available_utc"]
    ).dt.total_seconds() / 60.0

    valid = out[f"{tag}_available_utc"].notna()
    if (out.loc[valid, f"{tag}_available_utc"] >= out.loc[valid, "start_utc"]).any():
        raise RuntimeError(f"{tag}_STRICT_CLOCK_LEAK")
    if (out.loc[valid, f"{tag}_lag_minutes"] <= 0).any():
        raise RuntimeError(f"{tag}_NONPOSITIVE_LAG")

    return out

def timing_audit(panel, tags):
    rows = []
    for r in panel.itertuples(index=False):
        for tag in tags:
            avail = getattr(r, f"{tag}_available_utc")
            baropen = getattr(r, f"{tag}_bar_open_utc")
            lag = getattr(r, f"{tag}_lag_minutes")
            if pd.isna(avail):
                continue
            rows.append({
                "label_date": r.label_date,
                "partition": r.partition,
                "window": r.window,
                "target_start_utc": r.start_utc.isoformat(),
                "source": tag,
                "bar_open_utc": pd.Timestamp(baropen).isoformat(),
                "bar_close_available_utc": pd.Timestamp(avail).isoformat(),
                "lag_minutes": float(lag),
                "strictly_before_target": bool(pd.Timestamp(avail) < r.start_utc),
            })
    z = pd.DataFrame(rows)
    if not z.empty and not z["strictly_before_target"].all():
        raise RuntimeError("TIMING_AUDIT_FAIL")
    return z

def causal_replay(panel, name, features):
    rows = []
    for (part, win), g0 in panel.groupby(["partition", "window"], sort=True):
        g = g0.sort_values("start_utc").reset_index(drop=True)
        for bs in range(0, len(g), BLOCK):
            te = g.iloc[bs:bs + BLOCK].copy()
            if te.empty:
                continue
            cutoff = te["start_utc"].min()
            tr = g[(g["end_utc"] <= cutoff) & (g["start_utc"] < cutoff)].copy()
            if len(tr) < MIN_TRAIN:
                continue
            m = make_model()
            m.fit(tr[features].astype(float), tr["y_up"].to_numpy(int))
            p = m.predict_proba(te[features].astype(float))[:, 1]
            for r, pp in zip(te.itertuples(index=False), p):
                rows.append({
                    "model": name,
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

def summarize(pred):
    rows = []
    for (model, part, win, yr), g in pred.groupby(["model", "partition", "window", "year"], sort=True):
        rows.append({"model": model, "partition": part, "window": win, "period": str(yr), **metrics(g.y_up, g.p_up)})
    for (model, part, win), g in pred.groupby(["model", "partition", "window"], sort=True):
        rows.append({"model": model, "partition": part, "window": win, "period": "2023-2024_SCORED", **metrics(g.y_up, g.p_up)})
    return pd.DataFrame(rows)

def main():
    panel, hashes = load_panel()
    clock = audit_target_clocks(panel)

    xau_raw = v1.load_xau_hourly()
    si_raw = v1.load_si_hourly()
    pl_raw, pl_meta = v1.fetch_pl_hourly()
    if pl_raw is None:
        raise RuntimeError(f"PL_GATE_FAIL:{pl_meta}")

    xau_h, xau_f = build_bar_features(xau_raw, "g")
    si_h, si_f = build_bar_features(si_raw, "si")
    pl_h, pl_f = build_bar_features(pl_raw, "pl")

    panel = strict_align(panel, xau_h, xau_f, "g")
    panel = strict_align(panel, si_h, si_f, "si")
    panel = strict_align(panel, pl_h, pl_f, "pl")

    tags = ["g", "si", "pl"]
    required = CORE3 + xau_f + si_f + pl_f + ["direction"]
    panel = panel.dropna(subset=required).copy()
    for tag in tags:
        panel = panel[panel[f"{tag}_lag_minutes"].between(0.000001, MAX_SOURCE_LAG_MIN, inclusive="both")].copy()

    taudit = timing_audit(panel, tags)
    if taudit.empty:
        raise RuntimeError("EMPTY_TIMING_AUDIT")

    variants = {
        "CORE3_XAU_PATH_CLOCKSAFE": CORE3 + xau_f,
        "CORE3_XAU_SI_PATH_CLOCKSAFE": CORE3 + xau_f + si_f,
        "CORE3_XAU_SI_PL_PATH_CLOCKSAFE": CORE3 + xau_f + si_f + pl_f,
    }

    preds = []
    for name, feats in variants.items():
        z = causal_replay(panel, name, feats)
        if not z.empty:
            preds.append(z)
    pred = pd.concat(preds, ignore_index=True)
    mdf = summarize(pred)

    cov = []
    for (part, win), g in panel.groupby(["partition", "window"], sort=True):
        cov.append({
            "partition": part,
            "window": win,
            "rows": int(len(g)),
            "first_start": g.start_utc.min().isoformat(),
            "last_start": g.start_utc.max().isoformat(),
            "median_g_lag_min": float(g.g_lag_minutes.median()),
            "median_si_lag_min": float(g.si_lag_minutes.median()),
            "median_pl_lag_min": float(g.pl_lag_minutes.median()),
        })
    cdf = pd.DataFrame(cov)

    pred.to_csv(OUT / "predictions_2023_2024.csv", index=False)
    mdf.to_csv(OUT / "metrics_2023_2024.csv", index=False)
    cdf.to_csv(OUT / "coverage_2023_2024.csv", index=False)
    taudit.to_csv(OUT / "timing_audit_2023_2024.csv", index=False)

    summary = {
        "status": "CLOCKSAFE_ONE_STAGE_CROSSMETAL_V2_COMPLETE",
        "scope": "2023-2024 only; 2025/2026 unopened",
        "target_clock_audit": {
            "status": "PASS",
            "rows": int(len(clock)),
            "timezone": "America/New_York",
            "expected_windows": {f"{k[0]}::{k[1]}": list(v) for k, v in EXPECTED_CLOCKS.items()},
        },
        "source_clock_policy": {
            "bar_timestamp_semantics": "bar-open timestamp",
            "availability": "bar-open + 1h",
            "selection": "latest completed bar with available_at_utc STRICTLY LESS THAN target_start",
            "allow_exact_target_boundary": False,
            "max_source_lag_minutes": MAX_SOURCE_LAG_MIN,
            "session_ret_used": False,
            "path_return_semantics": "returns over the last N completed hourly observations; no target-window data included",
        },
        "pl_gate": pl_meta,
        "daily_stak_hashes": hashes,
        "common_panel_rows": int(len(panel)),
        "features": variants,
        "metrics": mdf.to_dict("records"),
        "guardrails": [
            "Target local clocks are asserted against frozen Sobti-5 and WGC-3 definitions using America/New_York.",
            "Every XAU/SI/PL feature bar must have completed strictly before target start; equality is rejected.",
            "No same-window outcome enters training before its end_utc has matured.",
            "No session_ret/calendar-day feature is used in V2.",
            "All variants use the identical common feature panel.",
            "2025 and 2026 outcomes remain unopened.",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

    lines = [
        "# STRUCTURAL IRIS CROSS-METAL V2 — CLOCK-SAFE ONE-STAGE DIAGNOSTIC",
        "",
        "**Status:** CLOCKSAFE_ONE_STAGE_CROSSMETAL_V2_COMPLETE",
        "",
        "- Scope: 2023–2024 only; 2025/2026 unopened.",
        "- Target clocks: frozen Sobti-5 and WGC-3, America/New_York, audit PASS.",
        "- Hourly source rule: latest completed bar with availability **strictly before** target start.",
        "- Exact-boundary hourly bars are excluded.",
        "- Ambiguous NY-calendar `session_ret` is excluded.",
        "- One-stage CORE3+PATH avoids the A1→Structural-IRIS double warm-up.",
        "",
        "## Metrics",
        "",
        "| Model | Partition | Window | Period | N | Acc | Balanced | UP recall | DOWN recall | Brier |",
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
        "target_clock_audit": summary["target_clock_audit"],
        "pl_gate": pl_meta,
        "common_panel_rows": int(len(panel)),
        "metric_rows": int(len(mdf)),
    }, indent=2, default=str))

if __name__ == "__main__":
    main()
