# GOLD MONTHLY — Feature & Variable Research Ledger V2.1

**Date:** 2026-10-01  
**Status:** HISTORICAL FEATURE / DATA / REPRESENTATION LEDGER  
**Canonical project state:** `GOLD_MONTHLY_PROJECT_MANIFEST.md`

This ledger preserves the detailed external-driver, F0–F4, Rates/FX/VIX/Brent, bias-control and representation research trail. Stage-local “next” statements are historical only. Current feature authority is summarized in the canonical manifest.

# 4. Data, Variable & Feature-Architecture Program

## 4.1 Binding interpretation before the detailed audit trail

The project distinguishes four different questions that must not be conflated:

1. **Data readiness:** is the series available with origin-safe vintage / release handling?
2. **Native feature value:** does adding the variable directly to ChHHO improve chronological DEV performance?
3. **Residual information:** can the variable explain prior-model residuals under a separate prequential correction protocol?
4. **Alarm / state information:** can the variable help describe market state or forecast-risk mechanisms without changing the price model?

Current native-price-model answer:
- CURRENT8 remains binding;
- F1 did not justify feature deletion;
- F2 did not justify representation expansion;
- F3 retained L1 only;
- F4 multi-family, Rates and FX native-input additions were not promoted.

Important residual-attribution qualification:
- residual layers can appear to improve BASE simply by correcting ChHHO's historical mean residual;
- Section 4's later BIAS_ONLY control is binding for subsequent Rates/VIX/Brent attribution;
- VIX_R1 was only **0.56 USD** better than BIAS_ONLY on DEV;
- Brent and PIT Rates were worse than BIAS_ONLY under that audit;
- earlier X-track CPI results remain recorded under their own frozen protocol and are not silently rewritten as native feature evidence.

**Governance note:** the detailed sections below preserve historical stage-local “next” statements. Section 9 is the only current roadmap authority.

## 4.2 Data execution architecture — Neon authority / snapshot execution

**Durum: ACTIVE INFRASTRUCTURE POLICY / BINDING**

Neon üretim verisinin otorite kaynağı olarak kalır; fakat model deneylerinde aynı tarihsel veri tekrar tekrar Neon'dan taşınmayacaktır. Mevcut data-transfer/egress kotasını korumak ve deneyleri yeniden üretilebilir yapmak için varsayılan çalışma yolu artık:

`NEON READ_ONLY → governed canonical snapshot → hash/parity gate → GitHub Actions/model execution`

### 20A.1 Ana kural

- Neon = authoritative source.
- Canonical snapshot = immutable execution cache; ikinci veri otoritesi değildir.
- Normal model run'ları snapshot üzerinden çalışır.
- Neon'a doğrudan historical full reload yalnız `REFRESH_DATASET=true` benzeri explicit refresh/audit modunda yapılır.
- Snapshot üretildiğinde schema/version/hash kaydedilir.
- Snapshot, en az bir canonical model üzerinde Neon-source sonuçlarıyla parity göstermeden yetkilendirilmez.
- Artifact expiry veya source refresh sonrası yeniden export + parity zorunludur.
- Model family'leri kendi snapshot kopyalarını üretmez; mümkün olduğunca tek governed dataset contract paylaşılır.
- DB write: YOK / READ_ONLY.

### 20A.2 Execution akışı

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

### 20A.3 Kota koruma kuralları

- Aynı tarihsel dataset her job'da Neon'dan yeniden indirilmez.
- `SELECT *` tipi gereksiz geniş sorgular kullanılmaz.
- Tarih ve kolon projection zorunludur.
- Bir batch'teki bağımsız modeller aynı snapshot'ı paylaşır.
- Büyük dışsal datasetler mümkünse Neon'a yazılmadan ayrı governed external snapshot olarak tutulur.
- Neon kullanımının amacı model compute değil, source-of-truth refresh/audit'tir.

---

## 4.3 External-driver research question and chronology rules

**Durum: COMPLETED X0-X6 / X7 OPTIONAL-DEFERRED**

Amaç mevcut en güçlü modellerin büyük hata yaptığı ayları sonradan açıklamak değil; tahmin anında bilinebilen dışsal bilgilerin **önceden** model hatasını veya fiyat hareketini açıklayıp açıklamadığını bilimsel olarak test etmektir.

Bu konu mevcut model ailelerini yeniden açmaz. Ayrı bir **feature-information research track**'tir.

### 20B.1 Ana araştırma sorusu

> Frozen CURRENT8 / mevcut metal-temelli bilgi setine eklenen origin-safe dışsal veri, ChHHO-ANFIS ve DE-ABC-RBFNN gibi güçlü modellerin out-of-sample fiyat hatasını sistematik ve chronology-safe biçimde azaltıyor mu?

İki ayrı gate vardır:

1. **Diagnostic gate:** dışsal bilgi, gelecekteki model hata büyüklüğünü/signed error'ı origin anında öngörebiliyor mu?
2. **Forecast-value gate:** aynı bilgi modele eklendiğinde honest rolling/expanding DEV forecast hatasını gerçekten azaltıyor mu?

Yalnız diagnostic ilişki bulmak model augmentation için yeterli değildir.

### 20B.2 Körlük / hindsight yasağı

- Büyük hata aylarına bakıp sonra uygun değişken seçmek YASAK.
- 2025 outcome'ları feature selection/tuning için YASAK.
- External candidate list, transform, lag ve publication/availability kuralı sonuç görülmeden freeze edilir.
- Tüm tarama 2022-04..2024-12 DEV içinde chronology-safe yapılır.
- 2025 ancak final frozen external specification sonrası transport/reporting olarak açılır.

### 20B.3 Stage akışı

#### X0 — External-driver authority + hypothesis freeze
Literatüre ve ekonomik mekanizmaya göre candidate family'leri önceden belirle; exact variable/transform/lag rules yaz.

#### X1 — Availability / vintage audit
Her seri için:
- source,
- frequency,
- timezone,
- release lag,
- revision/vintage riski,
- origin tarihinde gerçekten observable olup olmadığı,
- missingness/coverage
kaydedilir.

#### X2 — Residual predictability screen
ChHHO-ANFIS ve DE-ABC-RBFNN için tüm DEV originlerinde:
- signed error,
- absolute error,
- large-error flag
üzerinde yalnız origin-safe external predictors test edilir.
Tek tek en kötü aylara göre feature seçilmez.

