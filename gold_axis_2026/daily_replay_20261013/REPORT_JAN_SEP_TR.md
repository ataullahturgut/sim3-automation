# ASTRA — 2026 Ocak–Eylül günlük karar incelemesi

**Sonuç: O günün haberini ve piyasa tepkisini yorumlayarak verdiğim kararlar, bu uygulamada güvenilir bir al-sat üstünlüğü üretmedi.** Bazı düşüşlerde nakitte kalmak ve ağustostaki yükselişi taşımak işe yaradı; fakat sık giriş-çıkış, geç teyit ve haberlerin tersine dönmesi toplam sonucu bozdu. Komisyon öncesinde bile ana karşılaştırmada al-tut gerisinde kaldım. Bu olumsuz sonuç da araştırmanın sonucudur.

Kapsam **1 Ocak–30 Eylül 2026: 273 takvim günü**, 78 hafta sonu günü dahil. Kullanıcının son talebiyle ekim kapsam dışıdır. Her tarihte karar kaydı vardır; bu, her gün yayımlanan bütün haberlerin eksiksiz tarandığı anlamına gelmez. Araştırma 13 Ekim'de geçmişe dönük yürütüldü. Gerçek emir verilmedi.

## 1. Sayısal sonuç

100 birim USD eşdeğeri başlangıç, altın veya faizsiz nakit, kaldıraç/açığa satış yok. Gün sonu kararını ancak sonraki uygun günün fiyatıyla uyguladım. Ana fiyat: 09:00 UTC / 12:00 Türkiye saati tam 15 dakikalık barın açılışı. Bu bir **tanısal spot fiyat vekili**, banka alış/satış kotasyonu değildir.

| Ocak–Eylül | Komisyonsuz | Her alış ve satışta %0,8 |
|---|---:|---:|
| Günlük kararlar, sonraki uygun gün 09:00 UTC | −%7,41 | **−%31,68** |
| Aynı başlangıç fiyatıyla al-tut | −%5,30 | −%6,81 |
| Faizsiz USD nakit | %0,00 | %0,00 |
| Günlük kararlar, sonraki uygun günün son fiyatı | −%4,81 | −%29,76 |
| Son fiyat senaryosunun kendi al-tut kıyası | −%4,10 | −%5,62 |

Ana maliyetli senaryoda 100 birim **68,32** olur. **19 tamamlanmış pozisyon dönemi, 38 işlem yönü; 19 dönemin yalnızca 2'si maliyet sonrası pozitiftir.** Komisyonsuz pozitif dönem sayısı 4'tür. Günlük son gözlemle işaretlenen portföyün maksimum düşüşü yaklaşık **%42,31**; bu gün içi maksimum düşüş değildir.

Karar sayıları: **20 AL, 20 SAT, 75 TUT, 158 BEKLE.** 40 karar değişiminin 38 uygulamaya dönüşmesinin nedeni, 16 Ocak satışının hafta sonu ve tatil nedeniyle henüz uygulanmadan 18 Ocak alımıyla iptal olmasıdır. Kapalı günlerde hayali satış/alım yazılmadı. Hedef pozisyon 95 takvim günü altın; gecikmeli uygulanan pozisyon 97 gün altın oldu.

Maliyet yükü küçük değildir: 19 tam giriş-çıkışın servet çarpanı, fiyat hareketlerinden bağımsız olarak `(0.992/1.008)^19 ≈ 0.738` olur. Ancak **sorun yalnız komisyon değil**: ana komisyonsuz sonuç da al-tuttan yaklaşık 2,11 yüzde puan kötüdür. Sonraki kapanış duyarlılığı da üstünlük göstermedi. İyi çıkan saat seçilmedi.

## 2. Ben bunu neye göre yaptım?

Her güne şu sırayla baktım: tarihli haber → beklenti değişimi → dolar/faiz/petrol veya risk iştahı aktarımı → altının tepkisi → mevcut pozisyonu bozan kanıt. Çoğunlukla ilk tepkinin ardından devam aradım; fakat bu **sayısal eşikleri baştan dondurulmuş bir model değildi**. Teyit miktarı, haberin önemi ve çıkış kararı takdirî kaldı. Bu nedenle sonradan uygulanabilir, aynı sonucu garanti eden bir algoritma iddia edemem.

