# GOLD SESSION BOCPD V1 FINAL AUTHORITY — 2026-10-07

**Status:** COMPLETE / NOT PROMOTED / 2026 DATA-BLOCKED

## Frozen identity
BOCPD V1 only:
- Beta-Bernoulli competence;
- prior Beta(0.5,0.5);
- expected run = 4 Handoff alarms;
- ACT if P(RESCUE) >= 0.60 and P(theta>0.50) >= 0.80;
- state independent by partition/window;
- only matured same-window outcomes with end_utc <= current start_utc update state;
- no V4 hysteresis or later-controller inputs.

## Stage-2: 2023-2024
Two heads were eligible for frozen transport:
- SOBTI ASIA_AFTERNOON_LIT / S17_A1_SESSION: N 189, Handoff 16, ACT 5, rescue/broken/net 3/2/+1, BA 52.18% -> 52.77%.
- SOBTI NY_LONDON_LIT / STRUCTURAL_IRIS_1H: N 215, Handoff 17, ACT 5, rescue/broken/net 3/2/+1, BA 53.26% -> 53.74%.

All other session heads failed before 2025.

## Stage-3: frozen 2025
Only the two eligible heads were opened. No thresholds, hazard, source mapping, clocks, features or base models were retuned.

### ASIA_AFTERNOON_LIT
- N 134
- Handoff alarms 17
- ACT 0
- rescue/broken/net 0/0/0
- Accuracy 45.52% -> 45.52%
- BA 45.52% -> 45.52%
- Decision: REJECT

### NY_LONDON_LIT
- N 143
- Handoff alarms 12
- ACT 0
- rescue/broken/net 0/0/0
- Accuracy 49.65% -> 49.65%
- BA 50.78% -> 50.78%
- Decision: REJECT

## Decision
BOCPD is NOT PROMOTED. The SESSION implementation is causal and clock-safe; the failure is transport behavior. In 2025 the frozen posterior trust rule never authorized a Handoff correction.

Do not relax the BOCPD thresholds or hazard after seeing 2025. Any relaxed version is a new model identity.

## 2026
DATA_BLOCKED. No governed V5-equivalent 2026 SESSION target population is available, so no daily/H3 label is substituted.

Next task by user instruction: perform a horizon/clock semantic audit across all previously completed SESSION models before starting DPTC. The audit must detect any residual H3/3-day target assumptions, wrong session start/end clocks, non-matured target-state updates, legacy H3 prediction/state reuse, or daily-label substitution. DPTC remains next only after this audit closes.

Authorities:
- GOLD_SESSION_BOCPD_V1_STAGE1_READINESS_AUTHORITY_2026-10-07.md
- GOLD_SESSION_BOCPD_V1_STAGE2_FINAL_AUTHORITY_2026-10-07.md
- GOLD_SESSION_BOCPD_V1_STAGE3_2025_RESULT_2026-10-07.md
- GOLD_SESSION_BOCPD_V1_STAGE3_2025_SUMMARY_2026-10-07.json
