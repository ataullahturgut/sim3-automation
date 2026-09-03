from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOBILE = ROOT.parent / ".github" / "workflows" / "gold-control-mobile-ui-v1.yml"
SMOKE = ROOT.parent / ".github" / "workflows" / "gold-control-app-smoke.yml"


def replace_once(text: str, old: str, new: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{n}:{old[:120]!r}")
    return text.replace(old, new, 1)


def patch_mobile() -> None:
    text = MOBILE.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "name: Gold Control Mobile UI V1.23 Engine Observability Final",
        "name: Gold Control Mobile UI V1.25 Data Evidence Spine Final",
    )
    text = replace_once(
        text,
        "      - 'gold_axis_2026/apps/decision_source.py'\n      - 'gold_axis_2026/apps/engine_observability_contract.py'",
        "      - 'gold_axis_2026/apps/decision_source.py'\n      - 'gold_axis_2026/apps/runtime_source.py'\n      - 'gold_axis_2026/apps/engine_observability_contract.py'",
    )
    text = replace_once(
        text,
        "      - name: Verify manifest v1.23 and engine observability governance",
        "      - name: Verify manifest v1.25 and Data Evidence Spine governance",
    )
    manifest_old = r"          grep -q 'Manifest version:\*\* 1.23' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md"
    manifest_new = (
        r"          grep -q 'Manifest version:\*\* 1.25' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md"
        "\n          grep -q 'FROZEN_DATA_EVIDENCE_SPINE_V1' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md"
        "\n          grep -q 'RUNTIME_BOOTSTRAP_PRODUCTION_PASS' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md"
    )
    text = replace_once(text, manifest_old, manifest_new)
    text = replace_once(
        text,
        "          echo 'V123_ENGINE_OBSERVABILITY_UI_GOVERNANCE_PASS'",
        "          echo 'V125_DATA_EVIDENCE_SPINE_UI_GOVERNANCE_PASS'",
    )
    text = replace_once(
        text,
        "            gold_axis_2026/apps/decision_source.py \\\n            gold_axis_2026/apps/engine_observability_contract.py \\",
        "            gold_axis_2026/apps/decision_source.py \\\n            gold_axis_2026/apps/runtime_source.py \\\n            gold_axis_2026/apps/engine_observability_contract.py \\",
    )
    text = replace_once(
        text,
        "      - name: Audit local imports and manifest v1.23 screen markers",
        "      - name: Audit local imports and manifest v1.25 screen markers",
    )
    text = replace_once(
        text,
        "              'decision_source': {'fetch_current_decision_state', 'fetch_decision_history'},\n              'engine_observability_contract': {",
        "              'decision_source': {'fetch_current_decision_state', 'fetch_decision_history'},\n              'runtime_source': {'fetch_runtime_observability'},\n              'engine_observability_contract': {",
    )
    MOBILE.write_text(text, encoding="utf-8")


def patch_smoke() -> None:
    text = SMOKE.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "            gold_axis_2026/apps/decision_source.py \\\n            gold_axis_2026/apps/engine_observability_contract.py \\",
        "            gold_axis_2026/apps/decision_source.py \\\n            gold_axis_2026/apps/runtime_source.py \\\n            gold_axis_2026/apps/engine_observability_contract.py \\",
    )
    text = replace_once(
        text,
        "          from decision_source import CONTEXT_EVIDENCE_CLASS, fetch_current_decision_state\n\n          state = fetch_current_decision_state(os.environ['NEON_DATABASE_URL'])",
        "          from decision_source import CONTEXT_EVIDENCE_CLASS, fetch_current_decision_state\n          from runtime_source import fetch_runtime_observability\n\n          runtime = fetch_runtime_observability(os.environ['NEON_DATABASE_URL'])\n          assert runtime['status'] == 'DATA_EVIDENCE_SPINE_RUNTIME_HEALTH_PASS', runtime\n          assert runtime['runtime_engine_count'] == 12, runtime\n          assert runtime['context_exactly_one_link'] == 7, runtime\n          assert runtime['integrity_ok'] is True, runtime\n          assert runtime['database_writes'] == 'NONE', runtime\n          print('GOLD_CONTROL_DATA_EVIDENCE_SPINE_APP_READER_PASS runtime=12/12 context_links=7/7 integrity=PASS')\n\n          state = fetch_current_decision_state(os.environ['NEON_DATABASE_URL'])",
    )
    SMOKE.write_text(text, encoding="utf-8")


def main() -> int:
    patch_mobile()
    patch_smoke()
    print("RUNTIME_SOURCE_CI_CONTRACT_V1_PATCH_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
