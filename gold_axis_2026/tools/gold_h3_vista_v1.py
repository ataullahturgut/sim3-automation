from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import betainc

from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score

import gold_h3_iris_v1 as iris

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_vista_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

SENTRY = ROOT / "gold_axis_2026" / "GOLD_H3_SENTRY_V1_PREDICTIONS_2026-10-02.csv"
DART = ROOT / "gold_axis_2026" / "GOLD_H3_DART_V1_PREDICTIONS_2026-10-02.csv"

BASE_HAZARD = 0.05
HAZARD_MIN = 0.02
HAZARD_MAX = 0.125
KAPPA = math.log(4.0) / 0.8
MAX_RUN = 120
MIN_DISAGREEMENTS = 8
ENTER_PROB = 0.90
ENTER_Q = 0.60
EXIT_PROB = 0.10
EXIT_Q = 0.40
A0 = 1.0
B0 = 1.0
PCT_WINDOW = 504
PCT_MIN_HISTORY = 60

SEED = 20261002
REPS = 10000
BLOCKS = [5, 10]


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


def load_hourly_state():
    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError("VISTA_SOURCE_BRIDGE_FAIL")

    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    hourly = pd.concat([hist, ext], ignore_index=True)
    hourly = hourly.sort_values("ts").drop_duplicates("ts", keep="first").reset_index(drop=True)

    anchors = iris.build_anchor_features(hourly)
    need = ["local_date", "h_rv_24", "h_jump_concentration_24"]
    state = anchors[need].copy().sort_values("local_date").reset_index(drop=True)

    rv_pct = []
    jump_pct = []
    shock = []
    hazard = []

    for i, r in state.iterrows():
        lo = max(0, i - PCT_WINDOW)
        past = state.iloc[lo:i]
        if len(past) < PCT_MIN_HISTORY:
            rp = jp = 0.5
        else:
            rv = past.h_rv_24.to_numpy(float)
            ju = past.h_jump_concentration_24.to_numpy(float)
            rp = float((np.sum(rv <= float(r.h_rv_24)) + 0.5) / (len(rv) + 1.0))
            jp = float((np.sum(ju <= float(r.h_jump_concentration_24)) + 0.5) / (len(ju) + 1.0))
        sc = 0.70 * rp + 0.30 * jp
        hz = BASE_HAZARD * math.exp(KAPPA * (sc - 0.5))
        hz = float(np.clip(hz, HAZARD_MIN, HAZARD_MAX))
        rv_pct.append(rp)
        jump_pct.append(jp)
        shock.append(sc)
        hazard.append(hz)

    state["rv_pct"] = rv_pct
    state["jump_pct"] = jump_pct
    state["shock_score"] = shock
    state["dynamic_hazard"] = hazard
    return state, bridge, api_calls


def load_expert_ledger(state):
    s = pd.read_csv(SENTRY)
    d = pd.read_csv(DART)
    for x in [s, d]:
        for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
            x[c] = pd.to_datetime(x[c], errors="raise")

    keep = [
        "feature_cutoff_date", "forecast_issue_date", "target_end_date_h3",
        "year", "month", "y_up", "target_r3", "p_structural", "p_path_global",
        "p_sentry",
    ]
    s = s[keep].copy()
    d2 = d[["forecast_issue_date", "p_dart"]].copy()

    x = s.merge(d2, on="forecast_issue_date", how="left", validate="one_to_one")
    x["feature_date"] = x.feature_cutoff_date.dt.date
    x = x.merge(
        state,
        left_on="feature_date",
        right_on="local_date",
        how="left",
        validate="many_to_one",
    )
    if x[["p_dart", "dynamic_hazard", "shock_score"]].isna().any().any():
        bad = x[x[["p_dart", "dynamic_hazard", "shock_score"]].isna().any(axis=1)]
        raise RuntimeError(f"VISTA_STATE_MATCH_FAIL n={len(bad)}")
    return x.sort_values("forecast_issue_date").reset_index(drop=True)


