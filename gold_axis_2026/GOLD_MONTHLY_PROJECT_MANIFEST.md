# GOLD MONTHLY FORECAST — CANONICAL PROJECT MANIFEST

**Manifest version:** 1.3  
**Date:** 2026-09-28  
**Repository:** `ataullahturgut/sim3-automation`  
**Branch:** `gold-midas-headswap-v1-20260925`  
**Canonical path:** `gold_axis_2026/GOLD_MONTHLY_PROJECT_MANIFEST.md`  
**Status:** **CURRENT / BINDING / SELF-CONTAINED PROJECT STATE**

> **Single-source rule:** Bu dosya GOLD MONTHLY FORECAST projesini anlamak, daha önce neyin denendiğini görmek, hangi sonuçların elde edildiğini bilmek ve sıradaki işi belirlemek için yeterli olmalıdır. Eski ledger, result, freeze ve Challenger-B dosyaları yalnızca denetim/provenance kanıtıdır; mevcut proje durumunu anlamak için onlara gitmek gerekmez.

---

# 1. Projenin amacı ve değişmeyen kontrat

## 1.1 Hedef

Proje, bir sonraki takvim ayının ortalama **XAU/USD** fiyatını tahmin eder.

- Hedef ufuk: **H=1 ay**
- Forecast origin: önceki tamamlanmış takvim ayının sonu
- Ana modelleme hedefi: çoğu CURRENT8/neural/nonlinear hatta bir sonraki ay Gold log-return
- Fiyat rekonstrüksiyonu: önceki tamamlanmış ay ortalaması × exp(tahmin edilen log-return)

## 1.2 Seçim ve değerlendirme otoritesi

- DEV / model seçimi: **2022-04..2024-12, n=33**
- 2025: kilitli transport/final-holdout rolü; family freeze sonrasında kullanılabilir, geriye dönük tuning için kullanılamaz
- 2026: karantina / reporting-only
- Random split: **YOK**
- Chronological rolling/expanding origin: **ZORUNLU**
- Target-month leakage: **YASAK**
- DB: **READ_ONLY**
- Ana skor: **DEV ΣAE = aylık mutlak fiyat hatalarının toplamı**
- İkinci ana kriter: **aylık yön doğruluğu**
- Destek metrikleri: MAE, RMSE, MAPE/WAPE, RW-relative MAE, worst month, yearly stability

## 1.3 Mevcut veri çalıştırma altyapısı

Yetkilendirilmiş DEV Snapshot V1:
- schema: `GOLD_MONTHLY_DEV_SNAPSHOT_V1_2026-09-28`
- payload SHA-256: `2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb`
- 2025 modeling rows: **0**
- 2026 modeling rows: **0**
- offline CNN-LSTM parity: **tam eşleşme / fark 0.0**

Yeni uyumlu DEV modelleri, tekrar tekrar Neon’a bağlanmak yerine bu snapshot’ı kullanmalıdır. Neon veri otoritesi olarak kalır; snapshot yalnız immutable execution cache’dir.

Snapshot execution identity:
- source workflow run: `36456042954`
- snapshot artifact id: `10985453248`
- artifact name: `gold-monthly-dev-snapshot-v1-be98365d25e2e81b0f70fb724940e09d0191eb6c`
- loader: `gold_axis_2026/tools/gold_monthly_dev_snapshot_v1.py`
- parity result: CNN-LSTM canonical parent için aggregate/yearly SigmaAE ve direction farkı **0**
- artifact expire olursa: aynı governed schema ile yeniden export + parity yapılmadan kullanılmaz

## 1.4 Proje sözlüğü ve veri representation’ları

### Main path / Challenger A
Bu manifestte "main path" veya geçmiş konuşmalardaki "Challenger A", tek bir model adı değildir. ELM→ANN→ELMFIS→ANFIS→RBFNN→GPR→DMA/Boosting/SVR/CNN-LSTM boyunca gelişen ana Gold Monthly research hattını ifade eder.

### Challenger B
Grup-ARGE’de daha önce kullanılan seçili klasik/ileri modellerin Gold Monthly governance altında paralel portudur. Ana hattı değiştirmez; sonuçları artık bu manifestin aynı cross-family havuzundadır.

### CURRENT8
Dört metal için ikişer origin-safe predictor:
- Gold: MR + VW
- Silver: MR + VW
- Platinum: MR + VW
- Palladium: MR + VW

Tanımlar:
- **MR:** önceki tamamlanmış ayın log-return’u.
- **VW:** forecast origin ayında mevcut günlük verilerden, official point-in-time GPR vintage ile causal ağırlıklandırılmış günlük log-return özeti.
- GPR kullanımı exact-origin PIT vintage / publication-lag / causal normalization kurallarına tabidir.

Toplam boyut = **8**.

### DAILY_SUMMARY12
Her metal için forecast-origin ayının günlük seviyelerinden üç causal özet:
1. open-to-close log change,
2. realized-volatility özeti = sqrt(sum of squared daily log returns),
3. log range = log(max/min).

4 metal × 3 = **12 predictor**.

### RAW_LEVEL_LAGS8
Her metal için son iki tamamlanmış aylık seviye:
4 × 2 = **8 predictor**.

### SIMPLE_RETURNS8
Her metal için:
- 1-month log return
- 3-month log return

4 × 2 = **8 predictor**.

### MIXED20
- CURRENT8 = 8
- dört metal current monthly level = 4
- dört metal 3-month momentum = 4
- dört metal realized-volatility summary = 4

Toplam = **20**.

### Raw monthly 4-metal sequence
TimesFM-3 / TimeMixer++ / TimeXer gibi modern sequence hatlarında Gold, Silver, Platinum ve Palladium’un tamamlanmış aylık seviyeleri kullanılır. Bu hatlar CURRENT8 ile aynı representation değildir.

## 1.5 Metric authority ve supersession

Projenin erken ELM/ANN aşamalarında birçok screen **MAPE-merkezli** raporlandı. Bu tarihsel tablolar silinmez; fakat aktif seçim otoritesi değildir.

2026-09-26 cross-family re-audit sonrası bağlayıcı aktif değerlendirme:
1. DEV cumulative price error **ΣAE**
2. DEV monthly direction
3. diğer metrikler supporting/diagnostic

Sonuç:
- eski MAPE-merkezli "final winner" ifadeleri tarihsel/superseded olabilir;
- aynı model için aktif karar aranırken bu manifestteki ΣAE + direction kayıtları kullanılır;
- MAPE yalnız destekleyici olarak kalır.

## 1.6 2025 / 2026 bilgi durumu — önemli nüans

**2025 tüm proje için artık tamamen görülmemiş bir global blind holdout değildir.** Bazı tamamlanmış eski ailelerde 2025 report-only/transport olarak daha önce hesaplanmıştır; Boosting’de family freeze sonrasında one-shot olarak açılmıştır; Challenger B’de de report-only sonuçlar vardır.

Bağlayıcı kural:
- 2025 hiçbir mevcut sonucu geriye dönük tune/promote/rescue etmek için kullanılamaz.
- Bir family kendi protocolünde 2025’i henüz açmadıysa o family için kilitli kalır.
- **CNN/LSTM aktif family için 2025 hâlâ açılmamıştır.**
- SVR family için 2025 family freeze öncesinde açılmayacaktır.
- 2026 yalnız retrospective/quarantine evidence’dir; seçim otoritesi değildir.

Bu yüzden gelecekte "2025 blind holdout" ifadesi family-specific kullanılmalıdır; global proje için koşulsuz söylenmemelidir.

## 1.7 Yeni sohbet onboarding protokolü

Yeni bir sohbet bu projeyi devralırken yalnız şu sırayı izlemelidir:

1. Önce **yalnız bu manifesti** oku.
2. Bu dosyadaki current status / closed paths / next action satırlarını bağlayıcı kabul et.
3. Yeni model önermeden önce Section 4 ve family bölümlerinde duplicate kontrolü yap.
4. Ayrıntılı run/job/artifact doğrulaması gerekiyorsa ancak o zaman Section 22 provenance dosyalarına git.
5. Eski dosyalardaki "next action" satırlarını bu manifestten daha yeni otorite sayma.
6. Current checkpoint: **BiLSTM tamamlandı ve promote edilmedi; CNN-BiLSTM henüz çalıştırılmadı.**

Ayrı proje uyarısı:
- `GOLD_CONTROL_PROJECT_MANIFEST.md` = Gold **Direction Engine**
- bu dosya = Gold **Monthly Price Forecast**
- iki proje birbirinin model registry’si değildir.

---

# 2. Bugünkü durum — tek bakışta

## 2.1 Güncel Pareto çekirdeği

Aktif DEV ΣAE + direction kontratı altında en önemli mevcut referanslar:

| Model | Aile | DEV ΣAE | Direction | Rol |
|---|---|---:|---:|---|
| **ChHHO-ANFIS** | ANFIS | **1413.0298** | 23/33 | fiyat anchor |
| **DE-ABC-RBFNN** | RBFNN | **1415.8371** | **25/33** | güçlü Pareto model |
| **PLS1 V1 All-4** | Challenger B | **1420.0291** | 20/33 | Challenger-B fiyat lideri |
| **LMC2_RBF_M32** | GPR/MOGP | **1424.1711** | 19/33 | güçlü GPR benchmark |
| FULL7 ANN | ANN ensemble | 1428.8590 | 22/33 | benchmark |
| REDUCED4 ANN | ANN ensemble | 1431.4587 | 24/33 | dengeli Pareto |
| EPSILON_RBF_DAILY12 | SVR | 1449.1874 | 19/33 | SVR family leader |
| CATBOOST_PRICE | Boosting | 1460.4339 | 20/33 | Boosting price leader |

Bu tablo istatistiksel evrensel üstünlük iddiası değildir; DEV n=33’tür.

## 2.2 Aktif açık iş

**Şu an sıradaki model: CNN-BiLSTM.**

Mevcut CNN/LSTM family leader:
- CNN-LSTM
- lookback 6
- width 32
- dropout 0.10
- Adam LR 0.001
- DEV ΣAE **1528.569850656**
- direction **20/33**

BiLSTM:
- DEV ΣAE **1638.096795007**
- direction **19/33**
- scientific gate PASS
- **NOT PROMOTED**
- rescue tuning kapalı

CNN-BiLSTM henüz çalıştırılmadı.

## 2.3 Açık / kapalı aile özeti

| Aile | Durum | Tekrar nereden açılır? |
|---|---|---|
| ELM | COMPLETE_CLOSED | yalnız yeni yapısal gerekçe |
| ANN | COMPLETE_CLOSED | broad screen tekrarlanmaz |
| ELMFIS | COMPLETE_CLOSED | yalnız yeni yapısal gerekçe |
| ANFIS | COMPLETE_CLOSED | explicit reopen olmadan açılmaz |
| RBFNN | COMPLETE_CLOSED | broad/refinement tekrar yok |
| GPR/MOGP | Stage 3 complete, final closure eksik | frozen Stage-4 pool’dan |
| Boosting | COMPLETE_CLOSED | yeni mekanizma olmadan açılmaz |
| SVR/DWT-SVR | PAUSED | Stage 5A.3 DE-tuned PSO-SVR |
| DMA/DMS/IDMA | DEFERRED_REVISIT_LAST | daha geniş PIT predictor panel ile |
| Challenger B | COMPLETE_CLOSED | yeni explicit scope ile |
| CNN/LSTM | ACTIVE | CNN-BiLSTM |
| Modern sequence/foundation | MIXED | TimeXer frozen-not-run; diğerleri aşağıda |

---

# 3. Araştırma akışı — tarihsel sıra

Bu bölüm projenin neden bugünkü noktaya geldiğini tek akışta gösterir.

## 2026-09-25 — ELM → ANN → ELMFIS

İlk geniş optimizer araştırma hattı ELM’de kuruldu. Ardından aynı parity mantığı ANN’e ve ELMFIS’e taşındı. Bu dönemde ortak metaheuristic havuz, mandatory refinement ve kontrollü ensemble yaklaşımı şekillendi.

Ana sonuçlar:
- AOA-ELM güçlü ELM fiyat benchmark’ı oldu.
- ANN’de FULL7 ve REDUCED4 equal-weight ensemble’lar oluştu.
- ELMFIS fiyat lideri ABC, direction specialist’i SMA oldu.
- optimizer’ı tekrar tekrar değiştirmek tek başına kalıcı iyileşme sağlamadığı için daha yapısal ailelere geçildi.

## 2026-09-26 — ANFIS → RBFNN → GPR

ANFIS’te geniş metaheuristic screen sonrası ChHHO-ANFIS güçlü fiyat modeli olarak öne çıktı. RBFNN’de DE-ABC hem fiyat hem yön açısından güçlü Pareto sonuç verdi. GPR/MOGP’de LMC2_RBF_M32 Stage-3 lideri oldu.

Bu aşamadan sonra proje “aynı optimizer’ı başka base learner üzerinde yüzlerce kez dönme” yaklaşımından uzaklaştırıldı ve yapısal farklılık aranmaya başlandı.

## 2026-09-27 — DMA/DMS/IDMA → Boosting

DMA/DMS/IDMA canonical 256-subset Gold-only olarak düzeltildi. Sonuçlar kötü değildi fakat daha geniş macro-financial predictor setine ihtiyaç olduğu anlaşıldı; aile “revisit last” olarak park edildi.