#### X3 — Block-by-block augmentation
Aynı frozen model/protokol altında:
- BASE
- BASE + FX
- BASE + RATES
- BASE + RISK
- BASE + INFLATION
- BASE + COMMODITY
- diğer pre-frozen bloklar
ayrı ayrı çalıştırılır.

#### X4 — Ablation
Kazanan blok içindeki değişkenlerin marjinal katkısı leave-one-block/leave-one-feature veya compact predeclared ablation ile test edilir.

#### X5 — Compact combined panel
Yalnız DEV'de tutarlı marjinal bilgi taşıyan küçük panel kurulur. Small-n nedeniyle geniş feature soup yasaktır.

#### X6 — Frozen 2025 transport
Model + external panel tamamen freeze edildikten sonra 2025 bir kez reporting/transport için kullanılır. Geriye dönük feature/lag rescue yoktur.

#### X7 — Error-warning model (opsiyonel ayrı çıktı)
Fiyatı değiştirmeyen, yalnız `P(large forecast error)` veya beklenen `|error|` üreten ayrı reliability layer denenebilir. Bu katman da yalnız origin-safe girdilerle eğitilir.

### 20B.4 İlk external family havuzu

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

## 4.4 Global FX / international-capital-flow hypothesis

**Durum: VALIDATED SECONDARY CHANNEL FOR ChHHO / NOT PRIMARY FOR DE-ABC**

Kullanıcı hipotezi: yalnız DXY değil, majör döviz paritelerinin ortak davranışı uluslararası yatırımcı yönünü ve güvenli-liman rotasyonunu yansıtabilir; mevcut 4-metal/CURRENT8 yapısında bu kanal doğrudan temsil edilmiyor olabilir.

Bu nedenle FX bloğu tek bir DXY kolonu olarak değil, ayrı bir bilgi ailesi olarak test edilecektir.

### 20C.1 Başlangıç candidate seti

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

### 20C.2 Bilimsel hipotezler

- H0: FX/global-capital-flow bilgisi CURRENT8 üzerine ilave out-of-sample bilgi sağlamaz.
- H1: origin-safe FX bilgisi sonraki ay Gold price move veya base-model forecast error üzerinde ilave bilgi sağlar.
- H2: breadth/dispersion/rotation gibi türetilmiş FX-state göstergeleri tek DXY seviyesinden daha fazla incremental bilgi taşıyabilir.

### 20C.3 Test sırası

1. DXY-only benchmark.
2. Majör-parite raw-return block.
3. Breadth/dispersion block.
4. Safe-haven rotation block.
5. Compact FX combined panel.
6. ChHHO ve DE-ABC üzerinde ayrı augmentation.
7. Base vs augmented rolling-origin comparison.
8. Frozen 2025 transport only after DEV freeze.

### 20C.4 Promotion kuralı

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

## 4.5 External-driver X-track final result

**Status: COMPLETED / GOVERNED RESULT**

Research file:
`gold_axis_2026/GOLD_MONTHLY_EXTERNAL_DRIVER_FINAL_RESULT_2026-09-28.md`

### 20D.1 Main conclusion

The external-information hypothesis is **SUPPORTED**.

Frozen base-model residuals contain incremental information that can be reduced using origin-safe external data. The winning external channel is model-specific.

#### ChHHO-ANFIS
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

#### DE-ABC-RBFNN
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

### 20D.2 Compact-panel result

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

### 20D.3 Risk / commodity status

Risk/equity-history block:
- encouraging diagnostic signal;
- historical values were later-ingested and do not have sufficient original PIT-storage proof;
- status: **DIAGNOSTIC_ONLY / NOT PROMOTABLE**.

Commodity/oil:
- no governed usable WTI/Brent/commodity series found in current inventory;
- status: **DATA_NOT_READY / NOT_TESTED**.

### 20D.4 Architecture status

Quota-safe execution path validated:

`Neon READ_ONLY authority → compact governed snapshot → offline GitHub Actions model test`

Normal external-driver jobs must not full-read Neon historical data repeatedly.

### 20D.5 Interpretation boundary

These results prove **incremental external information value** through a chronology-safe residual-correction layer.

They do **not** yet prove that a natively retrained ChHHO/DE-ABC with the external features embedded internally will have the same performance.

Therefore:
- ChHHO+CPI residual layer: **PROMOTE_TO_NATIVE-INTEGRATION_CHALLENGE**
- DE-ABC+Rates residual layer: **PROMOTE_TO_NATIVE-INTEGRATION_CHALLENGE**
- neither replaces the current frozen base champion yet.

### 20D.6 Stage closure

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

## 4.6 Cross-family external-information screen

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

### 20E.1 Models screened

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

### 20E.2 Cross-family result

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

### 20E.3 Model-specific interpretation

#### ChHHO-ANFIS
Robust PASS:
- CPI: ΔΣAE **+69.3945 / +4.91%**
- PIT USD/CNY: +57.2741 / +4.05%
- H.10 major FX: +49.2814 / +3.49%
- H.10 broad USD: +42.4555 / +3.00%
- Rates: +42.1095 / +2.98%

Governed winner: **headline CPI surprise**.

#### DE-ABC-RBFNN
Governed winner: **PIT rates**, ΔΣAE **+42.2560 / +2.98%**.
Headline CPI and PIT USD/CNY also pass, but are weaker.
H.10 broad/major FX do not pass.

#### PLS1 V1 All-4
Only robust winner among tested blocks: **PIT rates**.
- ΔΣAE **+40.6456 / +2.86%**
- direction trade-off: **20/33 → 19/33**

#### ANN ensembles
FULL7:
- winner **PIT USD/CNY**
- ΔΣAE **+37.7231 / +2.64%**
- direction **22/33 → 23/33**

REDUCED4:
- winner **PIT USD/CNY**
- ΔΣAE **+32.6812 / +2.28%**
- direction remains **24/33**

#### CATBOOST_PRICE
Winner **PIT USD/CNY**:
- ΔΣAE **+32.0153 / +2.19%**
- direction remains 20/33.
Rates and CPI also pass.

#### LMC2_RBF_M32 / EPSILON_RBF_DAILY12
No tested external block passes the robustness gate.
These stay as **BASE controls** for the current external-information family.

### 20E.4 Interpretation boundary

This section proves **incremental external-information value on frozen model forecast residuals**.

It does **not** establish native architecture augmentation.

