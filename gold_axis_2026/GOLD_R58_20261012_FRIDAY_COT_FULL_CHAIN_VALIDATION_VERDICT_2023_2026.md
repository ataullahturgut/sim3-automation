# R58 — H3 Friday-release COT source-clock: 2023–2026 dynamic HELIOS, SAGE/RuleFlow and conditional DPTC-Q95 outcome

**2026-10-12 · Nonbinding experimental research — not a new operational model.**
**Verdict: NO VALIDATED BENEFIT FROM PROMOTING FRIDAY-COT TO FROZEN DPTC-Q95.**
Keep D0 source-day average → third retained-source-day D3 H3 target unchanged.
Do NOT change frozen Q95, target/source clocks, alarm/SELLR authority, or old manifest history.

## 1. Complete dynamic pipeline portion executed; what is strictly verified
Inputs: original 1029-row H3 OPAL feature panel, historic COT source features and special delayed reports, original 931-row CLEAN HELIOS V5 ledger, fixed upstream AURORA/RIFT/TURN/VEGA inputs. New COT as-of timestamp: Tuesday COT positioning released **Friday 15:30 New York (May 22:30 TRT)**; at assumed issue day **15:00 TRT**, report published later same Friday cannot enter. Special CFTC publication delays preserved from `GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv`. Respect unchanged underlying H3 D0/D1/D3 target.

- Refit **OPAL** across historical monthly matured rolling training windows with original 18 features, StandardScaler, balanced L2 logistic C=1 and reversal threshold 0.70. Independent JavaScript IRLS implementation reproduces original CLEAN OPAL May probabilities to max absolute 0.003095, not exact scikit-learn probability parity. It reproduces old/new reversal decisions with an approximately numerical model; calibration and threshold cases remain model-implementation sensitive. Original sklearn compatible script is saved separately at `tools/gold_h3_opal_friday_cot_asof_v2.py`, **not executed** in this connected runtime.
- Replayed **HELIOS V1 candidate maturation/gate (8-matured / enter5 / exit3), V2 posterior, V3 game-theory five policies, V4 REGRET-EXPANSION persistence, V5 DCE exception** over all 931 dated inputs, including delayed maturity queues and endogenous vintage-first signal count. **Independent baseline replay old COT reproduces stored CLEAN HELIOS V5 probability and GT score exactly at 931/931 rows (tol 1e-10)**. This strong parity check is the reason the new HELIOS conditional result is considered a valid re-simulation under fixed old non-COT upstream streams, despite OPAL solver error margin.
- Saved 931-row old/new per-issue full HELIOS diagnostic: `GOLD_R56_20261012_H3_FRIDAY_COT_DYNAMIC_HELIOS_V1_V5_931ROW_REPLAY.csv`.
- Applied **SAGE IFBC>=4 and score>=0.70; LLRS opposes/positive increment/pressure>=0.10 and updated V5 follows momentum**, plus **RuleFlow hotspot/gate/60day topology veto** on preserved external source states in 2026. The old combined baseline **126/191** is independently reproduced from recombined old HELIOS ledger. New candidate baseline is **124/191**. Note that IFBC, LLRS, TRES, macro/two-year Treasury and training states originated in later freezes: this is a **controlled overlay recombination**, not re-fitted upstream inputs.
- Applied DPTC **Q95 phase label-free indicator and SELLR scorer frozen**, and re-evaluated trigger eligibility, delayed target maturation, and two-broken streak trust exit on the **ORIGINAL 28-row 2026 Handoff alarm candidate cohort**, not on rederived candidates. Old DPTC actions **13**, old original Q95 success **135/191**, old May **17/21** reproduced exactly. New controlled cohort actions **11**, new conditional success **127/191**, May **15/21**. But **the old alarm list depends on the old combined baseline**; there may be new previously unrecorded alarms under new Friday COT, and the old SELLR numeric score could change after a proper refit. This is **not a complete newly trained Q95 model and 127/191 is NOT a certified new Q95 score**.
- Additional controlled check: keep all **13 original Q95 actions fixed**, only recompute updated HELIOS+SAGE/RF baseline: **129/191** new fixed-action result vs original **135/191**. On May same fixed-action **15/21** vs old **17/21**. Thus in two controlled scenarios (fixed actions vs old alarm cohort with adjusted maturation), no 2026 final-Q95 gain is observed.

## 2. HELIOS V5 dynamics — full 931-row original parity
| Period | N | Old HELIOS correct | Friday-COT dynamic HELIOS correct | Direction change N |
|---|---:|---:|---:|---:|
| 2023 | 219 | **156 (71.23%)** | **156 (71.23%)** | 0 |
| 2024 | 240 | **171 (71.25%)** | **171 (71.25%)** | 0 |
| 2025 | 248 | **165 (66.53%)** | **161 (64.92%)** | 6 |
| 2026 Jan–Sep | 191 | **121 (63.35%)** | **119 (62.30%)** | 16 |
| 2026 May subset | 21 | **12 (57.14%)** | **14 (66.67%)** | 2 |

