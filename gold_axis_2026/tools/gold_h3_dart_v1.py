from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import betainc

from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_dart_v1_out"))
SENTRY_LEDGER = ROOT / "gold_axis_2026" / "GOLD_H3_SENTRY_V1_PREDICTIONS_2026-10-02.csv"
OUT.mkdir(parents=True, exist_ok=True)

HAZARD = 1.0 / 20.0
MAX_RUN = 120
MIN_DISAGREEMENTS = 8
ENTER_PROB = 0.90
ENTER_Q = 0.60
EXIT_PROB = 0.10
EXIT_Q = 0.40
A0 = 1.0
B0 = 1.0


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
        "false_call_rate": float(np.mean(pred != y)),
        "prediction_std": float(np.std(p)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


class BetaBernoulliBOCPD:
    def __init__(self):
        # One empty-run component before the first event.
        self.mass = np.array([1.0], dtype=float)
        self.alpha = np.array([A0], dtype=float)
        self.beta = np.array([B0], dtype=float)
        self.runlen = np.array([0], dtype=int)
        self.n = 0

    def update(self, x: int):
        x = int(x)
        if x not in (0, 1):
            raise ValueError(x)

        # Prior predictive for a new regime.
        prior_pred = A0 / (A0 + B0) if x == 1 else B0 / (A0 + B0)

        pred_old = np.where(
            x == 1,
            self.alpha / (self.alpha + self.beta),
            self.beta / (self.alpha + self.beta),
        )

        growth_mass = self.mass * (1.0 - HAZARD) * pred_old
        cp_mass = float(np.sum(self.mass) * HAZARD * prior_pred)

        new_mass = np.concatenate([[cp_mass], growth_mass])
        new_alpha = np.concatenate([
            [A0 + x],
            self.alpha + x,
        ])
        new_beta = np.concatenate([
            [B0 + (1 - x)],
            self.beta + (1 - x),
        ])
        new_runlen = np.concatenate([
            [1],
            self.runlen + 1,
        ])

        # Truncate long run-length tail by retaining the highest-mass components
        # subject to the run-length cap. This keeps the online recursion bounded.
        keep = new_runlen <= MAX_RUN
        new_mass = new_mass[keep]
        new_alpha = new_alpha[keep]
        new_beta = new_beta[keep]
        new_runlen = new_runlen[keep]

        s = float(np.sum(new_mass))
        if not np.isfinite(s) or s <= 0:
            raise RuntimeError("BOCPD_MASS_COLLAPSE")
        new_mass /= s

        self.mass = new_mass
        self.alpha = new_alpha
        self.beta = new_beta
        self.runlen = new_runlen
        self.n += 1

    def summary(self):
        means = self.alpha / (self.alpha + self.beta)
        q = float(np.sum(self.mass * means))
        prob_path = float(np.sum(self.mass * (1.0 - betainc(self.alpha, self.beta, 0.5))))
        erun = float(np.sum(self.mass * self.runlen))
        cp_prob = float(self.mass[self.runlen == 1].sum()) if np.any(self.runlen == 1) else 0.0
        return {
            "q_path": q,
            "prob_path_superior": prob_path,
            "expected_run_length": erun,
            "changepoint_mass": cp_prob,
            "matured_disagreements": int(self.n),
        }


def build_disagreement_events(expert):
    g = expert.copy().sort_values(["target_end_date_h3", "forecast_issue_date"]).reset_index(drop=True)
    s = (g.p_structural >= 0.5).astype(int)
    p = (g.p_path_global >= 0.5).astype(int)
    g["disagree"] = s != p
    d = g[g.disagree].copy()
    d["struct_correct"] = (s[g.disagree].to_numpy() == d.y_up.to_numpy(int))
    d["path_correct"] = (p[g.disagree].to_numpy() == d.y_up.to_numpy(int))
    if not ((d.struct_correct.astype(int) + d.path_correct.astype(int)) == 1).all():
        raise RuntimeError("DISAGREEMENT_NOT_EXCLUSIVE")
    d["x_path_win"] = d.path_correct.astype(int)
    return d.reset_index(drop=True)


def apply_dart(expert):
    g = expert.sort_values("forecast_issue_date").copy().reset_index(drop=True)
    d = build_disagreement_events(expert)

    detector = BetaBernoulliBOCPD()
    state = "STRUCTURAL_IRIS"
    processed = set()
    rows = []
    switches = []

    for r in g.itertuples():
        cutoff = pd.Timestamp(r.feature_cutoff_date)

        matured = d[
            (d.target_end_date_h3 <= cutoff)
            & (~d.index.isin(processed))
        ].copy().sort_values(["target_end_date_h3", "forecast_issue_date"])

        for idx, ev in matured.iterrows():
            detector.update(int(ev.x_path_win))
            processed.add(int(idx))

        summ = detector.summary()
        old = state

        if summ["matured_disagreements"] >= MIN_DISAGREEMENTS:
            if (
                state == "STRUCTURAL_IRIS"
                and summ["prob_path_superior"] >= ENTER_PROB
                and summ["q_path"] >= ENTER_Q
            ):
                state = "PATH_GLOBAL"
            elif (
                state == "PATH_GLOBAL"
                and summ["prob_path_superior"] <= EXIT_PROB
                and summ["q_path"] <= EXIT_Q
            ):
                state = "STRUCTURAL_IRIS"

        if state != old:
            switches.append({
                "forecast_issue_date": str(pd.Timestamp(r.forecast_issue_date).date()),
                "from": old,
                "to": state,
                **summ,
            })

        ps = float(r.p_structural)
        pp = float(r.p_path_global)
        pout = pp if state == "PATH_GLOBAL" else ps

        rows.append({
            "feature_cutoff_date": r.feature_cutoff_date,
            "forecast_issue_date": r.forecast_issue_date,
            "target_end_date_h3": r.target_end_date_h3,
            "year": int(r.year),
            "month": str(r.month),
            "y_up": int(r.y_up),
            "target_r3": float(r.target_r3),
            "p_structural": ps,
            "p_path_global": pp,
            "active_expert": state,
            "p_dart": pout,
            **summ,
        })

    return pd.DataFrame(rows), pd.DataFrame(switches), d


def score_periods(g):
    rows = []
    specs = [
        ("2022_H2", g.forecast_issue_date.between("2022-07-01", "2022-12-31")),
        ("2023", g.year == 2023),
        ("2024", g.year == 2024),
        ("2025", g.year == 2025),
        ("2026", g.year == 2026),
        ("2023-2024", g.year.isin([2023, 2024])),
        ("2025-2026", g.year.isin([2025, 2026])),
    ]
    for label, mask in specs:
        z = g[mask].copy()
        if z.empty:
            continue
        rows.append({"model": "STRUCTURAL_IRIS", "period": label, **metrics(z.y_up, z.p_structural)})
        rows.append({"model": "PATH_GLOBAL", "period": label, **metrics(z.y_up, z.p_path_global)})
        rows.append({"model": "DART", "period": label, **metrics(z.y_up, z.p_dart)})
    return pd.DataFrame(rows)


def confirmation(mdf, switches):
    checks = []
    ok = True
    for yr in ["2023", "2024"]:
        b = mdf[(mdf.model == "STRUCTURAL_IRIS") & (mdf.period == yr)].iloc[0]
        d = mdf[(mdf.model == "DART") & (mdf.period == yr)].iloc[0]
        passed = bool(
            d.accuracy + 0.01 + 1e-12 >= b.accuracy
            and d.brier <= b.brier + 0.003 + 1e-12
        )
        checks.append({
            "period": yr,
            "pass": passed,
            "base_accuracy": float(b.accuracy),
            "dart_accuracy": float(d.accuracy),
            "base_balanced_accuracy": float(b.balanced_accuracy),
            "dart_balanced_accuracy": float(d.balanced_accuracy),
            "base_brier": float(b.brier),
            "dart_brier": float(d.brier),
        })
        ok = ok and passed

    b = mdf[(mdf.model == "STRUCTURAL_IRIS") & (mdf.period == "2023-2024")].iloc[0]
    d = mdf[(mdf.model == "DART") & (mdf.period == "2023-2024")].iloc[0]
    agg_ok = bool(d.balanced_accuracy + 0.01 + 1e-12 >= b.balanced_accuracy)
    switches_ok = len(switches) > 0
    return bool(ok and agg_ok and switches_ok), checks, agg_ok, switches_ok


def annual_state(g):
    rows = []
    for yr, z in g[g.year.between(2022, 2026)].groupby("year"):
        rows.append({
            "year": int(yr),
            "n": int(len(z)),
            "path_share": float((z.active_expert == "PATH_GLOBAL").mean()),
            "mean_q_path": float(z.q_path.mean()),
            "mean_prob_path_superior": float(z.prob_path_superior.mean()),
            "last_matured_disagreements": int(z.matured_disagreements.iloc[-1]),
            "mean_expected_run_length": float(z.expected_run_length.mean()),
        })
    return pd.DataFrame(rows)


def rescue_2026(g):
    z = g[g.year == 2026].copy()
    y = z.y_up.to_numpy(int)
    b = (z.p_structural.to_numpy(float) >= 0.5).astype(int)
    d = (z.p_dart.to_numpy(float) >= 0.5).astype(int)
    b_ok = b == y
    d_ok = d == y
    return {
        "n": int(len(z)),
        "base_accuracy": float(b_ok.mean()),
        "dart_accuracy": float(d_ok.mean()),
        "rescued": int(np.sum((~b_ok) & d_ok)),
        "broken": int(np.sum(b_ok & (~d_ok))),
        "net_rescue": int(np.sum((~b_ok) & d_ok) - np.sum(b_ok & (~d_ok))),
        "path_origins": int(np.sum(z.active_expert == "PATH_GLOBAL")),
    }


def monthly_2026(g):
    rows = []
    for mo, z in g[g.year == 2026].groupby("month"):
        for name, col in [
            ("STRUCTURAL_IRIS", "p_structural"),
            ("PATH_GLOBAL", "p_path_global"),
            ("DART", "p_dart"),
        ]:
            rows.append({"model": name, "month": mo, **metrics(z.y_up, z[col])})
        rows.append({
            "model": "STATE",
            "month": mo,
            "n": int(len(z)),
            "path_share": float((z.active_expert == "PATH_GLOBAL").mean()),
            "mean_q_path": float(z.q_path.mean()),
            "mean_prob_path_superior": float(z.prob_path_superior.mean()),
        })
    return pd.DataFrame(rows)


def main():
    expert = pd.read_csv(SENTRY_LEDGER)
    for col in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
        expert[col] = pd.to_datetime(expert[col], errors="raise")
    required = ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3",
                "year", "month", "y_up", "target_r3", "p_structural", "p_path_global"]
    missing = [x for x in required if x not in expert.columns]
    if missing:
        raise RuntimeError(f"SENTRY_LEDGER_MISSING={missing}")
    expert = expert[required].copy().sort_values("forecast_issue_date").reset_index(drop=True)

    dart, switches, disagreements = apply_dart(expert)
    dart.to_csv(OUT / "dart_v1_predictions.csv", index=False)
    switches.to_csv(OUT / "dart_v1_switches.csv", index=False)
    disagreements.to_csv(OUT / "dart_v1_disagreement_events.csv", index=False)

    mdf = score_periods(dart)
    mdf.to_csv(OUT / "dart_v1_metrics.csv", index=False)

    states = annual_state(dart)
    states.to_csv(OUT / "dart_v1_state_summary.csv", index=False)

    ok, checks, agg_ok, switches_ok = confirmation(mdf, switches)
    status = "MECHANISM_PASS" if ok else "NOT_PROMOTED_CONFIRM_FAIL"

    resc = rescue_2026(dart)
    pd.DataFrame([resc]).to_csv(OUT / "dart_v1_2026_rescue.csv", index=False)

    m26 = monthly_2026(dart)
    m26.to_csv(OUT / "dart_v1_2026_monthly.csv", index=False)

    summary = {
        "schema": "DART_H3_V1",
        "status": status,
        "expert_ledger_source": "GOLD_H3_SENTRY_V1_PREDICTIONS_2026-10-02.csv",
        "rule": {
            "hazard": HAZARD,
            "max_run": MAX_RUN,
            "min_disagreements": MIN_DISAGREEMENTS,
            "enter_prob": ENTER_PROB,
            "enter_q": ENTER_Q,
            "exit_prob": EXIT_PROB,
            "exit_q": EXIT_Q,
        },
        "confirmation_pass": bool(ok),
        "confirmation_checks": checks,
        "aggregate_2023_2024_balanced_guard": bool(agg_ok),
        "switches_present": bool(switches_ok),
        "switches": switches.to_dict(orient="records"),
        "annual_state": states.to_dict(orient="records"),
        "rescue_2026": resc,
        "metrics": mdf.to_dict(orient="records"),
        "total_disagreement_events": int(len(disagreements)),
    }
    (OUT / "dart_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# DART-H3 V1 — DISAGREEMENT-AWARE REGIME TRANSFER RESULT", "",
        f"**Status:** **{status}**  ",
        f"**BOCPD hazard:** **1/20 disagreement events**  ",
        f"**Enter PATH:** Pr(theta>0.5)>=0.90 and q_path>=0.60  ",
        f"**Exit PATH:** Pr(theta>0.5)<=0.10 and q_path<=0.40  ",
        f"**2023 + 2024 confirmation:** **{ok}**", "",
        "## Period metrics", "",
        "| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for period in ["2022_H2", "2023", "2024", "2025", "2026", "2025-2026"]:
        for model in ["STRUCTURAL_IRIS", "PATH_GLOBAL", "DART"]:
            q = mdf[(mdf.model == model) & (mdf.period == period)]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(
                f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
            )

    lines += ["", "## Annual DART state", "",
              "| Year | PATH share | Mean q_path | Mean Pr(PATH superior) | Matured disagreements by year-end |",
              "|---:|---:|---:|---:|---:|"]
    for r in states.itertuples():
        lines.append(
            f"| {int(r.year)} | {100*r.path_share:.1f}% | {r.mean_q_path:.3f} | "
            f"{r.mean_prob_path_superior:.3f} | {int(r.last_matured_disagreements)} |"
        )

    lines += ["", "## State switches", ""]
    if switches.empty:
        lines.append("- none")
    else:
        for _, r in switches.iterrows():
            lines.append(
                f"- {r['forecast_issue_date']}: {r['from']} -> {r['to']}; "
                f"q_path={r['q_path']:.3f}; Pr(PATH superior)={r['prob_path_superior']:.3f}; "
                f"matured disagreements={int(r['matured_disagreements'])}"
            )

    lines += ["", "## 2026 rescue", "",
              f"- Structural accuracy: **{100*resc['base_accuracy']:.2f}%**",
              f"- DART accuracy: **{100*resc['dart_accuracy']:.2f}%**",
              f"- rescued calls: **{resc['rescued']}**",
              f"- broken calls: **{resc['broken']}**",
              f"- net rescue: **{resc['net_rescue']:+d}**",
              f"- PATH-active origins: **{resc['path_origins']} / {resc['n']}**", "",
              "## Governance", "",
              "DART thresholds and hazard were fixed before this run. "
              "BOCPD updates used only expert-disagreement outcomes whose H3 target had already matured by the current feature cutoff. "
              "2025/2026 were not used to tune V1."]

    (OUT / "DART_V1_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "DART_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
