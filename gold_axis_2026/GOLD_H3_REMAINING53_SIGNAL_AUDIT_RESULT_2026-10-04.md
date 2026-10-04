# GOLD H3 — Remaining-53 Signal Audit Result

**Status:** retrospective mechanism diagnostic; not a new model and not a promotion test.

- Remaining missed reversals: **53**
- Correct-continuation controls: **95**
- Reversal episodes: **22**
- Multi-origin episodes: **17**

## Mechanism coverage

| Mechanism | Threshold | Timing | Miss coverage | Control prevalence | Lift |
|---|---:|---|---:|---:|---:|
| fragility_score | 0.67 | current | 32.1% | 22.1% | 1.45x |
| fragility_score | 0.67 | pre | 35.8% | 43.2% | 0.83x |
| fragility_score | 0.67 | any | 56.6% | 60.0% | 0.94x |
| fragility_score | 0.75 | current | 18.9% | 10.5% | 1.79x |
| fragility_score | 0.75 | pre | 20.8% | 23.2% | 0.90x |
| fragility_score | 0.75 | any | 35.8% | 32.6% | 1.10x |
| flow_score | 0.67 | current | 26.4% | 18.9% | 1.39x |
| flow_score | 0.67 | pre | 37.7% | 33.7% | 1.12x |
| flow_score | 0.67 | any | 50.9% | 45.3% | 1.13x |
| flow_score | 0.75 | current | 18.9% | 9.5% | 1.99x |
| flow_score | 0.75 | pre | 18.9% | 24.2% | 0.78x |
| flow_score | 0.75 | any | 32.1% | 30.5% | 1.05x |
| leadlag_score | 0.67 | current | 28.3% | 30.5% | 0.93x |
| leadlag_score | 0.67 | pre | 52.8% | 42.1% | 1.25x |
| leadlag_score | 0.67 | any | 71.7% | 58.9% | 1.22x |
| leadlag_score | 0.75 | current | 20.8% | 22.1% | 0.94x |
| leadlag_score | 0.75 | pre | 35.8% | 31.6% | 1.14x |
| leadlag_score | 0.75 | any | 50.9% | 44.2% | 1.15x |
| reaction_score | 0.67 | current | 17.0% | 18.9% | 0.90x |
| reaction_score | 0.67 | pre | 26.4% | 31.6% | 0.84x |
| reaction_score | 0.67 | any | 37.7% | 46.3% | 0.81x |
| reaction_score | 0.75 | current | 11.3% | 14.7% | 0.77x |
| reaction_score | 0.75 | pre | 18.9% | 26.3% | 0.72x |
| reaction_score | 0.75 | any | 30.2% | 37.9% | 0.80x |

## Origin-to-origin transition diagnostics

| Transition | Miss mean | Control mean | SMD |
|---|---:|---:|---:|
| internal_d1 | +0.085 | -0.048 | +0.395 |
| internal_d2 | +0.063 | -0.055 | +0.365 |
| fragility_score_d1 | +0.081 | -0.045 | +0.341 |
| fragility_score_d2 | +0.065 | -0.041 | +0.307 |
| handoff_gap | +0.374 | +0.243 | +0.284 |
| flow_score_d1 | +0.056 | -0.037 | +0.281 |
| flow_score_d2 | +0.024 | -0.060 | +0.245 |
| leadlag_premax_minus_now | +0.190 | +0.119 | +0.125 |
| reaction_score_d1 | +0.025 | +0.013 | +0.049 |
| leadlag_score_d1 | -0.004 | -0.000 | -0.005 |
| reaction_score_d2 | -0.003 | +0.010 | -0.046 |
| leadlag_score_d2 | -0.113 | +0.005 | -0.205 |

## Exploratory temporal sequence patterns

| Pattern | Miss coverage | Control prevalence | Lift | Episode starts |
|---|---:|---:|---:|---:|
| LEADLAG_PRE_TO_INTERNAL_NOW_067 | 24.5% | 12.6% | 1.94x | 3/22 |
| EXTERNAL_PRE_TO_INTERNAL_NOW_067 | 30.2% | 21.1% | 1.43x | 5/22 |
| INTERNAL_DUAL_NOW_067 | 13.2% | 8.4% | 1.57x | 2/22 |
| INTERNAL_ANY_NOW_075 | 26.4% | 18.9% | 1.39x | 3/22 |
| LEADLAG_PRE_TO_INTERNAL_NOW_075 | 13.2% | 5.3% | 2.51x | 1/22 |
| FLOW_PRE_TO_FRAGILITY_NOW_067 | 11.3% | 4.2% | 2.69x | 2/22 |
| FRAGILITY_PRE_TO_FLOW_NOW_067 | 9.4% | 9.5% | 1.00x | 1/22 |

## Episode-first early-warning coverage

At 0.67, at least one mechanism was already elevated at t-1/t-2 in **19/22** episode starts.
At 0.67, at least two mechanisms were already elevated at t-1/t-2 in **10/22** episode starts.
Allowing same-origin evidence as well, >=1 mechanism appears in **22/22**, >=2 in **13/22**.
At 0.75, pre-origin >=1 mechanism: **17/22**; pre-origin >=2: **4/22**.

