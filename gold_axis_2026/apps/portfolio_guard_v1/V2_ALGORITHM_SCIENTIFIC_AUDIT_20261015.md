# GOLD PORTFOLIO GUARD — V2 ALGORİTMA DENETİMİ
**Tarih:** 2026-10-15 | **Statü:** RESEARCH_SHADOW / NOT_PREDICTIVE_VALIDATED
**Öncelik:** Portföyü büyük DOWN riskinden koru, marjinal UP olursa katıl; gereksiz işlem yapma. 15 dakika yalnız veri kontrol kadansıdır, işlem sıklığı hedefi değildir.
**Değişiklik türü:** Bilimsel güvenilirlik / olay öğrenme kalite düzeltmesi. Yeni kâr/işlem modeli onaylanmadı.

## 1. Kaydedilen ölçülebilir V2 düzeltmeleri
| Problem | V1 | V2 |
|---|---|---|
| Aynı tarihsel olay iki farklı dosya kimliğiyle öğreniliyor | 92 olgun örnek satırı | **92 adayın 12 mükerrer kaydı ayrıştırıldı, 80 eşsiz checkpoint** |
| Tekrarların koşullu risk payını çarpıtması | k=9 ham vaka kimlikleri | k=9 `unique_checkpoint_id + timestamp` benzersiz; en iyi belge düzeyini (D2>D1>D0) korur |
| 96h etiketinin henüz bilinmemesi | Temel başlangıç olgunluğu kontrolü | İlk araştırma anında açık `maturesUTC` + sonraki ay kayıt kapısı |
| Olay seçme yanlılığı | Yalnız tarihsel büyük swing/event arşivi | **163 tarafsız takvim saatiyle** örneklenen fiyat dönemi kontrolü; 14'ünde -%3 alt uzama |
| Ekonomik nedeni fiyatla karıştırma | G01/G07 makro penceresi | 96/96 ilk yayın doğrulanmadı ve nedensellik doğrulanmadı; **`UNKNOWN`** ve `UNRESOLVED` kabul edilir |
| Bilinmeyen rejim | kNN risk skoru bazen düşük | Arşivden uzaklığı ayrı `OUT_OF_DISTRIBUTION` durumu; düşük skor “güvenli” sayılmaz |
| Komisyon | %0,8 alış ve %0,8 satış | Komisyonlara göre asgari tam tur fiyat hareketi **%1,6194**. Gerçek banka spreadi eklenince gereken hareket daha büyüktür |
| Sonucu görüp aynı ay modeli güncelleme | Dondurulmuş V1 | Ay sonu `learning_v2`: 96 saat olgunlaşmamış sonuç eğitim dışı; aynı ay parametre değişikliği yasak |
| Gerçekten kârı artırma | Jan2026 V1 +%19,75 | **Henüz kanıt yok; V2 diagnostik ve gölge model.** |

## 2. Jan 2026 kararlarında mükerrer örnekleri ayırmanın gerçek etkisi
| Karar | Eski seçilmiş vaka-ağırlıklı aşağı uzama payı | Mükerrer ayrıştırılmış pay | Takvim kontrol 21-komşu payı |
|---|---:|---:|---:|
| **5 Ocak 09.30 TSİ AL** | 0,578487 | 0,577350 | 0,069319 |
| **29 Ocak 18.15 TSİ SAT** | 0,109739 | 0,215064 | 0,099537 |

**UYARI:** Bu üç kolon da **olasılık tahmini değildir**; arşivden seçili olay, benzersiz olay ve takvim örneklemlerinin ağırlıklı tarihi gerçekleşme paylarıdır. Etkin ve kalibre edilmiş bir alarm olabilmeleri için negatif kontroller, bağımsız performans sınaması ve banka maliyeti gerekir.

29 Ocak'ta eski arşiv yaklaşık %11 payla güvenli gibi görünebilirdi; tekilleştirme sonrası oran yaklaşık %21,5 oldu. Ancak en yakın örneğin normalize mesafesi **1,28**; bu OOD rejimde risk skorunu ticari sinyal olarak yorumlamıyoruz.
Jan2026 V1 işlemleri **5 Ocak AL**, **29 Ocak SAT**, ay sonu **$119,753917 nakit** olarak korunur. **V2 ek getirisi = hesaplanmadı; yeni al/sat onayı yok.** Önceki ekonomik overlay'in V1'e ek katkısı aynı iki işlem nedeniyle $0'dır.

