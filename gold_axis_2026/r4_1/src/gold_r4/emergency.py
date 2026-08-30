from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .contracts import Direction, ReversalAlert


@dataclass
class EmergencyState:
    level_threshold_abs: float = 0.04
    reversal_threshold_abs: float = 0.04
    current_month: str | None = None
    shock_direction: Direction = Direction.NEUTRAL
    running_peak: float | None = None
    running_trough: float | None = None

    def _reset_month(self, month_key: str) -> None:
        self.current_month = month_key
        self.shock_direction = Direction.NEUTRAL
        self.running_peak = None
        self.running_trough = None

    def update(self, date: pd.Timestamp, close: float, monthly_vw_forecast: float) -> tuple[Direction, ReversalAlert]:
        """Frozen R4.1 EOD Emergency Direction + reversal alert."""
        month_key = date.strftime("%Y-%m")
        if self.current_month != month_key:
            self._reset_month(month_key)
        if monthly_vw_forecast <= 0:
            raise ValueError("monthly_vw_forecast must be positive")

        displacement = close / monthly_vw_forecast - 1.0
        if displacement >= self.level_threshold_abs:
            level = Direction.UP
        elif displacement <= -self.level_threshold_abs:
            level = Direction.DOWN
        else:
            level = Direction.NEUTRAL

        if level == Direction.UP and self.shock_direction != Direction.UP:
            self.shock_direction = Direction.UP
            self.running_peak = close
            self.running_trough = None
        elif level == Direction.DOWN and self.shock_direction != Direction.DOWN:
            self.shock_direction = Direction.DOWN
            self.running_trough = close
            self.running_peak = None

        alert = ReversalAlert.OFF
        if self.shock_direction == Direction.UP:
            self.running_peak = max(self.running_peak or close, close)
            if close / self.running_peak - 1.0 <= -self.reversal_threshold_abs:
                alert = ReversalAlert.DOWN_ALERT
        elif self.shock_direction == Direction.DOWN:
            self.running_trough = min(self.running_trough or close, close)
            if close / self.running_trough - 1.0 >= self.reversal_threshold_abs:
                alert = ReversalAlert.UP_ALERT

        return level, alert
