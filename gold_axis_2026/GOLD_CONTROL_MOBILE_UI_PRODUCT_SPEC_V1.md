# GOLD CONTROL — MOBILE UI PRODUCT SPEC V1

**Status:** `APPROVED_MOBILE_PRODUCT_UI_CONTRACT_V1`  
**Decision date:** 2026-09-02  
**Canonical branch:** `gold-r4-direction-engine`  
**Parent governance:** `GOLD_CONTROL_PROJECT_MANIFEST.md`  
**Implementation target:** Streamlit mobile-first web app

---

## 1. Purpose

This document freezes the approved mobile product presentation for Gold Control without changing model, data, source, signal, threshold, or evidence semantics.

The approved visual direction is the light institutional mobile design reviewed on 2026-09-02:

- white/light primary surface;
- deep navy institutional hero cards;
- controlled gold brand/selection accent;
- green only for favorable/up/normal state;
- red only for adverse/down/alert state;
- amber only for warning/attention;
- rounded but restrained cards;
- strong hierarchy and large touch targets;
- bottom mobile navigation;
- no dark trading-terminal aesthetic;
- no decorative luxury/glow overload;
- no metric added merely to fill a card.

Mockups are visual references only. Any numeric value, date, confidence score, forecast band, action label, or historical performance shown in a mockup is **not production truth** unless it exists in the canonical data/decision/forecast ledger under the manifest rules.

---

## 2. Canonical navigation and mobile labels

Canonical product semantics remain:

`Piyasa | Görünüm | Tahmin | Geçmiş`

For the mobile bottom bar, the user-facing label **`Bugün`** is approved as an alias for the canonical `Piyasa` screen.

Therefore:

- internal/canonical screen key: `Piyasa`;
- mobile label: `Bugün`;
- other mobile labels: `Görünüm | Tahmin | Geçmiş`.

This alias is presentation-only and does not reopen Stage-5 Piyasa data semantics.

Secondary technical navigation remains:

`Sistem / Veri Sağlığı / Audit`

and must not occupy one of the four primary bottom-navigation slots.

---

## 3. Global header

Every primary mobile screen uses the same compact header:

- Gold Control logo/brand;
- subtitle `DECISION SYSTEM`;
- optional menu icon for secondary navigation;
- refresh/data-state affordance where appropriate;
- no fabricated notification count;
- no user/profile functionality unless actually implemented.

If notification/profile actions are not implemented, they are omitted rather than shown as decorative dead controls.

---

## 4. Screen 1 — Bugün / Piyasa

### Product question

> Piyasa şu anda ne durumda?

### Primary block

Show:

- XAU/USD indicative live price from `XAU_SPOT_GOLDAPI`;
- exact source label and freshness/stale state;
- absolute/percentage change only when defensibly computed from an eligible completed comparison point;
- latest completed operational daily close from `XAU_DAILY_XAUS`, explicitly labelled operational cross-check;
- GVZ latest official close and frozen risk-regime translation;
- XAU operational display-history chart with only supported ranges `1A | 3A | 6A | 1Y`.

### Decision context strip

If a display-eligible Decision Store snapshot exists:

- show stored R4 classification;
- show decision as-of timestamp;
- show evidence class.

If none exists:

- show `KANONİK KARAR YOK`.

Always show the semantic warning:

`Canlı spot ≠ son EOD karar`.

### Forbidden

- derive direction/action from live spot;
- render raw Twelve NY17 vendor value without separately proven display rights;
- call XAUS/Yahoo operational history settlement, official close, or canonical EOD;
- fabricate intraday/long-history selectors not backed by adapters.

---

## 5. Screen 2 — Görünüm

### Product question

> Sistem neden böyle düşünüyor?

### Hero state

The hero card must display the **stored descriptive classification**, not a position instruction.

Allowed examples are only current R4 classification vocabulary:

