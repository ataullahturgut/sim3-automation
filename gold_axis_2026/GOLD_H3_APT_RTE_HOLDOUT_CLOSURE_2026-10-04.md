# GOLD H3 — APT-RTE HOLDOUT CLOSURE

**Date:** 2026-10-04  
**Identity:** `APT_RTE_H3_V1`  
**Status:** **PRE-2026 PASS / 2026 HOLDOUT FAIL / NOT PROMOTED**

## Pre-2026 development

APT-RTE encoded the strongest retrospective mechanism found in the reversal program:

- options pressure against 12h momentum;
- options pressure strengthening against that momentum;
- GC futures volume one-day change negative;
- GC futures volume acceleration negative;
- pRTE >= 0.60;
- pInst >= 0.50.

2024-2025:
- candidates: 15
- rescues: 10
- broken: 5
- net rescue: +5
- precision: 66.67%
- candidate rate: 3.68%
- half-year nets: +1 / +1 / +4 / -1

This passed the preregistered robustness gate.

## 2026 final holdout

The frozen rule was then opened once on 2026.

Result:
- eligible V5-continuation origins: 153
- APT candidates: 12
- rescues: 2
- broken: 10
- net rescue: **-8**
- rescue precision: **16.67%**
- OPAL-no-candidate missed reversals hit: 2/55

Whole clean 2026:
- HELIOS V5-DCE: 121/191 = **63.35%**
- hypothetical APT-assisted: 113/191 = **59.16%**

APT-RTE is therefore rejected for promotion.

## Scientific implication

The failure is a genuine out-of-sample regime break:
- a coherent 2024-2025 mechanism with positive block robustness did not transport to 2026;
- therefore retrospective reversal selectivity is not sufficient evidence for live override authority;
- raw Gold call/put volume pressure and futures-volume fade are not invariant enough to justify unconditional future flips.

## Holdout governance consequence

2026 outcomes have now been opened for APT-RTE.

Therefore:
- 2026 Jan-Sep may be used only as **post-holdout diagnostic/development** for successor architecture;
- no successor designed after this point may claim 2026 as an independent holdout;
- the next genuinely independent evaluation window is the prospective clean stream beginning with the already-governed `CLEAN_H3_PROSPECTIVE_V1` origins from 2026-10-05 onward.

## Binding next direction

Successor work should not search another retrospective flip threshold.

It should solve the demonstrated distribution-shift problem through:
1. explicit OOD / similarity gating against historically successful reversal states;
2. prospective shadow scoring;
3. trust activation only after matured prospective evidence;
4. fail-safe fallback to HELIOS V5 whenever reversal trust is unproven.

This turns reversal rescue from a permanently enabled retrospective rule into a **self-validating prospective specialist**.
