# GOLD CONTROL — CBR FALSE-DOWN NEXT-ORIGIN UP RESCUE AUDIT V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `CBR_FALSE_DOWN_NEXT_ORIGIN_UP_RESCUE_AUDIT_V1_RESEARCH`  
**Purpose:** quantify whether CBR false-DOWN losses would be economically mitigated by an UP signal emitted at the immediately following origin close.  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Question

For route-consistent CBR cases where:
- SQRT = HIGH RISK,
- frozen UP Verifier V2 = ABSTAIN,
- CBR-DTW STRICT P050 = DOWN,
- realized next-day close direction = UP,

ask:

> At that realized-UP day's close, does the frozen UP Verifier emit UP for the following trading day, and if so how much of the prior false-DOWN move would the next-day long trade recover?

This is a trading-path audit, not model tuning.

## 2. Frozen sources

CBR route-consistent ledger:
`GOLD_CONTROL_CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_LEDGER_2026-09-23.csv`
from frozen result commit:
`b22235f04dc48b173a93a98cc2ce22081bb0054e`.

Frozen SQRT parent:
`DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH`
at commit:
`2926796b6a7e9048d2c091c9c571cb928b773e02`.

Frozen Router V2 reconstruction:
final integrity-passing implementation from:
`7982b422476df61eb0339b74265afd553414f2d2`.

## 3. False-DOWN universe

Exact false-DOWN definition:
- CBR `down_call=1`;
- realized `actual_up=1`.

Expected counts before scoring:
- 2022: 4;
- 2023: 0;
- 2024: 3;
- locked 2025: 16.

If these do not reproduce exactly, block.

## 4. Immediate next-origin signal

For each false-DOWN target date T:

1. locate the frozen Router row whose `origin_date=T`;
2. record its next target date T+;
3. record standalone Router V2 UP/ABSTAIN;
4. join the frozen SQRT parent row at origin T;
5. record whether the high-risk cascade itself would have activated on T.

Two signal notions are reported separately:

- **Standalone next-origin UP:** Router V2 emits UP at close T, regardless of SQRT.
- **Cascade next-origin VERIFIED UP:** SQRT at origin T is HIGH RISK **and** Router V2 emits UP.

Do not conflate them.

## 5. Economic accounting

The previous false-DOWN trade is assumed to be:
- short from prior origin close to T close.

Its gross loss is the realized simple long return over that interval.

If an immediate next-origin UP signal exists, a hypothetical next trade is:
- long from T close to T+ close.

Report:
- prior short loss;
- following long return;
- additive fixed-notional two-leg net = `-prior_up_return + next_long_return`;
- amount of prior loss recovered by a positive next long return;
- whether recovery is full (`next_long_return >= prior_loss`), partial, zero, or negative.

No leverage, fees, spread or slippage.

This audit does **not** claim that a T-close UP signal can prevent the loss already realized from prior-origin close to T close. It only measures whether a next-day reversal signal would economically recover some or all of that loss on the following trade.

## 6. Annual summaries

For each year report:
- false-DOWN count;
- immediate standalone Router-UP count/rate;
- immediate cascade VERIFIED-UP count/rate;
- total prior false-DOWN gross loss;
- total following-day long return on standalone-UP cases;
- total additive two-leg net on standalone-UP cases;
- count fully recovered / partially recovered / not recovered;
- same statistics for cascade VERIFIED-UP cases.

Also provide exact row ledger.

## 7. Governance

- no model changes;
- no threshold changes;
- no random split;
- 2025 remains retrospective locked transport only;
- 2026 excluded;
- no use of these outcomes to retune Router, SQRT or CBR;
- DB read-only;
- no production writes;
- no runtime promotion.
