# GOLD-ADAPTIVE-MODEL-APP-01 — CANLI VERİ VE KARAR FREKANSI SÖZLEŞMESİ v1.0

**Tarih:** 17 Ekim 2026 · **İş paketi:** MODEL/M1 operasyonel veri sözleşmesi (uygulama/işlem açılmaz).  
**Durum:** `ARCHITECTURE_SPECIFIED`, `LIVE_INGESTION=NOT_IMPLEMENTED`, `AUTOMATED_TRADE=FORBIDDEN`, `MODEL_SCIENCE_GATE=FAIL`.  
**Kullanıcı amacı:** Ekonomik olay DNA'sını + mevcut S1/S2/S3 bileşenlerini tarihsiz öğrenerek, belirgin altın hareketlerinin başlangıç/devam/düzeltme/bitimini doğru değerlendirmek; **işlem saati kısıtı yok**, gereksiz AL/SAT yok, tüm işlem maliyeti hesaba katılır.

## Karar özeti

**HİBRİT MİMARİ:** Olay/quote akışı sürekli → tamamlanmış 15dk altın barında tek CORE değerlendirmesi → olayda hemen kanıt/risk yeniden değerlendirmesi ancak tamamlanmamış fiyattan S1/S2/S3 emir kararı YOK → S1'nin mevcut dört saatlik iç anchor ritmine dokunma → S2 FAST her tam M15 → S2 SLOW tek tamamlanmış kalite geçerli oturumda → S3 araştırma durumunu her tam M15'te güncelle, işlem üretimini yalnız başarısı doğrulanmış model/gerçek banka kotasyonuyla ileride ayrıca aç.

**Mimariyi KAVİS/ÖĞREN-03 ile karıştırma:** Tarihsiz ORG ekonomik öğrenmenin kimliği **4s, M15 veya tarih değildir**. Bunlar gözlem ve tahmin ölçüm aralıklarıdır. İleri sonuç olgunlaşmadan ağırlık güncellenmez; 2023–2026 analizi bağımsız kör test olarak puanlanmaz.

### Tartılan seçenekler

| Mimari | Artıları | Eksileri | Karar |
|---|---|---|---|
| 1 dakikada tüm model + AL/SAT | Hızlı görünen tepki | M1 veri/PIT kapsamı yetersiz, çok korelasyonlu sinyal, maliyet/yanlış alarm, modelin S1 dört saat/S2 M15 sözleşmesini sessiz bozar | **RET** |
| Sabit 4 saatte tam kontrol | Maliyet ve CPU düşük, S1 anchor ile uyumlu | FOMC/NFP/bankacılık şokunun ilk saatlerini atlayabilir | **RET** |
| Sadece haber geldikçe kontrol | Olay-ağırlıklı ve daha ucuz | Haber olmayan piyasa rejimi değişimleri ve haber güvenilirliği eksikleri | **RET** |
| Akış + 15dk ana CORE + olay-gelişi ön-kontrolü + günlük S2 | Veri frekansı ile işlem sıklığını ayırır, mevcut matematikle ve uzun trendle uyumlu, maliyeti denetler | Gecikme/kaliteli kaynak gerektirir; 15dk'dan önce sert sıçramayı garantili önleyemez | **SEÇİLDİ** |

### Veriyi çekme / izleme sözleşmesi

