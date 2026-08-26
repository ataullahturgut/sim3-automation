import base64,gzip,json,math,os
from pathlib import Path
import requests
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import pairwise_kernels
import torch
import torch.nn as nn

SEED=20260826
np.random.seed(SEED); torch.manual_seed(SEED); torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent
METALS=['Gold','Silver','Platinum','Palladium']

# ---------- data ----------
def load_core():
    b64=(ROOT/'core5_monthly.csv.gz.b64').read_text().strip()
    raw=gzip.decompress(base64.b64decode(b64)).decode()
    from io import StringIO
    return pd.read_csv(StringIO(raw),parse_dates=['date']).set_index('date').sort_index()

def fetch_history():
    s=requests.Session(); rows=[]
    for y in range(2010,2027):
        u=f'https://raw.githubusercontent.com/lbruton/StakTrakr/master/data/spot-history-{y}.json'
        r=s.get(u,timeout=90); r.raise_for_status()
        for z in r.json():
            if z.get('metal') in METALS:
                d=pd.to_datetime(z['timestamp']).normalize()
                if d<=pd.Timestamp('2026-07-31'):
                    rows.append((d,z['metal'],float(z['spot']),z.get('provider','')))
    d=pd.DataFrame(rows,columns=['date','metal','spot','provider']).sort_values(['date','metal'])
    d=d.drop_duplicates(['date','metal'],keep='last')
    w=d.pivot(index='date',columns='metal',values='spot').sort_index()[METALS].dropna()
    return w

def gpr_z(core,m):
    h=core.loc[:m,'gpr'].dropna(); lo=float(h.min()); hi=float(h.max())
    return 0.5 if hi<=lo else float((h.iloc[-1]-lo)/(hi-lo))

def vw_return(v,gz):
    r=np.diff(np.log(np.asarray(v,float)))
    if len(r)==0: return 0.0
    lam=0.1*math.exp(-10.0*float(np.clip(gz,0,1)))
    age=np.arange(len(r)-1,-1,-1,dtype=float)
    w=np.exp(-lam*age); w/=w.sum()
    return float(w@r)

# ---------- true multi-output SVR ----------
class MSVR:
    def __init__(self,C=1.0,epsilon=.05,gamma=None,tol=1e-3):
        self.C=C; self.epsilon=epsilon; self.gamma=gamma; self.tol=tol
    def fit(self,x,y):
        self.xTrain=x.copy(); C=self.C; ep=self.epsilon
        H=pairwise_kernels(x,x,metric='rbf',filter_params=True,gamma=self.gamma)
        self.Beta=np.zeros((len(x),y.shape[1])); E=y-H@self.Beta
        u=np.sqrt(np.sum(E*E,axis=1,keepdims=True)); i=np.where(u>ep)[0]
        if len(i)==0: return self
        a=2*C*(u-ep)/np.maximum(u,1e-12)
        L=np.zeros_like(u); L[i]=u[i]**2-2*ep*u[i]+ep**2
        prev=float(np.trace(self.Beta.T@H@self.Beta)/2+C*np.sum(L)/2)
        for _ in range(80):
            if len(i)==0: break
            oldB=self.Beta.copy(); oldu=u.copy(); oldi=i.copy()
            M=H[np.ix_(i,i)]+np.diag(1/np.maximum(a[i].reshape(-1),1e-10))+1e-10*np.eye(len(i))
            try: sol=np.linalg.solve(M,y[i])
            except np.linalg.LinAlgError: sol=np.linalg.pinv(M)@y[i]
            eta=1.0; accepted=False
            for _ in range(18):
                B=np.zeros_like(self.Beta); B[i]=eta*sol+(1-eta)*oldB[i]
                e=y-H@B; uu=np.sqrt(np.sum(e*e,axis=1,keepdims=True)); j=np.where(uu>=ep)[0]
                LL=np.zeros_like(uu); LL[j]=uu[j]**2-2*ep*uu[j]+ep**2
                cur=float(np.trace(B.T@H@B)/2+C*np.sum(LL)/2)
                if cur<=prev+1e-12:
                    self.Beta=B; u=uu; i=j; accepted=True; break
                eta/=10
            if not accepted:
                self.Beta=oldB; u=oldu; i=oldi; break
            if prev!=0 and (prev-cur)/abs(prev)<self.tol: break
            prev=cur; a=2*C*(u-ep)/np.maximum(u,1e-12)
        return self
    def predict(self,x):
        H=pairwise_kernels(x,self.xTrain,metric='rbf',filter_params=True,gamma=self.gamma)
        return H@self.Beta

