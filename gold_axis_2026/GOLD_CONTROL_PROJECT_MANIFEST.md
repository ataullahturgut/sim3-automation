# GOLD CONTROL — PROJECT MANIFEST

**Manifest version:** 1.74  
**Issue date:** 2026-09-18  
**Repository:** `ataullahturgut/sim3-automation`  
**Canonical branch:** `gold-r4-direction-engine`  
**Current research branch:** `gold-direction-vlmc-bs-family-v2-20260918`  
**Project root:** `gold_axis_2026/`

---

## 1. Sole authority

This file is the **only current Gold Control project manifest**.

`gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md` is the sole project-level authority for Gold Control architecture, model roles, data chronology, validation governance, research sequencing, frozen challenge definitions and promotion rules.

Contracts, preregistrations, design notes, checkpoints, reports, event inventories, run artifacts, historical handovers and audit outputs are subordinate to this manifest. If a subordinate artifact conflicts with this manifest, the current manifest wins once the corresponding manifest change is accepted on the governed branch.

Authority split:

- **GitHub:** current code, frozen model/feature/source contracts, reproducibility and this manifest.
- **Production Neon:** mutable source observations, point-in-time lineage, append-only runtime/context state and legitimately issued forecast/decision records.

Historical implementation detail may remain in Git history or immutable audit storage, but historical model scores do not define current project authority.

Gold Control is a **decision-support and research system, not an autonomous trading system**.

---

## 2. Current top-level architecture

Gold Control has **two parallel primary lines**. They may exchange role-preserving context but they are not one homogeneous model-selection pool.

### 2.1 Monthly H=1 price-level forecasting — ACTIVE AND INDEPENDENT

The monthly programme forecasts the next calendar month's XAU/USD price level from the previous completed month-end information boundary.

Current monthly H=1 expert identities:

- `CAUSAL_PATCH`
- `VW_MIDAS_MSVR_SUCCESSOR_V1`
- `MOMENTUM_3M`
- `RANDOM_WALK`

`MONTHLY_DIRECTION_3M` remains a strategic monthly direction/prior context.

The monthly H=1 line remains a standalone forecast output regardless of GC-BREAK research progress.

### 2.2 Short-term GC-BREAK — SEQUENTIAL TREND-HEALTH / BREAK EARLY WARNING

The current short-term problem is **not fixed-horizon 1D/3D direction prediction**.

Binding state ontology:

`STABLE -> WEAKENING -> BREAK_ALERT -> CONFIRMED_BREAK -> NEW_REGIME`

Recovery transitions are permitted, including `WEAKENING -> STABLE`, `BREAK_ALERT -> STABLE` or a lower warning state, and later stabilization of a new regime.

Primary short-term questions are warning lead time, false-warning burden, missed breaks, confirmation delay, regime stabilization and recovery behavior.

`NEXT_NY17_1D`, `NEXT_NY17_3D`, standalone 1D/3D directional accuracy and fixed-horizon break-risk are historical research targets only and may not silently re-enter the architecture.

---

## 3. Governed runtime registry versus current research activity

The governed runtime registry contains exactly **11 identities**. Runtime registration does **not** mean every identity is currently active in the GC-BREAK research sequence.

### 3.1 Governed runtime registry

1. `CAUSAL_PATCH`
2. `VW_MIDAS_MSVR_SUCCESSOR_V1`
3. `MOMENTUM_3M`
4. `RANDOM_WALK`
5. `MONTHLY_DIRECTION_3M`
6. `FAST`
7. `SLOW`
8. `MACRO_EVENT_SUCCESSOR_V2`
9. `EMERGENCY_LEVEL`
10. `EMERGENCY_REVERSAL`
11. `GVZ_RISK`

No additional research channel becomes a governed runtime identity without explicit promotion and manifest change control.

### 3.2 Current GC-BREAK research activity status

The current research-status layer is binding for work sequencing and must not be confused with the runtime registry above.

| Identity / lane | Current research status | Binding interpretation |
|---|---|---|
| `FAST` | `EVALUATED / RETAINED_TACTICAL_CONTEXT` | 2025 full-timeline replay complete; not proven standalone volatility-warning engine |
| `GVZ_RISK` | `EVALUATED / RETAINED_RISK_CONTEXT` | 2025 full-timeline historical replay complete; risk/severity only, no direction vote |
| `BOCPD` research lane | `EVALUATED / RETAINED_RESEARCH_REFERENCE` | only V5 + R2 remain authoritative; BOCPD is retained as regime/change context, not as the next standalone future-change-time predictor |
| RSM / ERSM family | `TERMINATED / FAILED_METHOD_FAMILY / DO_NOT_REVISIT` | closed by explicit user decision on 2026-09-18; historical artifacts are audit-only and the family must not re-enter research sequencing unless the user explicitly reverses the closure. |
| `DIRECTION_VLMC_BS_V1_RESEARCH` | `AUDIT_ONLY / SUPERSEDED_FOR_FAMILY_SCOPE` | original custom-Python rolling-52 experiment is retained only for lineage; corrected V2 uses source weekly-return construction and pinned R VLMC reference semantics. |
| `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH` | `EVALUATED / NO_PROMOTION / SOURCE_FAITHFUL_REFERENCE_REPLICATION_COMPLETE / 2025_GENERALIZATION_WEAK` | rolling 26/52/104 reference-family replay complete; k=52 validated strongly in 2024 but failed to generalize in 2025, while k=104 was more balanced in 2025 but had weaker pre-2025 evidence. |
| `DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH` | `REJECTED / NO_PROMOTION / 2025_GENERALIZATION_FAILED` | literature-grounded adaptive expert weighting of VLMC-26/52 improved 2023-2024 but collapsed in locked 2025; do not rescue by retuning this same grid against 2025. |
| `DIRECTION_BCT_CTW_V1_RESEARCH` | `EVALUATED / NO_PROMOTION / WEAK_DIRECTIONAL_DISCRIMINATION` | exact BCT/CTW-52 replay complete through 2025; probability quality improved materially versus VLMC-BS but 2025 produced 52/52 UP forecasts, balanced accuracy 50%, and 0/5 DOWN volatility-event agreement |
| `DIRECTION_BCARS_V1_RESEARCH` | `BLOCKED_PRE2025_BOUNDARY_SUPPORT / NOT_SCORED / NOT_RUNTIME` | source-form ordinary-Beta B-CARS(1,1) is blocked by genuine pre-2025 weekly up-ratios equal to 0; no silent clipping permitted |
| `DIRECTION_BCARS_SV_V1_RESEARCH` | `EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / WEAK_DIRECTIONAL_DISCRIMINATION` | separately preregistered Smithson-Verkuilen boundary-safe B-CARS(1,1) successor; 2024 validation failed and 2025 produced 51 UP / 1 DOWN with 0% DOWN sensitivity |
| Post-BOCPD future-change-time lane | `NEXT_RESEARCH_LANE / PREREGISTRATION_REQUIRED` | separately named residual-time / explicit-duration / Bayesian online changepoint-prediction challenger; exact identity and parameters must be frozen before implementation |
| `MACRO_EVENT_SUCCESSOR_V2` | `SUSPENDED_FOR_CURRENT_GC_BREAK_RESEARCH_SEQUENCE` | governed runtime identity remains registered, but it is **not the next motor** and no new Macro Event tuning/evaluation is authorized in the current sequence |
| `MACRO_EVENT_SUCCESSOR_V4_RELIABILITY_GATE` | `FROZEN_RESEARCH_CHALLENGER / NOT_RUNTIME_AUTHORITY` | historical preregistration remains audit lineage; not promoted and not the current workstream |
| `EMERGENCY_LEVEL` | `SUSPENDED / REDESIGN_REQUIRED` | do not treat as next motor until separately redesigned/preregistered |
| `EMERGENCY_REVERSAL` | `SUSPENDED` | do not treat as next motor until separately re-authorized |
| `SLOW` | `LOW_PRIORITY / NOT_NEXT` | valid confirmation/new-regime context but not the immediate research priority |
| Monthly H=1 line | `ACTIVE_INDEPENDENT` | continues separately from GC-BREAK motor sequencing |

