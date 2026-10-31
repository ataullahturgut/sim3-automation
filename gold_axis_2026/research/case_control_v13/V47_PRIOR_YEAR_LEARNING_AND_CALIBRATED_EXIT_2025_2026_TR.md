# V47 — YILLARDAN ÖĞRENEN, OLASILIK KALİBRASYONLU V22 → ÇIKIŞ SİNYALİ: GERÇEK DENEY RAPORU

**31 Ekim 2026 · Gold Control · yalnız araştırma / shadow; üretime, otomatik satışa veya ana V22'ye bağlanmadı.**

## Neden V47 geliştirildi?

V43 sabit eşikler (yükselişteki zirveden %1 geri çekilme, 4 saatte %1 gerileme, eski 96 fiyat barı desteğinin kırılması) 2026'da iyi görünüyordu; ama 2025 Nisan'da neredeyse dipten çıkış sinyali verip sonraki %17,6 yükselişi kaçırıyor. Dolayısıyla **V22 erken risk → izlemeye devam → yükselişten düşüşe geçişi geçmiş piyasa örneklerinden öğrenerek teyit et → yalnız ÇIK**.

## Kullanılan veri ve uygulanan öğrenme

- Neon `public.gold_research_histdata_xau15m_candidate`, 2020–1 Ekim 2026: **156.366 adet 15 dakikalık XAUUSD arşiv fiyatı** (2023 daha düşük kapsam). HistData serisi bankadan işlem yapılabilir fiyata / gerçek zamandaki ilk yayın verisine denk kabul edilmez.
- **17 nedensel özellik**: son 1 saat, 4 saat, 12 saat, 24 saat ve 288 fiyat barı yönü; 24s/480 bar zirve ve dip konumu; kısa-uzun EMA; kısa/uzun dönem oynaklık oranı; aşağı kapanış oranları; fiyat boşluğu göstergesi. Sinyal anında geleceğin fiyatını **girdi olarak kullanmaz**.
- Öğrenme hedefi: 5 sonraki NY17 piyasası seansı ufkunda fiyat **%4 düşüşü, öncesinde %2 yükseliş görmeden yakalar mı?** Bu **ilk gerçekleşen bariyer** etiketi, sadece sonraki %4 dip olup olmadığına bakmaktan daha seçicidir. Model, piyasa üzerindeki binlerce 2 saatlik örnekle öğrenir; yalnız 2024–2026'daki az sayıdaki V22 olayını ezberlemez.
- `HistGradientBoostingClassifier` ile ilk olasılık öğrenimi, ayrı kronolojik kohortta Platt lojistik olasılık kalibrasyonu.
- 2024 piyasasındaki **etiketsiz** öğrenilmiş risk-skoru dağılımından %70, %80, %90, %95 eşik adayları sabitlenir. Bu, 2025/26 sonuçlarına bakarak en iyi eşiği seçmek değildir; ancak 2024 validasyonunda bile V22 olay temelli isabet optimizasyonu yapılmamıştır.
- V22 günlük orijinal 2025 uyarılarını ve sonraki V33 2026 uyarılarını kullanır; iki V22 sürümü aynı değildir. Çıkış sinyali ancak V22 sonraki fiyat gününde, sekiz takvim günü içinde veya sonraki V22 uyarılarıyla uzatılan risk durumunda oluşabilir. Aynı risk dönemine ikinci ÇIK sinyali üretmez.
- Modeller:
  1. **FROZEN** 2020–2022 eğitim: **8.682 örnek**, 2023 olasılık kalibrasyonu: **2.472 örnek**, 2025 ve 2026 aynen uygulanır.
  2. **2025 annual refit**: 2020–2023 eğitimi **11.257 örnek**, 2024 kalibrasyonu **2.862**; yalnız 2025'te kullanılır.
  3. **2026 annual refit**: 2020–2024 eğitimi **14.212 örnek**, 2025 kalibrasyonu **2.849**; yalnız 2026'da kullanılır.
