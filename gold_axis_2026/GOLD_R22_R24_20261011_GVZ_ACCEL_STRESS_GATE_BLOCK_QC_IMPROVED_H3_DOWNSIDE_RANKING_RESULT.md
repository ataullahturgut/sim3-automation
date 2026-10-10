# R22 / R23 / R24 | Actual prior NY GVZ innovation and regime-conditioned H3 downside risk experiment + BLOCK dependence QC
**2026-10-11 TRT. Real independent Neon DB SELECTs, exact source provenance, no guessed backtest; not independent virgin validation, not investable buy/sell signal.**
R22, R23 and R24 separate preregs committed **BEFORE their corresponding result queries**, full names:
- `GOLD_R22_CAUSAL_IMPLIED_VOL_ACCELERATION_GVZ_VS_REALIZED_PREISSUE_H3_DOWNSIDE_PREREG_20261011.md`
- `GOLD_R23_IMPLIED_VOL_HIGH_REGIME_GVZ_SEMIVAR_GATING_ASOF_PREREG_20261011.md`
- `GOLD_R24_STRICT_BLOCK_BOOTSTRAP_R23_PREISSUE_RISK_RANKING_POST_SELECTION_QC_PRE_REG_20261011.md`.
Important previous science: R14 actual deepseek-v4-pro 2round got no high-quality signed metal GPR innovation; R15-R19 found statistically weak but consistently better 3day downside probability; R20 asymmetric return tests improved 2025/26 downside-tail risk rank but harmed 2023. R21 tried historic 20day lagged momentum signed H3 and FAILED, separate result file.
Source real PRIVATE Neon SELECT: historical `gold_research_evduka_xau15m_bidask_candidate` <=2025; 2026 `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2`, `m1_matched=15`; at 08:45TR the last of16 completed 04:45–08:30 M15 BID bar start time; entry 09TR BID/ASK quotes, outcome exact **third subsequent Mon–Fri weekday** 09TR BID and ASK agree on direction and both endpoints exist. Prior NY GVZ daily dated BEFORE issue (never same-day), stale<=7 caldays and 20 previous GVZ observations with adjacent gaps<=7; preceding 6 reference XAU 09 quotes yield five already-completed 09→09 logreturns, no future outcome in input. No 2026 Aug/Sep Stak fourmetal fabrication; no HMM smoothed regime leak.
Source cohort common R22/23/24 `1625` origins from 2020-02-03 to2026-10-02. 2023 test254 (21 severe DOWN), 2024 test256 (35 DOWN),2025 test255 (29 DOWN),2026 test116 (36 DOWN), original 2020–22 training742/2020–23 training996/2020–24 training1252; labels matured **strictly before annual cutoff**; 2025+2026 same frozen2024 model parameters and same prior-GVZ stress percentile threshold. Target `D=1` if realized exact H3 XAU BID logreturn `<=-0.015`, only on BIDASK sign agreeing samples. Gold 4h RV log; last-dated GVZ log; latest GVZ change last5/20 prior publication days; last5 already completed XAU 09 daily trend / max negative daily return and squared-negative fraction. All logistic coefficients standardized train only, L2 penalty30, intercept free, 16 Newton iterations; no hidden 2025/26 fitting. Not live-executable, no bank spreads or order fills.

## R22 actual experiments: raw GVZ acceleration did NOT beat stable two-feature prior
| Risk forecast, Brier LOW better |2023 N254|2024 N256|2025 N255|2026 N116|
|---|---:|---:|---:|---:|
| R18 common cohort RV+GVZ BASE| .077658 | **.115435** | .096303 | .214464 |
| GVZ_ACCEL =RV+GVZ+GVZ5+GVZ20|.078563|.115987|.095048|.218407|
| TREND_ACCEL =RV+GVZ+prior5 trend/min return+GVZ5|.080463|.116235|.094300|.215484|
| **SEMI_ACCEL**=TREND_ACCEL+past5 negative semivar fraction|.080238|.116193|.094906|.213870|
| FULL_ACCEL additionally GVZ20 and realized past5 variance|.082333|.116136|.094294|.215897|
Using SEMI_ACCEL as raw regression, 2026 high predicted DOWNtail quintile **11/23** vs low **4/23** (previous BASE 7/23 vs6/23),2025 16/51 vs0/51; but 2023 reverses1/50 vs3/50, and Brier2023/24 worsens relative BASE. Novel GVZ acceleration is NOT a universal incremental source.

## R23 actual risk proxy: no full 13D HMM
**New exact predeclared regime gate:** historical training P75 of lag prior-day NY GVZ quote levels. If previous GVZ>=TRAIN P75, assign .75×SEMI_ACCEL+.25×GVZ-only probability; if below, .25×SEMI_ACCEL+.75×GVZ-only. GATE is known as-of issue before gold open and is NOT original monthly HMM. Percentile threshold computed TRAIN only 2023=20.39,2024=19.61,2025/26 SAME=19.08 GVZ value. Number of HIGH-stress issue rows 2023 3/254,2024 7/256,2025 118/255,2026 **116/116**. This is an observed model SOURCE state distribution, not evidence of exact market R0/R1/R2 categories.

