from __future__ import annotations
import argparse, csv, json, math, os, importlib.util, sys
from collections import defaultdict
from pathlib import Path

def load_mod(path):
    spec=importlib.util.spec_from_file_location("parent",str(path))
    m=importlib.util.module_from_spec(spec); sys.modules["parent"]=m; spec.loader.exec_module(m); return m

def qloss(y,f,eps=1e-14):
    yy=max(float(y),eps); ff=max(float(f),eps); z=yy/ff
    return z-math.log(z)-1

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--parent",type=Path,required=True)
    ap.add_argument("--external-spine",type=Path,required=True)
    args=ap.parse_args()
    p=load_mod(args.parent)

    ext=p.load_external(args.external_spine); gov=p.load_governed()
    audit=p.overlap_audit(ext,gov)
    if not audit["passed"]: raise RuntimeError("SOURCE_AUDIT_FAIL")
    ds,close,dr=p.combine(ext,gov); rows=p.build_rows(ds,close,dr)

    cutoff=p.date(2025,12,31)
    train=[r for r in rows if r["target_date"]<=cutoff]
    test=[r for r in rows if r["target_date"].year==2026]
    if not test: raise RuntimeError("NO_2026")

    def details(train_rows):
        X,y=p.Xy(train_rows); b=p.np.linalg.lstsq(X,y,rcond=None)[0]
        Xt,_=p.Xy(test); sd=Xt@b
        pred=sd*sd
        hi=p.nearest_rank([r["target_dr"] for r in train_rows],.80)
        out=[]
        for r,fc in zip(test,pred):
            out.append({
              "target_date":r["target_date"].isoformat(),
              "month":r["target_date"].strftime("%Y-%m"),
              "actual_dr":float(r["target_dr"]),"forecast_dr":float(fc),
              "actual_high":int(r["target_dr"]>=hi),"alert":int(fc>=hi)
            })
        return out,hi

    exp,exp_hi=details(train)
    w500,w_hi=details(train[-500:])
    outrows=[]
    for name,rr,hi in [("EXPANDING",exp,exp_hi),("W500",w500,w_hi)]:
        by=defaultdict(list)
        for r in rr: by[r["month"]].append(r)
        for month,vals in sorted(by.items()):
            y=[x["actual_dr"] for x in vals]; f=[x["forecast_dr"] for x in vals]
            ah=[x["actual_high"] for x in vals]; al=[x["alert"] for x in vals]
            tp=sum(a==1 and b==1 for a,b in zip(ah,al))
            fp=sum(a==0 and b==1 for a,b in zip(ah,al))
            fn=sum(a==1 and b==0 for a,b in zip(ah,al))
            auc=p.roc_auc(ah,f)
            outrows.append({
              "month":month,"policy":name,"n":len(vals),
              "mse":sum((a-b)**2 for a,b in zip(y,f))/len(vals),
              "qlike":sum(qloss(a,b) for a,b in zip(y,f))/len(vals),
              "auc":auc,
              "alerts":sum(al),"coverage":sum(al)/len(vals),
              "precision":tp/(tp+fp) if tp+fp else None,
              "recall":tp/(tp+fn) if tp+fn else None,
              "tp":tp,"fp":fp,"fn":fn,"threshold":hi
            })
    result={"identity":"SQRT_2026_MONTHLY_STRESS_ANATOMY_V1","stress_only":True,
      "selection_allowed":False,"last_target_date":test[-1]["target_date"].isoformat(),
      "rows":outrows}
    out=Path("monthly_out"); out.mkdir(exist_ok=True)
    (out/"GOLD_CONTROL_SQRT_2026_MONTHLY_STRESS_ANATOMY_V1_RESULT_2026-09-24.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