**Important:** suspension here is a research-sequencing status. It does not erase historical runtime identities, old contracts or Git history, and it does not promote a replacement automatically.

The binding post-BOCPD scientific direction is **not another ordinary BOCPD threshold/hazard retune** and is not Macro Event, GVZ, Emergency or SLOW. The next research lane is a separately named **future change-time prediction** motor in the residual-time / explicit-duration / Bayesian online prediction of changepoints family. Its exact implementation is not pre-approved; it requires preregistration using pre-2025 chronology before any new outcome inspection.

---

## 4. BOCPD research authority — exactly two retained identities

The active BOCPD research authority contains exactly **two** identities:

1. `BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH` — **primary BOCPD research model**.
2. `BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH` — **frozen comparison baseline only**.

No other BOCPD identity is active authority. Raw hourly Candidate B, earlier optimized B2 identities, daily Candidate A, monthly `BOCPD_RETURN_SUCCESSOR_V1`, duration/residual V2, robust-clipped V3, duration+robust V4 and other superseded BOCPD experiments are historical only. Their active model-code/result/workflow surfaces are removed from the current research branch; Git history may retain them solely for audit traceability.

The **only authoritative BOCPD model surfaces** on the active research branch are:

- code: `gold_axis_2026/tools/bocpd_hourly_b2_adaptive_hazard_pre2025.py`;
- code: `gold_axis_2026/tools/bocpd_hourly_b2_baseline_r2_pre2025.py`;
- result: `gold_axis_2026/GOLD_CONTROL_BOCPD_B2_ADAPTIVE_HAZARD_V5_PRE2025_RESULT_2026-09-16.md`;
- result: `gold_axis_2026/GOLD_CONTROL_BOCPD_B2_BASELINE_R2_PRE2025_RESULT_2026-09-17.md`;
- reproducibility workflow: `.github/workflows/gold-bocpd-b2-adaptive-hazard-pre2025-20260916.yml`;
- reproducibility workflow: `.github/workflows/gold-bocpd-b2-baseline-r2-pre2025.yml`.

Any other BOCPD-named model code, model result or model workflow present on the active research branch is non-authoritative and must be removed or separately re-authorized by manifest change control.

The retained hourly input series is `XAU_USD_TWELVE_1H_RESEARCH_V1`. It is **research-only** and does not replace canonical `XAU_EOD_TWELVE_NY17` runtime semantics.

Neither retained BOCPD identity is a governed runtime or production engine. V5 is the active research reference; R2 is its benchmark. Neither emits an equal-weight direction vote.

### 4.1 BOCPD chronology

Binding chronology for both retained BOCPD identities:

- **2022:** research formation, hour-of-day normalization and prior formation;
- **2023:** development and parameter selection;
- **2024:** pre-2025 chronological retrospective comparison, not a pristine untouched holdout because BOCPD programme-level 2024 evidence had already been seen;
- **2025:** prohibited for tuning/model selection in the retained line and not queried/accessed by the V5/R2 pre-2025 model scripts.

The 2022 hourly history is accepted as **sufficient high-coverage research formation data for this phase**. This manifest does not claim that every theoretically expected 2022 market-hour slot has been independently completeness-certified.

### 4.2 BOCPD pre-2025 auxiliary comparison

`BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH` on the 2024 auxiliary abnormal-volatility comparison:

- 57 episodes;
- 12 matched episodes;
- 45 unmatched episodes;
- 11 / 17 events captured;
- precision `0.210526`;
- recall `0.647059`;
- F0.5 `0.243363`.

`BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH` on the same 2024 comparison:

- 65 episodes;
- 15 matched episodes;
- 50 unmatched episodes;
- 14 / 17 events captured;
- precision `0.230769`;
- recall `0.823529`;
- F0.5 `0.269576`.

These are **auxiliary abnormal-daily-volatility metrics**, not structural GC-BREAK precision/recall. V5 improves event coverage, precision, recall and F0.5 relative to R2 under the same comparison, but false-warning burden remains material. No runtime/production promotion is authorized.

Any future BOCPD successor requires a separately named preregistration/change-control step. The next future-change-time lane is a **separate model identity**, not a silent V6 retune of V5.


### 4.3 Planned direction-forecast research motors — four authorized identities

The following four identities are authorized as new research motors to be tried later. They are not implemented, not runtime identities, not production authorities, and may not silently replace the GC-BREAK state ontology. Their first implementation must preserve the mathematical method identity documented below and must use time-ordered, point-in-time-safe evaluation.

The previously discussed higher-moment direction-probability method is NOT SELECTED for this planned motor set.

#### 4.3.1 RSM / ERSM family — CLOSED

The RSM/ERSM family was fully evaluated for the source-feasible variants and is now permanently closed for the current project by explicit user decision dated 2026-09-18.

Binding status:

