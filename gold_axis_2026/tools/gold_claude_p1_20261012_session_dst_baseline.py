#!/usr/bin/env python3
"""CLAUDE P1 — session / US-DST conditional baselines (frozen by
GOLD_CLAUDE_P1_20261012_SESSION_DST_BASELINE_PREREG.md, commit 7c926e21).

Inputs : gold_axis_2026/data_claude_p1/GOLD_CLAUDE_P1_PANEL_<year>.csv (from
         sql/gold_claude_p1_20261012_session_panel.sql, read-only Neon, checksum-verified)
Outputs: gold_axis_2026/GOLD_CLAUDE_P1_20261012_{SCORE_ROWS.csv,SUMMARY.json,BASELINE_ATLAS.csv}
"""
import csv
import json
import math
import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data_claude_p1")
OUT = os.path.join(ROOT, "GOLD_CLAUDE_P1_20261012_")
YEARS = range(2020, 2027)
DEV = (2023, 2024)
REPORT_YEARS = (2023, 2024, 2025, 2026)
MIN_TRAIN = 250
ALPHA = 10.0
SHRINK_K = 100.0
SEED = 20261012
NY = ZoneInfo("America/New_York")
MODELS = ["RW", "INT", "M1", "M2", "M3"]
CANDIDATES = ["M1", "M2", "M3"]


def fnum(v):
    return float(v) if v not in ("", None) else None


def load():
    rows = []
    for y in YEARS:
        with open(os.path.join(DATA, f"GOLD_CLAUDE_P1_PANEL_{y}.csv")) as fh:
            for r in csv.DictReader(fh):
                d = datetime.strptime(r["d"], "%Y%m%d").date()
                noon = datetime(d.year, d.month, d.day, 12, tzinfo=NY)
                rows.append(dict(
                    d=d, year=d.year, wd=int(r["wd"]), day_ok=r["day_ok"] == "1", ovn_ok=r["ovn_ok"] == "1",
                    p0900=float(r["p0900"]), y_day=fnum(r["y_day"]), y_ovn=fnum(r["y_ovn"]),
                    f_us=fnum(r["f_us"]), f_asia=fnum(r["f_asia"]), g=fnum(r["g_daysofar"]),
                    dst=1 if noon.dst() != timedelta(0) else 0,
                    source="DUKASCOPY_DIRECT_2026" if d.year == 2026 else "EVTRADINGLABS_DUKASCOPY_2020_2025",
                ))
    rows.sort(key=lambda r: r["d"])
    return rows


def build_targets(rows):
    """Return per-target lists of observation dicts with frozen pre-issue features."""
    day, ovn = [], []
    last_ovn = None  # (date, y) most recent eligible OVN
    for i, r in enumerate(rows):
        prev = rows[i - 1] if i > 0 else None
        # DAY: decision 08:45 on d
        if r["day_ok"] and r["y_day"] is not None:
            prevday = prev["y_day"] if (prev and prev["day_ok"] and prev["y_day"] is not None) else 0.0
            feats = None
            if r["f_us"] is not None and r["f_asia"] is not None:
                feats = [r["f_us"], r["f_asia"], prevday]
            day.append(dict(d=r["d"], year=r["year"], wd=r["wd"], dst=r["dst"], y=r["y_day"], x=feats,
                            origin=r["p0900"], source=r["source"]))
        # OVN: decision 16:30 on d; previous eligible OVN must have ended by 09:00 on d
        if r["ovn_ok"] and r["y_ovn"] is not None:
            pov = last_ovn[1] if (last_ovn and (r["d"] - last_ovn[0]).days <= 7) else 0.0
            feats = [r["g"], pov] if r["g"] is not None else None
            origin = r["p0900"] * math.exp(r["y_day"] / 1e4)  # P(16:45)
            ovn.append(dict(d=r["d"], year=r["year"], wd=r["wd"], dst=r["dst"], y=r["y_ovn"], x=feats,
                            origin=origin, source=r["source"]))
        if r["ovn_ok"] and r["y_ovn"] is not None:
            last_ovn = (r["d"], r["y_ovn"])
    return {"DAY": day, "OVN": ovn}


