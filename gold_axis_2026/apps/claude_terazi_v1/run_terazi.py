"""TERAZİ v1 maratonu: 2020-01→2022-12 ısıtma, 2023-01→2025-12 işlem. Aylık rapor yazar, modeli dondurur.
Kullanım: python3 run_terazi.py [çıktı_klasörü]
"""
import json, math, os, sys
from collections import OrderedDict
from datetime import date
import numpy as np
import terazi_v1 as T
import deneyim_states as S
from deneyim_v1 import oracle

HERE = os.path.dirname(os.path.abspath(__file__))
START = date(2023, 1, 3)


def mdd(v):
    pk, m = -1e18, 0.0
    for x in v: pk = max(pk, x); m = max(m, 100 * (1 - x / pk))
    return m


def marathon(outdir, rows=None):
    rows = rows if rows is not None else S.load_rows(dev_only=True)
    raw, macro = S.build_states(rows)
    Z, std = S.standardize(raw)
    i0 = next(i for i, r in enumerate(rows) if r["date"] >= START)
    mid = lambda q: (rows[q]["bid"] + rows[q]["ask"]) / 2
    net = T.Terazi()
    os.makedirs(os.path.join(outdir, "reports"), exist_ok=True)
    learned = set()

    def matured_upto(end):
        """end gününe kadar olgunlaşmış (q + H <= end) günlerin durum/sonuç/indeksleri."""
        qs = list(range(0, end - T.H + 1))
        return Z[qs], np.array([100 * math.log(mid(q + T.H) / mid(q)) for q in qs]), qs

    # Tek aylık döngü: 2020-01'den itibaren öğrenme, işlem yalnız 2023-01-03'ten sonra (düzeltme eki)
    months = OrderedDict()
    for i in range(len(rows)):
        months.setdefault(str(rows[i]["date"])[:7], []).append(i)

    cash, units, pos = 100.0, 0.0, 0
    nav_hist, trades, reports = [], [], []
    for m, idxs in months.items():
        trading = idxs[-1] >= i0
        nav0 = cash + units * rows[idxs[0] - 1]["bid"] * (1 - S.FEE) if idxs[0] > i0 else 100.0
        mtr, days = [], []
        for i in idxs:
            r = rows[i]
            if i < i0:
                continue
            act, d = net.action(pos, Z[i])
            if d is None: net.audit["no_opinion"] += 1
            if act == "AL":
                units = cash * (1 - S.FEE) / r["ask"]; cash = 0.0; pos = 1
                mtr.append(dict(date=str(r["date"]), action="AL", price=round(r["ask"], 2), E=round(d["E"], 3), U=round(d["U"], 3), rules=d["top"]))
            elif act == "SAT":
                cash = units * r["bid"] * (1 - S.FEE); units = 0.0; pos = 0
                mtr.append(dict(date=str(r["date"]), action="SAT", price=round(r["bid"], 2), E=round(d["E"], 3), U=round(d["U"], 3), rules=d["top"]))
            days.append(dict(date=str(r["date"]), E=None if d is None else round(d["E"], 3),
                             U=None if d is None else round(d["U"], 3), fired=0 if d is None else d["n_fired"], pos=pos))
            nav_hist.append((i, cash + units * r["bid"] * (1 - S.FEE), pos))
        trades += mtr
        i_end = idxs[-1]
        # ay sonu: olgunlaşan yeni sonuçları öğren, sonra yapıyı değiştir (ısıtma aylarında da)
        for q in range(0, i_end - T.H + 1):
            if q not in learned:
                net.learn(q, Z[q], 100 * math.log(mid(q + T.H) / mid(q))); learned.add(q)
        Zm, rm, qs = matured_upto(i_end)
        ch = net.restructure(Zm, rm, qs, now=i_end)
        if not trading:
            continue
        opos, _ = oracle(rows, 0, i_end); Y = np.array(opos)
        posmap = {q: p for (q, _, p) in nav_hist}
        tdays = [i for i in idxs if i >= i0]
        wrong = sum(1 for i in tdays if Y[i] != posmap[i])
        rep = OrderedDict(month=m, days=len(idxs),
                          gold_change_pct=round(100 * (rows[i_end]["p06"] / rows[idxs[0] - 1]["p06"] - 1), 2),
                          nav_start=round(nav0, 4), nav_end=round(nav_hist[-1][1], 4),
                          month_ret_pct=round(100 * (nav_hist[-1][1] / nav0 - 1), 2),
                          position_end="ALTIN" if pos else "NAKİT", trades=mtr,
                          mean_E=round(float(np.mean([d["E"] for d in days if d["E"] is not None])), 3) if any(d["E"] is not None for d in days) else None,
                          mean_U=round(float(np.mean([d["U"] for d in days if d["U"] is not None])), 3) if any(d["U"] is not None for d in days) else None,
                          days_without_opinion=sum(1 for d in days if d["E"] is None),
                          wrong_days_vs_ideal=wrong, trading_days_in_month=len(tdays),
                          rule_base_size=len(net.rules), rules_born=ch["born"], rules_died=ch["died"],
                          strongest_rules=[R.to_dict() for R in sorted(net.rules, key=lambda x: -x.weight)[:5]])
        reports.append(rep)
        json.dump(rep, open(os.path.join(outdir, "reports", f"AYLIK_{m.replace('-', '_')}.json"), "w"), indent=1, ensure_ascii=False)
        L = [f"# TERAZİ v1 — {m}", "",
             f"Altın %{rep['gold_change_pct']}; model NAV {rep['nav_start']} → {rep['nav_end']} (%{rep['month_ret_pct']}); ay sonu {rep['position_end']}.",
             f"Ortalama görüş: beklenen 10g getiri %{rep['mean_E']}, belirsizlik {rep['mean_U']}; görüş üretemediği gün {rep['days_without_opinion']}/{rep['days']}.",
             f"İdeal yola göre yanlış gün: {wrong}/{len(tdays)}. Kural tabanı: {rep['rule_base_size']} kural.", ""]
        if mtr:
            L.append("## İşlemler")
            for t in mtr:
                L.append(f"- {t['date']} **{t['action']}** @ {t['price']} (E=%{t['E']}, U={t['U']})")
                for lab, mu, wt in t["rules"]:
                    L.append(f"    - tetiklenen kural: {lab} → beklenen %{mu} (güven {wt})")
        else:
            L.append("## İşlem yok")
        if ch["born"]:
            L += ["", "## Doğan kurallar"] + [f"- {b['label']} → beklenen %{b['mu']} (destek {b['support']} gün)" for b in ch["born"]]
        if ch["died"]:
            L += ["", "## Ölen kurallar"] + [f"- {d['label']} (güven {d['trust']}, {d['lifetime_days']} gün yaşadı)" for d in ch["died"]]
        L += ["", "## En güçlü kurallar (sahada sınanmış güvene göre)"]
        for R in rep["strongest_rules"]:
            L.append(f"- {R['label']} → beklenen %{R['mu']}, güven {R['trust']}, saha kanıtı {R['field_k']}")
        with open(os.path.join(outdir, "reports", f"AYLIK_{m.replace('-', '_')}.md"), "w") as fh:
            fh.write("\n".join(L))
    return dict(rows=rows, Z=Z, std=std, net=net, i0=i0, nav_hist=nav_hist, trades=trades, reports=reports)


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else HERE
    R = marathon(outdir)
    rows, nh, net, i0 = R["rows"], R["nav_hist"], R["net"], R["i0"]
    nav = [v for (_, v, _) in nh]
    first = rows[i0]
    passive = [100 * (1 - S.FEE) ** 2 * rows[i]["bid"] / first["ask"] for (i, _, _) in nh]
    P = [r["p06"] for r in rows]; c, u, ps, tn = 100.0, 0.0, 0, []
    for (i, _, _) in nh:
        r = rows[i]; sma = sum(P[i - 99:i + 1]) / 100
        if ps == 0 and P[i] > 1.01 * sma: u = c * (1 - S.FEE) / r["ask"]; c = 0; ps = 1
        elif ps == 1 and P[i] < 0.99 * sma: c = u * r["bid"] * (1 - S.FEE); u = 0; ps = 0
        tn.append(c + u * r["bid"] * (1 - S.FEE))
    opos, olog = oracle(rows, 0, len(rows) - 1)
    nav_at = lambda d: [v for (i, v, _) in nh if rows[i]["date"] <= d][-1]
    frozen = OrderedDict(model="TERAZI_V1", frozen_at_month="2025-12", features=S.FEATURES,
                         standardizer=R["std"].state(), constants=dict(H=T.H, gate_s=T.GATE_S, rho=T.RHO,
                             w_min=T.W_MIN, lam=T.LAM, buy_th=T.BUY_TH, sell_th=T.SELL_TH, fee=S.FEE,
                             max_gates=T.MAX_GATES, min_support=T.MIN_SUPPORT, trust_shrink=T.TRUST_SHRINK),
                         rules=[R_.to_dict() for R_ in sorted(net.rules, key=lambda x: -x.weight)],
                         note="2026 testi bu dosyayla, kod değiştirilmeden yapılır. 2026 verisi yüklenmedi.")
    json.dump(frozen, open(os.path.join(outdir, "TERAZI_V1_DONDURULMUS_MODEL.json"), "w"), indent=1, ensure_ascii=False)
    out = OrderedDict(period=[str(rows[i0]["date"]), str(rows[-1]["date"])], trading_days=len(nh),
                      terazi=dict(nav_2023=round(nav_at(date(2023, 12, 31)), 2), nav_2024=round(nav_at(date(2024, 12, 31)), 2),
                                  nav_final=round(nav[-1], 2), maxdd=round(mdd(nav), 2), trades=len(R["trades"]),
                                  trade_list=[(t["date"], t["action"], t["price"], t["E"]) for t in R["trades"]]),
                      benchmarks=dict(passive=round(passive[-1], 2), passive_maxdd=round(mdd(passive), 2),
                                      trend_sma100=round(tn[-1], 2), deneyim_v1_2=220.07, ideal=round(100 * math.exp(olog), 2)),
                      rule_base=dict(final_size=len(net.rules), total_born=net.audit["born"], total_died=net.audit["died"],
                                     days_without_opinion=net.audit["no_opinion"]),
                      strongest_rules=[R_.to_dict() for R_ in sorted(net.rules, key=lambda x: -x.weight)[:12]],
                      honesty=["Geliştirme dönemi sonucudur; 2026 testi ayrıdır.",
                               "Kurallar yalnız doğduktan sonraki günlerde kazandıkları güvenle oy kullanır.",
                               "Dukascopy BID/ASK + varsayımsal %0,8/yön; Türk bankası kotasyonu değildir."])
    json.dump(out, open(os.path.join(outdir, "TERAZI_V1_SONUC.json"), "w"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "strongest_rules"}, indent=1, ensure_ascii=False, default=str))
    print("\nEN GÜÇLÜ KURALLAR:")
    for R_ in out["strongest_rules"]:
        print(f"  {R_['label']:70s} → %{R_['mu']:+.2f}  güven {R_['trust']:+.2f}  saha {R_['field_k']}")


if __name__ == "__main__":
    main()
