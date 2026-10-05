# GOLD D1 — CIG-D1 V1 EXTENDED 2026 JAN–SEP REPLAY

**Date:** 2026-10-05  
**Identity:** `CIG_D1_V1_EXTENDED_JAN_SEP_REPLAY`  
**Status:** RETROSPECTIVE DIAGNOSTIC / SOURCE-REFRESH REPLAY — NOT PROSPECTIVE OOS  
**Binding CIG rule unchanged:** 4/4 agreement among SAGE V2 + RuleFlow V3-TG, HELIOS V5-DCE, RIFT, VEGA; any disagreement = UNCERTAIN.

## 1. Why the old report had 145 days

The original CIG-D1 report used the then-frozen StakTrakr 2026 historical source vintage. On weekdays from 2026-01-02 through 2026-07-31 that vintage contains exactly **145 Gold observations**.

The later clean H3 frozen snapshot restores six previously absent weekdays:
- 2026-02-27
- 2026-03-02
- 2026-03-03
- 2026-03-04
- 2026-03-05
- 2026-03-06

Therefore the refreshed clean Jan–Jul calendar contains **151** eligible D1 issue days, not 145.

The original 145-day CIG result remains valid for its own frozen source vintage. It must not be mechanically concatenated with Aug–Sep from the refreshed source, because that would mix source vintages.

## 2. Reproducible replay contract

Price realization:
`GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv`

Expert state files:
- `GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv`
- `GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv`
- `GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv`
- `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_EVENTS_2026-10-04.csv`

Daily target:
`Gold(forecast_issue_date) > Gold(feature_cutoff_date) => UP`, else DOWN.

The archived mature H3 prediction files support D1 issue dates through **2026-09-25**. Thus the coherent refreshed replay contains **191** D1 days from Jan through Sep. This result does not fabricate Sep 28–30 expert states.

## 3. Main result

| Period | D1 days | 4/4 consensus | Correct | Consensus accuracy | Coverage | Disagreement | V5 correct inside disagreement |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jan–Jul refreshed | 151 | 131 | 94 | 71.76% | 86.75% | 20 | 10/20 |
| Aug–Sep | 40 | 26 | 18 | 69.23% | 65.00% | 14 | 7/14 |
| **Jan–Sep refreshed** | **191** | **157** | **112** | **71.34%** | **82.20%** | **34** | **17/34** |

### Forced daily direction benchmarks on the same refreshed 191-day universe
- SAGE V2 + RuleFlow V3-TG: **130/191 = 68.06%**
- HELIOS V5-DCE: **129/191 = 67.54%**
- RIFT: **127/191 = 66.49%**
- VEGA: **127/191 = 66.49%**

## 4. Monthly consensus behavior

| Month | D1 days | Consensus N | Correct | Accuracy | Coverage | Disagreement |
|---|---:|---:|---:|---:|---:|---:|
| 2026-01 | 21 | 21 | 15 | 71.43% | 100.00% | 0 |
| 2026-02 | 20 | 15 | 11 | 73.33% | 75.00% | 5 |
| 2026-03 | 22 | 20 | 18 | 90.00% | 90.91% | 2 |
| 2026-04 | 22 | 16 | 10 | 62.50% | 72.73% | 6 |
| 2026-05 | 21 | 19 | 12 | 63.16% | 90.48% | 2 |
| 2026-06 | 22 | 20 | 12 | 60.00% | 90.91% | 2 |
| 2026-07 | 23 | 20 | 16 | 80.00% | 86.96% | 3 |
| 2026-08 | 21 | 10 | 8 | 80.00% | 47.62% | 11 |
| 2026-09 | 19 | 16 | 10 | 62.50% | 84.21% | 3 |

## 5. Key interpretation

1. **There were more usable 2026 days than the first CIG report showed.** The old 145 was source-vintage-specific, not the maximum available 2026 history.
2. On the refreshed single-source replay, Jan–Sep supplies **191** same-contract D1 observations and **157** high-confidence 4/4 consensus actions.
3. Aug–Sep adds **40** D1 observations; the consensus fires on **26** of them and is correct on **18** (**69.23%**).
4. August is unusual: consensus accuracy is **80.00%**, but coverage collapses to **47.62%**. The expert stack disagrees on 11/21 days.
5. September coverage recovers to **84.21%**, while consensus accuracy falls to **62.50%**.
6. Across the full refreshed Jan–Sep replay, disagreement days remain exactly chance under a forced V5 call: **17/34 = 50.00%**. This continues to support the core CIG interpretation that disagreement is an observable uncertainty state.
7. The full refreshed consensus accuracy is **71.34%**, below the original 145-day vintage result of 74.40%. This is not a clean degradation comparison because the source vintage and eligible calendar changed; it is the correct internally consistent Jan–Sep replay on the later clean snapshot.

## 6. Governance

- Do **not** replace the original `CIG_D1_V1` authority with this replay.
- Do **not** combine 93/125 from the old vintage with Aug–Sep counts from the refreshed vintage.
- Use this artifact as the internally consistent extended historical diagnostic for 2026 Jan–Sep.
- Any Sep 28–30 extension must generate same-origin expert states under the frozen inference contracts; it must not be imputed from later outcomes.
