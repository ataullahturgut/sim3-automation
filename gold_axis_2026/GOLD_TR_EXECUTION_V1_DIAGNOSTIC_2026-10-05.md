# GOLD D1 — TURKIYE EXECUTION VEHICLE DIAGNOSTIC V1

**Date:** 2026-10-05
**Identity:** `TR_EXECUTION_DIAGNOSTIC_V1`
**Status:** RETROSPECTIVE OPERATIONAL DIAGNOSTIC — NO LIVE VEHICLE PROMOTION

## Objective

Test the actual use case raised by the investor:
- a D1 forecast is available in the morning;
- if the signal is UP, deploy TRY capital through a Turkish gold instrument;
- if signal is DOWN or UNCERTAIN, remain in cash;
- buy at the BIST session open and sell at the same session close.

This is deliberately different from the model's research target, which is prior XAU daily cutoff -> next daily close direction.

## Data window

Common public OHLC history available for both BIST products:
- 2026-08-04 through 2026-09-25.

Price sources:
- GCM historical BIST table for ALTINS1.
- GCM historical BIST table for GLDTR.

Signal source:
- GOLD_D1_CIG_V1_EXTENDED_JAN_SEP_REPLAY_2026-10-05.csv

The interval includes the difficult August regime and September.

## Strategy

Initial capital: TRY 100,000.

Binding CIG long-only implementation:
- CIG UP -> invest 100% at opening price, liquidate at close.
- CIG DOWN -> cash.
- CIG UNCERTAIN -> cash.
- no leverage;
- no short selling;
- capital compounds across action days.

There are 18 CIG-UP issue dates in the common window.

## Raw morning-open -> close result

### ALTINS1
- profitable action days: 8/18
- gross compounded return: **-4.3809%**
- TRY 100,000 -> **TRY 95,619**

### GLDTR
- profitable action days: 9/18
- gross compounded return: **-0.3371%**
- TRY 100,000 -> **TRY 99,663**

Thus the research model's close-to-close directional accuracy does not translate mechanically into a morning BIST-open trading strategy.

## Execution-spread lower-bound diagnostic

Observed/current quoted minimum price steps:
- ALTINS1: TRY 0.01
- GLDTR: TRY 0.25 in the observed order book / trade grid.

A deliberately optimistic one-tick round-trip execution penalty was approximated by buying half a tick above the reported open and selling half a tick below the reported close.

With zero brokerage commission:

### Binding CIG
- ALTINS1: **-4.6142%** -> TRY 95,386
- GLDTR: **-1.1251%** -> TRY 98,875

This is a lower-bound execution-cost model; actual spread/slippage can be wider.

## CPG shadow overlay — exploratory only

CPG_D1_V1 is not production-approved. Its historical use here is diagnostic only.

Within this operational window, the strict YELLOW abstention removes six morning-long dates:
- 2026-09-01
- 2026-09-10
- 2026-09-14
- 2026-09-16
- 2026-09-23
- 2026-09-25

Twelve UP trades remain.

### Gross
- ALTINS1: **+1.3124%** -> TRY 101,312
- GLDTR: **+3.0491%** -> TRY 103,049

### One-tick execution, zero brokerage commission
- ALTINS1: **+1.1475%** -> TRY 101,147
- GLDTR: **+2.5053%** -> TRY 102,505 before investor-level tax.

Current GLDTR information indicates 17.5% withholding for resident real-person fund-unit gains. Under a simplified same-quarter/same-intermediary netting approximation, the +2.5053% gain would be roughly +2.067% after withholding, or about TRY 102,067. Exact broker tax accounting must be checked on the actual account.

ALTINS1 is reported at 0% withholding.

## Brokerage sensitivity

Current Turkish brokerage costs are institution-specific.

Examples verified on 2026-10-05:
- Midas states Borsa Istanbul transactions are zero commission; ALTIN.S1 is explicitly supported.
- Herkese Borsa lists Pay Market commissions from 5 to 15 basis points per side depending on average daily volume.

