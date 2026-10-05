# GOLD SHORT-HORIZON GLOBAL XAU — MASTER PROJECT MANIFEST

**Manifest version:** 3.1  
**Effective date:** 2026-10-05  
**Document class:** CANONICAL MASTER RESEARCH MANIFEST / DECISION AUTHORITY  
**Scope:** Global XAU/USD short-horizon H3 direction research  
**Evidence cutoff:** information committed through 2026-10-05  
**Supersedes:** Manifest v3.0 and the prior long-form v2.0 narrative for current project-state interpretation

| Authority item | Current state |
|---|---|
| Primary target | XAU/USD H3 direction — next three retained Gold observation dates, UP/DOWN |
| Retrospective clean champion | **HELIOS V5-DCE** |
| Prospective umbrella | **CLEAN_H3_PROSPECTIVE_V1** |
| Prospective baseline | **CLEAN_AURORA_H3_V1_PROSPECTIVE** |
| Prospective V5 status | **CLEAN_V5_DCE_H3_V1_PROSPECTIVE_SHADOW** |
| Advanced competence challenger | **DPTC_H3_V1 Q95 + Q99 — frozen future shadow, post-hoc development** |
| First eligible CLEAN prospective feature cutoff | **2026-10-05** |
| Prospective performance | **NOT YET ESTABLISHED** |

**Governance note:** “Champion”, “baseline”, “shadow” and “promotion” in this document refer to the research program. No live-trading or production authorization is implied.

---

## 1. Purpose of this manifest

This file is the canonical high-level record of the Global-XAU short-horizon project.

It is intentionally a **decision manifest**, not an experiment log. It records:

- what the project is trying to predict;
- how the target and data contract evolved;
- the major model-development stages;
- which mechanisms materially improved the system;
- which methods were tested and closed or blocked;
- the current performance hierarchy;
- the scientific status of each result;
- the current prospective/live state;
- the exact next research question.

Detailed grids, scripts, run IDs, intermediate diagnostics and row-level evidence remain in their dedicated authority/result files and Git history. They are not duplicated here unless they are needed to understand a binding decision.

---

## 2. Research objective

The active problem is:

> At an origin-safe daily feature cutoff, predict whether XAU/USD will be UP or DOWN over the next three retained business-day observations.

Primary target:

H3 return = log(P[t+3] / P[t])

Direction:

- UP if H3 return > 0
- DOWN otherwise.

The target clock is defined on the **retained Gold observation calendar**, not on an assumed three-calendar-day interval.

Binding timeline fields:

| Field | Meaning |
|---|---|
| feature_cutoff_date | Last retained Gold observation date whose information may enter the feature set. |
| forecast_issue_date | Next retained Gold observation date after the feature cutoff; the forecast is issued before using that date's closing information. |
| target_end_date_h3 | Third retained Gold observation date after the feature cutoff, where the H3 outcome matures. |

This clock distinction is mandatory for auditability around weekends, holidays and source delays.

The current project is **not** a monthly forecasting project and is **not** the former BIST Metal Price tactical lane.

The older BIST-target short-horizon program is historical evidence only. Its instrument-mapping failure led to the current Global-XAU target authority.

### 2.1 Why H3 became the main horizon

The first Global-XAU screen evaluated H1, H3 and H5 under chronological pre-2025 selection.

Only H3 direction produced a repeatable pre-2025 signal. H1 and H5 did not justify promotion.

The project therefore converged from a generic short-horizon program to a focused **H3 directional research program**.

---

## 3. Scientific evidence classes

Every result in this project must be interpreted under one of the following evidence classes.

| Class | Meaning |
|---|---|
| FROZEN PROSPECTIVE | Rule/model fixed before the new origin; no outcome-dependent backfill or retuning. |
| FROZEN TRANSPORT / CONFIRMATION | Parameters selected earlier and replayed on a later period without using that period for selection. |
| RETROSPECTIVE DEVELOPMENT | Later outcomes were already visible during mechanism development. Useful for hypothesis development, not independent validation. |
| DIAGNOSTIC | Explains errors, state or mechanism; does not itself authorize a direction change. |
| CLOSED / NOT PROMOTED | Tested under its declared gate and did not add sufficient evidence. |
| BLOCKED | Scientifically relevant hypothesis could not be tested under the required data/source contract. |

**Binding rule:** A higher retrospective accuracy does not outrank a lower but genuinely prospective result merely because the number is larger.

### 3.1 Methodological controls

The project uses chronological, origin-safe evaluation rather than random train/test splitting.

Core controls:

- features may use only information available by the declared feature cutoff;
- future H3 outcomes may enter adaptive state only after maturity;
- early Global-XAU model selection used pre-2025 history, with 2025 frozen transport and 2026 reporting/stress;
- once later 2025/2026 outcomes were inspected for reversal-mechanism development, those periods were explicitly reclassified as **retrospective development evidence** for the affected mechanisms;
- no method may regain “OOS” status after its evaluation period has been consumed;
- overlapping H3 targets are serially dependent and are not treated as independent Bernoulli trials;
- dependence-aware moving-block bootstrap or other chronology-aware tests are preferred for inferential comparisons;
- missing eligible prospective origins are recorded rather than outcome-aware backfilled.

---

## 4. Data and timing authority

### 4.1 Daily target / metals history

The active historical daily metal reconstruction is the pinned public StakTrakr R2 research history, with Gold, Silver, Platinum and Palladium.

Frozen R2 source reference:

`54fdf1c8d39b7b6c7b874d0f30f784296e886044`

This history is a **research reconstruction**, not a claim of original historical point-in-time market availability.

A deep integrity audit identified one confirmed severe corrupt daily row:

- 2026-02-27.

The clean research chain corrects that row and rebuilds affected targets, features and downstream states.

No other daily observation was confirmed corrupt under the same-semantic independent-source audit.

### 4.2 Intraday information

The key new-information source is hourly XAU/USD from Twelve Data.

Registered historical identity:

`XAU_USD_TWELVE_1H_RESEARCH_V1`

IRIS and descendants use recent intraday path information under an explicit origin-time cutoff, anchored at **16:00 America/New_York** under the frozen IRIS contract. This source was the major information breakthrough of the project.

### 4.3 Auxiliary sources

Depending on the specialist:

- CME Gold futures volume;
- CME Gold call/put activity;
- preliminary Open Interest where available;
- Nasdaq-100;
- VIX;
- rates / FX under lagged availability rules;
- event/macro context where point-in-time semantics are available.

No auxiliary source is allowed to enter merely because it exists. It must have an explicit origin-safe clock and source identity.

### 4.4 Integrity policy

Future ingestion is fail-closed.

A quarantined or unavailable source row cannot:

- enter the admitted feature panel;
- generate a forecast;
- settle an H3 target;
- be retrospectively inserted after the outcome becomes known.

Daily-average Gold and NY17/intraday endpoint identities are not silently mixed.

---

## 5. Project evolution — from baseline failure to the current architecture

### Phase A — Global-XAU target repair and classical baseline

The former BIST-target lane was archived after cross-instrument mapping proved inadequate.

The project was rebuilt around Global XAU/USD with corrected source/timeline semantics.

The first robust daily comparator was:

- H3;
- CORE3 = Gold + Silver + Platinum path features;
- Logistic L2;
- raw probability stream.

On 2022-2024 DEV this model showed a small but consistent probabilistic edge.

However frozen transport failed:

| Period | CORE3 Logistic accuracy | Balanced accuracy |
|---|---:|---:|
| 2025 | 50.20% | 50.10% |
| 2026 Jan-Sep | 43.98% | 45.21% |

**Conclusion:** the original daily information set contained a pre-2025 signal but did not transport. The problem could not be solved by simply tuning the existing daily model.

---

### Phase B — Direct model substitutions and meta-gates did not solve transport

A series of alternative nonlinear, adaptive and meta-selection approaches was tested.

The important conclusion was not that every such method is intrinsically weak; rather, **changing the learner while keeping essentially the same information set did not repair the 2025-2026 regime failure**.

Two especially important negative results were:

- NOVA: novelty/regime-shift detection did not identify a directionally forecastable state.
- FERG: a pre-call error-risk selector trained on the same daily state failed confirmation and often reversed sign.

This changed the research question from:

> Which model should replace Logistic?

to:

> What genuinely new origin-safe information is missing?

---

### Phase C — IRIS: intraday path information was the first major breakthrough

IRIS added hourly XAU/USD path information instead of another daily-model substitution.

Frozen representation:

- A1 structural daily baseline;
- recent 1h/3h/6h/12h/24h/48h path returns;
- related compact path features.

The selected A1+PATH representation produced:

| Period | Accuracy | Balanced accuracy |
|---|---:|---:|
| 2023 selection | 71.23% | 71.83% |
| 2024 frozen confirmation | 70.83% | 69.97% |
| 2025 frozen transport | 63.71% | 62.27% |
| 2026 stress | 58.64% | 59.12% |

Timing/placebo tests supported the interpretation that recent intraday path information carried real incremental information.

**Scientific turning point:** the project stopped treating the problem as a purely daily-feature classification problem.

#### Secondary numerical H3 return head

IRIS also produced a separately governed numerical return head:

**IRIS_H3_RETURN_V1**

Frozen model:
- ElasticNet alpha 0.0005;
- same origin-safe IRIS information set;
- causal 80% conformal interval.

