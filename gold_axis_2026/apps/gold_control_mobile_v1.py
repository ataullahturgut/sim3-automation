from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from decision_source import fetch_current_decision_state, fetch_decision_history
from forecast_source import (
    TRACK_EARLY_INDICATIVE,
    TRACK_MONTH_END,
    fetch_current_forecast,
    fetch_expert_forecast_history,
    fetch_forecast_history,
    fetch_latest_expert_forecasts,
)
from live_sources import fetch_gvz_latest, fetch_xau_history, fetch_xau_spot
from mobile_ui_contract import (
    AUTO_ENSEMBLE_STATUS,
    AUTO_SELECTOR_STATUS,
    EARLY_INDICATIVE_TRACK,
    EXPERT_DISPLAY_ORDER,
    EXPERT_SELECTION_STATUS,
    FINAL_MOCKUP_CONTRACT,
    MONTH_END_TRACK,
    SCENARIO_STATUS,
    arrow_state,
    classification_label,
    decision_view_state,
    deterministic_explanation,
    display_state,
    evidence_badge,
    expert_display_state,
    forecast_view_state,
    monthly_intramonth_relation,
)
from piyasa_contract import filter_history_timeframe, gvz_regime, latest_completed_daily_row, price_delta


ROOT = Path(__file__).resolve().parents[1]
R41_CONFIG = ROOT / "r4_1" / "config" / "frozen_r4_1.json"
HISTORICAL_REPLAY = ROOT / "production_closure" / "production_history_43.csv"

