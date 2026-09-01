from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'GOLD_CONTROL_PROJECT_MANIFEST.md'
STATUS = ROOT / 'GOLD_CONTROL_STAGE4_STATUS_2026-09-01.md'


def one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'{label}: expected 1 match, got {n}')
    return text.replace(old, new, 1)

m = MANIFEST.read_text(encoding='utf-8')
m = one(m, '**Manifest version:** 1.10', '**Manifest version:** 1.11', 'version')
m = one(
    m,
    '| 5 | `IN_PROGRESS_LIVE_SOURCE_PROVEN_NOT_UI_COMPLETE` | `XAU_SPOT_GOLDAPI` live-display probe SUCCESS; adapter/UI integration and full history/freshness QA remain |',
    '| 5 | `IN_PROGRESS_DATA_PATHS_PROVEN_UI_CONTRACT_NOT_COMPLETE` | Gold API live adapter smoke `SUCCESS` (run `33519370028`); XAUS 1-year history adapter smoke `SUCCESS` (run `33519506662`); canonical Piyasa UI/information-architecture implementation remains |',
    'stage5 status',
)
m = one(
    m,
    '## `STAGE 5 — PIYASA LIVE MONITORING: ACTIVATE THE PROVEN DISPLAY SOURCE WITHOUT CHANGING DECISION LOGIC`',
    '## `STAGE 5 — PIYASA UI CONTRACT: BIND PROVEN LIVE/HISTORY DATA TO THE CANONICAL PIYASA SCREEN`',
    'immediate stage5 task',
)
m = one(
    m,
    '**Piyasa / monitoring lane (may proceed now):**\n\n1. activate `XAU_SPOT_GOLDAPI` in the transitional live adapter with explicit source/freshness metadata;\n2. smoke-test the adapter without logging raw market values;\n3. keep `XAU_SPOT_XAUS` as a distinct secondary/degraded lineage; never silently merge providers;\n4. keep `Canlı spot ≠ son EOD karar` visible and show `KANONİK KARAR YOK` whenever the Decision Store has no display-eligible forward state;\n5. complete the real-history/freshness UI contract before Stage 5 is marked PASS.',
    '**Piyasa / monitoring lane (current):**\n\n1. `XAU_SPOT_GOLDAPI` canonical live adapter activation/smoke is `PASS` by run `33519370028`, job `99894418747`; raw market value was not logged and no forecast/decision/DB write occurred.\n2. Current XAUS 1-year history adapter smoke is `PASS` by run `33519506662`, job `99894890585`; >=200 rows, >=300-day span, latest observation age <=7 days, no duplicate dates/null closes, no DB write.\n3. Keep Gold API live spot, XAUS display history, and Twelve NY17 canonical EOD as visibly separate provider/semantic lineages.\n4. Implement the canonical `Piyasa` screen using only proven data paths: live price + source/freshness, 1-year history/timeframe views supported by the adapter, GVZ latest/history, and the Decision Store strip.\n5. Keep `Canlı spot ≠ son EOD karar` visible and show `KANONİK KARAR YOK` whenever the Decision Store has no display-eligible forward state.\n6. Stage 5 is not PASS until UI-level source/freshness/error-state/mobile smoke is complete.',
    'piyasa lane gates',
)
marker = 'Change-control record: `gold_axis_2026/GOLD_CONTROL_LIVE_MARKET_ROADMAP_CHANGE_CONTROL_2026-09-01.md`.\n'
evidence = marker + '\nStage-5 runtime evidence added in manifest v1.11:\n\n- canonical live adapter smoke: run `33519370028`, job `99894418747`, `SUCCESS`; source series `XAU_SPOT_GOLDAPI`, freshness PASS, role `INDICATIVE_DISPLAY_ONLY_NO_MODEL_USE`, no raw-value logging or writes;\n- current 1-year XAU history adapter smoke: run `33519506662`, job `99894890585`, `SUCCESS`; row/span/freshness/duplicate/null gates PASS, no raw-value logging or writes.\n'
m = one(m, marker, evidence, 'stage5 runtime evidence')
MANIFEST.write_text(m, encoding='utf-8')

s = STATUS.read_text(encoding='utf-8')
s = one(s, '**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.10', '**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.11', 'status manifest version')
s = one(
    s,
    '1. activate `XAU_SPOT_GOLDAPI` in the transitional live adapter and run a no-raw-value app/source smoke;\n2. continue Stage-4B VW/H=1 issuer change-control in parallel;\n3. do not mark `Görünüm` complete until a display-eligible stored forward decision exists;\n4. do not mark `Tahmin` complete until a canonical issued H=1 forecast exists;\n5. first complete forward Decision Store state remains `PROSPECTIVE_SHADOW`; `LIVE_PRODUCTION` stays disabled and `action_state` stays NULL under `NOT_PROVEN_POSITION_MAPPING`.',
    '1. Gold API live adapter activation/smoke is complete: run `33519370028`, job `99894418747`, `SUCCESS`.\n2. Current XAUS 1-year history adapter smoke is complete: run `33519506662`, job `99894890585`, `SUCCESS`.\n3. Implement and smoke the canonical `Piyasa` UI contract using only these proven monitoring paths plus Cboe GVZ and the evidence-isolated Decision Store strip.\n4. Continue Stage-4B VW/H=1 issuer change-control in parallel; do not infer a forecast/decision from the live UI path.\n5. Do not mark `Görünüm` complete until a display-eligible stored forward decision exists, and do not mark `Tahmin` complete until a canonical issued H=1 forecast exists.\n6. First complete forward Decision Store state remains `PROSPECTIVE_SHADOW`; `LIVE_PRODUCTION` stays disabled and `action_state` stays NULL under `NOT_PROVEN_POSITION_MAPPING`.',
    'status immediate next work',
)
STATUS.write_text(s, encoding='utf-8')
print('MANIFEST_V1_11_STAGE5_EVIDENCE_APPLY_PASS')
