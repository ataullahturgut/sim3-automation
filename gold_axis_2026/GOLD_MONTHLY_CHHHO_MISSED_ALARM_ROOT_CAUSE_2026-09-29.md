# GOLD MONTHLY — ChHHO Missed-Alarm Root-Cause Research

**Date:** 2026-09-29  
**Status:** EXPLORATORY MECHANISM DISCOVERY COMPLETE / NEW ALARMS NOT YET VALIDATED  
**Scope:** Alarm detection only. No routing, no fallback-model selection, no model switching.

## 1. Question

The frozen A/B/C/D alarm set detected only 3 of 13 post-DEV high-error months (2025 + 2026 Jan-Aug, high error = DEV-Q3 AE > 63.06 USD).

This report asks:

1. Why were the missed high-error months not visible to A/B/C/D?
2. Do the missed months share origin-visible patterns?
3. Do similar market states exist before 2025?
4. What new alarm families are scientifically worth testing next?

The answer is not one new rule. The missed months separate into at least three different mechanisms.

## 2. Missed months and origin-visible state

| Target | ChHHO AE | APE | Origin state summary |
|---|---:|---:|---|
| 2025-01 | 79.28 | 2.93% | Gold -0.46% 1m; +2.91% 3m; +10.74% vs trailing 12m mean; no major simple-market OOD |
| 2025-02 | 114.26 | 3.95% | Gold +2.38%; +10.81% vs MA12; Broad USD and yields rising; simple A-D sign rules not triggered |
| 2025-05 | 90.25 | 2.73% | Gold +7.44% 1m / +17.09% 3m; +20.87% vs MA12; realized-vol ratio 2.18; ChHHO only +0.02% |
| 2025-10 | 206.11 | 5.08% | Gold +8.55% 1m; +19.35% vs MA12; ChHHO UP but magnitude too small |
| 2025-11 | 163.94 | 4.01% | Gold +10.38% 1m / +19.41% 3m; +27.66% vs MA12; vol ratio 2.10; ChHHO -3.39% |
| 2026-01 | 458.50 | 9.65% | Gold +5.14% 1m / +16.17% 3m; +25.15% vs MA12; ChHHO -0.34% |
| 2026-03 | 145.62 | 3.00% | Gold +5.59% 1m / +20.62% 3m; +32.70% vs MA12; vol ratio 2.08; ChHHO -6.37% |
| 2026-06 | 362.17 | 8.57% | Gold -2.82% 1m / -8.88% 3m; +10.26% vs MA12; ordinary price-state OOD score; ChHHO near flat |
| 2026-07 | 82.68 | 2.03% | Gold -8.15% 1m / -11.61% 3m; shock state; ChHHO -5.79% and overshoots magnitude |
| 2026-08 | 347.99 | 7.89% | Gold -3.78% 1m / -14.76% 3m; post-liquidation drawdown; ChHHO -0.25%; subsequent sharp rebound |

A/B/C/D were designed mostly around **sign relationships** among metals, USD, rates and ChHHO direction. Many of the missed months are instead **magnitude / state-space / flow / volatility** failures.

## 3. Root cause family E — trend / level OOD + ChHHO mean-reversion disagreement

The strongest newly observed cluster is:

- 2025-05
- 2025-11
- 2026-01
- 2026-03
- with 2025-10 as a related continuation-magnitude case.

These origins show combinations of:
- very strong 1–3 month Gold momentum;
- Gold far above its trailing 12-month mean;
- often elevated intramonth realized volatility;
- ChHHO forecasting near-flat or a material reversal.

A descriptive post-hoc condition:

- Gold price > 20% above trailing 12m mean; and
- |ChHHO forecast return − current 1m Gold return| > 5 percentage points

fires post-DEV at:
- 2025-05 — AE 90.25
- 2025-11 — AE 163.94
- 2026-01 — AE 458.50
- 2026-03 — AE 145.62

All four are high-error months.

**Important:** this is discovery evidence only. The condition was found after inspecting the misses and therefore is not a validated alarm.

### Historical rarity / precedent

Before 2025, Gold monthly average >20% above its trailing 12m average is rare in the governed 2010–2024 history:
- 2011-08: +21.50%; next month +1.19%
- 2020-08: +20.36%; next month -2.45%

At the broader >15% level, examples include:
- 2011-08 / 2011-09
- 2020-07 / 2020-08 / 2020-09
- 2024-04
- 2024-09 / 2024-10

The subsequent direction is mixed at the most extreme level, which means the correct alarm is not “continue trend” or “reverse trend.” It is:

