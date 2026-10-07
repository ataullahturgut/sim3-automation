# GOLD SESSION — ROLE-AWARE MODEL EVALUATION AUTHORITY

**Date:** 2026-10-07  
**Status:** BINDING / SUPERSEDES BINARY PROMOTE-OR-REJECT INTERPRETATION

## Why this authority exists

The corrected session-model replay used a frozen 30% minimum-class-recall floor and other confirmation gates to decide whether a model could be promoted as a **stand-alone balanced direction engine**.

That gate remains useful for the primary-model question.

However, interpreting failure of that gate as:

`model is useless / delete from consensus pool`

is too strong.

A model may be deliberately asymmetric and still carry useful information for:
- UP detection;
- DOWN detection;
- reversal/correction;
- calibration;
- disagreement/error-diversity routing.

Therefore the project moves from one binary promotion label to a role-aware evaluation framework.

---

## 1. Probability decision threshold is unchanged

The ordinary direction threshold remains:

`p(UP) >= 0.50 -> UP; otherwise DOWN`

unless a model's historical identity explicitly defines another output semantics, such as a reversal specialist with a frozen intervention threshold.

This authority does **not** introduce a new UP-recall, DOWN-recall or confidence threshold.

In particular:

- 70% UP recall is **not** a new hard gate;
- 30% minimum class recall is **not** a universal deletion rule.

---

## 2. The 30% class-recall floor has one specific meaning

The frozen minimum-class-recall floor remains binding only for:

### PRIMARY / BALANCED promotion

Question:

> Can this model be used as a stand-alone two-class session direction engine?

For that question, severe collapse of either class remains disqualifying.

Failure of this floor means:

`NOT_PRIMARY_BALANCED`

It does **not** automatically mean:

`NOT_SPECIALIST`

or

`REMOVE_FROM_CONSENSUS_RESEARCH`.

Any earlier authority wording that says a variant was "rejected" solely because one class recall fell below 30% must now be read narrowly as:

> rejected for balanced/primary promotion.

---

## 3. Role taxonomy

Every completed model/session head may receive one or more of the following tags.

### A. PRIMARY_BALANCED_CANDIDATE

A model that has useful two-class performance and is suitable to be considered as a stand-alone direction head.

Primary evaluation:
- Accuracy
- Balanced Accuracy
- UP recall
- DOWN recall
- Brier / probability quality
- stability across development years

### B. UP_SPECIALIST_CANDIDATE

A model/head that is materially informative for UP events even if DOWN recall is weak.

The role is not awarded from a single transport percentage alone. Evidence must include:
- development-period one-sided skill;
- chronological stability;
- incremental information versus other UP-oriented candidates.

### C. DOWN_SPECIALIST_CANDIDATE

Symmetric definition for DOWN events.

### D. CORRECTION_REVERSAL_SPECIALIST

A model whose job is not to predict every row, but to improve another expert on a restricted subset.

Required reporting:
- intervention count
- rescued errors
- broken correct calls
- net rescue
- before/after BA
- before/after class recalls
- Brier change

RIFT, VEGA and OPAL belong to this family by identity even when a specific transport result is negative.

### E. CALIBRATION_ONLY_CANDIDATE

Direction calls may remain unchanged while Brier/log-loss improves.

This role may be useful for probability weighting but does not earn an extra direction vote by itself.

### F. ROUTER_STATE_EVIDENCE

SENTRY, DART and AURORA state/posterior histories may be useful as routing/context evidence even when the router itself is not a promoted primary model.

### G. NEGATIVE_CONTROL / NON-INCREMENTAL

A model may be preserved as evidence but excluded from final voting when it:
- produces no interventions;
- is effectively identical to an existing expert;
- adds no incremental disagreement value;
- or consistently harms the relevant specialist objective.

---

## 4. Development versus transport

The project chronology remains:

- 2022: governed warm-up where required
- 2023–2024: development, architecture and **role freeze**
- 2025: frozen transport
- 2026: unopened retrospective stress

### Binding rule

**Specialist membership and role definition must be rebuilt/frozen from 2023–2024 evidence only.**

The already-observed 2025 results may:
- confirm a frozen role;
- fail to transport;
- quantify degradation;
- remain descriptive evidence.

They may **not** be used to invent a new threshold, feature subset, role rule or consensus membership and then still be described as untouched 2025 holdout evidence.

If a later analysis deliberately uses 2025 to design membership, that analysis must be labelled retrospective/model-selection and 2025 loses holdout status for that specific architecture.

---

## 5. Existing results that motivated the correction

These examples are descriptive evidence and do not themselves redefine membership.

### Strong balanced/window-specific heads

- Model-01 CORE3, Sobti Asia Afternoon frozen 2025:
  - BA 61.58%
  - UP recall 58.12%
  - DOWN recall 65.04%

