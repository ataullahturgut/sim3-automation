# GOLD D1 CIG — AUGUST 2026 FAILURE / COVERAGE ANALYSIS

**Date:** 2026-10-05  
**Identity:** `GOLD_D1_CIG_AUGUST_2026_FAILURE_ANALYSIS_V1`  
**Evidence class:** retrospective diagnostic; August 2026 outcomes are consumed evidence and may not be used as prospective validation.

## Executive diagnosis

August 2026 is not primarily an accuracy-collapse month for the selective CIG signal. It is a **coverage / expert-coherence collapse**.

Refreshed D1 replay:
- D1 days: **21**
- 4/4 CIG actions: **10**
- correct CIG actions: **8**
- selective accuracy: **80.00%**
- coverage: **47.62%**
- UNCERTAIN: **11/21**
- SAGE+RuleFlow forced accuracy: **14/21 = 66.67%**
- V5 forced accuracy: **14/21 = 66.67%**
- RIFT forced accuracy: **13/21 = 61.90%**
- VEGA forced accuracy: **14/21 = 66.67%**

Thus the operational problem is that the system abstains on more than half the month.

## Opportunity-cost view

Total absolute D1 movement in August: **21.73 percentage points** (sum of absolute log returns).

- movement on CIG action days: **13.36 pp**
- movement on UNCERTAIN days: **8.37 pp**
- movement captured by the action set: **61.48%**

For comparison:
- July movement capture: **86.14%**
- September movement capture through Sep 25: **86.53%**

August therefore loses a materially larger share of tradable daily movement to the UNCERTAIN state.

The two wrong 4/4 consensus actions in August are consecutive:
- 2026-08-18: CIG UP, actual DOWN
- 2026-08-19: CIG DOWN, actual UP

This is a short whipsaw cluster inside an otherwise strong selective month.

## Main structural finding — OPAL activation regime

August is the most OPAL-active month in the 2023–2026 clean V5 history:

| Month | OPAL-active origins | Total | Share |
|---|---:|---:|---:|
| 2026-07 | 1 | 23 | 4.35% |
| **2026-08** | **12** | **21** | **57.14%** |
| 2026-09 | 7 | 19 | 36.84% |

The next-highest monthly count in the 2023–2026 history is 8 origins (2023-09). August 2026 is therefore a genuine derivatives/reversal-state concentration.

Inside August:
- OPAL active: **12 days**
- OPAL-active days that become CIG UNCERTAIN: **11/12**
- non-OPAL days: **9**
- non-OPAL days with 4/4 consensus: **9/9**

Even more specifically:
- on **10/12** OPAL-active days, RIFT and VEGA agree with each other **against V5**
- in September this same pattern occurs only **2/7** OPAL-active days.

This explains why August coverage collapses much more sharply than September despite both months having elevated OPAL activity.

## Two-camp anatomy

The dominant August conflict is not random four-way noise. It is a stable two-camp split:

**Continuation / parent camp**
- SAGE+RuleFlow
- HELIOS V5-DCE

versus

**Reversal camp**
- RIFT
- VEGA

Among the 11 August UNCERTAIN days:
- V5/SAGE side is correct on **6**
- RIFT side is correct on **5**
- VEGA side is correct on **6**

Therefore there is no defensible static winner. Replacing CIG abstention with "always trust V5" or "always trust reversal" would reduce the uncertainty problem to approximately chance.

## OPAL calibration stress

OPAL's direct August changed-call chronology contains **11** reversal actions:
- rescued: **6**
- broken: **5**
- realized success: **54.55%**

Mean stated reversal probability across those actions is approximately **78.0%**.

This is a large calibration gap: high model confidence, but close-to-coin-flip realized reversal success in this specific month.

This does not prove OPAL is invalid globally. It shows that its reversal probability is not a reliable daily authority during the August 2026 transition state.

## Why OPAL suddenly activated

The underlying CFTC options-only managed-money state rotates very rapidly.

Selected official COT state:

