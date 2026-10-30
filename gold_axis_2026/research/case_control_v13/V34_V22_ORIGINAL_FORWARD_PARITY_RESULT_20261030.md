# V34 + V22 — Original-model forward-only parity results (2026-10-30)

## Scope

Pure model inference and risk rule replication; the retrospective research history is **not** live, firstprint-certified, bank-executable, or automatically traded.

## V34 original weekly ANN (Stage 4 computation)

- Original model: `gold_weekly_h1_ann_4metal_v1.py`, expanding-window 16D AU/AG/PT/PD, MLP 8 tanh, sklearn lbfgs, alpha=1, 180 max iterations, seed 1701, training-only normalization.
- Adapter: `gold_v34_forward_parity_v1.py`.
- Model calculation for target week `2026-10-19` was recomputed with **all target- and future-week rows removed before model fitting**.
- Historical original forecast weekly mean: **4103.911794713988** USD/oz.
- Forward-only reimplementation weekly mean: **4103.911794713988** USD/oz.
- Original last reference forecast: **4127.30921063908** USD/oz.
- Forward-only last reference forecast: **4127.30921063908** USD/oz.
- Expanding training count: **874** weeks.
- Original and forward calculations match to tolerance 1e-8; rejecting any target-week presence and checking historical origin/training parity PASSED.
- Evidence: https://github.com/ataullahturgut/sim3-automation/actions/runs/41021962206

This is **not a new 30 October forecast**. The source is historical StakTrakr with an uncertified February reference scenario, and requires firstprint/origin reconciliation before live use.

## V22 original 7-rule as-of calculation (Stage 5 scoring)

- Original source: `risk_v22_slope_decision.py`; replacement source: `gold_v22_forward_rule_parity_v1.py`.
- Reproduced seven original rule flags and prior-day RED_CORE memory without target outcome fields.
- **647/647** chronological 2024–26 retrospective dates: signal level, reason string, RED core, watch/carry, slope and numeric acceleration values match original V22 source.
- Target outcome label poisoning did not change decisions.
- No BASE14/CFTC21 live feature creator yet; this scorer only accepts their previously calculated as-of feature rows.
- Evidence: https://github.com/ataullahturgut/sim3-automation/actions/runs/41022161414

## Remaining blocks before issuance

1. Original V34 currently depends on four-metal daily origin data, missing in live Neon after October 16, with research-only status and price-reference mismatch to canonical NY17.
2. 2026-10-30 Friday NY17 close had not occurred at audit time 07:41 UTC; issuing a 2026-11-02 weekly forecast before the origin is fully observed would violate the established model contract.
3. Original BASE14 and CFTC21 as-of feature generation and full quality/provenance clocks are not a validated live pipeline. V22 rule parity alone does not supply a current alert.
4. Need frozen source/model fingerprints, firstprint immutable publication, dry-run end-to-end replay, application display validation and scheduler evidence. Never fabricate a current signal to fill an empty table.
5. Monthly calibration remains paused and user portfolio records are untouched.

**Result:** Original V34 forward inference and original V22 seven-rule scorer are reproducible. Production issuance is still **BLOCKED_NOT_LIVE**.
