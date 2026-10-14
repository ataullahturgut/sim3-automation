# OLAY-02 · 15 Dakikalık Ekonomik Olay Takibi — Kaynak ve Saat QA

**Araştırma kapsamı:** Yalnız kullanıcı onaylı **tam 15 dakikalık kronolojik ekonomik olay** yaklaşımının veri hazırlığı. **AL/SAT/ay getirisi veya işaretleme bu dosyada yoktur.** ANA-01 bölüm 0 karar otoritesidir. Günlük tek NY17/21:45 kapanışı yöntem değildir.

## 1. Gerçek 15 dakikalık kapsama

- `Europe/Istanbul` 1–31 Ocak takvim günlerinde **31 × 96 = 2.976 zorunlu kontrol noktası**. Kontrol noktası bir fiyat barı veya işlem değildir.
- TRT gününe çevrilmiş HistData spot-XAU: **1.926 satır, 1.922 tam 15 native-min bar ve 4 kısmi bar**. Kaynak `gold_research_histdata_xau15m_candidate`, `source_timezone=EST_FIXED_UTC_MINUS_05`, veriler zaten `bar_start_utc` ile UTC'ye dönüştürülmüş; yerel takvime yeniden çevrilerek karşılaştırılır.
- TRT gününe çevrilmiş `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2`: **1.824 M15 satırın tümü** `m1_matched=15`. Ne var ki tüm günler yok: **12, 17, 18, 19 Ocak TRT'de 0 satır**; 16 Ocak'ta 12 adet; 12 Ocak TRT'de HistData'da 88 tam bar varken Duka 0. Kaynaklardan biri diğerinin boşluğunu doldurdu diye quote `EXECUTABLE` sayılmaz. 1 Ocak tatil / 3-4 Ocak hafta sonu kaynağı ayrıca piyasa saatiyle denetlenir.
- HistData ile Dukascopy'nin **1.642 aynı-start tam 15m eşleşmesi**: `abs(HistData close - Duka BID/ASK MID)` medyan **$0,3382**, p95 **$0,8228**, maksimum **$2,9520**. Dukascopy ortalama BID/ASK spreadi **$0,7944**, negatif spread **0**. **Aşağıdaki KRİTİK DÜZELTME nedeniyle bu rakamlar bağımsız kaynakların uyumu olarak yorumlanamaz.** İcra, yalnız Duka mevcutsa teorik vekildir.
- Cache `xau_intraday_research_cache_1m`: `Twelve Data XAU/USD` araştırma sunucusunda Ocak dönemini kapsıyor; ancak piyasanın kapalı hafta sonu/tatil saatlerinde de çok sayıda kayıt var. **Onaylı işlem kotasyonu veya güvenilir spot 1m sayma**; `1MIN_PRELIMINARY / SUSPICIOUS_CLOSED_MARKET`. Kritik bir M15 tetik anının ilk dakika sırasını araştırmakta, ancak borsa/saat ve başka kaynaktan doğrulama ile yardımcı kullanılabilir.
- CME H1 `symbol.c.0`: ay boyunca `NQ.c.0=479`, `ZN.c.0=479`, `CL.c.0=473`, `SI.c.0=270`, `GC.c.0=107`. Bunlar **saatlik futures barları**, `ts_event` başladığı anda değil **bar tamamlandığında** as-of kullanılabilir; `ZN` fiyatı faiz yüzdesi değildir, `SI.c.0` calendar roll ve seyrek veri nedeniyle spot gümüşle eşdeğer değildir. Platin/paladyum, DXY/2Y spot/reel faiz aynı UTC eksiksiz değil.

**KRİTİK BAĞIMSIZLIK DÜZELTMESİ (ikinci SQL kontrolü):** Aynı saatli **1.642/1.642** bar için HistData OHLC değerlerinin **dördü de Dukascopy BID OHLC ile bit düzeyinde birebir aynı** (open=high=low=close karşılıklı eşitlik sayıları ayrı ayrı 1.642). `HistData.close` ve `Duka BID` bağımsız kaynak doğrulaması **DEĞİLDİR**; hangi ETL/ortak kökten kopyalama olduğu henüz saptanmadı. Eşleşen 1.642 bar, **tek fiyat örneği** sayılacak ve `SOURCE_INDEPENDENCE_FAIL` etiketi taşıyacak. Duka ASK-BID spreadi uygulama için *sağlayıcı fiyat vekili*, gerçek banka fiyatı değildir. Önceki $0,3382 medyan fark **yalnız BID ile BID/ASK MID farkının yarısıdır**, iki sağlayıcının birbirine yakın olmasının kanıtı değildir. Alanlar `HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_2025_2026` ve `DUKASCOPY_DIRECT_M1_BIDASK_2026_M15_NATIVE_FULL_V2` olarak ayrı `source_id` taşır, ama fiyat değerlerinin tümü ortak/yeniden üretilmiş olabilir. Bu sorun giderilmeden `CROSS_PROVIDER_PASS` yazılmayacak.

