# GOLD CONTROL — MARKET SHOCK V2 2026 MULTI-FREQUENCY LM AUDIT CONTRACT

**Date:** 2026-09-08  
**Status:** `PRE-REGISTERED / 2026-01..2026-05 COMMON-SUPPORT RESEARCH AUDIT`  
**Model:** corrected `GOLD_CONTROL_MARKET_SHOCK_CHALLENGER_V2`  
**Primary purpose:** determine whether LM5 episodes—especially previously uncorroborated LM episodes—are stable across alternative sampling frequencies or look frequency-isolated/noise-sensitive.

## 1. Scientific basis

This audit follows the robustness logic in:

- Lee & Mykland (2008), intraday volatility-standardized jump detection;
- Lee & Mykland (2012), Journal of Econometrics, DOI 10.1016/j.jeconom.2012.04.001: market microstructure noise can distort ultra-high-frequency jump detection and requires explicit treatment;
- Boudt, Croux & Laurent (2011), Journal of Empirical Finance, DOI 10.1016/j.jempfin.2010.11.005: robust periodicity adjustment improves intraday jump accuracy, increases power for relatively small jumps in low-volatility slots, and reduces spurious detections in high-volatility slots;
- Dumitru & Urga (2012), Journal of Business & Economic Statistics, DOI 10.1080/07350015.2012.663250: ABD/LM perform well and combining tests/frequencies can reduce spurious jumps;
- Maneesoonthorn, Martin & Forbes (2020), Journal of Econometrics, DOI 10.1016/j.jeconom.2020.03.012: jump-test size/power depends on sampling frequency, volatility jumps, and microstructure noise;
- Sobti (2025), International Review of Financial Analysis, DOI 10.1016/j.irfa.2025.104380: for gold, uses Lee–Mykland plus robustness methods and explicitly checks 1/3/5/10-minute sampling frequencies and multiple significance thresholds to avoid spurious/fake jump detection.

## 2. Frozen data scope

Use only the complete common support where the production Neon 1-minute cache exactly matches the prior direct historical baseline:

- `2026-01-01 <= ts < 2026-06-01`;
- 1-minute source: `xau_intraday_research_cache_1m`;
- 5-minute authoritative V2 source remains `xau_intraday_research_cache_5m`;
- June and July 2026 are excluded from this multi-frequency audit because the 1-minute cache is incomplete/missing there;
- no interpolation, no zero filling, no reconstruction across missing 1-minute periods.

Training for all frequency-specific LM statistics uses only data before `2026-01-01`.

## 3. Frozen sampling frequencies

Evaluate LM at:

- 1 minute: `N=1440`, `K=1350`;
- 3 minutes: `N=480`, `K=450`;
- 5 minutes: authoritative current V2, `N=288`, `K=270`;
- 10 minutes: `N=144`, `K=135`.

The K values preserve the current V2 local-variance temporal bandwidth of 1,350 minutes (`270 × 5 min`) across frequencies. This is a project robustness design choice, not claimed as a universal literature constant.

All frequencies use Boudt-style WSD periodicity fitted on their own pre-2026 training data.

## 4. Frozen significance levels

For every alternative frequency calculate LM flags at:

- 99.9%: `alpha = 0.001` — primary confirmation level, matching current V2;
- 99%: `alpha = 0.01` — marginal diagnostic;
- 95%: `alpha = 0.05` — weak diagnostic.

No significance threshold may be changed after viewing the output.

## 5. Event matching

The authoritative event population is V2 LM5 episodes in 2026-01..2026-05.

An alternative-frequency signal confirms an LM5 episode when its signal timestamp is within the following absolute tolerance of any LM5 signal timestamp in that episode:

- 1m: ±2 minutes;
- 3m: ±3 minutes;
- 10m: ±10 minutes.

5m is the base detector and is not counted as an independent confirmation.

## 6. Pre-registered evidence classes

At the primary 99.9% level:

- `FREQ_STRONG`: at least two of {1m, 3m, 10m} confirm, and at least one confirming frequency is 3m or 10m;
- `FREQ_CONFIRMED`: 3m or 10m confirms, but the `FREQ_STRONG` rule is not met;
- `MICRO_ONLY`: only 1m confirms; this does **not** count as strong confirmation because 1m is most exposed to microstructure noise;
- `FREQ_ISOLATED`: none of {1m, 3m, 10m} confirms at 99.9%.

For `FREQ_ISOLATED`, additionally report whether the event appears at 99% or 95% on any alternate frequency:

- `MARGINAL_99`;
- `MARGINAL_95`;
- `ISOLATED_EVEN_95`.

## 7. Link to prior corroboration audit

Recompute the prior 2026 full-scope classes on the Jan-May subset:

- ABD5 ex-post confirmation;
- LM10 confirmation;
- EVT30 confirmation.

The key target subgroup is `PRIOR_LM_ONLY_UNCORROBORATED` = no ABD5, no LM10, no EVT30.

For this subgroup report how many are:

- recovered as `FREQ_STRONG` or `FREQ_CONFIRMED` by 1m/3m/10m evidence;
- `MICRO_ONLY`;
- `FREQ_ISOLATED` and marginal at 99/95;
- `ISOLATED_EVEN_95`.

## 8. Interpretation rules

- Cross-frequency stability is evidence against a pure frequency-specific artifact.
- `MICRO_ONLY` is not sufficient to rehabilitate a prior-unconfirmed event.
- `ISOLATED_EVEN_95` is a **noise-suspect / weak-evidence** class, not an authoritative false positive.
- The old 0.50% raw-move proxy remains a separate economic-magnitude diagnostic and is not the primary truth label here.
- No LM/EVT parameter is retuned.
- No production filter is created from this audit alone.
- No 2025 audit begins until the 2026 evidence is interpreted.

## 9. Governance

`prospective_claim = false`  
`authoritative_false_positive_rate = NOT_PROVEN`  
`production_promotion = BLOCKED_RESEARCH_ONLY`  
`canonical_merge = NOT_AUTHORIZED`  
`production_neon_write = NONE`
