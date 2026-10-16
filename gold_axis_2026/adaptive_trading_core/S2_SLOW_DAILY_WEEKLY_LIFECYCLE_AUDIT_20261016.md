# GOLD-ADAPTIVE-MODEL-APP-01 — S2 Yavaş Günlük/Haftalık Hareket Katmanı
**Denetim:** 16 Ekim 2026 · **MODEL aynı CORE** · **S1 bilimsel kabul FAIL** · **S2 SLOW geliştirme tamamlandı / bilimsel kabul geçilmedi** · **AL–SAT YOK**.

## 1. Hangi eksik giderildi?
İlk S2 katmanında medyan 3s45dk olan mikro hareketi bir haftaya uzatarak değerlendirmek tüm uzun ufuklarda tek sınıf yaratıyordu. [adaptive_slow_lifecycle_s2.js](adaptive_slow_lifecycle_s2.js) **ayrı bir algoritma/portföy stratejisi değil**, [adaptive_market_core_s1_s2.js](adaptive_market_core_s1_s2.js) altında aynı matematiksel S1+S2 CORE'a bağlanan, *gerçek farklı zaman ölçeğinde* ikincil S2 hareket sensörüdür.

- İstihdam haberlerinin retrospektif actual/consensus alanları **bu deneyin girdisi değil**. Günlük altın kapanışları, on önceki tamamlanmış seans getirisi, sadece seans sonunda bilinen yön/oynaklık durumunu kullanır. Günlük/haftalık başlangıç, devam, düzeltme, yeniden yükseliş ve bitiş etiketleri as-of hesaplanır. Yapısal eşikler (10 seans, |trendZ|≥1,15, iki karşı-sinyal, çekilme katsayısı 1,4) önceden sabittir; sonuçlara bakıp optimize edilmedi. Bu tanımlar **bilimsel gerçek etiketler değildir; algoritmik epizot adaylarıdır**.
- Öğrenme hedefi: aynı uzun epizodun **önümüzdeki 1, 3, 5 veya 10 tamamlanmış işlem seansı içinde biteceğine** dair olasılık, ters tamamlayıcısı devam olasılığıdır. Bu ufuklar *takvim günü değil işlem seansıdır*: 5 seans tipik hafta; 10 seans tipik iki hafta. Tahminler yalnız geçmişte bitmiş veya en az ufuk kadar gerçekten izlenmiş sansürlü örneklerden türetilir. Henüz sonuçlanmamış epizot bitmiş sayılmaz; veri boşlukları bilinmeyen kısımdır.
- **İşlem takvimi araştırma kuralı:** UTC 22:00 günlük referans kesimi; UTC+2s işlem-seans tarih atamasıyla normal cuma→pazartesi kapalı süre **veri kaybı sanılmaz**. Bu resmî altın kontratı settlement saati değil, sabit araştırma kesimidir. Kaynak değişimi / eksik hafta içi oturumu / sınırı geçmemiş fiyat verisi aktif epizodu sansürler. Resmî tatil takvimi yoksa tatil **kesin bilinen kapanış gibi varsayılmaz**, güvenli sansür uygulanır.
- Günün kabulü: ≥80 M15 satırı, en fazla **2 kısmi intraday M15**, son 15 dakikalık barın **tam** olması, en uzun iç boşluk ≤90dk, kapanış fiyatı UTC22 kesimine ≤90dk uzak. Kısmi bar kullanılan **99 gün açıkça kusurlu ancak araştırmaya alınmış** olarak sayılır; bunlar gerçek tam-vintage veri sayılmaz. Eksik veri tam gün olarak **uydurulmadı**. Bu yumuşatma yalnız araştırma kipidir.
- As-of entegrasyon: `observeSlowSession` yalnız UTC22 kapanmış seansın öğrenilmiş slow state'ini belleğe alır. M15 `observe` karar anından **sonra** biten seansın slow özelliğini reddeder; staleness ≤4 takvim günü ve **aynı fiyat source_id** gerekir. Tek [adaptif CORE köprüsü](adaptive_market_core_s1_s2.js) hem mikro evre hem yavaş evre (trendZ, yaş, yön, 5-seans bitiş riski) özelliklerini S1'e sunabilir. Tek checkpoint, ticaret=0. Bu tur canlıya sertifikalı veri veya ticaret politikası taşınmadı.

## 2. Gerçek fiyat veri kapsamı
**Kaynak:** Neon `gold_research_histdata_xau15m_candidate` salt-okunur. Yeniden üretim: [seans toplulaştırma SQL](S2_SLOW_SESSION_AGGREGATE_2023_2025.sql) + [özel verili tekrar koşusu](replay_slow_lifecycle_s2.js); SQL sonucu **özel altın fiyatları içerir, GitHub'a eklenmeyecek**. Retrospektif arşiv; ilk canlı erişim/vintage kanıtlanmış değildir.

| Sene | Seans adayı | Kalite kapısını geçen |
|---|---:|---:|
| 2023 | 257 | 118 |
| 2024 | 259 | 246 |
| 2025 | 258 | 245 |
| **Toplam** | **774** | **609** |

