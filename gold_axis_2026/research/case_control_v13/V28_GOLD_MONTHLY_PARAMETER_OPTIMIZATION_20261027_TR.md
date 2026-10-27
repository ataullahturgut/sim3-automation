# V28 | Aylık altın modellerinde zamansal parametre iyileştirmesi (27 Ekim 2026)

**Araştırma dalı:** `research/gold-monthly-v28-parameters-origin-safe-20261027`  
**Neon:** Gold Control; kaynak yalnız SELECT ile okundu, ham fiyat/üretim modelleri değişmedi.  
**Sonuç:** *MPA-ANN küçük fakat DEV / 2025 / 2026 boyunca tekrarlanabilen hata azalması gösterdi. ChHHO 2025'te iyileşirken 2026'da bozuldu. SMA-ELMFIS 2025'i geçemedi. Veri sağlığı henüz PIT-sertifikalı değil.*

## Deney sözleşmesi

- **DEV:** 2022-04…2024-12, 33 hedef ay. Tahmin yoğunluğu `gain` ve log-getiri üst sınırı `cap` burada seçildi; sıralama önceliği `ΣAE`, eşitlikte yön. Parametre alanı: `gain={0,0.25,0.4,0.55,0.7,0.85,1,1.15}`, `cap={0.03,0.05,0.075,0.10,0.15,0.25,∞}`. Formül: `forecast = origin_gold × exp(clip(gain × model_original_gold_logret, -cap, +cap))`.
- **VALIDATION (parametre seçiminde kullanılmadı):** 2025-01…2025-12, 12 hedef ay. Başarı kapısı: ortalama hata hem orijinal sürümden hem de basit `forecast=origin` başlangıcından küçük olmalı.
- **2026 stress (parametre seçiminde kullanılmadı):** Ocak–Eylül, 9 ay. Karşılaştırılabilir hata hesaplamasında Şubat 2026, 27 Şubat dört metalin kirli fiyatı nedeniyle hariç: **8 ay**. Şubat tahminleri yine ayrıca raporlandı.
- **Fiyat sözleşmesi:** V26 sabit StakTrakr 2010–2025 + ayrı 2026 snapshot, 4234 ortak gün; 2026-02-27 dört metalde **tek gün sansürlü**, fiyat uydurulmaz. Gerçek tam ay Şubat için nihai seans-aligned fixing değeri henüz yok.
- **GPR:** 2022-03…2025-11 **45** resmi Git-origin vintage ve 2025-12…2026-08 **9** ayrı vintage. 54 orijinin tam kronolojisi/Git yayın zamanı denetlendi; her hedef ayın `Y` değeri estimatöre verilmedi.
- **Özgün model optimizasyonları değişmedi.** MPA-ANN, ChHHO-ANFIS, AOA-ELM V2, SMA-ELMFIS V2'nin hesapladığı 8-özellik log-getiri tahminine ayrıca iki postprocessing kalibrasyon parametresi uygulanır. *Bu, optimizer içindeki popülasyon / jenerasyon / üyelik fonksiyonu mimarisini yeniden optimize etmek değildir*. Karşılaştırma için orijinal 8-feature multioutput Ridge iç çözücüsünde `alpha` ayrıca DEV'de seçildi.

## Seçilen parametreler (yalnız DEV verisi)

| Model | Getiri çarpanı gain | Aylık maksimum log-getiri cap | Durum |
|---|---:|---:|---|
| MPA-ANN | **1.15** | **0.050** | DEV seçimi, 2025 doğrulama geçti |
| ChHHO-ANFIS | 1.15 | 0.075 | 2025 geçti; 2026 geriledi |
| AOA-ELM V2 | 1.15 | 0.050 | 2025 geçti; 2026 az iyileşti |
| SMA-ELMFIS V2 | 0.55 | 0.050 | **2025 geriledi, reddedildi** |
| Ridge 8 özellik | ridge α=10, gain=1.15 | 0.050 | Araştırma benchmark adayı |

## 2025 bağımsız doğrulama (12 ay MAE USD/ons)

| Model | Eski | Yeni | Sonuç |
|---|---:|---:|---|
| MPA-ANN | 82.03 | **77.42** | PASS |
| ChHHO-ANFIS | 104.02 | **99.47** | PASS |
| AOA-ELM V2 | 90.04 | **87.80** | PASS |
| SMA-ELMFIS V2 | **104.45** | 119.07 | **FAIL** |
| Ridge 8 (α=10) | 90.22 | **85.31** | PASS |

Basit son-ay-fiyatı-rastgele-yürüyüş (RW) referans ortalama hatası aynı 2025'te **139.56 USD/ons**. Bununla birlikte 2025 verileri kalibrasyon seçmek için *kullanılmadı*, yalnız değerlendirmeye alındı.

## 2026 ay ay: gerçekleşen ve yeni kalibre tahminler

Araştırma veri sürümünün XAU/USD **aylık ortalama USD/ons** fiyatları. SMA-ELMFIS ayarı 2025'te geçmediği için son sütun yalnızca reddedilmiş deneme sonucudur.

