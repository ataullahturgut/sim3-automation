import os, io, json, math, hashlib, zipfile, warnings, shutil
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import torch
import lightning.pytorch as pl
from lightning.pytorch.callbacks import EarlyStopping, ModelCheckpoint

from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
from pytorch_forecasting.metrics import QuantileLoss, CrossEntropy, MultiLoss

warnings.filterwarnings("ignore")

REPO="ataullahturgut/sim3-automation"
READINESS_ARTIFACT=11166972412
TASK=os.environ["TASK"].lower()
OUT=Path(os.environ.get("OUT_DIR",f"stage4_tft_{TASK}"))
OUT.mkdir(parents=True,exist_ok=True)

SEED=20261001
LOOKBACK=60
REFIT_BLOCK=63
BATCH=64
MAX_EPOCHS=20
FEATURES=[
    "gold_r1","gold_r3","gold_r5","gold_r10","gold_r21","sigma20",
    "silver_r1","silver_r5","silver_r21","silver_age_days",
    "platinum_r1","platinum_r5","platinum_r21","platinum_age_days"
]
RET_TARGETS=["target_r1","target_r3","target_r5"]
UP_TARGETS=["up1","up3","up5"]
QUANTILES=[0.1,0.5,0.9]
VOL_CUTS=np.array([0.006485540146109267,0.008497615449687065],dtype=float)

pl.seed_everything(SEED,workers=True)
torch.set_num_threads(2)
try:
    torch.use_deterministic_algorithms(True,warn_only=True)
except Exception:
    pass

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"short-horizon-stage4-tft"},timeout=120)
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
    df=df.sort_values("date").reset_index(drop=True)
    df["time_idx"]=np.arange(len(df),dtype=int)
    df["series"]="GOLD"
    for h in [1,3,5]:
        df[f"up{h}"]=np.where(df[f"target_r{h}"].notna(),np.where(df[f"target_r{h}"]>0,"UP","DOWN"),None)
    return df

def fill_features(df, med):
    q=df.copy()
    for c,v in zip(FEATURES,med):
        q[c]=q[c].fillna(float(v))
    return q

def create_dataset(data, targets, min_pred_idx=None, template=None):
    kwargs=dict(
        time_idx="time_idx",
        target=targets,
        group_ids=["series"],
        min_encoder_length=LOOKBACK,
        max_encoder_length=LOOKBACK,
        min_prediction_length=1,
        max_prediction_length=1,
        time_varying_known_reals=["time_idx"]+FEATURES,
        add_relative_time_idx=False,
        add_target_scales=False,
        add_encoder_length=False,
        randomize_length=None,
        allow_missing_timesteps=False,
    )
    if template is None:
        return TimeSeriesDataSet(data,**kwargs)
    return TimeSeriesDataSet.from_dataset(
        template,data,min_prediction_idx=min_pred_idx,
        stop_randomization=True,predict=False
    )

def model_for(ds):
    common=dict(
        learning_rate=0.001,
        hidden_size=8,
        attention_head_size=1,
        dropout=0.10,
        hidden_continuous_size=4,
        lstm_layers=1,
        causal_attention=True,
        share_single_variable_networks=False,
        optimizer="adamw",
        weight_decay=0.0001,
        reduce_on_plateau_patience=3,
        log_interval=-1,
        log_val_interval=-1,
    )
    if TASK=="class":
        loss=MultiLoss([CrossEntropy(),CrossEntropy(),CrossEntropy()])
        return TemporalFusionTransformer.from_dataset(ds,loss=loss,output_size=[2,2,2],**common)
    elif TASK=="quant":
        loss=MultiLoss([QuantileLoss(quantiles=QUANTILES),QuantileLoss(quantiles=QUANTILES),QuantileLoss(quantiles=QUANTILES)])
        return TemporalFusionTransformer.from_dataset(ds,loss=loss,output_size=[3,3,3],**common)
    else:
        raise KeyError(TASK)

