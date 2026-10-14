# GOLD INTRAMONTH — AMAÇ ODAKLI ANA PROJE MANİFESTİ

**Sürüm:** 2026-10-14 · **Alan:** Ekonomik olay örgüsüyle adaptif XAU/USD volatilite/büyük-hareket araştırması · **Statü:** AMAÇ VE BİLİMSEL KURALLAR TANIMLANDI; BU YENİ UYGULAMA HENÜZ ÇALIŞTIRILMADI/DOĞRULANMADI.

> **Projenin asıl amacı:** Altınla ilgili **2023, 2024, 2025 ve 2026 dahil bütün mevcut olay kayıtlarından** ekonomik neden–sonuç adaylarını, benzerlikleri ve karşıt örnekleri araştırmak; tarihleri ilk etapta birer **olay kimliği / inceleme sırası** olarak ele almak; bu ortak öğrenimden **adaptif volatilite ve büyük hareket riski** hakkında gerekçeli değerlendirmeler üretebilen bir sistem geliştirmek. **Algoritmik sayısal inceleme ile yapay zekâ destekli kanıt muhakemesi birlikte** değerlendirilebilir. Geçmiş olaylarda **sonradan öğrenilmiş bilgiler serbestçe analiz edilebilir**, ancak bu çıktı tarihsel anda yapılmış kör tahmin sanılamaz. Kanıt yetersizse **BELİRSİZ** denir.

**Kapsam notu:** ANFIS şeması **yalnız fikir örneğidir**; model veya katman sayısı önceden seçilmemiştir. **Algoritma verilerden ölçülebilir özellikleri ve benzerlikleri çıkarabilir; yapay zekâ ikinci bir değerlendirmede olayları, ekonomik aktarımı, karşıt kanıtları ve uygun risk sonucunu tartışabilir.** Bu olası iş bölümü bugün için bir **araştırma seçeneğidir**, zorunlu teknik mimari veya doğrulanmış performans değildir. İlk karar **adaptif volatilite/risk değerlendirmesidir**; otomatik banka AL/SAT/TUT emri değildir.

## 1. Tam olarak hangi soruyu çözmek istiyoruz?

**"Bugün, bu saatte altın piyasasında ne oluyor? Hangi yeni olaylar ve ön koşullar bu durumu açıklıyor? Geçmişte benzer koşullarda sonrasında altın hangi büyüklükte ve türde hareket etmişti? Bugünün eldeki kanıtlarına bakarak sonraki belirtilen zaman aralığı için ne söyleyebiliriz?"**

- **Öncelikli çıktı:** Ufka göre beklenen **mutlak fiyat hareketi / realized volatility**, şok/sert hareket olasılığı, muhtemel büyüklük aralığı ve güven seviyesi. Bir fiyat hareketinin **başlaması, devamı, tersine dönüşü ve stabil kalması** birbirinden farklı sonuçlar olarak incelenir.
- **Yön (UP/DOWN)** ancak aynı vakalar üzerinde ayrıca bilimsel olarak doğrulanırsa ikincil çıktı olur. Volatilite = yön değildir; "yüksek risk" otomatik SAT değildir.
- **Ufuk başlangıçta tanımlanır:** 30 dakika, 2 saat, seans sonu, ertesi uygun seans, 1/3/5 işlem günü gibi pencereler **saat ve gerçek fiyat hedefiyle** ayrıdır. Bir tane keyfî ufuk bütün durumlara zorlanmaz; ufuk değiştirmek ayrı deney gerektirir.
- **Karar** bir olay-örgüsü + risk değerlendirmesi olabilir: "normal dalgalanma", "büyük hareket riski", "olası likidite şoku", "reversal olasılığı incelenmeli", "belirsiz". Etiketler **önceden tanımlı olasılık ve hata ölçümleriyle** anlam kazanır; olay adından sonuç uydurulmaz.
- **Başarı iki ayrı düzeyde ölçülür:** (i) **tam arşivli keşif** sırasında anlamlı, kaynakla destekli ve karşıt örneklerle yanlışlanabilir mekanizmalar bulmak; (ii) bunların **yeni/kör değerlendirmede** basit volatilite kıyaslarını geçip kalibrasyon ve yanlış-alarm/kaçan-şok hatasını iyileştirmesi. Keşif başarısı, kendiliğinden ileri tahmin başarısı değildir.

