# Ocak 2023 S1: Ekonomik kanıt ve araştırma ablation raporu

**Proje:** GOLD-ADAPTIVE-MODEL-APP-01 | **WORKSTREAM=MODEL** | **STAGE=S1** | 16 Ekim 2026
**Bilim kapısı:** MODEL_GATE=FAIL. S2/S3/AL-SAT/UI bu deneyin kapsamına alınmadı.

## 1. Aynı matematiksel CORE ve iki kanıt düzeyi

- STRICT_WALK_FORWARD: bağımsız ilk erişim ve gerçek tarihsel konsensüs doğrulaması olmadan EVENT girdisi kabul etmez. Ocak 2023 için gerçekten sertifikalı bileşen **0/4**.
- DISCOVERY_FULL_ARCHIVE: resmî BLS **ilk yayımlanan** actual ve yayım öncesinde tarihi belli basın beklentisiyle, embargo sonrasına 60/120/180 dakika varsayımsal erişim gecikmesi koyar. Bu yalnızca retrospektif ekonomik hipotez öğrenimidir. Gerçek first-received timestamp değildir ve ticaret sinyali sayılamaz.
- İki ayrı kipin checkpointleri karıştırılmaz. Yeni model ailesi açılmadı.
- CORE komşuluk ölçüsü düzeltildi: olay sürprizi varken oluşan prototipe, sürpriz **yokken** gelen bar atanmıyor. Böylece olaydan sonraki olaysız fiyat etiketleri haber kuralının destek sayısını sahte şekilde artırmıyor.
- Henüz minReady=8 bağımsız olgun etiket görmeyen ekonomik prototip tahmin vermiyor; karşılaştırmada piyasa-only fallback açıkça sayılıyor.

## 2. Kaynaklar

**6 Ocak 2023, 13:30 UTC — üç bileşen tek BLS yayın dalgasıdır.** NFP initial actual 223 bin, Reuters 6 Ocak **05:00 UTC** ön beklenti 200 bin; aylık ücret artışı %0,3 / %0,4 beklenti; işsizlik %3,5 / %3,7 beklenti.
- BLS ilk sürüm: https://www.bls.gov/news.release/archives/empsit_01062023.htm
- Reuters yayın tarihli beklenti: https://www.reuters.com/markets/us/strong-us-jobs-wages-growth-expected-december-2023-01-06/

**12 Ocak 2023, 13:30 UTC — tek CPI yayın dalgası.** BLS initial actual aylık -%0,1; Reuters 11 Ocak **21:05 UTC** beklenti %0,0.
- BLS: https://www.bls.gov/news.release/archives/cpi_01122023.htm
- Ön beklenti haberinin tarihli yeniden yayını: https://www.lse.co.uk/news/us-investors-bet-on-inflation-data-being-benign-q0acm1dj0xyn8f2.html

**Sınırlama:** Bugün görünen Reuters sayfaları tarihlerinden sonra güncellenmiş olabilir. Tarihli basın haberi doğrulanmış ilk piyasa erişimi değildir. Sayısal normalizasyon ölçekleri araştırma mühendislik varsayımıdır, önceden eğitilmiş kalibrasyon değildir. Bunlar yalnız DISCOVERY_FULL_ARCHIVE kanıtıdır.

## 3. Ocak 2023 gerçek Neon koşusu

Kullanılan önceki salt okunur SQL: JAN2023_RECONSTRUCTED_ASOF_S1_INPUT.sql. **102 gerçek 4 saatlik çıpa**, M15 bitiş fiyatı, XAU + tamamlanan NQ/ZN/CL market feature. İki model için aynı CORE, aynı piyasa fiyatları ve aynı horizon (4s). Lisanslı ham fiyatlar GitHub'a yazılmadı.

| Varsayımsal erişim gecikmesi | Olay yayını / bileşen kabulü | Ekonomik prototip | Hazır ekonomik olay tahmini | Yön: ekonomi açık | Yön: piyasa only | Brier ekonomi açık | Brier piyasa only |
|---|---|---:|---|---:|---:|---:|---:|
| 60 dk | 2 / 4 | 2 | **0/2** | 30/70 | 31/70 | 0,272335 | 0,271422 |
| 120 dk | 2 / 4 | 2 | **0/2** | 30/70 | 31/70 | 0,272335 | 0,271422 |
| 180 dk | 0 / 0 (4 karantina) | 0 | 0 | 31/70 | 31/70 | 0,271422 | 0,271422 |

