# V48–V49 | ADAPTİF ÖĞRENEN ALTIN ÇIKIŞ SİNYALİ — GERÇEK UZUN DÖNEM KARŞILAŞTIRMASI

**31 Ekim 2026 · Gold Control · GitHub Research · CANLI DEĞİL**

## Araştırma sorusu

**V22 düşüş riski oluştuğunda altın henüz yükseliyorsa yanlış zamanlı ÇIK üretmemek; yükselişin sona erdiği ve birden çok seanslık ciddi düşüşün öne geçtiği noktada çıkış sinyali oluşturmak.**

V22 = **EARLY_RISK/WATCH**, asla kendiliğinden SAT. Bu araştırmada alım, yeniden giriş, nakit getiri portföyü veya canlı broker emri **YOK**.

V43 sabit şartlarına (`tepe -1%`, `4s -1%`, `önceki 96 bar dip kapanışının kırılması`) karşı V48 ve V49, koşullara bağlı risk tahminlerini **her ay** yalnız olgunlaşmış geçmiş etiketlerle yeniden öğreniyor.

## Kullanılan kaynak / kalibrasyon

Neon `public.gold_research_histdata_xau15m_candidate`, 2020–2026 Ekim başı, **156.366 adet** 15m XAU/USD arşiv fiyat kaydı. Gerçek firstprint ve banka fiyatı değil. 2025 V22 `v22_daily_decisions.csv` özgün araştırma günlüğünden, 2026 V22 sonradan hazırlanmış V33 `model_v22_review` dosyasından; **aynı V22 sürümü değil, ikisi de ileriye dönük doğrulanmış ilk yayım değil**.

Her iki model:
- Başlangıçta 2020–22 `HistGradientBoostingClassifier` ile fiyat örüntüleri öğrenildi; 2023 Platt kalibrasyonu.
- 2025 Ocak–2026 Eylül **21 ayın her birinde** geriye dönük **540 takvim günü** ve **15 tam günlük etiket-olgunlaşma tamponu** ile ayrı lojistik meta-model eğitildi. Böylece değerlendirme anında sonraki beş piyasa gününün gerçekleşmiş fiyatı girdide yok.
- **Karar eşiği** geçmiş **1.280 adet 15m puan** üzerinden .80 / .90 / .95 yüzdelik sıralamasından alınır, *mevcut bar hariç tutulur*, ay ve piyasa rejimiyle değişir.
- Dört model türevi: yalnız dinamik skor; 4 kesintisiz 15m skor devamlılığı; **skor + geçmiş oynaklığa normalize geçmiş-96-dip kırılması**; kıyas V43 sabit kuralı.
- Tamamlanan her WATCH dönemi içinde yalnız bir ÇIK; son V22 uyarısından sonra 8 takvim gün içinde yeni uyarı yoksa WATCH kapanır. Bu bir **politika parametresidir**, otomatik öğrenilen bir karar değildir; farklı politikaları sonraki testte karşılaştırmak gerekir.

**V48** ikili P(-%4 önce +%2) hedefini kullanır. **V49** aynı zaman aralığında üç ayrı sonucu öğrenir: **-%4 önce**, **+%2 önce**, **ikisi de yok**. V49'da karar puanı P(düşüş önce)/(P(düşüş önce)+P(yükseliş önce)) şeklinde **koşullu** olasılıktır, bağımsız mutlak düşüş olasılığı DEĞİLDİR.

## Gerçek 2025 ve 2026 senaryo sonuçları

Sonuç ölçütü: bir sonraki uygun 15m referans fiyatından sonraki **beş NY17 piyasa seansındaki** herhangi bir fiyatta en az **-%4**. Bu ölçüt, bu beş seans içinde **önce +%2 yükseliş olsaydı bile** eşleşme sayabilir; bu nedenle ayrıca daha katı `-%4 önce +%2` ölçütünü de raporladık. `4/4` sayısı hiçbir zaman gelecekteki gerçek bütün büyük düşüş olaylarının yakalama oranı değildir.

| Model / skor sırası | 2025: ≥%4 düşüşe eşleşen / sinyal | 2026: ≥%4 düşüşe eşleşen / olgun sinyal | 2026: -%4 **önce** +%2 / olgun sinyal | 2026 yanlış |
|---|---:|---:|---:|---:|
| **V43** sabit fiyat kırılması kıyas | **1/2** | **4/5** | **3/5** | **1** |
| V48 adaptif ikili, vol kırılması, q80 | **1/2** | **4/4** | **3/4** | **0** |
| V48 adaptif ikili, vol kırılması, q90 | **1/2** | **1/4** | **0/4** | **3** |
| V48 adaptif ikili, vol kırılması, q95 | **1/2** | **1/4** | **0/4** | **3** |
| V49 adaptif üçlü, vol kırılması, **q80** | **1/2** | **4/4** | **3/4** | **0** |
| V49 adaptif üçlü, vol kırılması, **q90** | **1/2** | **4/4** | **3/4** | **0** |
| V49 adaptif üçlü, vol kırılması, q95 | **1/2** | **2/4** | **1/4** | **2** |

Her hücre **işlem senaryosuna bağlı, uyarı dönemi başına azami tek sinyal** testidir. 2025 iki uzun WATCH (Nisan–Mayıs bir, Ekim bir); 2026 yedi WATCH (Eylül sonu sonrası gelecek beş seans sansürlü).

