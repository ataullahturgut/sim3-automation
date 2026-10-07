# SESSION AIM V1 — PREREGISTRATION / IDENTITY CONTRACT

**Date:** 2026-10-07
**Status:** BINDING BEFORE SESSION RUN

## Role

AIM is a performance-adaptive mixture of three fresh session experts.

It is a combiner/router, not a new raw-feature classifier.

## Frozen expert set

### E1 — STRUCTURAL_IRIS
Canonical fresh session probability:
- `S14_A1_PLUS_1H_FULL`

### E2 — PATH_GLOBAL
Canonical fresh session probability:
- `PATH_GLOBAL_1H`

### E3 — PATH_RECENT126
Session-native reconstruction of historical AIM expert:
- canonical 1h PATH features only;
- LogisticRegression L2, C=1.0;
- class_weight=balanced;
- latest 126 matured same-window training rows;
- monthly-block causal OOS predictions;
- no feature selection.

E1 and E2 must come from the same fresh exact-common expert ledger used by SENTRY/DART/AURORA.

## Adaptive competence loss

For expert e at session origin t:

`L_e(t) = decayed weighted mean of (p_e-y)^2`

using only prior expert forecasts whose target has matured:

- same partition/window;
- `end_utc <= current start_utc`;
- prior origin only.

Half-life is measured in matured expert forecasts.

Adaptive weights:

`w_e = exp(-eta * L_e) / sum_j exp(-eta * L_j)`

Final probability:

`p_AIM = sum_e w_e p_e`.

If fewer than 30 matured exact-common expert forecasts are available:
- use equal weights 1/3, 1/3, 1/3.

## Frozen hyperparameter grid

Only:
- half-life = 21 / 63 / 126
- eta = 10 / 20 / 40

No expert-set search.
No PATH_RECENT lookback search.
No threshold search.

Ordinary direction threshold remains 0.50.

## Development selection

Fresh session experts do not have a clean 2022 OOS ledger matching the historical AIM selection period.

Therefore SESSION AIM uses the governed 2023–2024 development period only.

For each partition/window, a candidate is development-eligible if on exact-common 2023–2024 AIM rows:

- AIM Balanced Accuracy >= STRUCTURAL_IRIS;
- AIM Accuracy >= STRUCTURAL_IRIS - 0.5 pp;
- AIM Brier <= STRUCTURAL_IRIS;
- AIM LogLoss <= STRUCTURAL_IRIS + 0.005.

Rank eligible candidates by:
1. higher Balanced Accuracy;
2. higher Accuracy;
3. lower Brier;
4. lower LogLoss;
5. longer half-life;
6. smaller eta.

## Year-stability confirmation

After the best development configuration is selected, it must separately satisfy in both 2023 and 2024 where at least 30 scored rows exist:

- AIM BA >= STRUCTURAL_IRIS BA;
- AIM Accuracy >= STRUCTURAL_IRIS Accuracy - 1 pp;
- AIM Brier <= STRUCTURAL_IRIS Brier + 0.0025.

If either year has fewer than 30 exact-common scored rows:
- mark `INSUFFICIENT_YEAR_CONFIRMATION`;
- do not open 2025 for that session.

Only confirmed session heads may enter frozen 2025 transport.

## Role-aware interpretation

The 30% class-recall floor is not used as an automatic deletion rule.

Report:
- overall Accuracy;
- Balanced Accuracy;
- UP recall;
- DOWN recall;
- Brier;
- expert weights;
- changed calls vs Structural;
- rescued / broken / net rescue.

AIM may be retained as:
- balanced adaptive mixture;
- directional specialist mixture;
- or router evidence,
depending on the frozen results.

## Governance

- 2022 may train PATH_RECENT126 but is not a scored AIM selection period.
- 2023–2024 select/freeze AIM.
- 2025 is frozen transport only.
- 2026 is unopened.
- Historical H3 AIM artifacts are QA/history only.
