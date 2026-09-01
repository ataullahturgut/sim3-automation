from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from decision_source import fetch_current_decision_state
from live_sources import fetch_gvz_history, fetch_gvz_latest, fetch_xau_history, fetch_xau_spot

ROOT = Path(__file__).resolve().parents[1]
R41 = ROOT / "r4_1"
PROD = ROOT / "production_closure"
HISTORY = PROD / "production_history_43.csv"
SCORECARD = PROD / "common_scorecard.csv"
PROVENANCE = PROD / "PROVENANCE.json"
CONFIG = R41 / "config" / "frozen_r4_1.json"
BLOCKERS = R41 / "KNOWN_BLOCKERS.md"

st.set_page_config(page_title="Gold Control", page_icon="🟡", layout="wide")
st.markdown(
    """
    <style>
    .block-container {padding-top: .75rem; padding-bottom: 3rem; max-width: 920px;}
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 14px;
        padding: 10px;
    }
    .decisionbox {
        padding: 16px;
        border-radius: 16px;
        border: 1px solid rgba(128,128,128,.35);
        margin: 6px 0 14px 0;
    }
    .decisionbox .eyebrow {font-size:.78rem; opacity:.72; margin-bottom:2px;}
    .decisionbox .decision {font-size:1.65rem; font-weight:750; line-height:1.15; margin:2px 0 4px 0;}
    .decisionbox .meta {font-size:.82rem; opacity:.78;}
    .sourcebox {font-size:.79rem; opacity:.78; margin-top:-6px; margin-bottom:10px;}
    .sectionnote {font-size:.84rem; opacity:.78;}
    div[data-baseweb="tab-list"] {gap: .15rem;}
    button[data-baseweb="tab"] {padding-left: .65rem; padding-right: .65rem;}
    @media (max-width: 640px) {
        .block-container {padding-left:.65rem; padding-right:.65rem; padding-top:.45rem;}
        h1 {font-size:1.55rem !important; margin-bottom:.15rem !important;}
        h2 {font-size:1.25rem !important;}
        h3 {font-size:1.05rem !important;}
        button[data-baseweb="tab"] {padding-left:.42rem; padding-right:.42rem; font-size:.78rem;}
        div[data-testid="stMetricValue"] {font-size:1.25rem;}
        .decisionbox .decision {font-size:1.45rem;}
    }
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


def fmt_number(value, digits: int = 2) -> str:
    try:
        return f"{float(value):,.{digits}f}"
    except (TypeError, ValueError):
        return "N/A" if value is None else str(value)


def show_decision_box(classification: str, as_of: str, note: str) -> None:
    st.markdown(
        f"""
        <div class='decisionbox'>
          <div class='eyebrow'>SON ÜRETİLMİŞ R4.1 EOD KARARI</div>
          <div class='decision'>{classification}</div>
          <div class='meta'>as-of: {as_of} · {note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


config = load_json(CONFIG)
prov = load_json(PROVENANCE)

decision_store_error = None
db_url = os.environ.get("NEON_DATABASE_URL", "").strip()
if not db_url:
    try:
        db_url = str(st.secrets.get("NEON_DATABASE_URL", "")).strip()
    except Exception:
        db_url = ""

if db_url:
    try:
        latest = fetch_current_decision_state(db_url) or {}
    except Exception as exc:
        latest = {}
        decision_store_error = f"{type(exc).__name__}: {exc}"
else:
    latest = {}
    decision_store_error = "NEON_DATABASE_URL_NOT_CONFIGURED"

history = load_csv(HISTORY)
scorecard = load_csv(SCORECARD)

st.title("🟡 Gold Control")
st.caption("Karar → gerekçe → model → veri")

now_tab, signals_tab, model_tab, data_tab = st.tabs(["Şimdi", "Sinyaller", "Model", "Veri"])

with now_tab:
    # The first mobile screen answers one question: what is the latest valid system state?
    if latest:
        evidence = str(latest.get("evidence_class", "UNRESOLVED"))
        if evidence == "LIVE_PRODUCTION":
            decision_note = "Decision Store · LIVE_PRODUCTION · canlı spot değildir"
        else:
            decision_note = "Decision Store · PROSPECTIVE_SHADOW · canlı üretim kararı değildir"
        show_decision_box(
            str(latest.get("classification", "UNRESOLVED")),
            str(latest.get("date", "N/A")),
            decision_note,
        )
    else:
        show_decision_box(
            "KANONİK KARAR YOK",
            "N/A",
            "Decision Store'da LIVE_PRODUCTION / PROSPECTIVE_SHADOW kayıt yok",
        )
        if decision_store_error:
            st.caption(f"Decision Store: {decision_store_error}")
        st.warning("Canlı XAU fiyatından otomatik LONG/EXIT kararı türetilmiyor.")

    xau, xau_error = safe_live_xau()
    gvz_live, gvz_error = safe_live_gvz()

    c1, c2 = st.columns(2)
    if xau:
        c1.metric("XAU/USD spot", fmt_number(xau.get("price")))
        xau_status = "STALE" if xau.get("stale") else str(xau.get("status", "unknown")).upper()
        c1.markdown(
            f"<div class='sourcebox'>{xau_status} · {xau.get('as_of','N/A')}<br>{xau.get('source','N/A')} · indicative</div>",
            unsafe_allow_html=True,
        )
    else:
        c1.metric("XAU/USD spot", "UNAVAILABLE")
        c1.caption(xau_error or "Kaynak hatası")

    if gvz_live:
        gvz_value = float(gvz_live["close"])
        c2.metric("GVZ", f"{gvz_value:.2f}")
        c2.markdown(
            f"<div class='sourcebox'>{gvz_live.get('as_of','N/A')} · Cboe daily close</div>",
            unsafe_allow_html=True,
        )
    else:
        gvz_value = None
        c2.metric("GVZ", "UNAVAILABLE")
        c2.caption(gvz_error or "Kaynak hatası")

    st.markdown("#### Kararı oluşturan çekirdek durum")
    if latest:
        c1, c2 = st.columns(2)
        c1.metric("Aylık yön", latest.get("monthly_direction_3m", "N/A"))
        c2.metric("VW aylık referans", fmt_number(latest.get("vw_forecast_frozen")))
        c1, c2 = st.columns(2)
        c1.metric("Fast", latest.get("fast_state", "N/A"))
        c2.metric("Slow", latest.get("slow_state", "N/A"))
        c1, c2 = st.columns(2)
        c1.metric("Emergency", latest.get("level_emergency", "N/A"))
        c2.metric("Reversal", latest.get("reversal_emergency", "N/A"))
        c1, c2 = st.columns(2)
        c1.metric("GVZ cap", latest.get("gvz_cap", "N/A"))
        c2.metric("R4.1 EOD close", fmt_number(latest.get("close")))
    elif not history.empty:
        last = history.iloc[-1]
        st.info("Canlı karar yok. Aşağıdaki değerler yalnız son production-closure model kaydıdır.")
        c1, c2 = st.columns(2)
        c1.metric("Son değerlendirme ayı", last["month"].strftime("%Y-%m"))
        c2.metric("Gerçekleşen", fmt_number(last.get("actual")))
        c1, c2 = st.columns(2)
        c1.metric("VW audited reference", fmt_number(last.get("vw")))
        c2.metric("Patch executable", fmt_number(last.get("patch_r1")))

    if gvz_value is not None:
        gvz_cfg = config.get("gvz", {})
        full_max = float(gvz_cfg.get("full_cap_max", 25.9795))
        half_max = float(gvz_cfg.get("half_cap_max", 30.5238))
        if gvz_value <= full_max:
            st.success("GVZ rejimi: normal · risk cap 100%")
        elif gvz_value <= half_max:
            st.warning("GVZ rejimi: elevated · risk cap 50%")
        else:
            st.error("GVZ rejimi: panic · risk cap 25%")

    if st.button("↻ Canlı veriyi yenile", use_container_width=True):
        live_xau.clear()
        live_gvz.clear()
        live_xau_history.clear()
        live_gvz_history.clear()
        st.rerun()

    st.caption("Spot izleme verisidir. Son EOD kararının yerine geçmez.")

with signals_tab:
    st.subheader("Sinyal katmanları")
    st.caption("Bu ekran 'karar neden böyle?' sorusunu cevaplar. Frozen kural detayları aşağıdaki açılır bölümde tutulur.")

    signal_rows = []
    if latest:
        signal_rows = [
            ("CORE / 3M", latest.get("monthly_direction_3m", "N/A"), "Aylık ana yön prior"),
            ("Fast Tactical", latest.get("fast_state", "N/A"), "Kısa vadeli teyit"),
            ("Slow Tactical", latest.get("slow_state", "N/A"), "Daha yavaş trend teyidi"),
            ("Level Emergency", latest.get("level_emergency", "N/A"), "Frozen VW seviyesinden sapma"),
            ("Reversal", latest.get("reversal_emergency", "N/A"), "Koşullu reversal alarmı"),
            ("GVZ", latest.get("gvz_cap", "N/A"), "Pozisyon/risk tavanı"),
        ]
        st.dataframe(
            pd.DataFrame(signal_rows, columns=["Katman", "Son durum", "Rol"]),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(f"R4.1 stored state as-of: {latest.get('date','N/A')} · evidence: {latest.get('evidence_class','N/A')}")
    else:
        st.warning("Decision Store’da display-eligible karar yok. HISTORICAL_REPLAY canlı state olarak gösterilmez.")

    with st.expander("Frozen R4.1 kuralları"):
        tactical = config.get("tactical", {})
        emergency = config.get("emergency", {})
        gvz = config.get("gvz", {})
        rows = [
            ("Price reference", f"{prov.get('audited_shadow_reference', 'N/A')} — audited shadow/reference"),
            ("Executable point forecast", prov.get("temporary_executable_point_forecast", "N/A")),
            ("Core direction", config.get("core", {}).get("direction_model", "N/A")),
            ("Fast", f"SMA{tactical.get('fast_sma_days','?')} / {tactical.get('fast_persistence_days','?')} day persistence"),
            ("Slow", f"SMA{tactical.get('slow_sma_weeks','?')} completed weeks / {tactical.get('slow_persistence_weeks','?')} week persistence"),
            ("Level Emergency", f"±{100*emergency.get('level_threshold_abs',0):.1f}% vs frozen monthly VW"),
            ("Reversal Emergency", f"±{100*emergency.get('reversal_threshold_abs',0):.1f}% from running extreme · {emergency.get('reversal_role','N/A')}"),
            ("GVZ normal cap max", gvz.get("full_cap_max", "N/A")),
            ("GVZ elevated cap max", gvz.get("half_cap_max", "N/A")),
            ("BOCPD", config.get("bocpd", {}).get("role", "N/A")),
            ("Macro Event", config.get("macro_event_down", {}).get("status", "N/A")),
        ]
        st.dataframe(pd.DataFrame(rows, columns=["Katman", "Frozen rule/status"]), use_container_width=True, hide_index=True)

with model_tab:
    st.subheader("Aylık tahmin modeli")
    st.caption("Bu ekran H=1 modelinin ne söylediğini ve geçmişte nasıl performans verdiğini gösterir; execution sinyali değildir.")

    c1, c2 = st.columns(2)
    c1.metric("Analytical reference", prov.get("audited_shadow_reference", "N/A"))
    c2.metric("Executable fallback", prov.get("temporary_executable_point_forecast", "N/A"))

    aug_fc = prov.get("august_2026_patch_operational_forecast")
    if aug_fc is not None:
        st.info(
            f"Ağustos 2026 Patch operational forecast: {fmt_number(aug_fc)} · origin {prov.get('august_2026_patch_origin_date','N/A')}"
        )

    st.markdown("#### Production scorecard · 2023-01 → 2026-07")
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
        st.markdown("#### Son 18 ay")
        st.line_chart(history.tail(18).set_index("month")[["actual", "vw", "patch_r1", "mom", "rw"]])

        r2026 = history[history["month"].dt.year == 2026].copy()
        with st.expander("2026 aylık replay ve hata detayları"):
            st.dataframe(r2026.sort_values("month", ascending=False), use_container_width=True, hide_index=True)
            if not r2026.empty:
                st.bar_chart(r2026.set_index("month")[["vw_ape", "patch_r1_ape", "mom_ape", "rw_ape"]])

        with st.expander("Tüm production-history ham tablosu"):
            st.dataframe(history.sort_values("month", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.error("production_history_43.csv bulunamadı.")

with data_tab:
    st.subheader("Veri ve sağlık")
    st.caption("Bu ekran yalnız uygulamaya gerçekten bağlı kaynakları gösterir. Backend/Neon'daki bir seri UI'ya bağlanmadıysa burada canlıymış gibi gösterilmez.")

    try:
        xh, xmeta = live_xau_history()
        c1, c2 = st.columns(2)
        c1.metric("XAU runtime", "PASS")
        c2.metric("Son günlük tarih", str(xmeta.get("as_of", "N/A")))
        st.caption(f"Kaynak: {xmeta.get('source','XAUS')} · günlük cross-check, benchmark değildir")
        st.line_chart(xh.tail(120).set_index("date")[["close"]])
        with st.expander("XAU son günlük kayıtlar"):
            st.dataframe(xh.tail(60).sort_values("date", ascending=False), use_container_width=True, hide_index=True)
    except Exception as exc:
        st.error(f"XAU/USD günlük seri alınamadı: {type(exc).__name__}: {exc}")

    try:
        gh = live_gvz_history()
        c1, c2 = st.columns(2)
        c1.metric("GVZ runtime", "PASS")
        c2.metric("Son günlük tarih", str(gh["date"].max()) if not gh.empty else "N/A")
        st.caption("Kaynak: Cboe Gold ETF Volatility Index daily history")
        st.line_chart(gh.tail(120).set_index("date")[["close"]])
        with st.expander("GVZ son günlük kayıtlar"):
            st.dataframe(gh.tail(60).sort_values("date", ascending=False), use_container_width=True, hide_index=True)
    except Exception as exc:
        st.error(f"GVZ günlük seri alınamadı: {type(exc).__name__}: {exc}")

    if db_url:
        st.success("Neon Decision Store reader: CONNECTED · yalnız LIVE_PRODUCTION / PROSPECTIVE_SHADOW okunur")
    else:
        st.warning("Neon Decision Store reader: NOT_CONFIGURED · NEON_DATABASE_URL uygulama ortamında yok")
    st.info("Diğer makro/vendor serileri backend katmanındadır. UI'ya sorgu bağlantısı kurulmadan health PASS gösterilmeyecek.")

    with st.expander("Audit / provenance"):
        c1, c2 = st.columns(2)
        c1.metric("Branch", "gold-r4-direction-engine")
        c2.metric("R4.1 freeze", config.get("freeze_date", "N/A"))
        st.write("**Repository:** `ataullahturgut/sim3-automation`")
        st.write("**Production package:**", prov.get("source_package", "N/A"))
        st.write("**Production package SHA256:**", prov.get("source_package_sha256", "N/A"))
        st.write("**VW executable reproduction:**", prov.get("vw_executable_reproduction_status", "N/A"))
        st.write("**Runtime SHA:**", os.environ.get("GITHUB_SHA", "Platform runtime SHA not exposed"))
        st.json(prov)
        st.json(config)

    if BLOCKERS.exists():
        with st.expander("Known blockers"):
            st.markdown(BLOCKERS.read_text(encoding="utf-8"))

st.divider()
st.caption("Gold Control · karar odaklı mobil görünüm · live ≠ EOD signal · lineage açık")
