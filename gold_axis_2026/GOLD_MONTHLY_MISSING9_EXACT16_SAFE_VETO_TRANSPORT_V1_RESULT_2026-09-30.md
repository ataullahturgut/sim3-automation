# GOLD MONTHLY — Missing9 Frozen Transport + Exact16 SAFE-Veto Transport V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / EXACT16 TRANSPORT DECISION = HARMFUL  
**Binding conclusion:** the exact original 16-model cross-model SAFE-veto must **not** be placed on top of the frozen Specialist Hedge router. It preserves the two DEV false-call removals, but on opened transport it removes **0 false calls** and suppresses a genuine **2025-02 HIGH** alarm. The frozen Specialist Hedge router therefore remains the safer alarm layer.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_MISSING9_FROZEN_TRANSPORT_AND_EXACT16_VETO_V1_AUTHORITY_2026-09-30.md`
- authority commit: `9af53fe054bb25a1b1a2efb196da0e28c144019d`

Code:
- `gold_axis_2026/tools/gold_monthly_missing9_frozen_transport_v1.py`
- code commit: `044be46198f5faa5fe4a3c4ce8e4246412d20bbf`
- `gold_axis_2026/tools/gold_monthly_exact16_safe_veto_transport_v1.py`
- code commit: `e317a4bcdcd0f2ac133589df3097a7cdba0426ee`

Workflow:
- `.github/workflows/gold-monthly-missing9-exact16-safe-veto-v1.yml`
- workflow commit: `90f41aa569bfe2748bcbaedcf3fc00835d87317a`

Execution:
- workflow: **Gold Monthly Missing9 Exact16 Safe Veto V1**
- run: **36779063580**
- conclusion: **SUCCESS**
- exact16 artifact: **11128785588**
- exact16 artifact digest: `sha256:ac7cedf50793d7fe1945f54553efb9e1336962cb8adb298f32db8bd58246a007`

## 2. Missing-9 reconstruction

The original 16-model consensus pool required transport forecasts for nine models that had not previously been frozen through 2025-01..2026-07:

- BOOST_CATBOOST_ORDERED
- BOOST_RANDOM_FOREST_ANCHOR
- SVR_CURRENT8
- SVR_DAILY_SUMMARY12
- SVR_MIXED20
- SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB3_V1
- SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB6_V1
- SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB3_V1
- SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB6_V1

All six reconstruction jobs completed successfully.

Artifacts:
- boost: **11127052273**, `sha256:35e81b61145f856886b6170e327cc26ca031ad5d0f5f3b75e8471979f2d936b1`
- SVR: **11126323028**, `sha256:d2844b10eb8210be05292d8933b89a781b3d64472dc0b907bb6500ce164bbcbe`
- CNN_LSTM LB3: **11128106474**, `sha256:81b4ed10257aca1504e6a27ef9091c1eb8e58e63945a7648c78594aa9cb1ddb4`
- CNN_LSTM LB6: **11128006357**, `sha256:e95fec6b177a08a114f369014dfce0943f5f53efdbba6d4fc570462a7525192c`
- LSTM LB3: **11128136850**, `sha256:b5e0e68a84da9ef594afe15d5309604b2339400f9d96df9dbd0c052e11dab53e`
- LSTM LB6: **11128276122**, `sha256:28906c60d3e4b8e20457d6a6feb7dc55040fed231aa92a46d3f356f08c17755f`

The workflow's preregistered reproduction gates passed; the downstream exact16 job was therefore allowed to run.

## 3. Frozen exact-16 pool and veto rule

Competitive pool:
1. AOA_ELM
2. BOOST_CATBOOST_ORDERED
3. BOOST_RANDOM_FOREST_ANCHOR
4. ChHHO_ANFIS
5. DE_ABC_RBFNN
6. FULL7_ANN
7. LMC2_RBF_M32
8. PLS1_V1
9. REDUCED4_ANN
10. SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB3_V1
11. SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB6_V1
12. SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB3_V1
13. SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB6_V1
14. SVR_CURRENT8
15. SVR_DAILY_SUMMARY12
16. SVR_MIXED20

Frozen veto:
- ChHHO direction agreement >= **80%**
- cross-model dispersion <= expanding prior median
- no target actual in veto features
- no router retuning
- no threshold change
- 2025/2026 not used for selection.

## 4. DEV reproduction

Frozen Specialist Hedge router:
- events **20**
- HIGH **8**
- MEDIUM **2**
- false **10**
- HIGH recall **100%**
- useful-call rate **50.0%**

Exact16 overlay:
- events **18**
- HIGH **8**
- MEDIUM **2**
- false **8**
- HIGH recall **100%**
- useful-call rate **55.6%**

DEV removals:
- target 2022-12 — NORMAL
- target 2024-08 — NORMAL

Thus the prior DEV-safe behavior is reproduced exactly:
- HIGH removed **0**
- MEDIUM removed **0**
- false removed **2**.

## 5. Opened 2025 transport

Router:
- events **7**
- HIGH **5**
- MEDIUM **1**
- false **1**
- HIGH recall **100%**
- useful-call rate **85.7%**

Exact16 overlay:
- events **6**
- HIGH **4**
- MEDIUM **1**
- false **1**
- HIGH recall **80%**
- useful-call rate **83.3%**

Suppressed row:
- origin **2025-01**
- target **2025-02**
- active specialist **H**
- Specialist Hedge p_HIGH ≈ **0.7311**
- exact16 direction agreement **100%**
- dispersion **0.4408%**
- prior dispersion median **0.9515%**
- actual severity **HIGH**

Therefore the veto removes a genuine HIGH and removes **no** false call.

## 6. Opened 2026 Jan-Jul transport

Router and Exact16 overlay are identical:
- events **5**
- HIGH **2**
- MEDIUM **1**
- false **2**
- HIGH recall **100%**
- useful-call rate **60%**

Changes:
- false removed **0**
- HIGH removed **0**
- MEDIUM removed **0**

Critical 2026-06 V2-only HIGH is preserved.

## 7. Opened 2025 + 2026 Jan-Jul

Router:
- events **12**
- HIGH **7**
- MEDIUM **2**
- false **3**
- HIGH recall **100%**
- useful-call rate **75.0%**

Exact16 overlay:
- events **11**
- HIGH **6**
- MEDIUM **2**
- false **3**
- HIGH recall **85.7%**
- useful-call rate **72.7%**

Net effect:
- false removed: **0**
- HIGH removed: **1**
- MEDIUM removed: **0**

Transport interpretation:
- **EXACT16_TRANSPORT_HARMFUL**

## 8. August 2026 coverage boundary

The exact 16-model transport panel is complete through **2026-07 target**.  
For target **2026-08**, exact16 features are unavailable under the frozen reconstruction contract, so the system uses pass-through and preserves the frozen Specialist Hedge warning:
- origin 2026-07
- G + V2_TRANSITION
- p_HIGH ≈ **0.9734**
- target 2026-08 = HIGH.

No result is fabricated for the missing exact16 feature month.

## 9. Binding decision

Reject the Exact16 SAFE-veto as an operational overlay.

Do not:
- add it to the frozen Specialist Hedge router;
- change the 80% agreement threshold after seeing transport;
- retune dispersion limits;
- replace it with the prior seven-model shadow;
- use 2025/2026 outcomes to search another hard veto threshold.

Retain:
- Specialist Hedge router V1 as the current promoted alarm/reliability candidate;
- cross-model consensus and dispersion as **diagnostic/context features**, not a hard suppressor.

## 10. Consequence for the next research stage

The remaining project question is no longer primarily “can another veto remove more alarms?”

The next research question is:

> When the frozen Specialist Hedge router issues a HIGH-risk warning, what origin-safe action—KEEP, SWITCH, BLEND, or LOW-CONFIDENCE/ABSTAIN—has evidence of improving the main ChHHO forecast?

That question must condition on the already-frozen market-state context rather than treating all alarm months as exchangeable:
- soft R0/R1/R2 posterior
- BELIRSIZ/OOD
- STABLE/TRANSITION
- NORMAL/EXTREME/DEFER
- regime age
- Specialist Hedge score and active experts
- cross-model consensus/dispersion as context only.

No action rule is authorized by this result.
