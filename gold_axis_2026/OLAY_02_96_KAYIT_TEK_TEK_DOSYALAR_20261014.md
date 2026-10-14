# OLAY-02 • 96 TARİHSEL FİYAT KAYDININ TEKİL OLAY FİŞLERİ
**2026-10-14 • OLAY-02 alt belgesi • Kaynaklardan otomatik çıkarılmış, denetlenebilir tarihsel çalışma.**

**Bu belgede 96 KAYIT vardır, 96 farklı şok veya 96 kanıtlı nedensel olay yoktur.** Düzeltilmiş **42 NY17 ZigZag V1** ve **54 NY17 çok-ufuk V2** aynı fiyat hareketini birden fazla kez gösterebilir. Aşağıdaki `C_CORR_...` kimlikleri **NY17 düzeltilmiş V2 kimlikleridir; eski `MOVE_V2_C...` kimliğine sayısal sıraya göre eşlenmez**. V2'nin `movement_pct_value` değeri **mutlak maksimum ufuk genliğidir, toplam pencere veya gerçekleşebilir işlem getirisi değildir**. V1 ise yön işaretli NY17 kapanışları üzerinden tanımlı fiyat bacağı getirisi.

**İlk yayımlanma/saat ve nedensellik bilimsel QA:** Güncel 96 kanıt CSV'sinde bütün satırlarda `first_original_news_UTC_verified_for_initiation=NO` ve `causal_contribution_measured=NO`. Tarihli habere bağ vermek başlangıcı o haberin ürettiğini ispatlamaz. **Geçmiş WGC açıklaması olay bittikten sonra yayımlandıysa yalnız retrospektif mekanizma bağlamıdır.** 85 NFP/CPI/FOMC aynı takvim tarihli M15 release tepkisi *makro saatinde fiyatı* gösterir, uzun olayın ilk sebebini değil. İlişkili altın dışı fiyatların çoğu *günlük*, kaynak saatleri asenkron ve 2026'da araştırılmış; 2023 anında gözlenmiş canlı teyit kabul edilmez.

**Kayıt standardı:** Olay kimliği → zaman ve fiyat etiketi → aynı tarihli resmi makro yayınlar ve ilk M15 gözlemi → yayımlanma tarihi bilinen diğer haberler ve gerçek tarihleri → 38 derin vaka eşleşmesi varsa gümüş/platin/paladyum/hisse ve karşıt açıklama → ekonomik hipotez → zaman/kanıt açığı → işlem uygunluğu. `UNKNOWN` dürüstçe saklanır.

Kaynak otoriteleri: [96 NY17 düzeltmeli bilimsel CSV](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv) · [38 derin dış kaynak matrisi](GOLD_HISTORICAL_38_EVENT_CAUSAL_SOURCES_QUANT_V2_20261014.csv) · [85 resmî zamanlı makro olay testi](GOLD_2023_2025_CPI_NFP_FOMC_M15_RELEASE_WEEKMATCH_EVENTSTUDY_20261014.csv) · [95 eski, **fiyat versiyonu farklı** çapraz-piyasa atlası](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv). [OLAY-02 ana sayfası](OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md).

---


