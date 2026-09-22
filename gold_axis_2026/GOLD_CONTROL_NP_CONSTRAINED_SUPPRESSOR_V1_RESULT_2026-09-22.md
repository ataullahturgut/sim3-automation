# GOLD CONTROL — NP-CONSTRAINED SUPPRESSOR V1 RESULT

**Date:** 2026-09-22  
**Identity:** `NP_CONSTRAINED_SUPPRESSOR_V1_RESEARCH`  
**Preregistration:** `db782e19fa38fefb1fcace1366fa1d9b937991cf`  
**Scientific status:** `FORMAL_PASS_BUT_NP_GATE_NON_DISCRIMINATING`  
**Runtime authority:** NONE

## 1. NP calibration

The first cross-domain dampener was implemented as a Neyman-Pearson-style constrained suppressor.

Safety target:
- prioritized error = suppressing an actual DOWN;
- alpha = **0.20**;
- delta = **0.10**.

Calibration set:
- 2024 exact same-clock daily panel;
- 86 actual-DOWN rows.

Frozen suppression score:
- selected Router-V2 expert's one-sided 90% Wilson lower bound on historical UP precision;
- Router ABSTAIN = no suppression.

NP order-statistic result:
- n0 = 86;
- k = 74;
- binomial tail = **0.098998**;
- threshold `tau = 0.4302662741`.

Operational rule:
`SUPPRESS_DOWN` iff SQRT alarms, Router V2 emits UP, and score > tau.

## 2. 2024 calibration diagnostics

Across all 2024 daily rows:
- actual DOWN = 86;
- actual UP = 119;
- suppressed DOWN = 12;
- suppressed UP = 22;
- daily DOWN suppression rate = **13.95%**;
- suppression precision = **64.71%**.

On the 17 SQRT alarm origins:
- baseline = 7 true DOWN + 10 false forced-DOWN;
- suppressions = 4;
- good / bad = **3 / 1**;
- suppression precision = **75.00%**;
- false-alarm reduction = **30.00%**;
- true-DOWN retention = **85.71%**;
- remaining forced-DOWN precision = **46.15%**.

These 2024 SQRT numbers are calibration diagnostics, not independent validation.

## 3. Researcher-visible locked 2025 challenge

The 2024 threshold was frozen and applied unchanged.

SQRT baseline:
- alarms = 90;
- true DOWN = 45;
- false forced-DOWN = 45;
- baseline precision = 50.00%.

NP suppressor:
- suppressions = **16**;
- good suppressions = **10**;
- bad suppressions = **6**;
- suppression precision = **62.50%**;
- false-alarm reduction = **22.22%**;
- true-DOWN retention = **86.67%**;
- remaining forced-DOWN precision = **52.70%**;
- precision change = **+2.70 pp**.

On the full 2025 daily panel, actual-DOWN suppression rate was **10.31%**, below the alpha=20% target descriptively.

## 4. Critical finding

The NP threshold did **not** remove any additional Router-V2 veto.

All frozen Router-V2 UP scores that overlapped SQRT alarms were already above `tau`.

Therefore on the SQRT alarm subset:

> NP V1 = frozen hard Router-V2 veto.

2025 comparison:
- hard veto = 16 suppressions, 10 good / 6 bad;
- NP V1 = 16 suppressions, 10 good / 6 bad.

So the preregistered successor gate formally passes because NP V1 is no worse than the hard veto and preserves the safety constraint, but it provides **zero incremental operational improvement**.

## 5. Interpretation

This experiment is still useful.

It shows that the frozen Router V2 is already selective enough that a simple NP alpha=20% safety wrapper does not further prune its SQRT vetoes.

What NP V1 contributes is the correct asymmetric-risk framing:
- first constrain true-DOWN loss;
- then seek false-alarm removal.

What it does **not** provide is a better dampener.

The next method should therefore change the **action space**, not the UP verifier: use a separately preregistered selective controller with `RETAIN / WATCH / SUPPRESS` instead of another binary threshold on the same Router score.

## 6. Binding decision

`NP_CONSTRAINED_SUPPRESSOR_V1_RESEARCH = FORMAL_PASS_BUT_NP_GATE_NON_DISCRIMINATING / NO_INCREMENTAL_OPERATIONAL_GAIN / NOT_RUNTIME`

No threshold was changed after seeing 2025.
