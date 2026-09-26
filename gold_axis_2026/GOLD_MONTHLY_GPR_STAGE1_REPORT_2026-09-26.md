# GPR cumulative evidence — audited artifacts

Selection authority DEV only. External metrics reporting only, theta/kernel/scaler frozen at 2024-12.

| Model | DEV ΣAE | Direction | MAE | RMSE | 95% coverage | Max condition upper bound | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| GWO | 1650.2596 | 21/33 | 50.0079 | 61.4907 | 0.9394 | 1.913e+08 | ELIGIBLE |
| ABC | 1672.2945 | 22/33 | 50.6756 | 63.5447 | 0.9697 | 1.136e+05 | ELIGIBLE |
| MPA | 1701.5802 | 23/33 | 51.5630 | 64.8893 | 0.9091 | 1.408e+07 | ELIGIBLE |
| GA | 1723.5877 | 21/33 | 52.2299 | 63.4427 | 0.8788 | 9.282e+04 | ELIGIBLE |
| BAT | 1746.6720 | 21/33 | 52.9295 | 67.6103 | 0.9091 | 1.571e+06 | ELIGIBLE |
| PSO | 1780.2169 | 19/33 | 53.9460 | 65.0889 | 0.8485 | 1.682e+06 | ELIGIBLE |
| SSA | 1798.1173 | 21/33 | 54.4884 | 68.4977 | 0.8788 | 1.816e+05 | ELIGIBLE |
| ACO | 1815.8271 | 19/33 | 55.0251 | 69.5269 | 0.8788 | 3.268e+05 | ELIGIBLE |
| HHO | 1823.3648 | 21/33 | 55.2535 | 66.6063 | 0.9091 | 1.353e+06 | ELIGIBLE |
| WOA | 1836.8353 | 21/33 | 55.6617 | 69.7336 | 0.8182 | 1.589e+05 | ELIGIBLE |
| DE | 1924.6270 | 21/33 | 58.3220 | 71.5043 | 0.9091 | 6.502e+07 | ELIGIBLE |

## Reporting only

| Model | 2025 ΣAE / direction | 2026 ΣAE / direction |
|---|---|---|
| ABC | 1270.7420 / 9/12 | 1733.8828 / 3/7 |
| ACO | 1240.0333 / 8/12 | 1785.4657 / 4/7 |
| BAT | 1144.6360 / 10/12 | 1797.0547 / 4/7 |
| DE | 1193.9617 / 9/12 | 1500.4802 / 5/7 |
| GA | 1232.3520 / 9/12 | 1675.1882 / 4/7 |
| GWO | 1309.3998 / 7/12 | 1714.9181 / 3/7 |
| HHO | 1058.8792 / 10/12 | 1571.7864 / 5/7 |
| MPA | 1310.8517 / 10/12 | 1627.5845 / 4/7 |
| PSO | 1377.4255 / 8/12 | 1448.8102 / 4/7 |
| SSA | 1073.4934 / 9/12 | 1822.8569 / 4/7 |
| WOA | 1074.8662 / 9/12 | 1598.3084 / 5/7 |

## Provenance and interpretation

- ABC: run 36263592441, commit `b5885a50dfbc17474b8f22ac2e8b61f43b7b748d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- ACO: run 36263592441, commit `b5885a50dfbc17474b8f22ac2e8b61f43b7b748d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- BAT: run 36263592441, commit `b5885a50dfbc17474b8f22ac2e8b61f43b7b748d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- DE: run 36263592441, commit `b5885a50dfbc17474b8f22ac2e8b61f43b7b748d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- GA: run 36263592441, commit `b5885a50dfbc17474b8f22ac2e8b61f43b7b748d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- GWO: run 36263592441, commit `b5885a50dfbc17474b8f22ac2e8b61f43b7b748d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- HHO: run 36263592441, commit `b5885a50dfbc17474b8f22ac2e8b61f43b7b748d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- MPA: run 36263592441, commit `b5885a50dfbc17474b8f22ac2e8b61f43b7b748d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- PSO: run 36263592441, commit `b5885a50dfbc17474b8f22ac2e8b61f43b7b748d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- SSA: run 36263592441, commit `b5885a50dfbc17474b8f22ac2e8b61f43b7b748d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.
- WOA: run 36263592441, commit `b5885a50dfbc17474b8f22ac2e8b61f43b7b748d`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.

Intervals are uncalibrated predictive-observation intervals. Coverage/NLPD are diagnostics, not new acceptance authority. Finite budget-limited L-BFGS candidates are explicitly recorded and are not claims of converged/global optima.

## Kontrol ve Uyum Özeti

DEV-only PASS; 2025/2026 tuning/selection exclusion PASS; random split NONE; chronology and freeze hashes PASS; DB READ_ONLY/invariants equal; scientific failures retained without subset ranking; provenance recorded.
