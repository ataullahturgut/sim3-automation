"""Download raw official archives; never certify vintages from current archives."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,json,hashlib,datetime
ROOT=Path(__file__).parent; OUT=ROOT/'inputs';OUT.mkdir(exist_ok=True)
SOURCES={f'fred_{s}.csv':f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}' for s in ['DGS2','DGS10','DFII10','DTWEXB','DTWEXBGS','GOLDAMGBD228NLBM']}
SOURCES['fed_h15.csv']='https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package'
for y in range(2000,2010):SOURCES[f'cftc_legacy_{y}.zip']=f'https://www.cftc.gov/files/dea/history/deacot{y}.zip'
for y in range(2010,2023):SOURCES[f'cftc_disaggregated_futures_only_{y}.zip']=f'https://www.cftc.gov/files/dea/history/fut_disagg_txt_{y}.zip'
def get(item):
 name,url=item; rec={'name':name,'url':url,'first_print_verified':False,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  r=requests.get(url,timeout=(10,25));rec.update(http=r.status_code,mime=r.headers.get('Content-Type'),bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest())
  valid=r.status_code==200 and len(r.content)>100 and (r.content.startswith(b'PK') if name.endswith('.zip') else b'<html' not in r.content[:500].lower() and b'<!doctype' not in r.content[:500].lower())
  rec['download_valid']=valid
  if valid:(OUT/name).write_bytes(r.content)
 except Exception as e:rec.update(download_valid=False,error=str(e))
 print(name,rec.get('http'),rec['download_valid'],flush=True);return rec
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=8) as pool:rows=list(pool.map(get,SOURCES.items()))
 (OUT/'download_audit.json').write_text(json.dumps(rows,indent=2))
