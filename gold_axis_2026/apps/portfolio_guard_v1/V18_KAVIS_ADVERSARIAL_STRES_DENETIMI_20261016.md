# V18 KAVİS — Saldırgan stres denetimi, mantık düzeltmeleri ve terfi kararı

**Tarih:** 16 Ekim 2026  
**GitHub dalı:** `research-gold-v18-adversarial-robustness-20261016`  
**Ana sürüm:** V17 saklandı; V18 ayrı geliştirme.  
**Durum:** **Yalnız sentetik araştırma / canlı işlem kapalı / gerçek XAU/USD testi yapılmadı.**

## 1. Hangi V17 kusurları tespit edildi?

1. **Çoğaltılmış olay zehirlemesi:** Aynı `evidenceId` bir sinyale birden fazla konup G05 veya diğer grup puanı yapay artırılabiliyordu.
2. **Fiyat/veri kaynağı bozulması:** Yanlış yüzde ölçeği (ör. 100000 yerine 100), çok eski girdi, geçersiz/olmayan kaynağın etkin olmaması ayrıştırılmıyordu.
3. **Tek bozuk banka fiyatından Q zehirlenmesi:** Açık pozisyonun sonraki banka checkpoint'inde çok uç fiyat geldiğinde çift-Q modelinin öğrenilmiş katsayıları kalıcı biçimde etkilenebiliyordu.
4. **`confirmedExtremeQuote=true` yeterli görülmesi:** Sırf tek boolean ile olağanüstü fiyat doğrulamasını atlamak mümkün idi.
5. **Değişken banka maliyeti:** Öğrenilmiş SWITCH değeri her zaman normal banka maliyetinin sürmesini varsayıyordu; giriş fiyatındaki fiili komisyon ve sinyal anındaki bildirilmiş yeni komisyon birlikte izlenmiyordu.
6. **Yetersiz zorlayıcı senaryo seçimi:** Daha önceki 5+16 yapay senaryo yazılım davranışını açıklıyor ama maliyet, dağılım kayması, veri zehirlemesi ve uç kayıpları aynı çatı altında sınamıyordu.

## 2. V18'de gerçek kaynak kodu değişiklikleri

- **Olay ID tekrarı yasak:** Tek kararın olay listesinde aynı kanıt ID ikinci kez geçerse sinyal baştan reddedilir. `G01...G07` bağımsız öğrenme özellikleri korunur.
- **Veri birimi / bayatlık filtresi:** Market özelliği 500 mutlak yüzde-puanı aşarsa reddedilir (kullanıcı ayarlayabilir). `featureAvailableAt` sinyalden 96 saatten fazla eskiyse sinyal reddedilir. Bunlar **uygulama güvenlik eşikleridir, piyasanın doğrulanmış istatistiksel sınırları değildir**.
- **Gerçek şok / hatalı kotasyon ayrımı:** Son geçerli banka fiyatına göre aşırı log hareket varsa yeni checkpoint **işlem ve eğitim güncellemesi yapmadan karantinaya alınır**; bekleyen emir önerisi kaybolmaz. Varsayılan hareket eşiği günlük 35 log yüzde-puandır. `confirmedExtremeQuote` boolean **tek başına yeterli değildir**.
- **Uç fiyatın koşullu serbest bırakılması:** En az iki *farklı* veri sağlayıcı ID'si, en fazla bir saat eski gözlem zamanı, önerilen fiyatla log-fiyat farkının en çok %5 olması ve `confirmedExtremeQuote=true` gerekir. Bu sözleşme gerçek iki bağımsız veri sağlayıcısı kullanıldığını **kanıtlamaz**; adapterde ayrıca izin listesi / imzalı kayıt / erişim zamanı doğrulanmalıdır. Onaylı gerçek çöküşler kod tarafından reddedilmez.
- **Komisyonun asof farkı:** Gerçek fill anında `bankFeePerSide` kaydedilir, geçmiş epizodun ödülü o bacağın maliyetiyle hesaplanır. `bankFeeQuote` sinyal anında yayınlanmışsa (en çok 6 saat eski) öğrenilen tarihsel komisyon ortalamasından **yalnız fark kadar** SWITCH avantajı düzeltilir:
  ```
  fee_delta = 100[ ln(1 - posted_fee) - ln(1 - EWMA_historical_fee) ].
  Q_SWITCH_net_score <- Q_SWITCH_net_score + fee_delta
  ```
  Maliyet tekrar tam olarak eklenmez. `KEEP` sıfır bacak maliyetini korur.