Key transport result:

| Period | MAE | Sign accuracy | Mean 80% interval width |
|---|---:|---:|---:|
| 2025 | 1.37% | 65.32% | 3.90% |
| 2026 | 2.57% | 60.21% | 5.65% |

Interpretation:
- directional sign transports better than exact return magnitude;
- 2026 magnitude uncertainty expands materially;
- this head is retained as a **secondary magnitude/uncertainty output** and does not override the primary direction architecture.

---

### Phase D — Adaptive expert routing: SENTRY, DART and AURORA

IRIS exposed two useful experts:

1. STRUCTURAL_IRIS — daily structure + intraday PATH;
2. PATH_GLOBAL — intraday PATH-dominant expert.

Their relative competence changed over time.

#### SENTRY

SENTRY used a rolling matured paired-rescue score for hard failover.

It preserved the strong 2023-2024 structural regime and improved later transport.

#### DART

DART updated only on expert-disagreement events with a Bayesian online change-point mechanism.

It detected a PATH regime in late 2025 and remained PATH-active through 2026.

#### AURORA

AURORA combined:

- SENTRY fast entry;
- DART slow exit.

This asymmetric hysteresis preserved the strong historical structural regime while adapting to the later PATH regime.

Clean AURORA reference:

| Period | Accuracy | Balanced accuracy |
|---|---:|---:|
| 2023 | 71.23% | 71.83% |
| 2024 | 70.83% | 69.97% |
| 2025 | 64.52% | 62.93% |
| 2026 clean | 58.64% | 59.02% |

AURORA became the base router for the subsequent reversal architecture.

---

### Phase E — HELIOS: explicit reversal-specialist architecture

AURORA remained strong in continuation/trend persistence but still missed too many reversals.

The research program therefore shifted from general direction models to **selective reversal specialists and guarded routing**.

The sequence included RIFT, TURN, VEGA, OPAL and HELIOS V1-V5.

The final clean retrospective version is:

**HELIOS V5-DCE — Dominant-Expert Contradiction Exception**

Clean 2026 result:

- 121 / 191 correct;
- accuracy **63.35%**;
- balanced accuracy **63.76%**.

Clean 2025 result:

- 165 / 248 correct;
- accuracy **66.53%**.

Clean 2025-2026 combined:

- accuracy **65.15%**.

V5 is preferred over other recent HELIOS/OPAL variants because it combines the best clean directional result with stronger probability quality.

**Current retrospective clean direction champion: HELIOS V5-DCE.**

Prospective governance is different: under `CLEAN_H3_PROSPECTIVE_V1`, CLEAN AURORA is the baseline and CLEAN V5-DCE is a shadow challenger.

---

### Phase F — Data-integrity correction

A severe 2026-02-27 source corruption was independently verified.

The project then:

- corrected the single proven row in a separate clean chain;
- rebuilt affected labels/features;
- re-ran the recent model family;
- added a fail-closed Data Integrity Gate.

The major model hierarchy survived the correction.

This is important because the current architecture is not based on a known bad-tick artifact.

---

### Phase G — Residual reversal search: broad specialist expansion mostly failed

After clean V5, the dominant remaining weakness was missed reversals.

Several channels were tested:

- Flow / Volume / Open Interest;
- options/skew;
- duration/hazard;
- cross-market divergence;
- RTE transition engines;
- regime-conditioned and support-constrained RTE;
- fuzzy/uncertainty representations;
- TRES event-time survival;
- orthogonal surprise.

Most direct FLIP mappings either lacked selectivity, failed transport, or were data-blocked.

One important positive diagnostic survived:

**TRES event-time survival strongly separated reversal risk**, but simple conversion of that risk into a directional override reduced performance.

This distinction became central:

> Detecting elevated reversal risk is easier than deciding when it is safe to overturn an already-good continuation forecast.

---

### Phase H — SAGE and RuleFlow: rare high-precision exceptions

SAGE separated broad uncertainty from rare orthogonal concurrence.

The useful component was the exception-only OCS rule; the abstention mapping was rejected.

#### SAGE V2 exception-only

2026 retrospective development:

- V5: 121/191 = 63.35%;
- SAGE V2: 125/191 = **65.45%**;
- balanced accuracy: **65.81%**.

SAGE V2 is frozen as a prospective shadow challenger; it does not replace V5 until its future promotion gate is met.

#### RuleFlow V3-TG

RuleFlow added a distinct reversal mechanism.

A topology gate was introduced after RuleFlow V2 failed in 2026 Q2-Q3.

The combined retrospective reference became:

- **126/191 = 65.97%**
- balanced accuracy **66.31%**.

This 126/191 combined system is the reference baseline for the later competence-transition research.

It is **not independent OOS validation** because RuleFlow V3-TG was designed after observing later failures.

