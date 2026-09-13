# Gold Control V1.69 — Target Representation & Forecastability Audit Checkpoint

Date: 2026-09-13  
Branch: `gold-v169-target-forecastability-audit-research`  
Draft PR: #62  
Parent: V1.68 regime-similarity/local study  
Frozen contract commit: `e9984dde296dcc4c67a75ec18930e0244df2536d`  
Successful workflow run: `34756200461` — SUCCESS  
Artifact: `10317033109`  
Artifact digest: `sha256:c8f3220ff6acc37840ba7b34916ef10b6264305d42e3193bc9f5346d70e2b7d6`

Evidence class: `RETROSPECTIVE_METHOD_DEVELOPMENT_DIAGNOSTIC_NOT_FRESH_OOS`.

## Literature-guided question

After V1.66–V1.68 failed to establish a robust adaptive, invariant, or similar-regime 3D solution, V1.69 moved one level upstream: is binary `UP/DOWN` target construction itself discarding useful predictive information from the underlying continuous return?

The audit was motivated by general statistical literature showing that dichotomization of continuous outcomes can discard substantial information, by probabilistic-forecasting principles favoring prediction of uncertainty/distributions when supported by data, and by selective-classification theory which says abstention should be considered only after base predictive information is demonstrated. V1.69 deliberately does **not** claim to estimate an information-theoretic ceiling.

## Frozen design

Horizons: 1D and 3D.

For four pre-existing information blocks (`GOLD`, `SESSION_RM`, `PRICE_DISCOVERY`, `MACRO_CROSS`), the exact same causal chronology compared:

- direct binary L2 logistic regression for `y_h = 1[r_h > 0]`;
- fixed Ridge regression for continuous `r_h = log(close_{t+h}/close_t)`.

Every origin used only target-matured history. Formation environments were 2023H2, 2024H1 and 2024Q3 through 2024-09-25. 2024Q4 was the frozen bridge. 2025 and available-2026 remained retrospective diagnostics only.

No model-family search, hyperparameter search, deadband tuning, abstention tuning, selector/CRASE, drift detector, residual correction, post-score feature addition, or 2025/2026-based feature/horizon selection was allowed.

## Main result

### 1D

Frozen decision: `BINARY_TARGET_SIGNAL_ONLY__DO_NOT_SWITCH_TO_CONTINUOUS_ON_V169`.

Only `SESSION_RM` passed the pre-2025 **binary** formation + bridge gate. No block passed the continuous-return gate.

`SESSION_RM` binary formation:

- 2023H2: AUC `0.6522`, Brier skill `+6.57%`.
- 2024H1: AUC `0.5470`, Brier skill `-6.68%`.
- 2024Q3: AUC `0.5149`, Brier skill `+0.90%`.

2024Q4 bridge:

- direct binary AUC `0.5600`, Brier skill `+3.39%` and positive log-loss improvement;
- continuous Ridge score AUC `0.6978`, but MAE skill `-1.05%`; therefore the continuous bridge gate failed despite useful ranking in this small bridge sample.

Researcher-visible diagnostics show that the 1D binary signal is **weak rather than production-ready**:

- 2025 SESSION_RM AUC `0.5359`, Brier skill `-2.84%`;
- available-2026 AUC `0.5297`, Brier skill `-4.38%`.

Thus V1.69 does not establish high 1D predictive power. It only prevents the incorrect conclusion that binary 1D is completely signal-free: SESSION_RM carries a small amount of directional ranking information, but probability skill does not persist against the causal-frequency benchmark.

### 3D

Frozen decision: `NO_TRANSPORTABLE_SIGNAL_UNDER_EITHER_TARGET_REPRESENTATION__INFORMATION_OR_HORIZON_REDESIGN`.

No block passed the pre-2025 formation + bridge gate under either binary or continuous target representation.

`SESSION_RM` is instructive: its 2024Q4 bridge itself looked useful under both representations — binary AUC `0.6615`, Brier skill `+6.78%`; continuous AUC `0.6410`, MAE skill `+1.79%`, MSE skill `+2.08%`, Spearman `0.1560` — but both formation gates had already failed because the relationship was unstable across 2023H2/2024H1/2024Q3. Visible 2025 performance subsequently deteriorated strongly.

Therefore changing from binary direction to continuous return does **not** solve the 3D problem under the present information set.

## Magnitude-conditioned diagnostic

Absolute-return tertile thresholds were frozen from targets matured by 2024-09-25 and applied only as ex-post failure attribution. The results do not show a clean, persistent pattern in which only LARGE moves are predictable.

For example, 1D SESSION_RM direct AUC in the LARGE band was about `0.667` in the 2024Q4 bridge, `0.560` in 2025 and `0.597` in available-2026. This is somewhat more encouraging than the aggregate 2026 result but is not strong or stable enough to justify tuning a material-move/deadband rule. For 3D, large-move skill varies substantially by period and block.

Hence V1.69 does **not** authorize a post-hoc selective/material-move target.

## Scientific interpretation

The accumulated evidence is now stronger:

1. V1.66: recalibration-only and forgetting-only are insufficient.
2. V1.67: no globally invariant feature block was established.
3. V1.68: frozen state-similarity/local-history training fails the pre-2025 bridge.
4. V1.69: continuous-return modeling does not reveal hidden stable 3D signal; 1D SESSION_RM retains only weak binary ranking signal.

The dominant bottleneck is therefore no longer plausibly described as a particular calibration, weighting, drift, invariance, similarity, or target-dichotomization failure. The current declared information set appears insufficient for robust high-power 1D/3D direction forecasting.

## Literature-guided next direction

Do not add another algorithm to the same information set.

The next justified research program is **new-information acquisition**, prioritizing information that is forward-looking or closer to the price-formation mechanism rather than additional transforms of historical price:

- option-implied distribution information (implied volatility surface, skew/risk reversal, higher moments/density), because derivatives encode forward-looking information about the future return distribution;
- order-flow / order-book imbalance or related futures microstructure information, because short-horizon price changes are strongly linked to supply-demand imbalance, while recognizing that predictive effects can decay quickly with horizon;
- positioning/flow data may be tested as slower context, but weekly COT data should not be treated as a substitute for genuinely short-horizon information.

GVZ alone is already present as a risk/context signal and should not be mistaken for a full option-implied distribution. Full historical options analytics for COMEX/CME generally require a dedicated historical data source; CFTC COT is publicly available but weekly.

Before any V1.70 forecast model is frozen, the project should perform a source/clock/PIT feasibility audit for these new information classes and select only sources that can be reconstructed point-in-time for the historical origins.

No prospective, production, or action-mapping claim is made.
