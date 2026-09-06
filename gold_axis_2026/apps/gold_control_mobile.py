from __future__ import annotations

import os
from typing import Any

import pandas as pd
import streamlit as st

from engine_observability_contract import build_engine_inventory, engine_inventory_counts
from live_sources import fetch_gvz_latest, fetch_xau_history, fetch_xau_spot
from runtime_source import fetch_runtime_observability


st.set_page_config(page_title="Gold Control", page_icon="🟡", layout="centered", initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stToolbarActions"],[data-testid="stDecoration"]{display:none!important}
.block-container{max-width:880px;padding:.8rem .8rem 6rem}
.gc-head{display:flex;align-items:center;gap:.65rem;border-bottom:1px solid #e6ebf1;padding:.35rem 0 .9rem;margin-bottom:.8rem}
.gc-logo{width:42px;height:42px;border:4px solid #f2ad36;border-radius:11px;display:flex;align-items:center;justify-content:center;color:#f2ad36;font-weight:900}
.gc-brand{font-size:1.25rem;font-weight:900;color:#10294b}.gc-brand small{display:block;font-size:.62rem;color:#687995;letter-spacing:.12em;margin-top:.2rem}
.gc-card{background:#fff;border:1px solid #e3e9f0;border-radius:16px;padding:.95rem 1rem;margin:.65rem 0;box-shadow:0 4px 16px rgba(16,41,75,.04)}
.gc-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.65rem}.gc-mini{background:#fff;border:1px solid #e3e9f0;border-radius:15px;padding:.8rem;min-height:116px}
.gc-label{font-size:.68rem;font-weight:900;color:#687995;text-transform:uppercase}.gc-value{font-size:1.18rem;font-weight:900;color:#10294b;margin:.38rem 0}.gc-note{font-size:.68rem;color:#687995;line-height:1.4;overflow-wrap:anywhere}
.gc-ok{color:#168a4b}.gc-warn{color:#c57d00}.gc-bad{color:#d13c4b}.gc-muted{color:#687995}.gc-lock{background:#f7f9fc;border:1px solid #dfe6ee;border-radius:14px;padding:.75rem;font-size:.73rem;color:#50647e;line-height:1.45}
@media(max-width:600px){.gc-grid{grid-template-columns:1fr}.block-container{padding-left:.55rem;padding-right:.55rem}.gc-mini{min-height:100px}}
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


def text(value: Any, default: str = "—") -> str:
    if value is None:
        return default
    raw = str(value).strip()
    return raw if raw else default


def fmt_output(row: dict[str, Any]) -> str:
    value = row.get("output")
    if value is None:
        return "—"
    if row.get("category") == "MONTHLY_FORECAST":
        try:
            return f"{float(value):,.2f} USD/oz"
        except Exception:
            pass
    return text(value)


def status_class(runtime_status: Any) -> str:
    status = text(runtime_status, "MISSING").upper()
    if status == "ACTIVE":
        return "gc-ok"
    if status in {"WAITING", "MISSING"}:
        return "gc-warn"
    return "gc-bad"


@st.cache_data(ttl=30, show_spinner=False)
def runtime_data(url: str) -> dict[str, Any]:
    return fetch_runtime_observability(url)


@st.cache_data(ttl=30, show_spinner=False)
def spot_data() -> dict[str, Any] | None:
    return fetch_xau_spot()


@st.cache_data(ttl=1800, show_spinner=False)
def history_data():
    return fetch_xau_history()


@st.cache_data(ttl=1800, show_spinner=False)
def gvz_data() -> dict[str, Any] | None:
    return fetch_gvz_latest()


url = db_url()
runtime = runtime_data(url)
runtime_rows = list(runtime.get("runtime") or [])
engine_rows = build_engine_inventory(None, None, None, runtime_rows)
counts = engine_inventory_counts(engine_rows)
spot = spot_data()
gvz = gvz_data()

st.markdown("<div class='gc-head'><div class='gc-logo'>G</div><div class='gc-brand'>GOLD CONTROL<small>CURRENT DECISION-SUPPORT SURFACE</small></div></div>", unsafe_allow_html=True)

nav = st.radio("Navigation", ["Piyasa", "Görünüm", "Tahmin", "Geçmiş"], horizontal=True, label_visibility="collapsed")

if nav == "Piyasa":
    st.subheader("Piyasa")
    if spot:
        price = spot.get("price")
        try:
            price_text = f"{float(price):,.2f} USD/oz"
        except Exception:
            price_text = text(price)
        st.markdown(
            f"<div class='gc-card'><div class='gc-label'>XAU/USD · indicative live display</div><div class='gc-value'>{price_text}</div><div class='gc-note'>Kaynak: {text(spot.get('source'))} · model authority değildir · as-of: {text(spot.get('as_of') or spot.get('updated_at'))}</div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.warning("Canlı XAU/USD display kaynağı okunamadı.")
    if gvz:
        st.markdown(
            f"<div class='gc-card'><div class='gc-label'>GVZ display</div><div class='gc-value'>{text(gvz.get('value') or gvz.get('price'))}</div><div class='gc-note'>Risk bağlamıdır; altın yön tahmini değildir.</div></div>",
            unsafe_allow_html=True,
        )

elif nav == "Görünüm":
    st.subheader("Current 12-motor görünümü")
    st.markdown(
        f"<div class='gc-lock'>Runtime: <b>{counts['active']}/12 ACTIVE</b> · WAITING {counts['waiting']} · BLOCKED {counts['blocked']} · MISSING {counts['missing']}<br>AUTO_SELECTOR=OFF · AUTO_ENSEMBLE=OFF · position mapping yok.</div>",
        unsafe_allow_html=True,
    )
    cards: list[str] = []
    for row in engine_rows:
        cls = status_class(row.get("runtime_status"))
        cards.append(
            "<div class='gc-mini'>"
            f"<div class='gc-label'>{text(row.get('label'))}</div>"
            f"<div class='gc-value'>{fmt_output(row)}</div>"
            f"<div class='{cls}' style='font-size:.68rem;font-weight:900'>{text(row.get('runtime_status'))}</div>"
            f"<div class='gc-note'>{text(row.get('role'))}<br>{text(row.get('evidence_class'))} · as-of {text(row.get('as_of'))}</div>"
            "</div>"
        )
    st.markdown("<div class='gc-grid'>" + "".join(cards) + "</div>", unsafe_allow_html=True)

elif nav == "Tahmin":
    st.subheader("Eylül 2026 · 31 Ağustos origin")
    forecast_rows = [row for row in engine_rows if row.get("category") == "MONTHLY_FORECAST"]
    for row in forecast_rows:
        st.markdown(
            "<div class='gc-card'>"
            f"<div class='gc-label'>{text(row.get('label'))}</div>"
            f"<div class='gc-value'>{fmt_output(row)}</div>"
            f"<div class='gc-note'>H=1 aylık expert/reference · {text(row.get('evidence_class'))} · runtime {text(row.get('runtime_status'))}</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    st.info("Bu expert tahminleri otomatik olarak ortalanmaz, ağırlıklandırılmaz veya winner-selected yapılmaz. Eylül referansları 31 Ağustos bilgi sınırından sonradan yeniden hesaplandığı için prospective issuance değildir.")

else:
    st.subheader("Geçmiş piyasa")
    try:
        history, meta = history_data()
    except Exception:
        history, meta = pd.DataFrame(), {}
    if isinstance(history, pd.DataFrame) and not history.empty:
        frame = history.copy()
        if "date" in frame.columns:
            frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
            frame = frame.dropna(subset=["date"]).sort_values("date")
            if "close" in frame.columns:
                st.line_chart(frame.set_index("date")["close"])
        st.caption(f"Kaynak: {text((meta or {}).get('source'))}")
    else:
        st.info("Geçmiş XAU display verisi okunamadı.")

st.caption(
    f"Runtime source: {text(runtime.get('source_mode'))} · contract: {text(runtime.get('contract'))} · target: {text(runtime.get('context_target'))}. "
    "Current registry durumu canlı refresh başarısıyla aynı şey değildir; freshness ayrı audit edilir."
)
