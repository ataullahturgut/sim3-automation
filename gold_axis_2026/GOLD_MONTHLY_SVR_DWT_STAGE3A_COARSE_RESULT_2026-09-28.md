# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 3A COARSE NESTED GRID RESULT

Date: 2026-09-28
Status: **COMPLETE / SCIENTIFIC GATE PASS**

## Frozen search
- Parent: epsilon-SVR / RBF / DAILY_SUMMARY12.
- Grid: 150 combinations.
- log2(C): -8,-4,0,4,8,12.
- log2(gamma): -12,-8,-4,0,4.
- epsilon: 0.01,0.05,0.10,0.20,0.50.
- Inner validation: final 20% chronological pre-target tail, minimum 12 rows.
- Inner scalers fit only on inner train.
- Outer refit uses all pre-target rows only.
- 2025 opened: NO. 2026 used: NO.

## DEV result

| Candidate | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |
|---|---:|---:|---:|---:|---:|---:|---|
| Frozen Stage-2 parent | 1449.187363 | 43.914769 | 59.388776 | 2.1700% | 0.824339 | 19/33 | 2024-11 |
| Stage-3A coarse tuned | 1580.901050 | 47.906092 | 62.418145 | 2.3547% | 0.899261 | 20/33 | 2024-11 |

Delta tuned minus parent SigmaAE: **+131.713687**.

## Most frequent selected coarse points

| log2(C) | log2(gamma) | epsilon | Outer origins |
|---:|---:|---:|---:|
| 0 | -4 | 0.05 | 5 |
| 4 | -12 | 0.10 | 5 |
| 4 | -12 | 0.01 | 4 |
| 0 | -8 | 0.10 | 3 |
| 0 | -4 | 0.01 | 3 |
| 4 | -12 | 0.20 | 3 |
| 0 | -8 | 0.01 | 2 |
| 0 | -4 | 0.10 | 2 |
| 8 | -8 | 0.05 | 2 |
| 8 | -8 | 0.10 | 2 |
| 0 | -8 | 0.05 | 1 |
| 4 | -12 | 0.05 | 1 |

## Decision
- Stage 3A is a coarse nested benchmark, not the final tuned freeze.
- Stage 3B local refinement must be frozen separately before execution.
- No Stage-4 metaheuristic execution is authorized yet.

## Kontrol ve Uyum Özeti
- Pre-outcome Stage-3A freeze respected: PASS.
- Grid size exactly 150: PASS.
- Inner chronology: PASS.
- Inner scaling train-only: PASS.
- Outer refit pre-target only: PASS.
- Parent reconciliation: PASS.
- Deterministic replay: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB mutation: NONE / READ_ONLY.
- Payload SHA256: 289535fc26a3e12f8b2a2e4da8c86c0dd4c1a565aee30965239432bd6010bfc2
