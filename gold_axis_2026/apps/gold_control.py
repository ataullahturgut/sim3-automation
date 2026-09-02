from __future__ import annotations

# Canonical Gold Control Streamlit entrypoint.
# Presentation authority: manifest v1.20 / final mobile V2 contract.
# The implementation remains in gold_control_mobile_v1.py to preserve its
# audited candidate history while this file stays the deployment entrypoint.

import runpy
from pathlib import Path

import streamlit as st


APP = Path(__file__).with_name("gold_control_mobile_v1.py")
if not APP.exists():
    raise RuntimeError("GOLD_CONTROL_MOBILE_V2_ENTRYPOINT_NOT_FOUND")

runpy.run_path(str(APP), run_name="__main__")

# The implementation-level CSS predates the dedicated main-nav radio key and
# intentionally used a broad stRadio selector. Canonical entrypoint scopes the
# fixed positioning to gc_main_nav so timeframe radios remain normal controls.
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
