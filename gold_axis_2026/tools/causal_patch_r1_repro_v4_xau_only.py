from __future__ import annotations

import base64
import gzip
import io
import json
import math
import os
import random
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import torch
import torch.nn as nn

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"patch_repro_v1"
CONTRACT=ROOT/"GOLD_CONTROL_CAUSAL_PATCH_R1_PROSPECTIVE_INPUT_BRIDGE_CONTRACT_V4.md"
SOURCE_EVIDENCE=OUT/"prospective_input_bridge_v4_source_evidence.json"
IDENTITY="CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE"
SEED=20260902
L=252; P=21; D=32
LOCKED_START=pd.Timestamp("2023-01-01"); LOCKED_END=pd.Timestamp("2026-07-01")
TWELVE_URL="https://api.twelvedata.com/time_series"
FRED_URL="https://api.stlouisfed.org/fred/series/observations"


def seed_all(seed:int):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.set_num_threads(1)
    try: torch.use_deterministic_algorithms(True)
    except Exception: pass


def key(name):
    v=os.environ.get(name,"").strip()
    if not v: raise RuntimeError(f"{name}_NOT_SET")
    return v


def load_core():
    raw=gzip.decompress(base64.b64decode((ROOT/"core5_monthly.csv.gz.b64").read_text().strip())).decode()
    return pd.read_csv(io.StringIO(raw),parse_dates=["date"]).set_index("date").sort_index()


def get_json(url,params,headers=None):
    r=requests.get(url,params=params,headers=headers or {},timeout=(20,180)); r.raise_for_status(); p=r.json()
    if isinstance(p,dict) and p.get("status")=="error": raise RuntimeError(f"PROVIDER_ERROR:{p.get('code')}:{p.get('message')}")
    return p


def fetch_xau():
    p=get_json(TWELVE_URL,{"symbol":"XAU/USD","interval":"1day","start_date":"2010-01-01","end_date":"2026-08-31","outputsize":5000,"order":"ASC","format":"JSON"},{"Authorization":f"apikey {key('TWELVE_DATA_API_KEY')}","User-Agent":"Gold-Control-Patch-V4-Model-Impact/1.0"})
    rows=[]
    for z in p.get("values") or []:
        try:d=pd.Timestamp(str(z.get("datetime"))).normalize(); v=float(z.get("close"))
        except Exception:continue
        if np.isfinite(v) and v>0:rows.append((d,v))
    d=pd.DataFrame(rows,columns=["date","Gold"]).sort_values("date")
    if d.empty or d.duplicated("date").any(): raise RuntimeError("XAU_HISTORY_INVALID")
    return d.set_index("date")


def fetch_nasdaq_monthly():
    p=get_json(FRED_URL,{"series_id":"NASDAQCOM","api_key":key("FRED_API_KEY"),"file_type":"json","observation_start":"2010-01-01","observation_end":"2026-08-31","sort_order":"asc","limit":100000},{"User-Agent":"Gold-Control-Patch-V4-Model-Impact/1.0"})
    rows=[]
    for z in p.get("observations") or []:
        sv=str(z.get("value","."))
        if sv in {".","","nan","None"}:continue
        try:d=pd.Timestamp(str(z.get("date"))).normalize();v=float(sv)
        except Exception:continue
        if np.isfinite(v) and v>0:rows.append((d,v))
    d=pd.DataFrame(rows,columns=["date","v"]).sort_values("date")
    if d.empty or d.duplicated("date").any():raise RuntimeError("NASDAQ_HISTORY_INVALID")
    return d.set_index("date")["v"].resample("MS").mean().dropna()


def gpr_z_asof(core,asof_month):
    h=core.loc[:asof_month,"gpr"].dropna().astype(float)
    if h.empty:return 0.5
    lo,hi=float(h.min()),float(h.max())
    return 0.5 if hi<=lo else float((h.iloc[-1]-lo)/(hi-lo))


def causal_decomp(a,win=21):
    tr=np.zeros_like(a)
    for i in range(len(a)):tr[i]=a[max(0,i-win+1):i+1].mean(0)
    return np.concatenate([tr,a-tr],axis=1)


