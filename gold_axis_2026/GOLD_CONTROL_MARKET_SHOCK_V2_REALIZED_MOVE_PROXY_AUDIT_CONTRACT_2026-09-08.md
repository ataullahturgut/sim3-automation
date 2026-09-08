# GOLD CONTROL — MARKET SHOCK V2 REALIZED-MOVE PROXY AUDIT CONTRACT

**Date:** 2026-09-08  
**Status:** `PRE-REGISTERED / HISTORICAL PROXY VALIDATION / RESEARCH ONLY`  
**Model:** `GOLD_CONTROL_MARKET_SHOCK_CHALLENGER_V2`  
**Data:** production Neon research cache `xau_intraday_research_cache_5m`  
**Execution order:** `2026 -> 2025 -> 2024`, with strict stop-on-fail.  

## 1. Question

Does a Market Shock V2 alarm episode correspond to an economically material raw XAU/USD price movement, rather than merely exceeding the model's own standardized LM/EVT statistics?

This audit does **not** claim authoritative true/false event labels. It produces a `REALIZED_MOVE_PROXY_FALSE_ALARM` diagnostic only.

## 2. Authority and rationale

- Lee & Mykland (2008), *Review of Financial Studies*, identifies intraday jump arrival times and realized jump sizes and relates detected jumps to external news events.
- Maneesoonthorn, Martin & Forbes (2020), *Journal of Econometrics*, shows that high-frequency jump-test evaluation must consider size/power, sampling frequency, volatility behavior and microstructure noise; a detector should not be accepted solely because its own statistic fires.
- The existing Gold Control historical audit already uses raw realized-move thresholds of 0.50%, 1.00%, 1.50% and 2.00% as independent descriptive movement magnitudes. This audit freezes 0.50% as the primary economically-material support floor before viewing any new output.

The 0.50% threshold and project pass gates below are governance criteria, not universal constants from the literature.

## 3. Frozen proxy label

All percentage moves below are calculated directly from raw cached close prices, not from LM/EVT scores.

For each V2 signal episode:

- episode construction exactly follows V2 episode semantics: consecutive signal bars remain in one episode; a non-signal bar or a gap >10 minutes starts a new episode;
- if the episode contains an `LM_JUMP_5M` signal, its LM component is proxy-supported when at least one signal bar in that episode has an absolute raw 5-minute simple return `>= 0.50%`;
- if the episode contains an `EVT_FAST_MOVE_30M` signal, its EVT component is proxy-supported when at least one signal bar in that episode has an absolute raw 30-minute simple move `>= 0.50%`;
- an episode is `PROXY_SUPPORTED` when at least one component that actually fired is supported by its own raw-price horizon;
- otherwise the episode is `PROXY_UNSUPPORTED`.

No forward continuation requirement is imposed. Market Shock is a contemporaneous shock detector, not a 15/30/60-minute directional forecast.

## 4. Matched non-signal controls

For each signal episode, create five deterministic matched control windows from the same calendar month:

- same number of 5-minute bars as the signal episode;
- no Market Shock V2 signal bar inside the control window;
- no >10-minute gap inside the control window;
- the raw-return horizon required by the signal episode type must be available;
- deterministic seed `20260908 + year`;
- control support is evaluated with the same 0.50% raw-move rule and the same component horizon(s) as the paired signal episode.

The matched-control support rate estimates how often an equivalently sized ordinary window would satisfy the proxy by chance/background movement.

## 5. Frozen metrics

For each year report:

- signal bars and signal episodes;
- proxy-supported episodes;
- proxy-unsupported episodes;
- episode proxy precision = supported / all episodes;
- 95% Wilson interval for episode proxy precision;
- LM-containing, EVT-containing and compound episode support summaries;
- UP/DOWN episode support summaries;
- matched control windows and matched-control support rate;
- enrichment ratio = episode proxy precision / matched-control support rate.

`proxy_false_alarm_rate = 1 - episode_proxy_precision` is explicitly a proxy diagnostic, **not** an authoritative real false-positive rate.

## 6. Pre-registered year gate

A year is `PASS_PROXY_VALIDATION` only if all are true:

1. signal episodes `>= 30`;
2. episode proxy precision `>= 0.80`;
3. 95% Wilson lower bound `>= 0.75`;
4. enrichment ratio versus matched controls `>= 5.0`;
5. at least 90% of requested matched control windows are successfully constructed.

Otherwise:

- if episodes `<30`: `INSUFFICIENT_SAMPLE`;
- else: `FAIL_PROXY_VALIDATION`.

These thresholds are frozen before output is viewed and may not be relaxed after seeing results.

## 7. Sequential execution rule

- Run **2026 first**.
- Run **2025 only if 2026 = PASS_PROXY_VALIDATION**.
- Run **2024 only if 2025 = PASS_PROXY_VALIDATION**.
- Stop immediately on `FAIL_PROXY_VALIDATION`, `INSUFFICIENT_SAMPLE`, or execution error.

## 8. Governance

This audit:

- does not retune V2;
- does not change LM/EVT thresholds;
- does not change the existing `<1%` research alarm-rate gate;
- does not prove an authoritative real false-positive rate;
- does not create prospective evidence;
- does not authorize production promotion, UI promotion, selector use, action mapping, production Neon writes, canonical merge, or deployment.