Karar kaydedilmeden sonraki tarihin paketi açılmadı. Manifestteki 2026 olay atlası bu inceleme için açılmadı. Ancak önceki konuşmadan bilinen olaylar unutulamaz; gerçek kör test değildir. Haber aramasının sonraki tarihli URL'leri programla elendi. Aynı URL'nin ertesi gün güncellenmesi ise tam olarak engellenemedi: fark edilen gelecek seans anlatıları gerekçede dışlandı, fakat metni görmüş olmak zihinsel sızıntıyı tamamen ortadan kaldırmaz.

Kaynaklar Reuters öncelikli tarihli taramalar, bazı günlerde ek teyit aramaları ve araştırma veritabanındaki piyasa gözlemleriydi. Her gün için tarih, karar, hedef pozisyon, gerekçe, kararı bozan koşul, kapsam ve kaynak adayları ayrı JSON dosyasına kaydedildi. İlk kayıtlara sonradan başarılı görünecek şekilde müdahale edilmedi.

## 3. Ay ay ne oldu?

Aşağıdaki getiriler ana %0,8 maliyetli senaryoda aylık portföy değişimidir; gün sonu değerleme, açık pozisyonun gerçekleşmemiş sonucunu da içerir. Aylık oranlar toplanmaz, bileşiklenir.

| Ay | Net aylık değişim | Uygulanan altın pozisyonunda takvim günü | Karar davranışı |
|---|---:|---:|---|
| Ocak | +%5,07 | 25 | Jeopolitik/kurumsal güven yükselişine katıldım; çıkıp yeniden girdim. Ay sonu sert düşüşü önceden yakalayamadım. |
| Şubat | −%9,14 | 6 | Kısa toparlanmalara girişler ve sonraki geri çekilmeler maliyet yarattı; ocak sonu pozisyonunun kapanışı da bu ayda. |
| Mart | −%3,39 | 1 | Ay başındaki pozisyon kapandıktan sonra uzun süre nakit; ay sonu toparlanmasına alım kararı. |
| Nisan | −%7,24 | 15 | Ateşkes/yeniden gerilim döngüsünde sık yön değiştirdim. |
| Mayıs | −%2,63 | 7 | Uzun bekleme araları; sınırlı alımlar kalıcı üstünlük üretmedi. |
| Haziran | −%5,73 | 4 | Sert satışların çoğunda nakit, ancak ara toparlanmalara kısa girişler kayıp yarattı. |
| Temmuz | −%8,95 | 5 | Yumuşak veri ve iki günlük tepkiye tekrar tekrar alım; enerji/dolar dönüşlerinde hızlı çıkış. |
| Ağustos | +%2,23 | 27 | 5 Ağustos alımı sonrası uzun taşıma; 28 Ağustos şahin konuşma düşüşü yaşandıktan sonra satış. |
| Eylül | −%6,54 | 7 | İki kısa alım-satım dönemi başarısız; ayın çoğunda bekleme. |

## 4. En öğretici kararlar ve hatalar

**Ocak sonunu önceden bilmiş gibi gösteremem.** 29 Ocak kaydı TUT, 30 Ocak kaydı SAT. Gün içi/önceki hareket zaten yaşanmıştı. Sonraki uygun uygulama 2 Şubat oldu. 22 Ocak alım kararından başlayan dönemin net sonucu −%7,07. Bu, haberin mekanizmasını sonradan doğru anlatmanın düşüşü önceden önlemekle aynı şey olmadığını gösterir.

**Mart ve hazirandaki beklemeler kısmi başarıdır, toplam başarı değildir.** Enerji şoku, dolar ve faiz beklentileri altına baskı yaparken nakitte kalındı. Fakat birkaç doğru bekleme, aralarda yapılan pahalı işlemleri telafi etmedi. Bu dönemlerden başarılı örnek seçip bütün yöntemi başarılı ilan etmek yanlış olur.

**Temmuz açık bir yanlışlama örneğidir.** 15 Temmuz AL → 16 Temmuz SAT, 22 Temmuz AL → 23 Temmuz SAT, 30 Temmuz AL → 31 Temmuz SAT. Olumlu veri veya iki günlük toparlanma, kalıcı rejim değişimi sanılmaya elverişliydi. Sonraki gün fiyatı ve işlem maliyeti eklendiğinde bu dönüşler pahalı oldu. Kararların gerekçeleri makul görünse bile toplam ekonomik değeri zayıftı.

