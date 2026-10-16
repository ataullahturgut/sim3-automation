# GOLD-ADAPTIVE-MODEL-APP-01 — Ocak 2023 neden altın alınmadı? (16 Ekim 2026)
**Çalışma:** MODEL / S3 başarısızlık incelemesi · **durum:** neden doğrulandı, kâr/AL-SAT bilimsel kabulü YOK · **branch:** aynı araştırma dalı.

## 1. Tam olarak hangi veri ve bankacılık protokolü?
Kaynak: Neon `gold_research_evduka_xau15m_bidask_candidate`, tek `EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1` kaynağı; 2023 Ocak bar başlangıçlarında 1.920 M15 fiyatı. Tarihsel 2026-10-08 kurtarma; canlı PIT değil, banka kotasyonu değildir.
Bankanın varsayılan komisyon modeli: her alış **%0,8**, her satış **%0,8**. Al+sat `(1−0,008)^2=0,984064` sermaye çarpanı; fiyatın bir gidiş-dönüşü zararsız karşılaması için **%1,6194069** artış gerekir.
Banka işlemi saati kullanıcı protokolü: `Europe/Istanbul 09:00–17:00` (Ocak 2023'te UTC+3). Sadece `06:15Z–14:00Z` as-of tamamlanmış 15dk araştırma fiyatı seçildi; gerçek bankanın ilgili dakikada kotasyon verdiği **kanıtlı değil**. Tamamlama anı için yürüyüşte aynı kapanışa otomatik emir verilen varsayım henüz execution-certified değildir.

## 2. Geçmişi gören tek alış/tek satış kıyaslamaları — YATIRIM KARARI DEĞİLDİR
100 USD, başlangıç nakit; MID referans, iki banka maliyeti dahildir. Bu sonuçlar **hindsight upper bound** ve sabit senaryodur, o tarihte bilinen sinyaller değildir.

| Senaryo | Alım (TRT) | Çıkış (TRT) | 100 USD sonu |
|---|---|---|---:|
| Nakit pasif | — | — | **100,00** |
| İlk uygun seans sabahı al/tut | 3 Ocak 09:15 | 31 Ocak 17:00 | **102,5368** |
| 6 Ocak ABD istihdam açıklaması sonrasını varsayımsal giriş kabul et | 6 Ocak 16:45 | 31 Ocak 17:00 | **102,2352** |
| Aynı varsayımsal girişten 26 Ocak yerel yüksekliğinde çık | 6 Ocak 16:45 | 26 Ocak 09:15 | **103,7785** |
| İleri fiyatlar bilinerek tek en iyi alış/satış | 3 Ocak 14:45 | 26 Ocak 09:15 | **104,7155** |
| 12 Ocak CPI sonrasında al/tut | 12 Ocak 16:45 | 31 Ocak 17:00 | **99,8463** |

**Önemli:** 26 Ocak çıkışının fiyat zirvesi olduğu 6 Ocak'ta bilinemezdi. `104,7155` bir optimum kıyas çizgisidir, modelin yakaladığı işlem değildir. 6 Ocak istihdam raporu 08:30 EST = 13:30 UTC = 16:30 TRT; 12 Ocak CPI aynı resmî saat. Resmî ilk yayın arşivleri: https://www.bls.gov/news.release/archives/empsit_01062023.htm ve https://www.bls.gov/news.release/archives/cpi_01122023.htm. Ekonomik verinin **ilk olarak sistemimize ulaştığı timestamp yok**; açıklamaların ekonomik nedenselliğini kanıtlanmış model özelliği saymayız.

**Eski 103,8057 $ pasif GOLD sayısı ile fark:** Önceki S3 smoke `bar_start < 2023-02-01 UTC` filtresiyle, **2 Şubat değil, 1 Şubat 00:00 UTC'de tamamlanan son fiyatı** ve 2 Ocak 23:15 UTC ilk tamamlanmış fiyatı kullanıyordu. Bu sınır `Ocak Türkiye banka saatleri` sınırı değildir. Katı Ocak karşılaştırması için as-of `3 Ocak 00:00 UTC→31 Ocak 22:00 UTC` tam gün araştırmasında pasif GOLD **103,7278 $**; `09:00–17:00 TRT` fiyatlarında ilk sabah giriş/son gün çıkış **102,5368 $**. Bunlar farklı zaman aralıklarıdır, aynı örnek küme iddia edilemez.

## 3. Orijinal S3 neden hiç işlem yapmadı? — SAYISAL KÖK NEDEN
Orijinal tek CORE Ocak replay: **1.920 fiyat / 1.898 tek-bar gecikmeli Q güncellemesi / 21 kaynak veya günlük zaman boşluğu / 46 karşılaştırılabilir karar / 1.874 çekimser / 0 BUY / 100 USD CASH**.
- **1.768** karar `slow=WARMUP` durumunun `UNREADY` sınıfına dönüşerek hard-gate koyması nedeniyle doğrudan bloke. İstikamet eksik günlük sensör saatlik sinyali de veto etmişti.
- Ocak 2023 slow ayrı başlatıldığı için yalnız **20 kabul edilmiş gün** ve **0 tamamlanmış uzun epizot** vardı. Günlerce süren epizot bilgisi S3'te olgun yavaş destekli karar olarak erişilebilir değildi.
- İlk gerçek değerlendirme **17 Ocak 04:00 UTC**; toplam 46 değerlendirme (17 Ocak). **46/46 KEEP**, nakit iken `Q(CASH,SWITCH)-Q(CASH,KEEP)` yaklaşık **−0,009566 ile −0,006956 log-servet**. Buy tarafı bir kerelik %0,8 fiyat maliyetini öğreniyor; S3 kredi ataması **tek 15dk getiri** üzerinden gerçekleşiyor.
- `gamma=0,998` 15 dakikalık bir adıma uygulanıyor; 5×92 bar (yaklaşık 5 işlem seansı) ufkunda iskonto `0,998^460≈0,398`, 10×92 barda `≈0,159`. Uzun yükseliş fırsatı karar değerinde aşırı küçülüyor. Bu matematiksel neden, büyük zaman ölçeği için yalnız `minUpdates` düşürmenin çözüm olmayacağını gösteriyor.
- 21 eksik zaman aralığındaki fiyat değişimleri 15dk Q güncellemelerine alınmıyor. Ocak kapsamında tüm barlar üzerinden log-fiyat artışı yaklaşık **%5,3415**, kesintisiz 15dk çiftlerden yaklaşık **%5,1618**, aralıktaki toplam yaklaşık **%0,1797** log puan. Eksik aralık başlıca neden değil fakat tuttuğu altını gece de taşıyan politika için gelecekte muhasebe ayrımı gerekir.

## 4. Hata ayırıcı test ve fix
`adaptive_position_value_s3.js` ve `adaptive_market_core_s1_s2.js`: `slow.phase=WARMUP/REJECTED_SESSION/GAP` **NO_SLOW** olarak kodlanır; **fast WARMUP hâlâ hard-gate**. `minUpdates=32`, `fee=0,8%/leg`, model ve strict PIT kapısı **değişmedi**. `decisionsByReason` ile kaç kararın hangi nedenle verilemediği kayda alınır.
Düzeltme sonrası **aynı 1.920 gerçek M15 yeniden replay**:
- **1.384** karşılaştırılabilir karar (ilk **4 Ocak 03:45 UTC**);
- **536** çekimser: 22 eksik bar/gap, 318 fast hazır değil, 196 eylem değeri destek yetersiz;
- **1.384/1.384 KEEP, sıfır BUY**, son nakit **100 USD**. Teknik kapsam artmış, kârlılık artmamıştır.
- Örnek karar anları: **6 Ocak 13:45 UTC** fast NEUTRAL, slow WARMUP, `KEEP`, Q switch−keep yaklaşık −0,007603; **12 Ocak 13:45 UTC** fast CONTINUE, slow WARMUP, `KEEP`, marj yaklaşık −0,008048. **6 Ocak haberinden sonra bile** tek-bar değer fonksiyonu maliyeti yenememiştir.
- GitHub Actions sentetik testleri PASS; bu, gerçek piyasa alpha doğrulaması değildir.

## 5. Sıradaki geçerli MODEL geliştirmesi
Yeni ANN/ayrı strateji/branch yaratmadan **aynı S3 içinde** 5/10 işlem seanslık gecikmeli ödül ve pozisyon değeri için ek `Q_h(state,CASH/GOLD,KEEP/SWITCH)` ölçüleri oluşturulmalı. Sonuç yalnız **h ufku tamamlandıktan ve kaynak sürekliliği teyit edildikten sonra** güncellenmeli; kaynak/tatil/gap kesintisi varsa outcome sansürlenmeli. 2020–2022 (yalnız 2023'ten önce gerçekten kapanmış) aynı fiyat kaynağı eğitim/warmup; 2023 Ocak başlangıç sermayesi sıfır altınla **100 USD**; 2023 olayları veya sonraki fiyatları kural kurmak için kullanılmamalı. Ardından bankanın %0,8+%0,8 farkı, pasif nakit/altın, turnover, drawdown ve missed-opportunity ölçülmeli. Hindsight optimum ile gerçek *as-of* karar yan yana ama farklı etiketle raporlanmalı.

**Bilim kapısı:** MODEL_GATE=FAIL · S1_SCIENCE=FAIL · S2_SCIENCE=PENDING · S3_SCIENCE=NOT_PROVEN · STRICT_S4_NOT_DONE · U1_UNCHANGED.
