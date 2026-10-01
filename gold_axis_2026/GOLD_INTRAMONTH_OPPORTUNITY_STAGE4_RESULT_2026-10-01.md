# GOLD INTRAMONTH OPPORTUNITY — Stage 4 Monthly Context Incremental Test Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / NO_CONTEXT_PASS**  
**Workflow:** Gold Intramonth Opportunity Stage4  
**Run:** **36865648243**  
**Artifact:** **11164440527**  
**Artifact digest:** `sha256:ff16d38d3114efa1650e05b250af8c6646d6b1895097a0234511d4acf3965ccb`  
**Runner commit:** `b21e1ce2c685da44331e42e7edac79b703e522ea`  
**Authority:** `GOLD_INTRAMONTH_OPPORTUNITY_STAGE4_AUTHORITY_2026-10-01.md`

## 1. Binding conclusion

**No monthly-context block improves the frozen Stage-3 K100 core under the preregistered promotion gate.**

Therefore the current production/research core remains:

- target: **K100**
- model: **G_ONLY / HGB_CLASS**
- monthly direction: descriptive context only
- monthly forecast magnitude: not promoted
- T0 monthly reliability: not promoted
- previous-month regime/state: not promoted.

The project must **not** hard-code “monthly DOWN” into the K100 predictor.

## 2. Evaluation protocol

Stage-4 DEV:
- target months: **2022-04..2024-12**
- daily origins: **685**
- monthly-DOWN origins: **392**
- monthly-UP origins: **293**.

No 2025/2026 data were used.

The frozen Stage-3 HGB core was not retuned.

Monthly context entered only through a low-capacity chronological logistic overlay on the frozen core probability.

The invalid/pathological historical H1 ChHHO replay was excluded from context learning.

Valid pre-DEV monthly forecast context:
- 2021-11..2022-03 same-method H2 only.

## 3. Frozen CORE_ONLY reference on the common Stage-4 population

- Brier: **0.184211**
- log loss: **0.553937**
- PR-AUC: **0.2971**
- ROC-AUC: **0.5967**
- prediction SD: **0.0894**.

This is the apples-to-apples reference for every context block.

## 4. Context-block results

| Context block | Brier | Relative vs core | Log loss | DOWN Brier relative vs core | Fallback rows | Decision |
|---|---:|---:|---:|---:|---:|---|
| **CORE_ONLY** | **0.18421** | — | **0.55394** | — | 0 | **RETAIN** |
| CORE_DIR | 0.18571 | **-0.81%** | 0.55673 | **-7.59%** | 0 | FAIL |
| CORE_MAG | 0.19516 | **-5.95%** | 0.58236 | **-16.24%** | 0 | FAIL |
| CORE_DIR_MAG | 0.19527 | **-6.00%** | 0.57987 | **-17.21%** | 0 | FAIL |
| CORE_DIR_MAG_T0REL | 0.20220 | **-9.76%** | 0.60118 | **-16.55%** | 66 | FAIL |
| CORE_ALL_SAFE | 0.20918 | **-13.55%** | 0.65312 | **-12.72%** | 66 | FAIL |
| CORE_DIR_MAG_STATE | 0.21241 | **-15.31%** | 0.65414 | **-33.46%** | 0 | FAIL |

All context overlays fail.

## 5. Why this matters

Stage 3 showed a descriptive fact:

> The frozen K100 core itself performs materially better than its historical baseline inside monthly-DOWN origins.

That does **not** imply that monthly DOWN should be added as an explicit predictor.

Stage 4 directly tests that hypothesis and rejects it.

### Direction-only overlay

Adding only monthly UP/DOWN:
- worsens overall Brier by **0.81%**
- worsens monthly-DOWN Brier by **7.59%**
- worsens log loss.

Therefore:

**Monthly direction is useful for reporting/slicing, not for model augmentation under the current architecture.**

## 6. Forecast magnitude

Adding monthly predicted log-return magnitude performs substantially worse:

- CORE_MAG Brier deterioration: **5.95%**
- DOWN-slice deterioration: **16.24%**.