Boosting hattında CatBoost, GBRT, LightGBM, XGBoost, metaheuristics, decomposition, ensemble ve robustness tamamlandı. Family kapandı.

## 2026-09-28 — SVR → Challenger B → modern sequence → CNN/LSTM

SVR’de canonical/deterministic/metaheuristic hat büyük ölçüde tamamlandı fakat DWT/MODWT yapısal hattına geçmeden family bilinçli olarak pause edildi.

Paralel Challenger-B hattında Grup-ARGE’de daha önce kullanılan klasik/ileri modeller Gold Monthly kontratına taşındı. PLS1 güçlü sonuç verdi.

Daha sonra TimesFM-3, TimeMixer++ gibi modern sequence/foundation modelleri test edildi. Ardından CNN/LSTM ailesine geçildi. Local micro-tuning stop-rule tetiklenince yapısal challenger aşamasına geçildi. BiLSTM başarısız oldu; sıradaki yapı CNN-BiLSTM oldu.

---

# 4. Ortak optimizer / metaheuristic havuzu — daha önce denendi

Aşağıdaki optimizer isimleri proje boyunca ELM, ANN, ELMFIS, ANFIS, RBFNN, GPR ve büyük ölçüde SVR’de zaten denenmiştir. Başka bir base architecture üzerinde kullanılması mümkün olabilir; fakat bunlar artık “yeni keşfedilmiş yöntem” değildir.

1. Vanilla
2. PSO
3. GA
4. DE
5. MPA
6. ABC
7. SSA
8. GWO
9. WOA
10. HHO
11. ACO
12. Bat
13. FA
14. MFO
15. FPA
16. FA-FPA
17. CS / Cuckoo Search
18. SCA
19. Salp
20. SMA
21. GOA
22. ALO
23. TLBO
24. JAYA
25. HGS
26. ChOA
27. HGSO
28. AOA
29. CPA
30. Krill Herd
31. Crow Search
32. DE-ABC
33. Multi-swarm

Ayrıca birçok ailede şu refinement/hybrid sınıfları da denenmiştir:
- Adaptive PSO
- Adaptive TLBO
- TLBO-tuned PSO
- DE-tuned PSO
- Adaptive Crow
- PSO-TLBO hybrid
- MPA+SCA
- MPA+GA
- MPA+CPA

Bunların başka bir mimaride kullanılması ancak o mimarinin kendi scientific rationale’ı ile yeni bir deney olarak açılabilir.

## 4.1 Duplicate-prevention family coverage matrix

| Family | Vanilla / base | Full common optimizer screen | Adaptive/meta refinements | Structural/literature-specific | Current state |
|---|---|---|---|---|---|
| ELM | YES | YES — 33 identities total | YES | no further structural line retained | CLOSED |
| ANN | YES | YES — 33 identities total | YES | ensemble/refinement program complete | CLOSED |
| ELMFIS | YES | YES — 33 identities total | YES | CQCSA | CLOSED |
| ANFIS | YES | YES — 32 meta + vanilla | YES | ChHHO, MVO | CLOSED |
| RBFNN | YES | YES — 32 meta + anchors | YES | MOLS | CLOSED |
| GPR/MOGP | YES | Stage-1 broad screen complete | YES | LMC2_RBF_M32 | Stage 3 complete; Stage 4 frozen |
| SVR | YES | 32/32 technically executed | partial Stage 5A | causal DWT/MODWT not yet run | PAUSED |
| Boosting | YES | architecture-specific, not common-32 parity | YES | CEEMDAN-XGB, VMD-XGB | CLOSED |
| CNN/LSTM | YES | common-32 meta screen intentionally NOT opened | local ablations closed | BiLSTM run; CNN-BiLSTM next | ACTIVE |
| Challenger B | model-specific | not applicable | model-specific | PLS metal ablation | CLOSED SCOPE |

Bu tablo "bir optimizer adı daha gördük, bunu da yeni model diye deneyelim" tekrarını önlemek içindir.

---

# 5. ELM ailesi

**Durum: COMPLETE_CLOSED**

## Denenen yapı

- Vanilla ELM
- 32 civarı geniş optimizer/metaheuristic ekranı
- Adaptive PSO-ELM
- TLBO-tuned PSO-ELM
- DE-tuned PSO-ELM
- Adaptive/Improved TLBO-ELM
- Adaptive Crow Search-ELM
- PSO-TLBO Hybrid ELM

## Aktif-metrik sonuçları

- **AOA-ELM:** 1474.1021 / 20/33 — price benchmark
- SCA-ELM: 1508.71 / 21/33
- PSO-TLBO Hybrid ELM: yaklaşık 1487.55 / 20/33
- TLBO-ELM: 1758.75 / 23/33 — direction benchmark
- Vanilla ELM: yaklaşık 1480.08 / 21/33

## Karar

- AOA-ELM korunur.
- arbitrary optimizer cross-product genişletmesi kapalıdır.
- ELM ancak yapısal olarak farklı yeni mekanizma ile yeniden açılır.

---

# 6. ANN ailesi

**Durum: COMPLETE_CLOSED / FROZEN**

## Broad screen

33/33 ANN kimliği tamamlandı:
- Vanilla ANN
- ortak optimizer parity setinin tamamı

## Refinement

Tamamlanan önemli refinement’lar:
- Adaptive PSO-ANN
- Adaptive TLBO-ANN
- TLBO-tuned PSO-ANN
- DE-tuned PSO-ANN
- Adaptive Crow Search-ANN
- PSO-TLBO Hybrid ANN
- MPA+SCA Hybrid ANN
- MPA+GA Hybrid ANN
- MPA+CPA fallback

## Frozen ensemble’lar

### FULL7 equal-weight
Bileşenler:
- Vanilla ANN
- MPA-ANN
- SCA-ANN
- DE-ABC-ANN
- Adaptive TLBO-ANN
- TLBO-tuned PSO-ANN
- MPA+SCA Hybrid ANN

DEV:
- ΣAE **1428.8590**
- direction **22/33**

### REDUCED4 equal-weight
Bileşenler:
- Vanilla ANN
- MPA-ANN
- SCA-ANN
- DE-ABC-ANN

DEV:
- ΣAE **1431.4587**
- direction **24/33**

Diğer referans:
- MPA-ANN: yaklaşık **1471.53 / 19/33**

## Karar

- FULL7 benchmark.
- REDUCED4 dengeli Pareto challenger.
- full broad ANN screen tekrar edilmeyecek.
- post-hoc subset fishing kapalı.

---

# 7. ELMFIS ailesi

**Durum: COMPLETE_CLOSED**

## Denenen kapsam

- Vanilla ELMFIS
- 33-entry optimizer parity screen
- mandatory adaptive/meta-on-meta refinements
- MPA temelli hybrid’ler
- CQCSA-ELMFIS literature-specific model

## Sonuçlar

- Vanilla ELMFIS: **1996.2933 / 20/33**
- **ABC-ELMFIS: 1524.89 / 21/33** — price benchmark
- **SMA-ELMFIS: 1651.4482 / 25/33** — direction specialist
- CQCSA-ELMFIS: **1731.94 / 20/33** — not promoted

## Karar

- ABC internal price benchmark.
- SMA auxiliary direction/confirmation specialist.
- hard SMA override promote edilmedi.
- CQCSA Pareto noktası eklemedi.
- broad optimizer program tekrar edilmeyecek.

---

# 8. ANFIS ailesi

**Durum: COMPLETE_CLOSED**

## Vanilla anchor
- Vanilla ANFIS: **1852.0465 / 21/33**

## Broad screen
- 32/32 metaheuristic ANFIS denendi.
- 27 scientific gate PASS.
- ABC, WOA, FPA, HGS, AOA en az bir origin’de patolojik forecast büyüklüğü nedeniyle scientific reject.

Stage-2 valid benchmarks:
- MFO-ANFIS: **1630.3325 / 20/33**
- HHO-ANFIS: **1646.1336 / 23/33**

## Refinement
Valid fakat frontier geliştirmeyen:
- MPA-CPA: 1918.5637 / 18
- PSO-TLBO Hybrid: 3156.9979 / 19
- TLBO-tuned PSO: 3465.1623 / 20

Scientific-gate fail:
- Adaptive PSO
- Adaptive TLBO
- Adaptive Crow
- DE-tuned PSO
- MPA-SCA
- MPA-GA

## Literature-specific

### ChHHO-ANFIS
- DEV ΣAE **1413.029779**
- direction **23/33**
- rel.MAE/RW ≈ 0.80377
- current ANFIS champion

### MVO-ANFIS
İlk kod bug’ı düzeltildikten sonra valid rerun:
- DEV **2057.3973 / 17/33**
- not promoted

## Ensemble denetimi
Same-DEV optimized blend’ler diagnostik olarak iyi görünse de honest expanding-prequential weighting ChHHO’yu geçmedi.

## Karar
- ChHHO-ANFIS primary price anchor.
- ANFIS optimizer/stacking genişletmesi kapalı.

---

# 9. RBFNN ailesi

**Durum: COMPLETE_CLOSED / FROZEN**

## Denenen kapsam
- Vanilla RBFNN
- Regularized RBFNN
- 32/32 optimizer broad screen
- Adaptive PSO
- Adaptive TLBO
- TLBO-tuned PSO
- DE-tuned PSO
- Adaptive Crow
- PSO-TLBO
- MOLS-RBFNN
- controlled ensemble + shrinkage/prequential audit

## Sonuçlar
- **DE-ABC-RBFNN: 1415.8371 / 25/33**
- Adaptive Crow: 1455.8616 / 21
- PSO-TLBO: 1489.6671 / 21
- MOLS-RBFNN: 1578.5391 / 18
- FULL_MEDIAN ensemble: 1444.3008 / 22

## Karar
- DE-ABC family champion.
- global Pareto model.
- broad/refinement araştırması tekrar edilmeyecek.

---

# 10. GPR / MOGP ailesi

**Durum: STAGE 3 COMPLETE; FAMILY FINAL CLOSURE HENÜZ TAM DEĞİL**

## Tamamlananlar
- Stage 0 audited
- Stage 1 geniş screen
- Stage 2 parent freeze
- Stage 3A six refinements
- Stage 3B MPA-SCA
- Stage 3C LMC2_RBF_M32

## Stage-3 sonuçları

| Model | DEV ΣAE | Direction |
|---|---:|---:|
| **LMC2_RBF_M32** | **1424.1711** | 19/33 |
| MPA-SCA | 1709.2943 | 22/33 |
| Adaptive Crow | 1724.2888 | 19/33 |
| Adaptive TLBO | 1740.8877 | 19/33 |
| Adaptive PSO | 1794.2201 | 20/33 |
| PSO-TLBO | 1815.3287 | 21/33 |
| TLBO-tuned PSO | 1863.6677 | 19/33 |
| DE-tuned PSO | 1939.8588 | 16/33 |

## Karar
- LMC2_RBF_M32 retained benchmark.
- Stage 0-3 yeniden başlamaz.
- Repo’da Stage-4 pool freeze var.
- GPR yeniden açılırsa **Stage 4 frozen pool’dan** devam eder.

---

# 11. DMA / DMS / IDMA

**Durum: DEFERRED_REVISIT_LAST / REJECTED DEĞİL**

## Canonical düzeltme
Gold-only:
- 2^8 = 256 subset
- intercept dahil
- alpha=.99
- lambda=.99

## Sonuçlar
- Canonical DMA: **1486.2561 / 19/33**
- Canonical DMS: **1489.8247 / 20/33**
- 60m DMS: 1489.0965 / 19
- 84m DMS: 1497.7098 / 19
- **108m DMS: 1483.8794 / 20**
- 132m DMS: 1488.0163 / 20
- max-history DMS: 1489.8247 / 20
- exploratory IDMA MSFE selector: 1495.6721 / 20
- exploratory IDMA AE-price selector: 1495.5268 / 20

Fed + Nasdaq + USD/CNY küçük augmentation hattı aileyi kurtarmadı.

## Karar
Problem yalnız örneklem uzunluğu gibi görünmüyor. Literatürdeki geniş macro-financial predictor setiyle bizim CURRENT8 bilgi seti arasında fark var.

Reopen ancak:
- daha geniş origin-safe PIT macro-financial panel bulunursa, veya
- diğer yüksek öncelikli aileler bittikten sonra.

Küçük alpha/lambda/window oynamaları yapılmayacak.

---

# 12. Boosting / Trees ailesi

**Durum: COMPLETE_CLOSED**

## Denenen model hatları
- CatBoost PRICE
- CatBoost BALANCED
- GBRT
- LightGBM
- XGBoost direction component
- CatBoost metaheuristics: DE-ABC, PSO, MFO, HHO, TLBO
- CMA-ES–GBRT
- TPE/Optuna–GBRT
- causal CEEMDAN–XGB
- causal VMD–XGB
- median/equal/inverse-MAE ensemble
- expanding-prequential simplex
- shrinkage robustness
- 2025 one-shot final holdout

