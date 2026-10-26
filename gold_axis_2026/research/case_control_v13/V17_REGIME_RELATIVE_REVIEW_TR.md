# V17 — REJİME GÖRE NORMALLEŞTİRİLMİŞ DEĞİŞKEN İNCELEMESİ

Daha önceki *mutlak* faiz/GVZ seviyelerinin 2023–2025'e taşınmadığı
gözlendi. Bu yüzden AYNI 31 girdiyi kendi önceki 252 günlük
medyan ve IQR'sine göre değerlendiriyor; değişimin beş günlük
ivmesini ayrı kontrol ediyoruz. 31 x 2 = 62 aday ölçüm.

- Tarihsel vaka/kontrol: 2010–2022
- 2023–2025: sadece sonraki bağımsız dönem kontrolü
- 2026: hiçbir aşamada kullanılmadı
- Değerler resmî ilk-yayın PIT sertifikalı değil.
- BASE14/CFTC21 hesap ve kırmızı alarmları değişmedi.

## Tüm değişkenlerden tarihsel farklar — ilk 12

| metric               | family        | direction   |   consistency |   cluster_effect_IQR |   phase20 |   phase10 |   phase5 |   phase1 |
|:---------------------|:--------------|:------------|--------------:|---------------------:|----------:|----------:|---------:|---------:|
| REGIME:usd_ret5      | USD           | HIGH        |         0.929 |                0.448 |     0.026 |     0.064 |    0.268 |    0.455 |
| CHANGE5:GC_SI_diff   | CFTC          | HIGH        |         0.857 |                0.556 |     0.053 |     0.142 |    0.090 |    0.585 |
| REGIME:corr_AU_PD20  | METALS        | HIGH        |         0.857 |                0.316 |    -0.141 |    -0.100 |    0.308 |    0.180 |
| CHANGE5:SI_net       | CFTC          | LOW         |         0.786 |               -0.301 |    -0.047 |     0.208 |   -0.252 |   -0.347 |
| REGIME:nom2_delta5   | NOMINAL_RATES | HIGH        |         0.714 |                0.511 |     0.250 |    -0.316 |    0.201 |    0.536 |
| REGIME:gvz_dlog1     | GVZ           | HIGH        |         0.714 |                0.290 |    -0.004 |     0.395 |    0.108 |    0.166 |
| CHANGE5:real10       | REAL_RATES    | HIGH        |         0.714 |                0.287 |     0.272 |     0.042 |   -0.195 |    0.405 |
| REGIME:PT_ret5       | METALS        | LOW         |         0.714 |               -0.264 |    -0.060 |    -0.142 |   -0.436 |   -0.200 |
| REGIME:nom2          | NOMINAL_RATES | LOW         |         0.714 |               -0.244 |    -0.520 |    -0.482 |   -0.558 |   -0.514 |
| REGIME:nom10         | NOMINAL_RATES | HIGH        |         0.714 |                0.234 |     0.109 |    -0.004 |   -0.097 |   -0.004 |
| CHANGE5:GC_net       | CFTC          | LOW         |         0.714 |               -0.215 |     0.106 |     0.226 |   -0.133 |   -0.059 |
| CHANGE5:corr_AU_AG20 | METALS        | LOW         |         0.714 |               -0.186 |    -0.550 |    -0.101 |   -0.059 |   -0.253 |

## Endeks değişkenleri (yalnız 2010–2022 araştırmasından)

- REGIME:usd_ret5: HIGH, USD, vaka/negatif ayrımı tutarlılığı 0.929, çiftli IQR farkı 0.448
- CHANGE5:GC_SI_diff: HIGH, CFTC, vaka/negatif ayrımı tutarlılığı 0.857, çiftli IQR farkı 0.556
- REGIME:corr_AU_PD20: HIGH, METALS, vaka/negatif ayrımı tutarlılığı 0.857, çiftli IQR farkı 0.316
- CHANGE5:SI_net: LOW, CFTC, vaka/negatif ayrımı tutarlılığı 0.786, çiftli IQR farkı -0.301
- REGIME:nom2_delta5: HIGH, NOMINAL_RATES, vaka/negatif ayrımı tutarlılığı 0.714, çiftli IQR farkı 0.511
- REGIME:gvz_dlog1: HIGH, GVZ, vaka/negatif ayrımı tutarlılığı 0.714, çiftli IQR farkı 0.29

## 2023–2025 yıllara göre gerçek sonuçlar

|    year |      n |   threshold |   attention_days |   positive_5d_days |   captured_positive_days |   attention_without_5d_drop_days |   unflagged_positive_days |
|--------:|-------:|------------:|-----------------:|-------------------:|-------------------------:|---------------------------------:|--------------------------:|
| 2023.00 | 251.00 |       70.51 |            12.00 |               0.00 |                     0.00 |                            12.00 |                      0.00 |
| 2024.00 | 254.00 |       70.51 |            31.00 |               2.00 |                     0.00 |                            31.00 |                      2.00 |
| 2025.00 | 248.00 |       70.51 |            10.00 |               6.00 |                     0.00 |                            10.00 |                      6.00 |

Modern düşüş dönemleri: 4; düşüş vekil başlangıcından önce işaretlenen: 3.

## Değerlendirme

Bu indeks parametre davranışını betimler, gelecekteki fiyat düşüş
olasılığını veya işlem kararını hesaplamaz. Tüm geçmiş vaka/kontrol
eşleştirmeleri araştırma amaçlıdır, ilk yayın makro verisi kesin
sertifikalı değil. Başarısız testte kural/eşik 2025'e veya 2026'ya
bakılarak değiştirilmedi.

Kaynak dosyaları: outputs/v17r_all_62_metrics.csv,
outputs/v17r_modern_selected_metric_formation.csv,
outputs/v17r_modern_event_timing.csv,
outputs/v17r_modern_yearly_metrics.csv, outputs/v17r_audit.json.
