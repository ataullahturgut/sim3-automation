import os, io, json, math, hashlib, zipfile, copy, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import log_loss, roc_auc_score, average_precision_score

warnings.filterwarnings("ignore")

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=11166972412
OUT=Path(os.environ.get("OUT_DIR","stage3_seq_out"))
OUT.mkdir(parents=True,exist_ok=True)
ARCH=os.environ["ARCH"].upper()
LOOKBACK=int(os.environ["LOOKBACK"])
SEED=20261001
REFIT_BLOCK=20
BATCH=64
MAX_EPOCHS=30
PATIENCE=5
MIN_EPOCHS=5
FEATURES=[
    "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20",
    "silver_r1","silver_r5","silver_r21","silver_age_days",
    "platinum_r1","platinum_r5","platinum_r21","platinum_age_days"
]
VOL_CUTS=np.array([0.006485540146109267,0.008497615449687065],dtype=float)

torch.manual_seed(SEED)
np.random.seed(SEED)
torch.set_num_threads(2)
try:
    torch.use_deterministic_algorithms(True)
except Exception:
    pass

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"short-horizon-stage3"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_csv(z,suffix):
    names=[n for n in z.namelist() if n.endswith(suffix)]
    if len(names)!=1: raise RuntimeError((suffix,names))
    return pd.read_csv(io.BytesIO(z.read(names[0])))

def load_panel():
    z=get_zip(READINESS_ARTIFACT)
    df=read_csv(z,"short_horizon_readiness_panel.csv")
    df["date"]=pd.to_datetime(df["date"])
    df["signal_date"]=pd.to_datetime(df["signal_date"])
    return df.sort_values("date").reset_index(drop=True)

def maturity(df):
    return df["date"].shift(-3)

def qloss(y,p,q):
    e=y-p
    return torch.maximum(q*e,(q-1.0)*e).mean()

class TCNNet(nn.Module):
    def __init__(self,nf):
        super().__init__()
        self.c1=nn.Conv1d(nf,16,kernel_size=3,dilation=1)
        self.c2=nn.Conv1d(16,16,kernel_size=3,dilation=2)
        self.drop=nn.Dropout(0.10)
        self.head=nn.Linear(16,5)
    def forward(self,x):
        # x: B,T,F -> B,F,T
        x=x.transpose(1,2)
        x=F.pad(x,(2,0))
        x=self.drop(F.relu(self.c1(x)))
        x=F.pad(x,(4,0))
        x=self.drop(F.relu(self.c2(x)))
        h=x[:,:,-1]
        return self.head(h)

class GRUNet(nn.Module):
    def __init__(self,nf,bidir=False):
        super().__init__()
        hs=12 if bidir else 16
        self.gru=nn.GRU(nf,hs,batch_first=True,bidirectional=bidir)
        self.bidir=bidir
        self.head=nn.Linear(hs*(2 if bidir else 1),5)
    def forward(self,x):
        _,h=self.gru(x)
        if self.bidir:
            z=torch.cat([h[-2],h[-1]],dim=1)
        else:
            z=h[-1]
        return self.head(z)

def make_model(nf):
    if ARCH=="TCN": return TCNNet(nf)
    if ARCH=="GRU": return GRUNet(nf,False)
    if ARCH=="BIGRU": return GRUNet(nf,True)
    raise KeyError(ARCH)

def parameter_count(m):
    return int(sum(p.numel() for p in m.parameters() if p.requires_grad))

def build_sequences(df,sample_indices,med,mu,sd,ymean,ystd):
    xs=[]; yd=[]; yr=[]
    raw=df[FEATURES].copy()
    raw=raw.fillna(pd.Series(med,index=FEATURES))
    arr=((raw.to_numpy(float)-mu)/sd).astype(np.float32)
    y=df["target_r3"].to_numpy(float)
    for i in sample_indices:
        if i<LOOKBACK-1: continue
        xs.append(arr[i-LOOKBACK+1:i+1])
        yr.append((y[i]-ymean)/ystd)
        yd.append(1.0 if y[i]>0 else 0.0)
    return np.asarray(xs,np.float32),np.asarray(yd,np.float32),np.asarray(yr,np.float32)

def joint_loss(out,yd,yr):
    logit=out[:,0]
    rp=out[:,1]
    qs=out[:,2:5]
    bce=F.binary_cross_entropy_with_logits(logit,yd)
    mse=F.mse_loss(rp,yr)
    qv=(qloss(yr,qs[:,0],0.1)+qloss(yr,qs[:,1],0.5)+qloss(yr,qs[:,2],0.9))/3.0
    return bce+0.50*mse+0.50*qv

