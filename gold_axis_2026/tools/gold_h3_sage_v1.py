from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import timedelta

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_h3_iris_v1 as iris

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_sage_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20261002
PATH = list(iris.PATH)

SESSION_RET = [
    "sess_asia", "sess_europe", "sess_us_am", "sess_us_pm",
]
SESSION_PHASE = [
    "sess_us_total", "sess_west_total", "sess_east_west", "sess_us_reversal",
    "sess_dispersion", "sess_sign_changes", "sess_dominance",
    "sess_asia_us_interaction", "sess_east_west_conflict", "sess_us_conflict",
]
SESSION_ALL = SESSION_RET + SESSION_PHASE

CANDIDATES = {
    "A1_SESSION": ["base_logit"] + SESSION_ALL,
    "SESSION_ONLY": SESSION_ALL,
    "PATH_SESSION": PATH + SESSION_ALL,
    "A1_PATH_SESSION": ["base_logit"] + PATH + SESSION_ALL,
}
BASE_FEATURES = ["base_logit"] + PATH


def make_model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0, solver="lbfgs", max_iter=3000, random_state=SEED
        )),
    ])


def fill_xy(tr, te, features):
    a = tr[features].copy()
    b = te[features].copy()
    for c in features:
        a[c] = pd.to_numeric(a[c], errors="coerce")
        b[c] = pd.to_numeric(b[c], errors="coerce")
        med = a[c].median(skipna=True)
        v = float(med) if pd.notna(med) else 0.0
        a[c] = a[c].fillna(v)
        b[c] = b[c].fillna(v)
    return a.to_numpy(float), b.to_numpy(float)


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


def load_combined_hourly():
    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError("SAGE_SOURCE_BRIDGE_FAIL")
    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    hourly = pd.concat([hist, ext], ignore_index=True)
    hourly = hourly.sort_values("ts").drop_duplicates("ts", keep="first").reset_index(drop=True)
    return hourly, bridge, api_calls


def build_session_anchors(hourly):
    q = hourly.copy().sort_values("ts").reset_index(drop=True)
    q["ts_ny"] = q.ts.dt.tz_convert(iris.TZ)
    q["local_date"] = q.ts_ny.dt.date
    q["local_hour"] = q.ts_ny.dt.hour
    q["local_minute"] = q.ts_ny.dt.minute
    q["logp"] = np.log(q.value.astype(float))

    hh = q[(q.local_minute == 0)].copy()
    lookup = {
        (r.local_date, int(r.local_hour)): float(r.logp)
        for r in hh.itertuples()
    }

    anchor_dates = sorted(set(
        d for (d, h) in lookup.keys() if h == 16
    ))
    rows = []
    for d in anchor_dates:
        prev = d - timedelta(days=1)
        keys = {
            "asia_start": (prev, 18),
            "asia_end": (d, 3),
            "europe_end": (d, 8),
            "us_am_end": (d, 12),
            "anchor": (d, 16),
        }
        if not all(k in lookup for k in keys.values()):
            continue
        lp18 = lookup[keys["asia_start"]]
        lp03 = lookup[keys["asia_end"]]
        lp08 = lookup[keys["europe_end"]]
        lp12 = lookup[keys["us_am_end"]]
        lp16 = lookup[keys["anchor"]]

        asia = lp03 - lp18
        europe = lp08 - lp03
        us_am = lp12 - lp08
        us_pm = lp16 - lp12
        seq = np.array([asia, europe, us_am, us_pm], float)

        us_total = us_am + us_pm
        west_total = europe + us_total
        east_west = asia - west_total
        us_reversal = us_pm - us_am
        dispersion = float(np.std(seq, ddof=0))
        signs = np.sign(seq)
        sign_changes = float(np.sum(signs[1:] * signs[:-1] < 0))
        dominance = float(np.max(np.abs(seq)) / (np.sum(np.abs(seq)) + 1e-10))
        asia_us_interaction = float(asia * us_total)
        east_west_conflict = float(asia * west_total < 0)
        us_conflict = float(us_am * us_pm < 0)

        rows.append({
            "local_date": d,
            "sess_asia": asia,
            "sess_europe": europe,
            "sess_us_am": us_am,
            "sess_us_pm": us_pm,
            "sess_us_total": us_total,
            "sess_west_total": west_total,
            "sess_east_west": east_west,
            "sess_us_reversal": us_reversal,
            "sess_dispersion": dispersion,
            "sess_sign_changes": sign_changes,
            "sess_dominance": dominance,
            "sess_asia_us_interaction": asia_us_interaction,
            "sess_east_west_conflict": east_west_conflict,
            "sess_us_conflict": us_conflict,
        })
    return pd.DataFrame(rows)


