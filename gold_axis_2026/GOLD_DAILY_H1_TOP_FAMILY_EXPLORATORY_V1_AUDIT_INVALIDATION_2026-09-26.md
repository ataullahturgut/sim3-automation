# GOLD DAILY H=1 TOP-FAMILY EXPLORATORY V1 — AUDIT / INVALIDATION

**Audit date:** 2026-09-26
**Run:** 36200611626
**Commit:** f0f01ae600f30c0e9db42bc18697e3b64c8de80b

## Decision

**INVALID AS A GOVERNED DAILY BACKTEST.**

The run remains reproducible evidence of an exploratory frequency-transfer experiment, but its metrics MUST NOT be used as evidence for or against the monthly top models or as a canonical daily-model result.

## Why

### 1. Feature-contract mismatch
The governed monthly VW-MIDAS contract uses, for each metal: prior monthly log return plus a within-origin-month weighted daily return whose decay parameter is controlled by the GPR state.
The exploratory daily H=1 script instead used latest one-day log return plus fixed 20-trading-day EWMA log return.
Therefore the experiment changed the feature-generation contract rather than merely changing forecast frequency.

### 2. Point-in-time provenance is not proven
The four daily metal series used by the exploratory script are explicitly labeled APPROVED_HISTORICAL_RESEARCH_RECONSTRUCTION_NOT_PIT.
They may be used for exploratory retrospective research, but they do not prove historical origin-day availability in the same form.

### 3. Collapse-to-persistence diagnostic
On 145 weekday 2026 rows:
- actual mean absolute daily move: about 61.59 USD;
- actual daily log-return SD: about 1.904%;
- FULL7 mean absolute predicted move: about 7.91 USD;
- FULL7 predicted log-return SD: about 0.115%;
- FULL7 return correlation with realized return: about -0.066;
- FULL7 direction accuracy: about 51.03%.

## Required replacement protocol
1. Freeze a daily H=1 feature contract BEFORE seeing 2026 results.
2. Use only origin-safe / PIT-proven inputs, or label results research-reconstruction-only.
3. Preserve four-output Gold/Silver/Platinum/Palladium architecture if family parity is the objective.
4. Define daily analogues of governed VW-MIDAS inputs explicitly; do not silently replace GPR-adaptive weighting with generic EWMA.
5. Develop/tune on pre-2026 data only with chronological validation.
6. Keep 2026 locked as test.
7. Compare against persistence and report price error plus direction.
8. Do not reuse invalid exploratory metrics for model selection.

## Governance
- Previous daily H=1 table: SUPERSEDED / INVALID FOR GOVERNED INFERENCE
- Monthly model results: UNCHANGED
- Database writes: NONE
- 2026 daily canonical conclusion: NOT_PROVEN
