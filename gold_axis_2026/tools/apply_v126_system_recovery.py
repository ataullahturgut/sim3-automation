from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"EXPECTED_ONE_MATCH:{path}:{count}:{old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all(path: Path, old: str, new: str, expected: int) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f"EXPECTED_MATCH_COUNT:{path}:{count}:{expected}:{old[:120]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        raise RuntimeError(f"MARKER_ALREADY_PRESENT:{path}:{marker}")
    path.write_text(text.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")


manifest = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
mobile = ROOT / "apps" / "gold_control_mobile_v1.py"
contract = ROOT / "apps" / "mobile_ui_contract.py"
contract_test = ROOT / "apps" / "test_mobile_ui_contract.py"
entry = ROOT / "apps" / "gold_control.py"
qa = ROOT / "apps" / "mobile_viewport_qa.py"
cross_test = ROOT / "apps" / "test_ui_manifest_consistency_v126.py"

# 1) Manifest version + explicit non-model system-recovery change control.
replace_once(manifest, "**Manifest version:** 1.25", "**Manifest version:** 1.26")
append_once(
    manifest,
    "FROZEN_SYSTEM_RECOVERY_UI_CONSISTENCY_V1",
    r'''
### Manifest v1.26 — systematic UI/runtime consistency recovery

Status: `FROZEN_SYSTEM_RECOVERY_UI_CONSISTENCY_V1`

This patch closes presentation/runtime inconsistencies exposed by production-backed mobile evidence. It is a **bug-fix / consistency recovery**, not a model-selection, source-substitution, threshold-retuning, selector, ensemble, or position-mapping change.

Closed defects:

1. **GVZ display invocation mismatch** — the UI called the keyword-only frozen `gvz_regime(..., full_max=..., half_max=...)` contract positionally, which was caught and rendered as `KULLANILAMIYOR` despite valid GVZ data. The call is corrected without changing the frozen thresholds `25.9795 / 30.5238` or caps `1.0 / 0.5 / 0.25`.
2. **Simple-expert UI contract drift** — `mobile_ui_contract.py` still carried pre-promotion `MOMENTUM_3M_R1` / `RW_R1` identities and `BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND`. The user-facing forecast contract is synchronized to the already-approved R2 identities `MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND` and `RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`, both remaining `WAITING_ELIGIBLE_MONTH_END_ORIGIN`. No forecast value is issued by this patch.
3. **Mobile engine-card readability** — the governed 12-engine inventory remains complete, but the 390 px inventory surface now stacks engine cards in one column and enforces internal word wrapping so immutable technical status/version identifiers cannot be clipped inside a card.
4. **Frozen layout visibility** — `SENARYOLAR` is now rendered explicitly as fail-closed while `BLOCKED_NO_CANONICAL_SCENARIO_CONTRACT` remains active; `ÖZET METRİKLER` is rendered explicitly on `Geçmiş`. No scenario value or prospective score is fabricated.
5. **Acceptance drift** — production mobile QA is versioned to v1.26 and adds fail-closed checks for stale R1 simple-expert contracts, internal card overflow, visible scenario/summary sections, valid GVZ regime rendering, selector/ensemble/action locks, and the production DB evidence spine.

Binding operational state remains unchanged by this recovery:

- governed engines/channels: `12/12`;
- runtime distribution: `4 ACTIVE / 3 WAITING / 5 BLOCKED`;
- direction-vote permission: `3` (`Monthly Direction`, `FAST`, `SLOW` only);
- current expert issuance: `0`;
- current canonical H=1 forecast: not issued;
- selector: `NOT_PROVEN_EXPERT_SELECTION_RULE`;
- auto selector = `OFF`;
- auto ensemble = `OFF`;
- position mapping: `NOT_PROVEN_POSITION_MAPPING`;
- September 2026 backfill remains forbidden; no current result is converted into a prospective claim.
''',
)

# 2) Current mobile expert contract must match the promoted registry identities.
replace_once(contract, '"model_version": "MOMENTUM_3M_R1",', '"model_version": "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND",')
replace_once(contract, '"role": "Direction challenger / context expert",', '"role": "Monthly expert / direction challenger; H=1 price output is distinct from stored monthly direction context",')
replace_once(contract, '"model_version": "RW_R1",', '"model_version": "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND",')
replace_all(contract, '"empty_status": "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND",', '"empty_status": "WAITING_ELIGIBLE_MONTH_END_ORIGIN",', expected=2)
replace_once(
    contract,
    'subtitle="NOT_ISSUED_IN_CANONICAL_LEDGER",',
    'subtitle="Kanonik forecast ledger\'da henüz yayımlanmış kayıt yok.",',
)

# 3) Tests must stop institutionalizing the stale R1 blocker.
replace_once(
    contract_test,
    'assert state.subtitle == "NOT_ISSUED_IN_CANONICAL_LEDGER"',
    'assert state.subtitle == "Kanonik forecast ledger\'da henüz yayımlanmış kayıt yok."',
)
replace_all(
    contract_test,
    'assert mom["status"] == "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND"',
    'assert mom["status"] == "WAITING_ELIGIBLE_MONTH_END_ORIGIN"',
    expected=1,
)
replace_all(
    contract_test,
    'assert rw["status"] == "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND"',
    'assert rw["status"] == "WAITING_ELIGIBLE_MONTH_END_ORIGIN"',
    expected=1,
)
replace_once(
    contract_test,
    'def test_final_v2_mockup_contract_is_frozen_with_v122_expert_policy():',
    'def test_final_v2_mockup_contract_is_frozen_with_v126_expert_policy():',
)

# 4) Fix the actual GVZ bug, current manifest identity, missing fail-closed sections, and mobile card readability.
replace_once(
    mobile,
    'MULTI_EXPERT_ARCHITECTURE = "MANIFEST_V1_23_MULTI_EXPERT_BUILD_FIRST_SELECT_LATER_ENGINE_OBSERVABILITY"',
    'MULTI_EXPERT_ARCHITECTURE = "MANIFEST_V1_26_MULTI_EXPERT_BUILD_FIRST_SELECT_LATER_ENGINE_OBSERVABILITY"',
)
replace_once(mobile, 'raise RuntimeError("MANIFEST_V1_23_SELECTOR_STATUS_MISMATCH")', 'raise RuntimeError("MANIFEST_V1_26_SELECTOR_STATUS_MISMATCH")')
replace_once(
    mobile,
    'return gvz_regime(float(value), float(cfg.get("full_cap_max",25.9795)), float(cfg.get("half_cap_max",30.5238)))',
    'return gvz_regime(float(value), full_max=float(cfg.get("full_cap_max",25.9795)), half_max=float(cfg.get("half_cap_max",30.5238)))',
)
replace_once(
    mobile,
    '.gc-expert .role{font-size:.66rem;color:var(--gc-muted);line-height:1.35;margin-top:.16rem}',
    '.gc-expert .role{font-size:.66rem;color:var(--gc-muted);line-height:1.35;margin-top:.16rem;overflow-wrap:anywhere;word-break:break-word}',
)
replace_once(
    mobile,
    '.gc-expert .state{font-size:.65rem;font-weight:800;color:var(--gc-muted);line-height:1.35;word-break:break-word}',
    '.gc-expert .state{font-size:.65rem;font-weight:800;color:var(--gc-muted);line-height:1.35;word-break:break-word;overflow-wrap:anywhere}.gc-expert .note{overflow-wrap:anywhere;word-break:break-word}',
)
replace_once(
    mobile,
    '.gc-card{padding:.86rem .9rem}.gc-expert-grid{grid-template-columns:1fr 1fr}}',
    '.gc-card{padding:.86rem .9rem}.gc-expert-grid{grid-template-columns:1fr 1fr}.gc-engine-grid{grid-template-columns:1fr}}',
)
replace_once(
    mobile,
    'def engine_inventory_cards(rows: list[dict[str, Any]]) -> str:\n',
    '''def engine_status_label(value: Any) -> str:\n    raw=display_state(value,"UNRESOLVED").upper()\n    if raw=="STORED_CONTEXT_AVAILABLE": return "AKTİF · STORED CONTEXT"\n    if raw=="WAITING_ELIGIBLE_MONTH_END_ORIGIN": return "BEKLİYOR · UYGUN AY-SONU ORIGIN"\n    if raw.startswith("ISSUED_"): return "YAYIMLANDI · AYRI EXPERT ÇIKTISI"\n    if raw.startswith("BLOCKED_"): return "BLOCKED · BAĞIMLILIK/KANIT EKSİK"\n    if raw.startswith("NOT_PROVEN_"): return "KANITLANMADI"\n    if raw.startswith("WAITING_") or raw=="NOT_ISSUED": return "BEKLİYOR"\n    return raw.replace("_"," ")\n\ndef engine_inventory_cards(rows: list[dict[str, Any]]) -> str:\n''',
)
replace_once(
    mobile,
    '        output=engine_output_display(row); status=display_state(row.get("status"),"UNRESOLVED")\n',
    '        output=engine_output_display(row); raw_status=display_state(row.get("status"),"UNRESOLVED"); status=engine_status_label(raw_status)\n',
)
replace_once(
    mobile,
    '        cards.append("<div class=\'gc-expert\'>"+f"<div class=\'name\'>{esc(row.get(\'label\'))}</div><div class=\'role\'>{esc(row.get(\'role\'))}</div><div class=\'forecast\'>{esc(output)}</div><div class=\'state\'>{esc(status)}</div><div class=\'note\' style=\'font-size:.61rem;color:var(--gc-muted);line-height:1.35;margin-top:.34rem\'>{esc(detail)}</div></div>")\n    return "<div class=\'gc-expert-grid\'>"+"".join(cards)+"</div>"\n',
    '        cards.append("<div class=\'gc-expert\'>"+f"<div class=\'name\'>{esc(row.get(\'label\'))}</div><div class=\'role\'>{esc(row.get(\'role\'))}</div><div class=\'forecast\'>{esc(output)}</div><div class=\'state\'>{esc(status)}</div><div class=\'note\' style=\'font-size:.60rem;color:var(--gc-muted);line-height:1.35;margin-top:.34rem\'>Teknik durum: {esc(raw_status)}</div><div class=\'note\' style=\'font-size:.60rem;color:var(--gc-muted);line-height:1.35;margin-top:.26rem\'>{esc(detail)}</div></div>")\n    return "<div class=\'gc-expert-grid gc-engine-grid\'>"+"".join(cards)+"</div>"\n',
)
replace_once(
    mobile,
    '    spot_value=None if not spot else spot.get("price")\n',
    '    st.markdown("<div class=\'gc-card\'><div class=\'gc-section-title\'>SENARYOLAR</div>"+empty_html("SENARYOLAR HENÜZ YAYIMLANMADI",SCENARIO_STATUS)+"<div class=\'gc-footnote\'>Kanonik senaryo kontratı açılmadan baz/iyimser/kötümser sayı üretilmez.</div></div>",unsafe_allow_html=True)\n    spot_value=None if not spot else spot.get("price")\n',
)
replace_once(
    mobile,
    '    st.markdown("<div class=\'gc-footnote\' style=\'margin-bottom:.45rem\'><b>PROSPECTIVE / LIVE CANONICAL SCORECARD</b> · Historical Replay bu kartlara girmez.</div>",unsafe_allow_html=True);',
    '    st.markdown("<div class=\'gc-section-title\'>ÖZET METRİKLER</div><div class=\'gc-footnote\' style=\'margin-bottom:.45rem\'><b>PROSPECTIVE / LIVE CANONICAL SCORECARD</b> · Historical Replay bu kartlara girmez.</div>",unsafe_allow_html=True);',
)

# 5) Entrypoint authority comment must identify the actual current manifest.
replace_once(
    entry,
    '# Presentation authority: manifest v1.23 / final mobile V2 shell + all-engine observability contract.',
    '# Presentation authority: manifest v1.26 / final mobile V2 shell + all-engine observability contract.',
)

# 6) Version the browser evidence correctly and make it detect the defects that escaped v1.25.
replace_all(qa, 'v123', 'v126', expected=6)
replace_all(qa, 'V123', 'V126', expected=1)
replace_once(
    qa,
    '        common(page, "bugun"); segmented(page, MARKET_RANGE, 4, "MARKET_RANGE"); shot(page, out, "bugun")\n',
    '        common(page, "bugun"); segmented(page, MARKET_RANGE, 4, "MARKET_RANGE"); bugun_text=body(page);\n        if "RISK GÖRÜNÜMÜ: KULLANILAMIYOR" in bugun_text: raise AssertionError("GVZ_VALID_VALUE_RENDERED_UNAVAILABLE")\n        if not any(token in bugun_text for token in ("RISK GÖRÜNÜMÜ: NORMAL","RISK GÖRÜNÜMÜ: ELEVATED","RISK GÖRÜNÜMÜ: PANIC")): raise AssertionError("GVZ_REGIME_NOT_RENDERED")\n        shot(page, out, "bugun")\n',
)
replace_once(
    qa,
    '        assert_direction_engine_values(page, engine_cards)\n',
    '        assert_direction_engine_values(page, engine_cards)\n        if columns(page, ".gc-engine-grid") != 1: raise AssertionError("GORUNUM_ENGINE_GRID_MUST_BE_SINGLE_COLUMN_AT_390PX")\n        page_text=body(page)\n        if "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND" in page_text: raise AssertionError("STALE_SIMPLE_EXPERT_SOURCE_BLOCKER_VISIBLE")\n        for token in ("MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND","RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"):\n            if token not in page_text: raise AssertionError(f"R2_SIMPLE_EXPERT_IDENTITY_NOT_VISIBLE:{token}")\n        for i in range(engine_cards.count()):\n            dims=engine_cards.nth(i).evaluate("el => ({sw:el.scrollWidth,cw:el.clientWidth,sh:el.scrollHeight,ch:el.clientHeight})")\n            if int(dims["sw"]) > int(dims["cw"]) + 2: raise AssertionError(f"ENGINE_CARD_INTERNAL_HORIZONTAL_OVERFLOW:{i}:{dims}")\n',
)
replace_once(
    qa,
    '        markers(page, "TAHMIN", ["GELECEK AY TAHMİNİ","MULTI-EXPERT MONTHLY FORECAST ENGINE","CAUSAL PATCH","VW-MIDAS-MSVR","3M MOMENTUM","RANDOM WALK","GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI","EARLY INDICATIVE","MEVCUT FİYATA GÖRE FARK","MODEL PERFORMANSI","NOT_PROVEN_EXPERT_SELECTION_RULE","AUTO SELECTOR","AUTO ENSEMBLE","HISTORICAL_REPLAY"])\n',
    '        markers(page, "TAHMIN", ["GELECEK AY TAHMİNİ","MULTI-EXPERT MONTHLY FORECAST ENGINE","CAUSAL PATCH","VW-MIDAS-MSVR","3M MOMENTUM","RANDOM WALK","GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI","EARLY INDICATIVE","SENARYOLAR","MEVCUT FİYATA GÖRE FARK","MODEL PERFORMANSI","NOT_PROVEN_EXPERT_SELECTION_RULE","AUTO SELECTOR","AUTO ENSEMBLE","HISTORICAL_REPLAY","WAITING_ELIGIBLE_MONTH_END_ORIGIN"])\n',
)
replace_once(
    qa,
    '        ordered(page, "TAHMIN", ["GELECEK AY TAHMİNİ","GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI","MULTI-EXPERT MONTHLY FORECAST ENGINE","MEVCUT FİYATA GÖRE FARK","MODEL PERFORMANSI"])\n',
    '        ordered(page, "TAHMIN", ["GELECEK AY TAHMİNİ","GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI","MULTI-EXPERT MONTHLY FORECAST ENGINE","SENARYOLAR","MEVCUT FİYATA GÖRE FARK","MODEL PERFORMANSI"])\n',
)
replace_once(
    qa,
    '        markers(page, "GECMIS", ["MAPE","MAE (USD)","YÖN DOĞRULUĞU","REALIZED TAHMİN","TAHMİN PERFORMANSI","HATA / KARAR ZAMAN ÇİZELGESİ","SEÇİLMİŞ GEÇMİŞ KAYITLAR","MULTI-EXPERT FORECAST LEDGER","MONTH_END_EXPERT","EARLY INDICATIVE","HISTORICAL_REPLAY","NOT_PROVEN_EXPERT_SELECTION_RULE"])\n',
    '        markers(page, "GECMIS", ["ÖZET METRİKLER","MAPE","MAE (USD)","YÖN DOĞRULUĞU","REALIZED TAHMİN","TAHMİN PERFORMANSI","HATA / KARAR ZAMAN ÇİZELGESİ","SEÇİLMİŞ GEÇMİŞ KAYITLAR","MULTI-EXPERT FORECAST LEDGER","MONTH_END_EXPERT","EARLY INDICATIVE","HISTORICAL_REPLAY","NOT_PROVEN_EXPERT_SELECTION_RULE"])\n',
)
replace_once(
    qa,
    '        ordered(page, "GECMIS", ["PROSPECTIVE / LIVE CANONICAL SCORECARD","TAHMİN PERFORMANSI","HATA / KARAR ZAMAN ÇİZELGESİ","SEÇİLMİŞ GEÇMİŞ KAYITLAR","MULTI-EXPERT FORECAST LEDGER"])\n',
    '        ordered(page, "GECMIS", ["ÖZET METRİKLER","TAHMİN PERFORMANSI","HATA / KARAR ZAMAN ÇİZELGESİ","SEÇİLMİŞ GEÇMİŞ KAYITLAR","MULTI-EXPERT FORECAST LEDGER"])\n',
)
replace_once(
    qa,
    '    print("MOBILE_V126_ALL_ENGINE_FINAL_MOCKUP_VIEWPORT_QA_PASS");',
    '    print("MOBILE_V126_SYSTEM_RECOVERY_VIEWPORT_QA_PASS");',
)

# 7) Cross-contract regression guard: app UI identities may never drift from the governed registry again.
cross_test.write_text(
    '''from pathlib import Path\n\nfrom engine_observability_contract import ENGINE_REGISTRY\nfrom mobile_ui_contract import EXPERT_DISPLAY\nfrom piyasa_contract import gvz_regime\n\n\ndef test_monthly_expert_display_contract_matches_governed_registry():\n    for engine_id in ("CAUSAL_PATCH", "VW_MIDAS_MSVR", "MOMENTUM_3M", "RANDOM_WALK"):\n        assert EXPERT_DISPLAY[engine_id]["model_version"] == ENGINE_REGISTRY[engine_id]["version"]\n        assert EXPERT_DISPLAY[engine_id]["empty_status"] == ENGINE_REGISTRY[engine_id]["default_status"]\n\n\ndef test_promoted_simple_experts_are_waiting_not_source_blocked():\n    assert EXPERT_DISPLAY["MOMENTUM_3M"]["model_version"] == "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"\n    assert EXPERT_DISPLAY["RANDOM_WALK"]["model_version"] == "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"\n    assert EXPERT_DISPLAY["MOMENTUM_3M"]["empty_status"] == "WAITING_ELIGIBLE_MONTH_END_ORIGIN"\n    assert EXPERT_DISPLAY["RANDOM_WALK"]["empty_status"] == "WAITING_ELIGIBLE_MONTH_END_ORIGIN"\n\n\ndef test_gvz_frozen_threshold_mapping_is_available():\n    assert gvz_regime(25.9795, full_max=25.9795, half_max=30.5238) == "NORMAL"\n    assert gvz_regime(26.14, full_max=25.9795, half_max=30.5238) == "ELEVATED"\n    assert gvz_regime(30.6, full_max=25.9795, half_max=30.5238) == "PANIC"\n\n\ndef test_current_ui_source_contains_no_stale_v123_or_r1_simple_expert_contract():\n    root = Path(__file__).resolve().parent\n    mobile = (root / "gold_control_mobile_v1.py").read_text(encoding="utf-8")\n    contract = (root / "mobile_ui_contract.py").read_text(encoding="utf-8")\n    entry = (root / "gold_control.py").read_text(encoding="utf-8")\n    assert "BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND" not in contract\n    assert "MOMENTUM_3M_R1" not in contract\n    assert "RW_R1" not in contract\n    assert "MANIFEST_V1_23" not in mobile\n    assert "manifest v1.23" not in entry\n    assert "gvz_regime(float(value), full_max=" in mobile\n    assert "gc-engine-grid" in mobile\n    assert "SENARYOLAR HENÜZ YAYIMLANMADI" in mobile\n    assert "ÖZET METRİKLER" in mobile\n''',
    encoding="utf-8",
)

print("V126_SYSTEM_RECOVERY_PATCH_APPLIED")
