# SILVER SHORT-HORIZON PROJECT MANIFEST

**Project identity:** `GLOBAL_XAG_SHORT_HORIZON`  
**Opened:** 2026-10-05  
**Primary source identity:** pinned StakTrakr public four-metal history  
**Pinned commit:** `54fdf1c8d39b7b6c7b874d0f30f784296e886044`

## 1. Objective

Develop a leakage-safe Silver/XAG short-horizon direction system using the scientific governance established in the Gold H3 project, while requiring every horizon, feature family and controller mechanism to re-earn its place on Silver.

The Gold architecture is a methodological template, not a parameter/model template.

## 2. Data availability

Common Silver/Gold/Platinum/Palladium weekday history:
- first date: 2010-01-04
- current pinned common coverage: through 2026-09-28
- usable panel rows: 4,232.

The historical metal data required for an initial Silver project therefore already exists.

## 3. V1 — ordinary H1/H3/H5 target screen

Authority:
- `SILVER_SHORT_HORIZON_V1_PREREG_2026-10-05.md`
- `SILVER_SHORT_HORIZON_V1_RESULT_2026-10-05.md`
- `SILVER_SHORT_HORIZON_V1_SUMMARY_2026-10-05.json`

Protocol:
- TRAIN HISTORY: 2010-2021
- DEV selection: 2022-2024
- transport opened only after selection: 2025 and 2026
- fixed standardized Logistic L2
- expanding, maturity-safe five-origin blocks
- target candidates H1/H3/H5
- feature blocks SILVER_ONLY / CORE3 / CORE4.

DEV winner:
- **H5 / SILVER_ONLY**
- N 755
- accuracy **53.91%**
- balanced accuracy **53.91%**
- Brier **0.2481**
- log loss **0.6893**
- annual DEV BA remains above 50% in all three years.

Transport:
- 2025 STATIC_PRE2025: accuracy 43.08%, BA 51.78%, Brier 0.2574
- 2025 ADAPTIVE_ORIGIN_SAFE: accuracy 49.41%, BA 55.17%, Brier 0.2527
- 2026 STATIC_PRE2025: accuracy 43.39%, BA 44.11%, Brier 0.2808
- 2026 ADAPTIVE_ORIGIN_SAFE: accuracy 42.33%, BA 43.33%, Brier 0.2758.

Decision:
**V1 FAILS TRANSPORT.**

Unlike Gold, Silver does not present a robust H3 direction edge under the same simple metal-return representation.

## 4. V2 — Silver relative-value / metal-state mechanism

Authority:
- `SILVER_SHORT_HORIZON_V2_PREREG_2026-10-05.md`
- `SILVER_SHORT_HORIZON_V2_RESULT_2026-10-05.md`
- `SILVER_SHORT_HORIZON_V2_SUMMARY_2026-10-05.json`

New information tested:
- Gold path
- Silver-Gold return spreads
- Gold/Silver ratio z20/z60 and changes
- Platinum/Palladium state
- four-metal breadth and dispersion
- Silver vs industrial-metal-average spreads
- nonlinear HGB challenger.

The V2 DEV search still selected:
**H5 / SILVER_PATH / LOGIT_L2**

with the same:
- accuracy 53.91%
- BA 53.91%
- Brier 0.2481.

Neither relative-value features nor HGB displaced the simple Silver-path model on probability quality.

2025/2026 transport therefore remains the same failed V1 profile.

Decision:
**V2 RELATIVE-VALUE EXPANSION DOES NOT REPAIR TRANSPORT.**

## 5. Scientific conclusion so far

Do not copy the Gold H3 stack directly onto Silver.

Evidence currently says:
- H1 is near chance;
- H3 is near chance;
- H5 has a weak DEV signal;
- the H5 signal does not survive the 2025-2026 regime;
- Gold/Silver relative-value and four-metal-state features do not repair the failure;
- adding nonlinear HGB does not repair the failure.

Therefore importing AURORA/HELIOS/RIFT/VEGA/SAGE/CIG-D1 at this stage would optimize controllers on top of a weak/non-transporting Silver base state.

## 6. Next authorized research direction

The next Silver stage must introduce a genuinely new information family rather than further rearranging daily metal returns.

Priority blocks:
1. USD / FX and real/nominal rates;
2. VIX / Nasdaq risk state;
3. industrial-demand proxy family, with Copper preferred if an origin-safe series is available;
4. Silver-specific volatility / futures-volume / options state where source clocks are auditable;
5. XAG/SI hourly path if sufficient historical depth exists;
6. macro-event state.

Target research should also consider whether Silver is better represented by:
- H5 directional state;
- selective high-move direction;
- regime-conditioned direction;
- or an abstaining action target rather than forced binary direction.

