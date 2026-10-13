# GOLD JANUARY 2026 SCIENTIFIC SUCCESSOR — 3-STAGE CROSS-YEAR VERDICT
**Research date:** 2026-10-13. **Status:** experimental; no model or bank order approved for live use.
**GitHub:** `ataullahturgut/sim3-automation`, research branch `research-gold-jan26-scientific-successor-20261013`, based on remote main-working `gold-execution-channel-audit-20261006` HEAD `45aed5751b69186a3474a947039b24e94b14505a` at branch creation. **Canonical manifest** amended on this separate branch; no existing PR#123 forecast rewritten. Related previous empirical 31-day record in open PR#123.

## 1. Why another study
PR#123 sequential Jan-2026 B0 held GOLD from Jan7 entry 4497.265 until Jan30 close, 29 Jan high→subsequent low **−8.899%** hidden by close-to-close **−0.660%**; day30 B0 SAT after a large decline (Jan30 close 4891.195), sale unexecuted in January. Jan31 end mark +7.889% after buy fee, before sale, **+7.026%** if *hypothetically* haircut by 0.8% sale fee on final close (not a possible signal-time fill). 2026 events have long been researched; there is NO untouched OOS for January. Jan intraday anomaly cannot be freely back-fitted to produce a claimed future predictive model.

## 2. Frozen hypothesis families and sequence
- **Stage A:** `GOLD_JAN2026_SCIENTIFIC_SUCCESSOR_FROZEN_DEV_VALIDATION_PROTOCOL_20261013.md`. B0 legacy daily r3/r5/r20/SMA10 exit/entry plus alternative end-of-session ordered intra-day high→subsequent low drawdown cutoffs −2%, −3%, −4%, −5%. Three eligible-session cooldown after **shock-triggered** exit (not the baseline exit).
- **Stage B:** `GOLD_JAN2026_STAGE_B_SLOW_REGIME_CANDIDATES_FROZEN_20261013.md`. Formulated AFTER stage A's 2023/24 DEV finding of high churn; fixed independent family of SMA20/60 hysteresis, SMA50, 20-day trend, 60-day trend, and trail-60 slow exits. 5 eligible-session cooldown after any exit. This DEV reuse is **exploratory**, not confirmatory. Select only from 2023+2024 conditions; look at 2025 only AFTER choice; Jan2026 stress LAST.
- **Stage C:** `GOLD_JAN2026_STAGE_C_SLOW_TREND_SHOCK_COMBINATION_FROZEN_20261013.md`. Combine stage-B-selected 60d trend with end-of-day intraday drawdown −3/−4/−5. Study occurs AFTER learning Jan26 crash and is highly selection-sensitive; no favorable Jan result can authorize a model unless 2023/24 and 2025 gates pass.

All calculations from `EV` Dukascopy 2022 warmup+2023–25 bid/ask midpoint M15 and `HIST` 2025Sep–Dec warmup+Jan26 HistData 15min. Correct NY17 **bar ending at 17NY belongs to preceding session**; weekdays >=70 bars; Jan19 early close included as observed short session. Each day uses only already completed <=t bars. Cash initial each calendar cohort; one GOLD/CASH position, no short or leverage, next eligible session's FIRST completed M15 quote as research fill; **0.8% on each buy and sale**, bid-ask bank spreads and slippage NOT available. End-year still-long portfolios converted into *hypothetical* net-liquidation NAV by additional 0.8% haircut, not a contemporaneous bank fill. Historical quote receipts and cross-market 2026 PIT provenance unverified. Same calculation for passive comparator entering first NEXT eligible session and hypothetically selling at last close.

## 3. Results: cost-adjusted return % by annual cohort