class DynamicBetaBernoulliBOCPD:
    def __init__(self):
        self.mass = np.array([1.0], dtype=float)
        self.alpha = np.array([A0], dtype=float)
        self.beta = np.array([B0], dtype=float)
        self.runlen = np.array([0], dtype=int)
        self.n = 0

    def update(self, x: int, hazard: float):
        x = int(x)
        h = float(np.clip(hazard, HAZARD_MIN, HAZARD_MAX))

        prior_pred = A0 / (A0 + B0) if x == 1 else B0 / (A0 + B0)
        pred_old = np.where(
            x == 1,
            self.alpha / (self.alpha + self.beta),
            self.beta / (self.alpha + self.beta),
        )

        growth_mass = self.mass * (1.0 - h) * pred_old
        cp_mass = float(np.sum(self.mass) * h * prior_pred)

        new_mass = np.concatenate([[cp_mass], growth_mass])
        new_alpha = np.concatenate([[A0 + x], self.alpha + x])
        new_beta = np.concatenate([[B0 + (1 - x)], self.beta + (1 - x)])
        new_runlen = np.concatenate([[1], self.runlen + 1])

        keep = new_runlen <= MAX_RUN
        new_mass = new_mass[keep]
        new_alpha = new_alpha[keep]
        new_beta = new_beta[keep]
        new_runlen = new_runlen[keep]

        total = float(np.sum(new_mass))
        if total <= 0 or not np.isfinite(total):
            raise RuntimeError("VISTA_BOCPD_MASS_COLLAPSE")

        self.mass = new_mass / total
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
    s_pred = (g.p_structural >= 0.5).astype(int)
    p_pred = (g.p_path_global >= 0.5).astype(int)
    g["disagree"] = s_pred != p_pred
    d = g[g.disagree].copy()
    d["struct_correct"] = (
        (d.p_structural.to_numpy(float) >= 0.5).astype(int) == d.y_up.to_numpy(int)
    )
    d["path_correct"] = (
        (d.p_path_global.to_numpy(float) >= 0.5).astype(int) == d.y_up.to_numpy(int)
    )
    if not ((d.struct_correct.astype(int) + d.path_correct.astype(int)) == 1).all():
        raise RuntimeError("VISTA_DISAGREEMENT_NOT_EXCLUSIVE")
    d["x_path_win"] = d.path_correct.astype(int)
    return d.reset_index(drop=True)


def apply_vista(expert):
    g = expert.sort_values("forecast_issue_date").copy().reset_index(drop=True)
    devents = build_disagreement_events(expert)

    detector = DynamicBetaBernoulliBOCPD()
    processed = set()
    state = "STRUCTURAL_IRIS"
    rows = []
    switches = []

    for r in g.itertuples():
        cutoff = pd.Timestamp(r.feature_cutoff_date)
        matured = devents[
            (devents.target_end_date_h3 <= cutoff)
            & (~devents.index.isin(processed))
        ].copy().sort_values(["target_end_date_h3", "forecast_issue_date"])

        for idx, ev in matured.iterrows():
            detector.update(int(ev.x_path_win), float(ev.dynamic_hazard))
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
                "origin_shock_score": float(r.shock_score),
                "origin_hazard": float(r.dynamic_hazard),
                **summ,
            })

        pv = float(r.p_path_global) if state == "PATH_GLOBAL" else float(r.p_structural)

        rows.append({
            "feature_cutoff_date": r.feature_cutoff_date,
            "forecast_issue_date": r.forecast_issue_date,
            "target_end_date_h3": r.target_end_date_h3,
            "year": int(r.year),
            "month": str(r.month),
            "y_up": int(r.y_up),
            "target_r3": float(r.target_r3),
            "p_structural": float(r.p_structural),
            "p_path_global": float(r.p_path_global),
            "p_sentry": float(r.p_sentry),
            "p_dart": float(r.p_dart),
            "p_vista": pv,
            "active_expert": state,
            "h_rv_24": float(r.h_rv_24),
            "h_jump_concentration_24": float(r.h_jump_concentration_24),
            "rv_pct": float(r.rv_pct),
            "jump_pct": float(r.jump_pct),
            "shock_score": float(r.shock_score),
            "dynamic_hazard": float(r.dynamic_hazard),
            **summ,
        })

    return pd.DataFrame(rows), pd.DataFrame(switches), devents


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
    models = [
        ("STRUCTURAL_IRIS", "p_structural"),
        ("PATH_GLOBAL", "p_path_global"),
        ("SENTRY", "p_sentry"),
        ("DART", "p_dart"),
        ("VISTA", "p_vista"),
    ]
    for label, mask in specs:
        z = g[mask].copy()
        if z.empty:
            continue
        for model, col in models:
            rows.append({"model": model, "period": label, **metrics(z.y_up, z[col])})
    return pd.DataFrame(rows)


