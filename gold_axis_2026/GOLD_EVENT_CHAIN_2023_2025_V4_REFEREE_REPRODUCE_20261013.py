"""Referee audit #2 (after PR #118) of GOLD_EVENT_CHAIN V3/V4.

Inputs (all committed): V3 DAILY_VOL_SCALED_CONTROLS, V4 13_TENSION_ONSETS_MATCHED_CONTROLS,
V2 ALL_774_DAYS (intraday range). Optional: a derived cross-metal/equity ratio panel produced by
GOLD_EVENT_CHAIN_2023_2025_V4_REFEREE_RATIOS_20261013.sql on Neon (NOT committed: vendor rights
PRIVATE/NO_PUBLIC_RAW_REDISTRIBUTION). Pass its path as argv[1]; without it, ratio features are skipped.

Writes four CSVs next to this script. Descriptive research only: no model, no signal, no P&L.
"""
import os, sys
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr, fisher_exact

D = os.path.dirname(os.path.abspath(__file__)) + "/"
OUT = D + "GOLD_EVENT_CHAIN_2023_2025_V4_REFEREE_"
d = pd.read_csv(D + "GOLD_EVENT_CHAIN_2023_2025_V3_DAILY_VOL_SCALED_CONTROLS_20261013.csv", parse_dates=["date"]).reset_index(drop=True)
v4 = pd.read_csv(D + "GOLD_EVENT_CHAIN_2023_2025_V4_13_TENSION_ONSETS_MATCHED_CONTROLS_20261013.csv", parse_dates=["risk_cross_date", "control_date"])
v2 = pd.read_csv(D + "GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_ALL_774_DAYS_20261013.csv", parse_dates=["date"])[["date", "intraday_range_pct"]]
d = d.merge(v2, on="date", how="left")
b = lambda s: s.astype(str).eq("True")
d["nd"], d["nu"], d["fc"] = b(d.next_down), b(d.next_up), b(d.future_complete)
n = len(d)
ix = dict(zip(d.date, d.index))

# optional ratio panel: yymmdd,100*ln(XAG/XAU),100*ln(XPT/XAU),100*ln(NEM/XAU),100*ln(SPX)
HAVE_R = len(sys.argv) > 1 and os.path.exists(sys.argv[1])
if HAVE_R:
    R = []
    for t in open(sys.argv[1]).read().strip().split(";"):
        f = t.split(","); R.append([pd.to_datetime("20" + f[0])] + [float(x) if x else np.nan for x in f[1:]])
    r = pd.DataFrame(R, columns=["date", "lsr", "lpr", "lnem_au", "lspx"]).set_index("date")
    r[["lnem_au", "lspx"]] = r[["lnem_au", "lspx"]].ffill(limit=2)
    for c in ["lsr", "lpr", "lnem_au", "lspx"]:
        r["d20_" + c] = r[c] - r[c].shift(20); r["d5_" + c] = r[c] - r[c].shift(5)
    d = d.merge(r.reset_index(), on="date", how="left")

d["sd20"] = d.r1.rolling(20).std(); d["volx"] = d.sd20 / d.sd
d["zr20"] = d.r20 / (d.sd * np.sqrt(20))
d["rng5"] = d.intraday_range_pct.rolling(5).mean(); d["rng5n"] = d.rng5 / d.sd
d["acc"] = d.r5 / d.r20.where(d.r20.abs() > 0.5)
ge = (d.r20 >= 8).values

# ---------- 1. V4 matching audit ----------
risk = [ix[x] for x in v4.risk_cross_date]
ctrl = [ix[x] for x in v4.control_date]
fc_all = ge & ~np.r_[False, ge[:-1]]
print("[1] first crossings (complete):", int((fc_all & d.fc.values).sum()), "| incl. incomplete:", int(fc_all.sum()))
over = [(d.date[a].date(), d.date[c].date()) for k, a in enumerate(sorted(risk)) for c in sorted(risk)[k + 1:] if c - a <= 10]
print("    risk-onset pairs whose 10-session futures overlap:", len(over))
leak = sorted({cd.date() for ci, cd in zip(ctrl, v4.control_date) for ri in risk if ci < ri and ci + 10 >= ri - 20})
print("    V4 controls whose future window overlaps a risk onset's 20-session formation window:", len(leak), leak)
ep_onset = []
for ri in sorted(risk):
    if not ep_onset or ri - ep_onset[-1][-1] > 20: ep_onset.append([ri])
    else: ep_onset[-1].append(ri)
