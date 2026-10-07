from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score, precision_score, brier_score_loss, log_loss, confusion_matrix

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
XFILES=[AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv",AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"]
MACRO=AX/"GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv"
PAIR=AX/"GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_PREDICTIONS_2026-10-07.csv"
RFR=AX/"GOLD_EXECUTION_RFR_NOMACRO_ROWS_2026-10-07.csv"

OUTP=AX/"GOLD_EXECUTION_PSF_OVN_PREDICTIONS_2026-10-07.csv"
OUTM=AX/"GOLD_EXECUTION_PSF_OVN_METRICS_2026-10-07.csv"
OUTC=AX/"GOLD_EXECUTION_PSF_OVN_COMMON_2025_2026-10-07.csv"
OUTJ=AX/"GOLD_EXECUTION_PSF_OVN_SUMMARY_2026-10-07.json"
OUTR=AX/"GOLD_EXECUTION_PSF_OVN_RESULT_2026-10-07.md"

MIN_TRAIN=120
THRESHOLDS=[0.00,0.05,0.10,0.15]

FAMILIES={
 "M0_SCALAR":["ret3h","rv3h","semivol_balance","max_drawdown","sign_changes","r1600_1630","r1630_1700"],
 "M1_SIGNATURE":["ret3h","rv3h","semivol_balance","max_drawdown","sign_changes","r1600_1630","r1630_1700","ll_area_norm","tp_area_norm"],
 "M2_FPCA":["ret3h","rv3h","semivol_balance","max_drawdown","sign_changes","r1600_1630","r1630_1700","pc1","pc2"],
 "M3_SIG_FPCA":["ret3h","rv3h","semivol_balance","max_drawdown","sign_changes","r1600_1630","r1630_1700","ll_area_norm","tp_area_norm","pc1","pc2"],
 "M4_SIG_FPCA_MACRO":["ret3h","rv3h","semivol_balance","max_drawdown","sign_changes","r1600_1630","r1630_1700","ll_area_norm","tp_area_norm","pc1","pc2","macro_released","macro_max_abs_z","upcoming_fomc"],
}

def load15():
    xs=[]
    for p in XFILES:
        q=pd.read_csv(p,low_memory=False)
        if not {"dt_utc","open","close"}.issubset(q.columns): raise RuntimeError("SCHEMA_FAIL:"+p.name)
        q["ts"]=pd.to_datetime(q.dt_utc,utc=True,errors="raise")
        q["open"]=pd.to_numeric(q.open,errors="coerce"); q["close"]=pd.to_numeric(q.close,errors="coerce")
        xs.append(q[["ts","open","close"]])
    q=pd.concat(xs,ignore_index=True).dropna().sort_values("ts").drop_duplicates("ts",keep="last")
    return q[(q.ts>="2022-01-01")&(q.ts<"2026-01-10")].set_index("ts")

def point(q,d,hm,col):
    h,m=map(int,hm.split(":"))
    ts=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=h,minutes=m)
    try:return float(q.at[ts,col])
    except KeyError:return np.nan

def lret(a,b):
    return float(np.log(b/a)) if np.isfinite(a) and np.isfinite(b) and a>0 and b>0 else np.nan

def signature2(points):
    pts=np.asarray(points,float)
    s1=np.zeros(pts.shape[1],float)
    s2=np.zeros((pts.shape[1],pts.shape[1]),float)
    for i in range(1,len(pts)):
        dx=pts[i]-pts[i-1]
        s2 += np.outer(s1,dx)+0.5*np.outer(dx,dx)
        s1 += dx
    return s1,s2

def leadlag_area(cum):
    x=np.r_[0.0,np.asarray(cum,float)]
    pts=[(x[0],x[0])]
    for i in range(1,len(x)):
        pts.append((x[i],x[i-1]))
        pts.append((x[i],x[i]))
    _,s2=signature2(pts)
    return float(s2[0,1]-s2[1,0])

def timeprice_area(cum,rv):
    y=np.r_[0.0,np.asarray(cum,float)]
    yn=y/(rv+1e-12)
    t=np.linspace(0,1,len(y))
    _,s2=signature2(np.column_stack([t,yn]))
    return float(s2[0,1]-s2[1,0])

