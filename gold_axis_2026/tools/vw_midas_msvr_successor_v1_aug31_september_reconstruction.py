from __future__ import annotations
import argparse, io, json, math, os, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, pandas as pd, psycopg, requests

TOOLS=Path(__file__).resolve().parent
sys.path.insert(0,str(TOOLS))
import vw_midas_msvr_successor_v1 as base

TARGET='2026-09'; ORIGIN='2026-08'; PREV='2026-07'
URLS={
 'Gold':'https://www.myfxbook.com/forex-market/currencies/XAUUSD-historical-data',
 'Silver':'https://www.myfxbook.com/forex-market/currencies/XAGUSD-historical-data',
 'Platinum':'https://www.myfxbook.com/forex-market/currencies/XPTUSD-historical-data',
 'Palladium':'https://www.myfxbook.com/forex-market/currencies/XPDUSD-historical-data',
}


def fetch_myfxbook(url):
    r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=40); r.raise_for_status()
    dfs=pd.read_html(io.StringIO(r.text))
    best=None
    for df in dfs:
        if df.shape[1] < 5: continue
        c0=pd.to_datetime(df.iloc[:,0],errors='coerce')
        if c0.notna().sum()>=20:
            tmp=pd.DataFrame({'date':c0,'close':pd.to_numeric(df.iloc[:,4],errors='coerce')}).dropna()
            if len(tmp)>=20: best=tmp; break
    if best is None: raise RuntimeError('MYFXBOOK_TABLE_NOT_FOUND:'+url)
    best['date']=best['date'].dt.date
    return best.drop_duplicates('date').sort_values('date')


def neon_july_and_bundle(dsn):
    b=base.load_data(dsn)
    july={}
    with psycopg.connect(dsn,autocommit=True) as conn:
      with conn.cursor() as cur:
        cur.execute('SET default_transaction_read_only=on')
        for metal,sid in base.DAILY_SERIES.items():
          cur.execute("SELECT observation_ts::date,value FROM observations WHERE series_id=%s AND observation_ts>='2026-07-01' AND observation_ts<'2026-08-01' ORDER BY observation_ts",(sid,))
          july[metal]={d:float(v) for d,v in cur.fetchall()}
    return b,july


def bridge_and_extend(b,july,my):
    report={}; july_common=set.intersection(*(set(july[m]) & set(my[m].date) for m in base.METALS))
    aug_common=set.intersection(*(set(d for d in my[m].date if d.isoformat().startswith('2026-08')) for m in base.METALS))
    if len(july_common)<20: raise RuntimeError(f'BRIDGE_TOO_FEW_JULY_COMMON:{len(july_common)}')
    if len(aug_common)<20 or max(aug_common).isoformat()!='2026-08-31': raise RuntimeError(f'AUGUST_INCOMPLETE:n={len(aug_common)} last={max(aug_common) if aug_common else None}')
    lookup={m:dict(zip(my[m].date,my[m].close.astype(float))) for m in base.METALS}
    passed=True
    for m in base.METALS:
        a=np.array([july[m][d] for d in sorted(july_common)],float); q=np.array([lookup[m][d] for d in sorted(july_common)],float)
        ape=np.abs(q-a)/np.abs(a)*100
        met={'n':len(a),'median_daily_ape_pct':float(np.median(ape)),'p95_daily_ape_pct':float(np.percentile(ape,95)),'monthly_mean_ape_pct':float(abs(q.mean()-a.mean())/abs(a.mean())*100),'stak_mean':float(a.mean()),'myfxbook_mean':float(q.mean())}
        met['pass']=met['median_daily_ape_pct']<=2.5 and met['p95_daily_ape_pct']<=7.5 and met['monthly_mean_ape_pct']<=3.0
        passed &= met['pass']; report[m]=met
    if not passed: raise RuntimeError('BLOCKED_AUG31_MYFXBOOK_STAKTRAKR_BRIDGE_NOT_PROVEN:'+json.dumps(report,sort_keys=True))
    aug_dates=sorted(aug_common)
    for m in base.METALS:
        vals=np.array([lookup[m][d] for d in aug_dates],float)
        b.daily_month_values[m]['2026-08']=vals
        b.monthly_metal[m]['2026-08']=float(vals.mean())
    return report,aug_dates


