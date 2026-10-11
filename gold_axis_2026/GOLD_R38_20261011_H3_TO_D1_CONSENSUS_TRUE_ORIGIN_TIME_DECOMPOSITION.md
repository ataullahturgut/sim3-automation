# R38 — H3 → CIG-D1: first-leg clock and causal decomposition (2026-10-11)

**Binding follow-up to R37.** The user's correction is fundamental: CIG-D1 is **not a separately trained hourly or D1 forecasting model**. It is an ALL-FOUR H3 expert state converted into an issue-day direction. Frozen predictions unchanged; all results retrospective diagnostics and NOT prospective/tradable claims.

## 1. ORIGINAL model definition

Original `gold_axis_2026/tools/gold_short_horizon_global_xau_readiness_r2.py` explicitly creates `feature_cutoff_date=date`, `forecast_issue_date=date.shift(-1)`, `target_r3=log(gold.shift(-3)/gold)`. For issue date D, the original H3 movement begins on **previous governed data date C (previous trading day)** and ends on the **third forward observation after C (usually D+2)**. The CIG-D1 4-of-4 vote is the **same H3 direction**, re-used to score **the first leg C→D**.

Original 2023–25 daily Gold reference StakTrakr source `seed/LBMA` is strongly linked by independent HistData 2023–25 M15 market prices to **London Gold Price AM**, starting **10:30 UK local (13:30 Turkey winter, 12:30 Turkey summer)**. There is no inherent unique hourly price interval trained into the CIG vote. The H3 IRIS hourly **information cutoff is 16:00 America/New_York on C**, not D: typically **Turkey 00:00 next day (NY winter)** or **23:00 same day (NY summer)**. The governed issue deadline is D 08:00 NY (Turkey 16:00 winter /15:00 summer). Historical physical issuance time is NOT recorded.

## 2. Frozen same-218 H3-consensus decisions, original source 2025

Original Stak reference at model pin `54fdf1c8d39b7b6c7b874d0f30f784296e886044`. Exact CIG 218 predictions from `GOLD_OLD_CIG_2025_EXECUTION_TARGET_ROWS_2026-10-07.csv`; none re-trained:

| Reference target STARTS on prior input date C | Correct / 218 | Accuracy |
|---|---:|---:|
| **H1 C→D** (first H3 leg, old CIG-D1) | **176/218** | **80.73%** |
| H2 C→D+1 | 161/218 | 73.85% |
| **H3 C→D+2** (actual original three-observation horizon) | **149/218** | **68.35%** |
| H4 C→D+3 | 142/218 | 65.14% |
| H5 C→D+4 | 138/218 | 63.30% |

This is WHY H3 consensus appeared exceptionally accurate when re-scored on its first one-day leg. Those are original historical target-reference label counts, not after-origin market performance.

## 3. Critical real 15-minute market check: SPLIT first H3 leg at the last input cutoff

Independent archived HistData 2025 native 15-minute market `open_price` in private Neon table `gold_research_histdata_xau15m_candidate`. The source previous day's LBMA AM benchmark is the ORIGINAL Stak provider, not a newly introduced source to guess model target. Every New York and London hour was dynamically translated with SQL `AT TIME ZONE` (UK/US DST calendars accounted for).

**Segment A ALREADY SEEN BY H3**: previous cutoff date C original LBMA AM price → same cutoff date C **16:00 NY** M15 spot.
**Segment B GENUINELY IN FUTURE AT H3 CUTOFF**: C 16:00 NY spot → issue date D **London 10:30 AM** M15 spot.
**Full leg A+B**: C AM original benchmark → D London AM-near spot (provider mix only at first endpoint, existing LBMA first-leg proxy).

Identical subset **211** of the frozen 218 signals with every necessary historical quote and source reference:

| Market interval relative to H3 feature cutoff | CIG direction correct | N | Accuracy | Always UP baseline |
|---|---:|---:|---:|---:|
| **A: BEFORE cutoff (already-realized US-afternoon market move)** | **181** | **211** | **85.78%** | 121/211 |
| **B: AFTER cutoff (next London's morning session)** | **105** | **211** | **49.76%** | **122/211 = 57.82%** |
| A+B entire first-leg price move (cross-provider approximation) | 168 | 211 | 79.62% | — |
| Old exact historical first-leg label, full population | 176 | 218 | 80.73% | — |

Quarter audit, identical available examples per quarter:
- **2025 Jan–Mar** N57: known A 54, true future B 30, full leg 44.
- **Apr–Jun** N49: known 38, future 20, full 34.
- **Jul–Sep** N56: known 43, future 29, full 47.
- **Oct–Dec** N49: known 46, future 26, full 43.
- TOTAL N211, known181, future105, full168. Jan02 has previous original 2024-12-31 LBMA $2610.85, previous NY16 quote $2622.964 and current London10:30 $2644.568; model UP. Other seven original CIG dates lack the required complete matched source quotes.

**Key real example 2025-01-03**: Old CIG predicts UP, and original Stak LBMA 2025-Jan02 $2644.60 → Jan03 $2654.30 = UP, so historical 'correct'. But Jan02 NY16 market price was $2659.455, already UP from Jan02 AM and ALREADY OBSERVED at last input cutoff. From Jan02 NY16 $2659.455 to Jan03 London10:30 market $2656.015 = DOWN, thus the unobserved remaining first-leg move was actually AGAINST the signal. This is a H3 first-leg cutoff-overlap issue; do not call it verified illicit feature leakage.

## 4. Time-of-day descriptive checks

With same frozen 2025 CIG and independently fetched HistData **previous trading day spot same hour → issue day same hour**:
- **03TR: 170/217=78.34%**
- **09TR: 170/218=77.98%**
- **12TR: 171/218=78.44%**
- **13TR: 176/217=81.11%**
- **14TR: 170/218=77.98%**
- **15TR: 168/217=77.42%**

Thus many past-to-issue windows score near 80%; a single 'forecast UP hour' cannot be inferred by maximizing in-sample matches. The **physically supported target endpoint for 2023–25 is LBMA AM, not a hidden optimized hour**.

2026 Jan–Feb frozen LBMA-period CIG original label **18/25=72%**, next-am **13/25=52%**. On 23 independent Dukascopy quote-matched pairs, original **C NY16→D London10:30** forward segment: **15/23 = 65.22%**, exactly equal to always-UP 15/23. Mixed-provider full 2026 should not be treated as one source clock.

## 5. Governing conclusion

The user was correct to insist this is a **3-day H3 model's consensus collapsed to the FIRST DAY**. Old CIG 80.73% was **not** a time-invariant or physically released D1 prediction. The model agreed even more (85.78%) with the ALREADY OBSERVED price component in the first leg by the last H3 input cutoff, but only 49.76% with the genuinely future component, on 211 identical dates. A precise trained intraday prediction hour **does not exist** in old CIG model; only original provider benchmark and issue/cutoff times can be inferred. The old model should not be discarded as a H3 state estimator; however 74.4%/80.73% must not be marketed as prospective executable one-day direction skill.

Original author sources: `gold_short_horizon_global_xau_readiness_r2.py`, `gold_h3_iris_v1.py`, `GOLD_D1_CIG_V1_RESULT_2026-10-05.md`, `GOLD_R36_20261011_ORIGINAL_CIG_PLATFORM_CLOCK_SOURCE_RESULT.md`, `GOLD_R37_20261011_CIG_D1_ORIGINAL_LBMA_AM_CLOCK_AND_CAUSAL_FORWARD_VERDICT.md`. No model, predictions or historic forecasts were modified.
