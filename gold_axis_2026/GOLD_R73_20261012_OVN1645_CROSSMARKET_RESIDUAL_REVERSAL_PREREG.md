# R73 PREREGISTRATION — OVN 16:45 → next calendar day 09:00 TR: cross-market (ZN/NQ/CL) residual reversal

**Written and committed BEFORE any overnight target outcome of this panel was queried or viewed.**
Author: Claude Code research session, 2026-10-12. Base commit of work branch: `58cc4d52` (R72).

## 1. Duplication check against prior work (manifest `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`)

| Prior work | What it did | Same as R73? |
|---|---|---|
| CME3 K25 (2026-10-09) | NQ/ZN/CL 1h returns as K-NN analogue features, 17:00→next 09 OVN | No: no gold-on-factor regression, no residual, different clock (17:00) |
| R28–R29 | NQ/ZN/CL 01–04 UTC innovations as logistic inputs for H3 (3-day) | No: different horizon/target |
| R30 | NQ/ZN/CL stress flags, label-free audit | No: not scored |
| GC–spot gap (2026-10-09) | COMEX GC H1 vs spot price-discovery gap, 17→09 | No: GC-vs-spot, not cross-asset factors |
| ZN-VPT2 | ZN signed price × volume anomaly × spot disagreement, nested logistic | Related (ZN family) but not a residual of gold on factors |
| PRAMV / RFR | XAU-only 16:00–16:30 vs 16:30–17:00 half-hour reversal, macro veto, 17:00 clock | No: XAU-only; the 16:00–17:00 TR half-hours are AFTER the R73 feature cutoff |
| R11B gold-minus-crossmetals divergence | metal-relative divergence | No: different factor set |
| R67 | H3 prior + prior_overnight + prior_day + pre_close_day logistic, 16:45→next 09 OVN | Same target clock; raw gold day move is one of its inputs; no cross-market residual |
| PRAMV V2B | *proposed* GC/COMEX/spot residuals | Proposal only, never run, different factors |

Conclusion: the exact hypothesis "gold-specific residual after ZN/NQ/CL factor removal reverses in the 16:45→09 night" has **not** been run. The raw-gold-reversal component overlaps with R67/RFR-type information, so the **incremental** test vs raw reversal (H2) is the genuinely new part.

## 2. Clocks (Europe/Istanbul = UTC+3 all year since 2016)

- Decision: 16:45 TR = 13:45 UTC, decision days Mon–Thu only (Friday→Monday excluded; Sat/Sun never).
- Feature cutoff: **13:00 UTC (16:00 TR)**. No bar ending after 13:00 UTC is used. CME `ts_event` verified to be the bar START (2024 GC vs EV/Dukascopy XAU: corr 0.649 with [ts,ts+1h), 0.065 with [ts−1h,ts)). Hence the CME bar starting 12:00 UTC (ends 13:00 UTC) is the last allowed; the bar starting 13:00 UTC (ends 16:00 TR+1h = 17:00 TR) is forbidden.
- **Primary window W7:** 06:00→13:00 UTC (09:00→16:00 TR). **Secondary window W3 (late part):** 10:00→13:00 UTC (13:00→16:00 TR). Exactly two windows, fixed now; Holm correction across the two for H1. No other windows will be scored.
- CME price "as of T": close of the latest bar with `ts_event+1h <= T` and `ts_event >= T-3h`. Window start and end bars must have the **same `instrument_id`** (roll days dropped). Any root missing → day dropped.
- XAU price "as of T" for features: mid = (bid_close+ask_close)/2 of the M15 bar starting T−15min.
- **Target:** `ovn = ln(mid_exit / mid_entry)`, entry mid = (bid_open+ask_open)/2 of M15 bar starting 13:45 UTC (16:45:00 TR); exit = same for bar starting 06:00 UTC of the next calendar day (09:00 TR). Label y = 1 if ovn>0, 0 if ovn<0, ovn==0 dropped. 13:00–13:45 UTC is used neither as feature nor target → no leakage of the 16:45 entry price into features.
- Sources kept separate and labelled per row: 2023–2025 `gold_research_evduka_xau15m_bidask_candidate` (EV Trading Labs ex-Dukascopy); 2026 `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` (direct Dukascopy). No cross-source pooling of metrics; per-year metrics only, 2026 always reported separately.
- CME data begin 2023-01-02, so no feature exists before 2023; nothing is produced for 2020–2022.

## 3. Model (fixed, no tuning)

For each decision date t: ridge regression of gold window log-return g on standardized [zn, nq, cl] window log-returns, with intercept, penalty alpha = 10 (sum-of-squares scale), fitted on the **most recent 250 prior weekdays (< t) with complete window data** (Fridays included as training rows — they need no target), minimum 60 rows, else no prediction. The fit never uses any overnight outcome. Residual e_t = g_t − (a + x_t·b).

Rules on the same rows:
- **R_RESID:** predict UP iff e_t < 0 (sign(−residual)). — hypothesis rule
- R_REV: predict UP iff g_t < 0 (raw reversal)
- R_MOM: predict UP iff g_t > 0 (raw momentum)
- ALWAYS_UP, ALWAYS_DOWN
- R67 `new_pred` (16:45→09 HistData logistic, trained 2023–24 → in-sample on DEV, flattered) and R67 `h3bit`, on date-matched rows only.

## 4. Evaluation (fixed)

DEV = 2023–2024 pooled (and per year). 2025 and 2026 = **retrospective, already-inspected transport only**; never called untouched tests.

- **H1 (primary):** W7 R_RESID DEV accuracy > 50%, exact one-sided binomial p < 0.05 after Holm across {W7, W3}, AND DEV balanced accuracy > 50%.
- **H2 (incremental, the new claim):** W7 R_RESID vs R_REV on identical DEV rows, exact one-sided McNemar (R_RESID-correct/R_REV-wrong vs reverse) p < 0.05.
- **H3 (continuous):** DEV OLS `ovn ~ 1 + fitted + e` with HC3 SE; requires coef(e) < 0 with one-sided p < 0.05.

Verdict: **CONTINUE** if H1, H2, H3 pass. **RAW-REVERSAL-ONLY** if H1 and H3 pass but H2 fails. **REJECT** if H1 fails. Anything else = **INCONCLUSIVE / MORE DATA**. 2025/2026 cannot rescue a failed DEV gate.

Reported per year: N, coverage vs eligible nights, accuracy, BA, UP/DOWN recall, matched comparisons, rescues/breaks, Wilson 95% CI, month-block bootstrap (2,000×, seed 20261012) CI for DEV BA difference R_RESID − R_REV, Spearman(e, ovn), and gross mid-to-mid signed return plus Dukascopy ask/bid-crossed return (NOT bank spread).

No new thresholds, windows, factor sets or models will be searched if the fixed hypothesis fails.
