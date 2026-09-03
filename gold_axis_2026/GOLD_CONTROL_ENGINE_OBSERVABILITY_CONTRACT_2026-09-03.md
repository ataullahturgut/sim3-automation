# GOLD CONTROL — ALL-ENGINE OBSERVABILITY CONTRACT

**Issue date:** 2026-09-03  
**Authority:** `GOLD_CONTROL_PROJECT_MANIFEST.md` target v1.23  
**Status:** `FROZEN_ALL_GOVERNED_ENGINES_VISIBLE_V1`  
**Scope:** presentation/read-model observability only; no model, selector, ensemble, threshold, source, target, horizon, evidence-class, or action-rule change.

## 1. Purpose

The current product goal is to make every governed forecast, direction, tactical, event, emergency, regime, and risk motor visible before any future selector/final-decision research is undertaken.

The user must be able to answer, for every motor:

1. Does this motor exist in the governed architecture?
2. Is it currently producing a stored/issued output, waiting for an eligible origin, blocked, or not proven?
3. What is its latest legitimate output, if any?
4. What is the exact evidence class / track / target-as-of context?
5. What model or feature version produced the observable state?
6. What limitation or blocker currently prevents a forward output?

A blank card is not an acceptable representation when a governed blocker or stored context exists.

## 2. Authority basis

This contract is authority-informed, not a claim that Gold Control is a regulated banking model-risk program.

The design follows the model-observability principles in:

- Federal Reserve / OCC / FDIC **Revised Guidance on Model Risk Management (SR 26-2, 2026)**: an effective model inventory should contain sufficient information to understand model risks at individual and aggregate levels; ongoing monitoring should evaluate whether models perform as expected and should surface limitations.
- Federal Reserve examination guidance: model inventory information commonly includes purpose, usage/restrictions, inputs/components, outputs, whether models are functioning properly, last update, and exceptions/limitations.
- NIST AI RMF 1.0 **Govern 1.6**: mechanisms should exist to inventory AI systems.
- NIST AI 800-4 (2026): deployed-system monitoring is needed to verify that systems continue to operate reliably as intended and to provide visibility into unexpected outputs/conditions.

These principles are adopted as internal engineering/governance criteria for Gold Control.

## 3. Frozen engine inventory

### A. Monthly H=1 forecast experts

1. `CAUSAL_PATCH`
   - role: forward issuer candidate / monthly expert
   - version: `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE`
   - current forward state before eligible end-September origin: `WAITING_ELIGIBLE_MONTH_END_ORIGIN`

2. `VW_MIDAS_MSVR`
   - role: audited analytical shadow/reference
   - version: `VW_AUDITED_SHADOW_V2`
   - current forward state: `BLOCKED_NOT_PROVEN_EXECUTABLE`

3. `MOMENTUM_3M`
   - role: monthly expert / direction challenger
   - version: `MOMENTUM_3M_R1`
   - forward monthly-level state: `BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND`
   - its stored direction-context channel is separately visible as `MONTHLY_DIRECTION_3M` and must not be mistaken for an issued H=1 price forecast.

4. `RANDOM_WALK`
   - role: mandatory naive benchmark
   - version: `RW_R1`
   - forward monthly-level state: `BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND`

### B. Strategic/tactical direction channels

5. `MONTHLY_DIRECTION_3M`
   - role: strategic monthly direction / prior / context
   - feature version: `R4_1_3M_SIMPLE_RETURN_V1`
   - direction vote: yes, within its frozen role only

6. `FAST`
   - role: tactical short-horizon confirmation/conflict state
   - current feature version: `R4_1_SMA20_2_MARKET_DAY_PERSISTENCE_V1`
   - direction vote/context: yes, within its frozen tactical role only

7. `SLOW`
   - role: tactical medium-horizon confirmation/conflict state
   - current feature version: `R4_1_COMPLETED_WEEKLY_SMA4_2_WEEK_PERSISTENCE_V1`
   - direction vote/context: yes, within its frozen tactical role only

### C. Event / emergency / regime layers

8. `MACRO_EVENT`
   - role: timestamp-safe event-risk state only
   - current state: `BLOCKED_NOT_FULLY_RECOVERED`

9. `EMERGENCY_LEVEL`
   - role: abnormal level-move alert/context
   - current forward state: `BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE`

10. `EMERGENCY_REVERSAL`
    - role: reversal alert/context
    - current forward state: `BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE`

