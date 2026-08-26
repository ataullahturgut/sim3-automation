import json, math
from pathlib import Path
import requests
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import run_models as rm

ROOT=Path(__file__).resolve().parent
METALS=rm.METALS
SEED=20260827
np.random.seed(SEED); torch.manual_seed(SEED); torch.set_num_threads(2)


def fetch_all():
    s=requests.Session(); rows=[]
    for y in range(2010,2027):
        u=f'https://raw.githubusercontent.com/lbruton/StakTrakr/main/data/spot-history-{y}.json'
        r=s.get(u,timeout=90); r.raise_for_status()
        for z in r.json():
            if z.get('metal') in METALS:
                d=pd.to_datetime(z['timestamp']).normalize()
                if d<=pd.Timestamp('2026-08-26'):
                    rows.append((d,z['metal'],float(z['spot'])))
    d=pd.DataFrame(rows,columns=['date','metal','spot']).drop_duplicates(['date','metal'],keep='last')
    return d.pivot(index='date',columns='metal',values='spot').sort_index()[METALS].dropna()


def macro_for_date(core,d):
    cm=pd.Timestamp(d.year,d.month,1)-pd.offsets.MonthBegin(1); pm=cm-pd.offsets.MonthBegin(1)
    if cm not in core.index or pm not in core.index: return None
    h=core.loc[:cm,'gpr'].dropna(); lo=float(h.min()); hi=float(h.max()); gz=.5 if hi<=lo else float((h.iloc[-1]-lo)/(hi-lo))
    return np.array([core.loc[cm,'fedfunds'],np.log(core.loc[cm,'nasdaq']/core.loc[pm,'nasdaq']),np.log(core.loc[cm,'usdcny']/core.loc[pm,'usdcny']),np.log1p(core.loc[cm,'gpr']),gz],np.float32)


def causal(a,win=21):
    tr=np.zeros_like(a)
    for i in range(len(a)): tr[i]=a[max(0,i-win+1):i+1].mean(0)
    return np.concatenate([tr,a-tr],axis=1)


def samples(wide,core,h,L=126):
    lr=np.log(wide[METALS]).diff().dropna(); dates=list(lr.index); pos={d:i for i,d in enumerate(wide.index)}; out=[]
    for j,d in enumerate(dates):
        wi=pos.get(d)
        if wi is None or wi+h>=len(wide) or j+1<L: continue
        ma=macro_for_date(core,d)
        if ma is None: continue
        x=causal(lr.iloc[j-L+1:j+1].values.astype(np.float32),21).astype(np.float32)
        y=float(np.log(wide.iloc[wi+h].Gold/wide.iloc[wi].Gold))
        out.append((d,x,ma,y,float(wide.iloc[wi].Gold),float(wide.iloc[wi+h].Gold),wide.index[wi+h]))
    return out


