"""TERAZİ v4 maratonu: 2020-01→2022-12 ısıtma, 2023-01-03→2025-12-31 geliştirme koşusu.
Kullanım: python3 run_terazi_v4.py [çıktı_klasörü]
"""
import json, math, os, sys
from collections import OrderedDict
from datetime import date
import numpy as np
import terazi_v4 as T4
import terazi_v2 as T2
import deneyim_states as S
from deneyim_v1 import oracle, legs_from_positions

HERE = os.path.dirname(os.path.abspath(__file__))
START = date(2023, 1, 3)


def mdd(v):
    pk, m = -1e18, 0.0
    for x in v:
        pk = max(pk, x); m = max(m, 100 * (1 - x / pk))
    return m


def marathon(outdir, net_min=T4.NET_MIN, write=True):
    rows = S.load_rows(dev_only=True)
    raw, macro = S.build_states(rows)
    Z, std = S.standardize(raw)
    i0 = next(i for i, r in enumerate(rows) if r["date"] >= START)
    net = T4.Terazi()
    if write:
        os.makedirs(os.path.join(outdir, "reports"), exist_ok=True)
    months = OrderedDict()
    for i in range(len(rows)):
        months.setdefault(str(rows[i]["date"])[:7], []).append(i)

    cash, units, pos = 100.0, 0.0, 0
    gcash, gunits = 100.0, 0.0
    nav_hist, gross_hist, trades, reports, daily = [], [], [], [], []
    learned = {}                       # gün → öğrenilmiş etiket (bir kez, kesin)
    for mo, idxs in months.items():
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
                gunits = gcash / r["p06"]; gcash = 0.0
                mtr.append(dict(date=str(r["date"]), action="AL", price=round(r["ask"], 2),
                                P=round(d["P"], 3), U=round(d["U"], 3), rules=d["top"]))
            elif act == "SAT":
                cash = units * r["bid"] * (1 - S.FEE); units = 0.0; pos = 0
                gcash = gunits * r["p06"]; gunits = 0.0
                mtr.append(dict(date=str(r["date"]), action="SAT", price=round(r["bid"], 2),
                                P=round(d["P"], 3), U=round(d["U"], 3), rules=d["top"]))
            rec = dict(date=str(r["date"]), gold=round(r["p06"], 2), pos=pos,
                       P=None if d is None else round(d["P"], 3),
                       U=None if d is None else round(d["U"], 3),
                       z=None if (d is None or "z" not in d) else round(d["z"], 3),
                       p0=round(net.p0, 4), target=learned.get(i))
            days.append(rec); daily.append(rec)
            nav_hist.append((i, cash + units * r["bid"] * (1 - S.FEE), pos))
            gross_hist.append((i, gcash + gunits * r["p06"]))
        trades += mtr
        i_end = idxs[-1]

        # --- YUVARLANAN İDEAL: yalnız ay sonuna kadarki fiyatlarla ---
        lab, closed, last_known = T4.target_labels(rows, i_end, net_min)
        fresh = []
        for q, y in lab.items():
            if q not in learned:               # bir kez öğrenilen yeniden etiketlenmez
                learned[q] = y; fresh.append(q)
        for q in fresh:
            net.learn(q, Z[q], float(learned[q]))
        ok = sorted(learned)
        if ok:                           # ek-1: taban oran yalnız ÖĞRENİLMİŞ etiketlerden
            net.p0 = float(np.mean([learned[q] for q in ok]))
        ch = net.restructure(Z[ok], np.array([float(learned[q]) for q in ok]), now=i_end) \
            if len(ok) >= T4.MIN_SUPPORT else dict(born=[], died=[])
        if not trading or not write:
            continue
        tdays = [i for i in idxs if i >= i0]
        posmap = {q: p for (q, _, p) in nav_hist}
        known = [i for i in tdays if i in learned]
        agree = sum(1 for i in known if learned[i] == posmap[i])
        rep = OrderedDict(
            month=mo, days=len(tdays),
            gold_change_pct=round(100 * (rows[i_end]["p06"] / rows[idxs[0] - 1]["p06"] - 1), 2),
            nav_start=round(nav0, 4), nav_end=round(nav_hist[-1][1], 4),
            month_ret_pct=round(100 * (nav_hist[-1][1] / nav0 - 1), 2),
            position_end="ALTIN" if pos else "NAKİT",
            target_days_in=sum(1 for i in tdays if learned.get(i) == 1),
            target_known=len(known),
            position_matches_target=f"{agree}/{len(known)}" if known else "—",
            mean_P=round(float(np.mean([x["P"] for x in days if x["P"] is not None])), 3)
            if any(x["P"] is not None for x in days) else None,
            mean_U=round(float(np.mean([x["U"] for x in days if x["U"] is not None])), 3)
            if any(x["U"] is not None for x in days) else None,
            base_rate=round(net.p0, 4),
            days_without_opinion=sum(1 for x in days if x["P"] is None),
            labels_learned_total=len(learned),
            trades=mtr, rule_base_size=len(net.rules),
            rules_born=ch["born"], rules_died=ch["died"],
            strongest_rules=[R.to_dict() for R in sorted(net.rules, key=lambda x: -x.weight)[:5]])
        reports.append(rep)
        json.dump(rep, open(os.path.join(outdir, "reports", f"AYLIK_{mo.replace('-', '_')}.json"), "w"),
                  indent=1, ensure_ascii=False)
        L = [f"# TERAZİ v4 (kullanıcı seçimli hedef) — {mo}", "",
             f"Altın %{rep['gold_change_pct']}; NAV {rep['nav_start']} → {rep['nav_end']} (%{rep['month_ret_pct']}); ay sonu {rep['position_end']}.",
             f"Hedef: {rep['target_days_in']}/{rep['days']} gün ALTINDA olmalıydı. Pozisyon hedefle uyuştu: {rep['position_matches_target']}.",
             f"Ortalama P(altında ol)={rep['mean_P']} (belirsizlik {rep['mean_U']}); görüşsüz gün {rep['days_without_opinion']}/{rep['days']}.",
             f"Kural tabanı {rep['rule_base_size']}; öğrenilmiş etiket {rep['labels_learned_total']}.", ""]
        if mtr:
            L.append("## İşlemler")
            for t in mtr:
                L.append(f"- {t['date']} **{t['action']}** @ {t['price']} (P={t['P']}, belirsizlik={t['U']})")
                for lb, mu, wt in t["rules"]:
                    L.append(f"    - {lb} → P(altında)={mu} (güven {wt})")
        else:
            L.append("## İşlem yok")
        if ch["born"]:
            L += ["", "## Doğan kurallar"] + [
                f"- {b['label']} → P(altında)={b['p_in']} (destek {b['support']}, kanıt z={b['evidence_z']})"
                for b in ch["born"]]
        if ch["died"]:
            L += ["", "## Ölen kurallar"] + [
                f"- {d['label']} (güven {d['trust']}, {d['lifetime_days']} gün)" for d in ch["died"]]
        L += ["", "## En güçlü kurallar"] + [
            f"- {R['label']} → P(altında)={R['p_rising']}, güven {R['trust']}, saha {R['field_k']}"
            for R in rep["strongest_rules"]]
        with open(os.path.join(outdir, "reports", f"AYLIK_{mo.replace('-', '_')}.md"), "w") as fh:
            fh.write("\n".join(L))
    return dict(rows=rows, raw=raw, Z=Z, std=std, net=net, i0=i0, nav_hist=nav_hist,
                gross_hist=gross_hist, trades=trades, reports=reports, daily=daily,
                learned=learned, net_min=net_min)


