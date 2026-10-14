# ALTIN — 2023–2025 tarihsel olayların ekonomik neden–sonuç incelemesi: ilk sayısal epizot denetimi
**14 Ekim 2026 | İleri tahmin / al-sat yok | Çalışma durumu: 96/96 kayıt için fiyat–zaman çapraz eşlemesi; 10 araştırma epizodunda derinleştirilmiş tarihli kaynak ve 7 makro duyuru için karşılaştırmalı tepki.**

## Kısa bilimsel hüküm
Tüm 96 kaydın fiyat yönü, ufku, NY17 ilk eşik günü ve uzun bacak bağlantısı hesaplandı. **96 ekonomik neden ispatı yapılmadı.** 42 V1 ZigZag bacağı birbirine bitişik *fiyat segmentleridir*; bunları 42 benzersiz tarihsel şok olarak saymıyoruz. 54 V2 kaydı bu fiyat segmentleri üzerinde kısmen örtüşen başka ölçümlerdir. Bu sürümde 10 ekonomi-tarih epizodu seçilerek olayların kronolojisi ve alternatif açıklamaları gerçekten sınandı; 96 satırlık kanıt tablosundaki diğer kayıtlar büyük ölçüde tarihli kaynak bağlamı düzeyindedir. Önceki 60/36 ya da Claude 28/52/15 dereceleri istatistiksel olarak doğrulanmış nedensel başarı oranları değildir.

## A. Tekrarlanabilir fiyat-epizot ayrıştırması
| Fiyat-kronoloji kontrolü | Sayı |
|---|---:|
| V1 düzeltilmiş uzun ZigZag fiyat segmenti | 42 |
| V2 düzeltilmiş çok-ufuklu olay kümesi | 54 |
| V2 ilk bayrağında V1 ile aynı yön | 39 |
| V2 ilk bayrağında V1 ile ters yön (ham) | 15 |
| Bunlardan V1 dönüş tarihine denk geldiği için muğlak | 12 |
| Dönüş tarihi muğlaklığı olmadan V1 trendiyle ters V2 ilk bayrak | 3 |
| V2 aralığı birden fazla V1 segmentine dokunuyor | 25 |
| Kısa küme atanan V1 segmenti | 34 |
| Kısa küme atanmayan V1 segmenti | 8 |

**Önemli kural:** V2 birikimli/çok-ufuklu DOWN ilk bayrağı, mutlaka bayrak gününün tek-seans getirisinin negatif olduğu anlamına gelmez. V1 ise sonradan teyit edilmiş uç noktaya dayalı uzun fiyat bacağıdır. Aynı duyuru veya aynı gün iki farklı fiyat kaydına bağlanabilir; kesişim kendi başına ortak neden kanıtı değildir. V1 sınır günleri her iki bacağa ait olabildiğinden 12 kayıt ayrı `PIVOT_DATE_AMBIGUOUS` olarak korunmuştur.

Belirsiz sınır günleri hariç üç ters-yön V2 olayının ilk bayrağı: **C_CORR_013 (12.04.2024), C_CORR_018 (13.06.2024), C_CORR_049 (17.10.2025)**. Bu olayları fiyat etiketi hatası değil, kısa ve uzun ufukların ayrı ekonomik hikâyelerini araştırma nedeni olarak tutuyoruz.

## B. Haber saatli olay çalışması — aynı saat kontrolü
Veri: GitHub araştırma dalında tarihsel EV/Dukascopy XAU M15 release event-study; orijinal 85 CPI/NFP/FOMC defterinin tam kaynak verisi ve ayrıca eksik 2025 FOMC onarımı. `İlk15` log-getiridir (%); kontrol önceki dört haftanın aynı hafta-günü/saatindeki 15 dakikalık fiyat hareketidir. Kontrollerin hepsi makro bakımından steril değildir ve yalnız **N=4** kontrol vardır. Sonuçlar tekil olayda fiyat tepkisinin büyüklüğünü, **nedensel payını değil**, tanımlar.

