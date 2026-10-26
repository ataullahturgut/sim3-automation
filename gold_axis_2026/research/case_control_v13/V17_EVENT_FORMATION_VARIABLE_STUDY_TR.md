# V17 — DÜŞÜŞLER NASIL OLUŞTU? DEĞİŞKEN TARAMASI VE OLUŞUM İNDİSİ

Tahminci değil, geriye dönük olay oluşum araştırması ve açıklanabilir
gösterge endeksi. Tek bir faktöre takılmadan, 31 fiyat/makro/pozisyon
değişkeninin tamamı aynı olay ve kontrollerle incelendi.

## Kapsam ve güvenilirlik
- 2010–2022: 27 düşüş grubu, 15 örtüşmeyen bağlam; 81 benzer düşüşsüz gün.
- 2023–2025: değişken öğrenimine karıştırılmadan dış dönem kontrolü.
- Olayın başlangıcı fiyat kapanışlarına dayalı vekildir. İlk makro yayın
  anının PIT sertifikası mevcut değil.
- Endeks gelecekteki getirinin olasılığı veya bir al/sat kararı değildir.
- BASE14/CFTC21 değiştirilmedi; 2026 aday seçimine sokulmadı.

## 2010–2022 öncü değişken değerlendirmesi (ilk 12)

| feature       | family        | direction   |   consistency |   normalized_effect |   phase_minus20 |   phase_minus10 |   phase_minus5 |   phase_minus1 |
|:--------------|:--------------|:------------|--------------:|--------------------:|----------------:|----------------:|---------------:|---------------:|
| gvz_level     | GVZ           | HIGH        |         0.929 |               0.841 |           0.829 |           0.888 |          1.025 |          1.067 |
| usd_ret5      | USD           | HIGH        |         0.857 |               0.429 |          -0.232 |          -0.004 |          0.109 |          0.409 |
| nom2          | NOMINAL_RATES | LOW         |         0.857 |              -0.410 |          -0.463 |          -0.480 |         -0.445 |         -0.432 |
| usd_ret1      | USD           | LOW         |         0.786 |              -0.309 |          -0.443 |          -0.229 |          0.475 |         -0.307 |
| corr_AU_PD20  | METALS        | HIGH        |         0.714 |               0.503 |           0.062 |           0.485 |          0.512 |          0.333 |
| nom2_delta5   | NOMINAL_RATES | HIGH        |         0.714 |               0.371 |           0.129 |          -0.194 |          0.129 |          0.387 |
| PT_ret5       | METALS        | LOW         |         0.714 |              -0.304 |           0.222 |           0.104 |         -0.308 |         -0.219 |
| gvz_dlog1     | GVZ           | HIGH        |         0.714 |               0.247 |           0.104 |           0.356 |          0.269 |          0.179 |
| SI_d4         | CFTC          | LOW         |         0.714 |              -0.138 |          -0.198 |          -0.032 |          0.014 |         -0.151 |
| nom10         | NOMINAL_RATES | LOW         |         0.643 |              -0.356 |          -0.543 |          -0.429 |         -0.594 |         -0.402 |
| au_vol5       | GOLD_TREND    | HIGH        |         0.643 |               0.299 |           0.325 |           0.087 |          0.106 |          0.479 |
| real10_delta5 | REAL_RATES    | HIGH        |         0.643 |               0.292 |          -0.083 |           0.000 |          0.000 |          0.417 |

## Seçilmiş değişkenler (yalnız tarihsel kararlılık + vaka-kontrol farkı)

1. gvz_level (GVZ, HIGH), tutarlılık 0.929, medyan etkisi 0.841 IQR
2. usd_ret5 (USD, HIGH), tutarlılık 0.857, medyan etkisi 0.429 IQR
3. nom2 (NOMINAL_RATES, LOW), tutarlılık 0.857, medyan etkisi -0.41 IQR
4. usd_ret1 (USD, LOW), tutarlılık 0.786, medyan etkisi -0.309 IQR
5. corr_AU_PD20 (METALS, HIGH), tutarlılık 0.714, medyan etkisi 0.503 IQR
6. nom2_delta5 (NOMINAL_RATES, HIGH), tutarlılık 0.714, medyan etkisi 0.371 IQR

**Örüntü güven kapısı:** en az üç uygun değişken bulundu

## 2023–2025 bağımsız dönem denetimi

|    year |      n |   index95_threshold |   flag_days |   future5pct_label_days |   overlap_days |   negative_flag_days |   missed_label_days |
|--------:|-------:|--------------------:|------------:|------------------------:|---------------:|---------------------:|--------------------:|
| 2023.00 | 251.00 |               69.75 |        0.00 |                    0.00 |           0.00 |                 0.00 |                0.00 |
| 2024.00 | 254.00 |               69.75 |        0.00 |                    2.00 |           0.00 |                 0.00 |                2.00 |
| 2025.00 | 248.00 |               69.75 |        0.00 |                    6.00 |           0.00 |                 0.00 |                6.00 |

2023–2025 düşüş grubu sayısı: 4
Başlangıçtan önce indeks uyarısı görülen grup: 0
Uyarılar kontrol başlangıcına kadar her olay için 20 önceki işlem gününde aranmıştır.

## Denetim dosyaları
- outputs/v17_all_feature_effects.csv — 31 değişken ve -20/-10/-5/-3/-1 gün örüntüsü
- outputs/v17_history_formation_windows.csv — olay ve kontrol gelişim çizgileri
- outputs/v17_2023_2025_real_drawdown_events.csv — tüm bağımsız olaylar
- outputs/v17_2023_2025_precursor_windows.csv — modern olay parametreleri
- outputs/v17_2023_2025_daily_index.csv — tüm 2023–2025 kontrol günleri
- outputs/v17_research_audit.json — kapsam ve kabul kapıları

## Kritik metodoloji
Olaylar ve kontroller geçmişteki gerçekleşmelerle işaretlenir; **bu gelecek etiketleri
endeksin günlük değerinin girdisi değildir**. Etkiler eşleştirilmiş vaka
farklarıdır, nedensel ekonomik etki veya yatırım getirisi değildir.
2010–2022 resmî ilk yayım sayısal PIT doğruluğu kesinleşmeden bu çalışma
canlı kullanıma geçirilemez. 2000–2009 kaynağı henüz mevcut değil.
