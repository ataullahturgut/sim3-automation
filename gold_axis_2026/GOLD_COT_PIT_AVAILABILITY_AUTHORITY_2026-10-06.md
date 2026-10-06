# GOLD COT PIT AVAILABILITY AUTHORITY — 2026-10-06

**Status:** BINDING SOURCE-AVAILABILITY AUTHORITY FOR NEW SESSION REBUILDS  
**Scope:** CFTC Disaggregated COT Gold report availability only. This document does not promote OPAL or HELIOS performance.

## 1. Problem found

Legacy OPAL used:

`available_date = report_date + 7 calendar days`

as a date-only rule.

That rule is conservative in ordinary weeks, but it fails during extraordinary CFTC publication interruptions whose actual publication delay exceeds seven days.

Independent raw-source reaudit reproduced exactly:

- 2023 proven early-use rows: **21**
- 2025 proven early-use rows: **53**
- total: **74**

The historical rows affected by the old availability rule must not be treated as PIT-clean.

## 2. Official clock

CFTC states that COT Futures Only and Futures-and-Options Combined reports are normally released at **15:30 America/New_York**.

New project code must use timezone-aware publication timestamps, not date-only availability.

## 3. Governed conservative default

For ordinary reports the project deliberately retains a conservative buffer:

`governed_available_at = report_date + 7 calendar days at 15:30 America/New_York`

This is later than normal Friday publication and therefore sacrifices freshness for leakage protection.

## 4. Official delay overrides

If CFTC documents that publication occurred later than the governed +7-day buffer, use the official delayed publication date at 15:30 ET.

### 2023 ION backlog

- 2023-01-31 report -> 2023-02-24
- 2023-02-07 -> 2023-03-03
- 2023-02-14 -> 2023-03-08
- 2023-02-21 -> 2023-03-10
- 2023-02-28 -> 2023-03-14
- 2023-03-07 -> 2023-03-16
- 2023-03-14 -> 2023-03-21

### 2025 appropriations-lapse backlog — final accelerated schedule

- 2025-09-30 -> 2025-11-19
- 2025-10-07 -> 2025-11-21
- 2025-10-14 -> 2025-11-25
- 2025-10-21 -> 2025-12-02
- 2025-10-28 -> 2025-12-05
- 2025-11-04 -> 2025-12-09
- 2025-11-10 -> 2025-12-10
- 2025-11-18 -> 2025-12-12
- 2025-11-25 -> 2025-12-15
- 2025-12-02 -> 2025-12-17
- 2025-12-09 -> 2025-12-19
- 2025-12-16 -> 2025-12-23
- 2025-12-23 -> 2025-12-29

January 2025 Carter National Day of Mourning moved the relevant release to Jan. 13, but that date is still earlier than the project's +7-day conservative availability for the Jan. 7 report; therefore the conservative timestamp remains binding.

## 5. Implementation authority

- `tools/gold_cot_publication_pit_v1.py`
- `tools/gold_cot_pit_reaudit_20261006.py`
- `GOLD_COT_PUBLICATION_CALENDAR_PIT_V1.csv`
- `GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv`
- `GOLD_OPAL_OLD_PROVEN_EARLY_COT_ROWS_2026-10-06.csv`
- `GOLD_V5_SESSION_COT_AVAILABILITY_MAP_2023_2025.csv`
- `GOLD_COT_PIT_REAUDIT_SUMMARY_2026-10-06.json`

The raw feature state is rebuilt from CFTC Public Reporting Environment:
- Disaggregated Futures Only: dataset `72hh-3qpy`
- Disaggregated Futures-and-Options Combined: dataset `kh3c-gbw2`
- COMEX Gold CFTC contract code: `088691`

Options-only exposures remain reconstructed as combined minus futures-only.

## 6. Binding use rule

Every new OPAL/session model must perform an as-of join using:

`cot_available_at_utc <= model_feature_cutoff_or_target_start_utc`

A report cannot be selected by report date alone.

Archived OPAL feature panels and predictions may be used only to reproduce/audit the 74 historical early-use rows. They are prohibited as inputs to new model fitting.

## 7. Current model implications

- OPAL legacy H3 historical performance remains contaminated for the 74 affected feature rows.
- OPAL is **BLOCKED for new session replay** until its complete session feature panel is rebuilt from raw CFTC + raw XAU sources using this authority.
- HELIOS variants that consume OPAL remain **BLOCKED downstream** until fresh OPAL session state exists.
- COT data itself is not missing: every final V5 2023–2025 session row had a governed latest-available COT report in the availability audit.

## 8. External authorities

- CFTC COT Release Schedule — normal release time 15:30 ET.
- CFTC Historical Special Announcements — 2023 ION backlog publication sequence.
- CFTC Dec. 9, 2025 press release / revised accelerated backlog schedule.