## 3. Zaman seçilmiş kontrol örnekleri
- Neon HistData tam M15, 2023–2025, karar saati **15:00 UTC**, takvimden bağımsız her 4. gün. Fiyatın gelecekte ne yaptığına göre örnek seçilmedi.
- 163 nokta: 2023 35 (1 büyük DOWN), 2024 65 (5 DOWN), 2025 63 (8 DOWN); **14 / 163** 96h sonraki düşük fiyatta en az -%3 uzama.
- Bu noktalar **kesin habersiz / olaysız günler değildir**. Gerçek olay/olaysız ayrımı firstprint verisi gerektirir.
- Üretilen `forward96hlowpct` ve `forward96hhighpct` **yalnız tarihi etiketlerdir**, canlı karar sorularına predictor olarak girmez.
- Özellikler XAU son tamamlanmış M15; NQ/ZN yalnız tamamlanmış geçmiş H1. Kaynak Neon/HISTDATA ve CME DATABENTO, gerçek banka ASK/BID değil.
- Kaynak dosyası `data/CALENDAR_CONTROLS_2023_2025_M15_96H_V1.csv` ayrıca Git blob SHA ile kilitli: `cd6f520d4991dc7d429cb6e06deb9b73e161e6f6`.

## 4. Kronolojik kontrol validasyonu — dürüst başarısızlık
2023–2024 tarih seçilmiş 100 kontrol örneği modelin geçmişi; 2025 tarihli 63 kontrol daha sonraki dönem.
- 2023–24 aşağı bacak: **6 / 100**.
- 2025 aşağı bacak: **8 / 63**.
- 2025 Brier skoru (sabit geçmiş ortalaması): **0,115346**.
- 2025 Brier skoru (21 yakın takvim kontrolü ağırlıklı): **0,115535** (**daha kötü**).

**Sonuç:** Yakın-komşu takvim kalibrasyonu mevcut haliyle sabit öncülden daha iyi tahmin üretmedi. Bu yüzden V2, riski ekonomik tahmin olarak **yayınlamıyor ve otomatik işlem açmıyor**. Sonuç ayrı/test edilmemiş hiperparametrelerin başarı iddiası değildir. 2025'i araştırma boyunca daha önce görmüş olmak gerçek blind OOS niteliğini ayrıca sınırlıyor.

## 5. Jan→Feb 2026 öğrenme izleme
`monthly_learning_v2.js` saf/deterministik akıştır; `GET /api/learning/v2` çıktı üretir.
- 5 Ocak alış → ilk 96h hedefinin olgunlaşma zamanı **9 Ocak 06:30 UTC**.
- 29 Ocak satış → 96h hedefi ancak **2 Şubat 15:15 UTC** olgunlaşır.
- **1 Şubat 2026 başında bu 29 Ocak etiketi henüz bilinmez.** V2 modeline sızdırmak yasak.
- Şubat'a nakit **$119,753917** ve V1 sürümü ile başlanır. `autoRetrain=false`, `riskCalibrationReady=false`.
- Ay sonucu sonradan görülünce yalnız gelecek döneme yönelik yeni sürüm önerilebilir; Jan2026'a dönüp başarı şişirilmez.

## 6. Doğrulanan ve henüz tamamlanmayan işler
**Tamamlanan altyapı:** M15/H1 as-of kaynak kontrolü, kopya vakanın ayıklanması, geçmişte olgunlaşmamış hedefin dışlanması, zaman sabitli kontrol grubu, 2025 sonraki dönem kıyası, maliyet eşiği, 8 açık karar sorusu, aylık devir/etiket olgunluğu, Git blob sürümü ve Windows/Linux otomatik testleri.

**Henüz yapılmadı:** (1) tam tarih/saat/vintage haber doğrulaması; (2) gerçek olaysız kontrol günlerinin kaynakla kanıtlanması; (3) G01–G06 için ayırıcı faiz/FX/SI/akış mekanizma yanlışlama testleri; (4) 24/48/96h kalan önlenebilir hareketin güven aralığı kalibrasyonu; (5) gerçek BID/ASK, spread ve emir verilebilirlik; (6) kör ardışık aylarda kazanç/zarar tahmin doğrulaması; (7) maliyet-sonrası katma değer kanıtı.

**Bilinçli güvenlik kararı:** Bu eksikler giderilmeden V2'nin geçmiş risk paylarını doğrudan AL/SAT yapacak algoritmaya çevirmiyoruz. V1 ve V2 kodları ayrı; UI V2 denetimini görüntülerken V1 portföy kaydı değişmez.

## 7. Tekrar çalıştırma
- `BASLAT.bat` bilgisayarda aynı şekilde çalışır.
- Yeni yan menü: **Algoritma V2 denetimi**.
- `npm.cmd test` (Node >=18, Windows PowerShell npm.ps1 engeli için .cmd kullan).
- `npm.cmd run audit` (kayıtlı 2025 kontrol validasyonu ve 2026 iki olay analizi).
- GitHub Actions otomatik Windows+Ubuntu koşularında test dosyaları `test.js`, `v2.test.js` ve `monthly_learning_v2.test.js` değerlendirilir.
- `GET /api/algorithm/v2` ve `GET /api/learning/v2` salt okunur, uygulama gerçek bankaya bağlanmaz.
