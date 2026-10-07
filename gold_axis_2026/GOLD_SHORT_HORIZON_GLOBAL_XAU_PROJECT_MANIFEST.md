# GOLD SHORT-HORIZON GLOBAL XAU — MASTER PROJECT MANIFEST

**Manifest version:** 3.4  
**Effective date:** 2026-10-05  
**Document class:** CANONICAL MASTER RESEARCH MANIFEST / DECISION AUTHORITY  
**Scope:** Global XAU/USD short-horizon H3 direction research  
**Evidence cutoff:** information committed through 2026-10-05  
**Audit status:** SOURCE-LEVEL CROSS-CHECK COMPLETE / PASS  
**Supersedes:** Manifest v3.0 and the prior long-form v2.0 narrative for current project-state interpretation

| Authority item | Current state |
|---|---|
| Primary target | XAU/USD H3 direction — next three retained Gold observation dates, UP/DOWN |
| Retrospective clean champion | **HELIOS V5-DCE** |
| Prospective umbrella | **CLEAN_H3_PROSPECTIVE_V1** |
| Prospective baseline | **CLEAN_AURORA_H3_V1_PROSPECTIVE** |
| Prospective V5 status | **CLEAN_V5_DCE_H3_V1_PROSPECTIVE_SHADOW** |
| Advanced competence challenger | **DPTC_H3_V1 Q95 + Q99 — frozen future shadow, post-hoc development** |
| Topology competence challenger | **TCG_V1 — strong-pro-risk gate over DPTC, post-hoc challenger** |
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

> At an origin-safe daily feature cutoff, predict whether XAU/USD will be UP or DOWN over the next three retained Gold observation dates.

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

### 2.0A Binding separation from the Global Session / Execution project — 2026-10-07

The H3 project remains a distinct canonical forecasting lane.

- **H3 target:** XAU/USD direction over the next **three retained Gold observation dates**.
- **Session target:** direction inside a specified intraday Asia / Europe / NY-London / US clock window.
- Session work recorded in `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` is an **execution / timing subproject**, not a replacement for H3.
- A session result must never be interpreted as H3 accuracy, and an H3 result must never be interpreted as session accuracy.
- Same-family specialist names are namespace-specific. For example, `H3_RIFT` / `H3_VEGA` belong here; `SESSION_RIFT` / `SESSION_VEGA` belong to the session project.
- A future combined H3→execution router would require its own preregistered contract; no current Session result silently changes the H3 champion, baseline, shadow hierarchy or target horizon.

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

### 4.5 Naming and supersession register

Several historical files use related or reused labels. The following interpretation is binding:

| Historical identity / artifact | Current interpretation |
|---|---|
| `AURORA_H3_V1_RESEARCH` / 2026-10-02 result | Historical pre-clean research result. Its original 2026 score is not the authoritative clean score after the confirmed 2026-02-27 data correction. |
| `CLEAN_AURORA_H3_V1_PROSPECTIVE` | Clean corrected prospective baseline under `CLEAN_H3_PROSPECTIVE_V1`. Clean retrospective comparison uses the rebuilt clean chain. |
| `GOLD_H3_HELIOS_V5_DCE_RESULT_2026-10-03.md` | Mechanism-lineage result produced before the final clean-family re-score. Its historical 2026 metric is superseded for clean performance ranking. |
| `GOLD_H3_RECENT_CLEAN_SWEEP_RESULT_2026-10-03.md` | **Authoritative clean retrospective ranking** for AURORA/HELIOS/OPAL family metrics after the validated source correction. |
| SAGE-H3 V1 — session-aware, 2026-10-02 | Earlier session-decomposition experiment; failed closed. It is **not** the parent of SAGE V2. |
| SAGE-H3 V1 — selective action / guarded exception, 2026-10-04 | Later reversal-intervention experiment. Its retained OCS exception is the parent mechanism of SAGE V2. |
| SAGE-H3 V2 exception-only | Prospective shadow successor to the **2026-10-04 selective-action SAGE lineage**, not to the earlier session-aware SAGE experiment. |
| 2026-10-02 diagnostic nowcast | Separate diagnostic bridge; not an eligible `CLEAN_H3_PROSPECTIVE_V1` origin. |

