# GOLD CONTROL — UP COUNTERSIGN VETO V1 RESULT

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_UP_COUNTERSIGN_VETO_V1_RESEARCH`  
**Preregistration commit:** `34d69dbee2fc816e2def72ee2033abcd22a839b0`  
**Parent model:** frozen annual-origin SQRT-HAR-DR downside-risk alert  
**Runtime / production authority:** NONE  
**Final status:** `UP_COUNTERSIGN_VETO_NOT_SUPPORTED_WITH_CURRENT_ELIGIBLE_MODELS`

## 1. Question tested

The experiment tested the user's exact counter-model hypothesis:

> When SQRT-HAR-DR raises a high-downside-risk alarm, suppress the forced-DOWN interpretation if an independently frozen next-day direction model says UP at the same origin.

A veto produces `NO-DOWN / SUPPRESSED`. It does not produce an UP trading signal.

## 2. Parent baseline

Across the clean pre-2025 years 2022–2024, SQRT-HAR-DR issued 30 alarms:

- actual next-day DOWN: 14;
- actual next-day UP / forced-DOWN false alarms: 16;
- forced-DOWN precision: 46.67%.

The verifier therefore has a concrete job: remove some of the 16 false DOWN calls while retaining most of the 14 true DOWN calls.

## 3. Candidate results

### 3.1 TTSM S1 and S2 — same clock, but no pre-2025 counter-signal

TTSM and SQRT share the same governed Gold daily target axis. Exact return/sign checks passed.

On all 30 pre-2025 SQRT alarm days:

- TTSM_S1 UP vetoes: **0**;
- TTSM_S2 UP vetoes: **0**.

Therefore TTSM cannot perform the desired veto in the clean pre-2025 sample.

2025 stress:
- S1 vetoed 20 of 90 alarms: 11 good vetoes, 9 bad vetoes; veto precision 55.0%; true-DOWN retention 80.0%; remaining DOWN precision improved only from 50.0% to 51.43%.
- S2 vetoed 15 of 90 alarms: 8 good, 7 bad; veto precision 53.33%; true-DOWN retention 84.44%; remaining precision 50.67%.

Decision: `INSUFFICIENT_VETO_SUPPORT / NOT_PROMISING`.

### 3.2 Bonato QBoost h=1 — same clock, but veto is harmful

Only the preregistered next-day h=1 median signs were used.

Pre-2025 overlap is 19 SQRT alarms from 2023–2024, with 8 true DOWN and 11 false DOWN.

**AR1_QBOOST h=1:**
- vetoes: 7;
- good vetoes: 1;
- bad vetoes: 6;
- veto precision: 14.29%;
- false-alarm reduction: 9.09%;
- true-DOWN retention: 25.0%;
- remaining DOWN precision: 16.67%, down from 42.11%.

**AR1_RM_QBOOST h=1:**
- vetoes: 6;
- good vetoes: 1;
- bad vetoes: 5;
- veto precision: 16.67%;
- false-alarm reduction: 9.09%;
- true-DOWN retention: 37.5%;
- remaining DOWN precision: 23.08%, down from 42.11%.

Thus Bonato's UP calls remove true DOWN alarms much more often than they remove false DOWN alarms in the clean pre-2025 intersection.

2025 stress does not rescue this:
- AR1 vetoed 73/90 alarms, but removed 36 of 45 true DOWNs; true-DOWN retention only 20.0%.
- AR1_RM vetoed 54/90, but removed 28 of 45 true DOWNs; retention only 37.78%.

Decision: `COUNTERSIGN_VETO_NOT_SUPPORTED`.

### 3.3 Altuntaş AlexNet — target-clock mismatch

The Altuntaş reconstruction uses Twelve Data daily OHLC provider-day semantics, whereas the SQRT parent uses the governed New York grouped 5-minute Gold panel.

On exact origin-date joins, the candidate's recorded next-day actual sign matched the parent's next-day sign only:
- 10/17 = 58.82% on 2024 SQRT alarm overlap;
- 69/89 = 77.53% on 2025 overlap.

This is not an acceptable same-target alignment for a veto test.

Therefore Altuntaş is classified:
`BLOCKED_TARGET_CLOCK_MISMATCH / NOT_VALID_AS_PARENT_VETO`.

For anatomy only, even the raw 2024 exact-date join would fail the safety objective: it vetoed 11 alarms, removed 7 false DOWNs but also removed 4 of 7 true DOWNs, leaving true-DOWN retention at only 42.86%.

### 3.4 Preregistered 2-of-3 family consensus

The preregistered consensus required TTSM + Bonato + Altuntaş family votes.

Because Altuntaş fails the target-clock compatibility check, the three-family consensus is not admissible decision evidence.

Its raw 2024 anatomy was also weak:
- 17 common SQRT alarms;
- only 2 vetoes;
- 1 good and 1 bad;
- remaining DOWN precision 40.0% versus 41.18% baseline.

Decision: `INVALID_TARGET_CLOCK_MIX / INSUFFICIENT_VETO_SUPPORT`.

## 4. Weekly direction models

BCTX-AR, VLMC-BS, COVLMC, RealP-CARR and Parisi Rolling-Ward were deliberately not carried into daily veto origins. They predict a different weekly target horizon.

This does not mean those models were re-rejected here. It means their historical UP output cannot truthfully be used as a next-trading-day counter-signal without a newly preregistered daily-horizon reconstruction.

## 5. Execution correction

An interim in-memory Bonato check mistakenly keyed all Bonato horizons by origin, which allowed a later h=10 row to overwrite the h=1 row. This was detected before any result artifact was frozen.

The final evidence reported above:
- filters `horizon == 1` first;
- then performs the exact-date join;
- reproduces candidate `actual_return` and parent `target_close_return` exactly on the overlap.

The preregistration was not changed.

## 6. Final decision

**`UP_COUNTERSIGN_VETO_NOT_SUPPORTED_WITH_CURRENT_ELIGIBLE_MODELS`**

This result does **not** reject the user's counter-model architecture itself.

It rejects the currently available candidate set as a safe verifier:

- TTSM: clean clock, but no useful pre-2025 UP counter-signal on SQRT alarm days;
- Bonato: clean clock, but UP vetoes destroy too many real DOWN alarms;
- Altuntaş: target clock is insufficiently aligned and descriptive retention is also poor;
- three-family consensus: invalid because it mixes the misaligned Altuntaş axis and has weak support.

The unresolved requirement is a **same-clock UP/rebound verifier specifically capable of distinguishing SQRT false alarms from SQRT true DOWN alarms**. A successor must be preregistered under a new identity and must not be tuned on 2025.

## 7. Governance

- no random split;
- no 2025 tuning;
- no production DB writes;
- no runtime promotion;
- `AUTO_SELECTOR=OFF`;
- `AUTO_ENSEMBLE=OFF`;
- no BUY/SELL mapping;
- general DOWN engine remains NOT_PROVEN.
