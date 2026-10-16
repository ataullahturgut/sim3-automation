"""TERAZİ v3 maratonu: 2020-01→2022-12 ısıtma, 2023-01→2025-12 geliştirme koşusu.
Kullanım: python3 run_terazi_v3.py [çıktı_klasörü]
"""
import json, os, sys
from collections import OrderedDict
from datetime import date
import numpy as np
import terazi_v3 as T3
import terazi_v2 as T2
import deneyim_states as S
from deneyim_v1 import oracle

HERE = os.path.dirname(os.path.abspath(__file__))
START = date(2023, 1, 3)
WARM_END = date(2022, 12, 31)


def mdd(v):
    pk, m = -1e18, 0.0
    for x in v:
        pk = max(pk, x); m = max(m, 100 * (1 - x / pk))
    return m


def warmup_base_rate(brk, conf, warm_end_idx):
    """Ön kayıt 2.3: taban oran YALNIZ ısıtma döneminde onaylanmış etiketlerden."""
    vals = [brk[q] for q in range(len(brk))
            if brk[q] is not None and conf[q] is not None and conf[q] <= warm_end_idx]
    if not vals:
        raise RuntimeError("ısıtma döneminde onaylanmış kırılma etiketi yok")
    return float(np.mean(vals)), len(vals)


