# GOLD MONTHLY — Contextual HIGH-Alarm Rescueability Analysis V1 Result

**Date:** 2026-10-01  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / ANALYSIS ONLY / NO SWITCH AUTHORIZED

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CONTEXTUAL_HIGH_ALARM_RESCUEABILITY_V1_AUTHORITY_2026-10-01.md`
- authority commit: `c9eb9f06eb683591edcc1211fec12850ebaa67e4`

Code:
- `gold_axis_2026/tools/gold_monthly_contextual_high_alarm_rescueability_v1.py`
- code commit: `3e1f612ffb2adfbd97f591885435d30ab5a02f13`

Workflow:
- `.github/workflows/gold-monthly-contextual-high-alarm-rescueability-v1.yml`
- workflow commit: `783e39e0c28df250225faf43e1926e00cbdee516`

Execution:
- workflow: **Gold Monthly Contextual High Alarm Rescueability V1**
- run: **36790524882**
- job: **110142094485**
- conclusion: **SUCCESS**
- artifact: **11132141035**
- artifact digest: `sha256:6788f6bc1a1992570dc43ee019403e2765669cc749a6d2686613e500fa6d51e4`
- scientific gate: **PASS**

## 2. Main finding

There is substantial ex-post rescue headroom, but warning months are heterogeneous.

A frozen Specialist Hedge warning can correspond to:
- a false alarm where ChHHO should simply be kept;
- a broadly rescueable ChHHO miss;
- a narrow/specialist rescue opportunity;
- a shared-hard month where changing model makes the forecast worse.

Therefore:
**HIGH must not map directly to one fallback model.**

## 3. DEV anatomy — 2022-04..2024-12

Frozen Specialist Hedge warning months:
- warnings: **20**
- realized HIGH/MEDIUM: **10**
- realized NORMAL false warnings: **10**

Among the 10 realized elevated-error warning months:
- **BROAD_MATERIAL_RESCUE: 3**
- **BROAD_RESCUE: 2**
- **NARROW_MATERIAL_RESCUE: 1**
- **SHARED_HARD_OR_SHALLOW: 4**

Best fixed challenger if hindsight restricts switching only to the realized elevated warning months:
- **LMC2_RBF_M32**
- gain versus ChHHO: **+101.76 USD**
- wins: **8/10**

But this is not operationally available because the system does not know ex ante which warnings will be false.

On **all 20 warning months**, including false warnings:
- best fixed challenger is still **LMC2_RBF_M32**
- ChHHO warning-month ΣAE: **1127.89 USD**
- LMC2 warning-month ΣAE: **1144.00 USD**
- gain: **-16.11 USD**

So even the best fixed DEV fallback is worse than simply KEEPING ChHHO whenever the router warns.

This is the central negative result against a rule of the form:
> HIGH -> always switch to model X.

### DEV oracle ceiling — diagnostic only

On the same 20 warning months:
- best alternative every warning hindsight gain: **445.76 USD**
- KEEP-or-best-alternative hindsight gain: **469.73 USD**

There is therefore large theoretical rescue headroom, but it requires a selector that can distinguish warning type before the target month.

## 4. Opened 2025..2026-07 descriptive transport

Exact 16-model coverage:
- **2025-01..2026-07**
- 2026-08 full-16 rescue comparison is unavailable under the frozen transport contract and is not imputed.

Router warning months in this coverage:
- warnings: **12**
- realized HIGH/MEDIUM: **9**
- false warnings: **3**

Among the 9 elevated warnings:
- **BROAD_MATERIAL_RESCUE: 5**
- **BROAD_RESCUE: 2**
- **NARROW_MATERIAL_RESCUE: 1**
- **SHARED_HARD_OR_SHALLOW: 1**

Best fixed challenger on realized elevated warning months:
- **SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB6_V1**
- gain: **+440.84 USD**
- wins: **8/9**

On all 12 opened warning months:
- same CNN-LSTM LB6 has retrospective gain **+302.14 USD**
- wins **8/12**

This is strong descriptive evidence of recent complementarity, but it is **not selection authority** because 2025/2026 is already opened.

Opened oracle:
- best alternative every warning hindsight gain: **893.07 USD**
- KEEP-or-best-alternative hindsight gain: **1014.99 USD**

## 5. Critical cases

| Target | Severity | Origin-known context | ChHHO AE | Best alternative | Best alt AE | Alternatives beating ChHHO | Pattern |
|---|---|---|---:|---|---:|---:|---|
| **2025-02** | HIGH | R2 / NORMAL | 114.26 | LSTM LB6 | 65.17 | **14/15** | BROAD_MATERIAL_RESCUE |
| **2025-09** | HIGH | BELIRSIZ / TRANSITION | 288.42 | CNN-LSTM LB6 | 158.79 | **13/15** | BROAD_MATERIAL_RESCUE |
| **2026-01** | HIGH | R2 / NORMAL | 458.50 | CNN-LSTM LB6 | 336.22 | **13/15** | BROAD_RESCUE |
| **2026-03** | MEDIUM | R2 / EXTREME / OOD | 145.62 | SVR MIXED20 | 267.53 | **0/15** | SHARED_HARD_OR_SHALLOW |
| **2026-06** | HIGH | R2 / TRANSITION | 362.17 | LSTM LB6 | 252.61 | **9/15** | BROAD_RESCUE |

The 2026-03 row is especially important:
- the alarm correctly warned of elevated error;
- nevertheless **every alternative model was worse than ChHHO**;
- this is a genuine example where the correct post-alarm action would retrospectively have been **KEEP MAIN**, not SWITCH.

## 6. What regime information does and does not solve

Regime context is informative, but not deterministic.

Opened elevated warnings contain:
- R2 / NORMAL with broad material, broad, and narrow rescue behavior;
- R2 / EXTREME with a shared-hard case;
- R2 / TRANSITION with broad but shallower rescue;
- BELIRSIZ / TRANSITION with broad material rescue.

Therefore a rule such as:
> R2_TRANSITION -> switch  
or
> R2_EXTREME -> keep

is not authorized from these samples.

The more defensible role of regime is as a **context variable** inside a later rescueability model.

## 7. Why Exact16 direction-consensus veto failed conceptually

2025-02:
- direction agreement: **100%**
- dispersion was low enough for the prior SAFE-veto to suppress the warning
- actual severity: **HIGH**
- **14/15** alternatives nevertheless beat ChHHO
- the month is BROAD_MATERIAL_RESCUE.

This demonstrates that:
**direction agreement + low dispersion does not imply ChHHO itself is the correct point estimate.**

Models can agree on direction while differing materially in level.

Therefore later rescue analysis should use richer ensemble geometry:
- relative level position of ChHHO inside the forecast distribution;
- distance from ensemble median/IQR;
- challenger-specific relative-loss history;
- regime / transition / OOD context;
rather than another direction-only hard veto.

## 8. Binding decision

Do not:
- map HIGH directly to a fixed fallback;
- select CNN-LSTM LB6 from opened 2025/2026 as a production fallback;
- use the descriptive rescue taxonomy as thresholds;
- convert a regime cell directly into SWITCH/KEEP;
- revive Exact16 hard veto.

Retain:
- ChHHO as main forecast;
- Specialist Hedge as frozen risk router;
- full market-state stack as context;
- exact16 ensemble geometry as context only.

## 9. Next scientifically defensible question

The next research target is not gold price itself.

It is relative rescue gain:

`gain(j,t) = |error_ChHHO,t| - |error_model_j,t|`

The next stage, if opened, should ask whether origin-known alarm + regime + ensemble-geometry information can predict:
- KEEP MAIN;
- one or more positive-gain challenger specialists;
- BLEND candidate;
- or ABSTAIN / low-confidence.

No price action is authorized by this analysis.
