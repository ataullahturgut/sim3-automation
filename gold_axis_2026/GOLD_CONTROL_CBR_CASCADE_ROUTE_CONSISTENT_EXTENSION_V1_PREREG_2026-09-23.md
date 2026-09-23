# GOLD CONTROL — CBR CASCADE-ROUTE-CONSISTENT HISTORICAL EXTENSION V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESEARCH`  
**Purpose:** test the intended cascade exactly as designed, including route-consistent CBR training populations.  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Binding cascade

The tested architecture is exactly:

```
SQRT
  |
HIGH RISK
  |
Frozen UP Verifier V2
 /                  \
UP                  ABSTAIN
|                      |
VERIFIED UP           CBR-DTW
                     /       \
                  DOWN        no
                    |          |
             VERIFIED DOWN   UNCERTAIN
```

The critical routing rule is:

> A historical case may enter the CBR training library **only if that historical case itself reached the CBR stage**, i.e. `SQRT HIGH RISK + Frozen UP Verifier V2 ABSTAIN`.

Historical cases where the UP verifier emitted UP are excluded from the CBR library because the live cascade would have terminated them at `VERIFIED UP`.

This is the methodological correction relative to the prior historical-extension identity, which incorrectly allowed all historical SQRT alarms into the CBR library.

## 2. Frozen CBR method

Pinned original source:
`f187f89c166a75cefa8cf60709dcd4ce1027663d`.

No CBR parameter is changed:
- NPTS=48;
- two channels = normalized cumulative intraday return + cumulative signed-variance pressure;
- DTW band=6;
- K=3;
- EPS=1e-8;
- inverse-distance weighted p(DOWN);
- positive DOWN confirmation iff `p(DOWN) >= 0.50`.

The CBR target remains next-day close direction.

## 3. Frozen parent and UP route

### SQRT
Use the frozen SQRT-HAR-DR equations and frozen yearly high-risk thresholds.

### UP Verifier
Use the frozen `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH` semantics exactly.

External historical Router chronology:
- evaluate 2020 using 2019 common rows as initial competence history, updating causally within 2020;
- evaluate 2021 using 2020 common rows as initial competence history, updating causally within 2021.

Governed history:
- use the already frozen exact Router/SQRT unresolved rows for 2022–2024;
- reconstruct locked 2025 Router-abstain rows with the final integrity-passing Router chronology.

No UP threshold, expert eligibility rule, Wilson ranking rule, context bucket or tie order is changed.

## 4. External source authority

Corrected external daily source:
`gold_axis_2026/external_data/v2/dukascopy_xauusd_govsession_mid_5m_daily_features_2018_2021.csv`
at commit `509c5ffa762f4ea49644b8ffe723ed2591ba52bf`.

Transient public 1-minute path mirror:
`kevingtlin/Market-Data-Lab@922f83a60cc574e7395fb27397077288055a1ef6`.

Frozen path reconstruction:
- exact bid/ask timestamp inner join;
- mid close=(bid close+ask close)/2;
- UTC 5-minute last-close bars;
- convert to America/New_York;
- remove 17:00–17:55 maintenance hour;
- weekdays only;
- raw third-party minute files are transient and are not committed.

## 5. Mandatory integrity before scoring

### External daily/path integrity
Must reproduce the corrected external 2020–2021 daily spine:
- 518 rows;
- 276 bars/day;
- no missing/extra dates;
- close/RV/DR numerical equality within the previously frozen tolerances.

### Path-source harmonization
Use only dates representable by the frozen CBR contract (>=239 returns, positive RV).

Required:
- representable exact-date overlap >=300;
- median same-date flattened path correlation >=0.98;
- median same-date DTW <25% of deterministic shifted-date median DTW;
- >=90% of same-date DTW distances below shifted-date median.

### External SQRT integrity
Required:
- 2020 SQRT alarms=212 = 97 DOWN +115 UP;
- 2021 SQRT alarms=28 =16 DOWN +12 UP.

### External Router integrity
Required frozen annual totals:
- 2020 Router UP=185, TP=111, FP=74;
- 2021 Router UP=33, TP=19, FP=14.

Required exact SQRT×Router intersections:
- 2020 overlap=140 =80 actual UP +60 actual DOWN;
- 2021 overlap=2 =1 actual UP +1 actual DOWN.

Therefore the expected external route-consistent CBR cases are:
- 2020: 72 =37 DOWN +35 UP;
- 2021: 26 =15 DOWN +11 UP;
- pooled external route-consistent library=98 =52 DOWN +46 UP.

Any mismatch blocks interpretation.

### Governed route integrity
Frozen unresolved rows:
- 2022: 11 =6 DOWN +5 UP;
- 2023: 2 =1 DOWN +1 UP;
- 2024: 13 =6 DOWN +7 UP;
- pre-2025 pooled unresolved=26 =13 DOWN +13 UP.

Locked 2025 unresolved:
- 74 =39 DOWN +35 UP.

## 6. Route-consistent chronological CBR libraries

For every target year, only earlier matured rows that themselves satisfied:
`SQRT HIGH RISK + Router V2 ABSTAIN`
may be neighbors.

### 2022 test
Training:
- external unresolved 2020;
- external unresolved 2021.
Expected train n=98.

Test:
- governed unresolved 2022 n=11.

### 2023 test
Training:
- external unresolved 2020–2021;
- governed unresolved 2022.
Expected train n=109.

Test n=2.

### 2024 test
Training:
- external unresolved 2020–2021;
- governed unresolved 2022–2023.
Expected train n=111.

Test n=13.

### Locked 2025 transport
Training:
- external unresolved 2020–2021;
- governed unresolved 2022–2024.
Expected train n=124.

Test:
- locked 2025 unresolved n=74.

No historical `VERIFIED UP` case may enter these libraries.

## 7. Metrics

Per year and pooled 2022–2024:
- test n;
- actual DOWN/UP;
- training n and class balance;
- DOWN calls;
- correct DOWN;
- false DOWN;
- DOWN precision;
- DOWN recall;
- false-DOWN FPR;
- call coverage;
- one-sided 90% Wilson LCB;
- mean p(DOWN);
- mean nearest-neighbour distance;
- neighbour provenance by year/source.

## 8. Frozen support gates

### Pre-2025 route-consistent support
Supportive only if pooled 2022–2024:
- n=26;
- DOWN calls >=5;
- DOWN precision >0.50;
- false-DOWN FPR <0.50.

### Locked 2025 transport
Supportive only if:
- DOWN calls >=5;
- DOWN precision >39/74 =52.7027%;
- false-DOWN FPR <0.50.

2025 cannot rescue a pre-2025 failure or alter any setting.

## 9. Final statuses

- `BLOCKED_EXTERNAL_PATH_RECONSTRUCTION`
- `BLOCKED_PATH_HARMONIZATION`
- `BLOCKED_EXTERNAL_SQRT_ROUTER_MISMATCH`
- `BLOCKED_GOVERNED_ROUTE_MISMATCH`
- `CASCADE_ROUTE_CONSISTENT_NOT_SUPPORTED`
- `CASCADE_ROUTE_CONSISTENT_PRE2025_ONLY`
- `CASCADE_ROUTE_CONSISTENT_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT`

## 10. Governance

- no random split;
- no threshold tuning;
- no K/band/representation changes;
- no post-hoc exclusion of 2020 or any other year;
- 2025 locked transport only;
- 2026 excluded;
- external source research-only;
- governed DB read-only;
- no production writes;
- no runtime promotion.
