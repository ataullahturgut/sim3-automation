# GOLD CONTROL — UP COUNTERSIGN VETO V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** DOWNSIDE_UP_COUNTERSIGN_VETO_V1_RESEARCH  
**Parent risk model:** SQRT-HAR-DR annual-origin downside-risk alert  
**Branch:** gold-downside-up-counterveto-v1-20260922  
**Runtime / production authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. User hypothesis

The parent SQRT-HAR-DR alert may correctly identify a high-risk state while still being wrong as a forced next-day DOWN direction call.

V1 tests the user's counter-model idea:

> If SQRT-HAR-DR says downside risk is high, but an independently constructed model that is explicitly capable of issuing an UP direction says UP at the same origin, suppress the forced-DOWN interpretation.

This is a verifier/veto experiment. It does not modify the parent SQRT-HAR-DR model.

## 2. Frozen parent interpretation

At origin t:

- parent alarm = sqrt_high_risk_alert == 1;
- baseline forced direction call = DOWN;
- actual DOWN = parent target_close_return < 0;
- actual UP = parent target_close_return >= 0.

The baseline therefore contains only alarm days. A veto may convert the baseline forced-DOWN call into NO-DOWN / SUPPRESSED. It does not create an UP trading signal.

## 3. Eligible counter-models

Only already-frozen, next-trading-day direction outputs with origin-safe construction are eligible.

### Family A — TTSM realized-semivariance

Source identity:
DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_RESEARCH

Primary source:
Liu, Lu, Li & Wang (2023), Journal of Empirical Finance 72, 54–77,
DOI 10.1016/j.jempfin.2023.03.001.

Surfaces tested separately:
- TTSM_S1_UP: ttsm_s1_signal == +1;
- TTSM_S2_UP: ttsm_s2_signal == +1.

Neutral and DOWN states do not veto.

Available primary pre-2025 evidence: 2022–2024.

### Family B — Bonato QBoost realized moments

Source identity:
DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_RESEARCH

Primary source:
Bonato, Demirer, Gupta & Pierdzioch (2018), Resources Policy 57:196–212,
DOI 10.1016/j.resourpol.2018.03.004.

Only h=1 conditional-median sign is eligible:
- BONATO_AR1_UP: AR1_QBOOST_q0.50 > 0;
- BONATO_AR1_RM_UP: AR1_RM_QBOOST_q0.50 > 0.

Available primary pre-2025 evidence: 2023–2024.

### Family C — Altuntaş AlexNet candle model

Source identity:
DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_RESEARCH

Primary source:
Altuntaş, Okumuş & Kocamaz (2022),
DOI 10.53070/bbd.1205299.

Eligible surface:
- ALTUNTAS_UP: frozen pred_up == 1 using the original frozen P(UP)>=0.5 rule.

No new confidence threshold is introduced.

Available primary pre-2025 evidence: 2024.

## 4. Horizon-alignment exclusion

Weekly models such as BCTX-AR, VLMC-BS, COVLMC, RealP-CARR and Parisi Rolling-Ward are not eligible for V1 because their one-week target clock is not the same next-trading-day clock as the SQRT-HAR-DR parent alert.

A model is not admitted merely because it historically predicted UP frequently.

## 5. Exact-date join rule

Join a counter-model to the parent by exact forecast origin date.

For every model:
- candidate information must be completed no later than the parent origin;
- candidate prediction must refer to the next retained trading-day direction;
- no nearest-date carry, forward fill, interpolation or weekly carry-over is allowed.

If an exact origin is absent, that parent alert is excluded from that candidate's overlap denominator.

## 6. Veto mechanics

For each candidate independently:

- if parent alarm == 1 AND candidate says UP: suppress the forced-DOWN call;
- otherwise retain the forced-DOWN call.

Define:

- GOOD_VETO = candidate UP and actual parent direction is UP;
- BAD_VETO = candidate UP and actual parent direction is DOWN;
- BASELINE_FP = parent alarm and actual UP;
- BASELINE_TP = parent alarm and actual DOWN.

Mandatory candidate metrics:
- overlap alarm count;
- baseline TP / FP on overlap;
- number vetoed;
- GOOD_VETO;
- BAD_VETO;
- veto precision = GOOD_VETO / vetoed;
- false-alarm reduction = GOOD_VETO / BASELINE_FP;
- true-positive retention = (BASELINE_TP - BAD_VETO) / BASELINE_TP;
- remaining-DOWN precision after veto;
- precision change versus baseline;
- remaining DOWN-call count.

The target is not overall classifier accuracy. The verifier's job is specifically to remove false forced-DOWN calls without destroying too many true DOWN calls.

## 7. Family-consensus veto

To avoid overweighting correlated variants, define three family votes.

TTSM family UP:
- TTSM_S2_UP == true.

Bonato family UP:
- BONATO_AR1_UP == true AND BONATO_AR1_RM_UP == true.

AlexNet family UP:
- ALTUNTAS_UP == true.

On common exact-date overlap, FAMILY_CONSENSUS_2OF3 vetoes only when at least two of the three family votes are UP.

No other Boolean combination may be invented after results are seen under V1.

## 8. Evidence periods

Candidate-specific primary evidence uses all available pre-2025 frozen origins:
- TTSM: 2022–2024;
- Bonato: 2023–2024;
- Altuntaş: 2024;
- 2-of-3 family consensus: 2024 common overlap.

2025 is an unchanged retrospective stress test only.
2026 is not used because these candidate artifacts do not provide a common frozen 2026 next-day surface.

No random split.

## 9. Interpretation rule

Because pre-2025 parent alarm support is small, V1 is a falsification / mechanism diagnostic, not a promotion test.

A candidate is tagged COUNTERSIGN_VETO_PROMISING only if on its primary pre-2025 overlap:

1. veto precision >= 0.65;
2. false-alarm reduction >= 0.25;
3. true-positive retention >= 0.80;
4. remaining-DOWN precision improves by at least +0.05 absolute;
5. at least 5 parent alerts are vetoed.

If support is below five vetoes, status is INSUFFICIENT_VETO_SUPPORT regardless of percentages.

FAMILY_CONSENSUS_2OF3 is additionally required to have at least 10 common parent alarms in 2024 before any positive label is allowed.

2025 may confirm fragility or descriptive transport but cannot rescue a failed pre-2025 gate.

## 10. Forbidden post-result actions

Under V1 do not:
- change the parent risk threshold;
- change candidate direction thresholds;
- introduce AlexNet P(UP) cutoffs above/below 0.5;
- choose another Bonato quantile after seeing intersections;
- switch TTSM S1/S2 logic after results;
- carry weekly signals into daily origins;
- optimize Boolean consensus;
- tune on 2025;
- call a vetoed parent alarm an UP trading signal.

A successor may be preregistered only under a new identity.
