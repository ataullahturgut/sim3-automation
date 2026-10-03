# FLOW-H3 STAGE 1A — CLOSURE

**Date:** 2026-10-03  
**Branch:** `gold-h3-flow-v1-20261003`  
**Stage status:** **CLOSED FOR CURRENT ENVIRONMENT / NOT PROMOTED**

## 1. Full FLOW-H3 V1

Status: **BLOCKED_EXTERNAL_HISTORICAL_OI_ACCESS**

Completed:
- official CME/COMEX GC source identity frozen;
- H3 17:00 ET origin-safe FINAL-only VOI clock frozen;
- normalized Volume+OI feature contract frozen;
- 2023-2024 DEV / 2025 confirmation / 2026 holdout protocol preregistered;
- production Neon duplicate-source audit completed;
- CME public XLSX/JSON access probe completed;
- Nasdaq Data Link / Quandl continuous-futures access probe completed.

Blocking fact:
- historical FINAL daily GC open interest required by the frozen V1 contract is not available through the current environment.
- CME's Historical Daily Bulletin route is DataMine.
- direct automated CME public endpoints returned HTTP 403 and were not bypassed.
- no existing entitled DataMine integration or historical daily GC OI series exists in the project.

No threshold/model was fitted for full FLOW-H3 V1.

## 2. FLOW-VOL-H3 V1 ablation

Purpose:
- test whether prior-trade-date GC futures volume alone provides enough reversal discrimination to justify a volume-only fallback.

Source:
- Yahoo Finance `GC=F` daily volume proxy;
- 1439 raw rows retrieved, 1429 feature-ready rows;
- strict prior-trade-date use; same-day volume forbidden.

DEV = 2023-2024 only:
- eligible AURORA-follows-momentum origins: 388
- true reversals: 111

Frozen threshold results:
- 0.35: precision 28.95%, recall 99.10%, candidate rate 97.94% -> ineligible
- 0.40: precision 28.61%, recall 94.59%, candidate rate 94.59% -> ineligible
- 0.45: precision 27.69%, recall 76.58%, candidate rate 79.12% -> ineligible
- 0.50: precision 30.73%, recall 49.55%, candidate rate 46.13% -> ineligible
- 0.55: precision 32.14%, recall 16.22%, candidate rate 14.43% -> ineligible

Binding result:
**NO_ELIGIBLE_FLOW_VOL_THRESHOLD**

Because the preregistered DEV gate failed:
- 2025 confirmation was not opened;
- 2026 final holdout was not opened;
- the known 55 missed-reversal set was not used to rescue or tune FLOW-VOL.

## 3. Scientific interpretation

Volume by itself does not create a sufficiently selective reversal-candidate channel under the frozen protocol.

This does **not** reject the original FLOW hypothesis:
- daily OI change is the mechanism-defining variable for participation/position build-vs-liquidation states;
- the full Volume+OI specialist was not testable with the current entitled data access.

FLOW-H3 therefore remains a preserved blocked research branch, not a failed full model.

## 4. Project sequencing decision

Stage 1A is not skipped; it is closed as:
- full FLOW: **BLOCKED**
- volume-only ablation: **FAILED DEV GATE**
- promotion to HELIOS: **NO**

The project may now proceed to the separately preregistered next specialist family, SKEW-H3, without altering or retroactively weakening the FLOW-H3 rules.

If official CME historical FINAL GC OI later becomes available, FLOW-H3 V1 may resume from its frozen preregistration without using later SKEW/HAZARD outcomes to alter its contract.