## Ana DEV sonuçları
- **CATBOOST_PRICE: 1460.4339 / 20/33**
- **FULL5_MEDIAN: 1484.7313 / 23/33**
- frozen GBRT: 1500.4295 / 22
- TPE-GBRT: 1576.9729 / 18
- CMA-ES-GBRT: 1650.1985 / 18
- CEEMDAN-XGB: 1820.4746 / 17
- VMD-XGB: 2019.0624 / 15

CatBoost metaheuristic finalistleri Vanilla CatBoost’u geçmedi.

## 2025 one-shot
Freeze sonrasında:
- CATBOOST_PRICE: 1020.6861 / 11/12
- FULL5_MEDIAN: 993.9803 / 11/12

2025 sonucu frozen rolleri geriye dönük değiştirmedi.

## Karar
- PRICE = CATBOOST_PRICE
- BALANCE/DIRECTION = FULL5_MEDIAN
- boosting family kapalı

---

# 13. SVR / DWT-SVR

**Durum: PAUSED — restart yok**

## Stage 1
- RBF CURRENT8: **1524.5006 / 21**
- Linear: 1535.1160 / 19

## Kernel ablation
- RBF: 1524.5006 / 21
- Linear: 1535.1160 / 19
- Poly2: 1793.2474 / 17
- Poly3: 1810.3496 / 17
- Sigmoid: 2784.3324 / 15

## Representation ablation
- **DAILY_SUMMARY12: 1449.1874 / 19**
- CURRENT8: 1518.8970 / 21
- MIXED20: 1579.3083 / 17
- RAW_LEVEL_LAGS8: 1800.4286 / 18
- SIMPLE_RETURNS8: 1850.5436 / 17

## Formulation
- epsilon-SVR: **1449.1874 / 19**
- NuSVR: 1525.4334 / 18

## Deterministic tuning
- coarse: 1580.9011 / 20
- local: 1592.5905 / 22
- ikisi de parent’ı geçmedi

## Metaheuristic broad screen
32/32 teknik execution tamamlandı.
Best authoritative metaheuristic:
- **ALO: 1494.8081 / 20**

FA:
- technical PASS 1583.8106 / 19
- fakat kullanıcı stop kararı nedeniyle authoritative ranking dışında tutuldu

## Stage 5 refinements
- Adaptive PSO-SVR: 1748.6557 / 16
- TLBO-tuned PSO-SVR: 1871.8062 / 17

## Exact resume point
SVR’ye dönülürse:
1. **DE-tuned PSO-SVR**
2. Adaptive/Improved TLBO-SVR
3. Adaptive Crow Search-SVR
4. PSO-TLBO Hybrid SVR
5. conditional Stage 5B
6. causal DWT/MODWT-SVR
7. controlled ensemble
8. robustness
9. family freeze
10. 2025 one-shot

Stage 1-4 tekrarlanmayacak.

---

# 14. Challenger B — Grup-ARGE modellerinin Gold Monthly portu

**Durum: USER-AUTHORIZED SCOPE COMPLETE**

Bu hat ana yolu bozmak için değil, Grup-ARGE’de daha önce kullanılan modelleri aynı Gold Monthly governance altında challenger olarak test etmek için açıldı.

## Representation

### CURRENT8 kullananlar
- Gold_MR, Gold_VW
- Silver_MR, Silver_VW
- Platinum_MR, Platinum_VW
- Palladium_MR, Palladium_VW

### Raw monthly Gold kullananlar
- ARIMA
- SARIMA
- Prophet

Bu modeller CURRENT8’e zorlanmadı; family logic korundu.

## Tüm Challenger-B DEV sonuçları

| Model | Input | DEV ΣAE | Direction | rel.MAE/RW | Karar |
|---|---|---:|---:|---:|---|
| **PLS1 V1** | CURRENT8 | **1420.0291** | 20/33 | 0.8078 | RETAIN |
| **PLS2 V1** | CURRENT8 multi-output | 1489.3300 | **23/33** | 0.8472 | RETAIN secondary |
| Ridge V1 | CURRENT8 | 1520.9926 | 21/33 | 0.8652 | NOT_PROMOTED |
| Huber V1 | CURRENT8 | 1530.1300 | 20/33 | 0.8704 | NOT_PROMOTED |
| Extra Trees V1 | CURRENT8 | 1539.9221 | 20/33 | 0.8760 | NOT_PROMOTED |
| Elastic Net V1 | CURRENT8 | 1590.3571 | 16/33 | 0.9046 | NOT_PROMOTED |
| GPReg-Matérn V1 | CURRENT8 | 1637.9165 | 19/33 | 0.9317 | NOT_PROMOTED |
| GPReg-RBF V1 | CURRENT8 | 1696.3365 | 16/33 | 0.9649 | NOT_PROMOTED |
| SARIMA | raw monthly Gold | 1751.5242 | 19/33 | 0.9963 | NOT_PROMOTED |
| ARIMA | raw monthly Gold | 1781.7822 | 15/33 | 1.0135 | NOT_PROMOTED |
| HGB V1 | CURRENT8 | 1840.2678 | 20/33 | 1.0468 | NOT_PROMOTED |
| Prophet | raw monthly Gold | 7521.1360 | 14/33 | 4.2782 | REJECTED |

## PLS1 metal ablation

All-4 tekrar üretildi ve reproduction gate PASS.

| Variant | Metals | DEV ΣAE | Direction |
|---|---|---:|---:|
| **ALL4** | Au+Ag+Pt+Pd | **1420.0291** | 20/33 |
| No Silver | Au+Pt+Pd | 1454.3225 | **22/33** |
| No Palladium | Au+Ag+Pt | 1461.6772 | 19/33 |
| Gold + Silver | Au+Ag | 1491.2346 | 20/33 |
| Gold only | Au | 1519.4727 | 21/33 |
| No Platinum | Au+Ag+Pd | 1519.6757 | 20/33 |

Karar:
- primary PLS1 representation = **4 metal**
- No-Silver yalnız direction-heavy trade-off reference

## Challenger B’de özellikle çalıştırılmayanlar

Bunlar yapılmış sayılmayacak:
- Seasonal Naive
- Drift
- Theta
- Optimized Theta
- SARIMAX_SAFE
- Dynamic Ridge
- exact Grup-ARGE Linear SVR port

Status: **NOT_RUN**

---

# 15. CNN / LSTM family

**Durum: ACTIVE**

## Stage 0 canonical
- LSTM LB12: 1738.0595 / 15
- CNN LB12: 1906.9426 / 13
- CNN-LSTM LB12: 1554.3082 / 18

## Stage 1A — lookback
- LSTM LB3: **1589.9827 / 19**
- CNN LB3: **1641.8275 / 21**
- CNN-LSTM LB6: **1528.5699 / 20**

Lookback meaningful improvement sağladı.

## Stage 1B — width
- LSTM W32 retained
- CNN W16 fiyat açısından çok küçük near-tie sağladı; W32 direction daha iyi
- CNN-LSTM W32 retained

## Stage 1C — dropout
- LSTM D0.10 retained
- CNN-LSTM D0.10 retained
- D0 ve D0.20 anlamlı üstünlük sağlamadı

## Stage 1D — learning rate
- LSTM LR .0003: 1648.5032 / 20
- CNN LR .0003: 1637.1770 / 21; yalnız ~0.264% local price win
- CNN-LSTM LR .0003: 1583.4676 / 18

Pre-frozen stop rule tetiklendi:
- batch sweep iptal
- kernel sweep iptal
- local Cartesian micro-tuning kapalı

## BiLSTM
Frozen:
- lookback 3
- Bidirectional LSTM 32+32
- dropout .10
- Adam .001

DEV:
- ΣAE **1638.0968**
- direction **19/33**
- rel.MAE/RW 0.9318
- scientific gate PASS
- snapshot-only

Karar:
- NOT_PROMOTED
- BiLSTM micro-grid açılmayacak

## Current leader
CNN-LSTM:
- LB6
- W32
- D0.10
- LR .001
- **1528.5699 / 20/33**

## Next
**CNN-BiLSTM — NOT_RUN / sıradaki model**

---

# 16. Modern sequence / foundation modeller

## TimesFM-3 zero-shot V1

Representation:
- raw monthly Gold/Silver/Platinum/Palladium
- multivariate context
- no fine-tuning
- no covariates

DEV:
- **1850.4113 / 19/33**
- rel.MAE/RW 1.0526

Karar:
- NOT_PROMOTED
- frozen V1 kapalı
- aynı V1 tekrar edilmez

## TimeMixer++ V1

Representation:
- raw 4-metal monthly levels
- 48-month lookback
- reference-style architecture

DEV:
- **4232.5931 / 13/33**
- rel.MAE/RW 2.4076

Karar:
- REJECTED V1
- post-result architecture fishing yapılmaz

## TimeXer V1

Durum:
- **FROZEN_NOT_RUN**
- pre-run method freeze var
- seq_len 48
- patch_len 6
- Silver/Platinum/Palladium exogenous, Gold endogenous target
- henüz valid result yok

TimeXer test edilmiş gibi yazılmayacak.

---

# 17. Historical / external reference modeller

Aşağıdaki modeller ayrı yeni challenger olarak yeniden açılmamalı.

## Random Forest identity disambiguation

Repo’da iki farklı Random Forest referansı vardır ve **aynı model sonucu gibi birleştirilmemelidir**:

1. **Historical Random Forest reference:** **1491.550694 / 20/33**  
   - Challenger-B contextual reference olarak taşınmıştır.
   - Challenger B içinde yeniden koşturulmamıştır.
   - exact relation to the later Boosting canonical RF anchor is **NOT_PROVEN**.

2. **Boosting Stage-1 Random Forest anchor:** **1614.4908 / 20/33**  
   - frozen CURRENT8, Gold-log-return target, raw tree input, expanding-origin canonical Boosting Stage-1 protocolunda yeniden hesaplanmıştır.
   - provenance: `GOLD_MONTHLY_BOOSTING_STAGE1_CANONICAL_REPORT_2026-09-27.md`.

Bu iki değer bundan sonra yalnız kendi identity/protocol adıyla kullanılacaktır.

Diğer duplicate-sensitive references:
- CatBoost: Boosting ailesinde tamamlandı
- XGBoost CURRENT8/decomposition: Boosting ailesinde işlendi
- SVR: dedicated family mevcut
- PLS/Ridge/ElasticNet/Huber: Challenger B’de işlendi
- GPR-family regressors: GPR/MOGP + Challenger B içinde işlendi
- ARIMA/SARIMA/Prophet: Challenger B’de tamamlandı

---

# 18. Duplicate-prevention / yeniden çalışma kuralı

Bir model yalnız konuşma değiştiği veya geçmiş unutulduğu için yeniden çalıştırılmayacak.

Completed bir model şu koşullardan biri olmadan yeniden açılmaz:
- doğrulanmış implementasyon bug’ı
- materially farklı representation
- farklı target/horizon
- yeni structural mechanism
- yeni untouched validation authority
- independent reproducibility audit
- explicit user instruction

Sadece:
- seed değiştirmek,
- küçük parameter interval oynatmak,
- aynı modeli başka adla yazmak

yeni model kimliği değildir.

---

# 19. Şu anda kapalı araştırma yolları

Explicit reopen olmadan açılmayacak:
- ELM broad/refinement
- ANN broad/refinement
- ELMFIS broad/refinement
- ANFIS broad/refinement/ensemble
- RBFNN broad/refinement/ensemble
- Boosting family
- Challenger-B completed scope
- BiLSTM rescue tuning
- CNN/LSTM batch/kernel micro-tuning
- TimesFM-3 zero-shot V1
- TimeMixer++ V1
- SVR Stage 1-4 restart
- DMA/DMS small alpha/lambda/window tinkering

---

# 20. Açık roadmap

## Immediate
1. **CNN-BiLSTM**
2. Yalnız umut verirse predeclared structural refinement

## Sonraki ayrı yapısal aileler
- ICEEMDAN-LSTM-CNN-CBAM
- GRU
- Attention-GRU
- MA-GRUS
- Transformer
- PatchTST
- DPformer
- LSTM-Transformer
- TimeXer V1 frozen design

## Park edilmiş hatlar
- SVR: Stage 5A.3’ten
- GPR: frozen Stage 4’ten
- DMA/DMS/IDMA: en son, broader PIT panel ile

---

# 20A. Veri çalıştırma mimarisi — Neon otorite, snapshot execution

**Durum: ACTIVE INFRASTRUCTURE POLICY / BINDING**

Neon üretim verisinin otorite kaynağı olarak kalır; fakat model deneylerinde aynı tarihsel veri tekrar tekrar Neon'dan taşınmayacaktır. Mevcut data-transfer/egress kotasını korumak ve deneyleri yeniden üretilebilir yapmak için varsayılan çalışma yolu artık:

`NEON READ_ONLY → governed canonical snapshot → hash/parity gate → GitHub Actions/model execution`

## 20A.1 Ana kural

- Neon = authoritative source.
- Canonical snapshot = immutable execution cache; ikinci veri otoritesi değildir.
- Normal model run'ları snapshot üzerinden çalışır.
- Neon'a doğrudan historical full reload yalnız `REFRESH_DATASET=true` benzeri explicit refresh/audit modunda yapılır.
- Snapshot üretildiğinde schema/version/hash kaydedilir.
- Snapshot, en az bir canonical model üzerinde Neon-source sonuçlarıyla parity göstermeden yetkilendirilmez.
- Artifact expiry veya source refresh sonrası yeniden export + parity zorunludur.
- Model family'leri kendi snapshot kopyalarını üretmez; mümkün olduğunca tek governed dataset contract paylaşılır.
- DB write: YOK / READ_ONLY.

