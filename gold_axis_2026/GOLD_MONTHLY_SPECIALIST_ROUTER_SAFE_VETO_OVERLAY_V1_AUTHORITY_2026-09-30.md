# GOLD MONTHLY — Specialist Router + Cross-Model SAFE-Veto Overlay V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / FROZEN OVERLAY AUDIT

## 1. Objective

The frozen Specialist Router V1 is the first alarm router in the current line that:
- retains all DEV HIGH and MEDIUM hits;
- removes 5 DEV false calls;
- preserves the cleaner 2025 alarm set;
- adds the 2026-05 V2-only independent HIGH catch.

An earlier, orthogonal false-call study identified one promising origin-known SAFE-veto:

**V2_STRONG_DIRECTION_CONSENSUS**
- at least 80% of competitive forecasts agree with ChHHO direction versus RW; AND
- cross-model forecast dispersion is no greater than its expanding prior-history median.

This experiment asks:

> Can the frozen SAFE-veto remove additional false calls from the frozen Specialist Router without removing any DEV HIGH/MEDIUM warning?

No router or veto threshold is retuned.

## 2. Frozen router

Use exact V1 selected router:
- Specialist Hedge
- eta = 0.25
- alpha = 0
- HIGH decision threshold tau = 0.50
- experts A/B/C/D/E/G/H/I1/I2/T1_WGC/V2_TRANSITION + NULL.

Source artifact:
- Specialist Router V1 artifact **11124892942**.

The router is not recomputed or retuned in this stage; its recorded row-level WARN decisions are treated as frozen.

## 3. Frozen DEV SAFE-veto

Use the exact earlier DEV suppressor output:
- `V2_STRONG_DIRECTION_CONSENSUS`
- original frozen 16-model competitive pool
- threshold agreement >=0.80
- dispersion <= expanding prior median
- minimum prior history 6.

Source artifact:
- False-Call Suppressor Screen V1 artifact **11095060918**.

For DEV, the overlay uses the exact previously recorded V2 veto booleans. No recomputation of the 16-model DEV feature is permitted.

## 4. Overlay rule

For a row with frozen router WARN:

- if SAFE-veto is eligible and TRUE: **SUPPRESS**
- otherwise: **KEEP**

Rows without router WARN remain OFF.

No other condition is introduced.

## 5. Primary DEV evaluation

Targets:
- 2022-04..2024-12.

Compare:
- raw ANY_VISIBLE
- frozen Specialist Router
- Specialist Router + frozen 16-model SAFE-veto.

Report:
- events;
- HIGH hits;
- MEDIUM hits;
- false calls;
- HIGH recall;
- elevated recall;
- useful-call rate;
- false-call rate;
- exact suppressed rows.

Primary overlay candidate gate requires all:
1. retain **100%** of router DEV HIGH hits;
2. retain **100%** of router DEV MEDIUM hits;
3. remove at least **1** additional router false call;
4. useful-call rate strictly improves versus router.

If any fails:
- overlay is rejected;
- no threshold retuning.

## 6. Transport-capable consensus pool

The original 16-model pool does not have frozen 2025/2026 predictions for every member.

For transport diagnostics only, use the exact intersection of original competitive models with models having frozen DEV + 2025 + 2026 Jan-Jul forecasts:

- AOA_ELM
- ChHHO_ANFIS
- FULL7_ANN
- REDUCED4_ANN
- DE_ABC_RBFNN
- LMC2_RBF_M32
- PLS1_V1

This **7-model transport-capable pool** is fixed before transport outcomes are inspected in this stage.

No non-competitive model is added.

## 7. Transport SAFE-veto construction

For the 7-model pool, use the same formula as the frozen V2 SAFE-veto:

At each target month:
- median forecast;
- IQR forecast;
- `DISPERSION_PCT = IQR / abs(median) * 100`;
- ChHHO direction relative to RW;
- `CHHHO_DIRECTION_AGREEMENT` = share of the 7 models with the same direction as ChHHO relative to RW.

Veto:
- direction agreement >= 0.80; AND
- dispersion <= expanding prior median.

Prior median:
- feature history only;
- no target outcomes;
- starts from DEV 2022-04;
- minimum prior history = 6.

No threshold is fit from 2025/2026 outcomes.

## 8. Transport-pool DEV compatibility diagnostic

Before interpreting transport results, apply the 7-model transport-capable veto to DEV.

A minimum compatibility safety condition is:

> the 7-model shadow veto must suppress **zero** router DEV HIGH and **zero** router DEV MEDIUM warnings.

Also report:
- original 16-model V2 veto flags;
- 7-model shadow V2 veto flags;
- overlap/Jaccard on eligible DEV months;
- additional/missing veto months.

No overlap threshold is optimized.

If the 7-model shadow suppresses any DEV HIGH/MEDIUM:
- transport SAFE-veto results are considered **NOT SAFETY-COMPATIBLE** and cannot support promotion.

## 9. Opened transport evaluation

Opened evidence is descriptive only.

### 2025
All 12 target months have the 7-model transport feature.

### 2026
The frozen transport-capable pool has forecasts through target **2026-07**.
Target **2026-08** has no complete 7-model consensus feature.

Therefore:
- 2026-01..2026-07: apply 7-model SAFE-veto if eligible;
- 2026-08: SAFE-veto status = NO_FEATURE and the frozen router decision is passed through unchanged.

Report separately:
- 2025
- 2026 Jan-Aug
- combined 2025-2026.

## 10. Critical opened checks

Report explicitly whether the overlay preserves:

- origin 2026-05 -> target 2026-06:
  - V2-only frozen router warning;
  - HIGH target;
  - previously missed by all raw alarms.

Also report:
- origin 2026-07 -> target 2026-08;
- no complete transport-veto feature, therefore router pass-through.

Opened evidence cannot rescue a failed DEV overlay gate.

## 11. Decision statuses

Possible statuses:

### DEV_OVERLAY_CANDIDATE_PASS
Primary DEV overlay gate passes.

### DEV_OVERLAY_REJECT
Primary DEV overlay gate fails.

Separately:

### TRANSPORT_POOL_SAFETY_COMPATIBLE
7-model shadow veto removes zero DEV HIGH/MEDIUM router hits.

### TRANSPORT_POOL_NOT_SAFETY_COMPATIBLE
7-model shadow veto removes any DEV HIGH/MEDIUM router hit.

No production authorization is granted in V1.

## 12. Governance

Forbidden:
- changing Specialist Router eta/alpha/tau;
- changing V2 SAFE-veto 80% threshold;
- changing dispersion median rule;
- changing minimum history 6;
- selecting another model pool after results;
- using target outcomes in veto features;
- retuning from 2025/2026;
- forecast correction;
- model switching.

This stage tests only the frozen orthogonal overlay.
