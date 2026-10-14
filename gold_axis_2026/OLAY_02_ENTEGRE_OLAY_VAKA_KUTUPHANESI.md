# OLAY-02 — Altın Olay, Haber, Veri ve Karar Kütüphanesi

## Önce bunu oku — tek olay kütüphanesi, tek araştırma sırası

**OLAY-02 tek ve BİRİNCİL ekonomik araştırma manifestidir.** Eski VAKA-03 adlı müstakil manifest **yoktur**; eskiden oluşturulan rapor/CSV/JSON yalnız OLAY-02 içindeki `EVENT_ID` veya `EPISODE_ID` kaynak ekidir. Ayrı ikinci ana olay anlatısı oluşturulmaz.

**Hızlı erişim:** [Kapsam / 96 kaydın durumu](#1-kütüphane-kapsamı-ve-çalışma-sırası) → [Veri otoriteleri](#2-hangi-kaynak-hangi-konuda-yetkilidir) → [Haber/altın/çapraz piyasa/karar kayıt şablonu](#3-tek-olayda-haber-ve-verilerin-doğal-sıralaması) → [Mekanizma/karşıt neden aileleri](#4-araştıracağımız-altın-yön-mekanizmaları) → [9 öğretici tam olay](#5-dokuz-öğretici-olay--haber-veri-karşıt-kanıt-ve-aksiyon) → [96 kronolojik fiş](#6-bütün-96-düzeltilmiş-fiyat-kaydı--kronolojik-indeks) → [Yanlışlama](#7-haber-zamanı-negatif-kontrol-ve-yapısal-karşı-vakalar) → [2026 bağımsız araştırma](#8-ayrı-2026-astra-araştırmasından-aktarılacak-dersler) → [Maliyetli karar kuralı](#9-15-dakikalık-karar-denemesine-veri-aktarımı) → [Eksikler](#10-bilimsel-kalite-kontrol-ve-güncelleme-disiplini).

**Kimlikler birbirine karıştırılmaz:** `SWING_V1_...` ve `C_CORR_...` = **fiyat kaydı kimliği** (96 kayıt, örtüşme olabilir). `MACRO_2023_...` = **haber/olay kimliği** (bir fiyat dalgasında birden fazla olabilir). `EPISODE_ID` = dalganın üst kimliği. **Kaynak kanıtı:** doğrudan orijinal yayımlayıcı haber linki + `available_at_utc` + tamamlanmış piyasa barı + rakip haber + açıklama/saat mantığı; kaynak yoksa `MISSING` yaz. [96 tekil kanıt fişi](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md) fiyat olayından habere ulaşır; nedensel ilk haber kanıtının bulunmadığı satırı tamamlandı diye göstermez.

**Yeni olay ekleme standardı:** tek olay kimliğiyle bu indeksin ilgili yıl/epizot satırını güncelle → ilk kaynak haber akışı ve yayın saatini bağla → XAU M15/M1 ve USD/faiz/metallerin gerçekten bilinebilen verilerini ekle → ekonomik aktarım ve karşıt vakayı yaz → kararı/maliyeti/kalan fırsatı ayrı ölç → yalnız doğrulanabilen genel dersi [ÖĞREN-03](adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md) içine hipotez ID ile aktar → [DURUM-04](adaptive_volatility_learning/months/2023-01/STATE.json) ayını ilerlet. Yeni bir manifest açma; orijinal 5.190 satırlık arşivi değiştirme.

**Ana araştırma kaynağı · Sürüm 2 · 14 Ekim 2026 · XAU/USD · RESEARCH ONLY**

**OLAY-02 bizim ekonomik olayları anlamak için ilk okuyacağımız kaynaktır.** Her olayda haber akışı, verinin o anda bilinebilirliği, altın ve çapraz varlık tepkisi, mümkün mekanizmalar, karşıt kanıtlar, karar ve maliyetli sonuç **aynı olay kimliği altında bir arada** değerlendirilir. Geçmişte bilinmeyen haberler ve sonradan oluşmuş fiyat tepeleri as-of işlem kararı diye gösterilmez.

[ANA-01 — Projenin hedef ve protokolü](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) · [ÖĞREN-03 — Ortak mekanizma/karar hipotezleri](adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md) · [Belge haritası](BELGE_HARITASI_V1.md) · [Eski 5.190 satırlık tarihsel kayıt (korunmuştur)](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST_FULL_HISTORY_SNAPSHOT_20261014.md)

## 0. Her olay için ALTI ZORUNLU KARAR ALANI — 96/96 UYGULANDI (14 Ekim 2026)

**Yeni merkezî erişim:** [96 olayın altı alanı doldurulmuş karar değerlendirme fişleri](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md) · [96 olayın 4s/12s/1/3/5 uygun seans sayısal ve maliyetli sonuç JSON'u](OLAY_02_96_KARAR_ONCESI_VE_SONRASI_GERCEK_OLCUM_20261014.json). Her fiş, [tarihsel kaynak/haber fişi](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md) ile aynı `SWING_V1_...` veya `C_CORR_...` kimliğini kullanır. Bunlar **OLAY-02 alt kanıtlarıdır, yeni manifest değildir**.

**Her olayın altı alanı:** (1) **Karar öncesi** 1/4/12 saat ve 1/3/5 uygun seans XAU M15 geçmişi; USD/faiz/diğer metaller gibi bulunmayan varlıklar **EKSİK**. (2) İlk haber/haber zamanı ve aynı-UTC ilk fiyat teyidi, doğrulanmamışsa **BELİRSİZ**. (3) O anda olasılıklar/beklenen kalan hareket ve AL/SAT/TUT karar durumu — **kalibre edilmiş model yoksa karar ÜRETİLMEZ**. (4) **Sonradan** gerçekleşen 4/12 saat ve 1/3/5 seans getirileri. (5) **Aynı $100 başlangıçta**, bir al ve bir sat için %0,8'er komisyon + vendor BID/ASK ile NAKİT/ALTIN karşıt senaryoları. (6) **Karardan önce tamamlanmış geçmiş olaylara** dayalı yakın ve farklı sonuçlu desenler; ayrıca geriye dönük gelecek-yıllı analojiler karar için yasak.

**Kontrol saati ayrımı:** Bu ilk tarama fiyat olayının geriye dönük etiket başlangıç tarihindeki ilk uygun **09:15 TRT** kapalı M15 kontrolüdür. Olayın haberinin ilk saniyesi veya bilimsel olarak kanıtlanmış ilk fiyat reaksiyonu **değildir**; aynı tarihte daha sonraki NFP/CPI/FOMC actual bu kontrol noktasına giremez. Sonuç tarafında vendorun takip eden 15 dakika barının **OPEN BID/ASK fiyatı** yalnız **geriye dönük icra vekili**, gerçek banka kotasyonu değildir.

**Ölçülen ilk sonuç:** 96/96 olayda 09:15 öncesi 1 saat XAU verisi; 96/96 +4h, +12h, sonraki 1 seans; **95/96** sonraki 3 seans ve **94/96** sonraki 5 seans için al/sat maliyeti karşılaştırma olanağı. 3 seanslık 95 koşullu başlangıçta 100 dolar CASH için ex-post **17 AL+SAT / 78 CASH TUT**, başlangıçta 100 dolar GOLD için **42 GOLD TUT / 53 SAT ve NAKİT KAL** daha yüksek sonuç verdi. Bu **seçilmiş 96 fiyat olayına** aittir; şoksuz kontrol günleri, olaydan önce nedensel haber ilk yayımları, same-UTC faiz/DXY paneli ve `P(kalan hareket)` yok. **Geçmiş en iyi aksiyon = o gün öngörülebilen karar değildir.**


**Filtrelenebilir karar kataloğu:** [96 kayıtlık ön-rejim, 5 ufuk ve alternatif kararlar CSV](OLAY_02_96_VAKA_FILITRELENEBILIR_KARAR_KATALOGU_20261014.csv). **Aynı UTC'ye göre saatlik diğer piyasa kontrolü:** [ZN/NQ/CL/SI/GC H1 fiyat verileri CSV](OLAY_02_96_KARAR_ONCESI_CME_H1_ZN_NQ_CL_SI_20261014.csv); veri kapsamı sırasıyla **80/95/93/4/16 olay**. Bunlar **CME vadeli fiyat değişimleri** olup gerçek DXY, ABD 2Y/10Y tahvil getirisi veya spot XAG serisi değildir. Eksik seri MISSING kalır. Fiyat rejimi filtresi as-of fiyat yönüdür, Fed rejiminin ölçülmüş sınıfı değildir.

### Mevcut olaydan altı-alan fişine doğrudan git
[2023 Ocak uzun UP](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_001) · [2023 Şubat uzun DOWN](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_002) · [Mart 2023 SVB UP](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_003) · [96/96 diğer olay](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md)


## 1. Kütüphane kapsamı ve çalışma sırası

| Araştırma birimi | Mevcut, doğrulanmış envanter | Bilimsel anlamı |
|---|---:|---|
| 2023–2025 düzeltilmiş V1 NY17 yönlü uzun fiyat bacakları | **42** | Yön işaretli uzun fiyat hareketleri, uygulanan işlem sonucu değil |
| 2023–2025 düzeltilmiş V2 çok-ufuklu hareket kümeleri | **54** | Maksimum **mutlak** 1/4/12saat / 1/3/5 seans hareketleri; toplam fiyat bacağı net getirisi değil |
| **OLAY-02 kronolojik fiyat kimlikleri** | **96** (2023:22 / 2024:33 / 2025:41) | Örtüşen bacaklar var; 96 bağımsız ekonomik şok değil |
| Tarihli haber ve ekonomik kanıta bağlanan fiyat fişleri | **96/96** | Birincil haber–fiyat nedenselliği değil, eksikleri de belirtilen araştırma bağlantısı |
| İlk fiyat bacağını kesin başlattığı gösterilen haber / ölçülen nedensel katkı | **0/96** | Eski haber arşivindeki bu alanlar hâlen NO |
| 38 ayrıntılı önceki kaynak araştırması | **18 V1 + 20 eski V2** | Yalnız 18 V1 düzeltilmiş kimlikle birebir; V2 eski yeni ID sıra eşlemesi yok |
| 85 tarihli ABD NFP/CPI/FOMC duyurusu, M15 fiyat penceresi | **85×5=425** satır | İlk M15 haber tepkisi ve placebo; bacağın tamamının nedeni değil |
| Gerçek zaman/süreç maliyeti hesaplanmış üst olay örnekleri | **3** | 5 Ocak ADP, 6 Ocak NFP, 3 Şubat NFP; ex-post, OOS değil |
| Astra 2026 Ocak–Eylül | **273 takvim günü** ayrı araştırma | 2023–25 fiyat kataloğuyla aynı saat/fiyat evreni değildir |

**Nasıl kullanılır?** İlk önce aşağıdaki 96 kaydın tarih ve büyüklüğüne bak → kimliğine basıp haber–veri fişini aç → varsa 38 derin vaka kaynağını kontrol et → açıklama saatli makro tepki ve karşıt piyasa mekanizmalarını ayır → ÖĞREN-03'teki hipotezi sınama adayı olarak kullan → gerçek banka maliyeti sonrası işlem avantajı ölçülmediyse AL/SAT başarısı iddia etme.

## 2. Hangi kaynak hangi konuda yetkilidir?

| Belge ve bağlantı | Gerçek otoritesi / uyarısı |
|---|---|
| **[96 olayın tek tek tüm haber/veri fişleri](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md)** | Her corrected ID altında zaman penceresi, tarihli kaynak, varsa makro M15, ekonomi sınıfı, diğer piyasa kanıtı, karşıt açıklama, eksik ilk yayın ve işlem durumu |
| **[96 olayın makine-okunur bilimsel tablo/denetimi](OLAY_02_96_KAYIT_DENETIMLI_KATALOG_20261014.csv)** | 96 kayıt, kimlik, kaynak, 85 makro açıklama ile örtüşme, ilk haber ve nedensellik eksikleri |
| [96 NY17 düzeltilmiş fiyat/kanıt CSV](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv) | **Fiyat yüzdesi, etiket, başlangıç-bitiş ve bilimsel status için güncel kaynak** |
| [38 olay derin haber–mekanizma raporu](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md) · [38 tarihli haber/metal/hisse matrisi](GOLD_HISTORICAL_38_EVENT_CAUSAL_SOURCES_QUANT_V2_20261014.csv) | Reuters/WGC/metal/hisse bağlamı; farklı günlük kapanışların anlık fiyat tepkisi olmadığı unutulmaz |
| [95 eski neden aileleri](GOLD_HISTORICAL_95_TRIGGER_CAUSE_REGIME_TAXONOMY_AUTHORITY_20261014.md) · [eski fiyat/diğer piyasa atlası](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv) | **42+53 eski fiyat sözleşmesi; yeni 42+54'le otomatik birleştirme yasak** |
| [85 makro release M15 olayı](GOLD_HISTORICAL_SHOCK_CAUSAL_FALSIFICATION_MACRO_EVENTSTUDY_AUTHORITY_20261014.md) · [425 ölçüm CSV](GOLD_2023_2025_CPI_NFP_FOMC_M15_RELEASE_WEEKMATCH_EVENTSTUDY_20261014.csv) | NFP ilk 15dk medyan mutlak %0,3344 vs eşsaat normal %0,0802; CPI %0,2927 vs %0,0972. Bu **oynaklık** kanıtı, yön stratejisi değil |
| [2026 Astra günlük kaynak denetimi](GOLD_ASTRA_2026_JAN_SEP_DAILY_REPLAY_EVENT_MECHANISM_TRANSFER_AUDIT_20261014.md) | 273 günlük haber–karar metodolojisi ve başarısız maliyetli sonuç; ayrı dönem/clock |
| [OLAY-02 kaynak kalite denetimi](OLAY_02_ICERIK_KALITE_DENETIMI_20261014.md) | Hangi ilk yayımlar doğrulanmış ve hangi as-of / neden belgeleri eksik |

**Saat zorunluluğu:** UTC+3 Türkiye; NY17 New York yaz/kış ve 17:00 sınırına duyarlı. M15 fiyatı bar başladıktan **15 dakika**, M1 **1 dakika** sonra gözlenebilir; H1 futures için tamamlanmamış barı kullanma. ZN 10 yıllık ABD tahvil **vadeli fiyatıdır**, getiri (%) değildir. GVZ endeksi **puan**, yüzde değil; gün sonu değerinin erken sinyalde D-1 lag gereği var. DXY, gerçek 2Y/10Y, gümüş/platin/paladyum ve ETF/CFTC'nin eşsaatli as-of paneli eksik olabilir. BIST ons altın yönü için birincil veri değil.

## 3. Tek olayda haber ve verilerin doğal sıralaması

Her çok-günlü **EPISODE_ID** altında bir veya daha fazla farklı **EVENT_ID** (NFP, CPI, PBoC, ISM, enerji, tarife vb.) vardır. Bir olayın incelenme sırası:

1. **Olay başlangıcı:** fiyat olayının tespit yöntemi; gerçek haberin ilk saatiyle karıştırılmayan dönem; önceki makro rejim ve eldeki GOLD/CASH.
2. **Haber akışı:** resmî kurum/özgün URL, tarih, **firstprint UTC**, açıklama öncesi tahmin **vintage**, açıklanan actual ve sürpriz; yalnız henüz yayımlanmış bilgi.
3. **Altın fiyat akışı:** tam kapanmış BID/ASK M15 ile 1/4/12 saat ve 1/3/5 seans gözlemleri; AL/SAT adayı olursa olay-tetikli kapalı M1 teyit; sonraki uygulanabilir fiyat.
4. **Aktarım ve diğer piyasalar:** DXY, ABD 2Y/10Y nominal/reel faiz, gümüş/platin/paladyum, ZN/NQ/CL ve WTI/Brent, GVZ/VIX, CFTC/ETF/merkez bankası. Her veri için **available_at** ve MISSING/ALIGNED/LAGGED/POST_EVENT.
5. **Neden ve rakip açıklamalar:** haber → beklenti güncellemesi → USD/faiz/petrol/likidite/altın talebi → altın tepkisi. Diğer haberler ve mekanizmanın **neden yanlış olabileceği**.
6. **Hareket aşaması:** PRE-ONSET, ONSET, CONTINUATION, EXHAUSTION, REVERSAL veya UNCERTAIN. İlk gerçekleşmiş hareketin tamamını gelecekte kalan fırsat sayma.
7. **Karar ve test:** AL / SAT / altındayken TUT / nakitteyken TUT / ABSTAIN; **%0,8 AL + %0,8 SAT ve banka makası**, banka ASK/BID veya açıkça proxy, gecikme, $100 senaryo ve buy-hold/cash kıyası. Dondurulmuş farklı olaylarda başarı gösterilmeden üretim kuralı değil.

**K0** fiyat etiketi → **K1** tarihlenmiş kaynak → **K2** açıklama saati + fiyat reaksiyonu → **K3** rakip/negatif kontrol + eşzamanlı piyasa → **K4** işlem zamanı ve maliyetiyle dondurulmuş bağımsız doğrulama. *K2 bir haberin tek başına büyük trendi başlattığına dair nedensel ispat değildir.*

## 4. Araştıracağımız altın yön mekanizmaları

| Olay sınıfı | Makro/haber → aktarım adayı | Rakip mekanizma / yanlışlama | Aksiyon için araştırma adayı |
|---|---|---|---|
| **ABD CPI/NFP/Fed – güvercin** | Beklenenden düşük ücret/enflasyon → daha düşük faiz/USD beklentisi → XAU UP | Güçlü istihdam, diğer şahin veriler ve açıklama sonrası yeni haberler | NAKİT→AL ancak aynı UTC ve kalan net hareket teyidiyle |
| **ABD CPI/NFP/Fed – şahin** | Beklenenden yüksek istihdam/enflasyon → sıkılaşma/USD/faiz↑ → XAU DOWN | Banka stresi güvenli limanı baskın olabilir; 10 Mart 2023 karşıt NFP | ALTIN→SAT ancak devam düşüşü ve satış+yeniden alış faydası yeterliyse |
| **Zorunlu likidite** | Tarife/sistem paniği → teminat satışı → altın+hisse+petrol+metaller DOWN | Hisseler/petrol UP ise genel tasfiye değil, metal özel olabilir | Satış veya nakitte kalma; bankanın maliyetini aşan koruma gerekli |
| **Güvenli liman** | Bankacılık/jeopolitik tehdit → altın göreli talebi ve USD/faiz aktarımı | Petrol/enflasyon/faiz şoku altını bastırabilir | Risk başlığıyla otomatik AL değil; mekanizma ayrımı |
| **Altına özgü arz/talep** | PBoC/ETF/CFTC/altın fiziki talep/COMEX → metal farklılaşması | ETF fon çıkışı varken altın artabilir; bilgi yayımlanma gecikmesi | Altın/metaller ayrışmasını sadece gerçek as-of bilgiyle değerlendir |
| **Pozisyon çözülmesi** | Aşırı momentum, marjin artışı → kısa/günlük DOWN dönüşü | Genel makro şok ile metal-özel düzeltme ayrı | Kâr alma veya SAT için **kalan downside** kanıtı |
| **Karışık/çözümsüz** | Farklı haberler birbiriyle yarışır, fiyat tersine dönebilir | Nedeni son fiyata bakarak seçmek doğrulama değildir | **TUT/BEKLE/ABSTAIN**, gereksiz %0,8+%0,8 turdan kaçın |

**ÖĞREN-03** içinde ilk üç makro karar hipotezi [ayrı sicilde](adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md). Bunlar hala **hindsight-exposed**, bütün olaylarda test edilmiş kural değil.

## 5. Dokuz öğretici olay — haber, veri, karşıt kanıt ve aksiyon

### 1. SWING_V1_001 — Ocak 2023 — Fed beklentisi ve metal ayrışması
**Fiyat:** [Düzeltilmiş olay fişi](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_001).

**Haber akışı:** 5 Ocak ADP +235 bin ve claims; 6 Ocak 13:30 UTC NFP +223 bin/ortalama saatlik ücret aylık +%0,3. 6 Ocak 15:00 UTC ISM hizmetler 49,6: **13:46 UTC AL kararından sonra açıklanmış olup önce kullanılamaz**. 12 Ocak CPI sonradan geldi.

**Altın ve diğer piyasa veri akışı:** Yeni NY17 V1 bacağı +%6,042. Derin vakada aynı geniş pencerede gümüş −%3,29, platin −%7,27, paladyum −%9,20, Nasdaq-100 +%13,81. WGC 9 Şubat *sonradan* yazılmış raporda 10Y yaklaşık −37bp, ETF −26 ton, COMEX net-long 250 ton: bunlar 6 Ocak'ta bilinebilir bilgi değildir.

**Neden–sonuç yorumu ve karşıt kanıt:** Fed gevşeme beklentisi/altın özel talebi aday; beyaz metallerin düşmesi ‘bütün metaller ortak yükseldi’ açıklamasını çürütür. Aynı dakika DXY/gerçek 2Y/10Y teyidi yok.

**Aksiyon / sınama:** 6 Ocak 13:46Z **AL adayı**, 13:47Z varsayımsal ASK $1849,30; 13 Ocak değerlendirme tarihinde zorunlu tasfiye varsayımı $102,19. Başlangıç $100, %0,8 her yön; gerçek banka emri ve OOS değil. [Asıl araştırma](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_MACRO_EVENT_COSTED_REPLAY_20261014.md).

### 2. SWING_V1_002 — Şubat 2023 — şahin istihdam ve büyük DOWN
**Fiyat:** [Düzeltilmiş olay fişi](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_002).

**Haber akışı:** 1 Şubat FOMC, 3 Şubat 13:30 UTC NFP ilk açıklamada +517 bin, işsizlik %3,4. 14 Şubat CPI, 16 Şubat PPI ve 24 Şubat PCE daha sonraki **ayrı** bilgi şokları; 3 Şubat SAT gerekçesi olamaz.

**Altın ve diğer piyasa veri akışı:** Düzeltilmiş V1 −%7,147. Eski derin olay penceresinde gümüş −%10,24, platin −%6,65, paladyum −%11,84, S&P −%3,62. Bu günlük pencere tepkileri ilk NFP dakikasındaki eşzamanlı teyit değildir.

**Neden–sonuç yorumu ve karşıt kanıt:** Güçlü ABD büyüme/şahin Fed, USD/getiri baskısı adayı. NFP bütün Şubat bacağının tek nedeni ispatlanmadı; satış sonrası yeniden AL mekanizması yok.

**Aksiyon / sınama:** 3 Şubat 13:45Z **SAT adayı**, sonraki 13:46Z BID vekili yaklaşık $1887,305. Ayrı, şartlı 1 Şubat GOLD $100 ile $96,38 nakit; 24 Şubat pasif likidasyon $92,53; Ocak portföyüne eklenemez. [Asıl araştırma](independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_NFP_DOWN_EVENT_CASE_20261014.md).

### 3. SWING_V1_003 — Mart 2023 — SVB/bankacılık güveni ve NFP karşıtlığı
**Fiyat:** [Düzeltilmiş olay fişi](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_003).

**Haber akışı:** 10–13 Mart ABD banka/SVB stres haberleri ve istihdam açıklamaları. **10 Mart güçlü NFP +106 bin sürprizine rağmen** altının ilk 15 dakika tepkisi +%0,540: tek-kural şahin NFP→DOWN yanlış olabilir.

**Altın ve diğer piyasa veri akışı:** 24 Şubat–4 Mayıs V1 +%13,200 uzun bacağı içinde Mart bankacılık stresinin yalnız bir dönemi yer alır. 10/13 Mart haberlerinin ilk UTC anı ve altın/2Y/DXY/GVZ ortak reaksiyonuyla kapsam bütünü ayrıca doğrulanmalı.

**Neden–sonuç yorumu ve karşıt kanıt:** Güvenli liman talebi, Fed patikası yeniden fiyatlaması ve likidite birbirinin rakibi; NFP güçlüydü diye mutlaka SAT deneme.

**Aksiyon / sınama:** Bilimsel karşı-vaka; tam maliyetli banka AL/SAT kuralı sınanmadı. [Asıl araştırma](GOLD_HISTORICAL_SHOCK_CAUSAL_FALSIFICATION_MACRO_EVENTSTUDY_AUTHORITY_20261014.md).

### 4. SWING_V1_006 — Eylül 2023 — USD, tahvil, ETF ve pozisyon baskısı
**Fiyat:** [Düzeltilmiş olay fişi](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_006).

**Haber akışı:** İlgili WGC Eylül değerlendirmesi 10 Ekim'de yayımlandı; Temmuz–Ekim fiyat bacağının başlangıç haberi diye gösterilemez.

**Altın ve diğer piyasa veri akışı:** Düzeltilmiş V1 −%8,021. Eylül raporunda 10Y faiz yaklaşık +50 baz puan, DXY +%2,5, ETF −59 ton, COMEX managed net-long −70 ton; **retrospektif aylık veri**, anlık şok teyidi değil.

**Neden–sonuç yorumu ve karşıt kanıt:** Faiz/USD güçlenmesi + ETF/pozisyon çözülmesi aday; gerçek ilk yayımlar ve aynı UTC farklı piyasa reaksiyonu yok.

**Aksiyon / sınama:** DOWN sürekliliğinin araştırma vakası; test edilmiş banka SAT kararı yok. [Asıl araştırma](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).

### 5. SWING_V1_013 — Mart–Nisan 2024 — altına özgü talep ve makro birlikteliği
**Fiyat:** [Düzeltilmiş olay fişi](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_013).

**Haber akışı:** Mart zayıf ISM, WGC 12 Mart ve ardından aylık değerlendirmeler; Çin, OTC, fiziki ve opsiyon talebi haberleri farklı günlerde.

**Altın ve diğer piyasa veri akışı:** Düzeltilmiş NY17 V1 +%19,984; yaklaşık iki aylık bacağı tek ISM veya tek merkez bankası açıklamasına bağlamak geçersiz.

**Neden–sonuç yorumu ve karşıt kanıt:** USD/faiz gevşemesi ile merkez bankası/OTC ve momentum mekanizmaları birlikte olabilir, gerçek katkıları ayrıştırılmadı.

**Aksiyon / sınama:** Büyük UP epizodu; güvenilir ilk M1 AL ve maliyetli çıkış sınanmadı. [Asıl araştırma](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).

### 6. SWING_V1_016 — 7 Haziran 2024 — PBoC ve NFP ayrı haberler
**Fiyat:** [Düzeltilmiş olay fişi](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_016).

**Haber akışı:** 7 Haziran PBoC altın alış duraksaması ABD 12:30 UTC NFP'den **önce** biliniyordu. NFP +272 bin; Reuters beklentisi 185 bin ile eski ledger 182 bin farklı. 20 Mayıs–6 Haziran düşüşünün tamamını 7 Haziran NFP açıklayamaz.

**Altın ve diğer piyasa veri akışı:** Düzeltilmiş V1 −%5,459, NFP ardından ilk M15 −%0,612; iki mekanizmanın etkisi aynı şey değildir.

**Neden–sonuç yorumu ve karşıt kanıt:** PBoC talep şoku ve USD/ABD faiz sürprizi birbirinden ayrılarak kronolojik yanlışlama gerekir.

**Aksiyon / sınama:** İki tetik adayı; uygun banka SAT/yeniden AL testi yapılmadı. [Asıl araştırma](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).

### 7. SWING_V1_028 — 2–7 Nisan 2025 — güvenli liman yerine likidite satışı
**Fiyat:** [Düzeltilmiş olay fişi](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_028).

**Haber akışı:** Tarife ve teminat/fonlama gerilimi; 4 Nisan NFP'den **önceki bir saatte** XAU −%0,975, açıklama sonrası M15 −%0,261. Tüm hareketi NFP'ye atfetme.

**Altın ve diğer piyasa veri akışı:** Düzeltilmiş V1 −%4,777; eski ilgili geniş tarih aralığı fiyatlarında gümüş −%10,50, S&P −%12,14, Nasdaq −%12,72, WTI CL −%17,67, GVZ **+5,81 puan**. Bunlar farklı saatli geniş pencere verileridir.

**Neden–sonuç yorumu ve karşıt kanıt:** Tarife riskini ‘her zaman altın UP’ ilan etmek yanlış; nakde dönme gereği altını da satabilir.

**Aksiyon / sınama:** Likidite tipi DOWN adayının gerçek banka masraflı/same-UTC teyidi henüz yok. [Asıl araştırma](GOLD_HISTORICAL_95_TRIGGER_CAUSE_REGIME_TAXONOMY_AUTHORITY_20261014.md).

### 8. SWING_V1_038 — Ekim 2025 — metal odaklı pozisyon çözülmesi
**Fiyat:** [Düzeltilmiş olay fişi](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_038).

**Haber akışı:** WGC 13 Ekim ihtiyat değerlendirmesi ve 22 Ekim piyasa yorumları; altının yön değişimini başlatan ilk işlem/haber saati doğrulanmadı.

**Altın ve diğer piyasa veri akışı:** Düzeltilmiş V1 −%9,785. Eski karşılaştırmada gümüş −%7,80 iken S&P +%0,54, Nasdaq +%1,17, WTI +%5,19, GVZ −10,00 puan. Genel riskli varlık tasfiyesi **değil**, altına/metal pozisyonuna özel olabilir.

**Neden–sonuç yorumu ve karşıt kanıt:** Benzer fiyat DOWN hareketi Nisan 2025 ile **farklı** ekonomik kanaldan gelebilir; eski tarih aralığını yeni NY17 saatine kopyalama.

**Aksiyon / sınama:** EXHAUSTION/REVERSAL adayı; canlı SAT modelini doğrulamaz. [Asıl araştırma](GOLD_HISTORICAL_95_TRIGGER_CAUSE_REGIME_TAXONOMY_AUTHORITY_20261014.md).

### 9. SWING_V1_042 — Aralık 2025 — CME marjin ve yıl sonu tasfiyesi
**Fiyat:** [Düzeltilmiş olay fişi](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_042).

**Haber akışı:** 29 Aralık tarihli AP ve 31 Aralık marjin haberleri; 8 Ocak 2026 WGC **sonradan** açıklama, 2025 Aralık işlemine giremez.

**Altın ve diğer piyasa veri akışı:** Düzeltilmiş V1 −%4,730; beyaz metallerin tarih arası getirileri ve altındaki fiyat çözülmesi ilk marjin açıklama saatiyle kesin bağlanamadı.

**Neden–sonuç yorumu ve karşıt kanıt:** Marjin/pozisyon/ince tatil likiditesi rakip mekanizmalar, aynı-UTC kanıtı ve orijinal firstprint tamamlanmadı.

**Aksiyon / sınama:** Geç satışın bir iyileştirme sağladığı ispatlanmadı. [Asıl araştırma](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### 5.10. Dakika bazlı ve maliyetli ilk üç karar adayı

| Olay | İlk yayımlanan bilgiler | Tamamlanmış fiyat ve karar anı | Mali sonuç ve temel eksik |
|---|---|---|---|
| **5 Ocak ADP/claims** | 13:15Z ADP **235k**, 13:30Z claims **204k** | 13:58Z M1 kısa DOWN doğrulaması, buna rağmen **GOLD TUT** adayı | 6 Ocak BID-mark $100,07; erken SAT→geri AL karşı-olgusu $97,67/$97,23, gelecekteki NFP 5 Ocak'ta bilinmez. [Olay denetimi](adaptive_volatility_learning/stress_cases/2023-01/JAN_2023_TOP_VOLATILITY_DIRECTIONAL_STRESS_AUDIT_20261014.md) |
| **6 Ocak NFP** | 13:30Z NFP **223k**, saatlik ücret +%0,3; 15:00Z ISM daha sonra | 13:46Z **AL adayı**, sonraki 13:47Z ASK proxy **$1849,30** | Başlangıç $100 → 13 Ocak'ta zorunlu satış *varsayılırsa* $102,19. Fiili SAT sinyali yok, banka gerçek fill yok. [864 M15 kontrol](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_MACRO_EVENT_COSTED_REPLAY_20261014.md) |
| **3 Şubat NFP** | 13:30Z **517k**, %3,4 işsizlik | 13:45Z **SAT adayı**, sonraki 13:46Z BID proxy **$1887,305** | Şartlı 1 Şubat $100 GOLD başlangıcında $96,38 nakit vs 24 Şubat pasif GOLD net $92,53. Re-entry yok. [2304 M15 kontrol](independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_NFP_DOWN_EVENT_CASE_20261014.md) |

## 6. Bütün 96 düzeltilmiş fiyat kaydı — kronolojik indeks

Bu tablo yalnız giriş kapısı. **Her kimliğe tıklandığında haberlerin yayın tarihleri, varsa makro release saatleri ve ilk M15 tepkileri, ekonomi mekanizması, 38 derin araştırmanın eşleşebilen çapraz piyasa verileri, karşıt kanıt, işlem dosyası ve eksikler** [ayrıntılı fişte](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md) bulunur.

**Önemli:** Düzeltilmiş `C_CORR_` kayıtları eski `MOVE_V2_C` kayıtlarının sadece sırasıyla eşleştirilemez. **V2 mutlak maksimum genliği** net getiriyi vermez; katalogdan geriye dönük al/sat kârı hesaplamak bilimsel olarak yanlış olur.

### 2023 — 22 kayıt (12 uzun V1 / 10 kısa-orta V2)

| Olay kimliği (ayrıntı açılır) | Fiyat penceresi | Altın hareketi / **metrik** | Ekonomi aday sınıfı | Kanıt durumu |
|---|---|---|---|---|
| [`SWING_V1_001`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_001) | 2023-01-03 → 2023-02-01 | **UP** +6.04% net bacak | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_001`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_001) | 2023-01-12 → 2023-01-12 | **UP** 3.50% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_002`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_002) | 2023-02-01 → 2023-02-24 | **DOWN** -7.15% net bacak | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_002`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_002) | 2023-02-03 → 2023-02-08 | **DOWN** 4.26% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_003`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_003) | 2023-02-24 → 2023-05-04 | **UP** +13.20% net bacak | MAKRO_FAİZ_BEKLENTİSİ | Derin kaynak; nedensellik açık |
| [`C_CORR_003`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_003) | 2023-03-13 → 2023-03-23 | **UP** 6.50% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Derin kaynak; nedensellik açık |
| [`C_CORR_004`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_004) | 2023-05-04 → 2023-05-04 | **UP** 3.43% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_004`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_004) | 2023-05-04 → 2023-06-28 | **DOWN** -6.96% net bacak | JEOPOLİTİK_GÜVENLİK | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_005`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_005) | 2023-06-28 → 2023-07-18 | **UP** +3.75% net bacak | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_006`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_006) | 2023-07-18 → 2023-10-05 | **DOWN** -8.02% net bacak | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_005`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_005) | 2023-09-29 → 2023-10-03 | **DOWN** 4.58% MAX |hareket| | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_007`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_007) | 2023-10-05 → 2023-10-27 | **UP** +10.23% net bacak | JEOPOLİTİK_GÜVENLİK | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_006`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_006) | 2023-10-13 → 2023-10-20 | **UP** 5.64% MAX |hareket| | JEOPOLİTİK_GÜVENLİK | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_008`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_008) | 2023-10-27 → 2023-11-10 | **DOWN** -3.39% net bacak | JEOPOLİTİK_GÜVENLİK | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_009`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_009) | 2023-11-10 → 2023-12-01 | **UP** +6.89% net bacak | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_007`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_007) | 2023-12-01 → 2023-12-01 | **UP** 3.57% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_010`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_010) | 2023-12-01 → 2023-12-12 | **DOWN** -4.46% net bacak | FONLAMA_FİNANSAL_STRES | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_008`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_008) | 2023-12-04 → 2023-12-04 | **DOWN** 3.05% MAX |hareket| | İÇSEL_POZİSYON_DÖNÜŞÜ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_009`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_009) | 2023-12-08 → 2023-12-08 | **DOWN** 3.25% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_011`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_011) | 2023-12-12 → 2023-12-27 | **UP** +4.97% net bacak | ALTIN_FİZİKİ_RESERVE_TALEP | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_010`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_010) | 2023-12-19 → 2023-12-19 | **UP** 3.07% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_012`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_012) | 2023-12-27 → 2024-02-14 | **DOWN** -4.11% net bacak | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |

### 2024 — 33 kayıt (13 uzun V1 / 20 kısa-orta V2)

| Olay kimliği (ayrıntı açılır) | Fiyat penceresi | Altın hareketi / **metrik** | Ekonomi aday sınıfı | Kanıt durumu |
|---|---|---|---|---|
| [`SWING_V1_013`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_013) | 2024-02-14 → 2024-04-19 | **UP** +19.98% net bacak | ALTIN_FİZİKİ_RESERVE_TALEP | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_011`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_011) | 2024-03-04 → 2024-03-11 | **UP** 5.67% MAX |hareket| | ALTIN_FİZİKİ_RESERVE_TALEP | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_012`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_012) | 2024-04-01 → 2024-04-11 | **UP** 5.56% MAX |hareket| | ALTIN_FİZİKİ_RESERVE_TALEP | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_013`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_013) | 2024-04-12 → 2024-04-12 | **DOWN** 3.62% MAX |hareket| | İÇSEL_POZİSYON_DÖNÜŞÜ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_014`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_014) | 2024-04-19 → 2024-04-30 | **DOWN** -4.38% net bacak | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_014`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_014) | 2024-04-24 → 2024-04-24 | **DOWN** 3.12% MAX |hareket| | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_015`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_015) | 2024-04-30 → 2024-05-20 | **UP** +6.14% net bacak | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_015`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_015) | 2024-05-15 → 2024-05-20 | **UP** 3.83% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_016`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_016) | 2024-05-20 → 2024-06-07 | **DOWN** -5.46% net bacak | ALTIN_FİZİKİ_RESERVE_TALEP | Derin kaynak; nedensellik açık |
| [`C_CORR_016`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_016) | 2024-05-23 → 2024-05-27 | **DOWN** 4.01% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_017`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_017) | 2024-06-07 → 2024-06-07 | **DOWN** 3.59% MAX |hareket| | ALTIN_FİZİKİ_RESERVE_TALEP | Derin kaynak; nedensellik açık |
| [`SWING_V1_017`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_017) | 2024-06-07 → 2024-07-16 | **UP** +7.63% net bacak | MAKRO_FAİZ_BEKLENTİSİ | Derin kaynak; nedensellik açık |
| [`C_CORR_018`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_018) | 2024-06-13 → 2024-06-13 | **DOWN** 3.02% MAX |hareket| | JEOPOLİTİK_GÜVENLİK | Derin kaynak; nedensellik açık |
| [`C_CORR_019`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_019) | 2024-07-16 → 2024-07-17 | **UP** 4.43% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_018`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_018) | 2024-07-16 → 2024-07-25 | **DOWN** -4.22% net bacak | FONLAMA_FİNANSAL_STRES | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_020`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_020) | 2024-07-25 → 2024-07-25 | **DOWN** 3.29% MAX |hareket| | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_019`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_019) | 2024-07-25 → 2024-10-30 | **UP** +17.89% net bacak | ALTIN_FİZİKİ_RESERVE_TALEP | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_021`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_021) | 2024-08-01 → 2024-08-01 | **UP** 3.46% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_022`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_022) | 2024-08-12 → 2024-08-16 | **UP** 3.77% MAX |hareket| | İÇSEL_POZİSYON_DÖNÜŞÜ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_023`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_023) | 2024-09-13 → 2024-09-16 | **UP** 3.23% MAX |hareket| | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_024`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_024) | 2024-09-24 → 2024-09-26 | **UP** 3.83% MAX |hareket| | ALTIN_FİZİKİ_RESERVE_TALEP | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_025`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_025) | 2024-10-22 → 2024-10-22 | **UP** 3.24% MAX |hareket| | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_020`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_020) | 2024-10-30 → 2024-11-15 | **DOWN** -8.05% net bacak | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_026`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_026) | 2024-11-06 → 2024-11-15 | **DOWN** 5.32% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_021`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_021) | 2024-11-15 → 2024-11-22 | **UP** +5.97% net bacak | JEOPOLİTİK_GÜVENLİK | Derin kaynak; nedensellik açık |
| [`C_CORR_027`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_027) | 2024-11-20 → 2024-11-22 | **UP** 5.97% MAX |hareket| | JEOPOLİTİK_GÜVENLİK | Derin kaynak; nedensellik açık |
| [`SWING_V1_022`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_022) | 2024-11-22 → 2024-11-25 | **DOWN** -3.36% net bacak | JEOPOLİTİK_GÜVENLİK | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_028`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_028) | 2024-11-25 → 2024-11-25 | **DOWN** 3.36% MAX |hareket| | JEOPOLİTİK_GÜVENLİK | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_023`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_023) | 2024-11-25 → 2024-12-11 | **UP** +3.55% net bacak | JEOPOLİTİK_GÜVENLİK | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_029`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_029) | 2024-12-11 → 2024-12-11 | **UP** 3.22% MAX |hareket| | JEOPOLİTİK_GÜVENLİK | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_024`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_024) | 2024-12-11 → 2024-12-18 | **DOWN** -4.90% net bacak | ALTIN_FİZİKİ_RESERVE_TALEP | Derin kaynak; nedensellik açık |
| [`C_CORR_030`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_030) | 2024-12-18 → 2024-12-19 | **DOWN** 4.90% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Derin kaynak; nedensellik açık |
| [`SWING_V1_025`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_025) | 2024-12-18 → 2025-02-24 | **UP** +14.24% net bacak | TİCARET_TARİFE_POLİTİKASI | Tarihli bağlam; ilk haber UTC açık |

### 2025 — 41 kayıt (17 uzun V1 / 24 kısa-orta V2)

| Olay kimliği (ayrıntı açılır) | Fiyat penceresi | Altın hareketi / **metrik** | Ekonomi aday sınıfı | Kanıt durumu |
|---|---|---|---|---|
| [`C_CORR_031`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_031) | 2025-02-05 → 2025-02-10 | **UP** 3.89% MAX |hareket| | TİCARET_TARİFE_POLİTİKASI | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_026`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_026) | 2025-02-24 → 2025-02-28 | **DOWN** -3.24% net bacak | TİCARET_TARİFE_POLİTİKASI | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_027`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_027) | 2025-02-28 → 2025-04-02 | **UP** +9.64% net bacak | TİCARET_TARİFE_POLİTİKASI | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_032`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_032) | 2025-03-13 → 2025-03-19 | **UP** 4.06% MAX |hareket| | TİCARET_TARİFE_POLİTİKASI | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_033`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_033) | 2025-03-31 → 2025-04-02 | **UP** 3.76% MAX |hareket| | TİCARET_TARİFE_POLİTİKASI | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_028`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_028) | 2025-04-02 → 2025-04-07 | **DOWN** -4.78% net bacak | TİCARET_TARİFE_POLİTİKASI | Derin kaynak; nedensellik açık |
| [`C_CORR_034`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_034) | 2025-04-04 → 2025-04-08 | **DOWN** 4.78% MAX |hareket| | TİCARET_TARİFE_POLİTİKASI | Derin kaynak; nedensellik açık |
| [`SWING_V1_029`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_029) | 2025-04-07 → 2025-04-21 | **UP** +14.78% net bacak | TİCARET_TARİFE_POLİTİKASI | Derin kaynak; nedensellik açık |
| [`C_CORR_035`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_035) | 2025-04-09 → 2025-04-22 | **UP** 8.51% MAX |hareket| | TİCARET_TARİFE_POLİTİKASI | Derin kaynak; nedensellik açık |
| [`SWING_V1_030`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_030) | 2025-04-21 → 2025-05-01 | **DOWN** -5.41% net bacak | TİCARET_TARİFE_POLİTİKASI | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_036`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_036) | 2025-04-23 → 2025-04-23 | **DOWN** 3.04% MAX |hareket| | ALTIN_FİZİKİ_RESERVE_TALEP | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_037`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_037) | 2025-05-01 → 2025-05-01 | **DOWN** 3.29% MAX |hareket| | TİCARET_TARİFE_POLİTİKASI | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_031`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_031) | 2025-05-01 → 2025-05-06 | **UP** +5.95% net bacak | TİCARET_TARİFE_POLİTİKASI | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_038`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_038) | 2025-05-06 → 2025-05-07 | **UP** 5.95% MAX |hareket| | TİCARET_TARİFE_POLİTİKASI | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_032`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_032) | 2025-05-06 → 2025-05-14 | **DOWN** -7.41% net bacak | TİCARET_TARİFE_POLİTİKASI | Derin kaynak; nedensellik açık |
| [`C_CORR_039`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_039) | 2025-05-09 → 2025-05-16 | **DOWN** 5.56% MAX |hareket| | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Derin kaynak; nedensellik açık |
| [`SWING_V1_033`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_033) | 2025-05-14 → 2025-06-13 | **UP** +8.03% net bacak | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_040`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_040) | 2025-05-15 → 2025-05-15 | **UP** 3.14% MAX |hareket| | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_041`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_041) | 2025-05-21 → 2025-05-26 | **UP** 4.82% MAX |hareket| | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_042`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_042) | 2025-06-13 → 2025-06-13 | **UP** 3.68% MAX |hareket| | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_034`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_034) | 2025-06-13 → 2025-06-27 | **DOWN** -4.61% net bacak | JEOPOLİTİK_GÜVENLİK | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_035`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_035) | 2025-06-27 → 2025-07-22 | **UP** +4.80% net bacak | TİCARET_TARİFE_POLİTİKASI | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_043`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_043) | 2025-07-22 → 2025-07-22 | **UP** 3.23% MAX |hareket| | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_036`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_036) | 2025-07-22 → 2025-07-30 | **DOWN** -4.55% net bacak | TİCARET_TARİFE_POLİTİKASI | Derin kaynak; nedensellik açık |
| [`C_CORR_044`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_044) | 2025-07-29 → 2025-07-30 | **DOWN** 3.30% MAX |hareket| | TİCARET_TARİFE_POLİTİKASI | Derin kaynak; nedensellik açık |
| [`SWING_V1_037`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_037) | 2025-07-30 → 2025-10-20 | **UP** +33.00% net bacak | MAKRO_FAİZ_BEKLENTİSİ | Derin kaynak; nedensellik açık |
| [`C_CORR_045`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_045) | 2025-08-07 → 2025-08-07 | **UP** 3.25% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_046`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_046) | 2025-09-01 → 2025-09-08 | **UP** 4.76% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_047`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_047) | 2025-09-23 → 2025-09-23 | **UP** 3.29% MAX |hareket| | JEOPOLİTİK_GÜVENLİK | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_048`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_048) | 2025-10-01 → 2025-10-20 | **UP** 8.83% MAX |hareket| | TİCARET_TARİFE_POLİTİKASI | Derin kaynak; nedensellik açık |
| [`C_CORR_049`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_049) | 2025-10-17 → 2025-10-29 | **DOWN** 8.58% MAX |hareket| | İÇSEL_POZİSYON_DÖNÜŞÜ | Derin kaynak; nedensellik açık |
| [`SWING_V1_038`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_038) | 2025-10-20 → 2025-10-29 | **DOWN** -9.78% net bacak | TİCARET_TARİFE_POLİTİKASI | Derin kaynak; nedensellik açık |
| [`SWING_V1_039`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_039) | 2025-10-29 → 2025-11-12 | **UP** +6.76% net bacak | MAKRO_FAİZ_BEKLENTİSİ | Derin kaynak; nedensellik açık |
| [`C_CORR_050`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_050) | 2025-11-10 → 2025-11-13 | **UP** 5.41% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Derin kaynak; nedensellik açık |
| [`SWING_V1_040`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_040) | 2025-11-12 → 2025-11-17 | **DOWN** -3.58% net bacak | ALTIN_FİZİKİ_RESERVE_TALEP | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_051`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_051) | 2025-11-14 → 2025-11-17 | **DOWN** 3.58% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_041`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_041) | 2025-11-17 → 2025-12-26 | **UP** +12.08% net bacak | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_052`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_052) | 2025-11-28 → 2025-11-28 | **UP** 3.80% MAX |hareket| | DİĞER_BİLEŞİK_EKONOMİK_BİLGİ | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_053`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_053) | 2025-12-22 → 2025-12-26 | **UP** 4.67% MAX |hareket| | MAKRO_FAİZ_BEKLENTİSİ | Tarihli bağlam; ilk haber UTC açık |
| [`SWING_V1_042`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#swing_v1_042) | 2025-12-26 → 2025-12-31 | **DOWN** -4.73% net bacak | FONLAMA_FİNANSAL_STRES | Tarihli bağlam; ilk haber UTC açık |
| [`C_CORR_054`](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md#c_corr_054) | 2025-12-29 → 2025-12-31 | **DOWN** 4.73% MAX |hareket| | FONLAMA_FİNANSAL_STRES | Tarihli bağlam; ilk haber UTC açık |

## 7. Haber zamanı, negatif kontrol ve yapısal karşı-vakalar

**85 ABD NFP/CPI/FOMC release** penceresinde NFP ilk 15 dk medyan **mutlak** XAU hareketi **%0,3344**, eşsaat haftalık kontrol **%0,0802**; CPI **%0,2927 vs %0,0972**. Etkinin volatilite yönünden anlamlı olması otomatik UP/DOWN ya da gelecekte kalıcı hareketi kanıtlamaz. Eski 85 olaylık takvimde **2025 FOMC eksik**, ayrı 46 olaylık FOMC pilotunun evreni farklı.

- **10 Mart 2023:** pozitif NFP sürprizine rağmen altın ilk M15 +%0,540; SVB güven riski.
- **7 Haziran 2024:** PBoC bilgisi NFP'den önce geldi; NFP ilk 15dk −%0,612; aynı bacağı iki habere körlemesine atfetme.
- **4 Nisan 2025:** NFP öncesi 60dk altın −%0,975; NFP sonrası ilk 15dk −%0,261; ilk neden NFP olmayabilir.
- **Nisan 2025 vs Ekim 2025:** her ikisi altın DOWN; ilki geniş likidite stresi, ikincisi daha metal-özel çözülme imzası adayı. Aynı yön ≠ aynı neden.
- **‘Haber yok’ kontrol günü:** gerçek firstprint taraması tamamlanmadan ‘haber sıfır’ iddiası yok; şok etiketini gördükten sonra geçmişi seçip sahte beceri üretme.

## 8. Ayrı 2026 Astra araştırmasından aktarılacak dersler

[Astra'nın 273 günlük haber–karar metodolojisi ve kayıp denetimi](GOLD_ASTRA_2026_JAN_SEP_DAILY_REPLAY_EVENT_MECHANISM_TRANSFER_AUDIT_20261014.md) şunu gösteriyor: sadece çok hareketli günleri seçmek yerine **bütün günlerde haber → beklenti → dolar/faiz/petrol → XAU → karşıt neden → karar** zinciri gerekir. Ancak 2026 HistData saat sözleşmesi ve gerçek banka verisinin yokluğu 2023–25 NY17 çalışmasıyla karışmamalı.

2026 raporunun 19 tamamlanmış GOLD/NAKİT turunda her işlem tarafında %0,8 komisyon varsayımıyla **strateji yaklaşık −%31,68**, pasif altın yaklaşık **−%6,81**. Bu, mekanizma yorumunu otomatik para kazanma yöntemi sanmamak için güçlü karşı örnek. Enerji arzı → petrol → enflasyon/faiz baskısı; ateşkes → enerji rahatlaması; Fed/CPI; altın rezerv/kurumsal güven ve likidite aktarımı **aday** kalır. Hangi ara değişkenin ne zaman gözlendiği doğrulanmadan kesin sınıf olmaz.

## 9. 15 dakikalık karar denemesine veri aktarımı

**Girdiler:** yalnız tamamlanmış M15 fiyat, tarihe göre gerçekten yayımlanmış haber, varsa yayından önce belirlenmiş consensus, USD/2Y/10Y/diğer metaller/petrol ve GVZ/VIX'in doğru lag'i. **Sınıflandırma:** olay + rakip haber + aşama (ONSET/CONTINUATION/EXHAUSTION/REVERSAL/UNCERTAIN). **Karar:** pozisyona göre AL/SAT/TUT/BEKLE/ABSTAIN; ancak komisyon/spread sonrası *gelecekte kalan* olası hareket yeterliyse aday. **İcra kapısı:** AL/SAT adayında tamamlanmış M1'ler, ardından gerçek sonraki banka ASK/BID; yalnız spot MID+M15 makas varsa açıkça **PROXY**. **Denetim:** event_id, episode_id, ilk haber UTC, veri available_at, karar ve fill saati, güncel pozisyon, bankacılık maliyeti, yanlış alarm/kaçan fırsat, ÖĞREN-03 hipotez ID.

**İşlem maliyeti:** alım **%0,8**, satım **%0,8** ve banka makası. Makas sıfırken bir tam al–sat turunun yalnız komisyonları karşılaması için fiyatın yaklaşık **%1,6194** yükselmesi gerekir. TUT→SAT→tekrar AL döngüsünün ayrı maliyeti vardır. Geçmiş toplam dalga %3 veya %5 hareket etti diye, karar anında **kalan fiyat yolu** da o kadar değildir. Bu aşamada kalibre edilmiş kalan 4h/12h/1d/3/5seans yön/riski ve güvenilir işlem avantajı doğrulanmamıştır.

## 10. Bilimsel kalite kontrol ve güncelleme disiplini

| Sınır / test | Şu an | Ne gerekecek? |
|---|---|---|
| Düzeltilmiş fiyat kaydı, yön ve yöntem | **96/96** | Olayı bağımsız haber şoku saymama |
| Tarihli eski dış kaynak ilişkilendirmesi | **153 URL ilişkisi**, **32** fiyat penceresi bittikten sonra | Özgün firstprint, tarih/saat, sürüm ve yayın gecikmesi |
| 38 derin kaynak araştırmasının birebir corrected ID eşlemesi | **18 V1**, eski 20 V2 otomatik eşleşmedi | Saat/fiyat/kaynak tutarlı eski-yeni crosswalk |
| Saatli makro ilk fiyat tepkileri | **85 olay** | As-of consensus ve rakip eşsaatli haber kontrolleri |
| 96 fiyat bacağının ilk kesin haber nedeni ve nedensel katkısı | **0/96 doğrulandı** | İlk XAU onset UTC + firstprint + aynı-UTC USD/faiz/metaller + sakin zaman kontrolleri |
| Banka gerçek ASK/BID ve emir uygulaması | **YOK** | Gerçek banka saati, fiyat ve %0,8 her yön/spreadden sonra net performans |
| Üç maliyetli örneğin bağımsız OOS sonucu | **YOK** | Sabitlenmiş kuralı çalışmada görülmeyen ters/normal günlerde sınama |

**Ana yönetim ilkesi:** Eski 5.190 satırlık bilimsel arşiv değiştirilmez, yeni olaylar **OLAY-02 bu dosyaya** doğru kimlikle ve delil yollarıyla eklenir; ortak mekanizma deneyimleri **ÖĞREN-03**, çalışma hedefleri **ANA-01**, aylık durum ise **DURUM-04**. Yanlış bir sayı ya da ekonomik atıf düzeltilirse orijinali sessizce silme; kaynak, `supersedes` ve sürüm notuyla düzelt.

**Durum:** `96_PRICE_RECORDS_INDIVIDUALLY_LINKED / 85_TIMED_MACRO_EVENT_WINDOWS / 3_COSTED_RETRO_CASES / 0_VERIFIED_PRICE_INITIATION_CAUSES / RESEARCH_ONLY_NO_AUTOMATED_TRADING`.