`TERMINATED / FAILED_METHOD_FAMILY / DO_NOT_REVISIT / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

Do not reopen, extend, retune, augment, ensemble, or propose successors from this family unless the user explicitly reverses the closure. Detailed historical evidence remains in repository audit files, especially `GOLD_CONTROL_DIRECTION_RSM_FAMILY_CLOSURE_2026-09-18.md`, and is intentionally not repeated in this manifest.

#### 4.3.2 VLMC-BS family — corrected reference replication

The original `DIRECTION_VLMC_BS_V1_RESEARCH` is retained only as historical audit evidence and is superseded for family-level interpretation.

The authoritative corrected identity is:

`DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`.

V2 follows Liu, Papailias & Quinn (2021) and the Mächler-Bühlmann R reference implementation more closely:

- governed daily simple percentage returns are summed into Monday-start weekly returns before binary UP/DOWN conversion;
- rolling windows k=26, 52 and 104 are evaluated because these are the source-feasible windows with same-source pre-2025 history;
- direct reference implementation uses R 4.4.1 and pinned `VLMC` 1.4-4;
- `K0=0.30`;
- candidate cutoff grid `0.40..2.50` by 0.02;
- `B=1000` bootstrap replications;
- `n.start=10000`;
- bootstrap one-step classification uses `VLMC::predict(type="class")`;
- each window-specific cutoff is calibrated once pre-OOS and frozen for the rolling replay;
- final direction is UP iff `P(UP)>=0.5`;
- no smoothing, NO_SIGNAL band, provider splice, external/context input or post-2025 rescue is present.

Frozen cutoff calibration:
- k=26: K*=0.40, bootstrap loss 0.304;
- k=52: K*=0.54, bootstrap loss 0.287;
- k=104: K*=0.40, bootstrap loss 0.243.

Fair 2024 common support begins 2024-03-04, n=44:
- k=26: accuracy 0.5909, balanced accuracy 0.5833;
- k=52: accuracy 0.6364, balanced accuracy 0.6292;
- k=104: accuracy 0.5682, balanced accuracy 0.5583.

On its full 2024 support, k=52 reaches accuracy 0.6792 and balanced accuracy 0.6781, providing materially stronger pre-2025 validation than the superseded V1.

Locked 2025 replay:
- k=26: accuracy 0.5769, balanced accuracy 0.5045, DOWN sensitivity 0.3333;
- k=52: accuracy 0.5769, balanced accuracy 0.4450, DOWN sensitivity 0.1333;
- k=104: accuracy 0.6154, balanced accuracy 0.5514, DOWN sensitivity 0.4000;
- corrected always-UP raw-accuracy baseline = 0.7115.

Frozen 19-event overlay:
- k=26: raw 12/19, balanced 0.4286, DOWN 0/5;
- k=52: raw 12/19, balanced 0.4929, DOWN 1/5;
- k=104: raw 14/19, balanced 0.6929, DOWN 3/5.

The event overlay is diagnostic only. k=104's event-subset result does not override its weaker pre-2025 evidence or the absence of stable pre-2025-to-2025 generalization.

Binding status:

`DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH = EVALUATED / NO_PROMOTION / SOURCE_FAITHFUL_REFERENCE_REPLICATION_COMPLETE / 2025_GENERALIZATION_WEAK / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

Fixed-Share adaptive weighting was subsequently tested as `DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH`; it is `REJECTED / NO_PROMOTION / 2025_GENERALIZATION_FAILED`. Detailed evidence remains in `GOLD_CONTROL_DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESULT_2026-09-19.md`.

Authoritative V2 audit surfaces:
- `GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_PREREG_2026-09-18.md`;
- `tools/direction_vlmc_bs_family_v2_reference.R`;
- `GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_CALIBRATION_2026-09-18.csv`;
- `GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_PRE2025_RESULT_2026-09-18.md`;
- `GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_2025_RESULT_2026-09-18.md`;
- `GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_2025_VOLATILITY_RESULT_2026-09-18.md`.

#### 4.3.3 DIRECTION_BCT_CTW_V1_RESEARCH — Bayesian Context Tree / Context Tree Weighting

Primary literature basis: Kontoyiannis, Mertzanis, Panotopoulou, Papageorgiou & Skoularidou (2022), JRSS Series B, DOI 10.1111/rssb.12511.

Let T(D) be the set of proper context trees with maximal depth D over alphabet size m. The BCT model prior is

pi_D(T;beta) = alpha^(|T|-1) * beta^(|T|-L_D(T)),

where alpha = (1-beta)^(1/(m-1)), |T| is the number of leaves and L_D(T) is the number of leaves at depth D. For the planned binary direction motor, m=2.

At each leaf/context s, the transition vector has independent Jeffreys-Dirichlet prior

theta_s ~ Dirichlet(1/2,1/2).

With context counts a_s(j), the posterior becomes

theta_s | x,T ~ Dirichlet(a_s(0)+1/2, a_s(1)+1/2).

Unlike a single selected VLMC, BCT/CTW averages over tree-model and parameter uncertainty. The exact prior predictive likelihood is

P*_D(x) = sum_T pi_D(T;beta) * integral P(x|theta,T) pi(theta|T) dtheta.

CTW computes it recursively. At a leaf, P_w,s = P_e,s. At an internal node,

P_w,s = beta*P_e,s + (1-beta)*product_j P_w,sj.

The exact next-symbol posterior predictive distribution is

P*_D(x_(n+1)|x_1^n) = P*_D(x_1^(n+1)) / P*_D(x_1^n).

For binary UP/DOWN data, the native output is therefore the exact posterior predictive P(UP next | sign history), not merely a MAP-tree class. The source framework suggests beta near 1-2^(-m+1); for m=2 this is about 0.5.

**Current BCT/CTW V1 evaluation checkpoint (2026-09-18):** V1 froze `D=10`, `beta=0.5`, `Dirichlet(1/2,1/2)`, a rolling 52-week binary window, first 10 signs as the fixed initial context, and the exact CTW posterior predictive with UP iff `P(UP)>=0.5`. No depth grid, threshold tuning or randomization was used.

Pre-2025:
- 2023 accuracy 0.5581395, balanced accuracy 0.5877193;
- 2024 fixed validation accuracy 0.4905660, balanced accuracy 0.4829060;
- combined pre-2025 Brier 0.2628675 and log loss 0.7224324;
- pre-2025 P(UP) range 0.4250141..0.8670874 with no exact 0/1 probabilities.

The probability layer is materially better behaved than the superseded VLMC-BS V1 audit run, whose pre-2025 replay produced exact 0/1 probabilities at 70/96 origins. This confirms the intended Bayesian smoothing/model-averaging benefit but does not establish a direction edge.

Locked 2025 historical replay:
- accuracy 0.6923077;
- balanced accuracy 0.5000000;
- actual UP/DOWN 36/16;
- forecast UP/DOWN 52/0;
- UP sensitivity 1.0;
- DOWN sensitivity 0.0;
- Brier 0.2320852;
- log loss 0.6578098;
- P(UP) range 0.5195496..0.7344673.

