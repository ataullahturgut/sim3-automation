# GOLD MONTHLY — R0/R1/R2 Regime Alarm Audit V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Scope:** descriptive regime-conditioned alarm behavior only; no alarm selection, weighting, threshold tuning, forecast correction, or routing.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_R0_R2_REGIME_ALARM_AUDIT_V1_AUTHORITY_2026-09-30.md`
- authority commit: `7ad8fcbfa6551b0016ccd2c517e57c9690f0e46a`

Execution:
- workflow: **Gold Monthly R0 R1 R2 Regime Alarm Audit V1**
- run: **36719020701**
- artifact: **11097775756**
- code commit: `7ef6834864f4d6766947042254552a93bb2cc4c8`
- workflow commit: `074e067258b583816c6278f9dba32051b915046a`
- artifact digest: `sha256:22465de9a9dea579075408b179861c48f825cb7d151e16c4f5d8fc95418f6567`
- scientific gate: **PASS**

## 2. Conditioning

Primary regime subset:
- use forecast **origin-month** HMM state;
- posterior >=60%;
- OOD excluded.

All alarm definitions remain frozen.

## 3. Primary regime sample sizes

| Regime | Targets | HIGH | MEDIUM | NORMAL | HIGH share |
|---|---:|---:|---:|---:|---:|
| R0 | 9 | 4 | 0 | 5 | 44.4% |
| R1 | 19 | 4 | 3 | 12 | 21.1% |
| R2 | 22 | 7 | 3 | 12 | 31.8% |

These HIGH shares are descriptive model-error prevalence inside the observed sample, not regime forecasts.

## 4. Union alarm behavior by regime

### T0_STANDARD

| Regime | Events | HIGH hits | HIGH recall | MEDIUM hits | False calls | False-call rate |
|---|---:|---:|---:|---:|---:|---:|
| **R0** | 2 | 2/4 | 50.0% | 0 | **0** | **0.0%** |
| **R1** | 8 | 2/4 | 50.0% | 1 | **5** | **62.5%** |
| **R2** | 8 | 5/7 | **71.4%** | 1 | 2 | **25.0%** |

The same frozen T0_STANDARD architecture behaves very differently by regime.

### ANY_VISIBLE

| Regime | Events | HIGH hits | HIGH recall | MEDIUM hits | False calls | False-call rate | Useful-call rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| R0 | 7 | 4/4 | **100%** | 0 | 3 | 42.9% | 57.1% |
| R1 | 16 | 4/4 | **100%** | 2 | **10** | **62.5%** | 37.5% |
| R2 | 12 | 7/7 | **100%** | 2 | 3 | **25.0%** | **75.0%** |

All visible channels cover all observed HIGH cases in each confident regime, but the false-call burden is highly regime-dependent.

## 5. R0 details

Confident R0 targets:
- 9 targets
- HIGH: 2022-05, 2022-07, 2022-11, 2023-01
- NORMAL: 2022-03, 2022-06, 2022-08, 2022-10, 2022-12
- no MEDIUM cases.

Individual signals:

- A: 1 event -> 2022-11 HIGH, 0 false.
- B: 1 event -> 2023-01 HIGH, 0 false.
- G: 1 event -> 2022-08 NORMAL, 1 false.
- I1: 1 event -> 2022-05 HIGH, 0 false.
- I2: 5 events -> 2 HIGH, 3 false; false-call rate 60%.
- T1_WGC: 6 events -> 3 HIGH, 3 false; false-call rate 50%.
- C/D/E/H: no events in confident R0.

R0 ANY_VISIBLE false calls:
- 2022-08 — APE 2.031% — G + I2 + T1_WGC
- 2022-10 — 0.193% — I2 + T1_WGC
- 2022-12 — 1.755% — I2 + T1_WGC

R0 is therefore characterized by:
- selective T0_STANDARD signals being very clean in this sample;
- ETF persistence / WGC channels carrying substantial noise.

## 6. R1 details

Frozen from the completed R1 audit:

- 19 targets
- HIGH 4
- MEDIUM 3
- NORMAL 12.

