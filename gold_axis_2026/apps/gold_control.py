from __future__ import annotations

# Canonical Gold Control Streamlit entrypoint.
# Presentation authority: manifest v1.22 / final mobile V2 contract.
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
    required_exports=(
        "fetch_current_forecast",
        "fetch_forecast_history",
        "fetch_latest_expert_forecasts",
        "fetch_expert_forecast_history",
        "TRACK_MONTH_END",
        "TRACK_EARLY_INDICATIVE",
    ),
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
        "EXPERT_SELECTION_STATUS",
        "AUTO_SELECTOR_STATUS",
        "AUTO_ENSEMBLE_STATUS",
        "EXPERT_DISPLAY_ORDER",
        "MONTH_END_TRACK",
        "EARLY_INDICATIVE_TRACK",
        "arrow_state",
        "classification_label",
        "decision_view_state",
        "deterministic_explanation",
        "display_state",
        "evidence_badge",
        "expert_display_state",
        "forecast_view_state",
        "monthly_intramonth_relation",
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

mobile_app = _load_exact_module(
    "gold_control_mobile_v1",
    APP_DIR / "gold_control_mobile_v1.py",
)

# Presentation overrides use Streamlit 1.63 stable data-testid/data-selected
# attributes verified in the locked Python 3.14 browser runtime. Avoid hashed
# emotion class names and the removed data-baseweb="radio" structure.
st.markdown(
    """
<style>
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stToolbarActions"],
[data-testid="stAppToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeaderActionElements"],
.stAppToolbar,
[class*="viewerBadge"],
[class*="ViewerBadge"]{
 display:none!important;
 visibility:hidden!important;
}
header[data-testid="stHeader"]{
 height:0!important;
 min-height:0!important;
 background:transparent!important;
}
.vg-tooltip,
#vg-tooltip-element,
.vega-embed .vg-tooltip{
 display:none!important;
 visibility:hidden!important;
 pointer-events:none!important;
}
[data-testid="stRadio"]{
 position:static!important;
 left:auto!important;
 right:auto!important;
 bottom:auto!important;
 transform:none!important;
 z-index:auto!important;
 width:auto!important;
 max-width:none!important;
 box-shadow:none!important;
 margin:0!important;
}
.st-key-gc_main_nav [data-testid="stRadio"]{
 position:fixed!important;
 left:.5rem!important;
 right:.5rem!important;
 bottom:max(.45rem,env(safe-area-inset-bottom))!important;
 transform:none!important;
 z-index:9999!important;
 width:auto!important;
 max-width:844px!important;
 margin:0 auto!important;
 background:rgba(255,255,255,.98)!important;
 border:1px solid #e1e7ef!important;
 border-radius:18px!important;
 padding:.30rem!important;
 box-shadow:0 10px 30px rgba(15,39,72,.16)!important;
 overflow:hidden!important;
 backdrop-filter:blur(12px);
}
.st-key-gc_main_nav [data-testid="stRadio"] > [data-testid="stWidgetLabel"]{display:none!important}
.st-key-gc_main_nav [data-testid="stRadioGroup"]{
 display:grid!important;
 grid-template-columns:repeat(4,minmax(0,1fr))!important;
 gap:.20rem!important;
 width:100%!important;
 align-items:stretch!important;
}
.st-key-gc_main_nav label[data-testid="stRadioOption"]{
 margin:0!important;
 padding:0!important;
 min-width:0!important;
 width:100%!important;
 border-radius:13px!important;
 cursor:pointer!important;
}
.st-key-gc_main_nav label[data-testid="stRadioOption"] > div{
 width:100%!important;
 min-width:0!important;
 min-height:50px!important;
 padding:.56rem .16rem!important;
 border-radius:13px!important;
 box-sizing:border-box!important;
 display:flex!important;
 align-items:center!important;
 justify-content:center!important;
}
.st-key-gc_main_nav label[data-testid="stRadioOption"] > div > div{
 width:100%!important;
 min-width:0!important;
 display:flex!important;
 align-items:center!important;
 justify-content:center!important;
 gap:0!important;
}
.st-key-gc_main_nav label[data-testid="stRadioOption"] > div > div > div:first-child{
 display:none!important;
 visibility:hidden!important;
 width:0!important;
 height:0!important;
 min-width:0!important;
 min-height:0!important;
 margin:0!important;
 padding:0!important;
 border:0!important;
 flex:0 0 0!important;
}
.st-key-gc_main_nav label[data-testid="stRadioOption"] [data-testid="stMarkdownContainer"]{
 width:100%!important;
 text-align:center!important;
}
.st-key-gc_main_nav label[data-testid="stRadioOption"] p{
 margin:0!important;
 padding:0!important;
 color:#53657e!important;
 font-size:.76rem!important;
 font-weight:650!important;
 line-height:1.15!important;
 white-space:nowrap!important;
 text-align:center!important;
}
.st-key-gc_main_nav label[data-testid="stRadioOption"][data-selected="true"] > div{
 background:#082a4b!important;
 box-shadow:0 4px 12px rgba(8,42,75,.16)!important;
}
.st-key-gc_main_nav label[data-testid="stRadioOption"][data-selected="true"] p{
 color:#fff!important;
 font-weight:850!important;
}
.st-key-gc_market_range{margin:.10rem 0 .55rem!important;width:100%!important}
.st-key-gc_market_range [data-testid="stRadio"]{
 display:block!important;
 background:#f5f8fb!important;
 border:1px solid #e4eaf1!important;
 border-radius:12px!important;
 padding:.22rem!important;
 width:100%!important;
}
.st-key-gc_market_range [data-testid="stRadio"] > [data-testid="stWidgetLabel"]{display:none!important}
.st-key-gc_market_range [data-testid="stRadioGroup"]{
 display:grid!important;
 grid-template-columns:repeat(4,minmax(0,1fr))!important;
 gap:.18rem!important;
 width:100%!important;
}
.st-key-gc_market_range label[data-testid="stRadioOption"]{
 margin:0!important;
 padding:0!important;
 min-width:0!important;
 width:100%!important;
 border-radius:9px!important;
 cursor:pointer!important;
}
.st-key-gc_market_range label[data-testid="stRadioOption"] > div{
 width:100%!important;
 min-width:0!important;
 min-height:38px!important;
 padding:.38rem .20rem!important;
 border-radius:9px!important;
 box-sizing:border-box!important;
 display:flex!important;
 align-items:center!important;
 justify-content:center!important;
}
.st-key-gc_market_range label[data-testid="stRadioOption"] > div > div{
 width:100%!important;
 min-width:0!important;
 display:flex!important;
 align-items:center!important;
 justify-content:center!important;
 gap:0!important;
}
.st-key-gc_market_range label[data-testid="stRadioOption"] > div > div > div:first-child{
 display:none!important;
 visibility:hidden!important;
 width:0!important;
 height:0!important;
 min-width:0!important;
 min-height:0!important;
 margin:0!important;
 padding:0!important;
 border:0!important;
 flex:0 0 0!important;
}
.st-key-gc_market_range label[data-testid="stRadioOption"] [data-testid="stMarkdownContainer"]{
 width:100%!important;
 text-align:center!important;
}
.st-key-gc_market_range label[data-testid="stRadioOption"] p{
 margin:0!important;
 padding:0!important;
 color:#667790!important;
 font-size:.76rem!important;
 font-weight:700!important;
 white-space:nowrap!important;
 text-align:center!important;
}
.st-key-gc_market_range label[data-testid="stRadioOption"][data-selected="true"] > div{
 background:#082a4b!important;
}
.st-key-gc_market_range label[data-testid="stRadioOption"][data-selected="true"] p{
 color:#fff!important;
 font-weight:850!important;
}
.gc-card:has(> .gc-section-title:only-child){
 padding:.78rem .95rem!important;
 margin:.70rem 0 .18rem!important;
 min-height:0!important;
 border-radius:15px!important;
 box-shadow:0 2px 10px rgba(16,41,75,.025)!important;
}
.gc-card:has(> .gc-section-title:only-child) .gc-section-title{margin-bottom:0!important}
@media(max-width:620px){
 .block-container{
   padding-left:.62rem!important;
   padding-right:.62rem!important;
   padding-top:.20rem!important;
   padding-bottom:7.2rem!important;
 }
 .gc-shell{margin-bottom:.72rem!important;padding-top:.35rem!important;padding-bottom:.72rem!important}
 .gc-pagehead{margin-top:.20rem!important;margin-bottom:.75rem!important}
 .gc-hero{margin-top:.45rem!important;margin-bottom:.80rem!important}
 .gc-grid3{gap:.55rem!important}
 .gc-mini{min-height:92px!important;padding:.72rem .78rem!important}
 .st-key-gc_main_nav [data-testid="stRadio"]{
   left:.42rem!important;
   right:.42rem!important;
   bottom:max(.35rem,env(safe-area-inset-bottom))!important;
 }
 .st-key-gc_main_nav label[data-testid="stRadioOption"] > div{
   min-height:48px!important;
   padding:.50rem .08rem!important;
 }
 .st-key-gc_main_nav label[data-testid="stRadioOption"] p{font-size:.70rem!important}
}
@media(max-width:370px){
 .st-key-gc_main_nav label[data-testid="stRadioOption"] p{font-size:.65rem!important}
 .gc-brand{font-size:1.04rem!important}
}
</style>
    """,
    unsafe_allow_html=True,
)
