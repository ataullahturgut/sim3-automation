# GOLD SHORT-HORIZON GLOBAL XAU R2 — Stage 1 Classical / Boosting Screen Result

## Target decisions

| Horizon | Head | Status | Best feature | Best model | Primary | Baseline | Relative improvement |
|---|---|---|---|---|---:|---:|---:|
| H1 | direction | NO_PASS | CORE3_SAFE_EXTERNAL | LGBM_CLASS | 0.248734 | 0.249740 | 0.40% |
| H1 | return | NO_PASS | GOLD_ONLY | XGB_REG | 0.006591 | 0.006599 | 0.11% |
| H1 | quantile | NO_PASS | GOLD_ONLY | LGBM_QUANT | 0.002178 | 0.002182 | 0.15% |
| H3 | direction | PASS | CORE3 | LOGIT_L2 | 0.246637 | 0.249707 | 1.23% |
| H3 | return | NO_PASS | GOLD_ONLY | ELASTIC_NET | 0.011857 | 0.011841 | -0.13% |
| H3 | quantile | NO_PASS | CORE3 | LGBM_QUANT | 0.003787 | 0.003774 | -0.32% |
| H5 | direction | NO_PASS | CORE3 | LOGIT_L2 | 0.247894 | 0.249446 | 0.62% |
| H5 | return | NO_PASS | GOLD_ONLY | ELASTIC_NET | 0.015427 | 0.015419 | -0.05% |
| H5 | quantile | NO_PASS | CORE3 | LGBM_QUANT | 0.004951 | 0.004927 | -0.51% |

## Horizon summary

- H1: 0/3 heads PASS; mean relative improvement 0.22%.
- H3: 1/3 heads PASS; mean relative improvement 0.26%.
- H5: 0/3 heads PASS; mean relative improvement 0.02%.

## Binding interpretation
Stage 1 overall status: **PASS**.

At least one global-XAU horizon/head contains pre-2025 predictive signal. Freeze successful evidence before any robustness work or 2025 transport.