## 20A.2 Execution akışı

1. **Source inventory:** model için gereken raw/derived alanları belirle.
2. **One-shot Neon export:** yalnız gerekli kolon/tarih aralığını READ_ONLY çek.
3. **Canonical serialization:** Parquet tercih edilir; gerekirse sıkıştırılmış CSV/JSON.
4. **Data dictionary:** kolon, kaynak, unit, timezone, release/availability ve derivation kuralı.
5. **Hash freeze:** payload SHA-256 + schema/version.
6. **Parity audit:** en az bir frozen reference modelde Neon-direct vs snapshot sonuçları birebir/izin verilen toleransta karşılaştır.
7. **Authorize:** parity PASS ise snapshot MODEL_EXECUTION_AUTHORIZED.
8. **Default runs:** sonraki ANN/ANFIS/RBFNN/GPR/CNN-LSTM/challenger denemeleri snapshot'tan.
9. **Refresh:** yalnız yeni ay/veri gerekiyorsa incremental veya explicit snapshot refresh.
10. **Re-audit:** refresh sonrası hash, coverage, chronology, leakage ve parity yeniden kontrol edilir.

## 20A.3 Kota koruma kuralları

- Aynı tarihsel dataset her job'da Neon'dan yeniden indirilmez.
- `SELECT *` tipi gereksiz geniş sorgular kullanılmaz.
- Tarih ve kolon projection zorunludur.
- Bir batch'teki bağımsız modeller aynı snapshot'ı paylaşır.
- Büyük dışsal datasetler mümkünse Neon'a yazılmadan ayrı governed external snapshot olarak tutulur.
- Neon kullanımının amacı model compute değil, source-of-truth refresh/audit'tir.

---

# 20B. Yeni araştırma konusu — External Driver / Error-Regime Augmentation

**Durum: COMPLETED X0-X6 / X7 OPTIONAL-DEFERRED**

Amaç mevcut en güçlü modellerin büyük hata yaptığı ayları sonradan açıklamak değil; tahmin anında bilinebilen dışsal bilgilerin **önceden** model hatasını veya fiyat hareketini açıklayıp açıklamadığını bilimsel olarak test etmektir.

Bu konu mevcut model ailelerini yeniden açmaz. Ayrı bir **feature-information research track**'tir.

## 20B.1 Ana araştırma sorusu

> Frozen CURRENT8 / mevcut metal-temelli bilgi setine eklenen origin-safe dışsal veri, ChHHO-ANFIS ve DE-ABC-RBFNN gibi güçlü modellerin out-of-sample fiyat hatasını sistematik ve chronology-safe biçimde azaltıyor mu?

İki ayrı gate vardır:

1. **Diagnostic gate:** dışsal bilgi, gelecekteki model hata büyüklüğünü/signed error'ı origin anında öngörebiliyor mu?
2. **Forecast-value gate:** aynı bilgi modele eklendiğinde honest rolling/expanding DEV forecast hatasını gerçekten azaltıyor mu?

Yalnız diagnostic ilişki bulmak model augmentation için yeterli değildir.

## 20B.2 Körlük / hindsight yasağı

- Büyük hata aylarına bakıp sonra uygun değişken seçmek YASAK.
- 2025 outcome'ları feature selection/tuning için YASAK.
- External candidate list, transform, lag ve publication/availability kuralı sonuç görülmeden freeze edilir.
- Tüm tarama 2022-04..2024-12 DEV içinde chronology-safe yapılır.
- 2025 ancak final frozen external specification sonrası transport/reporting olarak açılır.

## 20B.3 Stage akışı

### X0 — External-driver authority + hypothesis freeze
Literatüre ve ekonomik mekanizmaya göre candidate family'leri önceden belirle; exact variable/transform/lag rules yaz.

### X1 — Availability / vintage audit
Her seri için:
- source,
- frequency,
- timezone,
- release lag,
- revision/vintage riski,
- origin tarihinde gerçekten observable olup olmadığı,
- missingness/coverage
kaydedilir.

### X2 — Residual predictability screen
ChHHO-ANFIS ve DE-ABC-RBFNN için tüm DEV originlerinde:
- signed error,
- absolute error,
- large-error flag
üzerinde yalnız origin-safe external predictors test edilir.
Tek tek en kötü aylara göre feature seçilmez.

### X3 — Block-by-block augmentation
Aynı frozen model/protokol altında:
- BASE
- BASE + FX
- BASE + RATES
- BASE + RISK
- BASE + INFLATION
- BASE + COMMODITY
- diğer pre-frozen bloklar
ayrı ayrı çalıştırılır.

### X4 — Ablation
Kazanan blok içindeki değişkenlerin marjinal katkısı leave-one-block/leave-one-feature veya compact predeclared ablation ile test edilir.

### X5 — Compact combined panel
Yalnız DEV'de tutarlı marjinal bilgi taşıyan küçük panel kurulur. Small-n nedeniyle geniş feature soup yasaktır.

### X6 — Frozen 2025 transport
Model + external panel tamamen freeze edildikten sonra 2025 bir kez reporting/transport için kullanılır. Geriye dönük feature/lag rescue yoktur.

### X7 — Error-warning model (opsiyonel ayrı çıktı)
Fiyatı değiştirmeyen, yalnız `P(large forecast error)` veya beklenen `|error|` üreten ayrı reliability layer denenebilir. Bu katman da yalnız origin-safe girdilerle eğitilir.

## 20B.4 İlk external family havuzu

Pre-outcome authority araştırmasında değerlendirilecek ana bloklar:
- USD / global FX
- nominal ve real rates
- yield curve / monetary-policy expectations
- inflation / breakevens
- market volatility / risk (örn. VIX/MOVE türü)
- economic-policy / geopolitical uncertainty
- oil / broad commodities
- equity risk appetite
- yatırımcı flow proxy'leri, yalnız real-time availability kanıtlanırsa
- official demand / central-bank data, yalnız publication-lag ve vintage güvenli ise

Bu liste nihai feature list değildir; X0 authority scan ile exact değişkenlere daraltılacaktır.

---

# 20C. Ayrı hipotez — Global FX / International Capital-Flow Proxy

**Durum: VALIDATED SECONDARY CHANNEL FOR ChHHO / NOT PRIMARY FOR DE-ABC**

Kullanıcı hipotezi: yalnız DXY değil, majör döviz paritelerinin ortak davranışı uluslararası yatırımcı yönünü ve güvenli-liman rotasyonunu yansıtabilir; mevcut 4-metal/CURRENT8 yapısında bu kanal doğrudan temsil edilmiyor olabilir.

Bu nedenle FX bloğu tek bir DXY kolonu olarak değil, ayrı bir bilgi ailesi olarak test edilecektir.

## 20C.1 Başlangıç candidate seti

Exact source/availability doğrulamasından sonra değerlendirilecekler:
- DXY veya broad USD index
- EUR/USD
- USD/JPY
- GBP/USD
- USD/CHF
- USD/CNH veya CNY, real-time/market availability uygunsa
- FX volatility proxy
- cross-FX dispersion
- USD breadth: doların kaç majör para birimine karşı aynı anda güçlendiği/zayıfladığı
- safe-haven rotation proxy: Gold / USD / JPY / CHF göreli yön veya standardized relative-strength yapısı

## 20C.2 Bilimsel hipotezler

- H0: FX/global-capital-flow bilgisi CURRENT8 üzerine ilave out-of-sample bilgi sağlamaz.
- H1: origin-safe FX bilgisi sonraki ay Gold price move veya base-model forecast error üzerinde ilave bilgi sağlar.
- H2: breadth/dispersion/rotation gibi türetilmiş FX-state göstergeleri tek DXY seviyesinden daha fazla incremental bilgi taşıyabilir.

## 20C.3 Test sırası

1. DXY-only benchmark.
2. Majör-parite raw-return block.
3. Breadth/dispersion block.
4. Safe-haven rotation block.
5. Compact FX combined panel.
6. ChHHO ve DE-ABC üzerinde ayrı augmentation.
7. Base vs augmented rolling-origin comparison.
8. Frozen 2025 transport only after DEV freeze.

## 20C.4 Promotion kuralı

FX bloğu ancak:
- availability/vintage PASS,
- leakage PASS,
- DEV rolling-origin improvement,
- year stability,
- worst-month/tail behavior,
- small-n robustness,
- ablation ile gerçek marjinal katkı
gösterirse ana modele aday olur.

2025'te iyi çalışması tek başına promotion gerekçesi değildir.

Ayrıntılı çalışma dosyası:
`gold_axis_2026/GOLD_MONTHLY_EXTERNAL_DRIVERS_AND_OFFLINE_SNAPSHOT_PLAN_2026-09-28.md`

---

# 20D. External Driver research — final result

**Status: COMPLETED / GOVERNED RESULT**

Research file:
`gold_axis_2026/GOLD_MONTHLY_EXTERNAL_DRIVER_FINAL_RESULT_2026-09-28.md`

## 20D.1 Main conclusion

The external-information hypothesis is **SUPPORTED**.

Frozen base-model residuals contain incremental information that can be reduced using origin-safe external data. The winning external channel is model-specific.

### ChHHO-ANFIS
Base:
- DEV ΣAE **1413.0299 / 23/33**
- 2025 ΣAE **1252.0542 / 9/12**

DEV-authorized winner:
- **Headline CPI surprise residual layer**
- corrected DEV ΣAE **1343.6354 / 23/33**
- DEV improvement **69.3945 / 4.91%**
- frozen 2025 ΣAE **1095.5792 / 9/12**
- 2025 improvement **156.4749 / 12.50%**

FX is a validated secondary channel for ChHHO:
- PIT CNY/USD DEV ΔΣAE **-57.2741**, 2025 **1083.4280**
- H.10 major-FX DEV ΔΣAE **-49.2814**, 2025 **1084.9928**, direction **10/12**

These FX alternatives are not allowed to replace the CPI DEV winner merely because their 2025 error is lower.

### DE-ABC-RBFNN
Base:
- DEV ΣAE **1415.8371 / 25/33**
- 2025 ΣAE **1145.3733 / 9/12**

DEV-authorized winner:
- **PIT rates residual layer**
- features: DGS10 change + DFF change + Δ(DGS10-DFF) curve proxy
- corrected DEV ΣAE **1373.5811 / 25/33**
- DEV improvement **42.2560 / 2.98%**
- frozen 2025 ΣAE **1012.7415 / 9/12**
- 2025 improvement **132.6318 / 11.58%**

FX is not promoted as DE-ABC's primary external channel.

## 20D.2 Compact-panel result

Feature stacking did not beat the best simple external block on DEV.

ChHHO:
- CNY+CPI corrected DEV **1359.6012**
- CPI-only corrected DEV **1343.6354**
- decision: **CPI-only**

DE-ABC:
- CNY+rates+CPI corrected DEV **1375.4340**
- rates-only corrected DEV **1373.5811**
- decision: **rates-only**

Small-n rule:
**more external variables are not automatically better; prefer the smallest DEV-authorized block.**

## 20D.3 Risk / commodity status

Risk/equity-history block:
- encouraging diagnostic signal;
- historical values were later-ingested and do not have sufficient original PIT-storage proof;
- status: **DIAGNOSTIC_ONLY / NOT PROMOTABLE**.

Commodity/oil:
- no governed usable WTI/Brent/commodity series found in current inventory;
- status: **DATA_NOT_READY / NOT_TESTED**.

## 20D.4 Architecture status

Quota-safe execution path validated:

`Neon READ_ONLY authority → compact governed snapshot → offline GitHub Actions model test`

Normal external-driver jobs must not full-read Neon historical data repeatedly.

## 20D.5 Interpretation boundary

These results prove **incremental external information value** through a chronology-safe residual-correction layer.

They do **not** yet prove that a natively retrained ChHHO/DE-ABC with the external features embedded internally will have the same performance.

Therefore:
- ChHHO+CPI residual layer: **PROMOTE_TO_NATIVE-INTEGRATION_CHALLENGE**
- DE-ABC+Rates residual layer: **PROMOTE_TO_NATIVE-INTEGRATION_CHALLENGE**
- neither replaces the current frozen base champion yet.

## 20D.6 Stage closure

- X0 hypothesis freeze: DONE
- X1 availability/vintage audit: DONE
- X2 residual screen: DONE
- X3 block tests: DONE
- X4 ablation: DONE
- X5 compact combined panel: DONE
- X6 frozen 2025 transport: DONE
- X7 error-warning layer: OPTIONAL / DEFERRED

Evidence:
- strict PIT run **36472278469**, artifact **10992755818**
- H.10 FX run **36472823372**, artifact **10992736653**
- inflation/risk run **36473442704**, artifact **10991394856**
- compact-panel run **36474415541**, artifact **10992940914**

---

# 20E. Cross-family external information screen — zero Neon

**Status: COMPLETE / ARTIFACT-ONLY / ZERO NEON READS**

Detailed result:
`gold_axis_2026/GOLD_MONTHLY_EXTERNAL_MULTIMODEL_SCREEN_V1_2026-09-29.md`