| Duyuru (UTC) | Altın ilk15, % | Dört kontrolün medyan mutlak hareketi, % | Tepki / medyan | Kontrollerden büyük |
|---|---:|---:|---:|---:|
| NFP_2023-02-03 (13:30) | -1.349 | 0.080 | 16.76× | 4/4 |
| NFP_2023-03-10 (13:30) | +0.540 | 0.027 | 20.03× | 4/4 |
| NFP_2024-06-07 (12:30) | -0.612 | 0.059 | 10.33× | 4/4 |
| FOMC_2024-06-12 (18:00) | -0.402 | 0.079 | 5.11× | 4/4 |
| FOMC_2024-12-18 (19:00) | -0.760 | 0.056 | 13.62× | 4/4 |
| NFP_2025-04-04 (12:30) | -0.261 | 0.046 | 5.71× | 4/4 |
| FOMC_2025-10-29 (18:00) | -0.288 | 0.100 | 2.89× | 4/4 |

**Yanlışlama:** 4 Nisan 2025 NFP açıklamasından önceki son 60 dakika XAU hareketi **−%0,974868** idi. Dolayısıyla en az bu fiyat düşüşü, 12:30 UTC istihdam açıklamasının *sonucundan* kaynaklanamaz. Yine aynı gün açıklama sonrası ilk15 yaklaşık −%0,261 idi; iki alt olay ayrılmalıdır. 29 Ekim 2025 Fed ilk15 −%0,288 ve ilk60 −%0,638 iken 29 Ekim–12 Kasım uzun bacağı +%6,755 olduğu için tek gün Fed → tüm toparlanma UP anlatısı da kanıtlı değildir.

## C. On somut epizodun olay örgüsü, alternatif nedeni ve yanlışlama denetimi

### E01. 2023-02-24 to 2023-05-04 banking stress and gold uptrend
- **Fiyat kapsamı:** SWING_V1_003;C_CORR_003 — SWING_V1_003 +13.200%; C_CORR_003 +6.496% 3/5-day/horizon.
- **Haber kronolojisi:** 2023-03-10 13:30Z payroll announcement; 2023-03-10 16:15Z SVB closure; FDIC bulletin 16:42Z.
- **Ölçülen piyasa tepkisi:** XAU first15 after NFP +0.540%; ZN 1h enclosing +0.615%, NQ enclosing -0.835%.
- **Test edilen ekonomik aktarım:** Bank funding stress → haven demand / bond price rise; wage/job surprise alternative.
- **Karşıt kanıt / yanlışlama:** 16:42 FDIC bulletin cannot cause 13:30 XAU impulse; preexisting bank distress may have been known.
- **Bilimsel sonuç:** `T2_EVENT_WINDOW_OBSERVED_COMPETING_CAUSES_UNRESOLVED`. Bu sınıf **nedensel yüzde katkısı veya ilk fiyat-onset doğrulaması değildir.**
- **Kaynak:** https://www.fdic.gov/news/speeches/2023/spmar2923.html; https://content.govdelivery.com/accounts/USFDIC/bulletins/34de35b

### E02. 2024-05-20 to 2024-06-07 PBoC pause plus payroll shock
- **Fiyat kapsamı:** SWING_V1_016;C_CORR_017 — V1 -5.459%; V2 2024-06-07 DOWN max 3.592%.
- **Haber kronolojisi:** PBoC buying pause was reported before 2024-06-07 NFP 12:30Z.
- **Ölçülen piyasa tepkisi:** XAU first15 after NFP -0.612%; ZN enclosing -0.796%, GC enclosing -0.960%.
- **Test edilen ekonomik aktarım:** First central bank marginal demand expectation changed, then NFP → rates/dollar repricing.
- **Karşıt kanıt / yanlışlama:** NFP cannot explain preceding morning price weakness; PBoC alone cannot explain later NFP postrelease impulse.
- **Bilimsel sonuç:** `T2_TWO_SEPARABLE_CATALYSTS_NO_UNIQUE_CAUSAL_SHARE`. Bu sınıf **nedensel yüzde katkısı veya ilk fiyat-onset doğrulaması değildir.**
- **Kaynak:** https://www.reuters.com/markets/commodities/gold-prices-dip-china-central-bank-holds-off-buying-2024-06-07/; https://www.bls.gov/news.release/archives/empsit_06072024.htm