> **MODEL EXTRAPOLATION / MAGNITUDE RISK IS HIGH BECAUSE CURRENT STATE IS OUTSIDE NORMAL TRAINING GEOMETRY.**

### Historical momentum persistence

In 2011–2024 there are 14 origin months with Gold monthly-average return > +5%.

- next month positive: 11/14 = **78.6%**
- mean next-month return: **+1.57%**
- mean absolute next-month return: **2.79%**

Examples:
- 2019-06 +5.71% -> next +4.05%
- 2020-07 +5.98% -> next +6.84%
- 2024-03 +6.35% -> next +7.92%
- 2024-09 +3.97% -> next +4.64% (near-threshold continuation)

This explains why a model that automatically compresses/extinguishes strong momentum can be fragile.

## 4. Root cause family F — gold-specific flows / derivatives / liquidity

Some missed months are poorly described by static price/rate/USD states.

### 2025 regime

World Gold Council evidence shows that 2025 introduced unusually strong gold-specific investment channels:
- January all-time highs with tariff fears, GPR, weaker USD and bond-yield support.
- February had US$9.4bn / 100t ETF inflows, the strongest month since March 2022, plus tariff-related COMEX inventory distortions.
- Q1 gold ETF inflows were the strongest quarter in three years.
- April added about US$11bn ETF inflows and elevated volatility/trade-policy risk.
- September had record monthly ETF inflows and increased COMEX managed-money exposure.
- October/November/December retained unusually strong ETF, options and futures activity.

These variables are not represented directly in CURRENT8 or A/B/C/D.

### 2026 regime

The missing-flow mechanism becomes even clearer:
- January 2026 gold rose about 14%; WGC attributes roughly half the month's modeled contribution to implied-volatility/options activity and reports +120t ETF inflows.
- March 2026 was described by WGC as the weakest month since June 2013 and primarily a deleveraging/liquidity episode rather than a normal macro-fundamental move.
- June 2026 experienced broad ETF outflows of US$8.9bn / 74t. US Q2 analysis characterizes March and June as discrete liquidation episodes rather than uniformly weak demand.
- August 2026's +13% rally was driven heavily by ETF flows, futures flows and options activity; managed-money and other-reportable COMEX positions rose materially.

This is a strong explanation for why VIX, rates and USD can fail to warn: the missing state is **gold-market positioning/option/flow pressure**.

## 5. GVZ is materially different from VIX

The current alarm work has VIX, which measures equity-market implied volatility.

Cboe GVZ instead estimates expected 30-day volatility of GLD from gold ETF options.

Official FRED/Cboe history runs from 2008 onward, making a full historical origin-safe test possible.

Relevant examples:
- Apr 2025 GVZ reached roughly 28 before ending Apr at 21.52.
- Oct 2025 GVZ rose from ~19 at month-start to a peak of 32.78.
- Dec 31 2025 GVZ = 23.92.
- Jan 29 2026 GVZ = 46.02; Jan 30 = 44.08.
- Feb 2026 remained around the low/mid-30s and March later spiked above 45.
- May 29 2026 = 24.91; June reached 32.18 and 31.60 on separate days.
- Jul 31 2026 = 23.31.

Therefore a gold-specific volatility family is scientifically justified to test; VIX failure does not imply GVZ failure.

## 6. Root cause family G — post-liquidation / reversal-risk state

2026-07 and 2026-08 form another cluster.

At the 2026-06 origin:
- Gold 1m = -8.15%
- Gold 3m = -11.61%

At the 2026-07 origin:
- Gold 3m = -14.76%

Historical 2011–2024 evidence:

### One-month Gold drop < -5%
7 historical origins:
- next-month up rate = **57.1%**
- mean next-month return approximately flat
- mean absolute next-month return = **3.18%**

### Three-month Gold drawdown < -10%
6 historical origins:
- next-month up rate = **50%**
- mean absolute next-month return = **4.03%**

Examples:
- 2013 Apr–Jul prolonged liquidation sequence, followed by a +4.62% August rebound.
- 2016-12: -7.37% monthly move / -14.10% 3m state, followed by +3.45% in Jan 2017.
- 2022-07: -5.40%, followed by +1.53% in August.

Thus extreme drawdown states do not produce a reliable directional sign, but they do produce **elevated next-month movement / reversal uncertainty**.

The correct proposed alarm is:

> **POST-LIQUIDATION / HIGH-UNCERTAINTY**

not “predict UP.”

## 7. Why 2026-06 is special

