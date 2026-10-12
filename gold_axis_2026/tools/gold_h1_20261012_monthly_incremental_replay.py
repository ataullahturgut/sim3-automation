"""H1 2026-10-12: deterministic expanding monthly residual diagnostic, no fitting after target.
Inputs archived/reconstructed; WB origin mean not PIT-proven; NEVER a live backtest.
"""
import csv,json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"GOLD_H1_20261012_MONTHLY_ARCHIVE_INPUT_ROWS.csv"
E=ROOT/"GOLD_H1_20261012_MONTHLY_SCORE_ROWS.csv"
S=ROOT/"GOLD_H1_20261012_MONTHLY_RESULTS.json"

def monthshift(s,n):
    y,m=map(int,s.split("-"))
    z=y*12+m-1+n
    return f"{z//12:04d}-{z%12+1:02d}"

def pred(tr,r,features):
    y=np.array([v["y"] for v in tr],float)
    ybar=float(y.mean())
    if not features:return ybar
    x=np.array([[v[f] for f in features] for v in tr],float)
    avg=x.mean(0); st=x.std(0); st[st<1e-10]=1
    z=(x-avg)/st
    beta=np.linalg.solve(z.T@z+10*np.eye(len(features)),z.T@(y-ybar))
    return ybar+float(np.dot((np.array([r[f] for f in features])-avg)/st,beta))

def main():
    with D.open(newline="") as f:
        d=list(csv.DictReader(f))
    assert len(d)==199
    mapping={v["month_key"]:v for v in d}
    def numeric(r,k):return float(r[k])
    sam=[]
    for v in d:
        p=mapping.get(monthshift(v["month_key"],-1))
        pp=mapping.get(monthshift(v["month_key"],-2))
        if not p or not pp:continue
        ks=[v["wb_avg"],p["wb_avg"],p["au_mean"],p["au_last"],pp["au_last"]]
        for met in ("ag","pt","pd"):ks.extend([p[met+"_last"],pp[met+"_last"]])
        if not all(z and float(z)>0 for z in ks):continue
        k=numeric(p,"wb_avg")*numeric(p,"au_last")/numeric(p,"au_mean")
        au=math.log(numeric(p,"au_last")/numeric(pp,"au_last"))
        cross=sum(math.log(numeric(p,met+"_last")/numeric(pp,met+"_last")) for met in ("ag","pt","pd"))/3-au
        sam.append({"target":v["month_key"],"y":math.log(numeric(v,"wb_avg")/k),
           "actual":numeric(v,"wb_avg"),"K":k,"au":au,"cross":cross})
    expected={}
    with E.open(newline="") as f:
        for r in csv.DictReader(f):expected[r["target"]]=r
    assert len(expected)==108
    for i,r in enumerate(sam):
        if not "2016-01"<=r["target"]<="2024-12":continue
        tr=[u for u in sam[:i] if u["target"]>="2012-01"]
        assert len(tr)>=36
        e=expected[r["target"]]
        assert int(e["train_n"])==len(tr)
        for k,features in [("BASE",[]),("B1",["au"]),("B2",["cross"]),("B12",["au","cross"])]:
            yhat=pred(tr,r,features)
            loss=(r["y"]-yhat)**2
            price=r["K"]*math.exp(yhat)
            for key,x in [(f"{k}_forecast_residual",yhat),
                          (f"{k}_forecast_WB_mean",price),
                          (f"{k}_squared_loss",loss),
                          (f"{k}_price_AE",abs(r["actual"]-price))]:
                assert abs(float(e[key])-x)<1e-8,(r["target"],key,x,e[key])
    j=json.loads(S.read_text())
    assert j["n"]==108
    assert j["conclusion"]=="REJECT_NO_PROMOTION"
    assert all(j["results"]["score"][k]["R2OS"]<0 for k in ("B1","B2","B12"))
    print("H1 PASS: 108 monthly replay rows agree with frozen source and fixed ridge; NO PROMOTION.")
if __name__=="__main__":main()