- Son kohort etiketlerinin ileri tarihe taşmaması için önceki eğitim yılının aralık ortasından sonrası atılır; 2025/2026 gerçekleşmelerini o yılın modeline eğitim için ekleme **yok**. Test yılları araştırmacı tarafından önceden incelendiğinden **kör out-of-sample sayılmaz**.
- Her yıl için `STRUCT_ONLY`, `ML_PROB_TREND`, `ML_PLUS_STRUCT` stratejileri karşılaştırıldı. Alış, yeniden alım, pozisyon getirisi YOK. Yalnız V22 WATCH → ÇIK.

## 2025 sonuçları: geçmiş eğitim, Nisan'daki yanılgıyı hâlâ gideremedi

2025 annual refit modeli (2020–23 eğitim, 2024 kalibrasyon), %95 referans risk-skoru eşiğinde, fiyat yapısının kırılmasıyla birlikte:

| İlk V22 | V47 ÇIK sinyali, TSİ | Simülasyonda sonraki 15m fiyatı | Sonraki 5 seansta dip | İLK -%4 bariyer +%2 yükselişten önce mi? | Bulgusu |
|---|---|---:|---:|---|---|
| 4 Nisan | **7 Nisan 20:15** | **2.974,865 $** | −%0,54 | **Hayır** | Çok erken; 22 Nisan zirvesine +%17,56 |
| 10 Ekim | **17 Ekim 18:00** | **4.240,389 $** | −%5,322 | **Hayır** | Önce fiyat +%3,24 daha yükselip sonra düştü |

`ML_PROB_TREND` saf öğrenilmiş puan + hafif momentum kuralı, 2025'te **0/2** olayda sonraki beş seansta bile %4 düşüş yakalayabildi. Yani **öğrenen modelin varlığı tek başına sorunumuzu çözmüyor**.

Tüm geçmiş öğrenme sürümlerinde %95 eşiğinde V47 + yapısal kırılma 2025 için **2 sinyal, 1 sonraki-%4-dip eşleşmesi, 1 sonuçsuz**; daha sıkı "önce %2 yükseliş gelmesin" ölçütünde **0/2**.

## 2026: önceki yılları öğrenip olasılık kalibrasyonunu güncellediğimiz sürüm

2026 annual refit (2020–24 eğitim ve 2025 kalibrasyonu), **2024'te sabitlenmiş %95 skor yüzdelik eşik değeri 0,047254** ve yapı kırılma koşulları:

| V22 risk başlangıcı | V47 ÇIK, TSİ | Sonraki fiyat USD/ons | Sonraki 5 seanstaki dip | Önce -%4, sonra +%2 (istenen) |
|---|---|---:|---:|---|
| 22 Ocak | **29 Ocak 18:15** | **5.120,715** | −%13,069 | **HAYIR:** çıkış sonrası önce +%2 test edildi |
| 19 Mart | **20 Mart 17:15** | **4.575,655** | −%9,748 | EVET |
| 17 Nisan | **23 Nisan 21:30** | **4.709,135** | **−%4,133** | EVET |
| 5 Haziran | **17 Haziran 22:00** | **4.292,435** | −%7,481 | EVET |
| 21 Ağustos (ayrışan yeni epizod) | **25 Ağustos 08:30** | **4.625,665** | −%4,818 | EVET |

Böylece 2026 uyarı kümelerinde **7 WATCH dönemi, 5 ÇIK, sonraki beş seansta 5/5 ≥%4 fiyat dip eşleşmesi; fakat asıl yarışmalı hedef olan -%4'ün +%2 yükselişten önce gelmesi 4/5.** Bunun 2026 **kör holdout olmaması**, %4 bariyerinin yalnız Nisan'da çok az aşılması ve risk kümelemesinin 8 gün sürmesi sonuca güçlü sınır koyar. Ayrıca risk başlatılmayan, hiç V22 uyarısı olmayan fiziksel düşüşler bu metrikte yoktur.

## Olasılık eşiğinin sağlamlığı: 2026 hâlâ hassas