When an older result file conflicts numerically with the clean sweep, the clean sweep governs **clean retrospective performance**, while the older file remains valid as model-development lineage evidence.

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
| 2025 source-backfilled | 30 | 8 | 22 | 26.7% |
| 2026 | 28 | 16 | 12 | 57.1% |

The original pre-backfill direct Handoff state-machine experiment also failed its preregistered 2025 gate; its best zero-net grid candidate produced 3 rescue / 3 broken and no rule passed eligibility.

The later source-backfill reconstruction materially expanded observable 2025 Handoff history:

- reconstructed IFBC score begins 2025-01-29;
- reconstructed LLRS begins 2024-12-02;
- first complete extended Handoff state: **2025-03-03**;
- 2025 canonical Handoff alarms: **30**;
- rescue / broken: **8 / 22**.

Therefore:

**Handoff is not a deterministic reversal signal. Its competence is state-dependent and time-varying.**

This was the second major conceptual turning point of the project.

---

### Phase K — Methodologically distinct competence diagnostics

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

This supported the competence-shift hypothesis through a methodologically distinct mechanism from BOCPD.

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

### Source-backfilled 2025 transport diagnostic

The earlier DPTC 2025 formation result was based on an incomplete Handoff state window. On 2026-10-05 the missing 2025 IFBC/LLRS history was reconstructed under the original source/formula contract.

Source-reproduction QA:

- IFBC overlap: **280 rows**, maximum raw-feature discrepancy approximately **1.1e-16**;
- LLRS overlap: **332 rows**, maximum pressure/incremental discrepancy approximately **1.43e-14**;
- status: **SOURCE_REPRO_PASS**;
- first complete reconstructed Handoff state: **2025-03-03**.

The full 2025 combined V5 + frozen SAGE + RuleFlow reference is:

- **171/248 = 68.95%**;
- balanced accuracy **67.13%**.

DPTC on the reconstructed 2025 Handoff history:

| Variant | Actions | Rescue | Broken | Net | Accuracy | BA |
|---|---:|---:|---:|---:|---:|---:|
| Q95 | 9 | 4 | 5 | **-1** | 170/248 = **68.55%** | **67.17%** |
| Q99 | 8 | 3 | 5 | **-2** | 169/248 = **68.15%** | **66.65%** |

This **supersedes the earlier narrow 2025 formation-only “net 0” interpretation** for historical contribution assessment.

The contrast is now sharper:

- 2025 reconstructed: DPTC mildly harmful;
- 2026 development: DPTC strongly positive (+9 Q95 / +8 Q99).

This strengthens the interpretation of DPTC as a **regime/competence-conditioned controller**, not an always-on reversal layer.

The earlier 2023 source block was subsequently resolved with Databento CME futures history. Because Databento continuous-contract stitching is not byte-identical to Yahoo =F, the pre-2025 replay is governed as a **source-bridged historical reconstruction**, not exact Yahoo lineage.

Source-robust Databento replay used seven admissible fixed roll mappings without choosing the source by DPTC performance:

- 2023 Q95/Q99 net contribution ranged **-1 to +1** across source mappings; 6/7 mappings were +1 and one was -1. Interpretation: weak / source-sensitive.
- 2024 Q95/Q99 net contribution ranged **-3 to -2**; all 7/7 mappings were negative. Interpretation: robust historical failure.
- Adding the already-frozen pre-2025 RuleFlow calls did not change the sign pattern.
- SAGE was not backcast into 2023-2024 because its current frozen source contract did not exist there.

A subsequent mechanism diagnostic found that generic structural-anomaly intensity did not explain DPTC competence. The more specific **strong-pro-risk topology** did:

- Gold-Nasdaq dependence positive;
- Gold-VIX dependence negative;
- frozen significance condition satisfied.

A label-free multiview structural change-point was located at **2026-03-16** (block-permutation p = **0.0175**), while the established dependence-phase onset remained **2026-04-30**. This supports a two-stage interpretation: structural transition first, then a more stable competence-bearing topology.

The 70.68% DPTC-Q95 result is therefore **not the proven prospective accuracy of the project**.

