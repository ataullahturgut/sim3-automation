"""TERAZİ v5 maratonu. Kullanım: python3 run_terazi_v5.py [month|week] [K]"""
import json, os, sys
from collections import OrderedDict
from datetime import date
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("claude_terazi_v4", "claude_terazi_v2", "claude_deneyim_v1"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
sys.path.insert(0, HERE)
import deneyim_states as S
import hedef_v5 as H
import terazi_v5 as T5

START = date(2023, 1, 3)
LAM = T5.T4.LAM
MIN_SUPPORT = T5.T4.MIN_SUPPORT


def mdd(v):
    pk, m = -1e18, 0.0
    for x in v:
        pk = max(pk, x); m = max(m, 100 * (1 - x / pk))
    return m


def period_key(d, period):
    if period == "week":
        y, w, _ = d.isocalendar()
        return f"{y}-W{w:02d}"
    return str(d)[:7]


def forget_mean(ys, rho=None):
    """Ek-4: kurallarla aynı unutma hızıyla taban oran. ys kronolojik sırada."""
    rho = T5.T2.RHO if rho is None else rho
    ys = np.asarray(ys, dtype=float)
    w = rho ** np.arange(len(ys) - 1, -1, -1, dtype=float)
    return float((w * ys).sum() / w.sum())


def marathon(period="month", k=H.K_LAG, relabel=False, variant=None, forget=False):
    rows = S.load_rows(dev_only=True)
    raw, _ = S.build_states(rows)
    Z, _ = S.standardize(raw)
    i0 = next(i for i, r in enumerate(rows) if r["date"] >= START)
    if variant is None:
        net = T5.Terazi5()
    else:
        net = T5.Terazi6(strong=variant in ("A", "C"), stable=variant in ("B", "C"))
    groups = OrderedDict()
    for i in range(len(rows)):
        groups.setdefault(period_key(rows[i]["date"], period), []).append(i)
    cash, units, pos = 100.0, 0.0, 0
    gcash, gunits = 100.0, 0.0
    nav_hist, gross_hist, trades, daily = [], [], [], []
    learned = {}
    for g, idxs in groups.items():
        for i in idxs:
            if i < i0:
                continue
            r = rows[i]
            d = net.decide(Z[i])
            act, zs = "HOLD", None
            if d is not None and d["U"] > 0:
                zs = (d["P"] - net.p0) / d["U"]
                if pos == 0 and zs > LAM:
                    act = "AL"
                elif pos == 1 and -zs > LAM:
                    act = "SAT"
            if act == "AL":
                units = cash * (1 - S.FEE) / r["ask"]; cash = 0.0; pos = 1
                gunits = gcash / r["p06"]; gcash = 0.0
                trades.append(dict(date=str(r["date"]), action="AL", price=round(r["ask"], 2),
                                   P=round(d["P"], 3), z=round(zs, 3)))
            elif act == "SAT":
                cash = units * r["bid"] * (1 - S.FEE); units = 0.0; pos = 0
                gcash = gunits * r["p06"]; gunits = 0.0
                trades.append(dict(date=str(r["date"]), action="SAT", price=round(r["bid"], 2),
                                   P=round(d["P"], 3), z=round(zs, 3)))
            daily.append(dict(date=str(r["date"]), gold=round(r["p06"], 2), pos=pos,
                              P=None if d is None else round(d["P"], 4),
                              z=None if zs is None else round(zs, 3), p0=round(net.p0, 4)))
            nav_hist.append((i, cash + units * r["bid"] * (1 - S.FEE), pos))
            gross_hist.append((i, gcash + gunits * r["p06"]))
        i_end = idxs[-1]
        lab, _, _ = H.target_labels(rows, i_end, k)
        if relabel:                                   # ek-1: güncel hedefle yeniden etiketle
            learned = dict(lab)
            ok = sorted(learned)
            if not ok:
                continue
            ys_ = [learned[q] for q in ok]
            net.p0 = forget_mean(ys_) if forget else float(np.mean(ys_))
            Zm = Z[ok]; ym = np.array([float(learned[q]) for q in ok])
            T5.rebuild_rules(net, Zm, ym, ok)
            if variant is not None:
                net.years = [rows[q]["date"].year for q in ok]
            if len(ok) >= MIN_SUPPORT:
                net.restructure(Zm, ym, now=i_end)
            continue
        fresh = [q for q in lab if q not in learned]
        for q in fresh:
            learned[q] = lab[q]
        ok = sorted(learned)
        if ok:
            net.p0 = float(np.mean([learned[q] for q in ok]))
        for q in fresh:
            net.learn(q, Z[q], float(learned[q]))
        if len(ok) >= MIN_SUPPORT:
            net.restructure(Z[ok], np.array([float(learned[q]) for q in ok]), now=i_end)
    return dict(rows=rows, Z=Z, net=net, i0=i0, nav_hist=nav_hist, gross_hist=gross_hist,
                trades=trades, daily=daily, learned=learned, period=period, k=k, relabel=relabel, variant=variant, forget=forget)


def evaluate(A):
    rows, i0 = A["rows"], A["i0"]; i1 = len(rows) - 1
    moves = H.robust_moves(rows, i0, i1, A["k"])
    tgt = {i: 0 for i in range(i0, i1 + 1)}
    for b, t, _ in moves:
        for q in range(b, t):
            tgt[q] = 1
    ceiling = 100.0
    for _, _, p in moves:
        ceiling *= 1 + p / 100
    pm = {q: p for q, _, p in A["nav_hist"]}
    agree = 100 * sum(1 for i in range(i0, i1 + 1) if tgt[i] == pm[i]) / (i1 - i0 + 1)
    d2i = {str(r["date"]): i for i, r in enumerate(rows)}
    jan = [i for i in range(d2i["2023-01-03"], d2i["2023-01-26"])]
    jan_in = 100 * sum(pm[i] for i in jan) / len(jan)
    nav = A["nav_hist"][-1][1]
    passive = 100 * (1 - S.FEE) / rows[i0]["ask"] * rows[i1]["bid"] * (1 - S.FEE)
    dd = mdd([v for _, v, _ in A["nav_hist"]])
    # hedefin hareketleri: model içeride miydi
    legs = []
    for b, t, p in moves:
        ds = list(range(b, t)); inn = sum(pm[q] for q in ds)
        legs.append(dict(al=str(rows[b]["date"]), sat=str(rows[t]["date"]), gun=len(ds),
                         icinde=inn, oran=round(inn / len(ds), 2), gecikmeli_net=round(p, 2)))
    cash_days = [i for i in range(i0, i1 + 1) if tgt[i] == 0]
    res = OrderedDict(
        period=A["period"], k=A["k"], net_nav=round(nav, 2), gross_nav=round(A["gross_hist"][-1][1], 2),
        trades=len(A["trades"]), max_dd=round(dd, 2), passive=round(passive, 2),
        ceiling=round(ceiling, 2), agree_pct=round(agree, 1), jan2023_in_pct=round(jan_in, 1),
        in_gold_pct=round(100 * sum(pm.values()) / len(pm), 1),
        in_gold_on_target_cash_pct=round(100 * sum(pm[i] for i in cash_days) / max(1, len(cash_days)), 1),
        base_rate=round(A["net"].p0, 4))
    crit = OrderedDict(
        G1=(nav >= 230.82, f"{nav:.2f} ≥ 230,82"),
        G2=(10 <= len(A["trades"]) <= 60, f"{len(A['trades'])} ∈ [10,60]"),
        G3=(agree >= 65, f"%{agree:.1f} ≥ %65"),
        G5=(jan_in >= 50, f"Ocak 2023 %{jan_in:.0f} ≥ %50"),
        G6=(dd <= 11.67, f"%{dd:.2f} ≤ %11,67"))
    return res, crit, legs


def main():
    period = sys.argv[1] if len(sys.argv) > 1 else "month"
    k = int(sys.argv[2]) if len(sys.argv) > 2 else H.K_LAG
    relabel = len(sys.argv) > 3 and sys.argv[3] == "relabel"
    variant = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "forget" else None
    forget = "forget" in sys.argv[3:]
    A = marathon(period, k, relabel, variant, forget)
    res, crit, legs = evaluate(A)
    print(f"\n=== TERAZİ v5{'.4 (unutan referans)' if forget else (('.2'+variant) if variant else ('.1 (yeniden etiketleme)' if relabel else ''))} ({period}, K={k}) — geliştirme kaydı, kanıt değil ===")
    for a, b in res.items():
        print(f"  {a:28} {b}")
    print("\n  ÖLÇÜTLER")
    for g, (ok, s) in crit.items():
        print(f"    {g}  {s:28} {'GEÇTİ' if ok else 'GEÇMEDİ'}")
    print("\n  HEDEFİN HAREKETLERİ — model içeride miydi")
    for L in legs:
        print(f"    {L['al']} → {L['sat']}  {L['gun']:3} gün  içeride {L['icinde']:3}  (%{100*L['oran']:.0f})  hedef gecikmeli net %{L['gecikmeli_net']:+.2f}")
    print("\n  İŞLEMLER")
    for t in A["trades"]:
        print(f"    {t['date']} {t['action']:3} @ {t['price']:8.2f}  P={t['P']} z={t['z']}")
    tag = f"{period}_K{k}" + ("_relabel" if relabel else "") + (f"_v52{variant}" if variant else "") + ("_v54" if forget else "")
    json.dump(dict(result=res, criteria={g: v[0] for g, v in crit.items()}, legs=legs, trades=A["trades"]),
              open(os.path.join(HERE, f"TERAZI_V5_SONUC_{tag}.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(A["daily"], open(os.path.join(HERE, f"TERAZI_V5_GUNLUK_{tag}.json"), "w"), indent=0)


if __name__ == "__main__":
    main()
