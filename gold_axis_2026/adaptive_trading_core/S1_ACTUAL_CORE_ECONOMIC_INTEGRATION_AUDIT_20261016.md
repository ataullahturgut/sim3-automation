# S1 — Ekonomik öğrenmeyi ASIL adaptif matematiksel CORE'a bağlama ve gerçek retrospektif deney
**Proje:** GOLD-ADAPTIVE-MODEL-APP-01 | **İş akışı:** MODEL | **16 Ekim 2026**
**Aşama:** S1 | **MODEL_GATE=FAIL** | **S2/S3/S4=NOT_STARTED** | **APP=UNCHANGED**

## 1. Önceki temel eksik kapatıldı: ayrı KNN araştırmasında kalmıyor

Önceki S1 arşiv araştırması bağımsız makro yakın-komşu hesaplamasına dayanıyordu. O deneyi, **asıl matematiksel öğrenme CORE'u içindeki kurallar öğrenilmiş gibi göstermemek** gerekir. Yeni [replay_macro_waves_in_existing_core_s1.js](replay_macro_waves_in_existing_core_s1.js), verileri doğrudan zaten var olan [adaptive_rule_discovery_s1.js](adaptive_rule_discovery_s1.js) işlevleriyle — `core.create`, `core.observe`, `core.rules` — eğitir, iki **aynı CORE** kolunu karşılaştırır.

Birinci CORE: haberden 60 dakika sonra elde varsayılan retrospektif makro actual−consensus sürprizleri + haber öncesi/ilk saat altın koşulları. İkinci CORE: aynı gözlem, aynı altın koşulları, **makro sürprizleri hariç**. İki kolda sadece bu girdi seti farklıdır; yön kuralı, manuel USD/FED altın işareti veya optimum gelecek AL/SAT tanımı yok. Karşıt/olaysız kontroller her iki CORE'un gerçek label hafızasına dahil edilir.

Güvenlik:
- `STRICT_WALK_FORWARD` değişmedi ve `RETROSPECTIVE_LEDGER_POST_EVENT_PAIR_UNVERIFIED` kaynaklarını reddeder. Yalnız `DISCOVERY_FULL_ARCHIVE` araştırması bu **sertifikasız** sürprizleri kaynak-lineage metadata'sıyla öğrenebilir.
- Ekonomik özellikli ile ekonomisiz prototipler birleştirilmez; yanlış destek büyütülmez. NFP/AHE/UNEMP eşzamanlı **tek açıklama / tek 4h etiket**, CPI tek açıklamadır. Aynı fiyat saatindeki yinelenen kontroller **tek fiyat etiketi** alır.
- **Gecikmiş etiket mekanizması:** 15dk tamamlanmış piyasa çıpası `t` anında tahmin edilir ve kural için pending etiket açılır. Bağımsız XAU gerçek fiyatı tam **t+4 saat** gözlenmeden CORE öğrenme sonucuna eklenmez. Gelecek bar sadece hedef sonucu olgunlaştırır, tahmin özelliği değildir. Model ham XAU fiyatlarını rapora veya GitHub'a yazmaz.
- Makro sürprizleri gerçekte yayından 60 dakika sonra görüldüğüne dair 2023–2025 first-received kaydı **yok**. 60 dakika yalnız eski arşiv için varsayımsal bilgi gecikmesi. Makro ledger satırları `POST_RELEASE_ONLY`, **VERIFIED_PIT=NO**. Bu nedenle hiçbir sonuç `STRICT_WALK_FORWARD` veya gerçek canlı yatırım başarısı değildir.

## 2. Kaynak ve fazlar

**Makro veri:** GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv; 69 ayrı BLS istihdam/enflasyon yayını. `independent_event_research_query_s1.js` baştan sona 2023–2025 için read-only Neon sorgusu üretir. `pre2h`: olay başlangıcından önceki bir saatlik XAU log fiyat hareketi. `pre1h`: varsayımsal 60dk haber erişimi sonrasına kadar oluşan **ilk saatlik piyasa tepkisi**. Bunlar `gold_prev_1h` ve `gold_1h` olarak, önceden belirlenen 1,5 yüzde puanı mühendislik ölçeğiyle normalize edilir; gerçekleşecek sonraki dört saatin hiçbir parçası bu feature'larda yoktur.