---

### Phase I — Remaining-error anatomy: the problem became a competence problem

After the combined system, 65 errors remained.

Of those:

- **53 were missed reversals**;
- approximately **81.5% of all remaining errors**;
- clustered into about **22 reversal episodes**.

The Remaining-53 audit found a repeated temporal structure:

external / lead-lag pressure  
→ trend initially resists  
→ internal Gold structure/flow deteriorates  
→ reversal risk rises.

Key origin-to-origin transition signal:

- reversal misses internal t-1 -> t mean change: **+0.085**;
- correct continuations: **-0.048**;
- SMD approximately **+0.395**.

The same qualitative direction appeared in 2025.

This led to the **Handoff** concept.

---

### Phase J — Handoff itself was not enough

Canonical broad Handoff:

- external_premax >= 0.60;
- internal_now >= 0.60;
- internal_d1 >= 0;
- combined baseline still follows momentum.

Raw Handoff performance:

| Period | Alarms | Rescue | Broken | Precision |
|---|---:|---:|---:|---:|
| 2025 | 13 | 4 | 9 | 30.8% |
| 2026 | 28 | 16 | 12 | 57.1% |

A direct Handoff state-machine FLIP failed in 2025:

- 6 actions;
- 3 rescue / 3 broken;
- net 0.

Therefore:

**Handoff is not a deterministic reversal signal. Its competence is state-dependent and time-varying.**

This was the second major conceptual turning point of the project.

---

### Phase K — Independent competence mechanisms

The Handoff problem was studied from multiple scientific angles rather than by fitting another threshold.

#### 1. SELLR — sequential evidence

A multi-mechanism tournament compared:

- multivariate change-point logic;
- sequential evidence log-likelihood ratio;
- duration/hazard;
- historical analogues.

Only SELLR passed the pre-2026 selection gate.

Frozen SELLR threshold:

**2.3677413378977423**

2026 frozen stress:

- 1 action;
- 1 rescue / 0 broken;
- combined baseline 126/191 -> **127/191 = 66.49%**;
- balanced accuracy **66.81%**.

Coverage is low, but SELLR is important because its threshold was selected before its 2026 stress.

#### 2. BOCPD competence tracking

A Bayesian online change-point model tracked whether the Handoff expert itself had become trustworthy.

BOCPD V4 retrospective development:

- 10 actions;
- 8 rescue / 2 broken;
- net +6;
- precision 80%;
- assisted 132/191 = **69.11%**;
- BA **69.36%**;
- trust entry: **2026-05-27**.

This is post-hoc development evidence.

A broad adversarial audit nevertheless showed substantial robustness:

- 162 neighboring parameter combinations;
- 92.6% positive net;
- median net +5;
- 54 combinations reached +6;
- stationary-null P(net >= +6) = 0.0004;
- chronology permutation P(net >= +6) = 0.0284;
- worst leave-one-month-out net = +2.

The effect therefore does not appear to be a single-threshold or single-month artifact, even though it is not independent validation.

#### 3. Online expert aggregation

Theory-fixed fixed-share Hedge variants also detected increasing value of the Handoff expert.

Best reported development variant:

- alpha 0.075;
- net +5;
- assisted accuracy **68.59%**.

This supported the competence-shift hypothesis through a mechanism independent of BOCPD.

---

### Phase L — Dependence Phase: an origin-observable market counterpart

General marginal/covariate drift did **not** explain the April-May competence transition.

The project then examined cross-asset dependence directly:

- r_GN = prior-60 correlation(Gold, Nasdaq);
- r_GV = prior-60 correlation(Gold, VIX).

Strong-pro-risk topology:

- r_GN > 0;
- r_GV < 0;
- at least one correlation statistically significant.

The label-free detector was calibrated without reversal outcomes.

Critical result:

- first 2026 Dependence Phase: **2026-04-30**;
- offline competence change-point: **2026-04-30**.

Handoff performance:

| State | Rescue / N | Precision |
|---|---:|---:|
| Inside dependence phase | 9 / 11 | **81.8%** |
| Outside phase | 7 / 17 | **41.2%** |

This provided an origin-observable structural interpretation of the competence change:

**the Handoff expert becomes substantially more useful under a changed Gold-Nasdaq/VIX dependence structure.**

---

### Phase M — DPTC V1: current advanced challenger

DPTC = **Dependence-Phase Transition Controller**.

It deliberately separates three jobs:

1. **PRE-TRUST / Dependence Phase**  
   Before trust, Handoff can act only when the label-free dependence condition permits it.

2. **CATALYST / SELLR**  
   Frozen SELLR evidence can open TRUST.

3. **TRUST / Hysteresis**  
   Once trusted, canonical Handoff remains active until two consecutive matured acted BROKEN outcomes; a RESCUE resets the failure streak.

