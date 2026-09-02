from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from decision_source import fetch_current_decision_state
from forecast_source import fetch_current_forecast, fetch_forecast_history
from live_sources import fetch_gvz_latest, fetch_xau_history, fetch_xau_spot
from mobile_ui_contract import decision_view_state, deterministic_explanation, evidence_badge, forecast_view_state
from piyasa_contract import filter_history_timeframe, gvz_regime, latest_completed_daily_row, price_delta

ROOT = Path(__file__).resolve().parents[1]
R41_CONFIG = ROOT / "r4_1" / "config" / "frozen_r4_1.json"
HISTORICAL_REPLAY = ROOT / "production_closure" / "production_history_43.csv"

st.set_page_config(page_title="Gold Control Mobile", page_icon="🟡", layout="centered", initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
:root{--gc-navy:#062847;--gc-navy2:#0b365e;--gc-gold:#f3ad32;--gc-ink:#0e2748;--gc-muted:#64748b;--gc-line:#e7edf4;--gc-green:#13a85b;--gc-red:#e63946;--gc-amber:#e59b18;}
[data-testid="stAppViewContainer"]{background:#f8fafc;color:var(--gc-ink)}
.block-container{max-width:860px;padding-top:.35rem;padding-bottom:5.5rem;padding-left:.8rem;padding-right:.8rem}
#MainMenu,footer{visibility:hidden}
[data-testid="stHeader"]{background:transparent;height:.2rem}
.gc-header{display:flex;align-items:center;gap:.75rem;padding:.7rem .2rem 1rem;border-bottom:1px solid var(--gc-line);margin-bottom:.8rem}
.gc-logo{width:40px;height:40px;border:3px solid var(--gc-gold);transform:rotate(30deg);border-radius:9px;display:flex;align-items:center;justify-content:center}
.gc-logo span{transform:rotate(-30deg);font-weight:900;color:var(--gc-gold)}
.gc-brand{font-size:1.28rem;font-weight:850;line-height:1;color:var(--gc-ink)}
.gc-brand small{display:block;color:var(--gc-gold);letter-spacing:.16em;font-size:.64rem;margin-top:.35rem}
.gc-hero{background:linear-gradient(135deg,var(--gc-navy),var(--gc-navy2));color:white;border-radius:20px;padding:1.25rem 1.15rem;margin:.55rem 0 1rem;box-shadow:0 8px 24px rgba(6,40,71,.12)}
.gc-kicker{font-size:.76rem;letter-spacing:.08em;opacity:.72;text-transform:uppercase}
.gc-big{font-size:2.25rem;font-weight:820;line-height:1.1;margin:.35rem 0}
.gc-mid{font-size:1.45rem;font-weight:800;margin:.3rem 0}
.gc-meta{font-size:.82rem;opacity:.78;line-height:1.45}
.gc-badge{display:inline-block;border:1px solid rgba(255,255,255,.28);border-radius:999px;padding:.35rem .65rem;font-weight:750;font-size:.72rem;margin-top:.6rem}
.gc-card{background:white;border:1px solid var(--gc-line);border-radius:16px;padding:1rem;margin:.6rem 0;box-shadow:0 4px 18px rgba(15,39,72,.035)}
.gc-card h4{margin:0 0 .65rem;color:var(--gc-ink)}
.gc-row{display:flex;justify-content:space-between;gap:1rem;padding:.55rem 0;border-bottom:1px solid var(--gc-line);font-size:.9rem}
.gc-row:last-child{border-bottom:none}
.gc-value{font-weight:800;text-align:right}
.gc-positive{color:var(--gc-green)}.gc-negative{color:var(--gc-red)}.gc-warning{color:var(--gc-amber)}.gc-muted{color:var(--gc-muted)}
.gc-empty{background:white;border:1px dashed #cbd5e1;border-radius:16px;padding:1.25rem;text-align:center;margin:.7rem 0}
.gc-empty strong{display:block;color:var(--gc-ink);font-size:1.05rem;margin-bottom:.4rem}
.gc-footnote{font-size:.75rem;color:var(--gc-muted);line-height:1.45}
div[data-baseweb="tab-list"]{position:sticky;bottom:.25rem;z-index:999;background:white;border:1px solid var(--gc-line);border-radius:16px;padding:.3rem;box-shadow:0 7px 25px rgba(15,39,72,.12);justify-content:space-around;margin-top:1rem}
button[data-baseweb="tab"]{border-radius:12px;padding:.65rem .45rem!important;flex:1;font-size:.78rem}
button[data-baseweb="tab"][aria-selected="true"]{background:var(--gc-navy)!important;color:white!important}
@media(max-width:520px){.block-container{padding-left:.55rem;padding-right:.55rem}.gc-big{font-size:1.95rem}.gc-mid{font-size:1.3rem}div[data-testid="column"]{min-width:0}.stDataFrame{font-size:.78rem}}
</style>
    """,
    unsafe_allow_html=True,
)


def html_row(label: str, value: str, value_class: str = "") -> str:
    return f"<div class='gc-row'><span>{label}</span><span class='gc-value {value_class}'>{value}</span></div>"


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


def read_decision(url: str):
    if not url:
        return None
    try:
        return fetch_current_decision_state(url)
    except Exception:
        return None


def read_forecast(url: str):
    if not url:
        return None
    try:
        return fetch_current_forecast(url)
    except Exception:
        return None


def read_forecast_rows(url: str):
    if not url:
        return []
    try:
        return fetch_forecast_history(url)
    except Exception:
        return []


url = db_url()
decision = read_decision(url)
forecast = read_forecast(url)
forecast_rows = read_forecast_rows(url)

st.markdown(
    "<div class='gc-header'><div class='gc-logo'><span>G</span></div><div class='gc-brand'>GOLD CONTROL<small>DECISION SYSTEM</small></div></div>",
    unsafe_allow_html=True,
)

piyasa, gorunum, tahmin, gecmis = st.tabs(["⌂ Bugün", "◉ Görünüm", "↗ Tahmin", "◷ Geçmiş"])

with piyasa:
    st.title("Bugün")
    st.caption("Piyasa şu anda ne durumda? Canlı izleme verisi karar veya tahmin değildir.")
    try:
        spot = get_spot()
    except Exception as exc:
        spot = None
        st.error(f"Canlı XAU/USD kullanılamıyor: {type(exc).__name__}")
    try:
        hist, hist_meta = get_xau_history()
    except Exception:
        hist, hist_meta = pd.DataFrame(), {}
    try:
        gvz = get_gvz()
    except Exception:
        gvz = None

    completed = latest_completed_daily_row(hist)
    completed_close = None if completed is None else float(completed["close"])
    delta = price_delta(None if spot is None else spot.get("price"), completed_close)

    if spot:
        dtext = "Karşılaştırma yok" if delta is None else f"{delta.absolute:+,.2f} USD ({delta.percent:+.2f}%)"
        dclass = "gc-muted" if delta is None else "gc-positive" if delta.absolute >= 0 else "gc-negative"
        st.markdown(
            f"<div class='gc-hero'><div class='gc-kicker'>ALTIN ONS · XAU/USD · INDICATIVE LIVE</div><div class='gc-big'>{float(spot['price']):,.2f} USD</div><div class='{dclass}'><b>{dtext}</b></div><div class='gc-meta'>Kaynak: Gold API · {spot.get('status','unknown').upper()} · display only / no model use</div></div>",
            unsafe_allow_html=True,
        )

    rows = ""
    if completed_close is not None:
        rows += html_row("Son tamamlanmış günlük close", f"{completed_close:,.2f} USD")
    else:
        rows += html_row("Son tamamlanmış günlük close", "KULLANILAMIYOR", "gc-muted")
    if gvz:
        cfg = {}
        try:
            import json
            cfg = json.loads(R41_CONFIG.read_text(encoding="utf-8")) if R41_CONFIG.exists() else {}
        except Exception:
            cfg = {}
        g = cfg.get("gvz", {})
        regime = gvz_regime(float(gvz["close"]), float(g.get("full_cap_max", 25.9795)), float(g.get("half_cap_max", 30.5238)))
        rows += html_row("GVZ risk katmanı", f"{float(gvz['close']):.2f} · {regime}")
    else:
        rows += html_row("GVZ risk katmanı", "KULLANILAMIYOR", "gc-muted")
    current_state = decision_view_state(decision)
    rows += html_row("Son kayıtlı karar durumu", current_state.title)
    st.markdown(f"<div class='gc-card'><h4>Kısa özet</h4>{rows}</div>", unsafe_allow_html=True)

    if not hist.empty:
        timeframe = st.radio("Aralık", ["1A", "3A", "6A", "1Y"], horizontal=True, label_visibility="collapsed")
        chart = filter_history_timeframe(hist, timeframe)
        st.line_chart(chart.set_index("date")[["close"]], height=260)
        st.markdown("<div class='gc-footnote'>XAUS günlük tarihçe yalnız operasyonel display cross-check'tir; canonical EOD/settlement değildir.</div>", unsafe_allow_html=True)
    st.info("Canlı spot ≠ son EOD karar.")

with gorunum:
    st.title("Görünüm")
    st.caption("Mevcut kayıtlı kararın neden oluştuğunu anlayın.")
    state = decision_view_state(decision)
    if not decision:
        st.markdown(f"<div class='gc-empty'><strong>{state.title}</strong>{state.subtitle}</div>", unsafe_allow_html=True)
    else:
        badge, _ = evidence_badge(decision.get("evidence_class"))
        tone_class = "gc-positive" if state.tone == "positive" else "gc-negative" if state.tone == "negative" else "gc-warning" if state.tone == "warning" else ""
        st.markdown(f"<div class='gc-hero'><div class='gc-kicker'>MEVCUT KAYITLI DURUM</div><div class='gc-mid {tone_class}'>{state.title}</div><div class='gc-meta'>{deterministic_explanation(decision)}</div><div class='gc-badge'>{badge}</div></div>", unsafe_allow_html=True)
        cards = [
            ("Aylık bağlam", decision.get("monthly_direction_3m", "N/A")),
            ("Fast", decision.get("fast_state", "N/A")),
            ("Slow", decision.get("slow_state", "N/A")),
            ("BOCPD / Rejim", decision.get("bocpd_context", "N/A")),
            ("Level Emergency", decision.get("level_emergency", "N/A")),
            ("Reversal Emergency", decision.get("reversal_emergency", "N/A")),
            ("GVZ / Risk", decision.get("gvz_cap", "N/A")),
        ]
        st.markdown("<div class='gc-card'><h4>Sinyal özeti</h4>" + "".join(html_row(k, str(v)) for k, v in cards) + "</div>", unsafe_allow_html=True)
    st.caption("Pozisyon/BUY/SELL/HOLD ve güven yüzdesi gösterilmez: NOT_PROVEN_POSITION_MAPPING.")

with tahmin:
    st.title("Tahmin")
    st.caption("Gelecek ay için canonical H=1 model tahmini.")
    fstate = forecast_view_state(forecast)
    if not forecast:
        st.markdown(f"<div class='gc-empty'><strong>{fstate.title}</strong>{fstate.subtitle}<br><br>İlk mümkün tam uyumlu hedef: Ekim 2026, end-Eylül origin.</div>", unsafe_allow_html=True)
        st.info("Eylül 2026 geriye dönük tahmin edilmez. Tahmin değeri uydurulmaz.")
    else:
        badge, _ = evidence_badge(forecast.get("evidence_class"))
        value = float(forecast["forecast_value"])
        target = str(forecast.get("target_month") or "")[:7]
        st.markdown(f"<div class='gc-hero'><div class='gc-kicker'>GELECEK AY TAHMİNİ · {target}</div><div class='gc-big'>{value:,.2f} {forecast.get('unit','USD/oz')}</div><div class='gc-badge'>{badge}</div><div class='gc-meta'>Origin: {forecast.get('forecast_origin','N/A')}</div></div>", unsafe_allow_html=True)
        info = html_row("Model", str(forecast.get("model_version") or "N/A"))
        info += html_row("Forecast contract ID", str(forecast.get("id") or "N/A"))
        info += html_row("Input snapshot sayısı", str(len(forecast.get("forecast_input_snapshot_ids") or [])))
        st.markdown(f"<div class='gc-card'><h4>Model bilgisi</h4>{info}</div>", unsafe_allow_html=True)
        st.caption("Tahmin bandı / güven yüzdesi gösterilmez; kalibre interval modeli henüz frozen değildir.")

with gecmis:
    st.title("Geçmiş")
    st.caption("Sistem geçmişte gerçekten ne yayımladı?")
    if forecast_rows:
        frame = pd.DataFrame([
            {
                "Hedef ay": str(r.get("target_month") or "")[:7],
                "Tahmin": r.get("forecast_value"),
                "Birim": r.get("unit"),
                "Evidence": r.get("evidence_class"),
                "Model": r.get("model_version"),
                "Origin": r.get("forecast_origin"),
            }
            for r in forecast_rows
        ])
        st.dataframe(frame, use_container_width=True, hide_index=True)
        st.caption("Gerçekleşen/APE metrikleri ancak target outcome gerçekleştikten ve canonical actual bağlandıktan sonra hesaplanır.")
    else:
        st.markdown("<div class='gc-empty'><strong>İLERİYE DÖNÜK PERFORMANS HENÜZ OLUŞMADI</strong>Prospective/live ledger'da gösterilecek forecast geçmişi yok.</div>", unsafe_allow_html=True)

    if HISTORICAL_REPLAY.exists():
        with st.expander("Araştırma · HISTORICAL_REPLAY"):
            replay = pd.read_csv(HISTORICAL_REPLAY)
            st.warning("HISTORICAL_REPLAY — prospective/live performans değildir.")
            st.dataframe(replay.tail(20), use_container_width=True, hide_index=True)

with st.expander("Sistem / Veri Sağlığı / Audit"):
    st.write("Decision Store:", "CONNECTED" if url else "NOT_CONFIGURED")
    st.write("Current decision evidence:", None if not decision else decision.get("evidence_class"))
    st.write("Current forecast evidence:", None if not forecast else forecast.get("evidence_class"))
    st.write("Mobile UI contract:", "APPROVED_MOBILE_PRODUCT_UI_CONTRACT_V1")
    st.write("Canonical branch: `gold-r4-direction-engine`")
    st.caption("Mockup sayıları production verisi değildir; yalnız canonical ledger/source değerleri render edilir.")
