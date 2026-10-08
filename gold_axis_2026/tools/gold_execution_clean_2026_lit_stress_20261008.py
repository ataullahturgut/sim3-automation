"""First 2026 independent-source chronological stress of existing LIT target models.
Data 2025+ repaired HistData M1 -> M15; no 2026 training data/labels in fit.
Fix models/features/horizons before seeing 2026 scores. No PRAMV proxy.
"""
from __future__ import annotations
import os,json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,pandas as pd,psycopg
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import gold_execution_long_history_lit_same_date_20261008 as base

AX=Path(__file__).resolve().parents[1]
R=AX/'GOLD_EXECUTION_CLEAN_2026_LIT_STRESS_RESULT_2026-10-08.md'
S=AX/'GOLD_EXECUTION_CLEAN_2026_LIT_STRESS_SUMMARY_2026-10-08.json'
M=AX/'GOLD_EXECUTION_CLEAN_2026_LIT_STRESS_METRICS_2026-10-08.csv'
SOURCE='HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_2025_2026'
FIXED_MODELS={
  'LIT_DAY0_EXEC_0900':('DAY',['r0800_0830','r0830_0900','prev_ovn']),
  'LIT_OVN0_1600_1630':('OVN',['r1600_1630']),
  'LIT_OVN1_PAIR':('OVN',['r1600_1630','r1630_1700','pair_inter','pair_same'])
}
WINDOWS={'SHORT_2022':2022,'LONG_2020':2020}
WEIGHTS={'PLAIN':None,'BALANCED':'balanced'}

def read_private():
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
        with con.cursor() as c:
            c.execute("""SELECT bar_start_utc,open_price,close_price
               FROM gold_research_histdata_xau15m_candidate
               WHERE source_id=%s AND bar_start_utc>='2025-01-01'
               AND bar_start_utc<'2026-10-02' ORDER BY bar_start_utc""",(SOURCE,))
            rows=c.fetchall()
    q=pd.DataFrame(rows,columns=['ts','open','close'])
    q.ts=pd.to_datetime(q.ts,utc=True)
    if len(q)<37000:raise RuntimeError('RECOVERED_2025_2026_SOURCE_INCOMPLETE')
    closed=(q.ts.dt.dayofweek==5)|((q.ts.dt.dayofweek==6)&(q.ts.dt.hour<21))
    if closed.any():raise RuntimeError('RECOVERED_SPOT_MARKET_CLOSED_HOURS_NOT_ZERO')
    by=q.groupby(q.ts.dt.year).size()
    if by.get(2025,0)<22000 or by.get(2026,0)<16500:raise RuntimeError('MONTHLY_SOURCE_THIN')
    return q

def get_rows():
    old=base.native_2022_25()
    old=old[(old.ts>='2022-01-01')&(old.ts<'2025-01-01')]
    q=pd.concat([base.private_2020_21(),old,read_private()],ignore_index=True)
    q[['open','close']]=q[['open','close']].apply(pd.to_numeric,errors='coerce')
    q=q.dropna(subset=['ts','open','close'])
    q=q.sort_values('ts')
    if q.ts.duplicated().any():raise RuntimeError('DUPLICATE_UTC_BAR')
    # source transition 2024 Dec->2025 Jan must never create a stitched overnight return
    d=base.build(q)
    d.loc[(d.date.dt.year==2024)&(d.next_date.dt.year==2025),'ret_OVN']=np.nan
    d.loc[(d.date.dt.year==2025)&(d.date.dt.month==1)&
       (d.date.dt.day<=2),'prev_ovn']=np.nan
    return d

def predict(d):
    rows=[]
    for spec,(target,feats) in FIXED_MODELS.items():
        q=d.dropna(subset=feats+['ret_'+target,'y_'+target]).sort_values('date')
        test=q[(q.date>='2026-01-01')&(q.date<'2026-10-01')]
        for h,year in WINDOWS.items():
            tr=q[(q.date<'2026-01-01')&(q.year>=year)].copy()
            if target=='OVN':tr=tr[tr.next_date<=pd.Timestamp('2026-01-01')]
            if len(tr)<700 or tr['y_'+target].nunique()<2:raise RuntimeError('TRAIN_HISTORY_TOO_THIN')
            for w,cw in WEIGHTS.items():
                model=make_pipeline(StandardScaler(),
                    LogisticRegression(C=1,class_weight=cw,max_iter=2000))
                model.fit(tr[feats].to_numpy(float),tr['y_'+target].astype(int).to_numpy())
                pr=model.predict_proba(test[feats].to_numpy(float))[:,1]
                for (_,r),p in zip(test.iterrows(),pr):
                    rows.append({'model':spec,'target':target,'train':h,'weight':w,
                         'date':str(r.date.date()),'true_y':int(r['y_'+target]),
                         'prob_up':float(p),'training_n':len(tr)})
    return pd.DataFrame(rows)

