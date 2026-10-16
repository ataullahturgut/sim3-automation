# V20 R2 KAVİS–ATLAS: ikinci bağımsız denetim, PREREG ve sonuç

16 Ekim 2026. GitHub araştırma dalı research-gold-v20-r2-shadow-prereg-20261016; taslak PR #138.
Statü: Yalnız araştırma ve bilgisayarda üretilmiş fiyat dünyaları. Gerçek XAU/USD, gerçek banka bid/ask kotasyonu, canlı emir veya onaylanmış yatırım stratejisi DEĞİL.

## Zamansal prosedür
Ön kayıt V20_R2_PREREG_20261016.md ilk commit olarak yeni model kodundan önce açıldı.
Orijinal V18, V20, R1 kodları değişmedi. R2 ana kodu v20_atlas_r2_shadow.js. Ondan sonra korunan 128 bilinen ve 48 farklı kurgusal örnek testi yapıldı.
48 aile ve yeni tohumlar R2 model kodu dondurulduktan sonra üretildi, ama sentetik aile keşfi model geliştirme bağlamında olduğundan gerçek, bağımsız piyasa holdout'u olarak sunulmamalı.

## Düzeltme kabul sonuçları
1. R1 64 dünya eski raporundaki 1 iyi/2 kötü farkları farklı yuvarlama hassasiyetinden kaynaklıydı. Doğru ifade ekonomik olarak 64/64 eşittir.
2. R1 %15 maxDD parametresi önceki hard SELL'i devre dışı bıraktığı için limitsiz R1 sonuçlarından farklı değildi. 238.623 USD ortalama, %15 limit uygulama başarısı değildi.
3. R1 isteğe bağlı ex-ante entry check'i eski peak altında CASH için sürekli BUY yasağına dönüşebiliyordu; R2 bu kuralı hiç kullanmaz. Tamamen risk toleransına bağlı prospektif, BOUNDED soft skor cezası yalnız açık opt-in riskMode=soft_penalty ve maxDrawdownPct verilmişse kullanılır.
4. R1 1/2-step karşı-olgusal danışmana tam tek-bacak ücret yüklenmesi tutma süresini gözetmiyordu. R2 iki bağımsız self-financing sanal portföyü tüm fiyat checkpoint dizisi boyunca yürütür. Her gölge yatırımcının kendi CASH/GOLD pozisyonu, CASH/units envanteri, her gerçekleşmiş geçişinde tek leg banka ücreti, anlık tasfiye NAV ve işlem sayısı vardır.
5. R2 risk uzmanının yetkisi son 32 geçerli banka aralığındaki net log-NAV farkına bağlı. En az 24 gerçekleşmiş fırsat, serisel bağımlılığa kaba bir ceza ve ardışık iki pozitif son skor gerekiyor; bu formal CI/regret bound değildir.
6. Varsayılan mod riskMode=alert, real risk-stop yetkisi YOK, V18 Double Q kararı tek otorite. Açık soft modunda hem danışman güven kapısı hem de olgunlaşmış kuyruk kaybı temelli giriş/çıkış amaç cezası olabilir; %15 maxDD hard cap veya stop-loss garantisi değildir.

## Test sonuçları (GitHub Actions, run 38884171133)
Yeni V20 R2 teknik testleri 12/12 PASS; V15–V20 R1 araştırma testleri 139/139 PASS; 0 hata. Source syntax, no-live-order/historical-import guard PASS.
R2 kontrol testlerinde gerçek danışman karar değiştirebilir (kontrollü kurgusal yükseliş), kötü danışman reddedilir (fiyat düşüşü). Yalnız yüksek Q net avantajı olan CASH, eski peak'in %49 altında bile BUY alabilir; risk cezası matematiksel olarak sonsuz nakit kilidi oluşturmaz.