Thus the 69.23% raw accuracy exactly equals the always-UP baseline and is non-discriminative. On the frozen 19-event volatility overlay, raw direction agreement is 14/19 but event-direction balanced accuracy is 0.50, DOWN-event agreement 0/5 and EXTREME-event agreement 2/5.

Binding status: `EVALUATED / NO_PROMOTION / WEAK_DIRECTIONAL_DISCRIMINATION`. No post-2025 threshold shift, alternate D, NO_SIGNAL band or context augmentation is authorized under V1.

**Authoritative BCT/CTW V1 research surfaces on the current branch:**
- preregistration: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_PREREG_2026-09-18.md`;
- implementation: `gold_axis_2026/tools/direction_bct_ctw_v1_research.py`;
- pre-2025 checkpoint: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_PRE2025_RESULT_2026-09-18.md`;
- frozen 2025 weekly forecast table: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv`;
- locked 2025 result: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_2025_RESULT_2026-09-18.md`;
- frozen 19-event overlay table: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_2025_VOLATILITY_OVERLAY_2026-09-18.csv`;
- volatility-overlay result: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_2025_VOLATILITY_RESULT_2026-09-18.md`.

#### 4.3.4 DIRECTION_BCARS_V1_RESEARCH — Beta Conditional Autoregressive Shape

Primary literature basis: Xie, Sun & Fan (2023), Financial Innovation, DOI 10.1186/s40854-023-00489-z.

Let p_t be log close and h_t the maximum log price over interval [t-1,t]. Define

u_t = h_t - p_(t-1),
d_t = h_t - p_t,
R_t = u_t + d_t,
ur_t = u_t / R_t.

Then

r_t = p_t - p_(t-1) = R_t * (2*ur_t - 1).

Since R_t > 0, r_t > 0 if and only if ur_t > 0.5. Thus direction forecasting is transformed into forecasting a continuous up-ratio in [0,1].

B-CARS assumes

ur_t ~ Beta(alpha_t,beta),

with conditional mean

k_t = E(ur_t | Omega_t) = alpha_t/(alpha_t+beta).

The source benchmark B-CARS(1,1) uses

k_t = omega + gamma*k_(t-1) + tau*ur_(t-1),

subject to omega>0, gamma>=0, tau>=0 and omega+gamma+tau<=1. The time-varying shape parameter is

alpha_t = k_t*beta/(1-k_t).

Parameters are estimated by maximum likelihood from the Beta conditional likelihood. The native direction rule follows from whether the forecasted up-ratio is above or below 0.5. A Gold adaptation may additionally report `1-F_Beta(0.5;alpha_t,beta)` only as a derived probability diagnostic, not as the source paper's native direction rule.

The source high adjustment is preserved as `H_t^a=max(H_t,C_(t-1))`.

**True-OHLC data audit (2026-09-18):** a research-only Twelve Data `XAU/USD` 1h OHLC artifact was retrieved with no production database write. It contains 23,965 validated hourly bars, 205 weekly close anchors and 204 weekly up-ratio rows. Weekly HIGH is the maximum provider `high` field between consecutive governed weekly close anchors; it is not the maximum hourly close. Weekly close-axis checks against `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1` passed at the investigated boundary dates. The weekly decomposition identity holds to machine precision (maximum absolute error approximately 6.94e-18).

The ordinary-Beta parent V1 is **blocked before 2025 scoring** because the true pre-2025 sample contains exact `ur=0` observations at target weeks 2022-08-15 and 2024-04-22. These are genuine gap/down interval geometries rather than extraction errors. Ordinary Beta density has open support `(0,1)`; the parent preregistration prohibited silent clipping. Therefore:

`DIRECTION_BCARS_V1_RESEARCH = BLOCKED_PRE2025_BOUNDARY_SUPPORT / NOT_SCORED / NOT_PROMOTED`.

No 2025 score exists for the unmodified parent identity.

#### 4.3.4a DIRECTION_BCARS_SV_V1_RESEARCH — boundary-safe preregistered successor

Because the support blocker was discovered using pre-2025 data only, a separately named successor was frozen before 2025 replay.

The successor preserves B-CARS(1,1), source/high semantics, expanding-window OOS, initial 52 modeled weekly up-ratios, deterministic five-start constrained L-BFGS-B fitting and the native 0.5 direction boundary, but applies the standard Smithson-Verkuilen transformation at each origin with n training observations:

`y_i^* = (y_i*(n-1)+0.5)/n`.

The transform maps [0,1] into (0,1) while leaving the 0.5 classification boundary invariant. Continuous forecast diagnostics are mapped back to raw up-ratio scale via

`k_raw=(n*k^*-0.5)/(n-1)`.

No epsilon/clipping parameter is tuned.

**Pre-2025 frozen evidence:**

2023 development/audit:
- n=43;
- accuracy 0.4418605;
- balanced accuracy 0.5000000;
- forecasts 0 UP / 43 DOWN;
- UP sensitivity 0.0000; DOWN sensitivity 1.0000;
- source-style up-ratio R2_oos = -0.0032779.

2024 fixed validation:
- n=53;
- accuracy 0.4716981;
- balanced accuracy 0.4729345;
- forecasts 23 UP / 30 DOWN;
- UP sensitivity 0.4074074; DOWN sensitivity 0.5384615;
- source-style up-ratio R2_oos = -0.0325649.

Combined 2023-2024:
- n=96;
- accuracy 0.4583333;
- balanced accuracy 0.4745098;
- forecasts 23 UP / 73 DOWN;
- source-style up-ratio R2_oos = -0.0208597.

This is a failed pre-2025 validation checkpoint; the model was nevertheless carried unchanged into 2025 to preserve the preregistered test sequence.

**Locked 2025 historical replay:**
- n=52;
- accuracy 0.6730769 versus always-UP 0.6923077;
- balanced accuracy 0.4861111;
- actual UP/DOWN 36/16;
- forecasts 51 UP / 1 DOWN;
- UP sensitivity 0.9722222;
- DOWN sensitivity 0.0000000;
- TP/TN/FP/FN = 35/0/16/1;
- the only DOWN forecast targeted 2025-03-03 and was wrong;
- up-ratio MSE 0.0807706 versus expanding historical-mean MSE 0.0819350;
- source-style up-ratio R2_oos = +0.0142111;
- derived Beta-tail Brier 0.2367432 and log loss 0.6669116.

Thus the small positive 2025 continuous up-ratio R2_oos does not translate into two-sided direction discrimination.

