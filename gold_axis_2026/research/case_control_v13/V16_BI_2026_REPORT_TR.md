# V16 — 2026 gerçek iş zekâsı karşılaştırması

Bu bir altın fiyatı/düşüş tahmin modeli değil. Orijinal RED korunur.
GVZ göstergesi IsolationForest skorunda en baskın gruptaysa veya
mevcut 14/21 parametrelerin 2010–2022 bilinen büyük düşüş örneğine
uzaklığı, aynı parametrelerle düşüşsüz kontrole uzaklığından küçükse
mevcut kırmızı ek olarak BI güçlü teyit olarak işaretlenir.
Aksi halde kırmızı alarm silinmez; sadece gözden geçirilmeli etiketi alır.

| Yıl | BASE14 alarm sınıfı | Gün | 5g %5 risk kümesi | Ertesi gün %3 hit | 5g hedefe göre yanlış gün |
|---|---|---:|---:|---:|---:|
| 2025 | ORIGINAL_RED | 32 | 3/3 | 2/3 | 27 |
| 2025 | BI_CONFIRMED | 28 | 3/3 | 2/3 | 23 |
| 2026 | ORIGINAL_RED | 50 | 4/4 | 4/4 | 40 |
| 2026 | BI_CONFIRMED | 28 | 4/4 | 3/4 | 19 |

**2026 BASE14:** BI güçlü teyitte 28 gün/19 yanlış gün ve 4/4 risk kümesi;
ancak ertesi gün %3 düşüşlerin yalnız 3/4 günü güçlü teyit.
Özgün BASE14 50 alarm / 40 yanlış / 4/4; hiçbir RED kaldırılmadı.
Erken alarm 5g penceresinin dışında kaldığında günlük yanlış alarm
sayılabilir; bu sayı bağımsız kriz-öncesi erkenlik başarısı değildir.

## Kanıt ve sınırlar
- v16_bi_daily.csv: karar günü, orijinal skor/alarm, parametre sebebi,
  geçmiş vaka/control yakınlığı ve BI ek etiketi.
- v16_bi_metrics.csv: 2025 ve 2026 karşılaştırma.
- v16_bi_event_timeline.csv: olayın başlamasından önce ek teyit.
- v16_bi_audit.json: değişmeyen alarm ve no-forecast kontrolleri.

2026 sonuçları daha önce araştırmacı tarafından görülmüştür;
**BU KÖR BİR BAŞARI TESTİ DEĞİLDİR.** Başarılı görünmesi
üretim modeline alınmasını kanıtlamaz. 2025 sadece üç 5g risk kümesi
içeriyor ve kaynak ilk yayın numerik vintage tam sertifikalı değil.
Neon ve gerçek alarm uygulaması değiştirilmedi.