## 128 eski, daha önce görülmüş sentetik dünya (100 USD başlangıç)
8 aile x 8 seed x [0.8%,2.5%] banka masrafı HER yön. Modelde gelecek fiyat sinyal anında yoktur.
- Alert / V18: ortalama net NAV 173.545164 USD; median maxDD %16.1710; 95-yüzdelik maxDD %26.6871; min final 67.9925 USD.
- R2 soft: ortalama NAV 174.975816 USD; median maxDD %15.9080; 95-yüzdelik maxDD %26.6871; min final 67.9925 USD.
- V18'e göre 25 iyi, 12 kötü, 91 eşit. 60 gerçekten uygulanan adviser override. Shadow rule portföyü 50/128 dünyada shadow V18'den üstün.
- **Soft penalty giriş vetosu bu 128 dünyada 0:** Risk skorunun doğrudan ileriye dönük ceza etkisi gerçek stres kümesinde tetiklenmedi. Kâr farkları danışmanın gölge portföy kanıt kapısından kaynaklanıyor. Bu nedenle %15 risk amacının pratikte yerine getirildiği iddia edilmez.
- 24 alt grup (gap_crash, whipsaw, fat_tails, %0.8/her yön): alert ortalama 238.6235, soft 238.8386 USD; median maxDD alert %14.2971, soft %12.0471; p95 maxDD ikisinde de %26.5919. Maksimum DD bütçesi 15% garanti edilmedi.
- Kayıplar saklanır: false_break seed 9099 fee 2.5% için alert 127.7321, soft 109.6925; bazı regime_flip sonuçlarında da 15-17 USD düşüş var. Sentetik ortalama üstünlük kullanıcı adına garantili üstünlük değildir.

## 48 ayrı kurgusal fiyat dünyası — modelden sonra ilk kez üretilenler
6 aile x 4 seed x [0.8%,2.5%] ücreti. Bunlar gerçek kör finans testi değildir.
- 15 daha iyi, 2 daha kötü, 31 aynı.
- Ortalama NAV alert 246.947483 USD, R2 soft 249.036614 USD.
- Gölge uzman gerçek portföye 19 kez müdahale etti. Opt-in giriş soft veto yine 0.
- 95% maksimum DD 22.0544; en kötü R2 final sermaye 100 USD (bu sentetik generator dağılımına özgü).
- Yeniden yükseliş, çöküş ve uzun trend örüntülerinde bazı olumlu sonuçlar var ama pazarın beklenen dağılımı temsil edilmiyor.

## Kalan önemli riskler / terfi yasağı
1. Yüksek maliyetle sık yön değiştirme durumlarında danışman kötüleşebiliyor. Karar yetkisi tam optimal değil ve global rolling skor farklı rejimlerde taşınabiliyor. Gölge uzman ayrı pozisyondan gelirken bugünkü gerçek CASH/GOLD eylem farkıyla off-policy mismatch kalabilir.
2. Gözlenen drawdown %15 üstüne çıkabilir. Proaktif soft penalty asıl maks. drawdown bütçesini garanti eden matematiksel constrained-MDP değildir. Kullanıcı adına otomatik stop-loss tercih edilmez.
3. 128 eski dünya çok defa kullanıldı. 48 yeni dünyada da pazar fiyat üreticisi tamamen kurgusal. CI başarısı genel kârlılık kanıtı değildir.
4. Ekonomik haber olay kaynaklarının gerçekte ilk erişim zamanı, as-of doğrulanmış bankanın ALIŞ/SATIŞ kotasyonları, 15-dakika fiyatları, likidite/kapanış ve gerçek banka fiyat ayrışması bağlanmadı.
5. Tam portföy risk değeri, maxDD, tail attribution, risk uzmanının alternatif kendi posizyonundan gerçek posizyona aktarımı ve çoklu test yanlılığı gerçek yeni dönemde sınanmalı.

Karar: V20 R2, teknik olarak uygulanan ve 128+48 sentetik stresle değerlendirilen yeni araştırma mimarisidir. V18 temelinin yerini almaz, main dalına terfi etmez ve otomatik banka emri vermez.