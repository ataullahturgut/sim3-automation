# GOLD H3 — EXCEPTION-CHANNEL LAB V1

**Date:** 2026-10-04  
**Branch:** `gold-h3-exception-channel-lab-v1-20261004`  
**Binding champion:** HELIOS V5-DCE  
**Surviving prospective exception:** SAGE-H3 V2 / OCS exception-only  
**Research principle:** improve by adding sparse, orthogonal, mechanism-specific exceptions; do not replace V5 with another global classifier.

## 1. Design doctrine

Every new channel must satisfy all:

1. target a physically distinct mechanism;
2. produce a sparse candidate set;
3. fail closed to V5 when evidence/source integrity is insufficient;
4. be judged by rescue / broken / net rescue and false-positive burden, not generic accuracy alone;
5. remain separate from the acceptance layer;
6. not reuse 2026 as a clean holdout;
7. receive a prospective freeze before any clean claim.

The expected architecture is a **mixture of rare mechanisms**:

`V5 baseline + exception_1 + exception_2 + ...`

rather than:

`one larger reversal classifier`.

## 2. Channel A — TPC-H3: Temporal Propagation Concurrence

### Hypothesis
OCS currently requires internal flow breakdown and external lead-lag stress to coexist at the origin.

A stronger mechanism is temporal propagation:

`external repricing stress -> internal Gold/Silver flow deterioration -> reversal exception`.

The aim is not to raise a static score, but to verify a plausible causal ordering.

### Inputs
Existing hourly / multiscale features:
- LLRS external pressure and incremental lead-lag stress;
- GC flow 3h / 6h / 12h;
- GC opposite-volume share 3h / 6h / 12h;
- GC/SI flow gap;
- late rejection;
- efficiency / absorption.

### Frozen first representation
Use multiscale ordering proxies, not outcome-fitted thresholds:
- external opposition must be active;
- 3h internal opposition must be stronger than 12h opposition;
- GC 3h flow deterioration must be stronger than 12h state;
- recent rejection must exceed the slower rejection state.

Primary role:
**precision-preserving successor to OCS**.

### Why distinct
OCS asks whether two channels agree.
TPC asks whether the concurrence is accompanied by the expected **temporal propagation pattern**.

Priority: **1**.

---

## 3. Channel B — DCX-H3: Directional-Change / Overshoot Exhaustion Exception

### Hypothesis
Calendar-time trend variables may miss intrinsic-time exhaustion.

Represent the pre-origin Gold path with directional-change events:
- current directional-change threshold;
- current overshoot length;
- overshoot / prior-event ratio;
- number of same-direction extensions;
- counter-move depth;
- event-clock acceleration.

Candidate reversal occurs only when an unusually extended overshoot is followed by an origin-available rejection / efficiency collapse.

### Inputs
Gold hourly price path only.

### Role
Purely endogenous exception channel, independent of OCS cross-asset concurrence.

### Why distinct
TRES modeled future H1/H2/H3 path states.
DCX uses **only the pre-origin event clock**.

Priority: **2**.

---

## 4. Channel C — PMBF-H3: Precious-Metals Breadth Fracture

### Hypothesis
A Gold trend unsupported by the precious-metals complex may be less durable than a broad complex move.

Construct origin-safe cross-sectional state from:
- Gold
- Silver
- Platinum
- Palladium

Potential mechanism variables:
- fraction of metals agreeing with Gold momentum;
- Gold-vs-complex return residual;
- rolling Gold / complex beta residual;
- breadth deterioration;
- dispersion shock;
- lead-lag disagreement.

Exception candidate:
strong Gold continuation call + breadth fracture + recent relative-value reversion pressure.

### Role
Cross-sectional relative-value exception.

### Why distinct
IFBC has Gold/Silver intraday flow.
PMBF tests a **four-metal breadth / relative-value** mechanism.

Priority: **3**, conditional on source coverage.

---

## 5. Channel D — OFDX-H3: Options/Futures Disagreement Exception

### Hypothesis
Generic options-flow scores were insufficiently selective, but a rare disagreement state may contain information:

- option activity strongly opposes momentum;
- options activity is unusual relative to its own history;
- futures participation does not confirm the trend or is decelerating.

Use official CME Gold CALL/PUT volume and, where origin-safe coverage exists, OI.
Do not rename this CVOL skew.

Possible state:
`option opposition × futures non-confirmation × activity shock`.

### Role
Informed-positioning / derivatives disagreement exception.

### Why distinct
Prior OAR / options-flow tried scalar reversal scores.
OFDX is a **conjunction of disagreement mechanisms**, analogous to the successful OCS philosophy.

Priority: **4**.

---

## 6. Channel E — OSRC-H3: One-Sided Risk-Control Acceptance Layer

This is not a new market signal.

It is a governance / acceptance layer over independently generated exception proposals.

### Objective
Maximize accepted exception coverage subject to a false-positive / precision constraint.

Possible methods:
- one-sided prediction;
- conformal selective risk control;
- beta-binomial / confidence-bound acceptance;
- prequential calibration.

The acceptance layer must never invent a candidate.
It only decides whether a candidate from TCC / DCX / PMBF / OFDX is trustworthy enough to act.

### Role
False-positive control for the union of rare exception channels.

Priority: **after at least two independent channels exist**.

---

## 7. Channel F — Drift Sentinel

Not a direction model.

Monitor unlabeled distribution shift in each exception mechanism:
- feature support;
- conditional entropy;
- covariance / dependence change;
- source regime / liquidity shift.

On strong OOD / drift:
- suppress the exception;
- KEEP V5;
- continue shadow logging.

This reuses changepoint ideas only as a **safety veto**, not as a reversal predictor.

Priority: **parallel safety layer**.

## 8. Test order

1. TPC-H3
2. DCX-H3
3. PMBF-H3 coverage audit + model
4. OFDX-H3
5. OSRC-H3 over surviving independent channels
6. Drift Sentinel attached to promoted shadow exceptions

## 9. Binding success metric

For each exception channel:

- candidate count;
- rescue;
- broken;
- net rescue;
- precision;
- candidate rate;
- half-year stability;
- overlap with OCS;
- **marginal rescues not already found by OCS**;
- OPAL-no-candidate rescue count;
- same-origin full-direction effect on V5.

A channel with good precision but zero marginal rescue over OCS is redundant, not an improvement.

## 10. Governance

Historical 2025–2026 data are development/stress-test only.

No new channel may be described as a clean 2026 improvement.

HELIOS V5-DCE remains binding.
SAGE-H3 V2 remains prospective shadow-only.