Reason native integration is not yet authorized:
- current governed CPI/rates/FX compact snapshots do not cover the full historical training span used by the base models;
- zero-filling early history or using unreconstructed revised history would violate the causal comparison.

Native integration requires a new long-history origin-safe external snapshot before retraining.

### 20E.5 Native-integration priority after long-history backfill

1. **ChHHO + headline CPI surprise**
2. **DE-ABC + PIT rates**
3. **PLS1 + PIT rates**
4. **FULL7 ANN + PIT USD/CNY**
5. **REDUCED4 ANN + PIT USD/CNY**
6. **CATBOOST_PRICE + PIT USD/CNY**
7. LMC2 and DAILY12-SVR remain BASE controls unless a new external family supplies a pre-outcome rationale.

---

## 4.7 Data readiness for scientific feature architecture

### 20G.0 F4 reset supersession note

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

### 20G.1 Ready data families

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

### 20G.2 Scientific use boundary

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

### 20G.3 Active next stage

The current active model-development task is no longer a new structural family.

**Active next: ChHHO-ANFIS feature-architecture audit, beginning F0 → F1, then F2 → F3 → F4.**

CNN-BiLSTM remains structurally eligible/deferred and does not override the user's current feature/data research priority.

---

## 4.8 F0/F1 feature-necessity audit

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

## 4.9 F2 representation audit

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

## 4.10 F3 lag-architecture audit

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

## 4.11 F4 Rates legacy endpoint representation

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

## 4.12 F4 processing / frequency / optimizer reset and family audits

**Status: ACTIVE / BINDING / MODEL RUNS PAUSED UNTIL DATA+TRANSFORM GATES PASS**

Detailed authority:
`gold_axis_2026/GOLD_MONTHLY_F4_RESET_PROCESSING_PARITY_AUDIT_2026-09-29.md`

### 20L.1 Why F4 was reset

The first F4 native Rates/FX lane was computationally valid for its exact implementation, but later audit identified three design mismatches:

1. **Processing parity defect:** daily external series were mostly compressed to endpoint-to-endpoint monthly changes rather than CURRENT8-style monthly representation + GPR-conditioned daily-path summary.
2. **Frequency under-use:** daily Nasdaq-100 and daily WTI/Brent were not yet governed even though daily source histories can be obtained; VIX/Rates/FX already had daily authority.
3. **Optimizer-dimension parity defect:** ChHHO kept POP=24 while antecedent dimension increased from 80 to 90/100+, reducing search effort per optimized parameter.

Standardization itself was present and is **not** the main defect.

### 20L.2 Legacy evidence status

#### Rates legacy native
- run **36550570628**
- BASE parity **1413.029779 / 23/33 PASS**
- routed result **1657.1153 / 21/33**
- status: **VALID_FOR_LEGACY_ENDPOINT_REPRESENTATION_ONLY / SUPERSEDED_FOR_FAMILY_DECISION**

#### FX legacy native
- run **36552598677**
- artifact **11026195076**
- digest `sha256:db389252b953b252a3a0b33fefbbc00c8e2df757ef53f25c64fcf254442d1a56`
- BASE parity **1413.029779 / 23/33 PASS**
- routed result **1811.986846 / 18/33**
- status: **VALID_FOR_LEGACY_ENDPOINT_REPRESENTATION_ONLY / SUPERSEDED_FOR_FAMILY_DECISION**

Detailed FX record:
`gold_axis_2026/GOLD_MONTHLY_CHHHO_F4_FX_LEGACY_RESULT_2026-09-29.md`

Earlier residual-correction screens remain valid for the separate residual-correction architecture and are not native-input evidence.

### 20L.3 New apple-to-apple external feature contract

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

### 20L.4 Optimizer parity

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

### 20L.5 External Authority V2

V2 must preserve the existing official H.10/H.15/VIX/CPI/World-Bank evidence and close these gaps:

- daily Nasdaq-100 authority;
- daily WTI authority;
- daily Brent authority;
- CPI prehistory sufficient for 2010-era YoY transforms;
- World Bank prehistory sufficient for canonical 2010-03 training parity.

Technical provider failures during V2 construction are **NOT MODEL RESULTS**.

### 20L.5A External Authority V2 — COMPLETE

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

### 20L.5B B1 transform parity — COMPLETE

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

### 20L.5C B2 processing + optimizer parity — COMPLETE

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

### 20L.6 ALL6-COMPACT diagnostic — COMPLETE / NOT PROMOTED

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

### 20L.6A Rates parity family decomposition — COMPLETE / COMBINED BLOCK NOT PROMOTED

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

### 20L.6B Rates R1 compact real-yield redesign — COMPLETE / NOT PROMOTED

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_F4_RATES_R1_REAL_YIELD_RESULT_2026-09-29.md`

R1 representation:
- one Rates feature only: `REAL10_MONTHLY_MEAN_DIFF = mean(REAL10[p]) - mean(REAL10[p-1])`
- nominal yield **NOT USED**
- Rates daily VW **NOT USED**
- GPR weighting on Rates **NOT USED**
- total inputs **9**
- antecedent parameter dimension **90**
- POP **27**
- generations **45**
- repeats **3**
- downstream chronological scaling / ANFIS / local-refit unchanged

Authoritative execution:
- workflow **Gold Monthly F4 Rates R1 Real Yield V1**
- run **36570943295**
- head commit **472db002a6f6fb6fb3700623386416179ca76aa0**
- 6/6 DEV shards **SUCCESS**
- summarize **SUCCESS**
- summary artifact **11033588984**
- summary digest `sha256:050e47f0c94711c7a73c8c5204e2c7734327de6301589607bf407a167c95842e`

DEV:
- BASE **1413.0297794084559 / 23/33**
- R1 **1837.6351578352678 / 19/33**
- ΣAE deterioration vs BASE **+424.605378426812 USD**
- relative deterioration **+30.05%**
- direction change **-4**
- paired wins/losses/ties **14 / 19 / 0**
- median paired improvement (BASE − R1) **-7.2854732528**
- worst R1 month **2024-03**, AE **154.8141711720**
- signed mean bias **-8.3247270751**

Yearly:
- 2022: BASE **397.8794** vs R1 **509.7708**
- 2023: BASE **395.7140** vs R1 **635.9704**
- 2024: BASE **619.4364** vs R1 **691.8939**

Representation diagnosis:
- earlier Rates(4) block: **6102.555639186698 / 16/33**
- R1: **1837.6351578352678 / 19/33**
- compacting Rates(4) → R1 reduces ΣAE by **4264.92048135143 USD**
- relative improvement versus Rates(4): **69.89%**
- direction recovers **+3 correct months**

Decision:
- R1 **VALID / NOT PROMOTED**
- Rates-no-signal conclusion **NOT AUTHORIZED**
- hypothesis that prior Rates failure was materially driven by representation/dimensionality **SUPPORTED**
- 2025/2026 remain closed
- next pre-outcome Rates redesign is **R2 orthogonal pair**:
  1. monthly real-yield change,
  2. monthly breakeven-inflation change = nominal10 − real10,
  with **10 total inputs / D100 / POP30 / 45 generations / 3 repeats**.
- R2 **NOT RUN YET**.
- FX remains **NOT STARTED**.

### 20L.6C Rates R2 orthogonal pair — COMPLETE / FAMILY CLOSED

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_F4_RATES_R2_FAMILY_CLOSURE_2026-09-29.md`

