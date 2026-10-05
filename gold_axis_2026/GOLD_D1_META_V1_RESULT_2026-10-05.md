# D1-META V1 — DIRECT NEXT-DAY SELECTIVE STACK RESULT

**Selected:** F2_EXPERT_PATH / HGB_SMALL  
**Frozen threshold:** 0.65  
**2025 confirmation:** PASS

## 2024-H1 model selection

| Family | Model | N | Acc | BA | Brier | Log loss |
|---|---|---:|---:|---:|---:|---:|
| F2_EXPERT_PATH | HGB_SMALL | 116 | 84.48% | 81.53% | 0.1208 | 0.4035 |
| F3_EXPERT_PATH_MACRO | HGB_SMALL | 116 | 82.76% | 80.08% | 0.1226 | 0.4020 |
| F3_EXPERT_PATH_MACRO | LOGIT_L2 | 116 | 83.62% | 81.14% | 0.1290 | 0.4195 |
| F2_EXPERT_PATH | LOGIT_L2 | 116 | 84.48% | 82.21% | 0.1301 | 0.4206 |
| F1_EXPERT | LOGIT_L2 | 116 | 77.59% | 75.39% | 0.1523 | 0.4795 |
| F1_EXPERT | HGB_SMALL | 116 | 80.17% | 78.58% | 0.1541 | 0.5156 |

## 2024-H2 threshold selection

| t | Actions | Coverage | Correct | Accuracy |
|---:|---:|---:|---:|---:|
| 0.55 | 118 | 95.16% | 98 | 83.05% |
| 0.60 | 113 | 91.13% | 95 | 84.07% |
| 0.65 | 109 | 87.90% | 92 | 84.40% |
| 0.70 | 108 | 87.10% | 91 | 84.26% |

## 2025 frozen confirmation

- full accuracy: **78.63%**
- full balanced accuracy: **77.03%**
- selective: **167/198 = 84.34%**, coverage **79.84%**
- confirmation: **PASS**

## 2026 frozen test

- full accuracy: **67.02%**
- full balanced accuracy: **67.36%**
- standalone selective: **117/167 = 70.06%**, coverage **87.43%**

## CIG integration

| Policy | 2026 actions | 2026 accuracy | Coverage | Aug actions | Aug accuracy | Aug coverage |
|---|---:|---:|---:|---:|---:|---:|
| original | 157 | 71.34% | 82.20% | 10 | 80.00% | 47.62% |
| resolve_only | 182 | 67.58% | 95.29% | 17 | 70.59% | 80.95% |
| veto_resolve | 181 | 67.96% | 94.76% | 17 | 70.59% | 80.95% |

## Promotion

- RESOLVE_ONLY: **FAIL**
- VETO_RESOLVE: **FAIL**

No 2025/2026 outcome altered model family, feature family, hyperparameters, or the selective threshold.
