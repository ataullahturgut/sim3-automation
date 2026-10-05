# SILVER SHORT-HORIZON — STAGE 2 SYNTHESIS

**Date:** 2026-10-05  
**Project:** `GLOBAL_XAG_SHORT_HORIZON`  
**Evidence class:** retrospective DEV / frozen transport diagnostics; no production promotion.

## 1. V3A — Macro / risk linear scout

The frozen H5 Silver-path Logistic was augmented using the origin-safe daily macro/risk panel already built for the Gold R2 project.

Availability clocks are inherited from that panel:
- H.15 rates: conservative 2-day availability lag;
- H.10 FX: conservative 7-day lag;
- VIX / NDX: 1-day lag.

2022-2024 DEV:

| Block | Accuracy | BA | Brier | Log loss |
|---|---:|---:|---:|---:|
| BASE | **53.38%** | **53.37%** | 0.2480 | 0.6891 |
| RATES | 52.85% | 52.85% | **0.2472** | **0.6875** |
| FX | 52.58% | 52.58% | 0.2497 | 0.6926 |
| RISK | 51.26% | 51.25% | 0.2495 | 0.6921 |
| MACRO_RISK | 51.13% | 51.12% | 0.2486 | 0.6904 |

Under the preregistered rule, the Brier advantage of RATES is within 0.002 of BASE, so the higher balanced accuracy wins.

**Frozen V3A selection remains BASE.**

Annual diagnostics show strong nonstationarity:
- BASE BA: 2022 52.27%, 2023 50.64%, 2024 57.09%;
- FX BA: 45.43%, 50.24%, 61.81%;
- RATES BA: 50.74%, 53.03%, 54.72%.

Conclusion:
daily rates contain some probability-quality information, but no macro/risk block earns promotion over the Silver-path base on DEV.

The exact full HGB walk-forward branch was not promoted or used for transport; V2 already showed nonlinear HGB does not repair the base Silver path. No 2025/2026 macro candidate was selected from these results.

## 2. Hourly readiness

Authority:
- `SILVER_HOURLY_READINESS_V1_2026-10-05.md`
- `SILVER_HOURLY_READINESS_V1_2026-10-05.json`

Neon inventory:
- `XAG_STAKTRAKR_RESEARCH_DAILY_R1`
- n=4,230
- 2010-01-04 through 2026-07-31.

No Silver/XAG 1H series is currently stored in Neon.

TwelveData historical `XAG/USD` 1H probes on sampled dates from 2018 through 2026 returned API 404 and no 16:00 NY bars.

Conclusion:
**Silver hourly path is currently DATA_NOT_PROVEN / BLOCKED.**

Do not create an hourly model from fabricated or silently substituted Silver data.

## 3. V4 — Copper / industrial-state test

Copper source:
- World Bank Pink Sheet monthly Copper;
- available history through 2026-08;
- deliberately conservative daily mapping uses only the Copper month two calendar months before the Silver forecast-issue month.

2022-2024 DEV:

| Block | Accuracy | BA | Brier | Log loss |
|---|---:|---:|---:|---:|
| BASE | **53.38%** | **53.37%** | **0.2480** | **0.6891** |
| COPPER_RATES | 50.46% | 50.45% | 0.2508 | 0.6948 |
| COPPER | 50.73% | 50.72% | 0.2517 | 0.6966 |
| COPPER_MACRO | 50.86% | 50.85% | 0.2521 | 0.6975 |
| COPPER_RISK | 50.60% | 50.58% | 0.2533 | 0.6999 |

Decision:
**Copper does not improve the H5 Silver direction state. V4 FAIL.**

This does not prove that daily Copper futures information has no value; it rejects the conservative monthly industrial-state proxy.

## 4. Silver consensus diagnostic

Gold-style consensus was tested on 2022-2024 DEV using:
- BASE;
- RATES;
- FX;
- RISK;
- optional MACRO_RISK.

Four-core full agreement:
- consensus N=505 / 755;
- coverage 66.89%;
- accuracy **53.47%**;
- BA **53.42%**;
- disagreement BASE accuracy **53.20%**.