**Frozen 19-event volatility overlay:**
- raw event-direction agreement 14/19 = 73.68%;
- balanced event-direction accuracy 0.5000;
- UP event agreement 14/14;
- DOWN event agreement 0/5;
- EXTREME event agreement 2/5;
- MAJOR-only agreement 12/14.

The raw event hit rate is class-balance driven because B-CARS-SV forecasts UP on every event week.

Binding successor status:

`DIRECTION_BCARS_SV_V1_RESEARCH = EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / WEAK_DIRECTIONAL_DISCRIMINATION / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

**Authoritative B-CARS research surfaces on the current branch:**
- parent preregistration: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_V1_PREREG_2026-09-18.md`;
- true-OHLC data audit: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_V1_DATA_AUDIT_2026-09-18.md`;
- parent pre-2025 blocker: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_V1_PRE2025_BLOCKER_2026-09-18.md`;
- boundary-safe successor preregistration: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_SV_V1_PREREG_2026-09-18.md`;
- successor implementation: `gold_axis_2026/tools/direction_bcars_sv_v1_research.py`;
- successor pre-2025 checkpoint: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_SV_V1_PRE2025_RESULT_2026-09-18.md`;
- frozen 2025 forecast table: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_SV_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv`;
- locked 2025 result: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_SV_V1_2025_RESULT_2026-09-18.md`;
- frozen 19-event overlay: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_SV_V1_2025_VOLATILITY_OVERLAY_2026-09-18.csv`;
- volatility-overlay result: `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCARS_SV_V1_2025_VOLATILITY_RESULT_2026-09-18.md`.

No post-2025 threshold, model-order, boundary treatment, frequency, optimizer or feature rescue is authorized under either B-CARS identity.

### 4.4 Common governance for the four new direction motors

These four motors form a parallel research-only direction lane. They do not reactivate the historical fixed NEXT_NY17_1D/3D programme and do not alter the primary GC-BREAK sequential state output.

Before implementation, a common preregistration must freeze target horizon/frequency, exact XAU source and close/OHLC semantics, rolling versus expanding formation, permitted training window(s), probability-to-direction mapping, abstention rule if any, evaluation metrics, and tie/missing handling.

Initial evaluation must report at minimum success rate, balanced accuracy where applicable, Brier score, log-loss, calibration and coverage. A model may not be selected solely because it has the highest raw hit rate.

The first implementation stage must reproduce each method's native mathematical identity WITHOUT FAST, GVZ, BOCPD, Macro or Emergency inputs. Only after standalone evidence is frozen may existing Gold Control motors be added one at a time through role-preserving ablation. Flat equal voting remains forbidden.

Current status is identity-specific: the RSM/ERSM family is `TERMINATED / FAILED_METHOD_FAMILY / DO_NOT_REVISIT`; VLMC-BS V1 is audit-only and superseded, while `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH` is `EVALUATED / NO_PROMOTION / SOURCE_FAITHFUL_REFERENCE_REPLICATION_COMPLETE / 2025_GENERALIZATION_WEAK / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`; BCT/CTW V1 is `EVALUATED / NO_PROMOTION / WEAK_DIRECTIONAL_DISCRIMINATION / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`; source-form B-CARS V1 is `BLOCKED_PRE2025_BOUNDARY_SUPPORT / NOT_SCORED / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`; its separately preregistered boundary-safe `DIRECTION_BCARS_SV_V1_RESEARCH` successor is `EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / WEAK_DIRECTIONAL_DISCRIMINATION / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

---

## 5. Role-preserving multi-clock architecture

Heterogeneous engines must not be flat-voted or ranked as though they solve the same task.

### Strategic block

- Monthly H=1 experts: independent price-level forecast plus strategic anchor/context.
- `MONTHLY_DIRECTION_3M`: slow strategic prior; not a daily trigger.

### Trend-structure block

- **FAST:** tactical daily trend state, flip, age and persistence; candidate early weakening evidence.
- **SLOW:** completed-week trend confirmation, alignment/conflict and state age; confirmation/new-regime evidence, currently low priority.

Frozen FAST rule:

- SMA20;
- current and previous completed daily state relative to SMA20;
- both UP -> `ROBUST_UP`;
- both DOWN -> `ROBUST_DOWN`;
- otherwise `MIXED`;
- exactly two-day persistence.

Frozen SLOW rule:

- completed W-FRI weekly closes;
- incomplete current week excluded;
- SMA4;
- previous and current completed week on same side -> `ROBUST_UP` / `ROBUST_DOWN`;
- otherwise `NOT_YET_ROBUST`;
- exactly two completed-week persistence.

### Regime / stress / risk block

- `BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH`: primary hourly BOCPD research context; causal adaptive hazard from run length and lagged volatility; no equal direction vote.
- `BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH`: frozen constant-hazard benchmark only.
- `GVZ_RISK`: retained options-implied gold-market risk/severity context only; never an equal direction vote and never silently converted into UP/DOWN.
- post-BOCPD future-change-time challenger: next research lane; must model prospective time-to-change / residual-time or equivalent explicit-duration hazard without reusing 2025 for tuning.
- `EMERGENCY_LEVEL`: **suspended / redesign required**.
- `EMERGENCY_REVERSAL`: **suspended**.
- realized volatility: retrospective uncertainty/severity/event context; never a predictor of the same realized event.
- chronology-safe optional VIX: risk context only.

### Event / shock block

- `MACRO_EVENT_SUCCESSOR_V2`: governed release-aware event-surprise identity, but **suspended for the current GC-BREAK research sequence**.
- `MARKET_SHOCK_V3`: research-only realized intraday shock intensity/concordance around eligible events.

Historical Macro Event contracts remain audit lineage. Their existence does not make Macro Event the next work item.

### Reliability / meta block

Permitted evidence includes matured reliability, support count, evidence age, explicit missingness, missing reason, class-degeneracy flags and justified regime/event-conditional reliability.

`NO_SIGNAL` / abstention is valid when support is insufficient.

---

## 6. Native clocks, availability time and evidence age

The architecture is multi-clock by design:

- **GC-BREAK main origin:** daily completed reference origin;
- **FAST:** tactical completed-daily clock;
- **SLOW:** completed weekly clock;
- **BOCPD research (V5/R2):** eligible completed-hour XAU clock; output usable only after the corresponding one-hour bar is complete;
- **future change-time challenger:** native clock must be explicitly preregistered; no output may be credited before all inputs required at that origin are complete;
- **Monthly H=1 / Monthly Direction:** strategic monthly clock;
- **Macro Event / Market Shock:** event-triggered intraday clock when that research lane is active;
- **GVZ_RISK:** completed GVZ daily-close clock under the frozen R4.1 implementation.

