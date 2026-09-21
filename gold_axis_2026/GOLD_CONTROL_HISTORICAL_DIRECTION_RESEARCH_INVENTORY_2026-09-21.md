# GOLD CONTROL — HISTORICAL DIRECTION / SHORT-HORIZON RESEARCH INVENTORY

**Inventory date:** 2026-09-21  
**Evidence class:** `HISTORICAL_RESEARCH_INVENTORY / AUDIT_ONLY`  
**Production authority:** NONE  
**Runtime authority:** NONE  
**Manifest relationship:** subordinate evidence; the current `GOLD_CONTROL_PROJECT_MANIFEST.md` remains sole project authority.

## 1. Purpose

This inventory prevents loss of Gold Control research memory.

The current project manifest intentionally focuses on the active GC-BREAK architecture, current runtime roles, and the newer literature-direction sequence. Earlier fixed-horizon and specialist direction experiments remain historically important even when they are no longer active architecture.

This file records those earlier experiments without reopening them, promoting them, or changing the current GC-BREAK objective.

## 2. Cross-clock comparability lock

The following clocks/targets are **not one homogeneous leaderboard**:

1. NY17 direct direction: NEXT_NY17_1D / NEXT_NY17_3D.
2. Normal-day selective intraday / short-medium horizon: H3/H5/H10/H20.
3. Event-time reaction: R15 and event-specific windows.
4. Weekly direction research: RSM/ERSM, VLMC, BCT, B-CARS/RealP, Parisi.
5. Bonato Spot-XAU adaptation: retained-trading-day forward h={1,5,10}.
6. GC-BREAK: sequential trend-health / break-warning states rather than fixed-horizon direction.

Therefore:
- raw accuracy, balanced accuracy, DOWN sensitivity or hit rate may be compared **within compatible target clocks and evidence windows**;
- cross-clock values may be discussed descriptively but may not be used to claim one universal best motor;
- a statement such as “best DOWN model in all Gold Control history” requires a metric-complete, clock-matched audit and is otherwise `NOT_PROVEN`.

## 3. Historical NY17 direct-direction foundations

### 3.1 V1.49 short-horizon research

Historical authority branch/commit lineage includes manifest v1.49 and V1.49 audit surfaces.

Target:
- `NEXT_NY17_1D`
- `NEXT_NY17_3D`

Information universe:
- Gold own-history block;
- role-preserving FAST/SLOW/MONTHLY_DIRECTION/Emergency context where PIT-proven;
- other rich blocks were partially blocked by source/PIT constraints.

Retained full rich-panel outer result:
- 1D: n=371, balanced accuracy=0.4899383, Brier=0.2526246, P50 Brier=0.25 -> `NOT_PROVEN`;
- 3D: n=369, balanced accuracy=0.5000000, Brier=0.2441998, expanding-frequency Brier=0.2442888 -> `NOT_PROVEN`.

Historical matched-subset summaries and later replay surfaces may have different n because they answer different audit questions. Do not merge them into one score.

### 3.2 HS_SDL_DMA_DIRECTION_FUSION_V1

Frozen candidate universe:
- FAST;
- FAST+SLOW;
- FAST+SLOW+MONTHLY_DIRECTION;
- role-preserving context; no flat BOCPD/GVZ/Macro/Emergency direction vote.

Retained full replay:
- 1D: n=279, accuracy=0.5089606, balanced accuracy=0.5098407, Brier=0.2544683 vs P50=0.25 -> `NOT_PROVEN`;
- 3D: n=273, accuracy=0.5677656, balanced accuracy=0.5000000, Brier=0.2554044 vs P50=0.25 and expanding frequency=0.2485827 -> `NOT_PROVEN`;
- 1D abstention rate under the frozen 0.40/0.60 mapping was 0.9426523;
- 3D abstention rate was 0.2234432.

Class-specific UP/DOWN sensitivity is not retained in the checkpoint summary and must not be invented from balanced accuracy alone.

## 4. V1.51–V1.70 chronological research sequence

