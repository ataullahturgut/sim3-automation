# GOLD BİRLEŞİK EKONOMİK ETKİ MEKANİZMASI V1

**18 Ekim 2026 — Araştırma katmanı çalıştırıldı. S1/S2/S3 karar algoritması değiştirilmedi.**

## 1. Ne oluşturuldu?

**Tek birleşik haber–ekonomik mekanizma araştırma motoru:**

```
HABER (OLAY-02; kaynak ve ilk bilgi saati)
  ↓
ETKİ-05 K01–K48 (tekli ekonomik koşullar)
  ↓
CR01–CR14 (eşzamanlı ekonomik koşul birleşimleri)
+ CTX01–CTX06 (önceden açıklanmış, zaman-doğru ekonomik bağlam)
  ↓
ÖĞREN-03 ORG01–ORG12 (rakip ekonomik mekanizma adayları)
  ↓
BAĞIMSIZ ARACI KANAL GÖSTERGELERİ (USD, reel getiri, fonlama, risk, fizikî talep, OI)
+ KANIT EKSİĞİ / RAKİP AÇIKLAMA
  ↓
G = GENEL piyasadaki 17 adet M15 trend referansı
E = olaydan itibaren yeni, ayrı fiyat referansı
  ↓
S1/S2/S3 İÇİN TARİHLİ GÖLGE ÖZELLİK ÇERÇEVESİ
  ↓
YALNIZ bilim kapısı geçildikten sonra ileri-yön/büyüklük tahmini ve S3 maliyet testi
```

**Gerçek modül:** [economic_mechanism_integrator_v1.js](adaptive_trading_core/economic_mechanism_integrator_v1.js). Dışarıdan `news,registry,mechanismLibrary,asof,completedBars,marketEvidence` alır. `event_news_condition_router_v1.js` ile OLAY-02 kaynak, ETKİ-05 K/CR/CTX ve ÖĞREN-03 ORG adaylarını birleştirir. Mevcut [12 ekonomik örgü matrisi](ETKI_05_GENEL_BUYUK_HAREKET_MEKANIZMA_KURAL_MATRISI_20261018.json) her mekanizmanın şarta bağlı UP/DOWN adayını, karşıt şartlarını ve kanıt eksiklerini taşır. `globalMarket`, `events[].mechanisms`, `events[].market`, `overlappingEpisodes`, `eventFeatureFrames`, `S1Shadow`, `S2Shadow`, `S3Shadow` üretir.

**Kodun şu anda yaptığı ve yapmadığı:**

| Kabiliyet | Sonuç |
|---|---|
| Farklı ülke ve kurumdan haber sınıflandırması | **Çalışıyor:** kaynak listesi 32, K koşulları 48 |
| Aynı zamanlı ve önceki haberdeki ekonomik madde kombinasyonları | **Çalışıyor:** 14 CR ve 6 CTX araştırma kalıbı |
| Mevcut ÖĞREN-03 ekonomik DNA örgülerinin bağlanması | **Çalışıyor:** 12/12 ORG aday mekanizma |
| Birden çok zıt makro sinyalin korunması | **Çalışıyor:** ORG01+ORG02 aynı anda mümkündür |
| P0 ilk piyasa bağlamı + P1 tetik + P2 olası ekonomik aktarım | **Araştırma**: P2 ancak birbirinden bağımsız ve ilk erişimi doğru iki aracı kanalla desteklenebilir; `H2_MEDIATOR_EVIDENCE_PRESENT_NOT_CAUSAL` |
| Olay saati E ve global saat G | **Çalışıyor (ölçüm)**: ekonomik haber ilk algılandığında ayrı fiyat referansı ve tamamlanmış bar |
| P3 hızlanma, P4 yorulma, P5 bitiş/sürme olasılığı | **Henüz öğrenilmiş gerçek olay-dinamiği değil**; tarihli fiyat ve olay olgunlaşma kuralı ileri araştırma gerektirir |
| H3 bağımsız sessiz dönem ve karşıt olay kıyası | **Yok** |
| H4 geçmişten geleceğe kalibreli fiyat yönü/büyüklüğü/süre | **Yok** |
| S1/S2/S3 CORE'a canlı bağlanıp alış/satış üretme | **Yok.** Gölge özellikler var; portföy ve gerçek CORE değişmedi |