A slower state may be carried forward only under its native-clock semantics and must carry explicit `age` / `state_age` information.

Missing channels may not be silently imputed as neutral or zero.

### 6.1 Binding signal-availability rule

A model output cannot be credited before the latest input needed to compute that output was actually available.

For completed-daily-close engines such as FAST and GVZ_RISK:

- a state calculated using date `t` close becomes usable only **after that close**;
- a volatility event realized during date `t` cannot be called an `EARLY_HIT` using a signal that itself requires date `t` close;
- same-date daily-close overlap is at most `SAME_EVENT_CONFIRM` / same-date diagnostic unless an earlier timestamp independently proves availability;
- genuine one-session-ahead warning comparison must use the latest completed engine origin strictly before the event session;
- no event date may be used to select which historical engine date is treated as the signal origin.

Each motor must declare its native decision time before outcome overlay.

---

## 7. Governance locks

Binding rules:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `NOT_PROVEN_POSITION_MAPPING`
- no automatic `BUY / SELL / HOLD / EXIT / REDUCE`
- no flat/equal-weight voting across heterogeneous engines
- no hindsight threshold tuning
- no random-split time-series validation
- no silent provider substitution
- no interpolation or forward-fill of missing canonical XAU session references
- no backdating of reconstruction/replay evidence
- no historical reconstruction relabelled as prospective evidence
- no target/future observation inserted into an earlier origin
- no challenge/stress result used to retune that locked challenge/stress evaluation
- no production forecast/decision authority write without explicit later authorization
- no stale context labelled fresh merely because an identity remains registered
- no fabricated state or feature when a historical channel is unavailable
- no rejected model family rescued by post-score tuning
- no same-day completed-close value labelled as a pre-event warning for an event already realized during that session
- no event-conditioned backward search presented as alarm precision, warning accuracy or false-warning performance
- no post-hoc warning horizon chosen because it makes 2025 results look better
- no suspended motor silently reactivated merely because historical code/contracts remain in GitHub
- no ordinary BOCPD retuning represented as future-change-time prediction without a separately named identity and preregistration

When evidence is absent or unproven, use `NOT_FOUND`, `NOT_PROVEN`, `UNRESOLVED`, `BLOCKED`, `NOT_TESTABLE` or `INSUFFICIENT_SUPPORT` as appropriate.

---

## 8. Evidence classes and point-in-time semantics

Evidence classes remain separate:

- `HISTORICAL_REPLAY`: reconstructed after the original origin using information bounded to that historical origin;
- `PROSPECTIVE_SHADOW`: issued after the governed mechanism is frozen/deployed and before the relevant future outcome is known;
- `LIVE_PRODUCTION`: only when separately authorized.

For every historical origin, all features, model states and reliability estimates must respect information available at that origin. Later target observations, future price paths and later revisions are forbidden from predictor construction or model selection.

Historical reconstruction is never proof that a signal was actually issued live at that historical time.

---

## 9. Canonical XAU / NY17 contract

Canonical tactical XAU series:

`XAU_EOD_TWELVE_NY17`

Provider/input contract:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval: `1min`;
- requested timezone: `America/New_York`;
- accepted bar: unique exact `16:59:00` source bar;
- accepted value: `close` after positive/range-valid OHLC checks;
- stored timestamp: corresponding 17:00 ET session boundary converted to UTC;
- fallback: none;
- interpolation: forbidden;
- forward-fill: forbidden;
- alternate-provider substitution: forbidden;
- official CME/EBS settlement/fixing claim: forbidden.

The Twelve Data value is Gold Control's internal NY17 reference, not an official CME settlement/fixing price.

Exact historical provider gaps remain gaps; a different bar may not be inserted into the canonical series merely to improve coverage.

---

## 10. Frozen GC-BREAK structural event-label rule

The primary GC-BREAK ground-truth event definition is engine-independent.

Binding rule:

- family: volatility-normalized directional change;
- daily log return;
- volatility scale: trailing 20 governed observations;
- sigma lagged one observation;
- primary threshold: `k = 3.0`;
- current regime extreme updated causally;
- break timestamp: first governed observation whose adverse move from the regime extreme reaches the frozen threshold;
- after an event, regime direction flips and the extreme resets to the event close.

`k = 2.5` is sensitivity-only and may not replace `k = 3.0` because a downstream model scores better.

FAST, SLOW, Monthly Direction, Emergency, BOCPD, GVZ, Macro Event, Market Shock and learned models may not define this structural ground truth.

---

## 11. Frozen 2025 volatility challenge

Authority file:

`gold_axis_2026/GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_CONTRACT_V1_2026-09-15.md`

Research event source:

`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`

This source is research-only and does not replace canonical exact-16:59 NY17 runtime semantics.

Cross-check facts:

- 2025 governed research weekdays: **255**;
- same-day overlap with exact 16:59 one-minute cache: **197**;
- equal close values on same-day overlap: **197 / 197**;
- directly comparable daily-return pairs: **168**;
- return correlation: **1.000000**;
- mean absolute return difference: **0.000000 percentage points**;
- sign agreement: **168 / 168**.

Frozen event formula:

`r_t = 100 * ln(P_t / P_{t-1})`

`sigma20_t = sample standard deviation of the 20 immediately preceding governed daily log returns`

`z_t = r_t / sigma20_t`

Frozen tiers:

- **MAJOR:** `|z_t| >= 2.0`
- **EXTREME:** `|z_t| >= 3.0`

The frozen inventory contains **19 event-days**, of which **5 are EXTREME**, with **14 UP / 5 DOWN**:

1. `2025-02-10` UP `+2.3407`
2. `2025-02-14` DOWN `-2.2468`
3. `2025-02-18` UP `+2.1885`
4. `2025-03-13` UP `+2.1237`
5. `2025-04-04` DOWN `-3.3930` EXTREME
6. `2025-04-09` UP `+3.2185` EXTREME
7. `2025-04-10` UP `+2.3440`
8. `2025-07-21` UP `+2.0611`
9. `2025-08-01` UP `+2.5481`
10. `2025-09-02` UP `+2.6673`
11. `2025-09-22` UP `+2.6254`
12. `2025-09-29` UP `+2.3040`
13. `2025-10-06` UP `+2.7911`
14. `2025-10-13` UP `+2.5043`
15. `2025-10-16` UP `+2.9074`
16. `2025-10-17` DOWN `-2.0589`
17. `2025-10-21` DOWN `-4.1054` EXTREME
18. `2025-12-22` UP `+4.0174` EXTREME
19. `2025-12-29` DOWN `-6.6415` EXTREME