DPTC is frozen for future shadow evaluation.

---

### Phase N — Topology Competence Gate V1 (TCG-V1)

The competence diagnosis was converted into a deliberately simple label-free gate over DPTC.

**Primary frozen challenger rule:**

> Allow a DPTC flip only when the already-defined `strong_pro_risk` topology is TRUE.

This rule was not numerically optimized on RESCUE/BROKEN outcomes. It uses the previously frozen dependence-state definition.

Historical action audit:

| Year | Ungated DPTC Q95 | TCG-V1 gated |
|---|---:|---:|
| 2023 | 6 rescue / 5 broken = **+1** | 0 actions = **0** |
| 2024 | 2 / 4 = **-2** | 0 actions = **0** |
| 2025 | 4 / 5 = **-1** | 2 / 1 = **+1** |
| 2026 | 11 / 2 = **+9** | 9 / 2 = **+7** |

Across the harmonized 2023-2026 action sample:

- ungated DPTC: 39 actions, 23 rescue / 16 broken, net **+7**, action precision 59.0%;
- TCG-V1: 14 actions, 11 rescue / 3 broken, net **+8**, action precision **78.6%**;
- RESCUE odds inside the primary gate versus rejected actions: **3.97x**, Fisher exact p = **0.0930**.

Exact Yahoo-lineage 2025-2026 projection under the primary gate:

- 2025: baseline 171/248 -> **172/248 = 69.35%**;
- 2026: baseline 126/191 -> **133/191 = 69.63%**;
- combined: 297/439 -> **305/439 = 69.48%**.

A sensitivity-only oil-decoupling gate was also tested:

> strong-pro-risk AND corr(Gold, WTI/CL) < 0.

It produced 12 actions, 10 rescue / 2 broken, net **+8**, precision **83.3%**. This oil condition is **not binding** because its apparent usefulness was discovered during consumed retrospective diagnosis. It remains a challenger/sensitivity signal only.

**Scientific status:** POST-HOC TOPOLOGY-GATE CHALLENGER. It must be prospectively shadow-tested before promotion.

---

## 6. Current performance hierarchy

The following table is the correct way to quote the project as of 2026-10-05.

| Layer / system | 2026 result | BA | Evidence status | Interpretation |
|---|---:|---:|---|---|
| Clean AURORA | 58.64% | 59.02% | retrospective clean baseline | adaptive base router |
| Clean HELIOS V5-DCE | **121/191 = 63.35%** | **63.76%** | authoritative clean retrospective champion | retrospective champion; prospective V5 shadow |
| SAGE V2 exception-only | **125/191 = 65.45%** | 65.81% | retrospective development; frozen shadow | rare OCS exception |
| SAGE V2 + RuleFlow V3-TG | **126/191 = 65.97%** | **66.31%** | retrospective combined reference | competence-research baseline |
| Direct frozen SELLR trigger on canonical Handoff | **127/191 = 66.49%** | **66.81%** | threshold selected on 2025 before 2026 stress; exactly one 2026 fire (2026-05-21) | temporally pre-frozen incremental evidence |
| BOCPD V4 | 132/191 = **69.11%** | 69.36% | post-hoc development | robust competence-state diagnostic |
| STCR — SELLR-triggered persistent competence state | 133/191 = **69.63%** | 69.86% | post-hoc synthesis | competence-transition challenger |
| TCG-V1 over DPTC-Q95 | **133/191 = 69.63%** | not separately re-scored here | post-hoc topology-gate challenger | sacrifices some 2026 gain to suppress 2024/2025 harm |
| DPTC-Q99 | 134/191 = **70.16%** | 70.36% | post-hoc development challenger | strict shadow variant |
| DPTC-Q95 | **135/191 = 70.68%** | **70.86%** | post-hoc development challenger | strongest development result |

### 6.1 What may and may not be claimed

May be claimed:

- Clean HELIOS V5-DCE achieved 63.35% accuracy on the clean 2026 retrospective universe.
- The retrospective SAGE + RuleFlow reference reached 65.97%.
- The pre-2026-frozen SELLR threshold fired exactly once on a canonical 2026 Handoff origin (2026-05-21); that FLIP rescued a baseline error.
- Multiple methodologically distinct analyses converge on a competence transition around late April-May 2026.
- DPTC reached 70.68% in post-hoc development and has been frozen for future shadow testing.
- TCG-V1 reduced historical DPTC action count while removing the robust 2024 loss and changing 2025 from net -1 to net +1; this remains post-hoc challenger evidence.

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
| SAGE-H3 V1 (session-aware, 2026-10-02) | No eligible pre-2023 representation | Closed; distinct from the later selective-action SAGE lineage. |
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
| Direct Handoff state machine | Best zero-net 2025 grid candidate: 3 rescue / 3 broken; **no rule passed eligibility** | Handoff is not a deterministic FLIP signal. |
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

### Layer 6 — Topology competence gate

**TCG-V1**

- permits DPTC intervention only inside the frozen strong-pro-risk topology;
- primary rule uses Gold-Nasdaq positive / Gold-VIX negative dependence with the existing significance condition;
- suppresses DPTC in 2023-2024 source-robust backcast and retains selective 2025-2026 actions;
- oil-decoupling is sensitivity telemetry only, not part of the binding V1 rule.

TCG-V1 is a **post-hoc shadow challenger**, not a promoted authority.

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

### 9.5 TCG-V1 governance

TCG-V1 is frozen as a separate topology-gated DPTC shadow challenger.

Binding V1 rule:

- DPTC action eligible only when `strong_pro_risk == TRUE` under the existing label-free dependence definition.

The following are **not** binding V1 additions:

- Gold-oil negative-correlation filter;
- persistence >= 3 origins;
- any retrospective threshold chosen to maximize rescue precision.

These remain sensitivity hypotheses. TCG-V1 must accumulate genuinely prospective action-level evidence before any promotion decision.

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
→ hysteresis prevents single noisy outcomes from immediately switching trust off  
→ TCG-V1 asks whether the competence-bearing strong-pro-risk topology is actually present before allowing the DPTC intervention.

The mechanism diagnostic suggests that generic structural shock intensity is insufficient. The relevant state is more specific: a changed cross-asset topology, especially Gold-Nasdaq positive and Gold-VIX negative dependence. Gold-WTI decoupling is a promising but non-binding secondary diagnostic.

This is the conceptual basis of DPTC + TCG-V1.

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
- **Topology competence challenger:** TCG-V1 over DPTC-Q95 — 2026 projected 133/191 = 69.63%, while suppressing the robust 2024 historical loss and changing 2025 net contribution from -1 to +1.
- **Prospective performance:** NOT YET ESTABLISHED; zero CLEAN prospective forecast/settlement rows at the evidence cutoff.

### Historical contribution audit completed

A source-level historical contribution audit was completed and then strengthened with a validated 2025 source backfill on 2026-10-05.

Key findings:

- RuleFlow V3-TG is **not** an unconditional improvement: its fixed-rule backcast produced net **-1** in 2023 and net **-1** in 2024.
- SAGE V2 exception-only adds **+1 net correct call in 2025** and **+4 in 2026** on its available exact source coverage.
- The full reconstructed 2025 V5 + SAGE + RuleFlow reference is **171/248 = 68.95%**, BA **67.13%**.
- After the missing 2025 Handoff state is reconstructed, ungated DPTC is harmful in 2025: Q95 **-1 net**, Q99 **-2 net**.
- Databento resolved the earlier pre-2025 source block. Source-robust replay shows 2023 is weak/source-sensitive (**-1..+1**) while 2024 is robustly negative across all seven mappings (**-3..-2**).
- In contrast, 2026 ungated development is strongly positive: Q95 **+9**, Q99 **+8**.
- Mechanism diagnosis found a label-free multiview structural break near **2026-03-16** and dependence-phase onset **2026-04-30**.
- TCG-V1, using the frozen strong-pro-risk topology as a gate, yields historical net contribution **0 (2023), 0 (2024), +1 (2025), +7 (2026)** in the harmonized Q95 action audit.
- The oil-decoupling condition improves retrospective selectivity in sensitivity analysis but is not part of the binding TCG-V1 rule.
- The evidence therefore supports a **topology/competence-conditioned controller interpretation**, not an always-on reversal rule.

