# ADAH-D1 V1 — Adaptive Direction-Age Hazard Result

**Selected 2024 candidate:** **ANALOG9**  
**2025 confirmation:** **FAIL**  
**Promotion:** **FAIL**

## 2024 candidate selection

| Candidate | N | Brier | Log loss | Directional acc |
|---|---:|---:|---:|---:|
| DBH93 | 20 | 0.2398 | 0.6724 | 50.00% |
| DBH97 | 20 | 0.2449 | 0.6831 | 60.00% |
| ANALOG9 | 20 | 0.2053 | 0.6002 | 70.00% |
| ENSEMBLE | 20 | 0.2218 | 0.6358 | 70.00% |

## 2025 confirmation

- selected Brier: **0.2446** vs static **0.2432**
- final V5 flip selective actions: **1/7**
- selective accuracy: **0.00%**
- confirmation: **FAIL**

## 2026 frozen test

- all OPAL overrides Brier: **0.2686**
- final V5 flip actions: **2/19**
- final V5 flip selective accuracy: **50.00%**

## CIG integration

| Period | Original actions | Original acc | ADAH actions | ADAH acc | Original coverage | ADAH coverage |
|---|---:|---:|---:|---:|---:|---:|
| 2026 | 157 | 71.34% | 159 | 71.07% | 82.20% | 83.25% |
| 2026-08 | 10 | 80.00% | 11 | 72.73% | 47.62% | 52.38% |

## August original UNCERTAIN dates

| Issue | Actual | p(immediate) | ADAH |
|---|---|---:|---|
| 2026-08-03 | DOWN | 0.419 | UNCERTAIN / ADAH_ABSTAIN |
| 2026-08-04 | UP | 0.380 | UNCERTAIN / ADAH_ABSTAIN |
| 2026-08-07 | UP | 0.351 | UNCERTAIN / ADAH_ABSTAIN |
| 2026-08-12 | UP | 0.554 | UNCERTAIN / ADAH_ABSTAIN |
| 2026-08-13 | DOWN | 0.553 | UNCERTAIN / ADAH_ABSTAIN |
| 2026-08-14 | DOWN | 0.496 | UNCERTAIN / ADAH_ABSTAIN |
| 2026-08-21 | UP | 0.534 | UNCERTAIN / ADAH_ABSTAIN |
| 2026-08-24 | UP | 0.384 | UNCERTAIN / ADAH_ABSTAIN |
| 2026-08-25 | DOWN | 0.381 | UNCERTAIN / ADAH_ABSTAIN |
| 2026-08-26 | DOWN | 0.345 | UP / ADAH_AURORA |
| 2026-08-28 | DOWN | 0.535 | UNCERTAIN / ADAH_ABSTAIN |

## Decision

ADAH is promoted only if the preregistered 2025 confirmation gate passes and the 2026/August promotion constraints pass. No 2026 result is used to alter the candidate, state definition, forgetting rate, analog k, or action thresholds.
