# HS-SDL-DMA retrospective pseudo-real-time validation report V1

## Governance result

`HS_SDL_DMA_DIRECTION_FUSION_V1` is implemented and deterministically replayed,
but neither horizon satisfies the frozen promotion rule. The evidence label is
`RETROSPECTIVE_PSEUDO_REAL_TIME_VALIDATED`; model/dashboard status remains
`NOT_PROVEN`. This is not prospective evidence.

No production database write, forecast authority, decision authority, selector,
ensemble, action or position mapping was created.

## Inventory and target clock

The frozen source panel has 400 unique chronological completed NY17 origins
(2025-01-03..2026-08-30). It yields 399 matured next-eligible-NY17 1D targets and
397 matured third-subsequent-eligible-NY17 3D targets. The evaluated/calibrated
outer samples are 279 and 273 respectively. Provider-no-bar dates are skipped,
not interpolated. Weekend/holiday arithmetic is never used.

FAST, SLOW and MONTHLY_DIRECTION_3M use fixed categorical one-hot contrasts.
No numeric vote mapping was invented. BOCPD, GVZ and Macro Event lack a proven
daily origin-as-of join in this panel; Emergency labels remain context-only.
They are excluded from the initial three-candidate direction core rather than
imputed or converted into votes.

## Frozen candidate and inner rules

The nested candidates are M1 FAST, M2 FAST+SLOW, and M3
FAST+SLOW+MONTHLY_DIRECTION. The pre-frozen grid contains ridge lambda
`{0.25,1,4}`, state discount `{1,0.99,0.97}`, and DMA alpha
`{1,0.99,0.95}`. Hyperparameter choice uses only matured earlier-origin raw
Brier evidence. Calibration is expanding prior-only Platt-logit with at least 60
matured inner-OOS predictions. A 3D outcome is unavailable until the third
subsequent eligible NY17 row. Direction thresholds were preregistered at
`p_cal >= 0.60` UP, `<=0.40` DOWN, otherwise UNCERTAIN.

## Results

| Horizon/model | N | Brier | Log loss | Accuracy | Balanced accuracy |
|---|---:|---:|---:|---:|---:|
| 1D HS-SDL-DMA | 279 | 0.254468 | 0.702351 | 0.5090 | 0.5098 |
| 1D P=0.50 | 279 | 0.250000 | 0.693147 | 0.4982 | 0.5000 |
| 1D expanding UP frequency | 279 | 0.252822 | 0.698854 | 0.4982 | 0.5000 |
| 1D FAST_ONLY | 279 | 0.254559 | 0.702423 | 0.4839 | 0.4856 |
| 1D static logistic | 279 | 0.256414 | 0.706281 | 0.5090 | 0.5101 |
| 1D equal candidates | 279 | 0.255539 | 0.704912 | 0.5269 | 0.5274 |
| 3D HS-SDL-DMA | 273 | 0.255404 | 0.710473 | 0.5678 | 0.5000 |
| 3D P=0.50 | 273 | 0.250000 | 0.693147 | 0.5678 | 0.5000 |
| 3D expanding UP frequency | 273 | 0.248583 | 0.690648 | 0.5678 | 0.5000 |
| 3D FAST_ONLY | 273 | 0.255212 | 0.705579 | 0.5678 | 0.5000 |
| 3D static logistic | 273 | 0.256980 | 0.709169 | 0.5641 | 0.5130 |
| 3D equal candidates | 273 | 0.259749 | 0.715826 | 0.5531 | 0.5104 |

1D calibration diagnostic: intercept `-0.0292`, slope `0.1147`. 3D:
intercept `0.3703`, slope `-0.1635`. Both slopes fail the preregistered
`[0.5,1.5]` gate; the 3D intercept also fails `|intercept|<=0.25`.

1D first/second-half Brier is `0.244051 / 0.264811`, with 94.27% abstention.
3D is `0.230981 / 0.279649`, with 22.34% abstention. The deterioration in the
second half is material stability evidence against promotion. Worst Brier origins
are 2025-10-16 (1D) and 2025-10-20 (3D).

## Inference and challenger review

Paired circular block bootstrap uses block length 2 for 1D and 4 for overlapping
3D, 2,000 deterministic replications, seed 20260910. It does not establish a
unique superior model: every mandatory model remains in the 5% MCS-style set.
The point-estimate leaders are P=0.50 for 1D and expanding UP-frequency for 3D.

This is explicitly `MCS_STYLE_PAIRED_CIRCULAR_BLOCK_BOOTSTRAP`; a formal Hansen
MCS and SPA implementation is `NOT_PROVEN/NOT_RUN`. No claim of formal MCS/SPA
significance is made. Optional architecture challengers are not run because the
core failed its simpler mandatory baselines and adding a post-result search would
violate the frozen sequence.

## Final gates

* Target/session and matured-outcome logic: PASS.
* Determinism: PASS for both horizons.
* Prefix/origin locality: PASS.
* Future-information violations: 0.
* Calibration isolation violations: 0.
* Mandatory baselines: PASS/present.
* 1D promotion: NOT_PROVEN.
* 3D promotion: NOT_PROVEN.
* TODAY_TO_NY17: BLOCKED_CONTRACT.
* Dashboard P_UP/direction: NOT_PROVEN; must display “Olasılık henüz kalibre
  edilmedi”.
* Genuine prospective shadow issuance: BLOCKED_PROMOTION_NOT_PROVEN.
* Production readiness/authority: CLOSED.
