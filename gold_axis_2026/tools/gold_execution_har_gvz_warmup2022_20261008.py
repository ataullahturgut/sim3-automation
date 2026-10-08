"""Reproducible strict PIT overnight >1% magnitude-risk forecasts, 2022 warm-up.

Scientific status: ARCHIVED-HISTORICAL CHALLENGER; 2025 research archive was
previously accessed, so no truly untouched OOS or investment promotion.
At each Istanbul 17:00 origin, features use previous completed overnights
and Cboe GVZ official daily close with date < issue date (D-1 contract).
The target is log(XAU close of next eligible 05:45 UTC 15m bar /
                    XAU open of origin 14:00 UTC 15m bar).
2022 is ONLY model warm-up; 2023-24 expanding prequential; 2025 fit fixed
to all <=2024 training rows. No 2025 y enters the fit.
Not a canonical estimated HAR-RV; fixed multi-horizon HAR-inspired proxy.
"""
from pathlib import Path
import numpy as np
import pandas as pd

AX = Path(__file__).resolve().parents[1]
RAW22 = AX / "GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv"
RAW35 = AX / "GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
GVZ = AX / "GOLD_GVZCLS_RAW_2021_2025.csv"
PSF = AX / "GOLD_EXECUTION_PSF_OVN_PREDICTIONS_2026-10-07.csv"
PRED = AX / "GOLD_OVN_2022_WARMUP_GVZ_TAIL1_PREDICTIONS_2026-10-08.csv"
MET = AX / "GOLD_OVN_2022_WARMUP_GVZ_TAIL1_METRICS_2026-10-08.csv"

def build():
    q = pd.concat([
        pd.read_csv(p, usecols=["dt_utc","open","close"], low_memory=False)
        for p in [RAW22,RAW35]
    ], ignore_index=True)
    q["ts"] = pd.to_datetime(q.dt_utc, utc=True, errors="raise")
    q["open"] = pd.to_numeric(q.open,errors="coerce")
    q["close"] = pd.to_numeric(q.close,errors="coerce")
    q = q.sort_values("ts", kind="stable").drop_duplicates("ts", keep="last")
    q["date"] = q.ts.dt.strftime("%Y-%m-%d")
    q["hm"] = q.ts.dt.strftime("%H:%M")
    # Only dates with a UTC 06:00 price; do not bridge to unqualified holidays.
    dates = sorted(q.loc[q.hm.eq("06:00"),"date"].unique())
    marks = q[q.hm.isin(["14:00","05:45"])][["date","hm","open","close"]]
    starts = marks[marks.hm.eq("14:00")].set_index("date")["open"].to_dict()
    ends = marks[marks.hm.eq("05:45")].set_index("date")["close"].to_dict()
    arr = []
    for d,next_d in zip(dates[:-1], dates[1:]):
        start,finish=starts.get(d),ends.get(next_d)
        if start is not None and finish is not None and start>0 and finish>0:
            arr.append({"date":d,"year":int(d[:4]),"nextDate":next_d,
                        "r":float(np.log(finish/start))})
    z = pd.DataFrame(arr).sort_values("date").reset_index(drop=True)
    z["y"] = z.r.abs().ge(.01).astype(int)
    for w in (5,20,60):
        z[f"rv{w}"] = np.sqrt(z.r.pow(2).shift(1).rolling(w,min_periods=w).mean())
    z["score"] = np.sqrt(.5*z.rv5.pow(2)+.3*z.rv20.pow(2)+.2*z.rv60.pow(2))
    g = pd.read_csv(GVZ).sort_values("date").reset_index(drop=True)
    g["value"] = pd.to_numeric(g.value,errors="coerce")
    # ISO YYYY-MM-DD lexicographic ordering exactly matches calendar order.
    # Strict '<' D-1 readiness; no same-date options close is consumed.
    source_dates = g.date.to_numpy(dtype=str)
    asof_idx = np.searchsorted(source_dates,z.date.to_numpy(dtype=str),side="left") - 1
    assert (asof_idx >= 0).all()
    z["gvz"] = g.value.to_numpy(dtype=float)[asof_idx]
    z["gvzAsOf"] = source_dates[asof_idx]
    ref = pd.read_csv(PSF)
    ref = ref[ref.family.eq("M4_SIG_FPCA_MACRO")][["date","ret_target"]]
    rr = ref.merge(z[["date","r"]],on="date",validate="one_to_one")
    assert len(rr)==769, ("MISSING_ORIGIN_TARGET",len(rr))
    assert float((rr.ret_target-rr.r).abs().max())<1e-9, "TARGET_PRICE_MISMATCH"
    z = z[z.year.between(2022,2025) & z.score.notna() & z.gvz.notna()].copy()
    z = z[(z.year.le(2024)) | z.date.isin(ref.date)].reset_index(drop=True)
    assert z.groupby("year").size().to_dict()=={2022:199,2023:256,2024:259,2025:254}
    assert (z.gvzAsOf < z.date).all()
    assert (z["nextDate"] > z.date).all()
    return z

def sigmoid(x):
    return 1/(1+np.exp(-np.clip(x,-25,25)))