Authorities:
- `GOLD_H3_LATEST_MODELS_HISTORICAL_CONTRIBUTION_AUDIT_2026-10-05.md`
- `GOLD_H3_2025_BACKFILL_DPTC_RESULT_2026-10-05.md`
- `GOLD_H3_DPTC_2023_2024_DATABENTO_SOURCE_ROBUST_REPLAY_2026-10-05.md`
- `GOLD_H3_DPTC_COMPETENCE_MECHANISM_DIAGNOSTIC_V1_2026-10-05.md`
- `GOLD_H3_TOPOLOGY_COMPETENCE_GATE_V1_2026-10-05.md`

### Next work

The next phase is **not another unrestricted retrospective threshold search**.

Priority order:

1. run the frozen clean prospective pipeline on every valid future origin;
2. keep SAGE V2, RuleFlow V3-TG, both ungated DPTC variants and TCG-V1 as separately identifiable shadow layers;
3. preserve the completed 2023-2026 historical/source-robust contribution audit as negative/positive transport evidence;
4. record MISS rather than backfill when source timing fails;
5. accumulate prospective action-level rescue/broken evidence;
6. compare probability quality, direction accuracy and balanced accuracy on identical origins;
7. compare TCG-V1 against ungated DPTC on exactly the same future Handoff opportunities;
8. keep the oil-decoupling condition as non-binding telemetry unless a separately preregistered future version is opened;
9. promote only after a preregistered prospective evidence gate is met.

If new research is opened before enough prospective evidence accumulates, it must address a **new information/mechanism question**, not retune the consumed 2026 development period.

---

## 13. Daily Action Layer — CIG-D1 Consensus Integrity Gate (2026-10-05)

**Identity:** `CIG_D1_V1`  
**Status:** `RETROSPECTIVE_SELECTIVE_D1_CHALLENGER`  
**Purpose:** convert the existing H3 expert architecture into a same-day daily action layer without changing the original H3 target or forcing every H3 expert to become a standalone D1 model.

### 13.1 Problem reformulation

The original H3 task remains:

> next 3-business-day net XAU direction.

The new operational question is different:

> using only the H3 state available at issuance, what should be done for the current trading day?

Therefore the daily layer is scored against the **same-day XAU direction**, while all H3 models keep their original frozen identities.

Binding action convention:
- D1 UP -> **LONG**
- D1 DOWN -> **OUT / CASH**
- unresolved -> **UNCERTAIN / no new D1 position**

### 13.2 Direct model-by-model D1 diagnostic

Common 2026-01-02 through 2026-07-31 daily window, N=145:

| H3-derived daily signal | Correct | D1 accuracy |
|---|---:|---:|
| **SAGE V2 + RuleFlow V3-TG** | **103/145** | **71.03%** |
| HELIOS V5-DCE | 102/145 | 70.34% |
| RIFT | 102/145 | 70.34% |
| VEGA | 102/145 | 70.34% |
| RC-RTE V2 | 102/145 | 70.34% |
| DPTC-Q95 | 98/145 | 67.59% |

This established a critical distinction:

**best H3 model != best same-day action model.**

DPTC-Q95 can improve the 3-day terminal direction while acting too early for the current day. DPTC is therefore not used as the binding D1 direction engine.

### 13.3 CIG-D1 expert set

The binding CIG-D1 V1 state uses:
1. **SAGE V2 + RuleFlow V3-TG**
2. **HELIOS V5-DCE**
3. **RIFT**
4. **VEGA**

These mechanisms are not claimed to be statistically independent. They are used because they expose materially different continuation/reversal states inside the H3 architecture.

RC-RTE V2 is not counted as an additional equal vote in the 2026 Jan-Jul D1 consensus because it adds insufficient independent daily variation relative to V5 on the common window.

DPTC / BOCPD / SELLR / OPAL / dependence-phase states remain telemetry and challenger context, not binding equal-vote CIG-D1 inputs.

### 13.4 Binding consensus rule

