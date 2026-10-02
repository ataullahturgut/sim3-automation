from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_h3_iris_v1 as iris

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_rift_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

AURORA = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"

THRESH = 0.70
SEED = 20261002
REPS = 10000
BLOCKS = [5, 10]

FEATURES = [
    "trend_strength",
    "opposite_semivar_share",
    "deceleration_6h",
    "session_against_trend",
    "path_consistency",
    "trend_close_location",
    "opposite_extreme_recency",
    "jump_concentration",
    "trend_to_range",
    "adverse_excursion",
]


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
        "prediction_std": float(np.std(p)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


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


def load_panel():
    a = pd.read_csv(AURORA)
    for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
        a[c] = pd.to_datetime(a[c], errors="raise")
    a["feature_date"] = a.feature_cutoff_date.dt.date

    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError(f"RIFT_SOURCE_BRIDGE_FAIL {bridge}")
    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    hourly = pd.concat([hist, ext], ignore_index=True)
    hourly = hourly.sort_values("ts").drop_duplicates("ts", keep="last").reset_index(drop=True)

    anchors = iris.build_anchor_features(hourly)
    p = a.merge(
        anchors,
        left_on="feature_date",
        right_on="local_date",
        how="inner",
        validate="one_to_one",
    )
    if len(p) != len(a):
        raise RuntimeError(f"RIFT_PANEL_MATCH_FAIL aurora={len(a)} panel={len(p)}")

    eps = 1e-8
    sign = np.where(p.h_ret_12.to_numpy(float) >= 0, 1.0, -1.0)
    up2 = p.h_up_semivol_24.to_numpy(float) ** 2
    dn2 = p.h_down_semivol_24.to_numpy(float) ** 2
    total = up2 + dn2 + eps

    p["trend_strength"] = np.abs(p.h_ret_12) / (p.h_rv_12 + eps)
    p["opposite_semivar_share"] = np.where(sign > 0, dn2 / total, up2 / total)
    p["deceleration_6h"] = -sign * (2.0 * p.h_ret_6 - p.h_ret_12) / (p.h_rv_12 + eps)
    p["session_against_trend"] = -sign * p.h_session_ret / (p.h_rv_12 + eps)
    p["path_consistency"] = sign * (2.0 * p.h_upfrac_24 - 1.0)
    p["trend_close_location"] = np.where(
        sign > 0,
        p.h_close_location_24,
        1.0 - p.h_close_location_24,
    )
    p["opposite_extreme_recency"] = np.where(
        sign > 0,
        1.0 / (1.0 + p.h_age_max_neg_24),
        1.0 / (1.0 + p.h_age_max_pos_24),
    )
    p["jump_concentration"] = p.h_jump_concentration_24
    p["trend_to_range"] = np.abs(p.h_ret_12) / (p.h_range_24 + eps)
    p["adverse_excursion"] = np.where(
        sign > 0,
        -p.h_max_drawdown_24 / (p.h_range_24 + eps),
        p.h_recovery_24 / (p.h_range_24 + eps),
    )

    p["momentum_up"] = (p.h_ret_12 >= 0).astype(int)
    p["reversal_target"] = (p.y_up.astype(int) != p.momentum_up.astype(int)).astype(int)
    p["aurora_pred"] = (p.p_aurora >= 0.5).astype(int)
    p["aurora_follows_momentum"] = p.aurora_pred == p.momentum_up
    p["month_key"] = p.forecast_issue_date.dt.to_period("M").astype(str)

    keep = [
        "feature_cutoff_date", "forecast_issue_date", "target_end_date_h3",
        "year", "month", "y_up", "target_r3", "p_aurora",
        "h_ret_12", "momentum_up", "reversal_target",
        "aurora_pred", "aurora_follows_momentum",
    ] + FEATURES
    p = p[keep].dropna().sort_values("forecast_issue_date").reset_index(drop=True)
    p["month_key"] = p.forecast_issue_date.dt.to_period("M").astype(str)
    return p, bridge, api_calls


def run_rift(panel):
    test = panel[panel.forecast_issue_date >= pd.Timestamp("2022-07-01")].copy()
    rows = []

    for mo in sorted(test.month_key.unique()):
        te = test[test.month_key == mo].copy()
        cutoff = te.feature_cutoff_date.min()
        first_issue = te.forecast_issue_date.min()

        tr = panel[
            (panel.target_end_date_h3 <= cutoff)
            & (panel.forecast_issue_date < first_issue)
        ].copy()
        if len(tr) < 80:
            continue

        model = make_model()
        model.fit(tr[FEATURES].to_numpy(float), tr.reversal_target.astype(int).to_numpy())
        prev = model.predict_proba(te[FEATURES].to_numpy(float))[:, 1]

        for r, p_rev in zip(te.itertuples(), prev):
            p_aur = float(r.p_aurora)
            a_pred = int(p_aur >= 0.5)
            mom = int(r.momentum_up)
            follows = bool(a_pred == mom)
            override = bool(follows and p_rev >= THRESH)

            if override:
                p_rift = float(1.0 - p_rev) if mom == 1 else float(p_rev)
            else:
                p_rift = p_aur

            rows.append({
                "feature_cutoff_date": r.feature_cutoff_date,
                "forecast_issue_date": r.forecast_issue_date,
                "target_end_date_h3": r.target_end_date_h3,
                "year": int(r.year),
                "month": str(r.month),
                "y_up": int(r.y_up),
                "target_r3": float(r.target_r3),
                "p_aurora": p_aur,
                "p_reversal": float(p_rev),
                "momentum_up": mom,
                "aurora_follows_momentum": follows,
                "override": override,
                "p_rift": p_rift,
                "train_n": int(len(tr)),
            })

    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)


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
        ma = metrics(z.y_up, z.p_aurora)
        mr = metrics(z.y_up, z.p_rift)
        ap = (z.p_aurora >= 0.5).astype(int)
        rp = (z.p_rift >= 0.5).astype(int)
        y = z.y_up.astype(int)
        changed = ap != rp
        rescued = int((changed & (ap != y) & (rp == y)).sum())
        broken = int((changed & (ap == y) & (rp != y)).sum())
        rows.append({
            "period": label,
            "override_n": int(z.override.sum()),
            "changed_n": int(changed.sum()),
            "rescued": rescued,
            "broken": broken,
            "net_rescue": rescued - broken,
            **{f"aurora_{k}": v for k, v in ma.items()},
            **{f"rift_{k}": v for k, v in mr.items()},
        })
    return pd.DataFrame(rows)


