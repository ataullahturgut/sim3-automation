from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
CONTRACTS=ROOT/"hs_sdl_dma_v1/contracts"


def load(name): return json.loads((CONTRACTS/name).read_text())


def test_candidate_universe_is_small_nested_and_frozen():
    c=load("candidate_universe_v1.json")
    assert c["status"]=="FROZEN_BEFORE_OUTER_SCORING"
    assert c["candidate_count"]==len(c["candidates"])<=4
    cols=[set(x["columns"]) for x in c["candidates"]]
    assert cols[0] < cols[1] < cols[2]


def test_context_roles_are_not_direction_votes():
    c=load("candidate_universe_v1.json")
    used={z for x in c["candidates"] for z in x["columns"]}
    assert all(name not in used for name in c["forbidden_as_direction_votes"])
    assert c["context_main_effects"]==[]


def test_inner_and_calibration_are_prior_only():
    c=load("inner_rules_v1.json")
    assert c["calibration"]["outer_target_in_fit"] is False
    assert c["three_day_delay"]=="UPDATE_ONLY_WHEN_TARGET_INDEX_LE_ORIGIN_INDEX"
    assert c["randomness_used"] is False


def test_abstention_and_promotion_frozen_before_outer():
    c=load("preregistration_v1.json")
    assert c["status"]=="FROZEN_BEFORE_OUTER_SCORING"
    assert c["outer_results_consumed"] is False
    assert c["direction_mapping"]["UP"]=="p_cal >= 0.60"
    assert c["direction_mapping"]["DOWN"]=="p_cal <= 0.40"
