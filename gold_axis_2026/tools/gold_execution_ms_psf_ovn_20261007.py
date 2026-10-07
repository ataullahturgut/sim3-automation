from pathlib import Path
import json, warnings
import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score, confusion_matrix

warnings.filterwarnings("ignore")

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
XFILES=[AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv",AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"]
MACRO=AX/"GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv"
PAIR=AX/"GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_PREDICTIONS_2026-10-07.csv"

OUTP=AX/"GOLD_EXECUTION_MS_PSF_OVN_PREDICTIONS_2026-10-07.csv"
OUTM=AX/"GOLD_EXECUTION_MS_PSF_OVN_METRICS_2026-10-07.csv"
OUTJ=AX/"GOLD_EXECUTION_MS_PSF_OVN_SUMMARY_2026-10-07.json"
OUTR=AX/"GOLD_EXECUTION_MS_PSF_OVN_RESULT_2026-10-07.md"

MIN_HMM=120
HMM_WINDOW=250
MIN_EXPERT=60
DOM=0.75

STATE_FEATURES=["ret3h","rv3h","semivol_balance","sign_changes","ll_area_norm","tp_area_norm"]
BASE_FEATURES=["ret3h","rv3h","semivol_balance","max_drawdown","sign_changes","r1600_1630","r1630_1700","ll_area_norm","tp_area_norm","pc1","pc2","macro_released","macro_max_abs_z","upcoming_fomc"]
PATHCOLS=[f"path{i:02d}" for i in range(12)]

def load15():
    xs=[]
    for p in XFILES:
        q=pd.read_csv(p,low_memory=False)
        q["ts"]=pd.to_datetime(q.dt_utc,utc=True,errors="raise")
        q["open"]=pd.to_numeric(q.open,errors="coerce");q["close"]=pd.to_numeric(q.close,errors="coerce")
        xs.append(q[["ts","open","close"]])
    q=pd.concat(xs,ignore_index=True).dropna().sort_values("ts").drop_duplicates("ts",keep="last")
    return q[(q.ts>="2022-01-01")&(q.ts<"2026-01-10")].set_index("ts")

def point(q,d,hm,col):
    h,m=map(int,hm.split(":"));ts=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=h,minutes=m)
    try:return float(q.at[ts,col])
    except KeyError:return np.nan

def lr(a,b):
    return float(np.log(b/a)) if np.isfinite(a) and np.isfinite(b) and a>0 and b>0 else np.nan

def signature2(points):
    pts=np.asarray(points,float);s1=np.zeros(pts.shape[1]);s2=np.zeros((pts.shape[1],pts.shape[1]))
    for i in range(1,len(pts)):
        dx=pts[i]-pts[i-1];s2+=np.outer(s1,dx)+0.5*np.outer(dx,dx);s1+=dx
    return s1,s2

def ll_area(cum):
    x=np.r_[0.0,np.asarray(cum,float)];pts=[(x[0],x[0])]
    for i in range(1,len(x)):pts.extend([(x[i],x[i-1]),(x[i],x[i])])
    _,s2=signature2(pts);return float(s2[0,1]-s2[1,0])

def tp_area(cum,rv):
    y=np.r_[0.0,np.asarray(cum,float)]/(rv+1e-12);t=np.linspace(0,1,len(y))
    _,s2=signature2(np.c_[t,y]);return float(s2[0,1]-s2[1,0])

def macro_table():
    m=pd.read_csv(MACRO,low_memory=False)
    m["event_ts_utc"]=pd.to_datetime(m.event_ts_utc,utc=True,errors="coerce")
    m["surprise_ready_at_utc"]=pd.to_datetime(m.surprise_ready_at_utc,utc=True,errors="coerce")
    m["surprise"]=pd.to_numeric(m.surprise,errors="coerce")
    m["pair_complete"]=m.pair_complete.astype(str).str.lower().eq("true")
    m=m.sort_values("event_ts_utc").reset_index(drop=True)
    zz=[]
    for _,r in m.iterrows():
        h=m[(m.event_type==r.event_type)&(m.event_ts_utc<r.event_ts_utc)&m.surprise.notna()]
        if len(h)>=6 and np.isfinite(r.surprise):
            sd=float(h.surprise.std(ddof=1));z=(float(r.surprise)-float(h.surprise.mean()))/sd if sd>1e-12 else np.nan
        else:z=np.nan
        zz.append(z)
    m["surprise_z_pit"]=zz
    return m

