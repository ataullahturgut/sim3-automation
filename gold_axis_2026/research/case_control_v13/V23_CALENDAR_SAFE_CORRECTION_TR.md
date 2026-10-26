# V23 — TAKVİM / HATALI FİYAT / 10 GÜNLÜK HEDEF DÜZELTMESİ

**Statü:** Ayrı araştırma dalında gerçekleştirilen kaynak-veri ve hedef hesabı düzeltmesi.
**BASE14/CFTC21 modeli yeniden eğitilmedi. Canlı alarm, Neon verisi veya üretim sistemi değiştirilmedi.**
**V22 karar kuralları değiştirilmedi:** Yalnızca ileri dönük sonuçların *sonradan* denetlenmesi düzeltildi.

## Sorun, yapılan düzeltme

1. Eski V22 değerlendirme kodu, ardışık 10 fiyat işlem günü yerine CFTC dahil ortak veri taşıyan **10 karar satırı** üzerinde minimum fiyat hesaplıyordu. Karar tablosunda 2025-10-21→11-20 ve 2026-02-19→03-30 boşlukları bu ufku bozuyordu.
2. Yeni hesap, 2024–25 LBMA etiketli StakTrakr araştırma rekonstrüksiyonu ve 2026 StakTrakr Git snapshot fiyatlarının **713 tarihli tam fiyat takvimini** kullanıyor. 647 karar gününün orijin fiyatı ile eşleşme **647/647**, gelecek 5 fiyat günü etiketlerinin eşleşmesi **647/647**.
3. 2026-02-27 tarihli 3516,02 $ gözlemi veri setinden silinmedi ve **asla gerçek fiyat kabul edilmiyor**. İleri 10 fiyat günü bu tarihe değen 2026-02-13, 16, 17, 18, 19 kararlarının sonuçları UNKNOWN olarak etiketlendi. Bozuk veriyi çıkartıp 11'inci günü 10'uncu gün kabul etme yok.
4. 2026 Eylül sonu skorlarının 10 günlük değerlendirmesi için kaynakta bulunan Ekim fiyatları kullanıldı. Fiyat kaynağı 16 Ekim 2026'da bitiyor.
5. Birden fazla alarm gününden oluşan epizotta **TRUE** = herhangi bir güvenilir TRUE; **FALSE** = bütün günler güvenilir FALSE; aksi halde **UNKNOWN**. Olay ve gün sayıları birbirine karıştırılmıyor.

## Örnek karşılaştırma (gelecek 10 tam fiyat oturumu)

| Karar tarihi | Eski seyrek-panel hesap | Düzeltilmiş hesap | Durum |
|---|---:|---:|---|
| 2025-10-17 | -%7,01 | **-%9,87** | TRUE |
| 2026-02-10 | -%10,54 | **-%3,41** | FALSE, eski TRUE yanlıştı |
| 2026-02-17 | -%7,39 | **belirsiz** | 27 Şubat şüpheli kaydı içeriyor |
| 2026-09-21 | olgunlaşmamış | **-%4,76** | FALSE, Ekim fiyatı sayesinde hesaplandı |

## 5 günlük alarm etiketi — aynen korunuyor

| Dönem | Eski BASE14 RED: 5g %5 düşüşsüz gün | V22 öncelikli + WATCH: 5g %5 düşüşsüz gün | V22 5g etiket kümeleri |
|---|---:|---:|---:|
| 2024 | 18 | 12 | 0/2 |
| 2025 | 27 | 15 | 3/3 |
| 2026 (21 Eylül'e kadar) | 40 | 22 | 4/4 |

**40→22 azalma gerçek RED alarmının kaldırılması değildir.** Öncelik listesinde görünen gün sayısındaki değişimdir.

## 10 günlük alarm epizotları — düzeltilmiş (4 takvim günü grup eşiği)

| Dönem | Politika | Toplam | Düşüşle eşleşen | Düşüşsüz | Belirsiz |
|---|---|---:|---:|---:|---:|
| 2024 | Orijinal RED | 4 | 0 | 4 | 0 |
| 2024 | V22 öncelikli + WATCH | 8 | 1 | 7 | 0 |
| 2025 | Orijinal RED | 7 | 3 | 4 | 0 |
| 2025 | V22 öncelikli + WATCH | 5 | 3 | 2 | 0 |
| 2026 | Orijinal RED | 8 | 3 | 4 | 1 |
| 2026 | V22 ACTIVE RED | 8 | 4 | 3 | 1 |
| 2026 | V22 öncelikli + WATCH | 9 | **5** | **3** | **1** |

Bunlar bağımsız ekonomik çöküş sayıları değil, alarm epizotlarıdır. Alarmın düşüşten önce oluştuğunu veya modelin canlı tahmin başarısını **ispatlamaz**.

## Kaynak ve kapsam kısıtları — düzeltilmiş değil, açık!

- 2024–25 fiyatı **tarihsel rekonstrüksiyon**, 2026 fiyatı **Git snapshot**. Sayısal ilk yayın (point-in-time/vintage) doğrulanmadı.
- Makro USD/Fed/CFTC ilk yayınları ve tatil sapmaları için tam PIT sertifikasyonu henüz **yok**. Kaynağın sonradan güncellenmiş sürümüne dayalı verilerle canlı tahmin başarısı kanıtlanamaz.
- 2026 olayları V22 eşikleri seçilirken zaten biliniyordu; geriye dönük uyumun çok iyi görünmesi aşırı uyum olabilir.
- 27 Şubat 2026 şüpheli fiyatının doğru karşılığı dış bağımsız kaynakla saptanıp kanıtlanmadı; etkilenen ufuklar UNKNOWN bırakıldı.
- Sonuç değerlendirmesinde geleceğin fiyatları kullanılır; **karar özelliklerine veya eğitime aktarılmaz**.

## Tekrar üretim

```bash
cd gold_axis_2026/research/case_control_v13
python risk_v23_calendar_safe_audit.py
python risk_v22_slope_decision.py
python risk_v22_episodes_audit.py
python -m unittest -v test_risk_v23_calendar_safe_audit.py test_risk_v22_slope_decision.py test_risk_v22_episode_audit.py
```

Yeni kanonik dosyalar:

- `outputs/v23_price_calendar_RESEARCH_NOT_PIT.csv`
- `outputs/v23_calendar_safe_daily.csv`
- `outputs/v23_calendar_safe_daily_metrics.csv`
- `outputs/v23_calendar_safe_episodes.csv`
- `outputs/v23_calendar_safe_episode_metrics.csv`
- `outputs/v23_validation_manifest.json`

Eski V22 test, kod ve çıktı dosyaları bu dalda yeni takvime uyarlandı. Değişiklik yalnız **araştırma dalındadır**; canlı ortama devreye alınmadı.
