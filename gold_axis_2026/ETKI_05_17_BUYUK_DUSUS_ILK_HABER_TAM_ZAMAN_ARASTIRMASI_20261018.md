# 17 büyük altın düşüşü: HABER TAM OLARAK BAŞLANGICIN NERESİNDE?

**18 Ekim 2026 — 2023–2025 | OLAY-02 × ÖĞREN-03 × ETKİ-05 | Gerçek 15dk vendor BID/ASK fiyat + tarihli ekonomik haber kanıt denetimi**

## ÖNEMLİ NET SONUÇ

Tek bir kötü haberi büyük düşüşün başlangıcı kabul etmek çoğu vakada yanlış. 17 uzun fiyat bacağının hepsi için **15 dakikalık altın fiyatında ilk %0,5, %1 ve %2 geri çekilme eşiklerini** ölçtük. Bu geçişler yalnızca **fiyata ait işlem-sonrası araştırma işaretleridir**. Haberleri aynı saatte görmek, aracı etkiyi kanıtlamaz; fiyat geri çekilmesi zaten başlatılmışsa haber ilk tetikleyici olamaz.

- **1 Şubat 2023 Fed** 19:00 UTC; ilk -%0,5 geri çekilme 17:15 UTC (**haber 105 dakika sonra**). 3 Şubat güçlü NFP başka daha büyük satış fazı; 1 Şubat fiyatın ilk inişinden önce değildir.
- **3 Mayıs 2023 Fed** 18:00 UTC; ilk -%0,5 ertesi gün 01:45 UTC (**haber 7s45dk önce**), fakat altın Fed sonrası önce yükselmişti; ters yön/ara haber kontrolü olmadan nedensel DOWN değil.
- **22 Mayıs 2024 Fed tutanakları** 18:00 UTC; ilk -%1 20 Mayıs 12:15 UTC (**2 gün+ önce**).
- **6 Kasım 2024 Trump zaferi** sonrasındaki dolar şoku; ilk -%1 31 Ekim 14:00 UTC (**yaklaşık 6 gün önce**). 30 Ekim Reuters altının hâlâ rekor yaptığını bildirdi.
- **18 Aralık 2024 Fed** 19:00 UTC; ilk -%1 12 Aralık 14:15 UTC (**6 gün+ önce**).
- **2 Nisan 2025 tarifesi** yaklaşık 20:00 UTC; ilk -%1 00:15 UTC (**haber 19s45dk sonra**), tarifeye ilk Reuters fiyat tepkisi gold +%0,6; **anında DOWN haber mekanizması değil**.
- **21–23 Nisan 2025:** arşiv bacağı 21 Nisan başlamış diye etiketli, Reuters 21/22 Nisan altının rekor yükselişini belgeliyor; 23 Nisan Fed/Çin yumuşaması sonrasındaki satış için ayrı alt-bacak araştırması gerekir.
- **6–12 Mayıs 2025:** 6 Mayıs fiyat zayıflamış, o gece ABD–Çin müzakere haberi/7 Mayıs ilk sert düşüş ve 12 Mayıs **anlaşma** farklı ekonomik haber aşamalarıdır.
- **13–24 Haziran 2025:** 13 Haziran saldırı açıklaması altını başta **+%1,7 yükseltmiş**, 24 Haziran ateşkes daha sonraki satış fazı; bunları tek DOWN başlangıcı sayma.
- **13 Ekim–21 Ekim 2025:** WGC 13 Ekim risk/RSI değerlendirmesi, 20 Ekim altın yeni rekoru, 21 Ekim 05:30 UTC -%1 ilk eşik; Reuters 21 Ekim fiyat hareketini “kâr alma” diye anlatıyor ama bu açıklama **ilk breaking headline değil**.
- **26–29 Aralık 2025:** CME Clearing 25-393 **26 Aralık** tarihli **resmî** marjin artışı; 29 Aralık kapanış sonrası yürürlük; altın -%0,5 ilk eşik **26 Aralık 17:30 UTC**, -%1 ilk eşik **29 Aralık 00:30 UTC**. **Duyurunun ilk erişim saati bulunmadığı için 26 Aralık ilk satışla dakika sırası kesin değil; 29 Aralık büyük satışının öncesinde resmî haber vardı.**

