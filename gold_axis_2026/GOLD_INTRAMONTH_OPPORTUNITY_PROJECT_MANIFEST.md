# GOLD INTRAMONTH — OLAY TEMELLİ ORTA/BÜYÜK UP–DOWN FIRSATLARI ANA MANİFESTİ

**Sürüm:** 2026-10-14 · **Kapsam düzeltmesi:** EVENT_DRIVEN_MEDIUM_LARGE_MOVE_OBJECTIVE_V2 · **Statü:** AMAÇ DÜZELTİLDİ / OCAK 2023 ASIL STRATEJİ HENÜZ TEKRAR ÇALIŞTIRILMADI / GERÇEK BANKA ONAYI YOK.

> **Bağlayıcı amaç:** Altın XAU/USD'de **orta ve büyük şiddetteki yükseliş (UP) ve düşüş (DOWN) olaylarını**, hareket henüz başlamadan **veya başladıktan sonra**, olayın ekonomik/piyasa mekanizmasını ve fiyat yolundaki işaretlerini yorumlayarak tespit etmek; ancak **alışta %0,8 + satışta %0,8, BID/ASK makası ve icra gecikmesini aşması beklenen** pozisyon değiştirme fırsatlarını seçmek. Sistem küçük günlük fiyat dalgalanmaları için mekanik AL/SAT yapan bir günlük momentum botu **değildir**. Bilgi yetersizse **ALTIN TUT / NAKİT TUT / BEKLE** meşru ve önemli kararlardır.

**Yatırım kararının iki yönü:** (i) Altın taşınırken anlamlı bir DOWN şoku/düzeltmesi başlamadan veya başladıktan sonra **altından nakde geçme ve uygun koşullarda yeniden girme**; (ii) nakitteyken, aylık görünüm DOWN olsa bile, anlamlı UP toparlanma/trend fırsatında **altına girme ve gerektiğinde çıkma**. Aylık altın tahmini durum değişkenidir, **otomatik veto veya günlük işlem zorunluluğu değildir**.

**Araştırma biçimi:** Önce ay ay **Ocak 2023, Şubat 2023, ...** ilerleyeceğiz. **Kip A/FULL_HISTORY_DISCOVERY** içinde 2024–2026 gibi sonraki olaylar, neden–sonuç hipotezlerini ve olay sınıflarını anlamada **kullanılabilir**; fakat o bilgiler 2023'te biliniyormuş gibi tarihsel emir oluşturulamaz ve geri-bakış sonucu kör başarı olarak sunulamaz. **Kip B/AS_OF_DECISION_EVALUATION**, sayısal yatırım kararlarını ileri bilgi kullanmadan sınama içindir. Yalnız **GPT** nitel değerlendirme desteği verebilir; ne tek başına kaynak ne de doğrulanmış sayısal tahmin sayılır.

**2023 Ocak kritik düzeltmesi:** Rapordaki `$100 → $101,9695` sonuç, geçmişte çalıştırılmış **5-seans-momentum V0** hesabıdır; **orta/büyük olay temelli ana stratejinin sonucu DEĞİLDİR**. İlgili hesap ve ücretler tarihsel karşılaştırma olarak korunur, ancak V0'nun başarısızlığı yalnız küçük momentum değişimlerini izleyen yaklaşımı ilgilendirir. Ocak 2023 araştırma ayı **olay-stratejisi bakımından AÇIK** tutulur; Şubat'a doğrulanmış yöntem devri yoktur.

**Yürürlük/ayrıntılı sözleşme:** [Orta/büyük olay odaklı yeniden başlangıç sözleşmesi](adaptive_volatility_learning/EVENT_DRIVEN_MEDIUM_LARGE_MOVE_RESTART_CONTRACT_20261014.md). 2026 Ocak B0–S4–V4 deneyleri tarihsel ilham/kısıt niteliğindedir; V4 2024'te 12 ilgili DOWN vakasına karşı **0 alarm** ürettiği için teyit edilmiş strateji olarak alınmaz.

## 1. Tam olarak hangi problemi çözüyoruz?

**İş sorusu:** "Altının mevcut hareketi, ufak gürültü mü yoksa **alım-satım maliyeti sonrası ekonomik değeri olabilecek** orta/büyük UP veya DOWN olayının başlangıcı/devamı/tersine dönüşü mü? Şu an altın mı nakit mi tutmak daha avantajlı; karar vermek için hangi kanıt yeterli?"

