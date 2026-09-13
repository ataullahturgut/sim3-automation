# Gold Control V1.68 — Regime Similarity / Local Historical Training Checkpoint

Date: 2026-09-13  
Branch: `gold-v168-regime-similarity-local-research`  
Draft PR: #61  
Parent: V1.67 invariant-signal screening  
Frozen contract commit: `9e4a29fd53fb98d5c5248a7d9efa0e7a6012954a`  
Successful workflow run: `34755825901` — SUCCESS  
Artifact: `10317336916`  
Artifact digest: `sha256:a14589214454b057cc575264ac9371d2d54a9fcfb188a1624134c0ddfa421925`

Evidence class: `RETROSPECTIVE_METHOD_DEVELOPMENT_DIAGNOSTIC_NOT_FRESH_OOS`.

## Frozen question

Can a model trained on historically similar causal market states recover more stable 3-day predictive skill than the same model trained on all matured history or the equally-sized most-recent history window?

This was the literature-guided follow-up to V1.67. V1.67 found no globally invariant block, while `SESSION_RM` and `MACRO_CROSS` showed pockets of pre-2025 predictability. V1.68 therefore tested local state similarity rather than more generic forgetting or a selector.

## Frozen design

- Predictor blocks: `SESSION_RM`, `MACRO_CROSS` only, selected from V1.67 pre-2025 evidence.
- Same fixed L2 logistic model for all comparisons.
- `GLOBAL`: all target-matured history.
- `RECENT_K`: K most recent target-matured observations.
- `SIMILAR_K`: K nearest target-matured historical observations under a frozen seven-variable state vector.
- State variables: `gold_mom20`, `gold_rv20`, `rm_vol`, `broad_usd_logdiff5`, `real10_delta5`, `fast_state_encoded`, `slow_state_encoded`.
- State imputation and standardization used matured history only at each origin.
- K grid: 40, 60, 80; one K shared by both blocks and chosen only from causal 2023H2 / 2024H1 / 2024Q3 predictions.
- 2024Q4 was the frozen bridge. 2025/available-2026 were retrospective diagnostics only.
- No state-vector changes, kernel tuning, block combination, CRASE/selector, detector, residual correction, abstention tuning, external data fetch, or production action.

## Pre-2025 K selection

All local variants were worse than the causal-frequency benchmark over the frozen K-selection sample, but K=80 was the best of the predeclared similarity choices and was therefore selected exactly as specified.

- K=40: SIMILAR Brier `0.29489`; RECENT `0.29567`; GLOBAL `0.25910`; frequency `0.24793`.
- K=60: SIMILAR `0.27954`; RECENT `0.28064`.
- K=80: SIMILAR `0.27315`; RECENT `0.27731`.

Chosen K: `80`.

## 2024Q4 bridge — decisive result

Neither block passed the frozen bridge gate.

### SESSION_RM

- Frequency Brier: `0.26616`.
- GLOBAL: Brier `0.24812`, AUC `0.66154`, BA `0.6000`.
- RECENT_K: Brier `0.28721`, AUC `0.53846`, BA `0.46154`.
- SIMILAR_K: Brier `0.29685`, AUC `0.48205`, BA `0.6000`.

For SESSION_RM, the global model was clearly superior. Similar-state training made probability quality worse and lost ranking skill.

### MACRO_CROSS

- Frequency Brier: `0.26616`.
- GLOBAL: Brier `0.37861`, AUC `0.37949`, one predicted direction.
- RECENT_K: Brier `0.45371`, AUC `0.30769`.
- SIMILAR_K: Brier `0.34981`, AUC `0.56410`, BA `0.56667`, MCC `0.25820`.

For MACRO_CROSS, state similarity did recover directional discrimination relative to GLOBAL and RECENT_K, but the probabilities remained far worse than the simple causal-frequency benchmark. Therefore this is not sufficient forecast skill.

## Researcher-visible diagnostics

### 2025

MACRO_CROSS:
- GLOBAL AUC `0.54242`, Brier `0.24327`.
- RECENT_K AUC `0.63789`, Brier `0.24924`.
- SIMILAR_K AUC `0.54926`, Brier `0.25605`.
- Frequency Brier `0.23783`.

SESSION_RM:
- GLOBAL AUC `0.39495`, Brier `0.25594`.
- RECENT_K AUC `0.43316`, Brier `0.27827`.
- SIMILAR_K AUC `0.32421`, Brier `0.30884`.

### available-2026

MACRO_CROSS:
- GLOBAL AUC `0.48222`, Brier `0.26581`.
- RECENT_K AUC `0.57704`, Brier `0.30819`.
- SIMILAR_K AUC `0.52089`, Brier `0.29801`.
- Frequency Brier `0.25111`.

SESSION_RM:
- GLOBAL AUC `0.52400`, Brier `0.25514`.
- RECENT_K AUC `0.56756`, Brier `0.26216`.
- SIMILAR_K AUC `0.54415`, Brier `0.27323`.

Neither block passes retrospective persistence either.

## Interpretation

`V1.68 = BRIDGE_FAIL__REJECT_REGIME_SIMILARITY_ESCALATION_FOR_CURRENT_INFORMATION_SET`.

The experiment does not support the idea that the current seven-variable state geometry reliably identifies historical observations that should receive more influence than either all history or recent history. Similarity occasionally improves discrimination, particularly MACRO_CROSS in 2024Q4, but does not produce calibrated/proper-score skill against the causal frequency benchmark.

This is important because V1.66 already showed that recalibration-only and forgetting-only are insufficient, V1.67 found no globally invariant information block, and V1.68 now rejects this particular local-regime representation. More adaptation complexity on the same binary target and information set is not justified.

## Frozen decision

Do not tune K, state variables, or a distance kernel after seeing these results. Do not combine SESSION_RM and MACRO_CROSS ad hoc. Do not restart CRASE or a drift detector.

The next research step must return to the more fundamental questions of **forecastability and target/information representation**: whether the declared information set contains usable predictive information at 1D/3D, whether binary UP/DOWN labeling is discarding useful magnitude information, and whether a continuous/distributional target should be studied before any further adaptive machinery.

No prospective, production, or action-mapping claim is made.