Purpose:
extend the external-information screen from the two Pareto leaders to the broader strong cross-family set, while preserving each model's frozen forecast rows and using the same chronology-safe prequential residual-correction protocol.

Run / provenance:
- workflow run **36527575572**
- artifact **11015042783**
- runner commit **529dc3739673a8ff4787b803fc6e1446ae7355d7**
- report commit **fcd476699c91080bfb32d8563ebe2d6d667ce951**
- Neon reads: **0**
- eight base-model parity gates: **PASS**

## 20E.1 Models screened

1. ChHHO-ANFIS
2. DE-ABC-RBFNN
3. PLS1 V1 All-4
4. LMC2_RBF_M32
5. FULL7 ANN
6. REDUCED4 ANN
7. EPSILON_RBF_DAILY12
8. CATBOOST_PRICE

Predeclared external blocks:
- headline CPI surprise
- PIT rates: ΔDGS10 + ΔDFF + Δ(DGS10-DFF)
- PIT USD/CNY
- official Federal Reserve H.10 broad USD
- official Federal Reserve H.10 major FX

Selection authority remains DEV 2022-04..2024-12 only.

## 20E.2 Cross-family result

| Model | Base DEV ΣAE | Direction | Best robust external block | Corrected DEV ΣAE | Direction | ΔΣAE |
|---|---:|---:|---|---:|---:|---:|
| **ChHHO-ANFIS** | 1413.0299 | 23/33 | **Headline CPI surprise** | **1343.6354** | 23/33 | **69.3945** |
| **DE-ABC-RBFNN** | 1415.8371 | 25/33 | **PIT Rates** | **1373.5811** | 25/33 | **42.2560** |
| **PLS1 V1 All-4** | 1420.0291 | 20/33 | **PIT Rates** | **1379.3835** | 19/33 | **40.6456** |
| **FULL7 ANN** | 1428.8590 | 22/33 | **PIT USD/CNY** | **1391.1359** | 23/33 | **37.7231** |
| **REDUCED4 ANN** | 1431.4587 | 24/33 | **PIT USD/CNY** | **1398.7775** | 24/33 | **32.6812** |
| LMC2_RBF_M32 | 1424.1711 | 19/33 | BASE | 1424.1711 | 19/33 | 0 |
| **CATBOOST_PRICE** | 1460.4339 | 20/33 | **PIT USD/CNY** | **1428.4187** | 20/33 | **32.0153** |
| EPSILON_RBF_DAILY12 | 1449.1874 | 19/33 | BASE | 1449.1874 | 19/33 | 0 |

Main result:
- **6/8** strong models have at least one external block passing the robustness gate.
- LMC2_RBF_M32 and EPSILON_RBF_DAILY12 have **no robust winning external block** under this screen.
- The useful missing information channel is model-specific rather than universal.

## 20E.3 Model-specific interpretation

### ChHHO-ANFIS
Robust PASS:
- CPI: ΔΣAE **+69.3945 / +4.91%**
- PIT USD/CNY: +57.2741 / +4.05%
- H.10 major FX: +49.2814 / +3.49%
- H.10 broad USD: +42.4555 / +3.00%
- Rates: +42.1095 / +2.98%

Governed winner: **headline CPI surprise**.

### DE-ABC-RBFNN
Governed winner: **PIT rates**, ΔΣAE **+42.2560 / +2.98%**.
Headline CPI and PIT USD/CNY also pass, but are weaker.
H.10 broad/major FX do not pass.

### PLS1 V1 All-4
Only robust winner among tested blocks: **PIT rates**.
- ΔΣAE **+40.6456 / +2.86%**
- direction trade-off: **20/33 → 19/33**

### ANN ensembles
FULL7:
- winner **PIT USD/CNY**
- ΔΣAE **+37.7231 / +2.64%**
- direction **22/33 → 23/33**

REDUCED4:
- winner **PIT USD/CNY**
- ΔΣAE **+32.6812 / +2.28%**
- direction remains **24/33**

### CATBOOST_PRICE
Winner **PIT USD/CNY**:
- ΔΣAE **+32.0153 / +2.19%**
- direction remains 20/33.
Rates and CPI also pass.

### LMC2_RBF_M32 / EPSILON_RBF_DAILY12
No tested external block passes the robustness gate.
These stay as **BASE controls** for the current external-information family.

## 20E.4 Interpretation boundary

This section proves **incremental external-information value on frozen model forecast residuals**.

It does **not** establish native architecture augmentation.

Reason native integration is not yet authorized:
- current governed CPI/rates/FX compact snapshots do not cover the full historical training span used by the base models;
- zero-filling early history or using unreconstructed revised history would violate the causal comparison.

Native integration requires a new long-history origin-safe external snapshot before retraining.

## 20E.5 Native-integration priority after long-history backfill

1. **ChHHO + headline CPI surprise**
2. **DE-ABC + PIT rates**
3. **PLS1 + PIT rates**
4. **FULL7 ANN + PIT USD/CNY**
5. **REDUCED4 ANN + PIT USD/CNY**
6. **CATBOOST_PRICE + PIT USD/CNY**
7. LMC2 and DAILY12-SVR remain BASE controls unless a new external family supplies a pre-outcome rationale.

---

# 20F. Public current-data refresh and Sep/Oct 2026 forward

**Status: CURRENT-DATE REFRESH COMPLETE / ZERO NEON / OCTOBER PROVISIONAL**

Detailed evidence:
`gold_axis_2026/GOLD_MONTHLY_PUBLIC_DATA_FORWARD_RESULT_2026-09-29.md`

Authoritative successful workflow:
- run **36531420723**
- runner commit **225e4f1e24534efce67399efd81668339cb92159**
- report commit **00cfcdd6172dc4506887e9fe686fb9e933b30551**

Current public bundle:
- artifact **11015874673**
- Neon reads **0**
- four-metal data through last fully completed common day **2026-09-28**
- World Bank Gold monthly through **2026-08**
- August 2026 World Bank Gold monthly average **4411.0**
- exact GPR vintages loaded: **202608** and **202609**
- StakTrakr annual history extended with StakTrakrApi 12:00 observations.

### September 2026 — completed August origin

| Model | Predicted log return | Monthly-average forecast | Direction |
|---|---:|---:|---|
| ChHHO-ANFIS | +0.0402280 | **4592.06** | UP |
| DE-ABC-RBFNN | +0.0353930 | **4569.91** | UP |

September role:
**FROZEN FORWARD FORECAST FROM FINAL 2026-08 ORIGIN**.

### October 2026 — provisional partial-September nowcast

September partial Gold average proxy through 2026-09-28:
**4348.9496**.

| Model | Predicted log return | Provisional monthly-average nowcast | Direction |
|---|---:|---:|---|
| ChHHO-ANFIS | -0.0212929 | **4257.33** | DOWN |
| DE-ABC-RBFNN | -0.0231670 | **4249.36** | DOWN |

October role:
**PROVISIONAL_NOWCAST_ONLY**.

Reason:
- September month-end is not complete on 2026-09-29;
- World Bank September monthly Gold target is not yet available;
- partial September target is not used as training Y;
- final October forecast must be regenerated after complete September origin inputs without retuning.

Artifacts:
- ChHHO Sep **11015679869**
- DE-ABC Sep **11016920015**
- ChHHO Oct provisional **11016204637**
- DE-ABC Oct provisional **11017025301**

Earlier runs 36530729337..36531229734:
**SUPERSEDED_TECHNICAL_RUNS / NOT MODEL RESULTS**.

Final runner fixed an import-state collision by isolating ANFIS and RBFNN family imports. Do not reuse the failed mixed-import results.

---


# 20G. Data readiness for scientific feature architecture — direct authority store

## 20G.0 F4 reset supersession note

**The original V1 readiness remains valid as source evidence but is no longer sufficient as the binding F4 modeling contract.**

Later audit found that:
- daily external families must be processed with CURRENT8-compatible temporal representations;
- daily Nasdaq/WTI/Brent should be governed instead of defaulting to monthly-only fallback;
- CPI/Copper need prehistory sufficient to preserve the canonical 2010-03 training start;
- external-feature ChHHO runs require optimizer-dimension parity.

Binding current authority is Section **20L — F4 processing/frequency/optimizer reset** and the forthcoming **External Authority V2**.



