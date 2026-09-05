# Gold Control — Macro Event Successor V2 Robust Score Replay Evidence

Date: 2026-09-05
Branch: `gold-control-macro-event-successor-v2-robust-score`
Engine identity: `MACRO_EVENT_SUCCESSOR_V2`
Workflow run: `33979730731`
Workflow head: `910af50d8c21571e68aae38cffb0697d8d06d2c7`
Conclusion: `SUCCESS`

## Frozen preregistration

Preregistration blob SHA:
`3584e8e89307971405a439fba9f8229f571e7852`

The V2 replay was executed only after the robust-scale formula had been frozen. V2 is a separate successor identity because V1 replay results had already been observed.

## Source binding

Frozen Neon research source run:
`6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a`

Source pipeline:
`MACRO_EVENT_SUCCESSOR_V1_RESEARCH_DATA_PLANE_R1`

Input fingerprint:
`f70278151929afce0fbc52cf0db8aeb4fff72f515fbd5cd116390ebb7b575e8a`

Source observations: 756
Complete-case reference months: 126
Excluded months: `2020-08`, `2025-10`

## Engineering validation

- status: `PASS_V2_ROBUST_PREREG_REPLAY_REPRODUCIBLE`
- unit tests: 7/7 PASS
- minimum prior history: 24 events
- scored events: 102
- insufficient-history events: 24
- prefix invariance: PASS
- production DB write: false
- model result persisted to Neon: false
- direction vote: false
- Forecast/Decision write: false
- all four Forecast/Decision authority-store counts remained 0 before and after replay

Every scored NFP, unemployment and AHE component used `MAD_1P4826`. The predeclared IQR fallback was not needed by the governed production research panel.

## State distribution

DEV 2016-01..2020-12:
- `INSUFFICIENT_HISTORY`: 24
- `MACRO_MIXED_OR_SMALL`: 29
- `GOLD_ADVERSE_MACRO_SHOCK`: 5
- `GOLD_SUPPORTIVE_MACRO_SHOCK`: 1

VAL 2021-01..2023-12:
- `MACRO_MIXED_OR_SMALL`: 29
- `GOLD_ADVERSE_MACRO_SHOCK`: 6
- `GOLD_SUPPORTIVE_MACRO_SHOCK`: 1

LOCK 2024-01..2026-08:
- `MACRO_MIXED_OR_SMALL`: 30
- `GOLD_ADVERSE_MACRO_SHOCK`: 1
- `GOLD_SUPPORTIVE_MACRO_SHOCK`: 0

Therefore V2 produced 8 shock states in VAL+LOCK, compared with zero under V1. This is a descriptive sensitivity result only; it is not by itself evidence that the shock states correctly predict gold reactions.

## Out-of-sample shock dates

VAL:
- 2021-02: adverse, score -1.138058
- 2021-04: supportive, score +2.403954
- 2021-07: adverse, score -1.203258
- 2022-01: adverse, score -1.544667
- 2022-07: adverse, score -1.733860
- 2023-01: adverse, score -1.736620
- 2023-04: adverse, score -1.179878

LOCK:
- 2024-01: adverse, score -1.565782

No other LOCK month through 2026-08 crossed the frozen V2 shock threshold.

## Latest governed event

Reference month: `2026-08`

Inputs:
- NFP actual 162k, consensus 55k, surprise +107k
- unemployment actual 4.1%, consensus 4.1%, surprise 0.0pp
- AHE MoM actual 0.3%, consensus 0.3%, surprise 0.0pp

Robust scales:
- NFP: 85.9908
- unemployment: 0.14826
- AHE: 0.14826

Standardized NFP surprise: +1.2443191597240637.
Gold-oriented composite score: `-0.414773053241`.
State: `MACRO_MIXED_OR_SMALL`.

Interpretation: the NFP surprise was gold-adverse under the frozen orientation, but unemployment and AHE were exactly at consensus. Breadth therefore remained only one adverse component and the composite did not satisfy the frozen strong-shock rule.

## Decision

V2 fixes the specific V1 scale-inflation problem in the sense that post-2020 shocks are no longer mathematically suppressed to zero incidence. However, V2 is **not approved for runtime promotion**.

Current stop state:
`NOT_APPROVED_EVENT_REACTION_VALIDATION_REQUIRED`

The next admissible phase is a separately frozen point-in-time gold event-reaction validation. Reaction source, observation window, sign-success definition and acceptance gates must be preregistered before reaction outcomes are inspected. No threshold or V2 score rule may be retuned using those future reaction results.