# DART-H3 V1 — DISAGREEMENT-AWARE REGIME TRANSFER RESULT

**Status:** **MECHANISM_PASS**  
**BOCPD hazard:** **1/20 disagreement events**  
**Enter PATH:** Pr(theta>0.5)>=0.90 and q_path>=0.60  
**Exit PATH:** Pr(theta>0.5)<=0.10 and q_path<=0.40  
**2023 + 2024 confirmation:** **True**

## Period metrics

| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|---:|
| STRUCTURAL_IRIS | 2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| PATH_GLOBAL | 2022_H2 | 112 | 60.71% | 60.26% | 0.2323 | 53.85% | 66.67% |
| DART | 2022_H2 | 112 | 62.50% | 62.05% | 0.2317 | 55.77% | 68.33% |
| STRUCTURAL_IRIS | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| PATH_GLOBAL | 2023 | 219 | 67.58% | 67.89% | 0.2145 | 61.74% | 74.04% |
| DART | 2023 | 219 | 71.23% | 71.83% | 0.2118 | 60.00% | 83.65% |
| STRUCTURAL_IRIS | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| PATH_GLOBAL | 2024 | 240 | 65.00% | 64.25% | 0.2073 | 69.85% | 58.65% |
| DART | 2024 | 240 | 70.83% | 69.97% | 0.2006 | 76.47% | 63.46% |
| STRUCTURAL_IRIS | 2025 | 248 | 63.71% | 62.27% | 0.2294 | 68.87% | 55.67% |
| PATH_GLOBAL | 2025 | 248 | 64.92% | 62.53% | 0.2269 | 73.51% | 51.55% |
| DART | 2025 | 248 | 64.11% | 62.60% | 0.2303 | 69.54% | 55.67% |
| STRUCTURAL_IRIS | 2026 | 191 | 58.64% | 59.12% | 0.2556 | 69.23% | 49.00% |
| PATH_GLOBAL | 2026 | 191 | 60.73% | 61.12% | 0.2477 | 69.23% | 53.00% |
| DART | 2026 | 191 | 60.73% | 61.12% | 0.2477 | 69.23% | 53.00% |
| STRUCTURAL_IRIS | 2025-2026 | 439 | 61.50% | 60.65% | 0.2408 | 69.01% | 52.28% |
| PATH_GLOBAL | 2025-2026 | 439 | 63.10% | 62.09% | 0.2360 | 71.90% | 52.28% |
| DART | 2025-2026 | 439 | 62.64% | 61.87% | 0.2378 | 69.42% | 54.31% |

## Annual DART state

| Year | PATH share | Mean q_path | Mean Pr(PATH superior) | Matured disagreements by year-end |
|---:|---:|---:|---:|---:|
| 2022 | 0.0% | 0.540 | 0.568 | 12 |
| 2023 | 0.0% | 0.390 | 0.213 | 35 |
| 2024 | 0.0% | 0.361 | 0.182 | 68 |
| 2025 | 22.2% | 0.436 | 0.319 | 98 |
| 2026 | 100.0% | 0.681 | 0.856 | 108 |

## State switches

- 2025-10-14: STRUCTURAL_IRIS -> PATH_GLOBAL; q_path=0.831; Pr(PATH superior)=0.944; matured disagreements=91

## 2026 rescue

- Structural accuracy: **58.64%**
- DART accuracy: **60.73%**
- rescued calls: **7**
- broken calls: **3**
- net rescue: **+4**
- PATH-active origins: **191 / 191**

## Governance

DART thresholds and hazard were fixed before this run. BOCPD updates used only expert-disagreement outcomes whose H3 target had already matured by the current feature cutoff. 2025/2026 were not used to tune V1.
