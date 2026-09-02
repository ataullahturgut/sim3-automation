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
 --gc-navy:#082a4b;--gc-navy2:#0d3b66;--gc-gold:#f2ad36;--gc-gold2:#ffd98a;
 --gc-ink:#10294b;--gc-muted:#687995;--gc-line:#e5ebf2;--gc-bg:#f8fafc;
 --gc-green:#17a85b;--gc-red:#e43d4e;--gc-blue:#1976d2;--gc-amber:#e59d1c;
}
[data-testid="stAppViewContainer"]{background:linear-gradient(180deg,#fff 0,#f9fbfd 100%);color:var(--gc-ink)}
.block-container{max-width:860px;padding-top:.35rem;padding-bottom:6.7rem;padding-left:.78rem;padding-right:.78rem}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent;height:.15rem}
h1{font-size:1.72rem!important;letter-spacing:.01em;color:var(--gc-ink);margin-bottom:.05rem!important}
h2,h3,h4{color:var(--gc-ink)}
.gc-shell{display:flex;align-items:center;gap:.7rem;border-bottom:1px solid var(--gc-line);padding:.45rem .1rem .9rem;margin-bottom:.9rem}
.gc-mark{width:42px;height:42px;border:4px solid var(--gc-gold);border-radius:10px;transform:rotate(30deg);display:flex;align-items:center;justify-content:center}
.gc-mark b{transform:rotate(-30deg);color:var(--gc-gold);font-size:1rem}
.gc-brand{font-size:1.27rem;font-weight:900;letter-spacing:.02em;line-height:1;color:var(--gc-ink)}
.gc-brand small{display:block;color:var(--gc-gold);letter-spacing:.16em;font-size:.62rem;margin-top:.36rem;font-weight:800}
.gc-pagehead{display:flex;justify-content:space-between;gap:1rem;align-items:flex-end;margin:.4rem 0 .7rem}
.gc-pagehead h2{font-size:1.55rem;margin:0;color:var(--gc-ink)}
.gc-pagehead p{margin:.25rem 0 0;color:var(--gc-muted);font-size:.86rem}
.gc-updated{font-size:.72rem;color:var(--gc-muted);text-align:right;white-space:nowrap}
.gc-hero{background:linear-gradient(135deg,#062746 0%,#0b365e 100%);color:#fff;border-radius:18px;padding:1.15rem 1.15rem;margin:.55rem 0 1rem;box-shadow:0 9px 28px rgba(8,42,75,.14);overflow:hidden;position:relative}
.gc-hero:after{content:"";position:absolute;right:-55px;top:-80px;width:190px;height:190px;border:1px solid rgba(255,255,255,.06);border-radius:50%}
.gc-hero-grid{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(145px,.65fr);gap:1rem;align-items:stretch}
.gc-hero-side{border-left:1px solid rgba(255,255,255,.17);padding-left:1rem}
.gc-kicker{font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;opacity:.78;font-weight:750}
.gc-big{font-size:2.45rem;font-weight:850;line-height:1.04;margin:.42rem 0}
.gc-mid{font-size:1.47rem;font-weight:850;line-height:1.14;margin:.35rem 0}
.gc-hero-label{font-size:.78rem;opacity:.72;margin-top:.15rem}
.gc-hero-value{font-size:1.22rem;font-weight:850;margin:.22rem 0 .7rem}
.gc-meta{font-size:.78rem;opacity:.78;line-height:1.45}
.gc-badge{display:inline-block;border:1px solid rgba(255,255,255,.28);border-radius:999px;padding:.32rem .62rem;font-weight:800;font-size:.68rem;margin-top:.55rem}
.gc-health{display:inline-flex;align-items:center;gap:.35rem;border:1px solid rgba(255,255,255,.23);border-radius:8px;padding:.34rem .55rem;font-size:.72rem;margin-top:.65rem}
.gc-dot{width:8px;height:8px;border-radius:50%;background:var(--gc-green);display:inline-block}
.gc-card{background:#fff;border:1px solid var(--gc-line);border-radius:15px;padding:.95rem 1rem;margin:.58rem 0;box-shadow:0 4px 16px rgba(16,41,75,.035)}
.gc-section-title{display:flex;align-items:center;gap:.55rem;font-size:.94rem;font-weight:850;color:var(--gc-ink);margin-bottom:.55rem}
.gc-num{display:inline-flex;width:26px;height:26px;border-radius:50%;background:var(--gc-navy);color:#fff;align-items:center;justify-content:center;font-size:.78rem;font-weight:850}
.gc-grid2{display:grid;grid-template-columns:1fr 1fr;gap:.72rem}
.gc-grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:.72rem}
.gc-grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:.64rem}
.gc-mini{background:#fff;border:1px solid var(--gc-line);border-radius:14px;padding:.85rem;min-height:112px;box-shadow:0 4px 15px rgba(16,41,75,.03)}
.gc-mini .label{font-size:.69rem;font-weight:800;color:var(--gc-ink);text-transform:uppercase;line-height:1.25}
.gc-mini .value{font-size:1.45rem;font-weight:850;margin:.45rem 0 .22rem;color:var(--gc-ink)}
.gc-mini .note{font-size:.72rem;color:var(--gc-muted);line-height:1.35}
.gc-row{display:flex;justify-content:space-between;align-items:flex-start;gap:.75rem;padding:.5rem 0;border-bottom:1px solid var(--gc-line);font-size:.86rem}
.gc-row:last-child{border-bottom:none}
.gc-value{font-weight:800;text-align:right}
.gc-positive{color:var(--gc-green)!important}.gc-negative{color:var(--gc-red)!important}.gc-warning{color:var(--gc-amber)!important}.gc-blue{color:var(--gc-blue)!important}.gc-muted{color:var(--gc-muted)!important}
.gc-empty{background:#fff;border:1px dashed #cbd5e1;border-radius:15px;padding:1.15rem;text-align:center;margin:.55rem 0;color:var(--gc-muted)}
.gc-empty strong{display:block;color:var(--gc-ink);font-size:1rem;margin-bottom:.35rem}
.gc-note{background:#fffaf0;border:1px solid #f5ddb1;border-radius:13px;padding:.8rem .9rem;color:#6f592a;font-size:.78rem;line-height:1.45;margin:.7rem 0}
.gc-info{background:#f5f8fc;border:1px solid var(--gc-line);border-radius:13px;padding:.8rem .9rem;color:#445a79;font-size:.78rem;line-height:1.45;margin:.7rem 0}
.gc-statusline{display:flex;gap:.45rem;flex-wrap:wrap;margin-top:.45rem}
.gc-chip{border:1px solid var(--gc-line);border-radius:999px;padding:.27rem .52rem;font-size:.7rem;font-weight:750;background:#fff}
.gc-chip.up{color:var(--gc-green);border-color:#cdebd9;background:#f2fbf6}
.gc-chip.down{color:var(--gc-red);border-color:#f2ccd1;background:#fff7f8}
.gc-chip.neutral{color:#52657f;background:#f7f9fc}
.gc-footnote{font-size:.72rem;color:var(--gc-muted);line-height:1.5}
div[data-baseweb="tab-list"]{position:fixed;left:50%;transform:translateX(-50%);bottom:.35rem;z-index:999;background:#fff;border:1px solid var(--gc-line);border-radius:17px;padding:.28rem;box-shadow:0 8px 28px rgba(15,39,72,.15);width:min(820px,calc(100vw - 1rem));justify-content:space-around}
button[data-baseweb="tab"]{border-radius:12px;padding:.68rem .28rem!important;flex:1;font-size:.78rem}
button[data-baseweb="tab"][aria-selected="true"]{background:var(--gc-navy)!important;color:#fff!important}
[data-testid="stPopover"] button{border:1px solid var(--gc-line)!important;border-radius:12px!important;min-height:40px!important}
@media(max-width:620px){
 .block-container{padding-left:.55rem;padding-right:.55rem;padding-bottom:6.4rem}
 .gc-pagehead{align-items:flex-start}.gc-updated{font-size:.64rem}
 .gc-big{font-size:2rem}.gc-mid{font-size:1.28rem}
 .gc-hero-grid{grid-template-columns:1fr}.gc-hero-side{border-left:0;border-top:1px solid rgba(255,255,255,.16);padding-left:0;padding-top:.75rem}
 .gc-grid4{grid-template-columns:1fr 1fr}.gc-grid3{grid-template-columns:1fr}.gc-grid2{grid-template-columns:1fr 1fr}
 .gc-mini{min-height:100px;padding:.75rem}.gc-mini .value{font-size:1.2rem}
 .stDataFrame{font-size:.75rem}
}
@media(max-width:390px){
 .gc-grid2{grid-template-columns:1fr}
 .gc-brand{font-size:1.12rem}
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


def read_decision(url: str):
    return safe_call(lambda: fetch_current_decision_state(url), None) if url else None


def read_decision_rows(url: str):
    return safe_call(lambda: fetch_decision_history(url), []) if url else []


def read_forecast(url: str):
    return safe_call(lambda: fetch_current_forecast(url), None) if url else None


def read_forecast_rows(url: str):
    return safe_call(lambda: fetch_forecast_history(url), []) if url else []


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


def empty_block(title: str, subtitle: str) -> None:
    st.markdown(
        f"<div class='gc-empty'><strong>{title}</strong>{subtitle}</div>",
        unsafe_allow_html=True,
    )


def page_head(title: str, subtitle: str, updated: Any = None) -> None:
    updated_text = "Henüz kayıt yok" if updated in (None, "", "N/A") else fmt_time(updated)
    st.markdown(
        f"<div class='gc-pagehead'><div><h2>{title}</h2><p>{subtitle}</p></div>"
        f"<div class='gc-updated'>Son güncelleme: {updated_text}</div></div>",
        unsafe_allow_html=True,
    )


def tone_class(tone: str) -> str:
    return {
        "positive": "gc-positive",
        "negative": "gc-negative",
        "warning": "gc-warning",
        "shadow": "gc-blue",
    }.get(tone, "")


def stored_risk_label(dec: dict[str, Any] | None) -> str:
    if not dec:
        return "KULLANILAMIYOR"
    if dec.get("gvz_panic") is True:
        return "PANİK"
    value = dec.get("gvz")
    if value is None:
        return "KULLANILAMIYOR"
    try:
        cfg = json.loads(R41_CONFIG.read_text(encoding="utf-8")) if R41_CONFIG.exists() else {}
        g = cfg.get("gvz", {})
        return gvz_regime(
            float(value),
            float(g.get("full_cap_max", 25.9795)),
            float(g.get("half_cap_max", 30.5238)),
        )
    except Exception:
        return "KULLANILAMIYOR"


def target_matches(dec: dict[str, Any] | None, fc: dict[str, Any] | None) -> bool:
    if not dec or not fc:
        return False
    return str(dec.get("target_month") or "")[:7] == str(fc.get("target_month") or "")[:7]


def mini_card(label: str, value: str, note: str, value_class: str = "") -> str:
    return (
        "<div class='gc-mini'>"
        f"<div class='label'>{label}</div>"
        f"<div class='value {value_class}'>{value}</div>"
        f"<div class='note'>{note}</div></div>"
    )


url = db_url()
decision = read_decision(url)
decision_rows = read_decision_rows(url)
forecast = read_forecast(url)
forecast_rows = read_forecast_rows(url)
spot = safe_call(get_spot, None)
hist_pack = safe_call(get_xau_history, (pd.DataFrame(), {}))
hist, hist_meta = hist_pack
gvz = safe_call(get_gvz, None)

# Real compact product shell. The left control is functional and exposes technical status.
head_cols = st.columns([0.12, 0.88], vertical_alignment="center")
with head_cols[0]:
    with st.popover("☰", use_container_width=True):
        st.markdown("**Sistem / Veri Sağlığı**")
        st.caption(f"UI contract: {FINAL_MOCKUP_CONTRACT}")
        st.write("Neon:", "BAĞLI" if url else "YAPILANDIRILMADI")
        st.write("Decision Store:", "KAYIT VAR" if decision else "KAYIT YOK")
        st.write("Forecast ledger:", "KAYIT VAR" if forecast else "KAYIT YOK")
        st.write("Spot:", "FRESH" if spot and not spot.get("stale") else "STALE / KULLANILAMIYOR")
with head_cols[1]:
    st.markdown(
        "<div class='gc-shell'><div class='gc-mark'><b>G</b></div>"
        "<div class='gc-brand'>GOLD CONTROL<small>DECISION SYSTEM</small></div></div>",
        unsafe_allow_html=True,
    )

piyasa, gorunum, tahmin, gecmis = st.tabs(["⌂ Bugün", "◉ Görünüm", "↗ Tahmin", "◷ Geçmiş"])


with piyasa:
    page_head(
        "BUGÜN",
        "Piyasa şu anda ne durumda?",
        None if not spot else spot.get("as_of") or spot.get("updated_at"),
    )

    completed = latest_completed_daily_row(hist)
    completed_close = None if completed is None else float(completed["close"])
    delta = price_delta(None if spot is None else spot.get("price"), completed_close)

    if spot:
        delta_text = "Karşılaştırma yok" if delta is None else f"{delta.absolute:+,.2f} USD · {delta.percent:+.2f}%"
        delta_class = "gc-muted" if delta is None else "gc-positive" if delta.absolute >= 0 else "gc-negative"
        freshness = "GÜNCEL" if not spot.get("stale") else "STALE"
        st.markdown(
            "<div class='gc-hero'><div class='gc-kicker'>ALTIN ONS · XAU/USD · INDICATIVE LIVE</div>"
            f"<div class='gc-big'>{fmt_num(spot.get('price'),2)} USD</div>"
            f"<div class='{delta_class}'><b>{delta_text}</b></div>"
            f"<div class='gc-statusline'><span class='gc-badge'>{freshness}</span></div>"
            f"<div class='gc-meta'>Kaynak: {display_state(spot.get('source'),'Gold API')} · display only / no model use</div></div>",
            unsafe_allow_html=True,
        )
    else:
        empty_block("CANLI XAU/USD KULLANILAMIYOR", "Kaynak veya bağlantı durumu doğrulanamadı.")

    current_state = decision_view_state(decision)
    risk_text = stored_risk_label(decision)
    st.markdown(
        "<div class='gc-grid3'>"
        + mini_card("TAMAMLANMIŞ GÜNLÜK CLOSE", fmt_num(completed_close, 2, " USD"), "XAUS operasyonel cross-check")
        + mini_card("GVZ", fmt_num(None if not gvz else gvz.get("close"), 2), "Cboe resmi günlük seri")
        + mini_card("SON KAYITLI DURUM", current_state.title, f"Risk: {risk_text}")
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='gc-card'><div class='gc-section-title'><span>PİYASA TARİHÇESİ</span></div>", unsafe_allow_html=True)
    if not hist.empty:
        timeframe = st.radio("Aralık", ["1A", "3A", "6A", "1Y"], horizontal=True, label_visibility="collapsed")
        chart = filter_history_timeframe(hist, timeframe)
        if not chart.empty:
            st.line_chart(chart.set_index("date")[["close"]], height=260)
        st.markdown(
            "<div class='gc-footnote'>XAUS günlük tarihçe operasyonel display cross-check'tir; canonical EOD/settlement olarak etiketlenmez.</div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div class='gc-empty'><strong>TARİHÇE KULLANILAMIYOR</strong>XAUS history kaynağı okunamadı.</div></div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='gc-info'><b>Karar bağlamı:</b> "
        f"{current_state.title}. Canlı spot yalnız piyasa izleme verisidir.<br><b>Canlı spot ≠ son EOD karar.</b></div>",
        unsafe_allow_html=True,
    )


with gorunum:
    updated = None if not decision else decision.get("generated_at") or decision.get("decision_as_of")
    page_head("GÖRÜNÜM", "Mevcut kayıtlı kararın neden üretildiğini anlayın.", updated)
    state = decision_view_state(decision)

    if decision:
        badge, _ = evidence_badge(decision.get("evidence_class"))
        monthly_arrow, monthly_tone = arrow_state(decision.get("monthly_direction_3m"))
        risk_label = stored_risk_label(decision)
        health = display_state(decision.get("quality_status"), "KALİTE DURUMU YOK")
        st.markdown(
            "<div class='gc-hero'><div class='gc-hero-grid'><div>"
            "<div class='gc-kicker'>MEVCUT KAYITLI DURUM</div>"
            f"<div class='gc-mid {tone_class(state.tone)}'>{state.title}</div>"
            f"<div class='gc-meta'>{state.subtitle}</div>"
            f"<div class='gc-health'><span class='gc-dot'></span>{health}</div>"
            f"<div class='gc-statusline'><span class='gc-badge'>{badge}</span></div>"
            "</div><div class='gc-hero-side'>"
            "<div class='gc-hero-label'>MODEL YÖNÜ (AYLIK)</div>"
            f"<div class='gc-hero-value {tone_class(monthly_tone)}'>{monthly_arrow} {display_state(decision.get('monthly_direction_3m'))}</div>"
            "<div class='gc-hero-label'>RİSK SEVİYESİ</div>"
            f"<div class='gc-hero-value'>{risk_label}</div>"
            "</div></div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='gc-hero'><div class='gc-kicker'>MEVCUT KAYITLI DURUM</div>"
            f"<div class='gc-mid'>{state.title}</div><div class='gc-meta'>{state.subtitle}</div>"
            "<div class='gc-badge'>YAYIMLANMADI</div></div>",
            unsafe_allow_html=True,
        )

    rows = ""
    if decision:
        rows += html_row("Kayıtlı sınıflandırma", classification_label(decision.get("classification")))
        rows += html_row("Ana aylık bağlam", display_state(decision.get("monthly_direction_3m")))
        rows += html_row("Evidence", display_state(decision.get("evidence_class")))
    else:
        rows = html_row("Durum", "KANONİK KARAR YOK", "gc-muted")
    st.markdown(f"<div class='gc-card'>{section_header(1,'SİNYAL ÖZETİ')}{rows}</div>", unsafe_allow_html=True)

    c2, c3 = st.columns(2)
    with c2:
        if decision:
            arrow, tone = arrow_state(decision.get("monthly_direction_3m"))
            body = (
                f"<div class='gc-mid {tone_class(tone)}'>{arrow} {display_state(decision.get('monthly_direction_3m'))}</div>"
                "<div class='gc-footnote'>Stored monthly context. Güç veya güven yüzdesi üretilmez.</div>"
            )
        else:
            body = "<div class='gc-muted'>Kayıtlı aylık yön yok.</div>"
        st.markdown(f"<div class='gc-card'>{section_header(2,'MODEL YÖNÜ (AYLIK)')}{body}</div>", unsafe_allow_html=True)
    with c3:
        if decision:
            fa, ft = arrow_state(decision.get("fast_state"))
            sa, stn = arrow_state(decision.get("slow_state"))
            body = (
                f"<div class='gc-row'><span>FAST</span><span class='gc-value {tone_class(ft)}'>{fa} {display_state(decision.get('fast_state'))}</span></div>"
                f"<div class='gc-row'><span>SLOW</span><span class='gc-value {tone_class(stn)}'>{sa} {display_state(decision.get('slow_state'))}</span></div>"
            )
        else:
            body = "<div class='gc-muted'>Fast / Slow stored state yok.</div>"
        st.markdown(f"<div class='gc-card'>{section_header(3,'FAST / SLOW TEYİDİ')}{body}</div>", unsafe_allow_html=True)

    if decision:
        risk_rows = html_row("Risk durumu", stored_risk_label(decision))
        risk_rows += html_row("GVZ", fmt_num(decision.get("gvz"), 2))
        risk_rows += html_row("Panic flag", "EVET" if decision.get("gvz_panic") else "HAYIR")
    else:
        risk_rows = html_row("Risk durumu", "KULLANILAMIYOR", "gc-muted")
    st.markdown(f"<div class='gc-card'>{section_header(4,'RİSK SEVİYESİ')}{risk_rows}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='gc-card'>{section_header(5,'SİNYAL ZAMAN ÇİZELGESİ')}", unsafe_allow_html=True)
    if decision_rows:
        timeline = pd.DataFrame(
            {
                "Tarih": [fmt_time(r.get("event_ts")) for r in decision_rows[:12]],
                "Durum": [classification_label(r.get("classification")) for r in decision_rows[:12]],
                "Neden": [display_state(r.get("reason_code")) for r in decision_rows[:12]],
                "Evidence": [display_state(r.get("evidence_class")) for r in decision_rows[:12]],
            }
        )
        st.dataframe(timeline, use_container_width=True, hide_index=True)
    else:
        empty_block("KAYITLI SİNYAL ZAMAN ÇİZELGESİ YOK", "Yalnız gerçek Decision Store event kayıtları burada görünür.")
    st.markdown("</div>", unsafe_allow_html=True)

    c6, c7 = st.columns(2)
    with c6:
        if decision:
            emergency_rows = html_row("Level", display_state(decision.get("level_emergency")))
            emergency_rows += html_row("Reversal", display_state(decision.get("reversal_emergency")))
            emergency_rows += html_row("BOCPD", display_state(decision.get("bocpd_context")))
        else:
            emergency_rows = html_row("Durum", "KULLANILAMIYOR", "gc-muted")
        st.markdown(f"<div class='gc-card'>{section_header(6,'EMERGENCY DURUMU')}{emergency_rows}</div>", unsafe_allow_html=True)
    with c7:
        explanation = deterministic_explanation(decision)
        st.markdown(
            f"<div class='gc-card'>{section_header(7,'SİSTEM YORUMU')}<div style='font-style:italic;line-height:1.55'>{explanation}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='gc-note'>Bu ekran stored state'i açıklar. Pozisyon, BUY/SELL/HOLD, exposure yüzdesi, keyfi güç veya güven yüzdesi üretmez.</div>",
        unsafe_allow_html=True,
    )


with tahmin:
    updated = None if not forecast else forecast.get("frozen_at") or forecast.get("forecast_origin")
    page_head("TAHMİN", "Gelecek aya ilişkin canonical H=1 altın fiyat tahmini.", updated)
    fstate = forecast_view_state(forecast)

    if forecast:
        badge, _ = evidence_badge(forecast.get("evidence_class"))
        target = str(forecast.get("target_month") or "")[:7]
        monthly = decision.get("monthly_direction_3m") if target_matches(decision, forecast) else None
        ma, mt = arrow_state(monthly)
        st.markdown(
            "<div class='gc-hero'><div class='gc-kicker'>GELECEK AY TAHMİNİ</div>"
            "<div class='gc-hero-grid'><div>"
            f"<div class='gc-hero-label'>Hedef ay: {target}</div>"
            f"<div class='gc-big'>{fmt_num(forecast.get('forecast_value'),2)} {display_state(forecast.get('unit'),'USD/oz')}</div>"
            f"<div class='gc-badge'>{badge}</div>"
            f"<div class='gc-meta'>Origin: {fmt_time(forecast.get('forecast_origin'))}</div>"
            "</div><div class='gc-hero-side'>"
            "<div class='gc-hero-label'>BEKLENEN YÖN / AYLIK BAĞLAM</div>"
            f"<div class='gc-hero-value {tone_class(mt)}'>{ma} {display_state(monthly)}</div>"
            "<div class='gc-meta'>Yalnız aynı target ayına bağlı stored context varsa gösterilir.</div>"
            "</div></div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='gc-hero'><div class='gc-kicker'>GELECEK AY TAHMİNİ</div>"
            f"<div class='gc-mid'>{fstate.title}</div><div class='gc-meta'>{fstate.subtitle}</div>"
            "<div class='gc-badge'>YAYIMLANMADI</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='gc-card'><div class='gc-section-title'><span>GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI</span></div>", unsafe_allow_html=True)
    if forecast_rows:
        fc_frame = pd.DataFrame(
            {
                "target_month": pd.to_datetime([r.get("target_month") for r in forecast_rows], errors="coerce"),
                "Yayımlanan tahmin": pd.to_numeric([r.get("forecast_value") for r in forecast_rows], errors="coerce"),
            }
        ).dropna().sort_values("target_month")
        if not fc_frame.empty:
            st.line_chart(fc_frame.set_index("target_month")[["Yayımlanan tahmin"]], height=285)
        st.markdown("<div class='gc-footnote'>Canonical actual bağlanana kadar bu grafik yalnız prospectively issued forecast noktalarını gösterir; actual serisi uydurulmaz.</div>", unsafe_allow_html=True)
    else:
        empty_block("KARŞILAŞTIRMA HENÜZ OLUŞMADI", "Canonical prospective forecast geçmişi yok.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='gc-card'><div class='gc-section-title'><span>SENARYOLAR</span></div>"
        f"<div class='gc-empty'><strong>SENARYO MODÜLÜ KAPALI</strong>{SCENARIO_STATUS}<br>"
        "Baz / Yukarı / Aşağı kartları ve tahmin bandı ancak ayrı canonical scenario/interval kontratı sonrası açılır.</div></div>",
        unsafe_allow_html=True,
    )

    diff_value = diff_pct = None
    if forecast and spot and spot.get("price"):
        try:
            diff_value = float(forecast["forecast_value"]) - float(spot["price"])
            diff_pct = diff_value / float(spot["price"]) * 100.0
        except Exception:
            diff_value = diff_pct = None

    cprice, cperf = st.columns(2)
    with cprice:
        if diff_value is not None:
            cls = "gc-positive" if diff_value >= 0 else "gc-negative"
            body = html_row("Indicative spot", fmt_num(spot.get("price"), 2, " USD"))
            body += html_row("H=1 tahmin", fmt_num(forecast.get("forecast_value"), 2, " USD"))
            body += html_row("Fark", f"{diff_value:+,.2f} USD · {diff_pct:+.2f}%", cls)
            note = "<div class='gc-footnote'>Bu bir beklenen getiri değil; iki farklı display değerinin aritmetik karşılaştırmasıdır.</div>"
        else:
            body = "<div class='gc-muted'>Karşılaştırma için hem spot hem issued forecast gerekir.</div>"
            note = ""
        st.markdown(f"<div class='gc-card'><div class='gc-section-title'><span>MEVCUT FİYATA GÖRE FARK</span></div>{body}{note}</div>", unsafe_allow_html=True)

    with cperf:
        issued_n = len(forecast_rows)
        body = html_row("Yayımlanan prospective/live", str(issued_n))
        body += html_row("Realized prospective MAPE", "—", "gc-muted")
        body += html_row("Realized prospective MAE", "—", "gc-muted")
        body += html_row("Yön isabeti", "—", "gc-muted")
        st.markdown(
            "<div class='gc-card'><div class='gc-section-title'><span>MODEL PERFORMANSI</span></div>"
            + body
            + "<div class='gc-footnote'>Üretim-facing performans yalnız outcome gerçekleşip canonical actual bağlandıktan sonra hesaplanır.</div></div>",
            unsafe_allow_html=True,
        )

    if forecast:
        with st.expander("Model bilgisi / Audit"):
            st.write("Model:", forecast.get("model_name"))
            st.write("Versiyon:", forecast.get("model_version"))
            st.write("Evidence:", forecast.get("evidence_class"))
            st.write("Forecast contract ID:", forecast.get("id"))
            st.write("Input snapshot sayısı:", len(forecast.get("forecast_input_snapshot_ids") or []))
            st.write("Git SHA:", forecast.get("git_commit"))
    st.markdown(
        "<div class='gc-info'>Tahmin ekranındaki sayı yalnız immutable canonical forecast ledger'dan gelir. "
        "Kalibre edilmemiş güven, tahmin bandı veya senaryo olasılığı gösterilmez. Yatırım tavsiyesi değildir.</div>",
        unsafe_allow_html=True,
    )


with gecmis:
    latest_hist_update = None
    if forecast_rows:
        latest_hist_update = forecast_rows[0].get("frozen_at") or forecast_rows[0].get("forecast_origin")
    elif decision_rows:
        latest_hist_update = decision_rows[0].get("event_ts")
    page_head("PERFORMANS", "Sistem geçmiş performansı ve karar geçmişi.", latest_hist_update)

    st.markdown(
        "<div class='gc-grid4'>"
        + mini_card("YAYIMLANAN İLERİ TAHMİN", str(len(forecast_rows)), "PROSPECTIVE_SHADOW + LIVE_PRODUCTION")
        + mini_card("PROSPECTIVE MAPE", "—", "Canonical actual sonrası")
        + mini_card("PROSPECTIVE MAE", "—", "Canonical actual sonrası")
        + mini_card("YÖN İSABETİ", "—", "Frozen direction outcome sonrası")
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='gc-card'><div class='gc-section-title'><span>TAHMİN PERFORMANSI</span></div>", unsafe_allow_html=True)
    if forecast_rows:
        fdf = pd.DataFrame(
            {
                "target_month": pd.to_datetime([r.get("target_month") for r in forecast_rows], errors="coerce"),
                "Yayımlanan tahmin": pd.to_numeric([r.get("forecast_value") for r in forecast_rows], errors="coerce"),
            }
        ).dropna().sort_values("target_month")
        if not fdf.empty:
            st.line_chart(fdf.set_index("target_month"), height=300)
        st.markdown("<div class='gc-footnote'>Actual bağlanmadığı sürece equity curve, buy-and-hold kıyası veya portföy getirisi değildir.</div>", unsafe_allow_html=True)
    else:
        empty_block("İLERİYE DÖNÜK PERFORMANS HENÜZ OLUŞMADI", "Prospective/live forecast ledger'da gösterilecek kayıt yok.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='gc-card'><div class='gc-section-title'><span>HATA / KARAR ZAMAN ÇİZELGESİ</span></div>", unsafe_allow_html=True)
    if decision_rows:
        ddf = pd.DataFrame(
            {
                "event_ts": pd.to_datetime([r.get("event_ts") for r in decision_rows], errors="coerce", utc=True),
                "Stored close": pd.to_numeric([r.get("close") for r in decision_rows], errors="coerce"),
            }
        ).dropna().sort_values("event_ts")
        if not ddf.empty:
            st.line_chart(ddf.set_index("event_ts")[["Stored close"]], height=250)
        marker_table = pd.DataFrame(
            {
                "Tarih": [fmt_time(r.get("event_ts")) for r in decision_rows[:10]],
                "Durum": [classification_label(r.get("classification")) for r in decision_rows[:10]],
                "Evidence": [display_state(r.get("evidence_class")) for r in decision_rows[:10]],
            }
        )
        st.dataframe(marker_table, use_container_width=True, hide_index=True)
    else:
        empty_block("KARAR EVENT GEÇMİŞİ YOK", "Portfolio drawdown uydurulmaz; bu alan gerçek Decision Store eventleriyle dolar.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='gc-card'><div class='gc-section-title'><span>SEÇİLMİŞ GEÇMİŞ KAYITLAR</span></div>", unsafe_allow_html=True)
    hist_forecast, hist_decision = st.tabs(["Tahmin kayıtları", "Karar kayıtları"])
    with hist_forecast:
        if forecast_rows:
            frame = pd.DataFrame(
                [
                    {
                        "Hedef": str(r.get("target_month") or "")[:7],
                        "Tahmin": r.get("forecast_value"),
                        "Birim": r.get("unit"),
                        "Evidence": r.get("evidence_class"),
                        "Model": r.get("model_version"),
                        "Origin": fmt_time(r.get("forecast_origin")),
                    }
                    for r in forecast_rows
                ]
            )
            st.dataframe(frame, use_container_width=True, hide_index=True)
        else:
            st.caption("Prospective/live forecast kaydı yok.")
    with hist_decision:
        if decision_rows:
            frame = pd.DataFrame(
                [
                    {
                        "Tarih": fmt_time(r.get("event_ts")),
                        "Durum": classification_label(r.get("classification")),
                        "Neden": r.get("reason_code"),
                        "Evidence": r.get("evidence_class"),
                    }
                    for r in decision_rows
                ]
            )
            st.dataframe(frame, use_container_width=True, hide_index=True)
        else:
            st.caption("Prospective/live decision event kaydı yok.")
    st.markdown("</div>", unsafe_allow_html=True)

    if HISTORICAL_REPLAY.exists():
        with st.expander("Araştırma · HISTORICAL_REPLAY"):
            replay = pd.read_csv(HISTORICAL_REPLAY)
            st.warning("HISTORICAL_REPLAY — prospective/live performans değildir.")
            if {"month", "actual", "patch_r1", "rw"}.issubset(replay.columns):
                rchart = replay[["month", "actual", "patch_r1", "rw"]].copy()
                rchart["month"] = pd.to_datetime(rchart["month"], errors="coerce")
                rchart = rchart.dropna().sort_values("month").set_index("month")
                st.line_chart(rchart, height=260)
            cols = [c for c in ["month", "actual", "patch_r1", "patch_r1_ape", "rw", "rw_ape"] if c in replay.columns]
            st.dataframe(replay[cols].tail(12), use_container_width=True, hide_index=True)

    st.markdown(
        "<div class='gc-note'>YBB/12A strateji getirisi, portföy maksimum düşüşü, trade sayısı, giriş/çıkış fiyatı ve DOĞRU/YANLIŞ trade sonucu "
        "execution/portfolio kontratı olmadan production metriği olarak gösterilmez.</div>",
        unsafe_allow_html=True,
    )
