from __future__ import annotations

from .contracts import Direction, FastState, ReversalAlert, SlowState


def classify_state(
    monthly_direction: Direction,
    level_emergency: Direction,
    reversal_alert: ReversalAlert,
    fast: FastState,
    slow: SlowState,
    macro_event_down: bool | None = None,
) -> str:
    """Descriptive state only; no unrecovered exposure ladder is invented."""
    if macro_event_down is True:
        return "MACRO_DOWN_RISK"
    if reversal_alert == ReversalAlert.DOWN_ALERT:
        return "REVERSAL_RISK_DOWN"
    if reversal_alert == ReversalAlert.UP_ALERT:
        return "REVERSAL_RISK_UP"
    if level_emergency == Direction.UP and fast == FastState.ROBUST_UP and slow == SlowState.ROBUST_UP:
        return "ALIGNED_UP"
    if level_emergency == Direction.DOWN and fast == FastState.ROBUST_DOWN and slow == SlowState.ROBUST_DOWN:
        return "ALIGNED_DOWN"
    opposing_up = level_emergency == Direction.UP or fast == FastState.ROBUST_UP or slow == SlowState.ROBUST_UP
    opposing_down = level_emergency == Direction.DOWN or fast == FastState.ROBUST_DOWN or slow == SlowState.ROBUST_DOWN
    if monthly_direction == Direction.DOWN and opposing_up:
        return "CONFLICT"
    if monthly_direction == Direction.UP and opposing_down:
        return "CONFLICT"
    return "UNRESOLVED_MIXED"
