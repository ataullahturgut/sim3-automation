# SESSION HELIOS V1-V5 — PREREGISTRATION / STAGE-2→4 CONTRACT

**Date:** 2026-10-07  
**Status:** BINDING BEFORE SESSION HELIOS RUN

## Scope

This contract rebuilds the historical HELIOS lineage on corrected SESSION targets:

`V1 -> V2 -> V3-GT -> V4-RGE -> V5-DCE`.

HELIOS remains a higher-order router/exception architecture. It is not an independent raw-feature direction model.

## Fresh upstream only

Mandatory inputs are regenerated from the current SESSION raw-source chain:

- SESSION AURORA probability/state;
- corrected-PIT SESSION OPAL probability/override/COT vintage;
- canonical SESSION RIFT reversal probability;
- canonical SESSION TURN tail override;
- canonical SESSION VEGA reversal probability.

Archived H3 prediction/state CSVs are prohibited as model inputs.

RIFT / TURN / VEGA are consumed only as HELIOS corroborator telemetry. Their use inside HELIOS does not grant them independent final-consensus votes.

## Clock / maturity

State is independent for every partition/window.

At current session start `T=start_utc`, adaptive histories may ingest only prior same-window outcomes satisfying:

`end_utc <= T`.

No overlapping or still-open target outcome may update competence, game-theory or regret state.

## Frozen historical HELIOS rules

### V1 competence gate
- competence window = 8 matured HELIOS candidate events;
- enter active when wins >= 5;
- exit active when wins <= 3;
- candidate reversal = OPAL override AND at least one corroborator override from RIFT / TURN / VEGA;
- hard route only when competence gate is active and candidate reversal is true.

### V2 posterior calibration
- routing identity unchanged from V1;
- routed probability uses Beta(1,1)-smoothed competence probability `q=(wins+1)/(8+2)`;
- if AURORA is UP, routed `p_up=1-q`;
- if AURORA is DOWN, routed `p_up=q`.

### V3-GT
Policies:
- KEEP
- HELIOS_CONSENSUS
- COT_FRESH
- FRESH_OR_CONSENSUS
- OPAL_ALL

Frozen market:
- last 8 matured OPAL events;
- broken-call cost = 1;
- exponential-weights learning rate inherited from historical HELIOS;
- route threshold = weighted flip share > 0.50;
- route additionally requires active HELIOS competence state + OPAL override.

COT freshness is evaluated independently within each SESSION partition/window.

### V4-RGE
- V2 base route retained;
- non-consensus OPAL expansion window = 10 matured events;
- enter regret state at +2;
- exit regret state at -2;
- expansion requires active regret state and GT flip share > 0.50.

### V5-DCE
DCE fires only when:
- V4 is not already routing;
- HELIOS competence gate active;
- OPAL override active;
- V1 consensus candidate false;
- GT flip share > 0.50;
- AURORA active expert = PATH_GLOBAL;
- AURORA Pr(PATH superior) > 0.50.

DCE mirrors AURORA probability.

No HELIOS threshold is retuned for SESSION data.

## Evaluation stages

### Stage-2 — 2023-2024 development / role gate

V5 is compared with fresh AURORA on exact HELIOS common rows. A session head is transport-eligible only if:

1. at least one V5 route occurs;
2. combined 2023-2024 V5 net rescue vs AURORA > 0;
3. combined V5 balanced accuracy >= AURORA balanced accuracy;
4. combined V5 Brier <= AURORA Brier + 0.003;
5. in each available year, V5 accuracy is not worse than AURORA by more than 1 percentage point.

The 30% minimum-class-recall floor is not used as a hard deletion rule because HELIOS is a correction/router layer, not a stand-alone balanced primary model. UP/DOWN recalls remain mandatory reporting fields.

### Stage-3 — frozen 2025 transport

Only heads passing Stage-2 may be opened in 2025. No 2025 observation may change HELIOS rules, upstream identities, thresholds, windows or eligibility.

### Stage-4 — 2026 retrospective stress

2026 is reporting/stress only and may not alter any frozen rule.

Stage-4 may run only if a corrected SESSION target/source chain equivalent to V5 exists for 2026 and raw pre-target dependencies cover the scored rows. If not, Stage-4 must fail closed as `DATA_BLOCKED`; no H3 or daily labels may substitute for missing SESSION outcomes.

## Required reporting

For each eligible session:
- N;
- Accuracy;
- Balanced Accuracy;
- UP recall;
- DOWN recall;
- Brier;
- routes/overrides;
- rescues;
- breaks;
- net rescue;
- exact partition/window;
- evidence class.

