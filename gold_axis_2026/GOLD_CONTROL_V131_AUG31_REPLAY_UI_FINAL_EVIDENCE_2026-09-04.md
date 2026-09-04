# GOLD CONTROL v1.31 — 31 AUGUST 2026 REPLAY UI FINAL EVIDENCE

**Status:** `PASS_GOVERNED_HISTORICAL_REPLAY_UI_CLOSURE`  
**Evidence date:** 2026-09-04  
**Manifest authority:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.31  
**Canonical branch authority:** `gold-r4-direction-engine`  
**Target context:** `2026-09`  
**Information/state boundary:** `2026-08-31T21:00:00Z` = 31 Aug 2026 17:00 ET  
**Evidence class:** `HISTORICAL_REPLAY` only

---

## 1. PURPOSE

This document closes the governed UI presentation work authorized by:

- `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.31;
- `GOLD_CONTROL_AUG31_REPLAY_EXPANSION_V2_CHANGE_CONTROL_2026-09-04.md`;
- `GOLD_CONTROL_AUG31_REPLAY_EXPANSION_V2_ENGINEERING_EVIDENCE_2026-09-04.md`.

The objective is to expose the now-recoverable 31-Aug-2026 replay outputs for Causal Patch, Emergency Level, Emergency Reversal, and the separately identified BOCPD successor without fabricating a backdated prospective issuance and without changing operational runtime authority.

This closure does **not** promote any replay result into prospective/live/canonical evidence.

---

## 2. FROZEN RESULT SET SHOWN IN THE UI

The UI is authorized to display the following immutable replay references for September 2026:

| Component | Governed replay result | Presentation status |
|---|---:|---|
| Causal Patch | `4452.046728838838 USD/oz` | `31 AĞUSTOS REPLAY · PROSPECTIVE DEĞİL` |
| Emergency · Level | `NEUTRAL` | `31 AĞUSTOS AY-AÇILIŞ REPLAY` |
| Emergency · Reversal | `OFF` | `31 AĞUSTOS AY-AÇILIŞ REPLAY` |
| BOCPD successor | `NO_ADVERSE_BREAK_CANDIDATE` | `SUCCESSOR V1 · 31 AĞUSTOS REPLAY` |

Additional frozen facts:

- Causal Patch last selected daily feature date: `2026-08-30`.
- Causal Patch input fingerprint: `029d71f693775159c120f9782c1bf3e91888ad04fe06b88b4322bced400c5554`.
- BOCPD successor identity: `BOCPD_RETURN_SUCCESSOR_V1`.
- BOCPD successor context bridge identity: `BOCPD_RETURN_SUCCESSOR_V1_AUG31_CONTEXT_BRIDGE_V1`.
- BOCPD successor source series remains explicitly named `PATCH_XAU_TWELVE_DAILY_MONTHLY_MEAN_V6_TRAIN`; it is not relabeled as CORE5.
- BOCPD successor result is research / out-of-lock historical context only.
- Archived `BOCPD` remains `BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED`.

The 31-Aug close is never treated as a September close. Therefore the frozen Emergency month-open state remains exactly `NEUTRAL` / `OFF` until a legitimate September EOD observation exists under the forward contract.

---

## 3. EVIDENCE CHAIN

### 3.1 Pre-result change control

The expansion contract was frozen before the replay result under status:

`FROZEN_BEFORE_AUG31_EXPANSION_RESULT`

No threshold, source identity, Emergency initialization rule, BOCPD successor identity, or authority role was changed after viewing the replay output.

### 3.2 Read-only construction

GitHub Actions run:

`33879414201 = SUCCESS`

Frozen engineering evidence status:

`PASS_READ_ONLY_REPLAY_CONSTRUCTION`

Artifact digest:

`sha256:f90a38ba6239931b272a5cff9f631f9bc9bb3c04dbc5ff10ffbf5f4fc4bb9b20`

### 3.3 Append-only production persistence

GitHub Actions run:

`33880449794 = SUCCESS`

The approved replay evidence was persisted append-only to the production historical-replay evidence lane. No destructive mutation was used.

Persisted replay scope:

- 6 immutable `derived_feature_snapshots` replay features;
- 4 `HISTORICAL_REPLAY` engine-execution rows;
- no canonical forecast output;
- no Decision Store output.

### 3.4 UI patch

One-shot patch workflow:

`33884843918 = SUCCESS`

The one-shot workflow was subsequently removed from the feature tree and is not part of the final canonical payload.

The UI implementation separates two states:

1. **operational technical state** — remains WAITING/BLOCKED according to production runtime authority;
2. **31-Aug historical replay reference** — shown as a secondary evidence layer with explicit `REPLAY · PROSPECTIVE DEĞİL` provenance.

A replay reference therefore cannot change an engine from WAITING/BLOCKED to ACTIVE/ISSUED prospective state.

### 3.5 Permanent UI validation

Permanent validation workflow:

`.github/workflows/gold-control-v131-aug31-replay-ui-validation.yml`

Successful validation run:

`33885341800 = SUCCESS`

Validated successfully:

- manifest v1.31 and frozen change-control authority;
- replay display unit tests;
- exact production replay values from Neon using read-only access;
- production operational runtime distribution;
- direction-vote count;
- Decision Store/canonical authority zero-state;
- frozen deployment snapshot fallback;
- Streamlit startup;
- real Chromium render at `390x844` for both **Görünüm** and **Tahmin**;
- required replay labels and exact output values;
- archived BOCPD blocker remains visible;
- no horizontal mobile overflow.

Screenshot artifact:

- artifact id: `9941627446`
- artifact name: `gold-control-v131-aug31-replay-ui-6a17da7b2236bc0a251ad02471046ddc1e5a3d13`
- artifact digest: `sha256:4fe19c178137fe6975ef3e17d65186d51f541d5d3e14ffbdcf10a4fe92c9be57`

---

## 4. PRODUCTION AUTHORITY AFTER THE CHANGE

The validated production runtime authority remains unchanged:

- `ACTIVE = 4`
- `WAITING = 5`
- `BLOCKED = 3`
- direction-vote permitted engines = `3`

Authority stores remain empty:

- `monthly_forecast_contracts = 0`
- `decision_signal_snapshots = 0`
- `decision_runs = 0`
- `decision_events = 0`

Governance locks remain:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `NOT_PROVEN_POSITION_MAPPING`
- no BUY / SELL / HOLD / EXIT / REDUCE mapping.

No replay value has current runtime authority, canonical authority, direction-vote permission, or prospective H=1 evidence status.

---

## 5. UI SEMANTICS NOW FROZEN

### Görünüm

For Causal Patch, Emergency Level, Emergency Reversal, and BOCPD:

- the card continues to show the operational technical state from production runtime;
- a separate amber replay block may show the 31-Aug replay result;
- the replay block is explicitly labeled `REPLAY · PROSPECTIVE DEĞİL`;
- BOCPD shows archived BLOCKED state separately from `BOCPD_RETURN_SUCCESSOR_V1` historical research context.

### Tahmin

The September historical replay section may show:

- previously governed Momentum / Random Walk September replay references;
- 31-Aug direction/risk state replay;
- Causal Patch September H=1 historical reference;
- Emergency month-open replay state;
- BOCPD successor historical context.

These evidence classes remain visibly separate from any future legitimate prospective September-month-end issuance for October 2026 H=1.

---

## 6. FORWARD STATE IS NOT SATISFIED BY THIS REPLAY

This replay does not satisfy the future prospective requirements.

- Causal Patch still waits for the first legitimate prospective month-end origin; the first planned candidate remains September 2026 month-end for October 2026 H=1, subject to the frozen issuer/PIT gates.
- Emergency Level/Reversal still wait for a governed **prospective** Causal Patch reference in the forward lane.
- Archived BOCPD remains blocked.
- `BOCPD_RETURN_SUCCESSOR_V1` remains a separate research/shadow successor identity until it earns prospective evidence under its own contract.
- VW-MIDAS-MSVR and Macro Event retain their exact blockers and were not modified by this change.

---

## 7. CLOSURE DECISION

`PASS_GOVERNED_HISTORICAL_REPLAY_UI_CLOSURE`

The 31-Aug-2026 replay expansion may be promoted to canonical/UI branches as a read-only presentation and historical-evidence enhancement because:

1. the change was authorized and frozen before result inspection;
2. replay construction and persistence passed;
3. production operational authority remained unchanged;
4. the UI visibly separates replay from prospective/live evidence;
5. the archived BOCPD identity was not silently repaired or replaced;
6. selector, ensemble, position mapping, canonical forecast, Decision Store, and direction-vote locks remain unchanged;
7. the mobile 390x844 render passed the permanent regression gate.

No claim is made that these outputs were prospectively issued on 31 August 2026. They are governed historical replay evidence constructed later using the frozen 31-Aug information boundary and retained retrieval-time provenance.
