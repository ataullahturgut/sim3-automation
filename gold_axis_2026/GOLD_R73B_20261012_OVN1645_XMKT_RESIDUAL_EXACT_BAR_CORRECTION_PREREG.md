# R73B PREREGISTRATION — exact-bar time-alignment correction of R73 (no model change)

This file was written **before** any corrected-panel model output was computed. The original R73 prereg (`2371b588`), its report and its numbers stay unchanged; R73B is an additive correction.

## 1. Defect being corrected (verified independently)

The R73 v1 panel SQL selected CME prices with `ts_event BETWEEN start-3h AND start-1h ORDER BY ts_event DESC LIMIT 1` (and `BETWEEN 10:00 AND 12:00` for the end bar). Where the exact bar was missing, an earlier bar was silently used, so XAU and ZN/NQ/CL returns could cover different intervals. This look-back was written into the R73 prereg as an "as-of last trade" rule, but it breaks exact interval matching.

Verified on Neon with a single-pass exact-hour check (2026-10-12): among the 624 nights scored in R73 W7, **41** lack at least one exact start/end bar for at least one root. By year: 2023 8, 2024 14, 2025 11, 2026 8. This matches the external audit exactly. In W3, 43 of 652 scored nights are affected (2023 9, 2024 13, 2025 13, 2026 8). Nearly all cases are ZN in quarterly roll weeks; a few are CL 05:00 UTC gaps.

## 2. Corrected definitions (R73B primary)

CME `ts_event` = bar START (unchanged). Istanbul = UTC+3.

| Window | Start price | End price |
|---|---|---|
| W7 = 09:00→16:00 TR | close of the bar with `ts_event = D 05:00 UTC` exactly (ends 06:00 UTC = 09:00 TR) | close of the bar with `ts_event = D 12:00 UTC` exactly (ends 13:00 UTC = 16:00 TR) |
| W3 = 13:00→16:00 TR | close of the bar with `ts_event = D 09:00 UTC` exactly (ends 10:00 UTC = 13:00 TR) | same exact 12:00 UTC bar |

- All three roots must have both exact bars.
- The start and end bars must carry the same `instrument_id`, giving continuity within the same contract.
- Otherwise the CME return is NULL for that root, and the whole day is unusable for **both** training and prediction.
- There is no shifting, interpolation, forward fill or substitute bar.
- XAU feature prices are unchanged from v1: mid of the M15 bar closing at 06:00/10:00/13:00 UTC. The target is unchanged: 13:45 UTC open → next calendar day 06:00 UTC open, Mon–Thu.
- No feature uses data completed after 13:00 UTC (16:00 TR), which is before the 16:45 decision.
- Consequence: wherever both exact bars exist, the v2 value is identical to v1, because v1's "latest bar" was then the exact bar. v2 = v1 with non-exact days removed. This identity will be checked in SQL.

## 3. Model — frozen, identical to R73

Rolling ridge on standardized ZN/NQ/CL, intercept, alpha = 10, most recent 250 prior eligible weekdays (training rows must also pass the exact-bar rule), minimum 60, rule `sign(−residual)`. Comparators are R_REV, R_MOM, ALWAYS_UP/DOWN and R67 (`new_pred`, `h3bit`) on matched dates. Gates H1/H2/H3 and the verdict mapping are exactly as in the R73 prereg. Holm is applied across W7/W3. DEV = 2023–24; 2025/2026 are retrospective.

## 4. Pre-declared sensitivity analyses (reported, never used to select a model)

- **S-FULL7:** additionally require all seven in-window bars 06:00–12:00 UTC for all three roots.
- **S-SRC (source mixing):** for 2026 prediction dates, count training rows from `EVDUKA_2020_2025` against `DUKA_DIRECT_2026`. Then re-score 2026 with training restricted to same-source (`DUKA_DIRECT_2026`) rows only. Model, alpha and window are unchanged; the minimum of 60 still applies, so early-2026 dates drop out. Comparison is made on the common 2026 dates.
- **Common-date decomposition:** compare v1 against v2 on dates scored by both, splitting into (a) dates dropped, (b) common dates whose prediction changed because the training sample changed, and (c) common dates with an unchanged prediction.

If the corrected primary still fails H1, the verdict stays **REJECT**. No new window, threshold, factor or parameter will be searched.
