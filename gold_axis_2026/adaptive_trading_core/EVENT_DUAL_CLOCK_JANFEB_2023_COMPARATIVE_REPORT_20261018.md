# Olay sonrası çift saat testi — Ocak ve Şubat 2023

**Gerçek çalıştırma: 18 Ekim 2026 · Girdi: 3.750 adet gerçek vendor XAU/USD M15 barı · Kapsam: 2023-01-02..2023-02-28 · Dört makro K-etkinleşmesi · Model/işlem kodu değişmedi.**

**Kullanıcı önerisi:** ÖĞREN-03 / ETKİ-05 ekonomik mekanizması tetiklenince S1/S2/S3, olay öncesi 4s piyasa ölçüsü ile olay sonrası fiyat tepkisini ayrıştırsın. Ekonomik mekanizma yoksa orijinal hesap devam etsin. Normal trendi yok etmeden **G=Global** ve **E=Event** hesaplar paralel çalışsın.

## Gerçek icra ve bağımsız denetim

- Source `Neon.gold_research_evduka_xau15m_bidask_candidate`; `2023-01-01 <= bar_start_utc < 2023-03-01`; **3.750** tam M15 gözlem, **tek vendor/source**. Her barın fiyati `(bid_close+ask_close)/2`, bilinebilir anı **bar bitişi** (`bar_start_utc+15min`).
- Reproducible implementation: [experimental_event_clock_janfeb2023_replay_v1.js](experimental_event_clock_janfeb2023_replay_v1.js). Node scripti `{bars,events}` JSON stdin alır, **üç hesap kolunun** olay saatli çıktısını üretir; fiyat verisini program içine gömmedik.
- **Sahici mevcut S2 fiyat fazı doğrulaması:** `adaptive_phase_lifecycle_s2.js` modülünün gerçek `create/observe` fonksiyonları 3.750 bar üzerinde aynı girdiyle ayrıca çalıştırıldı. Karşılaştırma kolu **A'nın fazı, yönü ve `trendZ` ölçüsü 3.750/3.750 eşleşti, sapma 0** (trendZ mutlak toleransı 0,0001). Bu eşdeğerlik **yalnız FAST S2 fiyat/phase hesabı** içindir; tüm CORE'un S1 kural tahmini, S2 hazard eğitimi ya da S3 portföy eğitimi tekrar çalıştırılmış değildir.
- Gözlenen dört K-olay penceresi: **6 Ocak NFP (K03+K18+K19), 12 Ocak CPI (K02), 3 Şubat NFP (K03+K19; ücret sürprizi sıfır), 14 Şubat CPI (K05)**. Her biri sonrası 4 saat (16 M15) → **64 olay barı**. Diğer **3.686 bar** normal fiyat hesap çalışmasına bırakıldı. 1 Şubat FOMC için K-etiği mekanizması henüz belgelenmedi; 2 Şubat ECB/BoE etkisi olay sinyali diye uydurulmadı.
- **PIT sınırı:** Tarihli makro ekonomik actual-consensus sürpriz verilerinin ilk-baskı/vintage kanıtı olmadığı için olayın `first_available_at` değeri duyuru saatine eşit **araştırma varsayımıdır**; bu nedenle dört olay **gölge/proxy** ve asla doğrulanmış gerçek zamanlı haber tespiti değildir.

## Üç ayrı yöntem

| Kol | İlk dört saatte ne hesaplanıyor? | Bilimsel rol |
|---|---|---|
| **A — Mevcut Global S2** | Son **17 tamamlanmış M15 fiyatından** kayan 4s trend/volatilite, `START/CONTINUE/PULLBACK/REENTRY/END/NEUTRAL` | Değişmeyen piyasa kontrolü |
| **B — Naif reset** | Olayda tüm kısa 17-fiyat pencere sıfırlanır. Yeniden 17 fiyat için **4s15dk** gerekir; ilk 4 saatin tamamında **WARMUP** | Karşılaştırma, tercih edilmeyen yöntemin gecikmesi |
| **C — Çift saat** | A korunur; ayrıca son tamamlanmış **olay-öncesi referans fiyatı** ile her 15dk gelen yeni fiyatın `100ln(P_t/P_pre)` değeri ve `pre_vol*sqrt(elapsed/4h)` ile normalize edilen **araştırma etkisi** kaydedilir | Olay etkisini genel 4s penceresinden ayrıştırır; ileri-yön tahmini değildir |

C'deki `eventVolZ` olayın kendi ani oynaklığıyla kalibre edilmiş anlamlılık değildir; paydadaki geçmiş 4s normal piyasa oynaklığı birinci şokta yetersiz kalabilir ve çok büyük |Z| üretebilir. Etiket `eventReady` ilk 30 dakikadan sonra, sadece **ölçüm hazır** demektir, ekonomik işlem için onay değildir.

## Açıklamadan 1 saat sonra: Şubat 2023 dahil gerçek sonuç

Tüm saatler aşağıdaki olaylar için UTC, Türkiye saati UTC+3; fiyat değişimi **açıklama öncesi son kapanıştan itibaren** ölçülmüştür.

| Olay | +1s eski A/S2 | +1s reset B | +1s C olay ölçümü | Açıklamadan itibaren 4s gerçekleşen |
|---|---|---|---:|---:|
| **6 Ocak 2023 13:30Z NFP** | NEUTRAL | WARMUP | **+%0,542** | +%1,391 |
| **12 Ocak 2023 13:30Z CPI** | REENTRY / UP | WARMUP | **+%0,257** | +%0,451 |
| **3 Şubat 2023 13:30Z NFP** | NEUTRAL | WARMUP | **−%1,731** | −%2,611 |
| **14 Şubat 2023 13:30Z CPI** | NEUTRAL | WARMUP | **−%0,600** | −%0,693 |

