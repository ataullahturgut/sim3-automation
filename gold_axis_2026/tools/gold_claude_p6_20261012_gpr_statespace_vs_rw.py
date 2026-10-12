#!/usr/bin/env python3
"""CLAUDE P6 — GP-LAG and local-linear-trend vs random walk (frozen by
GOLD_CLAUDE_P6_20261012_GPR_STATESPACE_VS_RW_PREREG.md, commit ec2ca3d5).

Inputs : data_claude_p1/GOLD_CLAUDE_P1_PANEL_<year>.csv
Outputs: GOLD_CLAUDE_P6_20261012_{SCORE_ROWS.csv,SUMMARY.json}
"""
import csv
import json
import math
import os
import warnings
from datetime import datetime, timedelta

import numpy as np
from scipy import stats
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from statsmodels.tsa.statespace.structural import UnobservedComponents

warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "GOLD_CLAUDE_P6_20261012_")
DEV = (2023, 2024)
YEARS = (2023, 2024, 2025, 2026)
CAP = 750
MIN_TRAIN = 250
MODELS = ("RW", "INT", "GP", "LLT")
CANDS = ("GP", "LLT")


def load():
    rows = []
    for y in range(2020, 2027):
        with open(os.path.join(ROOT, "data_claude_p1", f"GOLD_CLAUDE_P1_PANEL_{y}.csv")) as fh:
            for r in csv.DictReader(fh):
                d = datetime.strptime(r["d"], "%Y%m%d").date()
                f = lambda k: float(r[k]) if r[k] else None
                p0900 = float(r["p0900"])
                rows.append(dict(d=d, year=d.year, day_ok=r["day_ok"] == "1", ovn_ok=r["ovn_ok"] == "1", p0900=p0900,
                                 p1645=p0900 * math.exp(float(r["y_day"]) / 1e4), y_day=f("y_day"), y_ovn=f("y_ovn"),
                                 f_us=f("f_us"), f_asia=f("f_asia"), g=f("g_daysofar")))
    rows.sort(key=lambda r: r["d"])
    return rows


def last_k(vals, k=5):
    v = vals[-k:]
    return [0.0] * (k - len(v)) + v


def build(rows):
    day_ret = [(r["d"], r["y_day"]) for r in rows if r["day_ok"]]
    ovn_ret = [(r["d"], r["y_ovn"]) for r in rows if r["ovn_ok"] and r["y_ovn"] is not None]
    obs = {"DAY": [], "OVN": []}
    for r in rows:
        d = r["d"]
        if r["day_ok"] and r["f_us"] is not None and r["f_asia"] is not None:
            dl = [v for dd, v in day_ret if dd < d]
            ol = [v for dd, v in ovn_ret if dd + timedelta(days=1) < d]  # OVN ended at 09:00 on dd+1 < d
            obs["DAY"].append(dict(d=d, year=r["year"], y=r["y_day"], origin=r["p0900"],
                                   x=last_k(dl) + last_k(ol) + [r["f_us"], r["f_asia"]]))
        if r["ovn_ok"] and r["y_ovn"] is not None and r["g"] is not None:
            ol = [v for dd, v in ovn_ret if dd < d]
            dl = [v for dd, v in day_ret if dd < d]
            obs["OVN"].append(dict(d=d, year=r["year"], y=r["y_ovn"], origin=r["p1645"],
                                   x=last_k(ol) + last_k(dl) + [r["g"]]))
    # merged clock series (log price, bp) for LLT: (timestamp_key, value)
    series = []
    for r in rows:
        series.append(((r["d"], 0), 1e4 * math.log(r["p0900"])))
        series.append(((r["d"], 1), 1e4 * math.log(r["p1645"])))
    return obs, series


