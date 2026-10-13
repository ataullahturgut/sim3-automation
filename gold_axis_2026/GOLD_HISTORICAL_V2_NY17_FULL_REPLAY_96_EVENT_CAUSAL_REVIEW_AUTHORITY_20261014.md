# GOLD: 2023–2025 geçmiş olaylar — NY17 düzeltilmiş TAM V1/V2 yeniden hesaplama ve haber–piyasa nedensellik denetimi
**Tarih:** 14 Ekim 2026. **Bilimsel statü:** `PRICE_REPLAY_COMPLETE / NEWS-CAUSE_TEST_PARTIAL / NO_IDENTIFIED_CAUSAL_SHARE / NOT_FORECAST_NOT_TRADING`. Tamamen geçmiş altın hareketlerinin hangi ekonomik bilgilerle açıklanabileceğini araştırır. **AL/SAT, işlem, kârlılık veya yeni yön tahmini yoktur.**

## 1. Fiyat otoritesi ve *gerçekten* yeniden üretilen aşamalar
- Veri: Neon `gold_research_evduka_xau15m_bidask_candidate`, EVTradingLabs/Dukascopy tarihsel M15 BID/ASK; altın mid=`(bid_close+ask_close)/2`. M15 timestamp bar BAŞLANGICI; fiyatın gözlem anı **bar_end=bar_start+15 dakika**.
- Önceki `DATE((bar_end AT TIME ZONE 'America/New_York')+INTERVAL '7h')` tam New York 17:00 bitiş barını ertesi seansa atabiliyordu. Düzeltilmiş `DATE((bar_end AT TIME ZONE 'America/New_York')+INTERVAL '7h'-INTERVAL '1 microsecond')` ile tam NY17 barı kendisine ait seansın kapanışıdır. Saatlik/Yaz Saati geçmişi timezone üzerinden hesaplandı. Gerçek M15 bar olmayan yere veri koyulmadı.
- Eski-yeni aynı **774 geçerli gün** (2023 257/2024 259/2025 258; günlük en az 70 gerçek M15 bar). Toplam **746 seansın** altın kapanış fiyatı eski etiketten farklı; 2023 **248**, 2024 **249**, 2025 **249**.
- **V1 ZigZag geri üretim:** 42/42 orijinal `>=3% reversal` bacağı eski saatle **tarih, yön ve yuvarlanmış yüzde eşit**. Aynı algoritmanın doğru saatli sonucu **42 bacak, 42 aynı yön**, **38 aynı uç gün**, dört gün sınırı değişen bacak (aşağıda).
- **V2 çok-ufuklu GERÇEK TAM eşik taraması:** 2023–25 eski 774 günün orijinal **1h,4h,12h gerçek duvar saati fiyatı** (tam bar-lag ve timestamp gap kontrolü) + **önceki 1,3,5 uygun NY17 seans** kapanış getirilerinin **TÜM SAYISAL DEĞERLERİ** orijinal V2 dosyasına `<0.000054` yüzde puan yuvarlama toleransında eşit; **774/774 bayrak ve tier etiketi bire bir eşit**. Aynı yönün bayraklı uygun günleri arası indeks farkı **en fazla 3** olduğunda gruplama: eski **53/53** cluster ilk/son gün, yön, gün sayısı, maximum fixed horizon yüzdesine dek **yeniden üretildi**.
- DÜZELTİLMİŞ aynı V2 kurallarıyla **154 PRIMARY en az %3 gün** (önce **151**), **18 ilave SECONDARY en az %2 hızlı gün** (önce **23**), **155 işaretli >=%3 yön/gün** (önce **152**). **10 günün tier'ı değişti.** Eski **53** signed cluster ⇒ **54 düzeltilmiş fiyat-cluster**.
- Bu `V2 threshold/direction/cluster` hesabının tamamlandığı anlamındadır, fakat orijinal V2 dosyasındaki ayrıntılı **intraday high–low price range ve bütün makro açıklama alanları** yeniden hesaplanmış/değiştirilmiş değildir. Eski ham dosyalar silinmedi ve düzeltilmiş yeni dosyalar ayrı tutuldu.

