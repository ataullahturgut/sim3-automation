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
        """Emergency level + path-dependent reversal state.

        V1.46 defect fix: reversal is evaluated against the pre-existing
        shock excursion before a same-observation opposite level breach is
        allowed to replace that state. This preserves running-peak/running-
        trough drawdown/drawup semantics and prevents a sharp cross-through
        from erasing the reversal event. The frozen +/-4% thresholds are not
        retuned here.
        """
        month_key = date.strftime("%Y-%m")
        if self.current_month != month_key:
            self._reset_month(month_key)
        if monthly_vw_forecast <= 0:
            raise ValueError("monthly_vw_forecast must be positive")
        if close <= 0:
            raise ValueError("close must be positive")

        displacement = close / monthly_vw_forecast - 1.0
        if displacement >= self.level_threshold_abs:
            level = Direction.UP
        elif displacement <= -self.level_threshold_abs:
            level = Direction.DOWN
        else:
            level = Direction.NEUTRAL

        # Evaluate reversal against the excursion that existed before this
        # observation. Otherwise a one-step move from +4% territory to -4%
        # territory (or vice versa) can overwrite shock_direction before the
        # peak-to-current drawdown / trough-to-current drawup is measured.
        alert = ReversalAlert.OFF
        prior_direction = self.shock_direction
        if prior_direction == Direction.UP:
            self.running_peak = max(self.running_peak or close, close)
            if close / self.running_peak - 1.0 <= -self.reversal_threshold_abs:
                alert = ReversalAlert.DOWN_ALERT
        elif prior_direction == Direction.DOWN:
            self.running_trough = min(self.running_trough or close, close)
            if close / self.running_trough - 1.0 >= self.reversal_threshold_abs:
                alert = ReversalAlert.UP_ALERT

        # Only after measuring the prior excursion may the current level breach
        # become the regime tracked for the next observation.
        if level == Direction.UP and self.shock_direction != Direction.UP:
            self.shock_direction = Direction.UP
            self.running_peak = close
            self.running_trough = None
        elif level == Direction.DOWN and self.shock_direction != Direction.DOWN:
            self.shock_direction = Direction.DOWN
            self.running_trough = close
            self.running_peak = None
        elif level == Direction.UP:
            self.running_peak = max(self.running_peak or close, close)
        elif level == Direction.DOWN:
            self.running_trough = min(self.running_trough or close, close)

        return level, alert
