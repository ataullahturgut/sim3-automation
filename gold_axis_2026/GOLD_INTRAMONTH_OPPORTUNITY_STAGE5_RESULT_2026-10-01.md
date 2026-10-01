# GOLD INTRAMONTH OPPORTUNITY — Stage 5 Calibration & Decision-Threshold Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / PASS / FROZEN ALERT CANDIDATE**  
**Workflow:** Gold Intramonth Opportunity Stage5  
**Run:** **36866945286**  
**Artifact:** **11164696977**  
**Artifact digest:** `sha256:3c3133b79cf40655d9a3f266405547096f275153d4e83a3a71cbdbdc8a3b85be`  
**Runner commit:** `6cb84ff75d4646346de49089aee596d2f905b45f`  
**Authority:** `GOLD_INTRAMONTH_OPPORTUNITY_STAGE5_AUTHORITY_2026-10-01.md`

## 1. Binding decision

Freeze:

- probability source: **RAW Stage-3 HGB probability**
- target: **K100**
- alert rule: **p(K100) >= 0.30**
- monthly context: **not used**
- Platt calibration: **rejected**
- isotonic calibration: **rejected**.

This is a **DEV-frozen alert candidate**, not yet a production trading signal.

2025 may now be transported without retuning.

## 2. Calibration result

| Method | Brier | Log loss | ECE10 | PR-AUC | ROC-AUC | Decision |
|---|---:|---:|---:|---:|---:|---|
| **RAW** | **0.18942** | **0.56550** | 0.05275 | **0.3296** | **0.6078** | **RETAIN** |
| PLATT | 0.18956 | 0.56588 | **0.03202** | 0.3124 | 0.5912 | FAIL |
| ISOTONIC | 0.19050 | 0.65355 | 0.04723 | 0.3116 | 0.5893 | FAIL |

Platt improves ECE but worsens both Brier and log loss and reduces ranking metrics.

Isotonic is materially worse in log loss and fails the yearly stability rule.

Therefore no calibration layer replaces RAW.

## 3. Calibration stability

Platt relative Brier change versus RAW:
- 2022: **-0.68%**
- 2023: **-1.93%**
- 2024: **+2.50%**
- aggregate: **-0.07%**.

Isotonic:
- 2022: 0.00%
- 2023: **-3.38%**
- 2024: +1.86%
- aggregate: **-0.57%**.

The chronology-safe calibrators do not add sufficiently stable probability quality.

## 4. Frozen threshold screen

Unconditional DEV K100 prevalence:
- **25.90%**.

| Threshold | Alerts | Alert rate | Precision | Recall | Precision lift vs prevalence | Mean MFE5 after alert | Mean MAE5 after alert | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 0.20 | 401 | 53.5% | 31.2% | 64.4% | +5.3 pp | +1.24% | -0.93% | FAIL |
| 0.25 | 247 | 33.0% | 32.0% | 40.7% | +6.1 pp | +1.21% | -0.86% | FAIL |
| **0.30** | **132** | **17.6%** | **35.6%** | **24.2%** | **+9.7 pp** | **+1.18%** | **-0.88%** | **PASS** |
| 0.35 | 58 | 7.7% | 41.4% | 12.4% | +15.5 pp | +1.21% | -0.73% | FAIL |
| 0.40 | 19 | 2.5% | 31.6% | 3.1% | +5.7 pp | +0.64% | -0.96% | FAIL |
| 0.45 | 3 | 0.4% | 33.3% | 0.5% | +7.4 pp | +0.79% | -1.30% | FAIL |
| 0.50 | 2 | 0.3% | 0.0% | 0.0% | -25.9 pp | +0.14% | -1.19% | FAIL |

Only **T30** passes the preregistered operability gate.

## 5. T30 yearly robustness

| DEV year | Alerts | Alert rate | Precision | Recall | Mean MFE5 | Mean MAE5 |
|---|---:|---:|---:|---:|---:|---:|
| 2022 | 73 | 29.2% | 30.1% | 36.1% | +0.98% | -0.95% |
| 2023 | 48 | 19.1% | 39.6% | 27.1% | +1.11% | -0.89% |
| 2024 | 11 | 4.4% | **54.5%** | **9.5%** | +2.75% | -0.41% |

Interpretation:
- precision improves across years;
- alert frequency and recall fall materially in 2024;
- the preregistered yearly gate still passes because every year has >=5 alerts and precision >=25%;
- the declining alert frequency is a robustness caution that must be checked in frozen 2025 transport.