def msvr_samples(wide,core):
    mavg=wide.groupby(wide.index.to_period('M')).mean(); mavg.index=mavg.index.to_timestamp()
    out=[]
    for t in sorted(set(mavg.index)&set(core.index)):
        p=t-pd.offsets.MonthBegin(1); pp=p-pd.offsets.MonthBegin(1)
        if p not in mavg.index or pp not in mavg.index or p not in core.index or pp not in core.index: continue
        gz=gpr_z(core,p); X=[]; Y=[]; ok=True
        for metal in METALS:
            pm=float(np.log(mavg.loc[p,metal]/mavg.loc[pp,metal]))
            mask=wide.index.to_period('M')==p.to_period('M'); v=wide.loc[mask,metal].values
            if len(v)<5: ok=False; break
            X.extend([pm,vw_return(v,gz)])
            Y.append(float(np.log(mavg.loc[t,metal]/mavg.loc[p,metal])))
        if ok: out.append((t,np.array(X,float),np.array(Y,float)))
    return out

def tune_msvr(S):
    val=[t for t,_,_ in S if pd.Timestamp('2025-01-01')<=t<=pd.Timestamp('2025-12-01')]
    ranked=[]
    for C in [.1,1.,10.]:
      for ep in [.02,.05]:
       for gm in [.5,1.]:
        e=[]
        for t in val:
            tr=[s for s in S if s[0]<t]; te=[s for s in S if s[0]==t][0]
            X=np.stack([s[1] for s in tr]); Y=np.stack([s[2] for s in tr])
            sx=StandardScaler().fit(X); sy=StandardScaler().fit(Y)
            m=MSVR(C=C,epsilon=ep,gamma=gm/X.shape[1]).fit(sx.transform(X),sy.transform(Y))
            pr=sy.inverse_transform(m.predict(sx.transform(te[1][None])))[0,0]
            e.append(abs(pr-te[2][0]))
        ranked.append((float(np.mean(e)),C,ep,gm))
    return sorted(ranked)

def run_msvr(wide,core):
    S=msvr_samples(wide,core); rank=tune_msvr(S); _,C,ep,gm=rank[0]; out={}
    for t in pd.date_range('2026-01-01','2026-07-01',freq='MS'):
        tr=[s for s in S if s[0]<t]; te=[s for s in S if s[0]==t][0]
        X=np.stack([s[1] for s in tr]); Y=np.stack([s[2] for s in tr])
        sx=StandardScaler().fit(X); sy=StandardScaler().fit(Y)
        m=MSVR(C=C,epsilon=ep,gamma=gm/X.shape[1]).fit(sx.transform(X),sy.transform(Y))
        rr=float(sy.inverse_transform(m.predict(sx.transform(te[1][None])))[0,0])
        p=t-pd.offsets.MonthBegin(1); out[t]=(float(core.loc[p,'gold_monthly'])*math.exp(rr),rr)
    return out,rank

# ---------- causal decomposition + patch Transformer (Axis 3 implementation) ----------
def causal_decomp(a,win=21):
    tr=np.zeros_like(a)
    for i in range(len(a)): tr[i]=a[max(0,i-win+1):i+1].mean(0)
    return np.concatenate([tr,a-tr],axis=1)