At 13 bp per side plus the one-tick execution proxy, CPG shadow results fall to approximately:
- ALTINS1: **-1.96%**
- GLDTR: **-0.64%** before tax.

Therefore a high-turnover one-day strategy is very sensitive to brokerage commission. Near-zero commission is economically important.

## Bank gram-gold spread

The bank implementation cannot be backtested exactly without the investor's own bank historical bid/ask feed.

Current 2026-10-05 daytime comparison illustrates the scale:
- narrow example around ~0.8% round-trip spread;
- several large banks around ~2% to 4% or more.

This is much larger than current one-tick BIST spreads and is economically hostile to daily turnover.

Conclusion:
bank gram gold is not the preferred implementation for a one-day high-turnover strategy unless the user's actual bank quotes are exceptionally tight.

## Instrument-specific risks

### ALTINS1
Advantages:
- extremely small nominal tick/spread;
- strong liquidity;
- 0% withholding reported;
- explicit physical-gold backing/conversion framework.

Critical problem:
**basis/premium risk**.

One certificate represents 0.01 g of 0.995 gold, but market price can diverge materially from gold value. On 2026-10-05 ALTINS1 closed near TRY 71.40 while a contemporaneous gram-gold reference was around TRY 6,537/g; the simple purity-adjusted intrinsic proxy is about TRY 65.04 per certificate, implying roughly a 9.8% market premium.

The premium has been dramatically larger at other points in 2026. Therefore an investor can correctly forecast gold and still lose if the certificate premium compresses.

### GLDTR
Advantages:
- physical-gold/index tracking structure;
- creation/market-making/NAV mechanics make it structurally closer to an ETF gold exposure;
- in the tested window its morning-open implementation tracked the desired exposure materially better than ALTINS1.

Costs:
- wider tick in percentage terms than ALTINS1;
- annual management fee reported at 0.47% (already embedded in traded/NAV performance);
- 17.5% withholding reported for resident real-person gains.

## Information-clock diagnosis

This is the most important finding.

The D1 research target is approximately:
`previous XAU cutoff -> next XAU close`.

The proposed investment operation is:
`BIST morning open -> same-day BIST close`.

These are not the same return interval.

By BIST open:
- Asia/overnight XAU movement has already occurred;
- USD/TRY has moved;
- ALTINS1 premium can reprice;
- GLDTR NAV/opening auction has incorporated part of the global move.

Therefore part of the D1 alpha can already be embedded in the opening price before the investor can enter.

This explains why a reasonably accurate XAU close-to-close model can produce weak or negative BIST open-to-close returns.

## Binding operational conclusion

For immediate implementation:

1. **Do not use ordinary bank gram gold for daily turnover** unless the live round-trip spread is independently verified to be exceptionally low.
2. **Do not designate ALTINS1 as the automatic winner solely because its quoted spread is tiny.** Its premium/basis risk is material.
3. **GLDTR is structurally the cleaner XAU/TRY tracking candidate in this historical execution window**, but tax and spread must be included.
4. **CPG shows promising economic filtering but remains retrospective shadow evidence and cannot yet be treated as validated live alpha.**
5. The next production-relevant model should target the actual execution interval:
   **BIST-open (or fixed morning clock) -> BIST-close return**, separately for ALTINS1/GLDTR or a common local-gold return.

Recommended new identity:
`TR_GOLD_EXECUTION_D1_V1`.

Candidate PIT inputs at the morning cutoff:
- frozen CIG direction/state;
- CPG state;
- overnight XAU return;
- last 1h/3h XAU path;
- USD/TRY overnight return;
- ALTINS1 implied premium vs gold;
- GLDTR premium/discount vs iNAV/NAV;
- opening-auction gap;
- scheduled event clock.

The research objective becomes net economic return after spread, commission and applicable withholding — not merely XAU directional accuracy.
