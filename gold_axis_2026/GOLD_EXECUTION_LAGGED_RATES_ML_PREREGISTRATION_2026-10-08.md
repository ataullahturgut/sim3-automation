# GOLD EXECUTION — Lagged US 2Y nominal & 10Y real-yield challenger (preregistered 2026-10-08)

**Research stage:** follow-up to origin-safe price-shape/GVZ trial, **not** a redefinition of its baseline or a 2025-selected re-optimization.

## Hypothesis
US nominal 2Y / 10Y real yields are economically plausible conditioning signals for the gold direction process, but their daily changes and historical price-level relationships can vary. Test whether **strictly prior-day** official Fed H.15 DGS2 and DFII10 observation levels and one-observation changes incrementally predict:
- DAY: 09:00-17:00 Türkiye time;
- weekday regular 16h OVERNIGHT-HOLD: 17:00-next 09:00 Türkiye time.

## Inputs
- Frozen audited single-vendor BID XAU15m, same accepted DAY/OVN target ledger.
- Previous-origin price shape and preceding-day Cboe GVZ exactly as in source-clean Stage-1 challenger.
- Fed H.15 DGS2 candidate, Fed H.15 DFII10 candidate, verified as official daily archives covering 2020-2026. Use last two nonmissing observations strictly DATE EARLIER THAN origin date (conservative D-1; no observation from origin day, no backfill from the future).
- If a series is missing, DROP candidate test date for **both** comparison and new models, not encode as zero or forward-origin leak.

## Models fixed in advance
- SHAPE_GVZ_RATES_LOGIT = previous Stage-1 SHAPE_GVZ_LOGIT features + lagged nominal 2Y level, lagged real 10Y level, last-available one-observation change for both. StandardScaler + L2 Logistic C=0.3.
- SHAPE_GVZ_RATES_HGB = same features, frozen previous HGB architecture (90 iters, 0.04 learning rate, 7 leaves, min leaf 35, depth 3, L2 10). No hyperparameter search.
- Two prior comparators: BASE_LOGIT and SHAPE_GVZ_HGB retrained using identical accepted dates.

## Evaluation
2022 warm-up, calendar-month expanding/purged training 2023-24, 2025 frozen as of 2025-01-01 and retrospective ONLY; 64h Fridays separate, never mixed. Compare same-year same-date BA, UP/DOWN recall, Brier, log loss, correct-call rescues vs breaks and paired exact McNemar. Evaluate all negative evidence, and do not promote any model based on 2025 after historical inspection. This second stage **adds two research trials** to multiple-testing ledger. Bank executable bid/ask and publication-vintage proof remain deployment blockers.

**Literature context:** Intraday gold state-dependence in Xu et al. (2020), DOI 10.1016/j.resourpol.2020.101830; Sobti, Sehgal & Ilango (2021), DOI 10.1016/j.irfa.2021.101893. The rates hypothesis is a NEW test, not a claim that either paper demonstrates the chosen exact rate covariates.
