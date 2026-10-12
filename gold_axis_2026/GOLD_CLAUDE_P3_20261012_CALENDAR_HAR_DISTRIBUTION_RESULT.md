# CLAUDE P3 — Macro-calendar HAR-RV and return/price distribution: RESULT

**DAY: SUPPORTED_RV_ONLY (volatility only, with a 2025/26 caveat). OVN: REJECT.**
No direction or mean-return skill is claimed.

Prereg `GOLD_CLAUDE_P3_20261012_CALENDAR_HAR_DISTRIBUTION_PREREG.md` (commit `f4cb7a6b`, pushed before
any P3 forecast). Code `tools/gold_claude_p3_20261012_calendar_har_distribution.py`; outputs
`GOLD_CLAUDE_P3_20261012_{SUMMARY.json,SCORE_ROWS.csv}`. Inputs: H3A session RV rows 2020–25 (PR #91,
unchanged copies), 2026 DAY RV (`data_claude_p3/`, same H3A rule, separate source), macro calendar
(`data_claude_p3/GOLD_CLAUDE_P3_MACRO_CALENDAR.csv`: NFP 83, CPI 82, scheduled FOMC 55 timestamps from
Neon), returns from the P1 panels.

## Construction check
HAR-X reproduces H3A's HAR exactly in DEV (max |Δ log forecast| = 1.4e-14 over 515 DAY and 1.6e-14
over 395 OVN windows), so the only differences are the event dummy and the continued expanding
re-estimation in 2025/26.

## Primary (event increment, pooled DEV 2023–24, DM one-sided, Holm over 2)
| Target | N | mean QLIKE gain HAR-X → HAR-XE | t | p | Holm p |
|---|---|---|---|---|---|
| DAY (E = NFP or CPI day) | 515 | +0.0452 | 3.10 | 0.00096 | **0.0019** |
| OVN (E = scheduled FOMC night) | 395 | +0.0428 | 2.33 | 0.0100 | **0.0100** |

## Per-year QLIKE (lower is better) and gate
| Target, year | N (event windows) | HAR-XE | HAR-X | PERSIST5 | CLIM60 | H3A locked (matched) | event gain [95% block CI] |
|---|---|---|---|---|---|---|---|
| DAY 2023 | 256 (23) | **0.2014** | 0.2387 | 0.2793 | 0.2866 | 0.2387 | +0.037 [+0.009, +0.060] |
| DAY 2024 | 259 (24) | **0.2149** | 0.2681 | 0.3171 | 0.3015 | 0.2681 | +0.053 [+0.017, +0.106] |
| DAY 2025 (opened) | 258 (21) | 0.2741 | 0.2836 | **0.2680** | 0.4880 | 0.2895 | +0.010 [−0.008, +0.058] |
| DAY 2026 (opened, other source) | 177 (15) | 0.4132 | 0.4292 | **0.3669** | 0.6771 | — | +0.016 [−0.028, +0.077] |
| OVN 2023 | 198 (8) | **0.1679** | 0.1978 | 0.2171 | 0.2569 | 0.1978 | +0.030 [+0.008, +0.034] |
| OVN 2024 | 197 (8) | **0.1695** | 0.2252 | 0.2420 | 0.2983 | 0.2252 | +0.056 [+0.018, +0.097] |
| OVN 2025 (opened) | 198 (8) | 0.2380 | 0.2352 | **0.2060** | 0.6284 | 0.2491 | **−0.003** [−0.015, +0.007] |
| OVN 2026 | BLOCKED (direct source has no 75-minute break) | | | | | | |

| Gate | DAY | OVN |
|---|---|---|
| Holm p < 0.05 | pass (0.0019) | pass (0.0100) |
| HAR-XE < PERSIST5 and CLIM60 in 2023 and 2024 | pass | pass |
| 2025 event increment not reversed | pass (+0.010) | **fail (−0.003)** |
| **Verdict** | **SUPPORTED_RV_ONLY** | **REJECT** |