### E03. 2024-06-12 to 2024-06-13 5-session DOWN threshold inside upward trend
- **Fiyat kapsamı:** SWING_V1_017;C_CORR_018 — V1 +7.633%; corrected V2 -3.019736% over preceding five sessions, flag-day -0.898%.
- **Haber kronolojisi:** 2024-06-12 Fed statement and SEP 18:00Z; 2024-06-13 PPI release 12:30Z.
- **Ölçülen piyasa tepkisi:** XAU first15 after 12 Jun Fed -0.402%; no identified first impulse for whole 5-session move.
- **Test edilen ekonomik aktarım:** Rate path / expectation revisions + other prior information; cumulative drawdown.
- **Karşıt kanıt / yanlışlama:** Neither 12 Jun Fed nor 13 Jun PPI can initiate all price movement accumulated over five sessions.
- **Bilimsel sonuç:** `T1_TIME_CONTRADICTION_SINGLE_NEWS_ONSET_REJECTED`. Bu sınıf **nedensel yüzde katkısı veya ilk fiyat-onset doğrulaması değildir.**
- **Kaynak:** https://www.federalreserve.gov/newsevents/pressreleases/monetary20240612b.htm; https://www.bls.gov/news.release/archives/ppi_06132024.htm

### E04. 2024-11-15 to 2024-11-22 Russia-Ukraine tensions
- **Fiyat kapsamı:** SWING_V1_021;C_CORR_027 — V1 +5.974%; V2 max +5.974%.
- **Haber kronolojisi:** 2024-11-19 Russia updated its nuclear doctrine after conflict escalation.
- **Ölçülen piyasa tepkisi:** Reported contemporaneous gold/yen/bund haven bid, not independently matched UTC 15-minute XAU panel here.
- **Test edilen ekonomik aktarım:** Geopolitical escalation → haven premium → gold and yen, duration bid.
- **Karşıt kanıt / yanlışlama:** Movement started by 15 November; 19 Nov event cannot explain preceding trend.
- **Bilimsel sonuç:** `T1_DATED_CONTEMPORANEOUS_NEWS_PRICE_FIRSTPRINT_MISSING`. Bu sınıf **nedensel yüzde katkısı veya ilk fiyat-onset doğrulaması değildir.**
- **Kaynak:** https://www.reuters.com/markets/global-markets-russia-urgent-2024-11-19/

### E05. 2024-12-18 FOMC broad repricing
- **Fiyat kapsamı:** SWING_V1_024;C_CORR_030 — V1 -4.898%; V2 DOWN max 4.898% (multi-session).
- **Haber kronolojisi:** 2024-12-18 19:00Z Fed rate decision+projections.
- **Ölçülen piyasa tepkisi:** XAU first15 -0.760%; first60 -1.223%; CME enclosing GC -1.051%, SI -0.955%, ZN price -0.626%, NQ -1.681%.
- **Test edilen ekonomik aktarım:** Policy path + rate repricing and broad risk sell, not rate cut direction alone.
- **Karşıt kanıt / yanlışlama:** same-time Fed statement and SEP cannot be separately credited; H1 CME window != M15 XAU window.
- **Bilimsel sonuç:** `T2_POLICY_REPRICING_SUPPORTED_SHARE_UNKNOWN`. Bu sınıf **nedensel yüzde katkısı veya ilk fiyat-onset doğrulaması değildir.**
- **Kaynak:** https://www.federalreserve.gov/monetarypolicy/fomcpresconf20241218.htm

