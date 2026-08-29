# GOLD H1 R1 — 2023 Full-System Effectiveness Audit

## Contract
2023 is evaluation/diagnostic only. No 2023 actual is used to choose a threshold, flip rule, model weight, or emergency trigger. Existing pre-2023/frozen roles are preserved.

## Price-level forecast comparison
Computed from archived 2023 origin-safe forecasts in `autopsy_2023_direction.csv`.

| Model | 2023 MAPE |
|---|---:|
| VW | 1.9602% |
| Patch | 2.1280% |
| IDMA | 2.1824% |
| 3M Momentum level | 2.3013% |

VW is the best of these archived 2023 price-level forecasts.

## Direction baseline
3M strict reported accuracy: 7/12 = 58.33%.
October is exactly flat (1916 -> 1916), so economically directional months are 11. On those 11 months 3M is 7/11 = 63.64%.
Meaningful misses: February, May, June, November.

## Layered-system audit
- Tactical Slow: useful as CONFIRM/CONFLICT, but automatic conflict flipping is rejected because March, July and August are counterexamples where 3M was correct despite conflict.
- BOCPD-return: no 2023 alarm in the frozen validation record; it is risk context, not a direction vote.
- Emergency Shock Override: no 2023 trigger. It therefore corrects 0 and damages 0 in 2023; its role is severe intramonth fracture detection, not general reversal detection.
- Existing pre-2023 reversal discriminator families failed to improve 2023 generalization and remain rejected/not proven.

## What the current conservative system would do in 2023
Because Tactical/BOCPD are not approved automatic flips and Emergency does not trigger, the approved/conservative start-of-month direction remains the 3M prior. Therefore direction accuracy is not honestly improved above the 3M baseline by the currently approved layers in 2023.

The system is nevertheless better diagnostically: it distinguishes CONFIRM/CONFLICT and identifies June and November as strong reversal-disagreement cases without pretending that every conflict should be flipped.

## Decision
- PRICE LEVEL: IMPROVED — VW 1.9602% MAPE is best among the archived 2023 models listed above.
- DIRECTION: NOT YET IMPROVED IN HONEST 2023 REPLAY — 3M remains 7/12 strict, 7/11 excluding exact-flat October.
- RISK/DIAGNOSTICS: IMPROVED ROLE SEPARATION, but no proven 2023 directional gain.
- CLAIM THAT FULL SYSTEM BEATS OLD DIRECTION MODEL IN 2023: NOT PROVEN.

This is preferable to hindsight-flipping the 2023 misses: doing so would overfit the test year.