2026-06 is the hardest missed alarm to explain with existing market-state variables.

At the May origin:
- Gold -2.82% 1m
- -8.88% 3m
- price still +10.26% above MA12
- ordinary realized-vol state
- ChHHO nearly flat

This origin is not an obvious price-space outlier.

WGC's May commentary already showed:
- global ETF outflows;
- improved risk sentiment;
- falling implied volatility;
- “opaque flows”, potentially OTC, contributing to unexplained weakness.

June then became a concentrated liquidation month, with heavy global ETF outflows and broad regional selling.

Conclusion:

> 2026-06 is evidence that **state variables alone are insufficient**. A real alarm layer likely needs contemporaneous gold-specific flow/positioning information.

## 8. A measurement issue: fixed USD error threshold

The frozen alarm transport uses DEV Q3 = 63.06 USD because project selection is based on USD ΣAE.

But at Gold around US$4,000–5,000, 63 USD is only roughly 1.3–1.6%.

This is why some “high AE” misses are modest percentage misses:
- 2025-01: 2.93%
- 2025-05: 2.73%
- 2026-07: 2.03%

The project target/primary metric does **not** need to change.

But the future alarm target should likely model **error risk in normalized return/percentage space and translate it back into expected USD error at the current price level**, otherwise the alarm label becomes mechanically easier to trigger as Gold's nominal price rises.

This is an alarm-calibration issue, not a proposal to replace ΣAE.

## 9. New alarm families worth testing next

These are hypotheses, not validated alarms.

### E — TREND_OOD / MODEL-DISAGREEMENT
Candidate origin-safe ingredients:
- Gold distance from trailing 12m mean;
- 1m / 3m momentum;
- realized-vol ratio;
- distance of current state from historical training cloud;
- ChHHO forecast-vs-current-momentum gap.

Targets: 2025-05, 2025-10/11, 2026-01, 2026-03.

### F — GOLD FLOW / DERIVATIVES PRESSURE
Candidate PIT-safe ingredients:
- GVZ level/change/spike;
- CFTC Gold Managed Money net position and weekly change;
- Other Reportables / non-reportable positioning;
- open interest / gross leverage;
- gold ETF holdings/flows;
- where available, options activity proxies.

Targets: 2025 early-year flow regime, 2026-01, 2026-06, 2026-08.

### G — POST-LIQUIDATION / REVERSAL-RISK
Candidate origin-safe ingredients:
- trailing 1m/2m/3m Gold drawdown;
- realized volatility / range;
- GVZ state;
- ETF/CFTC stabilization after selling;
- breadth across Silver/Pt/Pd.

Targets: 2026-07 and 2026-08.

### H — EVENT-RISK STATE (secondary)
Known-before-origin calendar/policy risk may supplement the above:
- Fed/CPI calendar;
- scheduled political/tariff deadlines;
- other known policy events.

This cannot cover genuinely unscheduled shocks and should not be treated as a primary detector.

## 10. Feasibility of historical testing

The key missing datasets are historically testable:

- **GVZ:** Cboe/FRED daily history from 2008.
- **CFTC Disaggregated COT:** official weekly historical data from 2009, including Managed Money and Other Reportables; release timing must be lagged correctly.
- **Gold ETF flows/holdings:** WGC provides historical fund-flow/holding data; PIT availability/release dates must be governed before use.

Therefore the new alarm hypotheses can be tested on older history rather than being judged only on 2025/2026 anecdotes.

## 11. Decision

The missed alarms are not one homogeneous failure.

Current evidence supports three distinct missing mechanisms:

1. **TREND/LEVEL OOD + ChHHO mean-reversion disagreement**
2. **GOLD-SPECIFIC FLOW / DERIVATIVES / LIQUIDITY pressure**
3. **POST-LIQUIDATION high-uncertainty / reversal-risk**

The next stage should remain alarm research only:

1. build origin-safe E/F/G diagnostic features;
2. reconstruct them historically;
3. test whether they appear before high ChHHO errors without producing excessive false alarms;
4. keep A/B/C/D frozen;
5. do not test routing or fallback selection yet.

## Sources

- World Gold Council, Gold Market Commentary Jan/Feb/Apr/May/Sep 2025 and Jan/Mar/May/Jul/Aug 2026.
- World Gold Council, gold ETF holdings/flows reports.
- Cboe, GVZ Index methodology/dashboard.
- FRED, GVZCLS daily Cboe Gold ETF Volatility Index.
- CFTC, historical Disaggregated Commitments of Traders reports.