**Status: COMPLETE FOR F0–F4 CORE PROGRAM / ZERO NEON**

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_DATA_READINESS_2026-09-29.md`

Successful external-store authority:
- workflow: **Gold Monthly Direct External Store V1**
- run **36533719167**
- commit **6909edb79386c56e4a33bf614deb244117c5a988**
- artifact **11018030682**
- artifact digest: `sha256:9181d4a8a346d9594ec5105ae23ed9c7251b463cfd60064a55fbda0fc819af48`
- payload SHA256: `c52670ccf7bccc75e7c92e6d8261fe25d2d8c62b986300d45d5f264a26142353`
- Neon reads: **0**
- scientific/data gate: **PASS**

## 20G.1 Ready data families

| Family | Coverage / authority | Status |
|---|---|---|
| Four metals | canonical daily snapshot + public extension | **READY** |
| GPR | governed PIT + 2026-08/09 vintages | **READY** |
| Gold target | canonical history + World Bank through 2026-08 | **READY** |
| Nominal/real 10Y | Fed H.15, 2010-01-04..2026-09-25 | **READY** |
| Fed Funds | CORE5 monthly history | **READY** |
| FX | Fed H.10, 2010-01-04..2026-09-25 | **READY** |
| VIX | Cboe, 2010-01-04..2026-09-28 | **READY** |
| Headline/Core CPI NSA | BLS, 2010-01..2026-08 | **READY** |
| Brent/WTI/Crude/Copper | World Bank, 2010-01..2026-08 | **READY** |
| Nasdaq monthly | CORE5, research span from 2010 | **READY** |
| Nasdaq daily long-history | GIW credential-required | **NOT_PROVEN / BLOCKED** |
| CPI survey-consensus surprise long-history | no governed 2010+ consensus history | **NOT_PROVEN / DO NOT SYNTHESIZE** |

Important update:
- prior `commodity/oil = DATA_NOT_READY` statements are **SUPERSEDED**;
- prior `native integration blocked pending long-history external data` statements are **SUPERSEDED FOR THE CORE F0–F4 PROGRAM**;
- old FRED-heavy long-history workflow failures are **SUPERSEDED_TECHNICAL_PROVIDER_FAILURE / NOT MODEL RESULTS**.

## 20G.2 Scientific use boundary

Ready now:
- F0 CURRENT8 parity;
- F1 CURRENT8 necessity/ablation;
- F2 metal representation;
- F3 lag/distributed-lag/MIDAS research;
- F4 external-family tests using rates, FX, VIX, realized CPI, monthly Nasdaq and commodity/oil.

Nasdaq:
- monthly level / return / 3M / 6M momentum are authorized;
- daily realized-volatility / daily drawdown / daily-MIDAS variants are not authorized until a governed credential-free or retained daily history is proven.

Inflation:
- BLS headline/core realized CPI transformations are authorized;
- survey-consensus surprise remains a separate optional lane and may not be synthetically backfilled.

## 20G.3 Active next stage

The current active model-development task is no longer a new structural family.

**Active next: ChHHO-ANFIS feature-architecture audit, beginning F0 → F1, then F2 → F3 → F4.**

CNN-BiLSTM remains structurally eligible/deferred and does not override the user's current feature/data research priority.

---


# 20H. ChHHO F0/F1 feature necessity audit

**Status: COMPLETE / DEV-ONLY / ZERO NEON**

Detailed report:
`gold_axis_2026/GOLD_MONTHLY_CHHHO_F0_F1_FEATURE_AUDIT_2026-09-29.md`

Authority:
- F0/F1 broad run **36534691218**
- broad summary artifact **11018091595**
- broad runner commit **cf44dc1925b28132590d254db098382d7442fe67**
- F1 single-feature run **36535476553**
- single-feature summary artifact **11018880667**
- single-feature runner commit **023ffef8567ae309e5ca83cff8a812808d2f6e9b**
- Neon reads: **0**
- 2025/2026 selection use: **NONE**

F0 parity:
- CURRENT8 DEV ΣAE **1413.029779**
- direction **23/33**
- parity: **PASS**

Broad F1:
- Gold+Silver: **1402.8244 / 23/33**, aggregate ΔΣAE +10.2054 (0.72%) but only 15/33 months improved, 18/33 worsened, median paired AE improvement **-0.7379**.
- MR-only: **2187.2832 / 15/33**
- VW-only: **2304.5555 / 20/33**
- Gold-only: **1583.7389 / 22/33**
- No Gold: **1795.9566 / 18/33**
- No Silver: **1589.9368 / 20/33**
- No Platinum: **2680.1790 / 21/33**
- No Palladium / Gold+Silver+Platinum: **1736.2615 / 21/33**

Single-feature F1:
- No Palladium MR: **1582.1095 / 21**
- No Gold VW: **1764.6486 / 19**
- No Silver VW: **1808.1832 / 22**
- No Palladium VW: **1920.7006 / 17**
- No Gold MR: **4017.9842 / 21**
- No Silver MR: **4337.6786 / 24**
- No Platinum MR: **10723.7857 / 18**
- No Platinum VW: **30823.7420 / 19**

Interpretation boundary:
- every one-feature deletion worsens DEV ΣAE;
- MR-only and VW-only both fail materially, so MR and VW are complementary;
- pathological reduced-input explosions are treated as **architectural stability diagnostics**, not literal causal feature-importance magnitudes;
- Gold+Silver is an interesting compact challenger but is **NOT_PROMOTED** because its small aggregate gain is not month-wise robust.

Binding decision:
- **CURRENT8 RETAINED**
- no CURRENT8 feature removed at F1;
- no combinatorial subset mining beyond the predeclared F1 screen;
- next stage is **F2 representation audit** using CURRENT8 as the retained reference;
- Gold+Silver may remain a compact control only.

Earlier mean-masking run **36534304610**:
**SUPERSEDED_TECHNICAL / NOT MODEL EVIDENCE**.

---


# 20I. ChHHO F2 representation audit

**Status: COMPLETE / DEV-ONLY / ZERO NEON**

Detailed report:
`gold_axis_2026/GOLD_MONTHLY_CHHHO_F2_REPRESENTATION_AUDIT_2026-09-29.md`

Authority:
- run **36540846993**
- head commit **bbb7765dfa2eccd33995b6fd2a1bf64821d20597**
- summary artifact **11020404994**
- summary digest `sha256:999d51afd3f235c3a43918cf2aa977b55544c72f3a3a4b7626b846a537002b33`
- Neon reads: **0**
- 2025/2026 selection use: **NONE**

F2 baseline:
- CURRENT8 MR1+VW: **1413.029779 / 23/33**
- parity: **PASS**

Best non-baseline challenger:
- Palladium MR3: **1418.9295 / 19/33**
- aggregate ΔΣAE vs CURRENT8: **-5.8997**
- months improved/worsened: **18/15**
- median paired AE improvement: **+0.3007**
- yearly ΔΣAE: 2022 **+94.47**, 2023 **-93.37**, 2024 **-7.00**
- status: **NOT_PROMOTED**

Other notable challengers:
- Gold MR6: **1486.7031 / 21**
- MR6 all: **1498.2281 / 22**
- Palladium RV: **1614.9330 / 17**
- Gold MR3: **1619.2379 / 23**
- Platinum RV: **1644.9810 / 18**
- Palladium MR6: **1658.3514 / 19**
- Gold RV: **1662.2175 / 18**
- Palladium Range: **1662.4286 / 18**
- ABSRET all: **2021.0769 / 17**
- RANGE all: **2165.1015 / 15**
- RV all: **4003.8097 / 14**
- Silver MR6, MR3-all and Platinum Range show pathological instability and are not interpreted as literal feature-importance magnitudes.

Predeclared robustness result:
- **ROBUST_PASS = []**

Binding decision:
- **CURRENT8 representation retained**
- MR remains **MR1**
- daily summary remains **GPR-conditioned VW**
- no F2 representation challenger promoted
- no feature-space expansion by adding F2 transforms
- next active stage: **F3 lag architecture audit**

---


# 20J. ChHHO F3 lag architecture audit

**Status: COMPLETE / DEV-ONLY / ZERO NEON**

Detailed report:
`gold_axis_2026/GOLD_MONTHLY_CHHHO_F3_LAG_AUDIT_2026-09-29.md`

Authority:
- primary run **36544008921**
- authoritative L1+L2 recovery run **36545472948**
- L1 artifact **11021516711**
- L1+L2 recovery artifact **11021484607**
- Neon reads: **0**
- 2025/2026 selection use: **NONE**

F3 baseline:
- L1 CURRENT8: **1413.0299 / 23/33**
- parity: **PASS**

Lag challengers:
- DL3_DECAY: **1727.8880 / 17**
- DL3_EQUAL: **1912.0261 / 14**
- L1+L2+L3: **1971.3237 / 16**
- L1/L3/L6: **7587.4515 / 16**
- L1+L2: **9109.1640 / 19**
- DL6_BETA13_FIXED: **34407.8023 / 19**

Binding decision:
- **L1 CURRENT8 retained**
- no concatenated lag package promoted
- no fixed distributed-lag compression promoted
- internal ChHHO contract after F3:
  - CURRENT8
  - MR1 + GPR-conditioned VW
  - L1 only
- next active stage: **F4 external-family native integration**

L1+L2 early JSON failures:
**SUPERSEDED_TECHNICAL / NOT MODEL EVIDENCE**.

---


# 20K. ChHHO F4 Rates native family — legacy endpoint representation

**Status: COMPLETE / VALID FOR TESTED LEGACY IMPLEMENTATION / SUPERSEDED FOR FAMILY-WIDE DECISION**

Detailed report:
`gold_axis_2026/GOLD_MONTHLY_CHHHO_F4_RATES_NATIVE_RESULT_2026-09-29.md`

Authority:
- corrected run **36550570628**
- summary artifact **11025216884**
- summary digest `sha256:640ab422603e81c7ea420ab9f9349ab6358882ce6cc784dcada0f52c52c4269f`
- BASE artifact **11023949755**
- Neon reads **0**

Baseline parity:
- **1413.029779 / 23/33**
- **PASS**

Chronological routed Rates family:
- ΣAE **1657.1153**
- direction **21/33**
- ΔΣAE vs BASE **-244.0855**
- months improved/tied/worsened **9/9/15**
- 2022 ΔΣAE **-89.5792**
- 2023 ΔΣAE **-141.5176**
- 2024 ΔΣAE **-12.9887**
- promotion gate **FAIL**

Static candidate best:
- R_BE10 **1691.8333 / 19/33**, still worse than BASE.

Binding interpretation after F4 reset:
- run **36550570628** remains valid for the exact endpoint-change implementation tested;
- it **does not establish that Rates as an information family is useless**;
- Rates is reopened under the new processing-parity / optimizer-parity contract;
- earlier run **36549022859** remains SUPERSEDED_METHODOLOGY / NOT SCIENTIFIC RESULT.

---

# 20L. F4 processing / frequency / optimizer reset

**Status: ACTIVE / BINDING / MODEL RUNS PAUSED UNTIL DATA+TRANSFORM GATES PASS**

Detailed authority:
`gold_axis_2026/GOLD_MONTHLY_F4_RESET_PROCESSING_PARITY_AUDIT_2026-09-29.md`

## 20L.1 Why F4 was reset

The first F4 native Rates/FX lane was computationally valid for its exact implementation, but later audit identified three design mismatches:

1. **Processing parity defect:** daily external series were mostly compressed to endpoint-to-endpoint monthly changes rather than CURRENT8-style monthly representation + GPR-conditioned daily-path summary.
2. **Frequency under-use:** daily Nasdaq-100 and daily WTI/Brent were not yet governed even though daily source histories can be obtained; VIX/Rates/FX already had daily authority.
3. **Optimizer-dimension parity defect:** ChHHO kept POP=24 while antecedent dimension increased from 80 to 90/100+, reducing search effort per optimized parameter.

Standardization itself was present and is **not** the main defect.

## 20L.2 Legacy evidence status

### Rates legacy native
- run **36550570628**
- BASE parity **1413.029779 / 23/33 PASS**
- routed result **1657.1153 / 21/33**
- status: **VALID_FOR_LEGACY_ENDPOINT_REPRESENTATION_ONLY / SUPERSEDED_FOR_FAMILY_DECISION**

### FX legacy native
- run **36552598677**
- artifact **11026195076**
- digest `sha256:db389252b953b252a3a0b33fefbbc00c8e2df757ef53f25c64fcf254442d1a56`
- BASE parity **1413.029779 / 23/33 PASS**
- routed result **1811.986846 / 18/33**
- status: **VALID_FOR_LEGACY_ENDPOINT_REPRESENTATION_ONLY / SUPERSEDED_FOR_FAMILY_DECISION**

Detailed FX record:
`gold_axis_2026/GOLD_MONTHLY_CHHHO_F4_FX_LEGACY_RESULT_2026-09-29.md`

Earlier residual-correction screens remain valid for the separate residual-correction architecture and are not native-input evidence.

## 20L.3 New apple-to-apple external feature contract

For daily positive price/index series:
- monthly representation = `log(mean_level[p]/mean_level[p-1])`;
- daily representation = **same GPR-conditioned age-weighted daily log-return logic as CURRENT8**.

For daily yields/rates:
- monthly representation = `mean_yield[p]-mean_yield[p-1]`;
- daily representation = **same GPR-conditioned weighting applied to intramonth daily yield differences**.

For native monthly statistics:
- do not synthesize daily values;
- use economically appropriate monthly transforms while preserving full canonical training history.

FX quote sign is normalized so **positive = USD strengthening** before aggregation.

## 20L.4 Optimizer parity

Frozen base:
- 8 inputs
- 5 rules
- antecedent parameter dimension **80**
- POP **24**
- generations **45**
- repeats **3**

New rule:
`D(k)=10k`
and
`POP(k)=ceil(24 × D(k)/80)`.

Examples:
- 8 inputs → 24
- 9 → 27
- 10 → 30
- 20 → 60

Generations/repeats stay 45/3 unless a dedicated optimizer audit changes them.

## 20L.5 External Authority V2

V2 must preserve the existing official H.10/H.15/VIX/CPI/World-Bank evidence and close these gaps:

- daily Nasdaq-100 authority;
- daily WTI authority;
- daily Brent authority;
- CPI prehistory sufficient for 2010-era YoY transforms;
- World Bank prehistory sufficient for canonical 2010-03 training parity.

Technical provider failures during V2 construction are **NOT MODEL RESULTS**.

## 20L.5A External Authority V2 — COMPLETE

- run **36560331164**
- head commit **9f4f53c1a2ddbac5752c24227b94e6ce2d092fca**
- artifact **11028494060**
- artifact digest `sha256:36e7f723a6c84cfdfd3394950381d112267b59af57e0502986e80d7388b017f6`
- payload SHA256 `fb779f1f1a3f5689f9f631aadc7e6e6e0c8cf5e50ec7730a233b80e8789438bc`
- Neon reads **0**
- gate **PASS**

Daily authority now frozen:
- Nasdaq-100 direct Nasdaq API: 2010-01-01..2026-09-28, n=4264
- WTI direct U.S. EIA: 2010-01-04..2026-09-22, n=4140
- Brent direct U.S. EIA: 2010-01-04..2026-09-22, n=4230
- Rates/FX/VIX retained from governed V1 authority
- CPI prehistory extended to 2008
- World Bank commodity/Copper prehistory extended to 2008

Audit discovery:
- official WTI contains one non-positive observation in the governed span: **2020-04-20 = -36.98**;
- therefore WTI log-return transformation is forbidden;
- WTI uses signed monthly-mean difference + GPR-weighted daily first difference;
- no clipping/deletion/synthetic correction.

## 20L.5B B1 transform parity — COMPLETE

- run **36560992052**
- head commit **7edea63450ce993be1c8686ea20d1c0c2c502931**
- artifact **11028839840**
- artifact digest `sha256:36cd3d69c4510fa527e8eedad6bcdf08a7a73b42a6c2267399366b5044e195ea`
- External Authority V2 payload `fb779f1f1a3f5689f9f631aadc7e6e6e0c8cf5e50ec7730a233b80e8789438bc`
- gate **PASS**
- rows checked **5346**
- Gold VW formula max absolute parity difference **0.0**
- canonical history shortened **NO**
- all external features finite **YES**
- target-month external data **NO**
- 2025/2026 selection use **NO**
- minimum eligible monthly observations:
  - Brent 13
  - Broad USD 10
  - Nasdaq-100 18
  - Nominal10Y 17
  - Real10Y 17
  - VIX 18
  - WTI 7

Conclusion: external daily transforms are now processing-parity compatible with the retained CURRENT8 MR/VW architecture.

## 20L.5C B2 processing + optimizer parity — COMPLETE

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_F4_B2_PROCESSING_OPTIMIZER_PARITY_2026-09-29.md`

- run **36564452306**
- head commit **78ca76a51e5a44050eaa5600fec7213758e6e1c3**
- artifact **11031577274**
- artifact digest `sha256:f28c2175a3207b743baa99198e7f80f961366e13b81d89f40adddca58436a331`
- Neon reads **0**
- B1 revalidation **PASS**
- B2-A processing/preprocessing parity **PASS**
- B2-B optimizer + BASE parity **PASS**
- BASE rerun DEV ΣAE **1413.0297794084559**
- BASE direction **23/33**
- ALL6 inputs **22**
- antecedent parameter dimension **220**
- ALL6 population **66**
- generations **45**
- repeats **3**
- ALL6 model outcome produced **NO**
- 2025/2026 selection use **NO**

Earlier run **36564354047** failed before the scientific audit because of a workflow shell-variable escaping error and is **TECHNICAL_WORKFLOW_FAILURE / NOT_SCIENTIFIC_RESULT**.

Conclusion: the new external inputs are proven to pass through the same downstream chronological scaling / ANFIS / local-refit pipeline as CURRENT8, and optimizer search density is not below BASE.

