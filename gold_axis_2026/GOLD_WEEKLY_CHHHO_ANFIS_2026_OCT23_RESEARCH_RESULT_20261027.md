# Haftalık ChHHO-ANFIS — 2026 Ocak–23 Ekim gerçek sayısal koşu (araştırma V1)

**Durum:** ÇALIŞTIRILDI / ARAŞTIRMA DENEMESİ / PRODUCTION_PROMOTION_REJECTED.
**Veri tarihi:** Son tam hedef hafta 19–23 Ekim 2026.
**Gerçek çalıştırma çıktısı:** [42 haftalık satırlar ve model raporu](research/weekly_chhho_anfis_20261027_2026_OCT23_v2.json).
**Kod:** [Haftalık ChHHO–ANFIS hesaplama motoru](tools/gold_weekly_chhho_anfis_js_v1.js).

## 1. Veri ve eğitim
- Gold Control Neon, 2010–2025 dört metal (AU/AG/PT/PD) onaylı StakTrakr araştırma gözlemleri; 2026 Ocak–Eylül 02964d... pinned snapshot. Ekim 1–16 için kaynak Git blob `008c5e2477698df2c9bc3b88248ebef1345e5159`; 19–23 Ekim için `11e48dabc336eed2ec69745b616841ebb988c7d8`.
- Her ortak işlem gününde 4 metal, haftada en az 3 ortak iş günü. Özellikler yalnız **önceki iki tamamlanmış haftanın** dört metal haftalık ortalamasından log getiri. Hedef: bir sonraki haftanın altın ortalama fiyatı.
- Train 2010-01-18–2021-12-27, 624 hafta; check/validation 2022-01-03–2024-12-30, 157 hafta. Son `fit` yalnız 2024 sonuna kadar; 2025 ve 2026 hedef etiketleri ağırlık veya seçim için kullanılmadı.
- Model: 4 giriş, 5 Gaussian üyelik kurallı birinci dereceden Sugeno ANFIS, dört metal log-getiri çoklu çıktı, LSE katsayıları sayısal kararlılık için ridge 0.002. Chaotic logistic HHO merkez/genişlik optimizasyonu + ANFIS türevli yerel gradient güncellemeleri.
- **İşlem bütçesi:** 12 hawk × 18 jenerasyon × 2 tekrar, seçilmiş 23 yerel güncelleme. **Orijinal aylık ChHHO'yu birebir çalıştırmadık**: orijinal aylık 8 giriş, 24 × 45 × 3 bütçe; haftalık yeni 4 giriş kullanıldı. Bu sınır nedeniyle nihai model-aile hükmü verilmez.

## 2. Sonuç
2026'daki 42 tam hedef hafta (5 Ocak–23 Ekim): ChHHO-ANFIS MAPE **%3.064980**, yön **24/42 (%57.14)**. Ancak ham Neon fiyatındaki 2026-02-27 altın 3516.02 fiyat anomalisi gerçek seriyi temsil etmiyor; **bu 42 hafta ile kaynakları karışık ANN dosyasına doğrudan hüküm verme**.

Dışlanan üç dönem: `2026-02-23` (gerçekleşen fiyat hedefi tutarsız); `2026-03-02` ve `2026-03-09` (önceki hafta dört metal özelliğine anomali etkisi). 2026-02-23 Neon hafta AU ortalaması 4851.424 iken ANN V34 sonuç arşivi 5192.68; fark **341.256 USD**. İlk yayın zamanı kanıtlı değil; orijinal kaynak güncellenmedi.

**39 eşleşen ve üç anomali dönemi çıkarılmış haftada**:

| Metrik | Haftalık ChHHO-ANFIS V1 | Mevcut haftalık ANN V34 | Önceki haftanın ortalaması |
|---|---:|---:|---:|
| Ortalama mutlak yüzde fiyat hatası (MAPE) | **%2.98695** | **%1.88489** | %2.60025 |
| Doğru yön sayısı | **23 / 39 (%58.97)** | **28 / 39 (%71.79)** | Uygulanamaz |
| Toplam mutlak fiyat hatası (SumAE) | **5317.04 USD** | **3317.68 USD** | — |
| Daha küçük mutlak hatayla biten hafta | 11 | 28 | — |

2025 ayrı donmuş test: ChHHO-ANFIS 52 hafta, MAPE **%1.84489**, yön **30/52 (%57.69)**. Eski ANN 2025 raporuyla doğrudan kesin metodoloji eşitliği iddia edilmez.

## 3. Sınırlar ve karar
- **Aynı fiyat hedefi ve 39 ortak gerçekleşen gün eşleşmesi doğrulandı.** Ancak ANN 16 girdi / origin bazlı expanding eğitim, haftalık ANFIS ise 4 girdi / 2024 sonu dondurulmuş parametreler kullanır. Eşit mimari, öğrenme güncelleme protokolü ve optimizasyon bütçesi testi DEĞİLDİR.
- ChHHO haftalık uyarlaması bu deneyde hem ANN'den hem naive seviyeden daha çok fiyat hatası yaptı. **Mevcut GOLD / GUARD haftalık ANN panelini değiştirmeyin.**
- Gerçek bankanın işlem fiyatı, periyodun ilk fiyat yayını (PIT) ve araştırma fiyatı serisi tamamen sertifikalı değildir; yalnız retrospektif araştırma sonucudur.
- Model kaynağı ve yeni sonuç GitHub araştırma dalındadır. Neon satırlarında mutation yoktur, canlı otomatik alım/satım tavsiyesi üretilmez.