**Gerçek etiket:** veri tabanından alınan ve aynı 15dk serisine ait XAU `anchor_price` ile dört saat sonraki `due_price`; her olaydaki değerlerden hesaplanan getiri, ayrı SQL `next4h` alanıyla birebir tutarlı değilse deney hata verir. Bu iki fiyat, aynı kullanıcı Neon bağlantısında geçici okundu; **GitHub'a ham/lisanslı fiyat satırı, model hafızası veya işlem kaydı yüklenmedi**.

**Kontroller:** başka makro yayına ±24 saat uzak, aynı UTC saat/dakika ve yakın geçmiş altın hareketi açısından benzer, araştırma sırasında sonradan seçilmiş kontroller. 228 eşleşme **178 farklı** kontrol çıpasından oluştu. Bazı çıpalar dört saatlik ankraj yakınlığı yüzünden modelin bağımsız eğitim birimi sayılamaz. Bunlar karşıt hipotez sağlamaktadır ama sayıları 228 bağımsız haber olarak sunulamaz. Ayrıca kontrollerin tüm arşiv kullanılarak geriye dönük seçilmiş olması gerçek kör OOS kontrol tasarımı sayılmaz.

## 3. ASIL S1 matematiksel CORE gerçek koşusu — 2023–2025

| Ölçüm | Gerçek sonuç |
|---|---:|
| Arşivdeki ayrı makro yayın dalgası | 69 |
| Kaynağı tam ve ölçülebilir makro yayın | 57 |
| Kaynak tamlık nedeniyle reddedilen | 12 |
| Negatif kontrol ataması / benzersiz çıpası | 228 / 178 |
| CORE'a giren bağımsız anchor | 221 = 57 olay + 164 olaysız kontrol |
| Tam dört saat sonra olgunlaşan etiket | 221 |
| İki CORE'un birlikte hazır tahmin verdiği anchor | 196 |
| Bunlardan gerçek ekonomik olay | **40** |
| İki CORE'un birlikte hazır tahmin verdiği olaysız kontrol | 156 |
| Ekonomi kullanan modelin hazır olmayan olay tahminleri | 17 |

| Gerçek CORE performansı | Ekonomi dahil | Aynı CORE, yalnız piyasa |
|---|---:|---:|
| 196 eşit değerlendirilebilir durumda doğru yön | **101/196** | **95/196** |
| 196 durumda Brier (küçük daha iyi) | **0,255918** | **0,253149** |
| 40 bağımsız olayda doğru yön | **21/40** | **17/40** |
| 40 olayda Brier | **0,264965** | **0,256879** |

Sıralı olgunlaşan tüm gözlemlerden hesaplanan basit önceki UP oranı referansının 196 olaydaki Brier değeri **0,253028**. Ekonomili CORE hem bu taban orandan hem sadece piyasa kullanan CORE'dan **daha kötü kalibre**. Makro bilgisinin dört ek doğru yönle sonuçlanması, daha yüksek Brier ve sınırlı örnekle **üstün ekonomik öğrenme kanıtı** değildir.

Yalnız makro yayınları için önceki CORE'a göre Brier iyileşmesi ortalaması **−0,008086** (negatif: daha kötü). Makro yayımlarına göre 1.000-bootstrap açıklayıcı %95 fark aralığı **[−0,045366; +0,026942]**; sıfırı kapsıyor. Kâr, banka makası sonrası getiri ve varlık değişimi hesaplanmadı: **AL/SAT modeli hâlâ S3 görevidir.**

### Gerçekte öğrenilen ekonomik prototipler