2025 and 2026 are already consumed transport evidence for V1/V2 and may not be used to retune those identities.

## 7. Current status

**No production-quality Silver direction model yet.**

The data foundation is sufficient and the project is now properly separated from Gold. The first two falsification stages prevent wasting time by copying Gold-specific controllers onto a Silver base that currently fails transport.


## 8. Stage 2 — macro / industrial / uncertainty research (2026-10-05)

Detailed authority:
- `SILVER_SHORT_HORIZON_STAGE2_SYNTHESIS_2026-10-05.md`

### 8.1 V3A macro / risk

Using the Gold R2 origin-safe external panel:
- rates, FX, VIX and Nasdaq were added to the frozen Silver H5 path;
- no block displaced BASE under the preregistered DEV rule.

Headline 2022-2024 DEV:
- BASE: 53.38% accuracy / 53.37% BA / Brier 0.2480;
- RATES: 52.85% / 52.85% / Brier 0.2472;
- FX: 52.58% / 52.58%;
- RISK: 51.26% / 51.25%;
- MACRO_RISK: 51.13% / 51.12%.

The small RATES Brier improvement is within the 0.002 tie band; BASE wins on balanced accuracy.

Status: **NO_MACRO_BLOCK_PROMOTION**.

### 8.2 Hourly Silver readiness

Neon contains:
- `XAG_STAKTRAKR_RESEARCH_DAILY_R1`, 4,230 rows, 2010-01-04 .. 2026-07-31.

No Silver/XAG hourly series was found in Neon.

TwelveData sampled historical `XAG/USD` 1H probes from 2018-2026 returned API 404 / no bars.

Status: **SILVER_1H_DATA_NOT_PROVEN**.

Do not fabricate or silently substitute an hourly Silver series.

### 8.3 V4 Copper / industrial state

World Bank Pink Sheet monthly Copper was tested with a conservative two-calendar-month availability lag.

DEV 2022-2024:
- BASE: 53.38% accuracy / 53.37% BA / Brier 0.2480;
- COPPER: 50.73% / 50.72% / 0.2517;
- COPPER_RATES: 50.46% / 50.45% / 0.2508;
- COPPER_RISK: 50.60% / 50.58% / 0.2533;
- COPPER_MACRO: 50.86% / 50.85% / 0.2521.

Status: **V4_FAIL**.

This rejects the conservative monthly Copper proxy, not all possible daily Copper-futures information.

### 8.4 Gold-style consensus diagnostic

Daily H5 experts BASE / RATES / FX / RISK were tested as a Silver analogue of CIG-D1.

Four-way consensus:
- coverage 66.89%;
- accuracy 53.47%;
- BA 53.42%;
- disagreement BASE accuracy 53.20%.

Consensus is not a useful uncertainty separator, and 2022 consensus accuracy is only 47.14%.

Status: **SILVER_CONSENSUS_FAIL**.

### 8.5 V5 selective confidence gate

Candidate p-up action thresholds: 0.52, 0.53, 0.54, 0.55.

Coverage gate >=30% leaves 0.52 and 0.53. Their DEV BA is nearly tied, so higher-coverage **t=0.52** is frozen.

DEV at t=0.52:
- coverage 58.68%;
- accuracy 55.08%;
- BA 54.87%.

2026 origin-safe transport:
- coverage 75.00%;
- selective accuracy 43.97%;
- BA 46.91%.

Status: **V5_FAIL_2026_TRANSPORT**.

### 8.6 V6 rolling-memory adaptation

Candidate memory windows: expanding / 126 / 252 / 504 matured origins.

DEV aggregate:
- EXPANDING: 53.38% accuracy / 53.37% BA / Brier 0.2480;
- ROLL504: 53.38% / 53.38% / 0.2496;
- ROLL252: 52.19% / 52.19% / 0.2586;
- ROLL126: 50.60% / 50.60% / 0.2818.

EXPANDING remains the frozen winner.

Status: **V6_FAIL_DEV_SELECTION**.

### 8.7 Current scientific position

Silver does not currently justify importing the Gold AURORA / HELIOS / RIFT / SAGE / CIG-D1 controller stack.

The following have been rejected as sufficient solutions:
- precious-metal relative value;
- four-metal state;
- daily macro/risk;
- conservative monthly Copper state;
- expert consensus;
- probability abstention;
- rolling-memory adaptation.

The next authorized channels are:
1. a true Silver intraday source with auditable historical depth;
2. Silver futures volume / open interest / options / COT;
3. event-conditioned response models;
4. alternative target design such as high-move / barrier / selective-event direction.

**Current production status: NO PRODUCTION-QUALITY SILVER DIRECTION MODEL.**
