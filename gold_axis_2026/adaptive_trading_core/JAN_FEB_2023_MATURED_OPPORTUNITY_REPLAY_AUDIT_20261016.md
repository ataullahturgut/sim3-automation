# GOLD-ADAPTIVE-MODEL-APP-01 — Ocak ve Şubat 2023 fırsat öğrenimi + geri dönüşlü araştırma koşusu

**WORKSTREAM=MODEL | SAME CORE/SAME BRANCH | MODE=DISCOVERY_FULL_ARCHIVE | SCIENCE_GATE=FAIL | LIVE_TRADE=false | APP=UNCHANGED**

## 1. Sorunun teknik karşılığı
Kullanıcı, 6–9 Ocak fiyatları için dışarıdan AL noktası işaretlemeyi değil, önceki ekonomik/piyasa davranışlarından öğrenen **S1→S2→S3** zincirinin Ocak ve Şubat 2023'te ne yaptığını görmeyi istedi. **6 Ocak tarihini giriş özelliği yapan bir kural eklenmedi.** Yanlış/başarısız kararlar silinmedi. Model araştırma sonuçları bilimsel kabul değildir.

## 2. Gerçek kaynak ve öğrenim
Kaynak: Neon Gold Control, `gold_research_evduka_xau15m_bidask_candidate`, tek EV Trading Labs / Dukascopy türevi BID/ASK; kullanılan fiyat **(bid_close+ask_close)/2**. Orijinal 2023 tarihli ilk erişim kanıtı ve gerçek banka icra kotasyonları yok. Ekonomik olay ilk-baskı ve konsensüs PIT henüz doğrulanmadı.

S3 içindeki `adaptive_opportunity_learning_s3.js` yalnız **S2 START/REENTRY** epizodu başlarken giriş adayı açar; olgun tamamlanmış seanslarda **5/10/20 seans** sonra ücret dahil net log-getiri öğrenir. Ücret: %0,8 AL ve %0,8 SAT. Destekli kohort ortalama ve standart hata öğrenir, düşük kanıtta çekimser kalır.

Yıllık segmentler (yıl ortasındaki açık etiketler yıl değiştirilirken taşınmıyor; sonuçları henüz bilinmeyenler otomatik doğru sayılmıyor; fast-S2 her yıl yeniden ısınıyor). Yalnız **olgunlaşmış S3 opportunity knowledge**, `knowledge()/fromKnowledge()` yoluyla ardışık yıllara taşındı:

| Eğitim yılı | M15 bar | Kabul edilen giriş çıpası | Olgun ücretli etiket | Sansür |
|---|---:|---:|---:|---:|
| 2023 | 23.544 | 583 | 1.478 | 189 |
| 2024 | 23.733 | 571 | 1.443 | 249 |
| 2025 | 23.638 | 590 | 1.375 | 371 |
| **Toplam** | **70.915** | **1.744** | **4.296** | **809** |

**Çok önemli:** 4.296 etiket bağımsız işlem değil; vadeler ve örnekler örtüşüyor. Her horizon için ayrıca `effectiveN` tutuldu. Sayılar sadece **S2 fiyat-evresi + S3 opportunity** hafızasının geçmiş öğrenimidir; **2023–25 tamamından eğitilmiş ekonomik S1, S2 slow veya tam S3 karar CORE checkpoint'i değildir**. S1'in ekonomik OLAY-02/ÖĞREN-03 ve firstprint girdilerini transfer ettiği iddia edilmez.

Kalıcı olgun araştırma özeti: [OPPORTUNITY_ARCHIVE_DISCOVERY_MODEL_2023_2025.json](OPPORTUNITY_ARCHIVE_DISCOVERY_MODEL_2023_2025.json); ham fiyat GitHub'a taşınmadı.

2023–2025 başlangıç-evresi altın AL araştırma getiri beklentisi:

| S2 FAST:TREND:UP + vade | Olgun etiket n | Daha seyrek etkin n | Bağımsız-kohort ortalama net log-% | SE | İhtiyatlı alt değer |
|---|---:|---:|---:|---:|---:|
| 5 seans | 874 | 135 | −1,0210 | 0,2167 | −1,2377 |
| 10 seans | 817 | 67 | −0,5319 | 0,4154 | −0,9473 |
| 20 seans | 701 | 31 | +0,5983 | 0,7633 | −0,1651 |

**Sonuç:** 5/10 net olumsuz; 20 seansın ortalaması olumlu ama belirsizlik eklendiğinde güvenilir olumlu alım avantajı yok. `learnedResearchPreference=NO_SUPPORTED_ENTRY_ADVANTAGE`. Bunlar aynı arşiv içinde keşfedilmiş koşullu/örtüşen örnekler; geleceği görmeyen bağımsız test değildir.

## 3. Ocak–Şubat 2023 tek kaynaklı research replay
2023 Ocak 3 – Şubat 28, toplam alınan 3.750 M15 bar; Türkiye araştırma-seansı tarihine göre 3.745 bar işlendi (son 5 bar Mart seansına aitti), aynı M15 akışı, başlangıç **100 USD CASH**, **saat filtresi yok**, tek yön **0,8%**. Tamamlanmış yavaş S2 seansı veya M15 fiyatı gelecek karar anına taşınmadı.

