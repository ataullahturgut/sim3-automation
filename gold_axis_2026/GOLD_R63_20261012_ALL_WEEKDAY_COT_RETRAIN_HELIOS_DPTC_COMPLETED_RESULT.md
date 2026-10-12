# R61–R63 — All-weekday release-adjusted COT: OPAL retrain, dynamic HELIOS V1–V5, SAGE/RuleFlow and DPTC-Q95

**2026-10-12 | RESEARCH CHALLENGER, NOT LIVE AUTHORIZED | Target clock unchanged.**

## User objective — no further circular clock-only verification

Run the **models**, using real report-eligible COT dates on *all* forecast weekdays, keeping the existing H3 D0 → third retained source-date D3 target. Model success is an evaluation statistic, not the rationale for source-date correction. Frozen original operational history remains intact; outputs are separately versioned.

### Actual calculations performed in the current connected GitHub analysis environment

**R61 OPAL:** read 1,029 H3 source rows, CFTC 14-feature raw positioning state, R60 all-weekday release selection, and frozen 931 OPAL baseline. For each of **47 months (2022 Nov–2026 Sep)**, fit StandardScaler + class-balanced L2 logistic C=1, using only matured H3 labels available by the first issue cutoff, with 18 frozen features (14 COT + three momentum interactions + trend strength). Refitted separately on original 7-day-buffer inputs and release-first inputs. **Genuinely recomputed** all **931 probability scores**, not a row-substitution of a frozen model. Numerical algorithm: independent JavaScript Newton/IRLS rather than scikit-learn's LBFGS, with L2 Hessian and no-intercept regularization. Original frozen baseline probability max difference **0.003551**, original OPAL threshold/override **931/931 exact**, original direction **931/931 exact**. Exact sklearn code lives at `tools/gold_r64_all_weekdays_exact_sklearn_opal_to_dptc_replay.py` but was **not run** within this GitHub connector runtime.

**R62 HELIOS V1–V5:** Independently replayed all 931 full endogenous dated rows with candidate corroboration, H3 matured feedback gate (last 8, enter 5, exit 3), V2 competence probability, V3 five-policy game-theoretic weighted history, V4 nonconsensus regret expansion, V5 DCE. Original V5 old probabilities reproduced **931/931** to max abs difference **5.55e-17**; original policy flip shares max deviation **2.22e-16**. New all-weekday OPAL trained route history and every maturity queue replayed from scratch. No frozen gate transplant.

**R63 SAGE→RuleFlow→Handoff→DPTC:** Recombined new HELIOS with **frozen external SAGE IFBC/LLRS and RuleFlow topology features**, recomputing V5-dependent candidate eligibility on each of the **191** 2026 origins. Independently rebuilt Handoff premax/internal rank mechanism on 1,029 daily source rows (including missing-lag semantics), and recomputed all 191 alarm gates, SELLR eligibility using *frozen numeric score and original 2025-selected threshold*, label-free phase allowance, pending maturities, TRUST hysteresis. Gate checked against original frozen combined baseline **126/191**, Handoff **28/28**, Q95 actions **13/13** and **191/191 frozen final directional votes**, original **135/191**.

## Verified historical result (2025/2026 outcomes retrospective)

| Stage and window | Frozen legacy COT | All-weekday release-adjusted COT challenger |
|---|---:|---:|
| OPAL 2023 | 147/219 | 152/219 |
| OPAL 2024 | 168/240 | 171/240 |
| OPAL 2025 | 161/248 | 161/248 |
| OPAL 2026 Jan–Sep | 121/191 | **122/191** |
| OPAL May 2026 | 12/21 | **16/21** |
| HELIOS V5 2023 | 156/219 | 156/219 |
| HELIOS V5 2024 | 171/240 | 171/240 |
| HELIOS V5 2025 | 165/248 | **159/248** |
| HELIOS V5 2026 Jan–Sep | 121/191 | **120/191** |
| HELIOS V5 May 2026 | 12/21 | 14/21 |
| Combined V5+SAGE/RuleFlow 2026 | 126/191 | **125/191** |
| Eligible Handoff 2026 | 28 | **22** |
| DPTC-Q95 Handoff interventions | 13 (11 rescue, 2 broken) | **9 (7 rescue, 2 broken)** |
| **DPTC-Q95 final 2026** | **135/191 (70.68%)** | **130/191 (68.06%)** |
| **DPTC-Q95 May 2026** | **17/21** | **17/21** |

### 2026 issue-month DPTC scores

