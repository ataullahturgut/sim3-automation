# SESSION MODEL-01 — CLASSICAL CORE3 LOGISTIC — IDENTITY RECONCILIATION AUTHORITY

**Date:** 2026-10-07  
**Status:** **COMPLETE / IDENTITY_RECONCILED / NO_RERUN_REQUIRED**  
**Role:** first legacy near-term model family revalidated against the corrected V5 session targets.

## 1. Decision

The existing session artifact

`GOLD_SESSION_NOVA_A0_CORE3_RAW_REPLAY_V1_*`

is accepted as the authoritative **SESSION Model-01 Classical CORE3 Logistic** result.

A new duplicate fit is not required because the existing session replay already satisfies the corrected target/data/clock contract and uses the same classical CORE3 algorithmic identity.

The DAILY/H3 artifact at commit
`10849d00273d2dac1b539fba22891b45779466bf`
remains a separate DAILY/H3 benchmark and is not used as session evidence.

## 2. Identity audit

### Model identity — PASS

Existing session A0:
- StandardScaler
- LogisticRegression
- L2 penalty
- C = 1.0
- threshold = 0.5

This is the same classical logistic family intended for Model-01.

### Feature identity — PASS

Exact CORE3 feature block:
- gold_r1
- gold_r3
- gold_r5
- gold_r10
- gold_r21
- sigma20
- silver_r1
- silver_r5
- silver_r21
- silver_age_days
- platinum_r1
- platinum_r5
- platinum_r21
- platinum_age_days

No archived NOVA prediction or readiness feature panel is consumed as a model input.

### Source-ready clock rule — PASS

Because the intraday publication time of the Stak daily metal labels is not proven, every session uses only the latest common Gold/Silver/Platinum observation from a **strictly earlier America/New_York calendar date** than the session start.

Same-day daily metal observations are prohibited.

### Session target identity — PASS

Target raw authority:
`GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv`

Raw SHA256:
`8f1c00b34a95b7cef6a44c3c0bef59035fa9dde9cf6d241ba0b87fd146235308`

The V5 session targets were independently reconstructed from raw 15-minute XAU before fitting and the target reproduction gate passed.

The target is therefore **session start -> session end direction**, not
`sign(log(P[t+3]/P[t]))`.

### Chronology identity — PASS for the established session replay contract

Development replay:
- same-window causal training
- minimum 120 matured same-window outcomes
- five-row scoring blocks
- 2023–2024 scored development

2025 authority:
- model specification, features, clock, target and threshold frozen before 2025
- original five-row block phase preserved continuously through 2023 -> 2024 -> 2025
- no 2025 retuning
- 2026 unopened

**Important distinction:** this session authority is a **frozen-specification causal replay**, not the static-coefficient 31.12.2024 freeze used by the separate DAILY/H3 Model-01 benchmark. The two contracts must not be mixed.

## 3. 2023–2024 development results

| Partition / window | N | Accuracy | Balanced Acc. | UP recall | DOWN recall | Brier |
|---|---:|---:|---:|---:|---:|---:|
| Sobti Asia Afternoon | 358 | 47.77% | 47.91% | 39.56% | 56.25% | 0.2622 |
| Sobti Asia Morning | 358 | **54.19%** | **53.88%** | 57.14% | 50.62% | 0.2603 |
| Sobti Europe | 383 | 51.44% | 51.12% | 54.81% | 47.43% | 0.2655 |
| Sobti NY/London | 379 | 50.40% | 50.34% | 48.11% | 52.58% | 0.2659 |
| Sobti Late-US | 274 | 56.93% | 49.94% | **79.88%** | **20.00%** | 0.2466 |
| WGC Asia | 376 | 53.72% | 51.05% | 68.98% | 33.12% | 0.2551 |
| WGC Europe | 382 | 51.05% | 49.59% | 61.68% | 37.50% | 0.2578 |
| WGC US | 346 | 47.69% | 47.55% | 39.41% | 55.68% | 0.2697 |

Development conclusion:
- no robust universal session edge;
- Sobti Asia Morning is the least weak balanced development slice;
- Sobti Late-US nominal accuracy is misleading because DOWN recall collapses to 20%.

## 4. Frozen-specification 2025 causal transport

| Partition / window | N | Accuracy | Balanced Acc. | UP recall | DOWN recall | Brier |
|---|---:|---:|---:|---:|---:|---:|
| Sobti Asia Afternoon | 240 | **61.67%** | **61.58%** | 58.12% | **65.04%** | 0.2447 |
| Sobti Asia Morning | 239 | 50.63% | 50.56% | 56.20% | 44.92% | 0.2512 |
| Sobti Europe | 247 | 47.37% | 45.89% | 55.24% | 36.54% | 0.2616 |
| Sobti NY/London | 245 | 50.61% | 49.34% | 59.42% | 39.25% | 0.2552 |
| Sobti Late-US | 195 | 60.51% | 52.40% | **82.26%** | **22.54%** | 0.2384 |
| WGC Asia | 253 | 54.94% | 53.07% | 68.31% | 37.84% | 0.2481 |
| WGC Europe | 247 | 49.80% | 50.01% | 48.59% | 51.43% | 0.2607 |
| WGC US | 239 | 47.28% | 46.82% | 50.37% | 43.27% | 0.2587 |

2025 conclusion:
- A0/CORE3 transports strongly only in **Sobti Asia Afternoon**;
- Late-US again exhibits severe directional imbalance despite high nominal accuracy;
- the model is not a universal all-session champion;
- it remains a valid baseline and a window-specific candidate.

## 5. Binding Model-01 verdict

**SESSION Model-01 = COMPLETE.**

Verdict:
- algorithm identity: PASS
- CORE3 feature identity: PASS
- V5 session target identity: PASS
- source-ready daily-feature rule: PASS
- 2023–2024 causal development: PASS
- 2025 frozen-specification transport: PASS
- universal session promotion: **NO**
- window-specific evidence: **YES — strongest in Sobti Asia Afternoon transport**
- 2026: **UNOPENED / NOT A SELECTION SET**

## 6. Next model

The next authorized sequential legacy-family replay is:

**SESSION Model-02 — Shallow CART**

It must use the same corrected V5 session targets, source-ready feature cutoff, session chronology and class-balance reporting discipline. DAILY/H3 CART results, if any, may be historical comparators only.