### Metodoloji

- `t_pivot`: OLAY-02 içindeki sonuç-sonrası seçilmiş bacak **başlangıç takvim günü**. Bu tarihin 00:00 UTC'si “gerçek ilk düşüş saati” sayılmaz.
- `t_drawdown_0.5` ve `t_drawdown_1`: fiyat kaynağı gerçek tarihli 15dk BID/ASK orta fiyatı. OLAY-02 pivot gününün **bir takvim günü öncesinden itibaren görülen en yüksek kapanış** referans alınır; pivot gününden başlayarak bir sonraki 6 takvim günü içinde bu maksimumdan ilk %0,5 ve %1 geri çekilme eşikleri kronolojik ölçülür. Saat UTC; tarihsel etikete bakılarak kurulmuş tanısal pencere, geleceği tahmin eden AL/SAT algoritması değil.
- İlk negatif 15dk, ilk anlamlı %0,5 geri çekilme, ilk %1 kırılması ve 4–20 günlük seçilmiş hareketin başlangıcı **farklı tanımlardır**. Büyük hareket gününün içinde hâlâ UP fiyat barları bulunabilir.
- Bir medya haberinin ilk yayınlanma tarihi, resmî kararın olay UTC saati ve rapor/yorumun geriye dönük yayım tarihi birbirine karıştırılmaz. **İlk yayımlanma dakikası yalnız kesin/planlı resmî yayınlarda** saatle belirtilmiş, diğerlerinde bilinmiyor.
- **Nedensel ilk haber bulduk = 0/17 doğrulanmış**; bu, sıfır haberde düşüş yaratmadı demek değil. Kaynak ilk yayın saati ile bağımsız fiyat tepkisini doğrulamaya ihtiyaç var.

### Bütün 17 fiyat eşiği ve ilgili haber

