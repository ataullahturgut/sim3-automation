# RBFNN Stage 1 — artifact audit and cumulative results

Selection authority: DEV 2022-04..2024-12 only. 2025/2026 reporting only. No parent frozen.
Exact optimizer equations/constants: source file, function and SHA256 in each artifact. Population 24, generations 45, repeats 3.
Script `gold_axis_2026/tools/vw_midas_rbfnn_stage1_v1.py`; workflow `.github/workflows/gold-monthly-rbfnn-stage1-v1.yml`.
Numerical audit checks all available rows, chronology, full-period coverage, invariant equality, DEV freeze hash and recomputed metrics.

| Model | DEV ΣAE | Direction | MAE | RMSE | RW relative MAE | RW wins | Worst AE | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| ACO | 1481.9468 | 19/33 | 44.9075 | 57.7832 | 0.84297 | 18/33 | 152.5209 | PASS |
| WOA | 1499.2639 | 19/33 | 45.4322 | 60.5691 | 0.85282 | 18/33 | 157.4068 | PASS |
| BAT | 1501.6410 | 21/33 | 45.5043 | 58.1928 | 0.85418 | 16/33 | 152.4168 | PASS |
| MPA | 1510.5118 | 20/33 | 45.7731 | 61.0286 | 0.85922 | 18/33 | 153.0577 | PASS |
| GWO | 1511.6245 | 22/33 | 45.8068 | 62.1607 | 0.85985 | 19/33 | 158.3893 | PASS |
| GA | 1523.4710 | 19/33 | 46.1658 | 59.2889 | 0.86659 | 16/33 | 157.9942 | PASS |
| DE | 1550.2583 | 18/33 | 46.9775 | 60.5498 | 0.88183 | 17/33 | 146.9444 | PASS |
| ABC | 1558.8168 | 18/33 | 47.2369 | 60.9410 | 0.88670 | 17/33 | 150.7081 | PASS |
| SSA | 1559.8246 | 18/33 | 47.2674 | 59.4641 | 0.88727 | 15/33 | 153.1977 | PASS |
| HHO | 1586.1569 | 20/33 | 48.0654 | 60.9390 | 0.90225 | 18/33 | 141.8358 | PASS |
| PSO | 1598.5085 | 20/33 | 48.4397 | 65.2068 | 0.90928 | 18/33 | 167.8131 | PASS |

## External reporting — excluded from selection

| Model | 2025 ΣAE | 2025 direction | 2026 Jan–Jul ΣAE | 2026 direction |
|---|---:|---:|---:|---:|
| ABC | 1168.1027 | 8/12 | 1554.4114 | 5/7 |
| ACO | 1175.0249 | 9/12 | 1684.5221 | 5/7 |
| BAT | 1037.0801 | 8/12 | 1526.1445 | 5/7 |
| DE | 1115.9977 | 9/12 | 1665.7461 | 4/7 |
| GA | 989.9040 | 10/12 | 1560.4409 | 5/7 |
| GWO | 1203.3243 | 8/12 | 1661.8822 | 5/7 |
| HHO | 1109.8340 | 10/12 | 1404.7751 | 6/7 |
| MPA | 1103.2103 | 8/12 | 1490.3723 | 5/7 |
| PSO | 1031.3426 | 11/12 | 1475.5659 | 5/7 |
| SSA | 999.5913 | 9/12 | 1561.0808 | 5/7 |
| WOA | 1157.8414 | 10/12 | 1526.8745 | 5/7 |

## Provenance and decisions

- ABC: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_2_v1.py` / `abc_phase`.
- ACO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_3_v1.py` / `aco_phase`.
- BAT: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_3_v1.py` / `bat_phase`.
- DE: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_1_v1.py` / `de_phase`.
- GA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_1_v1.py` / `ga_phase`.
- GWO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_2_v1.py` / `gwo_phase`.
- HHO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_3_v1.py` / `hho_phase`.
- MPA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_2_v1.py` / `mpa_phase`.
- PSO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_1_v1.py` / `pso_phase`.
- SSA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_2_v1.py` / `ssa_phase`.
- WOA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_3_v1.py` / `woa_phase`.

Job/artifact IDs are recorded in the main ledger batch entries and evidence provenance JSON.

Completed artifacts audited: 11/32. Scientific failures retained; no missing rows silently dropped.
Next: finish remaining Stage-1 batches; only then Stage-2 filtering/parent freeze.
