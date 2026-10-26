"""Research-only PIT / source integrity audit; never writes to Neon or models.

Inputs are unmodified official-source files unpacked from GitHub Actions artifacts:
  input/slv_official_download_xml
  input/fed_h15_treasury_cmt_full_history.csv
  input/treasury_real_YYYY_original.csv for 2023-2026

Report records who knew what at a model decision instant; evidence on first
publication historical vintages is NOT asserted. If unavailable, block live use.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo
NY=ZoneInfo('America/New_York'); TR=ZoneInfo('Europe/Istanbul')
SHA={
 'slv_official_download_xml':'f3b618e04836451a752d56bc15624379c90d9bd5670a231bf0c34222c52e0950',
 'fed_h15_treasury_cmt_full_history.csv':'75dcc355bf51e2c45bd04d9b4cfc7fbc1edaa81abef1c0318de8a18ac44b9906',
 'treasury_real_2023_original.csv':'ef28bcafaca75c45bb6b3491b4df4bd1b5e2ab7ff35ac014b6f8362df330c0ca',
 'treasury_real_2024_original.csv':'d3ff00a9287ebf68fdc80e72fb2d1895a73c84b3ff2a6ca8c6d64648cb470f16',
 'treasury_real_2025_original.csv':'d3d3131c41e1f93f4661d227ce7079049d51888b395aaff863b6ad8e08838b64',
 'treasury_real_2026_original.csv':'fdc7c08fc76db7abf7784355516aec1b98d0a7cbcac88ca465587281cb082202',
}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def next_us_weekday(d):
    d+=dt.timedelta(days=1)
    while d.weekday()>4:d+=dt.timedelta(days=1)
    return d

def earliest_time(day,family):
    if family=='h15': return dt.datetime.combine(day,dt.time(16,15),NY)
    # Research-only conservative proxy, NOT publisher-verified availability.
    # Non-federal holidays and delayed releases require further evidence.
    return dt.datetime.combine(next_us_weekday(day),dt.time(9,0),NY)

def historical_slv(p):
    data=p.read_bytes()
    normalized,nfix=re.subn(rb'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9A-Fa-f]+;)',b'&amp;',data)
    root=ET.fromstring(normalized)
    sh=None
    for ws in root.iter():
        if ws.tag.split('}')[-1]!='Worksheet':continue
        name=next((v for k,v in ws.attrib.items() if k.endswith('}Name') or k=='Name'),'')
        if name=='Historical': sh=next((x for x in ws if x.tag.split('}')[-1]=='Table'),None);break
    assert sh is not None,'SLV Historical worksheet missing'
    all_rows=[]
    for row in sh:
        if row.tag.split('}')[-1]!='Row':continue
        vals=[]
        for cell in row:
            if cell.tag.split('}')[-1]!='Cell':continue
            idx=next((int(v)-1 for k,v in cell.attrib.items() if k.endswith('}Index')),None)
            if idx is not None:
                while len(vals)<idx: vals.append('')
            txt=next((x for x in cell if x.tag.split('}')[-1]=='Data'),None)
            vals.append((txt.text or '') if txt is not None else '')
        if any(vals):all_rows.append(vals)
    assert all_rows[0][:4]==['As Of','NAV per Share','Ex-Dividends','Shares Outstanding']
    rows=[]
    for vals in all_rows[1:]:
        d=dt.datetime.strptime(vals[0],'%b %d, %Y').date()
        if not (2023<=d.year<=2026):continue
        rows.append({'date':d,'nav':None if vals[1] in ('','--') else float(vals[1]),
                     'shares':None if len(vals)<4 or vals[3] in ('','--') else int(float(vals[3]))})
    return sorted(rows,key=lambda x:x['date']),nfix

def historical_h15(p):
    lines=list(csv.reader(p.open(encoding='utf-8-sig',newline='')))
    cols=lines[5];assert cols[0]=='Time Period'
    ix2=cols.index('RIFLGFCY02_N.B');ix10=cols.index('RIFLGFCY10_N.B')
    rows=[]
    for vals in lines[6:]:
        try:d=dt.date.fromisoformat(vals[0])
        except (ValueError,IndexError):continue
        if not (2023<=d.year<=2026):continue
        cv=lambda x:None if x in ('','ND') else float(x)
        rows.append({'date':d,'2y':cv(vals[ix2]),'10y':cv(vals[ix10])})
    return sorted(rows,key=lambda x:x['date'])

def historical_tips(src):
    rows=[]
    for year in range(2023,2027):
        with (src/f'treasury_real_{year}_original.csv').open(encoding='utf-8-sig',newline='') as f:
            for rec in csv.DictReader(f):
                d=dt.datetime.strptime(rec['Date'],'%m/%d/%Y').date()
                assert d.year==year
                rows.append({'date':d,'real10y':float(rec['10 YR']) if rec['10 YR'] else None})
    return sorted(rows,key=lambda x:x['date'])

def no_dupes(rows):return len(rows)-len({r['date'] for r in rows})
def available(rows,family,instant):
    usable=[r for r in rows if earliest_time(r['date'],family)<=instant]
    return usable[-1] if usable else None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    hashes={}
    for name,expected in SHA.items():
        p=a.input/name
        actual=digest(p)
        assert actual==expected,f'SHA mismatch: {name}'
        hashes[name]=actual
    slv,nfix=historical_slv(a.input/'slv_official_download_xml')
    h15=historical_h15(a.input/'fed_h15_treasury_cmt_full_history.csv')
    tips=historical_tips(a.input)
    for group in (slv,h15,tips):assert no_dupes(group)==0
    assert len(slv)==958 and len(h15)==994 and len(tips)==953
    assert [str(x['date']) for x in slv if x['shares'] is None]==['2024-03-29','2024-03-31']
    assert sum(r['2y'] is None and r['10y'] is None for r in h15)==42
    assert sum(r['real10y'] is None for r in tips)==0
    report={
      'generated_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
      'source_sha256_verified':hashes,'slv_bare_ampersands_xml_attribute_escaped':nfix,
      'rows_2023_2026':{'SLV':len(slv),'H15':len(h15),'TIPS_REAL10Y':len(tips)},
      'source_date_duplicates':{'SLV':no_dupes(slv),'H15':no_dupes(h15),'TIPS':no_dupes(tips)},
      'missing':{'SLV_shares':[str(r['date']) for r in slv if r['shares'] is None],
                 'SLV_NAV':sum(r['nav'] is None for r in slv),
                 'H15_missing_each':{'2y':sum(r['2y'] is None for r in h15),'10y':sum(r['10y'] is None for r in h15)},
                 'TIPS_real10y':sum(r['real10y'] is None for r in tips)},
      'caveats':{
          'H15':'Daily publication at 16:15 America/New_York (official schedule); historical value revisions/vintages not verified.',
          'TIPS':'Treasury observations ~15:30 NY market quotes; exact issuer publication instant and vintages unverified; T+1 09:00 NY proxy is research-only.',
          'SLV':'Issuer archived NAV and outstanding shares (not silver tonnage/confirmed cash flow); first-print vintages and issuer clock unverified; T+1 09:00 NY proxy research-only.',
          'GLD':'Not within downloaded artifacts; prior project audit reports 752 valid 2023-2025 rows but no original GLD file audited in this run.',
          'CFTC':'Not within downloaded artifacts; Tuesday position date is NOT Friday 15:30 NY publish date; holidays and exceptional delays must be mapped individually.',
          'CME':'Not downloaded; cannot verify.',
          'live_model_approved':False,'neon_written':False,'model_retrained':False,
      }
    }
    decisions=[]
    events=[dt.date(2026,3,30),dt.date(2026,3,31),dt.date(2026,4,1),dt.date(2026,4,2),dt.date(2026,4,3),dt.date(2026,8,11)]
    for day in events:
        when=dt.datetime.combine(day,dt.time(9,0),TR)
        f=available(h15,'h15',when); s=available(slv,'slv',when); t=available(tips,'tips',when)
        # No 'share_delta' if last visible value missing, including holiday dates.
        visible=[x for x in slv if earliest_time(x['date'],'slv')<=when]
        prev=visible[-2] if len(visible)>1 else None
        delta=(s['shares']-prev['shares']) if s and prev and s['shares'] is not None and prev['shares'] is not None else None
        decisions.append({'decision_tr_0900':when.isoformat(),'decision_ny':when.astimezone(NY).isoformat(),
           'h15_available_date':str(f['date']) if f else None,'h15_2y':f['2y'] if f else None,'h15_10y':f['10y'] if f else None,
           'tips_available_date_provisional':str(t['date']) if t else None,'tips_real10y':t['real10y'] if t else None,
           'slv_available_date_provisional':str(s['date']) if s else None,'slv_nav':s['nav'] if s else None,'slv_shares':s['shares'] if s else None,'slv_share_delta_proxy':delta,
           'all_data_point_in_time_certified':False})
    for row in decisions:
      when=dt.datetime.fromisoformat(row['decision_tr_0900'])
      for col in ('h15_available_date','tips_available_date_provisional','slv_available_date_provisional'):
        assert dt.date.fromisoformat(row[col])<=when.date(),'future date leakage!'
    with (a.output/'decision_time_provisional_2026.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=decisions[0].keys());w.writeheader();w.writerows(decisions)
    report['illustrative_decisions']=decisions
    (a.output/'source_time_integrity_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'counts':report['rows_2023_2026'],'missing':report['missing'],'decision_dates':[{k:v for k,v in x.items() if k.endswith('date') or k.endswith('_0900')} for x in decisions],'approval':False},indent=2))
if __name__=='__main__':main()