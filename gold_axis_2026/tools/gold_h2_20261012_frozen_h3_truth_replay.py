"""H2 retrospective no-fit H3 vote information audit: exact original R66 source parity.
No statistical promotion of inspected 2025/2026 H3 performance.
"""
import csv, json, math, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"GOLD_R66_20261012_H3_09_CARRY_15_1645_EXECUTION_TARGET_MODELS_ALLROWS.csv"
OUT=ROOT/"GOLD_H2_20261012_FROZEN_H3_FUTURE_INFORMATION_RESULT.json"
def met(rows):
    n=len(rows); up=sum(x["label"] for x in rows); down=n-up
    result={"n":n,"up":up,"down":down}
    for name,fn in [("H3",lambda x:x["signal"]),("ALWAYS_UP",lambda x:1),
                    ("GAP_SIGN",lambda x:int(x["gap"]>=0)),("PREDEC_SIGN",lambda x:int(x["pre"]>=0))]:
        cor=sum(fn(x)==x["label"] for x in rows)
        uc=sum(x["label"]==1 and fn(x)==1 for x in rows)
        dc=sum(x["label"]==0 and fn(x)==0 for x in rows)
        result[name]={"correct":cor,"acc":cor/n if n else None,
          "ba":(uc/up+dc/down)/2 if up and down else None,
          "up_recall":uc/up if up else None,"down_recall":dc/down if down else None,
          "pred_up":sum(fn(x)==1 for x in rows)}
    return result
def pair(rows,base):
    wins=losses=0
    for x in rows:
        h=(x["signal"]==x["label"])
        b=(base(x)==x["label"])
        wins+=bool(h and not b);losses+=bool(b and not h)
    return wins,losses
def check(a,b,path):
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        assert math.isclose(a,b,abs_tol=1e-9,rel_tol=1e-9),(path,a,b)
    else: assert a==b,(path,a,b)
def main():
    with SRC.open(newline="") as f:
        d=list(csv.DictReader(f))
    assert len(d)==2464
    rows=[]
    for v in d:
        x={"clock":v["clock"],"entry_date":v["entry_date"],"source_D3":v["source_D3"],"year":int(v["year"]),
           "signal":int(v["h3bit"]),"label":int(v["y"]),"gap":float(v["gap"]),
           "pre":float(v["predecision_intra"]),"real":float(v["realized_ret"]),
           "entry":float(v["entry_price"]),"target":float(v["target_price"]),
           "prior_signal":v["prior_signal"]=="true"}
        if x["year"]>=2023:
            assert math.isclose(math.log(x["target"]/x["entry"]),x["real"],abs_tol=1e-9)
            assert x["label"]==int(x["real"]>0) and x["source_D3"]>x["entry_date"]
        assert x["prior_signal"]==(x["clock"]=="09")
        rows.append(x)
    recorded=json.loads(OUT.read_text())
    assert recorded["rows"]==2464 and recorded["label_parity_failures"]==0
    for clock in ("09","15","1645"):
        source=[abs(x["gap"]) for x in rows if x["clock"]==clock and x["year"] in (2023,2024)]
        threshold=statistics.median(source)
        check(threshold,recorded["thresholds"][clock],clock+" threshold")
        for year in (2023,2024,2025,2026):
            a=sorted((x for x in rows if x["clock"]==clock and x["year"]==year),key=lambda x:x["entry_date"])
            small=[x for x in a if abs(x["gap"])<threshold]
            non=[];last=""
            for x in a:
                if x["entry_date"]>last:
                    non.append(x);last=x["source_D3"]
            r=recorded["results"][clock][str(year)]
            for key,arr in (("full",a),("small",small),("nonoverlap",non)):
                m=met(arr)
                for k,v in m.items():
                    if isinstance(v,dict):
                        for name,number in v.items():check(number,r[key][k][name],(clock,year,key,k,name))
                    else:check(v,r[key][k],(clock,year,key,k))
            for k,f in (("ALWAYS_UP",lambda x:1),("GAP_SIGN",lambda x:int(x["gap"]>=0))):
                wins,losses=pair(a,f)
                assert (wins,losses)==(r["paired"][k]["w"],r["paired"][k]["l"])
    assert recorded["conclusion"]=="REJECT_NO_PROMOTION"
    assert not any(recorded["gates"].values())
    print("H2 PASS: 2464 frozen source rows / 12 clock-year cohorts; no refit, no transport promotion.")
if __name__=="__main__":main()
