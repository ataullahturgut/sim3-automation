"""Read-only discover publicly documented EV Trading Labs Dukascopy-derived 2023 M15 download.
No account automation, no token, no vendor quote export, no speculative download URLs.
"""
import re,json,urllib.parse,requests
from pathlib import Path
from datetime import datetime,timezone
AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_EV_DATA_PUBLIC_ANNUAL_SOURCE_PROBE_2026-10-08.json'
SITE='https://evtradelabs.com/data'
def safe(path):
    return urllib.parse.urljoin(SITE,path) if path.startswith('/') else path
def run():
    r={'asof':'2026-10-08','source_site':SITE,'user_signup_attempted':False,
      'secret_required':False,'raw_prices_downloaded':False}
    try:
        h=requests.get(SITE,timeout=(8,18),headers={'User-Agent':'Mozilla/5.0'})
        r['page_status']=h.status_code
        r['page_len']=len(h.content)
        text=h.text
        paths=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',text)
        r['scripts']=paths[:15]
        direct=[x for x in re.findall(r'["\']([^"\']{8,250})["\']',text)
             if ('XAUUSD' in x.upper() or ('.json.gz' in x and 'AUDUSD' not in x))]
        r['text_asset_candidates']=direct[:18]
        r['server_contains_XAUUSD_2023']=('XAUUSD' in text and '2023' in text)
        scripts_out=[]
        for src in paths[:6]:
            path=safe(src)
            try:
                q=requests.get(path,timeout=(8,18))
                js=q.text
                # Only summarize references, not huge complete JS.
                route=set(re.findall(r'(?:(?:/api/|/data/|/download/)[a-zA-Z0-9_/?&=.-]{4,160})',js))
                snippets=[]
                for term in ('json.gz','download','XAUUSD'):
                    at=js.find(term)
                    if at>=0:snippets.append(js[max(0,at-70):at+90])
                scripts_out.append({'src':src[:150],'http':q.status_code,
                    'length':len(q.content),'candidate_routes':sorted(route)[:8],
                    'snippets':snippets[:3]})
            except Exception as e:scripts_out.append({'src':src[:150],'error':type(e).__name__})
        r['script_inspection']=scripts_out
        r['status']='PUBLIC_SOURCE_DISCOVERY_COMPLETE'
    except Exception as e:
        r['status']='SOURCE_PROBE_FAILED'
        r['error_type']=type(e).__name__
    r['finished_at']=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2)[:11000])
if __name__=='__main__':run()