2026 May HELIOS changed **May19 and May22**, both correct relative to frozen H3 targets (new DOWN). Original DPTC-Q95 **already** flipped the old May19/22 baseline UP→DOWN. When the new HELIOS baseline also changes to DOWN, unchanged DPTC switches it *back* to UP (double reversal), breaking both old correct Q95 calls. Never add the +2 HELIOS improvement atop DPTC +9 gain as if independent.

2023/24 HELIOS V5 original and Friday are same despite COT release refit because no extra accepted downstream routes alter final direction. 2025 degradation and 2026 Jan–Sep degradation refute assuming a May-only OPAL increase generalizes.

## 3. Explicit Q95 2026 controlled dependency graph — NOT a full re-fitted Q95
| 2026 endpoint (191 issues) | Correct | May correct (21 issues) | Scientific status |
|---|---:|---:|---|
| Old SAGE+RuleFlow combined baseline from old V5 | **126/191** | 13/21 | Frozen baseline parity |
| Old frozen Q95 final | **135/191** | **17/21** | Independently reproduced |
| New Friday-COT HELIOS + fixed external IFBC/LLRS/RuleFlow recombination | **124/191** | **15/21** | Controlled recombination |
| New baseline + frozen original 13 Q95 action dates | **129/191** | **15/21** | Fixed-action counterfactual |
| New baseline + Q95 trust recalculated in original alarm cohort | **127/191** | **15/21** | **Original-alarm-cohort sensitivity**, not authentic final successor |
All combined-baseline label comparisons use original finalized retrospectively corrected H3 full UTC-day spot means. Per-row data: `GOLD_R57_20261012_FRIDAY_COT_V5_FROZEN_SAGE_RF_ALARM_COHORT_Q95_191_SENSITIVITY.csv`. The new Q95 trust differs from frozen on Sept10 and Sept14 but **new alarm candidates cannot be inferred exhaustively** with existing old-cohort timeline.

Frozen phase and SELLR inputs are **not** legitimately fixed in a complete successor fit, because the SELLR score depends on original model features and training outcomes. This narrows what may be claimed from R57. No provisional action/state result is reported as independent out-of-sample 2026.

## 4. OPAL all-period robustness after Friday retraining (earlier R55)
| Window | Original CLEAN OPAL | Friday OPAL |
|---|---:|---:|
| 2025 | 161/248 | 160/248 |
| 2026 Jan–Apr | 60/85 | 57/85 |
| 2026 May | 12/21 | 16/21 |
| 2026 June–Sept | 49/85 | 48/85 |
| Combined 2025 + Jan–Sept 2026 | **282/439** | **281/439** |
May +4 OPAL is localized and not enough to authorize a system-wide change. Underlying target/source PIT limitations remain from R45–R48.

## 5. Binding decision for user
1. **Do not promote Friday COT to Q95 production** based on May 2026. On the most trustworthy fully replayable downstream stage (HELIOS), aggregate 2025 and 2026 performance deteriorates.
2. Preserve old DPTC-Q95 135/191, May17/21 as **historical posthoc** benchmarks, not live-certified forward accuracy. New 127/191 is conditional and does not supersede the original historical tally.
3. Release-clock correctness is separate from model feature freshness policy: the original +7-day conservative COT delay is NOT a calendar conversion bug; any Friday-first successor must be independently versioned, retrained, validated on 2023–2025 and evaluated on dates unseen after Oct2026.
4. Further authentic full DPTC test requires regenerated daily full-window 2025/2026 alarm eligibility (including newly created alarm days), recalculated SELLR scores from altered baseline, and BOCPD formation/transition, not only the original 28 alarms. It also requires provider PIT firstprints as described in R45–R48. Until then, model improvement is **NOT PROVEN**.

## Audit artifacts
- `GOLD_R56_20261012_H3_FRIDAY_COT_DYNAMIC_HELIOS_V1_V5_931ROW_REPLAY.csv` — 931 rows original and changed HELIOS dynamic chronological decisions with source dates and original parity gate.
- `GOLD_R57_20261012_FRIDAY_COT_V5_FROZEN_SAGE_RF_ALARM_COHORT_Q95_191_SENSITIVITY.csv` — 191 2026 original vs conditional SAGE/RF and alarm-cohort-Q95 decisions; not trained as a full successor.
- R50–R55 previous OPAL research artifacts. Avoid relying on invalidated R51.