def prepare_panel():
    ledger = iris.load_ledger()
    hourly, bridge, api_calls = load_combined_hourly()
    iris_anchors = iris.build_anchor_features(hourly)
    session_anchors = build_session_anchors(hourly)

    anchors = iris_anchors.merge(session_anchors, on="local_date", how="inner", validate="one_to_one")
    panel = ledger.merge(
        anchors,
        left_on="feature_date",
        right_on="local_date",
        how="inner",
        validate="many_to_one",
    )
    need = ["target_r3", "y_up", "base_logit"] + PATH + SESSION_ALL
    panel = panel.dropna(subset=need).copy()
    panel["year"] = panel.forecast_issue_date.dt.year.astype(int)
    panel["month"] = panel.forecast_issue_date.dt.to_period("M").astype(str)
    return panel.sort_values("forecast_issue_date").reset_index(drop=True), bridge, api_calls


def walk_forward(panel, tag, features):
    test = panel[
        (panel.forecast_issue_date >= pd.Timestamp("2022-07-01"))
        & (panel.forecast_issue_date.dt.year <= 2026)
    ].copy()
    rows = []
    for mo in sorted(test.month.unique()):
        te = test[test.month == mo].copy()
        cutoff = te.feature_cutoff_date.min()
        tr = panel[
            (panel.target_end_date_h3 <= cutoff)
            & (panel.forecast_issue_date < te.forecast_issue_date.min())
        ].copy()
        if len(tr) < 95:
            continue
        Xtr, Xte = fill_xy(tr, te, features)
        ytr = tr.y_up.astype(int).to_numpy()
        m = make_model()
        m.fit(Xtr, ytr)
        pp = m.predict_proba(Xte)[:, 1]
        for r, p in zip(te.itertuples(), pp):
            rows.append({
                "tag": tag,
                "feature_cutoff_date": r.feature_cutoff_date,
                "forecast_issue_date": r.forecast_issue_date,
                "target_end_date_h3": r.target_end_date_h3,
                "year": int(r.year),
                "month": str(r.month),
                "y_up": int(r.y_up),
                "target_r3": float(r.target_r3),
                "p_up": float(p),
                "sess_east_west_conflict": float(r.sess_east_west_conflict),
                "sess_us_conflict": float(r.sess_us_conflict),
                "sess_asia": float(r.sess_asia),
                "sess_europe": float(r.sess_europe),
                "sess_us_am": float(r.sess_us_am),
                "sess_us_pm": float(r.sess_us_pm),
                "train_n": int(len(tr)),
            })
    return pd.DataFrame(rows)


def score_periods(led):
    rows = []
    periods = [
        ("SELECT_2022_H2", (led.forecast_issue_date >= pd.Timestamp("2022-07-01")) & (led.forecast_issue_date <= pd.Timestamp("2022-12-31"))),
        ("2023", led.year == 2023),
        ("2024", led.year == 2024),
        ("2025", led.year == 2025),
        ("2026", led.year == 2026),
        ("2023-2024", led.year.isin([2023, 2024])),
        ("2025-2026", led.year.isin([2025, 2026])),
    ]
    for tag, g0 in led.groupby("tag"):
        for label, mask in periods:
            g = g0[mask.loc[g0.index] if hasattr(mask, "loc") else mask]
            if g.empty:
                continue
            rows.append({"tag": tag, "period": label, **metrics(g.y_up, g.p_up)})
    return pd.DataFrame(rows)


