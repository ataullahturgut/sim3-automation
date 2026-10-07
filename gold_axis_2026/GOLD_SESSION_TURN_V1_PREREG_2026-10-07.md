# SESSION TURN V1 — PREREGISTRATION / IDENTITY CONTRACT

**Date:** 2026-10-07
**Status:** BINDING BEFORE SESSION RUN

## Role

TURN is a fixed tail-unbalanced reversal specialist layered on fresh SESSION AURORA.

It is not a stand-alone primary direction engine.

## Frozen historical identity

Preserve from H3 TURN:

- semivariance horizon = latest 120 active completed hourly returns;
- historical reference window = previous 250 valid same-session anchors;
- minimum reference history = 120 prior valid same-session anchors;
- tail threshold = 80th percentile;
- no fitted classifier;
- no threshold search;
- both-tail state records uncertainty and does not force a direction.

## Session-native clock adaptation

For every governed session target start T:

1. use only canonical XAU hourly bars with `available_at_utc < T`;
2. the latest admissible completed hourly bar is the session anchor;
3. compute active-bar 12h momentum from the latest 12 completed hourly returns;
4. compute:
   - `RS_PLUS_120 = sum(r_h^2 * 1[r_h>0])`;
   - `RS_MINUS_120 = sum(r_h^2 * 1[r_h<0])`;
5. reference quantiles are calculated only from prior anchors of the **same partition/window**.

No current or overlapping session outcome is used.

2022 governed session starts may be used only as unlabeled tail-history warm-up.
2023–2024 are scored development.
2025 is frozen transport.
2026 is unopened.

## Upstream

Fresh SESSION AURORA must be recomputed from corrected session expert inputs.

Archived H3 AURORA/TURN predictions are prohibited as model input.

## Fixed TURN rule

AURORA remains the base probability.

TURN may act only if AURORA direction agrees with pre-target 12-active-hour momentum.

### Momentum UP

If:
- AURORA = UP;
- momentum > 0;
- RS_MINUS_120 > prior Q80_MINUS;
- RS_PLUS_120 <= prior Q80_PLUS;

then flip to DOWN.

### Momentum DOWN

If:
- AURORA = DOWN;
- momentum < 0;
- RS_PLUS_120 > prior Q80_PLUS;
- RS_MINUS_120 <= prior Q80_MINUS;

then flip to UP.

### Both-tail

If both tails exceed Q80:
- set BOTH_TAIL_RISK = 1;
- keep AURORA direction.

Otherwise keep AURORA.

## Probability handling

If TURN flips:
- `p_turn = 1 - p_aurora`.

Otherwise:
- `p_turn = p_aurora`.

## Role-aware development gate

TURN is a correction specialist. The 30% minimum-class-recall primary gate does not apply.

A session head may open 2025 only if, on 2023–2024 development:

1. at least one actual TURN override occurs;
2. net rescue > 0;
3. TURN combined Balanced Accuracy >= AURORA combined Balanced Accuracy;
4. TURN combined Brier <= AURORA combined Brier + 0.003;
5. neither 2023 nor 2024 accuracy is worse than AURORA by more than 1 pp when that year has scored observations.

No 2025 result may change:
- 120-hour semivariance horizon;
- 250-anchor reference window;
- minimum 120 reference anchors;
- 80th percentile;
- both-tail handling;
- probability flip rule;
- session membership.

## Reporting

Per session report:

- N
- Accuracy
- Balanced Accuracy
- UP recall
- DOWN recall
- Brier
- overrides
- rescued
- broken
- net rescue
- both-tail count
- 2025 transport only for development-eligible heads.
