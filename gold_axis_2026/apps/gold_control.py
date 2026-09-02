from __future__ import annotations

# Canonical Gold Control Streamlit entrypoint.
# Presentation authority: manifest v1.20 / final mobile V2 contract.
# Use normal module import semantics in hosted Streamlit. This deliberately
# avoids runpy so deployment errors point to the real application line.

import streamlit as st

import gold_control_mobile_v1  # noqa: F401

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