def score_periods_safe(led):
    rows = []
    for tag, g0 in led.groupby("tag"):
        specs = [
            ("SELECT_2022_H2", g0.forecast_issue_date.between("2022-07-01", "2022-12-31")),
            ("2023", g0.year == 2023),
            ("2024", g0.year == 2024),
            ("2025", g0.year == 2025),
            ("2026", g0.year == 2026),
            ("2023-2024", g0.year.isin([2023, 2024])),
            ("2025-2026", g0.year.isin([2025, 2026])),
        ]
        for label, mask in specs:
            g = g0[mask].copy()
            if not g.empty:
                rows.append({"tag": tag, "period": label, **metrics(g.y_up, g.p_up)})
    return pd.DataFrame(rows)


def select_candidate(mdf):
    b = mdf[(mdf.tag == "BASE_IRIS") & (mdf.period == "SELECT_2022_H2")].iloc[0]
    rows = []
    for name in CANDIDATES:
        q = mdf[(mdf.tag == name) & (mdf.period == "SELECT_2022_H2")]
        if q.empty:
            continue
        r = q.iloc[0]
        eligible = bool(
            r.balanced_accuracy + 1e-12 >= b.balanced_accuracy
            and r.accuracy + 0.005 + 1e-12 >= b.accuracy
            and r.brier <= b.brier + 0.0025 + 1e-12
            and r.prediction_std >= 0.02
        )
        rows.append({
            "model": name,
            "eligible": eligible,
            "delta_accuracy": float(r.accuracy - b.accuracy),
            "delta_balanced_accuracy": float(r.balanced_accuracy - b.balanced_accuracy),
            "delta_brier": float(r.brier - b.brier),
            "delta_logloss": float(r.logloss - b.logloss),
            **{k: r[k] for k in [
                "n", "accuracy", "balanced_accuracy", "brier", "logloss",
                "up_recall", "down_recall", "false_call_rate", "prediction_std"
            ]},
        })
    tab = pd.DataFrame(rows)
    elig = tab[tab.eligible].copy()
    if elig.empty:
        return tab, None
    elig = elig.sort_values(
        ["balanced_accuracy", "accuracy", "brier", "logloss"],
        ascending=[False, False, True, True],
    )
    return tab, elig.iloc[0].to_dict()


def confirmation_pass(mdf, selected):
    if selected is None:
        return False, []
    name = str(selected["model"])
    checks = []
    ok = True
    for yr in ["2023", "2024"]:
        b = mdf[(mdf.tag == "BASE_IRIS") & (mdf.period == yr)].iloc[0]
        s = mdf[(mdf.tag == name) & (mdf.period == yr)].iloc[0]
        passed = bool(
            s.balanced_accuracy + 1e-12 >= b.balanced_accuracy
            and s.accuracy + 0.01 + 1e-12 >= b.accuracy
            and s.brier <= b.brier + 0.003 + 1e-12
        )
        ok = ok and passed
        checks.append({
            "period": yr,
            "pass": passed,
            "base_accuracy": float(b.accuracy),
            "selected_accuracy": float(s.accuracy),
            "base_balanced_accuracy": float(b.balanced_accuracy),
            "selected_balanced_accuracy": float(s.balanced_accuracy),
            "base_brier": float(b.brier),
            "selected_brier": float(s.brier),
        })
    return ok, checks


def monthly_2026(led, tags):
    rows = []
    z = led[(led.year == 2026) & (led.tag.isin(tags))].copy()
    for tag, g0 in z.groupby("tag"):
        for mo, g in g0.groupby("month"):
            rows.append({"tag": tag, "month": mo, **metrics(g.y_up, g.p_up)})
    return pd.DataFrame(rows)


