# Gold Control — Macro Event Successor V1 Consensus Provider Decision

Date: 2026-09-05
Branch: `gold-control-macro-event-successor-v1-source-contract`
Engine identity: `MACRO_EVENT_SUCCESSOR_V1`
Scope: source/provider decision only. No model score, direction vote, Forecast Store write, or Decision Store write is authorized by this document.

## 1. Decision

For historical event-level market consensus, the first executable candidate is **Trading Economics Economic Calendar Point-in-Time (TE PIT)**.

This does **not** mean TE is already approved for model use. It means TE is the best currently executable candidate to audit because it exposes a structured historical economic-calendar API, explicitly documents point-in-time preservation, and separates the survey `Forecast` field from `TEForecast` (Trading Economics' own model forecast).

Provider hierarchy for research/audit:

1. **Bloomberg Economic Calendar historical consensus** — preferred authority benchmark when entitlement/data access is available, because Federal Reserve research commonly uses the latest Bloomberg panel median immediately before releases.
2. **Trading Economics Economic Calendar Point-in-Time** — primary executable candidate for this successor under current project constraints. Its `Forecast` field is the survey consensus; `TEForecast` is forbidden as a substitute.
3. **Reuters pre-release economist survey reporting** — independent public spot-check/evidence lane only; not a primary bulk ingestion source because coverage and structured historical retrieval are not guaranteed.
4. **Econoday** — secondary candidate only if TE/Bloomberg are unavailable and a separate entitlement/PIT audit proves historical pre-release consensus preservation. No automatic fallback is authorized.

## 2. Frozen event components

The successor consensus input universe is limited to the U.S. BLS Employment Situation event family:

- `Non Farm Payrolls` / headline total nonfarm payroll monthly change
- `Unemployment Rate`
- `Average Hourly Earnings MoM` for all employees on private nonfarm payrolls

No extra macro indicators may be added during this source audit.

## 3. TE PIT fields and semantics

Required TE fields:

- `CalendarId`
- `Date`
- `Country`
- `Category`
- `Event`
- `Reference`
- `ReferenceDate`
- `Source`
- `SourceURL`
- `Actual`
- `Previous`
- `Forecast`
- `TEForecast`
- `DateSpan`
- `Importance`
- `LastUpdate`
- `Revised`
- `Unit`
- `Ticker`
- `Symbol`

Binding rules:

- `Forecast` is the only TE field eligible to become market-consensus input after provider audit.
- `TEForecast` is a proprietary TE model projection and is **forbidden** as market consensus.
- `Actual` from TE is not the authority actual for model construction; BLS/ALFRED first-release reconstruction remains the actual-data authority lane.
- `LastUpdate` is record-update metadata and must not be silently reinterpreted as the time at which the survey consensus first became available.
- Where the provider preserves a pre-release survey `Forecast` attached to the release event but does not expose the exact last pre-release forecast-update timestamp, the project may only treat the consensus as eligible **at the official release timestamp**, tagged `PRE_RELEASE_CONSENSUS_FIELD_PRESERVED_BY_PROVIDER`. It may not be used for a decision timestamp strictly before the release.
- Current website calendar pages, search-engine caches, or post-release news articles are not substitutes for the governed PIT API record.

## 4. Why the timestamp rule is necessary

Public evidence shows that consensus can change during the days before a release. For example, Reuters reported an August-2025 payroll expectation of 78k one week before the report, while the immediate release-day Reuters poll figure was 75k. Therefore, selecting an arbitrary earlier survey snapshot would create a different model input.

The same issue is visible in August-2026: public Trading Economics calendar material and release-day Reuters reporting did not show an identical headline payroll consensus. That is not by itself evidence that either provider is wrong; it proves that provider identity and snapshot timing are part of the model contract.

Accordingly, provider identity is frozen once chosen. No per-origin provider switching is allowed.

## 5. Provider audit gates

Before TE PIT can be approved for historical model input, an authenticated API audit must pass all of the following on multiple separated release dates:

1. U.S. records for all three frozen indicators are retrievable.
2. The event date/time is exact (`DateSpan = 0`) and corresponds to the official Employment Situation release.
3. `Forecast` is present and numerically parseable for each required indicator/origin used in scoring.
4. `Forecast` and `TEForecast` remain separately identifiable.
5. Reference month/date can be aligned unambiguously with the BLS/ALFRED actual reconstruction.
6. No current-vintage actual is substituted for the BLS/ALFRED first print.
7. Missing consensus is fail-closed; it is not imputed from `TEForecast`, previous consensus, current web pages, or another provider.
8. Raw licensed provider payloads are not committed to the public repository. Audit evidence records hashes, field-presence checks, identifiers, and normalized non-licensed metadata only unless license terms explicitly permit more.
9. No model score or production authority-store write occurs during source audit.

## 6. Independent authority checks

Provider semantics are checked against:

- Federal Reserve research using actual minus market consensus, commonly Bloomberg panel median, with historical standardization.
- Reuters pre-release survey reports as public event-specific spot checks.
- BLS/ALFRED for official first-release actuals and release-time alignment.

A mismatch between TE and Reuters does not automatically fail TE because the survey populations/statistics and snapshot times can differ. It must be recorded as a provider-methodology difference and cannot be repaired by switching providers after viewing model results.

## 7. Current stop point

As of this decision:

- BLS current machine access: proven.
- ALFRED initial-release access: proven.
- ALFRED-as-of construction vs selected BLS first releases: proven on the frozen sample audit.
- TE PIT provider documentation: found and suitable for authenticated audit.
- `TRADING_ECONOMICS_API_KEY`: not configured in the project CI environment at the last verified preflight.
- Consensus provider: **NOT YET APPROVED FOR MODEL USE**.
- Model scoring: **NOT AUTHORIZED**.
- Production DB ingestion of consensus: **NOT AUTHORIZED**.

Next executable action: run the frozen authenticated TE PIT provider audit when entitlement is available; if it passes, freeze exact event mappings and then authorize a separate governed consensus-ingestion bundle for Neon.