def confirmation(mdf, switches):
    checks = []
    ok = True
    for yr in ["2023", "2024"]:
        b = mdf[(mdf.model == "STRUCTURAL_IRIS") & (mdf.period == yr)].iloc[0]
        v = mdf[(mdf.model == "VISTA") & (mdf.period == yr)].iloc[0]
        passed = bool(
            v.accuracy + 0.01 + 1e-12 >= b.accuracy
            and v.brier <= b.brier + 0.003 + 1e-12
        )
        checks.append({
            "period": yr,
            "pass": passed,
            "base_accuracy": float(b.accuracy),
            "vista_accuracy": float(v.accuracy),
            "base_balanced_accuracy": float(b.balanced_accuracy),
            "vista_balanced_accuracy": float(v.balanced_accuracy),
            "base_brier": float(b.brier),
            "vista_brier": float(v.brier),
        })
        ok = ok and passed

    b = mdf[(mdf.model == "STRUCTURAL_IRIS") & (mdf.period == "2023-2024")].iloc[0]
    v = mdf[(mdf.model == "VISTA") & (mdf.period == "2023-2024")].iloc[0]
    agg_ok = bool(v.balanced_accuracy + 0.01 + 1e-12 >= b.balanced_accuracy)
    switches_ok = len(switches) > 0
    return bool(ok and agg_ok and switches_ok), checks, agg_ok, switches_ok


def state_summary(g):
    rows = []
    for yr, z in g[g.year.between(2022, 2026)].groupby("year"):
        rows.append({
            "year": int(yr),
            "n": int(len(z)),
            "path_share": float((z.active_expert == "PATH_GLOBAL").mean()),
            "mean_shock_score": float(z.shock_score.mean()),
            "mean_dynamic_hazard": float(z.dynamic_hazard.mean()),
            "p90_dynamic_hazard": float(z.dynamic_hazard.quantile(0.90)),
            "mean_q_path": float(z.q_path.mean()),
            "mean_prob_path_superior": float(z.prob_path_superior.mean()),
            "last_matured_disagreements": int(z.matured_disagreements.iloc[-1]),
        })
    return pd.DataFrame(rows)


def rescue_2026(g):
    z = g[g.year == 2026].copy()
    y = z.y_up.to_numpy(int)
    b = (z.p_structural.to_numpy(float) >= 0.5).astype(int)
    v = (z.p_vista.to_numpy(float) >= 0.5).astype(int)
    b_ok = b == y
    v_ok = v == y
    return {
        "n": int(len(z)),
        "base_accuracy": float(b_ok.mean()),
        "vista_accuracy": float(v_ok.mean()),
        "rescued": int(np.sum((~b_ok) & v_ok)),
        "broken": int(np.sum(b_ok & (~v_ok))),
        "net_rescue": int(np.sum((~b_ok) & v_ok) - np.sum(b_ok & (~v_ok))),
        "path_origins": int(np.sum(z.active_expert == "PATH_GLOBAL")),
    }


