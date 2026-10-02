# SAGE-H3 V1 — SESSION-AWARE GOLD ENGINE RESULT

**Status:** **FAIL_CLOSED_NO_ELIGIBLE_2022H2_SESSION_MODEL**  
**Selected 2022-H2 representation:** **NONE**  
**2023 + 2024 frozen confirmation:** **False**

## Selection grid — 2022 H2

| Candidate | Eligible | Δ accuracy | Δ balanced | Δ Brier |
|---|---|---:|---:|---:|
| A1_SESSION | False | -2.70 pp | -2.66 pp | +0.0180 |
| SESSION_ONLY | False | -5.41 pp | -5.54 pp | +0.0164 |
| PATH_SESSION | False | -4.50 pp | -4.47 pp | +0.0171 |
| A1_PATH_SESSION | False | +0.90 pp | +0.96 pp | +0.0176 |

## Period metrics

| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|---:|
| BASE_IRIS | SELECT_2022_H2 | 111 | 62.16% | 61.78% | 0.2331 | 55.77% | 67.80% |
| BASE_IRIS | 2023 | 217 | 70.97% | 71.61% | 0.2116 | 60.87% | 82.35% |
| BASE_IRIS | 2024 | 229 | 70.74% | 70.02% | 0.2007 | 75.38% | 64.65% |
| BASE_IRIS | 2025 | 247 | 63.16% | 61.65% | 0.2293 | 68.67% | 54.64% |
| BASE_IRIS | 2026 | 191 | 58.12% | 58.66% | 0.2558 | 70.33% | 47.00% |
| BASE_IRIS | 2025-2026 | 438 | 60.96% | 60.03% | 0.2408 | 69.29% | 50.76% |

## Governance

SAGE representation selection used only Jul-Dec 2022. 2023 and 2024 were frozen confirmation periods; 2025/2026 were transport/stress. The 2026 rescue diagnostics did not alter V1.
