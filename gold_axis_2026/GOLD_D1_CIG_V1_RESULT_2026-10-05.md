# GOLD D1 — CIG-D1 CONSENSUS INTEGRITY GATE RESULT

**Date:** 2026-10-05  
**Identity:** `CIG_D1_V1`  
**Purpose:** convert the existing H3 expert architecture into a same-day daily action signal without forcing every H3 model to become a standalone D1 predictor.  
**Evidence class:** retrospective diagnostic / development evidence. **Not independent prospective OOS proof.**

---

## 1. Research question

The operational question is not the original H3 target:

> "What is the net XAU direction over the next three business days?"

The D1 action question is:

> "Given only information available when the H3 forecast is issued, what action should be taken for the current trading day?"

The daily layer therefore evaluates the H3 expert state against the **same-day XAU direction**. It does not relabel the original H3 target, and it does not alter the frozen H3 models.

For the 2026 Jan-Jul diagnostic, the same daily XAU realization series used in the prior daily-action work is retained. Direction is defined from previous available close to the current daily close.

Operational mapping:
- D1 UP -> LONG;
- D1 DOWN -> OUT / CASH for the gold-investment use case;
- UNCERTAIN -> no new position / separate rescue path.

Symmetric LONG/SHORT results may be used only as diagnostics; they are not the binding action convention.

---

## 2. Why the project moved to consensus rather than a new full-day classifier

A first benchmark applied each H3 model's currently available direction directly to the current day.

On the common 2026-01-02 through 2026-07-31 window, N=145 daily observations:

| H3-derived daily signal | Correct | D1 accuracy |
|---|---:|---:|
| SAGE V2 + RuleFlow V3-TG | 103/145 | **71.03%** |
| HELIOS V5-DCE | 102/145 | **70.34%** |
| RIFT | 102/145 | **70.34%** |
| VEGA | 102/145 | **70.34%** |
| RC-RTE V2 | 102/145 | **70.34%** |
| DPTC-Q95 | 98/145 | **67.59%** |

The key diagnostic was that the best H3 system was **not** the best same-day system. DPTC-Q95 is stronger on the H3 target, but some of its reversal interventions are intentionally early relative to the current day. This makes it unsuitable as a forced D1 direction engine.

This motivated a different formulation: use the H3 architecture as a **sensor array**, and estimate whether its current daily direction is trustworthy.

---

## 3. Independent expert set

The final D1 consensus uses four expert states:

1. **SAGE V2 + RuleFlow V3-TG** — exception-aware H3 direction;
2. **HELIOS V5-DCE** — clean H3 continuation/reversal architecture;
3. **RIFT** — learned reversal specialist;
4. **VEGA** — volatility-expectations reversal specialist.

These are not treated as four statistically independent models in a formal probabilistic sense. The purpose is narrower: expose materially different mechanism states inside the existing H3 architecture.

RC-RTE V2 is **not** counted as an additional vote in the 2026 Jan-Jul D1 consensus because, on the common daily evaluation window, it does not add independent same-day variation relative to V5 sufficient to justify an extra vote.

DPTC, BOCPD, SELLR, OPAL and dependence-state variables remain useful telemetry and research context, but are not binding equal-vote D1 inputs in CIG-D1 V1.

### 3.1 How DPTC / TCG-V1 should be used alongside the consensus

The H3 and D1 layers solve different problems and must not be mixed.

**CIG-D1 answers:**  
> What should be done for the current trading day?

**DPTC + TCG-V1 answers:**  
> When the H3 architecture wants to reverse the baseline H3 direction, is that reversal specialist currently trustworthy enough to act?

Current usage rule:

1. **For same-day action:** use CIG-D1 first.
   - 4/4 UP -> LONG.
   - 4/4 DOWN -> OUT / CASH.
   - disagreement -> UNCERTAIN.

2. **For H3 reversal intervention:** do not use ungated DPTC automatically.
   - DPTC may propose a FLIP.
   - TCG-V1 must first confirm the frozen strong-pro-risk topology.
   - The topology means Gold-Nasdaq dependence is positive and Gold-VIX dependence is negative under the frozen significance rule.
   - If TCG-V1 is FALSE, keep the H3 baseline; do not permit the DPTC FLIP.
   - If TCG-V1 is TRUE, the DPTC FLIP is eligible as a shadow/challenger action.

Historical reason for this restriction:

| Year | Ungated DPTC Q95 | TCG-V1 gated |
|---|---:|---:|
| 2023 | +1 net | 0 |
| 2024 | -2 net | 0 |
| 2025 | -1 net | +1 |
| 2026 | +9 net | +7 |

