# GLOBAL XAU DAILY H3 — ANFIS 2025/2026 Frozen Transport

Training rows: **3784**; last pre-2025 target maturity: **2024-12-31**.
Opened scoring through issue **2026-09-25**, target end **2026-09-29**.

| Model | Period | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| CHHHO_ANFIS | 2025 | 253 | 53.8% | 53.5% | 0.2497 | 0.6944 | 54.5% | 52.6% |
| CHHHO_ANFIS | 2026 | 191 | 50.3% | 51.2% | 0.3040 | 1.2354 | 71.4% | 31.0% |
| CHHHO_ANFIS | 2026-08 | 21 | 38.1% | 42.9% | 0.2740 | 0.7424 | 28.6% | 57.1% |
| CHHHO_ANFIS | 2026-09 | 19 | 52.6% | 56.5% | 0.2571 | 0.7076 | 71.4% | 41.7% |
| LOGIT_L2 | 2025 | 253 | 50.2% | 50.1% | 0.2508 | 0.6946 | 50.6% | 49.5% |
| LOGIT_L2 | 2026 | 191 | 44.0% | 45.2% | 0.2727 | 0.7420 | 71.4% | 19.0% |
| LOGIT_L2 | 2026-08 | 21 | 47.6% | 53.6% | 0.2488 | 0.6906 | 35.7% | 71.4% |
| LOGIT_L2 | 2026-09 | 19 | 47.4% | 58.3% | 0.2602 | 0.7137 | 100.0% | 16.7% |
| VANILLA_ANFIS | 2025 | 253 | 51.4% | 50.8% | 0.2578 | 0.7104 | 53.2% | 48.5% |
| VANILLA_ANFIS | 2026 | 191 | 45.0% | 45.9% | 0.3047 | 1.2489 | 63.7% | 28.0% |
| VANILLA_ANFIS | 2026-08 | 21 | 57.1% | 67.9% | 0.2599 | 0.7132 | 35.7% | 100.0% |
| VANILLA_ANFIS | 2026-09 | 19 | 47.4% | 55.4% | 0.2764 | 0.7482 | 85.7% | 25.0% |

All three rows use one pre-2025 frozen fit. No 2025/2026 label updates the models.
