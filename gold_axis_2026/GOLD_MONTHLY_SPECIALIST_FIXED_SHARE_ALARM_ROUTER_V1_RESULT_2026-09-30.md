# GOLD MONTHLY — Specialist Fixed-Share Alarm Router V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / PROMOTION CANDIDATE PASS  
**Selected algorithm:** **Specialist Hedge**, not Fixed-Share  
**Selected parameters:** eta=0.25, alpha=0, HIGH threshold=0.50

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_SPECIALIST_FIXED_SHARE_ALARM_ROUTER_V1_AUTHORITY_2026-09-30.md`
- authority commit: `001ca60737bd82853fed60972cafdec00ba96c2c`

Code:
- `gold_axis_2026/tools/gold_monthly_specialist_fixed_share_alarm_router_v1.py`
- code commit: `3a6986fd8bb8712301a64a585e977d0bca51358c`

Workflow:
- `.github/workflows/gold-monthly-specialist-fixed-share-alarm-router-v1.yml`
- workflow commit: `4038844097e6b6e1b881fbc495bff9f6a22ec4b2`

Execution:
- run: **36775933119**
- artifact: **11124892942**
- artifact digest: `sha256:06d8b70d61d0358978c46cc41078e57155763f1a0a56ad21ddef92b25e30f13e`
- scientific gate: **PASS**

## 2. Frozen search

Specialists:
- A/B/C/D/E/G/H/I1/I2/T1_WGC
- V2_TRANSITION
- always-awake NULL no-risk expert.

Tasks:
- HIGH primary
- HIGH+MEDIUM supporting.

Grid:
- eta = 0.25/0.50/1.00/2.00
- alpha = 0 for Hedge
- Fixed-Share alpha = 0.01/0.05/0.10/0.20
- HIGH decision tau = 0.25/0.35/0.45/0.50/0.60
- **100 preregistered candidates**
- **99/100** satisfy the preliminary >=90% DEV HIGH-retention eligibility.
- only `HEDGE_eta0.25_tau0.60` is ineligible.

Selection uses only DEV target months 2022-04..2024-12.
2025/2026 are not used for eta/alpha/tau selection.

## 3. Selected model

Winner:
- **HEDGE_eta0.25_tau0.50**
- eta=0.25
- alpha=0
- tau=0.50.

Important:
- the specialist-expert idea succeeds;
- **Fixed-Share redistribution itself is not selected**.
- The best Fixed-Share competitor with the same DEV decision counts is:
  - `FIXED_SHARE_eta0.25_alpha0.01_tau0.60`
  - 8 HIGH +2 MEDIUM +10 false
  - but HIGH-task Brier is worse: about **0.3170** vs selected Hedge **0.2987**.

Thus the data currently favor **specialist Hedge without sharing**.

## 4. DEV result — 2022-04..2024-12

### Raw ANY_VISIBLE

- events: **25**
- HIGH hits: **8**
- MEDIUM hits: **2**
- false calls: **15**
- HIGH recall: **100%**
- elevated recall: **100%**
- useful-call rate: **40.0%**
- false-call rate: **60.0%**

### Selected Specialist Hedge router

- events: **20**
- HIGH hits: **8**
- MEDIUM hits: **2**
- false calls: **10**
- HIGH recall: **100%**
- elevated recall: **100%**
- useful-call rate: **50.0%**
- false-call rate: **50.0%**

Comparison:
- HIGH lost: **0**
- MEDIUM lost: **0**
- false calls removed: **5/15 = 33.3%**
- useful-call rate: **40% -> 50%**.

This satisfies every preregistered promotion condition.

## 5. Exact DEV false calls removed

All five suppressed rows are NORMAL target months.

1. origin 2023-03 -> target 2023-04
   - T1_WGC only
   - p_HIGH ≈ **0.438**

2. origin 2023-11 -> target 2023-12
   - T1_WGC only
   - p_HIGH ≈ **0.269**

3. origin 2023-12 -> target 2024-01
   - T1_WGC only
   - p_HIGH ≈ **0.223**

4. origin 2024-01 -> target 2024-02
   - T1_WGC + V2_TRANSITION
   - p_HIGH ≈ **0.453**

5. origin 2024-04 -> target 2024-05
   - T1_WGC + V2_TRANSITION
   - p_HIGH ≈ **0.438**

No DEV HIGH or MEDIUM row is suppressed.

This is a stronger false-call result than the earlier simple reliability-gate experiments.

## 6. Why the architecture is behaving better

Sleeping specialists are updated only when awake.

Consequences:
- E is not punished for years in which it never fires;
- T1 accumulates loss from repeated false calls because it is frequently awake;
- V2 can maintain its own specialist history instead of globally modifying every other alarm;
- NULL provides the competing no-risk mass.

This avoids the stationary pooled-shrinkage failure in which sparse alarms were dragged toward an old global mean.

## 7. 2025 opened transport

Raw ANY_VISIBLE:
- 7 events
- 5 HIGH
- 1 MEDIUM
- 1 false
- HIGH recall **100%**
- useful-call rate **85.7%**.

Router:
- exactly the same 7 event months
- 5 HIGH
- 1 MEDIUM
- 1 false
- HIGH recall **100%**
- useful-call rate **85.7%**.

So the router does not damage the cleaner 2025 alarm set.

Examples correctly retained despite sparse/new history:
- H -> Feb25 HIGH
- B -> Mar25 HIGH
- E -> May25 MEDIUM
- A/V2 -> Sep25 HIGH
- H -> Oct25 HIGH
- E -> Nov25 HIGH.

This is a major improvement over prior 0.50 reliability gating, which had incorrectly suppressed several of these.

## 8. 2026 opened transport

Raw ANY_VISIBLE:
- 5 events
- 2 HIGH
- 1 MEDIUM
- 2 false
- HIGH recall **66.7%**
- elevated recall **75.0%**
- useful-call rate **60.0%**
- false rate 40.0%.

Selected router:
- **6 events**
- **3 HIGH**
- 1 MEDIUM
- same **2 false**
- HIGH recall **100%**
- elevated recall **100%**
- useful-call rate **66.7%**
- false rate **33.3%**.

The extra event is:

- origin **2026-05**
- only V2_TRANSITION specialist awake
- p_HIGH ≈ **0.731**
- target **2026-06 HIGH**
- no raw A/B/C/D/E/G/H/I1/I2/T1 alarm existed.

Thus the specialist router preserves V2's independent recent-risk value without globally promoting every historical V2 transition.

## 9. Combined opened 2025-2026

Raw ANY_VISIBLE:
- 12 events
- 7 HIGH
- 2 MEDIUM
- 3 false
- HIGH recall **87.5%**
- elevated recall **81.8%**
- useful-call rate **75.0%**
- false rate 25.0%.

Selected router:
- 13 events
- **8 HIGH**
- 2 MEDIUM
- same **3 false**
- HIGH recall **100%**
- elevated recall **90.9%**
- useful-call rate **76.9%**
- false rate **23.1%**.

So opened transport is directionally favorable:
- +1 HIGH
- +0 false.

Opened evidence is descriptive and does not select the model.

## 10. Sparse-expert protection works

Examples:

### E, origin 2025-04
Before E has any prior awake outcome:
- evidence tier = EMERGING
- p_HIGH ≈ **0.940**
- target May25 = MEDIUM
- router keeps the warning.

Previous pooled reliability methods had suppressed E here because it had insufficient history.

### G, origin 2026-07
Prior G history is still sparse:
- G remains EMERGING
- V2_TRANSITION also awake
- p_HIGH ≈ **0.973**
- target Aug26 = HIGH
- router keeps it.

The specialist design therefore behaves much better for rare but potentially critical experts.

## 11. Promotion gate

Pre-registered requirements and observed DEV:

1. HIGH recall >=90%
   - observed **100%**
   - PASS

2. raw-ANY HIGH-hit retention >=90%
   - observed **100%**
   - PASS

3. false-call reduction >=20%
   - observed **33.3%**
   - PASS

4. router useful-call rate > raw ANY
   - **50% vs 40%**
   - PASS

Overall:
- **PROMOTION CANDIDATE PASS**

This authorizes the router only as a candidate for the next frozen validation/audit stage; it is not yet a production rule.

## 12. Important qualification: Fixed-Share itself did not win

The literature-motivated architecture was useful, but the specific sharing mechanism was unnecessary in this sample.

Best result:
- Specialist Hedge
- alpha=0.

Interpretation:
- allowing specialists to sleep already solves much of the sparse-signal problem;
- explicit weight redistribution/revival does not add enough benefit yet;
- do not force Fixed-Share merely because it was the initial hypothesis.

## 13. Current structural conclusion

This is the first reliability/router experiment in the current sequence that simultaneously:

- preserves all DEV HIGH;
- preserves all DEV MEDIUM;
- removes a material number of false calls;
- does not suppress new E/H evidence in 2025;
- adds the independent 2026-05 V2 catch;
- introduces no new opened false calls.

This is substantially stronger than:
- pooled regime/V2 shrinkage;
- hard reliability gating;
- rolling/decay memory;
- universal V2 risk warning.

## 14. Next defensible step

Do not retune this router on 2025/2026.

Freeze:
- Specialist Hedge
- eta=0.25
- tau=0.50
- expert set including V2
- update rules exactly as V1.

The next stage should test **orthogonal false-call information**, especially the previously promising cross-model direction-consensus + low-dispersion suppressor, on top of the frozen router without changing the router itself.

Key question:

> Can consensus/dispersion remove additional router false calls while preserving the router's 100% DEV HIGH/MEDIUM coverage and the 2026 V2 incremental catch?

Until that stage passes, the router remains a promoted research candidate, not an operational production rule.
