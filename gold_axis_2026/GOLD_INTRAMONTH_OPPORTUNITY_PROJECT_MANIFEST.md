# GOLD INTRAMONTH — AMAÇ ODAKLI ANA PROJE MANİFESTİ

**Sürüm:** 2026-10-14 · **Alan:** Ekonomik olay örgüsüyle adaptif XAU/USD volatilite/büyük-hareket araştırması · **Statü:** AMAÇ VE BİLİMSEL KURALLAR TANIMLANDI; BU YENİ UYGULAMA HENÜZ ÇALIŞTIRILMADI/DOĞRULANMADI.

> **Projenin asıl amacı:** Belirlenen **karar anına kadar gerçekten erişilebilir** piyasa verileri ve haberleri çekmek, o andaki ekonomik gelişmelerin **olay örgüsünü** kurmak, geçmişteki **benzer ve karşıt** örneklerle karşılaştırmak, ardından gelecekte altının **ne büyüklükte hareket edebileceğini, oynaklık ve şok riskinin ne olduğunu** olasılıksal ve gerekçeli biçimde değerlendirmek. Kanıt yetersizse **BELİRSİZ** demek başarısızlık değil, doğru bilimsel karardır.

**Kapsam notu:** Kullanıcının paylaştığı ANFIS şeması **yalnız fikir örneğidir**; sabit model, katman sayısı, ağırlık, bulanık kural veya yazılım mimarisi seçilmiş değildir. Başarı belirli bir algoritmaya benzemekle değil **güvenilir, zamanda doğru ve sonradan yanlışlanabilir karar** üretmekle ölçülür. İlk karar **adaptif volatilite/risk değerlendirmesidir**; otomatik AL/SAT/TUT emri değildir.

## 1. Tam olarak hangi soruyu çözmek istiyoruz?

**"Bugün, bu saatte altın piyasasında ne oluyor? Hangi yeni olaylar ve ön koşullar bu durumu açıklıyor? Geçmişte benzer koşullarda sonrasında altın hangi büyüklükte ve türde hareket etmişti? Bugünün eldeki kanıtlarına bakarak sonraki belirtilen zaman aralığı için ne söyleyebiliriz?"**

- **Öncelikli çıktı:** Ufka göre beklenen **mutlak fiyat hareketi / realized volatility**, şok/sert hareket olasılığı, muhtemel büyüklük aralığı ve güven seviyesi. Bir fiyat hareketinin **başlaması, devamı, tersine dönüşü ve stabil kalması** birbirinden farklı sonuçlar olarak incelenir.
- **Yön (UP/DOWN)** ancak aynı vakalar üzerinde ayrıca bilimsel olarak doğrulanırsa ikincil çıktı olur. Volatilite = yön değildir; "yüksek risk" otomatik SAT değildir.
- **Ufuk başlangıçta tanımlanır:** 30 dakika, 2 saat, seans sonu, ertesi uygun seans, 1/3/5 işlem günü gibi pencereler **saat ve gerçek fiyat hedefiyle** ayrıdır. Bir tane keyfî ufuk bütün durumlara zorlanmaz; ufuk değiştirmek ayrı deney gerektirir.
- **Karar** bir olay-örgüsü + risk değerlendirmesi olabilir: "normal dalgalanma", "büyük hareket riski", "olası likidite şoku", "reversal olasılığı incelenmeli", "belirsiz". Etiketler **önceden tanımlı olasılık ve hata ölçümleriyle** anlam kazanır; olay adından sonuç uydurulmaz.
- **Başarı:** Sonradan görülmeyen tarihlerde saf tarihsel volatilite ve basit kıyasları aşabilmek, uygun kalibrasyon ve düşük yanlış alarm/kaçan şok oranı. Güzel haber hikâyesi tek başına başarı değildir.

## 2. Tek bir gün/karar anı için değişmez bilgi sınırı

Her değerlendirmede aşağıdaki kayıtlar başlamadan önce dondurulur:

