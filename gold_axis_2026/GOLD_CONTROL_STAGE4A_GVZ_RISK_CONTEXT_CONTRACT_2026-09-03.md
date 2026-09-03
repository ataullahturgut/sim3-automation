# GOLD CONTROL — STAGE 4A GVZ RISK CONTEXT CONTRACT

**Date:** 2026-09-03  
**Status:** `FROZEN_BEFORE_GVZ_CONTEXT_ISSUANCE`  
**Parent manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.22  
**Evidence class:** `LATE_BOOTSTRAP_SHADOW_CONTEXT`

## 1. Purpose

Persist the already-approved R4.1 GVZ risk-cap layer as an immutable component context so the mobile `Görünüm` screen can distinguish stored risk state from a live display-only value.

This contract does **not** create a gold direction, forecast, final decision, position, or action mapping.

## 2. Authority and series identity

Canonical series for this component:

- series: `GVZ_CBOE`
- source: `Cboe`
- source symbol: `GVZ`
- semantic: Cboe Gold ETF Volatility Index
- role: `R4_RISK_CAP`
- source quality: `APPROVED_AUTHORITY_RETRIEVAL_FLOOR`

Cboe is the authority for GVZ and publishes official historical price data. Gold Control consumes the governed Neon observation lineage; this issuer does not substitute another volatility index or fetch an ungoverned provider.

Historical publication timestamps for Cboe daily rows are not retroactively reconstructed. Point-in-time eligibility therefore follows the existing Gold Data R2 retrieval-time floor in Neon.

## 3. Frozen R4.1 rule

The issuer must load the thresholds from `gold_axis_2026/r4_1/config/frozen_r4_1.json` at runtime. No threshold may be copied into a new tuning surface.

Frozen roles:

- `full_cap_max = 25.9795`
- `half_cap_max = 30.5238`
- `panic_above = 30.5238`
- normal cap = `1.0`
- elevated cap = `0.5`
- panic cap = `0.25`
- direction vote = `false`
- role = `RISK_ONLY`

The calculation must use `gold_axis_2026/r4_1/src/gold_r4/gvz.py::gvz_risk` with the config values. Any config inconsistency fails closed.

## 4. Point-in-time input contract

At calculation time `t`, select only a `GVZ_CBOE` observation that:

1. is returned by `observations_as_of(t)`;
2. has `source='Cboe'`;
3. has `quality_status='APPROVED_AUTHORITY_RETRIEVAL_FLOOR'`;
4. has a positive finite value;
5. has `available_as_of <= t` and `retrieved_at <= t`.

The newest eligible observation is used. Provider substitution and future availability are forbidden.

## 5. Persisted component features

Persist four append-only rows in `derived_feature_snapshots`:

- `GVZ_VALUE`
- `GVZ_CAP`
- `GVZ_PANIC`
- `GVZ_REGIME` = `NORMAL | ELEVATED | PANIC`

Feature version: `R4_1_GVZ_RISK_CAP_CONTEXT_V1`.

Every row must carry:

- true calculation timestamp and input cutoff;
- source observation id, timestamps and lineage id;
- input fingerprint;
- config thresholds used;
- `target_context` equal to the calculation month;
- `evidence_class=LATE_BOOTSTRAP_SHADOW_CONTEXT`;
- `display_scope=COMPONENT_CONTEXT_ONLY`;
- `prospective_h1_claim=false`;
- `decision_store_write=NONE`;
- `canonical_forecast_write=NONE`;
- `direction_vote=false`;
- `position_mapping=NOT_PROVEN_POSITION_MAPPING`.

Raw GVZ values may be persisted in Neon as governed derived context but must not be printed into CI logs.

## 6. Fail-closed rules

The issuer must fail without writes if:

- the append-only guard is missing;
- no eligible authoritative GVZ observation exists;
- source, quality, lineage or PIT checks fail;
- the GVZ value is not positive and finite;
- frozen config is missing/inconsistent;
- a conflicting row already exists for the same target context/version/input identity.

## 7. Non-authorized effects

This contract does not authorize:

- BUY/SELL/HOLD/EXIT/REDUCE;
- exposure selection;
- forecast issuance;
- final Decision Store classification;
- BOCPD construction;
- Emergency construction;
- Macro Event reconstruction.

`GVZ` remains a risk cap only and never determines gold direction.