## Strongest current-origin discriminators

| Feature | Miss mean | Control mean | SMD |
|---|---:|---:|---:|
| fragility_score | 0.554 | 0.457 | +0.399 |
| r_frag_trend | 0.569 | 0.464 | +0.390 |
| r_frag_close | 0.568 | 0.465 | +0.359 |
| r_frag_session | 0.544 | 0.454 | +0.329 |
| r_flow_gc_oppvol | 0.597 | 0.512 | +0.317 |
| r_flow_ineff | 0.558 | 0.479 | +0.294 |
| r_frag_adverse | 0.532 | 0.462 | +0.240 |
| flow_score | 0.528 | 0.476 | +0.232 |
| r_flow_joint | 0.546 | 0.503 | +0.155 |
| tres_warning | 0.310 | 0.296 | +0.109 |
| r_flow_si_oppvol | 0.506 | 0.488 | +0.059 |
| r_llrs_incremental | 0.502 | 0.486 | +0.054 |
| reaction_score | 0.494 | 0.487 | +0.036 |
| reaction_abs_rank | 0.486 | 0.476 | +0.035 |
| reaction_against_rank | 0.502 | 0.497 | +0.016 |

## Episode starts

| Episode | Start | N origins | Max |H3| | Frag pre | Flow pre | LLRS pre | Reaction pre | #pre >=.67 | #any >=.67 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2026-01-02 | 2 | 1.64% | 0.48 | 0.70 | 0.83 | 0.46 | 2 | 2 |
| 2 | 2026-01-26 | 3 | 11.90% | 0.49 | 0.14 | 0.78 | 0.50 | 1 | 1 |
| 3 | 2026-02-02 | 2 | 3.81% | 0.76 | 0.85 | 0.00 | 0.99 | 3 | 4 |
| 4 | 2026-02-16 | 2 | 3.81% | 0.34 | 0.58 | 0.86 | 0.43 | 1 | 1 |
| 5 | 2026-02-23 | 4 | 2.70% | 0.12 | 0.31 | 0.00 | 0.58 | 0 | 1 |
| 6 | 2026-03-05 | 1 | 1.03% | 0.74 | 0.62 | 0.71 | 0.85 | 3 | 3 |
| 7 | 2026-03-16 | 1 | 5.84% | 0.32 | 0.79 | 0.90 | 0.60 | 2 | 3 |
| 8 | 2026-03-26 | 3 | 3.42% | 0.52 | 0.68 | 0.00 | 0.98 | 2 | 2 |
| 9 | 2026-04-06 | 1 | 1.74% | 0.92 | 0.54 | 0.00 | 0.48 | 1 | 2 |
| 10 | 2026-04-17 | 3 | 2.90% | 0.36 | 0.60 | 0.00 | 0.40 | 0 | 1 |
| 11 | 2026-04-29 | 3 | 3.26% | 0.55 | 0.65 | 0.71 | 0.38 | 1 | 1 |
| 12 | 2026-05-11 | 2 | 2.98% | 0.34 | 0.48 | 0.62 | 0.81 | 1 | 1 |
| 13 | 2026-05-18 | 5 | 2.87% | 0.38 | 0.62 | 0.87 | 0.47 | 1 | 2 |
| 14 | 2026-06-08 | 2 | 4.92% | 0.18 | 0.40 | 1.00 | 0.73 | 2 | 2 |
| 15 | 2026-06-24 | 3 | 1.23% | 0.61 | 0.60 | 0.73 | 0.41 | 1 | 1 |
| 16 | 2026-07-06 | 3 | 1.64% | 0.48 | 0.52 | 0.65 | 0.43 | 0 | 1 |
| 17 | 2026-07-14 | 5 | 1.71% | 0.78 | 0.84 | 0.74 | 0.42 | 3 | 4 |
| 18 | 2026-07-30 | 1 | 0.30% | 0.85 | 0.45 | 0.00 | 0.72 | 2 | 3 |
| 19 | 2026-08-18 | 1 | 4.41% | 0.61 | 0.60 | 0.00 | 0.83 | 1 | 1 |
| 20 | 2026-09-01 | 2 | 1.56% | 0.83 | 0.84 | 0.00 | 0.97 | 3 | 4 |
| 21 | 2026-09-09 | 2 | 2.03% | 0.11 | 0.59 | 0.80 | 0.44 | 1 | 3 |
| 22 | 2026-09-22 | 2 | 2.90% | 0.92 | 0.74 | 0.00 | 0.44 | 2 | 2 |

## Interpretation discipline

- A high same-origin score is detection, not necessarily advance warning.
- The key evidence for a usable signal is t-1/t-2 episode-start coverage with materially lower prevalence on correct-continuation controls.
- No threshold in this report is a frozen trading rule.
- TRES is secondary diagnostic context only and is not counted among the four primary mechanism families.
