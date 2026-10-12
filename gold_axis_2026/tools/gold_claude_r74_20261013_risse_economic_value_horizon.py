#!/usr/bin/env python3
"""CLAUDE R74 — Risse (2019, IJF) perspective: economic value of XAU/USD forecasts by horizon.
Frozen by GOLD_CLAUDE_R74_20261013_RISSE_ECONOMIC_VALUE_HORIZON_PREREG.md (commit 3d3240d3).

Inputs : data_claude_r74/GOLD_CLAUDE_R74_{STAKTRAKR_METALS_DAILY,NASDAQ100_DAILY,FEDFUNDS_MONTHLY}.csv
         data_claude_p1/GOLD_CLAUDE_P1_PANEL_<year>.csv (exact-clock 16:45 TR prices)
Outputs: GOLD_CLAUDE_R74_20261013_{SUMMARY.json,PERIOD_ROWS.csv}
"""
import csv
import json
import math
import os
import warnings
from bisect import bisect_left
from datetime import date, datetime
from multiprocessing import Pool

import numpy as np
from scipy import stats
from sklearn.svm import SVR

warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D74 = os.path.join(ROOT, "data_claude_r74")
OUT = os.path.join(ROOT, "GOLD_CLAUDE_R74_20261013_")
GAMMA = 3.0
CLIP = (-0.5, 1.5)
J = 4
LAMBDA = 0.94
MIN_BLOCKS = 120
CAP = 1500
COSTS_BP = (0, 2, 5, 10, 25)
STRATS = ("S0_HM_PAPER", "S1_DWTSVR_PAPER", "S2_SVRRAW_PAPER", "S3_VOLTIMING", "S4_DWTSVR_EWMA", "S5_BUYHOLD")


def d8(s):
    return datetime.strptime(s, "%Y%m%d").date()


def load_rf():
    ff = {}
    with open(os.path.join(D74, "GOLD_CLAUDE_R74_FEDFUNDS_MONTHLY.csv")) as fh:
        for r in csv.DictReader(fh):
            d = d8(r["d"])
            ff[(d.year, d.month)] = float(r["value"])

    keys = sorted(ff)

    def rf(d):  # latest monthly value strictly before the current month, % p.a. -> daily
        k = bisect_left(keys, (d.year, d.month)) - 1
        return ff[keys[k]] / 100 / 252 if k >= 0 else 0.0
    return rf


def load_cohort_b():
    dates, au, ag, pt = [], [], [], []
    with open(os.path.join(D74, "GOLD_CLAUDE_R74_STAKTRAKR_METALS_DAILY.csv")) as fh:
        for r in csv.DictReader(fh):
            if not (r["xau"] and r["xag"] and r["xpt"]):
                continue
            dates.append(d8(r["d"]))
            au.append(float(r["xau"])); ag.append(float(r["xag"])); pt.append(float(r["xpt"]))
    nd, nv = [], []
    with open(os.path.join(D74, "GOLD_CLAUDE_R74_NASDAQ100_DAILY.csv")) as fh:
        for r in csv.DictReader(fh):
            nd.append(d8(r["d"])); nv.append(float(r["value"]))
    # NASDAQ100 value strictly before the metal date (one extra day of lag)
    ndx = []
    for d in dates:
        k = bisect_left(nd, d) - 1
        ndx.append(nv[k] if k >= 0 else np.nan)
    return dict(name="B_STAKTRAKR", dates=dates, gold=np.array(au),
                preds=[np.array(au), np.array(ag), np.array(pt), np.array(ndx)],
                horizons=(1, 5, 10, 21), first_eval=date(2015, 1, 1), rolling_var=2520)


def load_cohort_a():
    rows = []
    for y in range(2020, 2027):
        with open(os.path.join(ROOT, "data_claude_p1", f"GOLD_CLAUDE_P1_PANEL_{y}.csv")) as fh:
            for r in csv.DictReader(fh):
                p1645 = float(r["p0900"]) * math.exp(float(r["y_day"]) / 1e4)
                rows.append((d8(r["d"]), p1645))
    rows.sort()
    dates = [d for d, _ in rows]
    px = np.array([p for _, p in rows])
    return dict(name="A_EXACT_1645TR", dates=dates, gold=px, preds=[px], horizons=(1, 3, 5),
                first_eval=date(2023, 1, 1), rolling_var=None)