Direction + magnitude together:
- overall deterioration: **6.00%**
- DOWN deterioration: **17.21%**.

No monthly forecast-magnitude promotion.

## 7. Reliability context

To preserve timing, the test uses only **T0-safe** monthly reliability information.

It does not apply T1_WGC or full target-month router p_HIGH before those signals are actually available.

CORE_DIR_MAG_T0REL:
- Brier deterioration: **9.76%**
- DOWN deterioration: **16.55%**
- 66 early rows conservatively fallback to frozen core due insufficient prior T0-context history.

No reliability overlay promotion.

## 8. Previous-month regime/state

Causal state block uses only prior completed month:
- R0/R1/R2/BELIRSIZ
- state posterior
- OOD
- Transition V2
- Extreme/DEFER.

CORE_DIR_MAG_STATE:
- Brier deterioration: **15.31%**
- DOWN deterioration: **33.46%**
- log loss materially worse.

Interesting but non-promotable:
- ROC-AUC rises to about **0.6173**
- PR-AUC about **0.3118**

However probability calibration degrades badly, and the project’s primary probability metrics are Brier/log loss.

Therefore state context is **not promoted**.

## 9. Combined context

CORE_ALL_SAFE:
- Brier deterioration: **13.55%**
- log-loss deterioration: **17.91%**
- DOWN Brier deterioration: **12.72%**.

Combining weak context channels does not rescue them.

## 10. Scientific interpretation

The evidence now supports a more precise architecture:

### What works
- Gold’s own recent daily path contains modest origin-safe information about **strong volatility-adjusted 5-observation rallies (K100)**.

### What does not add value
- monthly forecast direction
- monthly forecast magnitude
- T0 monthly reliability
- prior-month regime/state

when used as learned probability overlays.

This suggests that the useful tactical signal is primarily **local path structure**, not a simple top-down monthly conditioning rule.

## 11. Governance resolution

Do not:
- suppress K100 because the monthly forecast is DOWN;
- boost K100 probability because monthly forecast is UP;
- recalibrate K100 from monthly return magnitude;
- multiply K100 by monthly p_HIGH/reliability;
- gate K100 on R0/R1/R2/Transition/Extreme.

Monthly information may remain visible alongside the daily opportunity score for interpretation, but does not alter the frozen probability.

## 12. Artifact hashes

- `stage4_context_audit_table.csv`: `e264a38b3501eec16590301f7d232784c1594484932af822c84f5abad09b0e0d`
- `stage4_dev_predictions.csv`: `0f90aa98407bd6115364eceb9c4dc17364bdcea4c85bad6d75486b124b32e423`
- `stage4_metrics.csv`: `0b3df99933b49a4e702f86d00a0192a20253f96d19a38df9839b68c14992e2ff`
- `stage4_slice_metrics.csv`: `925dcaa56b915aba0f53fe70c9228f1d2cc5c8432197b80ae7c6b50630b433c0`
- `stage4_year_metrics.csv`: `068bb2b1837170bdc6b011c6930d0fed40e4f18fbc526489748795e94bad8e54`
- `STAGE4_RESULT.md`: `cbb6358ce9977fc931b5d59f63f0c6b8ca16fa8227f4a04122ec9c5cc662955c`

## 13. Decision and next stage

**Stage 4 = COMPLETE / NO_CONTEXT_PASS.**

Retain:
**Stage-3 CORE_ONLY K100 G_ONLY/HGB_CLASS.**

Exact next stage:

**Stage 5 — K100 Robustness, Calibration & Decision-Threshold Audit**

Stage 5 should:
- test calibration stability by year / monthly-DOWN / volatility bucket;
- compare raw HGB probability vs chronology-safe calibration methods;
- define whether a usable opportunity alert threshold can be frozen;
- measure precision / recall / false-opportunity rate at candidate thresholds;
- keep K100 target and G_ONLY HGB architecture frozen;
- use DEV only for threshold/calibration selection;
- do not inspect 2025 until the full Stage-5 rule is frozen.