## 20L.6 ALL6-COMPACT diagnostic — COMPLETE / NOT PROMOTED

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_F4_ALL6_COMPACT_RESULT_2026-09-29.md`

Authoritative execution:
- workflow **Gold Monthly F4 ALL6 Compact Sharded Diagnostic V1**
- run **36567473694**
- head commit **59fff6bba43eda027884af0088919a5c25d4d96c**
- 6/6 independent DEV shards **SUCCESS**
- merge/summary **SUCCESS**
- summary artifact **11032667656**
- summary artifact digest `sha256:c743f4e06185e6a64574cb78f5b35451123a2ea0ca9458a41c900a4118903c27`
- 2025 selection use **NO**
- 2026 selection use **NO**

Frozen BASE companion:
- DEV ΣAE **1413.0297794084559**
- Direction **23/33**
- MAE **42.8190842245**
- parity **PASS**

ALL6-COMPACT:
- CURRENT8 8 + external 14 = **22 inputs**
- Rates + Broad USD + VIX + Nasdaq-100 + WTI + Brent
- antecedent parameter dimension **220**
- POP **66**
- generations **45**
- repeats **3**
- DEV ΣAE **2870.961742339026**
- MAE **86.9988406769**
- Direction **19/33**
- paired wins/losses/ties **10 / 23 / 0**
- median paired AE improvement (BASE − ALL6) **-10.4520781833**
- worst month **2022-05**
- worst ALL6 absolute error **920.8863163163**
- signed mean bias **+23.8535037779**

Relative to BASE:
- ΣAE deterioration **+1457.93196293057 USD**
- relative ΣAE deterioration **+103.18%**
- direction **-4 correct months**

Yearly DEV:
- 2022: BASE **397.8794** vs ALL6 **1416.8928**
- 2023: BASE **395.7140** vs ALL6 **629.5865**
- 2024: BASE **619.4364** vs ALL6 **824.4825**

Decision:
- ALL6 diagnostic execution **VALID**
- ALL6 final promotion **REJECTED**
- rejection of all external families individually **NOT AUTHORIZED**
- 2025 transport for the 22-input ALL6 form **NOT OPENED**
- 2026 stress for the 22-input ALL6 form **NOT OPENED**
- next scientific stage: **family decomposition + dimensionality/redundancy diagnosis**, then constrained compact selection.

The system-level degradation may reflect harmful families, redundant/correlated blocks, interaction effects, weak-signal dilution, high-dimensional premise search difficulty, or isolated pathological origins. Therefore the six families must be decomposed before any family-wide conclusion.

## 20L.6A Rates parity family decomposition — COMPLETE / COMBINED BLOCK NOT PROMOTED

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_F4_RATES_PARITY_RESULT_2026-09-29.md`

Authoritative execution:
- workflow **Gold Monthly F4 Rates Parity Family V1**
- run **36569188686**
- head commit **c2d1e2148725ff9cae481ea28e724056617220a2**
- 6/6 DEV shards **SUCCESS**
- summarize **SUCCESS**
- summary artifact **11033071845**
- summary digest `sha256:d8abaeae0fd2c90f605d7c4beca4763ea2106f0bf475caefd00d9e054506850d`

Parity-correct Rates block:
- NOM10_MR_ANALOG
- NOM10_VW_ANALOG
- REAL10_MR_ANALOG
- REAL10_VW_ANALOG
- total inputs **12**
- antecedent parameter dimension **120**
- POP **36**
- generations **45**
- repeats **3**
- same chronological training-only scaling / ANFIS / local-refit path as CURRENT8

DEV result:
- BASE **1413.0297794084559 / 23/33**
- CURRENT8 + Rates(4) **6102.555639186698 / 16/33**
- ΣAE deterioration **+4689.525859778241 USD**
- relative deterioration **+331.88%**
- direction change **-7**
- paired wins/losses/ties **12 / 21 / 0**
- median paired AE improvement (BASE − Rates) **-11.9534526814**
- worst month **2022-04**, AE **1905.4333029326**
- signed mean bias **-131.7716439599**

Yearly DEV:
- 2022: BASE **397.8794** vs Rates **4276.9230**
- 2023: BASE **395.7140** vs Rates **659.9945**
- 2024: BASE **619.4364** vs Rates **1165.6381**

Redundancy diagnosis:
- BASE rank **8/8**, Rates-augmented rank **12/12**
- BASE condition number **6.8807**
- Rates-augmented condition number **9.1956**
- condition-number ratio **1.3364**
- NOM10_VW vs REAL10_VW correlation **+0.8266**
- NOM10_MR vs REAL10_MR correlation **+0.8194**
- max Rates-vs-CURRENT8 correlation: Gold_MR1 vs REAL10_MR **-0.5240**

Decision:
- combined four-input Rates block **NOT PROMOTED**
- Rates family-wide rejection **NOT YET AUTHORIZED**
- 2025/2026 remain closed
- because the block remains full-rank but has strong nominal-vs-real redundancy, the clean next Rates-only resolution is pre-outcome sub-decomposition:
  1. nominal-only pair,
  2. real-only pair,
  3. MR-only pair,
  4. VW-only pair,
  each with dimension-adjusted optimizer parity.
- **FX is not started yet**, consistent with one-family-at-a-time execution.

## 20L.7 Workflow hold

Legacy workflows:
- `.github/workflows/gold-monthly-chhho-f4-rates-v1.yml`
- `.github/workflows/gold-monthly-chhho-f4-fx-v1.yml`

are on **MANUAL LEGACY HOLD**.

Current exact active stage:
**F4 Rates internal sub-decomposition after parity-correct combined Rates block non-promotion; FX not started.**

---

# 21. Bundan sonra manifest nasıl güncellenecek

Her yeni deney bittiğinde **aynı commit zincirinde** bu ana manifest güncellenecek.

Yeni model kaydı şu bilgileri burada içermeli:
- model adı ve family
- neden açıldı
- exact representation
- target
- chronology
- frozen parameters
- DEV ΣAE
- DEV direction
- scientific gate
- 2025/2026 rolü
- karar
- tekrar açılma kuralı
- sıradaki adım

Machine-readable JSON registry yalnız bu manifestin aynasıdır; ikinci bir proje otoritesi değildir.

---

# 22. Provenance — sadece denetim için

Aşağıdaki dosyalar ayrıntılı run/job/artifact ve ham deney kanıtlarını tutar. Proje akışını anlamak için zorunlu değildir.

## Supersession kuralı

Bu provenance dosyalarının bazılarının içinde yazıldığı tarihte doğru olan fakat artık eski kalmış "next action", "primary model", "final winner" veya "stage status" ifadeleri bulunabilir.

Özellikle:
- eski ELM-vs-ANN MAPE-centered family freeze aktif metric açısından superseded;
- CNN/LSTM authority planındaki "Stage 0 next" satırı tarihsel; Stage 0-1D ve BiLSTM artık tamamlandı;
- SVR authority planının başlangıç "Stage 1 next" satırı tarihsel; family Stage 5A.3’e kadar ilerledi;
- Challenger-B ayrı manifesti artık project-state authority değil;
- eski ELM/ANN mega-ledger’daki historical next-action satırları binding değildir.

**Current state için daima bu master manifest kullanılır.**


- `GOLD_MONTHLY_ELM_METAHEURISTIC_LEDGER_ANN_PLAN_2026-09-25.md`
- `GOLD_MONTHLY_CROSS_FAMILY_REAUDIT_SIGMAAE_DIRECTION_2026-09-26.md`
- `GOLD_MONTHLY_ANFIS_FINAL_CLOSURE_CROSS_FAMILY_2026-09-26.md`
- `GOLD_MONTHLY_RBFNN_FINAL_FREEZE_2026-09-26.md`
- `GOLD_MONTHLY_GPR_STAGE3_REPORT_2026-09-26.md`
- `GOLD_MONTHLY_DMA_DMS_IDMA_DEFERRED_CHECKPOINT_2026-09-27.md`
- `GOLD_MONTHLY_BOOSTING_FAMILY_FINAL_CLOSURE_2026-09-28.md`
- `GOLD_MONTHLY_SVR_DWT_FAMILY_LEDGER_2026-09-28.md`
- `GOLD_MONTHLY_CHALLENGER_B_MANIFEST_2026-09-28.md`
- `GOLD_MONTHLY_CNN_LSTM_STAGE1D_LR_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_BILSTM_STRUCTURAL_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_TIMESFM3_ZERO_SHOT_V1_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_TIMEMIXERPP_V1_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_TIMEXER_V1_FREEZE_2026-09-28.md`

---

# 23. Kontrol ve Uyum Özeti

- Tek canonical monthly manifest: **YES**
- Projeyi anlamak için eski ledger zorunluluğu: **NO**
- Challenger B ana akışa entegre: **YES**
- Completed / paused / deferred / not-run ayrımı: **YES**
- Duplicate-prevention: **BINDING**
- DEV authority: **2022-04..2024-12**
- Random split: **NONE**
- 2025 retrospective tuning: **NONE**
- 2026 selection: **NONE**
- DB write: **NONE**
- Snapshot V1 authorized: **YES**
- Current exact next model/research stage: **F4 Rates internal sub-decomposition** after parity-correct Rates(4) DEV ΣAE **6102.555639 / 16/33** vs BASE **1413.029779 / 23/33**. Rates family-wide rejection is not yet authorized because nominal/real MR/VW pairs show strong internal redundancy; FX/VIX/Nasdaq/Energy remain not started in the one-family-at-a-time sequence.


---

# APPENDIX A — ELM tam broad-screen envanteri

Bu tablo **historical DEV MAPE** ile raporlanan ELM screen’idir. Aktif cross-family seçim otoritesi ΣAE+direction’dır; bu tablo duplicate-prevention ve tarihsel sonuç kaydı içindir.

| Model | Historical DEV MAPE % |
|---|---:|
| Vanilla ELM | 2.19286 |
| PSO-ELM | 2.73492 |
| GA-ELM | 2.55877 |
| DE-ELM | 2.58768 |
| MPA-ELM | 2.44941 |
| ABC-ELM | 2.48251 |
| SSA-ELM | 2.47446 |
| GWO-ELM | 2.45696 |
| WOA-ELM | 2.23961 |
| HHO-ELM | 2.60822 |
| ACO-ELM | 2.69993 |
| Bat-ELM | 2.79911 |
| FA-ELM | 3.03251 |
| MFO-ELM | 2.77548 |
| FPA-ELM | 2.34201 |
| FA-FPA-ELM | 2.63753 |
| CS-ELM | 2.73091 |
| SCA-ELM | 2.19271 |
| Salp-ELM | 2.45982 |
| SMA-ELM | 2.53462 |
| GOA-ELM | 2.42952 |
| ALO-ELM | 2.47135 |
| TLBO-ELM | 2.55127 |
| JAYA-ELM | 2.49871 |
| HGS-ELM | 2.45196 |
| ChOA-ELM | 2.64419 |
| HGSO-ELM | 2.26442 |
| AOA-ELM | **2.15854** |
| CPA-ELM | 2.69050 |
| Krill Herd-ELM | 2.64209 |
| Crow Search-ELM | 2.61964 |
| DE-ABC-ELM | 2.53226 |
| Multi-swarm ELM | 2.41470 |

Targeted ELM refinements:
- Adaptive PSO-ELM: DEV MAPE 2.60499
- TLBO-tuned PSO-ELM: 2.32298
- DE-tuned PSO-ELM: 2.56288
- Adaptive/Improved TLBO-ELM: 2.46807
- Adaptive Crow Search-ELM: 2.35034
- PSO-TLBO Hybrid ELM: **2.18548**

Active-metric re-audit references:
- AOA-ELM: **ΣAE 1474.10 / 20/33**
- SCA-ELM: **1508.71 / 21/33**
- TLBO-ELM: **1758.75 / 23/33**
- PSO-TLBO Hybrid ELM: **1487.55 / 20/33**

---

# APPENDIX B — ANN tam broad-screen ve refinement envanteri

Broad-screen tabloda DEV MAPE + DEV direction tarihsel screen metriğidir. Aktif cross-family karar için frozen ensemble ΣAE+direction sonuçları kullanılır.

| Model | DEV MAPE % | DEV Direction |
|---|---:|---:|
| Vanilla ANN | 2.18895 | 54.55% |
| PSO-ANN | 2.61194 | 54.55% |
| GA-ANN | 2.36033 | 63.64% |
| DE-ANN | 2.84842 | 51.52% |
| MPA-ANN | 2.19947 | 57.58% |
| ABC-ANN | 3.06525 | 51.52% |
| SSA-ANN | 2.41896 | 66.67% |
| GWO-ANN | 2.53258 | 54.55% |
| WOA-ANN | 2.38669 | 63.64% |
| HHO-ANN | 2.49709 | 57.58% |
| ACO-ANN | 2.35494 | 63.64% |
| Bat-ANN | 2.64871 | 54.55% |
| FA-ANN | 2.39002 | 60.61% |
| MFO-ANN | 2.60702 | 57.58% |
| FPA-ANN | 2.70125 | 42.42% |
| FA-FPA-ANN | 2.28398 | 60.61% |
| CS-ANN | 2.50128 | 54.55% |
| SCA-ANN | 2.36197 | **72.73%** |
| Salp-ANN | 2.43583 | 60.61% |
| SMA-ANN | 2.57631 | 51.52% |
| GOA-ANN | 3.00269 | 51.52% |
| ALO-ANN | 2.49827 | 60.61% |
| TLBO-ANN | 2.37828 | 60.61% |
| JAYA-ANN | 2.53899 | 63.64% |
| HGS-ANN | 2.48142 | 51.52% |
| ChOA-ANN | 2.46605 | 60.61% |
| HGSO-ANN | 2.66180 | 54.55% |
| AOA-ANN | 2.51719 | 57.58% |
| CPA-ANN | 2.27985 | 60.61% |
| Krill Herd-ANN | 2.37501 | 66.67% |
| Crow Search-ANN | 2.50491 | 60.61% |
| DE-ABC-ANN | 2.26109 | 66.67% |
| Multi-swarm ANN | 2.59615 | 54.55% |

