# GPT-6 P3 — calendar-conditioned rolling HAR500 M15 RV (independent)
**Result: DEV 2023/24 improvement, 2025 transport fails → REJECT / NO PROMOTION.** Prereg commit `a3832388` before the specific outcome comparison. This predicts *observed subinterval variance*, not UP/DOWN XAUUSD price or profit.

Source: strict EV/Dukascopy M15 complete DAY09→16:45 (issue08:45) / OVN16:45→next09 (issue16:30), TR timezone, 2020–25; 2740 source windows. Relative to original PR #91 H3A frozen HAR, **new** rolling latest500 historical complete sessions separately each window, fitted alpha10 ridge and one macro calendar binary factor: US 08:30ET CPI/NFP release day in DAY; regular scheduled 14:00ET FOMC event day in OVN. Historical CPI/NFP dates are archived `MACRO_*_ACTUAL_FIRST_PRINT`, not independently validated *advance published schedules*: **2025 US shutdown-related shifts are not point-in-time schedule certified**. DAY feature is retrospective scenario only. 2025 explicitly opened, not untouched.

| Window | Year, N | Previous Persist5 QLIKE | original PR91 H3A | rolling HAR500 | **rolling HAR500+EVENT** |
|---|---|---:|---:|---:|---:|
| DAY | 2023,256 | .279311 | .238694 | .244444 | **.202024** |
| DAY | 2024,259 | .317138 | .268061 | .280646 | **.220286** |
| DAY | 2025,258 | **.267952** | .289526 | .287257 | .278479 |
| OVN | 2023,198 | .217079 | .197824 | .200501 | **.169147** |
| OVN | 2024,197 | .241976 | .225200 | .229330 | **.171618** |
| OVN | 2025,198 | **.206006** | .249093 | .228243 | .232483 |

Three-month block bootstrap historical DEV difference baseline minus EVENT 95% CI:
- DAY vs ROLL500 [+0.02313,+0.08828], vs Persist5 [+0.04397,+0.13740]
- OVN vs ROLL500 [+0.02027,+0.07016], vs Persist5 [+0.02757,+0.09366].
All four DEV paired CIs above zero (P3's retrospective selected hypothesis; source vintage caveat). Yet in 2025 **both windows fail to beat best Persist5**, OVN also fails against ROLL500. **NO promotion** despite encouraging DEV variance gains.

**Interpretation:** Time-aware known-event covariate looks substantively explanatory for *volatility magnitude* when tested in DEV; robust 2025 transport isn't established. No directional-return model promoted. FOMC scheduled-event flag actually requires event dates from official calendars; Fed 2020 unscheduled actions excluded. CPI/NFP historical event first-print does not prove that the exact rescheduled date was known at 08:45, so use fail-closed policy on operational as-of statements.

Artifacts: raw `GOLD_GPT6_P3_TRAINING_SOURCE_RV_EVENTS.csv`, `GOLD_GPT6_P3_MACRO_EVENT_DATES_2020_2025.csv`, extraction SQL, scored `GOLD_GPT6_P3_SCORE_ROWS.csv` and `GOLD_GPT6_P3_RESULT.json`, Python model replay `tools/gold_gpt6_p3_replay.py`. Original PR91 model and its code/results unmodified.