- **Birincil olay çıktısı:** `UP_MEDIUM/UP_LARGE/DOWN_MEDIUM/DOWN_LARGE/NONE/UNCERTAIN` olasılığı/güven aralığı ve **olay evresi** (`PRE_ONSET/CONFIRMED_ONSET/CONTINUATION/EXHAUSTION/REVERSAL`). Büyüklük ve yön **birlikte** değerlendirilir; yalnız oynaklık artışı SAT anlamına gelmez. Doğrulanmamış olasılık üretilmez.
- **İkinci ve kritik çıktı:** Pozisyon `GOLD/CASH` ve olası eylem `BUY/SELL/HOLD_GOLD/HOLD_CASH/WAIT`, fakat **yalnız maliyet+uygulanabilirlik+güven kapısı** geçildiyse. Bu araştırmada otomatik gerçek banka emri yoktur.
- **Hareket başladıktan sonra karar SERBEST:** Şoku önceden öngörmek tek yol değil; başlangıcı teyit edip kalan hareketin beklenen büyüklüğü, maliyet ve geri dönüş riskiyle değerlendirmek de hedeftir. Giriş ve çıkış zorunlu sabit gün veya sabit saat ile sınırlandırılmaz.
- **Saat hedef değil, izdir:** Piyasa haberinin `first_published_at`, verinin `available_at`, sinyal, karar ve teorik uygulanabilir BID/ASK zamanları kesin saklanır. NY17/günlük kapanış her olayda zorunlu karar saati değildir; gerçek banka zamanları işlemin mümkün olup olmadığını belirler.
- **Maliyet eşiği:** %0,8 AL + %0,8 SAT için teorik aynı fiyatlı tam döngü kâr başabaşı `1/(0.992^2)-1 ≈ %1,6194` **ve buna ek BID/ASK spread, gecikme, slippage, varsa kur/vergi maliyetleri** gerekir. Bu **fiyat hareketi hedefi değildir**; bir işlem fırsatının beklenen kalan kazancı ve riski için asgari ekonomik kontrolüdür. Örn. ≥%3 hareketler tarihsel atlas için aday **orta/büyük olay inceleme ailesidir**, bütün rejimlere dayatılmış otomatik AL/SAT eşiği değil.
- **Aylık stratejiyle ilişki:** Aylık UP'da normal koşul altın taşımak, anlamlı geçici DOWN'da korunmak; aylık DOWN'da normal koşul nakitte olmak, anlamlı geçici UP'da fırsatı değerlendirmek. Aylık yön güveni düşükse rejim de `UNCERTAIN` olabilir.
- **Başarı:** İlk ölçüt **net 100 USD portföy** ve eşdeğer masraflı **BUY/HOLD**, **CASH**, aylık durum-temelli pasif bazlara karşı fark; ayrıca yakalanan/kaçan orta-büyük hareket sayısı, yanlış alarm, geç tepki, drawdown, işlem devir hızı, pozisyon dışı kaçırılmış UP, maliyetler. Sadece toplam para kazanılması **üstünlük değildir**.
- **Bilimsel sınır:** Tüm yılları kullanarak olay mekanizmasını yorumlama (`FULL_HISTORY_DISCOVERY`) ile geçmişte gerçekte uygulanabilir karar kazanımı veya kör gelecek tahmini **ayrı iddialardır**. Kip A'da tanımlanan iyi olayı geriye dönük uygun dip/tepeden alıp satmak geçerli performans değildir.


## 2. İKİ ÇALIŞMA KİPİ — araştırmayı tarih sırası sınırlamasına hapsetme

**KİP A — `FULL_HISTORY_DISCOVERY` (ŞİMDİKİ ANA ÇALIŞMA):** 2023'ten başlayan yürüyüş yalnız **olay inceleme sırasıdır**. 2023 Mart olayını anlamak için 2024–2026'da yaşanan benzer krizler, sonuçları, sonradan yayımlanmış WGC/COT yorumları ve 2026'daki bilimsel değerlendirmeler **kullanılabilir**. Gelecek olay verileri geçmiş olayın **anlamını ve mekanizma adayını yeniden yorumlamayı** sağlar; hiç kimse 2023'te o veriyi biliyordu denmez. Olayların gerçekleşen sonraki fiyatı da vaka analizinde **sonuç etiketi** olarak görülebilir. Tarihler, olay kimliği ve gözlem zamanı olarak saklanır; kronolojik kesme emri değildir. **Bu kipte verilen risk/olay kararı, geçmişin tümüyle bilgilendirilmiş geriye dönük araştırma hükmüdür, o tarihte yapılmış tahmin değildir.**

**KİP B — `AS_OF_DECISION_EVALUATION` (DAHA SONRA AYRI SINAMA):** Algoritmanın/yapay zekânın o anda gerçekten ulaşılabilecek veriyle bir **öngörü** yapıp yapamadığını sınamak istediğimizde, hem olay örnekleri hem modelin eğitildiği bilgi hem de tetikleyici haber ve karar girdileri **karar anıyla uygun** sınırlandırılır. Önceden bütün 2023–2026 olaylarını görerek kurduğumuz bir mekanizmayı 2023'te blind keşfedilmiş diye tanıtamayız. Böylece Kip A'nın geniş öğrenmesini bozmadan, Kip B'nin bilimsel sınırını koruruz.

**Kayıt zorunluluğu:** Her incelemede `mode, case_id, event_date, evidence_available_at, decision_origin_if_any, future_outcome_visible, historical_scope, comparator_cases, ai_assessment_version, result_status` yazılır. `FULL_HISTORY_DISCOVERY` içinde `event_date` bilgi kesme noktası değildir; `AS_OF_DECISION_EVALUATION` içinde `decision_origin` ve bilgi penceresi kesin olmalıdır.

### 2.1 Kaynak ve saat doğruluğu iki kipte de korunur

Her değerlendirmede aşağıdaki alanlar çalışma kipine göre kaydedilir:

| Kayıt | Şart |
|---|---|
| **Kimlik ve zaman** | **Kip A:** `case_id/event_date` yeterli başlangıç kimliği; olay/haber içindeki farklı zamanlar ayrı kaydedilir. **Kip B:** kesin `origin_utc`, Türkiye/New York saati ve DST zorunlu |
| **Veri erişimi** | Kaynağın ölçüm `observed_at` zamanı ile gerçek `first_published_at / available_at` **ayrı** |
| **Veri tanımı** | Sağlayıcı, spot/futures, BID/ASK/MID, 1m/15m/1h/gün, kontrat devri, kapanış ve tatil |
| **Hedef** | Hangi başlangıç-bitiş fiyatı, ileri mutlak log-getiri, realized-vol, kuyruk olasılığı ve şok eşiği |
| **Olay havuzu** | **Kip A:** 2023–2026 ve erişilebilir bütün tarihsel dönemlerden benzer, ters, sonradan açıklanmış olaylar; **Kip B:** deneyde izin verilen karar anı öncesi eğitim/kanıt havuzu |
| **Karşı kanıt** | Rakip nedenler, uyumsuz veriler, benzer haber olup şok olmayan günler |
| **Çıktı** | Kanıtlı olay yönü (UP/DOWN), şiddet/evre, kalma/çıkma/girme fırsatı ve net maliyet kapısı + destekleyici volatilite/risk + belirsizlik/ABSTAIN + veri kalitesi |
| **Deney izi** | Sürüm, kaynak/vintage, önceden belirlenmiş kıyas, test dönemi ve sonradan gerçekleşen sonuç |

