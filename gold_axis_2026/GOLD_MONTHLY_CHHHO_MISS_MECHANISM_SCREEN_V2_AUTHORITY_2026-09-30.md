# GOLD MONTHLY — ChHHO Miss Mechanism Screen V2 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / BINDING
**Scope:** alarm discovery/validation only. No routing or fallback-model selection.

## 1. Question

Among scientifically usable ChHHO periods, which origin-visible mechanisms recur before HIGH_AE months that are not already identified by frozen A/B/C/D?

Usable model periods:
- H2 valid same-method pre-DEV: targets 2021-11..2022-03
- H3 frozen canonical DEV: 2022-04..2024-12
- frozen 2025 transport
- frozen 2026 Jan-Aug stress/transport

The unstable 2013-2021 H1 counterfactual ChHHO replay is excluded from model-error labels.

## 2. Existing alarm accounting

A/B/C/D are recomputed with the canonical V3 alarm engine.
- A/C/D are hard mechanisms.
- B remains warning-only.
For mechanism discovery, an already-explained high-error target is any HIGH_AE month with A OR B OR C OR D.

The research target is:
**UNEXPLAINED_HIGH_AE = HIGH_AE AND NOT(A OR B OR C OR D).**

## 3. Independent calibration window

All quantile thresholds for GVZ/CFTC candidate states are calibrated on **2010-01..2020-12 only**.

This precedes:
- valid pre-DEV evaluation beginning 2021-11;
- canonical DEV;
- 2025/2026 discovery period.

No 2021+ ChHHO error is used to choose a quantile threshold.

## 4. Candidate origin-visible features

Use the already-defined EFG diagnostic family without threshold search on model errors:

### Gold state
- Gold 1m / 3m return
- Gold distance from prior MA12
- realized-volatility ratio
- ChHHO forecast-vs-current-Gold disagreement

### Gold-specific volatility
- GVZ max >= calibration Q80
- GVZ max >= calibration Q90
- GVZ dynamic ratio >= calibration Q90

### CFTC positioning
- POSITION_SHIFT: abs monthly change in Managed-Money net/OI >= calibration Q90 OR abs monthly OI change >= calibration Q90
- OI_COMPRESSION: OI / prior-12m median <= calibration Q10
- POSITION_EXTREME: Managed-Money net/OI <= Q10 OR >= Q90

### Existing exploratory flow family
- FLOW_2OF4 = at least two of GVZ-Q80, POSITION_SHIFT, OI_COMPRESSION, POSITION_EXTREME.

This structure is exploratory/post-hoc and must not be called validated merely because later misses are covered.

### Frozen E/G descriptors
Also show current frozen E and G flags, but do not treat them as independently validated ChHHO alarms.

## 5. Required reporting

For each candidate flag report separately for:
1. PRE_DISCOVERY_MODEL = 2021-11..2024-12
2. 2025
3. 2026 Jan-Aug
4. combined usable period

Metrics:
- events
- high-error hits
- false alarms
- precision
- recall of all HIGH_AE
- hits specifically among UNEXPLAINED_HIGH_AE
- list of alarm/hit targets

Also produce a row for every UNEXPLAINED_HIGH_AE target showing all candidate flags.

## 6. Interpretation gate

A candidate may be called a repeated mechanism only if it appears in at least one pre-discovery high-error case and again in later high-error cases without threshold retuning.

It is not promoted to a hard alarm from this screen alone.

Any high-error months with none of the fixed candidate states remain an explicit unresolved class.
