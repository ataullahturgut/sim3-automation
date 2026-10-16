# Matematiksel CORE — İnşa ve Bilimsel Kabul Planı | 16 Ekim 2026

**Üst proje sözleşmesi:** [GOLD-ADAPTIVE-MODEL-APP-01](../GOLD_ADAPTIVE_TRADING_MODEL_APPLICATION_PROJECT_MANIFEST.md).  
**Çalışma alanı:** MODEL; UYGULAMA geliştirmesi ayrıdır.  
**Kullanıcı hedefi:** 2023–2025 deneyimlerinden tarihi ezberlemeden kural keşfi, olay başlangıç/devam/bitim öğrenimi, net ücretli GOLD↔CASH politikası.  
**Kısıt:** Aynı GitHub araştırma dalında ilerle, yeni sürüm/branch/keyfî strateji açma, Ocak 2023 kapısını geçmeden Şubat'a ilerleme. OLAY-02/ÖĞREN-03 salt-okunur bilgi kaynaklarıdır.

## Bilimsel çalışma kipleri (karıştırmak yasaktır)

- `DISCOVERY_FULL_ARCHIVE`: tüm 2023–2025 vakaları ve retrospektif sonuçlarla ekonomik örüntü keşfi; aynı yıllara geri dönük simülasyon **in-sample**; performans yalnız açıklayıcı, OOS değildir.
- `STRICT_WALK_FORWARD`: 2023 Ocak başlangıçlı, sadece olgunlaşmış sonuçlarla as-of parametre ilerlemesi; geleceğin fiyat sonucu, ödülü, rejim sonu geçmiş giriş noktasına taşınamaz. Eski araştırmalarda 2026 görüldüğü için 2026 testi tam kör OOS değildir.
- İki kipin kuralları, ölçümleri, öğrenilmiş modelleri ve sermaye sonuçları farklı `run_id`/hash ile tutulur.

## Aşama geçişleri (geliştirme ile bilimsel kabul AYRI; 16 Ekim 2026 kullanıcı onayı)
**Onaylı istisna — S2 geliştirmesi serbest:** Kullanıcı, S1 ekonomik genelleme başarısını beklemeden S2 yaşam-döngüsü mühendisliğine geçilmesine açıkça izin verdi. **S1_GATE=FAIL** değişmez. S2_DEV yalnız kendi as-of M15 piyasa verisinden olay başlangıç/evre/bitiş tahmini prototipi geliştirir; S1'in araştırma döneminde sonradan görülen makro girdisini ilk aşamada kullanmaz. S2 araştırma sonuçları **ayrıca** bilimsel kabul testinden geçer; geliştirme izni S2_GATE=PASS değildir. Nihai S3 net pozisyon politikasına başarılı S1-ekonomik katkı zorunlu olarak *enjekte edilmeyecek*; girişler bağımsız ablation ile seçilecek. S3 bilimsel kabul, Ocak 2023 tam strict zaman yürüyüşü, S5 ay-ay tarih ilerlemesi ve U1 canlı kullanım izinleri otomatik açılmaz. Aynı repo, aynı branch, aynı matematiksel CORE projesi; yeni kopuk algoritma yok. 


| Aşama | Geliştirme çıktısı | Denetim / geçiş şartı | Başlangıç durumu |
|---|---|---|---|
| **S0 — Veri, zaman, tekrar üretilebilirlik** | Kaynak sözleşmesi; first_available_at/vintage; source quality/missing; bar tamamlanma; 0.8%/leg ve portföy birimleri; immutable deney kimliği | Future feature/label/news reddi; eksik veri uydurmama; kronolojik tekrar üretim; banka MID vekili açık | Başladı, eski korumalar mevcut; CORE şeması netleştirilecek |
| **S1 — Tarihsiz adaptif kural keşfi** | Sayısal özellik uzayından artan/birleşebilen koşullu kural prototipleri, olgunlaşmış sonuç istatistiği; her kural `support/opposition/coverage/uncertainty` | Model elle yön-kuralı alamaz; future leakage/negatif kontrol/synthetic regime ve checkpoint testleri; OLAY-02/ÖĞREN-03'ten desteklenmeyen nedensellik iddiası yok | **İlk kodlama işi** |
| **S2 — Hareketin yaşam döngüsü** | Başlangıç, devam, düzeltme, bitiş ve yeniden giriş durumu; ekonomik olay + çapraz varlık teyidi; süre/hazard ve kuyruk dağılımı | Uzun hareketler bağımsız epizot; overlap kontrolü; duration/tail kalibrasyonu; 4s-2hafta çapraz ufuklarda olgun sonuç | **Mikro + günlük/haftalık S2 birlikte çalışıyor; ayrı 2020–25 BID/ASK arşivinde 35 uzun epizot; tüm bootstrap %95 GA sıfırı içeriyor, bilimsel kabul PENDING** |
| **S3 — Net pozisyon-değeri öğrenimi** | `Q(state, CASH/GOLD, KEEP/SWITCH)`, risk ve gecikmeli credit assignment; nakitte beklemenin fırsat maliyeti; 0.8% alış, 0.8% satış | Net wealth, pasif gold/cash karşılaştırması, turnover, büyük fırsat-kaçırma, DD; fiyat eşiği/manuel tarihli stop değil | **Tek CORE içine S3 fee-net araştırma critic'i eklendi; 2023 Ocak ilk gerçek smoke 0 shadow işlem, cash 100$ vs pasif gold 103,8057$; bilimsel kabul YOK** |
| **S4 — Ocak 2023 bütüncül deney** | 15dk kronolojik kaynak denetimi + ekonomik kural vakaları/tersi/olaysız kontrol, tüm karar günlüğü; başlangıç/son CORE checkpoint | Gerçek ekonomik kural türedi/çürütüldü ve kararı etkiledi gösterilmeli; kaynak saati ve eksikler; 100$ net P&L; bağımsız ablation; başarısızsa ay açık | **MODEL_GATE=FAIL**, önceki V0 0 işlem |
| **S5 — Şubat 2023 → Aralık 2025** | Her ay bitiş CORE'u sonraki ay başına taşıyan 36 kronolojik handoff; yıl sonu dondurulmuş state | Her ayın immutable state'i, öğrenilen/yanlışlanan kural ve karar delili; aylar topluca tekrar oynatılıp sonradan başarı seçilemez | **BLOCKED** |
| **S6 — Dondurulmuş/ön kaydı yapılmış sınama** | 2025 sonu CORE ve 2026 retrospektif kontrollü sınama; mümkünse yeni görülmemiş veri | OOS/bilinen-2026 ayrımı; tüm işlem masrafları, risk, opportunity cost, ablation, baseline | **BLOCKED** |
| **U1 — Uygulamaya entegrasyon** | Uygulama model checkpoint/version ve audit raporunu *aynen* gösterir | APP_GATE ayrı; uygulama karar değiştirip öğrenemez | **BLOCKED** |

