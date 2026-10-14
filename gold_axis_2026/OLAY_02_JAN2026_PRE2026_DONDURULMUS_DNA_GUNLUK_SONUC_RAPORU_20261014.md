# OLAY-02 — OCAK 2026 TAM GÜNLÜK YENİDEN YÜRÜYÜŞ: OCAK SONUCUNU KURALA KARIŞTIRMAMA KONTROLÜ

**AYRI DENEY — KARAR ANINA GÖRE SINIRLI GİRDİ:** `AS_OF_INPUT_ENFORCED_RECONSTRUCTION`. **KÖR/BAĞIMSIZ OOS DEĞİL.** Araştırmacı bu denemeden önce Ocak 2026 sonuçlarını ve Astra Ocak'ı görmüştür. Ancak yeniden yürüyüşte kullanılan algoritmik kural [ayrı protokole](OLAY_02_JAN2026_PRE2026_FROZEN_REPLAY_PROTOCOL_20261014.md) **Ocak 2026 fiyat verisi yeniden sorgulanmadan önce commit edilmiştir**. Eski %2 yükselişte AL / %3 geri çekilmede SAT kuralı **kullanılmadı**. Önceki iptal edilen çalışma aynen `INVALIDATED_CONSTRAINT_BREACH` olarak kalır.

## 1. Bu defa tam olarak hangi bilgi ve hangi karar kullanıldı?

**ANA-01:** Orta/büyük olayları araştır, küçük günlük dalgalanmalarla sık işlem yapma; GOLD/CASH; alışta ve satışta %0,8, BID/ASK ve sonraki uygulanabilir fill; bağımsız nedensel teyit yoksa `HOLD/ABSTAIN`.

**OLAY-02:** Sadece 2023–2025 haber/fiyat vakaları, 96 kayıt ve karşıt mekanizmaları; 2026 olay verileri sınıflandırmayı öğretmek veya parametre seçmek için kullanılmadı.

**ÖĞREN-03:** ORG01–ORG12 tarihsiz ekonomik olay tipleri ve daha eski `H-UP01/H-DN01/H-HOLD01` hipotezleri. **Sonraki Ocak görme hatasından öğrenilmiş 12. bölüm karar kuralları kullanılmadı.**

**Dondurulmuş sayısal tamamlayıcı:** Neon HistData XAU M15'in 2023–2025 arasında **636 tam 21:45 UTC kapanış gözlemi**. Özellik ve beş seans sonra gerçekleşmiş getirisi ölçülebilen **485 geçmiş analog**; her gün 21 nearest-neighbor, 1/3/5/10 kapanış getirisi ve beş-kapanış geri çekilme yapısı. Beş seans sonraki getirilerin **medyanı**, yükseliş/düşüş analog olasılıkları hesaplandı. Komisyonun iki taraf başabaş ihtiyacı **%1,6194**; BUY/SELL adayları için hem medyan kalan hareketin bu sınırı aşması hem 21 analoğun en az %65'inin aynı yöne işaret etmesi şart. **Yalnız fiyat analoğu ekonomik DNA değildir**. Son aşamada ekonomi haberinin ilk kaynağı + faiz/USD/metaller eşsaat aktarımı gibi ÖĞREN-03 teyitleri gerekir.

**Saat:** Yalnız son tamamlanmış `UTC 21:45–22:00` 15 dakikalık HistData barı karara girer. Jan 21:45 UTC seçimi takvim yılı boyunca sabit fiyat kesitidir; **yaz saati uygulanan dönemlerde gerçek NY17 kapanışıyla aynı olmak zorunda değildir**. Bu nedenle referansı yanlış `NY17` diye etiketleme. İcra sinyali çıksaydı sonraki mevcut `09:00 UTC` Dukascopy direkt ASK/BID kullanılır; veri yoksa sahte fill yapılmaz.

