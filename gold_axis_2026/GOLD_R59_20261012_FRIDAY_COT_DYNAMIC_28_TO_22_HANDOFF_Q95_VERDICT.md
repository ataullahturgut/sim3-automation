# R59 — Friday COT: independent H3 alarm rederivation and chronological DPTC-Q95 replay

**2026-10-12. Status: NONBINDING CONTROLLED COUNTERFACTUAL / source-clock research.**
**Objective: validate Friday release-time availability, not optimize historical accuracy.**
Parent: R58; do not overwrite old-COT/+7-day frozen authority or historical baseline.
Data contract: original H3 **D0 source UTC-day mean → third retained source-day D3 UTC-day mean**, not +72h or Turkish-bank-hours returns.

## 1. Resolved alarm-count discrepancy and exact old-system parity

The previous JavaScript audit incorrectly used -Infinity for a missing prior internal observation, falsely producing nonfinite/infinite positive `internal_d1`. Four spurious alarm rows (source cutoff **2026-02-17, 03-11, 04-24, 07-06**) did **not** satisfy the canonical original Python gate. These are an audit implementation bug, **not** additional true Handoff alarms or a COT timestamp error.

Correctly preserve missingness through `max(skipna=True)`, matching canonical `tools/gold_h3_remaining53_signal_audit.py` and `tools/gold_h3_handoff_competence_bocpd_v1.py`.

Independent 1029-date score reconstruction (280 IFBC rows; 332 LLRS rows; 1029 daily cross-market backbone; 679 TRES rows), with 120-prior-row percentiles and source-cutoff-aligned one-/two-date lag:
- Old 2026 Handoff alarms: **28/28 exact membership parity**, **zero extra or missing** versus canonical BOCPD timeline.
- Old DPTC-Q95 intervention dates: **13/13 exact membership parity** versus frozen Q95 actions, **zero extra or missing**.
- Old DPTC-Q95 **191/191 final direction predictions exact** against R57 `originalQ95` (not only total score); baseline **126/191** → old Q95 final **135/191**.
- Corrected mature-target-clock processing uses actual R57 H3 target dates, not the older blank target dates from a known action-export pandas NaT bug.

This exact old parity is the certification gate for the subsequent **conditional** Friday-COT replay.

## 2. NEW Handoff alarm eligibility and chronological DPTC replay

From R56 931-row Friday OPAL→dynamic HELIOS V1–V5 challenger, R57 191-row new combined HELIOS+fixed SAGE/RuleFlow baseline, the complete full-universe Handoff score gate was re-evaluated:
1. `leadlag_score_premax >= 0.60`;
2. `internal_now >= 0.60`;
3. `internal_d1 >= 0`, *missing lags ineligible*;
4. **new Friday-COT SAGE/RuleFlow combined baseline** still follows prevailing momentum.

All 191 2026 forecast issue rows were inspected, **not just** the old 28 alarm dates. New alarms **22**, with no new-only dates and six old alarms removed (feature-cutoff dates): **2026-03-16, 03-23, 04-07, 04-10, 05-18, 05-21**. The other 22 alarm dates are unchanged.

The DPTC-Q95 trust machine was then **replayed in increasing feature-cutoff order** on the new 22 alarms: unchanged exogenous label-free DEPENDENCE_PHASE, existing frozen SELLR numeric signal and 2025-selected threshold 2.3677413378977423, **new** baseline-follows-momentum SELLR firing eligibility, **new** correct/broken counterfactual Handoff outcomes, pending feedback matured against true H3 target dates, and two-consecutive-matured-acted-BROKEN trust exit.

- Old 13 acted origins, **11 RESCUE / 2 BROKEN**; old TRUST begins May21 cutoff.
- New **9 acted origins**, **7 RESCUE / 2 BROKEN**. The removed May21 source-cutoff SELLR-triggered Handoff means **new TRUST never enters**; these 9 interventions are PHASE gated.
- New acted *source-cutoff* dates: **Apr30, May27, Jun01, Jun08, Jun29, Jul14, Jul17, Sep03, Sep24**. Their actual forecast issue dates are the following eligible source days; do not label the cutoff date as the issue date.

### 2026 January–September score accounting (191 issues)

