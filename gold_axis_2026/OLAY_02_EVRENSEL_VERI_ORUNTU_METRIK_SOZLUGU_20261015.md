# OLAY-02 — TÜM VAKALAR İÇİN ORTAK VERİ ÖRÜNTÜSÜ METRİK ve ENDEKS SÖZLÜĞÜ (V1)

**Tarih:** 2026-10-15 · **Kapsam:** 2023–2025 96 tarihli fiyat kaydı / 84 tekil as-of kontrol / 38 derin dokümantasyon / 12 ekonomik olay örgüsü. **Çalışma tipi:** yeniden kullanılabilir araştırma metodolojisi, **Ocak 2026 koşusu değildir**. ANA-01/OLAY-02/ÖĞREN-03 yerinde korunur. Bu belge OLAY-02 metodoloji ekidir.

**Temel ayrım:** OLAY (ilk belge) ≠ ÖĞREN (tarihsiz mekanizma hipotezi) ≠ ÖLÇÜM (açıklama öncesi ve esnası zamanlı piyasa örüntüsü) ≠ KARAR (maliyet sonrası koşullu aksiyon). Aynı fiyat yolunda G02 tetikleyici, G05 aktarım ve G06 güçlendirici olabilir. Bir sayı yüksek diye mekanizma ispatlanmaz.

## 1. As-of zorunlu zaman/veri sözleşmesi

