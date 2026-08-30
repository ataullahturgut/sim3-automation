from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
R41 = ROOT / "r4_1"
PROD = ROOT / "production_closure"
HISTORY = PROD / "production_history_43.csv"
SCORECARD = PROD / "common_scorecard.csv"
PROVENANCE = PROD / "PROVENANCE.json"
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
    @media (max-width: 640px) {.block-container {padding-left: .75rem; padding-right: .75rem;} h1 {font-size: 1.7rem !important;}}
    </style>
    """,
    unsafe_allow_html=True,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "month" in df.columns:
        df["month"] = pd.to_datetime(df["month"], errors="coerce")
        df = df.sort_values("month")
    return df


config = load_json(CONFIG)
prov = load_json(PROVENANCE)
latest = load_json(LATEST_SIGNAL)
history = load_csv(HISTORY)
scorecard = load_csv(SCORECARD)

st.title("🟡 Gold Control")
st.caption("Production-closure lineage • XAU/USD monthly forecast • R4.1 signals • audit")

today_tab, signals_tab, data_tab, forecast_tab, history_tab, audit_tab = st.tabs(
    ["Today", "Signals", "Data", "Forecast", "History", "Audit"]
)

with today_tab:
    if not latest:
        st.warning("CANLI SİNYAL HENÜZ BAĞLANMADI. Eski veriyi bugünkü sinyal gibi göstermiyoruz.")
        st.caption("Aşağıdaki değerler canlı spot/kapanış değil; final production-closure değerlendirme serisindeki son tamamlanmış aylık kayıttır.")
        if not history.empty:
            last = history.iloc[-1]
            st.subheader("Son production-closure aylık kayıt")
            c1, c2 = st.columns(2)
            c1.metric("Değerlendirme ayı", last["month"].strftime("%Y-%m"))
            c2.metric("Aylık gerçekleşen (evaluation actual)", f"{last['actual']:,.2f}")
            c1, c2 = st.columns(2)
            c1.metric("VW audited shadow/reference", f"{last['vw']:,.2f}")
            c2.metric("Patch R1 executable fallback", f"{last['patch_r1']:,.2f}")
            if prov.get("august_2026_patch_operational_forecast") is not None:
                st.info(
                    "Ağustos 2026 executable Patch forecast: "
                    f"{prov['august_2026_patch_operational_forecast']:,.2f} "
                    f"(origin {prov.get('august_2026_patch_origin_date', 'N/A')})."
                )
    else:
        final_state = latest.get("classification", "UNRESOLVED")
        st.markdown(f"<div class='statebox'><h3>FINAL STATE</h3><h2>{final_state}</h2></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("XAU/USD EOD", latest.get("close", "N/A"))
        c2.metric("As-of", latest.get("date", "N/A"))
        c1, c2, c3 = st.columns(3)
        c1.metric("VW frozen monthly", latest.get("vw_forecast_frozen", "N/A"))
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
        ("Price reference", prov.get("audited_shadow_reference", "N/A") + " — audited shadow/reference"),
        ("Executable point forecast", prov.get("temporary_executable_point_forecast", "N/A")),
        ("Core direction", config.get("core", {}).get("direction_model", "N/A")),
        ("Fast", f"SMA{tactical.get('fast_sma_days','?')} / {tactical.get('fast_persistence_days','?')} day persistence"),
        ("Slow", f"SMA{tactical.get('slow_sma_weeks','?')} completed weeks / {tactical.get('slow_persistence_weeks','?')} week persistence"),
        ("Level Emergency", f"±{100*emergency.get('level_threshold_abs',0):.1f}% vs frozen monthly VW"),
        ("Reversal Emergency", f"±{100*emergency.get('reversal_threshold_abs',0):.1f}% from running extreme • {emergency.get('reversal_role','N/A')}"),
        ("GVZ normal cap max", gvz.get("full_cap_max", "N/A")),
        ("GVZ elevated cap max", gvz.get("half_cap_max", "N/A")),
        ("BOCPD", config.get("bocpd", {}).get("role", "N/A")),
        ("Macro Event", config.get("macro_event_down", {}).get("status", "N/A")),
    ]
    st.dataframe(pd.DataFrame(rows, columns=["Layer", "Frozen rule/status"]), use_container_width=True, hide_index=True)

with data_tab:
    st.subheader("Authoritative production-closure data")
    st.caption("Kaynak: GOLD_H1_R1_STAGE9B_11_PRODUCTION_CLOSURE_V1. Legacy SIM3 experimental CSV'leri bu ekranda kullanılmaz.")
    if history.empty:
        st.error("production_history_43.csv bulunamadı.")
    else:
        view = history.set_index("month")[["actual", "vw", "patch_r1", "mom", "rw"]]
        st.line_chart(view)
        with st.expander("Ham production-history tablosu"):
            st.dataframe(history.sort_values("month", ascending=False), use_container_width=True, hide_index=True)

with forecast_tab:
    st.subheader("H=1 production scorecard • 2023-01 → 2026-07")
    if scorecard.empty:
        st.error("common_scorecard.csv bulunamadı.")
    else:
        labels = {
            "vw": "VW audited shadow/reference",
            "patch_r1": "Causal PatchTST R1",
            "repro_svr": "Repro SVR diagnostic",
            "mom": "3M Momentum",
            "rw": "Random Walk",
        }
        show = scorecard.copy()
        show["model"] = show["model"].map(labels).fillna(show["model"])
        st.dataframe(show, use_container_width=True, hide_index=True)
        if not history.empty:
            st.line_chart(history.tail(18).set_index("month")[["actual", "vw", "patch_r1", "mom", "rw"]])

with history_tab:
    st.subheader("2026 production-closure monthly replay")
    if history.empty:
        st.error("Production history unavailable.")
    else:
        r2026 = history[history["month"].dt.year == 2026].copy()
        st.dataframe(r2026.sort_values("month", ascending=False), use_container_width=True, hide_index=True)
        st.bar_chart(r2026.set_index("month")[["vw_ape", "patch_r1_ape", "mom_ape", "rw_ape"]])

with audit_tab:
    st.subheader("Model / data audit")
    c1, c2 = st.columns(2)
    c1.metric("Branch", "gold-r4-direction-engine")
    c2.metric("R4.1 freeze date", config.get("freeze_date", "N/A"))
    st.write("**Repository:** `ataullahturgut/sim3-automation`")
    st.write("**Production package:**", prov.get("source_package", "N/A"))
    st.write("**Production package SHA256:**", prov.get("source_package_sha256", "N/A"))
    st.write("**VW executable reproduction:**", prov.get("vw_executable_reproduction_status", "N/A"))
    st.write("**Runtime SHA:**", os.environ.get("GITHUB_SHA", "Platform runtime SHA not exposed"))
    st.json(prov)
    st.json(config)
    if BLOCKERS.exists():
        st.subheader("Known blockers")
        st.markdown(BLOCKERS.read_text(encoding="utf-8"))

st.divider()
st.caption("Gold Control • production-closure lineage pinned • no silent legacy-data substitution")
