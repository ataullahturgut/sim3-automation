#!/usr/bin/env python3
"""CLAUDE P2 — FOMC reaction -> next Türkiye DAY XAU/USD return (frozen by
GOLD_CLAUDE_P2_20261012_FOMC_NEXTDAY_PREREG.md, commit 83fc0b66).

Inputs : data_claude_p2/GOLD_CLAUDE_P2_FOMC_WINDOW_PRICES.csv (sql/gold_claude_p2_20261012_fomc_windows.sql)
         data_claude_p1/GOLD_CLAUDE_P1_PANEL_<year>.csv (DAY targets, P1 eligibility rule)
Outputs: GOLD_CLAUDE_P2_20261012_{EVENT_ROWS.csv,SUMMARY.json}
"""
import csv
import json
import math
import os
from datetime import date, datetime, timedelta

import numpy as np
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "GOLD_CLAUDE_P2_20261012_")
MIN_PRIOR_EVENTS = 10


def lr(a, b):
    return 1e4 * math.log(a / b) if (a and b) else None


def load_day_panel():
    day = {}
    for y in range(2020, 2027):
        with open(os.path.join(ROOT, "data_claude_p1", f"GOLD_CLAUDE_P1_PANEL_{y}.csv")) as fh:
            for r in csv.DictReader(fh):
                d = datetime.strptime(r["d"], "%Y%m%d").date()
                day[d] = dict(ok=r["day_ok"] == "1", y=float(r["y_day"]) if r["y_day"] else None,
                              p0900=float(r["p0900"]))
    return day


def load_windows(day):
    rows = []
    with open(os.path.join(ROOT, "data_claude_p2", "GOLD_CLAUDE_P2_FOMC_WINDOW_PRICES.csv")) as fh:
        for r in csv.DictReader(fh):
            d = datetime.strptime(r["d"], "%Y%m%d").date()
            f = {k: (float(r[k]) if r[k] else None) for k in ("p_pre", "p_m15", "p_p45", "p_n0830")}
            nxt = d + timedelta(days=1)
            tgt = day.get(nxt)
            rows.append(dict(
                d=d, year=d.year, target_date=nxt, sched=r["is_sched"] == "1", near=r["near_any"] == "1",
                x_react=lr(f["p_p45"], f["p_m15"]), x_pre=lr(f["p_m15"], f["p_pre"]), x_full=lr(f["p_n0830"], f["p_m15"]),
                y=(tgt["y"] if tgt and tgt["ok"] else None), origin=(tgt["p0900"] if tgt else None),
                source="DUKASCOPY_DIRECT_2026" if d.year == 2026 else "EVTRADINGLABS_DUKASCOPY_2020_2025"))
    return rows


def ols_hc3(y, X):
    """OLS with HC3 covariance. X includes intercept column. Returns beta, se, dof."""
    y, X = np.asarray(y, float), np.asarray(X, float)
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    h = np.einsum("ij,jk,ik->i", X, XtX_inv, X)
    w = (e / (1 - h)) ** 2
    cov = XtX_inv @ (X.T * w) @ X @ XtX_inv
    return b, np.sqrt(np.diag(cov)), n - k


def slope_test(rows, xkey):
    use = [r for r in rows if r[xkey] is not None and r["y"] is not None]
    n = len(use)
    if n < 6:
        return {"n": n, "status": "insufficient"}
    x = np.array([r[xkey] for r in use])
    y = np.array([r["y"] for r in use])
    b, se, dof = ols_hc3(y, np.column_stack([np.ones(n), x]))
    t = b[1] / se[1]
    rho, _ = stats.spearmanr(x, y)
    nz = [(xx, yy) for xx, yy in zip(x, y) if xx != 0 and yy != 0]
    hits = sum(1 for xx, yy in nz if np.sign(-xx) == np.sign(yy))
    up_hits = sum(1 for _, yy in nz if yy > 0)
    return dict(n=n, intercept_bp=float(b[0]), slope=float(b[1]), slope_se_hc3=float(se[1]), t=float(t),
                p_one_sided_negative=float(stats.t.cdf(t, dof)), spearman_rho=float(rho),
                reversal_hits=hits, n_sign=len(nz), reversal_hit_rate=hits / len(nz) if nz else None,
                reversal_binom_p_greater=float(stats.binomtest(hits, len(nz), 0.5, alternative="greater").pvalue) if nz else None,
                always_up_hit_rate=up_hits / len(nz) if nz else None)


