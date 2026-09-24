# GOLD CONTROL — Strict Daily MIDAS Pilot V3 Checkpoint

**Date:** 2026-09-25  
**Status:** RESEARCH_ONLY / NO PROMOTION  
**Canonical/runtime:** untouched

## Why V3 is the decision-quality pilot

V3 repairs the principal audit issues found in the earlier Daily MIDAS pilots:

- weekday business-source series is built before target pairing;
- source returns are computed before target-pair filtering;
- an origin is scored only when the next source business session is 1–4 calendar days away;
- target is never recomputed after row filtering;
- all ablations use the same equal-support panel and training history within each clock;
- cross-source daily data are lagged strictly before the origin date;
- GPR uses row-level `available_as_of`;
- PROXY uses a conservative prior-UTC-day GPR cutoff;
- NY17 research clock uses 17:00 America/New_York with DST;
- 2025 and 2026 are not used for tuning or feature/model-family selection.

Clean equal-support panels:

- PROXY: 1,041 rows, 2022-03-02..2026-07-30, zero gap>4 after final pair construction.
- NY17_RESEARCH: 1,007 rows, 2022-05-24..2026-08-28, zero gap>4 after final pair construction.

Weekend source rows removed before pairing:

- STAKTRAKR Gold: 44.
- NY17 hourly-derived: 81.

## Direction — strict V3

### Best pre-2025 pocket

The strongest strict pre-2025 UP result among the predeclared variants was:

**NY17_RESEARCH / GOLD_PLUS_METALS / HGB**

- n = 321
- UP recall = 52.94%
- false-UP FPR = 39.07%
- precision = 60.40%
- balanced accuracy = 56.93%
- ROC-AUC = 0.5672
- Youden J = +0.1387

Transport:

**2025**
- recall = 43.15%
- FPR = 40.95%
- BA = 51.10%
- AUC = 0.5001

**2026**
- recall = 47.19%
- FPR = 46.34%
- BA = 50.42%
- AUC = 0.5062

Interpretation: a real pre-2025 pocket exists, but it does not transport.

### Does slow MIDAS information add value?

Strict NY17_RESEARCH / FULL_MIXED_FREQ_MIDAS / HGB:

**Pre-2025**
- recall = 54.71%
- FPR = 45.70%
- BA = 54.51%
- AUC = 0.5720

**2025**
- BA = 47.56%
- AUC = 0.4835

**2026**
- BA = 47.28%
- AUC = 0.4760

The full mixed-frequency block does not beat the simpler Gold+metals block on pre-2025 class separation and transports worse. Current GPR slow block is therefore **NOT_PROVEN additive** for daily direction.

Strict L2 ablations reach the same high-level conclusion: no stable pre-2025 directional advantage from the slow MIDAS block or the full mixed-frequency block.

## Material-DOWN risk — strict V3

The most interesting pre-2025 PROXY results were:

### FULL_MIXED_FREQ_MIDAS / L2
Pre-2025:
- n = 158
- AUC = 0.6379
- recall at fixed 0.5 = 8.0%
- FPR = 0.75%
- precision = 66.67%
- BA = 53.62%

Transport:
- 2025 AUC = 0.5470, precision = 14.29%, BA = 48.96%
- 2026 AUC = 0.5039, precision = 23.08%, BA = 49.57%

### GOLD_METALS_CROSS / L2
Pre-2025:
- AUC = 0.6000
- recall = 16.0%
- FPR = 4.51%
- precision = 40.0%
- BA = 55.74%

Transport:
- 2025 BA = 48.61%, AUC = 0.5391
- 2026 BA = 48.83%, AUC = 0.4606

Thus the pre-2025 material-DOWN pocket also fails transport.

NY17_RESEARCH / GOLD_PLUS_METALS / L1 has pre-2025 AUC 0.6605, but n=60 and it emits zero positive calls at the fixed 0.5 threshold; its 2025 AUC falls to 0.4698. It is a small ranking pocket, not a validated DOWN detector.

## Main conclusion

### Daily general UP direction
No transportable high-recall / low-false-UP model was established.

The best corrected pre-2025 pocket is HGB with Gold + other daily metals, not a slow-MIDAS-driven winner.

### Daily material-DOWN
There are pre-2025 ranking pockets, especially in metal/cross/mixed blocks, but they do not survive locked 2025 transport.

### MIDAS incremental value
Under the currently verified information set:

**SLOW MIDAS / GPR incremental value = NOT_PROVEN.**

The current slow block does not create a stable advantage over simpler daily Gold / metals / cross-market information.

## What the result does NOT prove

This does not reject mixed-frequency modeling as a family.

The present slow block is narrow. The most scientifically justified missing daily information classes remain:

- broad USD / DXY-like daily index with proper clock/PIT identity;
- US 2Y / 10Y yields;
- real yield / TIPS;
- VIX/GVZ with sufficient pre-2025 history;
- oil;
- futures/options/positioning if clock/PIT can be reconstructed.

A new MIDAS experiment is justified only after one or more genuinely new daily information blocks are added with source/clock/PIT proof. Re-running more selectors on the same current information set is not justified.

## Frozen artifacts

Strict L2 pilot workflow:
- run: 36066845555
- artifact: 10837246152
- digest: sha256:47ece992609418486de7e3109398ca102dfcffa6ecf580c624b3ba508880e604

Strict predeclared L2/L1/HGB variant workflow:
- run: 36067291814
- artifact: 10837535001
- digest: sha256:440b7a66c2f25c99da6c65b2304c21919928768065c0812596b3a8c17958501d

## Governance

- random split: NO
- 2025 tuning: NO
- 2026 tuning: NO
- DB writes: NONE
- authority invariants changed: NO
- canonical branch modified: NO
- runtime promotion: NONE
