# R69 — How to use the successful native H3 forecast efficiently at Turkish bank clocks

**Date 2026-10-12 — FINISHED EXPERIMENTS, NO UNJUSTIFIED STRATEGY PROMOTION.**
**User's actual question:** Existing native H3 was reproduced (old HELIOS 931/931 and old DPTC Q95 191/191; old 2026 135/191) but forecasts reference D0→D3 gold *UTC daily means*. Can a bank user place a trade between **09:00 and 17:00 Europe/Istanbul** and exploit that native signal? Test execution target *rather than continuing clock audits*.

## 1. Source, chronology and experiment identities

- Parent source/version: R60 holiday-corrected COT as-of, R61 monthly trained OPAL, R62 endogenous HELIOS 931-row replay, R63 191-row 2026 DPTC; these are **historical/controlled retrospective** identities, not genuine forward deployment evidence.
- **R66** newly trains *three separate exact-clock H3 price targets* (09,15,16:45 TR quote at issue origin → same clock on native H3's D3 calendar date), using the original H3 prediction as one forecast feature, instead of copying native daily-mean outcome labels. Source: Neon `gold_research_histdata_xau15m_candidate` M15 OPEN spot, consistent within origin/target. Filter source completeness >=70 local 15min candles for entry/target and >=70 D0 UTC source M15 average candles. 09 morning uses **previous available H3 issue** (never same day's late signal), which shortens remaining time to original D3, explicitly disclosed. 15:00 and16:45 use same-day H3 signal, with actual historic `issued_at` / firstprint unknown: they are **research scenario**, not certified live ability.
- Ridge: 2023–24 development only, L2 20, forecast source-D0→same-clock-D3 log return with signed H3 prior, H3 confidence, already observed prior-anchor return and pre-origin session return, subtract known `log(entry_price/P_D0avg)` to forecast remaining expected move. Logistic: 2023–24 development only, class-balanced L2 10 with H3 direction/probability, source entry gap, last-anchor momentum, preorigin path. Evaluate unchanged 2025/26. Refit code in current connector was independent JavaScript; numerical sklearn parity not claimed.
- **R67** separate day/overnight trained 2023–24 DAY09→16:45 and OVN16:45→next calendar09 (excludes Fri weekend), treating H3 as auxiliary input. 09 always previous H3 issue. 15 minute underlying source HistData.
- **R68** sequential long/flat spot-proxy capital-use check, one position max, skip all H3/other signals while old position still open, exits at D3 **same clock**. No shorting, no overlapping compounding. Flat capital assumed zero interest; exits and fills assume ideal exact market quote. Hypothetical fixed total round-trip costs 10,25,50 bp. **Not real bank ASK/BID and not executable net return**.

## 2. Actual exact-clock 3-source-day direction — R66

All results below use 2023–24 for training, 2025/2026 unchanged; the old H3 is one expert. Same target and same eligible rows *within each hour/year*.

| Origin | 2025 eligible | Native H3 direction 2025 | Newly fitted direct logistic 2025 | 2026 eligible | Native H3 direction 2026 | New direct logistic 2026 |
|---|---:|---:|---:|---:|---:|---:|
| **09:00**, previous H3 issue | 247 | **127/247=51.42%** | **125/247=50.61%** | 185 | **95/185=51.35%** | **96/185=51.89%** |
| **15:00**, same-day H3 hypothetical readiness | 247 | **120/247=48.58%** | **128/247=51.82%** | 186 | **101/186=54.30%** | **95/186=51.08%** |
| **16:45**, same-day H3 | 247 | **123/247=49.80%** | **124/247=50.20%** | 186 | **105/186=56.45%** | **106/186=56.99%** |

Small numerical rebase regression R66 *did not beat* the direct logistics or unchanged H3 consistently; e.g. 16:45 regression exact-clock 2025 **128/247=51.82%**, 2026 **90/186=48.39%**. Applying an origin gap >1% as a "don't trade" gate also is not robust: 16:45 2025 **88/186=47.31%**, 2026 **73/123=59.35%** on its eligible subset. It must **NOT** be promoted based on 2026-only gain.

Always-UP class prevalence changed materially: 16:45 2025 **144/247=58.30%**, 2026 **88/186=47.31%**; compare to class base rates, not just raw 50%.

## 3. Exact user-executable DAILY vs OVERNIGHT H3-conditioning — R67

| Window (no PnL) | Period | Matched days | H3-only correct | Development-fitted 4-feature logistic correct | Always-UP |
|---|---|---:|---:|---:|---:|
| DAY 09→16:45 | 2025 | 248 | 119/248 | **110/248=44.35%** | 138/248 |
| DAY 09→16:45 | 2026 | 190 | 79/190 | **100/190=52.63%** | 98/190 |
| OVN 16:45→next09 (calendar next day only) | 2025 | 196 | 98/196 | **92/196=46.94%** | 109/196 |
| OVN 16:45→next09 | 2026 | 150 | 77/150 | **74/150=49.33%** | 69/150 |

No robust time-window-specialist edge was established. **The overnight risk still exists and is frequently larger than DAY**, but forecasting overnight direction via the old H3 signal is not enough. Friday/weekend is a separate risk class excluded from this overnight label, not silently counted as Friday→Monday “one night”.

## 4. Non-overlapping long/flat strategy proxy — R68

One position at a time; actual target is the source D3 same-clock quote. No simultaneous reinvestment across overlapping rolling H3 signals. All figures below **hypothetical** ideal source-price compounded percentage after **25bp constant total roundtrip cost** deducted once per executed round trip, NOT investor bank realised return or portfolio trade advice. Figures at different origins cannot be combined as if independent.

