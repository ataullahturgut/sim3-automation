from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from decision_source import fetch_current_decision_state, fetch_decision_history
from engine_observability_contract import (
    ENGINE_OBSERVABILITY_CONTRACT,
    build_engine_inventory,
    engine_inventory_counts,
)
from forecast_source import (
    TRACK_EARLY_INDICATIVE,
    TRACK_HISTORICAL_REPLAY,
    TRACK_MONTH_END,
    fetch_current_forecast,
    fetch_expert_forecast_history,
    fetch_forecast_history,
    fetch_latest_expert_forecasts,
)
from live_sources import fetch_gvz_latest, fetch_xau_history, fetch_xau_spot
from runtime_source import fetch_runtime_observability
from aug31_state_replay_source import fetch_aug31_state_replay
from aug31_replay_expansion_source import fetch_aug31_replay_expansion
from aug31_replay_expansion_display import attach_aug31_replay_expansion
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
MULTI_EXPERT_ARCHITECTURE = "MANIFEST_V1_26_MULTI_EXPERT_BUILD_FIRST_SELECT_LATER_ENGINE_OBSERVABILITY"
MACRO_EVENT_STATUS = "BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED"
SELECTOR_RULE_STATUS = "NOT_PROVEN_EXPERT_SELECTION_RULE"
if EXPERT_SELECTION_STATUS != SELECTOR_RULE_STATUS:
    raise RuntimeError("MANIFEST_V1_26_SELECTOR_STATUS_MISMATCH")

