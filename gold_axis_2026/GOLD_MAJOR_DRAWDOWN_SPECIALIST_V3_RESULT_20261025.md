# LARGE DRAWDOWN SPECIALIST V3 — 2026-10-25
**Görev:** BÜYÜK DÜŞÜŞÜ önceden tespit et, klasik XAU UP/DOWN tahmini yapma. AURORA'nın expert contradiction & fast-entry/slow-exit ilhamı, H3 tahminlerinin geçmiş başarı yüzdeleri değil.

## Kapsam
Research sources 2010–2026 dört metal günlük / CBOE GVZ / FRB Broad USD H10 / DGS10 H15 / CFTC COMEX GC 088691 ve SI 084691. CFTC yıllık 2023–2026 resmî 398 tarihli satır; 2025 shutdown gerçek yayın gecikmeleri as-of; normal dönem yedi gün tutucu araştırma vekili. 27 Şubat 2026 hatalı fiyat ve etkilenen hedef/özellik pencereleri dışarıda. GLD ilk yayın saati belirsiz; CME, SLV eksik; hiçbiri uydurulup modele eklenmedi.

## Yöntem — yanlış alarmı gizlemeden
6 aday sabit: (1) **ANOMALY_BASE21** frozen 21 input IsolationForest, (2) EXHAUSTION RSI/aşırı alım/crowding, (3) RUPTURE GVZ+spread+crowding/metal ayrışması, (4) AURORA_CONTRADICTION trend güçlü iken kırılma korkusu uzmanları, (5) LOGIT_SPARSE_5D regularized class-balanced Logistic 8 selected features, (6) LOGIT_ALL21_5D. Bu altı aday yeni araştırma fikri olarak retrospektif çalışıldı; 2026 olayı daha önceden bilindiği için model fikri yönünden tam kör test değil.

**Train/selection:** 2023–24 fit -> 2025 model seçimi yalnız 2025 bağımsız beş işlem gününde >=%5 kayıp risk dönemleri ve yanlış alarm önceliğiyle. 2023–25 refit -> 2026 stres, 2026 hedef etiketine dayalı eşik seçimi yok. Her aday kırmızı sinyali yalnız kendi fit skorunun en üst %5'inde; 2025 eşik seçimi 2026 sonucuna göre yapılmadı. Supervised modellerde 2024 yalnız iki birbirine bağımlı next5-%5 orijini vardır, dolayısıyla prob çöküşü öğrenimi güvenilir değil.

## Sonuç: BEKLENDİĞİNDEN ZOR
| Aday | 2025 5d-%5 risk kümesi yakalama | 2025 kırmızı alarm günü | 2026 5d-%5 risk kümesi yakalama | 2026 kırmızı alarm günü |
|---|---|---:|---|---:|
| **ANOMALY_BASE21** | **3/3** | 31 | **2/4** | 29 |
| EXHAUSTION | 1/3 | 24 | 1/4 | 12 |
| RUPTURE | 0/3 | 11 | 0/4 | 18 |
| AURORA_CONTRADICTION | 1/3 | 27 | 1/4 | 12 |
| LOGIT_SPARSE_5D | 0/3 | 11 | 2/4 | 22 |
| LOGIT_ALL21_5D | 1/3 | 46 | 1/4 | 27 |

2026'da 5d büyük düşüş risk kökleri: Jan26–Jan30 **YAKALANDI**, Jun3–Jun5 **KAÇTI**, Jun17–18 **KAÇTI**, Aug25–27 **YAKALANDI**. Dönemler **birbirine yakın ileriye dönük risk orijinlerinin kümeleri**dir; gerçekleşen ilk fiyat düşüş günleriyle aynı anlama gelmez. Günlük >=%3 şok epizotlarında 2025 3/3, 2026 2/2; günlük >=%4 bağımsız epizotlarında 2025 1/1 ve 2026 Ocak–Şubat 1/1; aşırı az sayıda olay vardır.

Önceki başarı raporlarındaki 2026'daki 13 adet "5g düşüş" **13 ayrı olay değil, 4 risk epizoduna bağlı örtüşen origin etiketleri**dir. 21 özellikli modelin 6/13 origin hit'i yalnız 2/4 epizodu temsil eder. Üç aday ve iki lojistik uzman daha iyi bir OOS sonuç göstermedi; V3 bir bilimsel üstünlük zaferi değildir.

### AURORA'dan doğrulanabilir ürün iyileştirmesi
Hızlı giriş, yavaş çıkış: RED olduğunda **OPEN**, devam günlerinde **KEEP**, üç ardışık normal gün sonrası **CLOSE**. Yalnız geçmiş as-of risk işaretlerini kullanır, hedef fiyat/sonuç kullanmaz. Eski modelde 2025 31 günlük kırmızı işaret -> 5 tek seferlik uyarı başlangıcı; 2026 29 kırmızı -> **6** risk-dönemi açılışı. Bu, modelin doğru olma olasılığını artırmaz; uyarı spam'ini azaltır.

**MODEL KARARI:** 2025'e göre seçilmiş ANOMALY_BASE21 araştırma champion kalır; 2026 Haziran iki beş günlük düşüş dönemi kaçtı. GLD zaman damgası/CME/SLV ve ekonomik ilk olay-haber kronolojisi olmadan 2026 başarısını geriye dönük parametre ayarıyla 'düzeltmek' metodolojik hata olur. Kullanım: sadece araştırma. ANN fiyat tahminleri/Neon/üretim uygulaması değişmedi. GitHub otomatik iş akışları tekrar açılmadı.
