# GOLD MONTHLY — CHHHO VIX RESIDUAL SCREEN V1

**Date:** 2026-09-29  
**Status:** COMPLETE / VIX RESIDUAL SIGNAL FOUND / VIX_R1_SELECTED  
**Scope:** DEV-only residual-information screen on frozen ChHHO-ANFIS. 2025/2026 not used for selection.

## 1. Frozen design

Frozen base:
- ChHHO-ANFIS authority artifact **10989389723**
- BASE DEV ΣAE **1413.0298545342782**
- BASE Direction **23/33**

Residual target:
- **actual price − frozen BASE forecast price**

Residual learner:
- Ridge
- alpha **10.0**
- StandardScaler fit only on prior eligible residual rows
- minimum prior residuals **12**
- correction cap **±1.5 × median(abs(prior residual))**
- chronology **prequential / prior DEV residuals only**
- random split **NONE**
- Neon reads **0**

Frozen VIX authority:
- External Authority V2 artifact **11028494060**
- VIX daily authority **READY_CBOE**
- release-lag safety rule **1 calendar day**

Predeclared VIX variables:
- `VIX_LEVEL`: mean eligible daily VIX close in origin month
- `VIX_CHANGE`: current origin-month VIX mean minus previous-month VIX mean
- `VIX_VOL`: population standard deviation of daily first differences in VIX during origin month
- `VIX_SPIKE`: max origin-month VIX divided by origin-month mean VIX

Predeclared blocks:
- **VIX_R1_CHANGE** = VIX_CHANGE
- **VIX_R2_LEVEL_CHANGE** = VIX_LEVEL + VIX_CHANGE
- **VIX_R3_FULL_STRESS** = VIX_LEVEL + VIX_CHANGE + VIX_VOL + VIX_SPIKE

## 2. Execution

- workflow: **Gold Monthly ChHHO VIX Residual Screen V1**
- authoritative run: **36585834751**
- head commit: **3c23d018f3c23b47c36d4ac21327be400c250339**
- job: **109465773517**
- artifact: **11041975865**
- artifact digest: `sha256:e864e30908658f9edc2e9ece8e8070d2d7c06c0d0a52ea7919f98385a7bf66f2`
- workflow result: **SUCCESS**

Earlier run **36585727221** failed before scientific execution because `psycopg` was missing from the runtime. Scientific specification was unchanged; the dependency-only fix produced the authoritative run above.

## 3. DEV results

| Variant | Full DEV ΣAE | Direction | ΔΣAE vs BASE | Relative improvement | Robustness gate |
|---|---:|---:|---:|---:|---|
| BASE | 1413.029855 | 23/33 | — | — | — |
| **VIX_R1_CHANGE** | **1338.330045** | **23/33** | **+74.699809** | **+5.2865%** | **PASS** |
| VIX_R2_LEVEL_CHANGE | 1345.909122 | 23/33 | +67.120733 | +4.7501% | PASS |
| VIX_R3_FULL_STRESS | 1407.226258 | **24/33** | +5.803597 | +0.4107% | **FAIL** |

Selected on DEV:
**VIX_R1_CHANGE**

## 4. VIX_R1 robustness

Eligible correction period contains **21 DEV origins** after the first 12 residuals are accumulated.

- eligible BASE ΣAE: **843.2884386436745**
- eligible corrected ΣAE: **768.5886293661572**
- eligible improvement: **74.69980927751726 USD**
- improvement excluding the single best month: **53.471601696024436 USD**
- 2024 improvement: **62.05453990225692 USD**
- eligible Direction: **14/21 → 14/21**
- robustness gate: **PASS**

The improvement is therefore not dependent on one single favorable month.

## 5. Interpretation

The VIX residual-information hypothesis is supported.

The strongest specification is also the simplest:
**monthly change in the average VIX level alone**.

Adding VIX level does not improve on R1. Adding volatility and spike features over-expands the small residual model and fails the robustness gate despite a one-origin Direction improvement.

This is consistent with small-n discipline:
- VIX contains incremental information about ChHHO forecast error;
- that information is mainly captured by **change in the volatility/risk regime**, not by a larger stress-feature stack.

## 6. Decision

- **VIX_R1_CHANGE residual layer: PROMOTABLE CHALLENGER**
- VIX_R2: valid but dominated by R1
- VIX_R3: reject
- native-input VIX remains **NOT YET TESTED**
- 2025/2026 remain outside selection at this stage
- next clean step, if authorized: freeze VIX_R1 residual specification and transport it unchanged to 2025 and 2026 reporting.