## 2. İKİ ÇALIŞMA KİPİ — araştırmayı tarih sırası sınırlamasına hapsetme

**KİP A — `FULL_HISTORY_DISCOVERY` (ŞİMDİKİ ANA ÇALIŞMA):** 2023'ten başlayan yürüyüş yalnız **olay inceleme sırasıdır**. 2023 Mart olayını anlamak için 2024–2026'da yaşanan benzer krizler, sonuçları, sonradan yayımlanmış WGC/COT yorumları ve 2026'daki bilimsel değerlendirmeler **kullanılabilir**. Gelecek olay verileri geçmiş olayın **anlamını ve mekanizma adayını yeniden yorumlamayı** sağlar; hiç kimse 2023'te o veriyi biliyordu denmez. Olayların gerçekleşen sonraki fiyatı da vaka analizinde **sonuç etiketi** olarak görülebilir. Tarihler, olay kimliği ve gözlem zamanı olarak saklanır; kronolojik kesme emri değildir. **Bu kipte verilen risk/olay kararı, geçmişin tümüyle bilgilendirilmiş geriye dönük araştırma hükmüdür, o tarihte yapılmış tahmin değildir.**

**KİP B — `AS_OF_DECISION_EVALUATION` (DAHA SONRA AYRI SINAMA):** Algoritmanın/yapay zekânın o anda gerçekten ulaşılabilecek veriyle bir **öngörü** yapıp yapamadığını sınamak istediğimizde, hem olay örnekleri hem modelin eğitildiği bilgi hem de tetikleyici haber ve karar girdileri **karar anıyla uygun** sınırlandırılır. Önceden bütün 2023–2026 olaylarını görerek kurduğumuz bir mekanizmayı 2023'te blind keşfedilmiş diye tanıtamayız. Böylece Kip A'nın geniş öğrenmesini bozmadan, Kip B'nin bilimsel sınırını koruruz.

**Kayıt zorunluluğu:** Her incelemede `mode, case_id, event_date, evidence_available_at, decision_origin_if_any, future_outcome_visible, historical_scope, comparator_cases, ai_assessment_version, result_status` yazılır. `FULL_HISTORY_DISCOVERY` içinde `event_date` bilgi kesme noktası değildir; `AS_OF_DECISION_EVALUATION` içinde `decision_origin` ve bilgi penceresi kesin olmalıdır.

### 2.1 Kaynak ve saat doğruluğu iki kipte de korunur

Her değerlendirmede aşağıdaki alanlar çalışma kipine göre kaydedilir:

