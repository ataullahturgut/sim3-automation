# GOLD SHORT-HORIZON — TARGET RESEARCH V1

Same CORE3 features and same fixed Logistic model for every target. DEV only: 2022-2024.

## Ordinary direction targets

| Target | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall | Majority acc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DIR_H1 | 755 | 50.73% | 50.45% | 0.2499 | 0.6930 | 56.46% | 44.44% | 52.32% |
| DIR_H3 | 755 | 54.17% | 53.67% | 0.2469 | 0.6869 | 64.56% | 42.78% | 52.32% |
| DIR_H5 | 755 | 54.97% | 53.43% | 0.2478 | 0.6888 | 79.25% | 27.61% | 52.98% |

## Volatility-normalized first-close-hit targets

| Target | N | Accuracy | Balanced acc | Macro F1 | Brier | Log loss | NO_MOVE share | Pred directional coverage | Selective dir acc | Majority acc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BARRIER_H3_K050 | 755 | 49.54% | 34.78% | 0.3359 | 0.5528 | 0.8750 | 6.23% | 100.00% | 49.54% | 50.33% |
| BARRIER_H3_K075 | 755 | 45.43% | 36.09% | 0.3254 | 0.6216 | 1.0229 | 17.48% | 100.00% | 45.43% | 44.90% |
| BARRIER_H3_K100 | 755 | 37.48% | 34.72% | 0.3267 | 0.6503 | 1.0720 | 27.42% | 91.79% | 37.95% | 39.07% |
| BARRIER_H5_K075 | 755 | 52.19% | 36.23% | 0.3505 | 0.5447 | 0.8621 | 5.83% | 100.00% | 52.19% | 51.66% |

Annual metrics and full prediction ledger are saved separately.