- 4/4 UP -> **HIGH-CONFIDENCE D1 UP -> LONG**
- 4/4 DOWN -> **HIGH-CONFIDENCE D1 DOWN -> OUT/CASH**
- any disagreement -> **UNCERTAIN**

No majority override is allowed in V1.

2026 Jan-Jul:

| State | N | Correct | Accuracy |
|---|---:|---:|---:|
| **4/4 consensus** | **125** | **93** | **74.40%** |
| **disagreement** | **20** | **10** | **50.00%** |

Selective coverage:

**125 / 145 = 86.21%**

The gain therefore comes from abstaining when expert integrity breaks, not from adding more votes.

### 13.5 Historical transport

The exact current SAGE source contract cannot be reconstructed identically for all early years. Historical transport is therefore separated to avoid inventing a synthetic SAGE history.

Common-core proxy, V5 + RIFT + VEGA:

| Year | Consensus N | Correct | Accuracy | Coverage |
|---|---:|---:|---:|---:|
| 2023 | 206 | 169 | **82.04%** | 94.1% |
| 2024 | 220 | 178 | **80.91%** | 91.7% |

Current enhanced CIG-D1 architecture:

| Year | Consensus N | Correct | Accuracy | Coverage |
|---|---:|---:|---:|---:|
| 2025 | 218 | 176 | **80.73%** | 87.9% |
| 2026 Jan-Jul | 125 | 93 | **74.40%** | 86.2% |

Interpretation:
- the consensus effect predates 2026;
- absolute performance weakens in 2026;
- consensus remains materially stronger than disagreement;
- the architecture is a **selective predictor**, not an unconditional D1 classifier.

### 13.6 Resolver research — rejected

The following attempts were explicitly tested and rejected as binding extensions:

- **majority voting:** 102/145 = 70.34% on 2026 Jan-Jul; below SAGE+RuleFlow and below selective consensus;
- **static vote-pattern lookup:** failed transport;
- **rolling best-expert / recent competence selector:** unstable across years;
- **supervised KEEP/FLIP residual classifier:** DR-Selective 12/16 = 75.0% in 2025 but 6/15 = 40.0% in 2026; DR-Full 27/39 = 69.2% in 2025 but 9/18 = 50.0% in 2026;
- **label-free dependence / transition state as direct direction override:** useful as regime telemetry, not as a stable D1 direction rule;
- **recency-weighted Pattern Regime Memory:** no tested configuration increased coverage without reducing the binding 2025 consensus accuracy.

Scientific conclusion:

**disagreement itself is the observable uncertainty state.**

The correct formulation is not:
`all days -> forced UP/DOWN`

but:
`H3 expert state -> trustworthy D1 direction OR abstain`.

### 13.7 Remaining research problem

CIG-D1 already covers about 86% of the 2026 Jan-Jul D1 universe. The unresolved research space is the approximately 14% UNCERTAIN subset.

Any rescue layer must add **orthogonal information**, not another recombination of the same H3 states. Preferred candidates:
- H1 / intraday path;
- overnight move;
- opening-state momentum/reversal;
- intraday volatility and deceleration;
- event proximity / event-time reaction;
- origin-safe cross-asset state.

This future component must be a separately frozen **D1 Rescue Head** with ABSTAIN preserved when evidence is weak.

### 13.8 2026-10-05 diagnostic note

For feature cutoff 2026-10-02 and planned issue 2026-10-05, the diagnostic-nowcast audit currently shows:
- AURORA DOWN, p_up 0.30075;
- V5-DCE DOWN, p_up 0.30075;
- RIFT DOWN, reversal probability 0.55628, no override;
- VEGA DOWN, reversal probability 0.46319, no override.

This is **diagnostic-nowcast**, not clean prospective proof. A completed CIG-D1 4/4 record requires the same-origin SAGE+RuleFlow state to be available under the frozen source/timing contract.

### 13.9 Evidence and governance

Detailed authority:
- `GOLD_D1_CIG_V1_RESULT_2026-10-05.md`

CIG-D1 V1 may be used for:
- retrospective D1 diagnostics;
- future frozen shadow evaluation;
- LONG / OUT / UNCERTAIN reporting under the exact rule above.