def marathon(outdir, theta=T3.THETA, m_break=T3.M_BREAK, exit_lam=T3.EXIT_LAM, mode="unified_sell", macro_gate=True, write=True):
    rows = S.load_rows(dev_only=True)
    raw, macro = S.build_states(rows)
    Z, std = S.standardize(raw)
    P06 = [r["p06"] for r in rows]
    lab, conf = T2.phase_labels(P06, theta)
    brk, bconf, tops = T3.break_labels(P06, theta, m_break)
    i0 = next(i for i, r in enumerate(rows) if r["date"] >= START)
    warm_end_idx = max(i for i, r in enumerate(rows) if r["date"] <= WARM_END)
    p0, n_p0 = warmup_base_rate(brk, bconf, warm_end_idx)

    net = T3.TeraziV3(p0, exit_lam, mode=mode, macro_gate=macro_gate)
    learned_lab, learned_brk = set(), set()
    if write:
        os.makedirs(os.path.join(outdir, "reports"), exist_ok=True)
    months = OrderedDict()
    for i in range(len(rows)):
        months.setdefault(str(rows[i]["date"])[:7], []).append(i)

    cash, units, pos = 100.0, 0.0, 0
    gcash, gunits = 100.0, 0.0
    nav_hist, gross_hist, trades, reports, daily = [], [], [], [], []
    for mo, idxs in months.items():
        trading = idxs[-1] >= i0
        nav0 = cash + units * rows[idxs[0] - 1]["bid"] if idxs[0] > i0 else 100.0
        mtr, days = [], []
        for i in idxs:
            if i < i0:
                continue
            r = rows[i]
            act, info = net.action(pos, Z[i], raw[i])
            if info["P"] is None:
                net.entry.audit["no_opinion"] += 1
            if act == "AL":
                units = cash * (1 - S.FEE) / r["ask"]; cash = 0.0; pos = 1
                gunits = gcash / r["p06"]; gcash = 0.0
                mtr.append(dict(date=str(r["date"]), action="AL", price=round(r["ask"], 2),
                                reason=info["reason"],
                                P=round(info["P"], 3), U=round(info["U"], 3),
                                rules=info["entry_top"]))
            elif act == "SAT":
                cash = units * r["bid"] * (1 - S.FEE); units = 0.0; pos = 0
                gcash = gunits * r["p06"]; gunits = 0.0
                mtr.append(dict(date=str(r["date"]), action="SAT", price=round(r["bid"], 2),
                                reason=info["reason"],
                                P=None if info["P"] is None else round(info["P"], 3),
                                Q=None if info["Q"] is None else round(info["Q"], 3),
                                UQ=None if info["UQ"] is None else round(info["UQ"], 3),
                                Pe=None if info["Pe"] is None else round(info["Pe"], 4),
                                Ue=None if info["Ue"] is None else round(info["Ue"], 4),
                                zq=None if info["zq"] is None else round(info["zq"], 3),
                                lam=info["lam"], macro=info["macro"],
                                rules=info["entry_top"], exit_rules=info["exit_top"]))
            rec = dict(date=str(r["date"]), gold=round(r["p06"], 2), pos=pos,
                       P=None if info["P"] is None else round(info["P"], 3),
                       U=None if info["U"] is None else round(info["U"], 3),
                       Q=None if info["Q"] is None else round(info["Q"], 3),
                       UQ=None if info["UQ"] is None else round(info["UQ"], 3),
                       Pe=None if info["Pe"] is None else round(info["Pe"], 4),
                       Ue=None if info["Ue"] is None else round(info["Ue"], 4),
                       zq=None if info["zq"] is None else round(info["zq"], 3),
                       macro=info["macro"], phase=lab[i], brk=brk[i])
            days.append(rec); daily.append(rec)
            nav_hist.append((i, cash + units * r["bid"] * (1 - S.FEE), pos))
            gross_hist.append((i, gcash + gunits * r["p06"]))
        trades += mtr
        i_end = idxs[-1]
        # ay sonuna kadar ONAYLANMIŞ etiketleri öğren — iki kanal, iki hedef
        for q in range(len(rows)):
            if q not in learned_lab and lab[q] is not None and conf[q] is not None and conf[q] <= i_end:
                net.entry.learn(q, Z[q], float(lab[q])); learned_lab.add(q)
            if q not in learned_brk and brk[q] is not None and bconf[q] is not None and bconf[q] <= i_end:
                net.exitb.learn(q, Z[q], float(brk[q])); learned_brk.add(q)
        okl, okb = sorted(learned_lab), sorted(learned_brk)
        che = net.entry.restructure(Z[okl], np.array([float(lab[q]) for q in okl]), now=i_end) \
            if okl else dict(born=[], died=[])
        chx = net.exitb.restructure(Z[okb], np.array([float(brk[q]) for q in okb]), now=i_end) \
            if okb else dict(born=[], died=[])
        if not trading or not write:
            continue
        tdays = [i for i in idxs if i >= i0]
        posmap = {q: p for (q, _, p) in nav_hist}
        agree = sum(1 for i in tdays if lab[i] is not None and lab[i] == posmap[i])
        rep = OrderedDict(
            month=mo, days=len(tdays),
            gold_change_pct=round(100 * (rows[i_end]["p06"] / rows[idxs[0] - 1]["p06"] - 1), 2),
            nav_start=round(nav0, 4), nav_end=round(nav_hist[-1][1], 4),
            month_ret_pct=round(100 * (nav_hist[-1][1] / nav0 - 1), 2),
            position_end="ALTIN" if pos else "NAKİT",
            phase_days_rising=sum(1 for i in tdays if lab[i] == 1),
            break_days=sum(1 for i in tdays if brk[i] == 1),
            position_matches_phase=f"{agree}/{len(tdays)}",
            mean_P=round(float(np.mean([x["P"] for x in days if x["P"] is not None])), 3)
            if any(x["P"] is not None for x in days) else None,
            mean_Q=round(float(np.mean([x["Q"] for x in days if x["Q"] is not None])), 3)
            if any(x["Q"] is not None for x in days) else None,
            exit_lambda=net.exit_lam, base_rate=round(net.p0, 4),
            macro_confirm_days=sum(1 for x in days if x["macro"]),
            trades=mtr,
            entry_base_size=len(net.entry.rules), exit_base_size=len(net.exitb.rules),
            entry_rules_born=che["born"], entry_rules_died=che["died"],
            exit_rules_born=chx["born"], exit_rules_died=chx["died"],
            strongest_exit_rules=[R.to_dict() for R in sorted(net.exitb.rules, key=lambda x: -x.weight)[:5]])
        reports.append(rep)
        json.dump(rep, open(os.path.join(outdir, "reports", f"AYLIK_{mo.replace('-', '_')}.json"), "w"),
                  indent=1, ensure_ascii=False)
        L = [f"# TERAZİ v3 (iki kanal) — {mo}", "",
             f"Altın %{rep['gold_change_pct']}; NAV {rep['nav_start']} → {rep['nav_end']} (%{rep['month_ret_pct']}); ay sonu {rep['position_end']}.",
             f"Gerçek evre: {rep['phase_days_rising']}/{rep['days']} gün yükselme; kırılma penceresi {rep['break_days']} gün. Pozisyon evreyle uyuştu: {rep['position_matches_phase']}.",
             f"Yavaş kanal ortalama P={rep['mean_P']}; hızlı kanal ortalama Q={rep['mean_Q']} (z-testi λ={rep['exit_lambda']}, taban oran {rep['base_rate']}); makro onaylı gün {rep['macro_confirm_days']}/{rep['days']}.",
             f"Kural tabanları: giriş {rep['entry_base_size']}, çıkış {rep['exit_base_size']}.", ""]
        if mtr:
            L.append("## İşlemler")
            for t in mtr:
                extra = ""
                if t["action"] == "SAT" and t.get("Q") is not None:
                    extra = f", Q(kırılma)={t['Q']}, belirsizlik={t['UQ']}, z={t['zq']} (λ={t['lam']}), makro={t['macro']}"
                L.append(f"- {t['date']} **{t['action']}** @ {t['price']} — {t['reason']}{extra}")
                for lb, mu, wt in (t.get("rules") or []):
                    L.append(f"    - {lb} → {mu} (güven {wt})")
        else:
            L.append("## İşlem yok")
        if chx["born"]:
            L += ["", "## Doğan çıkış kuralları"] + [
                f"- {b['label']} → P(kırılma)={b['p_break']} (destek {b['support']}, kanıt z={b['evidence_z']})"
                for b in chx["born"]]
        if chx["died"]:
            L += ["", "## Ölen çıkış kuralları"] + [
                f"- {d['label']} (güven {d['trust']}, {d['lifetime_days']} gün)" for d in chx["died"]]
        L += ["", "## En güçlü çıkış kuralları"] + [
            f"- {R['label']} → P(kırılma)={R['p_break']}, güven {R['trust']}, saha {R['field_k']}"
            for R in rep["strongest_exit_rules"]]
        with open(os.path.join(outdir, "reports", f"AYLIK_{mo.replace('-', '_')}.md"), "w") as fh:
            fh.write("\n".join(L))
    return dict(rows=rows, raw=raw, Z=Z, std=std, net=net, i0=i0, p0=p0, n_p0=n_p0,
                nav_hist=nav_hist, gross_hist=gross_hist, trades=trades, reports=reports,
                lab=lab, conf=conf, brk=brk, bconf=bconf, tops=tops, daily=daily,
                theta=theta, m_break=m_break, exit_lam=exit_lam, mode=mode, macro_gate=macro_gate)


