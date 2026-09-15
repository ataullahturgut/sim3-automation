# GOLD CONTROL — 2025 VOLATILITY CHALLENGE CONTRACT V1

**Status:** FROZEN RESEARCH CHALLENGE CONTRACT  
**Date:** 2026-09-15  
**Scope:** 2025 daily abnormal-move event universe for role-preserving evaluation of the 12 governed Gold Control identities.

---

## 1. Purpose

This contract defines a **separate 2025 volatility-challenge event universe** for answering one question:

> On materially abnormal XAU/USD daily moves in 2025, which governed Gold Control engines supplied useful early, same-event, confirmation, risk, or contextual evidence under their native roles?

This contract does **not** replace the frozen GC-BREAK structural break label contract. The two event universes serve different purposes:

- GC-BREAK event labels: structural trend-break/regime-transition research.
- 2025 volatility challenge: abnormal daily move detection and engine-coverage diagnostics.

No engine may define or alter the volatility-event list.

---

## 2. Authority basis

The event definition follows the established financial-econometrics principle that abnormal moves should be judged relative to prevailing volatility rather than by a universal fixed percentage threshold. Relevant authority includes:

- Andersen, Bollerslev, Diebold & Labys (2003), *Modeling and Forecasting Realized Volatility*, Econometrica 71(2), 579-625, DOI 10.1111/1468-0262.00418.
- Barndorff-Nielsen & Shephard (2004/2006), realized variation / bipower variation and jump-testing literature.
- Lee & Mykland (2008), *Jumps in Financial Markets: A New Nonparametric Test and Jump Dynamics*, Review of Financial Studies 21(6), 2535-2563, DOI 10.1093/rfs/hhm056.
- Sobti (2025), *What triggers intraday price jumps and co-jumps in gold?*, International Review of Financial Analysis 105, 104380, DOI 10.1016/j.irfa.2025.104380.

This contract is a deliberately simple daily standardized-return challenge, **not** a claim to implement a full Lee-Mykland or bipower-variation intraday jump test.

A universal raw `%2` price-change rule is therefore **not** the primary event definition.

---

## 3. Source and coverage

Research source identity:

`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`

Source metadata:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- research frequency: `daily_derived_from_1h`;
- transform: `SELECT_16_00_AMERICA_NEW_YORK_HOURLY_CLOSE`;
- database quality status: `APPROVED_HISTORICAL_RESEARCH_RETRIEVAL_NOT_CANONICAL_NY17`;
- 2025 weekday research observations: **255**.

This series is used only as the 2025 volatility-challenge research ground truth. It does **not** replace the canonical runtime `XAU_EOD_TWELVE_NY17` contract.

### Exact-NY17 coverage finding

The exact Twelve Data 1-minute `16:59:00 America/New_York` historical probe contains many dates on which the provider itself returns `PROVIDER_NO_BAR`. Those dates may not be fabricated, interpolated, forward-filled, or silently replaced in the canonical NY17 series.

### Same-provider equivalence validation

On dates where both the hourly-derived close and the exact 16:59 close have the **same previous close date**, 2025 comparison produced:

- comparable daily returns: **168**;
- return correlation: **1.000000**;
- mean absolute return difference: **0.000000 percentage points**;
- sign agreement: **168 / 168**.

Therefore the hourly-derived series is accepted for this **research-only 2025 volatility challenge** because it materially improves coverage while retaining same-provider return equivalence on directly comparable observations. It remains explicitly noncanonical for runtime NY17 use.

---

## 4. Frozen event rule

For each governed research date `t`:

`r_t = 100 * ln(P_t / P_{t-1})`

where `P_t` is the research daily close above.

Prior volatility is:

`sigma20_t = sample standard deviation of r over the 20 immediately preceding governed research observations`

The current return is excluded from its own scale estimate.

Standardized move:

`z_t = r_t / sigma20_t`

Frozen tiers:

- **MAJOR_VOLATILITY_EVENT:** `|z_t| >= 2.0`
- **EXTREME_VOLATILITY_EVENT:** `|z_t| >= 3.0`

`EXTREME` is a subset of `MAJOR`.

The `2.0 sigma` threshold is a project challenge threshold chosen before the 12-engine replay to retain meaningful abnormal moves for coverage analysis. It is **not** represented as a universal literature constant. The `3.0 sigma` tier is the stricter severity class.

Raw simple percentage return is descriptive only and may not replace the standardized event rule after engine results are observed.

Consecutive qualifying dates remain separate directional event-days in the primary evaluation. Episode consolidation may be reported only as a secondary diagnostic and may not alter primary counts after scoring.

