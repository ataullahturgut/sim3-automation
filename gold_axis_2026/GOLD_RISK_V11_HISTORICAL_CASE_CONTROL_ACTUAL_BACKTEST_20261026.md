# GOLD RISK V11 — Tarihsel olay ve karşı-örnek öğrenmesi (26 Ekim 2026)

**Durum:** Bağımsız araştırma deneyi tamamlandı. **Ana model değiştirilmedi.** Geçmiş ilk-baskı/pit sertifikası yok; canlı kullanılmaz.

## Gerçek çalışma

- Neon kaynağından tam ve sabit soy ağacından 2010–2019 **2.526 hafta içi altın referans fiyat kaydı** okundu. 10 yıllık ayırma, 2010-01-04/2019-12-31 uçları, yerel SHA ve **Neon üzerinde 10/10 yıl için bağımsız tarih+fiyat MD5 eşleşmesi** doğrulandı. Veriler kaynaktaki sonradan hazırlanmış **araştırma** arşividir, ilk yayın değerleri doğrulanmış değildir.
- 60 işlem günlük geçmiş pencere nedeniyle 2010 başındaki bir eski vaka model eğitiminden çıkartıldı. Kalan etiketler **43 adet gelecek 5 gün >=%5 düşüş başlangıç günü ve 16 bitişik etiket kümesi**; ayrıca aynı yılın trend ve volatilitesine yakın, olaysız **48 negatif karşı örnek** hazırlandı. 17 ham küme fiziksel bağımsız çöküş sayısı değildir.
- Sekiz geçmişe dönük fiyat özelliği: 5/20 günlük getiri, ivme, 5/20 günlük volatilite, fiyat/20g ortalama farkı, 60 günlük zirveden uzaklık, volatilite genişlemesi. Sadece karar gününe kadar olan fiyatlar özellikte yer alır.
- Model: `RobustScaler + L2 LogisticRegression(C=0.25, class_weight=balanced)`. **Fiyat seviye forecast yok.** Bu etiketli risk sınıflayıcısının sigmoid skoru **kalibre çöküş olasılığı değildir**.
- Tarihsel bağımsız denetim: 2010–2014 öğrenme, 2015–2019 test (2020–2022 kullanılmadı). 2015–2019 yalnız dört pozitif karar günü olduğundan güven aralığı çok geniş; buna rağmen **1/4 gün yakalama, 92 yanlış alarm günü, ROC AUC 0,448, AUPRC %.595** çok zayıf.
- Sonra 2010–2019 tamamından fiyat filtresi eğitildi; tarihsel skor kantilleri 0,35/0,50/0,65/0,80 ve eski BASE14/CFTC21 kullanılarak yalnız keşifsel kombinasyonlar üretildi. **2026 test sonuçlarından eşik seçilmedi.**

## Karşılaştırmalı aynı 873 tarihli V8 paneli

| Model | 2025 >=%3 ertesi gün | 2025 5g false gün | 2026 >=%3 ertesi gün | 2026 5g risk etiket kümesi | 2026 5g false gün |
|---|---:|---:|---:|---:|---:|
| BASE14 | 2/3 | 27 | 4/4 | 4/4 | 37 |
| CFTC21 | 3/3 | 25 | 4/4 | 2/4 | 25 |
| V10_BASE_AND_MGVZ | 2/3 | 26 | 4/4 | 4/4 | 32 |
| BASE14_HIST_0.65 | 2/3 | 25 | 4/4 | 4/4 | 34 |
| BASE14_HIST_0.8 | 2/3 | 18 | 4/4 | 3/4 | 34 |
| CFTC_OR_BASE_HIST_0.65 | 3/3 | 28 | 4/4 | 4/4 | 36 |
| CFTC_OR_BASE_HIST_0.8 | 3/3 | 25 | 4/4 | 4/4 | 36 |

**Önceden tanımlanan 2025 tercih kuralı yine CFTC21 seçiyor**, fakat bu model 2026 beş günlük kümelerin 2/4`ünü görüyor. 2026 BASE14_HIST_0.65 4/4 ve 34 yanlış alarm günü sağlar; ancak V10 4/4 ve 32 yanlış alarm günü daha iyidir, 2025 performansı da CFTC21`den zayıftır. **V11 ana sistem için terfi ettirilmedi.**

## Bilimsel sınırlar

1. 2026 dönemindeki dört **gelecek-beş-gün etiket kümesi** bağımsız fiziksel düşüş başlangıcı değildir; düşüş başlamadan kesin önceden uyarı verdiği kanıtlanmadı. 2026 geçmişte birçok kez incelendi, model hipotezleri açısından tam kör test değildir.
2. Altının geçmiş fiyatları ilk-piyasa yayını as-of sertifikalı değildir. 2010–2019 için CFTC/GVZ/GLD/yield verileri eklenmedi. 2020–2022 kullanılmadı.
3. Eğitim negatif örnekleri geçmiş sonuç bilgisiyle etiketlenebilir, ancak karar anındaki girişler asla gelecek fiyatı görmez. Olay kümeleri hem modelde hem değerlendirmede bağımsız günler gibi sayılmamalı.
4. **Ana BASE14 ve CFTC21, GitHub çalışma dalı ve Neon/uygulama canlı tarafı değiştirilmedi.**

## Yeniden çalıştırma

```bash
python -m pip install numpy scikit-learn
python exp_v11_historical_case_control.py
python -m unittest test_v11.py -v
```

Girdiler: V8 SHA ile denetlenen orijinal 2023–2026 overlay ZIP ve CFTC 398-kayıt CSV; 2010–2019 kaynağa sabitli fiyat CSV. Çıktılar: sonuç JSON, her gün uyarı CSV, 48 eşleştirilmiş kontrol CSV. 11/11 birim testi ve temiz klasör yeniden çalıştırmasında üç çıktı dosyasının byte-byte eşleşmesi PASS.
2010–2019 CSV SHA256: `65cd3e13885571cf2a125e59f6671b97eebb972525bdbc8ab8e103f0f99934d1`.