**Kaynak-vintage / as-of ayrımı:** **Kip A'da** gelecek yılın olayları ve geç yayımlanan veriler mekanizmayı araştırmak için **serbesttir**; ancak her bilginin **gerçekte ne zaman yayımlandığı** saklanır ki geçmiş olayın başlatıcısıyla sonradan gelen açıklama karıştırılmasın. **Kip B'de** `available_at <= origin_utc` zorunludur: yayımlanmamış CPI/NFP, kapanmamış GVZ/VIX, geç açıklanan ETF/COT veya sonradan revize seri tahmin girdisi olmaz. Her iki kipte de eksik veri `MISSING/UNKNOWN`; hiçbir kayıt uydurulmaz.

**COT özel kural:** Pozisyon salı ölçülür, normal kamu yayını cuma **15:30 America/New_York**; 2023 ION ve 2025 kapanma gecikmelerinde CFTC resmî istisna tarihleri kullanılır. **Kip A:** geç yayımlanan COT ve WGC aylık ETF değerleri **geriye dönük inceleme ve başka yıllarla kıyas için serbestçe görülebilir**, ancak yayın tarihleri kayıtlıdır. **Kip B:** rapor içeriği yalnız gerçek ilk yayımdan sonra karar girdisi olabilir. [CFTC yayımlanma saati](GOLD_COT_PUBLICATION_CLOCK_OFFICIAL_AUDIT_AND_RETROSPECTIVE_154_ORIGIN_RETEST_20261014.md). `d_opt_mm_net` ham opsiyon kontratı değil, normalize combined−futures pozisyon farkının değişimidir: [ham COT denetimi](GOLD_COT_RAW_LONG_SHORT_FALSIFICATION_2025_Q1_20261014.md).

**Olay kütüphanesinin bilimsel niteliği:** 2026'da yazılmış 2023–2025 mekanizma raporları **Kip A'da tam kullanılabilir**. Fakat hangi verinin gözlem, hangi ifadenin varsayım, hangi etiketin geriye dönük yorum olduğu korunur. İleride Kip B'ye geçersek, 2026'dan türetilmiş etiketi veya sonradan tanınan ZigZag dip/tepe noktalarını erken tarihli canlı özellik gibi aktaramayız. Aynı kayıt hem **tam-bilgili açıklama** hem **kilitli deney girdisi** olarak işaretlenemez.

## 3. İncelenecek bilgi türleri — hepsinin rolü farklı

| Faktör grubu | Neyi anlamak için? | Bilimsel sınır |
|---|---|---|
| **Altın XAU fiyat yolu**: gerçekleşmiş volatilite, yüksek/düşük, momentum, sıçrama, düşüş yarı-varyansı | Hareket başlamış mı, gücü azalıyor mu, risk ölçeği ne? | Gerçek zamanlı kapanmış bar, NY17, bar sonu; OHLC aynı bar high/low sırası bilinmez |
| **Gümüş, platin, paladyum** | Genel metal hareketi mi altına özgü gelişme mi? | Stak günlük fiyatı XAU 15m ile aynı UTC değildir; eşsaatli test gerekiyorsa yeni kaynak |
| **USD/DXY, ABD 2Y/10Y, mümkünse reel faiz/TIPS ve Fed beklentisi** | Faiz–dolar–iskonto/politika etkisi mi? | Sürpriz ve ilk-baskı; CME ZN **tahvil futures fiyatı**, tahvil faizi değildir |
| **NQ/S&P, VIX/GVZ, kredi/likidite** | Piyasa stresli mi, ortak tasfiye var mı? | VIX/GVZ çoğu kez risk göstergesi veya fiyat tepkisidir; otomatik ana neden olmaz |
| **WTI/Brent, jeopolitik risk, GPR** | Enerji/arz/enflasyon/savaş aktarımı var mı? | İlk haber saati, GPR açıklanma gecikmesi, eş-UTC petrol ve dolar reaksiyonu |
| **COT futures-only/combined, tüm trader grupları; açık pozisyon** | Büyük yatırımcılar risk türünü nasıl değiştiriyor? | Salı pozisyonu cuma bilinir; futures/opsiyon farkı, payda değişimi ve endojenlik |
| **ETF, merkez bankası, COMEX–Londra fiziki stok, EFP/basis, lease** | Fon girişi, altına özel arz, fiziki finansman sıkışması var mı? | Aylık WGC bilgisi günlük ilk basım değildir; fiyatla birlikte değişim nedensellik kanıtı değil |
| **Özgün resmî haberler** (CPI/PCE/NFP/ADP/JOLTS/FOMC, tarife, banka, savaş) | Yeni bilgi ne zaman geldi, önceki beklenti neydi? | İlk yayımlanma UTC, aynı anda başka şok, açıklama öncesi fiyat kontrolü |

**Kural:** Sabit sekiz değişkenli bir "kara kutu" kurma; hangi değişkenin neyi açıkladığı ayrı tutulur. Veri yoksa veya saat uyumsuzsa mekanizma **desteksiz/kararsız** kalır. "Daha fazla veri" geçmişi bilme hakkı vermez.

## 4. Geçmiş olaylardan nasıl yararlanılacak?

**Elimizdeki gerçek araştırma sermayesi:** 2023–2025'te **42 düzeltilmiş V1 uzun fiyat bacağı** ve **54 düzeltilmiş V2 kısa hareket kümesi** var. Bu **96 FİYAT KAYDI**, 96 bağımsız ekonomi haberi değildir; bacaklar/kümeler örtüşür. V1 dönüm noktaları retrospektiftir. 2023–25 araştırmasındaki haberler, 38 ayrıntılı vaka, dönemlik COT–ETF bulguları ve başarısız hipotezler **karşılaştırmalı araştırma malzemesidir**, doğrudan canlı öngörü kuralı değil.