- `ALIGNED_UP`
- `ALIGNED_DOWN`
- `CONFLICT`
- `UNRESOLVED_MIXED`
- `MACRO_DOWN_RISK`
- `REVERSAL_RISK_DOWN`
- `REVERSAL_RISK_UP`

If no display-eligible Decision Store snapshot exists:

- hero text: `KANONİK KARAR YOK`;
- explanation: current state cannot be reconstructed from live spot.

### Layer cards

When the stored snapshot exists, disclose:

1. Monthly context;
2. Fast;
3. Slow;
4. BOCPD regime/break;
5. Emergency state;
6. GVZ/risk state.

The visual structure may follow the approved mockup, but values must come only from stored state.

### Plain-language explanation

A short explanation may be generated deterministically from stored states, for example:

`Aylık yön ve Fast/Slow aynı yönde; rejim kırılması ve Emergency sinyali yok; GVZ risk katmanı normal.`

It must not invent causal factors not present in the stored snapshot.

### Explicitly prohibited mockup elements

Until separate change-control closes `NOT_PROVEN_POSITION_MAPPING`, do **not** display:

- `POZİSYONU KORU`;
- BUY / SELL / HOLD / EXIT / REDUCE;
- exposure percentage;
- `Güç: %68` or any arbitrary strength percentage;
- `Güven: orta-yüksek`, `yüksek`, etc.;
- investment-action language.

The approved visual composition is retained, but these labels are replaced by real stored classification/state fields.

---

## 6. Screen 3 — Tahmin

### Product question

> Gelecek ay için model ne bekliyor?

### Before first eligible issuance

While `monthly_forecast_contracts` contains no canonical issued H=1 row:

- do not show a forecast number;
- do not show a forecast band;
- do not show confidence/strength;
- hero state: `TAHMİN HENÜZ YAYIMLANMADI`;
- technical status: `NOT_ISSUED_IN_CANONICAL_LEDGER`;
- show earliest valid process note only if current contract permits it.

For the current 2026-09-02 state, the first possible target remains October 2026 at the end-September origin; no September backfill is allowed.

### After a canonical issuance

Primary hero may show:

- target month;
- issued Patch point forecast from `monthly_forecast_contracts`;
- evidence badge: initially `PROSPECTIVE_SHADOW`;
- forecast origin / issued-at timestamp;
- directional context if present as a separately frozen/stored context.

Secondary comparisons may show only if they are actually stored/available for the same origin and target:

- audited VW shadow/reference;
- RW benchmark;
- current indicative spot comparison.

If a reference is absent, render `KULLANILAMIYOR / NOT_ISSUED` rather than inventing a number.

### Provenance disclosure

Model/version, Git SHA, snapshot IDs and detailed source/geometry data belong in an expandable `Model bilgisi / Audit` area, not the primary hero.

### Forecast chart

Allowed:

- historical actual monthly averages with explicit source/evidence labeling;
- prospectively issued forecast points after they exist;
- forecast-vs-actual comparison after outcomes exist.

Not allowed until separately validated:

- min/max prediction band;
- arbitrary upper/base/lower scenarios;
- confidence score;
- scenario probabilities.

The mockup's decorative forecast band is therefore **not part of Production UI V1**.

---

## 7. Screen 4 — Geçmiş

### Product question

> Sistem geçmişte gerçekten ne yaptı?

### Default tab/section: Forecast history

When prospective forecast records exist, show:

- target month;
- issued forecast;
- actual after realization;
- APE/error after realization;
- evidence class;
- model version;
- origin/issued timestamp;
- status such as `BEKLİYOR`, `GERÇEKLEŞTİ`.

Top summary metrics may be computed **only over realized prospective/live rows**:

- MAPE;
- MAE (USD);
- directional accuracy only if direction is explicitly defined and stored;
- count of realized forecasts.

Before enough prospective rows exist, show the empty-state explanation instead of historical replay as if it were live performance.

### Secondary section: Decision history

Show actual stored decision events only:

- timestamp;
- descriptive R4 classification;
- stored signal context;
- reason/evidence code.

### Historical replay