Refinements/hybrids:

| Model | DEV MAPE % | DEV Direction |
|---|---:|---:|
| Adaptive PSO-ANN | 2.26567 | 57.58% |
| Adaptive TLBO-ANN | 2.24090 | 54.55% |
| TLBO-tuned PSO-ANN | 2.28920 | **69.70%** |
| DE-tuned PSO-ANN | 2.30759 | 54.55% |
| Adaptive Crow Search-ANN | 2.49577 | 60.61% |
| PSO-TLBO Hybrid ANN | 2.34425 | 60.61% |
| MPA+SCA Hybrid ANN | 2.23957 | 60.61% |
| MPA+GA Hybrid ANN | 2.48841 | 51.52% |
| MPA+CPA Hybrid ANN | 2.56713 | 57.58% |

Frozen active-metric ensembles:
- FULL7: **ΣAE 1428.8590 / 22/33**
- REDUCED4: **1431.4587 / 24/33**

---

# APPENDIX C — ELMFIS 33-entry broad-screen envanteri

| Model | DEV ΣAE | Direction |
|---|---:|---:|
| Vanilla ELMFIS | 1996.2933 | 20/33 |
| PSO-ELMFIS | 2358.4962 | 20/33 |
| GA-ELMFIS | 1980.8994 | 14/33 |
| DE-ELMFIS | 1665.4715 | 21/33 |
| MPA-ELMFIS | 3060.5864 | 19/33 |
| ABC-ELMFIS | **1524.8854** | 21/33 |
| SSA-ELMFIS | 2124.4760 | 20/33 |
| GWO-ELMFIS | 1943.5595 | 22/33 |
| WOA-ELMFIS | 2536.5468 | 15/33 |
| HHO-ELMFIS | 1857.8942 | 22/33 |
| ACO-ELMFIS | 1942.8695 | 19/33 |
| Bat-ELMFIS | 2137.8294 | 19/33 |
| FA-ELMFIS | 2421.4143 | 23/33 |
| MFO-ELMFIS | 2244.0539 | 19/33 |
| FPA-ELMFIS | 2251.8993 | 22/33 |
| FA-FPA-ELMFIS | 1820.4499 | **25/33** |
| CS-ELMFIS | 1809.3931 | **25/33** |
| SCA-ELMFIS | 3177.3119 | 21/33 |
| Salp-ELMFIS | 2273.0187 | 19/33 |
| SMA-ELMFIS | **1651.4482** | **25/33** |
| GOA-ELMFIS | 2322.7589 | 21/33 |
| ALO-ELMFIS | 2812.5033 | 18/33 |
| TLBO-ELMFIS | 3240.2851 | 20/33 |
| JAYA-ELMFIS | 1810.4656 | 21/33 |
| HGS-ELMFIS | 1780.8620 | 20/33 |
| ChOA-ELMFIS | 2822.8921 | 20/33 |
| HGSO-ELMFIS | 1594.6455 | 18/33 |
| AOA-ELMFIS | 1873.9154 | 22/33 |
| CPA-ELMFIS | 1925.0323 | 20/33 |
| Krill Herd-ELMFIS | 3043.2306 | 20/33 |
| Crow Search-ELMFIS | 1881.2292 | 20/33 |
| DE-ABC-ELMFIS | 2317.34 | 17/33 |
| Multi-swarm-ELMFIS | 1848.10 | 18/33 |

Literature-specific:
- CQCSA-ELMFIS: **1731.94 / 20/33**, not promoted.

---

# APPENDIX D — RBFNN 32-meta broad-screen envanteri

All rows below passed the Stage-1 scientific gate on DEV.

| Model | DEV ΣAE | Direction |
|---|---:|---:|
| DE-ABC | **1415.8371** | **25/33** |
| Salp | 1426.6878 | 23/33 |
| MFO | 1449.1065 | 20/33 |
| JAYA | 1460.7401 | 21/33 |
| HGS | 1461.9334 | 20/33 |
| ACO | 1481.9468 | 19/33 |
| GOA | 1492.8771 | 20/33 |
| WOA | 1499.2639 | 19/33 |
| AOA | 1501.0998 | 19/33 |
| Bat | 1501.6410 | 21/33 |
| MPA | 1510.5118 | 20/33 |
| GWO | 1511.6245 | 22/33 |
| GA | 1523.4710 | 19/33 |
| FA-FPA | 1524.5325 | 20/33 |
| FPA | 1525.4420 | 21/33 |
| CS | 1525.6645 | 20/33 |
| TLBO | 1525.7861 | 19/33 |
| Multi-swarm | 1525.8563 | 21/33 |
| FA | 1530.4171 | 20/33 |
| Crow | 1538.2158 | 19/33 |
| SCA | 1541.6271 | 21/33 |
| DE | 1550.2583 | 18/33 |
| ABC | 1558.8168 | 18/33 |
| SSA | 1559.8246 | 18/33 |
| Krill | 1560.4829 | 17/33 |
| HGSO | 1564.9802 | 20/33 |
| SMA | 1568.1653 | 19/33 |
| ChOA | 1571.0927 | 20/33 |
| HHO | 1586.1569 | 20/33 |
| ALO | 1597.3649 | 19/33 |
| PSO | 1598.5085 | 20/33 |
| CPA | 1608.6437 | 17/33 |

Stage-3 refinements:
- Adaptive PSO 1519.3532 / 18
- Adaptive TLBO 1552.2502 / 21
- TLBO-tuned PSO 1610.0497 / 19
- DE-tuned PSO 1524.1595 / 20
- Adaptive Crow 1455.8616 / 21
- PSO-TLBO 1489.6671 / 21
- MOLS-RBFNN 1578.5391 / 18
- FULL_MEDIAN ensemble 1444.3008 / 22

---

# APPENDIX E — GPR/MOGP Stage-1 full screen

| Model | DEV ΣAE | Direction |
|---|---:|---:|
| Multi-swarm | **1606.7414** | 23/33 |
| AOA | 1611.8839 | 22/33 |
| GWO | 1650.2596 | 21/33 |
| ABC | 1672.2945 | 22/33 |
| HGSO | 1677.9024 | 19/33 |
| SMA | 1701.0740 | 22/33 |
| MPA | 1701.5802 | 23/33 |
| MFO | 1702.0152 | 19/33 |
| ALO | 1704.0561 | 21/33 |
| DE-ABC | 1709.2591 | 23/33 |
| FPA | 1711.7090 | 20/33 |
| SCA | 1713.8379 | 23/33 |
| GA | 1723.5877 | 21/33 |
| FA-FPA | 1724.6532 | **25/33** |
| TLBO | 1736.5717 | 19/33 |
| Crow | 1736.9995 | 22/33 |
| Bat | 1746.6720 | 21/33 |
| JAYA | 1760.9248 | 22/33 |
| Krill | 1769.3329 | 22/33 |
| CPA | 1778.4226 | 22/33 |
| PSO | 1780.2169 | 19/33 |
| SSA | 1798.1173 | 21/33 |
| HGS | 1814.9260 | 20/33 |
| ACO | 1815.8271 | 19/33 |
| ChOA | 1822.1087 | 17/33 |
| HHO | 1823.3648 | 21/33 |
| CS | 1835.2043 | 22/33 |
| WOA | 1836.8353 | 21/33 |
| Salp | 1841.6043 | 20/33 |
| GOA | 1850.3608 | 22/33 |
| FA | 1861.6613 | 19/33 |
| DE | 1924.6270 | 21/33 |

Stage-3 structural/refinement table remains:
- LMC2_RBF_M32 **1424.1711 / 19**
- MPA-SCA 1709.2943 / 22
- Adaptive Crow 1724.2888 / 19
- Adaptive TLBO 1740.8877 / 19
- Adaptive PSO 1794.2201 / 20
- PSO-TLBO 1815.3287 / 21
- TLBO-tuned PSO 1863.6677 / 19
- DE-tuned PSO 1939.8588 / 16

---

# APPENDIX F — SVR Stage-4 metaheuristic broad screen

Frozen Stage-2 parent for comparison:
- **EPSILON_RBF_DAILY12 = 1449.187363 / 19/33**

| Method | DEV ΣAE | Direction | Authority status |
|---|---:|---:|---|
| PSO | 1719.949306 | 17/33 | scored |
| GA | 1611.632502 | 19/33 | scored |
| DE | 1590.781952 | 19/33 | scored |
| MPA | 1696.206317 | 15/33 | scored |
| ABC | 1563.258913 | 16/33 | scored |
| SSA | 1659.670617 | 19/33 | scored |
| GWO | 1590.104631 | 18/33 | scored |
| WOA | 1635.345256 | 17/33 | scored |
| HHO | 1549.539823 | 18/33 | scored |
| ACO | 1600.397350 | 18/33 | scored |
| Bat | 1540.482107 | 14/33 | scored |
| FA | 1583.810635 | 19/33 | technical PASS; user-excluded from authoritative ranking |
| MFO | 1690.484321 | 20/33 | scored |
| FPA | 1605.813991 | 15/33 | scored |
| FA-FPA | 1572.041237 | 20/33 | scored |
| CS | 1564.515299 | 19/33 | scored |
| SCA | 1843.705276 | 14/33 | scored |
| Salp | 1543.355326 | 19/33 | scored |
| SMA | 1517.362987 | 18/33 | scored |
| GOA | 1617.200714 | 17/33 | scored |
| ALO | **1494.808085** | 20/33 | best authoritative Stage-4 meta |
| TLBO | 1574.826138 | 20/33 | scored |
| JAYA | 1529.754239 | 18/33 | scored |
| HGS | 1664.428496 | 18/33 | scored |
| ChOA | 1560.301510 | 17/33 | scored |
| HGSO | 1508.944115 | 18/33 | scored |
| AOA | 1508.677155 | 20/33 | scored |
| CPA | 1737.873104 | 16/33 | scored |
| Krill | 1770.446584 | 15/33 | scored |
| Crow | 1541.791658 | 18/33 | scored |
| DE-ABC | 1514.213571 | 19/33 | scored |
| Multi-swarm | 1697.478100 | 13/33 | scored |

Sonuç:
- hiçbir Stage-4 metaheuristic frozen Stage-2 parent 1449.187363’ü geçmedi.
- optimizer-only SVR tuning’in zayıf görünmesi, later causal DWT/MODWT structural line’ı geçersiz kılmaz.

---

# APPENDIX G — ANFIS broad-screen completeness register

ANFIS’te ortak 32-meta setinin tamamı çalıştırıldı.

Scientific PASS broad screen: **27/32**.  
Scientific reject: **5/32**:
- ABC
- WOA
- FPA
- HGS
- AOA

Reject nedeni:
- en az bir origin’de pathological forecast magnitude / scientific forecast gate failure.

Broad-screen valid frontier before literature-specific extension:
- MFO-ANFIS: **1630.3325 / 20**
- HHO-ANFIS: **1646.1336 / 23**

Vanilla:
- **1852.0465 / 21**

Stage-3 parity refinement sonuçları:
- MPA-CPA: 1918.5637 / 18 — PASS
- PSO-TLBO Hybrid: 3156.9979 / 19 — PASS
- TLBO-tuned PSO: 3465.1623 / 20 — PASS
- Adaptive PSO: 363283.4306 / 22 — scientific FAIL
- Adaptive TLBO: 24830.2156 / 17 — scientific FAIL
- Adaptive Crow: 3432.3536 / 18 — scientific FAIL
- DE-tuned PSO: 9166.1914 / 18 — scientific FAIL
- MPA-SCA: 3275.4131 / 20 — scientific FAIL
- MPA-GA: 3242.7176 / 20 — scientific FAIL

Literature-specific:
- **ChHHO-ANFIS: 1413.029779 / 23 — family champion**
- MVO-ANFIS: 2057.3973 / 17 — valid, not promoted

Per-method numeric metrics for all 27 valid broad-screen ANFIS members are not reproduced here because the consolidated family closure does not expose a single authoritative full 27-row metric table. Their execution identity is nevertheless covered by the 32-meta completeness register. No missing metric is to be guessed.

---

# APPENDIX H — completeness statement

The following families already have their full relevant tested-set tables in the main body and therefore are not duplicated again here:
- Challenger B
- CNN/LSTM/BiLSTM
- Boosting final retained/structural variants
- DMA/DMS/IDMA
- TimesFM-3 / TimeMixer++ / TimeXer status

For any future model:
- if its identity appears anywhere in Sections 4–20 or Appendices A–G, it is **already known to the project**;
- if marked completed/rejected/not-promoted, do not rerun without a valid reopen condition;
- if marked NOT_RUN/FROZEN_NOT_RUN, it remains eligible for first execution under a new pre-outcome freeze.
