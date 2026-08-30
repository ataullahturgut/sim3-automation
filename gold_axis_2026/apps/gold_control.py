from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from live_sources import fetch_gvz_history, fetch_gvz_latest, fetch_xau_history, fetch_xau_spot

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
    .sourcebox {font-size:.80rem; opacity:.78; margin-top:-7px; margin-bottom:12px;}
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


@st.cache_data(ttl=60, show_spinner=False)
def live_xau() -> dict:
    return fetch_xau_spot()


@st.cache_data(ttl=1800, show_spinner=False)
def live_gvz() -> dict:
    return fetch_gvz_latest()


@st.cache_data(ttl=1800, show_spinner=False)
def live_xau_history() -> tuple[pd.DataFrame, dict]:
    return fetch_xau_history()


@st.cache_data(ttl=3600, show_spinner=False)
def live_gvz_history() -> pd.DataFrame:
    return fetch_gvz_history()


def safe_live_xau() -> tuple[dict | None, str | None]:
    try:
        return live_xau(), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def safe_live_gvz() -> tuple[dict | None, str | None]:
    try:
        return live_gvz(), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


config = load_json(CONFIG)
prov = load_json(PROVENANCE)
latest = load_json(LATEST_SIGNAL)
history = load_csv(HISTORY)
scorecard = load_csv(SCORECARD)

st.title("🟡 Gold Control")
st.caption("Live market data • production-closure forecast lineage • R4.1 signal audit")

if st.button("↻ Canlı veriyi yenile", use_container_width=True):
    live_xau.clear()
    live_gvz.clear()
    live_xau_history.clear()
    live_gvz_history.clear()
    st.rerun()

today_tab, signals_tab, data_tab, forecast_tab, history_tab, audit_tab = st.tabs(
    ["Today", "Signals", "Data", "Forecast", "History", "Audit"]
)

with today_tab:
    xau, xau_error = safe_live_xau()
    gvz_live, gvz_error = safe_live_gvz()

    st.subheader("Canlı piyasa verisi")
    c1, c2 = st.columns(2)
    if xau:
        c1.metric("XAU/USD indicative spot", f"{xau['price']:,.2f}")
        xau_status = "STALE" if xau.get("stale") else str(xau.get("status", "unknown")).upper()
        c1.markdown(
            f"<div class='sourcebox'>Durum: <b>{xau_status}</b> · as-of: {xau.get('as_of','N/A')}<br>Kaynak: {xau.get('source','N/A')}</div>",
            unsafe_allow_html=True,
        )
        if xau.get("stale"):
            c1.warning("Spot feed stale. R4.1 EOD kararı için kullanılmaz.")
    else:
        c1.metric("XAU/USD indicative spot", "UNAVAILABLE")
        c1.error(f"Canlı spot alınamadı: {xau_error}")

    if gvz_live:
        gvz_value = float(gvz_live["close"])
        c2.metric("GVZ official daily close", f"{gvz_value:.2f}")
        c2.markdown(
            f"<div class='sourcebox'>as-of: {gvz_live.get('as_of','N/A')}<br>Kaynak: Cboe GVZ daily history</div>",
            unsafe_allow_html=True,
        )
        gvz_cfg = config.get("gvz", {})
        full_max = float(gvz_cfg.get("full_cap_max", 25.9795))
        half_max = float(gvz_cfg.get("half_cap_max", 30.5238))
        if gvz_value <= full_max:
            c2.success("R4 GVZ risk cap: 100%")
        elif gvz_value <= half_max:
            c2.warning("R4 GVZ risk cap: 50%")
        else:
            c2.error("R4 GVZ panic cap: 25%")
    else:
        c2.metric("GVZ official daily close", "UNAVAILABLE")
        c2.error(f"GVZ alınamadı: {gvz_error}")

    st.info(
        "Canlı XAU/USD kartı izleme içindir. R4.1'in frozen EOD/next-session execution zincirine, "
        "daily-history lineage doğrulanmadan otomatik olarak bağlanmaz. GVZ kartı Cboe günlük kapanış serisidir."
    )

    if latest:
        final_state = latest.get("classification", "UNRESOLVED")
        st.subheader("Son üretilmiş R4.1 EOD state")
        st.markdown(f"<div class='statebox'><h3>FINAL STATE</h3><h2>{final_state}</h2></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("R4.1 EOD close", latest.get("close", "N/A"))
        c2.metric("R4.1 as-of", latest.get("date", "N/A"))
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
    else:
        st.warning("R4.1 CANLI EOD SİNYAL PIPELINE'I HENÜZ BAĞLANMADI. Canlı fiyatı otomatik sinyal diye göstermiyoruz.")
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
    st.subheader("Canlı / güncel piyasa serileri")
    st.caption("Canlı veri ile production-closure forecast geçmişi ayrı tutulur; sessiz birleştirme yapılmaz.")

    try:
        xh, xmeta = live_xau_history()
        st.write("**XAU/USD daily history**")
        st.caption(f"Kaynak: {xmeta.get('source','XAUS')} · as-of: {xmeta.get('as_of','N/A')}")
        st.line_chart(xh.tail(120).set_index("date")[["close"]])
        with st.expander("XAU/USD son günlük kayıtlar"):
            st.dataframe(xh.tail(60).sort_values("date", ascending=False), use_container_width=True, hide_index=True)
    except Exception as exc:
        st.error(f"XAU/USD günlük seri alınamadı: {type(exc).__name__}: {exc}")

    try:
        gh = live_gvz_history()
        st.write("**GVZ official daily close**")
        st.caption("Kaynak: Cboe Gold ETF Volatility Index (GVZ) daily history")
        st.line_chart(gh.tail(120).set_index("date")[["close"]])
        with st.expander("GVZ son günlük kayıtlar"):
            st.dataframe(gh.tail(60).sort_values("date", ascending=False), use_container_width=True, hide_index=True)
    except Exception as exc:
        st.error(f"GVZ günlük seri alınamadı: {type(exc).__name__}: {exc}")

    st.subheader("Authoritative production-closure forecast data")
    st.caption("Kaynak: GOLD_H1_R1_STAGE9B_11_PRODUCTION_CLOSURE_V1. Legacy SIM3 experimental CSV'leri kullanılmaz.")
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
    st.write("**Live XAU display adapter:** XAUS public API; source/freshness passed through from response")
    st.write("**GVZ live adapter:** Cboe official GVZ daily-history CSV")
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
st.caption("Gold Control • live data lineage explicit • production-closure forecast lineage pinned • no silent substitution")
