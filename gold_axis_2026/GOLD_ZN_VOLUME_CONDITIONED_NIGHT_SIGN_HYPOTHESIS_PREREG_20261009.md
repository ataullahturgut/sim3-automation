# ZN-VPT: Treasury volume-conditioned signed price-transmission study — 2026-10-09
**STATUS: GPT-6 ORIGINAL PRE-RESULT HYPOTHESIS / DESIGN ONLY / CRITICISM REQUIRED / NOT YET A PROVEN MODEL**
**Execution target:** XAUUSD overnight 17:00 Europe/Istanbul → NEXT ELIGIBLE 09:00; normal weekday nights ONLY. Target sign of same-source BID/ASK mid log return. No bank execution P&L; DAY remains separate.

## Hypothesis and literature
A burst of trade participation in US 10-year Treasury futures (CME ZN, **price up = approximate long-duration yield pressure down**) *before the Istanbul 17:00 decision* may indicate a macro-rate-driven price-discovery innovation not yet incorporated into spot XAU. A high-trading-volume ZN impulse **disagreeing with contemporaneous XAU** should have higher probability of XAU subsequently resolving in the ZN direction than an otherwise identical low-volume impulse. This is specifically a **volume × signed bond-return × contemporaneous gold disagreement** effect, NOT a claim that trading volume alone is signed or that futures price equals the level of the 10Y interest rate. Motivating literature:
- Hauptfleisch, Putniņš, Lucey (2016), DOI 10.1002/fut.21775 gold spot vs NY futures venue price discovery; does NOT directly establish Treasury-led Istanbul 17→09 gold alpha.
- Elder, Miao, Ramchander (2012), DOI 10.1016/j.jbankfin.2011.06.007 macro surprises have directional gold impact, with transmission to rates; not a pre-origin historical guarantee.
- Sobti, Sehgal, Ilango (2021), DOI 10.1016/j.irfa.2021.101893 gold intraday price-discovery information leadership depends on US data and regimes.
- Gold high-frequency TAQ order imbalance is predictive for jumps in Sobti (2025) DOI 10.1016/j.irfa.2025.104380, but ZN total OHLCV is NOT signed order flow, and ZN volume may just be volatility.

## Identifiable source fields / exact clock
Existing vetted research datasets: one-vendor EVTradingLabs/Dukascopy-derived XAU 2020–2025 M15 BID/ASK, frozen same-source night targets; Databento CME GLBX.MDP3 `ZN.c.0` 1H continuous (2023–Oct2026), `volume`, `instrument_id`, `ts_event`, `close`.
- For origin date `d`, use ZN hour-start local **14:00 and 15:00** bars only; they end at 15:00 and 16:00 and last is treated available only after 16:15 local. Require BOTH OHLCV records and same `instrument_id` (no cross-roll), positive volume and valid prices.
- Spot control `rX` log(mid at16:00/mid at15:00), where local M15 bars starting 15:45 and14:45 close 16:00 and15:00. They end BEFORE the 16:45 operational cutoff. No completed 16:45 start bar and no future midnight quote condition.
- Signed ZN 15→16 return `rZ=log(close(ZN 15-start)/close(ZN 14-start))`, do not bridge a contract roll.
- Trading participation surprise `v=log(volume(ZN 15-start)/median(volume(ZN same 15-local-hour in PRIOR 20 qualified days)))`. Prior 20 must be available before issue, no current/future volume in baseline, never impute missing zero. Test source-specific trading-day DST/holiday and continuous contract QC before any score.
- Ex-ante sign disagreement `D=1[sign(rZ)≠sign(rX)]`; high volume `H=1[v>log(1.5)]`; candidate prediction ONLY on D=1,H=1: UP if rZ>0, DOWN if rZ<0. These are **frozen mechanistic priors, NOT selected on 2025**; volume cutoff is a research hypothesis, not empirically optimal. Abstain elsewhere. In low-volume disagreement D=1,H=0, test as negative-control matched conditional cohort.
- Null: conditioning on `rX`, `rZ`, |rZ|, day/DST state, the interaction `D×v×sign(rZ)` has **no incremental ability** to predict the overnight endpoint. The claimed *sign* is learnable only if positive association appears in both development years and holds in later retrospective test; do not reverse sign based on 2025/26 outcomes.
- No new model needed if source fails; simple signed decision plus a development-only low-parameter interaction likelihood model could be secondary, NOT generic classifier optimization.

## Genuinely run source-readiness screening before seeing new model scores
Read-only Neon query on `gold_research_evduka_xau_session_target_candidate_v1` joined to native ZN 14/15 hour starts, same contract and positive volume, normal weekday night:
2023 **173/198** nights, 73 DOWN in ZN-ready subset; 2024 **175/198**, 75 DOWN; 2025 **178/198**, 76 DOWN. These are *coverage/base rates only*, not model accuracy or proof of past-close PIT.
No ZN prior-20 baseline or candidate predictions computed yet, so a **source-time validation** and downstream score are still due.

## Mandatory novelty/duplication audit
- Manifest's **CAVS** proposed GC-vs-spot venue synchronization, possible GC volume but status **untrained**. Present hypothesis uses **ZN** interest-rate futures *volume × signed yield-proxy information*, and is a distinct conditional economic variable; it MUST NOT be misrepresented as entirely separate from CAVS's conceptual cross-venue confirmation.
- Executed **CME3-K25** used ONLY six price-return features (NQ/ZN/CL 1h and3h), **no ZN volume or conditional volume disagreement**; 2026 mirror N53 K25 BA58.76 vs price-only RFR60.33 — a negative result.
- Executed BSC-8 used **XAU own mid sign, XAU BID/ASK spread widening, halfhour sign reversal** not independent bond volume; it failed in 2025.
- Original MACRO PRAMV uses RFR+PSF signature+published surprise veto, not a 14–16 ZN volume innovation.
- Despite this, reviewer should reject the idea if it collapses to ZN r1, time-of-day or volatility and cannot add information; **method novelty ≠ guaranteed signed alpha**.

## Falsification contract before DeepSeek and before outcomes
1. Independent review must identify identification flaws: **CME 1H OHLCV volume is total not aggressor signed trades, intraday seasonal participation, DST, rolled continuous contract, bond futures' yield-price mapping, proxy simultaneity, 15m synchrony and data missingness**.
2. Audit source-ready coverage and prior20 historical volume; no 2026-tuned parameter. Evaluate only full eligible common-date rows.
3. On 2023 and2024 both, report N, coverage, BA, accuracy, UP/DOWN recall, DOWN precision, false alarms, actual return risk and same-date signed ZN return-only, spot trend, price-only RFR, and SAME exact volume-but-shuffled-month placebo. 2025 retro is inspected; 2026 stress if source-qualified cannot promote.
4. Compare candidate cohort to **identical cohort** sign(ZN) with no volume filter as well as both continuation options; otherwise selectivity may explain gains. Report standardized interaction coefficient / likelihood ablation if fit, with CIs and month-block bootstrap; do not fit on 2025.
5. Reject if no sufficient cohort, DOWN label collapse, BA no stable positive incremental value over both development years, retrospective 2025 reversal, or the source-clock fails. No trade on thresholds guessed to win 2025/26.
6. Prospective frozen post-2026-10-09 samples essential before claiming independent confirmatory directional improvement.