class PatchTransformer(nn.Module):
    def __init__(self,ch,patch,d):
        super().__init__();self.patch=patch;self.stride=max(1,patch//2);self.emb=nn.Linear(patch*ch,d)
        layer=nn.TransformerEncoderLayer(d_model=d,nhead=4,dim_feedforward=4*d,dropout=0.10,batch_first=True,activation="gelu",norm_first=True)
        self.enc=nn.TransformerEncoder(layer,2);self.conv=nn.Conv1d(d,d,3,padding=1);self.head=nn.Sequential(nn.Linear(d+5,64),nn.GELU(),nn.Dropout(0.10),nn.Linear(64,1))
    def forward(self,x,m):
        p=x.unfold(1,self.patch,self.stride).permute(0,1,3,2).contiguous().flatten(2);z=self.enc(self.emb(p));z=self.conv(z.transpose(1,2)).transpose(1,2).mean(1);return self.head(torch.cat([z,m],1)).squeeze(1)


def build_samples(xau,core,nas_monthly):
    r=np.log(xau[["Gold"]]).diff().dropna();out=[];future_viol=0
    for t in sorted(core.index):
        if t<pd.Timestamp("2011-03-01") or t>LOCKED_END:continue
        p=t-pd.offsets.MonthBegin(1); pp=p-pd.offsets.MonthBegin(1); ppp=p-pd.offsets.MonthBegin(2)
        if any(q not in core.index for q in [p,pp]) or pp not in nas_monthly.index or ppp not in nas_monthly.index:continue
        origin_end=t-pd.Timedelta(days=1);hist=r.loc[:origin_end]
        if len(hist)<L:continue
        if hist.index.max()>origin_end:future_viol+=1
        x=causal_decomp(hist.iloc[-L:].values.astype(np.float32),21).astype(np.float32)
        # V3 origin-safe NASDAQ: only two fully completed pre-origin months.
        nas=float(np.log(float(nas_monthly.loc[pp])/float(nas_monthly.loc[ppp])))
        fx=float(np.log(float(core.loc[p,"usdcny"])/float(core.loc[pp,"usdcny"])))
        gpr=float(core.loc[pp,"gpr"])
        macro=np.array([float(core.loc[p,"fedfunds"]),nas,fx,np.log1p(gpr),gpr_z_asof(core,pp)],dtype=np.float32)
        y=float(np.log(float(core.loc[t,"gold_monthly"])/float(core.loc[p,"gold_monthly"])))
        out.append((t,x,macro,y))
    return out,future_viol


def normalize_sets(tr,va):
    X=np.stack([s[1] for s in tr]);M=np.stack([s[2] for s in tr]);y=np.array([s[3] for s in tr],np.float32)
    xm=X.reshape(-1,X.shape[-1]).mean(0);xs=X.reshape(-1,X.shape[-1]).std(0)+1e-6;mm=M.mean(0);ms=M.std(0)+1e-6;ym=float(y.mean());ys=float(y.std()+1e-6)
    def f(s):return ((s[1]-xm)/xs,(s[2]-mm)/ms,np.float32((s[3]-ym)/ys))
    return [f(s) for s in tr],[f(s) for s in va],(xm,xs,mm,ms,ym,ys)


def fit_patch(tr,va,seed,epochs=140):
    seed_all(seed);A,B,sc=normalize_sets(tr,va);X=torch.tensor(np.stack([z[0] for z in A]),dtype=torch.float32);M=torch.tensor(np.stack([z[1] for z in A]),dtype=torch.float32);Y=torch.tensor(np.array([z[2] for z in A]),dtype=torch.float32)
    model=PatchTransformer(X.shape[-1],P,D);opt=torch.optim.AdamW(model.parameters(),lr=1e-3,weight_decay=1e-4);loss_fn=nn.HuberLoss();best,best_v,bad=None,1e99,0
    for _ in range(epochs):
        model.train();q=torch.randperm(len(X))
        for k in range(0,len(X),32):
            ix=q[k:k+32];opt.zero_grad();loss=loss_fn(model(X[ix],M[ix]),Y[ix]);loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step()
        if B:
            model.eval();VX=torch.tensor(np.stack([z[0] for z in B]),dtype=torch.float32);VM=torch.tensor(np.stack([z[1] for z in B]),dtype=torch.float32);VY=torch.tensor(np.array([z[2] for z in B]),dtype=torch.float32)
            with torch.no_grad():v=float(torch.mean(torch.abs(model(VX,VM)-VY)))
            if v<best_v-1e-5:best_v=v;best={k:v.detach().clone() for k,v in model.state_dict().items()};bad=0
            else:
                bad+=1
                if bad>=24:break
    if best:model.load_state_dict(best)
    return model,sc


def predict(model,sc,s):
    xm,xs,mm,ms,ym,ys=sc;x=((s[1]-xm)/xs).astype(np.float32);m=((s[2]-mm)/ms).astype(np.float32);model.eval()
    with torch.no_grad():z=float(model(torch.tensor(x[None]),torch.tensor(m[None])).item())
    return z*ys+ym


def locked_predictions(core,xau,nas):
    S,future_viol=build_samples(xau,core,nas);out=[]
    for t in pd.date_range(LOCKED_START,LOCKED_END,freq="MS"):
        trall=[s for s in S if s[0]<t];te=[s for s in S if s[0]==t]
        if len(te)!=1:raise RuntimeError(f"TARGET_SAMPLE_MISSING:{t.date()}")
        cut=max(48,int(len(trall)*0.85));cut=min(cut,len(trall)-12);tr,va=trall[:cut],trall[cut:]
        if len(tr)<48 or len(va)<12:raise RuntimeError(f"TRAIN_VALID_SPLIT_INVALID:{t.date()}:{len(tr)}:{len(va)}")
        rr=[]
        for off in [0,101,202]:
            model,sc=fit_patch(tr,va,SEED+off+int(t.strftime("%Y%m")),140);rr.append(predict(model,sc,te[0]))
        ret=float(np.median(rr));p=t-pd.offsets.MonthBegin(1);forecast=float(core.loc[p,"gold_monthly"])*math.exp(ret);out.append((t.strftime("%Y-%m"),forecast,ret))
    return pd.DataFrame(out,columns=["month","patch_v4","predicted_log_return"]),future_viol


def metrics(actual,pred):
    a=np.asarray(actual,float);p=np.asarray(pred,float);e=p-a
    return {"MAE":float(np.mean(np.abs(e))),"MAPE_pct":float(np.mean(np.abs(e)/a)*100),"median_APE_pct":float(np.median(np.abs(e)/a)*100),"worst_APE_pct":float(np.max(np.abs(e)/a)*100),"RMSE":float(np.sqrt(np.mean(e*e)))}


def main():
    ctext=CONTRACT.read_text(encoding="utf-8")
    if "FROZEN_BEFORE_V4_SOURCE_RESULT" not in ctext or "CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE" not in ctext:raise RuntimeError("V4_CONTRACT_NOT_FROZEN")
    se=json.loads(SOURCE_EVIDENCE.read_text(encoding="utf-8"))
    if not se.get("source_bridge_pass"):raise RuntimeError("V4_SOURCE_GATE_NOT_PASS")
    gp=json.loads((OUT/"frozen_geometry.json").read_text(encoding="utf-8"))["selected_pre_2023_geometry"]
    if (int(gp["L"]),int(gp["P"]),int(gp["D"]))!=(L,P,D):raise RuntimeError(f"FROZEN_GEOMETRY_MISMATCH:{gp}")
    core=load_core();xau=fetch_xau();nas=fetch_nasdaq_monthly()
    a,fv1=locked_predictions(core,xau,nas);b,fv2=locked_predictions(core,xau,nas)
    maxdiff=float(np.max(np.abs(a.patch_v4.to_numpy()-b.patch_v4.to_numpy())))
    ref=pd.read_csv(ROOT/"production_closure"/"production_history_43.csv")
    if len(ref)!=43:raise RuntimeError("REFERENCE_N_NOT_43")
    z=ref.merge(a,on="month",how="inner")
    if len(z)!=43:raise RuntimeError(f"COMMON_N_NOT_43:{len(z)}")
    target_ok=0;rw_ok=0
    for _,row in z.iterrows():
        t=pd.Timestamp(row["month"]+"-01");p=t-pd.offsets.MonthBegin(1);target_ok+=int(abs(float(core.loc[t,"gold_monthly"])-float(row["actual"]))<=1e-9);rw_ok+=int(abs(float(core.loc[p,"gold_monthly"])-float(row["rw"]))<=1e-9)
    mv4=metrics(z.actual,z.patch_v4);mrw=metrics(z.actual,z.rw);march=metrics(z.actual,z.patch_r1);mvw=metrics(z.actual,z.vw)
    hard=bool(target_ok==43 and rw_ok==43 and maxdiff<=1e-8 and fv1==0 and fv2==0)
    perf=bool(mv4["MAPE_pct"]<mrw["MAPE_pct"] and mv4["MAE"]<mrw["MAE"] and mv4["worst_APE_pct"]<=1.25*mrw["worst_APE_pct"])
    passed=bool(hard and perf)
    decision="PATCH_R1_V4_XAU_ONLY_MODEL_IMPACT_PASS" if passed else "PATCH_R1_V4_XAU_ONLY_MODEL_IMPACT_FAIL_NO_RETUNE"
    z["patch_v4_ape"]=np.abs(z.patch_v4-z.actual)/z.actual*100;z.to_csv(OUT/"locked_replay_v4_xau_only_43.csv",index=False)
    e={"candidate_id":IDENTITY,"parent_architecture":"CAUSAL_PATCH_R1_REPRO_V1","evidence_class":"HISTORICAL_REPLAY_MODEL_IMPACT","prospective_claim":False,"source_gate":"PATCH_PROSPECTIVE_INPUT_BRIDGE_V4_SOURCE_PASS","daily_channels":["XAU"],"omitted_not_imputed":["XAG","XPT","XPD"],"geometry":{"L":L,"P":P,"D":D},"geometry_reselected":False,"locked_window":"2023-01..2026-07","N":43,"target_reconciliation":f"{target_ok}/43","rw_reconciliation":f"{rw_ok}/43","future_information_violations":int(fv1+fv2),"deterministic_max_abs_diff":maxdiff,"candidate_metrics":mv4,"rw_metrics":mrw,"archived_patch_reference_metrics":march,"vw_audited_reference_metrics":mvw,"worst_ape_ratio_vs_rw":float(mv4["worst_APE_pct"]/mrw["worst_APE_pct"]),"hard_gate_pass":hard,"performance_gate_pass":perf,"model_impact_pass":passed,"decision":decision,"post_result_retune":False,"forecast_ledger_write":"NONE","decision_store_write":"NONE","database_write":"NONE","raw_vendor_market_values_logged":False}
    (OUT/"locked_replay_v4_xau_only_evidence.json").write_text(json.dumps(e,indent=2),encoding="utf-8")
    print(f"V4_TARGET_RECONCILIATION={target_ok}/43");print(f"V4_RW_RECONCILIATION={rw_ok}/43");print(f"V4_DETERMINISTIC_MAX_ABS_DIFF={maxdiff:.12g}");print(f"V4_FUTURE_INFORMATION_VIOLATIONS={fv1+fv2}")
    print(f"V4_MAPE_PCT={mv4['MAPE_pct']:.9f}");print(f"RW_MAPE_PCT={mrw['MAPE_pct']:.9f}");print(f"V4_MAE={mv4['MAE']:.9f}");print(f"RW_MAE={mrw['MAE']:.9f}");print(f"V4_WORST_APE_PCT={mv4['worst_APE_pct']:.9f}");print(f"RW_WORST_APE_PCT={mrw['worst_APE_pct']:.9f}");print(f"V4_WORST_APE_RATIO_VS_RW={mv4['worst_APE_pct']/mrw['worst_APE_pct']:.9f}")
    print(f"V4_HARD_GATE_PASS={str(hard).lower()}");print(f"V4_PERFORMANCE_GATE_PASS={str(perf).lower()}");print(f"V4_MODEL_IMPACT_PASS={str(passed).lower()}");print(f"V4_DECISION={decision}");print("GEOMETRY_RESELECTED=NO");print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO");print("DATABASE_WRITES=NONE");print("FORECAST_LEDGER_WRITE=NONE");print("DECISION_STORE_WRITE=NONE")

if __name__=="__main__":seed_all(SEED);main()