### E06. 2025-04-02 to 2025-04-21 tariff shock, initial liquidation, rebound
- **Fiyat kapsamı:** SWING_V1_028;SWING_V1_029;C_CORR_034;C_CORR_035 — V1 -4.777% Apr2-7, then +14.779% Apr7-21.
- **Haber kronolojisi:** 2 April tariffs, subsequent escalations, 4 April NFP 12:30Z.
- **Ölçülen piyasa tepkisi:** Apr 4 pre-NFP 60m XAU -0.975%, post-NFP first15 -0.261%; Apr2-7 SPX -10.734%, CL -13.813%.
- **Test edilen ekonomik aktarım:** Initial gold liquidation / margin funding during broad risk sell, later safe-haven/weak USD/tariff uncertainty premium.
- **Karşıt kanıt / yanlışlama:** NFP does not cause earlier fall; blanket risk-off => gold up contradicted by early metal selloff; WGC May retrospective cannot be a firstprint.
- **Bilimsel sonuç:** `T2_MULTIPHASE_DESCRIPTIVE_EXPLICIT_PRE_RELEASE_COUNTEREXAMPLE`. Bu sınıf **nedensel yüzde katkısı veya ilk fiyat-onset doğrulaması değildir.**
- **Kaynak:** https://www.gold.org/goldhub/gold-focus/2025/04/weekly-markets-monitor-tariffs-spare-no-land; https://www.gold.org/goldhub/research/gold-market-commentary-april-2025

### E07. 2025-05-09 to 2025-05-16 trade talks and tariff agreement
- **Fiyat kapsamı:** SWING_V1_032;C_CORR_039 — V1 May6-14 -7.411%; V2 May9-16 DOWN max 5.564%; May9 single session +0.551%.
- **Haber kronolojisi:** 9 May US-China talks expected; official tariff joint statement dated May12.
- **Ölçülen piyasa tepkisi:** 9 May V2 flag occurs BEFORE May12 official source; no synchronized news minute yet.
- **Test edilen ekonomik aktarım:** Anticipated trade easing → safe-haven premium unwind; May12 agreement → subsequent repricing possible.
- **Karşıt kanıt / yanlışlama:** May12 agreement cannot initiate May9 flag; May9 positive single day is not evidence of spot decline on May9.
- **Bilimsel sonuç:** `T1_CLEAR_REVERSE_DATE_CAUSALITY_REJECTED`. Bu sınıf **nedensel yüzde katkısı veya ilk fiyat-onset doğrulaması değildir.**
- **Kaynak:** https://www.govinfo.gov/content/pkg/DCPD-202500592/html/DCPD-202500592.htm; https://www.reuters.com/markets/commodities/gold-falls-us-uk-trade-deal-weighs-safe-haven-appeal-us-china-talks-focus-2025-05-09/

### E08. 2025-07-29 to 2025-07-30 inverse first flag versus Fed
- **Fiyat kapsamı:** SWING_V1_036;C_CORR_044 — V2 flag 29 July DOWN 3-day/5-day threshold despite 29 July single-day +0.405%.
- **Haber kronolojisi:** Fed policy release July30 18:00Z.
- **Ölçülen piyasa tepkisi:** No price-firstprint linked to 29 July threshold; H15 following Fed different day.
- **Test edilen ekonomik aktarım:** Pre-Fed positioning / policy anticipation distinct from outcome.
- **Karşıt kanıt / yanlışlama:** July30 FOMC cannot be first news of July29 threshold.
- **Bilimsel sonuç:** `T1_TEMPORAL_COUNTEREXAMPLE_FIRST_CATALYST_REJECTED`. Bu sınıf **nedensel yüzde katkısı veya ilk fiyat-onset doğrulaması değildir.**
- **Kaynak:** https://www.federalreserve.gov/monetarypolicy/monetary20250730a.htm

