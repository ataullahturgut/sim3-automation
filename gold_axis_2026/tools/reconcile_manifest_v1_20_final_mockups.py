from pathlib import Path

MANIFEST = Path('gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md')

text = MANIFEST.read_text(encoding='utf-8')

if '**Manifest version:** 1.19' not in text:
    raise SystemExit('EXPECTED_MANIFEST_V1_19_NOT_FOUND')

text = text.replace('**Manifest version:** 1.19', '**Manifest version:** 1.20', 1)

start_marker = '## 17.6 Approved mobile product UI V1'
end_marker = '\n---\n\n# 18. UI / DESIGN SYSTEM FREEZE'
start = text.find(start_marker)
end = text.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit('MOBILE_UI_SECTION_BOUNDARY_NOT_FOUND')

replacement = '''## 17.6 Final mobile mockup contract V2

Binding presentation specification:

`gold_axis_2026/GOLD_CONTROL_MOBILE_UI_PRODUCT_SPEC_V2_FINAL_MOCKUPS.md`

Status: `APPROVED_FINAL_MOCKUP_UI_CONTRACT_V2`.

This V2 contract supersedes V1 for presentation structure. It does **not** change model, source, forecast, decision, threshold, evidence, licensing, or point-in-time semantics.

The latest approved mockup family is now the canonical visual target for `Görünüm`, `Tahmin`, and `Geçmiş/Performans`; `Bugün` / canonical `Piyasa` must be restyled into the same shell.

### Global mobile shell — binding

Every primary screen must use the same product shell:

- compact white institutional header;
- Gold Control logo + `DECISION SYSTEM` subtitle;
- menu affordance on the left;
- notification/profile controls only if implemented, never decorative dead controls;
- page title, short subtitle, and real last-update/freshness timestamp when available;
- white/light cool-neutral page surface;
- deep navy primary hero where the mockup uses one;
- controlled gold brand/selection accent;
- green only for favorable/up/normal state;
- red only for adverse/down/alert state;
- restrained white cards with subtle cool-gray border/shadow;
- four-item bottom navigation: `Bugün | Görünüm | Tahmin | Geçmiş`;
- one consistent navy/gold selected-state treatment across the four tabs.

`Bugün` remains only a user-facing alias for canonical `Piyasa`.

### Görünüm — final mockup hierarchy

The screen order is frozen as:

1. `GÖRÜNÜM` page header + last update;
2. deep navy primary state hero;
3. `1 · SİNYAL ÖZETİ`;
4. `2 · MODEL YÖNÜ (AYLIK)`;
5. `3 · FAST / SLOW TEYİDİ`;
6. `4 · RİSK SEVİYESİ`;
7. `5 · SİNYAL ZAMAN ÇİZELGESİ`;
8. `6 · EMERGENCY DURUMU`;
9. `7 · SİSTEM YORUMU`;
10. explanatory footer note;
11. bottom navigation.

The hero composition is also frozen: primary stored state on the left/center, monthly context on the upper-right, GVZ/risk state on the lower-right, plus a real system-health pill only when supported.

Mockup-to-production substitutions are mandatory:

- `POZİSYONU KORU` slot -> stored descriptive R4 classification;
- `MODEL YÖNÜ` -> stored monthly direction/context;
- `RİSK SEVİYESİ` -> frozen GVZ risk-state translation;
- `SİSTEM AKTİF` -> only a real health state;
- signal timeline -> actual stored decision/model events only;
- system comment -> deterministic explanation generated only from stored state.

The following visible mockup content remains blocked until separately proven: `POZİSYONU KORU`, position/action labels, BUY/SELL/HOLD/EXIT/REDUCE, `Güç %`, and arbitrary confidence labels.

### Tahmin — final mockup hierarchy

The screen order is frozen as:

1. `TAHMİN` page header + last update;
2. deep navy `GELECEK AY TAHMİNİ` hero;
3. `GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI` chart;
4. scenario/module row, only when a canonical scenario contract exists;
5. `MEVCUT FİYATA GÖRE FARK`;
6. `MODEL PERFORMANSI`;
7. methodology / non-advice information note;
8. bottom navigation.

The hero layout is frozen but data-gated:

- left slot = canonical immutable H=1 point forecast from `monthly_forecast_contracts` after issuance;
- right slot = separately stored/frozen monthly direction context;
- target month, evidence class and origin/issued time must remain available in the UI hierarchy.

Before a valid issuance, the hero must show `TAHMİN HENÜZ YAYIMLANMADI` and `NOT_ISSUED_IN_CANONICAL_LEDGER`, never a mockup number.

The mockup's confidence gauge, `Güven %`, lower/base/upper scenario values and forecast band are reserved visual slots only and remain hidden until a calibrated scenario/interval contract is frozen, prospectively validated and immutably stored.

The three-card `Baz / Yukarı / Aşağı` row has current status `BLOCKED_NO_CANONICAL_SCENARIO_CONTRACT`. It may not be populated by inventing scenarios or by relabelling VW/RW references as upside/downside cases.

`MEVCUT FİYATA GÖRE FARK` may compare the current indicative display spot with the issued H=1 point forecast when both are available; this is a comparison, not expected return.

`MODEL PERFORMANSI` must use realized prospective/live forecast rows for production-facing metrics. Historical replay belongs in a separately labelled research surface.

### Geçmiş / Performans — final mockup hierarchy

The bottom-navigation key remains `Geçmiş`; a user-facing `PERFORMANS` page heading is allowed.

The screen order is frozen as:

1. page header + last update;
2. four summary metric cards;
3. large primary history/performance chart;
4. secondary timeline/risk/error chart;
5. selected historical records table/list;
6. evidence/methodology footer;
7. bottom navigation.

The four-card row is visually binding but labels are data-contract dependent. Under the current production contract, preferred production-safe metrics are realized prospective forecast count, prospective MAPE, prospective MAE USD, and prospective direction hit rate only if direction has a frozen definition. Insufficient history renders an empty/not-enough-history state.

The original mockup's YBB strategy return, 12-month strategy return, portfolio maximum drawdown, trade count, entry/exit prices, trade return, `DOĞRU/YANLIŞ` trading outcome, strategy equity curve and buy-and-hold outperformance remain blocked until an audited execution/portfolio contract exists.

The primary chart slot should therefore use actual-vs-issued forecast history or another frozen forecast-performance view until a strategy ledger exists. The secondary drawdown/timeline slot may use forecast error plus actual stored event markers; it must not fabricate portfolio drawdown.

`HISTORICAL_REPLAY`, `PROSPECTIVE_SHADOW`, and `LIVE_PRODUCTION` must remain visibly separate. Replay metrics may not populate prospective summary cards.

### Final mockup interpretation rule

The final mockups are authority for **layout and visual hierarchy**, not for example values.

If a mockup slot lacks an authorized datum, the slot is hidden, empty-stated, or relabelled truthfully. It is never filled with a placeholder number merely to preserve visual balance.

If implementation and the V2 mockup structure disagree, V2 controls presentation. If V2 presentation and canonical data/model/evidence semantics disagree, the canonical semantic contract controls content truth.

Implementation candidate remains `gold_axis_2026/apps/gold_control_mobile_v1.py`, but it must be reconciled to this V2 hierarchy before Stage-10 mobile QA can pass.
'''

