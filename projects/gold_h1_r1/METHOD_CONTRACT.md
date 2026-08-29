# GOLD H1 R1 — Frozen Method Contract

## Forecast contract
- One-month-ahead target is the next calendar month's CORE5 monthly average gold USD/oz.
- Origin is the previous completed calendar month end.
- Target-month observations cannot enter features, model selection, thresholds, calibration, or weights.
- Random train/test split is prohibited.
- All evaluation must be rolling-origin or expanding-origin.

## Auto-control gates
Every new experiment must explicitly pass these checks before its result can be accepted:

1. **Target leakage check** — no target-month/later observation in prediction, calibration, threshold selection, routing, or feature construction.
2. **Origin availability check** — every signal has an availability timestamp and uses only completed observations available at the decision time.
3. **Split integrity check** — development, validation, and locked replay are not mixed; 2025–2026 cannot tune a fix later claimed robust on 2025–2026.
4. **Definition recovery check** — unavailable old formulas/thresholds/source contracts are `BLOCKED_MISSING_DEFINITION`; plausible reconstructions cannot be labelled exact.
5. **Metric-role check** — price-level accuracy, direction accuracy, model-selection accuracy, and trading performance are separate targets.
6. **Source-lineage check** — source, provider transitions, market/calendar-day handling, cutoff, and pinned commit/version must be recorded.
7. **Hindsight/oracle check** — oracle winners and realized errors are diagnostic only and cannot leak into ex-ante routing.
8. **Preservation check** — any 2023–2024 reversal fix is replayed unchanged on 2025–2026 and rejected if it materially destroys strong-trend behavior.

## Frozen Tactical R1
- Slow state: sign(completed weekly close - SMA4 of completed weekly closes).
- Slow persistence: same state for 2 consecutive completed weeks, else NEUTRAL.
- Fast state: sign(daily market close - SMA20 of completed market-day closes).
- Fast persistence: same state for 2 consecutive completed market days, else NEUTRAL.
- Production role: CONFIRM / CONFLICT / NEUTRAL only.
- Automatic full direction flip: challenger only.
- Continuous hard gate: rejected.

## Frozen BOCPD-return
- Expected run length: 36 months.
- Development alarm threshold: 0.034027906134261016.
- Alarm: BOCPD score >= threshold AND completed monthly log return < 0.
- Role: regime/break risk alert only.
- Automatic 3-month full exit: diagnostic only, not production-approved.

## Old Tactical V2
`BLOCKED_MISSING_EXACT_RULE`.
The historical M20/M40 formula, thresholds, and exact time-axis/source contract were not recovered.