def macro_table():
    m=pd.read_csv(MACRO,low_memory=False)
    for c in ["event_ts_utc","surprise_ready_at_utc"]:
        m[c]=pd.to_datetime(m[c],utc=True,errors="coerce")
    m["surprise"]=pd.to_numeric(m.surprise,errors="coerce")
    m["pair_complete"]=m.pair_complete.astype(str).str.lower().eq("true")
    m=m.sort_values("event_ts_utc").reset_index(drop=True)
    zs=[]
    for _,r in m.iterrows():
        h=m[(m.event_type==r.event_type)&(m.event_ts_utc<r.event_ts_utc)&m.surprise.notna()]
        if len(h)>=6 and np.isfinite(r.surprise):
            sd=float(h.surprise.std(ddof=1)); z=(float(r.surprise)-float(h.surprise.mean()))/sd if sd>1e-12 else np.nan
        else:z=np.nan
        zs.append(z)
    m["surprise_z_pit"]=zs
    return m

def macro_features(m,d,nxt):
    decision=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=14) # 17 TRT
    end=pd.Timestamp(nxt,tz="UTC")+pd.Timedelta(hours=6) if nxt is not None else decision
    ld=pd.Timestamp(d).date()
    rel=m[(m.surprise_ready_at_utc.notna())&(m.surprise_ready_at_utc<=decision)&
          ((m.event_ts_utc+pd.Timedelta(hours=3)).dt.date==ld)&m.pair_complete]
    maxz=float(rel.surprise_z_pit.abs().max()) if len(rel) and rel.surprise_z_pit.notna().any() else 0.0
    upf=m[(m.event_type=="FOMC")&(m.event_ts_utc>decision)&(m.event_ts_utc<=end)]
    return float(len(rel)>0),maxz,float(len(upf)>0)

def build(q,m):
    dates=sorted({t.date() for t in q.index if t.hour==6 and t.minute==0})
    rows=[]
    for i,d in enumerate(dates[:-1]):
        nxt=dates[i+1]
        start=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=11) # 14 TRT
        bars=[]
        for k in range(12):
            ts=start+pd.Timedelta(minutes=15*k)
            try:o=float(q.at[ts,"open"]);c=float(q.at[ts,"close"])
            except KeyError:o=c=np.nan
            bars.append((o,c))
        if not all(np.isfinite([z for b in bars for z in b])):
            continue
        p0=bars[0][0]
        closes=np.array([b[1] for b in bars],float)
        cum=np.log(closes/p0)
        inc=np.diff(np.r_[0.0,cum])
        rv=float(np.sqrt(np.sum(inc**2)))
        pos=np.sqrt(np.sum(np.square(inc[inc>0]))) if np.any(inc>0) else 0.0
        neg=np.sqrt(np.sum(np.square(inc[inc<0]))) if np.any(inc<0) else 0.0
        semibal=float((pos-neg)/(pos+neg+1e-12))
        peak=np.maximum.accumulate(np.r_[0.0,cum])
        dd=np.r_[0.0,cum]-peak
        mdd=float(np.min(dd))
        signs=np.sign(inc)
        nz=signs[signs!=0]
        changes=int(np.sum(nz[1:]!=nz[:-1])) if len(nz)>1 else 0
        r1=lret(point(q,d,"13:00","open"),point(q,d,"13:15","close"))
        r2=lret(point(q,d,"13:30","open"),point(q,d,"13:45","close"))
        ll=leadlag_area(cum)/(rv*rv+1e-12)
        tp=timeprice_area(cum,rv)
        target=lret(point(q,d,"14:00","open"),point(q,nxt,"05:45","close"))
        mac,maxz,upf=macro_features(m,d,nxt)
        pathnorm=cum/(rv+1e-12)
        row={"date":pd.Timestamp(d),"year":d.year,"next_date":pd.Timestamp(nxt),
             "ret3h":float(cum[-1]),"rv3h":rv,"semivol_balance":semibal,"max_drawdown":mdd,
             "sign_changes":float(changes),"r1600_1630":r1,"r1630_1700":r2,
             "ll_area_norm":ll,"tp_area_norm":tp,"macro_released":mac,
             "macro_max_abs_z":maxz,"upcoming_fomc":upf,"ret_target":target,
             "y":float(target>0) if np.isfinite(target) else np.nan}
        for j,v in enumerate(pathnorm): row[f"path{j:02d}"]=float(v)
        rows.append(row)
    return pd.DataFrame(rows)