print("    13 onsets fall in", len(ep_onset), "rally episodes (onsets <=20 sessions apart merged)")
rng = np.random.default_rng(0)
for p2 in [0.3, 0.4, 0.5, 0.6]:
    hits = 0
    for _ in range(2000):
        a_, b_ = rng.binomial(13, p2), rng.binomial(13, .1)
        hits += fisher_exact([[a_, 13 - a_], [b_, 13 - b_]], alternative="greater")[1] < .05
    print(f"    power 13 vs 13 (control 10% vs risk {p2:.0%}): {hits / 2000:.2f}")

def outcome(i):
    if i is None: return "NA"
    s = ("DOWN" if d.nd[i] else "") + ("UP" if d.nu[i] else "")
    return s or "NONE"
def rematch(rule):
    used, rows = set(), []
    for ri in risk:
        y = d.date[ri].year; cand = []
        for ci in range(n):
            if d.date[ci].year != y or not d.fc[ci] or ci in used or not d.r20[ci] < 5: continue
            if ge[max(0, ci - 5):ci + 6].any() or abs(ci - ri) <= 10: continue
            if rule != "v4" and ge[ci + 1:min(n, ci + 31)].any(): continue
            if rule == "no_leak_within_60" and abs(ci - ri) > 60: continue
            cand.append(ci)
        c = min(cand, key=lambda ci: abs(d.sd[ci] - d.sd[ri])) if cand else None
        if c is not None: used.add(c)
        rows.append(dict(rule=rule, risk=d.date[ri].date(), control=None if c is None else d.date[c].date(),
                         risk_outcome=outcome(ri), control_outcome=outcome(c),
                         sd_ratio=None if c is None else round(d.sd[c] / d.sd[ri], 2)))
    return pd.DataFrame(rows)
M = pd.concat([rematch(x) for x in ["v4", "no_leak", "no_leak_within_60"]])
for rule, g in M.groupby("rule", sort=False):
    print(f"    {rule:18s} control DOWN {g.control_outcome.str.contains('DOWN').sum()}/13 UP {g.control_outcome.str.contains('UP').sum()}/13"
          f" | risk DOWN {g.risk_outcome.str.contains('DOWN').sum()} UP {g.risk_outcome.str.contains('UP').sum()}")
M.to_csv(OUT + "MATCHING_SENSITIVITY_20261013.csv", index=False)

# ---------- 2. Tension episodes ----------
def episodes(mask, gap=10):
    idx = list(np.where(mask)[0]); E, cur = [], [idx[0]]
    for j in idx[1:]:
        if j - cur[-1] <= gap: cur.append(j)
        else: E.append(cur); cur = [j]
    E.append(cur); return E
rows = []
for name, mask in [("r20>=8%", ge), ("zr20>=2_vol_scaled", (d.zr20 >= 2).values)]:
    for e in episodes(mask):
        s, t = e[0], e[-1]; seg = d.iloc[s:t + 1]; pk = int(seg.price.idxmax())
        post = d.price.iloc[pk + 1:pk + 21]
        row = dict(definition=name, start=d.date[s].date(), end=d.date[t].date(), tension_days=len(e), span_sessions=t - s + 1,
                   peak_date=d.date[pk].date(), gain_20s_before_start_to_peak_pct=round((d.price[pk] / d.price[max(0, s - 20)] - 1) * 100, 1),
                   max_drawdown_20s_after_peak_pct=round((post.min() / d.price[pk] - 1) * 100, 1) if len(post) else np.nan,
                   days_followed_by_next10_down=f"{int(seg.nd.sum())}/{len(seg)}", volx_at_peak=round(d.volx[pk], 2))
        if HAVE_R:
            row.update(silver_vs_gold_20s_at_peak=round(d.d20_lsr[pk], 1), nem_vs_gold_20s_at_peak=round(d.d20_lnem_au[pk], 1), spx_20s_at_peak=round(d.d20_lspx[pk], 1))
        rows.append(row)
