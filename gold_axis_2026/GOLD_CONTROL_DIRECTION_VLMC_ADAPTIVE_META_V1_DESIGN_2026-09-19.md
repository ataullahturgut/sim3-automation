# GOLD CONTROL — VLMC ADAPTIVE META V1 RESEARCH

**Date:** 2026-09-19  
**Identity:** `DIRECTION_VLMC_ADAPTIVE_META_V1_RESEARCH`  
**Parent:** `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`  
**Evidence class:** `RETROSPECTIVE_TIME_ORDERED_NOT_PRISTINE`  
**Runtime authority:** NONE

## Purpose

Test literature-backed adaptations for the observed VLMC failure mode: the best memory length is not stable across regimes. The native reference VLMC family remains unchanged; the adaptive layer may only combine or select among its frozen k=26/52/104 weekly forecasts.

No FAST, BOCPD, GVZ, macro, event labels or 2025 event overlay enters model selection in this experiment.

## Literature-backed candidates

### A. Fixed-Share expert tracking

Treat k=26,52,104 VLMC forecasts as experts and use the Herbster-Warmuth Fixed-Share update, which is designed to track a best expert that may change over time.

Development hyperparameter grid on 2023 only (k=26/52 where both are available):
- eta in {0.25, 0.5, 1, 2, 4}
- alpha in {0, 0.01, 0.02, 0.05, 0.10, 0.20}
- expert loss = zero-one direction loss
- primary selection = balanced accuracy
- tie-break = accuracy, then Brier score

Frozen winner:
- eta=1
- alpha=0.05

For the fair 2024 validation beginning 2024-03-04, k=26/52/104 enter with equal 1/3 weights. The weight state at the end of 2024 is carried causally into 2025.

### B. Fading recent-best expert

Use exponentially fading historical direction accuracy to select the currently best VLMC expert, motivated by recent-performance / Online Performance Estimation / BLAST-style adaptation.

Development grid on 2023 only:
- rho in {0.20,0.40,0.60,0.70,0.80,0.90,0.95,0.98}
- primary selection = balanced accuracy
- tie-break = accuracy, then Brier score

Frozen winner:
- rho=0.90.

At each target week, only past realized outcomes update the expert scores. If expert scores tie exactly, their probabilities are averaged.

## Governance

- 2025 is not used to choose eta, alpha or rho.
- 2025 is a retrospective replay under frozen rules, not a pristine unseen holdout, because parent-family 2025 evidence was already known before this successor was conceived.
- Event overlay is downstream only.
- No post-2025 rescue is allowed under this identity.
