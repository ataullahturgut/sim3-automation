from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from decision_source import fetch_current_decision_state
from live_sources import fetch_gvz_history, fetch_gvz_latest, fetch_xau_history, fetch_xau_spot
from piyasa_contract import filter_history_timeframe, gvz_regime, latest_completed_daily_row, price_delta

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
      :root { --navy:#082743; --gold:#e2a531; --ink:#10233e; --muted:#63718a; }
      .block-container {padding-top:.8rem; padding-bottom:3.5rem; max-width:940px;}
      h1,h2,h3 {color:var(--ink);}
      .gc-brand {font-size:1.55rem;font-weight:800;letter-spacing:.02em;color:var(--ink);margin-bottom:.1rem;}
      .gc-brand span {color:var(--gold);font-weight:650;font-size:.78rem;display:block;letter-spacing:.11em;}
      .market-hero {background:var(--navy);color:white;border-radius:18px;padding:22px 24px;margin:10px 0 16px 0;}
      .market-kicker {font-size:.77rem;opacity:.72;letter-spacing:.06em;text-transform:uppercase;}
      .market-price {font-size:2.25rem;font-weight:760;line-height:1.15;margin:.25rem 0;}
      .market-meta {font-size:.82rem;opacity:.78;line-height:1.45;}
      .delta-pos {color:#4fd17b;font-weight:700;}
      .delta-neg {color:#ff6b72;font-weight:700;}
      .delta-flat {color:#d9e2ec;font-weight:700;}
      .decision-strip {border:1px solid rgba(8,39,67,.14);border-left:4px solid var(--gold);border-radius:12px;padding:13px 15px;margin:.8rem 0;background:#fff;}
      .decision-strip .title {font-size:.76rem;color:var(--muted);font-weight:700;letter-spacing:.04em;}
      .decision-strip .value {font-size:1.15rem;color:var(--ink);font-weight:760;margin-top:.2rem;}
      .decision-strip .meta {font-size:.8rem;color:var(--muted);margin-top:.25rem;}
      .sourcebox {font-size:.78rem;color:var(--muted);margin-top:-4px;margin-bottom:8px;line-height:1.4;}
      div[data-testid="stMetric"] {border:1px solid rgba(8,39,67,.12);border-radius:14px;padding:12px;background:white;}
      div[data-baseweb="tab-list"] {gap:.12rem;}
      button[data-baseweb="tab"] {padding-left:.65rem;padding-right:.65rem;}
      .stAlert {border-radius:12px;}
      @media (max-width:640px) {
        .block-container {padding-left:.65rem;padding-right:.65rem;padding-top:.5rem;}
        .market-hero {padding:18px 17px;border-radius:15px;}
        .market-price {font-size:1.9rem;}
        h1 {font-size:1.5rem !important;}
        h2 {font-size:1.2rem !important;}
        button[data-baseweb="tab"] {padding-left:.38rem;padding-right:.38rem;font-size:.77rem;}
        div[data-testid="stMetricValue"] {font-size:1.18rem;}
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


@st.cache_data(ttl=30, show_spinner=False)
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


def fmt_number(value, digits: int = 2) -> str:
    try:
        return f"{float(value):,.{digits}f}"
    except (TypeError, ValueError):
        return "N/A" if value is None else str(value)


def fmt_ts(value) -> str:
    if not value:
        return "N/A"
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return str(value)
    return ts.strftime("%d %b %Y %H:%M UTC")


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


def safe_xau_history() -> tuple[pd.DataFrame, dict, str | None]:
    try:
        frame, meta = live_xau_history()
        return frame, meta, None
    except Exception as exc:
        return pd.DataFrame(), {}, f"{type(exc).__name__}: {exc}"


def safe_gvz_history() -> tuple[pd.DataFrame, str | None]:
    try:
        return live_gvz_history(), None
    except Exception as exc:
        return pd.DataFrame(), f"{type(exc).__name__}: {exc}"


config = load_json(CONFIG)
prov = load_json(PROVENANCE)
historical_replay = load_csv(HISTORY)
scorecard = load_csv(SCORECARD)

db_url = os.environ.get("NEON_DATABASE_URL", "").strip()
if not db_url:
    try:
        db_url = str(st.secrets.get("NEON_DATABASE_URL", "")).strip()
    except Exception:
        db_url = ""

latest: dict = {}
decision_store_error: str | None = None
if db_url:
    try:
        latest = fetch_current_decision_state(db_url) or {}
    except Exception as exc:
        decision_store_error = f"{type(exc).__name__}: {exc}"
else:
    decision_store_error = "NEON_DATABASE_URL_NOT_CONFIGURED"

st.markdown("<div class='gc-brand'>GOLD CONTROL<span>DECISION SYSTEM</span></div>", unsafe_allow_html=True)
st.caption("Piyasa → Görünüm → Tahmin → Geçmiş")

piyasa_tab, gorunum_tab, tahmin_tab, gecmis_tab = st.tabs(["Piyasa", "Görünüm", "Tahmin", "Geçmiş"])

with piyasa_tab:
    st.subheader("Piyasa")
    st.caption("Piyasa şu anda ne durumda? Canlı izleme verisi karar veya tahmin değildir.")

    xau, xau_error = safe_live_xau()
    xhist, xmeta, xhist_error = safe_xau_history()
    gvz_live, gvz_error = safe_live_gvz()

    completed = latest_completed_daily_row(xhist)
    completed_close = None if completed is None else float(completed["close"])
    completed_date = None if completed is None else pd.Timestamp(completed["date"]).date().isoformat()
    delta = price_delta(None if xau is None else xau.get("price"), completed_close)

    if xau:
        live_price = float(xau["price"])
        status = "STALE" if xau.get("stale") else "FRESH"
        if delta is None:
            delta_html = "<span class='delta-flat'>Günlük karşılaştırma mevcut değil</span>"
        else:
            css = "delta-pos" if delta.absolute > 0 else "delta-neg" if delta.absolute < 0 else "delta-flat"
            sign = "+" if delta.absolute > 0 else ""
            delta_html = f"<span class='{css}'>{sign}{delta.absolute:,.2f} USD ({sign}{delta.percent:.2f}%)</span>"
        st.markdown(
            f"""
            <div class='market-hero'>
              <div class='market-kicker'>XAU/USD · indicative live</div>
              <div class='market-price'>{live_price:,.2f} USD</div>
              <div>{delta_html}</div>
              <div class='market-meta'>
                {status} · as-of {fmt_ts(xau.get('as_of'))}<br>
                Source: Gold API · XAU_SPOT_GOLDAPI · display only / no model use
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error(f"Canlı XAU/USD şu anda alınamıyor: {xau_error or 'UNAVAILABLE'}")

    c1, c2 = st.columns(2)
    if completed_close is not None:
        c1.metric("Son tamamlanmış günlük close", f"{completed_close:,.2f} USD")
        c1.markdown(
            f"<div class='sourcebox'>{completed_date} · XAUS daily operational cross-check · benchmark/EOD authority değildir</div>",
            unsafe_allow_html=True,
        )
    else:
        c1.metric("Son tamamlanmış günlük close", "UNAVAILABLE")
        c1.caption(xhist_error or "Tamamlanmış günlük kayıt bulunamadı")

    gvz_cfg = config.get("gvz", {})
    full_max = float(gvz_cfg.get("full_cap_max", 25.9795))
    half_max = float(gvz_cfg.get("half_cap_max", 30.5238))
    if gvz_live:
        gvz_value = float(gvz_live["close"])
        regime = gvz_regime(gvz_value, full_max=full_max, half_max=half_max)
        c2.metric("GVZ", f"{gvz_value:.2f}", regime)
        c2.markdown(
            f"<div class='sourcebox'>{gvz_live.get('as_of','N/A')} · Cboe official daily close · direction üretmez</div>",
            unsafe_allow_html=True,
        )
    else:
        c2.metric("GVZ", "UNAVAILABLE")
        c2.caption(gvz_error or "Cboe kaynağı alınamadı")

    st.markdown("#### XAU günlük görünüm")
    if not xhist.empty:
        timeframe = st.radio(
            "Zaman aralığı",
            ["1A", "3A", "6A", "1Y"],
            horizontal=True,
            label_visibility="collapsed",
            key="piyasa_timeframe",
        )
        chart = filter_history_timeframe(xhist, timeframe)
        st.line_chart(chart.set_index("date")[["close"]], height=300)
        st.caption(
            f"Kaynak: {xmeta.get('source','XAUS history')} · operational daily history / cross-check. "
            "Bu grafik canonical Twelve NY17 EOD veya settlement serisi değildir."
        )
    else:
        st.warning(f"Günlük tarihçe kullanılamıyor: {xhist_error or 'UNAVAILABLE'}")

    if latest:
        evidence = str(latest.get("evidence_class", "UNRESOLVED"))
        st.markdown(
            f"""
            <div class='decision-strip'>
              <div class='title'>SON DISPLAY-ELIGIBLE R4.1 EOD DURUMU</div>
              <div class='value'>{latest.get('classification','UNRESOLVED')}</div>
              <div class='meta'>as-of {latest.get('decision_as_of') or latest.get('date','N/A')} · {evidence}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class='decision-strip'>
              <div class='title'>SON DISPLAY-ELIGIBLE R4.1 EOD DURUMU</div>
              <div class='value'>KANONİK KARAR YOK</div>
              <div class='meta'>Decision Store'da LIVE_PRODUCTION / PROSPECTIVE_SHADOW kayıt yok.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if decision_store_error and decision_store_error != "NEON_DATABASE_URL_NOT_CONFIGURED":
            st.caption(f"Decision Store read: {decision_store_error}")

    st.info("Canlı spot ≠ son EOD karar. Canlı fiyat hiçbir zaman uygulama içinde otomatik yön/pozisyon kararına çevrilmez.")

    if st.button("↻ Piyasa verisini yenile", use_container_width=True):
        live_xau.clear()
        live_gvz.clear()
        live_xau_history.clear()
        live_gvz_history.clear()
        st.rerun()

with gorunum_tab:
    st.subheader("Görünüm")
    st.caption("Sistem neden böyle düşünüyor?")
    if not latest:
        st.warning("KANONİK KARAR YOK — Görünüm ekranı display-eligible Decision Store snapshot olmadan karar üretmez.")
        st.write("Stage 6 status: `BLOCKED_NO_DISPLAY_ELIGIBLE_DECISION_SNAPSHOT`")
    else:
        st.markdown(f"### {latest.get('classification','UNRESOLVED')}")
        st.caption(
            f"Decision Store · {latest.get('evidence_class','UNRESOLVED')} · as-of {latest.get('decision_as_of') or latest.get('date','N/A')}"
        )
        rows = [
            ("Monthly context", latest.get("monthly_direction_3m", "N/A")),
            ("Fast", latest.get("fast_state", "N/A")),
            ("Slow", latest.get("slow_state", "N/A")),
            ("Regime / BOCPD", latest.get("bocpd_context", "N/A")),
            ("Level Emergency", latest.get("level_emergency", "N/A")),
            ("Reversal", latest.get("reversal_emergency", "N/A")),
            ("GVZ risk cap state", latest.get("gvz_cap", "N/A")),
        ]
        st.dataframe(pd.DataFrame(rows, columns=["Katman", "Stored state"]), use_container_width=True, hide_index=True)
        st.info("Action mapping hâlâ NOT_PROVEN_POSITION_MAPPING. BUY/SELL/HOLD/EXIT veya güven yüzdesi üretilmez.")

with tahmin_tab:
    st.subheader("Tahmin")
    st.caption("Gelecek ay için model ne bekliyor?")
    st.warning("NOT_ISSUED_IN_CANONICAL_LEDGER")
    st.write(
        "Canonical H=1 forecast henüz immutable input snapshot + forecast contract ile prospectively yayımlanmadı. "
        "Bu nedenle üretim tahmin değeri, tahmin aralığı veya güven yüzdesi gösterilmiyor."
    )
    st.caption("Stage 7 status: BLOCKED_FORECAST_NOT_ISSUED")

    if not scorecard.empty:
        with st.expander("Araştırma / historical replay model scorecard"):
            st.warning("HISTORICAL_REPLAY — prospective/live performans değildir.")
            st.dataframe(scorecard, use_container_width=True, hide_index=True)

with gecmis_tab:
    st.subheader("Geçmiş")
    st.caption("Sistem geçmişte gerçekten ne yaptı?")
    st.info(
        "Prospective/live forecast ve decision ledger henüz yeterli forward kayıt içermiyor. "
        "Aşağıdaki dosya-backed sonuçlar yalnız HISTORICAL_REPLAY etiketiyle gösterilir."
    )
    if not historical_replay.empty:
        with st.expander("HISTORICAL_REPLAY · production closure geçmişi"):
            st.dataframe(historical_replay.sort_values("month", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.caption("Historical replay artifact bulunamadı.")

st.divider()
with st.expander("Sistem / Veri Sağlığı / Audit"):
    xhist_health, xmeta_health, xhist_health_error = safe_xau_history()
    gvz_history, gvz_history_error = safe_gvz_history()
    xau_health, xau_health_error = safe_live_xau()

    c1, c2, c3 = st.columns(3)
    c1.metric("Gold API live", "PASS" if xau_health else "FAIL")
    c2.metric("XAU 1Y history", "PASS" if not xhist_health.empty else "FAIL")
    c3.metric("GVZ history", "PASS" if not gvz_history.empty else "FAIL")

    if xau_health:
        st.caption(
            f"Gold API: {xau_health.get('status','unknown').upper()} · {fmt_ts(xau_health.get('as_of'))} · "
            f"series={xau_health.get('source_series','N/A')} · role={xau_health.get('use_role','N/A')}"
        )
    elif xau_health_error:
        st.caption(f"Gold API error: {xau_health_error}")

    if not xhist_health.empty:
        st.caption(
            f"XAUS history: rows={len(xhist_health)} · last={pd.Timestamp(xhist_health['date'].max()).date()} · "
            f"source={xmeta_health.get('source','N/A')}"
        )
    elif xhist_health_error:
        st.caption(f"XAUS history error: {xhist_health_error}")

    if not gvz_history.empty:
        st.caption(f"Cboe GVZ: last={pd.Timestamp(gvz_history['date'].max()).date()}")
    elif gvz_history_error:
        st.caption(f"GVZ error: {gvz_history_error}")

    st.write("**Decision Store reader:**", "CONNECTED" if db_url else "NOT_CONFIGURED")
    st.write("**Canonical branch:** `gold-r4-direction-engine`")
    st.write("**R4.1 freeze:**", config.get("freeze_date", "N/A"))
    st.write("**Runtime SHA:**", os.environ.get("GITHUB_SHA", "Platform runtime SHA not exposed"))
    st.write("**VW executable reproduction:**", prov.get("vw_executable_reproduction_status", "N/A"))
    st.caption("Twelve NY17 raw market value is intentionally not rendered here without separately proven display rights.")

    if BLOCKERS.exists():
        with st.expander("Known blockers"):
            st.markdown(BLOCKERS.read_text(encoding="utf-8"))

st.caption("Gold Control · market-first · live ≠ EOD decision · replay ≠ prospective · source lineage explicit")
