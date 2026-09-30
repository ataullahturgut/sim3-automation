# GOLD MONTHLY — ChHHO ETF Anomaly / Dynamic Regime Result

**Date:** 2026-09-30
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS
**Scope:** alarm research only; no routing/model switching.

## 1. Official origin-safe ETF sources

Two large physically backed US gold funds were analyzed from official daily data:

### GLD
SPDR Gold Shares official Historical Archive.
Daily fields used:
- Tonnes of Gold
- Daily Share Volume

### IAU
iShares Gold Trust official Historical data.
Daily field used:
- Shares Outstanding

The daily records are contemporaneous and therefore eligible as origin-known information.

Monthly World Gold Council global ETF flow reports were used only as ex-post corroboration, not as predictors, because the monthly reports are published after month-end.

## 2. V1 static anomaly screen — negative result

Authority:
- `GOLD_MONTHLY_CHHHO_ETF_ANOMALY_SCREEN_V1_AUTHORITY_2026-09-30.md`
- authority commit: `c1e440496b60444bbdb3dcf7ddbd86a1cba55388`

Execution:
- workflow: **Gold Monthly ChHHO ETF Anomaly Screen V1**
- run: **36704096595**
- artifact: **11091336563**
- workflow/code head: `48098a09a74bfaee22caa93097cb714e390bdf2d`
- scientific gate: **PASS**

Calibration:
- 2010-01..2020-12 only.

Frozen single-month anomaly thresholds:
- combined GLD/IAU flow Q10 = **-3.3588%**
- GLD tonnes monthly change Q10 = **-4.4034%**
- IAU shares monthly change Q10 = **-2.3666%**
- GLD churn Q90 = **8.7902%**
- IAU churn Q90 = **7.1857%**
- GLD volume ratio Q90 = **1.4981x**
- ETF divergence Q90 = **5.0605pp**

### Core result

None of the four unexplained HIGH-APE targets had a V1 single-month Q10/Q90 ETF anomaly:

| Target | Origin | APE | GLD m/m | IAU m/m | Combined | Static anomalies |
|---|---|---:|---:|---:|---:|---:|
| 2022-05 | 2022-04 | 4.324% | +0.285% | +0.744% | +0.514% | 0 |
| 2022-07 | 2022-06 | 3.748% | -1.690% | -1.674% | -1.682% | 0 |
| 2022-09 | 2022-08 | 3.509% | -3.231% | -1.008% | -2.120% | 0 |
| 2024-03 | 2024-02 | 6.098% | -3.318% | -1.564% | -2.441% | 0 |

Static ETF_STRESS_2PLUS:
- events across 58 usable targets: 3
- HIGH hits: 0
- false alarms: 3

Binding interpretation:
**single-month ETF extremity is rejected as the explanation for the four core misses.**

## 3. V2 dynamic regime screen — positive result

Authority:
- `GOLD_MONTHLY_CHHHO_ETF_DYNAMIC_REGIME_V2_AUTHORITY_2026-09-30.md`
- authority commit: `e85f36caf84130da833904d18864875e144520fb`

Execution:
- workflow: **Gold Monthly ChHHO ETF Dynamic Regime V2**
- run: **36704354365**
- artifact: **11090919621**
- code commit: `f7072974ea99f4113d77522aaa33011fcf6ab414`
- workflow commit: `0bf83b9129674d1db4c991b2220ebf757bf31510`
- scientific gate: **PASS**

Calibration:
- 2010-01..2020-12 only.

Frozen dynamic thresholds:
- combined-flow monthly deterioration Q10: **-4.2816 percentage points**
- 3-month cumulative combined flow Q10: **-6.1704%**
- 6-month cumulative combined flow Q10: **-10.3011%**
- combined-outflow streak Q90: **3.9 months** (operationally 4 consecutive months)
- GLD+IAU simultaneous-outflow streak Q90: **2 months**

### Four core HIGH-error targets

#### 2022-05 / origin 2022-04
- APE: **4.324% HIGH**
- GLD m/m holdings: +0.285%
- IAU shares m/m: +0.744%
- combined flow: +0.514%
- **FLOW_DELTA1 = -4.3673pp**
- historical Q10 threshold = -4.2816pp
- **ETF_FLOW_DETERIORATION_Q10 = TRUE**

Interpretation:
The level was still positive, but ETF demand momentum had collapsed unusually sharply from the prior month.

This matches WGC's later global report:
- April 2022 global inflow +43t;
- 77% lower than March's exceptionally strong inflow.

#### 2022-07 / origin 2022-06
- APE: **3.748% HIGH**
- GLD: -1.690%
- IAU: -1.674%
- **both-fund outflow streak = 2 months**
- historical Q90 threshold = 2 months
- **ETF_BREADTH2_STREAK_Q90 = TRUE**