- **Eksik/bekleyen banka fiyatı sonrası toparlanma:** Karantinaya alınan sahte fiyat eğitim başlığına girmez. Daha sonraki doğrulanmış kontrol noktasından hesaplama ve sanal işlem önerisi devam eder.
- **Temel yapı korunur:** V17'nin çift-Q Bellman hedefi, zaman-etiketinden bağımsız 20 özellik, asof veri sözleşmesi, 7 olay ailesi, üstel unutan gradyan istatistiği ve dört CASH/GOLD × KEEP/SWITCH eylemi değiştirilmedi.

## 3. Gerçekten çalıştırılan testler

**CI: 63 test geçti, 0 başarısız** (V16/V17 temel testleri + V18 saldırgan testleri).

### Veri zehirlemesi / nedensellik
- 200 rastgele yanlış piyasa girdisi + 100 geçersiz banka maliyeti: model durumuna yan etki olmadan ret.
- 40 deterministik yapay piyasada, 27. noktaya 10.000 kat sahte fiyat veya 0,0001 kat yanlış fiyat enjekte edildi. V18 bu fiyatları karantinaya aldı; aynı günün temiz 12:00 checkpoint'inde döndükten sonra **bütün Q/QB katsayıları temiz referans deneyle birebir eşleşti**. Bu koruma davranışının doğrudan teknik kanıtıdır.
- 2.000 günlük ortak takvim kaydırmasında öğrenilmiş Q/QB katsayıları aynı kaldı: yıl/tarih kimliği ezberlenmiyor.
- Çift kaynak iddialarından biri aynı sağlayıcıysa, gelecekte zaman damgalanmışsa veya farklı fiyat veriyorsa aşırı hareket için eğitim/işlem izni verilmedi.
- Doğrulanmış kurgusal %80 düşüş ve `1e-75 ↔ 1e75` uç fiyat dizilerinde sayısal NaN/Infinity veya checkpoint bozulması olmadı.
- Bayat gelecek olaylar, kopya `evidenceId`, yanlış yüzdelik birim, bozuk model restore ve uygunsuz banka saati engellendi.

### Ekonomik 128 kurgusal stres dünyası
8 dünya ailesi × 8 başlangıç tohumu × 2 maliyet koşulu (her yön %0,8 veya %2,5), her dünyada 300 karar sırası. Başlangıç sermayesi 100 USD. Her kararın özelliği **yalnız geçmiş gözlemlerden** hesaplandı; gelecek fiyat yatırım sinyalinden sonra açığa çıktı.

| Kriter | V18 |
|---|---:|
| 128 dünyanın V17'den farklı sermaye sonucu | **0** |
| Medyan nihai sermaye (iki maliyet birlikte) | **165.7755 USD** |
| En kötü nihai sermaye | **67.9925 USD** |
| Medyan maksimum geri çekilme | **%16.171** |
| MDD %95 örnek yüzdelik | **%26.687** |
| Nakit başlangıcı 100 USD'yi aşan dünyalar | **99/128** |
| Aynı dünyadaki pasif altını aşanlar | **80/128** |
| Maliyet %0,8 — 64 dünya medyan final | **182.1422 USD** |
| Maliyet %2,5 — 64 dünya medyan final | **117.0007 USD** |

**V18 ve V17'nin temiz veri fiyat yollarında 128/128 eşit çıkması tasarım gereğidir**, çünkü V18 güvenli veri kapıları ve asof makas düzeltmeleri ancak girdiler farklılaştığında etkinleşir. Sahte fiyat onayı için 40 ek zehirleme deneyi yapıldı; bu deneyler bir stratejinin gerçek kâr artışı değil, *temiz eğitimle aynı sonucu tekrar üretme* başarısını ölçer.