def gp_forecasts(obs):
    out = {}
    kern_cache = None
    month = None
    for j, o in enumerate(obs):
        if o["year"] < 2023:
            continue
        train = obs[max(0, j - CAP):j]
        if len(obs[:j]) < MIN_TRAIN:
            continue
        X = np.array([t["x"] for t in train])
        y = np.array([t["y"] for t in train])
        mu, sd = X.mean(0), X.std(0)
        sd[sd == 0] = 1.0
        Z = (X - mu) / sd
        zq = ((np.array(o["x"]) - mu) / sd).reshape(1, -1)
        key = (o["d"].year, o["d"].month)
        if key != month or kern_cache is None:
            k0 = ConstantKernel(1.0) * RBF(length_scale=3.0) + WhiteKernel(noise_level=1.0)
            gp = GaussianProcessRegressor(kernel=k0, normalize_y=True, n_restarts_optimizer=0, random_state=0).fit(Z, y)
            kern_cache, month = gp.kernel_, key
        else:
            gp = GaussianProcessRegressor(kernel=kern_cache, normalize_y=True, optimizer=None).fit(Z, y)
        m, s = gp.predict(zq, return_std=True)
        out[o["d"]] = (float(m[0]), float(s[0]))
    return out


def llt_forecasts(obs, series, target):
    out = {}
    params, month = None, None
    keys = [k for k, _ in series]
    vals = np.array([v for _, v in series])
    for o in obs:
        if o["year"] < 2023:
            continue
        # last observation available at decision: DAY 08:45 -> previous 16:45; OVN 16:30 -> same-day 09:00
        cutoff = (o["d"], 0) if target == "DAY" else (o["d"], 1)
        n = sum(1 for k in keys if k < cutoff)
        ysub = vals[:n]
        mod = UnobservedComponents(ysub, level="local linear trend")
        key = (o["d"].year, o["d"].month)
        if key != month or params is None:
            params = mod.fit(disp=False, maxiter=200).params
            month = key
        res = mod.filter(params)
        out[o["d"]] = float(res.filtered_state[1, -1])
    return out


def nw_dm(d, lags=5):
    d = np.asarray(d, float)
    n = len(d)
    e = d - d.mean()
    v = e @ e / n
    for k in range(1, lags + 1):
        v += 2 * (1 - k / (lags + 1)) * (e[k:] @ e[:-k]) / n
    t = d.mean() / math.sqrt(max(v, 1e-18) / n)
    return float(t), float(1 - stats.norm.cdf(t))


def dir_metrics(y, yh):
    keep = y != 0
    y, yh = y[keep], yh[keep]
    up, pu = y > 0, yh >= 0
    ru = float((pu & up).sum() / max(up.sum(), 1))
    rd = float((~pu & ~up).sum() / max((~up).sum(), 1))
    return dict(acc=float((pu == up).mean()), ba=(ru + rd) / 2, recall_up=ru, recall_down=rd)