def ridge_fit_predict(X, y, xq):
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Z = (X - mu) / sd
    yc = y - y.mean()
    beta = np.linalg.solve(Z.T @ Z + ALPHA * np.eye(Z.shape[1]), Z.T @ yc)
    return float(y.mean() + ((np.asarray(xq) - mu) / sd) @ beta)


def m3_design(x, dst):
    return list(x) + [dst] + [v * dst for v in x]


def forecast(obs):
    """Expanding daily re-estimation; train on rows with decision date < current date."""
    out = []
    for j, o in enumerate(obs):
        train = obs[:j]
        if len(train) < MIN_TRAIN:
            continue
        ys = np.array([t["y"] for t in train])
        m_all = ys.mean()
        cell = [t["y"] for t in train if t["dst"] == o["dst"] and t["wd"] == o["wd"]]
        n_c = len(cell)
        m1 = m_all + (n_c / (n_c + SHRINK_K)) * ((np.mean(cell) if n_c else m_all) - m_all)
        pred = {"RW": 0.0, "INT": float(m_all), "M1": float(m1), "M2": None, "M3": None}
        tr_x = [t for t in train if t["x"] is not None]
        if o["x"] is not None and len(tr_x) >= MIN_TRAIN:
            X = np.array([t["x"] for t in tr_x])
            yx = np.array([t["y"] for t in tr_x])
            pred["M2"] = ridge_fit_predict(X, yx, o["x"])
            X3 = np.array([m3_design(t["x"], t["dst"]) for t in tr_x])
            pred["M3"] = ridge_fit_predict(X3, yx, m3_design(o["x"], o["dst"]))
        out.append(dict(o, pred=pred, sigma=float(ys.std()), prior_up=float((ys > 0).mean())))
    return out


def norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def nw_dm(diff, lags=5):
    """One-sided DM: H1 mean(diff) > 0, Newey-West variance."""
    d = np.asarray(diff, float)
    n = len(d)
    if n < 10:
        return None, None
    m = d.mean()
    e = d - m
    v = e @ e / n
    for k in range(1, lags + 1):
        w = 1 - k / (lags + 1)
        v += 2 * w * (e[k:] @ e[:-k]) / n
    se = math.sqrt(max(v, 1e-18) / n)
    t = m / se
    return float(t), float(1 - norm_cdf(t))


def block_ci(diff, block, reps=2000, rng=None):
    d = np.asarray(diff, float)
    n = len(d)
    if n < 2 * block:
        return None
    starts = np.arange(n - block + 1)
    nb = int(math.ceil(n / block))
    stats = []
    for _ in range(reps):
        idx = np.concatenate([np.arange(s, s + block) for s in rng.choice(starts, nb)])[:n]
        stats.append(d[idx].mean())
    return [float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))]


def direction_metrics(y, yhat):
    y, yhat = np.asarray(y), np.asarray(yhat)
    keep = y != 0
    y, yhat = y[keep], yhat[keep]
    up, pu = y > 0, yhat >= 0
    rec_up = float((pu & up).sum() / max(up.sum(), 1))
    rec_dn = float((~pu & ~up).sum() / max((~up).sum(), 1))
    return dict(n_dir=int(len(y)), acc=float((pu == up).mean()), ba=(rec_up + rec_dn) / 2,
                recall_up=rec_up, recall_down=rec_dn, n_up=int(up.sum()), n_down=int((~up).sum()))


def logloss(y, p):
    y, p = np.asarray(y), np.clip(np.asarray(p), 1e-6, 1 - 1e-6)
    keep = y != 0
    up = (y[keep] > 0).astype(float)
    return float(-(up * np.log(p[keep]) + (1 - up) * np.log(1 - p[keep])).mean())


def wilson(k, n):
    if n == 0:
        return [None, None]
    z, ph = 1.96, k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [c - h, c + h]