| Forecast issue month | N | Frozen Q95 correct | Revised-weekday-source Q95 correct |
|---|---:|---:|---:|
| January | 21 | 16 | 16 |
| February | 20 | 13 | 13 |
| March | 22 | 17 | 16 |
| April | 22 | 15 | 13 |
| May | 21 | 17 | 17 |
| June | 22 | 14 | 15 |
| July | 23 | 13 | 13 |
| August | 21 | 16 | 15 |
| September | 19 | 14 | 12 |
| **Total** | **191** | **135** | **130** |

The release-adjusted R63 130/191 is **not** equal to R59 129/191; corrected historical COT vintage and retrained OPAL alter HELIOS on five 2025/2026 dates versus R56. In 2026, notably **July 6**, previously assumed July 3 release was actually **July 6 at 15:30 New York**, *after* the assumed 15:00 Türkiye issue time. Corrected COT positioning selection at that issue is June 23 (not June 30), with R61 OPAL P(reversal) ~**0.5481** versus R56 ~**0.7066**. A different OPAL call can propagate through model state to downstream outcomes, so do not manually adjust only that row's final vote.

May 2026 remains 17/21 despite OPAL 16/21 and HELIOS 14/21: **do not add gains across different nested model layers**. May 19 and 22 are rightly reversed by new HELIOS, but corresponding old Handoff Q95 flips are now ineligible and must not be double-applied. The **new** 2026 acted source cutoff dates are Apr30, May27, Jun01, Jun08, Jun29, Jul14, Jul17, Sep03 and Sep24; note source cutoff is **not** the following issue date.

## What is / is not certified

**Certified computation:** all-weekday 1,029 row calendar ledger and documented release fixes from R60, exact old HELIOS 931-row parity, exact old DPTC 191-row parity, all-new OPAL monthly fits and HELIOS/DPTC dynamic replay under the stated numerical and frozen external-input contract.

**NOT certified:** bit-exact scikit-learn LBFGS for new OPAL (the saved R64 script is executable but not run here); full independently retrained IFBC, LLRS, RuleFlow, SELLR numerical scorer or upstream AURORA/RIFT/VEGA; complete provider historical firstprint/PIT availability of metals/macro data; as-issued historical 15TR order signals. These are not grounds for reopening the same calendar test; they define the limits of the experiment and any future *genuinely forward* validation. Some 2022–2025 nonroutine publication firstprints remain unconfirmed; R60 handles documented exceptions but does not invent missing firstprints.

This is **development and retrospective stress evidence**, not prospective 2026 strategy performance. Preserve the conservative intentionally lagged original COT model; do not promote or discard based on a May-only win or total accuracy difference. The clock-consistent successor has now been meaningfully **trained and replayed**, so the source-date reconciliation phase is considered closed absent new external primary evidence.

## Saved and reproducible artifacts

1. `GOLD_R61_20261012_COT_ALL_WEEKDAY_RELEASE_ADJUSTED_OPAL_931_ROLLING_RETRAIN.csv` — 931 monthly origin-matured old versus new OPAL scores, COT selected reports, threshold votes; `GOLD_R61_20261012_COT_ALL_WEEKDAY_RELEASE_ADJUSTED_OPAL_SUMMARY.json`.
2. `GOLD_R62_20261012_H3_ALL_WEEKDAY_COT_DYNAMIC_HELIOS_931_REPLAY.csv` — chronological 931-row V1–V5 decisions, gate and phase states, old exact parity; `GOLD_R62_20261012_H3_ALL_WEEKDAY_COT_DYNAMIC_HELIOS_SUMMARY.json`.
3. `GOLD_R63_20261012_H3_ALL_WEEKDAY_RELEASE_OPAL_HELIOS_DPTC_DYNAMIC_191.csv` — all 191 origin/issue/target dates, old/new SAGE/RuleFlow flags, Handoff qualification, mode and final outcomes; `GOLD_R63_20261012_H3_ALL_WEEKDAY_RELEASE_OPAL_HELIOS_DPTC_SUMMARY.json`.
4. `tools/gold_r64_all_weekdays_exact_sklearn_opal_to_dptc_replay.py`: **authored but not executed** end-to-end Python/scikit-learn rerun with old parity gates, to resolve numerical exactness when run on a clone; outputs are new R64 paths, never frozen originals.

**Decision:** R63 **130/191** is the current actual, qualified all-weekday release-adjusted *controlled dynamic* DPTC result. R59 129/191 is preserved as a distinct, previously holiday-incomplete experiment; do not silently rewrite it. Next legitimate work should be new forecast development or genuinely prospective evaluation, not repeated identical historical time-label audits.