| Öğrenilmiş ekonomik prototip | Destek: bağımsız 4s etiket | UP | DOWN/diğer | Ortalama sonraki 4s log hareketi |
|---|---:|---:|---:|---:|
| NFP + AHE + UNEMP — ana ekonomik durum kümesi | 28 | 12 | 16 | −%0,0166 |
| CPI — ana ekonomik durum kümesi | 28 | 16 | 12 | +%0,1458 |
| İstihdam — ayrı uç örnek | 1 | 0 | 1 | −%0,9339 |

**Önemli:** Bu prototipler artık gerçekten ASIL S1 CORE'un istatistiklerinde yaratıldı ve dört saat sonrasında olgunlaşmış label ile güncellendi. Ancak bir aileyi ortalama olarak ayırmak, aynı ailenin neden bir gün yükseliş, başka gün düşüş yaptığını çözmek değildir. İlk iki grubun her birinde belirgin **karşıt sonuçlar** var; olay açıklaması ekonomik nedenselliği veya özel koşullu yön mekanizmasını ispatlamıyor. CPI/istihdam için 28'er örnek, mevcut CORE'un bilimsel rule-split eşiğini geriye dönük keyfî düşürerek optimizasyon yapılmasını haklı kılmaz.

## 4. Teknik tamamlık, kalan bilim kapısı

- [replay_macro_waves_in_existing_core_s1.js](replay_macro_waves_in_existing_core_s1.js) içinde asıl CORE'a iki koldan yürüyüş, dört saatlik tam fiyat label olgunlaşması, hem olay hem kontrol öğrenimi, karşıt sonuçlar ve belirsizlik istatistiği kaydedildi. Özel veriyle CLI: `node replay_macro_waves_in_existing_core_s1.js PRIVATE_ROWS.json PRIVATE_MACRO_LEDGER.csv`; çıktı yalnız toplulaştırılmış ölçümler ve SHA256 runId'dir.
- [independent_event_research_query_s1.js](independent_event_research_query_s1.js) aynı tam M15 piyasa penceresi ve gerçek fiyat hedefiyle güncellendi. Raw query çıktısı **özel tutulmalıdır**, zira anchor/due spot fiyatları içerir.
- [adaptive_rule_discovery_s1.js](adaptive_rule_discovery_s1.js) arşiv `POST_RELEASE_ONLY` kanıtını yalnız `DISCOVERY_FULL_ARCHIVE` içinde, `firstprintVerified=false` ve iki kaynak-lineage ile açıkça kabul eder. STRICT kip değişmedi.
- [replay_macro_waves_in_existing_core_s1.test.js](replay_macro_waves_in_existing_core_s1.test.js) yedi yeni entegre test: learned macro rules, exact maturity, source strict firewall, assumed availability, fiyat/lineage sahteciliği, yinelenen kontrol ve eksik fiyat karantinası. Yeni testler var olan GitHub Actions workflow'una eklendi.
- **Ek test sonucu:** 7/7 yeni entegre kod testi izole JS ortamında geçti. CI run sonucu ayrıca okunmalı.

**S1 bilimsel karar:**
`STRUCTURAL_MACRO_TO_EXISTING_CORE=PASS`;
`MATURITY_TIME_LEAKAGE_CONTRACT=PASS` (sentetik regresyon + geçmiş fiyat bütünlük denetimi);
`REAL_ECONOMIC_CONDITIONAL_GENERALIZATION=NOT_PROVEN`;
`CERTIFIED_PIT_S1=FAIL`;
`MODEL_GATE=FAIL`;
`S2_S3_S4=NOT_STARTED`;
`TRADE_ACTIONS=0`;
`APP=UNCHANGED`.

**Sonraki gerçek eksik:** aynı ekonomik açıklama ailesindeki UP/DOWN çelişkisinin, haber öncesi dolar/faiz/gümüş, pozisyon stresi, ilk tepkide liderlik ve farklı hareket rejimleriyle ilişkisini *origin-safe* şekilde yeterli bağımsız örnekte çözmek. Yalnız başına 28 istihdam / 28 CPI gözleminden oluşan iki ortalama, bitmiş adaptif ekonomik kural modeli değildir. CME SI/NQ/ZN/CL saatlik kaynakları bulundu, ama continuous futures roll ve exact 2023 observed-at henüz doğrulanmadığından bu deneyde sessizce eklenmedi.

