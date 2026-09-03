from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "apps" / "engine_observability_contract.py"
APP = ROOT / "apps" / "gold_control_mobile_v1.py"
TEST = ROOT / "apps" / "test_engine_observability_contract.py"


def replace_once(text: str, old: str, new: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{n}:{old[:120]!r}")
    return text.replace(old, new, 1)


def patch_engine() -> None:
    text = ENGINE.read_text(encoding="utf-8")
    old = '''def build_engine_inventory(
    decision: dict[str, Any] | None,
    month_end_experts: list[dict[str, Any]] | None,
    early_experts: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Return every governed motor even when it has no issued value.

    This is a presentation/read-model inventory. It must never create a selector,
    ensemble, final action, or substitute a missing forward output.
    """
    out: list[dict[str, Any]] = []
    for engine_id in ENGINE_DISPLAY_ORDER:
        base = ENGINE_REGISTRY[engine_id]
        if base.get("expert_id"):
            row = _expert_row(engine_id, base, month_end_experts, early_experts)
        else:
            row = _component_row(engine_id, base, decision)
        out.append(row)
    return out
'''
    new = '''def build_engine_inventory(
    decision: dict[str, Any] | None,
    month_end_experts: list[dict[str, Any]] | None,
    early_experts: list[dict[str, Any]] | None,
    runtime_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return every governed motor even when it has no issued value.

    Output values remain sourced only from governed expert/component ledgers.
    Data Evidence Spine runtime rows may supply operational status/provenance,
    but can never synthesize an output, selector, ensemble, final action, or
    canonical authority.
    """
    runtime_by_engine = {
        _text(row.get("engine_id")): dict(row)
        for row in (runtime_rows or [])
        if _text(row.get("engine_id")) in ENGINE_REGISTRY
    }
    out: list[dict[str, Any]] = []
    for engine_id in ENGINE_DISPLAY_ORDER:
        base = ENGINE_REGISTRY[engine_id]
        if base.get("expert_id"):
            row = _expert_row(engine_id, base, month_end_experts, early_experts)
        else:
            row = _component_row(engine_id, base, decision)

        runtime = runtime_by_engine.get(engine_id)
        if runtime:
            runtime_status = _text(runtime.get("runtime_status")).upper()
            status_code = _text(runtime.get("status_code"))
            if runtime_status in {"WAITING", "BLOCKED", "NOT_PROVEN"} and status_code:
                row["status"] = status_code
            elif runtime_status == "ACTIVE" and status_code:
                row["status"] = "STORED_CONTEXT_AVAILABLE" if _available(row.get("output")) else status_code
            elif runtime_status == "ISSUED" and not _available(row.get("output")) and status_code:
                row["status"] = status_code

            row["runtime_status"] = runtime_status or None
            row["runtime_status_code"] = status_code or None
            row["runtime_version"] = runtime.get("engine_version")
            row["runtime_role"] = runtime.get("engine_role")
            row["runtime_evidence_class"] = runtime.get("evidence_class")
            row["runtime_as_of"] = runtime.get("as_of")
            row["runtime_target_context"] = runtime.get("target_context")
            row["runtime_git_commit"] = runtime.get("git_commit")
            row["direction_vote"] = bool(
                row["direction_vote"] and runtime.get("direction_vote_permitted") is True
            )
        else:
            row["runtime_status"] = None
            row["runtime_status_code"] = None
            row["runtime_version"] = None
            row["runtime_role"] = None
            row["runtime_evidence_class"] = None
            row["runtime_as_of"] = None
            row["runtime_target_context"] = None
            row["runtime_git_commit"] = None
        out.append(row)
    return out
'''
    ENGINE.write_text(replace_once(text, old, new), encoding="utf-8")


def patch_app() -> None:
    text = APP.read_text(encoding="utf-8")
    text = replace_once(
        text,
        'from live_sources import fetch_gvz_latest, fetch_xau_history, fetch_xau_spot\n',
        'from live_sources import fetch_gvz_latest, fetch_xau_history, fetch_xau_spot\nfrom runtime_source import fetch_runtime_observability\n',
    )
    old = '''url=db_url(); decision=safe_call(lambda:fetch_current_decision_state(url),None) if url else None; decision_rows=safe_call(lambda:fetch_decision_history(url),[]) if url else []
forecast=safe_call(lambda:fetch_current_forecast(url),None) if url else None; forecast_rows=safe_call(lambda:fetch_forecast_history(url),[]) if url else []
month_end_experts=safe_call(lambda:fetch_latest_expert_forecasts(url,TRACK_MONTH_END),[]) if url else []; early_experts=safe_call(lambda:fetch_latest_expert_forecasts(url,TRACK_EARLY_INDICATIVE),[]) if url else []
month_end_history=safe_call(lambda:fetch_expert_forecast_history(url,TRACK_MONTH_END),[]) if url else []; early_history=safe_call(lambda:fetch_expert_forecast_history(url,TRACK_EARLY_INDICATIVE),[]) if url else []
spot=safe_call(get_spot,None); hist,hist_meta=safe_call(get_xau_history,(pd.DataFrame(),{})); gvz=safe_call(get_gvz,None); replay=load_replay(); rmetrics=replay_metrics(replay); _=classification_label
engine_rows=build_engine_inventory(decision,month_end_experts,early_experts); engine_counts=engine_inventory_counts(engine_rows)
'''
    new = '''url=db_url()
decision=safe_call(lambda:fetch_current_decision_state(url),None) if url else None
decision_rows=safe_call(lambda:fetch_decision_history(url),[]) if url else []
runtime_obs=safe_call(lambda:fetch_runtime_observability(url),None) if url else None
forecast=safe_call(lambda:fetch_current_forecast(url),None) if url else None
forecast_rows=safe_call(lambda:fetch_forecast_history(url),[]) if url else []
month_end_experts=safe_call(lambda:fetch_latest_expert_forecasts(url,TRACK_MONTH_END),[]) if url else []
early_experts=safe_call(lambda:fetch_latest_expert_forecasts(url,TRACK_EARLY_INDICATIVE),[]) if url else []
month_end_history=safe_call(lambda:fetch_expert_forecast_history(url,TRACK_MONTH_END),[]) if url else []
early_history=safe_call(lambda:fetch_expert_forecast_history(url,TRACK_EARLY_INDICATIVE),[]) if url else []
spot=safe_call(get_spot,None); hist,hist_meta=safe_call(get_xau_history,(pd.DataFrame(),{})); gvz=safe_call(get_gvz,None); replay=load_replay(); rmetrics=replay_metrics(replay); _=classification_label
runtime_rows=[] if not runtime_obs else list(runtime_obs.get("runtime") or [])
engine_rows=build_engine_inventory(decision,month_end_experts,early_experts,runtime_rows); engine_counts=engine_inventory_counts(engine_rows)
'''
    text = replace_once(text, old, new)
    old_summary = '''    inventory_summary=(
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
    new_summary = '''    inventory_summary=(
        f"Toplam {engine_counts['total']} motor/kanal · "
        f"Stored context {engine_counts['active']} · Issued expert {engine_counts['issued']} · "
        f"Blocked/Not proven {engine_counts['blocked']} · Waiting {engine_counts['waiting']}"
    )
    if runtime_obs:
        spine_ok=runtime_obs.get("status")=="DATA_EVIDENCE_SPINE_RUNTIME_HEALTH_PASS"
        spine_summary=(
            f"DB Evidence Spine: runtime {runtime_obs.get('runtime_engine_count',0)}/12 · "
            f"context link {runtime_obs.get('context_exactly_one_link',0)}/{runtime_obs.get('context_expected',7)} · "
            f"integrity {'PASS' if spine_ok else 'BLOCKED'}"
        )
    else:
        spine_summary="DB Evidence Spine: KULLANILAMIYOR"
    st.markdown(
        "<div class='gc-card'><div class='gc-section-title'>TÜM TAHMİN VE YÖN MOTORLARI</div>"
        +f"<div class='gc-footnote'><b>{esc(ENGINE_OBSERVABILITY_CONTRACT)}</b><br>{esc(inventory_summary)}<br>{esc(spine_summary)}<br>"
        +"Bir motor blocked olsa bile kartı görünür kalır. Stored yön context'i ile H=1 fiyat forecast'ı birbirine dönüştürülmez.</div>"
        +engine_inventory_cards(engine_rows)+"</div>",
        unsafe_allow_html=True,
    )
'''
    APP.write_text(replace_once(text, old_summary, new_summary), encoding="utf-8")


def patch_test() -> None:
    text = TEST.read_text(encoding="utf-8")
    anchor = '''def test_all_governed_engines_are_always_present() -> None:
'''
    helper = '''def _runtime_rows() -> list[dict]:
    status = {
        "CAUSAL_PATCH": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", False),
        "VW_MIDAS_MSVR": ("BLOCKED", "BLOCKED_NOT_PROVEN_EXECUTABLE", False),
        "MOMENTUM_3M": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", False),
        "RANDOM_WALK": ("WAITING", "WAITING_ELIGIBLE_MONTH_END_ORIGIN", False),
        "MONTHLY_DIRECTION_3M": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", True),
        "FAST": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", True),
        "SLOW": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", True),
        "MACRO_EVENT": ("BLOCKED", "BLOCKED_NOT_FULLY_RECOVERED", False),
        "EMERGENCY_LEVEL": ("BLOCKED", "BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE", False),
        "EMERGENCY_REVERSAL": ("BLOCKED", "BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE", False),
        "BOCPD": ("BLOCKED", "BLOCKED_EXACT_FORWARD_BOCPD_RULE_NOT_RECOVERED", False),
        "GVZ_RISK": ("ACTIVE", "VERIFIED_PERSISTED_CONTEXT_AVAILABLE", False),
    }
    return [
        {
            "engine_id": engine_id,
            "engine_version": f"runtime::{engine_id}",
            "engine_role": "TEST_RUNTIME_ROLE",
            "as_of": "2026-09-03T14:43:00Z",
            "target_context": "2026-09",
            "evidence_class": "RUNTIME_GOVERNANCE_AUDIT",
            "runtime_status": values[0],
            "status_code": values[1],
            "direction_vote_permitted": values[2],
            "git_commit": "3c7e2b1",
        }
        for engine_id, values in status.items()
    ]


'''
    text = replace_once(text, anchor, helper + anchor)
    append = '''

def test_runtime_ledger_is_status_authority_but_never_output_authority() -> None:
    decision = _decision()
    rows = {row["engine_id"]: row for row in build_engine_inventory(decision, [], [], _runtime_rows())}
    assert rows["MONTHLY_DIRECTION_3M"]["output"] == "DOWN"
    assert rows["MONTHLY_DIRECTION_3M"]["status"] == "STORED_CONTEXT_AVAILABLE"
    assert rows["MONTHLY_DIRECTION_3M"]["runtime_status"] == "ACTIVE"
    assert rows["MONTHLY_DIRECTION_3M"]["runtime_status_code"] == "VERIFIED_PERSISTED_CONTEXT_AVAILABLE"
    assert rows["MONTHLY_DIRECTION_3M"]["runtime_evidence_class"] == "RUNTIME_GOVERNANCE_AUDIT"
    assert rows["MONTHLY_DIRECTION_3M"]["direction_vote"] is True
    assert rows["GVZ_RISK"]["direction_vote"] is False
    assert rows["CAUSAL_PATCH"]["output"] is None
    assert rows["CAUSAL_PATCH"]["status"] == "WAITING_ELIGIBLE_MONTH_END_ORIGIN"
    assert rows["VW_MIDAS_MSVR"]["status"] == "BLOCKED_NOT_PROVEN_EXECUTABLE"
    assert all(row["canonical_authority"] is False for row in rows.values())


def test_runtime_cannot_self_promote_non_direction_engine_to_direction_vote() -> None:
    runtime = _runtime_rows()
    for row in runtime:
        if row["engine_id"] == "GVZ_RISK":
            row["direction_vote_permitted"] = True
    rows = {row["engine_id"]: row for row in build_engine_inventory(_decision(), [], [], runtime)}
    assert rows["GVZ_RISK"]["direction_vote"] is False
'''
    TEST.write_text(text + append, encoding="utf-8")


def main() -> int:
    patch_engine()
    patch_app()
    patch_test()
    print("DATA_SPINE_UI_READ_V1_PATCH_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
