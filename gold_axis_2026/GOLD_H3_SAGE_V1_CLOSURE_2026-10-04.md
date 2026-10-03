# SAGE-H3 V1 — SELECTIVE ACTION / GUARDED EXCEPTION CLOSURE

**Date:** 2026-10-04  
**Branch:** `gold-h3-sage-v1-20261004`  
**Binding champion:** HELIOS V5-DCE  
**Historical status:** development only

## 1. Frozen V1 architecture

SAGE V1 separated two mechanisms:

- TRES Stage-1 probabilities for KEEP vs ABSTAIN;
- OCS q=0.70 / 0.10 orthogonal concurrence as the only FLIP exception.

OCS condition:
- IFBC count60 >= 4
- IFBC score >= 0.70
- LLRS external-opposes = True
- LLRS incremental > 0
- LLRS pressure >= 0.10

TRES continuation-safe:
`F_continuation >= max(F_reversal, S3)`.

Action hierarchy:
- existing V5 non-momentum call -> KEEP;
- OCS exception -> FLIP;
- otherwise TRES continuation-safe -> KEEP;
- otherwise ABSTAIN.

## 2. Integrity

Common mature rows:
- **252**

Coverage:
- 2025-07-01 maturity boundary through 2026-09-24.

Integrity:
- source identity mismatches: **0**
- leakage failures: **0**

## 3. OCS exception result

Across the mature common universe:
- FLIP candidates: **7**
- rescue / broken / net: **6 / 1 / +5**
- precision: **85.71%**

Half-year:
- 2025 H2: 2 / 1 / **+1**
- 2026 H1: 2 / 0 / **+2**
- 2026 H2: 2 / 0 / **+2**

Every mature block had positive net rescue.

## 4. TRES abstention result

SAGE V1 selective action:
- KEEP: 208
- ABSTAIN: 37
- coverage: **85.32%**
- selective action accuracy: **67.91%**
- counterfactual V5 accuracy inside ABSTAIN rows: **72.97%**

Therefore the TRES argmax continuation governor abstained on rows where V5 was, on average, **more accurate** than on acted rows.

This fails the purpose of selective abstention.

SAGE V1 development gate therefore fails:
`SAGE_H3_V1_FAIL`.

## 5. Full-direction effect of the OCS exception only

If ABSTAIN is removed and every non-OCS row simply keeps V5:

### 2025
- V5: 165 / 248 = **66.53%**
- V5 + OCS exception: 166 / 248 = **66.94%**
- exception rescue / broken / net: **2 / 1 / +1**

### 2026
- V5: 121 / 191 = **63.35%**
- V5 + OCS exception: 125 / 191 = **65.45%**
- exception rescue / broken / net: **4 / 0 / +4**

On the common mature 252-row universe:
- V5: **66.67%**
- V5 + OCS exception: **68.65%**

## 6. Interpretation

The experiment supports a mechanism-specific conclusion:

### Retain
**OCS rare orthogonal exception.**

Internal futures-flow breakdown and external cross-asset lead-lag concurrence together produced a small but high-specificity reversal signal.

### Reject
**TRES argmax abstention governor.**

TRES remains useful as a research risk representation, but the tested KEEP/ABSTAIN mapping did not concentrate V5 errors.

## 7. Statistical caution

The OCS evidence is small:
- only 7 mature FLIP events in the common development universe;
- the q=0.70 / 0.10 configuration was identified during prior OCS development;
- historical 2026 was already available during model development.

Therefore the 2026 +4 net result is **retrospective development evidence, not a clean holdout**.

No production promotion is justified from these historical results.

## 8. Binding next action

Freeze an **exception-only prospective shadow challenger**:

- baseline = HELIOS V5-DCE;
- no TRES direction override;
- no TRES abstention;
- flip only on the frozen OCS concurrence;
- otherwise keep V5 unchanged.

This is the most parsimonious surviving intervention rule after the broader reversal research program.

A separate prospective freeze is required before post-2026-10-04 use.
