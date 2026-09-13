# Gold Control V1.67 — Invariant Signal Screening Checkpoint

Date: 2026-09-13  
Branch: `gold-v167-invariant-signal-screening-research`  
Draft PR: #60  
Parent checkpoint: V1.66-R1  
Frozen contract commit: `ebacab1f2d4d7e2e486d758085b5c8a3804cb37c`  
Successful workflow run: `34755611401` — SUCCESS  
Artifact: `10317316530`  
Artifact digest: `sha256:aa25299ed4f2da4c561092c4195e259291249c92b9a8213918c9b5489a77cfa3`

Evidence class: `RETROSPECTIVE_METHOD_DEVELOPMENT_DIAGNOSTIC_NOT_FRESH_OOS`.

## Literature-guided question

After V1.66 showed that recalibration-only and forgetting-only do not solve 3D temporal weakness, V1.67 tests a more fundamental question: does the current information universe contain any chronologically stable predictive block at all?

The design was motivated by four upper-level research lines:

1. Invariant prediction / causal transfer: stable conditional predictive relationships across environments are candidates for better transport under distribution shift.
2. Maximin/stable-effects ideas: information that works across heterogeneous regimes is more defensible than information dominated by one regime.
3. Time-series OOD generalization: temporal environment construction matters and invariant learning can fail when environment labels are poor or important variables are unobserved.
4. Structural-break forecasting: hard break detection or aggressive adaptation is not automatically forecast-optimal; stable predictors should be established first.

No FOIL, IRM, anchor-regression tuning, detector, selector, CRASE, residual correction, abstention tuning, new feature search, or 2025/2026-based block selection was allowed.

## Frozen design

Five pre-existing 3D information blocks were tested with the same fixed L2 logistic family:

- `GOLD`
- `SESSION_RM`
- `PRICE_DISCOVERY`
- `MACRO_CROSS`
- `ROLE_CONTEXT`

Chronology was forward-only:

- initial training: 2023H1;
- E1 test: 2023H2;
- E2 test: 2024H1;
- E3 test: 2024Q3 through 2024-09-25.

Eligibility was determined only from E1/E2/E3. A block needed positive Brier skill in at least 2/3 environments, worst-environment Brier skill >= -0.03, median AUC >= 0.53, and minimum AUC >= 0.47. 2024Q4 was frozen as a bridge period and 2025/2026 were diagnostic only, but the bridge was never reached because no block passed formation eligibility.

## Result

`V1.67 = NO_ELIGIBLE_STABLE_BLOCK`.

No current block satisfied the frozen cross-environment stability gate.

### GOLD

- E1 2023H2: AUC `0.7440`, Brier skill `-11.68%`.
- E2 2024H1: AUC `0.4163`, Brier skill `-77.25%`.
- E3 2024Q3: AUC `0.5417`, Brier skill `-5.78%`.
- Positive Brier-skill environments: `0/3`.

The very strong E1 AUC does not transport into E2; probability quality is worse than the causal frequency benchmark in every formation environment.

### SESSION_RM

- E1: AUC `0.6498`, Brier skill `+6.20%`.
- E2: AUC `0.3780`, Brier skill `-13.70%`.
- E3: AUC `0.6364`, Brier skill `+1.42%`.
- Positive Brier-skill environments: `2/3`.

This block contains real local signal in E1 and E3, but the sign/quality collapse in E2 is too large to qualify as invariant.

### PRICE_DISCOVERY

- E1: AUC `0.5072`, Brier skill `-22.33%`.
- E2: AUC `0.4689`, Brier skill `-22.23%`.
- E3: AUC `0.6553`, Brier skill `+3.94%`.
- Positive Brier-skill environments: `1/3`.

Price-discovery information becomes useful only in the later formation environment and is not stable across earlier environments.

### MACRO_CROSS

- E1: AUC `0.6812`, Brier skill `+3.21%`.
- E2: AUC `0.4721`, Brier skill `-12.90%`.
- E3: AUC `0.6932`, Brier skill `+10.22%`.
- Positive Brier-skill environments: `2/3`.

This is the most interesting block but still fails invariance: E2 is materially weaker, and E3 collapses to one predicted direction despite high ranking AUC. It therefore cannot be promoted as a stable transported signal.

### ROLE_CONTEXT

- AUC is `0.50` in all three environments.
- Brier skill is slightly negative in all three.
- Predictions collapse to one class in every environment.

FAST/SLOW/monthly-direction context does not form a standalone invariant direction predictor, consistent with its role map.

## Interpretation

The current 3D failure is not well described by a single globally stable information block. Several blocks show **pockets of predictability** — especially MACRO_CROSS and SESSION_RM — but their usefulness is regime-dependent and can reverse or disappear across adjacent historical environments.

This result argues against jumping directly to FOIL/IRM/anchor regression on the same information set. Invariance methods require some transportable structure to exploit; the frozen screen does not establish such a block-level structure.

At the same time, the result does **not** imply that the data contain no predictive signal. It shows that the signal is not globally invariant under the current block representation. The two strongest blocks alternate between useful and weak environments, which makes **similar-regime / local-environment weighting** a better-supported next hypothesis than simple recency weighting or global invariance.

## Frozen decision

`NO_ELIGIBLE_STABLE_BLOCK__REJECT_CURRENT_INVARIANT_SIGNAL_HYPOTHESIS`.

Do not:

- loosen the V1.67 gate after seeing the result;
- build a deep invariant learner on these visible results;
- combine the two strongest blocks ad hoc;
- restart drift-detector tuning;
- use 2025/2026 to choose states or features.

The next justified research direction is a separately frozen **regime-similarity / local-environment forecasting study**. It should test whether a current state can be matched to historically similar pre-origin states more effectively than pure recency, using only causal state variables and matured historical outcomes. A strong benchmark must remain global/static and causal expanding frequency. If that also fails, the project should return to new-information or target/horizon redesign rather than further adaptation complexity.

No prospective, production, or action-mapping claim is made.
