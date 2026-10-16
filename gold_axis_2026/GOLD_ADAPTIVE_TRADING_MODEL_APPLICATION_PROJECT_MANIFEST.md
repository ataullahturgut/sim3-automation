# ALTIN — ADAPTİF MATEMATİKSEL MODEL VE UYGULAMA AYRIMI | TEK PROJE MANİFESTİ

**Belge kimliği:** `GOLD-ADAPTIVE-MODEL-APP-01`  
**Sürüm:** 1.0 · **Kayıt tarihi:** 16 Ekim 2026  
**Statü:** Algoritma araştırması için bağlayıcı çalışma sözleşmesi; **nihai algoritma kabul edilmiş / 2023–2025 eğitimi tamamlanmış / canlı işlem yetkisi verilmiş değildir.**  
**Depo:** `ataullahturgut/sim3-automation`  
**Güncellenen araştırma dalı:** `research-gold-core-timeless-selective-learning-20261016` — bu belge henüz `main` üzerinde birleştirilmiş proje politikası değildir.  
**Kapsam:** Matematiksel AL–TUT–SAT–yeniden AL **MODEL** projesi ve bu modelin sonuçlarını yöneten/gösteren **UYGULAMA** projesi. Eski olay araştırma projesinin yerine geçmez.

> **KISA BAĞLAYICI İLKE:** Önce olay, haber ve piyasa verilerinden **tarihten bağımsız ekonomik davranış kurallarını kendisi öğrenen MATEMATİKSEL CORE** geliştirilecek. CORE'un ekonomi ve net portföy kararı yeterliliği kanıtlanmadan yeni aylar, yeni model aileleri veya yeni uygulama ekranları açılmayacak. **UYGULAMA, CORE'a hizmet eder; CORE, uygulamaya hizmet etmek için şekil değiştirmez.**

---

## 1. Nereden geldik? — karıştırılmayacak projeler

### A. TAMAMLANMIŞ/DEVAM EDEN ESKİ ARAŞTIRMA: ekonomik olay bilgisinin hazırlanması

- `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` (**ANA-01**): olay temelli önceki araştırmanın hedef/yöntem manifesti.
- `OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md` (**OLAY-02**): tarihli haber, fiyat, çoklu-piyasa olayları, ilk yayımlanma ve kanıt/karşıt vaka araştırma arşivi.
- `adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md` (**ÖĞREN-03**): tarih ve tekil işlem sonucundan bağımsız ekonomik DNA, ORG01–ORG12, mekanizma ve P0–P5 olay evreleri, karşıt örnek ve geçersizleşme hipotezleri.
- `adaptive_volatility_learning/months/YYYY-MM/STATE.json` (**DURUM-04**): bu önceki araştırmanın aylık ilerleme ve aktarım kaydı.
- Eski ANA-01 **bu yeni MODEL+UYGULAMA projesini yönetmez**. Belgeler **silinmez, yeniden adlandırılmaz veya algoritmanın kendi başarısıymış gibi gösterilmez**. Başlangıçta modelin okuyabileceği **kanıt/aday-hafıza** kaynaklarıdır. OLAY–ÖĞREN'ü yeniden baştan sınıflandırmak projenin ana işi değildir.
- OLAY-02 içindeki olay ailesi veya ÖĞREN-03'teki tarihsiz kurallar **doğrudan onaylanmış al/sat komutu değildir**. 96 tarihsel fiyat kaydı ve ORG etiketleri doğrulanmış 96 ekonomik sebep sayılmaz. Eksik ilk haber saatleri ve karşıt kanıt seviyesi görünür kalır.

### B. SONRADAN KARAR VERİLEN YENİ PROJE: özgün matematiksel karar motoru

Kullanıcı ANN/ANFIS/LSTM/Double Q isimlerinden birini **aynen kurmayı değil**; bu yöntemlerin öğrenme, hafıza, rejim, belirsizlik ve adaptasyon avantajlarından yararlanarak **kendi ekonomik kural tabanını keşfeden ve güncelleyen özgün bir CORE** istedi. Başarı şartı, önceden yazılmış `if(price>threshold)` kuralları, takvim veya uzman kapıları değildir.

Daha önceki V11–V23, REHBER/SENTEZ/KAVİS/ATLAS, Ocak 2023 veya Ocak 2026 deneyleri **karşılaştırma ve başarısızlık arşividir**. Bunların hiçbirine sırf kodu yazıldığı veya bazı testleri geçtiği için `ACTIVE_CORE`, `APPROVED` veya gerçek yatırım performansı unvanı verilmez. V22/V23'teki tahmin katsayısı güncellemeleri, otomatik ekonomik kural keşfi ve başarılı strateji geliştirme **değildir**.

### C. UYGULAMA İŞ AKIŞI — matematiksel öğrenmeden ayrı

`apps/portfolio_guard_v1` tarihsel araştırma uygulamasıdır: kullanıcı arayüzü, geçmiş simülasyonları oynatma, sonuç raporu, yöntem sürümü ve denetim kayıtlarını gösterme. **Uygulamanın mevcut varlığı, yeni algoritmanın eğitilmiş olduğu anlamına gelmez.** Bu klasör tarihsel olarak V11–V23 model araştırma kodlarını da barındırıyor: bu bir **ayrıştırılması gereken teknik borçtur**, kabul edilmiş mimari değil.

---

## 2. İKİ AYRI İŞ PAKETİ: MODEL M ve UYGULAMA U

| Konu | **M — ADAPTİF MATEMATİKSEL MODEL** | **U — MODEL UYGULAMASI** |
|---|---|---|
| Ana amaç | Ekonomik mekanizmaları keşfet, deneyim kazan, kural tabanını öğren, düşük devirli net ekonomik karar ver | Modelin durumu, gerekçesi, hataları, ay raporları ve yeniden üretilebilir deneyleri göster |
| Girdi | As-of piyasa/haber/OLAY-02/ÖĞREN-03 kaynakları, geçmiş olgunlaşmış sonuçlar | Modelin versiyonlu çıktı API'si, imzalı kayıtları ve checkpoint başlıkları |
| Hesaplama | Özellik/olay kodlama, temsil ve kural keşfi, evre/süre, karar ve karşı-olgusal portföy öğrenimi | Sunum, rapor seçimi, filtre, geçmişi açma, planlı koşuyu çağırma, güvenlik/izlenebilirlik |
| Kalıcı hafıza | Gerçek **CORE state**: öğrenilmiş kurallar/weights/prototypes, optimizer, episodik hafıza, uzman güveni, pending labels | Kullanıcı tercihleri, gösterim, rapor indisi; core ağırlıklarının ikinci kopyası değil |
| Güncelleme sahibi | **Sadece M**; yalnız olgunlaşmış geçmiş veriyle / dondurulmuş adaptasyon protokolüyle | **U, M'nin karar katsayısını değiştiremez** |
| Bilimsel kabul | Ekonomik genelleme, karşıt olay, maliyet-net sermaye, büyük fırsat, yanlış alarm, kayıp riski | Doğru model/versiyon/API gösterimi, rapor bütünlüğü, veri izinleri, hata mesajları |
| Canlı banka yetkisi | YOK | YOK |
| Durum | Kural keşif + karar critic'i **henüz tamamlanmadı** | Araştırma/rapor uygulaması mevcut; yeni CORE ile entegre değil |

