# GOLD MONTHLY — Anchored vs Expanding Regime Detector Comparison V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Binding decision:** NO OPERATIONAL WINNER YET — do not move to regime-conditioned alarm weighting.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_MARKET_REGIME_ANCHORED_COMPARISON_V1_AUTHORITY_2026-09-30.md`
- initial authority commit: `787617afd06c787e06f19f3371dbbc83ce0c624b`
- technical warm-up amendment: `6dddee2b5e9271c0f6e7df3281d2996e394250b6`

Code:
- `gold_axis_2026/tools/gold_monthly_market_regime_anchored_comparison_v1.py`
- successful code commit: `ad16b6dc1793b5acbae4e3dc8149c190837c7030`

Workflow:
- `.github/workflows/gold-monthly-market-regime-anchored-comparison-v1.yml`
- workflow commit: `64d27a35c6a66d235d7e4252adade62e5d5c6fa3`

Successful execution:
- workflow: **Gold Monthly Market Regime Anchored Comparison V1**
- run: **36731019903**
- artifact: **11104223104**
- artifact digest: `sha256:27fab3a8eecdc258c6278e9cd15097df33d6f52cb2d9372943442d1d729bba16`
- scientific gate: **PASS**

Preceding failed attempt:
- run: **36730775765**
- reason: first annual anchor (2014-12) had only 54 complete months, below the pre-existing 60-month minimum-history gate.
- no comparison result was produced before failure.
- technical fix: the first partial replay block, 2015-07..2015-12, is anchored at 2015-06, giving 60 prior months. From 2016 onward normal prior-December annual anchors are used.

## 2. Systems

**EXPANDING-REFIT**
- re-fits scaler/PCA/HMM every month using data through t-1.

**ANNUAL-ANCHORED**
- fits once at the prior December and keeps parameters fixed through the calendar year;
- 2015 partial-year warm-up exception described above.

**STRICT-2024-ANCHOR**
- sensitivity only for 2025-01..2026-08;
- fit once through 2024-12 and never re-fit during the 20-month period.

All systems:
- K=3;
- 13 market-state features only;
- no forecast errors;
- no alarm flags;
- no HIGH/MEDIUM/NORMAL labels;
- no model forecasts or router outputs.

The expanding implementation exactly reproduced Walk-Forward V1 across all 134 months.

## 3. Primary non-circular metric — one-step predictive log score

Higher is better.

### Core recent period: 2022-01..2026-08

- EXPANDING mean: **-9.97372**
- ANNUAL-ANCHORED mean: **-9.96133**
- anchored minus expanding: **+0.01239 per month**
- anchored better: **24/56 months**
- expanding better: **28/56 months**
- 4 ties
- median paired difference: approximately **0**

Interpretation:
The annual anchor has a tiny mean advantage, but not a broad month-by-month dominance. The evidence does not support a strong predictive-density win.

### Full replay: 2015-07..2026-08

- EXPANDING mean: **-9.62542**
- ANNUAL-ANCHORED mean: **-9.71664**
- anchored minus expanding: **-0.09122 per month**
- anchored better: 59/134
- expanding better: 67/134

Interpretation:
Across the long replay, expanding-refit has the better predictive density.

### 2025-01..2026-08 inspected transport

- EXPANDING mean: **-10.02083**
- ANNUAL-ANCHORED mean: **-9.92912**
- annual anchored minus expanding: **+0.09171**
- STRICT-2024-ANCHOR mean: **-10.13531**
- strict-2024 anchor minus expanding: **-0.11448**
- strict anchor better than expanding in only **5/20** months.

Interpretation:
Annual anchoring improves average predictive density in this 20-month slice, while a completely stale 2024 anchor does not.

## 4. Secondary reference-label diagnostics

These are secondary because the reference labels are themselves HMM-derived latent labels.

### Core 2022-01..2026-08

EXPANDING:
- strict R-state accuracy: **68.6%**
- balanced accuracy: **61.2%**
- R0 recall **44.4%**
- R1 recall **47.1%**
- R2 recall **92.0%**

ANNUAL-ANCHORED:
- strict R-state accuracy: **68.6%**
- balanced accuracy: **53.6%**
- R0 recall **0.0%**
- R1 recall **64.7%**
- R2 recall **96.0%**