## 2. Asıl ekonomik mekanizma neden tek yönlü değil?

- **Faiz/USD (ORG01 ve ORG02):** Beklenenden güvercin haber + USD ve reel getiri düşüşü `ORG01 UP` adayı; beklentiden şahin haber + USD ve reel getiri artışı `ORG02 DOWN` adayı. Gerçek reel faiz/USD verisi olmadan yalnız haber veya yalnız altın düşüşü yeterli kanıt değildir.
- **Güvenli liman ve bankacılık (ORG03/04/05):** Risk haberinin yönü ile altının talep rolü; nakit/fonlama baskısı yükselişi bastırabilir. Ateşkes sonrası risk priminin çözülmesi ayrı mekanizma.
- **Tarife (ORG06/07/08):** Artan belirsizlik hedge-UP adayı, ticaret rahatlaması hedge-DOWN adayı; fonlama sıkışırsa ilk faz DOWN, daha sonra UP görülebilir.
- **Altın fizikî/merkez bankası/ETF (ORG09/11):** Gerçek talep akımı, orijinal rapor yayım zamanı, USD ve karşıt Fed kanalları birlikte.
- **Kâr alma/marjin (ORG10/12):** Önceden yüksek kaldıraç, OI/hacim, yeni teminat belgesi, satış teyidi gerekir. Sırf düşüş grafiğinden `kâr alma` veya `zorunlu satış` türetme.

Tüm ORG için `initialHypothesis` **adlandırılmış ekonomik şart hipotezidir**, veriyle eğitilmiş yön tahmini değildir. `causalConfirmation=NOT_ESTABLISHED`, `remainingMovePrediction=null`, `largeMoveProb=null`, `tradeAllowed=false`.

## 3. Gerçek tarihli örnek — 2 Şubat 2023

[Gerçek fiyatla çalıştırılmış 5 zamanlı örnek JSON](adaptive_trading_core/ECONOMIC_MECHANISM_2023_FEB01_FEB03_REAL_PRICE_CHECKPOINTS_20261018.json). Neon kaynaklı **3.750 M15 bid/ask bar** okunarak 1–3 Şubat Fed, BoE, ECB kararı, Lagarde basın toplantısı ve sonraki NFP haberleri kronolojik yürütüldü. Bütün sistem aynı zamanda 32 kurum/12 ORG için genel şekilde tasarlandı; bu tarih yalnız çalışan örnektir.

**2 Şubat ECB kararı 13:15 UTC / 16:15 TRT:** `K39` = para politikası kararı var, fakat özgün *önceki piyasa beklentisi* doğrulanmadı. **ORG01 ve ORG02 birlikte rakip hipotez**. Türkiye saati 20:15'e (17:15 UTC) kadar tamamlanan M15 fiyatlarından altın, o haber anındaki önceki fiyat referansına göre yaklaşık **−%1,80**. Ancak aynı saatlerde BoE ve ECB söylem haberleri örtüşür. Bu nedenle düşüşü `K39 = DÜŞÜŞ NEDENİ` diye etiketlemez; `P2 bağımsız kanıt yok` ve `H0` raporlar.

**3 Şubat NFP:** altın fiyatındaki haber-sonrası sert düşüş ölçülebilir; ama 2023 tarihli gerçek CPI/NFP konsensüs ilk-baskısı o an için bağımsız olarak doğrulanmadığından strict motor **K03/K19'u canlı etiket diye atamaz**. Arşivdeki geriye dönük K03/K19 araştırma etiketi başka dosyada tutulabilir. Bu, bir sistem hatası değil **geçmişe bilgi sızmasını önleyen bilimsel kabul engelidir**.

