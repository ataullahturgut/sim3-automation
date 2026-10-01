import os,io,json,hashlib,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import requests

REPO="ataullahturgut/sim3-automation"
STAGE2_ARTIFACT=11167744845
OUT=Path(os.environ.get("OUT_DIR","stage5_reconcile_out"))
OUT.mkdir(parents=True,exist_ok=True)

def get_zip(aid):
    tok=os.environ["GITHUB_TOKEN"]
    u=f"https://api.github.com/repos/{REPO}/actions/artifacts/{aid}/zip"
    r=requests.get(u,headers={"Authorization":f"Bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"short-horizon-stage5"},timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))

def read_csv(z,suffix):
    n=[x for x in z.namelist() if x.endswith(suffix)]
    if len(n)!=1: raise RuntimeError((suffix,n))
    return pd.read_csv(io.BytesIO(z.read(n[0])))

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def vote_prob(p):
    if p>=0.55: return "UP"
    if p<=0.45: return "DOWN"
    return "NEUTRAL"

def vote_num(x,dead):
    if x>dead: return "UP"
    if x<-dead: return "DOWN"
    return "NEUTRAL"

def dir_state(a,b,c):
    v=[a,b,c]
    if all(x=="UP" for x in v): return "ALIGNED_UP"
    if all(x=="DOWN" for x in v): return "ALIGNED_DOWN"
    if sum(x=="NEUTRAL" for x in v)>=2:
        non=[x for x in v if x!="NEUTRAL"]
        if len(set(non))<=1: return "LOW_CONVICTION"
    return "MIXED"

def state_metrics(z):
    r=z["y_return"].astype(float)
    return {
        "n":int(len(z)),
        "frequency":None,
        "up_rate":float((r>0).mean()) if len(z) else None,
        "down_rate":float((r<0).mean()) if len(z) else None,
        "mean_return":float(r.mean()) if len(z) else None,
        "median_return":float(r.median()) if len(z) else None,
        "std_return":float(r.std(ddof=0)) if len(z) else None,
        "loss_frequency":float((r<0).mean()) if len(z) else None,
        "severe_downside_frequency":float(z["realized_severe_down"].mean()) if len(z) else None,
        "strong_upside_frequency":float(z["realized_strong_up"].mean()) if len(z) else None,
        "mean_abs_return":float(r.abs().mean()) if len(z) else None,
    }

def main():
    z=get_zip(STAGE2_ARTIFACT)
    p=read_csv(z,"stage2_h3_predictions.csv")
    q=read_csv(z,"stage2_h3_quantile_predictions.csv")

    d=p[(p["feature_block"]=="CORE3")&(p["head"]=="direction")][
        ["row_index","origin_date","signal_date","y_return","y_up","sigma20","vol_bucket","prediction"]
    ].copy().rename(columns={"prediction":"p_up"})
    r=p[(p["feature_block"]=="GOLD_ONLY")&(p["head"]=="return")][
        ["row_index","prediction"]
    ].copy().rename(columns={"prediction":"ret_hat"})
    qq=q[q["feature_block"]=="GOLD_ONLY"][["row_index","quantile","prediction"]].copy()
    qwide=qq.pivot(index="row_index",columns="quantile",values="prediction").reset_index()
    qwide=qwide.rename(columns={0.1:"q10",0.5:"q50",0.9:"q90"})

    x=d.merge(r,on="row_index",how="inner").merge(qwide,on="row_index",how="inner")
    x["origin_date"]=pd.to_datetime(x["origin_date"])
    x["signal_date"]=pd.to_datetime(x["signal_date"])
    if len(x)!=749: raise RuntimeError(f"Expected 749 rows, got {len(x)}")

    x["hvol"]=x["sigma20"].astype(float)*np.sqrt(3.0)
    x["deadband"]=0.25*x["hvol"]
    x["direction_vote"]=[vote_prob(v) for v in x["p_up"]]
    x["return_vote"]=[vote_num(v,d) for v,d in zip(x["ret_hat"],x["deadband"])]
    x["median_vote"]=[vote_num(v,d) for v,d in zip(x["q50"],x["deadband"])]
    x["directional_state"]=[
        dir_state(a,b,c) for a,b,c in zip(x["direction_vote"],x["return_vote"],x["median_vote"])
    ]
    x["high_downside"]=(x["q10"]<=-1.0*x["hvol"])
    x["strong_upside"]=(x["q90"]>=1.0*x["hvol"])
    x["final_state"]=np.select(
        [
            (x["directional_state"]=="ALIGNED_UP") & (~x["high_downside"]),
            (x["directional_state"]=="ALIGNED_UP") & (x["high_downside"]),
            x["directional_state"]=="ALIGNED_DOWN",
            x["directional_state"]=="LOW_CONVICTION"
        ],
        ["ALIGNED_UP_LOW_RISK","ALIGNED_UP_HIGH_RISK","ALIGNED_DOWN","LOW_CONVICTION"],
        default="MIXED"
    )
    x["realized_severe_down"]=(x["y_return"]<=-1.0*x["hvol"])
    x["realized_strong_up"]=(x["y_return"]>=1.0*x["hvol"])
    x["year"]=x["signal_date"].dt.year.astype(int)

    x.to_csv(OUT/"stage5_reconciled_forecasts.csv",index=False)

    unconditional=state_metrics(x)
    unconditional["frequency"]=1.0
    unconditional_up=unconditional["up_rate"]
    unconditional_down=unconditional["down_rate"]
    unconditional_severe=unconditional["severe_downside_frequency"]
    unconditional_abs=unconditional["mean_abs_return"]

    # Directional/final summaries
    rows=[]
    for typ,col in [("directional_state","directional_state"),("final_state","final_state")]:
        for val,zv in x.groupby(col):
            m=state_metrics(zv); m["frequency"]=float(len(zv)/len(x))
            rows.append({"state_type":typ,"state":val,**m})
    summary=pd.DataFrame(rows)
    summary.to_csv(OUT/"stage5_state_summary.csv",index=False)

    # year summary
    yrows=[]
    for col in ["directional_state","final_state"]:
        for (yr,val),zv in x.groupby(["year",col]):
            m=state_metrics(zv); m["frequency"]=float(len(zv)/len(x[x.year==yr]))
            yrows.append({"state_type":col,"year":int(yr),"state":val,**m})
    ys=pd.DataFrame(yrows)
    ys.to_csv(OUT/"stage5_state_year_summary.csv",index=False)

    # volatility
    vrows=[]
    for col in ["directional_state","final_state"]:
        for (vb,val),zv in x.groupby(["vol_bucket",col]):
            m=state_metrics(zv); m["frequency"]=float(len(zv)/len(x[x.vol_bucket==vb]))
            vrows.append({"state_type":col,"vol_bucket":vb,"state":val,**m})
    vs=pd.DataFrame(vrows)
    vs.to_csv(OUT/"stage5_state_volatility_summary.csv",index=False)

    # risk flags
    riskrows=[]
    for name,col in [("HIGH_DOWNSIDE","high_downside"),("STRONG_UPSIDE","strong_upside")]:
        for flag,zv in x.groupby(col):
            m=state_metrics(zv); m["frequency"]=float(len(zv)/len(x))
            riskrows.append({"flag_name":name,"flag_value":bool(flag),**m})
    rs=pd.DataFrame(riskrows)
    rs.to_csv(OUT/"stage5_risk_flag_summary.csv",index=False)

    # gates
    decisions=[]

    au=x[x.directional_state=="ALIGNED_UP"]
    au_year_counts=au.groupby("year").size().to_dict()
    au_pass=(
        len(au)>=30 and
        float((au.y_return>0).mean()) >= unconditional_up+0.07 and
        float(au.y_return.mean())>0 and
        all(int(au_year_counts.get(y,0))>=5 for y in [2022,2023,2024])
    )
    decisions.append({
        "component":"ALIGNED_UP","pass":bool(au_pass),"n":int(len(au)),
        "realized_up_rate":float((au.y_return>0).mean()) if len(au) else None,
        "unconditional_up_rate":unconditional_up,
        "lift_pp":float((au.y_return>0).mean()-unconditional_up) if len(au) else None,
        "mean_return":float(au.y_return.mean()) if len(au) else None,
        "year_counts":json.dumps({str(k):int(v) for k,v in au_year_counts.items()},sort_keys=True)
    })

    ad=x[x.directional_state=="ALIGNED_DOWN"]
    ad_year_counts=ad.groupby("year").size().to_dict()
    ad_pass=(
        len(ad)>=30 and
        float((ad.y_return<0).mean()) >= unconditional_down+0.07 and
        float(ad.y_return.mean())<0 and
        all(int(ad_year_counts.get(y,0))>=5 for y in [2022,2023,2024])
    )
    decisions.append({
        "component":"ALIGNED_DOWN","pass":bool(ad_pass),"n":int(len(ad)),
        "realized_down_rate":float((ad.y_return<0).mean()) if len(ad) else None,
        "unconditional_down_rate":unconditional_down,
        "lift_pp":float((ad.y_return<0).mean()-unconditional_down) if len(ad) else None,
        "mean_return":float(ad.y_return.mean()) if len(ad) else None,
        "year_counts":json.dumps({str(k):int(v) for k,v in ad_year_counts.items()},sort_keys=True)
    })

    hd=x[x.high_downside]
    hd_pass=(
        len(hd)>=30 and
        float(hd.realized_severe_down.mean()) >= unconditional_severe+0.05
    )
    decisions.append({
        "component":"HIGH_DOWNSIDE","pass":bool(hd_pass),"n":int(len(hd)),
        "realized_severe_down_rate":float(hd.realized_severe_down.mean()) if len(hd) else None,
        "unconditional_severe_down_rate":unconditional_severe,
        "lift_pp":float(hd.realized_severe_down.mean()-unconditional_severe) if len(hd) else None,
        "mean_return":float(hd.y_return.mean()) if len(hd) else None
    })

    lc=x[x.directional_state=="LOW_CONVICTION"]
    decisions.append({
        "component":"LOW_CONVICTION_DIAGNOSTIC","pass":None,"n":int(len(lc)),
        "mean_abs_return":float(lc.y_return.abs().mean()) if len(lc) else None,
        "unconditional_mean_abs_return":unconditional_abs,
        "relative_abs_return_change":float((lc.y_return.abs().mean()-unconditional_abs)/unconditional_abs) if len(lc) else None
    })

    mx=x[x.directional_state=="MIXED"]
    decisions.append({
        "component":"MIXED_DIAGNOSTIC","pass":None,"n":int(len(mx)),
        "up_rate":float((mx.y_return>0).mean()) if len(mx) else None,
        "mean_return":float(mx.y_return.mean()) if len(mx) else None,
        "mean_abs_return":float(mx.y_return.abs().mean()) if len(mx) else None
    })

    dec=pd.DataFrame(decisions)
    dec.to_csv(OUT/"stage5_usefulness_decisions.csv",index=False)

    pass_components=[d["component"] for d in decisions if d.get("pass") is True]
    status="USEFUL_PASS" if pass_components else "NO_RECONCILIATION_PASS"

    # component robustness tables
    comp_rows=[]
    for comp,mask in [
        ("ALIGNED_UP",x.directional_state=="ALIGNED_UP"),
        ("ALIGNED_DOWN",x.directional_state=="ALIGNED_DOWN"),
        ("HIGH_DOWNSIDE",x.high_downside)
    ]:
        for yr,zv in x[mask].groupby("year"):
            m=state_metrics(zv)
            comp_rows.append({"component":comp,"slice_type":"year","slice":str(int(yr)),**m})
        for vb,zv in x[mask].groupby("vol_bucket"):
            m=state_metrics(zv)
            comp_rows.append({"component":comp,"slice_type":"volatility","slice":vb,**m})
    cr=pd.DataFrame(comp_rows)
    cr.to_csv(OUT/"stage5_component_robustness.csv",index=False)

    lines=[
        "# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 5 Head Reconciliation Result","",
        f"**Status:** **{status}**","",
        "## Unconditional DEV context","",
        f"- origins: {len(x)}",
        f"- H3 UP rate: {100*unconditional_up:.2f}%",
        f"- H3 DOWN rate: {100*unconditional_down:.2f}%",
        f"- severe-downside frequency: {100*unconditional_severe:.2f}%",
        f"- mean absolute H3 return: {100*unconditional_abs:.3f}%",
        "",
        "## Usefulness gates","",
        "| Component | PASS | N | Key lift | Mean return |",
        "|---|---|---:|---:|---:|"
    ]
    for d0 in decisions[:3]:
        if d0["component"]=="ALIGNED_UP":
            lift=d0["lift_pp"]; mr=d0["mean_return"]
        elif d0["component"]=="ALIGNED_DOWN":
            lift=d0["lift_pp"]; mr=d0["mean_return"]
        else:
            lift=d0["lift_pp"]; mr=d0["mean_return"]
        lines.append(f"| {d0['component']} | {d0['pass']} | {d0['n']} | {100*lift:.2f} pp | {100*mr:.3f}% |")

    lines += ["","## Directional states",""]
    for _,rr in summary[summary.state_type=="directional_state"].sort_values("state").iterrows():
        lines.append(
            f"- {rr['state']}: n={int(rr['n'])}, freq={100*rr['frequency']:.1f}%, "
            f"UP={100*rr['up_rate']:.1f}%, mean={100*rr['mean_return']:.3f}%, "
            f"severe-down={100*rr['severe_downside_frequency']:.1f}%."
        )

    lines += ["","## Binding interpretation"]
    if status=="USEFUL_PASS":
        lines.append("At least one preregistered reconciliation component separates realized H3 outcomes. Freeze the forecast-state architecture exactly as preregistered and proceed to Stage 6 tactical allocation / utility design without threshold retuning.")
    else:
        lines.append("No preregistered reconciliation component passes. Keep the frozen H3 heads separate and proceed to Stage 6 using raw head outputs rather than categorical state labels.")

    (OUT/"STAGE5_RESULT.md").write_text("\n".join(lines),encoding="utf-8")
    files=list(OUT.iterdir())
    summary_json={
        "status":status,
        "pass_components":pass_components,
        "unconditional":unconditional,
        "decisions":decisions,
        "hashes":{p.name:sha(p) for p in files}
    }
    (OUT/"stage5_summary.json").write_text(json.dumps(summary_json,indent=2),encoding="utf-8")
    print("STAGE5_SUMMARY="+json.dumps(summary_json,separators=(",",":")),flush=True)
    print((OUT/"STAGE5_RESULT.md").read_text(),flush=True)

if __name__=="__main__":
    main()
