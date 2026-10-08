"""2025 source-repair sensitivity: retrain same pre-2025 LIT models, score same 2025 days.
No post-2024 outcome may influence fit or hyperparameters.
NEVER promote source or model automatically; metrics are retrospective.
"""
from __future__ import annotations
import os,json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import pandas as pd
import psycopg
from scipy.stats import binomtest
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import gold_execution_long_history_lit_same_date_20261008 as base
SOURCE='HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_2025_2026'

AX=Path(__file__).resolve().parents[1]
OUT=AX/'GOLD_EXECUTION_2025_SOURCE_REPAIRED_LIT_RESULT_2026-10-08.md'
MET=AX/'GOLD_EXECUTION_2025_SOURCE_REPAIRED_LIT_METRICS_2026-10-08.csv'
SUM=AX/'GOLD_EXECUTION_2025_SOURCE_REPAIRED_LIT_SUMMARY_2026-10-08.json'

def private2025():
    with psycopg.connect(os.environ['NEON_DATABASE_URL'],connect_timeout=20) as con:
        with con.cursor() as cur:
            cur.execute("""SELECT bar_start_utc,open_price,close_price,native_minute_bars
                FROM gold_research_histdata_xau15m_candidate
                WHERE source_id=%s AND bar_start_utc>='2025-01-01' AND bar_start_utc<'2026-01-01'
                ORDER BY bar_start_utc""",(SOURCE,))
            rows=cur.fetchall()
    q=pd.DataFrame(rows,columns=['ts','open','close','native_m1'])
    q.ts=pd.to_datetime(q.ts,utc=True)
    if len(q)<22000:raise RuntimeError('INDEPENDENT_2025_NOT_FULLY_AVAILABLE')
    if q.ts.duplicated().any():raise RuntimeError('INDEPENDENT_DUPLICATE_UTC')
    if ((q.ts.dt.dayofweek==5)|((q.ts.dt.dayofweek==6)&(q.ts.dt.hour<21))).any():
        raise RuntimeError('INDEPENDENT_BAD_CLOSED_MARKET_TIME')
    return q[['ts','open','close']]

def market(rows,which):
    frozen=base.native_2022_25()
    core=frozen[frozen.ts.dt.year<2025].copy()
    original=frozen[(frozen.ts>='2025-01-01')&(frozen.ts<'2026-01-10')].copy()
    independent=private2025()
    whole=pd.concat([base.private_2020_21(),core,
        original if which=='FROZEN' else independent],ignore_index=True)
    whole[['open','close']]=whole[['open','close']].apply(pd.to_numeric,errors='coerce')
    whole=whole.dropna(subset=['open','close','ts'])
    if whole.ts.duplicated().any():raise RuntimeError('DUPLICATE_TIMESTAMPS_'+which)
    q=base.build(whole)
    return q

def predict_2025(q,spec,target,feats,history_year):
    selected=q.dropna(subset=feats+['ret_'+target,'y_'+target]).sort_values('date')
    tr=selected[(selected.year>=history_year)&(selected.date<pd.Timestamp('2025-01-01'))]
    if target=='OVN':
        tr=tr[tr.next_date<=pd.Timestamp('2025-01-01')]
    te=selected[selected.year==2025].copy()
    if len(tr)<400 or len(te)<190:raise RuntimeError('TRAIN_OR_TEST_UNDER_COVERAGE')
    model=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000))
    model.fit(tr[feats].to_numpy(float),tr['y_'+target].astype(int).to_numpy())
    te['p']=model.predict_proba(te[feats].to_numpy(float))[:,1]
    te['y']=te['y_'+target].astype(int)
    te['ret']=te['ret_'+target].astype(float)
    return te[['date','y','ret','p']].copy(),len(tr)