Annual consensus accuracy:
- 2022 **47.14%**
- 2023 52.97%
- 2024 58.89%.

Five-block full agreement:
- coverage 62.52%;
- accuracy 53.60%;
- BA 53.65%;
- 2022 accuracy 47.06%.

Decision:
**Gold CIG-style consensus does not transport to Silver.**

Agreement does not create a stable uncertainty state; in 2022 consensus itself is below chance.

## 5. V5 — Selective confidence / abstention

Frozen base:
- H5 Silver-path Logistic.

DEV candidate action thresholds:
- t=0.52, 0.53, 0.54, 0.55;
- act only if p_up >= t or p_up <= 1-t;
- minimum DEV coverage 30%.

DEV results:

| t | Coverage | Selective accuracy | Selective BA |
|---|---:|---:|---:|
| **0.52** | **58.68%** | 55.08% | **54.87%** |
| 0.53 | 39.34% | 56.23% | 54.89% |
| 0.54 | 26.23% | 55.05% | 54.00% |
| 0.55 | 15.76% | 59.66% | 57.51% |

Only 0.52 and 0.53 meet the 30% coverage gate. Their BA difference is <1 pp, so the higher-coverage threshold **t=0.52** is frozen.

Annual t=0.52 BA:
- 2022 52.13%
- 2023 54.38%
- 2024 57.36%.

Frozen t=0.52 transport:

### 2025
- STATIC_PRE2025: coverage 60.08%, selective accuracy 42.76%, BA 53.12%;
- ADAPTIVE_ORIGIN_SAFE: coverage 55.34%, selective accuracy 49.29%, BA 54.75%.

### 2026 available R2-mature universe
- STATIC_PRE2025: coverage 85.64%, selective accuracy 44.10%, BA 45.08%;
- ADAPTIVE_ORIGIN_SAFE: coverage 75.00%, selective accuracy 43.97%, BA 46.91%.

Decision:
**V5 selective confidence FAILS 2026 transport.**

The problem is not merely low-confidence observations.

## 6. V6 — Rolling-memory regime adaptation

Target/features/model remain unchanged. Only training memory changes.

Candidate memories:
- EXPANDING
- ROLL126
- ROLL252
- ROLL504.

2022-2024 DEV:

| Memory | Accuracy | BA | Brier | Log loss |
|---|---:|---:|---:|---:|
| **EXPANDING** | **53.38%** | 53.37% | **0.2480** | **0.6891** |
| ROLL504 | 53.38% | **53.38%** | 0.2496 | 0.6926 |
| ROLL252 | 52.19% | 52.19% | 0.2586 | 0.7129 |
| ROLL126 | 50.60% | 50.60% | 0.2818 | 0.7785 |

Annual BA:
- EXPANDING: 52.27%, 50.64%, 57.09%
- ROLL504: 47.40%, 58.45%, 53.94%
- ROLL252: 44.51%, 54.88%, 57.09%
- ROLL126: 49.30%, 49.40%, 53.15%.

Decision:
**EXPANDING remains frozen winner. V6 rolling-memory adaptation FAILS DEV selection.**

2025/2026 are therefore not used to retune a rolling window.

## 7. Stage-2 scientific conclusion

The following explanations have now been tested and rejected as sufficient solutions:
- precious-metal relative value;
- four-metal state;
- daily macro/risk state;
- conservative monthly Copper industrial state;
- Gold-style expert consensus;
- confidence abstention;
- simple recent-history rolling adaptation.

This materially narrows the Silver problem.

The surviving interpretation is:

> the current daily Silver H5 feature representation does not contain a transport-stable direction signal strong enough to justify Gold-style specialist/controller engineering.

The next legitimate information channels are:
1. a **true Silver intraday source** (XAG/SI 1H) from a provider with proven historical coverage;
2. Silver futures-specific volume/open-interest/options/COT features with origin-time clocks;
3. event-conditioned Silver response rather than unconditional direction;
4. alternative target design: large-move / barrier / selective event target instead of forced H5 UP/DOWN.

Do not add AURORA/HELIOS/RIFT/SAGE-like complexity until one of these channels establishes a transportable base signal.
