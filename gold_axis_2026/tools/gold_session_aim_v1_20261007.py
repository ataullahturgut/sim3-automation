from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
SENTRYP=AX/"tools"/"gold_session_sentry_v1_20261007.py"
M04P=AX/"tools"/"gold_session_model04b_path_global_feature_selection_20261007.py"
OUT=AX/"SESSION_AIM_V1_OUT";OUT.mkdir(exist_ok=True)

RECENT_N=126
MIN_LEDGER=30
HALF_LIVES=[21,63,126]
ETAS=[10,20,40]
SEED=20261007

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

sentry=loadmod("session_sentry",SENTRYP)
m04=loadmod("session_m04",M04P)

def metric(y,p):
    y=np.asarray(y,int);p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "up_actual":int((y==1).sum()),
        "up_correct":int(((y==1)&(pred==1)).sum()),
        "down_actual":int((y==0).sum()),
        "down_correct":int(((y==0)&(pred==0)).sum()),
    }

def recent_model():
    return LogisticRegression(
        C=1.0,solver="lbfgs",max_iter=5000,
        class_weight="balanced",random_state=SEED
    )

def canonical_ledger():
    q=sentry.load_ledger().copy()
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
    q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
    q["year"]=q.start_utc.dt.year
    return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def path_feature_panel():
    p,features=m04.build_panel()
    p=p.copy()
    p["start_utc"]=pd.to_datetime(p.start_utc,utc=True)
    p["end_utc"]=pd.to_datetime(p.end_utc,utc=True)
    p["year"]=p.start_utc.dt.year
    return p.sort_values(["partition","window","start_utc"]).reset_index(drop=True),list(features)

def build_recent126(base,features_panel,features):
    scored=[]
    for (part,win),b0 in base.groupby(["partition","window"],sort=True):
        b=b0.sort_values("start_utc").copy()
        fp=features_panel[
            (features_panel.partition.eq(part))&
            (features_panel.window.eq(win))
        ].sort_values("start_utc").copy()
        if fp.empty:continue

        b=b.merge(
            fp[["start_utc"]+features],
            on="start_utc",how="inner",validate="one_to_one"
        )
        if b.empty:continue
        b["month_key"]=b.start_utc.dt.to_period("M").astype(str)

        for mo in sorted(b.month_key.unique()):
            te=b[b.month_key.eq(mo)].copy()
            if te.empty:continue
            cutoff=te.start_utc.min()
            tr=fp[(fp.end_utc<=cutoff)&(fp.start_utc<cutoff)].tail(RECENT_N).copy()
            if len(tr)<RECENT_N or tr.y_up.nunique()<2:
                continue
            X=tr[features].astype(float).to_numpy()
            T=te[features].astype(float).to_numpy()
            sc=StandardScaler().fit(X)
            m=recent_model().fit(sc.transform(X),tr.y_up.to_numpy(int))
            pp=m.predict_proba(sc.transform(T))[:,1]
            for r,p in zip(te.itertuples(index=False),pp):
                scored.append({
                    "partition":part,"window":win,"label_date":r.label_date,
                    "start_utc":r.start_utc,"end_utc":r.end_utc,"year":int(r.year),
                    "y_up":int(r.y_up),
                    "p_structural":float(r.p_struct),
                    "p_path_global":float(r.p_path),
                    "p_path_recent126":float(p),
                    "recent_train_n":int(len(tr))
                })
    q=pd.DataFrame(scored)
    if q.empty:raise RuntimeError("AIM_NO_EXPERT_LEDGER")
    return q.sort_values(["partition","window","start_utc"]).reset_index(drop=True)

def decayed_brier(matured,col,half_life):
    if matured.empty:return .25
    y=matured.y_up.to_numpy(float)
    p=matured[col].to_numpy(float)
    loss=(p-y)**2
    age=np.arange(len(loss)-1,-1,-1,dtype=float)
    w=.5**(age/float(half_life))
    return float(np.sum(w*loss)/np.sum(w))

def weights(losses,eta):
    a=-float(eta)*np.asarray(losses,float)
    a-=np.max(a);e=np.exp(a)
    return e/e.sum()

def apply_mixture(g,half_life,eta):
    g=g.sort_values("start_utc").reset_index(drop=True)
    pcols=["p_structural","p_path_global","p_path_recent126"]
    rows=[]
    for r in g.itertuples(index=False):
        matured=g[
            (g.end_utc<=r.start_utc)&
            (g.start_utc<r.start_utc)
        ].copy()
        if len(matured)<MIN_LEDGER:
            losses=[.25,.25,.25]
            w=np.array([1/3,1/3,1/3],float)
        else:
            losses=[decayed_brier(matured,c,half_life) for c in pcols]
            w=weights(losses,eta)
        pv=np.array([r.p_structural,r.p_path_global,r.p_path_recent126],float)
        pa=float(np.dot(w,pv))
        rows.append({
            "partition":r.partition,"window":r.window,"label_date":r.label_date,
            "start_utc":r.start_utc,"end_utc":r.end_utc,"year":int(r.year),
            "y_up":int(r.y_up),
            "p_structural":float(r.p_structural),
            "p_path_global":float(r.p_path_global),
            "p_path_recent126":float(r.p_path_recent126),
            "loss_structural":float(losses[0]),
            "loss_path_global":float(losses[1]),
            "loss_path_recent126":float(losses[2]),
            "w_structural":float(w[0]),
            "w_path_global":float(w[1]),
            "w_path_recent126":float(w[2]),
            "p_aim":pa,"matured_ledger_n":int(len(matured)),
            "half_life":int(half_life),"eta":int(eta)
        })
    return pd.DataFrame(rows)