def rescue_analysis(led, selected_name):
    b = led[(led.tag == "BASE_IRIS") & (led.year == 2026)][
        ["forecast_issue_date", "y_up", "p_up", "sess_east_west_conflict", "sess_us_conflict"]
    ].copy()
    s = led[(led.tag == selected_name) & (led.year == 2026)][
        ["forecast_issue_date", "p_up"]
    ].copy()
    x = b.merge(s, on="forecast_issue_date", suffixes=("_base", "_sage"))
    x["base_correct"] = ((x.p_up_base >= 0.5).astype(int) == x.y_up)
    x["sage_correct"] = ((x.p_up_sage >= 0.5).astype(int) == x.y_up)
    x["rescued"] = (~x.base_correct) & x.sage_correct
    x["broken"] = x.base_correct & (~x.sage_correct)

    rows = [{
        "group": "ALL_2026",
        "n": int(len(x)),
        "base_accuracy": float(x.base_correct.mean()),
        "sage_accuracy": float(x.sage_correct.mean()),
        "rescued": int(x.rescued.sum()),
        "broken": int(x.broken.sum()),
        "net_rescue": int(x.rescued.sum() - x.broken.sum()),
    }]
    for col, label in [
        ("sess_east_west_conflict", "EAST_WEST"),
        ("sess_us_conflict", "US_AM_PM"),
    ]:
        for val in [0.0, 1.0]:
            g = x[x[col] == val]
            if g.empty:
                continue
            rows.append({
                "group": f"{label}_{'CONFLICT' if val == 1.0 else 'AGREE'}",
                "n": int(len(g)),
                "base_accuracy": float(g.base_correct.mean()),
                "sage_accuracy": float(g.sage_correct.mean()),
                "rescued": int(g.rescued.sum()),
                "broken": int(g.broken.sum()),
                "net_rescue": int(g.rescued.sum() - g.broken.sum()),
            })
    return pd.DataFrame(rows), x


def coefficients(panel, selected_name):
    if selected_name is None:
        return pd.DataFrame()
    feats = CANDIDATES[selected_name]
    tr = panel[
        (panel.forecast_issue_date <= pd.Timestamp("2022-12-31"))
        & (panel.target_end_date_h3 <= pd.Timestamp("2022-12-31"))
    ].copy()
    X, _ = fill_xy(tr, tr.iloc[:1], feats)
    y = tr.y_up.astype(int).to_numpy()
    m = make_model()
    m.fit(X, y)
    co = m.named_steps["model"].coef_[0]
    return pd.DataFrame({
        "feature": feats, "coef_std": co, "abs_coef": np.abs(co)
    }).sort_values("abs_coef", ascending=False)


