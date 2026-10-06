# GOLD GLOBAL SESSION CLOCK CONTRACT — 2026-10-06

**Status:** CORRECTED PREREGISTERED CLOCK / TIMESTAMP AUTHORITY  
**Supersedes:** the earlier same-day version that treated two old SGE sub-sessions as canonical modern Asia targets.  
**Scope:** timestamp provenance, externally anchored candidate session partitions, DST handling, and label construction.  
**Important:** this document freezes clock semantics and candidate partitions. It does **not** preselect the final number of forecast heads or claim predictive performance.

## 1. Correction discovered during independent verification

The project must not equate:
- three dominant gold centres,
- historical exchange sub-sessions,
- academic price-discovery zones,
- and the eventual number of forecast models.

A material modernization issue was found in the first draft:

Sobti, Sehgal & Ilango (2021) use 2013–2018 data and divide the day into five ET zones:
- Asia Morning 21:00–23:30 ET
- Asia Afternoon 01:30–03:30 ET
- Europe 03:30–08:00 ET
- NY/London overlap 08:00–14:30 ET
- US 14:30–21:00 ET.

However, Shanghai Gold Exchange changed its matching-market schedule effective **2019-06-10**, adding the former 11:30–13:30 interval so that the day matching session became **09:00–15:30 Shanghai local time**. Therefore the old morning/afternoon split must not be presented as the official modern 2023–2026 SGE matching-session structure.

The first draft's hybrid rule that anchored W1/W2 to 09:00–11:30 and 13:30–15:30 Shanghai is therefore superseded as a binding modern target definition.

## 2. Raw XAU/USD timestamp provenance — binding

The project 15-minute downloader requests Twelve Data with:

`symbol=XAU/USD`  
`interval=15min`  
`timezone=UTC`  
`order=ASC`

The repository loader materializes API datetimes as timezone-aware UTC.

Twelve Data official API documentation states that the intraday `datetime` field refers to **when the bar with the specified interval was opened**. Therefore a row stamped `12:00 UTC` is the bar opened at 12:00 UTC.

This is the canonical raw clock.

## 3. Time-zone engine — binding

Use IANA time zones only:

- `UTC`
- `America/New_York`
- `Europe/London`
- `Asia/Shanghai`
- `Europe/Istanbul`

Conversions must be date-aware using the IANA tz database (Python `zoneinfo` / pandas timezone conversion).

Fixed-offset logic such as:
- New York = UTC-5,
- London = UTC+0,
- Istanbul = New York+7,

is prohibited.

DST transition dates must be resolved from the timestamp itself.

## 4. Two externally anchored candidate partitions

There is no single universal gold-session partition in the literature or institutional practice. To avoid inventing boundaries after observing performance, the project preregisters **two external candidate partitions**.

### Partition A — WGC_2026_NY3

Primary current-industry benchmark candidate.

World Gold Council 2026 weekly intraday analyses explicitly show the session windows in **New York local time**:
- **ASIA:** 18:00–03:00 America/New_York
- **EUROPE:** 03:00–08:00 America/New_York
- **US:** 08:00–17:00 America/New_York

For spring 2026 EDT weeks, WGC gives the UTC equivalents as 22:00–07:00, 07:00–12:00 and 12:00–21:00. Those UTC equivalents must **not** be hard-coded across winter dates.

Date-aware UTC mapping:
- during EDT (UTC-4): Asia 22:00–07:00 UTC, Europe 07:00–12:00 UTC, US 12:00–21:00 UTC;
- during EST (UTC-5): Asia 23:00–08:00 UTC, Europe 08:00–13:00 UTC, US 13:00–22:00 UTC.

Purpose:
- current-market three-session benchmark candidate;
- operationally coherent with the New York 17:00 daily break / 18:00 reopen convention;
- DST-aware by construction.

Important limitation:
WGC has used different session partitions in other analyses (for example a 2024 study used Asia 22:00–11:00 UTC, Europe 11:00–14:00 UTC, US 14:00–22:00 UTC). Therefore WGC_2026_NY3 is an externally anchored **candidate analytical partition**, not a universal definition of global gold market hours.

### Partition B — SOBTI_5_ET

Academic replication / price-discovery benchmark.

Using `America/New_York` date-aware local time:
- **ASIA_MORNING_LIT:** 21:00–23:30 ET
- **ASIA_AFTERNOON_LIT:** 01:30–03:30 ET
- **EUROPE_LIT:** 03:30–08:00 ET
- **NY_LONDON_LIT:** 08:00–14:30 ET
- **US_LATE_LIT:** 14:30–21:00 ET

Purpose:
- reproduce the externally published five-zone academic partition;
- test whether its price-discovery segmentation transports into 2023–2025;
- preserve NY/London overlap as an explicit candidate state.

Guardrail:
- these labels are **literature zones**, not claims that the modern SGE matching market still has the same 2013–2018 session structure.

## 5. Modern SGE venue-state markers — features/telemetry, not target boundaries

Official SGE evidence:

- night matching session: 20:00–02:30 Shanghai local;
- day matching session: **09:00–15:30 Shanghai local** after the 2019 extension;
- holiday schedules may alter availability.

Store venue-state markers per bar/date:
- `sge_night_open`
- `sge_day_open`
- `sge_holiday_or_closed`

Do **not** split the modern SGE day at 11:30/13:30 as if a matching-market break still governed 2023–2026.

## 6. LBMA and COMEX markers