- Model-05 canonical Structural-IRIS, Sobti Asia Morning frozen 2025:
  - BA 60.86%
  - UP recall 64.18%
  - DOWN recall 57.53%

- Model-04B selected PATH_GLOBAL, WGC Asia frozen 2025:
  - BA 59.21%
  - UP recall 75.86%
  - DOWN recall 42.55%
  - Brier 0.2461

- Model-09B selected A1_PATH_SESSION, Sobti NY/London frozen 2025:
  - BA 52.73%
  - UP recall 41.98%
  - DOWN recall 63.49%
  - incremental BA +6.88 pp versus its exact matched A1+PATH comparator

These remain important window-specific primary/challenger evidence.

### One-sided evidence that must no longer be deleted merely by the 30% floor

Examples from already-frozen 2025 diagnostics include:

- selected PATH_GLOBAL, Sobti Europe:
  - UP recall 77.11%
  - DOWN recall 21.31%

- selected PATH_GLOBAL, Sobti Late-US:
  - UP recall 79.10%
  - DOWN recall 25.00%

- selected PATH_GLOBAL, WGC Europe:
  - UP recall 78.75%
  - DOWN recall 24.62%

- selected Structural-IRIS, Sobti Europe:
  - UP recall 84.34%
  - DOWN recall 4.92%

- selected Structural-IRIS, Sobti Late-US:
  - UP recall 92.54%
  - DOWN recall 10.00%

- selected Structural-IRIS, WGC Asia:
  - UP recall 81.03%
  - DOWN recall 13.04%

- SENTRY, Sobti Europe frozen 2025:
  - UP recall 75.90%
  - DOWN recall 22.95%

These heads are **not primary/balanced models**.

But the existence of strong one-sided recall means they must remain visible in the specialist evidence inventory until a development-only incremental-value analysis determines whether they add information beyond correlated experts.

### Correction specialist example

Canonical OPAL, WGC Europe frozen 2025:
- AURORA BA 51.59% -> OPAL BA 52.64%
- DOWN recall 36.92% -> 41.54%
- 13 interventions
- 7 rescues
- 6 breaks
- net rescue +1

This remains a valid correction-specialist challenger.

### Negative / non-incremental examples

- VEGA WGC US frozen 2025:
  - zero overrides
  - zero rescues
  - zero breaks
  - no metric change

- AURORA Sobti Europe frozen 2025:
  - identical to PATH_GLOBAL because it remained in PATH state

Such models/states remain evidence, but duplicate/non-incremental outputs must not be counted as independent consensus votes.

---

## 6. Consensus governance

Final consensus must be **session-specific and role-aware**.

It must not be a simple majority vote over every surviving artifact.

Before any consensus is scored, create a frozen 2023–2024 role matrix for every session:

| Model/head | Primary | UP specialist | DOWN specialist | Correction | Calibration | Router evidence | Incremental/duplicate status |
|---|---|---|---|---|---|---|---|

### Independence / duplicate control

Two highly correlated or mechanically nested models must not automatically receive two full votes.

Examples:
- AURORA that remains PATH for the whole evaluation interval is not an independent PATH vote.
- a selected feature variant and its canonical parent may be alternative representations, not two independent experts.
- a correction specialist contributes only when its intervention condition is active.

### Specialist contribution

UP/DOWN specialist value must be assessed by development-only incremental evidence such as:
- conditional precision/recall when the specialist disagrees with the primary;
- rescue minus break count;
- disagreement lift;
- incremental log-loss/Brier or class-specific loss;
- stability across 2023 and 2024.

No arbitrary 70% threshold is introduced.

---

## 7. Interpretation of earlier authority documents

Earlier model authority files remain valid for:
- target/data identity;
- feature identity;
- clock safety;
- exact metrics;
- primary/balanced promotion decisions;
- frozen transport outcomes.

This authority supersedes only overly broad wording such as:

- "reject model"
- "remove from candidate set"
- "not promoted"

when that wording was based solely on balanced-primary criteria.

The corrected interpretation is:

- `NOT_PROMOTED_PRIMARY`
- specialist role remains to be evaluated separately unless the model has explicit negative/non-incremental evidence.

---

## 8. Immediate execution order

Do **not** jump directly into HELIOS yet.

First:

1. build a **2023–2024 role matrix** for all completed session models and specialists;
2. tag UP/DOWN/correction/calibration/router roles without using 2025 for membership selection;
3. identify duplicate/nested experts;
4. freeze the role matrix;
5. then continue remaining model-family work, including HELIOS, under the same role-aware governance;
6. after all families are complete, build the session-specific consensus from the frozen role inventory.

This preserves the useful asymmetric models instead of discarding them while maintaining leakage-safe research governance.
