# GOLD MONTHLY — Prototype-Anchored State Alignment V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Binding conclusion:** semantic label switching exists in some retrospective expanding-refit months, but it is **not the cause of the 2025-2026 transition problem**.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_MARKET_REGIME_PROTOTYPE_ALIGNMENT_V1_AUTHORITY_2026-09-30.md`
- authority commits:
  - `c8dd339c809fb28fd34a6b9d24fc93b3a0953a8f`
  - posterior-weighted profile clarification: `6a7ac5ee9880e737b75d4ae4562fdc0b333d04cf`

Code:
- `gold_axis_2026/tools/gold_monthly_market_regime_prototype_alignment_v1.py`
- code commit: `d2f61b77f4beff22e16e562a0d79cd391dee0651`

Workflow:
- `.github/workflows/gold-monthly-market-regime-prototype-alignment-v1.yml`
- workflow commit: `2d8f068ee98fc96f1e6df8ef449fe748b0e83e13`

Execution:
- workflow: **Gold Monthly Market Regime Prototype Alignment V1**
- run: **36733309569**
- artifact: **11106235879**
- artifact digest: `sha256:d26fbdffcc6e1c3409293e754fac0a8bdc2830f68b236d65e93dc2567b5ad1c4`
- scientific gate: **PASS**

Underlying expanding and annual detector fits reproduce the prior comparison exactly. Posterior probabilities and predictive log scores are unchanged by the semantic re-labeling.

## 2. Prototype method

Frozen semantic prototypes:
- development period: 2010-07..2024-12;
- R0/R1/R2 reference states from Discovery V1;
- all 13 market-state features;
- features standardized with frozen 2010-2024 mean/std;
- each newly fitted latent HMM state represented by its 13D posterior-weighted training-history mean profile;
- one-to-one state-to-prototype assignment solved by Hungarian minimum-distance matching.

This changes state names only, never the HMM likelihood/posterior/density model.

## 3. Core 2022-01..2026-08

### EXPANDING_REFIT

Old Gold_r1-order semantic mapping:
- strict R-state accuracy: **68.6%**
- balanced accuracy: **61.2%**
- decided-only accuracy: **76.1%**
- R0 recall: **44.4%**
- R1 recall: **47.1%**
- R2 recall: **92.0%**

Prototype-aligned mapping:
- strict R-state accuracy: **76.5%**
- balanced accuracy: **70.8%**
- decided-only accuracy: **84.8%**
- R0 recall: **55.6%**
- R1 recall: **64.7%**
- R2 recall: **92.0%**

Semantic label changed in:
- **7/56 months = 12.5%**

Changed core months:
- 2022-04
- 2022-12
- 2023-02
- 2023-05
- 2023-06
- 2023-07
- 2023-08

Interpretation:
Prototype alignment materially improves retrospective semantic consistency for the expanding-refit detector.

### ANNUAL_ANCHORED

Old and prototype-aligned results are **identical**:
- strict R-state accuracy: **68.6%**
- balanced accuracy: **53.6%**
- R0 recall: **0.0%**
- R1 recall: **64.7%**
- R2 recall: **96.0%**

Semantic changes:
- **0/56 months**

Interpretation:
The annual-anchor R0 failure is not caused by Gold_r1-only label ordering. The 13D prototype matcher chooses the same state semantics.

## 4. Full replay 2015-07..2026-08

### EXPANDING_REFIT

Old:
- strict accuracy **65.6%**
- balanced accuracy **63.0%**
- decided-only **69.5%**

Prototype aligned:
- strict accuracy **70.4%**
- balanced accuracy **67.5%**
- decided-only **74.6%**

Per-regime prototype recall:
- R0 **50.0%**
- R1 **61.1%**
- R2 **91.5%**

Semantic changes:
- **9/134 = 6.7%**

This confirms that label-switching/state-semantic drift exists historically in some independently re-fitted expanding models.

### ANNUAL_ANCHORED

Old and prototype-aligned:
- identical across all 134 months;
- strict accuracy **64.8%**
- balanced accuracy **63.6%**
- R0/R1/R2 recall **54.2% / 53.7% / 83.0%**

Semantic changes:
- **0/134**

## 5. Critical transport result: 2025-01..2026-08

This is the decisive finding.

### EXPANDING_REFIT
Prototype alignment changed:
- **0/20 months**

Metrics remain exactly:
- strict R-state accuracy **88.9%**
- represented-state balanced accuracy **71.9%**
- R1 recall **50.0%**
- R2 recall **93.75%**

### ANNUAL_ANCHORED
Prototype alignment changed:
- **0/20 months**

Metrics remain exactly:
- strict R-state accuracy **94.4%**
- represented-state balanced accuracy **75.0%**
- R1 recall **50.0%**
- R2 recall **100%**

There are no confident reference-R0 months in this 20-month transport interval.

Binding implication:
**the 2025-2026 behavior is not a state-label naming artifact.**

## 6. Mandatory 2026 transition checkpoint

Prototype alignment leaves every 2026 critical state unchanged.

| Month | Expanding prototype | Annual prototype |
|---|---|---|
| 2026-04 | R2 98.4% | R2 97.8% |
| 2026-05 | R2 70.9% | BELIRSIZ / underlying R2 50.8% |
| 2026-06 | R2 79.4% | R0 82.4% |
| 2026-07 | BELIRSIZ / underlying R1 50.8% | R0 76.6% |
| 2026-08 | R1 94.8% | R1 97.5% |

The 13D prototype distance assignment explicitly confirms the annual 2026 R0 semantics:
- the latent state used in 2026-06/07 is closest to the frozen R0 prototype, not R1/R2;
- therefore the R0 calls are not caused by a label swap.

## 7. 2024 transition checkpoint

Prototype alignment also leaves the 2024 R1 -> R2 transition behavior unchanged:
- 2024-03 R1;
- 2024-04 BELIRSIZ with underlying R2;
- 2024-05 confident R2;
- one-month confident-transition delay.

## 8. Binding conclusion

The hypothesis splits cleanly:

### Confirmed
Semantic label switching exists in the expanding-refit historical replay and prototype anchoring improves its retrospective R0/R1 consistency.

### Rejected as explanation for the current problem
Semantic label switching is **not** the cause of the 2025-2026 transition behavior:
- no 2025/2026 expanding label changes;
- no 2025/2026 annual label changes;
- annual 2026-06/07 R0 is supported by the full 13D prototype match.

Therefore the remaining issue is **regime dynamics / transition detection**, not naming.

## 9. Binding decision

Do not spend another stage only changing R0/R1/R2 naming.

Do not move to alarm selection/weighting yet.

Next exact regime-only study should be a **Transition / Change Detector V1** layered beside the HMM:
- preserve HMM R0/R1/R2 as state identity;
- separately detect when the current month's 13D state vector is departing from the incumbent regime before the HMM confidently changes state;
- output a transition flag / BELIRSIZ-transition status rather than forcing an early new R-state;
- evaluate especially 2024-04 and 2026-05/06/07, plus historical transitions;
- use market-state variables only.

No alarm selection.
No alarm weighting.
No forecast correction.
No routing/model switching.
