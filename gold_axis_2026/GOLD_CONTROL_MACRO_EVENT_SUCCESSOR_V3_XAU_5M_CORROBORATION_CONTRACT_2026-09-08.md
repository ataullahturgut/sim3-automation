# Gold Control Macro Event Successor V3 — XAU 5m Corroboration Contract

Status: FROZEN HISTORICAL ROBUSTNESS TEST ONLY
Date: 2026-09-08
Branch: gold-control-macro-event-successor-v3
Production authority: FALSE

## Purpose
This test does not replace the preregistered 1-minute reaction test. It is a separate robustness/corroboration lane used because the governed Twelve Data daily API credit allowance was exhausted during the 1-minute backfill attempt.

## Inputs
- Macro Event V3 strong events only: EMPLOYMENT, INFLATION, FOMC.
- Frozen evaluation window: 2021-01-01 through 2025-12-31.
- Strong states: GOLD_ADVERSE_MACRO_SHOCK or GOLD_SUPPORTIVE_MACRO_SHOCK.
- XAU source: existing Neon table `xau_intraday_research_cache_5m`.
- No external provider calls are permitted in this corroboration test.

## Frozen 5-minute event window
Event timestamps are aligned to 5-minute boundaries.
- pre: close of the completed 5-minute bar immediately preceding the release (`event_ts - 5m`).
- R5 diagnostic: close associated with `event_ts`.
- R15 primary: close associated with `event_ts + 10m`.
- R30 diagnostic: close associated with `event_ts + 25m`.

The primary signed response is therefore the pre-release completed-bar close to the third post-event 5-minute close, approximately 15 minutes of elapsed event reaction.

## Direction mapping
- GOLD_ADVERSE_MACRO_SHOCK: XAU decline is a directional hit.
- GOLD_SUPPORTIVE_MACRO_SHOCK: XAU rise is a directional hit.

## Frozen statistics
Report:
- supported/unsupported event counts,
- directional hits and hit rate,
- one-sided exact sign-test p-value versus 0.5,
- median signed R15 return,
- family-level results for EMPLOYMENT / INFLATION / FOMC.

## Acceptance gate
PASS only when:
1. all strong events are data-supported or unsupported events are explicitly reported,
2. one-sided exact sign-test p <= 0.10,
3. median signed R15 > 0.

## Governance
- HISTORICAL_REPLAY_RECONSTRUCTION only.
- No threshold tuning after result inspection.
- No production promotion.
- No Market Shock threshold or raw episode mutation.
- No decision-store writes.
- The original 1-minute test remains separately reported and is not overwritten by this corroboration result.
