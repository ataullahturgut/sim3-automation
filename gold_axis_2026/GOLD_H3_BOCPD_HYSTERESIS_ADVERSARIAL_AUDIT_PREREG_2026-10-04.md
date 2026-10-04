# GOLD H3 — BOCPD Hysteresis Adversarial Audit Preregistration

**Date:** 2026-10-04
**Status:** robustness / falsification audit of the already-observed BOCPD V4 hysteresis result.
**Purpose:** determine whether the reported 2026 +6 net rescue is a knife-edge artifact or a persistent competence-state phenomenon.

## Fixed core

Canonical Handoff alarm, 2025 formation data, Beta-Bernoulli BOCPD class, maturity-safe updating, combined 126/191 baseline, and V4 chronology are inherited unchanged.

Central V4:
- expected run = 4 alarms
- entry P(rescue) >= 0.60
- entry P(theta>0.50) >= 0.80
- exit after 2 consecutive matured BROKEN acted alarms

No central parameter changes are made.

## Falsification tests

### A. Parameter-neighborhood sensitivity

Evaluate the full fixed neighborhood, without choosing a winner:
- expected run: {3,4,5,6,8,12}
- entry P(rescue): {0.55,0.60,0.65}
- entry P(theta>0.50): {0.75,0.80,0.85}
- exit broken streak: {1,2,3}

Report all 162 combinations:
- actions
- rescue
- broken
- net
- precision
- first trust entry
- assisted accuracy

Robustness summaries:
- fraction with net > 0
- fraction with net >= +4
- median net
- minimum / maximum net
- central-rule percentile within the neighborhood

This is sensitivity analysis only; no parameter is selected from 2026.

### B. Entry-location perturbation

Using the observed 2026 Handoff chronology:
- force persistent trust to start 3,2,1 alarms before the central V4 entry,
- at the central entry,
- and 1,2,3 alarms after it,
while keeping the 2-broken exit.

This tests whether +6 depends on one exact alarm date.

### C. Stationary competence null

Simulate 20,000 2026 Handoff outcome sequences under a stationary Bernoulli rescue probability equal to the 2025 Handoff formation rate (4/13), preserving the 2026 alarm and maturity calendar.
Run the central V4 state machine on each simulated sequence.

Report:
- P(net >= observed +6)
- P(accuracy gain >= observed)
- null net distribution quantiles.

### D. Chronology-permutation null

Permute the observed 28 2026 Handoff rescue/broken labels 20,000 times across the fixed alarm/maturity calendar.
Run the central V4 state machine.

Report P(net >= observed +6).

This asks whether ordering, rather than just the total 16/12 rescue mix, drives the result.

### E. Offline competence change-point diagnostic

On the observed 28 Handoff outcomes:
- consider split points with at least 4 alarms on each side;
- find the split maximizing the Bernoulli two-segment log-likelihood gain over one stationary rate;
- report pre/post rescue rates;
- use 20,000 label permutations to assess the maximum change-point gain.

This is descriptive only and cannot be used to alter V4.

### F. Calendar-block deletion

For the central V4 acted alarms:
- remove each acted calendar month in turn;
- recompute rescue/broken/net on the remaining acted set.

Report the worst leave-one-month-out net.

### G. Simple statistical support

For the central V4 acted outcomes:
- exact one-sided Binomial test against p=0.5;
- Jeffreys posterior P(theta>0.5);
- 95% equal-tail Beta interval.

## Interpretation

V4 remains post-hoc development evidence because hysteresis was designed after the V1 2026 chronology was inspected. This audit cannot convert it into independent OOS validation. Its purpose is to determine whether the +6 result is structurally robust enough to justify a frozen prospective challenger.