**Saat ayrımı:** `eventTime`, `publishedAt`, `availableAt`, `detectedAt` farklı alanlar. E modülü `priceSinceAnnouncement` gerçekleşmiş fiyat yolunu betimleyebilir; **karar ancak `detectedAt` sonrasında**; `priceSinceDetection` ayrı fiyat oranıdır. İlk M15 ancak 15dk bar kapandıktan sonra görülür. Normal G kısa-dönem 17 fiyat belleği sıfırlanmaz. Ekonomik olay referansı 7 gün geçmişse tek haberden sürekli yüzdelik “etki” üretmeyi durdurur; **7 gün mekanizmanın süresi olarak ileri sürülmez**.

## 4. Bütün büyük hareketler için bilim kapısı

[96 fiyat hareketinin tamamı](ETKI_05_96_HAREKET_TUM_ARŞIV_GENEL_NEDEN_DENETIMI_20261018.csv), [38 derin olayın 12 ORG altında genel şartları](ETKI_05_GENEL_BUYUK_HAREKET_MEKANIZMA_KURAL_MATRISI_20261018.json) önceki arşivlerden devralındı. 42 uzun swing'in 25'i en az %5 mutlak hareket içerir. **0/96** orijinal ilk haberin fiyat başlangıcına nedensel katkısı ispatlanmış değildir. Bu yüzden ticari kanıt seviyesi `H4` oluşmuş gibi yeni alım/satım kuralı yazılmadı.

İspat için her mekanizmanın hem **haber→fiyat** hem **büyük fiyat→haber** kontrollü taraması gerekir: açıklandı ama büyük hareket olmadı, büyük hareket oldu ama doğrulanmış haber bulunamadı, faiz/USD haberinin tersi oldu, beraber yayımlanan haberler fiyatı böldü. Tamamlama ölçütü t0-ilk erişim, aracı piyasa değişkenleri, olaysız matched placebo, out-of-time yön/ölçek kalibrasyonu ve gidiş-dönüş yaklaşık %1,6 işlem maliyetini aşan **kalan** hareket doğrulamasıdır. `K/ORG` input; gerçekleşmiş toplam büyük swing yüzdesi asla aynı andaki tahmin input'u değildir.

## 5. Yürütülen kontroller ve güncel sonuç

- [Haber yönlendirici testi](adaptive_trading_core/test_event_news_condition_router_v1.js) **44/44 PASS**.
- [Birleşik ekonomik mekanizma testi](adaptive_trading_core/test_economic_mechanism_integrator_v1.js) **21/21 PASS**.
- Toplam **65/65**, özelliksel ve zaman-bağlı testler; **piyasa/strateji başarı testi sayılmaz**.
- [Çalışan kod](adaptive_trading_core/economic_mechanism_integrator_v1.js) ve [gerçek fiyat yürüyüşü](adaptive_trading_core/ECONOMIC_MECHANISM_2023_FEB01_FEB03_REAL_PRICE_CHECKPOINTS_20261018.json) kalıcı GitHub dalına yazıldı.
- `OLAY_02 → ETKI_05 → OGREN_03 → EVENT_PRICE_SHADOW=WORKING`.
- `EXTERNAL_MEDIATORS_PIT=NOT_CONNECTED`, `FIRSTPRINT_VINTAGE=UNVERIFIED`, `H3_H4_CAUSAL_VALIDATION=NOT_PROVEN`, `REAL_S1_S2_S3_APP_INTEGRATION=NOT_DONE`, `LEARNED_LARGE_MOVE_ALPHA=NO`, `BUY_SELL_ALLOWED=FALSE`.

## 6. Sonraki en anlamlı teknik iş

Mevcut 12 ORG'dan **ORG01/02 (faiz/USD)**, **ORG04/05 (jeopolitik)** ve **ORG08/12 (fonlama/tasfiye)** adaylarının temsil edici büyük UP/DOWN ve küçük/nötr karşı örneklerini, **gerçek olay saatli bağımsız USD/reel faiz/risk/marjin** gözlemleriyle beslemek. H0→H1→H2 geçişlerini canlı haber ingestion değil önce **tarihli doğrulanmış arşiv** üzerinden sağlamak; sonra 2023–25 ileri-zaman testinde H3/H4 kapısından geçeni eski G-only modele karşı sınamak. S1/S2/S3'ü ancak **artan tahmin değeri** görüldüğünde bağlamak.
