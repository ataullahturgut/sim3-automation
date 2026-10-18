# 2 Şubat 2023 — OLAY-02 / ÖĞREN-03 / ETKİ-05 kapsama düzeltmesi

**18 Ekim 2026 | GOLD-ADAPTIVE-MODEL-APP-01 | CORRECTION / RESEARCH ONLY | NO TRADING SIGNAL**

## Sorun

[Ocak–Şubat A/B/C ilk fiyat-met­rik testinde](EVENT_DUAL_CLOCK_JANFEB_2023_COMPARATIVE_REPORT_20261018.md) yalnız 6 Ocak NFP, 12 Ocak CPI, 3 Şubat NFP ve 14 Şubat CPI tetikleyicileri üzerinden ekonomik olay saati açıldı. **2 Şubat'ta "K01–K19'dan anlık CPI/NFP etiketi çıkmıyor" doğrudur; "2 Şubat'ta ekonomik olay veya ÖĞREN-03 mekanizması yok" YANLIŞTIR.** İlk A/B/C raporundaki örnek kapsamı bu açıdan eksik. Dört olaylık skor bütün Ocak/Şubat ekonomik etki çalışmasının performansı gibi sunulmamalıdır.

## Tarihli kanıtlı haberler

1. **1 Şubat 2023 Fed:** Fed +25bp artış; Powell basın toplantısı ve piyasa politikasının yeniden fiyatlanması. 2 Şubat'a taşınan önceki bilgi/aktif mekanizma adayı. [Resmî Fed](https://www.federalreserve.gov/newsevents/pressreleases/monetary20230201a.htm).
2. **2 Şubat 2023 12:00Z / 15:00 TRT — BoE:** +50bp artışla politika faizi %4; [resmî karar](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2023/february-2023). Bu tarihli karar vardır; artışın ne kadarının beklenmedik olduğu bu araştırmada ölçülmemiştir.
3. **2 Şubat 2023 13:15Z / 16:15 TRT — ECB:** +50bp politika faiz artışı; [resmî karar](https://www.ecb.europa.eu/press/pr/date/2023/html/ecb.mp230202~08a972ac76.en.html). ECB 2022'de karar açıklamasının 14:15 CET'e taşındığını resmî olarak duyurmuştur [ECB saat açıklaması](https://www.ecb.europa.eu/press/pr/date/2022/html/ecb.pr220627~73acedf868.en.html).
4. **2 Şubat 2023 13:45Z / 16:45 TRT — ECB basın toplantısı:** Lagarde; resmi video [ECB webcasts](https://www.ecb.europa.eu/press/press_conference/html/index.en.html?date=2023-02-02) ve [Q&A](https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/2023/html/ecb.is230202~4313651089.en.html). Bu *başlangıç* zamanıdır; konuşmanın her alt cümlesinin ilk yayımlanma anı değildir.

**Ekonomik mekanizma eşleşmesi:** ÖĞREN-03 ORG01 (faiz beklentisi/fırsat maliyeti gevşemesi, önceki Fed etkisi), ORG02 (USD/faiz yeniden baskı oluşturması) ve ORG10 (önceki güçlü altın rallisi sonrası kâr alımı/doygunluk hipotezi); mümkün destekler/rekabetçi kanallar. İlgili 38 derin vaka `SWING_V1_002` (1 Şubat–24 Şubat 2023 geniş DOWN bacağı) `ORG02` birincil, `ORG10` ikincil aday taşır. **Bu geçerli 2 Şubat olay ilk-baskı mekanizma sertifikası DEĞİLDİR**; derin arşivde bu V1 için kaynak zamanlaması `AFTER_WINDOW_RETROSPECTIVE`, `firstprint=UNKNOWN`, `true_initial_catalyst=UNVERIFIED`.

## Neon fiyatları: dört saatlik pencereler

Kaynak: `gold_research_evduka_xau15m_bidask_candidate`, 2 Şubat 2023, `mid=(bid_close+ask_close)/2`, her fiyat yalnız kapanan M15 barın sonunda bilinebilir. **Özel BoE/ECB 15m olay-şok çalışması ayrı olarak henüz eski tam CORE S1/S2/S3 işlem sistemine bağlanmadı.** Karar sonrası getiri etiketi olay saatindeki tahmin değildir.

| Referans / Türkiye saati | Yayın öncesi son kapanış MID | +15dk MID | +1s MID | +4s MID | +4s değişim |
|---|---:|---:|---:|---:|---:|
| BoE karar 15:00 | 1954.820 | 1954.975 | 1953.540 | 1926.240 | **−%1.462** |
| ECB karar 16:15 | 1953.190 | 1952.340 | 1946.560 | 1918.380 | **−%1.782** |
| ECB basın toplantısı başlangıcı 16:45 | 1948.665 | 1944.400 | 1938.065 | 1914.965 | **−%1.729** |

**Kritik çakışma:** Bunların 4s pencereleri birbiri içine girer; 15:00 BoE etkisi, 16:15 ECB kararı ve 16:45 ECB söylemi tek tek bağımsız fiyat etkisi gibi sayılmaz. ECB basın toplantısının başladığı **16:45 TRT** ile S2 fiyat rejiminin daha önce ayrıca yeniden üretilmiş **START DOWN 16:45 TRT** zamanı çakışmaktadır. Ancak fiyat kapanış/sinyal timestamps ve ECB *konuşulan bilginin* ilk erişim zamanı olmadan bu çakışmayı "ECB düşüşü başlattı" diye kanıtlama. 3 Şubat NFP (517k) 2 Şubat kararı anında bilinmiyordu.

## ETKİ-05 için gereken yeni K etiket alanları

Mevcut `K01–K19` büyük ölçüde NFP/CPI sürprizi ve bazı gözlenmemiş USD/reel getiri şartlarıyla sınırlı. Para politikası duyuruları için **kanıt koşuluna bağlı** yeni maddeler gerekir:
- `K_POLICY_CB_RATE_DECISION`: hangi merkez bankası, gerçek karar, *beklenen karar / konsensüs / önceki forward*, ilk erişim.
- `K_POLICY_GUIDANCE_HAWKISH_OR_DOVISH`: yeni yönlendirme metni ve beklentiye göre değişim, cümle seviyesinde ilk yayın/erişim, bağımsız kaynak.
- `K_POLICY_CROSS_CB_DIVERGENCE`: Fed/ECB/BoE açıklamalarının **eşzamanlı as-of politika patikaları** bakımından göreli ayrışması; yalnız 25bp/50bp farkını sapma diye yorumlama.
- `K_POST_EVENT_USD_YIELD`: aynı saniyede/ilk tamamlanmış bara uygun USD/US nominal-reel faiz ve değerli metallerin doğrulanmış tepkisi. Kaynak yoksa `UNKNOWN`.
- `K_PRIOR_GOLD_RUNUP`: önceki piyasa ralli/doygunluk bağımsız tamamlanmış fiyat/pozisyon bilgisi; ORG10 kâr alma nedeni olarak doğrudan kesinleştirilmez.

Bu tanımlar **öneri**, henüz çalıştırılmış/kalibre edilmiş K20+ kodları veya S3 kuralı değildir.

## Düzeltici sonuç

`FEB02_EVENTS_EXIST=YES`; `EXISTING_OLAY02_LONG_SWING_COVERS_DATE=YES`; `OGREN03_ORG01_ORG02_ORG10_RELEVANT_HYPOTHESES=YES`; `ETKI05_K_POLICY_TAGS=NOT_IMPLEMENTED`; `OLD_AB_C_4_RELEASES_ONLY=INCOMPLETE`; `FULL_2023_JANFEB_EVENT_CLOCK_PERFORMANCE=NOT_MEASURED`; `CAUSAL_ORG_CONFIRMATION=NO`; `CORE_TRADES=NONE`.

**Doğru sonraki yürüyüş:** 1 Şubat Fed → 2 Şubat BoE/ECB karar ve metin parçaları, eski fiyat ve makro kaynak saatlerini koruyarak ayrı t0/üst üste aktif mekanizma zincirleriyle ölçülsün; teyitli sinyalin olmadığı kısım fiyat-only kalmaya devam etsin. 2 Şubat'ın "olaysız" olduğu hiçbir raporda varsayılmasın.
