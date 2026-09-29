# GOLD MONTHLY — RESIDUAL ATTRIBUTION / BIAS-ONLY CONTROL

**Date:** 2026-09-29  
**Status:** COMPLETE / METHODOLOGICAL CORRECTION  
**Purpose:** Determine whether external-driver residual gains are incremental to a plain systematic-bias correction.

## 1. Why this control was required

All residual Ridge models include an intercept. For the frozen ChHHO DEV sample, the mean price residual is:

- **+13.690850943418237 USD**

Therefore an external residual model can appear to improve BASE even when the external feature contributes little, simply because the intercept corrects a persistent under-forecast bias.

The proper attribution benchmark is therefore not only **BASE**, but also a **BIAS_ONLY** residual correction:
- same minimum history: 12 prior residuals
- same correction cap: ±1.5 × median(abs(prior residual))
- prequential DEV
- frozen DEV mean-residual correction for 2025/2026 transport
- no external variables.

## 2. Bias-only result

Authoritative workflow:
- **Gold Monthly ChHHO Residual Bias Only Control V1**
- run **36591365527**
- job **109485005513**
- head **dfb1f2800bd6e7223e6ba0ecee6ac006ae8b4937**
- artifact **11044715151**
- digest `sha256:ecef7244d7dc3860b0c62da76cefe589eeaba6dad104d24601a3965b96c24300`

DEV:
- BASE ΣAE **1413.0298545342782**
- BIAS_ONLY ΣAE **1338.8935117711515**
- improvement vs BASE **74.13634276312678 USD**
- Direction **23/33 → 23/33**
- robustness gate **PASS**
- improvement excluding single best month **57.607579378347964 USD**
- 2024 improvement **62.9516270935801 USD**

Frozen DEV fit:
- mean residual / correction **+13.690850943418237 USD**
- cap **53.266887317887495**

2025:
- BASE **1252.0541594740248**
- BIAS_ONLY **1095.7493443344565**
- improvement **156.3048151395683 USD**
- Direction **9/12 → 9/12**

2026 Jan-Aug:
- BASE **1526.1332118229584**
- BIAS_ONLY **1526.1332118229575**
- improvement approximately **0**
- Direction **5/8 → 6/8**

## 3. External residual attribution after bias control

| Residual specification | DEV ΣAE | Improvement vs BASE | Incremental vs BIAS_ONLY | Attribution |
|---|---:|---:|---:|---|
| BASE | 1413.029855 | — | — | — |
| **BIAS_ONLY** | **1338.893512** | **74.136343** | — | control |
| VIX_R1_CHANGE | 1338.330045 | 74.699809 | **+0.563467** | marginal DEV incremental value |
| BRENT_R1_MR1 | 1346.502415 | 66.527439 | **−7.608904** | worse than bias-only |
| PIT Rates | 1370.920393 | 42.109462 | **−32.026881** | worse than bias-only |
| Rates + Brent | 1377.101415 | 35.928439 | **−38.207903** | worse than bias-only |

This materially changes interpretation.

## 4. Brent isolated screen

Authoritative run:
- workflow **Gold Monthly ChHHO Brent Residual Screen V1**
- run **36590486319**
- job **109481990464**
- head **f2eb03085e42005a3902dd278d94f17544675e1b**
- artifact **11043268953**
- digest `sha256:014754f03dc8f754cce60d385f98146c0ef8094a760940d13564633706b77c27`

Predeclared blocks:
- BRENT_R1_MR1
- BRENT_R2_VW
- BRENT_R3_MR1_VW

Results:
- BRENT_R1_MR1 **1346.502415 / 23/33**, BASE robustness PASS
- BRENT_R2_VW **1349.180909 / 23/33**, BASE robustness PASS
- BRENT_R3_MR1_VW **1357.706180 / 23/33**, BASE robustness PASS

Selected against BASE:
- **BRENT_R1_MR1**

But after the mandatory BIAS_ONLY control:
- BRENT_R1 is **7.608904 USD worse** than BIAS_ONLY on DEV.
- therefore it is **NOT an independently supported external residual driver**.

## 5. Rates + Brent combination

Authoritative run:
- workflow **Gold Monthly ChHHO Rates Plus Brent Residual Screen V1**
- run **36590746098**
- job **109482871506**
- head **b67b1dad7c816a3869f96e22661d4b44e50772c3**
- artifact **11043503614**
- digest `sha256:d7d457fb82b5f55dedc9d1dbac50ba38271b0436be650424a0b486242ad86f81`

DEV:
- Rates control **1370.920393**
- Brent control **1346.502415**
- Rates + Brent **1377.101415**
- selected = **Brent control**
- combination is worse than either Brent alone or BIAS_ONLY.

Conclusion:
- no additive Rates + Brent benefit under the frozen residual Ridge protocol.

## 6. Brent frozen transport

Authoritative run:
- workflow **Gold Monthly ChHHO Brent R1 Frozen Transport 2025 2026 V1**
- run **36591080686**
- job **109484018473**
- head **fafae3079fd2032d61a108d22b163d5869854f86**
- artifact **11043592796**
- digest `sha256:0908923fe1b11c678320f530062d80ae2e8068f7e2261e67ccdbd170062f3fe3`

Frozen fit:
- intercept **13.690850943418237**
- standardized BRENT_MR1 coefficient **−0.5545611852923165**

2025:
- BASE **1252.054159**
- Brent **1096.152741**
- Bias-only **1095.749344**
- Brent is **0.403396 USD worse than bias-only**

2026 Jan-Aug:
- BASE **1526.133212**
- Brent **1521.188957**
- Bias-only **1526.133212**
- Brent improves over bias-only by **4.944255 USD**
- Direction **5/8 → 6/8**

The 2026 gain is retrospective transport only and cannot rescue DEV attribution failure.

## 7. Corrected decision

- **BRENT residual external attribution: NOT PROMOTED**
- **Rates + Brent combined residual: NOT PROMOTED**
- **BIAS_ONLY residual control becomes mandatory** for all future external residual screens.
- VIX_R1 retains only **marginal DEV incremental value (+0.56 USD vs bias-only)**; its earlier BASE-relative improvement must not be interpreted as mostly VIX-driven.
- PIT Rates is worse than bias-only on DEV despite a positive 2026 retrospective effect; it remains a challenger observation, not a DEV-supported external residual winner.
- Future Nasdaq/WTI/etc. residual screens must pass both:
  1. BASE robustness gate
  2. **incremental improvement versus BIAS_ONLY**.