PATHCOLS=[f"path{i:02d}" for i in range(12)]

def fit_family(hist,row,fam):
    pca=None
    h=hist.copy()
    rr=row.copy()
    if "pc1" in FAMILIES[fam]:
        pca=PCA(n_components=2,random_state=0)
        pcs=pca.fit_transform(h[PATHCOLS].to_numpy(float))
        h["pc1"]=pcs[:,0];h["pc2"]=pcs[:,1]
        pr=pca.transform(rr[PATHCOLS].to_numpy(float).reshape(1,-1))[0]
        rr["pc1"]=float(pr[0]);rr["pc2"]=float(pr[1])
    feats=FAMILIES[fam]
    model=make_pipeline(StandardScaler(),LogisticRegression(C=1.0,penalty="l2",solver="lbfgs",max_iter=3000))
    model.fit(h[feats],h.y.astype(int))
    p=float(model.predict_proba(pd.DataFrame([rr])[feats])[0,1])
    return p

def frozen_models(tr,te):
    outs={}
    for fam in FAMILIES:
        h=tr.copy();t=te.copy()
        pca=None
        if "pc1" in FAMILIES[fam]:
            pca=PCA(n_components=2,random_state=0)
            pcs=pca.fit_transform(h[PATHCOLS].to_numpy(float))
            h["pc1"]=pcs[:,0];h["pc2"]=pcs[:,1]
            pcs2=pca.transform(t[PATHCOLS].to_numpy(float))
            t["pc1"]=pcs2[:,0];t["pc2"]=pcs2[:,1]
        feats=FAMILIES[fam]
        model=make_pipeline(StandardScaler(),LogisticRegression(C=1.0,penalty="l2",solver="lbfgs",max_iter=3000))
        model.fit(h[feats],h.y.astype(int))
        outs[fam]=model.predict_proba(t[feats])[:,1]
    return outs

def predictions(d):
    q=d.dropna(subset=["y"]+PATHCOLS+list(set(sum(FAMILIES.values(),[]))-{"pc1","pc2"})).sort_values("date").reset_index(drop=True)
    rows=[]
    for _,r in q[q.year.isin([2023,2024])].iterrows():
        h=q[(q.date<r.date)&(q.next_date<=r.date)].copy()
        if len(h)<MIN_TRAIN or h.y.nunique()<2: continue
        for fam in FAMILIES:
            p=fit_family(h,r,fam)
            rows.append({"date":r.date,"year":int(r.year),"period":"DEV","family":fam,"train_n":len(h),
                         "p_up":p,"pred":int(p>=.5),"y":int(r.y),"ret_target":float(r.ret_target)})
    tr=q[(q.year<=2024)&(q.next_date<=pd.Timestamp("2025-01-01"))].copy()
    te=q[q.year==2025].copy()
    outs=frozen_models(tr,te)
    for fam,pp in outs.items():
        for (_,r),p in zip(te.iterrows(),pp):
            rows.append({"date":r.date,"year":2025,"period":"TRANSPORT_2025","family":fam,"train_n":len(tr),
                         "p_up":float(p),"pred":int(p>=.5),"y":int(r.y),"ret_target":float(r.ret_target)})
    return pd.DataFrame(rows)

