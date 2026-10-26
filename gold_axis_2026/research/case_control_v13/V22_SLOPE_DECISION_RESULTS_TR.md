# V22: ORİJİNAL BASE14/CFTC21 + EĞİM TEMELLİ KARAR ÖNCELİĞİ

**SONUÇ: Araştırma amaçlı öncelik filtresi. Canlı kırmızı alarm
silinmedi, Neon/üretim uygulaması değişmedi.**

|   year | policy                            |   flagged_days |   false5_days |   true5_days |   nextday3_hit |   nextday3_total |   five_day_clusters_hit |   five_day_clusters_total |   mature10_flagged |   false10_days |
|-------:|:----------------------------------|---------------:|--------------:|-------------:|---------------:|-----------------:|------------------------:|--------------------------:|-------------------:|---------------:|
|   2024 | BASE14_ORIGINAL_RED               |             18 |            18 |            0 |              0 |                0 |                       0 |                         2 |                 18 |             18 |
|   2024 | V22_PRIORITIZED_REVIEW_PLUS_WATCH |             12 |            12 |            0 |              0 |                0 |                       0 |                         2 |                 12 |             10 |
|   2024 | V22_ACTIVE_RED_PHASE_ONLY         |              7 |             7 |            0 |              0 |                0 |                       0 |                         2 |                  7 |              7 |
|   2025 | BASE14_ORIGINAL_RED               |             32 |            27 |            5 |              2 |                3 |                       3 |                         3 |                 32 |             25 |
|   2025 | V22_PRIORITIZED_REVIEW_PLUS_WATCH |             20 |            15 |            5 |              3 |                3 |                       3 |                         3 |                 20 |             13 |
|   2025 | V22_ACTIVE_RED_PHASE_ONLY         |             18 |            13 |            5 |              2 |                3 |                       3 |                         3 |                 18 |             11 |
|   2026 | BASE14_ORIGINAL_RED               |             50 |            40 |           10 |              4 |                4 |                       4 |                         4 |                 46 |             27 |
|   2026 | V22_PRIORITIZED_REVIEW_PLUS_WATCH |             32 |            22 |           10 |              4 |                4 |                       4 |                         4 |                 32 |             17 |
|   2026 | V22_ACTIVE_RED_PHASE_ONLY         |             29 |            20 |            9 |              4 |                4 |                       4 |                         4 |                 29 |             16 |

## Gerçek zirve öncesi beş skorlanabilir işlem günü

| event         |   year | peak       |   original_RED_last5 | V22_active_before_or_on_peak   | first_V22_attention_last5   | hypothesis_was_not_blind   |
|:--------------|-------:|:-----------|---------------------:|:-------------------------------|:----------------------------|:---------------------------|
| 2024_11       |   2024 | 2024-10-30 |                    0 | True                           | 2024-10-30                  | True                       |
| 2025_04_MAY   |   2025 | 2025-04-22 |                    5 | True                           | 2025-04-14                  | True                       |
| 2025_10       |   2025 | 2025-10-17 |                    5 | True                           | 2025-10-13                  | True                       |
| 2026_01       |   2026 | 2026-01-29 |                    5 | True                           | 2026-01-23                  | True                       |
| 2026_MAY_JUNE |   2026 | 2026-04-17 |                    0 | True                           | 2026-04-17                  | True                       |
| 2026_08       |   2026 | 2026-08-24 |                    2 | True                           | 2026-08-21                  | True                       |

## Yöntem: Gözlenmiş veri ve ekonomik aşamalar
- Orijinal V18/V19 güçlü RED, 5g momentumun beş seans önceye göre >1 yüzde puanı hızlanması
- Orijinal risk skorunda CFTC21 doğrulanmış ivmelenen anormallik
- Orijinal GVZ kaynaklı RED, son günün kapanışında >=%1,5 değer kaybı
- Orijinal güçlü RED, GVZ>=35 ve RSI>=0,55
- Önceki asıl RED çekirdeğinden bir günlük pozitif momentum RED devamı
- V18 güçlü YELLOW'un tek oturumluk devamı
- V21 BASE14 NORMAL kırılganlık WATCH ayrı, kırmızı yerine geçmez

## Yöntem sınırları ve geliştirme kararı
- Eşikler 2024–2026 vakaları görüldükten sonra araştırıldı: sonuç kör OOS değil.
- 2024/2025/2026 günlük sonuçları az sayıda bağımsız düşüş içerir.
- 2010–22 dar V21 kuralını destekleyen yeterli bağımsız örnek yok.
- 2026 Mart bozuk veri karantinada, skor döneminin dışında.
- Sözde yanlış alarm sayısı 40->22 yalnız önceliklendirilen gün sayısıdır;
  BASE14 asli 50 kırmızı ve 40 false5 günü değişmedi.
- Olay bazlı öncü zirve inceleme ayrı, 5-gün ve 10-gün sonuçlar ayrı.
- Bu başlıktaki RED bir yatırım AL/SAT emri değildir.
- İlk yayın makro/CFTC sayısal vintage sertifikası eksik.
- Canlıya geçmek için yeni bağımsız dönem, olay sayısı ve dönem genişliği gerekir.

Dosyalar: outputs/v22_daily_decisions.csv,
outputs/v22_daily_outcome_audit_ONLY.csv,
outputs/v22_three_year_metrics.csv,
outputs/v22_physical_early_warning.csv, outputs/v22_audit_limits.json.
