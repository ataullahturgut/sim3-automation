# GOLD SESSION — BOCPD V1 STAGE-2 RESULT

**Status:** SESSION_BOCPD_V1_STAGE2_COMPLETE

- 2022: source/rank warm-up only.
- 2023–2024: development scoring.
- 2025/2026: not read.
- BOCPD V1 only; V4 hysteresis not used.

## Canonical BASE mapping — combined 2023–2024

| Partition | Window | Base | N | Handoff | ACT | R/B/Net | Precision | Base BA | Assisted BA | Base Acc | Assisted Acc | Gate |
|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | S17_A1_SESSION | 189 | 16 | 5 | 3/2/+1 | 60.0% | 52.18% | 52.77% | 52.38% | 52.91% | PASS_SOURCE_WEAK |
| SOBTI_5_ET | ASIA_MORNING_LIT | CORE3_A0 | 197 | 18 | 7 | 4/3/+1 | 57.1% | 53.57% | 54.19% | 54.31% | 54.82% | SOURCE_SENSITIVE_FAIL |
| SOBTI_5_ET | EUROPE_LIT | CORE3_A0 | 225 | 19 | 1 | 0/1/-1 | 0.0% | 51.41% | 51.01% | 52.00% | 51.56% | SOURCE_SENSITIVE_FAIL |
| SOBTI_5_ET | NY_LONDON_LIT | STRUCTURAL_IRIS_1H | 215 | 17 | 5 | 3/2/+1 | 60.0% | 53.26% | 53.74% | 53.49% | 53.95% | PASS_SOURCE_WEAK |
| SOBTI_5_ET | US_LATE_LIT | S17_A1_SESSION | 89 | 12 | 0 | 0/0/+0 | 0.0% | 50.23% | 50.23% | 51.69% | 51.69% | DEVELOPMENT_GATE_FAIL |
| WGC_2026_NY3 | ASIA | S15_SESSION_ONLY | 151 | 16 | 1 | 0/1/-1 | 0.0% | 55.66% | 55.17% | 59.60% | 58.94% | SOURCE_SENSITIVE_FAIL |
| WGC_2026_NY3 | EUROPE | STRUCTURAL_IRIS_1H | 209 | 18 | 1 | 0/1/-1 | 0.0% | 52.48% | 52.07% | 55.02% | 54.55% | SOURCE_SENSITIVE_FAIL |
| WGC_2026_NY3 | US | S18_A1_PATH_SESSION | 177 | 15 | 5 | 2/3/-1 | 40.0% | 50.89% | 50.38% | 51.41% | 50.85% | SOURCE_SENSITIVE_FAIL |

## Source sensitivity — combined net rescue

| Partition | Window | BASE | SI_n | NQ_n | ZN_v | CL_v | GC_n | NQ_c | Min | Median | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| SOBTI_5_ET | ASIA_AFTERNOON_LIT | 1 | 1 | 1 | 0 | 2 | 2 | 0 | 0 | +1.0 | PASS_SOURCE_WEAK |
| SOBTI_5_ET | ASIA_MORNING_LIT | 1 | -1 | -1 | -1 | -3 | 1 | 0 | -3 | -1.0 | SOURCE_SENSITIVE_FAIL |
| SOBTI_5_ET | EUROPE_LIT | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1.0 | SOURCE_SENSITIVE_FAIL |
| SOBTI_5_ET | NY_LONDON_LIT | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | +1.0 | PASS_SOURCE_WEAK |
| SOBTI_5_ET | US_LATE_LIT | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | +0.0 | DEVELOPMENT_GATE_FAIL |
| WGC_2026_NY3 | ASIA | -1 | -1 | -1 | -1 | 1 | 0 | 0 | -1 | -1.0 | SOURCE_SENSITIVE_FAIL |
| WGC_2026_NY3 | EUROPE | -1 | 0 | -1 | -1 | -1 | 0 | -1 | -1 | -1.0 | SOURCE_SENSITIVE_FAIL |
| WGC_2026_NY3 | US | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1 | -1.0 | SOURCE_SENSITIVE_FAIL |

## Frozen 2025 transport decision

- **SOBTI_5_ET / ASIA_AFTERNOON_LIT / S17_A1_SESSION** — PASS_SOURCE_WEAK
- **SOBTI_5_ET / NY_LONDON_LIT / STRUCTURAL_IRIS_1H** — PASS_SOURCE_WEAK

## Governance

The 2025 holdout remains closed in this run. Stage-2 cannot alter BOCPD parameters, Handoff thresholds, roll mapping, or the frozen session bases.
