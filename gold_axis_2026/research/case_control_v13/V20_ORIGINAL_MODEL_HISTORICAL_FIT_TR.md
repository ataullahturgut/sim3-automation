# V20 — 2010 GEÇMİŞİNİN BASE14/CFTC21 MODELLERİNE GERÇEK KATKISI

Tahmin modeli YOK. Mevcut RobustScaler+IsolationForest(200) ve 14/21
parametreleri, eğitim q95 RED eşiği ve rastgele durum aynen.
Sadece eğitim penceresi değişiyor; 2024, 2025, 2026 yıllarının
her birinde o yılın hiçbir verisi eğitimde kullanılmadı.

## BASE14 2024–2026 koşuları (yanlış alarm = 5 gün %5 düşüş YOK)

|   year | window           |   scored_origins |   red_days |   false5_red_days |   red_on_y5_positive |   y5_positive |   red_on_y1_positive |   y1_positive |   distinct_physical_early_peaks_found |   distinct_physical_peaks_total |
|-------:|:-----------------|-----------------:|-----------:|------------------:|---------------------:|--------------:|---------------------:|--------------:|--------------------------------------:|--------------------------------:|
|   2024 | FROZEN_BASELINE  |              254 |         18 |                18 |                    0 |             2 |                    0 |             0 |                                     0 |                               1 |
|   2024 | SINCE_2010       |              254 |         14 |                14 |                    0 |             2 |                    0 |             0 |                                     0 |                               1 |
|   2024 | SINCE_2023       |              254 |         23 |                23 |                    0 |             2 |                    0 |             0 |                                     0 |                               1 |
|   2024 | TRAILING_3_YEARS |              254 |         13 |                13 |                    0 |             2 |                    0 |             0 |                                     0 |                               1 |
|   2024 | TRAILING_5_YEARS |              254 |          6 |                 6 |                    0 |             2 |                    0 |             0 |                                     0 |                               1 |
|   2025 | FROZEN_BASELINE  |              232 |         32 |                27 |                    5 |             5 |                    2 |             3 |                                     2 |                               2 |
|   2025 | SINCE_2010       |              232 |         25 |                21 |                    4 |             5 |                    2 |             3 |                                     2 |                               2 |
|   2025 | SINCE_2023       |              232 |         34 |                29 |                    5 |             5 |                    3 |             3 |                                     2 |                               2 |
|   2025 | TRAILING_3_YEARS |              232 |         29 |                25 |                    4 |             5 |                    2 |             3 |                                     2 |                               2 |
|   2025 | TRAILING_5_YEARS |              232 |         21 |                17 |                    4 |             5 |                    2 |             3 |                                     2 |                               2 |
|   2026 | FROZEN_BASELINE  |              161 |         50 |                40 |                   10 |            13 |                    4 |             4 |                                     3 |                               3 |
|   2026 | SINCE_2010       |              161 |         38 |                29 |                    9 |            13 |                    4 |             4 |                                     3 |                               3 |
|   2026 | SINCE_2023       |              161 |         46 |                36 |                   10 |            13 |                    4 |             4 |                                     3 |                               3 |
|   2026 | TRAILING_3_YEARS |              161 |         46 |                36 |                   10 |            13 |                    4 |             4 |                                     3 |                               3 |
|   2026 | TRAILING_5_YEARS |              161 |         44 |                34 |                   10 |            13 |                    4 |             4 |                                     3 |                               3 |

## CFTC21 koşuları