Önceden 2024 skorlarından tanımlanan **0,047254** sabit eşiğin etrafında ±20% değişiklik yaptık. Bu duyarlılık testi, 2025/26 görüldükten sonra yapılan keşifsel rapordur; **geriye dönük en iyi eşik seçimi olarak kullanılmaz**.

| 2026 annual model eşiği (0,047254 × katsayı) | ÇIK | Sonraki ≥%4 dip | Sonuçsuz |
|---|---:|---:|---:|
| ×0,80 | 5 | 3 | 2 |
| ×0,90 | 5 | 4 | 1 |
| ×0,95 | 5 | 4 | 1 |
| ×1,00 | 5 | 5 | 0 |
| ×1,05 | 4 | 4 | 0 |
| ×1,10 | 4 | 4 | 0 |
| ×1,20 | 4 | 4 | 0 |

Temel eşikte 2026 Nisan dönüşünün model skoru **0,04781**, eşik **0,04725**'e yalnız **%1,18** görece yakındır; hesaplanan başarıda küçük kalibrasyon farkı bir eşleşmeyi değiştirebilir. Bu yüzden başarı **istikrarlı 5/5 değildir**, farklı eşiğe göre yanlış sinyal sayısı veya kapsama değişir.

**2025 annual refit** modelinde aynı q95 çevresi ±%20 için genellikle 1 doğru dip / 1 sonuçsuz sinyal; Nisan %17,56 kaçırılan yükseliş sorunu devam eder. Uygulanmış sabit ve öğrenen modellerin hiçbiri 2025'i güvenilir biçimde çözmedi.

## Bilimsel durum ve yapılmayanlar

- Yalnız piyasa fiyatı kullanıldı, **dört metal, GVZ, CFTC verileri öğrenen modelin doğrulanmış PIT girdileri değil**.
- **Yıllık yeniden öğrenme ve olasılık kalibrasyonu eklendi**; günlük veya aylık otomatik uyarlama eklenmedi. Bunu ileriye dönük ilk yayın günlükleri ve olgunlaşmış etiketlerle kurmadan bugün varmış gibi söylemek yanlış.
- **V47 yeni en iyi canlı SAT modeli değildir**; örneklem az, tek bir yılın iyi görülmesi riski yüksek. 2025 Nisan ve Ekim başarısız, 2026 5/5 %4 dip eşleşmesi seçilen eşiğe hassas, yarışmalı -4% önce +2% hedefi **4/5**.
- Risk **ilk V22 alarmındaki günün kapanışından sonra** başlatıldı. V22 gerçek ilk yayın zamanı doğrulanmadı, 15m zaman damgasının ilk ulaşılabilir kapanış/işlem fiyatı ve banka BID/ASK doğrulanmadı.
- V22'nin 2025 özgün sürümü ile 2026 V33 sürümü farklı; tam aynı sürüm as-of tekrar koşulmalı ve tamamlanmış gerçek fiziksel düşüş günleri üzerinden false/recall doğrulanmalı.
- **Üretim koduna/modeline sinyal terfisi yapılmadı, Neon'a veri yazılmadı, gerçek emir gönderilmedi**.

## Tekrar üretim

`gold_axis_2026/research/case_control_v13/risk_v47_yearwise_supervised_exit_adaptation.py`
`gold_axis_2026/research/case_control_v13/test_risk_v47_yearwise_supervised_exit_adaptation.py`
`.github/workflows/gold-v47-supervised-calibrated-exit-2020-26.yml`

GitHub Actions **8/8 test başarı**, `Neon` gerçek 156k fiyat verisi okundu, yıllık model eğitimi ve tüm sonuç JSON kaydedildi: https://github.com/ataullahturgut/sim3-automation/actions/runs/41189586287

**Kısa karar:** Geçmişten öğrenme ve yıllık kalibrasyon artık araştırma kodunda var; Nisan 2025 sorunu hâlâ duruyor. 2026 ümit verici, ama canlıya hazır değil. Bir sonraki araştırma ayrı *false-breakout vs trend reversal* ve bu probleme doğrudan yönelik gecikmiş teyit/hazard loss olarak düzenlenmelidir.
