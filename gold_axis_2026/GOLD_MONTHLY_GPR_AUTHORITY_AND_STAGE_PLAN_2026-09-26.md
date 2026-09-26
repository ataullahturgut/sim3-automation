# GOLD MONTHLY — N2 GPR authority, implementation contract and staged checklist

Status: AUTHORIZED / FROZEN BEFORE PRODUCTION RESULTS. Date: 2026-09-26.
User authorization: complete the same Stage 0–5 architecture as RBFNN, including the broad optimizer screen and six mandatory refinements; progress sequentially without repeated permission requests. This supersedes a compact-only N2 interpretation. It does not authorize other families or changes to the data contract.

## 1. Verified primary authority and what is transferred

| Source | Verified method | Project mapping and limits |
|---|---|---|
| Rasmussen & Williams (2006), GPML [chapter 2](https://gaussianprocess.org/gpml/chapters/RW2.pdf) | Gaussian regression posterior mean/covariance and log marginal likelihood | Exact analytic posterior solves; observations include noise; uncertainty is reported, not assumed calibrated |
| GPML [chapter 4](https://gaussianprocess.org/gpml/chapters/RW4.pdf) | Covariance functions, ARD squared exponential and Matérn | Eight origin-safe standardized features; RBF and Matérn-3/2 baseline comparison, Matérn-5/2 reserved |
| GPML [chapter 5](https://gaussianprocess.org/gpml/chapters/RW5.pdf) | Hyperparameter learning using marginal likelihood; priors | Negative log marginal likelihood for training; explicit Gaussian prior on transformed parameters for MAP variant; chronological validation chooses repeat |
| Bonilla, Chai & Williams (2007), [Multi-task Gaussian Process Prediction](https://proceedings.neurips.cc/paper/2007/file/66368270ffd51418ec58bd793f2d9b1b-Paper.pdf) | Shared input kernel, learned PSD task covariance, task-specific observation noise | Covariance B ⊗ K + D ⊗ I over four returns. B=L Lᵀ, positive Cholesky diagonal. No redundant kernel amplitude: B carries signal amplitude. Independent-output fitting is not mislabeled as joint learning. Noiseless complete-design cancellation means transfer cannot simply be assumed |
| Álvarez, Rosasco & Lawrence (2012), [Kernels for Vector-Valued Functions](https://arxiv.org/abs/1106.6251) | ICM and LMC vector-valued kernels | ICM is the canonical main family; multi-component LMC is a genuinely distinct Stage-3C candidate, to be specified before its results |

Sources support the GP mechanisms, not a claim that any optimizer will beat existing gold forecasts. The 32 optimizer equations remain the repository's parity implementations, with source hashes; independent paper-level equivalence of every optimizer is NOT_PROVEN.

## 2. Binding unchanged data and evaluation contract

H=1 next calendar-month average XAU/USD; origin previous completed month-end. Same frozen 8 VW-MIDAS features and governed database loader. Four metal log returns jointly learned in main family. Explicit roadmap-required single-output Gold benchmark is auxiliary, never silently promoted as four-output evidence.

DEV 2022-04..2024-12 n=33 exclusively selects models, parents, structures, pools and alpha. 2025 n=12 transport and 2026 Jan–Jul n=7 stress are retrospective reporting only. Database READ_ONLY; random split forbidden; target/future labels never enter fitting. Every origin uses chronological past; final 20% (minimum 6) is inner validation, minimum 30 inner-training rows. Scaling uses inner training only. Theta and scaler remain fixed when the exact posterior conditions on all pre-target observations.

Before external reporting, DEV decision/hash is saved. External theta, kernel and scaler are learned using data through 2024-12 only and then frozen. Past external observations may condition the posterior at subsequent origins, but cannot tune hyperparameters, select optimizer/parent/pool or recalibrate intervals.

Primary metrics: DEV ΣAE and correct monthly direction. Supporting: MAE, MAPE/WAPE, RMSE, median/worst AE/APE, RW-relative MAE, monthly RW wins, years, leave-one-origin and numerical stability. Uncertainty: uncalibrated predictive-observation 95% interval coverage/width and Gold log-return NLPD, diagnostics only. Price point forecast = previous actual × exp(predicted return mean), the lognormal median, consistent with absolute-price-loss focus. No external calibration.

## 3. Exact main-family implementation

- Kernel has unit diagonal: RBF k=exp(-0.5 Σ_d((x_d-z_d)/ell_d)^2), or stated Matérn variant.
- B=L Lᵀ is a 4×4 task covariance; L lower triangular. Four task noise standard deviations are learned separately. No output coefficients are meta-optimized.
- 22 nonlinear parameters: 8 log length scales; 4 log Cholesky diagonals; 6 free lower-triangle entries; 4 log noise standard deviations.
- Natural-scale bounds: ell [.05,20]; L diagonal [.1,3]; L off-diagonal [-2,2]; noise SD [.01,2]. Bounds are implementation choices frozen before outcomes, not paper-prescribed constants.
- Fixed jitter 1e-8 added to observation covariance, distinct from learned noise. No escalating jitter rescue based on outcomes.
- Exact task-noise whitening and 4×4 eigendecomposition reduce inference to four N×N Cholesky solves. This is not a sparse approximation. Dense Kronecker mean, observation variance and NLL oracle tests must pass for RBF/M32/M52.
- Training fitness = [joint Gaussian NLL + .5×lambda×Σ(theta-prior_center)^2]/(N×outputs). Prior center: log ell=0, log L diagonal=0, off-diagonal=0, log noise SD=log(.3). Lambda 0 for ML baselines; lambda 1 for regularized baseline and common Stage-1 MAP objective. Priors defined in transformed coordinates.
- Validation objective = .7 Gold standardized MAE + .3 all-four-output standardized MAE; single-output benchmark uses Gold only. Validation chooses repeat/candidate, never target month.
- Baseline optimizer: bounded L-BFGS-B, 3 deterministic starts, maxiter60/maxfun1600, ftol1e-7. Termination success/message/nfev logged. Finite budget-limited candidates are allowed and marked; no claim of a global or converged optimum.
- Stage-1 optimization: population24, generations45, repeats3; target-hash deterministic seeds. Same inner split, fixed MAP prior, RBF ICM and parameter bounds for all 32. Training NLL drives evolution, chronological validation selects from final candidates/repeats. Actual fitness calls logged; equal generations do not mean equal calls.
- Main scientific gates: finite means/variances; all four predicted absolute log returns <1; positive task covariance and observation noise; Cholesky success; observation variance >0; latent variance negative beyond 1e-7 rejected; covariance condition certified upper bound <=1e12. No RBF cluster/width gate is mechanically copied to GP. Boundaries and termination are diagnostics, not hidden rescue knobs.
- A failed month makes the whole period scientifically incomplete; no subset ranking. Implementation failures block dependent stages; scientific failure is retained without outcome-driven retuning.

## 4. Ordered architecture — same as RBFNN

### Stage 0 — canonical baselines and technical gate

1. SO_RBF: roadmap-required Gold-only ARD-RBF ML benchmark, explicitly auxiliary.
2. VANILLA_ICM_RBF: four-output ICM ARD-RBF ML canonical anchor.
3. ICM_M32: same four-output ML fit with Matérn-3/2; kernel comparison benchmark.
4. REGULARIZED_ICM_RBF: same ICM-RBF with explicit lambda1 parameter prior (MAP), not a claim that plain GP has no regularization.

Dense oracle, cross-output transfer/independent-limit, optimizer-interface and target/future-label invariance tests precede production. Audit all four baseline artifacts before Stage 1. Baseline failures do not silently redefine Stage-1 structure.

### Stage 1 — broad single-optimizer parity screen

| Batch | Methods |
|---|---|
| 1.1 | PSO, GA, DE |
| 1.2 | MPA, ABC, SSA, GWO |
| 1.3 | WOA, HHO, ACO, BAT |
| 1.4 | FA, MFO, FPA, FA_FPA |
| 1.5 | CS (Cuckoo), SCA, SALP, SMA |
| 1.6 | GOA, ALO, TLBO, JAYA |
| 1.7 | HGS, CHOA, HGSO, AOA |
| 1.8 | CPA, KRILL, CROW (Crow Search, not CS) |
| 1.9 | DE_ABC, MULTISWARM |

Sequential batches; <=4 independent jobs. No parent selection until all32 complete or explicitly scientifically rejected. Method identity, source hash, bounds, seeds, objective calls, convergence, DEV, reporting-only external results and decisions recorded each batch.

### Stage 2 — DEV filtering / parent freeze

Only scientifically complete four-output methods eligible. Audit all required metrics plus likelihood/uncertainty and numerical/validation dispersion. Full independent predictive-repeat robustness is NOT_PROVEN unless actually measured.

Roles: lowest ΣAE price leader; maximum direction then lowest ΣAE direction leader; minimum worst-year RW-relative MAE stability; Vanilla ICM architecture anchor; retained MPA conditional hybrid parent. Retain valid RW-beating models and required anchor; exact duplicates and correlation>.995 dominated models labeled redundant. Compute signed/absolute-error correlations, direction agreement, bidirectional rescue/loss counts and monthly price wins. Commit a small role-based parent set before Stage3.

### Stage 3A — six mandatory refinements

Adaptive PSO; Adaptive/Improved TLBO; TLBO-tuned PSO; DE-tuned PSO; Adaptive CROW; PSO-TLBO. Repository mechanisms transferred through the 22-parameter GP objective; outer parameter bounds/source/learned values recorded. Batch <=2. Final population24/generations45/repeats3. No pre-freeze refinement can be binding evidence.

### Stage 3B — conditional hybrids

At most one MPA+SCA/GA/CPA opens if both retained, signed-error correlation<.90, each direction rescue>=2 and each monthly price wins>=8. Select minimum correlation, then combined DEV ΣAE tie-break. No eligible pair => CLOSED_NOT_OPENED, not a missing experiment. Pool immutable after Stage3 outcomes.

### Stage 3C — genuinely GP-specific literature method(s)

Research/specify 1–3 candidates after Stage3AB closure. Preferred distinct class: two-component LMC with different kernels and explicit coregionalization matrices. Other candidates require verified sources, explicit parameters/data needs/compute gates and a genuine distinction from Stage3A/B. Definitions freeze before candidate outcomes. Unsupported mechanics => NOT_PROVEN, never relabeled generic optimizers.

### Stage 4 — ensembles / robustness / freeze

FULL roles: Vanilla anchor, price, direction, stability and best refinement/hybrid representative (deduplicate identities). REDUCED removes an unprotected role if dominated and signed-error correlation>.95; protect anchor/price/direction. Commit both pools before computing ensemble outcomes.

Both pools: simple average; median; inverse prior-MAE; nonnegative sum1 ΣAE-optimal simplex; shrinkage alpha [0,.1,.25,.5,.75,1]. First6 DEV origins equal weights; thereafter only preceding DEV errors. Full-DEV simplex DIAGNOSTIC ONLY. Alpha selected on prequential DEV. External weights frozen at DEV end. Pool selection uses full DEV, so these are conditional prequential estimates, not an independent nested holdout. Report leave-one-component-out, year/tail/leave-one-origin, numerical and uncertainty limits. Primary promotion only on predeclared DEV price/direction evidence.

### Stage 5 — cross-family final

Recompute matched monthly evidence for ChHHO-ANFIS, REDUCED4/FULL7 ANN, AOA-ELM, SMA-ELMFIS, DE-ABC-RBFNN and best GP single/hybrid/ensemble. Report two-objective Pareto, year stability and leave-one-origin sensitivity. Historical external protocols differ: display them with limitations, never use them as selection authority. No automatic next family.

## 5. Evidence and checkpoint policy

One binding monthly ledger; this document stores method/protocol detail. Per batch record run ID, job ID, artifact ID, script/workflow, execution SHA, specification/bounds, DEV and external metrics/gates, accept/reject/parent/benchmark decision and next action. Raw artifacts and provenance archived in repo. Each major stage receives Kontrol ve Uyum Özeti. States: PLANNED / RUNNING / COMPLETE / SCIENTIFIC_REJECTED / IMPLEMENTATION_BLOCKED / NOT_PROVEN / SUPERSEDED.

Current checkpoint: authority/specification and technical implementation in progress; no GP production results yet. Resume from latest GitHub run/artifact evidence, not an old conversation. Authorization to proceed persists across stages and context compaction.


## Implementation clarification recorded during Stage3A (no experiment change)

The frozen repository Stage1 optimizer interfaces call `validation_pick` at initialization and successive generations, retaining the best chronological validation candidate among each snapshot's top training-loss quartile (`max(3,population//4)`). Thus “final candidates/repeats” above means the retained candidate returned at the end of each optimizer run, not validation evaluated only at the final generation. Evolution still uses training NLL; target/future months remain excluded. Stage3B uses the same snapshot-retention mechanism. Stage3A deliberately validates each final training winner and chooses among three final repeats, with its stated nested historical validation for q. Validation evaluation counts therefore differ; equal final population/generation budgets do not imply equal selection opportunities or objective calls. All actual call counts and immutable source hashes were already stored. This clarifies the pre-execution code rather than changing algorithms, bounds, seeds or results.