Yapay fiyat dağılımı, yaşanan piyasanın modelini temsil etmeyebilir. Bu sonuçlar finansal kâr garantisi ve yeni dönemde kör test **değildir**.

## 4. En önemli çözülmemiş riskler

1. **Finansal kuyruk riski:** V18 ağır stresin en kötüsünde 100 USD'den 67,99 USD'ye düştü. Bu, kârlılık/koruma sorununun çözüldüğü iddiasını kesin olarak engeller.
2. **Gerçek şok sırasında güvenli işlem:** Karantinaya alınmış tek bankacılık fiyatı sebebiyle bekleyen işlem önerisi gecikebilir. Kullanıcı o anda GOLD'daysa gerçek kayıp yine yaşanabilir. Karantina **zarar durdurma mekanizması değildir**.
3. **İki kaynak kanıtı sahte olabilir:** Model sağlayıcı iddiasını denetler, bankadan API imzası veya sağlayıcı sunucusundan gerçek kimlik kanıtı çekmez. Üretimde ayrı attestation zorunludur.
4. **Gerçek bid/ask yok:** Banka komisyonlarının üstüne spread/slippage likiditeye göre değişebilir. Araştırma, sadece banka vekil kotasyonu ve oransal işlem maliyeti kullanır.
5. **Fiyata dayalı kötü girdiler eşik altında kalabilir:** %35'ten küçük ama bozuk kotasyon, başka dış doğrulama mekanizması olmadığında yakalanmaz.
6. **Piyasa genellemesi / model seçim yanlılığı:** V13–V18'e dek birçok sürüm defalarca seçilip yeniden sınandı. 128 sentetik dünya da gerçek bağımsız altın veri dönemi sayılamaz. Finansal anlamlılıkta seçim sayısı, çoklu test ve risk dağılımı ayrıca raporlanmalıdır.
7. **Yola bağımlı risk kontrolü:** V18'de temkinli Q avantajı vardır, ama kullanıcı tanımlı toplam portföy maksimum drawdown bütçesini *zorlayan* bir politikası yoktur. Portföy tutma yaşı ve likiditeye dayalı yeniden giriş hâlâ geliştirme konusudur.
8. **Asıl olay kaynakları:** OLAY-02/ÖĞREN-03 vakalarının ilk görülebilir yayın tarihlerini kanıtlayacak gerçek kaynak adaptörü henüz entegre edilmemiştir.

## 5. Yönetim kararı

**V18 yalnızca araştırma sürümü olarak korunsun; V17 ve önceki algoritmalar silinmesin.** Algoritma kurgusal veri zehirlemesine teknik olarak daha dirençlidir ve kaynak/komisyon sözleşmeleri iyileşmiştir. Ancak **gerçek altın fiyatında yüksek kârı veya kriz dayanıklılığını kanıtlamadığı için canlı terfi edilmesin**.

Önerilen bir sonraki bilimsel adım: kullanıcı risk bütçesine dayalı portföy zarar sınırı ve kuyruk-riski eylem öğrenmesini ayrı deney dalında araştırmak; ardından asof veri adaptörü ve gerçek banka fiyatı sınaması. Dondurulmuş algoritma kör dönem veri geldikten sonra değiştirilirse önceki test artık kör sayılamaz.

## Kaynak yaklaşımı

- Hado van Hasselt, Double Q-learning (NeurIPS 2010): https://papers.neurips.cc/paper_files/paper/2010/hash/091d584fced301b442654dd8c23b3fc9-Abstract.html
- Gama ve ark., A Survey on Concept Drift Adaptation (ACM 2014): https://doi.org/10.1145/2523813
- Fujimoto, van Hoof, Meger, Addressing Function Approximation Error in Actor-Critic Methods (ICML 2018): https://proceedings.mlr.press/v80/fujimoto18a.html
- Bailey & López de Prado, The Deflated Sharpe Ratio (JPM 2014): https://doi.org/10.2139/ssrn.2460551