## 6. Monthly-DOWN mission subset

T30 inside frozen monthly-DOWN DEV origins:

- origins: **392**
- alerts: **74**
- alert rate: **18.9%**
- K100 positives: 69
- true alerts: **19**
- false alerts: **55**
- precision: **25.68%**
- recall: **27.54%**
- mean MFE5 after alert: **+0.88%**
- median MFE5 after alert: **+0.77%**
- mean MAE5 after alert: **-1.12%**.

Monthly-UP:
- alerts: 36
- precision: **38.89%**
- recall: **14.14%**
- mean MFE5: +1.49%.

Important:

> T30 does pass the preregistered DOWN-subset gate, but only narrowly. It should not be described as a high-precision DOWN-month signal before transport.

Monthly DOWN remains reporting context, not a model feature or gate.

## 7. Volatility-bucket diagnostic

T30:

### Low SIGMA20 tercile
- alerts: **114**
- alert rate: 45.6%
- precision: **35.1%**
- recall: **48.8%**

### Mid volatility
- alerts: 9
- precision: 44.4%
- recall: 6.3%

### High volatility
- alerts: 9
- precision: 33.3%
- recall: 6.3%.

The alert concentrates strongly in the low-volatility tercile.

This is descriptive and cannot be used to create a new volatility gate after inspection.

## 8. Episode-deduplicated diagnostic

Because adjacent five-observation windows overlap, daily alerts naturally cluster.

For T30:
- daily alerts: **132**
- deduplicated alert episodes: **39**
- successful episodes: **19**
- episode precision: **48.72%**
- mean alerts per episode: **3.38**.

This suggests repeated daily alerts often refer to the same tactical setup.

Episode precision is diagnostic only; Stage 5 primary metrics remain daily-origin metrics.

## 9. What the alert means

T30 means:

> The frozen K100 model assigns at least 30% probability that Gold will achieve a five-observation maximum favorable excursion at least as large as its current 20-observation volatility-scaled hurdle.

K100 is not “Gold will rise tomorrow.”

It is not a guaranteed +2% signal.

Its hurdle changes with volatility:
- DEV median hurdle ≈ +2.09%
- monthly-DOWN median ≈ +1.94%.

## 10. Important limitation

Even at T30:
- only **35.6%** of daily alerts are K100 successes;
- about **64.4%** are false with respect to the strict K100 event;
- recall is only **24.2%**.

Therefore the alert is a **selective research opportunity flag**, not a standalone trading instruction.

The purpose of 2025 transport is to determine whether this modest DEV edge survives outside the selection period.

## 11. Artifact hashes

- `stage5_calibrated_predictions.csv`: `ffb764ca52ab47bd5a660b6264a47d892aeb8aeb4243fc0f851da978fc916e31`
- `stage5_calibration_metrics.csv`: `72a403cd61b6bb16b578520ad2e6873b4e5b138fe924ee75e63b442b13a6774e`
- `stage5_threshold_metrics.csv`: `54b0cea2a084b6b74d60d1f9e5593c98ec4a8437db64b424a8bcd9e15a8ccdf8`
- `stage5_threshold_year_metrics.csv`: `ab19cb41d9c2bf8b9d24b3354aa6d7481259ab690e068e2220e51329e4d9a855`
- `stage5_threshold_monthly_direction_metrics.csv`: `c8f781ad09db936c3a9e8a65e1047941e559ee33e6757991a657960398d66f09`
- `stage5_threshold_volatility_metrics.csv`: `7d8e9946da0cde37045501fa2f6198852eebcf724b1ed083a7c466d142d2713c`
- `stage5_episode_metrics.csv`: `7fad1ba0a4dc6ff867849eee7f4eaabb60424124b6d7cc7b2f6ca24702d5ce2e`
- `STAGE5_RESULT.md`: `40c18811c2cd229331ded48649da4f5124893aa33086e880c3885fa9eaa8be2b`

## 12. Decision and next stage

**Stage 5 = PASS.**

Frozen rule:
- model: **K100 G_ONLY/HGB_CLASS**
- probability: **RAW**
- alert: **p >= 0.30**.

Exact next stage:

**Stage 6 — Frozen 2025 Transport**

Requirements:
- no refit-rule changes;
- no threshold changes;
- no calibration changes;
- fit/predict chronology continues exactly from Stage 5;
- evaluate 2025 full year;
- report aggregate, monthly-DOWN subset, yearly/quarterly stability, episode metrics;
- if transport fails, do not rescue the rule using 2025 retuning.