Key signal behavior:
- B: 2 events, both false -> 100% false-call rate.
- H: 4 events -> 1 HIGH + 1 MEDIUM + 2 false.
- I2: 4 events -> 2 HIGH + 2 false.
- T1_WGC: 13 events -> 2 HIGH + 2 MEDIUM + 9 false.
- A: 1 HIGH + 1 false.
- G: one event, true HIGH; n=1.

R1 is the noisiest observed regime for both T0_STANDARD and ANY_VISIBLE.

## 7. R2 details

Confident R2 targets:
- 22 targets
- HIGH: 2024-11, 2025-02, 2025-03, 2025-09, 2025-10, 2025-11, 2026-01
- MEDIUM: 2024-07, 2025-01, 2025-05
- NORMAL: 12.

Individual signals:

### A
- 2 events
- HIGH: 2025-09
- false: 2025-12 (APE 2.166%)
- false-call rate 50%.

### B
- 1 event
- HIGH: 2025-03
- no false call.

### C
- 1 event
- MEDIUM: 2024-07
- no false call.

### D
- 1 event
- HIGH: 2024-11
- no false call.

### E
- **3 events**
- HIGH: 2025-11, 2026-01
- MEDIUM: 2025-05
- false: **0**
- useful-call rate **100% in this observed R2 sample**.

E remains discovery-period/unvalidated despite this favorable descriptive result.

### H
- 4 events
- HIGH: 2025-02, 2025-10
- MEDIUM: 2024-07
- false: 2024-08 (APE 1.796%)
- false-call rate 25%
- useful-call rate 75%.

### I1 / I2 / G
- no events in confident R2.

### T1_WGC
- 1 event
- 2024-05 NORMAL, APE 1.223%
- false-call rate 100% (n=1).

R2 ANY_VISIBLE false calls:
- 2024-05 — T1_WGC — APE 1.223%
- 2024-08 — H — APE 1.796%
- 2025-12 — A — APE 2.166%

## 8. Signal behavior changes by regime

The strongest descriptive regime-dependence:

### B
- R0: 1/1 HIGH, 0 false
- R1: 0 HIGH, 2/2 false
- R2: 1/1 HIGH, 0 false

This is a sharp sign reversal in observed usefulness, but sample sizes are small.

### H
- R0: no events
- R1: 1 HIGH + 1 MEDIUM + 2 false
- R2: 2 HIGH + 1 MEDIUM + 1 false

H is descriptively cleaner in R2 than R1.

### I2
- R0: 2 HIGH / 3 false
- R1: 2 HIGH / 2 false
- R2: no confident events

I2 is associated with R0/R1 rather than the confident R2 accumulation state.

### T1_WGC
- R0: 3 HIGH / 3 false
- R1: 2 HIGH + 2 MEDIUM / 9 false
- R2: 0 useful / 1 false

Raw T1_WGC has very different usefulness by regime and is especially noisy in R1.

### E
- R0: no events
- R1: no events
- R2: 2 HIGH + 1 MEDIUM / 0 false

All observed E activity is concentrated in R2.

## 9. R2 raw-state sensitivity

If raw R2 assignments are included regardless of confidence/OOD:
- 26 targets
- HIGH 7
- MEDIUM 4
- NORMAL 15
- ANY_VISIBLE 15 events
- HIGH 7/7
- MEDIUM 3
- false 5
- false-call rate 33.3%.

Additional raw-R2 false calls include:
- 2026-04 — I1 — APE 0.608%
- 2026-07 — G + I2 + T1_WGC — APE 2.030%.

These originate from OOD or low-confidence state months and therefore remain outside the primary confident-R2 audit.

## 10. Binding conclusion

1. Existing alarm behavior is **not regime-invariant**.
2. R1 is substantially noisier than R0/R2 for the observed T0_STANDARD and ANY_VISIBLE unions.
3. R2 is the cleanest observed regime for ANY_VISIBLE: 7/7 HIGH coverage, 2 MEDIUM hits, 3 false calls; false-call rate 25%.
4. R0 selective T0_STANDARD is very clean in the observed sample: 2 HIGH hits, 0 false calls; coverage remains only 50%.
5. Individual signals show large regime differences, especially B, H, I2, T1_WGC, and E.
6. These results are descriptive and sample sizes are small; they do not authorize alarm selection or regime-specific weights.
7. A later stage may formally test regime-conditioned reliability, but no such selection/weighting is performed here.
