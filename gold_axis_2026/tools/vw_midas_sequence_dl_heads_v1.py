from __future__ import annotations

import json, math, os, random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

import vw_midas_msvr_successor_v1 as base

DEV_START, DEV_END = "2022-04", "2024-12"
TR_START, TR_END = "2025-01", "2025-12"
ST_START, ST_END = "2026-01", "2026-07"
torch.set_default_dtype(torch.float64)
torch.set_num_threads(1)

class RNNHead(nn.Module):
    def __init__(self, kind, hidden):
        super().__init__()
        cls=nn.GRU if kind=="GRU" else nn.LSTM
        self.rnn=cls(input_size=8,hidden_size=hidden,num_layers=1,batch_first=True)
        self.out=nn.Linear(hidden,4)
    def forward(self,x):
        y,_=self.rnn(x)
        return self.out(y[:,-1,:])

class TCNHead(nn.Module):
    def __init__(self, hidden):
        super().__init__()
        self.c1=nn.Conv1d(8,hidden,kernel_size=2,dilation=1,padding=1)
        self.c2=nn.Conv1d(hidden,hidden,kernel_size=2,dilation=2,padding=2)
        self.out=nn.Linear(hidden,4)
    def forward(self,x):
        z=x.transpose(1,2)
        z=torch.tanh(self.c1(z))[:,:,:x.shape[1]]
        z=torch.tanh(self.c2(z))[:,:,:x.shape[1]]
        return self.out(z[:,:,-1])

def seq_for(samples,target,L):
    months=[base.month_shift(target,-i) for i in range(L-1,-1,-1)]
    if any(m not in samples for m in months): return None
    return np.stack([samples[m][0] for m in months])

def dataset(samples,target,L):
    keys=[]
    X=[]; Y=[]
    for k in sorted(k for k in samples if k<target):
        s=seq_for(samples,k,L)
        if s is None: continue
        keys.append(k); X.append(s); Y.append(samples[k][1])
    tx=seq_for(samples,target,L)
    if tx is None: raise RuntimeError(f"TARGET_SEQUENCE_MISSING {target} L={L}")
    if len(keys)<24: raise RuntimeError(f"TRAIN_SEQUENCE_TOO_SMALL {target} L={L} n={len(keys)}")
    X=np.stack(X); Y=np.stack(Y)
    xm=X.reshape(-1,8).mean(0); xs=X.reshape(-1,8).std(0)
    ym=Y.mean(0); ys=Y.std(0)
    xs=np.where(xs<1e-9,1.0,xs); ys=np.where(ys<1e-9,1.0,ys)
    Xs=(X-xm[None,None,:])/xs[None,None,:]
    txs=(tx-xm[None,:])/xs[None,:]
    Ys=(Y-ym)/ys
    return keys,Xs,Ys,txs[None,:,:],ym,ys

def make_model(kind,hidden):
    return TCNHead(hidden) if kind=="TCN" else RNNHead(kind,hidden)

def fit_predict(samples,target,spec):
    kind,L,hidden,wd=spec
    keys,X,Y,tx,ym,ys=dataset(samples,target,L)
    seed=9107 + sum(ord(c) for c in target) + L*13 + hidden*7 + {"GRU":1,"LSTM":2,"TCN":3}[kind]
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    model=make_model(kind,hidden)
    opt=torch.optim.AdamW(model.parameters(),lr=0.02,weight_decay=wd)
    lossfn=nn.MSELoss()
    Xt=torch.tensor(X); Yt=torch.tensor(Y); txt=torch.tensor(tx)
    best=float("inf"); best_state=None; stale=0
    for epoch in range(350):
        model.train(); opt.zero_grad()
        loss=lossfn(model(Xt),Yt)
        if not torch.isfinite(loss): raise RuntimeError(f"NONFINITE_LOSS {target} {spec}")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
        opt.step()
        lv=float(loss.detach())
        if lv < best-1e-6:
            best=lv; best_state={k:v.detach().clone() for k,v in model.state_dict().items()}; stale=0
        else:
            stale+=1
        if stale>=50 and epoch>=100: break
    if best_state is not None: model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad(): pz=model(txt).cpu().numpy()[0]
    return pz*ys+ym,len(keys),best

