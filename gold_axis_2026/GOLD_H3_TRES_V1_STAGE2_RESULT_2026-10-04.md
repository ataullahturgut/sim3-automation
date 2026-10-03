# TRES-H3 V1 — STAGE 2 V5 ERROR-RISK RESULT

**Status:** **NO_INCREMENTAL_TRES_ERROR_RISK**  
- predictions: **432**
- scored origins: **2024-08-30 .. 2026-09-24**
- maturity leakage failures: **0**

## Aggregate baseline vs survival-augmented error risk

| Metric | Baseline | + Survival | Delta |
|---|---:|---:|---:|
| ROC AUC | 0.5595 | 0.5552 | -0.0043 |
| Brier | 0.2332 | 0.2355 | +0.0023 |
| Log loss | 0.6673 | 0.6730 | +0.0057 |

## Augmented p_error concentration

- bottom quintile error rate: **28.74%**
- top quintile error rate: **36.78%**
- separation: **+8.05 pp**

## Half-year stability

| Block | N | Base AUC | Aug AUC | ΔAUC | ΔBrier | ΔLogloss | Top-bottom error sep |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024_H2 | 68 | 0.601 | 0.595 | -0.006 | +0.0003 | -0.0013 | +7.1pp |
| 2025_H1 | 102 | 0.604 | 0.617 | +0.013 | +0.0017 | +0.0064 | +23.8pp |
| 2025_H2 | 109 | 0.563 | 0.546 | -0.017 | +0.0003 | -0.0001 | +4.5pp |
| 2026_H1 | 109 | 0.491 | 0.477 | -0.014 | +0.0035 | +0.0082 | -9.1pp |
| 2026_H2 | 44 | 0.577 | 0.553 | -0.024 | +0.0082 | +0.0225 | +22.2pp |

## Survival feature coefficient stability

| Feature | Mean standardized coef | Median | Positive months |
|---|---:|---:|---:|
| F_continuation | +0.345 | +0.332 | 100.0% |
| F_reversal | +0.469 | +0.480 | 100.0% |
| expected_event_day | +0.151 | +0.098 | 92.0% |
| hR1 | -0.212 | -0.206 | 0.0% |

## Gate

- AUC non-worse blocks: **4/5** (required 4)
- AUC improved blocks: **1/5** (required 3)
- Survival outputs do not add enough stable incremental V5 error-risk information under the frozen gate.
- Stage 3 is not authorized under TRES V1.