|   year | window           |   red_days |   false5_red_days |   red_on_y5_positive |   y5_positive |   distinct_physical_early_peaks_found |   distinct_physical_peaks_total |
|-------:|:-----------------|-----------:|------------------:|---------------------:|--------------:|--------------------------------------:|--------------------------------:|
|   2024 | FROZEN_BASELINE  |         12 |                12 |                    0 |             2 |                                     0 |                               1 |
|   2024 | SINCE_2010       |         11 |                11 |                    0 |             2 |                                     0 |                               1 |
|   2024 | SINCE_2023       |         23 |                23 |                    0 |             2 |                                     0 |                               1 |
|   2024 | TRAILING_3_YEARS |          9 |                 9 |                    0 |             2 |                                     0 |                               1 |
|   2024 | TRAILING_5_YEARS |          0 |                 0 |                    0 |             2 |                                     0 |                               1 |
|   2025 | FROZEN_BASELINE  |         21 |                17 |                    4 |             5 |                                     2 |                               2 |
|   2025 | SINCE_2010       |         18 |                14 |                    4 |             5 |                                     2 |                               2 |
|   2025 | SINCE_2023       |         22 |                18 |                    4 |             5 |                                     2 |                               2 |
|   2025 | TRAILING_3_YEARS |         17 |                13 |                    4 |             5 |                                     2 |                               2 |
|   2025 | TRAILING_5_YEARS |         16 |                12 |                    4 |             5 |                                     2 |                               2 |
|   2026 | FROZEN_BASELINE  |         32 |                25 |                    7 |            13 |                                     3 |                               3 |
|   2026 | SINCE_2010       |         28 |                22 |                    6 |            13 |                                     3 |                               3 |
|   2026 | SINCE_2023       |         25 |                19 |                    6 |            13 |                                     3 |                               3 |
|   2026 | TRAILING_3_YEARS |         25 |                19 |                    6 |            13 |                                     3 |                               3 |
|   2026 | TRAILING_5_YEARS |         40 |                30 |                   10 |            13 |                                     3 |                               3 |

## Gerçek tepe vs sonradan belirlenmiş V13 olay başlangıcı

| event         | price_peak   | V13_onset_proxy   |   already_down_when_proxy_pct |
|:--------------|:-------------|:------------------|------------------------------:|
| 2024_11       | 2024-10-30   | 2024-11-06        |                         -2.07 |
| 2025_04_MAY   | 2025-04-22   | 2025-04-23        |                         -3.53 |
| 2025_10       | 2025-10-17   | 2025-10-20        |                         -1.97 |
| 2026_01       | 2026-01-29   | 2026-01-30        |                         -7.97 |
| 2026_MAY_JUNE | 2026-04-17   | 2026-06-05        |                         -8.65 |
| 2026_08       | 2026-08-24   | 2026-08-26        |                         -0.55 |

## Yöntem sınırları
- 2024 yeni bağımsız araştırma, 2025/2026 önceden analizi yapılmış stres dönemleri.
- 2010–2022 makro veri ilk-baskı PIT sayısal vintage tam doğrulanmış değil.
- FRED 10 takvim gün USD gecikmesi kaynak araştırma proxy'sidir, resmî ilk tarih kanıtı değil.
- 2026 bozuk altın fiyat günü geçmiş veride karantinada tutuldu.
- Gerçek fiziksel tepe: V13 olay vekilinden önceki skorlanabilir son 35 seansın en yüksek kapanışı.
- Bu tanım mutlak doğru ekonomik düşüş başlangıcını ispatlamaz; 5-gün
  risk etiketine kıyasla daha sıkı bir erkenlik denetimidir.
- 2025 Nisan/Mayıs ve 2026 Haziran bitişik vaka etiketleri bağımsız sayılmadı.
- Raporun en iyi satırına bakıp 2026 başarısı varmış gibi seçim yapmak,
  aynı döneme fazla uyum riski yaratır; kıyas keşif/denetim amaçlıdır.
- Orijinal BASE14/CFTC21 skor ve uyarıları canlı uygulamada değiştirilmedi.

Dosyalar: outputs/v20_all_original_model_replays.csv, outputs/v20_annual_results.csv,
outputs/v20_physical_peak_definitions.csv, outputs/v20_physical_peak_replay.csv,
outputs/v20_fitting_provenance.csv, outputs/v20_research_audit.json
