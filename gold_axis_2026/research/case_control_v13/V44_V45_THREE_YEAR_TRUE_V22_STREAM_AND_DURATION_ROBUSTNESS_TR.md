# V44–V45 | ERKEN V22 UYARISINDAN DOĞRU ÇIKIŞA: 2024–2026 GERÇEK TARİHSEL KARARLAR, 15 DAKİKALIK AKIŞ, DUYARLILIK

**31 Ekim 2026 — araştırma raporu; canlı alım/satım veya üretim sinyali YOK.**

## Araştırma kapsamı ve asıl hedef

**V22 risk = risk izlemeyi başlatır, SAT değildir.** Yükseliş sürerken erken ve maliyetli SAT sinyali üretmemek; yükselişin gerçekten çözüldüğü yerde değişime dayalı bir ÇIK/SAT sinyali üretmek. **Alım, yeniden giriş, nakit dönemi ve portföy getirisini bu çalışmaya katmıyoruz.**

2024 ve 2025'teki V22 araştırma kararları `outputs/v22_daily_decisions.csv` dosyasında yer almaktadır. Bunlar **V41/V42'nin sentetik vekil riskleri değil**, özgün 2024–25 V22 `effective_review` kararlarıdır. 2026 tarihsel araştırma uyarıları V33 yeniden oynatma dosyası `outputs/v33_2026_jan_oct27_DAILY_all_models_and_outcomes.csv` ve `model_v22_review` sütunundan alınmıştır. **2026 V33 sürümü ile 2024/25 ilk V22 sürümü birebir eş değildir.** Hiçbiri kaynak ilk yayım saati doğrulanmış canlı sinyal değildir.

Neon `public.gold_research_histdata_xau15m_candidate`: 2024 **23.713 bar**, 2025 **23.606 bar**, 2026 1 Ocak–1 Ekim erken saat **17.616 bar**, toplam **64.935** tarihsel altın 15m barı. Serinin piyasa/ilk yayım ve bankanın BID/ASK işlem yapılabilir fiyatı sertifikalı değildir. StakTrakr 2026 dört metal 15m kayıtları ayrı kaynaktır; tarihsel HistData'ya körce aynı seri kabul edilmemiştir.

**Streaming makine:** risk D günü kayıtlı ise ancak bir sonraki UTC fiyat gününden itibaren `WATCH` olabilir; algoritma geçmişten ileriye bir bar işler. 15m sinyali barına emir verildiği varsayılmaz; bir sonraki tam 15m kaydı gecikme veya piyasa boşluğu göstermiyorsa fiyat referansı olarak alınır. `EXIT_RECORDED` durumu WATCH içinde tekrar alarm sayısını sınırlıyor. Risk tazelendikten sonra süre aşılırsa yeniden WATCH kurulabilir. İşlem emri YOK.

Kural `V43_STRUCTURAL_1`: V22 WATCH + o ana kadar izlenen zirveden ≥%1 geri çekilme + kesintisiz son 4 saatte ≤−%1 fiyat değişimi + önceki 96 adet 15m bar kapanışlarının en düşüğünü aşağı kırma. Dört metal **bu kuralın içinde yok**. Etiket: çıkış sinyalinden **sonraki beş ayrı NY 17:00 piyasa seansı** boyunca XAU 15m en düşük kaydının sinyal sonrası referans fiyatından ≥%4 düşük olması. Bu, gerçek olay yakalama oranından ayrı, sinyal koşullu bir ölçüttür.

## V44 — 12 takvim günü risk-izleme süresi; 3 yıl aynı stream mantığı

| Yıl | V22 risk dönemi | Yapısal V43 çıkış | 5 seans olgunlaşmış | ≥%4 eşleşen | Sonuçsuz |
|---|---:|---:|---:|---:|---:|
| 2024 | 6 | 6 | 6 | **0** | **6** |
| 2025 | 2 | 2 | 2 | **1** | **1** |
| 2026 Eylül sonu | 5 | 4 | 4 | **4** | **0** |
| Toplam (farklı V22 kaynak sürümleri) | 13 | 12 | 12 | **5** | **7** |

V22 anında SAT karşılaştırması: 2024 **1/6**, 2025 **0/2**, 2026 olgunlaşmış **3/4** (ek 1 geleceği yetersiz). Aynı sayı kaynakta 2024–25 ve 2026 V22 sürümleri farklı olduğundan yıllar arasında homojen kör performans iddiası değildir.

**Olumsuz bilimsel bulgu:** V43 2026'da ümit verici ama 2024'te **6/6 sonuçsuz**, 2025'te **1/2 sonuçsuz** sinyal üretmiştir. 2026'daki 4/4'e bakıp model başarılı veya canlı ilan edilemez.