| OLAY ID | Bacak başlangıç günü | İlk -%0,5 fiyat eşiği (UTC) | İlk -%1 fiyat eşiği (UTC) | Haber / belge zamanı | Haber ve ilk düşüş ilişkisi |
|---|---|---|---|---|---|
| 002 | 2023-02-01 | 2023-02-01T17:15:00Z | 2023-02-02T14:45:00Z | **2023-02-01T19:00:00Z** | Fed kararı sırasında altın UP; 3 Şubat NFP DOWN şoku, ana düşüş başlamıştı |
| 004 | 2023-05-04 | 2023-05-04T01:45:00Z | 2023-05-04T07:15:00Z | **2023-05-03T18:00:00Z** | Fed haberi fiyat eşiğinden önce; karar sonrası fiyat ilk anda yükseldi. 5 Mayıs NFP başka haber |
| 006 | 2023-07-18 | 2023-07-19T11:30:00Z | 2023-07-20T14:45:00Z | 2023-10-10 (saat belirsiz) | Düşüş sona erdikten sonra yayımlanan yorum; başlangıçta kesin yeni haber bilinmiyor |
| 010 | 2023-12-01 | 2023-12-01T12:00:00Z | 2023-12-04T00:30:00Z | 2023-12-04 (saat belirsiz) | 1 Aralık'ta zaten %0,5; 4 Aralık fiyat kırılması haberin anlattığı durum, haber ilk tetik değil |
| 012 | 2023-12-27 | 2023-12-28T08:30:00Z | 2023-12-28T21:00:00Z | 2023-12-28 (saat belirsiz) | 27 Aralık altın yükseliyor; 28 Aralık ilk %0,5/%1 gerileme, Reuters olay sonrasını anlatıyor |
| 014 | 2024-04-19 | 2024-04-19T00:15:00Z | 2024-04-19T03:30:00Z | 2024-04-19 (saat belirsiz) | 19 Nisan ilk güvenli liman tepkisi UP; 22 Nisan riskin azalmasıyla büyük DOWN; t0 haberin pozitif ve negatif fazları ayrılmalı |
| 016 | 2024-05-20 | 2024-05-20T06:45:00Z | 2024-05-20T12:15:00Z | **2024-05-22T18:00:00Z** | 20 Mayıs'taki ilk %1 geri çekilmeye 2 günden fazla geç; sonraki düşüş fazı adayı |
| 018 | 2024-07-16 | 2024-07-16T00:00:00Z | 2024-07-17T16:30:00Z | 2024-07-17 (saat belirsiz) | 17 Temmuz 14:02 UTC fiyat rekor yakınında UP; %1 geri çekilme 16:30 UTC. Bağımsız negatif yeni haber doğrulanmıyor |
| 020 | 2024-10-30 | 2024-10-31T12:45:00Z | 2024-10-31T14:00:00Z | 2024-11-06 (saat belirsiz) | 30 Ekim altın rekor UP; ilk -%1 31 Ekim. 6 Kasım haberi sonraki DOWN şoku |
| 024 | 2024-12-11 | 2024-12-11T04:45:00Z | 2024-12-12T14:15:00Z | **2024-12-18T19:00:00Z** | 11 Aralık ilk %0,5, 12 Aralık ilk %1; Fed 18 Aralık bacağın sonunda |
| 028 | 2025-04-02 | 2025-04-02T00:00:00Z | 2025-04-02T00:15:00Z | **2025-04-02T20:00:00Z** | %1 fiyat düşüş eşiği 00:15 UTC: tarife 19s45dk sonra; ilk tarife tepkisi altın UP. 3–7 Nisan düşüşe dönmesi ayrı |
| 030 | 2025-04-21 | 2025-04-21T17:15:00Z | 2025-04-22T07:15:00Z | 2025-04-23 (saat belirsiz) | 21 ve 22 Nisan altın rekor UP; 22 Nisan 3500 sonrası ilk negatif faz, 23 Nisan haber risk rahatlaması ve satışlar |
| 032 | 2025-05-06 | 2025-05-06T03:00:00Z | 2025-05-06T22:30:00Z | 2025-05-06 (saat belirsiz) | 6 Mayıs ilk %0,5 03:00; May6 geç saatlerde temas haberleri, 7 Mayıs düşüş; 12 Mayıs resmi anlaşma çok sonra güçlü ek tetik |
| 034 | 2025-06-13 | 2025-06-13T05:30:00Z | 2025-06-16T07:15:00Z | 2025-06-13 (saat belirsiz) | 13 Haziran saldırılarda altın UP (+%1,7); 16 Haziran -%1 geri çekilme; 24 Haziran ateşkes sürmekte olan düşüş için |
| 036 | 2025-07-22 | 2025-07-22T07:30:00Z | 2025-07-23T16:00:00Z | 2025-07-22 (saat belirsiz) | 22 Temmuz 07:30 ilk %0,5; Reuters 11:20 GMT gözlem altın hafif DOWN; 23 Temmuz yeni anlaşma haberi ikinci DOWN basamak adayı |
| 038 | 2025-10-20 | 2025-10-20T00:00:00Z | 2025-10-21T05:30:00Z | 2025-10-13 (saat belirsiz) | WGC 7 gün önce yakın dönem aşırı alım uyarısı, ama Gold 20 Ekim rekor yapmayı sürdürdü; ilk -%1 21 Ekim 05:30Z; sonraki Reuters haberleri DOWN nedeni için ex-post yorum |
| 042 | 2025-12-26 | 2025-12-26T17:30:00Z | 2025-12-29T00:30:00Z | 2025-12-26 (saat belirsiz) | 26 Aralık 17:30Z ilk %0,5; CME duyurunun saatini bilmiyoruz. 29 Aralık 00:30Z ilk %1, önceden tarihli CME duyurusu haber→şok için ciddi aday |

**Saatler:** Sadece Fed gibi planlı resmî haberlerde `OFFICIAL_SCHEDULE`, Beyaz Saray tarife konuşmasında `APPROX_SCHEDULE`; gazetede belirtilen saatin haberin **gerçek olay** veya **ilk dünya haber saati** olduğu varsayılmaz.

## Ekonomik anlam — mekanizmayı iki değil dört katmanda kur