def compare(g):
    ms=metric(g.y_up,g.p_structural);ma=metric(g.y_up,g.p_aim)
    sd=(g.p_structural>=.5).astype(int)
    ad=(g.p_aim>=.5).astype(int);y=g.y_up.astype(int)
    ch=sd.ne(ad)
    rescue=int((ch&sd.ne(y)&ad.eq(y)).sum())
    broken=int((ch&sd.eq(y)&ad.ne(y)).sum())
    return ms,ma,{
        "changed_calls":int(ch.sum()),"rescued":rescue,
        "broken":broken,"net_rescue":rescue-broken
    }

def select_config(g):
    rows=[];mixes={}
    for h in HALF_LIVES:
        for eta in ETAS:
            z=apply_mixture(g,h,eta)
            d=z[z.year.isin([2023,2024])].copy()
            if d.empty:continue
            ms,ma,x=compare(d)
            eligible=bool(
                ma["balanced_accuracy"]+1e-12>=ms["balanced_accuracy"] and
                ma["accuracy"]+.005+1e-12>=ms["accuracy"] and
                ma["brier"]<=ms["brier"]+1e-12 and
                ma["logloss"]<=ms["logloss"]+.005+1e-12
            )
            rows.append({
                "half_life":h,"eta":eta,"eligible":eligible,
                "dev_n":len(d),
                "struct_accuracy":ms["accuracy"],"aim_accuracy":ma["accuracy"],
                "struct_ba":ms["balanced_accuracy"],"aim_ba":ma["balanced_accuracy"],
                "struct_brier":ms["brier"],"aim_brier":ma["brier"],
                "struct_logloss":ms["logloss"],"aim_logloss":ma["logloss"],
                "aim_up_recall":ma["up_recall"],"aim_down_recall":ma["down_recall"],
                **x
            })
            mixes[(h,eta)]=z
    tab=pd.DataFrame(rows)
    elig=tab[tab.eligible].copy()
    if elig.empty:return tab,None,None
    elig=elig.sort_values(
        ["aim_ba","aim_accuracy","aim_brier","aim_logloss","half_life","eta"],
        ascending=[False,False,True,True,False,True]
    )
    h=int(elig.iloc[0].half_life);eta=int(elig.iloc[0].eta)
    return tab,(h,eta),mixes[(h,eta)]

def year_confirmation(mix):
    checks=[];ok=True
    for yr in [2023,2024]:
        z=mix[mix.year.eq(yr)].copy()
        if len(z)<30:
            checks.append({"year":yr,"n":len(z),"pass":False,"reason":"INSUFFICIENT_YEAR_CONFIRMATION"})
            ok=False;continue
        ms,ma,_=compare(z)
        passed=bool(
            ma["balanced_accuracy"]+1e-12>=ms["balanced_accuracy"] and
            ma["accuracy"]+.01+1e-12>=ms["accuracy"] and
            ma["brier"]<=ms["brier"]+.0025+1e-12
        )
        checks.append({
            "year":yr,"n":len(z),"pass":passed,
            "struct_accuracy":ms["accuracy"],"aim_accuracy":ma["accuracy"],
            "struct_ba":ms["balanced_accuracy"],"aim_ba":ma["balanced_accuracy"],
            "struct_brier":ms["brier"],"aim_brier":ma["brier"]
        })
        ok=ok and passed
    return ok,checks

def summarize(pred,period):
    rows=[]
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        ms,ma,x=compare(g)
        rows.append({
            "period":period,"partition":part,"window":win,
            "half_life":int(g.half_life.iloc[0]),"eta":int(g.eta.iloc[0]),**x,
            "mean_w_structural":float(g.w_structural.mean()),
            "mean_w_path_global":float(g.w_path_global.mean()),
            "mean_w_path_recent126":float(g.w_path_recent126.mean()),
            **{f"struct_{k}":v for k,v in ms.items()},
            **{f"aim_{k}":v for k,v in ma.items()}
        })
    return pd.DataFrame(rows)

