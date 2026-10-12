"""Replay fixed GC completed-hour source against spot known preissue and future OVN return.
No paid Databento access; 2023 train, 2024 DEV, 2025 opened; requires numpy.
"""
import csv,json,math
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parents[1]
def ridge(tr,r,cols):
    x=np.array([[u[v] for v in cols] for u in tr]);y=np.array([u["target_r"] for u in tr])
    ym=y.mean();avg=x.mean(0);sd=x.std(0);sd[sd<1e-10]=1
    z=(x-avg)/sd;b=np.linalg.solve(z.T@z+10*np.eye(len(cols)),z.T@(y-ym))
    return float(ym+((np.array([r[v] for v in cols])-avg)/sd)@b)
def main():
    with (D/"GOLD_GPT6_P5_MATCHED_FULL_SOURCE.csv").open(newline="") as f:
        src=list(csv.DictReader(f))
    with (D/"GOLD_GPT6_P5_DECISION_SCORES.csv").open(newline="") as f:
        scored={r["date"]:r for r in csv.DictReader(f)}
    assert len(src)==355 and len(scored)==262
    raw=sorted([{"date":r["issue_date"],"year":int(r["issue_date"][:4]),
             "gc":float(r["gc_last1h_r"]),"spot":float(r["spot_pre1h_r"]),
             "target_r":float(r["target_r"]),"entry":float(r["entry"]),"exit":float(r["exit"])} for r in src],key=lambda r:r["date"])
    k=0
    for i,r in enumerate(raw):
        assert math.isclose(math.log(r["exit"]/r["entry"]),r["target_r"],abs_tol=1e-10)
        if r["year"]<2024:continue
        train=raw[:i] if r["year"]==2024 else [q for q in raw if q["year"]<2025]
        if len(train)<70:continue
        z=scored[r["date"]]
        assert int(z["h_n"])==len(train)
        assert int(z["GC_SIGN"])==int(r["gc"]>0)
        assert int(z["SPOT_SIGN"])==int(r["spot"]>0)
        pred={"RW":0.,"SPOT_ONLY":ridge(train,r,("spot",)),
              "GC_PLUS_SPOT":ridge(train,r,("spot","gc"))}
        for key,ret in pred.items():
            for suffix,value in (("pred",ret),("mse",(ret-r["target_r"])**2),
                                 ("price_ae",abs(r["entry"]*math.exp(ret)-r["exit"]))):
                assert math.isclose(value,float(z[key+"_"+suffix]),abs_tol=1e-8), (r["date"],key,suffix)
        k+=1
    assert k==262
    summary=json.loads((D/"GOLD_GPT6_P5_RESULT.json").read_text())
    assert summary["verdict"]=="REJECT_NO_PROMOTION"
    print("P5 PASS 355 matched completed GC hour / past spot 15m, 262 chronologically fitted labels; no leadlag edge.")
if __name__=="__main__":main()
