# GOLD MONTHLY FORECAST — ELMFIS STAGE 3C CQCSA

**Date:** 2026-09-26  
**Status:** STAGE 3C COMPLETE

## Authority and method provenance

CQCSA-ELMFIS is based on:
Sudeepa Das, Tirath Prasad Sahu, Rekh Ram Janghel,
"Oil and gold price prediction using optimized fuzzy inference system based extreme learning machine",
Resources Policy 79 (2022) 103109,
DOI: 10.1016/j.resourpol.2022.103109.

The paper proposes Cluster-based Quasi-oppositional Crow Search Algorithm (CQCSA) to optimize ELMFIS parameters for oil/gold forecasting.

This project implementation is an origin-safe adaptation to the frozen monthly H=1 ELMFIS problem and is **not claimed as exact source-code reproduction**.

Adapted optimizer elements:
- CSA awareness probability = 0.10.
- flight length = 2.0.
- population = 24.
- fitness-derived clustering into 4 groups.
- best member of each group acts as local leader.
- quasi-opposite candidate sampled coordinate-wise between search midpoint and opposite point.
- iteration-dependent worst-crow quasi-opposition replacement following the paper's decaying replacement concept.
- ELMFIS search scope remains antecedent centers + log-spreads only.
- TSK consequents remain analytic ridge.

Frozen forecasting authority:
- DEV 2022-04..2024-12 only for selection/tuning.
- 2025 reporting only.
- 2026 reporting only.
- no random split.
- DB READ_ONLY.
- target-month leakage prohibited.
- frozen 8-feature VW-MIDAS contract.

## DEV result

| Model | DEV ΣAE USD | Direction | MAE | RMSE | Rel MAE vs RW |
|---|---:|---:|---:|---:|---:|
| CQCSA-ELMFIS | **1,731.94** | **20/33 = 60.61%** | 52.48 | 66.25 | 0.9852 |

Reference ELMFIS frontier:
- ABC-ELMFIS: 1,524.89 / 21/33.
- SMA-ELMFIS: 1,651.45 / 25/33.

CQCSA is dominated by both frontier candidates and therefore adds no DEV Pareto point.

## Reporting-only external periods

| Period | ΣAE USD | Direction |
|---|---:|---:|
| 2025 | 1,427.10 | 7/12 = 58.33% |
| 2026 Jan-Jul | 4,611.31 | 5/7 = 71.43% |

2026 shows material price-error instability. This is robustness evidence only and did not affect DEV selection.

## Run

Workflow run: **36193027498 — SUCCESS / OUTPUT_GATE=PASS**  
Artifact: **10888718921**  
Implementation: `gold_axis_2026/tools/vw_midas_elmfis_stage3c_cqcsa_v1.py`  
Workflow: `.github/workflows/gold-midas-elmfis-stage3c-cqcsa-v1.yml`

## Decision

- Stage 3C: COMPLETE.
- CQCSA new Pareto point: NO.
- CQCSA promotion: NO.
- ELMFIS price frontier remains ABC + SMA.
- Next: corrected cross-family re-audit under ΣAE + direction.
