# GOLD MONTHLY — CHHHO PIT RATES RESIDUAL EXACT REPLICATION

**Date:** 2026-09-29  
**Status:** COMPLETE / EXACT REPLICATION PASS  
**Purpose:** Reproduce the previously successful Rates residual-correction method without redesigning it.

## 1. Exact method replicated

Frozen base:
- model: **ChHHO-ANFIS**
- frozen authority artifact: **10989389723**
- base model mutation: **NONE**

Strict-PIT Rates block:
- `dgs10_change`
- `dff_change`
- `curve_proxy_change = delta(DGS10-DFF)`
- snapshot: `GOLD_MONTHLY_EXTERNAL_PIT_COMPACT_V1_2026-09-28.json`

Residual learner:
- target: **price residual = actual price - frozen BASE forecast price**
- model: **Ridge**
- Ridge alpha: **10.0**
- scaler: **StandardScaler**
- minimum prior residuals: **12**
- correction cap: **±1.5 × median(abs(prior residual))**
- chronology: **prequential, prior DEV residuals only**
- random split: **NONE**
- 2025 selection/tuning: **NONE**
- Neon reads in model run: **0**

The first eligible corrected DEV target is **2023-04** because the method requires 12 prior residuals.

## 2. Authoritative replication execution

- workflow: **Gold Monthly ChHHO PIT Rates Residual Replication V1**
- run: **36581036837**
- head commit: **46fa4d92cc3b72efb87f2d1624758884e48defb0**
- job: **109448965788**
- result artifact: **11038844070**
- artifact digest: `sha256:3db616642fc285fff2c0357994bc8ab8390e6f65c24dc87380e2a5ac2cebf34b`
- replication gate: **PASS**

## 3. Exact reproduced result

### Frozen BASE
- DEV ΣAE: **1413.0298545342782**
- Direction: **23/33**

### PIT Rates residual correction
- DEV ΣAE: **1370.9203928352813**
- Direction: **23/33**

### Improvement
- full DEV ΣAE improvement: **42.10946169899694 USD**
- relative improvement: **2.98%**
- direction change: **0**

Eligible corrected period only:
- eligible months: **21**
- BASE eligible ΣAE: **843.2884386436745**
- corrected eligible ΣAE: **801.1789769446775**
- eligible improvement: **42.10946169899694 USD**
- improvement excluding the single best month: **17.922324074458402 USD**
- 2024 ΣAE improvement: **62.622909991857114 USD**
- stability gate: **PASS**

The tiny BASE difference versus the current canonical BASE `1413.0297794084559` is only about **0.000075 USD** and comes from the older frozen ChHHO authority artifact used by the original residual screen. The historical result itself reproduces exactly within the frozen tolerance.

## 4. Scientific interpretation

The earlier result is real and reproducible.

This resolves the apparent contradiction:

- Rates as **native ChHHO inputs**: not promoted.
- Rates as a **separate residual-correction layer**: improves ChHHO DEV ΣAE while preserving Direction.

Therefore the correct statement is not “Rates is useless.” The evidence supports:

> Rates information can add incremental value when used to model the frozen base model's residual error, but it does not add value when directly expanding the ChHHO-ANFIS native input space under the tested F4 representations.

## 5. Data-quality context

The direct Federal Reserve Board DDP hard re-audit also passed:
- Broad USD: exact daily parity
- nominal 10Y: exact daily parity
- real 10Y: exact daily parity
- all tested DEV transforms: max abs diff **0.0**

Thus the native-input failures are not explained by a demonstrated raw-data or transform error.

## 6. Next decision boundary

This replication re-opens **Rates residual correction** as a valid architecture-specific enhancement candidate.

It does **not** re-open native-input Rates.

Before promotion into the current champion path, the next step should be a clean current-authority re-run of the same price-residual protocol using the current canonical ChHHO BASE rows, with no change to the Ridge hyperparameters or PIT Rates block. 2025/2026 must remain outside selection until that specification is frozen.
