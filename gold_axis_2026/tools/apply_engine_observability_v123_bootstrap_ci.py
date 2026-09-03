from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "gold_axis_2026"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{path}:{count}:{old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_bootstrap() -> None:
    path = GOLD / "apps" / "gold_control.py"
    replace_once(
        path,
        "# Presentation authority: manifest v1.22 / final mobile V2 contract.\n",
        "# Presentation authority: manifest v1.23 / final mobile V2 shell + all-engine observability contract.\n",
    )
    marker = '''_load_exact_module(
    "forecast_source",
'''
    addition = '''_load_exact_module(
    "engine_observability_contract",
    APP_DIR / "engine_observability_contract.py",
    required_exports=(
        "ENGINE_OBSERVABILITY_CONTRACT",
        "build_engine_inventory",
        "engine_inventory_counts",
    ),
)
'''
    replace_once(path, marker, addition + marker)


def patch_mobile_workflow() -> None:
    path = ROOT / ".github" / "workflows" / "gold-control-mobile-ui-v1.yml"
    text = path.read_text(encoding="utf-8")

    replacements = [
        ("name: Gold Control Mobile UI V1.22 Multi-Expert Final\n", "name: Gold Control Mobile UI V1.23 Engine Observability Final\n"),
        ("      - name: Verify manifest v1.22 and UI governance\n", "      - name: Verify manifest v1.23 and engine observability governance\n"),
        ("          grep -q 'Manifest version:\\\\*\\\\* 1.22' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n", "          grep -q 'Manifest version:\\\\*\\\\* 1.23' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n"),
        ("          echo 'V122_MULTI_EXPERT_UI_GOVERNANCE_PASS'\n", "          grep -q 'FROZEN_ALL_GOVERNED_ENGINES_VISIBLE_V1' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -q 'GOLD_CONTROL_ENGINE_OBSERVABILITY_CONTRACT_2026-09-03.md' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          echo 'V123_ENGINE_OBSERVABILITY_UI_GOVERNANCE_PASS'\n"),
        ("          pytest -q test_mobile_ui_contract.py test_piyasa_contract.py\n", "          pytest -q test_mobile_ui_contract.py test_piyasa_contract.py test_engine_observability_contract.py\n"),
        ("            gold_axis_2026/apps/decision_source.py \\\n            gold_axis_2026/apps/forecast_source.py \\\n", "            gold_axis_2026/apps/decision_source.py \\\n            gold_axis_2026/apps/engine_observability_contract.py \\\n            gold_axis_2026/apps/forecast_source.py \\\n"),
        ("      - name: Audit local imports and manifest v1.22 screen markers\n", "      - name: Audit local imports and manifest v1.23 screen markers\n"),
        ("              'decision_source': {'fetch_current_decision_state', 'fetch_decision_history'},\n              'forecast_source': {\n", "              'decision_source': {'fetch_current_decision_state', 'fetch_decision_history'},\n              'engine_observability_contract': {\n                  'ENGINE_OBSERVABILITY_CONTRACT','build_engine_inventory','engine_inventory_counts'\n              },\n              'forecast_source': {\n"),
        ("              'HISTORICAL_REPLAY'\n", "              'HISTORICAL_REPLAY','TÜM TAHMİN VE YÖN MOTORLARI',\n              'ALL_GOVERNED_FORECAST_DIRECTION_ENGINES_VISIBLE_V1'\n"),
        ("          for name in ('decision_store','decision_store_reader','decision_source','forecast_source','live_sources','mobile_ui_contract','piyasa_contract','gold_control_mobile_v1'):\n", "          for name in ('decision_store','decision_store_reader','decision_source','engine_observability_contract','forecast_source','live_sources','mobile_ui_contract','piyasa_contract','gold_control_mobile_v1'):\n"),
    ]

    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise RuntimeError(f"WORKFLOW_EXPECTED_EXACTLY_ONE_MATCH:{count}:{old[:100]!r}")
        text = text.replace(old, new, 1)

    path_marker = "      - 'gold_axis_2026/apps/decision_source.py'\n"
    path_add = (
        "      - 'gold_axis_2026/apps/decision_source.py'\n"
        "      - 'gold_axis_2026/apps/engine_observability_contract.py'\n"
        "      - 'gold_axis_2026/apps/test_engine_observability_contract.py'\n"
        "      - 'gold_axis_2026/GOLD_CONTROL_ENGINE_OBSERVABILITY_CONTRACT_2026-09-03.md'\n"
    )
    if text.count(path_marker) != 1:
        raise RuntimeError("WORKFLOW_PATH_MARKER_MISMATCH")
    text = text.replace(path_marker, path_add, 1)

    text = text.replace("V122_", "V123_").replace("v122_", "v123_")
    text = text.replace("gold-control-mobile-v122-", "gold-control-mobile-v123-")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    patch_bootstrap()
    patch_mobile_workflow()
    print("ENGINE_OBSERVABILITY_V123_BOOTSTRAP_CI_PATCH_PASS")


if __name__ == "__main__":
    main()
