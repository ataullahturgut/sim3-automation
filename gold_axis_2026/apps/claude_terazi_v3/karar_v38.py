"""TERAZİ v3.8 (ön kayıt eki 9): yapı tabanlı alış/satış, aday A, B, C.
Girdi: v3.5'in günlük serisi. Kullanım: python3 karar_v38.py"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import terazi_v3 as T3, run_terazi_v3 as RV, deneyim_states as S

K = 2


def pivots(p, k=K):
    lows, highs = [], []
    for s in range(k, len(p) - k):
        nb = [p[s + d] for d in range(-k, k + 1) if d]
        if all(p[s] < x for x in nb): lows.append((s + k, p[s]))
        if all(p[s] > x for x in nb): highs.append((s + k, p[s]))
    return lows, highs


def known(lst, i):
    return [v for (kd, v) in lst if kd <= i]


def simulate(daily, rows, variant, start="2023-01-03"):
    p = [r["p06"] for r in rows]
    lows, highs = pivots(p)
    d2i = {str(r["date"]): i for i, r in enumerate(rows)}
    cash, units, pos = 100.0, 0.0, 0
    trades, navs, dates = [], [], []
    for d in daily:
        if d["date"] < start:
            continue
        i = d2i[d["date"]]; r = rows[i]
        L, Hh = known(lows, i), known(highs, i)
        broken = bool(L) and p[i] < L[-1]
        v2buy = d["P"] is not None and d["P"] - T3.LAM * d["U"] > 0.5
        if pos == 0:
            if variant == "A":
                ok = v2buy
            elif variant == "B":
                ok = v2buy and bool(Hh) and p[i] > Hh[-1]
            else:
                ok = v2buy and len(L) >= 2 and L[-1] > L[-2] and not broken
            if ok:
                units = cash * (1 - S.FEE) / r["ask"]; cash = 0.0; pos = 1
                trades.append((d["date"], "AL", round(r["ask"], 2)))
        elif broken and d["macro"]:
            cash = units * r["bid"] * (1 - S.FEE); units = 0.0; pos = 0
            trades.append((d["date"], "SAT", round(r["bid"], 2)))
        navs.append(cash + units * r["bid"] * (1 - S.FEE)); dates.append(d["date"])
    return navs, trades, dates


def fits_2023(tr):
    t23 = [t for t in tr if t[0] < "2024-01-01"]
    sells = [t[0] for t in t23 if t[1] == "SAT"]
    buys = [t[0] for t in t23 if t[1] == "AL"][1:]
    ok_s = all(("2023-02-03" <= s <= "2023-02-10") or ("2023-05-08" <= s <= "2023-05-31") for s in sells)
    has = any("2023-02-03" <= s <= "2023-02-10" for s in sells) and any("2023-05-08" <= s <= "2023-05-31" for s in sells)
    ok_b = all(b[:7] in ("2023-03", "2023-10") for b in buys)
    return ok_s and has and ok_b


def main():
    rows = S.load_rows(dev_only=True)
    daily = json.load(open(os.path.join(HERE, "TERAZI_V3_5_GUNLUK.json")))
    out = {}
    for v in ("A", "B", "C"):
        navs, tr, dates = simulate(daily, rows, v)
        nav23 = navs[dates.index(max(x for x in dates if x < "2024-01-01"))]
        out[v] = dict(net_nav=round(navs[-1], 2), nav_2023=round(nav23, 2), trades=len(tr),
                      max_dd=round(RV.mdd(navs), 2), fits_2023=fits_2023(tr), trade_list=tr,
                      nav_daily=list(zip(dates, [round(x, 2) for x in navs])))
        o = out[v]
        print(f"\n{v}: NAV {o['net_nav']}  2023 sonu {o['nav_2023']}  işlem {o['trades']}  düşüş %{o['max_dd']}  2023 yoluna uyuyor: {o['fits_2023']}")
        for t in tr: print("   ", *t)
    fit = [v for v in out if out[v]["fits_2023"]]
    pick = max(fit, key=lambda v: out[v]["net_nav"]) if fit else None
    print(f"\nSEÇİM (ön kayıt kuralı): {pick}")
    json.dump(dict(variants=out, secim=pick), open(os.path.join(HERE, "TERAZI_V3_8_SONUC.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
