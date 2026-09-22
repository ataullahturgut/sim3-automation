# GOLD CONTROL — ROUTER V2 HISTORICAL EXTENSION V1 RESULT

**Date:** 2026-09-22  
**Identity:** `ROUTER_V2_HISTORICAL_EXTENSION_V1_RESEARCH`  
**Preregistration:** `2368e8856d12505eff705ebe9556d5fdf5444e55`  
**Final status:** `HISTORICAL_EXTENSION_VALIDATED_SUPPORT_INCREASED_BUT_LTT_NOT_YET_CERTIFIABLE`

## 1. Historical reconstruction succeeded

The frozen expert definitions were reconstructed directly from the governed 5-minute source panel.

Retained daily source:
- 2020-04-06 through 2024-12-30;
- 958 retained weekdays;
- minimum 240 five-minute bars/day.

Common expert support:
- 2021: 91 rows;
- 2022: 205;
- 2023: 203;
- 2024: 205.

The 2021 rows provide the origin-safe formation history needed for the 2022 Router extension.

## 2. Reproduction audit

Against the frozen 2023 and 2024 expert artifacts:

- target-date mismatch: **0**
- actual-direction mismatch: **0**
- TTSM S1/S2 UP-state mismatch: **0**
- Bonato AR1_RM h=1 median-UP mismatch: **0**
- RM_LOGIT UP mismatch: **0**
- AR1_RM_LOGIT UP mismatch: **0**

The reconstructed 2024 Router also reproduces the frozen Router V2 result exactly:

- n=205
- UP outputs=42
- TP=26
- FP=16
- UP precision=61.90%
- false-UP FPR=18.60%

On 2024 SQRT alarms it again gives exactly 4 Router-UP overlaps = 3 actual UP + 1 actual DOWN.

Therefore the historical extension passes the preregistered integrity gate.

## 3. Historical Router results

| Year | Rows | Router UP | TP | FP | UP precision | false-UP FPR |
|---|---:|---:|---:|---:|---:|---:|
| 2022 | 205 | 22 | 12 | 10 | **54.55%** | **10.20%** |
| 2023 | 203 | 19 | 5 | 14 | **26.32%** | **13.73%** |
| 2024 | 205 | 42 | 26 | 16 | **61.90%** | **18.60%** |

The weak 2023 Router year is retained as evidence; it is not removed post hoc.

## 4. SQRT alarm support

| Year | SQRT alarms | Actual DOWN | Actual UP | Router-UP overlap | Good / bad veto |
|---|---:|---:|---:|---:|---:|
| 2022 | 11 | 6 | 5 | 0 | 0 / 0 |
| 2023 | 2 | 1 | 1 | 0 | 0 / 0 |
| 2024 | 17 | 7 | 10 | 4 | 3 / 1 |
| **Pooled** | **30** | **14** | **16** | **4** | **3 / 1** |

So the alarm-conditional actual-DOWN support grows from **7** to **14**.

That clears the earlier simple support floor of 11 for a *zero-error single policy*.

## 5. But LTT certification is still not available

The frozen hard Router policy has:

- actual-DOWN calibration alarms = 14;
- bad suppressions = 1.

At the frozen risk target alpha=0.20, the exact one-sided lower-tail p-value is:

**0.1979121**

which is greater than delta=0.10.

Therefore the hard Router suppression rule still cannot be certified as having BAD_SUPPRESSION risk <=20% at 90% confidence.

With one observed bad suppression, a single-policy exact test requires at least **18** actual-DOWN alarm calibration cases.

For the previously proposed five-policy Bonferroni family:
- per-policy delta = 0.02;
- even zero bad suppressions require at least **18** actual-DOWN alarm cases;
- one bad suppression requires at least **27**.

## 6. Binding interpretation

The history extension worked and materially increased calibration support.

But it also shows that **14 cases are not enough once the observed bad suppression is counted**.

The scientifically valid response is not to weaken alpha/delta. The next step must either:
- find additional methodologically valid pre-2025 same-clock support; or
- preregister one single fixed suppression policy without choosing it from pooled alarm outcomes.

2025 was not used anywhere in this historical extension.
