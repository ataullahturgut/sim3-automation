# OAR-CRED-H3 V2 — OPTIONS AGAINST-AND-RISING WITH SHADOW CREDIBILITY

**Date:** 2026-10-04  
**Identity:** `OAR_CRED_H3_V2`  
**Branch:** `gold-h3-oar-cred-v2-20261004`  
**Status:** **PREREGISTERED BEFORE 2026 OPENING**

## 1. Frozen base specialist

OAR-RTE V1 development selected the strongest aggregate mechanism at q=0.60:
- 34 candidates
- 22 rescues
- 12 broken
- net +10
- rescue precision 64.71%

Block net rescue:
- 2024 H1: +2
- 2024 H2: +2
- 2025 H1: +8
- 2025 H2: -2

The only remaining instability is local degradation in 2025 H2.

No threshold is searched in V2.

Base OAR proposal is frozen:

`p_rte >= 0.60`  
AND `p_inst >= 0.50`  
AND `signed_opt_pressure > 0`  
AND `signed_d_opt_pressure > 0`.

## 2. Continuous shadow credibility

Every base OAR proposal generates a shadow utility after its H3 target matures:
- +1 if the proposed flip would rescue V5;
- -1 if the proposed flip would break a correct V5 call.

At each origin:
- consider all earlier OAR proposals with `target_end_date_h3 <= current feature_cutoff_date`;
- inspect the most recent **3 matured OAR shadow outcomes**;
- if fewer than 3 exist, OAR is permitted;
- once 3 exist, OAR is permitted only when last-3 net utility >= +1 (at least 2/3 successful).

Vetoed OAR proposals continue to generate shadow outcomes after maturity, permitting recovery without taking the flip.

The memory is continuous across calendar boundaries; it is not reset at half-years.

## 3. Development audit

Evaluate the frozen V2 rule on:
- 2024 H1
- 2024 H2
- 2025 H1
- 2025 H2

No parameter is selected from these block results.

Pre-2026 robustness PASS requires:
- total acted candidates >=10
- aggregate net rescue >= +8
- aggregate rescue precision >=0.65
- at least 3 of 4 blocks have net rescue >=0
- no block net rescue < -1
- pooled assisted accuracy > pooled V5 accuracy

Failure => `NO_ROBUST_OAR_CRED_V2`; 2026 remains unopened.

## 4. 2026 final holdout

Only after robustness PASS.

The exact same continuous rule is applied sequentially to 2026:
- credibility memory can include matured late-2025 OAR shadow proposals;
- during 2026 it updates only after each proposal's target matures;
- no threshold, memory length or permission rule changes.

Report:
- proposals vs acted candidates
- rescue / broken / net
- precision
- number of credibility permission transitions
- eligible accuracy improvement
- whole-clean-2026 accuracy
- OPAL-no-candidate missed reversal coverage.

## 5. Governance

2024-2025 is development.  
2026 is the first independent OAR-CRED evaluation.  
No 2026 outcome may alter the rule.
