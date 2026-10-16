# GOLD-ADAPTIVE-MODEL-APP-01 — M2/M3/M4/M5 tek CORE bağlantı ve tam arşiv öğrenimi (16 Ekim 2026)

**WORKSTREAM=MODEL | PROJECT MANIFEST AS-IS | M2-M5 DEV=PARTIAL_WORKING | M2 SCIENCE=FAIL | M3 SCIENCE=PENDING | M4 SCIENCE=NOT_PROVEN | S4 SCIENCE=BLOCKED | APP=UNCHANGED.**

## 1. Manifestteki eksik bağlantıyı nasıl kapattık?
- `adaptive_market_core_s1_s2.js` **aynı mevcut CORE** içerisinde S1 fiyat-kural `forecastAtDecision` kanıtını S3'e `s1Evidence` olarak veriyor. O gün bilinen, olgunlaşmış S1 model çıktısı dışında bir sonraki fiyat S3'e verilmez.
- S1 şemasında `nfp_surprise_z`, `ahe_surprise_z`, `unemployment_surprise_z`, `cpi_surprise_z` olay özellikleri için ayrı **EVENT sourceRegistry** desteği var; ilk-baskı / first-available metadata'sı S1'in mevcut `featureVector()` denetiminden geçmek zorunda. S3 ekonomik kanıtlı durumu **yalnız yeterli destekli, öğrenilmiş S1 tahmini olduğunda** farklı state olarak değerlendirir; ekonomik olay adına göre elle AL/SAT kuralı yazmaz. `STRICT_WALK_FORWARD` arşiv kökenli, sertifikasız makro sürprizleri reddeder.
- **GÜNCEL GERÇEK VERİ SINIRI:** Ocak 2023 gerçek M15 replay'i ekonomik özellik satırları içermiyor: S3'e gelen `1920` S1 tahmininin tamamı `MARKET_ONLY_UNVALIDATED`. Makro kaynağı kabulü sentetik sözleşme testinde PASS olsa da, ekonomik araştırma ledger'ının canlı firstprint kanıtıyla tek CORE 15dk kararlarına aktarıldığı iddia edilmez. Bu nedenle **M2 ekonomik bilimsel başarı HÂLÂ YOK**.
- S2'nin gerçek `observeSlowSession()` çıktıları yeni `adaptive_position_memory_s3.js` S3 alt hafızasında `1/3/5/10` **tamamlanmış işlem seansı** boyunca birikiyor. Hedef tutar: 100×ln[(fiyat_son/fiyat_ilk)×(1−0.008)^2]; iki alış/satış bacağı dahil. Her etiket ancak **tam gelecekteki seans kapandıktan** sonra olgunlaşıyor; kaynak değişimi, eksik hafta içi/bozuk seans **censor**.
- S3 `LEGACY_M15` ve `MULTI_SESSION_RESEARCH` ablation modları aynı statik CORE'da, farklı konfigürasyonla. İkinci mod yalnız geçmişten olgunlaşmış beş seanslık net değeri/muhafazakâr belirsizliği ve **TR 09:00–17:00** araştırma pencere kapısını kullanıyor; `action:null`, `tradeAllowed:false`, `liveTradeAuthorized:false` daima korunuyor. Ufuk seçiminin bilimselliği, optimum öğrenme ve gerçek banka kotasyonları henüz doğrulanmadı. Bu mod gerçek politika üretimini onaylamaz.
- `s3.sessionMemory` ve alınan S1 tahmin kanıtı `core.checkpoint()/restore()` içinde taşınıyor; değişiklikte ayrı yeni model/uygulama veya dal açılmadı. **Özel ham arşivden oluşturulmuş kalıcı dondurulmuş eğitim checkpoint'i GitHub'a veya uygulamaya taşınmış DEĞİL**; yeniden üretim runner'ı ve testleri kaydedildi.

## 2. 2020–2025 salt-okunur fiyat arşivi, M3→M4 gerçek olgun fiyat etiketleri
Kaynak: `gold_research_evduka_xau15m_bidask_candidate`, `S2_SLOW_EV_DUKA_SESSION_AUDIT_2020_2025.sql`, tek rekonstre `EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1`; altı yıl SQL `2020:259; 2021:258; 2022:258; 2023:257; 2024:259; 2025:258` aday. Toplam **1549 aday / 49 reddedilen / 1500 kabul edilen** seans, **35** tamamlanmış uzun S2 epizot.
Aynı S2 slow `observe()` ve S3 `memory.completed()` JavaScript kodu üzerinde özel Neon satırları tarih sırasıyla işlendi:
- **4955 olgunlaşmış çok ufuklu net CASH→GOLD→CASH araştırma etiketi**, **1033 cenzor** (eksik gün, kaynak kalitesi, süreklilik).
- **28 durum×ufuk cohort**. 4 ufuk (1,3,5,10 tamamlanmış seans).
- Örnek karşıt/alternatif gruplar:

