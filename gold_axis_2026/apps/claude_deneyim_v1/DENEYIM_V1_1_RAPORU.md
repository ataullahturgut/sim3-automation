# DENEYİM v1.1 — Karar katmanı iyileştirmesi: sonuç ve dondurma

2026-10-16. Sıra: ön kayıt `a748479` → aday kodu ve testler `7f9d016` → bu sonuç. Geliştirme dönemi (2023-01 → 2025-12); 2026 verisi yüklenmedi.

## Adaylar (100 USD, gerçek zamanlı, her ay yalnız önceki ay sonu bilgisiyle)

| Aday | 2023–2024 NAV | 2025 getirisi | Son NAV (2025 sonu) | Maks. düşüş | İşlem |
|---|---:|---:|---:|---:|---:|
| C0 (v1, eşik araması) | 118,48 | %64,62 | 195,05 | %10,36 | 5 |
| **C1 (beklenen getiri, maliyet bandı)** | **129,69** | %64,62 | **213,49** | %10,79 | **1** |
| C2 (düşüş riski çıkışı) | 94,47 | %64,62 | 155,52 | %10,36 | 3 |
| Pasif altın | 140,21 | — | 230,82 | %10,79 | 1 |
| İdeal yol (geriye dönük) | — | — | 580,57 | — | 39 bacak |

**Seçim (ön kayıtlı kural):** 2023–2024 NAV'ı en yüksek olan **C1** seçildi. 2025 iç doğrulaması geçti (C1'in 2025 getirisi C0 ile aynı). v1.1 = C1 olarak donduruldu: `DENEYIM_V1_1_DONDURULMUS_MODEL.json`.

## Dürüst okuma: v1.1 pratikte "akıllı giriş + tut"
C1 tek işlem yaptı: **2023-04-24 AL**, sonra hiç satmadı. Nedeni ölçüldü:
- Benzer geçmiş durumlardan tahmin edilen 10 günlük beklenen getiri 2023'te −%0,49 … +%1,02, 2024'te −%0,21 … +%0,81, 2025'te +%0,02 … +%1,12 aralığında kaldı. Satış bandı (−%0,80, yarım tur maliyeti) hiçbir gün aşılmadı.
- Düşüş (> %1,6) olasılığı 2023'te 22 gün %50'yi aştı; 2024–2025'te %28–%46 arasında kaldı.
- Tahmin ile gerçekleşen 10 günlük getiri arasındaki sıra korelasyonu 0,12 (örtüşen günler, N = 743): yön bilgisi var ama zayıf.

Yani deneyim hafızası, %1,6 tam tur maliyetini karşılayacak kadar güçlü bir "düşüş geliyor" sinyali üretemedi; model bunun yerine yükselen trendde kalmayı öğrendi. v1'deki gereksiz işlemler (2023'te 5 işlem, −%6,3) ortadan kalktı, son değer 195,05'ten 213,49'a çıktı; ama pasif altının (230,82) gerisinde, çünkü giriş Ocak yerine Nisan 2023'te oldu.

## 2026 testi için anlamı
Dondurulmuş v1.1, 10 günlük beklenen getiri tahmini −%0,80'in altına inmedikçe altını tutar. 2026 testi bu kuralın gerçek bir düşüşte satış üretip üretmediğini gösterecek. Test için önce 2026 makro/olay verisi aynı formatta toplanacak ve ayrı bir test ön kaydı yazılacak.

## Dosyalar
- `DENEYIM_V1_1_SECIM_SONUCU.json` — üç adayın tüm sonuçları ve işlem listeleri
- `reports_v1_1/AYLIK_YYYY_MM.md/.json` — seçilen C1'in 36 aylık raporu (benzer durum tahminleri dahil)
- `DENEYIM_V1_1_DONDURULMUS_MODEL.json` — dondurulmuş algoritma (deneyim + sonuç belleği, metrik, katsayılar)
