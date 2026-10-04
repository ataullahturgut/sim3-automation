# GOLD H3 — RULEFLOW V3-TG TOPOLOGY DIAGNOSTIC

**Date:** 2026-10-04
**Status:** POST-Q2Q3 DIAGNOSTIC — NOT VALIDATION

## Binding successor tested

Keep every frozen RuleFlow V2 condition. Add one veto:

- 60-origin Gold-Nasdaq correlation > 0
- 60-origin Gold-VIX correlation < 0
- at least one of those two correlations has two-sided Pearson p < 0.05
- then VETO the RuleFlow FLIP and KEEP V5.

The veto is one-sided: pro-risk topology does not create an opposite trade.

## Main action result

| Rule | Actions | Rescue | Broken | Net | Precision | Rescue retention | Broken suppression |
|---|---:|---:|---:|---:|---:|---:|---:|
| RuleFlow V2 | 10 | 6 | 4 | +2 | 60.0% | — | — |
| RuleFlow V3-TG | 6 | 6 | 0 | +6 | 100.0% | 100.0% | 100.0% |

Diagnostic delta: net improves from +2 to +6 because all 6 historical rescues survive while all 4 Q2-Q3 broken actions are vetoed.

## Period split

| Period | Hotspots | V2 actions | V2 R/B/net | V3 actions | V3 R/B/net |
|---|---:|---:|---:|---:|---:|
| 2025 | 7 | 5 | 5/0/+5 | 5 | 5/0/+5 |
| 2026Q1 | 3 | 1 | 1/0/+1 | 1 | 1/0/+1 |
| 2026Q2Q3 | 7 | 4 | 0/4/-4 | 0 | 0/0/+0 |

## Why strength matters

- STRONG_PRO_RISK hotspots: 2/8 reversal = 25.0%
- All other hotspots: 7/9 reversal = 77.8%
- Fisher one-sided p = 0.04447

Among V2 actions:
- STRONG_PRO_RISK: 0 rescue / 4 broken
- Other topology: 6 rescue / 0 broken
- Fisher one-sided p = 0.00476

These p-values are descriptive only because the topology hypothesis was discovered after seeing the Q2-Q3 failures.

## Sensitivity: the first 20d+60d hard-confirmation idea

| Variant | Actions | Rescue | Broken | Net | Precision |
|---|---:|---:|---:|---:|---:|
| Hard SAFE confirmation at both 20d and 60d | 2 | 2 | 0 | +2 | 100.0% |
| 60d SAFE sign-only | 4 | 4 | 0 | +4 | 100.0% |
| Binding V3 strong-pro-risk veto | 6 | 6 | 0 | +6 | 100.0% |

The hard 20d+60d confirmation is rejected as too restrictive: it suppresses valid rescue episodes during topology transition.

## Action-level topology

| Date | V2 outcome | NDX r60 | VIX r60 | min p60 | Topology | V3 |
|---|---|---:|---:|---:|---|---|
| 2025-05-02 | RESCUE | +0.113 | -0.186 | 0.1547 | WEAK_PRO_RISK | KEEP FLIP |
| 2025-05-30 | RESCUE | -0.063 | +0.049 | 0.6303 | WEAK_SAFE_HAVEN | KEEP FLIP |
| 2025-06-04 | RESCUE | -0.072 | +0.054 | 0.5826 | WEAK_SAFE_HAVEN | KEEP FLIP |
| 2025-07-29 | RESCUE | -0.525 | +0.450 | 0.0000 | STRONG_SAFE_HAVEN | KEEP FLIP |
| 2025-07-30 | RESCUE | -0.514 | +0.461 | 0.0000 | STRONG_SAFE_HAVEN | KEEP FLIP |
| 2026-02-11 | RESCUE | +0.016 | -0.032 | 0.8060 | WEAK_PRO_RISK | KEEP FLIP |
| 2026-06-17 | BROKEN | +0.465 | -0.458 | 0.0002 | STRONG_PRO_RISK | VETO |
| 2026-06-25 | BROKEN | +0.373 | -0.332 | 0.0033 | STRONG_PRO_RISK | VETO |
| 2026-07-29 | BROKEN | +0.206 | -0.308 | 0.0168 | STRONG_PRO_RISK | VETO |
| 2026-08-04 | BROKEN | +0.196 | -0.324 | 0.0116 | STRONG_PRO_RISK | VETO |

## Scientific decision

RuleFlow V2 remains closed. RuleFlow V3-TG is a mechanistically stronger successor candidate, but the 2025/Q1/Q2-Q3 replay is consumed diagnostic evidence, not independent validation.

The V3 topology rule is frozen here for genuinely unseen origins from the clean prospective period beginning 2026-10-05. No threshold or sign change is allowed without opening a new challenger identity.
