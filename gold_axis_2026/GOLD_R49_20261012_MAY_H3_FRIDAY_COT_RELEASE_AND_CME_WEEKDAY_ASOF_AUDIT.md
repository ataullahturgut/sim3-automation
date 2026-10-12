# R49 — 2026 May H3 weekday and Friday-release event-time clock audit

Date: 2026-10-12. Status: **WEEKDAY_DATE_PASS; FRIDAY_COT_DUAL_CLOCK_AUDITED; CME_MAY22_PUBLIC_FTP_METADATA_CORRECTS_PREVIOUS_CAUTION; MODEL_UNCHANGED**.

## Mandate and immutable source
Original 21 May 2026 H3 forecasts and forecast issue/cutoff/target dates come from R46 (original D0 → third *retained public-source daily price observation* D3, next date D1 is issue), not from calendar days and not from an execution-hour re-label. All 21 rows were independently checked with actual UTC civil-calendar day-of-week.

Machine-readable per-issue labels: `GOLD_R49_20261012_MAY_H3_FRIDAY_FIRST_COT_CME_SOURCE_WEEKDAY_CLOCK_LABELS.csv`. It has issue/cutoff/target weekday, Monday/Friday flags, each H3 Friday origin next-Saturday completion, exact COT original observed report, official Friday release, conservative legacy availability date and latest officially released report at 15TR, and CME daily volume trading date/file/listing metadata. No model fit, target changes or new directional scores.

## 1. Five Friday issue dates (2026, Turkey)
| Forecast issue (Friday) | Source cutoff (Thursday) | Original H3 target (Tuesday) | Status |
|---|---|---|---|
| **May01 Fri** | Apr30 Thu | May05 Tue | PASS |
| **May08 Fri** | May07 Thu | May12 Tue | PASS |
| **May15 Fri** | May14 Thu | May19 Tue | PASS |
| **May22 Fri** | May21 Thu | May26 Tue | PASS |
| **May29 Fri** | May28 Thu | Jun02 Tue | PASS |

A Friday issue before 15TR can NEVER consume a COT report first released on the *same Friday 22:30TR*. Next normal issue at 15TR after COT release is the following Monday. Source `target_end_date_h3` counts source-observation rows, not 72 clock hours, US COMEX trade days, or +3 days from the D1 issue.

**Friday origin case:** for Monday issue e.g. **May25 Mon** uses Friday **May22** D0 full UTC daily average (May22 03TR → **May23 Sat03TR**) and same-Friday hourly Twelve Data NY16 candle (May22 Fri23TR → May23 Sat00TR). The origin is complete by Saturday 03TR at the observation layer. Original H3 target is **May27 Wed**; H3 retains May25 source spot observation despite CME Memorial Day. Do not omit or shift May25 from the original source calendar merely because CME holiday trading was nonstandard.

## 2. Exact CFTC Tuesday REPORT and Friday PUBLICATION calendar
Official CFTC 2026 release schedule: **2026 May 01,08,15,22,29**, at **15:30 America/New_York (EDT) = 22:30 Europe/Istanbul**, event times 19:30UTC. Official current reference: https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm .

| Tuesday as-of underlying position date | Official COT publication Friday 22:30TR | First standard May H3 issue at/after publication |
|---|---|---|
| Apr21 Tue | Apr24 Fri | Apr27 Mon |
| Apr28 Tue | May01 Fri | May04 Mon |
| May05 Tue | May08 Fri | May11 Mon |
| May12 Tue | May15 Fri | May18 Mon |
| May19 Tue | May22 Fri | May25 Mon (US Memorial Day; the frozen source DOES retain H3 issue) |
| May26 Tue | May29 Fri | Jun01 Mon |

**Important: existing COT authority is INTENTIONALLY more conservative, not an incorrect date conversion.** Current `GOLD_COT_PIT_AVAILABILITY_AUTHORITY_2026-10-06.md` requires `report_date + 7d at 15:30 NY` even for normal release weeks, with later holidays/backlogs overridden. Legacy `gold_h3_opal_v1.py` similarly uses a DATE-only `AVAIL_LAG_DAYS=7` and joins by **feature_cutoff_date**, not the precise real D1 issued_at. This remains the binding old-model replay rule and MUST NOT be silently overwritten.

For 15TR issue-time counterfactual **official Friday-first** as-of lookup, compared with frozen model-selected COT report, exactly **8/21 May issues** differ: May04/05 (official Apr28 versus legacy Apr21), May11/12 (May05 versus Apr28), May18/19 (May12 versus May05), May25/26 (May19 versus May12). These are **allowed-to-be-known** report selection differences, **NOT proof** live price vintage/OPAL model coefficients existed at the issue time and **NOT a justified change in model accuracy**. All 5 May Friday 15TR issue decisions correctly retain last week's already released report, rather than Friday night release.

