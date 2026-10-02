# SAGE-H3 V1 — SESSION-AWARE GOLD ENGINE AUTHORITY

**Date:** 2026-10-02
**Identity:** `SAGE_H3_V1_RESEARCH`
**Parent:** `IRIS_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Hypothesis

IRIS established that recent hourly XAU path information is materially more useful than the previous daily-only H3 information set. SAGE tests a more structured hypothesis:

**the same total 12-24 hour move can have different H3 implications depending on which global trading session generated it and whether later Western trading confirms or reverses the Asian move.**

SAGE is therefore a session price-discovery decomposition, not another generic classifier family.

## 2. Timing

- H3 target and daily timeline remain the Global-XAU R2 authority.
- Hourly source remains the validated IRIS 1h bridge.
- Anchor remains **16:00 America/New_York on feature_cutoff_date**.
- No forecast_issue_date hourly bar is used.

## 3. Session decomposition

Using New-York-local hourly closes available by the 16:00 anchor:

- ASIA: previous local day 18:00 -> current day 03:00
- EUROPE: 03:00 -> 08:00
- US_AM: 08:00 -> 12:00
- US_PM: 12:00 -> 16:00

These are an hourly-data approximation of the global Asia/Europe/US gold price-discovery windows documented in prior research and current World Gold Council intraday decompositions.

Primary session returns:
- `sess_asia`
- `sess_europe`
- `sess_us_am`
- `sess_us_pm`

Derived phase variables:
- `sess_us_total = US_AM + US_PM`
- `sess_west_total = EUROPE + US_AM + US_PM`
- `sess_east_west = ASIA - WEST_TOTAL`
- `sess_us_reversal = US_PM - US_AM`
- `sess_dispersion = std(ASIA, EUROPE, US_AM, US_PM)`
- `sess_sign_changes` across the ordered four-session path
- `sess_dominance = max(abs(session return))/sum(abs(session returns))`
- `sess_asia_us_interaction = ASIA * US_TOTAL`
- `sess_east_west_conflict = 1[ASIA * WEST_TOTAL < 0]`
- `sess_us_conflict = 1[US_AM * US_PM < 0]`.

## 4. Frozen candidate representations

All models are StandardScaler + LogisticRegression(L2, C=1.0).

Comparator:
- `BASE_IRIS` = A1 structural logit + frozen IRIS PATH features.

Candidates:
1. `A1_SESSION` = A1 structural logit + session/phase features.
2. `SESSION_ONLY` = session/phase features only.
3. `PATH_SESSION` = IRIS PATH + session/phase features, without A1.
4. `A1_PATH_SESSION` = A1 + IRIS PATH + session/phase features.

No post-2022 representation or hyperparameter search is allowed.

## 5. Evaluation chronology

To reduce dependence on already-inspected later history:

- Jan-Jun 2022: initial expanding training / burn-in.
- **Jul-Dec 2022: representation selection authority.**
- **2023: frozen confirmation 1.**
- **2024: frozen confirmation 2.**
- 2025: frozen transport.
- 2026: frozen stress transport.

At every monthly origin block, training includes only rows with:
`target_end_date_h3 <= test feature_cutoff_date`.

## 6. Selection rule — 2022 H2 only

Matched-row BASE_IRIS is the comparator.

Candidate eligibility:
- balanced accuracy >= BASE_IRIS balanced accuracy;
- accuracy >= BASE_IRIS accuracy - 0.5 percentage points;
- Brier <= BASE_IRIS Brier + 0.0025;
- prediction SD >= 0.02.

Among eligible candidates:
1. highest balanced accuracy;
2. highest accuracy;
3. lowest Brier;
4. lowest log loss.

If no session candidate is eligible, SAGE V1 fails closed.

## 7. Confirmation rule

The 2022-selected representation is a **mechanism pass** only if, separately in both 2023 and 2024:
- balanced accuracy >= matched BASE_IRIS;
- accuracy >= matched BASE_IRIS - 1.0 percentage point;
- Brier <= matched BASE_IRIS + 0.003.

No 2023/2024 failure may be repaired using 2025/2026.

## 8. 2026 diagnostics

After the model is frozen, report:
- monthly accuracy / balanced accuracy;
- BASE_IRIS wrong calls rescued by SAGE;
- BASE_IRIS correct calls broken by SAGE;
- accuracy conditional on East-West conflict vs agreement;
- accuracy conditional on US_AM/US_PM conflict vs agreement.

These diagnostics do not change V1.

## 9. Interpretation

SAGE is designed to test whether **where inside the 24-hour global gold market a move occurs** is more informative than raw multi-scale return magnitude alone.

The 2025/2026 results remain retrospective transport evidence, not pristine prospective proof.
