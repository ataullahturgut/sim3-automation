# V15 KAVİS — Bağımsız kaynak kodu, matematik ve nedensellik denetimi

**16 Ekim 2026 — Araştırma dalı:** `research-gold-v15-formal-audit-20261016`  
**Baz:** `research-gold-v15-kural-yerine-ogrenme-20261016` (orijinal korunuyor)  
**Durum:** Düzeltmeler **28/28 sentetik test** ile geçti. **Tarihsel altın portföy simülasyonu ÇALIŞTIRILMADI. Terfi, canlı emir ve kâr iddiası YOK.**

## 1. Yapılan inceleme

Bütün `v15_kavis_cekirdek.js` (girdi sözleşmesi, durum güncelleme,
5 ufuk, ENTRY/EXIT, MLP, Sugeno-benzeri model, gecikmeli geri bildirim,
banka maliyetleri, kuantil tahmini, kayıp-dual politikası, model saklama)
ve önceki 14 sentetik testi satır satır incelendi. Gerçek altın veri adaptörü
ve var olmayan bankanın gerçek BID/ASK bilgisi doğrulanmadı; bu fazın konusu değil.

## 2. Bulunan ve kaynak kodunda düzeltilen somut hatalar

| Önem | Sorun | Düzeltme |
|---|---|---|
| **Kritik** | Kayıp bütçesinin aynı cezayla SAT kararını engelleyebilmesi | Tahmin edilen 28 günlük altın taşıma kayıp riski, nakitten AL'ı zorlaştırır, GOLD pozisyonda koruyucu SAT'ı destekler; yalnız vadesi dolmuş güvenilir 28 günlük örnekle güncellenir |
| **Yüksek** | Bulanık üyelik merkezlerinin *tahmin hatasına göre* değil, veri merkezine doğru hareket etmesi | Normalleştirilmiş kuralın merkez gradyanı: `dŷ/dc_ij = p_i (rule_i-ŷ)(z_j-c_ij)`; olgunlaşmış hedef hatası ile güncelleme |
| **Yüksek** | Farklı ufukların en yüksek ham kârını tercih etmek | Karşı-olgusal *net log-servet farkı / takvim günü* karşılaştırması; hâlâ tam Bellman-optimal politika değil |
| **Yüksek** | Nakitte 1/3/7 günlük kısa UP fırsatlarının engellenmesi | ENTRY ve EXIT için 1, 3, 7, 28, 56 günlük maliyet sonrası fırsatlar erişilebilir |
| **Yüksek** | Özellikle pazar/geçişte yanlış zamanda banka checkpoint kabulü | Varsayılan UTC 06/09/12 = TR 09/12/15, açıkça izin verilmemiş checkpoint reddedilir; yapılandırılabilir |
| **Yüksek** | Model kaydından bozuk uzman matrisi veya pozisyon geçebilmesi | Boyut, sonlu sayı, sürüm, katsayı, risk, bekleyen emir adayı ve konfigürasyon doğrulaması; hatada restore reddi |
| **Yüksek** | Maliyetsiz iki fiyat arasındaki aşırı oran `P1/P0` taşması | `ln P1-ln P0` hesaplaması; uç pozitif fiyat testleri |
| **Orta** | Çok seyrek ara-fiyat noktasıyla "en kötü ara düşüş" uydurma | Maksimum aralık aşıldığında son fiyat getirisi hâlâ kullanılabilir ama *ara düşüş risk etiketi* geçersiz; risk modeli güncellenmez |
| **Orta** | Uzman kötü başladıktan sonra log-ağırlığı -60'a yapışıp dönemin değişimine cevap verememe | Vadesi dolmuş tahmin hatalarının sönümlü EMA kaybına göre sınırlı log-uzman ağırlığı; eski performans unutulabilir |
| **Orta** | Hafıza kapısına gradyan taşınırken o anda güncellenmiş lineer katsayıyı kullanma | Yerel gradyan için hata oluşmadan önceki katsayı saklanır; halen tam zamansal backpropagation değildir |
| **Orta** | Aynı modelde `GOLD`/ `CASH` pozisyonu dışarıdan keyfî değiştirilebilmesi | Araştırma düzeyinde sanal pozisyon ve aday fill senkronizasyonu; uyuşmayan sinyal reddedilir |
| **Orta** | Doğrudan `settle` çağrısıyla korumasız sonuç öğrenme yüzeyi | Dışa açılan API yalnız model kur, sinyal, alıntı-fiyat al, checkpoint/restore işlevleridir; sonuç olgunlaşmasını motor kontrol eder |
| **Düşük** | Saat dilimsiz tarihlerin sistem yerel zamanına göre farklı okunabilmesi | ISO saat dilimi (Z / offset) zorunluluğu |

