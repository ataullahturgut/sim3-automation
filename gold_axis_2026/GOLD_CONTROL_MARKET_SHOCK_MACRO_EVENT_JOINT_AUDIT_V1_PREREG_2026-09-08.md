# GOLD CONTROL — MARKET SHOCK + MACRO EVENT JOINT AUDIT V1

**Status:** `PREREGISTERED_HISTORICAL_RESEARCH_AUDIT / NOT_PRODUCTION_AUTHORITY`  
**Branch:** `gold-control-market-shock-macro-event-joint-audit-v1`  
**Macro base:** `gold-control-macro-event-successor-v3 @ 373f9cf910e12cddbc2a02054cf051c4bddc693b`  
**Market Shock identity:** `MARKET_SHOCK_CHALLENGER_V3`, exact frozen algorithm from branch `gold-control-market-shock-challenger-v3 @ 12edc11e42b58d9c91fb587efdda9269cae4c91a`  
**Evidence:** historical research only. No production, selector, ensemble, decision or forecast authority.

## Question
Does contemporaneous strong Macro Event V3 context add useful information to Market Shock V3 by identifying event-window shocks that are enriched versus matched controls, directionally concordant with the macro surprise, and followed by same-direction continuation after the shock is observed?

## Authority basis
This design follows the high-frequency event/jump literature: macro announcements can materially raise intraday jump incidence and jump size; gold-specific evidence finds US macro news explains a material share of intraday gold jumps, with FOMC particularly important. The audit therefore treats Macro Event as contemporaneous explanatory/confirmation context, not as a mechanism that deletes or rewrites raw Market Shock episodes.

## Frozen data
1. XAU/USD 5-minute cache: `xau_intraday_research_cache_5m`; only accepted if batch lineage is Twelve Data / XAU/USD / 5min / `HISTORICAL_RESEARCH_RETRIEVAL` / COMPLETE.
2. Macro score series from Neon observations:
   - `MACRO_EVENT_V3_EMPLOYMENT_SCORE`
   - `MACRO_EVENT_V3_INFLATION_SCORE`
   - `MACRO_EVENT_V3_FOMC_SCORE`
3. Market Shock V3 algorithm is not refit/tuned beyond its frozen walk-forward logic. The Twelve cache is storage reuse of the same provider identity, not provider substitution.

## Evaluation window
Primary joint audit: calendar years **2024 and 2025 only**, because these are completed frozen Market Shock V3 holdout years common to the Macro Event history. 2026 is excluded from the primary acceptance decision.

## Strong macro event definition
A Macro V3 observation is strong only when its frozen metadata state is one of:
- `GOLD_ADVERSE_MACRO_SHOCK`
- `GOLD_SUPPORTIVE_MACRO_SHOCK`.
Macro direction is `sign(score)`: positive = gold-supportive/up context; negative = gold-adverse/down context.

## Event-window Market Shock match
Primary match window: `[official/reconstructed macro release timestamp, +10 minutes]`, consistent with Macro V3's frozen primary event window. A match exists if any Market Shock V3 `shock_sig` bar occurs in that interval. The earliest qualifying shock is the matched shock. No pre-release price move is retroactively attributed to the macro event.

## Matched controls
For every strong event, seek up to four control timestamps preserving weekday and UTC clock time. Candidate offsets are searched in this fixed order:
`-7d, +7d, -14d, +14d, -21d, +21d, -28d, +28d`.
A control is rejected if any Employment/Inflation/FOMC Macro V3 score event (strong or weak) lies within +/-60 minutes of that control timestamp, or if required XAU bars are unavailable. No replacement rule may be invented after results are seen.

## Primary tests
### A. Shock-incidence enrichment
Compare Market Shock presence in strong macro windows versus matched control windows.
- report event incidence, control incidence, risk ratio and odds ratio;
- Fisher exact one-sided test (`event > control`).

### B. Direction concordance
Among matched strong-macro + Market-Shock windows, compare macro direction with earliest Market Shock direction.
- report concordant/discordant counts;
- exact one-sided binomial test against p=0.5.

### C. Post-confirmation continuation
For concordant joint matches only, define the signal as available at the earliest Market Shock bar. Measure future log return from that shock-bar close to the last XAU close at or before `macro release +30m`. Multiply by joint direction.
- report hit rate and median signed continuation;
- this return begins after the shock signal exists, preventing the detected jump itself from being counted as future performance.

## Frozen interpretation states
`JOINT_CONTEXT_PASS` only if all hold:
1. shock-incidence risk ratio > 1 and Fisher one-sided p <= 0.10;
2. direction concordance > 50% and exact one-sided binomial p <= 0.10;
3. median post-confirmation signed continuation > 0.

`CONTEXT_ASSOCIATION_ONLY` if A and B pass but C does not.

Otherwise: `JOINT_VALUE_NOT_PROVEN`.

Small family-level Employment / Inflation / FOMC results are descriptive unless sample size supports the same exact tests.

## Governance locks
- No Market Shock threshold changes.
- No Macro Event threshold changes.
- No result-driven window changes.
- No provider substitution.
- No random split.
- No suppression/deletion of raw Market Shock episodes.
- Market Shock V3's standalone failed research-gate status remains unchanged regardless of joint-audit outcome.
- Historical replay/retrieval is never relabeled as prospective evidence.
- No Neon writes are required for this audit; artifacts only.