Important:
The annual anchor redistributes the errors rather than clearly solving them. It materially improves R1/R2 recall but collapses reference-R0 recall in this replay.

### 2025-01..2026-08

EXPANDING:
- strict R-state accuracy: **88.9%**
- represented-state balanced accuracy: **71.9%**

ANNUAL-ANCHORED:
- strict R-state accuracy: **94.4%**
- represented-state balanced accuracy: **75.0%**

STRICT-2024-ANCHOR:
- exact agreement with the Discovery reference is 100%, but this is structurally circular because that reference is generated from the same 2024-frozen model. It must not be treated as independent accuracy evidence.

## 5. Mandatory transition checkpoints

### 2024-04 R1 -> R2

2024-03:
- expanding: R1, p=98.1%
- annual anchored: R1, p=90.9%

2024-04:
- expanding: underlying R2 p=55.5% -> **BELIRSIZ**
- annual anchored: underlying R2 p=58.6% -> **BELIRSIZ**

2024-05:
- expanding: **R2 p=99.4%**
- annual anchored: **R2 p=96.7%**

Both systems therefore recognize the 2024 R2 onset with a **1-month delay** and correctly avoid a forced confident regime call in the transition month.

### 2026 transition

Reference descriptive path:
- 2026-04 R2
- 2026-05 BELIRSIZ
- 2026-06 BELIRSIZ
- 2026-07 R1
- 2026-08 R1

EXPANDING:
- 2026-04 R2 98.4%
- 2026-05 R2 70.9%
- 2026-06 R2 79.4%
- 2026-07 BELIRSIZ, underlying R1 50.8%
- 2026-08 R1 94.8%

ANNUAL-ANCHORED:
- 2026-04 R2 97.8%
- 2026-05 **BELIRSIZ**, underlying R2 50.8%
- 2026-06 **R0 82.4%**
- 2026-07 **R0 76.6%**
- 2026-08 R1 97.5%

STRICT-2024-ANCHOR sensitivity:
- 2026-04 R2 98.3%
- 2026-05 **BELIRSIZ**, underlying R1 52.7%
- 2026-06 **BELIRSIZ**, underlying R2 36.3%
- 2026-07 R1 70.1%
- 2026-08 R1 98.6%

Interpretation:
- annual anchoring catches the May loss of confidence earlier than expanding-refit;
- however it then produces confident R0 calls in June and July, while the strict historical anchor and Discovery reference describe the interval as ambiguity -> R1;
- therefore the annual anchor is **not** a clean solution.

## 6. Why the result is mixed

The comparison suggests two separate issues:

1. **parameter drift / adaptation speed** — monthly re-fitting can keep the detector too confidently in R2 during the early transition;
2. **state semantic alignment** — independently re-fitted HMMs are currently named R0/R1/R2 mainly by ordering their Gold_r1 state means. The annual-anchor R0 collapse in the core replay and the 2026 R0 calls indicate that label alignment itself may be unstable across refits.

This means we cannot yet tell whether 2026 June/July annual-anchor R0 is a genuine stress-state identification or a state-label/prototype alignment artifact.

## 7. Binding decision

**Do not freeze either expanding-refit or annual-anchored as the operational regime gate yet.**

- Expanding-refit remains too slow around the 2026 transition.
- Annual anchoring improves May-2026 uncertainty timing and recent predictive density, but introduces materially unstable R0 behavior.
- Strict 2024 freezing gives the desired transition chronology but has worse out-of-sample predictive density and its reference-label agreement is circular.

Therefore:
- no alarm selection;
- no alarm weighting;
- no alarm suppression;
- no forecast correction;
- no routing/model switching.

## 8. Next exact regime-only step

Before testing another HMM training schedule, fix the semantic state-alignment problem.

Next study:
**Prototype-Anchored State Alignment V1**

Use the frozen 2010-2024 R0/R1/R2 multivariate market-state profiles as semantic prototypes and align every newly fitted HMM's three latent states to those prototypes using all 13 state variables (one-to-one assignment), instead of naming states primarily by Gold_r1 ordering.

Then re-run:
- expanding-refit;
- annual-anchored;
- 2024 and 2026 transition checkpoints;
- predictive log score unchanged as the non-circular density metric;
- R0/R1/R2 stability and transition delay as descriptive diagnostics.

Only after that alignment audit can we decide whether the problem is truly HMM re-fitting or merely label switching/state-definition drift.
