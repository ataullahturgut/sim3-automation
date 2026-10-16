# Altının %5 hareketlerinin ortak özellikleri | Ön kayıt

2026-10-17. Dal `r-gold-hareket-karakter-20261017`. **Hesaplamadan ÖNCE commit edilmiştir.**
Kullanıcının talebiyle araştırma yönü değişir: model değil, hareketlerin kendisi incelenir.

## Örneklem
- Fiyat: `PUSULA_V1_DAILY_ASOF_PANEL` p06 (günlük 06:00 UTC), yalnız açık günler.
- Hareket tanımı: klasik zigzag, eşik %5 (uç noktadan %5 ters dönüş hareketi bitirir).
- **Keşif:** 2023–2025 (14 kesin hareket; tepe ve dipler).
- **Tekrar sınaması:** 2020–2022, aynı tanım, ayrı hesaplanır. 2026 bu çalışmada kullanılmaz.
- Kaynak farkı yok (2020–2025 hepsi EVDUKA_15M); yıl bazında ayrıca raporlanır.

## Ne ölçülür
A. **Dönüş günü durumu** (tepe günü, dip günü): modeldeki 35 değişkenin nedensel z-değeri
   (yalnız o güne kadarki bilgi; `deneyim_states.standardize`). Eğitimde verisi olmayan 19
   değişken 2020–2022'de eksik olduğu için yalnız 2023–2025'te raporlanır, tekrar sınamasına
   giremez.
B. **Onay günü durumu**: hareketin %5 dönüşle kesinleştiği gün — gerçekte bilinebilecek ilk an.
C. **Hareket anatomisi**: büyüklük, süre, hız (%/gün), önceki hareketin büyüklüğü ve süresi,
   tepe/dip öncesi 5/20 günlük getiri, 60 günlük zirveden uzaklık.

## Ortaklık ölçütü (önceden)
Bir özellik, tepelerin (ya da diplerin) "ortak özelliği" sayılır ancak:
1. Keşif örnekleminde dönüş günlerinin **≥ %80'inde** aynı işaretli sapma (z > 0 ya da z < 0)
   VE ortalama |z| ≥ 0,5;
2. Tekrar örnekleminde (2020–2022) yine **≥ %70** aynı işaret ve tek taraflı binom p < 0,10;
3. Karşılaştırma: aynı dönemin tüm günlerinin aynı işaret oranı raporlanır (taban oran);
   işaret oranı taban orandan en az 20 puan yüksek olmalı.
Hareket sayısı küçüktür (tepe ~7, dip ~7 / dönem); sonuçlar keşif niteliğindedir, işlem
kuralı olarak sunulmaz. Hiçbir özellik geçmezse bu da sonuç olarak raporlanır.
