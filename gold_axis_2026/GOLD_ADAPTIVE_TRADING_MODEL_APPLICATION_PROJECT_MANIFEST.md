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

1. Başlangıç: **100 USD NAKİT**, banka işlem penceresi Türkiye 09:00–17:00 (gerçek bankada uygunluk ayrıca kanıtlanır). Her **AL** ve **SAT** bacağında %0,8. Gerçek banka BID/ASK, spread ve slippage kanıtı yoksa sonuçların tamamı **fiyat vekilli araştırma simülasyonu** olur. Çift ücret yanlışlıkla iki kez kesilmez.
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
