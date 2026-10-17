# CLAUDE P7 — Shanghai gold market information: SOURCE / FIRST-PRINT SURVEY — **BLOCKED (no auditable as-of data)**

Date: 2026-10-12. Protocol PR #93, stage P7: "Only source/cost/first-print survey until auditable
as-of data exists; no paid data without user approval." No model was fitted and no XAU/USD return
was examined for P7.

## Mechanism and clock fit (why it is worth unblocking)
- SGE Shanghai Gold Benchmark Price (SHAU) auctions run at 10:15 and 14:15 Beijing (UTC+8), which is
  **05:15 and 09:15 TR**. The AM fix precedes the 08:45 DAY decision. Both fixes precede the 16:30
  OVN decision.
- SHFE gold night session opens at 21:00 Beijing = **16:00 TR**, so its first 30 minutes are known at
  the 16:30 OVN decision. Ma, Bouri, Xu & Zhou (2025, GFJ) report that the first half-hour of the
  Chinese **night** session predicts later same-session returns (Chinese futures; not verified for
  XAU/USD at our horizon).
- The Shanghai–London premium reflects local demand, import quotas and VAT (WGC 2022 note). It is
  information that is not in XAU/USD's own past price only if it is measured separately from the
  CNY rate.

## Data availability (2026-10-12)
| Item | Status |
|---|---|
| Neon tables for SGE / SHFE | **none** (full public table list checked) |
| Onshore USD/CNY at fix time | only `DEXCHUS` (FRED/H.10 noon NY, release-lagged) is in Neon; no intraday CNY/CNH |
| SGE benchmark history | public display pages (SGE site, third-party mirrors such as Kitco, metalcharts.org, findbullionprices) show AM/PM tables; **no official bulk download found**, and third-party tables differ in dates and coverage; licensing not verified |
| SHFE AU intraday (night session) | exchange/vendor data; not in Neon; cost and license unknown |
| First-print timestamps | none of the surveyed sources gives a publication timestamp per fix, so as-of integrity cannot be proven |

## Verdict
**P7 BLOCKED.** Nothing was scraped or synthesized. The program question cannot be tested without
time-stamped Shanghai prices and a matching CNY rate.

## Smallest auditable next step (needs user decision; no cost incurred yet)
1. Obtain the official SGE SHAU AM/PM history (direct from SGE, or a licensed vendor), plus intraday
   onshore CNY at 10:15/14:15 Beijing. Verify against two independent sources.
2. Or start **prospective** capture of SHAU AM/PM and SHFE night-session first-half-hour prices with
   receipt timestamps, so a clean test exists in 12–24 months.
3. Test design when available: Shanghai premium change and SHFE night first-half-hour return as
   inputs for OVN (16:30) and DAY (08:45), against P1's RW/INT/always-UP baselines.

Sources: [Kitco SGE benchmark](https://www.kitco.com/price/fixes/shanghai-benchmark),
[metalcharts.org SGE](https://metalcharts.org/sge),
[findbullionprices Shanghai](https://findbullionprices.com/spot-prices/gold-price/shanghai),
[WGC Shanghai–London spread note (2022)](https://www.gold.org/goldhub/gold-focus/2022/10/sky-high-recent-surge-shanghai-london-gold-price-spread),
[Ma et al. 2025, GFJ](https://ideas.repec.org/a/eee/glofin/v64y2025ics1044028325000110.html).
