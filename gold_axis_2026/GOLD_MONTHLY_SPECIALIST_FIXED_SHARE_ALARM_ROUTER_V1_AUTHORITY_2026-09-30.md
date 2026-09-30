# GOLD MONTHLY — Specialist Fixed-Share Alarm Router V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / ONLINE SPECIALIST-EXPERT ROUTER

## 1. Objective

Prior work established four constraints:

1. alarm quality is non-stationary;
2. sparse alarms such as E must not be treated as failed simply because they were previously inactive;
3. hard reliability thresholds suppress too many genuine HIGH/MEDIUM events;
4. V2 may contain independent risk information in some eras but is not a universal risk gate.

This experiment tests an online specialist-expert architecture inspired by sleeping/specialist experts and Fixed-Share:

> each alarm is an expert that is updated only when it is active; expert weights may change through time; Fixed-Share allows previously weak experts to recover.

No raw alarm definition is changed.

## 2. Frozen source

Use:
- `GOLD_MONTHLY_ALARM_REGIME_V2_RELIABILITY_AUDIT_V1_2026-09-30.json`
- 58 common rows.

Specialist experts:
- A
- B
- C
- D
- E
- G
- H
- I1
- I2
- T1_WGC
- V2_TRANSITION

Awake rule:
- A..T1_WGC expert is awake iff the corresponding frozen signal is active at origin t;
- V2_TRANSITION expert is awake iff frozen `v2_transition_flag=true`.

A `NULL` expert is always awake and predicts no risk.

## 3. Two parallel binary tasks

### HIGH task
- y=1 iff target severity is HIGH;
- y=0 otherwise.

### ELEVATED task
- y=1 iff target severity is HIGH or MEDIUM;
- y=0 iff NORMAL.

HIGH is primary. ELEVATED is supporting.

## 4. Expert predictions

When awake:
- every alarm specialist predicts 1;
- NULL predicts 0.

Sleeping specialists abstain and are excluded from the current weighted vote.

At origin t:

`p_t = sum(weights of awake alarm experts) / (NULL weight + sum(weights of awake alarm experts))`

If no specialist is awake:
- `p_t = 0`.

The router therefore measures the online credibility mass of the currently active specialists against the always-awake no-risk expert.

## 5. Online update

Initial weights:
- every alarm expert = 1;
- NULL = 1.

Loss:
- binary 0/1 loss against the relevant task outcome.

Only awake alarm specialists are loss-updated.
NULL is updated every month.

For learning rate eta:

`w_i <- w_i * exp(-eta * loss_i)`

Sleeping alarm specialists are not penalized.

After each update, weights may be rescaled by a common positive constant for numerical stability; this does not change predictions.

## 6. Hedge and Fixed-Share candidates

### Specialist Hedge
- alpha = 0
- no sharing after multiplicative update.

### Specialist Fixed-Share
After loss update, alarm-expert weights only are mixed:

`w_i <- (1-alpha)*w_i + alpha*mean_alarm_weight`

NULL weight is not part of the share pool.

This lets previously weak/sleeping experts recover over time without transferring NULL credibility into alarm experts.

## 7. Frozen candidate grid

Learning rate:
- eta in {0.25, 0.50, 1.00, 2.00}

Fixed-Share alpha:
- {0.01, 0.05, 0.10, 0.20}

Hedge:
- alpha = 0

Decision threshold tau:
- {0.25, 0.35, 0.45, 0.50, 0.60}

Total:
- Hedge: 4 x 5 = 20
- Fixed-Share: 4 x 4 x 5 = 80
- total = 100 HIGH-router candidates.

No candidate may be added after results.

## 8. Chronology and pre-2025 selection

All 58 rows are processed chronologically.

At each origin:
1. predict using weights based only on earlier realized rows;
2. record the prediction;
3. only then update weights using the current target outcome.

Candidate selection uses only target months:
- 2022-04..2024-12.

Rows before DEV may initialize the online weights if chronologically earlier.

2025/2026 are forbidden from candidate selection.

## 9. Primary router decision

For a candidate:
- WARN iff `p_HIGH >= tau`.

This may:
- retain a raw alarm;
- suppress a raw false alarm;
- create an independent warning when V2 is the only awake specialist.

The threshold is selected only from the frozen pre-2025 grid.

## 10. Primary DEV selection rule

Reference:
- raw `ANY_VISIBLE` on DEV.

A candidate is eligible only if:

1. overall HIGH recall >= **90%**;
2. raw-ANY HIGH-hit retention >= **90%**;
3. it does not miss any HIGH month that raw ANY_VISIBLE hit if such a miss would push raw-hit retention below 90%.

Because DEV raw ANY has 8 HIGH hits, 90% effectively requires retaining all 8/8.

Among eligible candidates select lexicographically:

1. maximum false-call reduction vs raw ANY_VISIBLE;
2. maximum MEDIUM hits;
3. maximum useful-call rate;
4. minimum HIGH-task Brier;
5. minimum HIGH-task log loss;
6. prefer Fixed-Share over Hedge if otherwise tied;
7. lexical candidate id.

No 2025/2026 information enters selection.

## 11. Evidence-strength diagnostics

For every active specialist before update report:
- prior awake-event count;
- prior HIGH-hit count;
- prior ELEVATED-hit count;
- current HIGH weight;
- current ELEVATED weight.

Evidence tier:
- EMERGING: prior awake events <3
- DEVELOPING: 3..5
- ESTABLISHED: >=6

Evidence tier does not directly suppress a signal in V1.

This specifically protects interpretation of sparse experts such as E and G.

## 12. Baselines

Report:
- raw ANY_VISIBLE;
- raw T0_STANDARD;
- V2_TRANSITION alone;
- best Specialist Hedge candidate;
- selected overall Specialist Hedge/Fixed-Share candidate.

Also report all-grid eligibility counts.

## 13. Opened 2025-2026 transport

After selecting the candidate using pre-2025 DEV only:

- freeze eta, alpha, tau and algorithm;
- rerun the online process from the beginning;
- allow sequential updating after each realized 2025/2026 outcome;
- do not change parameters.

Report separately:
- 2025
- 2026 Jan-Aug
- combined 2025-2026.

Opened data cannot rescue a failed DEV result.

## 14. Candidate promotion gate

The selected router is only a later operational candidate if DEV satisfies all:

1. HIGH recall >=90%;
2. raw-ANY HIGH-hit retention >=90%;
3. false-call reduction vs raw ANY >=20%;
4. useful-call rate > raw ANY useful-call rate.

If no grid candidate satisfies the eligibility constraints, status = NO_ELIGIBLE_CANDIDATE.

If selected candidate fails promotion, no post-hoc tuning is allowed.

## 15. Governance

Forbidden:
- modifying raw alarms;
- retuning V2;
- using regime labels in the router;
- using 2025/2026 for eta/alpha/tau selection;
- adding grid values after results;
- post-hoc threshold search;
- forecast correction;
- model switching.

This V1 isolates the specialist/FIxed-Share hypothesis.
