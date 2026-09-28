# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 3B LOCAL REFINEMENT RESULT

Date: 2026-09-28
Status: **COMPLETE / SCIENTIFIC GATE PASS**

## Frozen local search
- Frozen parent: epsilon-SVR / RBF / DAILY_SUMMARY12.
- Frozen local union: 136 unique candidates.
- Same nested chronological protocol as Stage 3A.
- Inner validation final 20% pre-target tail, minimum 12 rows.
- Inner scalers fit only on inner train.
- Outer refit uses all pre-target rows only.
- 2025 opened: NO. 2026 used: NO.

## DEV comparison

| Candidate | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |
|---|---:|---:|---:|---:|---:|---:|---|
| Frozen Stage-2 parent | 1449.187363 | 43.914769 | 59.388776 | 2.1700% | 0.824339 | 19/33 | 2024-11 |
| Stage-3A coarse tuned | 1580.901050 | 47.906092 | 62.418145 | 2.3547% | 0.899261 | 20/33 | 2024-11 |
| Stage-3B local tuned | 1592.590456 | 48.260317 | 62.575787 | 2.3658% | 0.905910 | 22/33 | 2024-11 |

Stage-3B delta vs parent SigmaAE: **+143.403093**.
Stage-3B delta vs Stage-3A SigmaAE: **+11.689406**.

## Most frequent local selections

| log2(C) | log2(gamma) | epsilon | Outer origins |
|---:|---:|---:|---:|
| -2 | -6 | 0.030 | 5 |
| -2 | -4 | 0.030 | 4 |
| 0 | -4 | 0.010 | 3 |
| 4 | -12 | 0.100 | 3 |
| -2 | -6 | 0.010 | 2 |
| 2 | -10 | 0.030 | 2 |
| 4 | -12 | 0.010 | 2 |
| 4 | -12 | 0.150 | 2 |
| 4 | -12 | 0.200 | 2 |
| 8 | -8 | 0.100 | 2 |
| -2 | -4 | 0.010 | 1 |
| 0 | -4 | 0.030 | 1 |

## Decision
- Deterministic tuning promoted: **NO**.
- Deterministic benchmark carried forward: **STAGE2_PARENT**.
- No additional deterministic rescue tuning is authorized.
- Next step is a separate pre-outcome Stage-4 bounds freeze for the mandatory 32/32 metaheuristic screen.

## Kontrol ve Uyum Özeti
- Stage-3B pre-outcome freeze respected: PASS.
- Frozen local union size 136: PASS.
- Inner chronology: PASS.
- Inner scaling train-only: PASS.
- Outer refit pre-target only: PASS.
- Parent and Stage-3A reconciliation: PASS.
- Deterministic replay: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB mutation: NONE / READ_ONLY.
- Payload SHA256: 798f16bf175d010007529ffa0b1c47000fe9e36c66a7739ef33debc93fc3c4ab
