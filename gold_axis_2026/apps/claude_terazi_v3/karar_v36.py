"""TERAZİ v3.6 karar katmanı (ön kayıt eki 7): birikimli kırılma kanıtıyla satış.
Girdi: v3.5'in günlük serisi (öğrenme konumdan bağımsızdır). Kullanım: python3 karar_v36.py"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import terazi_v3 as T3, run_terazi_v3 as RV, deneyim_states as S

H = math.log(9.0)          # Wald, α = β = 0,10
P0 = 0.06630581867388363   # ısıtma taban oranı (v3 koşularında aynı)


def odds(x):
    x = min(max(x, 1e-9), 1 - 1e-9); return x / (1 - x)


def simulate(daily, rows, start="2023-01-03", end="9999"):
    d2i = {str(r["date"]): i for i, r in enumerate(rows)}
    cash, units, pos, Sc = 100.0, 0.0, 0, 0.0
    trades, navs, trace = [], [], []
    for d in daily:
        if not (start <= d["date"] <= end):
            continue
        r = rows[d2i[d["date"]]]
        if pos == 0:
            if d["P"] is not None and d["P"] - T3.LAM * d["U"] > 0.5:
                units = cash * (1 - S.FEE) / r["ask"]; cash = 0.0; pos = 1; Sc = 0.0
                trades.append((d["date"], "AL", round(r["ask"], 2)))
        else:
            l = 0.0 if d["Q"] is None else math.log(odds(d["Q"]) / odds(P0))
            Sc = max(0.0, Sc + l)
            if Sc > H and d["macro"]:
                cash = units * r["bid"] * (1 - S.FEE); units = 0.0; pos = 0
                trades.append((d["date"], "SAT", round(r["bid"], 2)))
        trace.append(dict(date=d["date"], gold=d["gold"], Q=d["Q"], S=round(Sc, 3), pos=pos))
        navs.append(cash + units * r["bid"] * (1 - S.FEE))
    return navs, trades, trace


def main():
    rows = S.load_rows(dev_only=True)
    daily = json.load(open(os.path.join(HERE, "TERAZI_V3_5_GUNLUK.json")))
    navs, tr, trace = simulate(daily, rows)
    dd = RV.mdd(navs)
    early = [t for t in tr if t[1] == "SAT" and "2023-01-03" <= t[0] <= "2023-02-02"]
    feb = [t for t in tr if t[1] == "SAT" and "2023-02-03" <= t[0] <= "2023-02-10"]
    res = dict(net_nav=round(navs[-1], 2), trades=len(tr), max_dd=round(dd, 2),
               S0=not early, S1=bool(feb), S2=navs[-1] >= 213.49, S3=len(tr) <= 20, S4=dd <= 11.67,
               trade_list=tr, jan_feb_2023=[x for x in trace if x["date"] <= "2023-03-10"])
    print(f"=== TERAZİ v3.6 — geliştirme kaydı, kanıt değil ===\nnet NAV {res['net_nav']}  işlem {len(tr)}  maks düşüş %{dd:.2f}  (h = {H:.3f})")
    for k in ("S0", "S1", "S2", "S3", "S4"):
        print(f"  {k}: {'GEÇTİ' if res[k] else 'GEÇMEDİ'}")
    print("işlemler:"); [print("  ", *t) for t in tr]
    print("Ocak–Mart 2023 birikim:")
    for x in res["jan_feb_2023"]:
        print(f"   {x['date']} altın {x['gold']} Q {x['Q']} S {x['S']} pos {x['pos']}")
    json.dump(res, open(os.path.join(HERE, "TERAZI_V3_6_SONUC.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
