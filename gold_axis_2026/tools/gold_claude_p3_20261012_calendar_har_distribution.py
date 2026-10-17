#!/usr/bin/env python3
"""CLAUDE P3 — macro-calendar HAR-RV and conditional return/price distribution (frozen by
GOLD_CLAUDE_P3_20261012_CALENDAR_HAR_DISTRIBUTION_PREREG.md, commit f4cb7a6b).

Inputs : GOLD_H3A_20261012_SESSION_RV_<2020..2025>.csv (PR #91, unchanged),
         data_claude_p3/GOLD_CLAUDE_P3_SESSION_RV_2026_DAY.csv, data_claude_p3/GOLD_CLAUDE_P3_MACRO_CALENDAR.csv,
         data_claude_p1/GOLD_CLAUDE_P1_PANEL_<year>.csv, GOLD_H3A_20261012_FIXED_HAR_SCORE_ROWS.csv
Outputs: GOLD_CLAUDE_P3_20261012_{SCORE_ROWS.csv,SUMMARY.json}
"""
import csv
import json
import math
import os
from datetime import datetime

import numpy as np
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "GOLD_CLAUDE_P3_20261012_")
DEV = (2023, 2024)
YEARS = (2023, 2024, 2025, 2026)
TAUS = (0.05, 0.25, 0.50, 0.75, 0.95)
SIG_MODELS = ("HARXE", "HARX", "PERSIST5", "UNCOND")


def load_rv():
    rows = []
    for y in range(2020, 2026):
        with open(os.path.join(ROOT, f"GOLD_H3A_20261012_SESSION_RV_{y}.csv")) as fh:
            for r in csv.DictReader(fh):
                rows.append((r["decision_date"], r["session"], float(r["rv"])))
    with open(os.path.join(ROOT, "data_claude_p3", "GOLD_CLAUDE_P3_SESSION_RV_2026_DAY.csv")) as fh:
        for r in csv.DictReader(fh):
            rows.append((r["decision_date"], r["session"], float(r["rv"])))
    return rows


def load_calendar():
    cal = {"DAY": set(), "OVN": set()}
    with open(os.path.join(ROOT, "data_claude_p3", "GOLD_CLAUDE_P3_MACRO_CALENDAR.csv")) as fh:
        for r in csv.DictReader(fh):
            d = r["ny_local"][:10]
            if r["event"] in ("NFP", "CPI"):
                cal["DAY"].add(d)  # 08:30 ET = 15:30/16:30 TR, inside DAY 09:00-16:45 of the same date
            else:
                cal["OVN"].add(d)  # 14:00 ET = 21:00/22:00 TR, inside OVN starting 16:45 of the same date
    return cal


def load_returns():
    ret = {"DAY": {}, "OVN": {}}
    for y in range(2020, 2027):
        with open(os.path.join(ROOT, "data_claude_p1", f"GOLD_CLAUDE_P1_PANEL_{y}.csv")) as fh:
            for r in csv.DictReader(fh):
                d = datetime.strptime(r["d"], "%Y%m%d").date().isoformat()
                p0900 = float(r["p0900"])
                if r["day_ok"] == "1" and r["y_day"]:
                    ret["DAY"][d] = (float(r["y_day"]), p0900)
                if r["ovn_ok"] == "1" and r["y_ovn"]:
                    ret["OVN"][d] = (float(r["y_ovn"]), p0900 * math.exp(float(r["y_day"]) / 1e4))
    return ret


def ridge(X, y, alpha=10.0):
    xm, sd = X.mean(0), X.std(0)
    sd[sd < 1e-14] = 1.0
    Z = (X - xm) / sd
    ym = y.mean()
    beta = np.linalg.solve(Z.T @ Z + alpha * np.eye(Z.shape[1]), Z.T @ (y - ym))
    return lambda x: float(ym + ((np.asarray(x) - xm) / sd) @ beta)


def qlike(rv, f):
    r = rv / f
    return r - math.log(r) - 1


def nw_dm(d, lags=5):
    d = np.asarray(d, float)
    n = len(d)
    e = d - d.mean()
    v = e @ e / n
    for k in range(1, lags + 1):
        v += 2 * (1 - k / (lags + 1)) * (e[k:] @ e[:-k]) / n
    t = d.mean() / math.sqrt(max(v, 1e-18) / n)
    return float(t), float(1 - stats.norm.cdf(t))


def block_ci(d, rng, block, reps=2000):
    d = np.asarray(d, float)
    n = len(d)
    if n < 2 * block:
        return None
    starts = np.arange(n - block + 1)
    nb = int(math.ceil(n / block))
    s = [d[np.concatenate([np.arange(a, a + block) for a in rng.choice(starts, nb)])[:n]].mean() for _ in range(reps)]
    return [float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))]


