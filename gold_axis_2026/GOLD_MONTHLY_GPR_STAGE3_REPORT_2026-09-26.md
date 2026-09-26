# GPR cumulative evidence — audited artifacts

Selection authority DEV only. External metrics reporting only, theta/kernel/scaler frozen at 2024-12.

| Model | DEV ΣAE | Direction | MAE | RMSE | 95% coverage | Max condition upper bound | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| ADAPTIVE_CROW | 1724.2888 | 19/33 | 52.2512 | 65.0567 | 0.9394 | 4.15e+06 | ELIGIBLE |
| ADAPTIVE_TLBO | 1740.8877 | 19/33 | 52.7542 | 63.8892 | 0.9091 | 3.571e+04 | ELIGIBLE |
| ADAPTIVE_PSO | 1794.2201 | 20/33 | 54.3703 | 68.0314 | 0.8485 | 4.64e+04 | ELIGIBLE |
| PSO_TLBO | 1815.3287 | 21/33 | 55.0100 | 65.6439 | 0.9394 | 1.747e+05 | ELIGIBLE |
| TLBO_TUNED_PSO | 1863.6677 | 19/33 | 56.4748 | 69.4799 | 0.8485 | 2.69e+04 | ELIGIBLE |
| DE_TUNED_PSO | 1939.8588 | 16/33 | 58.7836 | 69.7320 | 0.9394 | 3.691e+07 | ELIGIBLE |

## Reporting only

| Model | 2025 ΣAE / direction | 2026 ΣAE / direction |
|---|---|---|
| ADAPTIVE_CROW | 1223.9506 / 9/12 | 1613.7839 / 4/7 |
| ADAPTIVE_PSO | 1195.8734 / 9/12 | 1594.1298 / 5/7 |
| ADAPTIVE_TLBO | 1171.3549 / 8/12 | 1599.9542 / 4/7 |
| DE_TUNED_PSO | 1165.2957 / 9/12 | 1620.3487 / 4/7 |
| PSO_TLBO | 1240.6596 / 9/12 | 1564.8887 / 5/7 |
| TLBO_TUNED_PSO | 1400.8577 / 9/12 | 1894.1223 / 3/7 |

## Provenance and interpretation

- ADAPTIVE_CROW: run 36266015124, commit `47480bf7dc77d5e86437ace1f11bce7490baefe5`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- ADAPTIVE_PSO: run 36266015124, commit `47480bf7dc77d5e86437ace1f11bce7490baefe5`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- ADAPTIVE_TLBO: run 36266015124, commit `47480bf7dc77d5e86437ace1f11bce7490baefe5`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- DE_TUNED_PSO: run 36266015124, commit `47480bf7dc77d5e86437ace1f11bce7490baefe5`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- PSO_TLBO: run 36266015124, commit `47480bf7dc77d5e86437ace1f11bce7490baefe5`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- TLBO_TUNED_PSO: run 36266015124, commit `47480bf7dc77d5e86437ace1f11bce7490baefe5`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.

Intervals are uncalibrated predictive-observation intervals. Coverage/NLPD are diagnostics, not new acceptance authority. Finite budget-limited L-BFGS candidates are explicitly recorded and are not claims of converged/global optima.

## Kontrol ve Uyum Özeti

DEV-only PASS; 2025/2026 tuning/selection exclusion PASS; random split NONE; chronology and freeze hashes PASS; DB READ_ONLY/invariants equal; scientific failures retained without subset ranking; provenance recorded.
