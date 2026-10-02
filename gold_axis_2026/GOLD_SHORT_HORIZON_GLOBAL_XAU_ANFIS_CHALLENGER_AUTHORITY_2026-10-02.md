# GOLD SHORT-HORIZON GLOBAL XAU — ANFIS Challenger Authority

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN  
**Project:** GLOBAL_XAU_PUBLIC_STAKTRAKR_R2  
**Comparator:** H3 / CORE3 / Logistic-L2 / RAW

## 1. Ordered execution

The user-authorized order is binding:

1. **Vanilla ANFIS first**
2. **ChHHO-ANFIS hybrid second**

No hybrid result may be used to rewrite the vanilla specification.

## 2. Common daily target/governance

- Frequency: daily.
- Target: H3 direction, `1[target_r3 > 0]`.
- DEV selection: forecast-issue dates 2022-01-01..2024-12-31 only.
- 2025: frozen transport only.
- 2026: frozen/opened reporting only.
- Random split: none.
- Block cadence: 5 DEV origins.
- Training at each DEV block may use only labels whose `target_end_date_h3` is fully mature by the block feature-cutoff date.
- Inputs: frozen **CORE3** only.
- No threshold tuning on 2025/2026.
- Probability classification threshold: 0.50.

Frozen comparator:
- CORE3 / Logistic-L2
- DEV Brier 0.2466373999
- DEV log loss 0.6864471944
- DEV accuracy 54.97%
- DEV balanced accuracy 54.48%.

## 3. Vanilla ANFIS contract

Adapt the accepted monthly canonical Jang-style ANFIS architecture to the daily binary H3 target.

Architecture:
- 14 CORE3 inputs.
- 5 compact Gaussian rules.
- Product AND / normalized firing.
- First-order Sugeno/TSK consequents.
- Consequents solved analytically by least squares.
- Binary target remains 0/1; premise MSE is therefore Brier-scale loss.
- Deterministic training-only KMeans initialization.
- Premise centers/log-spreads updated by normalized Jang-style gradient.
- initial step size 0.01.
- +10% after four consecutive training-loss reductions.
- -10% after alternating error movement per the monthly canonical implementation.
- maximum 100 local epochs.
- chronological checking tail = last 20% of pre-origin training history.
- epoch selected by minimum checking Brier.
- selected epoch count then refit on all origin-safe training history.
- output clipped to [1e-6,1-1e-6] only for probability scoring.
- no metaheuristic.

Vanilla is an architecture anchor. Its DEV result is recorded regardless of promotion.

## 4. ChHHO-ANFIS daily hybrid contract

The hybrid is executed only after the vanilla run has completed and been recorded.

Architecture remains exactly the same ANFIS learner.

Hybrid mechanism:
- chaotic logistic-map initialization around the training-only KMeans ANFIS premise anchor;
- Harris Hawks Optimization of **premise centers and log-spreads only**;
- consequents solved analytically for every candidate;
- chronological inner checking selects premise candidate;
- local Jang-style ANFIS refinement follows HHO;
- no optimizer access to 2025/2026.

Daily computational contract:
- population = 8
- generations = 8
- deterministic repeat = 1
- center bounds on standardized X: [-4,4]
- spread bounds: [0.20,5.0]
- local refinement max epochs = 60
- same 5-origin DEV cadence.

This is a daily-compute adaptation of the monthly ChHHO principle, not a claim of parameter-for-parameter identity with the monthly H=1 model.

## 5. Challenger promotion gate

A candidate may be promoted over frozen Logistic-L2 only if all hold on DEV:

1. Brier relative improvement versus Logistic-L2 >= 0.50%.
2. Log loss <= Logistic-L2.
3. Prediction SD >= 0.02.
4. At least 2 of 3 DEV years have nonnegative Brier improvement versus Logistic-L2.
5. No DEV year is worse than Logistic-L2 by more than 2% relative Brier.

If a candidate fails, it remains recorded but is not rescued using opened outcomes.

## 6. Transport rule

Only a candidate that clears the DEV challenger gate is eligible for a one-shot frozen 2025 + 2026 Jan-Sep transport report.

Transport never changes the DEV decision.

## 7. Required outputs

For each stage:
- DEV prediction ledger
- aggregate metrics
- annual metrics
- comparator deltas
- gate decision
- architecture diagnostics.

The canonical daily manifest must record:
- Vanilla ANFIS result;
- ChHHO-ANFIS result;
- whether either becomes the frozen H3 challenger.
