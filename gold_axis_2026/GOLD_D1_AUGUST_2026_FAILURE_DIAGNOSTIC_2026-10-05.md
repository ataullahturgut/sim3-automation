# GOLD D1 — AUGUST 2026 FAILURE / COVERAGE DIAGNOSTIC

**Date:** 2026-10-05  
**Status:** RETROSPECTIVE MECHANISM DIAGNOSTIC — NOT MODEL SELECTION EVIDENCE  
**Scope:** CIG-D1 August 2026, refreshed 21-day universe.

## Executive finding

August is not primarily a low-precision month for CIG-D1. It is a **coverage-collapse / lineage-conflict month**.

- D1 days: **21**
- 4/4 consensus actions: **10**
- correct consensus actions: **8**
- selective accuracy: **80.00%**
- coverage: **47.62%**
- UNCERTAIN: **11**

The root cause of the 11 UNCERTAIN days is highly concentrated:

- OPAL override active on **12/21 = 57.14%** of August origins.
- The OPAL/V5 chain changes the final V5 direction relative to AURORA on **11/21 = 52.38%**.
- Those **11 final V5 direction changes are exactly the 11 CIG UNCERTAIN days**.
- SAGE+RuleFlow equals V5 on **21/21** August days.
- RIFT equals VEGA on **20/21** August days.
- Therefore most August disagreement is not four independent experts disagreeing randomly. It is predominantly a **two-lineage collision**:
  - V5 / SAGE lineage
  - RIFT / VEGA / AURORA lineage
- **10 of the 11** UNCERTAIN days are effectively 2-vs-2 splits.

## Lineage agreement collapse

| Month | SAGE=V5 | RIFT=VEGA | V5=RIFT | V5=VEGA | 4/4 coverage |
|---|---:|---:|---:|---:|---:|
| 2026-07 | 91.30% | 100.00% | 95.65% | 95.65% | 86.96% |
| **2026-08** | **100.00%** | **95.24%** | **47.62%** | **52.38%** | **47.62%** |
| 2026-09 | 100.00% | 94.74% | 84.21% | 89.47% | 84.21% |

Thus August coverage collapse is mathematically explained by the sudden loss of agreement between the V5 lineage and the RIFT/VEGA lineage.

## OPAL regime change

OPAL is an H3 reversal layer using lag-safe CFTC options/futures positioning plus trend interaction features.

Monthly OPAL diagnostics:

| Month | OPAL override rate | Final V5-vs-AURORA flip rate | Mean P(reversal) | Median P(reversal) |
|---|---:|---:|---:|---:|
| 2026-07 | 4.35% | 4.35% | 59.62% | 58.55% |
| **2026-08** | **57.14%** | **52.38%** | **69.10%** | **73.19%** |
| 2026-09 | 36.84% | 15.79% | 69.17% | 69.63% |

The frozen OPAL reversal threshold is 0.70. August therefore moves from a low-override July regime into a persistent threshold-crossing regime.

## Positioning state behind the override burst

The CFTC options positioning state changes sharply during the period.

| COT report | Options MM net | MM z52 | Swap z52 | Spec-vs-swap gap |
|---|---:|---:|---:|---:|
| 2026-07-21 | -0.00238 | -1.13 | +0.08 | -0.01201 |
| 2026-07-28 | +0.00108 | -0.28 | +0.11 | -0.00896 |
| 2026-08-04 | +0.00334 | +0.36 | -0.23 | -0.00422 |
| 2026-08-11 | +0.00745 | +1.60 | -1.33 | +0.00821 |
| 2026-08-18 | +0.00761 | +1.68 | -1.31 | +0.00826 |
| 2026-08-25 | +0.01018 | +2.40 | -1.62 | +0.01348 |

This is a genuine positioning polarity transition:
- options money-manager net exposure moves from negative to strongly positive;
- money-manager 52-week z-score moves from **-1.13 to +2.40**;
- swap z-score moves from roughly neutral to **-1.62**;
- spec-vs-swap gap changes sign and widens sharply.

This is consistent with a **crowding / reversal-risk state**. Because CFTC state is weekly and conservatively lagged by seven calendar days, one high-reversal positioning state persists over several consecutive D1 origins. That persistence creates clusters of V5 flips rather than isolated flips.

## Critical horizon result

OPAL was designed for the native **H3** target, not next-day D1.

In August H3:
- OPAL overrides: **12**
- H3 rescues: **7**
- H3 broken: **5**
- net rescue: **+2**

