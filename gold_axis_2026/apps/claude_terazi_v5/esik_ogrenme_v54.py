"""v5.4: öğrenen karar eşikleri, unutan referanslı sinyal (ek-4), yürüyen pencere. Kullanım: python3 esik_ogrenme_v53.py"""
import json, os, sys, math
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
for p in ("claude_terazi_v4", "claude_terazi_v2", "claude_deneyim_v1"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import run_terazi_v5 as RV
import deneyim_states as S
F = S.FEE
TB = [-0.5, -0.25, 0, 0.25, 0.5, 0.75, 1.0]
TS = [-1e9, -1.5, -1.0, -0.75, -0.5, -0.25, 0, 0.25]
SIG = os.path.join(HERE, "V54_Z_SERISI_2021_2025.json")


def get_signal():
    if os.path.exists(SIG):
        return json.load(open(SIG))
    RV.START = date(2021, 1, 4)
    A = RV.marathon("month", 2, relabel=True, forget=True)
    out = [dict(date=d["date"], z=d["z"]) for d in A["daily"]]
    json.dump(out, open(SIG, "w"))
    return out


def simulate(days, rows, d2i, tb, ts, pos0=0, cash=100.0):
    units = 0.0; pos = pos0; n = 0
    if pos0 == 1:
        units = cash / rows[d2i[days[0]["date"]]]["bid"]; cash = 0.0
    for x in days:
        r = rows[d2i[x["date"]]]; z = x["z"]
        if z is None:
            continue
        if pos == 0 and z > tb:
            units = cash * (1 - F) / r["ask"]; cash = 0.0; pos = 1; n += 1
        elif pos == 1 and z < ts:
            cash = units * r["bid"] * (1 - F); units = 0.0; pos = 0; n += 1
    last = rows[d2i[days[-1]["date"]]]
    return cash + units * last["bid"] * (1 - F), n, pos


def months_add(y, m, k):
    m2 = m - 1 + k
    return y + m2 // 12, m2 % 12 + 1


def walk(R, sig, rows, d2i):
    start = (2023, 1); end = (2026, 1)
    cash, units, pos = 100.0, 0.0, 0
    trades, chosen, navs = [], [], []
    y, m = start
    while (y, m) < end:
        ny, nm = months_add(y, m, R)
        p0 = f"{y:04d}-{m:02d}-01"; p1 = f"{ny:04d}-{nm:02d}-01"
        ly, lm = months_add(y, m, -12); l0 = f"{ly:04d}-{lm:02d}-01"
        look = [x for x in sig if l0 <= x["date"] < p0]
        best = None
        for tb in TB:
            for ts in TS:
                if ts >= tb:
                    continue
                v, n, _ = simulate(look, rows, d2i, tb, ts)
                key = (round(v, 6), -n)
                if best is None or key > best[0]:
                    best = (key, tb, ts, v, n)
        _, tb, ts, lv, ln = best
        chosen.append(dict(donem=p0, al=tb, sat=("hiç" if ts < -100 else ts), pencere_nav=round(lv, 2), pencere_islem=ln))
        for x in [x for x in sig if p0 <= x["date"] < p1 and x["date"] >= "2023-01-03"]:
            r = rows[d2i[x["date"]]]; z = x["z"]
            if z is not None:
                if pos == 0 and z > tb:
                    units = cash * (1 - F) / r["ask"]; cash = 0.0; pos = 1; trades.append((x["date"], "AL", round(r["ask"], 2)))
                elif pos == 1 and z < ts:
                    cash = units * r["bid"] * (1 - F); units = 0.0; pos = 0; trades.append((x["date"], "SAT", round(r["bid"], 2)))
            navs.append(cash + units * r["bid"] * (1 - F))
        y, m = ny, nm
    pk, dd = -1, 0
    for v in navs:
        pk = max(pk, v); dd = max(dd, 100 * (1 - v / pk))
    return navs[-1], trades, chosen, dd


def main():
    rows = S.load_rows(); d2i = {str(r["date"]): i for i, r in enumerate(rows)}
    sig = get_signal()
    out = {}
    for R in (3, 6, 12):
        nav, tr, ch, dd = walk(R, sig, rows, d2i)
        out[R] = dict(nav=round(nav, 2), trades=len(tr), max_dd=round(dd, 2), chosen=ch, ledger=tr)
        print(f"\nR = {R} ay{' (BİRİNCİL)' if R == 6 else ''}: net NAV {nav:.2f}, {len(tr)} işlem, maks düşüş %{dd:.2f}")
        for c in ch:
            print(f"   {c['donem']}: AL z>{c['al']:+}  SAT z<{c['sat'] if c['sat']=='hiç' else format(c['sat'],'+')}   (geçmiş 12 ay: {c['pencere_nav']}, {c['pencere_islem']} işlem)")
    print("\nkıyas: al-tut 230,82 · v5.1 189,94 · v5.3 230,82")
    json.dump(out, open(os.path.join(HERE, "TERAZI_V5_4_ESIK_SONUC.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