Thus TCG-V1 sacrifices some 2026 gain but removes the robust 2024 loss and changes 2025 from negative to positive.

Across the harmonized 2023-2026 action sample:

- ungated DPTC: 39 actions, 23 rescue / 16 broken, net +7;
- TCG-V1: 14 actions, 11 rescue / 3 broken, net +8;
- TCG-V1 action precision: **78.6%**.

**WTI / oil role:** Gold-oil negative correlation is promising as an additional confidence filter, but it is not part of the binding V1 rule. In retrospective sensitivity analysis, requiring strong-pro-risk plus negative Gold-WTI/CL correlation reduced the sample to 12 actions and produced 10 rescue / 2 broken = **83.3%** precision, while leaving 2025-2026 total accuracy unchanged at **305/439 = 69.48%**. Oil must therefore be recorded as telemetry / challenger evidence, not as a mandatory production filter.

Operational summary:

> **Daily decision = CIG-D1 consensus.**  
> **H3 reversal permission = DPTC filtered by TCG-V1.**  
> **Oil = secondary confidence telemetry only.**

---

## 4. 2026 consensus result

Using:
- SAGE+RuleFlow,
- V5-DCE,
- RIFT,
- VEGA,

the rule is:

- if all four indicate UP -> D1 UP;
- if all four indicate DOWN -> D1 DOWN;
- otherwise -> UNCERTAIN.

2026 Jan-Jul result:

| State | N | Correct | Accuracy |
|---|---:|---:|---:|
| **4/4 consensus** | **125** | **93** | **74.40%** |
| **disagreement** | **20** | **10** | **50.00%** |
| all days, SAGE+RuleFlow forced | 145 | 103 | 71.03% |

Coverage of the selective consensus layer:

**125 / 145 = 86.21%**

Therefore the gain does not come from majority voting. It comes from **abstaining when the expert structure loses integrity**.

The 20 disagreement days are empirically close to chance for a forced daily direction. They are therefore treated as an observable uncertainty state rather than as ordinary low-confidence forecasts.

---

## 5. Historical transport evidence

The exact current SAGE data contract cannot be reconstructed identically for all older years. To avoid fabricating a historical SAGE signal, transport is separated into:

### 5.1 Common-core transport proxy — V5 + RIFT + VEGA

| Year | Consensus N | Correct | Consensus accuracy | Coverage |
|---|---:|---:|---:|---:|
| 2023 | 206 | 169 | **82.04%** | 94.1% |
| 2024 | 220 | 178 | **80.91%** | 91.7% |

### 5.2 Current enhanced CIG-D1 architecture

| Year | Consensus N | Correct | Consensus accuracy | Coverage |
|---|---:|---:|---:|---:|
| 2025 | 218 | 176 | **80.73%** | 87.9% |
| 2026 Jan-Jul | 125 | 93 | **74.40%** | 86.2% |

Interpretation:
- consensus strength predates 2026;
- the absolute hit rate weakens in 2026;
- the separation between consensus and disagreement remains operationally meaningful;
- the evidence supports selective prediction, not an unconditional daily direction claim.

These results are still retrospective research evidence because the CIG-D1 architecture itself was formulated after reviewing the development history.

---

## 6. Resolver experiments that were rejected

The project explicitly tested whether the UNCERTAIN region could be recovered without sacrificing robustness.

### 6.1 Majority voting

Five-model majority on the 2026 Jan-Jul daily window:

**102/145 = 70.34%**

This is below SAGE+RuleFlow alone and below selective consensus. Majority voting is rejected.

### 6.2 Static disagreement-pattern lookup

A rule mapping historical expert bit-patterns to future D1 direction did not transport:
- 2025 resolved examples: **5/11 = 45.45%**;
- 2026 resolved examples: **3/8 = 37.50%** in the tested frozen mapping.

Rejected.

### 6.3 Rolling best-expert / competence selector

Selecting the recent best-performing expert on disagreement days was unstable across years. Representative 60-day competence selection deteriorated from useful 2024 behavior to approximately chance in 2025 and materially below chance in the 2026 disagreement sample.

Rejected as a binding resolver.

### 6.4 Supervised KEEP/FLIP residual classifier

The resolver target was reformulated as:

> KEEP V5 or FLIP V5 on disagreement days?

Two frozen candidates were tested.

**DR-Selective**
- train 2022-2024 -> 2025: 12/16 = **75.0%**
- retrain through 2025 -> 2026 Jan-Jul: 6/15 = **40.0%**

