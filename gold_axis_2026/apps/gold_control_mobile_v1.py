from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from decision_source import fetch_current_decision_state, fetch_decision_history
from forecast_source import fetch_current_forecast, fetch_forecast_history
from live_sources import fetch_gvz_latest, fetch_xau_history, fetch_xau_spot
from mobile_ui_contract import (
    FINAL_MOCKUP_CONTRACT,
    SCENARIO_STATUS,
    arrow_state,
    classification_label,
    decision_view_state,
    deterministic_explanation,
    display_state,
    evidence_badge,
    forecast_view_state,
)
from piyasa_contract import filter_history_timeframe, gvz_regime, latest_completed_daily_row, price_delta


ROOT = Path(__file__).resolve().parents[1]
R41_CONFIG = ROOT / "r4_1" / "config" / "frozen_r4_1.json"
HISTORICAL_REPLAY = ROOT / "production_closure" / "production_history_43.csv"

PATCH_FORWARD_ID = "CAUSAL_PATCH_R1_REPRO_V1_6"
PATCH_FORWARD_LABEL = "Patch Tahmini (V7)"
PATCH_GEOMETRY = "L=252 / P=21 / D=32"
PATCH_ANCHOR = "XAU/USD 1h · 16:00–17:00 ET"
PATCH_PIT = "Completed-session safe"

st.set_page_config(
    page_title="Gold Control",
    page_icon="🟡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
:root{
 --gc-navy:#082a4b; --gc-navy2:#0d3b66; --gc-gold:#f2ad36; --gc-gold2:#ffd98a;
 --gc-ink:#10294b; --gc-muted:#687995; --gc-line:#e3e9f0; --gc-bg:#f8fafc;
 --gc-green:#14a85a; --gc-red:#e33f50; --gc-blue:#1768d0; --gc-amber:#e79d18;
}
[data-testid="stAppViewContainer"]{
 background:linear-gradient(180deg,#fff 0%,#f8fafc 100%);
 color:var(--gc-ink);
}
.block-container{
 max-width:900px;
 padding-top:.25rem;
 padding-left:.72rem;
 padding-right:.72rem;
 padding-bottom:7.4rem;
}
#MainMenu, footer {visibility:hidden}
[data-testid="stHeader"]{background:transparent;height:.15rem}

.gc-shell{
 display:flex;align-items:center;gap:.65rem;border-bottom:1px solid var(--gc-line);
 padding:.48rem .12rem .85rem;margin-bottom:.82rem;min-height:58px;
}
.gc-menu{font-size:1.45rem;font-weight:800;color:var(--gc-navy);width:34px;text-align:center}
.gc-logo{
 width:43px;height:43px;border:4px solid var(--gc-gold);border-radius:10px;
 transform:rotate(30deg);display:flex;align-items:center;justify-content:center;flex:0 0 auto;
}
.gc-logo b{transform:rotate(-30deg);color:var(--gc-gold);font-size:1rem}
.gc-brand{font-size:1.31rem;font-weight:900;letter-spacing:.02em;line-height:1;color:var(--gc-ink)}
.gc-brand small{display:block;color:var(--gc-gold);letter-spacing:.15em;font-size:.61rem;margin-top:.35rem}

.gc-pagehead{display:flex;justify-content:space-between;align-items:flex-start;gap:.9rem;margin:.30rem 0 .75rem}
.gc-pagehead h2{font-size:1.7rem;margin:0;color:var(--gc-ink);letter-spacing:.01em}
.gc-pagehead p{margin:.32rem 0 0;color:var(--gc-muted);font-size:.91rem;line-height:1.45}
.gc-updated{font-size:.69rem;color:var(--gc-muted);text-align:right;max-width:145px;line-height:1.45}

.gc-hero{
 background:linear-gradient(135deg,#052746 0%,#0b3a65 100%);
 color:#fff;border-radius:20px;padding:1.18rem;margin:.50rem 0 .9rem;
 box-shadow:0 10px 28px rgba(8,42,75,.14);position:relative;overflow:hidden;
}
.gc-hero:after{
 content:"";position:absolute;right:-60px;top:-70px;width:190px;height:190px;
 border:1px solid rgba(255,255,255,.08);border-radius:50%;
}
.gc-hero-layout{display:grid;grid-template-columns:95px minmax(0,1.15fr) minmax(150px,.75fr);gap:1rem;align-items:center}
.gc-hero-icon{
 width:82px;height:82px;border:3px solid var(--gc-gold);border-radius:50%;
 display:flex;align-items:center;justify-content:center;color:var(--gc-gold);
 font-size:2.3rem;font-weight:900;box-shadow:0 0 0 8px rgba(242,173,54,.07);
}
.gc-kicker{font-size:.73rem;letter-spacing:.08em;text-transform:uppercase;opacity:.82;font-weight:850}
.gc-big{font-size:2.65rem;font-weight:900;line-height:1.02;margin:.42rem 0}
.gc-mid{font-size:1.55rem;font-weight:900;line-height:1.15;margin:.35rem 0}
.gc-meta{font-size:.80rem;opacity:.82;line-height:1.5}
.gc-hero-side{border-left:1px solid rgba(255,255,255,.18);padding-left:1rem}
.gc-hero-label{font-size:.75rem;opacity:.72;margin-top:.08rem}
.gc-hero-value{font-size:1.25rem;font-weight:900;margin:.25rem 0 .7rem}
.gc-badge{
 display:inline-block;border:1px solid rgba(255,255,255,.30);border-radius:999px;
 padding:.34rem .66rem;font-weight:850;font-size:.69rem;margin-top:.55rem;
}
.gc-badge-gold{border-color:var(--gc-gold);color:var(--gc-gold)}
.gc-positive{color:var(--gc-green)!important}.gc-negative{color:var(--gc-red)!important}
.gc-warning{color:var(--gc-amber)!important}.gc-blue{color:var(--gc-blue)!important}.gc-muted{color:var(--gc-muted)!important}

.gc-grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.72rem}
.gc-grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.72rem}
.gc-grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.64rem}
.gc-card{
 background:#fff;border:1px solid var(--gc-line);border-radius:16px;padding:.95rem 1rem;
 margin:.62rem 0;box-shadow:0 4px 16px rgba(16,41,75,.035);
}
.gc-mini{
 background:#fff;border:1px solid var(--gc-line);border-radius:15px;padding:.88rem;
 min-height:112px;box-shadow:0 4px 15px rgba(16,41,75,.03);
}
.gc-mini .label{font-size:.69rem;font-weight:850;color:var(--gc-ink);text-transform:uppercase;line-height:1.28}
.gc-mini .value{font-size:1.42rem;font-weight:900;margin:.44rem 0 .2rem;color:var(--gc-ink);word-break:break-word}
.gc-mini .note{font-size:.72rem;color:var(--gc-muted);line-height:1.42}