| Decision clock | Strategy | 2025 positions | 2025 proxy 25bp net | 2026 Jan–Sep positions | 2026 proxy 25bp net |
|---|---|---:|---:|---:|---:|
| 09 | existing H3 UP→buy | 97 | **−7.56%** | 55 | **−10.34%** |
| 09 | new exact-clock logistic UP→buy | 96 | **−13.25%** | 59 | **−5.17%** |
| 15 | existing H3 UP→buy | 71 | **+5.80%** | 44 | **−5.68%** |
| 15 | new exact-clock logistic UP→buy | 70 | **+12.59%** | 44 | **−21.74%** |
| **16:45** | existing H3 UP→buy | 71 | **+7.39%** | 44 | **−5.15%** |
| **16:45** | new exact-clock logistic UP→buy | 70 | **+9.84%** | 45 | **−8.09%** |
| **16:45** | deterministic enter-every-eligible-day (no predictor) | 83 | **−17.09%** | 63 | **+0.43%** |

Additional sensitivity: at 16:45 existing H3 2025 with 50bp total round trip **−10.07%** and 2026 **−15.03%**; new logistic **−7.80%** and **−17.87%** respectively. 2025 period continuously holding spot first→last quote rose approximately **+64.19%**, so positive 2025 selective strategies were **not** better than simple passive exposure on that broad window. 2026 passive first→last source quote fell ~**−2.30%** (not an identical invested-span or capital utilization benchmark). Observed price-path timing gives deterministic always-enter benchmark different results from passive.

No strategy's net proxy is *consistently attractive across 2025 and 2026* on this conservative 25bp illustrative cost. Some 2026 selected cells can look high with N<10; e.g. 09 high confidence 7 trades after 25bp +3.86% **but 2025 counterpart seven trades −5.27%** — sparse, unreplicated and not to be promoted.

Full source ledgers:
- `GOLD_R66_20261012_H3_09_CARRY_15_1645_EXECUTION_TARGET_MODELS_ALLROWS.csv` and same-prefix summary JSON;
- `GOLD_R67_20261012_H3_AS_DAY_AND_OVN_CONDITIONER_2023_2026_ROWS.csv` and summary;
- `GOLD_R68_20261012_H3_BANK_ORIGIN_NONOVERLAP_LONGFLAT_TRADES.csv`, `...STRATEGY_METRICS.csv`, `...SUMMARY.json`.

## 5. The practical decision, now

1. **Keep successful original H3 strictly as an indication of D0→D3 daily-average direction and a broad model-state/expert feature.** Do not market 135/191 or 130/191 as a profitable entry-clock success rate, and do not turn daily alerts automatically into bank purchases.
2. **Clock duties:** before **09:00** only last fully issued H3 (previous issue, sometimes a shorter remaining horizon); **15:00** same-day update only with observable issue timestamp and ready inputs (08NY = 16TR during EST, so historical use at15 all year is invalid); **16:45** main last-bank opportunity and overnight risk decision only when data complete, broker quote/spread acceptable. A Friday 16:45 reference can't use CFTC 15:30 NY Friday report.
3. **Do not chase every UP/DOWN reversal** with the bank: high turnover + spread overwhelms small directional advantages. Without contemporaneous **bank ASK on purchase and BID on sale**, transaction profit is unverified. Even 10bp/25bp cost sensitivity is a scenario, not actual fee data.
4. **Only defensible conditional use today:** use H3 as a **coarse multi-day context/watchlist**, not an order generator. A positive H3 can warrant a *separately verified entry-clock forecast*; a negative H3 can warrant *risk review*, not automatic liquidation. Build the bank-specific execution/price model first and validate strictly matched **same-time third-day target**, realistic spread and 2023–24 preregistered development. Compare to always hold/cash, zero-alpha and existing session models on the *same date coverage*. If no skill above a naive benchmark, abstain from active switching. 
5. **Next genuinely useful technical development (not a new clock audit):** target-specific conditional **quantile / distributional return** for `P_target_exact_clock / P_entry_bidask` using origin-known H3 **probability as one feature**, prior session path, already released macro calendar, volatility/jump state, USD/2yr US rates if asof-safe. Optimize abstention relative to actual *roundtrip spread*, predefine thresholds on 2023–24 only, then 2025/26 transport unchanged. Weekly H3 position decisions must be modeled separately from DAY and overnight. In parallel collect actual bank BID/ASK source timestamps, order fill lag and venue rules. No outcome-based retrospective selection of clock, gap threshold or regime split.
6. **Stopping condition:** do not approve a live execution rule merely because the native H3 still scores 70% on its original daily-average label. Require meaningful forward or untouched comparable holdout improvement in **bank-clock price target** and after-spread position capture; preserve the original H3 research model and avoid duplicate retrospective revalidations.

**Evidence qualification:** R66–R68 were genuinely calculated from connected Neon read-only SQL source rows and repository model predictions inside independent JavaScript, then committed to GitHub. Exact sklearn implementation/parity and true archived H3 generated_at/market-price firstprint are not established. 2025/2026 have already been repeatedly inspected in project development and are **retrospective transports**, not statistically untouched lockboxes. Results prove a lack of reliable **demonstrated** practical edge, not that no possible future bank-aligned H3 model can work.

**Takeaway:** We know *why* the successful native H3 result did not transfer: target origins and price semantics differ, and economically relevant night moves/spreads dominate small edges. We trained bank-origin H3 and DAY/OVN challengers, scored them, and tested non-overlap cost-sensitive long/flat returns. **No empirically robust bank-executable successor is proven. Preserve the old H3, do not promote an active strategy from its native 70%.**