def final_target(rows, i0, i1, net_min):
    """Tam dönemin hedefi — yalnız RAPORLAMA için (karar vermede kullanılmaz)."""
    pos, _ = oracle(rows, i0, i1)
    legs = legs_from_positions(rows, i0, pos)
    keep = [L for L in legs if (L["net_pct"] or 0) >= net_min]
    tgt = {i: 0 for i in range(i0, i1 + 1)}
    for L in keep:
        for q in range(L["entry_i"], (L["exit_i"] if L["exit_i"] is not None else i1)):
            tgt[q] = 1
    cash, units = 100.0, 0.0
    for i in range(i0, i1 + 1):
        r = rows[i]; prev = tgt[i - 1] if i > i0 else 0
        if tgt[i] == 1 and prev == 0: units = cash * (1 - S.FEE) / r["ask"]; cash = 0.0
        if tgt[i] == 0 and prev == 1: cash = units * r["bid"] * (1 - S.FEE); units = 0.0
    nav = cash + units * rows[i1]["bid"] * (1 - S.FEE)
    return tgt, keep, nav


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else HERE
    A = marathon(outdir)
    rows, nav = A["rows"], A["nav_hist"]
    i0 = A["i0"]; i1 = len(rows) - 1
    d2i = {str(r["date"]): i for i, r in enumerate(rows)}
    tgt, keep, tnav = final_target(rows, i0, i1, A["net_min"])
    posmap = {q: p for (q, _, p) in nav}
    agree = sum(1 for i in range(i0, i1 + 1) if tgt[i] == posmap.get(i, 0))
    net_final, gross_final = nav[-1][1], A["gross_hist"][-1][1]
    passive = 100 * (1 - S.FEE) / rows[i0]["ask"] * rows[i1]["bid"] * (1 - S.FEE)
    first_exit = next((t["date"] for t in A["trades"] if t["action"] == "SAT"), None)
    res = OrderedDict(
        net_nav=round(net_final, 2), gross_nav=round(gross_final, 2),
        trades=len(A["trades"]), max_drawdown_pct=round(mdd([v for _, v, _ in nav]), 2),
        target_nav=round(tnav, 2), target_legs=len(keep),
        passive=round(passive, 2),
        agree_pct=round(100 * agree / (i1 - i0 + 1), 1),
        first_exit=first_exit,
        days_in_gold_pct=round(100 * sum(posmap.get(i, 0) for i in range(i0, i1 + 1)) / (i1 - i0 + 1), 1),
        base_rate=round(A["net"].p0, 4),
        no_opinion_days=A["net"].audit["no_opinion"],
        rules_born=A["net"].audit["born"], rules_died=A["net"].audit["died"])
    print("\n=== TERAZİ v4 SONUÇ (geliştirme kaydı, kanıt değil) ===")
    for k, v in res.items():
        print(f"  {k:24} {v}")
    print("\n  GEÇME ÖLÇÜTLERİ")
    g = OrderedDict()
    g["G1 net NAV ≥ 230,82"] = (net_final >= 230.82, f"{net_final:.2f}")
    g["G2 işlem 20–60"] = (20 <= len(A["trades"]) <= 60, str(len(A["trades"])))
    g["G3 hedefle uyum ≥ %65"] = (res["agree_pct"] >= 65, f"%{res['agree_pct']}")
    g["G5 ilk çıkış < 2023-02-02"] = (bool(first_exit) and first_exit < "2023-02-02", str(first_exit))
    g["G6 maks düşüş ≤ %11,67"] = (res["max_drawdown_pct"] <= 11.67, f"%{res['max_drawdown_pct']}")
    for k, (ok, v) in g.items():
        print(f"    {k:32} {v:>14}  {'GEÇTİ' if ok else 'GEÇMEDİ'}")
    print("\n  işlem defteri:")
    for t in A["trades"]:
        print(f"    {t['date']} {t['action']:3} @ {t['price']:8.2f}  (P={t['P']}, U={t['U']})")
    json.dump(dict(result=res, criteria={k: v[0] for k, v in g.items()},
                   trades=A["trades"], net_min=A["net_min"],
                   rules=[R.to_dict() for R in sorted(A["net"].rules, key=lambda x: -x.weight)],
                   constants=dict(net_min=A["net_min"], lam=T4.LAM, gate_s=T4.GATE_S,
                                  rho=T4.RHO, fee=S.FEE, max_rules=T4.MAX_RULES)),
              open(os.path.join(outdir, "TERAZI_V4_DONDURULMUS_MODEL.json"), "w"),
              indent=1, ensure_ascii=False, default=str)
    json.dump(A["daily"], open(os.path.join(outdir, "TERAZI_V4_GUNLUK.json"), "w"),
              indent=0, ensure_ascii=False)
    print(f"\n  yazıldı: {outdir}/TERAZI_V4_DONDURULMUS_MODEL.json")


if __name__ == "__main__":
    main()