### SWING_V1_001

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_001). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-01-03 → 2023-02-01 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+6.042%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_001` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2023-01-12 13:30 UTC**: ilk M15 **0.250%**, 60dk **0.257%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2023-02-01 19:00 UTC**: ilk M15 **-0.013%**, 60dk **0.793%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2023-01-06 13:30 UTC**: ilk M15 **0.644%**, 60dk **0.542%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-01-06** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2023-01-06/gold-price-jumps-daily-highs-us-service-sector-contracts-december). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2023-02-09** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-january-2023). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **-3.29%**, platin **-7.27%**, paladyum **-9.2%**, S&P 500 **7.72%**, Nasdaq-100 **13.81%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Other white metals ↓ while stocks ↑: not broad precious-metal rally. Retrospektif ek olgu: Ocak WGC GRAM: USD zayıf; UST 10Y -37bp; altın ETF -26t, COMEX managed money netlong 250t..

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. **Belirli bağımsız makro alt-vaka hesabı:** [5–13 Ocak NFP/ISM AL-adayı](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_MACRO_EVENT_COSTED_REPLAY_20261014.md) (Jan5→Jan13 tarih penceresi ve fiyat ölçütü **bu V1 Jan3→Feb1 ZigZag ile aynı değil**).

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_002

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_002). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-02-01 → 2023-02-24 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-7.147%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_002` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2023-02-14 13:30 UTC**: ilk M15 **0.063%**, 60dk **-0.600%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2023-02-01 19:00 UTC**: ilk M15 **-0.013%**, 60dk **0.793%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2023-02-03 13:30 UTC**: ilk M15 **-1.349%**, 60dk **-1.731%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-02-03** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2023-02-03/gold-price-drops-nearly-50-us-service-sector-grows-january-market-still). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2023-03-07** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-february-2023). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **-10.24%**, platin **-6.65%**, paladyum **-11.84%**, S&P 500 **-3.62%**, Nasdaq-100 **-3.18%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Gold, white metals and shares ↓; do not claim one NFP covers entire February leg. Retrospektif ek olgu: Şubat WGC: ayda altın -%5.2; USD/faiz artışı; ETF çıkışları; CFTC yayını gecikmeli..

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. **Belirli bağımsız makro alt-vaka hesabı:** [1–24 Şubat NFP SAT-adayı](independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_NFP_DOWN_EVENT_CASE_20261014.md); başlangıç şartlı $100 GOLD, yeni giriş araştırması değil.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_003

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_003). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-02-24 → 2023-05-04 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+13.200%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_003` / ilişki `;ÇOKLU_TETİKLEYİCİ; YALNIZ_MART_BÖLÜMÜ`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2023-03-14 12:30 UTC**: ilk M15 **0.179%**, 60dk **0.072%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `CPI` **2023-04-12 12:30 UTC**: ilk M15 **0.733%**, 60dk **0.520%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2023-03-22 18:00 UTC**: ilk M15 **0.360%**, 60dk **1.257%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2023-05-03 18:00 UTC**: ilk M15 **0.093%**, 60dk **-0.037%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2023-03-10 13:30 UTC**: ilk M15 **0.540%**, 60dk **0.841%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2023-04-07 12:30 UTC**: ilk M15 **eksik**, 60dk **eksik**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-03-13** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.moneycontrol.com/news/business/gold-silver-soar-as-svb-collapse-spurs-flight-to-safety-10244241.html). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2023-04-06** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-march-2023). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **21.5%**, platin **11.6%**, paladyum **-0.76%**, S&P 500 **2.3%**, Nasdaq-100 **8.46%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Leg also spans April and May: SVB cannot be sole explanation for whole return. Retrospektif ek olgu: Mart WGC: SVB banka stresi; altın ETF +32t; altın Mart +%8.5; 10Y faiz Q1'de -40bp..

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_004

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_004). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-05-04 → 2023-06-28 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-6.960%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_004` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2023-05-10 12:30 UTC**: ilk M15 **0.784%**, 60dk **0.182%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `CPI` **2023-06-13 12:30 UTC**: ilk M15 **0.093%**, 60dk **0.007%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2023-06-14 18:00 UTC**: ilk M15 **-0.372%**, 60dk **-0.180%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2023-05-05 12:30 UTC**: ilk M15 **-1.257%**, 60dk **-1.273%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2023-06-02 12:30 UTC**: ilk M15 **-0.332%**, 60dk **-0.141%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-05-05** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/opinion/2023-05-05/robust-us-jobs-report-delays-gold-breakout). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2023-06-07** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-may-2023). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **-11.77%**, platin **-12.87%**, paladyum **-11.86%**, S&P 500 **7.77%**, Nasdaq-100 **15.27%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Equities ↑ while gold/metals ↓: gold opportunity-cost channel candidate. Retrospektif ek olgu: Mayıs WGC: altın ETF +19.3t fakat COMEX managed money net longs azalmış; USD/faiz baskısı ve ayrışan fon akışı..

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_005

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_005). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-06-28 → 2023-07-18 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+3.752%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_005` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2023-07-12 12:30 UTC**: ilk M15 **0.595%**, 60dk **0.822%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2023-07-07 12:30 UTC**: ilk M15 **-0.054%**, 60dk **0.003%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-08-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-july-2023). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **10.06%**, platin **7.99%**, paladyum **3.25%**, S&P 500 **4.07%**, Nasdaq-100 **5.86%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: ETF holdings still declined: do not attribute all rally to ETF inflows. Retrospektif ek olgu: Temmuz WGC: altın +%3.1 aylık, COMEX netlong +93t, ETF -32t, USD zayıf, breakeven enflasyon yukarı..

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_006

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_006). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-07-18 → 2023-10-05 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-8.021%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_006` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2023-08-10 12:30 UTC**: ilk M15 **-0.015%**, 60dk **-0.186%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `CPI` **2023-09-13 12:30 UTC**: ilk M15 **-0.058%**, 60dk **0.095%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2023-07-26 18:00 UTC**: ilk M15 **0.023%**, 60dk **0.390%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2023-09-20 18:00 UTC**: ilk M15 **-0.219%**, 60dk **-0.297%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2023-08-04 12:30 UTC**: ilk M15 **0.376%**, 60dk **0.482%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2023-09-01 12:30 UTC**: ilk M15 **0.122%**, 60dk **0.124%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-10-10** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-september-2023). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **-15.09%**, platin **-12.06%**, paladyum **-10.43%**, S&P 500 **-6.52%**, Nasdaq-100 **-7.06%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Price correction straddles August and September; monthly indicators are not daily first-prints. Retrospektif ek olgu: Eylül WGC: US 10Y +~50bp, DXY +%2.5, ETF -59t, COMEX managed netlong -70t; 27 Eylül verileri + Çin primi ve teknik kırılma..

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_007

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_007). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-10-05 → 2023-10-27 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+10.227%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_007` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2023-10-12 12:30 UTC**: ilk M15 **-0.309%**, 60dk **-0.421%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2023-10-06 12:30 UTC**: ilk M15 **-0.404%**, 60dk **0.226%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-10-09** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.business-standard.com/amp/markets/commodities/gold-rises-more-than-1-as-middle-east-conflict-spurs-safe-haven-demand-123100900602_1.html). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2023-10-31** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.cnbc.com/2023/10/31/gold-on-track-for-biggest-monthly-rise-in-11-on-safe-haven-flows.html). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2023-11-07** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-october-2023). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **3.149%**, NQ future **-3.975%**, ZN future **-0.743%**, GVZ değişimi **2.99 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_008

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_008). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-10-27 → 2023-11-10 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-3.388%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_008` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `FOMC` **2023-11-01 18:00 UTC**: ilk M15 **0.028%**, 60dk **-0.152%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2023-11-03 12:30 UTC**: ilk M15 **0.715%**, 60dk **-0.001%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-11-07** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-october-2023). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-9.288%**, NQ future **9.301%**, ZN future **0.969%**, GVZ değişimi **-3.73 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_009

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_009). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-11-10 → 2023-12-01 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+6.889%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_009` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2023-11-14 13:30 UTC**: ilk M15 **0.558%**, 60dk **0.719%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-11-28** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.fxempire.com/forecasts/article/gold-surges-dollar-declines-on-fed-officials-remark-geopolitical-unrest-1392051). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-01-10** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-december-2023). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-3.948%**, NQ future **2.742%**, ZN future **2.66%**, GVZ değişimi **3 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_010

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_010). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-12-01 → 2023-12-12 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-4.463%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_010` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2023-12-12 13:30 UTC**: ilk M15 **-0.263%**, 60dk **-0.344%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2023-12-08 13:30 UTC**: ilk M15 **-0.213%**, 60dk **-1.067%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-12-04** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://economictimes.indiatimes.com/markets/commodities/news/gold-retreats-from-record-peak-as-dollar-bounces-back/articleshow/105734711.cms). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2023-12-08** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://wealthinsights.metrobank.com.ph/reuters/precious-gold-slides-over-1-as-strong-us-jobs-data-cloud-rate-cut-bets). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-7.399%**, NQ future **2.122%**, ZN future **-0.113%**, GVZ değişimi **-4.14 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `FONLAMA_FİNANSAL_STRES` (**eski mekanizma etiketi**). **Olası aktarım:** Pozisyonun aşırı uzaması ve geri dönüşü. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_011

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_011). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-12-12 → 2023-12-27 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+4.965%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_011` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2023-12-12 13:30 UTC**: ilk M15 **-0.263%**, 60dk **-0.344%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2023-12-13 19:00 UTC**: ilk M15 **1.069%**, 60dk **1.581%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-12-13** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.investing.com/news/economy/fed-likely-to-hold-rates-steady-signal-couple-of-cuts-in-2024-3255540). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-01-10** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-december-2023). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **7.466%**, NQ future **4.594%**, ZN future **2.821%**, GVZ değişimi **4.14 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `ALTIN_FİZİKİ_RESERVE_TALEP` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_012

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_012). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-12-27 → 2024-02-14 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-4.113%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_012` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-01-11 13:30 UTC**: ilk M15 **-0.335%**, 60dk **-0.397%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `CPI` **2024-02-13 13:30 UTC**: ilk M15 **-0.886%**, 60dk **-1.396%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2024-01-31 19:00 UTC**: ilk M15 **-0.058%**, 60dk **-0.085%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2024-01-05 13:30 UTC**: ilk M15 **-0.263%**, 60dk **0.371%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2024-02-02 13:30 UTC**: ilk M15 **-0.674%**, 60dk **-1.094%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-02-14** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.spglobal.com/market-intelligence/en/news-insights/articles/2024/2/gold-price-ends-streak-trading-above-2-000-oz-mark-after-61-days-80444427). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-03-07** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-february-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **3.765%**, NQ future **4.396%**, ZN future **-2.95%**, GVZ değişimi **-4.94 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_013

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_013). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-02-14 → 2024-04-19 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+19.984%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_013` / ilişki `;BİRİKİMLİ_ÇOK_MEKA`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-03-12 12:30 UTC**: ilk M15 **0.431%**, 60dk **-0.260%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `CPI` **2024-04-10 12:30 UTC**: ilk M15 **-0.486%**, 60dk **-1.006%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2024-03-20 18:00 UTC**: ilk M15 **0.481%**, 60dk **1.130%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2024-03-08 13:30 UTC**: ilk M15 **0.733%**, 60dk **0.219%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2024-04-05 12:30 UTC**: ilk M15 **-0.297%**, 60dk **-0.024%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-03-12** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/gold-focus/2024/03/you-asked-we-answered-whats-behind-golds-march-rally). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-04-09** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-march-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-05-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-april-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **27.87%**, platin **6.81%**, paladyum **16.23%**, S&P 500 **-0.67%**, Nasdaq-100 **-4.32%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Gold +19.989% NY17 leg despite equities ↓: not ordinary equity risk-on; RSI overbought alone insufficient. Retrospektif ek olgu: WGC 12 Mart: 1 Mart zayıf ISM→USD/faiz gerilemesi; 11 Mart altın Mart içi +%6.5; opsiyon, COMEX, OTC ve Çin talebi ilave kanallar..

**Aday ekonomik sınıf:** `ALTIN_FİZİKİ_RESERVE_TALEP` (**eski mekanizma etiketi**). **Olası aktarım:** Merkez bankası, fiziki altın ve EFP kanalı. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_014

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_014). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-04-19 → 2024-04-30 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-4.379%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_014` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-04-22** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2024-04-22/gold-drops-more-2-one-week-low-middle-east-worries-ebb). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-05-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-april-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **-5.61%**, platin **-0.21%**, paladyum **-6.29%**, S&P 500 **1.38%**, Nasdaq-100 **2.37%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Other metals ↓ while equities ↑: differentiation vs general liquidation. Retrospektif ek olgu: Nisan WGC: altın aylık +%4; ay zirvesi sonrası Çin fiziki primleri düşmüş; COMEX pozisyonu düzleşmiş; GRAM'de açıklanamayan güç var..

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_015

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_015). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-04-30 → 2024-05-20 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+6.141%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_015` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-05-15 12:30 UTC**: ilk M15 **0.606%**, 60dk **0.240%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2024-05-01 18:00 UTC**: ilk M15 **0.150%**, 60dk **1.087%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2024-05-03 12:30 UTC**: ilk M15 **0.300%**, 60dk **0.208%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-06-06** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-may-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **19.28%**, platin **15.23%**, paladyum **6.93%**, S&P 500 **5.41%**, Nasdaq-100 **7.07%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Gold leg +6.003%, but month-end GRAM residual large; no sole factor. Retrospektif ek olgu: Mayıs WGC: altın +%2; ETF +529 milyon USD; COMEX managed netlong 4 yılın zirvesi; OTC/merkez bankası GRAM rezidü adayı..

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_016

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_016). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-05-20 → 2024-06-07 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-5.459%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_016` / ilişki `;GEÇ_ALT_OLAY_AYRI`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `NFP` **2024-06-07 12:30 UTC**: ilk M15 **-0.612%**, 60dk **-0.366%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-05-23** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2024-05-23/gold-falls-one-week-low-hawkish-fed-minutes). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-05-23** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2024-05-23/gold-prices-drop-us-flash-pmi-shows-improvement-manufacturing-services). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-06-07** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2024-06-07/chinas-shock-pause-gold-purchases-overshadows-jobs-report-triggers-algo). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **-4.81%**, platin **-7.95%**, paladyum **-10.01%**, S&P 500 **0.73%**, Nasdaq-100 **1.75%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: NFP and PBoC June 7 are endpoint releases, not known since May 20. Retrospektif ek olgu: Reuters 23 Mayıs: Fed tutanakları daha uzun süre yüksek faiz, zirveden ~-%3.6; NFP/PBoC 7 Haziran son gün gelişmesidir..

