# GOLD H3 — Latest Models Historical Contribution Audit

**Date:** 2026-10-05  
**Status:** SOURCE-LEVEL HISTORICAL CONTRIBUTION AUDIT COMPLETE — 2025 SOURCE BACKFILL INCORPORATED  
**Scope:** HELIOS V5-DCE, SAGE V2, RuleFlow V3-TG, DPTC Q95/Q99 and related competence layers.  
**Purpose:** Determine whether the latest intervention layers add value or damage the frozen baseline when replayed on historically available periods.

## 1. Interpretation rule

This audit separates:

- **exact historical replay/backcast**, where every mandatory input exists under the declared source contract;
- **partial historical evidence**, where the model can be tested only from the first date at which its mandatory state variables exist;
- **not testable**, where mandatory source inputs are absent and synthetic reconstruction would change the model identity.

For 2025, missing pre-snapshot IFBC/LLRS history is reconstructed only where the original source identity and equations can be reproduced. IFBC is bridged from the same Yahoo futures identities; LLRS is anchored to the archived original 2025 hourly raw panel, with same-source Yahoo history used only before that archive begins. Source-reproduction QA passed. No result is upgraded to prospective/OOS status.

For 2023, the exact source contract remains blocked: Yahoo 1h currently enforces a 730-day depth limit, the repository does not contain the required 2023 GC/SI/ZN/NQ/CL hourly futures archive, and the connected Twelve Data account did not expose a usable CME-futures bridge in the probe. No proxy result is substituted for exact DPTC.

## 2. Historical contribution matrix

| Layer | 2023 | 2024 | 2025 | 2026 | Historical conclusion |
|---|---|---|---|---|---|
| HELIOS V5-DCE | 156/219 = **71.23%** | 172/241 = **71.37%** in RuleFlow backcast authority | 165/248 = **66.53%** | 121/191 = **63.35%** | Strong historical base, but accuracy declines into 2026 regime. |
| RuleFlow V3-TG | 1 action: **0 rescue / 1 broken, net -1**; V5 71.23% -> 70.78% | 1 action: **0/1, net -1**; V5 71.37% -> 70.95% | Reconstruction QA: **5 actions, 5 rescue / 0 broken, net +5** on known 2025 evidence | Surviving topology-gated exception adds **+1** over SAGE V2: 125 -> 126 | Not universally beneficial; strongly state/regime dependent. |
| SAGE V2 exception-only | **NOT TESTABLE** — IFBC/LLRS source contract unavailable | **NOT TESTABLE** — IFBC/LLRS source contract unavailable | V5 165 -> 166, **net +1**; 3 OCS actions = 2 rescue / 1 broken | V5 121 -> 125, **net +4**; 4/4 rescues | Positive from available 2025 history, materially stronger in 2026. |
| SAGE V2 + RuleFlow V3-TG | **NOT EXACTLY TESTABLE** as full union because SAGE is unavailable | **NOT EXACTLY TESTABLE** as full union because SAGE is unavailable | Source-backfilled 2025 union: **171/248 = 68.95%**, BA **67.13%**; net **+6** vs V5 | 121 -> **126/191 = 65.97%**, BA 66.31%, net +5 vs V5 | Positive combined 2025/2026 retrospective reference; 2023-2024 full-union identity incomplete. |
| DPTC Q95 | **NOT TESTABLE** — exact 2023 IFBC/LLRS source state unavailable | **NOT TESTABLE** — exact historical source state not reconstructed | 2025 source-backfilled replay: **9 actions, 4 rescue / 5 broken, net -1**; 171 -> **170/248 = 68.55%**, BA **67.17%** | **13 actions, 11/2, net +9**; 126 -> **135/191 = 70.68%**, BA 70.86% | Slightly harmful in reconstructed 2025; very strong only in the 2026 competence regime. |
| DPTC Q99 | **NOT TESTABLE** — exact 2023 IFBC/LLRS source state unavailable | **NOT TESTABLE** — exact historical source state not reconstructed | 2025 source-backfilled replay: **8 actions, 3 rescue / 5 broken, net -2**; 171 -> **169/248 = 68.15%**, BA **66.65%** | **12 actions, 10/2, net +8**; 126 -> **134/191 = 70.16%**, BA 70.36% | More harmful than Q95 in reconstructed 2025; 2026 benefit remains regime-specific development evidence. |
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

