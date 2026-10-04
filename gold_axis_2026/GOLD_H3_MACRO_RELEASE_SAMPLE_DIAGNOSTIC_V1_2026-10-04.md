# GOLD H3 — MACRO RELEASE SAMPLE DIAGNOSTIC V1

**Date:** 2026-10-04  
**Sample:** 2025-03-01 .. 2025-06-30  
**Status:** retrospective mechanism diagnostic; not a promotion claim.

## Scope

Scheduled U.S. releases:
- ADP
- Nonfarm Payrolls (NFP)
- JOLTS
- CPI
- PCE
- FOMC

Unique event dates in the sample: **22**.

Two clocks were tested:

1. **Pre-release origin:** latest H3 feature cutoff before the release.
2. **Post-release origin:** H3 feature cutoff on the release date, after the release is already known.

This distinction is necessary because a release can flip Gold intraday before the canonical H3 origin and therefore disappear from a naive same-day reversal count.

## Aggregate result

### Post-release H3 reversal

- event dates: **7 / 22 = 31.82%**
- all H3 origins in Mar-Jun 2025: **35 / 79 = 44.30%**

Scheduled release days were **not enriched** for terminal H3 reversal.

### Intraday momentum state flip into the event-day cutoff

Compare the prior available origin 12h momentum to the release-day origin 12h momentum:

- event dates: **12 / 22 = 54.55%**
- non-event dates in the same period: **30 / 56 = 53.57%**

Again, the presence of a major scheduled release by itself adds essentially no discrimination.

### Pre-release origin reversal over the following H3

- all events: **9 / 22 = 40.91%**
- missed by V5: **3 / 22**

By event family:

| Event | N | Pre-release H3 reversal |
|---|---:|---:|
| FOMC | 3 | 2 / 3 = 66.7% |
| ADP | 4 | 2 / 4 = 50.0% |
| JOLTS | 4 | 2 / 4 = 50.0% |
| CPI | 4 | 2 / 4 = 50.0% |
| PCE | 4 | 2 / 4 = 50.0% |
| NFP | 4 | 0 / 4 = 0.0% |

The sample is far too small to generalize these family-specific rates.

## Actual-versus-consensus examples

The sample contains clear surprises in both directions:

- 2025-03-05 ADP: **77K vs 140K expected** — large labor downside surprise.
- 2025-04-02 ADP: **155K vs 115K expected** — upside labor surprise.
- 2025-04-29 JOLTS: **7.192M vs 7.480M expected** — labor-demand downside surprise.
- 2025-05-02 NFP: **177K vs 130K expected** — upside labor surprise.
- 2025-06-03 JOLTS: **7.391M vs 7.100M expected** — upside labor-demand surprise.
- 2025-06-04 ADP: **37K vs 110K expected** — very large downside labor surprise.
- 2025-03-12 CPI: **0.2% m/m vs 0.3% expected**, 2.8% y/y vs 2.9%.
- 2025-04-10 CPI: **-0.1% m/m vs +0.1% expected**, 2.4% y/y vs 2.6%.
- 2025-05-13 CPI: **0.2% m/m vs 0.3% expected**, 2.3% y/y vs 2.4%.
- 2025-06-11 CPI: **0.1% m/m**, 2.4% y/y vs 2.5% expected.
- 2025-03-28 core PCE: **0.4% m/m**, hotter than the roughly 0.3% expectation.
- 2025-05-30 core PCE: **0.1% m/m**, mild/in-line.
- 2025-06-27 core PCE: **0.2% m/m vs 0.1% expected**.

Yet the sign of the macro surprise is not a stable reversal rule.

Examples:
- Apr-02 strong ADP coincided with an UP -> DOWN H3 reversal.
- May-02 stronger-than-expected NFP occurred with a DOWN -> UP H3 reversal, opposite the simple rates-channel expectation.
- Jun-04 extremely weak ADP occurred after the event-day momentum had turned UP, but H3 subsequently reversed DOWN.
- Cooler CPI releases in March, April and June did not consistently produce a new H3 reversal after the release-day origin.

## Fed-expectation examples

Expectation repricing is measurable, but still not sufficient alone.

- Jun-11 cooler CPI raised the September cut probability from about **57% to 68%**; the event-day H3 did **not** reverse the prevailing UP momentum.
- Jun-18 FOMC raised the September cut probability from about **58% to 64%**; the event-day H3 did **not** reverse the prevailing DOWN momentum.
- Mar-19 FOMC retained a median projection of two 2025 cuts, but the event-day H3 did reverse UP -> DOWN.

Therefore even an observable Fed-funds repricing cannot be treated as a direct Gold reversal sign.

## Scientific conclusion

The hypothesis:

> "important U.S. release + surprise / Fed repricing => Gold reversal"

is **not supported** in this sample as a standalone rule.

The more plausible structure is conditional:

1. pre-existing Gold trend is fragile;
2. macro surprise changes rate expectations materially;
3. the cross-asset reaction confirms the repricing;
4. Gold fails to absorb that repricing in the old momentum direction.

The event and surprise are therefore **catalysts**, not sufficient reversal signals.

## Decision

Do **not** generalize a release-calendar or actual-minus-consensus rule from this sample.

If this line continues, the next test should condition macro surprise on:
- frozen internal susceptibility state;
- 2Y yield reaction;
- Fed-funds expectation change when observable;
- post-release Gold reaction / failed continuation.

That test must distinguish the first intraday reaction from the subsequent H3 direction.
