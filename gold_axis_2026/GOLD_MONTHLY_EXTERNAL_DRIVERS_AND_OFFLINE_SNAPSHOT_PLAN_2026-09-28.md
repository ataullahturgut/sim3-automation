# GOLD MONTHLY FORECAST — OFFLINE SNAPSHOT + EXTERNAL DRIVER RESEARCH PLAN

**Date:** 2026-09-28  
**Status:** PLANNED / GOVERNED / PRE-OUTCOME  
**Parent authority:** `GOLD_MONTHLY_PROJECT_MANIFEST.md`

## A. Amaç

Bu çalışma iki problemi birlikte çözer:

1. Neon data-transfer kotasını koruyarak model deneylerini reproducible biçimde çalıştırmak.
2. Mevcut güçlü Gold Monthly modellerinde eksik olabilecek dışsal bilgi kanallarını hindsight bias yaratmadan test etmek.

Bu dosya model sonucu içermez; bir research/execution contract'tır.

## B. Veri mimarisi

Default execution:
`Neon READ_ONLY authority -> canonical immutable snapshot -> hash/parity -> model runs`

Neon her model job'ında full historical source olarak tekrar okunmaz.

### B1. Snapshot stages
S0 source inventory  
S1 minimal one-shot export  
S2 canonical Parquet/compact serialization  
S3 data dictionary + availability metadata  
S4 SHA-256 freeze  
S5 parity run vs Neon-direct reference  
S6 authorize for model execution  
S7 shared reuse across families  
S8 incremental/explicit refresh only  
S9 refresh parity + new hash

### B2. Guardrails
- DB READ_ONLY.
- No target-month leakage.
- No future scaler fit.
- No random split.
- Same snapshot/hash across compared models.
- External datasets are separately versioned and hashed.
- Artifact expiry requires re-export + parity before reauthorization.

## C. External-driver research question

Question:
Can information available at forecast origin explain or reduce future forecast error beyond the existing frozen metal/CURRENT8 information set?

The exercise must not inspect a bad month and then choose a variable that narratively explains it.

### C1. Two gates
Diagnostic gate:
Does origin-safe X predict next-period signed error / absolute error / large-error risk?

Forecast-value gate:
Does adding X to the governed forecast system reduce honest rolling-origin DEV error?

A variable can pass diagnostic and fail forecast-value. Such a variable is not promoted.

## D. Pre-outcome candidate blocks

D1 Global FX / capital-flow proxy  
D2 Nominal and real rates  
D3 Yield curve / monetary-policy expectations  
D4 Inflation/breakevens  
D5 Volatility/risk  
D6 Economic-policy/geopolitical uncertainty  
D7 Oil/broad commodities  
D8 Equity risk appetite  
D9 Flow/demand proxies only if real-time availability is provable

Exact series, transforms and lags require an authority scan before execution.

## E. Global FX / International Capital-Flow block

Rationale:
The current metal-centric model may not explicitly represent global investor rotation among USD, JPY, CHF and Gold.

Candidate raw series, subject to availability audit:
- DXY / broad USD index
- EUR/USD
- USD/JPY
- GBP/USD
- USD/CHF
- USD/CNH or CNY if appropriate

Candidate derived features:
- monthly/within-origin returns
- realized FX volatility
- cross-FX dispersion
- USD breadth
- safe-haven rotation score among Gold/USD/JPY/CHF

Hypotheses:
- H0: no incremental forecast information.
- H1: FX block adds incremental out-of-sample information.
- H2: derived breadth/dispersion/rotation features outperform DXY-only as an information state.

## F. Governed experimental stages

X0 authority + exact feature/transform/lag freeze  
X1 availability/vintage audit  
X2 base-model residual predictability screen on all DEV origins  
X3 block-by-block augmentation  
X4 predeclared ablation  
X5 compact combined panel  
X6 frozen 2025 transport  
X7 optional error-warning/reliability layer

## G. Evaluation

Primary:
- DEV ΣAE
- DEV direction

Supporting:
- MAE
- RMSE
- relative MAE vs RW
- yearly stability
- worst AE / tail months
- leave-one-origin sensitivity where practical

External feature acceptance additionally requires:
- availability/vintage PASS
- leakage PASS
- stable incremental DEV value
- no single-month dependence
- compactness / small-n discipline

## H. 2025 rule

2025 may not influence:
- external variable selection
- lag selection
- transformations
- block composition
- model hyperparameters
- error threshold
- ablation decisions
- rescue

Only after full DEV freeze may 2025 be evaluated once as transport/reporting evidence.

## I. Relationship to current model roadmap

This is a parallel feature-information research track.
It does not replace or invalidate the active CNN/LSTM structural roadmap.
It does not reopen completed ELM/ANN/ELMFIS/ANFIS/RBFNN families.
Initial augmentation anchors should be the retained strong models:
- ChHHO-ANFIS
- DE-ABC-RBFNN

A future structural model may inherit an external panel only after that panel independently passes this research contract.

## J. Control and compliance

- Neon remains authoritative source: YES
- Snapshot becomes second authority: NO
- Default repeated Neon full-read: NO
- Snapshot hash/parity mandatory: YES
- External variables chosen after bad-month inspection: NO
- DEV-only feature research: YES
- 2025 tuning: NO
- 2026 selection: NO
- Random split: NONE
- Target-month leakage: NONE
- FX block preserved as explicit research topic: YES