class DailyPatch(nn.Module):
    def __init__(self,ch=8,patch=7,d=24):
        super().__init__(); self.patch=patch; self.stride=max(1,patch//2)
        self.emb=nn.Linear(patch*ch,d)
        lay=nn.TransformerEncoderLayer(d_model=d,nhead=4,dim_feedforward=4*d,dropout=.1,batch_first=True,activation='gelu',norm_first=True)
        self.enc=nn.TransformerEncoder(lay,2); self.conv=nn.Conv1d(d,d,3,padding=1)
        self.head=nn.Sequential(nn.Linear(d+5,48),nn.GELU(),nn.Dropout(.1),nn.Linear(48,1))
    def forward(self,x,m):
        p=x.unfold(1,self.patch,self.stride).permute(0,1,3,2).contiguous().flatten(2)
        z=self.enc(self.emb(p)); z=self.conv(z.transpose(1,2)).transpose(1,2).mean(1)
        return self.head(torch.cat([z,m],1)).squeeze(1)


def normalize(tr):
    X=np.stack([s[1] for s in tr]); M=np.stack([s[2] for s in tr]); Y=np.array([s[3] for s in tr],np.float32)
    xm=X.reshape(-1,X.shape[-1]).mean(0); xs=X.reshape(-1,X.shape[-1]).std(0)+1e-6
    mm=M.mean(0); ms=M.std(0)+1e-6; ym=float(Y.mean()); ys=float(Y.std()+1e-6)
    return (xm,xs,mm,ms,ym,ys)


def arr(ss,sc):
    xm,xs,mm,ms,ym,ys=sc
    X=np.stack([(s[1]-xm)/xs for s in ss]).astype(np.float32); M=np.stack([(s[2]-mm)/ms for s in ss]).astype(np.float32); Y=np.array([(s[3]-ym)/ys for s in ss],np.float32)
    return torch.tensor(X),torch.tensor(M),torch.tensor(Y)


def fit_model(tr,va,h):
    torch.manual_seed(SEED+h); sc=normalize(tr); X,M,Y=arr(tr,sc); VX,VM,VY=arr(va,sc)
    model=DailyPatch(); opt=torch.optim.AdamW(model.parameters(),lr=8e-4,weight_decay=1e-4); lossf=nn.HuberLoss()
    best=None; bv=1e9; bad=0
    for ep in range(100):
        model.train(); q=torch.randperm(len(X))
        for k in range(0,len(X),64):
            ix=q[k:k+64]; opt.zero_grad(); loss=lossf(model(X[ix],M[ix]),Y[ix]); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step()
        model.eval()
        with torch.no_grad(): v=float(torch.mean(torch.abs(model(VX,VM)-VY)))
        if v<bv-1e-5: bv=v; best={k:v.detach().clone() for k,v in model.state_dict().items()}; bad=0
        else:
            bad+=1
            if bad>=18: break
    if best: model.load_state_dict(best)
    return model,sc,bv


def predict(model,sc,s):
    xm,xs,mm,ms,ym,ys=sc
    x=torch.tensor(((s[1]-xm)/xs)[None],dtype=torch.float32); m=torch.tensor(((s[2]-mm)/ms)[None],dtype=torch.float32)
    model.eval()
    with torch.no_grad(): z=float(model(x,m).item())
    return z*ys+ym


def eval_h(wide,core,h):
    S=samples(wide,core,h); tr=[s for s in S if s[0]<=pd.Timestamp('2024-12-31')]; va=[s for s in S if pd.Timestamp('2025-01-01')<=s[0]<=pd.Timestamp('2025-12-31')]
    # 2025 is historical at the 2026 test origin and used only for early stopping.
    model,sc,v=fit_model(tr,va,h)
    test=[s for s in S if pd.Timestamp('2026-01-01')<=s[0]<=pd.Timestamp('2026-08-26')]
    rows=[]
    for idx,s in enumerate(test):
        if idx%5!=0: continue
        rr=predict(model,sc,s); fp=s[4]*math.exp(rr); act=s[5]
        # 20-day daily momentum baseline, using returns only through origin
        wi=wide.index.get_loc(s[0]); hist=np.log(wide.Gold).diff().iloc[max(1,wi-19):wi+1].dropna(); mr=float(hist.mean()*h)
        mp=s[4]*math.exp(mr)
        rows.append({'h':h,'origin':s[0],'target_date':s[6],'origin_price':s[4],'actual':act,'patch':fp,'patch_ape':abs(fp-act)/act*100,
                     'rw':s[4],'rw_ape':abs(s[4]-act)/act*100,'momentum20':mp,'momentum20_ape':abs(mp-act)/act*100,
                     'actual_return':math.log(act/s[4]),'patch_return':rr,'patch_dir_hit':int(np.sign(rr)==np.sign(math.log(act/s[4]))),'val_mae_standardized':v})
    d=pd.DataFrame(rows)
    # non-overlap sample from the same chronological test set
    dn=d.iloc[::max(1,int(math.ceil(h/5)))].copy()
    def sm(x):
        return {'n':len(x),'patch_MAPE':float(x.patch_ape.mean()),'rw_MAPE':float(x.rw_ape.mean()),'momentum_MAPE':float(x.momentum20_ape.mean()),'patch_direction':float(x.patch_dir_hit.mean()*100)} if len(x) else {}
    aug=d[(d.origin>=pd.Timestamp('2026-07-20'))].copy()
    return d, {'h':h,'all_5day_origins':sm(d),'approximately_nonoverlap':sm(dn),'late_july_august':sm(aug),'max_data_date':str(wide.index.max().date())}


def main():
    core=rm.load_core(); wide=fetch_all(); print('daily max',wide.index.max(),flush=True)
    frames=[]; summaries=[]
    for h in [5,10,20,30]:
        print('HORIZON',h,flush=True); d,s=eval_h(wide,core,h); frames.append(d); summaries.append(s)
    out=pd.concat(frames,ignore_index=True); out.to_csv(ROOT/'axis3_short_horizon_diagnostic.csv',index=False)
    (ROOT/'axis3_short_horizon_summary.json').write_text(json.dumps(summaries,indent=2))
    print(json.dumps(summaries,indent=2),flush=True)
    print(out[out.origin>=pd.Timestamp('2026-07-20')].to_string(index=False),flush=True)

if __name__=='__main__': main()
