from __future__ import annotations

from .contracts import GVZRisk


def gvz_risk(value: float, full_cap_max: float = 25.9795, half_cap_max: float = 30.5238) -> GVZRisk:
    if value <= full_cap_max:
        return GVZRisk(value=float(value), cap=1.0, panic=False)
    if value <= half_cap_max:
        return GVZRisk(value=float(value), cap=0.5, panic=False)
    return GVZRisk(value=float(value), cap=0.25, panic=True)