These dates are retrospective outcomes, not information available to a live motor before they occur.

### 11.1 Engine-first evaluation lock

The binding evaluation direction is **engine first, challenge overlay second**.

For every evaluated engine:

1. run/replay the engine across its complete eligible origin set on its native clock;
2. retain signals, abstentions, state transitions, episode onsets, persistence/age, missingness and blocked/not-testable states;
3. freeze the complete engine-output table before outcome overlay;
4. only then compute event coverage, false-warning burden, lead/lag, same-event confirmation and role-specific support;
5. do not choose warning horizon, carry window, threshold, score mapping or episode rule after viewing challenge outcomes;
6. retain exact engine signal dates even when no event is nearby.

Event-conditioned backward lookup alone is diagnostic and is not alarm-performance evidence.

---

## 12. Current validated motor evidence

### 12.1 FAST

Evidence class: `HISTORICAL_REPLAY / RETROSPECTIVE_DIAGNOSTIC`.

- complete 2025 governed timeline: **255 daily rows**;
- frozen rule: SMA20 + two completed-daily observations on the same side;
- new robust episode onsets: **22**;
- descriptive same-direction future-event incidence after onset: 1-day `1/22`, 3-day `2/22`, 5-day `3/22`, 10-day `5/22`;
- same-event day `1/22` is not early-warning credit under completed-close semantics.

FAST is retained as a **daily tactical trend-state engine** and is not proven as a standalone volatility-warning engine.

### 12.2 GVZ_RISK

Role: **RISK_ONLY**. No UP/DOWN direction vote.

Frozen R4.1 mapping:

- `GVZ <= 25.9795` -> `NORMAL`, cap `1.0`;
- `25.9795 < GVZ <= 30.5238` -> `ELEVATED`, cap `0.5`;
- `GVZ > 30.5238` -> `PANIC`, cap `0.25`.

2025 historical replay facts:

- source: `GVZ_CBOE_FRED_MIRROR_RESEARCH_V1`;
- valid daily observations/scored rows: **250 / 250**;
- frozen-score mismatch: **0**;
- FAST used in score: **false for all rows**;
- `NORMAL`: **237** days;
- `ELEVATED`: **10** days;
- `PANIC`: **3** days.

Same-date overlap with a completed GVZ daily close is not credited as pre-event warning for an event already realized that date.

GVZ_RISK is retained as a **selective market-stress / risk-context motor**. General volatility-day prediction performance is not proven; the PANIC sample is too small for promotion claims.

### 12.3 BOCPD

See Section 4. The retained BOCPD research authority is V5 + R2 only. BOCPD is retained as regime/change context; it is not to be further tuned on visible 2025 outcomes as the project’s future-change-time predictor.

### 12.4 Macro Event

`MACRO_EVENT_SUCCESSOR_V2` remains a governed runtime registry identity, and historical V3/V4 research contracts remain traceable, but the Macro Event lane is **suspended for the current GC-BREAK research sequence**.

Do not interpret old Macro Event preregistrations, workflows or runtime registration as an instruction to resume it next. Reactivation requires explicit new project direction/change control.

### 12.5 Emergency and SLOW

- `EMERGENCY_LEVEL`: suspended / redesign required.
- `EMERGENCY_REVERSAL`: suspended.
- `SLOW`: low-priority confirmation/new-regime context; not the immediate next motor.

### 12.6 Next motor / future-change-time challenger

The next research motor is a **new, separately named future-change-time prediction challenger**. Its scientific family is residual-time / explicit-duration / Bayesian online prediction of changepoints or a closely equivalent causally valid duration-hazard formulation.

Binding design boundary:

- objective: estimate whether / when a break or changepoint is approaching, rather than only detect that a regime change may already have occurred;
- BOCPD V5 remains complementary regime/change context and is not silently renamed into this motor;
- formation/development must use pre-2025 chronology; 2025 is not available for parameter tuning or model selection;
- no random split;
- native clock, warning horizon, episode formation, output semantics and evaluation rule must be preregistered before outcome overlay;
- exact model identity and parameterization remain `NOT_FROZEN` until that preregistration is created.

---

## 13. Frozen research split

### Formation / development

`2022-01-01 .. 2024-12-31`

Permitted use: label-quality inspection, baseline development, rolling/prequential internal validation, calibration/reliability estimation and architecture development under frozen governance.

### Retrospective Challenge

`2025-01-01 .. 2025-12-31`

Locked retrospective challenge. No threshold, feature or model choice may be derived from its outcomes and then claimed as untouched challenge evidence.

### Retrospective Stress / transport

`2026-01-01 .. 2026-08-31`

Researcher-visible retrospective stress/transport period; not fresh blind OOS evidence.

### Prospective Shadow

Begins only after final architecture/parameter freeze and before future outcomes are known.

Random splitting is forbidden.

---

## 14. Current work-package and sequencing status

1. **Coverage / PIT audit — COMPLETE**
2. **WP0 — State / break-label contract — COMPLETE / FROZEN**
3. **WP1 — PIT-safe formation panel — COMPLETE**
4. **WP2 — independent break-event inventory — COMPLETE WITH DATA-DENSITY WARNING**
5. **Split Freeze — COMPLETE / PRE-SCORE FROZEN**
6. **WP3 — preregistered simple formation baselines — COMPLETE WITH LIMITATIONS**
7. **2025 volatility challenge inventory — FROZEN**
8. **FAST full-timeline replay — COMPLETE**
9. **GVZ_RISK full-timeline historical replay — COMPLETE**
10. **BOCPD retained research comparison — COMPLETE FOR CURRENT V5/R2 CHECKPOINT**
11. **Macro Event — SUSPENDED FOR CURRENT SEQUENCE**
12. **Emergency Level/Reversal — SUSPENDED; Level requires redesign**
13. **SLOW — LOW PRIORITY / NOT NEXT**
14. **Post-BOCPD future change-time challenger — NEXT GC-BREAK RESEARCH LANE; exact identity/parameters require preregistration**
15. **Parallel direction-research lane — RSM/ERSM CLOSED / DO_NOT_REVISIT; corrected VLMC-BS family V2 NO_PROMOTION / 2025_GENERALIZATION_WEAK; BCT/CTW-52 NO_PROMOTION; B-CARS source-form BLOCKED and boundary-safe successor NO_PROMOTION**
16. **WP4 role-preserving integration/state-transition work — AFTER the new challenger has a frozen design/evidence checkpoint**
17. **Architecture/parameter freeze — PENDING**
18. **Prospective shadow — PENDING FINAL FREEZE**

