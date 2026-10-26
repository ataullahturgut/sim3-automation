# V19 — 2024 bağımsız yılını BASE14/CFTC21 asıl denklemiyle sınama

2024 için 2023 verileriyle 200 ağaç Isolation Forest 14/21 orijinal
parametrelerini 90/95 eğitim yüzdelik eşiklerini aynen hesapladık.
2024 gerçek fiyat sonuçları hiçbir parametreyi değiştirmedi.
V18 ekonomik yolları yalnız mevcut anormallik + 2010–2022
tarihsel vaka benzerliği ve önceki oturum durumuyla yürütüldü.

| model               |   year |   origins |   alerted |   false5 |   hit5 |   total5 |   hit1 |   total1 |   groups_hit |   groups |
|:--------------------|-------:|----------:|----------:|---------:|-------:|---------:|-------:|---------:|-------------:|---------:|
| BASE14_ORIGINAL_RED |   2024 |       254 |        18 |       18 |      0 |        2 |      0 |        0 |            0 |        2 |
| V18_BI_THREE_PATH   |   2024 |       254 |        11 |       11 |      0 |        2 |      0 |        0 |            0 |        2 |

## Büyük 2024 olaylarının öncesi

|   event_id | peak       | onset_proxy   | trough     |   size_pct | first_prior_original_red   | first_prior_BI_high   | possible_early_warning   |
|-----------:|:-----------|:--------------|:-----------|-----------:|:---------------------------|:----------------------|:-------------------------|
|   2023_001 | 2024-11-05 | 2024-11-06    | 2024-11-14 |   -6.94843 |                            |                       | False                    |

## Uyarı ve dürüstlük
- Bu bir 2024 için 2023 eğitimli açıklama/anormallik gösterimi; yatırım getirisi tahmini değil.
- 2025/2026 orijinal BASE14 ve CFTC21 sonuçları aynen dondurulmuştur.
- 2026 önceden görülmüş olduğundan kör doğrulama değildir.
- 2010–2022 makro ilk yayın sayısal vintage sertifikalı değil.
- Günlük kapanış verisiyle intraday ilk düşüş başlangıcı kesin bilinmez.

Dosyalar: outputs/v19_2024_original_models.csv,
outputs/v19_2024_historical_analogue.csv,
outputs/v19_2024_BI_signals.csv, outputs/v19_2024_replay_metrics.csv,
outputs/v19_2024_physical_onset.csv, outputs/v19_audit.json.
