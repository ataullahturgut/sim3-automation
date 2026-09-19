# GOLD CONTROL — DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH LOCKED 2025 REPLAY

**Date:** 2026-09-18  
**Identity:** `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`  
**Status:** `LOCKED_2025_REPLAY_COMPLETE / NO_PROMOTION`  
**Pre-2025 checkpoint commit:** `c08455979092d4641b972da67c3ae73964c4bb15`  
**2025 forecast freeze commit:** `5796969efc503ec1c9ee09513fbe5a3909dd6f63`

No cutoff, window, source construction, package path, threshold or bootstrap rule was changed after the pre-2025 checkpoint.

Corrected 2025 target distribution:
- 37 UP;
- 15 DOWN;
- always-UP accuracy = 0.7115385.

## Locked 2025 results

| Window | K* | Accuracy | Balanced | UP/DOWN forecasts | UP sens. | DOWN sens. | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 26 | 0.40 | 0.5769 | 0.5045 | 35 / 17 | 0.6757 | 0.3333 | 0.3799 | 7.2628 |
| 52 | 0.54 | 0.5769 | 0.4450 | 41 / 11 | 0.7568 | 0.1333 | 0.3532 | 6.2373 |
| 104 | 0.40 | **0.6154** | **0.5514** | 35 / 17 | 0.7027 | **0.4000** | **0.3135** | **4.6908** |

Confusion counts:
- k=26: TP/TN/FP/FN = 25/5/10/12;
- k=52: 28/2/13/9;
- k=104: 26/6/9/11.

Previous-week-sign raw accuracy is 0.5576923 for the same 2025 target set.

## Interpretation

The corrected V2 materially changes the scientific interpretation of the earlier V1.

- k=52 looked strongest in pre-2025 2024 validation (67.92% accuracy; 67.81% balanced accuracy), but does not generalize in 2025: 57.69% accuracy, 44.50% balanced accuracy and only 2/15 DOWN weeks captured.
- k=104 is the strongest 2025 member: 61.54% accuracy, 55.14% balanced accuracy and 6/15 DOWN weeks captured. It remains below the 71.15% always-UP raw-accuracy baseline and its pre-2025 evidence was materially weaker than k=52.
- k=26 provides nearly neutral balanced accuracy in 2025 and captures 5/15 DOWN weeks.

Therefore the family shows genuine two-sided pattern behavior, but no window demonstrates stable pre-2025-to-2025 generalization sufficient for standalone promotion.

Binding V2 status:

`EVALUATED / NO_PROMOTION / SOURCE_FAITHFUL_REFERENCE_REPLICATION_COMPLETE / 2025_GENERALIZATION_WEAK / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

V1 is retained as audit-only and is superseded for VLMC-BS family-level conclusions.