Interpretation:
Not an extreme one-month outflow; a persistent, broad redemption regime across both major funds.

WGC later reported June as the second consecutive global gold-ETF outflow month, after 53t left in May and another 28t in June.

#### 2022-09 / origin 2022-08
- APE: **3.509% HIGH**
- GLD: -3.231%
- IAU: -1.008%
- combined flow: -2.120%
- both-fund outflow streak: **4 months**
- combined-outflow streak: **4 months**
- 3-month cumulative combined flow: **-6.794%**

Flags:
- **ETF_BREADTH2_STREAK_Q90 = TRUE**
- **ETF_OUTFLOW_STREAK_Q90 = TRUE**
- **ETF_FLOW_SUM3_Q10 = TRUE**

Interpretation:
This is the strongest ETF-regime signal among the four core misses.

WGC later reported August as the fourth consecutive global outflow month, with 51t leaving global gold ETFs after 81t in July.

Cross-model context:
- 2022-09 was not a broad shared-hard month under the existing competitive-model rank test;
- only **1/16** competitive models placed it in their own worst eight;
- 8/15 alternatives beat ChHHO;
- best alternative AE 41.32 vs ChHHO 58.98.

Therefore ETF persistence may be especially useful here as an origin-state warning for a partially model-specific miss.

#### 2024-03 / origin 2024-02
- APE: **6.098% HIGH**
- GLD: -3.318%
- IAU: -1.564%
- both-fund outflow streak: **2 months**
- **ETF_BREADTH2_STREAK_Q90 = TRUE**
- 6-month combined flow: -8.737% (negative but not below the historical Q10 threshold)

Interpretation:
Again, the signal is persistence/breadth rather than a single-month extreme.

WGC later reported February 2024 as the ninth consecutive month of global gold-ETF outflows, with holdings falling by 49t to 3,126t.

Cross-model context:
- 2024-03 is a genuine SHARED-HARD month (16/16 competitive models top-8).

ETF persistence is therefore better interpreted as a global hard-regime warning here, not a ChHHO-specific failure signal.

## 4. Dynamic mechanism statistics

### ETF_FLOW_DETERIORATION_Q10
Across 58 usable targets:
- events: **2**
- HIGH hits: **1**
- false alarms: **1**
- hit: **2022-05**
- other event: 2026-04

Status:
**rare sharp ETF-demand-transition candidate warning.**

### ETF_BREADTH2_STREAK_Q90
Definition:
GLD and IAU both show monthly holdings/shares contraction for at least the historical Q90 persistence length (2 months).

Across 58 usable targets:
- events: **12**
- HIGH hits: **5**
- false alarms relative to HIGH: **7**
- precision: **41.7%**
- HIGH recall: **29.4%**

HIGH hits:
- **2022-07**
- **2022-09**
- 2022-11
- 2023-08
- **2024-03**

This is notable because it independently identifies:
- two core shared/broadly-hard cases (2022-07, 2024-03);
- the newly exposed normalized-error case 2022-09;
- two existing A-mechanism hits (2022-11, 2023-08).

Status:
**promising ETF persistence / redemption-regime warning, not a hard alarm due to false alarms.**

### ETF_FLOW_SUM3_Q10
- events 6
- HIGH hits 2
- hit targets: 2022-09, 2022-11
- precision 33.3%

### ETF_OUTFLOW_STREAK_Q90
- events 7
- HIGH hits 2
- hit targets: 2022-09, 2022-11
- precision 28.6%

## 5. Main scientific conclusion

The hypothesis must be stated carefully:

**Rejected:** "the four hard months have extreme one-month ETF values."

**Supported as an exploratory mechanism:** "the four hard months occur during abnormal ETF flow transitions or persistent broad redemption regimes."

Descriptively, all four core HIGH-error targets fall into one of two independently frozen dynamic states:
- 2022-05: sharp flow deterioration;
- 2022-07, 2022-09, 2024-03: simultaneous GLD+IAU outflow persistence.

This does **not** justify constructing a post-hoc OR hard alarm. The two mechanisms must remain separate candidates until evaluated prospectively or on an untouched historical segment.

## 6. Proposed mechanism names

- **I1 — ETF FLOW DETERIORATION:** sharp month-to-month collapse in combined GLD/IAU flow state.
- **I2 — ETF REDEMPTION PERSISTENCE:** GLD and IAU both contract for a historically extreme consecutive-month duration.

Both are **warning candidates**, not production hard alarms.

## 7. Governance

- All predictors are origin-month daily ETF data.
- No target-month ETF data used.
- 2010-2020 calibration only.
- No threshold retuning.
- Monthly WGC global flows used only as external corroboration.
- No router/model switching authorized.