## 3. Maliyet ve eylem etiketinin matematik kontrolü

Tamamlanmış bir `h` epizot için iki yön %0,8 ve gözlenen
fiyat `P0,P1` ile:

```
ENTRY(h) = 100 [ln(P1)-ln(P0) + 2 ln(1-0.008)]
EXIT(h)  = 100 [ln(P0)-ln(P1) + 2 ln(1-0.008)]
```

Her bir etiket tek işlem bacağı değil, **bir kez alıp bir kez satılan**
veya **satıp sonra yeniden alınan** iki bacaklı *sonlu* karşı-olgusaldır.
Ek %1,6 karar eşiği uygulanmaz; maliyet **zaten etiketin içindedir**.

Her iki pozisyon da baştaki varlığa `h` sonunda geri döndürülür;
`ENTRY+EXIT=400ln(.992)≈-3.2129` log yüzde puan. Bu
*uzun dönem sonsuz ufuk portföy optimizasyonunun Bellman değeri değildir*.

## 4. Öğrenme ve karar denetimi

- 14 özellik, 5 ufuk, iki eylem ailesi: giriş/çıkış için 10 ayrı alt başlık.
- Her başlıkta AdaGrad doğrusal uzman, 5 bulanık üyeliğe sahip Sugeno-benzeri uzman, 6 gizli nöronlu MLP, ayrı %10 alt-kuantil tahmini.
- Uzman ağırlıkları, ancak sonuç tamamlandığında hata üzerinden güncellenir. Hata büyüklüğü sabitlenir.
- Hafıza kapıları lokal gradyanla güncellenir, uçtan uca gerçek LSTM değildir.
- Fiyat şokunu kullanırken istatistiksel referansın sadece *önceden görülmüş* piyasa noktalarından gelmesi korunur.
- Kararlar için `confidenceZ` ve `minMaturedLabels` halen araştırmacı tarafından belirlenen **temkinlilik/örneklem ayarlarıdır**. Finansal optimal oldukları kanıtlanmadı.
- Seçim başlığı aynı tarihteki birden çok ufka bakar. Ufukların getirisi günlük normalize edildi fakat **çoklu karşılaştırma ve örtüşen etiket belirsizliği** bütünüyle giderilmiş değildir.

## 5. Yeniden üretilen sentetik kabul testleri

GitHub Actions `Gold V15 Algorithm-Only Acceptance` başarılı: **28 test / 28 geçti / 0 hata**.

- Eski 14 test: olgunlaşmamış hedef kullanmama; bankanın sinyalden sonra fiyatı; asof olay; devreden kayıt; sentetik yükselişin ardından düşüşte al/sat.
- Yeni 11 kritik denetim: sahte checkpoint, sahte pozisyon, birime göre ufuk seçimi, koruyucu satış risk işareti, eksik fiyat yüzünden yanlış risk etiketi, farklı banka saatleri ve saklanan bozuk matrislerin engellenmesi, kısa UP giriş.
- Yeni 3 stres testi: çok uç fiyatlar, komisyon nedeniyle hareketsiz düz piyasa ve 460 adımlık deterministik düzensiz fiyat senaryosu.
- **İçerik kontrolü:** V15 CI yalnız sentetik test dosyalarını çalıştırır; V13/V14/2023–2026 gerçek altın PnL kodunu çağırmaz.

