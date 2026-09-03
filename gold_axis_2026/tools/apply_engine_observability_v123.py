from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "gold_axis_2026"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{path}:{count}:{old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(path: Path, marker: str, addition: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(marker)
    if count != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MARKER:{path}:{count}:{marker[:80]!r}")
    path.write_text(text.replace(marker, addition + marker, 1), encoding="utf-8")


def patch_decision_source() -> None:
    path = GOLD / "apps" / "decision_source.py"
    old = '''        "context_components": tuple(sorted(latest)),
        "context_feature_ids": {name: row.get("id") for name, row in latest.items()},
        "target_month": target_month,
'''
    new = '''        "context_components": tuple(sorted(latest)),
        "context_feature_ids": {name: row.get("id") for name, row in latest.items()},
        "context_feature_versions": {name: row.get("feature_version") for name, row in latest.items()},
        "context_feature_updated_at": {name: _iso(row.get("calculation_ts")) for name, row in latest.items()},
        "context_feature_input_cutoff": {name: _iso(row.get("input_cutoff")) for name, row in latest.items()},
        "context_feature_evidence": {
            name: (dict(row.get("metadata") or {}).get("evidence_class") or row.get("quality_status"))
            for name, row in latest.items()
        },
        "target_month": target_month,
'''
    replace_once(path, old, new)


def patch_mobile_app() -> None:
    path = GOLD / "apps" / "gold_control_mobile_v1.py"

    replace_once(
        path,
        'from decision_source import fetch_current_decision_state, fetch_decision_history\n',
        'from decision_source import fetch_current_decision_state, fetch_decision_history\n'
        'from engine_observability_contract import (\n'
        '    ENGINE_OBSERVABILITY_CONTRACT,\n'
        '    build_engine_inventory,\n'
        '    engine_inventory_counts,\n'
        ')\n',
    )

    replace_once(
        path,
        'MULTI_EXPERT_ARCHITECTURE = "MANIFEST_V1_22_MULTI_EXPERT_BUILD_FIRST_SELECT_LATER"\n',
        'MULTI_EXPERT_ARCHITECTURE = "MANIFEST_V1_23_MULTI_EXPERT_BUILD_FIRST_SELECT_LATER_ENGINE_OBSERVABILITY"\n',
    )
    replace_once(
        path,
        '    raise RuntimeError("MANIFEST_V1_22_SELECTOR_STATUS_MISMATCH")\n',
        '    raise RuntimeError("MANIFEST_V1_23_SELECTOR_STATUS_MISMATCH")\n',
    )

    expert_marker = '''def selector_lock_html() -> str:
'''
    engine_helpers = '''def engine_output_display(row: dict[str, Any]) -> str:
    value=row.get("output")
    if value is None or str(value).strip()=="": return "—"
    if row.get("category")=="MONTHLY_FORECAST":
        try: return fmt_num(value,2," USD")
        except Exception: return display_state(value,"—")
    if row.get("direction_vote") is True:
        arrow,_=arrow_state(value); return f"{arrow} {display_state(value,'—')}"
    return display_state(value,"—")

def engine_inventory_cards(rows: list[dict[str, Any]]) -> str:
    cards=[]
    for row in rows:
        output=engine_output_display(row); status=display_state(row.get("status"),"UNRESOLVED")
        evidence=display_state(row.get("evidence_class"),"NO_CURRENT_EVIDENCE")
        version=display_state(row.get("version"),"VERSION_NOT_PROVEN")
        updated=fmt_time(row.get("as_of"))
        vote="YÖN OYU" if row.get("direction_vote") is True else "YÖN OYU DEĞİL"
        detail=f"{row.get('category')} · {vote} · {evidence} · {version} · Son: {updated}"
        cards.append("<div class='gc-expert'>"+f"<div class='name'>{esc(row.get('label'))}</div><div class='role'>{esc(row.get('role'))}</div><div class='forecast'>{esc(output)}</div><div class='state'>{esc(status)}</div><div class='note' style='font-size:.61rem;color:var(--gc-muted);line-height:1.35;margin-top:.34rem'>{esc(detail)}</div></div>")
    return "<div class='gc-expert-grid'>"+"".join(cards)+"</div>"

'''
    insert_before_once(path, expert_marker, engine_helpers)

    data_marker = 'spot=safe_call(get_spot,None); hist,hist_meta=safe_call(get_xau_history,(pd.DataFrame(),{})); gvz=safe_call(get_gvz,None); replay=load_replay(); rmetrics=replay_metrics(replay); _=classification_label\n'
    data_new = data_marker + 'engine_rows=build_engine_inventory(decision,month_end_experts,early_experts); engine_counts=engine_inventory_counts(engine_rows)\n'
    replace_once(path, data_marker, data_new)

    replace_once(
        path,
        'updated=None if not decision else decision.get("generated_at") or decision.get("decision_as_of"); page_head("GÖRÜNÜM","Sistem neden böyle düşünüyor? Aylık prior ve intramonth katmanlar ayrı okunur.",updated);',
        'updated=None if not decision else decision.get("generated_at") or decision.get("decision_as_of"); page_head("GÖRÜNÜM","Önce tüm tahmin, yön, event, emergency, rejim ve risk motorlarını gör; karar/selector katmanı sonraki aşamadır.",updated);',
    )

    summary_marker = '    summary=html_row("Frozen Final Decision State",state.title)+html_row("Monthly Direction / Prior / Context",display_state(monthly,"YAYIMLANMADI"))+html_row("Prior / intramonth ilişki",relation)+html_row("Evidence",badge_text);'
    inventory_block = '''    inventory_summary=(
        f"Toplam {engine_counts['total']} motor/kanal · "
        f"Stored context {engine_counts['active']} · Issued expert {engine_counts['issued']} · "
        f"Blocked/Not proven {engine_counts['blocked']} · Waiting {engine_counts['waiting']}"
    )
    st.markdown(
        "<div class='gc-card'><div class='gc-section-title'>TÜM TAHMİN VE YÖN MOTORLARI</div>"
        +f"<div class='gc-footnote'><b>{esc(ENGINE_OBSERVABILITY_CONTRACT)}</b><br>{esc(inventory_summary)}<br>"
        +"Bir motor blocked olsa bile kartı görünür kalır. Stored yön context'i ile H=1 fiyat forecast'ı birbirine dönüştürülmez.</div>"
        +engine_inventory_cards(engine_rows)+"</div>",
        unsafe_allow_html=True,
    )
'''
    insert_before_once(path, summary_marker, inventory_block)

    replace_once(
        path,
        'with st.expander("Sistem / Veri Sağlığı / Audit"):\n    st.write("UI contract:",FINAL_MOCKUP_CONTRACT);',
        'with st.expander("Sistem / Veri Sağlığı / Audit"):\n    st.write("UI contract:",FINAL_MOCKUP_CONTRACT); st.write("Engine observability:",ENGINE_OBSERVABILITY_CONTRACT); st.write("Governed engine inventory:",engine_counts);',
    )


def patch_manifest() -> None:
    path = GOLD / "GOLD_CONTROL_PROJECT_MANIFEST.md"
    replace_once(path, "**Manifest version:** 1.22  \n**Freeze / issue date:** 2026-09-02  \n", "**Manifest version:** 1.23\n**Freeze / issue date:** 2026-09-03\n")
    replace_once(
        path,
        "9. exposes the result through a simple user-facing interface without leaking backend complexity into the main UX.\n",
        "9. exposes the result through a simple user-facing interface without leaking backend complexity into the main UX,\n10. exposes a complete governed forecast/direction/event/regime/risk motor inventory so users can verify what is running, waiting, blocked, or not proven before any later selector/final-decision research.\n",
    )
    replace_once(
        path,
        "2. **Görünüm** — Sistem neden böyle düşünüyor?\n",
        "2. **Görünüm** — Hangi tahmin/yön/event/regime/risk motorları mevcut, hangileri çalışıyor veya blocked, son meşru çıktıları nedir ve sistem neden böyle düşünüyor?\n",
    )

    marker = "## 7.1 H=1 role freeze — restored agreed architecture\n"
    section = '''## 7.C ALL-ENGINE OBSERVABILITY / INVENTORY-FIRST POLICY — v1.23

This subsection freezes the user-facing observability requirement before any future expert-selection or final-decision research.

Binding contract:

`gold_axis_2026/GOLD_CONTROL_ENGINE_OBSERVABILITY_CONTRACT_2026-09-03.md`

Status:

`FROZEN_ALL_GOVERNED_ENGINES_VISIBLE_V1`

Binding rules:

1. **All governed forecast and direction-related motors must remain visible as inventory items even when they have no issued value.** `BLOCKED`, `NOT_PROVEN`, `WAITING`, and `NOT_ISSUED` are legitimate observable states and must not collapse into a blank card.
2. The frozen inventory covers the four monthly H=1 experts (Causal Patch, VW-MIDAS-MSVR, 3M Momentum, Random Walk), the stored Monthly Direction 3M channel, Fast, Slow, Macro Event, Emergency Level, Emergency Reversal, BOCPD, and GVZ risk context.
3. Each item must expose its role, latest legitimate output if one exists, explicit operational status/blocker, model/feature version, evidence class, target/as-of context, and whether it is permitted to cast a direction vote.
4. A stored direction context is **not** an H=1 point forecast. In particular, `MONTHLY_DIRECTION_3M` may be displayable while the `MOMENTUM_3M` H=1 monthly-level expert remains `BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND`.
5. GVZ remains risk-only and must never be rendered as a bullish/bearish direction vote.
6. Historical replay may be displayed as research evidence but may never be silently promoted to a current prospective/live output.
7. The application remains a read/presentation layer; it may not invent missing outputs, recompute production direction from live spot, or substitute providers/values merely to populate the inventory.
8. `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, `NOT_PROVEN_EXPERT_SELECTION_RULE`, and `NOT_PROVEN_POSITION_MAPPING` remain unchanged. Engine visibility does not authorize a winner, composite forecast, or action mapping.
9. The implementation sequence is now explicitly: **see all motors → verify operation/evidence → accumulate clean comparable outputs → research selector/decision rules later**.
10. The existing `APPROVED_FINAL_MOCKUP_UI_CONTRACT_V2` remains the visual-shell authority; this v1.23 contract extends content completeness/observability and does not change model methodology.

Authority rationale: the 2026 Federal Reserve/OCC/FDIC revised model-risk guidance emphasizes comprehensive model inventory, ongoing monitoring, limitations, outputs and functioning status; NIST AI RMF Govern 1.6 calls for mechanisms to inventory AI systems; NIST AI 800-4 emphasizes post-deployment functionality/operational monitoring. Gold Control adopts these principles as internal engineering governance, without claiming banking-regulatory applicability.

'''
    insert_before_once(path, marker, section)


def main() -> None:
    patch_decision_source()
    patch_mobile_app()
    patch_manifest()
    print("ENGINE_OBSERVABILITY_V123_PATCH_PASS")


if __name__ == "__main__":
    main()