R2 representation:
- monthly real-yield mean change
- monthly 10Y breakeven-inflation change = nominal10 − real10
- daily Rates VW **NOT USED**
- GPR weighting on Rates **NOT USED**
- total inputs **10**
- antecedent parameter dimension **100**
- POP **30**
- generations **45**
- repeats **3**

Authoritative execution:
- workflow **Gold Monthly F4 Rates R2 Orthogonal Pair V1**
- run **36572341391**
- head commit **17e61eb4819120419f003194a8dd50e039978abc**
- 6/6 DEV shards **SUCCESS**
- summarize **SUCCESS**
- summary artifact **11036170615**
- summary digest `sha256:087b2d6f62ba486d872dc5f1d4f8d8eb5549a6bd778d18aa474c7b9c7757456a`

Earlier run **36572222708** failed before scientific scoring because of a helper unpack bug; it is **TECHNICAL_IMPLEMENTATION_FAILURE / NOT_SCIENTIFIC_RESULT**.

DEV:
- BASE **1413.0297794084559 / 23/33**
- R2 **1716.9570365398133 / 19/33**
- ΣAE deterioration vs BASE **+303.92725713135746 USD**
- relative deterioration **+21.51%**
- direction change **-4**
- paired wins/losses/ties **15 / 18 / 0**
- median paired improvement (BASE − R2) **-8.6342994027**
- worst month **2024-03**, AE **140.2185519019**
- signed mean bias **-13.6002083193**

Yearly:
- 2022: BASE **397.8794** vs R2 **509.6601**
- 2023: BASE **395.7140** vs R2 **521.6554**
- 2024: BASE **619.4364** vs R2 **685.6415**

Rates redesign sequence:
- Rates(4) **6102.555639 / 16/33**
- R1 real-yield only **1837.635158 / 19/33**
- R2 real-yield + breakeven **1716.957037 / 19/33**
- R2 improves on R1 by **120.678121 USD**, but remains materially worse than BASE.

Decision:
- Rates R2 **VALID / NOT PROMOTED**
- native F4 Rates family **CLOSED / NOT PROMOTED**
- no further Rates native-input redesign
- 2025/2026 remain closed for these rejected Rates variants
- prior PIT Rates residual-layer evidence in other architectures remains historical evidence and is not deleted
- next external family: **FX**
- FX execution status: **NOT STARTED**

### 20L.6D FX1 Broad USD compact monthly representation — COMPLETE / NOT PROMOTED

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_F4_FX1_BROADUSD_RESULT_2026-09-29.md`

FX1 representation:
- one FX feature only: `log(mean(BROADUSD[p]) / mean(BROADUSD[p-1]))`
- source: Fed H.10 Broad USD index
- sign: positive = USD strengthening
- H.10 release cutoff **7 calendar days**
- daily FX VW **NOT USED**
- GPR weighting on FX **NOT USED**
- total inputs **9**
- antecedent parameter dimension **90**
- POP **27**
- generations **45**
- repeats **3**
- same chronological training-only scaling / ChHHO-ANFIS / local-refit path as BASE

Authoritative execution:
- workflow **Gold Monthly F4 FX1 Broad USD V1**
- run **36573963802**
- head commit **d89713432f54877c551b2b120ab63a655de26b37**
- 6/6 DEV shards **SUCCESS**
- summarize **SUCCESS**
- summary artifact **11036118411**
- summary digest `sha256:e8b222298bb25b49140cf2f3b77369641c1c9aba2b1e351a26948a0e8950d33f`

DEV:
- BASE **1413.0297794084559 / 23/33**
- FX1 **2532.59355901361 / 20/33**
- ΣAE deterioration vs BASE **+1119.5637796051542 USD**
- relative deterioration **+79.23%**
- direction change **-3**
- paired wins/losses/ties **13 / 20 / 0**
- median paired improvement (BASE − FX1) **-12.2449977274**
- worst month **2022-04**, AE **769.8660852655**
- signed mean bias **-34.9539510109**

Yearly:
- 2022: BASE **397.8794** vs FX1 **1278.0632**
- 2023: BASE **395.7140** vs FX1 **568.4122**
- 2024: BASE **619.4364** vs FX1 **686.1182**

Decision:
- FX1 **VALID / NOT PROMOTED**
- FX family-wide rejection **NOT AUTHORIZED**
- monthly Broad USD level-change alone does not add DEV value
- daily FX path remains untested in this compact family lane
- 2025/2026 remain closed
- next FX-only test should use **BROADUSD_MR1 + one daily-path scalar**, with total inputs **10 / D100 / POP30**, before any family closure.
- VIX/Nasdaq/Energy remain not started.

### 20L.6E FX2 Broad USD daily-path volatility — COMPLETE / NOT PROMOTED

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_F4_FX2_BROADUSD_DAILY_PATH_RESULT_2026-09-29.md`

FX2 representation:
- Broad USD monthly mean log change
- Broad USD intramonth daily RMS log-return volatility
- source: Fed H.10 Broad USD index
- H.10 release cutoff **7 calendar days**
- GPR weighting on FX **NOT USED**
- total inputs **10**
- antecedent parameter dimension **100**
- POP **30**
- generations **45**
- repeats **3**
- same chronological training-only scaling / ChHHO-ANFIS / local-refit path as BASE

