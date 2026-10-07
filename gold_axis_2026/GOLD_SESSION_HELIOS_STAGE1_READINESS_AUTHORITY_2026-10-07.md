# SESSION HELIOS — STAGE-1 IDENTITY / UPSTREAM / CLOCK READINESS AUTHORITY

**Date:** 2026-10-07  
**Status:** **STAGE-1 COMPLETE / PASS_WITH_SESSION_REBUILD_REQUIRED / RUN NOT YET EXECUTED**

## 1. Purpose

This authority closes only HELIOS Stage-1: identity, upstream dependency and clock/maturity reconciliation for the corrected SESSION target project.

It does **not** contain a HELIOS performance run and does **not** authorize reuse of historical H3 prediction files as SESSION outputs.

## 2. Binding model identity

SESSION HELIOS is a higher-order router / exception architecture. It is **not** a stand-alone raw-feature direction model.

The legitimate historical algorithmic lineage is preserved as:

1. **HELIOS V1**
   - base probability = AURORA;
   - candidate reversal = OPAL override AND at least one corroborator from RIFT / TURN / VEGA;
   - competence history uses only matured candidate outcomes;
   - frozen gate identity: window = 8, enter when wins >= 5, exit when wins <= 3;
   - route reverses AURORA only when the competence gate is active and the candidate condition fires.

2. **HELIOS V2**
   - preserves the V1 routing identity;
   - changes routed probability calibration to posterior competence probability.

3. **HELIOS V3-GT**
   - preserves the upstream AURORA / OPAL / V1-V2 state;
   - updates its policy market only from matured OPAL events;
   - frozen market window = 8;
   - route requires active HELIOS competence state, OPAL override and GT flip share > 0.50.

4. **HELIOS V4-RGE**
   - preserves V2 base routing;
   - adds regret-gated expansion for non-consensus OPAL events;
   - frozen expansion window = 10;
   - enter regret state at +2; exit at -2.

5. **HELIOS V5-DCE**
   - preserves V4;
   - adds the dominant-expert contradiction exception only when:
     - V4 is not already routing;
     - HELIOS competence gate is active;
     - OPAL override is active;
     - the V1 consensus candidate is false;
     - GT flip share > 0.50;
     - AURORA active expert is PATH_GLOBAL;
     - AURORA PATH-superiority posterior > 0.50.
   - on a DCE exception, mirror AURORA probability.

**Binding interpretation:** SESSION HELIOS must be rebuilt sequentially V1 -> V2 -> V3-GT -> V4-RGE -> V5-DCE. Running V5 alone from historical H3 artifacts is prohibited.

## 3. Upstream readiness

Fresh corrected SESSION-native upstream now exists:

- **SESSION AURORA V1:** COMPLETE; fresh causal probability/state ledger available.
- **SESSION OPAL V1:** COMPLETE; fresh corrected-PIT output available. The former BLOCKED_UPSTREAM_AURORA status is superseded.
- **SESSION RIFT:** COMPLETE.
- **SESSION TURN:** COMPLETE.
- **SESSION VEGA:** COMPLETE.

Therefore the previous HELIOS blocker **BLOCKED_UPSTREAM_OPAL/AURORA is resolved**.

RIFT and VEGA were not promoted as stand-alone session specialists after frozen transport. For HELIOS they may be consumed only as their fixed lineage role — corroborator/router telemetry — and must not be counted later as independent consensus votes merely because HELIOS consumes them.

Historical H3 AURORA / OPAL / RIFT / TURN / VEGA / HELIOS prediction CSVs remain prohibited as SESSION model inputs.

## 4. Binding SESSION clock conversion

Historical H3 HELIOS used:
- feature_cutoff_date;
- forecast_issue_date;
- target_end_date_h3.

That maturity clock is **not valid** for SESSION replay.

For every SESSION partition/window, HELIOS state must be independent and keyed to the corrected V5 session target clock.

For a current session origin with start time **T = start_utc**:

- only the same partition/window's prior target rows may update HELIOS adaptive state;
- an outcome is matured only when **end_utc <= T**;
- overlapping or still-open target windows may not enter competence, GT-policy or regret histories;
- no state may be pooled across Sobti and WGC windows;
- no state may be pooled across different windows inside a partition.

All upstream information must satisfy the relevant pre-target availability rule. In particular:
- COT requires `cot_available_at_utc <= start_utc`;
- hourly / 15-minute state must use only completed information available by session start;
- target-window bars are prohibited from features.

The corrected V5 target semantics remain binding:
- exact session-start OPEN;
- final 15-minute bar CLOSE at the declared session end;
- date-aware America/New_York / DST handling;
- venue/calendar eligibility and internal-path gates.

Before scoring, the SESSION HELIOS runner must reconstruct the V5 target from governed raw XAU/USD 15-minute data and verify equality against the frozen V5 target authority.

## 5. Evaluation chronology

- governed 2022 history: warm-up only where required;
- **2023-2024:** development / role and session eligibility;
- **2025:** frozen-specification transport only after the session HELIOS rule is fixed;
- **2026:** unopened for selection/tuning.

No 2025 observation may alter HELIOS windows, thresholds, policy definitions, exception conditions or upstream identities.

## 6. Stage-1 verdict

| Check | Result |
|---|---|
| HELIOS lineage identity | **PASS** |
| Fresh SESSION AURORA upstream | **PASS** |
| Fresh corrected-PIT SESSION OPAL upstream | **PASS** |
| RIFT / TURN / VEGA corroborator lineage available | **PASS** |
| Historical H3 clock directly reusable | **FAIL — must be converted** |
| SESSION maturity rule defined without leakage | **PASS** |
| Prior OPAL/AURORA blocker | **RESOLVED** |
| HELIOS performance run executed | **NO** |

### Binding next action

**HELIOS Stage-2 = implement/preregister the session-native V1->V5 replay under the clock above, then run 2023-2024 development first. Do not open 2025 until the HELIOS session rule and development eligibility are frozen.**
