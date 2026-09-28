# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 3B LOCAL REFINEMENT RESULT

Date: 2026-09-28
Status: **COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED**

## DEV comparison

| Candidate | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction |
|---|---:|---:|---:|---:|---:|---:|
| Frozen Stage-2 parent | 1449.187363 | 43.914769 | 59.388776 | 2.1700% | 0.824339 | 19/33 |
| Stage-3A coarse | 1580.901050 | 47.906092 | 62.418145 | 2.3547% | 0.899261 | 20/33 |
| Stage-3B local | 1615.913256 | 48.967068 | 63.002143 | 2.4023% | 0.919177 | 22/33 |

Promotion rule: Stage-3B SigmaAE < 1449.187363.
Decision: **NOT PROMOTED**.

## Frequent Stage-3B selections

| log2(C) | log2(gamma) | epsilon | Origins |
|---:|---:|---:|---:|
| -2 | -4 | 0.025 | 5 |
| 4 | -12 | 0.010 | 4 |
| 4 | -12 | 0.100 | 4 |
| -2 | -6 | 0.075 | 3 |
| -2 | -6 | 0.010 | 2 |
| 0 | -4 | 0.025 | 2 |
| 4 | -12 | 0.200 | 2 |
| 8 | -8 | 0.100 | 2 |
| -2 | -6 | 0.100 | 1 |
| 0 | -4 | 0.010 | 1 |
| 0 | -4 | 0.100 | 1 |
| 2 | -10 | 0.025 | 1 |

## Stage-3 closure
- Final deterministic SVR reference: **EPSILON_RBF_DAILY12_STAGE2_PARENT**.
- Continuous Stage-4 metaheuristic bounds must be frozen next.
- 32/32 Stage-4 screen remains mandatory.

## Kontrol ve Uyum Özeti
- Stage-3B freeze respected: PASS.
- Local neighborhoods derived only from Stage-3A coarse centers: PASS.
- Inner chronology/scaling unchanged: PASS.
- Parent and Stage-3A reconciliation: PASS.
- Determinism: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB mutation: NONE / READ_ONLY.
- Payload SHA256: 8ae88568da68a451d667ef53110888cd0ffe76bbf029003b71cfe37c9e938c9e
