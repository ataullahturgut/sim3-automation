"""Reproduce P3 2026 DAY historical-retrospective stress from independently frozen sources.
The direct 2026 Dukascopy source has 15 matching M1 rows per 15min bar (NOT flag==1).
No 2026 OVN: 65 bars vs 2020–25 complete source's 61 bars with 75m quote break.
Macro calendar dates are retrospective; they are not proven known as originally scheduled.
"""
import csv,json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/name).open(newline="") as f:
        return list(csv.DictReader(f))
def fit(tr,now,keys):
    x=np.array([[r[z] for z in keys] for r in tr],float)
    y=np.array([r["y"] for r in tr],float)
    mean=float(y.mean());cent=x.mean(axis=0);std=x.std(axis=0);std[std<1e-10]=1
    z=(x-cent)/std
    beta=np.linalg.solve(z.T@z+10*np.eye(len(keys)),z.T@(y-mean))
    return mean+float(((np.array([now[v] for v in keys])-cent)/std)@beta)
def main():
    historic=read("GOLD_GPT6_P3_2020_2025_DAY_RV_TRAINING_SOURCE.csv")
    direct=read("GOLD_GPT6_P3_2026_DAY_REALIZED_RV_ROWS.csv")
    stored=read("GOLD_GPT6_P3_2026_DAY_SCORES.csv")
    report=json.loads((ROOT/"GOLD_GPT6_P3_2026_DAY_RESULT.json").read_text())
    assert len(historic)==1547 and len(direct)==177 and len(stored)==177
    events=set(report["macro_2026_events"])
    allrows=[dict(day=r["day"],rv=float(r["rv"]),event=int(r["event"])) for r in historic]
    for r in direct:
        assert int(r["n"])==31 and int(r["n15"])==30 and float(r["rv"])>0
        allrows.append(dict(day=r["trade_date"],rv=float(r["rv"]),event=int(r["trade_date"] in events)))
    allrows.sort(key=lambda r:r["day"])
    assert len({v["day"] for v in allrows})==len(allrows)
    features=[]
    for i in range(60,len(allrows)):
        old=np.log([r["rv"] for r in allrows[:i]])
        current=allrows[i].copy()
        current.update(y=math.log(current["rv"]),L1=float(old[-1]),L5=float(old[-5:].mean()),
                       L22=float(old[-22:].mean()),clim=float(old[-60:].mean()))
        features.append(current)
    actual={r["date"]:r for r in stored}
    qvals={k:[] for k in ("PERSIST5","CLIM60","ROLL500","ROLL500_EVENT")}
    n=0
    for i in range(60,len(features)):
        r=features[i]
        if r["day"]<"2026-01-01": continue
        train=features[max(0,i-500):i]
        pred={"PERSIST5":r["L5"],"CLIM60":r["clim"],
              "ROLL500":fit(train,r,("L1","L5","L22")),
              "ROLL500_EVENT":fit(train,r,("L1","L5","L22","event"))}
        scored=actual[r["day"]]
        assert int(scored["training_n"])==500
        assert int(scored["event"])==r["event"]
        for k,x in pred.items():
            rel=r["rv"]/math.exp(x)
            qlike=rel-math.log(rel)-1
            logmse=(r["y"]-x)**2
            for field,value in (("log",x),("q",qlike),("logmse",logmse)):
                assert math.isclose(value,float(scored[k+"_"+field]),rel_tol=1e-9,abs_tol=1e-8),(r["day"],k,field)
            qvals[k].append(qlike)
        n+=1
    assert n==177
    for k,v in qvals.items():
        assert math.isclose(sum(v)/len(v),report["metrics"]["qlike"][k],abs_tol=1e-10)
    assert report["verdict"]=="2026_DAY_P3_NO_PROMOTION_FAILS_PRIMARY_QLIKE_VS_PERSIST5"
    assert report["metrics"]["qlike"]["PERSIST5"] < report["metrics"]["qlike"]["ROLL500_EVENT"]
    print("PASS: all 177 2026 DAY rows, HAR500/EV calendar and Persist5 QLIKE parity; night not tested.")
if __name__=="__main__":
    main()
