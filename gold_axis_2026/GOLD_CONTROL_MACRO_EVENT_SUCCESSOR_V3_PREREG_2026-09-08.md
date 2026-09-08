# Gold Control — Macro Event Successor V3 Preregistration

Date: 2026-09-08
Engine identity: `MACRO_EVENT_SUCCESSOR_V3`
Branch: `gold-control-macro-event-successor-v3`
Status: **PRE-REGISTERED CHALLENGER / RESEARCH ONLY / NO PRODUCTION PROMOTION**
Base: canonical `gold-r4-direction-engine` @ `ac17405f0bbedd0471fb2782c5da1fd13b0b95fc`

## 1. Scope lock

This successor is intentionally limited to exactly three macro event families:

1. `EMPLOYMENT`
   - Nonfarm Payrolls (NFP)
   - Unemployment Rate
   - Average Hourly Earnings (AHE)
2. `INFLATION`
   - CPI
   - Core CPI
3. `FOMC`
   - target-rate surprise
   - expected policy-path / forward-guidance surprise

No GDP, PPI, Retail Sales, ISM, Durable Goods, sentiment, media, geopolitical, FX, order-flow, social-media, or other event family is part of V3. Any expansion requires a separately named successor/change-control.

## 2. Purpose and relationship to Market Shock

`MACRO_EVENT_SUCCESSOR_V3` is an independent event-risk/context engine. It does **not** replace `MARKET_SHOCK` and does not alter Market Shock LM/EVT mathematics.

The intended integration is context-only:

- Market Shock answers: `Was there an unusual XAU/USD move?`
- Macro Event V3 answers: `Was there a contemporaneous, economically material scheduled U.S. macro/policy surprise?`

Macro Event V3 must never be a hard kill gate for Market Shock. `NO_MACRO_EXPLANATION` must not delete or mutate a raw Market Shock episode.

Permitted integration outputs are limited to:
- `macro_match`
- `macro_family`
- `macro_strength`
- `macro_release_ts`
- `macro_surprise_score`
- `macro_direction_context`

The raw Market Shock episode must remain independently auditable.

## 3. Evidence and methodological basis

The scope is frozen from literature before V3 locked-period results are inspected:

- Sobti (2025), International Review of Financial Analysis, `What triggers intraday price jumps and co-jumps in gold?`, DOI 10.1016/j.irfa.2025.104380: U.S. macroeconomic news predicts about 34% of intraday gold jumps; FOMC rate decisions are the dominant macro news surprise. This supports Macro Event as a strong independent confirmer, but not as a universal hard gate.
- Elder, Miao & Ramchander (2012), Journal of Banking & Finance, `Impact of macroeconomic news on metal futures`, DOI 10.1016/j.jbankfin.2011.09.006: unexpected U.S. economic improvements materially affect gold returns/volatility; employment news is important.
- Kuttner (2001), Journal of Monetary Economics, `Monetary policy surprises and interest rates: Evidence from the Fed funds futures market`, DOI 10.1016/S0304-3932(01)00055-1: expected and unexpected target-rate changes must be separated using market expectations; anticipated changes are not equivalent to policy surprises.
- `How do the gold intra-day returns and volatility react to monetary policy shocks?` (2024), International Review of Financial Analysis, DOI represented by ScienceDirect PII S1057521924004186: gold reacts at five-minute horizons and the adjustment can persist beyond five minutes after FOMC shocks.
- `Intraday jumps and US macroeconomic news announcements`, Journal of Banking & Finance, ScienceDirect PII S0378426611000896: roughly one third of intraday jumps coincide with macro releases and announcement-related jumps are larger; surprise content is the economically relevant quantity.

## 4. Event-time rule

V3 is not an `08:30 engine`.

Every event must carry its own immutable official release timestamp:

- `official_release_at`
- `event_family`
- `event_name`

No family-wide assumed clock time is permitted except where an official source contract explicitly establishes the release time for that exact event.

Pre-release Market Shock episodes are not retroactively attributed to a later macro event and must be labeled `PRE_RELEASE_SHOCK` if evaluated in event matching.

## 5. Point-in-time source contract

Every surprise input must satisfy all applicable fields:

- `actual_value`
- `actual_first_print`
- `actual_available_at`
- `consensus_value` or market-implied expectation
- `consensus_captured_at` / expectation snapshot timestamp
- `official_release_at`
- `provider`
- `lineage_id`
- immutable payload/input fingerprint

Core PIT invariant for consensus-based events:

`consensus_captured_at < official_release_at`

A historical value with no provider-level proof that it was available before the release is **not** fully PIT-proven, even if coverage and lineage exist.

Historical reconstruction and prospective capture must remain different evidence classes.

## 6. Family-specific surprise definitions

### 6.1 EMPLOYMENT

Keep the V2 family logic conceptually unchanged:
- NFP surprise = actual first print minus pre-release consensus
- unemployment surprise = actual first print minus pre-release consensus
- AHE surprise = actual first print minus pre-release consensus

Normalize each component only with prior event surprises using robust expanding scale. V2 MAD/IQR fallback semantics may be reused; no locked-period threshold optimization is permitted.

Gold-direction orientation remains contextual, not deterministic:
- stronger NFP is generally gold-adverse context
- higher unemployment is generally gold-supportive context
- stronger AHE is generally gold-adverse context

### 6.2 INFLATION

Only CPI and Core CPI are allowed.

