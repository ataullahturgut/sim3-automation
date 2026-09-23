"""Materialize pinned research evidence; fetch raw DB bars read-only.

Run in a private audit directory. NEON_DATABASE_URL is never printed or saved.
Use --skip-db when raw_YEAR.json files were obtained through the authorized SQL connector.
"""
import argparse,json,os,subprocess
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,required=True);p.add_argument('--workdir',type=Path,required=True);p.add_argument('--skip-db',action='store_true');p.add_argument('--mirror',action='store_true');a=p.parse_args();a.workdir.mkdir(parents=True,exist_ok=True)
refs={'up2':'eb928b2d5be6250227d8e14dea2d58abe494f762','iw':'b88ef75a2b15e5dd46623b014a7adf06d211e933','sqrt':'2926796b6a7e9048d2c091c9c571cb928b773e02','router':'f4c661731c8888985b82b4bf16eab401184fa76f','base':'7982b422476df61eb0339b74265afd553414f2d2','route':'b22235f04dc48b173a93a98cc2ce22081bb0054e','cbr':'f187f89c166a75cefa8cf60709dcd4ce1027663d','mechanism':'12c0e7d9cb0adb65e43064592a29617c887e4675'}
def git(*args):return subprocess.check_output(['git','-C',str(a.repository),*args])
index=[]
for group,ref in refs.items():
 for path in git('ls-tree','-r','--name-only',ref).decode().splitlines():
  pick=(path.endswith('.py') and ('tools/' in path or 'regime_dampener_v1/' in path)) or (path.endswith(('.csv','.json')) and any(t in path for t in ['ONE_SIDED_UP2','IMPORTANCE_WEIGHTED','RAW_VS_SQRT','ROUTER_V2_LEGACY','MECHANISM_GAP','PRE2025_LEDGER']))
  if not pick:continue
  dest=a.workdir/group/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(git('show',ref+':'+path));index.append(dict(group=group,commit=ref,path=path,blob=git('rev-parse',ref+':'+path).decode().strip()))
for ref,path,dest in [('509c5ffa762f4ea49644b8ffe723ed2591ba52bf','gold_axis_2026/external_data/v2/dukascopy_xauusd_govsession_mid_5m_daily_features_2018_2021.csv','external_daily.csv'),('ad0fc4dcbe1687833bd9a153cd4bc6a754523464','gold_axis_2026/tools/regime_v1_router_sqrt.py','external_sqrt.py')]:
 (a.workdir/dest).write_bytes(git('show',ref+':'+path));index.append(dict(commit=ref,path=path,blob=git('rev-parse',ref+':'+path).decode().strip()))
(a.workdir/'index.json').write_text(json.dumps(index,indent=2))
if not a.skip_db:
 import psycopg
 with psycopg.connect(os.environ['NEON_DATABASE_URL'],options='-c default_transaction_read_only=on') as c:
  assert c.execute("SHOW transaction_read_only").fetchone()[0]=='on'
  for year in range(2020,2027):
   bars=c.execute('SELECT extract(epoch from observation_ts)::double precision,close FROM public.xau_intraday_research_cache_5m WHERE observation_ts >= %s::timestamptz AND observation_ts < %s::timestamptz ORDER BY observation_ts',(f'{year}-01-01',f'{year+1}-01-01')).fetchall()
   (a.workdir/f'raw_{year}.json').write_text(json.dumps([{'bars':bars}]))
if a.mirror:
 dest=a.workdir/'mdl'
 if not (dest/'.git').exists():subprocess.run(['git','clone','--filter=blob:none','--no-checkout','https://github.com/kevingtlin/Market-Data-Lab.git',str(dest)],check=True)
 subprocess.run(['git','-C',str(dest),'sparse-checkout','init','--no-cone'],check=True)
 (dest/'.git/info/sparse-checkout').write_text('\n'.join('/xauusd/'+s+'/m1/xauusd_'+s+'_m1_'+y+'.csv' for s in ['ask','bid'] for y in ['2018_*','2019_*','2020_*','2021_*','2022_01'])+'\n')
 subprocess.run(['git','-C',str(dest),'checkout','922f83a60cc574e7395fb27397077288055a1ef6'],check=True)
print('Pinned inputs prepared. Raw source remains local; do not commit raw files or credentials.')