class PatchTransformer(nn.Module):
    def __init__(self,ch,patch,d=32):
        super().__init__(); self.patch=patch; self.stride=max(1,patch//2)
        self.emb=nn.Linear(patch*ch,d)
        lay=nn.TransformerEncoderLayer(d_model=d,nhead=4,dim_feedforward=4*d,dropout=.10,batch_first=True,activation='gelu',norm_first=True)
        self.enc=nn.TransformerEncoder(lay,2); self.conv=nn.Conv1d(d,d,3,padding=1)
        self.head=nn.Sequential(nn.Linear(d+5,64),nn.GELU(),nn.Dropout(.10),nn.Linear(64,1))
    def forward(self,x,m):
        p=x.unfold(1,self.patch,self.stride).permute(0,1,3,2).contiguous().flatten(2)
        z=self.enc(self.emb(p)); z=self.conv(z.transpose(1,2)).transpose(1,2).mean(1)
        return self.head(torch.cat([z,m],1)).squeeze(1)

def patch_samples(wide,core,L):
    r=np.log(wide[METALS]).diff().dropna(); out=[]
    for t in sorted(core.index):
        if t<pd.Timestamp('2011-03-01') or t>pd.Timestamp('2026-07-01'): continue
        p=t-pd.offsets.MonthBegin(1); pp=p-pd.offsets.MonthBegin(1)
        if p not in core.index or pp not in core.index: continue
        hist=r.loc[:t-pd.Timedelta(days=1)]
        if len(hist)<L: continue
        x=causal_decomp(hist.iloc[-L:].values.astype(np.float32),21).astype(np.float32)
        nas=float(np.log(core.loc[p,'nasdaq']/core.loc[pp,'nasdaq'])); fx=float(np.log(core.loc[p,'usdcny']/core.loc[pp,'usdcny']))
        ma=np.array([core.loc[p,'fedfunds'],nas,fx,np.log1p(core.loc[p,'gpr']),gpr_z(core,p)],np.float32)
        y=float(np.log(core.loc[t,'gold_monthly']/core.loc[p,'gold_monthly']))
        out.append((t,x,ma,y))
    return out

def norm_sets(tr,va):
    X=np.stack([s[1] for s in tr]); M=np.stack([s[2] for s in tr]); y=np.array([s[3] for s in tr],np.float32)
    xm=X.reshape(-1,X.shape[-1]).mean(0); xs=X.reshape(-1,X.shape[-1]).std(0)+1e-6
    mm=M.mean(0); ms=M.std(0)+1e-6; ym=float(y.mean()); ys=float(y.std()+1e-6)
    def f(s): return ((s[1]-xm)/xs,(s[2]-mm)/ms,np.float32((s[3]-ym)/ys))
    return [f(s) for s in tr],[f(s) for s in va],(xm,xs,mm,ms,ym,ys)

def fit_patch(tr,va,patch,d,seed,epochs=180):
    torch.manual_seed(seed); np.random.seed(seed)
    A,B,sc=norm_sets(tr,va); X=torch.tensor(np.stack([z[0] for z in A]),dtype=torch.float32); M=torch.tensor(np.stack([z[1] for z in A]),dtype=torch.float32); Y=torch.tensor(np.array([z[2] for z in A]),dtype=torch.float32)
    model=PatchTransformer(X.shape[-1],patch,d); opt=torch.optim.AdamW(model.parameters(),lr=1e-3,weight_decay=1e-4); lf=nn.HuberLoss()
    best=None; bv=1e99; bad=0
    for ep in range(epochs):
        model.train(); q=torch.randperm(len(X))
        for k in range(0,len(X),32):
            ix=q[k:k+32]; opt.zero_grad(); loss=lf(model(X[ix],M[ix]),Y[ix]); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step()
        if B:
            model.eval(); VX=torch.tensor(np.stack([z[0] for z in B]),dtype=torch.float32); VM=torch.tensor(np.stack([z[1] for z in B]),dtype=torch.float32); VY=torch.tensor(np.array([z[2] for z in B]),dtype=torch.float32)
            with torch.no_grad(): v=float(torch.mean(torch.abs(model(VX,VM)-VY)))
            if v<bv-1e-5: bv=v; best={k:v.detach().clone() for k,v in model.state_dict().items()}; bad=0
            else:
                bad+=1
                if bad>=30: break
    if best: model.load_state_dict(best)
    return model,sc,bv

def pred_patch(model,sc,s):
    xm,xs,mm,ms,ym,ys=sc; x=((s[1]-xm)/xs).astype(np.float32); m=((s[2]-mm)/ms).astype(np.float32)
    model.eval()
    with torch.no_grad(): z=float(model(torch.tensor(x[None]),torch.tensor(m[None])).item())
    return z*ys+ym

def tune_patch(wide,core):
    cfg=[(126,7,24),(126,14,32),(252,7,24),(252,14,32),(252,21,32)]; rank=[]
    for L,P,D in cfg:
        S=patch_samples(wide,core,L); tr=[s for s in S if s[0]<=pd.Timestamp('2023-12-01')]; va=[s for s in S if pd.Timestamp('2024-01-01')<=s[0]<=pd.Timestamp('2025-12-01')]
        mo,sc,_=fit_patch(tr,va,P,D,SEED+L+P,160); pr=np.array([pred_patch(mo,sc,s) for s in va]); yy=np.array([s[3] for s in va]); rank.append((float(np.mean(np.abs(pr-yy))),L,P,D))
    return sorted(rank)

def run_patch(wide,core):
    rank=tune_patch(wide,core); _,L,P,D=rank[0]; S=patch_samples(wide,core,L); out={}
    for t in pd.date_range('2026-01-01','2026-07-01',freq='MS'):
        trall=[s for s in S if s[0]<t]; te=[s for s in S if s[0]==t][0]; cut=max(36,int(len(trall)*.85)); tr=trall[:cut]; va=trall[cut:]; pp=[]
        for off in [0,101,202]:
            mo,sc,_=fit_patch(tr,va,P,D,SEED+off+t.month,200); pp.append(pred_patch(mo,sc,te))
        rr=float(np.median(pp)); p=t-pd.offsets.MonthBegin(1); out[t]=(float(core.loc[p,'gold_monthly'])*math.exp(rr),rr,pp)
    return out,rank

def metrics(res,col):
    e=res[col]-res.actual
    return {'MAPE':float(np.mean(np.abs(e)/res.actual)*100),'RMSE':float(np.sqrt(np.mean(e*e))),'MAE':float(np.mean(np.abs(e)))}

def main():
    core=load_core(); wide=fetch_history(); ms,msrank=run_msvr(wide,core); pt,ptrank=run_patch(wide,core)
    rows=[]
    for t in pd.date_range('2026-01-01','2026-07-01',freq='MS'):
        p=t-pd.offsets.MonthBegin(1); act=float(core.loc[t,'gold_monthly']); rw=float(core.loc[p,'gold_monthly']); h=core.loc[:p,'gold_monthly'].pct_change().dropna(); ma3=rw*(1+h.iloc[-3:].mean())
        mp=ms[t][0]; tp=pt[t][0]
        rows.append({'month':t.strftime('%Y-%m'),'actual':act,'rw':rw,'rw_ape':abs(rw-act)/act*100,'ma3':ma3,'ma3_ape':abs(ma3-act)/act*100,'vw_midas_msvr':mp,'vw_midas_msvr_ape':abs(mp-act)/act*100,'vw_midas_msvr_dir':int(np.sign(mp-rw)==np.sign(act-rw)),'axis3_patch_transformer':tp,'axis3_patch_transformer_ape':abs(tp-act)/act*100,'axis3_patch_transformer_dir':int(np.sign(tp-rw)==np.sign(act-rw))})
    res=pd.DataFrame(rows); res.to_csv(ROOT/'results_2026.csv',index=False,float_format='%.8f')
    s={'data_audit':{'start':str(wide.index.min().date()),'end':str(wide.index.max().date()),'rows':int(len(wide)),'source':'lbruton/StakTrakr spot-history; precious-metals rows provider LBMA'},'msvr_best':msrank[0],'msvr_rank':msrank,'axis3_best':ptrank[0],'axis3_rank':ptrank,'metrics':{'RW':metrics(res,'rw'),'MA3':metrics(res,'ma3'),'VW_MIDAS_MSVR':metrics(res,'vw_midas_msvr'),'AXIS3_PATCH_TRANSFORMER':metrics(res,'axis3_patch_transformer')}}
    s['metrics']['VW_MIDAS_MSVR']['direction_accuracy']=float(res.vw_midas_msvr_dir.mean()); s['metrics']['VW_MIDAS_MSVR']['months_beating_rw']=int((res.vw_midas_msvr_ape<res.rw_ape).sum()); s['metrics']['AXIS3_PATCH_TRANSFORMER']['direction_accuracy']=float(res.axis3_patch_transformer_dir.mean()); s['metrics']['AXIS3_PATCH_TRANSFORMER']['months_beating_rw']=int((res.axis3_patch_transformer_ape<res.rw_ape).sum())
    (ROOT/'summary_2026.json').write_text(json.dumps(s,indent=2,default=str)); print(res.to_string(index=False)); print(json.dumps(s,indent=2,default=str))

if __name__=='__main__': main()