Geçmişle kıyas için dört soru zorunludur:

1. **Ön koşul neydi?** O günün karar saatine kadar bilinen volatilite, altın/metaller, dolar/faiz, risk, COT/ETF, haber takvimi ve piyasa konumu.
2. **Yeni katalizör neydi?** Makro sonuç, Fed iletişimi, jeopolitik, tarife, likidite, COMEX/fiziki arz veya **hiç yeni haber yok**. **İlk haber UTC** ile fiyatın gerçek başlangıç zamanını ayrı kaydet.
3. **Aktarım doğrulandı mı?** USD/faiz, diğer metaller, hisse, petrol, pozisyon ve fiziki-premium kanalları **zaman-uyumlu** hareket ediyor mu? Beraber hareket tek başına nedensel etki demek değildir.
4. **Hangi rakip açıklama/karşı-vaka var?** Aynı açıklama olup altının hareket etmediği günleri, olay öncesinde başlayan fiyatı ve ters veri işaretlerini de incele.

**Kip A'da** geçmişten geleceğe **bütün olaylar arasında çift yönlü benzerlik** kurulabilir; 2023 olayı 2025 ve 2026 örneklerinden öğrenilerek yeniden sınıflanabilir. Olayın **gerçekleşen fiyat sonucu** da açıklama/keşif etiketidir; fakat aynı sonuç önce benzer vakayı seçmek, sonra o vakanın güya bağımsız öngörü gücünü ölçmek için kullanılmaz. **Kip B'de** benzerlik seçimi ve öğrenme tamamıyla origin-safe özelliklerle yapılır; gerçekleşen gelecek fiyatı yalnız sonraki test skoru olur. Her iki kipte de büyük hareket olan ve **olmayan** vakalar birlikte incelenir.

**Aday mekanizma aileleri (tek seçim zorunlu değil):** ABD makro/Fed–faiz–USD; finansman/likidite ve margin-call; jeopolitik güvenli liman; tarife/ticaret; ETF/merkez bankası/COT/fiziki-altın; aşırı momentum/pozisyon çözülmesi; mali/siyasi belirsizlik; **çok etkenli veya UNKNOWN**. Aynı olayda tetikleyici, güçlendirici ve fiyat tepkisi birbirinden ayrılır. 2025 ilk çeyrek fizikî COMEX–Londra arbitrajı ve 2025 Nisan likidite çöküşü **farklı ekonomi mekanizmalarıdır**.

**Araştırma dosyaları:**
- [96 düzeltilmiş fiyat kaydı ve olay zamanlaması](GOLD_HISTORICAL_V2_NY17_FULL_REPLAY_96_EVENT_CAUSAL_REVIEW_AUTHORITY_20261014.md) · [96 kanıt ve haber indeksi](GOLD_HISTORICAL_CORRECTED_96_RECORD_EVENT_NEWS_CAUSAL_EVIDENCE_INDEX_20261014.csv).
- [Geçmiş 95 kayıt için **geçici** mekanizma sınıflandırması](GOLD_HISTORICAL_95_TRIGGER_CAUSE_REGIME_TAXONOMY_AUTHORITY_20261014.md) · [38 vakanın delil incelemesi](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). **Eski 95/53 istatistikleri güncel 96'ya otomatik aktarılmaz.**
- [2025 Ocak–Nisan beş ekonomik olay ve ETF/COT/metaller/COMEX](GOLD_2025_JAN_APR_FIVE_EPISODES_COT_ETF_METALS_MICROSTRUCTURE_CAUSAL_AUDIT_20261014.md).
- [Tarihsel neden–haber kontrol protokolü](GOLD_HISTORICAL_EVENT_CAUSAL_ATTRIBUTION_SCOPE_PROTOCOL_20261014.md). Bu önceki tarihsel alt projenin "NO FORECAST" kuralı **o çalışmanın** kapsamıdır; yeni risk-araştırma hedefinin ileride sınanmasını yasaklamaz.

## 5. Ocak 2023 çalışma örneği — olay başladıktan sonra da karar verebilmek

**Araştırma başlangıcı:** Ocak 2023'teki **bütün takvim günleri**, sakin günler dahil gözlem evrenidir. **5 günlük trend işareti değiştiği için otomatik pozisyon değiştirilmez.** Başta altın/nakit durumumuz, gerçek fiyat yolu, maliyet ve aylık yön bilgisi belirlenir; ardından erken veya başlamış orta/büyük olay kanıtı araştırılır.

**Kaynaklı ilk örnekler:** 6 Ocak NFP ve 12 Ocak CPI sonrasında altındaki UP reaksiyonu, 18 Ocak PPI sonrasındaki ters fiyat reaksiyonu, 26 Ocak GDP ve 27 Ocak PCE bağlamları **aday olay incelemeleridir**. O günlerin NY17 getirilerini bilmek **o haberde maliyet-sonrası giriş fırsatı vardı** demek değildir. Olay başlangıcı, önceki hareket, açıklama saati, faiz/USD/metaller tepkisi, kalan gerçekleşebilir hareket ve fiyat/ücret ayrı hesaplanmalıdır. 26 Ocak V0 SAT işlemi `ret5` işaret değişimiyle üretilmişti; **orta/büyük DOWN olayının erken yakalandığının kanıtı değildir**.

**Şok öncesi veya sonrası aynı süreç:** (1) haber ve fiyatla kanıtlanmış `PRE_ONSET/ONSET/CONTINUATION` durumunu ayır; (2) **GOLD** veya **CASH** mevcut pozisyonuna göre, ters veya aynı yönde kalan hareketin maliyeti aşıp aşmadığını sorgula; (3) gerçek kararda bulunabilecek ilk geçerli BID/ASK/fill anını kayıtla; (4) ücret ve kaçırılan yükselişi dahil ederek `BUY/SELL/HOLD_GOLD/HOLD_CASH/WAIT` kararını karşılaştır; (5) hareket artık kalmadıysa geçmişte %3 oynamış olmasına bakarak geriye dönük işlem icat etme.

