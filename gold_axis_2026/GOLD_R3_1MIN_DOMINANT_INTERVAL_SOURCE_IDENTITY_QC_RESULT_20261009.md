# R3 source-only identity diagnostic: Is a dominant 15-minute price interval actually a one-minute price jump? (2026-10-09)
**Status: ACTUALLY COMPLETED (read-only Neon source audit) / independent source / NO NEW SIGNED MODEL TRAINED / false-jump caution.**

## Why it matters
The modest cross-year positive JDR4 DAY result is based on the maximal **15-minute squared return share** exceeding 50% of previous 4h squared returns. That is a *dominant interval*, not a formal jump, orderbook absorption event or causal dealer liquidity shock. The independent adversarial DeepSeek second opinion `GOLD_DEEPSEEK_JDR4_POST_RESULT_REFEREE_20261009_REVIEW.md` properly rejected the label “jump” for a coarse 15m statistic, citing Bajgrowicz et al, Management Science 2016 DOI10.1287/mnsc.2015.2234. It also rejected treating post-selection nominal p-values and zero-cost signed-return sums as confirmed skill. It did **not** backtest market data.

## Source provenance / original clock
- Approved original quote source: bid+ask XAUUSD M15, one upstream Dukascopy-derived vendor, year2023–25; issue DAY before09 Europe/Istanbul.
- Independent optional research minute close cache: Twelve Data historical `XAU_RESEARCH_TWELVE_1MIN_CACHE_V1`, source ledger shows 41 completed 1m batches (plus one provider-quota-partial batch), historical 2023–Jun2026 rows, first retrieved September 2026; NOT native Dukascopy tick/BID/ASK and NOT a 2023 PIT store. Cache table carries only timestamp and close; source provenance from separate ingestion batch registry. The minute cache is NOT automatically validated for all dates.
- An independent **clock-provenance test** of other fixed source times: 2023/24 16:44-minute-start source close aligns with approved16:30-start M15 close16:45 within median0.21/0.20 basis points; choosing16:45-start minute (a minute AFTER the original anchor) yields larger median2.83/3.03bps, confirming one-minute timestamps describe candle STARTS; 2025 16:44 med1.08bps with 95th 34.45bps vendor divergence. Never assume complete 2025 cross-source interchangeability.

## Pre-outcome audit gate
`GOLD_R3_DOMINANT_INTERVAL_1MIN_SOURCE_AND_JUMP_IDENTITY_PREREG_20261009.md` was written before this cross-frequency analysis. For each original JDR4 DAY **decision changed** versus preissue 4h net direction (2023 N31,2024 N22,2025 N28), find its dominant M15 return index over completed04:45→08:45. Load exactly16 consecutive minute-start CLOSE prices from event interval start-1min through event interval end-1min. Both FIRST and LAST minute-close levels must agree with approved M15 bidask-mid return start/end within 5bps to pass a cross-vendor QC gate (other data never interpolated). Compute:
- `qfrac = max_k (r_1m,k^2) / sum_{k=1..15} (r_1m,k^2)`, not a BNS/Lee–Mykland jump test; `qfrac>=0.5` is only a one-minute concentrated surrogate.
- `eff = abs(sum r_1m)/sum abs(r_1m)` as normalized path smoothness, not direction innovation.

## Real executed source QC
| Year | Original JDR4 DAY changed decisions | Contiguous16 one-minute closes | Both M15 endpoint cross-vendor ≤5bps | Median qfrac on passed | qfrac≥50% among passed | Median minute-path efficiency |
|---|---:|---:|---:|---:|---:|---:|
| 2023 |31|31|31|0.4049|6/31 = 19.35%|0.6826|
| 2024 |22|22|22|0.3457|4/22 = 18.18%|0.6313|
| 2025 inspected |28|23|19|0.3763|6/19 =31.58%|0.5866|

Source completeness: 2023/24 100% on **selected original signal-change events only**; 2025 just19/28 =67.86% source-qualified matched events. 2025 1min endpoint source mismatch has p95 20.5bps among available event bars (not a claim about the whole year). Scope is intentionally 81 decision-change events; no full-population inferred 1min coverage or conditioned performance sign claim.

## Interpretation / failure classification
**Sustained factual outcome:** 2023–24, despite excellent cross-provider endpoint match on original JDR-selected events, only10/53 events (18.87%) satisfy the predeclared one-minute concentrated condition. Therefore a majority of the original 15m “dominant squared return” bars **do NOT manifest as a single concentrated minute**. The older label **JDR4 = jump detector is NOT justified**. It remains a descriptive `DIR4` (Dominant Interval Reversal four-hour) price-path heuristic, without independent signed information. A one-minute bar with qfrac≥0.5 is not automatically a true discontinuous jump either; proper volatility-jump separation and multi-frequency invariance would be a *separate* preregistered method.

- The original small DAY BA improvements (2023/24/25 and 2026 native) survive numerically as **fixed 15m algorithm outputs**, but scientific explanation is not proven. Do NOT retroactively filter only minute-concentrated dates and advertise better BA; sample tiny and source gate poor in2025.
- Reviewer’s universal `REJECT_NOW` for a **jump mechanism** is supported, but concluding the fixed price-path rule must have no effect whatsoever would be more than the evidence shows. Keep only a frozen observational candidate (renamed DIR4), not bank-action champion.
- Independent modern primary literature for high-frequency jump detection: Bajgrowicz, Scaillet, Treccani (2016) DOI10.1287/mnsc.2015.2234; Sobti (2025) gold 5m multi-method jump tests DOI10.1016/j.irfa.2025.104380. Actual XAU orderflow, implied options tails, and independent cross-market 5m source are not magically present.