### 2025 — en kritik açık

**Nisan 2025 — HÂLÂ HATA:** V22 4 Nisan. V49 q80/q90/q95 adaptif + oynaklık kırılması, **7 Nisan 18:15 UTC** sinyal üretti, sonraki 15m proxy fiyatı yaklaşık **2.967,945$/oz**; beş sonraki seansta %4 dip oluşmadı. 22 Nisan'da fiyat **3.497,165$/oz** oldu; bu çıkıştan sonra yaklaşık **%17,83** ilave yükseliş. Üç sınıflı model 7 Nisan çıkışında **P(düşüş önce) ≈%13,91; P(yükseliş önce) ≈%11,94** tahmin etti, fakat gerçek hareket güçlü yükselişti. Model, geçici sert düşüş sonrası dönüşü hâlâ ayırt edemedi.

**Ekim 2025:** V22 10 Ekim; V49 vol kırılması 17 Ekim 15:00 UTC, takip fiyatı **4.240,389$**. Sonraki beş seansta dip −%5,322. Fakat önce 20 Ekim zirvesine **+%3,242** daha yükseldi; ana hedef (>%2 rally olmadan %4 düşüş) **başarısız**. Dolayısıyla 2025'te 2026'ya benzer güçlü performans oluşmadı.

### 2026 — V49 q80/q90 vol normalize yapı kırılması

| V22 başlama | V49 ÇIK (Türkiye saati) | Sonraki proxy fiyatı | Sonraki 5 seansta -%4 dip | Öncesinde +%2 yükseliş? |
|---|---|---:|---|---|
| 22 Ocak | 29 Ocak 18:15 | 5.120,715$ | EVET | **EVET** → zirveye göre hâlâ erken |
| 19 Mart | 20 Mart 17:15 (q80); q90 21:45 | 4.575,655$ (q80) | EVET | HAYIR |
| 5 Haziran | 9 Haziran 18:30 | 4.300,285$ | EVET | HAYIR |
| 21 Ağustos | 28 Ağustos 20:15 | ~4.498$ | EVET | HAYIR |
| 17 Nisan, 10 Ağustos, 28 Eylül | ÇIK teyidi yok | — | — | — |

q80 ile q90 **iki farklı koşullu skor eşiği** olsa da aynı dört olayı yakaladı. Ancak q95'te sadece 2/4 doğruluk kalıyor; risk sıralaması seçimine **duyarlılık önemli**. Ayrıca 2026 etiketi bilinen yıl üzerinde keşifsel model geliştirildi; **başarı istatistiksel olarak bağımsız değil**.

### V48 ve V49 neden beklenen garantiyi sağlamadı?

2025 Nisan'ındaki geçici kırılma, o ana dek görülen **fiyat örüntüleri** açısından tarihteki önemli düşüş öncesi örüntülerle benzer görünmektedir. Öğrenici daha önceki beş seanslık bariyer sonuçlarından öğrense de **V22 uyarısının gerçek nedensel başlangıç bağlamını**, ileri tarihli haberleri, gerçek otorite ilk yayın saatlerini, GVZ ve dört metal senkron rejimi henüz PIT ile öğrenmiyor. Bu nedenle bir fiyat örüntüsünden gelecekte mutlaka toparlanma/düşüş ayrımı güvenilir biçimde çıkmıyor.

**Önerilen bir sonraki deney:** V22'nin aynı kodla geçmiş dönemlere tarihsel giriş as-of günlüğünü üretmek; 2020–26 gerçekten bağımsız *fiziksel büyük düşüş olaylarını* etiketlemek ve **risk olayı üzerinden, yanlış çıkışın kaçırdığı ralliyi ayrı cezalandıran** uzun döneme yayılan çevrimiçi karar öğrenicisi kurmak. 2025 veya 2026 raporuna bakıp q80/q90 gibi iki eşiği seçerek bunları blind başarı diye pazarlamamak. Gerçek canlı ilk yayın gölge kayıtlarının tutulması ve karar değişmezliği kanıtlanmadan canlı SAT yok.

## Tekrar üretilebilirlik ve uygulama sınırı

- `risk_v48_online_adaptive_sell_only.py` / `test_risk_v48_online_adaptive_sell_only.py`
  GitHub Actions: https://github.com/ataullahturgut/sim3-automation/actions/runs/41192396630
  **8/8 test PASS**, gerçek Neon 2020–26 verisi, bütün 21 aylık öğrenme günlüğü/artifact.
- `risk_v49_online_three_class_exit.py` / `test_risk_v49_online_three_class_exit.py`
  GitHub Actions: https://github.com/ataullahturgut/sim3-automation/actions/runs/41192617855
  **15/15 test PASS**, üç sınıfın zaman sırası + V48 neden-sonra testleri; bütün sonuçlar arşiv.
- `V48_V49_ONLINE_ADAPTIVE_LEARNED_EXIT_2025_2026_RESEARCH_TR.md` (bu rapor)

**No BUY, no reentry, no trading/PnL, no production deployment, no Neon database mutation, no external orders.** Yanlış sinyal ve kaçırılan yükseliş halen açık problem.
