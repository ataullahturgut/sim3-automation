from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import emergency_reversal_volnorm_successor_v1 as v1

YEARS = (2022, 2023, 2024)
HOURS = (13, 14, 15, 16)


def main() -> None:
    key = __import__('os').environ.get('TWELVE_DATA_API_KEY', '').strip()
    if not key:
        raise RuntimeError('AUTHENTICATION_ERROR:TWELVE_DATA_API_KEY_NOT_SET')
    selected = {h: {} for h in HOURS}
    for year in YEARS:
        for start, end in v1._half_year_segments(year):
            payload = v1._request({
                'symbol': 'XAU/USD', 'interval': '1h', 'start_date': start, 'end_date': end,
                'timezone': 'America/New_York', 'outputsize': 5000, 'order': 'ASC', 'format': 'JSON'
            }, key)
            for item in payload.get('values') or []:
                text = str(item.get('datetime') or '')
                if len(text) < 19:
                    continue
                ts = pd.Timestamp(text)
                if ts.year != year or ts.hour not in HOURS or ts.minute != 0 or ts.second != 0:
                    continue
                value = float(item['close'])
                if not math.isfinite(value) or value <= 0:
                    continue
                selected[ts.hour][ts.normalize()] = value

    result = {'years': list(YEARS), 'hours': {}}
    ref = pd.Series(selected[16], dtype=float).sort_index()
    for h in HOURS:
        s = pd.Series(selected[h], dtype=float).sort_index()
        cov = v1.coverage_by_year(s, YEARS)
        joined = pd.concat([ref.rename('ref16'), s.rename('candidate')], axis=1, join='inner').dropna()
        if len(joined):
            rel_bps = (joined['candidate'] / joined['ref16'] - 1.0).abs() * 10000.0
            level_corr = float(joined['candidate'].corr(joined['ref16']))
            med_bps = float(rel_bps.median())
            p95_bps = float(rel_bps.quantile(0.95))
        else:
            level_corr = med_bps = p95_bps = None
        result['hours'][str(h)] = {
            'coverage': cov,
            'overlap_with_16': int(len(joined)),
            'level_corr_with_16': level_corr,
            'median_abs_level_gap_bps': med_bps,
            'p95_abs_level_gap_bps': p95_bps,
        }
    Path('/tmp/emergency-reversal-pre2025-source-probe').mkdir(parents=True, exist_ok=True)
    Path('/tmp/emergency-reversal-pre2025-source-probe/probe.json').write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