60/120 dk araştırmada 6 Ocak ve 12 Ocak için birer olay prototipi ayrıştı. **Her birinde yalnız 1 anchor / 1 olgun 4s etiket** var. Hareketler sırasıyla +%0,3486 ve +%0,4711; bunlar gözlenmiş geçmiş sonuç, öngörü başarısı değildir.

Her iki olay tahmini karar anında hazır olmadığından, araştırma karşılaştırmasında piyasa-only tahminine iki kez geri dönüldü. **Olay vakalarındaki Brier iki kolda da 0,347222 ve yön 1/2**. Dolayısıyla olayın ekonomiden geldiği veya prototipin bu hareketi önceden yakaladığı gösterilmedi. Ekonomik-on bütün-ağ puanı 30/70, market-only 31/70: ekonomi kuralına başarı yazılamaz. Bu farkın bir nedeni ekonomik saat çıpasının piyasa-only eğitiminden ayrılmasıyla sonraki market-only kural geçmişinin değişmesidir; event-specific alpha iddiası yapılmaz.

180 dk varsayımında 13:30 UTC yayının 16:00 UTC karar saatinden 150 dakika önce olması nedeniyle ekonomik kanıt hiç yetişmez. Haber erişim gecikmesine duyarlılık ölçüldü; optimizasyon hedefi yapılmadı.

Önceki çıpasal UP-baseline: 35/70 doğru, Brier 0,256330. Mevcut S1 ekonomik-on araştırması **daha kötü**. 70 fiyat kıyaslamasının yalnızca 2'si ayrı makro yayına maruz; aynı olay içindeki bileşenler bağımsız eğitim örneği değildir.

Daha önceki aynı-saat/benzer market-negative controls, olaydan sonra altın yükselişinin yükselen olaysız örneklerde de görülebildiğini gösterdi. Bu iki olay genellenebilir ekonomik nedensellik için yeterli değil.

## 4. Kalıcı kod, deney tekrar üretimi ve kabul

- adaptive_rule_discovery_s1.js: STRICT vs DISCOVERY koruması; EVENT present/missing ayrımı.
- economic_pit_learning_s1.js: BLS tarihli initial actual + dated pre-release consensus kontrolü; 60/120/180m varsayım; aynı CORE üzerinde iki kol; karşıt/olaysız kirlenmeyi engelleme ve minReady fallback.
- JAN2023_RESEARCH_PUBLICATION_ASSUMPTIONS_20261016.json: dört bileşen, tarihli kaynak URL'leri, açık ölçüm/erişim varsayımları.
- replay_jan2023_economic_research_s1.js: salt okunur SQL'den özel elde edilen private JSON girdiyle üretilebilir; yalnız türetilmiş metrikleri stdout'a yazar.
- economic_research_vintage_s1.test.js: research/strict ayırımı, sahte tarih, erken erişim, olay dışı veri kirlenmesi, fallback testleri.
- Eski testler ve yeni testlerle **26/26 izole JavaScript sözleşme testi PASS**; mevcut GitHub Actions dosyasına bu testler eklendi. Son Actions başarısı henüz bağımsız teyit edilmedi.

**Karar: MODEL_GATE=FAIL; S1_ECONOMIC_RULE_GENERALIZATION=NOT_PROVEN; TRADE_POLICY=NOT_IMPLEMENTED; APP=UNCHANGED; NO_FEBRUARY_PASS.**

Sıradaki bilimsel gereksinim, OLAY-02/ÖĞREN-03'ten daha geniş tarihli arşivde *araştırma amaçlı* bağımsız olay sayısı ve karşıt vaka çeşitliliği geliştirmek; Ocak 2023'ün tarihsel strict yürüyüşüne sonraki ekonomik sonuçları gizlice katmadan, aynı S1'in koşullu kuralının başka vakalara taşınıp taşınamadığını göstermek. Daha sık bar, tek bir ekonomik olayı çok bağımsız haber haline getirmez.
