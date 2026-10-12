# GPT-6 P2 independent gold FOMC reversal — negative result

**NO PROMOTION.** Frozen plan `9f5d84a` before event data extraction. The underlying 2025 *FX* publication Lee & Wang is not gold evidence and its pre-FOMC drift target differs from a post-statement shock response (see SSRN 4386170). Actual gold experiment uses archived EV/Dukascopy M15 XAUUSD bid/ask mids around preannounced 14:00 **America/New_York** regular meetings, future **next calendar day 09:00→16:45 TRT** return. All 47 planned matched; DEV2020–24 n39; opened2025 n8. Off-schedule 2020 pandemic Fed actions excluded. Event dates confirm to Federal Reserve statement list; macro high frequency alternative first-print timestamp historical source is 2026 backfill, not live capture.

Hpre x = ln(mid(t0−15m)/mid(t0−60m)); Hpost x = ln(mid(t0+45m)/mid(t0−15m)). Both known by next DAY 08:45 decision; predictor next DAY sign = opposite x sign, no learned model or lookahead. These are separate from event-day contemporaneous shock explanations.

| Year | N | Reverse pre-FOMC correct | Reverse post-FOMC first45 correct | Always-UP |
|---|---:|---:|---:|---:|
| 2020 | 7 | 4 | 3 | 5 |
| 2021 | 8 | 5 | 2 | 4 |
| 2022 | 8 | 5 | 2 | 4 |
| 2023 | 8 | 5 | 5 | 1 |
| 2024 | 8 | 4 | 4 | 3 |
| 2025 opened | 8 | 5 | 5 | 6 |
| **2020–24** | **39** | **23/39 = 58.97%** | **16/39 = 41.03%** | **17/39 = 43.59%** |

Hpre paired exact sign-vote McNemar vs ALWAYS-UP wins 11, losses5, one-sided p=.1051, two-family Holm **p=.2101**, 2024 4/8 not >50%; x_pre vs future signed return correlation **+0.0994** contradicts hypothesized negative continuous relationship. Hpost 16/39, Holm p=.6494 and correlation +.0975. Strong 2023 5/8 occurs amid uncommon DOWN=7/8; do not cherry-pick.

**Scientific reading:** Neither fixed rule establishes new future XAU/USD directional information with available N. FOMC frequency ~8/year cannot alone support daily signal. Do not adjust event lookback, event exclusion list, target window or sign convention after negative result.

Reproduce: `GOLD_GPT6_P2_FOMC_EVENT_PRICE_ROWS.csv`, `GOLD_GPT6_P2_FOMC_NEXTDAY_SCORE.csv`, `GOLD_GPT6_P2_FOMC_RESULT.json`, `sql/gold_gpt6_p2_fomc_event_m15_source.sql`, `tools/gold_gpt6_p2_replay.py`; P1 independently archives 2020–25 future DAY targets. Both pre/post verified from individual M15 mid quote times. No Neon writes.
