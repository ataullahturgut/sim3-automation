# HS-SDL-DMA candidate and evaluation preregistration V1

Status: `FROZEN_BEFORE_OUTER_SCORING`

The initial core contains three nested direction-only candidates: FAST; FAST +
SLOW; FAST + SLOW + MONTHLY_DIRECTION_3M. Context-only components are not main
effects or votes. This is below the manifest maximum K=4.

The complete admissible inner grid, delayed 3D update rule, expanding prior-only
Platt calibration, deterministic tie-break, clipping epsilon and initialization
are frozen in `inner_rules_v1.json`. No outer result was consumed.

After observing only the feasible inventory counts (400 origins; 399/397 matured
targets), the symmetric 0.40/0.60 abstention band and promotion/rejection rules
were preregistered in `preregistration_v1.json`. These values may not be changed
after outer replay without a governance failure and new versioned review.

This checkpoint grants no dashboard or production authority.
