# GOLD MONTHLY — F4 B2 PROCESSING + OPTIMIZER PARITY AUDIT

**Date:** 2026-09-29  
**Status:** COMPLETE / PASS  
**Scope:** Pre-model parity gate before ALL6-COMPACT  
**Model outcome produced:** NO

## 1. Authoritative run

- workflow: **Gold Monthly F4 B2 Processing Optimizer Parity V1**
- run: **36564452306**
- head commit: **78ca76a51e5a44050eaa5600fec7213758e6e1c3**
- artifact: **11031577274**
- artifact digest: `sha256:f28c2175a3207b743baa99198e7f80f961366e13b81d89f40adddca58436a331`
- Neon reads: **0**
- overall gate: **PASS**

Earlier run **36564354047** failed at the workflow-level Neon-disabled shell assertion because variable expansion was escaped literally. It did not reach data/model audit and is classified **TECHNICAL_WORKFLOW_FAILURE / NOT_SCIENTIFIC_RESULT**.

## 2. B1 revalidation

The authoritative B1 artifact was consumed as an input gate rather than assumed from prose.

- B1 artifact: **11028839840**
- B1 gate: **PASS**
- External Authority V2 payload match: **PASS**
- frozen DEV snapshot payload match: **PASS**
- B1 VW formula parity remains valid.

## 3. B2-A processing / preprocessing parity

**PASS**

Checks:
- 33 DEV outer origins checked: 2022-04..2024-12.
- ALL6 design matrix = **22 columns** = CURRENT8 8 + external 14.
- no canonical-history shortening; first training sample remains 2010-03.
- target/future rows do not enter training.
- the same vectorized feature scaler spans columns 0:8 and 8:22.
- inner scaler is fitted on chronological inner-training rows only.
- validation rows use the inner-training scaler.
- full refit scaler is fitted on all pre-target history only.
- target row is transformed after scaler fit and never enters scaler estimation.
- CURRENT8 and external variables use the same ANFIS `select` path, antecedent/consequent path, local-refit path and target reconstruction.
- no family-specific downstream scaler or shortcut is allowed.

Interpretation: after the family-specific MR/VW analogue construction, new external inputs enter the model through the same downstream preprocessing/model pipeline as CURRENT8.

## 4. B2-B optimizer + BASE parity

**PASS**

Frozen BASE was rerun through the same ChHHO-ANFIS path:

- reference DEV ΣAE: **1413.0297794085**
- observed DEV ΣAE: **1413.0297794084559**
- reference direction: **23/33**
- observed direction: **23/33**
- BASE inputs: 8
- BASE antecedent dimension: 80
- BASE POP: 24

ALL6 optimizer parity:

- total inputs: **22**
- rules: **5**
- antecedent parameter dimension: **220**
- population rule: `POP(k)=ceil(24*(10*k)/80)`
- ALL6 POP: **66**
- generations: **45**
- repeats: **3**
- generated optimizer population shape: **66 × 220**
- population-per-parameter density is not below BASE.

## 5. Gate decision

- B1 transform parity: **PASS**
- B2-A processing/preprocessing parity: **PASS**
- B2-B optimizer + BASE parity: **PASS**

Therefore the parity gate required before ALL6-COMPACT is closed successfully.

**Next authorized scientific experiment:** ALL6-COMPACT diagnostic challenger.

ALL6 has **not** been run by this audit. 2025 and 2026 remain excluded from selection.
