# KAVİS CORE S1 — Ocak 2023 gerçek piyasa verisi, retrospektif kaynak/ilk kural denetimi

**Tarih:** 16 Ekim 2026. **Çalışma hattı:** MODEL, [bağlayıcı manifest](../GOLD_ADAPTIVE_TRADING_MODEL_APPLICATION_PROJECT_MANIFEST.md).  
**Algoritma:** [adaptive_rule_discovery_s1.js](adaptive_rule_discovery_s1.js) — **aynı geliştirme çizgisi; yeni model ailesi, Git dalı, ekran veya AL/SAT kuralı oluşturulmadı.**  
**Veri okuma:** Neon (read-only), [tarihli SQL](JAN2023_RECONSTRUCTED_ASOF_S1_INPUT.sql); [çalıştırılabilir, kaynak denetimli araştırma adaptörü](replay_reconstructed_jan2023_s1.js). Ham lisanslı fiyatlar GitHub'a eklenmedi.  
**Deney:** 2023-01-03 04:00 UTC – 2023-01-31 20:00 UTC; 4 saatlik aralıklarla tamamlanmış XAU M15, daha önce tamamlanmış NQ/ZN/CL H1 koşullu getiriler; 1.5 yüzde puan başına bir sabit normalizasyon birimi, `noveltyDistance` deneysel başlangıç 0.3, `maxRules=16`.
**Kanıt sınıfı:** `RETROSPECTIVE_RECONSTRUCTED_ASOF_NONBLIND`. İlk yayım/vintage PIT sertifikası **YOK**; CME continuous future contract-roll oluşumunda geriye dönük bilgi kullanımı dışlanmadı. ZN **tahvil futures fiyatı**; ABD reel faiz/verim oranı değildir. SI (gümüş) Ocak 2023 H1 serisinde seyrek olduğundan **varsayılmış nötr sinyal olarak kullanılmadı**. OLAY-02/ÖĞREN-03 read-only arşiv: as-of ilk haber kanıtları eksik, bu deneye henüz olay/DNA etkisi verilemedi.

## Deneyin sayısal sonucu

| Kontrol | Ocak 2023 sonucu |
|---|---:|
| Tam M15 ve tamamlanmış H1 ile dört saatlik gözlem | **102** |
| Dört temel özellik kapsaması (XAU / NQ / ZN / CL) | **102 / 102 / 102 / 102** |
| Deneysel `noveltyDistance=0.30` ile oluşan durum prototipleri | **8** |
| Bunlardan 4s olgun sonucu `n>=8` olanlar | **4** |
| Toplam farklı ufuklarda olgunlaşmış etiket | **338** (farklı ufuklar örtüşebilir; bağımsız 338 olay DEĞİL) |
| Yanlış zaman ufkunda öğrenmeyi engellemek için atlanan gecikmiş etiket | **85** |
| Ay sonu henüz olgunlaşmamış etiket görevleri | **87** |
| Gerçek Ocak verisinde kanıtlı kural bölünmesi/birleşmesi | **0 / 0** |
| İcra edilen AL veya SAT | **0 — S1'de yatırım politikası YOK** |

### İleri bilgi kullanmadan, gerçekleşmiş 4s etiket ile prequential kontrol

Aynı ay içinde her tahmin verilmeden önceki olgun sonuçlar dışında veri kullanılmaması amaçlandı. Skor tablosundaki `model` yalnız `forecastAtDecision` kayıtlarından, hedef 4 saat sonra olgunlaştığında hesaplanmıştır. Karşılaştırma; orijinal karar anına kadarki tamamlanmış UP oranıdır. 70 karşılaştırılabilir, yeterli geçmişli 4h etiketinde:

| İstatistik | S1 kural prototip modeli | Önceki olgunlaşmış UP oranı |
|---|---:|---:|
| Doğru yön | **31 / 70** | **35 / 70** |
| Brier kaybı (küçük iyi) | **0.2714222191** | **0.2563301662** |
| S1 getiri büyüklüğü MAE, log-% puan | **0.2983294977** | N/A (temel oran getiri tahmini yapmıyor) |

**Sonuç:** S1 şu haliyle *yalnız fiyat + NQ/ZN/CL koşullu durum* öğrenmesinde tarihsel basit taban ölçütünü **GEÇMEDİ**; `S1_REAL_ECONOMIC_RULE_GATE=FAIL`. 2023-01'de iyi getiri sağlanmış gibi gösterilemez. `0 AL/SAT`, öğrenilmiş politikanın muhafazakâr başarısı değildir, **S1'in hiç politika üretmemesinden** kaynaklanır.