1. **PRECONDITION:** Fiyat daha düşmeden önce artan dolar/faiz yönü, yoğun pozisyon, yüksek risk primi, beklenen haber; bilindiği zamanda kaydedilecek.
2. **INITIATING_NEWS:** Yeni orijinal haber piyasa tarafından ilk erişildiğinde, altının ilk bağımsız olumsuz fiyat tepkisi haberden **sonra** başlıyorsa başlatıcı **ADAY**. Tek haber yeterli nedensellik kanıtı değil.
3. **ACCELERANT / PHASE_SWITCH:** Uzun düşüş başlamışken 3 Şubat NFP, 22 Mayıs Fed, 6 Kasım seçim, 12 Mayıs ticaret ve 24 Haziran ateşkes gibi sonraki farklı olaylar mevcut düşüşe yeni E saati açıp hızı artırabilir.
4. **POSTHOC COMMENT:** WGC aylık değerlendirme veya Reuters'ın yaşanmış satışları tasvir eden raporu **otomatik erken haber sinyali değildir**.

**Kısıt:** Kullanıcı bu aşamada ilk haber / fiyat saat sırasını istedi. Bu rapor **USD/reel faiz/OI verisi eklemiyor, yeni S1/S2/S3 kuralını değiştirmiyor veya işlem kârı yaratmıyor**. Veri toplama ve ekonomik nedensel tahmin ayrı bilim aşamasıdır.

**Makine çıktı:** [17 fiyat eşik noktası, tarih/saat ve aday ilk haber eşleştirmesi](ETKI_05_17_DUSUS_HABER_VE_M15_GERI_CEKILME_SAAT_KARSILASTIRMA_V2_20261018.json)

## Birincil ve tarihli ikincil kaynaklar

- Fed Feb1: https://www.federalreserve.gov/newsevents/pressreleases/monetary20230201a.htm
- Fed May3: https://www.federalreserve.gov/monetarypolicy/fomcpresconf20230503.htm
- May22 Fed meeting minutes: https://www.federalreserve.gov/monetarypolicy/fomcminutes20240501.htm
- Dec18 Fed statement: https://www.federalreserve.gov/newsevents/pressreleases/monetary20241218a.htm
- Apr19 2024 Iran/Israel initial gold UP and Apr22 DOWN: https://www.reuters.com/markets/commodities/safe-haven-gold-rises-israeli-attack-iran-raises-concerns-wider-conflict-2024-04-19/ , https://www.reuters.com/markets/commodities/gold-retreats-middle-east-tensions-ebb-2024-04-22/
- Oct30 2024 gold UP: https://www.kitco.com/news/off-the-wire/2024-10-30/us-election-uncertainty-pushes-safe-haven-gold-record-peak
- Nov6 2024 gold DOWN: https://www.kitco.com/news/off-the-wire/2024-11-06/gold-hastens-retreat-dollar-rallies-trump-victory
- Apr2 2025 initial gold UP: https://www.investing.com/news/economy/gold-climbs-on-safehaven-demand-ahead-of-us-reciprocal-tariffs-3961734
- Apr21/22/23 2025 up then down: https://www.kitco.com/news/off-the-wire/2025-04-21/gold-extends-record-run-breaks-above-3400oz-safe-haven-rush , https://www.kitco.com/news/off-the-wire/2025-04-23/gold-falls-2-trump-comments-fed-and-china-boost-risk-sentiment
- May7 2025 gold DOWN following reported May6 talks: https://fixedincome.fidelity.com/ftgw/fi/FINewsArticle?id=202505070442RTRSNEWSCOMBINED_L1N3RF0BD_1
- Jun13 2025 conflict gold UP: https://www.kitco.com/news/off-the-wire/2025-06-13/gold-advances-israel-iran-escalation-fuels-safe-haven-bids
- Jul22 2025 profit taking before US-Japan agreement: https://www.kitco.com/news/off-the-wire/2025-07-22/gold-retreats-five-week-high-investors-book-profits
- Oct13 2025 WGC risk warning: https://www.gold.org/goldhub/gold-focus/2025/10/gold-hits-us4000oz-trend-or-turning-point
- Oct21 2025 Reuters: https://www.reuters.com/world/india/golds-record-run-pauses-investors-book-profits-2025-10-21/
- Dec26 2025 official CME advisory: https://www.cmegroup.com/notices/clearing/2025/25-393.html