| Tamamlanmış rejim × vade | Ücret dahil olgun etiket n | Ortalama net log-getiri % | Net artı | Net sıfır/eksi |
|---|---:|---:|---:|---:|
| NO_SLOW:NONE × 5 | 474 | −1,500 | 94 | 380 |
| TREND:UP × 5 | 177 | −1,172 | 58 | 119 |
| TREND:UP × 10 | 133 | −0,619 | 58 | 75 |
| TREND:DOWN × 10 | 60 | +0,534 | 32 | 28 |
| NEUTRAL:NONE × 10 | 261 | −1,138 | 101 | 160 |

**Yorum sınırı:** n adetleri birbirine örtüşen oturum başlangıçlarıdır; 4955 birbirinden bağımsız işlemin kârı değildir. Bunlar belirli ufuk sonunda **zorunlu satılan** tek al/sat varsayımıdır; manifest M4'ün adaptif bekle/TUT/SAT gelecekteki politika değerine henüz eşit değildir. Özellikle bir ay sürebilen kârlı pozisyonun yalnız 5. günde zorunlu bozulmasının net etiketi, doğru uzun dönem yatırım kararı anlamına gelmez. 2020–25 tüm arşiv göstergelerinin Ocak 2023 as-of işlem başarısı olarak kullanılması yasaktır. Quote-only MID banka fiyatı değildir; 2026'da geri-kurtarıldı, firstprint PIT değildir.

Reprodüksiyon: `node replay_slow_position_memory_s3.js PRIVATE_S2_SESSION_ROWS.json` (ham dosyalar kullanıcı/veri bağlantısında kalır). Otomatik testler sentetik veriyle gecikmeli ödül, sansür, FIRSTPRINT ekonomik firewall, banka masrafı, shadow-only ve kaynak karışmamasını sınar.

## 3. Ocak 2023 aynı fiyat üzerinde iki S3 ablation
Kaynak aynı **1920** M15 fiyat satırı, Jan 2023 **20 kabul edilen / 1 reddedilen** slow seans. Model Ocak başında **yeni S3 ve boş oturum değerleriyle** başlıyor: eğitim geçmişi verildiği varsayılmıyor.
- S1 doğrudan S3'e **1920 market-only araştırma forecast** iletti; ekonomik PIT tahmin **0**.
- M4 memory: **43** olgunlaşmış oturum etiket, **18** sansür, **4** horizon cohort; beş seans `NO_SLOW:NONE` 10 örtüşen örnekte **−0,3854% ortalama net log-getiri**, yalnız 4/10 net pozitif. Tek başına bilimsel support değil.
- Klasik S3 M15 critic: **1384** anlamlı kıyas, hepsi KEEP, gölge portföy 0 işlem / **100$ nakit**. Yalnız Ocak verisiyle model **hangi gün GOLD alınacağını öğrenemedi**.
- Uzun süreli S3 araştırma ablation: önceki 5 seanslık etiketler üzerinden araştırma, Ocak'ta yine **0 BUY / 0 SELL / 100$ nakit**; bu sonuç bilerek gizlenmedi. 5 seans sonundaki -0,385% **bir ay boyunca yükseliş fırsatının ekonomik değerini açıklamıyor**.
- Eski rapordaki benchmark, başlangıç ve bitişte UTC fiyatı üzerinden pasif GOLD **103,8057$**; Türkiye banka-saatli Jan 3→31 kıyası **102,5368$**. Farklı işlem saati/dönem protokolleri aynı tabloymuş gibi birleştirilmez.

## 4. Hala manifest M2–M5'te neler eksik?
1. **M2:** Gerçek tarihli makro veri/vintage/event mekanizması ve OLAY-02/ÖĞREN-03 geçmiş DNA'sının **learned state** olarak S1→S3 geçişi canlı protokolde tamamlanmadı; mevcut ekonomi prototiplerinin ablation Brier üstünlüğü gösterilmedi.
2. **M3:** 35 tamamlanmış trend epizodunun duration/hazard forecast güven aralıkları ve farklı durumları ayırma gücü bilimsel PENDING.
3. **M4:** 1/3/5/10 seans zorunlu tasfiye reward öğrenmek, **alternatif gelecekteki HOLD/AL/SAT politika değerini** optimize eden M4'ün tamamı değildir. Overlap/episode-cluster, portföy risk ve fırsat kaybı için kontrollü policy improvement gerekir. Ocak 2023 sonucuna eşik ayarı yapılmadı.
4. **M5:** Gerçek bankada ücret ve spread teyidi; aylık immutable checkpoint hash ve 36 ay model-devamlılık zinciri henüz yok. Mevcut `checkpoint()/restore()` hafıza durumunun kaybolmasını önleyecek API'dir, gerçek özel eğitim snapshot'ının saklanması başka iştir.
5. **S4:** Ocak 2023 bilimsel gate, gerçek ekonomi katkısı ve kaynak PIT eksikleri nedeniyle **FAIL/BLOCKED**; Şubat 2023'e atlanmadı; **U1 uygulama değişmedi**.

**Final karar:** Bu çalışma manifestte istenen bağlantıları *mühendislik düzeyinde* kurup gerçek arşivde olgun net etiket üretti. **İstenen bilimsel olarak anlamlı ve kârlı adaptif AL–TUT–SAT modeli tamamlanmış DEĞİLDİR**; olmayan model başarısı ilan edilmez.