| Kontrol | Eski kaynak | NY17 düzeltilmiş | Kanıt dosyası |
|---|---:|---:|---|
| V1 günlük ZigZag | 42 bacak | **42 bacak** | [V1 old/new yeniden-üretim (42)](GOLD_HISTORICAL_42_V1_ZIGZAG_NY17_FULL_RESEGMENTATION_20261014.csv) |
| V2 PRIMARY >=%3 gün | 151 | **154** | [774 günlük eski/yeni ufuk+flag](GOLD_HISTORICAL_V2_NY17_CORRECTED_774_DAILY_HORIZON_REPLAY_20261014.csv) |
| V2 ek SECONDARY %2 hızlı gün | 23 | **18** | aynı 774-gün |
| V2 yönlü >=%3 bayrak | 152 | **155** | aynı 774-gün |
| V2 birleştirilmiş yönlü fiyat kümesi | 53 | **54** | [54 gerçek düzeltilmiş V2](GOLD_HISTORICAL_V2_NY17_CORRECTED_DIRECTIONAL_CLUSTERS_20261014.csv) |
| Ekonomik nedensellik | 95 fiyat kaydı (42+53) | **96 fiyat kaydı (42+54)** | [96 düzeltilmiş neden–haber ilişkisi veri indeksi](GOLD_HISTORICAL_CORRECTED_96_RECORD_EVENT_NEWS_CAUSAL_EVIDENCE_INDEX_20261014.csv) |

**ÖNEMLİ:** 96 fiyat KAYDI = 96 benzersiz haber/ekonomik şok değildir; fiyat etiketleri birbirini kapatabilir. V2 `first_flag_date` biriken hareketin eşik aştığı gündür; **ilk haber dakika/ilk fiyat dakika değildir**.

## 2. Düzeltilmiş önemli olay günleri
**V1 dört düzeltme:** `SWING_V1_028` DOWN 2025-04-02..**04-07** −4.776625% (eski son 04-08), `V1_029` UP 2025-**04-07**..04-21 +14.779037% (eski başlangıç 04-08), `V1_038` DOWN 2025-10-20..**10-29** −9.784683% (eski 11-04), `V1_039` UP 2025-**10-29**..11-12 +6.755117% (eski 11-04). [Aynı dört gün aralığı için değerli metal–hisse–petrol–ZN–GVZ **yeniden tarih uyumlu**](GOLD_HISTORICAL_4_RESEGMENTED_SWINGS_CORRECTED_CROSS_MARKETS_20261014.csv).

