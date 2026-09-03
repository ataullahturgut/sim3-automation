from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "simple_expert_v2" / "simple_expert_v2_source_binding_evidence.json"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{path}:{count}:{old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_once(path: Path, marker: str, addition: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        raise RuntimeError(f"PROMOTION_SECTION_ALREADY_PRESENT:{path}:{marker}")
    path.write_text(text.rstrip() + "\n\n" + addition.strip() + "\n", encoding="utf-8")


def verify_evidence() -> None:
    e = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    required = {
        "decision": "SIMPLE_EXPERT_V2_SOURCE_BINDING_PASS",
        "rw_decision": "RW_R2_SOURCE_BINDING_MODEL_IMPACT_PASS",
        "momentum_decision": "MOMENTUM_3M_R2_SOURCE_BINDING_MODEL_IMPACT_PASS",
        "actual_reconciliation": "43/43",
        "rw_r1_reconciliation": "43/43",
        "momentum_r1_reconciliation": "43/43",
    }
    for key, value in required.items():
        if e.get(key) != value:
            raise RuntimeError(f"PROMOTION_EVIDENCE_MISMATCH:{key}:{e.get(key)!r}:{value!r}")
    if not e.get("hard_integrity_pass"):
        raise RuntimeError("PROMOTION_HARD_INTEGRITY_NOT_PASS")
    if e.get("future_information_violations") != 0:
        raise RuntimeError("PROMOTION_FUTURE_INFORMATION_VIOLATION")
    if e.get("post_result_retune") is not False or e.get("thresholds_relaxed") is not False:
        raise RuntimeError("PROMOTION_CHANGE_CONTROL_VIOLATION")


def patch_multi_expert() -> None:
    path = ROOT / "data_pipeline" / "multi_expert_forecast.py"
    replace_once(path, 'MANIFEST_VERSION = "1.22"', 'MANIFEST_VERSION = "1.24"')
    replace_once(
        path,
        'EXPERT_ORDER = (PATCH_EXPERT, VW_EXPERT, MOMENTUM_EXPERT, RW_EXPERT)\n',
        'EXPERT_ORDER = (PATCH_EXPERT, VW_EXPERT, MOMENTUM_EXPERT, RW_EXPERT)\n\n'
        'SIMPLE_EXPERT_SOURCE_ID = "SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2"\n'
        'RW_V2_VERSION = "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"\n'
        'MOMENTUM_V2_VERSION = "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"\n'
        'SIMPLE_EXPERT_SOURCE_EVIDENCE = "SIMPLE_EXPERT_V2_SOURCE_BINDING_PASS"\n',
    )
    replace_once(
        path,
        '''    MOMENTUM_EXPERT: ExpertDefinition(
        expert_id=MOMENTUM_EXPERT,
        label="3M Momentum",
        model_name="MOMENTUM_3M",
        model_version="MOMENTUM_3M_R1",
        expert_role="EXPERT",
        execution_status="BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND",
        status_reason="Formula is reproducible, but a manifest-authorized forward monthly level source has not been bound to this expert.",
    ),
    RW_EXPERT: ExpertDefinition(
        expert_id=RW_EXPERT,
        label="Random Walk",
        model_name="RANDOM_WALK",
        model_version="RW_R1",
        expert_role="BENCHMARK",
        execution_status="BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND",
        status_reason="Benchmark formula is reproducible, but a manifest-authorized forward monthly level source has not been bound.",
    ),
''',
        '''    MOMENTUM_EXPERT: ExpertDefinition(
        expert_id=MOMENTUM_EXPERT,
        label="3M Momentum",
        model_name="MOMENTUM_3M",
        model_version=MOMENTUM_V2_VERSION,
        expert_role="EXPERT",
        execution_status="EXECUTABLE_FORWARD_EXPERT",
        status_reason="Source-bound V2 passed the frozen 43-origin source/materiality/non-inferiority audit; issuance waits for an eligible prospective month-end origin.",
    ),
    RW_EXPERT: ExpertDefinition(
        expert_id=RW_EXPERT,
        label="Random Walk",
        model_name="RANDOM_WALK",
        model_version=RW_V2_VERSION,
        expert_role="BENCHMARK",
        execution_status="EXECUTABLE_FORWARD_EXPERT",
        status_reason="Source-bound V2 passed the frozen 43-origin source/materiality/non-inferiority audit; issuance waits for an eligible prospective month-end origin.",
    ),
''',
    )
    replace_once(
        path,
        '        if EXPERT_REGISTRY[x].execution_status == "EXECUTABLE_FORWARD_ISSUER_CANDIDATE"\n',
        '        if EXPERT_REGISTRY[x].execution_status.startswith("EXECUTABLE_FORWARD_")\n',
    )
    marker = '\ndef expert_status(expert_id: str) -> dict[str, str]:\n'
    addition = '''\ndef rw_r2_source_bound(monthly_levels: Iterable[float]) -> float:
    """Forward V2 RW formula; source semantics are enforced by the issuer contract."""
    return rw_r1(monthly_levels)


def momentum_3m_r2_source_bound(monthly_levels: Iterable[float]) -> float:
    """Forward V2 3M Momentum formula; source semantics are enforced by the issuer contract."""
    return momentum_3m_r1(monthly_levels)

'''
    text = path.read_text(encoding="utf-8")
    if "def rw_r2_source_bound" in text:
        raise RuntimeError("V2_FORMULA_WRAPPERS_ALREADY_PRESENT")
    if marker not in text:
        raise RuntimeError("EXPERT_STATUS_MARKER_MISSING")
    path.write_text(text.replace(marker, addition + marker, 1), encoding="utf-8")


def patch_tests() -> None:
    path = ROOT / "data_pipeline" / "test_multi_expert_forecast.py"
    replace_once(
        path,
        '''    momentum_3m_r1,
    rw_r1,
    selector_contract,
''',
        '''    momentum_3m_r1,
    momentum_3m_r2_source_bound,
    rw_r1,
    rw_r2_source_bound,
    selector_contract,
''',
    )
    replace_once(
        path,
        '''def test_only_patch_is_currently_forward_executable():
    assert executable_experts() == (PATCH_EXPERT,)
    assert EXPERT_REGISTRY[VW_EXPERT].execution_status == "BLOCKED_NOT_PROVEN_EXECUTABLE"
    assert EXPERT_REGISTRY[MOMENTUM_EXPERT].execution_status == "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND"
    assert EXPERT_REGISTRY[RW_EXPERT].execution_status == "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND"
''',
        '''def test_patch_rw_and_momentum_are_forward_executable_after_frozen_v2_source_pass():
    assert executable_experts() == (PATCH_EXPERT, MOMENTUM_EXPERT, RW_EXPERT)
    assert EXPERT_REGISTRY[VW_EXPERT].execution_status == "BLOCKED_NOT_PROVEN_EXECUTABLE"
    assert EXPERT_REGISTRY[MOMENTUM_EXPERT].execution_status == "EXECUTABLE_FORWARD_EXPERT"
    assert EXPERT_REGISTRY[RW_EXPERT].execution_status == "EXECUTABLE_FORWARD_EXPERT"
    assert EXPERT_REGISTRY[MOMENTUM_EXPERT].model_version == "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"
    assert EXPERT_REGISTRY[RW_EXPERT].model_version == "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"
''',
    )
    replace_once(
        path,
        '''def test_rw_and_momentum_formulas_are_reproducible_but_source_agnostic():
    levels = [100.0, 110.0, 121.0, 133.1]
    assert rw_r1(levels) == pytest.approx(133.1)
    assert momentum_3m_r1(levels) == pytest.approx(146.41)
''',
        '''def test_rw_and_momentum_formulas_preserve_r1_math_under_explicit_v2_source_binding():
    levels = [100.0, 110.0, 121.0, 133.1]
    assert rw_r1(levels) == pytest.approx(133.1)
    assert momentum_3m_r1(levels) == pytest.approx(146.41)
    assert rw_r2_source_bound(levels) == pytest.approx(rw_r1(levels))
    assert momentum_3m_r2_source_bound(levels) == pytest.approx(momentum_3m_r1(levels))
''',
    )


def patch_observability() -> None:
    path = ROOT / "apps" / "engine_observability_contract.py"
    replace_once(
        path,
        '''        "version": "MOMENTUM_3M_R1",
        "default_status": "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND",
''',
        '''        "version": "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND",
        "default_status": "WAITING_ELIGIBLE_MONTH_END_ORIGIN",
''',
    )
    replace_once(
        path,
        '''        "version": "RW_R1",
        "default_status": "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND",
''',
        '''        "version": "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND",
        "default_status": "WAITING_ELIGIBLE_MONTH_END_ORIGIN",
''',
    )


def patch_manifest() -> None:
    path = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
    text = path.read_text(encoding="utf-8")
    old = "**Manifest version:** 1.23"
    if old not in text:
        raise RuntimeError("MANIFEST_V123_MARKER_MISSING")
    text = text.replace(old, "**Manifest version:** 1.24", 1)
    path.write_text(text, encoding="utf-8")
    append_once(
        path,
        "SIMPLE_EXPERT_V2_SOURCE_BINDING_PASS",
        '''## 7.D SIMPLE-EXPERT SOURCE BINDING V2 — FROZEN PASS / FORWARD READINESS

Status frozen on 2026-09-03 under `GOLD_CONTROL_SIMPLE_EXPERT_SOURCE_BINDING_V2_CHANGE_CONTROL_2026-09-03.md`.

- Source identity: `SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2`.
- Provider/semantic: Twelve Data `XAU/USD`, `1h`, `America/New_York`; use the close of the bar opened at `16:00:00` and aggregate positive finite selected closes to the completed calendar-month arithmetic mean; minimum 15 unique selected dates; no interpolation/forward-fill/provider substitution.
- CME/EBS 17:00 ET trade-date-roll evidence is supporting market-session context; the Gold Control source remains explicitly a Twelve hourly-derived measurement and is not relabelled as an official EBS/LBMA/settlement fixing.
- Frozen validation window: `2023-01..2026-07`, `N=43`; historical evidence class `HISTORICAL_REPLAY_MODEL_IMPACT`, not prospective proof.
- Extended required source months `2022-09..2026-06`: 46/46 present, zero low-count months, zero duplicate selected dates.
- Extended source vs CORE5: level correlation `0.9999721441764589`; median gap `10.9548 bps`; p95 gap `33.2791 bps`; return correlation `0.9964220374584144`; return direction agreement `0.9555555555555556`.
- Actual/R1 reconciliation: actual `43/43`; RW R1 `43/43`; Momentum R1 `43/43`; future-information violations `0`; deterministic rerun max diff `0.0`.
- Random Walk V2 identity: `RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`; result `RW_R2_SOURCE_BINDING_MODEL_IMPACT_PASS`.
- 3M Momentum V2 identity: `MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`; result `MOMENTUM_3M_R2_SOURCE_BINDING_MODEL_IMPACT_PASS`.
- Joint gate: `SIMPLE_EXPERT_V2_SOURCE_BINDING_PASS`.
- No threshold relaxation, post-result retuning, provider substitution, database write, forecast-ledger write, or Decision Store write occurred during validation.
- Forward status after this PASS: both V2 experts are executable, but **no September 2026 origin may be backfilled**. Their first eligible H=1 month-end issuance remains the end-September 2026 origin for the October 2026 target, subject to the frozen source-completion and immutable-snapshot gates.
- Until an eligible origin is actually issued, UI status is `WAITING_ELIGIBLE_MONTH_END_ORIGIN`, not a fabricated forecast value.
- `NOT_PROVEN_EXPERT_SELECTION_RULE` remains binding; `AUTO_SELECTOR=OFF`; `AUTO_ENSEMBLE=OFF`; every individual expert remains `canonical_authority=false`.
- This change does not authorize BUY/SELL/HOLD/EXIT/REDUCE or exposure mapping.
''',
    )


def main() -> None:
    verify_evidence()
    patch_multi_expert()
    patch_tests()
    patch_observability()
    patch_manifest()
    print("SIMPLE_EXPERT_V2_PROMOTION_PATCH_PASS")


if __name__ == "__main__":
    main()