The source-backfilled evidence now says:

- the earlier 2025 formation-only result (2 actions, 1 rescue / 1 broken, net 0) was **incomplete** because Handoff state started too late;
- after same-source historical reconstruction, the first complete 2025 Handoff state is **2025-03-03**;
- 2025 full replay: Q95 **4 rescue / 5 broken, net -1**; Q99 **3 rescue / 5 broken, net -2**;
- 2026 stress/development: **strongly positive** — Q95 net +9, Q99 net +8.

2025 source-reproduction QA passed:
- IFBC overlap: 280 rows; maximum raw-feature discrepancy approximately 1.1e-16;
- LLRS overlap: 332 rows; maximum score discrepancy approximately 1.43e-14;
- archived LLRS hourly panel begins 2025-01-02 05:00 UTC and is preserved from that timestamp onward.

This pattern is consistent with the design hypothesis that DPTC is a **competence-state controller**: it should activate Handoff only after the market's dependence/competence structure changes.

It does **not** prove that DPTC would have been positive in 2023-2024.

## 5. Why exact DPTC 2023-2024 is still not reported

The 2025 gap has now been reconstructed, but the same operation cannot currently be extended to 2023-2024 under the exact source identity.

Evidence:

- Yahoo's 1h chart endpoint currently rejects the required 2023/2024 ranges because 1h history must fall within the most recent **730 days**.
- The Git repository contains the archived original 2025 LLRS hourly panel but no corresponding 2023 GC/SI/ZN/NQ/CL hourly futures archive.
- The connected Twelve Data source was probed as an alternative bridge; the current symbol/search entitlement did not expose a usable CME-futures set for the five required channels.
- Databento publicly documents historical CME Globex data and continuous contracts and is a technically viable external acquisition route, but it is not connected to this project and therefore is not used in this audit.

A proxy or spot substitution would change the IFBC/LLRS model identity. Such a sensitivity study may be run separately, but it cannot be labeled exact DPTC historical replay.

## 6. Decision

The historical evidence changes the interpretation of the latest models:

1. **HELIOS V5-DCE remains the historical base/champion lineage.**
2. **SAGE V2 is additive on its available historical coverage** (+1 in 2025, +4 in 2026).
3. **RuleFlow is not safe as an unconditional override**; it damages 2023 and 2024 and becomes useful only under later gating/state conditions.
4. **DPTC is best classified as a regime/competence-conditioned controller**, not a universal reversal engine: it is mildly harmful in the source-backfilled 2025 replay but strongly positive in 2026 development.
5. DPTC Q95 and Q99 remain frozen prospective-testable challengers, but their 2026 strength must not be generalized to 2023-2024 without exact IFBC/LLRS reconstruction.
6. The strongest scientifically defensible statement is: **the combined SAGE/RuleFlow layer improves 2025 and 2026, but DPTC itself is mildly negative in reconstructed 2025 and strongly positive only in 2026 development; therefore DPTC's value is regime-dependent rather than universal.**

## 7. Source authority

This audit is derived from the existing frozen/result authorities:

- `GOLD_H3_RULEFLOW_V3_PRE2025_BACKCAST_RESULT_2026-10-04.md`
- `GOLD_H3_RULEFLOW_V3_PRE2025_BACKCAST_SUMMARY_2026-10-04.json`
- `GOLD_H3_SAGE_V1_CLOSURE_2026-10-04.md`
- `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_SUMMARY_2026-10-04.json`
- `GOLD_H3_DPTC_V1_SUMMARY_2026-10-05.json`
- `GOLD_H3_COMPETENCE_TRANSITION_PROGRAM_V1_SUMMARY_2026-10-05.json`
- `GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_SUMMARY_2026-10-05.json`
- `GOLD_H3_2025_BACKFILL_DPTC_RESULT_2026-10-05.md`
- `GOLD_H3_2025_BACKFILL_DPTC_SUMMARY_2026-10-05.json`
- `GOLD_H3_HOURLY_HISTORY_DEPTH_PROBE_2026-10-05.md`
- `GOLD_H3_2023_TWELVE_FUTURES_BRIDGE_PROBE_2026-10-05.md`

No threshold was changed and no result was selected using future outcomes during this audit.