|Brier (lower better)|2023|2024|2025 OPENED|2026 OPENED|
|---|---:|---:|---:|---:|
| Same source simple RV+GVZ|**.077658**|**.115435**|.096303|.214464|
| GVZ-only | **.077122** | .116770 |.095526|.216782|
| SEMI_ACCEL| .080238|.116193|.094906|.213870|
| fixed 50:50 GVZ+SEMI ensemble |.078455|.116328|**.094449**|.212736|
| HARD TRAIN-P75 switch |.077735|.117168|.095494|.213870|
| **SOFT fixed P75 conditional blend** |.078039|.116710|.094780|**.212655**|
R23 SOFT does NOT beat R18 best BASE in 2023/2024; incremental Brier gain limited and only 2025/2026. All variants beat year STATIC HISTORIC frequencies on some years but 2023 signal small. The annual source 2025/26 had been repeatedly opened long before R22/R23, so these numbers are **post-selection, exploratory**.

### Measurable benefit we were seeking: H3 major DOWN warning days in 2025/26
Preissue ranking by SOFT conditional forecast and actual 3day DOWN>=1.5% event (no retrospective threshold selection other than fixed top/bottom20% for evaluation):
| year | tested | upper quintile actual | lower quintile actual | high-minus-low tail-rate |
|---|---:|---:|---:|---:|
|2023|254|3/50 = 6.0%|3/50 =6.0%|0 pp|
|2024|256|13/51=25.5%|3/51=5.9%|19.6 pp|
|2025|255|15/51=29.4%|1/51=2.0%|27.5 pp|
|2026|116|**11/23=47.8%**|**3/23=13.0%**|**34.8 pp**|
The older R18 2026 scored original baseline7/23 vs6/23, almost no separation. The R23 risk GATE shows increased 2026 **retrospective ability to distinguish high from low expected 3day extreme downside**, but note that 2026 has *true event rate36/116=31%* and 2026 high-stress gate fires on every origin, meaning the distinction is FROM regression semivariance/trend information within the high regime, not the gate itself. This is not predicting UP/DOWN: a 1.5% downside event model need not predict sign on days that decline less than1.5%; it cannot just say 'sell gold' whenever risk high.

## R24 real 8-origin moving block bootstrap and residue QC (POST-SELECTION, not independent proof)
Fixed previously examined R23 SOFT predictions vs source-matched R18 RV+GVZ Brier scores, B1000 moving blocks of 8 consecutive source trading origins sampled with replacement, deterministic PRNG seed3110, no retraining/reselection. Risk spread computed on each bootstrap's highest and lowest20% predicted probability cohorts. Nonoverlap control four origin subpanels index modulo4, few per phase.
|year| high-low risk spread | 95% block bootstrap spread interval | mean matched Brier GAIN vs RV+GVZ | 95% block bootstrap paired gain interval|
|---|---:|---:|---:|---:|
|2023|0.0 pp|[−12.0,+10.0] pp|−.000381|[−.002076,+.001116]|
|2024|+19.6 pp|[0,+37.3] pp|−.001275|[−.002678,+.000103]|
|2025|+27.5 pp|[+9.8,+45.1] pp|+.001523|[−.001222,+.004619]|
|2026|**+34.8 pp**|[+4.35,+52.2] pp|+.001809|[−.006014,+.009171]|
**Interpretation**: stress regime R23 downside risk ranking spread is positive in the 2025/26 opened cohort and in respective internal dependent block resamples, but paired Brier gain relative stronger RV+GVZ includes0 on both 2025/26. R24 post-selected intervals **MUST NOT** be called valid 95% confirmatory confidence, especially 2026 small sample and multiple prior R15–R23 research hypotheses. For 2026 four stride4 nonoverlap phase spreads +60/+60/0/+20 pp, direction never negative, but each phase has29 dates and top/bottom quintile about5 dates -> very noisy. 2025 phase spreads +58/+25/+8/+25pp, also positive all; 2023 phases mixed. These are diagnostics not trade signal reliability.
### Result / go-no-go
- **YES, a source-causal, clock-correct risk-stratification hypothesis now has documented positive descriptive effect in EACH 2024,2025,2026 and retains it under 8-origin block dependence diagnostic.** Mark `RESEARCH_GAIN_RISK_RANKING`, NOT `PROVEN_TRADE_ALPHA`.
- **NO, no robust 2023 four-year risk-ranking generalization; no Brier win against best simple model on all years, nor original high-accuracy UP/DOWN signed prediction; no retrained exact original monthly ChHHO 8values / 13D historical PIT state assigned midmonth.** New model is not promoted.
- True scientific next milestone is a source-asof issuance-frozen unseen later period 2027 (or 2026 after a genuine time-frozen prospective start with no further tuning) with complete source, bank charges, and independent signed UP/DOWN head. Preserve previous historical negative results and model pool authority.
