# GPR Stage3C — LMC2_RBF_M32 authority and pre-outcome freeze

Status: FROZEN_BEFORE_PRODUCTION. Verified2026-09-26 after Stage3AB closure commit `e5f3ad9d6ca59fbe4696d80a4040566e710ccdc9`. Exactly one literature candidate opens. No LMC production results have been observed.

## Primary sources verified and adaptation boundary

- Álvarez, Rosasco & Lawrence (2012), [Kernels for Vector-Valued Functions: a Review](https://arxiv.org/pdf/1106.6251), section4 equations(10),(19)–(21), section6.2 equations(31)–(33): sums of separable covariance terms, LMC versus ICM, Gaussian marginal likelihood and learned coregionalization factors. Our implementation uses Q=2 and full-rank4 task covariance for each kernel group; this is a project adaptation, not replication of a published gold-forecast experiment.
- Rasmussen & Williams (2006), [GPML chapter5](https://gaussianprocess.org/gpml/chapters/RW5.pdf), section5.4.1 equations(5.8),(5.9), pages114–115: marginal likelihood derivatives and multiple local optima. The implementation minimizes negative likelihood, hence uses the opposite derivative sign; an explicit parameter prior is added.

Sources justify the covariance/inference mechanisms. RBF+Matérn-3/2, bounds, prior, seeds and budgets below are explicit project choices. They do not establish predictive superiority. One structural candidate satisfies the authorized1–3 range; extra optimizer relabelings are not opened as literature methods.

## Frozen specification

Same governed eight VW-MIDAS inputs, four metal log returns, H1 monthly gold price target, chronological inner split and train-only scalers as the main GPR authority. DEV33 exclusively selects; external2025/2026 report only. No additional data or features.

C = B1 ⊗ K_RBF + B2 ⊗ K_M32 + diag(noise_variance + 1e-8) ⊗ I.

Both scalar kernels have unit diagonal and separate8-dimensional ARD length scales. Each Bq=Lq Lqᵀ is4×4 with positive Cholesky diagonal. This corresponds to four latent functions per kernel group, rather than two rank-one latent functions. The two matrices need not be proportional; the model can represent output relationships that vary with the input covariance component. No claim of identifiable unique decomposition is made.

40 transformed parameters, in implementation order:

| Indices (zero-based) | Parameters | Natural-scale bounds |
|---|---|---|
|0:8|RBF log length scales|[0.05,20]|
|8:16|Matérn-3/2 log length scales|[0.05,20]|
|16:20,26:30|Two log Cholesky diagonals|[0.1,3]|
|20:26,30:36|Two sets of free lower-triangle entries|[-2,2]|
|36:40|Four log noise standard deviations|[0.01,2]|

Prior center: first length scales1, second2; each Lq diagonal√0.5; off-diagonals0; noise SD0.3. Training objective [NLL +0.5||theta−prior||²]/(4N), i.e. transformed-coordinate prior strength1. Final point forecast remains previous gold actual×exp(predicted gold return mean), with observed-return uncertainty including learned noise.

Exact dense4N covariance and Cholesky inference; no sparse approximation or post-fit nonlinear refit. Analytic NLL derivative is0.5 tr[(C⁻¹−aaᵀ)∂C/∂theta], a=C⁻¹y; prior derivative added before normalization. Derivatives of both kernels, both Cholesky factors and noise are implemented explicitly. All40 analytic derivatives passed central finite-difference checks on synthetic data; independent covariance indexing/mean/variance and target/future-label invariance also passed. The analytic gradient was prepared on synthetic data before activation, without examining production performance.

Three bounded L-BFGS-B starts; maxiter60, maxfun1600, ftol1e-7, analytic jacobian. First start prior center; later starts clipped prior+Normal(0,0.15) in transformed coordinates. Seed=(first8 hex digits SHA256(target)+7777×repeat+1911) mod2³². Final historical validation loss0.7 Gold MAE+0.3 all-output MAE selects repeat. Record every seed, objective evaluation count, termination message/success and theta. Finite budget-limited fits remain marked, without claiming convergence or global optimality.

External tuning once through2024-12, frozen theta/kernel/scalers thereafter; only expanding analytic posterior conditioning. Same numerical/scientific gates: finite predicted returns with absolute value<1, positive observed variances, latent variance no less than−1e-7, valid covariance Cholesky and certified condition upper bound≤1e12. Dense bound max absolute row sum(C)/minimum(noise+jitter) is conservative. Failed periods cannot be subset-ranked; no performance-driven parameter rescue.

## Execution and acceptance

Stage3AB closure and this document's SHA256 are written into the result. Workflow `.github/workflows/gpr-stage3c-v1.yml`, runner `tools/gpr_lmc_experiment_v1.py`, algebra `tools/gpr_lmc_core_v1.py`, technical gate `tools/test_gpr_lmc_core_v1.py`. Authority commits before workflow activation. Single job, timeout180minutes; timeout is an implementation/compute limitation, not a scored scientific result.

After audit, close all Stage3. LMC may enter DEV price/direction/stability roles in Stage4. The separate mandatory-refinement representative remains best Stage3A/B optimizer refinement; this role's definition predates LMC outcomes. Pools then commit before any ensemble evaluation. No additional LMC kernel/prior/budget variants will be selected from2025/2026 or opened to rescue this candidate's result.

## Kontrol ve Uyum Özeti

Primary equations verified; prototype numerical/gradient/chronology tests PASS; production NOT_YET_RUN; no external evidence used for candidate definition; Stage3AB closed before this authority; full specification frozen before outcomes.
