"""Hareket anatomisi: süre/büyüklük asimetrisi ve %5 onayıyla işlem yapılsa kalan pay."""
import json, os, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
O = json.load(open(os.path.join(HERE, "HAREKET_KARAKTER_SONUC.json")))
FEE = 0.008
legs = O["legs"]
def per(L): return "2023-2025" if L["bas"] >= "2023-01-01" else "2020-2022"
out = {}
for P in ("2020-2022", "2023-2025"):
    up = [L for L in legs if per(L) == P and L["yon"] == "YUKARI"]
    dn = [L for L in legs if per(L) == P and L["yon"] == "ASAGI"]
    # %5 onayıyla işlem: tepe onayında sat (tepe×(1+kayıp)), dip onayında geri al (dip×(1+kayıp))
    res = []
    for L in dn:
        sell = 1 + L["onay_fiyat_kaybi"] / 100 if False else None
    out[P] = dict(
        yukari_n=len(up), yukari_sure_medyan=st.median(L["gun"] for L in up), yukari_buyukluk_medyan=st.median(L["yuzde"] for L in up),
        asagi_n=len(dn), asagi_sure_medyan=st.median(L["gun"] for L in dn), asagi_buyukluk_medyan=st.median(L["yuzde"] for L in dn),
        asagi_hiz_medyan=st.median(L["hiz"] for L in dn), yukari_hiz_medyan=st.median(L["hiz"] for L in up))
    print(P, json.dumps(out[P], ensure_ascii=False))
# satış onayı → geri alım onayı: bir düşüş bacağı için tepe onayındaki fiyat ile dip onayındaki fiyat
print("\nTepe %5 onayında sat → dip %5 onayında geri al (masraf %0,8×2 dahil):")
rows = []
for a, b in zip(legs, legs[1:]):
    if a["yon"] == "YUKARI" and b["yon"] == "ASAGI":
        top_conf = a["onay_fiyat_kaybi"]          # tepe onay günü, tepeye göre (−)
        # dip onayında fiyat: dip×(1+b.onay_fiyat_kaybi); tepe→dip: b.yuzde
        sell = (1 + top_conf / 100)
        buy = (1 + b["yuzde"] / 100) * (1 + b["onay_fiyat_kaybi"] / 100)
        net = 100 * (sell * (1 - FEE) ** 2 / buy - 1)
        rows.append(dict(tepe=b["bas"], dusus=b["yuzde"], sat_onay=a["onay"], al_onay=b["onay"], net=round(net, 2)))
        print(f"  tepe {b['bas']} düşüş %{b['yuzde']:+.1f}  sat {a['onay']} → al {b['onay']}  net %{net:+.2f}")
for P in ("2020-2022", "2023-2025"):
    x = [r for r in rows if (r["tepe"] >= "2023-01-01") == (P == "2023-2025")]
    print(f"{P}: {len(x)} düşüş, kazandıran {sum(r['net']>0 for r in x)}, toplam %{sum(r['net'] for r in x):+.1f}")
json.dump(dict(ozet=out, onay_islemi=rows), open(os.path.join(HERE, "HAREKET_ANATOMI.json"), "w"), indent=1, ensure_ascii=False)
