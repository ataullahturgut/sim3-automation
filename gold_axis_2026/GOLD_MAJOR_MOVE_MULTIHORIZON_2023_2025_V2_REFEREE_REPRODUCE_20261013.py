"""Independent referee audit of the XAU 2023-2025 multi-horizon move atlas V2.

Reads ONLY the committed V2 CSVs (no network, no Neon). Reproduces every
price-derived number in GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_REFEREE_REVIEW_20261013.md.
Cross-market numbers (GC/SI/ZN/NQ/CL) come from the companion SQL file run on Neon.
Macro surprises are embedded below (Neon `observations`: *_ACTUAL_FIRST_PRINT vs *_CONSENSUS_PIT).

Usage: python3 GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_REFEREE_REPRODUCE_20261013.py
"""
import os
import numpy as np
import pandas as pd

D = os.path.dirname(os.path.abspath(__file__)) + "/"
P = "GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_"
a = pd.read_csv(D + P + "ALL_774_DAYS_20261013.csv", parse_dates=["date"]).reset_index(drop=True)
c = pd.read_csv(D + P + "DIRECTIONAL_CLUSTERS_20261013.csv", parse_dates=["start", "end"])
news = pd.read_csv(D + P + "53_CLUSTER_NEWS_RESEARCH_20261013.csv", parse_dates=["main_source_publication_date"])

# ---------- 1. Recompute flags from raw fields ----------
UPC = {"1H": a.max_1h_up_pct >= 3, "4H": a.max_4h_up_pct >= 3, "12H": a.max_12h_up_pct >= 3,
       "1TD": a.ret_1tradingday_pct >= 3, "3TD": a.ret_3tradingdays_pct >= 3, "5TD": a.ret_5tradingdays_pct >= 3}
DNC = {"1H": a.max_1h_down_pct <= -3, "4H": a.max_4h_down_pct <= -3, "12H": a.max_12h_down_pct <= -3,
       "1TD": a.ret_1tradingday_pct <= -3, "3TD": a.ret_3tradingdays_pct <= -3, "5TD": a.ret_5tradingdays_pct <= -3}
up = pd.DataFrame(UPC); dn = pd.DataFrame(DNC)
a["rup"] = up.apply(lambda r: ";".join(k for k in r.index if r[k]), axis=1)
a["rdn"] = dn.apply(lambda r: ";".join(k for k in r.index if r[k]), axis=1)
prim = up.any(axis=1) | dn.any(axis=1)
mism = ((a.rup != a.flags_up_3pct.fillna("")) | (a.rdn != a.flags_down_3pct.fillna(""))).sum()
print("[1] primary days", prim.sum(), "| flag-string mismatches vs V2:", mism)
print("    flags by horizon (UP,DOWN):", {k: (int(up[k].sum()), int(dn[k].sum())) for k in up.columns})
miss = sorted(set(pd.bdate_range("2023-01-02", "2025-12-31")) - set(a.date))
print("    weekdays absent:", [d.strftime("%Y-%m-%d") for d in miss])

# ---------- 2. Re-cluster and estimate window onset ----------
def clus(col, gap=3):
    idx = a.index[a[col] != ""].tolist(); out, cur = [], [idx[0]]
    for j in idx[1:]:
        if j - cur[-1] <= gap: cur.append(j)
        else: out.append(cur); cur = [j]
    out.append(cur); return out
print("[2] clusters by merge gap:", {g: len(clus("rup", g)) + len(clus("rdn", g)) for g in [1, 2, 3, 5]})
H = {"1H": 0, "4H": 0, "12H": 0, "1TD": 1, "3TD": 3, "5TD": 5}
ons = []
for _, r in c.iterrows():
    col = "rup" if r.direction == "UP" else "rdn"
    g = a[(a.date >= r.start) & (a.date <= r.end) & (a[col] != "")]
    i0 = min(i - max(H[h] for h in fl.split(";")) for i, fl in zip(g.index, g[col]))
    ons.append(a.date[i0])
c["window_onset"] = ons
c["lag_days"] = (c.start - c.window_onset).dt.days
print("    first-flag lags true window onset by >=3 calendar days in", (c.lag_days >= 3).sum(), "of 53 clusters")
c = c.merge(news[["id", "source_timing", "main_source_publication_date"]], on="id")
def retime(r):
    d = r.main_source_publication_date
    if pd.isna(d): return "NONE"
    return "PRE" if d < r.window_onset else ("DURING" if d <= r.end else "POST")
c["timing_vs_onset"] = c.apply(retime, axis=1)
print("    V2 timing vs onset-based timing:\n", pd.crosstab(c.source_timing, c.timing_vs_onset))