## 2. Kaynak-vintage ve haberin girebileceği kontrol zamanı

- Fed karar/statement resmi **28 Ocak 2026 14:00 EST = 19:00 UTC = 22:00 TRT**. İlk haberi 22:00 TRT anında gündeme al, 15 dakikalık **sonraki tamamlanmış** fiyat tepkisini ancak 22:15 TRT kontrolünde gözle (BLS/Fed bilgisi ile bar sonucu geleceğe bakılarak doldurulmaz). Kaynak: https://www.federalreserve.gov/newsevents/pressreleases/monetary20260128a.htm
- BLS resmi `Employment Situation` **9 Ocak 2026 08:30 EST = 13:30 UTC = 16:30 TRT**. NFP +50.000, işsizlik %4,4, ancak konsensüs zaman-vintage ilk veri dışında bağımsız doğrulanmadan `HAWKISH/DOVISH` sonuç kesin değildir. Kaynak: https://www.bls.gov/news.release/archives/empsit_01092026.htm
- BLS `CPI` **13 Ocak 2026 08:30 EST = 13:30 UTC = 16:30 TRT**; headline aylık %0,3, çekirdek aylık %0,2, headline yıllık %2,7. Yalnız sonuç, beklenti-sürpriz değildir. Kaynak: https://www.bls.gov/news.release/archives/cpi_01132026.htm
- BLS diğer planlı yayınlar (bazıları 7/8/14/15/29/30 Ocak) resmi yayın saatleri kontrol edilecek; takvimin güncel web görünümü sonradan değişmiş olabilir: orijinal arşiv/snapshot doğrulama olmadan sürpriz `as-of` kabul edilmez. https://www.bls.gov/schedule/2026/01_sched_list.htm
- Reuters Venezuela ilk piyasa raporunun ikincil sendikasyon kaydı **4 Ocak 23:00 EST = 5 Ocak 04:00 UTC**, 5 Ocak 02:55 EST güncellemesi. Bu **aynı haberin piyasa raporu** için güvenli yayın alt sınırıdır; hafta sonundaki operasyonun asıl *ilk duyuru saati değildir*. Kaynak: https://www.marketscreener.com/news/gold-surges-as-us-capture-of-venezuela-president-spurs-safe-haven-demand-ce7e59d9d08df026
- Reuters Grönland ticaret rahatlaması kaynak sayfası **22 Ocak 08:52 UTC güncellenmiş** gözükür; makale 21 Ocak olayını anlatır ama geriye dönük **21 Ocak ilk yayımlanma saati değildir**. Bu sayfa 21 Ocak 15 dakikalık erken karara **kaynak yapılamaz**: https://www.reuters.com/business/davos/determined-seize-greenland-trump-faces-tough-reception-davos-2026-01-21/

## 3. Uygulama alanı — kaynak hem sayısal hem anlatısal

Her TRT kontrol slotunun kaydı:

`check_trt,check_utc,bar_start,bar_end,bar_complete,bar_staleness,source_quality,price_provider,price_close,duka_bid,duka_ask,source_spread,h1_context_available_at,SI_age,ZN_age,NQ_age,CL_age,independent_evidence_at,news_id,firstprint_utc,trigger_DNA,transmission_DNA,amplifier_DNA,EPISODE_ID,phase,competing_mechanism,confidence_level,expected_remaining_range,portfolio_state,decision,order_quote_time,fee_and_spread,status`.

**Belirsizlikler korunur:** bir veri aynı anda erişilemiyorsa `MISSING`, geçmiş fiyatın 15 dakikadan eski olması `STALE`, pazar/kapanışta `CLOSED`; saatli haberin ekonomik ilk nedeni bilinmiyorsa `FIRSTPRINT_UNKNOWN`. `observed_at` tarihli haberden gelecekte olamaz. Dayanaksız `CONFIRMED` yazılmaz. İcra ve PnL ayrı deney safhasında gerçekleşir, bu QA puanları karar değildir.

**Kaynak denetimi notu:** 31 gün ve 2.976 slot takvimsel yükümlülüktür; ürün fiyat barları 24/7 değildir. **96 slot olmaması değil, 96 slot içinde eksik/kapalı işaretinin tutulmaması hatadır.**
