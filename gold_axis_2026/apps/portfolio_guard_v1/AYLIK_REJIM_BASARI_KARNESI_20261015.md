# 2026 Aylık strateji başarısını ölçme protokolü

**15 Ekim 2026 · Araştırma · Geleceği bilen referans işlem talimatı DEĞİLDİR**

## Tanım

Bir takvim ayı için yalnız iki basit seçenek:

- **NAKİT:** Hiç altın alma; net aylık getiri sıfır.
- **ALTIN:** O ayın ilk Türkiye 09:00 3s araştırma kesitinde al; son Türkiye 15:00 kesitinde tasfiye et; alış ve satış için ayrı ayrı %0,8 maliyet uygula. Ayrıca gerçek banka ASK/BID farkı, kayma ve kur etkisi bilinmiyor.

`goldNetFactor=(1-0.008)^2*(exitMID/entryMID)`. ALTIN'in daha iyi olması için yalnız komisyondan doğan fiyat artış eşiği **%1,6194069**. Ocak 2026 ayrı 100 USD başlangıç örneğidir; Şubat–Eylül kesintisiz araştırma bakiyesi 119,753917 USD nakitten başlar.

**İki farklı etiketin birbirine karıştırılması yasak:**
1. `hindsightWinner`: Ay sonunda, son fiyat görülünce öğrenilen hedef. Gerçek zamanlı algoritma başarısı değildir.
2. `laggedSelected`: Önceki ayın sonunda öğrenilen en iyi stratejiye bakıp gelecek ayın ilk işlem anında seçilen, geleceği kullanmayan çok basit kıyas modeli.

Aylık altın/para kıyaslaması sadece **tek giriş-tek çıkış** strateji ailesinin teorik karşılaştırmasıdır. Ay içi aktif al-sat yapan V7'nin kâr üst sınırı sayılmaz; V4/V5 fiyat ve emir sözleşmelerinin birebir eşiti değildir.

## 2026 ay bazında gerçekleşen fiyat-temelli sonuçlar

| Ay | Aylık ALTIN net getirisi | Ay sonunda belli olan ideal strateji | Bir önceki aya bakarak gerçek zamanda seçilen |
|---|---:|---|---|
| Ocak | +%15,3665 | ALTIN | Şubat stratejisi için eğitim referansı |
| Şubat | +%12,2182 | ALTIN | ALTIN |
| Mart | −%16,6151 | NAKİT | ALTIN **HATA** |
| Nisan | −%2,3663 | NAKİT | NAKİT |
| Mayıs | −%3,0978 | NAKİT | NAKİT |
| Haziran | −%12,1613 | NAKİT | NAKİT |
| Temmuz | +%0,3365 | ALTIN (marj çok küçük) | NAKİT **HATA** |
| Ağustos | +%7,8539 | ALTIN | ALTIN |
| Eylül | −%6,9683 | NAKİT | ALTIN **HATA** |

Yalnız iki sınıfa göre geçmiş ayın kazananını kopyalamak **5/8** ayda aynı seçimi verdi. Ama **%62,5 sınıflandırma doğruluğu kârlı bir yöntem değildir:** Mart'ta düşüşü yakalayamadı ve Eylül'de geç satış yaptı.

## Kesintisiz 119,753917 USD Şubat–Eylül portföy kıyası

| Yöntem | Eylül sonu USD | Pozisyon seçimi kanıtı |
|---|---:|---|
| Ay bittiğinde en iyi kararı bilme; aylık iki alternatif içinde hindsight ideal | **145,427924** | **Geleceği kullandığı için uygulanamaz; hedef referansı** |
| Önceki ayın kazananını gelecek ayda aynen uygulama | **112,436454** | **As-of geçerli; kârsız ve nakitten kötü** |
| V7 çift ufuk + çevrimiçi düzeltme + XAU/NQ stres SAT | **123,529545** | 2026'nın bilinen verisine göre oluşturulmuş geri test; bağımsız başarı değil |
| Nakit tutma | **119,753917** | İşlem yok |

**V7 ile aylık hindsight hedefin portföy değeri farkı:** 21,898378 USD. Bu tutar kaybedilmiş **kesin** kâr değildir; modelden farklı, geleceği bilen ve aylık tek işlemle sınırlı bir kıyasın farkıdır.

V7 2026 Şubat performansı 134,385691 USD, Mart sonu 120,203209 USD, Nisan–Eylül sonu 123,529545 USD. Mart düşüşünde aldığı zarar ve Ağustos yükselişini tamamen kaçırması sonraki araştırmanın iki somut `missed_UP / defensive_reentry / drawdown_protection` konusudur. 

Temmuzdaki +%0,3365 net getiri, gerçek banka BID/ASK spreadi nedeniyle sıfırlanabilir; bu ay **GÜÇLÜ ALTIN** sınıfına sokulmaz, `COST_MARGIN_UNCERTAIN` olarak işaretlenmelidir. Bu marjın eşiği aynı ayın sonucuna göre optimize edilmemelidir.

## Uyarlanabilir ay seçimine geçiş kriterleri

1. **Ay başlamadan tahmin:** Önceki ay sonuna kadar yayımlanmış verilerle `P(month_gold_net>0)`, olası büyüklük ve dağılım belirsizliği üret. O ayın gerçekleşeni bir feature değil, yalnız gelecekte olgunlaşacak öğrenme etiketi.
2. **Ay içinde olay desteği:** Aylık yön projeksiyonu risk tercihidir, katı AL emri değil. CPI/NFP/FOMC yayımlanmış sürprizi, USD, reel tahvil, NQ/SI, OLAY-02 olay DNA'sı kaynak as-of doğrulanmışsa zamanla değişen şok katmanını çalıştır. Gerektiğinde aylık UP rejiminde bile koruma SAT, aylık DOWN rejiminde seçici kısa UP AL yap.
3. **Hata karnesi:** Ayın kazananını doğru seçme oranı, net banka sonrası portföy USD, nakde ve altına karşı ek getiri, maksimum DD, işlem başına maliyet ve `monthly_regime_regret` ayrı metrikler olsun. Ay içindeki geç AL, gereksiz SAT, şok görmezden gelme olayları kayıt altına alınsın.
4. **Zaman sıralı eğitim:** 2023–2025 tarihsel geliştirme, 2026 geriye dönük stres analizi; bunların hiçbiri artık kör dönem değildir. Bir sonraki ay için kriterleri önceden kilitle, tamamlandığında gerçek sonucu al, yalnız sonra ağırlıkları güncelle.
5. **Başarı kapısı:** Hindsight aylık kazanana yaklaşmak **tek başına** model terfisi değildir. Nakit + pasif GOLD + V4/V5 + olay-katmanı-kapalı V7 karşısında aynı veri/maliyet sözleşmesiyle güvenilir maliyet-sonrası katkı gösterilmeli; gerçek banka BID/ASK kaynaklanmalı.

## Programda nasıl çalıştırılır?

Dal: `research-gold-portfolio-v7-adaptive-app-20261015`, mevcut `BASLAT.bat`. Sol menü `V7 adaptif öğrenme (araştırma)`; `2026 aylık strateji karşılaştırmasını hesapla` düğmesi.

Kaynak `monthly_regime_benchmark_v7.js`, API `GET /api/algorithm/v7/monthly-regimes`, test `monthly_regime_benchmark_v7.test.js`. Git SHA ile kilitli 3511 satırlık araştırma verisini kullanır. Eski V1–V6 modellerini veya ana manifestleri değiştirmez, banka emri üretmez.