| Family / policy | 2023 DEV | 2024 DEV | 2025 exploratory VALIDATION | Jan2026 prior-exposed stress |
|---|---:|---:|---:|---:|
| B0 ORIGINAL, close-only daily | -3.64 | -12.47 | +2.09 | +7.03 |
| Always-GOLD same-clock passive | +10.41 | +25.43 | +59.90 | +10.15 |
| Stage A B1 shock -2% plus B0 | -0.14 | -17.67 | -3.89 | +8.70 |
| Stage A B2 shock -3% plus B0 | -3.64 | -14.44 | +9.27 | +18.63 |
| Stage A B3 shock -4% plus B0 | -3.64 | -14.44 | +5.58 | +18.63 |
| Stage A B4 shock -5% plus B0 | -3.64 | -12.47 | +2.09 | +18.63 |
| **Stage B S4 60-session r60 trend** | **+6.00** | **+15.09** | **+41.17** | **+10.15** |
| Stage C S4 + session intra DD <=-3% | +6.87 | +8.55 | +37.42 | +22.09 |
| Stage C S4 + intra DD <=-4% | +6.87 | +11.97 | +45.76 | +22.09 |
| Stage C S4 + intra DD <=-5% | +6.87 | +15.09 | +46.02 | +22.09 |

**Scale caveat:** Stages B/C start with CASH at each year's first eligible date and compute >=20/60 last-date trend from prior-year historical series. S4 Jan enters at an EARLIER DATE than B0 Jan, so +10.15 vs B0 +7.03 does not isolate trading exit effectiveness. "Always-GOLD" is matched first eligible next quote, not a Turkish bank fill. Exposure, transaction counts, daily marked NAV drawdown and every next-quote action in JSON evidence.
**2023–2025** EV same source; **Jan2026** different HistData source. Direct Jan Duk comparison PR#123 average close difference 0.0218%, max 0.0908% on 18 paired days but irregular quote coverage and actual bank prices unverified.

## 4. Frozen gates and what passed / failed
**Stage A = REJECTED (no DEV winner).** −2% shock exit improved DEV2023 by 3.50pp but harmed DEV2024 by 5.20pp and triggered 30 paid actions in 2024 vs B0 26. −3/−4% harmed DEV2024 by 1.97pp and 2023 unchanged. −5% made NO improvement in either year. Jan26 +18.63 from -3% vs original +7.03 is a *post-seen example*, not evidence of stable early SELL. 2025 +9.27 for stage A -3% is ineligible because DEV gate already failed.

**Stage B = exploratory S4 CHOSEN on DEV 2023–24**. S4 low turnover (3 paid orders in 2023, 4 in 2024; vs B0 17 and 26); conditional 60d sign/risk proxy, AL if r60>=+2%, SAT if r60<=−2%, 5 session cooldown. DEV S4 beats B0 by +9.64pp (2023) and +27.56pp (2024), with LESS maximum end-session NAV drawdown by 2.38pp/7.51pp. Stage-B S5 also passes DEV but smaller worst improvement. Provisional 2025 check S4 +41.17 vs B0 +2.09, max end-session NAV DD ~−10.06% vs B0 −26.31%. **Despite this, S4 underperformed buy-and-hold in all three years, and Jan2026 Jan30 crash was NOT caught** (portfolio MDD −9.666%, same large 2026 liquidation). Stage B created after looking at Stage A DEV, and prior 2025 outcomes known from other gold projects: 2025 is only a *quasi-validation*, not a virgin OOS. Thus S4 = **experimental reference/regime gate**, not live AL/SAT rule.

**Stage C = REJECTED (no DEV 2023+2024 improvement)**. For S4+intraday DD<=-3%, DEV2023 +0.87pp but DEV2024 −6.54pp. At -4%, DEV2023 +0.87pp, DEV2024 −3.13pp. At -5%, DEV2023 +0.87pp, DEV2024 unchanged. 2025 results 37.42/45.76/46.02, versus S4 41.17. **Jan2026 +22.09** for each of -3/-4/-5 because all exit from Jan29 shock at first quote of Jan30, *before Jan30 plunge in quotes*; this is an **already underway shock response**, NOT pre-Jan29 event forecast. The 2024 null/worse results force NO_PROMOTION. Daily stress Jan MDD is ~-0.84%, but actual intraday exposure before Jan29 close can incur larger drawdown.

