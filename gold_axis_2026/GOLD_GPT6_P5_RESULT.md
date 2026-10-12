# GPT-6 P5 — completed COMEX GC hour vs future XAU/USD overnight return
**Decision: REJECT as an hourly OHLCV lead-lag model, NOT a test of real order flow.** Fixed plan `9eb683fd`. Actual available Databento GC.c.0 continuous 1h: source has only 1,829 hourly 2023 / 1,879 hourly 2024 / 2,782 hourly 2025 futures bars — less than 24h/day, and data coverage is selective. Query only uses a **fully completed hour** before16:30TR issue, max 2h stale, compared with **four spot M15 bars ending16:15TR** (15-minute safety lag), future strictly complete EV/Dukascopy XAU MID OVN16:45→next09.

Source coverage before strict joined eligible night: GC+past spot both 2023 96, 2024 117, 2025 155. Actual complete and matched future OVN target: 2023 **93**, 2024 **112**, 2025 **150** = 355. Not representative of all sessions; hour source receipt not live-proven. Training only 2023 and prior mature 2024 (ridge alpha10); 2025 coefficients frozen to 2023/24, 2025 already inspected.

| Outcome | 2024 N112 | 2025 N150 |
|---|---:|---:|
| GC previous completed hour direction accuracy | **43.75%** | **50.00%** |
| Spot prior completed hour sign accuracy | 51.79% | 52.00% |
| GC sign BA | 47.26% | 51.65% |
| RW zero-return future OVN RMSE(logret) | .00599987 | .00893479 |
| Spot-only regularized ridge RMSE | **.00588320** | **.00880190** |
| Spot+GC ridge RMSE | .00588502 | .00887397 |
| Spot-only next mid USD/oz MAE | **10.418** | **23.237** |
| Spot+GC next mid USD/oz MAE | 10.507 | 23.486 |

Adding currently stored GC OHLCV to a spot-prior model makes future-return and price estimates *worse* in both development 2024 and opened 2025. Future profit unstudied; no promotion. Underlying 2023 GC sign accuracy 41/93=44.09%, BA46.34%.

This result does **not** prove there is no microstructure informational edge at 15min/different hour or true GC trades/MBP: those data do not exist currently in Neon; do not pay Databento for trades without user's explicit authorization. Overlap selection bias, different futures/spot vendors and GC contract roll limit inference.

Source: `sql/gold_gpt6_p5_gc_completed_hour_spot_15m.sql`, `GOLD_GPT6_P5_SOURCE_ROWS.csv`, `GOLD_GPT6_P5_MATCHED_FULL_SOURCE.csv`; results `GOLD_GPT6_P5_DECISION_SCORES.csv`, `GOLD_GPT6_P5_RESULT.json`; deterministic verification `tools/gold_gpt6_p5_replay.py`. Database untouched.

### Post-audit interpretation correction (P6 known-price target)
The reported spot-only and GC+spot `price_mae` reconstitute an exit price **using observed 16:45 future OVN origin entry**; the issue decision is 16:30, so those two price-MAE numbers are retrospective **conditional level errors, not executable/issue-as-of numerical price forecasts**. Core GC-vs-spot **forward-return** RMSE and directional signals remain valid label comparisons. The independent P6 true 16:15 known-price anchor vs future OVN exit supplies the correct fixed issue-time spot price forecast test.
