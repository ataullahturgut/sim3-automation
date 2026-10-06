from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
P=AX/"GOLD_SESSION_V3_INTEGRITY_ROWS_2023_2025.csv"
OUT=AX/"SESSION_INTERNAL_COVERAGE_DISTRIBUTION_OUT"; OUT.mkdir(exist_ok=True)

def main():
    x=pd.read_csv(P)
    x=x[x.trainable.astype(str).str.lower().eq("true")].copy()
    rows=[]
    for (part,win),g in x.groupby(["partition","window"]):
        s=g.internal_coverage.astype(float)
        rows.append({
            "partition":part,"window":win,"n":len(g),
            "min":float(s.min()),"p01":float(s.quantile(.01)),"p05":float(s.quantile(.05)),
            "p10":float(s.quantile(.10)),"median":float(s.median()),
            "below_075":int((s<.75).sum()),"below_080":int((s<.80).sum()),
            "below_090":int((s<.90).sum()),"below_095":int((s<.95).sum()),
            "below_100":int((s<1.0).sum())
        })
    q=pd.DataFrame(rows)
    q.to_csv(OUT/"summary.csv",index=False)
    obj={"status":"SESSION_INTERNAL_COVERAGE_DISTRIBUTION","rows":rows}
    (OUT/"summary.json").write_text(json.dumps(obj,indent=2)+"\n")
    print(json.dumps(obj,indent=2))
if __name__=="__main__":main()
