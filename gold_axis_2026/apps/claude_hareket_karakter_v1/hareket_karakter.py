"""%5 hareketlerin ortak özellikleri. Ön kayıt: HAREKET_KARAKTER_ON_KAYIT.md. Kullanım: python3 hareket_karakter.py"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "claude_deneyim_v1"))
import numpy as np
import deneyim_states as S

TH = 0.05
DISC, REP = ("2023-01-01", "2025-12-31"), ("2020-01-01", "2022-12-31")


def zigzag(p):
    """Dönüş noktaları: (indeks, 'TEPE'|'DIP', onay_indeksi). Son uç onaysız olduğu için dahil edilmez."""
    piv, ext, dirn = [], 0, 0
    for i in range(1, len(p)):
        if dirn == 0:
            lo = int(np.argmin(p[:i + 1])); hi = int(np.argmax(p[:i + 1]))
            if p[i] >= p[lo] * (1 + TH) and lo < i:
                piv.append((lo, "DIP", i)); ext, dirn = i, 1
            elif p[i] <= p[hi] * (1 - TH) and hi < i:
                piv.append((hi, "TEPE", i)); ext, dirn = i, -1
            continue
        if dirn == 1:
            if p[i] > p[ext]: ext = i
            elif p[i] <= p[ext] * (1 - TH): piv.append((ext, "TEPE", i)); ext, dirn = i, -1
        else:
            if p[i] < p[ext]: ext = i
            elif p[i] >= p[ext] * (1 + TH): piv.append((ext, "DIP", i)); ext, dirn = i, 1
    return piv


def binom_p(k, n, p0):
    return sum(math.comb(n, j) * p0 ** j * (1 - p0) ** (n - j) for j in range(k, n + 1))


def main():
    rows = S.load_rows(dev_only=True)
    raw, _ = S.build_states(rows)
    Z, _ = S.standardize(raw)
    F = S.FEATURES
    p = np.array([r["p06"] for r in rows]); d = [str(r["date"]) for r in rows]
    piv = zigzag(p)
    inper = lambda i, per: per[0] <= d[i] <= per[1]
    # anatomi
    legs = []
    for (a, ka, ca), (b, kb, cb) in zip(piv, piv[1:]):
        legs.append(dict(bas=d[a], son=d[b], yon="YUKARI" if kb == "TEPE" else "ASAGI",
                         yuzde=round(100 * (p[b] / p[a] - 1), 2), gun=b - a,
                         hiz=round(100 * (p[b] / p[a] - 1) / max(b - a, 1), 3),
                         onay=d[cb], onay_gecikme_gun=cb - b,
                         onay_fiyat_kaybi=round(100 * (p[cb] / p[b] - 1), 2)))
    # dönüş günü ve onay günü durum analizi
    untrained = {f for f in F if sum(1 for i, r in enumerate(rows) if r["date"].year <= 2022 and raw[i].get(f) is None)
                 > 0.5 * sum(1 for r in rows if r["date"].year <= 2022)}
    out = dict(pivots=[(d[i], k, d[c]) for i, k, c in piv], legs=legs, analiz={})
    for when in ("donus", "onay"):
        for kind in ("TEPE", "DIP"):
            res = []
            for j, f in enumerate(F):
                row = dict(ozellik=f, egitimsiz=f in untrained)
                for name, per in (("kesif", DISC), ("tekrar", REP)):
                    idx = [(c if when == "onay" else i) for i, k, c in piv if k == kind and inper(i, per)]
                    allidx = [i for i in range(len(d)) if inper(i, per)]
                    v = Z[idx, j]; base = Z[allidx, j]
                    if len(v) == 0 or (f in untrained and name == "tekrar"):
                        row[name] = None; continue
                    pos = float(np.mean(v > 0)); neg = float(np.mean(v < 0))
                    sgn = 1 if pos >= neg else -1
                    share = max(pos, neg)
                    bshare = float(np.mean(base > 0)) if sgn > 0 else float(np.mean(base < 0))
                    k = int(round(share * len(v)))
                    row[name] = dict(n=len(v), isaret="+" if sgn > 0 else "−", oran=round(share, 2),
                                     ort_z=round(float(np.mean(v)), 2), taban=round(bshare, 2),
                                     binom_p=round(binom_p(k, len(v), max(bshare, 1e-9)), 3))
                kk, tt = row["kesif"], row["tekrar"]
                row["GECTI"] = bool(kk and tt and kk["oran"] >= 0.8 and abs(kk["ort_z"]) >= 0.5
                                    and kk["oran"] - kk["taban"] >= 0.2
                                    and tt["isaret"] == kk["isaret"] and tt["oran"] >= 0.7 and tt["binom_p"] < 0.10)
                res.append(row)
            out["analiz"][f"{when}_{kind}"] = res
    json.dump(out, open(os.path.join(HERE, "HAREKET_KARAKTER_SONUC.json"), "w"), indent=1, ensure_ascii=False)
    # özet yazdır
    print("HAREKETLER (tüm dönem):")
    for L in legs:
        print(f"  {L['yon']:6} {L['bas']}→{L['son']} %{L['yuzde']:+6.2f} {L['gun']:3}g  hız {L['hiz']:+.3f}%/g  onay {L['onay']} (+{L['onay_gecikme_gun']}g, %{L['onay_fiyat_kaybi']:+.2f})")
    for key, res in out["analiz"].items():
        print(f"\n== {key}: geçen özellikler: {[r['ozellik'] for r in res if r['GECTI']]}")
        strong = sorted([r for r in res if r["kesif"]], key=lambda r: -(r["kesif"]["oran"] - r["kesif"]["taban"]))[:8]
        for r in strong:
            k, t = r["kesif"], r["tekrar"]
            ts = f"tekrar {t['isaret']} %{100*t['oran']:.0f} (taban %{100*t['taban']:.0f}, p {t['binom_p']})" if t else "tekrar yok (eğitimsiz)"
            print(f"   {r['ozellik']:14} keşif {k['isaret']} %{100*k['oran']:.0f} n{k['n']} ort z {k['ort_z']:+.2f} (taban %{100*k['taban']:.0f}) | {ts}")


if __name__ == "__main__":
    main()
