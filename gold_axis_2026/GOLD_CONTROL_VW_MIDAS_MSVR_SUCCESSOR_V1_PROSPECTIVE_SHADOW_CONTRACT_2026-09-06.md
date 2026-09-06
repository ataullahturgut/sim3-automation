# GOLD CONTROL — VW_MIDAS_MSVR_SUCCESSOR_V1 PROSPECTIVE SHADOW CONTRACT

Registration date: 2026-09-06
Model identity: `VW_MIDAS_MSVR_SUCCESSOR_V1`
Historical model contract: `ca08da189fedb326674190221fd0d12bbf936a10`
Historical engineering evidence: `a061adf32b51ae367f5aa24adf95fbed4b125ba8`
Scope: PROSPECTIVE SHADOW RESEARCH ONLY

## 1. First genuinely prospective origin

The first preregistered prospective origin is:

- forecast origin: **2026-09-30 end of completed calendar month**
- target month: **2026-10**
- target definition: monthly-average XAU/USD price under a separately frozen current-target measurement/anchor contract

A forecast created on or after 2026-09-06 for origin 2026-08-31 / target 2026-09 is NOT prospective. Any such output is historical reconstruction only and may not be backdated or entered into the prospective registry.

## 2. Model freeze

The historical V1 mathematical design is immutable for this first prospective test:
- four metals: Gold, Silver, Platinum, Palladium;
- two features per metal: prior monthly log return + GPR-adaptive weighted within-origin-month daily return;
- 8-dimensional input;
- joint four-output RBF MSVR;
- frozen C/epsilon/gamma grid and nested-selection rules from the 2026-09-06 historical contract;
- no feature addition/removal;
- no post-result hyperparameter/grid changes;
- no 2026-10 actual or partial target information in training, selection, scaling, feature construction or issuance.

## 3. Prospective source gates — fail closed

A 2026-09-30 shadow forecast may be issued only if every gate below is satisfied before issuance.

### 3.1 Four-metal September source

The historical R1 StakTrakr identities are commit-pinned reconstruction series. New future rows MUST NOT be silently appended under the old pinned lineage.

Before issuance, a separately governed prospective/future four-metal source-refresh identity/contract must be frozen. It must preserve the same four-metal measurement semantics or explicitly document any change.

September completeness gate:
- exact four metals present;
- at least 20 common complete four-metal daily observations in 2026-09;
- latest common four-metal observation date >= 2026-09-27;
- no imputation;
- no provider substitution;
- no filling one metal from another source without a separate pre-registered bridge.

Failure status: `WAITING_FOUR_METAL_SOURCE_DATA` or `BLOCKED_FOUR_METAL_SOURCE_REFRESH_CONTRACT_NOT_FROZEN`.

### 3.2 GPR origin vintage

Primary GPR identity remains `GPR_OFFICIAL_GIT_PIT`.
For the 2026-09 origin, the official archive vintage associated with origin month 2026-09 must be available by issuance and must contain the required 2026-08 observation for the frozen p-1 lag rule.

No current/final GPR series may silently replace the origin vintage.

Failure status: `WAITING_GPR_2026_09_ORIGIN_VINTAGE`.

### 3.3 Current XAU price-level anchor / target measurement

The historical price-level recovery used `CORE5_GOLD_USD_OZ_RESEARCH_R1`, a locked local snapshot ending 2026-07. It is not proven as a continuously refreshable live measurement source.

Production Neon contains newer XAU series, including `XAU_EOD_TWELVE_NY17`, but it may NOT silently replace the frozen CORE5 anchor.

Before the 2026-09-30 forecast can be issued as a price level, a separate pre-registered source/measurement bridge must freeze:
- the September monthly XAU anchor used to convert predicted October log return into an October price forecast;
- the exact October actual measurement used later for prospective scoring;
- aggregation, timezone, missing-day, and publication/availability rules;
- historical bridge evidence sufficient to demonstrate that changing the measurement source does not redefine the target without disclosure.

Until this is frozen, status is:
`BLOCKED_TARGET_ANCHOR_REFRESH_CONTRACT_NOT_FROZEN`.

## 4. Readiness state before origin

Before 2026-09-30 23:59:59 in the project time convention, no prospective forecast may be issued.

Current expected top-level status before origin:
`WAITING_ORIGIN_NOT_REACHED`.

Secondary blockers/readiness conditions must still be reported rather than hidden.

## 5. Issuance rules

When origin is reached and all source gates pass:
- use only information available through the frozen origin;
- run the immutable V1 implementation;
- create a research-shadow evidence artifact with forecast, input identities, origin timestamps, hashes, selected hyperparameters and benchmark forecasts;
- freeze the artifact before any October actual is available;
- no backdating;
- no forecast overwrite after issuance;
- no production `monthly_forecast_contracts` write;
- no decision-store write;
- no runtime activation;
- no selector/ensemble activation.

Maximum status after valid issuance:
`PROSPECTIVE_SHADOW_FORECAST_ISSUED_AWAITING_TARGET_MATURITY`.

## 6. Scoring rules after October completes

The October actual is forbidden from model construction/selection/issuance.
After target maturity, score the frozen forecast against the separately frozen October target measurement and the same-origin Random Walk benchmark.

At minimum report:
- absolute error;
- APE;
- squared error;
- direction result;
- same-origin RW error;
- relative absolute loss vs RW.

One prospective month is evidence, not proof of production superiority. No promotion threshold may be invented after observing the result.

## 7. Hard governance locks

- `AUTO_SELECTOR=OFF`
- `AUTO_ENSEMBLE=OFF`
- no production forecast/decision write
- no runtime mutation
- no silent source substitution
- no false PIT claim
- no falsely backdated prospective issuance
- archived `VW_MIDAS_MSVR` remains blocked and untouched
- historical V1 result remains historical evidence only
