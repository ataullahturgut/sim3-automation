# OLD CIG-D1 2025 — EXECUTION-TARGET RESCORE RESULT

**Status:** COMPLETE / RETROSPECTIVE DIAGNOSTIC  
**Identity:** old CIG-D1 V1 unchanged; no retraining or new consensus selection.

## Identity reconstruction

- H3 rows: **248 / 248**
- V5 H3 correct: **165 / 248** (expected 165)
- SAGE V2 + RuleFlow V3-TG H3 correct: **171 / 248** (expected 171)
- Old 4/4 consensus rows: **218** (expected 218)
- Reconstruction QA: **PASS**

## Rescore on the two current execution targets

| Target | N | Correct | Direction accuracy | Clock usability |
|---|---:|---:|---:|---|
| 09:00 -> 17:00 Europe/Istanbul | 217 | 114 | **52.53%** | **NOT executable at 09:00** |
| 17:00 -> next eligible 09:00 Europe/Istanbul | 216 | 106 | **49.07%** | **Clock-compatible** |

### Signal-side detail

DAY 09->17:
- old-consensus UP calls: 74/131 = **56.49%**
- old-consensus DOWN calls: 40/86 = **46.51%**

OVERNIGHT 17->09:
- old-consensus UP calls: 70/130 = **53.85%**
- old-consensus DOWN calls: 36/86 = **41.86%**

## Critical interpretation

The DAY score is only a **retrospective alignment diagnostic**. The old CIG signal was governed for **08:00 America/New_York**, which is about **15:00/16:00 Türkiye time** in 2025. Therefore it could not have been known at the 09:00 origin of the new DAY target.

The OVERNIGHT target is different: the governed old-CIG issue deadline occurs before 17:00 Türkiye time, so its 17:00->next-09:00 rescore is clock-compatible as a historical execution diagnostic.

Neither result is prospective OOS evidence. No 2025 outcome was used here to alter the old consensus membership or direction.