def logloss_row(y, p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    y = np.asarray(y, int)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def diff_arrays(y, cand, base):
    y = np.asarray(y, int)
    cand = np.asarray(cand, float)
    base = np.asarray(base, float)
    return {
        "accuracy": ((cand >= 0.5).astype(int) == y).astype(float)
                    - ((base >= 0.5).astype(int) == y).astype(float),
        "brier": (cand - y) ** 2 - (base - y) ** 2,
        "logloss": logloss_row(y, cand) - logloss_row(y, base),
    }


def circular_boot(diff, block_len, rng):
    diff = np.asarray(diff, float)
    n = len(diff)
    nblocks = int(np.ceil(n / block_len))
    vals = np.empty(REPS, float)
    offsets = np.arange(block_len, dtype=int)
    batch = 500
    for st in range(0, REPS, batch):
        m = min(batch, REPS - st)
        starts = rng.integers(0, n, size=(m, nblocks))
        idx = (starts[:, :, None] + offsets[None, None, :]) % n
        idx = idx.reshape(m, -1)[:, :n]
        vals[st:st + m] = diff[idx].mean(axis=1)
    return vals


def inference(g):
    comparisons = {
        "VISTA_vs_DART": ("p_vista", "p_dart"),
        "VISTA_vs_SENTRY": ("p_vista", "p_sentry"),
        "VISTA_vs_STRUCTURAL": ("p_vista", "p_structural"),
    }
    periods = {
        "2026": g.year == 2026,
        "2025-2026": g.year.isin([2025, 2026]),
    }
    rows = []
    seed_i = 0
    for period, mask in periods.items():
        z = g[mask].copy()
        y = z.y_up.to_numpy(int)
        for comp, (cand_col, base_col) in comparisons.items():
            diffs = diff_arrays(y, z[cand_col], z[base_col])
            for metric, diff in diffs.items():
                for block_len in BLOCKS:
                    seed_i += 1
                    rng = np.random.default_rng(SEED + seed_i)
                    boot = circular_boot(diff, block_len, rng)
                    lo, hi = np.quantile(boot, [0.025, 0.975])
                    improve = float(np.mean(boot > 0)) if metric == "accuracy" else float(np.mean(boot < 0))
                    rows.append({
                        "period": period,
                        "comparison": comp,
                        "metric": metric,
                        "block_len": block_len,
                        "n": int(len(z)),
                        "observed_diff": float(np.mean(diff)),
                        "ci95_low": float(lo),
                        "ci95_high": float(hi),
                        "bootstrap_improve_share": improve,
                    })
    return pd.DataFrame(rows)


def main():
    state, bridge, api_calls = load_hourly_state()
    expert = load_expert_ledger(state)

    vista, switches, devents = apply_vista(expert)
    vista.to_csv(OUT / "vista_v1_predictions.csv", index=False)
    switches.to_csv(OUT / "vista_v1_switches.csv", index=False)
    devents.to_csv(OUT / "vista_v1_disagreement_events.csv", index=False)

    mdf = score_periods(vista)
    mdf.to_csv(OUT / "vista_v1_metrics.csv", index=False)

    st = state_summary(vista)
    st.to_csv(OUT / "vista_v1_state_summary.csv", index=False)

    ok, checks, agg_ok, switches_ok = confirmation(mdf, switches)
    status = "MECHANISM_PASS" if ok else "NOT_PROMOTED_CONFIRM_FAIL"

    resc = rescue_2026(vista)
    pd.DataFrame([resc]).to_csv(OUT / "vista_v1_2026_rescue.csv", index=False)

    inf = inference(vista)
    inf.to_csv(OUT / "vista_v1_inference.csv", index=False)

    summary = {
        "schema": "VISTA_H3_V1",
        "status": status,
        "source_bridge": bridge,
        "api_calls": int(api_calls),
        "rule": {
            "base_hazard": BASE_HAZARD,
            "hazard_min": HAZARD_MIN,
            "hazard_max": HAZARD_MAX,
            "kappa": KAPPA,
            "percentile_window": PCT_WINDOW,
            "percentile_min_history": PCT_MIN_HISTORY,
            "shock_weights": {"rv24": 0.70, "jump24": 0.30},
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
        "state_summary": st.to_dict(orient="records"),
        "rescue_2026": resc,
        "metrics": mdf.to_dict(orient="records"),
        "inference": inf.to_dict(orient="records"),
    }
    (OUT / "vista_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# VISTA-H3 V1 — VOLATILITY-INFORMED STATE-TRANSITION RESULT", "",
        f"**Status:** **{status}**  ",
        f"**Dynamic hazard:** 0.05 * exp(k*(shock-0.5)), clipped [0.02, 0.125]  ",
        f"**2023 + 2024 confirmation:** **{ok}**", "",
        "## Period metrics", "",
        "| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for period in ["2022_H2", "2023", "2024", "2025", "2026", "2025-2026"]:
        for model in ["STRUCTURAL_IRIS", "SENTRY", "DART", "VISTA"]:
            q = mdf[(mdf.model == model) & (mdf.period == period)]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(
                f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
            )

    lines += ["", "## Annual state / hazard", "",
              "| Year | PATH share | Mean shock | Mean hazard | P90 hazard | Mean Pr(PATH superior) |",
              "|---:|---:|---:|---:|---:|---:|"]
    for r in st.itertuples():
        lines.append(
            f"| {int(r.year)} | {100*r.path_share:.1f}% | {r.mean_shock_score:.3f} | "
            f"{r.mean_dynamic_hazard:.4f} | {r.p90_dynamic_hazard:.4f} | "
            f"{r.mean_prob_path_superior:.3f} |"
        )

    lines += ["", "## State switches", ""]
    if switches.empty:
        lines.append("- none")
    else:
        for _, r in switches.iterrows():
            lines.append(
                f"- {r['forecast_issue_date']}: {r['from']} -> {r['to']}; "
                f"shock={r['origin_shock_score']:.3f}; hazard={r['origin_hazard']:.4f}; "
                f"q_path={r['q_path']:.3f}; Pr(PATH superior)={r['prob_path_superior']:.3f}"
            )

    lines += ["", "## 2026 rescue", "",
              f"- Structural accuracy: **{100*resc['base_accuracy']:.2f}%**",
              f"- VISTA accuracy: **{100*resc['vista_accuracy']:.2f}%**",
              f"- rescued: **{resc['rescued']}**",
              f"- broken: **{resc['broken']}**",
              f"- net rescue: **{resc['net_rescue']:+d}**",
              f"- PATH origins: **{resc['path_origins']} / {resc['n']}**", "",
              "## Dependence-aware bootstrap highlights", ""]

    for period in ["2026", "2025-2026"]:
        for comp in ["VISTA_vs_DART", "VISTA_vs_SENTRY", "VISTA_vs_STRUCTURAL"]:
            for metric in ["accuracy", "brier"]:
                q = inf[
                    (inf.period == period)
                    & (inf.comparison == comp)
                    & (inf.metric == metric)
                    & (inf.block_len == 10)
                ]
                if q.empty:
                    continue
                r = q.iloc[0]
                scale = 100.0 if metric == "accuracy" else 1.0
                suffix = " pp" if metric == "accuracy" else ""
                lines.append(
                    f"- {period} {comp} {metric} (block10): "
                    f"diff={scale*r.observed_diff:+.4f}{suffix}; "
                    f"95%=[{scale*r.ci95_low:+.4f}, {scale*r.ci95_high:+.4f}]{suffix}; "
                    f"P(improve)={100*r.bootstrap_improve_share:.1f}%."
                )

    lines += ["", "## Governance", "",
              "VISTA changes only the BOCPD hazard prior. Expert probabilities, disagreement outcomes, and DART state thresholds are frozen. "
              "Shock percentiles use only prior 16:00 anchors. 2025/2026 did not tune V1."]

    (OUT / "VISTA_V1_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "VISTA_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
