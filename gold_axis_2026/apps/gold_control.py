from __future__ import annotations

# Canonical Gold Control Streamlit entrypoint.
# Presentation authority: manifest v1.20 / final mobile V2 contract.
#
# Streamlit Cloud may execute this file with launcher-specific import paths.
# Do not rely on sibling-module discovery. Load the small local dependency set
# from exact repository file paths, register them under the legacy module names
# used by the V2 implementation, then execute the mobile implementation from
# its exact file path. This is deterministic across Python launcher semantics.

import importlib.util
import sys
from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
GOLD_ROOT = APP_DIR.parent
DATA_PIPELINE_DIR = GOLD_ROOT / "data_pipeline"


def _load_exact_module(name: str, path: Path, *, refresh: bool = False):
    """Load one local module from an exact path without sys.path discovery."""
    if not refresh and name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create import spec for {name} at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        # Do not leave a half-imported module cached after a failed load.
        sys.modules.pop(name, None)
        raise
    return module


# decision_source -> decision_store_reader -> decision_store dependency chain.
_load_exact_module("decision_store", DATA_PIPELINE_DIR / "decision_store.py")
_load_exact_module("decision_store_reader", DATA_PIPELINE_DIR / "decision_store_reader.py")

# Local app dependencies imported by gold_control_mobile_v1.py.
for _module_name in (
    "decision_source",
    "forecast_source",
    "live_sources",
    "mobile_ui_contract",
    "piyasa_contract",
):
    _load_exact_module(_module_name, APP_DIR / f"{_module_name}.py")

# Streamlit re-executes this entrypoint on every widget interaction, so execute
# the presentation module afresh each time while keeping deterministic helpers.
mobile_app = _load_exact_module(
    "gold_control_mobile_v1",
    APP_DIR / "gold_control_mobile_v1.py",
    refresh=True,
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
