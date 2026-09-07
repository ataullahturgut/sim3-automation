# GOLD CONTROL — MARKET SHOCK CHALLENGER V1

**Status:** `CHANGE_CONTROL / RESEARCH CHALLENGER / NOT_PRODUCTION_AUTHORITY`  
**Branch:** `gold-control-market-shock-challenger-v1`  
**Parent state:** `gold-control-live-frequency-v145 @ d1cbfe014a85df884380662e0d747e611862921c`  
**Purpose:** Detect an unusual/abrupt gold-market move from the market price process itself (the user's requested B objective), without using any monthly H=1 forecast as an anchor.

## 1. Governance isolation

This challenger does not mutate or replace `EMERGENCY_LEVEL` / `EMERGENCY_REVERSAL` V1.46. It creates no production runtime identity, no automatic action, no model/decision authority row and no production Neon write. It is historical-research evidence only until separately reviewed and promoted.

Binding locks remain: `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, no hindsight threshold tuning, no silent provider substitution, no action mapping, and no historical evidence relabelled as prospective.

## 2. Research basis and design choices

The pre-registered design follows high-frequency jump/anomaly literature:

1. **5-minute primary sampling.** Gold-specific intraday studies commonly use 5-minute returns to reduce microstructure noise; recent gold jump work uses Lee–Mykland as a primary detector and alternative jump methods as robustness checks across 1/3/5/10-minute sampling and 95/99/99.9% thresholds.
2. **Jump-robust local volatility.** Lee–Mykland standardizes the tested return by a preceding-window bipower-variation scale so the current tested return is excluded from its own volatility denominator.
3. **Intraday periodicity adjustment.** Boudt–Croux–Laurent show that ignoring periodic volatility can create spurious jump detections; a robust periodicity factor is therefore estimated from prior data only.
4. **Tail method robustness.** Extreme Value Theory / Peaks-Over-Threshold is used as a distinct tail model on volatility-normalized returns.
5. **Non-instantaneous fast move coverage.** A 30-minute standardized fast-move tail detector covers unusually fast, large moves that need not be one-bar jumps.
6. **Streaming drift discipline.** Parameters are re-estimated only at pre-defined calendar boundaries from data strictly preceding the scored segment; metrics are reported by segment rather than pooling incompatible score distributions.

The 2025 gold-specific study is used only as an external scale/sanity reference, not as a calibration target for Twelve Data spot XAU/USD. It reports intraday gold-futures jumps as rare (~0.43% probability) and average detected jump magnitudes around +1.59% / -1.78%. Different instrument, venue and sample mean these values cannot be asserted as Twelve spot truth.

## 3. Frozen candidate definitions

### C1 — `LM_JUMP_5M`

- input: Twelve Data `XAU/USD`, 5-minute close;
- return: log close-to-close return;
- discontinuous session gaps: return is not scored if the preceding timestamp gap exceeds 10 minutes; this avoids manufacturing a weekend/session-boundary return without pretending that the exact Twelve session calendar is solved;
- local scale: preceding `K=270` valid 5-minute returns using bipower products, excluding the tested return;
- intraday periodicity factor: robust WSD-style factor by observed UTC weekday/5-minute slot, estimated from strictly prior training data and normalized to unit mean-square;
- main significance: `99.9%`; `95%` and `99%` are sensitivity outputs only;
- direction: sign of tested 5-minute return.

### C2 — `EVT_JUMP_5M`

- score: absolute 5-minute return divided by the same causal local scale and prior-data periodicity factor;
- POT threshold: prior-data 97.5th percentile;
- excess distribution: Generalized Pareto, location fixed at zero;
- main unconditional tail probability: `p <= 0.001`;
- no threshold is chosen by looking at 2026 outcomes.

### C3 — `EVT_FAST_MOVE_30M`

- move: absolute 30-minute log price change across six contiguous 5-minute bars;
- normalization: square-root-six times the causal 5-minute local scale and the contemporaneous prior-data periodicity factor;
- POT/GPD setup: same 97.5% tail threshold and `p <= 0.001` rule, fitted from strictly prior data;
- purpose: detect fast non-instantaneous events, not only one-bar jumps.

### Consensus challenger — `MARKET_SHOCK_CONSENSUS_V1`

A market-shock episode starts when at least **2 of 3** frozen candidates signal on the same 5-minute bar. This 2-of-3 rule is pre-registered and may not be changed after viewing the holdout results. Direction is the sign of the 30-minute move when C3 is active; otherwise the sign of the 5-minute return.

This consensus is a research classification only, not a BUY/SELL/HOLD instruction.

## 4. Historical validation protocol

Provider-history availability is checked through Twelve Data `/earliest_timestamp`. Raw market values are processed in-memory only and are not committed, logged or persisted to Neon.

Walk-forward segments:

- warm-up/development history begins at provider availability;
- `2024` score parameters use only data before `2024-01-01`;
- `2025` score parameters use only data before `2025-01-01`;
- `2026` completed-history holdout uses only parameters estimated before `2026-01-01` and is evaluated only through `2026-08-31` to avoid tuning on the still-open September context.

No random split is permitted.

## 5. Validation outputs

For each segment and detector:

- scored bars and coverage;
- alert bars and independent alert episodes;
- empirical alert rate;
- median/95th-percentile absolute 5-minute and 30-minute moves on alert vs non-alert bars;
- overlap/agreement matrix among C1/C2/C3;
- consensus episode count, duration, direction and magnitude summaries;
- sensitivity only at 95/99/99.9% for Lee–Mykland;
- no `FALSE_POSITIVE_RATE` claim from unlabeled history.

### Synthetic-injection power audit

Because real history does not contain an authoritative complete label set for all true/false gold shocks, an additional controlled audit injects permanent price-level jumps into real historical volatility contexts. The tested jump sizes are frozen before execution: `0.25%, 0.50%, 0.75%, 1.00%, 1.50%, 2.00%`, both signs. Injection locations are sampled deterministically from eligible non-gap holdout bars with a fixed seed. Detection power is reported by size/sign/segment. Null sampled bars provide an empirical no-injection alert rate, but this is test calibration evidence, not a claim about economic false positives.

## 6. Quantitative research acceptance gates — frozen before holdout review

These gates are intentionally conservative and are not a claim that the external gold-futures rates are identical to Twelve spot XAU/USD.

1. `2.00%` injected permanent jumps: consensus detection power must be **>= 95% in every scored holdout segment**.
2. `1.50%` injected permanent jumps: consensus detection power must be **>= 80% in every scored holdout segment**.
3. Synthetic detection power should be non-decreasing with jump magnitude, allowing at most a **2 percentage-point Monte-Carlo tolerance** between adjacent tested sizes.
4. Historical consensus bar rate must remain **< 1.0% in every holdout segment**; this is a broad anti-saturation gate, not a target rate.
5. On deterministic no-injection sampled bars, consensus alert rate must remain **< 1.0% in every holdout segment**. This is a calibration diagnostic, not a real-history false-positive rate.
6. Consensus alert rate must be lower than the median alert rate of the three constituent main detectors in each segment; otherwise the 2-of-3 layer is not providing meaningful selectivity.
7. Real-history `FALSE_POSITIVE_RATE` remains `NOT_PROVEN` unless an independent authoritative event-label contract is later issued.

Failure of any numeric gate means `REJECT_OR_REVISE_CHALLENGER_V1`; the same V1 thresholds or vote rule may not be adjusted post hoc to manufacture a pass. Any revised candidate must receive a new challenger identity and a fresh pre-registration.

## 7. Promotion gates

Production promotion is `BLOCKED` unless all are satisfied:

1. historical fetch and point-in-time segmentation complete;
2. all Section 6 quantitative research acceptance gates pass;
3. yearly/segment behavior is stable enough to survive concept-drift review;
4. no monthly H=1 forecast reference is used by the challenger;
5. exact implementation tests pass;
6. code/data provenance and provider identity are explicit;
7. exact provider/session-calendar handling is separately governed for production streaming;
8. a separate governance decision explicitly approves a new runtime identity.

If these gates fail, the outcome is `REJECT_OR_REVISE_CHALLENGER`; thresholds are not retroactively tuned under the same identity.