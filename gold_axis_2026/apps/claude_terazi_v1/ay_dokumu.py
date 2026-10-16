"""TERAZİ v1 — bir ayın tam kaydı (gün gün): kural tabanı, tetiklenen kurallar, karar, ideal yol.
Kullanım: python3 ay_dokumu.py 2023-01
"""
import math, os, sys
import numpy as np
import terazi_v1 as T
import deneyim_states as S
from deneyim_v1 import oracle

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "claude_deneyim_v1"))
from collections import OrderedDict
from datetime import date

TARGET = sys.argv[1] if len(sys.argv) > 1 else "2023-01"
START = date(2023, 1, 3)

rows = S.load_rows(dev_only=True)
raw, macro = S.build_states(rows)
Z, std = S.standardize(raw)
i0 = next(i for i, r in enumerate(rows) if r["date"] >= START)
mid = lambda q: (rows[q]["bid"] + rows[q]["ask"]) / 2
net = T.Terazi()
learned = set()
months = OrderedDict()
for i in range(len(rows)):
    months.setdefault(str(rows[i]["date"])[:7], []).append(i)

cash, units, pos = 100.0, 0.0, 0
snapshot_before = None
for m, idxs in months.items():
    if m == TARGET:
        snapshot_before = [(R.label(), R.weight, R.mu, R.n, R.k, R.born) for R in sorted(net.rules, key=lambda x: -x.weight)]
        print(f"=== {TARGET} AYINA GİRERKEN KURAL TABANI: {len(net.rules)} kural ===")
        if not net.rules:
            print("  (boş)")
        for lab, a, mu, n, k, born in snapshot_before:
            print(f"  oy ağırlığı {a:+.3f} | beklenen %{mu:+.2f} | n {n:6.1f} | saha kanıtı {k:6.2f} | doğum günü {rows[born]['date'] if born < len(rows) else born}")
            print(f"      {lab}")
        print(f"\n  Görüş eşiği: tetiklenen kuralların (oy ağırlığı × tetikleme) toplamı W ≥ {T.W_MIN}")
        print(f"  AL şartı: E − {T.LAM}·U > %{T.BUY_TH:.3f}   SAT şartı: E + {T.LAM}·U < %{T.SELL_TH:.3f}\n")
        opos, _ = oracle(rows, 0, idxs[-1]); Y = np.array(opos)
        print("=== GÜN GÜN ===")
        print("tarih       altın    ALIŞ     SATIŞ    ideal  model  tetiklenen  W      E       U      karar")
    for i in idxs:
        if i < i0:
            continue
        d = net.decide(Z[i])
        act, _ = net.action(pos, Z[i])
        if m == TARGET:
            fired = []
            for R in net.rules:
                a = R.weight
                if a <= 0: continue
                w = R.fire(Z[i])
                if w >= 0.05: fired.append((R, a * w, w))
            W = sum(aw for _, aw, _ in fired)
            r = rows[i]
            print(f"{r['date']}  {mid(i):8.2f} {r['ask']:8.2f} {r['bid']:8.2f}   "
                  f"{'ALTIN' if Y[i] else 'NAKİT'}  {'ALTIN' if pos else 'NAKİT'}   {len(fired):3d}       "
                  f"{W:5.2f}  {('%+.2f' % d['E']) if d else '  -  '}  {('%.2f' % d['U']) if d else ' -  '}   "
                  f"{act if act!='HOLD' else ('bekle' if d else 'GÖRÜŞ YOK')}")
            if fired and d:
                for R, aw, w in sorted(fired, key=lambda x: -x[1])[:3]:
                    print(f"             ↳ {R.label()[:62]:62s} tetik {w:.2f} × güven {R.weight:.2f} → beklenen %{R.mu:+.2f}")
        if act == "AL":
            units = cash * (1 - S.FEE) / rows[i]["ask"]; cash = 0.0; pos = 1
        elif act == "SAT":
            cash = units * rows[i]["bid"] * (1 - S.FEE); units = 0.0; pos = 0
    i_end = idxs[-1]
    for q in range(0, i_end - T.H + 1):
        if q not in learned:
            net.learn(q, Z[q], 100 * math.log(mid(q + T.H) / mid(q))); learned.add(q)
    qs = list(range(0, i_end - T.H + 1))
    ch = net.restructure(Z[qs], np.array([100 * math.log(mid(q + T.H) / mid(q)) for q in qs]), qs, now=i_end)
    if m == TARGET:
        nav = cash + units * rows[i_end]["bid"] * (1 - S.FEE)
        tdays = [i for i in idxs if i >= i0]
        print(f"\n=== AY SONU ===")
        print(f"NAV: {nav:.4f} | pozisyon: {'ALTIN' if pos else 'NAKİT'}")
        print(f"İdeal yol bu ay {int(sum(Y[i] for i in tdays))}/{len(tdays)} gün ALTIN diyordu.")
        best = max(((100 * (1 - S.FEE) ** 2 * rows[b]['bid'] / rows[a]['ask'], a, b) for a in tdays for b in tdays if b > a), default=None)
        if best: print(f"Bu ay içinde en iyi tek işlem: {rows[best[1]]['date']} AL → {rows[best[2]]['date']} SAT = net %{best[0]-100:+.2f}")
        print(f"\nDoğan kural: {len(ch['born'])}")
        for b in ch["born"]:
            print(f"  + {b['label']}")
            print(f"      beklenen %{b['mu']:+.2f} | destek {b['support']} gün | artık ortalaması %{b['residual_mean']:+.2f} | oy hakkı YOK (çıraklık)")
        print(f"Ölen kural: {len(ch['died'])}")
        for dd in ch["died"]:
            print(f"  − {dd['label']} (güven {dd['trust']:+.2f}, saha {dd['field_k']}, {dd['lifetime_days']} gün yaşadı)")
        print(f"Ay sonu kural tabanı: {len(net.rules)} kural")
        break