**Deney özeti:** WORKSTREAM=MODEL | STAGE=S1 | INPUT=69 yayın / 57 tam / 164 olaysız CORE anchor / 221 matured | OUTCOME=ASL CORE öğrenme kanıtı var, ekonomik üstünlük yok | SCIENCE=FAIL | NEXT=kanıt sınıflı çapraz piyasalar + içsel koşullu ayrıştırma, bağımsız karşıt-vaka doğrulama.


## 5. Çapraz piyasa eklemesi: aynı CORE üzerinde ayrıca yürütülen kanıt-dereceli duyarlılık

2023–2025 Neon CME sürekli vadeli saatlik serileri SI (gümüş), NQ (Nasdaq), ZN (10Y tahvil vadeli) ve CL (petrol) için bulundu. As-of piyasa özellikleri, **tamamlanmış** 1h barın bitişi haber sonrası 60dk XAU karar çıpasından **önce veya eşit** ve en fazla **75 dakika eskiyse** kabul edildi; ardışık H1 bar başlangıçları tam 1 saat ayrılmak zorunda. Hiçbir eksik bar sıfırla doldurulmadı.

**Gerçek makro olaylarındaki kapsama:** 57 olayı kapsayan NQ **57/57**, CL **57/57**, ZN **51/57**, SI **10/57**. Çok eksik SI güvenilir bir zorunlu açıklayıcı alan yapılamaz.

**Ek deney:** `independent_event_research_query_s1.js --cross-assets` opsiyonu ve `replay_macro_waves_in_existing_core_s1.js ... --cross-assets` opsiyonu yalnız research-only koşuda CME H1 sinyalini iki CORE koluna **birlikte** ekler. Aynı baz hareketi, aynı ekonomik etkinlik ve kontroller korunur, yeni algoritma/model branşı oluşturulmaz. CME continuous future verisinin contract roll ve 2023 ilk-provider-availability sertifikası bulunmadığı için **STRICT_WALK_FORWARD başarı iddiası yasak**.

| CROSS-MARKET yapılandırmasında ölçüm | Ekonomi dahil CORE | Yalnız piyasa CORE |
|---|---:|---:|
| İki kolda karşılaştırılabilir tüm tahmin | 194 | 194 |
| Doğru yön | 99/194 | 99/194 |
| Brier hatası | **0,256040** | **0,251404** |
| Bağımsız makro yayın tahminleri | 38 | 38 |
| Ekonomik olay doğru yön | 19/38 | 17/38 |
| Makro yayın Brier hatası | **0,266061** | **0,251126** |

Makro yayım bazlı açıklayıcı bootstrap Brier iyileşmesi **−0,014935**, %95 **[−0,042748; +0,009971]**; hem sıfırı kapsar hem işaret olarak ekonomik-on modeli olumsuzdur. İlk XAU-only koşusu ve bu yeni koşu **196 vs 194 / 40 vs 38 farklı değerlendirilebilir örnek** içerdiği için çapraz piyasanın bağımsız iyileşmesi/kötüleşmesi hakkında doğrudan tek sayı karşılaştırması yapılamaz. Makro sürpriz özelliklerinin ek faydası her yapılandırmada, aynı gözlem kümesindeki aynı CORE'un sürprizsiz koluyla kıyaslandı.

**Bilimsel karar değişmedi:** İstihdam/CPI dönemlerinde karşıt UP/DOWN sonuçlarını genelleyen ve olasılık kalitesini doğrulayan ekonomik karar kuralı hâlâ gösterilemedi. CME eklemek tek başına başarı getirmedi. Görülmüş retrospektif performansa göre sonradan tek yapılandırmayı seçip kör OOS saymak yasak.

