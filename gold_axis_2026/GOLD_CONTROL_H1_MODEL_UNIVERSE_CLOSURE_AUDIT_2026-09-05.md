# GOLD CONTROL — H=1 MODEL UNIVERSE CLOSURE AUDIT

Date: 2026-09-05

Canonical target: next calendar month's average XAU/USD price.
Canonical origin: completed month-end information boundary immediately before the target month.

## Purpose

This audit answers one narrow question before any selector/ensemble work:

> Which H=1 price-forecast models were part of the original Gold H1 build plan, which have been completed/rejected/blocked, and which additional model families are only research-expansion candidates rather than unfinished binding stages?

This document does **not** authorize a selector, ensemble, forecast-store write, decision-store write, position mapping, or automatic action.

## A. Original binding Gold H1 R1 price-expert build universe

Historical Gold H1 foundation material defined the working expert set as Random Walk, 3M Momentum, VW-MIDAS-MSVR, and Causal Patch, with the build sequence requiring VW reconstruction and Causal Patch reconstruction before selector/ensemble work.

| Identity / family | Current status | Closure finding |
|---|---|---|
| `RANDOM_WALK` | DONE | Reproducible H=1 benchmark/expert lane exists. September 2026 reconstructed 31-Aug origin reference exists. |
| `MOMENTUM_3M` | DONE | Reproducible H=1 expert lane exists. September 2026 reconstructed 31-Aug origin reference exists. |
| `CAUSAL_PATCH` | DONE | Governed Causal Patch forward/replay lane has been rebuilt under frozen contracts; September 2026 reconstructed 31-Aug origin reference exists. |
| archived `VW_MIDAS_MSVR` | BLOCKED / TERMINAL LEGACY RECOVERY FAILURE | Exact executable identity and PIT/source contract were not recovered. It must not be repaired by guessing. |
| `VW_MIDAS_SVR_XAU_SUCCESSOR_V2` | REJECTED | Separately named successor was tested under its frozen validation contract and ended `REJECT_ALL_VW_SUCCESSOR_V2_CANDIDATES`; it has no runtime/selector authority. |

### Original-plan conclusion

There is **no remaining unattempted mandatory price model in the original Gold H1 R1 build sequence**.

The original sequence is therefore execution-complete in the following truthful sense:

- Random Walk: completed;
- Momentum 3M: completed;
- Causal Patch: completed;
- VW lane: attempted, but not successfully admitted; archived exact identity remains blocked and successor V2 is rejected.

This is **not** the same statement as "the global model universe is closed".

## B. Non-price/context motors — not missing H=1 price models

The following current motors must not be counted as unfinished H=1 price experts:

- `MONTHLY_DIRECTION_3M` — direction context;
- `FAST` — tactical context;
- `SLOW` — tactical context;
- `GVZ_RISK` — risk-only context;
- `BOCPD_RETURN_SUCCESSOR_V1` — regime-break context, no H=1 price forecast;
- `MACRO_EVENT_SUCCESSOR_V2` — intramonth event-risk context, no H=1 price forecast;
- `EMERGENCY_LEVEL` / `EMERGENCY_REVERSAL` — alert/context layer.

## C. Research-expansion universe — NOT part of the old mandatory stage list

The prior deep-research report recommended a broader adaptive architecture. These are legitimate challenger families, but they were **not** frozen as mandatory unfinished stages in the original Gold H1 R1 build sequence.

Each would require a new H=1-specific pre-registration/change-control before scoring.

| Research family | Current Gold Control H=1 status | Audit classification | Priority if user elects to expand universe |
|---|---|---|---|
| TVP-DMA / DMS macro | No governed H=1 implementation identified in current canonical model set | NOT_TESTED | **P1 — first expansion candidate** |
| Regularized macro regression (e.g. ElasticNet/Ridge-style macro) | No governed H=1 expert identified in current canonical model set | NOT_TESTED | P2 |
| Small nonlinear tree model (XGBoost/LightGBM-style) | No governed H=1 expert identified in current canonical model set | NOT_TESTED | P3 |
| Local-level / state-space / ARIMA / ETS benchmark family | Not present as a current governed H=1 expert; RW already supplies the mandatory persistence benchmark | NOT_TESTED_AS_GOVERNED_H1_EXPERT | P4 / benchmark expansion |
| BVAR / factor macro model | No governed H=1 expert identified | NOT_TESTED | P5 |
| Structural institutional process using central-bank demand + ETF flows | No dedicated governed H=1 expert identified | NOT_TESTED | P6; requires PIT/release-lineage work |
| Analyst-consensus benchmark | No governed H=1 consensus benchmark identified | NOT_TESTED | Optional benchmark |
| Deep LSTM / GRU / TCN | No governed H=1 expert identified | NOT_TESTED_LOW_EVIDENCE_PRIORITY | Optional / low priority |
| Wavelet / EMD / VMD + ML | No governed H=1 expert identified | OUT_OF_CORE_UNLESS_CAUSAL_DECOMPOSITION_CONTRACT | Low priority because leakage risk is material |
| GARCH / stochastic-volatility mean model | Not a core H=1 point-mean expert in current design | OUT_OF_CORE_POINT_FORECAST; POSSIBLE_RISK_LAYER | Low priority for point forecast |

## D. Important horizon caveat

The broader research report gave its strongest ranking to TVP-DMA/DMS mainly in a 6–12 month evidence discussion. Gold Control's canonical target is H=1 next-month average XAU/USD.

Therefore this audit **does not silently transfer 6–12M performance claims to H=1**.

If the universe is expanded, every candidate above must receive its own H=1 target/origin/PIT contract and untouched validation gate before model outputs are inspected.

## E. Decision / next step

Two distinct choices now exist:

1. **Close to the original H1 R1 universe.**
   - Then model development is finished: 3 admitted/available price lanes + 1 failed VW lane.
   - Only after an explicit universe-closure decision may selector/ensemble research begin.

2. **Expand the model universe before selector work.**
   - The first justified research-expansion candidate is `TVP_DMA_DMS_H1_SUCCESSOR_V1` (new identity; exact name may be frozen in a separate preregistration).
   - It must be built as a new H=1 model, not inferred from old VW/Causal identities.
   - No selector work should begin until the chosen expansion list reaches terminal states (PASS/REJECT/BLOCKED).

## F. Current audit conclusion

`ORIGINAL_H1_R1_MODEL_PLAN = COMPLETE_WITH_VW_TERMINAL_FAILURE`

`GLOBAL_H1_MODEL_UNIVERSE = NOT_CLOSED`

Reason: the old stage plan has no unattempted mandatory price model left, but the research program contains additional untested adaptive challenger families. Whether they become mandatory is a governance/research-scope decision, not something that may be assumed after seeing model results.

No production Forecast/Decision authority is changed by this audit.
