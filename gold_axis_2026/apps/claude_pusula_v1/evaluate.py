"""PUSULA v1 koşusu + PREREG §10 kabul ölçütleri + aylık/yıllık raporlar.
Kullanım: python3 evaluate.py data/PUSULA_V1_DAILY_ASOF_PANEL.csv results/
"""
import sys, os, json, math, csv
from collections import OrderedDict
import numpy as np
import pusula_v1 as P

SEED, NBOOT, BLOCK = 20261016, 2000, 6


def rank(a):
    a = np.asarray(a, float); o = a.argsort(); r = np.empty(len(a)); r[o] = np.arange(len(a))
    for v in np.unique(a):            # bağlar için ortalama sıra
        idx = np.where(a == v)[0]
        if len(idx) > 1: r[idx] = r[idx].mean()
    return r


def spearman(x, y):
    rx, ry = rank(x), rank(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def block_boot_ci(x, y):
    rng = np.random.default_rng(SEED); n = len(x); x = np.asarray(x); y = np.asarray(y)
    starts = n - BLOCK + 1; nb = math.ceil(n / BLOCK); vals = []
    for _ in range(NBOOT):
        idx = np.concatenate([np.arange(s, s + BLOCK) for s in rng.integers(0, starts, nb)])[:n]
        vals.append(spearman(x[idx], y[idx]))
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))



def direction_stats(rows):
    n = len(rows)
    if n == 0: return dict(N=0)
    tp = sum(1 for r in rows if r["pred_up"] and r["y"] > 0); tn = sum(1 for r in rows if not r["pred_up"] and r["y"] <= 0)
    up = sum(1 for r in rows if r["y"] > 0); dn = n - up
    rec_up = tp / up if up else None; rec_dn = tn / dn if dn else None
    bal = None if rec_up is None or rec_dn is None else (rec_up + rec_dn) / 2
    return dict(N=n, accuracy=(tp + tn) / n, balanced_accuracy=bal, up_recall=rec_up, down_recall=rec_dn, actual_up_share=up / n)


