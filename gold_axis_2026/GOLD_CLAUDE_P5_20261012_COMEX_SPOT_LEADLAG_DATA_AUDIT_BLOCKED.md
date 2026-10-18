# CLAUDE P5 — COMEX→spot lead-lag persistence to the decision horizon: DATA AUDIT — **BLOCKED (zero-cost data)**

Date: 2026-10-12. Protocol PR #93, stage P5: "Start with zero-cost price/quote timestamps; stop if
lead-lag effect vanishes before intended horizon. Order-flow paid data only after explicit user
permission, with cost quote." No model was fitted and no future spot return was examined for P5.

## Prior work (not relabelled)
2026-10-09 (manifest line 332): "Preissue correctly aligned separate COMEX GC H1/spot price-discovery
gap OVN 2023/24/25 matched N43/45/80, BA46.55/60.92/52.08 … 2025 gap rescued22, broke25 (net −3);
**NO TRANSPORT**. GC same-contract 2-hour coverage low and selective". CAVS (manifest line 4490)
requires a GC coverage audit before training. P5 would differ only in measuring the **decay ladder**
(15 min → 1 h → full window) and using log-return error targets. Both need dense GC bars.

## Zero-cost data available (read-only Neon, 2026-10-12)
`gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c`, Databento GLBX ohlcv-1h, `ts_event` =
bar start:

| Symbol | 2023 | 2024 | 2025 | 2026 (to 10-07) |
|---|---|---|---|---|
| CL.c.0 (reference, near-continuous) | 5,838 | 5,863 | 5,828 | 4,493 |
| NQ.c.0 | 5,865 | 5,892 | 5,852 | 4,525 |
| **GC.c.0** | **1,829** | **1,879** | **2,782** | **1,445** |
| SI.c.0 | 1,039 | 1,159 | 1,482 | 1,264 |

GC hourly bars on weekdays 2023–24, by UTC hour (≈520 weekdays):
- 04:00 UTC (the last complete hour before the 08:45 TR DAY decision): **97 bars (≈19%)**.
- 12:00 UTC (the last complete hour before the 16:30 TR OVN decision): **227 bars (≈44%)**.
- Peak 13:00–14:00 UTC: about 295 bars (≈57%).

`GC.c.0` is the **calendar** front contract (13 instruments per year). It is frequently a thin
delivery month, and an ohlcv bar exists only when a trade prints. Missingness therefore depends on
activity (selective), which is the same defect the 2026-10-09 study recorded. A lead-lag ladder
estimated on 19–44% of days selected by trading activity would not be a valid decision-time
estimate. Spot M15 is complete, but the futures leg is not.

## Verdict
**P5 BLOCKED** with zero-cost data. No synthetic fill (no forward-filled GC, no spot-substituted
futures price).

## What would unblock it (requires explicit user approval; nothing purchased)
1. **Volume-ranked continuous GC** (`GC.v.0` or `GC.n.0`) from Databento GLBX.MDP3, `ohlcv-1m` or
   `ohlcv-1h`, 2020–2026. These are the same schemas already used in the repository. A previous cost probe
   showed about $0.40–1.39 per request; a fresh `metadata.get_cost` quote is needed before any pull.
   This enables the 15-minute/1-hour/window decay ladder at the two decision clocks.
2. Signed order flow (`trades`/`tbbo`) only after (1) shows a lead surviving to ≥1 hour. The
   literature (Cont et al. 2014/2023) predicts decay within minutes, so the prior is low.