### E09. 2025-10-17 to 2025-10-29 peak, momentum reversal and late ETF outflows
- **Fiyat kapsamı:** SWING_V1_037;SWING_V1_038;C_CORR_048;C_CORR_049 — V1 Jul30-Oct20 +32.998%; Oct20-29 -9.785%; V2 DOWN flag Oct17 before V1 peak.
- **Haber kronolojisi:** Oct17 V2 DOWN looks back 3/5 days; Oct20 top; Oct21 abrupt fall; ETF day Oct21 inflows +$334m despite price fall.
- **Ölçülen piyasa tepkisi:** Oct20-29 SPX +2.308%, oil +5.157%, silver -6.998%, GVZ -6.73 index points.
- **Test edilen ekonomik aktarım:** Gold-specific momentum crowding/long liquidation; ETF outflows emerged afterward (not price-onset mechanism confirmed).
- **Karşıt kanıt / yanlışlama:** Oct21 ETF outflow-initiated crash contradicted by reported same-day ETF net inflow; WGC Nov6 ex-post cannot be Oct20 firstprint.
- **Bilimsel sonuç:** `T2_CROSS_SOURCE_CONTRAINDICATES_INITIAL_ETF_FLOW_NARRATIVE`. Bu sınıf **nedensel yüzde katkısı veya ilk fiyat-onset doğrulaması değildir.**
- **Kaynak:** https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2025/11; https://www.gold.org/goldhub/research/gold-market-commentary-october-2025

### E10. 2025-10-29 to 2025-11-12 gold recovery against equities
- **Fiyat kapsamı:** SWING_V1_039;C_CORR_050 — V1 +6.755%; silver +6.975%, SPX -0.576%, CL -3.164%.
- **Haber kronolojisi:** 2025-10-29 Fed statement 18:00Z.
- **Ölçülen piyasa tepkisi:** XAU first15 post-Fed -0.288%, first60 -0.638%, while Oct29-Nov12 V1 net UP.
- **Test edilen ekonomik aktarım:** Later gold-specific demand / rate path and equity hedge candidates; not confirmed haven cause.
- **Karşıt kanıt / yanlışlama:** Initial Fed reaction DOWN contradicts simple statement that Fed immediately initiated the subsequent UP leg.
- **Bilimsel sonuç:** `T2_SIGN_REVERSAL_INITIAL_NEWS_VS_LATER_LEG`. Bu sınıf **nedensel yüzde katkısı veya ilk fiyat-onset doğrulaması değildir.**
- **Kaynak:** https://www.federalreserve.gov/newsevents/pressreleases/monetary20251029a.htm; https://www.gold.org/goldhub/research/gold-market-commentary-october-2025

## D. 96 kaydın son kanıt durumu ve eski sınıflandırmaya düzeltme
**24 fiyat kaydı**, yukarıdaki 10 epizottan en az biriyle eşleştirilip ayrıca tarihli kaynak/ölçülü duyuru tepkisi bakımından denetlendi. Diğer **72 kayıt** için eldeki çalışma, tarihli haber bağlamını olay fiyatıyla birleştirmektedir; ilk haberin tam orijinal yayın anı, aynı UTC dolar/reel faiz ve karşıt haber denetimleri henüz yeterli değildir. Buradaki 24/72 sayısı *önceliklendirilmiş inceleme kapsamıdır*; 24’ünün güçlü ve 72’sinin zayıf olduğu sonucu çıkarılamaz. Dönemin tüm 96 kaydında doğrulanmış tekil “olay bütün hareketin nedeni oldu” hükmü YOKTUR.

Eski Claude 95 kaydı, bazı farklı tarihli V2 ilk bayraklar ve eski NY17 sınırı nedeniyle doğrudan nedensel etiketin otoritesi değildir. Üç eksenli taksonomi **tetikleyici ailesi / ekonomik aktarım kanalı / fiyat tepkisi zaman yapısı** ile korunmalı; bundan sonra özel olaylar `hazırlık → haberin ilk basımı → ilk 15dk → 1 saat → devam → tersine dönüş` aşamalarına ayrılmalıdır. Örneğin 2025 Ekim ETF *ilk sebep* iddiası WGC verilerindeki aynı gün pozitif ETF akış gözlemiyle desteklenmez; piyasa hareketini takiben gelen fon çıkışı olasılığı daha tutarlı bir alternatif açıklamadır.

