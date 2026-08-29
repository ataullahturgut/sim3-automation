# New Chat / New Session Recovery Checklist

Read these files before doing any new GOLD H1 R1 work:

1. `projects/gold_h1_r1/PROJECT_STATE.json`
2. `projects/gold_h1_r1/METHOD_CONTRACT.md`
3. `projects/gold_h1_r1/SOURCE_MANIFEST.md`
4. `projects/gold_h1_r1/direction_static_scorecard.csv`
5. `projects/gold_h1_r1/direction_locked_replay.csv`
6. `projects/gold_h1_r1/tactical_validation.csv`
7. `projects/gold_h1_r1/bocpd_final_audit.csv`
8. `projects/gold_h1_r1/model_selector_gate_2024_2026.csv`

Then inspect relevant existing GitHub Actions workflows/commits before rebuilding a runner.

## Mandatory interpretation guardrails
- Do not describe 3M Momentum as the whole direction engine.
- Do not describe the VW/Patch/Momentum/RW gate as the canonical direction engine; it is a price-model selector.
- Do not invent old Tactical V2.
- Do not use 2025–2026 to tune a 2023–2024 correction.
- Keep BOCPD as risk context, not a directional voter.
- Mark absent evidence `NOT_FOUND`, `NOT_PROVEN`, `BLOCKED`, or `UNRESOLVED` rather than guessing.

## Current next task
Reproducible 2023–2024 direction-error autopsy, focused on reversal/turning-point failures. Test only minimal causal corrections and preserve 2025–2026 behavior.