def fit_model(train, columns, l2=5.0):
    xx=np.column_stack([np.log(train[col].to_numpy(float)) for col in columns])
    yy=train.y.to_numpy(float)
    mean=xx.mean(axis=0)
    sd=np.sqrt(np.mean((xx-mean)**2,axis=0))
    sd=np.where(sd<=0,1,sd)
    X=np.column_stack([np.ones(len(train)),(xx-mean)/sd])
    b=np.zeros(X.shape[1])
    prior=float((1+yy.sum())/(2+len(yy)))
    b[0]=np.log(prior/(1-prior))
    penalty=np.diag(np.array([0.0]+[l2]*len(columns)))
    for _ in range(35):
        pp=sigmoid(X@b)
        ww=pp*(1-pp)
        grad=X.T@(yy-pp)-penalty@b
        H=X.T@(X*ww[:,None])+penalty+np.diag([1e-5]+[0.0]*len(columns))
        step=np.linalg.solve(H,grad)
        b=b+step
        if float(step@step)<1e-10:break
    def predict(row):
        xr=np.log(np.array([float(row[col]) for col in columns]))
        return float(sigmoid(b[0]+((xr-mean)/sd)@b[1:]))
    return predict

def main():
    q=build()
    frozen=q[q.year<=2024]
    frozen_models={name:fit_model(frozen,cols) for name,cols in
                   {"HAR":["score"],"GVZ":["gvz"],"HAR_GVZ":["score","gvz"]}.items()}
    out=[]
    for i,row in q.iterrows():
        if int(row.year)<2023:continue
        hist=frozen if int(row.year)==2025 else q.iloc[:i]
        assert len(hist)>=120 and (hist.date < row.date).all()
        prior=(1+hist.y.sum())/(2+len(hist))
        scores={}
        for name,cols in {"HAR":["score"],"GVZ":["gvz"],"HAR_GVZ":["score","gvz"]}.items():
            fn=frozen_models[name] if int(row.year)==2025 else fit_model(hist,cols)
            scores[name]=fn(row)
        out.append({"date":row.date,"year":int(row.year),"nextDate":row.nextDate,
                    "trainN":len(hist),"gvzAsOf":row.gvzAsOf,"r":float(row.r),
                    "y":int(row.y),"rv5":float(row.rv5),"rv20":float(row.rv20),
                    "rv60":float(row.rv60),"score":float(row.score),"gvz":float(row.gvz),
                    "p0":prior,**scores})
    p=pd.DataFrame(out)
    assert p.groupby("year").size().to_dict()=={2023:256,2024:259,2025:254}
    assert len(p)==769
    metrics=[]
    for year,v in p.groupby("year"):
        n=len(v)
        brier={name:float(np.mean((v[name]-v.y)**2)) for name in ("p0","HAR","GVZ","HAR_GVZ")}
        def auc(x):
            # rank AUC with tied ranks, no external fitting
            pos=v.y.astype(bool)
            ranks=v[x].rank(method="average")
            npos=int(pos.sum());nneg=n-npos
            return float((ranks[pos].sum()-npos*(npos+1)/2)/(npos*nneg))
        logloss=lambda key:float(np.mean(-v.y*np.log(v[key])-(1-v.y)*np.log(1-v[key])))
        metrics.append({"year":year,"n":n,"tail_events":int(v.y.sum()),
                        "brier_base":brier["p0"],"brier_har":brier["HAR"],
                        "brier_gvz":brier["GVZ"],"brier_har_gvz":brier["HAR_GVZ"],
                        "delta_base_minus_har_gvz":brier["p0"]-brier["HAR_GVZ"],
                        "delta_har_minus_har_gvz":brier["HAR"]-brier["HAR_GVZ"],
                        "auc_har_gvz":auc("HAR_GVZ"),"auc_har":auc("HAR"),
                        "auc_gvz":auc("GVZ"),
                        "logloss_har_gvz":logloss("HAR_GVZ"),"logloss_base":logloss("p0"),
                        "mean_forecast":float(v.HAR_GVZ.mean())})
    m=pd.DataFrame(metrics)
    assert abs(float(m.loc[m.year.eq(2025),"brier_har_gvz"].iloc[0])-0.13127657532647113)<1e-8
    assert abs(float(m.loc[m.year.eq(2023),"brier_har_gvz"].iloc[0])-0.08745701034158115)<1e-8
    # The immutable script is the authority for future reproduction. Comparing
    # against published CSVs must precede overwrite in an independent replay.
    if PRED.exists() and MET.exists():
        old=pd.read_csv(MET).set_index("year")
        delta=(old.brier_har_gvz-m.set_index("year").brier_har_gvz).abs().max()
        assert delta<1e-8,("EXISTING_REPORT_MISMATCH",delta)
        predold=pd.read_csv(PRED)
        assert len(predold)==len(p)
        assert (predold.date.to_numpy()==p.date.to_numpy()).all()
        assert float(np.max(np.abs(predold.HAR_GVZ.to_numpy()-p.HAR_GVZ.to_numpy())))<1e-8
    else:
        p.to_csv(PRED,index=False)
        m.to_csv(MET,index=False)
    print("RESULT PASS: 769/769 targets; D-1 GVZ; 199 2022 risk warm-up rows.")
    print(m.to_string(index=False))

if __name__=="__main__":
    main()