text = text[:start] + replacement + text[end:]

old_stage10 = '| 10 | **Mobile QA** | Mobile-first UX validated |'
new_stage10 = '| 10 | **Mobile QA** | Final V2 mockup hierarchy, phone viewport behavior, empty states and semantic gates validated |'
if old_stage10 not in text:
    raise SystemExit('STAGE10_ROW_NOT_FOUND')
text = text.replace(old_stage10, new_stage10, 1)

anchor = 'Dependency rule frozen by manifest v1.10:\n'
if anchor not in text:
    raise SystemExit('ROADMAP_DEPENDENCY_ANCHOR_NOT_FOUND')
addition = '''Dependency rule frozen by manifest v1.10:\n\nFinal-mockup rule added by manifest v1.20:\n\n- Stage 10 is not a generic responsive-design check; it must validate fidelity to `GOLD_CONTROL_MOBILE_UI_PRODUCT_SPEC_V2_FINAL_MOCKUPS.md`.\n- Mockup layout slots may remain hidden/empty when their data contract is unresolved; a visual placeholder never satisfies a stage gate.\n- `Görünüm`, `Tahmin`, and `Geçmiş` implementation must preserve the final V2 section ordering unless a later explicit UI change-control supersedes it.\n'''
text = text.replace(anchor, addition, 1)

if 'APPROVED_FINAL_MOCKUP_UI_CONTRACT_V2' not in text:
    raise SystemExit('FINAL_MOCKUP_STATUS_NOT_WRITTEN')
if 'GOLD_CONTROL_MOBILE_UI_PRODUCT_SPEC_V2_FINAL_MOCKUPS.md' not in text:
    raise SystemExit('FINAL_MOCKUP_SPEC_NOT_WRITTEN')
if '**Manifest version:** 1.20' not in text:
    raise SystemExit('MANIFEST_VERSION_NOT_UPDATED')

MANIFEST.write_text(text, encoding='utf-8')
print('MANIFEST_V1_20_FINAL_MOCKUP_RECONCILE_PASS')
print('FINAL_MOCKUP_UI_STATUS=APPROVED_FINAL_MOCKUP_UI_CONTRACT_V2')
print('MODEL_DATA_SEMANTICS_CHANGED=NO')