def interaction_test(events, placebo, xkey):
    use = [(r, 1.0) for r in events if r[xkey] is not None and r["y"] is not None] + \
          [(r, 0.0) for r in placebo if r[xkey] is not None and r["y"] is not None]
    x = np.array([r[xkey] for r, _ in use])
    D = np.array([dd for _, dd in use])
    y = np.array([r["y"] for r, _ in use])
    b, se, dof = ols_hc3(y, np.column_stack([np.ones(len(y)), x, D, x * D]))
    t = b[3] / se[3]
    return dict(n=len(y), d_interaction=float(b[3]), se_hc3=float(se[3]), t=float(t),
                p_one_sided_negative=float(stats.t.cdf(t, dof)))


def oos_block(events, all_day, r67):
    """Expanding OOS slope forecast vs RW and INT on scheduled events."""
    ev = sorted([r for r in events if r["x_react"] is not None and r["y"] is not None], key=lambda r: r["d"])
    day_sorted = sorted((d, v["y"]) for d, v in all_day.items() if v["ok"] and v["y"] is not None)
    out = []
    for j, r in enumerate(ev):
        prior = ev[:j]
        if len(prior) < MIN_PRIOR_EVENTS:
            continue
        x = np.array([p["x_react"] for p in prior])
        y = np.array([p["y"] for p in prior])
        b, _, _ = ols_hc3(y, np.column_stack([np.ones(len(y)), x]))
        intv = np.mean([v for d, v in day_sorted if d < r["target_date"]])
        out.append(dict(r, pred_slope=float(b[0] + b[1] * r["x_react"]), pred_rw=0.0, pred_int=float(intv),
                        r67=r67.get(r["target_date"].isoformat())))
    return out


def score(rows):
    if not rows:
        return {"n": 0}
    y = np.array([r["y"] for r in rows])
    res = {"n": len(rows)}
    for m in ("slope", "rw", "int"):
        yh = np.array([r[f"pred_{m}"] for r in rows])
        actual = np.array([r["origin"] * math.exp(r["y"] / 1e4) for r in rows])
        fc = np.array([r["origin"] * math.exp(r[f"pred_{m}"] / 1e4) for r in rows])
        keep = y != 0
        up, pu = y[keep] > 0, yh[keep] >= 0
        rec_up = float((pu & up).sum() / max(up.sum(), 1))
        rec_dn = float((~pu & ~up).sum() / max((~up).sum(), 1))
        res[m] = dict(mse_bp2=float(((y - yh) ** 2).mean()), rmse_bp=float(np.sqrt(((y - yh) ** 2).mean())),
                      price_mae_usd=float(np.abs(actual - fc).mean()), acc=float((pu == up).mean()),
                      ba=(rec_up + rec_dn) / 2, recall_up=rec_up, recall_down=rec_dn)
    for b in ("rw", "int"):
        res[f"r2_os_slope_vs_{b}"] = 1 - res["slope"]["mse_bp2"] / res[b]["mse_bp2"]
    mm = [(r["y"] > 0, r["pred_slope"] >= 0, r["r67"]) for r in rows if r["r67"] is not None and r["y"] != 0]
    if mm:
        b_ = sum(1 for up, mine, th in mm if mine == up and (th == 1) != up)
        c_ = sum(1 for up, mine, th in mm if mine != up and (th == 1) == up)
        res["vs_R67_new_pred"] = dict(n=len(mm), corrected=b_, broken=c_,
                                      mcnemar_p=float(stats.binomtest(min(b_, c_), b_ + c_, 0.5).pvalue) if b_ + c_ else 1.0)
    return res