def log_returns(p):
    r = np.full(len(p), np.nan)
    r[1:] = np.diff(np.log(p))
    return r


def modwt_haar_causal(x):
    """Causal Haar MODWT coefficients W1..WJ and smooth VJ at every t, using x[t-L+1..t] only."""
    x = np.nan_to_num(x)
    c = np.concatenate([[0.0], np.cumsum(x)])
    n = len(x)
    out = np.full((n, J + 1), np.nan)
    for t in range(n):
        s = lambda a, b: c[t + 1 - a] - c[t + 1 - b]  # sum of x[t-b+1 .. t-a]
        if t + 1 < 2 ** J:
            continue
        for j in range(1, J + 1):
            half = 2 ** (j - 1)
            out[t, j - 1] = (s(0, half) - s(half, 2 * half)) / 2 ** j
        out[t, J] = s(0, 2 ** J) / 2 ** J
    return out


def raw_feats(x, h):
    x = np.nan_to_num(x)
    n = len(x)
    c = np.concatenate([[0.0], np.cumsum(x)])
    out = np.full((n, 7), np.nan)
    for t in range(21, n):
        out[t, :5] = x[t - 4:t + 1][::-1]
        out[t, 5] = c[t + 1] - c[t + 1 - h]
        out[t, 6] = c[t + 1] - c[t + 1 - 21]
    return out


def ewma_var(r):
    v = np.full(len(r), np.nan)
    rr = np.nan_to_num(r)
    v[20] = np.var(rr[1:21])
    for t in range(21, len(r)):
        v[t] = LAMBDA * v[t - 1] + (1 - LAMBDA) * rr[t] ** 2
    return v


def svr_fit_predict(X, y, xq):
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    ym, ys = y.mean(), y.std() or 1.0
    m = SVR(kernel="rbf", C=3.0, epsilon=0.1, gamma=1.0 / X.shape[1])
    m.fit((X - mu) / sd, (y - ym) / ys)
    return float(m.predict(((xq - mu) / sd).reshape(1, -1))[0] * ys + ym)


def run_task(args):
    cohort_name, h = args
    co = load_cohort_b() if cohort_name.startswith("B") else load_cohort_a()
    rf = load_rf()
    dates, gold = co["dates"], co["gold"]
    n = len(dates)
    rg = log_returns(gold)
    rfd = np.array([rf(d) for d in dates])
    exd = rg - rfd  # daily excess log return
    wav = np.hstack([modwt_haar_causal(log_returns(p)) for p in co["preds"]])
    raw = np.hstack([raw_feats(log_returns(p), h) for p in co["preds"]])
    ev = ewma_var(exd)
    decisions = list(range(2 ** J + 21, n - h, h))
    # targets: excess log return over (t, t+h]
    tgt = {t: float(np.log(gold[t + h] / gold[t]) - rfd[t + 1:t + h + 1].sum()) for t in decisions}
    simple_ex = {t: float(gold[t + h] / gold[t] - 1 - rfd[t + 1:t + h + 1].sum()) for t in decisions}
    rows = []
    for t in decisions:
        if dates[t] < co["first_eval"]:
            continue
        past = [s for s in decisions if s + h <= t]
        if len(past) < MIN_BLOCKS:
            continue
        past = past[-CAP:]
        yb = np.array([tgt[s] for s in past])
        hm = float(np.mean([tgt[s] for s in decisions if s + h <= t]))
        Xw = wav[past]
        Xr = raw[past]
        ok_w = ~np.isnan(Xw).any(1)
        ok_r = ~np.isnan(Xr).any(1)
        if np.isnan(wav[t]).any() or np.isnan(raw[t]).any() or ok_w.sum() < MIN_BLOCKS:
            continue
        f_dwt = svr_fit_predict(Xw[ok_w], yb[ok_w], wav[t])
        f_raw = svr_fit_predict(Xr[ok_r], yb[ok_r], raw[t])
        lo = 1 if co["rolling_var"] is None else max(1, t + 1 - co["rolling_var"])
        var_paper = float(np.nanvar(exd[lo:t + 1])) * h
        var_ewma = float(ev[t]) * h
        rows.append(dict(cohort=co["name"], h=h, d=dates[t].isoformat(), year=dates[t].year, y=tgt[t],
                         ex_simple=simple_ex[t], rf_h=float(rfd[t + 1:t + h + 1].sum()),
                         f_hm=hm, f_dwt=f_dwt, f_raw=f_raw, var_paper=var_paper, var_ewma=var_ewma))
    return rows