**Aday ekonomik sınıf:** `ALTIN_FİZİKİ_RESERVE_TALEP` (**eski mekanizma etiketi**). **Olası aktarım:** Merkez bankası, fiziki altın ve EFP kanalı. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_017

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_017). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-06-07 → 2024-07-16 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+7.633%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_017` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-06-12 12:30 UTC**: ilk M15 **0.610%**, 60dk **1.081%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `CPI` **2024-07-11 12:30 UTC**: ilk M15 **1.151%**, 60dk **1.177%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2024-06-12 18:00 UTC**: ilk M15 **-0.402%**, 60dk **-0.537%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2024-06-07 12:30 UTC**: ilk M15 **-0.612%**, 60dk **-0.366%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2024-07-05 12:30 UTC**: ilk M15 **0.268%**, 60dk **0.329%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-07-11** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.fxstreet.com/news/gold-rises-as-powell-steers-middle-way-while-market-still-price-rate-cuts-202407110754). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-08-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-july-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **1.98%**, platin **-0.7%**, paladyum **3.16%**, S&P 500 **5.99%**, Nasdaq-100 **7.36%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Pt -0.70% while silver +1.98%; no unanimous metal rally. Retrospektif ek olgu: Temmuz WGC: altın aylık +%4.1; 10Y faiz düşüşü ve USD zayıflığı; COMEX netlong/OI oranı aleyhte..

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_018

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_018). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-07-16 → 2024-07-25 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-4.222%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_018` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-08-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-july-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **-9.31%**, platin **-4.55%**, paladyum **-2.85%**, S&P 500 **-4.73%**, Nasdaq-100 **-7.69%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Nasdaq ↓ materially; multiple possible sources, event-specific ex ante cause unresolved. Retrospektif ek olgu: Temmuz WGC ayı +%4.1 fakat 16–25 Temmuz zirve-sonrası altın düzeltmesi; tek günlük tetikleyici bağımsız doğrulanmadı..

