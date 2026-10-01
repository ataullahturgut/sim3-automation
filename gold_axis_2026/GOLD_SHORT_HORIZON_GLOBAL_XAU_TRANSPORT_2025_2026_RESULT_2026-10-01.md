# GOLD SHORT-HORIZON GLOBAL XAU — Frozen 2025 / 2026 Transport Result

**Status:** COMPLETE

Binding model: **H3 / CORE3 / Logistic L2 / RAW probability**

Primary score mode: **STRICT_FROZEN_FIT** — one fit using only H3 labels mature by 2024-12-31; unchanged through 2025/2026.

## Primary transport metrics

| Year | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall | p>=0.55 N / UP rate | p<=0.45 N / UP rate |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2025 | 253 | 49.4% | 49.4% | 0.2509 | 0.6949 | 49.4% | 49.5% | 53 / 49.1% | 47 / 42.6% |
| 2026 | 142 | 42.3% | 45.2% | 0.2655 | 0.7261 | 75.0% | 15.4% | 71 / 47.9% | 14 / 71.4% |

## Secondary walk-forward diagnostic

| Year | N | Accuracy | Balanced acc | Brier | Log loss |
|---|---:|---:|---:|---:|---:|
| 2025 | 253 | 52.2% | 51.3% | 0.2499 | 0.6930 |
| 2026 | 142 | 42.3% | 45.3% | 0.2685 | 0.7323 |

No 2025/2026 result was used to retune the model, calibration, probability threshold or conviction bands.
