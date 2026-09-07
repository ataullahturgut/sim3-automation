# GOLD CONTROL — MARKET SHOCK CHALLENGER V2

**Status:** `CHANGE_CONTROL / RESEARCH CHALLENGER / NOT_PRODUCTION_AUTHORITY`  
**Branch:** `gold-control-market-shock-challenger-v2`  
**Parent audit state:** `gold-control-market-shock-challenger-v1 @ df01db0fc1ea81dd73c60f3a7653ba176009e123`  
**V1 status:** `REJECTED_PRIMARY_FORMULA_AUDIT`  
**Objective:** answer only the market-process question: **has XAU/USD undergone an unusually abrupt / shock-like move?** No monthly H=1 forecast may be used as an anchor.

## 1. Governance isolation

V2 is a new challenger identity. It does not patch, overwrite or promote V1, and it does not mutate `EMERGENCY_LEVEL` / `EMERGENCY_REVERSAL` V1.46. It creates no production runtime identity, no automatic action, no selector/ensemble authority and no production Neon write.

Binding locks remain: `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, no hindsight threshold tuning, no random split, no silent provider substitution, no target/outcome leakage, no backdating of evidence and no action mapping.

## 2. Authority correction inherited from V1 rejection

V1 used the wrong Lee–Mykland Gumbel scale constant. V2 uses the primary Lee–Mykland formula:

- `c = sqrt(2/pi)`;
- `C_n = sqrt(2 log n)/c - [log(pi)+log(log n)]/[2 c sqrt(2 log n)]`;
- **`S_n = 1/[c sqrt(2 log n)]`**;
- critical value for tail probability `alpha`: `C_n + S_n * beta_alpha`, where `beta_alpha = -log(-log(1-alpha))`.

The primary live-event significance remains frozen at `alpha=0.001` (99.9%). `0.05` and `0.01` are sensitivity outputs only. The alpha is not changed because of the V1 formula defect.

## 3. V2 architecture

V2 deliberately avoids pretending that two thresholds on the same 5-minute standardized return are independent detectors.

### C1 — `LM_JUMP_5M_V2` — primary instantaneous-jump detector

- provider identity: Twelve Data `XAU/USD`;
- primary sampling: 5-minute closes;
- return: close-to-close log return;
- a return is not scored when the preceding timestamp gap exceeds 10 minutes;
- causal local scale: preceding `K=270` valid 5-minute returns via adjacent absolute-return bipower products; the tested return is excluded from its own denominator;
- robust intraweek periodicity factor: WSD-style robust factor by UTC weekday / 5-minute slot, estimated from strictly prior training data;
- main threshold: corrected Lee–Mykland 99.9%;
- direction: sign of the tested 5-minute return.

### C2 — `EVT_FAST_MOVE_30M_V2` — distinct fast-move detector

- move: 30-minute log price change over six contiguous valid 5-minute intervals;
- windows crossing a >10-minute gap are not scored;
- normalization: causal 5-minute local scale times `sqrt(6)` and the prior-data periodicity factor;
- training tail threshold: prior-data 97.5th percentile of the normalized absolute 30-minute move;
- excess model: Generalized Pareto Distribution with location fixed at zero;
- main unconditional tail probability: `p <= 0.001`;
- direction: sign of the 30-minute move.

### V2 market-shock state

- `INSTANT_JUMP`: C1 only;
- `FAST_MOVE`: C2 only;
- `COMPOUND_SHOCK`: C1 and C2 on the same scored bar;
- `OFF`: neither.

For the binary B-question, `MARKET_SHOCK_V2 = C1 OR C2`. This OR rule is frozen before holdout review. `COMPOUND_SHOCK` is a stronger-confirmation subtype, not a prerequisite for declaring a shock-like market move.

## 4. Independent ex-post robustness — BNS daily jump audit

A separate Barndorff-Nielsen / Shephard realized-variation audit is computed at the session-bucket/day level and **does not vote in the live V2 signal**.

For valid 5-minute returns in a day/session bucket:

- `RV = sum(r_i^2)`;
- `BPV = mu_1^-2 * sum(|r_i||r_{i-1}|)`, `mu_1=sqrt(2/pi)`;
- `TQ = M * mu_(4/3)^-3 * sum(|r_i|^(4/3)|r_(i-1)|^(4/3)|r_(i-2)|^(4/3))`;
- ratio statistic `Z = sqrt(M) * ((RV-BPV)/RV) / sqrt((mu_1^-4 + 2*mu_1^-2 - 5) * max(1,TQ/BPV^2))`;
- ex-post significant-jump diagnostic: right-tail `Z > Phi^-1(0.999)`.

To avoid manufacturing a precise Twelve Data session calendar that has not been proven, V2 uses a clearly labelled **17:00 ET boundary bucket** based on the CME/EBS precious-metals market convention. Returns across >10-minute gaps are already excluded. A bucket requires at least 200 valid 5-minute returns before a BNS statistic is reported. This BNS result is ex-post robustness only and must not be described as causal intraday confirmation.

## 5. Point-in-time / walk-forward validation

Historical raw provider prices are processed in memory only. They are not committed, logged as raw values or written to Neon.

Frozen segments:

- 2024 scoring: all fitted quantities use data strictly before `2024-01-01`;
- 2025 scoring: fitted quantities use data strictly before `2025-01-01`;
- 2026 holdout scoring: fitted quantities use data strictly before `2026-01-01`; evaluation stops at `2026-08-31 23:59:59Z`, excluding the current open September context.

No random split is permitted. Periodicity and EVT parameters are recomputed only at the predeclared annual boundaries.

## 6. Synthetic-injection power audit

Because real history has no complete authoritative true/false shock label set, V2 also performs a deterministic controlled audit in real holdout volatility contexts.

Frozen permanent level jumps injected at eligible bars:

`0.25%, 0.50%, 0.75%, 1.00%, 1.50%, 2.00%`, both UP and DOWN.

The tested bar's causal volatility denominator is not recomputed after injection. Detection power is reported separately for C1, C2 and the V2 OR shock state. A fixed seed is used. No-injection sampled bars provide calibration evidence only; they are not an economic false-positive truth set.

## 7. Quantitative V2 research acceptance gates — frozen before holdout output

1. `2.00%` injected jumps: `MARKET_SHOCK_V2` power **>=95% in every holdout segment**.
2. `1.50%` injected jumps: `MARKET_SHOCK_V2` power **>=80% in every holdout segment**.
3. Injection power should be non-decreasing as magnitude rises, allowing at most 2 percentage points Monte-Carlo tolerance between adjacent sizes.
4. Real-history V2 shock-bar rate must remain **<1.0% in every holdout segment**; this is an anti-saturation gate, not a target rate.
5. Deterministic no-injection sampled-bar V2 alert rate must remain **<1.0% in every holdout segment**; this is calibration evidence, not a real false-positive rate.
6. `FALSE_POSITIVE_RATE_REAL_HISTORY = NOT_PROVEN` unless an independent authoritative event-label contract is later created.
7. BNS overlap is reported as an independent ex-post robustness diagnostic but is **not** a numeric promotion gate because a daily BNS non-rejection does not prove an intraday alert false.

If a numeric gate fails, V2 is `REJECT_OR_REVISE_CHALLENGER_V2`. V2 parameters may not be relaxed after viewing the holdout output; any method change requires a V3 identity and fresh pre-registration.

## 8. Production promotion remains blocked

Even if V2 passes the research gates, production promotion remains `BLOCKED` until all of the following are separately resolved:

- deterministic implementation tests PASS;
- historical walk-forward run PASS;
- provider/session behavior is production-governed;
- continuous live runtime and freshness semantics are proven;
- runtime identity, persistence/provenance and UI semantics are reviewed;
- a separate governance decision explicitly authorizes promotion.