Authoritative execution:
- workflow **Gold Monthly F4 FX2 Broad USD Daily Path V1**
- run **36575331412**
- head commit **d6f1fe245587bbcd82cf4d4ffdbaf4f53378b182**
- 6/6 DEV shards **SUCCESS**
- summarize **SUCCESS**
- summary artifact **11037330894**
- summary digest `sha256:a14e70151f71d3ed1561b5f85f0d4d0c0a976317f919f746032436a1dd14da36`

DEV:
- BASE **1413.0297794084559 / 23/33**
- FX2 **1787.6000747067567 / 17/33**
- ΣAE deterioration vs BASE **+374.57029529830083 USD**
- relative deterioration **+26.51%**
- direction change **-6**
- paired wins/losses/ties **14 / 19 / 0**
- median paired improvement (BASE − FX2) **-10.0237615596**
- worst month **2023-10**, AE **147.5005218662**
- signed mean bias **-12.6547936971**

Yearly:
- 2022: BASE **397.8794** vs FX2 **497.9771**
- 2023: BASE **395.7140** vs FX2 **668.6240**
- 2024: BASE **619.4364** vs FX2 **620.9990**

FX sequence:
- FX1 monthly Broad USD only **2532.593559 / 20/33**
- FX2 monthly Broad USD + daily RMS volatility **1787.600075 / 17/33**
- FX2 improves ΣAE over FX1 by **744.993484 USD**, but still does not beat BASE.

Decision:
- FX2 **VALID / NOT PROMOTED**
- FX family-wide rejection **NOT YET AUTHORIZED**
- daily volatility path materially repairs FX1 price error, especially by 2024, but direction degrades
- a true compact daily directional MIDAS path remains untested
- next FX-only test: **FX3 Broad USD MR1 + training-only parsimonious MIDAS-weighted daily return scalar**, no GPR weighting and no extra currency pairs
- 2025/2026 remain closed
- VIX/Nasdaq/Energy remain not started.

### 20L.6F FX3 directional Almon-MIDAS — COMPLETE / FX FAMILY CLOSED

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_F4_FX3_FAMILY_CLOSURE_2026-09-29.md`

FX3 representation:
- Broad USD monthly mean log change
- one directional daily Broad USD return scalar
- daily scalar uses parsimonious exponential-Almon MIDAS weighting
- MIDAS weight selection occurs only inside the ANFIS inner-train pool; ANFIS validation remains untouched
- no GPR weighting
- no additional currency pairs
- total inputs **10**
- antecedent parameter dimension **100**
- POP **30**
- generations **45**
- repeats **3**

Authoritative execution:
- workflow **Gold Monthly F4 FX3 Directional MIDAS V1**
- run **36576876579**
- head commit **ea2bd5c5a119929ef448d6853941b89f5e056337**
- 6/6 DEV shards **SUCCESS**
- summarize **SUCCESS**
- summary artifact **11037952667**
- summary digest `sha256:d0a553ffa7caaa4119143dacfebb9292338378832722e1537da60c2a5a222842`

DEV:
- BASE **1413.0297794084559 / 23/33**
- FX3 **1829.800218215398 / 20/33**
- ΣAE deterioration vs BASE **+416.77043880694214 USD**
- relative deterioration **+29.49%**
- direction change **-3**
- paired wins/losses/ties **13 / 20 / 0**
- median paired improvement (BASE − FX3) **-6.7261486840**
- worst month **2024-04**, AE **170.1781399883**
- signed mean bias **-13.3699152671**

Yearly:
- 2022: BASE **397.8794** vs FX3 **474.9862**
- 2023: BASE **395.7140** vs FX3 **636.4662**
- 2024: BASE **619.4364** vs FX3 **718.3478**

MIDAS weight-selection diagnostic:
- (-8, 0): **26/33 origins**
- (0, 0): **4/33**
- (-1, 0): **1/33**
- (1, -2): **1/33**
- (2, -2): **1/33**

The dominant selection is the strongest recency-decay candidate, so the daily FX path tends to prefer the newest available Broad USD returns. The resulting directional scalar still does not beat BASE.

FX sequence:
- FX1 monthly Broad USD **2532.593559 / 20/33**
- FX2 monthly + daily RMS volatility **1787.600075 / 17/33**
- FX3 monthly + directional Almon-MIDAS **1829.800218 / 20/33**
- BASE remains **1413.029779 / 23/33**

Decision:
- FX3 **VALID / NOT PROMOTED**
- native F4 FX family **CLOSED / NOT PROMOTED**
- no further native-input FX redesign by default
- 2025/2026 remain closed for rejected FX variants
- historical residual-layer/USD-CNY evidence from other architectures remains historical and is not deleted
- next external family: **VIX**
- VIX execution status: **NOT STARTED**
- Nasdaq/Energy remain not started.

### 20L.6G Hard raw-data re-audit — COMPLETE / PASS

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_F4_FX_RATES_HARD_DATA_REAUDIT_2026-09-29.md`

Purpose:
- determine whether the poor native-input Rates/FX results could be explained by bad source rows, date shifts, missing observations, stale frozen data, or transform arithmetic errors.

Authority:
- fresh direct **Federal Reserve Board DDP** re-fetch
- workflow **Gold Monthly F4 FX Rates Direct DDP Reaudit V1**
- run **36580341003**
- head commit **3d8ca815ede86fd8b7ad694d0a58be0278b13e22**
- job **109446532518**
- result artifact **11038493043**
- digest `sha256:a24c1ed64097eeb4c25055695ff34b8785da1815de8c57093e95e2cd6427be20`
- overall gate **PASS**

Raw package hashes:
- H.10 index package SHA256: **EXACT MATCH**
- H.10 rates package SHA256: **EXACT MATCH**
- H.15 package SHA256: **EXACT MATCH**

Full daily-series parity:
- Broad USD: **4167/4167 common**, 0 missing dates, 0 mismatches, max abs diff **0.0**
- nominal 10Y: **4186/4186 common**, 0 missing dates, 0 mismatches, max abs diff **0.0**
- real 10Y: **4186/4186 common**, 0 missing dates, 0 mismatches, max abs diff **0.0**

All 33 DEV-origin transforms were independently recomputed from the fresh Board DDP data:
- Broad USD MR1 max diff **0.0**
- Broad USD daily RMS volatility max diff **0.0**
- nominal 10Y monthly difference max diff **0.0**
- real 10Y monthly difference max diff **0.0**
- 10Y breakeven monthly difference max diff **0.0**