It may not be used to:
- relabel retrospective evidence as prospective;
- tune membership/thresholds on 2026 outcomes and call the result OOS;
- force an action on UNCERTAIN days without a separately named rescue identity;
- silently mix target clocks or price sources.


### 13.10 CIG-D1 2026-09-28 through 2026-10-02 diagnostic extension

A source-refresh extension was replayed for five additional D1 issue dates after the archived mature H3 files ended on 2026-09-25.

Reconstructed origin/issue pairs:
- 2026-09-25 -> 2026-09-28
- 2026-09-28 -> 2026-09-29
- 2026-09-29 -> 2026-09-30
- 2026-09-30 -> 2026-10-01
- 2026-10-01 -> 2026-10-02

Frozen-model reproduction check:
- HELIOS V5-DCE historical full-chain max absolute reproduction difference = **5.551e-17**, effectively exact.

Daily extension result:

| Issue | Actual D1 | SAGE+RF | V5 | RIFT | VEGA | CIG |
|---|---|---|---|---|---|---|
| 2026-09-28 | DOWN | UP | UP | UP | UP | UP — wrong |
| 2026-09-29 | DOWN | UP | UP | DOWN | DOWN | UNCERTAIN |
| 2026-09-30 | UP | UP | UP | UP | UP | UP — correct |
| 2026-10-01 | UP | DOWN | DOWN | DOWN | DOWN | DOWN — wrong |
| 2026-10-02 | DOWN | UP | UP | UP | UP | UP — wrong |

Extension totals:
- D1 days: **5**
- 4/4 consensus days: **4**
- correct consensus: **1/4 = 25.00%**
- coverage: **4/5 = 80.00%**
- UNCERTAIN: **1/5**

Critical interpretation:
- this late-September / early-October pocket is a **clear local failure regime** for the CIG consensus;
- three of four unanimous calls are wrong, so unanimity by itself is not sufficient under this transition state;
- the 2026-09-29 issue is correctly rejected as UNCERTAIN because V5/SAGE disagree with RIFT/VEGA.

Governance:
- the extension is **retrospective diagnostic evidence**, not prospective OOS;
- SAGE V2 frozen IFBC/LLRS snapshots end on 2026-09-24. Under the frozen missing-source rule, post-snapshot SAGE exceptions fail closed to **KEEP V5**;
- RuleFlow V3-TG has no same-origin frozen post-snapshot source record here, so no retrospective RuleFlow flip was invented;
- therefore these five rows are suitable for diagnosing the late-September/early-October failure pocket, but they are not equivalent to a fully reconstructed prospective SAGE/RuleFlow source state.

Authority:
- `GOLD_D1_CIG_V1_SEP28_OCT2_EXTENSION_2026-10-05.md`
- `GOLD_D1_CIG_V1_SEP28_OCT2_EXTENSION_2026-10-05.csv`
- `GOLD_D1_CIG_V1_SEP28_OCT2_EXTENSION_2026-10-05.json`

---

## 14. Canonical evidence index

### Target, clean data and base architecture

- GOLD_H3_CLEAN_CORE_RESULT_2026-10-03.md
- GOLD_H3_RECENT_CLEAN_SWEEP_RESULT_2026-10-03.md
- GOLD_H3_CLEAN_PROSPECTIVE_V1_FREEZE_2026-10-03.md
- GOLD_H3_DATA_INTEGRITY_GATE_V1_REPLAY_RESULT_2026-10-03.md
- GOLD_H3_IRIS_V1_RESULT_2026-10-02.md
- GOLD_H3_IRIS_RETURN_V1_RESULT_2026-10-02.md
- GOLD_H3_SENTRY_V1_RESULT_2026-10-02.md
- GOLD_H3_DART_V1_RESULT_2026-10-02.md
- GOLD_H3_AURORA_V1_RESULT_2026-10-02.md

### Reversal architecture

