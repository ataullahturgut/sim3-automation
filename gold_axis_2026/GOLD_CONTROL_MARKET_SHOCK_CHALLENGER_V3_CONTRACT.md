# GOLD CONTROL — MARKET SHOCK CHALLENGER V3

**Status:** `CHANGE_CONTROL / RESEARCH CHALLENGER / NOT_PRODUCTION_AUTHORITY`  
**Branch:** `gold-control-market-shock-challenger-v3`  
**Parent:** `gold-control-market-shock-challenger-v2 @ b78fb23b0acab5cc4898a9daf074382352b63e13`  
**V1 status:** `REJECTED_PRIMARY_FORMULA_AUDIT`  
**V2 status:** `REJECT_OR_REVISE_CHALLENGER_V2`  
**Objective:** detect unusually abrupt / shock-like XAU/USD market-process moves without using any monthly forecast anchor.

## 1. Why V3 exists

V2 corrected the Lee–Mykland primary formula and retained strong injected-jump power, but it is not accepted. Its historical run failed the frozen anti-saturation / no-injection gates and, more importantly, showed severely inconsistent scoring coverage across holdouts. The V2 local bipower rolling implementation required a long run of non-missing adjacent products; routine >10-minute gaps therefore propagated missing local scale for many subsequent rows. V3 changes the method identity rather than relaxing V2 thresholds after seeing holdout results.

V3 does **not** alter or promote Emergency V1.46, the canonical forecast engine, selector/ensemble authority or production Neon state.

## 2. Authority basis

V3 is grounded in the following high-frequency volatility/jump literature:

- Andersen, Dobrev & Schaumburg (2012), *Journal of Econometrics*, DOI `10.1016/j.jeconom.2012.01.011`: nearest-neighbor jump-robust volatility estimation; MedRV has improved finite-sample robustness to jumps and small/zero returns and motivates short local blocks.
- Corsi, Pirino & Renò (2010), *Journal of Econometrics*, DOI `10.1016/j.jeconom.2010.07.008`: threshold bipower/multipower methods address finite-sample bias of standard bipower variation in the presence of jumps.
- Boudt, Croux & Laurent (2011), *Journal of Empirical Finance*, DOI `10.1016/j.jempfin.2010.11.005`: robust intraday/intraweek periodicity improves jump-detection accuracy and reduces spurious detections in normally high-volatility periods.
- Lee & Mykland primary extreme-value normalization remains the V3 instantaneous-jump threshold basis. The corrected V2 formula is inherited unchanged.

The exact Twelve Data XAU/USD trading-session calendar remains `NOT_PROVEN`. CME/EBS precious-metals session conventions may be used only as labelled external context, not silently imposed as Twelve truth.

## 3. V3 causal return and gap semantics

Provider identity remains Twelve Data `XAU/USD`, 5-minute closes.

- close-to-close log return is valid only when the preceding timestamp gap is between 4 and 10 minutes inclusive;
- a timestamp gap >10 minutes creates `REOPEN_GAP_CONTEXT`;
- the return spanning that gap is never treated as a 5-minute return;
- after each >10-minute gap, the gap row plus the next five 5-minute rows are in `GAP_REOPEN_WARMUP` (six bars / approximately 30 minutes total from the first post-gap timestamp);
- warmup bars cannot produce the V3 intraday shock signal;
- the observed price difference across a gap is retained only as a separately reported reopen-context move. It is not silently called a 5-minute jump and it does not vote in the V3 intraday shock state.

This rule is based on observable provider timestamps and therefore does not require pretending that an unverified exchange/session calendar applies to Twelve.

## 4. Causal jump-robust local scale

V3 replaces the gap-fragile V2 rolling bipower denominator with a strictly lagged MedRV-derived local scale.

For valid contiguous returns, a robust nearest-neighbor term is formed from the squared median of three adjacent absolute returns. The MedRV consistency constant is:

`c_med = pi / (6 - 4*sqrt(3) + pi)`.

For a row being tested at time `t`, the local scale uses only robust terms whose underlying returns end strictly before `t`.

Frozen local-scale parameters:

- maximum prior robust terms: `270`;
- minimum prior robust terms before scoring: `96`;
- maximum age of the latest robust term: `72 hours`;
- current tested return never enters its own denominator;
- future returns never enter its denominator;
- missing/gap rows are skipped rather than poisoning the following 270 row positions;
- scale older than 72 hours is not used.

This is a **causal MedRV-derived local adaptation**, not a claim that the live row-wise construction is identical to the full-sample Andersen–Dobrev–Schaumburg integrated-variance estimator.

## 5. Robust periodicity with explicit fallback

The prior-data WSD-style robust periodicity concept is retained, but missing exact weekday/5-minute slots may no longer silently make a large portion of holdout unscorable.

Training uses only data strictly before each annual holdout cutoff.

Hierarchy:

1. exact UTC weekday + 5-minute slot factor when at least `20` prior standardized observations exist;
2. otherwise pooled UTC time-of-day 5-minute slot factor when at least `50` prior standardized observations exist;
3. otherwise periodicity factor is missing and the row is reported as unscorable.

There is **no silent numeric factor of 1.0 fallback**. Exact/fallback/missing usage is reported.

## 6. V3 detectors

### C1 — `LM_JUMP_5M_V3`

- corrected Lee–Mykland normalization inherited unchanged from V2;
- `alpha=0.001` remains frozen;
- denominator = causal MedRV-derived local scale × prior-data robust periodicity factor;
- tested return excluded from denominator;
- warmup/gap rows cannot vote.

### C2 — `EVT_FAST_MOVE_30M_V3`

- 30-minute log move over six contiguous valid 5-minute intervals;
- no window may cross a >10-minute gap;
- no warmup row may vote;
- normalized by `sqrt(6) × local_scale × periodicity_factor`;
- prior-data POT quantile remains `97.5%`;
- GPD unconditional tail probability remains `p<=0.001`.

Binary rule remains frozen before replay:

`MARKET_SHOCK_V3 = LM_JUMP_5M_V3 OR EVT_FAST_MOVE_30M_V3`.

States remain `OFF`, `INSTANT_JUMP`, `FAST_MOVE`, `COMPOUND_SHOCK`. `REOPEN_GAP_CONTEXT` is reported separately and is not an intraday shock vote.

## 7. Walk-forward validation

- 2024 scoring: all fitted quantities strictly pre-`2024-01-01`;
- 2025 scoring: all fitted quantities strictly pre-`2025-01-01`;
- 2026 scoring: all fitted quantities strictly pre-`2026-01-01`, evaluation ending `2026-08-31 23:59:59Z`;
- no random split;
- September 2026 is excluded from V3 historical development evidence;
- raw provider prices remain in memory only and are not written to Neon or committed as artifacts.

## 8. Frozen V3 research gates

The V2 power and anti-saturation gates are retained unchanged; V3 adds an explicit coverage gate.

1. `2.00%` injected-jump power >= `95%` in every segment.
2. `1.50%` injected-jump power >= `80%` in every segment.
3. Injection power non-decreasing with at most 2 percentage-point Monte-Carlo tolerance between adjacent sizes.
4. Historical V3 shock-bar rate < `1.0%` in every segment.
5. Deterministic no-injection sampled-bar V3 alert rate < `1.0%` in every segment.
6. **Adjusted scoring coverage >= `90%` in every segment**, where the denominator is every valid-return bar outside `GAP_REOPEN_WARMUP`; missing local scale or missing periodicity counts against coverage.
7. Intraday V3 signal count during `GAP_REOPEN_WARMUP` must equal zero by implementation and test.
8. `FALSE_POSITIVE_RATE_REAL_HISTORY = NOT_PROVEN` unless an independent authoritative event-label contract is created.
9. BNS/day-level robustness remains diagnostic only, not a live vote or numeric promotion gate.

If any numeric/coverage gate fails, status is `REJECT_OR_REVISE_CHALLENGER_V3`. No threshold or gate may be relaxed after observing V3 holdout output; another method change requires a new identity.

## 9. Production remains blocked

Even a V3 research PASS means only `RESEARCH_GATES_PASS_NOT_PROMOTED`. Production/shadow integration requires separate governance, provider/session operational validation, continuous runtime/freshness proof, persistence/provenance review and explicit authorization.