**Aday ekonomik sınıf:** `FONLAMA_FİNANSAL_STRES` (**eski mekanizma etiketi**). **Olası aktarım:** Teminat, zorunlu satış, likidite ve kaldıraç. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_019

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_019). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-07-25 → 2024-10-30 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+17.886%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_019` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-08-14 12:30 UTC**: ilk M15 **-0.051%**, 60dk **-0.848%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `CPI` **2024-09-11 12:30 UTC**: ilk M15 **-0.614%**, 60dk **-0.488%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `CPI` **2024-10-10 12:30 UTC**: ilk M15 **0.293%**, 60dk **0.162%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2024-07-31 18:00 UTC**: ilk M15 **-0.160%**, 60dk **0.311%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2024-09-18 18:00 UTC**: ilk M15 **0.812%**, 60dk **0.310%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2024-08-02 12:30 UTC**: ilk M15 **0.585%**, 60dk **0.389%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- Aynı fiyat penceresinde ayrıca **2** makro release kaydı var; tam zaman tablosu kaynak CSV'de.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-09-13** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.thejakartapost.com/business/2024/09/13/dollar-droops-gold-at-record-high-as-bets-for-big-fed-cut-ramp-up). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-09-19** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2024-09-19/gold-gains-over-1-fed-begins-deeper-rate-cut-cycle). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-10-21** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://itiger.com/news/2477042591). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-10-08** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-september-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-11.844%**, NQ future **7.961%**, ZN future **-0.423%**, GVZ değişimi **3.14 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `ALTIN_FİZİKİ_RESERVE_TALEP` (**eski mekanizma etiketi**). **Olası aktarım:** ETF/CTA/OTC/metal akışı ve çokgünlü talep. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_020

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_020). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-10-30 → 2024-11-15 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-8.048%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_020` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-11-13 13:30 UTC**: ilk M15 **0.017%**, 60dk **0.167%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2024-11-07 19:00 UTC**: ilk M15 **-0.097%**, 60dk **-0.044%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2024-11-01 12:30 UTC**: ilk M15 **0.180%**, 60dk **0.098%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-11-12** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-october-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-3.011%**, NQ future **-0.074%**, ZN future **-0.92%**, GVZ değişimi **-1.51 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_021

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_021). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-11-15 → 2024-11-22 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+5.974%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_021` / ilişki `;BİRİNCİL_ADAY_JEOPOLİTİK`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-11-19** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2024-11-19/gold-hits-1-week-high-russia-ukraine-tensions-boost-rush-safety). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **6.255%**, NQ future **1.735%**, ZN future **0.157%**, GVZ değişimi **0.37 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_022

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_022). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-11-22 → 2024-11-25 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-3.360%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_022` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-11-25** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.marketpulse.com/markets/golds-xauusd-sharp-drop-ceasefire-optimism-and-bessents-impact-on-markets/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-2.95%**, NQ future **0.148%**, ZN future **0.855%**, GVZ değişimi **0.26 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_023

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_023). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-11-25 → 2024-12-11 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+3.548%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_023` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-12-11 13:30 UTC**: ilk M15 **0.196%**, 60dk **0.205%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2024-12-06 13:30 UTC**: ilk M15 **0.019%**, 60dk **-0.211%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-12-09** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2024-12-09/chinas-central-bank-resumes-gold-purchases-after-six-month-hiatus). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-12-09** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://mining.com/?p=1167582). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **1.781%**, NQ future **4.377%**, ZN future **0.254%**, GVZ değişimi **-0.94 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** Merkez bankası, fiziki altın ve EFP kanalı. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_024

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_024). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-12-11 → 2024-12-18 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-4.898%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_024` / ilişki `;BÖLÜMSEL_FED_ETKİ`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-12-11 13:30 UTC**: ilk M15 **0.196%**, 60dk **0.205%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2024-12-18 19:00 UTC**: ilk M15 **-0.760%**, 60dk **-1.223%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-01-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-december-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-0.412%**, NQ future **-2.657%**, ZN future **-1.579%**, GVZ değişimi **-0.32 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `ALTIN_FİZİKİ_RESERVE_TALEP` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_025

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_025). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-12-18 → 2025-02-24 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+14.243%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_025` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `FOMC` **2024-12-18 19:00 UTC**: ilk M15 **-0.760%**, 60dk **-1.223%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `CPI` **2025-01-15 13:30 UTC**: ilk M15 **0.113%**, 60dk **0.212%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `CPI` **2025-02-12 13:30 UTC**: ilk M15 **-0.199%**, 60dk **0.643%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2025-01-10 13:30 UTC**: ilk M15 **-0.064%**, 60dk **0.434%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2025-02-07 13:30 UTC**: ilk M15 **-0.033%**, 60dk **0.333%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-02-06** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2025-02-06/gold-flows-new-york-vaults-could-be-costly-and-unnecessary-says-naxitis). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-03-06** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-february-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **1.085%**, NQ future **0.982%**, ZN future **0.716%**, GVZ değişimi **0.19 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** Merkez bankası, fiziki altın ve EFP kanalı. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_026

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_026). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-02-24 → 2025-02-28 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-3.239%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_026` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-02-25** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.xtb.com/en/market-analysis/gold-dips-1-5). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-03-06** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-february-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-1.017%**, NQ future **-2.34%**, ZN future **1.238%**, GVZ değişimi **-0.91 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** Pozisyonun aşırı uzaması ve geri dönüşü. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_027

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_027). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-02-28 → 2025-04-02 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+9.640%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_027` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2025-03-12 12:30 UTC**: ilk M15 **0.156%**, 60dk **-0.122%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2025-03-07 13:30 UTC**: ilk M15 **0.356%**, 60dk **0.150%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-03-14** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.axios.com/2025/03/14/gold-all-time-high-3000). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-04-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-march-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **0.956%**, NQ future **-8.449%**, ZN future **0.66%**, GVZ değişimi **2.1 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** ABD politika güvenilirliği ve dolar güveni hipotezi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_028

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_028). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-04-02 → 2025-04-07 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-4.777%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_028` / ilişki `;BİRİNCİL_ADAY_LİKİDİTE`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `NFP` **2025-04-04 12:30 UTC**: ilk M15 **-0.261%**, 60dk **-0.688%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-04-07** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.reuters.com/markets/commodities/commodities-oil-drops-four-year-low-metals-fall-recession-fears-2025-04-07/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-04-07** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/gold-focus/2025/04/weekly-markets-monitor-tariffs-spare-no-land). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-17.673%**, NQ future **-10.026%**, ZN future **-0.544%**, GVZ değişimi **5.81 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** Teminat, zorunlu satış, likidite ve kaldıraç. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_029

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_029). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-04-07 → 2025-04-21 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+14.779%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_029` / ilişki `;ÇOKLU_AŞAMA`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2025-04-10 12:30 UTC**: ilk M15 **-0.048%**, 60dk **0.213%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-04-14** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/gold-focus/2025/04/weekly-markets-monitor-gold-above-us3200oz). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-04-21** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/gold-focus/2025/04/weekly-markets-monitor-easter-gold-surge). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **8.844%**, NQ future **3.958%**, ZN future **-0.533%**, GVZ değişimi **4.41 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** ABD politika güvenilirliği ve dolar güveni hipotezi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_030

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_030). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-04-21 → 2025-05-01 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-5.411%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_030` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-04-23** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-04-23/gold-falls-3-trump-comments-fed-and-china-boost-risk-sentiment). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-05-01** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.business-standard.com/world-news/gold-hits-2-week-low-as-trade-optimism-china-holiday-weigh-on-prices-125050100904_1.html). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-6.942%**, NQ future **10.522%**, ZN future **1.058%**, GVZ değişimi **-6.63 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** ABD politika güvenilirliği ve dolar güveni hipotezi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_031

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_031). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-05-01 → 2025-05-06 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+5.948%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_031` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `NFP` **2025-05-02 12:30 UTC**: ilk M15 **-0.103%**, 60dk **-0.061%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-05-06** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.mining.com/gold-price-rallies-to-two-week-high-as-china-resumes-trading/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **2.8%**, platin **1.55%**, paladyum **0.85%**, S&P 500 **0.05%**, Nasdaq-100 **0.02%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: US equities nearly flat on date-to-date; no broad flight-to-quality inference. Retrospektif ek olgu: Mayıs WGC: ay altın -%0.7; ETF -19t; managed money netlong +4t; tarife/enflasyon beklentisi yükselişi desteklerken momentum ve ETF aleyhte..

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** Merkez bankası, fiziki altın ve EFP kanalı. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_032

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_032). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-05-06 → 2025-05-14 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-7.411%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_032` / ilişki `;12_MAYIS_BAŞLATAMAZ`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2025-05-13 12:30 UTC**: ilk M15 **0.208%**, 60dk **0.120%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-05-12** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-05-12/gold-slides-3-us-china-agree-slash-reciprocal-tariffs). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **-0.42%**, platin **1.94%**, paladyum **0.73%**, S&P 500 **5.09%**, Nasdaq-100 **7.72%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: S&P/Nasdaq ↑ yet gold leg ↓, industrial metals ↑; safe-haven unwind plausible, opposite equity-riskoff. Retrospektif ek olgu: 12 Mayıs Reuters: ABD–Çin 90 gün süreyle tarifeleri azaltıyor; spot altın ~-%3, hisse/USD ↑, güvenli liman talebi azalıyor..

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_033

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_033). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-05-14 → 2025-06-13 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+8.030%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_033` / ilişki `;SON_GÜN_ALT_TETİKLEYİCİ`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2025-06-11 12:30 UTC**: ilk M15 **0.424%**, 60dk **-0.073%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2025-06-06 12:30 UTC**: ilk M15 **-0.172%**, 60dk **-0.152%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-05-21** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-05-21/weaker-dollar-geopolitical-uncertainty-push-gold-one-week-high). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-05-21** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.mnimarkets.com/articles/bullion-finds-support-from-middle-east-concerns-1747802659597). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-06-13** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.reuters.com/world/china/gold-tops-1-month-high-middle-east-tensions-spur-safe-haven-demand-2025-06-13/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **9.7%**, platin **27.63%**, paladyum **10.3%**, S&P 500 **1.43%**, Nasdaq-100 **1.46%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Precious metals ↑ sharply, including platinum; June 13 shock not known May 14. Retrospektif ek olgu: 13 Haziran İsrail–İran askeri çatışması güvenli liman alımına neden adayı, ancak 14 Mayıs'tan başlayan bacağın önceki bölümünü açıklamaz..

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** ABD politika güvenilirliği ve dolar güveni hipotezi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_034

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_034). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-06-13 → 2025-06-27 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-4.611%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_034` / ilişki `;GEÇ_ATEŞKES_AYRI`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-06-24** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.reuters.com/world/india/gold-near-2-week-low-after-trump-announces-israel-iran-ceasefire-2025-06-24/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **-0.26%**, platin **7.22%**, paladyum **6.7%**, S&P 500 **3.28%**, Nasdaq-100 **4.18%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Pt/Pd and equities ↑ as gold falls: gold haven-premium unwind plausible, not global metal selloff. Retrospektif ek olgu: 24 Haziran Reuters: İsrail–İran ateşkesi, altın gün içinde ~-%0.9 ve hisse ↑/petrol ↓; jeopolitik prim çözülmesi..

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_035

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_035). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-06-27 → 2025-07-22 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+4.795%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_035` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2025-07-15 12:30 UTC**: ilk M15 **-0.089%**, 60dk **-0.407%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2025-07-03 12:30 UTC**: ilk M15 **-1.131%**, 60dk **-0.525%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-07-16** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2025-07-16/gold-price-pops-backs-powell-firing-rumor). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-08-07** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-july-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **7.95%**, platin **5.85%**, paladyum **11.58%**, S&P 500 **2.21%**, Nasdaq-100 **2.35%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: All metals/equities ↑; broad asset inflation/risk regime; original trigger not proven. Retrospektif ek olgu: Temmuz WGC: ay altın +%0.3; ETF +23t, managed-money netlong ↑, USD güçlenmesi düşürücü..

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** ABD politika güvenilirliği ve dolar güveni hipotezi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_036

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_036). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-07-22 → 2025-07-30 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-4.545%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_036` / ilişki `;GEÇ_FED_ALT_OLAY`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-07-28** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-07-28/gold-falls-1-us-eu-deal-boosts-risk-appetite-ahead-fed-meeting). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-08-07** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-july-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Gümüş **-2.37%**, platin **-4.08%**, paladyum **-0.48%**, S&P 500 **0.84%**, Nasdaq-100 **1.22%**. `5/5`; **günlük baş–son, aynı UTC değil, ilk yayın PIT değil**. [38 kaynak ve karşıt kanıt dosyası](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). Karşıt kanıt: Metals ↓ while equities ↑; gold/metal-specific policy/rates more plausible than broad stock crisis. Retrospektif ek olgu: Temmuz WGC: altın aylık +%0.3, ETF +23t ve COMEX uzunlar ↑; daha güçlü dolar kısa düşüşle uyumlu fakat genel fon satışı kanıtlanmadı..

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). [Ayrıntılı 38-vaka bağlantısı](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md).


