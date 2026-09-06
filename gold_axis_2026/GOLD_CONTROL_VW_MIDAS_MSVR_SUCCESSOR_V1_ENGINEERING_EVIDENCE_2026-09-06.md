# GOLD CONTROL — VW_MIDAS_MSVR_SUCCESSOR_V1 ENGINEERING EVIDENCE

Date: 2026-09-06
Identity: `VW_MIDAS_MSVR_SUCCESSOR_V1`
Scope: research / historical replay only
Feature branch: `gold-control-vw-midas-msvr-successor-v1`
Frozen change-control commit: `ca08da189fedb326674190221fd0d12bbf936a10`
Runner implementation commit before workflow: `92ce35bd42422840e98606ede9493e162442901f`
Workflow head SHA: `56ebb97eb2e9852f17767bdc3b044f8dc8e9acb9`
Workflow run: `34020740010`
Workflow job: `101452741895`
Workflow conclusion: `SUCCESS`
Artifact id: `9985398790`
Artifact digest: `sha256:19576d8976443715cc2494708c01ec213118a585fa7c8f3c5874fa1164f8c6fd`
Deterministic model payload SHA-256: `6c422ebbb9b9d75306d9b6d60a336490744540ef084419a56ce28878b399424b`
Determinism rerun: `PASS`

## 1. Why this is a successor, not a repair

The archived `VW_MIDAS_MSVR` remains blocked as:

`BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN`

The missing archived runner was not guessed and was not silently repaired. The successor is a separately named, transparent four-metal implementation based on the retained weekend research mathematics and the now-governed research data plane.

## 2. Frozen model surface used

Four-metal daily research panel:
- Gold
- Silver
- Platinum
- Palladium

Common complete four-metal daily dates:
- first: `2010-01-04`
- last: `2026-07-31`
- common rows: `4229`

CORE5 Gold monthly target:
- rows: `390`
- first: `1994-02`
- last: `2026-07`

Official GPR PIT archive:
- governed origin vintages available: `54`
- missing required origins: `0`
- late required origins: `0`
- missing required one-month-lag GPR observations: `0`

The governed lane uses `GPR_OFFICIAL_GIT_PIT` from the origin-specific official Git vintage and uses the publication-lagged `p-1` GPR observation. The final CORE5 GPR series is used only in the separate legacy reconciliation lane and is not treated as historical PIT.

## 3. Model mathematics

The preregistered V1 feature vector contains exactly two features per metal:

- previous monthly log return;
- GPR-adaptive exponentially weighted within-origin-month daily log return.

This yields an 8-dimensional input vector for Gold/Silver/Platinum/Palladium.

The output is a joint four-dimensional next-month log-return vector fitted with a true multi-output RBF MSVR.

Frozen hyperparameter grid:
- `C ∈ {0.1, 1.0, 10.0}`
- `epsilon ∈ {0.02, 0.05}`
- `gamma_scale ∈ {0.5, 1.0}`
- `gamma = gamma_scale / 8`

Each outer target selects the configuration only from prior eligible rolling-origin forecasts. Scaling is fit inside each training fit. No random split or 2026 hindsight tuning is used.

## 4. Governed PIT-safe nested replay result

Evaluation window: `2023-01 .. 2026-07`
N: `43`

| Metric | Successor V1 | Random Walk |
|---|---:|---:|
| MAPE | `2.6910649759522176%` | `3.302322023320139%` |
| MAE | `87.7032462994936` | `107.46511627906976` |
| Median AE | `50.496279596392924` | `72.0` |
| RMSE | `137.4793424120283` | — |
| sMAPE | `2.711674901809337%` | — |
| Monthly win rate vs RW | `55.81395348837209%` | — |
| Direction accuracy | `60.46511627906976%` | — |
| Relative MAE vs RW | `0.8161089787661165` | `1.0` |
| Worst APE | `10.074151299353934%` | — |

### Completed-year breakdown

| Year | V1 MAE | RW MAE | Relative MAE | V1 MAPE | RW MAPE | V1 monthly win rate |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | `35.70225177496476` | `41.5` | `0.8602952234931266` | `1.8567202162346839%` | `2.1355631091053944%` | `41.67%` |
| 2024 | `57.499817764048565` | `64.83333333333333` | `0.8868866493169444` | `2.3938264916997802%` | `2.6995175800513223%` | `58.33%` |
| 2025 | `81.77223286161075` | `140.58333333333334` | `0.5816637785058263` | `2.347851468636661%` | `3.988666319811826%` | `75.00%` |

