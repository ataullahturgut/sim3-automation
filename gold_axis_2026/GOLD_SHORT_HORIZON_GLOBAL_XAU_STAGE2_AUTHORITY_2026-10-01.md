# GOLD SHORT-HORIZON GLOBAL XAU — Stage 2 H3 Direction Robustness Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN  
**Parent:** `GOLD_SHORT_HORIZON_GLOBAL_XAU_PROJECT_MANIFEST.md`

## 1. Mission

Audit the only Stage-1 global-XAU PASS:

- horizon: **H3**
- head: **direction**
- feature block: **CORE3**
- model: **Logistic L2**.

No new model family is introduced.

2025 remains frozen.

## 2. Target

Historical development target:
- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- global XAU/USD daily spot-average research series
- H3 forward log-return sign.

BIST Metal Price is excluded.

## 3. Chronology

- training history: through 2021 plus matured prior DEV labels
- DEV: 2022-2024
- 2025: forbidden
- expanding chronological refits every 5 DEV origins
- H3 maturity purge identical to Stage 1.

## 4. Frozen core contract

### CORE3
Gold:
- gold_r1
- gold_r3
- gold_r5
- gold_r10
- gold_r21
- sigma20

Silver:
- silver_r1
- silver_r5
- silver_r21
- silver_age_days

Platinum:
- platinum_r1
- platinum_r5
- platinum_r21
- platinum_age_days.

### Model
- StandardScaler
- LogisticRegression
- L2
- C = 1.0
- solver = lbfgs
- max_iter = 1000
- no class weighting
- fixed seed 20261001.

## 5. Comparison representations

Use the same Logistic L2 contract on:

1. GOLD_ONLY
2. CORE3
3. CORE4
4. CORE3_SAFE_EXTERNAL_RAW
5. CORE3_SAFE_EXTERNAL_CHG.

No model hyperparameter tuning.

### SAFE_EXTERNAL_RAW
Existing origin-safe as-of levels:
- DGS10
- DFII10
- BREAKEVEN10_PROXY
- BROAD_USD_INDEX
- EURUSD_QUOTE
- GBPUSD_QUOTE
- JPY_PER_USD
- CHF_PER_USD
- CNY_PER_USD
- VIX
- NDX.

### SAFE_EXTERNAL_CHG
CORE3 plus causal changes computed only from the already origin-safe Stage-0 panel:

Rates:
- 5-origin difference of DGS10
- 5-origin difference of DFII10
- 5-origin difference of BREAKEVEN10_PROXY.

Market / FX:
- 5-origin log change of BROAD_USD_INDEX
- EURUSD_QUOTE
- GBPUSD_QUOTE
- JPY_PER_USD
- CHF_PER_USD
- CNY_PER_USD
- VIX
- NDX.

The change representation is fixed before result inspection.

## 6. Primary baselines

At each block start:
- expanding historical UP prevalence
- trailing-252 UP prevalence.

The better Brier baseline is binding.

## 7. Primary H3 robustness gate

CORE3 / Logistic L2 remains **ROBUST PASS** only if:

1. aggregate relative Brier improvement >= **1.0%**
2. aggregate log loss <= best baseline log loss
3. prediction SD >= **0.02**
4. at least **2 of 3** DEV years have positive Brier improvement
5. no DEV year is worse than its best baseline by more than **3.0% relative Brier**
6. each DEV year has >= 200 observations.

If aggregate Stage-1 PASS survives but annual guard fails:
- status = FRAGILE / NO PROMOTION.

## 8. Volatility diagnostics

Define volatility buckets from DEV origin-known `sigma20` terciles:
- LOW
- MID
- HIGH.

Report:
- N
- Brier
- baseline Brier
- relative improvement
- log loss
- accuracy
- balanced accuracy.

No volatility-specific gate or rule may be created.

## 9. Coefficient stability

For every CORE3 refit record standardized Logistic coefficients.

For each feature report:
- median coefficient
- mean coefficient
- coefficient SD
- positive-sign share
- negative-sign share
- sign-consistency = max(positive, negative)
- median absolute coefficient.

Diagnostic stability flags:

- STABLE_DIRECTIONAL if sign-consistency >= 80%
- UNSTABLE otherwise.

No coefficient may be manually removed after inspection.

## 10. Representation decision

A comparison block may replace CORE3 only if:

1. aggregate relative Brier improvement is at least **0.50 percentage points better** than CORE3's relative improvement;
2. annual guard from section 7 also passes;
3. log loss not worse than CORE3;
4. prediction SD >=0.02.

Otherwise retain CORE3.

This is intentionally conservative.

## 11. H5 secondary diagnostic

Re-run H5 CORE3 / Logistic L2 under the same chronology.

H5 stays **SECONDARY ONLY** unless:
- aggregate relative Brier improvement >=1.0%.

Annual evidence is reported but cannot lower this gate.

## 12. No economic layer

No:
- P&L
- cost
- entry threshold
- position sizing
- 2025 transport.

## 13. Required outputs

- H3 origin-level predictions for all representations
- H3 aggregate metrics
- H3 yearly metrics
- H3 volatility metrics
- CORE3 coefficient-path table
- coefficient-stability summary
- H5 secondary metrics
- binding robustness decision
- hashes.

## 14. Next stage

If H3 direction = ROBUST PASS:
- freeze H3 direction engine;
- next research question is whether a **direction-only tactical architecture** can be economically useful without pretending return magnitude / quantile heads exist.

If H3 fails robustness:
- stop current global-XAU tactical promotion;
- retain it as weak research evidence only.
