# H15 NEWS NARRATIVE REVERSAL — OUTCOME-HIDDEN CODING PROTOCOL
Date 2026-10-13; research branch `research-gold-event-chain-h15-2016-2026-test-20261013`. No trading model, no signal.
**Status: feasible design / NOT executed blind annotation or confirmatory causal test.**

## Why separate from price-only H03 test?
H03 (prior 20-session gold return conditional on a +3%/-3% first crossing within next 10 sessions) was directly tested in 2016–2019 reconstructed London fixing, 2020–2022 independent NY17 M15 vendors, and 2026 reconstructed NY17 M15. H15 is NOT testable by looking for famous winners and then narrating their news. It requires a pre-existing story, a timestamped counter-news item, and NO-event controls, all coded without knowing gold's future price return.

## Frozen candidate universe, independent of realized gold direction
- `GOLD_EVENT_CHAIN_H15_NEWS_BLIND_CODING_UNIVERSE_249_MACRO_RELEASES_20261013.csv`: all 249 historical FOMC/NFP/CPI dates for 2016–2022 and 2026 from Neon `observations`, selected by event type/date alone; 67 FOMC, 91 CPI and 91 NFP releases.
- `GOLD_EVENT_CHAIN_H15_NEWS_BLIND_NONEVENT_CALENDAR_20261013.csv`: 1,429 weekday calendar control CANDIDATES, not overlapping CPI/NFP/FOMC ±1 calendar day. These dates may contain UNSCHEDULED geopolitical/margin/policy news, so they are not true "no-news" or "no-price-shock" controls.
- `GOLD_EVENT_CHAIN_H15_EXTRAPERIOD_DATED_NEWS_AUDIT_20261013.csv`: 13 date-labelled publication leads for Brexit 2016, liquidity March 2020, Fed QE March 2020, invasion Feb 2022, Warsh Jan 2026 and March 2026 liquidity. These were identified with prior knowledge of famous events and are **illustrative**; they must not be presented as blinded statistical test cases.

## Independent news annotations required (DO NOT USE GOLD PRICE RESULTS)
At each candidate news event origin, freeze:
1. `dominant_narrative_pre`: exclusive categories (HAVEN_GEOPOLITICAL, FED_EASING, FED_TIGHTENING, USD_WEAKNESS, INSTITUTIONAL_US_RISK, PHYSICAL_LOCATION_PREMIUM, FUNDING_STRESS, OTHER, MULTIPLE_CONFLICTING, NO_DOMINANT, UNKNOWN) using **only sources first published BEFORE** news event timestamp.
2. `report_new_claim`: reliable contemporaneous source plus *original first-print UTC*, not an updated Reuters copy.
3. `narrative_displacement`: TOWARD, REVERSES, UNRELATED, UNCERTAIN, judged against frozen `dominant_narrative_pre`; two independent judges and adjudicated disagreement if feasible. This is a structured cross-asset story classification **without reading gold's post-news price headline**.
4. `expected_gold_sign_from_prior_story`: only if pre-story has documented direction, not inferred post hoc.
5. `information_available_utc`, `first_gold_tradable_decision_utc`: ensure event news is observable before any measured outcome begins; NY17 day label alone insufficient for intraday triggers.
6. `counterevidence_pre`: pre-event articles arguing against the dominant story, missing, unclear, or opposite predictions.
7. Mark missing source/time as `UNVERIFIABLE`; code outcomes as withheld and do not silently discard hard cases.

**H15 test definition once the codebook is genuinely filled:** for identical previous-session tension/risk states and similar calendar regime, compare gold subsequent +/−3% first passages for independently identified REVERSES vs TOWARD news events and matched candidate controls, preserve coexistence of UP/DOWN shocks, and run permutation tests at disjoint episode/event level. Split sources by original availability and condition on event magnitude, prior return, vol, year; never use gold price changes to determine news coding.

## 3 publication pitfalls already found
- WGC Brexit webpage *claims 23 June 2016* while discussing the 24 June 2016 Leave referendum RESULT and reaction: this metadata cannot be safely used as pre-event warning (original editorial timestamp uncertain). Original Reuters coverage is 24 June AFTER vote result.
- WGC 2 March 2020 highlighted COMEX crowded longs, liquidity/margin calls and supportive ETF inflows BEFORE March 12–16 sell-off, but did not forecast the exact shock or date. WGC 19 March explains the already occurred liquidation.
- Reuters Jan 30 2026 stories about Warsh already refer to gold plunging in the morning: same-day publication is not automatically a time-leading event, and pre-announcement Warsh speculation was developing earlier.

## Data-vintage and source limitations
2016–19 gold source is retro-ingested StakTrakr 'LBMA' fixing at 12:00 London, **not** NY17 spot close; 2020–22 actual EV and HistData M15 are well correlated but reconstructed from after-the-fact research feeds; 2026 HistData + Twelve daily reconstructed price have separate clocks/market gaps. FOMC historical USMPD 'available_as_of' occurs Sep 2026; only meeting dates should be used for candidate calendar until original press release time is reverified. CFTC/CPI/PIT consensus original archival timestamps also must be checked before considering a possible ex ante narrative.
Coding not performed by a genuinely independent human/LLM blind annotator; we do NOT state H15 is proven or disproven. The famous cases are exploratory only.

## Illustrative publications & temporal quality
- WGC March 2 2020 pre-liquidation: https://www.gold.org/goldhub/gold-focus/2020/03/despite-last-weeks-selloff-market-shifts-could-bode-well-gold-prices
- WGC March 19 2020 post-liquidation: https://www.gold.org/goldhub/research/gold-prices-swing-as-markets-sell-off
- Fed official March 23 2020 08:00 EDT extraordinary operations: https://www.federalreserve.gov/newsevents/pressreleases/monetary20200323a.htm
- Reuters Feb 24 2022 04:10 EST haven rise: https://www.marketscreener.com/news/latest/Gold-jumps-over-2-as-Russia-attacks-Ukraine-39562653/
- Reuters Feb 24 2022 17:11 EST haven rise reversal: https://www.marketscreener.com/news/latest/Investors-regain-risk-appetite-dollar-oil-pare-gains-after-Ukraine-invasion-39577470/
- Reuters Jan 30 2026 Warsh news with already underway selling: https://www.marketscreener.com/news/stocks-steady-gold-tumbles-as-kevin-warsh-emerges-as-likely-fed-pick-ce7e5bdcdb8df720
- WGC Apr 8 2026 explanation of March liquidity and deleveraging: https://www.gold.org/goldhub/research/gold-market-commentary-march-2026