Each component must use actual first print minus a pre-release consensus proven to exist before `official_release_at`, normalized only with prior event surprises.

The family state may use a robust aggregate plus breadth/consistency across headline and core, but no numeric strong-event threshold may be selected from 2024–2026 outcomes. Any numeric threshold must be frozen from development data or inherited by a separately documented rule before locked evaluation.

### 6.3 FOMC

FOMC may **not** be implemented as simple announced target rate minus an analyst calendar consensus if a market-implied expectation source is absent.

Required conceptual components:
- `target_surprise`: unexpected target-rate component relative to a PIT market-implied expectation
- `path_surprise`: unexpected change in the expected policy path / forward guidance, derived from an independently specified market-implied expectation design

If the required PIT market-implied expectation source is unavailable or not reproducible:

`FOMC = BLOCKED_EXPECTATION_SOURCE`

No proxy substitution, hand-entered expectation, current-vintage substitution, or guessed path factor is allowed.

## 7. Market Shock matching semantics

Macro Event V3 is a confirmer/context layer only.

Frozen primary event windows:
- `EMPLOYMENT`: `[official_release_at, official_release_at + 10 minutes]`
- `INFLATION`: `[official_release_at, official_release_at + 10 minutes]`
- `FOMC`: `[official_release_at, official_release_at + 10 minutes]`

Frozen diagnostic window for all three families:
- `[official_release_at, official_release_at + 30 minutes]`

The primary window is the only window eligible for V3-to-Market-Shock confirmation claims. The 30-minute window is diagnostic only.

No pre-release episode may be counted as macro-confirmed.

## 8. Macro-to-Market-Shock output states

Exactly these context states are permitted:

1. `MACRO_CONFIRMED`
   - Market Shock episode occurs inside the family primary post-release window; and
   - Macro Event family has a PIT-valid strong surprise under the frozen family rule.
2. `MACRO_EVENT_PRESENT_BUT_NOT_STRONG`
   - a scheduled governed event is present, but its frozen surprise rule is not strong.
3. `NO_MACRO_EXPLANATION`
   - no governed strong event explains the Market Shock episode.
4. `PRE_RELEASE_SHOCK`
   - Market Shock begins before the governed event release timestamp.
5. `MACRO_DATA_NOT_PIT_READY`
   - event exists, but required PIT expectation/consensus evidence is not proven.

`NO_MACRO_EXPLANATION` must never delete or suppress the raw Market Shock episode.

## 9. Validation design

### Source readiness gate

Before any family contributes `MACRO_CONFIRMED`, all required actual/expectation/availability/lineage fields for that event must pass PIT checks.

### Development stage

Use only pre-locked development history to define any family strong-event threshold not inherited exactly from V2. No random split.

### Matched-control validation

For each family, compare Market Shock occurrence in strong-event primary windows against predeclared matched non-event/control windows preserving relevant calendar/time-of-day structure.

Report at minimum:
- event-window Market Shock rate
- control-window Market Shock rate
- enrichment ratio
- odds ratio
- confidence interval
- Fisher exact test or another preregistered exact small-sample method where appropriate

A macro family is not accepted merely because many Market Shock episodes occur after announcements; it must discriminate against matched controls.

### Locked sequence

After rules and sources are frozen, evaluate in the existing sequence:

`2026 -> 2025 -> 2024`

Stop on FAIL / INSUFFICIENT_SAMPLE / BLOCKED unless a separately named methodology revision is preregistered before further locked results are inspected.

## 10. Governance locks

- `AUTO_SELECTOR=OFF`
- `AUTO_ENSEMBLE=OFF`
- no Market Shock threshold mutation
- no Market Shock raw-episode deletion
- no post-result macro threshold tuning
- no silent provider substitution
- no random split
- no backdating historical reconstruction as prospective evidence
- no production Forecast Store / Decision Store write
- no BUY/SELL/position mapping
- no canonical merge/promotion by this challenger

## 11. Current source-readiness facts at preregistration

As of 2026-09-08 production Neon audit:

### EMPLOYMENT

Existing V2 source lane contains 6 series (NFP, unemployment, AHE actual first print + consensus), 126 rows each / 756 total observations, with lineage and `available_as_of` populated.

However, historical consensus rows explicitly carry:

`provider_exact_pre_release_update_timestamp_proven = false`

Therefore:
- historical source coverage = present
- exact historical pre-release consensus PIT = `NOT_PROVEN`
- V3 employment `MACRO_CONFIRMED` authority = `BLOCKED_PIT_CONSENSUS_PROOF` until resolved or prospective immutable pre-release capture exists.

### INFLATION

No governed CPI/Core CPI Macro Event V3 source series was found in the current canonical repository/production source registry audit performed before this preregistration.

Status: `BLOCKED_SOURCE_NOT_ESTABLISHED`.

### FOMC

Production source registry contains `EFFR_NYFED` and a monthly research-only fed-funds series, but no governed PIT market-implied FOMC target/path surprise source suitable for the Kuttner-style requirement.

Status: `BLOCKED_EXPECTATION_SOURCE`.

These blockers are evidence, not permission to substitute other data.

## 12. Promotion boundary

A successful V3 historical replay is not production authority.

Promotion would require separate change-control after:
- family source/PIT readiness PASS,
- preregistered development and matched-control validation,
- locked-sequence evidence,
- runtime/prospective capture proof,
- governance approval.
