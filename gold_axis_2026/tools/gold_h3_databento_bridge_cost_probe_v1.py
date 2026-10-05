from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / 'gold_axis_2026'
OUTJ = AX / 'GOLD_H3_DATABENTO_BRIDGE_COST_PROBE_2026-10-05.json'
OUTM = AX / 'GOLD_H3_DATABENTO_BRIDGE_COST_PROBE_2026-10-05.md'

DATASET = 'GLBX.MDP3'
SCHEMA = 'ohlcv-1h'
ROOTS = ['GC', 'SI', 'NQ', 'ZN', 'CL']
ROLLS = ['c', 'n', 'v']
SYMBOLS_ALL = [f'{r}.{roll}.0' for r in ROOTS for roll in ROLLS]
BRIDGE_START = '2025-01-02'
BRIDGE_END = '2026-10-03'
HIST_START = '2023-01-01'
HIST_END = '2025-01-01'

def main():
    key = os.environ.get('DATABENTO_API_KEY', '').strip()
    out = {
        'schema': 'GOLD_H3_DATABENTO_BRIDGE_COST_PROBE_V1',
        'date': '2026-10-05',
        'dataset': DATASET,
        'bar_schema': SCHEMA,
        'roots': ROOTS,
        'roll_rules': ROLLS,
        'symbols_all': SYMBOLS_ALL,
        'bridge_window': [BRIDGE_START, BRIDGE_END],
        'historical_window': [HIST_START, HIST_END],
        'data_download_performed': False,
        'model_changed': False,
        'dptc_thresholds_changed': False,
    }

    if not key:
        out['status'] = 'BLOCKED_DATABENTO_API_KEY_MISSING'
        out['next_action'] = 'Add GitHub Actions repository secret DATABENTO_API_KEY and rerun.'
        write(out)
        return

    try:
        import databento as db
    except Exception as e:
        out['status'] = 'BLOCKED_DATABENTO_CLIENT_IMPORT'
        out['error'] = repr(e)
        write(out)
        return

    client = db.Historical(key)

    resolves = {}
    for label, start, end in [
        ('bridge', BRIDGE_START, BRIDGE_END),
        ('historical', HIST_START, HIST_END),
    ]:
        try:
            rr = client.symbology.resolve(
                dataset=DATASET,
                symbols=SYMBOLS_ALL,
                stype_in='continuous',
                stype_out='instrument_id',
                start_date=start,
                end_date=end,
            )
            if hasattr(rr, 'to_dict'):
                payload = rr.to_dict()
            elif hasattr(rr, '__dict__'):
                payload = {k: v for k, v in rr.__dict__.items() if not k.startswith('_')}
            else:
                payload = str(rr)
            resolves[label] = {'ok': True, 'payload': payload}
        except Exception as e:
            resolves[label] = {'ok': False, 'error': repr(e)}
    out['symbology_resolve'] = resolves

    costs = {}
    requests = {
        'bridge_all_15_symbols': dict(
            dataset=DATASET, schema=SCHEMA, symbols=SYMBOLS_ALL,
            stype_in='continuous', start=BRIDGE_START, end=BRIDGE_END
        ),
        'historical_2023_2024_calendar_5': dict(
            dataset=DATASET, schema=SCHEMA, symbols=[f'{r}.c.0' for r in ROOTS],
            stype_in='continuous', start=HIST_START, end=HIST_END
        ),
        'historical_2023_2024_open_interest_5': dict(
            dataset=DATASET, schema=SCHEMA, symbols=[f'{r}.n.0' for r in ROOTS],
            stype_in='continuous', start=HIST_START, end=HIST_END
        ),
        'historical_2023_2024_volume_5': dict(
            dataset=DATASET, schema=SCHEMA, symbols=[f'{r}.v.0' for r in ROOTS],
            stype_in='continuous', start=HIST_START, end=HIST_END
        ),
    }

    for name, kwargs in requests.items():
        try:
            cost = client.metadata.get_cost(**kwargs)
            costs[name] = {'ok': True, 'usd': float(cost), 'request': kwargs}
        except Exception as e:
            costs[name] = {'ok': False, 'error': repr(e), 'request': kwargs}
    out['costs'] = costs

    sym_ok = all(x.get('ok') for x in resolves.values())
    cost_ok = any(x.get('ok') for x in costs.values())
    if sym_ok and cost_ok:
        out['status'] = 'DATABENTO_COST_AND_SYMBOLOGY_PROBE_PASS'
        out['next_action'] = 'Review costs, then run a separate 2025 bridge download if approved.'
    else:
        out['status'] = 'DATABENTO_PROBE_PARTIAL_OR_FAILED'
        out['next_action'] = 'Inspect errors before any paid historical download.'

    write(out)

def write(out):
    OUTJ.write_text(json.dumps(out, indent=2, default=str) + '\n', encoding='utf-8')
    lines = [
        '# GOLD H3 — Databento Bridge Cost Probe — 2026-10-05',
        '',
        f"**Status:** **{out.get('status')}**",
        '',
        '- This probe performs no historical market-data download.',
        '- It does not change LLRS, IFBC, Handoff, DPTC, Q95 or Q99.',
        '- Purpose: verify continuous symbology and estimate cost before spending credits.',
        '',
    ]
    if out.get('status') == 'BLOCKED_DATABENTO_API_KEY_MISSING':
        lines += [
            '## Blocker',
            '',
            'GitHub Actions secret DATABENTO_API_KEY is not present or visible to the workflow.',
            '',
            'Add that repository secret, then rerun this workflow.',
        ]
    else:
        lines += ['## Symbology', '']
        for k, v in (out.get('symbology_resolve') or {}).items():
            lines.append(f"- {k}: **{'PASS' if v.get('ok') else 'FAIL'}**")
            if not v.get('ok'):
                lines.append(f"  - error: {v.get('error')}")
        lines += ['', '## Cost estimates', '', '| Request | Status | Estimated USD |', '|---|---|---:|']
        for k, v in (out.get('costs') or {}).items():
            lines.append(f"| {k} | {'PASS' if v.get('ok') else 'FAIL'} | {v.get('usd','—')} |")
        lines += [
            '',
            '## Next scientific step',
            '',
            'After cost approval, download only the 2025 bridge window for all three roll rules. '
            'Select the roll mapping using source agreement only: timestamp/session, return correlation, '
            'direction agreement, 1h/3h/6h rolling returns and GC/SI volume stability. '
            'Never use DPTC outcome labels to choose the roll rule.',
        ]
    OUTM.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUTM.read_text())

if __name__ == '__main__':
    main()
