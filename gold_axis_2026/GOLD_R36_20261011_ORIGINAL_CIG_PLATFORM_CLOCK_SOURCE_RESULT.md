# R36: Original CIG-D1 data platforms and their source clocks (11 Oct 2026)

**Scope:** trace the OLD forecast model's original platforms, rather than inferring timestamps from a newly sourced quotation. Do not re-fit or select clocks by hit rate.

## Original code, immutable source and findings

Original H3 DAILY MODEL raw data: `gold_axis_2026/tools/gold_short_horizon_global_xau_readiness_r2.py` directly fetched GitHub `lbruton/StakTrakr/data/spot-history-{YEAR}.json`. R2 source pinned at commit `54fdf1c8d39b7b6c7b874d0f30f784296e886044`, confirmed by `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_READINESS_SUMMARY_2026-10-02.json`. Gold/Silver/Platinum/Palladium daily prices and daily directional targets are derived from the named date's `spot` price.

Original H3 INTRADAY FEATURES came from **a different platform**: `gold_axis_2026/tools/gold_h3_iris_v1.py` explicitly requests `api.twelvedata.com/time_series?symbol=XAU/USD&interval=1h&timezone=America/New_York`, with earlier Neon series `XAU_USD_TWELVE_1H_RESEARCH_V1`. Model feature cutoff: **16:00 New York on the previous feature date** = **00:00 Türkiye next day in US winter**, **23:00 Türkiye same day in US summer**. Governing issue deadline: **08:00 NY on forecast date** = **16:00 Türkiye US winter /15:00 Türkiye US summer**. The hourly Twelve Data feature cutoff is not the time at which the daily target Gold price is fixed.

Critically, the frozen OLD CIG 145-date **realization** file `GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv` matches ALL 145 prices exactly in a DIFFERENT Stak historical snapshot, commit `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`. That produces the published 125 predictions and 93 correct (74.40%). Across 125 CIG dates, 9 DAILY DIRECTION labels differ when re-labelled using the 54f frozen clean source vintage: 88/125 (70.40%). These mixed-vintage scores are retrospective, not live executable results.

## Direct source metadata, without using Dukascopy to guess provenance

Checked `data/spot-history-2023.json`, `2024.json`, `2025.json` at original input-pinned Stak commit 54f: **2023 251/251 Gold rows seed/LBMA; 2024 254/254 seed/LBMA; 2025 253/253 seed/LBMA.** This explains why 2023–25 daily target clocks cannot be regarded as UTC calendar-day averages simply because 2026 sqld records are later averages.

Original 2026 CIG exact old realizations at pinned Stak commit ed2:
- **Jan 2–Feb 11:** 29 **seed/LBMA** days, 25 CIG signals with 18 correct. LBMA starts gold auction at 10:30 London (winter **13:30 Türkiye**) and 15:00 London (**18:00 Türkiye**). The upstream Stak `provider=LBMA` alone does NOT identify AM vs PM or the final auction time; R35 independently found 26 first-party Dukascopy M15 quote days matching AM 13:30 (price MAE $3.43) far more closely than PM 18:00 ($21.35). Strongly AM-like, not a licensed final fixing equivalence proof.
- **Feb 12–20 and Mar 9:** 8 **seed/MetalPriceAPI** days, 7 CIG signals with 5 correct. Original Stak seed updater calls `api.metalpriceapi.com/v1/timeframe`. Official MetalpriceAPI FAQ says daily historical date D timestamp is **23:59:59 UTC** (**02:59:59 Türkiye D+1**) and first available **00:05 GMT the following day** (**03:05 Türkiye D+1**). The timestamp is a daily-date convention, not proof of an exact single spot transaction at 02:59:59.
- **Feb 23–26:** 4 **seed/StakTrakr** days, 4 signals with 2 correct. Original `devops/pollers/shared/spot-poller/poller.py` hard-codes `NOON_HOUR = 17` UTC (20:00 Türkiye) and triggers daily seed on first subsequent `/latest` poll. Exact first-write clock not in historical file.
- **Mar 10–Jul 31:** 104 **sqld** days, 89 signals with 68 correct. Original platform `.agents/skills/update-spot-bundle/update-spot-bundle.py` groups `DATE(timestamp_floor)` and computes **AVG(spot)** from original spot poll DB. Original `spot-extract.js` writes UTC timestamp. Thus **UTC calendar-day grouping = Türkiye 03:00 until next day's 03:00**, a daily AVERAGE of original app's available poll measurements. It is NOT a 03:00 buy and next-day 03:00 sell return. Original poll completeness is unknown without private original DB.

**Important:** Stak saved `YYYY-MM-DD 12:00:00` on every daily history row is explicitly a **synthetic noon date label**, NOT actual observation at 12UTC (15Türkiye). Do not apply naive timestamp timezone conversion.

## Genuine inference and limitations

The original time identity is proven from the ORIGINAL SOURCE CODE and attached source/provider metadata. **There is NO single original 24-hour spot-to-spot horizon that explains all historical 74.4% source labels**: most old historical data through 2025 is LBMA benchmark-labelled, while later 2026 records are UTC calendar daily AVG; intervening dates use MetalPriceAPI EOD and Stak poll seed. Twelve Data was an intraday FEATURE vendor, not the frozen old CIG DAILY REALIZATION vendor.

The 2023–25 Stak LBMA rows do not record whether AM or PM official fixing was copied. Strong Jan–Feb 2026 AM correspondence alone must not be promoted to proven 2023–25 AM clock.

Original CIG issue deadline 16TR winter/15TR summer could be **after** same-date LBMA AM auction (13:30 winter/12:30 summer); real retrospective signal production timestamps are not recorded. The 74.40% historical label hit rate is not evidence of an actionable price movement following signal issuance. It is equally wrong to claim all historical edge was noncausal without checking whether original inputs allowed earlier lawful issuance.

External publisher authoritative timing: LBMA https://www.lbma.org.uk/prices-and-data/lbma-precious-metal-prices ; MetalpriceAPI https://metalpriceapi.com/faq ; Twelve Data https://support.twelvedata.com/en/articles/5745849-timezones .

Other project evidence: `GOLD_DAILY_REALIZATION_SOURCE_AUDIT_2026-10-06.md`, `GOLD_R35_20261011_CIG_D1_SOURCE_CLOCK_MONTH_AND_WEEK_FORENSIC_RESULT.md`. Original H3 R2 source: `GOLD_SHORT_HORIZON_GLOBAL_XAU_R2_READINESS_SUMMARY_2026-10-02.json`.

**NEXT FORENSIC ACTION:** identify AM-versus-PM LBMA fixing for 2023–25 from authentic benchmark identification or same-era original source record; recover old sqld raw poll time stamps if accessible; reconstruct original date-labelled vendor-specific outcomes without retuning model and with true source-ready forecast timestamps. These are different from retargeting to an investor spot clock.

**FINAL RESULT SUPERSESSION (2026-10-11):** See `GOLD_R37_20261011_CIG_D1_ORIGINAL_LBMA_AM_CLOCK_AND_CAUSAL_FORWARD_VERDICT.md`. Original Stak 2023–25 LBMA daily prices were matched to London AM (not PM) by independent 2023/24/25 HistData M15. Most importantly, 2025 EXACT same 218 frozen CIG signals scored 176/218=80.73% on PRIOR-AM to issue-day AM old label, but only **118/218=54.13%** on the **08NY issue instant to next LBMA AM** post-issue return, exactly equal to always-UP baseline on those same rows. Do not market 80.73% or 74.40% as post-issuance daily investable success.
