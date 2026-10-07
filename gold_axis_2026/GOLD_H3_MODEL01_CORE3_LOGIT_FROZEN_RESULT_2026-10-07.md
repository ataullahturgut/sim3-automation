# H3 MODEL 01 — CLASSICAL CORE3 LOGISTIC — CORRECT FROZEN CONTRACT

**Status:** COMPLETE / MODEL-01 AUTHORITY

**Target:** H3 direction = sign(log(P[t+3]/P[t]))

- t+3 = third retained Gold observation; not 3 calendar days.
- Features = Gold/Silver/Platinum CORE3.
- Model = StandardScaler + LogisticRegression(L2, C=1.0).
- DEV 2022-2024 = causal block-5 replay using only already-matured H3 outcomes.
- Frozen transport fit = 3784 rows; last train target end = 2024-12-31.
- 2025/2026 are scored with that unchanged pre-2025 fit.
- Clean chain includes the confirmed 2026-02-27 integrity correction.

| Period | N | Accuracy | BA | Brier | UP recall | DOWN recall |
|---|---:|---:|---:|---:|---:|---:|
| DEV_2022_2024 | 755 | 54.97% | 54.48% | 0.2466 | 65.06% | 43.89% |
| 2022 | 250 | 53.20% | 53.30% | 0.2457 | 66.13% | 40.48% |
| 2023 | 251 | 52.59% | 52.20% | 0.2494 | 63.08% | 41.32% |
| 2024 | 254 | 59.06% | 58.20% | 0.2447 | 65.96% | 50.44% |
| FROZEN_2025 | 253 | 50.20% | 50.06% | 0.2508 | 50.64% | 49.48% |
| FROZEN_2026 | 191 | 46.60% | 47.76% | 0.2573 | 72.53% | 23.00% |
| FROZEN_2025_2026 | 444 | 48.65% | 47.37% | 0.2536 | 58.70% | 36.04% |

The earlier 2026-10-07 Model-01 trial based on NOVA A0 expanding refits is superseded for the classical CORE3 frozen-transport question.
