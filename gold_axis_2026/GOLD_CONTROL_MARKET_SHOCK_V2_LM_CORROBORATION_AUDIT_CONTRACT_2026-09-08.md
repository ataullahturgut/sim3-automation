# GOLD CONTROL — MARKET SHOCK V2 LM CORROBORATION AUDIT CONTRACT

**Date:** 2026-09-08  
**Status:** `PRE-REGISTERED / 2026 HISTORICAL CORROBORATION / RESEARCH ONLY`  
**Model under audit:** `GOLD_CONTROL_MARKET_SHOCK_CHALLENGER_V2`  
**Primary question:** Are the many 2026 LM 5-minute alarms genuine volatility-adjusted jumps or largely uncorroborated noise?

## 1. Why the previous 0.50% proxy is insufficient

The prior realized-move proxy audit deliberately used a frozen absolute 0.50% floor and failed. That result is retained. It is not rewritten.

However, an absolute raw-return threshold is not a sufficient scientific definition of a Lee–Mykland jump. Lee–Mykland is a volatility-standardized jump test. Boudt, Croux & Laurent (2011, Journal of Empirical Finance, DOI 10.1016/j.jempfin.2010.11.005) show that robust intraday periodicity adjustment increases power for relatively small jumps occurring in low-periodic-volatility intervals and reduces spurious detections during high-periodic-volatility intervals.

Dumitru & Urga (2012, Journal of Business & Economic Statistics, DOI 10.1080/07350015.2012.663250) report strong performance for ABD/LM intraday procedures and explicitly motivate combining tests and sampling frequencies to reduce spurious jumps.

Sobti (2025, International Review of Financial Analysis, DOI 10.1016/j.irfa.2025.104380) studies intraday gold jumps using Lee–Mykland as the main detector, Andersen et al. as a robustness method, Boudt WSD periodicity, and alternative 1/3/5/10-minute frequencies and significance levels to avoid spurious/fake jump detection.

Therefore this audit changes the validation question, not the V2 model parameters: **does an LM5 episode receive corroboration from another jump methodology and/or another sampling frequency?**

## 2. Frozen 2026 data scope

- production Neon research cache: `xau_intraday_research_cache_5m`
- complete 5-minute history: 482,734 rows
- full Market Shock 2026 holdout: 2026-01-01 through 2026-08-31
- model fit remains walk-forward: all 2026 detector parameters are estimated only from data before 2026-01-01 unless a confirmatory statistic is explicitly ex-post and labelled as such.

## 3. Primary V2 signals remain unchanged

- LM5 uses current corrected Lee–Mykland V2 formula and frozen alpha = 0.001.
- EVT30 uses current frozen V2 EVT implementation.
- V2 remains `LM5 OR EVT30` for this audit. No production/runtime change is made.

## 4. Corroboration channel A — ABD/WSD 5-minute ex-post test

Implement an Andersen–Bollerslev–Dobrev-style intraday standardized-return confirmation on the same 5-minute holdout, using:

- Boudt-style WSD periodicity fitted only on pre-2026 data;
- per-session continuous variance estimated with jump-robust tripower variation (TPV);
- session = existing 17:00 New York convention bucket, explicitly `EX_POST_RESEARCH_ONLY` because the exact provider session calendar remains unresolved;
- family-wise alpha = 0.001 per session with Šidák multiple-testing correction;
- an LM5 episode is ABD-confirmed if an ABD signal occurs on an LM signal bar in the episode or within one adjacent 5-minute bar.

This channel is a robustness test, not a live vote and not a production rule.

## 5. Corroboration channel B — LM10 cross-frequency test

Construct a deterministic 10-minute series from the 5-minute cache using the last close in each 10-minute UTC bin.

- preserve the current 5-minute LM temporal bandwidth: `K5=270` bars × 5 min = 1,350 minutes; therefore `K10=135` bars × 10 min = 1,350 minutes;
- use `N_INTRADAY_10M=144`;
- alpha remains 0.001;
- fit 10-minute WSD periodicity only on pre-2026 data;
- reject any 10-minute return spanning >15 minutes;
- an LM5 episode is LM10-confirmed if an LM10 signal timestamp falls within ±10 minutes of any LM5 signal timestamp in that episode.

This channel is a sampling-frequency robustness test; it is not called an independent statistical family.

## 6. Corroboration channel C — existing EVT30

An LM5 episode is EVT-confirmed when the same V2 episode contains an EVT30 signal. EVT30 is an independently fitted extreme-value fast-move detector on a different horizon, but it still uses the same underlying price series.

## 7. Secondary evidence — BNS day jump