| Girdi | Hedef operasyon | Gerçek kullanma koşulu |
|---|---|---|
| **XAU/USD quote** | Tercihen yetkili sağlayıcı WebSocket/push; 30sn watchdog, açık piyasada 120sn tazelik üst sınırı *ilk test hedefi*. Streaming yoksa izinli REST için 30–60sn polling | `source_id, bid, ask, event_time, first_available_at, received_at`; quote olmadan yeni işlem değerlendirmesi KAPALI. Bid/ask gerçek bankanınkinden ayrılır |
| **XAG / DXY veya USD çiftleri / tahvil/faiz / NQ vb.** | Push varsa akış; yoksa kaynak çözünürlüğüne uyumlu ~1–5dk polling, yüksek etkili açıklama yakınında veri mevcutsa daha sık | Çapraz-asset `event_time, available_at, missing_mask` ile; eski/yanlış saatli kaynak `UNKNOWN`, bir varlığın verisi başkasının saatinden ileri taşınmaz |
| **NFP, CPI, PPI, PCE, FOMC, resmî takvim** | Takvimi her gün ve revizyonda yenile; izinli resmî feed ile önceden planlı duyuruyu takip et, yayın çevresinde sağlayıcının limitine göre 15–60sn denetle | Saat `America/New_York` ve duyuru bazlı; ilk erişim kesin değilse `RESEARCH_UNVERIFIED` ve ekonomik koşullu işlem SİNYALİ kapalı |
| **Beklenmedik banka/jeopolitik haberler** | Lisanslı düşük-gecikmeli haber akışı tercih; yoksa 2–5dk polling (tam kapsam/30sn haber garantisi YOK) | Kaynak, yayın/ilk erişim, deduplikasyon; tek başlık = ekonomik nedeni doğrulayan işlem girdisi değildir |
| **CFTC COT / ETF / diğer periyodik veriler** | Kaynağın gerçek yayınında; COT tipik Cuma 15:30 ET, verisi önceki Salı | **As-of** yayın günü baz alınır, Salı'nın verisini Salı günü biliniyormuş gibi koyma |
| **Haber ve resmî açıklama revizyonu** | Her yeni `source+release_id+revision_id` için tek kayıt, append-only | Revizyon önceki kararın veri tabanını geriye dönük değiştiremez |

