# GOLD MONTHLY — Rescue-Gain Predictor V1 Opened Transport

**Date:** 2026-10-01  
**Status:** COMPLETE / FROZEN DEV LEADER / OPENED TRANSPORT ONLY / NO PRODUCTION SWITCH

## Frozen transport contract

The DEV-selected configuration was transported without retuning:
- predictor: **RIDGE_CORE_A10**
- alpha: **10**
- feature set: **CORE**
- policy: **DIRECT_SWITCH**

No 2025/2026 outcome was used to change the predictor, feature set, alpha, challenger pool, or action rule.

Execution:
- workflow run: **36847543031**
- artifact: **11154625268**
- conclusion: **SUCCESS**

Coverage:
- **2025-01..2026-07**
- 19 fully covered Exact16 months
- **12 Specialist Hedge warning months**
- 2026-08 excluded because full Exact16 coverage is unavailable.

## Transport result

- KEEP MAIN warning-month ΣAE: **2153.0192 USD**
- frozen selector ΣAE: **2057.7830 USD**
- cumulative gain versus KEEP: **+95.2362 USD**
- actions: **11 SWITCH / 1 KEEP**
- beneficial switches: **7**
- harmful switches: **4**
- worst incremental harm: **238.5690 USD**

The aggregate result is positive, but the tail loss is not acceptable for production authorization.

### Critical failure

**2026-03**
- realized severity: MEDIUM
- frozen selector chose **DE_ABC_RBFNN**
- predicted rescue gain: about **+89.88 USD**
- realized incremental result versus KEEP ChHHO: **-238.57 USD**

This is the previously identified shared-hard month: the alarm correctly indicated elevated ChHHO risk, but the alternative-model layer should have kept the main model.

## Binding interpretation

The opened transport strengthens the evidence that relative-loss structure exists, because the frozen DEV selector produces positive cumulative gain without retuning. But it also confirms that **automatic switching is unsafe**.

Current production architecture remains:
- ChHHO-ANFIS = main forecast;
- Specialist Hedge = reliability warning layer;
- Rescue-Gain Predictor V1 = research-only contextual layer;
- no automatic SWITCH or BLEND.

The next research problem is a DEV-only harmful-switch / shared-hard guard that can preserve rescue gains while rejecting cases analogous to 2023-03 and 2026-03. Opened 2025/2026 must not be used to tune that guard.
