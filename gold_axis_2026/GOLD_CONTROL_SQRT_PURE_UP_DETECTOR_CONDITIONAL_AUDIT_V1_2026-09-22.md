# GOLD CONTROL — SQRT + PURE UP DETECTOR CONDITIONAL AUDIT V1

**Date:** 2026-09-22  
**Identity:** `SQRT_PURE_UP_DETECTOR_CONDITIONAL_AUDIT_V1_RESEARCH`  
**Purpose:** test the user's proposed simple architecture using the actual frozen pure-UP leaders from the manifest, not Router.

## 1. Frozen question

When SQRT emits a high-risk alarm:

- if the UP detector says UP -> predict UP;
- otherwise -> predict DOWN.

This audit compares:

1. `RV_LOGIT` — binding manifest leader on pooled pre-2025 pure-UP ranking (2023–2024).
2. `TTSM_S2` — binding manifest 2025 transport leader among the frozen daily pure-UP models, shown only as a secondary descriptive comparator.

Router is not used.

## 2. Governance

- no random split;
- no threshold tuning;
- RV_LOGIT uses frozen p>=0.50;
- TTSM-S2 uses its frozen UP signal exactly;
- 2025 and 2026 are not used in this audit;
- 2020–2024 are descriptive retrospective anatomy;
- because RV_LOGIT's "best pre-2025" identity was selected using pooled 2023–2024 evidence, 2020–2022 results here are retrospective characterization, not causal model-selection evidence;
- governed DB is read-only;
- no runtime promotion.

## 3. Primary populations

Report separately:

A. all frozen SQRT alarm rows;  
B. only those SQRT alarm rows where realized target downside-RV >= the same frozen yearly Q80 (`RISK_HIT`).

For each detector report coverage, UP precision, UP recall, false-UP FPR, DOWN precision, DOWN recall, ordinary accuracy and balanced accuracy under the exact rule `UP signal => UP; no UP signal => DOWN`.

## 4. Integrity

Frozen SQRT alarms must reproduce:
2020=212, 2021=28, 2022=11, 2023=2, 2024=17, pooled=270.

Frozen risk-hit anatomy must reproduce:
HIT_DOWN=115, HIT_UP=103, MISS=52.

Any mismatch blocks interpretation.
