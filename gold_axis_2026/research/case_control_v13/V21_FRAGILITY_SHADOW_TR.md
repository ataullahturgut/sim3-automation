# V21 — 2024 ve 2026 BASE14 NORMAL İKEN GÖRÜNMEYEN KIRILGANLIK

Bu, mevcut alarm matematiğini bozmayan **RESEARCH-ONLY WATCH** katmanıdır.
Yeni fiyat tahmin algoritması veya olasılık modeli yoktur. Eski BASE14 ve
CFTC21 kırmızı alarmları ve Neon değiştirilmedi.

## Açıklanabilir beş parametreli durum

- Orijinal BASE14 NORMAL
- RSI14 >= 0.74
- Geçmiş 20g altın log getirisi 0.04-0.06 arasında
- GVZ geçmiş oynaklık z-skoru >= 0
- Kamuya açık gecikmeli CFTC altın net pozisyon haftalık değişimi < 0

**KRİTİK:** %4-%6 bandı ve birlikte kullanım 2024/2026 tarihlerini daha
önce inceledikten sonra oluşturuldu. Bu nedenle elde edilen 2024/2026
performansı kör test DEĞİLDİR; aşırı uyum mümkündür.

## 2024–2026 geriye dönük sonuçlar

|   year |   original_red_days |   original_BI_high_days |   new_shadow_watch_days |   new_watch_next10_true_5pct |   new_watch_next10_false_5pct |   new_watch_episodes |   new_watch_episodes_true |   new_watch_episodes_false |   original_BI_peak_coverage |   combined_BI_peak_coverage |   physical_event_count |
|-------:|--------------------:|------------------------:|------------------------:|-----------------------------:|------------------------------:|---------------------:|--------------------------:|---------------------------:|----------------------------:|----------------------------:|-----------------------:|
|   2024 |                  18 |                      11 |                       4 |                            2 |                             2 |                    3 |                         1 |                          2 |                           0 |                           1 |                      1 |
|   2025 |                  32 |                      30 |                       0 |                            0 |                             0 |                    0 |                         0 |                          0 |                           2 |                           2 |                      2 |
|   2026 |                  50 |                      34 |                       1 |                            1 |                             0 |                    1 |                         1 |                          0 |                           2 |                           3 |                      3 |

## Gerçek zirveden önceki dört işlem gününde görünürlük

| event         |   year | price_peak   | original_high_before_peak   | additional_watch_before_peak   | combined_review_before_peak   | first_original_high   | first_shadow_fragility   | first_either   | not_certified_intraday   | event_dates_were_known_during_rule_research   |
|:--------------|-------:|:-------------|:----------------------------|:-------------------------------|:------------------------------|:----------------------|:-------------------------|:---------------|:-------------------------|:----------------------------------------------|
| 2024_11       |   2024 | 2024-10-30   | False                       | True                           | True                          |                       | 2024-10-30               | 2024-10-30     | True                     | True                                          |
| 2025_04_MAY   |   2025 | 2025-04-22   | True                        | False                          | True                          | 2025-04-14            |                          | 2025-04-14     | True                     | True                                          |
| 2025_10       |   2025 | 2025-10-17   | True                        | False                          | True                          | 2025-10-13            |                          | 2025-10-13     | True                     | True                                          |
| 2026_01       |   2026 | 2026-01-29   | True                        | False                          | True                          | 2026-01-23            |                          | 2026-01-23     | True                     | True                                          |
| 2026_MAY_JUNE |   2026 | 2026-04-17   | False                       | True                           | True                          |                       | 2026-04-17               | 2026-04-17     | True                     | True                                          |
| 2026_08       |   2026 | 2026-08-24   | True                        | False                          | True                          | 2026-08-21            |                          | 2026-08-21     | True                     | True                                          |

## Yeni WATCH günleri (gelecek düşüş sonradan ayrı sütun)

| origin     | watch   | original_alert   | review_priority   |   next10_min_pct_AUDIT_ONLY | meets_10d_5pct_outcome_AUDIT_ONLY   | ten_day_target_mature   |
|:-----------|:--------|:-----------------|:------------------|----------------------------:|:------------------------------------|:------------------------|
| 2024-07-18 | True    | NORMAL           | False             |                       -3.88 | False                               | True                    |
| 2024-10-01 | True    | NORMAL           | False             |                       -1.19 | False                               | True                    |
| 2024-10-30 | True    | NORMAL           | False             |                       -6.94 | True                                | True                    |
| 2024-10-31 | True    | NORMAL           | False             |                       -8.31 | True                                | True                    |
| 2026-04-17 | True    | NORMAL           | False             |                       -5.29 | True                                | True                    |

## Tarihsel destek kontrolü

2010–2022 düşüş/kontrol vaka defterinde ilgili çok dar koşula uygun
örnek **yok** (case ve kontrol için 0). Bu veri yeni kuralın
genellenebildiğini göstermez. Bu bir 'geçmişten kesin öğrenilmiş'
indeks diye sunulamaz. 2023'ün tamamı da orijinal risk modelinin
karar geçmişinde temsil edilmiyor.

## Sınırlar
- Yeni 5 WATCH günlük gözlem, sadece yeni 'dikkat' kaydıdır, RED değildir.
- 2024 4 WATCH'un ikisi sonraki 10g >=%5 düşüşle örtüşmüyor.
- 2026 tek WATCH 17 Nisan tarihindedir, sonraki 10g >=%5 düşüşle örtüşür.
- 2025 ek WATCH üretilmedi; önceki iş zekası 2/2 zirve öncesi kayıttadır.
- Geniş düşüş dönemlerinin 6/6 zirvede öncü koşulu görünmesi,
  nokta atışı veya canlı tahmin başarı oranı değildir.
- Günlük makro/CFTC ilk-baskı sayısal PIT doğrulaması tamam değil.
- 2024/2026 vakaları bilinerek parametre bandı oluşturuldu;
  istatistiksel bağımsız kanıt yoktur ve üretime alınamaz.

Denetim: outputs/v21_daily_shadow.csv, outputs/v21_2024_2026_comparison.csv,
outputs/v21_watch_episodes.csv, outputs/v21_6_events_peak_audit.csv,
outputs/v21_historical_casebook_limitations.json, outputs/v21_audit.json.