## E. Bilimsel test kapıları ve sınırlarımız
1. **Fiyat ve saat:** Düzeltilmiş 774 gün NY17, M15 gerçek BID/ASK barı. Olay listeleri ilk duyuru anını içermez; V1 dönüş günü sonradan, V2 ilk bayrak gününün çok-ufuklu eşiğiyle belirlenir.
2. **İlk duyuru:** Kaynak metni olaydan *sonra* yayımlandıysa olay öncesi sebep gibi gösterilmez. Bu çalışmada 2023 FDIC, Fed/BLS saatleri seçili olaylarda resmî kaynakla doğrulandı; 96 kaydın tamamında orijinal ilk-baskı dakikası doğrulanmadı.
3. **Çoklu fiyat aktarımı:** CME H1 *enclosing* getiri penceresi XAU M15 ilk15 ile aynı değil; ZN **tahvil vadeli fiyatıdır**, 10 yıl tahvil faizi değildir. Farklı pencerelerden aynı anda nedensel işaret katsayısı hesaplanmadı.
4. **Kontrol:** Dört haftalık saat kontrolü yalnız koşullu fiyat büyüklüğü kıyasıdır. Çakışan makro haberli bazı kontroller var; güven aralığı, randomize karşılaştırma veya konjonktüre göre eşleşmiş karşı-olgu yok.
5. **Yayın/vintage:** ETF ve WGC aylık raporlarını olaydan önce piyasada biliniyormuş gibi kullanma. COT, VIX/GVZ, Fed sürprizi, DXY, 2Y/10Y/TIPS PIT/gerçek zaman veri saati ayrı tutulmalı.
6. **Hedef:** Olaylar açıklanana kadar AL/SAT/TUT yok; 2026, işlem bedelleri, banka emirleri veya ileri dönük performans bu raporun konusu değil.

## F. Yeniden üretim, ek veri dosyaları ve kayıt
- `build_economic_episode_crosswalk.py`: 96 fiyat kaydından tam tarih/interval crosswalk ve 42 V1 uzun-bacak bağlantısı.
- `GOLD_96_TO_42_V1_54_V2_INTERVAL_CROSSWALK_20261014.csv`: 54 satır kısa/uzun ilişki, dönüş günü belirsizliği ve çoklu bacak çakışmaları.
- `GOLD_42_LONG_LEGS_WITH_SHORT_SHOCKS_20261014.csv`: 42 V1 uzun fiyat bacağı, her biri için alt V2 kayıtlarının listesi.
- `GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv`: 96 kayıt, kaynak haberleri, hipotez ve açık bilimsel sınırlama.
- `GOLD_10_EPISODE_CAUSAL_FALSIFICATION_VERDICTS_20261014.csv`: 10 gerçek derin olay örgüsü ve yanlışlama gerekçesi.
- `GOLD_SELECTED_MACRO_RELEASE_VS_4_CLOCK_CONTROLS_20261014.csv`: 7 resmi açıklamanın ilk15 ve önceki dört aynı-saat fiyat karşılaştırmaları.
- `build_gold_causal_evidence_20261014.py`: olaya özgü iddia kaydı ve zamanlı kontrol puanlarının yeniden üretimi; sayılar sabit kaynak CSV’den kanıtlanarak alınmıştır.

**Kaynak otoritesi:** `ataullahturgut/sim3-automation`, açık araştırma dalı `research-gold-jan26-two-factor-confirmation-v4-20261013`, 2026-10-14 `GOLD_HISTORICAL_V2_NY17_FULL_REPLAY_96_EVENT_CAUSAL_REVIEW_AUTHORITY_20261014.md`; `GOLD_2023_2025_CPI_NFP_FOMC_M15_RELEASE_WEEKMATCH_EVENTSTUDY_20261014.csv`; `GOLD_2025_FOMC_8_MISSING_EVENTS_XAU_M15_EXPLORATORY_REPAIR_20261014.csv` ve beş önemli yeni düzeltilmiş V2 karşılaştırması. Ek olay kaynakları ilgili vaka altında açık URL ile kayıtlıdır.