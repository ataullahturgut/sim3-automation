from __future__ import annotations

# Canonical Gold Control Streamlit entrypoint.
# Presentation authority: manifest v1.20 / final mobile V2 contract.
#
# Streamlit Cloud can preserve module objects across hot-reload/deploy cycles.
# Do not trust sys.path discovery or an existing sys.modules entry for any local
# Gold Control module. Every local dependency is reloaded from its exact file
# path on every Streamlit script run, its source path is verified, and required
# exports are checked before the presentation module is executed.

import importlib
import importlib.util
import sys
from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
GOLD_ROOT = APP_DIR.parent
DATA_PIPELINE_DIR = GOLD_ROOT / "data_pipeline"


def _load_exact_module(name: str, path: Path, *, required_exports: tuple[str, ...] = ()):
    """Force-load one local module from an exact path and validate its identity."""
    expected_path = path.resolve(strict=True)
    importlib.invalidate_caches()

    # Streamlit Cloud may retain a stale or foreign module with the same generic
    # name. Never reuse it for canonical local modules.
    sys.modules.pop(name, None)

    spec = importlib.util.spec_from_file_location(name, expected_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"LOCAL_MODULE_SPEC_FAILED:{name}:{expected_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise

    actual_file = getattr(module, "__file__", None)
    if actual_file is None or Path(actual_file).resolve() != expected_path:
        sys.modules.pop(name, None)
        raise ImportError(f"LOCAL_MODULE_PATH_MISMATCH:{name}:{actual_file}:{expected_path}")

    missing = [export for export in required_exports if not hasattr(module, export)]
    if missing:
        sys.modules.pop(name, None)
        raise ImportError(f"LOCAL_MODULE_EXPORT_MISSING:{name}:{','.join(missing)}")

    return module


# Full local dependency chain used by the mobile V2 application. Load in
# dependency order and verify every symbol consumed by downstream modules.
_load_exact_module(
    "decision_store",
    DATA_PIPELINE_DIR / "decision_store.py",
    required_exports=("EVIDENCE_CLASSES",),
)
_load_exact_module(
    "decision_store_reader",
    DATA_PIPELINE_DIR / "decision_store_reader.py",
    required_exports=("read_latest_decision",),
)
_load_exact_module(
    "decision_source",
    APP_DIR / "decision_source.py",
    required_exports=("fetch_current_decision_state", "fetch_decision_history"),
)
_load_exact_module(
    "forecast_source",
    APP_DIR / "forecast_source.py",
    required_exports=("fetch_current_forecast", "fetch_forecast_history"),
)
_load_exact_module(
    "live_sources",
    APP_DIR / "live_sources.py",
    required_exports=("fetch_xau_spot", "fetch_xau_history", "fetch_gvz_latest"),
)
_load_exact_module(
    "mobile_ui_contract",
    APP_DIR / "mobile_ui_contract.py",
    required_exports=(
        "FINAL_MOCKUP_CONTRACT",
        "SCENARIO_STATUS",
        "arrow_state",
        "classification_label",
        "decision_view_state",
        "deterministic_explanation",
        "display_state",
        "evidence_badge",
        "forecast_view_state",
    ),
)
_load_exact_module(
    "piyasa_contract",
    APP_DIR / "piyasa_contract.py",
    required_exports=(
        "filter_history_timeframe",
        "gvz_regime",
        "latest_completed_daily_row",
        "price_delta",
    ),
)

# Execute the presentation module afresh on every Streamlit rerun. Its legacy
# sibling imports now resolve only to the exact modules registered above.
mobile_app = _load_exact_module(
    "gold_control_mobile_v1",
    APP_DIR / "gold_control_mobile_v1.py",
)

# The implementation-level CSS predates the dedicated main-nav radio key and
# used a broad stRadio selector. Reset ordinary radios, then re-apply fixed
# positioning only to the canonical gc_main_nav control.
st.markdown(
    """
<style>
[data-testid="stRadio"]{
 position:static!important;left:auto!important;right:auto!important;bottom:auto!important;
 transform:none!important;z-index:auto!important;width:auto!important;max-width:none!important;
 box-shadow:none!important;margin:0!important;
}
.st-key-gc_main_nav [data-testid="stRadio"]{
 position:fixed!important;left:50%!important;transform:translateX(-50%)!important;bottom:.45rem!important;
 z-index:9999!important;width:min(820px,calc(100vw - 1rem))!important;
 background:#fff!important;border:1px solid #e4eaf1!important;border-radius:17px!important;
 padding:.28rem!important;box-shadow:0 8px 28px rgba(15,39,72,.16)!important;
}
</style>
    """,
    unsafe_allow_html=True,
)
