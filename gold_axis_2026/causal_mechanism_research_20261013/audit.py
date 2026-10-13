#!/usr/bin/env python3
"""Read-only audit of pinned research inputs; writes only this new research folder.
Python 3.9+, standard library. No fitting, news scoring, trading or database writes.
Run from a checkout containing the three unmerged review commits (see README.md).
The original vendor bars are NOT audited by this program.
"""
import csv
import hashlib
import io
import json
import math
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE = '4ecdf810e4e76fba37d20b4a94d30d0bc54b30a3'
PR118 = '1893fcdfeb91ca3e20165fa5f044ccf42dcefec3'
PR119 = 'e1ead36ec670368dc6688f13179cf97cc6b05a25'
PR120 = '2e4f11348470ca99b43ba13c477dffc9a247bcc1'
PREFIX = 'gold_axis_2026/'
inventory = []

def read(sha, name):
    raw = subprocess.check_output(['git', 'show', sha + ':' + PREFIX + name], cwd=REPO)
    inventory.append(dict(commit=sha, path=PREFIX+name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
    return raw.decode('utf-8-sig')

def rows(sha, name):
    return list(csv.DictReader(io.StringIO(read(sha, name))))

def number(x):
    return float(x) if x else float('nan')

def auc(r):
    d = [number(x['r20']) for x in r if x['first'] == 'DOWN']
    u = [number(x['r20']) for x in r if x['first'] == 'UP']
    return sum((a > b) + 0.5*(a == b) for a in d for b in u)/(len(d)*len(u)) if d and u else None

def save(name, obj):
    (HERE/name).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False)+'\n')

def csvsave(name, data):
    with (HERE/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]), lineterminator='\n'); w.writeheader(); w.writerows(data)

# Inventory every event-chain / multihorizon research report, CSV, code and SQL
# at its correct commit, not an accidental working-tree mixture.
for sha, prefixes in [(BASE, ('GOLD_EVENT_CHAIN_', 'GOLD_MAJOR_MOVE_MULTIHORIZON_', 'GOLD_MAJOR_MOVE_EVENT_ATLAS_')),
                      (PR118, ('GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_REFEREE_',)),
                      (PR119, ('GOLD_EVENT_CHAIN_2023_2025_V4_REFEREE_',)),
                      (PR120, ('GOLD_EVENT_CHAIN_H03_', 'GOLD_EVENT_CHAIN_H15_', 'GOLD_EVENT_CHAIN_ASTRA_'))]:
    names = subprocess.check_output(['git','ls-tree','-r','--name-only',sha], cwd=REPO, text=True).splitlines()
    for p in names:
        if p.startswith(PREFIX) and Path(p).name.startswith(prefixes):
            text = read(sha, Path(p).name)
            if p.endswith('.csv'):
                rr = list(csv.DictReader(io.StringIO(text)))
                inventory[-1].update(rows=len(rr), columns=list(rr[0]) if rr else [])
            elif p.endswith('.json'):
                json.loads(text)

v2 = rows(BASE, 'GOLD_MAJOR_MOVE_MULTIHORIZON_2023_2025_V2_ALL_774_DAYS_20261013.csv')
v3 = rows(BASE, 'GOLD_EVENT_CHAIN_2023_2025_V3_DAILY_VOL_SCALED_CONTROLS_20261013.csv')
v4 = rows(BASE, 'GOLD_EVENT_CHAIN_2023_2025_V4_13_TENSION_ONSETS_MATCHED_CONTROLS_20261013.csv')
daily = rows(PR120, 'GOLD_EVENT_CHAIN_H03_EXTRAPERIOD_2016_2026_DAILY_OUTCOMES_20261013.csv')
stored = json.loads(read(PR120, 'GOLD_EVENT_CHAIN_H03_EXTRAPERIOD_2016_2026_RESULTS_20261013.json'))
cal = rows(PR120, 'GOLD_EVENT_CHAIN_H15_NEWS_BLIND_CODING_UNIVERSE_249_MACRO_RELEASES_20261013.csv')
controls = rows(PR120, 'GOLD_EVENT_CHAIN_H15_NEWS_BLIND_NONEVENT_CALENDAR_20261013.csv')
ref119 = read(PR119, 'GOLD_EVENT_CHAIN_2023_2025_V4_REFEREE_REPRODUCE_20261013.py')

# Derived arithmetic replication, not upstream price or publication validation.
upcols = ['max_1h_up_pct','max_4h_up_pct','max_12h_up_pct','ret_1tradingday_pct','ret_3tradingdays_pct','ret_5tradingdays_pct']
dncols = ['max_1h_down_pct','max_4h_down_pct','max_12h_down_pct','ret_1tradingday_pct','ret_3tradingdays_pct','ret_5tradingdays_pct']
flag = [any(number(x[k]) >= 3 for k in upcols) or any(number(x[k]) <= -3 for k in dncols) for x in v2]
secondary = [not b and (max(number(x[k]) for k in upcols[1:3])>=2 or min(number(x[k]) for k in dncols[1:3])<=-2) for x,b in zip(v2,flag)]
assert (len(v2),sum(flag),sum(secondary)) == (774,151,23)
annual = []
for year in ['2023','2024','2025']:
    rr=[x for x in v3 if x['date'].startswith(year)]
    annual.append(dict(year=year, n=len(rr), z5=sum(abs(number(x['z5']))>=2 for x in rr),
                       z_union=sum(abs(number(x['z5']))>=2 or abs(number(x['z1']))>=2.5 for x in rr)))