def fit_model(X,yd,yr):
    n=len(X)
    split=max(int(n*0.85),1)
    if n-split<20:
        split=max(n-20,1)
    Xtr,Xv=X[:split],X[split:]
    ydtr,ydv=yd[:split],yd[split:]
    yrtr,yrv=yr[:split],yr[split:]

    model=make_model(X.shape[2])
    opt=torch.optim.Adam(model.parameters(),lr=0.001,weight_decay=0.0001)
    ds=TensorDataset(torch.from_numpy(Xtr),torch.from_numpy(ydtr),torch.from_numpy(yrtr))
    g=torch.Generator(); g.manual_seed(SEED)
    dl=DataLoader(ds,batch_size=BATCH,shuffle=True,generator=g)

    xv=torch.from_numpy(Xv); ydv_t=torch.from_numpy(ydv); yrv_t=torch.from_numpy(yrv)
    best=None; bestloss=float("inf"); bad=0; epochs=0
    for ep in range(1,MAX_EPOCHS+1):
        model.train()
        for xb,ydb,yrb in dl:
            opt.zero_grad(set_to_none=True)
            out=model(xb)
            loss=joint_loss(out,ydb,yrb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(),5.0)
            opt.step()
        model.eval()
        with torch.no_grad():
            vl=float(joint_loss(model(xv),ydv_t,yrv_t).item()) if len(Xv) else 0.0
        epochs=ep
        if vl < bestloss-1e-6:
            bestloss=vl
            best=copy.deepcopy(model.state_dict())
            bad=0
        else:
            bad+=1
        if ep>=MIN_EPOCHS and bad>=PATIENCE:
            break
    if best is not None:
        model.load_state_dict(best)
    return model,epochs,bestloss

