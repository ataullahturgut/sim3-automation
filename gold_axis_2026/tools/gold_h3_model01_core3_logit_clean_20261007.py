from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, log_loss

import gold_h3_clean_core_rebuild_v1 as clean
import gold_h3_nova_v1 as nova

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
OUT = AX / "H3_MODEL01_CORE3_LOGIT_OUT"
OUT.mkdir(exist_ok=True)


def metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(0.5 * (tp/max(tp+fn,1) + tn/max(tn+fp,1))),
        "brier": float(np.mean((p-y)**2)),
        "logloss": float(log_loss(y, p, labels=[0,1])),
        "up_recall": float(tp/max(tp+fn,1)),
        "down_recall": float(tn/max(tn+fp,1)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def main():
    panel, audit = clean.patched_readiness()

    # Binding H3 identity guard.
    required = ["feature_cutoff_date","forecast_issue_date","target_end_date_h3","target_r3"] + list(nova.CORE3)
    miss = [c for c in required if c not in panel.columns]
    if miss:
        raise RuntimeError(f"MISSING_REQUIRED_COLUMNS {miss}")

    # Rebuild the original global CORE3 Logistic only.
    led = nova.run_base_sequence(panel, 2017, 2026)
    out = led[[
        "feature_cutoff_date","forecast_issue_date","target_end_date_h3",
        "year","month","target_r3","y_up","p_A0_global","train_n"
    ]].copy()
    out = out.rename(columns={"p_A0_global":"p_up"})
    out["pred_direction"] = np.where(out.p_up >= 0.5, "UP", "DOWN")
    out["actual_direction"] = np.where(out.y_up == 1, "UP", "DOWN")
    out["correct"] = out.pred_direction == out.actual_direction
    out.to_csv(OUT / "predictions.csv", index=False)

    rows = []
    specs = [
        ("DEV_2022_2024", out.year.between(2022, 2024)),
        ("2022", out.year == 2022),
        ("2023", out.year == 2023),
        ("2024", out.year == 2024),
        ("FROZEN_2025", out.year == 2025),
        ("2026", out.year == 2026),
        ("2025_2026", out.year.isin([2025, 2026])),
    ]
    for label, mask in specs:
        z = out[mask].copy()
        if z.empty:
            continue
        rows.append({"period": label, **metrics(z.y_up, z.p_up)})

    m = pd.DataFrame(rows)
    m.to_csv(OUT / "metrics.csv", index=False)

    summary = {
        "status": "H3_MODEL01_CORE3_LOGIT_COMPLETE",
        "model": "CORE3_LOGISTIC_L2",
        "target": "H3 direction = sign(log(P[t+3]/P[t]))",
        "horizon_semantics": "t+3 means third retained Gold observation, not 3 calendar days",
        "features": list(nova.CORE3),
        "data_chain": "clean H3 chain using pinned StakTrakr R2 readiness plus confirmed 2026-02-27 integrity correction",
        "integrity_patch": audit,
        "chronology": "expanding causal fit; only rows with target_end_date_h3 <= current feature cutoff can train",
        "threshold": 0.5,
        "metrics": m.to_dict("records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")

    lines = [
        "# H3 MODEL 01 — CORE3 LOGISTIC",
        "",
        "**Status:** COMPLETE",
        "",
        "**Target:** H3 direction = sign(log(P[t+3]/P[t]))",
        "",
        "- t+3 = third retained Gold observation; not three calendar days.",
        "- Features = Gold/Silver/Platinum CORE3 only.",
        "- Model = StandardScaler + LogisticRegression(L2, C=1.0).",
        "- Causal training: only already-matured H3 outcomes.",
        "- Data = clean H3 chain with confirmed 2026-02-27 integrity correction.",
        "",
        "| Period | N | Accuracy | BA | Brier | UP recall | DOWN recall |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in m.itertuples(index=False):
        lines.append(
            f"| {r.period} | {r.n} | {100*r.accuracy:.2f}% | "
            f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
        )
    (OUT / "result.md").write_text("\n".join(lines) + "\n")
    print((OUT / "result.md").read_text())


if __name__ == "__main__":
    main()