PATCH_EXACT_ID = "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE"
PATCH_GEOMETRY = "L=252 / P=21 / D=32"
MULTI_EXPERT_ARCHITECTURE = "MANIFEST_V1_22_MULTI_EXPERT_BUILD_FIRST_SELECT_LATER"
MACRO_EVENT_STATUS = "BLOCKED_NOT_FULLY_RECOVERED"

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
 --gc-navy:#082a4b; --gc-navy2:#0d3b66; --gc-gold:#f2ad36; --gc-ink:#10294b;
 --gc-muted:#687995; --gc-line:#e3e9f0; --gc-bg:#f8fafc; --gc-green:#14a85a;
 --gc-red:#e33f50; --gc-blue:#1768d0; --gc-amber:#e79d18;
}
[data-testid="stAppViewContainer"]{background:linear-gradient(180deg,#fff 0%,#f8fafc 100%);color:var(--gc-ink)}
.block-container{max-width:900px;padding-top:.25rem;padding-left:.72rem;padding-right:.72rem;padding-bottom:7.4rem}
#MainMenu,footer{visibility:hidden}[data-testid="stHeader"]{background:transparent;height:.15rem}
.gc-shell{display:flex;align-items:center;gap:.65rem;border-bottom:1px solid var(--gc-line);padding:.48rem .12rem .85rem;margin-bottom:.82rem;min-height:58px}
.gc-menu{font-size:1.45rem;font-weight:800;color:var(--gc-navy);width:34px;text-align:center}
.gc-logo{width:43px;height:43px;border:4px solid var(--gc-gold);border-radius:10px;transform:rotate(30deg);display:flex;align-items:center;justify-content:center;flex:0 0 auto}
.gc-logo b{transform:rotate(-30deg);color:var(--gc-gold);font-size:1rem}
.gc-brand{font-size:1.31rem;font-weight:900;letter-spacing:.02em;line-height:1;color:var(--gc-ink)}
.gc-brand small{display:block;color:var(--gc-gold);letter-spacing:.15em;font-size:.61rem;margin-top:.35rem}
.gc-pagehead{display:flex;justify-content:space-between;align-items:flex-start;gap:.9rem;margin:.30rem 0 .75rem}
.gc-pagehead h2{font-size:1.7rem;margin:0;color:var(--gc-ink)}
.gc-pagehead p{margin:.32rem 0 0;color:var(--gc-muted);font-size:.91rem;line-height:1.45}
.gc-updated{font-size:.69rem;color:var(--gc-muted);text-align:right;max-width:145px;line-height:1.45}
.gc-hero{background:linear-gradient(135deg,#052746 0%,#0b3a65 100%);color:#fff;border-radius:20px;padding:1.18rem;margin:.50rem 0 .9rem;box-shadow:0 10px 28px rgba(8,42,75,.14);position:relative;overflow:hidden}
.gc-hero:after{content:"";position:absolute;right:-60px;top:-70px;width:190px;height:190px;border:1px solid rgba(255,255,255,.08);border-radius:50%}
.gc-hero-layout{display:grid;grid-template-columns:95px minmax(0,1.15fr) minmax(150px,.75fr);gap:1rem;align-items:center}
.gc-hero-icon{width:82px;height:82px;border:3px solid var(--gc-gold);border-radius:50%;display:flex;align-items:center;justify-content:center;color:var(--gc-gold);font-size:2.3rem;font-weight:900;box-shadow:0 0 0 8px rgba(242,173,54,.07)}
.gc-kicker{font-size:.73rem;letter-spacing:.08em;text-transform:uppercase;opacity:.82;font-weight:850}.gc-big{font-size:2.65rem;font-weight:900;line-height:1.02;margin:.42rem 0}.gc-mid{font-size:1.55rem;font-weight:900;line-height:1.15;margin:.35rem 0}.gc-meta{font-size:.80rem;opacity:.82;line-height:1.5}
.gc-hero-side{border-left:1px solid rgba(255,255,255,.18);padding-left:1rem}.gc-hero-label{font-size:.75rem;opacity:.72}.gc-hero-value{font-size:1.18rem;font-weight:900;margin:.25rem 0 .7rem;word-break:break-word}.gc-badge{display:inline-block;border:1px solid rgba(255,255,255,.30);border-radius:999px;padding:.34rem .66rem;font-weight:850;font-size:.69rem;margin-top:.55rem}.gc-badge-gold{border-color:var(--gc-gold);color:var(--gc-gold)}
.gc-positive{color:var(--gc-green)!important}.gc-negative{color:var(--gc-red)!important}.gc-warning{color:var(--gc-amber)!important}.gc-blue{color:var(--gc-blue)!important}.gc-muted{color:var(--gc-muted)!important}
.gc-grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.72rem}.gc-grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.72rem}.gc-grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.64rem}
.gc-card{background:#fff;border:1px solid var(--gc-line);border-radius:16px;padding:.95rem 1rem;margin:.62rem 0;box-shadow:0 4px 16px rgba(16,41,75,.035)}
.gc-mini{background:#fff;border:1px solid var(--gc-line);border-radius:15px;padding:.88rem;min-height:112px;box-shadow:0 4px 15px rgba(16,41,75,.03)}
.gc-mini .label{font-size:.69rem;font-weight:850;color:var(--gc-ink);text-transform:uppercase;line-height:1.28}.gc-mini .value{font-size:1.30rem;font-weight:900;margin:.44rem 0 .2rem;color:var(--gc-ink);word-break:break-word}.gc-mini .note{font-size:.72rem;color:var(--gc-muted);line-height:1.42}
.gc-section-title{display:flex;align-items:center;gap:.55rem;font-size:.94rem;font-weight:900;color:var(--gc-ink);margin-bottom:.60rem}.gc-num{display:inline-flex;width:27px;height:27px;border-radius:50%;background:var(--gc-navy);color:#fff;align-items:center;justify-content:center;font-size:.78rem;font-weight:900;flex:0 0 auto}
.gc-row{display:flex;justify-content:space-between;align-items:flex-start;gap:.75rem;padding:.54rem 0;border-bottom:1px solid var(--gc-line);font-size:.87rem}.gc-row:last-child{border-bottom:none}.gc-value{font-weight:850;text-align:right;word-break:break-word;max-width:60%}
.gc-footnote{font-size:.73rem;color:var(--gc-muted);line-height:1.52}.gc-info{background:#f5f8fc;border:1px solid var(--gc-line);border-radius:14px;padding:.85rem .95rem;color:#445a79;font-size:.79rem;line-height:1.5;margin:.7rem 0}.gc-note{background:#fffaf0;border:1px solid #f0d8a7;border-radius:14px;padding:.86rem .95rem;color:#6e582b;font-size:.79rem;line-height:1.5;margin:.7rem 0}.gc-empty{background:#fbfcfe;border:1px dashed #cbd5e1;border-radius:15px;padding:1.05rem;text-align:center;color:var(--gc-muted);margin:.45rem 0}.gc-empty strong{display:block;color:var(--gc-ink);font-size:.92rem;margin-bottom:.30rem}
.gc-replay{background:#f7f9fc;border:1px solid #d9e1ec;border-radius:16px;padding:.95rem 1rem;margin:.70rem 0}.gc-replay-head{display:flex;justify-content:space-between;align-items:center;gap:.7rem;margin-bottom:.55rem}.gc-replay-pill{font-size:.66rem;font-weight:900;color:#8a5b00;background:#fff3d8;border:1px solid #f1d08d;border-radius:999px;padding:.28rem .55rem}
.gc-expert-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.62rem;margin:.65rem 0}.gc-expert{background:#fff;border:1px solid var(--gc-line);border-radius:15px;padding:.86rem .9rem;min-height:142px}.gc-expert .name{font-size:.76rem;font-weight:900;color:var(--gc-ink)}.gc-expert .role{font-size:.67rem;color:var(--gc-muted);line-height:1.35;margin-top:.16rem}.gc-expert .forecast{font-size:1.30rem;font-weight:900;color:var(--gc-ink);margin:.58rem 0 .25rem}.gc-expert .state{font-size:.66rem;font-weight:800;color:var(--gc-muted);line-height:1.35;word-break:break-word}
.gc-lock{display:grid;grid-template-columns:1fr 1fr 2fr;gap:.45rem;background:#f5f8fc;border:1px solid var(--gc-line);border-radius:15px;padding:.72rem;margin:.65rem 0}.gc-lock div{font-size:.70rem;color:var(--gc-muted)}.gc-lock b{display:block;color:var(--gc-ink);font-size:.76rem;margin-top:.12rem;word-break:break-word}
.gc-pipeline{display:flex;flex-wrap:wrap;gap:.32rem;margin:.52rem 0}.gc-step{font-size:.65rem;font-weight:800;color:#405574;background:#f6f8fb;border:1px solid var(--gc-line);border-radius:999px;padding:.30rem .48rem}.gc-arrow{font-size:.65rem;color:#9aa8ba;align-self:center}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--gc-line)!important;border-radius:16px!important;box-shadow:0 4px 16px rgba(16,41,75,.03)!important}[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden}
@media(max-width:620px){.block-container{padding-left:.58rem;padding-right:.58rem;padding-bottom:7.2rem}.gc-shell{gap:.50rem}.gc-logo{width:39px;height:39px}.gc-brand{font-size:1.16rem}.gc-brand small{font-size:.54rem}.gc-pagehead h2{font-size:1.62rem}.gc-pagehead p{font-size:.86rem}.gc-updated{font-size:.64rem;max-width:120px}.gc-hero{padding:1.05rem}.gc-hero-layout{grid-template-columns:70px 1fr;gap:.75rem}.gc-hero-icon{width:62px;height:62px;font-size:1.8rem}.gc-hero-side{grid-column:1/-1;border-left:0;border-top:1px solid rgba(255,255,255,.17);padding-left:0;padding-top:.72rem;display:grid;grid-template-columns:1fr 1fr;gap:.5rem}.gc-big{font-size:2rem}.gc-mid{font-size:1.25rem}.gc-grid4{grid-template-columns:1fr 1fr}.gc-grid3{grid-template-columns:1fr}.gc-grid2{grid-template-columns:1fr 1fr}.gc-lock{grid-template-columns:1fr 1fr}.gc-lock div:last-child{grid-column:1/-1}.gc-mini{min-height:102px;padding:.76rem}.gc-mini .value{font-size:1.15rem}}
@media(max-width:380px){.gc-grid2,.gc-expert-grid{grid-template-columns:1fr}}
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
    return f"<div class='gc-mini'><div class='label'>{label}</div><div class='value {value_class}'>{value}</div><div class='note'>{note}</div></div>"


def load_r41_cfg() -> dict[str, Any]:
    try:
        return json.loads(R41_CONFIG.read_text(encoding="utf-8")) if R41_CONFIG.exists() else {}
    except Exception:
        return {}


def gvz_display_regime(value: Any) -> str:
    try:
        if value is None or pd.isna(value):
            return "KULLANILAMIYOR"
        cfg = load_r41_cfg().get("gvz", {})
        return gvz_regime(float(value), float(cfg.get("full_cap_max", 25.9795)), float(cfg.get("half_cap_max", 30.5238)))
    except Exception:
        return "KULLANILAMIYOR"


def stored_risk_label(dec: dict[str, Any] | None) -> str:
    if not dec:
        return "KULLANILAMIYOR"
    if dec.get("gvz_panic") is True:
        return "PANİK"
    return gvz_display_regime(dec.get("gvz"))


def target_matches(dec: dict[str, Any] | None, fc: dict[str, Any] | None) -> bool:
    return bool(dec and fc and str(dec.get("target_month") or "")[:7] == str(fc.get("target_month") or "")[:7])


def load_replay() -> pd.DataFrame:
    if not HISTORICAL_REPLAY.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(HISTORICAL_REPLAY)
        df["month"] = pd.to_datetime(df.get("month"), errors="coerce")
        return df.dropna(subset=["month"]).sort_values("month")
    except Exception:
        return pd.DataFrame()


def replay_metrics(df: pd.DataFrame) -> dict[str, Any]:
    out: dict[str, Any] = {"n": 0}
    if df.empty:
        return out
    out["n"] = int(len(df))
    for key, ape_col, pred_col in [
        ("patch", "patch_r1_ape", "patch_r1"),
        ("vw", "vw_ape", "vw"),
        ("mom", "mom_ape", "mom"),
        ("rw", "rw_ape", "rw"),
    ]:
        out[f"{key}_mape"] = float(pd.to_numeric(df[ape_col], errors="coerce").mean()) if ape_col in df else None
        if pred_col in df and "actual" in df:
            out[f"{key}_mae"] = float((pd.to_numeric(df["actual"], errors="coerce") - pd.to_numeric(df[pred_col], errors="coerce")).abs().mean())
    return out


def expert_cards(rows: list[dict[str, Any]]) -> str:
    cards = []
    for expert_id in EXPERT_DISPLAY_ORDER:
        x = expert_display_state(expert_id, rows)
        value = fmt_num(x.get("forecast_value"), 2, " USD") if x.get("issued") else "—"
        note = f"{x['role']}<br>{x['status']}"
        cards.append(
            "<div class='gc-expert'>"
            f"<div class='name'>{x['label']}</div><div class='role'>{x['model_version']}</div>"
            f"<div class='forecast'>{value}</div><div class='state'>{note}</div></div>"
        )
    return "<div class='gc-expert-grid'>" + "".join(cards) + "</div>"


def selector_lock_html() -> str:
    return (
        "<div class='gc-lock'>"
        f"<div>AUTO SELECTOR<b>{AUTO_SELECTOR_STATUS}</b></div>"
        f"<div>AUTO ENSEMBLE<b>{AUTO_ENSEMBLE_STATUS}</b></div>"
        f"<div>SELECTION / AGGREGATION RULE<b>{EXPERT_SELECTION_STATUS}</b></div>"
        "</div>"
    )


def pipeline_html() -> str:
    steps = [
        "Multi-Expert Monthly Forecast Engine", "Monthly Direction / Prior / Context", "Fast / Slow",
        "Macro Event", "Emergency", "BOCPD", "GVZ risk cap", "Frozen Final Decision State",
        "Immutable Decision Snapshot / Event Ledger",
    ]
    bits = []
    for i, step in enumerate(steps):
        if i:
            bits.append("<span class='gc-arrow'>→</span>")
        bits.append(f"<span class='gc-step'>{step}</span>")
    return "<div class='gc-pipeline'>" + "".join(bits) + "</div>"


def expert_history_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if df.empty or not {"target_month", "expert_id", "forecast_value"}.issubset(df.columns):
        return pd.DataFrame()
    df["target_month"] = pd.to_datetime(df["target_month"], errors="coerce")
    df["forecast_value"] = pd.to_numeric(df["forecast_value"], errors="coerce")
    return df.dropna(subset=["target_month", "forecast_value"]).sort_values(["target_month", "expert_id"])


url = db_url()
decision = safe_call(lambda: fetch_current_decision_state(url), None) if url else None
decision_rows = safe_call(lambda: fetch_decision_history(url), []) if url else []
forecast = safe_call(lambda: fetch_current_forecast(url), None) if url else None
forecast_rows = safe_call(lambda: fetch_forecast_history(url), []) if url else []
month_end_experts = safe_call(lambda: fetch_latest_expert_forecasts(url, TRACK_MONTH_END), []) if url else []
early_experts = safe_call(lambda: fetch_latest_expert_forecasts(url, TRACK_EARLY_INDICATIVE), []) if url else []
month_end_history = safe_call(lambda: fetch_expert_forecast_history(url, TRACK_MONTH_END), []) if url else []
early_history = safe_call(lambda: fetch_expert_forecast_history(url, TRACK_EARLY_INDICATIVE), []) if url else []
spot = safe_call(get_spot, None)
hist, hist_meta = safe_call(get_xau_history, (pd.DataFrame(), {}))
gvz = safe_call(get_gvz, None)
replay = load_replay()
rmetrics = replay_metrics(replay)

st.markdown("<div class='gc-shell'><div class='gc-menu'>☰</div><div class='gc-logo'><b>G</b></div><div class='gc-brand'>GOLD CONTROL<small>DECISION SYSTEM</small></div></div>", unsafe_allow_html=True)
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
            f"<div class='gc-big'>{fmt_num(spot.get('price'),2)} USD</div><div class='{delta_class}'><b>{delta_text}</b></div>"
            f"<span class='gc-badge'>{freshness}</span><div class='gc-meta' style='margin-top:.55rem'>Kaynak: {display_state(spot.get('source'),'Gold API')} · display only / no model use</div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(empty_html("CANLI XAU/USD KULLANILAMIYOR", "Kaynak veya bağlantı durumu doğrulanamadı."), unsafe_allow_html=True)
    state = decision_view_state(decision)
    st.markdown(
        "<div class='gc-grid3'>"
        + mini_card("TAMAMLANMIŞ GÜNLÜK CLOSE", fmt_num(completed_close, 2, " USD"), "XAUS operasyonel cross-check")
        + mini_card("GVZ", fmt_num(None if not gvz else gvz.get("close"), 2), f"Risk görünümü: {gvz_display_regime(None if not gvz else gvz.get('close'))}")
        + mini_card("SON KAYITLI DURUM", state.title, "Decision Store" if decision else "Henüz display-eligible kayıt yok")
        + "</div>", unsafe_allow_html=True)
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
    st.markdown(f"<div class='gc-info'><b>Karar bağlamı:</b> {state.title}. Canlı spot yalnız piyasa izleme verisidir. <b>Canlı spot ≠ son EOD karar.</b></div>", unsafe_allow_html=True)


elif nav == "◉ Görünüm":
    updated = None if not decision else decision.get("generated_at") or decision.get("decision_as_of")
    page_head("GÖRÜNÜM", "Aylık prior ile intramonth katmanların kayıtlı durumunu birlikte okuyun.", updated)
    state = decision_view_state(decision)
    monthly = None if not decision else decision.get("monthly_direction_3m")
    ma, mt = arrow_state(monthly)
    live_gvz = None if not gvz else gvz.get("close")
    risk_label = stored_risk_label(decision) if decision else gvz_display_regime(live_gvz)
    relation = monthly_intramonth_relation(decision)
    badge_text = evidence_badge(decision.get("evidence_class"))[0] if decision else "YAYIMLANMADI"
    st.markdown(
        "<div class='gc-hero'><div class='gc-hero-layout'><div class='gc-hero-icon'>◎</div>"
        f"<div><div class='gc-kicker'>MEVCUT KAYITLI DURUM</div><div class='gc-mid'>{state.title}</div><div class='gc-meta'>{state.subtitle}</div><span class='gc-badge'>{badge_text}</span></div>"
        f"<div class='gc-hero-side'><div><div class='gc-hero-label'>MONTHLY PRIOR</div><div class='gc-hero-value {tone_class(mt)}'>{ma} {display_state(monthly,'YAYIMLANMADI')}</div></div>"
        f"<div><div class='gc-hero-label'>INTRAMONTH İLİŞKİ</div><div class='gc-hero-value' style='font-size:.88rem'>{relation}</div></div></div></div></div>", unsafe_allow_html=True)

    summary = html_row("Frozen Final Decision State", state.title)
    summary += html_row("Monthly prior", display_state(monthly, "YAYIMLANMADI"))
    summary += html_row("Prior / intramonth", relation)
    summary += html_row("Expert selector", EXPERT_SELECTION_STATUS)
    st.markdown(f"<div class='gc-card'>{section_header(1,'SİNYAL ÖZETİ')}{summary}{selector_lock_html()}</div>", unsafe_allow_html=True)

    if decision:
        fa, ft = arrow_state(decision.get("fast_state")); sa, stn = arrow_state(decision.get("slow_state"))
        model_body = f"<div class='gc-mid {tone_class(mt)}'>{ma} {display_state(monthly)}</div><div class='gc-footnote'>Stratejik anchor/prior; günlük işlem emri değildir.</div>"
        fs_body = html_row("FAST", f"{fa} {display_state(decision.get('fast_state'))}", tone_class(ft)) + html_row("SLOW", f"{sa} {display_state(decision.get('slow_state'))}", tone_class(stn))
    else:
        model_body = "<div class='gc-mid gc-muted'>—</div><div class='gc-footnote'>Monthly context yalnız stored state ile gösterilir. Canonical forecast seçicisi şu an yoktur.</div>"
        fs_body = html_row("FAST", "YAYIMLANMADI", "gc-muted") + html_row("SLOW", "YAYIMLANMADI", "gc-muted")
    st.markdown("<div class='gc-grid2'>" + f"<div class='gc-card'>{section_header(2,'MODEL YÖNÜ (AYLIK)')}{model_body}</div>" + f"<div class='gc-card'>{section_header(3,'FAST / SLOW TEYİDİ')}{fs_body}</div></div>", unsafe_allow_html=True)

    risk_rows = html_row("Risk durumu", risk_label) + html_row("GVZ", fmt_num(live_gvz if not decision else decision.get("gvz"), 2)) + html_row("Rol", "Risk cap · yön üretmez")
    st.markdown(f"<div class='gc-card'>{section_header(4,'RİSK SEVİYESİ')}{risk_rows}</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(section_header(5, "SİNYAL ZAMAN ÇİZELGESİ"), unsafe_allow_html=True)
        if not hist.empty:
            chart = filter_history_timeframe(hist, "6A")
            if not chart.empty:
                st.line_chart(chart.set_index("date")[["close"]], height=255)
            st.caption(f"Persisted Decision Store event sayısı: {len(decision_rows)}. Fiyat hareketi tek başına karar eventi değildir.")
        else:
            st.markdown(empty_html("ZAMAN ÇİZELGESİ KULLANILAMIYOR", "Display-authorized fiyat tarihçesi okunamadı."), unsafe_allow_html=True)

    if decision:
        emergency_rows = html_row("Macro Event", display_state(decision.get("macro_event_state"), MACRO_EVENT_STATUS))
        emergency_rows += html_row("Emergency · Level", display_state(decision.get("level_emergency")))
        emergency_rows += html_row("Emergency · Reversal", display_state(decision.get("reversal_emergency")))
        emergency_rows += html_row("BOCPD", display_state(decision.get("bocpd_context")))
    else:
        emergency_rows = html_row("Macro Event", MACRO_EVENT_STATUS, "gc-warning") + html_row("Emergency", "YAYIMLANMADI", "gc-muted") + html_row("BOCPD", "YAYIMLANMADI", "gc-muted")
    explanation = deterministic_explanation(decision)
    st.markdown("<div class='gc-grid2'>" + f"<div class='gc-card'>{section_header(6,'EMERGENCY DURUMU')}{emergency_rows}</div>" + f"<div class='gc-card'>{section_header(7,'SİSTEM YORUMU')}<div style='font-style:italic;line-height:1.6'>{explanation}</div>{pipeline_html()}</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='gc-note'>Aylık prior ile intramonth durumun çelişmesi mümkündür ve tek başına hata değildir. Güncelleme yalnız Fast/Slow, Macro Event, Emergency, BOCPD ve GVZ'nin dondurulmuş rolleri üzerinden yapılır.</div>", unsafe_allow_html=True)


elif nav == "↗ Tahmin":
    expert_update = month_end_experts[0].get("as_of") if month_end_experts else (early_experts[0].get("as_of") if early_experts else None)
    updated = forecast.get("frozen_at") if forecast else expert_update
    page_head("TAHMİN", "Multi-Expert H=1 aylık forecast; expert çıktıları selector'dan önce ayrı tutulur.", updated)
    fstate = forecast_view_state(forecast)
    if forecast:
        target = str(forecast.get("target_month") or "")[:7]
        badge = evidence_badge(forecast.get("evidence_class"))[0]
        hero_title = fmt_num(forecast.get("forecast_value"), 2, " USD")
        hero_sub = f"Hedef dönem: {target}"
        direction = decision.get("monthly_direction_3m") if target_matches(decision, forecast) else None
        da, _ = arrow_state(direction)
        direction_text = f"{da} {display_state(direction,'—')}"
        origin_text = fmt_time(forecast.get("forecast_origin"))
    else:
        hero_title = fstate.title; hero_sub = fstate.subtitle; badge = "KANONİK SELECTOR YOK"; direction_text = "—"; origin_text = "—"
    st.markdown(
        "<div class='gc-hero'><div class='gc-hero-layout'><div class='gc-hero-icon'>↗</div>"
        f"<div><div class='gc-kicker'>GELECEK AY TAHMİNİ</div><div class='gc-mid'>{hero_title}</div><div class='gc-meta'>{hero_sub}</div><span class='gc-badge gc-badge-gold'>{badge}</span></div>"
        f"<div class='gc-hero-side'><div><div class='gc-hero-label'>MONTHLY DIRECTION / PRIOR</div><div class='gc-hero-value'>{direction_text}</div></div><div><div class='gc-hero-label'>CANONICAL ORIGIN</div><div class='gc-hero-value' style='font-size:.92rem'>{origin_text}</div></div></div></div></div>", unsafe_allow_html=True)

    st.markdown("<div class='gc-card'><div class='gc-section-title'>MULTI-EXPERT MONTHLY FORECAST ENGINE</div><div class='gc-footnote'>Aynı target için her expert ayrı kimlik, lineage ve evidence ile saklanır. Hiçbiri hindsight ile otomatik kazanan yapılmaz.</div>" + expert_cards(month_end_experts) + selector_lock_html() + "</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='gc-card'><div class='gc-metadata'>"
        f"<div class='gc-meta-item'>▣ <span><b>Patch V7:</b> {PATCH_EXACT_ID}</span></div>"
        f"<div class='gc-meta-item'>⌘ <span><b>Patch geometry:</b> {PATCH_GEOMETRY}</span></div>"
        "<div class='gc-meta-item'>◉ <span><b>VW:</b> VW_AUDITED_SHADOW_V2 · BLOCKED_NOT_PROVEN_EXECUTABLE</span></div>"
        "<div class='gc-meta-item'>↗ <span><b>3M:</b> MOMENTUM_3M_R1 · forward source binding bekliyor</span></div>"
        "<div class='gc-meta-item'>— <span><b>RW:</b> RW_R1 · mandatory benchmark · forward source binding bekliyor</span></div>"
        f"<div class='gc-meta-item'>✓ <span><b>Architecture:</b> {MULTI_EXPERT_ARCHITECTURE}</span></div>"
        "</div></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI</div>", unsafe_allow_html=True)
        mdf = expert_history_frame(month_end_history)
        if not mdf.empty:
            pivot = mdf.pivot_table(index="target_month", columns="expert_id", values="forecast_value", aggfunc="last")
            st.line_chart(pivot, height=285)
            st.caption("MONTH_END_EXPERT: ayrı expert çıktıları. Bu grafik selector/ensemble sonucu değildir.")
        elif not replay.empty and {"actual", "patch_r1", "vw", "mom", "rw"}.issubset(replay.columns):
            st.markdown("<div class='gc-replay-head'><strong>Prospective expert geçmişi henüz yok; aşağıdaki seri araştırma referansıdır.</strong><span class='gc-replay-pill'>HISTORICAL_REPLAY</span></div>", unsafe_allow_html=True)
            research = replay.tail(12).set_index("month")[["actual", "patch_r1", "vw", "mom", "rw"]].rename(columns={"actual":"Gerçekleşen","patch_r1":"Causal Patch","vw":"VW-MIDAS-MSVR","mom":"3M Momentum","rw":"Random Walk"})
            st.line_chart(research, height=285)
            st.caption("Historical replay, prospective forecast veya selector kanıtı değildir.")
        else:
            st.markdown(empty_html("KARŞILAŞTIRMA HENÜZ OLUŞMADI", "MONTH_END_EXPERT geçmişi yok."), unsafe_allow_html=True)

        st.markdown("<div class='gc-section-title' style='margin-top:1rem'>EARLY INDICATIVE · AYRI REVISION TRACK</div>", unsafe_allow_html=True)
        if early_experts:
            st.markdown(expert_cards(early_experts), unsafe_allow_html=True)
            st.caption("EARLY_INDICATIVE yalnız PIT-safe yeni verilerle revision history'dir; kanonik ay-sonu H=1 değildir.")
        else:
            st.markdown(empty_html("EARLY INDICATIVE HENÜZ YOK", "Yeni eligible completed-session as_of çalışmaları ayrı track'te birikecek."), unsafe_allow_html=True)

    spot_value = None if not spot else spot.get("price")
    if forecast and spot_value:
        try:
            diff_value = float(forecast["forecast_value"]) - float(spot_value)
            diff_pct = diff_value / float(spot_value) * 100
            diff_display = f"{diff_value:+,.2f} USD · {diff_pct:+.2f}%"
            diff_class = "gc-positive" if diff_value >= 0 else "gc-negative"
        except Exception:
            diff_display, diff_class = "—", "gc-muted"
    else:
        diff_display, diff_class = "—", "gc-muted"
    st.markdown(
        "<div class='gc-grid3'>"
        "<div class='gc-card'><div class='gc-section-title'>MEVCUT FİYATA GÖRE FARK</div>"
        + html_row("Indicative spot", fmt_num(spot_value,2," USD")) + html_row("Canonical H=1", fmt_num(None if not forecast else forecast.get("forecast_value"),2," USD")) + html_row("Fark", diff_display, diff_class) + "<div class='gc-footnote'>Expert bazlı farklar beklenen getiri olarak sunulmaz.</div></div>"
        "<div class='gc-card'><div class='gc-section-title'>MODEL PERFORMANSI</div><div class='gc-footnote'>Prospective scorecard yalnız realized canonical forecast sonrası oluşur. Expert araştırma replay'i ayrı aşağıda tutulur.</div></div>"
        f"<div class='gc-card'><div class='gc-section-title'>NOT</div><div class='gc-footnote'>Scenario status: <b>{SCENARIO_STATUS}</b>.<br><br>Auto selector: <b>{AUTO_SELECTOR_STATUS}</b><br>Auto ensemble: <b>{AUTO_ENSEMBLE_STATUS}</b><br><br>Yatırım tavsiyesi değildir.</div></div>"
        "</div>", unsafe_allow_html=True)

    if not replay.empty:
        st.markdown(
            "<div class='gc-replay'><div class='gc-replay-head'><strong>MULTI-EXPERT MODEL ARAŞTIRMA KANITI</strong><span class='gc-replay-pill'>HISTORICAL_REPLAY</span></div><div class='gc-grid4'>"
            + mini_card("CAUSAL PATCH MAPE", fmt_num(rmetrics.get("patch_mape"),2,"%"), "Historical replay")
            + mini_card("VW-MIDAS-MSVR MAPE", fmt_num(rmetrics.get("vw_mape"),2,"%"), "Historical analytical reference")
            + mini_card("3M MOMENTUM MAPE", fmt_num(rmetrics.get("mom_mape"),2,"%"), "Direction/context challenger")
            + mini_card("RANDOM WALK MAPE", fmt_num(rmetrics.get("rw_mape"),2,"%"), "Mandatory benchmark")
            + "</div><div class='gc-footnote' style='margin-top:.7rem'>2026 sonuçlarına bakarak winner/selector türetilmez. Selector araştırması ancak temiz karşılaştırmalı geçmişten sonra rolling-origin leakage-safe yapılır.</div></div>", unsafe_allow_html=True)


else:
    latest = None
    if month_end_history:
        latest = month_end_history[0].get("as_of")
    elif early_history:
        latest = early_history[0].get("as_of")
    page_head("GEÇMİŞ", "Canonical performans ile ayrı expert/revision ledger geçmişini karıştırmadan izleyin.", latest)

    st.markdown("<div class='gc-footnote' style='margin-bottom:.45rem'><b>PROSPECTIVE / LIVE CANONICAL SCORECARD</b> · Expert outputs ve Historical Replay bu kartlara karıştırılmaz.</div>", unsafe_allow_html=True)
    st.markdown("<div class='gc-grid4'>" + mini_card("MAPE","—","Realized canonical prospective outcome sonrası") + mini_card("MAE (USD)","—","Realized canonical prospective outcome sonrası") + mini_card("YÖN DOĞRULUĞU","—","Frozen outcome tanımı sonrası") + mini_card("TOPLAM TAHMİN",str(len(forecast_rows)),"Governed canonical issued rows") + "</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>TAHMİN – GERÇEKLEŞEN KARŞILAŞTIRMASI</div>", unsafe_allow_html=True)
        if forecast_rows:
            fdf = pd.DataFrame({"target_month":pd.to_datetime([r.get("target_month") for r in forecast_rows],errors="coerce"),"Canonical Forecast":pd.to_numeric([r.get("forecast_value") for r in forecast_rows],errors="coerce")}).dropna().sort_values("target_month")
            if not fdf.empty:
                st.line_chart(fdf.set_index("target_month")[["Canonical Forecast"]], height=285)
        else:
            st.markdown(empty_html("İLERİYE DÖNÜK KANONİK PERFORMANS HENÜZ OLUŞMADI", "Selector/aggregation rule kanıtlanmadığı için canonical forecast scorecard boş kalır."), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>HATA ORANI ZAMAN ÇİZGİSİ</div>", unsafe_allow_html=True)
        st.markdown(empty_html("REALIZED PROSPECTIVE HATA HENÜZ YOK", "Outcome gerçekleşmeden canonical hata oranı üretilmez."), unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>SEÇİLMİŞ GERÇEKLEŞEN TAHMİNLER</div>", unsafe_allow_html=True)
        if forecast_rows:
            frame = pd.DataFrame([{"Hedef Ay":str(r.get("target_month") or "")[:7],"Canonical Forecast":r.get("forecast_value"),"Gerçekleşen":None,"Hata (%)":None,"Evidence":r.get("evidence_class")} for r in forecast_rows])
            st.dataframe(frame,width="stretch",hide_index=True)
        else:
            st.markdown(empty_html("KANONİK PROSPECTIVE KAYIT YOK", EXPERT_SELECTION_STATUS), unsafe_allow_html=True)

    st.markdown("<div class='gc-card'><div class='gc-section-title'>MULTI-EXPERT FORECAST LEDGER</div>" + selector_lock_html() + "<div class='gc-footnote'>MONTH_END_EXPERT ile EARLY_INDICATIVE farklı track'lerdir; birleştirilmez.</div></div>", unsafe_allow_html=True)
    mdf = expert_history_frame(month_end_history)
    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>MONTH_END_EXPERT · KARŞILAŞTIRMALI GEÇMİŞ</div>", unsafe_allow_html=True)
        if not mdf.empty:
            pivot = mdf.pivot_table(index="target_month",columns="expert_id",values="forecast_value",aggfunc="last")
            st.line_chart(pivot,height=285)
            table = mdf[["target_month","expert_id","model_version","forecast_value","evidence_class","as_of"]].tail(20).copy()
            table["target_month"] = table["target_month"].dt.strftime("%Y-%m")
            st.dataframe(table,width="stretch",hide_index=True)
        else:
            st.markdown(empty_html("MONTH_END_EXPERT KAYDI YOK", "İlk eligible expert çıktıları burada ayrı ayrı birikecek."), unsafe_allow_html=True)

    edf = expert_history_frame(early_history)
    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>EARLY INDICATIVE · REVISION HISTORY</div>", unsafe_allow_html=True)
        if not edf.empty:
            pivot = edf.pivot_table(index="as_of",columns="expert_id",values="forecast_value",aggfunc="last") if "as_of" in edf.columns else pd.DataFrame()
            if not pivot.empty:
                st.line_chart(pivot,height=255)
            st.caption("Early Indicative canonical month-end H=1 scorecard'a karıştırılmaz.")
        else:
            st.markdown(empty_html("EARLY INDICATIVE REVISION YOK", "PIT-safe completed-session güncellemeleri ayrı track'te saklanacak."), unsafe_allow_html=True)

    if not replay.empty and {"actual","patch_r1","vw","mom","rw"}.issubset(replay.columns):
        st.markdown("<div class='gc-replay'><div class='gc-replay-head'><strong>ARAŞTIRMA GEÇMİŞİ — AYRI KANIT SINIFI</strong><span class='gc-replay-pill'>HISTORICAL_REPLAY</span></div><div class='gc-grid4'>" + mini_card("PATCH MAPE",fmt_num(rmetrics.get("patch_mape"),2,"%"),"Historical replay") + mini_card("VW MAPE",fmt_num(rmetrics.get("vw_mape"),2,"%"),"Historical analytical") + mini_card("3M MAPE",fmt_num(rmetrics.get("mom_mape"),2,"%"),"Context challenger") + mini_card("RW MAPE",fmt_num(rmetrics.get("rw_mape"),2,"%"),"Benchmark") + "</div></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='gc-section-title'>HISTORICAL_REPLAY · GERÇEKLEŞEN / DÖRT EXPERT</div>", unsafe_allow_html=True)
            research = replay.tail(18).set_index("month")[["actual","patch_r1","vw","mom","rw"]].rename(columns={"actual":"Gerçekleşen","patch_r1":"Causal Patch","vw":"VW-MIDAS-MSVR","mom":"3M Momentum","rw":"Random Walk"})
            st.line_chart(research,height=300)
            st.caption("Replay prospective değildir ve selector/ensemble otoritesi yaratmaz.")

    st.markdown("<div class='gc-note'>Build first → separate expert outputs → Early Indicative revision track → clean comparable evidence → selector/combination research → leakage-safe rolling-origin validation → only then change-control freeze. Sonuç üstün değilse expert'ler ayrı kalır.</div>", unsafe_allow_html=True)


st.markdown("<div id='system-health'></div>", unsafe_allow_html=True)
with st.expander("Sistem / Veri Sağlığı / Audit"):
    st.write("UI contract:", FINAL_MOCKUP_CONTRACT)
    st.write("Architecture:", MULTI_EXPERT_ARCHITECTURE)
    st.write("Neon:", "BAĞLI" if url else "YAPILANDIRILMADI")
    st.write("Decision Store:", "KAYIT VAR" if decision else "KAYIT YOK")
    st.write("Canonical forecast ledger:", "KAYIT VAR" if forecast else "KAYIT YOK / SELECTOR NOT PROVEN")
    st.write("MONTH_END_EXPERT rows:", len(month_end_history))
    st.write("EARLY_INDICATIVE rows:", len(early_history))
    st.write("Auto selector:", AUTO_SELECTOR_STATUS)
    st.write("Auto ensemble:", AUTO_ENSEMBLE_STATUS)
    st.write("Selector status:", EXPERT_SELECTION_STATUS)
    st.write("Historical replay:", "MEVCUT" if not replay.empty else "YOK")
