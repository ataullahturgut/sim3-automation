"""TERAZİ v3.7 karar katmanı (ön kayıt eki 8): satış için piyasa yapısı kırılması şart.
Girdi: v3.5'in günlük serisi (öğrenme konumdan bağımsız). Kullanım: python3 karar_v37.py"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import terazi_v3 as T3, run_terazi_v3 as RV, deneyim_states as S

K = 2


def structure_break(p, k=K):
    """brk[t] = p[t] < t anında bilinen son salınım dibinin fiyatı. Dip s, s+k'da bilinir."""
    n = len(p); out = [False] * n; last = None; lows = []
    for s in range(k, n - k):
        if all(p[s] < p[s + d] for d in range(-k, k + 1) if d):
            lows.append((s + k, p[s]))          # (bilindiği gün, fiyat)
    j = 0
    for t in range(n):
        while j < len(lows) and lows[j][0] <= t:
            last = lows[j][1]; j += 1
        out[t] = last is not None and p[t] < last
    return out, lows


def simulate(daily, rows, start="2023-01-03"):
    p = [r["p06"] for r in rows]
    brk, lows = structure_break(p)
    d2i = {str(r["date"]): i for i, r in enumerate(rows)}
    cash, units, pos = 100.0, 0.0, 0
    trades, navs, trace = [], [], []
    for d in daily:
        if d["date"] < start:
            continue
        i = d2i[d["date"]]; r = rows[i]
        cond = d["Pe"] is not None and d["Pe"] + T3.LAM * d["Ue"] < 0.5
        if pos == 0:
            if d["P"] is not None and d["P"] - T3.LAM * d["U"] > 0.5:
                units = cash * (1 - S.FEE) / r["ask"]; cash = 0.0; pos = 1
                trades.append((d["date"], "AL", round(r["ask"], 2)))
        elif brk[i] and cond and d["macro"]:
            cash = units * r["bid"] * (1 - S.FEE); units = 0.0; pos = 0
            trades.append((d["date"], "SAT", round(r["bid"], 2)))
        last_low = max((lp for (kd, lp) in [(a, b) for a, b in lows] if kd <= i), key=lambda x: 0, default=None)
        known = [lp for (kd, lp) in lows if kd <= i]
        trace.append(dict(date=d["date"], gold=d["gold"], son_dip=None if not known else round(known[-1], 2),
                          yapi_kirik=brk[i], sonsal_sat=cond, makro=d["macro"], pos=pos))
        navs.append(cash + units * r["bid"] * (1 - S.FEE))
    return navs, trades, trace


def main():
    rows = S.load_rows(dev_only=True)
    daily = json.load(open(os.path.join(HERE, "TERAZI_V3_5_GUNLUK.json")))
    navs, tr, trace = simulate(daily, rows)
    dd = RV.mdd(navs)
    early = [t for t in tr if t[1] == "SAT" and "2023-01-03" <= t[0] <= "2023-02-02"]
    feb = [t for t in tr if t[1] == "SAT" and "2023-02-03" <= t[0] <= "2023-02-10"]
    pairs = [dict(sat=a[0], sat_f=a[2], al=b[0], al_f=b[2], kazanc=round(100 * (a[2] * (1 - S.FEE) ** 2 / b[2] - 1), 2))
             for a, b in zip(tr, tr[1:]) if a[1] == "SAT" and b[1] == "AL"]
    res = dict(net_nav=round(navs[-1], 2), trades=len(tr), max_dd=round(dd, 2),
               S0=not early, S1=bool(feb), S2=navs[-1] >= 213.49, S3=len(tr) <= 20, S4=dd <= 11.67,
               trade_list=tr, sell_rebuy=pairs, trace_2023=[x for x in trace if x["date"] < "2024-01-01"],
               nav_daily=[(x["date"], round(v, 2)) for x, v in zip(trace, navs)])
    print(f"=== TERAZİ v3.7 — geliştirme kaydı, kanıt değil ===\nnet NAV {res['net_nav']}  işlem {len(tr)}  maks düşüş %{dd:.2f}")
    for k in ("S0", "S1", "S2", "S3", "S4"):
        print(f"  {k}: {'GEÇTİ' if res[k] else 'GEÇMEDİ'}")
    print("işlemler:"); [print("  ", *t) for t in tr]
    print("satış → geri alım:"); [print(f"   {q['sat']} {q['sat_f']} → {q['al']} {q['al_f']}  %{q['kazanc']:+}") for q in pairs]
    print("Ocak–Şubat 2023:")
    for x in trace:
        if x["date"] <= "2023-02-28":
            print(f"   {x['date']} altın {x['gold']} son dip {x['son_dip']} yapı kırık {x['yapi_kirik']} sonsal {x['sonsal_sat']} makro {x['makro']} pos {x['pos']}")
    json.dump(res, open(os.path.join(HERE, "TERAZI_V3_7_SONUC.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
