# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 4.2 METAHEURISTIC RESULT

Date: 2026-09-28
Status: **COMPLETE / BATCH 4.2 SCIENTIFIC GATE PASS**

Methods: ABC, SSA, GWO, WOA.

Frozen parent reference:
- EPSILON_RBF_DAILY12
- DEV SigmaAE **1449.187363**
- Direction **19/33**

## DEV ranking

| Rank | Method | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | ABC | **1563.258913** | **47.371482** | **62.367316** | **2.3251%** | **0.889226** | 16/33 | 2024-11 |
| 2 | GWO | 1590.104631 | 48.184989 | 63.997706 | 2.3805% | 0.904496 | 18/33 | 2024-11 |
| 3 | WOA | 1635.345256 | 49.555917 | 63.415749 | 2.4628% | 0.930231 | 17/33 | 2024-11 |
| 4 | SSA | 1659.670617 | 50.293049 | 67.134298 | 2.5014% | 0.944067 | **19/33** | 2024-11 |

## Comparison with frozen parent
None of the Batch 4.2 methods beats the frozen parent on DEV SigmaAE.

Best Batch 4.2 candidate:
- ABC = 1563.258913 / 16/33

Frozen parent:
- EPSILON_RBF_DAILY12 = 1449.187363 / 19/33

Delta ABC minus parent:
- **+114.071550 SigmaAE**

## Decision
- Batch 4.2 recorded only.
- No Stage-4 parent selected yet.
- Mandatory broad-screen progress: **8/32**.
- Remaining 24 methods must complete before Stage-4 filtering.
- Frozen Stage-2 parent remains the price reference.

## Reproducibility
- GitHub Actions run: 36398195330
- Job: 108849513102
- Artifact: 10959831017
- Scientific gate: SVR_DWT_STAGE42_GATE=PASS
- Workflow run conclusion is FAILURE only because the final report git push was rejected as non-fast-forward after another branch update; model execution, aggregate, scientific gate and artifact upload all passed.
- WOA payload SHA256: ef759053568fba184f3d15765941c18d8fcf790d4621cefd921125dc2417102d
- Full method JSON evidence is retained in workflow artifact 10959831017.

## Kontrol ve Uyum Özeti
- Common frozen bounds/budget: PASS.
- Prior-only chronology: PASS.
- Scientific gate: PASS.
- Model results valid despite final push conflict: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB mutation: NONE / READ_ONLY.
