"""TERAZİ v2 maratonu: 2020-01→2022-12 ısıtma, 2023-01→2025-12 işlem. Aylık rapor, dondurma.
Kullanım: python3 run_terazi_v2.py [çıktı_klasörü] [theta]
"""
import json, math, os, sys
from collections import OrderedDict
from datetime import date
import numpy as np
import terazi_v2 as T
import deneyim_states as S
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "claude_deneyim_v1"))
from deneyim_v1 import oracle

HERE = os.path.dirname(os.path.abspath(__file__))
START = date(2023, 1, 3)


def mdd(v):
    pk, m = -1e18, 0.0
    for x in v: pk = max(pk, x); m = max(m, 100 * (1 - x / pk))
    return m


def marathon(outdir, theta=T.THETA, write=True):
    rows = S.load_rows(dev_only=True)
    raw, macro = S.build_states(rows)
    Z, std = S.standardize(raw)
    P06 = [r["p06"] for r in rows]
    lab, conf = T.phase_labels(P06, theta)
    i0 = next(i for i, r in enumerate(rows) if r["date"] >= START)
    net = T.TeraziV2()
    learned = set()
    if write:
        os.makedirs(os.path.join(outdir, "reports"), exist_ok=True)
    months = OrderedDict()
    for i in range(len(rows)):
        months.setdefault(str(rows[i]["date"])[:7], []).append(i)
    cash, units, pos = 100.0, 0.0, 0
    gcash, gunits, gpos = 100.0, 0.0, 0          # brüt (masrafsız) muhasebe
    nav_hist, gross_hist, trades, reports = [], [], [], []
    for m, idxs in months.items():
        trading = idxs[-1] >= i0
        nav0 = cash + units * rows[idxs[0] - 1]["bid"] if idxs[0] > i0 else 100.0
        mtr, days = [], []
        for i in idxs:
            if i < i0:
                continue
            r = rows[i]
            act, d = net.action(pos, Z[i])
            if d is None:
                net.audit["no_opinion"] += 1
            if act == "AL":
                units = cash * (1 - S.FEE) / r["ask"]; cash = 0.0; pos = 1
                gunits = gcash / r["p06"]; gcash = 0.0; gpos = 1
                mtr.append(dict(date=str(r["date"]), action="AL", price=round(r["ask"], 2),
                                P=round(d["P"], 3), U=round(d["U"], 3), rules=d["top"]))
            elif act == "SAT":
                cash = units * r["bid"] * (1 - S.FEE); units = 0.0; pos = 0
                gcash = gunits * r["p06"]; gunits = 0.0; gpos = 0
                mtr.append(dict(date=str(r["date"]), action="SAT", price=round(r["bid"], 2),
                                P=round(d["P"], 3), U=round(d["U"], 3), rules=d["top"]))
            days.append(dict(date=str(r["date"]), P=None if d is None else round(d["P"], 3),
                             U=None if d is None else round(d["U"], 3), pos=pos,
                             phase=lab[i], phase_known=conf[i] is not None and conf[i] <= i))
            nav_hist.append((i, cash + units * r["bid"] * (1 - S.FEE), pos))
            gross_hist.append((i, gcash + gunits * rows[i]["p06"]))
        trades += mtr
        i_end = idxs[-1]
        # ay sonuna kadar ONAYLANMIŞ etiketleri öğren
        for q in range(len(rows)):
            if q in learned or lab[q] is None or conf[q] is None or conf[q] > i_end:
                continue
            net.learn(q, Z[q], float(lab[q])); learned.add(q)
        ok = sorted(learned)
        ch = net.restructure(Z[ok], np.array([float(lab[q]) for q in ok]), now=i_end) if ok else dict(born=[], died=[])
        if not trading or not write:
            continue
        tdays = [i for i in idxs if i >= i0]
        posmap = {q: p for (q, _, p) in nav_hist}
        agree = sum(1 for i in tdays if lab[i] is not None and lab[i] == posmap[i])
        rep = OrderedDict(month=m, days=len(tdays),
                          gold_change_pct=round(100 * (rows[i_end]["p06"] / rows[idxs[0] - 1]["p06"] - 1), 2),
                          nav_start=round(nav0, 4), nav_end=round(nav_hist[-1][1], 4),
                          month_ret_pct=round(100 * (nav_hist[-1][1] / nav0 - 1), 2),
                          position_end="ALTIN" if pos else "NAKİT",
                          phase_days_rising=sum(1 for i in tdays if lab[i] == 1),
                          position_matches_phase=f"{agree}/{len(tdays)}",
                          mean_P=round(float(np.mean([x["P"] for x in days if x["P"] is not None])), 3) if any(x["P"] is not None for x in days) else None,
                          mean_U=round(float(np.mean([x["U"] for x in days if x["U"] is not None])), 3) if any(x["U"] is not None for x in days) else None,
                          days_without_opinion=sum(1 for x in days if x["P"] is None),
                          trades=mtr, rule_base_size=len(net.rules), rules_born=ch["born"], rules_died=ch["died"],
                          labels_learned_total=len(learned),
                          strongest_rules=[R.to_dict() for R in sorted(net.rules, key=lambda x: -x.weight)[:5]])
        reports.append(rep)
        json.dump(rep, open(os.path.join(outdir, "reports", f"AYLIK_{m.replace('-', '_')}.json"), "w"), indent=1, ensure_ascii=False)
        L = [f"# TERAZİ v2 (evre modeli) — {m}", "",
             f"Altın %{rep['gold_change_pct']}; NAV {rep['nav_start']} → {rep['nav_end']} (%{rep['month_ret_pct']}); ay sonu {rep['position_end']}.",
             f"Gerçek evre: {rep['phase_days_rising']}/{rep['days']} gün yükselme. Modelin pozisyonu evreyle uyuştu: {rep['position_matches_phase']}.",
             f"Modelin yükselme evresi olasılığı: ortalama {rep['mean_P']} (belirsizlik {rep['mean_U']}); görüşsüz gün {rep['days_without_opinion']}/{rep['days']}.",
             f"Kural tabanı {rep['rule_base_size']}; öğrenilmiş onaylı etiket {rep['labels_learned_total']}.", ""]
        if mtr:
            L.append("## İşlemler")
            for t in mtr:
                L.append(f"- {t['date']} **{t['action']}** @ {t['price']} (P(yükselme)={t['P']}, belirsizlik={t['U']})")
                for lb, mu, wt in t["rules"]:
                    L.append(f"    - {lb} → P(yükselme)={mu} (güven {wt})")
        else:
            L.append("## İşlem yok")
        if ch["born"]:
            L += ["", "## Doğan kurallar"] + [f"- {b['label']} → P(yükselme)={b['p_rising']} (destek {b['support']}, kanıt z={b['evidence_z']}, doğum güveni {b['birth_credibility']})" for b in ch["born"]]
        if ch["died"]:
            L += ["", "## Ölen kurallar"] + [f"- {d['label']} (güven {d['trust']}, {d['lifetime_days']} gün)" for d in ch["died"]]
        L += ["", "## En güçlü kurallar"] + [f"- {R['label']} → P(yükselme)={R['p_rising']}, güven {R['trust']}, saha {R['field_k']}" for R in rep["strongest_rules"]]
        with open(os.path.join(outdir, "reports", f"AYLIK_{m.replace('-', '_')}.md"), "w") as fh:
            fh.write("\n".join(L))
    return dict(rows=rows, Z=Z, std=std, net=net, i0=i0, nav_hist=nav_hist, gross_hist=gross_hist,
                trades=trades, reports=reports, lab=lab, conf=conf, theta=theta)


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else HERE
    R = marathon(outdir)
    rows, nh, gh, net, i0 = R["rows"], R["nav_hist"], R["gross_hist"], R["net"], R["i0"]
    nav = [v for (_, v, _) in nh]; gross = [v for (_, v) in gh]
    first = rows[i0]
    passive = [100 * (1 - S.FEE) ** 2 * rows[i]["bid"] / first["ask"] for (i, _, _) in nh]
    P = [r["p06"] for r in rows]; c, u, ps, tn = 100.0, 0.0, 0, []
    for (i, _, _) in nh:
        r = rows[i]; sma = sum(P[i - 99:i + 1]) / 100
        if ps == 0 and P[i] > 1.01 * sma: u = c * (1 - S.FEE) / r["ask"]; c = 0; ps = 1
        elif ps == 1 and P[i] < 0.99 * sma: c = u * r["bid"] * (1 - S.FEE); u = 0; ps = 0
        tn.append(c + u * r["bid"] * (1 - S.FEE))
    _, olog = oracle(rows, 0, len(rows) - 1)
    nav_at = lambda d: [v for (i, v, _) in nh if rows[i]["date"] <= d][-1]
    lab = R["lab"]; tdays = [i for (i, _, _) in nh]
    posmap = {q: p for (q, _, p) in nh}
    agree = sum(1 for i in tdays if lab[i] is not None and lab[i] == posmap[i])
    sens = {}
    for th in (3.0, 8.0):
        Rx = marathon(outdir, theta=th, write=False)
        sens[f"theta_{int(th)}pct"] = dict(nav_final=round(Rx["nav_hist"][-1][1], 2), trades=len(Rx["trades"]))
    frozen = OrderedDict(model="TERAZI_V2_EVRE", frozen_at_month="2025-12", theta_pct=R["theta"],
                         features=S.FEATURES, standardizer=R["std"].state(),
                         constants=dict(gate_s=T.GATE_S, rho=T.RHO, w_min=T.W_MIN, lam=T.LAM,
                                        prior_w=T.PRIOR_W, prior_p=T.PRIOR_P, trust_shrink=T.TRUST_SHRINK,
                                        tau=T.TAU, admit_margin=T.ADMIT_MARGIN, max_gates=T.MAX_GATES,
                                        min_support=T.MIN_SUPPORT, fee_in_decision=False, fee_in_nav=S.FEE),
                         rules=[R_.to_dict() for R_ in sorted(net.rules, key=lambda x: -x.weight)],
                         note="2026 testi bu dosyayla, kod değiştirilmeden yapılır. 2026 verisi yüklenmedi.")
    json.dump(frozen, open(os.path.join(outdir, "TERAZI_V2_DONDURULMUS_MODEL.json"), "w"), indent=1, ensure_ascii=False)
    out = OrderedDict(period=[str(rows[i0]["date"]), str(rows[-1]["date"])], trading_days=len(nh),
                      terazi_v2=dict(nav_2023=round(nav_at(date(2023, 12, 31)), 2), nav_2024=round(nav_at(date(2024, 12, 31)), 2),
                                     nav_final_net=round(nav[-1], 2), nav_final_gross_no_fee=round(gross[-1], 2),
                                     maxdd=round(mdd(nav), 2), trades=len(R["trades"]),
                                     position_matches_phase=f"{agree}/{len(tdays)}",
                                     trade_list=[(t["date"], t["action"], t["price"], t["P"]) for t in R["trades"]]),
                      benchmarks=dict(passive=round(passive[-1], 2), passive_maxdd=round(mdd(passive), 2),
                                      trend_sma100=round(tn[-1], 2), ideal=round(100 * math.exp(olog), 2),
                                      terazi_v1_hard=131.10, terazi_v1_1_fuzzy=153.92, deneyim_v1_2=220.07),
                      zigzag_sensitivity=sens,
                      rule_base=dict(final_size=len(net.rules), total_born=net.audit["born"], total_died=net.audit["died"],
                                     days_without_opinion=net.audit["no_opinion"]),
                      strongest_rules=[R_.to_dict() for R_ in sorted(net.rules, key=lambda x: -x.weight)[:12]],
                      honesty=["Geliştirme dönemi kaydıdır; v1→v1.1→v2 zinciri bu döneme bakılarak değişti, kanıt değildir.",
                               "Masraf kararda kullanılmadı; NAV'da %0,8/yön tam uygulandı (brüt NAV de verildi).",
                               "Evre etiketi geriye dönüktür; yalnız onaylanmış bacaklar öğrenildi.",
                               "Tek gerçek sınav 2026 testidir."])
    json.dump(out, open(os.path.join(outdir, "TERAZI_V2_SONUC.json"), "w"), indent=1, ensure_ascii=False, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "strongest_rules"}, indent=1, ensure_ascii=False, default=str))
    print("\nEN GÜÇLÜ KURALLAR (P=yükselme evresi olasılığı):")
    for R_ in out["strongest_rules"]:
        print(f"  {R_['label'][:64]:64s} P={R_['p_rising']:.2f}  güven {R_['trust']:+.2f}  saha {R_['field_k']}")


if __name__ == "__main__":
    main()