def main():
    rows = load()
    obs, series = build(rows)
    summary = {"prereg_commit": "ec2ca3d5d0abbfc48915f4fdc6c46ee46a13ff46", "targets": {}}
    score_rows, dm_p = [], {}
    for T in ("DAY", "OVN"):
        ob = obs[T]
        gp = gp_forecasts(ob)
        print(T, "GP done", len(gp), flush=True)
        llt = llt_forecasts(ob, series, T)
        print(T, "LLT done", len(llt), flush=True)
        sc = []
        for j, o in enumerate(ob):
            if o["d"] not in gp or o["d"] not in llt:
                continue
            prior = [t["y"] for t in ob[:j]]
            sd_y = float(np.std(prior))
            rec = dict(target=T, d=o["d"].isoformat(), year=o["year"], y=o["y"], origin=o["origin"],
                       RW=0.0, INT=float(np.mean(prior)), GP=gp[o["d"]][0], GP_sd=gp[o["d"]][1], LLT=llt[o["d"]],
                       prior_up=float(np.mean(np.array(prior) > 0)), sd_y=sd_y)
            sc.append(rec)
        score_rows += sc
        tsum = {}
        for yr in YEARS:
            blk = [r for r in sc if r["year"] == yr]
            if not blk:
                tsum[str(yr)] = {"status": "BLOCKED: 0 eligible windows"}
                continue
            y = np.array([r["y"] for r in blk])
            res = {"n": len(blk)}
            for m in MODELS:
                yh = np.array([r[m] for r in blk])
                act = np.array([r["origin"] * math.exp(r["y"] / 1e4) for r in blk])
                fc = np.array([r["origin"] * math.exp(r[m] / 1e4) for r in blk])
                if m == "GP":
                    p = np.array([stats.norm.cdf(r["GP"] / r["GP_sd"]) for r in blk])
                else:
                    p = np.array([stats.norm.cdf(r[m] / r["sd_y"]) for r in blk])
                keep = y != 0
                upv = (y[keep] > 0).astype(float)
                pc = np.clip(p[keep], 1e-6, 1 - 1e-6)
                res[m] = dict(mse_bp2=float(((y - yh) ** 2).mean()), rmse_bp=float(np.sqrt(((y - yh) ** 2).mean())),
                              price_mae_usd=float(np.abs(act - fc).mean()),
                              price_rmse_usd=float(np.sqrt(((act - fc) ** 2).mean())),
                              logloss=float(-(upv * np.log(pc) + (1 - upv) * np.log(1 - pc)).mean()),
                              **dir_metrics(y, yh))
            pr = np.clip(np.array([r["prior_up"] for r in blk])[y != 0], 1e-6, 1 - 1e-6)
            upv = (y[y != 0] > 0).astype(float)
            res["PRIOR_logloss"] = float(-(upv * np.log(pr) + (1 - upv) * np.log(1 - pr)).mean())
            res["ALWAYS_UP"] = dir_metrics(y, np.zeros(len(y)))
            lo = np.array([r["GP"] - 1.645 * r["GP_sd"] for r in blk])
            hi = np.array([r["GP"] + 1.645 * r["GP_sd"] for r in blk])
            res["GP_cover90"] = float(np.mean((y >= lo) & (y <= hi)))
            for m in CANDS:
                for b in ("RW", "INT"):
                    res[m][f"r2_os_vs_{b}"] = 1 - res[m]["mse_bp2"] / res[b]["mse_bp2"]
            tsum[str(yr)] = res
        dev = [r for r in sc if r["year"] in DEV]
        y = np.array([r["y"] for r in dev])
        pooled = {"n": len(dev)}
        for m in CANDS:
            for b in ("RW", "INT"):
                d = (y - np.array([r[b] for r in dev])) ** 2 - (y - np.array([r[m] for r in dev])) ** 2
                t, p = nw_dm(d)
                pooled[f"{m}_vs_{b}"] = dict(mean_gain=float(d.mean()), t=t, p=p)
                dm_p[f"{T}:{m}_vs_{b}"] = p
        tsum["DEV_pooled"] = pooled
        summary["targets"][T] = tsum
    items = sorted(dm_p.items(), key=lambda kv: kv[1])
    adj, run = {}, 0.0
    for i, (k, v) in enumerate(items):
        run = max(run, min(1.0, (len(items) - i) * v))
        adj[k] = run
    gate = {}
    for T in ("DAY", "OVN"):
        ts = summary["targets"][T]
        for m in CANDS:
            yrs = all(ts[str(y)][m]["mse_bp2"] < min(ts[str(y)]["RW"]["mse_bp2"], ts[str(y)]["INT"]["mse_bp2"]) for y in DEV)
            hp = all(adj[f"{T}:{m}_vs_{b}"] < 0.05 for b in ("RW", "INT"))
            nr = ts["2025"][m]["mse_bp2"] < min(ts["2025"]["RW"]["mse_bp2"], ts["2025"]["INT"]["mse_bp2"])
            gate[f"{T}:{m}"] = dict(each_dev_year=yrs, holm_p_vs_RW=adj[f"{T}:{m}_vs_RW"], holm_p_vs_INT=adj[f"{T}:{m}_vs_INT"],
                                    holm_pass=hp, no_2025_reversal=nr, SUPPORTED=bool(yrs and hp and nr))
    summary["gate"] = gate
    summary["P6_VERDICT"] = "SUPPORTED_COMPONENT_EXISTS" if any(g["SUPPORTED"] for g in gate.values()) else "REJECT"
    with open(OUT + "SCORE_ROWS.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(score_rows[0].keys()))
        w.writeheader()
        for r in score_rows:
            w.writerow({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()})
    with open(OUT + "SUMMARY.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps({"verdict": summary["P6_VERDICT"], "gate": gate}, indent=1))


if __name__ == "__main__":
    main()
