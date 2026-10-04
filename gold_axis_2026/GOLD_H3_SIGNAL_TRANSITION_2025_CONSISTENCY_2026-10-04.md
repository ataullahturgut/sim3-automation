# 2025 SIGNAL-TRANSITION CONSISTENCY DIAGNOSTIC

**Status:** historical consistency check only; not independent validation.

- coverage: 2025-05-09 onward, N=165
- V5 missed reversals: 40
- correct continuations: 96

## Transition signs

| Feature | Miss mean | Control mean | SMD |
|---|---:|---:|---:|
| fragility_score_d1 | +0.087 | -0.027 | +0.324 |
| internal_d1 | +0.062 | -0.020 | +0.263 |
| fragility_score_d2 | +0.085 | -0.005 | +0.247 |
| leadlag_score_d1 | +0.082 | -0.013 | +0.202 |
| internal_d2 | +0.047 | +0.016 | +0.093 |
| flow_score_d1 | +0.024 | +0.004 | +0.063 |
| leadlag_score_d2 | +0.026 | -0.003 | +0.062 |
| handoff_gap | +0.395 | +0.398 | -0.006 |
| leadlag_premax_minus_now | +0.097 | +0.104 | -0.015 |
| flow_score_d2 | -0.016 | -0.006 | -0.032 |

## Sequence patterns

| Pattern | Miss coverage | Control prevalence | Lift |
|---|---:|---:|---:|
| LEADLAG_PRE_TO_INTERNAL_NOW_067 | 17.5% | 10.4% | 1.68x |
| EXTERNAL_PRE_TO_INTERNAL_NOW_067 | 27.5% | 25.0% | 1.10x |
| FLOW_PRE_TO_FRAGILITY_NOW_067 | 10.0% | 10.4% | 0.96x |
