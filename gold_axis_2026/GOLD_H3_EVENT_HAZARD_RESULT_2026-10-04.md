# GOLD H3 — MACRO EVENT HAZARD / CATALYST DIAGNOSTIC

**Status:** retrospective mechanism diagnostic; not a new clean holdout.

Academic mechanism: gold futures react materially and asymmetrically to macroeconomic surprises, especially employment/inflation and FOMC-related shocks. This experiment tests whether the H3 reversal error is concentrated around such events.

## V5 error-rate anatomy

| Group | n | Missed reversals | Error rate |
|---|---:|---:|---:|
| future_any_major_event=1 | 248 | 84 | 33.87% |
| future_any_major_event=0 | 530 | 164 | 30.94% |
| future_emp_event=1 | 107 | 34 | 31.78% |
| future_emp_event=0 | 671 | 214 | 31.89% |
| future_inflation_event=1 | 113 | 37 | 32.74% |
| future_inflation_event=0 | 665 | 211 | 31.73% |
| future_fomc_event=1 | 51 | 17 | 33.33% |
| future_fomc_event=0 | 727 | 231 | 31.77% |
| recent_emp_1d=1 | 36 | 6 | 16.67% |
| recent_emp_1d=0 | 742 | 242 | 32.61% |
| recent_emp_3d=1 | 68 | 18 | 26.47% |
| recent_emp_3d=0 | 710 | 230 | 32.39% |

## Simple intervention diagnostics

| Rule | Candidates | Rescue | Broken | Net | Precision |
|---|---:|---:|---:|---:|---:|
| FLIP_ON_ANY_FUTURE_MAJOR_EVENT | 248 | 84 | 164 | -80 | 33.87% |
| FLIP_ON_FUTURE_EMPLOYMENT | 107 | 34 | 73 | -39 | 31.78% |
| FLIP_ON_FUTURE_INFLATION | 113 | 37 | 76 | -39 | 32.74% |
| FLIP_ON_FUTURE_FOMC | 51 | 17 | 34 | -17 | 33.33% |
| FLIP_RECENT_EMP_1D_AGAINST_GE_0.0 | 14 | 4 | 10 | -6 | 28.57% |
| FLIP_RECENT_EMP_1D_AGAINST_GE_0.5 | 3 | 1 | 2 | -1 | 33.33% |
| FLIP_RECENT_EMP_1D_AGAINST_GE_1.0 | 1 | 0 | 1 | -1 | 0.00% |
| FLIP_RECENT_EMP_3D_AGAINST_GE_0.0 | 28 | 8 | 20 | -12 | 28.57% |
| FLIP_RECENT_EMP_3D_AGAINST_GE_0.5 | 6 | 1 | 5 | -4 | 16.67% |
| FLIP_RECENT_EMP_3D_AGAINST_GE_1.0 | 2 | 0 | 2 | -2 | 0.00% |

## 2026 V5-missed / OPAL-no-candidate reversal slice

- total: **55**
- H3 window contains any major event: **13**
- employment: **5**
- inflation: **5**
- FOMC: **3**
- employment release occurred within prior 3 calendar days: **4**

## Year-by-year any-event hazard

| Year | Future major event | n | V5 errors | Error rate |
|---:|---|---:|---:|---:|
| 2022 | False | 17 | 7 | 41.18% |
| 2022 | True | 12 | 6 | 50.00% |
| 2023 | False | 125 | 32 | 25.60% |
| 2023 | True | 63 | 21 | 33.33% |
| 2024 | False | 125 | 29 | 23.20% |
| 2024 | True | 72 | 27 | 37.50% |
| 2025 | False | 163 | 53 | 32.52% |
| 2025 | True | 48 | 15 | 31.25% |
| 2026 | False | 100 | 43 | 43.00% |
| 2026 | True | 53 | 15 | 28.30% |