**Kip A:** 2024–2026 sonraki olaylarını, 2023 vakasının mekanizma yorumuna karşı örnek/analojiler olarak katabilir; sonraki yıllardaki doğru cevabı 2023 işlem saatine taşımak yasaktır. **Kip B:** 2023 işlem anında erişilebilir giriş verileriyle ayrı çalışır; önce görülmüş dönem nedeniyle bu çalışma bağımsız/kör test olarak tanıtılmaz.

**İlk esas deney statüsü:** `JAN2023_EVENT_DRIVEN_MEDIUM_LARGE_RESEARCH_NOT_YET_RUN`. 2023 Ocak V0 sayıları yalnız referanstır; burada hiçbir yeni kar/zarar, alarm doğruluğu veya AI başarısı varsayılmamıştır.

## 6. Bilimsel doğrulama — zorlama ilişki yerine ölçülebilir katkı

- **Önce olay/yön/evre/ufuk ve işlem hedefi tanımlanır.** `UP/DOWN` orta/büyük olay başlangıcı/devamı, ilk bariyere varış, kalan hareketin MFE/MAE'si ve gerçekleşebilir giriş/çıkış fiyatları ayrı ölçülür. Volatilite yalnız **destekleyici risk özelliğidir**, tek nihai amaç değildir. Ufuk olayın koşuluna göre aday olabilir, seçimde ileri bilgi kullanılamaz.
- **En az üç baz çizgisi:** tarihsel koşulsuz medyan/ampirik oran; önceki pencerenin EWMA/rolling realized-vol modeli; mevcut ayrı risk çalışmasında ölçülen dondurulmuş Ridge veya adaptif ölçek yaklaşımı. Gerekmedikçe karmaşık yöntem seçme.
- **Skorlar:** Yön ve şiddete göre ayrı olay precision/recall, kaçan sert DOWN ve UP, erken/geç teyit, false alarm, Brier/reliability, beklenen kalan MFE/MAE ve koşullu net fırsat; **100 USD net NAV, masraflı BUY/HOLD/CASH/aylık politika karşılaştırması, net fazla getiri, drawdown, işlem sayısı ve işlem dışı kalmanın fırsat maliyeti** zorunludur. Aynı veya örtüşen vaka bağımsız tekrar sayılamaz.
- **Karşıt deney:** ekonomik olay bağlantısını çıkarınca başarı ne oluyor? Gerçek ilk yayın saati yerine hatalı gecikme kullanınca? Olaysız eşleşmiş günlerde? Önceki gerçekleşmiş altın hareketine kontrol ekleyince? Seçim/çoklu test ve rejim değişimi altında üstünlük devam ediyor mu? Başarısız ve olumsuz bulgular korunur.
- **İki farklı değerlendirme:** **Kip A** kaynak doğrulama, olay benzerliği, tüm-yıl çapraz delil, olaysız kontroller ve mekanizma yanlışlama için retrospektif keşif yapar. **Kip B**, ileride deney yapılacaksa kaynak-vintage/DST QA, önceden sabitlenmiş protokol, kronolojik prequential öğrenme ve olgunlaşmış tahmin hatalarıyla adaptasyonu kullanır. Çoktan incelenmiş 2023–2026 üzerinde bulunan ilişkiyi 'bağımsız OOS' sayma. Ay-blok bağımlılığı, çoklu deneme ve farklı dönem aktarımını ayrıca sorgula.
- **İstatistiksel ilişki ≠ nedensellik ≠ işlem başarısı.** Haberler, dolar ve faiz birbiriyle etkileşebilir; haber sonrası faiz hareketini kör kontrol ederek toplam nedensel etki ölçmeye çalışma. Her olayın **en az iki rakip açıklaması** ve uygun sessiz kontrol grubu tutulur.
- **Teknik yöntem açık:** ANFIS, bulanık mantık, olay analojisi, EWMA/GARCH, volatilite-ölçekleme, probabilistik yöntem veya hibrit ancak gerçek karşılaştırmada **ek fayda gösterirse** aday olur. Şimdiden model veya katman dondurulmadı.

**Önceki gerçek büyüklük çalışması:** [2026 adaptif risk araştırması](GOLD_EXECUTION_2026_CAUSAL_REGIME_AND_VOLATILITY_RISK_RESEARCH_AUTHORITY_2026-10-08.md), mutlak overnight hareketi için basit baseline'a göre dinamik Ridge risk ölçeği 2025'te MAE **%5,49**, 2026'daki **bağımsız olmayan** iki arşiv alt-kohortunda **%12,46 / %14,20** iyileşme raporladı; **2023–24'te sürekli fayda göstermedi**, DOWN/yön kabiliyeti ve bankada işlem geçerliliği **kanıtlanmadı**. Bu eski deney yeni olay-örgülü uygulamanın **çalıştırıldığı** anlamına gelmez; sadece karşılaştırma kaynağıdır.

## 7. Karar anı raporunun içeriği

**Algoritma + yapay zekâ destekli ikinci değerlendirme, zorunlu tek bir mimari değil, denenebilecek çalışma biçimidir.** Önce sayısal inceleme XAU/metaller/FX/faiz/pozisyon/haber zamanlarından özellik, kaynak güveni, aday bağlantı, geçmiş analog ve karşıt vaka çıkarabilir. Daha sonra yapay zekâ bu **kaynağı ve sayılarını görebildiği kanıt paketini** değerlendirebilir: birbirine karışan nedenleri ayırır, alternatif mekanizmalar önerir, eksik ve çelişkili veriyi sorar, en savunulabilir olay/risk hükmünü **gerekçesiyle** verir veya `ABSTAIN` der. Yapay zekânın yeni önerisi **test edilmemiş hipotez** olarak kalır; uydurma haber, kaynağı olmayan olasılık veya geriye dönük “kesin tahmin” kabul edilmez. Üretilen her yorum `evidence_ids`, `competing_hypotheses`, `counterexamples`, `what_would_falsify`, `uncertainty` ile kayda geçer.

