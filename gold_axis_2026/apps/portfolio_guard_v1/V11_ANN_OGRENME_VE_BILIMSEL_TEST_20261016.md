# V11 · Gerçek ANN eğitimi, maliyetli işlem hedefi ve bilimsel sonuç

**16 Ekim 2026.** Dal: `research-gold-v11-ann-supervised-20261016`.
**Durum:** Çalışır ve test edilir ANN araştırma adayı; otomatik yatırım kararına terfi **YOK**.

## V7–V10 neden yeterli olmadı?

V7-V10 ağırlıklı olarak fiyat eğilimi için elle yazılmış karar kuralları ve çevrimiçi doğrusal tahminler kullandı. ANN'nin temel anlamı olan girdi → gizli katman → kayıp → geri yayılım → ağırlık güncellemesi işlem stratejisinin merkezinde değildi. V10'da Mart 2026 yanlış yeniden alımı engellenmiş olsa da Ağustos yükselişi yakalanamadı, 2025 karşı testi pasif altının gerisindeydi.

## Bu çalışmada uygulanan gerçek ANN

- **Topoloji:** 14 sayısal girdi, iki gizli katman (12 ve 8 tanh nöron), iki doğrusal çıkış.
- **Girdiler:** As-of altın getirileri (`r4`,`r1`,`r3`), volatilite, düşüş payı, bar verimliliği, kapanış konumu, drawdown, Nasdaq 6-saatlik dönüşü, ZN değişimi, veri varlığı maskeleri ve geçmişten türetilen iki getiri özelliği.
- **Geri yayılım:** Gerçek analitik çok katmanlı türevler; Huber kaybı, Adam iyileştirici, L2 düzenleme, sabit tohumlu deterministik başlangıç. Gradyan sonlu fark ile birim testte kontrol edilir.
- **Hedef:** Önümüzdeki 4 ve 14 takvim günü sonrasına kadar altın alıp satarsak, hem alış hem satışta %0,8 komisyon sonrasında yüzde kaç net getiri elde edilir? Sinyal Türkiye 09.00'da, alış en erken sonraki Türkiye 12.00 kesitindeki fiyat vekiliyle; çıkış hedefi vade dolduktan sonraki ilk uygun banka kesitindeki fiyat vekiliyle hesaplanıyor.
- **Veri:** 2023–Eylül 2026 tarihli 6.724 satırdan 947 olgunlaşmış, ileri 14 gün karşı etiketi. Bunların önemli kısmı zamansal olarak örtüşür: 947 bağımsız deney değildir.
- **Eğitim:** Eğitim kesitindeki etiketin 14 günlük çıkış fiyatı, testin başlangıcından önce oluşmuş olmak zorunda. Son %20 kronolojik iç doğrulama ve öncesinde 21 günlük hedef embargo. Özellik ölçekleme sadece erken eğitim örneklerinde yapılıyor; dış test yılına uydurulmuyor.
- **Aylık öğrenme:** Yeni ayın başlangıcında yalnız o ana kadar kapanmış 14 günlük etiketi olan örneklerle modelin yeniden eğitilmesi (2026 üzerinde ayrı deney).
- **Karar katmanı:** Tahmin edilen komisyon-sonrası 14g getiri pozitifse ve 4g kötü değilse AL; beklenen düşüşte veya doğrulanmış XAU/NQ stresinde SAT. Bu kararlar ANN'den ayrı, şimdilik araştırma politikasıdır.
- **Belirsizlik katmanı:** İç kronolojik doğrulamanın 14g MAE hata miktarı, beklenen net getiriden büyükse işlem açma. Bu eşik sabit 2026 fiyatından alınmadı ama varyant 2026 sonuçları görüldükten sonra geliştirildi: OOS başarı gibi sunulamaz.

## İşlem sonuçları: %0,8 alış + %0,8 satış maliyeti

2024/2025 başlangıç 100 USD; Şubat–Eylül 2026 başlangıç 119,753917 USD:

| ANN işlem politikası | 2024 net USD | 2025 net USD | 2026 Şub–Eyl net USD |
|---|---:|---:|---:|
| ANN temel maliyetli beklenen getiri (`netPositive`) | 92,5767 | 98,3048 | 105,3787 |
| ANN temkinli giriş (`cautious`) | 98,4071 | 103,3457 | 100,4044 |
| ANN + şok freni (`shockGuard`) | 98,4071 | 103,3457 | 93,9415 |
| ANN geçmiş hata kalibrasyonu (`calibratedAbstain`) | **100,0000** | **100,0000** | **123,5710** |
| ANN her ay geçmiş etiketlerle yeniden öğrenme (`adaptiveMonthly`) | ayrıca 101,1652 test edildi | ayrıca 103,1390 test edildi | **93,9415** |

