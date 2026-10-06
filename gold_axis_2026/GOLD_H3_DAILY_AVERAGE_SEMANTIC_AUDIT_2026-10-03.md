> **SOURCE-SEMANTIC CORRECTION — 2026-10-06:** The similarity to a Twelve Data UTC-calendar-day hourly mean is a cross-provider comparator only. It does **not** prove that the StakTrakr daily value is itself a full-UTC-day average. The recovered daily realization series has been traced 145/145 to pinned StakTrakr daily history, whose stored noon timestamp is a synthetic calendar-date label rather than an executable observation time. Binding authority: `GOLD_DAILY_REALIZATION_SOURCE_AUDIT_2026-10-06.md`. Any "full-UTC-day-average semantic" wording below is superseded as a source-semantic claim.

# GOLD H3 DAILY-AVERAGE SEMANTIC AUDIT — 2026-10-03

Comparator: Twelve Data XAU/USD 1h, requested in UTC, aggregated to arithmetic mean of hourly closes per UTC calendar day. This is a cross-provider approximation to the StakTrakr STRK-403 full-UTC-day-average semantic.

## Level audit

- hourly observations: **6527**
- weekday daily overlaps: **193**
- median Stak / Twelve-hourly-mean ratio: **1.000118**
- clean deviations >=1%: **1**
- >=2%: **0**
- >=3%: **0**
- >=5%: **0**
- max deviation: **1.05%** on **2026-02-18**
- clean Stak value outside Twelve hourly min/max: **1**

## H3 direction using matched daily-average semantics

- comparable origins: **190**
- direction disagreements: **8 (4.21%)**
- disagreements with both |H3| >=0.5%: **2**
- disagreements with both |H3| >=1.0%: **0**

## Flagged daily levels

| Date | Clean Stak | Twelve mean | Hour n | Twelve min | max | Deviation | In range |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-04-03 | 4676.71 | 4676.45 | 24 | 4676.23 | 4676.63 | 0.01% | False |

## Direction disagreements

| Start | End | Stak H3 | Twelve-mean H3 |
|---|---|---:|---:|
| 2026-01-05 | 2026-01-08 | -0.104% | +0.416% |
| 2026-02-04 | 2026-02-09 | -1.180% | +0.524% |
| 2026-02-09 | 2026-02-12 | +1.143% | -0.369% |
| 2026-02-13 | 2026-02-18 | +0.975% | -0.871% |
| 2026-02-16 | 2026-02-19 | +0.484% | -0.092% |
| 2026-02-23 | 2026-02-26 | -0.684% | +0.061% |
| 2026-04-29 | 2026-05-04 | +0.014% | -0.037% |
| 2026-08-13 | 2026-08-18 | +0.029% | -0.007% |
