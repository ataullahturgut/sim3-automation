# OAR-RTE-H3 V1 — OPTIONS-AGAINST-AND-RISING REVERSAL ENGINE PREREGISTRATION

**Date:** 2026-10-04  
**Identity:** `OAR_RTE_H3_V1`  
**Branch:** `gold-h3-oar-rte-v1-20261004`  
**Status:** **PREREGISTERED BEFORE 2026 OPENING**

## 1. Mechanism

The common 2024/2025 H1→H2 state audit did not support a generic calendar continuation regime.

The repeated origin-state shift was instead in Gold options pressure:
- signed option-pressure level weakens in H2 in both years;
- signed change in option pressure also weakens in H2 in both years.

Earlier RTE V1 DEV diagnostics independently showed that the boolean state
`signed_opt_pressure > 0 AND signed_d_opt_pressure > 0`
was more frequent in true rescues than broken flips among high-tension candidates.

OAR-RTE therefore requires Gold options pressure to be:
1. against the prevailing 12h momentum, and
2. strengthening against that momentum.

## 2. Candidate rule

Use existing origin-safe RTE V1 scores/features.

Frozen threshold family:
`q ∈ [0.60, 0.65, 0.70]`

Candidate at origin t if all hold:
- `p_rte >= q`
- `p_inst >= 0.50`
- `signed_opt_pressure > 0`
- `signed_d_opt_pressure > 0`

Action:
flip V5 direction.

No regime clustering, no live prior correction, no additional path gate.

## 3. Development robustness

Development blocks:
- 2024 H1
- 2024 H2
- 2025 H1
- 2025 H2

Robust-eligible if:
- aggregate candidate count >=10
- aggregate net rescue >= +4
- aggregate rescue precision >=0.60
- candidate rate <=0.15
- at least 3 of 4 half-year blocks have net rescue >=0
- no half-year block has net rescue < -1

Selection:
1. maximum net rescue
2. higher precision
3. more rescued
4. lower candidate rate
5. higher q

No eligible q => `NO_ROBUST_OAR_RTE_RULE`; 2026 remains unopened.

## 4. 2026 final holdout

Only after development robustness PASS.

Selected q is frozen and applied once to 2026.

Report:
- candidates / rate
- rescued / broken / net
- rescue precision
- eligible V5 -> assisted accuracy
- whole-clean-2026 accuracy
- OPAL-no-candidate missed reversal coverage

No 2026 outcome may alter q or the dual options-pressure gate.

## 5. Governance

2024-2025 is complete development.  
The first independent OAR-RTE evaluation is 2026.  
HELIOS V5-DCE remains binding unless a later promotion decision is justified.