## 5. Scientific interpretation
- Stronger past gold trend over 60 eligible NY17 sessions appears more economically useful for *position state* than high-turnover short 3-day stop gates in this particular retrospective research; literature's "time-series momentum" is broad but cross-asset studies DO NOT validate our own XAU bank strategy: Moskowitz, Ooi & Pedersen, *Journal of Financial Economics* 104(2), 2012, doi:10.1016/j.jfineco.2011.11.003.
- The sharp Jan2026 intraday shock proves a close-only signal can hide intraday market risk. It does not prove any simple peak-to-low threshold predicts subsequent market collapse; for EV 2023–25 shock dates with >=3% ordered intra DD, immediate next NY17 <=-3% closing drop count previously 0/21 in PR#123. Mechanism study needs gold↔silver joined time-safe 15m, independent liquidity/tariff headlines and true original publication minute, plus non-event controls.
- Multiple backtest comparisons can overfit even when a prior development/holdout split is used. Bailey et al., *The Probability of Backtest Overfitting*, J Computational Finance 2017, DOI 10.21314/JCF.2016.322. We deliberately **refuse to declare a Jan-winning shock rule validated** based solely on January returns.
- Stage B is NOT a causally identified economic model, trained machine-learning network, deep learning or hedge. It is prewritten time-series threshold rule with development-year selection, retro data, different January price source, no bank bid/ask and no true untouched out-of-time year. No new 2026 future forecasts or executions.

## 6. Artifacts and rerun
- Canonical manifest `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`: January failure evidence and nonpromotional testing governance added on this research branch.
- Stage A `GOLD_JAN2026_SCIENTIFIC_SUCCESSOR_FROZEN_DEV_VALIDATION_PROTOCOL_20261013.md` and `GOLD_JAN2026_SCIENTIFIC_SUCCESSOR_CROSSYEAR_OUTCOMES_20261013.json`.
- Stage B `GOLD_JAN2026_STAGE_B_SLOW_REGIME_CANDIDATES_FROZEN_20261013.md` and `GOLD_JAN2026_STAGE_B_SLOW_REGIME_CROSSYEAR_RESULTS_20261013.json`.
- Stage C `GOLD_JAN2026_STAGE_C_SLOW_TREND_SHOCK_COMBINATION_FROZEN_20261013.md` and `GOLD_JAN2026_STAGE_C_REGIME_SHOCK_COMBINATION_RESULTS_20261013.json`.
- `GOLD_JAN2026_SCIENTIFIC_SUCCESSOR_DERIVED_DAILY_FEATURE_INPUT_20261013.csv`: 1,139 source-days in EV 2022–25 + HIST late25/Jan26 normalized *ratios*, ordered intraday DD and session bars; spot prices not republished.
- `GOLD_JAN2026_SCIENTIFIC_SUCCESSOR_REPRODUCE_20261013.py`: Python stdlib standalone A/B/C policy replayer and assertions against saved JSON figures; run locally for independent repeat. `GOLD_JAN2026_SCIENTIFIC_SUCCESSOR_UPSTREAM_SQL_20261013.sql` upstream Neon SELECT source definition.

## 7. Recommended next science stage
**Do not promote S4 or shock hybrids to bank trade execution yet**; use S4 as low-turnover baseline. Reconcile exact 15m quote timing across EV and HIST in 2024–26 and bank ASK/BID historical or live logged quotes in Türkiye 09:00–17:00, including gap risk. Expand **independent pre-announced-period** mechanism studies for (a) options/positioning/physical premium distress, (b) spot-gold vs silver/platinum synchronous 15m liquidity unwind, and (c) Fed policy surprise vs information effect. Build hazard classifier on beginning-of-day fully PIT variables with verified news UTC, include **quiet/no-event controls** and report nonoverlapping episode-wise confidence; compare price-only S4+always-GOLD reference. No 2026-tuned parameter selection, no fund deployment or alpha claim. It is scientifically acceptable if improved exit cannot be validated.
