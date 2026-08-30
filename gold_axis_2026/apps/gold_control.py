from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
R41 = ROOT / "r4_1"
PREDICTIONS = ROOT / "monthly_predictions_2023_2026.csv"
RESULTS_2026 = ROOT / "results_2026.csv"
LATEST_SIGNAL = R41 / "output" / "latest_signal.json"
CONFIG = R41 / "config" / "frozen_r4_1.json"
BLOCKERS = R41 / "KNOWN_BLOCKERS.md"

st.set_page_config(page_title="Gold Control", page_icon="🟡", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 4rem; max-width: 1100px;}
    div[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.25); border-radius: 14px; padding: 10px;}
    .statebox {padding: 18px; border-radius: 16px; border: 1px solid rgba(128,128,128,.30); margin: 8px 0 18px 0;}
    @media (max-width: 640px) {
      .block-container {padding-left: .75rem; padding-right: .75rem;}
      h1 {font-size: 1.7rem !important;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data
def load_predictions() -> pd.DataFrame:
    if not PREDICTIONS.exists():
        return pd.DataFrame()
    df = pd.read_csv(PREDICTIONS)
    df["month"] = pd.to_datetime(df["month"], errors="coerce")
    return df.sort_values("month")


@st.cache_data
def load_2026() -> pd.DataFrame:
    if not RESULTS_2026.exists():
        return pd.DataFrame()
    df = pd.read_csv(RESULTS_2026)
    df["month"] = pd.to_datetime(df["month"], errors="coerce")
    return df.sort_values("month")


config = load_json(CONFIG)
latest = load_json(LATEST_SIGNAL)
pred = load_predictions()
r2026 = load_2026()

st.title("🟡 Gold Control")
st.caption("XAU/USD • forecast • direction • tactical • emergency • risk • audit")

# Mobile-friendly navigation: Streamlit tabs render horizontally and can be swiped/scrolled on iPhone.
today_tab, signals_tab, data_tab, forecast_tab, history_tab, audit_tab = st.tabs(
    ["Today", "Signals", "Data", "Forecast", "History", "Audit"]
)

with today_tab:
    if not latest:
        st.warning("CANLI SİNYAL HENÜZ BAĞLANMADI. Bu ekran sahte/güncel olmayan değer üretmez.")
        st.write(
            "Uygulama kodu çalışıyor; otomatik günlük XAU/USD + GVZ + monthly-contract pipeline'ı "
            "bağlandıktan sonra bu ekran en son R4.1 durumunu gösterecek."
        )
        if not r2026.empty:
            last = r2026.iloc[-1]
            st.subheader("Son doğrulanmış aylık kayıt")
            c1, c2, c3 = st.columns(3)
            c1.metric("Ay", last["month"].strftime("%Y-%m"))
            c2.metric("Gerçekleşen", f"{last['actual']:,.2f}")
            c3.metric("VW H=1", f"{last['vw_midas_msvr']:,.2f}")
    else:
        final_state = latest.get("classification", "UNRESOLVED")
        st.markdown(f"<div class='statebox'><h3>FINAL STATE</h3><h2>{final_state}</h2></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("XAU/USD", latest.get("close", "N/A"))
        c2.metric("As-of", latest.get("date", "N/A"))
        c1, c2, c3 = st.columns(3)
        c1.metric("VW Forecast", latest.get("vw_forecast_frozen", "N/A"))
        c2.metric("3M Direction", latest.get("monthly_direction_3m", "N/A"))
        c3.metric("GVZ Cap", latest.get("gvz_cap", "N/A"))
        c1, c2 = st.columns(2)
        c1.metric("Fast", latest.get("fast_state", "N/A"))
        c2.metric("Slow", latest.get("slow_state", "N/A"))
        c1, c2 = st.columns(2)
        c1.metric("Level Emergency", latest.get("level_emergency", "N/A"))
        c2.metric("Reversal", latest.get("reversal_emergency", "N/A"))

with signals_tab:
    st.subheader("Frozen R4.1 signal contract")
    tactical = config.get("tactical", {})
    emergency = config.get("emergency", {})
    gvz = config.get("gvz", {})
    rows = [
        ("Core price", config.get("core", {}).get("price_model", "N/A")),
        ("Core direction", config.get("core", {}).get("direction_model", "N/A")),
        ("Fast", f"SMA{tactical.get('fast_sma_days','?')} / persistence {tactical.get('fast_persistence_days','?')} days"),
        ("Slow", f"SMA{tactical.get('slow_sma_weeks','?')} completed weeks / persistence {tactical.get('slow_persistence_weeks','?')} weeks"),
        ("Level Emergency", f"±{100*emergency.get('level_threshold_abs',0):.1f}% vs frozen monthly VW"),
        ("Reversal Emergency", f"±{100*emergency.get('reversal_threshold_abs',0):.1f}% from running extreme • {emergency.get('reversal_role','N/A')}"),
        ("GVZ normal cap max", gvz.get("full_cap_max", "N/A")),
        ("GVZ elevated cap max", gvz.get("half_cap_max", "N/A")),
        ("BOCPD", config.get("bocpd", {}).get("role", "N/A")),
        ("Macro Event", config.get("macro_event_down", {}).get("status", "N/A")),
    ]
    st.dataframe(pd.DataFrame(rows, columns=["Layer", "Frozen rule/status"]), use_container_width=True, hide_index=True)

with data_tab:
    st.subheader("Verified repository data")
    st.caption("Bu sekme yalnız GitHub branch'inde bulunan veri dosyalarını gösterir.")
    if pred.empty:
        st.info("monthly_predictions_2023_2026.csv bulunamadı.")
    else:
        view = pred[[c for c in ["month", "actual", "rw", "ma3", "vw_midas_msvr", "causal_patch_transformer"] if c in pred.columns]].copy()
        view = view.set_index("month")
        st.line_chart(view)
        with st.expander("Ham aylık tablo"):
            st.dataframe(pred.sort_values("month", ascending=False), use_container_width=True, hide_index=True)

with forecast_tab:
    st.subheader("H=1 monthly forecast audit")
    if pred.empty:
        st.info("Forecast dosyası bulunamadı.")
    else:
        models = {
            "Random Walk": "rw_ape",
            "3M Momentum/MA3": "ma3_ape",
            "VW-MIDAS-MSVR": "vw_midas_msvr_ape",
            "Causal Patch": "causal_patch_transformer_ape",
        }
        summary = []
        for name, col in models.items():
            if col in pred.columns:
                x = pd.to_numeric(pred[col], errors="coerce").dropna()
                if not x.empty:
                    summary.append({"Model": name, "MAPE %": x.mean(), "Median APE %": x.median(), "N": len(x)})
        st.dataframe(pd.DataFrame(summary).sort_values("MAPE %"), use_container_width=True, hide_index=True)
        if not pred.empty:
            show = pred[[c for c in ["month", "actual", "vw_midas_msvr", "causal_patch_transformer", "rw", "ma3"] if c in pred.columns]].tail(18)
            st.line_chart(show.set_index("month"))

with history_tab:
    st.subheader("2026 verified monthly replay history")
    if r2026.empty:
        st.info("results_2026.csv bulunamadı.")
    else:
        st.dataframe(r2026.sort_values("month", ascending=False), use_container_width=True, hide_index=True)
        mape_cols = [c for c in ["rw_ape", "ma3_ape", "vw_midas_msvr_ape", "axis3_patch_transformer_ape"] if c in r2026.columns]
        if mape_cols:
            st.bar_chart(r2026.set_index("month")[mape_cols])

with audit_tab:
    st.subheader("Model / data audit")
    c1, c2 = st.columns(2)
    c1.metric("Branch", "gold-r4-direction-engine")
    c2.metric("Freeze date", config.get("freeze_date", "N/A"))
    st.write("**Repository:** `ataullahturgut/sim3-automation`")
    st.write("**Path:** `gold_axis_2026/r4_1/`")
    st.write("**Runtime SHA:**", os.environ.get("GITHUB_SHA", "Platform runtime SHA not exposed"))
    st.json(config)
    if BLOCKERS.exists():
        st.subheader("Known blockers")
        st.markdown(BLOCKERS.read_text(encoding="utf-8"))

st.divider()
st.caption("Gold Control • GitHub is source of truth • 2026-derived threshold tuning is prohibited")