### LBMA
Event markers:
- LBMA Gold Price AM: **10:30 Europe/London**
- LBMA Gold Price PM: **15:00 Europe/London**

These are benchmark-event flags, not automatic session target boundaries.

### COMEX / GC
GC is an almost round-the-clock electronic futures market with a daily maintenance break under the standard contract schedule. COMEX activity therefore cannot be reduced to a simple “US market is closed outside cash hours” assumption.

Store:
- GC active/maintenance state where available;
- US 08:30 ET macro-event flag separately.

## 7. Why both partitions are necessary

The modern WGC partition is closer to current 2026 gold-market attribution practice.

The Sobti partition has stronger academic microstructure motivation and explicitly isolates the NY/London overlap, but was estimated using 2013–2018 market structure.

Therefore the project will **not choose 3 vs 5 because one happens to score better on 2026**.

Chronology:
- 2023–2024: development / partition and expert-structure study;
- 2025: frozen transport deciding whether the structure is stable;
- 2026: retrospective stress only, never used to move clock boundaries.

Possible final outcomes:
- 3 operational heads;
- 4 heads if a robust NY/London overlap split is warranted;
- 5 heads if both Asian subzones and overlap states independently transport;
- fewer heads if session-specific forecasting adds no robust value.

## 8. Raw-bar matching rule

For every candidate boundary:

1. Construct the boundary in its declared canonical clock (UTC for WGC_3; America/New_York for SOBTI_5_ET).
2. Convert the aware timestamp to UTC.
3. Match exactly to `dt_utc`.
4. Boundary price = **open of the bar opened exactly at the boundary**.
5. Return = `P(end boundary) / P(start boundary) - 1`.
6. Missing exact boundary => `MISSING_BOUNDARY`.
7. No silent nearest-bar substitution, forward fill, or backfill.

All registered boundaries are multiples of 15 minutes.

## 9. SESSION_DIRECTION versus EXECUTABLE_DIRECTION

Two concepts remain mandatory.

### SESSION_DIRECTION
Theoretical boundary-to-boundary direction for a registered session partition.

### EXECUTABLE_DIRECTION
Direction from the first strictly post-ready/post-signal tradable bar to a frozen future endpoint.

Example:
if a forecast is finalized at 08:00 New York after the 08:00 instant, the 08:00 bar open is not a strictly post-signal entry. With 15-minute data, 08:15 New York is the conservative first post-signal boundary unless a finer governed feed proves otherwise.

Never report SESSION_DIRECTION accuracy as executable trading accuracy.

## 10. Source-ready rule

For every future session head H:

`t_ready(H) = max(availability timestamp of every required input) + compute latency`

If `t_ready(H) > target_start(H)`, that head cannot claim the full session as its tradable target.

Either:
- create a separately frozen post-ready executable target, or
- declare the full-session forecast unavailable.

## 11. DST audit requirements

Every data row used in clock validation must carry:
- `dt_utc`
- `dt_ny`
- `dt_london`
- `dt_shanghai`
- `dt_istanbul`
- UTC offsets for NY/London/Shanghai/Istanbul.

Mandatory audit samples:
- normal winter week;
- normal summer week;
- US DST transition week;
- UK DST transition week;
- weeks where US and UK are temporarily on different seasonal offsets.

Both WGC_2026_NY3 and SOBTI_5_ET are anchored to `America/New_York` local time and therefore move in UTC according to date-aware DST conversion.

## 12. Historical diagnostic artifacts

Older repository buckets such as:
- `asia_to_europe`
- `europe_pre_overlap`
- `ny_london_overlap`
- `late_us`

remain diagnostic and must not be silently reused as training truth for the new project unless their clock definition exactly matches one of the registered candidate partitions.

## 13. External authorities

1. World Gold Council, 2026 intraday session analysis:
   - session table shown in New York time: Asia 18:00–03:00, Europe 03:00–08:00, US 08:00–17:00;
   - spring-2026 UTC equivalents: Asia 22:00–07:00, Europe 07:00–12:00, US 12:00–21:00;
   - UTC conversion is date-aware in this project, not fixed.

1A. World Gold Council, 2024 intraday analysis:
   - used a different analytical partition (Asia 22:00–11:00 UTC, Europe 11:00–14:00 UTC, US 14:00–22:00 UTC), demonstrating that WGC session windows are analysis constructs rather than universal exchange-open definitions.

2. Sobti, Sehgal & Ilango (2021), *International Review of Financial Analysis* 78, 101893:
   - five sequential ET price-discovery zones using 2013–2018 one-minute New York/London/Shanghai data.

3. Shanghai Gold Exchange, notice effective 2019-06-10:
   - matching-market day trading extended to 09:00–15:30 by adding the former 11:30–13:30 interval.

4. LBMA:
   - Gold Price auctions commence at 10:30 and 15:00 London time.

5. CME Group:
   - standard GC futures trade electronically for approximately 23 hours per trading day with a daily maintenance period under the standard schedule.

6. Twelve Data:
   - `timezone` may be explicitly set to UTC;
   - intraday `datetime` refers to the bar-open timestamp.

## 14. Next gate

Before model fitting:

1. use the governed XAU/USD 15-minute UTC backfill for 2023–2025;
2. create **both** WGC_2026_NY3 and SOBTI_5_ET label panels with date-aware New York DST conversion;
3. run exact-boundary coverage audit;
4. run DST-transition audit;
5. freeze data hashes / request metadata;
6. only then test expert-by-window predictive performance.

No 2026 result may be used to alter these candidate clock boundaries.