def make_row(b,t,pred,n,best,spec):
    p=base.month_shift(t,-1)
    return {"target":t,"origin":p,"spec":[spec[0],spec[1],spec[2],spec[3]],
            "train_rows":n,"train_loss":best,
            "pred_log_return_gold":float(pred[0]),
            "forecast":float(b.core_gold[p]*math.exp(float(pred[0]))),
            "actual":float(b.core_gold[t]),"rw":float(b.core_gold[p])}

def eval_spec(b,cache,spec,a,z):
    rows=[]; errs=[]
    for t in base.month_range(a,z):
        pred,n,best=fit_predict(cache[t],t,spec)
        rows.append(make_row(b,t,pred,n,best,spec))
        p=base.month_shift(t,-1)
        ar=math.log(b.monthly_metal["Gold"][t]/b.monthly_metal["Gold"][p])
        errs.append(abs(float(pred[0])-ar))
    return float(np.mean(errs)),rows

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    b=base.load_data(dsn)
    cache={t:base.all_samples_at_origin(b,t,governed=True) for t in base.month_range(DEV_START,ST_END)}

    # Deliberately small architecture grid for low-N data. All selection pre-2025.
    specs=[(kind,L,8,0.10) for kind in ("GRU","LSTM","TCN") for L in (6,12)]
    cand=[]; saved={}
    for spec in specs:
        obj,rows=eval_spec(b,cache,spec,DEV_START,DEV_END)
        saved[spec]=rows
        cand.append({"spec":list(spec),"dev_logret_mae":obj,"dev_metrics":base.metrics(rows)})
    cand.sort(key=lambda x:(x["dev_logret_mae"],str(x["spec"])))
    sb=cand[0]["spec"]; best=(sb[0],int(sb[1]),int(sb[2]),float(sb[3])); dev=saved[best]
    _,tr=eval_spec(b,cache,best,TR_START,TR_END)
    _,st=eval_spec(b,cache,best,ST_START,ST_END)

    # Also report every architecture on 2025/2026 without using those periods for selection.
    all_specs={}
    for rec in cand:
        s=rec["spec"]; spec=(s[0],int(s[1]),int(s[2]),float(s[3]))
        _,tr0=eval_spec(b,cache,spec,TR_START,TR_END)
        _,st0=eval_spec(b,cache,spec,ST_START,ST_END)
        all_specs[str(spec)]={
            "dev":rec["dev_metrics"],
            "transport_2025":base.metrics(tr0),
            "stress_2026":base.metrics(st0),
        }

    out={
        "model_id":"VW_MIDAS_SEQUENCE_DL_HEADS_V1",
        "authority":{
            "database_access":"READ_ONLY","feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
            "sequence_inputs":"ONLY_ORIGIN_SAFE_VW_MIDAS_X_HISTORY",
            "selection_period":f"{DEV_START}..{DEV_END}","random_split":"NONE",
            "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION","2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION"
        },
        "candidate_selection":cand,"selected_spec":list(best),
        "selected_result":{
            "dev":{"metrics":base.metrics(dev),"yearly":base.yearly(dev),"rows":dev},
            "transport_2025":{"metrics":base.metrics(tr),"rows":tr},
            "stress_2026":{"metrics":base.metrics(st),"rows":st},
        },
        "all_specs_fixed_after_pre2025_design":all_specs,
    }
    Path("vw_midas_sequence_dl_heads_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "selected_spec":out["selected_spec"],
        "selected_dev":out["selected_result"]["dev"]["metrics"],
        "selected_2025":out["selected_result"]["transport_2025"]["metrics"],
        "selected_2026":out["selected_result"]["stress_2026"]["metrics"],
        "all_specs":all_specs
    },sort_keys=True))

if __name__=="__main__": main()
