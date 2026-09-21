from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import random
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import numpy as np
import requests
import torch
from PIL import Image, ImageDraw
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

IDENTITY = "DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_RESEARCH"
API_URL = "https://api.twelvedata.com/time_series"
SYMBOL = "XAU/USD"
INTERVAL = "1day"
SEED = 20260921
BATCH_SIZE = 32
LR = 1e-4
MOMENTUM = 0.9
MAX_EPOCHS = 100
PATIENCE = 10
IMG_SIZE = 227
START = "2017-10-01"
PRE2025_END = "2024-12-31"
FULL_END = "2025-12-31"
TRAIN_START = date(2018,1,1)
TRAIN_END = date(2022,12,31)
DEV_START = date(2023,1,1)
DEV_END = date(2023,12,31)
VAL_START = date(2024,1,1)
VAL_END = date(2024,12,31)
CHALLENGE_START = date(2025,1,1)
CHALLENGE_END = date(2025,12,31)

@dataclass(frozen=True)
class Row:
    d: date
    o: float
    h: float
    l: float
    c: float
    sma7: float | None = None
    sma20: float | None = None
    sma50: float | None = None
    bb_up: float | None = None
    bb_dn: float | None = None

def seed_all() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(2)
    try:
        torch.use_deterministic_algorithms(True)
    except Exception:
        pass

def api_key() -> str:
    k = os.environ.get("TWELVE_DATA_API_KEY","").strip()
    if not k:
        raise RuntimeError("TWELVE_DATA_API_KEY_MISSING")
    return k

def request_year(session: requests.Session, key: str, year: int, end_year: int):
    s = f"{year}-01-01" if year > 2017 else START
    e = f"{year}-12-31"
    if year == end_year:
        e = PRE2025_END if end_year == 2024 else FULL_END
    params = {
        "symbol": SYMBOL, "interval": INTERVAL,
        "start_date": s, "end_date": e,
        "order": "ASC", "outputsize": 5000, "format": "JSON"
    }
    last = None
    for attempt in range(4):
        try:
            r = session.get(
                API_URL, params=params,
                headers={"Authorization":f"apikey {key}","User-Agent":"GoldControl-Altuntas-AlexNet/1.0"},
                timeout=(10,90),
            )
            payload = r.json()
            if isinstance(payload,dict) and payload.get("status")=="error":
                msg = str(payload.get("message",""))
                code = str(payload.get("code",""))
                if attempt < 3 and ("credit" in msg.lower() or "rate" in msg.lower() or code in {"429","4290"}):
                    time.sleep(61); continue
                raise RuntimeError(f"TWELVE_ERROR:{code}:{msg[:180]}")
            r.raise_for_status()
            vals = payload.get("values") if isinstance(payload,dict) else None
            if not isinstance(vals,list) or not vals:
                raise RuntimeError(f"NO_VALUES:{year}")
            return vals
        except Exception as exc:
            last = exc
            if attempt == 3:
                raise
            time.sleep(5*(attempt+1))
    raise RuntimeError(str(last))

def load_rows(end_year: int) -> list[Row]:
    sess = requests.Session()
    key = api_key()
    by_date = {}
    for y in range(2017,end_year+1):
        vals = request_year(sess,key,y,end_year)
        for raw in vals:
            d = datetime.fromisoformat(str(raw["datetime"])).date()
            if d.weekday() >= 5:
                continue
            o,h,l,c = [float(raw[k]) for k in ("open","high","low","close")]
            if any((not math.isfinite(x) or x<=0) for x in (o,h,l,c)):
                raise RuntimeError(f"INVALID_PRICE:{d}")
            if l>h or not (l<=o<=h) or not (l<=c<=h):
                raise RuntimeError(f"INVALID_OHLC:{d}")
            v=(o,h,l,c)
            old=by_date.get(d)
            if old is not None and old != v:
                raise RuntimeError(f"DUPLICATE_CONFLICT:{d}")
            by_date[d]=v
        time.sleep(1.0)
    rows=[Row(d,*by_date[d]) for d in sorted(by_date)]
    closes=np.array([r.c for r in rows],dtype=float)
    out=[]
    for i,r in enumerate(rows):
        def mean_n(n):
            return float(np.mean(closes[i-n+1:i+1])) if i>=n-1 else None
        sma7=mean_n(7); sma20=mean_n(20); sma50=mean_n(50)
        if i>=19:
            w=closes[i-19:i+1]
            sd=float(np.std(w,ddof=0))
            bb_up=sma20+2*sd
            bb_dn=sma20-2*sd
        else:
            bb_up=bb_dn=None
        out.append(Row(r.d,r.o,r.h,r.l,r.c,sma7,sma20,sma50,bb_up,bb_dn))
    return out

