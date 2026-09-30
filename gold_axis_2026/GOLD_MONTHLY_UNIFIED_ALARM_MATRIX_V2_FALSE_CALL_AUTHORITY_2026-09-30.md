# GOLD MONTHLY — Unified Alarm Matrix V2 False-Call Accounting Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / BINDING CONSOLIDATION UPDATE
**Scope:** add explicit false-call accounting to the existing 58-row alarm matrix. No new alarm thresholds, no forecast correction, no routing/model switching.

## 1. Severity outcome

APE remains binding:
- NORMAL < 2.5%
- MEDIUM 2.5% <= APE < 3.0%
- HIGH APE >= 3.0%.

For each signal on each month:
- HIGH_HIT = signal on and severity HIGH
- MEDIUM_HIT = signal on and severity MEDIUM
- FALSE_CALL = signal on and severity NORMAL
- OFF = signal off

A MEDIUM hit is not counted as a false call.

## 2. Signals

A, B, C, D, E, G, H, I1, I2, T1_WGC.

Keep existing evidence statuses unchanged.

## 3. Union summaries

Report separately:
- T0_STANDARD = A OR B OR C OR D OR H
- T0_ALL_VISIBLE = A OR B OR C OR D OR E OR G OR H OR I1 OR I2
- T0_PLUS_T1_STANDARD = T0_STANDARD OR T1_WGC
- ANY_VISIBLE = T0_ALL_VISIBLE OR T1_WGC

For every union report:
- events
- HIGH hits
- MEDIUM hits
- NORMAL false calls
- HIGH precision
- useful-call rate = (HIGH + MEDIUM) / events
- false-call rate = NORMAL / events
- HIGH recall
- elevated (MEDIUM+HIGH) recall.

## 4. Required false-call outputs

For every individual signal and union:
- exact false-call target list
- APE of every false-call target
- active simultaneous signals in that month.

Also report:
- false-call months with 2+ simultaneous signals
- repeated false-call clusters
- yearly false-call burden.

## 5. Governance

- Do not drop a signal solely because it has false calls.
- Do not call all visible signals one production alarm.
- Do not optimize a new Boolean combination.
- The purpose is to expose selectivity and noise transparently before any future alarm selection.