# ---------- 3. Volatility normalisation ----------
s = a.close_mid
a["r1"] = np.log(s).diff() * 100
a["vol60"] = a.r1.rolling(60, min_periods=40).std().shift(1)
a["z"] = a.r1 / a.vol60
a["z5"] = a.ret_5tradingdays_pct / (a.vol60 * 5 ** 0.5)
for y in [2023, 2024, 2025]:
    w = a[a.date.dt.year == y]
    print(f"[3] {y}: daily sd {w.r1.std():.3f}% (3% = {3 / w.r1.std():.1f} sd) | 5TD |ret|>=3%: {(w.ret_5tradingdays_pct.abs() >= 3).sum()}"
          f" vs |z5|>=2: {(w.z5.abs() >= 2).sum()}")
rows = []
for _, k in c.iterrows():
    g = a[(a.date >= k.window_onset) & (a.date <= k.end)]
    rows.append((g.z5.abs().max(), g.z.abs().max()))
c["max_abs_z5"], c["max_abs_z1"] = zip(*rows)
intr = c.horizons.str.contains("4H|12H")
c["vol_status"] = np.where(c.max_abs_z5.isna(), "UNKNOWN_SHORT_HISTORY",
                  np.where((c.max_abs_z5 < 2) & (c.max_abs_z1 < 2.5) & ~intr, "THRESHOLD_ARTIFACT_CANDIDATE", "VOL_ADJUSTED_LARGE"))
print("    cluster vol status:", c.vol_status.value_counts().to_dict())

# ---------- 4. Missed moves ----------
fl = prim
cov = pd.Series(False, index=a.index)
for _, k in c.iterrows(): cov |= (a.date >= k.window_onset) & (a.date <= k.end)
print("[4] unflagged days with |z|>=2.5:", a[(a.z.abs() >= 2.5) & ~fl].date.dt.strftime("%Y-%m-%d").tolist())
print("    unflagged days with intraday range>=2.5% and outside every cluster window:",
      a[(a.intraday_range_pct >= 2.5) & ~fl & ~cov].date.dt.strftime("%Y-%m-%d").tolist())
r20 = (s / s.shift(20) - 1) * 100
unc = [a.date[i].strftime("%Y-%m-%d") for i in a.index[r20.abs() >= 6] if not cov.loc[max(0, i - 20):i].any()]
print("    20TD |ret|>=6% windows with zero cluster overlap:", unc)

# ---------- 5. Ex-ante stretch conditions vs forward outcomes ----------
a["r20"] = r20
a["d50"] = (s / s.rolling(50).mean() - 1) * 100
a["d200"] = (s / s.rolling(200).mean() - 1) * 100
d = s.diff(); g_ = d.clip(lower=0).ewm(alpha=1 / 14).mean(); l_ = (-d.clip(upper=0)).ewm(alpha=1 / 14).mean()
a["rsi"] = 100 - 100 / (1 + g_ / l_)
p = s.values; n = len(p); Hf = 10
a["fmin"] = [np.nan if i >= n - Hf else (p[i + 1:i + Hf + 1].min() / p[i] - 1) * 100 for i in range(n)]
a["fmax"] = [np.nan if i >= n - Hf else (p[i + 1:i + Hf + 1].max() / p[i] - 1) * 100 for i in range(n)]
v = a.dropna(subset=["fmin", "r20"])
print(f"[5] base P(10-session min<=-3%)={(v.fmin <= -3).mean():.3f}  P(max>=+3%)={(v.fmax >= 3).mean():.3f}  N={len(v)}")
def rep(name, m):
    q = v[m]; runs = int((m.astype(int).diff() == 1).sum() + int(m.iloc[0]))
    print(f"    {name:22s} days={len(q):4d} runs={runs:3d} P(dn)={(q.fmin <= -3).mean():.3f} P(up)={(q.fmax >= 3).mean():.3f}")
for th in [3, 5, 8]: rep(f"r20>={th}%", v.r20 >= th)
rep("r20<=-3%", v.r20 <= -3); rep("RSI14>=70", v.rsi >= 70); rep("RSI14>=80", v.rsi >= 80)
rep("above MA50>=5%", v.d50 >= 5); rep("above MA50>=8%", v.d50 >= 8)
m = (a.rsi >= 75) & (a.d200 >= 20)
print("    RSI>=75 & >20% above MA200 dates:", a[m].date.dt.strftime("%Y-%m-%d").tolist())

