# GOLD CONTROL — AUG31 REPLAY EXPANSION V2 ENGINEERING EVIDENCE

**Evidence date:** 2026-09-04  
**Change-control:** `GOLD_CONTROL_AUG31_REPLAY_EXPANSION_V2_CHANGE_CONTROL_2026-09-04.md`  
**Dry-run status:** `PASS_READ_ONLY_REPLAY_CONSTRUCTION`  
**Git SHA:** `f255fbcc7f8e3513242fe9f99cfc380d234dc94e`  
**GitHub Actions run:** `33879414201` — `SUCCESS`  
**Artifact:** `gold-control-aug31-replay-expansion-v2-f255fbcc7f8e3513242fe9f99cfc380d234dc94e`  
**Artifact digest:** `sha256:f90a38ba6239931b272a5cff9f631f9bc9bb3c04dbc5ff10ffbf5f4fc4bb9b20`

## Evidence classification

- target context: `2026-09`
- information cutoff / replay origin: `2026-08-31T21:00:00Z`
- replay execution timestamp: `2026-09-04T13:42:09.025554Z`
- evidence: `HISTORICAL_REPLAY`
- prospective claim: `false`
- current runtime authority: `false`
- canonical authority: `false`
- selector: `OFF`
- ensemble: `OFF`
- position mapping: `NOT_PROVEN_POSITION_MAPPING`
- database writes during dry-run: `NONE`
- canonical forecast write: `NONE`
- Decision Store write: `NONE`

## Causal Patch — September H=1 historical reference

Identity:
`CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE`

Result:
- September 2026 replay forecast: **4452.046728838838 USD/oz**
- predicted log return: `0.012371922987700623`
- monthly anchor: `4397.305673870967 USD/oz`
- training sample count: `185`
- train/validation cut: `157`
- latest selected daily-feature date: `2026-08-30`
- input fingerprint: `029d71f693775159c120f9782c1bf3e91888ad04fe06b88b4322bced400c5554`

PIT gate:
`2026-08-30 < 2026-08-31` → **PASS**.

Frozen geometry remains unchanged at `L=252, P=21, D=32`. The replay was recomputed from the identical source bundle and deterministic equality gates passed.

Source metadata retained in the artifact includes:
- Twelve XAU/USD 1h August monthly anchor, America/New_York, 16:00 bar / 17:00 ET end, 31 observations, last date 2026-08-31;
- FRED DFF August real-time-as-of 2026-08-31, max source date 2026-08-28, 28 observations;
- FRED DEXCHUS August real-time-as-of 2026-08-31, max source date 2026-08-28, 20 observations;
- NASDAQCOM reconstructed with real-time-as-of 2026-08-31;
- actual retrieval occurred after the historical origin and is therefore marked `retrieved_post_origin=true`.

## Emergency — September month-open state

Replay-only monthly reference: Causal Patch September replay above.

At the 31-Aug month-open boundary no September EOD observation exists. Frozen R4.1 initialization therefore gives:

- **EMERGENCY_LEVEL = NEUTRAL**
- **EMERGENCY_REVERSAL = OFF**
- reason: `MONTH_OPEN_INITIALIZED_NO_SEPTEMBER_EOD_OBSERVATION`

The 31-Aug close was not misclassified as a September observation. Direction vote remains false.

## BOCPD successor — August completed-month context

Archived `BOCPD` remains unchanged and BLOCKED:
`BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED`.

Separate successor:
`BOCPD_RETURN_SUCCESSOR_V1`

Context identity:
`BOCPD_RETURN_SUCCESSOR_V1_AUG31_CONTEXT_BRIDGE_V1`

Result:
- state: **NO_ADVERSE_BREAK_CANDIDATE**
- August log return: `0.07622174452967813`
- previous MAP run length: `5`
- expected uninterrupted run: `6`
- current MAP run length: `6`
- MAP reset: `false`
- reset fraction: `0.0`
- expected run length: `36`
- direction vote: `false`
- validation claim: `false`
- production claim: `false`

The frozen CORE5 artifact did not provide the required August context row, so the pre-registered context bridge was used. Source identity remains explicitly:
`PATCH_XAU_TWELVE_DAILY_MONTHLY_MEAN_V6_TRAIN`.

August daily measurement:
- valid observations: `30`
- monthly mean: `4395.589154333333`
- bridge parent source gate: `PATCH_MONTHLY_LEVEL_BRIDGE_V6_SOURCE_PASS`
- retrieved after historical origin: `true`.

This is **out-of-lock historical context only**. It does not modify BOCPD V1 validation/locked evidence and is not production-graduation evidence.

## Production isolation proof

At dry-run execution:
- engine inventory: `4 ACTIVE / 5 WAITING / 3 BLOCKED`
- direction-vote-permitted count: `3`
- `monthly_forecast_contracts = 0`
- `decision_signal_snapshots = 0`
- `decision_runs = 0`
- `decision_events = 0`

## Dry-run decision

`AUG31_REPLAY_EXPANSION_V2_DRY_RUN_PASS`

This authorizes only the next change-controlled step: append-only persistence into historical replay/display evidence lanes, followed by read-only UI regression. It does **not** authorize prospective/live promotion, canonical H=1 issuance, selector/ensemble activation, Decision Store action, or archived BOCPD recovery claims.
