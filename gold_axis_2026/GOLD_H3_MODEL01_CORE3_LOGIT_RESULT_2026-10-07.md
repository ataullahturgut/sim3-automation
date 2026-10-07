# H3 MODEL 01 — CORE3 LOGISTIC

**Status:** COMPLETE

**Target:** H3 direction = sign(log(P[t+3]/P[t]))

- t+3 = third retained Gold observation; not three calendar days.
- Features = Gold/Silver/Platinum CORE3 only.
- Model = StandardScaler + LogisticRegression(L2, C=1.0).
- Causal training: only already-matured H3 outcomes.
- Data = clean H3 chain with confirmed 2026-02-27 integrity correction.

| Period | N | Accuracy | BA | Brier | UP recall | DOWN recall |
|---|---:|---:|---:|---:|---:|---:|
| DEV_2022_2024 | 755 | 54.97% | 54.49% | 0.2466 | 64.81% | 44.17% |
| 2022 | 250 | 53.60% | 53.70% | 0.2458 | 66.13% | 41.27% |
| 2023 | 251 | 52.59% | 52.20% | 0.2494 | 63.08% | 41.32% |
| 2024 | 254 | 58.66% | 57.85% | 0.2447 | 65.25% | 50.44% |
| FROZEN_2025 | 253 | 51.78% | 50.95% | 0.2499 | 54.49% | 47.42% |
| 2026 | 191 | 44.50% | 45.76% | 0.2605 | 72.53% | 19.00% |
| 2025_2026 | 444 | 48.65% | 47.06% | 0.2544 | 61.13% | 32.99% |
