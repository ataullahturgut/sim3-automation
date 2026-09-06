# GOLD CONTROL — VW_MIDAS_MSVR_SUCCESSOR_V1 XAU TARGET / ANCHOR BRIDGE CONTRACT

Frozen: 2026-09-06, before the first prospective origin.
Model: `VW_MIDAS_MSVR_SUCCESSOR_V1`
Scope: prospective shadow price-level anchor and later target measurement.

## 1. Historical target reference

Historical V1 evaluation used `CORE5_GOLD_USD_OZ_RESEARCH_R1` as the monthly-average XAU/USD price-level reference. That source is a locked local research snapshot ending 2026-07 and is not treated as a continuously refreshable live source.

## 2. Prospective measurement identity

Prospective identity:
`STAKTRAKR_COMMON4_GOLD_MONTHLY_MEAN_PROSPECTIVE_V1`

It is derived from the exact commit-pinned prospective StakTrakr snapshot frozen by:
`GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_FOUR_METAL_PROSPECTIVE_SOURCE_REFRESH_CONTRACT.md`.

For any calendar month m:
1. retain only dates where Gold, Silver, Platinum and Palladium are all present;
2. take the arithmetic mean of Gold spot values across those common complete dates;
3. no interpolation, imputation or alternate provider fill;
4. record common-day count and first/last common date.

This is intentionally the same common-date Gold monthly mean surface used to construct the MSVR monthly Gold return target, avoiding an unnecessary provider change.

## 3. Historical bridge evidence frozen before prospective scoring

Production Neon overlap comparison was performed on 2026-09-06 using the historical StakTrakr R1 common-four-metal dates and `CORE5_GOLD_USD_OZ_RESEARCH_R1`.

Overlap:
- months: 199
- window: 2010-01 through 2026-07
- mean common dates/month: 21.25
- minimum common dates/month: 18
- maximum common dates/month: 31

Bridge error vs CORE5:
- mean absolute difference: 2.8103185966814905 USD/oz
- median absolute difference: 1.652173913043498 USD/oz
- maximum absolute difference: 100.48173913043411 USD/oz
- mean APE: 0.14063840606656702%
- median APE: 0.10121457489877987%
- maximum APE: 2.0692285652890057%
- Pearson correlation: 0.9999537033295735

These numbers are bridge evidence, not a post-result acceptance threshold and must not be retuned after October is observed.

## 4. First prospective forecast anchor

For forecast origin 2026-09-30 / target 2026-10:
- September anchor = `STAKTRAKR_COMMON4_GOLD_MONTHLY_MEAN_PROSPECTIVE_V1` for September 2026 from the exact issuance snapshot;
- predicted October Gold log return is produced by the immutable V1 MSVR;
- prospective price forecast = September anchor × exp(predicted October Gold log return).

The anchor may be used only if the four-metal September completeness gate passes.

## 5. Prospective October actual for scoring

After October 2026 is complete and target data are mature, the primary prospective actual is the same measurement identity:
`STAKTRAKR_COMMON4_GOLD_MONTHLY_MEAN_PROSPECTIVE_V1` for October 2026.

The October actual must be generated from an exact commit-pinned snapshot retrieved after target maturity. The forecast artifact issued before October maturity is immutable.

Any contemporaneous CORE5-like or Twelve measurement may be reported only as secondary bridge diagnostics; it cannot silently replace the frozen primary actual.

## 6. Benchmark

Same-origin Random Walk forecast for the prospective test equals the frozen September prospective anchor.

Thus candidate and RW are scored against exactly the same prospective target measurement.

## 7. Governance

- no CORE5 future values are invented;
- no Twelve substitution is required;
- historical and prospective target identities are explicitly bridged rather than claimed identical;
- model architecture/features/grid remain unchanged;
- no production forecast/decision write;
- no selector/ensemble activation;
- no backdated issuance.