### SWING_V1_037

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_037). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-07-30 → 2025-10-20 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+32.998%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_037` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2025-08-12 12:30 UTC**: ilk M15 **0.292%**, 60dk **0.231%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `CPI` **2025-09-11 12:30 UTC**: ilk M15 **0.372%**, 60dk **-0.062%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2025-08-01 12:30 UTC**: ilk M15 **1.130%**, 60dk **1.508%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2025-09-05 12:30 UTC**: ilk M15 **0.807%**, 60dk **0.679%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-08-26** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-08-26/gold-hits-two-week-peak-after-trump-says-he-firing-fed-governor). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-09-23** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.mining.com/?p=1188819). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-10-17** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-10-17/bank-stocks-tumble-us-lender-jitters-gold-hits-fresh-peak). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-09-04** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-august-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-10-07** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-september-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-18.35%**, NQ future **7.037%**, ZN future **2.336%**, GVZ değişimi **14.95 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** ETF/CTA/OTC/metal akışı ve çokgünlü talep. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_038

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_038). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-10-20 → 2025-10-29 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-9.785%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_038` / ilişki `;METAL_ODAKLI_DÜZELTME_ADAYI`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2025-10-24 12:30 UTC**: ilk M15 **0.531%**, 60dk **1.289%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-10-13** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.gold.org/goldhub/gold-focus/2025/10/gold-hits-us4000oz-trend-or-turning-point). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-10-22** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://origin01-en.protothema.gr/2025/10/22/gold-crash-what-caused-the-biggest-correction-in-12-years-what-analysts-see-for-gold). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-10-22** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.montinvest.com/investor-insights/insights/golds-glitter-fades-biggest-one-day-drop-since-2013). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **5.192%**, NQ future **0.992%**, ZN future **-0.688%**, GVZ değişimi **-10 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** Pozisyonun aşırı uzaması ve geri dönüşü. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_039

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_039). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-10-29 → 2025-11-12 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+6.755%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_039` / ilişki `;BAŞLANGIÇ_FED_TERS_İŞARET`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-11-12** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.fxstreet.com/news/gold-tests-4-200-amid-weak-dollar-and-yields-ahead-of-us-shutdown-vote-202511122007). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-11-06** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-october-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-3.196%**, NQ future **0.185%**, ZN future **0.166%**, GVZ değişimi **4.39 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_040

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_040). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-11-12 → 2025-11-17 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-3.582%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_040` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-11-14** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-11-14/gold-slips-over-3-hawkish-fed-comments-spark-market-sell). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **2.224%**, NQ future **-2.876%**, ZN future **-0.332%**, GVZ değişimi **-1.75 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `ALTIN_FİZİKİ_RESERVE_TALEP` (**eski mekanizma etiketi**). **Olası aktarım:** Teminat, zorunlu satış, likidite ve kaldıraç. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_041

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_041). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-11-17 → 2025-12-26 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **+12.077%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_041` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `NFP` **2025-11-20 13:30 UTC**: ilk M15 **-0.137%**, 60dk **-0.134%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2025-12-16 13:30 UTC**: ilk M15 **0.060%**, 60dk **0.559%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-11-25** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://profit.pakistantoday.com.pk/2025/11/25/gold-hits-one-week-high-as-fed-remarks-renew-rate-cut-bets/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-12-22** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://seekingalpha.com/news/4534430-gold-silver-rise-to-record-highs-amid-rising-u-s-venezuela-tensions). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-12-05** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2025/12). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **-4.77%**, NQ future **3.932%**, ZN future **-0.042%**, GVZ değişimi **1.71 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** ETF/CTA/OTC/metal akışı ve çokgünlü talep. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### SWING_V1_042

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#swing_v1_042). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-12-26 → 2025-12-31 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **-4.730%** · V1: NY17 kapanışlı uzun fiyat bacağı, İŞARETLİ getiri. **Örtüşme:** `SWING_V1_042` / ilişki `V1_SELF_OR_NOT_SPECIFIED`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-12-29** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://apnews.com/article/c49577dedd4c799005de5b7af552ce81). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-12-31** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://news.bloombergtax.com/securities-law/cme-hikes-precious-metal-margins-again-after-wild-price-swings). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2026-01-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-december-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Eski 95 atlasında gün–tarihli çapraz piyasa satırı var (WTI CL **0.949%**, NQ future **-1.591%**, ZN future **-0.278%**, GVZ değişimi **-1.86 endeks puanı**). **Bu rakamlar eski fiyat sözleşmesinin tarihlerine aittir; düzeltilmiş 96 fiyat hareketinin aynı saatli kanıtı değildir**. Eski [95 veri matrisi](GOLD_HISTORICAL_95_PRICE_RECORDS_TRIGGER_REGIME_CROSSMARKET_ATLAS_V1_20261014.csv).

**Aday ekonomik sınıf:** `FONLAMA_FİNANSAL_STRES` (**eski mekanizma etiketi**). **Olası aktarım:** Pozisyonun aşırı uzaması ve geri dönüşü. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_001

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_001). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-01-12 → 2023-01-12 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.504%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_001` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2023-01-12 13:30 UTC**: ilk M15 **0.250%**, 60dk **0.257%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-01-06** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2023-01-06/gold-price-jumps-daily-highs-us-service-sector-contracts-december). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_002

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_002). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-02-03 → 2023-02-08 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|4.257%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_002` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `NFP` **2023-02-03 13:30 UTC**: ilk M15 **-1.349%**, 60dk **-1.731%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-02-03** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2023-02-03/gold-price-drops-nearly-50-us-service-sector-grows-january-market-still). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_003

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_003). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-03-13 → 2023-03-23 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|6.496%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_003` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2023-03-14 12:30 UTC**: ilk M15 **0.179%**, 60dk **0.072%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2023-03-22 18:00 UTC**: ilk M15 **0.360%**, 60dk **1.257%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-03-13** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.moneycontrol.com/news/business/gold-silver-soar-as-svb-collapse-spurs-flight-to-safety-10244241.html). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2023-04-06** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-march-2023). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_004

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_004). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-05-04 → 2023-05-04 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.430%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_004` / ilişki `PIVOT_DATE_AMBIGUOUS_COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-05-02** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2023-05-02/gold-price-jumps-above-2000-us-job-openings-drop-96-million). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2023-05-04** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2023-05-04/gold-price-soars-renewed-banking-fears-pacwest-western-alliance-stocks). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_005

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_005). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-09-29 → 2023-10-03 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|4.585%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_006` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-10-10** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-september-2023). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_006

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_006). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-10-13 → 2023-10-20 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|5.641%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_007` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;İLK_HABER_ÖNCEDEN`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-10-09** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.business-standard.com/amp/markets/commodities/gold-rises-more-than-1-as-middle-east-conflict-spurs-safe-haven-demand-123100900602_1.html). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2023-10-13** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/gold-focus/2023/10/you-asked-we-answered-whats-impact-of-geopolitics-on-gold). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_007

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_007). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-12-01 → 2023-12-01 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.567%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_010` / ilişki `PIVOT_DATE_AMBIGUOUS_COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-11-28** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.fxempire.com/forecasts/article/gold-surges-dollar-declines-on-fed-officials-remark-geopolitical-unrest-1392051). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_008

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_008). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-12-04 → 2023-12-04 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|3.054%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_010` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-12-04** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://economictimes.indiatimes.com/markets/commodities/news/gold-retreats-from-record-peak-as-dollar-bounces-back/articleshow/105734711.cms). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `İÇSEL_POZİSYON_DÖNÜŞÜ` (**eski mekanizma etiketi**). **Olası aktarım:** Pozisyonun aşırı uzaması ve geri dönüşü. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_009

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_009). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-12-08 → 2023-12-08 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|3.253%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_010` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `NFP` **2023-12-08 13:30 UTC**: ilk M15 **-0.213%**, 60dk **-1.067%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-12-08** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://wealthinsights.metrobank.com.ph/reuters/precious-gold-slides-over-1-as-strong-us-jobs-data-cloud-rate-cut-bets). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_010

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_010). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2023-12-19 → 2023-12-19 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.071%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_011` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2023-12-13** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.investing.com/news/economy/fed-likely-to-hold-rates-steady-signal-couple-of-cuts-in-2024-3255540). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_011

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_011). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-03-04 → 2024-03-11 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|5.669%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_013` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `NFP` **2024-03-08 13:30 UTC**: ilk M15 **0.733%**, 60dk **0.219%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-03-12** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/gold-focus/2024/03/you-asked-we-answered-whats-behind-golds-march-rally). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-04-09** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-march-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `ALTIN_FİZİKİ_RESERVE_TALEP` (**eski mekanizma etiketi**). **Olası aktarım:** Merkez bankası, fiziki altın ve EFP kanalı. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_012

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_012). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-04-01 → 2024-04-11 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|5.557%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_013` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-04-10 12:30 UTC**: ilk M15 **-0.486%**, 60dk **-1.006%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `NFP` **2024-04-05 12:30 UTC**: ilk M15 **-0.297%**, 60dk **-0.024%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-05-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-april-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `ALTIN_FİZİKİ_RESERVE_TALEP` (**eski mekanizma etiketi**). **Olası aktarım:** Merkez bankası, fiziki altın ve EFP kanalı. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_013

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_013). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-04-12 → 2024-04-12 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|3.620%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_013` / ilişki `COUNTER_TREND_AT_FIRST_FLAG;TETİKLEYİCİ_VE_TERSİ_AYRI`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-04-12** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.bloomberg.com/news/articles/2024-04-12/gold-hits-fresh-high-as-mideast-tensions-boost-haven-demand/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `İÇSEL_POZİSYON_DÖNÜŞÜ` (**eski mekanizma etiketi**). **Olası aktarım:** Pozisyonun aşırı uzaması ve geri dönüşü. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_014

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_014). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-04-24 → 2024-04-24 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|3.120%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_014` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-04-22** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2024-04-22/gold-drops-more-2-one-week-low-middle-east-worries-ebb). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_015

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_015). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-05-15 → 2024-05-20 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.828%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_015` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-05-15 12:30 UTC**: ilk M15 **0.606%**, 60dk **0.240%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-06-06** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-may-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_016

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_016). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-05-23 → 2024-05-27 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|4.011%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_016` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-05-23** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2024-05-23/gold-falls-one-week-low-hawkish-fed-minutes). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-05-23** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2024-05-23/gold-prices-drop-us-flash-pmi-shows-improvement-manufacturing-services). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_017

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_017). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-06-07 → 2024-06-07 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|3.592%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_017` / ilişki `PIVOT_DATE_AMBIGUOUS_COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP;İKİ_AYRI_HABER`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `NFP` **2024-06-07 12:30 UTC**: ilk M15 **-0.612%**, 60dk **-0.366%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-06-07** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2024-06-07/chinas-shock-pause-gold-purchases-overshadows-jobs-report-triggers-algo). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `ALTIN_FİZİKİ_RESERVE_TALEP` (**eski mekanizma etiketi**). **Olası aktarım:** Merkez bankası, fiziki altın ve EFP kanalı. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_018

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_018). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-06-13 → 2024-06-13 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|3.020%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_017` / ilişki `COUNTER_TREND_AT_FIRST_FLAG;YENİ_BEŞ_SEANS_BİRİKİM`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- Kayıtta kaynak URL yok / tarihi belirsiz. Haber yok varsayma.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** Baskın mekanizma bilinmiyor. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_019

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_019). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-07-16 → 2024-07-17 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|4.430%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_018` / ilişki `PIVOT_DATE_AMBIGUOUS_COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-07-11** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.fxstreet.com/news/gold-rises-as-powell-steers-middle-way-while-market-still-price-rate-cuts-202407110754). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-07-12** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.herobullion.com/precious-metals-market-news-12-july-2024/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_020

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_020). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-07-25 → 2024-07-25 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|3.293%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_019` / ilişki `PIVOT_DATE_AMBIGUOUS_COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-08-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-july-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** Teminat, zorunlu satış, likidite ve kaldıraç. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_021

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_021). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-08-01 → 2024-08-01 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.463%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_019` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-08-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-july-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_022

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_022). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-08-12 → 2024-08-16 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.765%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_019` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-08-14 12:30 UTC**: ilk M15 **-0.051%**, 60dk **-0.848%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-08-16** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://investing.com/news/commodities-news/gold-prices-hit-record-high-as-rate-cut-bets-build-3614695). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `İÇSEL_POZİSYON_DÖNÜŞÜ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_023

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_023). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-09-13 → 2024-09-16 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.227%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_019` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-09-13** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.thejakartapost.com/business/2024/09/13/dollar-droops-gold-at-record-high-as-bets-for-big-fed-cut-ramp-up). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_024

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_024). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-09-24 → 2024-09-26 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.831%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_019` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-09-19** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2024-09-19/gold-gains-over-1-fed-begins-deeper-rate-cut-cycle). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `ALTIN_FİZİKİ_RESERVE_TALEP` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_025

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_025). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-10-22 → 2024-10-22 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.240%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_019` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-10-21** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://itiger.com/news/2477042591). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-10-21** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.dailymaverick.co.za/article/2024-10-21-gold-hovers-near-fresh-record-on-mideast-election-uncertainty.md). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_026

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_026). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-11-06 → 2024-11-15 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|5.321%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_020` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-11-13 13:30 UTC**: ilk M15 **0.017%**, 60dk **0.167%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.
- `FOMC` **2024-11-07 19:00 UTC**: ilk M15 **-0.097%**, 60dk **-0.044%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-11-12** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-october-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_027

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_027). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-11-20 → 2024-11-22 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|5.974%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_021` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;MULTI_LEG_OVERLAP;JEOPOLİTİK_ADAY`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-11-19** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2024-11-19/gold-hits-1-week-high-russia-ukraine-tensions-boost-rush-safety). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_028

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_028). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-11-25 → 2024-11-25 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|3.360%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_023` / ilişki `PIVOT_DATE_AMBIGUOUS_COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-11-25** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.marketpulse.com/markets/golds-xauusd-sharp-drop-ceasefire-optimism-and-bessents-impact-on-markets/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_029

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_029). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-12-11 → 2024-12-11 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.220%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_024` / ilişki `PIVOT_DATE_AMBIGUOUS_COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2024-12-11 13:30 UTC**: ilk M15 **0.196%**, 60dk **0.205%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2024-12-09** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2024-12-09/chinas-central-bank-resumes-gold-purchases-after-six-month-hiatus). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2024-12-09** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://mining.com/?p=1167582). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** Merkez bankası, fiziki altın ve EFP kanalı. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_030

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_030). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2024-12-18 → 2024-12-19 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|4.898%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_025` / ilişki `PIVOT_DATE_AMBIGUOUS_COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP;MAKRO_SAAT_UYUMLU`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `FOMC` **2024-12-18 19:00 UTC**: ilk M15 **-0.760%**, 60dk **-1.223%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-01-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-december-2024). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_031

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_031). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-02-05 → 2025-02-10 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.888%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_025` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `NFP` **2025-02-07 13:30 UTC**: ilk M15 **-0.033%**, 60dk **0.333%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-02-06** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2025-02-06/gold-flows-new-york-vaults-could-be-costly-and-unnecessary-says-naxitis). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** Merkez bankası, fiziki altın ve EFP kanalı. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_032

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_032). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-03-13 → 2025-03-19 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|4.058%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_027` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-03-14** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.axios.com/2025/03/14/gold-all-time-high-3000). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-04-08** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-march-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** ABD politika güvenilirliği ve dolar güveni hipotezi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_033

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_033). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-03-31 → 2025-04-02 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.760%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_027` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-03-31** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.reuters.com/markets/commodities/gold-sails-above-3100-uncharted-territory-us-tariffs-approach-2025-03-31/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** ABD politika güvenilirliği ve dolar güveni hipotezi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_034

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_034). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-04-04 → 2025-04-08 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|4.777%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_028` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;MULTI_LEG_OVERLAP;ÖNCE_LİKİDİTE_SATISI`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `NFP` **2025-04-04 12:30 UTC**: ilk M15 **-0.261%**, 60dk **-0.688%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-04-07** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.reuters.com/markets/commodities/commodities-oil-drops-four-year-low-metals-fall-recession-fears-2025-04-07/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-04-07** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/gold-focus/2025/04/weekly-markets-monitor-tariffs-spare-no-land). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** Teminat, zorunlu satış, likidite ve kaldıraç. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_035

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_035). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-04-09 → 2025-04-22 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|8.515%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_029` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2025-04-10 12:30 UTC**: ilk M15 **-0.048%**, 60dk **0.213%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-04-14** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/gold-focus/2025/04/weekly-markets-monitor-gold-above-us3200oz). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-04-21** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/gold-focus/2025/04/weekly-markets-monitor-easter-gold-surge). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** ABD politika güvenilirliği ve dolar güveni hipotezi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_036

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_036). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-04-23 → 2025-04-23 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|3.035%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_030` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-04-23** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-04-23/gold-falls-3-trump-comments-fed-and-china-boost-risk-sentiment). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `ALTIN_FİZİKİ_RESERVE_TALEP` (**eski mekanizma etiketi**). **Olası aktarım:** ABD politika güvenilirliği ve dolar güveni hipotezi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_037

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_037). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-05-01 → 2025-05-01 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|3.295%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_031` / ilişki `PIVOT_DATE_AMBIGUOUS_COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-05-01** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.business-standard.com/world-news/gold-hits-2-week-low-as-trade-optimism-china-holiday-weigh-on-prices-125050100904_1.html). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_038

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_038). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-05-06 → 2025-05-07 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|5.948%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_032` / ilişki `PIVOT_DATE_AMBIGUOUS_COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-05-06** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.mining.com/gold-price-rallies-to-two-week-high-as-china-resumes-trading/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** Merkez bankası, fiziki altın ve EFP kanalı. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_039

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_039). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-05-09 → 2025-05-16 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|5.564%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_032` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;MULTI_LEG_OVERLAP;12_MAYIS_BAŞLATAMAZ`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2025-05-13 12:30 UTC**: ilk M15 **0.208%**, 60dk **0.120%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-05-12** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-05-12/gold-slides-3-us-china-agree-slash-reciprocal-tariffs). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_040

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_040). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-05-15 → 2025-05-15 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.143%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_033` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-05-15** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.fxstreet.com/news/gold-price-rebounds-above-3-200-as-us-ppi-and-retail-sales-miss-estimates-202505151446). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** Pozisyonun aşırı uzaması ve geri dönüşü. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_041

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_041). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-05-21 → 2025-05-26 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|4.825%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_033` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-05-21** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-05-21/weaker-dollar-geopolitical-uncertainty-push-gold-one-week-high). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-05-21** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.mnimarkets.com/articles/bullion-finds-support-from-middle-east-concerns-1747802659597). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** ABD politika güvenilirliği ve dolar güveni hipotezi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_042

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_042). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-06-13 → 2025-06-13 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.682%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_034` / ilişki `PIVOT_DATE_AMBIGUOUS_COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-06-13** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.reuters.com/world/china/gold-tops-1-month-high-middle-east-tensions-spur-safe-haven-demand-2025-06-13/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_043

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_043). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-07-22 → 2025-07-22 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.226%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_036` / ilişki `PIVOT_DATE_AMBIGUOUS_COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-07-16** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.kitco.com/news/article/2025-07-16/gold-price-pops-backs-powell-firing-rumor). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** ABD politika güvenilirliği ve dolar güveni hipotezi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_044

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_044). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-07-29 → 2025-07-30 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|3.304%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_036` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;MULTI_LEG_OVERLAP;30_TEMMUZ_BAŞLATAMAZ`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-07-28** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-07-28/gold-falls-1-us-eu-deal-boosts-risk-appetite-ahead-fed-meeting). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** Güvenli liman risk primi oluşması/çözülmesi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_045

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_045). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-08-07 → 2025-08-07 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.252%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_037` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;İLK_ESKİ_BAYRAK_DÜŞTÜ`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-09-04** *(fiyat penceresinden SONRA; karar girdisi olamaz)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-august-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_046

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_046). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-09-01 → 2025-09-08 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|4.757%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_037` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `NFP` **2025-09-05 12:30 UTC**: ilk M15 **0.807%**, 60dk **0.679%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-08-26** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-08-26/gold-hits-two-week-peak-after-trump-says-he-firing-fed-governor). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-09-04** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-august-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** ABD politika güvenilirliği ve dolar güveni hipotezi. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_047

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_047). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-09-23 → 2025-09-23 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.287%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_037` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-09-23** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.mining.com/?p=1188819). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `JEOPOLİTİK_GÜVENLİK` (**eski mekanizma etiketi**). **Olası aktarım:** ETF/CTA/OTC/metal akışı ve çokgünlü talep. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_048

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_048). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-10-01 → 2025-10-20 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|8.827%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_037` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-10-17** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-10-17/bank-stocks-tumble-us-lender-jitters-gold-hits-fresh-peak). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-10-07** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.gold.org/goldhub/research/gold-market-commentary-september-2025). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `TİCARET_TARİFE_POLİTİKASI` (**eski mekanizma etiketi**). **Olası aktarım:** ETF/CTA/OTC/metal akışı ve çokgünlü talep. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_049

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_049). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-10-17 → 2025-10-29 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|8.580%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_037` / ilişki `COUNTER_TREND_AT_FIRST_FLAG;MULTI_LEG_OVERLAP;KÜME_FİYAT_IŞARETİ_ÇOK_GÜNLÜ`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- `CPI` **2025-10-24 12:30 UTC**: ilk M15 **0.531%**, 60dk **1.289%**. Resmî makro schedule/vintage ledger, aynı tarihli tepki; olayın tümüne sebep diye yorumlama.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-10-13** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://www.gold.org/goldhub/gold-focus/2025/10/gold-hits-us4000oz-trend-or-turning-point). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-10-22** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://origin01-en.protothema.gr/2025/10/22/gold-crash-what-caused-the-biggest-correction-in-12-years-what-analysts-see-for-gold). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `İÇSEL_POZİSYON_DÖNÜŞÜ` (**eski mekanizma etiketi**). **Olası aktarım:** Pozisyonun aşırı uzaması ve geri dönüşü. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_050

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_050). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-11-10 → 2025-11-13 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|5.408%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_039` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;MULTI_LEG_OVERLAP;DÖNÜŞ_SONRASI_ALTIN_AYRIŞMASI`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-11-12** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.fxstreet.com/news/gold-tests-4-200-amid-weak-dollar-and-yields-ahead-of-us-shutdown-vote-202511122007). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `PRIORITY_CASE_SOURCE_TIMELINE_REVIEW_NOT_FULL_CAUSAL_IDENTIFICATION`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_051

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_051). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-11-14 → 2025-11-17 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|3.582%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_040` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-11-14** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.kitco.com/news/off-the-wire/2025-11-14/gold-slips-over-3-hawkish-fed-comments-spark-market-sell). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** Teminat, zorunlu satış, likidite ve kaldıraç. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_052

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_052). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-11-28 → 2025-11-28 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|3.797%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_041` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-11-25** *(pencere öncesi bağlam)*: [tarihli dış kaynak](https://profit.pakistantoday.com.pk/2025/11/25/gold-hits-one-week-high-as-fed-remarks-renew-rate-cut-bets/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `DİĞER_BİLEŞİK_EKONOMİK_BİLGİ` (**eski mekanizma etiketi**). **Olası aktarım:** Nominal/reel faiz–dolar–Fed patikası. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_053

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_053). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-12-22 → 2025-12-26 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **UP** · **|4.674%| (mutlak, yön UP)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_041` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG;MULTI_LEG_OVERLAP`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-12-22** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://seekingalpha.com/news/4534430-gold-silver-rise-to-record-highs-amid-rising-u-s-venezuela-tensions). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-12-22** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://www.reuters.com/world/india/gold-hits-record-high-fed-rate-cut-bets-silver-scales-fresh-peak-2025-12-22/). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `MAKRO_FAİZ_BEKLENTİSİ` (**eski mekanizma etiketi**). **Olası aktarım:** ETF/CTA/OTC/metal akışı ve çokgünlü talep. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 


