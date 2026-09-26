# GPR cumulative evidence — audited artifacts

Selection authority DEV only. External metrics reporting only, theta/kernel/scaler frozen at 2024-12.

| Model | DEV ΣAE | Direction | MAE | RMSE | 95% coverage | Max condition upper bound | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| SO_RBF | 1519.4443 | 19/33 | 46.0438 | 59.4798 | 0.9091 | 173.2 | BENCHMARK_ONLY |
| ICM_M32 | 1640.0091 | 17/33 | 49.6972 | 59.6653 | 0.9697 | 4.899e+08 | ELIGIBLE |
| VANILLA_ICM_RBF | 1726.6205 | 15/33 | 52.3218 | 60.8932 | 0.9394 | 1.107e+08 | ELIGIBLE |
| REGULARIZED_ICM_RBF | 1842.2361 | 16/33 | 55.8253 | 64.7459 | 0.9394 | 6538 | ELIGIBLE |

## Reporting only

| Model | 2025 ΣAE / direction | 2026 ΣAE / direction |
|---|---|---|
| ICM_M32 | 966.7238 / 9/12 | 1566.2865 / 5/7 |
| REGULARIZED_ICM_RBF | 1086.4234 / 9/12 | 1548.0149 / 4/7 |
| SO_RBF | 1064.1439 / 10/12 | 1608.0868 / 4/7 |
| VANILLA_ICM_RBF | 1175.6207 / 9/12 | 1561.4442 / 3/7 |

## Provenance and interpretation

- ICM_M32: run 36263297105, commit `b28d63cb5dbf5d0f8290b20dfe8152b40a54623d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- REGULARIZED_ICM_RBF: run 36263297105, commit `b28d63cb5dbf5d0f8290b20dfe8152b40a54623d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- SO_RBF: run 36263297105, commit `b28d63cb5dbf5d0f8290b20dfe8152b40a54623d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- VANILLA_ICM_RBF: run 36263297105, commit `b28d63cb5dbf5d0f8290b20dfe8152b40a54623d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.

Intervals are uncalibrated predictive-observation intervals. Coverage/NLPD are diagnostics, not new acceptance authority. Finite budget-limited L-BFGS candidates are explicitly recorded and are not claims of converged/global optima.

## Kontrol ve Uyum Özeti

DEV-only PASS; 2025/2026 tuning/selection exclusion PASS; random split NONE; chronology and freeze hashes PASS; DB READ_ONLY/invariants equal; scientific failures retained without subset ranking; provenance recorded.