**İkinci katmanın gerçekten faydalı olup olmadığını ayrıca ölç:** (a) sadece sayısal algoritma, (b) sadece yapay zekânın kanıt yorumu, (c) algoritma + yapay zekâ karşılaştırılır; sabit aynı vaka setinde olaysız/ters örnek, **orta/büyük UP/DOWN yön-şiddet-evre sınıflaması, doğru/tarihinde uygulanabilir maliyetli BUY/SELL/HOLD/WAIT kararı ve portföy bazlarına karşı net katkı**, kaynak doğruluğu, risk kalibrasyonu ve bariz yanlış neden atfı puanlanır. Tek bir dil modelinin özgüveni veya akıcı anlatımı bilimsel doğrulama değildir. LLM değerlendirmesi sayısal olasılığı keyfine göre değiştiremez; değişiklik varsa kanıt ve yeniden hesap gerekir.

**Her çalışmanın nihai yanıtı** kipine göre doğal dille, sayılar ve kaynaklarıyla aşağıdaki soruları cevaplar:

1. **Kip / olay kimliği / kanıt ufku:** Tarih olay ID'si mi yoksa gerçek as-of karar anı mı? Hangi yılların olayları karşılaştırıldı, hangi kanıtlar sonradan bulundu? Altın mı nakit mi tutuluyordu?
2. **Olay örgüsü:** Ne olmuştu, hangi yeni bilgi ne zaman gelmişti, aktarım ve piyasa tepkisi hangi kanıtla uyumluydu?
3. **Benzer ve karşıt geçmiş:** Hangi geçmiş olayların hangi koşulları benziyor, farklar ve benzer haber–şoksuz kontroller neler?
4. **Orta/büyük UP/DOWN ve evre değerlendirmesi:** Hareket başlamış mı, ne kadarı kalmış olabilir, teyit/tersine dönüş işareti var mı; destekleyici volatilite ve güven/belirsizlik sonucu.
5. **Karar ve gerekçe:** `BUY/SELL/HOLD_GOLD/HOLD_CASH/WAIT` adayının beklenen kalan kazancı, kayıp riski ve **komisyon+spread+uygulama** kapısı; kanıt yetmezse **WAIT/ABSTAIN**. Kip A'da bu karar *retrospektif inceleme* olarak etiketlenir.
6. **Doğrulama statüsü:** Kip A'da gerçekleşen olaylar kullanılabilir, sonuç `EX_POST_DISCOVERY` olarak raporlanır. Kip B'de tahmin kilitlenir, gerçekleşen fiyat/şok ancak hedef olgunlaşınca açılır; başarısız nedenler ve yeni deney sürümü ayrıca belgelenir.

**Banka/işlem kapısı:** Olay temelli **araştırma AL/SAT/TUT/BEKLE kararları üretmek hedefin parçasıdır**; fakat Türkiye saatli uygulanabilir banka ASK/BID ve işlem pencere/gerçekleşme kaydı olmadan bu kararlar **teorik** kalır. Alışta **%0,8**, satışta **%0,8**, makas/gecikme/slippage maliyetleri her simülasyonda ortak koşulda gösterilir. Sabit karar saatine ihtiyaç yoktur; banka emir alınan zaman aralığı araştırma yürütme kısıtıdır. K100/H3/SESSION/aylık yön modelleri kanıt ve karşılaştırma kaynağı olarak değerlendirilebilir, doğrudan taşınıp kanıtlanmış sayılamaz.


**14 Ekim 2026 sayısal takip testi (V1, yalnız fiyat):** [Ocak 2023 tüm 31 gün olay-takip ve GPT karşıt delil raporu](adaptive_volatility_learning/months/2023-01/JAN_2023_EVENT3_FULL_31DAY_RESEARCH_REPLAY_20261014.md) kaydedildi. Tamamlanmış M15 / dört önceki tam NY17 kapanışı bazlı **+%3 UP / -%3 DOWN** tespiti, 4 Ocak 08:00 UTC UP teyidi ve **08:15 UTC ASK alış**, başka DOWN3 yok; Ocak sonu *sadece kıyas amaçlı* kapanış SAT. %0,8 + %0,8 komisyon, vendor makasıyla **100 → 101,9914 USD**; aynı eski fiyat/masrafla pasif altın **103,7589 USD**. Bu **GPT olay yorumunun işleme ek getirisi testi DEĞİL**, fiyat-only tek ay `EXPLORATORY` baseline'ıdır; orta/büyük olayın kalan getirisi, eş-UTC çok faktör teyidi ve banka-gerçek ASK/BID yok; **asıl üretime hazır olay stratejisi sonuçlanmadı**. 31 gün CSV ve frozen sayısal JSON raporda, yöntem sicili ve aylık STATE güncellendi.

## 8. Bugünkü durum, açık işler ve otorite

