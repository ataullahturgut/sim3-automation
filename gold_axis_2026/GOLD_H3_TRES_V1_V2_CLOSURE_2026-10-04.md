# GOLD H3 — TRES V1 / V2 TRANSITION-SURVIVAL CLOSURE

**Date:** 2026-10-04  
**Branch:** `gold-h3-tres-v1-20261004`  
**Binding direction champion:** **HELIOS V5-DCE**  
**TRES intervention status:** **NOT PROMOTED**

## 1. Objective

Reformulate the reversal problem away from a single terminal H3 binary label and test whether path-event timing creates stable information that can repair HELIOS V5 continuation errors.

## 2. Stage 0 — timeline / event semantics

Frozen daily-price path:
- origin = feature_cutoff_date;
- H1/H2/H3 = next 1st/2nd/3rd available frozen Gold observations;
- primary barrier = 1.00 × origin-safe sigma20;
- momentum-normalized cumulative path.

Integrity result:
- panel rows: **1,029**
- audited rows: **1,029**
- failures: **0**
- max target_r3 identity error: **9.975e-17**

Primary first-passage counts:
- continuation 550
- reversal 205
- censored 274.

Terminal H3 reversal conditional on first-passage state:
- first-passage REVERSAL: **96.59%**
- first-passage CONTINUATION: **10.18%**
- CENSORED: **46.35%**

Stage 0: **PASS**.

## 3. Stage 1 — discrete competing-risk survival

Low-capacity monthly expanding multinomial hazard model.

No leakage:
- cumulative-incidence identity failures: **0**
- maturity leakage failures: **0**

Out-of-sample replay:
- predictions: **679**
- 2024-01-02 .. 2026-09-24.

Aggregate F_reversal top-vs-bottom quintile:
- first-passage reversal: **4.41% -> 34.56%**
- separation: **+30.15 pp**
- terminal H3 reversal: **20.59% -> 52.94%**
- separation: **+32.35 pp**.

Half-year terminal-reversal separation:
- 2024 H1 +50.0 pp
- 2024 H2 +40.0 pp
- 2025 H1 +45.8 pp
- 2025 H2 +19.2 pp
- 2026 H1 +23.1 pp
- 2026 H2 +15.4 pp.

All six blocks retained the correct sign.

Stage 1:
`TRES_EVENT_SIGNAL_PASS`.

**Binding positive finding:** origin-time state contains a stable signal about future path-event type and terminal reversal risk.

## 4. Stage 2 — V5 error-risk stacking

Only prior out-of-sample Stage-1 survival predictions were permitted into the meta-model.

No maturity leakage.

Baseline vs survival-augmented V5 error-risk:
- ROC AUC: **0.5595 -> 0.5552**
- Brier: **0.2332 -> 0.2355**
- log loss: **0.6673 -> 0.6730**
- augmented top-bottom error separation: **+8.05 pp**.

Status:
`NO_INCREMENTAL_TRES_ERROR_RISK`.

The second logistic stacking layer degraded the survival signal.

## 5. Direct survival diagnostic

Within the V5-continuation eligible universe:
- 561 origins
- identity check: V5 wrong == terminal reversal, mismatches **0**.

Direct scores:
- F_reversal AUC **0.6194**
- cause-share AUC **0.6138**
- cause-dominance AUC **0.6030**.

F_reversal bottom/top quintile V5 error:
- **19.47% -> 40.71%**
- separation **+21.24 pp**.

On the exact narrower Stage-2 scoring universe:
- p_error_aug AUC **0.5552**
- direct F_reversal AUC **0.6033**.

Interpretation:
the survival representation is useful; the extra meta-classifier is not.

However direct F_reversal is not fully stable for V5 rescue:
- 2025 H2 separation +4.5 pp
- 2026 H1 separation 0.0 pp.

Therefore it is not sufficient as a standalone reversal override.

## 6. Path-sequence diagnosis — absorbing-risk flaw

The absorbing first-passage abstraction discards later crossovers.

At fixed 1.00×sigma20:

- C_ONLY: n=527, terminal reversal **6.45%**
- R_ONLY: n=199, terminal reversal **99.50%**
- C_THEN_R: n=23, terminal reversal **95.65%**
- R_THEN_C: n=6, terminal reversal **0.00%**
- NONE: n=274, terminal reversal **46.35%**.

Using the latest decisive barrier state:
- CONTINUATION_LAST: n=533, terminal reversal **6.38%**
- REVERSAL_LAST: n=222, terminal reversal **99.10%**
- UNRESOLVED: n=274, terminal reversal **46.35%**.

This is a strong physical/path representation and a principled three-state uncertainty geometry.

## 7. TRES V2 — last-decisive path-state governor

A low-capacity multinomial model predicted:
- mu_R = P(REVERSAL_LAST)
- mu_C = P(CONTINUATION_LAST)
- mu_U = P(UNRESOLVED).

Frozen action:
- never touch V5 if V5 already disagrees with momentum;
- if V5 follows momentum, FLIP only when mu_R is the largest of the three memberships.

Replay:
- V5-continuation eligible: **561**
- flips: **35 (6.24%)**
- rescue / broken / net: **15 / 20 / -5**
- FLIP precision: **42.86%**
- V5 accuracy **67.30%**
- assisted accuracy **66.57%**.

Block net:
- 2024 H1 +1
- 2024 H2 -1
- 2025 H1 +4
- 2025 H2 **-6**
- 2026 H1 -2
- 2026 H2 -1.

Status:
`TRES_V2_PATH_GOVERNOR_FAIL`.

No prospective FLIP challenger is authorized.

## 8. Scientific conclusion

The work separates two questions that must no longer be conflated.

### Retain

**Event/path representation is valuable.**

Stage 1 is one of the most stable reversal-risk signals found in the project:
- correct sign across all six half-year blocks;
- large aggregate terminal-reversal separation;
- zero timeline/leakage failures.

### Reject

**Current intervention mapping is not valuable.**

Rejected:
- second V5 error-risk logistic stacking;
- simple argmax last-state FLIP governor.

The main remaining difficulty is not recognizing reversal-prone path states in aggregate; it is identifying which reversal-prone state should be allowed to overturn an already-strong V5 continuation call.

## 9. Implication for fuzzy / uncertainty work

The last-state representation gives a principled uncertainty tuple:

- reversal evidence = mu_R
- continuation evidence = mu_C
- unresolved evidence = mu_U.

This is superior to inventing fuzzy memberships from arbitrary transforms.

But V2 shows that `argmax(mu_R)` is not a safe FLIP rule.

Therefore any later Picture / Neutrosophic governor should initially use the tuple for:
- confidence damping,
- abstention,
- conflict measurement,

not automatic direction reversal.

A later FLIP rule requires new independent evidence beyond these three path-state probabilities.

## 10. Governance

- historical 2026 is development/stress-test only.
- no threshold was tuned on historical results in TRES V1/V2.
- the 1.00×sigma20 barrier remains frozen.
- HELIOS V5-DCE remains binding.
- Stage-1 survival outputs may be retained as auxiliary features / diagnostics.
- TRES V2 is not promoted.
