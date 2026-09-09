from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("pilot",ROOT/"gold_axis_2026/tools/run_gold_pilot_validation_v145.py")
assert SPEC and SPEC.loader
m=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(m)


def test_frozen_inventory_and_axis():
    assert len(m.ENGINES)==12 and len(set(m.ENGINES))==12
    assert len(m.PILOT_MONTHS)==20
    assert m.PILOT_MONTHS[0]=="2025-01" and m.PILOT_MONTHS[-1]=="2026-08"


def test_no_random_split_or_optimizer_surface():
    source=(ROOT/"gold_axis_2026/tools/run_gold_pilot_validation_v145.py").read_text()
    assert "train_test_split" not in source
    assert "GridSearchCV" not in source
    assert "AUTO_SELECTOR" not in source


def test_run_lengths_are_deterministic():
    assert m.runs([1,1,0,0,0,-1])==[2,3,1]


def test_explicit_sign():
    assert [m.sign(v) for v in (-0.1,0,0.1)]==[-1,0,1]