İki mevcut S3 araştırma modu ayrı karşılaştırıldı:
- `INTEGRATED_LONG_RESEARCH`: mevcut 14/56 gün; yeni opportunity hafızası karar açısından kullanılmıyor.
- `OPPORTUNITY_MATURED_RESEARCH`: aynı S3 içinde, `opportunityResearch` olgun kohortları ve destek-belirsizlik koşullarıyla aday AL/SAT yönlendiriyor; destek varsa sonraki gözlenen M15 barında shadow işleme girer, bankada gerçek emir verilmez. Ocak-Feb akışına `fromKnowledge` ile **2023–2025 retrospektif öğrenme parametreleri** yüklendi, sonradan gelen Ocak/Şubat olgun etiketleri aynı araştırma hafızasında güncellendi.

| Yöntem | 31 Ocak USD | 28 Şubat USD | AL | SAT | Durum |
|---|---:|---:|---:|---:|---|
| Mevcut S3 uzun 14/56 | 100,00 | 100,00 | 0 | 0 | CASH |
| **Yeni olgun-fırsat karar ablasyonu** | **100,00** | **100,00** | **0** | **0** | **CASH** |
| Her zaman nakit | 100,00 | 100,00 | — | — | CASH |
| 3 Ocak'ta ilk fiyatla al + ay sonu sat | **103,8558** | **98,4161** | Kıyas | Kıyas | Hipotetik GOLD |

Kıyas iki farklı tasfiye ufku içeriyor: Ocak kolonunda Ocak sonunda varsayımsal satış, Şubat kolonunda Ocak başından Şubat sonuna kesintisiz GOLD elde tutup Şubat sonunda satış. Fiyatlar: Jan ilk **1827,13**, 31 Ocak son **1928,31**, 28 Şubat son **1827,31**. Bu araştırma MID fiyatı, gerçek bankanın BID/ASK'ı değildir.

### Örnek gerçek o-an çıktı
| Tarih, UTC | TRT | S2 sinyali | Fiyat $/ons | Yeni S3 |
|---|---|---|---:|---|
| 6 Ocak 03:15 | 06:15 | START UP | 1840,54 | KEEP CASH; net alım kanıtı yok |
| **6 Ocak 17:00** | **20:00** | **START UP** | **1863,485** | **KEEP CASH; net alım kanıtı yok** |
| 9 Ocak 03:15 | 06:15 | START UP | 1877,51 | KEEP CASH |
| 1 Şubat 20:45 | 23:45 | START UP | 1952,26 | KEEP CASH |
| 3 Şubat 15:30 | 18:30 | START DOWN | 1875,675 | CASH korunuyor |

Ocak–Şubat yeni S3 araştırma karar nedenleri: **50** `OPPORTUNITY_NO_SUPPORTED_NET_ENTRY`, **2.996** `OPPORTUNITY_NO_NEW_EPISODE`, **656** kaynak/hazır-olmayan kısa evre çekimserliği, **43** mevcut CASH pozisyonunun korunması. Hiçbir veri noktası banka saati diye reddedilmedi.

S1 market-only: **3 fiyat-evresi kural prototipi**, **218** kural çıpası, **208** olgun 4 saatlik sonuç; ekonomik PIT özellikleri verilmedi. Bu 3 fiyat prototipini önceki S1 makro prototipleriyle karıştırma. Macro firstprint/ISM vb. halen sisteme bağlanmadı.

## 4. Kritik doğrulama ve bilimsel durum
- **7/7** izole mevcut JS test PASS: geçmişi label öncesinde kullanmama, sansür, checkpoint/knowledge ayrımı, yetersiz delilden işlem açmama, destekli sentetik avantajda **sonraki M15 barında** shadow AL.
- Testlerde kârlılık, genellenebilir ekonomi, 2023–2025 ilk-vintage ve kör OOS PASS iddiası yok.
- Bu deneyde **gelecek yıllardan öğrenilen opportunity sonuçları Ocak 2023'e önden yüklendi**; yani `DISCOVERY_FULL_ARCHIVE` içinde **IN-SAMPLE AÇIKLAYICI GERİYE DÖNÜK DENEY**. STRICT_WALK_FORWARD veya 2023 Ocak'ta gerçekten mevcut yatırımcının becerisi değildir.
- OLAY-02/ÖĞREN-03'ten bilgi aktarılan koşullu **ekonomik mekanizma**, hareketin **kalan büyüklüğü ve süresi**, TAM **Q(CASH/GOLD, AL/TUT/SAT)** öğrenimi hâlâ bilim kapısını geçmedi. Yeni fırsat hafızası taşındı fakat 3 yıllık arşivi tamamıyla açıklayan **net yatırım stratejisi üretilmedi**.

**Gösterilen başarı: Gerçek 2023–2025 S2 hareket-girişlerinin olgun net getiri istatistiği kalıcı biçimde öğrenildi ve mevcut S3 kararı üzerinde ablation yapıldı. Gösterilemeyen başarı: Ocak 2023 büyük yükselişine AL ile katılmak ve Şubat 2023 zararlı dönemde pozisyonu yönetmek. Başarı kapısı FAIL, 0 işlem ve karşılaştırma gizlenmedi.**

**Ana geliştirme açığı:** `FAST:TREND:UP` durumu ekonomiyi ayırt etmediği için farklı türdeki yükseliş başlangıçları aynı havuza düşüyor. Ekonomik ilk-baskı, USD/faiz/gümüş tepkisi ve gerçek uzun-döngü kalan-hareket değeri **origin-safe** birleşik ayrıştırma ile öğretilmeden "6 Ocak benzeri" fırsatları diğer yalancı başlangıçlardan genellemek mümkün değil. Yeni isimli algoritma veya yeni model familyası açmak yerine aynı M2→M3→M4→M5 CORE'da bunu çöz.
