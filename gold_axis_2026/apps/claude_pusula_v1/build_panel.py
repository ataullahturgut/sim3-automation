"""PUSULA v1 günlük as-of panelini Neon dökümlerinden üretir.

Girdi: sql/pusula_v1_panel.sql ile Neon'dan alınan yıllık altın dökümleri (raw_gold_YYYY.txt)
ve CME sembol dökümleri (raw_cme_SYM.txt). Her döküm, Neon'un verdiği satır sayısı ve
toplamlarıyla doğrulanır; uyuşmazlıkta panel üretilmez.

Veri kuralı (model sonuçlarından önce sabitlendi): kaynakta 06:00Z veya 09:00Z fiyatı yoksa
ya da gün altın piyasasının tam kapalı olduğu günlerden biriyse (1 Ocak, Kutsal Cuma, 25 Aralık)
gün "kapalı" işaretlenir; o gün karar ve dolum yapılmaz. (Dukascopy H1 2026 kaynağı bu günlerde
son fiyatı taşıdığı için açık liste gereklidir. İlk denenen "06:00 ve 09:00 mid eşitse kapalı"
kuralı 3 gerçek işlem gününü tesadüfen yakaladığı için, herhangi bir model sonucu üretilmeden
önce bırakıldı.)

Kullanım: python3 build_panel.py <raw_klasörü> <çıktı.csv>
"""
import sys, glob, os, csv
from datetime import date

GOOD_FRIDAY = {date(2020, 4, 10), date(2021, 4, 2), date(2022, 4, 15), date(2023, 4, 7),
               date(2024, 3, 29), date(2025, 4, 18), date(2026, 4, 3)}

def load_gold(raw):
    rows = {}
    for f in sorted(glob.glob(os.path.join(raw, "raw_gold_*.txt"))):
        hdr, body = open(f).read().strip().split("\n", 1)
        y, n, np6, nf, sp, sb, sa = hdr.split("|")
        recs = [r.split(",") for r in body.strip().split(";")]
        p = [float(r[1]) for r in recs if r[1]]
        b = [float(r[3]) for r in recs if r[3]]
        a = [float(r[4]) for r in recs if r[4]]
        ok = (len(recs) == int(n) and len(p) == int(np6) and len(b) == int(nf)
              and abs(sum(p) - float(sp)) < 0.02 and abs(sum(b) - float(sb)) < 5e-4
              and abs(sum(a) - float(sa)) < 5e-4)
        if not ok:
            raise SystemExit(f"CHECKSUM_FAIL {f}")
        for r in recs:
            d = date(int(y), int(r[0][:2]), int(r[0][2:]))
            rows[d] = dict(p06=float(r[1]) if r[1] else None,
                           bid09=float(r[3]) if r[3] else None,
                           ask09=float(r[4]) if r[4] else None,
                           src="EVDUKA_15M" if int(y) <= 2025 else "DUKASCOPY_H1")
    return rows

def load_cme(raw, sym):
    f = os.path.join(raw, f"raw_cme_{sym}.txt")
    hdr, body = open(f).read().strip().split("\n", 1)
    s, n, tot = hdr.split("|")
    recs = [r.split(",") for r in body.strip().split(";")]
    if len(recs) != int(n) or abs(sum(float(r[1]) for r in recs) - float(tot)) >= 5e-4:
        raise SystemExit(f"CHECKSUM_FAIL {f}")
    out = {}
    for r in recs:
        d = date(2000 + int(r[0][:2]), int(r[0][2:4]), int(r[0][4:]))
        out[d] = (float(r[1]), int(r[2]))
    return out

def main(raw, outpath):
    g = load_gold(raw)
    cme = {s: load_cme(raw, s) for s in ("NQ", "ZN", "CL", "SI")}
    closed = 0
    with open(outpath, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "src", "open", "p06", "bid09", "ask09",
                    "nq", "nq_k", "zn", "zn_k", "cl", "cl_k", "si", "si_k"])
        for d in sorted(g):
            r = g[d]
            is_open = r["p06"] is not None and r["bid09"] is not None
            if is_open and ((d.month, d.day) in ((1, 1), (12, 25)) or d in GOOD_FRIDAY):
                is_open = False; closed += 1
            row = [d.isoformat(), r["src"], int(is_open),
                   r["p06"] if is_open else "", r["bid09"] if is_open else "", r["ask09"] if is_open else ""]
            for s in ("NQ", "ZN", "CL", "SI"):
                v = cme[s].get(d)
                row += [v[0], v[1]] if v else ["", ""]
            w.writerow(row)
    print(f"{len(g)} gün yazıldı; taşınmış-fiyat kuralıyla kapalı sayılan: {closed}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