def main():
    panel, bridge, api_calls = prepare_panel()

    ledgers = [walk_forward(panel, "BASE_IRIS", BASE_FEATURES)]
    for name, feats in CANDIDATES.items():
        ledgers.append(walk_forward(panel, name, feats))
    led = pd.concat(ledgers, ignore_index=True)
    led.to_csv(OUT / "sage_v1_predictions.csv", index=False)

    mdf = score_periods_safe(led)
    mdf.to_csv(OUT / "sage_v1_metrics.csv", index=False)

    sel_grid, selected = select_candidate(mdf)
    sel_grid.to_csv(OUT / "sage_v1_selection_grid.csv", index=False)

    if selected is None:
        selected_name = None
        confirm_ok = False
        checks = []
        status = "FAIL_CLOSED_NO_ELIGIBLE_2022H2_SESSION_MODEL"
    else:
        selected_name = str(selected["model"])
        confirm_ok, checks = confirmation_pass(mdf, selected)
        status = "MECHANISM_PASS" if confirm_ok else "NOT_PROMOTED_CONFIRM_FAIL"

    if selected_name is not None:
        m26 = monthly_2026(led, ["BASE_IRIS", selected_name])
        m26.to_csv(OUT / "sage_v1_2026_monthly.csv", index=False)
        resc, detail = rescue_analysis(led, selected_name)
        resc.to_csv(OUT / "sage_v1_2026_rescue_summary.csv", index=False)
        detail.to_csv(OUT / "sage_v1_2026_rescue_detail.csv", index=False)
        coef = coefficients(panel, selected_name)
        coef.to_csv(OUT / "sage_v1_selected_coefficients.csv", index=False)
    else:
        m26 = resc = coef = pd.DataFrame()

    summary = {
        "schema": "SAGE_H3_V1",
        "status": status,
        "source_bridge": bridge,
        "api_calls": int(api_calls),
        "selected": selected,
        "selected_model": selected_name,
        "confirmation_pass": bool(confirm_ok),
        "confirmation_checks": checks,
        "metrics": mdf.to_dict(orient="records"),
        "rescue_2026": resc.to_dict(orient="records") if not resc.empty else [],
    }
    (OUT / "sage_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# SAGE-H3 V1 — SESSION-AWARE GOLD ENGINE RESULT", "",
        f"**Status:** **{status}**  ",
        f"**Selected 2022-H2 representation:** **{selected_name or 'NONE'}**  ",
        f"**2023 + 2024 frozen confirmation:** **{confirm_ok}**", "",
        "## Selection grid — 2022 H2", "",
        "| Candidate | Eligible | Δ accuracy | Δ balanced | Δ Brier |",
        "|---|---|---:|---:|---:|",
    ]
    for r in sel_grid.itertuples():
        lines.append(
            f"| {r.model} | {r.eligible} | {100*r.delta_accuracy:+.2f} pp | "
            f"{100*r.delta_balanced_accuracy:+.2f} pp | {r.delta_brier:+.4f} |"
        )

    lines += ["", "## Period metrics", "",
              "| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |",
              "|---|---|---:|---:|---:|---:|---:|---:|"]
    display_tags = ["BASE_IRIS"] + ([selected_name] if selected_name else [])
    for period in ["SELECT_2022_H2", "2023", "2024", "2025", "2026", "2025-2026"]:
        for tag in display_tags:
            q = mdf[(mdf.tag == tag) & (mdf.period == period)]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(
                f"| {tag} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
            )

    if not resc.empty:
        lines += ["", "## 2026 rescue / break analysis", "",
                  "| Group | N | BASE acc | SAGE acc | Rescued | Broken | Net rescue |",
                  "|---|---:|---:|---:|---:|---:|---:|"]
        for r in resc.itertuples():
            lines.append(
                f"| {r.group} | {int(r.n)} | {100*r.base_accuracy:.2f}% | {100*r.sage_accuracy:.2f}% | "
                f"{int(r.rescued)} | {int(r.broken)} | {int(r.net_rescue):+d} |"
            )

    if not m26.empty:
        lines += ["", "## 2026 month-by-month", "",
                  "| Model | Month | N | Accuracy | Balanced acc |",
                  "|---|---|---:|---:|---:|"]
        for r in m26.itertuples():
            lines.append(
                f"| {r.tag} | {r.month} | {int(r.n)} | {100*r.accuracy:.1f}% | {100*r.balanced_accuracy:.1f}% |"
            )

    if not coef.empty:
        lines += ["", "## Selected standardized coefficients through 2022", "",
                  "| Feature | Coef |",
                  "|---|---:|"]
        for r in coef.head(12).itertuples():
            lines.append(f"| {r.feature} | {r.coef_std:+.3f} |")

    lines += ["", "## Governance", "",
              "SAGE representation selection used only Jul-Dec 2022. "
              "2023 and 2024 were frozen confirmation periods; 2025/2026 were transport/stress. "
              "The 2026 rescue diagnostics did not alter V1."]

    (OUT / "SAGE_V1_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "SAGE_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
