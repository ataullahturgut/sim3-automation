from __future__ import annotations

import base64, gzip, io, math, re
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
WB_URL='https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx'


def load_core():
    b64=(ROOT/'core5_monthly.csv.gz.b64').read_text().strip()
    raw=gzip.decompress(base64.b64decode(b64)).decode()
    return pd.read_csv(io.StringIO(raw),parse_dates=['date']).set_index('date').sort_index()


def load_wb():
    r=requests.get(WB_URL,headers={'User-Agent':'Gold-Control-Target-Identity/1.0'},timeout=120)
    r.raise_for_status()
    raw=pd.read_excel(io.BytesIO(r.content),sheet_name='Monthly Prices',header=None)
    gold_col=None
    for rr in range(min(12,len(raw))):
        for cc in range(raw.shape[1]):
            v=str(raw.iat[rr,cc]).strip().lower()
            if v=='gold' or v.startswith('gold '):
                gold_col=cc; break
        if gold_col is not None: break
    if gold_col is None: raise RuntimeError('WORLD_BANK_GOLD_COLUMN_NOT_FOUND')
    rows=[]
    for _,row in raw.iterrows():
        m=re.match(r'^(\d{4})M(\d{1,2})$',str(row.iloc[0]).strip(),re.I)
        if not m: continue
        val=pd.to_numeric(row.iloc[gold_col],errors='coerce')
        if pd.notna(val): rows.append((pd.Timestamp(int(m.group(1)),int(m.group(2)),1),float(val)))
    return pd.Series(dict(rows)).sort_index()


def main():
    core=load_core(); wb=load_wb()
    if 'gold_monthly' not in core.columns: raise RuntimeError('CORE_GOLD_MONTHLY_NOT_FOUND')
    window=pd.date_range('2016-01-01','2026-07-01',freq='MS')
    rows=[]
    for m in window:
        a=float(core.loc[m,'gold_monthly']) if m in core.index and pd.notna(core.loc[m,'gold_monthly']) else math.nan
        b=float(wb.loc[m]) if m in wb.index and pd.notna(wb.loc[m]) else math.nan
        if math.isfinite(a) and math.isfinite(b): rows.append((m,a,b,abs(a-b)))
    d=np.array([r[3] for r in rows],float)
    aa=np.array([r[1] for r in rows],float); bb=np.array([r[2] for r in rows],float)
    print(f'WINDOW_EXPECTED_MONTHS={len(window)}')
    print(f'COMMON_MONTHS={len(rows)}')
    print(f'EXACT_EQUAL_COUNT={int(np.sum(aa==bb))}/{len(rows)}')
    print(f'WITHIN_0_01_COUNT={int(np.sum(d<=0.01))}/{len(rows)}')
    print(f'WITHIN_0_50_COUNT={int(np.sum(d<=0.50))}/{len(rows)}')
    print(f'MAX_ABS_DIFF_USD={float(d.max()) if len(d) else math.nan:.12f}')
    print(f'MEDIAN_ABS_DIFF_USD={float(np.median(d)) if len(d) else math.nan:.12f}')
    print(f'LEVEL_CORR={float(np.corrcoef(aa,bb)[0,1]) if len(rows)>1 else math.nan:.12f}')
    rel=np.abs(aa-bb)/np.abs(bb)*10000
    print(f'MEDIAN_ABS_DIFF_BPS={float(np.median(rel)):.9f}')
    print(f'P95_ABS_DIFF_BPS={float(np.quantile(rel,0.95)):.9f}')
    print('TARGET_VALUES_LOGGED=NO')
    print('DATABASE_WRITES=NONE')
    print('MODEL_SCORE_RUN=NONE')
    print('CORE5_WORLDBANK_TARGET_IDENTITY_AUDIT_COMPLETE')

if __name__=='__main__': main()