V1 beats Random Walk on MAE in all three completed calendar years used by the preregistered completed-year gate.

### 2026 partial-year diagnostic

2026-01..2026-07 is not hidden:
- V1 MAE: `238.79256601010508`
- RW MAE: `236.85714285714286`
- Relative MAE: `1.0081712678351844`
- V1 MAPE: `5.21928797815598%`
- RW MAPE: `5.159268985020495%`

Therefore the partial 2026 slice is slightly worse than RW. This does not get retuned away. The full 43-month aggregate remains better than RW and the preregistered completed-year gates remain satisfied.

## 5. Hyperparameter-selection behavior

Across the 43 governed outer targets the selected configurations were:
- `(C=1.0, epsilon=0.05, gamma_scale=0.5)`: 29 months
- `(C=1.0, epsilon=0.02, gamma_scale=1.0)`: 8 months
- `(C=0.1, epsilon=0.02, gamma_scale=1.0)`: 3 months
- `(C=1.0, epsilon=0.02, gamma_scale=0.5)`: 2 months
- `(C=1.0, epsilon=0.05, gamma_scale=1.0)`: 1 month

The dominant configuration is the same `(1.0, 0.05, 0.5)` structure retained in the weekend research evidence as the pre-2025 best configuration, but V1 does not hard-code it in the governed nested lane.

## 6. Weekend-model reconciliation

Retained weekend/audited reference:
- N = `43`
- VW MAPE = `2.672150%`
- VW median APE = `1.962940%`
- VW worst APE = `8.831236%`
- RW MAPE = `3.302322%`

The explicitly non-PIT legacy reconciliation lane, using the retained four-metal feature mathematics and fixed `(C=1.0, epsilon=0.05, gamma_scale=0.5)` configuration, produced:
- MAPE = `2.6632562048736115%`
- MAE = `86.61998963706779`
- median APE = `2.1632732199123406%`
- worst APE = `9.828688603746304%`
- Relative MAE vs RW = `0.8060289016217086`

MAPE distance from the retained 43-month weekend reference is only:

`-0.008893795126388326 percentage points`

The 2025 reconciliation MAPE is `2.3427985468624337%`, versus retained weekend 2025 MAPE `2.3859417402868672%`, distance `-0.04314319342443351 percentage points`.

Independent retained-artifact comparison across 2023-2025 also showed that the governed V1 monthly forecasts differ from the retained weekend VW forecasts by approximately:
- mean absolute forecast difference: `8.26 USD/oz`
- median absolute forecast difference: `5.15 USD/oz`
- maximum absolute forecast difference: `36.79 USD/oz`

This supports that the recovered four-metal/MSVR mathematics is materially aligned with the weekend model path, while the separately governed lane removes the known GPR availability problem and uses nested origin-safe tuning.

Exact archived-runner identity is still not claimed.

## 7. Preregistered gate result

All frozen gates passed:
- source/provenance/PIT: PASS
- deterministic rerun: PASS
- authority invariants unchanged: PASS
- Relative MAE vs RW < 1: PASS
- MAPE <= RW: PASS
- median AE <= RW: PASS
- completed-year win requirement: PASS (`3/3` completed years by MAE)
- no completed year MAE > 1.50 × RW: PASS
- unresolved leakage/availability exception: NONE under the frozen V1 contract

Terminal research status:

`RESEARCH_SHADOW_CANDIDATE_HISTORICAL_REPLAY_PASS_PROSPECTIVE_VALIDATION_REQUIRED`

This is a historical research/shadow eligibility result, not proof of prospective superiority and not runtime/production forecast authority.

## 8. Production safety verification

Independent production Neon verification after the run:
- `monthly_forecast_contracts = 0`
- `decision_signal_snapshots = 0`
- `decision_runs = 0`
- `decision_events = 0`
- current governed runtime = `ACTIVE 6 / WAITING 5 / BLOCKED 1`

The run performed no production database writes, no runtime activation, no selector or ensemble action, and no forecast/decision issuance.

## 9. Final engineering conclusion

`VW_MIDAS_MSVR_SUCCESSOR_V1` is now a reproducible, four-metal, PIT-aware historical-replay research challenger that passes the preregistered R1 historical gate.

The archived `VW_MIDAS_MSVR` remains blocked and unchanged.

The next permissible promotion step is a separately governed prospective/shadow validation contract. Historical replay alone must not be used to backdate or manufacture a production issuance.