| Alan | 14 Ekim 2026 itibarıyla kanıtlı durum |
|---|---|
| Tarihsel altın olayları | **MEVCUT:** 42 düzeltilmiş V1 + 54 V2 fiyat kaydı; farklı olaylar arasında örtüşme var. 2023–25 haber/metal verisi ve 2025 Ocak–Nisan beş olay incelemesi |
| COT/ETF kaynak zamanı | **KISMEN DOĞRULANDI:** CFTC cuma yayını ve 2023/25 istisnaları; 2025 bazı ham long/short örnekleri. Tüm tatil haftaları ve bütün ETF günlük firstprint tam değil |
| USD/faiz/metallerin haberle eşsaatli aktarımı | **EKSİK:** DXY/2Y/10Y reel getiriler ve metal/COMEX-Londra veri-vintage tüm olaylarda aynı UTC ile doğrulanmadı |
| Geçmiş volatilite tahminleri | **AYRI EMPİRİK ÇALIŞMA VAR:** dinamik büyüklük ölçeği bazı yıllarda iyileşti; önceki yıllarda taşınabilirliği ve yön güvenilirliği yok |
| **Ocak 2023 araştırma statüsü** | **YALNIZ HATALI HEDEFE AİT V0 BAZ DENEME TAMAMLANDI:** 31 takvim günü, 20 tam/1 kısmi NY17 seansı; mekanik $100 → **$101,9695**, buyhold **$103,7589**, 0/20 vol-gate. **2023 Ocak fiyat-only %3 olay V1 adayı çalıştırıldı (100 → 101,9914 USD); ekonomik olay+GPT sayısal karar katkısı hâlâ denenmedi.** |
| Al/sat ve gerçek banka yürütmesi | **BU AŞAMANIN SONUCU DEĞİL; ÜRETİM ONAYI YOK** |

**Düzeltilmiş iş sırası:** [Ocak 2023 V0 sayısal arşivi](adaptive_volatility_learning/months/2023-01/JAN_2023_FULL_MONTH_GPT_ONLY_SCIENTIFIC_AUDIT.md) korunur. **Ocak 2023 V1 %3 fiyat-olay baseline'ı yapıldı; şimdi çok-etkenli GPT+sayısal gerçek olay fırsatı modelini ayrıca incele:** bütün günlerde sakin/olay-adayı gözlem evreni, fiyat yolu, aynı-saat makro/metaller/FX/faiz/risk, GPT karşıt olay incelemesi, olası BUY/SELL/HOLD/WAIT kararı, gerçekleşebilir fiyat ve tam ücret; ay sonunda $100 NAV ile pasif kıyas. Yeni sonuç üretilince [STATE.json](adaptive_volatility_learning/months/2023-01/STATE.json) güncellenerek Şubat'a geçilir. Geriye dönük tam-yıl bilgisi açıklama için kullanılabilir, **as-of emir simülasyonuna gizlice taşınamaz**. [Yeniden başlangıç protokolü](adaptive_volatility_learning/EVENT_DRIVEN_MEDIUM_LARGE_MOVE_RESTART_CONTRACT_20261014.md).

### 8.1 Aylık kalıcı öğrenme: hafıza, algoritma ve yapay zekâ kanıtı

**Çalışma dilimi aylıktır:** Önce **Ocak 2023**, sonra **Şubat 2023**, ilerleyen aylar. Bu sıra yalnız vaka inceleme düzenidir: `FULL_HISTORY_DISCOVERY` içinde Ocak 2023 araştırılırken **2024/2025/şimdiye kadarki 2026 olayları kullanılabilir**. Her ayın sonunda **sonraki aya aktarılabilecek öğrenme** yalnız sözle değil, dosya/kod/deney kimliğiyle kaydedilir.

**Tek düzenli kayıt kökü:** [Aylık öğrenme ve kalıcı kayıt rehberi](adaptive_volatility_learning/README.md). **Ana manifest** yalnız araştırma amacı, bilimsel sınırlar ve bu dosyalara bağlantıları tutar; her ayın binlerce veri satırı ve öğrenme dökümü ana manifeste eklenmez.

