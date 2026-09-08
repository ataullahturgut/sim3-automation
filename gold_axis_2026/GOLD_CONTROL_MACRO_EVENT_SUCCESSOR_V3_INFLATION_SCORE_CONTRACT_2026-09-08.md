# Gold Control — Macro Event Successor V3 Inflation Score Contract

Date: 2026-09-08
Engine: `MACRO_EVENT_SUCCESSOR_V3`
Family: `INFLATION`
Status: **PRE-RESULT FROZEN RULE / RESEARCH ONLY**

This contract implements only the CPI + Core CPI scope already frozen in `GOLD_CONTROL_MACRO_EVENT_SUCCESSOR_V3_PREREG_2026-09-08.md`.

## Inputs

- Headline CPI MoM, seasonally adjusted, actual first print.
- Core CPI MoM, seasonally adjusted, actual first print.
- Pre-release consensus for the same two measures.
- Official BLS release timestamp for the exact reference month.

Historical reconstructed consensus values that lack a provider-level pre-release update timestamp remain `HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PIT_PROVEN`. They may be used to inspect/reproduce the historical model but may not create `MACRO_CONFIRMED` authority.

Prospective consensus is PIT-eligible only when our immutable capture satisfies `captured_at < official_release_at` and carries provider-response/payload fingerprint lineage.

## Surprise and normalization

For each event t:

- `e_cpi,t = CPI_actual_first_print,t - CPI_consensus,t`
- `e_core,t = CORE_CPI_actual_first_print,t - CORE_CPI_consensus,t`

Each component is standardized using only prior events. The robust scale is inherited exactly from Macro Event V2:

1. `1.4826 * MAD(prior surprises)` when positive and finite.
2. `(Q75-Q25)/1.3489795003921634` fallback when MAD scale is zero/non-finite.
3. At least 24 prior events are required.

No current or future event enters its own scale.

## Gold-context orientation

Hotter-than-expected inflation is adverse gold context; cooler-than-expected inflation is supportive gold context.

- `g_cpi = -z_cpi`
- `g_core = -z_core`
- `family_score = mean(g_cpi, g_core)`

This is context, not a deterministic gold price forecast.

## Strong-event rule

The V2 magnitude boundary is inherited without locked-period optimization:

- `GOLD_ADVERSE_MACRO_SHOCK` if `family_score <= -1.0` **and both** oriented components are negative.
- `GOLD_SUPPORTIVE_MACRO_SHOCK` if `family_score >= +1.0` **and both** oriented components are positive.
- otherwise `MACRO_MIXED_OR_SMALL`.

Because Inflation contains exactly two governed components, breadth is frozen at `2/2` for a strong state. No 2024–2026 outcome was inspected to choose this rule.

## Evidence classes

- Historical reconstruction with non-proven consensus timestamp: `HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PIT_PROVEN`.
- Prospective pre-release snapshot plus first-print actual: `PROSPECTIVE_SHADOW` until a separate promotion decision.

## Locks

- No CPI/Core substitution.
- No PPI or other inflation series.
- No threshold tuning after replay.
- No Market Shock threshold mutation or raw episode deletion.
- No production Decision Store / Forecast Store write.
- No canonical promotion from this contract alone.
