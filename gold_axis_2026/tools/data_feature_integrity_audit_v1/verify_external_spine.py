import os
import json,math
from pathlib import Path
import numpy as np,pandas as pd
R=Path(os.environ.get("GOLD_AUDIT_WORKDIR", str(Path(__file__).parent)));O=R/'results'
frames={};quality={}
for side in ['ask','bid']:
 files=sorted((R/'mdl/xauusd'/side/'m1').glob('*.csv'))
 x=pd.concat([pd.read_csv(p,usecols=['timestamp','close']) for p in files],ignore_index=True)
 quality[side]=dict(files=len(files),rows=len(x),duplicate_timestamps=int(x.timestamp.duplicated().sum()),conflicting_duplicate_timestamps=int((x.groupby('timestamp').close.nunique()>1).sum()),invalid=int((~np.isfinite(x.close)|(x.close<=0)).sum()))
 frames[side]=x.drop_duplicates('timestamp',keep='last').set_index('timestamp').sort_index().rename(columns={'close':side})
m=frames['ask'].join(frames['bid'],how='inner');quality['joined_rows']=len(m);quality['ask_without_bid']=len(frames['ask'])-len(m);quality['bid_without_ask']=len(frames['bid'])-len(m);quality['crossed_quotes']=int((m.ask<m.bid).sum())
m['mid']=(m.ask+m.bid)/2;m['bin']=pd.to_datetime(m.index,unit='ms',utc=True).floor('5min')
b=m.groupby('bin').mid.last();local=b.index.tz_convert('America/New_York');b=b[(local.weekday<5)&(local.hour!=17)];local=b.index.tz_convert('America/New_York');rows=[]
for d,g in b.groupby(local.strftime('%Y-%m-%d')):
 if d>='2022-01-01' or len(g)<240:continue
 a=g.to_numpy();r=np.diff(np.log(a));rv=float(r@r);neg=r[r<0];pos=r[r>0]
 if not math.isfinite(rv) or rv<=0:continue
 rows.append(dict(date=d,n_bars=len(a),close_mid=a[-1],rv_5m=rv,dr_5m=float(neg@neg),r3_5m=float(np.sum(r**3)),rs_plus_5m=float(pos@pos),rs_minus_5m=float(neg@neg)))
new=pd.DataFrame(rows);old=pd.read_csv(R/'external_daily.csv');j=new.merge(old,on='date',suffixes=('_new','_old'),validate='one_to_one');checks=[]
for f in new.columns[1:]:
 a=j[f+'_new'].to_numpy();b=j[f+'_old'].to_numpy();checks.append(dict(field=f,rows=len(j),mismatches=int((~np.isclose(a,b,atol=1e-12,rtol=1e-9)).sum()),max_abs=float(np.max(abs(a-b)))))
out=dict(quality=quality,new_rows=len(new),frozen_rows=len(old),joined=len(j),missing=sorted(set(old.date)-set(new.date)),extra=sorted(set(new.date)-set(old.date)),checks=checks)
(O/'external_full_spine_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