Report whether each LM5 episode falls in a 17:00 New York bucket that is BNS-significant at the existing 99.9% level. Because this is day-level and ex-post, BNS support is **secondary only** and cannot by itself upgrade an LM episode to primary corroborated status.

## 8. Frozen episode classifications

For every 2026 V2 episode containing LM5:

- `MULTI_METHOD_STRONG`: at least two of {ABD5, LM10, EVT30} corroborate;
- `CORROBORATED`: at least one of {ABD5, LM10, EVT30} corroborates;
- `LM_ONLY_UNCORROBORATED`: none of {ABD5, LM10, EVT30} corroborate.

BNS is reported separately.

## 9. Pre-registered diagnostic outputs

Report:

- total V2 and LM-containing episodes;
- ABD5, LM10, EVT30 and BNS corroboration counts;
- `CORROBORATED` and `LM_ONLY_UNCORROBORATED` counts/rates;
- corroboration by UP/DOWN direction;
- raw 0.50% proxy support inside each corroboration tier (diagnostic only);
- median and quantiles of raw 5-minute move by tier;
- current V2 2026 alarm rate unchanged;
- a **research candidate diagnostic**, not a model change: `EVT30 OR (LM5 AND (ABD5 OR LM10))`; report its signal/episode rate and its old 0.50% proxy support.

## 10. Interpretation rules frozen before output

- The old 0.50% proxy FAIL remains valid as an economic-magnitude diagnostic.
- `LM_ONLY_UNCORROBORATED` is not automatically a false positive; it is an **unconfirmed LM event**.
- `CORROBORATED` is stronger statistical evidence but still not authoritative ground truth.
- No threshold is retuned from these results.
- No V2/V2.1 runtime replacement is authorized by this audit alone.
- If corroboration is weak, investigate LM/noise specification before any model promotion.
- If corroboration is strong and the candidate diagnostic materially improves alarm quality without destroying large-shock power, a separate pre-registered V2.1 challenger test may be opened.

## 11. Governance

`prospective_claim = false`  
`authoritative_false_positive_rate = NOT_PROVEN`  
`production_promotion = BLOCKED_RESEARCH_ONLY`  
`canonical_merge = NOT_AUTHORIZED`  
`production_neon_write = NONE`

## 12. Execution record — 2026

Workflow run `34205666369` completed successfully on commit `7e6474840aae0608c7e2f9f36ed2933f51021409`.

Observed 2026 LM corroboration:

- LM-containing episodes: `381`;
- ABD5 confirmed: `178`;
- LM10 confirmed: `220`;
- EVT30 confirmed: `46`;
- BNS-day secondary support: `58`;
- at least one primary corroboration: `300 / 381 = 0.7874015748`;
- multi-method strong (at least two of ABD5/LM10/EVT30): `129 / 381 = 0.3385826772`;
- LM-only uncorroborated: `81 / 381 = 0.2125984252`.

Raw 0.50% diagnostic by tier:

- `MULTI_METHOD_STRONG`: 69/129 supported = `0.5348837209`; median absolute 5-minute raw move `0.0042848885`; p90 `0.0118897707`;
- `CORROBORATED` with exactly one primary corroboration: 23/171 supported = `0.1345029240`; median absolute 5-minute raw move `0.0025260029`;
- `LM_ONLY_UNCORROBORATED`: 10/81 supported = `0.1234567901`; median absolute 5-minute raw move `0.0021260992`.

Research-only filter diagnostic `EVT30 OR (LM5 AND (ABD5 OR LM10))`:

- baseline V2 signal bars: `578`, rate `0.0102784792`;
- filtered diagnostic signal bars: `488`, rate `0.0086780240`;
- filtered diagnostic episodes: `304`;
- old raw-0.50% proxy precision: `0.3125` versus baseline `0.2727272727`.

Interpretation:

- evidence does **not** support the claim that most LM episodes are random/noise; 78.7% receive at least one primary corroboration;
- evidence does support a quality gradient: multi-method-strong events are materially larger and much more likely to satisfy the old 0.50% economic-magnitude proxy;
- 21.3% remain LM-only uncorroborated and require a dedicated higher-frequency/noise audit before they can be classified;
- the filter diagnostic lowers the historical signal rate below the frozen 1% rate gate, but it contains an ex-post ABD component and therefore is **not a production-eligible live rule**;
- authoritative false-positive rate remains `NOT_PROVEN`.

Next scientific step is restricted to 2026: use the complete common-support 1-minute cache through 2026-05 to perform 1/3/5/10-minute LM frequency-stability analysis, focused especially on the LM-only-unccorroborated class. No 2025 audit is authorized until this 2026 question is resolved.