def macro_features(m,d,nxt):
    decision=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=14)
    end=pd.Timestamp(nxt,tz="UTC")+pd.Timedelta(hours=6)
    ld=pd.Timestamp(d).date()
    rel=m[(m.surprise_ready_at_utc.notna())&(m.surprise_ready_at_utc<=decision)&
          ((m.event_ts_utc+pd.Timedelta(hours=3)).dt.date==ld)&m.pair_complete]
    maxz=float(rel.surprise_z_pit.abs().max()) if len(rel) and rel.surprise_z_pit.notna().any() else 0.0
    upf=m[(m.event_type=="FOMC")&(m.event_ts_utc>decision)&(m.event_ts_utc<=end)]
    return float(len(rel)>0),maxz,float(len(upf)>0)

def build():
    q=load15();m=macro_table()
    dates=sorted({t.date() for t in q.index if t.hour==6 and t.minute==0})
    rows=[]
    for i,d in enumerate(dates[:-1]):
        nxt=dates[i+1];start=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=11)
        bars=[]
        for k in range(12):
            ts=start+pd.Timedelta(minutes=15*k)
            try:o=float(q.at[ts,"open"]);c=float(q.at[ts,"close"])
            except KeyError:o=c=np.nan
            bars.append((o,c))
        if not all(np.isfinite([z for b in bars for z in b])):continue
        p0=bars[0][0];cum=np.log(np.array([b[1] for b in bars])/p0);inc=np.diff(np.r_[0.0,cum])
        rv=float(np.sqrt(np.sum(inc**2)))
        pos=np.sqrt(np.sum(inc[inc>0]**2)) if np.any(inc>0) else 0.;neg=np.sqrt(np.sum(inc[inc<0]**2)) if np.any(inc<0) else 0.
        sem=float((pos-neg)/(pos+neg+1e-12))
        peak=np.maximum.accumulate(np.r_[0.0,cum]);mdd=float(np.min(np.r_[0.0,cum]-peak))
        s=np.sign(inc);s=s[s!=0];chg=float(np.sum(s[1:]!=s[:-1])) if len(s)>1 else 0.
        r1=lr(point(q,d,"13:00","open"),point(q,d,"13:15","close"))
        r2=lr(point(q,d,"13:30","open"),point(q,d,"13:45","close"))
        target=lr(point(q,d,"14:00","open"),point(q,nxt,"05:45","close"))
        mac,maxz,upf=macro_features(m,d,nxt)
        row={"date":pd.Timestamp(d),"year":d.year,"next_date":pd.Timestamp(nxt),
             "ret3h":float(cum[-1]),"rv3h":rv,"semivol_balance":sem,"max_drawdown":mdd,"sign_changes":chg,
             "r1600_1630":r1,"r1630_1700":r2,"ll_area_norm":ll_area(cum)/(rv*rv+1e-12),
             "tp_area_norm":tp_area(cum,rv),"macro_released":mac,"macro_max_abs_z":maxz,"upcoming_fomc":upf,
             "ret_target":target,"y":float(target>0) if np.isfinite(target) else np.nan}
        pn=cum/(rv+1e-12)
        for j,v in enumerate(pn):row[f"path{j:02d}"]=float(v)
        rows.append(row)
    return pd.DataFrame(rows)

def causal_regimes(d):
    d=d.copy().sort_values("date").reset_index(drop=True)
    ph=[]
    for i,r in d.iterrows():
        h=d.iloc[max(0,i-HMM_WINDOW):i].dropna(subset=STATE_FEATURES)
        if len(h)<MIN_HMM or r[STATE_FEATURES].isna().any():
            ph.append(np.nan);continue
        sc=StandardScaler().fit(h[STATE_FEATURES])
        xh=sc.transform(h[STATE_FEATURES]);xc=sc.transform(pd.DataFrame([r])[STATE_FEATURES])
        hmm=GaussianHMM(n_components=2,covariance_type="diag",n_iter=50,tol=1e-3,random_state=17)
        try:
            hmm.fit(xh)
            hi=int(np.argmax(hmm.means_[:,STATE_FEATURES.index("rv3h")]))
            post=hmm.predict_proba(np.vstack([xh,xc]))[-1]
            ph.append(float(post[hi]))
        except Exception:
            ph.append(np.nan)
    d["p_high"]=ph
    return d

def prepare_fpca(hist,row):
    pca=PCA(n_components=2,random_state=0).fit(hist[PATHCOLS])
    hh=hist.copy();rr=row.copy()
    z=pca.transform(hh[PATHCOLS]);hh["pc1"]=z[:,0];hh["pc2"]=z[:,1]
    zr=pca.transform(pd.DataFrame([rr])[PATHCOLS])[0];rr["pc1"]=float(zr[0]);rr["pc2"]=float(zr[1])
    return hh,rr

def fitlog(h,features):
    return make_pipeline(StandardScaler(),LogisticRegression(C=1.0,penalty="l2",solver="lbfgs",max_iter=3000)).fit(h[features],h.y.astype(int))