## V45 — risk süresi 4, 6, 8, 10, 12, 16 gün; eşikleri değiştirmeden tekrar

**2026, V43 yapısal çıkış**:

| Risk izlemesi (takvim günü) | Risk kümeleri | Çıkış | Olgun 5 seans ≥%4 eşleşen | Sonuçsuz |
|---|---:|---:|---:|---:|
| 4 | 11 | 8 | 4 | 4 |
| 6 | 9 | 7 | 4 | 3 |
| 8 | 7 | 5 | 4 | 1 |
| 10 | 6 | 5 | 4 | 1 |
| 12 | 5 | 4 | 4 | 0 |
| 16 | 4 | 3 | 3 | 0 |

**2024 V43** her süre için 0 eşleşen; sonuçsuz sayısı 4 günlük 2, 6 günlük 4, 8 günlük 6, 10 günlük 6, 12 günlük 6, 16 günlük 5. **2025 V43** 4 günde 2/5 eşleşen/uyarı, 6 günde 2/3, 8–16 günde 1/2. Bu duyarlılık, uyarıların birleştirilmesine göre "en iyi" sonucun seçilemeyeceğini gösterir.

**2026'da 12 gün 4/4, 8 gün 4/5.** 12 günlük gözlemde Mart ve Nisan olaylarının tek dönemde birleşmesi gibi kurallar, yanlış sinyalleri ayrı alarm saymama riski yaratır. 4 günlük pencerede sonuca bakıldığında dört eşleşmenin yanında dört sonuçsuz sinyal bulunur. 16 günde ise çok uzun izleme üç eşleşen sinyale düşürmüştür. **Süreyi 2026 sonucu için optimize edip başarı ilan etmek bilimsel hata.**

## Düzeltmeler ve kanıt

- V44 streaming ve NY17 piyasa seansı ufku için **15/15 test PASS**, tam Neon okuması success: <https://github.com/ataullahturgut/sim3-automation/actions/runs/41182369173>.
- V45 altı süre boyunca aynı sabit koşul, 2024–26 Neon tam test **18/18 PASS**: <https://github.com/ataullahturgut/sim3-automation/actions/runs/41182425857>.
- V44 gerçek orijinal V22 girdisi 2024–25 (ek kaynak `outputs/v22_daily_decisions.csv`), 2026 farklı V33 model günlüğü. Tam olay geçişleri/hesaplanabilir SHA256 her risk->exit işaretinin `signal` kaydında.
- GitHub Actions artifact: V44 `gold-v44-2024-2026-real-V22-stream-research`; V45 `gold-v45-three-year-six-expiry-research`.
- Neon read-only, gerçek emir gönderimi yok; çalışan üretim V22, ANN, GVZ, CFTC risk ve parça sistemleri değiştirilmedi.

## Sonraki bilimsellik şartları / sınır

1. **Sinyal bazında 5 seanslık ileri sonuçla eşleşme**, bağımsız tüm altın büyük düşüş olaylarının `recall` oranı değildir. V22'nin uyarı vermediği Mayıs gibi dönemleri kaybedebilir.
2. Risk kümelerini retrospektif 8 seans veya 12 gün birleştirmek yanlış alarm sayısını doğrudan etkileyebilir. Sabit saatli çevrimiçi durumda bunu önceden dondurmak ve bağımsız `physical-event` tabanlı skorlamaya geçmek gerekir.
3. V22 asof/firstprint ve yüksek frekanslı spot ilk gözlenebilir zamanlar kanıtlanmadı; **2026 olayları çoktan incelendi**. Bağımsız holdout başarısı değildir.
4. 2024–25 v22 `effective_review` orijinal araştırma kararları olmasına rağmen **2026 V33 sürümüyle birebir aynılık yok**. Birebir karşılaştırma için aynı sürüm modelin 2024–26 sonradan tek seferde yeniden oluşturulması, daha sonra ileri günlük kayıt gereklidir.
5. Aynı kaynaktan alış–satışta %0,8 ve %0,8 maliyetli davranış kararının ekonomik anlamı, spread, kayma ve banka fiyatı ayrı değerlendirmeye ihtiyaç duyar. Bu çalışma **trade/PnL analizi değildir**.
6. Bilimsel karar: **V43/V44/V45 canlı ÇIK sinyaline terfi etmez**. Asıl çözüm olay (gerçek fiziksel %4 düşüş) bazında tam hatasız/sansürlü ground-truth ve ileri prospektif model gölge izleme ile sağlanır.

**Doküman yeni deneyin güvenilmez iyi görünen sonuçları saklamadan bütünlüğünü korumak içindir.**
