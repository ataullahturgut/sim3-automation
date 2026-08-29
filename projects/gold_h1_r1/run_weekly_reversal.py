#!/usr/bin/env python3
import io, urllib.request
from pathlib import Path
import numpy as np, pandas as pd
PIN='f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0'
BASE=f'https://raw.githubusercontent.com/simom1/XAUUSD-history/{PIN}/Gold-Cash/XAUUSD'
OUT=Path('projects/gold_h1_r1')
def get(name):
    with urllib.request.urlopen(f'{BASE}/{name}',timeout=60) as r:return pd.read_csv(io.BytesIO(r.read()))
def met(df,fire):
    p=df.dir3.to_numpy().copy(); m=(df.conflict.to_numpy()==1)&np.asarray(fire,bool); p[m]=df.slow_dir.to_numpy()[m]; y=df.actual_dir.to_numpy()
    rec=[np.mean(p[y==c]==y[y==c]) for c in (-1,1) if np.any(y==c)]
    return {'acc':float(np.mean(p==y)),'ba':float(np.mean(rec)),'flips':int(m.sum()),'corrected':int(np.sum(m&(df.dir3.to_numpy()!=y)&(p==y))),'damaged':int(np.sum(m&(df.dir3.to_numpy()==y)&(p!=y)))}
monthly=pd.read_csv(OUT/'monthly_direction_min_2010_2023.csv'); monthly.target=pd.to_datetime(monthly.target); monthly.origin=pd.to_datetime(monthly.origin)
d1=get('XAUUSD_D1.csv'); w1=get('XAUUSD_W1.csv'); d1.time=pd.to_datetime(d1.time); w1.time=pd.to_datetime(w1.time)
R=[]
for _,r in w1[(w1.time>='2010-01-01')&(w1.time<='2022-12-31')].iterrows():
 q=d1[(d1.time>=r.time+pd.Timedelta(days=1))&(d1.time<=r.time+pd.Timedelta(days=5))]
 if q.empty:R.append([r.time,0,np.nan,np.nan,np.nan,np.nan,np.nan,False]);continue
 a=np.array([q.iloc[0].open,q.high.max(),q.low.min(),q.iloc[-1].close,q.tick_volume.sum()],float); b=np.array([r.open,r.high,r.low,r.close,r.tick_volume],float); d=a-b
 R.append([r.time,len(q),*d,bool(np.all(np.abs(d)<1e-8))])
recon=pd.DataFrame(R,columns=['week','n_d1','open_diff','high_diff','low_diff','close_diff','volume_diff','exact']); recon.to_csv(OUT/'d1_w1_reconciliation_2010_2022.csv',index=False)
w=w1.sort_values('time').reset_index(drop=True); w['sma4']=w.close.rolling(4).mean(); w['gap']=w.close/w.sma4-1; w['raw']=np.sign(w.gap).fillna(0).astype(int); w['ret1']=w.close.pct_change(); w['vol8']=w.ret1.rolling(8).std(); w['gprev']=w.gap.shift()
run=[]; last=0;n=0
for x in w.raw:
 n=n+1 if x!=0 and x==last else (1 if x!=0 else 0); run.append(n); last=x
w['persist']=run; w['slow']=np.where((w.raw!=0)&(w.raw==w.raw.shift()),w.raw,0).astype(int); w['wend']=w.time+pd.Timedelta(days=5)
E=[]
for _,m in monthly.iterrows():
 z=w[w.wend<=m.origin+pd.offsets.MonthEnd(0)].iloc[-1]; prior=int(m.dir3); slow=int(z.slow); conflict=int(slow!=0 and slow==-prior); cs=float(-prior*z.gap); ga=float(-prior*(z.gap-z.gprev)); oz=float(slow*z.ret1) if slow else np.nan; sz=float(cs/z.vol8) if z.vol8>0 else np.nan
 E.append([m.target.strftime('%Y-%m'),m.origin.strftime('%Y-%m'),int(m.actual_dir),bool(m.flat),prior,int(prior==int(m.actual_dir)),z.time.strftime('%Y-%m-%d'),z.wend.strftime('%Y-%m-%d'),float(z.close),float(z.sma4),float(z.gap),int(z.raw),slow,int(z.persist),conflict,cs,ga,float(z.ret1),oz,float(z.vol8),sz])
ev=pd.DataFrame(E,columns=['target','origin','actual_dir','flat','dir3','base_hit','week_label','week_end','weekly_close','sma4','gap_pct','raw_dir','slow_dir','raw_persistence','conflict','conflict_strength','gap_accel','weekly_ret1','oriented_weekly_ret','vol8','strength_z']); ev.to_csv(OUT/'weekly_event_panel_2010_2023.csv',index=False)
def cnt(a,b):
 q=ev[(ev.target>=a)&(ev.target<=b)]; s=np.where(q.slow_dir==0,'NEUTRAL',np.where(q.slow_dir==q.dir3,'CONFIRM','CONFLICT')); return pd.Series(s).value_counts().to_dict()
