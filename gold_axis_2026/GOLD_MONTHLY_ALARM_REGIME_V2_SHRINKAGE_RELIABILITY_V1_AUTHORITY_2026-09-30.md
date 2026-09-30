# GOLD MONTHLY — Alarm × Live Regime × V2 Shrinkage Reliability Model V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / RELIABILITY-SCORING EXPERIMENT

## 1. Objective

Estimate the probability that an already-fired alarm is useful:

- useful = HIGH_HIT or MEDIUM_HIT;
- false = FALSE_CALL.

The model does not create new raw alarms. It assigns a reliability score to each already-active frozen signal using:

1. the signal's own historical reliability;
2. live R0/R1/R2 regime context;
3. V2 STABLE/TRANSITION context;
4. live regime posterior confidence.

The core question is:

> Does partial pooling across signal × live regime × V2 status improve chronology-safe alarm reliability enough to reduce false calls without materially losing HIGH coverage?

## 2. Frozen input

Use:
- `GOLD_MONTHLY_ALARM_REGIME_V2_RELIABILITY_AUDIT_V1_2026-09-30.json`
- primary V2 schedule already embedded: EXPANDING_REFIT
- 58 alarm rows.

Signals:
- A, B, C, D, E, G, H, I1, I2, T1_WGC.

Frozen unions:
- T0_STANDARD core signals = A/B/C/D/H.
- ANY_VISIBLE = all ten signals.

No alarm definition or threshold is changed before scoring.

## 3. Outcome

For each active individual signal event:

- y=1 if the frozen outcome is HIGH_HIT or MEDIUM_HIT;
- y=0 if FALSE_CALL.

OFF rows are not signal-event observations.

## 4. Reliability hierarchy

All means are empirical-Bayes-style shrinkage estimators with fixed pseudo-count strengths; no strength is tuned.

### 4.1 Global mean

`m_global = (useful_all + 1) / (events_all + 2)`

This is a Beta(1,1)-regularized event mean.

### 4.2 Signal mean

For signal s:

`m_s = (useful_s + 4*m_global) / (events_s + 4)`

### 4.3 Signal × regime mean

For signal s and semantic regime r:

`m_sr = (useful_sr + 4*m_s) / (events_sr + 4)`

### 4.4 Signal × V2-status mean

For signal s and status z in STABLE/TRANSITION:

`m_sz = (useful_sz + 4*m_s) / (events_sz + 4)`

### 4.5 Signal × regime × V2-status cell

Parent:

`m_parent = (m_sr + m_sz)/2`

Cell:

`m_srz = (useful_srz + 6*m_parent) / (events_srz + 6)`

This prevents 1/1, 2/2, etc. from becoming raw 0%/100% weights.

## 5. Posterior-confidence blending

V2 always supplies:
- best semantic state R0/R1/R2;
- semantic probability p.

Do not force the cell estimate as if p=1.

Three prespecified scores:

### M0 — SIGNAL_ONLY
`score_M0 = m_s`

### M1 — SIGNAL_REGIME
`score_M1 = p*m_sr + (1-p)*m_s`

### M2 — SIGNAL_REGIME_V2
`score_M2 = p*m_srz + (1-p)*m_sz`

Thus uncertain regime months automatically shrink back toward the status-specific signal estimate.

M2 is the primary candidate.

## 6. Chronology-safe DEV scoring

Primary DEV targets:
- 2022-04..2024-12.

For each DEV origin t:
- fit all shrinkage counts using only rows with origin < t;
- score active signals at t;
- then advance.

This is expanding origin-safe out-of-fold scoring.

No same-month or future outcome enters the score.

Earlier rows in the frozen 58-row matrix may serve only as prior historical observations if their origin precedes t.

## 7. Opened 2025-2026 transport scoring

For targets 2025-01..2026-08:

- freeze M0/M1/M2 counts using all rows with target <=2024-12;
- score all 2025-2026 events from that frozen pre-2025 fit;
- do not update using 2025/2026 outcomes.

This makes the opened-period comparison easier to interpret and prevents incremental adaptation from hiding transport failure.

2025/2026 remain opened/descriptive and do not select or tune the model.

## 8. Event-level scoring metrics

For M0/M1/M2 report separately on:
- DEV chronology-safe OOF;
- opened 2025-2026 frozen transport.

Metrics:
- n signal events;
- Brier score;
- log loss;
- mean predicted reliability for useful events;
- mean predicted reliability for false calls.

Primary scoring metric:
- **Brier score**.

## 9. Fixed reliability gate

For a simple policy diagnostic only:

`KEEP signal if reliability score >= 0.50`.

Threshold 0.50 is fixed before results and is not optimized.

Report for M0/M1/M2:
- kept individual signal events;
- useful kept;
- false kept;
- useful-event recall;
- false-call suppression.

## 10. Union reconstruction

Using the fixed 0.50 gate, reconstruct monthly unions:

### T0_STANDARD_GATED
Active accepted signal among:
- A/B/C/D/H.

### ANY_VISIBLE_GATED
Active accepted signal among:
- all ten signals.

For each union report:
- events;
- HIGH hits;
- MEDIUM hits;
- false calls;
- HIGH recall;
- elevated recall;
- false-call rate;
- useful-call rate.

Compare with the original ungated frozen union in the same period.

## 11. DEV candidate gate for M2

M2 becomes a candidate for a later operational validation only if DEV chronology-safe OOF satisfies all:

1. Brier improvement vs M0 >= **5%**;
2. Brier improvement vs M1 >= **2%**;
3. ANY_VISIBLE_GATED retains at least **90% of original ANY_VISIBLE HIGH hits**;
4. ANY_VISIBLE_GATED reduces original ANY_VISIBLE false calls by at least **20%**.

If any fails:
- M2 is not promoted;
- do not tune shrinkage strengths or the 0.50 threshold on DEV/2025/2026.

Opened transport is reported after this decision and cannot rescue a failed DEV gate.

## 12. Additional diagnostics

Report:
- per-signal M0/M1/M2 event Brier where n permits;
- score distributions for STABLE vs TRANSITION;
- score distributions by R0/R1/R2;
- rows/signals suppressed by M2 at 0.50;
- whether suppressed rows were HIGH/MEDIUM/NORMAL.

Cells/events with n<3 remain SMALL_N diagnostics.

## 13. Governance

Forbidden:
- changing raw alarm definitions;
- retuning V2;
- changing R0/R1/R2;
- changing pseudo-count strengths after seeing results;
- changing 0.50 threshold after seeing results;
- selecting from 2025/2026;
- forecast correction;
- model routing.

This is a frozen reliability-model experiment only.
