# GOLD H3 NEON CROSS-SOURCE AUDIT — 2026-10-03

**Mode:** READ ONLY.

## 2026-02-24 .. 2026-03-04 exact database values

| Series | Date | Value | Revisions | Distinct values |
|---|---|---:|---:|---:|
| XAG_STAKTRAKR_RESEARCH_DAILY_R1 | 2026-02-24 | 87.080000 | 1 | 1 |
| XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1 | 2026-02-24 | 5143.595150 | 1 | 1 |
| XAU_STAKTRAKR_RESEARCH_DAILY_R1 | 2026-02-24 | 5136.060000 | 1 | 1 |
| XPD_STAKTRAKR_RESEARCH_DAILY_R1 | 2026-02-24 | 1774.730000 | 1 | 1 |
| XPT_STAKTRAKR_RESEARCH_DAILY_R1 | 2026-02-24 | 2147.330000 | 1 | 1 |
| XAG_STAKTRAKR_RESEARCH_DAILY_R1 | 2026-02-25 | 90.780000 | 1 | 1 |
| XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1 | 2026-02-25 | 5164.815720 | 1 | 1 |
| XAU_STAKTRAKR_RESEARCH_DAILY_R1 | 2026-02-25 | 5212.100000 | 1 | 1 |
| XPD_STAKTRAKR_RESEARCH_DAILY_R1 | 2026-02-25 | 1816.480000 | 1 | 1 |
| XPT_STAKTRAKR_RESEARCH_DAILY_R1 | 2026-02-25 | 2320.540000 | 1 | 1 |
| XAG_STAKTRAKR_RESEARCH_DAILY_R1 | 2026-02-26 | 86.700000 | 1 | 1 |
| XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1 | 2026-02-26 | 5184.817290 | 1 | 1 |
| XAU_STAKTRAKR_RESEARCH_DAILY_R1 | 2026-02-26 | 5178.700000 | 1 | 1 |
| XPD_STAKTRAKR_RESEARCH_DAILY_R1 | 2026-02-26 | 1761.600000 | 1 | 1 |
| XPT_STAKTRAKR_RESEARCH_DAILY_R1 | 2026-02-26 | 2236.960000 | 1 | 1 |
| XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1 | 2026-02-27 | 5278.636210 | 1 | 1 |
| XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1 | 2026-02-28 | 5277.921420 | 1 | 1 |
| XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1 | 2026-03-01 | 5277.920540 | 1 | 1 |
| XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1 | 2026-03-02 | 5322.134170 | 1 | 1 |
| XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1 | 2026-03-03 | 5088.512670 | 1 | 1 |
| XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1 | 2026-03-04 | 5140.826780 | 1 | 1 |

## StakTrakr XAU vs independent NY17 hourly-derived XAU

- overlap: **1089** dates
- median level ratio Stak/NY17: **0.999830**
- severe flags (>=5% deviation from normal ratio OR robust |z|>=8): **0**

| Date | Stak | NY17-derived | Approx dev from normal ratio | Robust z |
|---|---:|---:|---:|---:|

## Multi-metal coincident extremes

- flagged dates: **5**

| Date | >=8z assets | >=6z assets | Max | Gold r | Silver r | Platinum r | Palladium r |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-01-30 | 4 | 4 | 17.3 | -8.30% | -13.79% | -22.04% | -15.66% |
| 2020-03-16 | 3 | 4 | 13.6 | -5.40% | -19.59% | -11.64% | -13.82% |
| 2026-02-02 | 2 | 2 | 16.0 | -7.76% | -23.02% | -6.88% | -6.04% |
| 2013-04-15 | 2 | 2 | 11.4 | -8.91% | -15.18% | -5.05% | -6.89% |
| 2011-09-26 | 2 | 3 | 10.8 | -6.88% | -15.56% | -9.46% | -5.72% |

## XAUS daily revisions

- latest-dedup timestamps with conflicting stored values: **125**

Flags are candidates only. A large true market move can be a statistical outlier; correction requires independent source confirmation.
