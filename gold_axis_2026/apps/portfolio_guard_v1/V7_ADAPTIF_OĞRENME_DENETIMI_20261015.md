# V7 — Hatalardan öğrenen çift ufuklu altın/nakit model prototipi

**Tarih:** 15 Ekim 2026 · **Statü:** EX_POST_RESEARCH / NOT_BLIND / NO_LIVE_EXECUTION / ECONOMIC_EVENT_ZERO_VERIFIED.

## Mevcut uygulama entegrasyonu
Bu belge ve kod yalnız `research-gold-portfolio-v7-adaptive-app-20261015` araştırma dalındadır. Ana `gold-portfolio-guard-app-v1-20261015` dalındaki V1–V6 çalışmaları ve bütün ana manifestler değiştirilmemiştir. 15m Ocak/Şubat V1 sonuçları korunur.

`adaptive_v7_engine.js`: 96 saatlik koruma + 336 saatlik fırsat tahminleri, fiyat/cross-market/önsel uzmanların olgunlaşmış tahmin hatasına göre online parametre ve ağırlık güncellemesi. Ekonomik olay uzmanı yalnız gerçek `VERIFIED firstprint`, `available_at` ve kaynaklı yeterli geçmiş olduğunda açılır.

`adaptive_v7_app.js`: 2025–Eylül 2026 3511 satırlık kaynağı Git blob `db9a2777b5daf0bc4dab64157a176f71a30a9df5` ile doğrular, önceki sonuçları bozmadan modeli çalıştırır.

`server.js`: salt okunur `GET /api/algorithm/v7/adaptive`. `public/index.html` / `public/app.js`: V7 adaptif öğrenme ekranı. Komisyon her yönde %0,8, gerçek banka BID/ASK hariç; emir verilemez.

## Aynı panelde 119,753917 USD CASH başlangıçlı Şubat–Eylül 2026

| Model | Son USD |
|---|---:|
| V7 online + fiyat/Nasdaq stres satış kuralı | **123,529545** |
| V7 2026 adaptif güncelleme dondurulmuş | 105,181771 |
| V7 stres satış kuralı kapalı | 108,444342 |
| Fiyat uzmanı + önsel + stres satışı | 123,529545 |
| Aynı başlangıçta nakitte kalma | 119,753917 |
| Aynı 3h panelinin ilk alımından Eylül sonuna pasif GOLD | 108,444342 |

Tarihsel V7 işlemleri (Türkiye saati): 2 Şubat 09:00 AL; 3 Mart 12:00 SAT; 6 Mart 12:00 AL; 2 Nisan 09:00 SAT. Eylül sonunda pozisyon CASH.

**Karşı örnek:** 2025'te 100 USD CASH başlangıcında V7 104,275734 USD, pasif GOLD 160,415265 USD. Ocak 2026 ayrı denemesinde 100→115,202011 USD, pasif GOLD 115,366463 USD. Bu deneylerde döneme özgü tutar, önceki aylık kaynakların rakamıyla karıştırılamaz.

**Kritik bilimsel sınır:** Doğrulanmış erişim saatli ekonomik haber **0**; ekonomi öğrenmesi kazancı ispatlanmadı. 2026 verileri model tasarımında görülmüştür; test bağımsız OOS değildir. V4/V5 başka kaynak/kesit/uygulama varsayımıyla sınandığından doğrudan zafer ilan edilmez. V7, gerçek banka işlemi önerisi değildir.

## Kullanım

1. GitHub Desktop'ta `research-gold-portfolio-v7-adaptive-app-20261015` dalını seç, **Fetch origin** ve **Pull origin**.
2. Önceden açılmış Node/PowerShell penceresindeki sunucuyu durdur.
3. `gold_axis_2026\apps\portfolio_guard_v1\BASLAT.bat` ile uygulamayı aç.
4. Solda **V7 adaptif öğrenme (araştırma)** bölümüne gir, **V7 adaptif öğrenme deneyini çalıştır** düğmesine bas.
5. Sonuçlar karşı denetim ve ayrıntılı AL/SAT tablosuyla gösterilir. Gerçek emir verilmez.

Doğrulama: `npm test`, `npm run verify-adaptive-v7`, `npm run verify`. GitHub Actions V7 entegrasyon regresyonu tamamlandı: **PASS**.

## Sonraki bilimsel kabul koşulları

- OLAY-02'deki 96 olay için gerçek haber yayın / kullanıcı erişim saatleri ve çakışan haberler doğrulansın; ekonomi uzmanı neden-sonuç uydurmasın.
- XAU, SI, NQ, ZN, USD, reel faiz, COT/ETF için first-available gözlemler ve olaysız karşı kontroller çalışılsın.
- Hata tipleri `missed_UP, false_SELL, missed_DOWN, premature_BUY, bad_REENTRY` bölümlensin. Örtüşen 336 saatlik kaçan hareketler topluca dolar getiri sayılmasın.
- Aylık kayıtların model parametre snapshotları ve gözlenmiş hataları ayrı sürüm/commit ile saklansın; bu sürüm demo replay içinde günceller ancak yeniden açıldığında kalıcı canlı öğrenme saklamaz.
- Gerçek banka saatli BID/ASK ve maliyetleri ölçülsün. 3 saatlik araştırma verisi ile 15m/M1 gerçek uygulanabilir işleme otomatik geçilmesin.
- V4/V5 ve pasif nakit/altın karşılaştırmaları aynı veri sözleşmesi + gerçekten dokunulmamış ileri dönem üzerinde gerçekleşmeden bilimsel terfi yapılmasın.