**V2 orijinal 53'ün `49`'u aynı yön/bayraklı gün/başlangıç-bitiş tarihini korudu; 4'ü değişti:**
- `C006 UP 2023-10-13..19` → `C_CORR_006 UP 2023-10-13..**20**`.
- `C038 DOWN 2025-05-**12**..16` → `C_CORR_039 DOWN 2025-05-**09**..16`. **Mayıs 9 değişimi çok kritik:** May9 günü tek seans altın +%0.551, ancak önceki **3 uygun seans** toplamı **≤−%3** olduğundan DOWN bayraklı. Bu ilk bayrak, **12 Mayıs resmi ABD–Çin tarife indirimi haberinden ÖNCE**; May12 açıklaması en fazla önce başlamış bir fiyat dalgasının *devamını/yeniden fiyatlamasını* etkileyebilir. May12 günü altın tek seans **−%2.636** ve 3 günlük DOWN bayrağı devam. [Reuters 7 ve 9 Mayıs mevcut müzakere beklentisi](https://www.reuters.com/markets/commodities/gold-falls-us-uk-trade-deal-weighs-safe-haven-appeal-us-china-talks-focus-2025-05-09/), [**12 Mayıs tarihli ABD–Çin resmî ortak açıklaması**](https://www.govinfo.gov/content/pkg/DCPD-202500592/html/DCPD-202500592.htm). **Müzakere beklentisi**, nihai anlaşmayla özdeşleştirilmez. Açıklamanın dakikalı gerçek firstprint'i ayrıca doğrulanmalı.
- `C043 DOWN 2025-07-30` → `C_CORR_044 DOWN 2025-**07-29..30**`.
- `C044 UP 2025-08-04..07` → `C_CORR_045 UP 2025-**08-07**`. 4 Ağustos'ta eski yüzde-3 UP bayrağı doğru kapanış serisinde bulunmuyor; ekonomik haber başlangıcı 4 Ağustos kabul edilmesin.

**TAMAMEN YENİ BEŞİNCİ KÜME:**
- `C_CORR_018` **13 Haziran 2024**, **DOWN**, önceki **5 uygun NY17 seans** toplam **−%3.019736**, ama o günkü tek seans **−%0.897849**. Dolayısıyla `−%3.02 olayın hepsi 13 Haziran gün içinde oldu` yanlıştır. [13 Haziran dönemine ait haber özeti Fed'in 12 Haziran güvercin CPI ardından sınırlı indirim projeksiyonu](https://www.marketwatch.com/story/gold-futures-settle-down-after-wednesday-s-brief-inflation-data-driven-rally-market-talk-0b0a0d31). **Fed/PPI ve beklenti kanalı adaydır**, ilki haber ilk baskısı ve gerçek USD/faiz ilk-tepki eşsaat analizi tamamlanmadan bu olayın nedeni olarak **ispatlanmaz**.
- [53 eski →54 yeni çapraz tablo, hiçbir eski nedensel anlatı otomatik aktarılmıyor](GOLD_HISTORICAL_V2_53_LEGACY_TO_CORRECTED_CLUSTER_CROSSWALK_20261014.csv).

## 3. NY17 hatası gerçekten ekonomik aday grubu değiştiriyor
Düzeltilmiş `V1_038` Ekim20..29 2025 altın **−%9.785**, gümüş **−%6.998**, S&P500 **+%2.308**, CME WTI **+%5.157**, GVZ **−6.73 puan**. Genel bütün-varlık tasfiyesine benzemiyor; metal/pozisyon yapısı ile ekonomik aktarımın ayrışması araştırılmalı.

Düzeltilmiş `V1_039` Ekim29..Kasım12 2025 altın **+%6.755**, gümüş **+%6.975**, S&P500 **−%0.576**, WTI **−%3.164**, GVZ **+1.12 puan**. **Eski `GOLD_AND_EQUITIES_UP` sınıfı YANLIŞLANIYOR; yeni gözlenen imza `GOLD_UP_EQUITY_DOWN`**. Bu bir güvenli liman mekanizması ARAŞTIRMA ADAYI, altına talep getiren asıl aktörün kanıtı değil.

Ek gerilim: **29 Ekim 2025 saat 14:00 EDT/18:00 UTC Fed açıklaması** [resmî duyuru](https://www.federalreserve.gov/newsevents/pressreleases/monetary20251029a.htm). Bizim XAU M15 ilk 15 dakikalık gözlemimiz **−%0.287657**, günün NY17 altın kapanış getirisi yaklaşık **−%0.568**. Ama **Ekim29..Kasım12 V1 uzun bacağı UP +%6.755**. Aynı gün Fed açıklaması olması, uzun UP bacağının *Fed açıklamasıyla başladığı* tezini ispatlamaz; tam tersine ilk açıklama penceresi düşüşü, **ikinci tetikleyici/sonraki geri dönüş** araştırılmasını gerektirir.

## 4. 96 olayda haber kaynak tarihinin rolü
[96 kaydın **doğru V1 ve doğru V2 fiyat zamanlarına** bağlanan tarih-haber-kanıt indeksi](GOLD_HISTORICAL_CORRECTED_96_RECORD_EVENT_NEWS_CAUSAL_EVIDENCE_INDEX_20261014.csv):
- **56/96** haberin bugünkü kaynak yayın tarihi, düzeltilmiş ilk fiyat anchor'ından **sonra**.
- **15/96** aynı takvim günü (dakika ilk basım garantisi YOK).
- **7/96** kaynak tarihi önce.
- **18/96** kayıt için tarihli özgül haber kaynağı yok (yeni 2024-06-13 dâhil).

Bu durumda `56 olayın nedeni çürütüldü` sonucu da, `72 olay kesin açıklandı` sonucu da **YANLIŞ**. V1 başlangıç extremum, V2 ilk eşik aşımı gerçek ekonomik fiyatın ilk dakikası değildir. WGC/Reuters raporları bazen yalnız ex-post bağlam sağlar; ilk yayımlanan olay-haber kronolojisi için onaylı UTC arşiv gerekir. Aynı makro duyuru birden fazla örtüşen fiyat kayıt satırını açıklamak için *aday* olabilir; sayıları bağımsız olay gibi şişirme.

## 5. Aynı habere karşıt çok-varlıklı piyasa tepkileri: sınama ve sayısal kontrol
Önceki 85 makro duyuru günü (`NFP=35 CPI=34 FOMC=16`, FOMC 2025 EKSİK) ×5 CME vadeli `CL,NQ,ZN,GC,SI` ayrı `enclosing H1` piyasa reaksiyonları hesaplandı. CL **84/85**, NQ **85/85**, 10Y tahvil **ZN FUTURES PRICE 79/85**, GC **50/85**, SI **30/85** uygun saatli karşılaştırma; XAU M15 85 kayıtla birleştirildi. **H1 aralığı M15 ile aynı 15dk değil**; tek bir fiyat kımıldaması bütün 1–3 saatin nedensel etkisi diye sunulamaz.

Makro duyuru fiyat imzası (XAU M15 ilk15; ZN futures yaklaşık pre/post H1; Nasdaq NQ futures yaklaşık pre/post H1):
| Gözlenen imza | Yayın kaydı |
|---|---:|
| XAU↓, ZN fiyatı↓, NQ↓ | 17 |
| XAU↓, ZN fiyatı↓, NQ↑ | 11 |
| XAU↓, ZN fiyatı↑ | 8 |
| XAU↑, ZN fiyatı↓ | 13 |
| XAU↑, ZN fiyatı↑, NQ↑ | 22 |
| XAU↑, ZN fiyatı↑, NQ↓ | 7 |
| Eksik eşleştirme | 7 |

Örnekler [makro 85 imza tablosunda](GOLD_HISTORICAL_85_MACRO_NEWS_XAU_M15_CROSSMARKET_H1_SIGNATURES_20261014.csv):
1. **3 Şubat 2023 NFP** (resmî BLS açıklaması +517 bin): XAU ilk15 **−%1.349**, ZN-price **−%0.676**, NQ **−%0.108**, COMEX GC **−%1.776**, fakat WTI **+%1.710** ⇒ `TÜM risk varlıkları aynı yönde satıldı` tezini bu pencerede desteklemiyor.
2. **10 Mart 2023** pozitif NFP sürprizine rağmen XAU **+%0.540**, ZN-price **+%0.615**, NQ **−%0.835**. Banka stresi ayrı rakip, [FDIC 16:42 UTC SVB bülteni](https://content.govdelivery.com/accounts/USFDIC/bulletins/34de35b) sabahki 13:30 fiyat tepkisinden **sonra**; bülten ilk sebep sayılamaz.
3. **7 Haziran 2024** PBoC altın alım-duraklama haberi **ABD NFP saatinden önce**, sonrasında NFP +272 bin 12:30UTC, XAU ilk15 **−%0.612**, ZN-price **−%0.796**, GC **−%0.960**; çift haber kaynağı ilk barına ayrılmalıdır.
4. **18 Aralık 2024 FOMC**, 19:00UTC resmî statement/projeksiyonlar, XAU ilk15 **−%0.760**, ilk60 **−%1.223**, NQ−%1.681, ZN-price−%0.626, GC−%1.051, SI−%0.955 => genel yeniden fiyatlama hipotezini destekleyen **saatli fiyat eşleşmesi**, saf politika sürprizinin payı ayrıştırılmadı.
5. **4 Nisan 2025 NFP**, XAU bültenden **önceki 60dk −%0.975**, ilk15 sonrası **−%0.261**, CME GC−%1.625, SI−%1.828, NQ **+%0.365**; duyuru önceki büyük satışın tek nedeni olamaz.

**Eksik resmî makro defterine 2025 FOMC düzeltmesi**: [2025 8 olağan Fed duyurusunun XAU 15dk + 4 haftalık aynı-saat kontrol karşılaştırmaları](GOLD_2025_FOMC_8_MISSING_EVENTS_XAU_M15_EXPLORATORY_REPAIR_20261014.csv) ve [8×5 CME vadeli](GOLD_2025_FOMC_8_MISSING_EVENTS_CME_5_ASSET_H1_20261014.csv), özgün [Astra 2020–25 USMPD release listesi PR #122](https://github.com/ataullahturgut/sim3-automation/blob/research-gold-fomc-mechanism-pilot-20261013/gold_axis_2026/GOLD_FOMC_PILOT_2020_2025_EVENT_LEVEL_V1_20261013.csv). Böylece **85 eski release +8 Fed 2025 =93 incelenmiş zamanlı makro duyuru**, bu resmî bütün açıklama takvimi değildir. 2025 FOMC 8'i ayrı kalite gözlemidir; eski 85 gözlemin placebo istatistiklerini 93'e otomatik yeniden puanlama YOK.

## 6. Bilimsel kanıt dereceleri ve eksik kalan işler
**UYGULANAN:**
- V1 42 eski ve düzeltilmiş kural tam-replay; V2 774 eski/düzeltilmiş eşik ve 53→54 kümeler tam-replay; 53 eski olayla **neden taşımadan** crosswalk oluşturma.
- 4 değişmiş V1 bacağının yeni tarihli XAG/ETF değil **XAG/XPT/XPD + S&P/NDX + CL/NQ/ZN + Cboe GVZ** retrospektif günlük karşılaştırması.
- 96 olay kaydının haber yayın-tarihi / fiyat-gün kronolojisi; 85+8 resmî makro yayımlanma saatlerine örnekleyen fiyat ve CME paneli.

**HENÜZ YAPILMAYAN / YAPILMIŞ GİBİ GÖSTERİLMEYECEK:**
- 96 kaydın tamamında haberin **orijinal ilk yayın dakikası**, arz/dolar/UST2Y/10Y/TIPS ve diğer metal/hisse/petrol **tam aynı 15dk ilk fiyat kanal paneli**, ETF/CFTC as-of akım ve pozisyon doğrulaması.
- Değişmiş **4 V2** ve **yeni 2024 Haziran** V2 için eski kaynaklara karışmayan **5-seans-before-first-flag → last-flag** karşılaştırması **6A bölümünde YENİ TAMAMLANDI**. Ancak 96 olayın tamamı için haberin asıl ilk dakikasına göre **eşsaatli metal/FX/faiz** karşılaştırması, aynı-olay onsets ve nedensel etki hâlâ EKSİK.
- Haberle tetiklenmesine rağmen büyük altın hareketi olmayan **bütün açıklama günleri ve şoksuz benzer piyasa günlerinin** eşleştirilmiş karşıt-faktör nedensel testi ve orijinal web ilk yayınları. Dönem/evre/rollover/holiday ve 2026'da indirilmiş geriye dönük kaynak hatası ayrı.
- Büyük hareketi **hangi yüzde katkıyla** belirli haberin yarattığını ekonometrik olarak ispatlamak. Uygun karşı olgusal/şok aracı ve belirsizlik yok.

**KADEME:** Kısmi `FIRSTPRINT_ONLY_SELECTED_OFFICIAL_MACRO`; gözlenen `MULTI_ASSET_PRICE_ASSOCIATION`; bazı ünlü neden hikâyelerinde `CANDIDATE_WEAKENED_BY_TIMING`. **Hiçbir yeni sayı, 96 gerçek ekonomik nedeni ispatladığımız iddiası değildir.** Önceki sekiz gruptaki 72 aday/23 belirsiz sayı tarihi ilk atlasın hipotez sınıflamasıdır; düzeltilmiş 96 olay yeni bir bilimsel doğrulanmış “72/96” oranı değildir.

## 6A. Beş YENİ veya tarih aralığı değişmiş V2 olayının çoklu piyasa eksik veri kapısı — SAYISAL TAMAMLANDI
[5 olayın altın dışı metaller/hisse/petrol/tahvil vadeli/GVZ ile doğru tarihli yeni karşılaştırması](GOLD_HISTORICAL_V2_5_CHANGED_OR_NEW_CLUSTERS_CROSSMARKET_CONTEXT_20261014.csv) araştırma arşivine eklendi. İlk bayrağın **önceki beş uygun NY17 seans kapanışı** ile son bayrak günü arasındaki günlük farklı sağlayıcı fiyatları ölçüldü; **özgün olayın ilk dakika tepkisi veya V2 max-horizon yüzde getirisi değildir**. Ayrıca **önceki tek NY17 seans kapanışından ilk bayrak gününe getiri** ayrıca tutuldu; gümüş/platin/paladyum, S&P500/Nasdaq, WTI CL ve ZN vadeli fiyatları için kaynakta bulunmayan değerler boş.

| Düzeltilmiş V2 küme | İlk/son bayrak | İlk bayrak günü tek-seans XAU | Önceki 5 seans kapanışı→son bayrak aralığında gümüş | S&P500 | WTI CL | GVZ (puan) |
|---|---|---:|---:|---:|---:|---:|
| `C_CORR_006` UP | 13–20 Eki 2023 | **+%3,424** | **+%9,946** | **−%1,958** | **+%7,499** | **+4,53** |
| `C_CORR_018` DOWN **YENİ** | 13 Haz 2024 | **−%0,898** | **−%3,482** | **+%1,509** | **+%2,987** | **−1,14** |
| `C_CORR_039` DOWN | 9–16 May 2025 | **+%0,551** | **−%0,711** | **+%4,778** | **+%7,040** | **+0,12** |
| `C_CORR_044` DOWN | 29–30 Tem 2025 | **+%0,405** | **−%2,369** | **+%0,844** | **+%5,937** | **−2,60** |
| `C_CORR_045` UP | 7 Ağu 2025 | **+%0,835** | **+%5,950** | **+%0,010** | **−%7,987** | **+0,91** |

**Neden bu ek bulgu önemli?** `DOWN` label'ı bazen **o gün XAU düşmüş** demek değildir. Örneğin yeni May9 ve Jul29 bayraklarının **tek-seans altın getirileri pozitiftir**, fakat geçmiş **3/5 seans penceresinde** negatif yüzde-3 eşik aşılmıştır. 2024 Haz13 yeni kümesinde altın −%0,898 tek-seans, beş seans -%3,0197; buna dayanarak bütün düşüşü yalnız o günkü Fed/PPI haberine yazmak bilimsel değildir. `UP` C_CORR_006 ise tarihli İsrail/Hamas krizini araştırmaya uygun altın+gümüş yükseliş / hisse düşüşü örneğidir; ancak olayın gerçek ilk haber 7 Ekim, bayrak başlangıcı 13 Ekim olduğundan haberin ilk tepkisi ile devamı farklıdır.

**Güncelleme:** Aşağıdaki 6. bölümde önce yazılmış `beş V2 düzeltilmiş yeni tarihli piyasa bağlamı yapılmadı` ifadesi, bu raporun daha erken sürümünü tanımlar ve artık **superseded** durumundadır. Günlük/takvim başlangıç-son dönemli **beş karşılaştırma tamamlandı**; buna karşılık **haber ilk baskı UTC'siyle beş olayın eşzamanlı XAG/XPT/XPD/DXY/2Y/10Y reaksiyonları ve nedensel ayrıştırması** hâlâ tamamlanmadı.

---

## 7. Dosya otoritesi / diğer aşamaları düzeltme
**Bu dosya önceki** [GOLD_HISTORICAL_CORRECTED_CLOCK_NEWS_CROSSMARKET_CAUSAL_EVIDENCE_RESULTS_20261014.md](GOLD_HISTORICAL_CORRECTED_CLOCK_NEWS_CROSSMARKET_CAUSAL_EVIDENCE_RESULTS_20261014.md) raporunda **“V2 still pending”** yazan durumu açıkça **GÜNCELLER**: çünkü sonradan 774 günlük V2 tüm ufuklar/tier ve signed-cluster yeniden üretimi **tamamlandı**. O dosyanın V1/95/85+8 sayısal kanıtı tarihli olarak doğrudur; V2 PENDING artık son statü değildir. Orijinal V1, V2, eski 95 atlas, 38 vaka, 2026 Astra raporu ve ana manifestteki Ocak 2026 özel dosyası değiştirilmez; ek sürüm ve çapraz kanıt olarak tutulur.

**Son bilimsel hüküm:** Fiyat olayının ne zaman gerçekleştiği ve eski verideki hataların gerçekte ne değiştirdiği artık çok daha iyi doğrulandı: 42 uzun +54 kısa fiyat kaydı. Olayların bir kısmında makro ilk duyuru ve çoklu piyasa tepkisi ilişkilendirildi; **ekonomik nedenlerin tümünün benzersiz biçimde ispatı henüz yok**. Bir sonraki aşama yalnız eksik haber ilk-baskı, EŞSAAT faiz/dolar/metaller ve rakip **nedensel** açıklamalar; yatırım stratejisi değil.