Therefore OPAL is not simply a failed August model on its intended horizon.

The D1 problem arises when an H3 reversal override is treated as a D1 directional vote. The reversal may be correct over the H3 window while being early or wrong for the next session.

This is directly visible on the 2026-08-18 D1 issue:
- D1 consensus: UP
- next-day realized D1: DOWN, approximately **-0.51%**
- native H3 target from the same origin: UP, approximately **+2.18%**
- thus the H3 direction is correct while the D1 sign is wrong.

This is a clean **temporal phase / horizon-mismatch** example.

## The genuine August model miss

The 2026-08-19 issue is different:
- consensus: DOWN
- realized D1: UP, approximately **+0.84%**
- native H3 target: UP, approximately **+4.41%**
- therefore this is a real directional miss, not merely a D1/H3 phase mismatch.

External market context identifies a major same-day discontinuity: on 2026-08-19 the U.S. Treasury unexpectedly doubled liquidity-support buybacks for long-dated Treasury securities. Yields and the dollar fell sharply and gold surged more than 3%. This information did not exist at the 2026-08-18 feature cutoff. It is therefore an exogenous post-origin policy shock, not a leakage-correct model input that the prior-day system could have known.

## Why simply disabling OPAL is wrong

Post-hoc August counterfactual:
- replace the V5 OPAL-driven direction flip with base AURORA direction;
- keep RIFT and VEGA unchanged.

Result:
- coverage rises from **47.62% to 95.24%**
- but selective accuracy falls from **80.00% to 65.00%**.

Therefore the existing CIG abstention is doing useful risk control. The correct conclusion is **not** “remove OPAL.”

## Cross-month evidence

Across 2025-01 through 2026-09 monthly panels:
- correlation between OPAL override rate and UNCERTAIN rate: **r = +0.57**
- correlation between final V5-vs-AURORA flip rate and UNCERTAIN rate: **r = +0.75**
- August 2026 ranks **#1** in both OPAL override rate and UNCERTAIN rate.

This supports a structural, not anecdotal, explanation.

## Existing rescue layers

DPTC / TCG do not explain or repair this August failure:
- DPTC has **no August 2026 actions** in its frozen action chronology.
- TCG gates DPTC competence and therefore also provides no August rescue action.

This is a different failure class from the DPTC competence-transition problem.

## Scientific diagnosis

August contains three interacting phenomena:

1. **Positioning-regime inversion / crowding**
   - CFTC options positioning moves rapidly into an extreme money-manager-long / swap-short state.
   - OPAL correctly interprets this as elevated H3 reversal probability.

2. **H3-to-D1 horizon mismatch**
   - H3 reversal timing is not guaranteed to occur on the next session.
   - Using the H3 override as a D1 vote causes systematic V5-vs-RIFT/VEGA conflict.

3. **Fast policy-event regime changes**
   - August includes inflation/Fed uncertainty, Treasury-market stress, the unexpected 19-Aug Treasury liquidity-support announcement, late-month Jackson Hole repricing and rapid dollar/yield changes.
   - weekly positioning state can remain valid for H3 while daily path direction changes much faster.

## Recommended research lane — not yet promoted

Do not retune OPAL's 0.70 H3 threshold using August outcomes.

Open a separate D1 challenger:

**Temporal Concordance Gate (TCG-D1 / Horizon Alignment Gate)**

Purpose:
- keep OPAL as an H3 expert;
- when V5 direction differs from AURORA specifically because of OPAL / H3 reversal logic, do not automatically treat the flip as an immediate D1 vote;
- require independent fast evidence (H1 path, overnight move, rates/FX reaction, event proximity/reaction, intraday deceleration) before promoting the H3 reversal to a D1 directional vote;
- otherwise keep the existing CIG state as UNCERTAIN.

This targets the demonstrated August failure mechanism without destroying the useful 80% accuracy of the current selective consensus.

## Authority inputs

- `GOLD_D1_CIG_V1_EXTENDED_JAN_SEP_REPLAY_2026-10-05.csv`
- `GOLD_H3_CLEAN_AURORA_PREDICTIONS_2026-10-03.csv`
- `GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv`
- `GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv`
- `GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv`
- `GOLD_H3_CLEAN_OPAL_PREDICTIONS_2026-10-03.csv`
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_OPAL_PANEL.csv`
- `GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv`
- `GOLD_H3_DPTC_V1_RESULT_2026-10-05.md`
- `GOLD_H3_TOPOLOGY_COMPETENCE_GATE_V1_2026-10-05.md`
