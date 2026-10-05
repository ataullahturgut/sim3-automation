# SILVER SHORT-HORIZON V5 — SELECTIVE CONFIDENCE GATE PREREGISTRATION

**Date:** 2026-10-05  
**Identity:** `GLOBAL_XAG_SELECTIVE_H5_V5`  
**Status:** PREREGISTERED BEFORE 2025/2026 V5 TRANSPORT IS OPENED.

## Motivation

V1-V4 show that forced H5 direction is weak and non-transporting.  
Silver consensus across daily information blocks does not create a stable uncertainty separation on DEV.

V5 therefore tests a simpler selective-prediction hypothesis:

> Does the frozen H5 Silver-path Logistic become useful if it acts only when its probability is sufficiently far from 0.50?

## Base model

Exactly the V1/V2 H5 Silver-path standardized Logistic L2.

No new features.

## Candidate confidence gates

Act only if:
- p_up >= t, or
- p_up <= 1-t.

Candidate t values, frozen before transport:
- 0.52
- 0.53
- 0.54
- 0.55

Otherwise output ABSTAIN.

## DEV selection

2022-2024 expanding maturity-safe DEV predictions only.

Eligibility:
- aggregate coverage >= 30%;
- aggregate selective balanced accuracy > 50%.

Selection:
1. highest selective balanced accuracy;
2. if within 1 percentage point, higher coverage;
3. annual stability flag reported; two DEV years below 50% BA disqualifies promotion.

After the gate is selected, 2025/2026 may be opened once for transport reporting only.

No threshold may be changed from 2025/2026 outcomes.