def exact_mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def score_block(rows, models, rng, block):
    res = {"n": len(rows)}
    y = np.array([r["y"] for r in rows])
    for m in models:
        yh = np.array([r["pred"][m] for r in rows])
        e = y - yh
        actual = np.array([r["origin"] * math.exp(r["y"] / 1e4) for r in rows])
        fc = np.array([r["origin"] * math.exp(r["pred"][m] / 1e4) for r in rows])
        p = np.array([norm_cdf(r["pred"][m] / r["sigma"]) if r["sigma"] > 0 else 0.5 for r in rows])
        res[m] = dict(mse_bp2=float((e ** 2).mean()), mae_bp=float(np.abs(e).mean()),
                      price_mae_usd=float(np.abs(actual - fc).mean()),
                      price_rmse_usd=float(np.sqrt(((actual - fc) ** 2).mean())),
                      logloss=logloss(y, p), **direction_metrics(y, yh))
    res["PRIOR_logloss"] = logloss(y, np.array([r["prior_up"] for r in rows]))
    res["ALWAYS_UP"] = direction_metrics(y, np.zeros(len(y)))
    for m in models:
        if m in ("RW", "INT"):
            continue
        for b in ("RW", "INT"):
            diff = (y - np.array([r["pred"][b] for r in rows])) ** 2 - (y - np.array([r["pred"][m] for r in rows])) ** 2
            res[m][f"r2_os_vs_{b}"] = float(1 - res[m]["mse_bp2"] / res[b]["mse_bp2"])
            res[m][f"mse_gain_vs_{b}_ci95"] = block_ci(diff, block, rng=rng)
    return res


def holm(pvals):
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    adj, running = {}, 0.0
    m = len(items)
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        adj[k] = running
    return adj


def load_r67():
    path = os.path.join(ROOT, "GOLD_R67_20261012_H3_AS_DAY_AND_OVN_CONDITIONER_2023_2026_ROWS.csv")
    out = {}
    with open(path) as fh:
        for r in csv.DictReader(fh):
            out[(r["clock"], r["day"])] = (int(r["new_pred"]), int(r["h3bit"]))
    return out