**Ağustosta yükselişin bir kısmını taşıdım; tamamını yakalamadım.** 5 Ağustos AL, uygulama 6 Ağustos 09:00 UTC: 4262,635. 28 Ağustos SAT, uygulama 31 Ağustos: 4442,955. Dönem net +%2,58. 5 Ağustos'un alım kararından önceki büyük yükselişi kazanç değildir. 28 Ağustos düşüşü de satıştan önce yaşandığı için kayıptan çıkarılmadı. 19 Ağustos Hazine geri alım genişlemesi sonrası yükseliş mevcut pozisyonda karşılandı; bu tek vaka politika şokunun nedensel etkisini ölçmez.

**Eylülün ilk alımı veri riskini gösterdi.** 3 Eylül Waller mesajı ve toparlanma sonrası AL; 4 Eylül güçlü istihdam sonrası SAT. Tatil nedeniyle çıkış 8 Eylül'e kaydı, net −%3,58. Haber öncesi yön kararı ile haber sonrası risk azaltma aynı yetenek değildir.

Bütün 19 dönem, iyi-kötü ayrımı yapılmadan [ALL_TRADES.md](ALL_TRADES.md) dosyasındadır. Karar tarihi ve uygulama tarihi ayrı gösterilir; özgün kararlar günlük kayıtlarda korunur. İşlemlerin son bilgi kesimi ayrıca CALCULATIONS.json içindedir.

## 5. Araştırma amacımız açısından hangi mekanizmalar göründü?

| Aday olay zinciri | Defterdeki gözlem | Karşıt örnek / sınır | Kanıt gücü |
|---|---|---|---|
| Enerji arz tehdidi → petrol/enflasyon kaygısı → sıkılaşma/dolar → altın baskısı | Mart, mayıs, haziran, temmuz ve eylülün bazı günlerinde tekrarlandı. | Ağustosta yüksek uzun faize rağmen altın yükseldi; mekanizma tek başına yeterli değil. | Tarihli ilişki ve tutarlı mekanizma adayı; tanımlanmış nedensel etki değil. |
| Diplomasi → enerji rahatlaması → faiz/dolar rahatlaması → altın toparlanması | Birçok ateşkes/görüşme gününde görüldü. | Kısa sürede bozulan anlaşmalar; 26 Mayıs gibi önceki toparlanmanın sürdürülememesi. | Tekrar eden ama istikrarsız, haber güncellemesine hassas ilişki. |
| Makro sürpriz/Fed iletişimi → faiz patikası beklentisi → altın | Temmuz başı zayıf istihdam; ağustos istihdam; eylül şahin veriler. | Yumuşak veri sonrası enerji şokunun baskın çıkması; 30 Eylül olumlu veriye rağmen düşüş. | Sürpriz büyüklüğü ve ilk yayın arşivi olmadan nicel nedensellik kurulamaz. |
| Kurumsal/mali güven ve rezerv talebi → altın talebi | Ocak Fed bağımsızlığı haberleri; ağustos rezerv ve borç tartışmaları. | Rezerv verileri gecikmeli; aynı gün fiyatı açıklaması belirsiz. | Daha zayıf, karıştırıcıları çok olan mekanizma adayı. |
| Likidite politikası → uzun faiz/dolar → altın | 19 Ağustos Hazine geri alım haberi sonrası ortak tepki. | Öncesinde pozisyon zaten açıktı; başka haberler ve beklenti farkı kontrol edilmedi. | Vaka kanıtı; QE veya genel nedensel yasa değil. |

Bu defter, EFP/fiziki sevkiyat, teminat çağrısı, gerçek dealer gamma, fonlama veya CFTC pozisyonları için tam veri içermiyor. Dolayısıyla bu kanalları doğrulamış sayamayız. Nominal DGS10'u reel faiz diye kullanmadım; reel faiz ve enflasyon beklentisi ayrıştırması ayrı veri gerektirir. Haber içindeki analist açıklaması, gözlenmiş aktarım veya kanıtlanmış neden değildir.

## 6. Neden karar yaklaşımı başarısız oldu?