Two variants were frozen together. Future data may not be used to choose whichever one looks better.

| Variant | 2026 actions | Rescue | Broken | Net | Action precision | Accuracy | BA | Worst leave-one-month-out net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DPTC-Q95 | 13 | 11 | 2 | +9 | **84.6%** | **70.68%** | **70.86%** | +5 |
| DPTC-Q99 | 12 | 10 | 2 | +8 | 83.3% | 70.16% | 70.36% | +4 |

**Scientific status:** POST-HOC DEVELOPMENT CHALLENGER.

The 70.68% result is therefore **not the proven prospective accuracy of the project**.

DPTC is frozen for future shadow evaluation.

---

## 6. Current performance hierarchy

The following table is the correct way to quote the project as of 2026-10-05.

| Layer / system | 2026 result | BA | Evidence status | Interpretation |
|---|---:|---:|---|---|
| Clean AURORA | 58.64% | 59.02% | retrospective clean baseline | adaptive base router |
| Clean HELIOS V5-DCE | **121/191 = 63.35%** | **63.76%** | authoritative clean retrospective champion | retrospective champion; prospective V5 shadow |
| SAGE V2 exception-only | **125/191 = 65.45%** | 65.81% | retrospective development; frozen shadow | rare OCS exception |
| SAGE V2 + RuleFlow V3-TG | **126/191 = 65.97%** | **66.31%** | retrospective combined reference | competence-research baseline |
| Frozen SELLR single-action test | **127/191 = 66.49%** | **66.81%** | threshold selected on 2025 before 2026 stress; very low coverage | temporally pre-frozen incremental evidence |
| BOCPD V4 | 132/191 = **69.11%** | 69.36% | post-hoc development | robust competence-state diagnostic |
| STCR — SELLR-triggered persistent competence state | 133/191 = **69.63%** | 69.86% | post-hoc synthesis | competence-transition challenger |
| DPTC-Q99 | 134/191 = **70.16%** | 70.36% | post-hoc development challenger | strict shadow variant |
| DPTC-Q95 | **135/191 = 70.68%** | **70.86%** | post-hoc development challenger | strongest development result |

### 6.1 What may and may not be claimed

May be claimed:

- Clean HELIOS V5-DCE achieved 63.35% accuracy on the clean 2026 retrospective universe.
- The retrospective SAGE + RuleFlow reference reached 65.97%.
- A pre-2026-frozen SELLR trigger added one successful action in 2026.
- Multiple independent analyses support a competence transition around late April-May 2026.
- DPTC reached 70.68% in post-hoc development and has been frozen for future shadow testing.

Must **not** be claimed:

- that the project's proven prospective accuracy is 70.68%;
- that DPTC has independent 2026 OOS validation;
- that retrospective exception rules are production-certified;
- that overlapping H3 origins are independent Bernoulli trials.

**Prospective accuracy is not yet established.**

---

## 7. Tested but non-contributing, closed or blocked paths

The following methods are retained here only so future work does not unknowingly repeat them.

| Family / method | Result | Decision / lesson |
|---|---|---|
| Former BIST short-horizon target | Cross-instrument mapping inadequate | Archived; Global-XAU target replaced it. |
| Classical daily CORE3 Logistic | DEV signal but 2025/2026 transport failed | Retained only as historical comparator. |
| Vanilla ANFIS | Worse than Logistic on DEV | Closed for current H3 lane. |
| ChHHO-ANFIS | No DEV promotion; 2026 probabilities badly calibrated | Monthly success did not transfer to H3 direction. |
| Raw-source shallow CART screens | No stable promotable pattern | Diagnostic only. |
| NOVA novelty/regime model | Detected stress but not direction | Novelty is not forecastability. |
| FERG error-risk gate | Confirmation reversed / negative selection | Same-information meta-gating closed. |
| SAGE V1 session decomposition | No eligible pre-2023 representation | Session idea not promoted. |
| AIM adaptive mixture | Averaging diluted the stronger expert | Hard/state routing preferred. |
| VISTA dynamic BOCPD hazard | Same decisions as DART | Mechanism-pass but non-incremental. |
| TWIN path-shape analogues | No eligible representation | Closed unless representation changes materially. |
| PRISM wavelet residual | No eligible regularization | Closed. |
| FLOW-VOL | Low selectivity | Not promoted. |
| Preliminary Volume+OI FLOW | No eligible threshold | Aggregate preliminary OI representation not promoted. |
| FINAL OI branch | Required historical access unavailable | BLOCKED, not scientifically disproven. |
| Directional Gold CVOL / SKEW | Entitlement unavailable | BLOCKED, not scientifically disproven. |
| HAZARD | Recall gained only with excessive false positives | Closed. |
| DIVERGE exact source | Source blocked | BLOCKED. |
| DIVERGE proxy | No eligible selectivity | Closed. |
| RTE V1-V4 | Strong development pockets, failed 2025 transport / half-year stability | Closed as scalar threshold family. |
| RC-RTE V1/V2 | 2026 clean holdout produced net -1 | Not promoted. |
| SCR-RTE | Retrospective net -7 | Shadow-only / closed for override. |
| Fuzzy tournament: T1/IFS/Pythagorean/q-rung/Hesitant/Picture/Neutrosophic/IT2 | No directional FLIP representation passed | Direction branch closed; weak confidence damping only. |
| TRES survival | Strong reversal-risk representation | Retained as diagnostic; direct FLIP/abstention mappings failed. |
| ORS local reversal surprise | Net negative | Closed. |
| Static KMeans latent regimes | Weak separation; no reliable Handoff gate | Static regime classification rejected. |
| Direct Handoff state machine | 3 rescue / 3 broken in selected 2025 variant | Handoff is not a deterministic FLIP signal. |
| Generic label-free marginal drift | Did not locate competence transition | Problem is dependence/conditional structure, not simple marginal drift. |
| Alternative competence mechanisms: change-point, duration/hazard and historical analogue candidates | Did not pass the pre-2026 tournament gate | SELLR was the only retained tournament signal. |