- `t` Türkiye saatiyle 15 dakikalık kontrol anı, bütün matematik UTC eşleştirilmiş veriden. XAU M15 barı ancak `start_utc + 15m <= t`; doğal barı `native_minute_bars=15` ve seans açık olmalı; sahte weekend, 14 dakikalık bar ve ileri doldurma yasak.
- H1 CME futures `ts_event+60m<=t` asgari kapalı-bar şartı; *feed latency/publish available_at* doğrulanmadıysa canlı onay yetkisi yok. Her enstrüman (GC, SI, NQ, ZN, CL) için sembol, continuous-roll, hacim, bar yaşı ve kontrat değişimi QA alanları tutulur. `ZN` **tahvil futures fiyatıdır**; faiz getirisi veya 2Y/10Y yield değildir.
- As-of haber: `first_published_at`, `revised_at`, `available_at`, `actual`, `consensus_vintage`, `revised_value` ve `source_url` ayrıdır. Sonradan değiştirilmiş Reuters/WGC raporu önceki slota geçirilemez.
- Veri kapsamı, her metrik için `observed`, `age_minutes`, `source_id`, `confidence`, `missing_reason` içerir. **Eksik değer 0 yapılmaz.** Bilgi yoksa `UNKNOWN` korunur.
- İlgili kayıtlar: [96'lık ortak matris](OLAY_02_96_TUM_VAKA_EVRENSEL_ORUNTU_MATRIKS_20261015.csv), [84 tekil as-of kontrol](OLAY_02_84_ASOF_FIYAT_CAPRAZ_METRIKLER_20261015.csv), [38 derin örgü-vaka matrisi](OLAY_02_38_DERIN_VAKA_12_ORGU_METRIK_KOPRUSU_20261015.csv).
- İki ayrı kayıt: `PREDECISION_FEATURE` t'den önce bilinen; `POSTDECISION_OUTCOME` t'den sonra oluşan etiket. Eski V1 net bacak yüzdesi ve V2 maksimum |hareket| **yalnız ikinci türdür**; yeni tahmine girdi yapılamaz. 96 fiyat kimliği 84 ayrı karar kontrolü oluşturur, 12 mükerrer aynı checkpoint ağırlıklandırılmaz.

## 2. Evrensel metrik sözlüğü (aynı alanlar bütün ORG01–ORG12 için)

| ID | Metrik; özet tanım (matematik) | Frekans / kanıt kapısı | Vaka/karar işlevi |
|---|---|---|---|
| **Q01** | `BAR_VALID` = tam M15 var mı? `STALE_AGE` = t−bar_end; `MARKET_STATE` = OPEN/CLOSED/MISSING | 15m, zorunlu | Veri hatasını mekanizma sanma |
| **P01** | `r15` = 100 ln(P_t/P_{t-15m}) | XAU M15, tam ardışık | İlk tepki |
| **P02** | `r1h,r4h,r12h,r1d` = 100 ln(P_t/P_{t-h}); uç barlar tamam | 1h/4h/12h/1 seans | İvme ve trend devamı |
| **P03** | `RV_h` = 100 sqrt(Σ r_i²); log getiriler *ondalık*, toplam sadece ardışık barlar | M15, 1/4/12h | Gerçekleşen toplam oynaklık |
| **P04** | `DOWN_RV_SHARE` = Σ(r_i<0) r_i² / Σ r_i²; tersine `UP_RV_SHARE` | M15, 4/12h | Aşağı baskının oynaklık payı |
| **P05** | `EFF_h` = |ln(P_t/P_{t-h})| / Σ |ln(P_i/P_{i-1})| (0–1) | M15, tam h | Yönlü ilerleme mi çalkantı mı? |
| **P06** | `CLOSE_LOC_h` = (C_t−min(L))/(max(H)−min(L)) | M15 OHLC, 1/4/12h | Bölgeye göre kapanış gücü (0–1) |
| **P07** | `DD_FROM_SEEN_HIGH_h`=100(C_t/max_{s≤t} H_s−1); `RALLY_FROM_SEEN_LOW_h` analoğu | M15, 4/24/120h | Tersine dönüş/erime |
| **P08** | `GAP_ADVERSE`=önceki geçerli seans sonu ile ilk yeni seans arası fiyat farkı, **bir işlem fiyatı değil** | seans açık/kapalı geçişi | Açılış şoku, hafta sonu ayrı |
| **P09** | `IMPULSE_ABS_Z` = (|r15|−20 geçmiş seansın aynı saat |r15| medyanı)/(1.4826 MAD); 20 yetersizse NA | Aynı saat/TOD & mevsimsellik | Olağan dışı ilk şok |
| **P10** | `JUMP_PROXY` = max(|r15|)/RV4h ve `RV−BPV` ayrıştırması; sıçrama testi ancak yeterli dakika veri ve kalibrasyonla | M15 / uygun yüksek frekans | Tek kırılma mı birikim mi? |
| **P11** | `RV_ACCEL`=RV4h / median(RV4h, önceki 20 tam seans aynı saat) | rolling geçmiş | Rejim hızlanması |
| **P12** | `REVERSAL_STRENGTH` = 100 ln(P_t/P_{seen_peak_or_trough}), faz-yön ve minimum sıralı pivot ile; pivot yalnız t'ye kadar | M15, olay süresince | P4/P5 dönüş adayı |
| **P13** | `DRAW_DOWN_SPEED` = DD(t)−DD(t−1h), %puan/saat | M15 | Yükseliş/satış baskısı hızlanıyor mu? |
| **P14** | `CHOP/WHIPSAW` = işaret değişimi / toplam geçerli M15 adedi; ve maksimum karşı-yön düzeltmesi | M15 4/12h | Güçlü/kararsız trend ayrımı |
| **P15** | `SESSION_REL_STRENGTH` = cari |r15| veya RV4h / geçmiş aynı seans-saat karşılaştırma | Asya/Avrupa/ABD ayrı baseline | Saat etkisine duyarlı hareket |
| **X01** | `rNQ1h,rSPX1h`, `rXAU1h×rNQ1h` işareti; ancak saat-sonu eşleşme şartı sağlanırsa co-move | H1/daha sık | Güvenli liman vs genel satım |
| **X02** | `rSI,rXPT,rXPD` ve `GSR=XAUpx/XAGpx`, `Δln GSR` | zaman eş / roll QA | Altına özel ve geniş metal şokunu ayır |
| **X03** | `DXY_Δ,UST2Y_Δbp,UST10Y_Δbp,TIPS10Y_Δbp` ayrı as-of yayımlarla; yield futures fiyatına eşit değildir | tick/H1 güvenilir | G01 aktarım kanalı |
| **X04** | `rWTI,rBrent,ΔVIX,ΔGVZ`; risk-on/off ve enerji/enflasyon rekabeti | H1/daily lag | G03/G05 / volatilite kanalı |
| **X05** | `ROLL_CORR(XAU,NQ)`, `ROLL_CORR(XAU,SI)` 24/72 tamam H1 + örnek sayısı + t'den önce veriler | H1 asof | Rejimde eş hareket değişimi |
| **X06** | `LEAD_LAG(XAU,NQ/USD)` ve ortak sıçrama zamanı; salt korelasyon yönlü neden değildir | yayım saati gerekli | Önce hangi pazar tepki verdi? |
| **N01** | `EVENT_TIME` = yayın/teyit zamanı, `Δt` = karar−firstprint; `NEWS_NEW_AT_T` kaynaklı | resmî/özgün haber | P1 tetik saatini saptama |
| **N02** | `SURPRISE` = actual−o anda geçerli consensus; `SURPRISE_Z`=SURPRISE / geçmiş aynı seri std; bileşenler ayrı | veri-vintage kritik | G01 sözlü değil ölçülmüş şok |
| **N03** | `ABNORMAL_REACTION15` = |r_after15| − geçmiş 4 benzer hafta aynı saat ort | resmî açıklama + placebo | Fiyat sıradan mı haber-şoku mu? |
| **N04** | `REACTION_DECAY` = |r_after60|/|r_after15|, ayrıca 15→60→240 dakika **aynı işaret/ters** | yalnız post-event analizi, t'de ulaşılabilen kadar | İlk haber tepkisi söndü mü? |
| **N05** | `NEWS_COMPETITION`: 1/4/12s pencere ayrı firstprint sayısı, rolü; `RIVAL_EXPLANATION` | kaynaklı haber saati | Tek nedene yanlış atfı engelle |
| **F01** | `FUT_VOLUME_SURPRISE`, `ΔOI`, `ETF_NET_FLOW` ve `CFTC_POSITION`; her biri yayın gecikmesi ve kontrat için | H1, günlük/haftalık lag | G04/G05/G06 pozisyon/akım |
| **F02** | `SPREAD_BPS`=(ask−bid)/mid×10^4, `TICK_INTENSITY`=kıyaslı dakika/tick, `QUOTE_GAP` | gerçek bağımsız BID/ASK | Likidite/uygulanabilirlik |
| **F03** | `MARGIN_STEP` = borsanın duyurduğu ilk as-of marjin değişimi, `VOLUME/OI_SPIKE` | kaynak firstprint | ORG12 ayrıştırma |
| **B01** | `ROUNDTRIP_PRICE_HURDLE`=1/(0.992²)−1≈%1,6194, **ilave spread ve gecikme hariç** | banka sözleşmesi | Yeni tam tur beklenen kalan hareket > maliyet mi? |
| **B02** | `NET_REMAINING_UP/DOWN`: yalnız geçmiş örneklerde dondurulmuş, kalibre ileri getiri dağılımı−maliyet; gerçekleşmiş bacak getirisi **değil** | gerçek banka quote + bağımsız backtest | Pozisyon değiştirme kararı |
| **B03** | `ACTION_ELIGIBLE`: kaynak, çapraz piyasa, rakip neden, maliyet ve yürütme kapıları ayrı PASS | otomatik onay değil | AL/SAT/TUT/BEKLE |

**Birleşim:** Bütün olaylarda aynı `Q/P/X/N/F/B` alanları tutulur. DNA ailelerinin farkı, gözlenen metriklerin **hangi koşullu ilişkiyi test ettiği** ve hangi negatif kontrolün gerekli olduğudur. Örüntü bilinmiyor diye sahte 0 veya nötr güven atanmaz. P09/P11/P15/ X05/X06/F* ve B02 şu an **tasarım**, henüz bütün 96 vakaya hesaplanmış değil.

## 3. Ortak ÖRÜNTÜ İNDEKSLERİ (araştırma adayı; doğrulanmış AL/SAT kuralı değil)

| İndeks | Girdi ve şeffaf bileşim | Ne ayırır? | İlk durum |
|---|---|---|---|
| **PCI — Price Conviction Index** | ayrı alanlar `sign(r4h)`, `|r4h|/max(RV4h,ε)`, `EFF4h`, `CLOSE_LOC4h`; tek skora geçmeden işaretli bileşen matrisi | Kalıcı trend / gürültü | **81/84** 4h girdisi var |
| **VAI — Volatility Acceleration Index** | `RV4h / TOD-RV4h-20d-median`, `IMPULSE_ABS_Z`, asimetrik semivaryans | Yeni şok / olağan oynaklık | TOD baseline hesaplanacak |
| **RFI — Reversal Fragility Index** | `−DD_FROM_SEEN_HIGH` + `DOWN_RV_SHARE` + `DRAW_DOWN_SPEED` + negatif haber yanlışlama; ayrı normalize edilir | P3→P4 yorulma mı, kriz mi? | Çekirdek 81/84, kalibrasyon yok |
| **CHI — Cross-market Haven Index** | XAU ile NQ, DXY, SI, USD yield **eş-saatli** işaretleri; en az 2 bağımsız uygun kanal, alternatifler | Güvenli liman vs USD/likidite | NQ 83/84; DXY/faiz ve SI eksik |
| **LPI — Liquidity Pressure Index** | altın+NQ+SI/CL beraber düşüş imzası + spread/hacim/OI/marjin kanıtı; fonlama varsayılamaz | G05/G06, ORG08/12 | **Şimdilik NA** |
| **MRI — Macro Repricing Index** | tek ilan sürpriz z'si, 15/60/240 tepki, DXY, gerçek 2Y/reel yield değişimi; rakip haber | G01 para politikası aktarımı | 85 ayrı release placebo, tam değil |
| **FPI — Flow/Positioning Index** | ETF sürpriz akış, CFTC net-length vintage, OI/hacim değişimi ve fiyat | G04/ORG09/10 | **Şimdilik NA** |
| **DPI — DNA Pattern Compatibility** | ORG01–12 için `MATCHED_OBSERVABLES / TESTABLE_OBSERVABLES` + ayrı `FALSIFIER_COUNT`, **min. 3 uygun ayrıştırıcı ve bağımsız kontrol olmadan SKOR YOK**. Eşit puan 'kâr olasılığı' değildir. | En iyi *aday* olay karakteri | 12 örgü için aşağıdaki matriste kriterler |
| **NAI — Net Action Feasibility** | `expected_remaining_after_decision − buy/sell fees − actual spread − latency/slippage` ve rakip senaryodaki zarar; kalibrasyonsuz => NA | İşlem yapılmalı mı? | **Uygulanabilir banka kotasyonu yok** |

**İlk denemede indeksler tek sayıya indirgenip sahte 0–100 güvene dönüştürülmeyecek.** Bilimsel sonraki aşama: normalizasyon, eşikler ve ağırlıkları 2023–2024 train/validation üzerinde dondur; 2025 bağımsız ileri test; 2026 retrospektif sadece stres. Rejim ve ters vaka karşılaştırması zorunlu.

## 4. ORG01–ORG12 için AYNI metriklerin beklenen koşullu örüntüsü ve yanlışlamaları

| Örgü | İlk beklenecek veri örüntüsü | Ayırıcı metrikler | Kritik yanlışlama |
|---|---|---|---|
| **ORG01** fırsat maliyeti gevşemesi | UST2Y/10Y veya reel getiriler↓, DXY↓ ve XAU↑; metallere özgü talep ayrıca olabilir | N02/MRI, X03, P02/P05, X02 | XAU↑ ama getiri+USD↑ ise G04/G03 alternatifleri |
| **ORG02** fırsat maliyeti baskısı | Faiz ve DXY↑, XAU↓; bazen metaller/hisseler↓ | X03, N02, P04/P07, X01 | Birlikte co-sell otomatik faiz nedeni değil |
| **ORG03** banka stresi | Kredi spreadi / bankacılık stresi ↑; XAU↑ ve Fed easing adayı veya önce likidite satışı | N01, X03, F02, X01, P04 | İlk banka haberinden önce fiyat hareketi ve diğer makro |
| **ORG04** jeopolitik risk yükselişi | İlk güvenlik haberinden sonra XAU↑; NQ↓, enerji/gümüş farklı yanıt verebilir | N01, X01/X04, P09/P05 | Haberden önce altın hareketi |
| **ORG05** jeopolitik rahatlama | Risk azaltıcı ilk haber + altın risk primi sönmesi, hisseler rahatlama | N01, X01, X03, P07/P12 | USD/getiri şoku veya genel risk tasfiyesi |
| **ORG06** tarife koruması | Tarife belirsizliği↑ + altın güvenli liman eğimi, NQ zayıflık olabilir | N01, CHI, P01/P05, X01 | Geniş likidite satışı: altın da düşebilir |
| **ORG07** ticaret anlaşması/rahatlama | İlk anlaşma haberi + XAU çekilme ve risk-on hisseler | N01, X01/X03, P07 | Altın+NQ birlikte↓ ise salt rahatlama şüpheli |
| **ORG08** iki fazlı politik risk | İlk faz XAU+NQ+metaller↓; sonra ayrı altın toparlanması | LPI, P04, P14, N05, X01 | Gerçek marjin/teminat ve faz sırası yoksa kanıt değil |
| **ORG09** fizikî/finansal birikim | ETF/OI/rezerv pozitif sürpriz, fiyat trendi gecikmeli hızlanma | FPI, P05, P11, X02 | Sonradan WGC raporu ilk akım kanıtı olamaz |
| **ORG10** pozisyon doygunluğu/düzeltme | Önce yüksek EFF/momentum, sonra DD hızlanması ve down semivaryans↑ | PCI→RFI, P04/P07/P10/P14, F01 | Yeni makro/jeopolitik şok asıl tetik olabilir |
| **ORG11** rezerv × makro çatışması | İki ayrı tarihli ilk kaynak, fiyat çok-fazlı, metal/reel getiri çelişkileri | N05, F01, MRI, X03, P14 | Bir haber diğerinden sonra geldiyse onu önceden neden sayma |
| **ORG12** marjin/ince piyasa | İlk borsa marjin duyurusu, metal satışları, spread/hacim/OI değişimi | N01, F02/F03, LPI, P10/P14 | Fiyat açıklamadan önce çöktüyse marjin ilk neden değil |

**Özellikle Nisan 2025 `SWING_V1_028`:** tarife şokunun altını yükseltmek yerine likidite satışına eşlik edebildiği bir karşıt vakadır. `G02` tetik ile `G05` aktarımı karıştırma. Aynı vakada `r4h`, `RV4h`, `NQ H1` ölçülür; ama karar anı ile uzun bacak sonu birbirine karışmaz.

## 5. Karar motoru: gözlem, evre, güven ve iki farklı portföy

**Her t kontrolünde tut:**
1. Veri yeterlilik ve as-of: Q01, seans, son tamam M15 ve ilk yayım. PASS değilse MISSING; sırf fiyat yok diye TUT bile yanlış 'piyasa görüşü' olarak puanlanmaz.
2. Gözlem: `P/Q` tüm fiyat karakteri, `X` mevcut çapraz kanallar, `N` ilk haber/çoklu olay rekabeti. Her kanalın yaşı ve kaynak ayrı.
3. Olay benzerliği: geçmiş 84 tekil checkpoint içinden aynı *ön karar* veri penceresi ve benzer habere dayalı komşular; gelecekteki fiyat, sonradan rapor ve aynı epizot/14 günlük embargo dışlanır. 38 derin vakadan güncel V1 ile eşleşen 18 doğrudan; eski V2 vaka ID'leri düzeltilmiş C_CORR ile sayısal eşlenmez.
4. ÖĞREN-03 P0→P5: tetik/aktarım/güçlendirici/ters-vaka ayrı. Kanıt yoksa G07/UNCERTAIN.
5. Hangi koşul yanlışlarsa karar görüşü değişir? `falsifier`, sonraki kontrol gereği ve horizon tanımla.
6. **İki portföy:** `GOLD→HOLD/SELL` ve `CASH→HOLD/BUY` ayrı; kısa satış varsayma. `expected_remaining` kalibre değilse yalnız araştırma önerisi, banka eylemi değil. İşlem yapılırsa sonraki uygulanabilir ASK/BID ve toplam ücret üzerinden kâr/zarar, ayrıca al/sat yapmama fırsat maliyeti hesaplanır.
7. **Sonradan öğrenilen:** 15/60/240dk ve 1/3/5 gün *yalnız karar kilitlendikten sonra* etiketlenir, ÖĞREN-03'e yalnız zamansız tekrar kullanılabilir mekanizma hipotezi geçer.

## 6. Bağımsız literatür dayanakları (verilmiş indekslerin doğrulanması değil)

- Cai, Cheung & Wong (2001), *What moves the gold market?*, Journal of Futures Markets: altın yüksek frekanslı volatilitede gün içi kalıbın ve duyuruların önemi, **saat etkisini normalize et**. https://onlinelibrary.wiley.com/doi/10.1002/1096-9934%28200103%2921%3A3%3C257%3A%3AAID-FUT4%3E3.0.CO;2-W
- Elder, Miao & Ramchander (2012), *Impact of macroeconomic news on metal futures*, Journal of Banking & Finance: duyuruda yön, şiddet, hız ve metal farklılığı. https://doi.org/10.1016/j.jbankfin.2011.06.007
- Smales & Yang (2015), *The importance of belief dispersion in the response of gold futures to macroeconomic announcements*: konsensüs beklentilerinin dağılımı etkinin kuvvetini değiştirebilir; tek 'actual' eksiktir. https://doi.org/10.1016/j.irfa.2015.01.017
- Evans (2011), *Intraday jumps and US macroeconomic news announcements*: jump, bipower, makro açıklama ve co-jump ayrımı. https://orca.cardiff.ac.uk/id/eprint/19013/
- Gençyürek & Ekinci (2023), *Safe-haven and hedging roles of precious metals for BRICS and Turkey*: zamanla değişen bağımlılık (DCC/coupla), 'altın güvenli limandır' her rejim için sabit değil. https://doi.org/10.1016/j.bir.2022.10.013

**Bu 33 metrik ve 9 indeks** metodoloji sözlüğüdür. 84 as-of noktasında gerçekten hesaplanan altın/çapraz veri çekirdeği ayrı CSV'de, geri kalanı **MISSING/NOT_IMPLEMENTED** statüsündedir. Bu metnin hiçbir formülü 2026 Ocak'ta yürütülmüş işlem veya doğrulanmış sinyal değildir.
