# GOLD CONTROL — MARKET SHOCK V2 ROBUSTNESS CONTRACT

**Date:** 2026-09-08  
**Status:** `PRE-REGISTERED ROBUSTNESS AUDIT / RESEARCH ONLY / NO PRODUCTION PROMOTION`  
**Model:** `GOLD_CONTROL_MARKET_SHOCK_CHALLENGER_V2`  
**Data authority for this audit:** production Neon research cache `xau_intraday_research_cache_5m`  
**Scope:** `2020-04-06T00:00:00Z` through `2026-08-31T23:55:00Z`  
**Expected rows:** `482734`

## 1. Purpose

This audit is frozen before robustness output is viewed. It does not retune V2, change alpha, change POT/EVT settings, alter the LM local-variance window, alter the WSD periodicity estimator, change the OR rule, or authorize production use.

The purpose is to decide whether the corrected V2 implementation is sufficiently stable and reproducible to become the sole current Market Shock research implementation in the repository tree, while preserving rejected V1 history in Git history rather than keeping duplicate active source/workflow files.

V1 remains rejected because its Lee–Mykland Gumbel scale constant was incorrect. V1 cannot regain authority from this audit.

## 2. Authority basis

Robustness dimensions are motivated by:

- Lee & Mykland (2008), *Review of Financial Studies*: high-frequency nonparametric jump detection and finite-sample jump identification.
- Boudt, Croux & Laurent (2011), *Journal of Empirical Finance*: robust intraweek periodicity materially improves intraday jump-detection accuracy and reduces spurious detections in high-periodic-volatility intervals.
- Maneesoonthorn, Martin & Forbes (2020), *Journal of Econometrics*, “High-frequency jump tests: Which test should we use?”: jump-test performance should be evaluated for sampling/noise/volatility robustness, not only nominal detection power.
- Lee & Mykland (2012), *Journal of Econometrics*: microstructure noise can distort ultra-high-frequency jump detection; noise robustness is a distinct issue.
- multiple-testing literature on high-frequency jump detection: real-history false-positive truth requires independent labels and is not inferred from signal frequency alone.

## 3. Frozen V2 model parameters

The production-under-test code must retain exactly the V2 contract values:

- `K_LM = 270`
- `LM_MAIN_ALPHA = 0.001`
- `N_INTRADAY = 288`
- `POT_Q = 0.975`
- `TAIL_P = 0.001`
- `BNS_ALPHA = 0.001`
- `BNS_MIN_RETURNS = 200`
- shock rule = `LM_JUMP_5M OR EVT_FAST_MOVE_30M`
- no monthly forecast anchor
- no target/outcome leakage
- annual walk-forward fit boundaries unchanged.

## 4. Robustness tests and pre-registered gates

### R1 — Exact deterministic rerun

Recompute the full 2024/2025/2026 V2 annual fit + scoring package twice from the same cached data.

**PASS:** canonicalized fit/segment signatures are exactly identical.

### R2 — Prefix invariance / future-append immunity

For 2024 and 2025, recompute that year from data truncated at that year-end and compare with the same year's output produced when later years are present.

**PASS:** LM, EVT30 and V2 eligible bars, signal bars, signal rates, episode counts and fitted EVT critical values are exactly equal within `1e-12` for floats. Future observations must not alter prior-year output.

### R3 — Synthetic seed stability

For each holdout year, repeat controlled real-context synthetic injection over 20 predeclared seeds, `n=300` eligible bars per seed, both UP and DOWN.

**PASS:**
- minimum across all year/seed cells at `1.50%` jump >= `0.80`;
- minimum across all year/seed cells at `2.00%` jump >= `0.95`.

This keeps the original V2 power gates and tests whether the reported power is an artifact of one random seed.

### R4 — Volatility-regime robustness

Within each holdout year, partition eligible observations into quartiles of the causal denominator `local_sigma * period_factor`; evaluate permanent synthetic jumps over every eligible bar in each quartile.

**PASS:** every year/quartile cell must have:
- `1.50%` average UP/DOWN V2 power >= `0.80`;
- `2.00%` average UP/DOWN V2 power >= `0.95`.

No regime may be excluded after viewing the output.

### R5 — Direction symmetry

For each holdout year, compare UP and DOWN synthetic detection power using all eligible observations.

**PASS:** absolute UP-vs-DOWN power difference <= `0.05` at both `1.50%` and `2.00%`.

### R6 — Gap safety unit contract

Existing deterministic tests must continue to prove that a return spanning a >10-minute gap is not scored and that a 30-minute window crossing the gap is not scored.

**PASS:** V2 deterministic pytest suite passes unchanged.

### R7 — Microstructure-noise stress diagnostic

A controlled observation-noise sensitivity diagnostic will apply independent zero-mean log-price noise at `0.5 bp` and `1.0 bp` to holdout observations using fixed seeds and report resulting alarm-rate inflation with the causal denominator held fixed for the tested bar.

Because the production Twelve Data noise distribution and efficient-price truth are not independently identified, this is **diagnostic only**. It cannot prove a real false-positive rate and is not a promotion gate.

## 5. Existing V2 research gates remain binding

The original V2 research gates are not relaxed by this audit. In particular:

- real-history shock-bar rate `<1.0%` in every holdout segment;
- no-injection sample alert rate `<1.0%` in every segment;
- real-history false-positive rate remains `NOT_PROVEN` without an authoritative event-label set.

A robustness PASS does not turn an existing base-gate FAIL into PASS.

## 6. Repository cleanup decision

If R1–R6 all PASS, V2 is considered `SOLE_CURRENT_MARKET_SHOCK_RESEARCH_IMPLEMENTATION_READY` for repository-tree cleanup purposes only.

Then rejected V1 duplicate source/workflow/test/contract files may be removed from the current branch tree because Git history preserves the audit trail. The V2 contract must retain a concise statement that V1 was rejected for the primary-formula defect.

This cleanup status does **not** authorize:

- production runtime identity;
- UI promotion;
- selector/ensemble use;
- action mapping;
- production Neon writes;
- rewriting historical evidence.

If any R1–R6 gate FAILS, V1 files are not deleted in the same change set and the robustness defect must be investigated first.
