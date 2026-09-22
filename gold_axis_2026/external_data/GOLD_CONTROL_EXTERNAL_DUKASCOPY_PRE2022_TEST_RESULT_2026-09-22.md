# GOLD CONTROL — EXTERNAL DUKASCOPY HARMONIZATION + PRE-2022 TEST RESULT

**Date:** 2026-09-22  
**Harmonization preregistration:** `039960e98489bd098e5e47344cb333b811bfe97c`  
**Single-policy LTT preregistration:** `9a0c98861b6d26890d52dab576038a666492c25a`

## 1. Source harmonization

The staged Dukascopy-derived 5-minute daily feature spine passes every frozen harmonization gate against the governed internal 5-minute cache over the exact 2020-04-06..2021-12-31 overlap.

Pooled exact overlap:
- 345 / 345 governed retained days = **100%**
- close-return Pearson = **0.999975**
- close-return sign agreement = **99.42%**
- RV Spearman = **0.997529**
- downside-RV Spearman = **0.996985**
- mean external/governed RV scale ratio = **0.99664**
- mean external/governed downside-RV scale ratio = **0.99608**
- source-specific top-quintile downside-risk event agreement = **99.42%**
- top-quintile Jaccard = **0.97183**

By year:
- 2020 return correlation **0.999958**, sign agreement **98.64%**, DR Spearman **0.9950**
- 2021 return correlation **0.999993**, sign agreement **100%**, DR Spearman **0.9968**

Status: `HARMONIZED_FOR_RESEARCH_EXTENSION_NOT_PRODUCTION_AUTHORITY`.

## 2. External 2020–2021 SQRT parent

Using the exact frozen SQRT-HAR-DR annual-origin equations:

| year | formation n | test n | SQRT alarms | actual DOWN | actual UP |
|---|---:|---:|---:|---:|---:|
| 2020 | 498 | 260 | **212** | 97 | 115 |
| 2021 | 758 | 258 | **28** | 16 | 12 |

2020 is a very high-risk crisis regime: the source-specific annual threshold makes SQRT active on 81.5% of the year.

## 3. External Router reconstruction

Frozen direct experts and legacy-context Router semantics were reconstructed origin-safely.

| year | Router UP | TP | FP | UP precision | false-UP FPR |
|---|---:|---:|---:|---:|---:|
| 2020 | **185** | 111 | 74 | **60.00%** | **66.07%** |
| 2021 | **33** | 19 | 14 | **57.58%** | **11.20%** |

## 4. SQRT × Router alarm intersection

| year | SQRT alarms | Router-UP overlap | good suppress | bad suppress | veto precision | true-DOWN retention |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | 212 | **140** | 80 | **60** | 57.14% | **38.14%** |
| 2021 | 28 | **2** | 1 | 1 | 50.00% | **93.75%** |

The 2020 result is a clear crisis-regime failure of the hard veto. Because source harmonization is near-exact in the governed overlap, this cannot reasonably be dismissed as a simple feed mismatch.

## 5. Single-policy LTT V2, pooled 2020–2024

Predeclared policy:
> suppress SQRT forced-DOWN iff frozen Router V2 emits UP.

Pooled calibration:
- SQRT alarms = **270**
- actual DOWN = **127**
- actual UP = **143**
- suppressions = **146**
- good suppressions = **84**
- bad suppressions = **62**
- suppression precision = **57.53%**
- false-alarm reduction = **58.74%**
- true-DOWN retention = **51.18%**
- baseline forced-DOWN precision = **47.04%**
- remaining forced-DOWN precision = **52.42%**
- precision gain = **+5.38 pp**

Exact safety test:
- alpha = 0.20
- delta = 0.10
- n = 127 actual-DOWN alarms
- x = 62 bad suppressions
- lower-tail binomial p-value ≈ **1.0000**

Therefore:

`HARD_ROUTER_POLICY_DECISIVELY_NOT_RISK_CERTIFIED_ON_2020_2024_EXTENSION`.

## 6. Scientific interpretation

The earlier 2024-only near miss was not enough to establish a generally safe hard veto.

The larger historical extension shows:
- Router V2 remains useful as a selective UP verifier in some regimes;
- but a universal rule `Router UP => delete SQRT DOWN` is unsafe across regimes;
- specifically, 2020 produces massive over-suppression of true DOWN alarms.

This does **not** invalidate the frozen UP verifier baseline itself. It invalidates the unconditional hard-veto coupling as a generally safe controller.

The next controller must be regime-aware or risk-aware and must explicitly prevent crisis/high-SQRT-risk periods from inheriting the same suppression semantics as calmer regimes.
