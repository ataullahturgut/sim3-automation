from __future__ import annotations

import json
import math
import os
from pathlib import Path

import pandas as pd

import emergency_reversal_volnorm_successor_v1 as v1

YEARS = (2022, 2023, 2024)
HOURS = (13, 14, 15, 16)


def calendar_weekdays(year: int) -> int:
    return int(sum(d.dayofweek < 5 for d in pd.date_range(f'{year}-01-01', f'{year}-12-31', freq='D')))


def main() -> None:
    key = os.environ.get('TWELVE_DATA_API_KEY', '').strip()
    if not key:
        raise RuntimeError('AUTHENTICATION_ERROR:TWELVE_DATA_API_KEY_NOT_SET')
    selected = {h: {} for h in HOURS}
    excluded_weekend = {h: 0 for h in HOURS}
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
                if ts.dayofweek >= 5:
                    excluded_weekend[ts.hour] += 1
                    continue
                day = ts.normalize()
                if day in selected[ts.hour]:
                    raise RuntimeError(f'DUPLICATE_WEEKDAY_BAR:{text}')
                selected[ts.hour][day] = value

    result = {'years': list(YEARS), 'hours': {}}
    ref = pd.Series(selected[16], dtype=float).sort_index()
    for h in HOURS:
        s = pd.Series(selected[h], dtype=float).sort_index()
        coverage = {}
        for year in YEARS:
            n = int((s.index.year == year).sum())
            denom = calendar_weekdays(year)
            coverage[str(year)] = {'selected_weekdays': n, 'calendar_weekdays': denom, 'ratio': n / denom}
        joined = pd.concat([ref.rename('ref16'), s.rename('candidate')], axis=1, join='inner').dropna()
        if len(joined):
            gaps = (joined['candidate'] / joined['ref16'] - 1.0).abs() * 10000.0
            level_corr = float(joined['candidate'].corr(joined['ref16']))
            med_bps = float(gaps.median())
            p95_bps = float(gaps.quantile(0.95))
        else:
            level_corr = med_bps = p95_bps = None
        result['hours'][str(h)] = {
            'coverage': coverage,
            'weekend_bars_excluded': int(excluded_weekend[h]),
            'overlap_with_weekday_16': int(len(joined)),
            'level_corr_with_weekday_16': level_corr,
            'median_abs_level_gap_bps': med_bps,
            'p95_abs_level_gap_bps': p95_bps,
        }

    out = Path('/tmp/emergency-reversal-pre2025-weekday-source-probe')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'probe.json').write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
