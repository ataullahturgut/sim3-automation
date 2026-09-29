# GOLD MONTHLY — ChHHO F4 Rates Native Family Result

**Date:** 2026-09-29  
**Status:** COMPLETE / VALID FOR LEGACY ENDPOINT REPRESENTATION ONLY / SUPERSEDED FOR FAMILY DECISION  
**Decision:** DO NOT INTERPRET AS FAMILY-WIDE RATES REJECTION

## Authority
- corrected run: **36550570628**
- head commit: **6df3eead1a4bf7734a2753ccd86a5cf72ba2a9f2**
- summary artifact: **11025216884**
- digest: `sha256:640ab422603e81c7ea420ab9f9349ab6358882ce6cc784dcada0f52c52c4269f`
- baseline artifact: **11023949755**
- Neon reads: **0**
- 2025/2026 selection use: **NONE**
- random split: **NONE**

## Baseline parity
- canonical BASE: **1413.029779 / 23/33**
- observed BASE: **1413.029779 / 23/33**
- parity: **PASS**

## Native static candidates
| Candidate | DEV ΣAE | Direction |
|---|---:|---:|
| BASE | **1413.0298** | **23/33** |
| R_BE10 | 1691.8333 | 19/33 |
| R_REAL_BE | 2063.7075 | 21/33 |
| R_NOM10 | 3730.6040 | 21/33 |
| R_REAL10 | 3837.7884 | 22/33 |
| R_NOM_REAL | 13624477.7928 | 19/33 |

## Chronological inner-family routed result
- routed ΣAE: **1657.1153**
- routed direction: **21/33**
- ΔΣAE vs BASE: **-244.0855**
- pct improvement: **-17.27%**
- months improved / tied / worsened: **9 / 9 / 15**
- median paired AE improvement: **0.0**
- year ΔΣAE vs BASE:
  - 2022: **-89.5792**
  - 2023: **-141.5176**
  - 2024: **-12.9887**
- min leave-one-origin total improvement: **-283.7625**
- promotion gate: **FAIL**

Router usage:
- BASE 9
- R_BE10 7
- R_REAL10 8
- R_NOM10 3
- R_NOM_REAL 2
- R_REAL_BE 4

## Interpretation
Rates contained incremental information in earlier residual-correction screens, but **native integration into ChHHO-ANFIS does not improve the frozen baseline under the F4 charter**. This is not contradictory: residual correction and native architecture integration are different estimation problems.

The two-feature nominal+real candidate is pathologically unstable and is treated as an architecture-stability diagnostic, not as a literal economic statement.

## Supersession decision

This result remains valid for the exact endpoint-change native implementation tested in run 36550570628.

It is **superseded for family-level inference** because the later F4 reset found:
- processing-parity mismatch versus CURRENT8 MR1+VW;
- frequency under-use of daily rate paths;
- optimizer search-density reduction as input dimension increased.

Therefore:
- do not label Rates economically useless;
- do not use this result to block the redesigned Rates restart;
- retain it only as negative evidence for the legacy endpoint-change implementation.

Current authority:
`GOLD_MONTHLY_F4_RESET_PROCESSING_PARITY_AUDIT_2026-09-29.md`.

## Superseded run
Run **36549022859** is **SUPERSEDED_METHODOLOGY / NOT SCIENTIFIC RESULT** because its BASE began at 2010-04 and failed canonical baseline parity.

## Kontrol ve Uyum Özeti
- BASE parity: PASS
- Native Rates improvement: NO
- Promotion: FAIL
- 2025 tuning: NONE
- 2026 tuning: NONE
- Neon: 0
- Next: F4-FX