def main():
    rng = np.random.default_rng(SEED)
    rows = load()
    targets = build_targets(rows)
    summary = {"prereg_commit": "7c926e21e0efdf82919556132c84fe87be8d138c", "targets": {}, "gate": {}}
    score_rows, dm_p = [], {}
    r67 = load_r67()
    for tgt, obs in targets.items():
        fc = forecast(obs)
        for f in fc:
            score_rows.append(dict(target=tgt, d=f["d"].isoformat(), year=f["year"], source=f["source"], dst=f["dst"],
                                   wd=f["wd"], y_bp=f["y"], origin_usd=round(f["origin"], 2),
                                   **{f"pred_{m}": (None if f["pred"][m] is None else round(f["pred"][m], 4)) for m in MODELS}))
        tsum = {}
        for yr in REPORT_YEARS:
            yr_rows = [f for f in fc if f["year"] == yr]
            if not yr_rows:
                tsum[str(yr)] = {"status": "BLOCKED: 0 eligible windows under frozen rule"}
                continue
            block = max(5, round(len(yr_rows) / 4))
            full = [f for f in yr_rows if all(f["pred"][m] is not None for m in MODELS)]
            tsum[str(yr)] = {
                "matched_all_models": score_block(full, MODELS, rng, block) if len(full) >= 20 else {"n": len(full)},
                "calendar_models_all_rows": score_block(yr_rows, ["RW", "INT", "M1"], rng, block),
            }
            # Matched direction vs R67 (secondary)
            mm = {}
            for m in CANDIDATES + ["ALWAYS_UP"]:
                for ref_i, ref in enumerate(("R67_new_pred", "R67_h3bit")):
                    b = c = n = 0
                    for f in full:
                        key = (tgt, f["d"].isoformat())
                        if key not in r67 or f["y"] == 0:
                            continue
                        up = f["y"] > 0
                        mine = True if m == "ALWAYS_UP" else f["pred"][m] >= 0
                        theirs = r67[key][ref_i] == 1
                        n += 1
                        b += int(mine == up and theirs != up)
                        c += int(mine != up and theirs == up)
                    mm[f"{m}_vs_{ref}"] = dict(n=n, corrected=b, broken=c, mcnemar_p=exact_mcnemar(b, c))
            tsum[str(yr)]["matched_direction_vs_R67"] = mm
        # Pooled DEV DM tests (primary)
        dev = [f for f in fc if f["year"] in DEV and all(f["pred"][m] is not None for m in MODELS)]
        y = np.array([f["y"] for f in dev])
        pooled = {"n": len(dev)}
        for m in CANDIDATES:
            for b in ("RW", "INT"):
                diff = (y - np.array([f["pred"][b] for f in dev])) ** 2 - (y - np.array([f["pred"][m] for f in dev])) ** 2
                t, p = nw_dm(diff)
                pooled[f"{m}_vs_{b}"] = dict(mean_mse_gain_bp2=float(diff.mean()), dm_t=t, p_one_sided=p)
                dm_p[f"{tgt}:{m}_vs_{b}"] = p
        tsum["DEV_pooled_2023_2024"] = pooled
        summary["targets"][tgt] = tsum
    adj = holm(dm_p)
    for tgt in targets:
        for m in CANDIDATES:
            yrs_ok = all(
                summary["targets"][tgt][str(yr)]["matched_all_models"][m]["mse_bp2"]
                < min(summary["targets"][tgt][str(yr)]["matched_all_models"][b]["mse_bp2"] for b in ("RW", "INT"))
                for yr in DEV)
            p_ok = all(adj[f"{tgt}:{m}_vs_{b}"] < 0.05 for b in ("RW", "INT"))
            r25 = summary["targets"][tgt]["2025"]["matched_all_models"]
            no_rev = r25[m]["mse_bp2"] < min(r25["RW"]["mse_bp2"], r25["INT"]["mse_bp2"])
            summary["gate"][f"{tgt}:{m}"] = dict(
                beats_RW_and_INT_each_DEV_year=bool(yrs_ok), holm_p_vs_RW=adj[f"{tgt}:{m}_vs_RW"],
                holm_p_vs_INT=adj[f"{tgt}:{m}_vs_INT"], holm_pass=bool(p_ok), no_2025_reversal=bool(no_rev),
                SUPPORTED=bool(yrs_ok and p_ok and no_rev))
    summary["P1_CLASSIFICATION"] = "SUPPORTED_COMPONENT_EXISTS" if any(
        g["SUPPORTED"] for g in summary["gate"].values()) else "BASELINE_ONLY"
    # Baseline atlas (descriptive)
    atlas = []
    seg_defs = [("DAY", "y_day", "day_ok"), ("OVN", "y_ovn", "ovn_ok"), ("PREV_US_SEGMENT", "f_us", None),
                ("ASIA_SEGMENT", "f_asia", None)]
    for yr in YEARS:
        for name, col, ok in seg_defs:
            for dst in (0, 1, "ALL"):
                vals = [r[col] for r in rows if r["year"] == yr and r[col] is not None
                        and (ok is None or r[ok]) and (dst == "ALL" or r["dst"] == dst)]
                if not vals:
                    atlas.append(dict(year=yr, segment=name, us_dst=dst, n=0))
                    continue
                v = np.array(vals)
                k = int((v > 0).sum())
                lo, hi = wilson(k, len(v))
                atlas.append(dict(year=yr, segment=name, us_dst=dst, n=len(v), mean_bp=round(float(v.mean()), 3),
                                  std_bp=round(float(v.std(ddof=1)) if len(v) > 1 else 0.0, 3),
                                  up_rate=round(k / len(v), 4), up_ci95_lo=round(lo, 4), up_ci95_hi=round(hi, 4),
                                  source="DUKASCOPY_DIRECT_2026" if yr == 2026 else "EVTRADINGLABS_DUKASCOPY_2020_2025"))
    with open(OUT + "BASELINE_ATLAS.csv", "w", newline="") as fh:
        keys = ["year", "segment", "us_dst", "n", "mean_bp", "std_bp", "up_rate", "up_ci95_lo", "up_ci95_hi", "source"]
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for a in atlas:
            w.writerow(a)
    with open(OUT + "SCORE_ROWS.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(score_rows[0].keys()))
        w.writeheader()
        w.writerows(score_rows)
    with open(OUT + "SUMMARY.json", "w") as fh:
        json.dump(summary, fh, indent=1, default=str)
    print(json.dumps({"classification": summary["P1_CLASSIFICATION"], "gate": summary["gate"]}, indent=1))


if __name__ == "__main__":
    main()
