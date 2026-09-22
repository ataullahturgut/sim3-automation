# GOLD CONTROL — SELECTIVE THREE-ACTION CONTROLLER V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `SELECTIVE_THREE_ACTION_CONTROLLER_V1_RESEARCH`  
**Frozen parent risk model:** SQRT-HAR-DR annual-origin downside-risk alarm  
**Frozen verifier:** `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. Objective

Replace the binary hard-veto action with a selective three-action controller:

- `RETAIN_DOWN`
- `WATCH_DOWN`
- `SUPPRESS_DOWN`

The controller must preserve the frozen SQRT model and frozen Router V2. It changes only the downstream action applied to an SQRT alarm.

## 2. Frozen confidence score

For every daily origin where Router V2 emits `UP`:

`score = selected expert's one-sided 90% Wilson lower confidence bound on matured historical UP precision`.

If Router V2 emits `ABSTAIN`, score is unavailable and the action is `RETAIN_DOWN`.

No SQRT-alarm outcome, 2025 outcome, or post-hoc feature enters the score.

## 3. Two NP-style safety thresholds

Thresholds are calibrated from the **2024 full daily common panel**, using only actual-DOWN rows.

Use the same order-statistic construction as NP Suppressor V1.

### WATCH threshold

- prioritized-error target: `alpha_watch = 0.20`
- confidence: `1-delta = 0.90`, so `delta = 0.10`

Let `tau_watch` be the corresponding NP order-statistic threshold.

### SUPPRESS threshold

- prioritized-error target: `alpha_suppress = 0.10`
- confidence: `1-delta = 0.90`
- same construction, producing `tau_suppress`

These alpha values are fixed before calibration:
- WATCH is allowed at the project's historical 80% true-DOWN-retention safety floor;
- SUPPRESS requires the stricter 90% true-DOWN-retention target.

If either order-statistic threshold cannot be identified, status is `BLOCKED_INSUFFICIENT_CALIBRATION_SUPPORT`.

## 4. Frozen action rule

On a SQRT alarm origin:

1. if Router V2 = ABSTAIN -> `RETAIN_DOWN`
2. if Router V2 = UP and score <= tau_watch -> `RETAIN_DOWN`
3. if Router V2 = UP and tau_watch < score <= tau_suppress -> `WATCH_DOWN`
4. if Router V2 = UP and score > tau_suppress -> `SUPPRESS_DOWN`

Strict `>` is used conservatively at both thresholds.

`WATCH_DOWN` does **not** delete the SQRT alarm. It is a downgraded/uncertain state for research evaluation only.

## 5. Evaluation periods

### 2024
Calibration diagnostics only:
- threshold values;
- action counts over all daily rows;
- action anatomy on SQRT alarms.

### 2025
Researcher-visible locked challenge:
- apply both 2024 thresholds unchanged;
- no 2025 value may alter thresholds or action rules.

## 6. Metrics

On 2025 SQRT alarms report:

### SUPPRESS action
- suppressions;
- good suppressions;
- bad suppressions;
- suppression precision;
- false-alarm reduction;
- true-DOWN retention;
- remaining forced-DOWN precision.

### WATCH action
- watch count;
- actual-UP / actual-DOWN anatomy;
- watch UP rate;
- whether WATCH contains a mixed-risk region rather than a de facto suppress group.

### Overall triage
- RETAIN / WATCH / SUPPRESS counts;
- total fraction of SQRT alarms downgraded or suppressed;
- false-DOWN cases captured by WATCH+SUPPRESS;
- true-DOWN cases touched by WATCH+SUPPRESS.

## 7. Benchmarks

Compare with:
1. no dampener;
2. frozen hard Router-V2 veto;
3. NP Suppressor V1.

## 8. Decision rule

`SUPPORTED_AS_SELECTIVE_SUCCESSOR` only if 2025 satisfies all:

1. at least 3 SUPPRESS actions;
2. SUPPRESS precision >= hard-veto precision (62.5%);
3. SUPPRESS true-DOWN retention >= 0.90;
4. remaining forced-DOWN precision >= hard-veto remaining precision (52.70%);
5. false-alarm reduction > 0;
6. WATCH count >= 3, demonstrating a genuine middle action rather than a binary relabeling.

If SUPPRESS safety passes but WATCH count <3:
`SAFE_BUT_NOT_GENUINELY_THREE_ACTION`.

If SUPPRESS true-DOWN retention <0.90:
`SUPPRESS_SAFETY_FAILED`.

If SUPPRESS actions <3:
`TOO_CONSERVATIVE_INSUFFICIENT_SUPPRESS_SUPPORT`.

## 9. Forbidden actions

Do not:
- tune alpha_watch or alpha_suppress;
- tune delta;
- change Router V2;
- add SQRT alarm strength after seeing results;
- add GVZ, Macro Event, Emergency, or other overlays;
- convert WATCH into a suppression after seeing 2025;
- change score definition;
- use 2025 to alter thresholds;
- optimize on the SQRT alarm subset.

## 10. Governance

- no random split;
- matured-only Router V2 competence;
- no production writes;
- no runtime promotion.
