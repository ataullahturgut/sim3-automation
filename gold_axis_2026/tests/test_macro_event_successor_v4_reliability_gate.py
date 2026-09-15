from datetime import datetime, timezone

import pytest

from gold_axis_2026.data_pipeline.macro_event_successor_v4_reliability_gate import (
    ROLE_BY_FAMILY,
    binom_one_sided_p,
    classify_role,
    reaction_pct,
    signed_reaction,
)


def test_family_roles_are_frozen():
    assert ROLE_BY_FAMILY == {
        "EMPLOYMENT": "DIRECTIONAL",
        "FOMC": "DIRECTIONAL",
        "INFLATION": "CONTEXT_ONLY",
    }


@pytest.mark.parametrize(
    ("family", "state", "role", "signal"),
    [
        ("EMPLOYMENT", "GOLD_ADVERSE_MACRO_SHOCK", "DIRECTIONAL", "GOLD_ADVERSE"),
        ("FOMC", "GOLD_SUPPORTIVE_MACRO_SHOCK", "DIRECTIONAL", "GOLD_SUPPORTIVE"),
        ("INFLATION", "GOLD_SUPPORTIVE_MACRO_SHOCK", "CONTEXT_ONLY", "ABSTAIN_CONTEXT_ONLY"),
        ("EMPLOYMENT", "MACRO_MIXED_OR_SMALL", "DIRECTIONAL", "NO_SIGNAL"),
    ],
)
def test_classify_role(family, state, role, signal):
    assert classify_role(family, state) == (role, signal)


def test_reaction_and_sign_semantics():
    assert reaction_pct(100.0, 101.0) == pytest.approx(1.0)
    assert signed_reaction("GOLD_SUPPORTIVE_MACRO_SHOCK", 1.0) == pytest.approx(1.0)
    assert signed_reaction("GOLD_ADVERSE_MACRO_SHOCK", -1.0) == pytest.approx(1.0)


def test_exact_sign_gate_reference_values():
    assert binom_one_sided_p(7, 8) == pytest.approx(0.03515625)
    assert binom_one_sided_p(6, 8) == pytest.approx(0.14453125)
    assert binom_one_sided_p(6, 6) == pytest.approx(0.015625)