.gc-section-title{display:flex;align-items:center;gap:.55rem;font-size:.94rem;font-weight:900;color:var(--gc-ink);margin-bottom:.60rem}
.gc-num{
 display:inline-flex;width:27px;height:27px;border-radius:50%;background:var(--gc-navy);color:#fff;
 align-items:center;justify-content:center;font-size:.78rem;font-weight:900;flex:0 0 auto;
}
.gc-row{display:flex;justify-content:space-between;align-items:flex-start;gap:.75rem;padding:.54rem 0;border-bottom:1px solid var(--gc-line);font-size:.87rem}
.gc-row:last-child{border-bottom:none}.gc-value{font-weight:850;text-align:right;word-break:break-word}
.gc-footnote{font-size:.73rem;color:var(--gc-muted);line-height:1.52}
.gc-info{background:#f5f8fc;border:1px solid var(--gc-line);border-radius:14px;padding:.85rem .95rem;color:#445a79;font-size:.79rem;line-height:1.5;margin:.7rem 0}
.gc-note{background:#fffaf0;border:1px solid #f0d8a7;border-radius:14px;padding:.86rem .95rem;color:#6e582b;font-size:.79rem;line-height:1.5;margin:.7rem 0}
.gc-empty{background:#fbfcfe;border:1px dashed #cbd5e1;border-radius:15px;padding:1.05rem;text-align:center;color:var(--gc-muted);margin:.45rem 0}
.gc-empty strong{display:block;color:var(--gc-ink);font-size:.92rem;margin-bottom:.30rem}
.gc-replay{
 background:#f7f9fc;border:1px solid #d9e1ec;border-radius:16px;padding:.95rem 1rem;margin:.70rem 0;
}
.gc-replay-head{display:flex;justify-content:space-between;align-items:center;gap:.7rem;margin-bottom:.55rem}
.gc-replay-head strong{font-size:.92rem;color:var(--gc-ink)}
.gc-replay-pill{font-size:.66rem;font-weight:900;color:#8a5b00;background:#fff3d8;border:1px solid #f1d08d;border-radius:999px;padding:.28rem .55rem}
.gc-modelstrip{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));background:#fff;border:1px solid var(--gc-line);border-radius:16px;margin:.65rem 0;overflow:hidden}
.gc-modelcell{padding:.85rem .9rem;border-right:1px solid var(--gc-line)}
.gc-modelcell:last-child{border-right:none}
.gc-modelcell .label{font-size:.72rem;font-weight:850;color:var(--gc-ink)}
.gc-modelcell .value{font-size:1.18rem;font-weight:900;margin:.30rem 0}
.gc-modelcell .note{font-size:.68rem;color:var(--gc-muted);line-height:1.35}
.gc-metadata{display:grid;grid-template-columns:1fr 1fr;gap:.42rem .8rem}
.gc-meta-item{display:flex;gap:.45rem;align-items:flex-start;font-size:.77rem;color:#405574;line-height:1.42}
.gc-meta-item b{color:var(--gc-ink)}

[data-testid="stVerticalBlockBorderWrapper"]{
 border-color:var(--gc-line)!important;border-radius:16px!important;box-shadow:0 4px 16px rgba(16,41,75,.03)!important;
}
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden}

@media(max-width:620px){
 .block-container{padding-left:.58rem;padding-right:.58rem;padding-bottom:7.2rem}
 .gc-shell{gap:.50rem}.gc-logo{width:39px;height:39px}.gc-brand{font-size:1.16rem}.gc-brand small{font-size:.54rem}
 .gc-pagehead h2{font-size:1.62rem}.gc-pagehead p{font-size:.86rem}.gc-updated{font-size:.64rem;max-width:120px}
 .gc-hero{padding:1.05rem}.gc-hero-layout{grid-template-columns:70px 1fr;gap:.75rem}
 .gc-hero-icon{width:62px;height:62px;font-size:1.8rem}
 .gc-hero-side{grid-column:1/-1;border-left:0;border-top:1px solid rgba(255,255,255,.17);padding-left:0;padding-top:.72rem;display:grid;grid-template-columns:1fr 1fr;gap:.5rem}
 .gc-big{font-size:2rem}.gc-mid{font-size:1.30rem}
 .gc-grid4{grid-template-columns:1fr 1fr}.gc-grid3{grid-template-columns:1fr}.gc-grid2{grid-template-columns:1fr 1fr}
 .gc-modelstrip{grid-template-columns:1fr}.gc-modelcell{border-right:0;border-bottom:1px solid var(--gc-line)}.gc-modelcell:last-child{border-bottom:none}
 .gc-metadata{grid-template-columns:1fr}
 .gc-mini{min-height:102px;padding:.76rem}.gc-mini .value{font-size:1.20rem}
}
@media(max-width:380px){
 .gc-grid2{grid-template-columns:1fr}
}
</style>
    """,
    unsafe_allow_html=True,
)


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if value:
        return value
    try:
        return str(st.secrets.get("NEON_DATABASE_URL", "")).strip()
    except Exception:
        return ""


@st.cache_data(ttl=30, show_spinner=False)
def get_spot():
    return fetch_xau_spot()


@st.cache_data(ttl=1800, show_spinner=False)
def get_xau_history():
    return fetch_xau_history()


@st.cache_data(ttl=1800, show_spinner=False)
def get_gvz():
    return fetch_gvz_latest()


def safe_call(fn, default):
    try:
        return fn()
    except Exception:
        return default


def fmt_num(value: Any, decimals: int = 2, suffix: str = "") -> str:
    try:
        if value is None or pd.isna(value):
            return "—"
        return f"{float(value):,.{decimals}f}{suffix}"
    except Exception:
        return "—"


def fmt_time(value: Any) -> str:
    if value in (None, "", "N/A"):
        return "—"
    try:
        ts = pd.to_datetime(value, utc=True, errors="coerce")
        if pd.isna(ts):
            return str(value)
        return ts.tz_convert("Europe/Istanbul").strftime("%d %b %Y %H:%M")
    except Exception:
        return str(value)


def html_row(label: str, value: str, value_class: str = "") -> str:
    return f"<div class='gc-row'><span>{label}</span><span class='gc-value {value_class}'>{value}</span></div>"


def section_header(number: int, title: str) -> str:
    return f"<div class='gc-section-title'><span class='gc-num'>{number}</span><span>{title}</span></div>"


def empty_html(title: str, subtitle: str) -> str:
    return f"<div class='gc-empty'><strong>{title}</strong>{subtitle}</div>"


def page_head(title: str, subtitle: str, updated: Any = None) -> None:
    updated_text = "Henüz kayıt yok" if updated in (None, "", "N/A") else fmt_time(updated)
    st.markdown(
        f"<div class='gc-pagehead'><div><h2>{title}</h2><p>{subtitle}</p></div>"
        f"<div class='gc-updated'>Son güncelleme:<br>{updated_text}</div></div>",
        unsafe_allow_html=True,
    )


def tone_class(tone: str) -> str:
    return {"positive": "gc-positive", "negative": "gc-negative", "warning": "gc-warning", "shadow": "gc-blue"}.get(tone, "")


def mini_card(label: str, value: str, note: str, value_class: str = "") -> str:
    return (
        "<div class='gc-mini'>"
        f"<div class='label'>{label}</div><div class='value {value_class}'>{value}</div>"
        f"<div class='note'>{note}</div></div>"
    )


def load_r41_cfg() -> dict[str, Any]:
    try:
        return json.loads(R41_CONFIG.read_text(encoding="utf-8")) if R41_CONFIG.exists() else {}
    except Exception:
        return {}


def gvz_display_regime(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "KULLANILAMIYOR"
        cfg = load_r41_cfg()
        g = cfg.get("gvz", {})
        return gvz_regime(float(value), float(g.get("full_cap_max", 25.9795)), float(g.get("half_cap_max", 30.5238)))
    except Exception:
        return "KULLANILAMIYOR"


def stored_risk_label(dec: dict[str, Any] | None) -> str:
    if not dec:
        return "KULLANILAMIYOR"
    if dec.get("gvz_panic") is True:
        return "PANİK"
    return gvz_display_regime(dec.get("gvz"))


def target_matches(dec: dict[str, Any] | None, fc: dict[str, Any] | None) -> bool:
    if not dec or not fc:
        return False
    return str(dec.get("target_month") or "")[:7] == str(fc.get("target_month") or "")[:7]


def load_replay() -> pd.DataFrame:
    if not HISTORICAL_REPLAY.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(HISTORICAL_REPLAY)
        if "month" in df.columns:
            df["month"] = pd.to_datetime(df["month"], errors="coerce")
        return df.dropna(subset=["month"]).sort_values("month")
    except Exception:
        return pd.DataFrame()


def replay_metrics(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty or not {"actual", "patch_r1", "patch_r1_ape", "rw_ape"}.issubset(df.columns):
        return {"n": 0, "mape": None, "mae": None, "rw_mape": None}
    actual = pd.to_numeric(df["actual"], errors="coerce")
    patch = pd.to_numeric(df["patch_r1"], errors="coerce")
    return {
        "n": int(len(df)),
        "mape": float(pd.to_numeric(df["patch_r1_ape"], errors="coerce").mean()),
        "mae": float((actual - patch).abs().mean()),
        "rw_mape": float(pd.to_numeric(df["rw_ape"], errors="coerce").mean()),
    }


url = db_url()
decision = safe_call(lambda: fetch_current_decision_state(url), None) if url else None
decision_rows = safe_call(lambda: fetch_decision_history(url), []) if url else []
forecast = safe_call(lambda: fetch_current_forecast(url), None) if url else None
forecast_rows = safe_call(lambda: fetch_forecast_history(url), []) if url else []
spot = safe_call(get_spot, None)
hist, hist_meta = safe_call(get_xau_history, (pd.DataFrame(), {}))
gvz = safe_call(get_gvz, None)
replay = load_replay()
rmetrics = replay_metrics(replay)

st.markdown(
    "<div class='gc-shell'>"
    "<div class='gc-menu'>☰</div>"
    "<div class='gc-logo'><b>G</b></div>"
    "<div class='gc-brand'>GOLD CONTROL<small>DECISION SYSTEM</small></div>"
    "</div>",
    unsafe_allow_html=True,
)

NAV_OPTIONS = ["⌂ Bugün", "◉ Görünüm", "↗ Tahmin", "◷ Geçmiş"]
nav = st.radio("Ana navigasyon", NAV_OPTIONS, horizontal=True, label_visibility="collapsed", key="gc_main_nav")


if nav == "⌂ Bugün":
    page_head("BUGÜN", "Piyasa şu anda ne durumda?", None if not spot else spot.get("as_of") or spot.get("updated_at"))
    completed = latest_completed_daily_row(hist)
    completed_close = None if completed is None else float(completed["close"])
    delta = price_delta(None if not spot else spot.get("price"), completed_close)

    if spot:
        delta_text = "Karşılaştırma yok" if delta is None else f"{delta.absolute:+,.2f} USD · {delta.percent:+.2f}%"
        delta_class = "gc-muted" if delta is None else ("gc-positive" if delta.absolute >= 0 else "gc-negative")
        freshness = "GÜNCEL" if not spot.get("stale") else "STALE"
        st.markdown(
            "<div class='gc-hero'><div class='gc-kicker'>ALTIN ONS · XAU/USD · INDICATIVE LIVE</div>"
            f"<div class='gc-big'>{fmt_num(spot.get('price'),2)} USD</div>"
            f"<div class='{delta_class}'><b>{delta_text}</b></div>"
            f"<span class='gc-badge'>{freshness}</span>"
            f"<div class='gc-meta' style='margin-top:.55rem'>Kaynak: {display_state(spot.get('source'),'Gold API')} · display only / no model use</div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(empty_html("CANLI XAU/USD KULLANILAMIYOR", "Kaynak veya bağlantı durumu doğrulanamadı."), unsafe_allow_html=True)

    current_state = decision_view_state(decision)
    st.markdown(
        "<div class='gc-grid3'>"
        + mini_card("TAMAMLANMIŞ GÜNLÜK CLOSE", fmt_num(completed_close, 2, " USD"), "XAUS operasyonel cross-check")
        + mini_card("GVZ", fmt_num(None if not gvz else gvz.get("close"), 2), f"Risk görünümü: {gvz_display_regime(None if not gvz else gvz.get('close'))}")
        + mini_card("SON KAYITLI DURUM", current_state.title, "Decision Store" if decision else "Henüz display-eligible kayıt yok")
        + "</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True, key="gc_market_history_card"):
        st.markdown("<div class='gc-section-title'>PİYASA TARİHÇESİ</div>", unsafe_allow_html=True)
        if not hist.empty:
            timeframe = st.radio("Aralık", ["1A", "3A", "6A", "1Y"], horizontal=True, key="gc_market_range", label_visibility="collapsed")
            chart = filter_history_timeframe(hist, timeframe)
            if not chart.empty:
                st.line_chart(chart.set_index("date")[["close"]], height=255)
            st.markdown("<div class='gc-footnote'>XAUS tarihçesi yalnız operasyonel display cross-check'tir; canonical EOD/settlement değildir.</div>", unsafe_allow_html=True)
        else:
            st.markdown(empty_html("TARİHÇE KULLANILAMIYOR", "XAUS history kaynağı okunamadı."), unsafe_allow_html=True)

    st.markdown(
        f"<div class='gc-info'><b>Karar bağlamı:</b> {current_state.title}. Canlı spot yalnız piyasa izleme verisidir.<br><b>Canlı spot ≠ son EOD karar.</b></div>",
        unsafe_allow_html=True,
    )


elif nav == "◉ Görünüm":
    updated = None if not decision else decision.get("generated_at") or decision.get("decision_as_of")
    page_head("GÖRÜNÜM", "Mevcut kayıtlı kararın neden üretildiğini anlayın.", updated)
    state = decision_view_state(decision)

    monthly = None if not decision else decision.get("monthly_direction_3m")
    ma, mt = arrow_state(monthly)
    live_gvz = None if not gvz else gvz.get("close")
    risk_label = stored_risk_label(decision) if decision else gvz_display_regime(live_gvz)
    risk_caption = "Stored Decision State" if decision else "Canlı GVZ display risk görünümü"

    if decision:
        badge, _ = evidence_badge(decision.get("evidence_class"))
        status_badge = badge
    else:
        status_badge = "YAYIMLANMADI"

    st.markdown(
        "<div class='gc-hero'><div class='gc-hero-layout'>"
        "<div class='gc-hero-icon'>✓</div>"
        "<div><div class='gc-kicker'>MEVCUT KAYITLI DURUM</div>"
        f"<div class='gc-mid'>{state.title}</div>"
        f"<div class='gc-meta'>{state.subtitle}</div>"
        f"<span class='gc-badge'>{status_badge}</span></div>"
        "<div class='gc-hero-side'>"
        "<div><div class='gc-hero-label'>MODEL YÖNÜ (AYLIK)</div>"
        f"<div class='gc-hero-value {tone_class(mt)}'>{ma} {display_state(monthly,'YAYIMLANMADI')}</div></div>"
        "<div><div class='gc-hero-label'>RİSK SEVİYESİ</div>"
        f"<div class='gc-hero-value'>{risk_label}</div><div class='gc-meta'>{risk_caption}</div></div>"
        "</div></div></div>",
        unsafe_allow_html=True,
    )

    summary_rows = html_row("Durum", state.title, "gc-muted" if not decision else "")
    summary_rows += html_row("Ana aylık bağlam", display_state(monthly, "YAYIMLANMADI"))
    summary_rows += html_row("Evidence", display_state(None if not decision else decision.get("evidence_class"), "YOK"))
    st.markdown(f"<div class='gc-card'>{section_header(1,'SİNYAL ÖZETİ')}{summary_rows}</div>", unsafe_allow_html=True)

    if decision:
        fa, ft = arrow_state(decision.get("fast_state"))
        sa, stn = arrow_state(decision.get("slow_state"))
        model_body = f"<div class='gc-mid {tone_class(mt)}'>{ma} {display_state(monthly)}</div><div class='gc-footnote'>Stored monthly direction context.</div>"
        fs_body = html_row("FAST", f"{fa} {display_state(decision.get('fast_state'))}", tone_class(ft))
        fs_body += html_row("SLOW", f"{sa} {display_state(decision.get('slow_state'))}", tone_class(stn))
    else:
        model_body = "<div class='gc-mid gc-muted'>—</div><div class='gc-footnote'>Aylık yön ancak complete forward Decision Store kaydıyla gösterilir.</div>"
        fs_body = html_row("FAST", "YAYIMLANMADI", "gc-muted") + html_row("SLOW", "YAYIMLANMADI", "gc-muted")

    st.markdown(
        "<div class='gc-grid2'>"
        f"<div class='gc-card'>{section_header(2,'MODEL YÖNÜ (AYLIK)')}{model_body}</div>"
        f"<div class='gc-card'>{section_header(3,'FAST / SLOW TEYİDİ')}{fs_body}</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    risk_rows = html_row("Risk durumu", risk_label)
    risk_rows += html_row("GVZ", fmt_num(live_gvz if not decision else decision.get("gvz"), 2))
    risk_rows += html_row("Kaynak", "Decision Store" if decision else "Cboe canlı display")
    st.markdown(f"<div class='gc-card'>{section_header(4,'RİSK SEVİYESİ')}{risk_rows}</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(section_header(5, "SİNYAL ZAMAN ÇİZELGESİ"), unsafe_allow_html=True)
        if not hist.empty:
            chart = filter_history_timeframe(hist, "6A")
            if not chart.empty:
                st.line_chart(chart.set_index("date")[["close"]], height=255)
            if decision_rows:
                st.caption(f"{len(decision_rows)} gerçek Decision Store event kaydı mevcut; yalnız persisted eventler sinyal olarak kabul edilir.")
            else:
                st.caption("Fiyat tarihçesi gösteriliyor; henüz persisted Decision Store sinyal marker'ı yok.")
        else:
            st.markdown(empty_html("ZAMAN ÇİZELGESİ KULLANILAMIYOR", "Display-authorized fiyat tarihçesi okunamadı."), unsafe_allow_html=True)

    if decision:
        emergency_rows = html_row("Level", display_state(decision.get("level_emergency")))
        emergency_rows += html_row("Reversal", display_state(decision.get("reversal_emergency")))
        emergency_rows += html_row("BOCPD", display_state(decision.get("bocpd_context")))
    else:
        emergency_rows = html_row("Durum", "YAYIMLANMADI", "gc-muted")
    explanation = deterministic_explanation(decision)

    st.markdown(
        "<div class='gc-grid2'>"
        f"<div class='gc-card'>{section_header(6,'EMERGENCY DURUMU')}{emergency_rows}</div>"
        f"<div class='gc-card'>{section_header(7,'SİSTEM YORUMU')}<div style='font-style:italic;line-height:1.6'>{explanation}</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='gc-note'>Görünüm ekranı gerçek stored state'i açıklar. Veri yokken BUY/SELL/HOLD, pozisyon, keyfi güç veya güven yüzdesi üretilmez.</div>", unsafe_allow_html=True)


elif nav == "↗ Tahmin":
    updated = None if not forecast else forecast.get("frozen_at") or forecast.get("forecast_origin")
    page_head("TAHMİN", "Gelecek ay için model tabanlı H=1 aylık ortalama tahmini.", updated)
    fstate = forecast_view_state(forecast)

    if forecast:
        target = str(forecast.get("target_month") or "")[:7]
        badge, _ = evidence_badge(forecast.get("evidence_class"))
        monthly = decision.get("monthly_direction_3m") if target_matches(decision, forecast) else None
        ma, mt = arrow_state(monthly)
        forecast_value = fmt_num(forecast.get("forecast_value"), 2, " USD")
        hero_title = forecast_value
        hero_sub = f"Hedef dönem: {target}"
        badge_text = badge
        direction_text = f"{ma} {display_state(monthly,'—')}"
        origin_text = fmt_time(forecast.get("forecast_origin"))
    else:
        target = "—"
        hero_title = "TAHMİN HENÜZ YAYIMLANMADI"
        hero_sub = "NOT_ISSUED_IN_CANONICAL_LEDGER"
        badge_text = "BEKLİYOR"
        direction_text = "—"
        origin_text = "—"

    st.markdown(
        "<div class='gc-hero'><div class='gc-hero-layout'>"
        "<div class='gc-hero-icon'>↗</div>"
        "<div><div class='gc-kicker'>GELECEK AY TAHMİNİ</div>"
        f"<div class='gc-mid'>{hero_title}</div>"
        f"<div class='gc-meta'>{hero_sub}</div>"
        f"<span class='gc-badge gc-badge-gold'>{badge_text}</span></div>"
        "<div class='gc-hero-side'>"
        "<div><div class='gc-hero-label'>AYLIK YÖN</div>"
        f"<div class='gc-hero-value'>{direction_text}</div></div>"
        "<div><div class='gc-hero-label'>TAHMİN TARİHİ / ORIGIN</div>"
        f"<div class='gc-hero-value' style='font-size:1rem'>{origin_text}</div></div>"
        "</div></div></div>",
        unsafe_allow_html=True,
    )

    patch_current = fmt_num(None if not forecast else forecast.get("forecast_value"), 2, " USD")
    st.markdown(
        "<div class='gc-modelstrip'>"
        f"<div class='gc-modelcell'><div class='label'>{PATCH_FORWARD_LABEL}</div><div class='value gc-positive'>{patch_current}</div><div class='note'>Ana H=1 issuer · yalnız canonical ledger değeri</div></div>"
        "<div class='gc-modelcell'><div class='label'>VW REFERANS</div><div class='value gc-blue'>—</div><div class='note'>Referans rolü var; current issued değer henüz ledger'da yok</div></div>"
        "<div class='gc-modelcell'><div class='label'>RANDOM WALK (RW)</div><div class='value'>—</div><div class='note'>Aynı horizon benchmark</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='gc-card'><div class='gc-metadata'>"
        f"<div class='gc-meta-item'>▣ <span><b>Model:</b> {PATCH_FORWARD_ID}</span></div>"
        f"<div class='gc-meta-item'>⌘ <span><b>Geometri:</b> {PATCH_GEOMETRY}</span></div>"
        f"<div class='gc-meta-item'>◷ <span><b>Anchor:</b> {PATCH_ANCHOR}</span></div>"
        f"<div class='gc-meta-item'>✓ <span><b>Veri Koruması:</b> {PATCH_PIT}</span></div>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI</div>", unsafe_allow_html=True)
        if forecast_rows:
            fcf = pd.DataFrame(
                {
                    "target_month": pd.to_datetime([r.get("target_month") for r in forecast_rows], errors="coerce"),
                    "Yayımlanan tahmin": pd.to_numeric([r.get("forecast_value") for r in forecast_rows], errors="coerce"),
                }
            ).dropna().sort_values("target_month")
            if not fcf.empty:
                st.line_chart(fcf.set_index("target_month")[["Yayımlanan tahmin"]], height=285)
            st.caption("Bu panel yalnız prospectively issued forecast ledger noktalarını gösterir.")
        elif not replay.empty and {"actual", "patch_r1", "vw", "rw"}.issubset(replay.columns):
            st.markdown(
                "<div class='gc-replay-head'><strong>Prospective forecast henüz yok; aşağıdaki grafik araştırma referansıdır.</strong>"
                "<span class='gc-replay-pill'>HISTORICAL_REPLAY</span></div>",
                unsafe_allow_html=True,
            )
            research = replay.tail(12).set_index("month")[["actual", "patch_r1", "vw", "rw"]].rename(
                columns={"actual": "Gerçekleşen", "patch_r1": "Archived Patch", "vw": "VW", "rw": "RW"}
            )
            st.line_chart(research, height=285)
            st.caption("Replay sonuçları geleceğe önceden kaydedilmiş tahmin değildir; current forecast yerine geçmez.")
        else:
            st.markdown(empty_html("KARŞILAŞTIRMA HENÜZ OLUŞMADI", "Prospective forecast geçmişi yok."), unsafe_allow_html=True)

    spot_value = None if not spot else spot.get("price")
    diff_value = diff_pct = None
    if forecast and spot_value:
        try:
            diff_value = float(forecast["forecast_value"]) - float(spot_value)
            diff_pct = diff_value / float(spot_value) * 100.0
        except Exception:
            pass

    if diff_value is None:
        diff_display = "—"
        diff_class = "gc-muted"
    else:
        diff_display = f"{diff_value:+,.2f} USD · {diff_pct:+.2f}%"
        diff_class = "gc-positive" if diff_value >= 0 else "gc-negative"

    st.markdown(
        "<div class='gc-grid3'>"
        "<div class='gc-card'><div class='gc-section-title'>TAHMİN ÖZETİ</div>"
        + html_row("Güncel indicative spot", fmt_num(spot_value, 2, " USD"))
        + html_row("Issued H=1 tahmin", patch_current)
        + html_row("Fark", diff_display, diff_class)
        + html_row("Aylık yön", direction_text)
        + "</div>"
        "<div class='gc-card'><div class='gc-section-title'>MODEL BİLGİSİ</div>"
        f"<div class='gc-footnote'><b>{PATCH_FORWARD_LABEL}</b><br>Ana issuer adayı; frozen geometri ve PIT-safe feature contract.<br><br>"
        "<b>VW Referans</b><br>Hacim ağırlıklı referans rolü.<br><br><b>RW</b><br>Yön içermeyen benchmark.</div></div>"
        "<div class='gc-card'><div class='gc-section-title'>NOT</div>"
        f"<div class='gc-footnote'>Scenario status: <b>{SCENARIO_STATUS}</b>.<br><br>"
        "Kalibre edilmemiş güven yüzdesi, forecast bandı veya Baz/Yukarı/Aşağı senaryo fiyatı gösterilmez.<br><br><b>Yatırım tavsiyesi değildir.</b></div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    if not replay.empty:
        st.markdown(
            "<div class='gc-replay'><div class='gc-replay-head'><strong>MODEL ARAŞTIRMA KANITI</strong>"
            "<span class='gc-replay-pill'>HISTORICAL_REPLAY</span></div>"
            "<div class='gc-grid4'>"
            + mini_card("ARCHIVED PATCH MAPE", fmt_num(rmetrics["mape"], 2, "%"), "43 aylık historical replay")
            + mini_card("ARCHIVED PATCH MAE", fmt_num(rmetrics["mae"], 2, " USD"), "Historical replay")
            + mini_card("RW MAPE", fmt_num(rmetrics["rw_mape"], 2, "%"), "Aynı replay window")
            + mini_card("REPLAY N", str(rmetrics["n"]), "Prospective değildir")
            + "</div></div>",
            unsafe_allow_html=True,
        )


else:
    latest_hist_update = forecast_rows[0].get("frozen_at") or forecast_rows[0].get("forecast_origin") if forecast_rows else (
        decision_rows[0].get("event_ts") if decision_rows else None
    )
    page_head("GEÇMİŞ", "Üretilen tahminlerin gerçekleşen sonuçlarla karşılaştırılması.", latest_hist_update)

    st.markdown("<div class='gc-footnote' style='margin-bottom:.45rem'><b>PROSPECTIVE / LIVE LEDGER</b> · Historical replay bu metriklere karıştırılmaz.</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='gc-grid4'>"
        + mini_card("MAPE", "—", "Realized prospective outcome sonrası")
        + mini_card("MAE (USD)", "—", "Realized prospective outcome sonrası")
        + mini_card("YÖN DOĞRULUĞU", "—", "Frozen outcome tanımı sonrası")
        + mini_card("TOPLAM TAHMİN", str(len(forecast_rows)), "Issued PROSPECTIVE_SHADOW / LIVE")
        + "</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>TAHMİN – GERÇEKLEŞEN KARŞILAŞTIRMASI</div>", unsafe_allow_html=True)
        if forecast_rows:
            fdf = pd.DataFrame(
                {
                    "target_month": pd.to_datetime([r.get("target_month") for r in forecast_rows], errors="coerce"),
                    "Yayımlanan tahmin": pd.to_numeric([r.get("forecast_value") for r in forecast_rows], errors="coerce"),
                }
            ).dropna().sort_values("target_month")
            if not fdf.empty:
                st.line_chart(fdf.set_index("target_month")[["Yayımlanan tahmin"]], height=285)
            st.caption("Gerçekleşen canonical monthly actual bağlandıkça aynı grafikte karşılaştırma açılır.")
        else:
            st.markdown(empty_html("İLERİYE DÖNÜK PERFORMANS HENÜZ OLUŞMADI", "Prospective forecast ledger henüz boş."), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>HATA ORANI ZAMAN ÇİZGİSİ</div>", unsafe_allow_html=True)
        st.markdown(empty_html("REALIZED PROSPECTIVE HATA HENÜZ YOK", "Outcome gerçekleşmeden hata oranı üretilmez."), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>SEÇİLMİŞ GERÇEKLEŞEN TAHMİNLER</div>", unsafe_allow_html=True)
        if forecast_rows:
            frame = pd.DataFrame(
                [
                    {
                        "Hedef Ay": str(r.get("target_month") or "")[:7],
                        "Patch Tahmini": r.get("forecast_value"),
                        "Gerçekleşen": None,
                        "Hata (%)": None,
                        "Evidence": r.get("evidence_class"),
                    }
                    for r in forecast_rows
                ]
            )
            st.dataframe(frame, width="stretch", hide_index=True)
        else:
            st.markdown(empty_html("PROSPECTIVE KAYIT YOK", "İlk gerçek issued forecast oluşunca burada listelenecek."), unsafe_allow_html=True)

    if not replay.empty and {"actual", "patch_r1", "vw", "rw"}.issubset(replay.columns):
        st.markdown(
            "<div class='gc-replay'><div class='gc-replay-head'><strong>ARAŞTIRMA GEÇMİŞİ — AYRI KANIT SINIFI</strong>"
            "<span class='gc-replay-pill'>HISTORICAL_REPLAY</span></div>"
            "<div class='gc-grid4'>"
            + mini_card("REPLAY MAPE", fmt_num(rmetrics["mape"], 2, "%"), "Archived Patch")
            + mini_card("REPLAY MAE", fmt_num(rmetrics["mae"], 2, " USD"), "Archived Patch")
            + mini_card("RW MAPE", fmt_num(rmetrics["rw_mape"], 2, "%"), "Benchmark")
            + mini_card("REPLAY N", str(rmetrics["n"]), "Prospective değildir")
            + "</div></div>",
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.markdown("<div class='gc-section-title'>HISTORICAL_REPLAY · GERÇEKLEŞEN / MODEL / REFERANSLAR</div>", unsafe_allow_html=True)
            research = replay.tail(18).set_index("month")[["actual", "patch_r1", "vw", "rw"]].rename(
                columns={"actual": "Gerçekleşen", "patch_r1": "Archived Patch", "vw": "VW", "rw": "RW"}
            )
            st.line_chart(research, height=300)
            st.caption("Bu grafik araştırma replay'idir; prospective/live performans değildir.")

        with st.container(border=True):
            st.markdown("<div class='gc-section-title'>SEÇİLMİŞ HISTORICAL_REPLAY KAYITLARI</div>", unsafe_allow_html=True)
            cols = [c for c in ["month", "actual", "patch_r1", "patch_r1_ape", "vw", "rw"] if c in replay.columns]
            table = replay[cols].tail(8).copy()
            if "month" in table.columns:
                table["month"] = table["month"].dt.strftime("%Y-%m")
            st.dataframe(table, width="stretch", hide_index=True)

    st.markdown("<div class='gc-note'>Prospective ve replay performansları aynı kartta birleştirilmez. Trade getirisi, giriş/çıkış, YBB getiri veya portföy drawdown execution contract olmadan gösterilmez.</div>", unsafe_allow_html=True)


st.markdown("<div id='system-health'></div>", unsafe_allow_html=True)
with st.expander("Sistem / Veri Sağlığı / Audit"):
    st.write("UI contract:", FINAL_MOCKUP_CONTRACT)
    st.write("Neon:", "BAĞLI" if url else "YAPILANDIRILMADI")
    st.write("Decision Store:", "KAYIT VAR" if decision else "KAYIT YOK")
    st.write("Forecast ledger:", "KAYIT VAR" if forecast else "KAYIT YOK")
    st.write("Spot:", "FRESH" if spot and not spot.get("stale") else "STALE / KULLANILAMIYOR")
    st.write("Historical replay:", "MEVCUT" if not replay.empty else "YOK")