**Önemli 3 Şubat bulgusu:** Fiyat penceresi S2 saat **14:30 UTC (17:30 Türkiye)** `NEUTRAL` iken, olay-özel fiyat etkisi **−%1,731**. Böylece yeni ölçüm olay şokunu ayrı etiketliyor. **İlk 15 dakikada −%1,349** gözlenebildi; saat 14:30Z itibarıyla gelecek 4 saatte gözlenen ek değişim **−%0,934**, o zamandan önce bilinemez. Bankanın ~%1,6 gidiş-dönüş maliyetiyle bu fiyat yolu kârlı al/sat iddiası değildir. Banka long/cash stratejisi short-profit elde edemez.

**14 Şubat çürütücü örnek:** İlk 15dk **+%0,063**, ilk 60dk **−%0,600**; **ilk pozitif tepkiye göre karar üretmek hatalıdır**. 60 dakikadan *sonraki* 60dk altın **+%0,508** yükselmiştir. C'nin olay-kümülatif yönü, sürmekte olan sonraki hareketin işareti olarak kullanılamaz.

## Yön ile ileri tahmini AYIR: 60 dakika daha sonra ne oldu?

Her ekonomik olayın `release+60min` anında (**ilk bir saat gözlendikten sonra**) hesaplanan faz/etki yönü, bu andan **sonraki 60dk gerçekleşmiş yönle** karşılaştırıldı. Araştırma için olay içi döngü; sadece **4 örnek**, dondurulmuş bağımsız doğrulama veya S1 performans testi **değil**.

| Gösterge | Doğru yön | Yanlış yön | Çekimser |
|---|---:|---:|---:|
| **A — o anda aktif S2 fiyat yönü** | 0 | 1 | 3 |
| **B — reset** | 0 | 0 | 4 |
| **C — o ana kadar gerçekleşmiş kümülatif olay yönü** | **2** | **2** | 0 |

**Dürüst sonuç:** C, *olaydan bu yana olan tepkiyi* daha iyi etiketler; **sonraki bir saat yönü için dört vakada %50'den yüksek isabet göstermedi.** A çok çekimser, B ilk 4 saatte tamamen kör; örnek adedi de çok küçük olduğu için bu doğru/yanlış hücreleri yöntemlerin tahmin üstünlüğünü karşılaştırmaya yetmez. Gerçek bir tahmin için geçmiş **yalnız olgunlaşmış bağımsız olay örneklerinden** öğrenilen model, rejim kontrolü ve ayrı ileri-yıl sınavı gerekir.

## Ocak–Şubat işlem sonucuna etki var mı?

- **Mevcut S1/S2/S3 portföy replay:** [Jan–Feb gölge raporu](../apps/portfolio_guard_v1/data/JAN_FEB_2023_AI_SHADOW_CHRONOLOGICAL_20261017.json) Ocak–Şubat süresince kanıtlı **0 gerçek BUY/SELL**, S3 **KEEP CASH**, başta 100 USD → **100 USD**. GPT çağrısı yoktur.
- **Bu A/B/C fiyat-metrik testi:** Original S1 kural öğrenimi ve S3 para/pozisyon kararı tekrar çalıştırılmadı. Dolayısıyla C'nin yeni **kâr, hit rate, kümülatif $ portföy sonucu veya AL/SAT tarihi** ürettiği ileri sürülmez. A'nın dışındaki fiyat olay skorunu S3 otomatik emir yapma; diğer tüm kontroller `tradeAllowed=false` olmalıdır.
- 2 Şubat `S2 DOWN` olay mekanizması değil **fiyat fazıdır**. Bu deneyde ekonomik K yayımlanmadığı için C'nin economic event kanalı açılmadı. 1 Şubat FOMC, dış ekonomik metrik yokluğu nedeniyle yine G-only'dir.

## Karar ve uygulama kapısı

**Önerilen mimari C'yi ileri geliştirme için koru**, B full reset'i reddet; **orijinal normal CORE'u değiştirme**. Geliştirilecek gerçek `event_clock_adapter`, ETKİ-05 K maddelerinin birden fazla aynı zamanda gözlenmesini, `first_available_at/detected_at`, olgunlaşan fiyat referansını, ekonomik ORG rakip mekanizmaları, önceki rejim bağlamını, olayın bitiş ve çakışma durumlarını tutmalı. S1 olay-ankorlu `P(next_direction, scale, duration)` **eğitimli ve kalibreli olmadan** tamamlanmış fiyat değişimini tahmin diye göstermemeli. S3'te bankadaki ~%0,8 her bacak ve ilk uygulanabilir fiyat ile artımlı net avantaj doğrulaması yapılmalı.

**Aktif iş sınırı:** `EVENT_CLOCK_PRICE_METRIC_EXPERIMENT=EXECUTED`, `ORIGINAL_S2_PRICE_PHASE_CROSSCHECK=3750/3750_PASS`, `C_FORECAST_SUPERIORITY=NOT_PROVEN`, `LIVE_CORE_INTEGRATION=NOT_DONE`, `PIT_CERTIFIED=FALSE`, `MODEL_TRADES=0`, `SCIENCE_GATE=FAIL`.

[**Dört olay × 16 barın 64 kayıtlı tüm araştırma metrikleri**](EVENT_DUAL_CLOCK_JANFEB_2023_MEASURED_RESULTS_20261018.json).