Conclusion:
- **NO EVIDENCE OF RAW-DATA OR TRANSFORM ERROR** in the governed Rates/FX inputs.
- native Rates/FX degradation is therefore classified as **MODEL / REPRESENTATION / GENERALIZATION**, not a demonstrated data-quality failure.
- B0/B1/B2 and Rates/FX family closures remain valid.
- earlier FRED-distribution reaudit run 36578797117 failed only on download timeout before comparison; later FRED network attempts are non-authority because the stronger direct Board DDP audit supersedes them.
- next unopened family remains **VIX**.

### 20L.6H ChHHO PIT Rates residual exact replication — COMPLETE / PASS

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_CHHHO_PIT_RATES_RESIDUAL_REPLICATION_2026-09-29.md`

Purpose:
- re-run the previously successful Rates residual-correction method **without redesigning it**;
- distinguish native-input failure from residual-layer usefulness.

Exact historical method:
- frozen ChHHO-ANFIS authority artifact **10989389723**
- strict-PIT Rates block:
  - `dgs10_change`
  - `dff_change`
  - `curve_proxy_change = delta(DGS10-DFF)`
- correction target: **price residual = actual price − BASE forecast price**
- learner: **Ridge(alpha=10)**
- StandardScaler fit on prior eligible residual rows only
- minimum prior residuals **12**
- correction cap **±1.5 × median(abs(prior residual))**
- prequential chronology: prior DEV residuals only
- random split **NONE**
- 2025 selection/tuning **NONE**
- Neon reads **0**

Authoritative replication:
- workflow **Gold Monthly ChHHO PIT Rates Residual Replication V1**
- run **36581036837**
- head commit **46fa4d92cc3b72efb87f2d1624758884e48defb0**
- job **109448965788**
- result artifact **11038844070**
- artifact digest `sha256:3db616642fc285fff2c0357994bc8ab8390e6f65c24dc87380e2a5ac2cebf34b`
- replication gate **PASS**

Exact reproduced DEV:
- frozen historical BASE **1413.0298545342782 / 23/33**
- PIT Rates residual corrected **1370.9203928352813 / 23/33**
- full DEV improvement **42.10946169899694 USD**
- relative improvement **2.98%**
- first eligible corrected target **2023-04**
- eligible-period BASE ΣAE **843.2884386436745**
- eligible-period corrected ΣAE **801.1789769446775**
- improvement excluding single best month **17.922324074458402 USD**
- 2024 improvement **62.622909991857114 USD**
- stability gate **PASS**

The historical frozen BASE differs from the current canonical BASE by only about **0.000075 USD** in ΣAE; the old result reproduces exactly within the frozen tolerance.

Interpretation:
- **native-input Rates remains CLOSED / NOT PROMOTED**
- **Rates residual correction is REPRODUCED / VALID**
- therefore Rates contains architecture-specific incremental information, but direct expansion of the ChHHO native input space is the wrong tested integration path
- direct Board DDP hard-data audit remains PASS with max daily/transform diff **0.0**
- next clean enhancement test, if pursued, is the **same frozen PIT Rates price-residual protocol applied to the current canonical ChHHO BASE rows**, with no hyperparameter redesign
- VIX native family remains unopened.

### 20L.6I ChHHO VIX residual screen — COMPLETE / VIX_R1 PASS

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_CHHHO_VIX_RESIDUAL_SCREEN_2026-09-29.md`

Frozen design:
- BASE: frozen ChHHO-ANFIS authority artifact **10989389723**
- residual target: **actual price − BASE forecast price**
- learner: **Ridge(alpha=10)**
- StandardScaler on prior eligible residual rows only
- minimum prior residuals **12**
- correction cap **±1.5 × median(abs(prior residual))**
- chronology **prequential / prior DEV residuals only**
- VIX daily authority: External Authority V2 / **READY_CBOE**
- VIX release safety lag: **1 calendar day**
- 2025/2026 selection: **NONE**
- Neon reads: **0**

Predeclared VIX variables:
- `VIX_LEVEL`: origin-month mean daily VIX
- `VIX_CHANGE`: origin mean minus previous-month mean
- `VIX_VOL`: std of origin-month daily VIX first differences
- `VIX_SPIKE`: origin-month max VIX / origin-month mean VIX

Predeclared blocks and DEV results:
- **VIX_R1_CHANGE**: **1338.330045 / 23/33**, improvement **74.699809 USD / 5.2865%**, gate **PASS**
- **VIX_R2_LEVEL_CHANGE**: **1345.909122 / 23/33**, improvement **67.120733 USD / 4.7501%**, gate **PASS**
- **VIX_R3_FULL_STRESS**: **1407.226258 / 24/33**, improvement **5.803597 USD / 0.4107%**, gate **FAIL**

Selected:
**VIX_R1_CHANGE**

VIX_R1 robustness:
- eligible BASE ΣAE **843.2884386436745**
- eligible corrected ΣAE **768.5886293661572**
- eligible improvement **74.69980927751726 USD**
- excluding the single best month improvement **53.471601696024436 USD**
- 2024 improvement **62.05453990225692 USD**
- eligible Direction **14/21 → 14/21**
- robustness gate **PASS**

Authoritative execution:
- workflow **Gold Monthly ChHHO VIX Residual Screen V1**
- run **36585834751**
- head commit **3c23d018f3c23b47c36d4ac21327be400c250339**
- job **109465773517**
- artifact **11041975865**
- artifact digest `sha256:e864e30908658f9edc2e9ece8e8070d2d7c06c0d0a52ea7919f98385a7bf66f2`

Earlier run **36585727221** failed before scientific execution only because the runtime lacked `psycopg`; no scientific parameter or feature definition was changed.

Decision:
- VIX residual information is **SUPPORTED**
- **VIX_R1_CHANGE = PROMOTABLE CHALLENGER**
- R2 valid but dominated by R1
- R3 rejected by robustness gate
- native-input VIX remains **NOT YET TESTED**
- 2025/2026 transport for VIX_R1 is now **COMPLETE**
- frozen VIX_R1 transport result:
  - 2025 BASE **1252.054159 / 9/12** → corrected **1082.027319 / 9/12**
  - 2025 ΣAE improvement **170.026841 USD / 13.58%**
  - 2026 Jan-Aug BASE **1526.133212 / 5/8** → corrected **1526.048523 / 6/8**
  - 2026 Jan-Aug ΣAE improvement only **0.084689 USD**, Direction **+1**
  - September 2026 canonical ChHHO remains **BLOCKED** because August four-metal origin inputs are incomplete