Karşı kontrol: 2024 pasif altın 123,8497 USD, 2025 pasif altın 160,4153 USD, 2026 Şubat–Eylül nakit 119,753917 USD. Eski V10 2026 130,6663 USD ama 2026 görülerek tasarlanan koruma. V7 2026 aynı-bar 123,5295, işlemi sonraki banka noktasına geciktirilince 116,5000 USD; ANN deneyleri de gecikmeli icra kullanır.

**Model kârlı bulundu demiyoruz.** 2026 kalibrasyonlu 123,5710 USD, önceden görülmüş sonuçlar arasında yapılan araştırma varyantıdır. 2025'te bu kural hiç altın almayarak yaklaşık %60,42 pasif altın yükselişini kaçırmıştır. 2026'nın aynı deneylerde tekrar kullanılması strateji seçimi sızıntısı oluşturur.

## Tahmin başarısı ve bilimsel kısıtlar

| Dönem | Başlangıçta geçmiş kronolojik iç doğrulama 14g MAE | O dönemin sonradan gözlenen 14g MAE | O dönemde 14g maliyetli net getirinin işareti doğru |
|---|---:|---:|---:|
| 2024 | %2,396 | %2,420 | 149 / 249 (%59,84) |
| 2025 | %2,250 | %2,879 | 117 / 246 (%47,56) |
| 2026 Şub–Eyl | %3,299 | %4,311 | 91 / 162 (%56,17) |

MAE ve işaret doğruluğu 14 gün boyunca örtüşen günlük tahminlerden geldiği için bu sayılar bağımsız 249/246/162 vaka anlamına gelmez. Ayrıca 2026 değerlendirmesi yeni kör test değildir. 2026'daki belirsizlik artışı, basit yön doğruluğunun otomatik olarak komisyonlu işlem avantajına dönüşmediğini gösterir.

## Hatalardan öğrenmenin gerçekten öğrettiği şey

1. **Sinir ağı eğitimi artık var.** Ağ geçmişten ağırlık öğreniyor ve yeni ay başında eski olgunlaşmış etiketlerden yeniden öğrenebiliyor. Sırf teknik öğrenme, AL/SAT başarısı değil.
2. **Yanlış etiket, iyi modelin dahi hedefini bozabilir.** 14g net getiri pozitif olsa bile ara süreçte %6 düşüşte satmak gereksiz olabilir; 4g tahmininin riskle birlikte optimizasyonu gerekiyor.
3. **Girdi dağılımı değişiyor.** 2026 çıkış tahmin hatası 2025'ten daha büyük, dolayısıyla girdi/olay rejim değişimini algılayan ayrı kalibrasyon gerekir.
4. **Maliyet ve belirsizlik fiyat yönünden ayrı hedefler.** Salt direction accuracy değil, maliyet-sonrası kâr, maksimum geri çekilme, riskli şoklarda sermaye korunması ve pasif altın/nakit ile karşılaştırma gerekir.
5. **Önceki OLAY-02/ÖĞREN-03 olay ailesi henüz gerçek haber firstprint ve ekonomik sürprizlerle ANN girdisi haline gelmedi.** Bu kanıt olmadan haber temelli ANN başarısından söz edilemez.
6. **2024/2025 iç doğrulama ve 2026 araştırmaları tamam. Gerçek ileri kör doğrulama için yeni, henüz incelenmemiş dönem gerekiyor.**

## Kod ve korunma

`v11_ann_mlp.js`: ANN matematiği, backpropagation ve Adam.
`v11_ann_research.js`: gerçek zaman sıralı ileri getiri etiketleri, geçmiş eğitim, zaman purging, 5 farklı işlem politikası, ay başı yeniden eğitim.
`v11_ann_research.test.js`: sonlu fark türev testi, zaman sızıntısı, kaynak etiketi, komisyon, farklı yıl net sonuçları ve otomatik işlem/terfi engeli.
Salt okunur API: `GET /api/algorithm/v11/ann`. Uygulama menüsü: **V11 gerçek ANN ve hata öğrenmesi**.

Bu deney V1–V10 kodunu ve kullanıcının üretim/imalat konulu dosyalarını değiştirmez. Gerçek banka hesabına bağlanmaz; otomatik al/sat içermez.