cd=cnt('2010-01','2020-12'); cv=cnt('2021-01','2023-12'); expd={'CONFIRM':53,'CONFLICT':36,'NEUTRAL':40}; expv={'CONFIRM':14,'CONFLICT':14,'NEUTRAL':7}
D=ev[(ev.target>='2010-01')&(ev.target<='2020-12')&(~ev.flat)].copy(); V=ev[(ev.target>='2021-01')&(ev.target<='2022-12')&(~ev.flat)].copy(); T=ev[(ev.target>='2023-01')&(ev.target<='2023-12')&(~ev.flat)].copy(); bd=met(D,np.zeros(len(D)));bv=met(V,np.zeros(len(V)));bt=met(T,np.zeros(len(T)))
F=['conflict_strength','raw_persistence','gap_accel','oriented_weekly_ret','strength_z']; dc=D[D.conflict==1]; C=[]
for f in F:
 for q in (.25,.5,.75):
  t=float(dc[f].dropna().quantile(q)); md=met(D,D[f]>=t); mv=met(V,V[f]>=t); C.append(['single',f,'',q,np.nan,t,np.nan,*md.values(),*mv.values()])
for i,f1 in enumerate(F):
 for f2 in F[i+1:]:
  for q1,q2 in ((.5,.5),(.25,.5),(.5,.25)):
   t1=float(dc[f1].dropna().quantile(q1));t2=float(dc[f2].dropna().quantile(q2));md=met(D,(D[f1]>=t1)&(D[f2]>=t2));mv=met(V,(V[f1]>=t1)&(V[f2]>=t2)); C.append(['and',f1,f2,q1,q2,t1,t2,*md.values(),*mv.values()])
cols=['kind','f1','f2','q1','q2','t1','t2']+[f'dev_{k}' for k in bd]+[f'val_{k}' for k in bv]; A=pd.DataFrame(C,columns=cols); A['dev_net']=A.dev_corrected-A.dev_damaged;A['val_net']=A.val_corrected-A.val_damaged;A['qualified']=(A.dev_acc>=bd['acc'])&(A.dev_net>0)&(A.val_acc>bv['acc'])&(A.val_ba>bv['ba'])&(A.val_net>0)&(A.val_flips>=2)
Q=A[A.qualified].copy(); best=None; status='NOT_PROVEN_PRE2023'
if len(Q):
 Q['score']=Q.val_ba+Q.val_acc+.25*Q.dev_ba+.01*Q.val_net; best=Q.sort_values(['score','dev_ba'],ascending=False).iloc[0]; fire=T[best.f1]>=best.t1
 if best.kind=='and':fire=fire&(T[best.f2]>=best.t2)
 mt=met(T,fire); status='PASS_2023_GENERALIZATION' if mt['acc']>bt['acc'] and mt['corrected']>mt['damaged'] else 'FAIL_2023_GENERALIZATION'
 for k,v in mt.items():best[f'test_{k}']=v
 t=T.copy();t['fire']=fire.astype(int);t['pred']=t.dir3;t.loc[(t.conflict==1)&(t.fire==1),'pred']=t.loc[(t.conflict==1)&(t.fire==1),'slow_dir'];t['hit']=(t.pred==t.actual_dir).astype(int);t.to_csv(OUT/'weekly_reversal_frozen_2023_test.csv',index=False)
A.to_csv(OUT/'weekly_reversal_rule_audit.csv',index=False)
pass_data=bool(recon.exact.all() and cd==expd and cv==expv)
lines=['# GOLD H1 R1 — Weekly Event-Level Reversal Discriminator R1','',f'- D1→W1 exhaustive 2010–2022: **{"PASS" if recon.exact.all() else "FAIL"}** ({len(recon)} bars, exact={int(recon.exact.sum())})',f'- Tactical count DEV reconciliation: **{"PASS" if cd==expd else "FAIL"}** reconstructed={cd} expected={expd}',f'- Tactical count VAL 2021–2023 reconciliation: **{"PASS" if cv==expv else "FAIL"}** reconstructed={cv} expected={expv}','',f'- Baseline DEV acc={bd["acc"]:.4f}, BA={bd["ba"]:.4f}',f'- Baseline VAL 2021–22 acc={bv["acc"]:.4f}, BA={bv["ba"]:.4f}',f'- Baseline 2023 acc={bt["acc"]:.4f}, BA={bt["ba"]:.4f}',f'- Pre-2023 qualified rules={len(Q)}']
if best is not None:lines += [f'- Frozen rule: {best.kind} {best.f1}>={best.t1:.6g}'+(f' AND {best.f2}>={best.t2:.6g}' if best.kind=='and' else ''),f'- DEV acc={best.dev_acc:.4f}, BA={best.dev_ba:.4f}, corrected={int(best.dev_corrected)}, damaged={int(best.dev_damaged)}',f'- VAL acc={best.val_acc:.4f}, BA={best.val_ba:.4f}, corrected={int(best.val_corrected)}, damaged={int(best.val_damaged)}',f'- 2023 acc={best.test_acc:.4f}, BA={best.test_ba:.4f}, corrected={int(best.test_corrected)}, damaged={int(best.test_damaged)}',f'- Final model status: **{status}**']
else: lines += ['- No rule survived DEV + 2021–22 validation.','- Final model status: **NOT_PROVEN_PRE2023**']
lines += ['',f'- DATA_GATE={"PASS" if pass_data else "FAIL"}','- Target leakage: NONE','- 2023+ tuning: NONE','- Random split: NONE','- False flips counted: YES']
(OUT/'WEEKLY_REVERSAL_DISCRIMINATOR_R1.md').write_text('\n'.join(lines)+'\n'); print('\n'.join(lines))
