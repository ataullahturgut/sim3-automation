# GOLD H3 — Latest Models Historical Contribution Audit

**Date:** 2026-10-05  
**Status:** SOURCE-LEVEL HISTORICAL CONTRIBUTION AUDIT COMPLETE  
**Scope:** HELIOS V5-DCE, SAGE V2, RuleFlow V3-TG, DPTC Q95/Q99 and related competence layers.  
**Purpose:** Determine whether the latest intervention layers add value or damage the frozen baseline when replayed on historically available periods.

## 1. Interpretation rule

This audit separates:

- **exact historical replay/backcast**, where every mandatory input exists under the declared source contract;
- **partial historical evidence**, where the model can be tested only from the first date at which its mandatory state variables exist;
- **not testable**, where mandatory source inputs are absent and synthetic reconstruction would change the model identity.

No missing IFBC/LLRS history is imputed. No result is upgraded to prospective/OOS status.

## 2. Historical contribution matrix

| Layer | 2023 | 2024 | 2025 | 2026 | Historical conclusion |
|---|---|---|---|---|---|
| HELIOS V5-DCE | 156/219 = **71.23%** | 172/241 = **71.37%** in RuleFlow backcast authority | 165/248 = **66.53%** | 121/191 = **63.35%** | Strong historical base, but accuracy declines into 2026 regime. |
| RuleFlow V3-TG | 1 action: **0 rescue / 1 broken, net -1**; V5 71.23% -> 70.78% | 1 action: **0/1, net -1**; V5 71.37% -> 70.95% | Reconstruction QA: **5 actions, 5 rescue / 0 broken, net +5** on known 2025 evidence | Surviving topology-gated exception adds **+1** over SAGE V2: 125 -> 126 | Not universally beneficial; strongly state/regime dependent. |
| SAGE V2 exception-only | **NOT TESTABLE** — IFBC/LLRS source contract unavailable | **NOT TESTABLE** — IFBC/LLRS source contract unavailable | V5 165 -> 166, **net +1**; 3 OCS actions = 2 rescue / 1 broken | V5 121 -> 125, **net +4**; 4/4 rescues | Positive from available 2025 history, materially stronger in 2026. |
| SAGE V2 + RuleFlow V3-TG | **NOT EXACTLY TESTABLE** as full union because SAGE is unavailable | **NOT EXACTLY TESTABLE** as full union because SAGE is unavailable | Full-union score not declared from source authority; do not infer by adding separate nets | 121 -> **126/191 = 65.97%**, BA 66.31%, net +5 vs V5 | Useful 2026 retrospective reference; earlier full-union identity incomplete. |
| DPTC Q95 | **NOT TESTABLE** — canonical Handoff IFBC/LLRS state absent | **NOT TESTABLE** — canonical Handoff IFBC/LLRS state absent | Exact formation slice: **2 actions, 1 rescue / 1 broken, net 0** | **13 actions, 11/2, net +9**; 126 -> **135/191 = 70.68%**, BA 70.86% | No evidence of 2025 damage on exact available formation slice; very strong 2026 regime benefit. |
| DPTC Q99 | **NOT TESTABLE** — canonical Handoff IFBC/LLRS state absent | **NOT TESTABLE** — canonical Handoff IFBC/LLRS state absent | Exact formation slice: **2 actions, 1/1, net 0** | **12 actions, 10/2, net +8**; 126 -> **134/191 = 70.16%**, BA 70.36% | Same qualitative result as Q95 with slightly lower 2026 coverage. |
| BOCPD V4 | Not part of a frozen pre-2026 historical replay | Not part of a frozen pre-2026 historical replay | Development/formation input only | 10 actions, 8/2, **net +6**; 126 -> 132/191 = 69.11% | Strong 2026 competence-state evidence, post-hoc. |
| STCR | Not testable as the later synthesis | Not testable as the later synthesis | SELLR formation used for trigger selection; persistence synthesis is later | 11 actions, 9/2, **net +7**; 126 -> 133/191 = 69.63% | Strong 2026 synthesis; not an independent historical validation. |

## 3. Important negative evidence

The latest mechanisms must not be interpreted as permanently active reversal rules.

RuleFlow V3-TG is the clearest counterexample:

- 2023: one action, **BROKEN**, net -1;
- 2024: one action, **BROKEN**, net -1;
- 2025: the reconstructed 2025 evidence is strongly positive;
- 2026: the topology gate removes the four known Q2-Q3 RuleFlow V2 failures and retains one complementary rescue.

Therefore the mechanism's usefulness changes by state/regime.

## 4. DPTC-specific result

DPTC is not supported as a universal always-on rule.

The exact evidence currently says:

- 2025 formation: **neutral** — 2 actions, 1 rescue / 1 broken, net 0;
- 2026 stress/development: **strongly positive** — Q95 net +9, Q99 net +8.

This pattern is consistent with the design hypothesis that DPTC is a **competence-state controller**: it should activate Handoff only after the market's dependence/competence structure changes.

It does **not** prove that DPTC would have been positive in 2023-2024.

## 5. Why exact DPTC 2023-2024 is not reported

The canonical Handoff/DPTC state requires the frozen internal/external state inputs used by SAGE/Handoff:

- IFBC frozen snapshot begins **2025-05-09**;
- LLRS frozen snapshot begins **2025-02-07**.

The repository contains older target history, HELIOS/V5 calls, cross-asset topology and several CME daily sources, but it does not contain the original 2023-2024 raw IFBC/LLRS inputs or a reproducible source artifact that can recreate the exact frozen IFBC/LLRS state.

Consequently an apparent 2023/2024 DPTC score would require replacing missing state variables with proxies or synthetic values. That would be a different model and is prohibited in this audit.

## 6. Decision

The historical evidence changes the interpretation of the latest models:

1. **HELIOS V5-DCE remains the historical base/champion lineage.**
2. **SAGE V2 is additive on its available historical coverage** (+1 in 2025, +4 in 2026).
3. **RuleFlow is not safe as an unconditional override**; it damages 2023 and 2024 and becomes useful only under later gating/state conditions.
4. **DPTC is best classified as a regime/competence-conditioned controller**, not a universal reversal engine.
5. DPTC Q95 and Q99 remain frozen prospective-testable challengers, but their 2026 strength must not be generalized to 2023-2024 without exact IFBC/LLRS reconstruction.
6. The strongest scientifically defensible statement is: **latest layers add clear value in the 2026 competence regime, are neutral-to-positive on available 2025 evidence, and at least one component (RuleFlow) is demonstrably harmful when transported unconditionally to 2023-2024.**

## 7. Source authority

This audit is derived from the existing frozen/result authorities:

- `GOLD_H3_RULEFLOW_V3_PRE2025_BACKCAST_RESULT_2026-10-04.md`
- `GOLD_H3_RULEFLOW_V3_PRE2025_BACKCAST_SUMMARY_2026-10-04.json`
- `GOLD_H3_SAGE_V1_CLOSURE_2026-10-04.md`
- `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_SUMMARY_2026-10-04.json`
- `GOLD_H3_DPTC_V1_SUMMARY_2026-10-05.json`
- `GOLD_H3_COMPETENCE_TRANSITION_PROGRAM_V1_SUMMARY_2026-10-05.json`
- `GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_SUMMARY_2026-10-05.json`

No threshold was changed and no result was selected using future outcomes during this audit.
