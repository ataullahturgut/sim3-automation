# Gold Control V1.50 — Role-Hierarchical Development Result

**Date:** 2026-09-12  
**Contract:** `GOLD_CONTROL_V150_ROLE_HIERARCHY_DEVELOPMENT_FREEZE_V1`  
**Evidence class:** `RETROSPECTIVE_DEVELOPMENT_ONLY_NOT_PROSPECTIVE_NOT_PROMOTION`  
**Workflow:** GitHub Actions run `34697188430`  
**Artifact id:** `10299600403`  
**Artifact digest:** `sha256:3745ee66f2db95aee731387e744b96d94df4f483db8bb83045d7230983f4bb5b`  
**Production authority:** `false`  
**AUTO_SELECTOR:** `OFF`  
**AUTO_ENSEMBLE:** `OFF`  
**Production writes:** `NONE`

## 1. Research integrity / outer lock

The V1.50 contract was frozen before this run. The already researcher-visible 2025-2026 V1.49 outer outcomes were not read by the V1.50 runner. General-direction and event-direction development were restricted to 2023-2024. The general lane used a pre-lock selection window ending 2024-06-30 and a one-pass development lock from 2024-07-01 through 2024-12-31.

The final artifact explicitly records `outer_2025_2026_read=false`.

## 2. Data geometry and the block-design correction

The development panel contained 213 exact governed NY17 origins from 2023-01-04 through 2024-12-30.

Diagnostic complete-case counts were:

| Information set | Complete rows |
|---|---:|
| G0 gold own history | 193 |
| G0 + G1 role context | 185 |
| G0 + G1 + G2 rates/FX PIT | 185 |
| G0 + G1 + G3 equities | 185 |
| G0 + G1 + G4 precious metals | 185 |
| G0 + G1 + G2 + G3 + G4 | 185 |

This confirms the earlier V1.49 zero/near-zero complete-case problem was materially affected by block packaging. In V1.50, late-starting volatility series no longer erase the longer equity history, and the ALFRED PIT rate/FX lane is separated from late-starting direct series. Train-only missing-data handling replaces full-block deletion.

G3 equity and G4 precious-metal histories remain labelled historical economic-date/research reconstructions; their current backfill retrieval clocks do not prove that the same observations were prospectively available at old NY17 origins. They therefore cannot create promotion authority from this retrospective development run.

## 3. General NEXT_NY17_1D result

The model/feature-set winner had to be selected using only the pre-lock window. The selected candidate was:

- feature set: `G0`
- model: `LOGIT_C01`
- pre-lock N = 84
- pre-lock Brier = 0.27615664
- pre-lock log loss = 0.74787869
- pre-lock accuracy = 42.86%

Frozen selective threshold selected on the pre-lock window was `|p-0.5| >= 0.00`, therefore no useful abstention threshold was supported.

Applied once to the 2024-H2 development lock:

| Metric | Selected model | P50 | Expanding frequency |
|---|---:|---:|---:|
| N | 68 | 68 | 68 |
| Brier | 0.25274367 | **0.25000000** | 0.25079273 |
| Log loss | 0.69869808 | **0.69314718** | 0.69473414 |
| Accuracy | 52.94% | 54.41% | 54.41% |
| Balanced accuracy | 53.36% | 50.00% | 50.00% |

Selective accepted N = 68, coverage = 100%, accuracy = 52.94%.

**Decision:** `NOT_ELIGIBLE_FOR_PROSPECTIVE_SHADOW` under the frozen V1.50 gate. The selected 1D candidate does not beat the unconditional P50 benchmark on Brier or log loss.

### Regime-instability diagnostic — not selectable after the lock

The best ex-post lock performer was `G0_G1_G4 + HGB_D2` with lock Brier 0.24664123, log loss 0.68743661 and accuracy 60.29% (N=68). However, the same candidate was poor in the frozen pre-lock selection window: Brier 0.30794907, log loss 0.82204778, accuracy 39.29% (N=84).

This is **not** a new winner. Selecting it after seeing the lock would violate the frozen protocol. The reversal is retained only as evidence of material regime/nonstationarity and as a motivation for a separately preregistered future adaptive-model hypothesis.

## 4. General NEXT_NY17_3D result

The pre-lock winner was again:

- feature set: `G0`
- model: `LOGIT_C01`
- pre-lock N = 82
- pre-lock Brier = 0.30275730
- pre-lock log loss = 0.80359521
- pre-lock accuracy = 37.80%

Frozen selective threshold was again zero.

Applied once to the development lock:

| Metric | Selected model | P50 | Expanding frequency |
|---|---:|---:|---:|
| N | 66 | 66 | 66 |
| Brier | 0.24482591 | 0.25000000 | **0.24325776** |
| Log loss | 0.68283100 | 0.69314718 | **0.67972592** |
| Accuracy | 57.58% | 60.61% | 60.61% |
| Balanced accuracy | 49.52% | 50.00% | 50.00% |

The model beats P50 probabilistically but does not beat the expanding-frequency benchmark and fails the frozen selective-accuracy gate.