**Haber protokolü:** [BLS Ocak 2026 yayın takvimi](https://www.bls.gov/schedule/2026/01_sched_list.htm) (9 Ocak NFP, 13 Ocak CPI, 14 Ocak PPI), [BLS NFP asıl arşivi](https://www.bls.gov/news.release/archives/empsit_01092026.htm), [BLS CPI asıl arşivi](https://www.bls.gov/news.release/archives/cpi_01132026.htm) ve [Fed 28 Ocak basın duyurusu](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260128a.htm) zamanlı resmî bağlam. [3 Ocak Reuters Venezuela](https://www.reuters.com/world/americas/view-investors-economists-react-us-capture-venezuelas-maduro-2026-01-03/), [19 Ocak Reuters Grönland](https://www.reuters.com/world/india/gold-silver-hit-record-highs-trumps-greenland-tariffs-spark-safety-rally-2026-01-19/), [30 Ocak Reuters metal satışları](https://www.reuters.com/business/tsx-futures-fall-gold-slumps-ahead-trumps-fed-chair-decision-oil-retreats-2026-01-30/) yeni olay bağlamıdır. **Haber ilk baskı veya yeniden yayım saati ve USD/faiz aynı UTC dizisi eksik olduğundan hiçbir ORG kesin neden sayılmadı.** Haber içerikleri fiyat modelinin sinyaline ek parametre olarak sokulmadı.

## 2. Ocak ayının 31 günü — gün bazında gerçek çıktı

| Gün | XAU 21:45 fiyatı ($) | Benzer 21 olayın medyan ileri 5-seans getirisi | Ekonomik DNA adayı | Karar | O anda haber/yayın / belirsizlik |
|---|---:|---:|---|---|---|
| 01 | — | — | UNRESOLVED | NAKİT TUT | Yılbaşı, doğrulanmış kapanış yok |
| 02 | 4.331,58 | 1,21% | UNRESOLVED | NAKİT TUT | Yeni işlem yılı; yeni ekonomi tetikleyicisinin ilk baskısı doğrulanmadı |
| 03 | — | — | ORG04 | NAKİT TUT | Venezuela müdahalesi — Reuters'ın aynı gün haberi; hafta sonu |
| 04 | — | — | UNRESOLVED | NAKİT TUT | Hafta sonu; bağımsız ekonomik aktarım ölçümü yok |
| 05 | 4.448,35 | 1,08% | ORG04 | NAKİT TUT | Venezuela haberinin sonrasındaki piyasa; ORG04 güvenli liman adayı |
| 06 | 4.493,19 | 0,56% | UNRESOLVED | NAKİT TUT | Yeni teyitli haber yok; önceki durum üzerinden gözlem |
| 07 | 4.455,64 | -0,17% | G01-X | NAKİT TUT | JOLTS açıklama günü; istihdam/Fed G01-X adayı |
| 08 | 4.477,56 | 1,23% | UNRESOLVED | NAKİT TUT | Ekonomik ilk haber ve çapraz piyasa teyidi eksik |
| 09 | 4.509,02 | 1,02% | G01-X | NAKİT TUT | BLS istihdam raporu — sonuç bilinse de faiz/dolar ilk tepki teyidi eksik |
| 10 | — | — | UNRESOLVED | NAKİT TUT | Hafta sonu |
| 11 | — | — | UNRESOLVED | NAKİT TUT | Hafta sonu |
| 12 | 4.598,55 | 0,73% | UNRESOLVED | NAKİT TUT | Fed/kurumsal güven anlatısı için as-of bağımsız ilk baskı teyidi yok |
| 13 | 4.585,66 | 0,40% | G01-X + ORG06 | NAKİT TUT | BLS Aralık enflasyon (CPI), Fed bağımsızlığı haberi; iki olası kanal |
| 14 | 4.626,07 | 0,26% | G01-X | NAKİT TUT | BLS PPI programı; makro kanal teyidi eksik |
| 15 | 4.614,82 | 0,12% | G01-X | NAKİT TUT | BLS ithalat/ihracat fiyatları; makro kanal teyidi eksik |
| 16 | 4.595,52 | 0,02% | UNRESOLVED | NAKİT TUT | Belgelendirilmiş ilk tetikleyici yok |
| 17 | — | — | UNRESOLVED | NAKİT TUT | Hafta sonu; kaynaklı ilk baskı yok |
| 18 | — | — | UNRESOLVED | NAKİT TUT | Hafta sonu; fiyat teyidi yok |
| 19 | — | — | ORG06 | NAKİT TUT | Grönland tarife gerilimi; Reuters tarihli haber, ABD tatili |
| 20 | 4.762,95 | 0,69% | UNRESOLVED | NAKİT TUT | Ekonomik ilk haber/same-UTC aktarım eksik |
| 21 | 4.831,69 | -1,06% | ORG07 | NAKİT TUT | Tarife gerilimi çözülmesi ORG07 adayı, ilk baskı saati doğrulanmadı |
| 22 | 4.935,69 | -1,86% | ORG07 + ORG09 | NAKİT TUT | Tarife rahatlaması ORG07 ile altın talebi ORG09 rakip anlatılar |
| 23 | 4.983,79 | -1,55% | UNRESOLVED | NAKİT TUT | Spesifik doğrulanmış yeni kaynak yok |
| 24 | — | — | UNRESOLVED | NAKİT TUT | Hafta sonu |
| 25 | — | — | UNRESOLVED | NAKİT TUT | Hafta sonu |
| 26 | 5.009,54 | -0,92% | UNRESOLVED | NAKİT TUT | Spesifik doğrulanmış yeni kaynak yok |
| 27 | 5.178,68 | -1,66% | G01-X | NAKİT TUT | Fed toplantısı ilk günü; sonuç ancak açıklanınca bilinir |
| 28 | 5.414,58 | -1,66% | G01-X | NAKİT TUT | Fed 14:00 EST'de faizi değiştirmedi; 22:00 UTC karar öncesi bilinir |
| 29 | 5.378,82 | 0,43% | UNRESOLVED | NAKİT TUT | Teyitli teminat/pozisyon ilk nedeni yok; fiyat riskini DNA sanma |
| 30 | — | — | ORG02 + ORG10 | NAKİT TUT | Warsh Fed adayı, USD/metaller; ancak 21:45 HistData 14/15 ve karar barı geçersiz |
| 31 | — | — | UNRESOLVED | NAKİT TUT | Hafta sonu |

**Kapsam açıklaması:** 31 takvim günü kaydedildi; fiyat modelinin tam karşılaştırılabilir **19 kapanış gözlemi** var. Kalan **12 gün** tatil/hafta sonu veya tamamlanmamış M15 nedeniyle sinyal üretmedi. **30 Ocak 21:45** HistData barı 15 yerine **14 kaynak dakika** taşıyor, bu nedenle karara sokulmadı. İşlem günü fiyatları geçmişte görülse bile o tarihin fiyat kararında 22:00'den sonrasını kullanmadık. Tablo alt DNA kodları otomatik mekanizma doğrulaması değil, araştırılacak **aday**.

## 3. Gerçek 100 USD portföy sonucu ve karşılaştırma

| Başlangıç 100 USD | Ay sonu değer | Değişim |
|---|---:|---:|
| **Ekonomik DNA sıkı kanıt kapısı** | **100,00 USD** | **%0,00** |
| **Geçmiş fiyat benzerliği — ayrı tanısal karşılaştırma** | **100,00 USD** | **%0,00** |
| İlk kullanılabilir 2 Ocak 09:00 UTC Dukascopy ASK ile altın al-tut, 30 Ocak 21:45 UTC BID ile tasfiye, %0,8 iki taraf | **109,79 USD** | **+%9,79** |

Altın al-tut referansının ham işlem fiyatları: 2 Ocak `ASK=4.387,435`, 30 Ocak `BID=4.895,118`. Formül `100 × 0.992 / 4387.435 × 4895.118 × 0.992 = 109.7933`. Aynı kaynağın BID/ASK farkı dahil; **banka makası/kur/swap/stopaj/slippage yok**, gerçek banka performansı değil. Giriş veya çıkış **0 adet** olduğu için DNA/numerik modelin 100 USD'si gerçek spot fiyattan bağımsız nakit bakiyesidir.

**Fiyat modelinin işlem üretmeme nedeni:** 5 Ocak benzer geçmiş durumların ileri beş-seans medyan hareketi **+%1,08** ve UP olasılığı 14/21=**%66,67**. Olasılık eşiği geçse de +%1,08, iki taraf maliyet başabaş **%1,6194'ün altında**; AL yok. 22 Ocak medyan **−%1,86** ama DOWN işareti **12/21=%57,14** olduğu için SAT adayı yok. 28 Ocak medyan **−%1,66**, DOWN yalnız **11/21=%52,38** ve geçmişe normalize mesafe aşırı geniş; aşırı güçlü fiyat hareketi modelin analog evreninden **taşmış**. 29 Ocak medyan **+%0,43**: fiyat-analog sistemi ertesi günkü satışı önceden işaret edemedi. Bu 29 Ocak sonucunu bilmeden kurulmuş sabit modelin **somut sınırlamasıdır**.

## 4. Somut ekonomik DNA öğrenimi: hangi olayları tanıdı, hangilerinde başarısız?

- **Jeopolitik ilk haber → altın riski (ORG04):** 3 Ocak Venezuela kaynaklı haber tarihi doğrulanabiliyor; 5 Ocak fiyat büyümesi mevcut. Ancak geçmiş fiyat benzerliği medyan tahmininin maliyeti aşmaması ve eş-UTC güvenli liman / faiz / USD teyidinin yokluğu **H-UP01'de geçerli AL üretmedi**. Sonradan görülen yükseliş iyi bir açıklayıcı hikâye olabilir, ex-ante ekonomik üstünlük kanıtı değildir.
- **Politik belirsizlik ↔ rahatlama (ORG06/ORG07):** Grönland tarife haberleri ve geri adımla ilişkili açıklamalar farklı günlerde; ilk baskı saati belirsizse 21/22 Ocak'taki fiyat teyidini önceden ekonomik dalga olarak bilmiş gibi işlem verilemez. Özellikle bu olaylar, tek başlık=tek altın yönü yaklaşımını çürütebilir.
- **Fed/makro (G01):** NFP ve CPI resmî duyuruları doğru günlü; 28 Ocak FOMC 14EST açıklaması da 22UTC'den önce. Ancak 2Y/real rate/USD/metaller ve alt bileşen beklentisinin eşsaatli paneli **tam değil**. Bu yüzden makrodan kalibre edilmiş al/sat sinyali türetilemedi.
- **Aşırı ivme → risk dönüşü (ORG09/ORG10):** Geçmiş 2023–25 analoğu 27–28 Ocak'ta yüksek fiyat düzeylerinin yalnız kısıtlı benzerine sahipti; model aşırı geniş mesafeli kaldı. 29 Ocak'ta ekonomik nedeni teyit eden, önceden belirlenmiş ORG10 kapısı da yoktu; **30 Ocak satışından kaçınmayı öngörmüş sayamayız**.

## 5. Bilimsel sonuç / negatif bulgu

**Düzeltmeden sonra kazanç yok.** Yapılan şey, Ocak'ın fiyat sonucunu kural seçimine sokmamak için önceden yazılmış **denetimli yeniden yürüyüş**. Önceki araştırmada Ocak görülerek seçilen başarılı eşikler kaldırılınca sistem **0 işlem**, **0 getiri**, pasif maliyetli altının **9,79 yüzde puan gerisinde** kaldı. Bu olumsuz sonuç korunmalı; yeni analoga Ocak sonunu bildiğimiz için ekstra kurallar eklemeyiz.

**Geçerlilik sınırı:** Model özellikleri ve eğitim etiketleri 2026'dan önceki veriye kapalı olsa da araştırmacı daha önce bu ayın tüm sonuçlarını gördü. Dolayısıyla **tam bağımsız tarihsel körlük sağlanmadı**. Bu yeni dosya `INPUT_TIME_RESTRICTED_DIAGNOSTIC_COMPLETE / NOT_BLIND_OOS / NOT_TRADING_VALIDATED` statüsündedir. Gerçek zamanlı ekonomik DNA aktarımını tamamlayacak veri ve geleceği görünmemiş sınama dönemleri ayrıca gerekir.

**Dosyalar:** [2026'yı ölçmeden önce commit edilmiş yöntem](OLAY_02_JAN2026_PRE2026_FROZEN_REPLAY_PROTOCOL_20261014.md) · [31 gün / her tarihte 21 kaynak analog ve ham score + source QA](OLAY_02_JAN2026_PRE2026_DONDURULMUS_DNA_31_GUN_REPLAY_20261014.csv). Eski tarihli hatalı raporun `INVALIDATED_CONSTRAINT_BREACH` işareti kaldırılmaz; bu çalışma onun *yerine* geçer ama onu silmez.

## 6. Beş seanslık tahmin ile SONRADAN gerçekleşenin ayrıştırılmış denetimi

[14 olgunlaşmış beş-seans tahmin/gözlem CSV](OLAY_02_JAN2026_PRE2026_DNA_5_SEANS_TAHMIN_GERCEKLESEN_DENETIMI_20261014.csv) yalnız **bütün günlük kararlar üretildikten sonra** etiketlendi. Bu gözlemlerin hedef pencereleri örtüşür: **14 bağımsız deney sayılmazlar**.

| Ölçüt | Sonuç |
|---|---:|
| Ocak içinde +5 tamamlanmış fiyat gözlemi bulunan tahmin | **14** |
| İleri beş-seans **yön işareti** tutanlar | **11/14 (%78,57)** |
| Medyan fiyat tahmini ile gerçekleşen 5-seans getirisi arasındaki MAE | **5,46 yüzde puan** |
| Örnek: 21 Ocak tahmini → 28 Ocak gerçekleşen | **−%1,06 → +%12,06** |
| Örnek: 22 Ocak tahmini → 29 Ocak gerçekleşen | **−%1,86 → +%8,98** |

**Yorum:** 11/14 işaret doğruluğu yüksek görünür; ancak 14 hedef örtüşen, aynı trendde ileri beş seanstan üretildiği ve araştırmacı Ocak'ı önceden bildiği için bağımsız yön-doğruluk istatistiği olarak terfi ettirilmez. Hareketlerin büyüklüğü özellikle yükseliş rejiminde ağır biçimde **az tahmin edildi**. Altının gerçekte daha fazla yükselmiş olması, modelin o gün maliyet şartını geçmeyen `BUY` sonucuna geriye dönük kâr yazma yetkisi vermez. Eski ANA-01'deki piyasa rejimi ve makro DNA değişkenlerinin eşsaatli aktarım eksikliği bundan dolayı esas araştırma darboğazıdır.