Historical replay may appear only in a clearly separated expandable research block labelled `HISTORICAL_REPLAY`.

### Explicitly prohibited from the approved older mockup

Until position/action mapping and an actual portfolio execution contract exist, do not display as production metrics:

- YBB strategy return;
- 12-month strategy return;
- drawdown of a simulated portfolio;
- trade count;
- profitable/unprofitable trade labels;
- entry/exit prices;
- `DOĞRU/YANLIŞ` trade outcomes;
- buy-and-hold outperformance claims.

These are not currently supported by the canonical production state contract.

---

## 8. Technical/Audit screen

Secondary route only.

May display:

- source health;
- source freshness;
- latest retrieval run status;
- Decision Store state/evidence class;
- latest forecast contract ID;
- forecast input snapshot count/IDs;
- model version;
- Git SHA;
- R4 config version;
- blockers;
- historical replay evidence metrics with explicit label.

Raw licensed vendor values remain subject to display rights.

---

## 9. Evidence badges

User-facing badges must map directly to stored evidence class:

- `HISTORICAL REPLAY` — neutral/amber research label;
- `PROSPECTIVE SHADOW` — blue/gold shadow label;
- `LIVE PRODUCTION` — green production label only after graduation gates pass.

A historical replay result may never receive a prospective/live badge.

---

## 10. Empty-state behavior is a product feature

The UI must remain visually complete even when a canonical datum does not yet exist.

Examples:

- no Decision Store current state → `KANONİK KARAR YOK`;
- no H=1 forecast row → `TAHMİN HENÜZ YAYIMLANMADI`;
- no prospective history → `İLERİYE DÖNÜK PERFORMANS HENÜZ OLUŞMADI`;
- unavailable source → source-specific `VERİ KULLANILAMIYOR` with freshness/error context.

No placeholder numeric value is permitted to make the screen look finished.

---

## 11. Mobile layout rules

Target width: phone-first, approximately 360–430 CSS px.

Rules:

- one-column hero and primary content on phones;
- two-column cards may be used only when readable at 360 px;
- minimum practical touch target ~44 px;
- bottom navigation fixed/sticky where Streamlit implementation permits without accessibility regression;
- desktop may widen cards but must preserve the same information hierarchy;
- no horizontal-scroll dependency for core content;
- dense tables must collapse to selected rows/cards on mobile or use a controlled scroll container;
- primary numbers must remain readable without zoom.

---

## 12. Implementation sequence

1. Freeze this UI product contract and reconcile manifest.
2. Add deterministic UI presentation-state helpers/tests.
3. Add forecast-ledger read path; it must return no value when ledger is empty.
4. Restyle the existing Stage-5 Piyasa implementation without changing its source semantics.
5. Implement compliant Görünüm hero/layer cards from Decision Store.
6. Implement Tahmin empty state first, then canonical forecast hero once an issued row exists.
7. Implement Geçmiş from prospective forecast/decision ledgers; keep replay separately labelled.
8. Add mobile viewport/runtime smoke tests.
9. Perform Stage-10 mobile QA before declaring UI complete.

---

## 13. Release blockers

A UI release is blocked if any of the following occur:

- mockup placeholder is rendered as real data;
- position/action mapping is inferred from descriptive classification;
- confidence/strength/band is shown without frozen definition;
- replay is presented as prospective/live;
- provider identity is hidden or silently substituted;
- raw vendor data is displayed without rights;
- Tahmin shows a value not backed by canonical `monthly_forecast_contracts`;
- Görünüm creates a current decision when Decision Store has no display-eligible row.

---

## 14. Approved design reference interpretation

The mobile designs approved by the user on 2026-09-02 are accepted for:

- visual hierarchy;
- card structure;
- navy/gold/white palette;
- mobile spacing;
- hero treatment;
- bottom navigation concept;
- chart/card placement concept.

They are **not accepted as authority for the example numbers or prohibited labels inside those drawings**. Manifest/data/ledger semantics always override mockup sample content.