def param_count(model):
    return int(sum(p.numel() for p in model.parameters() if p.requires_grad))

def class_up_indices(ds):
    out=[]
    norms=ds.target_normalizers
    for n in norms:
        classes=getattr(n,"classes_",None)
        if isinstance(classes,dict):
            out.append(int(classes["UP"]))
        elif classes is not None:
            vals=list(classes)
            out.append(vals.index("UP"))
        else:
            raise RuntimeError(f"No classes_ on normalizer {n}")
    return out

def predict_block(model,dl,up_idx=None):
    model.eval()
    tids=[]; preds=[]
    with torch.no_grad():
        for x,y in dl:
            out=model(x)
            pp=out["prediction"]
            tids.extend(x["decoder_time_idx"][:,0].cpu().numpy().astype(int).tolist())
            if TASK=="class":
                arr=[]
                for k,t in enumerate(pp):
                    prob=torch.softmax(t[:,0,:],dim=-1)[:,up_idx[k]]
                    arr.append(prob.cpu().numpy())
                preds.append(np.stack(arr,axis=1))
            else:
                arr=[]
                for t in pp:
                    arr.append(t[:,0,:].cpu().numpy())
                preds.append(np.stack(arr,axis=1))  # B, 3 horizons, 3 quantiles
    return np.asarray(tids,int),np.concatenate(preds,axis=0)

def metric_direction(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    return {
        "n":int(len(y)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p))),
        "accuracy":float(np.mean((p>=0.5)==y)),
        "prediction_std":float(np.std(p))
    }

def pinball(y,p,q):
    e=np.asarray(y,float)-np.asarray(p,float)
    return float(np.mean(np.maximum(q*e,(q-1)*e)))

def metric_quant(y,q10,q50,q90):
    y=np.asarray(y,float)
    qs=[np.asarray(q10,float),np.asarray(q50,float),np.asarray(q90,float)]
    pins=[pinball(y,qs[i],QUANTILES[i]) for i in range(3)]
    return {
        "n":int(len(y)),
        "mae_q50":float(np.mean(np.abs(qs[1]-y))),
        "rmse_q50":float(np.sqrt(np.mean((qs[1]-y)**2))),
        "mean_pinball":float(np.mean(pins)),
        "pinball_q10":pins[0],"pinball_q50":pins[1],"pinball_q90":pins[2],
        "coverage_q10":float(np.mean(y<=qs[0])),
        "coverage_q50":float(np.mean(y<=qs[1])),
        "coverage_q90":float(np.mean(y<=qs[2])),
        "crossing_rate":float(np.mean((qs[0]>qs[1])|(qs[1]>qs[2]))),
        "prediction_std_q50":float(np.std(qs[1]))
    }

