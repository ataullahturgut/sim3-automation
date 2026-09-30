# GOLD MONTHLY — Frozen Market-State × ChHHO Reliability Audit V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / NO ALARM-WEIGHTING PROMOTION

## 1. Authority and execution

Authority:
- gold_axis_2026/GOLD_MONTHLY_MARKET_STATE_CHHHO_RELIABILITY_AUDIT_V1_AUTHORITY_2026-09-30.md
- authority commit: 49b4c52174f26984b8a273025b76c1decf6e1a65

Code:
- gold_axis_2026/tools/gold_monthly_market_state_chhho_reliability_audit_v1.py
- code commit: e9f13ab8b0d5a736e08b765173f4405d212178c8

Workflow:
- .github/workflows/gold-monthly-market-state-chhho-reliability-audit-v1.yml
- workflow commit: e1a8af5592f8481281c1c8e740fbb8a32aaa82aa

Execution:
- workflow: Gold Monthly Market-State ChHHO Reliability Audit V1
- run: 36754939746
- artifact: 11116487006
- artifact digest: sha256:a783ad0d9d8ef94ebfe3cb79644975cab35c57fa7dddaf1fd4f07b7a99dc3d65
- scientific gate: PASS

## 2. Critical chronology

The audit joins market state by **forecast origin month**, not by target month.

For a target t+1 forecast:
- state at completed origin month t is used.

This matters materially in 2026.

Example:
- 2026-01 market state is evaluated against the forecast for 2026-02.
- The large 2026-01 ChHHO error was generated at origin 2025-12, whose market-state category was NORMAL under the primary expanding schedule.

No target-month market state was used.

## 3. Primary DEV result — EXPANDING_REFIT, targets 2022-04..2024-12

Overall ChHHO:
- n = 33
- ΣAE = 1413.0299 USD
- MAE = 42.8191 USD
- direction = 24/33 = 72.73%
- HIGH = 8/33 = 24.24%

### NORMAL
- n = 20
- MAE = **53.0036 USD**
- mean APE = **2.5618%**
- HIGH = **7/20 = 35.0%**
- direction = **16/20 = 80.0%**

### EXTREME
- n = 4
- MAE = **29.8948 USD**
- mean APE = **1.5966%**
- HIGH = **0/4 = 0%**
- direction = **2/4 = 50.0%**
- worst AE = 48.9582 USD

EXTREME / NORMAL MAE ratio:
- **0.564**

Thus EXTREME has **lower**, not higher, next-month price error on primary DEV.

Diagnostic statistics:
- mean MAE difference EXTREME - NORMAL = **-23.1088 USD**
- deterministic bootstrap 95% CI = **[-47.1168, -0.9645]**
- Mann-Whitney two-sided p = **0.2405**
- n is only 4 for EXTREME, so this is not treated as stable proof.

### TRANSITION
- n = 9
- MAE = **25.9310 USD**
- mean APE = **1.3256%**
- HIGH = **1/9 = 11.1%**
- direction = **6/9 = 66.7%**

TRANSITION / NORMAL MAE ratio:
- **0.489**

Diagnostic statistics:
- mean MAE difference TRANSITION - NORMAL = **-27.0726 USD**
- deterministic bootstrap 95% CI = **[-48.1829, -5.1253]**
- Mann-Whitney two-sided p = **0.0942**

Again, DEV Transition does not behave as a high-error-risk state.

## 4. Schedule sensitivity

ANNUAL_ANCHORED on the same DEV window does not reproduce the expanding Extreme relationship:

- NORMAL: n=21, MAE **44.73**, HIGH **23.8%**
- EXTREME: n=3, MAE **61.78**, HIGH **66.7%**
- TRANSITION: n=8, MAE **33.86**, HIGH **12.5%**

Therefore the Extreme-to-ChHHO relationship is **schedule-sensitive** in DEV.

This materially weakens any attempt to interpret EXTREME as a reliable ChHHO risk flag.

## 5. Opened 2025-2026 evidence — EXPANDING_REFIT

This period is already inspected and is descriptive only.

### NORMAL
- n = 12
- MAE = **115.58 USD**
- mean APE = **2.993%**
- HIGH = **5/12 = 41.7%**
- direction = **66.7%**

