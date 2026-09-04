# Gold Control — Unresolved Engine Successor Roadmap

**Date:** 2026-09-04  
**Status:** `PRE_REGISTERED_SUCCESSOR_ROADMAP_V1`  
**Authority:** subordinate to `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.30, current frozen contracts, production Neon state, and `GOLD_CONTROL_V130_UNRESOLVED_ENGINE_RECOVERY_AUDIT_2026-09-04.md`.  
**Canonical branch authority remains:** `gold-r4-direction-engine`  
**Working branch:** `gold-control-bocpd-successor-v1`

## 1. Purpose

The project has three remaining archived motors whose exact forward implementation is not fully recovered:

1. `VW_MIDAS_MSVR`
2. `MACRO_EVENT`
3. `BOCPD`

A missing archived implementation must not be guessed and relabelled as the original motor. However, a missing exact archive does not prohibit building a new, clearly identified successor motor under a separate change-control and prospective validation path.

This roadmap therefore separates two identities:

- **archived identity** — remains `BLOCKED` / `NOT_PROVEN` until exact recovery is proven;
- **successor identity** — new implementation, new version, new evidence chain, no inheritance of archived production authority.

## 2. Global governance locks

The following remain unchanged throughout successor work:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `NOT_PROVEN_POSITION_MAPPING`
- no BUY / SELL / HOLD / EXIT / REDUCE mapping;
- no retrospective prospective claim;
- no automatic winner;
- historical replay is never promoted to prospective evidence;
- no source substitution under the same series identity;
- app remains read-only / presentation;
- production state authority remains Neon;
- code / model / frozen-contract authority remains GitHub;
- no production DB write from a successor research gate unless a later explicitly frozen issuer contract authorizes it.

## 3. Mandatory successor sequence

Every successor motor must follow this order:

1. authority / literature recovery;
2. pre-registered change-control;
3. frozen source + information-set contract;
4. deterministic executable implementation;
5. unit, determinism and prefix/PIT tests;
6. development-only calibration where calibration is required;
7. untouched validation evaluation;
8. locked replay diagnostic without tuning;
9. explicit evidence classification;
10. only then, if justified, a separate prospective-shadow issuer contract.

No parameter, threshold, source, feature, alert mapping or role may be changed after validation/locked results are inspected without a new change-control and a new successor version.

## 4. Priority order

### 4.1 First — `BOCPD_RETURN_SUCCESSOR_V1`

Reason for first priority:

- archived role and much of the historical contract are recovered;
- approved role is regime/break context only, not a direction vote;
- frozen expected run length `L=36` is recovered;
- signal availability after completed month close is recovered;
- validation and locked windows are recovered;
- the remaining missing archived items are specifically likelihood/prior/reset-score implementation.

The successor must **not** reverse-fit the archived BOCPD score path. It must define a new score/state semantic before validation output is inspected.

### 4.2 Second — `VW_MIDAS_MSVR_SUCCESSOR_V1`

The archived exact VW executable remains blocked. Existing research/rebuild code and the published VW-MIDAS-MSVR family may be used as research evidence, but unresolved `GPY`, exact trend/volatility definitions, `g_volatility`, provider identity and revision-safe PIT lineage prevent silent exact-replication claims.

The successor must have a new source contract and must not use convenience/proxy identities as if they were archived identities.

### 4.3 Third — `MACRO_EVENT_SUCCESSOR_V1`

The archived Macro Event motor preserves only partial trigger logic. A successor requires a separately frozen definition for macro releases, actuals, expectations/consensus if used, surprise normalization, revision/vintage semantics and release timestamps.

Official release actuals and historical vintages must be point-in-time safe. If a governed historical consensus source cannot be established, a consensus-based score must remain blocked; a different successor design would require a different change-control and identity.

## 5. BOCPD-specific authority basis

Primary methodological authority:

- Ryan Prescott Adams and David J. C. MacKay, **Bayesian Online Changepoint Detection** (2007), arXiv:0710.3742.

Authority-relevant principles adopted:

- online causal filtering using only observed data;
- posterior distribution over run length;
- hazard function defines changepoint-interval prior;
- geometric/discrete-exponential gap prior implies constant hazard `H=1/L`;
- conjugate-exponential predictive models permit exact recursive updating;
- finance application demonstrates BOCPD on return data;
- the detector/model likelihood and the changepoint recursion are modular and must be explicitly specified.

These principles do **not** prove the missing archived Gold Control likelihood/prior/reset score. They are the basis for a **new successor** only.

## 6. Recovered archived BOCPD facts retained as constraints

The successor work may retain the following recovered project facts without claiming exact archived executable identity:

- role: regime/break context only;
- direction vote: `false`;
- monthly CORE5 gold log-return axis;
- development family window: 2010-01 through 2020-12;
- validation: 2021-01 through 2023-12;
- locked replay: 2024-01 through 2026-07;
- 2026 tuning: prohibited;
- expected run length: `L=36` months;
- adverse context requires a completed-month negative return;
- month `t` signal is usable only after month `t` closes;
- no automatic direction flip;
- no automatic hard exit;
- no position sizing/action mapping.

The archived threshold `0.034027906134261016` belongs to the archived reset-score semantic and **must not be reused** by a successor unless score equivalence is independently proven. No such equivalence is currently proven.

## 7. Evidence classes

Successor evidence must be labelled explicitly:

- implementation/unit tests: `ENGINEERING_EVIDENCE`
- historical development/validation/locked run: `HISTORICAL_REPLAY_SUCCESSOR_RESEARCH`
- first future origin-time run, only after an issuer contract exists: `PROSPECTIVE_SHADOW`
- `LIVE_PRODUCTION` is prohibited until later graduation gates are explicitly frozen and passed.

## 8. Runtime consequences

Creating or validating a successor candidate does not overwrite the archived runtime row.

Until a later promotion contract exists:

- archived `BOCPD` remains blocked;
- `BOCPD_RETURN_SUCCESSOR_V1` is a research/shadow candidate outside direction voting;
- runtime counts and direction-vote permissions must not be silently changed;
- Decision Store authority is not created;
- no canonical final decision is created.

## 9. Exit criterion for this roadmap stage

The BOCPD successor stage may be called complete only when:

- the BOCPD successor change-control is frozen before validation results;
- implementation is deterministic;
- future-prefix invariance/PIT tests pass;
- no DB writes occur;
- validation/locked windows are not used for retuning;
- results are recorded with non-prospective evidence labels;
- archived BOCPD remains clearly distinct and blocked;
- any later prospective-shadow issuer is a separate contract.