1. **Teyit gecikmesi:** hareketi gördükten sonra alım; ertesi uygun fiyat zaten daha yüksek olabilir. Aynı günün getirisi kararın başarısı sayılamaz.
2. **Geçici tepkiyi kalıcı dönüş sanma:** iki olumlu gün, aynı makro baskının geri dönmesini engellemedi. Özellikle temmuzda belirgin.
3. **Karar değişiminin maliyeti:** haber akışına sık cevap verilmesi, %0,8 + %0,8 maliyet altında yüksek bir eşik yaratıyor. Beklenen hareket büyüklüğünü ve belirsizliğini ölçmeden işlem kararı verdim.
4. **Gerçek uygulama gecikmesi:** cuma/hafta sonu kararının pazartesi veya sonraki iş gününe kayması sonucu değiştiriyor. 16 Ocak–18 Ocak örneğinde niyet değişimi gerçek işlem bile oluşturmuyor.
5. **Eksik beklenti ölçümü:** haberin iyi/kötü olması ile fiyatlanmış beklentiden sürprizi ayrılmadı; ortak, sayısal bir sürpriz serisi yok.
6. **Tutarsız takdir riski:** bazı olumsuz günlerde tek seansla çıkıldı, bazılarında ikinci gün beklendi. Önceden kodlanmış ölçüt olmayınca sonuç yeniden üretilebilir bir karar modeli değil, sabitlenmiş bir insan/LLM değerlendirme defteridir.

Bu açıklamalar sonuç sonrası teşhistir; aynı dönem üzerinde yeni eşik seçerek sonucu iyileştirmedim. Buradan doğrudan yeni strateji önerisi çıkarmıyorum.

## 7. Veri ve bilimsel güvenilirlik denetimi

**Doğrulananlar:** 273 tarihin her biri tekil ve kesintisiz; 78 hafta sonu dahil. 2026 bar tablosunda 17.616 kayıt ve 17.616 tekil zaman damgası; temel OHLC tutarsızlığı sıfır, 29 kısmi bar. Bunların 20 barı 1 Ekim'in ilk saatlerine ait olup sonuç kapsamı dışındadır. 09:00 uygulamada yalnız 15 dakika kaynak kapsayan barlar kullanıldı. Kaynak dönüşüm kodu sabit EST (UTC−5) → UTC yapıyor; yaz saati varsayılmıyor.

**Fiyat otoritesi sınırlı:** HistData kaynağı veritabanında bağımsız ama **noncanonical candidate** olarak etiketli. OHLC tutarlılığı doğru fiyatı veya işlem yapılabilirliği kanıtlamaz. Günlük panel son UTC barıdır; LBMA fixing veya New York 17:00 kapanışı değildir. Haber fiyatları farklı saatlerde olabilir. Değerlendirme fiyatı ayrıca sonraki uygun bar olarak seçildi.

**Bilgi zamanlaması sınırlı:** FRED ve diğer seriler sonradan indirilmiş araştırma gözlemleridir. Gözlem tarihi, ilk yayımlanma zamanı değildir. İlk baskı/revizyon arşivi yok. Dolar ve petrol çoğunlukla haberden nitel olarak izlendi; eşzamanlı sayısal panel kurulmadı. VIX'in erken dönem kapsamı eksik; diğer metal serileri ağustosta güncellenmiyor, bazı hafta sonu değerlerinde saat farkı var. Eski tarihli gözlem yeni bilgi sayılmadı.

**Haber kapsamı sınırlı:** 1 Ocak, 4 Ocak, 10 Ocak, 30 Mayıs ve 11 Temmuz'da tarih filtresini geçen kaynak bulunamadı. Bu beş günün dışında da bazı günlerde yalnız sınırlı veya ilgisiz haber bulundu. Kaynak listesi, aramanın döndürdüğü adayları içerir; hepsi gerekçede kullanılmadı. URL tarih filtresi ilk yayın güvencesi değildir. Bazı arama özetlerinde saat/tarih ve anlatım hataları görüldü. Önemli bazı günlerde tam metin parçası okundu; her kaynak bağımsız ilk-yayın denetiminden geçirilmedi.