11. `BOCPD`
    - role: regime/break context and alert only
    - current state: `BLOCKED_EXACT_FORWARD_BOCPD_RULE_NOT_RECOVERED`

### D. Risk layer

12. `GVZ_RISK`
    - role: volatility/risk-cap context
    - feature version: `R4_1_GVZ_RISK_CAP_CONTEXT_V1`
    - direction vote: **false**
    - it may constrain risk but may not be displayed as a bullish/bearish gold-direction engine.

## 4. Required UI fields

Every inventory item must expose, where applicable:

- engine ID and human-readable label;
- category;
- frozen role;
- current legitimate output;
- operational status (`ISSUED`, `STORED_CONTEXT_AVAILABLE`, `WAITING`, `BLOCKED`, `NOT_PROVEN`, or explicit governed status string);
- model/feature version;
- evidence class;
- target month / target context;
- as-of / last update timestamp;
- direction-vote flag or explicit `NOT_DIRECTION` role when relevant.

If a legitimate value does not exist, the UI must display the exact blocker or waiting status rather than inventing a number, direction, probability, confidence, or proxy.

## 5. Evidence separation

The UI may expose multiple evidence classes, but it must not silently merge them:

- `HISTORICAL_REPLAY`
- `LATE_BOOTSTRAP_SHADOW_CONTEXT`
- `PROSPECTIVE_SHADOW`
- `LIVE_PRODUCTION`

Historical replay availability may be shown as research evidence, but it is not a current forward output.

## 6. Decision separation

This observability contract does **not** authorize:

- expert selection;
- automatic ensemble/weighting;
- winner labels;
- final BUY/SELL/HOLD/EXIT/REDUCE mappings;
- promotion of a context component to canonical forecast authority;
- promotion of a blocked or historical-replay object to prospective/live state.

The existing locks remain binding:

- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `AUTO_SELECTOR=OFF`
- `AUTO_ENSEMBLE=OFF`
- `NOT_PROVEN_POSITION_MAPPING`

The sequence is deliberately:

`SEE ALL MOTORS → VERIFY OPERATION / EVIDENCE → ACCUMULATE CLEAN OUTPUT HISTORY → RESEARCH SELECTION / DECISION RULES LATER`.

## 7. Read-path rule

The application is a read/presentation layer. It may display already persisted immutable component context and issued expert rows, but it may not recompute a new production direction or forecast from live spot.

For component shadow context, per-feature version, calculation timestamp, input cutoff, evidence class and target context should be preserved by the UI read model whenever those fields exist in Neon.

## 8. Acceptance gates

PASS requires all of the following:

1. all 12 governed inventory entries are visible in one user-facing observability surface;
2. `MONTHLY_DIRECTION_3M`, `FAST`, `SLOW`, and `GVZ_RISK` can display persisted current context independently;
3. a missing H=1 expert row does not suppress its engine card;
4. a blocked motor displays its exact blocker;
5. `MOMENTUM_3M` H=1 price output and `MONTHLY_DIRECTION_3M` stored direction are visibly distinct;
6. GVZ is never rendered as a direction vote;
7. no selector/ensemble/final-action inference is introduced;
8. tests prove complete inventory coverage and fail-closed behavior;
9. mobile 390px QA remains passing.

## 9. Current production snapshot at contract freeze

Read-only Neon audit on 2026-09-03 showed:

- `monthly_expert_forecasts`: **0 rows**;
- `MONTHLY_DIRECTION_3M = DOWN`, version `R4_1_3M_SIMPLE_RETURN_V1`;
- `FAST_STATE = ROBUST_UP`, version `R4_1_SMA20_2_MARKET_DAY_PERSISTENCE_V1`;
- `SLOW_STATE = ROBUST_UP`, version `R4_1_COMPLETED_WEEKLY_SMA4_2_WEEK_PERSISTENCE_V1`;
- `GVZ_VALUE = 26.14`, `GVZ_REGIME = ELEVATED`, `GVZ_CAP = 0.5`, version `R4_1_GVZ_RISK_CAP_CONTEXT_V1`;
- all of the above component rows carry `LATE_BOOTSTRAP_SHADOW_CONTEXT` evidence/quality;
- Macro Event, Emergency forward state, and BOCPD remain blocked under their existing frozen gates.

This snapshot is evidence of the need for observability; it does not authorize a final decision.