This table does **not** mean blocked methods are scientifically false. It distinguishes negative empirical evidence from missing-data/access constraints.

---

## 8. Current architecture map

The project should now be understood as a layered system rather than a single classifier.

### Layer 1 — Information

- clean daily metals / CORE3 structure;
- hourly XAU intraday PATH;
- selected options/flow/cross-asset state under origin-safe clocks.

### Layer 2 — Base expert routing

**AURORA**

- STRUCTURAL_IRIS versus PATH_GLOBAL;
- fast SENTRY-style entry;
- slow DART-style exit.

### Layer 3 — Reversal handling

**HELIOS V5-DCE**

- guarded reversal specialists;
- OPAL/HELIOS routing and contradiction exceptions;
- current **retrospective clean champion**;
- prospective status: **CLEAN V5-DCE shadow challenger**, not the umbrella baseline.

### Layer 4 — Rare orthogonal exceptions

**SAGE V2 + RuleFlow V3-TG**

- frozen shadow/development exceptions;
- combined retrospective reference 126/191.

### Layer 5 — Competence transition

**DPTC V1**

- label-free dependence phase;
- frozen SELLR catalyst;
- hysteretic trust of canonical Handoff.

This layer is currently **shadow research**, not promoted production authority.

---

## 9. Prospective governance from 2026-10-05

### 9.1 Umbrella prospective authority

The current clean forward experiment is:

**CLEAN_H3_PROSPECTIVE_V1**

Freeze date: **2026-10-03**  
First eligible feature cutoff: **2026-10-05**

Its formal hierarchy is:

1. **Baseline:** CLEAN_AURORA_H3_V1_PROSPECTIVE
2. **Shadow challenger:** CLEAN_V5_DCE_H3_V1_PROSPECTIVE_SHADOW

This distinction is binding. HELIOS V5-DCE is the strongest clean retrospective architecture, but it has **not** been prospectively promoted over CLEAN AURORA.

At the current evidence cutoff:

- CLEAN AURORA prospective forecast rows: **0**
- CLEAN AURORA settled rows: **0**
- CLEAN V5 shadow forecast rows: **0**
- CLEAN V5 shadow settled rows: **0**

Therefore **prospective performance is not yet estimable**.

No post-freeze outcome may be used to:

- change a V1 threshold;
- alter source lags or feature timing;
- reconstruct a missed eligible forecast after outcome information is available;
- rewrite an already-issued probability or direction;
- promote V5, SAGE, RuleFlow or DPTC on retrospective evidence alone.

Any substantive modification requires a new named version.

### 9.2 SAGE V2 shadow governance

SAGE V2 is a separately frozen exception-only shadow challenger whose internal comparison baseline is HELIOS V5-DCE.

Its historical 2025/2026 gains are development evidence. They do not change the umbrella CLEAN prospective baseline.

### 9.3 RuleFlow V3-TG governance

RuleFlow V3-TG is a frozen post-hoc mechanism candidate for genuinely unseen origins. Its retrospective 2026 gain is not independent validation and does not create production or baseline authority.

### 9.4 DPTC governance

Both DPTC-Q95 and DPTC-Q99 remain frozen in parallel from 2026-10-05 onward.

Future outcomes may compare them, but may not be used to choose one retrospectively, redefine their thresholds or alter the trust-state logic.

DPTC promotion requires genuinely prospective evidence.

---

