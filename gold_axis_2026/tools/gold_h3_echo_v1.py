from __future__ import annotations

import json
import math
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
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_echo_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

AURORA = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"

SERIES = {
    "nem": "NEM_TWELVEDATA",
    "barrick": "BARRICK_B_TWELVEDATA",
    "gll": "GLL_TWELVEDATA",
    "dzz": "DZZ_TWELVEDATA",
}
HORIZONS = [1, 3, 5, 10]
HEADS = ["LINKED_ONLY", "AURORA_PLUS_LINKED"]

C = 0.25
MIN_TRAIN = 80
UP_OVERRIDE = 0.70
DOWN_OVERRIDE = 0.30
SEED = 20261002

BOOT_REPS = 10000
BOOT_BLOCKS = [5, 10]


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


def make_model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=C, solver="lbfgs", max_iter=3000, random_state=SEED
        )),
    ])


def load_aurora():
    x = pd.read_csv(AURORA)
    for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
        x[c] = pd.to_datetime(x[c], errors="raise")
    x = x.sort_values("forecast_issue_date").reset_index(drop=True)
    p = np.clip(x.p_aurora.astype(float).to_numpy(), 1e-6, 1 - 1e-6)
    x["aurora_logit"] = np.log(p / (1.0 - p))
    return x


