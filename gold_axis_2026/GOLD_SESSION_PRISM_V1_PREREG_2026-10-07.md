# SESSION PRISM V1 — PREREGISTRATION / IDENTITY CONTRACT

**Date:** 2026-10-07
**Status:** BINDING BEFORE SESSION RUN

## Role

PRISM is a spectral residual correction model layered on fresh SESSION AURORA.

It is not a stand-alone direction engine.

## Frozen architecture

Preserve historical PRISM identity:

`logit(p_PRISM) = logit(p_AURORA) + beta' z_wavelet`

The coefficient on the AURORA logit is fixed at 1.0.

Wavelet representation:
- latest 48 active completed XAU hourly returns before session start;
- normalize by 48-return L2 norm + epsilon;
- stationary wavelet transform;
- wavelet = db2;
- level = 3;
- approximation + three detail scales;
- four chronological PAA blocks per scale;
- 16 phase-resolved coefficients;
- append log 48h realized norm;
- append jump concentration = max(abs(r))/sqrt(sum(r^2));
- total latent dimension = 18.

No wavelet, level, latent dimension or feature search is permitted.

## Source timing

For session target start T:

- only canonical XAU hourly bars with `available_at_utc < T` are admissible;
- current/overlapping target information is forbidden;
- 48 active completed hourly returns are taken strictly before T.

## Estimator

Residual offset-logistic model:

`eta = logit(p_AURORA) + Z beta`

Fit beta by penalized Bernoulli negative log likelihood:

`NLL + 0.5 * lambda * ||beta||^2`

Latent features are standardized from matured training rows only.

Fixed lambda grid:
- 1
- 10
- 50

Minimum matured same-window training rows:
- 80.

## Session development selection

Historical H3 PRISM selected lambda on 2022-H2, but fresh session AURORA does not exist for 2022.

Therefore session-native lambda selection is allowed only inside the governed 2023–2024 development period.

For each partition/window:
1. run causal monthly walk-forward for every lambda using only matured same-window rows;
2. score the resulting 2023–2024 predictions;
3. eligible lambda requires:
   - at least one changed direction call;
   - net rescue > 0;
   - PRISM BA >= matched AURORA BA;
   - PRISM Brier <= AURORA Brier + 0.003;
4. among eligible lambdas rank:
   - higher BA;
   - higher accuracy;
   - lower Brier;
   - lower log loss;
   - smaller lambda as final tie-break.

No 2025 outcome may affect lambda selection.

## Frozen 2025 transport

Only session heads with an eligible development lambda may open 2025.

The chosen lambda is frozen.

## Reporting

Per session:
- N
- Accuracy
- Balanced Accuracy
- UP recall
- DOWN recall
- Brier
- changed calls
- rescued
- broken
- net rescue
- selected lambda

## Governance

- 30% minimum-class-recall floor does not apply because PRISM is a residual/correction specialist.
- No 2026 outcome is opened.
- Historical H3 PRISM predictions are QA-only and are not model inputs.