def mechanism_gate(mdf):
    ok = True
    checks = []
    for yr in ["2023", "2024"]:
        r = mdf[mdf.period == yr].iloc[0]
        passed = bool(
            r.rift_accuracy + 0.01 + 1e-12 >= r.aurora_accuracy
            and r.rift_brier <= r.aurora_brier + 0.003 + 1e-12
        )
        checks.append({"period": yr, "pass": passed})
        ok = ok and passed

    agg = mdf[mdf.period == "2023-2024"].iloc[0]
    agg_ok = bool(
        agg.rift_balanced_accuracy + 1e-12 >= agg.aurora_balanced_accuracy
        and int(agg.net_rescue) > 0
    )
    return bool(ok and agg_ok), checks, agg_ok


def logloss_row(y, p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    y = np.asarray(y, int)
    return -(y*np.log(p) + (1-y)*np.log(1-p))


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
        starts = rng.integers(0,n,size=(m,nb))
        idx = (starts[:,:,None] + offs[None,None,:]) % n
        idx = idx.reshape(m,-1)[:,:n]
        vals[st:st+m] = diff[idx].mean(axis=1)
    return vals


def inference(g):
    rows = []
    seed_i = 0
    for period, mask in {
        "2023-2024": g.year.isin([2023, 2024]),
        "2025-2026": g.year.isin([2025, 2026]),
        "2026": g.year == 2026,
    }.items():
        z = g[mask].copy()
        diffs = paired_diff(z.y_up, z.p_rift, z.p_aurora)
        for metric, d in diffs.items():
            for block in BLOCKS:
                seed_i += 1
                boot = circular_boot(d, block, np.random.default_rng(SEED+seed_i))
                lo, hi = np.quantile(boot,[.025,.975])
                improve = float(np.mean(boot > 0)) if metric=="accuracy" else float(np.mean(boot < 0))
                rows.append({
                    "period":period,"metric":metric,"block_len":block,
                    "observed_diff":float(np.mean(d)),
                    "ci95_low":float(lo),"ci95_high":float(hi),
                    "bootstrap_improve_share":improve,"n":int(len(z)),
                })
    return pd.DataFrame(rows)


def main():
    panel, bridge, api_calls = load_panel()
    panel.to_csv(OUT/"rift_v1_panel.csv", index=False)

    pred = run_rift(panel)
    pred.to_csv(OUT/"rift_v1_predictions.csv", index=False)

    mdf = score_periods(pred)
    mdf.to_csv(OUT/"rift_v1_metrics.csv", index=False)

    passed, checks, agg_ok = mechanism_gate(mdf)
    status = "MECHANISM_PASS" if passed else "NOT_PROMOTED_CONFIRM_FAIL"

    inf = inference(pred) if passed else pd.DataFrame()
    if passed:
        inf.to_csv(OUT/"rift_v1_inference.csv", index=False)

    z = pred[pred.year == 2026].copy()
    z["aurora_dir"] = np.where(z.p_aurora >= .5, "UP", "DOWN")
    z["rift_dir"] = np.where(z.p_rift >= .5, "UP", "DOWN")
    z["actual_dir"] = np.where(z.y_up == 1, "UP", "DOWN")
    z["aurora_correct"] = z.aurora_dir == z.actual_dir
    z["rift_correct"] = z.rift_dir == z.actual_dir
    changed = z[z.aurora_dir != z.rift_dir].copy()
    changed["effect"] = np.where(
        (~changed.aurora_correct) & changed.rift_correct,
        "RESCUED",
        np.where(changed.aurora_correct & (~changed.rift_correct), "BROKEN", "NO_NET"),
    )
    changed.to_csv(OUT/"rift_v1_2026_changed.csv", index=False)

    summary = {
        "schema":"RIFT_H3_V1",
        "status":status,
        "evidence_class":"RETROSPECTIVE_MECHANISM_VALIDATION_POST_HOC_ARCHITECTURE",
        "threshold":THRESH,
        "source_bridge":bridge,
        "api_calls":int(api_calls),
        "mechanism_pass":bool(passed),
        "confirmation_checks":checks,
        "aggregate_guard":bool(agg_ok),
        "metrics":mdf.to_dict(orient="records"),
        "inference":inf.to_dict(orient="records") if passed else [],
        "changed_2026":int(len(changed)),
        "rescued_2026":int((changed.effect=="RESCUED").sum()),
        "broken_2026":int((changed.effect=="BROKEN").sum()),
    }
    (OUT/"rift_v1_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    lines = [
        "# RIFT-H3 V1 — REVERSAL IMBALANCE & FAT-TAIL TRIGGER RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence class:** retrospective mechanism validation; architecture was motivated after inspecting historical errors including 2026.  ",
        f"**Fixed reversal threshold:** **{THRESH:.2f}**","",
        "## Period metrics","",
        "| Period | AURORA Acc | RIFT Acc | AURORA BA | RIFT BA | AURORA Brier | RIFT Brier | Overrides | Rescued | Broken |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _,r in mdf.iterrows():
        lines.append(
            f"| {r.period} | {100*r.aurora_accuracy:.2f}% | {100*r.rift_accuracy:.2f}% | "
            f"{100*r.aurora_balanced_accuracy:.2f}% | {100*r.rift_balanced_accuracy:.2f}% | "
            f"{r.aurora_brier:.4f} | {r.rift_brier:.4f} | {int(r.override_n)} | "
            f"{int(r.rescued)} | {int(r.broken)} |"
        )

    lines += ["","## 2026 changed calls",""]
    if changed.empty:
        lines.append("- none")
    else:
        lines += [
            "| Issue | H3 end | AURORA | P(reversal) | RIFT | Actual | H3 return | Effect |",
            "|---|---|---|---:|---|---|---:|---|",
        ]
        for r in changed.itertuples():
            lines.append(
                f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | "
                f"{r.aurora_dir} | {100*r.p_reversal:.1f}% | {r.rift_dir} | {r.actual_dir} | "
                f"{100*r.target_r3:+.2f}% | {r.effect} |"
            )

    if passed:
        lines += ["","## Dependence-aware bootstrap",""]
        for r in inf.itertuples():
            scale = 100 if r.metric=="accuracy" else 1
            unit = " pp" if r.metric=="accuracy" else ""
            lines.append(
                f"- {r.period} {r.metric} block{r.block_len}: diff={scale*r.observed_diff:+.4f}{unit}; "
                f"95%=[{scale*r.ci95_low:+.4f},{scale*r.ci95_high:+.4f}]{unit}; "
                f"P(improve)={100*r.bootstrap_improve_share:.1f}%."
            )

    lines += ["","## Governance","",
              "No feature, threshold or model hyperparameter was searched after this authority was written. "
              "Because the architecture itself was discovered from historical error anatomy, these results cannot be called pristine prospective validation. "
              "A passed RIFT must be frozen separately and judged only on future origins."]

    (OUT/"RIFT_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"RIFT_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