EP = pd.DataFrame(rows); EP.to_csv(OUT + "TENSION_EPISODES_20261013.csv", index=False)
e8 = EP[EP.definition == "r20>=8%"]
print("[2] r20>=8% episodes:", len(e8), "| post-peak drawdown <=-3% in", int((e8.max_drawdown_20s_after_peak_pct <= -3).sum()))
print("    Spearman(gain-to-peak, post-peak drawdown):", spearmanr(e8.gain_20s_before_start_to_peak_pct, e8.max_drawdown_20s_after_peak_pct))

# ---------- 3. Direction separators ----------
ep = np.full(n, -1); k = -1; last = -99
for i in np.where(ge)[0]:
    if i - last > 10: k += 1
    ep[i] = k; last = i
d["ep"] = ep; d["dur"] = d.groupby("ep").cumcount() + 1; d.loc[d.ep < 0, "dur"] = 0
F = ["r20", "zr20", "r5", "acc", "volx", "rng5", "rng5n", "dur", "NQ_prevd", "CL_prevd", "ZN_prevd"]
if HAVE_R: F += ["d20_lsr", "d5_lsr", "d20_lpr", "d20_lnem_au", "d5_lnem_au", "d20_lspx"]
def auc(x, y):
    x = np.asarray(x, float); y = np.asarray(y, bool); ok = ~np.isnan(x); x, y = x[ok], y[ok]
    if y.sum() == 0 or (~y).sum() == 0: return np.nan, int(y.sum()), int((~y).sum())
    return mannwhitneyu(x[y], x[~y]).statistic / (y.sum() * (~y).sum()), int(y.sum()), int((~y).sum())
def block_ci(x, y, B=2000, L=20, seed=1):
    g = np.random.default_rng(seed); m = len(x); st = np.arange(0, m - L + 1); out = []
    for _ in range(B):
        idx = np.concatenate([np.arange(s, s + L) for s in g.choice(st, size=m // L + 1)])[:m]
        out.append(auc(x[idx], y[idx])[0])
    return np.nanpercentile(out, [2.5, 97.5])
res = []
t = d[(d.r20 >= 8) & d.fc].reset_index(drop=True)
mix = t.groupby("ep").nd.transform(lambda s: s.any() and (~s).any())
for f in F:
    a, n1, n0 = auc(t[f], t.nd)
    loeo = [auc(t[t.ep != e][f], t[t.ep != e].nd)[0] for e in t.ep.unique()]
    u = t[mix].copy(); u["rk"] = u.groupby("ep")[f].rank(pct=True)
    ar = auc(u.rk, u.nd)[0]
    res.append(dict(analysis="A_within_tension_next10_down", feature=f, auc=round(a, 3), n_pos=n1, n_neg=n0,
                    loeo_min=round(np.nanmin(loeo), 3), loeo_max=round(np.nanmax(loeo), 3), within_episode_rank_auc=round(ar, 3)))
w = d[d.fc & d["first"].isin(["UP", "DOWN"])].reset_index(drop=True); y = (w["first"] == "DOWN").values
for f in F:
    if f in ("dur",): continue
    x = w[f].values.astype(float); a, n1, n0 = auc(x, y); lo, hi = block_ci(x, y)
    yr = {yy: round(auc(w[w.date.dt.year == yy][f].values.astype(float), y[w.date.dt.year == yy])[0], 3) for yy in [2023, 2024, 2025]}
    res.append(dict(analysis="B_down_first_vs_up_first_given_3pct_hit", feature=f, auc=round(a, 3), n_pos=n1, n_neg=n0,
                    block_ci_lo=round(lo, 3), block_ci_hi=round(hi, 3), auc_2023=yr[2023], auc_2024=yr[2024], auc_2025=yr[2025]))
S = pd.DataFrame(res); S.to_csv(OUT + "DIRECTION_SEPARATORS_20261013.csv", index=False)
print("[3] separators written:", len(S), "rows; features tested:", F)
print(S[S.analysis.str.startswith("B")][["feature", "auc", "block_ci_lo", "block_ci_hi", "auc_2023", "auc_2024", "auc_2025"]].to_string(index=False))
print(S[S.analysis.str.startswith("A")][["feature", "auc", "loeo_min", "loeo_max", "within_episode_rank_auc"]].to_string(index=False))
tt = t.assign(db=pd.cut(t.dur, [0, 3, 10, 20, 40]))
print("    duration buckets:\n", tt.groupby("db", observed=True).agg(n=("nd", "size"), down=("nd", "sum"), up=("nu", "sum"), episodes=("ep", "nunique")))