def crps_gauss(y, mu, s):
    z = (y - mu) / s
    return s * (z * (2 * stats.norm.cdf(z) - 1) + 2 * stats.norm.pdf(z) - 1 / math.sqrt(math.pi))


def main():
    rng = np.random.default_rng(20261012)
    rv_rows, cal, ret = load_rv(), load_calendar(), load_returns()
    h3a = {}
    with open(os.path.join(ROOT, "GOLD_H3A_20261012_FIXED_HAR_SCORE_ROWS.csv")) as fh:
        for r in csv.DictReader(fh):
            h3a[(r["decision_date"], r["session"])] = float(r["HAR_log"])
    summary = {"prereg_commit": "f4cb7a6bf2bfdf4e8a89174521ee752b0a238d6d", "targets": {}}
    score_rows, dm_p = [], {}
    for T in ("DAY", "OVN"):
        hist = sorted([r for r in rv_rows if r[1] == T], key=lambda r: r[0])
        feat = []
        for i in range(60, len(hist)):
            prev = np.log([v[2] for v in hist[:i]])
            d = hist[i][0]
            feat.append(dict(d=d, year=int(d[:4]), rv=hist[i][2], y=math.log(hist[i][2]),
                             x=[prev[-1], prev[-5:].mean(), prev[-22:].mean()], e=1.0 if d in cal[T] else 0.0,
                             p5=prev[-5:].mean(), clim=prev[-60:].mean()))
        scored = []
        for i, r in enumerate(feat):
            if r["year"] < 2023:
                continue
            prior = feat[:i]
            X = np.array([p["x"] for p in prior])
            yv = np.array([p["y"] for p in prior])
            fx = ridge(X, yv)(r["x"])
            fxe = ridge(np.column_stack([X, [p["e"] for p in prior]]), yv)(r["x"] + [r["e"]])
            logs = {"HARXE": fxe, "HARX": fx, "PERSIST5": r["p5"], "CLIM60": r["clim"]}
            if (r["d"], T) in h3a:
                logs["H3A_LOCKED"] = h3a[(r["d"], T)]
            scored.append(dict(r, logs=logs, q={k: qlike(r["rv"], math.exp(v)) for k, v in logs.items()},
                               lmse={k: (r["y"] - v) ** 2 for k, v in logs.items()}))
        # parity: HAR-X must equal H3A HAR in DEV (identical construction)
        par = [abs(s["logs"]["HARX"] - s["logs"]["H3A_LOCKED"]) for s in scored if s["year"] in DEV and "H3A_LOCKED" in s["logs"]]
        tsum = {"parity_HARX_vs_H3A_DEV": dict(n=len(par), max_abs_diff=float(max(par)) if par else None)}
        for yr in YEARS:
            blk = [s for s in scored if s["year"] == yr]
            if not blk:
                tsum[str(yr)] = {"status": "BLOCKED: 0 eligible windows"}
                continue
            res = {"n": len(blk), "n_event": int(sum(s["e"] for s in blk))}
            for k in ("HARXE", "HARX", "PERSIST5", "CLIM60"):
                res[k] = dict(qlike=float(np.mean([s["q"][k] for s in blk])), logmse=float(np.mean([s["lmse"][k] for s in blk])))
            inc = [s["q"]["HARX"] - s["q"]["HARXE"] for s in blk]
            res["event_increment_qlike"] = float(np.mean(inc))
            res["event_increment_ci95"] = block_ci(inc, rng, max(5, round(len(blk) / 4)))
            res["event_increment_on_event_windows"] = float(np.mean([v for v, s in zip(inc, blk) if s["e"]])) if res["n_event"] else None
            for b in ("PERSIST5", "CLIM60"):
                g = [s["q"][b] - s["q"]["HARXE"] for s in blk]
                res[f"HARXE_gain_vs_{b}"] = float(np.mean(g))
                res[f"HARXE_gain_vs_{b}_ci95"] = block_ci(g, rng, max(5, round(len(blk) / 4)))
            h = [s for s in blk if "H3A_LOCKED" in s["logs"]]
            if h:
                res["H3A_LOCKED_matched"] = dict(n=len(h), qlike=float(np.mean([s["q"]["H3A_LOCKED"] for s in h])),
                                                 HARXE_qlike=float(np.mean([s["q"]["HARXE"] for s in h])))
            tsum[str(yr)] = res
        dev = [s for s in scored if s["year"] in DEV]
        t, p = nw_dm([s["q"]["HARX"] - s["q"]["HARXE"] for s in dev])
        tsum["DEV_event_increment_DM"] = dict(n=len(dev), mean=float(np.mean([s["q"]["HARX"] - s["q"]["HARXE"] for s in dev])), t=t, p=p)
        dm_p[T] = p
        # ---- distribution (secondary)
        ret_hist = sorted(ret[T].items())
        rv_map = {s["d"]: s["rv"] for s in feat}
        dist_rows = []
        for s in scored:
            if s["d"] not in ret[T]:
                continue
            y, origin = ret[T][s["d"]]
            prior_ret = [v[0] for d_, v in ret_hist if d_ < s["d"]]
            pairs = [(v[0], rv_map[d_]) for d_, v in ret_hist if d_ < s["d"] and d_ in rv_map]
            mu = float(np.mean(prior_ret))
            k_scale = sum(a * a for a, _ in pairs) / (sum(b for _, b in pairs) * 1e8)  # (bp^2)/(log^2*1e8)
            sig = {m: math.sqrt(k_scale * math.exp(s["logs"][m]) * 1e8) for m in ("HARXE", "HARX", "PERSIST5")}
            sig["UNCOND"] = float(np.std(prior_ret, ddof=1))
            row = dict(target=T, d=s["d"], year=s["year"], e=s["e"], y_bp=y, mu_bp=mu, origin=origin, rv=s["rv"],
                       k_scale=k_scale, **{f"logF_{m}": s["logs"][m] for m in s["logs"]}, **{f"sigma_{m}": v for m, v in sig.items()})
            for m, sg in sig.items():
                row[f"crps_{m}"] = crps_gauss(y, mu, sg)
                row[f"pinball_{m}"] = float(np.mean([max(tau * (y - (mu + sg * stats.norm.ppf(tau))),
                                                         (tau - 1) * (y - (mu + sg * stats.norm.ppf(tau)))) for tau in TAUS]))
                lo, hi = mu - 1.645 * sg, mu + 1.645 * sg
                row[f"cover90_{m}"] = int(lo <= y <= hi)
                row[f"width90_bp_{m}"] = hi - lo
                row[f"width90_usd_{m}"] = origin * (math.exp(hi / 1e4) - math.exp(lo / 1e4))
            dist_rows.append(row)
        score_rows.extend(dist_rows)
        dsum = {}
        for yr in YEARS:
            blk = [r for r in dist_rows if r["year"] == yr]
            if not blk:
                continue
            res = {"n": len(blk)}
            for m in SIG_MODELS:
                res[m] = dict(crps_bp=float(np.mean([r[f"crps_{m}"] for r in blk])),
                              pinball_bp=float(np.mean([r[f"pinball_{m}"] for r in blk])),
                              cover90=float(np.mean([r[f"cover90_{m}"] for r in blk])),
                              width90_bp=float(np.mean([r[f"width90_bp_{m}"] for r in blk])),
                              width90_usd=float(np.mean([r[f"width90_usd_{m}"] for r in blk])))
            for b in ("UNCOND", "PERSIST5", "HARX"):
                tt, pp = nw_dm([r[f"crps_{b}"] - r["crps_HARXE"] for r in blk])
                res[f"crps_gain_HARXE_vs_{b}"] = dict(mean=float(np.mean([r[f"crps_{b}"] - r["crps_HARXE"] for r in blk])), t=tt, p=pp)
            dsum[str(yr)] = res
        tsum["distribution"] = dsum
        summary["targets"][T] = tsum
    # Holm over 2 primary tests
    items = sorted(dm_p.items(), key=lambda kv: kv[1])
    adj, run = {}, 0.0
    for i, (k, v) in enumerate(items):
        run = max(run, min(1.0, (len(items) - i) * v))
        adj[k] = run
    gate = {}
    for T in ("DAY", "OVN"):
        ts = summary["targets"][T]
        beats = all(ts[str(y)]["HARXE"]["qlike"] < min(ts[str(y)]["PERSIST5"]["qlike"], ts[str(y)]["CLIM60"]["qlike"]) for y in DEV)
        no_rev = ts["2025"]["event_increment_qlike"] > 0
        gate[T] = dict(holm_p=adj[T], holm_pass=adj[T] < 0.05, HARXE_beats_PERSIST5_CLIM60_each_DEV_year=beats,
                       no_2025_reversal=no_rev, SUPPORTED_RV_ONLY=bool(adj[T] < 0.05 and beats and no_rev))
    summary["gate"] = gate
    summary["P3_VERDICT"] = {T: ("SUPPORTED_RV_ONLY" if g["SUPPORTED_RV_ONLY"] else "REJECT") for T, g in gate.items()}
    with open(OUT + "SCORE_ROWS.csv", "w", newline="") as fh:
        keys = sorted({k for r in score_rows for k in r})
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in score_rows:
            w.writerow({k: (round(v, 8) if isinstance(v, float) else v) for k, v in r.items()})
    with open(OUT + "SUMMARY.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps({"verdict": summary["P3_VERDICT"], "gate": gate}, indent=1))


if __name__ == "__main__":
    main()
