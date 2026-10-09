# Causal pre-origin quote-pressure and GC-versus-spot gap experiments — 2026-10-09

**Status:** ACTUALLY EXECUTED via READ-ONLY Neon SQL on existing source; negative transport evidence. **NO PROMOTED MODEL.** 2025 retrospectively inspected. 2026 not evaluated in these two studies. No bank profits, live spreads, or guaranteed accuracy.

## Source and clock authority
- Gold source: **one** approved EVTradingLabs/Dukascopy-derived XAUUSD BID/ASK M15 table, 2020–2025 (141,890 source bars). Labels: **same-source** `gold_research_evduka_xau_session_target_candidate_v1`, 1,549 session rows.
- Turkey clock strictly fixed in Europe/Istanbul. Pre-17 issue uses only fully closed 15:30/16:00/16:30 local *bar starts* (end times 15:45/16:15/16:45). All pre-09 DAY features analogously use 07:30/08:00/08:30 starts (ends 07:45/08:15/08:45). No 16:45/08:45-start incomplete bars.
- Direction targets `overnight_y` and `day_y`, 1=UP, 0=DOWN. OVN: `overnight_gate='COMPLETE_SINGLE_SOURCE'` and `next_expected_date=issue_date+1`; Fridays-to-Mondays excluded. DAY: `day_gate='COMPLETE_SINGLE_SOURCE'`. Zero missing feature joins scored, never imputed. Actual bank execution not assumed.

## Experiment A: BSC-8 signed quote-pressure stress test — executed
**Predeclared simple concept for this trial:** 8-way categorical state from (a) mid-price last-hour sign, (b) contemporaneous BID/ASK spread expansion sign, (c) intrahour sign reversal between two half-hours. Forecast DOWN probability as `(historical_DOWN+2)/(historical_count+4)` within the eight exact categories; predict DOWN only if probability > 0.5. Model cells trained on 2020–2022 only, **held fixed** during 2023–2025. Comparisons are always-UP and last-hour-price continuation/reversal on identical eligible rows. Existing PRAMV/H3 not silently renamed. This diagnostic is not a new causal exogenous signal; it tests whether quote-side state carries robust signed information.

### Regular overnight 17→next09, 2020–22 frozen eight-cell lookup
| Year | N | BSC-8 Accuracy | BSC-8 BA | BSC-8 DOWN recall | Hourly price-trend BA | Hourly price-reversal BA |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | 198 | 59.60% | 58.74% | 51.72% | 46.78% | 53.22% |
| 2024 | 198 | 51.01% | 50.37% | 45.88% | 44.78% | 55.22% |
| 2025 (inspected) | 198 | 48.48% | 48.12% | 45.35% | 54.11% | 45.89% |

### DAY 09→17, separate analogous 2020–22 frozen eight-cell lookup
| Year | N | BSC-8 Accuracy | BSC-8 BA | BSC-8 DOWN recall | Hourly price-trend BA |
|---|---:|---:|---:|---:|---:|
| 2023 | 256 | 50.78% | 51.96% | 14.39% | 51.61% |
| 2024 | 259 | 54.44% | 49.13% | 9.82% | 44.32% |
| 2025 (inspected) | 258 | 53.88% | 49.06% | 12.50% | 52.05% |

**Decision:** rejects promotion. 2023 overnight apparent association does not transfer; DAY nearly collapses to mostly-UP. Spreads are liquidity/uncertainty indicators, not proof of signed alpha. No 2025 re-fit, threshold re-selection, or promoted 2026 "confirmation" permitted.

## Experiment B: independently sourced COMEX GC-to-spot return gap — executed
- Different feed: originally acquired Databento CME GLBX.MDP3 GC.c.0 1H native continuous contract; join on **exact 14:00 and 15:00 Europe/Istanbul hour-bar start**, both completed by 16:00, known conservatively before 16:45. Same `instrument_id` at both H1 starts; do not bridge futures roll.
- Same-hour local spot BID/ASK mid values at 15:00 and 16:00, as observed in closes of M15 bars starting 14:45 and 15:45. Both known before issue. All price-change calculations only within the pair.
- Signed `GC-minus-spot gap = ln(GC_16/GC_15) - ln(spot_16/spot_15)`. Predict DOWN if gap<0, otherwise UP. Fixed zero threshold, no fit; versus identical-date plain spot hourly trend and GC hourly trend. This is an exploratory market-leadership *proxy*, not causally identified price discovery; vendor/contract continuity limits apply.
- Strict same-instrument, both GC bar complete, both spot prices present: only N43/198 nights (2023), N45/198 (2024), N80/198 (2025); source missingness alone prevents broad inference.

| Year | Eligible N | Gap BA | Gap DOWN recall | Spot same-date BA | Gap rescues / breaks vs spot |
|---|---:|---:|---:|---:|---:|
| 2023 | 43 | 46.55% | 46.67% | 36.79% | 13 / 11 |
| 2024 | 45 | 60.92% | 64.71% | 38.45% | 17 / 7 |
| 2025 (inspected) | 80 | 52.08% | 56.25% | 54.17% | 22 / 25 |

**Decision:** 2024 improvement not sustained in 2025 even against matched simple spot. Coverage insufficient; **no paired significance claim** and no Brier/probability because threshold model is hard-label only. Do not select 2024 alone, tune 2025 threshold, splice GC continuous contracts, or score unavailable GC sessions as zero. Existing 2026 CME3 K25 negative test is distinct.

## Research conclusion / next falsification
Both a source-safe quote-side state and truly distinct GC-vs-spot synchronous rate comparison failed cross-year stability. The strongest surviving direction hypothesis must bring an *independent, before-issue, high-frequency signed information process* with auditable availability: source-qualified futures/orderflow or time-aligned FX/real-yield repricing, PLUS exact-time ex-ante event calendar. Announcement schedule alone is a **two-sided movement hazard**, not a signed probability. No post-17 CPI/FOMC surprise may be sent to a 17:00 model. A prospective locked holdout after these heavily inspected years is mandatory for promotion.

## Literature context (motivation only; no success inferred)
- Sobti, Sehgal & Ilango (2021), *International Review of Financial Analysis* 78:101893: time-of-day gold price discovery, news state dependence and asymmetric responses.
- Awartani, Hussain & Virk (2024), *International Review of Financial Analysis*, DOI 10.1016/j.irfa.2024.103486: five-minute FOMC price/volatility response asymmetry is **post-release**, not a pre-release signed predictor.
- Kurov, Sancetta, Strasser & Wolfe (2019), *Journal of Financial and Quantitative Analysis*: pre-release price drift across selected US futures; not direct proof for XAU/USD Turkey 17:00 execution clock.

**Data security:** Only group-level counts and metrics included here. No raw price rows, secrets, credentials, or user trade information exported from Neon. The read-only SQL statements were executed directly against the governed tables. Audit queries can be reconstructed from exact feature-clock/categorical specification above.
