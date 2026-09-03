from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS = ROOT / "apps"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{path}:{count}:{old[:90]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_entrypoint() -> None:
    path = APPS / "gold_control.py"
    old = '''_load_exact_module(\n    "decision_source",\n    APP_DIR / "decision_source.py",\n    required_exports=("fetch_current_decision_state", "fetch_decision_history"),\n)\n'''
    new = '''_load_exact_module(\n    "aug31_state_replay_source",\n    APP_DIR / "aug31_state_replay_source.py",\n    required_exports=("fetch_aug31_state_replay",),\n)\n_load_exact_module(\n    "decision_source",\n    APP_DIR / "decision_source.py",\n    required_exports=("fetch_current_decision_state", "fetch_decision_history"),\n)\n'''
    replace_once(path, old, new)


def patch_mobile() -> None:
    path = APPS / "gold_control_mobile_v1.py"
    replace_once(
        path,
        'from runtime_source import fetch_runtime_observability\n',
        'from runtime_source import fetch_runtime_observability\nfrom aug31_state_replay_source import fetch_aug31_state_replay\n',
    )
    replace_once(
        path,
        '''@st.cache_data(ttl=30, show_spinner=False)\ndef get_expert_history_cached(database_url: str, forecast_track: str): return fetch_expert_forecast_history(database_url,forecast_track)\n''',
        '''@st.cache_data(ttl=30, show_spinner=False)\ndef get_expert_history_cached(database_url: str, forecast_track: str): return fetch_expert_forecast_history(database_url,forecast_track)\n@st.cache_data(ttl=30, show_spinner=False)\ndef get_aug31_state_replay_cached(database_url: str): return fetch_aug31_state_replay(database_url)\n''',
    )
    helper_anchor = '''def engine_status_label(value: Any) -> str:\n'''
    helper = '''def aug31_state_replay_html(state: dict[str, Any] | None) -> str:\n    if not state:\n        return empty_html("31 AĞUSTOS STATE REPLAY OKUNAMADI","Production Evidence Spine ve deployment replay snapshot kullanılamıyor.")\n    ma,mt=arrow_state(state.get("monthly_direction_3m")); fa,ft=arrow_state(state.get("fast_state")); sa,stn=arrow_state(state.get("slow_state"))\n    source="DB READ-ONLY" if state.get("source_mode")=="NEON_DB_READ_ONLY" else "SNAPSHOT FALLBACK"\n    rows=(\n        html_row("Monthly Direction 3M",f"{ma} {display_state(state.get('monthly_direction_3m'),'—')}",tone_class(mt))\n        +html_row("FAST",f"{fa} {display_state(state.get('fast_state'),'—')}",tone_class(ft))\n        +html_row("SLOW",f"{sa} {display_state(state.get('slow_state'),'—')}",tone_class(stn))\n        +html_row("GVZ",f"{fmt_num(state.get('gvz_value'),2)} · {display_state(state.get('gvz_regime'),'—')}")\n        +html_row("GVZ risk cap",fmt_num(state.get("gvz_cap"),1))\n    )\n    blockers=dict(state.get("blocked_components") or {})\n    blocker_rows="".join(html_row(k,v,"gc-warning") for k,v in blockers.items())\n    return (\n        "<div class='gc-card' style='margin-top:.7rem'><div class='gc-section-title'>31 AĞUSTOS 2026 EOD STATE REPLAY</div>"\n        +f"<div class='gc-footnote'><b>HISTORICAL REPLAY · PROSPECTIVE DEĞİL</b> · state boundary 31.08.2026 17:00 ET · kaynak: {esc(source)}. Bu durumlar H=1 fiyat tahmini değildir ve current yön oyu/kararı değiştirmez.</div>"\n        +rows\n        +"<div class='gc-track-head'><b>REPLAY'DE DOLDURULAMAYAN MOTORLAR</b><span class='gc-track-pill'>FAIL-CLOSED</span></div>"\n        +blocker_rows\n        +"</div>"\n    )\n\n'''
    text = path.read_text(encoding="utf-8")
    if helper.strip() in text:
        raise RuntimeError("AUG31_STATE_REPLAY_HELPER_ALREADY_PRESENT")
    if text.count(helper_anchor) != 1:
        raise RuntimeError("AUG31_STATE_REPLAY_HELPER_ANCHOR_MISMATCH")
    path.write_text(text.replace(helper_anchor, helper + helper_anchor, 1), encoding="utf-8")

    replace_once(
        path,
        '''elif nav=="↗ Tahmin":\n    historical_replay_experts=safe_call(lambda:get_latest_experts_cached(url,TRACK_HISTORICAL_REPLAY),[])\n''',
        '''elif nav=="↗ Tahmin":\n    historical_replay_experts=safe_call(lambda:get_latest_experts_cached(url,TRACK_HISTORICAL_REPLAY),[])\n    aug31_state_replay=safe_call(lambda:get_aug31_state_replay_cached(url),None)\n''',
    )
    old_replay = '''    st.markdown("<div class='gc-replay'><div class='gc-replay-head'><strong>EYLÜL 2026 HISTORICAL REPLAY</strong><span class='gc-replay-pill'>REPLAY · PROSPECTIVE DEĞİL</span></div>"+replay_db_body+"<div class='gc-footnote' style='margin-top:.65rem'><b>Resmî prospective durum:</b> NOT_ISSUED_MISSED_2026_08_31_ORIGIN. Bu satırlar 31 Ağustos bilgi kesitiyle sonradan yeniden hesaplanmıştır; canonical forecast, selector, ensemble veya yön oyu değildir.</div></div>",unsafe_allow_html=True)\n'''
    new_replay = '''    st.markdown("<div class='gc-replay'><div class='gc-replay-head'><strong>EYLÜL 2026 HISTORICAL REPLAY</strong><span class='gc-replay-pill'>REPLAY · PROSPECTIVE DEĞİL</span></div><div class='gc-footnote'><b>H=1 EXPERT REPLAY</b> · Aşağıdaki USD değerleri Eylül aylık ortalama fiyat replay'idir.</div>"+replay_db_body+aug31_state_replay_html(aug31_state_replay)+"<div class='gc-footnote' style='margin-top:.65rem'><b>Resmî prospective durum:</b> NOT_ISSUED_MISSED_2026_08_31_ORIGIN. H=1 replay ile 31 Ağustos EOD state replay birbirinden ayrıdır; hiçbiri canonical forecast, selector, ensemble, current yön oyu veya karar değildir.</div></div>",unsafe_allow_html=True)\n'''
    replace_once(path, old_replay, new_replay)


def patch_manifest() -> None:
    path = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
    text = path.read_text(encoding="utf-8")
    if "FROZEN_AUG31_EOD_STATE_REPLAY_V1" in text:
        raise RuntimeError("MANIFEST_V130_ALREADY_PRESENT")
    if text.count("**Manifest version:** 1.29") != 1:
        raise RuntimeError("MANIFEST_V129_HEADER_NOT_UNIQUE")
    text = text.replace("**Manifest version:** 1.29", "**Manifest version:** 1.30", 1)
    text += '''\n\n## v1.30 — 31-August EOD State Historical Replay Closure\n\n- Frozen contract: `FROZEN_AUG31_EOD_STATE_REPLAY_V1`.\n- Deployment fallback contract: `FROZEN_AUG31_STATE_REPLAY_DISPLAY_SNAPSHOT_V1`.\n- September official H=1 prospective status remains `NOT_ISSUED_MISSED_2026_08_31_ORIGIN`; no backdating or prospective relabeling is introduced.\n- The existing September H=1 historical replay remains separate: `MOMENTUM_3M` and `RANDOM_WALK` price-level replay only.\n- A second replay layer now reconstructs the 31-August EOD component state from frozen rules and source observations ending at the boundary: Monthly Direction 3M, FAST, SLOW and GVZ risk state.\n- State replay rows are persisted under replay-specific feature identities with `HISTORICAL_REPLAY`, `prospective_h1_claim=false`, `current_runtime_authority=false`, `canonical_authority=false`; `latest_engine_runtime_state` excludes them.\n- Components that cannot be exactly reproduced remain explicit blockers: Causal Patch replay input set, VW executable identity, full Macro Event rule, authorized Emergency monthly reference, and exact BOCPD forward rule.\n- UI must show `31 AĞUSTOS 2026 EOD STATE REPLAY` inside the September replay surface, distinct from H=1 expert replay. FAST/SLOW/GVZ state values are not H=1 forecasts.\n- A hosting instance without `NEON_DATABASE_URL` reads a fingerprint-validated read-only state-replay deployment snapshot generated from production Neon.\n- Locks retained: `NOT_PROVEN_EXPERT_SELECTION_RULE`, `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, `NOT_PROVEN_POSITION_MAPPING`; canonical forecast and Decision Store remain empty.\n'''
    path.write_text(text, encoding="utf-8")


def main() -> int:
    patch_entrypoint()
    patch_mobile()
    patch_manifest()
    print("V130_AUG31_STATE_REPLAY_UI_PATCH_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