| Version | Historical experiment | Principal frozen finding | Historical decision |
|---|---|---|---|
| V1.51 | General 1D/3D master + event audit | General 1D/3D unstable; 3D pocket did not transport; event lane materially stronger | `FAIL_GENERAL_DIRECTION` |
| V1.52 | Selective event router | Employment + Inflation separated; R15 retained as event-specific lane | `KEEP_EVENT_LANE` |
| V1.53 | Intraday regime specialists | Regime-specific pockets existed but did not establish universal 1D direction | `NOT_PROVEN_GENERAL_1D` |
| V1.54 | Settlement RF/BAG/SGB/LOGIT, H5/H10/H20 | Class skew and regime flip | `FAIL` |
| V1.55 | Dynamic cross-market LOGIT/HGB/MLP + DMA/DMS | Regime instability plus DEXCHUS ontology/input problem | `FAIL_INPUT_AUDIT` |
| V1.56 | Realtime quantile selective / H20 RTQ | 2025 one-class collapse; 2026 strong retrospective pocket | `RESEARCH_LEAD_NOT_ROBUST` |
| V1.57 | Break-aware realized moments + BOCPD, H10/H20 | No incremental primary gain from realized moments under that architecture | `FAIL` |
| V1.58 | Trend-reversal router | Reversal classifier contained local information; forced direction routing degraded result | `FAIL_REVERSAL_CONTEXT_ONLY` |
| V1.59/R1 | Corrected broad-USD + real-10Y meta-trust | Economic ontology fixed; 2025 one-class behavior; 2026 nonlinear pocket did not transport | `FAIL` |
| V1.60 | Causal regime selector | 0% coverage / all NO_SIGNAL under frozen support gates | `FAIL_SUPPORT_GATE` |
| V1.61 | H3/H5 price discovery + realized moments + quantile boost | Distributional improvement did not create robust two-direction H3/H5 skill | `FAIL` |
| V1.62 | Context-aware meta forecast / CRASE_V0 | Experts weak/highly similar; CRASE coverage 0; proper-score gate failed | `FAIL` |
| V1.63 | Five heterogeneous forecasters | Diversity improved materially; no expert passed stable 2025+2026 skill gate | `FAIL_SKILL_GATE` |
| V1.64 | Forgetting + causal error memory | Local 3D Session/RM 2026 recovery, but 2025/proper-score transport failed | `NOT_PROMOTED` |
| V1.65A | ADWIN / Page-Hinkley drift detector | ADWIN low power; PH high false-alarm burden | `FAIL` |
| V1.65-DIAG | Failure attribution | 1D discrimination ceiling; 3D structured instability/shift | `DIAGNOSTIC` |
| V1.66 | Recalibration vs forgetting | Neither full gate passed | `STOP_ADAPTATION_ESCALATION` |
| V1.67 | Invariant-signal screening | No pre-2025 stable block passed invariance gate | `REJECT_INVARIANT_HYPOTHESIS` |
| V1.68 | Regime-similarity local | 2024Q4 bridge failed | `REJECT_SIMILARITY_ESCALATION` |
| V1.69 | Binary vs continuous-return target representation | Continuous return did not rescue 3D; weak 1D Session bridge pocket | `INFO_HORIZON_REDESIGN` |
| V1.70 | PIT-safe public COT + lagged GVZ context | Pre-2025 incremental gate failed; visible 2025 pocket reversed in 2026 | `FREE_CONTEXT_FAIL` |

Verified historical branch identities include:
- `gold-v151-master-orchestrator-thesis`
- `gold-v152-selective-event-router-thesis`
- `gold-v153-intraday-regime-specialists-thesis`
- `gold-v154-settlement-horizon-tree-thesis`
- `gold-v155-dynamic-crossmarket-direction-thesis`
- `gold-v156-realtime-quantile-selective-thesis`
- `gold-v157-breakaware-realized-moments-thesis`
- `gold-v158-trend-reversal-router-thesis`
- `gold-v159-driver-corrected-meta-trust-thesis`
- `gold-v160-final-regime-selector-thesis`
- `gold-v161-short-horizon-price-discovery-thesis`
- `gold-v162-context-aware-meta-forecast-research`
- `gold-v163-heterogeneous-forecasters-research`
- `gold-v164-adaptive-error-memory-forecaster-research`
- `gold-v165a-drift-detector-validation-research`
- `gold-v165diag-failure-attribution-research`
- `gold-v166-3d-mechanism-isolation-research`
- `gold-v167-invariant-signal-screening-research`
- `gold-v168-regime-similarity-local-research`
- `gold-v169-target-forecastability-audit-research`
- `gold-v170-public-positioning-context-research`.

## 5. Important retained quantitative checkpoints

### 5.1 Employment + Inflation event specialist — R15

Different clock from Bonato and daily/weekly direction; do not rank directly.

Historical hit evidence:
- 2023-2024 formation: 31/41 = 75.61%;
- 2025: 15/20 = 75%;
- available 2026: 7/9 = 77.78%, small-N.

Role:
- event-release first-reaction direction;
- not next-day continuation;
- Market Shock may confirm assimilation/intensity but does not prove continuation.

### 5.2 LEGACY_RTQ_R126 — H20

Different normal-day selective horizon from Bonato.

2025:
- accuracy=77.46%;
- balanced accuracy=50%;
- direction support=142 UP / 0 DOWN;
- MCC=0;
- interpretation: class-prior / one-class collapse.

Available 2026:
- coverage=72.97%;
- accuracy=70.37%;
- balanced accuracy=69.23%;
- MCC=0.4947;
- direction support=88 UP / 20 DOWN;
- interpretation: meaningful retrospective pocket, not stable cross-regime proof.

### 5.3 V1.59 nonlinear meta-trust diagnostic

2026:
- direction accuracy approximately 74%;
- balanced accuracy approximately 70.65%.

2025:
- all accepted signals UP;
- balanced accuracy=50%.

Interpretation:
- strong regime-dependent pocket;
- no stable global promotion.

### 5.4 V1.61 H5 price-discovery + realized-moments QBoost