def load_series_from_neon():
    dsn = os.environ["NEON_DATABASE_URL"]
    frames = {}
    meta = []
    with psycopg.connect(dsn, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            for key, sid in SERIES.items():
                cur.execute(
                    """
                    SELECT observation_ts, value, retrieved_at
                    FROM observations
                    WHERE series_id=%s
                    ORDER BY observation_ts, retrieved_at
                    """,
                    (sid,),
                )
                rows = cur.fetchall()
                if not rows:
                    raise RuntimeError(f"ECHO_NO_SERIES_ROWS {sid}")
                z = pd.DataFrame(rows, columns=["ts", "value", "retrieved_at"])
                z["ts"] = pd.to_datetime(z.ts, utc=True)
                z["value"] = pd.to_numeric(z.value, errors="coerce")
                z = z.dropna(subset=["value"])
                z = z[z.value > 0].copy()
                z = (
                    z.sort_values(["ts", "retrieved_at"])
                    .drop_duplicates("ts", keep="last")
                    .sort_values("ts")
                    .reset_index(drop=True)
                )
                z["date"] = z.ts.dt.tz_convert("UTC").dt.tz_localize(None).dt.normalize()
                z = z.sort_values(["date", "retrieved_at"]).drop_duplicates("date", keep="last")
                z = z[["date", "value"]].sort_values("date").reset_index(drop=True)
                frames[key] = z
                meta.append({
                    "key": key,
                    "series_id": sid,
                    "rows": int(len(z)),
                    "first": str(z.date.min().date()),
                    "last": str(z.date.max().date()),
                })
        conn.rollback()
    return frames, meta


def asset_return_before(series_df, cutoff_date, h):
    z = series_df[series_df.date < pd.Timestamp(cutoff_date)].copy()
    if len(z) < h + 1:
        return np.nan
    vals = z.value.to_numpy(float)
    return float(math.log(vals[-1] / vals[-1-h]))


def build_linked_features(origins, frames):
    rows = []
    for r in origins.itertuples():
        d = pd.Timestamp(r.feature_cutoff_date)
        row = {"feature_cutoff_date": d}

        for h in HORIZONS:
            vals = {}
            for key in SERIES:
                vals[key] = asset_return_before(frames[key], d, h)
                row[f"{key}_r{h}"] = vals[key]

            miner = np.array([vals["nem"], vals["barrick"]], float)
            aligned = np.array([
                vals["nem"], vals["barrick"],
                -vals["gll"], -vals["dzz"],
            ], float)

            row[f"miner_mean_{h}"] = float(np.mean(miner))
            row[f"miner_spread_{h}"] = float(vals["nem"] - vals["barrick"])
            row[f"miner_breadth_{h}"] = float(np.mean(miner > 0))
            row[f"inverse_mean_{h}"] = float(np.mean([vals["gll"], vals["dzz"]]))
            row[f"confirm_{h}"] = float(row[f"miner_mean_{h}"] - row[f"inverse_mean_{h}"])
            row[f"linked_breadth_{h}"] = float(np.mean(aligned > 0))
            row[f"linked_dispersion_{h}"] = float(np.std(aligned, ddof=0))

        rows.append(row)
    return pd.DataFrame(rows)


def linked_cols():
    cols = []
    for h in HORIZONS:
        for key in SERIES:
            cols.append(f"{key}_r{h}")
        cols += [
            f"miner_mean_{h}",
            f"miner_spread_{h}",
            f"miner_breadth_{h}",
            f"inverse_mean_{h}",
            f"confirm_{h}",
            f"linked_breadth_{h}",
            f"linked_dispersion_{h}",
        ]
    return cols


def fill_xy(tr, te, cols):
    a = tr[cols].copy()
    b = te[cols].copy()
    for c in cols:
        a[c] = pd.to_numeric(a[c], errors="coerce")
        b[c] = pd.to_numeric(b[c], errors="coerce")
        med = a[c].median(skipna=True)
        v = float(med) if pd.notna(med) else 0.0
        a[c] = a[c].fillna(v)
        b[c] = b[c].fillna(v)
    return a.to_numpy(float), b.to_numpy(float)


def walk_head(panel, head):
    lcols = linked_cols()
    cols = lcols if head == "LINKED_ONLY" else ["aurora_logit"] + lcols
    test = panel[panel.forecast_issue_date >= pd.Timestamp("2022-06-01")].copy()
    rows = []

    for mo in sorted(test.month.unique()):
        te = test[test.month == mo].copy()
        cutoff = te.feature_cutoff_date.min()
        first_issue = te.forecast_issue_date.min()
        tr = panel[
            (panel.target_end_date_h3 <= cutoff)
            & (panel.forecast_issue_date < first_issue)
        ].copy()
        if len(tr) < MIN_TRAIN:
            continue

        Xtr, Xte = fill_xy(tr, te, cols)
        ytr = tr.y_up.astype(int).to_numpy()
        md = make_model()
        md.fit(Xtr, ytr)
        pe = md.predict_proba(Xte)[:, 1]

        for r, p_echo in zip(te.itertuples(), pe):
            p_base = float(r.p_aurora)
            bdir = int(p_base >= 0.5)
            rescue = False
            p_out = p_base

            if bdir == 0 and p_echo >= UP_OVERRIDE:
                rescue = True
                p_out = float(p_echo)
            elif bdir == 1 and p_echo <= DOWN_OVERRIDE:
                rescue = True
                p_out = float(p_echo)

            edir = int(p_out >= 0.5)
            actual = int(r.y_up)

            rows.append({
                "head": head,
                "feature_cutoff_date": r.feature_cutoff_date,
                "forecast_issue_date": r.forecast_issue_date,
                "target_end_date_h3": r.target_end_date_h3,
                "year": int(r.year),
                "month": str(r.month),
                "y_up": actual,
                "target_r3": float(r.target_r3),
                "p_aurora": p_base,
                "p_echo_head": float(p_echo),
                "p_echo": float(p_out),
                "aurora_dir": bdir,
                "echo_dir": edir,
                "rescue": bool(rescue),
                "rescue_correct": bool(rescue and bdir != actual and edir == actual),
                "rescue_broken": bool(rescue and bdir == actual and edir != actual),
                "high_conf_base": bool(abs(p_base - 0.5) >= 0.20),
                "train_n": int(len(tr)),
            })
    return pd.DataFrame(rows)


def period_table(led):
    rows = []
    specs = [
        ("SELECT_2022_H2", led.forecast_issue_date.between("2022-07-01", "2022-12-31")),
        ("2023", led.year == 2023),
        ("2024", led.year == 2024),
        ("2025", led.year == 2025),
        ("2026", led.year == 2026),
        ("2023-2024", led.year.isin([2023, 2024])),
        ("2025-2026", led.year.isin([2025, 2026])),
    ]
    for period, mask in specs:
        z = led[mask].copy()
        if z.empty:
            continue
        for name, col in [("AURORA", "p_aurora"), ("ECHO", "p_echo")]:
            m = metrics(z.y_up, z[col])
            rows.append({
                "period": period,
                "model": name,
                **m,
                "overrides": int(z.rescue.sum()) if name == "ECHO" else 0,
                "correct_rescue": int(z.rescue_correct.sum()) if name == "ECHO" else 0,
                "broken": int(z.rescue_broken.sum()) if name == "ECHO" else 0,
                "high_conf_correct_rescue": int((z.rescue_correct & z.high_conf_base).sum()) if name == "ECHO" else 0,
            })
    return pd.DataFrame(rows)


def select_head(ledgers):
    rows = []
    for head, led in ledgers.items():
        mdf = period_table(led)
        b = mdf[(mdf.period == "SELECT_2022_H2") & (mdf.model == "AURORA")].iloc[0]
        e = mdf[(mdf.period == "SELECT_2022_H2") & (mdf.model == "ECHO")].iloc[0]

        eligible = bool(
            e.balanced_accuracy + 1e-12 >= b.balanced_accuracy
            and e.accuracy + 0.005 + 1e-12 >= b.accuracy
            and e.brier <= b.brier + 0.0025 + 1e-12
            and int(e.overrides) >= 3
        )
        rows.append({
            "head": head,
            "eligible": eligible,
            "delta_accuracy": float(e.accuracy - b.accuracy),
            "delta_balanced_accuracy": float(e.balanced_accuracy - b.balanced_accuracy),
            "delta_brier": float(e.brier - b.brier),
            "delta_logloss": float(e.logloss - b.logloss),
            "overrides": int(e.overrides),
            "correct_rescue": int(e.correct_rescue),
            "broken": int(e.broken),
            "accuracy": float(e.accuracy),
            "balanced_accuracy": float(e.balanced_accuracy),
            "brier": float(e.brier),
            "logloss": float(e.logloss),
        })

    tab = pd.DataFrame(rows)
    elig = tab[tab.eligible].copy()
    if elig.empty:
        return tab, None
    elig = elig.sort_values(
        ["balanced_accuracy", "accuracy", "brier", "logloss"],
        ascending=[False, False, True, True],
    )
    return tab, str(elig.iloc[0]["head"])


def confirmation(mdf):
    checks = []
    ok = True
    for yr in ["2023", "2024"]:
        b = mdf[(mdf.period == yr) & (mdf.model == "AURORA")].iloc[0]
        e = mdf[(mdf.period == yr) & (mdf.model == "ECHO")].iloc[0]
        passed = bool(
            e.accuracy + 0.01 + 1e-12 >= b.accuracy
            and e.brier <= b.brier + 0.003 + 1e-12
        )
        checks.append({
            "period": yr,
            "pass": passed,
            "base_accuracy": float(b.accuracy),
            "echo_accuracy": float(e.accuracy),
            "base_balanced_accuracy": float(b.balanced_accuracy),
            "echo_balanced_accuracy": float(e.balanced_accuracy),
            "base_brier": float(b.brier),
            "echo_brier": float(e.brier),
        })
        ok = ok and passed

    b = mdf[(mdf.period == "2023-2024") & (mdf.model == "AURORA")].iloc[0]
    e = mdf[(mdf.period == "2023-2024") & (mdf.model == "ECHO")].iloc[0]
    agg_ok = bool(e.balanced_accuracy + 1e-12 >= b.balanced_accuracy)
    rescue_ok = bool(int(e.correct_rescue) > 0)
    return bool(ok and agg_ok and rescue_ok), checks, agg_ok, rescue_ok


def rescue_detail(led, year):
    z = led[(led.year == year) & (led.rescue)].copy()
    if z.empty:
        return z
    z["base_correct"] = z.aurora_dir.astype(int) == z.y_up.astype(int)
    z["echo_correct"] = z.echo_dir.astype(int) == z.y_up.astype(int)
    return z[[
        "forecast_issue_date", "target_end_date_h3", "target_r3",
        "p_aurora", "p_echo_head", "p_echo",
        "aurora_dir", "echo_dir", "y_up",
        "base_correct", "echo_correct", "high_conf_base",
    ]]


def row_logloss(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return -(y * np.log(p) + (1-y) * np.log(1-p))


def paired_diffs(y, cand, base):
    y = np.asarray(y, int)
    cand = np.asarray(cand, float)
    base = np.asarray(base, float)
    return {
        "accuracy": (((cand >= 0.5).astype(int) == y).astype(float)
                     - ((base >= 0.5).astype(int) == y).astype(float)),
        "brier": (cand-y)**2 - (base-y)**2,
        "logloss": row_logloss(y, cand) - row_logloss(y, base),
    }


def circular_bootstrap(diff, block_len, rng):
    diff = np.asarray(diff, float)
    n = len(diff)
    nblocks = int(np.ceil(n / block_len))
    offsets = np.arange(block_len, dtype=int)
    vals = np.empty(BOOT_REPS, float)
    batch = 500
    for st in range(0, BOOT_REPS, batch):
        m = min(batch, BOOT_REPS-st)
        starts = rng.integers(0, n, size=(m, nblocks))
        idx = (starts[:, :, None] + offsets[None, None, :]) % n
        idx = idx.reshape(m, -1)[:, :n]
        vals[st:st+m] = diff[idx].mean(axis=1)
    return vals


def inference(led):
    rows = []
    seed_i = 0
    for period, mask in [
        ("2026", led.year == 2026),
        ("2025-2026", led.year.isin([2025, 2026])),
    ]:
        z = led[mask].copy()
        y = z.y_up.to_numpy(int)
        diffs = paired_diffs(y, z.p_echo, z.p_aurora)
        for metric, diff in diffs.items():
            for block in BOOT_BLOCKS:
                seed_i += 1
                rng = np.random.default_rng(SEED + seed_i)
                boot = circular_bootstrap(diff, block, rng)
                lo, hi = np.quantile(boot, [0.025, 0.975])
                improve = float(np.mean(boot > 0)) if metric == "accuracy" else float(np.mean(boot < 0))
                rows.append({
                    "period": period,
                    "comparison": "ECHO_vs_AURORA",
                    "metric": metric,
                    "block_len": block,
                    "n": int(len(z)),
                    "observed_diff": float(np.mean(diff)),
                    "ci95_low": float(lo),
                    "ci95_high": float(hi),
                    "bootstrap_improve_share": improve,
                })
    return pd.DataFrame(rows)


def main():
    base = load_aurora()
    frames, source_meta = load_series_from_neon()
    feat = build_linked_features(base, frames)
    panel = base.merge(feat, on="feature_cutoff_date", how="inner", validate="one_to_one")
    coverage = float(len(panel) / len(base))
    if coverage < 0.99:
        raise RuntimeError(f"ECHO_FEATURE_COVERAGE_FAIL {coverage:.4f}")
    panel = panel.sort_values("forecast_issue_date").reset_index(drop=True)

    source = {
        "series": source_meta,
        "origin_coverage": coverage,
        "same_day_close_used": False,
        "timing_rule": "strictly before feature_cutoff_date",
    }
    (OUT / "echo_v1_source.json").write_text(json.dumps(source, indent=2, default=str) + "\n")

    ledgers = {}
    for head in HEADS:
        led = walk_head(panel, head)
        ledgers[head] = led
        led.to_csv(OUT / f"echo_v1_predictions_{head.lower()}.csv", index=False)

    grid, selected = select_head(ledgers)
    grid.to_csv(OUT / "echo_v1_selection_grid.csv", index=False)

    if selected is None:
        summary = {
            "schema": "ECHO_H3_V1",
            "status": "FAIL_CLOSED_NO_ELIGIBLE_LINKED_HEAD",
            "selected_head": None,
            "source": source,
            "selection_grid": grid.to_dict(orient="records"),
        }
        (OUT / "echo_v1_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n")
        (OUT / "ECHO_V1_RESULT.md").write_text(
            "# ECHO-H3 V1 — RESULT\n\n**Status:** FAIL CLOSED — no eligible 2022-H2 linked-market rescue head.\n"
        )
        print((OUT / "ECHO_V1_RESULT.md").read_text())
        return

    led = ledgers[selected]
    mdf = period_table(led)
    mdf.to_csv(OUT / "echo_v1_metrics.csv", index=False)

    ok, checks, agg_ok, rescue_ok = confirmation(mdf)
    status = "MECHANISM_PASS" if ok else "NOT_PROMOTED_CONFIRM_FAIL"

    led.to_csv(OUT / "echo_v1_selected_predictions.csv", index=False)
    d26 = rescue_detail(led, 2026)
    d26.to_csv(OUT / "echo_v1_2026_rescue_detail.csv", index=False)

    inf = inference(led) if ok else pd.DataFrame()
    if not inf.empty:
        inf.to_csv(OUT / "echo_v1_inference.csv", index=False)

    summary = {
        "schema": "ECHO_H3_V1",
        "status": status,
        "selected_head": selected,
        "source": source,
        "selection_grid": grid.to_dict(orient="records"),
        "confirmation_pass": bool(ok),
        "confirmation_checks": checks,
        "aggregate_balanced_guard": bool(agg_ok),
        "rescue_present": bool(rescue_ok),
        "metrics": mdf.to_dict(orient="records"),
        "rescue_2026": d26.to_dict(orient="records"),
        "inference": inf.to_dict(orient="records") if not inf.empty else [],
    }
    (OUT / "echo_v1_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n")

    lines = [
        "# ECHO-H3 V1 — GOLD-LINKED MARKET CONFIRMATION RESCUE RESULT", "",
        f"**Status:** **{status}**  ",
        f"**Selected head (2022-H2 only):** **{selected}**  ",
        f"**Origin coverage:** **{100*coverage:.2f}%**  ",
        f"**Same-day linked close used:** **NO**  ",
        f"**2023 + 2024 confirmation:** **{ok}**", "",
        "## Selection grid — 2022 H2", "",
        "| Head | Eligible | ΔAcc | ΔBA | ΔBrier | Overrides | Correct rescue | Broken |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in grid.itertuples():
        lines.append(
            f"| {r.head} | {r.eligible} | {100*r.delta_accuracy:+.2f} pp | "
            f"{100*r.delta_balanced_accuracy:+.2f} pp | {r.delta_brier:+.4f} | "
            f"{int(r.overrides)} | {int(r.correct_rescue)} | {int(r.broken)} |"
        )

    lines += ["", "## Period metrics", "",
              "| Model | Period | N | Accuracy | Balanced | Brier | Overrides | Correct rescue | Broken |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for period in ["SELECT_2022_H2", "2023", "2024", "2025", "2026", "2025-2026"]:
        for name in ["AURORA", "ECHO"]:
            q = mdf[(mdf.period == period) & (mdf.model == name)]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(
                f"| {name} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
                f"{int(r.overrides)} | {int(r.correct_rescue)} | {int(r.broken)} |"
            )

    lines += ["", "## 2026 override details", ""]
    if d26.empty:
        lines.append("- no 2026 overrides")
    else:
        lines += [
            "| Issue | Target end | AURORA pUP | ECHO head pUP | AURORA | ECHO | Actual | H3 return | Base correct | ECHO correct | High-conf base |",
            "|---|---|---:|---:|---|---|---|---:|---|---|---|",
        ]
        for r in d26.itertuples():
            ad = "UP" if int(r.aurora_dir) == 1 else "DOWN"
            ed = "UP" if int(r.echo_dir) == 1 else "DOWN"
            yy = "UP" if int(r.y_up) == 1 else "DOWN"
            lines.append(
                f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | "
                f"{100*r.p_aurora:.1f}% | {100*r.p_echo_head:.1f}% | {ad} | {ed} | {yy} | "
                f"{100*r.target_r3:+.2f}% | {bool(r.base_correct)} | {bool(r.echo_correct)} | {bool(r.high_conf_base)} |"
            )

    if not inf.empty:
        lines += ["", "## Dependence-aware bootstrap", ""]
        for rr in inf.itertuples():
            scale = 100.0 if rr.metric == "accuracy" else 1.0
            suffix = " pp" if rr.metric == "accuracy" else ""
            lines.append(
                f"- {rr.period} {rr.metric} block{rr.block_len}: "
                f"diff={scale*rr.observed_diff:+.4f}{suffix}; "
                f"95%=[{scale*rr.ci95_low:+.4f}, {scale*rr.ci95_high:+.4f}]{suffix}; "
                f"P(improve)={100*rr.bootstrap_improve_share:.1f}%."
            )

    lines += ["", "## Governance", "",
              "ECHO uses linked-market observations strictly before each AURORA feature-cutoff date. "
              "Only LINKED_ONLY vs AURORA_PLUS_LINKED was selected on 2022-H2. "
              "Feature definitions, C and rescue thresholds were frozen before opening 2023-2026. "
              "The frozen AURORA prospective champion remains unchanged."]

    (OUT / "ECHO_V1_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "ECHO_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
