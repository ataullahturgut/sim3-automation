# GOLD MONTHLY — Market Regime Walk-Forward Detection V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Operational regime freeze:** HOLD — transition behavior is not yet strong enough to authorize regime-conditioned alarm selection.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_MARKET_REGIME_WALKFORWARD_V1_AUTHORITY_2026-09-30.md`
- authority commit: `ea178786adb44ad0506972e051b433b2bf31fb67`

Code:
- `gold_axis_2026/tools/gold_monthly_market_regime_walkforward_v1.py`
- code commit: `ba7cc0772465f0e106e83432abe1700a27efc2dc`

Workflow:
- `.github/workflows/gold-monthly-market-regime-walkforward-v1.yml`
- workflow commit: `3041a36df6a7840c0368ba0edeb5533df69c901a`

Execution:
- workflow: **Gold Monthly Market Regime Walk-Forward V1**
- run: **36723724702**
- conclusion: **SUCCESS**
- artifact: **11101827380**
- artifact digest: `sha256:7f411996513c690f5af016be2073a28a66a3a2e509504d7bc9b12ab3f61e8f90`

Frozen input:
- Market Regime Discovery V1 run **36716979693**
- artifact **11097041821**

## 2. Governance / leakage audit

Detector uses only the 13 frozen market-state variables.

Explicitly excluded from fitting:
- ChHHO errors;
- HIGH/MEDIUM/NORMAL labels;
- A/B/C/D/E/G/H/I1/I2/T1 alarms;
- model forecasts;
- router/fallback outputs;
- reference regime labels;
- future market-state observations.

At month t:
- scaler/PCA/HMM fit window ends at **t-1**;
- current month t is transformed and filtered only after parameter fitting;
- K=3 is frozen from the prior regime-discovery architecture;
- posterior <60% => **BELIRSIZ**;
- OOD is a separate AŞIRI/OOD flag.

Scientific execution gate: **PASS**.

## 3. Primary results

### 3.1 Frozen-architecture transport: 2025-01..2026-08

20 months total.

- exact label agreement: **80.0%**
- reference-confident months: **18**
- strict R-state accuracy: **16/18 = 88.9%**
- decided-only accuracy: **16/16 = 100%**
- walk-forward BELIRSIZ rate: **10.0%**
- walk-forward OOD rate: **10.0%**
- strict balanced accuracy over represented states: **71.9%**
- R2 recall: **15/16 = 93.75%**
- R1 recall: **1/2 = 50.0%**
- no confident R0 reference month exists in this transport interval, so R0 transport recall is not estimable.

Interpretation:
The detector is very strong at maintaining the long R2 regime and makes no wrong confident R-state call in the transport period. Its weakness is timing the transition from R2 toward R1.

### 3.2 Core recent period: 2022-01..2026-08

56 months total.

- exact label agreement: **64.3%**
- reference-confident months: **51**
- strict R-state accuracy: **35/51 = 68.6%**
- decided-only accuracy: **35/46 = 76.1%**
- walk-forward BELIRSIZ rate: **10.7%**
- walk-forward OOD rate: **7.1%**
- strict balanced accuracy: **61.2%**

Per-regime recall:
- R0: **4/9 = 44.4%**
- R1: **8/17 = 47.1%**
- R2: **23/25 = 92.0%**

Interpretation:
The current detector is asymmetric: **R2 is recognized very well, while R0/R1 separation is materially weaker.**

### 3.3 Full replay: 2015-07..2026-08

134 months total.

- exact label agreement: **61.9%**
- reference-confident months: **125**
- strict R-state accuracy: **82/125 = 65.6%**
- decided-only accuracy: **82/118 = 69.5%**
- walk-forward BELIRSIZ rate: **6.0%**
- strict balanced accuracy: **63.0%**

Per-regime recall:
- R0: **45.8%**
- R1: **53.7%**
- R2: **89.4%**

This confirms the same structural asymmetry seen in the recent-period audit.

## 4. Mandatory checkpoint audit

### 4.1 2024-04 R2 onset

Reference:
- 2024-03: R1, posterior 96.5%
- 2024-04: R2, posterior 90.2%

Walk-forward:
- 2024-03: **R1**, posterior 98.1%
- 2024-04: underlying R2 but posterior **55.5%**, therefore **BELIRSIZ**
- 2024-05: **R2**, posterior 99.4%
- 2024-06: **R2**, posterior 99.8%

Result:
- R1 -> R2 transition detected with **1 month delay**.
- The actual transition month is not falsely forced into R1; it is correctly treated as low confidence, then R2 is recognized one month later.

This is a favorable transition pattern.

### 4.2 2026-05 / 2026-06 transition zone

Reference:
- 2026-04: R2, 98.3%
- 2026-05: R1 raw state but 52.7% => **BELIRSIZ**
- 2026-06: R2 raw state but 36.3% => **BELIRSIZ**
- 2026-07: R1, 70.1%
- 2026-08: R1, 98.6%

Walk-forward:
- 2026-04: **R2**, 98.4%
- 2026-05: **R2**, 70.9%
- 2026-06: **R2**, 79.4%
- 2026-07: underlying R1 but 50.8% => **BELIRSIZ**
- 2026-08: **R1**, 94.8%

Result:
- the walk-forward detector **did not identify May/June as an ambiguity zone**;
- it stayed confidently R2 through June;
- it became uncertain only in July;
- it confirmed R1 in August.

Relative to the first confident reference R1 month (2026-07), R1 detection delay is **1 month**.

This is the main weakness of V1.

## 5. Transition-delay audit

Notable recent transitions:

- 2022-02 R1 -> R0: **5-month delay**
- 2023-01 R0 -> R1: **1-month delay**
- 2024-04 R1 -> R2: **1-month delay**
- 2026-07 R2 -> R1: **1-month delay**

Historical replay also contains several 0-2 month transitions, but the 2022 R0 transition shows that the detector can be materially late when the new regime is not R2.

## 6. Binding interpretation

The answer is **not simply yes or no**.

What is supported:

1. The market-regime engine can identify a sustained R2 regime in real time with high reliability.
2. The 2024-04 R2 transition is recognized with only a one-month delay and with an uncertainty flag on the transition month.
3. 2025-2026 transport accuracy is strong when the detector makes a confident call.

What is not yet strong enough:

1. R0 and R1 recall are materially weaker than R2 in the long replay.
2. The 2026-05/06 transition zone is recognized too late: the detector remains confidently R2 instead of becoming uncertain.
3. Therefore the detector should **not yet be frozen as an operational gate for alarm weighting/suppression**.

## 7. Binding decision

**Do not move yet to regime-conditioned alarm selection.**

Keep all alarm channels unchanged.

The next regime-only research step should compare the current expanding-refit detector against a frozen/anchored HMM detection design, with no alarm inputs. The purpose is to determine whether parameter drift from monthly refitting is causing the weak R0/R1 and transition-zone behavior.

2025/2026 has now been inspected in this regime-detection audit and must not later be described as untouched for a tuned regime-detector variant.

No alarm selection.
No alarm weighting.
No forecast correction.
No routing/model switching.
