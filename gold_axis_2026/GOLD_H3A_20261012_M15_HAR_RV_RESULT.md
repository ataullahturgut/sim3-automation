# H3A — future-session realized variance from predecision M15 XAU/USD
**Scientific verdict: REJECT / NO PROMOTION under the fixed strict transport gate.** Original prereg commit `60ebc230` precedes computations. This is an analysis of **volatility magnitude / distribution**, not an XAU direction or future price estimate.

## Data and clock
2020–2025 EV/Dukascopy archived XAU/USD MID M15, 09:00→16:45 Europe/Istanbul DAY, 16:45→next09:00 OVN (Mon–Thu only). DAY exactly 31 contiguous 15-minute bars; OVN exactly 61 available bars, with one 75-minute market quotation closure and all other gaps precisely 15 minutes. Missing/incomplete windows explicitly excluded, **no interpolation**. The RV target omits returns across the 75-minute closure (not full integrated overnight variance). All historical lag RV observations are **completed before** decision window. Archived quotes not certified as contemporaneously first received.

Historical source panels committed per year 2020–2025 (DAY: 1547, OVN: 1193 rows); model-score rows `1366` in 2023–2025. Feature `logRV(last1),mean(logRV(last5)),mean(logRV(last22))`; fixed ridge alpha10 chronological, 2025 model coefficients frozen through 2024. Three price-direction-independent log-RV baseline competitors. Outcome primary QLIKE (lower better).

## DAY 09:00→16:45, future M15 observed realized variance
| Year | N | HAR | Clim60 | Persist5 |
|---|---:|---:|---:|---:|
| 2023 | 256 | 0.23869 | 0.28657 | 0.27931 |
| 2024 | 259 | 0.26806 | 0.30152 | 0.31714 |
| 2025 opened | 258 | 0.28953 | 0.48802 | 0.26795 |
| DEV | 515 | 0.25346 | 0.29409 | 0.29834 |

2023 and 2024 HAR is better than every control numerically, but **3-month block-bootstrap QLIKE improvement versus Clim60 CI [-0.00386, 0.10148] crosses zero**. And opened 2025 HAR loses to Persist5 (**0.28953 vs 0.26795**). DAY fails original gate.

## OVN 16:45→next 09:00, future M15 observed realized variance
| Year | N | HAR | Clim60 | Persist5 |
|---|---:|---:|---:|---:|
| 2023 | 198 | 0.19782 | 0.25693 | 0.21708 |
| 2024 | 197 | 0.22520 | 0.29832 | 0.24198 |
| 2025 opened | 198 | 0.24909 | 0.62842 | 0.20601 |
| DEV | 395 | 0.21148 | 0.27757 | 0.22950 |

In DEV 2023–24, HAR beats all controls every year and bootstrap CIs against Clim60 [0.00887, 0.14776], Persist5 [0.00771, 0.03073] stay above zero. This is an **interesting retrospective signal about movement variability**. In previously observed **2025 HAR loses to Persist5** (0.24909 vs 0.20601), so **transport gate fails** and no champion changes.

## Unfinished / blocked parts
- **H3B macro-calendar enhancement:** no independently verified historical announcement *scheduling vintage* at pre-08:45/16:30 decision times for all event types. Event *actual/consensus* rows known only after release are forbidden as predecision predictors. Label H3B **BLOCKED**, not tested.
- **GVZ 2023–24 as-of daily history not available in required source; source coverage currently concentrated in 2025–26.** Do not fill back with current revisions.
- **2026 direct-M1 matching status:** present M15 table reports `m1_matched !=1` for 17184/17184 rows; source gate not certified. Do not manufacture 2026 transport results from it.
- This **does not** establish future spot return direction, bank profitability, or any change to pre-existing XAU monthly/H3 champions.

## Reproduce
- `sql/gold_h3a_20261012_yearly_source.sql` (replace year placeholders only) reproduces strict M15 session RV.
- `GOLD_H3A_20261012_SESSION_RV_2020.csv` to `...2025.csv` raw filtered session RV.
- `tools/gold_h3a_20261012_rv_replay.py` independently regenerates and checks all 1366 forecasts and losses.
- `GOLD_H3A_20261012_FIXED_HAR_SCORE_ROWS.csv` and `GOLD_H3A_20261012_M15_HAR_RESULTS.json` frozen detailed evidence.