def main(panel, outdir):
    os.makedirs(outdir, exist_ok=True)
    rows = P.load_panel(panel)
    log, models, final = P.run(rows)
    # karar anı ağırlık/aday tahminlerini yeniden üretmek için run içindeki store yerine log'daki alanlar kullanılır
    trade = [g for g in log if g["date"] >= P.TRADE_START.isoformat()]
    t0 = trade[0]["t"]
    matured = [g for g in trade if g["y"] is not None]
    nonov = [g for g in matured if (g["t"] - t0) % P.H == 0]

    # K1 kalibrasyon (o anda geçerli c ile %80 aralık)
    cov = [abs(g["y"] - g["mu"]) <= 1.2816 * math.sqrt(g["c2"] * g["v"]) for g in nonov]
    K1 = sum(cov) / len(cov)
    # K2 sıra korelasyonu ve blok bootstrap
    rho = spearman([g["mu"] for g in nonov], [g["y"] for g in nonov])
    lo, hi = block_boot_ci([g["mu"] for g in nonov], [g["y"] for g in nonov])
    # K3 log-skor: topluluğun karışım öngörü yoğunluğu vs S0 δ=0,997 (ikisi de o anda geçerli c ile)
    def mixls(g):
        dens = sum(wk * math.exp(P.lognorm(g["y"], mk, g["c2"] * vk)) for wk, (mk, vk) in zip(g["wf"], g["kp"]))
        return math.log(max(dens, 1e-300))
    ls_ens = float(np.mean([mixls(g) for g in nonov]))
    ls_s0 = float(np.mean([P.lognorm(g["y"], g["mu_s0"], g["c2"] * g["v_s0"]) for g in nonov]))
    # K4 ekonomik
    nav = [g["nav"] for g in trade]; navp = [g["nav_passive"] for g in trade]; navt = [g["nav_trend"] for g in trade]
    mdd, mddp, mddt = P.max_dd(nav), P.max_dd(navp), P.max_dd(navt)
    K = OrderedDict(
        K1_calibration=dict(coverage80=K1, N=len(nonov), passed=0.72 <= K1 <= 0.88),
        K2_skill=dict(spearman=rho, ci95=[lo, hi], N=len(nonov), passed=rho > 0 and lo > 0),
        K3_beyond_drift=dict(mean_logscore_ensemble=ls_ens, mean_logscore_S0_d0997=ls_s0, passed=ls_ens > ls_s0),
        K4_economic=dict(final_nav=nav[-1], final_nav_trend=navt[-1], final_nav_passive=navp[-1],
                         maxdd=mdd, maxdd_passive=mddp, maxdd_trend=mddt,
                         passed=nav[-1] >= navt[-1] and mdd <= mddp))
    trades = [g for g in trade if g["action"] != "WAIT"]

    # aylık rapor
    months = OrderedDict()
    for g in trade:
        months.setdefault(g["date"][:7], []).append(g)
    monthly = []
    prev = dict(nav=100.0, navp=None, navt=100.0)
    for m, gs in months.items():
        lab = [g for g in matured if g["date"][:7] == m]
        first_p = gs[0]["nav_passive"] if prev["navp"] is None else prev["navp"]
        row = OrderedDict(month=m, nav_start=round(prev["nav"], 4), nav_end=round(gs[-1]["nav"], 4),
                          ret_pct=round(100 * (gs[-1]["nav"] / prev["nav"] - 1), 3),
                          passive_ret_pct=round(100 * (gs[-1]["nav_passive"] / first_p - 1), 3),
                          trend_ret_pct=round(100 * (gs[-1]["nav_trend"] / prev["navt"] - 1), 3),
                          position_end=gs[-1]["pos"], trades=[f'{g["date"]} {g["action"]}' for g in gs if g["action"] != "WAIT"],
                          mu_mean=round(float(np.mean([g["mu"] for g in gs])), 4),
                          labels_matured_for_month=len(lab),
                          hit_rate=round(float(np.mean([(g["mu"] > 0) == (g["y"] > 0) for g in lab])), 3) if lab else None,
                          coverage80=round(float(np.mean([abs(g["y"] - g["mu"]) <= 1.2816 * math.sqrt(g["c2"] * g["v"]) for g in lab])), 3) if lab else None,
                          c2_used=round(gs[-1]["c2"], 4), c2_next=round(gs[-1].get("c2_next", gs[-1]["c2"]), 4),
                          weights_end=gs[-1]["w"])
        monthly.append(row)
        prev = dict(nav=gs[-1]["nav"], navp=gs[-1]["nav_passive"], navt=gs[-1]["nav_trend"])

    # yıllık / kaynak raporu
    yearly = OrderedDict()
    for y in sorted({g["date"][:4] for g in trade}):
        ys = [g for g in nonov if g["date"][:4] == y]
        gs = [g for g in trade if g["date"][:4] == y]
        model_dir = [dict(pred_up=g["mu"] > 0, y=g["y"]) for g in ys]
        always_up = [dict(pred_up=True, y=g["y"]) for g in ys]
        s0 = [dict(pred_up=g["mu_s0"] > 0, y=g["y"]) for g in ys]
        tr = [g for g in ys if g["trend_up"] is not None]
        fixed = sum(1 for g in tr if (g["mu"] > 0) == (g["y"] > 0) and g["trend_up"] != (g["y"] > 0))
        broken = sum(1 for g in tr if (g["mu"] > 0) != (g["y"] > 0) and g["trend_up"] == (g["y"] > 0))
        start = [g for g in trade if g["date"][:4] < y]
        nav0 = start[-1]["nav"] if start else 100.0; p0 = start[-1]["nav_passive"] if start else gs[0]["nav_passive"]
        t0n = start[-1]["nav_trend"] if start else 100.0
        yearly[y] = OrderedDict(sources=sorted({g["src"] for g in gs}),
                                coverage80=float(np.mean([abs(g["y"] - g["mu"]) <= 1.2816 * math.sqrt(g["c2"] * g["v"]) for g in ys])) if ys else None,
                                model=direction_stats(model_dir), always_up=direction_stats(always_up), s0_drift=direction_stats(s0),
                                vs_trend_corrected=fixed, vs_trend_broken=broken,
                                strategy_ret_pct=100 * (gs[-1]["nav"] / nav0 - 1),
                                passive_ret_pct=100 * (gs[-1]["nav_passive"] / p0 - 1),
                                trend_ret_pct=100 * (gs[-1]["nav_trend"] / t0n - 1))

    res = OrderedDict(model="PUSULA_V1", panel=os.path.basename(panel),
                      period=[trade[0]["date"], trade[-1]["date"]], trading_days=len(trade),
                      acceptance=K, all_passed=all(v["passed"] for v in K.values()),
                      trades=[dict(date=g["date"], action=g["action"], nav=round(g["nav"], 4), mu=round(g["mu"], 4), sd=round(g["sd"], 4)) for g in trades],
                      final_position=final["pos"], yearly=yearly,
                      notes=["2023-2026 daha önce görülmüş dönemdir; kör test değildir.",
                             "Dukascopy BID/ASK + varsayımsal %0,8/yön banka maliyeti; Türk bankası kotasyonu değildir.",
                             "Haber verisi kullanılmadı (as-of doğrulanmış haber kaynağı yok)."])
    json.dump(res, open(os.path.join(outdir, "PUSULA_V1_RESULTS.json"), "w"), indent=1, ensure_ascii=False, default=float)
    with open(os.path.join(outdir, "PUSULA_V1_MONTHLY.csv"), "w", newline="") as fh:
        w = csv.writer(fh); keys = list(monthly[0].keys()); w.writerow(keys)
        for m in monthly: w.writerow([m[k] if not isinstance(m[k], list) else "|".join(map(str, m[k])) for k in keys])
    with open(os.path.join(outdir, "PUSULA_V1_DAILY_LOG.csv"), "w", newline="") as fh:
        w = csv.writer(fh); keys = ["date", "src", "mu", "sd", "v", "c2", "action", "pos", "nav", "nav_passive", "nav_trend", "trend_pos", "y"]
        w.writerow(keys)
        for g in log: w.writerow([g.get(k) for k in keys])
    return res, monthly


if __name__ == "__main__":
    res, monthly = main(sys.argv[1], sys.argv[2])
    print(json.dumps(dict(acceptance=res["acceptance"], all_passed=res["all_passed"], n_trades=len(res["trades"]),
                          final_position=res["final_position"]), indent=1, default=float))