| Kalıcı bileşen | Gerçek dosya / rol |
|---|---|
| [Olay kimlikleri ve benzer/karşıt örnekler](adaptive_volatility_learning/EVENT_REGISTRY.json) | Yıllar arası olay kütüphanesi; eski 42+54 fiyat kaydı doğrudan benzersiz olay varsayılmaz |
| [Özellik ve yöntem/algoritma sürümleri](adaptive_volatility_learning/METHOD_REGISTRY.json) | Eski V0 sonucu **karşılaştırma yöntemi** olarak durur; olay temelli asıl yöntem **henüz oluşturulup test edilmedi** |
| [Ocak 2023 aylık durum / Şubat'a devir](adaptive_volatility_learning/months/2023-01/STATE.json) | V0 ve GPT incelemesi **ARŞİVLENDİ**; **fiyat-only V1 olay baseline'ı tamamlandı, GPT destekli gerçek net fırsat stratejisi AÇIK** |
| [AI ikinci inceleme ve kalite protokolü](adaptive_volatility_learning/AI_REVIEW_PROTOCOL.md) | **Yalnız GPT**; olayın evresi, yönü, net işlem fırsatı, yanlışlama ve kanıt denetimi; harici AI kullanılmıyor |

**GPT-ONLY kullanıcı sınırı:** Bugün bu projede **yalnız GPT** yorumlar; DeepSeek/Gemini/harici AI çalıştırılmaz. **Test aşamasındaki AI entegrasyonu:** Sayısal analiz kaynak kimlikli özellik ve vaka karşılaştırmasını üretir; ChatGPT ikinci incelemede kanıtları, alternatif nedenleri ve çelişkileri eleştirir. **Aynı vaka kümesinde algoritma tek, AI tek, birlikte** sonuçları kıyaslanır. AI özgün kaynak olmadığı gibi metin yazınca modelin parametreleri otomatik değişmez. Önerilen yeni algoritmik kuralın gerçek kaynak/kod/deney doğrulaması olmadan `validated` statüsü alamaz. Dış servise ham özel piyasa verisi, banka bilgisi, API anahtarı gönderilmez.

**Ocak→Şubat devamlılığı:** `STATE.json` içindeki `handoff_to_next_month` ve ortak yöntem/olay sicilleri daha sonra Şubat'ın başlangıç girdisi olacaktır; her iyileştirmede yeni sürüm, eski metrikler, başarısızlıklar ve geriye dönük seçim yanlılığı korunur. **V0 fiyat/NAV hesabı ve GPT nitel incelemesi GERÇEKTEN kaydedildi; fakat yanlış hedefli V0 asıl olay stratejisi tamamlandı anlamına gelmez. Ocak 2023 yeniden çalışma yapılmadan Şubat'a doğrulanmış strateji aktarılmaz.**

### Belgeler ve sürüm yönetimi

- **Bu dosya**, yeni amacın ve araştırma çıktısının **tek güncel yönlendirme manifestidir**. 14 Ekim 2026 tarihli eski **5.190 satırlık TAM** ana metin değişmeden [TARİHSEL MANİFEST ARŞİVİNE](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST_FULL_HISTORY_SNAPSHOT_20261014.md) alındı. Önceki veri denetimleri, model sonuçları, başarısız testler, Ocak 2026 V1–V4 ve referans bağlantıları **kaybolmadı**. Arşivdeki eski "BINDING/NEXT/NO FORECAST" yalnız **kendi tarih/deney kapsamı** içindir.
- **Kaynak hiyerarşisi:** ilgili veri/kapanış saati/PIT sözleşmesi → dondurulmuş deney protokolü ve sayısal CSV/JSON → bilimsel sonuç/yanlışlama → bu amaç manifesti → tarihsel arşiv notları. Bir amaç değişikliği eski deney skorlarını değiştirmez.
- [Otorite/değişiklik ve eski modellerin ayrımı](GOLD_INTRAMONTH_MANIFEST_AUTHORITY_AND_CHANGE_CONTROL_20261013.md). Aylık H=1 [ayrı proje manifesti](GOLD_MONTHLY_PROJECT_MANIFEST.md) yetkisini korur. V1/V2 olay/38 kaynak, günlük/H3/SESSION ve banka saatleri ayrı hedef/otorite.
- **Repo:** `ataullahturgut/sim3-automation`, araştırma dalı `research-gold-jan26-two-factor-confirmation-v4-20261013`, [PR #128](https://github.com/ataullahturgut/sim3-automation/pull/128) **AÇIK, MAIN'E BİRLEŞMEDİ**. Üretime geçiş veya gerçek işlem emirleri için ayrı yetki gerekir. Açık depoya erişim anahtarı, lisanslı ham özel veri veya hesap bilgisi girilmez.
- **Bakım standardı:** Her yeni iş `FULL_HISTORY_DISCOVERY` ya da `AS_OF_DECISION_EVALUATION` olarak açık etiketlenir. Ana manifeste binlerce satırlık deney günlüğü yığma; amaç, olay ID/kullanılan yıl evreni, yöntem, sayısal/AI karşılaştırma sonucu, alternatif açıklamalar, test statüsü ve ayrı rapor linki kısa tutulur. Eski negatif sonuçlar ve veri açıklıkları korunur.

### 14 Ekim 2026 — 15 dakika / tek takvim günü denetimi
Kullanıcı talimatı: gün yalnız 1 kez kontrol edilmez; **TRT 00:00–23:45 her 15 dakikada (96 zaman damgası)** as-of XAU BID/ASK, diğer piyasalar, ilk yayım haberleri ve mevcut pozisyonun haklılığı yeniden değerlendirilir. **Yeni kanıt yoksa karar korunur**, kör işlem üretilmez. Günler sırayla çalışılacak; yeni pozisyon açma/tasfiye yalnız o saatte erişilebilir ve maliyeti karşılayan kanıta dayanacak. 1 Ocak Pazar/tatil olduğundan **2 Ocak 2023 ilk gün çalışıldı**: 96 slot, **0 spot fiyat çubuğu**, makro-tatil takvim ve geçmiş olay bağlantıları, 18:49 TRT BIST +%2,76 ilk haber sonrası risk bağlam güncellemesi, ancak 0 kanıtlanmış banka kotasyonu → **WAIT/CASH 100,00$**. Ertesi günün 02:00 TRT yeni fiyatı 2 Ocak slotuna konmadı. [İlk gün raporu](adaptive_volatility_learning/months/2023-01/days/2023-01-02/JAN02_2023_SINGLE_DAY_15M_EVENT_EVIDENCE_AUDIT_20261014.md). **Yalnız 2 Ocak yeni ayrıntılı rejim taraması tamamlandı, 3 Ocak henüz çalışılmadı**; önceki full-month simülasyonları bundan ayrı saklanır.

### 14 Ekim 2026 — 3 Ocak küresel olay bazlı 96×15 dakika protokolü
**3 Ocak tamamlandı**: [3 Ocak vakalar, M15 çapraz piyasa ve $100 raporu](adaptive_volatility_learning/months/2023-01/days/2023-01-03/JAN03_2023_SINGLE_DAY_CAUSAL_MARKET_REPLAY_20261014.md), 96×15m decision CSV ve ilk yayım/cross-year analog JSON. TRT 00:00–23:45 **88 M15 başlangıç/87 tamamlanmış/9 tamamlanmamış kontrol**; global XAU + ABD ZN/NQ/CL eş-zaman *geciktirilmiş bar* eşleme; As-of Reuters Caixin, altın-yield, Almanya CPI, US PMI, US construction ilk yayımları. Fed2022/CPI2022 analogları **geçmiş olay açıklama**, bugün otomatik kural değil. *BIST100 ve Türkiye iç hisse/risk göstergeleri XAU/USD ons yönü için hiçbir karar değişkenine alınmaz; 2 Ocak arşivinde geçmiş BIST haberinin gözlenmiş olması onu model sinyali yapmaz.* 3 Ocak başlangıç ve bitiş 100 USD CASH, **0 işlem**; yüksek güvenilir net kalan büyük hareket sinyali görülmedi ve gerçekte banka kotasyonu da arşivde yok. Kararlar hindsight-exposed, OOS değildir. Yeni 15 dakikalık protokolde sıradaki gün 4 Ocak; eski aylık V0/V1 baselines ayrıdır.