def calc(g,threshold=0.0):
    x=g[np.abs(g.p_up-.5)>=threshold].copy()
    if len(x)==0:return dict(n=0,coverage=0,accuracy=np.nan,ba=np.nan,up_recall=np.nan,down_recall=np.nan,up_precision=np.nan,down_precision=np.nan,brier=np.nan,log_loss=np.nan,pred_up_rate=np.nan,tn=0,fp=0,fn=0,tp=0)
    y=x.y.astype(int).to_numpy();p=x.pred.astype(int).to_numpy();pr=np.clip(x.p_up.to_numpy(float),1e-6,1-1e-6)
    tn,fp,fn,tp=map(int,confusion_matrix(y,p,labels=[0,1]).ravel())
    return dict(n=len(x),coverage=len(x)/len(g),accuracy=float(accuracy_score(y,p)),ba=float(balanced_accuracy_score(y,p)),
                up_recall=float(recall_score(y,p,pos_label=1,zero_division=0)),down_recall=float(recall_score(y,p,pos_label=0,zero_division=0)),
                up_precision=float(precision_score(y,p,pos_label=1,zero_division=0)),down_precision=float(precision_score(y,p,pos_label=0,zero_division=0)),
                brier=float(brier_score_loss(y,pr)),log_loss=float(log_loss(y,pr,labels=[0,1])),
                pred_up_rate=float(np.mean(p)),tn=tn,fp=fp,fn=fn,tp=tp)

def metric_table(p):
    rows=[]
    for fam in FAMILIES:
        for year in [2023,2024,2025]:
            g=p[(p.family==fam)&(p.year==year)]
            if len(g):
                z=calc(g,0);rows.append({"family":fam,"year":year,"threshold":0.0,**z})
        for th in THRESHOLDS:
            g=p[(p.family==fam)&(p.year==2023)]
            if len(g):
                z=calc(g,th);rows.append({"family":fam,"year":"2023_SELECTIVE","threshold":th,**z})
    return pd.DataFrame(rows)

def choose_family(m):
    z=m[(m.year==2023)&(m.threshold==0)].copy()
    z["nfeat"]=z.family.map(lambda x:len(FAMILIES[x]))
    z=z.sort_values(["ba","brier","nfeat"],ascending=[False,True,True])
    return str(z.iloc[0].family)

def choose_threshold(p,fam):
    g=p[(p.family==fam)&(p.year==2023)].copy()
    cand=[]
    for th in THRESHOLDS:
        z=calc(g,th)
        elig=z["coverage"]>=.30 and z["n"]>=60 and .10<=z["pred_up_rate"]<=.90
        cand.append({"threshold":th,"eligible":bool(elig),**z})
    cand=sorted(cand,key=lambda x:((x["ba"] if x["eligible"] else -1),x["coverage"]),reverse=True)
    return float(cand[0]["threshold"]),cand

def merge_common_2025(p,fam,th):
    q=p[(p.family==fam)&(p.year==2025)][["date","y","p_up","pred"]].copy()
    q["psf_active"]=np.abs(q.p_up-.5)>=th
    pair=pd.read_csv(PAIR,parse_dates=["date"])
    pair=pair[(pair.policy=="PAIR_ALL")&(pair.period=="TRANSPORT_2025")][["date","pred","y"]].drop_duplicates("date").rename(columns={"pred":"pair_pred","y":"pair_y"})
    rfr=pd.read_csv(RFR,parse_dates=["date"])
    rfr=rfr[rfr.year.eq(2025)][["date","rule_pred","eligible_nomacro"]].drop_duplicates("date")
    q=q.merge(pair,on="date",how="left").merge(rfr,on="date",how="left")
    q["psf_correct"]=q.pred.astype(int).eq(q.y.astype(int))
    q["pair_correct"]=np.where(q.pair_pred.notna(),q.pair_pred.astype("Int64").eq(q.y.astype(int)),np.nan)
    q["rfr_correct"]=np.where(q.rule_pred.notna(),q.rule_pred.astype("Int64").eq(q.y.astype(int)),np.nan)
    return q