# ---------- 6. Release days: same-day |z| (no overlapping windows) ----------
rel = a.same_date_macro_release.fillna("")
for lab, mm in [("CPI", rel.str.contains("CPI")), ("NFP", rel.str.contains("NFP")), ("FOMC", rel.str.contains("FOMC")), ("none", rel == "")]:
    zz = a[mm].z.abs().dropna()
    print(f"[6] {lab:5s} n={len(zz):3d} mean|z|={zz.mean():.2f} P(|z|>=2)={(zz >= 2).mean():.3f}")
try:
    from scipy.stats import fisher_exact
    k_f = int((a[rel.str.contains("FOMC")].z.abs() >= 2).sum()); n_f = int(a[rel.str.contains("FOMC")].z.notna().sum())
    k_n = int((a[rel == ""].z.abs() >= 2).sum()); n_n = int(a[rel == ""].z.notna().sum())
    print("    FOMC vs none Fisher:", fisher_exact([[k_f, n_f - k_f], [k_n, n_n - k_n]]))
except ImportError:
    pass

# ---------- 7. Macro surprises (Neon first print minus PIT consensus) ----------
NFP = {"2023-01-06": (223, 200), "2023-02-03": (517, 185), "2023-03-10": (311, 205), "2023-04-07": (236, 239), "2023-05-05": (253, 180),
       "2023-06-02": (339, 180), "2023-07-07": (209, 225), "2023-08-04": (187, 200), "2023-09-01": (187, 170), "2023-10-06": (336, 170),
       "2023-11-03": (150, 180), "2023-12-08": (199, 180), "2024-01-05": (216, 170), "2024-02-02": (353, 187), "2024-03-08": (275, 198),
       "2024-04-05": (303, 212), "2024-05-03": (175, 238), "2024-06-07": (272, 182), "2024-07-05": (206, 191), "2024-08-02": (114, 176),
       "2024-09-06": (142, 164), "2024-10-04": (254, 147), "2024-11-01": (12, 106), "2024-12-06": (227, 202), "2025-01-10": (256, 164),
       "2025-02-07": (143, 169), "2025-03-07": (151, 159), "2025-04-04": (228, 137), "2025-05-02": (177, 138), "2025-06-06": (139, 126),
       "2025-07-03": (147, 111), "2025-08-01": (73, 106), "2025-09-05": (22, 75), "2025-11-20": (119, 53), "2025-12-16": (64, 51)}
CC = {"2023-01-12": (.3, .3), "2023-02-14": (.4, .4), "2023-03-14": (.5, .4), "2023-04-12": (.4, .4), "2023-05-10": (.4, .4), "2023-06-13": (.4, .4),
      "2023-07-12": (.2, .3), "2023-08-10": (.2, .2), "2023-09-13": (.3, .2), "2023-10-12": (.3, .3), "2023-11-14": (.2, .3), "2023-12-12": (.3, .3),
      "2024-01-11": (.3, .3), "2024-02-13": (.4, .3), "2024-03-12": (.4, .3), "2024-04-10": (.4, .3), "2024-05-15": (.3, .3), "2024-06-12": (.2, .3),
      "2024-07-11": (.1, .2), "2024-08-14": (.2, .2), "2024-09-11": (.3, .2), "2024-10-10": (.3, .2), "2024-11-13": (.3, .3), "2024-12-11": (.3, .3),
      "2025-01-15": (.2, .3), "2025-02-12": (.4, .3), "2025-03-12": (.2, .3), "2025-04-10": (.1, .3), "2025-05-13": (.2, .3), "2025-06-11": (.1, .3),
      "2025-07-15": (.2, .3), "2025-08-12": (.3, .3), "2025-09-11": (.3, .3), "2025-10-24": (.2, .3)}
ai = a.set_index("date")
for name, dct in [("NFP", NFP), ("CoreCPI", CC)]:
    x = pd.DataFrame([(pd.Timestamp(k), v_[0] - v_[1]) for k, v_ in dct.items()], columns=["date", "surp"]).set_index("date")
    x = x[x.index.isin(ai.index)]; x["r1"] = ai.loc[x.index, "r1"]
    nz = x[x.surp != 0]
    print(f"[7] {name}: n={len(x)} nonzero={len(nz)} corr(surprise, same-day gold)={np.corrcoef(x.surp, x.r1)[0, 1]:.2f}"
          f" opposite-sign share={(np.sign(nz.surp) == -np.sign(nz.r1)).mean():.2f}")

c.to_csv(D + P + "REFEREE_RECOMPUTED_CLUSTER_TIMING_20261013.csv", index=False,
         columns=["id", "direction", "start", "end", "window_onset", "lag_days", "horizons", "source_timing",
                  "main_source_publication_date", "timing_vs_onset", "max_abs_z5", "max_abs_z1", "vol_status"], float_format="%.2f")
print("wrote recomputed cluster timing CSV")
