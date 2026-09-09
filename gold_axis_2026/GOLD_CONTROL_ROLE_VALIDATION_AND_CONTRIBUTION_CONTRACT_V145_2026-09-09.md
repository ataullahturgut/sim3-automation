# Gold Control V1.45 — Frozen Role Validation and Contribution Contract

Date: 2026-09-09  
State: `FROZEN_BEFORE_ROLE_METRICS_AND_CONTRIBUTION_RESULTS`  
Binding parent: `GOLD_CONTROL_HISTORICAL_PILOT_READINESS_CONTRACT_V145_2026-09-08.md`

## Governance boundary

This is evaluation-only. It changes no engine, feature, source, threshold, hazard,
hyperparameter, weight, selector, ensemble, forecast authority or position mapping.
`AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, and expert-to-position mapping remains
`NOT_PROVEN`. Historical reconstruction is never prospective evidence.

The pilot windows are fixed: 2025-01..2025-12 retrospective validation and
2026-01..2026-08 retrospective frozen OOS. A missing realized target remains
`BLOCKED_DATA`; it is never imputed. No random split is permitted.

## Frozen role measures

* H=1 experts: origin-safe MAE, MAPE, median AE/APE, RMSE, direction accuracy,
  monthly AE relative to the frozen RANDOM_WALK benchmark, and worst absolute
  error. The 2026-08 realized target must be exact or the cell is blocked.
* MONTHLY_DIRECTION_3M: target-month constant state, completed-prior-month
  timing, hit/miss/neutral counts against the exact NY17 month-end movement.
* FAST: chronological state changes, direct UP-to-DOWN/DOWN-to-UP false flips,
  persistence runs, next-observation directional agreement and timing.
* SLOW: chronological completed-week changes, persistence, lag relative to FAST,
  false regime changes and distinct-state share.
* MACRO_EVENT_SUCCESSOR_V2: frozen release chronology, frozen shock-state counts,
  event-reaction evidence if already preregistered; 2025-10 stays
  `CONTRACTUAL_EXCLUSION` and is not imputed.
* BOCPD_RETURN_SUCCESSOR_V1: frozen change-point probability/state chronology,
  break timing, candidate frequency and persistence. 2026-08 remains
  `BLOCKED_DATA` when exact CORE5 gold monthly data is absent.
* EMERGENCY_LEVEL: chronological threshold crossings, first crossing date,
  alert persistence and missed/false material-displacement counts under the
  already frozen engine threshold.
* EMERGENCY_REVERSAL: chronological alert onset, persistence, latency and
  missed/false reversal counts under the already frozen engine rule.
* GVZ_RISK: chronological cap/panic state counts, persistence and association
  with next matched adverse NY17 movement.

Role-validation labels are frozen as follows: component-verification BLOCKED or
FAIL propagates to `BLOCKED` or `FAIL`. A technically PASS H=1 engine with the
full available forecast vector and finite role diagnostics is `VALIDATED_CORE`.
A technically PASS context/risk engine with chronological role diagnostics is
`VALIDATED_COMPLEMENTARY`. Missing required role evidence is `NOT_PROVEN`; no
performance threshold is a technical PASS gate.

## Frozen contribution measures and labels

H=1 experts are compared only inside the H=1 layer. Report residual correlation,
direction agreement/disagreement with RANDOM_WALK, monthly win rate, and summed
`AE_RANDOM_WALK - AE_ENGINE`. RANDOM_WALK is the mandatory benchmark, not a
candidate selected by score.

Context/risk engines are compared by frozen numeric state encodings only to
describe overlap, agreement, disagreement, conditional movement and lead/lag.
They are not ranked against H=1 price errors. Leave-one-component-out uses only
already frozen output rows and may not optimize weights.

Classification is descriptive and frozen: `UNIQUE_CONTRIBUTION_PROVEN` requires
positive H=1 aggregate error reduction plus win rate above 0.5, or a distinct
role-specific output with non-zero conditional separation and at least 20
chronological cells. A non-constant distinct output without that proof is
`COMPLEMENTARY`. Negative H=1 aggregate error reduction with win rate at or below
0.5 is `HARMFUL_EVIDENCE`. Missing/blocked inputs give `INSUFFICIENT_EVIDENCE`.
These labels cannot alter the frozen engines during this pilot.

## Architecture carry-forward

Architecture review must combine technical validity, role evidence, stability,
incremental contribution, reproducibility, data dependence, failure severity,
interpretability and governance burden. One performance result alone cannot
remove an engine. No selector, ensemble, optimized weight or production decision
authority may be created.
