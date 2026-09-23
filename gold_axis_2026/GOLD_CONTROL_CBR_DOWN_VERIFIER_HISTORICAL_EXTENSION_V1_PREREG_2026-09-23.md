# GOLD CONTROL — CBR DOWN VERIFIER HISTORICAL EXTENSION V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `CBR_DOWN_VERIFIER_HISTORICAL_EXTENSION_V1_RESEARCH`  
**Parent architecture:** SQRT-HAR-DR risk motor + frozen UP Verifier V2 + CBR-DTW STRICT P050 research DOWN candidate  
**Purpose:** test whether the CBR-DTW DOWN-confirmation signal survives when its formation history is extended backward with the corrected external 2018–2021 Dukascopy source.  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Frozen research question

The current research candidate is:

> on `SQRT HIGH RISK + frozen UP Verifier V2 ABSTAIN`, emit DOWN only when `CBR-DTW STRICT P050` gives `p(DOWN) >= 0.50`; otherwise remain UNCERTAIN.

The original CBR candidate was selected from only 13 unresolved 2024 rows and transported unchanged to locked 2025 with supportive descriptive performance.

This extension asks:

> If the exact same CBR path representation, DTW distance, K=3 rule and p=0.50 decision threshold are kept fixed, does adding source-harmonized 2020–2021 high-risk cases to the chronological formation pool preserve useful DOWN discrimination in 2022–2024 and locked 2025?

No parameter, feature, K, DTW band or probability threshold may be changed after scoring.

## 2. Frozen CBR method

Pinned original CBR source:

`f187f89c166a75cefa8cf60709dcd4ce1027663d`

Frozen constants:
- representation points = 48;
- channels = normalized cumulative intraday return + cumulative signed-variance pressure;
- DTW band = 6;
- K = 3 nearest historical cases;
- epsilon = 1e-8;
- STRICT pool = historical rows where frozen SQRT high-risk alarm = 1;
- DOWN confirmation = `p(DOWN) >= 0.50`.

The original CBR algorithm is not altered.

## 3. External source authority

Pinned public raw mirror:

`kevingtlin/Market-Data-Lab@922f83a60cc574e7395fb27397077288055a1ef6`

Only XAUUSD 1-minute bid/ask files needed for 2020–2021 path construction are downloaded transiently in CI. Raw third-party files are **not** committed to this repository.

Pinned corrected external daily spine:

`gold_axis_2026/external_data/v2/dukascopy_xauusd_govsession_mid_5m_daily_features_2018_2021.csv`

from commit:

`509c5ffa762f4ea49644b8ffe723ed2591ba52bf`

Frozen construction:
- exact bid/ask timestamp inner join;
- mid close = (bid close + ask close)/2;
- UTC 5-minute last-close bins;
- convert bins to `America/New_York`;
- remove 17:00–17:55 local maintenance hour;
- weekday grouping;
- zero-variance synthetic rows excluded.

No 2025 or 2026 external data enter model formation.

## 4. External path reconstruction integrity

Before any CBR result is interpreted, the transient 2020–2021 raw mirror reconstruction must reproduce the corrected external daily spine.

Mandatory checks:
- every retained external 2020–2021 date used in the model has 276 five-minute bars;
- exact date coverage agrees with the pinned corrected spine for 2020–2021;
- max absolute close difference <= 1e-8;
- max absolute RV difference <= 1e-12;
- max absolute downside-RV difference <= 1e-12.

Failure => `BLOCKED_EXTERNAL_PATH_RECONSTRUCTION`.

## 5. Cross-source path harmonization gate

Because the extension mixes external path morphology with governed internal path morphology, an explicit overlap gate is required before model scoring.

On all available exact-date 2020–2021 overlap between the reconstructed external path and governed internal 5-minute path:

- overlap n must be >=300;
- median same-date flattened path correlation must be >=0.98;
- median same-date CBR-DTW distance must be <25% of the median deterministic shifted-date CBR-DTW distance;
- at least 90% of same-date cross-source DTW distances must be below the median shifted-date distance.

The shifted comparator pairs each external overlap date with the next governed overlap date in chronological order, wrapping once at the end. It is deterministic and outcome-blind.