**Körlük ve kontrol sınırlı:** Önceden bilinen vakalar, aynı yıl üzerinde takdirî düşünme ve kaynak güncellemeleri nedeniyle bu bağımsız out-of-sample deney değildir. BEKLE/TUT günlerinin dahil olması seçilmiş vaka sorununu azaltır; fakat bunlar rastgele veya eşlenmiş nedensel kontrol grubu değildir. 273 bağımsız istatistiksel örnek de değildir: haberler, pozisyonlar ve fiyat pencereleri aynı epizod içinde bağımlıdır. AUC, p-değeri, nedensel başarı oranı veya geleceğe genellenebilir performans hesaplanmadı.

**Getiri sınırı:** USD spot vekili kullanıldı. Gram altın/TL, USD/TRY, banka makası, vergi, kayma, likidite ve nakit faizi yok. %0,8 her yön maliyet senaryosudur. Gerçek kullanıcının banka hesabı için −%31,68 olacak denemez. Sonuç, bu takdirî kararların seçilen makul uygulama varsayımı altında zayıf olduğunu gösterir.

## 8. Asıl araştırma sorusuna cevap

**Tekrarlayan olay zinciri adayları var; bu günlük çalışma onları bilimsel olarak nedensel veya gelecekte güvenilir biçimde ayırt etmiş değil.** En belirgin aday, enerji arz şokunun enflasyon/faiz/dolar üzerinden altını baskılaması ve bu baskının geçici rahatlamalarda çözülmesi. Aynı haber sınıfının farklı günlerde farklı sonuç verdiği karşı örnekler de var.

Benim doğrudan günlük muhakemem, bu uygulamada basit al-tutu yenmedi. Bu, kullanıcının “belki çok karmaşık modele gerek kalmadan daha iyi karar verirsin” önerisinin dürüst sınamasında olumsuz sonuçtur. “Hiçbir model çalışmaz” veya “olay zinciri yoktur” sonucu çıkmaz; yalnız bu karar yönteminin üstünlüğü gösterilemedi.

Bir sonraki bilimsel adım daha çok model eklemek değil: ilk-yayın zamanları doğrulanmış az sayıda mekanizma, fiyat sonucu gizlenmiş haber etiketleri, aynı koşullarda büyük hareket olmayan dönemler ve ileriye dönük sabit karar kaydı. Bu rapor yeni test yapmıyor; sonraki çalışmaya yanlışlanabilir adaylar ve başarısız kararlar sağlıyor.

## 9. Dosyalar ve yeniden üretim

- [Ocak](DAILY_01.md), [Şubat](DAILY_02.md), [Mart](DAILY_03.md), [Nisan](DAILY_04.md), [Mayıs](DAILY_05.md), [Haziran](DAILY_06.md), [Temmuz](DAILY_07.md), [Ağustos](DAILY_08.md), [Eylül](DAILY_09.md): her gün karar, gerekçe, bozulma koşulu, kapsam ve kaynak adayları.
- [Bütün işlemler](ALL_TRADES.md), [sayısal özet](RESULTS.json), [hesap ayrıntıları](CALCULATIONS.json).
- [İlk protokol](PROTOCOL.md), [sonuç hesabından önce sabitlenen uygulama varsayımları](EVALUATION_SPEC.md).
- `days/2026-01-01.json`–`days/2026-09-30.json`: özgün günlük kayıtlar. [SHA-256 listesi](FROZEN_DAY_HASHES.json), bütünlük kontrolü sağlar; bağımsız zaman damgası kanıtı değildir.
- [Fiyat kesiti](execution_prices.json), [bar kapsamı](bar_coverage.json), [SQL sorguları](SOURCE_QUERIES.sql), [sıralı inceleme yardımcıları](REPLAY_HELPERS.js).
- Yeniden hesaplama: `python gold_axis_2026/daily_replay_20261013/evaluate.py`. Hesap standart Python kütüphanesini kullanır; veri indirmez, mevcut günlük kararları değiştirmez. Karar muhakemesinin kendisi algoritmik olarak yeniden üretilemez; yalnız sabit kararların muhasebesi üretilebilir.

Mevcut araştırma dosyaları değiştirilmedi; ayrı dal/PR. Ana dal çalışma sırasında ilerledi: başlangıç `4ecdf810e4e76fba37d20b4a94d30d0bc54b30a3`, yayın öncesi görülen uç `45aed5751b69186a3474a947039b24e94b14505a`. Yeni sonuçlar son uç üzerine yalnız yeni dosyalar olarak eklenecek; hiçbir PR birleştirilmeyecek.