assert [x['z_union'] for x in annual] == [24,26,30]
prices=[number(x['price']) for x in v3]
mismatches=[]
for i,x in enumerate(v3[:-10]):
    future=[100*(p/prices[i]-1) for p in prices[i+1:i+11]]
    first=next(('UP' if a>=3 else 'DOWN' for a in future if a>=3 or a<=-3),'NONE')
    if first != x['first']: mismatches.append(x['date'])
assert not mismatches
summary=[]
for ref in stored['results']:
    rr=[x for x in daily if x['scope']==ref['period']]
    c=Counter(x['first'] for x in rr)
    assert (len(rr),c['UP'],c['DOWN'],c['NONE'])==(ref['days'],ref['up'],ref['down'],ref['none'])
    assert abs(auc(rr)-ref['auc_r20_given_move'])<1e-11
    summary.append(dict(scope=ref['period'], n=len(rr), up=c['UP'],down=c['DOWN'],none=c['NONE'],
                        any_rate=(c['UP']+c['DOWN'])/len(rr), auc_conditional=auc(rr),
                        interpretation='overlapping origins; descriptive; no causal or predictive validation'))

# Directly verified missing release dates (official-source evidence in references.md).
# An ADDITIVE exception ledger, not a claim that the entire calendar is now complete.
known=[('2016-01-08','NFP','08:30','https://www.bls.gov/news.release/archives/empsit_01082016.htm'),
       ('2016-01-20','CPI','08:30','https://www.bls.gov/news.release/archives/cpi_01202016.htm'),
       ('2020-09-04','NFP','08:30','https://www.bls.gov/news.release/archives/empsit_09042020.htm'),
       ('2026-09-11','CPI','08:30','https://www.bls.gov/news.release/archives/cpi_09112026.htm'),
       ('2026-09-16','FOMC','14:00','https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm')]
existing={(x['date'],x['type']) for x in cal}
cdates={x['candidate_date'] for x in controls}
exceptions=[]
for d,k,t,url in known:
    utc=datetime.fromisoformat(d+'T'+t).replace(tzinfo=ZoneInfo('America/New_York')).astimezone(ZoneInfo('UTC')).isoformat()
    contaminated=sorted(x for x in cdates if abs((datetime.fromisoformat(x)-datetime.fromisoformat(d)).days)<=1)
    exceptions.append(dict(date=d,type=k,official_release_utc=utc,missing_in_249=(d,k) not in existing,
                           same_day_in_controls=d in cdates,within_1_day_controls=';'.join(contaminated),source=url,
                           scope='verified exception only; not exhaustive calendar repair'))
assert all(x['missing_in_249'] for x in exceptions)

# Source-code diagnostics with literal evidence; not modified referees' files.
assert 'ge[ci + 1:min(n, ci + 31)].any()' in ref119
idx={x['date']:i for i,x in enumerate(v3)}
risk=sorted(idx[x['risk_cross_date']] for x in v4)
overlaps=sum(b-a<=10 for i,a in enumerate(risk) for b in risk[i+1:])

# Unit checks expose the closed-bar rollover edge in the committed source SQL.
boundary=[]
for s in ['2024-01-05T17:00:00-05:00','2024-07-05T17:00:00-04:00']:
    local=datetime.fromisoformat(s)
    old=(local+timedelta(hours=7)).date().isoformat()
    close_inclusive=(local+timedelta(hours=7,microseconds=-1)).date().isoformat()
    assert old!=close_inclusive
    boundary.append(dict(bar_end=s,source_sql_session=old,close_inclusive_session=close_inclusive,
                         status='boundary test only; actual affected vendor bars not counted'))

result=dict(status='PILOT_0_DATA_AND_DESIGN_AUDIT_COMPLETED; MECHANISM_ESTIMATION_BLOCKED',
    v2=dict(n=774,primary=sum(flag),secondary=sum(secondary)),v3_annual=annual,
    v3_close_firstpass_mismatches=mismatches,h03=summary,
    calendar=dict(n=len(cal),by_year_type=dict(sorted(Counter(x['date'][:4]+'_'+x['type'] for x in cal).items())),
                  controls=len(controls), verified_missing=len(exceptions),
                  omitted_release_days_in_controls=sum(x['same_day_in_controls'] for x in exceptions),
                  contaminated_candidate_dates=sorted(set(d for x in exceptions for d in x['within_1_day_controls'].split(';') if d)),
                  filled_reversal_labels=sum(x['news_reversal_label'] not in ('','UNSCORED') for x in cal)),
    control_future_selection_confirmed=True,overlapping_risk_pairs=overlaps,rollover_edge_tests=boundary,
    blockers=['No complete outcome-independent release universe','No blind firstprint narrative labels',
              'No audited event-aligned intraday mediators in committed packet',
              'No raw-bar boundary replication performed; aggregate counts do not prove correct timestamps'],
    scientific_claim='No mechanism effect size, no causal p-value, no new forecasting success claim')
csvsave('calendar_exceptions.csv',exceptions)
csvsave('descriptive_replication.csv',summary)
save('audit_results.json',result)
unique={(x['commit'],x['path']):x for x in inventory}
save('input_inventory.json',list(unique.values()))
print(json.dumps(result,indent=2,ensure_ascii=False))