If Friday-based freshness is desired in future, build explicitly separate `COT_OFFICIAL_FRIDAY_ASOF_V2` keyed to an ACTUAL forecast_eligible_at / issue timestamp, with release calendar overrides, retrain from point-in-time public data and chronologically evaluate all experts and withheld periods. Do not replace the governed +7d COT calendar because its historical PIT-breach remediation for 2023/2025 would be silently removed.

## 3. CME Friday volume and US Memorial Day 25 May
Official live CME FTP directory listing https://www.cmegroup.com/ftp/pub/pub/daily_volume/ explicitly lists:
- `daily_volume_20260501.xlsx` — displayed Last Modified **May04 00:01**;
- `daily_volume_20260508.xlsx` — **May11 00:01**;
- `daily_volume_20260515.xlsx` — **May18 00:01**;
- `daily_volume_20260522.xlsx` — **May25 00:01**;
- `daily_volume_20260529.xlsx` — **Jun02 00:11**.
The FTP directory's **display-time timezone is not established**, and last-modified timestamps do **not** prove first historical publication or all original contents. All 21 selected source CME file displayed-modification **dates precede their corresponding H3 forecast issue DATE**, which is evidence against the previous hypothetical May26 file-late-to-15TR assertion.

**Correction of previous warning:** May26 Tue H3 / cutoff May25 Mon uses 22May Fri COMEX GC+options volume file. That **file is already listed with May25 Mon 00:01 last-modified date**, and so treating May26 Tue as necessarily too early for Friday data because of Memorial Day is **unsupported and wrong**. The verified CME holiday schedule covers **May24–26** and has modified sessions. There is no `daily_volume_20260525.xlsx` in the public directory even though daily UTC spot-source labels include May25. Must separate **COMEX trade date** from **source OTC gold UTC observation date**. Official CME holiday reference https://www.cmegroup.com/trading-hours.html .

**No 2026 May CME date mismatch in original RTE**: `gold_h3_rte_v1.py` uses only `cme_trade_date < feature_cutoff_date`; Friday/holiday properly handled by *existing FTP-trade-date rows*, not a weekday arithmetic `previous US business day` assumption. A historical FTP firstprint/archive-snapshot gate is still unproven, but a forced Tuesday-18TR delay for May22 would be worse than using real file listing evidence.

## 4. Source clock tags retained
- Daily Au/Ag/Pt/Pd `sqld` UTC day D: D03TR to next-date03TR; Friday D Friday03TR→Saturday03TR, irrespective of CME week-end.
- Twelve Data NY16 hourly candle: timestamp is START (Fri23TR in May), close value becomes knowable **Sat00TR**; exact provider retrieval time remains unknown.
- COT Tuesday underlying observation: never treat as immediately published Tuesday. Separate Friday22:30 official publish and governed next-Tuesday22:30 conservative use.
- CME Friday daily GC volume: trade date Friday; FTP file last-modified displayed on next Monday in ordinary calendar, no Friday same-day volume assumed.
- RTE crossmarket labels currently require `date < feature_cutoff_date` and are not proven firstprint; retained as recorded.
- H3 result matured target full UTC day after its dated day at TRT 03:00; release lag/open-vintage caveat unchanged.

## 5. Audit result
- Issue/cutoff/target **calendar weekday identity PASS 21/21**;
- Five Friday issue → Thursday source / Tuesday D3 targets exactly;
- Four Monday issue → prior Friday source; including May25 US holiday source-vs-CME calendar distinction;
- COT official-Friday vs intentionally conservative current-policy COT report selection differs in **8/21**, not just four Mondays;
- CME 22May Friday file listing predates the 26May Tuesday issue, so retract previous unsupported late-publication alarm;
- No live May Q95 accuracy asserted, model predictions unchanged, native H3 result 17/21 remains R48 frozen-data retrospective only.

## Authoritative evidence
CFTC official 2026 release schedule https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm
CME FTP directory https://www.cmegroup.com/ftp/pub/pub/daily_volume/
CME 2026 holiday hours https://www.cmegroup.com/trading-hours.html
Current project COT conservative authority `GOLD_COT_PIT_AVAILABILITY_AUTHORITY_2026-10-06.md`, `GOLD_COT_PUBLICATION_CALENDAR_PIT_V1.csv`.