def weights(rows):
    clip = lambda w: float(min(max(w, CLIP[0]), CLIP[1]))
    for r in rows:
        r["w"] = {"S0_HM_PAPER": clip(r["f_hm"] / (GAMMA * r["var_paper"])),
                  "S1_DWTSVR_PAPER": clip(r["f_dwt"] / (GAMMA * r["var_paper"])),
                  "S2_SVRRAW_PAPER": clip(r["f_raw"] / (GAMMA * r["var_paper"])),
                  "S3_VOLTIMING": clip(r["f_hm"] / (GAMMA * r["var_ewma"])),
                  "S4_DWTSVR_EWMA": clip(r["f_dwt"] / (GAMMA * r["var_ewma"])),
                  "S5_BUYHOLD": 1.0}


def port_series(rows, s, cost_bp):
    out, prev = [], 0.0
    for r in rows:
        w = r["w"][s]
        out.append(w * r["ex_simple"] - cost_bp / 1e4 * abs(w - prev))
        prev = w
    return np.array(out)


def cer(p, h):
    return float((p.mean() - 0.5 * GAMMA * p.var()) * 252 / h * 100)


def evaluate(rows, h, rng):
    if len(rows) < 6:
        return {"n": len(rows), "status": "insufficient"}
    y = np.array([r["y"] for r in rows])
    res = {"n": len(rows), "first": rows[0]["d"], "last": rows[-1]["d"]}
    for name, key in (("DWTSVR", "f_dwt"), ("SVRRAW", "f_raw")):
        f = np.array([r[key] for r in rows])
        b = np.array([r["f_hm"] for r in rows])
        res[f"r2os_{name}"] = float(100 * (1 - ((y - f) ** 2).sum() / ((y - b) ** 2).sum()))
        cw = (y - b) ** 2 - ((y - f) ** 2 - (b - f) ** 2)
        t = cw.mean() / (cw.std(ddof=1) / math.sqrt(len(cw))) if cw.std() > 0 else 0.0
        res[f"cw_p_{name}"] = float(1 - stats.norm.cdf(t))
        res[f"diracc_{name}"] = float(np.mean(np.sign(f) == np.sign(y)))
    res["diracc_alwaysUP"] = float(np.mean(y > 0))
    for c in COSTS_BP:
        blk = {}
        for s in STRATS:
            p = port_series(rows, s, c)
            wealth = np.cumprod(1 + p + np.array([r["rf_h"] for r in rows]))
            peak = np.maximum.accumulate(wealth)
            turnover = float(np.mean(np.abs(np.diff([0.0] + [r["w"][s] for r in rows]))))
            blk[s] = dict(cer=cer(p, h), sharpe=float(p.mean() / p.std() * math.sqrt(252 / h)) if p.std() > 0 else 0.0,
                          tw=float(wealth[-1]), maxdd=float((wealth / peak - 1).min()), turnover=turnover,
                          mean_w=float(np.mean([r["w"][s] for r in rows])))
        res[f"cost_{c}bp"] = blk
    # bootstrap one-sided p for dCER at 5 bp: S3 vs S0, S4 vs S3, S1 vs S0
    def boot(sa, sb):
        pa, pb = port_series(rows, sa, 5), port_series(rows, sb, 5)
        n, bl = len(pa), 6
        if n < 2 * bl:
            return None, None
        obs = cer(pa, h) - cer(pb, h)
        starts = np.arange(n - bl + 1)
        k = int(math.ceil(n / bl))
        draws = []
        for _ in range(5000):
            idx = np.concatenate([np.arange(s, s + bl) for s in rng.choice(starts, k)])[:n]
            draws.append(cer(pa[idx], h) - cer(pb[idx], h))
        return float(obs), float(np.mean(np.array(draws) <= 0))
    for a, b in (("S3_VOLTIMING", "S0_HM_PAPER"), ("S4_DWTSVR_EWMA", "S3_VOLTIMING"), ("S1_DWTSVR_PAPER", "S0_HM_PAPER")):
        d, p = boot(a, b)
        res[f"dCER5_{a}_vs_{b}"] = dict(dcer=d, p_boot=p)
    # break-even one-way cost for S3 vs S0 and S4 vs S0
    for a in ("S3_VOLTIMING", "S4_DWTSVR_EWMA", "S1_DWTSVR_PAPER"):
        f = lambda c: cer(port_series(rows, a, c), h) - cer(port_series(rows, "S0_HM_PAPER", c), h)
        if f(0) <= 0:
            res[f"breakeven_bp_{a}"] = 0.0
        else:
            lo_, hi_ = 0.0, 500.0
            if f(hi_) > 0:
                res[f"breakeven_bp_{a}"] = ">500"
            else:
                for _ in range(40):
                    mid = (lo_ + hi_) / 2
                    lo_, hi_ = (mid, hi_) if f(mid) > 0 else (lo_, mid)
                res[f"breakeven_bp_{a}"] = round((lo_ + hi_) / 2, 2)
    return res