def metrics_direction(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    out={"n":len(y),"brier":float(np.mean((p-y)**2)),"logloss":float(log_loss(y,p,labels=[0,1])),"accuracy":float(np.mean((p>=0.5)==y))}
    try: out["roc_auc"]=float(roc_auc_score(y,p))
    except: out["roc_auc"]=None
    try: out["pr_auc"]=float(average_precision_score(y,p))
    except: out["pr_auc"]=None
    return out

def metrics_return(y,p):
    y=np.asarray(y,float); p=np.asarray(p,float); e=p-y
    return {"n":len(y),"mae":float(np.mean(np.abs(e))),"rmse":float(np.sqrt(np.mean(e**2))),"direction_accuracy":float(np.mean((p>0)==(y>0)))}

def pinball(y,p,q):
    e=np.asarray(y,float)-np.asarray(p,float)
    return float(np.mean(np.maximum(q*e,(q-1)*e)))

def main():
    df=load_panel()
    mat=maturity(df)
    dev_idx=df.index[(df["role"]=="DEV") & df["target_r3"].notna()].tolist()
    if len(dev_idx)!=749: raise RuntimeError(f"DEV {len(dev_idx)}")

    rows=[]; diagnostics=[]
    for s in range(0,len(dev_idx),REFIT_BLOCK):
        test_idx=dev_idx[s:s+REFIT_BLOCK]
        start=df.loc[test_idx[0],"date"]
        train_idx=df.index[
            mat.notna() & (mat<=start) & df["target_r3"].notna() & (df["signal_date"]<pd.Timestamp("2025-01-01"))
        ].tolist()
        train_idx=[i for i in train_idx if i>=LOOKBACK-1]
        if len(train_idx)<500: raise RuntimeError(f"train {len(train_idx)}")

        max_i=max(train_idx)
        hist=df.loc[:max_i,FEATURES]
        med=hist.median(skipna=True).fillna(0.0).to_numpy(float)
        filled=hist.fillna(pd.Series(med,index=FEATURES))
        mu=filled.mean().to_numpy(float)
        sd=filled.std(ddof=0).replace(0,1.0).fillna(1.0).to_numpy(float)

        ytrain=df.loc[train_idx,"target_r3"].to_numpy(float)
        ymean=float(np.mean(ytrain)); ystd=float(np.std(ytrain))
        if not np.isfinite(ystd) or ystd<1e-8: ystd=1.0

        X,yd,yr=build_sequences(df,train_idx,med,mu,sd,ymean,ystd)
        model,epochs,valloss=fit_model(X,yd,yr)
        pc=parameter_count(model)

        Xte,ydte,yrte=build_sequences(df,test_idx,med,mu,sd,ymean,ystd)
        model.eval()
        with torch.no_grad():
            out=model(torch.from_numpy(Xte)).numpy()
        pdir=1/(1+np.exp(-out[:,0]))
        pret=out[:,1]*ystd+ymean
        qraw=out[:,2:5]*ystd+ymean
        crossings=((qraw[:,0]>qraw[:,1]) | (qraw[:,1]>qraw[:,2])).astype(int)
        qsorted=np.sort(qraw,axis=1)

        for k,ix in enumerate(test_idx):
            sig=float(df.at[ix,"sigma20"])
            vb="LOW" if sig<=VOL_CUTS[0] else ("MID" if sig<=VOL_CUTS[1] else "HIGH")
            rows.append({
                "arch":ARCH,"lookback":LOOKBACK,"row_index":int(ix),
                "origin_date":str(df.at[ix,"date"].date()),"signal_date":str(df.at[ix,"signal_date"].date()),
                "year":int(df.at[ix,"signal_date"].year),"vol_bucket":vb,
                "y_return":float(df.at[ix,"target_r3"]),"y_up":int(df.at[ix,"target_r3"]>0),
                "p_up":float(pdir[k]),"return_pred":float(pret[k]),
                "q10":float(qsorted[k,0]),"q50":float(qsorted[k,1]),"q90":float(qsorted[k,2]),
                "quantile_cross_pre_repair":int(crossings[k]),
                "refit_block":s//REFIT_BLOCK
            })
        diagnostics.append({
            "arch":ARCH,"lookback":LOOKBACK,"refit_block":s//REFIT_BLOCK,
            "block_start":str(start.date()),"train_sequences":len(X),
            "epochs":epochs,"best_val_loss":valloss,"parameter_count":pc
        })
        print("BLOCK",s//REFIT_BLOCK,"train",len(X),"epochs",epochs,"val",valloss,flush=True)

    p=pd.DataFrame(rows)
    d=pd.DataFrame(diagnostics)
    p.to_csv(OUT/f"stage3_{ARCH.lower()}_l{LOOKBACK}_predictions.csv",index=False)
    d.to_csv(OUT/f"stage3_{ARCH.lower()}_l{LOOKBACK}_training.csv",index=False)

    # Aggregate metrics
    dm=metrics_direction(p["y_up"],p["p_up"])
    rm=metrics_return(p["y_return"],p["return_pred"])
    qms={q:pinball(p["y_return"],p[col],q) for q,col in [(0.1,"q10"),(0.5,"q50"),(0.9,"q90")]}
    summary={
        "arch":ARCH,"lookback":LOOKBACK,"n":len(p),
        "direction":dm,"return":rm,
        "quantile":{"q10":qms[0.1],"q50":qms[0.5],"q90":qms[0.9],"mean_pinball":float(np.mean(list(qms.values()))),
                    "coverage_q10":float((p["y_return"]<=p["q10"]).mean()),"coverage_q50":float((p["y_return"]<=p["q50"]).mean()),
                    "coverage_q90":float((p["y_return"]<=p["q90"]).mean()),"crossing_rate_pre_repair":float(p["quantile_cross_pre_repair"].mean())},
        "training":{"parameter_count":int(d["parameter_count"].iloc[0]),"mean_epochs":float(d["epochs"].mean()),"max_epochs_used":int(d["epochs"].max()),"refits":len(d)}
    }
    # slices
    years={}; vols={}
    for yr,z in p.groupby("year"):
        years[str(yr)]={
            "direction":metrics_direction(z["y_up"],z["p_up"]),
            "return":metrics_return(z["y_return"],z["return_pred"]),
            "quantile":{"mean_pinball":float(np.mean([pinball(z["y_return"],z[c],q) for q,c in [(0.1,"q10"),(0.5,"q50"),(0.9,"q90")]]))}
        }
    for vb,z in p.groupby("vol_bucket"):
        vols[str(vb)]={
            "direction":metrics_direction(z["y_up"],z["p_up"]),
            "return":metrics_return(z["y_return"],z["return_pred"]),
            "quantile":{"mean_pinball":float(np.mean([pinball(z["y_return"],z[c],q) for q,c in [(0.1,"q10"),(0.5,"q50"),(0.9,"q90")]]))}
        }
    summary["years"]=years; summary["volatility"]=vols
    (OUT/f"stage3_{ARCH.lower()}_l{LOOKBACK}_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("SEQ_SUMMARY="+json.dumps(summary,separators=(",",":")),flush=True)

if __name__=="__main__":
    main()
