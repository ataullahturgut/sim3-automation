# GOLD H1 R1 — Unified 2023 Daily Investment Engine R2

## Corrections
- Continuous position state: NO month-boundary reset. A changed monthly prior creates an explicit AL/SAT event.
- Removed ad-hoc MOM1/Fast/Slow equal voting.
- Restored 2026 hierarchy: 3M monthly prior; MOM1/VW/Patch/IDMA as origin context; Fast/Slow as tactical evidence; frozen bidirectional Emergency; BOCPD/CFTC remain risk/context outside daily vote.
- Added GVZCLS as non-directional gold-volatility context; GVZ never votes UP/DOWN.
- Monthly VW/Patch/IDMA/3M price forecasts are target-month-average anchors, not daily-price targets. Daily close-vs-forecast gap is diagnostic only.
- News/Event emergency execution remains BLOCKED_CONSENSUS_HISTORY: no invented surprise threshold or hindsight rule is allowed.

- Frozen DOWN emergency rule: (0.03, 0.04, 'NONE')
- Frozen UP emergency rule: (0.03, 0.02, 'NONE')
- Tactical risk overlay enabled: False; persistence=99; release=99
- 2023 net (10bp/change): 13.57%; MDD: -7.14%; turns=2
- Jan-Feb 2023 net: 0.17%; MDD: -7.14%

## Jan-Feb direction-changing / action days
|Date|Close|Prior|MOM1|VW|Patch|IDMA|Fast|Slow|GVZ|GVZ stress|Emergency|Evidence|Action|Reason|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---|
|2023-01-03|1839.28|+1|+1|+1|+1|+1|+1|+1|nan|False|-|ANCHOR_CONFIRMED|AL|INITIAL_MONTHLY_ANCHOR|
|2023-01-12|1896.77|+1|+1|+1|+1|+1|+1|+1|nan|False|UP|ANCHOR_CONFIRMED|TUT|HOLD|
|2023-01-13|1920.23|+1|+1|+1|+1|+1|+1|+1|nan|False|UP|ANCHOR_CONFIRMED|TUT|HOLD|
|2023-01-16|1915.41|+1|+1|+1|+1|+1|+1|+1|nan|False|UP|ANCHOR_CONFIRMED|TUT|HOLD|
|2023-01-25|1945.76|+1|+1|+1|+1|+1|+1|+1|nan|False|UP|ANCHOR_CONFIRMED|TUT|HOLD|
|2023-02-02|1912.63|+1|+1|+1|+1|+1|+0|+1|nan|False|-|MIXED_NEUTRAL|TUT|HOLD|
|2023-02-03|1864.97|+1|+1|+1|+1|+1|-1|+1|nan|False|-|EARLY_REVERSAL_FAST|TUT|HOLD|
|2023-02-13|1853.47|+1|+1|+1|+1|+1|-1|-1|nan|False|-|REVERSAL_CONFIRMED_FAST_SLOW|TUT|HOLD|

## Status
- Price-level engine: INCLUDED as monthly anchor/context.
- Direction engine: INCLUDED.
- Fast/Slow tactical: INCLUDED with pre-2023 risk-overlay audit.
- Bidirectional price/macro Emergency: INCLUDED and pre-2023 frozen.
- GVZ: INCLUDED correctly as volatility/risk context.
- VIX/USD/real-yield: INCLUDED in Emergency/context.
- News/Event surprise engine: BLOCKED_CONSENSUS_HISTORY; no exact point-in-time consensus dataset is source-locked, so it is NOT allowed to manufacture a 3-Feb SAT.
- BOCPD: monthly structural risk context only; not a same-day direction vote.
- CFTC: weekly positioning context only; no automatic flip.
- 2023 actuals: evaluation only, never used for threshold/persistence/rule selection.