def metrics(z):
    r=[]
    for (spec,train,w),group in z.groupby(['model','train','weight']):
        for split,name in ((group,'ALL_2026_JAN_SEP'),
             (group[group.date<'2026-04-01'],'Q1'),
             (group[(group.date>='2026-04-01')&(group.date<'2026-07-01')],'Q2'),
             (group[group.date>='2026-07-01'],'Q3'),
             (group[group.date>='2026-08-01'],'AUG_SEP_DIAGNOSTIC')):
            if len(split)<20:continue
            o=base.calc(split.true_y.to_numpy(),split.prob_up.to_numpy())
            r.append({'model':spec,'target':group.target.iloc[0],'train':train,
                'weight':w,'split':name,'n':len(split),'actual_up_rate':float(split.true_y.mean()),
                'accuracy':o['accuracy'],'balanced_accuracy':o['ba'],
                'up_recall':o['up_recall'],'down_recall':o['down_recall'],
                'brier':o['brier'],'predicted_up_rate':o['pred_up_rate'],
                'always_up_accuracy':float(split.true_y.mean()),
                'always_up_balanced_accuracy':.5})
    return pd.DataFrame(r)

def main():
    q=get_rows()
    forecasts=predict(q)
    met=metrics(forecasts)
    met.to_csv(M,index=False)
    info={'status':'COMPLETED_INDEPENDENT_SOURCE_2026_STRESS_NON_PROSPECTIVE',
      'training_cutoff':'2025-12-31','training_actuals_2026_used':False,
      'source_2025_2026':'HistData EST-fixed 1min->15min private candidate',
      'source_2020_2021':'Twelve Data native M15 private',
      'source_2022_2024':'previous frozen archive',
      'source_2026_weeks':'No Saturday/early Sunday bars',
      'target':'Istanbul 09:00 DAY; Istanbul 17:00 OVN',
      'feature_model_identity':'Existing LIT only, original three feature sets, C=1 sklearn',
      'method_selection':'No parameters selected using 2026 outcomes; plain/class-balanced both fully reported',
      'status_warning':'Retrospective 2026 period already viewed; not genuine out-of-sample confirmation. 2025 source is independent candidate; source stitching at boundaries remains provisional.',
      'no_PRAMV_model_retrained':True,'no_investment_strategy_promoted':True,
      'generated_at_utc':datetime.now(timezone.utc).isoformat()}
    S.write_text(json.dumps(info,indent=2)+'\n')
    lines=['# Independently recovered 2026 Jan-Sep LIT direction stress','',
      '**Status:** retrospective sensitivity study on private corrected historical spot data. No bank P&L, no PRAMV V1 score, no prospective proof.','',
      '| LIT model | Training | Weight | N | Accuracy | Balanced accuracy | UP recall | DOWN recall | Predicted UP rate |',
      '|---|---|---|---:|---:|---:|---:|---:|---:|']
    d=met[met.split=='ALL_2026_JAN_SEP']
    for row in d.itertuples(index=False):
        lines.append(f"| {row.model} | {row.train} | {row.weight} | {row.n} | {100*row.accuracy:.2f}% | {100*row.balanced_accuracy:.2f}% | {100*row.up_recall:.2f}% | {100*row.down_recall:.2f}% | {100*row.predicted_up_rate:.2f}% |")
    lines+=['','**Regime / quarter check** (same fixed policies, never selected on 2026 labels):','',
       '| Model | Training | Weight | Period | N | BA | DOWN recall | UP forecast share |','|---|---|---|---|---:|---:|---:|---:|']
    for row in met[met.split!='ALL_2026_JAN_SEP'].itertuples(index=False):
        lines.append(f"| {row.model} | {row.train} | {row.weight} | {row.split} | {row.n} | {100*row.balanced_accuracy:.2f}% | {100*row.down_recall:.2f}% | {100*row.predicted_up_rate:.2f}% |")
    lines+=['','This is diagnostic only: the 2026 market data source was corrected using a candidate independent vendor, 2026 outcomes were observed in the project, and no confidence claim or permanent retraining decision is justified.']
    R.write_text('\n'.join(lines)+'\n')
    print(R.read_text(),flush=True)
if __name__=='__main__':main()