def periods(cohort):
    if cohort.startswith("B"):
        return {"2015_2022": (2015, 2022), "DEV_2023_2024": (2023, 2024), "OPENED_2025_2026": (2025, 2026),
                "PRIMARY_2015_2024": (2015, 2024)}
    return {"DEV_2023": (2023, 2023), "DEV_2024": (2024, 2024), "PRIMARY_DEV_2023_2024": (2023, 2024),
            "OPENED_2025": (2025, 2025), "OPENED_2026_SEPARATE_SOURCE": (2026, 2026)}


def main():
    tasks = [("B", h) for h in (1, 5, 10, 21)] + [("A", h) for h in (1, 3, 5)]
    with Pool(4) as pool:
        results = pool.map(run_task, tasks)
    rng = np.random.default_rng(20261013)
    summary = {"prereg_commit": "3d3240d3d5c012325595178adf7d4f6ec3e5dbec", "results": {}}
    all_rows, primary_p = [], {}
    for rows in results:
        if not rows:
            continue
        co, h = rows[0]["cohort"], rows[0]["h"]
        weights(rows)
        key = f"{co}_h{h}"
        summary["results"][key] = {}
        for pname, (y0, y1) in periods(co).items():
            sub = [r for r in rows if y0 <= r["year"] <= y1]
            summary["results"][key][pname] = evaluate(sub, h, rng)
        prim = summary["results"][key]["PRIMARY_2015_2024" if co.startswith("B") else "PRIMARY_DEV_2023_2024"]
        if "status" not in prim:
            primary_p[f"{key}:H1"] = prim["cw_p_DWTSVR"]
            primary_p[f"{key}:H2"] = prim["dCER5_S3_VOLTIMING_vs_S0_HM_PAPER"]["p_boot"]
            primary_p[f"{key}:H3"] = prim["dCER5_S4_DWTSVR_EWMA_vs_S3_VOLTIMING"]["p_boot"]
        for r in rows:
            all_rows.append({k: v for k, v in r.items() if k != "w"} | {f"w_{s}": r["w"][s] for s in STRATS})
    items = sorted((k, v) for k, v in primary_p.items() if v is not None)
    items.sort(key=lambda kv: kv[1])
    adj, run = {}, 0.0
    for i, (k, v) in enumerate(items):
        run = max(run, min(1.0, (len(items) - i) * v))
        adj[k] = run
    gate = {}
    for k, p in adj.items():
        key, hyp = k.split(":")
        res = summary["results"][key]
        subs = ["2015_2022", "DEV_2023_2024"] if key.startswith("B") else ["DEV_2023", "DEV_2024"]
        opened = ["OPENED_2025_2026"] if key.startswith("B") else ["OPENED_2025", "OPENED_2026_SEPARATE_SOURCE"]

        def eff(block):
            if "status" in block:
                return None
            if hyp == "H1":
                return block["r2os_DWTSVR"]
            if hyp == "H2":
                return block["dCER5_S3_VOLTIMING_vs_S0_HM_PAPER"]["dcer"]
            return block["dCER5_S4_DWTSVR_EWMA_vs_S3_VOLTIMING"]["dcer"]
        signs = [eff(res[s]) for s in subs]
        gate[k] = dict(holm_p=p, sub_period_effects=signs, opened_effects=[eff(res[o]) for o in opened],
                       SUPPORTED=bool(p < 0.05 and all(e is not None and e > 0 for e in signs)))
    summary["gate"] = gate
    with open(OUT + "SUMMARY.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    with open(OUT + "PERIOD_ROWS.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        for r in all_rows:
            w.writerow({k: (round(v, 8) if isinstance(v, float) else v) for k, v in r.items()})
    print(json.dumps(gate, indent=1))


if __name__ == "__main__":
    main()
