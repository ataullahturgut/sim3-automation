# GOLD SHORT-HORIZON GLOBAL XAU — ANFIS 2025/2026 Transport Authority

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN / USER-AUTHORIZED REPORTING  
**Scope:** Vanilla ANFIS + ChHHO-ANFIS  
**Target:** Global XAU daily H3 direction

## Purpose

The user explicitly authorized opened-period reporting for the two already-frozen ANFIS specifications.

This stage does not reopen model selection.

## Binding rules

- 2025 and 2026 remain reporting-only.
- No architecture, rule count, feature, optimizer, epoch limit, threshold or probability calibration may be selected from 2025/2026.
- CORE3 inputs only.
- H3 target only.
- Classification threshold fixed at 0.50.
- The fit used for opened reporting is frozen before 2025.

## Primary transport mode

**STRICT_FROZEN_FIT**

For each model:

1. use only rows whose H3 target end is <= 2024-12-31;
2. choose any internal training complexity only from the chronological pre-2025 checking tail;
3. refit/finalize on the full pre-2025 mature set;
4. freeze parameters;
5. predict every eligible 2025 and 2026 issue whose H3 target is observed through 2026-09-30;
6. never update the model using 2025/2026 outcomes.

Models:

### Vanilla ANFIS
- 14 CORE3 inputs
- 5 Gaussian rules
- first-order Sugeno/TSK
- LSE consequents
- Jang normalized-gradient premise learning
- max 100 epochs
- chronological pre-2025 checking tail.

### ChHHO-ANFIS
- same ANFIS architecture
- chaotic initialization
- HHO premise optimization
- population 8
- generations 8
- local Jang refinement max 60 epochs
- all optimizer/checking selection uses pre-2025 data only.

## Required reporting

For 2025 and 2026:
- N
- Brier
- log loss
- accuracy
- balanced accuracy
- UP recall
- DOWN recall
- mean P(UP)
- prediction SD
- monthly 2026 summary
- origin-level prediction ledger.

Frozen Logistic-L2 transport metrics are shown only as a comparator; they do not change ANFIS specifications.