## S1 için teknik protokol

- Girdi ekonomik alanlar modelin tarih-kimliği değil `features={name:{value,availableAt,...}}` biçiminde **as-of** sayısal kanıttır. NaN, future veya timestamp'siz veri reject; eksik kaynağa uydurma sıfır yazılmaz. Faktörler **önceden tanımlı ve origin-safe normalizasyonla** benzer ölçeğe gelir; özellik isimleri ekonomik ilişkiyi kodlamaz.
- Öğrenme motoru: gözetimsiz adaptif kural prototiplerinin **birlikte gözlenen piyasa özelliklerine göre** oluşturulması, farklılığın ölçülmesi, yeterli kanıtla yakın prototiplerin birleştirilmesi; etiketli ufuk/getiri/risk istatistiği **yalnız gerçek ufuk olgunlaşınca** güncellenir. Kural yönü/önem/güven el ile verilmez. Prototip merkezleri ve ağırlıklar checkpointte saklanır.
- Yapısal eşik ve örnekleme sıklığı kuralın kendisi değildir; test ayının sonucu görülerek optimize edilmesi yasaktır. M15 overlap veri noktaları bağımsız olay sayılmaz; birbiriyle çakışmayan 4 saatlik **ankraj** ile başlangıç testleri yapılır.
- Çıktı `RESEARCH_RULE_ONLY`: kural merkezi, öğrenilmiş eşleşme olasılığı, olgun n, UP/DOWN örnekleri, beklenen log-% getiri, downside ve belirsizlik. **Henüz AL/SAT/YATIRIM önerisi değildir.**
- **Kural keşif başarı kapısı:** aynı as-of gözlem/kayıt üzerinden modelin en az iki farklı durumu ayırdığı, geçmişte olgunlaşmış sonuçlarla istatistiklerinin güncellendiği ve hata/karşı-örnek raporlandığı kod + testle kanıtlanmalıdır. Sentetik başarı gerçek ekonomik kanıt değildir.
- OLAY-02/ÖĞREN-03 metadata'sı G01/ORG vb. olasılıksal başlangıç hipotezi olabilir; `verifiedFirstprint` yoksa o olay anlık girdiye zorla konmaz. Olay tarihleri/model state indeksi alfa özelliği olamaz.

## Çalışma raporu şablonu (her commit)

`WORKSTREAM=MODEL | STAGE=S1 | INPUT=... | WRITTEN=... | TEST=... | LIMIT=... | NEXT=...`

**Ölçülecek ilk deney:** salt yapısal ve gecikmeli öğrenme testleri, sonra **Ocak 2023'te ilk yayın/çapraz piyasa saat-denetimi yapılmış veri** ile ekonomik kural öğrenmesi. Ocak yürüyüşünde fiyat sinyallerini ekonomik nedensellikmiş gibi raporlamak ve bu nedenle aynı ay daha iyi P&L uydurmak yasaktır.

**Değişiklik kontrolü:** Bu aşamalar ve amaç, model ailesi, tarih sınırı, banka masrafı, proje/branch ve MODEL/UYGULAMA ayrımı ancak kullanıcı değişiklik kararıyla değiştirilir. Basit bug fix ayrı kayıt. Başarısız test, ileri aşamaya kısayol değil, aynı aşamanın açık hatasıdır.


## 16 Ekim 2026 — M2–M5 entegrasyon ek denetim, başarı kapısı değişmedi
- S1 event release alanları bilimsel ilk-baskı/vintage/admission ile aynı CORE S3 araştırma context'ine bağlandı; gerçek Jan23 M15 koşusu yalnız MARKET_ONLY, makro PIT olay sinyali=0. S1 karşıt örnek üstünlüğü hâlâ FAIL.
- S2 tamamlanmış yavaş seanslarından yeni S3 kalıcı `sessionMemory` öğreniyor. 2020–2025 quote-only araştırma: 1500 kabul, 35 bitmiş S2 epizot, 4955 ücretli 1/3/5/10-session olgun etiket, 1033 cenzor. 28 cohort, overlap yüksek, kâr kabulu YOK.
- Ocak 2023 gerçek M15 iki S3 ablation: her ikisi de **0 alım/100 USD nakit**; 5 günlük zorunlu satılma getirisi gerçek bütün ay GOLD tutmanın getirisi değildir. Uygulama, model gate ve Şubat ilerleme değişmedi.
- Kaynak, test, sayısal sonuçlar: `M2_M5_INTEGRATION_ARCHIVE_JAN2023_AUDIT_20261016.md`.
