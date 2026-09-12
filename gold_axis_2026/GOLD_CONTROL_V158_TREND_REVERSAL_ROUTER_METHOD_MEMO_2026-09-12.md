# Gold Control V1.58 — Trend/Reversal Router Method Memo

Date: 2026-09-12  
Status: research-only frozen successor; no production authority.

## Why this successor exists

A retrospective audit of the V1.49–V1.57 research path shows a repeated pattern: several weak results came from asking a component to solve a target that did not match its role or clock. Event-time Macro Event works when evaluated on event reaction horizons; monthly experts work on monthly price levels; BOCPD is useful as regime context but not as a direction vote; raw H20 accuracy was misleading when the model emitted almost only UP signals; realized semivariance was added to a generic return-quantile model in V1.57 even though the relevant commodity-futures literature motivates it specifically for momentum-reversal episodes.

The canonical repository also already contains a frozen Emergency geometry and a deterministic historical replay for EMERGENCY_LEVEL / EMERGENCY_REVERSAL. The replay audit reports PASS, 400 observation rows and zero future-information violations for both Emergency identities, while preserving the fact that the replay is retrospective rather than prospective. V1.58 therefore does not create a new ungoverned 'reversal vote'. It reuses the 4% Emergency geometry only as a research-clock reversal-context feature.

## Authority basis

- Liu, Lu, Li & Wang (2023), *Journal of Empirical Finance*, DOI 10.1016/j.jempfin.2023.03.001: asymmetric realized semivariance contains information about time-series-momentum reversals in commodity futures and can be used to tune momentum signals.
- Jacobs, Jordan, Nowlan & Hinton (1991), *Neural Computation*, DOI 10.1162/neco.1991.3.1.79: adaptive mixtures of local experts motivate specialist decomposition rather than forcing one model to solve heterogeneous subproblems.
- Giacomini & White (2006), *Econometrica*, DOI 10.1111/j.1468-0262.2006.00718.x: conditional predictive ability motivates asking which forecast/specialist works under current information rather than which model wins unconditionally.
- Dichtl (2020), *Journal of Commodity Markets*, DOI 10.1016/j.jcomm.2019.100106: gold predictability is regime-dependent and classification/regime-dependent forecasting is a natural research direction when hit rate is of interest.

## Frozen V1.58 hypothesis

V1.58 changes the target, not just the feature set. The primary horizon is H20. At each origin, the trailing 20-session cumulative return defines the origin-observable trend sign. The model predicts whether the future H20 direction will **continue** that trend or **reverse** it. Only after this router decision is made is the result mapped back to UP/DOWN.

This transforms the problem from:

`absolute UP vs DOWN`  
into  
`CONTINUATION vs REVERSAL relative to the current trend`.

The latter is better aligned with the realized-semivariance literature and reduces the pathological interpretation of a strong bull year in which a model can achieve high raw accuracy by always saying UP.

## Existing motors and roles

The continuation lane uses the existing trend state plus the frozen H20 RTQ baseline as a confirmation option. The reversal router consumes realized volatility/semivariance/skew/jump information, FAST/SLOW/Monthly Direction agreement or disagreement, and a causal reconstruction of the frozen Emergency geometry from the monthly Patch V7 reference and the 13:29 research close.

Emergency context is explicitly **not** a direction vote. A persistent `DOWN_ALERT` or `UP_ALERT` is not counted as a new independent forecast every day. Its state, onset and age are context variables for a reversal classifier.

## Frozen models

Primary: shallow `HistGradientBoostingClassifier`, depth 2, rolling 252 mature targets.  
Diagnostic: class-balanced standardized logistic regression, rolling 252 mature targets.  
No hyperparameter search is permitted after 2025/2026 scores are observed.

Router thresholds are frozen at 0.60 / 0.40:

- `p(reversal) >= 0.60` → opposite of trend.
- `p(reversal) <= 0.40` → trend continuation.
- otherwise → `NO_SIGNAL`.

A second predeclared confirmed router allows continuation only when the existing frozen H20 RTQ selective signal agrees with the trend. Reversal decisions are not backdated and are not automatically overridden by Emergency state.

## Evidence windows and interpretation

Training may use only mature targets. A H20 target is mature at origin t only if its target row has already occurred (`j + 20 <= t`). Formation scoring is 2024, validation diagnostic is 2025, and available test diagnostic is 2026 through 2026-06-30. Targets crossing a frozen period boundary are excluded from that period's score.

Because V1.51–V1.57 already exposed 2025/2026 outcomes to the researcher, V1.58 labels them `RETROSPECTIVE_SUCCESSOR_DIAGNOSTIC`. They are not described as untouched OOS evidence. Future prospective shadow evidence is required for any promotion.

## Primary support gate

A V1.58 primary-router claim requires, in both 2025 and 2026 available periods: >=20% coverage, balanced accuracy > 0.50, MCC > 0, both UP and DOWN signals, and reversal-probability Brier/log-loss no worse than an expanding-frequency benchmark with at least one strictly better. In addition, 2025 balanced accuracy must beat the frozen H20 RTQ baseline and 2026 balanced accuracy must not fall below it.

Raw accuracy alone can never pass V1.58.

## Governance

`AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, no BUY/SELL mapping, no production writes, no production authority, no threshold/horizon/feature/router repair after score inspection. Failure is recorded unchanged and can only motivate a separately frozen future successor.
