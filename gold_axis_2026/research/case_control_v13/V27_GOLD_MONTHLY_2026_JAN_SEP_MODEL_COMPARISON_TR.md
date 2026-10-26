# V27 | 2026 Ocak–Eylül aylık altın tahminleri

**Hedef:** Gelecek takvim ayının XAU/USD ortalama fiyatı (USD/ons).

**Gerçek çalıştırma:** GitHub Actions 40401107515 **başarılı**. Orijinal MPA-ANN, ChHHO-ANFIS, düzeltilmiş AOA-ELM V2 ve SMA-ELMFIS V2 fonksiyonları 9 ay × 4 model × 3 fiyat senaryosunda **108 kez** çalıştırıldı. Mart 2026 için V26 ile 12/12 tahmin paritesi geçti.

| 2026 | Gerçekleşen | MPA ANN | ChHHO ANFIS | AOA ELM V2 | SMA ELMFIS V2 |
|---|---:|---:|---:|---:|---:|
| Ocak | 4747.00 | 4443.96 | 4285.50 | 4263.29 | 4495.22 |
| Şubat* | 5008.68 | 4748.88 | 5058.98 | 4903.44 | **1842.52** |
| Mart | 4879.70 | 5125.52 | 4631.06 | 5302.35 | 5243.69 |
| Nisan | 4721.17 | 4801.83 | 4647.50 | 4703.37 | 4766.32 |
| Mayıs | 4588.08 | 4652.38 | 4635.60 | 4685.51 | 4694.10 |
| Haziran | 4240.63 | 4547.19 | 4562.08 | 4606.88 | 4624.19 |
| Temmuz | 4071.92 | 4147.06 | 4055.44 | 4159.42 | 4324.73 |
| Ağustos | 4407.30 | 4057.71 | 4050.64 | 4056.19 | 4108.31 |
| Eylül | 4327.88 | 4614.87 | 4685.06 | 4630.55 | 4577.86 |

*Şubat gerçekleşeni eksik 19 günün ortalaması; doğrulanmış nihai tam ay değildir.*

## Sekiz değerlendirilebilir ay (Şubat hariç)

| Model | Toplam mutlak hata | MAE | MAPE | Yön |
|---|---:|---:|---:|---:|
| MPA-ANN | 1712.11 | 214.01 | %4.771 | 5/8 |
| ChHHO-ANFIS | 1883.10 | 235.39 | %5.218 | 5/8 |
| SMA-ELMFIS V2 | 1952.29 | 244.04 | %5.481 | 4/8 |
| AOA-ELM V2 | 2129.12 | 266.14 | %5.887 | 3/8 |

**Çok önemli SMA-ELMFIS kusuru:** Şubat için 1842.52 tahmini, ayın 4934–5019 dolar aralığındaki makul karşılaştırma seviyelerinden 3000 doların üzerinde farklıdır. Şubatın karşılaştırılabilir metrikten çıkarılması bu modelin çökmesini mazur göstermez.

## Doğruluk ve veri sözleşmesi

- Aynı dört metal StakTrakr verisi (2010–2025 sabit commit, 2026 sabit commit), ortak 4234 fiyat günü.
- 27 Şubat 2026 dört metalde gerçek veri anomalisi. `CENSORED_ONE_DAY` araştırma sürümünde dört metalin o günü çıkarılır, gerçekmiş gibi başka fiyat uydurulmaz. Alternatif PM kapanış senaryosu ayrı etiketlidir; gerçek tam ay benchmarkı değildir.
- Dokuz tahmin başlangıcı (Aralık 2025–Ağustos 2026), ayrı resmî orijin-GPR arşiv sürümlerini kullanır. Eğitimde hedef ay Y değeri gizlidir. Mart V26 orijinal model sonuçları aynen tekrarlandı.
- 2026 bu modellerin geçmiş deneylerde görüldüğü yıl; **kör ileri test değildir**. Metal fiyatlarının tüm geçmiş ilk baskıları ayrıca doğrulanmadığı için **PIT fiyat sağlığı sertifikası verilemez**. Canlıya alınamaz.
- Neon, üretim modeli, eski tahminler değiştirilmedi.

**Kalıcı sonuç dosyaları:** `outputs/v27_all_2026_monthly_results_COMMITTED.csv` (108 kayıt), `outputs/v27_model_accuracy_JAN_SEP_FEB_EXCLUDED_COMMITTED.csv` (4 model özeti), `outputs/v27_all_nine_gpr_origin_provenance.csv` (GPR Git sürüm delilleri), `risk_v27_monthly_2026_full_replay.py` (tekrar çalıştırma).

**CI:** https://github.com/ataullahturgut/sim3-automation/actions/runs/40401107515