**Decision:** `NOT_ELIGIBLE_FOR_PROSPECTIVE_SHADOW`.

### Regime-instability diagnostic — not selectable after the lock

The best ex-post lock performer was `G0_G1_G2_G3_G4 + LOGIT_C1`: Brier 0.22754407, log loss 0.64818906, accuracy 65.15%, balanced accuracy 61.83% (N=66). Yet its pre-lock performance was very poor: Brier 0.43782850, log loss 1.38409240, accuracy 42.68% (N=82).

Again, this is diagnostic evidence of instability, **not** authority to choose the model after observing the lock.

## 5. Macro Event specialist: strong positive development evidence

The event lane uses its own event-time clock and is not mixed with unconditional daily NY17 scoring. The gold-oriented Macro Event V3 score sign was evaluated only on pre-2025 events.

### All non-zero-score events

| Horizon | Hits / N | Hit rate | Exact one-sided Binomial p | Median signed log return |
|---|---:|---:|---:|---:|
| R5 | **43 / 57** | **75.44%** | **0.00007694** | +0.00254132 |
| R15 | **41 / 57** | **71.93%** | **0.00063178** | +0.00267095 |
| R30 | **42 / 56** | **75.00%** | **0.00011722** | +0.00279635 |
| Event -> next NY17 | 32 / 57 | 56.14% | 0.21352143 | +0.00246684 |

Exact 95% Clopper-Pearson intervals for directional hit rate are approximately:

- R5: 62.24% to 85.87%
- R15: 58.46% to 83.03%
- R30: 61.63% to 85.61%
- Event -> next NY17: 42.36% to 69.26%

The evidence is therefore concentrated in the **initial intraday reaction**, not in unconditional next-NY17 continuation.

### Existing frozen strong-state subgroup

No new threshold was selected from V1.50 outcomes. Using the already-existing `GOLD_ADVERSE_MACRO_SHOCK` / `GOLD_SUPPORTIVE_MACRO_SHOCK` states:

| Horizon | Hits / N | Hit rate | Exact one-sided p | Median signed log return |
|---|---:|---:|---:|---:|
| R5 | **8 / 9** | **88.89%** | 0.01953125 | +0.00413823 |
| R15 | **8 / 9** | **88.89%** | 0.01953125 | +0.00774695 |
| R30 | **8 / 8** | **100.00%** | 0.00390625 | +0.01034011 |
| Event -> next NY17 | 7 / 9 | 77.78% | 0.08984375 | +0.01350237 |

Important coverage note: strong-state R30 is 8/8 because one strong FOMC event lacks the required R30 bar. It must not be relabelled as 9/9 or full strong-state coverage.

### Family detail

- Employment: R5/R15/R30 = 17/23 = 73.91%; next NY17 = 12/23 = 52.17%.
- Inflation: R5 = 16/18 = 88.89%; R15/R30 = 14/18 = 77.78%; next NY17 = 9/18 = 50.00%.
- FOMC: R5/R15 = 10/16 = 62.50%; R30 = 11/15 = 73.33%; next NY17 = 11/16 = 68.75%.

### Year stability

- 2023: R5 20/28 = 71.43%; R15 18/28 = 64.29%; R30 19/27 = 70.37%.
- 2024: R5/R15/R30 = 23/29 = 79.31%.

The initial-reaction signal is therefore present in both development years rather than being created by a single 2024 episode.

## 6. Scientific conclusion

The first V1.50 run produces a deliberately asymmetric conclusion:

1. **Unconditional general 1D/3D direction remains NOT_PROVEN.** The frozen pre-lock winner does not clear the prospective-shadow gate. The ex-post lock leaderboard cannot be used to overturn that decision.
2. **Macro Event initial-reaction direction is the strongest positive V1.50 finding.** Pre-2025 all-event R5/R15/R30 direction is materially above 50%, statistically significant under the exact one-sided sign/binomial test, and the frozen strong-state subgroup is stronger still.
3. **The Macro Event result does not justify daily continuation authority.** All-event event-to-next-NY17 direction is only 56.14% with p=0.2135.
4. **Market Shock V3 should remain a confirmation/context layer**, not a standalone daily continuation vote. Existing 2026 joint evidence already showed strong initial sign confirmation but weak post-shock continuation.
5. **The large pre-lock -> lock reversals in the general candidate rankings are evidence for time variation/regime dependence**, consistent with the thesis motivation for dynamic/role-conditioned modelling. They are not permission for hindsight model selection.

## 7. Governed next step

The defensible next step is to freeze a prospective event-direction shadow before future events mature, with the 15-minute reaction retained as the primary endpoint for continuity with the earlier preregistered Macro Event V2 validation. R5 and R30 remain secondary endpoints; event-to-next-NY17 remains a separate continuation endpoint. Market Shock confirmation must be timestamped after the shock is observable and cannot be back-propagated to a pre-release or release-time origin.

General 1D/3D should remain research-only until a separately preregistered adaptive/regime hypothesis is evaluated on genuinely unseen future outcomes. No 2025-2026 retrospective rescue selection is permitted.
