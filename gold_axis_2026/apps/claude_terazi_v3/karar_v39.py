"""TERAZİ v3.9 (ön kayıt eki 10): iki ölçekli yapı. Girdi: v3.5 günlük serisi."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import terazi_v3 as T3, run_terazi_v3 as RV, deneyim_states as S
from karar_v38 import pivots, known, fits_2023

K_SMALL, K_BIG = 2, 5


def trend_states(p, k=K_BIG):
    lows, highs = pivots(p, k)
    st, out = "YUKARI", []
    for i in range(len(p)):
        L, H = known(lows, i), known(highs, i)
        if L and p[i] < L[-1]:
            st = "ASAGI"
        elif H and p[i] > H[-1]:
            st = "YUKARI"
        out.append(st)
    return out


def simulate(daily, rows, start="2023-01-03"):
    p = [r["p06"] for r in rows]
    lows2, _ = pivots(p, K_SMALL)
    tr_st = trend_states(p)
    d2i = {str(r["date"]): i for i, r in enumerate(rows)}
    cash, units, pos = 100.0, 0.0, 0
    trades, navs, dates, trace = [], [], [], []
    for d in daily:
        if d["date"] < start:
            continue
        i = d2i[d["date"]]; r = rows[i]
        L2 = known(lows2, i)
        brk2 = bool(L2) and p[i] < L2[-1]
        post = d["Pe"] is not None and d["Pe"] + T3.LAM * d["Ue"] < 0.5
        v2buy = d["P"] is not None and d["P"] - T3.LAM * d["U"] > 0.5
        why = None
        if pos == 0:
            if v2buy and tr_st[i] == "YUKARI":
                units = cash * (1 - S.FEE) / r["ask"]; cash = 0.0; pos = 1
                trades.append((d["date"], "AL", round(r["ask"], 2), "v2 + büyük trend yukarı"))
        elif d["macro"] and ((brk2 and post) or tr_st[i] == "ASAGI"):
            why = "kısa yapı + sonsal" if (brk2 and post) else "büyük trend aşağı"
            cash = units * r["bid"] * (1 - S.FEE); units = 0.0; pos = 0
            trades.append((d["date"], "SAT", round(r["bid"], 2), why))
        navs.append(cash + units * r["bid"] * (1 - S.FEE)); dates.append(d["date"])
        trace.append(dict(date=d["date"], gold=d["gold"], trend=tr_st[i], brk2=brk2, post=post, macro=d["macro"], pos=pos))
    return navs, trades, dates, trace


def main():
    rows = S.load_rows(dev_only=True)
    daily = json.load(open(os.path.join(HERE, "TERAZI_V3_5_GUNLUK.json")))
    navs, tr, dates, trace = simulate(daily, rows)
    nav23 = navs[max(i for i, x in enumerate(dates) if x < "2024-01-01")]
    dd = RV.mdd(navs)
    res = dict(net_nav=round(navs[-1], 2), nav_2023=round(nav23, 2), trades=len(tr), max_dd=round(dd, 2),
               fits_2023=fits_2023([t[:3] for t in tr]), S2=navs[-1] >= 213.49, S3=len(tr) <= 20, S4=dd <= 11.67,
               trade_list=tr, nav_daily=list(zip(dates, [round(x, 2) for x in navs])), trace=trace)
    print(f"=== TERAZİ v3.9 — geliştirme kaydı, kanıt değil ===\nNAV {res['net_nav']}  2023 sonu {res['nav_2023']}  işlem {len(tr)}  düşüş %{dd:.2f}  2023 yolu: {res['fits_2023']}  S2 {res['S2']} S3 {res['S3']} S4 {res['S4']}")
    for t in tr: print("   ", *t)
    json.dump(res, open(os.path.join(HERE, "TERAZI_V3_9_SONUC.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