## 10. 5 October 2026 operational snapshot

Two different clocks must be kept separate.

### 10.1 CLEAN prospective experiment

`CLEAN_H3_PROSPECTIVE_V1` was frozen on 2026-10-03 with:

**first eligible feature cutoff = 2026-10-05**

Therefore a 2026-10-02 feature-cutoff forecast is **not an eligible CLEAN prospective origin** and must not be entered as a CLEAN prospective MISS or forecast.

As of the evidence cutoff, both CLEAN AURORA and CLEAN V5 shadow ledgers contain zero prospective forecasts.

### 10.2 Legacy / pre-clean source state

The earlier prospective infrastructure expected post-freeze metal observations from the pinned StakTrakr source, which had not advanced beyond 2026-09-29 during the 5 October review.

This source lag explains why the earlier source-complete chain could not produce a normal 2026-10-02 origin forecast.

That historical operational state must not be confused with the later CLEAN prospective eligibility contract.

### 10.3 Separate diagnostic nowcast for the 5 October morning question

To answer the user-requested 5 October morning question, a separate **diagnostic-only** run used:

**feature cutoff = 2026-10-02**

because 5 October closing information was not available at the morning issuance time.

Important provenance correction:

- the diagnostic JSON label says “TwelveData daily spot”;
- the successful implementation actually preserved the frozen 2026-09-29 spot level and extended Gold/Silver/Platinum/Palladium using **Yahoo futures daily returns** from GC=F, SI=F, PL=F and PA=F;
- Twelve Data was used for the hourly XAU extension.

Therefore the 2 October nowcast is:

**DIAGNOSTIC BRIDGE ONLY — NOT CLEAN PROSPECTIVE EVIDENCE.**

AURORA diagnostic output:

- p(UP) = **0.30075169**;
- direction = **DOWN**;
- active expert = PATH_GLOBAL;
- h_ret_12 = -1.049%;
- h_ret_24 = -0.864%;
- h_ret_48 = -0.360%.

HELIOS V5-DCE diagnostic output:

- direction = **DOWN**;
- candidate_reversal = False;
- OPAL override = False;
- GT flip share ≈ 4.60%;
- V4 route = False;
- RGE active = False;
- DCE exception = False.

### 10.4 Diagnostic call

**5 October 2026 morning diagnostic direction: DOWN**

Model-internal p(DOWN) is approximately **69.9%**.

This probability is a model output under the diagnostic bridge; it is not a calibrated prospective success probability and must not be included in prospective performance statistics.
---

## 11. Current scientific interpretation

The project has evolved through three distinct scientific problems.

### Stage 1 — ordinary prediction problem

Initial question:

> Can daily cross-asset features predict H3 direction?

Answer:

Only weakly; the original daily signal did not transport.

### Stage 2 — information problem

Question:

> Is useful information missing from the daily panel?

Answer:

Yes. Recent intraday XAU path information materially improved confirmation and transport. This produced IRIS and then adaptive AURORA.

### Stage 3 — conditional competence problem

Question:

> Why does the strong trend/continuation architecture still fail in reversal episodes?

Current answer:

The decisive issue is not simply whether a reversal-risk feature is high. The **competence of the reversal/Handoff expert itself changes with market dependence structure**.

The best current mechanistic picture is:

external opposition / lead-lag pressure  
→ internal fragility increases  
→ Handoff condition appears  
→ whether the Handoff should be trusted depends on a changing cross-asset dependence phase  
→ SELLR / competence evidence confirms the transition  
→ hysteresis prevents single noisy outcomes from immediately switching trust off.

This is the conceptual basis of DPTC.

---

## 12. Current research state and next decision

### Binding today

- **Retrospective clean champion:** HELIOS V5-DCE — 121/191 = 63.35% in clean 2026.
- **Prospective umbrella:** CLEAN_H3_PROSPECTIVE_V1.
- **Prospective baseline:** CLEAN_AURORA_H3_V1_PROSPECTIVE.
- **Prospective V5 status:** CLEAN_V5_DCE_H3_V1_PROSPECTIVE_SHADOW.
- **Reference combined retrospective system:** SAGE V2 + RuleFlow V3-TG — 126/191.
- **Temporally pre-frozen incremental competence evidence:** SELLR threshold selected on 2025, then 1/1 rescue in its 2026 stress.
- **Strongest development challenger:** DPTC-Q95 — 135/191 = 70.68%.
- **Prospective performance:** NOT YET ESTABLISHED; zero CLEAN prospective forecast/settlement rows at the evidence cutoff.

### Next work

The next phase is **not another unrestricted retrospective threshold search**.

Priority order:

1. run the frozen clean prospective pipeline on every valid future origin;
2. keep SAGE V2, RuleFlow V3-TG and both DPTC variants as separately identifiable shadow layers;
3. record MISS rather than backfill when source timing fails;
4. accumulate prospective action-level rescue/broken evidence;
5. compare probability quality, direction accuracy and balanced accuracy on identical origins;
6. promote only after a preregistered prospective evidence gate is met.

If new research is opened before enough prospective evidence accumulates, it must address a **new information/mechanism question**, not retune the consumed 2026 development period.

---

## 13. Canonical evidence index

### Target, clean data and base architecture

- GOLD_H3_CLEAN_CORE_RESULT_2026-10-03.md
- GOLD_H3_RECENT_CLEAN_SWEEP_RESULT_2026-10-03.md
- GOLD_H3_CLEAN_PROSPECTIVE_V1_FREEZE_2026-10-03.md
- GOLD_H3_DATA_INTEGRITY_GATE_V1_REPLAY_RESULT_2026-10-03.md
- GOLD_H3_IRIS_V1_RESULT_2026-10-02.md
- GOLD_H3_AURORA_V1_RESULT_2026-10-02.md

### Reversal architecture

- GOLD_H3_HELIOS_V5_DCE_RESULT_2026-10-03.md
- GOLD_H3_REMAINING53_SIGNAL_AUDIT_RESULT_2026-10-04.md
- GOLD_H3_SAGE_V1_CLOSURE_2026-10-04.md
- GOLD_H3_SAGE_V2_EXCEPTION_ONLY_PROSPECTIVE_FREEZE_2026-10-04.md
- GOLD_H3_RULEFLOW_V3_TOPOLOGY_DIAGNOSTIC_2026-10-04.md
- GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_DIAGNOSTIC_2026-10-04.md

### Competence transition

- GOLD_H3_HANDOFF_DISCRIMINATOR_AUDIT_RESULT_2026-10-04.md
- GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V4_HYSTERESIS_RESULT_2026-10-04.md
- GOLD_H3_BOCPD_HYSTERESIS_ADVERSARIAL_AUDIT_RESULT_2026-10-04.md
- GOLD_H3_COMPETENCE_TRANSITION_PROGRAM_V1_RESULT_2026-10-05.md
- GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_RESULT_2026-10-05.md
- GOLD_H3_DPTC_V1_DEVELOPMENT_FREEZE_2026-10-05.md
- GOLD_H3_DPTC_V1_RESULT_2026-10-05.md

### Latest diagnostic issuance

- GOLD_H3_OCT5_DIAGNOSTIC_NOWCAST_2026-10-05.json
- GOLD_H3_OCT5_DIAGNOSTIC_ALT_PRICES_2026-10-05.csv
- tools/gold_h3_oct5_diagnostic_nowcast.py

---

## 14. Change-control rules

1. This manifest summarizes decisions; detailed evidence remains in immutable Git history and dedicated result files.
2. Failed and blocked hypotheses are not deleted from the repository; they are compressed in this manifest to prevent repeated work.
3. A model/result must always retain its evidence class.
4. Consumed retrospective periods cannot be relabeled OOS after the fact.
5. Future model identities must declare:
   - data/source authority;
   - feature cutoff and issuance semantics;
   - selection period;
   - confirmation/transport period;
   - thresholds before opening the relevant holdout;
   - promotion and fail-safe rules.
6. Any result affected by a confirmed data-integrity correction must be rebuilt or explicitly marked as superseded.
7. Mainline performance comparisons must use the same target identity and the same eligible-origin universe.

---

## 15. Executive one-paragraph state

The Global-XAU short-horizon project began with a weak daily H3 signal that failed 2025-2026 transport. Replacing the classifier did not solve the problem. The first major improvement came from genuinely new hourly XAU path information through IRIS, followed by adaptive expert routing through SENTRY, DART and AURORA. Reversal specialists then evolved into HELIOS V5-DCE, the current **clean retrospective champion** at **63.35% accuracy / 63.76% balanced accuracy in 2026**. Rare SAGE and RuleFlow exceptions raise the retrospective reference to **65.97% / 66.31%**, after which the dominant residual error becomes missed reversal. Handoff research showed that reversal alarms are not uniformly trustworthy; their competence changes with the market's cross-asset dependence structure. SELLR, BOCPD, online expert aggregation and the label-free Gold-Nasdaq/VIX Dependence Phase independently support a transition around late April-May 2026. DPTC integrates these mechanisms and reaches **70.68% accuracy / 70.86% balanced accuracy** in post-hoc development, but this is not prospective proof. The project is now in the **prospective validation phase** under `CLEAN_H3_PROSPECTIVE_V1`: CLEAN AURORA is the formal baseline, CLEAN V5-DCE is a shadow challenger, and DPTC Q95/Q99 are frozen future shadow challengers.