st.set_page_config(page_title="Gold Control", page_icon="🟡", layout="centered", initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
:root{--gc-navy:#082a4b;--gc-navy2:#0d3b66;--gc-gold:#f2ad36;--gc-ink:#10294b;--gc-muted:#687995;--gc-line:#e3e9f0;--gc-green:#17a85b;--gc-red:#e43d4e;--gc-blue:#1976d2;--gc-amber:#e59d1c;--gc-soft:#f6f8fb}
[data-testid="stAppViewContainer"]{background:linear-gradient(180deg,#fff 0,#f8fafc 100%);color:var(--gc-ink)}
.block-container{max-width:860px;padding:.45rem .78rem 7.4rem}
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stToolbarActions"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],.stDeployButton{display:none!important;visibility:hidden!important}
[data-testid="stHeader"]{height:0!important;min-height:0!important;background:transparent!important}.vg-tooltip,#vg-tooltip-element{display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important}
.gc-shell{display:flex;align-items:center;gap:.72rem;border-bottom:1px solid var(--gc-line);padding:.55rem .1rem .9rem;margin-bottom:.82rem;min-height:54px}.gc-menu{width:36px;text-align:center;color:var(--gc-navy);font-size:1.38rem;font-weight:900}.gc-logo{width:42px;height:42px;border:4px solid var(--gc-gold);border-radius:10px;transform:rotate(30deg);display:flex;align-items:center;justify-content:center;flex:0 0 auto}.gc-logo b{transform:rotate(-30deg);color:var(--gc-gold);font-size:1rem}.gc-brand{font-size:1.27rem;font-weight:900;letter-spacing:.02em;line-height:1;color:var(--gc-ink)}.gc-brand small{display:block;color:var(--gc-gold);letter-spacing:.16em;font-size:.62rem;margin-top:.36rem;font-weight:800}
.gc-pagehead{display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;margin:.28rem 0 .72rem}.gc-pagehead h2{font-size:1.62rem;margin:0;color:var(--gc-ink)}.gc-pagehead p{margin:.28rem 0 0;color:var(--gc-muted);font-size:.86rem;line-height:1.42}.gc-updated{font-size:.69rem;color:var(--gc-muted);text-align:right;max-width:130px;line-height:1.42}
.gc-hero{background:linear-gradient(135deg,#052746 0%,#0b3a65 100%);color:#fff;border-radius:20px;padding:1.18rem;margin:.5rem 0 .86rem;box-shadow:0 10px 28px rgba(8,42,75,.14);position:relative;overflow:hidden}.gc-hero:after{content:"";position:absolute;right:-60px;top:-70px;width:190px;height:190px;border:1px solid rgba(255,255,255,.08);border-radius:50%}.gc-hero-layout{display:grid;grid-template-columns:84px minmax(0,1.15fr) minmax(150px,.72fr);gap:1rem;align-items:center}.gc-hero-icon{width:72px;height:72px;border:3px solid var(--gc-gold);border-radius:50%;display:flex;align-items:center;justify-content:center;color:var(--gc-gold);font-size:2rem;font-weight:900;box-shadow:0 0 0 8px rgba(242,173,54,.07)}
.gc-kicker{font-size:.71rem;letter-spacing:.08em;text-transform:uppercase;opacity:.82;font-weight:850}.gc-big{font-size:2.45rem;font-weight:900;line-height:1.04;margin:.42rem 0}.gc-mid{font-size:1.42rem;font-weight:900;line-height:1.16;margin:.36rem 0}.gc-meta{font-size:.78rem;opacity:.82;line-height:1.48}.gc-hero-side{border-left:1px solid rgba(255,255,255,.18);padding-left:1rem}.gc-hero-label{font-size:.72rem;opacity:.72}.gc-hero-value{font-size:1.05rem;font-weight:900;margin:.25rem 0 .72rem;word-break:break-word}.gc-badge{display:inline-block;border:1px solid rgba(255,255,255,.30);border-radius:999px;padding:.32rem .62rem;font-weight:850;font-size:.67rem;margin-top:.54rem}.gc-badge-gold{border-color:var(--gc-gold);color:var(--gc-gold)}
.gc-positive{color:var(--gc-green)!important}.gc-negative{color:var(--gc-red)!important}.gc-warning{color:var(--gc-amber)!important}.gc-blue{color:var(--gc-blue)!important}.gc-muted{color:var(--gc-muted)!important}.gc-grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.72rem}.gc-grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.72rem}.gc-grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.64rem}
.gc-card{background:#fff;border:1px solid var(--gc-line);border-radius:16px;padding:.95rem 1rem;margin:.62rem 0;box-shadow:0 4px 16px rgba(16,41,75,.035)}.gc-mini{background:#fff;border:1px solid var(--gc-line);border-radius:15px;padding:.86rem;min-height:108px;box-shadow:0 4px 15px rgba(16,41,75,.03)}.gc-mini .label{font-size:.68rem;font-weight:850;color:var(--gc-ink);text-transform:uppercase;line-height:1.28}.gc-mini .value{font-size:1.24rem;font-weight:900;margin:.44rem 0 .2rem;color:var(--gc-ink);word-break:break-word}.gc-mini .note{font-size:.70rem;color:var(--gc-muted);line-height:1.42}.gc-section-title{display:flex;align-items:center;gap:.55rem;font-size:.93rem;font-weight:900;color:var(--gc-ink);margin-bottom:.60rem}.gc-num{display:inline-flex;width:27px;height:27px;border-radius:50%;background:var(--gc-navy);color:#fff;align-items:center;justify-content:center;font-size:.77rem;font-weight:900;flex:0 0 auto}.gc-row{display:flex;justify-content:space-between;align-items:flex-start;gap:.75rem;padding:.53rem 0;border-bottom:1px solid var(--gc-line);font-size:.85rem}.gc-row:last-child{border-bottom:none}.gc-value{font-weight:850;text-align:right;word-break:break-word;max-width:62%}
.gc-footnote{font-size:.72rem;color:var(--gc-muted);line-height:1.52}.gc-info{background:#f5f8fc;border:1px solid var(--gc-line);border-radius:14px;padding:.84rem .94rem;color:#445a79;font-size:.78rem;line-height:1.5;margin:.7rem 0}.gc-note{background:#fffaf0;border:1px solid #f0d8a7;border-radius:14px;padding:.85rem .94rem;color:#6e582b;font-size:.78rem;line-height:1.5;margin:.7rem 0}.gc-empty{background:#fbfcfe;border:1px dashed #cbd5e1;border-radius:15px;padding:1.05rem;text-align:center;color:var(--gc-muted);margin:.45rem 0;min-height:104px;display:flex;flex-direction:column;justify-content:center}.gc-empty strong{display:block;color:var(--gc-ink);font-size:.92rem;margin-bottom:.30rem}.gc-replay{background:#f7f9fc;border:1px solid #d9e1ec;border-radius:16px;padding:.95rem 1rem;margin:.72rem 0}.gc-replay-head{display:flex;justify-content:space-between;align-items:center;gap:.7rem;margin-bottom:.55rem}.gc-replay-pill{font-size:.65rem;font-weight:900;color:#8a5b00;background:#fff3d8;border:1px solid #f1d08d;border-radius:999px;padding:.28rem .55rem}
.gc-expert-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.62rem;margin:.68rem 0}.gc-expert{background:#fff;border:1px solid var(--gc-line);border-top:3px solid var(--gc-gold);border-radius:15px;padding:.84rem .9rem;min-height:138px;box-shadow:0 3px 13px rgba(16,41,75,.025)}.gc-expert .name{font-size:.76rem;font-weight:900;color:var(--gc-ink)}.gc-expert .role{font-size:.66rem;color:var(--gc-muted);line-height:1.35;margin-top:.16rem;overflow-wrap:anywhere;word-break:break-word}.gc-expert .forecast{font-size:1.28rem;font-weight:900;color:var(--gc-ink);margin:.56rem 0 .24rem}.gc-expert .state{font-size:.65rem;font-weight:800;color:var(--gc-muted);line-height:1.35;word-break:break-word;overflow-wrap:anywhere}.gc-expert .note{overflow-wrap:anywhere;word-break:break-word}.gc-track-head{display:flex;justify-content:space-between;align-items:center;gap:.7rem;margin-top:.9rem;padding-top:.75rem;border-top:1px solid var(--gc-line)}.gc-track-head b{font-size:.78rem;color:var(--gc-ink)}.gc-track-pill{font-size:.62rem;font-weight:900;border:1px solid var(--gc-line);background:var(--gc-soft);border-radius:999px;padding:.26rem .52rem;color:#53657e}.gc-lock{display:grid;grid-template-columns:1fr 1fr 2fr;gap:.45rem;background:#f5f8fc;border:1px solid var(--gc-line);border-radius:15px;padding:.72rem;margin:.68rem 0}.gc-lock div{font-size:.69rem;color:var(--gc-muted)}.gc-lock b{display:block;color:var(--gc-ink);font-size:.74rem;margin-top:.12rem;word-break:break-word}.gc-pipeline{display:flex;flex-wrap:wrap;gap:.30rem;margin:.55rem 0}.gc-step{font-size:.63rem;font-weight:800;color:#405574;background:#f6f8fb;border:1px solid var(--gc-line);border-radius:999px;padding:.29rem .46rem}.gc-arrow{font-size:.64rem;color:#9aa8ba;align-self:center}.gc-metadata{display:grid;gap:.45rem}.gc-meta-item{display:flex;gap:.52rem;align-items:flex-start;background:#f8fafc;border:1px solid var(--gc-line);border-radius:11px;padding:.58rem .68rem;font-size:.70rem;color:#52657f;line-height:1.38}.gc-meta-item b{color:var(--gc-ink)}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--gc-line)!important;border-radius:16px!important;box-shadow:0 4px 16px rgba(16,41,75,.03)!important;background:#fff!important}[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden}[data-testid="stAltairChart"]{margin-top:.2rem!important}
@media(max-width:620px){.block-container{padding-left:.58rem;padding-right:.58rem;padding-bottom:7.2rem}.gc-shell{gap:.50rem}.gc-logo{width:39px;height:39px}.gc-brand{font-size:1.16rem}.gc-brand small{font-size:.54rem}.gc-pagehead h2{font-size:1.56rem}.gc-pagehead p{font-size:.83rem}.gc-updated{font-size:.63rem;max-width:108px}.gc-hero{padding:1.02rem}.gc-hero-layout{grid-template-columns:64px 1fr;gap:.72rem}.gc-hero-icon{width:56px;height:56px;font-size:1.6rem}.gc-hero-side{grid-column:1/-1;border-left:0;border-top:1px solid rgba(255,255,255,.17);padding-left:0;padding-top:.68rem;display:grid;grid-template-columns:1fr 1fr;gap:.5rem}.gc-big{font-size:1.92rem}.gc-mid{font-size:1.22rem}.gc-grid4{grid-template-columns:1fr 1fr}.gc-grid3{grid-template-columns:1fr}.gc-grid2{grid-template-columns:1fr}.gc-lock{grid-template-columns:1fr 1fr}.gc-lock div:last-child{grid-column:1/-1}.gc-mini{min-height:98px;padding:.74rem}.gc-mini .value{font-size:1.10rem}.gc-card{padding:.86rem .9rem}.gc-expert-grid{grid-template-columns:1fr 1fr}.gc-engine-grid{grid-template-columns:1fr}}
@media(max-width:350px){.gc-expert-grid{grid-template-columns:1fr}.gc-grid4{grid-template-columns:1fr}.gc-hero-side{grid-template-columns:1fr}}
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
def get_spot(): return fetch_xau_spot()
@st.cache_data(ttl=1800, show_spinner=False)
def get_xau_history(): return fetch_xau_history()
@st.cache_data(ttl=1800, show_spinner=False)
def get_gvz(): return fetch_gvz_latest()

# Navigation reruns must not reopen the same read-only Neon queries. The cache
# contains display/evidence rows only, expires quickly, and never performs writes.
@st.cache_data(ttl=30, show_spinner=False)
def get_decision_cached(database_url: str): return fetch_current_decision_state(database_url)
@st.cache_data(ttl=30, show_spinner=False)
def get_decision_history_cached(database_url: str): return fetch_decision_history(database_url)
@st.cache_data(ttl=30, show_spinner=False)
def get_runtime_cached(database_url: str): return fetch_runtime_observability(database_url)
@st.cache_data(ttl=30, show_spinner=False)
def get_current_forecast_cached(database_url: str): return fetch_current_forecast(database_url)
@st.cache_data(ttl=30, show_spinner=False)
def get_forecast_history_cached(database_url: str): return fetch_forecast_history(database_url)
@st.cache_data(ttl=30, show_spinner=False)
def get_latest_experts_cached(database_url: str, forecast_track: str): return fetch_latest_expert_forecasts(database_url,forecast_track)
@st.cache_data(ttl=30, show_spinner=False)
def get_expert_history_cached(database_url: str, forecast_track: str): return fetch_expert_forecast_history(database_url,forecast_track)
@st.cache_data(ttl=30, show_spinner=False)
def get_aug31_state_replay_cached(database_url: str): return fetch_aug31_state_replay(database_url)
@st.cache_data(ttl=30, show_spinner=False)
def get_aug31_replay_expansion_cached(database_url: str): return fetch_aug31_replay_expansion(database_url)

def safe_call(fn, default):
    try: return fn()
    except Exception: return default

def esc(value: Any) -> str: return html.escape(str(value if value is not None else ""))

def fmt_num(value: Any, decimals: int = 2, suffix: str = "") -> str:
    try:
        if value is None or pd.isna(value): return "—"
        return f"{float(value):,.{decimals}f}{suffix}"
    except Exception: return "—"

def fmt_time(value: Any) -> str:
    if value in (None, "", "N/A"): return "—"
    try:
        ts = pd.to_datetime(value, utc=True, errors="coerce")
        if pd.isna(ts): return esc(value)
        return ts.tz_convert("Europe/Istanbul").strftime("%d %b %Y %H:%M")
    except Exception: return esc(value)

def html_row(label: str, value: str, value_class: str = "") -> str:
    return f"<div class='gc-row'><span>{esc(label)}</span><span class='gc-value {value_class}'>{esc(value)}</span></div>"

def section_header(number: int, title: str) -> str:
    return f"<div class='gc-section-title'><span class='gc-num'>{number}</span><span>{esc(title)}</span></div>"

def empty_html(title: str, subtitle: str) -> str:
    return f"<div class='gc-empty'><strong>{esc(title)}</strong><span>{esc(subtitle)}</span></div>"

def page_head(title: str, subtitle: str, updated: Any = None) -> None:
    updated_text = "Henüz kayıt yok" if updated in (None, "", "N/A") else fmt_time(updated)
    st.markdown(f"<div class='gc-pagehead'><div><h2>{esc(title)}</h2><p>{esc(subtitle)}</p></div><div class='gc-updated'>Son güncelleme:<br>{updated_text}</div></div>", unsafe_allow_html=True)

def tone_class(tone: str) -> str:
    return {"positive":"gc-positive","negative":"gc-negative","warning":"gc-warning","shadow":"gc-blue"}.get(tone, "")

def mini_card(label: str, value: str, note: str, value_class: str = "") -> str:
    return f"<div class='gc-mini'><div class='label'>{esc(label)}</div><div class='value {value_class}'>{esc(value)}</div><div class='note'>{esc(note)}</div></div>"

def load_r41_cfg() -> dict[str, Any]:
    try: return json.loads(R41_CONFIG.read_text(encoding="utf-8")) if R41_CONFIG.exists() else {}
    except Exception: return {}

def gvz_display_regime(value: Any) -> str:
    try:
        if value is None or pd.isna(value): return "KULLANILAMIYOR"
        cfg = load_r41_cfg().get("gvz", {})
        return gvz_regime(float(value), full_max=float(cfg.get("full_cap_max",25.9795)), half_max=float(cfg.get("half_cap_max",30.5238)))
    except Exception: return "KULLANILAMIYOR"

def stored_risk_label(dec: dict[str, Any] | None) -> str:
    if not dec: return "KAYIT YOK"
    if dec.get("gvz_panic") is True: return "PANİK"
    return gvz_display_regime(dec.get("gvz"))

def target_matches(dec: dict[str, Any] | None, fc: dict[str, Any] | None) -> bool:
    return bool(dec and fc and str(dec.get("target_month") or "")[:7] == str(fc.get("target_month") or "")[:7])

def load_replay() -> pd.DataFrame:
    if not HISTORICAL_REPLAY.exists(): return pd.DataFrame()
    try:
        df = pd.read_csv(HISTORICAL_REPLAY); df["month"] = pd.to_datetime(df.get("month"), errors="coerce")
        return df.dropna(subset=["month"]).sort_values("month")
    except Exception: return pd.DataFrame()

def replay_metrics(df: pd.DataFrame) -> dict[str, Any]:
    out: dict[str, Any] = {"n":0}
    if df.empty: return out
    out["n"] = int(len(df))
    for key, ape_col, pred_col in [("patch","patch_r1_ape","patch_r1"),("vw","vw_ape","vw"),("mom","mom_ape","mom"),("rw","rw_ape","rw")]:
        out[f"{key}_mape"] = float(pd.to_numeric(df[ape_col], errors="coerce").mean()) if ape_col in df else None
        if pred_col in df and "actual" in df: out[f"{key}_mae"] = float((pd.to_numeric(df["actual"], errors="coerce")-pd.to_numeric(df[pred_col], errors="coerce")).abs().mean())
    return out

def expert_cards(rows: list[dict[str, Any]]) -> str:
    cards=[]
    for expert_id in EXPERT_DISPLAY_ORDER:
        x=expert_display_state(expert_id,rows); value=fmt_num(x.get("forecast_value"),2," USD") if x.get("issued") else "—"; status=x.get("status") or "UNRESOLVED"
        cards.append("<div class='gc-expert'>"+f"<div class='name'>{esc(x['label'])}</div><div class='role'>{esc(x['role'])}</div><div class='forecast'>{esc(value)}</div><div class='state'>{esc(status)}</div></div>")
    return "<div class='gc-expert-grid'>"+"".join(cards)+"</div>"

def engine_output_display(row: dict[str, Any]) -> str:
    value=row.get("output")
    if value is None or str(value).strip()=="": return "—"
    if row.get("category")=="MONTHLY_FORECAST":
        try: return fmt_num(value,2," USD")
        except Exception: return display_state(value,"—")
    if row.get("direction_vote") is True:
        arrow,_=arrow_state(value); return f"{arrow} {display_state(value,'—')}"
    return display_state(value,"—")

def aug31_state_replay_html(state: dict[str, Any] | None, expansion: dict[str, Any] | None = None) -> str:
    if not state:
        return empty_html("31 AĞUSTOS ORIGIN YÖN SNAPSHOT OKUNAMADI","Production Evidence Spine ve deployment origin snapshot kullanılamıyor.")
    ma,mt=arrow_state(state.get("monthly_direction_3m")); fa,ft=arrow_state(state.get("fast_state")); sa,stn=arrow_state(state.get("slow_state"))
    source="DB READ-ONLY" if state.get("source_mode")=="NEON_DB_READ_ONLY" else "SNAPSHOT FALLBACK"
    rows=(
        html_row("Monthly Direction 3M",f"{ma} {display_state(state.get('monthly_direction_3m'),'—')}",tone_class(mt))
        +html_row("FAST",f"{fa} {display_state(state.get('fast_state'),'—')}",tone_class(ft))
        +html_row("SLOW",f"{sa} {display_state(state.get('slow_state'),'—')}",tone_class(stn))
        +html_row("GVZ",f"{fmt_num(state.get('gvz_value'),2)} · {display_state(state.get('gvz_regime'),'—')}")
        +html_row("GVZ risk cap",fmt_num(state.get("gvz_cap"),1))
    )
    if expansion:
        blockers={
            "VW-MIDAS-MSVR":"BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN",
            "Macro Event":"BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED",
            "BOCPD · archived":display_state(expansion.get("bocpd_archived_engine_status"),"BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED"),
        }
    else:
        blockers=dict(state.get("blocked_components") or {})
    blocker_rows="".join(html_row(k,v,"gc-warning") for k,v in blockers.items())
    return (
        "<div class='gc-card' style='margin-top:.7rem'><div class='gc-section-title'>EYLÜL 2026 · 31 AĞUSTOS ORIGIN YÖN / RİSK SNAPSHOT</div>"
        +f"<div class='gc-footnote'><b>31 AĞUSTOS ORIGIN · EYLÜL AY-AÇILIŞ CONTEXT</b> · information boundary 31.08.2026 17:00 ET · kaynak: {esc(source)}. <span style='color:var(--gc-muted)'>Audit: 4 Eylül'de yeniden hesaplandı · HISTORICAL_REPLAY / ORIGIN_RECONSTRUCTION.</span> Bu durumlar H=1 fiyat tahmini değildir ve current yön oyu/kararı değiştirmez.</div>"
        +rows
        +"<div class='gc-track-head'><b>31 AĞUSTOS ORIGIN'DE HALEN BLOCKED / ARCHIVED</b><span class='gc-track-pill'>FAIL-CLOSED</span></div>"
        +blocker_rows
        +"</div>"
    )

def aug31_replay_expansion_html(replay: dict[str, Any] | None) -> str:
    if not replay:
        return empty_html("31 AĞUSTOS ORIGIN MOTOR SETİ OKUNAMADI","Causal Patch / Emergency / BOCPD successor immutable origin-reconstruction evidence kullanılamıyor.")
    source="DB READ-ONLY" if replay.get("source_mode")=="NEON_DB_READ_ONLY" else "SNAPSHOT FALLBACK"
    rows=(
        html_row("Causal Patch · Eylül H=1",fmt_num(replay.get("causal_patch_forecast"),2," USD"))
        +html_row("Emergency · Level",display_state(replay.get("emergency_level"),"—"))
        +html_row("Emergency · Reversal",display_state(replay.get("emergency_reversal"),"—"))
        +html_row("BOCPD successor V1",display_state(replay.get("bocpd_successor_state"),"—"))
    )
    return (
        "<div class='gc-card' style='margin-top:.7rem;border-color:#f0d8a7'>"
        +"<div class='gc-section-title'>EYLÜL 2026 · 31 AĞUSTOS ORIGIN MOTOR SETİ</div>"
        +f"<div class='gc-footnote'><b>EYLÜL AY-AÇILIŞ REFERANSI · 31 AĞUSTOS ORIGIN</b> · information boundary 31.08.2026 17:00 ET · kaynak: {esc(source)}. <span style='color:var(--gc-muted)'>Audit provenance: 4 Eylül'de yeniden hesaplandı · HISTORICAL_REPLAY / ORIGIN_RECONSTRUCTION; 31 Ağustos'ta issued edildi iddiası yoktur.</span></div>"
        +rows
        +f"<div class='gc-footnote' style='margin-top:.55rem'>Patch günlük feature son tarihi: {esc(display_state(replay.get('causal_patch_daily_max_date'),'—'))}. Emergency month-open başlangıcıdır; 31 Ağustos close Eylül close sayılmaz. Archived BOCPD: <b>{esc(display_state(replay.get('bocpd_archived_engine_status'),'BLOCKED'))}</b>. Successor <b>{esc(display_state(replay.get('bocpd_successor_id'),'BOCPD_RETURN_SUCCESSOR_V1'))}</b> yalnız research / out-of-lock historical replay context'tir. Selector OFF · Ensemble OFF · canonical authority false · direction vote false.</div>"
        +"</div>"
    )

def engine_status_label(value: Any) -> str:
    raw=display_state(value,"UNRESOLVED").upper()
    if raw=="STORED_CONTEXT_AVAILABLE": return "AKTİF · STORED CONTEXT"
    if raw=="WAITING_ELIGIBLE_MONTH_END_ORIGIN": return "BEKLİYOR · UYGUN AY-SONU ORIGIN"
    if raw.startswith("ISSUED_"): return "YAYIMLANDI · AYRI EXPERT ÇIKTISI"
    if raw.startswith("BLOCKED_"): return "BLOCKED · BAĞIMLILIK/KANIT EKSİK"
    if raw.startswith("NOT_PROVEN_"): return "KANITLANMADI"
    if raw.startswith("WAITING_") or raw=="NOT_ISSUED": return "BEKLİYOR"
    return raw.replace("_"," ")

def engine_activation_note(value: Any) -> str:
    raw=display_state(value,"UNRESOLVED").upper()
    if raw=="STORED_CONTEXT_AVAILABLE":
        return "ÇALIŞIYOR · persisted context mevcut."
    if raw=="WAITING_ELIGIBLE_MONTH_END_ORIGIN":
        return "Eylül için 31 Ağustos origin referansı mevcut. İleri operasyonel durum bir sonraki aylık döngüyü bekliyor: 30 Eylül origin → Ekim 2026 H=1; yalnız issuer/PIT gate'leri geçerse. Eylül referansının audit sınıfı ORIGIN_RECONSTRUCTION / HISTORICAL_REPLAY olarak korunur."
    if raw=="BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN":
        return "Takvime bağlı değil; exact archived VW replication ve PIT/revision-safe source-vintage contract kanıtlanmadan çalışmaz."
    if raw=="BLOCKED_EXACT_MACRO_SCORE_CONSENSUS_AND_VINTAGE_CONTRACT_NOT_RECOVERED":
        return "Takvime bağlı değil; exact macro score, consensus ve release-vintage/timestamp contract recover edilmeden çalışmaz."
    if raw=="WAITING_FIRST_GOVERNED_PATCH_EXPERT_REFERENCE":
        return "Eylül ay-açılış Emergency state'i 31 Ağustos origin referansıyla mevcut. İleri operasyonel lane, 30 Eylül origin → Ekim için zamanında yayımlanacak governed CAUSAL_PATCH referansını bekliyor. Reconstruction forward prospective kanıt yerine geçmez."
    if raw=="BLOCKED_EXACT_BOCPD_PRIOR_AND_RESET_SCORE_IMPLEMENTATION_NOT_RECOVERED":
        return "Archived BOCPD takvime bağlı değil; exact prior/init ve reset-score implementation recover edilmeden çalışmaz. BOCPD_RETURN_SUCCESSOR_V1 ayrı research/HISTORICAL_REPLAY context olarak gösterilebilir; archived motoru ACTIVE yapmaz."
    if raw.startswith("ISSUED_"):
        return "Çıktı yayımlandı; evidence/track kuralları içinde ayrı expert olarak gösterilir."
    return "Mevcut teknik durum değişmeden sayı veya yön uydurulmaz."

def engine_inventory_cards(rows: list[dict[str, Any]]) -> str:
    cards=[]
    for row in rows:
        output=engine_output_display(row); raw_status=display_state(row.get("status"),"UNRESOLVED"); status=engine_status_label(raw_status)
        evidence=display_state(row.get("evidence_class"),"NO_CURRENT_EVIDENCE")
        version=display_state(row.get("version"),"VERSION_NOT_PROVEN")
        updated=fmt_time(row.get("as_of"))
        vote="YÖN OYU" if row.get("direction_vote") is True else "YÖN OYU DEĞİL"
        activation=engine_activation_note(raw_status)
        detail=f"{row.get('category')} · {vote} · {evidence} · {version} · Son: {updated}"
        ref=row.get("replay_reference") if isinstance(row.get("replay_reference"),dict) else None
        replay_html=""
        if ref:
            ref_output=fmt_num(ref.get("output"),2," USD") if ref.get("unit")=="USD/oz" else display_state(ref.get("output"),"—")
            archived=ref.get("archived_engine_status")
            archived_html=(f"<div style='font-size:.57rem;color:var(--gc-warning);line-height:1.34;margin-top:.22rem'><b>Archived runtime:</b> {esc(archived)}</div>" if archived else "")
            replay_html=(
                "<div style='margin-top:.52rem;padding:.48rem .52rem;border:1px solid #f0d8a7;border-radius:10px;background:#fffaf0'>"
                +f"<div style='font-size:.58rem;font-weight:900;color:#8a5b00'>{esc(ref.get('label'))} · EYLÜL / 31 AĞUSTOS ORIGIN</div>"
                +f"<div style='font-size:.88rem;font-weight:900;color:var(--gc-ink);margin:.22rem 0'>{esc(ref_output)}</div>"
                +f"<div style='font-size:.56rem;color:var(--gc-muted);line-height:1.34'>{esc(ref.get('evidence_class'))} · {esc(ref.get('version'))}</div>"
                +archived_html
                +f"<div style='font-size:.57rem;color:var(--gc-muted);line-height:1.34;margin-top:.22rem'>{esc(ref.get('note'))}</div>"
                +"</div>"
            )
        cards.append("<div class='gc-expert'>"+f"<div class='name'>{esc(row.get('label'))}</div><div class='role'>{esc(row.get('role'))}</div><div class='forecast'>{esc(output)}</div><div class='state'>{esc(status)}</div><div class='note' style='font-size:.60rem;color:var(--gc-muted);line-height:1.35;margin-top:.34rem'>Operasyonel teknik durum: {esc(raw_status)}</div>"+replay_html+f"<div class='note' style='font-size:.60rem;color:var(--gc-muted);line-height:1.35;margin-top:.26rem'>{esc(detail)}</div><div class='note' style='font-size:.62rem;color:var(--gc-ink);line-height:1.38;margin-top:.34rem'><b>Ne zaman:</b> {esc(activation)}</div></div>")
    return "<div class='gc-expert-grid gc-engine-grid'>"+"".join(cards)+"</div>"

def selector_lock_html() -> str:
    return "<div class='gc-lock'>"+f"<div>AUTO SELECTOR<b>{esc(AUTO_SELECTOR_STATUS)}</b></div><div>AUTO ENSEMBLE<b>{esc(AUTO_ENSEMBLE_STATUS)}</b></div><div>SELECTION / AGGREGATION RULE<b>{esc(EXPERT_SELECTION_STATUS)}</b></div></div>"

def pipeline_html() -> str:
    steps=["Multi-Expert Monthly Forecast Engine","Monthly Direction / Prior / Context","Fast / Slow","Macro Event","Emergency","BOCPD","GVZ risk cap","Frozen Final Decision State","Immutable Decision Snapshot / Event Ledger"]
    parts=[]
    for i,step in enumerate(steps):
        if i: parts.append("<span class='gc-arrow'>→</span>")
        parts.append(f"<span class='gc-step'>{esc(step)}</span>")
    return "<div class='gc-pipeline'>"+"".join(parts)+"</div>"

def expert_history_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    if not rows: return pd.DataFrame()
    df=pd.DataFrame(rows)
    if df.empty or not {"target_month","expert_id","forecast_value"}.issubset(df.columns): return pd.DataFrame()
    df["target_month"]=pd.to_datetime(df["target_month"],errors="coerce"); df["forecast_value"]=pd.to_numeric(df["forecast_value"],errors="coerce")
    if "as_of" in df: df["as_of"]=pd.to_datetime(df["as_of"],errors="coerce",utc=True)
    return df.dropna(subset=["target_month","forecast_value"]).sort_values(["target_month","expert_id"])

def plot_lines(df: pd.DataFrame, x: str, columns: list[str], height: int=270) -> None:
    available=[c for c in columns if c in df.columns]
    if df.empty or not available or x not in df.columns: return
    frame=df[[x]+available].copy().melt(id_vars=[x],var_name="Seri",value_name="Değer").dropna()
    if frame.empty: return
    chart=(alt.Chart(frame).mark_line(strokeWidth=2.2).encode(x=alt.X(f"{x}:T",title=None),y=alt.Y("Değer:Q",title="USD",scale=alt.Scale(zero=False)),color=alt.Color("Seri:N",title=None)).properties(height=height).configure_view(strokeOpacity=0).configure_axis(gridColor="#edf1f5",labelColor="#687995",titleColor="#687995").configure_legend(labelColor="#52657f",orient="bottom"))
    st.altair_chart(chart,width="stretch")

url=db_url()
decision=safe_call(lambda:get_decision_cached(url),None)
decision_rows=safe_call(lambda:get_decision_history_cached(url),[]) if url else []
runtime_obs=safe_call(lambda:get_runtime_cached(url),None)
forecast=safe_call(lambda:get_current_forecast_cached(url),None) if url else None
forecast_rows=safe_call(lambda:get_forecast_history_cached(url),[]) if url else []
month_end_experts=safe_call(lambda:get_latest_experts_cached(url,TRACK_MONTH_END),[]) if url else []
early_experts=safe_call(lambda:get_latest_experts_cached(url,TRACK_EARLY_INDICATIVE),[]) if url else []
month_end_history=safe_call(lambda:get_expert_history_cached(url,TRACK_MONTH_END),[]) if url else []
early_history=safe_call(lambda:get_expert_history_cached(url,TRACK_EARLY_INDICATIVE),[]) if url else []
historical_replay_experts=[]
historical_replay_history=[]
aug31_state_replay=safe_call(lambda:get_aug31_state_replay_cached(url),None) if url else None
aug31_replay_expansion=safe_call(lambda:get_aug31_replay_expansion_cached(url),None) if url else None
spot=safe_call(get_spot,None); hist,hist_meta=safe_call(get_xau_history,(pd.DataFrame(),{})); gvz=safe_call(get_gvz,None); replay=load_replay(); rmetrics=replay_metrics(replay); _=classification_label
runtime_rows=[] if not runtime_obs else list(runtime_obs.get("runtime") or [])
engine_rows=attach_aug31_replay_expansion(build_engine_inventory(decision,month_end_experts,early_experts,runtime_rows),aug31_replay_expansion); engine_counts=engine_inventory_counts(engine_rows)

st.markdown("<div class='gc-shell'><div class='gc-menu'>☰</div><div class='gc-logo'><b>G</b></div><div class='gc-brand'>GOLD CONTROL<small>DECISION SYSTEM</small></div></div>",unsafe_allow_html=True)
NAV_OPTIONS=["⌂ Bugün","◉ Görünüm","↗ Tahmin","◷ Geçmiş"]; nav=st.radio("Ana navigasyon",NAV_OPTIONS,horizontal=True,label_visibility="collapsed",key="gc_main_nav")

if nav=="⌂ Bugün":
    page_head("BUGÜN","Piyasa şu anda ne durumda?",None if not spot else spot.get("as_of") or spot.get("updated_at")); completed=latest_completed_daily_row(hist); completed_close=None if completed is None else float(completed["close"]); delta=price_delta(None if not spot else spot.get("price"),completed_close)
    if spot:
        delta_text="Karşılaştırma yok" if delta is None else f"{delta.absolute:+,.2f} USD · {delta.percent:+.2f}%"; delta_class="gc-muted" if delta is None else ("gc-positive" if delta.absolute>=0 else "gc-negative"); freshness="GÜNCEL" if not spot.get("stale") else "STALE"
        st.markdown("<div class='gc-hero'><div class='gc-kicker'>ALTIN ONS · XAU/USD · INDICATIVE LIVE</div>"+f"<div class='gc-big'>{esc(fmt_num(spot.get('price'),2))} USD</div><div class='{delta_class}'><b>{esc(delta_text)}</b></div><span class='gc-badge'>{esc(freshness)}</span><div class='gc-meta' style='margin-top:.55rem'>Kaynak: {esc(display_state(spot.get('source'),'Gold API'))} · display only / no model use</div></div>",unsafe_allow_html=True)
    else: st.markdown(empty_html("CANLI XAU/USD KULLANILAMIYOR","Kaynak veya bağlantı durumu doğrulanamadı."),unsafe_allow_html=True)
    state=decision_view_state(decision); st.markdown("<div class='gc-grid3'>"+mini_card("TAMAMLANMIŞ GÜNLÜK CLOSE",fmt_num(completed_close,2," USD"),"XAUS operasyonel cross-check")+mini_card("GVZ",fmt_num(None if not gvz else gvz.get("close"),2),f"Risk görünümü: {gvz_display_regime(None if not gvz else gvz.get('close'))}")+mini_card("SON KAYITLI DURUM",state.title,"Decision Store" if decision else "Henüz display-eligible kayıt yok")+"</div>",unsafe_allow_html=True)
    with st.container(border=True,key="gc_market_history_card"):
        st.markdown("<div class='gc-section-title'>PİYASA TARİHÇESİ</div>",unsafe_allow_html=True); timeframe=st.radio("Aralık",["1A","3A","6A","1Y"],horizontal=True,key="gc_market_range",label_visibility="collapsed")
        if not hist.empty:
            chart=filter_history_timeframe(hist,timeframe)
            if not chart.empty: plot_lines(chart.rename(columns={"date":"Tarih","close":"Operasyonel Close"}),"Tarih",["Operasyonel Close"],245)
            st.markdown("<div class='gc-footnote'>XAUS tarihçesi yalnız operasyonel display cross-check'tir; canonical EOD/settlement değildir.</div>",unsafe_allow_html=True)
        else: st.markdown(empty_html("TARİHÇE KULLANILAMIYOR","XAUS history kaynağı okunamadı."),unsafe_allow_html=True)
    st.markdown(f"<div class='gc-info'><b>Karar bağlamı:</b> {esc(state.title)}. Canlı spot yalnız piyasa izleme verisidir. <b>Canlı spot ≠ son EOD karar.</b></div>",unsafe_allow_html=True)

elif nav=="◉ Görünüm":
    updated=None if not decision else decision.get("generated_at") or decision.get("decision_as_of"); page_head("GÖRÜNÜM","Önce tüm tahmin, yön, event, emergency, rejim ve risk motorlarını gör; karar/selector katmanı sonraki aşamadır.",updated); state=decision_view_state(decision); monthly=None if not decision else decision.get("monthly_direction_3m"); ma,mt=arrow_state(monthly); live_gvz=None if not gvz else gvz.get("close"); stored_risk=stored_risk_label(decision); relation=monthly_intramonth_relation(decision); badge_text=evidence_badge(decision.get("evidence_class"))[0] if decision else "YAYIMLANMADI"
    st.markdown("<div class='gc-hero'><div class='gc-hero-layout'><div class='gc-hero-icon'>◎</div>"+f"<div><div class='gc-kicker'>MEVCUT KAYITLI DURUM</div><div class='gc-mid'>{esc(state.title)}</div><div class='gc-meta'>{esc(state.subtitle)}</div><span class='gc-badge'>{esc(badge_text)}</span></div><div class='gc-hero-side'><div><div class='gc-hero-label'>MODEL YÖNÜ / MONTHLY PRIOR</div><div class='gc-hero-value {tone_class(mt)}'>{esc(ma)} {esc(display_state(monthly,'YAYIMLANMADI'))}</div></div><div><div class='gc-hero-label'>RİSK SEVİYESİ</div><div class='gc-hero-value'>{esc(stored_risk)}</div></div></div></div></div>",unsafe_allow_html=True)
    fast_value=None if not decision else decision.get("fast_state")
    slow_value=None if not decision else decision.get("slow_state")
    fa,ft=arrow_state(fast_value); sa,stn=arrow_state(slow_value)
    direction_summary=(
        "<div class='gc-card gc-direction-summary' style='padding:.62rem .68rem;margin:.42rem 0'>"
        +"<div class='gc-section-title' style='margin-bottom:.42rem'>YÖN MOTORLARI ÖZETİ · STORED CONTEXT</div>"
        +"<div class='gc-direction-strip' style='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.36rem'>"
        +f"<div class='gc-direction-cell' style='min-width:0;border:1px solid var(--gc-line);border-radius:12px;padding:.52rem .42rem;text-align:center'><div style='font-size:.59rem;font-weight:900;color:var(--gc-muted)'>MONTHLY 3M</div><div class='{tone_class(mt)}' style='font-size:.95rem;font-weight:900;margin:.22rem 0'>{esc(ma)} {esc(display_state(monthly,'YAYIMLANMADI'))}</div><div style='font-size:.56rem;color:var(--gc-muted)'>Stratejik prior</div></div>"
        +f"<div class='gc-direction-cell' style='min-width:0;border:1px solid var(--gc-line);border-radius:12px;padding:.52rem .42rem;text-align:center'><div style='font-size:.59rem;font-weight:900;color:var(--gc-muted)'>FAST</div><div class='{tone_class(ft)}' style='font-size:.95rem;font-weight:900;margin:.22rem 0'>{esc(fa)} {esc(display_state(fast_value,'YAYIMLANMADI'))}</div><div style='font-size:.56rem;color:var(--gc-muted)'>Taktik teyit</div></div>"
        +f"<div class='gc-direction-cell' style='min-width:0;border:1px solid var(--gc-line);border-radius:12px;padding:.52rem .42rem;text-align:center'><div style='font-size:.59rem;font-weight:900;color:var(--gc-muted)'>SLOW</div><div class='{tone_class(stn)}' style='font-size:.95rem;font-weight:900;margin:.22rem 0'>{esc(sa)} {esc(display_state(slow_value,'YAYIMLANMADI'))}</div><div style='font-size:.56rem;color:var(--gc-muted)'>Orta hız teyidi</div></div>"
        +"</div><div class='gc-footnote' style='margin-top:.38rem'>Persisted context · selector/ensemble değildir. GVZ risk-only olarak aşağıdaki risk bölümünde kalır.</div></div>"
    )
    st.markdown(direction_summary,unsafe_allow_html=True)
    inventory_summary=(
        f"Toplam {engine_counts['total']} motor/kanal · "
        f"Stored context {engine_counts['active']} · Issued expert {engine_counts['issued']} · "
        f"Blocked/Not proven {engine_counts['blocked']} · Waiting {engine_counts['waiting']}"
    )
    if runtime_obs:
        spine_ok=runtime_obs.get("status")=="DATA_EVIDENCE_SPINE_RUNTIME_HEALTH_PASS"
        source_mode=display_state(runtime_obs.get("source_mode"),"UNKNOWN_SOURCE")
        source_label="DB Evidence Spine" if source_mode=="NEON_DB_READ_ONLY" else "Production Evidence Snapshot · FALLBACK"
        spine_summary=(
            f"{source_label}: runtime {runtime_obs.get('runtime_engine_count',0)}/12 · "
            f"context link {runtime_obs.get('context_exactly_one_link',0)}/{runtime_obs.get('context_expected',7)} · "
            f"integrity {'PASS' if spine_ok else 'BLOCKED'}"
        )
        if source_mode=="PRODUCTION_SNAPSHOT_FALLBACK" and runtime_obs.get("snapshot_source_state_at"):
            spine_summary += f" · state {fmt_time(runtime_obs.get('snapshot_source_state_at'))}"
    else:
        spine_summary="Production Evidence: BLOCKED · DB ve doğrulanmış snapshot kullanılamıyor"
    st.markdown(
        "<div class='gc-card'><div class='gc-section-title'>TÜM TAHMİN, YÖN, EVENT, REJİM VE RİSK MOTORLARI</div>"
        +f"<div class='gc-footnote'><b>{esc(ENGINE_OBSERVABILITY_CONTRACT)}</b><br>{esc(inventory_summary)}<br>{esc(spine_summary)}<br>"
        +"Bir motor blocked olsa bile kartı görünür kalır. Stored yön context'i ile H=1 fiyat forecast'ı birbirine dönüştürülmez.</div>"
        +engine_inventory_cards(engine_rows)+"</div>",
        unsafe_allow_html=True,
    )
    summary=html_row("Frozen Final Decision State",state.title)+html_row("Monthly Direction / Prior / Context",display_state(monthly,"YAYIMLANMADI"))+html_row("Prior / intramonth ilişki",relation)+html_row("Evidence",badge_text); st.markdown(f"<div class='gc-card'>{section_header(1,'SİNYAL ÖZETİ')}{summary}</div>",unsafe_allow_html=True)
    if decision:
        fa,ft=arrow_state(decision.get("fast_state")); sa,stn=arrow_state(decision.get("slow_state")); model_body=f"<div class='gc-mid {tone_class(mt)}'>{esc(ma)} {esc(display_state(monthly))}</div><div class='gc-footnote'>Stratejik anchor/prior; günlük işlem emri değildir.</div>"; fs_body=html_row("FAST",f"{fa} {display_state(decision.get('fast_state'))}",tone_class(ft))+html_row("SLOW",f"{sa} {display_state(decision.get('slow_state'))}",tone_class(stn))
    else:
        model_body="<div class='gc-mid gc-muted'>—</div><div class='gc-footnote'>Aylık prior yalnız stored state ile gösterilir; expert çıktısı otomatik prior değildir.</div>"; fs_body=html_row("FAST","YAYIMLANMADI","gc-muted")+html_row("SLOW","YAYIMLANMADI","gc-muted")
    st.markdown("<div class='gc-grid2'>"+f"<div class='gc-card'>{section_header(2,'MODEL YÖNÜ (AYLIK)')}{model_body}</div>"+f"<div class='gc-card'>{section_header(3,'FAST / SLOW TEYİDİ')}{fs_body}</div></div>",unsafe_allow_html=True)
    risk_rows=html_row("Stored risk",stored_risk)+html_row("GVZ · stored",fmt_num(None if not decision else decision.get("gvz"),2))+html_row("GVZ · live display",fmt_num(live_gvz,2))+html_row("Rol","Risk cap · yön üretmez"); st.markdown(f"<div class='gc-card'>{section_header(4,'RİSK SEVİYESİ')}{risk_rows}</div>",unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(section_header(5,"SİNYAL ZAMAN ÇİZELGESİ"),unsafe_allow_html=True)
        if not hist.empty:
            plot_lines(filter_history_timeframe(hist,"6A").rename(columns={"date":"Tarih","close":"Operasyonel Close"}),"Tarih",["Operasyonel Close"],245); st.caption(f"Persisted Decision Store event sayısı: {len(decision_rows)}. Fiyat hareketi tek başına karar eventi değildir.")
        else: st.markdown(empty_html("ZAMAN ÇİZELGESİ KULLANILAMIYOR","Display-authorized fiyat tarihçesi okunamadı."),unsafe_allow_html=True)
    if decision:
        emergency_rows=html_row("Macro Event",display_state(decision.get("macro_event_state"),MACRO_EVENT_STATUS))+html_row("Emergency · Level",display_state(decision.get("level_emergency")))+html_row("Emergency · Reversal",display_state(decision.get("reversal_emergency")))+html_row("BOCPD",display_state(decision.get("bocpd_context")))
    else:
        if aug31_replay_expansion:
            emergency_rows=html_row("Macro Event",MACRO_EVENT_STATUS,"gc-warning")+html_row("Emergency · Level",f"{display_state(aug31_replay_expansion.get('emergency_level'),'—')} · EYLÜL / 31 AĞUSTOS ORIGIN","gc-warning")+html_row("Emergency · Reversal",f"{display_state(aug31_replay_expansion.get('emergency_reversal'),'—')} · EYLÜL / 31 AĞUSTOS ORIGIN","gc-warning")+html_row("BOCPD",f"Archived BLOCKED · Successor: {display_state(aug31_replay_expansion.get('bocpd_successor_state'),'—')}","gc-warning")
        else:
            emergency_rows=html_row("Macro Event",MACRO_EVENT_STATUS,"gc-warning")+html_row("Emergency","YAYIMLANMADI","gc-muted")+html_row("BOCPD","YAYIMLANMADI","gc-muted")
    explanation=deterministic_explanation(decision); st.markdown("<div class='gc-grid2'>"+f"<div class='gc-card'>{section_header(6,'EMERGENCY DURUMU')}{emergency_rows}</div>"+f"<div class='gc-card'>{section_header(7,'SİSTEM YORUMU')}<div style='font-style:italic;line-height:1.62'>{esc(explanation)}</div>{pipeline_html()}</div></div>",unsafe_allow_html=True); st.markdown(selector_lock_html(),unsafe_allow_html=True); st.markdown("<div class='gc-note'>Aylık prior ile intramonth durum çelişebilir. Sistem yeni uygun veriler geldikçe Fast/Slow, Macro Event, Emergency, BOCPD ve GVZ'nin yalnız dondurulmuş rolleriyle güncellenir; 2026 sonucuna bakarak expert seçimi yapılmaz.</div>",unsafe_allow_html=True)

elif nav=="↗ Tahmin":
    historical_replay_experts=safe_call(lambda:get_latest_experts_cached(url,TRACK_HISTORICAL_REPLAY),[])
    replay_update=historical_replay_experts[0].get("as_of") if historical_replay_experts else None
    expert_update=month_end_experts[0].get("as_of") if month_end_experts else (early_experts[0].get("as_of") if early_experts else None); updated=forecast.get("frozen_at") if forecast else (expert_update or replay_update); page_head("TAHMİN","Her ayın tahmin ve ay-açılış yön referansı bir önceki tamamlanmış ay-sonu originine bağlıdır. Reconstruction provenance audit katmanında ayrıca gösterilir.",updated); fstate=forecast_view_state(forecast)
    if forecast:
        target=str(forecast.get("target_month") or "")[:7]; badge=evidence_badge(forecast.get("evidence_class"))[0]; hero_title=fmt_num(forecast.get("forecast_value"),2," USD"); hero_sub=f"Hedef dönem: {target}"; direction=decision.get("monthly_direction_3m") if target_matches(decision,forecast) else None; da,_=arrow_state(direction); direction_text=f"{da} {display_state(direction,'—')}"; origin_text=fmt_time(forecast.get("forecast_origin")); hero_kicker="GELECEK AY TAHMİNİ"; direction_label="MONTHLY DIRECTION / PRIOR"; origin_label="CANONICAL ORIGIN"
    elif historical_replay_experts:
        replay_by_id={str(r.get("expert_id") or ""):r for r in historical_replay_experts}
        replay_primary=replay_by_id.get("MOMENTUM_3M") or replay_by_id.get("RANDOM_WALK") or historical_replay_experts[0]
        replay_target=str(replay_primary.get("target_month") or "")[:7]
        mom=replay_by_id.get("MOMENTUM_3M"); rw=replay_by_id.get("RANDOM_WALK")
        mom_value=fmt_num(None if not mom else mom.get("forecast_value"),2)
        rw_value=fmt_num(None if not rw else rw.get("forecast_value"),2)
        patch_value=fmt_num(None if not aug31_replay_expansion else aug31_replay_expansion.get("causal_patch_forecast"),2)
        hero_title=f"{mom_value} / {rw_value} / {patch_value} USD"
        hero_sub=f"3M Momentum / Random Walk / Causal Patch · Hedef: {replay_target} · 31 Ağustos bilgi sınırı"
        badge="31 AĞUSTOS ORIGIN · RECONSTRUCTION"
        replay_monthly=None if not aug31_state_replay else aug31_state_replay.get("monthly_direction_3m")
        replay_fast=None if not aug31_state_replay else aug31_state_replay.get("fast_state")
        replay_slow=None if not aug31_state_replay else aug31_state_replay.get("slow_state")
        rma,_=arrow_state(replay_monthly); rfa,_=arrow_state(replay_fast); rsa,_=arrow_state(replay_slow)
        direction_text=f"M {rma} {display_state(replay_monthly,'—')} · F {rfa} {display_state(replay_fast,'—')} · S {rsa} {display_state(replay_slow,'—')}"
        origin_text=fmt_time(replay_primary.get("forecast_origin"))
        hero_kicker="EYLÜL 2026 · 31 AĞUSTOS ORIGIN"
        direction_label="EYLÜL AY-AÇILIŞ YÖN MOTORLARI"
        origin_label="ORIGIN BOUNDARY"
    else:
        hero_title=fstate.title; hero_sub=fstate.subtitle; badge="KANONİK SONUÇ YOK"; direction_text="—"; origin_text="—"; hero_kicker="GELECEK AY TAHMİNİ"; direction_label="MONTHLY DIRECTION / PRIOR"; origin_label="CANONICAL ORIGIN"
    st.markdown("<div class='gc-hero'><div class='gc-hero-layout'><div class='gc-hero-icon'>↗</div>"+f"<div><div class='gc-kicker'>{esc(hero_kicker)}</div><div class='gc-mid'>{esc(hero_title)}</div><div class='gc-meta'>{esc(hero_sub)}</div><span class='gc-badge gc-badge-gold'>{esc(badge)}</span></div><div class='gc-hero-side'><div><div class='gc-hero-label'>{esc(direction_label)}</div><div class='gc-hero-value'>{esc(direction_text)}</div></div><div><div class='gc-hero-label'>{esc(origin_label)}</div><div class='gc-hero-value' style='font-size:.90rem'>{esc(origin_text)}</div></div></div></div></div>",unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI</div>",unsafe_allow_html=True); mdf=expert_history_frame(month_end_history)
        if not mdf.empty:
            pivot=mdf.pivot_table(index="target_month",columns="expert_id",values="forecast_value",aggfunc="last").reset_index(); plot_lines(pivot,"target_month",[c for c in EXPERT_DISPLAY_ORDER if c in pivot.columns],275); st.caption("MONTH_END_EXPERT: ayrı expert çıktıları; selector/ensemble sonucu değildir.")
        elif not replay.empty and {"actual","patch_r1","vw","mom","rw"}.issubset(replay.columns):
            st.markdown("<div class='gc-replay-head'><strong>Prospective geçmiş henüz yok; araştırma referansı gösteriliyor.</strong><span class='gc-replay-pill'>HISTORICAL_REPLAY</span></div>",unsafe_allow_html=True); research=replay.tail(12)[["month","actual","patch_r1","vw","mom","rw"]].rename(columns={"month":"Tarih","actual":"Gerçekleşen","patch_r1":"Causal Patch","vw":"VW-MIDAS-MSVR","mom":"3M Momentum","rw":"Random Walk"}); plot_lines(research,"Tarih",["Gerçekleşen","Causal Patch","VW-MIDAS-MSVR","3M Momentum","Random Walk"],275); st.caption("Historical replay prospective değildir ve selector otoritesi yaratmaz.")
        else: st.markdown(empty_html("KARŞILAŞTIRMA HENÜZ OLUŞMADI","MONTH_END_EXPERT veya gösterilebilir araştırma geçmişi yok."),unsafe_allow_html=True)
    st.markdown("<div class='gc-card'><div class='gc-section-title'>MULTI-EXPERT MONTHLY FORECAST ENGINE</div><div class='gc-footnote'>Aynı target için Causal Patch, VW-MIDAS-MSVR, 3M Momentum ve Random Walk ayrı kimlik/evidence ile tutulur. Winner yoktur.</div>"+expert_cards(month_end_experts)+selector_lock_html()+"<div class='gc-track-head'><b>EARLY INDICATIVE · AYRI REVISION TRACK</b><span class='gc-track-pill'>PIT-SAFE ONLY</span></div>"+(expert_cards(early_experts) if early_experts else empty_html("EARLY INDICATIVE HENÜZ YOK","Ay-sonu kanonik forecast'tan ayrı tutulur; PIT-safe contract açılmadan sayı üretilmez."))+"</div>",unsafe_allow_html=True)
    replay_db_body=(expert_cards(historical_replay_experts) if historical_replay_experts else empty_html("EYLÜL 2026 · 31 AĞUSTOS ORIGIN KAYDI YOK","Production Evidence Spine üzerinde Eylül için origin-reconstruction kaydı okunamadı."))
    st.markdown("<div class='gc-replay'><div class='gc-replay-head'><strong>EYLÜL 2026 · 31 AĞUSTOS ORIGIN</strong><span class='gc-replay-pill'>MONTH-OPEN REFERENCE</span></div><div class='gc-footnote'><b>H=1 AY-AÇILIŞ EXPERT SETİ</b> · Aşağıdaki USD değerleri 31 Ağustos bilgi sınırıyla Eylül 2026 aylık ortalama fiyatı için ayrı expert referanslarıdır; winner/ortalama değildir.</div>"+replay_db_body+aug31_state_replay_html(aug31_state_replay,aug31_replay_expansion)+aug31_replay_expansion_html(aug31_replay_expansion)+"<div class='gc-footnote' style='margin-top:.65rem'><b>Audit provenance:</b> Bu Eylül origin seti 4 Eylül'de 31 Ağustos bilgi sınırıyla yeniden hesaplandı; bu nedenle evidence sınıfı ORIGIN_RECONSTRUCTION / HISTORICAL_REPLAY olarak korunur. Bu, 31 Ağustos'ta gerçekten issued edildi iddiası değildir. Bir sonraki normal aylık döngü: <b>30 Eylül origin → Ekim 2026</b>. Canonical forecast, selector, ensemble veya karar otoritesi yaratılmaz.</div></div>",unsafe_allow_html=True)
    st.markdown("<div class='gc-card'><div class='gc-section-title'>SENARYOLAR</div>"+empty_html("SENARYOLAR HENÜZ YAYIMLANMADI",SCENARIO_STATUS)+"<div class='gc-footnote'>Kanonik senaryo kontratı açılmadan baz/iyimser/kötümser sayı üretilmez.</div></div>",unsafe_allow_html=True)
    spot_value=None if not spot else spot.get("price")
    if forecast and spot_value:
        try: diff_value=float(forecast["forecast_value"])-float(spot_value); diff_pct=diff_value/float(spot_value)*100; diff_display=f"{diff_value:+,.2f} USD · {diff_pct:+.2f}%"; diff_class="gc-positive" if diff_value>=0 else "gc-negative"
        except Exception: diff_display,diff_class="—","gc-muted"
    else: diff_display,diff_class="—","gc-muted"
    performance_body=empty_html("İLERİYE DÖNÜK PERFORMANS HENÜZ OLUŞMADI","Prospective/live canonical forecast gerçekleşmeden MAPE/MAE üretilmez."); st.markdown("<div class='gc-grid2'><div class='gc-card'><div class='gc-section-title'>MEVCUT FİYATA GÖRE FARK</div>"+html_row("Indicative spot",fmt_num(spot_value,2," USD"))+html_row("Canonical H=1",fmt_num(None if not forecast else forecast.get("forecast_value"),2," USD"))+html_row("Fark",diff_display,diff_class)+"<div class='gc-footnote'>Bu aritmetik karşılaştırmadır; beklenen getiri değildir.</div></div><div class='gc-card'><div class='gc-section-title'>MODEL PERFORMANSI</div>"+performance_body+"</div></div>",unsafe_allow_html=True)
    if not replay.empty:
        st.markdown("<div class='gc-replay'><div class='gc-replay-head'><strong>MULTI-EXPERT ARAŞTIRMA KANITI</strong><span class='gc-replay-pill'>HISTORICAL_REPLAY</span></div><div class='gc-grid4'>"+mini_card("CAUSAL PATCH MAPE",fmt_num(rmetrics.get("patch_mape"),2,"%"),"Historical replay")+mini_card("VW-MIDAS-MSVR MAPE",fmt_num(rmetrics.get("vw_mape"),2,"%"),"Historical analytical reference")+mini_card("3M MOMENTUM MAPE",fmt_num(rmetrics.get("mom_mape"),2,"%"),"Direction/context challenger")+mini_card("RANDOM WALK MAPE",fmt_num(rmetrics.get("rw_mape"),2,"%"),"Mandatory benchmark")+"</div><div class='gc-footnote' style='margin-top:.65rem'>Bu skorlar prospective scorecard'a taşınmaz ve 2026 winner/selector üretmez.</div></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='gc-note'><b>Metodoloji:</b> Monthly forecast stratejik anchor/prior'dır; günlük işlem emri değildir. Scenario status: <b>{esc(SCENARIO_STATUS)}</b>. Auto selector: <b>{esc(AUTO_SELECTOR_STATUS)}</b>. Auto ensemble: <b>{esc(AUTO_ENSEMBLE_STATUS)}</b>. Selector: <b>{esc(EXPERT_SELECTION_STATUS)}</b>. Build first → ayrı expert çıktıları → Early Indicative → temiz karşılaştırmalı geçmiş → rolling-origin leakage-safe selector araştırması. Yatırım tavsiyesi değildir.</div>",unsafe_allow_html=True)

else:
    historical_replay_history=safe_call(lambda:get_expert_history_cached(url,TRACK_HISTORICAL_REPLAY),[])
    latest=month_end_history[0].get("as_of") if month_end_history else (early_history[0].get("as_of") if early_history else None); page_head("GEÇMİŞ","Sistem geçmişte gerçekten ne yaptı? Evidence sınıfları birbirine karıştırılmaz.",latest); realized_count=0
    st.markdown("<div class='gc-section-title'>ÖZET METRİKLER</div><div class='gc-footnote' style='margin-bottom:.45rem'><b>PROSPECTIVE / LIVE CANONICAL SCORECARD</b> · Historical Replay bu kartlara girmez.</div>",unsafe_allow_html=True); st.markdown("<div class='gc-grid4'>"+mini_card("REALIZED TAHMİN",str(realized_count),"Outcome-linked prospective/live")+mini_card("MAPE","—","YETERLİ VERİ YOK")+mini_card("MAE (USD)","—","YETERLİ VERİ YOK")+mini_card("YÖN DOĞRULUĞU","—","Frozen outcome tanımı sonrası")+"</div>",unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>TAHMİN PERFORMANSI · GERÇEKLEŞEN / ISSUED</div>",unsafe_allow_html=True)
        if forecast_rows:
            fdf=pd.DataFrame({"Tarih":pd.to_datetime([r.get("target_month") for r in forecast_rows],errors="coerce"),"Canonical Forecast":pd.to_numeric([r.get("forecast_value") for r in forecast_rows],errors="coerce")}).dropna().sort_values("Tarih"); plot_lines(fdf,"Tarih",["Canonical Forecast"],280); st.caption("Outcome bağlanana kadar bu yalnız issued canonical point history'dir; performans sonucu değildir.")
        else: st.markdown(empty_html("İLERİYE DÖNÜK PERFORMANS HENÜZ OLUŞMADI","Governed canonical forecast ve realized outcome henüz yok."),unsafe_allow_html=True)
    with st.container(border=True): st.markdown("<div class='gc-section-title'>HATA / KARAR ZAMAN ÇİZELGESİ</div>",unsafe_allow_html=True); st.markdown(empty_html("REALIZED PROSPECTIVE HATA HENÜZ YOK",f"Persisted decision event: {len(decision_rows)} · outcome gerçekleşmeden hata üretilmez."),unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>SEÇİLMİŞ GEÇMİŞ KAYITLAR</div>",unsafe_allow_html=True)
        if forecast_rows: st.dataframe(pd.DataFrame([{"Hedef Ay":str(r.get("target_month") or "")[:7],"Forecast":r.get("forecast_value"),"Gerçekleşen":None,"APE":None,"Evidence":r.get("evidence_class"),"Model":r.get("model_version")} for r in forecast_rows]),width="stretch",hide_index=True)
        else: st.markdown(empty_html("KANONİK PROSPECTIVE KAYIT YOK",EXPERT_SELECTION_STATUS),unsafe_allow_html=True)
    st.markdown("<div class='gc-card'><div class='gc-section-title'>MULTI-EXPERT FORECAST LEDGER</div>"+selector_lock_html()+"<div class='gc-footnote'>MONTH_END_EXPERT ile EARLY_INDICATIVE farklı track'lerdir; birleştirilmez.</div></div>",unsafe_allow_html=True); mdf=expert_history_frame(month_end_history)
    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>MONTH_END_EXPERT · KARŞILAŞTIRMALI GEÇMİŞ</div>",unsafe_allow_html=True)
        if not mdf.empty:
            pivot=mdf.pivot_table(index="target_month",columns="expert_id",values="forecast_value",aggfunc="last").reset_index(); plot_lines(pivot,"target_month",[c for c in EXPERT_DISPLAY_ORDER if c in pivot.columns],280); cols=[c for c in ["target_month","expert_id","model_version","forecast_value","evidence_class","as_of"] if c in mdf.columns]; table=mdf[cols].tail(20).copy(); table["target_month"]=table["target_month"].dt.strftime("%Y-%m") if "target_month" in table else table.get("target_month"); st.dataframe(table,width="stretch",hide_index=True)
        else: st.markdown(empty_html("MONTH_END_EXPERT KAYDI YOK","İlk eligible expert çıktıları burada ayrı ayrı birikecek."),unsafe_allow_html=True)
    edf=expert_history_frame(early_history)
    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>EARLY INDICATIVE · REVISION HISTORY</div>",unsafe_allow_html=True)
        if not edf.empty and "as_of" in edf.columns:
            pivot=edf.pivot_table(index="as_of",columns="expert_id",values="forecast_value",aggfunc="last").reset_index(); plot_lines(pivot,"as_of",[c for c in EXPERT_DISPLAY_ORDER if c in pivot.columns],250); st.caption("Early Indicative canonical month-end H=1 scorecard'a karıştırılmaz.")
        else: st.markdown(empty_html("EARLY INDICATIVE REVISION YOK","PIT-safe completed-session güncellemeleri ayrı track'te saklanacak."),unsafe_allow_html=True)
    rdf=expert_history_frame(historical_replay_history)
    with st.container(border=True):
        st.markdown("<div class='gc-section-title'>PRODUCTION HISTORICAL_REPLAY · EYLÜL 2026</div>",unsafe_allow_html=True)
        if not rdf.empty:
            pivot=rdf.pivot_table(index="target_month",columns="expert_id",values="forecast_value",aggfunc="last").reset_index(); plot_lines(pivot,"target_month",[c for c in EXPERT_DISPLAY_ORDER if c in pivot.columns],250)
            cols=[c for c in ["target_month","expert_id","model_version","forecast_value","evidence_class","forecast_origin","as_of"] if c in rdf.columns]; table=rdf[cols].copy(); table["target_month"]=table["target_month"].dt.strftime("%Y-%m"); st.dataframe(table,width="stretch",hide_index=True)
            st.caption("ORIGIN_RECONSTRUCTION / HISTORICAL_REPLAY · target/origin: 31 Ağustos → Eylül · gerçek hesaplama/persistence tarihi korunur")
        else: st.markdown(empty_html("PRODUCTION HISTORICAL_REPLAY KAYDI YOK","Replay ledger yalnız HISTORICAL_REPLAY evidence ile okunur."),unsafe_allow_html=True)
    if not replay.empty and {"actual","patch_r1","vw","mom","rw"}.issubset(replay.columns):
        st.markdown("<div class='gc-replay'><div class='gc-replay-head'><strong>ARAŞTIRMA GEÇMİŞİ — AYRI KANIT SINIFI</strong><span class='gc-replay-pill'>HISTORICAL_REPLAY</span></div><div class='gc-grid4'>"+mini_card("PATCH MAPE",fmt_num(rmetrics.get("patch_mape"),2,"%"),"Historical replay")+mini_card("VW MAPE",fmt_num(rmetrics.get("vw_mape"),2,"%"),"Historical analytical")+mini_card("3M MAPE",fmt_num(rmetrics.get("mom_mape"),2,"%"),"Context challenger")+mini_card("RW MAPE",fmt_num(rmetrics.get("rw_mape"),2,"%"),"Benchmark")+"</div></div>",unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='gc-section-title'>HISTORICAL_REPLAY · GERÇEKLEŞEN / DÖRT EXPERT</div>",unsafe_allow_html=True); research=replay.tail(18)[["month","actual","patch_r1","vw","mom","rw"]].rename(columns={"month":"Tarih","actual":"Gerçekleşen","patch_r1":"Causal Patch","vw":"VW-MIDAS-MSVR","mom":"3M Momentum","rw":"Random Walk"}); plot_lines(research,"Tarih",["Gerçekleşen","Causal Patch","VW-MIDAS-MSVR","3M Momentum","Random Walk"],290); st.caption("Replay prospective değildir; selector/ensemble otoritesi yaratmaz.")
    st.markdown("<div class='gc-note'>Evidence ayrımı: HISTORICAL_REPLAY ≠ PROSPECTIVE_SHADOW ≠ LIVE_PRODUCTION. Selector ancak temiz karşılaştırmalı geçmiş üzerinde leakage-safe rolling-origin kanıtla freeze edilebilir; üstün değilse expert'ler ayrı kalır.</div>",unsafe_allow_html=True)

st.markdown("<div id='system-health'></div>",unsafe_allow_html=True)
with st.expander("Sistem / Veri Sağlığı / Audit"):
    st.write("UI contract:",FINAL_MOCKUP_CONTRACT); st.write("Engine observability:",ENGINE_OBSERVABILITY_CONTRACT); st.write("Governed engine inventory:",engine_counts); st.write("Architecture:",MULTI_EXPERT_ARCHITECTURE); st.write("Neon:","BAĞLI" if url else "YAPILANDIRILMADI"); st.write("Decision Store:","KAYIT VAR" if decision else "KAYIT YOK"); st.write("Canonical forecast ledger:","KAYIT VAR" if forecast else "KAYIT YOK / SELECTOR NOT PROVEN"); st.write("MONTH_END_EXPERT rows:",len(month_end_history)); st.write("EARLY_INDICATIVE rows:",len(early_history)); st.write("HISTORICAL_REPLAY rows (active view):",len(historical_replay_history)); st.write("Auto selector:",AUTO_SELECTOR_STATUS); st.write("Auto ensemble:",AUTO_ENSEMBLE_STATUS); st.write("Selector status:",EXPERT_SELECTION_STATUS); st.write("Scenario status:",SCENARIO_STATUS); st.write("Patch executable expert:",PATCH_EXACT_ID); st.write("Patch geometry:",PATCH_GEOMETRY); st.write("VW executable status:","BLOCKED_NOT_PROVEN_EXECUTABLE"); st.write("3M/RW forward source binding:","BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND"); st.write("Historical replay:","MEVCUT" if not replay.empty else "YOK"); st.write("Track constants:",MONTH_END_TRACK,EARLY_INDICATIVE_TRACK)