**DR-Full**
- train 2022-2024 -> 2025: 27/39 = **69.2%**
- retrain through 2025 -> 2026 Jan-Jul: 9/18 = **50.0%**

The mapping is non-stationary. The 2025 success does not transport to 2026.

Rejected.

### 6.5 Label-free transition/dependence state used as a direct direction override

The existing Gold-Nasdaq / Gold-VIX dependence-phase machinery was tested as a state descriptor. It is useful as a **regime/transition alarm**, but it does not provide a stable direct KEEP/FLIP decision for the D1 disagreement subset.

Retain as telemetry; reject as direct D1 direction override.

### 6.6 Recency-weighted Pattern Regime Memory

A dynamic pattern memory was tested to allow the meaning of an expert-vote pattern to change through time. Some local pockets were useful, but under the binding requirement:

> increase coverage without reducing 2025 consensus accuracy,

no acceptable parameterization survived.

Rejected as a binding CIG-D1 V1 extension.

---

## 7. Scientific interpretation

The main finding is not that four models voting together mechanically creates alpha.

The stronger interpretation is:

> **expert disagreement is an observable uncertainty regime.**

When the H3 expert architecture is internally coherent, its state contains useful same-day directional information. When the architecture fragments, forcing an H3-derived daily call removes that edge.

This changes the modelling problem from:

`all days -> forced UP/DOWN classifier`

to:

`H3 expert state -> trustworthy daily direction OR abstain`

This is a selective-prediction formulation.

---

## 8. Binding CIG-D1 V1 rule

**Identity:** `CIG_D1_V1`

Inputs:
- SAGE V2 + RuleFlow V3-TG direction;
- HELIOS V5-DCE direction;
- RIFT direction;
- VEGA direction.

Decision:

### HIGH-CONFIDENCE UP
All four = UP.

Operational action:
**LONG**

### HIGH-CONFIDENCE DOWN
All four = DOWN.

Operational action:
**OUT / CASH**

### UNCERTAIN
Any disagreement among the four.

Operational action:
**no new D1 position from CIG-D1 alone**.

No majority override.
No DPTC override.
No pattern-memory override.
No rolling-competence override.
No retrospective rescue rule.

---

## 9. Remaining research problem

CIG-D1 already covers approximately 86% of the 2026 Jan-Jul daily universe.

The remaining problem is deliberately restricted to the UNCERTAIN subset.

The next legitimate research lane is therefore an **orthogonal D1 Rescue Head** using information not already encoded by the H3 expert stack, especially:
- H1 / intraday path;
- overnight move;
- opening-state momentum and reversal;
- intraday volatility/deceleration;
- event proximity and event-time reaction;
- origin-safe cross-asset state.

The rescue head must be trained and selected on pre-test periods and must retain ABSTAIN when evidence is insufficient.

The project should not continue recombining the same H3 states with increasingly complex meta-models; that path has already failed transport tests.

---

## 10. 2026-10-05 diagnostic issuance note

For the 2026-10-05 morning diagnostic with feature cutoff 2026-10-02:
- AURORA = DOWN, p_up = **0.30075**;
- HELIOS V5-DCE = DOWN, p_up = **0.30075**;
- RIFT = DOWN, reversal probability = **0.55628**, no override;
- VEGA = DOWN, reversal probability = **0.46319**, no override.

This is **diagnostic-nowcast evidence**, not clean prospective validation, because the formal post-freeze source path could not issue the complete forecast under its original timing contract and the missing recent market rows were supplied through the diagnostic bridge.

A full CIG-D1 action requires the same-origin SAGE+RuleFlow state as well. Until that state is independently confirmed for the 2026-10-02 origin, the 2026-10-05 CIG-D1 record must not be mislabeled as a completed 4/4 prospective consensus.

---

## 11. Governance status

**CIG-D1 V1 status:** `RETROSPECTIVE_SELECTIVE_D1_CHALLENGER`

Allowed:
- historical D1 diagnostics;
- frozen future shadow evaluation;
- reporting LONG / OUT / UNCERTAIN under the rule above.

Not allowed:
- relabeling retrospective 2023-2026 results as prospective;
- tuning consensus membership or thresholds on 2026 outcomes and calling the result OOS;
- converting UNCERTAIN to a forced action without a separately frozen rescue identity;
- mixing source clocks silently.

Promotion requires a separate prospective freeze and sufficient unseen daily observations.


---

## 12. Clock-semantics correction — 2026-10-06

**Authority:** `GOLD_D1_FORECAST_CLOCK_RECONCILIATION_2026-10-06.md`

The 2026 Jan-Jul figure **93/125 = 74.40%** remains the historical accuracy of the frozen **daily label** used in this document.

