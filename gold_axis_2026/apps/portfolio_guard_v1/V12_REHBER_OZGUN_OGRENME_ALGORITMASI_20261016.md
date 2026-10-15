# V12 · REHBER: Rejim Evresi Hafızası, Benzetim ve Eylem Revizyonu

**16 Ekim 2026 — özgün kural + episodik model araştırması — eski modeller değiştirilmedi.**

## Kullanıcının esas talebine verilen yanıt

ANN modelini tekrar kurmak değil; ANN'nin temel prensibi olan **girdi → örüntü çıkarımı → öngörü → hata → öğrenerek uyarlama** dizisini özel bir altın/nakit karar algoritmasına dönüştürmek. V12 REHBER yapay sinir ağı değildir. Geçmişe ait olay hafızası, farklı mercekler, gecikmeli gerçekleşme ve karşı-olgusal hata beslemesi kullanır. Bu özel tasarıma bilimsel literatürde tamamen emsalsiz bir yöntem olduğu iddia edilmez; episodik bellek, kernel benzerliği ve online expert aggregation ilkelerini bu problem için özgün şekilde birleştirir.

## Mimari ve özgün değişkenler

1. **Hafıza:** 2023–2026 Eylül tarihli SHA kilitli veri kaynaklarında 6.724 kronolojik üç saatlik piyasa kaydı; V11 veri oluşturucusundan 947 gerçek 14 günlük sonuç etiketi. Şimdiden bilinen gelecekteki fiyatlar karar sürecine giriş yapamaz; yalnızca çıkış saati geçmişte kalmış kayıtlar hafızaya alınır.
2. **Üç piyasa merceği:** TREND, STRESS, STRUCTURE. Aynı günün altın eğilimi, çapraz piyasa risk yayılımı ve fiyat çubuğunun davranış karakteri farklı benzerlik ölçüleriyle geçmişteki koşullarla eşleşir. Her merceğin yakın tarihi örnekleri kernel ağırlığıyla bir getiri dağılımı üretir; **her 14 günlük bloktan en çok bir komşu** alır.
3. **İleriye bakmayan tahmin:** 4 ve 14 günlük altın al-sat brüt yönü değil, **hem alışta %0,8 hem satışta %0,8 kesilmiş net getiri**; kârlı olma olasılığı, %20 olumsuz kuantil, dağılım genişliği ve benzeyen geçmiş vakalar.
4. **Öğrenen güven:** Her merceğin geçmiş *tahmini*, onun gerçek 14 günlük sonucu belli olduktan sonra hatayla karşılaştırılır. Hata büyüdükçe güven ağırlığı azalır; yalnız olgunlaşmış 14 günlük bloklar esas alınır.
5. **Öğrenen karar marjı:** NAKİT iken kâr kaçırıldıysa karar marjı sınırlı miktarda azalır; NAKİT iken yanlış AL öngörüsü varsa artar. Bu düzeltme yalnız gerçekleşme sonrasında yapılır; altın içindeyken geç SAT işaretleri de kaydedilir. Risk koşullarında BEKLE seçimi ayrı bir aksiyondur.
6. **Nedensel icra:** Sinyal Türkiye 09.00 kontrolünde oluşturulur; işlem aynı anda değil, ancak sonraki Türkiye 12.00 banka kontrolünde (veya takvimli ilk uygun sonraki kesitte) fiyat vekili üzerinden gerçekleşir. Banka hesabına bağlantı, gerçek BID/ASK kotasyonu ve otomatik emir yok.

## Gerçek, çalıştırılmış deney — şeffaf negatif kontroller

| Dönem | Başlangıç USD | V12 REHBER sonucu | Karşılaştırma |
|---|---:|---:|---|
| 2024 | 100,00 | **100,00** | Hiç alım yok; pasif altın ~123,85 USD |
| 2025 | 100,00 | **100,00** | Hiç alım yok; pasif altın ~160,42 USD |
| 2026 Şubat–Eylül | 119,753917 | **135,663808** | Yalnız incelenmiş tarihsel dönemde |
| 2026 Şubat–Eylül, Şubat başında hafızayı dondur | 119,753917 | **130,591594** | 11 işlem / aktif hafıza 6 işlem |

2026 aktif hafıza fiyat vekili üzerinden **3 AL + 3 SAT** gerçekleştirdi: 5 Şubat AL, 10 Şubat SAT, 17 Şubat AL, 23 Şubat SAT, 23 Mart AL, 1 Nisan SAT (Türkiye 12.00 saatleri). Tüm işlemlerde %0,8 giriş ve %0,8 çıkış bedeli düşülmüştür.

**Önemli bilimsel ayrım:**