**Yeni kodun hedef sınırı (ileriye dönük, henüz taşınmış değildir):**
- Model çekirdeğinin kod alanı: `gold_axis_2026/adaptive_trading_core/` (yalnız kabul edilen CORE modülleri ve model testleri için; oluşturulmadan uygulamada ayrılmış gibi gösterilmez).
- Modelin ay verileri ve sürüm kayıtları: `gold_axis_2026/adaptive_trading_core/months/YYYY-MM/` (gizli/lisanslı ham veri GitHub'a dökülmez).
- Uygulama: mevcut `gold_axis_2026/apps/portfolio_guard_v1/` **yalnız ayrı U hattı**, araştırma uygulaması.
- Eski modeller ve kayıtlar mevcut yollarda korunur. **Kod taşıma/refaktör** ayrı test ve onay gerektirir; sırf dosyayı yer değiştirerek modeli iyileştirmiş sayma.

---

## 3. MODEL M'NİN DEĞİŞMEYECEK HEDEFİ

1. Başlangıç: **100 USD NAKİT**. **Modelde zorunlu banka işlem saati yoktur**; güvenilir ve karar anında erişilebilir piyasa gözlemleri üzerinde saatten bağımsız AL/TUT/SAT/NAKİT karar değeri öğrenilir. Her **AL** ve **SAT** bacağında %0,8 maliyet vekili uygulanır. Gerçek banka BID/ASK, spread, emrin o saatte iletilebilirliği ve slippage doğrulanmadıkça sonuç **araştırma simülasyonu**dur; gerçek emir yetkisi veya fiyat gerçekleşmesi iddia edilmez. Çift ücret yanlışlıkla iki kez kesilmez.
2. Modelin asıl işi **altının önemli ve işlem maliyeti sonrasında ekonomik değer taşıyan yükseliş/düşüş epizotlarını** başlangıç/devam/yorulma/bitme/yeniden giriş olarak anlamaktır. Her M15 oynama yeni bir işlem fırsatı sayılmaz. **Az, gerekçeli, büyük net avantajlı** AL/SAT; mevcut GOLD veya CASH pozisyonunu uzun süre TUTMAK doğal bir karardır.
3. Büyük hareketin başlangıcından ÖNCE tahmin şart değil; başladıktan sonra geriye kalan beklenen hareketin net değeri pozitifse işlem mümkündür. Pozisyondan çıkış ve yeniden giriş tek ekonometrik süreç olarak öğrenilir.
4. **Tarih, ay, yıl, geçmiş vaka ID'si, gerçekleşmiş tepe/dip veya haber başlığı pozisyon açan matematiksel kural OLAMAZ.** Zaman damgaları yalnız yayın/erişim, hedef olgunlaşması, işlem icrası, rapor ve dönem sırası içindir; olaydan beri geçen süre veya ekonomik evre süresi kullanılabilir. Tarih-adresli vaka geçmişinin kopyalanması algoritmik deneyim değildir.
5. Kalıcı öğrenme = yalnız tahmin denklemi katsayılarını güncellemek DEĞİL; ekonomik **koşullu kural** üretmek, destek/karşıt kanıt öğrenmek, kuralı bölmek/birleştirmek/zayıflatmak veya söndürmek, yeni olay koşullarında doğruluğunu ve yatırım kararına net katkısını ölçmek.
6. Kural biçimi tarih bağımsızdır: **ön durum → tetikleyici/olay karakteri → çapraz piyasa aktarımı → hareket rejimi/evresi → olası büyüklük, süre ve tersine dönüş → altın/nakit karar değeri**.
7. Model teknolojisi şu anda **nihai olarak kabul edilmiş değildir**. Adaptif bulanık/TSK kural sistemi, öğrenen temsiller/ANN, rejim geçişi, episodik hafıza, counterfactual actor-critic/Double-Q veya uygun hibritler kullanılabilir; seçim **bilimsel katkı testine** tabidir. İsim yazmak algoritmanın kurulduğu veya öğrenildiği anlamına gelmez.

### M mimarisi — 5 kapalı döngü, ayrı ayrı doğrulanacak

**M1. Kaynak/as-of katmanı:** Altın, gümüş, platin, paladyum, dolar, tahvil/faiz, S&P/Nasdaq, ETF/CFTC, volatilite, petrol, yayımlanmış haberler; her bileşende `event_time`, `first_available_at`, kaynak ve revision/vintage, missing mask. Hangi verinin mevcut olduğuna göre çalış; olmayanı veya ilk-yayını bilinmeyeni uydurma.

**M2. Ekonomik örüntü/kural keşfi:** ÖĞREN-03 mekanizma aileleri yalnız **başlangıç sözlüğü/hypothesis space**. Tarihli OLAY-02 vakaları kanıt/karşı-vaka örneği. Model ekonomik koşulların ortak matematiksel temsilini öğrensin; yeni kural adayları çıkarsın; kapsam (support), karşıt örnek, güven aralığı, geçerlilik bölgesi, kural bölünmesi/birleşmesi ve çürütme kayıtları tutsun. Kullanıcının tarihsiz öğrenmesi budur; salt `G01` dummy regresyonu yeterli değildir.

**M3. Hareketin yaşam döngüsü:** Önemli hareketin gelişmesi, kalıcılığı, beklenen kalan mesafe, geri çekilme ve sona erme dinamikleri; çok ufuklu getiri dağılımı, süre/hazard, rejimler arası geçiş, belirsizlik. Hareketin gelecekteki tamamlanmış bölümü tahmin anında bilinemez.

**M4. Net ekonomik karar/pozisyon öğrenimi:** CASH/GOLD ve AL/TUT/SAT/yeniden giriş seçeneklerinin gelecekteki **öz-finansmanlı net sermaye** üzerindeki toplam değerini öğren; satın almamanın fırsat maliyetini ve gereksiz al/sat maliyetini **birlikte** hesaba kat. Eylem `a` ancak

`DeltaV_t(a) = E[U(W_future | a, learned policy, z_t)] - E[U(W_future | HOLD, learned policy, z_t)]`

ve güven/risk koşulları gereği avantajlıysa uygundur. `U` portföy net log-serveti, aşırı düşüş riskini ve **gerçek işlem maliyetini** içerir. Yalnız kısa vadeli fiyat tahmini `> %1,6` kuralı M4 yerine geçemez; maliyet politika değerleme fonksiyonunun parçasıdır. İşlem sıklığının düşmesi hedeflenen *ekonomik sonuçtur*, tarihli günlük işlem kotası değil.

**M5. Adaptasyon/hata ve deneyim hafızası:** Tahmin ve karar zamanında kaydet; yalnız ufuk bittikten sonra hata, kaçırılmış fırsat, yanlış AL/SAT, gereksiz masraf, kural destek/çürütme, beklenen/gerçekleşen süre, alternatif mekanizma sonuçlarını hesapla. Olgunlaşmış sonuçlarla **M2 kural yapısı, M3 evre modeli ve M4 karar modeli** güncellensin. Ay sonu yalnız performans özeti değil **modelin neyi nasıl öğrendiğinin kanıtı** üretilsin.

**Bunlar mimari kabul ölçütleridir. Bugün M2/M3/M4/M5'in yukarıdaki tam hali kodlandı/eğitildi denmemelidir.**

---

## 4. ÇALIŞMA MARATONU — 36 ayın muhasebesi, otomatik tarama değil

### Sıra ve sınama tanımı

- **M eğitim başlangıcı = OCAK 2023.** Ocak ayının her yeni gözleminde o anda mevcut bilgi kullanılarak kural adayları ve kararlar ilerler. Olay/ÖĞREN arşivi geçmiş araştırma sözlüğü olarak okunabilir; fiyat sonucu daha sonra gerçekleşmişse anlık kararın önbilgisi sayılamaz.
- **İLK AKTİF AŞAMA yalnız Ocak 2023'tür.** Bu ayın büyük hareketlerinin olay başlangıç/aktarımı/bitimi, en az iki rakip ekonomik açıklama, kontrol günleri, modelin veriye as-of erişimi, tahminin ve işlem kararının düzeltilebilmesi, net PnL ve kaçırılan fırsatlar analizi yapılmadan Şubat'a geçilmez.
- Ocak bittiğinde gerçekten **öğrenilmiş CORE checkpoint** saklanır; **Şubat** bu state ile başlar, sıfır model başlatmak yasaktır. Sonraki aylar aynı disiplinle kronolojik ilerler. Her ayda modelin kural keşif/güven ve hareket-dinamiği öğrenmesi raporlanır.
- **Aralık 2025 sonunda** tüm eğitim zincirinin SON checkpoint'i, olay mekanizmalarının öğrenilmiş kural/prototipleri, optimizer/hafıza, rejim evresi, politika, maliyet/risk kalibrasyonu ve kaynak soy-ağacı bir **CORE_FROZEN_2025_12** şeklinde saklanır. 36 raporu birleştirip elle IF tablosu yazmak **bu değildir**.
- **Ocak 2026** eğitilmiş CORE ile sonraki dönemde sınanır; 2026 Ocak önceki projelerde görüldüğü için hiçbir sonuç `BLIND_OOS` diye sunulmaz. Gerçek hiç-görülmemiş dönem ayrıca ayrılmalıdır.

### İKİ BİLİMSEL KİP AÇIKÇA AYRILIR

**`DISCOVERY_FULL_ARCHIVE`:** 2023–2025 OLAY–ÖĞREN olaylarının tamamıyla ekonomik karakter taksonomisi/prototip araştırılabilir. Böyle bir arşivden öğrenilen model 2023 Ocak'a geri götürülürse bu **in-sample/açıklayıcı retrospektif karşılaştırmadır**, Ocak fiyat sonucunu bilmeyen başarılı model deneyi değildir.

**`STRICT_WALK_FORWARD`:** Ocak 2023'te başlayan ticaret ve adaptasyon performansı için o gün/yıl **sonrasında olgunlaşan** fiyat/olay etiketleri, kalibrasyon ağırlıkları veya karar hedefi modele **önceden yüklenmez**. İlgili gelecek bilgi yalnız ufku dolduğunda öğrenilir. İki kipin performansı tek başarı tablosunda harmanlanamaz.

Kullanıcının **tarihsiz ekonomik bilgi** talebi, **gelecekteki gerçek fiyat sonuçlarını geçmişte bildirme yetkisi değildir**. Tarihsiz *mekanizma kavramı* ile tarihli *hangi örnekte hangi sonuç gerçekleşti* ayrıdır.

### Her ayın kabul edilecek dosyaları (MODEL M)

Aylık kalıcı kök: `adaptive_trading_core/months/YYYY-MM/` (hedef düzen; eski raporlar taşınmış değildir).

1. `MODEL_SNAPSHOT_START.json` — günün/ayın başında gerçekten mevcut parametre/öğrenilmiş kural, portföy ve kaynak durumunun hash'i.
2. `EVENT_RULE_LEARNING.jsonl` — gözlem/ekonomik olay, çıkarılmış **genel kural adayı**, matematiksel koşulları, rakip açıklama, destek/karşıt/UNKNOWN, öğrenme güncelleme nedeni; tekil olaylar OLAY-02'de referanslı.
3. `DECISIONS.csv` — yalnız yeterli kanıtlı as-of kontrol, mevcut portföy, AL/TUT/SAT, karar değeri ve belirsizlik, mevcut fiyat/valid quote, masraf, kararın kullandığı olgun bilgi, kullanılan CORE sürümü. Tüm uygun kontroller korunur; **her kayıt emir değildir**.
4. `MATH_LEARNING_AUDIT.json` — hangi kurallar ortaya çıktı, kural bölünme/birleşme/sönme sayısı, tahmin/evre geçişi hataları, kural ablasyonları, işlem pişmanlığı, net NAV, en büyük düşüş, işlem sayısı, cash & pasif altın & önceki CORE karşılaştırması ve **maliyet sonrası büyük fırsat yakalama** metriği.
5. `MONTH_REPORT.md` — neden yükseldi/düştü sorularına **kanıt seviyeli**, rakipli, kaynaklı cevaplar; ayın ekonomik hareket epizotlarının kapsamı, gerçekleşmiş yanlış karar/fırsat analizi; ne öğrenildi/ne hala bilinmiyor.
6. `CORE_CHECKPOINT_END.json` — M2/M3/M4/M5 weights, öğrenilmiş kural/prototip, meta-öğrenme, optimizer moments, portföy CASH/GOLD/ons/sermaye, risk, henüz olgunlaşmamış **sonucu yazılmamış** görevler ve devamlılık hash'i. Sonraki ayın START'ı bunun kendisi olmalı.

**Checkpoint bütünlük koşulu:** `checkpoint(month_end) == snapshot(next_month_start)` (aynı veri dönemi/versiyon ve pending görevlerle). Tek metin rapor matematiksel öğrenme hafızası değildir.

---

## 5. UYGULAMA U — ALTIN MODELİNİ GÖSTEREN, MODELİ DEĞİŞTİRMEYEN ÜRÜN

Uygulama için mevcut başlangıç: `apps/portfolio_guard_v1`. Uygulama tarafı yapılabilirler:

- **Model durumu:** sürüm, `RESEARCH_ONLY`, hangi aya kadar gerçekten eğitildi, hangi verinin eksik olduğu, tahmin aralıkları, model uygunluğu, güncel portföy ve net maliyet.
- **Ay seç / ayı çalıştır:** yalnız **M'nin** onaylı motor çalıştırıcısına, kaydedilmiş `model_version` ve `checkpoint_id` ile çağrı; uygulama `AL` veya `SAT` eşikleri, Q/TSK katsayıları, model aileleri, test ayı sınırı veya olay rolü yazmaz.
- **Ekonomik karar görünümü:** öğrenilmiş kural ID'si, o anki koşul, olay kanıtı/alternatif açıklama, beklenen kalan hareket, model belirsizliği, neden BUY/SELL/HOLD/WAIT, ücret ve fiyat kaynak vintage.
- **Kural ve deneyim görünümü:** yeni/bozulan/birleşen ekonomik kurallar, karşıt örnekler, model eğitimi ve sürüm değişiklik kayıtları; onaylanmamış kural `VALIDATED` olarak renklendirilmez.
- **Aylık rapor ekranı:** matematiksel aylık kontrol defteri, sermaye eğrisi, fırsat maliyeti, cash ve buy-hold, kural kalitesi, kaynaklık.
- **Araştırma izni:** hiçbir model performansı garanti edilmez; banka emirleri ve kişisel banka hesap bilgisi erişimi **bu kapsamda YOK**.

Uygulama **asla** yeni ayı, yeni algoritma modelini, başka varlığı, bir haber kaynak entegrasyonunu veya bir koşuyu kendi başına devreye sokamaz. Onaylı CORE sürümünü yüklemek dışında karar üretimi U'ya ait değildir. UI tasarımının kolay ilerlemesi **bilimsel öğrenme tamamlandı** sonucunu doğurmaz.

---

## 6. KAPSAM KİLİDİ — BENİM BAŞKA YOLLARA SAPMAMI ENGELLEYEN BAĞLAYICI KURALLAR

Aşağıdaki ihlaller bir sonraki araştırma adımını **DURDURUR**:

**K1 — Tek proje, iki iş paketi.** Her işin başında mutlaka `WORKSTREAM=MODEL` veya `WORKSTREAM=APP`, `CURRENT_STAGE`, `EXPECTED_OUTPUT`, `SOURCE`, `PASS/FAIL` tanımlanır. Bir konuşmada kullanıcı model soruyorsa ekran/uygulama geliştirmesine geçilmez; uygulama soruyorsa yeni matematiksel model icat edilmez.

**K2 — Önce mevcut karar ve manifest.** Kod veya araştırma öncesi **bu dosya** ve ilgili MODEL checkpointi, önceki başarısızlık raporu, varsa açık iş listesi okunur. Eski ANA-01/OLAY-02/ÖĞREN-03 bilgi kaynağıdır; yanlışlıkla MODEL yönetim belgesi ilan edilmez.

**K3 — Yeni dal/yeni sürüm keyfî değil.** Kullanıcı açıkça yeni bir alternatif model araştırması veya yeni Git dalı istemedikçe **başka dal açılmaz**. Geçerli araştırma dalında çalışılır; ilgili PR veya korunan ana dal birleştirilmez. **V24/V25...** isim çoğalması veya yeni ANN/kapı/algoritma ancak ölçülmüş eksikliği çözen açık hipotez + ön kayıt + başarısız olma ölçütü + kullanıcı onayıyla mümkündür. Bu manifesti oluşturmak yeni bir modelin onaylandığı anlamına gelmez.

**K4 — Modelin hedefini küçük probleme indirgeme.** Sadece 3h fiyat tahmini, günlük yön başarısı, ANN doğruluğu, RSI eşiği, seri Q katsayı güncellemesi veya banka saatlik kontrol sayısı **ana başarı ölçütü olarak tek başına kabul edilmez**. Ekonomik kural öğrenimi, hareketin ömrü ve net AL/SAT kararı birlikte ele alınır.

**K5 — Ay sırasını atlama.** Kullanıcı Ocak 2023 kapsamı verirken Şubat 2023–Aralık 2025 otomatik koşusu açılmaz. **Önce Ocak** için gerçek ekonomik kural keşfi ve strateji değerlendirmesi bitirilip rapor/checkpoint denetlenir. Sonraki ay ayrı ilerleme kararıdır. 36 ayın hızlı simülasyonu, 36 aylık ekonomik öğrenme olarak ilan edilemez.

**K6 — Verileri seçmeci kullanma.** Yalnız NQ eklemek, GPR veya haber etiketlerini verisiz kesin mekanizma saymak ya da kullanıcı istemeden XAU dışı fırsat projesine geçmek yasak. Çapraz piyasalar yalnız **altını açıklayan girdiler** olabilir; hangi veri ve neden gerekli olduğu kayda alınır, kaynak saat/vintage denetlenir.

**K7 — Bilimsel dürüstlük.** Gerçek öğrenme, parametre/hafıza değişimi ve karar politikasına etkisi ayrı raporlanır. Eksik haber veya diğer metal as-of olmayan kaynağı tamamlanmış veriymiş gibi gösterme. Fiyat örüntüsü ekonomik nedensellik kanıtı değildir; `UNKNOWN` korunur. Geleceği kullanarak optimum al/sat sadece **ex-post oracle benchmark** olabilir, modelin canlı öngörüsü sayılamaz.

**K8 — Kullanıcının banka ekonomisi.** Alış %0,8, satış %0,8. Seyrek ama anlamlı işlem, cash-versus-gold, yanlış çıkış ve kaçırılan yükseliş birlikte ölçülür. Sırf sıfır işlemle zarar etmedik diye başarı ilan edilmez; sırf çok işlemle hareket yakalandı diye maliyet görmezden gelinmez.

**K9 — Eski işleri koruma.** Eski OLAY/ÖĞREN, 2023–2025 olay kütüphaneleri, Ocak 2026 arşivleri, yıllık tahmin ayrı modelleri ve ana dal kullanıcı açıkça istemedikçe **silinmez, taşınmaz, yeni raporla üzerine yazılmaz**. Yeni araştırma eklentisi eski performans iddialarını geriye dönük değiştiremez.

**K10 — Uygulama yeni bilimsel otorite değildir.** UI veya `package.json` testlerinin yeşil olması, modelin ilk ekonomik kuralını öğrenmiş olduğunu kanıtlamaz. Model science gate ve app acceptance gate ayrıdır.

**K11 — Durum eksiksiz ve açık.** Her yanıt sonunda gerekiyorsa şu ayrım zorunlu: `TASARIM / KODLANDI / GERÇEK VERİDE ÇALIŞTI / EKONOMİK KURAL ÖĞRENDİ / ÇOK AYLI TAŞINDI / BAĞIMSIZ TEST / UYGULAMAYA ENTEGRE EDİLDİ`. Kanıtı olmayan basamak atlanmaz.

**K12 — Değişiklik onay yolu.** Bu belgedeki amaç, dönem, maliyet, model-app rol dağılımı, eğitim/test veri sınırı, risk hedefi veya yeni dal/ana algoritma ailesi değiştirilmeden **önce kullanıcı kararı** ve `CHANGE_DECISION.md` (önerilen değişiklik, gerekçe, etkilenen dosyalar, korunacak deneyler, onay ve commit) gereklidir. Basit hata düzeltmesi bilimsel karar mantığını değiştirmiyorsa ayrı `TECHNICAL_FIX` kayıtlanır. Aynı ayın sonuçlarına bakıp eşiği değiştirerek geri-çalıştırma yeni kör başarı olamaz.

---

## 7. İKİ AYRI KABUL KAPISI

### `MODEL_GATE`
- Ocak 2023'te gerçekten **makine tarafından türetilen/uyarlanan genel ekonomik kural tabanının** kod ve sayısal kanıtı var mı? Tarih/kural şablonu dışarıdan verilmişse açıkça işaretlendi mi?
- Kuralın destekleyen, ters ve olaysız örnekleri ile kaynak/vintage kalitesi kaydedildi mi?
- Kural ve hareket evre tahmini **yalnız olgunlaşmış** sonuçlarla güncelleniyor mu?
- Kural değişimi karar değerinde görülebiliyor mu? Karşılaştırma `without economic rules` ve `with economic rules` var mı?
- Portföy kararları maliyet-net ve seyrek mi? Kazanç, DD, turnover, kaçırılan önemli hareketler raporlandı mı?
- Ocak raporları, başlangıç ve bitiş state'i, bütün işlem kararı satırları Git/denetim artefaktında mı?
- Düzgün değilse `MODEL_GATE=FAIL`; **Şubat'a geçme / başarı iddia etme**.

### `APP_GATE`
- Uygulama model API'sini sürüm ve checkpoint ile **aynen** çağırıyor mu, sonucu değiştirmeden gösteriyor mu?
- İzin verilmeyen veri, bozuk/eksik quote, eğitim eksikliği ve NOT-VALIDATED durumları doğru mu?
- 100 USD/banka ücreti/bakiye/gold miktarı/doğru tarih farklılığı/hata durumlarında UI ile kayıt tutarlı mı?
- Rapor/karar/öğrenme state'ini sadece doğru modelden çekiyor mu?
- Hayırsa `APP_GATE=FAIL`; modelin matematiksel kabulü etkilenmez, yalnız ürün entegrasyonu bekler.

---

## 8. BUGÜNKÜ SOMUT DURUM (16 EKİM 2026)

| Bileşen | Kanıtlanan mevcut durum | Henüz tamamlanmayan |
|---|---|---|
| OLAY-02 / ÖĞREN-03 bilgi kaynakları | Olay arşivi ve tarihsiz DNA hipotezleri mevcut | Tüm vakalarda ilk haber, nedensellik ve güvenilir zaman eşleşmesi yok |
| V11–V23 araştırma yöntemleri | Çok sayıda algoritma/karşılaştırma/teknik test mevcut; V22/V23 Ocak araştırması | Kapsamlı ekonomik kural keşfinin M2–M5 olarak çalışması |
| KAVİS V0 prototipi | 15dk altın ve sınırlı makro girdilerle gecikmeli tahmin ağırlığı güncelliyor; Ocak 2023'te **100 USD CASH, 0 AL/SAT** | Ekonomik kural çıkarma, yaşam döngüsü ve portfolio critic |
| Model yürüyüşü | 2023 Ocak için prototip raporu/checkpoint kayıtlı | Asıl M modelinin **Ocak ayı MODEL_GATE geçmedi**; Şubat'a geçilmez; 2023–2025 eğitim tamamlandı denemez |
| Uygulama | Tarihsel Portfolio Guard V1 araştırma arayüzü ve rapor altyapısı var | Yeni M CORE ile sürüm-imzalı bağ ve uygulama için `APP_GATE` henüz yok |
| 2026 Ocak değerlendirmesi | Daha önce başka algoritmalarla retrospective araştırma yapıldı | 2025 sonunda eğitilmiş bu yeni CORE ile test yok; kör OOS iddiası yok |

**Önemli:** Bu manifest, araştırma protokolü ve teknik ayrımın kaydıdır. Algoritma eğitimi veya test sonucu değildir. Dosya yaratmak, M2–M5 eksiklerini gidermiş sayılmaz.

## 9. İLK VE TEK SONRAKİ İŞ

**`WORKSTREAM=MODEL` · `CURRENT_STAGE=OCAK_2023_EKONOMIK_KURAL_KESFI_CORE`**

Mevcut OLAY-02/ÖĞREN-03'ten kaynakları **read-only** al; Ocak 2023'ün fiyat ve çapraz-varlık/önceden yayınlı haberlerini as-of denetle; sayısal ekonomik kural keşif (M2) + hareket evresi (M3) + net pozisyon-değeri öğrenimini (M4/M5) **aynı CORE içinde kodla ve test et**. Ay raporları, gerçekten öğrenilmiş kural tabanı ve checkpoint çıkmadan **Şubat'a, başka model ailesi deneyine, yeni araştırma dalına veya uygulama ekrana geçme**. Kullanıcı U iş paketini ayrı olarak istediğinde uygulamayı çalış.

**DEĞİŞMEZ YÖNLENDİRME:** `ECONOMIC_RULE_DISCOVERY → PHASE/TRAJECTORY_LEARNING → NET_PORTFOLIO_POLICY_LEARNING → MONTHLY_CORE_MEMORY`. Modelden kopuk sinyal kapıları/ekranlar bu zincirin yerini tutamaz.

---

## 10. S1 Geliştirme kaydı — 16 Ekim 2026 (durum, amaç değişikliği değil)

- [MODEL inşa aşamaları ve kabul kapıları](adaptive_trading_core/BUILD_STAGES_20261016.md): S0–S6 ve U1; ekonomik kural öğrenimi, epizot yaşam döngüsü, net portföy critic, aylık handoff sırası.
- [S1 ilk uygulama bilimsel denetimi](adaptive_trading_core/STAGE_S1_FIRST_IMPLEMENTATION_AUDIT_20261016.md): [çekirdek JS](adaptive_trading_core/adaptive_rule_discovery_s1.js), [8 sözleşme testi](adaptive_trading_core/adaptive_rule_discovery_s1.test.js) ve GitHub Actions doğrulaması.
- **KANIT STATÜSÜ:** `S1=KODLANDI+SENTETİK_TEST_PASS`; `S1_GERÇEK_2023_EKONOMIK_KURAL=NOT_VERIFIED`; `MODEL_GATE=FAIL`; `S2/S3/S4=NOT_STARTED`; `UYGULAMA_ENTEGRASYON=NOT_STARTED`. Bu kayıt Ocak 2023 için başarılı AL/SAT veya gerçek piyasa öğrenmesi iddia etmez.
- **Tek sıradaki iş:** OLAY-02/ÖĞREN-03 salt-okunur kaynaklarından S1 girdi kanıtı ve ilk-yayın/UTC/normalizasyon denetimi; Ocak 2023 ekonomik örüntüleri üzerinden gerçek kural güncellemelerinin bilimsel denetimi. Yeni branch/model/UI yok.
---

## 11. Ocak 2023 S1 gerçek piyasa denetimi — 16 Ekim 2026 (ÖNEMLİ NEGATİF KANIT)

[Detaylı sayısal rapor](adaptive_trading_core/JAN2023_S1_RECONSTRUCTED_MARKET_AUDIT_20261016.md) · [S0–S1 tarihli kaynak sorgusu](adaptive_trading_core/JAN2023_RECONSTRUCTED_ASOF_S1_INPUT.sql) · [MODEL-only asof adaptörü](adaptive_trading_core/replay_reconstructed_jan2023_s1.js).

**Gerçek durum:** Aynı dalda S1 kaynak/öngörü/etiket güvenliği hataları düzeltildi; prototip öğrenimine olgunlaşmış karşıt sonuçlarla koşullu `ruleSplit` eklendi. **Teknik sentetik regresyonları geçti**. Read-only Neon Ocak 2023 rekonstrüksiyonundan **102 tam gözlem, 338 çok ufuklu olgunlaşmış etiket, 8 deneysel prototip, 0 işlem** elde edildi. 8 prototipin yalnız 4'ü dört saatlik ufukta 8+ sonuç taşıyor. Doğrulanmış ekonomik neden, ilk yayın/vintage ve getiriyi artıran yatırım politikası **henüz yok**.

**Negatif bilimsel sonuç:** 70 olgunlaşmış 4s yön karşılaştırmasında S1 `31/70`, önceki olgun veriyle hesaplanan sabit UP taban oranı `35/70`; Brier `0.271422` vs `0.256330` (S1 **daha kötü**). Sırf `noveltyDistance` değiştirmek aynı ayda 1/2/8 kural üretir, bağımsız kalibrasyon verisi olmadan sonuç optimize etmek yasak. **`MODEL_GATE=FAIL`**, `S1_SCIENCE_GATE=FAIL`, `S2/S3/S4=NOT_STARTED`, `TRAINED_2023_2025=false`, `APP_GATE=NOT_APPLICABLE`.

**Zorunlu sonraki adım değişmiyor:** Aynı S1 ekonometrik kural motorunda OLAY-02/ÖĞREN-03 read-only ve ilk-baskı kaynaklarını gerçek-time ekon kanıtlara bağla; CME sürekli sözleşme ileri bilgi riski, gümüş serisi eksikleri, kontrol-vakalar ve yapısal kuralın genellemesi doğrulanmadan yeni sürüm/dal/ay/AL-SAT politikası ve ekran açma. Araştırma performansı yatırım tavsiyesi değildir.

---

## 12. S1 ekonomik kanıt/karşıt örnek giriş katmanı — 16 Ekim 2026

**Belge:** [Ocak 2023 OLAY–ÖĞREN ekonomik kanıt ve negatif kontrol denetimi](adaptive_trading_core/JAN2023_ECONOMIC_EVIDENCE_AND_CONTROLS_AUDIT_20261016.md). **Kod:** [economic_evidence_s1.js](adaptive_trading_core/economic_evidence_s1.js) ve [testleri](adaptive_trading_core/economic_evidence_s1.test.js).

OLAY-02/ÖĞREN-03 orijinal kaynakları **read-only** kullanılarak 7 aile, 12 ORG, 38 derin vaka hipotezi ve Ocak 2023'teki 4 makro kayıt/2 ortak yayın anı ekonomik bilgi kaydı oluşturuldu. İlk gerçek haber yayınını sertifikalayan tarihli kayıt yok: 38 vaka 0 sertifika, 2 makro küme `firstprintVerified=false`. **Hiçbiri onaylı S1 haber veya AL/SAT girdisine dönüştürülmedi.**

102 piyasa gözleminden, 2 açıklama için aynı-UTC saatli/daha önce bilinen piyasa durumlarına göre kontrol eşleştirmesi yapıldı; 68 olaysız kontrolün 33'ü UP, 35'i UP dışı. 6 Ocak olay sonrası 4s +%0,3486 ve kontrol ortalaması +%0,2437; 12 Ocak +%0,4711 ve kontrol ortalaması +%0,2473. Her iki seçilmiş kontrol grubu da pozitif olduğundan **ekonomik haberin altın yükselişine neden olduğuna veya kuralın bağımsız öngörü sağladığına kanıt yoktur**. Bu yalnız retrospektif olay-kontrol araştırmasıdır; causal signal veya öğrenilmiş net işlem politikası değildir.

**Model durum kilidi:** `ECONOMIC_EVIDENCE_RESEARCH_LINK=YES`, `CERTIFIED_PIT_EVENT_SIGNAL=NO`, `MODEL_GATE=FAIL`, `S2/S3=NOT_STARTED`, `UYGULAMA=UNCHANGED`; ekonomik araştırma için ayrı branch/model/sinyal kapısı açılmadı. Başka aya atlama yok. Bir sonraki gereklilik ilk baskı ve vintage ile doğrulanmış ekonomik veri + çapraz-piyasa saat kanıtı, ardından yalnız eğitimin izinli saatinde S1 kural öğrenimine giriş ve karşıt/olaysız kontrollere karşı bağımsız denetim.


---

## 13. S1 PIT ekonomik veri kabulü + öğrenim/ablasyon köprüsü — 16 Ekim 2026

**Kayıt:** [Ocak 2023 S1 PIT ekonomik öğrenim ve bilim kapısı](adaptive_trading_core/JAN2023_S1_PIT_ECONOMIC_LEARNING_GATE_20261016.md) · [PIT-gated mevcut CORE bağlantısı](adaptive_trading_core/economic_pit_learning_s1.js) · [5 yeni test](adaptive_trading_core/economic_pit_learning_s1.test.js) · [BLS ilk-vintage kontrol satırları](adaptive_trading_core/JAN2023_BLS_ORIGINAL_RELEASE_VINTAGE_AUDIT_20261016.csv).

- Yeni model/branch/app veya manuel yön kuralı açılmadı; aynı S1 çekirdeği için source-vintage şartlı EVENT özellikleri ve aynı CORE ile ekonomik-on/off prequential ablation koşucu kodlandı.
- Resmî BLS 6 Ocak NFP 223 bin / UNEMP %3,5 / AHE %0,3 ile 12 Ocak TÜFE -%0,1 ilk açıklama arşivinden karşılaştırıldı; **4/4 initial actual içerik doğrulandı**. Ancak resmî embargo 13:30 UTC **ilk gerçek ulaşma zamanı sertifikası değildir**; contemporaneous actual erişim logu ve ön-yayın konsensüs vintage hâlâ yok.
- Yeni katmanda iki açıklama dalgasında **0/4 PIT-sertifikalı bileşen**, **0 gerçek EVENT özelliği**; 6 Ocak üç bileşen aynı yayım, 12 Ocak CPI tek yayım. Sentetik complete-PIT kaydı CORE'a öğrenen özellik olarak aktarılabilir; mevcut gerçek arşiv bu yetkiyi almadı.
- Yeni 5/5 eklenti sözleşme testi izole JS çalışma ortamında PASS; aynı dalda [var olan CORE GitHub Actions workflow'u](../.github/workflows/gold-core-timeless-v0-tests.yml) yeni testleri de çalıştıracak şekilde güncellendi. **GitHub Actions sonucunun ayrıca okunması gerekir; teknik test real alpha başarısı değildir.**
- Değişmeyen bilimsel durum: **MODEL_GATE=FAIL**, VERIFIED_ECONOMIC_RULE=NOT_PROVEN, S2/S3/S4=NOT_STARTED, AL_SAT=NOT_IMPLEMENTED, APP=UNCHANGED. Ocak 2023 Neon'dan salt okunur alınan **102 gerçek piyasa gözlemiyle yeni çift-CORE koşusu çalıştırıldı**: 70/70 karşılaştırılabilir tahmin, ekonomik-on ve ekonomik-off **31/70** doğru, Brier **0,271422/0,271422**, **8/8 aynı prototip**, **0/4 gerçek PIT olay kabulü**. Eski tarihsel basit UP baseline 35/70, Brier 0,256330. Gerçek üstünlük kanıtlanmadı; lisanslı veri GitHub'a yazılmadı.
- Tek izinli ilerleme: ilk erişim ve konsensüs gerçek PIT kanıtını bul/doğrula; aynı-UTC çapraz piyasa/missing/roll denetimini tamamla; sonra aynı S1 ekonomik-on/off ayrışmasını bağımsız negatif kontrollerde test et. Şubat'a veya alternatif algoritmaya geçme.


---

## 14. Ocak 2023 S1 — kontrollü tarihli-yayın araştırması ve ekonomi kuralının gerçek destek testi (16 Ekim 2026)

**WORKSTREAM=MODEL, STAGE=S1, STATUS=SCIENTIFIC_FAIL.** [Bu araştırmanın sayısal raporu](adaptive_trading_core/JAN2023_S1_RESEARCH_VINTAGE_ABLATION_AUDIT_20261016.md) · [yayımlanma kaynağı/varsayım JSON](adaptive_trading_core/JAN2023_RESEARCH_PUBLICATION_ASSUMPTIONS_20261016.json) · [reproducible özel-veri replay runner](adaptive_trading_core/replay_jan2023_economic_research_s1.js) · [öğrenim birimi testleri](adaptive_trading_core/economic_research_vintage_s1.test.js).

- **Önceki ilk-erişim katı şartı model araştırmasını kilitlemesin, doğrulama zorunluluğunu da kaybetmeyelim:** 6 Ocak 05:00 UTC Reuters, açıklama öncesi NFP 200k/AHE +%0,4/UNEMP %3,7 beklentilerini; 11 Ocak 21:05 UTC Reuters, 12 Ocak CPI için %0,0 beklentisini tarihli olarak destekliyor. İlk açıklama *actual* BLS ilk arşivlerinden alındı. Bunlar tarihli yayım kanıtı ama **gerçek 2023 tick-firstprint/first-receipt logu değil**. STRICT_WALK_FORWARD bu gerçek kanıt yokken hâlâ 0/4 sertifikalı; yeni **DISCOVERY_FULL_ARCHIVE** alanında sadece araştırma varsayımı olarak 60/120/180 dakika gecikmeyle girdiler kabul ediliyor.
- **Bir bilimsel algoritma hatası düzeltildi:** Event özellikli prototipler artık event olmayan sonraki barel ile asla birleştirilemiyor, böylece olay kuralının destek sayısı olaysız fiyat etiketleri ile sahte büyütülemiyor. Olay alt modeli 8 bağımsız olgun etikete ulaşmadığında ekonomi tahmini hazır değil; araştırma skoru piyasa-only fallback'i açıkça sayar. Çok sayıda satır veya dört makro bileşen, dört bağımsız olay diye sunulmuyor.
- Neon'dan salt-okunur **102 gerçek Ocak 2023 çıpası** ile aynı matematiksel CORE üzerinde gerçek ekonomik-on/off yeniden koşuldu: varsayımsal 60 ve 120 dk haber erişiminde **2 yayım dalgası, 4 bileşen, 2 event prototipi**, fakat her prototip yalnızca **1 anchor / 1 olgun 4s etiketi** taşır. **0/2 olay ufkunda hazır ekonomik tahmin**. Olay saatlerindeki iki fallback Brier her iki kolda 0,347222; yön her iki kolda 1/2.
- Bütün Ocak fiyat tahminleri 60/120 dk ekonomik-on **30/70**, Brier **0,272335**; market-only **31/70**, Brier **0,271422**; önceki basit tarihsel UP baseline **35/70**, Brier **0,256330**. 180 dk gecikmede olay kabul edilmedi, iki model **31/70** ve **0,271422** ile aynı kaldı. Gerçek economic-alpha veya kazanç kanıtı **yok**.
- Yeniden üretilebilir runner ve yeni kaynak/testleri aynı dalda kayıtlı, ham/lisanslı fiyat repo dışına taşınmadı. **26/26** mevcut S1 ve yeni JS testleri izole yürütme ortamında geçti; GitHub Actions adımı güncellendi ancak bağımsız başarılı son CI koşusu teyidi bekliyor.
- **Değişmeyen yön:** S1 ECONOMIC_RULE_DISCOVERY; sonra S2 yaşam döngüsü, S3 net maliyetli CASH/GOLD critic, sonra 2023 Ocak MODEL_GATE ve checkpoint, ancak bundan sonra sonraki aylar. OLAY-02/ÖĞREN-03 immutable hipotez kaynağı; yeni algoritma/dal/uygulama yok. MODEL_GATE=FAIL, S2/S3/S4=NOT_STARTED, TRADE_ACTIONS=0, APP=UNCHANGED. DISCOVERY_FULL_ARCHIVE retrospektif sonuçları kesinlikle STRICT_WALK_FORWARD Ocak 2023 bağımsız öngörü başarısı olarak ilan edilmez.


---

## 15. S1 bağımsız ekonomik yayın dalgaları / karşıt olay / arşiv genelleme denetimi — 16 Ekim 2026

**WORKSTREAM=MODEL; CURRENT_STAGE=S1; MODEL_GATE=FAIL; UYGULAMA=UNCHANGED.** [Ayrıntılı 69 olay araştırma ve negatif kontrol raporu](adaptive_trading_core/S1_ARCHIVE_INDEPENDENT_EVENT_DISCOVERY_AUDIT_20261016.md).

**Tek CORE ve araştırma ayrımı korunur:** Ayrı canlı karar modeli yaratılmadı. [Araştırma sorgusu](adaptive_trading_core/independent_event_research_query_s1.js), [S1 bağımsız olay koşullu öğrenme doğrulayıcısı](adaptive_trading_core/independent_event_learning_s1.js), [özel veriyle tekrar üretilebilir koşucu](adaptive_trading_core/replay_independent_event_learning_s1.js) ve [yeni testler](adaptive_trading_core/independent_event_learning_s1.test.js) mevcut dalda oluşturuldu. OLAY-02/ÖĞREN-03 read-only; S1 üretim CORE'u veya uygulama başka sürüme geçirilmedi.

- 2023–2025 makro ledger: 139 reconstructed pair-complete NFP/AHE/UNEMP/CPI bileşeni, **69 bağımsız yayım dalgası** (NFP/AHE/UNEMP aynı dalga). Read-only Neon XAU M15 üzerinden tam saat ve 4s etiket şartlarıyla **57 ölçülebilir yayım**, **12 eksik/kesik kaynak nedeniyle reddedildi** (29 employment, 28 CPI).
- Yayın +60dk sonrası başlayan 4 saatlik getiri (ilk reaksiyon değil) ve aynı UTC saatli, haber ±24h dışındaki 4 negatif kontrol: **228 kontrol eşleşmesi, 178 benzersiz fiyat çıpası (50 yeniden kullanım)**. Kontroller sonuç yönüne göre seçilmedi; tekrar kullanım bağımsızlık iddiasını sınırlar.
- S1 **DISCOVERY_FULL_ARCHIVE research-only** ekonomik-sürpriz-vs-no-surprise **eşit karşılaştırma** (aynı yayın ailesi, aynı geçmiş örnekler, sabit 8 komşu ve haber öncesi/sonrası saat ayrımı): **41 farklı olgun yayım** üzerinde ekonomi açık **20/41** doğru, Brier **0,295443**; aynı yayın ailesi ve yalnız önceki altın hareketi karşılaştırması **19/41**, Brier **0,281137**; basit geçmiş yayın-aile UP oranı Brier **0,257885**. Yön başarısının 1 olay artması, olasılık hatası ve baseline üstünlüğü nedeniyle gerçek performans kanıtı değildir.
- Olay düzeyi açıklayıcı Brier iyileşmesi **−0,014306**, 1.000 bootstrap %95 **[−0,0541; +0,0231]**, sıfırı içerir. Kontrol vaka karşıt örnekleri yaygındır. Ekonomik sürpriz tek başına anlamlı/genellenebilir alpha olarak **desteklenmedi**. Verinin source/vintage niteliği RETROSPECTIVE_UNVERIFIED_LEDGER olduğu için 2024–2025 kronolojik skorları dahi bağımsız firstprint-validated out-of-sample **değildir**.
- Resmî 2023 Ocak ilk yayın actual kaynaklarını kontrol etme işlemiyle, 2023–2025 bütün reconstructed ledger'ın point-in-time sertifikasyonu karıştırılmaz. Kullanılan piyasa fiyatları lisanslı ham satırlar GitHub'a yazılmadı; sadece toplulaştırılmış audit.
- **Bilimsel sıra kilitli:** S0 tam kaynak/PIT ve kesintisizlik açık, S1 koşullu ekonomik genelleme açık, MODEL_GATE=FAIL. S2 harekete yaşam döngüsü, S3 fee-net GOLD/CASH critic, S4 Ocak 2023 tam 15dk walk-forward, S5 ay/ay öğrenme, S6 bağımsız koşu **henüz başarılı aşamaya geçmiş sayılmaz**. Şubat 2023 strict koşusuna atlama / yeni branch / UI yok.
- **Bir sonraki S1 geliştirmesi:** olaysız/karşıt yayım örneklerine karşı XAG, USD, faiz, oynaklık, ilk fiyat tepkisi ve durasyon koşullarını **as-of ve evidence-grade** sözleşmeyle ekle. Tam bilim kapısı geçmeden modelin kârlı olduğuna karar verme.

**İzlenebilir kayıt:** WORKSTREAM=MODEL | STAGE=S1 | INPUT=69 distinct publication clusters + XAU M15 read-only Neon + reconstructed ledger | WRITTEN=independent event learner audit/query/replay/tests | SCIENCE=FAIL | NEXT=condition features with PIT validation; rerun control ablation; gate unchanged.


---

## 16. S1 eksik entegrasyonun kapatılması: Makro ve karşıt örnekler doğrudan TEK ADAPTİF CORE'da — 16 Ekim 2026

**WORKSTREAM=MODEL · CURRENT_STAGE=S1 · SCIENTIFIC_MODEL_GATE=FAIL.** [Gerçek 2023–2025 CORE entegrasyonu, prototip ve performans denetimi](adaptive_trading_core/S1_ACTUAL_CORE_ECONOMIC_INTEGRATION_AUDIT_20261016.md) · [Birebir aynı CORE ile çift kol gerçek öğrenme ve yeniden koşum](adaptive_trading_core/replay_macro_waves_in_existing_core_s1.js) · [7 yeni entegre test](adaptive_trading_core/replay_macro_waves_in_existing_core_s1.test.js).

**Bir önceki önemli metodolojik eksik giderildi:** Bölüm 15'teki 69 olay/41 sıralı araştırma deneyi yardımcı yakın-komşu modülde yapılmıştı ve ASIL adaptif CORE'un bunu öğrendiği iddia edilemezdi. Bu defa aynı [adaptive_rule_discovery_s1.js](adaptive_trading_core/adaptive_rule_discovery_s1.js) üzerindeki `create/observe/rules` akışına gerçek ekonomik yayın dalgaları, açıklama öncesi XAU 1s durum, ilk yayın sonrası 60dk XAU tepkisi ve olaysız/karşıt kontrol çıpaları **doğrudan** aktarıldı. Gerçek XAU M15 fiyatı tam 4s olgunlaşmadan ekonomik rule outcome güncellenmedi; piyasa-only ve ekonomik-on aynı CORE kodunu aynı tarih/çıpalarda çalıştırdı. Başka ANN/KNN ana algoritması, ayrı branch veya APP açılmadı.

- Neon 2023–2025 salt-okunur: **69** benzersiz makro açıklaması; **57** gerçek tam XAU 4s örneği, **12** eksik; 228 kontrol atamasından **178** benzersiz olaysız çıpa; ortak 4s ankraj kuralıyla CORE'a giren **164** kontrol çıpası. Toplam **221** gerçek olgunlaşmış 4s eğitim etiketi; aynı anda her iki kolda hazır olan **196** karar-öncesi tahmin ve bunlardan **40** bağımsız gerçek makro yayım.
- Asıl adaptif matematiksel CORE kendi öğrenme hafızasında **3 ekonomik prototip** üretti: istihdam ana kuralında 28 olgun bağımsız açıklama sonucu (12 UP / 16 DOWN), CPI ana kuralında 28 (16 UP / 12 DOWN), ayrı istihdam uç örneğinde 1 (0 UP / 1 DOWN). Bu sayılar kural istatistiğinin **gerçekten** olgunlaştığını, ancak her grubun hem UP hem DOWN taşıdığını ve ekonomik olayın koşullu mekanizmasının henüz başarılı ayrışmadığını gösterir.
- **196 karşılaştırılabilir tahminde:** ekonomi açık **101/196** doğru, Brier **0,255918**; sadece piyasa **95/196** doğru, Brier **0,253149**; geçmişe kadar olgun UP oranı basit referans **0,253028** Brier. **40 ekonomik olayda:** ekonomi açık **21/40** doğru, Brier **0,264965**; piyasa-only **17/40**, Brier **0,256879**. Ekonomik sürpriz dört daha fazla yön doğruluğuna rağmen Brier'da **daha kötü**. Ekonomik olaylara özel bootstrap ortalama Brier üstünlüğü **−0,008086**, açıklayıcı %95 **[−0,045366; +0,026942]** — sıfır içeriyor, gerçek alpha gösterilmiyor.
- Araştırmada kullanılan 2023–2025 macro ledger firstprint/consensus **RETROSPECTIVE_UNVERIFIED_LEDGER**, true live `VERIFIED_PIT=NO`; bunun için CORE'un source katmanına açıkça *daha düşük kanıt sınıfı* eklendi ve **yalnız `DISCOVERY_FULL_ARCHIVE`** içine alındı. `STRICT_WALK_FORWARD` kaynak ve gelecek bilgi kapısı değişmeden kaldı. Makro bilgisi 60dk sonra hazır **varsayıldı**; gerçekten ilk ulaştığı saat sertifikalanmadı. Piyasa fiyatlarının ilk edinim anı da tam gerçek-zaman PIT değildir, sadece tarihsel tamamlanmış bar rekonstrüksiyonu. Ham/lisanslı XAU fiyatları veya research checkpoint GitHub'a yazılmadı.
- **Test:** yeni 7 CORE entegrasyon sözleşmesi (gerçek delayed labels, illegal early release, sıkı PIT, duplicate kontrol, corrupt price/lineage, missing case) geçti; eski diğer testlerle birlikte **41/41** S1 regresyon testi izole JS harnessinde PASS. GitHub Actions test adımı var, fakat CI başarı durumunun ayrı doğrulanması gerekiyor.
- **Tekrar üretim:** Güncellenmiş [özel-veri SELECT generator](adaptive_trading_core/independent_event_research_query_s1.js) ve `node replay_macro_waves_in_existing_core_s1.js PRIVATE_ROWS.json PRIVATE_MACRO_LEDGER.csv`, yalnız toplu rapor + hashed runId üretir. Özel SQL çıktısı **gerçek anchor/due fiyatlarını içerir, asla repoya ekleme**.

**Sonraki S1 bilim kapısı:** gerçek haber öncesi dollar/rates/silver cross-asset ve yayın sonrasındaki ilk reaksiyon/reversal **origin-safe** sınırlarda, ekonomik aile içindeki karşıt UP/DOWN sonuçları ayırabiliyor mu? CORE'un koşullu kural istatistiği başka bağımsız olaylarda baseline'ı aşıyor mu? Hayırsa S1 başarı değil. Mevcut Neon CME SI/NQ/ZN/CL gerçek H1 kaynakları saptandı; *continuous futures hindsight roll/PIT* doğrulanmadığı için sessizce güvenilir sinyal ilan edilmedi.

**Önceki manifest ve proje şartları değişmedi:** `MODEL_GATE=FAIL`, `S1_REAL_ECONOMIC_RULE_READY=NOT_PROVEN`, `S2/S3/S4=NOT_STARTED`, `TRADE_POLICY=NOT_IMPLEMENTED`, `APP=UNCHANGED`, Şubat 2023 strict ay-koşusuna geçiş yok. Gerçek piyasa üstünlüğü doğrulanana kadar kodlama/öğrenme altyapısı PASS olması finansal model PASS değildir.


**§16 tamamlayıcı denetim — çapraz piyasa yalnız araştırma kipi:** 2023–2025 gerçek Neon saatlik CME NQ (57/57), CL (57/57), ZN (51/57), SI (10/57) bağımsız makro yayım çıpasında tamamlanmış/önceden bilinebilir H1 pencere koşuluna göre bulundu. Opsiyonel as-of CME özellikleri aynı mevcut S1 CORE'un her iki karşılaştırma koluna bağlandı. **194 karşılaştırılabilir tahmin:** ekonomi açık **99/194**, Brier **0,256040**; yalnız market **99/194**, Brier **0,251404**. **38 gerçek makro olay:** ekonomi açık **19/38**, Brier **0,266061**; yalnız market **17/38**, Brier **0,251126**. Ekonomi açıklayıcı Brier üstünlüğü **−0,014935**, release-level %95 bootstrap **[−0,042748; +0,009971]**, genellenebilir fayda kanıtlamadı. CME sürekli sözleşme ex-post roll/PIT kanıtı eksik; SI çok eksik. Eski XAU-only koşusu 196/40 örnek kullandığı için iki yapılandırmanın skorlarını birebir ekonomik üstünlük karşılaştırması yapma. SQL üretici ve aynı CORE koşucusuna isteğe bağlı `--cross-assets` eklendi. **44/44** ilgili test izole JS yürütmesinde geçti, GitHub Actions CI bağımsız statüsü teyit edilemedi. **MODEL_GATE=FAIL; SCIENTIFIC_S1_ACCEPTANCE=NOT_PROVEN; S2/S3/S4=NOT_STARTED.**


---

## 17. S1 kısa karar — olgunlaşmış örneğe göre koşullu ekonomik kural deneyi (16 Ekim 2026)

**WORKSTREAM=MODEL; CURRENT_STAGE=S1; MODEL_GATE=FAIL.** [Aynı CORE'da yeni koşullu tahmin deneyi ve olumsuz gerçek sonuç](adaptive_trading_core/S1_ACTUAL_CORE_ECONOMIC_INTEGRATION_AUDIT_20261016.md#6-tek-odaklı-koşullu-öğrenme-deneyi--mevcut-core-yeni-model-değil-16-ekim-2026).

Ana `adaptive_rule_discovery_s1.js` içine tek isteğe bağlı `LOCAL_MATURED_EXAMPLES` yöntemi kondu. Yalnız geçmişte **gerçekten olgunlaşmış** ekonomik/prototip karşıt örneklerini (k=12, 8 gözlem shrinkage önceliği) kullanır. Aynı aile içindeki farklı işaretleri ayırt edebilme **sentetik** testi başarılı (UP olasılıkları 0,80/0,20; eski prototip 0,50/0,50). **Gerçek 2023–2025** iki ayrı pazar bağlamı deneyi ise başarılı değil: yalnız XAU 196 tahminde yeni koşullu ekonomik-on Brier **0,259068** vs mevcut ekonomik-on **0,255918**; XAU+CME 194 tahminde yeni koşullu ekonomik-on **0,266928** vs mevcut **0,256040**. Eşit örnekte ekonomi-off kolu ve ekonomik olaylar için de Brier üstünlüğü gösterilemedi. Bu olumsuz sonuç sonradan hiperparametre optimize etmek için kullanılmadı; `forecastMethod=PROTOTYPE` **varsayılan kaldı**. Mevcut 46/46 S1 teknik test izole JS ortamında PASS; CI başarı bağımsız olarak teyit edilmedi.

**Güvenilir ekonomi alpha/güvenli AL–SAT halen yok.** `LOCAL_CONDITIONAL_CODE_PASS` farklıdır `REAL_S1_SCIENCE_PASS` (FAIL). S2/S3/APP/2023 strict yürüyüşü açılmadı; başka branch/model yok. Sıradaki gerekli iş yalnız yeni küçük ayar denemek değil: gerçek olaylarda önceden gözlenebilen ve ilk erişimi doğrulanan ekonomik rejim verilerini genişletip, önkayıtlı bağımsız sonraki gözlemlerde ekonominin fiyat-only basit baseline'a katkısını göstermek.


---

## 18. Onaylı yöntem değişikliği — S1 tamamlanmadan S2 geliştirmesine geçiş (16 Ekim 2026)

**Kullanıcı kararı:** `S1_REAL_ECONOMIC_RULE_READY=NOT_PROVEN` dururken S2 fiyat hareketi yaşam döngüsü üzerinde kod ve araştırma deneylerine geçilebilir. Bu, S1’in başarısızlığını düzeltmez, üstünü örtmez veya `S1_GATE=PASS` demez. **S2_DEV=AUTHORIZED; S2_SCIENTIFIC_GATE=PENDING**. S1 araştırmasıyla tekrar eden küçük parametre testlerinde vakit harcanmayacak.

**Tek algoritma sözleşmesi:** S2, mevcut GOLD-ADAPTIVE-MODEL-APP-01 matematiksel CORE ile birlikte çağrılan **yaşam döngüsü alt mekanizmasıdır**; başka araştırma projesi / ayrı karar veren AL-SAT algoritması değildir. İlk S2 alt yapısında yalnız tamamlanmış ve as-of XAU M15 fiyatı kullanılabilir: `START/CONTINUE/PULLBACK/END/REENTRY` gözlem durumu, bağımsız epizot tanıma, yaş/duration ve bitiş hazard tahmini, geleceği görmeyen 4s etiket olgunlaşması, veri boşluklarında sağ-sansür. Haberin sonradan derlenmiş ekonomik metadata'sı S2’ye canlı özellik olarak taşınmaz.

**Geliştirme ≠ bilimsel kabul:** S2 teknik testleri, geçmiş veride 2023–2025 araştırma koşusu, kalibrasyon ve basit süre/hazard baz çizgisi ayrı raporlanacak. Bir bileşenin üretilmiş olması yatırım getirisi veya OOS avantajı anlamına gelmez; retrospective `DISCOVERY_FULL_ARCHIVE` gerçek ilk-vintage `STRICT_WALK_FORWARD` yerine konmaz. 2023 Ocak tam strateji yürüyüşü/S3 bilimsel kabul/S5 handoff/U1 canlı uygulama bu izinle otomatik açılmaz. Banka makası (%0,8 her yön) değişmez. OLAY-02/ÖĞREN-03 salt-okunur.

**Güncel proje durumu:** S1 bilimsel kabul açık (FAIL); **S2 mühendislik geliştirmesi başladı, bilimsel kabul açık**; S3/S4/S5/S6/U1 henüz kabul edilmedi. Bu bölüm önceki sıra kilidinin sadece **S2_DEV başlangıç koşulunu** açıkça değiştirir; diğer bilim kapılarını kaldırmaz. [Geliştirme aşamaları](adaptive_trading_core/BUILD_STAGES_20261016.md).


---

## 19. S2 DEV ilk gerçek yürüyüş — fiyat yaşam döngüsü ve bitiş hazard (16 Ekim 2026)

**Kullanıcı onaylı §18 esnetmesi uygulandı.** [S2 tam denetim raporu](adaptive_trading_core/S2_PRICE_LIFECYCLE_PILOT_AUDIT_20261016.md) · [epizot ve hazard öğrenme CORE bileşeni](adaptive_trading_core/adaptive_phase_lifecycle_s2.js) · [tek S1+S2 CORE birleşimi](adaptive_trading_core/adaptive_market_core_s1_s2.js) · [salt-okunur piyasa replay](adaptive_trading_core/replay_phase_lifecycle_s2.js) · [dokuz S2 testi](adaptive_trading_core/adaptive_phase_lifecycle_s2.test.js).

- **S2_DEV başladı ve ilk kod gerçek veride çalıştı, S2 bilimsel kabul edilmedi.** S1 ekonomik sürprizlerinden bağımsız, tamamlanmış XAU M15'e dayanan tarafsız/dairesel olmayan basit trend/retracement evre adayları (START/CONTINUE/PULLBACK/END/REENTRY), kapanmış/sansürlü epizot hafızası, tamamlandıktan sonra öğrenilen durum/istikamet-koşullu 4s bitiş riski ve gecikmiş etiketli kıyaslama kuruldu. Bu evreler **mühendislik koşullu tanımlarıdır**, ekonomik nedenle veya AL/SAT kararıyla karıştırılmayacak. Yapısal eşik kalibrasyonu 2023–25 sonuçlarına göre sonradan optimize edilmedi.
- **Gerçek Neon 2023–25:** 67.919 XAU M15 satırı / **67.653 tam** / 266 reddedilen; **1.223 tamamlanmış** epizot, **341 sağ-sansürlü**; medyan süre 3s 45dk; **1.596** zamanında olgunlaşmış karşılaştırılabilir 4s bitiş tahmini. 2023–24 ve 2025 iki farklı XAU kaynak kimliği taşıdığı için kaynak değişiminde **sansür** zorunlu, fiyat/epizot yapay olarak birleştirilmedi.
- **S2 Brier 0,241926**, yalnız önceden bitmiş epizotların geçmiş süre risk dağılımı baz çizgisi **0,243622**. Küçük iyileşme **+0,001696**, epizot bazlı 1.000-bootstrap açıklayıcı %95 **[−0,000320; +0,003733]** ve **sıfır dahil**. Bu, bağımsız OOS başarı/alpha değil, 2023–25 arşivinde retrospektif research. `S2_SCIENCE_GATE=PENDING`.
- **Tek model doğrulaması:** 2023 Ocak'taki 1.903 tam M15 barı mevcut S1 kural motoruna S2'nin as-of evre/süre/yön/drawdown özellikleriyle birleştirilmiş girildi; S1 CORE **101 anchor, 94 olgun sonuç, 2 öğrenilmiş prototip** üretti. İki alt mekanizma birlikte çalıştı; S1'in ekonomik genellemesi hâlâ bilimsel kabul edilmiş değil.
- **Test:** Önceki 46 S1 + yeni 9 S2 = **55/55** izolasyonlu JS regresyon testi başarılı; workflow'a yeni S2 CI adımı eklendi, gerçek Actions çalışması henüz ayrıca doğrulanmadı. Ham fiyatlar veya gerçek lisanslı piyasa checkpointleri depoya yazılmadı.
- **Açık kalacak bilim şartları:** epizot ground-truth ve hazard kalibrasyonu, çakışmayan bağımsız olaylar, 4s–2hafta çapraz ufuklar, geleceği görmeyen fiyat-vintage, mümkünse yeni gerçek veri, bağımsız baseline/ablation. S2 hazırlığı S1 bilim FAIL'ini silmez ve **S3, S4, S5, S6, APP bilimsel ya da canlı kabulünü otomatik açmaz**. AL–TUT–SAT=NOT_IMPLEMENTED; banka maliyeti %0,8/her yön değişmedi.

**WORKSTREAM=MODEL | S1_SCIENCE=FAIL | S2_DEV=INITIAL_IMPLEMENTATION_DONE | S2_SCIENCE=PENDING | S3_S4_S5_S6_U1=NOT_ACCEPTED | TRADES=0.**


---

## 20. S2 çoklu ufuk gerçek veri denetimi — 4s/1g/3g/1hft/2hft (16 Ekim 2026)

**WORKSTREAM=MODEL | S2_DEV=FIVE_HORIZONS_IMPLEMENTED | S2_SCIENCE_GATE=PENDING | S1_SCIENCE=FAIL.** [Ayrıntılı araştırma denetimi](adaptive_trading_core/S2_MULTIHORIZON_LIFECYCLE_AUDIT_20261016.md).

Mevcut `adaptive_phase_lifecycle_s2.js` (tek S1+S2 CORE'a bağlanan aynı bileşen) 4s, 1gün, 3gün, 1hafta, 2hafta **bitiş ve devam olasılığı** üretmek, her ufku ayrı olgunlaştırmak, gerçek END görüldüyse ufuk süresi dolmadan pozitif olarak bilmek, aksi halde tam ufuk boyunca doğrulanmış devamı beklemek ve aradaki M15/kaynak boşluğunda **etiketi sağ-sansürlemek** üzere geliştirildi. Bir ufukta yalnız END etiketi varsa `estimable=false`; bunlar yüksek yön doğruluğu sayılmaz. Sansürlü epizot, geçmişte gerçekten sağ kaldığı ufuk dışındaki END/CONTINUE etiketlerine zorla yazılmaz. S2 araştırma checkpoint sürümü `KAVIS_S2_CAUSAL_EPISODE_MULTIHORIZON_20261016`; eski tek-ufuk checkpointleri geçerli sayılmaz.

**2023–2025 gerçek salt-okunur Neon:** 67.919 XAU M15 satırı / 67.653 tam; **1.223** tamamlanmış, **341** sağ-sansürlü mikro epizot. **4s:** 1.763 değerlendirilebilir tahmin, 1.137 END / 626 CONTINUE, model Brier **0,218717**, koşulsuz süre referansı **0,219215**; iyileşme **0,000499**, epizot-kümeli %95 bootstrap **[−0,001493; +0,002431]**: **üstünlük kanıtı yok**. Bu yöntem, erken gözlenmiş END'leri artık sonraki veri boşluğunda kaybolmadan skorladığından eski 1.596 tahmin/0,241926 koşusuyla aynı değerlendirme kümesi **değildir**.

**1 gün, 3 gün, 1 hafta, 2 hafta:** her biri için 1.632 skorlanabilir kaydın tümü zaten erken bitmiş kısa epizotlardan **END=1**. **0 doğrulanmış CONTINUE** ⇒ **`UNESTIMABLE`**. Bu kritik tespit, 4 saatlik fiyat hareketi epizotlarını uzatarak haftalık ekonomik şok yaşam döngüsü öğrenilemeyeceğini gösteriyor. Skorlanan tüm olumlu sonuçlar için görünen küçük hata, gerçek devam/bitiş tahmin başarısı **değildir**. Gelecekte günlük/haftalık ayrı zaman ölçekli epizot/oturum süresi tanımı (planlı hafta sonu kapanışı ≠ veri kaybı) geliştirilmeli ve yeniden sınanmalı; veri yetersizliği sabit yönde kural üretme gerekçesi değildir.

**Güvenlik ve denetim:** Önceki 46 S1 ve yeni/önceki 12 S2 test = **58/58 izole JS test PASS**. GitHub Actions workflow'da S2 test adımı mevcut; sunucu koşusunun sonucuna dair bağımsız kanıt henüz yok. S1'in başarısız ekonomi alpha durumu, S3 net %0,8/her-yön ücretli AL–TUT–SAT kapısı, S4 katı Ocak 2023, S5/6 ve uygulama otomatik açılmadı. Yalnız aynı matematiksel projede S2 geliştirme çalışması ilerletildi.

**NEXT (tek net teknik eksik):** günlük ve haftalık **gerçek yavaş epizotların** planlı kapanışları bilinerek kronolojik tanımlanması; mikro START/END etiketlerini 2 haftalık bitiş başarısı gibi çoğaltma. `S2 SCIENCE` hâlâ kabul edilmedi.


---

## 21. S2 yavaş günlük/haftalık hareketlerin as-of öğrenimi — 16 Ekim 2026

**WORKSTREAM=MODEL | SINGLE_ADAPTIVE_CORE | S2_SLOW_DEV=IMPLEMENTED_AND_REAL_DATA_TESTED | S2_SCIENCE=PENDING | S1_SCIENCE=FAIL | S3_TRADE_NOT_IMPLEMENTED.** [Gerçek günlük/haftalık S2 denetimi](adaptive_trading_core/S2_SLOW_DAILY_WEEKLY_LIFECYCLE_AUDIT_20261016.md).

§20'deki 4s mikro-epizotların 1g–2hafta için tek sınıflı kalması sebebiyle, **aynı S2/CORE sistemine** tamamlanmış günlük işlem-seansı ölçeğinde bir trend ve epizot bileşeni [eklendi](adaptive_trading_core/adaptive_slow_lifecycle_s2.js). S1'e fiziksel olarak [mevcut tek CORE köprüsü](adaptive_trading_core/adaptive_market_core_s1_s2.js) ile as-of bağlandı; S2 ayrı AL-SAT politikası, ayrı proje/branch veya APP değildir. Slow state kapatılmış günün UTC22 araştırma kesiminden **önceki M15 kararına aktarılmıyor**. Normatif resmî altın settlement ve güncel firstprint/vintage sertifikası **yok**, bu yalnız arşiv araştırmasıdır.

**Ne öğrendi:** 10 seanslık geçmiş fiyat/oynaklık tabanlı yönsel mikro-dışı trend başlama, devam, düzeltme, yeniden giriş, bitiş fazları; yalnız kapanmış eski uzun epizotlardan 1/3/5/10 **işlem-seansı** içindeki bitiş riski `P(END)` ve devamı `1-P(END)`. Her ufuk bağımsız gecikmiş outcome; hafta sonu (cuma→pazartesi) planlı kapanış olarak kabul edilir, ancak bilinmeyen hafta içi eksik/tatil seansı, kaynak geçişi veya örnek sonu **sağ-sansür** edilir. Resmî borsa takvimi yokken tatil tam açık veri gibi gösterilmez.

**Gerçek salt-okunur Neon 2023–2025:** [tekrar üretilebilir seans SQL](adaptive_trading_core/S2_SLOW_SESSION_AGGREGATE_2023_2025.sql) kaynaklı **774 aday / 609 kalite kapısını geçen** seans; 2023 **118/257**, 2024 **246/259**, 2025 **245/258**. **165 reddedilen**; Mart–Temmuz 2023 özellikle kısa/kısmi günlük fiyat arşivi nedeniyle reddedildi. Araştırma amaçlı **99** kabul edilmiş seansın en çok 2 kısmi *intraday* barı vardı, **son fiyat barı daima tam** ve diğer kalite/boşluk şartları sağlandı; tam PIT kalitesi iddia edilmedi. **12 tamamlanmış uzun epizot (medyan 9 işlem seansı)**, **10 sansürlü**, **7 tarih aralığı kırığı**, 2025 kaynak değişimi nedeniyle **1 kaynak kırığı**.

**Ufkuna göre gerçek tahmin ve bilim kararı** (tümü 2025'te oluşabilen olgun ve karşılaştırılabilir veri; değerlendirme yılları yeni OOS değildir):
- **1 işlem seansı:** 24 skor / 1 END + 23 CONTINUE; Brier S2 **0,050526** vs basit geçmiş süre **0,047538** → model daha kötü.
- **3 işlem seansı:** 21 skor / 3 + 18; S2 **0,139235** vs baseline **0,141383** → çok küçük açıklayıcı fark, kanıt değil.
- **5 işlem seansı:** 17 skor / 5 + 12; S2 **0,214835** vs baseline **0,214398** → daha kötü.
- **10 işlem seansı:** 9 skor / 5 + 4; S2 **0,272305** vs baseline **0,248663** → daha kötü.

Tüm ufuklar artık 4s kısa epizottan farklı şekilde hem END hem CONTINUE üretse de, **her ufukta bağımsız iki sınıfı yeterince öğrenme şartı sağlanmadı**, `estimable=false`; epizot kümeleri yalnız 2–5 olduğundan bootstrap CI yok. Dolayısıyla **S2_SCIENTIFIC_GATE=PENDING / ALPHA_NOT_PROVEN**. Başarısızlıkta minReady/keyfî eşik düşürülmedi; 2023–25 hindsight hiperparametre avına dönülmedi.

**Kod/test:** yavaş S2 bileşeni + eski S1/S2 CORE kompozisyonu + [özel veri replay](adaptive_trading_core/replay_slow_lifecycle_s2.js) + 9 yeni güvenlik testi. Eski 58 + yeni 9 = **67/67 izole JS test PASS**. GitHub Actions test adımı eklendi, bağımsız CI başarı statüsü görülmedi. Ham/lisanslı altın fiyat satırı veya özel model checkpointi repoya yüklenmedi. S3 net banka komisyonu %0,8/her yön ve 2023 Ocak strict yürüyüşü henüz başlatılmadı.

**Sonraki doğru adım:** gerekli veri/lisans ve seans kalite boşluğunu gidermek; tarihsel bağımsız uzun epizot ve karşıt örnek sayısını yükseltmek. S2 bilim onayı olmadan bitiş hazard'ı gerçek ticaret sinyali ilan edilemez; S1 ekonomik öğrenmenin başarısızlığı S2 mühendislik izniyle silinmez.


---

## 22. S2 alternatif arşiv ve yavaş hareketlerin gerçek tekrar ölçümü (16 Ekim 2026)

**WORKSTREAM=MODEL; STAGE=S2; DEVELOPMENT=PASS; SCIENCE=PENDING.** [Alternatif veri kaynağı ve karşıt sonuç denetimi](adaptive_trading_core/S2_ALT_SOURCE_QUALITY_AUDIT_20261016.md) · [read-only kaynak SQL](adaptive_trading_core/S2_SLOW_EV_DUKA_SESSION_AUDIT_2020_2025.sql). Önceki HistData 2023-25 **609 uygun seans/12 tamamlanmış uzun hareket** için eksikleri tahminle doldurmak yerine ayrı EVTradingLabs-Dukascopy-türevli 2020-25 BID/ASK M15 **tek kaynak** arşivi incelendi. 1.549 adaydan **1.500** kaynak/quote/gap kriterleriyle kabul edildi; **35 uzun hareket bitmiş, 24 sansürlü**, medyan **9 seans**. 2023-25 yalnız bu veriyle 748 kabul/17 bitmiş bulundu. M15 quote bütünlüğü native M1 full coverage/PIT belgesi sayılmadı; `BIDASK_M15_RECONSTRUCTED_NOT_M1` ayrı sınıfla aynı slow CORE'a eklendi. Arşivler splice edilmez.

2020-25 gerçek kronolojik retrospektif S2 Brier (model / basit süre): 1g **0,043069/0,042541**, 3g **0,116184/0,123571**, 5g **0,183422/0,203705**, 10g **0,193725/0,229801**. 3/5/10 ufukları küçük avantaj gösterdi; fakat **dördünün de epizot bootstrap %95 GA sıfırı içeriyor**. Bu çalışma canlı PIT/OOS alpha değildir. S2 bilimsel kapısı **PENDING**.

## 23. S3 tek CORE AL–TUT–SAT araştırma critic'i ve ilk Ocak 2023 pilotu (16 Ekim 2026)

**WORKSTREAM=MODEL; STAGE=S3; S3_DEV=INITIAL_INTEGRATED; S3_SCIENCE=NOT_PROVEN; TRADE_AUTHORITY=FALSE; U1=UNCHANGED.** [S3 geliştirme, maliyet ve ilk gerçek fiyat smoke denetimi](adaptive_trading_core/S3_SHADOW_POSITION_VALUE_DEV_AUDIT_20261016.md) · [S3 critic](adaptive_trading_core/adaptive_position_value_s3.js) · [aynı CORE köprüsü](adaptive_trading_core/adaptive_market_core_s1_s2.js) · [özel-veri research replay](adaptive_trading_core/replay_position_value_s3.js).

S1/S2 aynı matematiksel CORE'da S3 `Q(state, CASH/GOLD, KEEP/SWITCH)` olgunlaşmış 15dk fiyat değişimlerinden online öğreniyor; %0,8/her bankacılık yönü (bileşik tam tur **%1,5936**) sabit. Nakit 100 USD, gölge portföy, fee-net CASH/B&H GOLD/critic, drawdown/turnover; kaynağı değiştiren kağıt portföy sonuçları geçersizlenir, gelecek etiket bugünkü karara giremez. `action=null`, `tradeAllowed=false`, `bankTrades=0`; uygulama veya banka işlemi yapılmadı.

**Ocak 2023 salt okunur gerçek BID/ASK MID araştırma smoke:** 1.920 tamamlanmış M15, 21 seans girişi/20 kabul, 1.898 15dk gecikmeli critic güncellemesi; **0 shadow alış/satış**. Net critic/nakit **100 USD**, iki-komisyonlu aynı kaynağın pasif altın referansı **103,8057 USD**. **Net fırsat kaybı 3,8057 USD**; modelin al/sat üstünlüğü gösterilemedi. Bu retrospektif araştırma veri çalışması **S4 sıkı Ocak 2023 tam yürüyüş değildir**, bağımsız alpha iddiası yoktur; bankanın gerçek alış/satış kotasyonları, firstprint erişim kanıtı ve bağımsız OOS eksik. Sonuç görüldü diye yapısal eşiği azaltma/aylık sonuç optimizasyonu yasak. **S1 bilim FAIL; S2 bilim PENDING; S3 bilim NOT_PROVEN; S4/S5/S6/U1 NOT_ACCEPTED.**


---

## 24. Ocak 2023 AL–TUT–SAT başarısızlığının nedensel mühendislik denetimi (16 Ekim 2026)

**WORKSTREAM=MODEL | STAGE=S3_RESEARCH_DIAGNOSTIC | SCIENTIFIC_ACCEPTANCE=NOT_PROVEN.** [Tam neden analizi ve geçmişe bakarak optimum işlem kıyası](adaptive_trading_core/JAN2023_S3_NO_BUY_FORENSIC_AUDIT_20261016.md). Önceki 1.920 M15 Ocak araştırma koşusu **46** karar karşılaştırması/0 BUY idi; **1.768** noktada eksik S2 yavaş durumunun `UNREADY` olarak fast öğrenmeyi yanlışlıkla bloke etmesi belirlendi. `NO_SLOW` eksik-veri kodlamasıyla düzeltildi; hard fast WARMUP, 32 Q destek ve banka ücreti aynı kaldı. Gerçek özel Neon Ocak verisi tekrar oynatıldı: **1.384** değerlendirme, **536** çekimser, **0 BUY**, **100 USD** nakit. Bu sonuç gizlenmedi: 15dk TD ödülü + ücret nedeniyle model hâlâ uzun pozisyon değerini öğrenemiyor. 5/10 işlem seansı olgun, sansürlü, maliyetli Q başlığı ve 2020–22 yalnız geçmiş warmup bir sonraki bilimsel geliştirme işidir; henüz kurulmuş ilan edilmez.

**Ocak senaryoları (TR 09:00–17:00 araştırma fiyatları, iki kez %0,8 banka maliyet vekili):** 3 Ocak sabahı alıp ay sonuna tut **102,54$**; 6 Ocak ABD istihdam açıklaması sonrası alıp 26 Ocak yerel zirvesinde (sonradan bilinen) sat **103,78$**; tek en kârlı geçmişe dönük giriş–çıkış **104,72$**; gerçek S3 **100,00$**. Zirve/sabah girişleri *hindsight/oracle kıyasıdır*, as-of başarısı değildir; gerçek banka emir kotasyonu veya ilk haber erişimi yoktur. Önceki **103,8057$** pasif altın kıyası farklı UTC başlangıç/bitiş barlarını içerir ve TR banka-saatli kıyasla bir tutulmaz. `MODEL_GATE=FAIL`, `U1=UNCHANGED`.


---

## 25. Manifest M2–M5 öğrenme zincirinin gerçek uygulaması ve Ocak 2023 negatif kanıtı (16 Ekim 2026)

**WORKSTREAM=MODEL | M2–M5_DEV=PARTIAL_WORKING | MODEL_GATE=FAIL | SCIENCE_NOT_PROVEN | U1=UNCHANGED.** [M2–M5 gerçek fiyat ve tek CORE entegrasyon denetimi](adaptive_trading_core/M2_M5_INTEGRATION_ARCHIVE_JAN2023_AUDIT_20261016.md).

1. **M2→M4:** Aynı `adaptive_market_core_s1_s2.js` içindeki S1 piyasa kuralının `forecastAtDecision` çıktısı S3 `s1Evidence` girdisine bağlandı. OLAY-02/ÖĞREN-03'ten veya gazeteden sayı uydurulmaz. Normalleştirilmiş `nfp/ahe/unemployment/cpi_surprise_z` gerçek economic EVENT kaynak alanları ilk-baskı/vintage doğrulama kapısıyla S1 öğrenmesine girebilir; S3 bu durumu yalnız araştırma state'i olarak kullanır. **Gerçek Ocak 2023 S3 yürüyüşünde macro PIT feature 0, market-only S1 çıktısı 1920**. Bu, entegre ekonomik bilimsel modelin başarıyla eğitildiği anlamına gelmez.
2. **M3→M4:** 2020–2025 tek-source rekonstre fiyat arşivi S2 slow→S3 `adaptive_position_memory_s3.js` ile çalıştı: **1549 aday / 1500 kabul edilmiş seans / 35 tamamlanmış yavaş epizot / 4955 olgunlaşmış net 1/3/5/10 oturum öğrenme etiketi / 1033 sansür / 28 durum-ufuk cohort**. Bunlar **örtüşen** örnekler ve quote MID vekilidir, bağımsız kâr kanıtı değil.
3. **M4 2023 Ocak negatif deney:** Gerçek **1920 M15**, **20 geçerli slow seans**; S3 aynı model içinde uzun-vade araştırma moduyla koşuldu. Ücretli 5-seans sonlandırılmış `NO_SLOW:NONE` örnekleri `n=10, meanNetLogPct=−0,3854`, **0 shadow BUY**, son nakit **100 USD**, eski MID bazlı pasif GOLD referansı **103,8057 USD**. Nakit bekleme hatası halen çözülemedi; yalnız ufuk eklemek M4 tamamlandığı anlamına gelmez. Ocak optimum giriş-çıkış fiyatı kural diye yüklenmedi.
4. **M5 hafıza:** Oturum `pending`, `cohorts`, `censored` ve geçmişte hazır S1 kanıtı artık tek S3 checkpoint/restore içinde. Gizli eğitim checkpointi ve 2023–2025 aylık devir zinciri henüz yaratılmadı. Kaynak firstprint/PIT eksik, bağımsız kural üstünlüğü kanıtlanmadı. **M2_SCIENCE=FAIL, M3_SCIENCE=PENDING, M4_SCIENCE=NOT_PROVEN, S4_MODEL_GATE=FAIL, NEXT_MONTHS=BLOCKED, APP=UNCHANGED.**

**Yeniden üretim:** `adaptive_trading_core/replay_slow_position_memory_s3.js`, testleri ve GitHub Actions; 2020–2025 arşiv *açıklayıcı* deneyi kronolojik Ocak 2023 performansının eğitim önbilgisine dönüştürülmez. Manifestin başlangıç, ücret, tarih, proje ve branch sözleşmesi değişmedi.


---

## 26. Kullanıcı talebiyle 2023 Ocak–Aralık tam yıl araştırma performans denetimi (16 Ekim 2026)

**Yıllık sonuç: S3 LEGACY_M15 ve S3 MULTI_SESSION_RESEARCH her biri 23.544 M15 fiyatını mevcut tek CORE'dan kronolojik geçirdi; ikisi de 0 BUY / 0 SELL / 100,00 USD CASH, net getiri %0.** 2023 ilk izinli fiyatı `03 Ocak 09:00 TRT` 1840,52 USD/oz, son `29 Aralık 17:00 TRT` 2059,265 USD/oz. Her iki %0,8 işlem maliyeti dahil **pasif GOLD 110,10196 USD / +%10,10196**. Yıllık fırsat farkı model aleyhine yaklaşık **10,10 USD/100 USD**. S1 1438 anchor, 1384 olgun dört saatlik sonuç, 4 prototip; S2 fast 463 tamamlanmış mikro hareket, full-year slow arşivinde 249 kaliteli seans/6 epizot. Yıllık koşuda **makro PIT features 0**. S3 M4 oturum hafızası (son gün henüz karar zamanında olgunlaşmadığından) 812 olgun /170 sansür. **Bilim kapısı ve S5 AÇILMADI:** Bu kullanıcı talebine cevap olarak yapılan retrospective shadow performans araştırması, zorunlu Ocak gate'i geçmeden Şubat–Aralık kronolojik resmi eğitim ve aylık snapshot zincirini tamamlamak değildir; ilkprint sertifikası, banka gerçek kotasyonu ve ekonomi katkısı yoktur. [Ayrıntılı 2023 yıllık performans ve aylık tasfiye kıyasları](adaptive_trading_core/S3_FULL_YEAR_2023_RECONSTRUCTED_SHADOW_DIAGNOSTIC_20261016.md). `MODEL_GATE=FAIL` · `APP=UNCHANGED`.


---

## 27. Kullanıcı düzeltmesi: banka işlem saati zorunluluğu YOK, normatif karar (16 Ekim 2026)

**WORKSTREAM=MODEL | USER_RULE_CORRECTION | PRIOR_HOUR_GATES=REVOKED | MATH_GATE=UNCHANGED.** Kullanıcı *banka işlem saati diye bir şartımız yok* olarak açıkça düzeltti. Bu nedenle §3 hedefindeki eski `Türkiye 09:00–17:00` kuralları silinip **saat bağımsız, yalnız gerçek gözlenmiş ve as-of doğrulanmış fiyat** kıstası yazıldı. `adaptive_position_value_s3.js` içindeki `BANK_WINDOW_CLOSED_RESEARCH` abstain ve zorunlu paperTrade saat kilidi kaldırıldı; 23:00 Türkiye saatinde tamamlanmış, geçerli kaynaklı sentetik fiyatla araştırma `BUY` üretilebileceğini ve **gerçek banka emri** üretilmediğini doğrulayan regresyon testi eklendi.

**Önceki ay/yıl raporları yeniden yazılmış gerçek performans değildir:** §24, §26 ve ilgili 09:00–17:00 benchmark tabloları *eski ve artık geçersiz kabul edilen varsayımla üretilmiş tarihsel kıyaslar* olarak okunmalı; yeni araştırmalarda kıyas ilk/son uygun M15 gözlemleri üzerinden yapılır. Eski benchmarkların saat penceresini çıkarınca sonuçlar değişir; eski `110,10$` pasif altın 2023 yılı için yeni sözleşmedeki ilk `2023-01-02 23:15Z` 1827,13 MID ve son `2023-12-29 22:00Z` 2062,90 MID kaynak vekiliyle **111,104608 USD**'dir. Bu veri gerçek banka kotasyonu değildir, ilk/son kapanışta işlem garantisi yoktur. Tüm eski 0 işlem sonuçları düzeltmeden sonra henüz yeniden yeniden oynatılmış ilan edilmez.

M2–M5 arızaları: (a) gerçek 2023 ekonomik firstprint feature'ları S3 kararlarına akmıyor, (b) S2'nin kalan trend ömrü/fırsat değeri S3 eylem Q'ya bağlı değil, (c) 5 seans sabit-mecburi tasfiye öğrenimi uzun HOLD politikasının toplam değerine denk değildir, (d) M5'te kayıtlı missed-up/regret ve uzman-önceki performans ağırlığı karara geri beslenmiyor, (e) V13'teki 14/56 gün ve recurrent/gated memory mimarisi yeni S3'e aktarılmış değil. Eski deneyler otomatik kabul edilmiş model sayılmaz; karşılaştırmada as-of, kaynak ve maliyet eşitliği şarttır. **MODEL_GATE=FAIL | LIVE=NO | APP=UNCHANGED.**


## 28. Zorunlu saat filtresi kaldırıldıktan sonra 2023 bağımsız araştırma teyidi (16 Ekim 2026)

GitHub `55f20d641cc33a43151a6cdfdcebf221833f85cf` sonrası aynı S1/S2/S3 mevcut CORE, 2023 **23.544 M15** fiyatında kullanıcı isteğine uygun **saat filtresiz** 12 aylık tek shadow replay olarak çalıştırıldı: `LEGACY_M15` **0 AL/0 SAT/100,00 USD CASH**; `MULTI_SESSION_RESEARCH` **0 AL/0 SAT/100,00 USD CASH**; tüm gözlenen veri ilk/son MID üzerinde %0,8+%0,8 masraflı pasif GOLD **111,104608 USD**. S3 multi-session: 18.216 karar kıyası, 5.571 yetersiz destek, 12.645 ikna etmeyen 5-seanslık etiket, 0 AL. Bunlar 15 Ekim'in eski SENTEZ/REHBER çalışma varsayımlarıyla doğrudan başarı yarışı değil ve gerçek banka kotasyonu değildir. Önceki §26'nın 09–17 bazlı **110,10 USD** benchmarkı güncel kıyas olarak geçerli sayılmaz. Kaynak/açıklama: [2023 yıllık denetimin saat bağımsız ek bölümü](adaptive_trading_core/S3_FULL_YEAR_2023_RECONSTRUCTED_SHADOW_DIAGNOSTIC_20261016.md#16-ekim-2026-kullanıcı-düzeltmesi-sonrasında-saat-kısıtsız-yeniden-üretim). `M2/M3/M4/M5` mimari eksikleri aynı, `MODEL_GATE=FAIL`, APP/TRADE=UNAUTHORIZED.


---

## 29. Eski V7–V20 deneylerinden tek CORE öğrenme iyileştirmesi (16 Ekim 2026)

**WORKSTREAM=MODEL | STAGE=M2–M5 | ENGINEERING=PARTIAL_PASS | SCIENTIFIC_MODEL_GATE=FAIL | APP=UNCHANGED.**
[Ayrıntılı önceki-algoritma envanteri, uygulama ve 2023 negatif karşılaştırması](adaptive_trading_core/M2_M5_LEGACY_CONSOLIDATION_DELIVERY_MATRIX_20261016.md).

Mevcut S3 modeline yeni bir uygulama veya dal açmadan `adaptive_long_cycle_s3.js` eklendi: SENTEZ deneylerinden 14/56 takvim günlü olgunlaşmış getiri, recurrent trend/stres belleği; geçmiş sonucuyla AdaGrad güncellenen kapılı uzman; olgunlaşan tahmin-hata uzman ağırlıkları; CASH iken kaçırılan/kaçınılan değerlerin M5 kaydı; yalnız sonraki tamamlanmış M15'te gölge icra; **zorunlu işlem saati YOK**. Bu gerçek LSTM/ANN veya başarıyla öğrenilmiş ekonomik M2 ilişkisi değildir. `LEGACY_M15` ve `MULTI_SESSION_RESEARCH` karşı modelleri saklandı; `INTEGRATED_LONG_RESEARCH` üçüncü shadow moddur. `replay_s3_monthly_challengers.js` aynı kaynak, iki yön %0,8 maliyet, input SHA ve aylık kıyası sistematik üretir. S3 checkpoint sürümü R2; eski checkpoint R2 diye açılamaz.

**2023 gerçek yeniden araştırma:** aynı 23.544 M15 quote-only arşivde bütün üç mod da **100 USD, 0 BUY/0 SELL**; pasif altın **111,104608 USD**. Yeni öğrenme 25 olgun 14g ve 11 olgun 56g etiket; 56g etkin destek 6; sonuç negatif/kararsız. Ocak/2023 sonucuna bakarak işlem açtıran keyfî eşik eklenmedi. İlk-published makro veri modeline gerçek 2023 girişi 0; M2 bilimsel performans, M3 kalan hareket, M4 öğrenilmiş değişken süreli HOLD, M5 immutable aylık devir, S4 başarılı geçiş hâlâ **EKSİK/FAIL**. Başarı denetimi ve açık iş sırası bağlantılı raporda tutulur.
