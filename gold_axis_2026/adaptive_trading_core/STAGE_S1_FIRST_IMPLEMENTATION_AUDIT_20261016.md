# S1 İlk Uygulama Denetimi — 16 Ekim 2026

**Üst proje manifesti:** [GOLD-ADAPTIVE-MODEL-APP-01](../GOLD_ADAPTIVE_TRADING_MODEL_APPLICATION_PROJECT_MANIFEST.md).  
**Çalışma kolu:** MODEL, yeni GitHub dalı/alternatif algoritma oluşturulmadı.  
**Kod:** [adaptive_rule_discovery_s1.js](adaptive_rule_discovery_s1.js)  
**Test:** [adaptive_rule_discovery_s1.test.js](adaptive_rule_discovery_s1.test.js)  
**İnşa aşamaları:** [BUILD_STAGES_20261016.md](BUILD_STAGES_20261016.md)  
**CI kanıtı:** [GitHub Actions run #38917966345](https://github.com/ataullahturgut/sim3-automation/actions/runs/38917966345), commit `4bd2d3d2bdbf6ddf1dd8e6e755511e4df37f9ca4`. Aynı işte önceki 7 KAVİS V0 sözleşme testi, ayrıca **S1 8/8** test geçti.

## Gerçekte kodlanan matematiksel S1

1. Model yalnız bilimsel olarak anlamlı, `availableAt <= asof` olacak şekilde zaman damgalı ve önceden normalleştirilmiş `feature` girdilerini kabul eder. Model içinde takvim tarihi/vaka ID'si/gelecek hedef özellikleri yasak. Bar kapanışı karar saatinde gerçekten erişilebilir olmalıdır.
2. Her 4 saat içinde en fazla bir gözlemden **yeni bağlamsal kural prototipi** oluşturur; kendiliğinden öğrendiği merkez ve koordinat ağırlıkları zamanla güncellenir. Elle `USD düşerse AL` vb. yön kuralları YOK.
3. Kural yakınlığını çoklu özelliğin sayısal uzaklığıyla ölçer; benzer koşullarda ayrı küme oluşturmayabilir; desteklendiyse merkezleri/yükleri yakın kural prototiplerini birleştirebilir (birleştirme eşiği ve minimum örnek sayısı önceden sabit). **Kural bölme/çoklu rejim içi ayrı dallara ayrıştırma bu sürümde henüz kodlanmadı.**
4. 4 saat, 24 saat, 3 gün, 1 hafta, 2 hafta gecikmeli etiketleri yalnız ufuk dolup sonraki uygun fiyat gelince kuralın `n, up, down, mean log return, variance, downside` istatistiğine ekler. Çok geç gelen fiyatla yanlış 4 saat etiketi yaratmaz.
5. Bütün öğrenilmiş merkezleri, outcome istatistiklerini, pending örnekleri, eksik-veri ve olay delili denetim izlerini `checkpoint` olarak saklayıp devam ettirebilir.
6. `forecastAtDecision` yalnız araştırma tahminidir. **Henüz AL/SAT politikası veya kârlılık yoktur.** `action:null` bunu zorunlu kılar.

## İlk sentetik doğrulama (GERÇEK PİYASA BAŞARISI DEĞİL)

- 100 adet 4 saat aralıklı **tamamen yapay** iki ters ekonomik-feature rejimi (USD-vekil ve gümüş-vekil) üzerinde mekanizma, **2 ayrı prototip** oluşturdu.
- Birinci durumun olgunlaşmış 4s sonuç istatistiği `n=50, mean=+0.60 log-%`; ikinci durum `n=49, mean=-0.70 log-%`. Bu sayılar sentetik veri üretiminde **önceden belirlenen deney kontrol değerlerinden** öğrenildi; gerçek altın piyasa getirisi olarak kullanılamaz.
- İki durum için tahminlerin farklı yönde olması, öğretilmiş manuel fiyat yön kuralından değil, olgunlaşmış etiketli veri ve prototiplerden çıktı.
- 99 olgunlaşan eğitim etiketi; 100 bağımsız zaman ankrajı. Model `tradeActions=0` ve yatırım karar motoru olmadan kaldı.
- Kaynak/kapanış zaman damgası ileri olan feature/price, doğrulanmamış haber, hedef bilgi enjeksiyonu, eksik veriyle sahte nötr özellik, olgunlaşmamış label, checkpoint ve aksi yönde durum öğrenimi testleri **8/8 geçti**.

## Neden Ocak 2023 MODEL_GATE hâlâ FAIL?

- Bu deney yalnız **sentetik**. Gerçek 2023 veri ilk-baskı, USD/faiz/metaller aynı UTC / normalize-origin ve banka fiyat vekili kanıtı birleştirilmedi. Mevcut 2023 Ocak koşusundaki dört makro yayın bütün ekonomik DNA öğrenmesi değildir.
- Üretilen prototipler gerçek **ekonomik neden** göstermez; yalnız çok boyutlu gözlemsel birlikte-oluş örüntüsüdür.
- Kuralların **olay yaşam döngüsü**, kalıcı/tersine dönen uzun hareket, ileri kritik ekonomik karar değeri ve fırsat pişmanlığı henüz öğrenilmiyor.
- Prototipleri veriyle bölme, geçerlilik bölgelerinin bilimsel seçilimi, zamansal rejim kayması ve true effective sample-size güven aralığı eksik; `upFraction` kalibre edilmiş başarılı yatırım olasılığı sayılamaz.
- Bu nedenle model `MODEL_GATE=FAIL`, `TRAINED_2023_2025=false`, `APP_GATE=NOT_APPLICABLE`.

## S1'in sıradaki izinli adımı (diğer aşamalara sapma YOK)

1. S0 as-of kaynak sözleşmesinde XAU tam M15 bar saati, XAG/metaller, USD/2Y-10Y, NQ, varsa resmi makro ilk-yayın ve revision; her özelliğin normalize dönüşümü ve güvenilirlik kaydı.
2. OLAY-02 vaka/ÖĞREN-03 mekanizma sözlüğünü *read-only* inceleyip S1'in gerektirdiği bileşenleri **yalnız as-of doğrulanabilir sayısal features** olarak çıkarmak. Kaynağı yetersiz olayların rolü `UNVERIFIED / UNKNOWN` kalır.
3. Önce **Ocak 2023** as-of örüntülerinde gerçek kural oluşumu, destekleyen/ters/olaysız durum ve sonraki olgunlaşmış sonuçları kaydetmek; ekonomik kuralın karşıt örneklerde doğru genelleşip genelleşmediğini denetlemek.
4. S1 gerçek ekonomik kural kanıtı ve checkpoint oluşmadan S2'ye veya Şubat 2023'e geçmek yok. Uygulama arayüzü bu aşamada geliştirilmez.

**Sonuç:** S1 kodlandı ve teknik-sentetik testleri geçti; ekonomik model öğreniminin gerçek veri ve nedensellik/karar başarısı **henüz gösterilmedi**. Eski sonuçları bu yeni çekirdeğe aktarmak başarı iddiası yaratmaz.
