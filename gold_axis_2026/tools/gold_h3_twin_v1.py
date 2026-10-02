from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score

import gold_h3_iris_v1 as iris

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_twin_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

AURORA = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"

KNN_K = 25
MIN_MEMORY = 40
UP_OVERRIDE = 0.70
DOWN_OVERRIDE = 0.30
SEED = 20261002

REPS = ["SHAPE24", "SHAPE48", "SHAPE_MULTI"]


def metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(np.mean((p-y)**2)),
        "logloss": float(log_loss(y, p, labels=[0,1])),
        "up_recall": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "down_recall": float(recall_score(y, pred, pos_label=0, zero_division=0)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def fetch_hourly():
    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError("TWIN_SOURCE_BRIDGE_FAIL")
    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    h = pd.concat([hist, ext], ignore_index=True)
    h = h.sort_values("ts").drop_duplicates("ts", keep="last").reset_index(drop=True)
    return h, bridge, api_calls


def paa(x, blocks):
    x = np.asarray(x, float)
    n = len(x)
    if n % blocks != 0:
        raise ValueError((n, blocks))
    return x.reshape(blocks, n//blocks).mean(axis=1)


def norm_cum_path(rets):
    r = np.asarray(rets, float)
    scale = float(np.sqrt(np.sum(r*r)) + 1e-12)
    return np.cumsum(r) / scale


def build_shape_embeddings(hourly, dates):
    q = hourly.copy().sort_values("ts").reset_index(drop=True)
    q["ts_ny"] = q.ts.dt.tz_convert(iris.TZ)
    q["local_date"] = pd.to_datetime(q.ts_ny.dt.date)
    q["local_hour"] = q.ts_ny.dt.hour
    q["local_minute"] = q.ts_ny.dt.minute
    q["logp"] = np.log(q.value.astype(float))

    rows = []
    for d in sorted(pd.to_datetime(pd.Series(list(dates))).dropna().unique()):
        d = pd.Timestamp(d)
        anchor_local = pd.Timestamp(f"{d.date()} 16:00:00").tz_localize(iris.TZ)
        anchor_utc = anchor_local.tz_convert("UTC")
        z = q[q.ts <= anchor_utc].tail(49).copy()
        if len(z) < 49:
            continue
        vals = z.logp.to_numpy(float)
        rets48 = np.diff(vals)
        if len(rets48) != 48:
            continue
        rets24 = rets48[-24:]

        s24 = paa(norm_cum_path(rets24), 8)
        s48 = paa(norm_cum_path(rets48), 12)
        row = {"feature_cutoff_date": d}
        for i,v in enumerate(s24):
            row[f"s24_{i}"] = float(v)
        for i,v in enumerate(s48):
            row[f"s48_{i}"] = float(v)
        rows.append(row)

    out = pd.DataFrame(rows)
    return out


def rep_cols(rep):
    c24 = [f"s24_{i}" for i in range(8)]
    c48 = [f"s48_{i}" for i in range(12)]
    if rep == "SHAPE24":
        return c24
    if rep == "SHAPE48":
        return c48
    if rep == "SHAPE_MULTI":
        return c24 + c48
    raise KeyError(rep)


def local_probability(memory, row, rep):
    cols = rep_cols(rep)
    if len(memory) < MIN_MEMORY:
        return np.nan, 0, np.nan

    X = memory[cols].to_numpy(float)
    x = row[cols].to_numpy(float)

    mu = np.nanmean(X, axis=0)
    sd = np.nanstd(X, axis=0)
    sd = np.where(sd < 1e-8, 1.0, sd)
    Xz = (X - mu) / sd
    xz = (x - mu) / sd

    dist = np.sqrt(np.sum((Xz - xz)**2, axis=1))
    k = min(KNN_K, len(memory))
    ix = np.argsort(dist)[:k]
    dk = dist[ix]
    med = float(np.median(dk))
    tau = med if med > 1e-8 else 1.0
    w = np.exp(-dk / tau)
    y = memory.iloc[ix].y_up.to_numpy(float)
    p = float(np.sum(w*y) / np.sum(w))
    return p, int(k), float(np.mean(dk))


def apply_rep(panel, rep):
    rows = []
    g = panel.sort_values("forecast_issue_date").reset_index(drop=True)

    for i, r in g.iterrows():
        cutoff = pd.Timestamp(r.feature_cutoff_date)
        mem = g[
            (g.target_end_date_h3 <= cutoff)
            & (g.forecast_issue_date < r.forecast_issue_date)
        ].copy()
        p_local, nn, mean_dist = local_probability(mem, r, rep)

        p_base = float(r.p_aurora)
        base_dir = int(p_base >= 0.5)
        rescue = False
        p_out = p_base

        if np.isfinite(p_local):
            if base_dir == 0 and p_local >= UP_OVERRIDE:
                rescue = True
                p_out = float(p_local)
            elif base_dir == 1 and p_local <= DOWN_OVERRIDE:
                rescue = True
                p_out = float(p_local)

        out_dir = int(p_out >= 0.5)
        actual = int(r.y_up)
        rows.append({
            "rep": rep,
            "feature_cutoff_date": r.feature_cutoff_date,
            "forecast_issue_date": r.forecast_issue_date,
            "target_end_date_h3": r.target_end_date_h3,
            "year": int(r.year),
            "month": str(r.month),
            "y_up": actual,
            "target_r3": float(r.target_r3),
            "p_aurora": p_base,
            "p_local": p_local,
            "p_twin": p_out,
            "aurora_dir": base_dir,
            "twin_dir": out_dir,
            "rescue": bool(rescue),
            "rescue_correct": bool(rescue and out_dir == actual),
            "rescue_broken": bool(rescue and base_dir == actual and out_dir != actual),
            "nn": nn,
            "mean_nn_distance": mean_dist,
        })
    return pd.DataFrame(rows)


def period_rows(led):
    rows = []
    specs = [
        ("SELECT_2022_H2", led.forecast_issue_date.between("2022-07-01","2022-12-31")),
        ("2023", led.year == 2023),
        ("2024", led.year == 2024),
        ("2025", led.year == 2025),
        ("2026", led.year == 2026),
        ("2023-2024", led.year.isin([2023,2024])),
        ("2025-2026", led.year.isin([2025,2026])),
    ]
    for period, mask in specs:
        z = led[mask].copy()
        if z.empty:
            continue
        for model,col in [("AURORA","p_aurora"),("TWIN","p_twin")]:
            m = metrics(z.y_up, z[col])
            rows.append({
                "period": period,
                "model": model,
                **m,
                "rescues": int(z.rescue.sum()) if model=="TWIN" else 0,
                "rescue_correct": int(z.rescue_correct.sum()) if model=="TWIN" else 0,
                "rescue_broken": int(z.rescue_broken.sum()) if model=="TWIN" else 0,
            })
    return pd.DataFrame(rows)


def selection(all_ledgers):
    rows = []
    selected_led = None
    for rep, led in all_ledgers.items():
        mdf = period_rows(led)
        b = mdf[(mdf.period=="SELECT_2022_H2")&(mdf.model=="AURORA")].iloc[0]
        t = mdf[(mdf.period=="SELECT_2022_H2")&(mdf.model=="TWIN")].iloc[0]
        eligible = bool(
            t.balanced_accuracy + 1e-12 >= b.balanced_accuracy
            and t.accuracy + 0.005 + 1e-12 >= b.accuracy
            and t.brier <= b.brier + 0.0025 + 1e-12
            and int(t.rescues) >= 3
        )
        rows.append({
            "rep": rep,
            "eligible": eligible,
            "delta_accuracy": float(t.accuracy-b.accuracy),
            "delta_balanced_accuracy": float(t.balanced_accuracy-b.balanced_accuracy),
            "delta_brier": float(t.brier-b.brier),
            "delta_logloss": float(t.logloss-b.logloss),
            "rescues": int(t.rescues),
            "rescue_correct": int(t.rescue_correct),
            "rescue_broken": int(t.rescue_broken),
            "accuracy": float(t.accuracy),
            "balanced_accuracy": float(t.balanced_accuracy),
            "brier": float(t.brier),
            "logloss": float(t.logloss),
        })
    tab = pd.DataFrame(rows)
    elig = tab[tab.eligible].copy()
    if elig.empty:
        return tab, None
    elig = elig.sort_values(
        ["balanced_accuracy","accuracy","brier","logloss"],
        ascending=[False,False,True,True],
    )
    return tab, str(elig.iloc[0].rep)


def confirmation(mdf):
    checks=[]
    ok=True
    for yr in ["2023","2024"]:
        b=mdf[(mdf.period==yr)&(mdf.model=="AURORA")].iloc[0]
        t=mdf[(mdf.period==yr)&(mdf.model=="TWIN")].iloc[0]
        passed=bool(
            t.accuracy + 0.01 + 1e-12 >= b.accuracy
            and t.brier <= b.brier + 0.003 + 1e-12
        )
        checks.append({
            "period":yr,"pass":passed,
            "base_accuracy":float(b.accuracy),
            "twin_accuracy":float(t.accuracy),
            "base_balanced_accuracy":float(b.balanced_accuracy),
            "twin_balanced_accuracy":float(t.balanced_accuracy),
            "base_brier":float(b.brier),
            "twin_brier":float(t.brier),
        })
        ok=ok and passed

    b=mdf[(mdf.period=="2023-2024")&(mdf.model=="AURORA")].iloc[0]
    t=mdf[(mdf.period=="2023-2024")&(mdf.model=="TWIN")].iloc[0]
    agg=bool(t.balanced_accuracy + 1e-12 >= b.balanced_accuracy)
    rescue=bool(t.rescues > 0)
    return bool(ok and agg and rescue), checks, agg, rescue


def rescue_detail(led, year):
    z=led[(led.year==year)&(led.rescue)].copy()
    if z.empty:
        return z
    z["base_correct"] = z.aurora_dir.astype(int)==z.y_up.astype(int)
    z["twin_correct"] = z.twin_dir.astype(int)==z.y_up.astype(int)
    return z[[
        "forecast_issue_date","target_end_date_h3","target_r3",
        "p_aurora","p_local","p_twin","aurora_dir","twin_dir","y_up",
        "base_correct","twin_correct","mean_nn_distance"
    ]].copy()


def main():
    base = pd.read_csv(AURORA)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        base[c]=pd.to_datetime(base[c],errors="raise")

    hourly, bridge, api_calls = fetch_hourly()
    emb = build_shape_embeddings(hourly, base.feature_cutoff_date.unique())
    panel = base.merge(emb,on="feature_cutoff_date",how="inner",validate="one_to_one")
    if len(panel) != len(base):
        raise RuntimeError(f"TWIN_EMBEDDING_MATCH_FAIL base={len(base)} panel={len(panel)}")
    panel = panel.sort_values("forecast_issue_date").reset_index(drop=True)

    all_ledgers={}
    for rep in REPS:
        led=apply_rep(panel,rep)
        all_ledgers[rep]=led
        led.to_csv(OUT/f"twin_v1_predictions_{rep.lower()}.csv",index=False)

    sel_grid, selected = selection(all_ledgers)
    sel_grid.to_csv(OUT/"twin_v1_selection_grid.csv",index=False)

    if selected is None:
        summary={
            "schema":"TWIN_H3_V1",
            "status":"FAIL_CLOSED_NO_ELIGIBLE_SHAPE_REPRESENTATION",
            "source_bridge":bridge,
            "api_calls":int(api_calls),
        }
        (OUT/"twin_v1_summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
        (OUT/"TWIN_V1_RESULT.md").write_text("# TWIN-H3 V1 — RESULT\n\n**Status:** FAIL CLOSED — no eligible 2022-H2 representation.\n")
        print((OUT/"TWIN_V1_RESULT.md").read_text())
        return

    led=all_ledgers[selected]
    mdf=period_rows(led)
    mdf.to_csv(OUT/"twin_v1_metrics.csv",index=False)

    ok, checks, agg_ok, rescue_ok=confirmation(mdf)
    status="MECHANISM_PASS" if ok else "NOT_PROMOTED_CONFIRM_FAIL"

    led.to_csv(OUT/"twin_v1_selected_predictions.csv",index=False)
    d26=rescue_detail(led,2026)
    d26.to_csv(OUT/"twin_v1_2026_rescue_detail.csv",index=False)

    summary={
        "schema":"TWIN_H3_V1",
        "status":status,
        "selected_representation":selected,
        "source_bridge":bridge,
        "api_calls":int(api_calls),
        "selection_grid":sel_grid.to_dict(orient="records"),
        "confirmation_pass":bool(ok),
        "confirmation_checks":checks,
        "aggregate_balanced_guard":bool(agg_ok),
        "rescue_present":bool(rescue_ok),
        "metrics":mdf.to_dict(orient="records"),
        "rescue_2026":d26.to_dict(orient="records"),
    }
    (OUT/"twin_v1_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    lines=[
        "# TWIN-H3 V1 — PATH-SHAPE ANALOGUE RESCUE RESULT","",
        f"**Status:** **{status}**  ",
        f"**Selected representation (2022-H2 only):** **{selected}**  ",
        f"**k:** {KNN_K}  ",
        f"**Override:** local p>=0.70 against DOWN / <=0.30 against UP  ",
        f"**2023 + 2024 confirmation:** **{ok}**","",
        "## Selection grid — 2022 H2","",
        "| Representation | Eligible | ΔAcc | ΔBA | ΔBrier | Rescues | Correct rescue | Broken |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in sel_grid.itertuples():
        lines.append(
            f"| {r.rep} | {r.eligible} | {100*r.delta_accuracy:+.2f} pp | "
            f"{100*r.delta_balanced_accuracy:+.2f} pp | {r.delta_brier:+.4f} | "
            f"{int(r.rescues)} | {int(r.rescue_correct)} | {int(r.rescue_broken)} |"
        )

    lines += ["","## Period metrics","",
              "| Model | Period | N | Accuracy | Balanced | Brier | Rescues | Correct rescue | Broken |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for period in ["SELECT_2022_H2","2023","2024","2025","2026","2025-2026"]:
        for model in ["AURORA","TWIN"]:
            q=mdf[(mdf.period==period)&(mdf.model==model)]
            if q.empty: continue
            r=q.iloc[0]
            lines.append(
                f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
                f"{int(r.rescues)} | {int(r.rescue_correct)} | {int(r.rescue_broken)} |"
            )

    lines += ["","## 2026 override details",""]
    if d26.empty:
        lines.append("- no 2026 overrides")
    else:
        lines += ["| Issue | Target end | AURORA pUP | Local pUP | AURORA dir | TWIN dir | Actual | H3 return | Base correct | TWIN correct |",
                  "|---|---|---:|---:|---|---|---|---:|---|---|"]
        for r in d26.itertuples():
            ad="UP" if int(r.aurora_dir)==1 else "DOWN"
            td="UP" if int(r.twin_dir)==1 else "DOWN"
            yy="UP" if int(r.y_up)==1 else "DOWN"
            lines.append(
                f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | "
                f"{100*r.p_aurora:.1f}% | {100*r.p_local:.1f}% | {ad} | {td} | {yy} | "
                f"{100*r.target_r3:+.2f}% | {bool(r.base_correct)} | {bool(r.twin_correct)} |"
            )

    lines += ["","## Governance","",
              "Only representation choice used 2022-H2. k=25 and rescue thresholds 0.70/0.30 were fixed before the run. "
              "2025/2026 results did not alter V1. The frozen AURORA prospective ledger is unchanged."]

    (OUT/"TWIN_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"TWIN_V1_RESULT.md").read_text())


if __name__=="__main__":
    main()
