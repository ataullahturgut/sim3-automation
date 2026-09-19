# GOLD CONTROL — VLMC-BS FIXED-SHARE ENHANCEMENT V1 RESULT

**Date:** 2026-09-19  
**Parent:** `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`  
**Enhancement identity:** `DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH`  
**Status:** `REJECTED / NO_PROMOTION / 2025_GENERALIZATION_FAILED`

## Motivation

The corrected VLMC-BS family showed regime instability: the 52-week expert validated strongly in 2024 but weakened sharply in 2025, while the 104-week expert behaved relatively better in 2025. A literature-grounded response to changing-best-expert problems is Fixed-Share online expert tracking (Herbster & Warmuth, 1998), which reallocates weight among experts based only on past losses.

To preserve chronology, only VLMC-26 and VLMC-52 are used in the meta-model because both are available throughout the 2023 development block. VLMC-104 is not introduced later into the meta-model.

## Frozen experiment

Experts:
- corrected source-faithful VLMC-BS-26;
- corrected source-faithful VLMC-BS-52.

Expert probabilities come directly from the frozen V2 forecast surfaces.

At each target week:
1. combine expert probabilities using current weights;
2. classify UP iff combined P(UP)>=0.5;
3. after the realized direction becomes available, apply zero-one loss to each expert;
4. multiplicative loss update with learning rate eta;
5. Fixed-Share redistribution using share alpha;
6. carry weights forward chronologically.

Development grid, evaluated on 2023 only:
- eta in {0.25,0.5,1,2,4};
- alpha in {0,0.01,0.02,0.05,0.1,0.2}.

Selection rule:
1. maximize 2023 balanced accuracy;
2. minimize Brier score among ties;
3. prefer smaller alpha, then smaller eta if still tied.

Selected before 2024:
- eta = 1;
- alpha = 0.05.

No 2024 or 2025 outcome was used to choose eta or alpha.

## 2023 development

n=43:
- accuracy = 0.6046512;
- balanced accuracy = 0.6184211;
- UP sensitivity = 0.5000000;
- DOWN sensitivity = 0.7368421;
- forecast UP/DOWN = 17/26;
- Brier = 0.2962416;
- log loss = 2.5832831;
- always-UP accuracy = 0.5581395;
- previous-sign accuracy = 0.5348837.

End-2023 expert weights:
- VLMC-26 = 0.5982059;
- VLMC-52 = 0.4017941.

## 2024 fixed validation

Weights were carried forward unchanged from the 2023 development endpoint and updated online using the frozen rule.

n=53:
- accuracy = 0.6603774;
- balanced accuracy = 0.6595442;
- UP sensitivity = 0.7037037;
- DOWN sensitivity = 0.6153846;
- forecast UP/DOWN = 29/24;
- Brier = 0.2518638;
- log loss = 1.1798023;
- always-UP accuracy = 0.5094340;
- previous-sign accuracy = 0.5094340.

End-2024 weights:
- VLMC-26 = 0.5708201;
- VLMC-52 = 0.4291799.

Interpretation: validation is materially above trivial baselines, but it does not improve on the corrected standalone VLMC-BS-52 full-2024 result (accuracy 0.6792453; balanced accuracy 0.6780627).

## Locked 2025 test

Weights were carried forward from end-2024. No rule or parameter changed.

n=52:
- accuracy = 0.4807692;
- balanced accuracy = 0.3972973;
- UP sensitivity = 0.5945946;
- DOWN sensitivity = 0.2000000;
- TP/TN/FP/FN = 22/3/12/15;
- forecast UP/DOWN = 34/18;
- Brier = 0.3430915;
- log loss = 3.3246319;
- always-UP accuracy = 0.7115385;
- previous-sign accuracy = 0.5576923.

End-2025 weights:
- VLMC-26 = 0.5221456;
- VLMC-52 = 0.4778544.

## Decision

Fixed-Share does not solve the VLMC-BS regime-instability problem in this experiment.

Although the enhancement is reasonable for changing-expert environments and looked promising in 2023-2024, it fails decisively in the untouched 2025 replay:
- 48.08% raw accuracy;
- 39.73% balanced accuracy;
- only 3/15 DOWN weeks captured;
- worse than both the always-UP and previous-sign raw baselines;
- worse than corrected VLMC-BS-104 in 2025.

Binding status:

`DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH = REJECTED / NO_PROMOTION / 2025_GENERALIZATION_FAILED / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

Do not treat this Fixed-Share variant as a successful improvement. Further VLMC development, if authorized, must use a materially different mechanism rather than retuning this same Fixed-Share grid against 2025.