| 2026 | Gerçekleşen | MPA-ANN ayarlı | ChHHO ayarlı | AOA-ELM V2 ayarlı | Ridge ayarlı | SMA-ELMFIS ayarı (RED) |
|---|---:|---:|---:|---:|---:|---:|
| Ocak | 4747.00 | 4465.97 | 4283.33 | 4257.82 | 4348.60 | 4406.28 |
| Şubat* | 5008.68 | 4749.16 | 5107.51 | 4927.35 | 4990.38 | 4515.49 |
| Mart | 4879.70 | 5143.27 | 4646.77 | 5265.48 | 5265.48 | 5136.60 |
| Nisan | 4721.17 | 4790.26 | 4613.64 | 4677.47 | 4641.71 | 4817.01 |
| Mayıs | 4588.08 | 4642.15 | 4622.90 | 4680.18 | 4695.07 | 4706.26 |
| Haziran | 4240.63 | 4541.09 | 4558.19 | 4609.71 | 4590.54 | 4607.91 |
| Temmuz | 4071.92 | 4133.21 | 4028.37 | 4147.37 | 4033.82 | 4286.68 |
| Ağustos | 4407.30 | 4055.58 | 4047.45 | 4053.83 | 4112.10 | 4091.89 |
| Eylül | 4327.88 | 4633.27 | 4728.21 | 4633.27 | 4613.50 | 4500.31 |

*** Şubat ayının 5008.68 USD/ons değeri yalnız 19 gözlemli geçici araştırma ortalamasıdır, tam ay gerçekleşeni ve doğrulanmış fiyat değildir.**

## 2026 performansı: Ocak, Mart–Eylül toplam 8 ay

| Model | Önceki MAE | Yeni MAE | Değişim | Önceki MAPE | Yeni MAPE | Doğru yön |
|---|---:|---:|---:|---:|---:|---:|
| **MPA-ANN** | 214.01 | **210.83** | **−3.19** | %4.77 | **%4.70** | 5/8 |
| ChHHO-ANFIS | **235.39** | 245.03 | **+9.64** | %5.22 | %5.44 | 5/8 |
| AOA-ELM V2 | 266.14 | **264.27** | −1.87 | %5.89 | %5.85 | 3/8 |
| SMA-ELMFIS V2 (2025 **FAIL**) | 244.04 | 235.19 | −8.85 | %5.48 | %5.27 | 4/8 |
| Ridge 8 benchmark | 247.41 | **242.43** | −4.98 | %5.44 | %5.35 | 5/8 |

2026 **sabit kal** RW MAE = **224.82 USD/ons**; yalnız MPA-ANN ayarlı (210.83) bu basit kıyaslamayı 8 ayda geçti. Gelişme **marjinal** ve yön başarı oranları hiç değişmedi, çünkü pozitif gain ve simetrik cap **yönü değil tahmin büyüklüğünü** değiştirir. Haziran büyük düşüşü ve Ağustos yükselişi hâlâ kaçırılıyor.

### Teknik risk kapıları

- **SMA Şubat çökmesi**: özgün V27 SMA-ELMFIS V2 Şubat 2026 öngörüsü **1.842.52**, ayarlı versiyon **4.515.49**. Aşırı yanlış fiyat azaltılsa bile DEV sonrası 2025 MAE kötüleşti, bu sebeple parametre ayarı **REJECT**.
- **ChHHO**: 2025 ayarlı daha iyi fakat 2026'da eski sürümden kötü. Otomatik canlı geçiş yok.
- **AOA-ELM**: küçük iyileşme var ama 2026 RW referansından kötü, canlı terfi yok.
- **MPA-ANN**: hem 2025 hem 2026 ölçümünde küçük hata düşüşü, yalnız araştırma adayı olarak saklanabilir. Daha ileri prospektif testi zorunlu.
- **Ridge**: DEV'de alpha=10 önceden seçildi; 2025'te geçti; 2026'da MPA'dan kötü, öncelikli aday değil.
- **Kaynak sağlığı**: Tam 2010–2026 benchmark ilk-basım ve seans saati uyumu (PIT) bağımsız sertifikalı değil. Test edilen 2026 yılları geçmiş araştırmalarla görünür olduğu için buradaki sonuç **tamamen kör, bağımsız ileri performans iddiası DEĞİLDİR**.

### Gerçek araç yürütümü

- İş akışı: https://github.com/ataullahturgut/sim3-automation/actions/runs/40481675509 — DEV + holdout ve kilitli 2026 iki iş de **SUCCESS**, 5/5 fail-closed metod testleri PASS.
- Kod: `risk_v28_gold_monthly_parameter_study.py`; test: `test_risk_v28_parameter_study.py`.
- Kalıcı sayısal CSV'ler: `outputs/v28_DEV_selected_hyperparameters_COMMITTED.csv`, `outputs/v28_holdout_and_2026_score_COMMITTED.csv`, `outputs/v28_2026_tuned_monthly_gold_COMMITTED.csv`.
- CI artifact: `gold-v28-dev-only-selected-2025-locked-validation`, `gold-v28-2026-lock-params-results` (tam 45 aylık modeller, tüm DEV grid, 2026 aylık sonuçlar, girdi arşivleri ve SHA'lar).

**İzin verilen operasyonel karar:** araştırma sürümünü koru, canlı aylık tahmini değiştirme, şüpheli 27 Şubat ham fiyatlarını elle düzeltme. Fiyat kaynak sağlık sertifikasını tamamla, sonra gerçek gelecek verisinde doğrula.