### C_CORR_054

> **Bu olayın karar öğrenme değerlendirmesi (6 alan):** [karar öncesi XAU, haber, tahmin/eksik, kalan hareket, maliyetli alternatifler, benzer/ters olaylar](OLAY_02_96_VAKA_ALTI_KARAR_ALANI_20261014.md#c_corr_054). İlgili altın fiyatı, haber kaynakları ve tarihsel neden hipotezleri aşağıda korunmuştur.
**Fiyat kimliği ve zaman:** 2025-12-29 → 2025-12-31 (NY17 düzeltilmiş çalışma etiketi, ilk haber UTC'si değildir). **DOWN** · **|4.730%| (mutlak, yön DOWN)** · V2: 1/4/12 saat ve 1/3/5 seans tarama MAX MUTLAK genlik, pencere net getirisi DEĞİL. **Örtüşme:** `SWING_V1_042` / ilişki `SAME_DIRECTION_AT_FIRST_FLAG`; 42+54 bağımsız sayılmaz.

**Makro haber saatli pencereler (yalnız CPI/NFP/FOMC altkümesi):**
- Bu pencere içinde 85 olaylık **CPI/NFP/FOMC altkümesinde** eşleşen duyuru yok; haber olmadığı sonucuna varılmaz.

**Diğer tarihli haber/görüşler — yayımlanma saati nedensel teyit değildir:**
- **2025-12-29** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://apnews.com/article/c49577dedd4c799005de5b7af552ce81). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.
- **2025-12-31** *(fiyat penceresinin tarihi içinde; kesin ilk-saat bilinmiyor)*: [tarihli dış kaynak](https://news.bloombergtax.com/securities-law/cme-hikes-precious-metal-margins-again-after-wild-price-swings). Kaynaktaki anlatının özgün ilk yayımlanma UTC'si BAĞIMSIZ kanıtlanmadı.

**Piyasa veri bağlamı / farklılaştırıcı / karşıt kanıt:** Bu düzeltilmiş V2 kimliğine bire bir kaynak-vintage denetimli çapraz veri iliştirilmedi. Olayın `associated_V1` bağlantısı, V1 sonuçlarını doğrudan aynı V2 pencerenin oranıymış gibi taşıma izni vermez.

**Aday ekonomik sınıf:** `FONLAMA_FİNANSAL_STRES` (**eski mekanizma etiketi**). **Olası aktarım:** Pozisyonun aşırı uzaması ve geri dönüşü. Bu ikisi nedensel tanı değil. Altının fiyatı aynı yöne gitti diye haber öncesinde bilinebilen sinyal olduğu çıkarılamaz.

**As-of & karar uygunluğu:** İlk haberin fiyat bacağını **başlattığı UTC saati: DOĞRULANMADI**. İlk haberin özgün yayın anı ile pozisyon/likidite aktarım katkısı: **ölçülmedi**. Bu fiyat kaydına özel **saatli banka kârı, AL/SAT kararı veya geçerli sonraki 1m fill** bu katalogdan üretilemez. Vaka için böyle bir rapor varsa ayrıca bağlanmalı.

**Sicil kanıt seviyesi:** `DATED_SOURCE_CONTEXT_FIRSTPRINT_NOT_VERIFIED`; `first_original_news_UTC_verified_for_initiation=NO`; `causal_contribution_measured=NO`. **Eksik bilimsel kapı:** `FIRST_PRICE_ONSET_UTC;FIRST_NEWS_FIRSTPRINT_UTC;RELEASE_SAME_UTC_DXY_2Y_10Y_TIPS_XAG;QUIET_MACRO_CONTROLS;COT_ETF_AS_OF`. [Tarihi fiyat/hipotez orijinal satırları](GOLD_96_EVENT_SCIENTIFIC_CAUSE_EVIDENCE_REGISTER_20261014.csv). 