**165 gün** kalite/red sürecinden geçti; özellikle **2023 Mart–Temmuz** çoğu seans ~65–67 bar içerdiğinden kabul edilmedi (normal yakın seans ~92 bar). 2023'ün bu kayıp dönemi üzerinden gizlice haftalık rejim taşınmadı. **7 takvim kırığı** ve **2025 kaynak değişiminde 1 lineage kırığı** raporlandı.

**Gerçek sonuç:** **12 tamamlanmış gün-hafta hareket epizodu**, medyan süre **9 tamamlanmış işlem seansı**, ayrıca **10 sansürlü uzun epizot**. Bu sayılar S2 mikro katmanındaki 1.223 epizotla karıştırılamaz.

## 3. Gerçek kronolojik araştırma tahminleri

| Ufuk (tam işlem seansı) | Skorlanabilen | Bitiş etiketi | Devam etiketi | S2 Brier | Yalnız tamamlanmış geçmiş süre Brier | S2 kabul |
|---|---:|---:|---:|---:|---:|---|
| 1 seans | 24 | 1 | 23 | 0,050526 | **0,047538** | Başarısız / yetersiz kanıt |
| 3 seans | 21 | 3 | 18 | **0,139235** | 0,141383 | Yetersiz kanıt |
| 5 seans (~1 hafta) | 17 | 5 | 12 | 0,214835 | **0,214398** | Yetersiz kanıt |
| 10 seans (~2 hafta) | 9 | 5 | 4 | 0,272305 | **0,248663** | Başarısız / yetersiz kanıt |

Teknik olarak her ufukta artık **hem END hem CONTINUE vardır**; eski 4s mikro katmandan farklı ve önemli veri-ölçeği ilerlemesi. Ancak modelin olgun karşılaştırılabilir tahminlerinin tümü **2025'te** geldi (süre hafızası ancak o zaman minReady=8 destek sınırına ulaştı); geçerli tahmin sayıları 9–24 arasında. Her ufuk için END ve CONTINUE bağımsız etiket destekleri ayrı ayrı ≥12 olmalıydı: **hiçbiri karşılamıyor** (`estimable=false`). Epizot-kümeli %95 belirsizlik aralığı için de yalnızca 2–5 farklı epizot kümesi var; güvenilir CI **üretilemedi**. 2025 verileri 2026'da retrospektif incelenmiş olduğundan kör bağımsız OOS değildir.

**Şimdiki bilimsel karar:** Uzun ölçekli gerçek epizotlar ilk kez modellendi, fakat onlardan öğrenilen tehlike/bitiş riskinin fiyat yalnız baseline'a karşı sağlam üstünlüğü **kanıtlanmadı**. S2 bilimsel kapısı PENDING. Bu sonuçlardan net komisyon sonrası kâr, al/sat yetkisi, güvenilir ekonomik nedensellik veya gerçek canlı alpha çıkarılamaz.

## 4. Kod ve doğrulama
- [adaptive_slow_lifecycle_s2.js](adaptive_slow_lifecycle_s2.js): uzun seans epizotları, her ufuk için gerçek END/CONTINUE, bilinmeyeni sansürleme, duration hazard hafızası, küçük-küme çekimserliği.
- [adaptive_market_core_s1_s2.js](adaptive_market_core_s1_s2.js): **tek kompozit CORE**; geç ulaşan günlük bilgiyi önceki M15 kararına taşımaz, farklı veri kaynaklarını birleştirmez. Checkpoint sürümü değişti; eski kayıt sessizce kabul edilmez.
- [S2_SLOW_SESSION_AGGREGATE_2023_2025.sql](S2_SLOW_SESSION_AGGREGATE_2023_2025.sql) ve [replay_slow_lifecycle_s2.js](replay_slow_lifecycle_s2.js): özel fiyatlı veri yalnız geçici, GitHub çıktısı yalnız toplu araştırma özeti.
- [adaptive_slow_lifecycle_s2.test.js](adaptive_slow_lifecycle_s2.test.js): 9 test (cuma→pazartesi açık takvim, hafta içi eksik sansür, terminal bar kalite, trend 5+ seans, as-of M15 geçişi, iki source, tek checkpoint).
- **Önceki 58 + yeni 9 = 67/67** test izole JS harnessinde PASS. GitHub Actions workflow yeni S2 slow testini içerir fakat Actions sunucu koşusunun sonucu ayrıca teyit edilmedi.

**Mühendislik kabulü:** günlük/haftalık çalışan ilk araştırma sensörü + birleşik model **PASS**. **Bilimsel kabul:** `S2_LONG_HORIZON_SCIENCE=NOT_PROVEN`, `S1_SCIENCE=FAIL`. **S3 AL–TUT–SAT/2023 tam strict replay/U1** bu çalışmadan otomatik açılmaz.

**Sonraki pratik engel:** kaliteli, kesintisiz uzun yıllar / bağımsız bitmiş uzun epizotlar. Bu giderilmeden aynı 2025 veri setinde minReady düşürüp sonuç aramak yanlış iyileştirme olur. S2 slow hazard, gerçek S3'e ancak bilimsel ablation ve risk denetimiyle aday özellik olarak geçebilir.
