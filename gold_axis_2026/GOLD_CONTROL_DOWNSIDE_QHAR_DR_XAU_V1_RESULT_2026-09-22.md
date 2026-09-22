# GOLD CONTROL — QLIKE-ESTIMATED HAR-DR V1 RESULT

**Identity:** `DOWNSIDE_QHAR_DR_XAU_V1_RESEARCH`  
**Manifest update:** deferred pending user review.  

## Main comparison

| Period | Model | QLIKE | MSE | OOS R2 | High-risk AUC | Precision | Recall | Calibration slope |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | QHAR_DR | 0.736137 | 1.11771e-08 | -14.0101 | 0.5398 | 0.1610 | 1.0000 | 0.1315 |
| 2024 | OLS_HAR_DR | 0.156463 | 6.03853e-10 | 0.1891 | 0.7283 | 0.5000 | 0.3030 | 0.8450 |
| 2025 | QHAR_DR | 0.807520 | 9.69996e-08 | -1.5991 | 0.8013 | 0.4008 | 1.0000 | 0.1332 |
| 2025 | OLS_HAR_DR | 0.309654 | 3.76716e-08 | -0.0094 | 0.8444 | 0.7065 | 0.6842 | 0.3858 |

## Frozen decisions

- 2024 QLIKE-estimation gate: **FAIL**.
- 2025 transport gate: **FAIL**.
- No adaptive calibration state or post-2025 rescue was used.
- No manifest change was made by this workflow.