def main():
    base=canonical_ledger()
    fp,features=path_feature_panel()
    led=build_recent126(base,fp,features)

    selection=[];confirm=[];dev_parts=[];tr_parts=[];chosen=[]
    for (part,win),g in led.groupby(["partition","window"],sort=True):
        tab,key,mix=select_config(g)
        for r in tab.to_dict("records"):
            selection.append({"partition":part,"window":win,**r})
        if key is None:continue
        ok,checks=year_confirmation(mix)
        h,eta=key
        chosen.append({
            "partition":part,"window":win,"half_life":h,"eta":eta,
            "confirmed":ok,"confirmation":checks
        })
        for q in checks:confirm.append({"partition":part,"window":win,"half_life":h,"eta":eta,**q})
        if ok:
            dev_parts.append(mix[mix.year.isin([2023,2024])].copy())
            tr_parts.append(mix[mix.year.eq(2025)].copy())

    sel=pd.DataFrame(selection);conf=pd.DataFrame(confirm)
    dev=pd.concat(dev_parts,ignore_index=True) if dev_parts else pd.DataFrame()
    tr=pd.concat(tr_parts,ignore_index=True) if tr_parts else pd.DataFrame()

    led.to_csv(OUT/"expert_ledger.csv",index=False)
    sel.to_csv(OUT/"selection_grid.csv",index=False)
    conf.to_csv(OUT/"year_confirmation.csv",index=False)
    dev.to_csv(OUT/"confirmed_dev_predictions.csv",index=False)
    tr.to_csv(OUT/"transport_2025_predictions.csv",index=False)
    if not dev.empty:summarize(dev,"DEV_2023_2024").to_csv(OUT/"dev_metrics.csv",index=False)
    else:pd.DataFrame().to_csv(OUT/"dev_metrics.csv",index=False)
    if not tr.empty:summarize(tr,"FROZEN_2025").to_csv(OUT/"transport_2025_metrics.csv",index=False)
    else:pd.DataFrame().to_csv(OUT/"transport_2025_metrics.csv",index=False)

    summary={
        "status":"SESSION_AIM_V1_COMPLETE",
        "experts":["STRUCTURAL_IRIS","PATH_GLOBAL","PATH_RECENT126"],
        "recent_n":RECENT_N,"half_life_grid":HALF_LIVES,"eta_grid":ETAS,
        "selected":chosen,
        "transport_2025_metrics":summarize(tr,"FROZEN_2025").to_dict("records") if not tr.empty else [],
        "guardrails":[
            "Canonical Structural/PATH probabilities come from fresh SENTRY exact-common ledger.",
            "PATH_RECENT126 uses only last 126 matured same-window PATH-feature rows.",
            "Adaptive losses use only matured prior exact-common expert forecasts.",
            "Hyperparameters selected only on 2023-2024.",
            "2025 opens only after year-stability confirmation.",
            "No 2025 retuning; 2026 unopened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# SESSION AIM V1 — RESULT","",
           "## Development selection","",
           "| Partition | Window | H | Eta | N | Structural BA | AIM BA | AIM UP | AIM DOWN | Changed | Net | Eligible |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in sel.itertuples(index=False):
        lines.append(
            f"| {r.partition} | {r.window} | {int(r.half_life)} | {int(r.eta)} | {int(r.dev_n)} | "
            f"{100*r.struct_ba:.2f}% | {100*r.aim_ba:.2f}% | "
            f"{100*r.aim_up_recall:.2f}% | {100*r.aim_down_recall:.2f}% | "
            f"{int(r.changed_calls)} | {int(r.net_rescue):+d} | {r.eligible} |"
        )
    lines+=["","## Year-stability confirmation","",
            "| Partition | Window | H | Eta | Year | N | Pass | Structural BA | AIM BA |",
            "|---|---|---:|---:|---:|---:|---|---:|---:|"]
    for r in conf.itertuples(index=False):
        sb=getattr(r,"struct_ba",np.nan);ab=getattr(r,"aim_ba",np.nan)
        lines.append(
            f"| {r.partition} | {r.window} | {int(r.half_life)} | {int(r.eta)} | {int(r.year)} | {int(r.n)} | "
            f"{r.pass_ if hasattr(r,'pass_') else getattr(r,'_6',False)} | "
            f"{'' if pd.isna(sb) else f'{100*sb:.2f}%'} | {'' if pd.isna(ab) else f'{100*ab:.2f}%'} |"
        )
    lines+=["","## Frozen 2025 transport",""]
    if tr.empty:
        lines.append("No AIM session head passed development plus year-stability confirmation; 2025 remained closed.")
    else:
        tm=summarize(tr,"FROZEN_2025")
        lines+=["| Partition | Window | H | Eta | N | Structural BA | AIM BA | AIM UP | AIM DOWN | Brier Structural | Brier AIM | Mean weights S/P/R | Net rescue |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|"]
        for r in tm.itertuples(index=False):
            lines.append(
                f"| {r.partition} | {r.window} | {int(r.half_life)} | {int(r.eta)} | {int(r.aim_n)} | "
                f"{100*r.struct_balanced_accuracy:.2f}% | {100*r.aim_balanced_accuracy:.2f}% | "
                f"{100*r.aim_up_recall:.2f}% | {100*r.aim_down_recall:.2f}% | "
                f"{r.struct_brier:.4f} | {r.aim_brier:.4f} | "
                f"{100*r.mean_w_structural:.1f}/{100*r.mean_w_path_global:.1f}/{100*r.mean_w_path_recent126:.1f} | "
                f"{int(r.net_rescue):+d} |"
            )
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print((OUT/"result.md").read_text())

if __name__=="__main__":
    main()