| Report | Available | opt_mm_net | opt_mm_z52 | spec_hedger_gap |
|---|---|---:|---:|---:|
| 2026-07-21 | 2026-07-28 | -0.00238 | -1.13 | -0.00596 |
| 2026-08-04 | 2026-08-11 | +0.00334 | +0.36 | -0.00168 |
| 2026-08-11 | 2026-08-18 | +0.00745 | +1.60 | +0.00358 |
| 2026-08-18 | 2026-08-25 | +0.00761 | +1.68 | +0.00421 |
| 2026-08-25 | 2026-09-01 | +0.01018 | +2.40 | +0.00654 |

The managed-money options-only state moves from a negative / below-normal condition to a strongly positive and increasingly extreme condition within roughly one month.

The problem is temporal:
- COT is weekly;
- OPAL uses a conservative +7 calendar-day availability lag;
- one COT state therefore persists across several daily/H3 origins;
- August market dynamics change faster than the weekly positioning state.

This creates a **slow-state / fast-market conflict**: a persistent derivatives reversal warning is applied while the daily price and macro regime repeatedly changes.

## Not primarily an H3-to-D1 horizon problem

August D1 and H3 realized directions agree on:
- **17/21 = 80.95%**

V5's native H3 accuracy in August is:
- **16/21 = 76.19%**

Therefore the August CIG coverage collapse cannot be explained mainly by repurposing H3 expert states for D1. The H3 and D1 directions are unusually aligned in August.

## Not a raw-price data-integrity failure

The clean August calendar contains all 21 D1 observations used in the replay.

The upstream StakTrakr cross-source integrity audit did not flag an August 2026 XAU anomaly; the 2026 severe flags were elsewhere in the year.

Thus the August behavior should be treated as model/regime behavior, not a missing-price or corrupted-price artifact.

## Transition character

The existing competence-transition drift panel does not show an acute broad-system shock in August:
- no August `FISHER99` event
- no `BROAD2` / `STRICT2` regime trigger.

This suggests a **slow structural rotation with repeated local reversals**, rather than one single discontinuous shock. That is exactly the environment in which a weekly state can remain directionally stale while intraday/daily signals change.

## Rejected simple explanation

A post-analysis observation suggested CROSS_MACRO score might separate which camp is correct.

To avoid tuning on August, a threshold was selected using only Jan–Jul 2026 disagreement days and then applied to August.

Result:
- August test accuracy: **50%**

Therefore a single macro-score threshold is rejected as an explanation/resolver.

## Architecture implication

The CIG's four votes are not four fully independent models:
- SAGE+RuleFlow is primarily an exception layer around V5;
- V5 is an AURORA descendant and incorporates reversal sublayers;
- RIFT and VEGA are also AURORA-derived reversal heads.

August exposes this genealogy. When the reversal regime activates, the stack bifurcates into two correlated camps rather than four independent opinions.

Hence raw vote count overstates information diversity.

## Scientific conclusion

August 2026 should be classified as:

**DERIVATIVES-POSITIONING TRANSITION + EXPERT-COHERENCE FAILURE**

not:
- a raw data failure;
- a simple D1/H3 mismatch;
- a month where the selective consensus signal itself had poor hit rate.

The primary failure is **coverage and regime validity**.

## Recommended next research lane

Do not tune CIG on August outcomes.

Build a separately named **Consensus Validity / Transition Gate** whose purpose is not to predict UP/DOWN directly, but to determine whether the current expert agreement/disagreement state is trustworthy.

Candidate origin-safe inputs:
1. OPAL activation density over the last 5/10 origins;
2. COT report age and week-to-week state velocity;
3. `opt_mm_z52` sign crossing and change;
4. spec-hedger / spec-swap gap changes;
5. expert split topology (V5/SAGE versus RIFT/VEGA);
6. Rates / USD / VIX / Nasdaq / Brent / WTI daily state;
7. event proximity / economic-surprise state;
8. intraday trend strength, adverse excursion, session-against-trend and deceleration.

Development must use pre-August / earlier historical analogues. August 2026 remains consumed diagnostic evidence and cannot be used as clean validation.
