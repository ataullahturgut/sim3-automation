from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Direction(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"


class FastState(str, Enum):
    ROBUST_UP = "ROBUST_UP"
    ROBUST_DOWN = "ROBUST_DOWN"
    MIXED = "MIXED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class SlowState(str, Enum):
    ROBUST_UP = "ROBUST_UP"
    ROBUST_DOWN = "ROBUST_DOWN"
    NOT_YET_ROBUST = "NOT_YET_ROBUST"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ReversalAlert(str, Enum):
    UP_ALERT = "UP_ALERT"
    DOWN_ALERT = "DOWN_ALERT"
    OFF = "OFF"


@dataclass(frozen=True)
class GVZRisk:
    value: float
    cap: float
    panic: bool


@dataclass(frozen=True)
class EngineSnapshot:
    date: str
    close: float
    monthly_vw_forecast: float
    monthly_direction: Direction
    level_emergency: Direction
    reversal_alert: ReversalAlert
    fast_state: FastState
    slow_state: SlowState
    gvz: Optional[GVZRisk]
    macro_event_down: Optional[bool]
    bocpd_context: Optional[str]
    classification: str