def prefix_hash(rows: list[Row], end_date: date) -> str:
    s="\n".join(
        f"{r.d.isoformat()}|{r.o:.10f}|{r.h:.10f}|{r.l:.10f}|{r.c:.10f}"
        for r in rows if r.d<=end_date
    )
    return hashlib.sha256(s.encode()).hexdigest()

def render_chart(rows: list[Row], i: int) -> Image.Image:
    if i < 49 or i < 10:
        raise RuntimeError("INSUFFICIENT_WARMUP")
    win=rows[i-10:i+1]
    vals=[]
    for r in win:
        vals.extend([r.l,r.h])
        for x in (r.sma7,r.sma20,r.sma50,r.bb_up,r.bb_dn):
            if x is not None and math.isfinite(x):
                vals.append(x)
    lo=min(vals); hi=max(vals)
    span=max(hi-lo,1e-9)
    lo-=0.05*span; hi+=0.05*span

    W=320; H=320; L=16; R=16; T=16; B=16
    img=Image.new("RGB",(W,H),"white")
    dr=ImageDraw.Draw(img)

    def ymap(v):
        return int(round(T + (hi-v)/(hi-lo)*(H-T-B)))

    xs=[int(round(L + j*(W-L-R)/(len(win)-1))) for j in range(len(win))]
    bodyw=7
    for x,r in zip(xs,win):
        dr.line((x,ymap(r.h),x,ymap(r.l)),fill=(150,150,150),width=1)
        y1=ymap(r.o); y2=ymap(r.c)
        top=min(y1,y2); bot=max(y1,y2)
        if bot==top: bot=top+1
        if r.c>=r.o:
            dr.rectangle((x-bodyw//2,top,x+bodyw//2,bot),fill="white",outline="black",width=1)
        else:
            dr.rectangle((x-bodyw//2,top,x+bodyw//2,bot),fill="black",outline="black",width=1)

    series=[
        ("sma7",(0,210,220),2),
        ("sma50",(255,0,0),2),
        ("bb_up",(0,220,0),2),
        ("sma20",(235,210,0),2),
        ("bb_dn",(230,0,220),2),
    ]
    for name,color,width in series:
        pts=[]
        for x,r in zip(xs,win):
            v=getattr(r,name)
            if v is None or not math.isfinite(v):
                pts=[]; continue
            pts.append((x,ymap(v)))
        if len(pts)>=2:
            dr.line(pts,fill=color,width=width)

    return img.resize((IMG_SIZE,IMG_SIZE),Image.Resampling.BILINEAR)

def label(rows: list[Row], i: int) -> int | None:
    if i+1>=len(rows):
        return None
    a=rows[i].c; b=rows[i+1].c
    if b==a:
        return None
    return 1 if b>a else 0

def period_name(d: date) -> str | None:
    if TRAIN_START<=d<=TRAIN_END: return "train"
    if DEV_START<=d<=DEV_END: return "dev"
    if VAL_START<=d<=VAL_END: return "validation"
    if CHALLENGE_START<=d<=CHALLENGE_END: return "challenge"
    return None

class CandleDataset(Dataset):
    def __init__(self, rows: list[Row], period: str):
        self.rows=rows
        self.idxs=[]
        for i,r in enumerate(rows[:-1]):
            if period_name(r.d)!=period or i<49:
                continue
            y=label(rows,i)
            if y is None:
                continue
            self.idxs.append((i,y))
        self.tf=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485,0.456,0.406],std=[0.229,0.224,0.225]),
        ])
    def __len__(self): return len(self.idxs)
    def __getitem__(self,k):
        i,y=self.idxs[k]
        img=render_chart(self.rows,i)
        x=self.tf(img)
        return x, torch.tensor(y,dtype=torch.long), self.rows[i].d.isoformat()