| Kayıt | Şart |
|---|---|
| **Karar anı** | \`case_id\`, kesin \`origin_utc\`, Türkiye/New York yerel saatleri ve yaz saati; yalnız gün adı yeterli değil |
| **Veri erişimi** | Kaynağın ölçüm \`observed_at\` zamanı ile gerçek \`first_published_at / available_at\` **ayrı** |
| **Veri tanımı** | Sağlayıcı, spot/futures, BID/ASK/MID, 1m/15m/1h/gün, kontrat devri, kapanış ve tatil |
| **Hedef** | Hangi başlangıç-bitiş fiyatı, ileri mutlak log-getiri, realized-vol, kuyruk olasılığı ve şok eşiği |
| **Olay havuzu** | **Kip A:** 2023–2026 ve erişilebilir bütün tarihsel dönemlerden benzer, ters, sonradan açıklanmış olaylar; **Kip B:** deneyde izin verilen karar anı öncesi eğitim/kanıt havuzu |
| **Karşı kanıt** | Rakip nedenler, uyumsuz veriler, benzer haber olup şok olmayan günler |
| **Çıktı** | Kanıtlı ekonomi yorumu + şartlı volatilite/risk + belirsizlik/ABSTAIN + veri kalitesi |
| **Deney izi** | Sürüm, kaynak/vintage, önceden belirlenmiş kıyas, test dönemi ve sonradan gerçekleşen sonuç |

**Kaynak-vintage / as-of ayrımı:** **Kip A'da** gelecek yılın olayları ve geç yayımlanan veriler mekanizmayı araştırmak için **serbesttir**; ancak her bilginin **gerçekte ne zaman yayımlandığı** saklanır ki geçmiş olayın başlatıcısıyla sonradan gelen açıklama karıştırılmasın. **Kip B'de** \`available_at <= origin_utc\` zorunludur: yayımlanmamış CPI/NFP, kapanmamış GVZ/VIX, geç açıklanan ETF/COT veya sonradan revize seri tahmin girdisi olmaz. Her iki kipte de eksik veri \`MISSING/UNKNOWN\`; hiçbir kayıt uydurulmaz.

**COT özel kural:** Pozisyon salı ölçülür, **normal** resmî yayın cuma **15:30 America/New_York**; 2023 ION ve 2025 kapanma gecikmelerinde resmî istisna tarihi geçerlidir. [CFTC yayımlanma ve 154-hafta zaman düzeltmesi](GOLD_COT_PUBLICATION_CLOCK_OFFICIAL_AUDIT_AND_RETROSPECTIVE_154_ORIGIN_RETEST_20261014.md). ETF aylık WGC verisi de yalnız **ilk yayımlandıktan sonra** kullanılabilir. CFTC \`d_opt_mm_net\` ham opsiyon kontratı değil, normalize **(combined net − futures-only net)** farkının değişimidir: [ham COT yanlışlama çalışması](GOLD_COT_RAW_LONG_SHORT_FALSIFICATION_2025_Q1_20261014.md).

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

## 5. 2 Ocak örneği: sistemden fiilen ne bekliyoruz?

**Örnek tarih:** \`2026-01-02\` (konuşmadaki "2 Ocak" örneği 2026 Ocak araştırma bağlamında yorumlanmıştır). **Kesin saat ve ufuk henüz seçilmediği için hiçbir risk sayısı, tahmin veya gerçekleşmiş karar burada üretilmiş değildir.** Ocak 2026 daha önce defalarca incelendiğinden yeni sonuç **kör dış örnek test** diye sunulamaz.

**Kip A çalışma örneği:** \`EVENT_2026_01_02\` seçilir → o günün fiyat/metaller/makro/ETF/COT/fiziki veri ve haberlerinin **sonradan derlenmiş tam kanıtları** okunur → 2023, 2024, 2025 ve **2 Ocak sonrasındaki 2026 olayları** dahil benzer/ters olaylar bulunur → geçmiş benzerlik ve farklı mekanizmalar tartışılır → sayısal özelliklerden hareket büyüklüğü, oynaklık ve şok riskine ilişkin geriye dönük **araştırma hükmü** oluşturulur → yapay zekâ bu hükmü bağımsız kanıt/karşı kanıt üzerinden eleştirir. **Kip B** daha sonra ayrıca seçilirse 2 Ocak günündeki belirli saatin bilinebilir kaynaklarıyla sıfırdan bir deney açılır ve bu Kip A incelemesi **blind sonuç** sayılmaz.

**Örnek çalışmanın henüz üretilmemiş çıktısı:** \`mode=FULL_HISTORY_DISCOVERY; case_id=EVENT_2026_01_02; event_time=TO_BE_DEFINED; compared_event_ids=NOT_EVALUATED; quant_features=NOT_COMPUTED; economic_hypotheses=NOT_EVALUATED; ai_second_assessment=NOT_RUN; historical_risk_verdict=NOT_ESTIMATED; evidence_confidence=UNKNOWN; validation_status=NO_BLIND_TEST\`. Bu bir sonuç değil, kayıt örneğidir.

## 6. Bilimsel doğrulama — zorlama ilişki yerine ölçülebilir katkı

- **Önce ufuk/hedef/metrik dondurulur.** Adaptif volatilite için ileri mutlak log-getiri, realized volatility, önceden seçilmiş quantile/aralık veya ilk şok bariyerine varış riski ayrı ölçülür. Tahmin ufku veri çözünürlüğüyle uyumlu olmalı.
- **En az üç baz çizgisi:** tarihsel koşulsuz medyan/ampirik oran; önceki pencerenin EWMA/rolling realized-vol modeli; mevcut ayrı risk çalışmasında ölçülen dondurulmuş Ridge veya adaptif ölçek yaklaşımı. Gerekmedikçe karmaşık yöntem seçme.
- **Skorlar:** MAE/RMSE (hareket), quantile pinball loss ve kapsama, Brier/reliability (olasılık), risk alarmında recall/false alarm/missed-tail, rejim/tarih/uç olay altgrupları ve tahmin yok/ABSTAIN kapsaması. Aynı vaka veya örtüşen fiyat penceresi yüzlerce bağımsız örnek gibi sayılamaz.
- **Karşıt deney:** ekonomik olay bağlantısını çıkarınca başarı ne oluyor? Gerçek ilk yayın saati yerine hatalı gecikme kullanınca? Olaysız eşleşmiş günlerde? Önceki gerçekleşmiş altın hareketine kontrol ekleyince? Seçim/çoklu test ve rejim değişimi altında üstünlük devam ediyor mu? Başarısız ve olumsuz bulgular korunur.
- **İki farklı değerlendirme:** **Kip A** kaynak doğrulama, olay benzerliği, tüm-yıl çapraz delil, olaysız kontroller ve mekanizma yanlışlama için retrospektif keşif yapar. **Kip B**, ileride deney yapılacaksa kaynak-vintage/DST QA, önceden sabitlenmiş protokol, kronolojik prequential öğrenme ve olgunlaşmış tahmin hatalarıyla adaptasyonu kullanır. Çoktan incelenmiş 2023–2026 üzerinde bulunan ilişkiyi 'bağımsız OOS' sayma. Ay-blok bağımlılığı, çoklu deneme ve farklı dönem aktarımını ayrıca sorgula.
- **İstatistiksel ilişki ≠ nedensellik ≠ işlem başarısı.** Haberler, dolar ve faiz birbiriyle etkileşebilir; haber sonrası faiz hareketini kör kontrol ederek toplam nedensel etki ölçmeye çalışma. Her olayın **en az iki rakip açıklaması** ve uygun sessiz kontrol grubu tutulur.
- **Teknik yöntem açık:** ANFIS, bulanık mantık, olay analojisi, EWMA/GARCH, volatilite-ölçekleme, probabilistik yöntem veya hibrit ancak gerçek karşılaştırmada **ek fayda gösterirse** aday olur. Şimdiden model veya katman dondurulmadı.

**Önceki gerçek büyüklük çalışması:** [2026 adaptif risk araştırması](GOLD_EXECUTION_2026_CAUSAL_REGIME_AND_VOLATILITY_RISK_RESEARCH_AUTHORITY_2026-10-08.md), mutlak overnight hareketi için basit baseline'a göre dinamik Ridge risk ölçeği 2025'te MAE **%5,49**, 2026'daki **bağımsız olmayan** iki arşiv alt-kohortunda **%12,46 / %14,20** iyileşme raporladı; **2023–24'te sürekli fayda göstermedi**, DOWN/yön kabiliyeti ve bankada işlem geçerliliği **kanıtlanmadı**. Bu eski deney yeni olay-örgülü uygulamanın **çalıştırıldığı** anlamına gelmez; sadece karşılaştırma kaynağıdır.

## 7. Karar anı raporunun içeriği

**Algoritma + yapay zekâ destekli ikinci değerlendirme, zorunlu tek bir mimari değil, denenebilecek çalışma biçimidir.** Önce sayısal inceleme XAU/metaller/FX/faiz/pozisyon/haber zamanlarından özellik, kaynak güveni, aday bağlantı, geçmiş analog ve karşıt vaka çıkarabilir. Daha sonra yapay zekâ bu **kaynağı ve sayılarını görebildiği kanıt paketini** değerlendirebilir: birbirine karışan nedenleri ayırır, alternatif mekanizmalar önerir, eksik ve çelişkili veriyi sorar, en savunulabilir olay/risk hükmünü **gerekçesiyle** verir veya `ABSTAIN` der. Yapay zekânın yeni önerisi **test edilmemiş hipotez** olarak kalır; uydurma haber, kaynağı olmayan olasılık veya geriye dönük “kesin tahmin” kabul edilmez. Üretilen her yorum `evidence_ids`, `competing_hypotheses`, `counterexamples`, `what_would_falsify`, `uncertainty` ile kayda geçer.

**İkinci katmanın gerçekten faydalı olup olmadığını ayrıca ölç:** (a) sadece sayısal algoritma, (b) sadece yapay zekânın kanıt yorumu, (c) algoritma + yapay zekâ karşılaştırılır; sabit aynı vaka setinde olaysız/ters örnek, kaynak doğruluğu, risk kalibrasyonu ve bariz yanlış neden atfı puanlanır. Tek bir dil modelinin özgüveni veya akıcı anlatımı bilimsel doğrulama değildir. LLM değerlendirmesi sayısal olasılığı keyfine göre değiştiremez; değişiklik varsa kanıt ve yeniden hesap gerekir.

**Her çalışmanın nihai yanıtı** kipine göre doğal dille, sayılar ve kaynaklarıyla aşağıdaki soruları cevaplar:

1. **Kip / olay kimliği / kanıt ufku:** Tarih olay ID'si mi yoksa gerçek as-of karar anı mı? Hangi yılların olayları karşılaştırıldı, hangi kanıtlar sonradan bulundu?
2. **Olay örgüsü:** Ne olmuştu, hangi yeni bilgi ne zaman gelmişti, aktarım ve piyasa tepkisi hangi kanıtla uyumluydu?
3. **Benzer ve karşıt geçmiş:** Hangi geçmiş olayların hangi koşulları benziyor, farklar ve benzer haber–şoksuz kontroller neler?
4. **Adaptif volatilite sonucu:** Tanımlı ufukta beklenen hareket/riske ilişkin olasılık veya aralık, referans baseline, kalibrasyon ve belirsizlik.
5. **Karar ve gerekçe:** Risk değerlendirmesi; güven yetersizse **ABSTAIN**, risk yokmuş gibi kesin hüküm değil.
6. **Doğrulama statüsü:** Kip A'da gerçekleşen olaylar kullanılabilir, sonuç `EX_POST_DISCOVERY` olarak raporlanır. Kip B'de tahmin kilitlenir, gerçekleşen fiyat/şok ancak hedef olgunlaşınca açılır; başarısız nedenler ve yeni deney sürümü ayrıca belgelenir.

**Ayrı banka/işlem kapısı:** Türkiye saatli gerçek banka ASK/BID olmadan; alışta **%0,8**, satışta **%0,8** komisyon, banka makası ve gecikme ayrıca ölçülmeden volatilite/risk kararı otomatik AL/SAT/TUT olmaz. Daha önceki K100/H3/SESSION/aylık yön modelleri farklı hedeflerdir; kendiliğinden bu yeni sisteme taşınmaz.

## 8. Bugünkü durum, açık işler ve otorite

| Alan | 14 Ekim 2026 itibarıyla kanıtlı durum |
|---|---|
| Tarihsel altın olayları | **MEVCUT:** 42 düzeltilmiş V1 + 54 V2 fiyat kaydı; farklı olaylar arasında örtüşme var. 2023–25 haber/metal verisi ve 2025 Ocak–Nisan beş olay incelemesi |
| COT/ETF kaynak zamanı | **KISMEN DOĞRULANDI:** CFTC cuma yayını ve 2023/25 istisnaları; 2025 bazı ham long/short örnekleri. Tüm tatil haftaları ve bütün ETF günlük firstprint tam değil |
| USD/faiz/metallerin haberle eşsaatli aktarımı | **EKSİK:** DXY/2Y/10Y reel getiriler ve metal/COMEX-Londra veri-vintage tüm olaylarda aynı UTC ile doğrulanmadı |
| Geçmiş volatilite tahminleri | **AYRI EMPİRİK ÇALIŞMA VAR:** dinamik büyüklük ölçeği bazı yıllarda iyileşti; önceki yıllarda taşınabilirliği ve yön güvenilirliği yok |
| **Bütün yıllarla olay-ID üzerinden keşif ve algoritma + yapay zekâ yorumu** | **ARAŞTIRMA HEDEFİ OLARAK TANIMLANDI; 2023→2026 çapraz-olay otomatik analizi veya ikinci yapay zekâ değerlendirmesi henüz çalıştırılmadı** |
| Al/sat ve gerçek banka yürütmesi | **BU AŞAMANIN SONUCU DEĞİL; ÜRETİM ONAYI YOK** |

**Bir sonraki araştırma işi:** 2023'te bir olay ID'sinden başlayıp **2024, 2025 ve 2026 olaylarının tamamına erişebilen Kip A** ile çoklu-etkenli benzerlik/karşıtlık incelemesi yürütmek; sayısal faktör çıktısına **kanıt temelli yapay zekâ ikinci görüşünü** ekleyip nerede gerçek katkı, nerede anlatı yanılgısı olduğunu ölçmek. Ardından gereken noktada Kip B protokolünü **ayrı** oluşturmak. **Tek bir güzel hikâye veya sonradan bilinen doğru fiyat sonucu erken öngörü ispatı değildir.**

### Belgeler ve sürüm yönetimi

- **Bu dosya**, yeni amacın ve araştırma çıktısının **tek güncel yönlendirme manifestidir**. 14 Ekim 2026 tarihli eski **5.190 satırlık TAM** ana metin değişmeden [TARİHSEL MANİFEST ARŞİVİNE](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST_FULL_HISTORY_SNAPSHOT_20261014.md) alındı. Önceki veri denetimleri, model sonuçları, başarısız testler, Ocak 2026 V1–V4 ve referans bağlantıları **kaybolmadı**. Arşivdeki eski "BINDING/NEXT/NO FORECAST" yalnız **kendi tarih/deney kapsamı** içindir.
- **Kaynak hiyerarşisi:** ilgili veri/kapanış saati/PIT sözleşmesi → dondurulmuş deney protokolü ve sayısal CSV/JSON → bilimsel sonuç/yanlışlama → bu amaç manifesti → tarihsel arşiv notları. Bir amaç değişikliği eski deney skorlarını değiştirmez.
- [Otorite/değişiklik ve eski modellerin ayrımı](GOLD_INTRAMONTH_MANIFEST_AUTHORITY_AND_CHANGE_CONTROL_20261013.md). Aylık H=1 [ayrı proje manifesti](GOLD_MONTHLY_PROJECT_MANIFEST.md) yetkisini korur. V1/V2 olay/38 kaynak, günlük/H3/SESSION ve banka saatleri ayrı hedef/otorite.
- **Repo:** \`ataullahturgut/sim3-automation\`, araştırma dalı \`research-gold-jan26-two-factor-confirmation-v4-20261013\`, [PR #128](https://github.com/ataullahturgut/sim3-automation/pull/128) **AÇIK, MAIN'E BİRLEŞMEDİ**. Üretime geçiş veya gerçek işlem emirleri için ayrı yetki gerekir. Açık depoya erişim anahtarı, lisanslı ham özel veri veya hesap bilgisi girilmez.
- **Bakım standardı:** Her yeni iş `FULL_HISTORY_DISCOVERY` ya da `AS_OF_DECISION_EVALUATION` olarak açık etiketlenir. Ana manifeste binlerce satırlık deney günlüğü yığma; amaç, olay ID/kullanılan yıl evreni, yöntem, sayısal/AI karşılaştırma sonucu, alternatif açıklamalar, test statüsü ve ayrı rapor linki kısa tutulur. Eski negatif sonuçlar ve veri açıklıkları korunur.
