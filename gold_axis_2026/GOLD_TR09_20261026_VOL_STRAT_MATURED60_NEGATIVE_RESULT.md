# TR09 H3 — volatility-stratified matured60 calibration: executed, preregistered cross-year rejection (2026-10-26)

**Verdict: REJECT, no model promotion and no user alert**: the fixed preregistered two-year acceptance criterion fails. The modest risk Brier gains against frozen vol Q75 are not sufficient to rescue poor 2025 directional classification or beat the 2026 pooled matured60 benchmark. Keep canonical manifest and all existing models unchanged.

## Audit trail
- Checked branch HEAD `b3f4e67995f058a703bb5ec6d0614b43eb1b4766` and canonical `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` blob `279dae0b2d5694593adda076d644a5d186241304` BEFORE this work.
- Preregistration `GOLD_TR09_20261026_VOL_STRATIFIED_MATURED60_PREREG.md`, committed `b36e69f817dd8ce345b237bd5a8b59218f305435` BEFORE any outcome scoring.
- Executable READ-ONLY SQL `tools/gold_tr09_20261026_vol_strat_matured60_reproduce.sql`, committed `e0aceb9ea10e730b1e9cfaf24b0bd3e893e06d57` BEFORE execution, blob `7457bd0857615368797866ed2bb086460b6032c3`. Actual SQL executed via connected Neon `winter-art-94880101`, `public.gold_research_histdata_xau15m_candidate`; independent second SQL grouped the online results by year × regime and confirmed counts, calibration and no lookahead.
- Data source historical HistData fixed EST M1 aggregated native 15m, retrieved 2026-10-08; 08:45–09:00 Europe/Istanbul completed 15m close used as 09:00 reference. This is **NOT proof of a 09:00 executable quote or historical firstprint**. 3 NEXT eligible business-date 09:00 target, fixed enumerated holiday exclusions, 2026-09-25 missing quote treated as outage. All five past anchors and target must exist. No future label admitted until target_date<origin date.
- Purged 2023–24 train N=496; 2023–24 volatility Q75=0.010206552832574104. Frozen online window 60 already-matured historical labels, 20 group-prior pseudo-observations, group HIGH iff v5>Q75. All 2025/26 rows have exactly 60 matured records; same-regime subset count 4–56 (2025), 4–57 (2026); **0** maturity violations. Frozen arms do not use online matured labels, a genuine difference in information budget.

## Equal-row results
BA = (UP recall + DOWN recall)/2; Brier lower is better. Both online arms and all five frozen arms share EXACTLY the same eligible rows in each year.

| Year | Arm | N | BA % | UP recall % | DOWN recall % | Direction Brier | >=2% DOWN Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| 2025 | Constant | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2400672 | 0.0822839 |
| 2025 | Two-UP | 258 | 52.5133 | 68.9441 | 36.0825 | 0.2406951 | 0.0822271 |
| 2025 | Vol Q75 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2440358 | 0.0795049 |
| 2025 | Max drawdown Q75 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2402204 | 0.0820787 |
| 2025 | Calendar>=5 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2401858 | 0.0821760 |
| 2025 | Matured60 pooled (prior study parity) | 258 | 47.2850 | 83.2298 | 11.3402 | 0.2448019 | 0.0843355 |
| 2025 | **NEW vol-strat matured60** | **258** | **45.9499** | **85.7143** | **6.1856** | **0.2471405** | **0.0787308** |
| 2026 Jan–Sep | Constant | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2535882 | 0.1920017 |
| 2026 Jan–Sep | Two-UP | 188 | 46.2183 | 68.4783 | 23.9583 | 0.2609284 | 0.1922523 |
| 2026 Jan–Sep | Vol Q75 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2585391 | 0.1882070 |
| 2026 Jan–Sep | Max drawdown Q75 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2545877 | 0.1908302 |
| 2026 Jan–Sep | Calendar>=5 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2531117 | 0.1914909 |
| 2026 Jan–Sep | Matured60 pooled (prior study parity) | 188 | 57.0199 | 61.9565 | 52.0833 | 0.2512439 | **0.1767554** |
| 2026 Jan–Sep | **NEW vol-strat matured60** | **188** | **57.7672** | **72.8261** | **42.7083** | **0.2480173** | **0.1792687** |

Actual events: 2025 161 UP /97 DOWN /23 >=2% DOWN; 2026 92 UP /96 DOWN /40 >=2% DOWN.

**Paired same-row comparisons**:
- NEW tail Brier vs frozen Vol Q75: 2025 0.0795049 -> 0.0787308 (gain 0.0007741, ~0.97%); 2026 0.1882070 -> 0.1792687 (gain 0.0089383, ~4.75%).
- NEW tail Brier vs pooled online: 2025 0.0843355 -> 0.0787308 (gain 0.0056047); 2026 0.1767554 -> 0.1792687 (**worsens 0.0025133**).
- Direction 2025 BA **45.95%** vs constant 50% and two-UP 52.51%; 2025 direction Brier **0.2471405** vs constant 0.2400672. Fails prereg BA and direction calibration gates.

## Independent year × regime verification (second read-only SQL)
| Year | Regime | N | Actual severe DOWN | Mean predicted tail NEW | Mean predicted tail pooled | Tail Brier NEW | Tail Brier pooled |
|---|---|---:|---:|---:|---:|---:|---:|
| 2025 | LOW | 155 | 2 | 0.036606 | 0.074137 | 0.0137916 | 0.0182446 |
| 2025 | HIGH | 103 | 21 | 0.129969 | 0.077042 | 0.1764548 | 0.1837927 |
| 2026 | LOW | 37 | 12 | 0.140991 | 0.173854 | 0.2645324 | 0.2587184 |
| 2026 | HIGH | 151 | 28 | 0.155840 | 0.166126 | 0.1583762 | 0.1566718 |

2026 LOW actual tail 12/37=32.43% while HIGH 28/151=18.54%, reversing 2025 LOW 2/155=1.29%, HIGH 21/103=20.39%. This cross-year reversal was ALREADY identified in 2026-10-22 experiment; it is **not** claimed as new discovery. New stratified calibration underestimates 2026 LOW risk, consistent with instability. All maturity audits in independent query 0 violations.

## Scientific decision
Predeclared acceptance required tail Brier better than constant, frozen Vol Q75, AND pooled matured60 in EACH 2025 and 2026, plus BA>=50%, nonzero DOWN recall, and no material direction Brier deterioration in BOTH. It fails 2026 pooled comparator and 2025 BA/direction calibration. Do not optimize threshold, window, pseudo-count or select years after observing 2025/26. Three-day outcomes overlap; 2025/26 are repeatedly inspected retrospective transports, **not independent validation**. No verified origin-time source publication, no bank bid/ask/spread. 2027 prospective pre-outcome issue and timestamp-certified source is required before any model promotion. This is a negative research result retained to prevent redundant future work; no user notification threshold met.
