# GOLD H3 — BOCPD Hysteresis Adversarial Audit

**Status:** ROBUSTNESS_AUDIT_COMPLETE

## Central V4 replication

- actions **10**, rescue/broken **8/2**, net **+6**, precision **80.0%**
- entry: **2026-05-27**
- assisted accuracy: **132/191 = 69.11%**

## Parameter-neighborhood attack

- combinations: **162**
- net > 0: **92.6%**
- net >= +4: **61.1%**
- median net: **+5.0**
- min / max net: **-2 / +6**
- central +6 percentile (fraction neighborhood <= +6): **100.0%**

### Net distribution

| Net | Count |
|---:|---:|
| -2 | 3 |
| +0 | 9 |
| +1 | 21 |
| +2 | 9 |
| +3 | 21 |
| +4 | 6 |
| +5 | 39 |
| +6 | 54 |

## Entry-date perturbation

| Shift (alarms) | Entry date | Actions | Rescue | Broken | Net | Precision |
|---:|---|---:|---:|---:|---:|---:|
| -3 | 2026-04-30 | 13 | 11 | 2 | +9 | 84.6% |
| -2 | 2026-05-18 | 12 | 10 | 2 | +8 | 83.3% |
| -1 | 2026-05-21 | 11 | 9 | 2 | +7 | 81.8% |
| +0 | 2026-05-27 | 10 | 8 | 2 | +6 | 80.0% |
| +1 | 2026-06-01 | 9 | 7 | 2 | +5 | 77.8% |
| +2 | 2026-06-08 | 8 | 7 | 1 | +6 | 87.5% |
| +3 | 2026-06-29 | 7 | 6 | 1 | +5 | 85.7% |

## Null attacks

- stationary 2025-competence null P(net >= +6): **0.0004**
- chronology-permutation P(net >= +6): **0.0284**

## Offline change-point diagnostic

- best split: between **2026-04-28** and **2026-04-30**
- pre rescue rate: **33.3%**
- post rescue rate: **84.6%**
- max log-likelihood gain: **3.993**
- permutation P(max gain >= observed): **0.0544**

## Calendar-block deletion

| Deleted month | Remaining actions | Rescue | Broken | Net |
|---|---:|---:|---:|---:|
| 2026-05 | 9 | 7 | 2 | +5 |
| 2026-06 | 7 | 6 | 1 | +5 |
| 2026-07 | 8 | 7 | 1 | +6 |
| 2026-09 | 6 | 4 | 2 | +2 |

Worst leave-one-month-out net: **+2**

## Statistical support for central acted set

- one-sided exact Binomial p vs 50%: **0.0547**
- Jeffreys posterior P(theta>0.5): **0.9740**
- Jeffreys 95% interval: **[49.7%, 95.6%]**

## Governance

This audit does not promote V4 to independent validation. V4 remains post-hoc development evidence. The purpose is falsification: assess whether the observed competence-state shift survives broad perturbations and null comparisons.
