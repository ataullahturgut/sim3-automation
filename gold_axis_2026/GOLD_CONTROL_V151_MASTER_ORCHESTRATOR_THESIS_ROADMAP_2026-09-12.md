# Gold Control V1.51 — Master Orchestrator Doctoral Research Roadmap

**Date:** 2026-09-12  
**Branch:** `gold-v151-master-orchestrator-thesis`  
**Parent research state:** V1.50 role-hierarchical thesis branch  
**Canonical production authority:** unchanged; canonical V1.49 remains authoritative until later explicit promotion  
**AUTO_SELECTOR:** `OFF`  
**AUTO_ENSEMBLE:** `OFF`  
**Production writes:** `NONE`

## 1. Research objective

Build a single **role-aware, availability-aware, point-in-time-safe Master Orchestrator** that consumes the existing Gold Control expert/context engines without pretending that heterogeneous engines are interchangeable votes.

The Master Orchestrator must answer five separate questions:

1. **Price level:** where is the monthly XAU/USD level expected to be?  
2. **Strategic/tactical direction:** what direction is supported at monthly, daily and short-horizon clocks?  
3. **Event direction:** when a governed macro event occurs, what is the first post-release reaction direction?  
4. **Regime / reversal / shock:** has the market regime changed, is the move extreme, and has an event signal transmitted into price?  
5. **Confidence / evidence quality:** which engines are actually eligible at origin `t`, with what lineage, freshness and evidence class?

The goal is **not** to force every engine into one monolithic regression. The goal is to create a governed **mixture-of-specialists / hierarchical forecast-decision architecture** in which each engine contributes only within its legitimate role and clock.

## 2. Scientific principles and external methodological anchors

The design is anchored to established forecasting literature:

- **Rolling-origin / time-series cross-validation:** only past observations may be used for each forecast origin; multi-step targets require horizon-aware rolling origins. Hyndman & Athanasopoulos, *Forecasting: Principles and Practice*, time-series cross-validation.
- **Forecast combination under instability:** recursive and rolling estimators can have different bias-variance profiles under structural change; combining them can improve forecast accuracy. Clark & McCracken (2009), *International Economic Review*, DOI `10.1111/j.1468-2354.2009.00533.x`.
- **Dynamic Model Averaging:** model probabilities/weights may evolve over time under model uncertainty rather than assuming one permanent winner. Raftery, Kárný & Ettler (2010), *Technometrics*, DOI `10.1198/TECH.2009.08104`.
- **Conditional forecast combinations:** recent relative performance can contain information, but model rankings can cross; conditional pooling and shrinkage are preferable to blindly choosing a single recent winner. Aiolfi & Timmermann (2006), *Journal of Econometrics*, DOI `10.1016/j.jeconom.2005.07.015`.
- **Mixture of local experts / gating:** modular specialists can be assigned to different subsets/regimes rather than averaged indiscriminately. Jacobs, Jordan, Nowlan & Hinton (1991), *Neural Computation*, DOI `10.1162/neco.1991.3.1.79`.
- **Forecast comparison:** pairwise predictive-accuracy claims require loss-differential testing rather than point estimates alone. Diebold & Mariano (1995), *JBES*, DOI `10.1080/07350015.1995.10524599`. DM results must be interpreted as forecast comparisons, not universal model superiority.
- **Gold macro-event specialization:** macroeconomic announcement effects on gold are fast, directional and event-specific, which supports a separate event specialist rather than pooling event reactions into unconditional daily forecasts. Elder, Miao & Ramchander (2012), *Journal of Banking & Finance*, DOI `10.1016/j.jbankfin.2011.06.007`; later high-frequency gold work also documents rapid announcement incorporation and belief-dispersion effects.

These references justify the architecture, but do not pre-authorize any Gold Control implementation. Gold Control evidence must still pass its own frozen validation gates.

## 3. Evidence-window policy

The requested thesis evaluation geometry is retained, with one important labeling safeguard:

- **Development / research formation:** through 2024-12-31, with inner rolling/expanding origins only.
- **2025:** validation / architecture-selection audit.
- **2026:** locked test audit.
- **Future unseen origins after V1.51 freeze:** genuine prospective shadow evidence.

Because 2025-2026 outcomes have already been researcher-visible in earlier Gold Control work, they may not be represented as fully blind untouched evidence. They are therefore labelled **retrospective locked validation/test audits**. No rule may be changed after examining 2026 test outcomes. Genuine promotion evidence must come from newly frozen future origins.

## 4. Master Orchestrator architecture

### 4.1 Price layer

Monthly H=1 experts remain separate:

- `VW_MIDAS_MSVR_SUCCESSOR_V1`
- `CAUSAL_PATCH`
- `MOMENTUM_3M`
- `RANDOM_WALK`

The Master Orchestrator does not silently select or average them. Research-only combination challengers may be evaluated, but `AUTO_SELECTOR=OFF` and `AUTO_ENSEMBLE=OFF` remain binding.

### 4.2 Direction layer

- `MONTHLY_DIRECTION_3M`: strategic prior.
- `FAST`: tactical persistence/trend context.
- `SLOW`: slower trend/regime context.
- general `NEXT_NY17_1D` / `NEXT_NY17_3D`: research probabilistic direction lane.

### 4.3 Event specialist layer

- `MACRO_EVENT_SUCCESSOR_V2` / governed research score lineage for Employment, Inflation and FOMC.
- first-reaction targets remain separate from continuation targets.
- prospective primary endpoint remains post-score 15-minute direction under the V1.50 event shadow freeze.

### 4.4 Regime / shock / reversal layer

- `BOCPD_RETURN_SUCCESSOR_V1`: regime-break context.
- `MARKET_SHOCK_CHALLENGER_V3`: post-release shock confirmation/context only.
- `EMERGENCY_LEVEL`: extreme-level context.
- `EMERGENCY_REVERSAL`: reversal-risk context.
- `GVZ_RISK`: volatility/risk-only context.

### 4.5 Evidence / availability gate

Every engine consumed by the orchestrator must expose at minimum:

```text
engine_id
engine_role
as_of
information_cutoff
source_ids
source_freshness
pit_status
evidence_class
runtime_status
eligible
state_or_prediction
confidence_or_calibration
block_reason
input_fingerprint
git_commit
```

**Missing is not neutral.** If an engine is unavailable at origin `t`, its contribution is `NOT_APPLICABLE` / `BLOCKED`, never `0` or a fabricated neutral vote.

## 5. Research hypotheses

### H1 — Role hierarchy beats naive equal voting

A hierarchy that respects engine role and clock will outperform a naive equal-vote architecture on calibration / probabilistic loss and will reduce contradictory state interpretation.

### H2 — Regime-aware general direction beats static winner selection

General 1D/3D performance is time-varying. A predeclared regime-adaptive architecture based only on information available at the origin can outperform a permanently fixed winner or recent-winner hindsight selection.

### H3 — Event specialist must remain conditionally separate

Macro-event first-reaction predictive power will be materially stronger than unconditional daily-direction performance, while event-to-next-NY17 continuation will remain a distinct task.

### H4 — Risk/context engines improve calibration more reliably than raw hit rate

`BOCPD`, `GVZ`, Emergency and Market Shock should be evaluated first as **confidence / eligibility / regime modifiers**, not as equal-weight direction votes.

### H5 — Dynamic combination is only justified within homogeneous roles

Dynamic Model Averaging / conditional combination may be tested **within** homogeneous candidate sets (e.g. general 1D models, monthly H=1 experts) but not across engines with fundamentally different targets and clocks.

## 6. Implementation phases

### Phase A — Inventory and origin-time availability matrix

Create one audit table for every candidate input / engine:

- earliest usable economic timestamp;
- earliest defensible origin-time availability;
- latest timestamp;
- retrieval/vintage semantics;
- historical reconstruction vs true PIT/prospective status;
- source gaps;
- target clocks for which the source is eligible.

**Gate A:** no engine enters the orchestrator until availability semantics are explicit.

### Phase B — Master state schema and deterministic orchestrator baseline

Implement `MASTER_ORCHESTRATOR_BASELINE_V1` as a deterministic state renderer with **no learned fusion weights**.

Required outputs:

```text
monthly_price_expert_state
strategic_direction
tactical_direction
general_1d_probability
general_3d_probability
event_direction
market_shock_confirmation
regime_break_state
emergency_level
emergency_reversal
volatility_risk
source_coverage
engine_disagreement
master_confidence
master_interpretation
```

This baseline is the control treatment for every later learned orchestrator.

### Phase C — General-direction candidate lane

Keep the V1.50 correction to feature blocks and extend only by preregistered hypotheses.

Candidate families:

1. fixed expanding logistic baseline;
2. fixed rolling logistic baseline;
3. convex recursive+rolling combination;
4. shallow HGB as nonlinear challenger;
5. conditional combination / shrinkage challenger;
6. DMA-style challenger among a small fixed set of general-direction models.

No deep network or large hyperparameter search is allowed before simpler candidates fail under the same PIT design.

Candidate context blocks:

- G0: gold own history;
- G1: FAST / SLOW / Monthly Direction;
- G2: rates / FX PIT;
- G3: equities where availability semantics permit;
- G4: precious metals where availability semantics permit;
- G5: regime/risk states **only when historically legitimate at that origin**.

`GVZ` is never backfilled into dates where a legitimate historical/prospective series is absent.

### Phase D — Event specialist lane

Preserve the V1.50 event freeze.

Primary future endpoint:

- post-score R15.

Secondary:

- R5;
- R30;
- strong-state subgroup;
- Market Shock overlap/sign confirmation;
- event-to-next-NY17 continuation, reported separately.

No continuation model may inherit the event specialist's initial-reaction hit rate as if they were the same target.

### Phase E — Role-aware orchestrator challengers

Evaluate the following **in this order**, stopping a candidate when it fails gates:

- **O0 — deterministic hierarchy:** no learned weights; displays all eligible role states.
- **O1 — confidence gating:** direction output may be suppressed to `NO_SIGNAL` under poor calibration, regime break, high disagreement or insufficient source coverage. Thresholds selected only inside development/validation.
- **O2 — within-role conditional combination:** recent mature forecast errors determine shrinkage weights only among same-target models.
- **O3 — DMA-style within-role model probabilities:** small fixed candidate universe; forgetting factor / transition design selected only in development.
- **O4 — regime-conditioned specialist gate:** BOCPD / trend context may change which **predeclared** general-direction expert is eligible; it may not choose after the target outcome.
- **O5 — event override context:** on governed event origins, Macro Event becomes the event-direction authority for its short reaction horizon; Market Shock can confirm after it is observable but cannot backdate the event signal.

There is no O6 that simply places all engines in a single equal-weight vote.

## 7. Validation design

### 7.1 Chronology

- random split forbidden;
- nested rolling/expanding origin only;
- transformations fitted on training data only;
- every prediction frozen before target maturity;
- target-horizon maturity respected before an error enters any adaptive weight.

### 7.2 2025 validation use

2025 may choose among **already preregistered** V1.51 orchestrator candidates only.

A candidate cannot be invented after seeing its 2025 result and then represented as if it were preregistered.

### 7.3 2026 locked test use

After one V1.51 candidate is chosen from development + 2025 validation, its specification is frozen. 2026 is then evaluated once.

No feature, threshold, weighting rule, forgetting factor, event definition or regime gate may change after 2026 test results are inspected.

## 8. Metrics and statistical gates

### Monthly price layer

- MAE;
- RMSE;
- MAPE as descriptive secondary metric;
- benchmark: Random Walk;
- pairwise loss differential / DM-style or appropriate HAC comparison when sample permits;
- expert disagreement and stability.