It must no longer be described as:
- accuracy from 08:00 New York onward;
- executable same-day return accuracy;
- evidence that the entire realized daily move occurred after signal issuance.

The governed issue deadline is **08:00 America/New_York**. Historical retrospective CIG rows do not contain actual `issued_at_utc` timestamps.

A 15-minute clock diagnostic on a reconstructed raw execution population produced 08:00->20:00 direction accuracy of:
- 2025 H2: 50.45% (N=111)
- 2026 Jan-Jul: 51.15% (N=131)
- 2026 Aug-Sep: 42.31% (N=26).

However, the reconstructed Jan-Jul timing population has **131** consensus rows, while this canonical CIG result has **125**. Therefore the 51.15% figure is **not** an apples-to-apples replacement for 74.40%.

Binding terminology from this point:
- **74.40% = historical daily-label accuracy**
- post-08:00 statistics = **execution-clock diagnostics**
- final executable CIG accuracy remains **UNRESOLVED** until the exact 125-row canonical population is rejoined to intraday prices.

This correction supersedes any prior wording that implied otherwise.


## 13. Binding clock identity — 2026-10-06

Authority: `GOLD_MODEL_CLOCK_IDENTITY_2026-10-06.md`

CIG-D1 inherits a mixed clock stack:
- underlying governed daily label = **UTC-day daily-reference semantic**;
- intraday H3 expert features = **New York clock**, 16:00 anchor;
- operational issue deadline = **08:00 New York**;
- Istanbul time is only a user-facing conversion.

Therefore CIG-D1 is not currently a Turkey-session model and its historical same-day label is not an 08:00-NY-to-close label.


---

## 14. Exact canonical post-issue rescore — 2026-10-06

**Authority:** `GOLD_CIG_EXACT_125_CLOCK_RESCORE_RESULT_2026-10-06.md`

The original 145-row Jan-Jul daily realization ledger has now been recovered exactly from the prior project artifact:
`GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv`.

Pinned historical expert states reproduce this document's published counts exactly:
- daily universe: 145
- SAGE+RuleFlow: 103/145
- V5: 102/145
- RIFT: 102/145
- VEGA: 102/145
- 4/4 consensus: 125
- consensus correct: 93
- consensus accuracy: **74.40%**
- disagreement: 20
- SAGE forced correct on disagreement: 10.

The six dates missing from the old frozen realization snapshot are:
2026-02-27 and 2026-03-02 through 2026-03-06.
This is a snapshot coverage gap, not a market-hours rule.

The exact same 125 consensus signals were then re-scored strictly after the governed 08:00 New York issue deadline using XAU/USD 15-minute prices and a first executable timestamp of 08:15 New York:

- 08:15->16:00 NY: **59/125 = 47.20%**
- 08:15->20:00 NY: **59/125 = 47.20%**
- 17:00->20:00 NY: **63/125 = 50.40%**

UP-only:
- 08:15->16:00: 34/71 = 47.89%
- 08:15->20:00: 34/71 = 47.89%
- 17:00->20:00: 35/71 = 49.30%.

DOWN-only:
- 08:15->16:00: 25/54 = 46.30%
- 08:15->20:00: 25/54 = 46.30%
- 17:00->20:00: 28/54 = 51.85%.

**Binding consequence:** the historical 74.40% remains valid only as daily-label accuracy. CIG-D1 V1 is not established as an 08:00-NY-forward tradable same-day direction model.

Earlier reconstructed 151/131 timing results are superseded for the canonical Jan-Jul CIG interpretation.


## 14. Exact canonical 125 post-issue reconciliation — 2026-10-06

Authority:
- `GOLD_CIG_EXACT_125_CLOCK_RESCORE_RESULT_2026-10-06.md`

The original 2026 Jan-Jul CIG population was recovered exactly from the prior daily-realization artifact.

Exact reproduction:
- universe: **145**
- consensus: **125**
- consensus correct: **93**
- historical daily-label accuracy: **74.40%**
- disagreement: **20**
- disagreement correct: **10**.

Using those identical 125 consensus rows and XAU/USD 15-minute prices beginning strictly after the governed 08:00 New York deadline:

- 08:15 -> 16:00 NY: **59/125 = 47.20%**
- 08:15 -> 20:00 NY: **59/125 = 47.20%**
- 17:00 -> 20:00 NY: **63/125 = 50.40%**

Therefore 74.40% is confirmed as **historical daily-reference label accuracy**, not post-08:00 executable direction accuracy.

Any prior canonical-CIG interpretation that treated 74.40% as tradable same-day accuracy after issuance is superseded.