**Ek üç test:** Tamamlanmış CME H1 yanında missing SI'nin gerçekten eksik kalması, gelecekte/eskimiş CME barının karantinaya alınması, SQL'in yayın kararından sonraki barı kullanmaması. İlgili bütün matematiksel S1/core testleri **44/44** izole JS harnessinde PASS; GitHub Actions sonucu ayrıca teyit gerektirir. MODEL_GATE=FAIL.


## 6. Tek odaklı koşullu öğrenme deneyi — mevcut CORE, yeni model değil (16 Ekim 2026)

**Değişiklik:** `adaptive_rule_discovery_s1.js` içinde isteğe bağlı `forecastMethod=LOCAL_MATURED_EXAMPLES` eklendi. Mevcut bir rule prototipine bağlı **yalnızca olgunlaşmış** geçmiş örnekler arasından en yakın 12 örnek seçilir; 8 öncül (parent) eşdeğer gözlem ile shrinkage uygulanır. Yeni ANN/KNN proje modeli veya manuel ekonomik yön kuralı yok: yöntemin algoritmik tahmini ve hafızası mevcut adaptif CORE içinde; varsayılan `PROTOTYPE` **değişmedi**. Aynı yöntem hem ekonomik açık hem ekonomik kapalı CORE koluna uygulanır; parametreler gerçek koşu sonrasında seçilmedi. `replay_macro_waves_in_existing_core_s1.js` için `--local-evidence` seçeneği eklendi.

**Sentetik karşıt-örnek sınaması:** Tek adaptif rule 28 olgun etikete ulaşmışken, negatif ve pozitif ekonomik durumlar için sabit prototip her ikisine 0,50 UP olasılığı verirken, olgun örneklere koşullanan yöntem 0,80 / 0,20 UP olasılığı veriyor. Bu **kodun koşullu ayrıştırma yeteneği** kanıtıdır, gerçek ekonomi doğruluğu değildir.

**Gerçek 2023–2025 retrospektif ekonomi-on/off tekrar koşuları** (Brier düşük daha iyi):

| Piyasa bağlamı ve aynı örnekler | Forecast | Ekonomik açık CORE Brier | Ekonomik kapalı CORE Brier | Ekonomik olaylarda açık / kapalı Brier |
|---|---|---:|---:|---:|
| Yalnız XAU; 196 tahmin / 40 olay | mevcut PROTOTYPE | 0,255918 | **0,253149** | 0,264965 / **0,256879** |
| Yalnız XAU; aynı 196 / 40 | LOCAL_MATURED_EXAMPLES | 0,259068 | **0,258381** | 0,265498 / **0,261829** |
| XAU+CME; 194 tahmin / 38 olay | mevcut PROTOTYPE | 0,256040 | **0,251404** | 0,266061 / **0,251126** |
| XAU+CME; aynı 194 / 38 | LOCAL_MATURED_EXAMPLES | 0,266928 | **0,258135** | 0,265123 / **0,245481** |

Bu deneyde yeni koşullu forecast, **hiçbir piyasa bağlamında ekonomik alpha göstermedi ve mutlak Brier değerlerini kötüleştirdi**. Parametre değiştirilip aynı arşivde sonuca göre ayar yapılmadı. **Varsayılan CORE PROTOTYPE olarak tutuldu; deneysel yöntem otomatik terfi ettirilmedi.** Yeterince çeşitli bağımsız piyasa/ekonomi vakası olmadan yüksek yerel farklılık sentetikte güzel gözükse de gerçek piyasada overfit olabilir. Aynı CORE'un event present/missing kontrolleri, olgun label filtreleri, sıkı araştırma/vintage ayrımı devam eder. Tüm ilgili JS S1 teknik testleri **46/46** izole ortamda PASS; gerçek model geçişi **FAIL**.

**Karar:** `S1_LOCAL_CONDITIONAL_TECHNICAL=PASS`, `S1_LOCAL_CONDITIONAL_SCIENCE=FAIL`, `ACTIVE_FORECAST_METHOD=PROTOTYPE`, `MODEL_GATE=FAIL`. S2/S3/APP değiştirilmedi.
