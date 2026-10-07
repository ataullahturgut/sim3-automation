# GOLD SESSION — DPTC FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** **COMPLETE / DEVELOPMENT-BLOCKED BY INSUFFICIENT 2023 SESSION-SELLR HISTORY / NOT PROMOTED / 2025 NOT OPENED / 2026 DATA-BLOCKED**

## 1. Identity

DPTC was not allowed to consume historical H3 SELLR scores, H3 SELLR bin tables, H3 reversal labels, or the historical numeric threshold `2.3677413378977423`.

The original SELLR producer lineage was recovered and its algorithmic idea was ported as a new **SESSION-SELLR V1** identity:

`signed feature -> quintile bin -> Laplace-smoothed log P(bin|SESSION reversal) / P(bin|SESSION continuation) -> additive score`.

The new SESSION chronology was preregistered before results:
- 2023 = SESSION-SELLR fitting/calibration only;
- 2024 = untouched development;
- 2025 = closed until the 2024 transport gate;
- 2026 = unread.

## 2. Stage-2 feature coverage

The SESSION-safe eleven-feature panel was successfully reconstructed, but exact-common 2023 history was too short for the frozen minimum training requirement of **80 rows per partition/window**.

| Partition | Window | Total N | 2023 N | 2024 N |
|---|---|---:|---:|---:|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 191 | 51 | 140 |
| SOBTI_5_ET | ASIA_MORNING_LIT | 205 | 69 | 136 |
| SOBTI_5_ET | EUROPE_LIT | 225 | 77 | 148 |
| SOBTI_5_ET | NY_LONDON_LIT | 215 | 65 | 150 |
| SOBTI_5_ET | US_LATE_LIT | 89 | 0 | 89 |
| WGC_2026_NY3 | ASIA | 152 | 61 | 91 |
| WGC_2026_NY3 | EUROPE | 210 | 62 | 148 |
| WGC_2026_NY3 | US | 177 | 35 | 142 |

Maximum available 2023 same-window history was **77 rows** (Sobti Europe), below the preregistered minimum of 80.

Therefore:
- no SESSION-SELLR specification was fitted;
- no SESSION-SELLR threshold was selected;
- no DPTC-Q95/Q99 development action was authorized;
- no 2024 DPTC transport gate could be evaluated as eligible;
- 2025 remained closed.

## 3. Why the model was not forced

The project must not lower `MIN_SELLR_TRAIN=80` after observing this result merely to make DPTC run.

Doing so would create a new, post-result model identity.

Likewise, the project must not:
- pool unrelated session windows after seeing the shortage;
- substitute H3 SELLR bins or scores;
- reuse the H3 threshold `2.3677413378977423`;
- use 2024 outcomes to manufacture a 2023 calibration set;
- open 2025 to choose a lower training minimum.

Any future attempt would require a separately preregistered successor, for example:
- a 2022+2023 SESSION-SELLR warmup identity if the full eleven-feature source history can be reconstructed causally for 2022; or
- a preregistered hierarchical/pooling design justified before outcomes are opened.

Neither is part of DPTC V1 closed here.

## 4. Clock / horizon integrity

The DPTC Stage-2 implementation remained consistent with the SESSION horizon contract:

- corrected SESSION target identity;
- intraday XAU features strictly before session start;
- CME daily option state from prior trade dates only;
- daily cross-market/topology state from prior dates only;
- topology advances as a daily process, not once per session;
- same-window momentum `trend_age`;
- canonical SESSION Handoff reconstructed from raw-source state;
- adaptive TRUST state isolated by partition/window;
- only prior acted outcomes matured by `end_utc <= current start_utc` can update hysteresis.

The failure is therefore **not a horizon leakage failure**. It is a governed sample-support failure.

## 5. 2025

**NOT OPENED.**

Because no SESSION-SELLR head could satisfy the pre-registered fitting requirement, there was no valid DPTC head eligible for frozen 2025 transport.

No 2025 outcome was used to alter:
- SELLR training minimum;
- feature set;
- threshold grid;
- dependence phase;
- TRUST hysteresis;
- baseline membership.

## 6. 2026

**DATA_BLOCKED / NOT RUN.**

No governed V5-equivalent 2026 SESSION target population is currently available. Daily/H3 labels are not substituted.

## 7. Binding decision

1. DPTC SESSION research line is **COMPLETE for the current identity**.
2. The original SELLR producer lineage is resolved.
3. Historical H3 SELLR is confirmed horizon-dependent and remains prohibited as a SESSION input.
4. SESSION-SELLR V1 could not be fitted under the frozen 2023-only minimum-history rule.
5. DPTC is **NOT PROMOTED**.
6. 2025 remains **UNOPENED**.
7. Do not lower the minimum history or pool windows post hoc.
8. Proceed to the next meta-controller family only under its own horizon/clock identity audit.

## Authorities

- `GOLD_SESSION_DPTC_V1_STAGE1_HORIZON_CLOCK_IDENTITY_AUTHORITY_2026-10-07.md`
- `GOLD_SESSION_DPTC_STAGE1B_SELLR_LINEAGE_RECONSTRUCTION_AUTHORITY_2026-10-07.md`
- `GOLD_SESSION_DPTC_STAGE1C_STAGE2_PREREG_2026-10-07.md`
- `GOLD_SESSION_DPTC_STAGE2_RESULT_2026-10-07.md`
- `GOLD_SESSION_DPTC_STAGE2_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_DPTC_STAGE2_FEATURE_COVERAGE_2026-10-07.csv`