def one_pred(hist,row):
    hh,rr=prepare_fpca(hist,row)
    global_m=fitlog(hh,BASE_FEATURES)
    pglob=float(global_m.predict_proba(pd.DataFrame([rr])[BASE_FEATURES])[0,1])
    lo=hh[hh.p_high<.5];hi=hh[hh.p_high>=.5]
    if len(lo)>=MIN_EXPERT and lo.y.nunique()>1: ml=fitlog(lo,BASE_FEATURES);plo=float(ml.predict_proba(pd.DataFrame([rr])[BASE_FEATURES])[0,1])
    else:plo=pglob
    if len(hi)>=MIN_EXPERT and hi.y.nunique()>1: mh=fitlog(hi,BASE_FEATURES);phi=float(mh.predict_proba(pd.DataFrame([rr])[BASE_FEATURES])[0,1])
    else:phi=pglob
    q=float(rr.p_high);pmix=(1-q)*plo+q*phi
    agree=int(plo>=.5)==int(phi>=.5)
    agree_pred=int((plo+phi)/2>=.5)
    if agree:
        dom_active=True;dom_pred=agree_pred
    elif q>=DOM:
        dom_active=True;dom_pred=int(phi>=.5)
    elif q<=1-DOM:
        dom_active=True;dom_pred=int(plo>=.5)
    else:
        dom_active=False;dom_pred=int(pmix>=.5)
    return pglob,plo,phi,pmix,agree,agree_pred,dom_active,dom_pred

def frozen_models(tr):
    pca=PCA(n_components=2,random_state=0).fit(tr[PATHCOLS])
    hh=tr.copy();z=pca.transform(hh[PATHCOLS]);hh["pc1"]=z[:,0];hh["pc2"]=z[:,1]
    global_m=fitlog(hh,BASE_FEATURES)
    lo=hh[hh.p_high<.5];hi=hh[hh.p_high>=.5]
    ml=fitlog(lo,BASE_FEATURES) if len(lo)>=MIN_EXPERT and lo.y.nunique()>1 else global_m
    mh=fitlog(hi,BASE_FEATURES) if len(hi)>=MIN_EXPERT and hi.y.nunique()>1 else global_m
    return pca,global_m,ml,mh

def predict(d):
    q=d.dropna(subset=["y","p_high"]+PATHCOLS+[x for x in BASE_FEATURES if x not in ["pc1","pc2"]]).sort_values("date").reset_index(drop=True)
    rows=[]
    for _,r in q[q.year.isin([2023,2024])].iterrows():
        h=q[(q.date<r.date)&(q.next_date<=r.date)].copy()
        if len(h)<MIN_HMM or h.y.nunique()<2:continue
        pglob,plo,phi,pmix,agree,ap,da,dp=one_pred(h,r)
        rows.append({"date":r.date,"year":int(r.year),"period":"DEV","y":int(r.y),"p_high":float(r.p_high),
                     "p_global":pglob,"p_low":plo,"p_high_exp":phi,"p_mix":pmix,
                     "pred_global":int(pglob>=.5),"pred_mix":int(pmix>=.5),
                     "agree_active":bool(agree),"pred_agree":int(ap),"dominant_active":bool(da),"pred_dominant":int(dp)})
    tr=q[(q.year<=2024)&(q.next_date<=pd.Timestamp("2025-01-01"))].copy()
    te=q[q.year==2025].copy()
    pca,mg,ml,mh=frozen_models(tr)
    for _,r in te.iterrows():
        rr=r.copy();zr=pca.transform(pd.DataFrame([rr])[PATHCOLS])[0];rr["pc1"]=float(zr[0]);rr["pc2"]=float(zr[1])
        x=pd.DataFrame([rr])[BASE_FEATURES]
        pg=float(mg.predict_proba(x)[0,1]);pl=float(ml.predict_proba(x)[0,1]);ph=float(mh.predict_proba(x)[0,1]);qq=float(rr.p_high)
        pm=(1-qq)*pl+qq*ph;agree=int(pl>=.5)==int(ph>=.5);ap=int((pl+ph)/2>=.5)
        if agree: da=True;dp=ap
        elif qq>=DOM: da=True;dp=int(ph>=.5)
        elif qq<=1-DOM: da=True;dp=int(pl>=.5)
        else: da=False;dp=int(pm>=.5)
        rows.append({"date":r.date,"year":2025,"period":"TRANSPORT_2025","y":int(r.y),"p_high":qq,
                     "p_global":pg,"p_low":pl,"p_high_exp":ph,"p_mix":pm,
                     "pred_global":int(pg>=.5),"pred_mix":int(pm>=.5),
                     "agree_active":bool(agree),"pred_agree":int(ap),"dominant_active":bool(da),"pred_dominant":int(dp)})
    return pd.DataFrame(rows)