## 6. Tamamlanmayan bilimsel/entegrasyon konuları — açık engeller

1. **Tam işlem politikası ve uzun dönem planlama:** V15 şu an sonuç ufkuna göre karşı-olgusal AL/SAT kararını öğrenir. Piyasanın sonraki durumuna bağlı yeniden giriş zamanını ve uzun vadeli değer fonksiyonunu (semi-Markov/Bellman, model-based RL, explicit switching-cost optimal stopping gibi) henüz çözmez. "Tam kâr optimizasyonu" denemez.
2. **Veri kaynağı güveni:** `verifiedFirstPublication` alanı tarih sırasını kontrol eden bir kullanıcı/veri sağlayıcı iddiasıdır; resmi yayın kaynağını doğrulayan bağımsız adapter henüz yoktur. Gerçek haberleri karar motoruna güvenilir şekilde bağlama işi açık.
3. **Üretilen özelliklerin asof denetimi:** `r4,r1,r3,rv,dd,nq6` girdileri gerçekten hangi saatlere ait, publication lag ve NY/TR saatleri doğru mu? Henüz haricî veri adaptörü yapılmadı.
4. **Gerçek banka maliyetleri:** MID veri vekili üstünden %0,8 her yön; bankanın anlık alış/satış fiyatı, slippage, genişleyen akşam makası ve izinli zamanları henüz doğrulanmadı.
5. **Öğrenme kararlılığı:** Aynı anda 5 ufuktan en yüksek *günlükleştirilmiş* fırsatı seçmek çoklu seçim yanlılığı taşır. Her eylem için güven aralığı gerçek etiket bağımsızlığına dayanmaz; ciddi rejim kaymaları ve sürekli yeniden optimizasyon davranışı ayrıca sınanmalı.
6. **Risk:** 28 günlük gözlenen en kötü ara fiyat, **hesap portföy maksimum düşüşü ya da gerçek CVaR değildir**. Risk ikili portföyün açık-kapanış politikasıyla birlikte modellenmeli.
7. **Model karmaşıklığı:** 56 gün etiketi az olduğundan MLP gibi yüksek parametreli uzmanın gerçek kullanımda aşırı uyma riski var. Önce dağılım kalibrasyonu/regularizasyon ve çoklu uzman ablasyonları gerekir.
8. **Kapılı hafıza:** Lokal gradyan geçerli olsa bile zaman boyunca BPTT ile eğitilmiş doğrulanmış LSTM performansı göstermez.
9. **Dışsal olay öğrenmesi:** OLAY-02/ÖĞREN-03 henüz ilk yayın kontrollü makro/düşüş sınıflarına dönüşmüş değil; makro ve altın fiyat nedenselliğini kanıtlamadan zorla kullanmayacağız.
10. **Ekonomik kabul:** Şimdiki 28 test **sadece yazılım/karar sözleşmesini** kanıtlar, kârı değil. Geçmiş döneme göre yeni parametre ayarlama ve bağımsız kör sınama ayrı fazdır.

## 7. Araştırma kararı

**Kod açısından:** Düzeltmeler yapılmış, sentetik sözleşme testlerinden geçmiştir.
**Modelin iş stratejisi açısından:** V15-FormalAudit yalnız aday; ekonomik uygunluk, canlı yatırım, gerçek banka ve bilimsel genelleme **REDDEDİLMİŞ / doğrulanmamış**.
**Bir sonraki öneri:** Simülasyondan *önce* bu dalda karar hedefinin uzun dönem yeniden giriş planını ve veri kaynağının güven modelini tasarlayıp dondurmak. Ardından kullanıcı onayıyla gerçek veri asof adaptörü ve simülasyon. Orijinal V15, V14 ve V13'e dokunulmaz.