def pair(a,b):
    x=a.rename(columns={'y':'y_frozen','ret':'ret_frozen','p':'p_frozen'})
    y=b.rename(columns={'y':'y_repaired','ret':'ret_repaired','p':'p_repaired'})
    z=x.merge(y,on='date',validate='one_to_one')
    if len(z)<185:raise RuntimeError('INSUFFICIENT_SAME_DATE_COMPARISON')
    old=base.calc(z.y_frozen.to_numpy(),z.p_frozen.to_numpy())
    fixed=base.calc(z.y_repaired.to_numpy(),z.p_repaired.to_numpy())
    # Also score unchanged old predictions using independent repaired target.
    old_on_repaired=base.calc(z.y_repaired.to_numpy(),z.p_frozen.to_numpy())
    yf=z.y_repaired.to_numpy()
    oc=(z.p_frozen.to_numpy()>=.5)==yf
    nc=(z.p_repaired.to_numpy()>=.5)==yf
    rescue=int((nc&~oc).sum());breaks=int((~nc&oc).sum())
    return {'same_days':len(z),'changed_realized_direction':int((z.y_frozen!=z.y_repaired).sum()),
        'changed_prediction_direction':int(((z.p_frozen>=.5)!=(z.p_repaired>=.5)).sum()),
        'frozen_evaluated_frozen':old,'frozen_evaluated_repaired':old_on_repaired,
        'repaired_evaluated_repaired':fixed,'rescues_vs_frozen_on_repaired':rescue,
        'breaks_vs_frozen_on_repaired':breaks,
        'mcnemar_exact_p':float(binomtest(rescue,rescue+breaks,.5).pvalue) if rescue+breaks else 1.,
        'delta_repaired_vs_frozen_prediction_ba_pp':100*(fixed['ba']-old_on_repaired['ba']),
        'delta_repaired_vs_old_archive_ba_pp':100*(fixed['ba']-old['ba'])}

def main():
    qf=market(None,'FROZEN')
    qc=market(None,'REPAIRED')
    rows=[]
    for spec,(target,feats) in base.FEATURES.items():
        for start_year in (2020,2022):
            a,na=predict_2025(qf,spec,target,feats,start_year)
            c,nc=predict_2025(qc,spec,target,feats,start_year)
            res=pair(a,c)
            rows.append({'spec':spec,'train_since':start_year,'ntrain':na,
             'new_train_n':nc,**res})
    detail=pd.DataFrame(rows)
    data=[]
    for r in rows:
        f=r['frozen_evaluated_frozen']; same=r['frozen_evaluated_repaired']
        c=r['repaired_evaluated_repaired']
        data.append({'spec':r['spec'],'train_since':r['train_since'],
         'n':r['same_days'],'label_flips':r['changed_realized_direction'],
         'prediction_flips':r['changed_prediction_direction'],
         'frozen_original_ba':f['ba'],'frozen_on_repaired_ba':same['ba'],
         'repaired_ba':c['ba'],'repaired_acc':c['accuracy'],
         'repaired_up_recall':c['up_recall'],'repaired_down_recall':c['down_recall'],
         'repaired_brier':c['brier'],
         'delta_on_same_true_label_pp':r['delta_repaired_vs_frozen_prediction_ba_pp'],
         'rescues':r['rescues_vs_frozen_on_repaired'],
         'breaks':r['breaks_vs_frozen_on_repaired'],
         'mcnemar_p':r['mcnemar_exact_p']})
    df=pd.DataFrame(data);df.to_csv(MET,index=False)
    SUM.write_text(json.dumps({'status':'COMPLETED_RESEARCH_CANDIDATE_NONCANONICAL',
      '2025_source':'HistData independent M1->M15, EST fixed UTC-05',
      '2025_old_source':'Frozen legacy archived M15 (weekend contamination)',
      'comparison':'Identical eligible 2025 dates and model configurations; old predictions also rescored on repaired labels',
      'training_cutoff':'2024-12-31','model_promotion':False,
      'label_evidence':'newly calculated 2025 retrospective, not prospective / independently confirmed bank executable quote',
      'metrics':data,'created_at':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
    lines=['# 2025 LIT: frozen suspect vs independent repaired source — same-date retrospective','',
      '**Source gate:** 2025 frozen 15m archive has forbidden weekend activity. HistData 2025 is a distinct private recovery candidate, not a silently replaced canonical feed. No model was promoted.','',
      '| Model | Train start | Common days | Frozen BA (old target) | Frozen forecast vs repaired target BA | Repaired BA | Repaired DOWN recall | Label flips | McNemar p |',
      '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in data:
        lines.append(f"| {r['spec']} | {r['train_since']} | {r['n']} | {r['frozen_original_ba']*100:.2f}% | {r['frozen_on_repaired_ba']*100:.2f}% | {r['repaired_ba']*100:.2f}% | {r['repaired_down_recall']*100:.2f}% | {r['label_flips']} | {r['mcnemar_p']:.4f} |")
    lines+=['','The 2025 test dates were seen by earlier researchers; retrospective comparison is **not** prospective OOS. Differences can be caused by changed input features **and** changed realized target quotes. 2020/2021 source and old 2022-24 remain fixed in both columns.','','Scientific standard: do not infer improvement from switching sources, or deploy without vintage/market-clock/source comparison and genuinely new forward 2026 test.']
    OUT.write_text('\n'.join(lines)+'\n')
    print(OUT.read_text(),flush=True)
if __name__=='__main__':main()