What the DAY result means, precisely:
- On NFP/CPI days the next-window realized variance is much higher than a price-only HAR expects.
  The QLIKE gain on event windows alone is 0.44 (2023), 0.65 (2024), 0.30 (2025), 0.44 (2026).
  Adding the pre-announced release-day dummy reduces DAY QLIKE by 15.6% (2023) and 19.8% (2024)
  against H3A's HAR.
- **Caveat that is not hidden by the gate.** In opened 2025 and 2026 the whole HAR family, HAR-XE
  included, still loses to PERSIST5 (2025: 0.2741 vs 0.2680; 2026: 0.4132 vs 0.3669). The
  calendar increment stays positive, but the PR #91 problem remains: a slowly adapting HAR level
  in a volatility-regime shift. Continued expanding refits help a little versus H3A's locked
  coefficients (2025 DAY 0.2836 vs 0.2895) but do not fix it.
- OVN: the FOMC-night effect was strong in DEV (event windows gain 0.81 and 1.50 QLIKE) but vanished
  in 2025 (0.18 on 8 event nights; increment over all nights −0.003). REJECT as preregistered.

## Secondary: return and price distribution (μ = expanding mean; σ² = k·RV forecast)
Gaussian CRPS (bp, lower better), 90% interval coverage and mean width:

| Target, year | N | HAR-XE | HAR-X | PERSIST5 | UNCOND | HAR-XE gain vs PERSIST5 (p) | vs UNCOND (p) |
|---|---|---|---|---|---|---|---|
| DAY 2023 | 256 | **25.56**; 89.8%; 150 bp / $29.2 | 25.65 | 25.71; 88.7% | 26.86; 94.5%; 210 bp / $40.7 | +0.15 (0.048) | +1.30 (<0.001) |
| DAY 2024 | 259 | **28.93**; 90.3%; 157 bp / $37.7 | 29.04 | 29.07; 88.8% | 29.53; 94.6%; 200 bp / $47.6 | +0.14 (0.086) | +0.60 (0.001) |
| DAY 2025 | 258 | 35.68; 86.0%; 180 bp / $62.6 | 35.57 | 35.59; 87.2% | 35.93; 88.4% | −0.09 (0.69) | +0.26 (0.12) |
| DAY 2026 | 177 | **49.27**; 84.7%; 243 bp / $109.7 | 49.29 | 49.47; 85.9% | 49.91; 78.0% | +0.20 (0.23) | +0.64 (0.06) |
| OVN 2023 | 198 | **31.82**; 89.9%; 176 bp / $34.1 | 32.14 | 32.28; 86.4% | 32.80; 93.4% | +0.46 (0.002) | +0.98 (<0.001) |
| OVN 2024 | 197 | **34.17**; 88.8%; 194 bp / $46.5 | 34.27 | 34.37; 88.3% | 34.85; 91.9% | +0.20 (0.12) | +0.68 (0.003) |
| OVN 2025 | 198 | 46.76; 85.9%; 238 bp / $83.6 | 46.63 | **46.30**; 88.4% | 47.80; 84.3% | −0.46 (0.98) | +1.05 (0.002) |

Volatility-scaled intervals are sharper than unconditional ones at near-nominal DEV coverage (DAY
90%-interval width 150–157 bp vs 200–210 bp). This is a **range/uncertainty** improvement for the
future price, not a better point forecast: the mean is the same INT forecast for every row, so
return MSE and price-level point error are identical to P1's INT baseline. In 2025 every
conditional interval under-covers (86–88%) because of the volatility-level shift.

## Answer to the program question
The pre-announced US release calendar is information that is **not** in past prices and is known
at 08:45. It measurably improves the forecast of **how much** XAU/USD will move in the 09:00–16:45
window (realized variance and interval width), robustly in sign across 2023–2026. It does **not**
improve the forecast of **where** the price goes (direction or point return). The FOMC-night
volatility effect in the OVN window did not persist into 2025.

## Limits
Calendar dates are the realized release dates. The Neon CPI series lacks the 2025-12-18 release
(the shutdown year), which affects only opened 2025. Window eligibility (H3A completeness) is
known only after the window, a shared limitation of all H3A-based work. Historical vendor data,
not live receipt. No profitability claim.
