# LLRS-H3 V1 — LEAD-LAG REPRICING STRESS PREREGISTRATION

**Date:** 2026-10-04  
**Identity:** `LLRS_H3_V1`  
**Branch:** `gold-h3-llrs-v1-20261004`  
**Evidence class:** retrospective mechanism/development; first new clean claim must be prospective after freeze.

## 1. Why LLRS is a new information channel

The previous DIVERGE-PROXY-H3 experiment used only prior-day daily changes in DXY/TNX/NDX/VIX/Silver and simple momentum-conditioned interactions. It failed DEV selectivity.

LLRS does not repeat that experiment.

LLRS asks whether continuously traded cross-asset futures **lead Gold futures intraday**, such that a repricing process has already started in Treasury/Nasdaq/Silver/Oil before the H3 Gold direction flips.

Hourly proxy coverage verified:
- GC=F — PASS
- ZN=F — PASS
- NQ=F — PASS
- SI=F — PASS
- CL=F — PASS
- DX=F — unavailable in this transport
- VX=F — unavailable in this transport

No silent substitution is allowed.

## 2. Clock

Canonical H3 decision reference remains 17:00 America/New_York.

For the Yahoo hourly mechanism test, only hourly bars with timestamp <= **16:00 ET** on the feature-cutoff date may enter the origin state.

The one-hour buffer is conservative because bar timestamp/end semantics are not asserted as exchange authority.

Future hourly observations are forbidden.

## 3. Synchronized hourly panel

Channels:
- Gold futures GC=F
- 10Y Treasury Note futures ZN=F
- Nasdaq-100 futures NQ=F
- Silver futures SI=F
- WTI crude futures CL=F

Synchronize on UTC hourly timestamps after dropping rows with missing Gold.

External features at each hourly training timestamp:
- ZN log returns over 1h, 3h, 6h
- NQ log returns over 1h, 3h, 6h
- SI log returns over 1h, 3h, 6h
- CL log returns over 1h, 3h, 6h

Gold-only baseline features:
- GC log returns over 1h, 3h, 6h

Target for the hourly lead model:
- GC forward 6-hour log return.

A training row is eligible only if its forward-6h Gold target is fully observed **strictly before the current H3 origin cutoff**.

## 4. Rolling lead models

At every H3 origin:

Training history:
- trailing **60 calendar days** of synchronized hourly rows;
- minimum 500 matured hourly rows.

External lead model:
- StandardScaler + Ridge(alpha=10)

Gold persistence baseline:
- StandardScaler + Ridge(alpha=10)

Both are fit only on matured hourly rows.

Origin outputs:
- `pred_ext_6h`: external cross-asset implied next-6h Gold return
- `pred_gc_6h`: Gold-only baseline next-6h return
- `lead_delta = pred_ext_6h - pred_gc_6h`
- `ext_resid_sigma`: training residual standard deviation of the external model

Let `s=+1` for H3 12h Gold momentum UP and -1 for DOWN.

Frozen reversal-pressure variables:
- `llrs_pressure = -s * pred_ext_6h / ext_resid_sigma`
- `llrs_incremental = -s * lead_delta / ext_resid_sigma`
- `llrs_external_opposes = 1[s * pred_ext_6h < 0]`

Interpretation: higher values mean cross-asset futures imply a short-horizon Gold move opposite the current 12h momentum.

## 5. Mechanism diagnostic

Before constructing a router, evaluate whether LLRS pressure separates:
- V5-correct continuation
vs
- V5-missed reversal

within the V5-follows-momentum universe.

Report by half-year:
- median/mean LLRS pressure in rescue vs continuation
- standardized mean difference
- AUC of LLRS pressure for rescue_target
- candidate precision/recall/net for fixed pressure thresholds.

## 6. Frozen candidate family

Candidate only if:
- `llrs_external_opposes = 1`
- `llrs_incremental > 0`
- `llrs_pressure >= q`

Frozen q grid:
`[0.25, 0.50, 0.75, 1.00]`

No additional feature or threshold search is allowed in V1.

## 7. Historical development robustness

Historical 2026 has already been spent by prior research and is development only.

Development blocks:
- 2025 H1
- 2025 H2
- 2026 H1
- 2026 H2 through available September history

A q is development-eligible if:
- total candidates >= 10
- net rescue > 0
- rescue precision >= 0.55
- at least 2 of 4 half-year blocks have net rescue > 0
- no block net < -2

Selection:
1. maximum aggregate net rescue
2. higher rescue precision
3. more rescued
4. fewer candidates
5. higher q

No eligible q => `NO_ELIGIBLE_LLRS_V1_MECHANISM`.

## 8. Prospective freeze

Historical replay is not promotion evidence.

If a q passes the development gate:
- freeze LLRS-H3 V1 on 2026-10-04;
- first clean prospective origin on/after 2026-10-05;
- run as shadow challenger against HELIOS V5-DCE.

Promotion evidence requires:
- at least 20 accepted prospective candidates;
- at least 6 calendar months;
- cumulative net rescue >0;
- precision >=0.60.

## 9. Governance

- Yahoo hourly futures are retrospective mechanism proxies, not source authority.
- A successful mechanism result justifies engineering an authoritative prospective hourly source before production use.
- No post-freeze prospective outcome may alter 60-day window, 6h target, Ridge alpha, feature family or q under V1.
- HELIOS V5-DCE remains champion/binding.
