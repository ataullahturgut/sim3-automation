# GOLD MONTHLY FORECAST — EXTERNAL DRIVER RESEARCH FINAL RESULT

**Date:** 2026-09-28  
**Status:** X0-X6 COMPLETED / X7 OPTIONAL-DEFERRED  
**Role:** Parallel feature-information research track  
**Base models:** ChHHO-ANFIS and DE-ABC-RBFNN  
**Selection authority:** DEV 2022-04..2024-12 only  
**2025 role:** frozen transport/reporting only

## 1. Final answer

The external-information hypothesis is **SUPPORTED**.

Origin-safe external information reduces out-of-sample forecast error for both retained strong Gold Monthly models, but the useful external channel is model-specific:

- **ChHHO-ANFIS:** strongest DEV-authorized external correction = **headline CPI surprise**.
- **DE-ABC-RBFNN:** strongest DEV-authorized external correction = **rates block**.
- **FX/global currency information is materially useful for ChHHO**, but does not beat CPI surprise on the DEV selection authority.
- **Broad/major FX does not pass as a robust promotion block for DE-ABC.**

This result does **not** mean the base architectures have already been retrained with external inputs. The experiment uses a chronology-safe residual-correction layer on top of frozen base forecasts to isolate incremental external information.

## 2. Governance

- Random split: NONE
- Base models: frozen / unchanged
- Feature/block selection: DEV only
- 2025 used for tuning/selection: NO
- 2025 rescue after seeing result: NO
- Neon writes: NONE
- Repeated full Neon historical download: NONE
- Risk-appetite promotion: blocked due insufficient original PIT-storage proof
- Commodity/oil: DATA_NOT_READY
- General FRED fredgraph path: provider timeout; superseded for FX by official Federal Reserve H.10 DDP

## 3. ChHHO-ANFIS

### Base
- DEV ΣAE: **1413.0299**
- DEV direction: **23/33**
- 2025 ΣAE: **1252.0542**
- 2025 MAE: **104.3378**
- 2025 RMSE: **131.0040**
- 2025 MAPE: **2.9712%**
- 2025 direction: **9/12**

### DEV-authorized external winner: CPI_SURPRISE
- Corrected full DEV ΣAE: **1343.6354**
- DEV ΔΣAE: **-69.3945**
- DEV improvement: **4.91%**
- DEV direction: **23/33**
- Frozen 2025 ΣAE: **1095.5792**
- Frozen 2025 improvement: **-156.4749 / 12.50%**
- 2025 MAE: **91.2983**
- 2025 RMSE: **120.3822**
- 2025 MAPE: **2.5854%**
- 2025 direction: **9/12**
- 2025 worst AE: **274.7266**

### Important secondary FX evidence
- PIT CNY/USD block DEV ΔΣAE: **-57.2741**, PASS.
- PIT CNY/USD frozen 2025 ΣAE: **1083.4280**.
- Federal Reserve H.10 major-FX block DEV ΔΣAE: **-49.2814**, PASS.
- H.10 major-FX frozen 2025 ΣAE: **1084.9928**.
- H.10 major-FX frozen 2025 direction: **10/12**.

The FX alternatives happen to score slightly better than CPI on 2025 price error, but they are **not selected**, because CPI surprise had the stronger DEV improvement. 2025 is not allowed to overturn the pre-test choice.

## 4. DE-ABC-RBFNN

### Base
- DEV ΣAE: **1415.8371**
- DEV direction: **25/33**
- 2025 ΣAE: **1145.3733**
- 2025 MAE: **95.4478**
- 2025 RMSE: **118.9333**
- 2025 MAPE: **2.7432%**
- 2025 direction: **9/12**

### DEV-authorized external winner: PIT_RATES
Rates block:
- DGS10 monthly change
- DFF monthly change
- delta(DGS10-DFF) curve proxy

Results:
- Corrected full DEV ΣAE: **1373.5811**
- DEV ΔΣAE: **-42.2560**
- DEV improvement: **2.98%**
- DEV direction: **25/33**
- Frozen 2025 ΣAE: **1012.7415**
- Frozen 2025 improvement: **-132.6318 / 11.58%**
- 2025 MAE: **84.3951**
- 2025 RMSE: **107.9507**
- 2025 MAPE: **2.4251%**
- 2025 direction: **9/12**
- 2025 worst AE: **238.4988**

### FX result
- PIT CNY/USD: PASS but weaker DEV contribution.
- Federal Reserve H.10 broad/major/global FX blocks: no robust promotion winner for DE-ABC.
- Therefore DE-ABC's missing channel appears more strongly related to **rates/monetary regime** than global FX.

## 5. Compact combined panel — X5 result

Feature stacking did **not** improve on the best simple block.

### ChHHO
Best combined promotable candidate:
- CNY + CPI
- full DEV ΣAE **1359.6012**
- frozen 2025 ΣAE **1085.8289**
- 11/12 months improved vs base in 2025

