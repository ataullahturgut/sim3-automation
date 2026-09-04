# Gold Control — BOCPD Return Successor V1 Change Control

**Date:** 2026-09-04  
**Status:** `FROZEN_PRE_REGISTERED_CANDIDATE_V1`  
**Successor identity:** `BOCPD_RETURN_SUCCESSOR_V1`  
**Archived identity:** `BOCPD` — remains `BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED`  
**Authority:** subordinate to `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.30, `GOLD_CONTROL_V130_UNRESOLVED_ENGINE_RECOVERY_AUDIT_2026-09-04.md`, and `GOLD_CONTROL_UNRESOLVED_ENGINE_SUCCESSOR_ROADMAP_2026-09-04.md`.

## 1. Why a successor is required

The archived Gold Control BOCPD family is substantially recovered, including role, data axis, expected run length, historical windows and alarm-side negative-return constraint. The exact archived likelihood/prior initialization and archived `BOCPD reset score` implementation are not recovered.

Therefore this change-control does **not** claim exact recovery. It creates a new motor identity. Archived BOCPD scores/alarms are evidence for historical project understanding only and are not reverse-fitted targets.

## 2. Method authority

Primary methodological authority:

- Ryan Prescott Adams and David J. C. MacKay, *Bayesian Online Changepoint Detection*, arXiv:0710.3742 (2007).

Adopted authority principles:

- causal online recursion over run length;
- no use of future observations in state at month `t`;
- geometric/discrete-exponential changepoint-gap prior represented by constant hazard;
- conjugate predictive model updated recursively;
- explicit separation of hazard model, observation model and alert/state mapping.

Project-specific choices below are **new successor choices**, not claims about the archived implementation.

## 3. Role and prohibitions

Role:

`REGIME_BREAK_CONTEXT`

Direction vote:

`false`

The successor is prohibited from:

- producing an H=1 price forecast;
- replacing Monthly / Fast / Slow direction;
- acting as a second direction vote;
- changing GVZ risk cap;
- selecting a forecast expert;
- producing BUY / SELL / HOLD / EXIT / REDUCE;
- changing exposure/position size;
- writing a canonical decision;
- inheriting the archived `BOCPD` runtime identity.

## 4. Data axis

Frozen research source artifact:

`gold_axis_2026/core5_monthly.csv.gz.b64`

Frozen field:

`gold_monthly`

Semantic:

monthly average gold price, used by the canonical CORE5 H=1 research target family.

Observation transform:

`x_t = ln(P_t / P_{t-1})`

Only completed monthly observations are eligible.

For a future month `t`, the state for `t` may be emitted only after the monthly price observation for `t` is complete and governed as available. Same-month hindsight use is prohibited.

## 5. Frozen windows

Development / fitting information:

`2010-01` through `2020-12`

Validation — untouched by fitting:

`2021-01` through `2023-12`

Locked replay — diagnostic only, no tuning:

`2024-01` through `2026-07`

2026 parameter tuning:

`NONE`

No result from validation or locked replay may change any V1 parameter or rule.

## 6. BOCPD recursion

Expected run length:

`L = 36 months`

Hazard:

`H = 1 / L`

This uses the Adams–MacKay constant-hazard case corresponding to a geometric/discrete-exponential gap prior.

No run-length tail pruning is used in V1. The full finite posterior vector is retained for deterministic research replay.

## 7. Observation model — new successor definition

V1 uses a univariate Gaussian segment model with unknown segment mean and variance and a Normal-Inverse-Gamma conjugate prior. The resulting one-step predictive distribution is Student-t.

Prior hyperparameters are estimated/frozen using **development data only**:

- `mu0 = mean(x_t)` on 2010-01..2020-12;
- `kappa0 = 1.0`;
- `alpha0 = 2.0`;
- `beta0 = sample_variance(x_t) * (alpha0 - 1)` on 2010-01..2020-12.

Interpretation:

- the development sample fixes location/scale before validation is inspected;
- `kappa0=1` gives one effective prior observation on the mean;
- `alpha0=2` supplies a weak finite-mean inverse-gamma variance prior;
- no validation/locked statistic enters the prior.

These hyperparameters are successor V1 design choices and are not attributed to the archived detector.

## 8. Successor score/state semantic

The archived numeric threshold `0.034027906134261016` is **not used** because archived score equivalence is not proven.

V1 does not introduce a fitted numeric alarm threshold.

At each completed month `t`:

- `prev_map_run = argmax P(r_{t-1} | x_{1:t-1})`;
- uninterrupted MAP growth would be `expected_run = prev_map_run + 1`;
- `map_run = argmax P(r_t | x_{1:t})`;
- `map_reset = map_run < expected_run`;
- `reset_fraction = max(0, (expected_run - map_run) / expected_run)`.

Adverse regime-break candidate:

`adverse_break_candidate = map_reset AND x_t < 0`

Output state:

- if true: `ADVERSE_BREAK_CANDIDATE`;
- otherwise: `NO_ADVERSE_BREAK_CANDIDATE`.

This is a **new V1 state semantic**. It must never be labelled as the archived BOCPD score or archived alarm.

## 9. Development-state handling

The NIG prior hyperparameters are frozen from the full development window only. The BOCPD recursion is then run sequentially from the first eligible return in 2010 through development, validation and locked replay.

Validation state at 2021-01 is therefore based only on the frozen V1 prior plus observations through 2020-12. Each later state is updated only with observations available through that month.

No state is initialized from validation or locked outcomes.

## 10. Required implementation outputs

Per month:

- month;
- completed-month log return;
- MAP run length;
- previous MAP run length;
- reset flag;
- reset fraction;
- MAP segment mean;
- run-length entropy;
- V1 state;
- evidence period: DEV / VAL / LOCK;
- evidence class: `HISTORICAL_REPLAY_SUCCESSOR_RESEARCH`.

Audit summary:

- data span and row counts;
- exact V1 prior hyperparameters;
- exact `L` / hazard;
- validation alarm count/rate;
- locked alarm count/rate;
- determinism hash;
- database writes = `NONE`.

Validation/locked alarm counts are descriptive evidence only in V1. They do not authorize tuning or production promotion.

## 11. Hard engineering gates

All must pass:

1. `CONTRACT_IDENTITY_PASS` — successor and archived identities are distinct.
2. `NO_ARCHIVED_THRESHOLD_REUSE_PASS`.
3. `DEVELOPMENT_ONLY_PRIOR_PASS`.
4. `POSTERIOR_NORMALIZATION_PASS` — each run-length posterior sums to one within numerical tolerance.
5. `DETERMINISM_PASS` — identical input/contract produces byte-stable canonical result payload/hash.
6. `PREFIX_INVARIANCE_PASS` — outputs through month `t` are unchanged when later months are appended.
7. `COMPLETED_MONTH_ONLY_PASS`.
8. `VALIDATION_NO_TUNING_PASS`.
9. `LOCKED_NO_TUNING_PASS`.
10. `DIRECTION_VOTE_FALSE_PASS`.
11. `DATABASE_WRITES_NONE_PASS`.
12. `NO_POSITION_MAPPING_PASS`.

A hard-gate failure leaves the successor `BLOCKED_RESEARCH_CANDIDATE`.

## 12. Promotion boundary

Passing V1 engineering/historical gates does **not** make the motor ACTIVE and does not change production runtime counts.

The maximum status after this change-control is:

`RESEARCH_SHADOW_CANDIDATE_ENGINEERING_PASS`

A future prospective run requires a separate issuer contract defining:

- eligible month-close origin;
- governed monthly input identity;
- immutable input snapshot/linkage;
- exact code SHA / rule version;
- evidence class `PROSPECTIVE_SHADOW`;
- persistence path;
- no direction vote;
- no automatic action.

`LIVE_PRODUCTION` remains out of scope.