def holm(p):
    items = sorted(p.items(), key=lambda kv: kv[1])
    out, run = {}, 0.0
    for i, (k, v) in enumerate(items):
        run = max(run, min(1.0, (len(items) - i) * v))
        out[k] = run
    return out


def main():
    day = load_day_panel()
    rows = load_windows(day)
    r67 = {}
    with open(os.path.join(ROOT, "GOLD_R67_20261012_H3_AS_DAY_AND_OVN_CONDITIONER_2023_2026_ROWS.csv")) as fh:
        for r in csv.DictReader(fh):
            if r["clock"] == "DAY":
                r67[r["day"]] = int(r["new_pred"])
    ev_all = [r for r in rows if r["sched"]]
    ev = [r for r in ev_all if 2020 <= r["year"] <= 2024]
    pl = [r for r in rows if not r["sched"] and not r["near"] and 2020 <= r["year"] <= 2024 and r["d"].isoweekday() == 3]
    s = {"prereg_commit": "83fc0b669060fcff09a9503ed874ac64fbd404a1",
         "events_total_scheduled": len(ev_all),
         "data_gate": {str(y): dict(scheduled=sum(1 for r in ev_all if r["year"] == y),
                                     usable=sum(1 for r in ev_all if r["year"] == y and r["x_react"] is not None and r["y"] is not None))
                       for y in range(2020, 2027)}}
    s["primary"] = slope_test(ev, "x_react")
    s["placebo"] = slope_test(pl, "x_react")
    s["interaction"] = interaction_test(ev, pl, "x_react")
    oos_all = oos_block(ev_all, day, r67)
    s["oos_2021_2024"] = score([r for r in oos_all if 2021 <= r["year"] <= 2024])
    s["oos_by_year"] = {str(y): score([r for r in oos_all if r["year"] == y]) for y in range(2021, 2027)}
    s["secondary"] = {k: slope_test(ev, k) for k in ("x_pre", "x_full")}
    s["secondary_holm"] = holm({k: v["p_one_sided_negative"] for k, v in s["secondary"].items()})
    s["placebo_secondary"] = {k: slope_test(pl, k) for k in ("x_pre", "x_full")}
    s["by_year"] = {str(y): slope_test([r for r in ev_all if r["year"] == y], "x_react") for y in range(2020, 2027)}
    s["opened_2025"] = slope_test([r for r in ev_all if r["year"] == 2025], "x_react")
    s["opened_2026"] = slope_test([r for r in ev_all if r["year"] == 2026], "x_react")
    o = s["oos_2021_2024"]
    gate = dict(
        primary_p_lt_005=s["primary"]["p_one_sided_negative"] < 0.05,
        placebo_not_negative=s["placebo"]["p_one_sided_negative"] >= 0.05,
        interaction_p_lt_005=s["interaction"]["p_one_sided_negative"] < 0.05,
        oos_beats_rw_and_int=bool(o["n"] and o["slope"]["mse_bp2"] < min(o["rw"]["mse_bp2"], o["int"]["mse_bp2"])))
    gate["TENTATIVE"] = all(gate.values())
    s["gate"] = gate
    s["P2_VERDICT"] = "TENTATIVE" if gate["TENTATIVE"] else "REJECT"
    with open(OUT + "EVENT_ROWS.csv", "w", newline="") as fh:
        keys = ["d", "target_date", "year", "source", "sched", "x_react", "x_pre", "x_full", "y", "origin",
                "pred_slope", "pred_rw", "pred_int", "r67"]
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        oos_map = {r["d"]: r for r in oos_all}
        for r in ev_all:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in {**r, **oos_map.get(r["d"], {})}.items()})
    with open(OUT + "SUMMARY.json", "w") as fh:
        json.dump(s, fh, indent=1, default=str)
    print(json.dumps({"verdict": s["P2_VERDICT"], "gate": gate, "primary": s["primary"], "placebo": s["placebo"],
                      "interaction": s["interaction"]}, indent=1))


if __name__ == "__main__":
    main()