Primary `H5_PD_RM_QB`:
- 2024 formation: coverage=15.42%, accuracy=51.28%, BA=46.12%, MCC=-0.1267, 35 UP / 4 DOWN;
- 2025 validation: coverage=21.61%, accuracy=72.55%, BA=52.22%, MCC=0.1021, 49 UP / 2 DOWN;
- available 2026: coverage=14.29%, accuracy=43.48%, BA=50%, MCC=0, 23 UP / 0 DOWN.

Decision: support gate failed; distributional pinball improvement did not establish robust direction discrimination.

### 5.5 V1.63 heterogeneous direct 1D/3D forecasters

1D 2025, n=203:
- GOLD_RIDGE BA=0.4831;
- SESSION_RM_RIDGE BA=0.5243;
- PRICE_DISCOVERY_HGB BA=0.5144;
- MACRO_CROSS_RIDGE BA=0.5389;
- FULL_HGB BA=0.5508.

1D available 2026, n=167:
- GOLD_RIDGE BA=0.4941;
- SESSION_RM_RIDGE BA=0.5219;
- PRICE_DISCOVERY_HGB BA=0.4782;
- MACRO_CROSS_RIDGE BA=0.5126;
- FULL_HGB BA=0.5004.

3D 2025, n=201:
- GOLD_RIDGE BA=0.5284;
- SESSION_RM_RIDGE BA=0.4797;
- PRICE_DISCOVERY_HGB BA=0.5142;
- MACRO_CROSS_RIDGE BA=0.5462;
- FULL_HGB BA=0.5090.

3D available 2026, n=165:
- GOLD_RIDGE BA=0.4056;
- SESSION_RM_RIDGE BA=0.4933;
- PRICE_DISCOVERY_HGB BA=0.4556;
- MACRO_CROSS_RIDGE BA=0.4656;
- FULL_HGB BA=0.4811.

No expert passed the frozen skill gate in both periods.

Exact class-specific DOWN sensitivity is not in the retained V1.63 checkpoint table; it is `CLASS_SPECIFIC_DOWN_NOT_REPORTED_IN_CHECKPOINT`.

### 5.6 V1.64 adaptive error memory

Strongest retrospective directional self-correction pocket was 3D Session/RM in available 2026:
- STATIC BA=0.49333;
- FORGET BA=0.52222;
- ERRMEM BA=0.56444;
- LOCAL_ERRMEM BA=0.57000, MCC=0.15256.

Same LOCAL_ERRMEM parent in 2025:
- BA approximately 0.48463;
- MCC negative;
- Brier=0.25924 vs frequency=0.23795.

Decision: real local repair, no transportable promotion.

### 5.7 V1.70 public COT + lagged GVZ

Pre-2025 incremental gate failed for both 1D and 3D.

2025 3D PUBLIC_ONLY pocket:
- Brier=0.23213 vs frequency=0.23783;
- AUC=0.6192.

Available 2026 reversal:
- Brier=0.28378 vs frequency=0.25111;
- AUC=0.4356.

Decision: intermittent public-context pocket, not stable skill.

## 6. Relationship to current literature-direction sequence

The newer weekly/literature families remain governed separately in the current manifest:
- RSM/ERSM;
- VLMC and successors;
- BCT/CTW and BCT-X/AR;
- B-CARS / RealP;
- Parisi;
- Bonato;
- registered but not-yet-executed Sadorsky/Basher-Sadorsky/Altuntas/Yadav/Sulman/Mahato-Attar/Zhang candidates.

This historical inventory does not reopen any closed family.

## 7. Bonato placement after restoring historical memory

Current Bonato identity:
`DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_RESEARCH`.

Bonato 1D RM:
- 2024 validation: accuracy=0.5415, BA=0.5293, UP sensitivity=0.6050, DOWN sensitivity=0.4535;
- locked 2025 replay: accuracy=0.5359, BA=0.5090, UP sensitivity=0.6571, DOWN sensitivity=0.3608.

What can be stated:
- Bonato 1D realized moments produces one of the clearest explicitly preserved two-sided DOWN improvements versus its own AR1 comparator;
- within Bonato, RV/RSK lifts DOWN sensitivity from 0.2209 to 0.4535 in 2024 and from 0.1134 to 0.3608 in 2025;
- many earlier 1D/3D checkpoints report BA/Brier/AUC but not class-specific DOWN sensitivity, so a complete all-history DOWN ranking is `NOT_PROVEN`;
- H20 and R15 results are different clocks and must not be used to declare Bonato globally best or worse;
- weekly VLMC/BCT/Parisi families are also a different target clock, so their DOWN sensitivities are descriptive cross-family context, not a strict same-task leaderboard.

Binding statement:

`BONATO_ALL_HISTORY_DOWN_RANK = NOT_PROVEN`.

Permitted statement:

`BONATO_1D_RM = ONE_OF_THE_STRONGER_EXPLICITLY_PRESERVED_TWO_SIDED_DOWN_SIGNALS, BUT NO_GLOBAL_RANKING`.

## 8. Historical-memory governance

Future manifest maintenance must preserve three separate inventories:

1. active/current GC-BREAK runtime/research roles;
2. current literature-direction sequence;
3. historical fixed-horizon / specialist research inventory.

A change in active architecture may retire a motor from current sequencing, but must not erase the historical research identity or its evidence classification.