def image_digest(rows: list[Row], periods: tuple[str,...]) -> str:
    h=hashlib.sha256()
    for period in periods:
        ds=CandleDataset(rows,period)
        for i,y in ds.idxs:
            img=render_chart(rows,i)
            buf=io.BytesIO(); img.save(buf,format="PNG",optimize=False)
            h.update(rows[i].d.isoformat().encode()); h.update(b"|")
            h.update(str(y).encode()); h.update(b"|"); h.update(buf.getvalue())
    return h.hexdigest()

def build_model(pretrained: bool) -> nn.Module:
    if pretrained:
        m=models.alexnet(weights=models.AlexNet_Weights.IMAGENET1K_V1)
    else:
        m=models.alexnet(weights=None)
    m.classifier[6]=nn.Linear(m.classifier[6].in_features,2)
    return m

def eval_model(model, loader, device):
    model.eval()
    ys=[]; ps=[]; dates=[]
    total_loss=0.0; n=0
    ce=nn.CrossEntropyLoss(reduction="sum")
    with torch.no_grad():
        for x,y,d in loader:
            x=x.to(device); y=y.to(device)
            logits=model(x)
            total_loss+=float(ce(logits,y).cpu())
            p=torch.softmax(logits,dim=1)[:,1]
            ys.extend(y.cpu().numpy().tolist())
            ps.extend(p.cpu().numpy().tolist())
            dates.extend(list(d))
            n+=len(y)
    return np.array(ys,dtype=int),np.array(ps,dtype=float),dates,total_loss/max(n,1)

def metrics(y,p):
    pred=p>=0.5
    up=y==1; dn=y==0
    tp=int(np.sum(up & pred)); tn=int(np.sum(dn & (~pred)))
    fp=int(np.sum(dn & pred)); fn=int(np.sum(up & (~pred)))
    up_n=int(np.sum(up)); dn_n=int(np.sum(dn))
    up_s=tp/up_n if up_n else None
    dn_s=tn/dn_n if dn_n else None
    bal=(up_s+dn_s)/2 if up_s is not None and dn_s is not None else None
    eps=1e-12
    brier=float(np.mean((p-y)**2))
    logloss=float(-np.mean(y*np.log(np.clip(p,eps,1-eps))+(1-y)*np.log(np.clip(1-p,eps,1-eps))))
    prec_up=tp/(tp+fp) if tp+fp else 0.0
    rec_up=up_s or 0.0
    f1_up=2*prec_up*rec_up/(prec_up+rec_up) if prec_up+rec_up else 0.0
    prec_dn=tn/(tn+fn) if tn+fn else 0.0
    rec_dn=dn_s or 0.0
    f1_dn=2*prec_dn*rec_dn/(prec_dn+rec_dn) if prec_dn+rec_dn else 0.0
    return {
        "n":int(len(y)),"accuracy":float(np.mean(pred==up)),
        "balanced_accuracy":bal,"up_sensitivity":up_s,"down_sensitivity":dn_s,
        "precision_up":prec_up,"f1_up":f1_up,"precision_down":prec_dn,"f1_down":f1_dn,
        "tp":tp,"tn":tn,"fp":fp,"fn":fn,
        "actual_up":up_n,"actual_down":dn_n,
        "forecast_up":int(np.sum(pred)),"forecast_down":int(np.sum(~pred)),
        "brier":brier,"log_loss":logloss,
        "always_up_accuracy":float(np.mean(up)),"always_down_accuracy":float(np.mean(dn)),
    }

def write_preds(path: Path, y, p, dates):
    lines=["origin_date,actual_up,p_up,pred_up"]
    for d,yy,pp in zip(dates,y,p):
        lines.append(f"{d},{int(yy)},{float(pp):.12f},{int(pp>=0.5)}")
    path.write_text("\n".join(lines)+"\n",encoding="utf-8")