### Yapısal parametre hassasiyeti — aynı Ocak sonuçlarını seçerek optimize etmek yasak

Modelde yalnız **yapısal** prototip açma mesafesi değiştirildi; sonuçlar başka bir dönemde doğrulanmadı.

| Açılma uzaklığı | Kural prototipi | 4s skor n | Model Brier | Önceki UP oranı Brier |
|---:|---:|---:|---:|---:|
| 0.30 | 8 | 70 | 0.2714222 | 0.2563302 |
| 0.50 | 2 | 73 | 0.2596260 | 0.2587997 |
| 1.25 | 1 | 73 | 0.2587997 | 0.2587997 |

`noveltyDistance=0.30`, 0.50 veya 1.25'ten **hiçbiri diğerinden iyi diye seçilmedi**: bu değerler Ocak 2023'te incelenmiş, yapısal hiperparametre hassasiyeti gösterilmiştir. Daha iyi kural keşif seçimi ek ay/ayrılmış veride önceden dondurulmuş protokolle yapılmalıdır. Tek bir kural üretip temel oranla aynı Brier sonucu almak ekonomik öğrenme kanıtı değildir.

## Kodlanan somut eklemeler ve testler

1. **P0** `forecast` eski bir asof anını daha sonra eğitilmiş checkpointle yeniden üretemez (`HISTORICAL_FORECAST_REQUIRES_ASOF_CHECKPOINT`).
2. **P0** geçmiş M15 bar kapanışı, asof saat, model clock, kaynak kayıt/yetki ve hangi kaynağın MARKET veya doğrulanmış EVENT olduğu gözlenir; yetkisiz kaynak adı reddedilir. Bu whitelist dışsal gerçeklik sertifikası *değildir*.
3. **P1** geç kalan 4s etiketi 5s15dk getiriyi 4s etiketine dönüştüremez; izinli gecikme 15dk. İşlem günleri/tatil ve uzun ufuklar için olgunlaşmayan görevler ayrıca saklanır.
4. **S1** birbirine zıt olgun sonuçlar tek prototipte yeterli destek, özellik-ayrışması, en az 32 mature 4h örneği, en az 12/12 karşıt alt grup, >= 3.5 Welch ayırıcı istatistiği ve >=0.2 log-% farkı ile saptanırsa kuralı **iki koşullu alt kurala bölebilir**. Eski etiketleri kaybetmeden yeniden atar; henüz olgunlaşmamış etiketlerde eski ID'yi yeni alt kurala yönlendirir.
5. Bölünme sentetik zıt-ekonomik-girdi testinde **PASS**, aynı gerçekleşmeli olaysız/kontrol örneğinde **no false split PASS**; **Ocak gerçek gözlemlerinde henüz kural bölünmesi olmadı**.
6. [CI sözleşme testleri](https://github.com/ataullahturgut/sim3-automation/actions/runs/38921272236): eski CORE V0 **7/7**, yeni S1 matematiksel birim testleri **14/14**, Jan asof adaptör testleri **5/5**, CI tamamı PASS. Testler tarihsel ekonomik üstünlük kanıtlamaz.

## Kabul kararı ve bir sonraki engel

- **S0:** zaman/fiyat kapanış ve kayıtlı kaynak whitelist korumaları iyileştirildi, gerçek 2023 haber ilk baskı ve CME continuous-roll geriye dönük hata kontrolü henüz tamam değil.
- **S1:** matematiksel prototip, olgun sonuç istatistiği, sınırlandırılmış split, merge ve checkpoint kodlandı. **Gerçek ekonomik mekanizma ile pozisyon kararına genelleme kanıtı yok; basit taban başarısı geçilemedi**.
- **S2:** çok-günlü olay başlangıç/yaşam döngüsü öğrenicisi **henüz yok**.
- **S3:** net fee-wealth critic ve AL–TUT–SAT portföy politikası **henüz yok**.
- **S4:** Ocak 2023 model-gate **FAIL**; Şubat'a geçilmez, `TRAINED_2023_2025=false`.
- **U:** uygulama ayrı, yeni öğrenen CORE bağlı değil.

**Tek meşru devam:** Aynı S1 içinde ilk yayın, H1 continuous roll, kaynak available-at, ekonomik olay karakteri/karşı-vaka ve (eksik) XAG verileriyle **gerçek ekonomik koşullu örüntü** temsilini tamamlamak, kural kalibrasyonunu ve gözlenen negatif kontrolden daha iyi olma ihtimalini ayrı önceden kayıtlı örneklerde sınamak. Sırf 2023 Ocak'ta daha güzel kural sayısı veya işlem kârı almak için eşik seçmek yasak.