### General 1D / 3D probabilistic direction

Primary:

- Brier score;
- log loss;
- calibration intercept/slope;
- balanced accuracy.

Secondary:

- directional accuracy;
- coverage under selective prediction;
- risk-coverage curve;
- regime/family stability.

Mandatory benchmarks:

- P50;
- expanding up-frequency;
- fixed G0 logistic;
- V1.50 frozen baseline where directly comparable.

### Event direction

- exact directional hit rate;
- exact binomial test against 0.5;
- median signed return;
- event-family decomposition;
- strong-state subgroup;
- source coverage and prediction latency;
- Market Shock overlap and sign concordance.

### Master Orchestrator

The master system is not scored by one artificial scalar alone. It must report a **multi-objective scorecard**:

1. price forecast loss;
2. direction probabilistic loss;
3. event hit/calibration;
4. source coverage;
5. abstention / no-signal rate;
6. false-confidence rate;
7. stability across regimes;
8. contradiction/disagreement resolution quality.

A composite research score may be reported only as secondary sensitivity analysis, with predeclared normalization and weights. It cannot replace the individual primary gates.

## 9. Promotion gates

A V1.51 candidate is **not** promoted merely because one headline accuracy number is high.

Minimum requirements:

- chronology and PIT audit pass;
- no silent missing-as-neutral substitution;
- no 2026-driven tuning;
- at least one primary metric beats the relevant simple benchmark in 2025 validation;
- no material degradation in the paired primary metric (e.g. Brier improvement with catastrophic log-loss deterioration is failure);
- 2026 locked test does not reverse the economic conclusion;
- calibration is usable;
- source coverage is reported and acceptable;
- result survives family/year/regime decomposition;
- any statistical superiority claim is supported by an appropriate forecast-comparison procedure and sample size caveat;
- future prospective shadow remains mandatory before production authority.

## 10. "Do not stop until a good result" research rule

This instruction is interpreted scientifically as **persistent falsification, not test-set mining**.

If a candidate fails:

1. record the failure unchanged;
2. diagnose whether the failure is data, clock, calibration, regime instability, redundancy or model-class misspecification;
3. formulate one new hypothesis;
4. freeze a new successor identity before evaluating new evidence;
5. never repair a failed candidate using the same locked test outcomes and then call the repair out-of-sample.

The research programme continues across successor hypotheses until either:

- a candidate clears the frozen gates, or
- the available data cannot identify the claimed improvement, in which case the thesis result is `NOT_PROVEN` / `MORE_DATA_REQUIRED`, not a manufactured success.

## 11. Immediate implementation order

1. Build the complete engine/data availability matrix from Neon + canonical contracts.
2. Implement `MASTER_ORCHESTRATOR_BASELINE_V1` with deterministic role hierarchy and evidence gates.
3. Add a reproducible historical replay surface that emits one master-state row per eligible origin without production writes.
4. Reconstruct 2023-2024 development master states.
5. Freeze the V1.51 candidate universe and all adaptive-rule hyperparameters before 2025 scoring.
6. Run 2025 validation once and choose only among preregistered candidates.
7. Freeze the winner/specification.
8. Run 2026 locked test once.
9. Produce thesis tables: overall, year, regime, event-family, coverage, calibration, error dependence, and failure analysis.
10. Start newly prospective shadow collection under the frozen winner.

## 12. Thesis contribution target

If supported by evidence, the intended methodological contribution is not merely "another gold forecasting model". It is:

> **A point-in-time-safe, role-hierarchical mixture-of-specialists architecture for gold forecasting that separates price-level forecasting, unconditional direction, event-conditioned direction, regime detection, shock confirmation, reversal risk and confidence gating; and that evaluates adaptive fusion under structural instability without contaminating locked test periods.**

That claim is provisional until the corresponding frozen validation and prospective evidence supports it.
