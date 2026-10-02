# HELIOS-H3 V1 — HIERARCHICAL EVIDENCE-LOSS INFORMED ONLINE SWITCHING

**Date:** 2026-10-03
**Identity:** `HELIOS_H3_V1_RESEARCH`
**Parent:** `AURORA_H3_V1_RESEARCH`
**Frozen expert inputs:** RIFT-H3 V1, TURN-H3 V1, VEGA-H3 V1, OPAL-H3 V1
**Status:** PREREGISTERED / POST-HOC STRENGTHENING RESEARCH

## 1. Objective

OPAL found strong 2025-2026 reversal information but was harmful in 2023. HELIOS does not append regime variables directly to AURORA. It uses regime information only to decide whether a residual reversal expert is allowed to intervene.

This follows the regime-gated residual mixture-of-experts principle: protect the base forecast and route residual corrections only when the correction expert has demonstrated recent competence.

## 2. Independent reversal-evidence requirement

At origin t define a candidate reversal only if:

1. OPAL-H3 V1 requests an override; and
2. at least one independent corroborator also requests an override:
   - RIFT-H3 V1, or
   - VEGA-H3 V1, or
   - TURN-H3 V1.

Thus:

`candidate_t = OPAL_t AND (RIFT_t OR VEGA_t OR TURN_t)`.

No expert probability is re-fit and no vote threshold is searched in HELIOS V1.

## 3. Causal competence ledger

Each matured candidate reversal contributes one binary outcome:

- success = 1 if the candidate reversal would correct an AURORA error;
- success = 0 if the candidate reversal would break a correct AURORA call.

A candidate outcome may enter the competence ledger only when:

`target_end_date_h3 <= current feature_cutoff_date`.

No future or unmatured candidate outcome is used.

## 4. Regime gate

- initial state: **INACTIVE**
- history: latest **8 matured candidate outcomes**
- minimum history: 8 candidate outcomes.

Enter ACTIVE if:
- wins among latest 8 >= **5**.

Exit ACTIVE if:
- wins among latest 8 <= **3**.

Otherwise retain the previous state.

This 5/8 versus 3/8 hysteresis creates a dead-band and avoids one-event regime thrashing.

## 5. Soft residual routing

When gate is INACTIVE or no candidate reversal exists:
- `p_HELIOS = p_AURORA`.

When gate is ACTIVE and candidate reversal exists:

1. posterior competence mean with Beta(1,1) prior:
   `q = (wins + 1) / (8 + 2)`.
2. reverse expert probability:
   `p_reverse = 1 - p_AURORA`.
3. soft residual mixture:
   `p_HELIOS = (1-q)*p_AURORA + q*p_reverse`.

Because ACTIVE requires at least 5/8 wins, q >= 0.60 and the directional call reverses, but confidence is attenuated according to recent demonstrated competence.

A hard-routing ablation is also reported:
- `p_HARD = 1 - p_AURORA` on active candidate events.

The hard ablation cannot determine the V1 decision rule; HELIOS V1 is the soft router.

## 6. Why the gate uses losses rather than raw regime features

The discovered problem is not that a specific volatility or positioning state is universally predictive. OPAL, TURN, RIFT and VEGA each changed quality across time. HELIOS therefore models the **competence regime of the reversal expert itself**.

This is closer to online expert-loss integration than to a second direct forecaster.

## 7. Evaluation

Architecture development is post-hoc after examining 2022-2026 errors. Therefore all historical results are:

**RETROSPECTIVE_STRENGTHENING_EVIDENCE**

and are not pristine lockbox evidence.

Report:
- 2022 H2
- 2023
- 2024
- 2025
- 2026
- 2023-2024
- 2025-2026.

Also report:
- candidate counts and success rates by year;
- gate active share;
- switch dates;
- hard vs soft routing;
- rescued/broken calls;
- Brier/logloss;
- 2025 and 2026 month-by-month.

## 8. Dependence-aware inference

For HELIOS-soft vs AURORA and HELIOS-soft vs raw OPAL:
- circular moving-block bootstrap
- 10,000 replicates
- block lengths 5 and 10
- periods 2023-2024, 2025-2026, 2026.

## 9. Promotion governance

Historical superiority cannot replace prospective proof because HELIOS was designed after inspecting historical reversal behavior.

If HELIOS is stable enough to retain as a challenger:
- freeze HELIOS under a separate prospective identity;
- do not modify the existing AURORA prospective ledger;
- only future origins after HELIOS freeze count as prospective evidence.

No 2022-2026 result may change:
- evidence membership rule;
- 8-event window;
- 5/8 entry;
- 3/8 exit;
- Beta(1,1) competence prior;
- soft-mixture formula.