But the DEV-authorized CPI-only layer is better:
- CPI-only DEV **1343.6354**
- CNY+CPI DEV **1359.6012**

Decision: **do not combine; keep CPI-only as the governed winner**.

### DE-ABC
Best combined promotable candidate:
- CNY + rates + CPI
- full DEV ΣAE **1375.4340**
- frozen 2025 ΣAE **1027.2253**
- 10/12 months improved vs base in 2025

But rates-only is better:
- rates-only DEV **1373.5811**
- CNY+rates+CPI DEV **1375.4340**

Decision: **do not combine; keep rates-only as the governed winner**.

This is positive evidence for small-n discipline: more external features are not automatically better.

## 6. Inflation and risk blocks

### Inflation
Headline CPI surprise passes for both models:
- ChHHO DEV ΔΣAE: **-69.3945**
- DE-ABC DEV ΔΣAE: **-22.0035**

Core CPI also contains signal for ChHHO, but headline CPI is the DEV winner.

### Risk appetite
Risk/equity-history blocks produced encouraging diagnostics:
- ChHHO SP500 risk-appetite DEV improvement: **67.0045**
- ChHHO diagnostic 2025 ΣAE: **1123.6097**
- DE-ABC equity-triad DEV improvement: **49.9877**
- DE-ABC diagnostic 2025 ΣAE: **1099.2222**

However these market-history series were ingested later and lack original PIT-storage proof. Therefore:
**DIAGNOSTIC_ONLY / NOT PROMOTABLE**.

### Commodity/oil
No governed usable WTI/Brent/commodity series was found in the current Neon inventory for this run.
Status: **DATA_NOT_READY / NOT_TESTED**.

## 7. External data architecture result

The quota-safe architecture works:

`Neon READ_ONLY authority -> compact governed snapshot -> GitHub Actions offline model test`

Strict replay compact snapshots used only dozens of monthly rows instead of repeatedly exporting raw history.

External-data model jobs execute with:
- `NEON_DATABASE_URL` unset
- frozen model artifacts
- frozen compact external snapshot(s)
- official H.10 public FX download where applicable

This becomes the default external-research execution pattern.

## 8. Stage status

- X0 authority/hypothesis freeze: **DONE**
- X1 availability/vintage audit: **DONE**
- X2 residual predictability/incremental-information screen: **DONE**
- X3 block-by-block augmentation: **DONE**
- X4 ablation: **DONE**
- X5 compact combined panel: **DONE**
- X6 frozen 2025 transport: **DONE**
- X7 error-warning layer: **OPTIONAL / DEFERRED**; not required to answer whether external information adds forecast value

## 9. Decision

### ChHHO-ANFIS
External correction candidate:
**CPI_SURPRISE residual layer**

Status:
**PROMOTE_TO_NATIVE-INTEGRATION_CHALLENGE**, not yet replace/freeze as new champion.

### DE-ABC-RBFNN
External correction candidate:
**PIT_RATES residual layer**

Status:
**PROMOTE_TO_NATIVE-INTEGRATION_CHALLENGE**, not yet replace/freeze as new champion.

### FX / international capital-flow hypothesis
Status:
**SUPPORTED FOR ChHHO / NOT SUPPORTED AS PRIMARY DE-ABC AUGMENTATION**.

The user's hypothesis that international currency information may represent missing investor-direction information is therefore retained as a validated secondary ChHHO channel.

## 10. Next reopen condition

Before external information becomes part of the production/frozen base model:
1. integrate the selected external feature(s) natively into each architecture,
2. repeat the same rolling/expanding DEV contract,
3. compare native augmentation vs residual correction,
4. keep 2025 locked until native specification is frozen,
5. reject if improvement depends on a small number of origins or worsens stability.

## 11. Evidence

Successful runs/artifacts:
- Strict-PIT external audit: workflow run **36472278469** / artifact **10992755818**
- Federal Reserve H.10 FX audit: workflow run **36472823372** / artifact **10992736653**
- Inflation + risk audit: workflow run **36473442704** / artifact **10991394856**
- Final compact panel: workflow run **36474415541** / artifact **10992940914**

Final compact-panel commit:
`03a9fbfeae508e9d7e0d8dce963bfdf0cb486780`

## 12. Kontrol ve Uyum Özeti

- Hindsight bad-month feature picking: **NONE**
- 2025 tuning/selection: **NONE**
- Random split: **NONE**
- Target-month leakage: **NONE**
- Base model mutation: **NONE**
- External correction chronology: **prior residuals only**
- Risk PIT proof: **INSUFFICIENT -> diagnostic only**
- Commodity data: **NOT_READY**
- External information incremental value: **SUPPORTED**
- Simple blocks vs feature soup: **simple blocks preferred**
