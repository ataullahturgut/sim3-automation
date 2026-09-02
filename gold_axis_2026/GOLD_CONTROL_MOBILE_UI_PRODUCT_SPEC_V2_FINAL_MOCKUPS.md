# GOLD CONTROL — MOBILE UI PRODUCT SPEC V2 / FINAL MOCKUPS

**Status:** `APPROVED_FINAL_MOCKUP_UI_CONTRACT_V2`  
**Decision date:** 2026-09-02  
**Canonical branch:** `gold-r4-direction-engine`  
**Parent governance:** `GOLD_CONTROL_PROJECT_MANIFEST.md`  
**Supersedes for presentation:** `GOLD_CONTROL_MOBILE_UI_PRODUCT_SPEC_V1.md`  
**Model/data semantics changed:** `NO`

---

## 1. Authority and interpretation

This document freezes the latest approved Gold Control mockup family as the canonical presentation target for the primary mobile product screens.

The final mockups define:

- visual hierarchy;
- section ordering;
- hero-card composition;
- card grouping;
- chart placement;
- four-item bottom navigation;
- white / navy / gold institutional visual language;
- green / red semantic state treatment;
- mobile spacing and information density.

They do **not** make their sample numbers, sample dates, sample trade results, sample action labels, sample confidence values, sample forecast ranges, or sample backtest returns production truth.

Production truth continues to come only from the canonical market, forecast and decision stores under the manifest.

---

## 2. Global shell frozen from the final mockups

Primary screens share the same product shell:

1. compact white header;
2. Gold Control logo and `DECISION SYSTEM` subtitle;
3. menu affordance on the left;
4. right-side notification/profile affordances only when those features actually exist;
5. page title and short explanatory subtitle;
6. last-update / freshness area when backed by a real timestamp;
7. soft white content surface with restrained shadow/border cards;
8. deep navy hero card for the primary state/forecast;
9. navy section headings and numbered navy section badges where the mockup uses them;
10. fixed/sticky four-item bottom navigation where runtime permits.

Canonical bottom navigation:

`Bugün | Görünüm | Tahmin | Geçmiş`

`Bugün` remains the user-facing alias of canonical `Piyasa`.

The final implementation must use one consistent selected-state treatment across all four tabs. The visual language is navy + gold; mockup-specific inconsistent active-tab variants are not separate product states.

---

## 3. Screen — Görünüm

### 3.1 Page order

The final Görünüm screen follows this order:

1. page header — `GÖRÜNÜM` + explanatory subtitle + last update;
2. deep navy primary decision hero;
3. `1 · SİNYAL ÖZETİ`;
4. `2 · MODEL YÖNÜ (AYLIK)`;
5. `3 · FAST / SLOW TEYİDİ`;
6. `4 · RİSK SEVİYESİ`;
7. `5 · SİNYAL ZAMAN ÇİZELGESİ`;
8. `6 · EMERGENCY DURUMU`;
9. `7 · SİSTEM YORUMU`;
10. explanatory footer note;
11. bottom navigation.

### 3.2 Primary hero

The hero composition from the mockup is frozen:

- large left-side state icon / shield-style visual treatment;
- primary stored state in the center-left;
- monthly model/direction context in the right-side upper area;
- risk state in the right-side lower area;
- optional real system-health/status pill.

Production content substitution is mandatory:

- mockup `POZİSYONU KORU` slot -> **stored descriptive R4 classification**;
- mockup `MODEL YÖNÜ` slot -> stored monthly direction/context;
- mockup `RİSK SEVİYESİ` slot -> frozen GVZ risk-state translation;
- mockup `SİSTEM AKTİF` pill -> only a real health state, never decorative.

### 3.3 Signal summary card

The three-row visual composition is retained, but rows must come from stored state.

Allowed content examples:

- final descriptive classification;
- monthly direction/context;
- evidence / quality state.

The card must not fabricate a position instruction or a confidence label.

### 3.4 Monthly model-direction card

Show:

- stored monthly direction/context;
- model/reference identity in secondary text where useful;
- evidence badge if applicable.

The mockup percentage-strength bar is hidden unless a separately frozen, validated strength metric exists.

### 3.5 Fast / Slow confirmation card

Show the two stored tactical states side by side.

Allowed plain-language summary:

- `UYUMLU` only when the deterministic stored Fast and Slow states satisfy a frozen alignment rule;
- otherwise a neutral/conflict wording derived deterministically from stored states.

No exposure or trade instruction is inferred.

### 3.6 Risk card

Show:

- GVZ latest eligible value if displayable;
- frozen user-facing risk regime;
- low / medium / high style scale only if its band mapping is read from the frozen config.

GVZ never generates gold direction.

### 3.7 Signal timeline

The final mockup timeline placement is approved, but only actual stored events may appear.

Allowed markers:

- stored descriptive decision/classification change;
- actual model/engine update event;
- neutral/unresolved event where actually persisted.

Prohibited:

- invented signal dates;
- synthetic BUY/SELL arrows;
- fabricated entry/exit events.

The underlying price series must use a display-authorized lineage.

### 3.8 Emergency card

Show stored Level/Reversal Emergency state.

`NORMAL` may be displayed only when the stored/frozen Emergency layer really indicates no active emergency condition.

### 3.9 System interpretation card

The final mockup quote/comment card is approved.

Text must be generated deterministically from the stored signal vector. It may summarize monthly context, Fast/Slow, regime, Emergency and GVZ state. It must not introduce unstored causal claims, confidence, or investment advice.

### 3.10 Currently blocked mockup content

Until separately proven, the following remain hidden/replaced even though they are visible in the drawing:

- `POZİSYONU KORU`;
- `Pozisyon` action labels;
- BUY / SELL / HOLD / EXIT / REDUCE;
- `Güç: %68` or any arbitrary strength percentage;
- `Güven Seviyesi: Orta–Yüksek` or similar arbitrary confidence labels.

---

## 4. Screen — Tahmin

### 4.1 Page order

The final Tahmin screen follows this order:

1. page header — `TAHMİN` + explanatory subtitle + last update;
2. deep navy `GELECEK AY TAHMİNİ` hero;
3. `GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI` chart;
4. scenario/module row only when a scenario contract exists;
5. `MEVCUT FİYATA GÖRE FARK` module;
6. `MODEL PERFORMANSI` module;
7. methodology / non-advice information note;
8. bottom navigation.

### 4.2 Forecast hero

The mockup hero composition is frozen:

- left: next-month average price forecast;
- right: expected direction/context;
- lower band: supporting forecast metadata/modules.

After a canonical issuance, the left value is the immutable H=1 point forecast from `monthly_forecast_contracts`.

The hero must also show:

- target month;
- evidence class;
- issued/origin timestamp in secondary disclosure.

Before issuance, the hero renders:

`TAHMİN HENÜZ YAYIMLANMADI`

and

`NOT_ISSUED_IN_CANONICAL_LEDGER`.

### 4.3 Expected direction

The right-side direction slot may show a separately stored/frozen monthly direction context. It must not be reverse-engineered from the forecast number or live spot.

### 4.4 Confidence and forecast-range slots

The final mockup visually contains confidence and lower/base/upper range elements. These slots are **reserved but gated**.

They remain hidden until all of the following exist under separate change control:

- calibrated interval/scenario definition;
- prospective validation;
- immutable stored output;
- explicit display contract.

Therefore V2 does not authorize:

- `GÜVEN DÜZEYİ YÜKSEK`;
- `Güven %68`;
- lower/base/upper prices;
- scenario probabilities;
- forecast-band shading as a model interval.

### 4.5 Historical + forecast comparison chart

The final chart placement and visual concept are approved.

Allowed plotted objects:

- historical actual XAU monthly outcome series under explicit source/evidence semantics;
- prospectively issued point forecasts;
- actual-vs-issued comparison after outcome realization.

A future continuous forecast curve or interval fan may not be fabricated from a single H=1 point.

Time-range selectors may be exposed only for ranges genuinely supported by the connected data.

### 4.6 Scenario cards

The visual three-card row (`Baz / Yukarı / Aşağı`) is a reserved module.

Current status: `BLOCKED_NO_CANONICAL_SCENARIO_CONTRACT`.

Until a scenario contract exists, the application either hides this row or replaces it with available reference-comparison cards that are clearly named and semantically correct. It must not label VW/RW as upside/downside scenarios unless that meaning is separately frozen.

### 4.7 Current-price difference module

When both values exist, show the arithmetic and percentage difference between:

- current indicative display spot; and
- the canonical issued H=1 point forecast.

Source/evidence semantics remain explicit. This is a comparison, not expected return.

### 4.8 Model-performance module

The mockup placement is approved, but displayed metrics must be evidence-safe.

Production-facing metrics may be computed only from realized prospective/live forecast rows, e.g.:

- realized forecast count;
- MAPE;
- MAE USD;
- direction hit rate only if a frozen direction definition exists.

Historical replay model metrics, if shown, must be in a visibly separate `HISTORICAL_REPLAY` research block.

---