- transport interpretation: strong 2025 out-of-sample value, effectively zero aggregate 2026 price-error gain, but one additional correct direction in 2026
- next clean action is **native-input VIX challenge** if authorized; do not retune VIX_R1 on 2025/2026.

### 20L.6J VIX_R1 frozen transport — COMPLETE / 2025 STRONG, 2026 FLAT

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_CHHHO_VIX_R1_FROZEN_TRANSPORT_2025_2026_2026-09-29.md`

Authoritative execution:
- workflow **Gold Monthly ChHHO VIX R1 Frozen Transport 2025 2026 V1**
- run **36587033148**
- head commit **acfee6fdc0c7b41e874e7a166d5376cba74bf9bb**
- job **109469978233**
- artifact **11042740289**
- artifact digest `sha256:5d6966e470412675af649c1fc869b32fadb9b0252be27f6b5fec4307716aa285`

Frozen fit:
- n **33**
- Ridge alpha **10**
- cap **53.266887317887495**
- standardized VIX_CHANGE coefficient **2.3347459307325407**
- intercept **13.690850943418237**
- 2025/2026 residual updating **NONE**

2025:
- BASE ΣAE **1252.0541594740248**, Direction **9/12**
- corrected ΣAE **1082.0273188083147**, Direction **9/12**
- improvement **170.0268406657101 USD / 13.58%**

2026 Jan-Aug:
- BASE ΣAE **1526.1332118229584**, Direction **5/8**
- corrected ΣAE **1526.0485229389474**, Direction **6/8**
- improvement **0.08468888401102959 USD**
- Direction change **+1**
- August BASE **4063.0063** → corrected **4076.2610** vs actual **4411.00**; direction flips from wrong to correct
- September canonical ChHHO **BLOCKED**

Decision:
- VIX_R1 remains a valid residual challenger
- 2025 transport is strongly supportive
- 2026 aggregate price-error gain is effectively zero
- do not claim universal stability
- do not retune on 2025/2026
- native-input VIX remains not yet tested.

### 20L.6K Brent residual + Rates combination — COMPLETE

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_CHHHO_BRENT_RESIDUAL_AND_RATES_COMBINATION_2026-09-29.md`

Brent isolated residual screen:
- BASE **1413.029855 / 23/33**
- **BRENT_R1_MR1** **1346.502415 / 23/33**, improvement **66.527439 USD**, gate **PASS**
- **BRENT_R2_VW** **1349.180909 / 23/33**, improvement **63.848945 USD**, gate **PASS**
- **BRENT_R3_MR1_VW** **1357.706180 / 23/33**, improvement **55.323674 USD**, gate **PASS**
- selected Brent representation: **BRENT_R1_MR1**
- R1 improvement excluding single best month **49.835209 USD**
- R1 2024 improvement **60.713525 USD**

Brent authoritative execution:
- run **36590486319**
- head **f2eb03085e42005a3902dd278d94f17544675e1b**
- job **109481990464**
- artifact **11043268953**
- digest `sha256:014754f03dc8f754cce60d385f98146c0ef8094a760940d13564633706b77c27`

Rates + Brent combination:
- Rates control **1370.920393 / 23/33**
- Brent control **1346.502415 / 23/33**
- Rates + Brent **1377.101415 / 23/33**
- combined robustness gate **PASS**
- combined is worse than Brent alone by **30.599000 USD**
- combined is worse than Rates alone by **6.181022 USD**
- combination decision: **REJECTED / DOMINATED**

Combination authoritative execution:
- run **36590746098**
- head **b67b1dad7c816a3869f96e22661d4b44e50772c3**
- job **109482871506**
- artifact **11043503614**
- digest `sha256:d7d457fb82b5f55dedc9d1dbac50ba38271b0436be650424a0b486242ad86f81`

Decision — superseded by mandatory bias-only attribution control in §20L.6L:
- Brent improves versus raw BASE but **does not beat BIAS_ONLY on DEV**
- **BRENT_R1_MR1 is NOT promoted as an independent external residual driver**
- Rates + Brent stacking is **NOT PROMOTED**
- frozen Brent transport was completed for diagnosis only; holdout results do not rescue DEV attribution failure.

### 20L.6L Residual attribution bias-only control — COMPLETE / BINDING

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_CHHHO_RESIDUAL_ATTRIBUTION_BIAS_CONTROL_2026-09-29.md`

Reason:
- every Ridge residual model includes an intercept;
- frozen ChHHO DEV mean price residual is **+13.690850943418237 USD**;
- therefore BASE-relative improvement alone can falsely attribute a systematic bias correction to an external variable.

Mandatory control:
- **BIAS_ONLY** = prior mean residual under the same 12-history minimum and same cap;
- prequential on DEV;
- frozen full-DEV mean residual for 2025/2026 transport;
- no external variables.

Authoritative bias-only execution:
- workflow **Gold Monthly ChHHO Residual Bias Only Control V1**
- run **36591365527**
- head **dfb1f2800bd6e7223e6ba0ecee6ac006ae8b4937**
- job **109485005513**
- artifact **11044715151**
- digest `sha256:ecef7244d7dc3860b0c62da76cefe589eeaba6dad104d24601a3965b96c24300`

BIAS_ONLY:
- DEV BASE **1413.029855 / 23/33**
- DEV BIAS_ONLY **1338.893512 / 23/33**
- improvement **74.136343 USD**
- robustness gate **PASS**
- 2025 **1252.054159 → 1095.749344**
- 2026 Jan-Aug **1526.133212 → 1526.133212** (effectively zero ΣAE change), Direction **5/8 → 6/8**

Corrected external attribution on DEV:
- **VIX_R1_CHANGE**: **1338.330045**, only **0.563467 USD better than BIAS_ONLY**
- **BRENT_R1_MR1**: **1346.502415**, **7.608904 USD worse than BIAS_ONLY**
- **PIT Rates**: **1370.920393**, **32.026881 USD worse than BIAS_ONLY**
- **Rates + Brent**: **1377.101415**, **38.207903 USD worse than BIAS_ONLY**

Brent frozen transport diagnostic:
- run **36591080686**
- artifact **11043592796**
- 2025 Brent **1096.152741** vs BIAS_ONLY **1095.749344** → Brent **0.403396 USD worse**
- 2026 Jan-Aug Brent **1521.188957** vs BIAS_ONLY **1526.133212** → Brent **4.944255 USD better**
- 2026 transport is retrospective only and cannot override DEV attribution failure.

Binding methodological correction:
- all future residual external-driver screens must pass **two** tests:
  1. BASE robustness gate;
  2. **incremental improvement versus BIAS_ONLY**.
- old BASE-relative language saying Rates/Brent/VIX residual gains are external-variable gains is superseded wherever inconsistent with this control.
- Brent residual external attribution: **NOT PROMOTED**
- Rates + Brent: **NOT PROMOTED**
- VIX_R1: only **marginal DEV incremental value** beyond bias-only.
- PIT Rates: not a DEV-supported external winner after bias control, despite positive 2026 retrospective behavior.

### 20L.6M Brent expanded residual screen — COMPLETE / NO ROBUST PROMOTION

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_CHHHO_BRENT_EXPANDED_RESIDUAL_SCREEN_2026-09-29.md`

