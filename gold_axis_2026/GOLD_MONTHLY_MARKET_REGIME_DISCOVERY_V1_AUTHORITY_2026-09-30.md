# GOLD MONTHLY — Gold Market Regime Discovery V1 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / MARKET-STATE ONLY
**Purpose:** determine whether statistically persistent gold-market regimes exist, independently of forecast errors and alarm labels.

## 1. Prohibited inputs

The following are forbidden from regime construction, model selection, naming, or validation:
- ChHHO forecast error;
- A/B/C/D/E/G/H/I1/I2/T1 alarm flags;
- HIGH/MEDIUM/NORMAL error labels;
- model forecasts;
- routing/fallback outcomes.

## 2. Market-state panel

Monthly state is indexed by the completed calendar month.

Core features, all market-observable:
- Gold 1-month log return;
- Gold 3-month log return;
- Gold level gap versus prior-12-month mean;
- Gold realized-volatility ratio versus prior 12-month median;
- cross-metal monthly-return dispersion across Gold/Silver/Platinum/Palladium;
- GVZ ratio versus prior-12-month median;
- CFTC Managed-Money net/OI;
- CFTC open-interest ratio versus prior-12-month median;
- broad USD monthly log change;
- nominal 10Y monthly-mean change;
- real 10Y monthly-mean change;
- combined GLD/IAU monthly flow proxy;
- GLD/IAU two-fund outflow breadth.

Panel target coverage: 2010-01 through 2026-08, subject to complete-source gates.

## 3. Train / transport split

- REGIME DEVELOPMENT: 2010-01..2024-12
- TRANSPORT / STRUCTURAL CHECK: 2025-01..2026-08

2025/2026 is not used to choose the number of regimes, scaling, PCA dimension, HMM parameters, or GMM parameters.

## 4. Preprocessing

- complete-case monthly panel;
- fit StandardScaler on 2010-2024 only;
- fit PCA on 2010-2024 only;
- retain the minimum number of PCs explaining >=85% variance, capped at 6 and floored at 2;
- apply the frozen transform to 2025/2026.

## 5. Primary regime model — Gaussian HMM

Fit diagonal-covariance Gaussian HMMs with K=1..5 states on 2010-2024 only.

For each K:
- 10 deterministic random initializations;
- retain the highest training log-likelihood run;
- compute BIC using start probabilities, transition matrix, state means and diagonal variances.

Primary K = minimum BIC.

Regime-existence evidence is STRONG only if:
- selected K >=2;
- BIC improvement versus K=1 is >=10;
- at least two states have >=12 training months;
- average self-transition probability >=0.60.

## 6. Robustness model — Gaussian mixture

Fit GMM K=1..5 on the same frozen PCA scores.

Report:
- BIC by K;
- selected K;
- silhouette for K>=2.

GMM is robustness evidence only; it does not replace HMM because persistence matters.

## 7. Independent structural-break check

Run multivariate PELT/RBF change-point detection on the frozen standardized/PCA state series.

Use three pre-fixed penalties:
- 2*log(n);
- 4*log(n);
- 6*log(n).

Report break dates and dates shared by at least two penalties within +/-2 months.

No break penalty is selected using forecast-error outcomes.

## 8. 2025/2026 transport diagnostics

Using the frozen 2010-2024 HMM:
- sequentially filter state probabilities month by month;
- assign 2025/2026 state by filtered posterior maximum;
- report state occupancy by year;
- report state-probability confidence;
- compute each month's emission log-density under the fitted HMM;
- flag OOD months below the 5th percentile of 2010-2024 monthly emission log-density.

Compare 2025 and 2026 state occupancy with 2010-2024 using Jensen-Shannon distance.

## 9. Required outputs

- complete monthly regime table;
- HMM/GMM model-selection table;
- state transition matrix;
- state duration/spell statistics;
- original-feature state profiles;
- 2010-2024 regime timeline;
- 2025 and 2026 regime assignments;
- change-point dates;
- explicit answer to:
  1. are statistically persistent regimes supported?
  2. how many regimes are supported?
  3. did 2025/2026 show a different regime mix?
  4. are any 2025/2026 months outside the historical state distribution?

## 10. Governance

- This study does not select alarms.
- This study does not score alarms.
- This study does not change forecast or routing logic.
- Alarm-conditioned reliability is a later stage only if regime evidence is first established.
