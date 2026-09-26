# Stage 3C predeclared methodological authority

Candidate: **MOLS + ridge RBFNN**, a literature-derived structural challenger.
Primary source: S. Chen, P. M. Grant and C. F. N. Cowan (1991), *Orthogonal least squares algorithm for training multi-output radial basis function networks*, Second International Conference on Artificial Neural Networks, pp. 336–339.
Author-hosted full text: https://www.southampton.ac.uk/~sqc/listP/c-icann1991.pdf

The paper selects centers from training input points by orthogonal forward regression, maximizing the increment in explained multi-output covariance trace. Near-dependent candidate basis vectors are excluded. This directly differs from k-means anchors plus stochastic center/width perturbations in Stage 3A/3B.

Our declared adaptations: Gaussian bases with intercept; four standardized metal returns; center count [4,6,8,12] selected chronologically rather than the paper's tolerance stopping; width = training median positive pair distance times [0.5,1,1.5,2]; ridge [0,0.0001,0.001,0.01,0.1]. Validation uses the project's Gold-weighted MAE. Output weights remain analytic. No new external data. All external geometry/hyperparameters freeze at 2024-12; only analytic output coefficients expand afterward.

This is an adapted implementation, not a reproduction of the paper's application results. Technical test independently checks the first center's explained-trace optimum. Production execution requires completed Stage 3A/3B closure. No performance evidence used in candidate definition.
