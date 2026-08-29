# GOLD H1 R1 — Permanent Project State

This directory is the persistent source of truth for the gold 1-month-ahead forecasting/direction project.

## Canonical target
- Target: next calendar month's `CORE5 GOLD_USD_OZ` monthly average.
- Forecast origin: previous completed month end.
- Random split: prohibited.
- Future target leakage: prohibited.
- Tuning/selection: rolling or expanding origin using only information available at each origin.
- 2024–2026 terminology: procedurally locked historical replay, **not** untouched prospective holdout.

## Current architecture
1. **Price level:** VW-MIDAS-SVR Adapt V2 remains the strongest audited H=1 level reference. Exact archived rerun is still `BLOCKED_NOT_PROVEN`.
2. **Monthly direction context:** VW direction + exact 3M Momentum disagreement/context. 3M Momentum is a bull/trend-continuation challenger, **not** the canonical direction engine by itself.
3. **Tactical R1:** short-horizon reversal confirmation via `CONFIRM / CONFLICT / NEUTRAL`.
4. **BOCPD-return:** structural/regime-break risk alert only. It does not create direction and does not automatically change exposure.
5. **GVZ/risk:** planned/secondary risk context; not yet frozen in the current chain.

## Critical corrections
- `model_selector_gate_2024_2026.csv` is a **price-model selector** among VW/Patch/Momentum/RW. It must not be described as the canonical direction engine.
- The old Tactical V2 / M20-M40 exact rule was not recovered. Status stays `BLOCKED_MISSING_EXACT_RULE`; never reconstruct it from memory and call it exact.
- Do not tune fixes on 2025–2026 outcomes. Those years are preservation/locked replay evidence.
- The current research problem is **turning-point/reversal failure**, especially 2023–2024, not generic trend continuation.

## Final component decisions
- 3M Momentum: `KEEP` as bull/trend-continuation challenger.
- VW direction: `KEEP` as secondary disagreement signal.
- Tactical R1: `KEEP` as CONFIRM/CONFLICT layer.
- Automatic Tactical flip: `CHALLENGER / NOT_PRODUCTION`.
- Continuous Tactical hard gate: `REJECT`.
- CUSUM-return: `REJECT`.
- BOCPD-volatility: `REJECT`.
- Dual BOCPD: `REJECT`.
- BOCPD-return: `KEEP` as regime-risk alert.
- Automatic BOCPD exposure reduction/exit: `NOT_APPROVED`.

## Next research task
Run a reproducible 2023–2024 direction-error autopsy and test the smallest causal reversal correction using pre-target information only. Preserve 2025–2026 behavior; do not optimize against those outcomes.

## Files
- `PROJECT_STATE.json` — machine-readable current state.
- `METHOD_CONTRACT.md` — frozen methodology and auto-check gates.
- `direction_locked_replay.csv` — reproducible monthly direction replay data.
- `direction_static_scorecard.csv` — long-history direction candidates and validation metrics.
- `tactical_validation.csv` — Tactical R1 validation summary.
- `bocpd_final_audit.csv` — final BOCPD/CUSUM decisions and economic diagnostic.
- `model_selector_gate_2024_2026.csv` — separate price-model selector history.
- `SOURCE_MANIFEST.md` — data/source lineage and known source-quality constraints.
- `RECOVERY_CHECKLIST.md` — required first read when continuing in a new chat/session.

Updated: 2026-08-29.