## 5. Screen — Geçmiş / Performans

The bottom-navigation key remains `Geçmiş`. The page may use a user-facing `PERFORMANS` heading as in the final mockup only if evidence classes remain explicit.

### 5.1 Page order

The final Geçmiş/Performans screen follows this order:

1. page header + last update;
2. four summary metric cards;
3. large primary cumulative/history chart;
4. second timeline/risk/error chart;
5. selected historical records table/list;
6. methodology/evidence footer;
7. bottom navigation.

### 5.2 Four summary cards

The four-card visual row is frozen; the **labels are data-contract dependent**.

Current production-safe preferred fields are:

1. realized prospective forecast count;
2. prospective MAPE;
3. prospective MAE (USD);
4. prospective direction hit rate, only if direction is formally defined.

If the dataset is insufficient, the card renders an empty/not-enough-history state rather than a mockup number.

The original drawing's YBB return, maximum drawdown and 12-month strategy return are not authorized until an execution/portfolio contract exists.

### 5.3 Primary history chart

The chart occupies the same primary visual slot as the mockup.

Current canonical content preference:

- forecast actual vs issued history; or
- cumulative forecast-error/accuracy view with a frozen definition.

A strategy-equity curve and buy-and-hold comparison are blocked until a real execution/portfolio contract is approved.

### 5.4 Secondary timeline chart

The mockup's drawdown + decision-event composition is visually approved as a reserved module.

Current allowed implementation may instead show:

- absolute forecast error through time;
- actual stored decision-event markers;
- model/forecast issuance markers.

Portfolio drawdown is disabled until a portfolio ledger exists.

### 5.5 Historical records table

The table/list placement is approved.

Allowed columns/cards are drawn from actual ledgers, e.g.:

- date / target month;
- evidence class;
- issued forecast;
- actual after realization;
- APE/error;
- model version;
- descriptive stored decision classification/reason where relevant.

Prohibited without an execution contract:

- entry price;
- exit price;
- trade return;
- profitable/unprofitable trade classification;
- fabricated `DOĞRU / YANLIŞ` trading outcome.

### 5.6 Evidence segregation

`HISTORICAL_REPLAY`, `PROSPECTIVE_SHADOW`, and `LIVE_PRODUCTION` must remain visibly separate. A replay scorecard may not populate the prospective summary cards.

---

## 6. Screen — Bugün / Piyasa

The existing Stage-5 Piyasa data contract remains unchanged.

The screen must be restyled into the same final product shell:

- common header;
- light institutional surface;
- deep navy primary market hero;
- restrained cards;
- final four-item bottom navigation;
- matching spacing/typography.

Data semantics remain:

- Gold API = indicative live display;
- XAUS operational history = labelled cross-check;
- Twelve NY17 = internal canonical EOD decision reference, not raw public display unless rights are proven;
- GVZ = risk layer, not direction.

---

## 7. Visual design tokens frozen at product level

The implementation must stay within this visual system:

- base background: white / very light cool neutral;
- primary ink/navy: deep institutional navy;
- brand accent: controlled warm gold;
- favorable state: green;
- adverse/alert state: red;
- warning/attention: amber/gold;
- cards: white, restrained radius, subtle cool-gray border/shadow;
- hero: deep navy gradient/solid treatment with gold/white primary text;
- section labels: uppercase or strong navy hierarchy consistent with the mockups;
- numeric hierarchy: large hero numbers, medium summary metrics, small muted metadata;
- no neon glow, casino/trading-terminal styling, excessive gradients, or decorative cards without data purpose.

---

## 8. Empty-state visual contract

The screen skeleton must remain visually complete without false data.

Approved empty states:

- Decision Store empty -> `KANONİK KARAR YOK`;
- Forecast ledger empty -> `TAHMİN HENÜZ YAYIMLANMADI`;
- Prospective performance insufficient -> `İLERİYE DÖNÜK PERFORMANS HENÜZ OLUŞMADI`;
- Source unavailable -> `VERİ KULLANILAMIYOR` plus source/freshness context;
- Scenario contract absent -> scenario row hidden / `SENARYO MODÜLÜ HENÜZ YETKİLENDİRİLMEDİ` in technical disclosure.

No sample/mockup number may be used as a fallback.

---

## 9. Binding implementation rule

When implementation and mockup visual structure disagree, this V2 contract controls presentation.

When V2 visual structure and canonical data/model/evidence semantics disagree, the canonical manifest/data contract controls **content truth**, while the V2 layout slot remains empty, hidden, or relabelled correctly.

This is the required interpretation of the final mockups.