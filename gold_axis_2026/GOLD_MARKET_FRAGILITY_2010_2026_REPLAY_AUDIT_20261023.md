# GOLD MARKET FRAGILITY CORE V1 — LOCKED HISTORICAL AUDIT (2026-10-23)

**Branch:** gold-market-fragility-core-v1-20261023 (standalone shared research component; NOT automatically merged into app/production)
**Validated GitHub Actions:** https://github.com/ataullahturgut/sim3-automation/actions/runs/40009445333 (2/2 jobs SUCCESS)
**Status:** COMPLETE HISTORICAL RETROSPECTIVE RESEARCH; JAN 2026 EX-ANTE RANK ALERT OBSERVED; **PRODUCTION PROMOTION REJECTED** BECAUSE 2025 ONE-DAY GENERALIZATION FAILS
**Full artifact:** gold-market-fragility-full-2010-2026-locked-model-comparison (includes every origin 2024–2026)
**GVZ + priced data source artifact:** gold-market-fragility-official-gvz-canonical-research-source
**Code:** gold_axis_2026/tools/gold_market_fragility_origin_safe_v1.py
**CI:** .github/workflows/gold-market-fragility-origin-safe-v1.yml

## Explicitly preserved research design

- One independent, re-usable market risk research core; does NOT use monthly, weekly or daily forecast outputs, outcomes or prediction errors when creating input features.
- Four metal daily prices (AU AG PT PD) from existing pinned research Git source. Align trading dates and exactly reproduce existing Neon authoritative monthly research view; 4234 aligned dates since 2010. Historical pinned source **NOT FIRST-PRINT PIT**. Excludes research price error on 2026-02-27 from scored Jan/Feb 2026 targets.
- Gold implied volatility from **primary CBOE official GVZ_History.csv**, 4298 daily closes since Sept 2009, SHA-256 5d117354bc410ebfcb87d30c110d0a23289485648576c84de73db29fe1d4a28d. CBOE source https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv . One FRED official crosscheck: GVZCLS on 2026-01-29 = 46.02. Official CBOE GVZ is based on GLD options, not spot XAU put implied 1-day return.
- Issue at **after US options daily close** on day t, using the last known same-date GVZ close and last same-day available LBMA-labeled four-metal daily quotes (not an EOD exchange close, not a tick stream). Future target: next aligned trading-day reference XAU return, and lowest daily-reference XAU during following five aligned price days.
- Features 16: GOLD_RET1, RET5, RET20, RSI14 rolling proxy, distance MA20, drawdown from 20d peak, realized vol 5/20; SILVER_RET1, SILVER_RET5, SILVER_RV5, 4-metal return dispersion 5d; GVZ_LEVEL, GVZ_Z252, GVZ_RET5, GVZ_RET1.
- CME silver margin Jan27 exists as chronologically valid piece of **qualitative evidence**, but complete 2010–2025 CME margin event archives have NOT been verified. CME margin is therefore **NOT** inserted as falsely-complete model feature. News / after-event content is also NOT in the numeric model.
- Three independent research targets:
  1. DROP_1D_3PCT: next reference daily XAU <=-3%,
  2. DRAWDOWN_NEXT5D_5PCT: min(next five daily reference quotes)/current-1 <=-5%,
  3. MOVE_1D_3PCT: absolute next daily reference XAU move >=3%.
- Historical model comparison for each target: GOLD_ONLY (8 input), GOLD_GVZ (12), GOLD_CROSS_GVZ (16).
- Fixed balanced LogisticRegression(C=0.25), standardized using ONLY 2010-2023 training. **No features, labels or thresholds selected by 2024/2025/2026 performance.**
- Three fixed phases: TRAIN 2010–2023 **3268 mature origins**, DIAGNOSTIC 2024 **254**, HOLDOUT 2025 **253**, 2026-STRESS Jan 1..Feb 19 **35** origins (2026-02-27 price source defect cannot appear in future five-day outcome).
- Scores from balanced logistic are **UNCALIBRATED risk ranks, not true-event probabilities**. Pre-2024 train scores' fixed 90th percentile is the alert cutoff. The actual alert percentage outside train can exceed 10% due distribution shift.
- No database writes; no existing forecast model code altered; no live trading deployment.

## Main test: next-day serious drop (>=3%), not just mild directional downside

| Family | 2025 actual down events | 2025 detected | 2025 total warnings | 2025 false warnings | 2026 Jan-Feb actual down events | 2026 detected | 2026 total warnings | 2026 false warnings |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GOLD_ONLY | 3 | 1 | 46 | 45 | 3 | 3 | 21 | 18 |
| GOLD_GVZ | 3 | **0** | 18 | 18 | 3 | **2** | 11 | 9 |
| GOLD_CROSS_GVZ | 3 | **0** | 8 | 8 | 3 | **2** | 9 | 7 |