| Statistic | Original frozen DPTC-Q95 | Friday-COT conditional dynamic Handoff/Q95 |
|---|---:|---:|
| Old/new recombined SAGE+RuleFlow baseline | **126/191** | **124/191** |
| Eligible alarms | **28** | **22** |
| DPTC actions | **13** | **9** |
| Action rescues / broken | **11 / 2** | **7 / 2** |
| Final correct H3 directions | **135/191 (70.68%)** | **129/191 (67.54%)** |
| May 2026, 21 forecasts | **17/21** | **17/21** |

The May result **17/21** is important: unlike R58's **15/21** under fixed old action dates/old 28-alarm cohort, the correctly regenerated new alarm gate **removes the two already-correct May19 and May22 issue-day reversals**, avoiding a double flip of Friday HELIOS's correctly revised direction. May's equal final score does **not** mean unchanged decisions or prospective proof.

| Forecast issue month | Issues | Old Q95 correct | New conditional Q95 correct |
|---|---:|---:|---:|
| 2026-01 | 21 | 16 | 16 |
| 2026-02 | 20 | 13 | 13 |
| 2026-03 | 22 | 17 | 16 |
| 2026-04 | 22 | 15 | 13 |
| 2026-05 | 21 | 17 | 17 |
| 2026-06 | 22 | 14 | 15 |
| 2026-07 | 23 | 13 | 12 |
| 2026-08 | 21 | 16 | 15 |
| 2026-09 | 19 | 14 | 12 |
| **Total** | **191** | **135** | **129** |

## 3. Source-time contract and method limitations

- COT positions are **Tuesday as-of**; ordinary release is **Friday 15:30 America/New_York**; 2026 May = **Friday 22:30 Europe/Istanbul**. At assumed issue time **15:00 Istanbul Friday**, same-Friday COT is unavailable. A Friday release generally first qualifies for a Monday issue, respecting **21 recorded CFTC delayed-report exceptions**; Monday U.S. holidays and report lateness are based on actual release timestamps, not guesswork.
- Old `+7 calendar day` policy is a conservative **deliberate freshness rule**. It is not a false conversion of Friday release or a corrupted target clock. Friday-first is an alternate research *policy*, not a repair that proves greater predictability.
- The OPAL rolling logistic Friday-COT probability stream in R56 was computed using independently coded **approximate IRLS**; original sklearn probabilities differed by up to **0.003095**. Exact sklearn refit script `tools/gold_h3_opal_friday_cot_asof_v2.py` **is present but was not executed**. R59 inherits this numeric qualification.
- Frozen external SAGE IFBC/LLRS, RuleFlow macro/topology and TRES streams are **not refitted**. Existing source-derived DEPENDENCE_PHASE and precomputed numeric SELLR score are reused, with **recomputed** trigger eligibility. Full upstream model refitting / SELLR score recalibration and BOCPD standalone competence diagnostics remain open; the **DPTC-Q95 controller** here is genuinely re-simulated on the **new** alarm cohort.
- May historical commodity source firstprint/PIT vintage and full model-issue 15:00 Istanbul availability are **not certified** by matching COT release timestamps alone; R45–R48 remain binding. Q95 was developed retrospectively in October 2026: none of these 2026 scores are genuinely independently prospective performance.
- Therefore the result is **not** a fully refitted successor or a production replacement; success/failure is a test statistic, **not** the goal of correct Friday-time attribution.

## 4. Evidence and reproduction

- Row ledger: `GOLD_R59_20261012_FRIDAY_COT_DYNAMIC_ALARM_DPTC_Q95_191_REPLAY.csv` — all 191 rows with old/new issue date, source cutoff, H3 end date, COT positioning report date, HELIOS, SAGE/RuleFlow baseline, new alarm/phase/trust/action and final outcome.
- Machine summary: `GOLD_R59_20261012_FRIDAY_COT_DYNAMIC_ALARM_DPTC_Q95_SUMMARY.json`.
- Reproduction code: `tools/gold_r59_friday_cot_dynamic_alarm_dptc_q95_replay.py`. This Python rerun has **not** been executed in the connected GitHub-only runtime; the stored R59 row ledger and count/row parity arose from an **independent JavaScript replay of the retrieved repository source CSVs**. Python code includes asserts for 28-alarm parity, 13 action parity, R56 V5 row parity, exact 191/191 original predictions and scores 135→129. Do not assert the Python executable itself was run.

**Decision:** retain original model authority; recognize correct Friday COT dates as historical source metadata, not a performance improvement premise. R59 **supersedes only** R58's claim that no regenerated new alarm candidate result is yet available. R58's fixed-action 129 and original-cohort 127 remain correctly described as different, less dynamic tests.