**Kaynak doğrulama:** [BLS CPI takvimi](https://www.bls.gov/schedule/news_release/cpi.htm), [BLS istihdam takvimi](https://www.bls.gov/schedule/news_release/empSit.htm), [CFTC COT yayın takvimi](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm). Saatler ABD mevsimsel saatine uyarlanmalı, Türkiye yerel saatine sabit gömülmemeli.

### Bilgi / karar değerlendirmesi ve öğrenme

1. **Her quote geldiğinde:** Kaynak kalitesi, fiyat yaş/dağılım ve son kalite statüsü güncellenir; **her tickte S1 ve AL/SAT çalıştırma YOK**.
2. **Her 15 dakikalık M15 barı tamamlanıp yayımlandığında:** Kalite kapısı ve as-of koşuluyla S1+S2_FAST+S3 aynı CORE'dan **bir kez** çalıştırılır. Eksik bar, gap, kaynak değişimi, kapanıştan önce veri veya çok geç bar `BLOCKED / RESEARCH_ONLY`; geriye dönük emir uydurma yok. Provider kapanış toleransı başlangıç test hedefi **120sn**, sonradan gözlenmiş dağılımla ayarlanabilir; geç geçmiş barı sakla ama canlı karar yapma.
3. **S1 mevcut kod:** `horizonMinutes=240, anchorMinutes=240`. S1'in 4s çıpasına karşı **15dk'da bir bağımsız hazır 4s tahmin çıkmış** gibi davranma. 15dk'da S1 durum güncellenebilir; `ready` ve tahminin son üretim zamanı ayrı gösterilir.
4. **Ekonomik olay geldiğinde:** Duyuru/anomali **hemen** kayıt edilir, kanıt/güvenilirlik ve veri eksiği tekrar kontrol edilir, dashboard'a `RECHECK_PENDING` gösterilir. Tamamlanmamış 15dk fiyatıyla S1/S2/S3 yeniden tahmin **üretme**; bir sonraki kaliteli M15 barı ilk çoklu-piyasa teyidini değerlendirsin. İleride ayrı M1 erken şok modeli istenirse farklı bilimsel kapıdan geçmeden işlem yetkisi verilmez.
5. **S2 yavaş:** Yalnız tamamlanmış, bağımsız kalite geçen **günlük oturum** için **bir kez**; M15 UTC22 araştırma konvansiyonu (resmî kapanış değil). Üretimde yerel NY 17:00 ve DST geçişi **ayrı** kabul testi gerekir; kanıtlanmadan mevcut `UTC22` otomatik canlı settlement ilan edilmez.
6. **S3:** Her tamamlanmış M15 ile net CASH/GOLD avantajı araştırma olarak güncellenebilir; **0.8% alış + 0.8% satış** iki ayak komisyonun başabaş fiyat eşiği **~%1.6194**; mevcut banka ASK/BID, slip ve vergi ek maliyettir. Model net getiri **ufka göre** belirsizliği aşmadıkça sırf her 15dk geçti diye AL/SAT yok. Bu sayı tek başına AL/SAT politikası eşik parametresi değildir.
7. **Gerçek öğrenme:** Modeller ancak kendi ufkundaki sonuç **tamamlanıp olgunlaştığında** ağırlık günceller. 4s etiket 4s sonra; günlük/haftalık ve çok-seans etiket ilgili tamamlanan oturumla; ekonomi vakaları olayın bağımsız destek/karşıt örnekleriyle. Zamanı gelmemiş geleceğin fiyatı yasaktır.
8. **Ekran:** Verinin son alım saati, fiyatın kaynağı/yaşı, son S1 tahmin zamanı/ufuk/ready, S2 fast ve slow, ekonomik kural/kaynak/vintage, S3 `NO_ACTION` nedeni ve gerçek banka fiyatı yoksa araştırma etiketi net görünür. İstatistiksel olasılık dayanağı yoksa `—`, 0% değil.
9. **Kalıcı durum ve kurtarma:** Her bar/olayda append-only gözlem+decision audit; checkpoint önemli değişimde ve en geç 1 saatte bir (hedef), bütün state: S1/S2/S3/M2 ekonomik öğrenme/pending etiketi, kaynak hash, pozisyon, UTC watermark. Kesinti sonrası **eksik bar backfill**, kronolojik replay ve idempotency; eski güncellemeden otomatik sonradan işlem yok. Açık piyasada anomali/veri kopması = `DATA_STALE`, yeni AL/SAT engel.
10. **Piyasa kapalıyken:** Yanlış fiyat üretme, hafta sonu kapalıysa `MARKET_CLOSED`; haber gelirse kaynaklı `PENDING` yaz fakat açılışta ilk geçerli fiyat/likiditeyi bekle. **Banka işlem saati KISITI YOK**, ancak gerçek banka kotasyonu ve icra izni ayrıca gerekir.

### Canlıya geçiş kapıları (zorunlu)

- **M1 FEED VALIDATION**: İlk sağlayıcı, gecikme p50/p95/p99, veri boşluğu, quote-alım saati, spreads, UTC/DST, lisans ve maliyet; backfill/failover kanıtı.
- **M2 PIT ECONOMIC VALIDATION**: En az resmî kritik veri ailelerinde orijinal ilk yayın actual/consensus ve revision, bağımsız alternatif/olaysız vakalar, çapraz-piyasa aktarımın **ekonomik-on/off** faydası.
- **S1/S2 SCIENCE**: Kronolojik geleceği görmeyen çoklu ufuk puanları, S2 bitiş/kalım olasılık kalibrasyonu ve base-rate/ablation üstünlüğü.
- **S3 NET PORTFOLIO**: Banka bid/ask + maliyet + likidite + gerçek yapılabilirlik; nakit, pasif GOLD ve aynı olay/risk karşıtlarıyla maliyet-net portföy; kârlılık eşiği bilimsel doğrulanana kadar `tradeAllowed=false`.
- **OPERATIONS**: En az 30 gün canlı gölge veri toplama, 7/24 sağlık, karar kaydı/ara versiyon hash, kullanıcı uyarı testleri; **bu süre kabul için önerilen asgari operasyon testi, finansal isabetin garantisi değildir**.

**Açık iş:** Onaylı veri/haber provider ve fiyat ile bağlantı henüz YOK; API limitleri nedeniyle 15/30/60sn hedefleri ileride servis sözleşmesine göre revize edilebilir. Bu belge bağlantı, sunucu, scheduler veya canlı ticaretin aktif edildiği iddiası değildir.