def main():
    d=build(load15(),macro_table())
    p=predictions(d)
    m=metric_table(p)
    selected=choose_family(m)
    th,ranking=choose_threshold(p,selected)

    def yr(y,threshold=0):
        g=p[(p.family==selected)&(p.year==y)]
        return calc(g,threshold)
    full23,full24,full25=yr(2023),yr(2024),yr(2025)
    sel23,sel24,sel25=yr(2023,th),yr(2024,th),yr(2025,th)
    confirm_family=bool(full24["ba"]>.50 and full24["up_recall"]>=.35 and full24["down_recall"]>=.35)
    m0_24=calc(p[(p.family=="M0_SCALAR")&(p.year==2024)])
    confirm_family=confirm_family and full24["ba"]>=m0_24["ba"]-.02
    confirm_selective=bool(sel24["n"]>=60 and sel24["ba"]>full24["ba"] and sel24["up_recall"]>=.35 and sel24["down_recall"]>=.35)

    common=merge_common_2025(p,selected,th)
    common.to_csv(OUTC,index=False)

    summary={
      "status":"COMPLETE",
      "selected_family_2023_only":selected,
      "selected_family_features":FAMILIES[selected],
      "family_confirmation_2024":confirm_family,
      "selected_threshold_2023_only":th,
      "threshold_ranking_2023":ranking,
      "selective_confirmation_2024":confirm_selective,
      "metrics":{"full_2023":full23,"full_2024":full24,"full_2025":full25,
                 "selective_2023":sel23,"selective_2024":sel24,"selective_2025":sel25,
                 "m0_2024":m0_24},
      "selection_uses_2025":False,
      "transport_note":"2025 is retrospective frozen transport; no family/threshold tuning uses 2025."
    }
    p.to_csv(OUTP,index=False);m.to_csv(OUTM,index=False);OUTJ.write_text(json.dumps(summary,indent=2)+"\n")
    def pct(x):return "NA" if x is None or not np.isfinite(float(x)) else f"{100*float(x):.2f}%"
    lines=["# GOLD EXECUTION PSF-OVN RESULT — 2026-10-07","",
           "**Status:** COMPLETE / PREREGISTERED PATH-REPRESENTATION CHALLENGER","",
           "Family selection uses 2023 only; 2024 is confirmation; 2025 is frozen retrospective transport.","",
           "## Family comparison","",
           "| Family | 2023 BA | 2023 Brier | 2024 BA | 2025 BA | 2025 Acc |",
           "|---|---:|---:|---:|---:|---:|"]
    for fam in FAMILIES:
        z23=calc(p[(p.family==fam)&(p.year==2023)]);z24=calc(p[(p.family==fam)&(p.year==2024)]);z25=calc(p[(p.family==fam)&(p.year==2025)])
        lines.append(f"| {fam} | {pct(z23['ba'])} | {z23['brier']:.4f} | {pct(z24['ba'])} | {pct(z25['ba'])} | {pct(z25['accuracy'])} |")
    lines += ["",f"2023-selected family: **{selected}**.",f"2024 family confirmation: **{confirm_family}**.","",
              "## Selective layer","",
              f"2023-selected confidence threshold: **|p-0.5| >= {th:.2f}**.",
              f"2024 selective confirmation: **{confirm_selective}**.","",
              "| Period | Full N | Full Acc | Full BA | Select N | Coverage | Select Acc | Select BA |",
              "|---|---:|---:|---:|---:|---:|---:|---:|",
              f"| 2023 | {full23['n']} | {pct(full23['accuracy'])} | {pct(full23['ba'])} | {sel23['n']} | {pct(sel23['coverage'])} | {pct(sel23['accuracy'])} | {pct(sel23['ba'])} |",
              f"| 2024 | {full24['n']} | {pct(full24['accuracy'])} | {pct(full24['ba'])} | {sel24['n']} | {pct(sel24['coverage'])} | {pct(sel24['accuracy'])} | {pct(sel24['ba'])} |",
              f"| 2025 | {full25['n']} | {pct(full25['accuracy'])} | {pct(full25['ba'])} | {sel25['n']} | {pct(sel25['coverage'])} | {pct(sel25['accuracy'])} | {pct(sel25['ba'])} |",
              "",
              "Interpretation: promotion requires 2024 confirmation. 2025 is transport evidence only and cannot rescue a failed 2024 confirmation."]
    OUTR.write_text("\n".join(lines)+"\n")
    print(OUTR.read_text());print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
