> **2026-10-26 düzeltmesi — V22 eski 10 günlük tablo artık geçersizdir.** 10 işlem günü yanlışlıkla seyrek karar günlerinden hesaplanmıştı. Tam fiyat takvimli ve 27 Şubat 2026 karantinalı düzeltilmiş sonuçlar için **[V23_CALENDAR_SAFE_CORRECTION_TR.md](V23_CALENDAR_SAFE_CORRECTION_TR.md)** dosyasını esas alın. Bu dosyanın aşağısındaki eski 10 günlük rakamlar tarihsel hata kaydıdır; aktif referans değildir.

# V22 BAĞIMSIZ OLMAYAN ALARM EPİZOTLARI DENETİMİ

Kırmızı alarm GÜNLERİ ile ardışık ALARM EPİZOTLARI
aynı başarı ölçütü değildir. Eski 2026 RED 50 gün; işlem günleri
dört takvim günü boşluk aşmadıkça aynı alarm epizodu sayılıyor.
Çakışan 10-gün etiketleri bağımsız piyasa krizi gibi sayılmaz.

|   year | policy                     |   episodes_total |   episodes_true10 |   episodes_false10 |   episodes_unknown10 |
|-------:|:---------------------------|-----------------:|------------------:|-------------------:|---------------------:|
|   2024 | BASE14_ORIGINAL_RED        |                4 |                 0 |                  4 |                    0 |
|   2024 | V22_ACTIVE_RED_ONLY        |                4 |                 0 |                  4 |                    0 |
|   2024 | V22_ACTIVE_AND_YELLOW      |                5 |                 0 |                  5 |                    0 |
|   2024 | V22_PRIORITIZED_PLUS_WATCH |                8 |                 1 |                  7 |                    0 |
|   2024 | V22_WATCH_ONLY             |                3 |                 1 |                  2 |                    0 |
|   2025 | BASE14_ORIGINAL_RED        |                7 |                 3 |                  4 |                    0 |
|   2025 | V22_ACTIVE_RED_ONLY        |                4 |                 3 |                  1 |                    0 |
|   2025 | V22_ACTIVE_AND_YELLOW      |                5 |                 3 |                  2 |                    0 |
|   2025 | V22_PRIORITIZED_PLUS_WATCH |                5 |                 3 |                  2 |                    0 |
|   2025 | V22_WATCH_ONLY             |                0 |                 0 |                  0 |                    0 |
|   2026 | BASE14_ORIGINAL_RED        |                8 |                 4 |                  3 |                    1 |
|   2026 | V22_ACTIVE_RED_ONLY        |                8 |                 6 |                  2 |                    0 |
|   2026 | V22_ACTIVE_AND_YELLOW      |                8 |                 6 |                  2 |                    0 |
|   2026 | V22_PRIORITIZED_PLUS_WATCH |                9 |                 7 |                  2 |                    0 |
|   2026 | V22_WATCH_ONLY             |                1 |                 1 |                  0 |                    0 |

## Düşüş etiketi ve sansür
Gelecek 10 işlem günü boyunca altının aynı uyarı kapanışına göre
en az %5 aşağı işlem günü kapanışı varsa geriye dönük TRUE.
Dönem sonundan ötürü gelecek 10 işlem günü görünmüyorsa UNKNOWN.
Epizot TRUE ise en az bir uyarı günü olgun TRUE; bu baştan
tahminin gerçekleştiğini kanıtlamaz.

## Neden yalnız yanlış uyarı günlerini azaltmak yetmez?
- 2024: Eski 4 RED epizodu da sonradan düşüşle eşleşmez;
  V22 ACTIVE_RED 4 benzer false epizod; başarı ilerlemesi YOK.
- 2024: V22 FRAGILITY_WATCH da alarm sayılırsa kompozit 8 epizot
  üretir, sadece biri (30 Ekim) düşüşle örtüşür. Bunu saklama.
- 2025: Eski 7 epizot, 4 false; ACTIVE_RED 4 epizot, 1 false.
- 2026: Eski 8 epizot, 3 false, 1 gelecek 10g yetersiz;
  ACTIVE_RED 8 epizot, 2 false, 0 yetersiz.
- Dört takvim günü epizot ayrımı sabit ve keyfi, 6 ve 10 gün
  sonuçları outputs/v22_episode_sensitivity.csv içinde.
- 2024 WATCH ve 2026 WATCH canli al/sat tetikleyici degildir.
- İlk-baskı makro veri PIT tam doğrulanmadı; olaylar biliniyordu.

Dosyalar: outputs/v22_alarm_episodes.csv, outputs/v22_episode_sensitivity.csv,
outputs/v22_episode_caveat.json.