### EXTREME
- n = 4
- MAE = **75.59 USD**
- mean APE = **1.635%**
- HIGH = **0/4 = 0%**
- direction = **100%**

### TRANSITION
- n = 3
- MAE = **332.86 USD**
- mean APE = **8.106%**
- HIGH = **3/3 = 100%**
- direction = **33.3%**

Opened-period Transition therefore looks strongly associated with ChHHO failure.

However this relationship **reverses the DEV pattern**, where Transition had lower error than NORMAL.

The opened-period Transition months are too few and the transition detector itself failed its prior promotion gate. Therefore this result cannot authorize alarm weighting.

## 6. 2025 separately

EXPANDING:
- NORMAL: n=10, MAE 87.34, HIGH 40%
- TRANSITION: n=1, MAE 288.42, HIGH 100%
- DEFER: n=1, MAE 90.25
- EXTREME: n=0

The single 2025 Transition-origin forecast corresponds to:
- origin 2025-08
- target 2025-09
- AE 288.42 USD
- HIGH.

This is descriptive single-event evidence only.

## 7. 2026 chronology — primary EXPANDING_REFIT

| Origin state month | Forecast target | Frozen state category | ChHHO AE | Severity | Direction |
|---|---|---|---:|---|---|
| 2025-12 | 2026-01 | NORMAL | 458.50 | HIGH | wrong |
| 2026-01 | 2026-02 | EXTREME | 45.37 | NORMAL | correct |
| 2026-02 | 2026-03 | EXTREME | 145.62 | MEDIUM | correct |
| 2026-03 | 2026-04 | EXTREME | 28.70 | NORMAL | correct |
| 2026-04 | 2026-05 | NORMAL | 55.10 | NORMAL | correct |
| 2026-05 | 2026-06 | TRANSITION | 362.17 | HIGH | wrong |
| 2026-06 | 2026-07 | EXTREME | 82.68 | NORMAL | correct |
| 2026-07 | 2026-08 | TRANSITION | 347.99 | HIGH | wrong |

2026 category summaries:
- NORMAL: n=2, MAE **256.80**, HIGH 50%, direction 50%
- EXTREME: n=4, MAE **75.59**, HIGH 0%, direction 100%
- TRANSITION: n=2, MAE **355.08**, HIGH 100%, direction 0%

This is the clearest chronology-safe finding:
- EXTREME is **not** acting as a next-month ChHHO failure warning in 2026.
- Transition origins 2026-05 and 2026-07 precede the two very large June/August errors.
- the January 2026 large error is **not** preceded by an EXTREME origin state; its origin 2025-12 is NORMAL.

## 8. Main interpretation

### EXTREME
The hypothesis "within-regime EXTREME means ChHHO is more likely to fail next month" is **not supported** by the primary expanding evidence.

Observed:
- DEV EXTREME has lower MAE and zero HIGH errors.
- 2026 EXTREME has lower MAE and zero HIGH errors.
- annual DEV points in the opposite direction, showing schedule sensitivity.

Therefore Extreme V1 should remain a **market-description layer**, not a ChHHO risk multiplier.

### TRANSITION
Transition evidence is **non-stationary / unstable**:
- DEV: lower error than NORMAL.
- opened 2025-2026: very high error, 3/3 HIGH.

This is potentially important because it fits the recent regime-change episode, but the reversal across periods and the failed Transition V2 promotion gate prevent operational use.

## 9. Binding decision

Do **not** use EXTREME to downweight ChHHO.

Do **not** use Transition V2 to automatically downweight/switch ChHHO yet.

Do **not** optimize state thresholds against ChHHO errors.

The frozen market-state layers remain descriptive research evidence.

## 10. Next scientific step

The current simple Transition V2 rule is not historically selective enough, while its 2025-2026 ChHHO relationship is potentially valuable.

The next regime-side experiment, if continued, should be **structurally different**, not another threshold tweak:

- duration-aware / semi-Markov regime transition model, and/or
- dedicated multivariate changepoint detector with persistence.

Its detector must be frozen using historical market-state data only before any ChHHO reliability analysis.

Alarm weighting remains blocked.
