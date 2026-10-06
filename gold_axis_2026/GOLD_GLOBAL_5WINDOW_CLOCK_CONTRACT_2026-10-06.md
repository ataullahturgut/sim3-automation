# GOLD GLOBAL 5-WINDOW CLOCK CONTRACT — 2026-10-06

**Status:** PREREGISTERED CLOCK / TIMESTAMP AUTHORITY  
**Scope:** session-target clock construction and mapping to the governed 15-minute XAU/USD feed.  
**Important:** this freezes timestamp semantics and research-window construction. It does **not** yet freeze the number of final operational consensus heads or claim predictive performance.

## 1. Why this contract exists

Three dominant gold centres (London, New York/COMEX, Shanghai) do not mechanically imply three prediction models. The project first studies five sequential price-discovery windows, then decides from pre-2026 evidence whether contiguous windows should be merged.

The five-window research prior comes from Sobti, Sehgal & Ilango (2021), while venue-local clock definitions come from official SGE/LBMA/CME sources.

## 2. Raw XAU/USD timestamp provenance — binding

The project 15-minute coverage downloader requests Twelve Data with:

`symbol=XAU/USD`  
`interval=15min`  
`timezone=UTC`  
`order=ASC`

The repository loader materializes each API datetime as:

`dt_utc = pd.Timestamp(datetime, tz="UTC")`

Twelve Data documentation defines intraday `datetime` as the timestamp at which the interval bar **opened**. Therefore a row stamped `12:00 UTC` is the 12:00–12:15 bar, not a close timestamp.

This is the canonical raw clock. No session label may be assigned from an unzoned timestamp.

## 3. Time-zone engine — binding

Use IANA time zones only:

- `UTC`
- `America/New_York`
- `Europe/London`
- `Asia/Shanghai`
- `Europe/Istanbul`

All conversions are date-aware. Fixed offsets such as “New York = UTC-5” or “London = UTC+0” are prohibited.

Implementation must use an IANA tz database (Python `zoneinfo` / pandas tz conversion). DST transitions must be resolved from the date itself.

## 4. Five target windows — clock definition

### W1 — ASIA_MORNING

**Canonical boundary:** official Shanghai Gold Exchange local morning session.

- timezone: `Asia/Shanghai`
- start: **09:00**
- end: **11:30**
- UTC: **01:00–03:30** year-round
- Istanbul: **04:00–06:30** year-round

Reason: SGE local trading hours are venue-defined and Shanghai does not use seasonal DST. This avoids shifting the actual Shanghai morning by one hour during New York winter time.

### W2 — ASIA_AFTERNOON

**Canonical boundary:** official Shanghai Gold Exchange local afternoon session.

- timezone: `Asia/Shanghai`
- start: **13:30**
- end: **15:30**
- UTC: **05:30–07:30** year-round
- Istanbul: **08:30–10:30** year-round

### W3 — EUROPE

There is no single official London OTC market open because Loco London trades continuously. Therefore the research boundary uses the externally published Sobti et al. sequential price-discovery zone rather than inventing a London open.

- timezone anchor: `America/New_York`
- start: **03:30 ET**
- end: **08:00 ET**

Date-aware mapping:
- while New York is EDT (UTC-4): **07:30–12:00 UTC**, **10:30–15:00 Istanbul**
- while New York is EST (UTC-5): **08:30–13:00 UTC**, **11:30–16:00 Istanbul**

The corresponding London local clock is recorded per date; it must not be hard-coded because US and UK DST change on different dates.

### W4 — NY_LONDON_OVERLAP

Academic sequential price-discovery zone:

- timezone anchor: `America/New_York`
- start: **08:00 ET**
- end: **14:30 ET**

Date-aware mapping:
- EDT: **12:00–18:30 UTC**, **15:00–21:30 Istanbul**
- EST: **13:00–19:30 UTC**, **16:00–22:30 Istanbul**

This is a research target clock. It must not be confused with the legacy CIG-D1 daily-reference target merely because legacy CIG-D1 had an 08:00 New York governed issue deadline.

### W5 — LATE_US

Academic sequential US zone:

- timezone anchor: `America/New_York`
- start: **14:30 ET**
- end: **21:00 ET**

Date-aware mapping:
- EDT: **18:30–01:00 UTC next day**, **21:30–04:00 Istanbul next day**
- EST: **19:30–02:00 UTC next day**, **22:30–05:00 Istanbul next day**

## 5. Why Asia is not frozen directly from the paper's ET clock

Sobti et al. report Asia Morning 21:00–23:30 ET and Asia Afternoon 01:30–03:30 ET. When New York is on daylight time these map exactly to the official SGE 09:00–11:30 and 13:30–15:30 Shanghai sessions. In New York standard time they shift by one hour relative to Shanghai because Shanghai does not observe DST.

