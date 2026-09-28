# GOLD MONTHLY FORECAST — CANONICAL PROJECT MANIFEST

**Manifest version:** 1.2  
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
- Current exact next model: **CNN-BiLSTM**