- Yeni olgunlaşmış vaka hafızasını kapatınca 2026 sonucu 135,663808 USD'den 130,591594 USD'ye geriledi; geçmiş fiyatlar üzerinden yaklaşık **5,072214 USD fark**. Bu, hafıza eklemenin kararları etkilediğini gösterir ancak bağımsız nedensel yatırım başarısı kanıtlamaz.
- **Sabit karar marjı** veya **sabit mercek güven ağırlığı** kullanan ablasyonlar 2026'da ana modelle **aynı 6 işlemi** ve **aynı 135,663808 USD sonucu** verdi. Dolayısıyla bunların işlem kalitesine ek katkısını henüz kanıtlayamadık. Bunları 'iyileştirme' diye sunmak yanlış.
- Güvenlik eşikleri artırılmış varyant (`REHBER_SAFETY`) 2026 boyunca **nakitte kaldı**; 119,753917 USD. Bu da aşırı temkinliliğin fırsatları kaçırabileceğini gösteriyor.
- 2024/2025'te işlem yapılamaması çok ciddi bir **yüksek getiri rejimini tanıyamama** sorunudur. Model yalnız krizden korunup yükseliş yılında altına katılamıyorsa genel amaçlı başarılı model sayılamaz.

## Bilimsel sınırlamalar

**Kör test yok.** 2024, 2025 ve 2026 sonuçları önceki V7–V11 araştırmalarında görüldü. V12'de parametreleri yalnız 2026'a uydurmadık; fakat parametre seçimi için tarihler zaten bilinen tarihsel deneyler olduğundan yeni performans gerçek ileriye dönük doğrulama değildir.

**Bağımsız gözlem ≠ 947 etiket.** Günlük 14g hedefler birbirine örtüşür. REHBER komşuları tarihsel 14g bloklarda tekilleştiriyor; aynı şekilde tahmin hatası ağırlıklarını her 14 günlük bloktan en fazla bir örnekle güncelliyor. Fakat bağımsızlık kesin değildir; makro şoklar ardışık bloklara da yayılabilir.

**Haber DNA'sı henüz sayısal doğrulanmış veri olarak yok.** OLAY-02 / ÖĞREN-03 veri setindeki olayların ilk yayın zamanı (firstprint) / karar anında erişilebilir ekonomik göstergesi doğrulanmış değil; REHBER yalnız teknik/çapraz piyasa durum hafızası kullanıyor, haber yorumladığı iddia edilemez.

**Banka fiyatı ve yürütüm:** %0,8 alış ve %0,8 satış vekil fiyat üzerine uygulanır, fakat bankanın gerçek ASK/BID, ek kur farkı, emir gecikmesi ve fiyat kayması bilinmiyor. Şimdilik işlem önerisi olarak uygulanamaz.

## Bundan sonraki gerçek geliştirme soruları

- Hafıza kendini nasıl yeniden temsil etmeli? Aynı olaya benzeyen ama farklı sonuç doğuran vakaları hangi önceki ekonomik haber/stres verisi ayırt edebilir? İlk yayımlanma saatlerini doğrula.
- 2024–2025 yükselişlerinin neden atlandığını incelemek: koşullu risk eşiği, kazanç olasılığının kalibrasyonu, tüm piyasa rejimlerini tanıma ve geçmişteki pozitif trend epizotlarını gereğinden fazla reddetme.
- Yeni doğrulanmış olay çıkınca önce öngörü üret, tarih-saatli kararı dondur; hedef vade dolunca gerçekle karşılaştır ve yalnız ondan sonra ağırlıkları güncelle.
- Net getirinin yanında nakit, pasif altın, piyasa rejimine göre max drawdown, işlem sayısı, tam işlem maliyeti ve vaka/ay bazlı farklılaşma raporları.
- Aynı zamana bağlı sonuçlardan bağımsız başarı üretmemek için zaman bloklu doğrulama, purging/embargo, episode bootstrap ve zaman dışı gerçek prospektif deney.

## Üretilen ve doğrulanan kod

- `v12_episodic_memory.js` — piyasa mercekleri, zamana göre filtrelenmiş hafıza, nonparametrik komşu tahmini, çevrimiçi güven öğrenmesi.
- `v12_rehber_agent.js` — AL/SAT/BEKLE kararı, gecikmiş banka kesitinde komisyonlu işlem, olgunlaşmış sonuçlarla hata ve karar marjı güncellemeleri, dondurulmuş hafıza karşı deneyi.
- `v12_rehber.test.js` — olgunlaşmamış sonuçları engelleme, geçmiş komşuların tekilleştirilmesi, negatif yıllık kontroller, hafızayı dondurma ablasyonu, işlem saati ve gelecekteki fiyat değişiminin önceki kararı etkilememesi.
- `GET /api/algorithm/v12/rehber` — sadece araştırma sonuçlarını döndürür. Sol menü: **V12 REHBER özgün karar hafızası**.

**Sonuç:** Kullanıcının talebi doğrultusunda yeni bir ANN kopyası yerine, başka yapıdan öğrenme ilkelerini uyarlayan özgün ve çalışır bir hafıza/karar algoritması kuruldu. Geliştirilmesi gereken kritik aşama, geçmişten öğrendiklerini sadece 2026'da değil **2024 ve 2025 gibi yükseliş rejimlerinde de** etkili kararlara dönüştürebilmesidir. Model terfi edilmedi, gerçek emir üretilmedi.