Therefore the project preserves the paper as the five-zone research authority but anchors the two Asia windows to **official SGE local time**. A separate `LIT_ET_ASIA` sensitivity may be retained for replication, but it is not the canonical venue-aligned Asia label.

## 6. LBMA benchmark markers — event flags, not session boundaries

Record separately for every date:

- LBMA Gold Price AM: **10:30 Europe/London**
- LBMA Gold Price PM: **15:00 Europe/London**

These are event markers inside the intraday path. They do not define the Europe start/end target by themselves.

## 7. Raw-bar matching rule

For every session boundary:

1. Construct the boundary in its canonical local zone.
2. Convert that aware timestamp to UTC.
3. Match it to `dt_utc` in the 15-minute XAU/USD table.
4. Because `datetime` is a bar-open timestamp, boundary price = **open of the bar stamped exactly at the boundary**.
5. The theoretical session return is:
   `P(end boundary) / P(start boundary) - 1`.
6. If either exact boundary bar is absent, mark the label **MISSING**. Do not silently forward-fill/back-fill.

All five canonical boundaries are multiples of 15 minutes, so no rounding is required.

## 8. Forecast vs realization clocks

Two labels must be stored separately.

### SESSION_DIRECTION
Direction from the theoretical session start boundary to theoretical session end boundary. Used for scientific price-discovery analysis.

### EXECUTABLE_DIRECTION
Direction from the first bar that is strictly tradable after the forecast is genuinely available to the frozen session exit.

For example, if a head is issued at exactly 08:00 New York and computation/decision occurs after that timestamp, the 08:00 bar open is not a strictly post-signal entry. With 15-minute data, **08:15 New York** is the first conservative post-signal bar unless a finer execution feed proves an earlier executable timestamp.

The project must never report SESSION_DIRECTION accuracy as executable trading accuracy.

## 9. Source-ready rule for each future head

For a session head H:

`t_ready(H) = max(publication/availability timestamp of every required input) + compute latency`

A head is valid for the full theoretical session only if `t_ready <= target_start`.

If `t_ready > target_start`:
- do not backdate the prediction;
- either define a separately frozen post-ready executable target, or
- declare that head unavailable for that full session.

## 10. DST governance

New York and London seasonal clock changes are not synchronized; Shanghai and Istanbul are treated through their IANA rules. Therefore every row must carry at minimum:

- `dt_utc`
- `dt_ny`
- `dt_london`
- `dt_shanghai`
- `dt_istanbul`
- `ny_utc_offset`
- `london_utc_offset`

No model feature or target may be generated using manually coded “summer = +7 / winter = +8” logic. Those values may be displayed after date-aware conversion but are not the conversion engine.

## 11. Holiday / venue-state rule

The XAU/USD aggregate spot feed may contain data when one venue is closed. Therefore keep separate venue-state flags:

- `sge_open`
- `lbma_business_day`
- `comex_regular_status` / holiday state where available

Do not silently delete a global-XAU session label merely because one venue is closed. Instead retain the clock-window label and tag venue closure for conditional analysis.

## 12. Chronology

Clock definitions are fixed without using 2026 directional accuracy.

- 2023–2024: development of session models and expert membership
- 2025: frozen transport / architecture decision
- 2026: retrospective stress only; no clock retuning

## 13. Superseded older session buckets

Older repository diagnostics such as:
- prior-day 20:00 NY -> 03:30 NY “asia_to_europe”
- 03:30 -> 08:00 NY
- 08:00 -> 14:30 NY
- 14:30 -> 20:00/21:00 NY

remain useful historical attribution artifacts, but they are **not** the binding five-window label contract for the new session-model research.

In particular, the prior “asia_to_europe” bucket mixed multiple Asia/overnight states and must not be used as W1/W2 training truth.

## 14. External authorities

- Sobti, Sehgal & Ilango (2021), *International Review of Financial Analysis* 78, 101893. Five sequential zones: Asia Morning, Asia Afternoon, Europe, NY/London overlap, US.
- Shanghai Gold Exchange official trading schedule: night 20:00–02:30; morning 09:00–11:30; afternoon 13:30–15:30 (venue schedule/announcements).
- LBMA: Gold Price auctions commence 10:30 and 15:00 London time.
- CME Group: benchmark Gold futures trade approximately 23 hours per trading day.
- Twelve Data: intraday timezone can be explicitly requested; returned `datetime` denotes the bar-open time.
- IANA timezone database / Python `zoneinfo`: date-aware DST transitions.

## 15. Next gate

Before any session model is fit:

1. backfill governed XAU/USD 15-minute UTC data for 2023–2025;
2. create the five labels from this contract;
3. produce boundary-bar coverage and DST-transition audits;
4. verify a sample of winter, summer, US-only-DST, and UK-only-DST/mismatch dates;
5. only then begin expert-by-window predictive testing.
