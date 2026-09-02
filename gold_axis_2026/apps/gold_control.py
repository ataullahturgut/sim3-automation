from __future__ import annotations

# Canonical Gold Control Streamlit entrypoint.
# Presentation authority: manifest v1.20 / final mobile V2 contract.
# Hosted Streamlit re-executes this file on widget interaction. Python caches
# imported modules, so execute the mobile implementation exactly once per
# Streamlit script run via importlib reload/import semantics. This avoids runpy
# while preserving correct rerun behavior.

import importlib
import sys
from pathlib import Path

import streamlit as st


# Streamlit Cloud can execute the entrypoint with the repository root on
# sys.path but without this script's directory. The mobile implementation uses
# sibling-module imports (decision_source, forecast_source, live_sources, ...),
# so make the canonical apps directory explicit before importing it. This is
# deterministic and does not depend on the host's Python launcher semantics.
APP_DIR = Path(__file__).resolve().parent
APP_DIR_STR = str(APP_DIR)
if APP_DIR_STR not in sys.path:
    sys.path.insert(0, APP_DIR_STR)

MODULE_NAME = "gold_control_mobile_v1"
if MODULE_NAME in sys.modules:
    mobile_app = importlib.reload(sys.modules[MODULE_NAME])
else:
    mobile_app = importlib.import_module(MODULE_NAME)

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