- GOLD_H3_HELIOS_V5_DCE_RESULT_2026-10-03.md
- GOLD_H3_MULTI_SPECIALIST_PHASE1_9_CLOSURE_2026-10-03.md
- GOLD_H3_RTE_V1_V4_CLOSURE_2026-10-03.md
- GOLD_H3_RC_RTE_V1_V2_CLOSURE_2026-10-04.md
- GOLD_H3_FRS_V1_CLOSURE_2026-10-04.md
- GOLD_H3_TRES_V1_V2_CLOSURE_2026-10-04.md
- GOLD_H3_REMAINING53_SIGNAL_AUDIT_RESULT_2026-10-04.md
- GOLD_H3_HANDOFF_STATE_MACHINE_V1_RESULT_2026-10-04.md
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
- GOLD_H3_LATEST_MODELS_HISTORICAL_CONTRIBUTION_AUDIT_2026-10-05.md
- GOLD_H3_2025_BACKFILL_DPTC_RESULT_2026-10-05.md
- GOLD_H3_2025_BACKFILL_DPTC_SUMMARY_2026-10-05.json
- GOLD_H3_HOURLY_HISTORY_DEPTH_PROBE_2026-10-05.md
- GOLD_H3_2023_TWELVE_FUTURES_BRIDGE_PROBE_2026-10-05.md
- GOLD_H3_2023_SOURCE_RECOVERY_AUDIT_2026-10-05.md
- GOLD_H3_DATABENTO_YAHOO_SOURCE_BRIDGE_V2_2026-10-05.md
- GOLD_H3_DPTC_2023_2024_DATABENTO_SOURCE_ROBUST_REPLAY_2026-10-05.md
- GOLD_H3_DPTC_COMPETENCE_MECHANISM_DIAGNOSTIC_V1_2026-10-05.md
- GOLD_H3_TOPOLOGY_COMPETENCE_GATE_V1_2026-10-05.md

### Daily action / CIG-D1

- GOLD_D1_CIG_V1_RESULT_2026-10-05.md
- GOLD_D1_CIG_V1_SEP28_OCT2_EXTENSION_2026-10-05.md
- GOLD_D1_CIG_V1_SEP28_OCT2_EXTENSION_2026-10-05.csv
- GOLD_D1_CIG_V1_SEP28_OCT2_EXTENSION_2026-10-05.json

### Latest diagnostic issuance

- GOLD_H3_OCT5_DIAGNOSTIC_NOWCAST_2026-10-05.json
- GOLD_H3_OCT5_DIAGNOSTIC_ALT_PRICES_2026-10-05.csv
- tools/gold_h3_oct5_diagnostic_nowcast.py

---

## 15. Change-control rules

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

## 16. Executive one-paragraph state

The Global-XAU short-horizon project now also contains a separate **CIG-D1 selective daily-action layer**: SAGE+RuleFlow, V5-DCE, RIFT and VEGA must agree 4/4 for a binding D1 direction; otherwise the output is UNCERTAIN. In 2026 Jan-Jul this covers 125/145 days (86.21%) at 93/125 = 74.40% same-day accuracy, while disagreement days are 10/20 = 50.00%. The Global-XAU short-horizon project began with a weak daily H3 signal that failed 2025-2026 transport. Replacing the classifier did not solve the problem. The first major improvement came from genuinely new hourly XAU path information through IRIS, followed by adaptive expert routing through SENTRY, DART and AURORA. Reversal specialists then evolved into HELIOS V5-DCE, the current **clean retrospective champion** at **63.35% accuracy / 63.76% balanced accuracy in 2026**. Rare SAGE and RuleFlow exceptions raise the retrospective reference to **65.97% / 66.31%**, after which the dominant residual error becomes missed reversal. Handoff research showed that reversal alarms are not uniformly trustworthy; their competence changes with the market's cross-asset dependence structure. SELLR, BOCPD, online expert aggregation and the label-free Gold-Nasdaq/VIX Dependence Phase provide methodologically distinct evidence converging on a transition around late April-May 2026. DPTC integrates these mechanisms and reaches **70.68% accuracy / 70.86% balanced accuracy** in post-hoc development, but this is not prospective proof. The project is now in the **prospective validation phase** under `CLEAN_H3_PROSPECTIVE_V1`: CLEAN AURORA is the formal baseline, CLEAN V5-DCE is a shadow challenger, and DPTC Q95/Q99 are frozen future shadow challengers.