def train_pre2025(outdir: Path):
    seed_all()
    rows=load_rows(2024)
    train_ds=CandleDataset(rows,"train")
    dev_ds=CandleDataset(rows,"dev")
    val_ds=CandleDataset(rows,"validation")
    if min(len(train_ds),len(dev_ds),len(val_ds))==0:
        raise RuntimeError("EMPTY_DATASET")

    gen=torch.Generator().manual_seed(SEED)
    train_loader=DataLoader(train_ds,batch_size=BATCH_SIZE,shuffle=True,num_workers=0,generator=gen)
    dev_loader=DataLoader(dev_ds,batch_size=BATCH_SIZE,shuffle=False,num_workers=0)
    val_loader=DataLoader(val_ds,batch_size=BATCH_SIZE,shuffle=False,num_workers=0)

    device=torch.device("cpu")
    model=build_model(pretrained=True).to(device)
    opt=torch.optim.SGD(model.parameters(),lr=LR,momentum=MOMENTUM,weight_decay=0.0)
    ce=nn.CrossEntropyLoss()

    best_acc=-1.0; best_epoch=0; stale=0; history=[]; best_state=None
    for epoch in range(1,MAX_EPOCHS+1):
        model.train(); tr_loss=0.0; n=0; corr=0
        for x,y,_ in train_loader:
            x=x.to(device); y=y.to(device)
            opt.zero_grad(set_to_none=True)
            logits=model(x)
            loss=ce(logits,y)
            loss.backward(); opt.step()
            tr_loss += float(loss.detach().cpu())*len(y)
            corr += int((logits.argmax(1)==y).sum().cpu())
            n += len(y)
        dy,dp,dd,dev_loss=eval_model(model,dev_loader,device)
        dev_acc=float(np.mean((dp>=0.5)==(dy==1)))
        history.append({"epoch":epoch,"train_loss":tr_loss/n,"train_accuracy":corr/n,"dev_loss":dev_loss,"dev_accuracy":dev_acc})
        print(json.dumps(history[-1],sort_keys=True))
        if dev_acc > best_acc + 1e-12:
            best_acc=dev_acc; best_epoch=epoch; stale=0
            best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
        else:
            stale += 1
        if stale>=PATIENCE:
            break

    if best_state is None:
        raise RuntimeError("NO_BEST_STATE")
    model.load_state_dict(best_state)
    model.to(device)
    vy,vp,vd,_=eval_model(model,val_loader,device)
    vm=metrics(vy,vp)

    ckpt=outdir/"altuntas_alexnet_v1_pre2025_checkpoint.pt"
    torch.save({
        "identity":IDENTITY,"seed":SEED,"best_epoch":best_epoch,
        "model_state":model.state_dict(),
        "reconstruction":{"optimizer":"SGD","lr":LR,"momentum":MOMENTUM,"batch_size":BATCH_SIZE},
    },ckpt)
    ckpt_sha=hashlib.sha256(ckpt.read_bytes()).hexdigest()
    panel_sha=prefix_hash(rows,date(2024,12,31))
    img_sha=image_digest(rows,("train","dev","validation"))

    config={
        "identity":IDENTITY,"seed":SEED,"batch_size":BATCH_SIZE,"learning_rate":LR,
        "optimizer_reconstruction":"SGD","momentum":MOMENTUM,"weight_decay":0.0,
        "max_epochs":MAX_EPOCHS,"patience":PATIENCE,
        "best_epoch":best_epoch,"checkpoint_sha256":ckpt_sha,
        "pre2025_panel_sha256":panel_sha,"pre2025_image_sha256":img_sha,
        "train_n":len(train_ds),"dev_n":len(dev_ds),"validation_n":len(val_ds),
        "frozen_before_2025":True,
    }
    result={
        "identity":IDENTITY,"status":"PRE2025_FROZEN",
        "best_epoch":best_epoch,"best_dev_accuracy":best_acc,
        "2024_validation":vm,
        "pre2025_gate_passed": bool(
            vm["balanced_accuracy"]>=0.55 and vm["up_sensitivity"]>=0.40 and
            vm["down_sensitivity"]>=0.40 and
            vm["accuracy"]>vm["always_up_accuracy"] and vm["accuracy"]>vm["always_down_accuracy"]
        ),
        "training_history":history,
    }
    (outdir/"GOLD_CONTROL_DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_FROZEN_CONFIG_2026-09-21.json").write_text(json.dumps(config,indent=2),encoding="utf-8")
    (outdir/"GOLD_CONTROL_DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_PRE2025_RESULT_2026-09-21.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    write_preds(outdir/"GOLD_CONTROL_DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_2024_FORECASTS_2026-09-21.csv",vy,vp,vd)
    print("ALTUNTAS_PRE2025_SUCCESS")

def replay_2025(outdir: Path, config_path: Path, pre_result_path: Path, checkpoint_path: Path):
    seed_all()
    config=json.loads(config_path.read_text())
    pre=json.loads(pre_result_path.read_text())
    if config["identity"]!=IDENTITY or pre["identity"]!=IDENTITY:
        raise RuntimeError("IDENTITY_MISMATCH")
    if hashlib.sha256(checkpoint_path.read_bytes()).hexdigest()!=config["checkpoint_sha256"]:
        raise RuntimeError("CHECKPOINT_HASH_MISMATCH")

    rows=load_rows(2025)
    if prefix_hash(rows,date(2024,12,31)) != config["pre2025_panel_sha256"]:
        raise RuntimeError("PRE2025_PANEL_PREFIX_CHANGED")
    ch_ds=CandleDataset(rows,"challenge")
    ch_loader=DataLoader(ch_ds,batch_size=BATCH_SIZE,shuffle=False,num_workers=0)
    model=build_model(pretrained=False)
    ck=torch.load(checkpoint_path,map_location="cpu",weights_only=False)
    model.load_state_dict(ck["model_state"])
    y,p,d,_=eval_model(model,ch_loader,torch.device("cpu"))
    m=metrics(y,p)
    result={
        "identity":IDENTITY,"status":"LOCKED_2025_REPLAY_COMPLETE",
        "pre2025_gate_passed":pre["pre2025_gate_passed"],
        "2025_challenge":m,
    }
    (outdir/"GOLD_CONTROL_DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_2025_RESULT_2026-09-21.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    write_preds(outdir/"GOLD_CONTROL_DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_2025_FORECASTS_2026-09-21.csv",y,p,d)

    v=pre["2024_validation"]
    lines=[
        "# GOLD CONTROL — ALTUNTAŞ ALEXNET CANDLE V1 RESULT","",
        f"**Identity:** `{IDENTITY}`  ",
        "**Evidence:** source-constrained shorter-history transfer-learning reconstruction; not exact MATLAB replication.","",
        "## Fixed 2024 validation and locked 2025 challenge","",
        "| period | n | accuracy | BA | UP sens | DOWN sens | UP/DOWN forecasts | Brier | always-UP |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        f"| 2024 | {v['n']} | {v['accuracy']:.4f} | {v['balanced_accuracy']:.4f} | {v['up_sensitivity']:.4f} | {v['down_sensitivity']:.4f} | {v['forecast_up']}/{v['forecast_down']} | {v['brier']:.4f} | {v['always_up_accuracy']:.4f} |",
        f"| 2025 | {m['n']} | {m['accuracy']:.4f} | {m['balanced_accuracy']:.4f} | {m['up_sensitivity']:.4f} | {m['down_sensitivity']:.4f} | {m['forecast_up']}/{m['forecast_down']} | {m['brier']:.4f} | {m['always_up_accuracy']:.4f} |",
        "",
        "## Frozen decision","",
        f"- Pre-2025 research-interest gate: **{'PASS' if pre['pre2025_gate_passed'] else 'FAIL'}**.",
        "- 2025 cannot rescue a failed 2024 gate.",
        "- No runtime, production or trading authority is created.",
    ]
    (outdir/"GOLD_CONTROL_DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_RESULT_2026-09-21.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("ALTUNTAS_2025_REPLAY_SUCCESS")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage",choices=("pre2025","2025"),required=True)
    ap.add_argument("--outdir",required=True)
    ap.add_argument("--config")
    ap.add_argument("--pre-result")
    ap.add_argument("--checkpoint")
    args=ap.parse_args()
    out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)
    if args.stage=="pre2025":
        train_pre2025(out)
    else:
        if not args.config or not args.pre_result or not args.checkpoint:
            raise RuntimeError("CONFIG_PRE_RESULT_CHECKPOINT_REQUIRED")
        replay_2025(out,Path(args.config),Path(args.pre_result),Path(args.checkpoint))

if __name__=="__main__":
    main()
