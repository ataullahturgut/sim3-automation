# GOLD MONTHLY — Alarm Fine-Tuning V1 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / BINDING DEV-ONLY FINE-TUNE
**Purpose:** update alarm decision settings using DEV only, then freeze before any 2025/2026 evaluation.

## 1. Data separation

### Fine-tune authority
- DEV targets: **2022-04..2024-12**
- 33 rows
- outcomes use binding APE severity:
  - NORMAL <2.5%
  - MEDIUM 2.5%..<3.0%
  - HIGH >=3.0%

### Untouched transport
- 2025-01..2025-12
- 2026-01..2026-08

No 2025/2026 outcome may influence rule selection, signal membership, objective, thresholds, or tie-breaking.

## 2. Existing signal definitions are frozen

Do **not** retune the underlying definitions of A, B, C, D, E, G, H, I1, I2, T1_WGC.

This fine-tune changes only the decision layer: which frozen signals are allowed to create a RED alarm versus AMBER/shadow status.

## 3. T0 RED search

A and D are protected selective mechanisms and remain eligible in every T0 RED candidate.

Candidate additional T0 signals:
- B
- G
- H
- I1
- I2

C is not a HIGH-alarm search input because its frozen observed role is MEDIUM-error warning.
E is excluded from fine-tune selection because it has no DEV activations and therefore cannot be estimated from DEV without leakage.

Candidate rule:
'T0_RED = A OR D OR any selected subset of {B,G,H,I1,I2}'.

Selection is deterministic and DEV-only:

1. require DEV HIGH recall >=75%;
2. minimize NORMAL false-call count;
3. maximize DEV HIGH recall;
4. minimize false-call rate;
5. maximize MEDIUM hits;
6. minimize number of optional signals;
7. deterministic alphabetical tie-break.

No candidate interaction beyond sparse OR is allowed.

## 4. T1 fine-tune

Raw T1_WGC is a noisy early-month warning and is not automatically RED.

Candidate T1 confirmation rule:
'T1_RED_CONFIRM = T1_WGC AND (OR of a non-empty subset of {A,B,C,D,G,H,I1,I2})'.

Selection:
1. preserve **all DEV HIGH hits of raw T1_WGC**;
2. minimize NORMAL false calls;
3. maximize MEDIUM hits;
4. minimize number of confirming signals;
5. alphabetical tie-break.

This creates a confirmation gate, not a new WGC threshold.

## 5. Final tuned alarm

'FINAL_RED = T0_RED OR T1_RED_CONFIRM'.

Because T1 occurs after month-end, report:
- T0 RED status at forecast time;
- T1 incremental RED status after WGC report;
- final RED status.

Do not backdate T1 to month-end.

## 6. Non-RED channels retained

These remain visible and are tracked separately, never discarded:

- 'AMBER_T0 = B OR C OR H'
- 'SHADOW_T0 = E OR G'
- raw 'T1_WGC'

The selected T0 RED subset may overlap AMBER definitions; RED takes precedence operationally.

I2 retains regime-warning interpretation even if selected into RED by DEV tuning.

## 7. Mandatory DEV report before transport

Report selected rule and:
- RED events
- HIGH hits / recall
- MEDIUM hits
- NORMAL false calls
- false-call rate
- useful-call rate
- exact false-call targets
- exact missed HIGH targets
- raw T0_STANDARD comparison
- raw ANY_VISIBLE comparison.

The fine-tune artifact must contain only DEV selection results plus frozen rule configuration.

## 8. 2025/2026 evaluation

A separate workflow must consume the frozen fine-tune artifact.

For 2025 and 2026 separately and combined, report:
- every target month;
- APE and severity;
- T0_RED;
- T1_RED_CONFIRM;
- FINAL_RED;
- AMBER_T0;
- SHADOW_T0;
- active raw signals;
- outcome of FINAL_RED: HIGH_HIT / MEDIUM_HIT / FALSE_CALL / OFF;
- HIGH recall;
- false-call rate;
- exact false-call months and APE;
- exact missed HIGH months;
- incremental value of T1.

No rule modification after opening 2025/2026.

## 9. Safe-veto governance

The cross-model V2 safe-veto candidate is **not** included in FINAL_RED V1 unless an unchanged 2025/2026 transport calculation can be produced from frozen transport forecasts.

It remains a separate exploratory suppressor until then.