def metric(g,pred,active=None):
    x=g.copy()
    if active:x=x[x[active]]
    if not len(x):return dict(n=0,coverage=0,accuracy=np.nan,ba=np.nan,up_recall=np.nan,down_recall=np.nan)
    y=x.y.to_numpy(int);p=x[pred].to_numpy(int)
    return dict(n=len(x),coverage=len(x)/len(g),accuracy=float(accuracy_score(y,p)),ba=float(balanced_accuracy_score(y,p)),
                up_recall=float(recall_score(y,p,pos_label=1,zero_division=0)),down_recall=float(recall_score(y,p,pos_label=0,zero_division=0)))

def main():
    d=causal_regimes(build())
    p=predict(d)
    rows=[]
    for y in [2023,2024,2025]:
        g=p[p.year==y]
        for name,pred,active in [("GLOBAL_M4","pred_global",None),("MS_MIX_FULL","pred_mix",None),("MS_AGREE","pred_agree","agree_active"),("MS_DOMINANT75","pred_dominant","dominant_active")]:
            z=metric(g,pred,active);rows.append({"year":y,"model":name,**z})
    m=pd.DataFrame(rows)

    pair=pd.read_csv(PAIR,parse_dates=["date"])
    pair=pair[(pair.policy=="PAIR_ALL")&(pair.period=="TRANSPORT_2025")][["date","pred","y"]].drop_duplicates("date").rename(columns={"pred":"pair_pred","y":"pair_y"})
    c=p[p.year==2025].merge(pair,on="date",how="inner")
    common={}
    for name,pred,active in [("GLOBAL_M4","pred_global",None),("MS_MIX_FULL","pred_mix",None),("MS_AGREE","pred_agree","agree_active"),("MS_DOMINANT75","pred_dominant","dominant_active")]:
        x=c if active is None else c[c[active]]
        if len(x):
            z=metric(c,pred,active);bp=metric(x.rename(columns={"pair_pred":"_p"}),"_p",None)
            resc=int(((x[pred].astype(int)==x.y.astype(int))&(x.pair_pred.astype(int)!=x.y.astype(int))).sum())
            brk=int(((x[pred].astype(int)!=x.y.astype(int))&(x.pair_pred.astype(int)==x.y.astype(int))).sum())
            common[name]={"model":z,"pair_same_rows":bp,"rescue":resc,"break":brk,"net":resc-brk}

    summary={"status":"COMPLETE","selection_uses_2025":False,"hmm_states":2,"hmm_window":HMM_WINDOW,"dominant_threshold":DOM,
             "metrics":rows,"common_2025_vs_pair":common,
             "regime_occupancy":{str(y):{"n":int(len(p[p.year==y])),"mean_p_high":float(p[p.year==y].p_high.mean()),"high_share":float((p[p.year==y].p_high>=.5).mean()),"expert_disagree_share":float((~p[p.year==y].agree_active).mean())} for y in [2023,2024,2025]},
             "interpretation_rule":"No production claim unless both development years exceed 50 BA and 2025 transport is directionally coherent."}
    p.to_csv(OUTP,index=False);m.to_csv(OUTM,index=False);OUTJ.write_text(json.dumps(summary,indent=2)+"\n")
    def pct(x):return "NA" if x is None or not np.isfinite(float(x)) else f"{100*float(x):.2f}%"
    lines=["# GOLD EXECUTION MS-PSF OVERNIGHT RESULT — 2026-10-07","","**Status:** COMPLETE / FIXED TWO-STATE MARKOV-SWITCHING CHALLENGER","",
           "| Model | 2023 N | 2023 Cov | 2023 Acc | 2023 BA | 2024 N | 2024 Cov | 2024 Acc | 2024 BA | 2025 N | 2025 Cov | 2025 Acc | 2025 BA |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for model in ["GLOBAL_M4","MS_MIX_FULL","MS_AGREE","MS_DOMINANT75"]:
        z=[]
        for y in [2023,2024,2025]:z.append(m[(m.model==model)&(m.year==y)].iloc[0])
        lines.append(f"| {model} | {int(z[0].n)} | {pct(z[0].coverage)} | {pct(z[0].accuracy)} | {pct(z[0].ba)} | {int(z[1].n)} | {pct(z[1].coverage)} | {pct(z[1].accuracy)} | {pct(z[1].ba)} | {int(z[2].n)} | {pct(z[2].coverage)} | {pct(z[2].accuracy)} | {pct(z[2].ba)} |")
    lines += ["","## 2025 exact-common comparison with PAIR",""]
    for k,v in common.items():
        lines.append(f"- **{k}**: model Acc {pct(v['model']['accuracy'])}, BA {pct(v['model']['ba'])}; PAIR same rows Acc {pct(v['pair_same_rows']['accuracy'])}, BA {pct(v['pair_same_rows']['ba'])}; rescue/break/net {v['rescue']}/{v['break']}/{v['net']:+d}.")
    OUTR.write_text("\n".join(lines)+"\n")
    print(OUTR.read_text());print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