---

## 5. Frozen 2025 event inventory

| # | Date | Simple return | z-score | Direction | Tier |
|---:|---|---:|---:|---|---|
| 1 | 2025-02-10 | +1.6463% | +2.3407 | UP | MAJOR |
| 2 | 2025-02-14 | -1.5677% | -2.2468 | DOWN | MAJOR |
| 3 | 2025-02-18 | +1.8303% | +2.1885 | UP | MAJOR |
| 4 | 2025-03-13 | +1.8927% | +2.1237 | UP | MAJOR |
| 5 | 2025-04-04 | -2.4392% | -3.3930 | DOWN | EXTREME |
| 6 | 2025-04-09 | +3.3871% | +3.2185 | UP | EXTREME |
| 7 | 2025-04-10 | +2.9940% | +2.3440 | UP | MAJOR |
| 8 | 2025-07-21 | +1.4764% | +2.0611 | UP | MAJOR |
| 9 | 2025-08-01 | +1.8937% | +2.5481 | UP | MAJOR |
| 10 | 2025-09-02 | +1.7065% | +2.6673 | UP | MAJOR |
| 11 | 2025-09-22 | +1.9380% | +2.6254 | UP | MAJOR |
| 12 | 2025-09-29 | +1.8743% | +2.3040 | UP | MAJOR |
| 13 | 2025-10-06 | +2.2264% | +2.7911 | UP | MAJOR |
| 14 | 2025-10-13 | +2.4814% | +2.5043 | UP | MAJOR |
| 15 | 2025-10-16 | +3.0777% | +2.9074 | UP | MAJOR |
| 16 | 2025-10-17 | -2.2873% | -2.0589 | DOWN | MAJOR |
| 17 | 2025-10-21 | -5.4288% | -4.1054 | DOWN | EXTREME |
| 18 | 2025-12-22 | +2.4221% | +4.0174 | UP | EXTREME |
| 19 | 2025-12-29 | -4.4229% | -6.6415 | DOWN | EXTREME |

Frozen totals:

- major-or-extreme event-days: **19**;
- extreme `|z| >= 3` event-days: **5**;
- UP event-days: **14**;
- DOWN event-days: **5**.

---

## 6. Engine evaluation rule

The same 19 event-days must be presented to all 12 governed identities, but engines must be judged by their **native role**, not by a flat direction-accuracy metric.

Permitted event-level statuses include:

- `EARLY_HIT`
- `SAME_EVENT_HIT`
- `CONFIRM`
- `WRONG_DIRECTION`
- `MISS`
- `NO_SIGNAL`
- `NOT_APPLICABLE`
- `BLOCKED`
- `NOT_TESTABLE`

Examples of role preservation:

- FAST: tactical weakening / direction evidence and lead time.
- SLOW: completed-week confirmation / new-regime evidence and delay.
- Monthly Direction / monthly H=1 experts: strategic prior/context, not daily triggers.
- Macro Event: eligible scheduled-event context only; non-event dates are not automatic misses.
- BOCPD: regime/change context, not a direction vote.
- Emergency Level/Reversal: abnormal displacement/reversal context.
- GVZ_RISK: risk/severity/uncertainty context, not equal direction voting.

For each motor, report coverage, event-level status, relevant direction correctness where applicable, lead/lag, abstention/NO_SIGNAL, and missing/PIT limitations.

---

## 7. Anti-hindsight lock

This event inventory is frozen **before** the new 12-engine 2025 volatility replay.

After any engine result is inspected, the following are forbidden for the same challenge identity:

- changing `2.0` or `3.0` sigma thresholds to improve an engine;
- changing the trailing-20 scale window to improve an engine;
- deleting inconvenient event-days;
- consolidating or splitting episodes to improve reported performance;
- changing source/provider to improve performance;
- treating an inapplicable event-clock engine as a miss solely because no eligible event existed.

If a later event definition is scientifically desired, it requires a separately named successor contract and may not overwrite this V1 challenge.

---

## 8. Evidentiary interpretation

This 2025 volatility challenge is `HISTORICAL_REPLAY / RETROSPECTIVE_DIAGNOSTIC` evidence.

It may answer whether the existing engines appear complementary enough to justify subsequent model research. It may **not** be used to tune a model on 2025 and then claim the same 2025 period as untouched out-of-sample validation.

If a combined model is pursued after inspecting these results, learning/tuning must return to the permitted formation window or a newly governed development design, and later validation claims must reflect the information actually used.