| Kayıt | Şart |
|---|---|
| **Karar anı** | \`case_id\`, kesin \`origin_utc\`, Türkiye/New York yerel saatleri ve yaz saati; yalnız gün adı yeterli değil |
| **Veri erişimi** | Kaynağın ölçüm \`observed_at\` zamanı ile gerçek \`first_published_at / available_at\` **ayrı** |
| **Veri tanımı** | Sağlayıcı, spot/futures, BID/ASK/MID, 1m/15m/1h/gün, kontrat devri, kapanış ve tatil |
| **Hedef** | Hangi başlangıç-bitiş fiyatı, ileri mutlak log-getiri, realized-vol, kuyruk olasılığı ve şok eşiği |
| **Geçmiş olay havuzu** | Karar anından önce **tamamlanmış** ve o tarihe kadar kanıtları gerçekten erişilebilir vakalar |
| **Karşı kanıt** | Rakip nedenler, uyumsuz veriler, benzer haber olup şok olmayan günler |
| **Çıktı** | Kanıtlı ekonomi yorumu + şartlı volatilite/risk + belirsizlik/ABSTAIN + veri kalitesi |
| **Deney izi** | Sürüm, kaynak/vintage, önceden belirlenmiş kıyas, test dönemi ve sonradan gerçekleşen sonuç |

**PIT/as-of kuralı:** \`available_at <= origin_utc\`. Gelecek haber, henüz açıklanmamış CPI/NFP sürprizi, aynı gün kapanmamış GVZ/VIX, sonradan açıklanan aylık ETF raporu, haftalar sonra yayımlanan COT, geçmişe uygulanmış kaynak revizyonu **o an biliniyor gibi kullanılamaz**. Açıklama takvimi önceden bilinebilir ama actual/surprise ancak kamuya açıklandığında bilinir. Eksik veri \`MISSING/UNKNOWN\`; doldurulmuş hayalî değer yok.

**COT özel kural:** Pozisyon salı ölçülür, **normal** resmî yayın cuma **15:30 America/New_York**; 2023 ION ve 2025 kapanma gecikmelerinde resmî istisna tarihi geçerlidir. [CFTC yayımlanma ve 154-hafta zaman düzeltmesi](GOLD_COT_PUBLICATION_CLOCK_OFFICIAL_AUDIT_AND_RETROSPECTIVE_154_ORIGIN_RETEST_20261014.md). ETF aylık WGC verisi de yalnız **ilk yayımlandıktan sonra** kullanılabilir. CFTC \`d_opt_mm_net\` ham opsiyon kontratı değil, normalize **(combined net − futures-only net)** farkının değişimidir: [ham COT yanlışlama çalışması](GOLD_COT_RAW_LONG_SHORT_FALSIFICATION_2025_Q1_20261014.md).

**Geçmiş bilgi kütüphanesinin gizli riski:** 2026'da hazırlanmış 2023–2025 neden-sonuç raporlarındaki **sonradan öğrenilen neden etiketleri**, 2024 veya 2025 karar gününde mevcut değildir. Bir tarihsel örneği kullanmadan önce o gün itibarıyla hangi fiyat, olay, haber ve sonuçların gerçekten bilindiği **yeniden kurulur**. Sonradan tanınmış mükemmel dip/tepe ZigZag bölütü karar anında henüz bilinen "benzer olay" olamaz.

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

Benzerliği, **tarihsel vakaların gerçekleşen gelecek altın hareketine bakarak seçmek yasaktır**. Önce yalnız o tarihte bilinen sayısal piyasa/olay ön koşullarıyla eşleş; sonra olgunlaşmış geçmiş benzerlerin sonraki oynaklık dağılımını, **olaysız/ters kontrollere göre** karşılaştır. Gelecek fiyat yönünü kullanarak geçmiş neden sınıfı üretilmez.

**Aday mekanizma aileleri (tek seçim zorunlu değil):** ABD makro/Fed–faiz–USD; finansman/likidite ve margin-call; jeopolitik güvenli liman; tarife/ticaret; ETF/merkez bankası/COT/fiziki-altın; aşırı momentum/pozisyon çözülmesi; mali/siyasi belirsizlik; **çok etkenli veya UNKNOWN**. Aynı olayda tetikleyici, güçlendirici ve fiyat tepkisi birbirinden ayrılır. 2025 ilk çeyrek fizikî COMEX–Londra arbitrajı ve 2025 Nisan likidite çöküşü **farklı ekonomi mekanizmalarıdır**.

**Araştırma dosyaları:**
- [96 düzeltilmiş fiyat kaydı ve olay zamanlaması](GOLD_HISTORICAL_V2_NY17_FULL_REPLAY_96_EVENT_CAUSAL_REVIEW_AUTHORITY_20261014.md) · [96 kanıt ve haber indeksi](GOLD_HISTORICAL_CORRECTED_96_RECORD_EVENT_NEWS_CAUSAL_EVIDENCE_INDEX_20261014.csv).
- [Geçmiş 95 kayıt için **geçici** mekanizma sınıflandırması](GOLD_HISTORICAL_95_TRIGGER_CAUSE_REGIME_TAXONOMY_AUTHORITY_20261014.md) · [38 vakanın delil incelemesi](GOLD_HISTORICAL_38_CASES_DEEP_CAUSAL_RESEARCH_VERDICT_20261014.md). **Eski 95/53 istatistikleri güncel 96'ya otomatik aktarılmaz.**
- [2025 Ocak–Nisan beş ekonomik olay ve ETF/COT/metaller/COMEX](GOLD_2025_JAN_APR_FIVE_EPISODES_COT_ETF_METALS_MICROSTRUCTURE_CAUSAL_AUDIT_20261014.md).
- [Tarihsel neden–haber kontrol protokolü](GOLD_HISTORICAL_EVENT_CAUSAL_ATTRIBUTION_SCOPE_PROTOCOL_20261014.md). Bu önceki tarihsel alt projenin "NO FORECAST" kuralı **o çalışmanın** kapsamıdır; yeni risk-araştırma hedefinin ileride sınanmasını yasaklamaz.

## 5. 2 Ocak örneği: sistemden fiilen ne bekliyoruz?

**Örnek tarih:** \`2026-01-02\` (konuşmadaki "2 Ocak" örneği 2026 Ocak araştırma bağlamında yorumlanmıştır). **Kesin saat ve ufuk henüz seçilmediği için hiçbir risk sayısı, tahmin veya gerçekleşmiş karar burada üretilmiş değildir.** Ocak 2026 daha önce defalarca incelendiğinden yeni sonuç **kör dış örnek test** diye sunulamaz.

Örnek çalışma şöyle ilerlemelidir: Karar saati kayda geçer → sadece o saate kadar yayımlanmış altın/metaller, dolar/faiz, risk, enerji, ekonomik haber, ETF/COT ve bunların gerçek gecikmeleri alınır → piyasanın durumu ile haberin ekonomik aktarımı ayrı değerlendirilir → **2 Ocak 2026'dan önce bitmiş ve o gün itibarıyla bilinebilir** benzer/ters vakalar bulunur → aynı ufukta koşullu volatilite/büyük hareket olasılığı ve belirsizlik, geçmiş risk baz çizgisine göre değerlendirilir → sonuç daha sonraki gerçekleşene bakmadan kilitlenir → gelecekteki hedef olgunlaşınca hata ve neden-sonuç denetimi yapılır.

**Örnek kaydın geçerli fakat henüz boş çıktısı:** \`origin_utc=TBD; horizon=TBD; available_sources=TBD; observed_economic_state=NOT_EVALUATED; comparable_past_cases=NOT_EVALUATED; counterexamples=NOT_EVALUATED; candidate_causes=NOT_EVALUATED; volatility_forecast=NOT_ESTIMATED; P(abs_return>=predeclared_threshold)=NOT_ESTIMATED; confidence=UNKNOWN; decision=ABSTAIN_PENDING_DATA; future_actual=SEALED\`.

## 6. Bilimsel doğrulama — zorlama ilişki yerine ölçülebilir katkı

- **Önce ufuk/hedef/metrik dondurulur.** Adaptif volatilite için ileri mutlak log-getiri, realized volatility, önceden seçilmiş quantile/aralık veya ilk şok bariyerine varış riski ayrı ölçülür. Tahmin ufku veri çözünürlüğüyle uyumlu olmalı.
- **En az üç baz çizgisi:** tarihsel koşulsuz medyan/ampirik oran; önceki pencerenin EWMA/rolling realized-vol modeli; mevcut ayrı risk çalışmasında ölçülen dondurulmuş Ridge veya adaptif ölçek yaklaşımı. Gerekmedikçe karmaşık yöntem seçme.
- **Skorlar:** MAE/RMSE (hareket), quantile pinball loss ve kapsama, Brier/reliability (olasılık), risk alarmında recall/false alarm/missed-tail, rejim/tarih/uç olay altgrupları ve tahmin yok/ABSTAIN kapsaması. Aynı vaka veya örtüşen fiyat penceresi yüzlerce bağımsız örnek gibi sayılamaz.
- **Karşıt deney:** ekonomik olay bağlantısını çıkarınca başarı ne oluyor? Gerçek ilk yayın saati yerine hatalı gecikme kullanınca? Olaysız eşleşmiş günlerde? Önceki gerçekleşmiş altın hareketine kontrol ekleyince? Seçim/çoklu test ve rejim değişimi altında üstünlük devam ediyor mu? Başarısız ve olumsuz bulgular korunur.
- **Doğru değerlendirme:** Kaynak-vintage ve DST QA; ileri bir zamanda gizlenmiş hedef/firstprint; kronolojik **prequential** deneme; yalnız **olgunlaşmış geçmiş tahmin hatasıyla** risk ölçeği adaptasyonu. Daha önce incelenmiş 2023/24/25 veya Ocak 2026'ya yeni eşiği uyarlayıp "bağımsız OOS" deme. Ay-blok bootstrap, farklı yıllarda tekrar ve gerçek kaynak tutarlılığı gerek.
- **İstatistiksel ilişki ≠ nedensellik ≠ işlem başarısı.** Haberler, dolar ve faiz birbiriyle etkileşebilir; haber sonrası faiz hareketini kör kontrol ederek toplam nedensel etki ölçmeye çalışma. Her olayın **en az iki rakip açıklaması** ve uygun sessiz kontrol grubu tutulur.
- **Teknik yöntem açık:** ANFIS, bulanık mantık, olay analojisi, EWMA/GARCH, volatilite-ölçekleme, probabilistik yöntem veya hibrit ancak gerçek karşılaştırmada **ek fayda gösterirse** aday olur. Şimdiden model veya katman dondurulmadı.

**Önceki gerçek büyüklük çalışması:** [2026 adaptif risk araştırması](GOLD_EXECUTION_2026_CAUSAL_REGIME_AND_VOLATILITY_RISK_RESEARCH_AUTHORITY_2026-10-08.md), mutlak overnight hareketi için basit baseline'a göre dinamik Ridge risk ölçeği 2025'te MAE **%5,49**, 2026'daki **bağımsız olmayan** iki arşiv alt-kohortunda **%12,46 / %14,20** iyileşme raporladı; **2023–24'te sürekli fayda göstermedi**, DOWN/yön kabiliyeti ve bankada işlem geçerliliği **kanıtlanmadı**. Bu eski deney yeni olay-örgülü uygulamanın **çalıştırıldığı** anlamına gelmez; sadece karşılaştırma kaynağıdır.

## 7. Karar anı raporunun içeriği

Her çalışmanın nihai yanıtı doğal dille, sayılar ve kaynaklarıyla aşağıdaki soruları cevaplar:

1. **Karar anı ve mevcut veri:** Hangi gün/saat, hangi fiyat ve haberler gerçekten biliniyordu, neler eksikti?
2. **Olay örgüsü:** Ne olmuştu, hangi yeni bilgi ne zaman gelmişti, aktarım ve piyasa tepkisi hangi kanıtla uyumluydu?
3. **Benzer ve karşıt geçmiş:** Hangi geçmiş olayların hangi koşulları benziyor, farklar ve benzer haber–şoksuz kontroller neler?
4. **Adaptif volatilite sonucu:** Tanımlı ufukta beklenen hareket/riske ilişkin olasılık veya aralık, referans baseline, kalibrasyon ve belirsizlik.
5. **Karar ve gerekçe:** Risk değerlendirmesi; güven yetersizse **ABSTAIN**, risk yokmuş gibi kesin hüküm değil.
6. **Gelecekte doğrulama:** Gerçekleşen fiyat/şok ancak hedef olgunlaştığında açılır; hata, yanlış nedensellik, eksik veri ve önerilen yeni deney sürümü ayrıca belgelenir.

**Ayrı banka/işlem kapısı:** Türkiye saatli gerçek banka ASK/BID olmadan; alışta **%0,8**, satışta **%0,8** komisyon, banka makası ve gecikme ayrıca ölçülmeden volatilite/risk kararı otomatik AL/SAT/TUT olmaz. Daha önceki K100/H3/SESSION/aylık yön modelleri farklı hedeflerdir; kendiliğinden bu yeni sisteme taşınmaz.

## 8. Bugünkü durum, açık işler ve otorite

| Alan | 14 Ekim 2026 itibarıyla kanıtlı durum |
|---|---|
| Tarihsel altın olayları | **MEVCUT:** 42 düzeltilmiş V1 + 54 V2 fiyat kaydı; farklı olaylar arasında örtüşme var. 2023–25 haber/metal verisi ve 2025 Ocak–Nisan beş olay incelemesi |
| COT/ETF kaynak zamanı | **KISMEN DOĞRULANDI:** CFTC cuma yayını ve 2023/25 istisnaları; 2025 bazı ham long/short örnekleri. Tüm tatil haftaları ve bütün ETF günlük firstprint tam değil |
| USD/faiz/metallerin haberle eşsaatli aktarımı | **EKSİK:** DXY/2Y/10Y reel getiriler ve metal/COMEX-Londra veri-vintage tüm olaylarda aynı UTC ile doğrulanmadı |
| Geçmiş volatilite tahminleri | **AYRI EMPİRİK ÇALIŞMA VAR:** dinamik büyüklük ölçeği bazı yıllarda iyileşti; önceki yıllarda taşınabilirliği ve yön güvenilirliği yok |
| **Yeni amaçlı olay örgüsü + adaptif volatilite karar-ânı uygulaması** | **TANIMLANDI, HENÜZ GERÇEKLEŞTİRİLMEDİ / TEST EDİLMEDİ** |
| Al/sat ve gerçek banka yürütmesi | **BU AŞAMANIN SONUCU DEĞİL; ÜRETİM ONAYI YOK** |

**Bir sonraki meşru araştırma işi:** Kesin \`origin_utc\` ve değerlendirme ufkunu belirleyip bir örnek günü **geleceği kapatarak** çözümlemek; gerçek erişilebilir veri ve geçmiş karşı-vakaları almak; sadece risk büyüklüğünde basit baseline'a karşı değer katıyorsa devam etmek. Veri/kanıt yoksa güven düzeyi düşürülür. **Tek bir iyi 2 Ocak anlatısı sisteme başarı veya neden–sonuç ispatı vermez.**

### Belgeler ve sürüm yönetimi

- **Bu dosya**, yeni amacın ve araştırma çıktısının **tek güncel yönlendirme manifestidir**. 14 Ekim 2026 tarihli eski **5.190 satırlık TAM** ana metin değişmeden [TARİHSEL MANİFEST ARŞİVİNE](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST_FULL_HISTORY_SNAPSHOT_20261014.md) alındı. Önceki veri denetimleri, model sonuçları, başarısız testler, Ocak 2026 V1–V4 ve referans bağlantıları **kaybolmadı**. Arşivdeki eski "BINDING/NEXT/NO FORECAST" yalnız **kendi tarih/deney kapsamı** içindir.
- **Kaynak hiyerarşisi:** ilgili veri/kapanış saati/PIT sözleşmesi → dondurulmuş deney protokolü ve sayısal CSV/JSON → bilimsel sonuç/yanlışlama → bu amaç manifesti → tarihsel arşiv notları. Bir amaç değişikliği eski deney skorlarını değiştirmez.
- [Otorite/değişiklik ve eski modellerin ayrımı](GOLD_INTRAMONTH_MANIFEST_AUTHORITY_AND_CHANGE_CONTROL_20261013.md). Aylık H=1 [ayrı proje manifesti](GOLD_MONTHLY_PROJECT_MANIFEST.md) yetkisini korur. V1/V2 olay/38 kaynak, günlük/H3/SESSION ve banka saatleri ayrı hedef/otorite.
- **Repo:** \`ataullahturgut/sim3-automation\`, araştırma dalı \`research-gold-jan26-two-factor-confirmation-v4-20261013\`, [PR #128](https://github.com/ataullahturgut/sim3-automation/pull/128) **AÇIK, MAIN'E BİRLEŞMEDİ**. Üretime geçiş veya gerçek işlem emirleri için ayrı yetki gerekir. Açık depoya erişim anahtarı, lisanslı ham özel veri veya hesap bilgisi girilmez.
- **Bakım standardı:** Ana manifeste yeni binlerce satırlık deney günlüğü yığma. Her yeni işin *amacı, karar saati, cohort, sayı ve karşı ölçüm, sonuç, bilimsel sınırlama ve ayrı tam rapor linki* kısa kaydedilir. Eski negatif sonuçlar ve açıklanmamış veri açıkça kalır.