2024 validation: **ZERO actual daily XAU declines >=3%**; model cannot show recall/precision predictive success for this target in that phase, GOLD_CROSS_GVZ had two false alarms. Historical pre-2024 TRAIN had only **14** single-day >=3% drop events, making one-day down classifier small-positive/high uncertainty.

For GOLD_CROSS_GVZ:
- 2025 drops (signal origin): Apr22, May9, Oct21: **all 3 missed**.
- 2026 event origins: Jan29 (target Jan30 drop -7.97%), Jan30 (target Feb2 drop -7.47%) **both alerted**; Feb4 (another >3% following-day down move) **missed**.
- 2026 total 9 daily-drop warnings in 35 origins: 2 hits + 7 false; cannot label ready.
- Comparison: adding GVZ and 4-metal divergence **reduced false warnings dramatically** in 2025 versus price-only 45→8, but at cost of detecting 1/3→0/3. This is NOT evidence of superior qualified crash detection.

## Next-five-day drop >=5% — remember overlapping origins are NOT separate crash episodes

| Family | 2025 true positive issue-date rows | 2025 hits | 2025 warnings | 2025 false | 2026 true positive issue-date rows | 2026 hits | 2026 warnings | 2026 false |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GOLD_ONLY | 6 | 6 | 65 | 59 | 5 | 5 | 31 | 26 |
| GOLD_GVZ | 6 | 5 | 34 | 29 | 5 | 5 | 30 | 25 |
| GOLD_CROSS_GVZ | 6 | 6 | 48 | 42 | 5 | 5 | 18 | 13 |

2024 valid: 2 five-day true rows, **0 caught** by all families (2 GVZ+cross warnings both false). 2025 six true rows cluster in several market episodes, not six independent crashes. 2026 Jan26–Jan30 five true rows are **all overlapping labels of the same Jan30–Feb2 collapse**. Score 5/5 means correctly flagged every eligible ISSUE ORIGIN near that **one** episode, not five crashes.

## Crucial Jan-Feb source-visible warning time sequence (GOLD_CROSS_GVZ)

| End-of-options-close origin | CBOE GVZ | Price RSI14 rolling proxy | Upcoming next-five-day <-5% flagged? | Next-day <-3% flagged? | Interpretation |
|---|---:|---:|---|---|---|
| Jan22 | 28.11 | 85.18 | YES | YES | FALSE for next-five-day, later movement not yet within 5-day horizon |
| Jan26 | 32.70 | 88.50 | YES | YES | TRUE next-five-day because Feb2 drops to -8.01% vs Jan26 price; next-day -3 false |
| Jan27 | 33.13 | 87.85 | YES | YES | TRUE next-five-day; next-day -3 false |
| Jan28 | 39.67 | 92.68 | YES | YES | TRUE next-five-day; next-day -3 false (Jan29 was UP) |
| **Jan29** | **46.02** | **93.69** | **YES** | **YES** | **NEXT-DAY TRUE: Jan30 XAU -7.96572%, first main plunge** |
| Jan30 | 44.08 | 66.74 | YES | YES | NEXT-DAY TRUE: Feb2 XAU -7.46527%; Jan30 decline already happened |
| Feb2 | 37.38 | 52.98 | NO | NO | next-day bounce +5.08%, correct no DROP but MOVE abs >=3 flagged |

The Jan26 five-day flag is ~4 trading days before Feb2 event (Jan27,28,29,30,Feb2). The Jan29 next-day warning is generated after the **already-large intraday reversal** within Jan29 and after GVZ 46 close, i.e. before Jan30's next major leg, NOT before every onset.

## Decision and scientific limits

**PRE-30-JAN WARNING: YES. ROBUST GENERAL PROVEN PERFORMANCE: NO.**
- The model generated a genuine strict origin-based *retrospective replay* warning before Jan30 and a 5d risk alert as of Jan26, frozen training from <=2023.
- It did not detect ANY of the three 2025 one-day >=3% drops and generated 8 false alerts across 2025 on GOLD_CROSS_GVZ. In 2024 there were zero daily >=3% down events, so 2024 cannot validate single-day recall.
- This is a 2026 retrospective holdout on current-snapshot historical market data, not fully firstprint/PIT or an actual logged real-time alert. Should not claim it predicted the crash live.
- Need other large crashes and *matched high GVZ/RSI controls without crash*, evaluate episode-level precision/recall, false alarms per month, and realistic decision time trade execution; gain independent validation on post-2026 data before deployment.
- Do not recalibrate to 2026 events and then recount them as untouched stress. Do not merge automatically into canonical monthly/weekly application.
- In next audit, convert 5-day rolling labels to separated **episode IDs** and compute warning lead time and number of missed independent episodes; aggregate all-2010–2025 historical source anomaly audit, and verify CBOE daily close publication time for prospective as-of setup.
