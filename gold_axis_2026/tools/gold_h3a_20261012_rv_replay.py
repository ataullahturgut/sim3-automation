"""H3A recompute strict realized-variance model predictions from archived M15 session RV rows.
Read only, no Neon auth, no model modifications. Requires numpy.
"""
import csv, math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
INPUT="GOLD_H3A_20261012_SESSION_RV_{}.csv"
SCORED=ROOT/"GOLD_H3A_20261012_FIXED_HAR_SCORE_ROWS.csv"
def fit(train):
    y=np.array([r["y"] for r in train])
    x=np.array([r["x"] for r in train])
    ym=y.mean();xm=x.mean(axis=0);sd=x.std(axis=0);sd[sd<1e-14]=1.
    z=(x-xm)/sd
    beta=np.linalg.solve(z.T@z+10*np.eye(3),z.T@(y-ym))
    return float(ym),xm,sd,beta
def forecast(mod,x):
    ym,xm,sd,beta=mod
    return ym+float(np.dot((np.array(x)-xm)/sd,beta))
def main():
    src=[]
    for year in range(2020,2026):
        with (ROOT/INPUT.format(year)).open(newline="") as f:
            for r in csv.DictReader(f):
                q={k:float(r[k]) if k in ("rv","n","n15","n75") else r[k] for k in r}
                q["year"]=year
                src.append(q)
    assert len(src)==2740
    assert len({(v["decision_date"],v["session"]) for v in src})==len(src)
    with SCORED.open(newline="") as f:
        out={(r["decision_date"],r["session"]):r for r in csv.DictReader(f)}
    assert len(out)==1366
    n=0
    for session in ("DAY","OVN"):
        hist=sorted((r for r in src if r["session"]==session),key=lambda r:r["decision_date"])
        feat=[]
        for i in range(22,len(hist)):
            previous=np.log([v["rv"] for v in hist[:i]])
            assert (hist[i]["n"],hist[i]["n15"],hist[i]["n75"])==((31.,30.,0.) if session=="DAY" else (61.,59.,1.))
            v=hist[i]
            if i>=60:
                feat.append({"decision_date":v["decision_date"],"year":v["year"],"rv":v["rv"],"y":math.log(v["rv"]),
                  "x":[previous[-1],previous[-5:].mean(),previous[-22:].mean()],
                  "clim":previous[-60:].mean(),"p1":previous[-1],"p5":previous[-5:].mean()})
        locked=fit([r for r in feat if r["decision_date"]<"2025-01-01"])
        for i,r in enumerate(feat):
            if r["year"]<2023:continue
            prior=feat[:i]
            mod=locked if r["year"]>=2025 else fit(prior)
            predictions={"HAR":forecast(mod,r["x"]),"CLIM60":r["clim"],
                 "PERSIST1":r["p1"],"PERSIST5":r["p5"]}
            e=out[(r["decision_date"],session)]
            assert int(e["prior_training_windows"])==i
            for k,lv in predictions.items():
                ratio=r["rv"]/math.exp(lv)
                qlike=ratio-math.log(ratio)-1
                logmse=(r["y"]-lv)**2
                for key,target in [(k+"_log",lv),(k+"_q",qlike),(k+"_logmse",logmse)]:
                    if abs(float(e[key])-target)>1e-8:
                        raise AssertionError((r["decision_date"],session,key,e[key],target))
            n+=1
    assert n==1366
    print("H3A PASS 1366 fixed actual M15 RV predictions, exact source parity; no promotion")
if __name__=="__main__":main()
