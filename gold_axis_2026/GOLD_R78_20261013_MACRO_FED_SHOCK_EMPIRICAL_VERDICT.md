# R78 completed — FED policy-calendar and source-timed NQ/ZN/CL incremental value for R77 scaled gold shock alarms

**Date:** 2026-10-13. **Executed, no signal promotion.** Preregistered before R78 scoring in commit `a0025c5`. Frozen R77 dynamic +/- threshold first-touch labels and original outputs not overwritten.

## User's question and key distinction
Yes Fed decisions/expectations and rates, inflation, employment surprises, risk appetite, and FX plausibly matter for gold corrections and rebounds. But they enter a model ONLY when their actual value and timestamp is proved available *before* the alarm issue.
This audited preliminary integration contains:
- Three independent CME Databento continuous 4h futures observations: NQ (Nasdaq-100), ZN (10yr Treasury price **not actual nominal or real yield**), CL (crude); exactly UTC 01,02,03,04 start bars ending <=05 UTC and before issue 09 TRT (=06 UTC). Data provenance source historically reconstructed; exact continuous futures roll mapping and historical firstprint not certified. Retrieved from Neon in read-only fashion, `data_r78/GOLD_R78_20261013_CME_NQ_ZN_CL_01_04UTC_AVAILABLE.csv`.
- Two known Fed **schedule-only** flags from official [FOMC calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm), upcoming expected decision release during same-day/next3 weekdays and whether previous business day was a scheduled announcement. Archived asof schedule vintage not proven.
- NO policy-decision future outcome, Fed funds futures probability-change or consensus revision, CPI/PCE/NFP economic release surprise, actual DXY, real yields, GVZ, or announcements after the 09:00 origin as features. Historical exact-asof provider consensus/surprise timestamps still unavailable. Future dates are known schedule flags, never known market surprises.

## Fair fixed-set ablations and calendar periods
Only 670 full crossasset-matched gold decision dates: 2023 n189 **training only**, 2024 n186 research development evaluation, 2025 n180 and 2026 Feb-Oct n115 **opened retrospective transport**. All three models same target, same date set, same method/training: PRICE7; PRICE7+MACRO3; PRICE7+MACRO3+FEDCAL2. L2 regularized logistic (C=.2), standardization from training only. 2024 training on mature 2023, freeze same fitted train through 2024 Dec24 for 2025/26. Original R77 all-eligible 2026 n146 differs in sample and historical model training, so **do not compare unmatched AUC 0.676 with R78 0.757** as a valid gain.
2026 R78 matched sample n115, standardized event outcomes DOWN_FIRST 11, UP_FIRST 16, ANY 27. High alert threshold = 2024 dev top-fifth of that spec score; later-year use frozen.

## Matched Brier and AUC change (higher AUC/better ranks; lower Brier/better probabilities)
| year | risk | model | Brier | AUC |
|---|---|---|---:|---:|
| 2024 | DOWN | PRICE7 / +MACRO3 / +FEDCAL2 | .11639 / .11608 / .11325 | .643 / .566 / .585 |
| 2024 | UP | PRICE7 / +MACRO3 / +FEDCAL2 | .17540 / .18001 / .17945 | .495 / .480 / .521 |
| 2024 | ANY | PRICE7 / +MACRO3 / +FEDCAL2 | .23126 / .23288 / .23198 | .597 / .588 / .604 |
| 2025 | DOWN | PRICE7 / +MACRO3 / +FEDCAL2 | .09435 / .09453 / .09530 | .696 / .694 / .680 |
| 2025 | UP | PRICE7 / +MACRO3 / +FEDCAL2 | .19716 / .19668 / .20074 | .653 / .652 / .617 |
| 2025 | ANY | PRICE7 / +MACRO3 / +FEDCAL2 | .20266 / .20463 / .20462 | .743 / .733 / .735 |
| 2026 | DOWN | PRICE7 / +MACRO3 / +FEDCAL2 | .08472 / .08475 / .08501 | .757 / .763 / .746 |
| 2026 | UP | PRICE7 / +MACRO3 / +FEDCAL2 | .11975 / .12036 / .12161 | .663 / .663 / .634 |
| 2026 | ANY | PRICE7 / +MACRO3 / +FEDCAL2 | .17803 / .17935 / .18112 | .729 / .728 / .705 |

**0/6 (DOWN,UP,ANY × +MACRO3,+FEDCAL) strict predeclared three-year paired DEV-CI improvement gates passed**. Positive apparent 2024 DOWN Brier gain for +FEDCAL is not repeated 2025–26. 2026 macro DOWN AUC increases just .006, but Brier WORSENS slightly and event alert performance unchanged.

### Actual 2026 warning recall at original 2024-frozen score thresholds
DOWN_FIRST 11 actual exceptional risk windows:
- PRICE7 alerts 12, **2 hits / 11 true declines**; precision 2/12.
- PRICE7+MACRO3 alerts 11, **2 hits / 11**; precision 2/11.
- PRICE7+MACRO3+FEDCAL alerts 15, **2 hits / 11**; precision 2/15.
UP_FIRST 16: baseline 6 alerts, 2 hits; macro 6 alerts, 2 hits; Fed7 alerts, 2 hits. Hence not a bank-trade / timely risk exit.

## What must be researched next, without leaking the future
1. Actual Fed information shock = change in Fed-funds/2yr implied path from **timestamped** pre/post announcement market prices, and change only AFTER released, never before. Reconstruct provider ingestion clock with DST; 09TR origin on Fed announcement day is **before** 14:00 US ET actual decision.
2. NFP, CPI, PCE release surprise from real *preceding consensus snapshot* with vendor reception timestamp; mere final consensus/reconstructed surprise on issue morning is not PIT proof. US macro known release calendar date indicator may be added only if scheduled asof.
3. GVZ previous US close allowed only with published prior-day close and timestamp; independent DXY/US 2yr/10yr real yield after issue gate. Differentiate 2025 bullish inflation/risk regime and 2026 bearish/liquidity/rates vs these observables.
4. User's bank trade action needs **as-of monthly forecast** plus two hazard heads for exit and reentry; historical monthly-asof trained summary absent in Neon, so no valid bank trading backtest yet. Use bank buy/ask actual source and fee/spread at 09/16:30, withholding time and false exits; instrument GLDTR/certificate changes spot relevance.
5. 2025–26 reopened many times; require future locked untouched live decisions (2027 paper/live-shadow) to establish meaningful alpha. No new test-time feature selection based on these 2026 results.

## Reproducibility
Research PR R78, input commit `f074617`, executable `tools/gold_r78_macro_fed_first_touch_ablation.py`, [successful CI run 38384409037](https://github.com/ataullahturgut/sim3-automation/actions/runs/38384409037), [full output artifact id11804846170](https://github.com/ataullahturgut/sim3-automation/actions/runs/38384409037/artifacts/11804846170), 2024/25/26 all row probabilities + JSON summary. No Neon writes, no canonical overwrite or production merge.

**Final finding:** Yes these drivers should be candidates. However measured simple preissue market/fed-calendar ablation DOES NOT establish incremental edge on the tested dynamic gold first-touch shock. Cannot infer that actual high-frequency Fed surprise matters little: it was NOT part of this test.
