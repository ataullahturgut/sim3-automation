# HAG-D1 V1 — Horizon Alignment Gate

**Status:** RETROSPECTIVE CHALLENGER — NOT PROMOTED

Goal: learn timing from all OPAL override events; when an OPAL reversal survives into a final V5-vs-AURORA flip, estimate whether that reversal is already aligned with the next-day D1 move or is delayed/not immediate.

## Design

- Development: through 2023.
- Family confirmation/selection: 2024 only.
- Refit selected family on all <=2024 flip cases.
- 2025 and 2026 are untouched by feature-family selection and coefficient fitting.
- Fixed primary action band: p(immediate) >= 0.60 => use V5/OPAL flip; <= 0.40 => use AURORA/base direction; otherwise ABSTAIN.

Selected family: **CORE**

## 2024 family confirmation

| Family | Train N | Confirm N | Accuracy | BA | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|
| CORE | 35 | 20 | 60.00% | 69.23% | 0.2897 | 0.8157 |
| FUSED | 35 | 20 | 55.00% | 62.09% | 0.2991 | 0.8665 |
| MACRO | 35 | 20 | 50.00% | 58.24% | 0.2990 | 0.8241 |

## Flip-case evaluation

| Period | Flip cases | Always V5 | Always AURORA | HAG actions | HAG coverage | HAG accuracy |
|---|---:|---:|---:|---:|---:|---:|
| 2025 | 7 | 4/7 (57.14%) | 3/7 (42.86%) | 7 | 100.00% | 5/7 (71.43%) |
| 2026 | 19 | 11/19 (57.89%) | 8/19 (42.11%) | 17 | 89.47% | 8/17 (47.06%) |
| 2025-2026 | 26 | 15/26 (57.69%) | 11/26 (42.31%) | 24 | 92.31% | 13/24 (54.17%) |

## CIG integration

| Period | Original actions | Original acc | HAG actions | HAG acc | Original coverage | HAG coverage |
|---|---:|---:|---:|---:|---:|---:|
| 2026 | 157 | 71.34% | 174 | 68.97% | 82.20% | 91.10% |
| 2026-08 | 10 | 80.00% | 20 | 55.00% | 47.62% | 95.24% |

## August 2026 — original UNCERTAIN days

| Issue | Actual | p(immediate) | HAG result | Correct |
|---|---|---:|---|---:|
| 2026-08-03 | DOWN | 0.691 | UP (HAG_RESOLVED_V5) | 0 |
| 2026-08-04 | UP | 0.175 | DOWN (HAG_RESOLVED_AURORA) | 0 |
| 2026-08-07 | UP | 0.396 | DOWN (HAG_RESOLVED_AURORA) | 0 |
| 2026-08-12 | UP | 0.878 | UP (HAG_RESOLVED_V5) | 1 |
| 2026-08-13 | DOWN | 0.630 | DOWN (HAG_RESOLVED_V5) | 1 |
| 2026-08-14 | DOWN | 0.572 | UNCERTAIN (HAG_ABSTAIN) |  |
| 2026-08-21 | UP | 0.309 | UP (HAG_RESOLVED_AURORA) | 1 |
| 2026-08-24 | UP | 0.634 | DOWN (HAG_RESOLVED_V5) | 0 |
| 2026-08-25 | DOWN | 0.297 | UP (HAG_RESOLVED_AURORA) | 0 |
| 2026-08-26 | DOWN | 0.113 | UP (HAG_RESOLVED_AURORA) | 0 |
| 2026-08-28 | DOWN | 0.755 | UP (HAG_RESOLVED_V5) | 0 |

## Governance

HAG-D1 V1 is a timing/horizon challenger, not a replacement for OPAL H3. No 2025/2026 outcome is used in feature-family selection or coefficient fitting. The 0.40/0.60 action band is fixed before test scoring. Sensitivity bands are reported but not used to choose the result.
