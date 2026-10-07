# SESSION OPAL — READINESS / IDENTITY AUTHORITY

**Date:** 2026-10-07  
**Status:** DATA_READY / MODEL_BLOCKED_UPSTREAM_AURORA

## Role

OPAL is an options-positioning / COT reversal specialist. It is not a primary direction engine.

Historical H3 OPAL identity:
- baseline/upstream = AURORA direction probability;
- reversal target = actual direction differs from pre-target momentum sign;
- fixed reversal threshold = 0.70;
- correction only when AURORA follows momentum and OPAL reversal probability >= 0.70;
- otherwise keep AURORA.

## Historical OPAL feature identity

Canonical H3 OPAL used 18 variables:

- opt_mm_net
- opt_prod_net
- opt_swap_net
- opt_other_net
- d_opt_mm_net
- d_opt_prod_net
- opt_mm_z52
- opt_prod_z52
- opt_swap_z52
- opt_other_z52
- spec_hedger_gap
- spec_swap_gap
- fut_mm_net
- fut_prod_net
- trend_x_opt_mm
- trend_x_opt_prod
- trend_x_spec_hedger_gap
- trend_strength

Estimator:
- StandardScaler
- LogisticRegression(C=1.0, class_weight=balanced)
- fixed threshold = 0.70

The historical H3 implementation is **not** session evidence and may not be copied into the session project without rebuilding its upstream and timing contract.

## Corrected COT authority — READY

Authorities:
- `GOLD_COT_PIT_REAUDIT_SUMMARY_2026-10-06.json`
- `GOLD_COT_PUBLICATION_CALENDAR_PIT_V1.csv`
- `GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv`
- `GOLD_V5_SESSION_COT_AVAILABILITY_MAP_2023_2025.csv`
- `GOLD_OPAL_OLD_PROVEN_EARLY_COT_ROWS_2026-10-06.csv`

Raw source:
- official CFTC Public Reporting Environment
- Gold contract code `088691`
- futures-only disaggregated dataset `72hh-3qpy`
- futures+options combined disaggregated dataset `kh3c-gbw2`

Rebuilt report rows:
- 1,060
- first report: 2006-06-13
- last report in audit: 2026-09-29

## Correct publication-time rule

The old fixed date-only `report_date + 7 days` assumption is superseded.

Binding governed availability:
- default = report date + 7 calendar days at **15:30 America/New_York**;
- if an official documented delayed CFTC publication is later, use that later official publication date at 15:30 ET;
- a feature row may use a COT report only when
  `cot_available_at_utc <= feature_cutoff_or_target_start_utc`.

This corrected audit reproduces:
- legacy OPAL rows audited = 1,029
- proven early-use rows = 74
- 2023 early-use = 21
- 2025 early-use = 53
- rows whose selected report changes under corrected PIT = 74

Therefore archived OPAL/HELIOS predictions that depended on those rows are not PIT-clean session evidence.

## Session COT mapping

All current final-trainable WGC/Sobti session rows in 2023–2025 can be mapped to an eligible governed COT report under the corrected publication-time rule.

Therefore:

**COT DATA AVAILABILITY = READY**

This establishes data readiness only, not OPAL model readiness.

## Upstream dependency — BLOCKED

The OPAL correction rule requires a fresh upstream **AURORA** state/probability plus pre-target momentum.

Repository audit on 2026-10-07 finds:
- historical H3 AURORA artifacts exist;
- **no fresh SESSION AURORA artifact exists**;
- archived H3 AURORA predictions cannot be used as session inputs;
- no hidden or alternate session AURORA authority was found.

Historical AURORA identity is a router between:
- STRUCTURAL_IRIS
- PATH_GLOBAL

with:
- SENTRY fast entry using latest 63 matured paired-rescue history, minimum 42, enter PATH at net rescue >= +3;
- DART slow exit using disagreement posterior, minimum 8 disagreements, return to STRUCTURAL when Pr(PATH superior) <= 0.10 and q_path <= 0.40.

Those H3 ledgers/states cannot be transplanted into session clocks.

## Current OPAL readiness verdict

- corrected raw COT = **READY**
- corrected COT publication timestamp = **READY**
- V5 session COT as-of mapping = **READY**
- OPAL historical feature identity = **KNOWN**
- OPAL historical correction rule = **KNOWN**
- fresh session momentum state = reconstructable from governed XAU
- fresh session AURORA probability/state = **MISSING**
- session OPAL fit/replay = **BLOCKED_UPSTREAM_AURORA**
- session HELIOS downstream of OPAL = **BLOCKED**

## Binding next action

Do **not** run OPAL yet.

First reconstruct a fresh session-native AURORA from fresh session Structural-IRIS and PATH_GLOBAL outputs using matured same-window evidence only.

Only after SESSION AURORA is closed may OPAL be rebuilt with:
- corrected COT publication-time authority;
- fresh session AURORA state;
- pre-target session momentum;
- 2023–2024 development;
- frozen 2025 transport;
- 2026 unopened.

No archived H3 AURORA/OPAL prediction file may substitute for that rebuild.
