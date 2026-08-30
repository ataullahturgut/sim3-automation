from __future__ import annotations

from collections.abc import Sequence

from .contracts import Direction


def three_month_direction(completed_month_returns: Sequence[float]) -> Direction:
    """Frozen 3M direction using only the last three completed monthly returns."""
    if len(completed_month_returns) < 3:
        return Direction.NEUTRAL
    m3 = sum(completed_month_returns[-3:]) / 3.0
    if m3 > 0:
        return Direction.UP
    if m3 < 0:
        return Direction.DOWN
    return Direction.NEUTRAL
