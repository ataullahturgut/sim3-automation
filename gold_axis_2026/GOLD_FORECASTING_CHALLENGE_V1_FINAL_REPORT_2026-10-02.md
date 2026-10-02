# GOLD FORECASTING CHALLENGE V1 — FINAL REPORT

**Date:** 2026-10-02  
**Target:** Global XAU daily H3 UP/DOWN direction  
**Sealed test year:** 2021

## Integrity chain

1. Challenge contract frozen:
   - `GOLD_FORECASTING_CHALLENGE_V1_CONTRACT_2026-10-02.md`
   - commit `5a25a1f191815ea1043f153c9a110051e381444c`

2. Validation selection used only 2019-2020:
   - workflow run **37011922179**
   - selection evidence commit `875734b04557d42d93e4da74dcb1a9e9e8593870`
   - selection program explicitly loaded no post-2020 rows.

3. Champion locked before sealed test:
   - `GOLD_FORECASTING_CHALLENGE_V1_CHAMPION_LOCK_2026-10-02.json`
   - lock commit `627775a5388e8aa99744e9c4e7fce602edf53975`

4. Sealed 2021 evaluation:
   - workflow run **37013143077**
   - result evidence commit `4a1376a169ec78b264f7222e5e8bf3e69c7d78e1`

No 2021 target statistic was used to choose the champion.

## Validation winner

2019-2020 deterministic model selection chose:

- feature block: **CORE3**
- model: **Elastic-Net Logistic Regression**
- C = 0.30
- l1_ratio = 0.50

Validation metrics:
- n = 507
- accuracy = **54.83%**
- balanced accuracy = **54.63%**
- Brier = **0.24985**
- log loss = **0.69295**
- UP recall = **56.34%**
- DOWN recall = **52.91%**

## Sealed 2021 result

| Model | Accuracy | Balanced acc | False calls | Brier | Log loss | UP recall | DOWN recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| Expanding prior | 48.02% | 50.00% | 51.98% | **0.2512** | **0.6955** | 100.00% | 0.00% |
| CORE3 Logistic L2 comparator | 49.60% | 50.26% | 50.40% | 0.2527 | 0.6988 | 66.94% | 33.59% |
| **Locked CORE3 Elastic-Net champion** | **51.19%** | **51.92%** | **48.81%** | 0.2522 | 0.6977 | **70.25%** | 33.59% |

The locked champion improves direction metrics relative to both reference models, but the improvement is small.

Probability quality is not superior to the expanding-prior baseline:
- champion Brier 0.2522 vs prior 0.2512;
- champion log loss 0.6977 vs prior 0.6955.

## Frozen selective-call audit

Validation-derived confidence cutoffs were frozen before 2021.

| Rule | Coverage | Accuracy | Balanced acc | False calls |
|---|---:|---:|---:|---:|
| ~60% validation coverage cutoff | 61.51% | 50.97% | 52.31% | 49.03% |
| ~40% validation coverage cutoff | 46.03% | 50.00% | 52.52% | 50.00% |

The confidence filter does not create a high-accuracy subset in sealed 2021.

## Scientific interpretation

Challenge V1 demonstrates that disciplined pre-2021 model selection can extract a small H3 direction signal, but the sealed evidence is **not strong enough to call the resulting model a good forecasting model**.

What survives:
- balanced accuracy rises above 50%;
- false calls fall below 50%;
- Elastic-Net generalizes slightly better than the fixed L2 comparator.

What does not survive strongly:
- overall accuracy remains only 51.19%;
- DOWN recall remains weak at 33.59%;
- Brier/log loss do not beat the simple expanding-prior probability baseline;
- validation confidence does not identify a materially more accurate selective subset.

## Challenge conclusion

V1 is retained as a clean negative/weak-positive result.

The challenge should not be repaired after seeing 2021. Any further attempt must be a separately pre-registered **Challenge V2**, with a new model hypothesis and a different untouched test protocol.