def gate_census(rules):
    cnt = {}
    for R in rules:
        for g in R.gates:
            f = S.FEATURES[g[0]]
            cnt[f] = cnt.get(f, 0) + 1
    tot = sum(cnt.values())
    return cnt, tot


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else HERE
    A = marathon(outdir)
    rows, nav = A["rows"], A["nav_hist"]
    i0 = A["i0"]
    print(f"taban oran p0 = {A['p0']:.4f}  ({A['n_p0']} ısıtma etiketinden)")
    print(f"çıkış testi: (Q−p0)/U_Q > {A['exit_lam']}")
    net_final = nav[-1][1]
    gross_final = A["gross_hist"][-1][1]
    print(f"\nv3 net NAV  {net_final:.2f}   brüt {gross_final:.2f}   işlem {len(A['trades'])}")
    print(f"maks düşüş  %{mdd([v for _, v, _ in nav]):.2f}")
    print("\nişlem defteri:")
    for t in A["trades"]:
        print(f"  {t['date']} {t['action']:3} @ {t['price']:8.2f}  — {t['reason']}")
    cnt, tot = gate_census(A["net"].exitb.rules)
    print(f"\nH1 — çıkış tabanı kapı sayımı ({len(A['net'].exitb.rules)} kural, {tot} kapı):")
    for k, v in sorted(cnt.items(), key=lambda x: -x[1]):
        print(f"   {v:3d}  %{100 * v / tot:5.2f}  {k}")
    s1 = 100 * cnt.get("g_r1", 0) / tot
    s15 = 100 * (cnt.get("g_r1", 0) + cnt.get("g_r5", 0)) / tot
    print(f"\n  H1a g_r1 payı       = %{s1:.2f}   (hedef ≥ %5;   v2: %0,60)  → {'TUTTU' if s1 >= 5 else 'TUTMADI'}")
    print(f"  H1b g_r1+g_r5 payı  = %{s15:.2f}   (hedef ≥ %30;  v2: %16,17) → {'TUTTU' if s15 >= 30 else 'TUTMADI'}")
    json.dump(dict(p0=A["p0"], n_p0=A["n_p0"], exit_lambda=A["exit_lam"],
                   net_nav=round(net_final, 4), gross_nav=round(gross_final, 4),
                   max_drawdown_pct=round(mdd([v for _, v, _ in nav]), 2),
                   trades=A["trades"], gate_census=cnt, gate_total=tot,
                   h1a_g_r1_share_pct=round(s1, 2), h1b_fast_share_pct=round(s15, 2),
                   exit_rules=[R.to_dict() for R in sorted(A["net"].exitb.rules, key=lambda x: -x.weight)],
                   entry_rules=[R.to_dict() for R in sorted(A["net"].entry.rules, key=lambda x: -x.weight)],
                   standardizer=A["std"].state() if hasattr(A["std"], "state") else None,
                   constants=dict(theta=A["theta"], m_break=A["m_break"], exit_lam=A["exit_lam"],
                                  lam=T3.LAM, gate_s=T3.GATE_S, rho=T3.RHO, fee=S.FEE)),
              open(os.path.join(outdir, "TERAZI_V3_DONDURULMUS_MODEL.json"), "w"),
              indent=1, ensure_ascii=False, default=str)
    json.dump(A["daily"], open(os.path.join(outdir, "TERAZI_V3_GUNLUK.json"), "w"),
              indent=0, ensure_ascii=False)
    print(f"\nyazıldı: {outdir}/TERAZI_V3_DONDURULMUS_MODEL.json")


if __name__ == "__main__":
    main()