Failure => `BLOCKED_PATH_HARMONIZATION`.

## 6. Frozen SQRT historical parent extension

Pinned SQRT implementation:

`gold_axis_2026/tools/regime_v1_router_sqrt.py`

at commit:

`ad0fc4dcbe1687833bd9a153cd4bc6a754523464`

Using only the corrected external daily spine:
- reconstruct 2020 SQRT rows chronologically from 2018–2019 formation;
- reconstruct 2021 SQRT rows chronologically from 2018–2020 formation.

Mandatory exact aggregate reproduction:
- 2020 SQRT alarms = 212;
- 2020 alarm direction = 97 DOWN / 115 UP;
- 2021 SQRT alarms = 28;
- 2021 alarm direction = 16 DOWN / 12 UP.

Failure => `BLOCKED_SQRT_EXTENSION_MISMATCH`.

## 7. Chronological CBR formation pools

No random split.

For each target year:

### 2022
CBR STRICT formation =
- external 2020 SQRT alarm cases;
- external 2021 SQRT alarm cases.

Test =
- exact frozen 2022 unresolved rows:
  `SQRT HIGH RISK + UP Verifier V2 ABSTAIN`.

Expected test support = 11.

### 2023
Formation =
- external 2020–2021 SQRT alarm cases;
- governed frozen 2022 SQRT alarm cases.

Expected unresolved test support = 2.

### 2024
Formation =
- external 2020–2021 SQRT alarm cases;
- governed frozen 2022–2023 SQRT alarm cases.

Expected unresolved test support = 13.

### Locked 2025 transport
Formation =
- external 2020–2021 SQRT alarm cases;
- governed frozen 2022–2024 SQRT alarm cases.

Test =
- exact frozen 2025 `SQRT HIGH RISK + UP Verifier V2 ABSTAIN` rows.

Expected support = 74 = 39 DOWN + 35 UP.

2025 cannot change any rule, threshold or candidate identity.

## 8. Primary metrics

Report per year and pooled 2022–2024:

- test n;
- actual DOWN / UP;
- DOWN calls;
- correct DOWN;
- false DOWN;
- DOWN precision;
- DOWN recall;
- false-DOWN FPR;
- call coverage;
- one-sided 90% Wilson lower bound on DOWN precision;
- mean CBR probability;
- mean neighbour distance.

Also report training-pool size and class balance by year.

## 9. Frozen interpretation gates

### Pre-2025 extension support

Call the extension `PRE2025_EXTENSION_SUPPORTIVE` only if pooled 2022–2024:
- total available n = 26;
- DOWN calls >=5;
- DOWN precision >50%;
- false-DOWN FPR <50%.

No tuning follows a failure.

### Locked 2025 transport support

Call 2025 `TRANSPORT_SUPPORTIVE` only if:
- DOWN calls >=5;
- DOWN precision > 39/74 = 52.7027%;
- false-DOWN FPR <50%.

### Final statuses

- `BLOCKED_EXTERNAL_PATH_RECONSTRUCTION`
- `BLOCKED_PATH_HARMONIZATION`
- `BLOCKED_SQRT_EXTENSION_MISMATCH`
- `HISTORICAL_EXTENSION_NOT_SUPPORTED`
- `HISTORICAL_EXTENSION_PRE2025_ONLY`
- `HISTORICAL_EXTENSION_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT`

Even the strongest status remains retrospective research evidence, not certification.

## 10. Comparators

For context only, report:
- original 2024 CBR STRICT P050 unresolved-subset result: 5 DOWN calls, 3 correct / 2 false, precision 60.00%;
- original locked 2025 unresolved-subset result: 33 DOWN calls, 21 correct / 12 false, precision 63.64%.

These are not optimization targets.

## 11. Governance

- random split: forbidden;
- threshold tuning: forbidden;
- K/band/representation tuning: forbidden;
- 2025 selection or rescue: forbidden;
- 2026 model selection: forbidden;
- external source remains research-only;
- governed DB access read-only;
- raw third-party minute files are transient and not redistributed;
- production writes: NONE;
- runtime promotion: NONE.
