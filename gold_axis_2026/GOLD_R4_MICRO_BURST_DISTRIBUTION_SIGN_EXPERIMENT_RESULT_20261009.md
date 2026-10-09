# R4 Mechanism falsification completed: One-minute diffuse-versus-concentrated DIR4 correction
**2026-10-09. STATUS: actual read-only Neon experiment, completed; none promoted.**
Authored prerequisite BEFORE conditional outcomes: `GOLD_R4_20261009_MICROSTRUCTURE_BURST_VS_DISCRETE_SIGN_PREREG.md`.
The 2023-25 source is same 17 completed Dukascopy-derived XAUUSD BID+ASK M15 closes for 09TR→17TR; source of high-frequency independent inspection is historical Twelve Data 1-minute close cache first downloaded Sep2026 (so NO archived original PIT from 2023). Changed candidate events follow original frozen DIR4 prereg from previous R3. Do not fit threshold on inspected 2025 labels or 2026 outcomes.

## Fixed rules
B4 = sign(net last4h logret), full DAY eligible target. DIR4 = if one of last16 returns contributes >=50% of last4h M15 squared variation, invert the sign of that dominant M15 return, otherwise B4.
For ONLY events where DIR4 changes B4, require 16 contiguous one-minute close observations spanning that 15m interval and both one-minute endpoint vs Dukascopy M15 counterpart deviations <=5 basis points.
qfrac = largest one-minute return squared / total 15 one-minute returns squared:
- X1: apply original DIR4 flip if source passes and qfrac < 0.5 (DIFFUSE), otherwise B4.
- X2: apply original DIR4 flip if source passes and qfrac >= 0.5 (ONE-MINUTE-CONCENTRATED), otherwise B4.
Both threshold and fallback to B4 frozen before new conditional outcomes. These are proxies; qfrac>=0.5 is NOT a Lee-Mykland/BNS jump detection.

## Actually scored same-year paired metrics (balanced accuracy BA; N full original DAY population)
| Year | Full N | DIR4 changed | 1m source-qualified | Diffuse qualified | Concentrated qualified | B4 BA | Original DIR4 BA | X1 diffuse-only BA | X2 concentrated-only BA |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 256 | 31 |31|25|6|48.34|50.97|50.21|49.10|
| 2024 | 259 |22|22|18|4|50.43|52.89|53.10|50.21|
| 2025 inspected |258|28|19|13|6|53.94|55.58|54.76|55.52|

DOWN recall:
- 2023 B4 51.52%, DIR4 57.58%, X1 56.06%, X2 53.03%.
- 2024 B4 46.43%, DIR4 50.00%, X1 51.79%, X2 44.64%.
- 2025 B4 54.46%, DIR4 50.89%, X1 52.68%, X2 56.25%.

Corrected/broken decisions against B4 (exact McNemar 2-sided p):
- 2023 original19/12 (p=.28104), diffuse15/10 (p=.42436), concentrated4/2 (p=.68750).
- 2024 original14/8 (p=.28628), diffuse12/6 (p=.23788), concentrated2/2 (p=1.000).
- 2025 original17/11 (p=.34493), diffuse8/5 (p=.58105), concentrated5/1 (p=.21875).

Caution: The 2025 1min source-quality gate covers only19/28 original change events, with 9 missing/mismatched. X1/X2 force unmatched cases to original B4, so same-year results are source-conditioned, not equal coverage to original DIR4. Conservative year-complete N reported to prevent inflated selected-cohort accuracy.

Gross long/short midpoint idealized signed log-return (NOT bank-executable net PnL):
- 2023 B4 .02725, DIR4 .00969, X1 .01579, X2 .02115.
- 2024 B4 .03927, DIR4 .09704, X1 .07989, X2 .05643.
- 2025 B4 .10928, DIR4 .21819, X1 .13541, X2 .19356.

## Scientific verdict
A minute-scale reclassification **does not reliably identify a dominant price-pressure mechanism that raises signed DAY skill above the frozen original DIR4**. The diffuse-only X1 slightly improves 2024 but loses versus original in 2023 and2025; concentrated-only X2 inconsistent and sparse (6/4/6 events). No statistically robust paired improvement, and 2025 source inconsistency weakens inference. Therefore REJECT X1 and X2 as standalone forecasting solutions, do not optimize qfrac cutoffs based on observed outcomes. Previous R3 descriptive tiny DIR4 DAY effect persists, not an actionable champion. No clear signed edge in OVN.

**Next source-science route**: acquire one truly independent minute/hour FX USD shock (e.g. EUR/USD or USD/JPY) **pre-decision** with vendor rights and historical clocks, then test *incremental* signed information beyond XAU own return and original fixed DIR4 on exactly common dates. This should not be called data available until live entitlement + source test passes. Do not make another DOMINANT/SHOCK same-price repackaging with new thresholds. Literature: https://www.sciencedirect.com/science/article/pii/S1057521921002209 (Sobti et al 2021 intraday information leadership), https://www.sciencedirect.com/science/article/pii/S1057521925004673 (Sobti 2025 gold jumps/news/flow), and https://www.sciencedirect.com/science/article/pii/S0378426611000896 (macro related jumps have different persistence).
