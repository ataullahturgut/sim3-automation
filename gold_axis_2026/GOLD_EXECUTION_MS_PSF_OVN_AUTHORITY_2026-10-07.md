# GOLD EXECUTION MS-PSF OVERNIGHT AUTHORITY — 2026-10-07

**Status:** PREREGISTERED SUCCESSOR / NO 2025 TUNING
**Target:** 17:00 -> next eligible 09:00 Europe/Istanbul

## Hypothesis

The overnight mapping from pre-17:00 path to direction is regime-dependent. A single calendar-time classifier averages incompatible continuation/reversal states.

Scientific basis:
- Rosa (2022), Journal of Futures Markets, DOI 10.1002/fut.22375: intraday momentum can disappear OOS in calendar time while a Markov-switching model reveals regime-dependent predictability; thresholded implementation can outperform always-active use.
- Pradkhan (2016), Journal of Futures Markets, DOI 10.1002/fut.21755: precious-metal return relations are asymmetric across Markov bull/bear regimes.
- Choi (2026), Journal of Forecasting, DOI 10.1002/for.70176: lead-lag signature features encode path dependence / quadratic variation and are tested in finance including gold.

## Origin-known regime observation vector

Use only the completed 14:00-17:00 Europe/Istanbul XAU path:
- 3h return
- realized volatility
- semivolatility balance
- sign-change count
- normalized lead-lag signature area
- normalized time-price signature area

No target outcome and no future macro data enter the regime model.

## Latent state model

- Gaussian HMM
- exactly 2 states
- diagonal covariance
- rolling 250-origin history
- minimum 120 rows
- random_state fixed
- parameters fit only on observations strictly before current origin
- state labels canonicalized by emission mean of realized volatility: LOW_VOL / HIGH_VOL
- current state posterior is filtered at the current origin; no future observation may enter.

## Direction experts

Two L2-logistic experts:
- LOW_VOL expert trained on matured historical rows whose causal state posterior >= 0.50 for LOW_VOL
- HIGH_VOL expert trained analogously
- minimum 60 rows per expert
- if an expert is underfilled, fall back to the global M4_SIG_FPCA_MACRO expert.

Expert features:
- PSF M4 features: scalar path + lead-lag signature + FPCA(2) + origin-known macro state.

Prediction identities:
1. MS_MIX_FULL: posterior-weighted mixture of low/high expert probabilities.
2. MS_AGREE: act only when both experts give same direction.
3. MS_DOMINANT75: if experts disagree, act only when one regime posterior >= 0.75; otherwise abstain.

No confidence threshold search is allowed.

## Governance

- 2022 warm-up
- 2023-2024 development evidence
- 2025 retrospective frozen transport evidence
- no parameter, state count, posterior threshold, feature family or fallback may be changed after reading 2025.

Required:
- 2023 / 2024 / 2025 N, coverage, accuracy, BA, class recalls
- compare against M4 PSF and PAIR on exact common rows
- report regime occupancy and expert disagreement
- rescue/break/net on exact common rows
- no production claim unless both development years are >50 BA and 2025 transport is directionally coherent.