Frozen variables:
- `BRENT_MR1`
- `BRENT_VW`
- `BRENT_RVOL`
- `BRENT_DOWNSIDE_VOL`
- `BRENT_MAX_DD`

No raw Brent price level was used.

Mandatory benchmark:
- BIAS_ONLY **1338.893512 / 23/33**

DEV results:
- B1 MR1 **1346.502415 / 23/33**, incremental vs bias **-7.608904**, FAIL
- B2 MR1+RVOL **1332.365899 / 23/33**, incremental **+6.527612** but excl-best-month **-1.219005**, FAIL
- B3 MR1+DOWNSIDE **1330.832804 / 23/33**, incremental **+8.060708** but excl-best-month **-1.265988**, FAIL
- B4 MR1+MAXDD **1359.785146 / 23/33**, FAIL
- B5 MR1+RVOL+DOWNSIDE+MAXDD **1347.836087 / 23/33**, FAIL
- B6 ALL5 **1354.323041 / 23/33**, FAIL

Important:
- all six blocks pass the old BASE-relative gate;
- **none** passes the binding incremental-vs-BIAS_ONLY robustness gate;
- best numerical block B3 depends too heavily on one favorable DEV month.

Decision:
- **no Brent residual block promoted**
- Brent simple feature expansion is exhausted under the current residual Ridge protocol
- do not transport B3 as a selected challenger
- next residual family should be WTI or Nasdaq, using the same mandatory BIAS_ONLY gate.

Authoritative execution:
- workflow **Gold Monthly ChHHO Brent Expanded Residual Screen V1**
- run **36593458061**
- head **b00e410dadcf24fb5c8a1ba2f4d05240be5ad8b8**
- job **109492222857**
- artifact **11045435477**
- digest `sha256:c3af6e6e550f849bcc2c6e63db4e7d943ae829999c80176d26347891e5fcbfff`

### 20L.6N Cross-model error overlap / router viability — COMPLETE

Detailed record:
`gold_axis_2026/GOLD_MONTHLY_CROSS_MODEL_ERROR_OVERLAP_ROUTER_VIABILITY_2026-09-29.md`

Purpose:
- determine whether ChHHO's large-error DEV months are also large-error months for essentially all other models;
- quantify whether a side-model/router has any ex-post rescue capacity before opening a new gate model.

Evidence:
- exact per-origin DEV rows from **24 models**
- competitive pool **16 models**, frozen rule: DEV ΣAE <= 1.15 × ChHHO
- DEV only 2022-04..2024-12
- no 2025/2026 selection.

ChHHO:
- DEV ΣAE **1413.029779**
- worst 8 months contribute **747.086 USD ≈ 52.9%** of total error.

Key overlap:
- 2024-03: **16/16** competitive models also top-8; best rescue only **5.47 USD**
- 2022-07: **14/16**; best rescue only **1.76 USD**
- 2024-11: **15/16**, but CNN-LSTM LB6 still reduces AE **119.13 → 62.99**
- 2023-01: 12/16; best AE **29.59** vs ChHHO **100.74**
- 2022-11: 10/16; **15/15 alternatives beat ChHHO**, best AE **43.74** vs **102.20**
- 2023-08: only **3/16** top-8; **14/15 alternatives beat ChHHO**, best AE **22.36** vs **77.53**
- 2024-07: 10/16; best AE **44.75** vs **71.01**

Fixed fallback diagnostic on exactly ChHHO's known worst 8 months:
- CNN-LSTM LB6: **588.89**, improvement **158.19**, wins **6/8**
- LMC2-RBF M32: **626.30**, improvement **120.79**, wins **7/8**
- REDUCED4 ANN: **639.09**, improvement **108.00**, wins **6/8**
- PLS1: **654.80**, improvement **92.28**, wins **7/8**

Diversity:
- CNN-LSTM LB6 has the lowest AE correlation with ChHHO in the competitive pool, about **0.588**; signed-error correlation about **0.767**.

Oracle ceiling — diagnostic only, not deployable:
- perfect hindsight best competitive model each month: **704.522 ΣAE**
- if hindsight switching only on ChHHO worst 8: total **1120.839**, theoretical gain **292.191**.

Binding interpretation:
- the claim “all strong models fail on the same months” is **NOT supported**;
- failure structure is mixed: some shared-hard months, plus meaningful ChHHO-specific / model-specific failure months;
- router hypothesis remains **VIABLE**, but complementarity shown here is strictly **ex-post**;
- no side model is promoted from this table alone;
- next valid stage is an **origin-safe error-risk / rescueability gate**, initially with **no price switching**. Only if prequential risk/rescue prediction works may a fallback router be tested.

Authority:
- workflow **Gold Monthly Cross Model Error Overlap V1**
- run **36600141673**
- head **ee82eb25cb4017e9f59d38affeee27304f32ea7a**
- job **109515089218**
- artifact **11049132605**
- digest `sha256:baa25ab1ee06130bdf188cde96be00ee9a8344b5e7a6c609ada996dfd8bec414`

### 20L.7 Workflow hold

Legacy workflows:
- `.github/workflows/gold-monthly-chhho-f4-rates-v1.yml`
- `.github/workflows/gold-monthly-chhho-f4-fx-v1.yml`

are on **MANUAL LEGACY HOLD**.

Current exact active stage:
**Cross-model error-overlap audit COMPLETE. Large-error months are not universally shared: some are common-hard, while several ChHHO failures are materially rescued by frozen alternatives. Router hypothesis remains viable. Next valid stage is an origin-safe error-risk / rescueability gate with no price switching in Stage 1.**

---
