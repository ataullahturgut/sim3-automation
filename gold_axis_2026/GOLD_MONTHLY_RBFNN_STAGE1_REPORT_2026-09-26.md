# RBFNN Stage 1 — artifact audit and cumulative results

Selection authority: DEV 2022-04..2024-12 only. 2025/2026 reporting only. No parent frozen.
Exact optimizer equations/constants: source file, function and SHA256 in each artifact. Population 24, generations 45, repeats 3.
Script `gold_axis_2026/tools/vw_midas_rbfnn_stage1_v1.py`; workflow `.github/workflows/gold-monthly-rbfnn-stage1-v1.yml`.
Numerical audit checks all available rows, chronology, full-period coverage, invariant equality, DEV freeze hash and recomputed metrics.

| Model | DEV ΣAE | Direction | MAE | RMSE | RW relative MAE | RW wins | Worst AE | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| GA | 1523.4710 | 19/33 | 46.1658 | 59.2889 | 0.86659 | 16/33 | 157.9942 | PASS |
| DE | 1550.2583 | 18/33 | 46.9775 | 60.5498 | 0.88183 | 17/33 | 146.9444 | PASS |
| PSO | 1598.5085 | 20/33 | 48.4397 | 65.2068 | 0.90928 | 18/33 | 167.8131 | PASS |

## External reporting — excluded from selection

| Model | 2025 ΣAE | 2025 direction | 2026 Jan–Jul ΣAE | 2026 direction |
|---|---:|---:|---:|---:|
| DE | 1115.9977 | 9/12 | 1665.7461 | 4/7 |
| GA | 989.9040 | 10/12 | 1560.4409 | 5/7 |
| PSO | 1031.3426 | 11/12 | 1475.5659 | 5/7 |

## Provenance and decisions

- DE: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_1_v1.py` / `de_phase`.
- GA: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_1_v1.py` / `ga_phase`.
- PSO: run 36256830372; commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; decision ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED. Source `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_1_v1.py` / `pso_phase`.

Job/artifact IDs are recorded in the main ledger batch entries and evidence provenance JSON.

Completed artifacts audited: 3/32. Scientific failures retained; no missing rows silently dropped.
Next: finish remaining Stage-1 batches; only then Stage-2 filtering/parent freeze.
