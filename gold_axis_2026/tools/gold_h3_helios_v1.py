from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_helios_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

AURORA = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"
RIFT = ROOT / "gold_axis_2026" / "GOLD_H3_RIFT_V1_PREDICTIONS_2026-10-02.csv"
TURN = ROOT / "gold_axis_2026" / "GOLD_H3_TURN_V1_PREDICTIONS_2026-10-02.csv"
VEGA = ROOT / "gold_axis_2026" / "GOLD_H3_VEGA_V1_PREDICTIONS_2026-10-02.csv"
OPAL = ROOT / "gold_axis_2026" / "GOLD_H3_OPAL_V1_PREDICTIONS_2026-10-03.csv"

WINDOW = 8
ENTER_WINS = 5
EXIT_WINS = 3
REPS = 10000
BLOCKS = [5, 10]
SEED = 20261003


def metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(np.mean((p-y)**2)),
        "logloss": float(log_loss(y, p, labels=[0, 1])),
        "up_recall": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "down_recall": float(recall_score(y, pred, pos_label=0, zero_division=0)),
        "prediction_std": float(np.std(p)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def load_csv(path, prefix=None):
    x = pd.read_csv(path)
    for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
        if c in x.columns:
            x[c] = pd.to_datetime(x[c], errors="raise")
    if prefix:
        keep = ["forecast_issue_date", "override"]
        extra = []
        if prefix == "opal":
            extra = ["p_opal", "p_reversal"]
        z = x[keep + [c for c in extra if c in x.columns]].copy()
        ren = {"override": f"{prefix}_override"}
        if "p_opal" in z.columns:
            ren["p_opal"] = "p_opal_raw"
        if "p_reversal" in z.columns:
            ren["p_reversal"] = "p_opal_reversal"
        return z.rename(columns=ren)
    return x


def build_ledger():
    a = load_csv(AURORA)
    r = load_csv(RIFT, "rift")
    t = load_csv(TURN, "turn")
    v = load_csv(VEGA, "vega")
    o = load_csv(OPAL, "opal")

    g = a.merge(r, on="forecast_issue_date", how="inner", validate="one_to_one")
    g = g.merge(t, on="forecast_issue_date", how="inner", validate="one_to_one")
    g = g.merge(v, on="forecast_issue_date", how="inner", validate="one_to_one")
    g = g.merge(o, on="forecast_issue_date", how="inner", validate="one_to_one")

    if len(g) != len(a):
        raise RuntimeError(f"HELIOS_MATCH_FAIL aurora={len(a)} merged={len(g)}")

    for c in ["rift_override", "turn_override", "vega_override", "opal_override"]:
        if g[c].dtype != bool:
            g[c] = g[c].astype(str).str.lower().map({"true": True, "false": False})
        if g[c].isna().any():
            raise RuntimeError(f"HELIOS_BAD_BOOL {c}")

    g["corroborator_n"] = (
        g.rift_override.astype(int)
        + g.turn_override.astype(int)
        + g.vega_override.astype(int)
    )
    g["candidate_reversal"] = g.opal_override & (g.corroborator_n >= 1)
    g["aurora_pred"] = (g.p_aurora >= 0.5).astype(int)
    g["candidate_success"] = np.where(
        g.candidate_reversal,
        (g.aurora_pred != g.y_up.astype(int)).astype(float),
        np.nan,
    )
    g = g.sort_values("forecast_issue_date").reset_index(drop=True)

    pending = []
    competence = []
    active = False
    rows = []
    switches = []

    for r0 in g.itertuples(index=False):
        cutoff = pd.Timestamp(r0.feature_cutoff_date)

        still_pending = []
        for item in pending:
            if pd.Timestamp(item["target_end_date_h3"]) <= cutoff:
                competence.append(int(item["success"]))
            else:
                still_pending.append(item)
        pending = still_pending

        recent = competence[-WINDOW:]
        wins = int(sum(recent)) if len(recent) >= WINDOW else 0
        losses = int(WINDOW - wins) if len(recent) >= WINDOW else 0
        prior_active = active

        if len(recent) >= WINDOW:
            if (not active) and wins >= ENTER_WINS:
                active = True
            elif active and wins <= EXIT_WINS:
                active = False

        if active != prior_active:
            switches.append({
                "forecast_issue_date": str(pd.Timestamp(r0.forecast_issue_date).date()),
                "new_state": "ACTIVE" if active else "INACTIVE",
                "matured_candidate_n": int(len(competence)),
                "recent_wins": int(wins),
                "recent_losses": int(losses),
                "recent_sequence": "".join(str(x) for x in recent),
            })

        candidate = bool(r0.candidate_reversal)
        hard_route = bool(active and candidate)
        if len(recent) >= WINDOW:
            q = float((wins + 1) / (WINDOW + 2))
        else:
            q = 0.5

        p_a = float(r0.p_aurora)
        p_reverse = 1.0 - p_a
        p_hard = p_reverse if hard_route else p_a
        p_soft = ((1.0-q)*p_a + q*p_reverse) if hard_route else p_a

        row = r0._asdict()
        row.update({
            "gate_active": bool(active),
            "competence_matured_n": int(len(competence)),
            "recent_candidate_n": int(len(recent)),
            "recent_wins": int(wins),
            "recent_losses": int(losses),
            "competence_q": float(q),
            "hard_route": hard_route,
            "p_helios_hard": float(p_hard),
            "p_helios_soft": float(p_soft),
        })
        rows.append(row)

        if candidate:
            pending.append({
                "target_end_date_h3": r0.target_end_date_h3,
                "success": int(r0.candidate_success),
            })

    return pd.DataFrame(rows), pd.DataFrame(switches)


def score_periods(g):
    specs = [
        ("2022_H2", g.forecast_issue_date.between("2022-07-01", "2022-12-31")),
        ("2023", g.year == 2023),
        ("2024", g.year == 2024),
        ("2025", g.year == 2025),
        ("2026", g.year == 2026),
        ("2023-2024", g.year.isin([2023, 2024])),
        ("2025-2026", g.year.isin([2025, 2026])),
    ]
    rows = []
    for label, mask in specs:
        z = g[mask].copy()
        if z.empty:
            continue
        base = metrics(z.y_up, z.p_aurora)
        soft = metrics(z.y_up, z.p_helios_soft)
        hard = metrics(z.y_up, z.p_helios_hard)
        opal = metrics(z.y_up, z.p_opal_raw)

        bp = (z.p_aurora >= .5).astype(int)
        sp = (z.p_helios_soft >= .5).astype(int)
        y = z.y_up.astype(int)
        changed = bp != sp
        rescued = int((changed & (bp != y) & (sp == y)).sum())
        broken = int((changed & (bp == y) & (sp != y)).sum())

        cand = z[z.candidate_reversal].copy()
        cand_success = float(cand.candidate_success.mean()) if len(cand) else np.nan

        rows.append({
            "period": label,
            "gate_active_share": float(z.gate_active.mean()),
            "candidate_n": int(z.candidate_reversal.sum()),
            "candidate_success_rate": cand_success,
            "routed_n": int(z.hard_route.sum()),
            "rescued": rescued,
            "broken": broken,
            "net_rescue": rescued-broken,
            **{f"aurora_{k}": v for k,v in base.items()},
            **{f"soft_{k}": v for k,v in soft.items()},
            **{f"hard_{k}": v for k,v in hard.items()},
            **{f"opal_{k}": v for k,v in opal.items()},
        })
    return pd.DataFrame(rows)


def score_monthly(g):
    rows = []
    for mo, z in g[g.year.isin([2025, 2026])].groupby("month"):
        b = metrics(z.y_up, z.p_aurora)
        s = metrics(z.y_up, z.p_helios_soft)
        rows.append({
            "month": mo,
            "n": int(len(z)),
            "gate_active_share": float(z.gate_active.mean()),
            "candidate_n": int(z.candidate_reversal.sum()),
            "routed_n": int(z.hard_route.sum()),
            "aurora_accuracy": b["accuracy"],
            "helios_accuracy": s["accuracy"],
            "aurora_brier": b["brier"],
            "helios_brier": s["brier"],
        })
    return pd.DataFrame(rows)


def logloss_row(y, p):
    p = np.clip(np.asarray(p, float), 1e-6, 1-1e-6)
    y = np.asarray(y, int)
    return -(y*np.log(p)+(1-y)*np.log(1-p))


def paired_diff(y, cand, base):
    y = np.asarray(y, int)
    cand = np.asarray(cand, float)
    base = np.asarray(base, float)
    return {
        "accuracy": ((cand >= .5).astype(int) == y).astype(float)
                  - ((base >= .5).astype(int) == y).astype(float),
        "brier": (cand-y)**2 - (base-y)**2,
        "logloss": logloss_row(y,cand) - logloss_row(y,base),
    }


def circular_boot(diff, block_len, rng):
    diff = np.asarray(diff, float)
    n = len(diff)
    nb = int(np.ceil(n/block_len))
    vals = np.empty(REPS, float)
    offs = np.arange(block_len)
    batch = 500
    for st in range(0, REPS, batch):
        m = min(batch, REPS-st)
        starts = rng.integers(0, n, size=(m, nb))
        idx = (starts[:,:,None] + offs[None,None,:]) % n
        idx = idx.reshape(m, -1)[:, :n]
        vals[st:st+m] = diff[idx].mean(axis=1)
    return vals


def inference(g):
    rows = []
    si = 0
    comparisons = {
        "AURORA": "p_aurora",
        "OPAL_RAW": "p_opal_raw",
    }
    periods = {
        "2023-2024": g.year.isin([2023, 2024]),
        "2025-2026": g.year.isin([2025, 2026]),
        "2026": g.year == 2026,
    }
    for base_name, base_col in comparisons.items():
        for period, mask in periods.items():
            z = g[mask].copy()
            for metric, d in paired_diff(z.y_up, z.p_helios_soft, z[base_col]).items():
                for b in BLOCKS:
                    si += 1
                    boot = circular_boot(d, b, np.random.default_rng(SEED+si))
                    lo, hi = np.quantile(boot, [.025, .975])
                    improve = float(np.mean(boot > 0)) if metric == "accuracy" else float(np.mean(boot < 0))
                    rows.append({
                        "comparison": f"HELIOS_vs_{base_name}",
                        "period": period,
                        "metric": metric,
                        "block_len": int(b),
                        "observed_diff": float(np.mean(d)),
                        "ci95_low": float(lo),
                        "ci95_high": float(hi),
                        "bootstrap_improve_share": improve,
                        "n": int(len(z)),
                    })
    return pd.DataFrame(rows)


def candidate_anatomy(g):
    rows = []
    for year in [2022, 2023, 2024, 2025, 2026]:
        z = g[(g.year == year) & g.candidate_reversal].copy()
        if z.empty:
            continue
        rows.append({
            "year": year,
            "candidate_n": int(len(z)),
            "success_n": int(z.candidate_success.sum()),
            "failure_n": int(len(z)-z.candidate_success.sum()),
            "success_rate": float(z.candidate_success.mean()),
            "mean_opal_reversal_p": float(z.p_opal_reversal.mean()),
            "mean_aurora_confidence": float(np.mean(np.abs(z.p_aurora-.5))),
        })
    return pd.DataFrame(rows)


def main():
    g, switches = build_ledger()
    g.to_csv(OUT/"helios_v1_predictions.csv", index=False)
    switches.to_csv(OUT/"helios_v1_switches.csv", index=False)

    m = score_periods(g)
    m.to_csv(OUT/"helios_v1_metrics.csv", index=False)

    monthly = score_monthly(g)
    monthly.to_csv(OUT/"helios_v1_monthly_2025_2026.csv", index=False)

    anatomy = candidate_anatomy(g)
    anatomy.to_csv(OUT/"helios_v1_candidate_anatomy.csv", index=False)

    inf = inference(g)
    inf.to_csv(OUT/"helios_v1_inference.csv", index=False)

    z = g[g.year == 2026].copy()
    z["aurora_dir"] = np.where(z.p_aurora >= .5, "UP", "DOWN")
    z["helios_dir"] = np.where(z.p_helios_soft >= .5, "UP", "DOWN")
    z["actual_dir"] = np.where(z.y_up == 1, "UP", "DOWN")
    z["aurora_correct"] = z.aurora_dir == z.actual_dir
    z["helios_correct"] = z.helios_dir == z.actual_dir
    changed = z[z.aurora_dir != z.helios_dir].copy()
    changed["effect"] = np.where(
        (~changed.aurora_correct) & changed.helios_correct, "RESCUED",
        np.where(changed.aurora_correct & (~changed.helios_correct), "BROKEN", "NO_NET")
    )
    changed.to_csv(OUT/"helios_v1_2026_changed.csv", index=False)

    summary = {
        "schema": "HELIOS_H3_V1",
        "status": "POSTHOC_STRENGTHENING_RESULT",
        "evidence_class": "RETROSPECTIVE_STRENGTHENING_EVIDENCE",
        "gate": {
            "candidate_rule": "OPAL AND (RIFT OR VEGA OR TURN)",
            "window": WINDOW,
            "enter_wins": ENTER_WINS,
            "exit_wins": EXIT_WINS,
            "soft_prior": "Beta(1,1)",
        },
        "switches": switches.to_dict(orient="records"),
        "candidate_anatomy": anatomy.to_dict(orient="records"),
        "metrics": m.to_dict(orient="records"),
        "inference": inf.to_dict(orient="records"),
        "changed_2026": int(len(changed)),
        "rescued_2026": int((changed.effect == "RESCUED").sum()),
        "broken_2026": int((changed.effect == "BROKEN").sum()),
    }
    (OUT/"helios_v1_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str)+"\n")

    lines = [
        "# HELIOS-H3 V1 — REGIME-GATED REVERSAL ROUTER RESULT","",
        "**Status:** **POSTHOC_STRENGTHENING_RESULT**  ",
        "**Evidence class:** retrospective strengthening evidence; future freeze required for prospective proof.  ","",
        "## Candidate reversal anatomy","",
        "| Year | Candidate | Success | Failure | Precision | Mean OPAL P(reversal) |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for r in anatomy.itertuples():
        lines.append(
            f"| {r.year} | {r.candidate_n} | {r.success_n} | {r.failure_n} | "
            f"{100*r.success_rate:.1f}% | {100*r.mean_opal_reversal_p:.1f}% |"
        )

    lines += ["","## Gate switches",""]
    if switches.empty:
        lines.append("- none")
    else:
        for r in switches.itertuples():
            lines.append(
                f"- **{r.forecast_issue_date}** -> **{r.new_state}**; "
                f"recent 8 = {r.recent_sequence} ({r.recent_wins}W/{r.recent_losses}L)."
            )

    lines += ["","## Period metrics","",
              "| Period | AURORA Acc | HELIOS Soft Acc | Hard Acc | Raw OPAL Acc | AURORA BA | HELIOS BA | AURORA Brier | HELIOS Brier | Routed | Rescue | Broken |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in m.itertuples():
        lines.append(
            f"| {r.period} | {100*r.aurora_accuracy:.2f}% | {100*r.soft_accuracy:.2f}% | "
            f"{100*r.hard_accuracy:.2f}% | {100*r.opal_accuracy:.2f}% | "
            f"{100*r.aurora_balanced_accuracy:.2f}% | {100*r.soft_balanced_accuracy:.2f}% | "
            f"{r.aurora_brier:.4f} | {r.soft_brier:.4f} | {r.routed_n} | {r.rescued} | {r.broken} |"
        )

    lines += ["","## 2026 changed calls",""]
    if changed.empty:
        lines.append("- none")
    else:
        lines += [
            "| Issue | H3 end | q competence | AURORA | HELIOS | Actual | H3 return | Effect |",
            "|---|---|---:|---|---|---|---:|---|",
        ]
        for r in changed.itertuples():
            lines.append(
                f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | "
                f"{100*r.competence_q:.1f}% | {r.aurora_dir} | {r.helios_dir} | {r.actual_dir} | "
                f"{100*r.target_r3:+.2f}% | {r.effect} |"
            )

    lines += ["","## Dependence-aware bootstrap",""]
    for r in inf.itertuples():
        scale = 100 if r.metric == "accuracy" else 1
        unit = " pp" if r.metric == "accuracy" else ""
        lines.append(
            f"- {r.comparison} / {r.period} / {r.metric} / block{r.block_len}: "
            f"diff={scale*r.observed_diff:+.4f}{unit}; "
            f"95%=[{scale*r.ci95_low:+.4f},{scale*r.ci95_high:+.4f}]{unit}; "
            f"P(improve)={100*r.bootstrap_improve_share:.1f}%."
        )

    lines += ["","## Governance","",
              "HELIOS routes only a residual reversal correction. The base AURORA probability is untouched outside active consensus events. "
              "All competence evidence is target-matured before use. Because HELIOS was designed after historical error analysis, these results cannot be called pristine confirmation. "
              "Any operational challenge to AURORA requires a new prospective HELIOS freeze."]

    (OUT/"HELIOS_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"HELIOS_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
