# GOLD MONTHLY FORECAST — BOOSTING STAGE 6C-D AUTHORITY DECISION

Date: 2026-09-28
Status: AUTHORITY REVIEW COMPLETE — CONDITIONAL GO WITH STAGED ABLATION

## Question
Should the project still test the literature model VMD-RES.-CEEMDAN-WOA-XGBoost after canonical causal CEEMDAN-XGBoost failed in Stage 6C-C?

## Primary gold-specific authority
Guo, Y.; Li, C.; Wang, X.; Duan, Y.
"Gold Price Prediction Using Two-layer Decomposition and XGboost Optimized by the Whale Optimization Algorithm."
Computational Economics 66(2), 1157-1189, 2025.
DOI: 10.1007/s10614-024-10736-9.

The paper's architecture is structurally different from Stage 6C-C:
1. preliminary VMD of the gold price series,
2. secondary CEEMDAN only on the complex residual from VMD,
3. XGBoost optimized by WOA,
4. recombination of forecasts,
5. external predictors are also considered.

Therefore the failure of CEEMDAN directly on the raw monthly Gold series does not logically falsify the VMD-residual-CEEMDAN architecture.

## VMD authority
Dragomiretskiy, K.; Zosso, D.
"Variational Mode Decomposition."
IEEE Transactions on Signal Processing 62(3), 531-544, 2014.
DOI: 10.1109/TSP.2013.2288675.

VMD is a non-recursive variational decomposition extracting modes concurrently.

## Leakage control
Forecasting literature explicitly documents that global VMD decomposition before temporal evaluation can introduce look-ahead bias.
Origin-safe / sliding-window or moving-front VMD avoids this by restricting each decomposition to information available at the forecast time.

Therefore any project implementation MUST perform VMD separately for each target prefix ending at t-1.
Global full-sample VMD is BLOCKED.

## Cross-domain structural support
Duan et al. (2024), Energy Science & Engineering, DOI 10.1002/ese3.1655:
- WOA-XGBoost baseline,
- CEEMDAN applied to residuals,
- component forecasts recombined,
- reported gains from residual decomposition over WOA-XGBoost.

A 2025 Carbon Balance and Management study, DOI 10.1186/s13021-025-00348-7, similarly uses secondary decomposition with WOA-XGBoost and reports that the extra VMD layer improves over single decomposition within its own data/protocol.

These studies support the structural rationale but do not validate transfer to this project's monthly Gold protocol.

## What Stage 6C-C taught us
Canonical causal CEEMDAN-XGBoost:
- SigmaAE = 1820.4745552856104
- direction = 17/33
- relative MAE vs RW = 1.0355372897
- worse than frozen CURRENT8 XGBoost = 1583.8534958594905 / 20/33
- scientifically valid, NOT PROMOTED.

This specifically rejects:
"raw monthly Gold -> causal CEEMDAN IMF endpoint features -> frozen XGBoost"

It does NOT directly reject:
"raw Gold -> causal VMD -> residual -> causal CEEMDAN of residual -> component forecasting/reconstruction"

## Decision
CONDITIONAL GO.

Do NOT jump directly to the complete VMD-RES.-CEEMDAN-WOA-XGBoost kitchen-sink model.

Use staged ablation so only one structural dimension changes at a time.

### Stage 6C-D0 — Causal VMD-XGBoost
Purpose:
Test whether causal VMD itself provides useful multiscale information under the project protocol.

Rules:
- VMD prefix ends at t-1 for every training and outer target row.
- XGBoost learner frozen to Stage-5 X_R4_COMBO.
- No WOA.
- No CEEMDAN.
- No 2025/2026.
- DEV only.
- Pre-outcome frozen VMD parameters or DEV-safe nested parameter selection; parameter strategy must be authority-defined before outcomes.

Gate:
Proceed to D1 only if VMD shows meaningful structural signal versus frozen XGBoost CURRENT8 or clearly useful complementarity under a pre-defined rule.

### Stage 6C-D1 — Causal VMD + Residual CEEMDAN-XGBoost
Purpose:
Test the paper's actual two-layer decomposition idea.

Rules:
- CEEMDAN applies ONLY to the VMD residual/complex remainder.
- Both VMD and CEEMDAN are moving-front / point-in-time.
- XGBoost remains frozen.
- No WOA yet.
- Reconstruction/component accounting must pass numerical integrity checks.

Gate:
Proceed to D2 only if D1 improves on D0 or provides pre-defined complementary value.

### Stage 6C-D2 — WOA optimization
Purpose:
Only after structural decomposition earns its place, test whether WOA improves the winning D0/D1 learner.

Rules:
- WOA cannot be allowed to rescue a structurally failed decomposition after seeing outer outcomes.
- Optimization must be nested chronological.
- Same fixed objective budget as comparable Stage-6 searches unless authority evidence justifies otherwise.
- 2025 and quarantined 2026 remain unavailable.

## Why this is the preferred decision
1. Gold-specific literature directly supports the two-layer VMD-residual-CEEMDAN architecture.
2. The architecture is materially different from failed Stage 6C-C.
3. VMD has strong independent methodological authority.
4. But direct full-model execution would confound VMD, residual decomposition and WOA effects.
5. Our small monthly sample makes over-parameterized hybrid pipelines especially vulnerable to apparent in-sample/inner gains that do not transport.
6. Staged ablation preserves interpretability and matches the governance used in prior ANN/ANFIS/RBFNN families.

## Current authorization
AUTHORIZED NEXT: Stage 6C-D0 authority freeze + causal VMD-XGBoost DEV run.
NOT YET AUTHORIZED:
- Stage 6C-D1
- Stage 6C-D2
- full VMD-RES.-CEEMDAN-WOA-XGBoost
- ensemble
- 2025 holdout

## Governance
- DEV = 2022-04..2024-12 only
- 2025 = NOT OPENED
- 2026 = QUARANTINED / BLOCKED FROM DEVELOPMENT
- random split = NONE
- DB = READ_ONLY
- global decomposition = BLOCKED
