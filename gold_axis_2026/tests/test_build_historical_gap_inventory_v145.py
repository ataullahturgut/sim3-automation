from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "gold_axis_2026/tools/build_historical_gap_inventory_v145.py"
SPEC = importlib.util.spec_from_file_location("gap_inventory_v145", MODULE_PATH)
assert SPEC and SPEC.loader
gap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gap)


def test_ny17_same_month_and_lookback_cell_mapping():
    cells = gap.impacted_ny17_cells("2025-01-15")
    assert "FAST:2025-01" in cells
    assert "SLOW:2025-02" in cells
    assert "EMERGENCY_LEVEL:2025-01" in cells
    assert "EMERGENCY_REVERSAL:2025-01" in cells
    assert "MONTHLY_DIRECTION_3M:2025-02" in cells
    assert "MONTHLY_DIRECTION_3M:2025-05" in cells


def test_prehistory_maps_into_first_pilot_month():
    cells = gap.impacted_ny17_cells("2024-09-30")
    assert "MONTHLY_DIRECTION_3M:2025-01" in cells
    assert all(cell.split(":")[1] in gap.PILOT_MONTHS for cell in cells)


def test_month_arithmetic_crosses_year_boundary():
    assert gap.add_month("2025-12", 1) == "2026-01"
    assert gap.add_month("2025-01", -1) == "2024-12"


if __name__ == "__main__":
    tests = [(name, value) for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for name, test in sorted(tests):
        test()
        print(f"PASS {name}")
    print(f"PASS total={len(tests)}")
