# R4 Research Board — stop-one-model mentality, actual separate mechanisms and sourced FX experiment, Oct 9 2026
**Research outcome: source unlocked; neither mechanism earns a scientific signed champion.** No overnight bank P&L claims, no 2026 untouched promotion. User asked not to stop after a failed individual test, and this report documents two distinct actual developments after R3.

## Workstream I: XAU 15-minute physical interpretation (completed)
The authorized 2023–25 original DIR4 DAY model relies on a dominant 15m squared price return. A separate peer review noted the danger of classifying it as a genuine jump. First source-only cross-provider 1min audit found 2023 6/31 and 2024 4/22 DIR4 change events dominated by a SINGLE 1min variance increment; 2025 6/19 with only 19 of 28 licensed source matched. This suggests a dominant 15min bar is typically a *multi-minute event*, not necessarily a point jump.
New **pre-outcome** `GOLD_R4_20261009_MICROSTRUCTURE_BURST_VS_DISCRETE_SIGN_PREREG.md` froze two mutually distinct variants:
- X1 one-minute-diffuse only if 1min maximal minute QV share <0.5, else revert to B4;
- X2 one-minute-concentrated only if QV share >=0.5, else B4;
- source-mismatch/missing => B4, never synthesized price; original DIR4 and B4 compared on all original days.
Executed historical DAY on full source-qualified target universe 2023 N256,2024 N259,2025 N258. Balanced accuracy: B4 **48.34 /50.43 /53.94**, original DIR4 **50.97/52.89/55.58**, X1 **50.21/53.10/54.76**, X2 **49.10/50.21/55.52**. None improves robustly over both original DIR4 and price baseline; 2025 minute event source pass19/28 only. Statistical paired X1 rescues/breaks 2023 15/10 (p.424),2024 12/6 (.238),2025 8/5 (.581). X2 2023 4/2 (.688),2024 2/2 (1),2025 5/1 (.219). **REJECT both** as stable model improvements. Evidence: `GOLD_R4_MICRO_BURST_DISTRIBUTION_SIGN_EXPERIMENT_RESULT_20261009.md`.

## Workstream II: truly separate independent FX data route and controlled forecast trial (completed)
### Novelty and academic grounding
Rather than another gold-only pattern, test source-independent intraday USD factor as seen through EUR/USD and USD/JPY. Sobti et al. (2021, IRFA 78:101893, DOI10.1016/j.irfa.2021.101893) discusses FX shocks/price discovery state dependence in gold, **not evidence of exact Istanbul signed forecast alpha**.
Existing project broad USD/Fed-rate state and macro PRAMV proposed or tested related macro variables; this particular **intraday EURUSD+USDJPY exact-clock double-signed filter** had not been run as a source-verified study. CME3-K25 and ZN-VPT2 were NOT the same instruments, although same cross-asset research family. Do not claim architectural novelty.

### Real API source proof and limited ingestion
- Official Twelve Data API docs explicitly allow Forex H1 with `timezone=UTC` and historical `start_date/end_date`: https://twelvedata.com/docs .
- Four minimal preflight GETs using the existing authorized GitHub Actions `TWELVE_DATA_API_KEY`: EUR/USD and USD/JPY 2023 and2025, each55 historical one-hour observations and provider identity verified. `GOLD_R4_TWELVE_INDEPENDENT_FX_H1_SOURCE_PROBE_20261009.json`; all passed.
- **12 subsequent capped calls** (two pairs × Jan–Jun / Jul–Dec × 2023–25) actually executed, one per >=8.2s to respect provider call-frequency, 1h UTC archived bars from each halfyear. Source counts/coverage/hashes are in `GOLD_R4_FX2_EURJPY_HISTORY_2023_2025_RETRO_RESULTS_20261009.json`. No raw licensed FX quotes, secrets, or raw Neon rows were exported/persisted to repository. The provider data were actually obtained and used in memory for past-context study.
- Note all history was returned/retrieved in **2026**, not native historical time-of-release receipts; H1 bar availability at last close+45minutes is a modeled conservative quote production policy, not independently proven PIT vendor publication timestamp.