The next research lane is therefore **not inferred from runtime-registry order**. It is the separately governed future-change-time challenger defined in Section 12.6. Macro Event, Emergency and SLOW remain outside the immediate next step unless explicitly reactivated.

---

## 15. Post-BOCPD future model-development rule

Ordinary BOCPD is primarily an online **change-detection / regime-context** mechanism: after new evidence arrives, it updates belief that a change may have occurred. The next scientific question is different: whether the system can estimate **time-to-change / residual time / approaching-break hazard before the break**.

Accordingly, the next motor must be a separately named and preregistered future-change-time challenger. Preferred research families include:

- residual-time prediction under non-geometric duration models;
- explicit-duration / semi-Markov or duration-hazard formulations;
- Bayesian online prediction of changepoints / learned or structured time-to-change models;
- another low-dimensional causal duration-hazard formulation only if its role and timing semantics are explicitly frozen.

An HMM/HSMM may be used as an implementation family **only if it serves this frozen future-change-time objective**; `HSMM` by itself is not the binding motor identity and is not automatically selected.

The exact identity, features, native clock, duration state, horizon/output definition, loss/objective, episode rule and evaluation metrics must be preregistered before the model is run against outcomes used for evaluation.

Chronology lock for the new challenger:

- use 2022–2024 as the pre-2025 research/design universe under time ordering;
- do not use 2025 to choose thresholds, duration family, features, warning horizon or parameterization;
- 2025 is researcher-visible and cannot be relabelled as pristine holdout after design choices informed by it;
- no random split;
- BOCPD V5/R2, FAST and GVZ may contribute only in role-preserving origin-safe form; no flat equal vote.

High-capacity boosting, mixture-of-experts and deep-learning escalation remain blocked until a simpler duration/hazard challenger justifies additional complexity under time-ordered evidence.

---

## 16. Historical research interpretation

Historical fixed-horizon, 1D/3D, V1.48/V1.49, HS-SDL-DMA and related studies remain historical/auxiliary research only.

Old result files or artifact names are not current project authority. Historical traceability belongs in Git history and/or immutable evidence storage.

Specific superseded interpretation locks:

- old event-conditioned FAST `11/19` is not current alarm performance;
- same-date GVZ daily-close overlap is not early-warning evidence;
- any result that hides full-year engine outputs by starting only from realized event dates is invalid for alarm-performance claims;
- old Macro Event research artifacts do not override the current Macro research suspension;
- superseded BOCPD identities do not re-enter because historical files or commits exist;
- an ordinary BOCPD retune is not the approved substitute for the new future-change-time challenger.

---

## 17. Neon / write authority

GC-BREAK currently has **no production forecast, decision or trading authority**.

Unless separately authorized later:

- no production decision-signal writes;
- no BUY/SELL/action mapping;
- no automatic selector/ensemble writes;
- no mutation of legitimately issued historical records;
- no speculative schema expansion solely for an unaccepted research challenger.

Research panels, labels, predictions and evaluations must remain logically separated and lineage-complete.

Historical research backfills must use explicit research series identities and truthful provenance. They may not silently overwrite direct-authority series identities.

---

## 18. Promotion and prospective-evidence rule

Binding scientific order:

`PIT-safe formation`

-> `independent event inventories`

-> `engine-first full native-clock replay`

-> `freeze exact engine outputs and signal timestamps`

-> `outcome overlay`

-> `role-preserving evaluation`

-> `BOCPD context freeze`

-> `separately preregistered future-change-time challenger`

-> `role-preserving integration / state-transition work`

-> `same-origin ablation / optional extensions`

-> `architecture + parameter freeze`

-> `prospective shadow`

A model is not promoted because it is theoretically elegant or retrospectively impressive. Promotion requires reproducible, time-ordered incremental evidence with adequate support and no leakage.

The strongest future claim comes only from outcomes first observed after final architecture/parameter freeze.

---

## 19. Final binding summary

Gold Control is a **role-preserving, multi-clock sequential early-warning / regime-transition research programme** running in parallel with an independent monthly H=1 price-level forecasting programme.

Two distinct retrospective event universes are explicit:

1. frozen GC-BREAK structural-break labels;
2. frozen 2025 volatility challenge of 19 abnormal daily moves.

Current validated motor checkpoint:

- FAST: replay complete, retained tactical context, standalone volatility warning not proven;
- GVZ_RISK: replay complete, retained risk context, no direction vote;
- BOCPD: V5 primary research reference + R2 frozen benchmark only; retained as regime/change context;
- Macro Event: runtime registry identity retained but **current research lane suspended**;
- Emergency Level/Reversal: suspended, with Level requiring redesign;
- SLOW: low priority, not next.

The **next GC-BREAK research motor/lane** is a new separately named **future-change-time prediction challenger** based on residual-time / explicit-duration / Bayesian online changepoint-prediction principles (or a causally equivalent preregistered duration-hazard formulation). Exact model identity and parameters are not yet frozen; the scientific lane is frozen. It must be designed with pre-2025 chronology and may not use visible 2025 outcomes for tuning.

In parallel, the direction-research families remain governed. RSM/ERSM is permanently closed as `TERMINATED / FAILED_METHOD_FAMILY / DO_NOT_REVISIT`; detailed history is audit-only and intentionally omitted from the manifest. The old VLMC-BS-52 V1 is audit-only. Corrected VLMC-BS family V2 is `NO_PROMOTION / SOURCE_FAITHFUL_REFERENCE_REPLICATION_COMPLETE / 2025_GENERALIZATION_WEAK`: k=52 validated strongly in 2024 but did not generalize in 2025; k=104 was more balanced in 2025 but had weaker pre-2025 evidence. BCT/CTW-52 is `NO_PROMOTION / WEAK_DIRECTIONAL_DISCRIMINATION`; it materially improves probability stability versus VLMC-BS but collapses to 52/52 UP forecasts in the 2025 replay. Source-form B-CARS V1 is blocked by genuine pre-2025 boundary up-ratios and was not scored. Its separately preregistered Smithson-Verkuilen boundary-safe successor, `DIRECTION_BCARS_SV_V1_RESEARCH`, is `NO_PROMOTION / PRE2025_VALIDATION_FAILED / WEAK_DIRECTIONAL_DISCRIMINATION`; in 2025 it forecast 51 UP / 1 DOWN with 0% DOWN sensitivity, while the frozen event overlay had 50% balanced direction accuracy. None may override GC-BREAK. The higher-moment direction-probability method is not selected for this set.

All future work must preserve point-in-time integrity, native engine clocks, role semantics, engine-independent event definitions, time-ordered validation, explicit missingness and strict separation of retrospective diagnostics from genuine prospective evidence.
