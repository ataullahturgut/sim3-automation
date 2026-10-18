"""Reproduce every rolling HAR500 macro event volatility forecast from frozen actual M15 session RV data.
Original event *dates* retrospective; event scheduling vintage not certified at decision; no live claim.
"""
import csv,json,math
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parents[1]
def read(name):
    with (D/name).open(newline="") as f:return list(csv.DictReader(f))
def model(training,r,features):
    yy=np.array([u["y"] for u in training],float)
    xx=np.array([[u[k] for k in features] for u in training],float)
    ym=yy.mean();means=xx.mean(axis=0);sd=xx.std(axis=0);sd[sd<1e-10]=1
    z=(xx-means)/sd
    beta=np.linalg.solve(z.T@z+10*np.eye(len(features)),z.T@(yy-ym))
    now=np.array([r[k] for k in features],float)
    return float(ym+((now-means)/sd)@beta)
def main():
    raw=read("GOLD_GPT6_P3_TRAINING_SOURCE_RV_EVENTS.csv")
    assert len(raw)==2740
    source=[{"day":r["day"],"sn":r["sn"],"rv":float(r["rv"]), "event":int(r["event"]),"year":int(r["day"][:4])} for r in raw]
    scored={(r["day"],r["sn"]):r for r in read("GOLD_GPT6_P3_SCORE_ROWS.csv")}
    assert len(scored)==1366
    cnt=0
    for sn in ("DAY","OVN"):
        allr=sorted((r for r in source if r["sn"]==sn),key=lambda r:r["day"])
        feats=[]
        for i in range(60,len(allr)):
            history=np.log([u["rv"] for u in allr[:i]])
            r=allr[i].copy()
            r.update(y=math.log(r["rv"]),L1=float(history[-1]),L5=float(history[-5:].mean()),
                     L22=float(history[-22:].mean()),clim=float(history[-60:].mean()))
            feats.append(r)
        for i,r in enumerate(feats):
            if i<60 or r["year"]<2023:continue
            tr=feats[max(0,i-500):i]
            preds={"PERSIST5":r["L5"],"CLIM60":r["clim"],
                    "ROLL500":model(tr,r,("L1","L5","L22")),
                    "ROLL500_EVENT":model(tr,r,("L1","L5","L22","event"))}
            score=scored[r["day"],sn]
            assert int(score["train_n"])==len(tr)
            assert int(score["event"])==r["event"]
            assert abs(float(score["rv"])-r["rv"])<1e-10
            for k,val in preds.items():
                ratio=r["rv"]/math.exp(val)
                found={"log":val,"q":ratio-math.log(ratio)-1,"logmse":(r["y"]-val)**2}
                for suffix,x in found.items():
                    assert abs(float(score[k+"_"+suffix])-x)<1e-8,(r["day"],sn,k,suffix)
            cnt+=1
    assert cnt==1366
    stats=json.loads((D/"GOLD_GPT6_P3_RESULT.json").read_text())
    assert stats["conclusion"]=="REJECT_NO_PROMOTION"
    print("P3 PASS: 2740 complete historic session RV source+event flags, 1366 causal model predictions; no transport.")
if __name__=="__main__":main()