def x_for_target(b,target,gpr_history):
    p=base.month_shift(target,-1); pp=base.month_shift(target,-2); z=base.gpr_norm(gpr_history,pp)
    x=[]
    for m in base.METALS:
        M=b.monthly_metal[m]
        x.extend((math.log(M[p]/M[pp]),base.weighted_daily_return(b,m,p,z)))
    return np.array(x,float)


def forecast_cfg(b,target,cfg):
    origin=base.month_shift(target,-1); hist=b.gpr_vintages[origin]
    train={}
    for t in base.month_range('2010-03',base.month_shift(target,-1)):
        try: train[t]=base.sample_for_target(b,t,hist,True)
        except RuntimeError: pass
    keys=sorted(train)
    X=np.stack([train[k][0] for k in keys]); Y=np.stack([train[k][1] for k in keys]); tx=x_for_target(b,target,hist)[None,:]
    xm,xs,ym,ys=X.mean(0),X.std(0),Y.mean(0),Y.std(0); xs=np.where(xs<1e-9,1,xs); ys=np.where(ys<1e-9,1,ys)
    C,ep,gm=cfg; mdl=base.MSVR(C=C,epsilon=ep,gamma=gm/X.shape[1]).fit((X-xm)/xs,(Y-ym)/ys)
    pred=mdl.predict((tx-xm)/xs)[0]*ys+ym
    return float(pred[0]),len(keys)


def select_cfg(b):
    eligible=list(base.month_range(base.INNER_START,'2026-08')); scores=[]
    for cfg in base.CONFIGS:
        errs=[]
        for u in eligible:
            try:
                samples=base.all_samples_at_origin(b,u,governed=True)
                pred,_=base.fit_predict(samples,u,cfg)
                p=base.month_shift(u,-1); actual=math.log(b.monthly_metal['Gold'][u]/b.monthly_metal['Gold'][p]); errs.append(abs(float(pred[0])-actual))
            except RuntimeError: pass
        if len(errs)<base.MIN_INNER: continue
        scores.append((float(np.mean(errs)),cfg[0],cfg[1],cfg[2],cfg,len(errs)))
    if not scores: raise RuntimeError('NO_ELIGIBLE_CONFIG')
    scores.sort(); return scores[0][-2],scores[0][0],scores[0][-1]


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',default='vw_midas_msvr_aug31_sep_reconstruction.json'); args=ap.parse_args()
    dsn=os.environ.get('NEON_DATABASE_URL');
    if not dsn: raise SystemExit('NEON_DATABASE_URL required')
    retrieved=datetime.now(timezone.utc).isoformat()
    my={m:fetch_myfxbook(URLS[m]) for m in base.METALS}
    b,july=neon_july_and_bundle(dsn); bridge,aug_dates=bridge_and_extend(b,july,my)
    cfg,inner_err,inner_n=select_cfg(b); pred_log,train_n=forecast_cfg(b,TARGET,cfg)
    aug_anchor=float(b.monthly_metal['Gold']['2026-08']); fc=aug_anchor*math.exp(pred_log)
    out={'model_id':base.MODEL_ID,'evidence_class':'ORIGIN_RECONSTRUCTION_HISTORICAL_REPLAY','calculated_at_utc':retrieved,'origin_month':'2026-08','origin_boundary':'2026-08-31','target_month':'2026-09','source_identity':'MYFXBOOK_FOUR_METAL_AUG31_RECONSTRUCTION_V1','source_urls':URLS,'july_bridge':bridge,'august_common_days':len(aug_dates),'august_first_common_date':min(aug_dates).isoformat(),'august_last_common_date':max(aug_dates).isoformat(),'august_monthly_means':{m:float(b.monthly_metal[m]['2026-08']) for m in base.METALS},'gpr_identity':base.GPR_PIT,'gpr_origin_vintage':'2026-08','gpr_lag_observation_month':'2026-07','selected_config':list(cfg),'inner_forecasts_n':inner_n,'inner_mean_abs_gold_log_return_error':inner_err,'training_rows':train_n,'predicted_gold_log_return':pred_log,'random_walk_same_origin':aug_anchor,'september_xau_monthly_average_forecast':float(fc),'governance':{'prospective_claim':False,'database_writes':'NONE','forecast_authority_write':'NONE','decision_write':'NONE','runtime_mutation':'NONE','auto_selector':'OFF','auto_ensemble':'OFF'}}
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'forecast':fc,'rw':aug_anchor,'config':cfg,'august_common_days':len(aug_dates),'evidence_class':out['evidence_class']},sort_keys=True))
if __name__=='__main__': main()