### Frozen signals and controlled clock
Source `GOLD_R4_EURJPY_USD_COMMON_FACTOR_SIGN_AUDIT_PREREG_20261009.md` written BEFORE backtest results. FX H1 source is start-labelled, with local07-start closes08:00 for DAY09TR decision at08:45; local15-start closes16:00 for OVN17TR decision at16:45 (compare previous H1 06-start or14-start). Both bar-close inputs >=45min before practical issue clock, not leaking targets.
FX2 only chooses XAU-UP if EURUSD hour return UP and USDJPY hour return DOWN, or XAU-DOWN if opposite; otherwise abstains. Overlay replaces a frozen legacy price-model sign on agreement days, falls back to it when pair directions conflict, and reports all eligible dates on the same FX-complete population. Macro inverse-dollar interpretation a testable sign, **not a causal guarantee**.
Baselines are already frozen legacy (2026-10-07) source research model `LIT_DAY0_EXEC_0900` and `LIT_OVN0_1530_1600`; 2023–25 price target labels are **NOT** the new canonical single-source 2026-10-09 EV-DUKA target and some target cohorts include noncalendar overnight gaps. A separate concrete canonical label audit established 5 **opposing signs among 589 matched canonical normal weekday night dates** (0.849%), plus 27 excluded quarantined legacy dates. This pilot is **NON-CANONICAL**, not a promoted same-source forecast. Date-by-date canonical refitting or joining would be required for final test.

### ACTUAL yearly full-coverage **paired BA**, not selected tiny-cohort performance
| Window / year | Same eligible FX-complete N | Price-only LIT baseline BA | FX2 overlay BA | Rescued/broken same-date directional decisions | Exact McNemar p |
|---|---:|---:|---:|---:|---:|
| DAY 2023 |252|51.36%|48.46%|35/42|.4944|
| DAY 2024 |259|47.75%|46.87%|35/44|.3682|
| DAY 2025 inspected |217|50.03%|48.27%|30/40|.2820|
| OVN 2023 |205|50.81%|45.00%|40/55|.1505|
| OVN 2024 |208|46.97%|48.20%|47/50|.8392|
| OVN 2025 inspected |202|50.55%|55.78%|41/37|.7343|
The apparently positive 2025 OVN is ONLY +5.23 BA pp and not statistically reliable on paired predictions; large failure in 2023. OVN pre-issue 2025 FX2 selective subset 142/204 dates (69.61% of original eligible LIT), FX-only BA59.49% versus same-date historical price expert BA50.57%. However **2023** FX-only selected BA44.64 vs baseline53.11, and 2024 BA50.56 vs baseline47.30 — so no 2023/24/25 transport. Avoid selective-accuracy advertising and target-vintage mixing. 2025 selective FX DOWN correct37, false DOWN35 (precision51.39%); 2025 full overlay DOWN recall46.07%, false DOWN39. All before actual Turkish bank spread, short-sale rights, execution-quote proof.

### Independent DeepSeek scientific challenge ACTUALLY run BEFORE FX scores
One bounded DeepSeek `deepseek-flash` provider review: `GOLD_DEEPSEEK_FX2_HOSTILE_PRERESULT_REVIEW_20261009_REVIEW.md`, 1,520 prompt +1,029 completion =2,549 tokens, final answer complete. Referee says **BLOCK promotion, GO exploration only**: yen is risk-off/rate-differential channel not an unambiguous USD leg, two FX pairs share broad USD macro shocks, original target vintage mismatch invalidates promotion, source H1 as-of publication cannot be retroactively certified, and wants a lagged-FX negative control. The requested **lag-shift placebo has NOT been executed** in this trial (because raw FX data were intentionally never stored, extra 12 API retrieval calls not justified after negative yearwise results); explicitly marked OPEN and do not call a passed negative control.

### Scientific conclusion / next meaningful route
No stable incremental prediction value from naive co-moving currency signs. **REJECT static FX double-agreement overlay for BOTH Turkish windows** and do not invert/optimize FX signs based on inspected 2025.
Actual progress is a VERIFIED new independent historical source with full-hour chronological span 2023–25 and distinct currency rates and publication clock. This removes the previous categorical “no FX source” obstacle for experiments, but no signed market skill. A principled next program would use *independent as-of FX and interest-rate shock surprises*, forecast-real-time native quote vintages, USDJPY risk-off confounding explicitly corrected, and canonical DAY/OVN target stored ONLY privately with proper source agreements. Pre-register a low-dimensional exchange-rate macro factor (e.g. common signed FX innovation orthogonal to XAU preorigin return, not a second USD sign overlay) BEFORE inspecting outcome, and implement independent prospective validation plus bank BID/ASK execution quotes; otherwise STOP the family rather than many retrospective parameter sweeps.
**No validated high-accuracy model, no executable bank returns, no promotions.** Main manifest authority unchanged unless separately updated.
