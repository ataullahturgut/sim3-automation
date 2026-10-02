# HELIOS-H3 V2 — POSTERIOR-CALIBRATED REGIME ROUTER AUTHORITY

**Date:** 2026-10-03
**Identity:** `HELIOS_H3_V2_RESEARCH`
**Parent:** `HELIOS_H3_V1_RESEARCH`
**Status:** PREREGISTERED / POST-HOC STRENGTHENING RESEARCH

## 1. Frozen routing inherited from V1

Candidate reversal:
`OPAL AND (RIFT OR VEGA OR TURN)`.

Causal competence ledger:
- latest 8 matured candidate outcomes;
- target must be mature before entering the ledger.

Regime gate:
- initial INACTIVE;
- enter at >=5 wins of latest 8;
- exit at <=3 wins of latest 8;
- hold state otherwise.

No routing threshold changes are allowed in V2.

## 2. V2 probability calibration

V1 used a residual blend between AURORA and its mirror probability.

V2 treats the regime gate's demonstrated competence as the probability of the reversal decision.

With Beta(1,1) prior and latest-8 results:

`q = (wins+1)/(8+2)`.

If gate is inactive or no candidate:
- `p_V2 = p_AURORA`.

If gate is active and a candidate exists:
- if AURORA predicts UP and reversal predicts DOWN:
  `p_V2(UP)=1-q`;
- if AURORA predicts DOWN and reversal predicts UP:
  `p_V2(UP)=q`.

Thus routed probability is calibrated to recent intervention competence rather than inherited base confidence.

## 3. Robustness study

Report neighboring, non-selected gate formulations as sensitivity diagnostics only:
- W6: last 6, enter 4, exit 2
- W8: last 8, enter 5, exit 3 (V2 binding)
- W10: last 10, enter 6, exit 4.

Sensitivity variants may not replace V2 based on historical results.

## 4. Evaluation

All 2022-2026 evidence remains retrospective strengthening evidence because the architecture was developed after historical error analysis.

Report:
- 2023, 2024, 2025, 2026;
- 2023-2024;
- 2025-2026;
- AURORA, HELIOS V1 soft, HELIOS V1 hard, HELIOS V2;
- dependence-aware moving-block bootstrap;
- gate sensitivity.

## 5. Governance

V2 cannot replace the frozen AURORA prospective champion from historical results.

If retained, V2 must be frozen as a separate prospective challenger and judged only on future origins after its freeze timestamp.