def main():
    df=load_panel()
    targets=UP_TARGETS if TASK=="class" else RET_TARGETS
    dev_idx=df.index[(df["role"]=="DEV") & df["target_r1"].notna() & df["target_r3"].notna() & df["target_r5"].notna()].tolist()
    if len(dev_idx)!=749:
        raise RuntimeError(f"Expected 749 DEV rows, got {len(dev_idx)}")

    maturity5=df["date"].shift(-5)
    all_rows=[]; diagnostics=[]

    work=OUT/"checkpoints"
    if work.exists(): shutil.rmtree(work)
    work.mkdir(parents=True,exist_ok=True)

    for bstart in range(0,len(dev_idx),REFIT_BLOCK):
        test_idx=dev_idx[bstart:bstart+REFIT_BLOCK]
        start_date=df.loc[test_idx[0],"date"]
        train_pool=df.index[
            maturity5.notna() & (maturity5<=start_date) &
            df["target_r1"].notna() & df["target_r3"].notna() & df["target_r5"].notna() &
            (df["signal_date"]<pd.Timestamp("2025-01-01"))
        ].tolist()
        train_pool=[i for i in train_pool if i>=LOOKBACK]
        if len(train_pool)<700:
            raise RuntimeError(f"Too few matured train rows {len(train_pool)}")

        split=max(int(len(train_pool)*0.85),LOOKBACK+20)
        sub_idx=train_pool[:split]
        val_idx=train_pool[split:]
        if len(val_idx)<40:
            raise RuntimeError(f"Too few validation rows {len(val_idx)}")

        med=df.loc[sub_idx,FEATURES].median(skipna=True).fillna(0.0).to_numpy(float)
        filled=fill_features(df,med)

        train_end=sub_idx[-1]
        val_start=val_idx[0]
        val_end=val_idx[-1]
        test_start=test_idx[0]
        test_end=test_idx[-1]

        train_data=filled.iloc[:train_end+1].copy()
        val_data=filled.iloc[max(0,val_start-LOOKBACK):val_end+1].copy()
        test_data=filled.iloc[max(0,test_start-LOOKBACK):test_end+1].copy()

        # Classification targets must remain categorical strings.
        if TASK=="class":
            for c in UP_TARGETS:
                train_data[c]=train_data[c].astype(str)
                val_data[c]=val_data[c].astype(str)
                test_data[c]=test_data[c].astype(str)

        train_ds=create_dataset(train_data,targets)
        val_ds=create_dataset(val_data,targets,min_pred_idx=int(val_start),template=train_ds)
        test_ds=create_dataset(test_data,targets,min_pred_idx=int(test_start),template=train_ds)

        train_dl=train_ds.to_dataloader(train=True,batch_size=BATCH,num_workers=0)
        val_dl=val_ds.to_dataloader(train=False,batch_size=BATCH,num_workers=0)
        test_dl=test_ds.to_dataloader(train=False,batch_size=BATCH,num_workers=0)

        ckdir=work/f"block_{bstart//REFIT_BLOCK}"
        ckdir.mkdir(parents=True,exist_ok=True)
        early=EarlyStopping(monitor="val_loss",min_delta=1e-4,patience=4,mode="min",verbose=False)
        ck=ModelCheckpoint(dirpath=str(ckdir),monitor="val_loss",mode="min",save_top_k=1,filename="best")
        trainer=pl.Trainer(
            max_epochs=MAX_EPOCHS,
            accelerator="cpu",
            devices=1,
            gradient_clip_val=0.1,
            callbacks=[early,ck],
            logger=False,
            enable_progress_bar=False,
            enable_model_summary=False,
            deterministic=True,
            num_sanity_val_steps=0,
            log_every_n_steps=50
        )
        model=model_for(train_ds)
        pc=param_count(model)
        if pc>30000:
            raise RuntimeError(f"TFT parameter ceiling exceeded: {pc}")
        trainer.fit(model,train_dataloaders=train_dl,val_dataloaders=val_dl)

        best_path=ck.best_model_path
        if not best_path:
            raise RuntimeError("No best checkpoint")
        best=TemporalFusionTransformer.load_from_checkpoint(best_path)
        up_idx=class_up_indices(train_ds) if TASK=="class" else None
        tids,preds=predict_block(best,test_dl,up_idx=up_idx)

        # keep exactly the requested test decoder indices
        take=np.isin(tids,np.asarray(test_idx,int))
        tids=tids[take]; preds=preds[take]
        order=np.argsort(tids)
        tids=tids[order]; preds=preds[order]
        if list(tids)!=list(test_idx):
            raise RuntimeError(f"Decoder index mismatch block={bstart//REFIT_BLOCK}: got {tids[:3]}..{tids[-3:]} expected {test_idx[:3]}..{test_idx[-3:]}")

        for j,ix in enumerate(tids):
            sig=float(df.at[ix,"sigma20"])
            vb="LOW" if sig<=VOL_CUTS[0] else ("MID" if sig<=VOL_CUTS[1] else "HIGH")
            row={
                "task":TASK,"row_index":int(ix),
                "origin_date":str(df.at[ix,"date"].date()),
                "signal_date":str(df.at[ix,"signal_date"].date()),
                "year":int(df.at[ix,"signal_date"].year),
                "vol_bucket":vb,
                "refit_block":bstart//REFIT_BLOCK
            }
            if TASK=="class":
                for k,h in enumerate([1,3,5]):
                    row[f"y_up{h}"]=int(df.at[ix,f"target_r{h}"]>0)
                    row[f"p_up{h}"]=float(preds[j,k])
            else:
                for k,h in enumerate([1,3,5]):
                    vals=np.sort(preds[j,k,:].astype(float))
                    row[f"y_r{h}"]=float(df.at[ix,f"target_r{h}"])
                    row[f"q10_h{h}"]=float(vals[0])
                    row[f"q50_h{h}"]=float(vals[1])
                    row[f"q90_h{h}"]=float(vals[2])
                    row[f"cross_pre_h{h}"]=int((preds[j,k,0]>preds[j,k,1]) or (preds[j,k,1]>preds[j,k,2]))
            all_rows.append(row)

        diagnostics.append({
            "task":TASK,"refit_block":bstart//REFIT_BLOCK,
            "block_start":str(start_date.date()),
            "train_pool_n":len(train_pool),"subtrain_n":len(sub_idx),"validation_n":len(val_idx),
            "test_n":len(test_idx),"parameter_count":pc,
            "epochs_completed":int(trainer.current_epoch+1),
            "best_val_loss":float(ck.best_model_score.cpu().item()) if ck.best_model_score is not None else None
        })
        print("TFT_BLOCK",TASK,bstart//REFIT_BLOCK,"params",pc,"epochs",trainer.current_epoch+1,"best_val",diagnostics[-1]["best_val_loss"],flush=True)

    p=pd.DataFrame(all_rows).sort_values("row_index").reset_index(drop=True)
    d=pd.DataFrame(diagnostics)
    if len(p)!=749:
        raise RuntimeError(f"Prediction rows {len(p)} != 749")

    p.to_csv(OUT/f"stage4_tft_{TASK}_predictions.csv",index=False)
    d.to_csv(OUT/f"stage4_tft_{TASK}_training.csv",index=False)

    summary={"task":TASK,"n":len(p),"training":{"parameter_count":int(d.parameter_count.iloc[0]),"mean_epochs":float(d.epochs_completed.mean()),"refits":len(d)},"horizons":{}}
    for h in [1,3,5]:
        if TASK=="class":
            met=metric_direction(p[f"y_up{h}"],p[f"p_up{h}"])
            years={str(int(y)):metric_direction(z[f"y_up{h}"],z[f"p_up{h}"]) for y,z in p.groupby("year")}
            vols={str(v):metric_direction(z[f"y_up{h}"],z[f"p_up{h}"]) for v,z in p.groupby("vol_bucket")}
        else:
            met=metric_quant(p[f"y_r{h}"],p[f"q10_h{h}"],p[f"q50_h{h}"],p[f"q90_h{h}"])
            years={str(int(y)):metric_quant(z[f"y_r{h}"],z[f"q10_h{h}"],z[f"q50_h{h}"],z[f"q90_h{h}"]) for y,z in p.groupby("year")}
            vols={str(v):metric_quant(z[f"y_r{h}"],z[f"q10_h{h}"],z[f"q50_h{h}"],z[f"q90_h{h}"]) for v,z in p.groupby("vol_bucket")}
            met["pre_repair_crossing_rate"]=float(p[f"cross_pre_h{h}"].mean())
        summary["horizons"][str(h)]={"aggregate":met,"years":years,"volatility":vols}

    (OUT/f"stage4_tft_{TASK}_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("TFT_SUMMARY="+json.dumps(summary,separators=(",",":")),flush=True)

if __name__=="__main__":
    main()
