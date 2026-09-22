# GOLD CONTROL — ROUTER V2 HISTORICAL EXTENSION V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `ROUTER_V2_HISTORICAL_EXTENSION_V1_RESEARCH`  
**Purpose:** extend the frozen UP Router V2 logic backward to obtain additional pre-2025 same-clock SQRT-alarm support for risk-control calibration.  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. Binding principle

The frozen Router V2 rules are not changed.

This study reconstructs the same direct expert definitions and the same legacy competence context on earlier years using only information available at each origin.

No 2025 data are used.

## 2. Direct expert definitions

Reconstruct exactly:

- TTSM-S2
- TTSM-S1
- Bonato AR1_RM QBoost h=1 median direction
- AR1_RM_LOGIT
- RM_LOGIT

Source panel:
- `public.xau_intraday_research_cache_5m`
- timezone: America/New_York
- retained day: weekday with at least 240 five-minute bars
- source begins 2020-01-01, as in the frozen expert scripts.

Frozen expert parameters remain unchanged:
- TTSM: momentum 20d; semivariance 5d; 250d reference; q=0.80 nearest rank.
- Bonato: h=1; AR1_RM features; median quantile; step size 0.1; m_break initial 10; m_max 500; minimum 250 training rows.
- Logit: minimum 250 training rows; ridge 1e-6; direction threshold 0.5; same feature definitions.

## 3. Historical Router protocol

For evaluation year Y in {2022, 2023, 2024}:

- initialize competence history using only target-year Y-1 common expert rows;
- within Y, add outcomes only after their target date has matured;
- use exact frozen Router V2 eligibility:
  - current expert must emit UP;
  - same legacy bucket history when expert has >=30 UP calls there, else global matured history;
  - historical UP calls >=30;
  - historical UP precision >0.50;
  - historical false-UP FPR <0.50;
- rank by one-sided 90% Wilson lower bound;
- tie-break lower FPR, higher raw precision, then fixed identity:
  TTSM-S2 > TTSM-S1 > Bonato AR1_RM > AR1_RM_LOGIT > RM_LOGIT;
- if none eligible -> ABSTAIN.

This yearly Y-1 formation protocol is chosen before reconstruction because it reproduces the frozen 2024 Router V2 design exactly: 2023 formation -> 2024 evaluation.

## 4. Legacy context

Reconstruct without change:

- FAST_UP = SMA20 + two completed-day persistence ROBUST_UP;
- SLOW_UP = completed-week SMA4 + two completed-week persistence ROBUST_UP;
- MONTHLY_UP = mean of last 3 completed monthly returns >0;
- CONSENSUS_UP iff at least 2 of the 3 are UP;
- otherwise NON_CONSENSUS_UP.

Legacy states are competence context, not direct votes.

## 5. Integrity validation

Before accepting the historical extension:

1. reconstructed 2023/2024 direct-expert rows must align exactly in target date and actual direction with frozen artifacts;
2. reconstructed 2024 Router V2 standalone counts must reproduce the frozen result:
   - n=205;
   - UP outputs=42;
   - TP=26;
   - FP=16;
   - precision=61.9048%;
   - false-UP FPR=18.6047%;
3. 2024 SQRT alarm intersection must reproduce:
   - 4 Router-UP veto opportunities;
   - 3 actual UP / 1 actual DOWN.

Failure of reproduction blocks use of earlier rows.

## 6. Historical support objective

After integrity passes, report for 2022, 2023 and 2024:

- exact common daily rows;
- Router UP outputs / abstentions;
- Router UP precision and false-UP FPR;
- SQRT alarm count;
- actual-DOWN SQRT alarms;
- actual-UP SQRT alarms;
- Router-UP overlap on SQRT alarms.

Primary support question:

> how many actual-DOWN SQRT alarm cases exist in the combined 2022–2024 same-clock calibration population?

The previous LTT support requirement is at least 11 actual-DOWN SQRT alarms for alpha=0.20, delta=0.10 under a single-policy zero-error best case.

## 7. Forbidden actions

Do not:
- use 2025;
- alter expert rules;
- lower minimum training support;
- alter Router eligibility;
- backfill missing expert outputs with future information;
- use nearest-date joins;
- treat 2021/2022 rows as frozen historical artifacts unless reconstructed from origin-safe source data.

## 8. Governance

- read-only DB;
- no random split;
- no production writes;
- no runtime promotion.
