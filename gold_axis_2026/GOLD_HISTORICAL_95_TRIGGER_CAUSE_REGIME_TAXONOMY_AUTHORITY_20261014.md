# GOLD INTRAMONTH — Tarihsel fiyat hareketlerinin tetikleyici × güçlendirici × risk rejimi sınıflandırması V1
**Tarih:** 2026-10-14 · **Otorite:** `RESEARCH CANDIDATE GROUPING / NO FULL CAUSAL IDENTIFICATION / NOT PRODUCTION`.
**Bağlayıcı 95 satırlık sayısal atlas:** [GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv). Olayların daha önceki 291 kaynak kaydı: [GOLD_HISTORICAL_EVENT_MASTER_CROSSWALK_V1_20261013.csv](GOLD_HISTORICAL_EVENT_MASTER_CROSSWALK_V1_20261013.csv). İlişkili 38 derin araştırma: [GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Makro kontrollü olay çalışması: [GOLD_HISTORICAL_SHOCK_CAUSAL_FALSIFICATION_MACRO_EVENTSTUDY_AUTHORITY_20261014.md](GOLD_HISTORICAL_SHOCK_CAUSAL_FALSIFICATION_MACRO_EVENTSTUDY_AUTHORITY_20261014.md).

## 1. Doğru nedensel yapı
1. **İlk koşullar (antecedents):** D-1'e kadar yayımlanan gerçek CFTC/ETF, GPR/rejim, önceki altın ve diğer metal getirileri, D-1 GVZ/VIX, önceki faiz/FX ve fiziki talep. Bu, olaydan *önce* varsa yalnız koşullayıcıdır.
2. **Yeni bilgi (trigger, candidate):** Fed/CPI/NFP gerçek açıklaması; tarife kararı veya ticaret antlaşması; savaş/banka iflası; Çin Merkez Bankası duyurusu; CME teminat gereksinimi. Tarihli kaynak olayın *ilk baskı anı* ve ilk 15m fiyat tepkisiyle eşleşmedikçe neden **ispatlanmış** sayılmaz.
3. **Aktarım ve kuvvetlendirme (amplifier):** DXY/nominal-reel tahvil getiri yeniden fiyatlaması; ETF/CFTC/COMEX poziyon azaltımı veya pozisyon artışı, açık pozisyon, fiziki EFP/arbitraj; fonlama/likidite, stop/marjin tasfiyesi.
4. **Eşzamanlı fiyat tepkisi ve rejim:** XAU/XAG/XPT/XPD, S&P500/Nasdaq, WTI Brent, GVZ/VIX/diğer endeks; aynı yöne gitmeleri nedensel zincire **uyum/karşıtlık** sağlar. Petrol veya GVZ'nin beraber hareketi altını mutlaka *başlattığını* ispatlamaz.
5. **Bankada karar kapısı:** Türkiye işlem saatleri 09:00–17:00, gerçek ASK/BID ve banka %0,8 alış + %0,8 satış; akademik olay açıklamasından otomatik alım/satım stratejisi oluşmaz.

**Ontoloji ilkesi:** Bir ekonomik gelişmenin birden fazla aktarım yolu vardır. En olası **ANA TETİKLEYİCİ ADAYI** sınıfı analitik dizin için *tek* gösterilir; ikincil mekanizmalar ve karşıt kanıtlar ayrıca tutulur. Ana etiketin sayılması o olayın sebebinin kanıtlandığı anlamına gelmez. V1 ZigZag ve V2 sabit-ufuk olayları örtüşebilir ve aynı vaka iki kayda girebilir. V1 uzun bacak `gold_original_move_pct` yönlü net değişim, V2 yüzdesi maksimum mutlak 1h/4h/12h/1d/3d/5d işaret penceresi büyüklüğü; **birbirinin getirisi değildir**.

## 2. 95 fiyat-kayıt satırının **ADAY** birincil mekanizmaya göre dağılımı
| Aday tetikleyici / mekanizma ailesi | Kayıt | Ne aranır, veriyle nasıl kontrol edilir? | Vaka örnekleri |
|---|---:|---|---|
| **ABD makro / faiz / dolar / Fed / CPI / NFP** | **24** | Resmî release UTC; `actual−pre-release consensus`; ilk 15/60m XAU; senkron DXY/ABD 2Y–10Y, ZN fiyatı yalnız getiri ikamesi olarak **kullanılmaz**; başka haber kontrolü | C002 3 Şubat 2023 NFP; C017 7 Haziran 2024 NFP+PBoC; C029 18 Aralık 2024 FOMC |
| **Finansal sistem krizi ve likidite zorunlu tasfiye** | **4** | Banka/finansman riski, hisse+metal+petrol eşzamanlı satışı, GVZ/VIX, zorunlu teminat, fonlama; aynı kriz içinde sonraki toparlanmayı ayrı fiyatla | SWING 003/C003 Mart 2023 SVB; SWING 028/C033 Nisan 2025 likidite |
| **Jeopolitik risk ve güvenli liman priminin büyümesi/çözülmesi** | **9** | İlk savaş/ateşkes haberinin UTC'si, petrol ve risk/altın ayrışması, haber sonrası ilk fiyat reaksiyonu | SWING 007/C006 Ekim 2023 Gazze; SWING 033/034 ve C041 Haziran 2025 İsrail–İran |
| **Tarife, ticaret ve ekonomi politikası** | **10** | Tarife oranı/son tarih/90 günlük rahatlama, USD ve ETF talebi, önce nakde geçme sonra güvenli liman dönüşü | SWING 032/C038 Mayıs 2025 ABD–Çin anlaşması; C034 2025 Nisan sonrası |
| **Altına özgü ETF–merkez bankası–CFTC/COMEX–fiziki akış** | **9** | WGC ETF net ton, PBoC raporu, `COT published_at`, COMEX open interest/opsiyon, OTC/fiziki EFP baz farkı | SWING 013 Mart 2024 OTC/opsiyon; SWING 015; C045/C047 ETF/pozisyon |
| **Aşırı momentum, pozisyon sıkışması ve kâr alma** | **13** | RSI, 200gün ortalamadan sapma, GVZ, futures marjin, COT/ETF ve karşı trend, likidite | SWING 038/C048 Ekim 2025; C053 29 Aralık 2025 marjin |
| **ABD seçimi ve mali politika beklentilerinin yeniden fiyatlanması** | **3** | Seçim/atama haberleri, ABD dolar-faiz-hisse ve altın ayrışması | SWING 020, C025/C027 Kasım 2024 |
| **Başlatıcı net değil, karışık veya özgül kaynak bulunamadı** | **23** | Kaynak tarihi/haber ilk baskı ve DXY-faiz/akım imzaları olmadan kesin kategori atama; sırf geçmiş metal korelasyonu yerine `UNRESOLVED` koru | C004, C007, C014, C031, C050–C052 ve diğerleri |
| **Toplam fiyat kaydı; bağımsız ekonomik şok sayısı değil** | **95** | **72 aday aile etiketi + 23 henüz çözümlenmemiş kayıt**, `0` adet ispatlanmış benzersiz nedensel yüzde katkısı | 42 V1 +53 V2 |

Bu tablo **analitik sınıflandırmadır**, ekonometrik olarak öğrenilmiş cluster değildir. Aday ana sınıflar yorumla seçilmiş ve bazıları önceki retrospektif WGC/Reuters raporuna dayalıdır. Alt etken kategorilerinin örtüşmesi beklenir; ekonomik gerçeğin tek etikete zorlanmasına izin verilmez. Başarı/metrik olarak `72/95` ya da `24/95` açıklama doğruluğu kullanılamaz. **Birincil aday sınıflaması gelecekte yanlışlanabilir / güncellenebilir.**

## 3. Hangi veriyi gerçekten bütün kayıtlara ekledik?
| Veri | Olayların gerçek eşleştirmesi | Kaynak ve bilimsel kısıt |
|---|---:|---|
| XAU ana fiyat olayı | **95/95** | EV/Dukascopy M15 NY17 V1/V2; retrospektif etiket |
| Gümüş/platin/paladyum/S&P500/Nasdaq beşli **iki farklı gün arasında tam** | **83/95** | StakTrakr günlük ve FRED endeks. Ayrıca **4/95** beşli uç satırı **aynı gün için 0** olup piyasa etkisi konusunda **ANLAMSIZ**; **6/95** kısmi, **2/95** tam eksik |
| WTI petrol **CL.c.0** vadeli | **95/95** | Databento CME GLBX 1h calendar continuous C. Her takvim tarihinde UTC **20:00'dan önceki en son kayıt**, iki tarih yüzde farkı. Kontrat devri/roll, illiquid last bar ve kaynağın 2026 arşiv tazeliği var; olay saatli akım/nedensellik **değil** |
| Nasdaq vadeli **NQ.c.0** | **95/95** | Aynı takvim-sampling, spot Nasdaq100 indeksi ile eşdeğerliği iddia edilmez |
| ABD 10Y tahvil vadeli **ZN.c.0** | **95/95** | **Tahvil FİYATI** yüzdesi; 10Y faiz/baz puan değişimi **değildir**, roll ve likidite kaynak hatasına açık |
| Cboe altın beklenen oynaklık endeksi **GVZ** | **93/95** | [GOLD_GVZCLS_RAW_2021_2025.csv](GOLD_GVZCLS_RAW_2021_2025.csv) resmî günlük endeks; `GVZ_end−GVZ_start` **endeks puanı**, yüzde getiri değil. Aynı tarihli kapanış olaydan sonra gelebilir; D-1 kullanılmadan **erken risk sinyali değil** |
| VIX | **95 olayın tamamı için aynı saatli bağımsız eşleştirme yapılmadı** | Eski [VIX/GVZ geliştirme özetinde](GOLD_EXECUTION_ORIGIN_SAFE_VIX_GVZ_ML_CHALLENGE_20261008_SUMMARY.json) **2022–25 ayrı DAY/OVN testleri** var; bunlar bu 95 olayın nedensel ilk haber/ilk fiyat anını doğrulayan tablo değildir |
| Brent, FX/DXY, 2Y/10Y nominal/reel faiz, ETF/COT/opsiyon/EFP | **95/95 için saatli tam doğrulanmış mekanizma matrisi yok** | Bazı ayrı aylık/makro ve vaka analizlerinde aralık değerleri/tarihli kaynak var; ilk source-vintage + eşsaat fiyata otomatik taşıma yanlış |
| Kullanıcının ifade ettiği **`BYDZ`** | **UNRESOLVED_SYMBOL** | Bu tam kodun hangi finansal endekse ait olduğu kurumsal veri anahtarında doğrulanmadı. `BDI` / `VIX` veya diğer bir ürün sayılıp veri UYDURULMADI. Önce orijinal sağlayıcı ticker + açıklaması gerekir |

**Zaman serilerinin rolü:** Kullanıcının eski GVZ/VIX/altın aşırı hareket riski çalışması gerçek ölçülebilir. [GVZ Signed Tail araştırması](GOLD_EXECUTION_GVZ_SIGNED_TAIL_RESEARCH_RESULT_2026-10-08.md) 2025 retrospektif ağır DOWN-event için score+GVZ AUC≈0,813 bulmuş, fakat 2023 AUC≈0,498 ve artımlı skor farklarının bootstrap aralıkları sıfırı dışlamamıştır. Bu, **GVZ'nin bazen tail-risk sıralaması için yararlı olabileceğini**, fakat bu 95 fiyat vakasında düşüşün ekonomik **nedeninin** GVZ olduğunu veya canlı AL/SAT sinyali verdiğini göstermez. VIX/GVZ ML geliştirme testlerinin çoğu 2023/24 gelişim geçidini geçmedi; katkısız özellikler otomatik eklenmez.

## 4. Neden grubunu veriyle sınayan karşıt örnekler
| Vaka / altın | Gözlenen çapraz veri, aynı *geniş tarih aralığı* | Doğru neden-grubu yorumu |
|---|---|---|
| **2–8 Nisan 2025 SWING 028 XAU −%4,788** | XAG −%10,50; S&P −%12,14; Nasdaq100 −%12,72; CL WTI vadeli **−%17,67**; GVZ **+5,81 endeks puanı** | Yaygın hisse/petrol/metal tasfiyesi, tarife şoku sonrasında zorunlu likidite azaltımı ile uyumlu. `FINANCIAL_STRESS_AND_LIQUIDITY`, tarife *tetikleyici*, marjin *güçlendirici*, GVZ *risk göstergesi*. |
| **20 Ekim–4 Kasım 2025 SWING 038 XAU −%9,782** | XAG −%7,80, S&P **+%0,54**, Nasdaq100 **+%1,17**, CL WTI **+%5,19**, GVZ **−10,00 puan** | Nisan'ın aynı geniş risk-off tipi DEĞİL: altına/pozisyona özgü aşırı momentum/kâr realizasyonu/uzun sıkışıklığı araştırması; GVZ düşmesi 'önceden satış olmazdı' demek değildir. |
| **5–27 Ekim 2023 SWING 007 XAU +%10,202** | Gümüş +%7,69; platin +%4,72; paladyum −%2,83; ABD hisseleri gerilemiş | Savaş/jeopolitik güvenli liman ile uyumlu; `bütün kıymetli metaller aynı nedenle yükselir` hipotezi karşılanmadı. |
| **6 Mayıs–14 Mayıs 2025 SWING 032 XAU −%7,208** | S&P +%5,09, Nasdaq100 +%7,72, gümüş yaklaşık −%0,42 | ABD–Çin 12 Mayıs 90 günlük tarife kolaylığı ile güvenli liman risk priminin çözülmesi adayı; hisse tasfiyesi değil; 12 Mayıs haberini 6 Mayıs öncesine çekme. |
| **18 Aralık 2024 C029 DOWN** | Fed 19:00 UTC yayımlanması sonrası XAU M15 ilk 15dk **−%0,760**, ilk 60dk **−%1,223** | `US_MACRO_FED` ailesi için güçlü saatli fiyat/duyuru eşleşmesi var; 2025 FOMC eski makro defterinde yok, diğer yasal ve pazar haberlerini ayrıştırmak yine gerekir. |
| **7 Haziran 2024 C017 DOWN** | PBoC alım-duraklatma açıklaması BLS NFP'den önce, NFP **272k**; resmi piyasada 12:30 UTC sonrası XAU ilk 15dk **−%0,612** | Aynı güne iki farklı *haber-katalizör*; WGC tarih/Reuters kaynakları farklı; ertesi trend UP olabilir. İkisini tek etken olarak etiketlememek gerek. |

**Şok ile trend ayrımı zorunlu:** 2024 Ağustos 5 gün içi altın ~%4 yüksek-düşük fiyat aralığının önceki NY17 kapanış farkı yalnız yaklaşık −%1,3'tür. Bu olay **kapanış eşiğiyle dışlanabilir**; ilk fiyat şoku ve sonra seans düzeyi hareketini ayrı kaydet. V1+V2 toplamı tarihsel dev hareket evreninin eksiksiz kapsandığını garanti etmez. H3 2025 reversallar, 2026 22 sinyal epizodu ve 10 aylık forecast hatası ayrı üst-alt kayıt gruplarıdır.

## 5. Gerçekte ne kadarını açıkladık?
- **95/95** fiyat kaydı arşivlenmiş ve *ilk aday etken sınıfı* verilmiştir. **72/95** mekanizma ailesi ile ilişkilendirilmiş (yorumlu aday), **23/95** tetikleyicisi çözümsüz/karışık. Bunlar **72 ispatlı neden / 23 nedensiz olay değildir**.
- Bu 95 kaydın daha önce sorgu nedeniyle boş kalan 38'inin **38/38** derin olay raporu oluşturulmuş, **35/38** sonradan beşli tarih eşleştirmesi tamamlanmış (C035 same-day 0 bilgi taşımaz).
- **85** bağımsız resmî zamanlı CPI/NFP/FOMC (NFP35, CPI34, FOMC16 2023–24) tarihi M15 ve 4 aynı gün/saat placebo ile ölçüldü. İlk 15dk NFP olaylarında **29/34**, CPI **27/34** normal aynı saat medyan hareketinden büyük. Ancak sonuç **yönün önceden tahmini değil**, makro şok sonrası fiyat şiddetinin sınırlı kanıtıdır.
- **38** derin incelenmiş fiyat kaydından yalnız **6** ilk-fiyat-bayrağı takvim gününde CPI/NFP/FOMC açıklaması vardı. **4** olayda ilk 15dk aynı yönde ≥%0,2 değişim, **1** küçük işaret, **1** ters işaret. İlk *fiyat bayrağının dakika sınırı* ayrıca doğrulanmadığı için bu 4 bile tekil nedeni kesin ispatlamaz.
- Özgün 53 kısa-ufuk V2 kümenin **25**'inde önceki vaka araştırmasında özel tarihli haber kaynağı yoktu; WGC/Reuters sonraki araştırmalarda yeni olgu bulunduğunda bile orijinal ilk yayın saati/haber arşivi ispatı değil.
- **0/95** için tek nedenin bağımsız karşıt-faktörler denetlenerek katkısının tamamen ayrıştırıldığı ve canlı uygulanabilir işlem bilgisi olarak doğrulandığı iddiası yapılamaz. Bu **bilimsel standart eksikliği**dir, bütün eşzamanlı gözlenen etkilerin rastlantı olduğunu söylemez.

## 6. Gelecek mekanizma araştırmasının kurumsal şeması ve kapıları
**Zorunlu kayıt:** `event_id`, `definition(M15/NY17/1h...)`, `candidate_first_trigger`, `firstprint_utc`, `precondition_known_at`, `posttrigger_0_15_60_240m`, `matched_USD_US2Y_US10Y`, `silver_platinum_palladium_same_UTC`, `WTI/Brent_asof`, `equities_asof`, `GVZ_D-1_and_VIX_D-1`, `ETF_CFTC_first_published_asof`, `primary_alternative`, `matched_non_event_controls`, `classification_verdict`. Çoklu nedenlerde `primary` ve `secondary` ayrı; birbirini çürüten göstergeler silinmez.

**Nedensellik delil seviyeleri:**
- L0 = fiyat olayı var, özgül neden bilinmiyor.
- L1 = tarihli açıklama + piyasa verileriyle **uyumlu** hipotez var.
- L2 = açıklamanın saatli ilk yayımlanma zamanı ve aynı saatli tepki açık, temel karşı hipotezler ayrıca denenmiş.
- L3 = çağdaş kontrollü negatif örnekler/karşı olgusal fark, veri-vintage, bağımsız doğrulama; ekonomik kaynak etki ayrıştırması savunulabilir.
- L4 = bağımsız ileri-rapor tahmin uyarısı, Türkiye bankası emir saatleri ve maliyetleriyle gerçek test. **L2–L4 elde edilmiş sayılmaz.**

**Not:** Cboe GVZ altın ETF opsiyonlarının 30 gün ima ettiği oynaklıktır; yön vermez. VIX hisse piyasası beklenen oynaklık rejimidir; altının yönünün tek başına nedeni sayılamaz. CL/NQ/ZN vadeli fiyatları, fiziki petrol/spot hisse/ABD faiz serisiyle *birim ve saat açısından* değiştirilmez.

## 7. Belgelerin sıradaki yeri
Ana manifest sıralaması **0.1 GENEL → 0.1A TETİKLEYİCİ×REJİM GRUPLARI → 0.1B 38 OLAY → 0.1C SAATLİ MAKRO TEST → 0.2 KURUMSAL 291 KAYIT ÇAPRAZ SİCİLİ → diğer arşiv sonuçları → en son #12 OCAK 2026 ÖZEL VAKA**. Eski 29.218 karakterlik Ocak bölümünün bütün aşamaları değiştirilmeden korunacaktır. Yeni yıllar/gelişmeler 0.1A/B/C veya tematik yeni bölümde, *Ocak ekinin sonuna değil* saklanacaktır.
